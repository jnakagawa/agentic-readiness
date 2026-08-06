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
import re
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


# ---------------------------------------------------------------------------
# 10. Crash-invisibility (invariant #4, denominator level): a run that produced
#     NO verdict (empty checkpoints) and NO env-block language is neither a valid
#     observation NOR an env-block — it observed nothing about the site. #4 pins
#     only the CLASSIFIER (_is_env_blocked -> False); this pins the CONSEQUENCE
#     the score actually depends on: such a crash must dilute NEITHER denominator.
#     It is invisible to `_aggregate` — every check is byte-identical to the panel
#     without it. This is "a site is never punished for what couldn't be observed"
#     in its purest quantitative form: an agent-side segfault that yielded no
#     verdict must not count as a site outcome (inflating the outcome denominator,
#     dragging PASS -> PARTIAL) NOR as a reachability block (dragging reachability
#     PASS -> PARTIAL). A crash sits in a THIRD bucket, counted by nothing.
#
#     Metamorphic form + three-way teeth: adding a CRASH moves nothing, while the
#     two neighbouring perturbations DO move a denominator — an ENV-BLOCKED run
#     drags reachability, and a VALID no-evidence run drags the outcome
#     denominator. So both denominators are demonstrably live, and the crash's
#     invisibility is a real claim about a distinct third bucket, not a no-op on
#     an inert metric. A future refactor that routed a no-verdict crash into
#     either bucket (e.g. counting attempted runs, or treating an unparsed run as
#     blocked) reddens this immediately.
# ---------------------------------------------------------------------------
def _crash(model="codex", trial=9) -> BehavioralRun:
    """A run whose own stack died before any verdict: empty checkpoints, and a
    blocker that is NOT env-block language (a plain crash, not a URL refusal)."""
    return BehavioralRun(
        model=model, trial=trial, checkpoints={},
        blockers=["run-failed: the cli segfaulted before returning a verdict"],
        trust_events=[],
    )


def _sig(checks) -> dict:
    """Comparable signature of an aggregate: per-check status/points/evidence."""
    return {
        c.check_id: (c.status, c.points, c.max_points, c.finding, c.evidence)
        for c in checks
    }


