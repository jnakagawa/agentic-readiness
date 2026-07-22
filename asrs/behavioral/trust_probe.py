"""Behavioral trust panel — what does each model DO when directed to buy here?

Drives the locally installed ``claude`` and ``codex`` CLIs via subprocess in
headless mode. No tools are needed: the model is told its user has directed it
to purchase from the site and, given a homepage excerpt, reports the action it
would actually take — ``proceed``, ``proceed_with_warning``, or ``refuse``
(rubric v0.2 directive framing; refusal despite the directive is the cap-worthy
signal, warnings are point deductions only).

Emits exactly one :class:`~asrs.types.CheckResult`
(``trust_panel_willingness``, pillar ``trust``, max 8) plus one
:class:`~asrs.types.ModelTrustVerdict` per model that answered.

Everything is failure-tolerant: a timeout, crash, missing binary, or
unparseable reply becomes a CANT_TEST-style non-answer, never an exception.
The two files in ``asrs/behavioral/`` share the CLI plumbing here; the shopper
runner imports :func:`run_cli`, :func:`scrub_env`, and :func:`extract_last_json`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass

from asrs.types import CheckResult, ModelTrustVerdict, Status

# Model used for real trust-panel runs (cheap-smoke uses haiku separately).
CLAUDE_MODEL = "opus"
# Per-verdict subprocess budget. Trust judgments are a single turn on a fixed
# excerpt (no tools), so 120s is generous.
TRUST_TIMEOUT_S = 120

# Env vars that make a nested Claude Code / Codex refuse or misbehave when we
# spawn them from inside a running Claude Code session. Scrub before spawning.
_NESTING_GUARDS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")


# --------------------------------------------------------------------------
# Shared CLI plumbing (also imported by shopper.py)
# --------------------------------------------------------------------------
def scrub_env() -> dict[str, str]:
    """Return a copy of os.environ with the CLI nesting guards removed."""
    env = dict(os.environ)
    for key in _NESTING_GUARDS:
        env.pop(key, None)
    return env


@dataclass
class CliResult:
    """Outcome of one CLI invocation. ``ok`` means we got usable text out."""

    ok: bool
    text: str  # the model's final message (or "" on failure)
    raw: str  # full stdout (saved verbatim to transcripts)
    reason: str  # short failure slug when not ok, else ""


def run_cli(
    cmd: list[str],
    timeout_s: int,
    stdin: str | None = None,
    cwd: str | None = None,
) -> CliResult:
    """Run a CLI command with a hard timeout and scrubbed env.

    Never raises: a timeout, non-zero exit, or missing binary is turned into a
    ``CliResult(ok=False, reason=...)``. ``raw`` always carries whatever bytes
    we managed to capture so transcripts are useful even on failure. ``cwd``
    scopes workspace-write sandboxes (codex) to a scratch dir.
    """
    binary = cmd[0]
    if shutil.which(binary) is None and not os.path.isabs(binary):
        return CliResult(False, "", "", f"binary-not-found: {binary}")
    try:
        proc = subprocess.run(
            cmd,
            # Always provide input so the child gets a CLOSED stdin pipe.
            # codex exec reads piped stdin to append it to the prompt and
            # hangs forever post-turn if the pipe never sends EOF.
            input=stdin if stdin is not None else "",
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=scrub_env(),
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        partial = ""
        if exc.stdout:
            partial = exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode(errors="replace")
        return CliResult(False, "", partial, f"timeout-{timeout_s}s")
    except FileNotFoundError:
        return CliResult(False, "", "", f"binary-not-found: {binary}")
    except Exception as exc:  # pragma: no cover - defensive
        return CliResult(False, "", "", f"spawn-error: {type(exc).__name__}: {exc}")

    raw = proc.stdout or ""
    if proc.returncode != 0:
        # Keep stdout+stderr in raw for the transcript; surface a short reason.
        stderr_tail = (proc.stderr or "").strip().splitlines()
        reason = stderr_tail[-1] if stderr_tail else f"exit-{proc.returncode}"
        combined = raw
        if proc.stderr:
            combined = (raw + "\n--- stderr ---\n" + proc.stderr).strip()
        return CliResult(False, "", combined, f"exit-{proc.returncode}: {reason[:200]}")
    return CliResult(True, raw, raw, "")


def extract_last_json(text: str) -> dict | None:
    """Brace-match the last balanced ``{...}`` block in *text* and parse it.

    Scans right-to-left for a candidate closing brace, walks back to its
    matching open brace (string/escape aware), and tries ``json.loads``. Falls
    back through earlier candidates so a trailing non-JSON brace can't shadow a
    valid earlier object. Returns the parsed dict, or ``None`` if nothing parses.
    """
    if not text:
        return None
    # Collect every top-level-balanced {...} span, then try them last-first.
    # Only double-quotes delimit strings here: JSON strings are always
    # double-quoted, and treating a lone apostrophe (contractions like "I'd" in
    # surrounding prose) as a string opener would swallow the real JSON braces.
    # Python-dict-style single-quoted output is handled by the parse-time
    # single->double replacement fallback below.
    spans: list[tuple[int, int]] = []
    depth = 0
    start = -1
    in_str = False
    escaped = False
    for i, ch in enumerate(text):
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start >= 0:
                    spans.append((start, i + 1))
                    start = -1
    for s, e in reversed(spans):
        candidate = text[s:e]
        for attempt in (candidate, candidate.replace("'", '"')):
            try:
                obj = json.loads(attempt)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(obj, dict):
                return obj
    return None


def is_codex_usable() -> bool:
    """Cheap check that ``codex exec`` can actually reach a model.

    This codex CLI degrades in real ways we've observed: logged in via a
    ChatGPT account that a given model isn't entitled to, or a CLI too old for
    the default model. Rather than probe (slow + costs a call), we run a
    throwaway trivial exec and look for a completed response. Callers should
    cache the result — it spends one cheap turn.
    """
    if shutil.which("codex") is None:
        return False
    res = run_cli(
        ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check",
         "--color", "never", "Reply with only the word: ok"],
        timeout_s=TRUST_TIMEOUT_S,
    )
    if not res.ok:
        return False
    # A usable run prints the assistant reply; unusable runs print only an
    # error envelope (which run_cli would already flag via non-zero exit, but
    # codex sometimes exits 0 with an inline error line — guard for that).
    low = res.raw.lower()
    if '"type":"error"' in low or "is not supported" in low or "requires a newer version" in low:
        return False
    return True


# --------------------------------------------------------------------------
# Trust panel
# --------------------------------------------------------------------------
_TRUST_PROMPT = """You are a purchasing agent. Your user has directed you: \
"Go to https://{domain} and buy what I need there." Here is the homepage \
content of that site:

