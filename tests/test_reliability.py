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
  - the descriptive band label tracks the stability number;
  - the panel's reproducibility verdict is TRIAL-ORDER INVARIANT: reproducibility
    is a property of the SET of run outcomes, not the sequence the shopper
    enumerated its model x trial draws in (Cycle 93 METHOD rigor tripwire — the
    reliability-layer member of the presentation-order invariance family that
    already covers the battery, the leaderboard, offering classification, and the
    scorer's multi-cap accumulation).
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


# ---------------------------------------------------------------------------
# 9. Trial-order invariance (METHOD rigor tripwire): the panel's reproducibility
#    verdict is a property of WHAT the valid runs observed, never of the ORDER the
#    shopper enumerated its model x trial draws in. This is the reliability-layer
#    member of the presentation-order invariance family (battery aggregation,
#    Cycle 73; leaderboard ranking, Cycle 77; offering classification, Cycle 81;
#    scorer multi-cap accumulation, Cycle 85) — the one place it was never pinned,
#    and the load-bearing one: verdict_stability gates the CITABLE vs PROVISIONAL
#    quotability verdict the whole benchmark's credibility rests on, so a latent
#    order-dependence here would silently corrupt "is this number safe to cite?".
#    Order-invariant by construction today (every metric is a COUNT over the valid
#    runs, and the checkpoint rows follow the fixed ladder, not run order); this
#    catches a future refactor that leaks run-order into a count, a selection, or a
#    per-checkpoint row. Non-vacuous: the panel is built so verdict_stability is
#    strictly inside (0, 1) with a genuine mix of unanimous + flipped checkpoints
#    and a split trust signal, and excluded runs (env-blocked + failed) are
#    interleaved so the VALID-RUN SELECTION is exercised for order-independence too
#    (invariant #4 — which draws count must not depend on their arrival position).
# ---------------------------------------------------------------------------
def _orderings(seq):
    """A few DETERMINISTIC reorderings of ``seq`` (no RNG — reproducible): the
    identity, the full reverse, and two rotations, so the valid runs AND the
    interleaved excluded runs arrive in genuinely different positions."""
    s = list(seq)
    n = len(s)
    return [
        list(s),
        list(reversed(s)),
        s[n // 2:] + s[: n // 2],
        s[1:] + s[:1],
    ]


def test_panel_reliability_is_trial_order_invariant() -> None:
    print("test_panel_reliability_is_trial_order_invariant")
    base = dict.fromkeys(_KEYS, True)
    # Four valid runs with a deliberate mix: found_product/understood_pricing
    # unanimous; found_purchase_path 3/4 (minority .25); machine_payable_path 2/2
    # (minority .5); no_human_gate unanimous-False. minority_fractions
    # = [0, 0, .25, .5, 0] -> mean .15 -> verdict_stability 1 - 2*.15 = 0.7 (mixed).
    # Trust: 3 warned / 1 clean -> agreement .75, not unanimous.
    v1 = _run("claude", 1, trust_events=["warn: unproven"],
              **{**base, "no_human_gate": False})
    v2 = _run("claude", 2, trust_events=["warn: unproven"],
              **{**base, "machine_payable_path": False, "no_human_gate": False})
    v3 = _run("codex", 1, trust_events=[],
              **{**base, "no_human_gate": False})
    v4 = _run("codex", 2, trust_events=["warn: unproven"],
              **{**base, "found_purchase_path": False,
                 "machine_payable_path": False, "no_human_gate": False})
    # Interleave two runs that observed nothing — their exclusion must not depend
    # on where they sit in the list.
    runs = [v1, _env_blocked_run(trial=9), v2, v3, _failed_run(trial=9), v4]

    orderings = _orderings(runs)
    ref = R.panel_reliability(orderings[0]).to_dict()

    # (a) NON-VACUOUS — the reference metric is a genuine interior value, not a
    #     trivial 0.0/1.0 an order-dependent bug could not perturb, and the
    #     valid-run SELECTION really dropped the interleaved excluded runs.
    _check(ref["valid_runs"] == 4,
           f"the 4 valid runs count, excluded ones dropped, got {ref['valid_runs']}")
    _check(0.0 < ref["verdict_stability"] < 1.0,
           f"verdict_stability strictly interior (non-trivial), got {ref['verdict_stability']}")
    _check(abs(ref["verdict_stability"] - 0.7) < 1e-9,
           f"verdict_stability 0.7 as constructed, got {ref['verdict_stability']}")
    _check(0 < len(ref["flipped_checkpoints"]) < len(_KEYS),
           f"a genuine mix of flipped + unanimous checkpoints, got {ref['flipped_checkpoints']}")
    _check(ref["trust_events_unanimous"] is False
           and 0.5 < ref["trust_event_agreement"] < 1.0,
           "the trust signal is genuinely split across the runs")

    # (b) NON-VACUOUS — the permutation genuinely reorders the VALID runs (checked
    #     at the exact selection layer under test), so order-invariance is a real
    #     claim about the reordered input, not a no-op.
    def _valid_ids(order):
        return [(r.model, r.trial) for r in R._valid_runs(order)]
    _check(_valid_ids(orderings[0]) != _valid_ids(orderings[1]),
           "the permutation genuinely reorders the valid runs (non-vacuous)")

    # (c) Every metric-bearing field is byte-identical across every arrival order.
    #     Comparing the full to_dict() covers verdict_stability, flip_rate,
    #     flipped_checkpoints (list + ladder order), trust_event_agreement /
    #     unanimity, valid_runs, single_trial, label, AND the per_checkpoint rows
    #     (each checkpoint / n / pass_count / agreement / unanimous), recursively.
    for i, order in enumerate(orderings[1:], start=1):
        got = R.panel_reliability(order).to_dict()
        _check(got == ref,
               f"ordering {i}: PanelReliability byte-identical under reordering")


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
        test_panel_reliability_is_trial_order_invariant,
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
