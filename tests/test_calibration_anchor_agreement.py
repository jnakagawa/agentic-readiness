"""TRUTH guard: the LIVE calibration-sweep anchors agree with the OFFLINE
fixture-replay baseline.

Runnable directly, no pytest required:

    python tests/test_calibration_anchor_agreement.py

The loop measures the two canonical anchors (drift-flight.org / driftflight.com)
along TWO independent paths that, until now, floated free of each other:

  1. the OFFLINE fixture replay — tests/test_canonical_replay.py replays the
     committed fixtures through the real scorer and pins 46.1 F / 85.5 B /
     +39.4 (rubric v0.7). This is the in-cloud regression floor.
  2. the LIVE population sweep — experiments/calibration_sweep.py re-scores the
     real domains over the network on a cadence and commits a dated
     runs/local/calibration_sweep_*.json; each carries the two anchors under the
     segments api-storefront:{rails,no-rails}-anchor.

Nothing asserted these two paths AGREE. They are measurements of the SAME two
storefronts: if a live re-capture ever drifts from the committed fixture floor,
that is a real calibration signal — either the site changed (the fixtures are
stale and owe a [LOCAL] re-capture) or the live crawl is unstable. This guard
welds the paths together so a divergence in EITHER goes red, giving the
canonical-delta regression check a SECOND, independent witness on live data.

Attribution honesty (invariant #4): a sweep anchor that is not-scorable
(unreachable that cadence) is SKIPPED, never counted as a divergence — a site is
never punished for what could not be observed. Versioned comparability
(invariant #2): only sweeps at the baseline's rubric version are compared; a
different-version sweep is never diffed against a v0.7 floor.

Pure guard: reads committed JSON + imports the replay baseline constants (ONE
source of truth — a legitimate version-bump re-capture that moves
test_canonical_replay.EXPECTED moves this guard's target in lockstep). No
network, no scoring-path import. Off the scoring path, score-neutral — this only
pins that the two committed measurement paths of the anchors agree.
"""
from __future__ import annotations

import glob
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "tests"))

import test_canonical_replay as replay  # noqa: E402  (ONE source of truth for the baseline)

# The two canonical anchors, keyed as they appear both in replay.EXPECTED and in
# each sweep's `rows` (by `domain`). Their sweep `segment` ends with "-anchor".
_ANCHORS = ("drift-flight.org", "driftflight.com")
_BASELINE_VERSION = "0.7"  # asserted == the replay baseline's version below (test 1)
_TOL = 0.05  # overalls are rounded to 0.1 on both paths; this catches any real move


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _committed_sweeps() -> list:
    """Every committed dated sweep, oldest first, as (basename, dict) pairs."""
    out = []
    pattern = os.path.join(_REPO, "runs", "local", "calibration_sweep_*.json")
    for p in sorted(glob.glob(pattern)):
        with open(p) as fh:
            out.append((os.path.basename(p), json.load(fh)))
    return out


def _anchor_row(sweep: dict, domain: str):
    for row in sweep.get("rows", []):
        if row.get("domain") == domain:
            return row
    return None


def _divergences(sweeps, expected, baseline_version, tol=_TOL):
    """Pure comparison shared by the real-evidence and synthetic legs.

    Returns (divergences, n_compared, n_unreachable, n_offversion). A divergence
    is a SCORED, same-version anchor whose overall differs from the fixture-replay
    baseline by more than `tol`. Not-scorable anchors (invariant #4) and
    off-version sweeps (invariant #2) are COUNTED, never compared."""
    divergences = []
    n_compared = n_unreachable = n_offversion = 0
    for label, sweep in sweeps:
        if str(sweep.get("rubric_version")) != baseline_version:
            n_offversion += 1
            continue
        for domain in _ANCHORS:
            row = _anchor_row(sweep, domain)
            if row is None:
                continue
            if not row.get("scored") or row.get("overall") is None:
                n_unreachable += 1
                continue
            exp = float(expected[domain]["overall"])
            got = float(row["overall"])
            n_compared += 1
            if abs(got - exp) > tol:
                divergences.append((label, domain, got, exp))
    return divergences, n_compared, n_unreachable, n_offversion


