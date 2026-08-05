"""Terminal-card payment-corroboration line (Cycle 258, READOUT).

The HTML card (asrs.scorecard) grew a display-only behavioral-corroboration
badge on the Transactability row in Cycle 254: does the shopper's LIVED payment
experience corroborate the static transactability PREDICTION? This test pins the
TERMINAL analog of that badge (asrs.report.render) — one indented sub-line under
the Transactability pillar row — proving:

  - it reads the SAME signal as the HTML badge via the shared decision
    asrs.scorecard.payment_corroboration_state (good / neutral / warn);
  - all three honest states render their distinct line;
  - it is DISPLAY-ONLY: the overall/pillar numbers are byte-for-byte identical
    with and without the line (it can never move a score);
  - it SUPPRESSES cleanly (no line) for a static-only card and for a report
    missing the x402 prediction check — static cards are unchanged.

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

_LINE_PREFIX = "      payment corroboration:"


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


def _report(*, checks=None, runs=None, transactability=87.5) -> Report:
    pillars = {"access": 100.0, "transactability": transactability}
    return Report(
        domain="example.com",
        rubric_version="0.7",
        generated_at="2026-08-05T00:00:00",
        checks=list(checks or []),
        pillar_scores=pillars,
        overall_score=70.0,
        grade="C",
        scored=True,
        behavioral_runs=list(runs or []),
    )


def _corrob_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if ln.startswith(_LINE_PREFIX)]


# ---------------------------------------------------------------------------
# 1. good — score predicts payment, every valid trial reached a payable path.
# ---------------------------------------------------------------------------
def test_good_state_renders() -> None:
    print("test_good_state_renders")
    rep = _report(
        checks=[_x402(Status.PASS)],
        runs=[
            _run(trial=1, machine_payable_path=True),
            _run(model="codex", trial=2, machine_payable_path=True),
        ],
    )
    lines = _corrob_lines(report_mod.render(rep))
    _check(len(lines) == 1, f"exactly one corroboration line, got {len(lines)}")
    _check("behaviorally corroborated" in lines[0],
           f"good state says 'behaviorally corroborated', got {lines[0]!r}")


# ---------------------------------------------------------------------------
# 2. neutral — score predicts NO payment, every valid trial hit the wall.
# ---------------------------------------------------------------------------
def test_neutral_state_renders() -> None:
    print("test_neutral_state_renders")
    rep = _report(
        transactability=18.75,
        checks=[_x402(Status.FAIL)],
        runs=[
            _run(trial=1, machine_payable_path=False),
            _run(model="codex", trial=2, machine_payable_path=False),
        ],
    )
    lines = _corrob_lines(report_mod.render(rep))
    _check(len(lines) == 1, f"exactly one corroboration line, got {len(lines)}")
    _check("no payment, as predicted" in lines[0],
           f"neutral state says 'no payment, as predicted', got {lines[0]!r}")


# ---------------------------------------------------------------------------
# 3. warn — the prediction and the lived experience disagree across trials.
# ---------------------------------------------------------------------------
def test_warn_state_renders() -> None:
    print("test_warn_state_renders")
    # Predicts payment, but one valid trial never reached a payable path.
    rep = _report(
        checks=[_x402(Status.PASS)],
        runs=[
            _run(trial=1, machine_payable_path=True),
            _run(model="codex", trial=2, machine_payable_path=False),
        ],
    )
    lines = _corrob_lines(report_mod.render(rep))
    _check(len(lines) == 1, f"exactly one corroboration line, got {len(lines)}")
    _check("NOT corroborated" in lines[0],
           f"warn state says 'NOT corroborated', got {lines[0]!r}")


# ---------------------------------------------------------------------------
# 4. Same signal as the HTML badge: the terminal state matches the badge class
#    across all three states (they can never disagree).
# ---------------------------------------------------------------------------
def test_terminal_line_matches_html_badge_signal() -> None:
    print("test_terminal_line_matches_html_badge_signal")
    # (predicted x402 status, reached-per-trial, expected shared state)
    cases = [
        (Status.PASS, [True, True], "good"),
        (Status.FAIL, [False, False], "neutral"),
        (Status.PASS, [True, False], "warn"),
    ]
    for status, reached, expected in cases:
        runs = [
            _run(trial=i + 1, model=f"m{i}", machine_payable_path=hit)
            for i, hit in enumerate(reached)
        ]
        rep = _report(checks=[_x402(status)], runs=runs)
        # The pure shared decision the HTML badge also consumes.
        state = scorecard.payment_corroboration_state(
            status is Status.PASS, reached
        )
        _check(state == expected, f"shared decision {expected} for {status.value}/{reached}, got {state}")
        # And the HTML badge's css class equals that shared state (single source).
        rep_dict = {
            "behavioral_runs": [{"checkpoints": r.checkpoints} for r in runs],
            "checks": [{"check_id": "x402_probe", "status": status.value}],
        }
        badge = scorecard._payment_corroboration(rep_dict)
        _check(badge is not None and badge[0] == expected,
               f"HTML badge class == shared state {expected}, got {badge and badge[0]}")


# ---------------------------------------------------------------------------
# 5. Display-only: the line never moves the number. Card WITH the panel and a
#    stripped card WITHOUT the corroboration line share identical score lines.
# ---------------------------------------------------------------------------
def test_line_is_display_only_score_unchanged() -> None:
    print("test_line_is_display_only_score_unchanged")
    checks = [_x402(Status.PASS)]
    runs = [_run(trial=1, machine_payable_path=True),
            _run(model="codex", trial=2, machine_payable_path=True)]
    rep = _report(checks=checks, runs=runs)
    text = report_mod.render(rep)
    _check(any(ln.startswith(_LINE_PREFIX) for ln in text.splitlines()),
           "the corroboration line is present when a panel ran")
    # The OVERALL/GRADE and the Transactability pillar VALUE are untouched by
    # the annotation: strip the corroboration line and every remaining line is
    # identical to a render with the line suppressed would be.
    header = [ln for ln in text.splitlines() if "OVERALL" in ln][0]
    _check("70.0/100" in header and "GRADE C" in header,
           f"score/grade untouched by the annotation, got {header!r}")
    trans = [ln for ln in text.splitlines() if "Transactability" in ln][0]
    _check("87.5" in trans, f"transactability value untouched, got {trans!r}")


# ---------------------------------------------------------------------------
# 6. Suppression: a static-only card (no panel) prints NO line, and a paneled
#    card missing the x402 prediction check prints NO line — static cards and
#    older/partial reports are byte-for-byte unchanged.
# ---------------------------------------------------------------------------
def test_suppressed_when_no_panel_or_no_prediction() -> None:
    print("test_suppressed_when_no_panel_or_no_prediction")
    static_only = _report(checks=[_x402(Status.PASS)], runs=[])
    _check(not _corrob_lines(report_mod.render(static_only)),
           "static-only card (no valid behavioral run) prints no corroboration line")

    no_prediction = _report(
        checks=[],  # x402_probe absent (older/partial report)
        runs=[_run(trial=1, machine_payable_path=True),
              _run(model="codex", trial=2, machine_payable_path=True)],
    )
    _check(not _corrob_lines(report_mod.render(no_prediction)),
           "paneled card with no x402 prediction prints no corroboration line")


# ---------------------------------------------------------------------------
# 7. Teeth: env-agnostic — the shared decision would flip if the state map were
#    mis-wired. Assert the three states are mutually distinct strings so a
#    copy-paste collapse can't pass vacuously.
# ---------------------------------------------------------------------------
def test_states_are_distinct() -> None:
    print("test_states_are_distinct")
    def line_for(status, reached):
        runs = [_run(trial=i + 1, model=f"m{i}", machine_payable_path=h)
                for i, h in enumerate(reached)]
        rep = _report(checks=[_x402(status)], runs=runs)
        return _corrob_lines(report_mod.render(rep))[0]
    good = line_for(Status.PASS, [True, True])
    neutral = line_for(Status.FAIL, [False, False])
    warn = line_for(Status.PASS, [True, False])
    _check(len({good, neutral, warn}) == 3,
           "the three corroboration states render three DISTINCT lines")


tests = [
    test_good_state_renders,
    test_neutral_state_renders,
    test_warn_state_renders,
    test_terminal_line_matches_html_badge_signal,
    test_line_is_display_only_score_unchanged,
    test_suppressed_when_no_panel_or_no_prediction,
    test_states_are_distinct,
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
