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
    scorer's multi-cap accumulation);
  - reproducibility + citability are VERDICT-POLARITY INVARIANT: reversing the
    direction of every observed outcome (pass<->fail on every checkpoint,
    warned<->clean on the trust posture) leaves verdict_stability, flip_rate, the
    flipped-checkpoint set, trust agreement, the band label AND the citability gate
    unchanged — only the reported per-checkpoint pass_count reflects the flip. The
    metric measures whether the panel AGREED, not WHICH WAY, so a no-rails store's
    unanimous FAIL is exactly as citable as a with-rails store's unanimous PASS
    (Cycle 225 METHOD rigor — the two-sided calibration anchor stated at the
    reliability layer; the metamorphic sibling of the attribution layer's
    host-relabel-invariance guards);
  - reproducibility + citability are PANEL-SIZE (REPLICATION) INVARIANT:
    reproducibility is an agreement RATE, not a head count — replicating every
    valid run k-fold leaves verdict_stability, flip_rate, the flipped set,
    per-checkpoint agreement/unanimity, trust agreement, the band label AND the
    citability verdict byte-identical (only valid_runs and the per-checkpoint
    n/pass_count scale). The anti-gaming complement to polarity invariance: a
    store cannot pad its panel with copies of an agreeing run to buy citability, a
    below-threshold panel stays provisional however many duplicates are stacked on
    it, and a 2/2 unanimous panel is exactly as reproducible as a 10/10 one — with
    a negative control (adding one DISSENTING run must move the metric) proving the
    invariance is specific to replication (Cycle 229 METHOD rigor).
