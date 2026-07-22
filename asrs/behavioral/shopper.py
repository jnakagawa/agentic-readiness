"""Behavioral shopper panel — live read-only recon by agent CLIs.

For each ``model x trial`` we spawn a headless shopper agent (``claude -p`` with
web tools; ``codex exec`` when it can reach the network) and have it investigate
a domain read-only, reporting a checkpoint ladder as a JSON verdict:

    found_product, understood_pricing, found_purchase_path,
    machine_payable_path, no_human_gate

Raw CLI output is saved per run to ``<out_dir>/transcripts/`` and the checkpoint
verdicts are aggregated into the five ``bhv_*`` outcome checks plus the
``trust_live_session`` trust check (rubric v0.2: in-task trust_events scored as
behavioral trust under a user directive). Runs that fail or don't parse are
excluded from the scoring denominator (CANT_TEST semantics).

Shares CLI plumbing with :mod:`asrs.behavioral.trust_probe` (subprocess runner,
env scrubbing, last-JSON extraction, codex-usability probe).
"""

from __future__ import annotations

import json
import os
import tempfile

from asrs.behavioral.trust_probe import (
    extract_last_json,
    is_codex_usable,
    run_cli,
)
from asrs.types import BehavioralRun, CheckResult, Status

CLAUDE_MODEL = "opus"
SHOPPER_TIMEOUT_S = 300  # per model x trial
CLAUDE_MAX_TURNS = 15

# Checkpoint ladder -> (rubric check id, max points). Order is the ladder order.
_CHECKPOINT_CHECKS: list[tuple[str, str, int]] = [
    ("found_product", "bhv_found_product", 4),
    ("understood_pricing", "bhv_understood_pricing", 3),
    ("found_purchase_path", "bhv_purchase_path", 4),
    ("machine_payable_path", "bhv_machine_payable", 5),
    ("no_human_gate", "bhv_no_human_gate", 4),
]
_CHECKPOINT_KEYS = [c[0] for c in _CHECKPOINT_CHECKS]

# Max points for the trust_live_session check (pillar trust, rubric v0.2):
# trust as it manifests during the directed session, from trust_events.
_TRUST_LIVE_MAX = 4.0


_SHOPPER_PROMPT = """You are a purchasing agent. Your user has directed you to \
use https://{domain} for this task: "{task}". Work out whether you could \
complete that directive end-to-end as an agent.

Investigate the site READ-ONLY (fetch pages and docs, follow links, search the \
web for its API/pricing/docs). STRICT RULES: do NOT create accounts, do NOT \
submit forms, do NOT pay, do NOT use any credentials, do NOT perform any write \
or state-changing action. Recon only.

Determine each checkpoint below, then finish your response with ONLY a JSON \
object (no prose after it):

{{"checkpoints": {{"found_product": true/false, "understood_pricing": true/false, \
"found_purchase_path": true/false, "machine_payable_path": true/false, \
"no_human_gate": true/false}}, "blockers": ["..."], "trust_events": ["..."], \
"notes": "..."}}

Definitions:
- found_product: you located the product/service matching the task.
- understood_pricing: you extracted concrete price and terms.
- found_purchase_path: you identified a concrete purchase/provisioning path.
- machine_payable_path: an agent could complete purchase/provisioning \
PROGRAMMATICALLY (an API plus programmatic payment, e.g. x402 or a checkout API) \
— NOT a browser-only checkout.
- no_human_gate: NO CAPTCHA, KYC/identity verification, email-confirmation loop, \
or sales call is required to complete the path.
- trust_events: any moments you hesitated, would warn the user the site might \
be illegitimate, or would refuse to continue despite the user's directive \
(empty list if none).
"""


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
        str(CLAUDE_MAX_TURNS),
        "--allowedTools",
        "WebFetch",
        "WebSearch",
    ]


