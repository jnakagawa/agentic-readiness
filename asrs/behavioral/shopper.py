"""Behavioral shopper panel — live read-only recon by agent CLIs.

For each ``model x trial`` we spawn a headless shopper agent (``claude -p`` with
web tools; ``codex exec`` when it can reach the network) and have it investigate
a domain read-only, reporting a checkpoint ladder as a JSON verdict:

    found_product, understood_pricing, found_purchase_path,
    machine_payable_path, no_human_gate

Raw CLI output is saved per run to ``<out_dir>/transcripts/`` and the checkpoint
verdicts are aggregated into the five ``bhv_*`` outcome checks plus the
``trust_live_session`` trust check (rubric v0.2: in-task trust_events scored as
behavioral trust under a user directive) and the ``hosted_agent_reachability``
access check (rubric v0.4). Runs that fail or don't parse are excluded from
the scoring denominator (CANT_TEST semantics); runs whose OWN hosting stack
refused to load the site are excluded from outcome/trust denominators and
scored as reachability instead — a blocked agent observed nothing about the
site, but its population can't buy from you.

Shares CLI plumbing with :mod:`asrs.behavioral.trust_probe` (subprocess runner,
env scrubbing, last-JSON extraction, codex-usability probe).
"""

from __future__ import annotations

import json
import os
import re
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

# Max points for hosted_agent_reachability (pillar access, rubric v0.4).
_REACHABILITY_MAX = 5.0

