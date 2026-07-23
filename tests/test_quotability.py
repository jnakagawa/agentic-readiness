"""Tests for the quotability gate (METHOD, Cycle 5).

Runnable directly, no pytest required:

    python tests/test_quotability.py

Quotability is the one-bit readout a reader needs before citing a headline
number: reproducible, or provisional. It is display-only — it NEVER changes the
score — and it classifies a Report by how the evidence behind the number held up.
Covered with synthetic Report / BehavioralRun fixtures (no network, no CLIs):
  - a static score (no panel) is deterministic -> CITABLE, never flagged;
  - a not-scorable report has no number to quote and prints no quotability line;
  - a single valid trial is PROVISIONAL (reproducibility unmeasured) — the
    honest state behind the observed same-day refuse<->warn flip;
  - a multi-trial panel that DISAGREES is PROVISIONAL (unstable), and carries the
    stability number through;
  - a multi-trial panel that AGREES is CITABLE (reproducible);
  - --behavioral with every run env-blocked -> behavioral-unobserved (the
    behavioral dimension, not the static floor, is judged);
  - the terminal card renders the verdict, and the overall score is byte-for-byte
    unchanged by the annotation.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import report as report_mod  # noqa: E402
from asrs.reliability import quotability  # noqa: E402
from asrs.types import BehavioralRun, Report  # noqa: E402

_KEYS = ["found_product", "understood_pricing", "found_purchase_path",
         "machine_payable_path", "no_human_gate"]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(model="claude", trial=1, **cp) -> BehavioralRun:
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(model=model, trial=trial, checkpoints=checkpoints)


def _env_blocked_run(model="codex", trial=1) -> BehavioralRun:
    return BehavioralRun(
        model=model, trial=trial,
        checkpoints={k: False for k in _KEYS},
        blockers=["navigation blocked by browser security policy"],
    )


def _report(overall=72.0, scored=True, runs=None) -> Report:
    return Report(
        domain="example.com",
        rubric_version="0.5",
        generated_at="2026-07-23T00:00:00",
        pillar_scores={"access": overall},
        overall_score=overall,
        grade="C" if scored else "N/A",
        scored=scored,
        behavioral_runs=list(runs or []),
    )


# ---------------------------------------------------------------------------
# 1. Static score (no panel) -> deterministic, citable, not flagged.
# ---------------------------------------------------------------------------
def test_static_is_citable() -> None:
    print("test_static_is_citable")
    q = quotability(_report(runs=[]))
    _check(q.quotable is True, "static score is quotable")
    _check(q.tag == "static-deterministic", f"tag static-deterministic, got {q.tag!r}")
    _check(q.verdict_stability is None, "no panel -> no stability number")


# ---------------------------------------------------------------------------
# 2. Not scorable -> no number to quote; render prints no quotability line.
# ---------------------------------------------------------------------------
def test_not_scorable() -> None:
    print("test_not_scorable")
    rep = _report(overall=None, scored=False)
    rep.overall_score = None
    q = quotability(rep)
    _check(q.quotable is False, "not-scorable is not quotable")
    _check(q.tag == "not-scorable", f"tag not-scorable, got {q.tag!r}")
    text = report_mod.render(rep)
    _check("QUOTABILITY" not in text,
           "not-scorable card suppresses the quotability line (no double no-number)")


# ---------------------------------------------------------------------------
# 3. Single valid trial -> provisional (reproducibility unmeasured).
# ---------------------------------------------------------------------------
def test_single_trial_is_provisional() -> None:
    print("test_single_trial_is_provisional")
    q = quotability(_report(runs=[_run(found_product=True)]))
    _check(q.quotable is False, "single trial is not quotable")
    _check(q.tag == "provisional-single-trial", f"tag, got {q.tag!r}")
    _check("--trials>=2" in q.reason, "reason points at the trials>=2 fix")


# ---------------------------------------------------------------------------
# 4. Multi-trial panel that DISAGREES -> provisional-unstable, carries stability.
# ---------------------------------------------------------------------------
def test_unstable_panel_is_provisional() -> None:
    print("test_unstable_panel_is_provisional")
    # Two runs disagree on every checkpoint -> verdict_stability 0.0 (< 0.8).
    r1 = _run(trial=1, **dict.fromkeys(_KEYS, True))
    r2 = _run(model="codex", **dict.fromkeys(_KEYS, False))
    q = quotability(_report(runs=[r1, r2]))
    _check(q.quotable is False, "unstable panel is not quotable")
    _check(q.tag == "provisional-unstable", f"tag provisional-unstable, got {q.tag!r}")
    _check(q.verdict_stability == 0.0, f"stability 0.0 carried, got {q.verdict_stability}")


# ---------------------------------------------------------------------------
# 5. Multi-trial panel that AGREES -> reproducible, citable.
# ---------------------------------------------------------------------------
def test_reproducible_panel_is_citable() -> None:
    print("test_reproducible_panel_is_citable")
    allpass = dict.fromkeys(_KEYS, True)
    q = quotability(_report(runs=[_run(trial=1, **allpass), _run(model="codex", **allpass)]))
    _check(q.quotable is True, "reproducible panel is quotable")
    _check(q.tag == "reproducible", f"tag reproducible, got {q.tag!r}")
    _check(q.verdict_stability == 1.0, f"stability 1.0 carried, got {q.verdict_stability}")


# ---------------------------------------------------------------------------
# 6. --behavioral but every run env-blocked -> behavioral dimension unobserved.
# ---------------------------------------------------------------------------
def test_all_env_blocked_is_behavioral_unobserved() -> None:
    print("test_all_env_blocked_is_behavioral_unobserved")
    q = quotability(_report(runs=[_env_blocked_run(trial=1), _env_blocked_run(trial=2)]))
    _check(q.quotable is False, "no valid behavioral run -> not quotable")
    _check(q.tag == "behavioral-unobserved", f"tag behavioral-unobserved, got {q.tag!r}")
    # Attribution honesty: it names the behavioral dimension, not the static floor.
    _check("static floor" in q.reason or "not observed" in q.reason,
           "reason scopes the verdict to the behavioral dimension")


# ---------------------------------------------------------------------------
# 7. The terminal card renders the verdict; the score is untouched by it.
# ---------------------------------------------------------------------------
def test_render_shows_verdict_and_score_unchanged() -> None:
    print("test_render_shows_verdict_and_score_unchanged")
    # Static report: CITABLE line present, overall number still printed verbatim.
    static_text = report_mod.render(_report(overall=72.0, runs=[]))
    _check("QUOTABILITY: CITABLE (static-deterministic)" in static_text,
           "static card shows the CITABLE/static-deterministic verdict")
    _check("OVERALL 72.0/100" in static_text, "overall score unchanged by the annotation")

    # Single-trial behavioral report: PROVISIONAL line present.
    beh_text = report_mod.render(_report(overall=64.0, runs=[_run(found_product=True)]))
    _check("QUOTABILITY: PROVISIONAL (provisional-single-trial)" in beh_text,
           "single-trial card shows the PROVISIONAL verdict")
    _check("OVERALL 64.0/100" in beh_text, "behavioral overall score unchanged too")


# ---------------------------------------------------------------------------
# 8. CLI default: --trials is now >=2 so a bare --behavioral run is checked.
# ---------------------------------------------------------------------------
def test_cli_trials_default_is_two() -> None:
    print("test_cli_trials_default_is_two")
    from asrs.cli import build_parser

    args = build_parser().parse_args(["score", "example.com", "--behavioral"])
    _check(args.trials == 2, f"default --trials is 2 (multi-trial by default), got {args.trials}")


def main() -> int:
    tests = [
        test_static_is_citable,
        test_not_scorable,
        test_single_trial_is_provisional,
        test_unstable_panel_is_provisional,
        test_reproducible_panel_is_citable,
        test_all_env_blocked_is_behavioral_unobserved,
        test_render_shows_verdict_and_score_unchanged,
        test_cli_trials_default_is_two,
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