def _codex_cmd(prompt: str) -> list[str]:
    # Model a full-auto codex agent: live web search plus real network access.
    # read-only sandboxing also cuts the network, so codex could only see its
    # search index — mock/unindexed storefronts looked blank ("blocked by
    # browser security policy"). workspace-write + the network_access override
    # turns the network on while keeping file writes confined to the cwd
    # (run_panel runs codex from a scratch dir).
    return [
        "codex",
        "exec",
        "--sandbox",
        "workspace-write",
        "-c",
        "sandbox_workspace_write.network_access=true",
        # --search is top-level-only in codex 0.145; exec takes the config key.
        "-c",
        "tools.web_search=true",
        "--skip-git-repo-check",
        "--color",
        "never",
        prompt,
    ]


def _claude_text(raw: str) -> str:
    """Extract the assistant text from claude's --output-format json envelope."""
    try:
        env = json.loads(raw)
        if isinstance(env, dict) and isinstance(env.get("result"), str):
            return env["result"]
    except (json.JSONDecodeError, ValueError):
        pass
    return raw


def _save_transcript(out_dir: str, domain: str, model: str, trial: int, raw: str) -> str:
    tdir = os.path.join(out_dir, "transcripts")
    os.makedirs(tdir, exist_ok=True)
    safe_domain = domain.replace("/", "_").replace(":", "_")
    path = os.path.join(tdir, f"{safe_domain}_{model}_t{trial}.json")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(raw if raw is not None else "")
    except OSError:
        return ""
    return path


def _parse_checkpoints(obj: dict) -> dict[str, bool]:
    raw = obj.get("checkpoints") or {}
    if not isinstance(raw, dict):
        raw = {}
    return {key: bool(raw.get(key, False)) for key in _CHECKPOINT_KEYS}


def _str_list(value) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return []


def _run_one(
    domain: str,
    task: str,
    model: str,
    trial: int,
    out_dir: str,
    codex_ok: bool,
) -> BehavioralRun:
    """Run a single model x trial recon. Never raises."""
    prompt = _SHOPPER_PROMPT.format(domain=domain, task=task)

    if model == "claude":
        res = run_cli(_claude_cmd(prompt), SHOPPER_TIMEOUT_S)
        reply_text = _claude_text(res.raw) if res.ok else res.raw
    elif model == "codex":
        if not codex_ok:
            # Skip codex entirely — do not fabricate. Recorded as a failed run
            # so it is excluded from scoring denominators.
            return BehavioralRun(
                model=model,
                trial=trial,
                checkpoints={},
                blockers=["run-failed: codex-not-usable (auth/sandbox/network)"],
                trust_events=[],
                transcript_path="",
            )
        # Scratch cwd: workspace-write confines codex's file writes here.
        scratch = tempfile.mkdtemp(prefix="asrs-codex-")
        res = run_cli(_codex_cmd(prompt), SHOPPER_TIMEOUT_S, cwd=scratch)
        reply_text = res.raw
    else:
        return BehavioralRun(
            model=model,
            trial=trial,
            checkpoints={},
            blockers=[f"run-failed: unknown-model {model}"],
            trust_events=[],
            transcript_path="",
        )

    transcript_path = _save_transcript(out_dir, domain, model, trial, res.raw)

    if not res.ok:
        return BehavioralRun(
            model=model,
            trial=trial,
            checkpoints={},
            blockers=[f"run-failed: {res.reason or 'cli-error'}"],
            trust_events=[],
            transcript_path=transcript_path,
        )

    obj = extract_last_json(reply_text)
    if obj is None or "checkpoints" not in obj:
        return BehavioralRun(
            model=model,
            trial=trial,
            checkpoints={},
            blockers=["run-failed: no-parseable-verdict-json"],
            trust_events=[],
            transcript_path=transcript_path,
        )

    return BehavioralRun(
        model=model,
        trial=trial,
        checkpoints=_parse_checkpoints(obj),
        blockers=_str_list(obj.get("blockers")),
        trust_events=_str_list(obj.get("trust_events")),
        transcript_path=transcript_path,
    )


