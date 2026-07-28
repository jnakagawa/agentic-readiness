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


def test_methodology_documents_weight_robustness() -> None:
    # Cycle 56 (READOUT): the READOUT complement to Cycle 55's weight-robustness
    # guard (guard 15, test_canonical_replay) — the same move Cycle 24 made for
    # Cycle 23's earned-dominance guard. The worked example must name, in prose a
    # critic can read, the SECOND credibility objection (the delta's sign is
    # invariant to the pillar weighting because the higher side is pillar-wise
    # dominant over an identical, uncapped applicable-pillar set), stay
    # vendor-neutral, and say it is test-pinned.
    print("test_methodology_documents_weight_robustness")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    for phrase in ("re-weight the pillars", "pillar-wise dominant",
                   "same applicable-pillar set", "non-negative weights",
                   "every reasonable weighting", "cannot flip"):
        _check(phrase in text, f"methodology documents weight-robustness: {phrase!r}")
    # It must claim the property is enforced, not merely asserted (mirrors the
    # earned-dominance paragraph's "executable regression test" language).
    _check("executable regression test" in text,
           "weight-robustness is stated as test-pinned")
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


# Cycle 32 (READOUT): a "Grade capped" chip on a card links to the cap's row in
# the methodology page, so a reader who sees a capped grade can jump straight to
# why that finding caps. The methodology row's id and the card link's fragment
# both come from the ONE helper `_cap_anchor` — these tests pin that they render,
# that they can't drift, and that a no-cap card still emits nothing.


def test_cap_anchor_helper_is_stable_and_sanitizing() -> None:
    print("test_cap_anchor_helper_is_stable_and_sanitizing")
    # Clean slugs pass through as cap-<slug>.
    _check(scorecard._cap_anchor("no-https") == "cap-no-https", "clean slug -> cap-no-https")
    # A future odd slug still yields a valid, matching fragment on both sides.
    _check(scorecard._cap_anchor("Weird Slug!!") == "cap-weird-slug",
           "odd slug lowercased + non-alnum runs collapsed to '-'")
    _check(scorecard._cap_anchor("a__b") == "cap-a-b", "underscore run collapses")


def test_methodology_cap_rows_carry_anchor_ids() -> None:
    print("test_methodology_cap_rows_carry_anchor_ids")
    rubric = load_rubric()
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Every live cap slug has an addressable row id, so a link can target it.
    for slug in rubric["caps"]:
        anchor = scorecard._cap_anchor(slug)
        _check(f'id="{anchor}"' in text, f"methodology cap row carries id={anchor!r}")


def test_caps_alert_chip_links_to_methodology() -> None:
    print("test_caps_alert_chip_links_to_methodology")
    # No cap applied -> no alert, no link (byte-for-byte the pre-change no-op).
    _check(scorecard._caps_alerts({"caps_applied": []}) == "", "no cap -> empty")
    slug = "no-https"
    html_out = scorecard._caps_alerts({"caps_applied": [slug]})
    anchor = scorecard._cap_anchor(slug)
    _check(f'href="methodology.html#{anchor}"' in html_out,
           "capped chip links to the methodology cap anchor")
    _check('<a class="chip"' in html_out, "the cap chip is rendered as a link")
    _check("Grade capped" in html_out, "the alert still reads 'Grade capped'")


def test_cap_link_and_methodology_anchor_cannot_drift() -> None:
    # The load-bearing assertion: for every cap the rubric can apply, the
    # fragment the CARD links to must resolve to an id actually PRESENT in the
    # methodology page. Ties the two rendered surfaces, not just the helper.
    print("test_cap_link_and_methodology_anchor_cannot_drift")
    rubric = load_rubric()
    with tempfile.TemporaryDirectory() as d:
        methodology = Path(scorecard._write_methodology_page(Path(d))).read_text()
    for slug in rubric["caps"]:
        alert = scorecard._caps_alerts({"caps_applied": [slug]})
        frag = f"methodology.html#{scorecard._cap_anchor(slug)}"
        _check(frag in alert, f"card links {frag!r} for cap {slug!r}")
        target_id = frag.split("#", 1)[1]
        _check(f'id="{target_id}"' in methodology,
               f"the linked fragment {target_id!r} resolves to a methodology row")