# A shopper run whose own hosting stack refused to load the site — the agent's
# URL-safety layer, not the site. Language the models use when their OWN tool
# blocked navigation; deliberately does NOT match site-side blocks (403s,
# Cloudflare challenges), which are real access findings, not artifacts.
# "safety" is a sibling of "security" here (v0.6): the SAME hosted-browser
# URL-safety layer surfaces its block as either word — codex on the canonical
# .org reported "blocked by browser safety controls" in one trial and "browser
# security controls" in its siblings on the same domain. Both name the agent's
# own navigation gate, not the site.
#
# v0.7 (Cycle 269): as the canonical domains aged (~20d), codex's SAME own-tool
# refusals DRIFTED off the "security"/"safety" vocabulary onto phrasings that
# name the gated TOOL instead — "Browser access permission ... was denied",
# "Interactive browser access was declined", "denied by the browser's
# site-permission boundary", "Safety-controlled navigation ... were denied".
# These are genuine AGENT-side blocks (same-run FetchContext.homepage() = HTTP
# 200; codex reached the same domain on sibling trials; reputable example.com
# was never gated) that v0.6 MISSED -> _is_env_blocked False -> mis-scored as
# SITE FAILs (invariant #4 leak; runs/local/codex_reachability_20260805T{204555,
# 214534}Z/). Each new alternative below is SELF-QUALIFIED to the agent's own
# apparatus and carries a negative lookahead rejecting site-side attribution
# ("...denied BY the firewall/server/Cloudflare"), so a real 403 / Cloudflare
# block is STILL never excused — attribution honesty cuts both ways.
# Pure-semantic reputation-gate phrasings that name NO own tool ("flagged as
# unsafe", "unable to browse") remain deliberately out of scope
# (tests/test_attribution.py #8); the own-tool drift is pinned by #12.
_NOT_SITE_ATTRIBUTED = (
    r"(?!\s{0,4}by (?:a |an |the )?"
    r"(?:site|server|origin|host|firewall|cloud\s?flare|gateway|proxy|edge|cdn|waf)\b)"
)
_ENV_BLOCK_RE = re.compile(
    # v0.6: the browser {security,safety} URL-safety layer, both phrase orders.
    r"(?:blocked|rejected|refused|denied)[^.]{0,80}"
    r"(?:browser (?:security|safety)|(?:security|safety) (?:policy|controls|grounds))"
    r"|(?:browser (?:security|safety) (?:policy|controls))[^.]{0,80}"
    r"(?:blocked|rejected|refused|denied)"
    # v0.7 (a): the agent's own browser gate declining/denying ITS access.
    # The gap tolerates a dot INSIDE a token (a domain like "driftflight.com")
    # but stops at a sentence boundary (". "), so a match can't span into an
    # unrelated following sentence. Cycle 284: "browser" made OPTIONAL for the
    # "interactive access" concept (+ "direct browser access") — a LIVE near-miss
    # ("Interactive access to driftflight.com was denied before the homepage
    # loaded.", runs/local/behavioral_canonical_delta_20260806T064733Z/) dropped
    # the word "browser" and leaked past the mandatory-"browser" alternation,
    # counting codex's own hosted-browser refusal as a valid all-false site run
    # (invariant #4). "interactive"/"browser" stay REQUIRED as the own-apparatus
    # anchor so a bare site 403 body ("Access Denied") is never matched.
    # v0.7 (e) (Cycle 296): the trailing "permission" made OPTIONAL too, so a bare
    # "browser access ... denied" is anchored. codex's own-tool refusal drifted a
    # FOURTH time (PR #148 post-merge panel, runs/local/pr148_postmerge_
    # 20260806T184617Z/): driftflight.com codex t2 said "Permitted browser access
    # was denied, and the public web retriever classified the direct URL as unsafe
    # to open." while the SAME-run FetchContext.homepage() = HTTP 200 and codex t1
    # reached the site in full. "browser access" ALONE — not "interactive/direct
    # browser access", not "browser access permission", not v0.7(d)'s "denied BY
    # the browser permission ..." — slipped every branch, so the all-false refusal
    # counted a VALID WITH-side SITE run (.com valid_runs 1->2), NARROWING the
    # behavioral delta by scoring codex's OWN hosted-browser refusal as site
    # evidence (the exact invariant-#4 leak). "browser access" (not a bare
    # "access") stays REQUIRED and _NOT_SITE_ATTRIBUTED still rejects "...denied BY
    # the server/WAF/Cloudflare", so a site 403 body ("Access Denied") and any
    # site-attributed block are STILL never excused. Pinned by
    # tests/test_attribution.py #15.
    # v0.7 (f) (Cycle 296): the SITE-access qualifier made OPTIONAL too, so
    # "browser SITE-access permission ... declined" is anchored. codex's own-tool
    # refusal drifted a FIFTH time (PR #149 post-merge panel, runs/local/
    # pr149_postmerge_20260806T204850Z/ -> run record runs/drift-flight_org_
    # 20260806T205238.json, codex t2, .org NO-rails side): "Browser site-access
    # permission for drift-flight.org was declined, preventing direct read-only
    # inspection." while the SAME-run FetchContext.homepage() = HTTP 200 and codex
    # t1 on the SAME panel was correctly caught by the v0.6 "browser security layer"
    # branch. The apparatus is "browser SITE-access permission" -- not "browser
    # access" (v0.7(a)/(e) require "access" ADJACENT to "browser"), not possessive
    # "browser's" (v0.7(b)), and the block verb "declined" FOLLOWS the noun rather
    # than "declined BY the browser permission ..." (v0.7(d)) -- so it slipped EVERY
    # branch, and the all-false refusal counted a VALID .org SITE run, NARROWING the
    # behavioral delta by scoring codex's OWN hosted-browser refusal as site evidence
    # (the exact invariant-#4 leak). The OPTIONAL "(?:site[- ])?" accepts the
    # "site-"/"site " qualifier while "browser ... access" (with "access" still
    # REQUIRED after "browser") keeps a bare site 403 body ("Access Denied") unmatched
    # and _NOT_SITE_ATTRIBUTED intact -- a site-attributed "...declined BY the
    # server/WAF/Cloudflare" is STILL never excused (both directions). A strict
    # SUPERSET of v0.7(e) (the added group is optional): a differential leak-scan over
    # all 1417 committed run-record string leaves flips EXACTLY this one text
    # OLD->NEW, ZERO collateral, ZERO loss. Pinned by tests/test_attribution.py #16.
    r"|(?:interactive(?: browser)? access|direct browser access|browser (?:site[- ])?access(?: permission)?)"
    r"(?:[^.]|\.(?=\S)){0,60}?"
    r"(?:denied|declined|refused|rejected|blocked)" + _NOT_SITE_ATTRIBUTED +
    # v0.7 (b): the browser's OWN site-permission / safety boundary as the gate.
    r"|browser['’]s (?:site[- ]permission|safety|security) "
    r"(?:boundary|layer|policy|controls?|system)"
    # v0.7 (c): the hosted safety layer controlling the agent's navigation.
    r"|safety[- ]controlled (?:navigation|fetch(?:ing|ers?)?)"
    r"(?:[^.]|\.(?=\S)){0,60}?"
    r"(?:denied|declined|refused|rejected|blocked)" + _NOT_SITE_ATTRIBUTED +
    # v0.7 (d) (Cycle 287): the browser's OWN "permission" gate named WITHOUT the
    # apostrophe-s AND WITHOUT the "site-" qualifier, acting as the DENIER of
    # access. codex's own-tool vocabulary drifted a THIRD time (Cycle 286 post-#147
    # panel, runs/local/pr147_postmerge_20260806T084420Z/): "Browser access ... was
    # denied by the browser permission policy." / "...denied by the browser
    # permission boundary." — no possessive "browser's", "permission" not
    # "site-permission", so both slipped past v0.7(b) and were mis-scored as valid
    # all-false SITE runs (.com valid_runs 2->3, .org 3->4), narrowing the
    # behavioral delta by counting codex's OWN hosted-browser refusal as site
    # evidence (invariant #4). This branch is TIGHTER than v0.7(b)'s standalone
    # possessive form precisely because the bare "browser permission policy" is
    # ambiguous (cf. "grant the browser permission to use your camera"): it fires
    # ONLY when a block word is PAIRED with the apparatus AS THE DENIER — a literal
    # "...denied/blocked BY (the) browser permission {boundary|policy|layer|
    # controls}". "by" makes the browser gate the AGENT of the denial, so a
    # site-actor subject ("the server denied the browser permission policy") never
    # matches, and _NOT_SITE_ATTRIBUTED keeps a real "...denied BY the
    # server/WAF/Cloudflare" out (attribution honesty, both directions). Pinned by
    # tests/test_attribution.py #14.
    r"|(?:denied|declined|refused|rejected|blocked)" + _NOT_SITE_ATTRIBUTED +
    r"\s+by\s+(?:a |an |the )?"
    r"browser['’]?s? (?:site[- ])?permission (?:boundary|policy|layer|controls?)"
    # v0.7 (g) (Cycle 317 / Local 20260808T230000Z): the block verb PRECEDES the
    # own-apparatus, joined by a LOCUS/AGENT preposition other than v0.7(d)'s "by",
    # so "...denied AT the browser permission boundary" is anchored. codex's own-tool
    # refusal drifted a SIXTH time (this fire's $0 codex-reachability recon,
    # runs/local/codex_reachability_20260808T214615Z/): driftflight.com codex t2 said
    # "Live-site access was denied at the browser permission boundary." while the
    # SAME-run FetchContext.homepage() = HTTP 200 (site UP) and codex t1 on the SAME
    # panel was correctly caught by the v0.6 "browser security policy" branch. It
    # slipped EVERY branch because the VERB precedes the apparatus: v0.7(a)/(e)/(f)
    # need "browser ... access ... <verb>" in that order (here "access" binds to
    # "Live-site" and "browser" only appears trailing), it is not possessive
    # "browser's" (v0.7(b)), and the connector is "at" not "by" (v0.7(d) requires
    # "by"). The all-false refusal would count a VALID .com SITE run, NARROWING the
    # behavioral delta by scoring codex's OWN hosted-browser refusal as site evidence
    # (the exact invariant-#4 leak). The own-apparatus anchor is a browser-NAMED
    # "boundary" GOVERNED by a locus/agent preposition (at|by|behind|within|under|via)
    # — one is "denied AT/BY a boundary", not "denied FROM" one — so a site 403 body
    # ("Access Denied"), a site-side "denied at the firewall boundary" (apparatus is
    # NOT a browser), and a "...denied; retry FROM the browser permission boundary"
    # recovery aside all stay unmatched, and _NOT_SITE_ATTRIBUTED keeps a real
    # "...denied BY the server/WAF/Cloudflare ... boundary" out (attribution honesty,
    # both directions). A strict SUPERSET (a new alternation): a differential leak-scan
    # over the committed run-record string leaves flips EXACTLY this one text OLD->NEW,
    # ZERO collateral. Pinned by tests/test_attribution.py #17.
    r"|(?:denied|declined|refused|rejected|blocked)" + _NOT_SITE_ATTRIBUTED +
    r"(?:[^.]|\.(?=\S)){0,40}?"
    r"\b(?:at|by|behind|within|under|via)\s+(?:a |an |the )?"
    r"browser (?:permission|access) boundary",
    re.I,
)


