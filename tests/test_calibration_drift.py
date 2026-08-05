"""TRUTH guard for the calibration-population DRIFT diff.

Runnable directly, no pytest required:

    python tests/test_calibration_drift.py

`experiments/calibration_sweep.py` re-runs the shipped static scoring path over
a curated population of real storefronts on a cadence and — since LOCAL Cycle
244 — emits a DRIFT block: per-domain overall movement vs the newest prior dated
sweep, so a real storefront ADDING or REMOVING agentic rails (its score moves)
is VISIBLE, not buried in a re-averaged population. That drift block is the
calibration-against-reality signal, and until now it had zero test coverage.

The property that most needs teeth is invariant #4 applied to the sweep: a
domain going scored<->NOT SCORABLE is a REACHABILITY change, never a capability
move — it must land in `status_changed`, never in `moved`, and must never
pollute the delta statistics (a site is never punished, or credited, for what
could not be observed). The two committed sweeps happen to have NO such
transition this period (`status_changed == []`), so the real-evidence leg alone
can never exercise that branch — hence the synthetic negative-control leg below,
whose teeth are that a naive impl treating NOT SCORABLE as 0.0 would blow up
`max_abs_delta`.

Pure-function guard (`_compute_drift` takes plain dicts): no network, no
scoring-path import beyond the drift helpers themselves. Off the scoring path,
score-neutral — this only pins how the sweep READS its own dated artifacts.
"""
from __future__ import annotations

import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.calibration_sweep import _compute_drift  # noqa: E402

# The two committed dated sweeps (force-added under runs/local/; runs/ is
# gitignored). The 07-28 sweep is the baseline the 08-05 sweep drifted against.
_BASELINE = os.path.join(_REPO, "runs", "local", "calibration_sweep_20260728T234815Z.json")
_CURRENT = os.path.join(_REPO, "runs", "local", "calibration_sweep_20260805T014754Z.json")


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _load(path: str) -> dict:
    with open(path) as fh:
        return json.load(fh)


def test_committed_sweeps_reproduce_their_drift_facts() -> None:
    """Real-evidence (invariant #3): `_compute_drift` over the two committed
    sweeps re-derives the drift facts the 08-05 artifact recorded."""
    baseline = _load(_BASELINE)
    current = _load(_CURRENT)
    drift = _compute_drift(current["rows"], baseline)

    _check(drift is not None, "two committed sweeps yield a drift block")
    _check(drift["baseline_ts"] == "20260728T234815Z", f"baseline_ts, got {drift['baseline_ts']}")
    # 13 domains scored in BOTH the 14-member baseline and the 16-member current.
    _check(drift["n_compared"] == 13, f"13 scored-in-both, got {drift['n_compared']}")
    _check(drift["n_moved"] == 2, f"exactly 2 domains moved over 8 days, got {drift['n_moved']}")
    _check(drift["max_abs_delta"] == 6.8, f"max |Δ| 6.8, got {drift['max_abs_delta']}")

    moved = {m["domain"]: m for m in drift["moved"]}
    # The two real movers, each a single-pillar upward move (see STATE Cycle 244).
    _check(moved["deepai.org"]["delta"] == 6.8, f"deepai +6.8, got {moved['deepai.org']['delta']}")
    _check(moved["allbirds.com"]["delta"] == 5.0, f"allbirds +5.0, got {moved['allbirds.com']['delta']}")
    # THE POPULATION-LEVEL REGRESSION ECHO: the canonical pair is byte-stable
    # across the 8-day cadence (both present in `moved`, both delta 0.0) — the
    # same +39.4 the in-cloud replay guard freezes, seen from the sweep.
    _check(
        moved["driftflight.com"]["delta"] == 0.0 and moved["drift-flight.org"]["delta"] == 0.0,
        "canonical pair unmoved over the cadence (delta 0.0 both)",
    )

    # The population broadened to two NEW storefront TYPES; nothing was dropped.
    _check(
        drift["added_members"] == ["acuityscheduling.com", "ipinfo.io"],
        f"two new members listed, got {drift['added_members']}",
    )
    _check(drift["removed_members"] == [], f"no members removed, got {drift['removed_members']}")
    # No reachability transition this period — the branch real data cannot cover.
    _check(drift["status_changed"] == [], f"no scored<->not-scorable transitions, got {drift['status_changed']}")

    # rei.com is NOT SCORABLE in BOTH sweeps -> it contributes to NEITHER list
    # (invariant #4: unobserved in both = no drift entry, not a zero-delta move).
    names = {m["domain"] for m in drift["moved"]} | {s["domain"] for s in drift["status_changed"]}
    _check("rei.com" not in names, "rei.com (not-scorable in both) is in neither moved nor status_changed")


