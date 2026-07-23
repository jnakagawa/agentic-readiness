"""Canonical-pair replay regression guard — the in-cloud proxy for the live re-score.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_canonical_replay.py

The playbook's per-cycle rule is to LIVE-static-re-score the canonical pair
(drift-flight.org vs driftflight.com) every shipping cycle as a REGRESSION
SIGNAL. The cloud loop has no outbound network (STATE.md environment
constraint), so that live re-score cannot run in-cloud — both canonical hosts
return NOT SCORABLE. Cycle 15 built ``FetchContext`` record/replay as the
offline proxy; a [LOCAL] fire (2026-07-23T16:46Z) captured the two committed
fixtures below from ONE live static crawl of each domain (46.1 F / 85.5 B on
rubric v0.7).

This test is the last piece: it replays each committed fixture through the
CURRENT probe + scoring pipeline (no network) and asserts the canonical numbers.
It converts the per-cycle "delta unchanged by construction" PROSE into an
EXECUTABLE guard — the cloud-adapted form of "re-score every shipping cycle".
Any scoring/probe change that would have moved the canonical score now fails a
test instead of shipping silently.

When a rubric version bump LEGITIMATELY moves the canonical score, the fixtures
are re-captured [LOCAL] (``asrs.cli score --record-fixture``) and the EXPECTED
numbers below are updated in the SAME PR — the guard tracks intended change,
it does not forbid it.

No network: every request is served from the fixture's recorded response cache;
a request the fixture does not cover surfaces as a ``replay-miss`` (asserted
absent below — a miss means a probe changed WHAT it fetches, which must fail
loudly rather than silently rescore against a partial fixture).
"""

from __future__ import annotations

import os
import sys

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs import scoring  # noqa: E402
from asrs.cli import _run_probes  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402

_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# The canonical numbers pinned on rubric v0.7 (captured LIVE [LOCAL] 16:46Z and
# reproduced byte-faithfully offline). Update these — and re-capture the fixtures
# — together, in the same PR, whenever a version bump legitimately moves a score.
EXPECTED = {
    "drift-flight.org": {
        "overall": 46.1,
        "grade": "F",
        "rubric_version": "0.7",
        "pillars": {
            "access": 100.0,
            "legibility": 36.36363636363637,
            "transactability": 18.75,
            "trust": 60.0,
            "outcome": None,
        },
    },
    "driftflight.com": {
        "overall": 85.5,
        "grade": "B",
        "rubric_version": "0.7",
        "pillars": {
            "access": 100.0,
            "legibility": 90.9090909090909,
            "transactability": 87.5,
            "trust": 60.0,
            "outcome": None,
        },
    },
}
EXPECTED_DELTA = 39.4  # driftflight.com (rails) - drift-flight.org (no rails)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _score_fixture(domain: str):
    """Replay ``fixtures/canonical/<domain>.json`` through the real pipeline.

    Returns ``(report, replay_misses)`` where ``replay_misses`` is the list of
    cache keys whose recorded/served result carries a ``replay-miss`` error —
    i.e. probe requests the fixture does not cover.
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    checks = _run_probes(ctx)
    report = scoring.score(checks, scoring.load_rubric(None), domain)
    misses = [
        key for key, res in ctx._cache.items()
        if res.error and "replay-miss" in res.error
    ]
    return report, misses


def _assert_domain(domain: str) -> None:
    exp = EXPECTED[domain]
    report, misses = _score_fixture(domain)

    # (a) The fixture must cover every probe request — a miss means a probe
    # changed WHAT it fetches, so the score is no longer a like-for-like re-score.
    _check(not misses, f"{domain}: no replay-miss (fixture covers every probe request)")

    # (b) The headline number, grade, and rubric version are the pinned canonical values.
    _check(
        report.overall_score == exp["overall"],
        f"{domain}: overall_score == {exp['overall']} (got {report.overall_score})",
    )
    _check(
        report.grade == exp["grade"],
        f"{domain}: grade == {exp['grade']!r} (got {report.grade!r})",
    )
    _check(
        report.rubric_version == exp["rubric_version"],
        f"{domain}: rubric_version == {exp['rubric_version']!r} "
        f"(got {report.rubric_version!r})",
    )
    _check(report.scored is True, f"{domain}: report is scored (not NOT-SCORABLE)")

    # (c) Pillar scores unchanged — a finer regression signal than the roll-up:
    # a probe change could move a pillar while leaving the rounded overall equal.
    for pillar, want in exp["pillars"].items():
        got = report.pillar_scores.get(pillar)
        if want is None:
            _check(got is None, f"{domain}: pillar {pillar} is None (no result)")
        else:
            _check(
                got is not None and abs(got - want) < 1e-6,
                f"{domain}: pillar {pillar} == {want} (got {got})",
            )


# ---------------------------------------------------------------------------
# 1. Each canonical fixture replays to its pinned score on rubric v0.7.
# ---------------------------------------------------------------------------
def test_canonical_org_replays_46_1() -> None:
    print("test_canonical_org_replays_46_1")
    _assert_domain("drift-flight.org")


def test_canonical_com_replays_85_5() -> None:
    print("test_canonical_com_replays_85_5")
    _assert_domain("driftflight.com")


# ---------------------------------------------------------------------------
# 2. The capability DELTA (the number the benchmark exists to defend) is +39.4:
#    the with-rails side wins by the recorded margin, pinned offline. If a rigor
#    change narrows or widens this, THIS test is the tripwire that forces the
#    LOG entry to explain it in capability terms (or not ship).
# ---------------------------------------------------------------------------
def test_canonical_delta_is_39_4() -> None:
    print("test_canonical_delta_is_39_4")
    org, org_misses = _score_fixture("drift-flight.org")
    com, com_misses = _score_fixture("driftflight.com")
    _check(not org_misses and not com_misses, "no replay-miss on either domain")
    delta = round(com.overall_score - org.overall_score, 1)
    _check(
        delta == EXPECTED_DELTA,
        f"canonical delta (.com - .org) == {EXPECTED_DELTA} (got {delta})",
    )


def main() -> int:
    tests = [
        test_canonical_org_replays_46_1,
        test_canonical_com_replays_85_5,
        test_canonical_delta_is_39_4,
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