# ---------------------------------------------------------------------------
# Cycle 40 (READOUT): the live canonical-delta HISTORY as an HTML surface.
# `asrs canonical-history` computes the whole diagnosis — delta trend, divergence
# band, sustained-drift run, PILLAR attribution (which pillar moved) and a
# SIDE/direction cause (no-rails gaining vs with-rails softening) — but that was
# terminal-only. `_write_canonical_history_page` renders it so a reader eyeballs the
# curve, the named mover, and which side drove it. Display-only: no scoring path.
# ---------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone  # noqa: E402

from asrs import canonical_history as ch  # noqa: E402


def _hist_point(ts, no_o, no_g, with_o, with_g, no_pil, with_pil) -> ch.CanonicalPoint:
    return ch.CanonicalPoint(
        ts=ts,
        no_rails_overall=no_o,
        no_rails_grade=no_g,
        with_rails_overall=with_o,
        with_rails_grade=with_g,
        delta=round(with_o - no_o, 4),
        no_rails_pillars=no_pil,
        with_rails_pillars=with_pil,
    )


def _drifting_history() -> ch.CanonicalHistory:
    """A synthetic series: an in-band anchor at the pinned +39.4, then 3 out-of-band
    readings where the WITH-RAILS side's legibility softened (delta narrows to
    +32.6) — the real-world scenario the committed series is in, made deterministic.
    """
    no_pil = {"access": 100.0, "legibility": 36.4, "transactability": 18.75,
              "trust": 60.0}
    anchor_with = {"access": 100.0, "legibility": 90.9, "transactability": 87.5,
                   "trust": 60.0}
    drift_with = {"access": 100.0, "legibility": 63.6, "transactability": 87.5,
                  "trust": 60.0}
    pts = [
        _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", no_pil, anchor_with),
        _hist_point("20260727T060000Z", 46.1, "F", 78.7, "C", no_pil, drift_with),
        _hist_point("20260727T070000Z", 46.1, "F", 78.7, "C", no_pil, drift_with),
        _hist_point("20260727T080000Z", 46.1, "F", 78.7, "C", no_pil, drift_with),
    ]
    return ch.summarize(pts)


def test_canonical_history_page_written_and_links() -> None:
    print("test_canonical_history_page_written_and_links")
    rep = _report([])  # static report — the common hosted case
    with tempfile.TemporaryDirectory() as d:
        rp = Path(d) / "rep.json"
        rp.write_text(rep.to_json())
        out = scorecard.build_scorecard([str(rp)], out_path=str(Path(d) / "card.html"))
        _check((Path(d) / "canonical-history.html").exists(),
               "canonical-history.html published next to the card")
        # Unchanged behaviour: the two prior prose pages still ship.
        _check((Path(d) / "methodology.html").exists(), "methodology.html still published")
        _check((Path(d) / "rubric.html").exists(), "rubric.html still published")
        _check('href="canonical-history.html"' in Path(out).read_text(),
               "the card footer links to canonical-history.html")


def test_canonical_history_page_renders_drift_diagnosis() -> None:
    # The page must surface the SAME diagnosis the terminal computes: band verdict,
    # divergence value, the pillar mover, and the side/direction cause.
    print("test_canonical_history_page_renders_drift_diagnosis")
    hist = _drifting_history()
    with tempfile.TemporaryDirectory() as d:
        path = scorecard._write_canonical_history_page(Path(d), history=hist)
        _check(Path(path).name == "canonical-history.html", "writes canonical-history.html")
        text = Path(path).read_text()
    _check("Drifting" in text, "names the DRIFTING band")
    _check("-6.8" in text, "shows the divergence value (-6.8)")
    _check("Sustained" in text, "flags the sustained (3-in-a-row) out-of-band run")
    # Pillar attribution: the with-rails legibility move is named as the top mover.
    _check("legibility" in text and "90.9" in text and "63.6" in text,
           "names the with-rails legibility pillar move (90.9 -> 63.6)")
    # Side/direction cause: the with-rails reference softened (not the floor rising).
    _check("SOFTENED" in text, "names the with-rails-softened cause")
    _check("<svg" in text and text.count("<circle") == 4,
           "renders the 4-point trend chart")


