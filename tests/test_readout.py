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


# ---------------------------------------------------------------------------
# Task battery card (Cycle 12, READOUT): the battery_summary that already ships
# terminal + JSON now renders on the HTML scorecard too.
# ---------------------------------------------------------------------------
def _battery_summary(multi_kind: bool = True):
    """A faithful battery_summary built through asrs.battery.aggregate_battery
    on synthetic runs — not a hand-typed dict — so the rendering test tracks the
    real aggregation shape (per_task, per_kind, cross_task_spread)."""
    from asrs import battery as bt

    tasks = [bt.BatteryTask(id="buy_image", kind="digital_service", intent="buy one image")]
    runs_by_task = {
        "buy_image": [_run(found_product=True, understood_pricing=True),
                      _run(found_product=True, understood_pricing=True, trial=2)],
    }
    if multi_kind:
        tasks.append(bt.BatteryTask(id="order_widget", kind="physical_good", intent="order the widget"))
        runs_by_task["order_widget"] = [_run(found_product=True), _run(trial=2)]
    b = bt.Battery(id="t", description="", tasks=tasks)
    return bt.aggregate_battery(b, runs_by_task).to_dict()


def test_json_carries_battery() -> None:
    print("test_json_carries_battery")
    summary = _battery_summary()
    rep = _report([_run(found_product=True)])
    rep.battery_summary = summary
    loaded = json.loads(rep.to_json())
    _check("battery_summary" in loaded, "battery_summary key present in JSON")
    _check(loaded["battery_summary"] == summary, "battery_summary round-trips through JSON unchanged")


def test_html_renders_battery() -> None:
    print("test_html_renders_battery")
    summary = _battery_summary(multi_kind=True)
    html = scorecard._battery({"battery_summary": summary})
    _check("Task battery" in html, "battery card header renders")
    _check("buy_image" in html and "order_widget" in html, "each intent row renders")
    _check("By archetype" in html, "multi-kind battery renders the per-archetype rollup")
    _check("digital_service" in html and "physical_good" in html, "each archetype renders")
    spread = summary["cross_task_spread"]
    _check(f"{spread:.2f}" in html, "cross-task spread value renders in the pill/footer")


def test_html_battery_single_kind_no_rollup() -> None:
    print("test_html_battery_single_kind_no_rollup")
    summary = _battery_summary(multi_kind=False)
    html = scorecard._battery({"battery_summary": summary})
    _check("Task battery" in html, "single-kind battery still renders the card")
    _check("By archetype" not in html, "single kind -> no per-archetype rollup (mirrors terminal)")
    # A single kind has an unobservable between-type spread (None) -> no pill,
    # matching the aggregation's honest None (attribution honesty).
    _check(summary["between_kind_spread"] is None,
           "single-kind fixture has no between-archetype spread (unobservable)")
    _check("Between-archetype spread" not in html,
           "single kind -> no between-archetype pill/desc (nothing to specialize between)")


def test_html_battery_between_kind_pill() -> None:
    print("test_html_battery_between_kind_pill")
    # Cycle 20 (READOUT): the storefront-TYPE specialization signal
    # (between_kind_spread) that already ships terminal + JSON (Cycle 18) now
    # renders as an HTML pill + interpretation line, only when >=2 archetypes had
    # signal. Assert the value and the band label are driven off the aggregation,
    # not hand-typed, so the pill can't drift from the number.
    summary = _battery_summary(multi_kind=True)
    bks = summary["between_kind_spread"]
    _check(isinstance(bks, (int, float)),
           "multi-kind fixture produces an observable between-archetype spread")
    html = scorecard._battery({"battery_summary": summary})
    _check(f"{bks:.2f}" in html, "between-archetype spread value renders")
    _check("Between-archetype spread" in html, "between-archetype interpretation line renders")
    _cls, label = scorecard._battery_between_band(bks)
    _check(label in html, f"between-archetype pill carries the {label!r} band label")
    # The band thresholds/labels must match the terminal readout exactly.
    _check(scorecard._battery_between_band(0.10) == ("good", "Generalist"),
           "low between-spread -> Generalist (mirrors terminal <0.15)")
    _check(scorecard._battery_between_band(0.25) == ("warn", "Somewhat type-dependent"),
           "mid between-spread -> Somewhat type-dependent (mirrors terminal <0.35)")
    _check(scorecard._battery_between_band(0.50) == ("bad", "Type-specialized"),
           "high between-spread -> Type-specialized (mirrors terminal >=0.35)")