def _is_env_blocked(run: BehavioralRun) -> bool:
    """True when the run's own environment blocked the site and it observed nothing.

    Requires BOTH: self-reported own-tool block language, and zero passed
    checkpoints. A run that was partially blocked but still gathered evidence
    (e.g. via web search) keeps its verdict.
    """
    if not run.checkpoints or any(run.checkpoints.values()):
        return False
    text = " ".join(run.blockers + run.trust_events)
    return bool(_ENV_BLOCK_RE.search(text))


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
        # Hermetic panel: ignore the operator's filesystem MCP config so the
        # shopper does NOT boot the machine's full MCP fleet (trigger/unity/
        # linear/motherduck/...) before browsing. Those servers add ~1 min of
        # startup PER PANEL and pull unrelated external connections into the
        # measurement environment; the shopper only needs WebFetch/WebSearch
        # (below). --strict-mcp-config + no --mcp-config == zero MCP servers.
        "--strict-mcp-config",
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
    # Runs whose own hosting stack refused the site observed nothing about it:
    # they are excluded from outcome/trust denominators (v0.4 attribution fix)
    # and surface instead as the hosted_agent_reachability access signal.
    env_blocked = [r for r in runs if _is_env_blocked(r)]
    valid = [r for r in runs if r.checkpoints and r not in env_blocked]
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
            # Self-labeled per-run rows, ordered by the (model, trial) label so
            # the evidence is byte-identical regardless of panel arrival order
            # (matches the sort-before-emit siblings block_statements/refusing_
            # models; would leak if panel construction ever parallelizes).
            "by_run": [
                {"model": r.model, "trial": r.trial, "blockers": r.blockers,
                 "transcript": r.transcript_path}
                for r in sorted(runs, key=lambda r: (r.model, r.trial))
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
        reach = _reachability_check(valid, env_blocked)
        if reach is not None:
            cant.append(reach)
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

    reach = _reachability_check(valid, env_blocked)
    if reach is not None:
        checks.append(reach)

    return checks


def _reachability_check(
    valid: list[BehavioralRun], env_blocked: list[BehavioralRun]
) -> CheckResult | None:
    """Hosted-agent reachability (pillar access, rubric v0.4).

    Some agent stacks gate which sites their agents may load (hosted URL-safety
    / reputation layers). A run whose own stack refused the site is not
    evidence about the site's content — but it IS evidence that part of the
    agent population cannot reach the storefront at all. Scored as the
    fraction of verdict-producing runs that reached the site. Returns None
    when nothing was attempted (static mode / all runs crashed).
    """
    reached = len(valid)
    blocked = len(env_blocked)
    n = reached + blocked
    if n == 0:
        return None

    evidence = {
        "reached_runs": reached,
        "blocked_runs": blocked,
        "blocked_by_model": sorted({r.model for r in env_blocked}),
        # Sorted distinct set, capped — order-invariant like every sibling
        # evidence field above (blocked_by_model / all_trust_events /
        # failure_reasons / run_blockers). A panel re-run with the same runs in
        # a different arrival order must quote the SAME refusals (points/status
        # are already order-invariant counts; this makes the citable evidence
        # surface reproduce too). See tests/test_attribution.py #11.
        "block_statements": sorted({b for r in env_blocked for b in (r.blockers + r.trust_events)})[:6],
    }
    points = _REACHABILITY_MAX * (reached / n)

    if blocked == 0:
        return CheckResult(
            check_id="hosted_agent_reachability",
            pillar="access",
            status=Status.PASS,
            points=round(points, 3),
            max_points=_REACHABILITY_MAX,
            finding="hosted-agents-reach-site",
            remediation="",
            evidence=evidence,
        )

    status = Status.FAIL if reached == 0 else Status.PARTIAL
    finding = "hosted-agents-blocked-all" if reached == 0 else "hosted-agent-blocked"
    return CheckResult(
        check_id="hosted_agent_reachability",
        pillar="access",
        status=status,
        points=round(points, 3),
        max_points=_REACHABILITY_MAX,
        finding=finding,
        remediation=(
            "A hosted agent stack's own URL-safety layer refused to load the "
            "site — those users cannot reach you at all. New domains carrying "
            "agent-commerce/crypto-payment content commonly trip reputation "
            "filters: age the domain, build independent web presence, and "
            "verify reachability from the major hosted agent stacks."
        ),
        evidence=evidence,
    )


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
        # Ordered by the (model, trial) label, not arrival order, so the trust
        # evidence stays byte-identical under any panel permutation.
        "by_run": [
            {"model": r.model, "trial": r.trial, "trust_events": r.trust_events}
            for r in sorted(valid, key=lambda r: (r.model, r.trial))
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