def test_canonical_history_in_band_shows_no_drift() -> None:
    # Non-vacuous: an in-band series (live delta reproduces the pinned +39.4) shows
    # the IN-BAND verdict and NO drift/attribution/cause markup — the drift prose in
    # the test above is earned by the data, not baked into the template.
    print("test_canonical_history_in_band_shows_no_drift")
    no_pil = {"access": 100.0, "legibility": 36.4}
    with_pil = {"access": 100.0, "legibility": 90.9}
    pts = [
        _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
        _hist_point("20260727T060000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
    ]
    hist = ch.summarize(pts)
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("In-band" in text, "names the IN-BAND band on an in-band series")
    # The band legend always lists all three band names, so assert on the drift
    # PROSE (the sustained-run line + the attribution/cause card), not the labels.
    _check("consecutive re-score(s) out of band" not in text,
           "no sustained/recent out-of-band line when in-band")
    _check("What moved, and which side" not in text,
           "no attribution/cause card when there is nothing to explain")


def test_canonical_history_trend_svg_colors_by_band() -> None:
    # The chart is a single series, so identity needs no legend; but each point is
    # colored by its divergence BAND (a reserved status encoding). Pin that an
    # in-band point is green and a diverged point is red, and that the baseline
    # reference line + latest direct-label render — non-vacuous status coloring.
    print("test_canonical_history_trend_svg_colors_by_band")
    p_in = _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", {}, {})   # +39.4 in-band
    p_div = _hist_point("20260727T060000Z", 46.1, "F", 60.0, "F", {}, {})  # +13.9 diverged
    svg = scorecard._history_trend_svg([p_in, p_div], ch.FIXTURE_BASELINE_DELTA)
    _check(scorecard._HISTORY_BAND_COLOR["in-band"] in svg, "in-band point drawn green")
    _check(scorecard._HISTORY_BAND_COLOR["diverged"] in svg, "diverged point drawn red")
    _check("stroke-dasharray" in svg, "the pinned-fixture baseline is a dashed line")
    _check(">+13.9<" in svg, "the latest point is direct-labeled with its delta")


def test_canonical_history_empty_series_renders_gracefully() -> None:
    print("test_canonical_history_empty_series_renders_gracefully")
    hist = ch.summarize([])
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("No readings yet" in text, "empty series renders the no-data card")
    _check("<svg" not in text, "no chart drawn with no data")
    _check(text.rstrip().endswith("</html>"), "still a well-formed page")


def test_canonical_history_names_reference_pair_as_data() -> None:
    # This page is ABOUT the reference pair, so it names both hosts as DATA — the
    # SAME engineering-history category as rubric.html, deliberately OUT OF SCOPE for
    # the vendor-neutral-wording scanner (which guards capability-worded CHECK prose
    # on methodology + card). Pinning it here documents that the naming is intended.
    print("test_canonical_history_names_reference_pair_as_data")
    hist = _drifting_history()
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check(ch.CANONICAL_NO_RAILS in text and ch.CANONICAL_WITH_RAILS in text,
           "the page names both reference-pair hosts as data")


def test_canonical_history_page_renders_recapture_defer() -> None:
    # Cycle 43 computed the re-capture DECISION on the terminal readout; the HTML page
    # must surface it too. On the drifting series (with-rails reference SOFTENED, 3
    # in a row) the honest recommendation is DEFER — a real-world site change, not the
    # gap closing, so the pinned fixture still represents the true gap; do NOT chase it.
    print("test_canonical_history_page_renders_recapture_defer")
    hist = _drifting_history()
    _check(hist.recapture is not None and hist.recapture.code == ch.REC_DEFER,
           "the drifting series's recommendation is DEFER (sanity on the fixture)")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Re-capture decision" in text, "the page renders the re-capture decision card")
    _check(ch._REC_LABEL[ch.REC_DEFER] in text, "names the DEFER recommendation label")
    _check("DEFER re-capture until the reference recovers" in text,
           "surfaces the decision reason (defer until the reference recovers)")
    # The chip is coloured by the code, and the [LOCAL] framing (a decision, not an
    # action) is stated — re-capture is never performed by this page.
    _check(scorecard._HISTORY_REC_COLOR[ch.REC_DEFER] in text,
           "the recommendation chip is coloured by its code")
    _check("[LOCAL]" in text, "names re-capture as a [LOCAL], comparability-affecting step")


def test_canonical_history_recapture_is_data_driven() -> None:
    # Non-vacuous: an in-band series (live delta reproduces the pinned +39.4) renders
    # the BASELINE-VALID recommendation, NOT the DEFER prose — proving the decision
    # card is earned by the data, not baked into the template.
    print("test_canonical_history_recapture_is_data_driven")
    no_pil = {"access": 100.0, "legibility": 36.4}
    with_pil = {"access": 100.0, "legibility": 90.9}
    pts = [
        _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
        _hist_point("20260727T060000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
    ]
    hist = ch.summarize(pts)
    _check(hist.recapture is not None and hist.recapture.code == ch.REC_VALID,
           "an in-band series recommends BASELINE-VALID (sanity)")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Re-capture decision" in text, "the decision card renders on the in-band series too")
    _check(ch._REC_LABEL[ch.REC_VALID] in text, "names the BASELINE-VALID recommendation")
    _check(ch._REC_LABEL[ch.REC_DEFER] not in text,
           "does NOT show the DEFER label on an in-band series (data-driven, not templated)")


def test_canonical_history_page_renders_per_side_determinism() -> None:
    # Cycle 45/47 measured whether the ±band is transient-absorption vs measurement
    # noise, and (stronger) whether the stable delta is PER-SIDE determinism or two
    # drifts cancelling. That was terminal-only; the page must surface it. A 2-reading
    # in-band series where BOTH sides are exact at rest earns the strong per-side claim.
    print("test_canonical_history_page_renders_per_side_determinism")
    no_pil = {"access": 100.0, "legibility": 36.4}
    with_pil = {"access": 100.0, "legibility": 90.9}
    pts = [
        _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
        _hist_point("20260727T060000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
    ]
    hist = ch.summarize(pts)
    _check(hist.noise_floor is not None and hist.noise_floor.sides_deterministic,
           "the fixture is per-side deterministic (sanity)")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Is the band real noise, or transient absorption?" in text,
           "renders the noise-floor calibration card")
    _check("DETERMINISTIC at rest" in text, "names the at-rest determinism verdict")
    _check("genuine per-side determinism, not two drifts cancelling" in text,
           "names the strictly-stronger per-side determinism finding")
    _check("2</b> in-band re-scores" in text, "reports the in-band sample size")


def test_canonical_history_per_side_claim_withheld_on_cancellation() -> None:
    # NON-VACUOUS: two in-band readings whose sides jitter in LOCK-STEP (both +2.0)
    # keep the delta deterministic (σ=0) yet are NOT per-side deterministic — the exact
    # cancellation Cycle 47's guard exists for. The card must show the delta-deterministic
    # headline but WITHHOLD the per-side claim; otherwise the strong sentence is templated,
    # not earned.
    print("test_canonical_history_per_side_claim_withheld_on_cancellation")
    pil = {"access": 100.0, "legibility": 90.9}
    pts = [
        _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", pil, pil),   # +39.4 in-band
        _hist_point("20260727T060000Z", 48.1, "F", 87.5, "B", pil, pil),   # +39.4 in-band, both sides moved
    ]
    hist = ch.summarize(pts)
    nf = hist.noise_floor
    _check(nf is not None and nf.deterministic and not nf.sides_deterministic,
           "the fixture has a deterministic delta but NON-deterministic sides (cancellation)")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("DETERMINISTIC at rest" in text, "still names the delta-level determinism")
    _check("genuine per-side determinism" not in text,
           "WITHHOLDS the per-side claim when sides are not exact (cancellation not ruled out)")


def test_canonical_history_noise_card_absent_without_floor() -> None:
    # Honest silence: with < 2 in-band readings there is no measurable floor, so the
    # calibration card must not render at all (never a fabricated determinism claim).
    print("test_canonical_history_noise_card_absent_without_floor")
    hist = _drifting_history()  # 1 in-band anchor + 3 out-of-band -> no floor
    _check(hist.noise_floor is None, "the drifting fixture has < 2 in-band readings (no floor)")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Is the band real noise, or transient absorption?" not in text,
           "no noise-floor card when the floor is unmeasurable")


def _in_band_pts() -> list:
    """Two in-band readings at the pinned +39.4 — a healthy verdict, so the STALE
    banner's warning is earned by AGE alone, not by any drift."""
    no_pil = {"access": 100.0, "legibility": 36.4}
    with_pil = {"access": 100.0, "legibility": 90.9}
    return [
        _hist_point("20260727T050000Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
        _hist_point("20260727T224106Z", 46.1, "F", 85.5, "B", no_pil, with_pil),
    ]


def test_canonical_history_stale_banner_when_signal_old() -> None:
    # The Cycle-51 terminal freshness signal, now on the HTML surface: when the
    # newest re-score is past the 6h floor, a prominent STALE banner warns the
    # reader BEFORE the (old) verdict — even though the verdict itself is a perfectly
    # healthy IN-BAND +39.4 (staleness is about AGE, not drift). Mirrors the terminal
    # "STALE despite in-band" case (test_canonical_history STALE test).
    print("test_canonical_history_stale_banner_when_signal_old")
    latest = datetime(2026, 7, 27, 22, 41, 6, tzinfo=timezone.utc)
    now = latest + timedelta(hours=7, minutes=30)  # 7.5h old -> past the 6h floor
    hist = ch.summarize(_in_band_pts(), now=now)
    _check(hist.band == "in-band", "verdict itself is a healthy in-band reading")
    _check(hist.liveness is not None and not hist.liveness.fresh,
           "liveness reads STALE at 7.5h")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Live signal STALE" in text, "renders the STALE banner heading")
    _check("7.5h old" in text, "names the age of the newest re-score")
    _check("verify runner may be down" in text,
           "warns the runner may be down (the runner-down warning)")
    _check("describes an OLD crawl" in text,
           "warns the verdict below is an old crawl, not the pair now")
    # The banner sits ABOVE the latest-reading card (warn before the stale content).
    _check(text.index("Live signal STALE") < text.index("Latest reading"),
           "the STALE banner renders before the latest-reading card")


def test_canonical_history_fresh_shows_age_no_stale_banner() -> None:
    # Non-vacuous: a FRESH newest re-score (within the floor) shows a quiet age note
    # and NO stale warning — the STALE prose is earned by age, not baked in.
    print("test_canonical_history_fresh_shows_age_no_stale_banner")
    latest = datetime(2026, 7, 27, 22, 41, 6, tzinfo=timezone.utc)
    now = latest + timedelta(hours=1)  # 1.0h old -> fresh
    hist = ch.summarize(_in_band_pts(), now=now)
    _check(hist.liveness is not None and hist.liveness.fresh, "liveness reads FRESH at 1h")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Live signal STALE" not in text, "no STALE banner on a fresh signal")
    _check("1.0h old" in text and "fresh (within the 6h floor)" in text,
           "shows the quiet fresh age note")


def test_canonical_history_no_liveness_line_without_clock() -> None:
    # Honest-None: a series summarized WITHOUT a clock makes no freshness claim, so
    # NEITHER the stale banner nor the fresh age note renders — the age qualifier is
    # driven by the supplied wall clock, never fabricated from the series alone.
    print("test_canonical_history_no_liveness_line_without_clock")
    hist = ch.summarize(_in_band_pts())  # no now= -> liveness is None
    _check(hist.liveness is None, "no clock -> liveness None")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_canonical_history_page(Path(d), history=hist)).read_text()
    _check("Live signal STALE" not in text and "Live signal: newest re-score" not in text,
           "no liveness markup at all when the summary carries no clock")


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
        test_methodology_documents_weight_robustness,
        test_methodology_page_tracks_live_rubric,
        test_build_scorecard_publishes_and_links_methodology,
        test_cap_anchor_helper_is_stable_and_sanitizing,
        test_methodology_cap_rows_carry_anchor_ids,
        test_caps_alert_chip_links_to_methodology,
        test_cap_link_and_methodology_anchor_cannot_drift,
        test_canonical_history_page_written_and_links,
        test_canonical_history_page_renders_drift_diagnosis,
        test_canonical_history_in_band_shows_no_drift,
        test_canonical_history_trend_svg_colors_by_band,
        test_canonical_history_empty_series_renders_gracefully,
        test_canonical_history_names_reference_pair_as_data,
        test_canonical_history_page_renders_recapture_defer,
        test_canonical_history_recapture_is_data_driven,
        test_canonical_history_page_renders_per_side_determinism,
        test_canonical_history_per_side_claim_withheld_on_cancellation,
        test_canonical_history_noise_card_absent_without_floor,
        test_canonical_history_stale_banner_when_signal_old,
        test_canonical_history_fresh_shows_age_no_stale_banner,
        test_canonical_history_no_liveness_line_without_clock,
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