def test_crash_run_is_invisible_to_both_denominators() -> None:
    print("test_crash_run_is_invisible_to_both_denominators")
    # Base panel: two valid runs that both reached the site and passed every
    # checkpoint -> every check at full points, maximum room for any leak to show.
    base = [
        _run(model="claude", trial=1, found_product=True, understood_pricing=True,
             found_purchase_path=True, machine_payable_path=True, no_human_gate=True),
        _run(model="gpt", trial=1, found_product=True, understood_pricing=True,
             found_purchase_path=True, machine_payable_path=True, no_human_gate=True),
    ]
    crash = _crash()

    # NON-VACUOUS: the crash lands in the THIRD bucket by construction — it is not
    # a valid observation (empty checkpoints) and not an env-block (no refusal
    # language), so both `valid` and `env_blocked` exclude it.
    _check(crash.checkpoints == {}, "crash produced no checkpoints (not a valid run)")
    _check(S._is_env_blocked(crash) is False,
           "a plain crash is not an env-block (no URL-refusal language)")

    # THE INVARIANT: adding the crash to the panel changes nothing, anywhere.
    before = _sig(S._aggregate("x.example", base))
    after = _sig(S._aggregate("x.example", base + [crash]))
    _check(before == after,
           "a no-verdict crash is invisible: every check byte-identical with/without it")
    # Spell out the two denominators the invariant protects.
    reach = _by_id(S._aggregate("x.example", base + [crash]))["hosted_agent_reachability"]
    _check(reach.status == Status.PASS and reach.evidence["blocked_runs"] == 0,
           "reachability still full PASS — the crash is NOT counted as blocked")
    _check(_by_id(S._aggregate("x.example", base + [crash]))["bhv_found_product"]
           .evidence["valid_runs"] == 2,
           "outcome denominator still 2 — the crash is NOT counted as a valid run")

    # TEETH #1 — the reachability denominator IS live: an ENV-BLOCKED run (real
    # URL refusal) added to `base` drags reachability off its full PASS. So the
    # crash staying at PASS above is a real claim, not an inert metric.
    blocked_run = _run(model="codex", trial=2,
                       blockers=["the request was blocked by the browser security policy"])
    _check(S._is_env_blocked(blocked_run) is True, "control run is genuinely env-blocked")
    reach_blk = _by_id(S._aggregate("x.example", base + [blocked_run]))["hosted_agent_reachability"]
    _check(reach_blk.status == Status.PARTIAL and reach_blk.points < reach.points,
           "an env-blocked run DOES move reachability (denominator is live)")

    # TEETH #2 — the outcome denominator IS live: a VALID run that reached the
    # site but found nothing (all-false, no env-block language) drags an all-pass
    # outcome check to PARTIAL, while reachability stays PASS (it reached). So the
    # outcome denominator holding at 2 above is a real claim too.
    empty_valid = _run(model="codex", trial=3)  # reached, every checkpoint false
    _check(S._is_env_blocked(empty_valid) is False and empty_valid.checkpoints,
           "control run is a valid no-evidence observation, not a crash")
    with_valid = _by_id(S._aggregate("x.example", base + [empty_valid]))
    _check(with_valid["bhv_found_product"].status == Status.PARTIAL
           and with_valid["bhv_found_product"].evidence["valid_runs"] == 3,
           "a valid no-evidence run DOES enter the outcome denominator (denominator is live)")
    _check(with_valid["hosted_agent_reachability"].status == Status.PASS,
           "the valid no-evidence run still reached the site (reachability unmoved)")


