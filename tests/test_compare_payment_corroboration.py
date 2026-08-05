"""Compare-view payment corroboration (Cycle 264, READOUT).

The terminal single card grew a payment-corroboration sub-line under its
Transactability row in Cycle 258 — does the shopper's LIVED payment experience
corroborate the static transactability PREDICTION? The two-column DELTA view
(``asrs.report.render_compare``) carried the with/without transactability delta —
the single most-cited number in the whole benchmark — with NO corroboration for
EITHER side. This test pins the compare view's per-side corroboration annotation
under the Transactability delta row, proving:

  - it reads the SAME signal as the single card and the HTML badge, via the ONE
    shared extraction ``asrs.report._payment_corroboration_state_for`` (which
    calls the pure ``asrs.scorecard.payment_corroboration_state``);
  - both sides that ran a panel get their own corroboration line, each spelling
    its state with the SAME wording the single card uses;
  - it is DISPLAY-ONLY: the OVERALL/DELTA/pillar numbers are byte-for-byte
    identical with and without the annotation (it can never move a score);
  - it SUPPRESSES cleanly — NO line when neither side ran a panel (a static
    compare is byte-for-byte unchanged), and exactly ONE line when only one side
    ran a panel;
  - the single-card sub-line is unchanged by the shared-helper refactor
    (regression guard against the Cycle-258 wording drifting).

Synthetic Report / BehavioralRun / CheckResult fixtures — no network, no CLIs.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import report as report_mod  # noqa: E402
from asrs import scorecard  # noqa: E402
from asrs.types import BehavioralRun, CheckResult, Report, Status  # noqa: E402

_KEYS = (
    "found_product",
    "understood_pricing",
    "found_purchase_path",
    "machine_payable_path",
    "no_human_gate",
)

_COMPARE_PREFIX = "      "  # a corroboration line is indented under the row
_SINGLE_PREFIX = "      payment corroboration:"


def _check(cond, msg) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(model="claude", trial=1, **cp) -> BehavioralRun:
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(model=model, trial=trial, checkpoints=checkpoints)


def _x402(status: Status) -> CheckResult:
    return CheckResult(
        check_id="x402_probe",
        pillar="transactability",
        status=status,
        points=8.0 if status is Status.PASS else 0.0,
        max_points=8.0,
        finding="x402-live" if status is Status.PASS else "no-agent-native-payment",
        remediation="",
    )


def _report(domain="example.com", *, checks=None, runs=None, transactability=87.5,
            overall=70.0, grade="C") -> Report:
    pillars = {"access": 100.0, "transactability": transactability}
    return Report(
        domain=domain,
        rubric_version="0.7",
        generated_at="2026-08-05T00:00:00",
        checks=list(checks or []),
        pillar_scores=pillars,
        overall_score=overall,
        grade=grade,
        scored=True,
        behavioral_runs=list(runs or []),
    )


def _paid_side(domain="driftflight.com") -> Report:
    # WITH rails: predicts payment, reached a payable path in every valid trial.
    return _report(
        domain=domain,
        checks=[_x402(Status.PASS)],
        runs=[_run(trial=1, machine_payable_path=True),
              _run(model="codex", trial=2, machine_payable_path=True)],
        transactability=87.5, overall=85.5, grade="B",
    )


def _wall_side(domain="drift-flight.org") -> Report:
    # WITHOUT rails: predicts no payment, hit the wall in every valid trial.
    return _report(
        domain=domain,
        checks=[_x402(Status.FAIL)],
        runs=[_run(trial=1, machine_payable_path=False),
              _run(model="codex", trial=2, machine_payable_path=False)],
        transactability=62.5, overall=46.1, grade="F",
    )


def _static_side(domain="drift-flight.org", *, transactability=62.5,
                 status=Status.FAIL, overall=46.1, grade="F") -> Report:
    # No behavioral panel — a static-only side (the canonical in-cloud re-score).
    return _report(
        domain=domain,
        checks=[_x402(status)],
        runs=[],
        transactability=transactability, overall=overall, grade=grade,
    )


def _corrob_lines(text: str) -> list[str]:
    return [
        ln for ln in text.splitlines()
        if ln.startswith(_COMPARE_PREFIX) and "payment corroboration:" in ln
    ]


# ---------------------------------------------------------------------------
# 1. Both sides ran a panel: two corroboration lines, one per side, each with
#    the state matching that side's shared decision.
# ---------------------------------------------------------------------------
def test_both_sides_annotated() -> None:
    print("test_both_sides_annotated")
    a, b = _wall_side(), _paid_side()
    text = report_mod.render_compare(a, b)
    lines = _corrob_lines(text)
    _check(len(lines) == 2, f"exactly two corroboration lines, got {len(lines)}")
    without = [ln for ln in lines if ln.startswith("      without ")][0]
    with_ = [ln for ln in lines if ln.startswith("      with ")][0]
    _check("no payment, as predicted" in without,
           f"without side (neutral) confirmed, got {without!r}")
    _check("behaviorally corroborated" in with_,
           f"with side (good) corroborated, got {with_!r}")


# ---------------------------------------------------------------------------
# 2. Same signal: each side's compare text uses the SAME state the shared
#    decision (and the HTML badge) yields — they can never disagree.
# ---------------------------------------------------------------------------
def test_compare_reads_the_shared_signal() -> None:
    print("test_compare_reads_the_shared_signal")
    # (predicted x402 status, reached-per-trial, expected shared state, snippet)
    cases = [
        (Status.PASS, [True, True], "good", "behaviorally corroborated"),
        (Status.FAIL, [False, False], "neutral", "no payment, as predicted"),
        (Status.PASS, [True, False], "warn", "NOT corroborated"),
    ]
    for status, reached, expected, snippet in cases:
        runs = [_run(trial=i + 1, model=f"m{i}", machine_payable_path=h)
                for i, h in enumerate(reached)]
        side = _report(checks=[_x402(status)], runs=runs)
        # The compare helper's decision == the pure shared decision the HTML
        # badge consumes == the state name.
        shared = scorecard.payment_corroboration_state(status is Status.PASS, reached)
        via_report = report_mod._payment_corroboration_state_for(side)
        _check(shared == expected and via_report == expected,
               f"shared/report decision {expected} for {status.value}/{reached}, "
               f"got shared={shared} report={via_report}")
        # And it renders that state's snippet in a compare where this side is B.
        text = report_mod.render_compare(_static_side(), side, "without", "with")
        wline = [ln for ln in _corrob_lines(text) if ln.startswith("      with ")]
        _check(len(wline) == 1 and snippet in wline[0],
               f"compare 'with' line renders {expected} snippet, got {wline}")


# ---------------------------------------------------------------------------
# 3. Display-only: the annotation moves no number. Strip the corroboration
#    lines and every remaining line (OVERALL, DELTA, the pillar rows) is
#    identical to a compare rendered from static-only sides (no annotation).
# ---------------------------------------------------------------------------
def test_compare_annotation_is_display_only() -> None:
    print("test_compare_annotation_is_display_only")
    paneled = report_mod.render_compare(_wall_side(), _paid_side())
    # Static twins carry the SAME domain/scores/x402 status but no panels, so a
    # compare of them differs from the paneled compare ONLY by the annotation.
    static = report_mod.render_compare(
        _static_side("drift-flight.org", transactability=62.5,
                     status=Status.FAIL, overall=46.1, grade="F"),
        _static_side("driftflight.com", transactability=87.5,
                     status=Status.PASS, overall=85.5, grade="B"),
    )
    _check(not _corrob_lines(static), "static compare has no corroboration lines")
    stripped = [ln for ln in paneled.splitlines() if ln not in _corrob_lines(paneled)]
    # The score-bearing rows (everything except the two annotation lines) match
    # the un-annotated static compare exactly.
    _check(stripped == static.splitlines(),
           "stripping the annotation lines yields the un-annotated compare byte-for-byte")


# ---------------------------------------------------------------------------
# 4. Suppression: neither side ran a panel -> NO line (static compare unchanged);
#    exactly one side ran a panel -> exactly ONE line, on that side.
# ---------------------------------------------------------------------------
def test_suppression_and_single_side() -> None:
    print("test_suppression_and_single_side")
    none = report_mod.render_compare(_static_side(), _static_side("driftflight.com"))
    _check(not _corrob_lines(none), "no panel on either side -> no corroboration line")

    only_b = report_mod.render_compare(_static_side(), _paid_side())
    lines_b = _corrob_lines(only_b)
    _check(len(lines_b) == 1 and lines_b[0].startswith("      with "),
           f"only side B paneled -> one 'with' line, got {lines_b}")

    only_a = report_mod.render_compare(_wall_side(), _static_side("driftflight.com"))
    lines_a = _corrob_lines(only_a)
    _check(len(lines_a) == 1 and lines_a[0].startswith("      without "),
           f"only side A paneled -> one 'without' line, got {lines_a}")


# ---------------------------------------------------------------------------
# 5. Regression: the single-card sub-line is UNCHANGED by the shared-helper
#    refactor — the Cycle-258 wording is byte-identical, and it still reads the
#    shared state (the compare and the single card can never diverge).
# ---------------------------------------------------------------------------
def test_single_card_line_unchanged_by_refactor() -> None:
    print("test_single_card_line_unchanged_by_refactor")
    good = _paid_side()
    single = [ln for ln in report_mod.render(good).splitlines()
              if ln.startswith(_SINGLE_PREFIX)]
    _check(len(single) == 1, f"single card still emits one corroboration line, got {single}")
    _check(single[0] ==
           "      payment corroboration: behaviorally corroborated — reached a "
           "machine-payable path in every valid trial",
           f"Cycle-258 wording byte-identical, got {single[0]!r}")
    # Its state equals the shared extraction (same source as the compare line).
    _check(report_mod._payment_corroboration_state_for(good) == "good",
           "single card and compare share one decision source")


# ---------------------------------------------------------------------------
# 6. Teeth: the three states render three DISTINCT compare lines (a copy-paste
#    collapse of the text map cannot pass vacuously).
# ---------------------------------------------------------------------------
def test_states_render_distinct_compare_lines() -> None:
    print("test_states_render_distinct_compare_lines")
    def with_line(status, reached):
        runs = [_run(trial=i + 1, model=f"m{i}", machine_payable_path=h)
                for i, h in enumerate(reached)]
        text = report_mod.render_compare(_static_side(), _report(checks=[_x402(status)], runs=runs),
                                         "without", "with")
        return [ln for ln in _corrob_lines(text) if ln.startswith("      with ")][0]
    good = with_line(Status.PASS, [True, True])
    neutral = with_line(Status.FAIL, [False, False])
    warn = with_line(Status.PASS, [True, False])
    _check(len({good, neutral, warn}) == 3,
           "the three corroboration states render three DISTINCT compare lines")


tests = [
    test_both_sides_annotated,
    test_compare_reads_the_shared_signal,
    test_compare_annotation_is_display_only,
    test_suppression_and_single_side,
    test_single_card_line_unchanged_by_refactor,
    test_states_render_distinct_compare_lines,
]


def main() -> int:
    passed = 0
    for t in tests:
        t()
        passed += 1
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
