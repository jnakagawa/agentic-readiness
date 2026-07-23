"""Tests for within-panel verdict reliability (rubric-agnostic layer, Cycle 3).

Runnable directly, no pytest required:

    python tests/test_reliability.py

Covers the load-bearing behaviours with synthetic ``BehavioralRun`` fixtures
(no network, no CLIs):
  - stability is measured over VALID runs only (env-blocked + failed runs are
    excluded, exactly as the per-task score excludes them);
  - < 2 valid runs -> single_trial, metrics None, never a site failure (the
    honest "not quotable yet" state);
  - unanimous runs -> stability 1.0, no flips; a split checkpoint appears in
    flipped_checkpoints in ladder order and lowers stability by the right amount;
  - the trust-event flip (refuse/warn <-> clean) is a SEPARATE dimension from the
    checkpoint ladder and does not perturb verdict_stability;
  - the descriptive band label tracks the stability number.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import reliability as R  # noqa: E402
from asrs.types import BehavioralRun  # noqa: E402

_KEYS = ["found_product", "understood_pricing", "found_purchase_path",
         "machine_payable_path", "no_human_gate"]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(model="claude", trial=1, trust_events=None, **cp) -> BehavioralRun:
    """A valid run: checkpoints default False, override by keyword."""
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(
        model=model, trial=trial, checkpoints=checkpoints,
        trust_events=list(trust_events or []),
    )


def _env_blocked_run(model="codex", trial=1) -> BehavioralRun:
    return BehavioralRun(
        model=model, trial=trial,
        checkpoints={k: False for k in _KEYS},
        blockers=["navigation blocked by browser security policy"],
    )


def _failed_run(model="codex", trial=1) -> BehavioralRun:
    return BehavioralRun(model=model, trial=trial, checkpoints={},
                         blockers=["run-failed: cli-error"])


# ---------------------------------------------------------------------------
# 1. Two unanimous runs -> perfectly reproducible.
# ---------------------------------------------------------------------------
def test_unanimous() -> None:
    print("test_unanimous")
    allpass = dict.fromkeys(_KEYS, True)
    rel = R.panel_reliability([_run(trial=1, **allpass), _run(model="codex", **allpass)])
    _check(rel.valid_runs == 2 and not rel.single_trial, "2 valid runs, not single-trial")
    _check(rel.verdict_stability == 1.0, f"stability 1.0, got {rel.verdict_stability}")
    _check(rel.flip_rate == 0.0, "flip_rate 0")
    _check(rel.flipped_checkpoints == [], "no flipped checkpoints")
    _check(rel.trust_events_unanimous is True, "no trust flip")
    _check(rel.label == "stable", f"label stable, got {rel.label!r}")


# ---------------------------------------------------------------------------
# 2. One checkpoint splits -> that checkpoint flips, stability drops by 2/5/n.
# ---------------------------------------------------------------------------
def test_one_flip() -> None:
    print("test_one_flip")
    # Runs agree on all but machine_payable_path (1 pass of 2 -> minority 0.5).
    r1 = _run(trial=1, found_product=True, machine_payable_path=True)
    r2 = _run(model="codex", found_product=True, machine_payable_path=False)
    rel = R.panel_reliability([r1, r2])
    _check(rel.flipped_checkpoints == ["machine_payable_path"],
           f"only machine_payable_path flipped, got {rel.flipped_checkpoints}")
    _check(rel.flip_rate == 0.2, f"flip_rate 0.2, got {rel.flip_rate}")
    # minority_fractions = [0,0,0,0.5,0]; mean 0.1; stability 1-2*0.1 = 0.8
    _check(abs(rel.verdict_stability - 0.8) < 1e-9,
           f"stability 0.8, got {rel.verdict_stability}")
    _check(rel.label == "stable", "0.8 is the stable/mixed boundary -> stable")
    cp = {c.checkpoint: c for c in rel.per_checkpoint}
    _check(cp["machine_payable_path"].agreement == 0.5, "split checkpoint agreement 0.5")
    _check(cp["found_product"].unanimous is True, "agreed checkpoint unanimous")


# ---------------------------------------------------------------------------
# 3. Every checkpoint splits 50/50 -> fully unstable.
# ---------------------------------------------------------------------------
def test_all_flip() -> None:
    print("test_all_flip")
    r1 = _run(trial=1, **dict.fromkeys(_KEYS, True))
    r2 = _run(model="codex", **dict.fromkeys(_KEYS, False))
    rel = R.panel_reliability([r1, r2])
    _check(rel.verdict_stability == 0.0, f"stability 0.0, got {rel.verdict_stability}")
    _check(rel.flip_rate == 1.0, "flip_rate 1.0")
    _check(len(rel.flipped_checkpoints) == 5, "all 5 flipped")
    _check(rel.flipped_checkpoints == _KEYS, "flipped list in ladder order")
    _check(rel.label == "unstable", f"label unstable, got {rel.label!r}")


# ---------------------------------------------------------------------------
# 4. Single valid run -> not assessable (never a site failure).
# ---------------------------------------------------------------------------
def test_single_trial() -> None:
    print("test_single_trial")
    rel = R.panel_reliability([_run(found_product=True)])
    _check(rel.valid_runs == 1 and rel.single_trial, "1 valid -> single_trial")
    _check(rel.verdict_stability is None, "stability None on single trial")
    _check(rel.flip_rate is None and rel.trust_event_agreement is None, "metrics None")
    _check(rel.per_checkpoint == [], "no per-checkpoint rows")
    _check(rel.label == "single-trial", f"label single-trial, got {rel.label!r}")


# ---------------------------------------------------------------------------
# 5. Zero valid runs -> no-signal (not the same as single-trial in the readout).
# ---------------------------------------------------------------------------
def test_no_signal() -> None:
    print("test_no_signal")
    rel = R.panel_reliability([_failed_run(), _env_blocked_run()])
    _check(rel.valid_runs == 0 and rel.single_trial, "0 valid -> single_trial True")
    _check(rel.label == "no-signal", f"label no-signal, got {rel.label!r}")
    _check(rel.verdict_stability is None, "stability None with no signal")


# ---------------------------------------------------------------------------
# 6. env-blocked / failed runs are excluded from the valid denominator.
# ---------------------------------------------------------------------------
def test_valid_selection_mirrors_shopper() -> None:
    print("test_valid_selection_mirrors_shopper")
    allpass = dict.fromkeys(_KEYS, True)
    runs = [
        _run(trial=1, **allpass),
        _run(model="codex", trial=1, **allpass),
        _env_blocked_run(),   # excluded
        _failed_run(),        # excluded
    ]
    rel = R.panel_reliability(runs)
    _check(rel.valid_runs == 2, f"only the 2 real verdicts count, got {rel.valid_runs}")
    _check(rel.verdict_stability == 1.0, "the 2 valid runs agree -> 1.0")


# ---------------------------------------------------------------------------
# 7. Trust-event flip is its own dimension; checkpoints can stay unanimous.
# ---------------------------------------------------------------------------
def test_trust_event_flip_is_separate() -> None:
    print("test_trust_event_flip_is_separate")
    allpass = dict.fromkeys(_KEYS, True)
    r1 = _run(trial=1, trust_events=["would warn the user the site looks unproven"], **allpass)
    r2 = _run(model="codex", trust_events=[], **allpass)
    rel = R.panel_reliability([r1, r2])
    # Checkpoints all agree -> stability untouched by the trust flip.
    _check(rel.verdict_stability == 1.0, "checkpoint stability unaffected by trust flip")
    _check(rel.flipped_checkpoints == [], "no checkpoint flips")
    _check(rel.trust_events_unanimous is False, "trust signal flipped across runs")
    _check(abs(rel.trust_event_agreement - 0.5) < 1e-9,
           f"trust agreement 0.5 (1 warned / 1 clean), got {rel.trust_event_agreement}")


# ---------------------------------------------------------------------------
# 8. Mixed band: a 3-run split lands in the "mixed" label.
# ---------------------------------------------------------------------------
def test_mixed_band() -> None:
    print("test_mixed_band")
    # 3 runs; 2 of 5 checkpoints split 1/2 (minority 1/3 each) -> mean minority
    # = (2 * 1/3)/5 = 0.1333; stability = 1 - 2*0.1333 = 0.733 -> "mixed".
    base = dict.fromkeys(_KEYS, True)
    r1 = _run(trial=1, **base)
    r2 = _run(trial=2, **{**base, "machine_payable_path": False})
    r3 = _run(model="codex", **{**base, "no_human_gate": False})
    rel = R.panel_reliability([r1, r2, r3])
    _check(set(rel.flipped_checkpoints) == {"machine_payable_path", "no_human_gate"},
           f"two checkpoints flipped, got {rel.flipped_checkpoints}")
    _check(0.5 <= rel.verdict_stability < 0.8,
           f"stability in mixed band, got {rel.verdict_stability}")
    _check(rel.label == "mixed", f"label mixed, got {rel.label!r}")


def main() -> int:
    tests = [
        test_unanimous,
        test_one_flip,
        test_all_flip,
        test_single_trial,
        test_no_signal,
        test_valid_selection_mirrors_shopper,
        test_trust_event_flip_is_separate,
        test_mixed_band,
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