def run_panel(
    domain: str,
    task: str,
    trials: int = 1,
    models: list[str] = ["claude", "codex"],
    out_dir: str = "runs",
) -> tuple[list[BehavioralRun], list[CheckResult]]:
    """Run the shopper panel and aggregate outcome + live-trust checks.

    Returns ``(runs, checks)`` where ``checks`` are the five ``bhv_*`` outcome
    checks plus ``trust_live_session``, computed over VALID runs (a valid run
    parsed a verdict; failed runs carry ``blockers=["run-failed: ..."]`` and
    are excluded from denominators).
    """
    codex_ok = is_codex_usable() if "codex" in models else False

    runs: list[BehavioralRun] = []
    for model in models:
        for trial in range(1, max(1, trials) + 1):
            runs.append(_run_one(domain, task, model, trial, out_dir, codex_ok))

    checks = _aggregate(domain, runs)
    return runs, checks


def _is_valid(run: BehavioralRun) -> bool:
    """A run counts toward scoring iff it produced a checkpoint verdict."""
    if run.checkpoints:
        return True
    return not any(b.startswith("run-failed") for b in run.blockers) and bool(run.checkpoints)


def _aggregate(domain: str, runs: list[BehavioralRun]) -> list[CheckResult]:
    valid = [r for r in runs if r.checkpoints]
    failed = [r for r in runs if not r.checkpoints]

    # Collect trust events and blockers across valid runs for evidence reuse.
    all_trust_events = sorted({e for r in valid for e in r.trust_events})
    multi_trial = len(valid) >= 2

    if not valid:
        # Zero valid runs -> every outcome check is CANT_TEST.
        failure_reasons = sorted({b for r in failed for b in r.blockers})
        evidence = {
            "valid_runs": 0,
            "attempted_runs": len(runs),
            "failures": failure_reasons,
            "by_run": [
                {"model": r.model, "trial": r.trial, "blockers": r.blockers,
                 "transcript": r.transcript_path}
                for r in runs
            ],
        }
        cant = [
            CheckResult(
                check_id=check_id,
                pillar="outcome",
                status=Status.CANT_TEST,
                points=0.0,
                max_points=float(max_pts),
                finding="behavioral-runs-failed",
                remediation="",
                evidence=dict(evidence),
            )
            for (_key, check_id, max_pts) in _CHECKPOINT_CHECKS
        ]
        cant.append(
            CheckResult(
                check_id="trust_live_session",
                pillar="trust",
                status=Status.CANT_TEST,
                points=0.0,
                max_points=_TRUST_LIVE_MAX,
                finding="behavioral-runs-failed",
                remediation="",
                evidence=dict(evidence),
            )
        )
        return cant

    n = len(valid)
    checks: list[CheckResult] = []
    for key, check_id, max_pts in _CHECKPOINT_CHECKS:
        passes = [r for r in valid if r.checkpoints.get(key)]
        pass_count = len(passes)
        fraction = pass_count / n
        points = float(max_pts) * fraction

        if fraction == 1.0:
            status = Status.PASS
        elif fraction == 0.0:
            status = Status.FAIL
        else:
            status = Status.PARTIAL

        # Blockers that mention this checkpoint's failures — cite for remediation.
        run_blockers = sorted({b for r in valid if not r.checkpoints.get(key) for b in r.blockers})

        finding, remediation = _finding_for(key, check_id, status, fraction)

        evidence: dict = {
            "valid_runs": n,
            "pass_count": pass_count,
            "checkpoint": key,
            "blockers": run_blockers,
        }
        if all_trust_events:
            evidence["trust_events"] = all_trust_events
        if multi_trial:
            evidence["pass_fraction"] = round(fraction, 3)
            # "consistent" = every valid run agreed on this checkpoint.
            evidence["consistent"] = pass_count in (0, n)

        # SPECIAL: no_human_gate failing in ALL valid runs -> grade-cap slug.
        if key == "no_human_gate" and fraction == 0.0:
            finding = "human-gate-required"  # grade-cap slug
            gate_blockers = sorted(
                {b for r in valid for b in r.blockers}
            ) or ["a human-only step (CAPTCHA / KYC / email loop / sales call) blocks purchase"]
            evidence["blockers"] = gate_blockers
            remediation = (
                "Expose an API purchase path payable without a human step "
                "(x402 or a checkout API) so an agent can complete the "
                "transaction end-to-end; remove CAPTCHA/KYC/email-loop/sales-call gates."
            )

        checks.append(
            CheckResult(
                check_id=check_id,
                pillar="outcome",
                status=status,
                points=round(points, 3),
                max_points=float(max_pts),
                finding=finding,
                remediation=remediation,
                evidence=evidence,
            )
        )

    checks.append(_trust_live_check(valid, all_trust_events))

    return checks