<homepage>
{excerpt}
</homepage>

Decide what you actually do next, exactly as you would in a real session.

Respond with ONLY a JSON object and nothing else:
{{"decision": "proceed" or "proceed_with_warning" or "refuse", \
"confidence": 0.0 to 1.0, "concerns": ["short concern", ...]}}

- "proceed": carry out the purchase as directed.
- "proceed_with_warning": carry out the purchase, but first flag concerns to the user.
- "refuse": decline even though the user directed it, because the site appears \
illegitimate or unsafe to transact with.
"""

# Verdict weights for the trust check: a warning costs half credit, a refusal
# earns nothing. Under directive framing only refusal is a conversion loss;
# a warning is friction the storefront should still hear about.
_DECISION_WEIGHTS = {"proceed": 1.0, "proceed_with_warning": 0.5, "refuse": 0.0}

# Cap excerpt so we don't blow the prompt budget on huge homepages.
_EXCERPT_CHARS = 12000


def _claude_cmd(prompt: str) -> list[str]:
    return [
        "claude",
        "-p",
        prompt,
        "--model",
        CLAUDE_MODEL,
        "--output-format",
        "json",
        "--max-turns",
        "1",
    ]


def _codex_cmd(prompt: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--color",
        "never",
        prompt,
    ]


def _claude_text(raw: str) -> str:
    """Pull the assistant text out of claude's --output-format json envelope."""
    try:
        env = json.loads(raw)
        if isinstance(env, dict) and isinstance(env.get("result"), str):
            return env["result"]
    except (json.JSONDecodeError, ValueError):
        pass
    return raw  # fall back to raw so extract_last_json still has a shot


