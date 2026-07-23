"""Tests for the rubric roll-up engine (asrs/scoring.py).

Runnable directly with the venv python, no pytest required:

    .venv/bin/python tests/test_scoring.py

Focus of this suite (rubric v0.5): the NOT-SCORABLE attribution rule and a
regression guard that ordinary, scorable roll-ups are UNCHANGED by it.

The attribution-honesty invariant lives at two layers: each probe already
emits CANT_TEST when it can't observe something, and the roll-up must not turn
a report where NOTHING was observable into a punitive 0.0/F. These are the
first unit tests for the roll-up itself; everything here is offline (synthetic
CheckResults, no network).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import scoring  # noqa: E402
from asrs.types import CheckResult, Status  # noqa: E402


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _rubric() -> dict:
    """The bundled rubric, indexed — the real weights/caps/bands."""
    return scoring.load_rubric()


def _cr(check_id, pillar, status, points, max_points, finding="x"):
    return CheckResult(
        check_id=check_id, pillar=pillar, status=status,
        points=points, max_points=max_points, finding=finding, remediation="",
    )


# ---------------------------------------------------------------------------
# 1. No observable pillar -> NOT SCORABLE (never a punitive 0.0/F).
# ---------------------------------------------------------------------------
def test_all_cant_test_is_not_scorable() -> None:
    print("test_all_cant_test_is_not_scorable")
    # Exactly what the canonical pair produced in a network-blocked env: every
    # check CANT_TEST, so every pillar denominator is empty.
    checks = [
        _cr("robots_ai_crawlers", "access", Status.CANT_TEST, 0.0, 10.0, "robots-fetch-failed"),
        _cr("agent_ua_reachability", "access", Status.CANT_TEST, 0.0, 10.0, "site-unreachable"),
        _cr("llms_txt", "legibility", Status.CANT_TEST, 0.0, 6.0, "fetch-failed"),
        _cr("x402_probe", "transactability", Status.CANT_TEST, 0.0, 8.0, "fetch-failed"),
        _cr("https_hsts", "trust", Status.CANT_TEST, 0.0, 5.0, "fetch-failed"),
    ]
    rep = scoring.score(checks, _rubric(), "unreachable.example")
    _check(rep.scored is False, "scored is False when nothing was observable")
    _check(rep.overall_score is None, "overall_score is None (not 0.0)")
    _check(rep.grade == "N/A", f'grade is "N/A" (not "F"), got {rep.grade!r}')
    _check(rep.caps_applied == [], "no caps applied on a not-scorable report")
    # Findings are still preserved for the reader.
    _check(len(rep.checks) == 5, "all checks retained for the findings view")


def test_empty_checks_is_not_scorable() -> None:
    print("test_empty_checks_is_not_scorable")
    rep = scoring.score([], _rubric(), "empty.example")
    _check(rep.scored is False, "no checks at all => not scorable")
    _check(rep.overall_score is None, "overall None")
    _check(rep.grade == "N/A", "grade N/A")


# ---------------------------------------------------------------------------
# 2. NA-only (free tier not advertised etc.) is also not scorable, not 0/F.
# ---------------------------------------------------------------------------
def test_all_na_is_not_scorable() -> None:
    print("test_all_na_is_not_scorable")
    checks = [
        _cr("bhv_free_tier_transaction", "outcome", Status.NA, 0.0, 5.0, "no-free-tier-advertised"),
    ]
    rep = scoring.score(checks, _rubric(), "na.example")
    _check(rep.scored is False, "NA-only => not scorable")
    _check(rep.overall_score is None, "overall None for NA-only")


# ---------------------------------------------------------------------------
# 3. REGRESSION: one observable pillar is scored exactly as before (the change
#    must be a strict no-op for any domain with >=1 observable pillar).
# ---------------------------------------------------------------------------
def test_single_pillar_unchanged() -> None:
    print("test_single_pillar_unchanged")
    # Access pillar fully passes (20/20); every other pillar unobservable.
    checks = [
        _cr("robots_ai_crawlers", "access", Status.PASS, 10.0, 10.0, "robots-allows-ai-crawlers"),
        _cr("agent_ua_reachability", "access", Status.PASS, 10.0, 10.0, "agent-ua-allowed"),
        _cr("llms_txt", "legibility", Status.CANT_TEST, 0.0, 6.0, "fetch-failed"),
    ]
    rep = scoring.score(checks, _rubric(), "one.example")
    _check(rep.scored is True, "scored True with an observable pillar")
    # Only access applies; renormalized over its own weight -> 100.0.
    _check(rep.overall_score == 100.0, f"overall 100.0 (access 100, alone), got {rep.overall_score}")
    _check(rep.grade == "A+", f"grade A+, got {rep.grade}")


def test_mixed_pillars_scored_and_weighted() -> None:
    print("test_mixed_pillars_scored_and_weighted")
    # access 100 (w .15), legibility 50 (w .20), transactability 0 (w .30).
    # Renormalized: (100*.15 + 50*.20 + 0*.30) / (.15+.20+.30) = 25 / .65 = 38.46..
    checks = [
        _cr("robots_ai_crawlers", "access", Status.PASS, 10.0, 10.0),
        _cr("agent_ua_reachability", "access", Status.PASS, 10.0, 10.0),
        _cr("llms_txt", "legibility", Status.PARTIAL, 3.0, 6.0),
        _cr("x402_probe", "transactability", Status.FAIL, 0.0, 8.0),
    ]
    rep = scoring.score(checks, _rubric(), "mix.example")
    _check(rep.scored is True, "scored True")
    _check(abs(rep.overall_score - 38.5) < 0.06, f"overall ~38.5, got {rep.overall_score}")
    _check(rep.grade == "F", f"grade F (below 60), got {rep.grade}")


# ---------------------------------------------------------------------------
# 4. REGRESSION: caps still bind for a scorable report.
# ---------------------------------------------------------------------------
def test_cap_still_binds_when_scorable() -> None:
    print("test_cap_still_binds_when_scorable")
    # A high-scoring access pillar, but agent-ua-hard-blocked caps overall at 69.
    checks = [
        _cr("robots_ai_crawlers", "access", Status.PASS, 10.0, 10.0, "robots-allows-ai-crawlers"),
        _cr("agent_ua_reachability", "access", Status.FAIL, 0.0, 10.0, "agent-ua-hard-blocked"),
    ]
    rep = scoring.score(checks, _rubric(), "capped.example")
    _check(rep.scored is True, "scored True")
    # access = 50 (10/20); below the 69 cap, so the cap does NOT bind here.
    _check("agent-ua-hard-blocked" not in rep.caps_applied,
           "non-binding cap not recorded (50 < 69)")
    # Now make access high enough that the cap binds.
    checks2 = [
        _cr("robots_ai_crawlers", "access", Status.PASS, 10.0, 10.0, "robots-allows-ai-crawlers"),
        _cr("agent_ua_reachability", "access", Status.PASS, 10.0, 10.0, "agent-ua-hard-blocked"),
    ]
    rep2 = scoring.score(checks2, _rubric(), "capped2.example")
    _check(rep2.overall_score == 69.0, f"overall capped to 69.0, got {rep2.overall_score}")
    _check("agent-ua-hard-blocked" in rep2.caps_applied, "binding cap recorded")


# ---------------------------------------------------------------------------
# 5. to_json survives a null overall (machine consumers read scored/None).
# ---------------------------------------------------------------------------
def test_not_scorable_json_roundtrips() -> None:
    print("test_not_scorable_json_roundtrips")
    import json
    rep = scoring.score(
        [_cr("llms_txt", "legibility", Status.CANT_TEST, 0.0, 6.0, "fetch-failed")],
        _rubric(), "j.example",
    )
    data = json.loads(rep.to_json())
    _check(data["overall_score"] is None, "overall_score serializes as null")
    _check(data["scored"] is False, "scored serializes as false")
    _check(data["grade"] == "N/A", "grade serializes as N/A")


# ---------------------------------------------------------------------------
# 6. Coverage-warning routing: behavioral-only checks are expected-absent in a
#    static run (debug, not warning), while a genuine static gap still warns.
#    This is the fix for the ~12 stderr lines a static run used to emit — noise
#    that buried real gaps and leaked into the local verify runner's captured
#    output. It changes NO score (asserted alongside).
# ---------------------------------------------------------------------------
import logging  # noqa: E402


class _CaptureHandler(logging.Handler):
    """Collect log records so a test can assert on level + message."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _score_capturing(checks, rubric, domain):
    """Run score() with every asrs.scoring log record captured.

    Returns (report, records). Sets the logger level to DEBUG so behavioral
    debug lines are observable, and restores it after.
    """
    log = logging.getLogger("asrs.scoring")
    handler = _CaptureHandler()
    prev_level = log.level
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    try:
        rep = scoring.score(checks, rubric, domain)
    finally:
        log.removeHandler(handler)
        log.setLevel(prev_level)
    return rep, handler.records