def test_html_battery_absent_renders_nothing() -> None:
    print("test_html_battery_absent_renders_nothing")
    _check(scorecard._battery({"domain": "x"}) == "",
           "absent battery_summary key -> empty string (no card)")
    _check(scorecard._battery({"battery_summary": None}) == "",
           "explicit None -> empty string (no card)")


# Offering-relative comparability on the HTML card (operator directive brick 5,
# READOUT): the terminal readout already names WHICH archetypes were assessed and
# which the site does not offer (brick 3, na_archetypes / assessed_archetypes);
# the HTML battery card now mirrors it. Built through the REAL aggregation WITH an
# OfferingProfile so the NA/assessed lists are populated the production way.
def _offering_battery_summary():
    from asrs import battery as bt
    from asrs import offering as off

    tasks = [
        bt.BatteryTask(id="digital_good", kind="digital_good",
                       intent="obtain one generated image"),
        bt.BatteryTask(id="physical_good", kind="physical_good",
                       intent="order the widget"),
    ]
    runs_by_task = {
        "digital_good": [_run(found_product=True, understood_pricing=True),
                         _run(found_product=True, understood_pricing=True, trial=2)],
        "physical_good": [_run(found_product=True), _run(trial=2)],
    }
    b = bt.Battery(id="t", description="", tasks=tasks)
    # Site claims digital_good only -> physical_good and the rest of the template
    # bank are NA. The claim is built through the real dataclass so `unclaimed`
    # derives from offering.ARCHETYPES, never a hand-typed complement.
    profile = off.OfferingProfile(
        domain="example.test",
        claimed=[off.ArchetypeClaim(
            archetype="digital_good",
            signals=[off.ArchetypeSignal(
                archetype="digital_good", surface="homepage",
                label="generated-media", quote="every generated image")],
        )],
    )
    return bt.aggregate_battery(b, runs_by_task, profile=profile).to_dict()


def test_html_battery_offering_relative_names_na() -> None:
    print("test_html_battery_offering_relative_names_na")
    summary = _offering_battery_summary()
    na = summary["na_archetypes"]
    assessed = summary["assessed_archetypes"]
    _check(bool(na), "offering-relative fixture marks unclaimed archetypes NA")
    _check("physical_good" in na, "physical_good is NA (site claims digital only)")
    _check(assessed == ["digital_good"], "only the claimed archetype is assessed")
    html = scorecard._battery({"battery_summary": summary})
    _check("Assessed over" in html, "HTML names which archetypes were assessed")
    _check("Not offered" in html, "HTML names the not-offered archetypes (brick 5)")
    # Every NA archetype from the summary renders — driven off the aggregation, not
    # hand-typed, so the readout can't drift from the numbers. The archetypes with
    # no task (metered_api, subscription, service_booking, data_retrieval) appear
    # ONLY via this block, so their presence is a non-trivial assertion.
    for a in na:
        _check(a in html, f"not-offered archetype {a!r} renders")
    _check("chip na" in html, "not-offered archetypes use the dimmed NA chip class")


def test_html_battery_no_offering_no_na_block() -> None:
    print("test_html_battery_no_offering_no_na_block")
    # Without an offering profile the aggregation is pre-brick-3: na_archetypes is
    # empty, so the offering-relative naming block does NOT render — mirroring the
    # terminal readout, which prints neither line for a hand-authored battery.
    summary = _battery_summary(multi_kind=True)
    _check(summary["na_archetypes"] == [], "no-profile fixture has no NA archetypes")
    html = scorecard._battery({"battery_summary": summary})
    _check("Not offered" not in html, "no profile -> no not-offered block")
    _check("Offering-relative" not in html, "no profile -> no offering-relative header")


