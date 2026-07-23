"""Tests for the behavioral attribution boundary (invariant #4).

Runnable directly, no pytest required:

    python tests/test_attribution.py

Invariant #4 (playbook): *agent-side environment failures are never scored as
site evidence, and site failures are never excused as environment; when in
doubt, CANT_TEST — a site is never punished for what couldn't be observed.*

That boundary lives in :mod:`asrs.behavioral.shopper`:
  - ``_is_env_blocked`` decides whether a run's own hosting stack (not the site)
    refused to load the URL, and
  - ``_aggregate`` routes env-blocked runs OUT of the outcome/trust denominators
    and INTO the ``hosted_agent_reachability`` access signal.

It is the mechanism that makes a behavioral score *truthful* about the site
rather than about the agent's environment — yet before this suite it was tested
only INDIRECTLY, through downstream consumers (reliability/quotability/battery),
all reusing a single happy-path phrase. This suite pins the classifier and the
denominator routing in BOTH directions, including the previously-untested
negative cases: a site-side block (403 / Cloudflare) must NOT be excused as
environment, and a run that gathered any evidence keeps its verdict.

All fixtures are synthetic ``BehavioralRun`` records — no network, no CLIs.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.behavioral import shopper as S  # noqa: E402
from asrs.types import BehavioralRun, Status  # noqa: E402

_KEYS = ["found_product", "understood_pricing", "found_purchase_path",
         "machine_payable_path", "no_human_gate"]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(model="claude", trial=1, blockers=None, trust_events=None, **cp) -> BehavioralRun:
    """A verdict-producing run: checkpoints default False, override by keyword."""
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(
        model=model, trial=trial, checkpoints=checkpoints,
        blockers=list(blockers or []), trust_events=list(trust_events or []),
    )


def _by_id(checks) -> dict:
    return {c.check_id: c for c in checks}


# ---------------------------------------------------------------------------
# 1. Positive classification: own-stack refusals, both phrase orderings and
#    across the security-* vocabulary the regex covers, whether the language
#    lands in blockers OR in trust_events (a codex refusal can surface as either).
#    The sibling "safety"-phrased family (v0.6) is pinned separately in #9.
# ---------------------------------------------------------------------------
def test_env_block_positive_phrasings() -> None:
    print("test_env_block_positive_phrasings")
    positives = [
        # order A: block-word ... security-phrase
        "navigation blocked by browser security policy",
        "the request was refused on security grounds by my browser",
        "loading was denied by the browser security controls",
        # order B: security-phrase ... block-word
        "browser security policy blocked this navigation",
        "browser security controls rejected the page load",
    ]
    for i, phrase in enumerate(positives):
        # in blockers
        r = _run(model="codex", trial=i, blockers=[phrase])
        _check(S._is_env_blocked(r), f"blocker env-block detected: {phrase!r}")
        # same phrase carried as a trust_event (refusal framing) is also caught
        r2 = _run(model="codex", trial=i, trust_events=[phrase])
        _check(S._is_env_blocked(r2), f"trust_event env-block detected: {phrase!r}")


# ---------------------------------------------------------------------------
# 2. Negative classification (CRITICAL — the second attribution error):
#    a SITE-side block is a real access finding, NOT an environment artifact,
#    and must never be excused. If these were misclassified, a genuinely
#    agent-hostile site would be quietly lifted out of the scoring denominator.
# ---------------------------------------------------------------------------
def test_site_side_blocks_are_not_excused() -> None:
    print("test_site_side_blocks_are_not_excused")
    site_side = [
        "site returned 403 Forbidden to the agent user-agent",
        "a Cloudflare challenge page blocked the request",
        "the server responded 429 Too Many Requests",
        "robots.txt disallows the /shop path for our crawler",
        "hit a CAPTCHA wall before the product page",
    ]
    for i, phrase in enumerate(site_side):
        r = _run(model="claude", trial=i, blockers=[phrase])
        _check(not S._is_env_blocked(r),
               f"site-side block NOT excused as environment: {phrase!r}")


# ---------------------------------------------------------------------------
# 3. Guard: a run that gathered ANY evidence keeps its verdict, even if a
#    blocker mentions browser security — a partial block is not a full block.
# ---------------------------------------------------------------------------
def test_partial_evidence_keeps_verdict() -> None:
    print("test_partial_evidence_keeps_verdict")
    r = _run(model="codex", found_product=True,
             blockers=["navigation blocked by browser security policy"])
    _check(not S._is_env_blocked(r),
           "run with a passed checkpoint is NOT env-blocked despite block language")


# ---------------------------------------------------------------------------
# 4. A crashed/unparsed run (no checkpoints dict at all) is a plain failure,
#    not an environment block — even if its error text mentions security.
# ---------------------------------------------------------------------------
def test_no_checkpoints_is_not_env_block() -> None:
    print("test_no_checkpoints_is_not_env_block")
    r = BehavioralRun(model="codex", trial=1, checkpoints={},
                      blockers=["run-failed: browser security policy crashed the cli"])
    _check(not S._is_env_blocked(r),
           "empty-checkpoints failure is not classified as env-block")


# ---------------------------------------------------------------------------
# 5. Denominator routing (the core v0.4 fix): an env-blocked run is EXCLUDED
#    from the outcome/trust denominators and surfaces instead as reachability.
#    One valid run (2 checkpoints passed) + one env-blocked run -> outcome
#    fractions are computed over n=1, so a passed checkpoint reads PASS, not
#    PARTIAL. If the env-blocked run leaked into the denominator it would read
#    PARTIAL (1/2) — so PASS here is the proof of exclusion.
# ---------------------------------------------------------------------------
def test_env_blocked_excluded_from_outcome_denominator() -> None:
    print("test_env_blocked_excluded_from_outcome_denominator")
    valid = _run(model="claude", trial=1, found_product=True, understood_pricing=True)
    blocked = _run(model="codex", trial=1,
                   blockers=["navigation blocked by browser security policy"])
    checks = _by_id(S._aggregate("example.com", [valid, blocked]))

    _check(checks["bhv_found_product"].status == Status.PASS,
           "found_product PASS (denominator n=1, env-blocked run excluded)")
    _check(checks["bhv_found_product"].evidence["valid_runs"] == 1,
           "outcome denominator counts only the 1 valid run")
    _check(checks["bhv_understood_pricing"].status == Status.PASS,
           "understood_pricing PASS over the valid run only")
    _check(checks["bhv_purchase_path"].status == Status.FAIL,
           "purchase_path FAIL (0/1 on the valid run)")

    reach = checks["hosted_agent_reachability"]
    _check(reach.pillar == "access", "reachability is an ACCESS-pillar signal")
    _check(reach.status == Status.PARTIAL,
           "reachability PARTIAL (1 reached / 1 blocked)")
    _check(reach.evidence["reached_runs"] == 1 and reach.evidence["blocked_runs"] == 1,
           "reachability evidence records 1 reached + 1 blocked")
    _check("codex" in reach.evidence["blocked_by_model"],
           "the blocked model is attributed in reachability evidence")


# ---------------------------------------------------------------------------
# 6. When ALL runs are env-blocked, the site is NOT punished: every outcome
#    check is CANT_TEST (never FAIL), and reachability records the total block.
#    This is invariant #4's "when in doubt, CANT_TEST" applied end-to-end.
# ---------------------------------------------------------------------------
def test_all_env_blocked_is_cant_test_not_fail() -> None:
    print("test_all_env_blocked_is_cant_test_not_fail")
    runs = [
        _run(model="codex", trial=1,
             blockers=["navigation blocked by browser security policy"]),
        _run(model="codex", trial=2,
             trust_events=["refused to continue on browser security grounds"]),
    ]
    checks = _by_id(S._aggregate("example.com", runs))
    for _key, cid, _mx in S._CHECKPOINT_CHECKS:
        _check(checks[cid].status == Status.CANT_TEST,
               f"{cid} is CANT_TEST when nothing was observed (not FAIL)")
    _check(checks["trust_live_session"].status == Status.CANT_TEST,
           "trust_live_session CANT_TEST when no valid run observed the site")
    reach = checks["hosted_agent_reachability"]
    _check(reach.status == Status.FAIL and reach.points == 0.0,
           "reachability FAIL/0 when every run was blocked from the site")
    _check(reach.finding == "hosted-agents-blocked-all",
           "all-blocked reachability carries the hosted-agents-blocked-all slug")


# ---------------------------------------------------------------------------
# 7. All runs reached the site -> reachability is a full PASS and adds no
#    penalty; the outcome denominator is the full valid population.
# ---------------------------------------------------------------------------
def test_all_reached_full_reachability() -> None:
    print("test_all_reached_full_reachability")
    runs = [_run(model="claude", trial=1, found_product=True),
            _run(model="codex", trial=1, found_product=True)]
    checks = _by_id(S._aggregate("example.com", runs))
    reach = checks["hosted_agent_reachability"]
    _check(reach.status == Status.PASS, "reachability PASS when all runs reached")
    _check(reach.points == S._REACHABILITY_MAX, "full reachability points on all-reached")
    _check(checks["bhv_found_product"].evidence["valid_runs"] == 2,
           "both runs count toward the outcome denominator")


# ---------------------------------------------------------------------------
# 8. Documented coverage boundary (feeds the [LOCAL] codex investigation).
#    The classifier keys off explicit browser-security vocabulary. A hosted-
#    browser REPUTATION-gate refusal ("this domain is flagged as unsafe"),
#    which the loop has observed from codex on the canonical .com but whose
#    exact transcript is not yet committed, does NOT contain that vocabulary
#    and is therefore currently NOT classified as env-blocked. We pin the
#    present behaviour deliberately: broadening the regex blind — without the
#    real transcript — would risk the opposite, worse error (excusing a
#    genuine site-side block, test #2). Resolving this gap is a [LOCAL] task:
#    capture the codex reputation-gate transcript, then extend the pattern
#    with a fixture drawn from it. When that lands, THIS assertion should be
#    updated in lockstep — its failure is the intended signal that the
#    attribution boundary moved.
# ---------------------------------------------------------------------------
def test_reputation_gate_phrasing_is_current_coverage_gap() -> None:
    print("test_reputation_gate_phrasing_is_current_coverage_gap")
    reputation_gate = [
        "I can't help with visiting this site",
        "this domain has been flagged as potentially unsafe",
        "I'm unable to browse that URL",
    ]
    for i, phrase in enumerate(reputation_gate):
        r = _run(model="codex", trial=i, trust_events=[phrase])
        # NOT desired behaviour — a documented gap; see the docstring above.
        _check(not S._is_env_blocked(r),
               f"reputation-gate phrasing is the KNOWN coverage gap: {phrase!r}")


# ---------------------------------------------------------------------------
# 9. v0.6: the "safety"-phrased sibling of the browser-security family. The SAME
#    hosted-browser URL-safety layer surfaces its block as either word — codex on
#    the canonical .org reported "blocked by browser safety controls" in one trial
#    while its siblings on the same domain said "security". Fixtures are the LITERAL
#    committed transcript strings (runs/local/trial_stability_20260723T064359Z.json),
#    per invariant #3. Before v0.6 this all-false verdict LEAKED into the outcome
#    denominator (invariant #4 violation); pin BOTH that it now classifies as
#    env-blocked AND that it routes to reachability, not outcome/trust.
# ---------------------------------------------------------------------------
def test_env_block_safety_phrasing_covered() -> None:
    print("test_env_block_safety_phrasing_covered")
    # Drawn verbatim from the committed trial-stability artifact (codex t3).
    safety_blocker = "drift-flight.org was blocked by browser safety controls"
    safety_trust = "Browser safety controls explicitly blocked the domain."
    # positive classification, in blockers AND as a trust_event
    _check(S._is_env_blocked(_run(model="codex", trial=3, blockers=[safety_blocker])),
           f"safety blocker classified env-blocked: {safety_blocker!r}")
    _check(S._is_env_blocked(_run(model="codex", trial=3, trust_events=[safety_trust])),
           f"safety trust_event classified env-blocked: {safety_trust!r}")
    # other phrase orderings of the same family
    for phrase in ("refused to continue on browser safety grounds",
                   "the page load was denied by the browser safety policy"):
        _check(S._is_env_blocked(_run(model="codex", blockers=[phrase])),
               f"safety-family phrasing classified env-blocked: {phrase!r}")

    # denominator routing: one valid claude run + one safety-blocked codex run ->
    # outcome computed over n=1 (a passed checkpoint reads PASS, not PARTIAL), and
    # the blocked run surfaces as reachability. Mirrors #5 for the safety family.
    valid = _run(model="claude", trial=1, found_product=True)
    blocked = _run(model="codex", trial=3, blockers=[safety_blocker])
    checks = _by_id(S._aggregate("drift-flight.org", [valid, blocked]))
    _check(checks["bhv_found_product"].status == Status.PASS,
           "found_product PASS — safety-blocked run excluded from denominator (n=1)")
    _check(checks["bhv_found_product"].evidence["valid_runs"] == 1,
           "outcome denominator counts only the 1 valid run")
    reach = checks["hosted_agent_reachability"]
    _check(reach.status == Status.PARTIAL and reach.evidence["blocked_runs"] == 1,
           "safety-blocked codex run counted as reachability, not site evidence")
    _check("codex" in reach.evidence["blocked_by_model"],
           "the safety-blocked model is attributed in reachability evidence")


def main() -> int:
    tests = [
        test_env_block_positive_phrasings,
        test_site_side_blocks_are_not_excused,
        test_partial_evidence_keeps_verdict,
        test_no_checkpoints_is_not_env_block,
        test_env_blocked_excluded_from_outcome_denominator,
        test_all_env_blocked_is_cant_test_not_fail,
        test_all_reached_full_reachability,
        test_reputation_gate_phrasing_is_current_coverage_gap,
        test_env_block_safety_phrasing_covered,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL: {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