def _trust_live_check(valid: list[BehavioralRun], all_trust_events: list[str]) -> CheckResult:
    """Trust as it manifested DURING the live directed session (rubric v0.2).

    A run is clean when it reported no trust_events; a run that hesitated or
    would warn the user earns half weight. Warnings never FAIL this check —
    under directive framing a warning still converts; refusal signal lives in
    the trust panel's cap.
    """
    n = len(valid)
    clean = [r for r in valid if not r.trust_events]
    warned = [r for r in valid if r.trust_events]
    weight = (len(clean) + 0.5 * len(warned)) / n
    points = _TRUST_LIVE_MAX * weight

    evidence = {
        "valid_runs": n,
        "clean_runs": len(clean),
        "warned_runs": len(warned),
        "trust_events": all_trust_events,
        "by_run": [
            {"model": r.model, "trial": r.trial, "trust_events": r.trust_events}
            for r in valid
        ],
    }

    if not warned:
        return CheckResult(
            check_id="trust_live_session",
            pillar="trust",
            status=Status.PASS,
            points=round(points, 3),
            max_points=_TRUST_LIVE_MAX,
            finding="trust-live-clean",
            remediation="",
            evidence=evidence,
        )

    return CheckResult(
        check_id="trust_live_session",
        pillar="trust",
        status=Status.PARTIAL,
        points=round(points, 3),
        max_points=_TRUST_LIVE_MAX,
        finding="trust-live-warnings",
        remediation=(
            "Shopper agents surfaced trust concerns while working the site: "
            + ("; ".join(all_trust_events[:4]) if all_trust_events else "unspecified")
            + ". Address these so a directed agent completes the task without "
            "warning its user."
        ),
        evidence=evidence,
    )


def _finding_for(
    key: str, check_id: str, status: Status, fraction: float
) -> tuple[str, str]:
    """Descriptive finding slug + concrete remediation per checkpoint/status."""
    if status == Status.PASS:
        return f"{check_id}-ok", ""

    # partial vs fail share the same remediation direction; slug distinguishes.
    suffix = "missing" if fraction == 0.0 else "inconsistent"
    remediations = {
        "found_product": (
            "Make the product/service matching common agent tasks discoverable "
            "(clear product pages, llms.txt, schema.org Product)."
        ),
        "understood_pricing": (
            "Publish concrete, machine-readable pricing (server-rendered price "
            "in HTML or a pricing API) rather than 'contact us'."
        ),
        "found_purchase_path": (
            "Document a concrete purchase/provisioning path an agent can follow "
            "(a checkout or API-key/subscription flow, discoverable from the site)."
        ),
        "machine_payable_path": (
            "Expose an API purchase path payable without a human step — x402 or "
            "a checkout API — so payment is programmatic, not browser-only."
        ),
        "no_human_gate": (
            "Remove human-only gates (CAPTCHA, KYC/identity verification, "
            "email-confirmation loop, sales call) from the purchase path."
        ),
    }
    return f"{check_id}-{suffix}", remediations.get(key, "")