# ---------------------------------------------------------------------------
# Cycle 16 (READOUT): the methodology page — the "read the paper" doc behind the
# rubric page. Display-only; these tests pin that it renders the measurement
# semantics a critic needs and stays in sync with the LIVE rubric (weights /
# caps / grade bands / version pulled from load_rubric, never hardcoded), and
# that build_scorecard publishes it next to every card and links to it. No
# scoring-semantics assertions — this page has none.
# ---------------------------------------------------------------------------
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

from asrs.scoring import load_rubric  # noqa: E402


def test_methodology_page_written_and_covers_semantics() -> None:
    print("test_methodology_page_written_and_covers_semantics")
    with tempfile.TemporaryDirectory() as d:
        path = scorecard._write_methodology_page(Path(d))
        _check(Path(path).name == "methodology.html", "writes methodology.html")
        text = Path(path).read_text()
    # The distinctions that make ASRS credible must be documented by name.
    for phrase in ("FAIL", "CANT_TEST", "NOT SCORABLE", "agent-side",
                   "site-side", "$0", "comparable only", "capability"):
        _check(phrase in text, f"methodology documents {phrase!r}")


def test_methodology_documents_earned_dominance() -> None:
    # Cycle 24 (READOUT): the worked example that surfaces the earned-dominance /
    # observability property (made an executable guard in Cycle 23) in prose a
    # critic can read. It must name the three facts that make a delta trustworthy
    # and stay vendor-neutral (no domain/product/brand named on the page).
    print("test_methodology_documents_earned_dominance")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    for phrase in ("worked example", "Full observability",
                   "Like-for-like denominator", "no inversion",
                   "superset", "earned", "blind spot"):
        _check(phrase in text, f"methodology documents earned-dominance: {phrase!r}")
    # Vendor-neutral: the reference pair is described by capability, never named.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"methodology names no vendor/domain ({banned!r})")


def test_methodology_page_tracks_live_rubric() -> None:
    print("test_methodology_page_tracks_live_rubric")
    rubric = load_rubric()
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    _check(f"v{rubric['version']}" in text, "shows the live rubric version")
    # Weights are rendered as percentages straight from the rubric.
    tw = rubric["pillar_weights"]["transactability"]
    _check(f"{tw:.0%}" in text, "renders the live transactability weight")
    # Every cap slug from the rubric appears (pulled live, not hardcoded).
    for slug in rubric["caps"]:
        _check(slug in text, f"lists cap {slug!r} from the live rubric")


def test_build_scorecard_publishes_and_links_methodology() -> None:
    print("test_build_scorecard_publishes_and_links_methodology")
    rep = _report([])  # static report, no panel — the common hosted case
    with tempfile.TemporaryDirectory() as d:
        rp = Path(d) / "rep.json"
        rp.write_text(rep.to_json())
        out = scorecard.build_scorecard([str(rp)], out_path=str(Path(d) / "card.html"))
        _check((Path(d) / "methodology.html").exists(),
               "methodology.html published next to the card")
        _check((Path(d) / "rubric.html").exists(),
               "rubric.html still published (unchanged behaviour)")
        _check('href="methodology.html"' in Path(out).read_text(),
               "the card footer links to methodology.html")


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
        test_json_carries_battery,
        test_html_renders_battery,
        test_html_battery_single_kind_no_rollup,
        test_html_battery_between_kind_pill,
        test_html_battery_absent_renders_nothing,
        test_html_battery_offering_relative_names_na,
        test_html_battery_no_offering_no_na_block,
        test_methodology_page_written_and_covers_semantics,
        test_methodology_documents_earned_dominance,
        test_methodology_page_tracks_live_rubric,
        test_build_scorecard_publishes_and_links_methodology,
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
