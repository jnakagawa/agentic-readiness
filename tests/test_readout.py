"""Tests for surfacing panel reliability in the JSON Report + HTML scorecard.

Runnable directly, no pytest required:

    python tests/test_readout.py

Cycle 4 (READOUT) attached the within-panel reproducibility metric — computed
only inside the terminal renderer before — to the ``Report`` as an ADDITIVE
field and to the HTML scorecard. These tests pin that surfacing (no network, no
CLIs, no scoring-semantics assertions — the metric math itself lives in
``test_reliability.py``):
  - a behavioral Report round-trips ``panel_reliability`` through to_json/JSON,
    carrying the same numbers the pure metric produces;
  - a static report (no runs) carries ``panel_reliability = None`` — no invented
    reproducibility for a panel that never ran;
  - the HTML card renders the stability number + flipped checkpoints for a real
    panel, the honest "single trial" note for one draw, and NOTHING when the
    field is absent (so static scorecards are unchanged).

Cycle 8 (READOUT) attached the companion ``quotability`` verdict the same way —
the one-bit "is the headline number safe to cite?" the terminal card already
computed, now on the JSON ``Report`` and the HTML scorecard (the classifier math
lives in ``test_quotability.py``):
  - a Report round-trips ``quotability`` through JSON, byte-for-byte the pure
    ``quotability()`` output (one source of truth), for static and panel modes;
  - the HTML card renders a Citable pill for a static/reproducible report and a
    Provisional pill for a single-trial one, showing the reason;
  - a not-scorable verdict and an absent field both render NOTHING (the grade
    already carries N/A — same suppression as the terminal line).
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import scorecard  # noqa: E402
from asrs.reliability import panel_reliability, quotability  # noqa: E402
from asrs.types import BehavioralRun, Report  # noqa: E402

_KEYS = ["found_product", "understood_pricing", "found_purchase_path",
         "machine_payable_path", "no_human_gate"]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(model="claude", trial=1, trust_events=None, **cp) -> BehavioralRun:
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(
        model=model, trial=trial, checkpoints=checkpoints,
        trust_events=list(trust_events or []),
    )


def _report(runs) -> Report:
    """Assemble a Report the way cli._evaluate does: score-agnostic here — we
    only exercise the additive attach + serialization, not the rubric."""
    rep = Report(domain="example.test", rubric_version="0.5", generated_at="2026-07-23T00:00:00",
                 behavioral_runs=runs, overall_score=50.0, grade="F")
    if runs:
        rep.panel_reliability = panel_reliability(runs).to_dict()
    # cli._evaluate attaches quotability for every mode -> mirror it here so the
    # fixture stays faithful to the pipeline.
    rep.quotability = quotability(rep).to_dict()
    return rep


# ---------------------------------------------------------------------------
# 1. A behavioral Report round-trips panel_reliability through JSON.
# ---------------------------------------------------------------------------
def test_json_carries_reliability() -> None:
    print("test_json_carries_reliability")
    # 2 runs agree on all but machine_payable_path -> stability 0.8, one flip.
    r1 = _run(trial=1, found_product=True, machine_payable_path=True)
    r2 = _run(model="codex", found_product=True, machine_payable_path=False)
    rep = _report([r1, r2])

    loaded = json.loads(rep.to_json())
    _check("panel_reliability" in loaded, "panel_reliability key present in JSON")
    rel = loaded["panel_reliability"]
    _check(rel is not None, "reliability not None for a behavioral report")
    _check(abs(rel["verdict_stability"] - 0.8) < 1e-9,
           f"stability 0.8 survives serialization, got {rel['verdict_stability']}")
    _check(rel["flipped_checkpoints"] == ["machine_payable_path"],
           f"flipped list survives, got {rel['flipped_checkpoints']}")
    _check(rel["label"] == "stable", f"label survives, got {rel['label']!r}")
    # The stored dict must equal the pure metric — one source of truth.
    _check(rel == panel_reliability([r1, r2]).to_dict(),
           "stored dict is byte-for-byte the pure metric output")


# ---------------------------------------------------------------------------
# 2. A static report (no runs) carries None — no invented reproducibility.
# ---------------------------------------------------------------------------
def test_static_report_has_none() -> None:
    print("test_static_report_has_none")
    rep = _report([])
    loaded = json.loads(rep.to_json())
    _check(loaded["panel_reliability"] is None,
           "static report reliability is None (no panel ran)")


# ---------------------------------------------------------------------------
# 3. HTML card renders stability + flipped checkpoints for a real panel.
# ---------------------------------------------------------------------------
def test_html_renders_panel() -> None:
    print("test_html_renders_panel")
    r1 = _run(trial=1, found_product=True, machine_payable_path=True)
    r2 = _run(model="codex", found_product=True, machine_payable_path=False)
    rep = _report([r1, r2])
    html = scorecard._reliability(json.loads(rep.to_json()))
    _check("Panel reliability" in html, "card title present")
    _check("0.80" in html, "stability number rendered")
    _check("Stable" in html, "band label rendered")
    # Flipped checkpoint shown by its human label, not the raw key.
    _check("Machine-payable" in html, "flipped checkpoint shown by human label")
    _check("machine_payable_path" not in html, "raw key not leaked into the card")


# ---------------------------------------------------------------------------
# 4. Single-trial report -> the honest "not assessed" note, no fake number.
# ---------------------------------------------------------------------------
def test_html_single_trial_note() -> None:
    print("test_html_single_trial_note")
    rep = _report([_run(found_product=True)])
    html = scorecard._reliability(json.loads(rep.to_json()))
    _check("Panel reliability" in html, "card still shown for a single trial")
    _check("Single trial" in html, "single-trial band label present")
    _check("not assessed" in html, "explains reproducibility was not assessed")


# ---------------------------------------------------------------------------
# 5. Absent field -> no card at all (static scorecards unchanged).
# ---------------------------------------------------------------------------
def test_html_absent_renders_nothing() -> None:
    print("test_html_absent_renders_nothing")
    _check(scorecard._reliability({"domain": "x"}) == "",
           "no panel_reliability key -> empty string (no card)")
    _check(scorecard._reliability({"panel_reliability": None}) == "",
           "explicit None -> empty string (no card)")


# ---------------------------------------------------------------------------
# 6. quotability round-trips through JSON, byte-for-byte the pure metric.
# ---------------------------------------------------------------------------
def test_json_carries_quotability() -> None:
    print("test_json_carries_quotability")
    # Static (no runs) -> deterministic / citable.
    static = _report([])
    loaded = json.loads(static.to_json())
    _check("quotability" in loaded, "quotability key present in JSON")
    q = loaded["quotability"]
    _check(q is not None, "quotability populated for a static report")
    _check(q["tag"] == "static-deterministic", f"static tag, got {q['tag']!r}")
    _check(q["quotable"] is True, "static score is citable")
    _check(q == quotability(static).to_dict(),
           "stored dict is byte-for-byte the pure quotability() output")

    # A stable 2-run panel -> reproducible / citable, stability carried through.
    allpass = dict.fromkeys(_KEYS, True)
    rep = _report([_run(trial=1, **allpass), _run(model="codex", **allpass)])
    q2 = json.loads(rep.to_json())["quotability"]
    _check(q2["tag"] == "reproducible", f"reproducible tag, got {q2['tag']!r}")
    _check(q2["verdict_stability"] == 1.0, f"stability carried, got {q2['verdict_stability']}")


# ---------------------------------------------------------------------------
# 7. HTML card renders a Citable / Provisional pill with its reason.
# ---------------------------------------------------------------------------
def test_html_renders_quotability_pill() -> None:
    print("test_html_renders_quotability_pill")
    # Static report -> Citable pill.
    static_html = scorecard._quotability(json.loads(_report([]).to_json()))
    _check("Quotability" in static_html, "card title present")
    _check("Citable" in static_html, "Citable pill rendered for a static report")
    _check("pill good" in static_html, "citable uses the good band")
    _check("Provisional" not in static_html, "static is not flagged provisional")

    # Single-trial panel -> Provisional pill.
    prov_html = scorecard._quotability(json.loads(_report([_run(found_product=True)]).to_json()))
    _check("Provisional" in prov_html, "Provisional pill rendered for a single trial")
    _check("pill warn" in prov_html, "single-trial provisional uses the warn band")
    _check("--trials" in prov_html, "reason (re-run with more trials) is shown")


# ---------------------------------------------------------------------------
# 8. not-scorable + absent field -> no card (grade already carries N/A).
# ---------------------------------------------------------------------------
def test_html_quotability_suppressed() -> None:
    print("test_html_quotability_suppressed")
    _check(scorecard._quotability({"domain": "x"}) == "",
           "absent quotability key -> empty string (no card)")
    _check(scorecard._quotability({"quotability": None}) == "",
           "explicit None -> empty string (no card)")
    _check(scorecard._quotability({"quotability": {"tag": "not-scorable", "quotable": False}}) == "",
           "not-scorable tag -> no card (grade already says N/A)")


def main() -> int:
    tests = [
        test_json_carries_reliability,
        test_static_report_has_none,
        test_html_renders_panel,
        test_html_single_trial_note,
        test_html_absent_renders_nothing,
        test_json_carries_quotability,
        test_html_renders_quotability_pill,
        test_html_quotability_suppressed,
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