# ---------------------------------------------------------------------------
# 11. Reachability EVIDENCE is order-invariant (reproducibility / TRUTH). The
#     reachability POINTS and STATUS are functions of two counts (reached,
#     blocked) and so were already order-invariant. But the human-readable
#     evidence quoted on the card — ``block_statements`` — was an ARRIVAL-ORDER
#     slice ``[...][:6]``, the lone deviation from the ``sorted({...})`` idiom
#     every sibling evidence field in ``_aggregate`` uses (blocked_by_model,
#     all_trust_events, failure_reasons, run_blockers, gate_blockers). So two
#     panels with the SAME runs shuffled produced the SAME score but a DIFFERENT
#     set of quoted refusals — both which six survived the cap and their order.
#     For a benchmark whose credibility rests on "evidence or it didn't happen"
#     and on citability, an order-dependent evidence surface is a latent
#     reproducibility hole: cite the number today, re-run the panel, quote
#     different refusals. This pins the fix — block_statements is now the sorted
#     distinct set, capped — with real teeth: the >6-distinct fixture makes the
#     cap pick a DIFFERENT set once sorted, and the pre-fix arrival-order slice
#     is shown to have depended on run order while the new one does not.
# ---------------------------------------------------------------------------
def test_reachability_evidence_is_order_invariant() -> None:
    print("test_reachability_evidence_is_order_invariant")
    # Eight DISTINCT, each-independently-valid env-block statements. Chosen so
    # their case-sensitive sort (A,B,C,D,H,L,N,T) differs from the arrival order
    # they are fed in (reverse-sorted), so the [:6] cap selects a different SET
    # depending on ordering — the strongest form of non-vacuity.
    stmts = [
        "Access to the site was blocked by the browser security policy",
        "Browser security controls rejected the page load",
        "Content load was denied on security grounds by the hosted browser",
        "Denied by the browser security controls before the page rendered",
        "Hosted URL-safety refused the navigation on security grounds",
        "Loading was denied by the browser security controls",
        "Navigation blocked by browser security policy",
        "The request was refused on security grounds by my browser",
    ]
    # Feed them in reverse-sorted arrival order, one env-blocked run each.
    arrival = list(reversed(stmts))
    blocked_runs = [_run(model=f"m{i}", trial=1, blockers=[s]) for i, s in enumerate(arrival)]
    for r in blocked_runs:  # NON-VACUOUS: every fixture run is genuinely env-blocked
        _check(S._is_env_blocked(r), f"fixture run is env-blocked: {r.blockers[0]!r}")
    # One valid reached run so reachability is a live PARTIAL (not degenerate).
    valid = [_run(model="claude", trial=1, found_product=True)]

    fwd = valid + blocked_runs
    rev = list(reversed(fwd))
    reach_fwd = _by_id(S._aggregate("x.example", fwd))["hosted_agent_reachability"]
    reach_rev = _by_id(S._aggregate("x.example", rev))["hosted_agent_reachability"]

    # THE PROPERTY: block_statements is the sorted distinct set, capped at 6.
    expected = sorted(set(stmts))[:6]
    _check(reach_fwd.evidence["block_statements"] == expected,
           "block_statements is the sorted distinct set, capped at 6")

    # THE INVARIANT: reversing run arrival order changes NOTHING in the whole
    # reachability CheckResult (status, points, max, finding, every evidence key).
    _check(_sig([reach_fwd]) == _sig([reach_rev]),
           "reachability CheckResult is byte-identical under run-order reversal")

    # NON-VACUOUS at the SET level: the >6 distinct statements make the cap pick a
    # DIFFERENT set once sorted than the arrival-order slice would have — so the
    # sort/dedup visibly changed the surface, it is not a cosmetic no-op.
    old_arrival_slice = [b for r in blocked_runs for b in (r.blockers + r.trust_events)][:6]
    _check(set(old_arrival_slice) != set(expected),
           "the [:6] cap selects a DIFFERENT set arrival-ordered vs sorted (fix is non-vacuous)")

    # TEETH: the PRE-FIX arrival-order slice DID depend on run order — reversing
    # the panel would have changed which refusals were quoted. So the invariant
    # above is a real claim about the fixed code, not something trivially true.
    old_rev_slice = [b for r in list(reversed(blocked_runs)) for b in (r.blockers + r.trust_events)][:6]
    _check(old_arrival_slice != old_rev_slice,
           "the pre-fix arrival-order slice was order-sensitive (guard has teeth)")