def test_reachability_transition_is_never_a_move() -> None:
    """Invariant #4, with teeth: a scored<->NOT SCORABLE flip is a reachability
    change, kept out of `moved` and out of the delta stats. The committed data
    has none, so this synthetic case is the only exercise of the branch."""
    baseline = {
        "ts": "BASE",
        "rows": [
            {"domain": "x", "segment": "s", "scored": True, "overall": 90.0},
            {"domain": "y", "segment": "s", "scored": False, "overall": None},
            {"domain": "z", "segment": "s", "scored": True, "overall": 50.0},
        ],
    }
    rows = [
        {"domain": "x", "segment": "s", "scored": False, "overall": None},  # scored -> not
        {"domain": "y", "segment": "s", "scored": True, "overall": 40.0},   # not -> scored
        {"domain": "z", "segment": "s", "scored": True, "overall": 55.0},   # the sole real move
    ]
    drift = _compute_drift(rows, baseline)

    moved = {m["domain"]: m for m in drift["moved"]}
    status = {s["domain"]: s for s in drift["status_changed"]}
    _check(set(moved) == {"z"}, f"only the scored-in-both domain moved, got {set(moved)}")
    _check(moved["z"]["delta"] == 5.0, f"z delta +5.0, got {moved['z']['delta']}")
    _check(set(status) == {"x", "y"}, f"both flips are status changes, got {set(status)}")
    _check(
        status["x"]["baseline"] == 90.0 and status["x"]["current"] == "NOT SCORABLE",
        "scored->not shows the last observed score -> NOT SCORABLE",
    )
    _check(
        status["y"]["baseline"] == "NOT SCORABLE" and status["y"]["current"] == 40.0,
        "not->scored shows NOT SCORABLE -> the newly observed score",
    )
    # TEETH: x's 90.0 baseline is by far the largest would-be magnitude. A naive
    # impl treating NOT SCORABLE as 0.0 would record x delta -90.0 and report
    # max_abs_delta 90.0. Invariant #4 keeps it out -> the stats see only the
    # genuine move. max_abs_delta == 5.0 (NOT 90.0) is what catches the leak.
    _check(drift["n_compared"] == 1, f"one scored-in-both pair, got {drift['n_compared']}")
    _check(drift["n_moved"] == 1, f"one real move, got {drift['n_moved']}")
    _check(drift["max_abs_delta"] == 5.0, f"max |Δ| driven only by the genuine move (not 90.0), got {drift['max_abs_delta']}")


def test_added_and_removed_members_are_listed_not_averaged() -> None:
    """A broadened / trimmed population is legible: new and dropped members are
    named, never silently folded into the compared-in-both statistics."""
    baseline = {
        "ts": "BASE",
        "rows": [
            {"domain": "a", "segment": "s", "scored": True, "overall": 50.0},
            {"domain": "b", "segment": "s", "scored": True, "overall": 60.0},  # dropped
        ],
    }
    rows = [
        {"domain": "a", "segment": "s", "scored": True, "overall": 55.0},
        {"domain": "c", "segment": "s", "scored": True, "overall": 70.0},  # added
    ]
    drift = _compute_drift(rows, baseline)
    _check(drift["added_members"] == ["c"], f"added member listed, got {drift['added_members']}")
    _check(drift["removed_members"] == ["b"], f"removed member listed, got {drift['removed_members']}")
    _check(
        [m["domain"] for m in drift["moved"]] == ["a"],
        f"only the in-both domain contributes a delta, got {[m['domain'] for m in drift['moved']]}",
    )
    _check(drift["n_compared"] == 1, f"n_compared counts in-both only, got {drift['n_compared']}")


def test_no_baseline_yields_no_drift_block() -> None:
    """First sweep of a fresh population (or an unreadable baseline): no drift
    block at all, rather than a misleading empty diff."""
    rows = [{"domain": "a", "segment": "s", "scored": True, "overall": 50.0}]
    _check(_compute_drift(rows, None) is None, "None baseline -> no drift block")
    _check(_compute_drift(rows, {}) is None, "empty baseline -> no drift block")


def test_moved_sorted_by_abs_delta_and_rounded() -> None:
    """Movers are ranked by magnitude (biggest first) so the readout leads with
    the largest real-world drift; deltas round to one decimal like the artifact."""
    baseline = {
        "ts": "BASE",
        "rows": [
            {"domain": "p", "segment": "s", "scored": True, "overall": 20.0},
            {"domain": "q", "segment": "s", "scored": True, "overall": 30.0},
            {"domain": "r", "segment": "s", "scored": True, "overall": 40.0},
        ],
    }
    rows = [
        {"domain": "p", "segment": "s", "scored": True, "overall": 22.34},  # +2.3
        {"domain": "q", "segment": "s", "scored": True, "overall": 25.0},   # -5.0
        {"domain": "r", "segment": "s", "scored": True, "overall": 43.0},   # +3.0
    ]
    drift = _compute_drift(rows, baseline)
    _check(
        [m["domain"] for m in drift["moved"]] == ["q", "r", "p"],
        f"sorted by |delta| desc, got {[m['domain'] for m in drift['moved']]}",
    )
    pdelta = next(m["delta"] for m in drift["moved"] if m["domain"] == "p")
    _check(pdelta == 2.3, f"delta rounds to one decimal (2.34 -> 2.3), got {pdelta}")
    _check(drift["max_abs_delta"] == 5.0, f"max |Δ| is q's 5.0, got {drift['max_abs_delta']}")


def main() -> int:
    tests = [
        test_committed_sweeps_reproduce_their_drift_facts,
        test_reachability_transition_is_never_a_move,
        test_added_and_removed_members_are_listed_not_averaged,
        test_no_baseline_yields_no_drift_block,
        test_moved_sorted_by_abs_delta_and_rounded,
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