def _synthetic_sweep(version, org_overall, com_overall, *, com_scored=True):
    """A minimal sweep dict carrying just the two anchor rows (for the teeth legs)."""
    return {
        "rubric_version": version,
        "rows": [
            {
                "domain": "drift-flight.org",
                "segment": "api-storefront:no-rails-anchor",
                "scored": org_overall is not None,
                "overall": org_overall,
            },
            {
                "domain": "driftflight.com",
                "segment": "api-storefront:rails-anchor",
                "scored": com_scored and com_overall is not None,
                "overall": com_overall,
            },
        ],
    }


def test_baseline_version_and_gap_match_replay_guard() -> None:
    print("test_baseline_version_and_gap_match_replay_guard")
    # This file's constants are NOT a second source of truth — they must equal the
    # replay guard's. If a version bump re-captures the fixtures, EXPECTED moves and
    # these assertions drag this whole guard onto the new baseline.
    for domain in _ANCHORS:
        _check(
            replay.EXPECTED[domain]["rubric_version"] == _BASELINE_VERSION,
            f"{domain} replay baseline is rubric v{_BASELINE_VERSION}",
        )
    gap = round(
        float(replay.EXPECTED["driftflight.com"]["overall"])
        - float(replay.EXPECTED["drift-flight.org"]["overall"]),
        1,
    )
    _check(
        gap == replay.EXPECTED_DELTA,
        f"replay baseline gap {gap} == EXPECTED_DELTA {replay.EXPECTED_DELTA}",
    )


def test_committed_sweeps_carry_scored_anchors() -> None:
    print("test_committed_sweeps_carry_scored_anchors")
    # Non-vacuity: without this, a future sweep that silently dropped an anchor
    # would make the agreement test pass by comparing nothing.
    sweeps = _committed_sweeps()
    _check(len(sweeps) >= 1, f"at least one committed sweep exists (got {len(sweeps)})")
    v07 = [(lbl, s) for lbl, s in sweeps if str(s.get("rubric_version")) == _BASELINE_VERSION]
    _check(len(v07) >= 1, f"at least one committed v{_BASELINE_VERSION} sweep (got {len(v07)})")
    both_scored = 0
    for lbl, sweep in v07:
        for domain in _ANCHORS:
            _check(
                _anchor_row(sweep, domain) is not None,
                f"{lbl} carries anchor {domain}",
            )
        rows = [_anchor_row(sweep, d) for d in _ANCHORS]
        if all(r.get("scored") and r.get("overall") is not None for r in rows):
            both_scored += 1
    _check(
        both_scored >= 1,
        f"at least one v{_BASELINE_VERSION} sweep has BOTH anchors scored (got {both_scored})",
    )


def test_live_sweep_anchors_agree_with_replay_baseline() -> None:
    print("test_live_sweep_anchors_agree_with_replay_baseline")
    # THE weld: every scored, same-version live anchor equals the offline fixture
    # floor. n_compared>=2 keeps it non-vacuous (the committed cadence carries
    # 3 sweeps x 2 anchors today).
    sweeps = _committed_sweeps()
    divergences, n_compared, n_unreachable, n_offversion = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(
        divergences == [],
        f"no live anchor diverges from the replay floor (got {divergences})",
    )
    _check(
        n_compared >= 2,
        f"the weld is non-vacuous: >=2 (sweep, anchor) pairs compared (got {n_compared})",
    )
    print(
        f"  .. {n_compared} compared, {n_unreachable} not-scorable (skipped), "
        f"{n_offversion} off-version (skipped)"
    )