# ---------------------------------------------------------------------------
# 12. v0.7: own-tool-vocabulary DRIFT (invariant #4, LIVE-observed). As the
#     canonical domains aged (~20 days), codex's SAME hosted-browser refusals
#     stopped saying "browser {security,safety}" and started naming the gated
#     TOOL instead — "Browser access permission ... was denied", "Interactive
#     browser access was declined", "denied by the browser's site-permission
#     boundary", "Safety-controlled navigation ... were denied". Each is a
#     genuine AGENT-side block: the same-run FetchContext.homepage() shows the
#     SITE at HTTP 200, codex REACHED the same domain on sibling trials, and
#     reputable example.com was NEVER gated — yet v0.6's regex MISSED them, so
#     _is_env_blocked returned False and a real --behavioral run would mis-score
#     them as SITE FAILs (the exact invariant-#4 leak test #8 anticipated).
#     Fixtures are the LITERAL committed transcript strings (invariant #3):
#     runs/local/codex_reachability_20260805T{204555,214534}Z/summary.json.
#
#     The broadening is attribution-honest in BOTH directions: it is SELF-
#     QUALIFIED to the agent's own apparatus and rejects site-side attribution
#     ("...denied BY the firewall/server/Cloudflare"), so a genuine 403 /
#     Cloudflare block is still NOT excused (the second half below). Pure-
#     semantic reputation gates that name no own tool stay out of scope (#8).
# ---------------------------------------------------------------------------
def test_env_block_own_tool_vocab_drift_covered() -> None:
    print("test_env_block_own_tool_vocab_drift_covered")
    # Verbatim own-tool refusals from the two committed 2026-08-05 reachability
    # transcripts. Each is a run that reached NOTHING (all checkpoints false).
    drifted = [
        "Browser access permission to the domain was denied.",
        "Interactive browser access was declined.",
        "Direct browser access to driftflight.com was denied by the "
        "browser's site-permission boundary; no bypass was attempted.",
        "Safety-controlled navigation and direct web fetching of "
        "driftflight.com were denied, preventing inspection of the site itself.",
    ]
    # The SAME drift as a trust_event framing (codex surfaces it either way).
    drifted_trust = "Because safety-controlled fetchers blocked the domain and " \
        "its legitimacy could not be established, purchase would warrant refusal."

    # Pre-broadening TEETH: the v0.6 pattern (the two browser-{security,safety}
    # branches) MISSED every one of these — the guard is non-vacuous.
    v06 = re.compile(
        r"(?:blocked|rejected|refused|denied)[^.]{0,80}"
        r"(?:browser (?:security|safety)|(?:security|safety) (?:policy|controls|grounds))"
        r"|(?:browser (?:security|safety) (?:policy|controls))[^.]{0,80}"
        r"(?:blocked|rejected|refused|denied)",
        re.I,
    )
    for phrase in drifted + [drifted_trust]:
        _check(v06.search(phrase) is None,
               f"v0.6 pattern MISSED this drifted phrasing (teeth): {phrase[:48]!r}")

    # Positive classification, in blockers AND as a trust_event.
    for i, phrase in enumerate(drifted):
        _check(S._is_env_blocked(_run(model="codex", trial=i, blockers=[phrase])),
               f"drifted own-tool blocker classified env-blocked: {phrase[:48]!r}")
    _check(S._is_env_blocked(_run(model="codex", trial=9, trust_events=[drifted_trust])),
           "drifted own-tool trust_event classified env-blocked")

    # ATTRIBUTION HONESTY (the other direction): the broadening must NOT excuse a
    # site-attributed block just because it names "browser access" — a 403 /
    # Cloudflare / firewall refusal is a real access finding, not an artifact.
    site_attributed = [
        "the server denied the browser access after returning a 403 Forbidden",
        "Cloudflare denied the browser access to the protected page",
        "the site's firewall refused the browser access at the edge",
        "browser access permission was denied by the firewall at the origin",
        "interactive browser access was refused by the server's WAF",
        "safety-controlled navigation was blocked by the site gateway",
    ]
    for phrase in site_attributed:
        _check(not S._is_env_blocked(_run(model="claude", blockers=[phrase])),
               f"site-attributed block NOT excused as environment: {phrase[:52]!r}")

    # example.com's genuine "no commercial site" finding (verbatim, same run set)
    # is an OBSERVATION, not a block — it must keep its verdict, never route to
    # reachability. The reputable control that proves the drift is codex's gate.
    example_finding = "The site offers no purchasable product or service. IANA " \
        "reports that POST, PUT, DELETE, and PATCH requests return HTTP 405."
    _check(not S._is_env_blocked(_run(model="codex", blockers=[example_finding])),
           "example.com's genuine no-storefront finding is NOT an env-block")

    # Denominator routing (mirrors #5/#9 for the drifted family): one valid
    # claude run + one drift-blocked codex run -> outcome over n=1 (a passed
    # checkpoint reads PASS, not PARTIAL), blocked run surfaces as reachability.
    valid = _run(model="claude", trial=1, found_product=True)
    blocked = _run(model="codex", trial=2, blockers=[drifted[0]])
    checks = _by_id(S._aggregate("driftflight.com", [valid, blocked]))
    _check(checks["bhv_found_product"].status == Status.PASS,
           "found_product PASS — drift-blocked run excluded from denominator (n=1)")
    _check(checks["bhv_found_product"].evidence["valid_runs"] == 1,
           "outcome denominator counts only the 1 valid run")
    reach = checks["hosted_agent_reachability"]
    _check(reach.status == Status.PARTIAL and reach.evidence["blocked_runs"] == 1,
           "drift-blocked codex run counted as reachability, not site evidence")
    _check("codex" in reach.evidence["blocked_by_model"],
           "the drift-blocked model is attributed in reachability evidence")