def _full_static_checks(rubric):
    """One CheckResult for every NON-behavioral rubric check (a realistic
    static run: static probes always emit a result, even CANT_TEST)."""
    return [
        _cr(c["id"], c["pillar"], Status.CANT_TEST, 0.0, float(c.get("max_points", 1)))
        for c in rubric["checks"]
        if not scoring._is_behavioral_only(c)
    ]


def test_behavioral_absence_is_silent_in_static() -> None:
    print("test_behavioral_absence_is_silent_in_static")
    rubric = _rubric()
    checks = _full_static_checks(rubric)
    _rep, records = _score_capturing(checks, rubric, "static.example")
    warns = [r for r in records if r.levelno >= logging.WARNING]
    _check(warns == [], f"a realistic static run emits ZERO warnings, got {[r.getMessage() for r in warns]}")
    # The behavioral-only absences are still logged — at DEBUG (visible under -v),
    # not silently swallowed.
    debug_msgs = " ".join(r.getMessage() for r in records if r.levelno == logging.DEBUG)
    _check("bhv_found_product" in debug_msgs, "behavioral-only absence recorded at debug")
    _check("trust_live_session" in debug_msgs, "behavioral trust absence recorded at debug")
    _check("trust_panel_willingness" in debug_msgs, "behavioral trust-panel absence recorded at debug")