def test_live_sweep_gap_matches_expected_delta() -> None:
    print("test_live_sweep_gap_matches_expected_delta")
    # The +39.4 regression delta, seen through the LIVE population path: for every
    # same-version sweep with BOTH anchors scored, com - org == EXPECTED_DELTA.
    sweeps = _committed_sweeps()
    checked = 0
    for lbl, sweep in sweeps:
        if str(sweep.get("rubric_version")) != _BASELINE_VERSION:
            continue
        org = _anchor_row(sweep, "drift-flight.org")
        com = _anchor_row(sweep, "driftflight.com")
        if not (org and com and org.get("scored") and com.get("scored")):
            continue
        gap = round(float(com["overall"]) - float(org["overall"]), 1)
        _check(
            abs(gap - replay.EXPECTED_DELTA) <= _TOL,
            f"{lbl}: live gap {gap} == EXPECTED_DELTA {replay.EXPECTED_DELTA}",
        )
        checked += 1
    _check(checked >= 1, f"at least one live sweep had both anchors scored (got {checked})")


def test_not_scorable_anchor_is_skipped_not_a_divergence() -> None:
    print("test_not_scorable_anchor_is_skipped_not_a_divergence")
    # Invariant #4 teeth: a not-scorable anchor is a REACHABILITY gap, never a
    # divergence. A naive impl treating overall=None as 0.0 would flag an 85.5
    # divergence here; the guard must skip it.
    synth = [("synthetic-unreachable", _synthetic_sweep("0.7", 46.1, None, com_scored=False))]
    divergences, n_compared, n_unreachable, n_offversion = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(divergences == [], f"not-scorable anchor is not a divergence (got {divergences})")
    _check(n_unreachable == 1, f"the not-scorable anchor was counted unreachable (got {n_unreachable})")
    _check(n_compared == 1, f"the reachable anchor (org) was still compared (got {n_compared})")


def test_drifted_live_anchor_is_caught() -> None:
    print("test_drifted_live_anchor_is_caught")
    # Teeth: a real live re-capture that drifted the rails anchor 85.5 -> 70.0 MUST
    # trip the weld. Without this, the agreement test could be silently toothless.
    synth = [("synthetic-drift", _synthetic_sweep("0.7", 46.1, 70.0))]
    divergences, n_compared, _, _ = _divergences(synth, replay.EXPECTED, _BASELINE_VERSION)
    _check(len(divergences) == 1, f"exactly one divergence caught (got {divergences})")
    label, domain, got, exp = divergences[0]
    _check(
        domain == "driftflight.com" and abs(got - 70.0) < 1e-9 and abs(exp - 85.5) < 1e-9,
        f"the drifted rails anchor is the caught divergence (got {divergences[0]})",
    )
    _check(n_compared == 2, f"both anchors were compared (got {n_compared})")


def test_off_version_sweep_is_not_compared() -> None:
    print("test_off_version_sweep_is_not_compared")
    # Invariant #2 teeth: a different-rubric sweep is never diffed against the v0.7
    # floor, even with a wildly wrong anchor overall. Scores compare within a
    # version only.
    synth = [("synthetic-v0.8", _synthetic_sweep("0.8", 999.0, 999.0))]
    divergences, n_compared, n_unreachable, n_offversion = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(divergences == [], f"off-version sweep yields no divergence (got {divergences})")
    _check(n_compared == 0, f"off-version anchors were not compared (got {n_compared})")
    _check(n_offversion == 1, f"the off-version sweep was counted, not diffed (got {n_offversion})")


def main() -> int:
    tests = [
        test_baseline_version_and_gap_match_replay_guard,
        test_committed_sweeps_carry_scored_anchors,
        test_live_sweep_anchors_agree_with_replay_baseline,
        test_live_sweep_gap_matches_expected_delta,
        test_not_scorable_anchor_is_skipped_not_a_divergence,
        test_drifted_live_anchor_is_caught,
        test_off_version_sweep_is_not_compared,
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