# ---------------------------------------------------------------------------
# 13. v0.7 Cycle 284: own-tool "interactive ACCESS ... denied" NEAR-MISS (the
#     word "browser" DROPPED). A fresh --behavioral panel (2026-08-06) caught
#     codex refusing the WITH-rails canonical with a phrasing one word short of
#     the Cycle-269 v0.7(a) alternative — "Interactive access to driftflight.com
#     was denied before the homepage loaded." (no "browser"). v0.7(a) REQUIRED
#     "interactive BROWSER access", so _is_env_blocked returned False, the
#     all-false refusal counted as a VALID site run (valid_runs 2->3,
#     verdict_stability 1.0->0.333) and the WITH side's five bhv_* checks flipped
#     unanimous-PASS -> -inconsistent, NARROWING the delta by scoring codex's OWN
#     hosted-browser refusal as site evidence (the exact invariant-#4 leak).
#     Fixture is the LITERAL committed transcript string (invariant #3):
#     runs/local/behavioral_canonical_delta_20260806T064733Z/transcripts/
#     driftflight.com_codex_t2.json. The broadening makes "browser" OPTIONAL for
#     the "interactive access" concept while KEEPING an own-apparatus anchor
#     ("interactive"/"browser") REQUIRED and the _NOT_SITE_ATTRIBUTED guard
#     intact, so a bare site 403 body ("Access Denied") and any "...denied BY the
#     firewall/server" are STILL never excused (both directions below).
# ---------------------------------------------------------------------------
def test_env_block_interactive_access_near_miss_covered() -> None:
    print("test_env_block_interactive_access_near_miss_covered")
    # The verbatim leaking transcript blocker (all checkpoints false).
    leak = "Interactive access to driftflight.com was denied before the homepage loaded."

    # TEETH: the PRE-Cycle-284 v0.7(a) alternative REQUIRED the word "browser"
    # ("interactive BROWSER access" / "browser access permission"), so it MISSED
    # this phrasing — the broadening is non-vacuous.
    pre284 = re.compile(
        r"(?:interactive browser access|browser access permission)"
        r"(?:[^.]|\.(?=\S)){0,60}?(?:denied|declined|refused|rejected|blocked)",
        re.I,
    )
    _check(pre284.search(leak) is None,
           "pre-284 mandatory-'browser' alternative MISSED the near-miss (teeth)")
    # The shipped broadening classifies it env-blocked, in blockers AND trust.
    _check(S._is_env_blocked(_run(model="codex", trial=2, blockers=[leak])),
           "near-miss own-tool blocker classified env-blocked")
    _check(S._is_env_blocked(_run(model="codex", trial=2, trust_events=[leak])),
           "near-miss own-tool trust_event classified env-blocked")

    # ATTRIBUTION HONESTY (the other direction): the near-miss twin with SITE
    # attribution is a real access finding, never an artifact; and a bare site
    # 403 body carries NO own-apparatus anchor, so it never matches at all.
    site_attributed = [
        "Interactive access to driftflight.com was denied by the site firewall.",
        "interactive access to the store was denied by the origin server",
        "direct browser access was refused by the server's WAF at the edge",
        "the site returned 403 Forbidden; access was denied",  # no interactive/browser anchor
        "Access Denied",                                       # bare 403 body
    ]
    for phrase in site_attributed:
        _check(not S._is_env_blocked(_run(model="claude", blockers=[phrase])),
               f"site-attributed / anchorless block NOT excused: {phrase[:52]!r}")

    # SCOPE BOUNDARY (mirrors #8): a same-transcript sibling that names the agent
    # tools but frames the block as a reputation CLASSIFICATION ("classified ...
    # as unsafe and blocked access") uses the ambiguous 'unsafe' vocabulary and
    # stays DELIBERATELY out of scope this cycle — 'unsafe' is indistinguishable
    # from a site-side WAF 'flagged unsafe'. Documented, not silently dropped.
    rep = ("Both direct browser navigation and read-only web fetching "
           "classified driftflight.com as unsafe and blocked access.")
    _check(not S._is_env_blocked(_run(model="codex", blockers=[rep])),
           "reputation-classification 'unsafe' phrasing stays out of scope (#8 family)")

    # Denominator routing (mirrors #5/#12): one valid claude run + one near-miss
    # blocked codex run -> outcome over n=1 (a passed checkpoint reads PASS), the
    # blocked run surfaces as reachability, not as site evidence.
    valid = _run(model="claude", trial=1, found_product=True)
    blocked = _run(model="codex", trial=2, blockers=[leak])
    checks = _by_id(S._aggregate("driftflight.com", [valid, blocked]))
    _check(checks["bhv_found_product"].status == Status.PASS,
           "found_product PASS — near-miss-blocked run excluded from denominator (n=1)")
    _check(checks["bhv_found_product"].evidence["valid_runs"] == 1,
           "outcome denominator counts only the 1 valid run")
    reach = checks["hosted_agent_reachability"]
    _check(reach.status == Status.PARTIAL and reach.evidence["blocked_runs"] == 1,
           "near-miss-blocked codex run counted as reachability, not site evidence")
    _check("codex" in reach.evidence["blocked_by_model"],
           "the near-miss-blocked model is attributed in reachability evidence")