"""

from __future__ import annotations

import itertools
import os
import statistics
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


# ---------------------------------------------------------------------------
# 10. verdict_stability MONOTONICITY + shared CITABILITY THRESHOLD (Cycle 201
#     METHOD rigor). verdict_stability is the single number the whole benchmark's
#     "is this safe to cite?" credibility rests on: the quotability gate reads it
#     to call a panel CITABLE ("reproducible") vs PROVISIONAL ("provisional-
#     unstable"), and the descriptive band label reads it to print stable/mixed/
#     unstable. The point-value tests (1-8) and the order-invariance tripwire (9)
#     pin WHAT it computes and that it ignores arrival order; this pins two
#     load-bearing SHAPE properties they do not:
#       (A) MONOTONICITY — adding disagreement to the panel can only LOWER
#           stability and can only DEGRADE citability (reproducible -> provisional,
#           never the reverse). A refactor that let more disagreement RAISE
#           stability would silently mark a flipping panel citable.
#       (B) THRESHOLD COHERENCE — the "stable" band and the "reproducible" citable
#           verdict cut over at the SAME threshold (_STABLE_MIN), so a reader can
#           never see a "stable" label on a number the gate calls provisional (or
#           vice versa). Proven with a mutation sweep of _STABLE_MIN across a panel
#           whose stability sits at an interior operating point: label and gate
#           must flip TOGETHER at every threshold — which they can only do if
#           quotability has NO independent hardcoded cutoff of its own.
#     Plus an EXHAUSTIVE boundedness+formula check over every possible n=4 panel
#     (reliability depends only on the per-checkpoint pass COUNT, so enumerating
#     pass-count vectors covers every distinct 4-run panel): stability stays in
#     [0, 1] and equals the independent recomputation 1 - 2*mean(minority).
# ---------------------------------------------------------------------------
class _StubReport:
    """Minimal duck for R.quotability (overall_score / scored / behavioral_runs)."""

    def __init__(self, runs):
        self.scored = True
        self.overall_score = 72.0
        self.behavioral_runs = list(runs)


def _panel(n, splits):
    """``n`` valid runs; ``splits`` maps a checkpoint key -> how many of the n runs
    PASS it (unlisted checkpoints pass in all n -> unanimous). Run i passes key k
    iff i < pass_count[k], so key k gets exactly pass_count[k] passes."""
    runs = []
    for i in range(n):
        cp = {k: (i < splits.get(k, n)) for k in _KEYS}
        runs.append(_run(model="m", trial=i, **cp))
    return runs


def _expected_stability(n, pass_counts):
    mins = [min(p, n - p) / n for p in pass_counts]
    return round(1.0 - 2.0 * statistics.fmean(mins), 3)


def test_verdict_stability_is_monotone_and_shares_the_citability_threshold() -> None:
    print("test_verdict_stability_is_monotone_and_shares_the_citability_threshold")

    # --- (A) MONOTONICITY: split an increasing prefix of the 5 checkpoints 1/2 --
    # kf=0..5 split checkpoints -> minority mean kf*0.5/5 -> stability 1 - 0.2*kf,
    # i.e. [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]: a strictly descending ladder.
    stabilities, tags, labels = [], [], []
    for kf in range(len(_KEYS) + 1):
        splits = {_KEYS[j]: 1 for j in range(kf)}  # 1 pass of 2 = a 50/50 split
        runs = _panel(2, splits)
        rel = R.panel_reliability(runs)
        stabilities.append(rel.verdict_stability)
        labels.append(rel.label)
        tags.append(R.quotability(_StubReport(runs)).tag)

    # stability is strictly DECREASING as disagreement grows (never rebounds).
    for a, b in zip(stabilities, stabilities[1:]):
        _check(b < a, f"stability strictly decreases with disagreement: {a} -> {b}")
    _check(stabilities == [1.0, 0.8, 0.6, 0.4, 0.2, 0.0],
           f"stability ladder as constructed, got {stabilities}")

    # Citability degrades MONOTONICALLY: 'reproducible' exactly while stability
    # >= _STABLE_MIN, 'provisional-unstable' after — and once provisional it never
    # returns to reproducible as the panel disagrees more.
    expect_tags = ["reproducible" if s >= R._STABLE_MIN else "provisional-unstable"
                   for s in stabilities]
    _check(tags == expect_tags, f"citability tracks the threshold, got {tags}")
    first_provisional = tags.index("provisional-unstable")
    _check(all(t == "provisional-unstable" for t in tags[first_provisional:]),
           "once provisional, more disagreement never restores citable")
    # NON-VACUOUS: the ladder genuinely spans BOTH citability verdicts and BOTH
    # sides of the label bands, so the monotonicity claim has something to bite on.
    _check("reproducible" in tags and "provisional-unstable" in tags,
           "the constructed ladder exercises both citability verdicts")
    _check({"stable", "unstable"} <= set(labels),
           f"the ladder spans stable..unstable, got {labels}")

    # --- (B) EXHAUSTIVE boundedness + formula over EVERY n=4 panel -------------
    n = 4
    for pass_counts in itertools.product(range(n + 1), repeat=len(_KEYS)):
        splits = {_KEYS[j]: pass_counts[j] for j in range(len(_KEYS))}
        rel = R.panel_reliability(_panel(n, splits))
        _check(0.0 <= rel.verdict_stability <= 1.0,
               f"stability in [0,1] for {pass_counts}, got {rel.verdict_stability}")
        exp = _expected_stability(n, pass_counts)
        _check(abs(rel.verdict_stability - exp) < 1e-9,
               f"stability == 1-2*mean(minority) for {pass_counts}: "
               f"{rel.verdict_stability} vs {exp}")

    # --- (C) THRESHOLD COHERENCE: label 'stable' <-> gate 'reproducible' share --
    #         ONE threshold. Build a panel whose stability is an interior 0.75
    #         (n=8: one checkpoint split 4/4 -> minority .5, one split 1/7 ->
    #         minority .125, rest unanimous -> mean .125 -> 1-2*.125 = 0.75), then
    #         sweep _STABLE_MIN ACROSS 0.75. At every threshold the descriptive
    #         'stable' label and the 'reproducible' citability verdict must agree
    #         about THIS panel — which is only possible if quotability reads the
    #         same _STABLE_MIN the label does. A hardcoded literal in quotability
    #         would desync them at a threshold on the far side of the literal.
    panel = _panel(8, {_KEYS[0]: 4, _KEYS[1]: 1})
    _check(abs(R.panel_reliability(panel).verdict_stability - 0.75) < 1e-9,
           "coherence panel sits at the interior operating point 0.75")

    saved = R._STABLE_MIN
    seen_stable, seen_provisional = False, False
    try:
        for thr in (0.60, 0.70, 0.74, 0.76, 0.80, 0.90):
            R._STABLE_MIN = thr
            rel = R.panel_reliability(panel)
            tag = R.quotability(_StubReport(panel)).tag
            is_stable_label = rel.label == "stable"
            is_citable = tag == "reproducible"
            _check(is_stable_label == is_citable,
                   f"at _STABLE_MIN={thr}: 'stable' label ({is_stable_label}) and "
                   f"'reproducible' gate ({is_citable}) must agree on this panel")
            seen_stable |= is_stable_label
            seen_provisional |= not is_citable
    finally:
        R._STABLE_MIN = saved

    # NON-VACUOUS: the sweep genuinely crossed the boundary (both a citable and a
    # provisional verdict appeared), so the coupling was actually put under strain.
    _check(seen_stable and seen_provisional,
           "the threshold sweep straddled the boundary (both verdicts appeared)")


# ---------------------------------------------------------------------------
# 11. verdict_stability + citability are VERDICT-POLARITY INVARIANT (Cycle 225
#     METHOD rigor). Reliability measures whether the panel AGREED, not WHICH WAY
#     it agreed: reverse the direction of every observed outcome (pass<->fail on
#     every checkpoint, warned<->clean on the trust posture) and every
#     reproducibility/citability field must be unchanged. This is the calibration
#     anchor's two-sidedness stated at the reliability layer — a no-rails store
#     whose panel unanimously FAILS the payment checkpoints has to be exactly as
#     REPRODUCIBLE and as CITABLE as a with-rails store whose panel unanimously
#     PASSES them. If it were not, the citability gate would carry a hidden pro-
#     PASS bias: the "fail" side of the two-sided calibration anchor would look
#     less quotable purely because it failed, which would quietly disqualify the
#     negative anchor the whole calibration rests on. The point-value tests (1-8)
#     pin WHAT it computes, order-invariance (9) that it ignores arrival order,
#     monotonicity+threshold (10) its SHAPE; this pins that it is blind to the
#     SIGN of the verdict — the metamorphic sibling of the attribution layer's
#     host-relabel-invariance guards.
# ---------------------------------------------------------------------------
def _invert(run: BehavioralRun) -> BehavioralRun:
    """The same run with the DIRECTION of every observed outcome reversed:
    every checkpoint verdict negated and the trust posture flipped
    (warned<->clean). The metamorphic transform under test — it changes which way
    the panel voted, nothing about how much it agreed."""
    return BehavioralRun(
        model=run.model, trial=run.trial,
        checkpoints={k: (not v) for k, v in run.checkpoints.items()},
        trust_events=[] if run.trust_events else ["warn: unproven"],
    )


def test_verdict_stability_is_polarity_invariant() -> None:
    print("test_verdict_stability_is_polarity_invariant")

    # --- (A) The crisp two-sided calibration statement: a unanimously-FAILING ---
    #     panel is exactly as reproducible AND as citable as a unanimously-PASSING
    #     one. This is the reliability-layer face of the two-sided calibration
    #     anchor (with-rails PASS / no-rails retail FAIL): reproducibility is a
    #     property of the AGREEMENT, not of the direction agreed on.
    allpass = [_run(model=m, trial=t, **dict.fromkeys(_KEYS, True))
               for m, t in (("claude", 1), ("codex", 1))]
    allfail = [_invert(r) for r in allpass]
    rp = R.panel_reliability(allpass)
    rf = R.panel_reliability(allfail)
    # non-vacuous: the transform genuinely reversed every checkpoint verdict.
    _check(all(c.pass_count == 2 for c in rp.per_checkpoint),
           "PASS panel: every checkpoint passed by both runs")
    _check(all(c.pass_count == 0 for c in rf.per_checkpoint),
           "FAIL panel: every checkpoint failed by both runs (the flip is real)")
    _check(rp.verdict_stability == 1.0 and rf.verdict_stability == 1.0,
           "unanimous PASS and unanimous FAIL are BOTH perfectly reproducible")
    _check(rp.label == rf.label == "stable",
           "both land in the same descriptive band")
    qp = R.quotability(_StubReport(allpass))
    qf = R.quotability(_StubReport(allfail))
    _check(qp.quotable and qf.quotable and qp.tag == qf.tag == "reproducible",
           "a unanimously-FAILING store is exactly as CITABLE as a "
           "unanimously-PASSING one — the gate carries no pro-PASS bias")

    # --- (B) The general metamorphic invariance over an INTERIOR-mix panel ------
    #     (some unanimous, some split, trust posture split). Inverting every run's
    #     verdict polarity leaves every reproducibility/citability field identical;
    #     ONLY the reported per-checkpoint pass_count reflects the flip (n - p).
    base = dict.fromkeys(_KEYS, True)
    v1 = _run("claude", 1, trust_events=["warn: unproven"],
              **{**base, "no_human_gate": False})
    v2 = _run("claude", 2, trust_events=["warn: unproven"],
              **{**base, "machine_payable_path": False, "no_human_gate": False})
    v3 = _run("codex", 1, trust_events=[],
              **{**base, "no_human_gate": False})
    v4 = _run("codex", 2, trust_events=["warn: unproven"],
              **{**base, "found_purchase_path": False,
                 "machine_payable_path": False, "no_human_gate": False})
    panel = [v1, v2, v3, v4]
    inv = [_invert(r) for r in panel]
    rel = R.panel_reliability(panel)
    reli = R.panel_reliability(inv)

    # non-vacuous: a genuine interior operating point with a real mix + split trust.
    _check(abs(rel.verdict_stability - 0.7) < 1e-9
           and 0.0 < rel.verdict_stability < 1.0,
           f"reference panel at a genuine interior 0.7, got {rel.verdict_stability}")
    _check(0 < len(rel.flipped_checkpoints) < len(_KEYS)
           and rel.trust_events_unanimous is False,
           "reference panel mixes flipped/unanimous checkpoints AND splits trust")

    # non-vacuous: inversion really moved the reported pass counts (n - original).
    ref_pc = {c.checkpoint: c.pass_count for c in rel.per_checkpoint}
    inv_pc = {c.checkpoint: c.pass_count for c in reli.per_checkpoint}
    _check(inv_pc != ref_pc,
           "inversion genuinely changed the reported pass counts (non-vacuous)")
    _check(all(inv_pc[k] == rel.valid_runs - ref_pc[k] for k in _KEYS),
           "each reported pass_count reflects the flip exactly: inverted == n - original")

    # THE INVARIANT: every reproducibility/citability field is unchanged.
    d, di = rel.to_dict(), reli.to_dict()
    for fkey in ("valid_runs", "single_trial", "flipped_checkpoints", "flip_rate",
                 "verdict_stability", "trust_event_agreement",
                 "trust_events_unanimous", "label"):
        _check(d[fkey] == di[fkey],
               f"{fkey} invariant under verdict-polarity inversion")
    # per-checkpoint agreement/unanimity are invariant; only pass_count moved.
    for c, ci in zip(rel.per_checkpoint, reli.per_checkpoint):
        _check(c.checkpoint == ci.checkpoint and c.n == ci.n
               and c.agreement == ci.agreement and c.unanimous == ci.unanimous,
               f"{c.checkpoint}: agreement/unanimity invariant "
               "(only pass_count reflects the flip)")

    # and the citability GATE returns the same verdict on the inverted panel.
    q = R.quotability(_StubReport(panel))
    qi = R.quotability(_StubReport(inv))
    _check(q.tag == qi.tag and q.quotable == qi.quotable
           and q.verdict_stability == qi.verdict_stability,
           f"citability gate is polarity-invariant (tag {q.tag!r} both ways)")


# ---------------------------------------------------------------------------
# 12. verdict_stability + citability are PANEL-SIZE (REPLICATION) INVARIANT
#     (Cycle 229 METHOD rigor). Reproducibility is an agreement RATE, not a
#     head count: replicating every valid run k-fold (each outcome-identical run
#     duplicated k times) leaves verdict_stability, flip_rate, the flipped set,
#     per-checkpoint agreement/unanimity, trust agreement, the band label AND the
#     citability verdict byte-identical — ONLY valid_runs scales k-fold. This is
#     the ANTI-GAMING complement to polarity invariance: a store cannot buy
#     citability by padding its panel with copies of an agreeing run, and a panel
#     that sits BELOW the citability threshold stays provisional no matter how many
#     duplicate runs are stacked on it (20 padded runs cannot cross _STABLE_MIN).
#     It is what makes a 2/2 unanimous panel exactly as reproducible as a 10/10
#     one, and it is DISTINCT from trial-order invariance (9): that permutes a
#     FIXED multiset; this changes n while holding the per-checkpoint pass RATE.
#     The metamorphic transform is run-replication; the negative control adds a
#     single DISSENTING run (which changes the rate) and must move the metric,
#     proving the invariance is specifically to replication, not to any change.
# ---------------------------------------------------------------------------
def _replicate(runs: list[BehavioralRun], k: int) -> list[BehavioralRun]:
    """Each run duplicated k times with distinct trial ids (so _valid_runs keeps
    every copy as its own valid draw) but byte-identical observed outcomes — the
    metamorphic transform under test: it scales the panel size, nothing about how
    the panel voted or how much it agreed."""
    return [
        BehavioralRun(
            model=r.model, trial=r.trial * 100 + c,
            checkpoints=dict(r.checkpoints), trust_events=list(r.trust_events),
        )
        for c in range(k)
        for r in runs
    ]


def test_verdict_stability_is_panel_size_invariant() -> None:
    print("test_verdict_stability_is_panel_size_invariant")

    # --- (A) The crisp anti-gaming statement: a panel that sits BELOW the ---------
    #     citability threshold cannot be pushed OVER it by padding with copies.
    #     Two runs split on two checkpoints -> minority mean 2*.5/5 = .2 ->
    #     verdict_stability 0.6 (< _STABLE_MIN 0.8 -> provisional). Replicating that
    #     panel to 4, 6, 20 runs leaves it at 0.6 / provisional every time: extra
    #     agreeing-copy runs are not extra evidence.
    base = dict.fromkeys(_KEYS, True)
    below = [_run("claude", 1, **base),
             _run("codex", 1, **{**base, "machine_payable_path": False,
                                 "no_human_gate": False})]
    ref_below = R.panel_reliability(below)
    ref_tag = R.quotability(_StubReport(below)).tag
    _check(abs(ref_below.verdict_stability - 0.6) < 1e-9
           and ref_below.verdict_stability < R._STABLE_MIN,
           f"seed panel sits below the citability threshold, got "
           f"{ref_below.verdict_stability}")
    _check(ref_tag == "provisional-unstable",
           "seed panel is NOT citable (provisional-unstable)")
    for k in (2, 3, 10):
        rep = _replicate(below, k)
        rel = R.panel_reliability(rep)
        tag = R.quotability(_StubReport(rep)).tag
        _check(rel.valid_runs == 2 * k,
               f"k={k}: panel really grew to {2 * k} valid runs, got {rel.valid_runs}")
        _check(abs(rel.verdict_stability - ref_below.verdict_stability) < 1e-9,
               f"k={k}: verdict_stability unchanged by padding, got "
               f"{rel.verdict_stability}")
        _check(tag == ref_tag == "provisional-unstable",
               f"k={k}: padding with agreeing copies cannot buy citability "
               f"(still {tag})")

    # --- (B) The general metamorphic invariance over an INTERIOR-mix panel --------
    #     (some unanimous, some split, trust posture split). Replicating every run
    #     k-fold leaves EVERY reproducibility/citability field identical; ONLY
    #     valid_runs (and the per-checkpoint n/pass_count that scale with it) move.
    v1 = _run("claude", 1, trust_events=["warn: unproven"],
              **{**base, "no_human_gate": False})
    v2 = _run("claude", 2, trust_events=["warn: unproven"],
              **{**base, "machine_payable_path": False, "no_human_gate": False})
    v3 = _run("codex", 1, trust_events=[],
              **{**base, "no_human_gate": False})
    v4 = _run("codex", 2, trust_events=["warn: unproven"],
              **{**base, "found_purchase_path": False,
                 "machine_payable_path": False, "no_human_gate": False})
    panel = [v1, v2, v3, v4]
    rel = R.panel_reliability(panel)

    # non-vacuous: a genuine interior operating point with a real mix + split trust.
    _check(abs(rel.verdict_stability - 0.7) < 1e-9
           and 0.0 < rel.verdict_stability < 1.0,
           f"reference panel at a genuine interior 0.7, got {rel.verdict_stability}")
    _check(0 < len(rel.flipped_checkpoints) < len(_KEYS)
           and rel.trust_events_unanimous is False,
           "reference panel mixes flipped/unanimous checkpoints AND splits trust")

    for k in (2, 3, 5):
        rep = R.panel_reliability(_replicate(panel, k))
        # non-vacuous: the panel genuinely scaled k-fold.
        _check(rep.valid_runs == len(panel) * k,
               f"k={k}: valid_runs scaled to {len(panel) * k}, got {rep.valid_runs}")
        # THE INVARIANT: every RATE-bearing field is unchanged by replication.
        for fkey in ("single_trial", "flipped_checkpoints", "flip_rate",
                     "verdict_stability", "trust_event_agreement",
                     "trust_events_unanimous", "label"):
            _check(getattr(rep, fkey) == getattr(rel, fkey),
                   f"k={k}: {fkey} invariant under panel replication")
        # per-checkpoint agreement/unanimity are RATES -> invariant; only n and
        # pass_count scale with the panel size.
        for c, cr in zip(rel.per_checkpoint, rep.per_checkpoint):
            _check(c.checkpoint == cr.checkpoint and c.agreement == cr.agreement
                   and c.unanimous == cr.unanimous,
                   f"k={k}: {c.checkpoint} agreement/unanimity invariant")
            _check(cr.n == c.n * k and cr.pass_count == c.pass_count * k,
                   f"k={k}: {c.checkpoint} n/pass_count scale k-fold (non-vacuous)")

    # --- (C) NEGATIVE CONTROL: the invariance is to REPLICATION, not to any -------
    #     panel change. Adding ONE dissenting run changes the pass RATE and MUST
    #     move verdict_stability — otherwise (B) would pass vacuously for a metric
    #     that ignored its input entirely.
    dissent = _run("claude", 9, **{**base, "found_product": False,
                                   "machine_payable_path": False,
                                   "no_human_gate": False})
    moved = R.panel_reliability(panel + [dissent])
    _check(moved.verdict_stability != rel.verdict_stability,
           "adding a DISSENTING run moves the metric (invariance is to "
           f"replication only): {rel.verdict_stability} -> {moved.verdict_stability}")


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
        test_verdict_stability_is_monotone_and_shares_the_citability_threshold,
        test_verdict_stability_is_polarity_invariant,
        test_verdict_stability_is_panel_size_invariant,
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