def test_static_gap_still_warns() -> None:
    print("test_static_gap_still_warns")
    rubric = _rubric()
    # Drop one STATIC check (x402_probe) from an otherwise-complete static run:
    # a genuine coverage gap that must still surface.
    checks = [c for c in _full_static_checks(rubric)
              if getattr(c, "check_id", None) != "x402_probe"]
    _rep, records = _score_capturing(checks, rubric, "gap.example")
    warns = [r.getMessage() for r in records if r.levelno >= logging.WARNING]
    _check(any("x402_probe" in m for m in warns),
           f"an absent STATIC check still warns, got {warns}")
    _check(not any("bhv_" in m for m in warns),
           "behavioral-only checks never warn even when other checks are absent")


def test_unknown_pillar_and_extra_check_warn() -> None:
    print("test_unknown_pillar_and_extra_check_warn")
    rubric = _rubric()
    # A result for a check id NOT in the rubric, and a result on an unknown
    # pillar — both are genuinely unexpected and must stay loud.
    checks = _full_static_checks(rubric) + [
        _cr("not_a_real_check", "access", Status.PASS, 1.0, 1.0),
        _cr("robots_ai_crawlers", "made_up_pillar", Status.PASS, 1.0, 1.0),
    ]
    _rep, records = _score_capturing(checks, rubric, "weird.example")
    warns = " ".join(r.getMessage() for r in records if r.levelno >= logging.WARNING)
    _check("not_a_real_check" in warns, "result not in rubric warns")
    _check("made_up_pillar" in warns, "unknown pillar warns")


def test_warning_routing_does_not_change_score() -> None:
    print("test_warning_routing_does_not_change_score")
    # The SAME observable pillars must score identically whether or not the
    # behavioral checks are present as absent rubric entries (they always are,
    # via the bundled rubric). Warning routing is orthogonal to the math.
    checks = [
        _cr("robots_ai_crawlers", "access", Status.PASS, 10.0, 10.0),
        _cr("agent_ua_reachability", "access", Status.PASS, 10.0, 10.0),
        _cr("llms_txt", "legibility", Status.PARTIAL, 3.0, 6.0),
    ]
    rep, _records = _score_capturing(checks, _rubric(), "score.example")
    # access 100 (w .15), legibility 50 (w .20) -> (15 + 10) / .35 = 71.43
    _check(abs(rep.overall_score - 71.4) < 0.1, f"score unaffected by routing, got {rep.overall_score}")


def main() -> int:
    tests = [
        test_all_cant_test_is_not_scorable,
        test_empty_checks_is_not_scorable,
        test_all_na_is_not_scorable,
        test_single_pillar_unchanged,
        test_mixed_pillars_scored_and_weighted,
        test_cap_still_binds_when_scorable,
        test_not_scorable_json_roundtrips,
        test_behavioral_absence_is_silent_in_static,
        test_static_gap_still_warns,
        test_unknown_pillar_and_extra_check_warn,
        test_warning_routing_does_not_change_score,
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