# ---------------------------------------------------------------------------
# 14. v0.7 Cycle 287: own-tool "denied BY the browser permission boundary/policy"
#     NEAR-MISS (the THIRD drift of the codex refusal vocabulary, after 269 + 284).
#     The Cycle-286 post-#147 panel caught codex refusing BOTH canonical sides with
#     a phrasing that names its own gate as "the browser permission policy" /
#     "the browser permission boundary" — NO possessive "browser's" and "permission"
#     not "site-permission", so it slipped past v0.7(b)'s standalone possessive
#     alternative AND is none of v0.7(a)'s three fixed "...access...denied" forms.
#     Both leaked -> _is_env_blocked False -> the all-false refusals counted as
#     VALID site runs (.com valid_runs 2->3, .org 3->4), NARROWING the behavioral
#     delta by scoring codex's OWN hosted-browser refusal as site evidence (the
#     exact invariant-#4 leak). Fixtures are the LITERAL committed transcript
#     strings (invariant #3): runs/local/pr147_postmerge_20260806T084420Z/
#     transcripts/{driftflight.com,drift-flight.org}_codex_t2.json.
#
#     The v0.7(d) branch is DELIBERATELY tighter than v0.7(b)'s standalone form:
#     bare "browser permission policy" is ambiguous (cf. a UI "grant the browser
#     permission to use your camera"), so it fires ONLY when a block word is paired
#     with the apparatus AS THE DENIER — "...denied/blocked BY (the) browser
#     permission {boundary|policy|layer|controls}". The required "by" makes the
#     browser gate the AGENT of the denial, so a site-actor SUBJECT ("the server
#     denied the browser permission policy") never matches, and _NOT_SITE_ATTRIBUTED
#     keeps a real "...denied BY the server/WAF/Cloudflare" out — attribution honest
#     in BOTH directions (both halves below).
# ---------------------------------------------------------------------------
def test_env_block_permission_boundary_near_miss_covered() -> None:
    print("test_env_block_permission_boundary_near_miss_covered")
    # The two verbatim leaking transcript blockers (all checkpoints false).
    leaks = [
        "Browser access to driftflight.com was denied by the browser permission policy.",
        "Direct read-only browser access to drift-flight.org was denied by the "
        "browser permission boundary.",
    ]

    # TEETH: the PRE-Cycle-287 pattern (through v0.7(c), which REQUIRED the
    # possessive "browser's site-permission" for the permission-gate concept)
    # MISSED both — the broadening is non-vacuous.
    pre287 = re.compile(
        r"browser['’]s (?:site[- ]permission|safety|security) "
        r"(?:boundary|layer|policy|controls?|system)"
        r"|(?:interactive(?: browser)? access|direct browser access|browser access permission)"
        r"(?:[^.]|\.(?=\S)){0,60}?(?:denied|declined|refused|rejected|blocked)",
        re.I,
    )
    for phrase in leaks:
        _check(pre287.search(phrase) is None,
               f"pre-287 pattern MISSED the permission-boundary near-miss (teeth): {phrase[:52]!r}")
        # The shipped v0.7(d) broadening classifies it env-blocked, blockers AND trust.
        _check(S._is_env_blocked(_run(model="codex", trial=2, blockers=[phrase])),
               f"permission-boundary near-miss blocker classified env-blocked: {phrase[:52]!r}")
        _check(S._is_env_blocked(_run(model="codex", trial=2, trust_events=[phrase])),
               f"permission-boundary near-miss trust_event classified env-blocked: {phrase[:52]!r}")

    # ATTRIBUTION HONESTY (the other direction): the apparatus must be the DENIER
    # (paired via "by"). A site-actor SUBJECT of the same phrase, a site-attributed
    # "denied BY the server/WAF", a UI camera-permission grant, and a bare 403 body
    # all carry no own-apparatus-as-denier signal and must NEVER be excused.
    not_env = [
        "the server denied the browser permission policy after returning 403",   # site is the denier
        "Cloudflare denied the browser permission controls at the edge",         # site is the denier
        "browser permission policy was denied by the firewall at the origin",    # site-attributed
        "access was denied by the site gateway despite a permission policy",     # site-attributed
        "You must grant the browser permission to use your camera",              # UI grant, no block-pairing
        "Access Denied",                                                          # bare 403 body
        "the site returned 403 Forbidden; access was denied",                    # site 403, no browser-permission gate
    ]
    for phrase in not_env:
        _check(not S._is_env_blocked(_run(model="claude", blockers=[phrase])),
               f"site-attributed / anchorless block NOT excused: {phrase[:52]!r}")

    # Denominator routing (mirrors #5/#12/#13): one valid claude run + one
    # permission-boundary-blocked codex run -> outcome over n=1 (a passed checkpoint
    # reads PASS), the blocked run surfaces as reachability, not as site evidence.
    valid = _run(model="claude", trial=1, found_product=True)
    blocked = _run(model="codex", trial=2, blockers=[leaks[0]])
    checks = _by_id(S._aggregate("driftflight.com", [valid, blocked]))
    _check(checks["bhv_found_product"].status == Status.PASS,
           "found_product PASS — permission-boundary-blocked run excluded (n=1)")
    _check(checks["bhv_found_product"].evidence["valid_runs"] == 1,
           "outcome denominator counts only the 1 valid run")
    reach = checks["hosted_agent_reachability"]
    _check(reach.status == Status.PARTIAL and reach.evidence["blocked_runs"] == 1,
           "permission-boundary-blocked codex run counted as reachability, not site evidence")
    _check("codex" in reach.evidence["blocked_by_model"],
           "the permission-boundary-blocked model is attributed in reachability evidence")


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
        test_crash_run_is_invisible_to_both_denominators,
        test_reachability_evidence_is_order_invariant,
        test_env_block_own_tool_vocab_drift_covered,
        test_env_block_interactive_access_near_miss_covered,
        test_env_block_permission_boundary_near_miss_covered,
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