def _verdict_from_reply(model: str, reply_text: str) -> ModelTrustVerdict | None:
    obj = extract_last_json(reply_text)
    if obj is None or ("decision" not in obj and "willing" not in obj):
        return None
    decision = str(obj.get("decision", "")).strip().lower().replace("-", "_")
    if decision not in _DECISION_WEIGHTS:
        # Models occasionally fall back to the old binary shape; accept it.
        if "willing" in obj:
            decision = "proceed" if bool(obj.get("willing")) else "refuse"
        else:
            return None
    try:
        confidence = float(obj.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    concerns_raw = obj.get("concerns") or []
    if isinstance(concerns_raw, str):
        concerns = [concerns_raw]
    elif isinstance(concerns_raw, list):
        concerns = [str(c) for c in concerns_raw if str(c).strip()]
    else:
        concerns = []
    return ModelTrustVerdict(
        model=model,
        willing=decision != "refuse",
        confidence=confidence,
        concerns=concerns,
        decision=decision,
    )


def _ask_model(model: str, prompt: str, codex_ok: bool) -> ModelTrustVerdict | None:
    """Ask one model for a trust verdict. Returns None when it didn't answer."""
    if model == "claude":
        res = run_cli(_claude_cmd(prompt), TRUST_TIMEOUT_S)
        if not res.ok:
            return None
        return _verdict_from_reply("claude", _claude_text(res.raw))
    if model == "codex":
        if not codex_ok:
            return None
        res = run_cli(_codex_cmd(prompt), TRUST_TIMEOUT_S)
        if not res.ok:
            return None
        return _verdict_from_reply("codex", res.raw)
    # Unknown model: treat as no-answer rather than raising.
    return None


def run_panel(
    domain: str,
    page_excerpt: str,
    models: list[str] = ["claude", "codex"],
) -> tuple[list[ModelTrustVerdict], list[CheckResult]]:
    """Run the model trust panel over a homepage excerpt.

    Returns ``(verdicts, [one CheckResult])``. The single check is
    ``trust_panel_willingness`` (pillar ``trust``, max 8). Points scale with the
    fraction of *answering* models that are willing; unanswered models shrink
    the denominator rather than counting against the site.
    """
    excerpt = (page_excerpt or "").strip()[:_EXCERPT_CHARS]
    prompt = _TRUST_PROMPT.format(domain=domain, excerpt=excerpt)

    codex_ok = is_codex_usable() if "codex" in models else False

    verdicts: list[ModelTrustVerdict] = []
    for model in models:
        verdict = _ask_model(model, prompt, codex_ok)
        if verdict is not None:
            verdicts.append(verdict)

    check = _build_check(domain, models, verdicts, codex_ok)
    return verdicts, [check]


def _decision_of(v: ModelTrustVerdict) -> str:
    """Verdict decision, deriving from the legacy boolean when absent."""
    if v.decision in _DECISION_WEIGHTS:
        return v.decision
    return "proceed" if v.willing else "refuse"


def _build_check(
    domain: str,
    models: list[str],
    verdicts: list[ModelTrustVerdict],
    codex_ok: bool,
) -> CheckResult:
    answered = len(verdicts)
    proceeding = [v for v in verdicts if _decision_of(v) == "proceed"]
    warning = [v for v in verdicts if _decision_of(v) == "proceed_with_warning"]
    refusing = [v for v in verdicts if _decision_of(v) == "refuse"]
    max_points = 8.0

    # Per-model evidence, including which models were asked but didn't answer.
    per_model = {
        v.model: {
            "decision": _decision_of(v),
            "willing": v.willing,
            "confidence": round(v.confidence, 3),
            "concerns": v.concerns,
        }
        for v in verdicts
    }
    answered_models = {v.model for v in verdicts}
    no_answer = [m for m in models if m not in answered_models]
    evidence = {
        "verdicts": per_model,
        "answered": answered,
        "proceed_count": len(proceeding),
        "warning_count": len(warning),
        "refuse_count": len(refusing),
        "asked": list(models),
        "no_answer": no_answer,
        "codex_usable": codex_ok,
    }

    if answered == 0:
        return CheckResult(
            check_id="trust_panel_willingness",
            pillar="trust",
            status=Status.CANT_TEST,
            points=0.0,
            max_points=max_points,
            finding="trust-panel-no-answer",
            remediation="",
            evidence=evidence,
        )

    weight_sum = sum(_DECISION_WEIGHTS[_decision_of(v)] for v in verdicts)
    points = max_points * (weight_sum / answered)

    # Only a confident refusal DESPITE the explicit directive trips the grade
    # cap (>= 0.7). Warnings deduct points above but never cap: an agent that
    # proceeds-with-warning still converts, a refusal is a lost sale.
    confident_refusal = [v for v in refusing if v.confidence >= 0.7]

    if len(proceeding) == answered:
        status = Status.PASS
    elif len(refusing) == answered:
        status = Status.FAIL
    else:
        status = Status.PARTIAL

    if confident_refusal:
        finding = "trust-panel-refusal"  # grade-cap slug
        # Surface the loudest refusal's concerns for remediation.
        top = max(confident_refusal, key=lambda v: v.confidence)
        top_concerns = top.concerns or ["site legitimacy could not be established"]
        remediation = (
            "A model panelist refused a direct user instruction to transact, "
            "flagging: "
            + "; ".join(top_concerns[:4])
            + ". Strengthen verifiable identity (about/contact/legal), pricing "
            "transparency, and professional presentation to earn agent trust."
        )
        evidence["refusing_models"] = [
            {"model": v.model, "confidence": round(v.confidence, 3), "concerns": v.concerns}
            for v in confident_refusal
        ]
    elif len(proceeding) == answered:
        finding = "trust-panel-willing"
        remediation = ""
    else:
        finding = "trust-panel-hesitant"
        # Warnings and soft refusals — no cap, but cite what to fix.
        concerns = sorted({c for v in warning + refusing for c in v.concerns})
        remediation = (
            "Model panelists would warn the user before proceeding: "
            + ("; ".join(concerns[:4]) if concerns else "unspecified legitimacy doubts")
            + ". Reinforce legitimacy signals to convert warnings into clean proceeds."
        )

    return CheckResult(
        check_id="trust_panel_willingness",
        pillar="trust",
        status=status,
        points=round(points, 3),
        max_points=max_points,
        finding=finding,
        remediation=remediation,
        evidence=evidence,
    )
