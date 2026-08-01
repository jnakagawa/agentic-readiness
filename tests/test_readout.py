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
    # Cycle 60 (READOUT): the READOUT complement to Cycle 59's POPULATION-wide
    # weight-robustness guard (guard 17, test_canonical_replay) — the same move
    # Cycle 56 made for the PAIR (guard 15). The sub-section must now also state,
    # in prose a critic can read, that the WHOLE ranking (not just the head delta)
    # is weight-robust because the population is a total pillar-wise dominance
    # chain, and that this too is test-pinned over the reference spectrum.
    for phrase in ("whole ranking", "total dominance chain", "any</b> rung",
                   "reference spectrum"):
        _check(phrase in text,
               f"methodology documents population weight-robustness: {phrase!r}")
    # Vendor-neutral: the reference pair is described by capability, never named.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"methodology names no vendor/domain ({banned!r})")


def test_methodology_documents_check_layer_honesty() -> None:
    # Cycle 64 (READOUT): the READOUT complement to Cycle 63's per-CHECK
    # population earned-dominance guard (guard 19, test_canonical_replay). The
    # weight-robustness sub-section states the chain is a TOTAL dominance chain at
    # the PILLAR layer; Cycle 63 established that at the finer per-CHECK layer one
    # rung is an honest MAJORITY with a single inversion (a human-checkout retail
    # shop's HTTPS/HSTS out-ranks a no-rails API's, absorbed by the trust pillar).
    # The page must surface that refinement in prose a critic can read — that
    # dominance is a pillar-layer property, that the aggregation ABSORBS a lone
    # minority reversal, and that the reversal is surfaced (test-pinned), not
    # hidden — and stay vendor-neutral.
    print("test_methodology_documents_check_layer_honesty")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    for phrase in ("pillar-layer", "per-check", "minority", "absorbs",
                   "HTTPS", "trust", "surfaces", "executable regression test"):
        _check(phrase in text,
               f"methodology documents check-layer honesty: {phrase!r}")
    # It must frame the reversal as disclosed, not hidden (the honesty punchline).
    _check("honest reversal" in text,
           "check-layer refinement frames the inversion as disclosed")
    # Vendor-neutral: no domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"methodology names no vendor/domain ({banned!r})")


def test_methodology_documents_payment_rail_neutrality() -> None:
    # Cycle 80 (READOUT): the READOUT complement to Cycle 78's agent-payment-rail
    # COVERAGE (offering discovery recognizing open rails beyond x402) and Cycle
    # 79's SIGNAL-level relabel-invariance TRUTH guard. The capability lens already
    # says "no payment brand is special-cased"; this makes that concrete for the
    # north-star "many payment rails" flexibility axis in prose a critic can read.
    # It must (a) frame agent-native payment as a CAPABILITY, not a single rail;
    # (b) name the open rail landscape as OPEN STANDARDS (not vendors); (c) say
    # recognition keys on protocol/settlement STRUCTURE so every rail is read on
    # equal terms; and (d) say the "what is declared, not who declares it" property
    # is test-pinned by an identity-relabel guard — while staying vendor-neutral.
    print("test_methodology_documents_payment_rail_neutrality")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    for phrase in ("open payment protocols", "not a rail", "more than one",
                   "protocol and settlement structure", "equal terms",
                   "open standards", "relabels the storefront",
                   "executable regression test"):
        _check(phrase in text,
               f"methodology documents payment-rail neutrality: {phrase!r}")
    # The rail landscape must be named as open standards (the same protocol names
    # the offering signal bank recognizes) — protocol names, never a vendor brand.
    for rail in ("x402", "MPP", "ACP", "UCP", "AP2"):
        _check(rail in text, f"methodology names the open rail {rail!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"methodology names no vendor/domain ({banned!r})")


def test_methodology_documents_async_job_contract() -> None:
    # Cycle 84 (READOUT): the READOUT complement to Cycle 82's async-job COVERAGE
    # (offering discovery recognizing the asynchronous long-running-job contract of
    # a metered API) and Cycle 83's SIGNAL-level relabel-invariance TRUTH guard.
    # The capability chain already names "finish the job"; this makes concrete, in
    # prose a critic can read, the growing class of long-running agent-native APIs
    # (image/video gen, training runs, batch inference) whose result is collected
    # AFTER the request that starts them. It must (a) name the long-running-job
    # class; (b) name the two vendor-neutral collection mechanisms (webhook callback
    # / poll a status endpoint); (c) say recognition keys on the CONTRACT STRUCTURE
    # not the API's name and is pinned by an identity-relabel guard; and (d) stay
    # HONEST about scope — this offering read is diagnostic, off the scoring path,
    # not a scored pillar (the same scored-vs-diagnostic line the leaderboard prose
    # keeps). Vendor-neutral throughout.
    print("test_methodology_documents_async_job_contract")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # The methodology HTML is a multi-line string literal that preserves its source
    # newlines verbatim, so a multi-word phrase can straddle a line break in the
    # rendered output. Match on the whitespace-collapsed text (same technique as
    # test_methodology_documents_calibration) so wording, not source wrapping, is
    # what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("long-running jobs", "webhook callback",
                   "polling a status endpoint", "asynchronous contract",
                   "shape of the contract, not the name",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents async-job contract: {phrase!r}")
    # The vendor-neutral machine-integration vocabulary the offering signal bank
    # anchors on must appear as open convention, never a vendor product.
    for token in ("webhook", "async endpoint", "poll"):
        _check(token in collapsed, f"methodology names async vocabulary {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"async-job prose names no vendor/domain ({banned!r})")


def test_methodology_documents_api_auth_scheme() -> None:
    # Cycle 88 (READOUT): the READOUT complement to Cycle 86's api-auth COVERAGE
    # (offering discovery recognizing programmatic API AUTHENTICATION) and Cycle
    # 87's SIGNAL-level relabel-invariance TRUTH guard. The reach->understand->
    # pay->PROVISION->finish capability lens names "provision without a human";
    # payment-rail prose covers "pay" and async-job prose covers "finish", but the
    # PROVISION leg — an agent can only call a metered API if it can read HOW to
    # authenticate — was never surfaced in prose a critic can read. It must (a)
    # frame credential provisioning as the "provision without a human" capability;
    # (b) name the vendor-neutral credential SCHEMES as open conventions (an HTTP
    # Authorization: Bearer header, an API key / X-API-Key, an OpenAPI
    # securityScheme, OAuth2); (c) say recognition keys on the SCHEME not the
    # vendor and is pinned by an identity-relabel guard; and (d) stay HONEST about
    # scope — this offering read is diagnostic, off the scoring path, not a scored
    # pillar (the same scored-vs-diagnostic line the payment-rail/async-job prose
    # keeps). Vendor-neutral throughout.
    print("test_methodology_documents_api_auth_scheme")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job
    # guard) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Provisioning without a human", "present the right credential",
                   "documents its auth scheme", "credential scheme",
                   "scheme, not the vendor", "relabels the API",
                   "executable regression test", "off the scoring path",
                   "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents api-auth scheme: {phrase!r}")
    # The vendor-neutral credential schemes the offering signal bank anchors on
    # must appear as open conventions, never a vendor product.
    for token in ("Authorization: Bearer", "X-API-Key", "API key",
                  "securityScheme", "OAuth2"):
        _check(token in collapsed, f"methodology names auth scheme {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"api-auth prose names no vendor/domain ({banned!r})")


def test_methodology_documents_error_contract() -> None:
    # Cycle 92 (READOUT): the READOUT complement to Cycle 90's error-contract
    # COVERAGE (offering discovery recognizing a metered API's documented 4xx/5xx
    # error contract) and Cycle 91's SIGNAL-level relabel-invariance TRUTH guard —
    # closing the fourth COVERAGE->TRUTH->READOUT arc after payment-rail (78/79/80),
    # async-job (82/83/84) and api-auth (86/87/88). The capability chain names
    # "finish the job"; async-job prose covers collecting a result, but the
    # RELIABILITY leg — an agent can only RECOVER from a failed call if the error
    # contract is machine-readable — was never surfaced in prose a critic can read.
    # It must (a) frame it as recovering from a failed call / the error contract;
    # (b) name the vendor-neutral machine-readable forms as open conventions (an
    # HTTP status code, an RFC 7807 application/problem+json body, a named error
    # code); (c) say recognition keys on the DECLARED contract not who declares it
    # and is pinned by an identity-relabel guard; and (d) stay HONEST about scope —
    # this offering read is diagnostic, off the scoring path, not a scored pillar
    # (the same scored-vs-diagnostic line the payment-rail/async-job/api-auth prose
    # keeps). Vendor-neutral throughout.
    print("test_methodology_documents_error_contract")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Recovering from a failed call", "recover autonomously",
                   "error contract", "declared contract, not who declares it",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents error-contract: {phrase!r}")
    # The vendor-neutral machine-readable error forms the offering signal bank
    # anchors on must appear as open conventions, never a vendor product: an HTTP
    # status code (4xx/5xx, with 401/429 as the recoverable exemplars), an RFC 7807
    # problem+json body, and a snake_case error code.
    for token in ("4xx/5xx", "status code", "401", "429",
                  "RFC&nbsp;7807", "application/problem+json",
                  "error code", "invalid_request"):
        _check(token in collapsed, f"methodology names error form {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text, f"error-contract prose names no vendor/domain ({banned!r})")


def test_methodology_documents_offering_relative_battery() -> None:
    # Cycle 96 (READOUT): the READOUT complement closing the generate-media
    # plural/participle arc opened by Cycle 94 (COVERAGE — offering discovery
    # recognizing plural/participle generate-media forms) and Cycle 95 (TRUTH —
    # the digital_good DESCRIPTOR recovering plural/participle media nouns). The
    # behavioral battery is OFFERING-RELATIVE (operator directive): tasks are
    # derived from the storefront's OWN discovered offering, and the digital_good
    # task descriptor ("generated image") is filled from the site's OWN media
    # language, normalized across singular/plural/verb-inflection. That derivation
    # was pinned in code + tests but NEVER surfaced in prose a critic can read —
    # a reader of the methodology could not learn WHY a derived task says
    # "generated image" or that the wording comes from the site, not from ASRS.
    # The paragraph must (a) frame the battery as offering-relative — one task per
    # capability the site CLAIMS to sell, unadvertised archetypes never probed
    # (attribution honesty applied to tasks); (b) say the task is worded in the
    # SITE'S own terms, with "generated image" as the derived example; (c) name
    # the vendor-neutral media vocabulary the noun is drawn from (image/video/
    # audio/art, or the "digital output" fallback) and that it is derived from
    # ASRS's own bank matched to the site, never by injecting arbitrary site prose
    # — so it is injection-safe and names no vendor product; (d) say recognition
    # is form-normalized (image / images / generating images -> the SAME singular
    # task noun) and pinned by an executable regression test; and (e) stay HONEST
    # about scope — this battery is diagnostic, off the scoring path, not a scored
    # pillar (the same scored-vs-diagnostic line the sibling prose keeps).
    # Vendor-neutral throughout.
    print("test_methodology_documents_offering_relative_battery")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract guards) so wording, not source wrapping, is pinned.
    collapsed = " ".join(text.split())
    for phrase in ("offering-relative", "claims to sell",
                   "worded in the site", "generated image",
                   "never built to answer", "injection-safe",
                   "form-normalized", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents offering-relative battery: {phrase!r}")
    # The vendor-neutral media vocabulary the digital_good descriptor is drawn
    # from must appear as generic media nouns + the generic fallback, never a
    # vendor product; and the form-normalization exemplars must be present.
    for token in ("image", "video", "audio", "art", "digital output",
                  "images", "generating images"):
        _check(token in collapsed, f"methodology names media form {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text,
               f"offering-relative-battery prose names no vendor/domain ({banned!r})")


def test_methodology_documents_output_license() -> None:
    # Cycle 100 (READOUT): the READOUT complement CLOSING the deliverable-rights arc
    # opened by Cycle 98 (COVERAGE — the digital_good `output-license` offering signal:
    # a commercial licence / royalty-free terms / stated usage rights / ownership of
    # the render) and Cycle 99 (TRUTH — the SIGNAL-level HOST/VENDOR relabel-invariance
    # guard for that signal). The metered_api "complete the job" legs each earned a
    # prose paragraph (payment-rail 80, auth 88, async-job 84, error-contract 92); the
    # digital-good RIGHTS leg was pinned in code + tests but NEVER surfaced in prose a
    # critic can read — a reader could not learn WHY the digital-good archetype weighs
    # deliverable rights, or that an agent handed a render it has no licence to USE has
    # not completed the commercial job. The paragraph must (a) frame it as owning /
    # being able to USE the deliverable, and say an agent that cannot use what it
    # obtained has not completed the commercial job; (b) name the vendor-neutral rights
    # vocabulary the offering signal anchors on as open forms — a commercial licence,
    # royalty-free terms, usage rights, ownership ("you own the output"); (c) keep the
    # signal's PRECISION honesty — a bare `license` word (software / business / a hosted
    # model's own licence) is not a deliverable-rights grant and is read as no signal;
    # (d) say recognition keys on the rights GRANTED not who grants it and is pinned by
    # an identity-relabel executable regression test; and (e) stay HONEST about scope —
    # this offering read is diagnostic, off the scoring path, not a scored pillar (the
    # same scored-vs-diagnostic line the sibling offer-side prose keeps). Vendor-neutral.
    print("test_methodology_documents_output_license")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract guards) so wording, not source wrapping, is pinned.
    collapsed = " ".join(text.split())
    for phrase in ("Owning the deliverable", "usage rights",
                   "not completed the commercial job",
                   "rights the offer grants, not who grants them",
                   "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents output-license: {phrase!r}")
    # The vendor-neutral rights forms the offering signal bank anchors on must appear
    # as open IP/rights conventions, never a vendor product: a commercial licence,
    # royalty-free terms, stated usage rights, and ownership of the output.
    for token in ("commercial licence", "royalty-free", "usage rights",
                  "you own the output"):
        _check(token in collapsed, f"methodology names rights form {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-`license` guard —
    # a hosted model's own licence is not a deliverable-rights grant, no signal.
    for token in ("bare", "license", "model", "no signal"):
        _check(token in collapsed,
               f"methodology keeps output-license precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text,
               f"output-license prose names no vendor/domain ({banned!r})")


def test_methodology_documents_test_mode() -> None:
    # Cycle 104 (READOUT): the READOUT complement CLOSING the test-mode arc opened by
    # Cycle 102 (COVERAGE — the metered_api `test-mode` offering signal: a sandbox /
    # test-key / dry-run facility an agent uses to rehearse a call at ZERO cost) and
    # Cycle 103 (TRUTH — the SIGNAL-level HOST + KEY-PREFIX relabel-invariance guard for
    # that signal). The four other metered_api offer-side legs each earned a prose
    # paragraph (payment-rail 80, auth 88, async-job 84, error-contract 92) and the
    # digital_good rights leg earned one at Cycle 100; the "try the call safely first"
    # leg was pinned in code + tests but NEVER surfaced in prose a critic can read — a
    # reader could not learn WHY a metered API that lets an agent validate its
    # integration and dry-run a call at $0 before authorizing anything real is MORE
    # agent-completable, or how that dovetails with ASRS's own $0-only ethos. The
    # paragraph must (a) frame it as trying/rehearsing the call safely first, at zero
    # cost, before authorizing a real charge, and tie it to the $0-only ethos; (b) name
    # the vendor-neutral test-facility vocabulary the offering signal anchors on as open
    # conventions — a sandbox environment, a test-mode flag, a test API key / credential,
    # a dry-run, the `_test_`/`_sandbox_` key convention; (c) keep the signal's PRECISION
    # honesty — a bare `sandbox`/`test` word (a demo-site title, a sandboxed iframe, a
    # unit_test_runner filename) is not a test facility and is read as no signal; (d) say
    # recognition keys on the facility PROVIDED not who provides it and is pinned by an
    # identity-relabel executable regression test that relabels the host AND its key
    # prefix; and (e) stay HONEST about scope — this offering read is diagnostic, off the
    # scoring path, not a scored pillar (the same scored-vs-diagnostic line the sibling
    # offer-side prose keeps). Vendor-neutral throughout.
    print("test_methodology_documents_test_mode")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract / output-license guards) so wording, not source
    # wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Trying the call safely first", "zero cost", "$0-only",
                   "test facility", "facility the offer provides, not who provides it",
                   "and its key prefix", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents test-mode: {phrase!r}")
    # The vendor-neutral test-facility vocabulary the offering signal bank anchors on
    # must appear as open machine-integration conventions, never a vendor product: a
    # sandbox environment, a test-mode flag, a test credential/API key, a dry-run, and
    # the masked-stub `_test_`/`_sandbox_` key convention.
    for token in ("sandbox environment", "test-mode", "test API key",
                  "dry-run", "_test_", "_sandbox_"):
        _check(token in collapsed, f"methodology names test facility {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `sandbox`/`test` word (a demo-site title, a sandboxed iframe, a unit_test_runner
    # filename) is not a test facility and is read as no signal.
    for token in ("bare", "no signal", "unit_test_runner", "Sandbox"):
        _check(token in collapsed,
               f"methodology keeps test-mode precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight"):
        _check(banned not in text,
               f"test-mode prose names no vendor/domain ({banned!r})")


def test_methodology_documents_pagination() -> None:
    # Cycle 108 (READOUT): the READOUT complement CLOSING the pagination arc opened by
    # Cycle 106 (COVERAGE — the metered_api `pagination` offering signal: a cursor /
    # next-page URL / paginated collection response an agent follows to walk a
    # multi-page result set to completion) and Cycle 107 (TRUTH — the SIGNAL-level
    # HOST relabel-invariance guard for that signal). The four earlier metered_api
    # offer-side legs each earned a prose paragraph (payment-rail 80, auth 88,
    # async-job 84, error-contract 92) and the test-mode leg its own at Cycle 104; the
    # "walk the paged collection to completion" leg was pinned in code + tests but
    # NEVER surfaced in prose a critic can read — a reader could not learn WHY a
    # metered API that documents how to page through a collection is MORE
    # agent-completable, or how an agent that stops at the first page silently
    # under-completes the retrieval. The paragraph must (a) frame it as walking a
    # multi-page result set to completion / the pagination contract, and name the
    # under-completion failure (stop at page one, report a partial answer as whole);
    # (b) name the vendor-neutral pagination vocabulary the offering signal anchors on
    # as open conventions — a cursor query parameter, a next/previous page URL, a
    # paginated collection response; (c) keep the signal's PRECISION honesty — a bare
    # `next`/`cursor` word (a retail product link, a "next campaign" banner, a text
    # cursor, the "next page of the novel") is not an API pagination facility and is
    # read as no signal; (d) say recognition keys on the CONTRACT the API documents
    # not who published it and is pinned by an identity-relabel executable regression
    # test; and (e) stay HONEST about scope — this offering read is diagnostic, off the
    # scoring path, not a scored pillar (the same scored-vs-diagnostic line the sibling
    # offer-side prose keeps). Vendor-neutral throughout.
    print("test_methodology_documents_pagination")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract / test-mode guards) so wording, not source
    # wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Walking the whole collection", "under-completes the retrieval",
                   "pagination contract", "contract the API documents, not who published it",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents pagination: {phrase!r}")
    # The vendor-neutral pagination vocabulary the offering signal bank anchors on
    # must appear as open collection conventions, never a vendor product: a cursor
    # parameter, a next/previous page URL, a paginated collection response.
    for token in ("cursor", "page URL", "paginated collection response"):
        _check(token in collapsed, f"methodology names pagination convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `next`/`cursor` word (a retail product link, a "next campaign" banner, a text
    # cursor, the "next page of the novel") is not an API pagination facility and is
    # read as no signal.
    for token in ("bare", "no signal", "next campaign", "next page of the novel"):
        _check(token in collapsed,
               f"methodology keeps pagination precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"pagination prose names no vendor/domain ({banned!r})")


def test_methodology_documents_cancel_job() -> None:
    # Cycle 112 (READOUT): the READOUT complement CLOSING the cancel-job arc opened by
    # Cycle 110 (COVERAGE — the metered_api `cancel-job` offering signal: how an agent
    # ABORTS a long-running job it already submitted — a `.../cancel` endpoint on the
    # job resource, a `Cancel-After` deadline header, or a documented `canceled`
    # terminal job state) and Cycle 111 (TRUTH — the SIGNAL-level HOST
    # relabel-invariance guard for that signal). This is the SEVENTH metered_api
    # offer-side leg to complete the full COVERAGE->TRUTH->READOUT arc (after
    # payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88, error-contract
    # 90/91/92, test-mode 102/103/104, pagination 106/107/108). The "abort a runaway
    # job to bound your spend" leg was pinned in code + tests but NEVER surfaced in
    # prose a critic can read — a reader could not learn WHY a metered API that
    # documents how to cancel a submitted job is MORE agent-completable, or how an
    # agent that cannot stop a runaway generation keeps paying for compute it no longer
    # wants. The paragraph must (a) frame it as aborting a long-running job to bound
    # spend / the cancellation contract, and name the capital-drain failure (a runaway
    # or wrong job billing while it runs, no way to stop it); (b) name the
    # vendor-neutral REST cancellation vocabulary the offering signal anchors on as open
    # conventions — a `.../cancel` endpoint on a job resource, a `Cancel-After` deadline
    # header, a `canceled` job state; (c) keep the signal's PRECISION honesty — a bare
    # `cancel` word ("cancel your subscription", a "cancellation policy", "cancel your
    # order", a canceled flight) is not a job-cancellation facility and is read as no
    # signal; (d) say recognition keys on the CONTRACT the API documents not who
    # published it and is pinned by an identity-relabel executable regression test; and
    # (e) stay HONEST about scope — this offering read is diagnostic, off the scoring
    # path, not a scored pillar (the same scored-vs-diagnostic line the sibling
    # offer-side prose keeps). Vendor-neutral throughout.
    print("test_methodology_documents_cancel_job")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract / test-mode / pagination guards) so wording, not
    # source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Aborting a runaway job", "bound its own spend",
                   "cancellation contract",
                   "contract the API documents, not who published it",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents cancel-job: {phrase!r}")
    # The vendor-neutral cancellation vocabulary the offering signal bank anchors on
    # must appear as open REST conventions, never a vendor product: a cancel endpoint
    # on a job resource, a Cancel-After deadline header, a canceled job state.
    for token in ("cancel endpoint on a job resource", "Cancel-After", "job state"):
        _check(token in collapsed, f"methodology names cancel convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `cancel` word ("cancel your subscription", a "cancellation policy", a canceled
    # flight) is not a job-cancellation facility and is read as no signal.
    for token in ("bare", "no signal", "cancel your subscription",
                  "cancellation policy", "flight was canceled"):
        _check(token in collapsed,
               f"methodology keeps cancel-job precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"cancel-job prose names no vendor/domain ({banned!r})")


def test_methodology_documents_streaming_response() -> None:
    # Cycle 128 (READOUT): the READOUT complement CLOSING the streaming-response arc
    # opened by Cycle 126 (COVERAGE — the metered_api `streaming-response` offering
    # signal: how an agent consumes output INCREMENTALLY over the OPEN connection as
    # it is produced — server-sent events / text/event-stream / a streaming
    # API/endpoint that streams the output/tokens) and Cycle 127 (TRUTH — the
    # SIGNAL-level HOST relabel-invariance guard for that signal). This is the EIGHTH
    # metered_api offer-side leg to complete the full COVERAGE->TRUTH->READOUT arc
    # (after payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88,
    # error-contract 90/91/92, test-mode 102/103/104, pagination 106/107/108,
    # cancel-job 110/111/112). The "consume the output as it streams" leg was pinned in
    # code + tests but NEVER surfaced in prose a critic can read — a reader could not
    # learn WHY a metered API that documents how its output streams is MORE
    # agent-completable, or how it is the IN-BAND sibling of the async-job leg (async
    # collects a completed job OUT of band; streaming delivers partial output WITHIN the
    # same request over the live connection). The paragraph must (a) frame it as
    # consuming the output as it streams / the streaming contract, name it the in-band
    # sibling of async-job, and name the failure (block on a long call it could have
    # consumed progressively, or a `stream` URL it never learns how to open); (b) name
    # the vendor-neutral open-standard streaming vocabulary the offering signal anchors
    # on as open conventions — server-sent events, the text/event-stream media type, a
    # streaming endpoint; (c) keep the signal's PRECISION honesty — a bare `stream`/`SSE`
    # token (an application/octet-stream binary MIME, the Shanghai Stock Exchange (SSE),
    # sum of squared errors, a live stream, the bloodstream, a "stream of consciousness")
    # is not a streaming delivery and is read as no signal, and a bare SSE must never
    # conjure a metered-API claim; (d) say recognition keys on the CONTRACT the API
    # documents not who published it and is pinned by an identity-relabel executable
    # regression test; and (e) stay HONEST about scope — this offering read is
    # diagnostic, off the scoring path, not a scored pillar (the same
    # scored-vs-diagnostic line the sibling offer-side prose keeps). Vendor-neutral
    # throughout.
    print("test_methodology_documents_streaming_response")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract / test-mode / pagination / cancel-job guards) so
    # wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Consuming the output as it streams", "in-band sibling",
                   "streaming contract",
                   "contract the API documents, not who published it",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents streaming-response: {phrase!r}")
    # The vendor-neutral streaming vocabulary the offering signal bank anchors on must
    # appear as open delivery conventions, never a vendor product: server-sent events,
    # the text/event-stream media type, a streaming endpoint.
    for token in ("server-sent events", "text/event-stream", "streaming endpoint"):
        _check(token in collapsed, f"methodology names streaming convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `stream`/`SSE` token (an octet-stream MIME, the Shanghai Stock Exchange (SSE), a
    # "stream of consciousness") is not a streaming delivery and is read as no signal.
    for token in ("bare", "no signal", "octet-stream", "Shanghai Stock Exchange",
                  "stream of consciousness"):
        _check(token in collapsed,
               f"methodology keeps streaming-response precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"streaming-response prose names no vendor/domain ({banned!r})")


def test_methodology_documents_webhook_verification() -> None:
    # Cycle 136 (READOUT): the READOUT complement CLOSING the webhook-verification arc
    # opened by Cycle 134 (COVERAGE — the tenth metered_api `webhook-verification`
    # offering signal: whether an agent can TRUST that an inbound async callback is
    # GENUINELY from the API rather than a forged/spoofed webhook — a webhook signing
    # secret, a webhook signature, verifying inbound webhook requests) and Cycle 135
    # (TRUTH — the SIGNAL-level HOST relabel-invariance guard for that signal). This is
    # the NINTH metered_api offer-side leg to complete the full COVERAGE->TRUTH->READOUT
    # arc (after payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88,
    # error-contract 90/91/92, test-mode 102/103/104, pagination 106/107/108, cancel-job
    # 110/111/112, streaming-response 126/127/128). The webhook-AUTHENTICITY leg was
    # pinned in code + tests but NEVER surfaced in prose a critic can read — a reader
    # could not learn WHY a metered API that documents how an agent verifies an inbound
    # callback is MORE agent-completable, or how it is the SECURITY/TRUST sibling of the
    # async-job leg (async-job says a webhook DELIVERY channel EXISTS; webhook-
    # verification says whether the agent can AUTHENTICATE what arrives on it). The
    # paragraph must (a) frame it as trusting the async callback / verifying an inbound
    # webhook is authentic, name it the security sibling of async-job, and name the
    # failure (an agent acts on an unverified "job complete" webhook, is tricked by a
    # forged/spoofed callback into treating fabricated output as real or releasing a
    # payment) and its tie to the $0-only capital-safety ethos; (b) name the vendor-
    # neutral webhook-security vocabulary the offering signal anchors on as open
    # conventions — a webhook signature, a webhook signing secret, an X-Webhook-Signature
    # header; (c) keep the signal's PRECISION honesty — a bare `signature`/`signing
    # secret` (a marketing "signature look", a settlement signature a payment proof
    # verifies locally, a signed-URL signing secret for file access, a digital signature
    # on a contract, a webhook that merely EXISTS = async-job's turf) is not webhook
    # verification and is read as no signal; (d) say recognition keys on the CONTRACT the
    # API documents not who published it and is pinned by an identity-relabel executable
    # regression test; and (e) stay HONEST about scope — this offering read is diagnostic,
    # off the scoring path, not a scored pillar (the same scored-vs-diagnostic line the
    # sibling offer-side prose keeps). Vendor-neutral throughout.
    print("test_methodology_documents_webhook_verification")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # streaming-response / cancel-job guards) so wording, not source wrapping, is what
    # the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Trusting the async callback", "security sibling",
                   "forged or spoofed callback", "treating fabricated output as real",
                   "releasing a payment", "verifies an inbound webhook is authentic",
                   "contract the API documents, not who published it",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents webhook-verification: {phrase!r}")
    # The vendor-neutral webhook-security vocabulary the offering signal bank anchors on
    # must appear as open conventions, never a vendor product: a webhook signature, a
    # webhook signing secret, an X-Webhook-Signature header.
    for token in ("webhook signature", "webhook signing secret", "X-Webhook-Signature"):
        _check(token in collapsed, f"methodology names webhook-security convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `signature`/`signing secret` (a settlement signature a payment proof verifies, a
    # signed-URL signing secret, a digital signature on a contract) is not webhook
    # verification and is read as no signal.
    for token in ("bare", "no signal", "settlement signature", "signed-URL",
                  "digital signature"):
        _check(token in collapsed,
               f"methodology keeps webhook-verification precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"webhook-verification prose names no vendor/domain ({banned!r})")


def test_methodology_documents_output_resolution() -> None:
    # Cycle 140 (READOUT): the READOUT complement CLOSING the output-resolution arc
    # opened by Cycle 138 (COVERAGE — the eleventh digital_good `output-resolution`
    # offering signal: the output RESOLUTION / pixel DIMENSIONS / ASPECT RATIO of the
    # generated deliverable an agent must request and can rely on) and Cycle 139 (TRUTH
    # — the SIGNAL-level HOST relabel-invariance guard for that signal). This is the
    # digital_good output-SPEC leg completing the full COVERAGE->TRUTH->READOUT arc
    # (mirroring the metered_api siblings webhook-verification 134/135/136,
    # streaming-response 126/127/128, cancel-job 110/111/112). The output-SHAPE leg was
    # pinned in code + tests but NEVER surfaced in prose a critic can read — a reader
    # could not learn WHY a generation storefront that documents its output resolutions
    # is MORE agent-completable, or how the leg is DISTINCT from every existing
    # digital_good leg: generation/render say WHAT is produced, hosted-output says WHERE
    # it is delivered, output-license whether the agent may USE it, content-provenance
    # whether the agent can TRUST it — NONE says the physical SHAPE the agent must
    # parameterize its request with. The paragraph must (a) frame it as specifying the
    # deliverable's shape / the output-resolution contract, name it the output-spec
    # sibling of owning/trusting the render, and name the failure (an agent requests a
    # size the API cannot produce, or is handed a deliverable at the wrong resolution for
    # its downstream use — a hero image delivered at thumbnail size); (b) name the
    # vendor-neutral output-format vocabulary the offering signal anchors on as open
    # conventions — a maxResolution field, a WxH pixel dimension, an aspect ratio; (c)
    # keep the signal's PRECISION honesty — a bare `resolution` (dispute resolution, a
    # New-Year resolution, DNS resolution, a hosted model's own Super-resolution/enhance-
    # image-resolution FEATURE, a screen/monitor/display hardware resolution) is not an
    # output spec and is read as no signal; (d) say recognition keys on the SHAPE the
    # offer documents not who documents it and is pinned by an identity-relabel
    # executable regression test; and (e) stay HONEST about scope — this offering read is
    # diagnostic, off the scoring path, not a scored pillar. Vendor-neutral throughout.
    print("test_methodology_documents_output_resolution")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the webhook-verification
    # / streaming-response guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Specifying the deliverable", "output-spec sibling",
                   "output resolution", "output-resolution contract",
                   "wrong resolution for its downstream use",
                   "shape the offer documents, not who documents it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents output-resolution: {phrase!r}")
    # The vendor-neutral output-format vocabulary the offering signal bank anchors on
    # must appear as open conventions, never a vendor product: a maxResolution field, a
    # WxH pixel dimension, an aspect ratio.
    for token in ("maxResolution", "pixel dimension", "aspect ratio"):
        _check(token in collapsed, f"methodology names output-format convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `resolution` (dispute resolution, a hosted model's Super-resolution feature, a
    # screen/monitor/display hardware resolution) is not an output spec, no signal.
    for token in ("bare", "no signal", "dispute resolution",
                  "Super-resolution", "screen / monitor / display"):
        _check(token in collapsed,
               f"methodology keeps output-resolution precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"output-resolution prose names no vendor/domain ({banned!r})")


def test_methodology_documents_payment_receipt() -> None:
    # Cycle 144 (READOUT): the READOUT complement CLOSING the payment-receipt arc
    # opened by Cycle 142 (COVERAGE — the metered_api `payment-receipt` offering
    # signal: the machine-readable PROOF-OF-PAYMENT an agent gets BACK after a paid
    # call and logs to reconcile its own spend) and Cycle 143 (TRUTH — the SIGNAL-
    # level HOST relabel-invariance guard for that signal). This is the metered_api
    # ACCOUNTING / capital-safety leg completing the full COVERAGE->TRUTH->READOUT
    # arc (mirroring the metered_api siblings webhook-verification 134/135/136,
    # streaming-response 126/127/128, cancel-job 110/111/112, and the digital_good
    # output-resolution 138/139/140). The accounting leg was pinned in code + tests
    # but NEVER surfaced in prose a critic can read — a reader could not learn WHY a
    # metered offer that returns a receipt an agent can log is MORE agent-completable,
    # or how it is DISTINCT from the payment RAILS: an agent-payment rail (x402, a
    # machine-payable endpoint) is the PAY leg (WHETHER the agent can pay); the
    # payment-receipt is the proof that comes BACK so the agent can reconcile what it
    # was charged. The paragraph must (a) frame it as accounting for the spend /
    # trusting the receipt, name it the capital-safety accounting sibling of the
    # payment rails, tie the PAY leg to the receipt-comes-back leg, tie it to the
    # $0-only capital-safety ethos, and name the failure (an agent pays and cannot
    # reconcile its own spend — capital it can neither confirm nor dispute); (b) name
    # the vendor-neutral proof-of-payment vocabulary the offering signal anchors on as
    # open conventions — a receipt header, a payment / settlement receipt, a serialized
    # receipt, a spend record, explicit proof of payment; (c) keep the signal's
    # PRECISION honesty — a bare `receipt` (an email receipt, a read receipt, an order
    # receipt on a retail checkout, "in receipt of" a message, a warehouse receipt of
    # goods) is not proof of payment and is read as no signal; (d) say recognition keys
    # on the RECEIPT the offer returns not who returns it and is pinned by an
    # identity-relabel executable regression test; and (e) stay HONEST about scope —
    # this offering read is diagnostic, off the scoring path, not a scored pillar.
    # Vendor-neutral throughout.
    print("test_methodology_documents_payment_receipt")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the output-resolution
    # / webhook-verification guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Accounting for the spend", "capital-safety accounting sibling",
                   "reconcile its own spend", "PAY leg",
                   "proof that comes back to reconcile the spend",
                   "receipt the offer returns, not who returns it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents payment-receipt: {phrase!r}")
    # The vendor-neutral proof-of-payment vocabulary the offering signal bank anchors
    # on must appear as open conventions, never a vendor product: a receipt header, a
    # payment / settlement receipt, a serialized receipt, a spend record, proof of payment.
    for token in ("receipt header", "settlement receipt", "serialized receipt",
                  "spend record", "proof of payment"):
        _check(token in collapsed, f"methodology names proof-of-payment convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `receipt` (email/read/order/goods receipt, "in receipt of") is not proof of
    # payment, no signal.
    for token in ("bare", "no signal", "email receipt", "read receipt",
                  "order receipt", "receipt of goods"):
        _check(token in collapsed,
               f"methodology keeps payment-receipt precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"payment-receipt prose names no vendor/domain ({banned!r})")


def test_methodology_documents_failure_not_billed() -> None:
    # Cycle 154 (READOUT): the READOUT complement CLOSING the failure-not-billed arc
    # opened by Cycle 152 (COVERAGE — the metered_api `failure-not-billed` offering
    # signal: whether a metered call that FAILS — a render did not complete, a job
    # errored, a request timed out — is NOT charged) and Cycle 153 (TRUTH — the
    # SIGNAL-level HOST relabel-invariance guard for that signal). This is the metered
    # capital-safety FAILURE-BILLING leg completing the full COVERAGE->TRUTH->READOUT
    # arc (mirroring payment-receipt 142/143/144, webhook-verification 134/135/136,
    # cancel-job 110/111/112). The leg was pinned in code + tests but NEVER surfaced in
    # prose a critic can read — a reader could not learn WHY a metered offer that
    # promises a failed call is not billed is MORE agent-completable, or how it is
    # DISTINCT from its neighbours: the receipt is proof of a SUCCESSFUL charge, the
    # error contract is the SHAPE of a failure (not its price), a free trial is a
    # subscription's $0 window. The paragraph must (a) frame it as not paying for a
    # call that failed, name it the capital-safety sibling of the receipt leg, tie it to
    # the $0-only capital-safety ethos ("you don't pay for work you didn't get"), and
    # name the failure (an autonomous per-call buyer that cannot tell whether a failed
    # unit is silently charged cannot bound its spend against a flaky endpoint); (b)
    # name the vendor-neutral failure-billing vocabulary the offering signal anchors on
    # as open conventions — a failure token (failed/errored/did not complete/timed out)
    # joined to not/never charged or billed, or only charged for successful/completed
    # calls; (c) keep the signal's PRECISION honesty — a bare "not charged" (a
    # subscription trial's "card is not charged until the trial ends" $0-evaluation
    # promise) is not a failure guarantee and is read as no signal; (d) say recognition
    # keys on the failure-billing contract the offer documents not who documents it and
    # is pinned by an identity-relabel executable regression test; and (e) stay HONEST
    # about scope — this offering read is diagnostic, off the scoring path, not a scored
    # pillar. Vendor-neutral throughout.
    print("test_methodology_documents_failure_not_billed")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the payment-receipt /
    # output-resolution guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Not paying for a call that failed", "capital-safety sibling",
                   "bound its own spend", "flaky endpoint",
                   "you don&rsquo;t pay for work you didn&rsquo;t get",
                   "failure-billing contract the offer documents, not who documents it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents failure-not-billed: {phrase!r}")
    # The vendor-neutral failure-billing vocabulary the offering signal bank anchors on
    # must appear as open conventions: a failure token joined to not/never charged or
    # billed, or only charged for successful/completed calls.
    for token in ("failure token", "not / never charged or billed",
                  "only charged for successful / completed", "did not complete",
                  "timed out"):
        _check(token in collapsed, f"methodology names failure-billing convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # "not charged" (a subscription trial's $0-evaluation promise) is not a failure
    # guarantee, no signal.
    for token in ("bare", "no signal", "not charged until the trial ends",
                  "$0-evaluation promise"):
        _check(token in collapsed,
               f"methodology keeps failure-not-billed precision note: {token!r}")
    # DISTINCTNESS: the prose must name the neighbours it is distinct from so a reader
    # cannot conflate the failure-billing leg with the receipt, error-contract, or trial.
    for token in ("proof of a", "successful", "shape", "free trial"):
        _check(token in collapsed,
               f"methodology keeps failure-not-billed distinctness note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"failure-not-billed prose names no vendor/domain ({banned!r})")


def test_methodology_documents_reserve_and_settle() -> None:
    # Cycle 158 (READOUT): the READOUT complement CLOSING the reserve-and-settle arc
    # opened by Cycle 156 (COVERAGE — the metered_api `reserve-and-settle` offering
    # signal: whether an agent can CAP its per-call exposure up front by reserving a
    # spend CEILING, being charged only the ACTUAL usage, the unused remainder refunded)
    # and Cycle 157 (TRUTH — the SIGNAL-level HOST relabel-invariance guard for that
    # signal). This is the metered capital-safety leg that bounds a SUCCESSFUL call's
    # cost, completing the full COVERAGE->TRUTH->READOUT arc (mirroring failure-not-billed
    # 152/153/154, payment-receipt 142/143/144, webhook-verification 134/135/136). The
    # leg was pinned in code + tests but NEVER surfaced in prose a critic can read — a
    # reader could not learn WHY a metered offer that lets an agent reserve a ceiling and
    # pay only actual is MORE agent-completable, or how it is DISTINCT from its
    # neighbours: the payment rails (x402, a machine-payable endpoint) say the agent CAN
    # pay; the receipt is proof of a SUCCESSFUL charge after the fact; the pricing signals
    # say HOW you are charged on success; and failure-not-billed bounds a FAILURE's cost
    # while this bounds a SUCCESS's, before the agent commits. The paragraph must (a)
    # frame it as bounding a single call's cost up front, name it the capital-safety
    # sibling of the failure-not-billed leg, tie it to the $0-only capital-safety ethos,
    # and name the failure (a per-call buyer against a variable-priced endpoint cannot
    # bound its worst-case exposure until the bill arrives); (b) name the vendor-neutral
    # reserve-and-settle vocabulary the offering signal anchors on as open conventions —
    # a reserve-and-pay-actual rail, reserving a spend ceiling, being charged only actual
    # against a reserved ceiling, an escrow/channel that refunds the remainder; (c) keep
    # the signal's PRECISION honesty — a bare reserve/refund/ceiling/escrow (a hotel
    # reservation, "we reserve the right", a retail full refund, cloud reserved capacity,
    # a ceiling fan) is no signal; (d) say recognition keys on the reserve-and-settle
    # contract the offer documents not who documents it and is pinned by an identity-
    # relabel executable regression test; and (e) stay HONEST about scope — this offering
    # read is diagnostic, off the scoring path, not a scored pillar. Vendor-neutral throughout.
    print("test_methodology_documents_reserve_and_settle")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the failure-not-billed /
    # payment-receipt guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Bounding a single call", "capital-safety sibling",
                   "worst-case cost per request", "credit-card hold",
                   "reserve-and-settle contract the offer documents, not who documents it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents reserve-and-settle: {phrase!r}")
    # The vendor-neutral reserve-and-settle vocabulary the offering signal bank anchors on
    # must appear as open conventions: a reserve-and-pay-actual rail, a reserved spend
    # ceiling, being charged only actual, an escrow/channel that refunds the remainder.
    for token in ("reserve-and-pay-actual", "spend ceiling", "charged only actual",
                  "refunds the remainder"):
        _check(token in collapsed, f"methodology names reserve-and-settle convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # reserve/refund/ceiling/escrow (a hotel reservation, reserve-the-right, retail refund,
    # reserved capacity, ceiling fan) is no signal.
    for token in ("bare", "no signal", "reserve the right", "reserved capacity",
                  "ceiling fan"):
        _check(token in collapsed,
               f"methodology keeps reserve-and-settle precision note: {token!r}")
    # DISTINCTNESS: the prose must name the neighbours it is distinct from so a reader
    # cannot conflate reserve-and-settle with the payment rails, receipt, pricing, or
    # failure-not-billed leg.
    for token in ("can pay", "proof of a", "failure-not-billed", "success&rsquo;s"):
        _check(token in collapsed,
               f"methodology keeps reserve-and-settle distinctness note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"reserve-and-settle prose names no vendor/domain ({banned!r})")


def test_methodology_documents_plan_purchase() -> None:
    # Cycle 148 (READOUT): the READOUT complement CLOSING the plan-purchase arc opened
    # by Cycle 146 (COVERAGE — the SUBSCRIPTION `plan-purchase` offering signal: whether
    # an agent can programmatically BUY / commit to a credit-or-subscription plan via an
    # API call, the "commit without a human" leg) and Cycle 147 (TRUTH — the SIGNAL-level
    # HOST relabel-invariance guard for that signal). This is the SECOND subscription-
    # archetype leg to complete a full COVERAGE->TRUTH->READOUT arc (after free-trial
    # 114/115/116) and mirrors the metered_api payment-receipt arc 142/143/144. The
    # commit leg was pinned in code + tests but NEVER surfaced in prose a critic can read
    # — a reader could not learn WHY a subscription that lets an agent buy the plan
    # programmatically is MORE agent-completable, or how it is DISTINCT from the three
    # subscription/payment reads already on the page: the recurring PRICE an agent reads,
    # the $0 free-trial EVALUATION leg, and the payment RAILS (x402 / a machine-payable
    # endpoint = the PAY leg, WHETHER the agent can pay at all). plan-purchase is the
    # subscription-archetype counterpart of metered_api's self-provisioning (obtain access
    # without a human) — here, take on the recurring commitment without a human. The
    # paragraph must (a) frame it as the commit leg, distinguish it from the price / $0
    # evaluation / payment-rails reads, name it the counterpart of self-provisioning, and
    # name the failure (a human runs a pricing-page checkout or dashboard onboarding → the
    # agent stranded one step short of the recurring offer); (b) name the vendor-neutral
    # plan-commitment vocabulary the offering signal anchors on as open conventions — a
    # plan-purchase endpoint on the plan resource, a purchasable plan, a buy/purchase/
    # activate verb naming a credit or subscription plan; (c) keep the signal's PRECISION
    # honesty — a bare `plan` / "subscribe to a plan" on a pricing page / a dashboard
    # onboarding flow / bare "subscription plans" marketing is the HUMAN path, no signal;
    # (d) say recognition keys on the PLAN the offer lets an agent BUY not who sells it,
    # pinned by an identity-relabel executable regression test; and (e) stay HONEST about
    # scope — this offering read is diagnostic, off the scoring path, not a scored pillar.
    # Vendor-neutral throughout.
    print("test_methodology_documents_plan_purchase")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the payment-receipt /
    # free-trial / self-provisioning guards) so wording, not source wrapping, is pinned.
    collapsed = " ".join(text.split())
    for phrase in ("Committing to a plan without a human", "commit leg",
                   "self-provisioning", "PAY leg",
                   "plan the offer lets an agent buy, not who sells it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents plan-purchase: {phrase!r}")
    # The vendor-neutral plan-commitment vocabulary the offering signal bank anchors on
    # must appear as open subscription conventions, never a vendor product: a plan-purchase
    # endpoint on the plan resource, a purchasable plan, a buy/purchase/activate verb
    # naming a credit or subscription plan.
    for token in ("/plans/", "purchasable plan", "credit or subscription plan"):
        _check(token in collapsed, f"methodology names plan-commitment convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's guard — the HUMAN plan path
    # (a bare `plan`, "subscribe to a plan", dashboard onboarding, bare "subscription
    # plans" marketing) is not the agentic commit and is read as no signal.
    for token in ("bare", "no signal", "subscribe to a plan",
                  "dashboard onboarding", "subscription plans"):
        _check(token in collapsed,
               f"methodology keeps plan-purchase precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"plan-purchase prose names no vendor/domain ({banned!r})")


def test_methodology_documents_free_trial() -> None:
    # Cycle 116 (READOUT): the READOUT complement CLOSING the free-trial arc opened by
    # Cycle 114 (COVERAGE — the `free-trial` offering signal added to the SUBSCRIPTION
    # archetype bank: a no-cost evaluation of a recurring offer BEFORE billing begins)
    # and Cycle 115 (TRUTH — the SIGNAL-level relabel-invariance guard for that signal).
    # This is the FIRST SUBSCRIPTION-archetype leg to complete a full COVERAGE->TRUTH->
    # READOUT arc — every prior prose leg (payment-rail 78/79/80, async-job 82/83/84,
    # api-auth 86/87/88, error-contract 90/91/92, test-mode 102/103/104, pagination
    # 106/107/108, cancel-job 110/111/112) was a metered_api offer-side leg, plus the
    # digital_good rights leg at Cycle 100. The "evaluate the recurring plan at $0
    # before committing to billing" leg was pinned in code + tests but NEVER surfaced
    # in prose a critic can read — a reader could not learn WHY a subscription that lets
    # an agent try the plan free before any charge is MORE agent-completable, or how it
    # is the subscription-side mirror of trying a metered call safely first. The
    # paragraph must (a) frame it as evaluating/trying the recurring subscription at $0
    # before any charge begins, tie it to the $0-only ethos, and name the failure
    # (commit to recurring billing sight-unseen); (b) name the vendor-neutral trial-offer
    # vocabulary the offering signal anchors on as open conventions — a free trial, a
    # trial period, an N-day trial, a trial account/allowance; (c) keep the signal's
    # PRECISION honesty — a bare `trial` word (a clinical trial, a court trial, "trial
    # and error", "trial by fire", "on trial") is not a free-trial offer and is read as
    # no signal; (d) say recognition keys on the TRIAL the offer grants not who grants
    # it and is pinned by an identity-relabel executable regression test; and (e) stay
    # HONEST about scope — this offering read is diagnostic, off the scoring path, not a
    # scored pillar (the same scored-vs-diagnostic line the sibling offer-side prose
    # keeps). Vendor-neutral throughout.
    print("test_methodology_documents_free_trial")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the async-job /
    # api-auth / error-contract / test-mode / pagination / cancel-job guards) so
    # wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Evaluating a subscription at $0 first",
                   "recurring billing sight-unseen", "$0-only", "trial offer",
                   "trial the offer grants, not who grants it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents free-trial: {phrase!r}")
    # The vendor-neutral trial-offer vocabulary the offering signal bank anchors on
    # must appear as open subscription conventions, never a vendor product: a free
    # trial, a trial period, an N-day trial, a trial account/allowance.
    for token in ("free trial", "trial period", "N-day trial", "trial account"):
        _check(token in collapsed, f"methodology names trial-offer convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `trial` word (a clinical trial, a court trial, "trial and error") is not a
    # free-trial offer and is read as no signal.
    for token in ("bare", "no signal", "clinical trial", "trial and error"):
        _check(token in collapsed,
               f"methodology keeps free-trial precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"free-trial prose names no vendor/domain ({banned!r})")


def test_methodology_documents_self_provisioning() -> None:
    # Cycle 132 (READOUT): the READOUT complement CLOSING the ninth metered_api arc,
    # opened by Cycle 130 (COVERAGE — the `self-provisioning` offering signal: whether
    # an autonomous agent can OBTAIN API access with no signup / no human account
    # creation / provisioning its own identity) and Cycle 131 (TRUTH — the SIGNAL-level
    # relabel-invariance guard for that signal). Self-provisioning is DISTINCT from the
    # api-auth leg (Cycle 86/87/88 — presenting a credential you already HOLD) and the
    # test-mode leg (102/103/104 — trying safely first): NONE of the prior legs said
    # whether a HUMAN must onboard the agent before it can obtain a credential at all. A
    # metered API whose credentials only a human can issue is not agent-completable
    # end-to-end however cleanly it documents auth/errors/async — a load-bearing gap that
    # was pinned in code + tests but never surfaced in prose a critic can read. The
    # paragraph must (a) frame it as obtaining access WITHOUT a human onboarding step,
    # positioned before the credential can be presented, and name the failure (a human
    # must sign up on a dashboard → an autonomous agent stranded at the door); (b) name
    # the vendor-neutral agent-onboarding vocabulary the offering signal anchors on as
    # open conventions — no signup, no human account creation, an agent provisioning its
    # own identity, a self-provision path; (c) keep the signal's PRECISION honesty — it
    # recognizes ONLY the affirmative agentic path and never the OPPOSITE human one (a
    # "sign up on the dashboard for an API key" instruction, a 401 No API key error, the
    # pricing sense "no signup fees"); (d) say recognition keys on WHETHER A HUMAN MUST
    # ONBOARD the agent not who runs the API, pinned by an identity-relabel executable
    # regression test; and (e) stay HONEST about scope — this offering read is diagnostic,
    # off the scoring path, not a scored pillar (the same scored-vs-diagnostic line the
    # sibling offer-side prose keeps). Vendor-neutral throughout.
    print("test_methodology_documents_self_provisioning")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the api-auth /
    # free-trial guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Onboarding without a human", "provision its own access",
                   "provisioning the offer",
                   "whether a human must onboard the agent, not who runs the API",
                   "relabels the API", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents self-provisioning: {phrase!r}")
    # The vendor-neutral agent-onboarding vocabulary the offering signal bank anchors
    # on must appear as open conventions, never a vendor product: no signup, no human
    # account creation, provisioning its own identity, a self-provision path.
    for token in ("no signup", "no human account creation",
                  "provisions its own identity", "self-provision"):
        _check(token in collapsed, f"methodology names onboarding convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's OPPOSITE-path guard — the
    # human onboarding path, the 401 error, and the pricing sense are NOT
    # self-provisioning and must be named as what the read rejects.
    for token in ("precision-guarded", "sign up on the dashboard",
                  "No API key", "no signup fees"):
        _check(token in collapsed,
               f"methodology keeps self-provisioning precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"self-provisioning prose names no vendor/domain ({banned!r})")


def test_methodology_documents_content_provenance() -> None:
    # Cycle 120 (READOUT): the READOUT leg CLOSING the content-provenance arc opened by
    # Cycle 118 (COVERAGE — the `content-provenance` offering signal added to the
    # DIGITAL_GOOD archetype bank: the "verify + trust the deliverable" leg, the
    # authenticity mirror of `output-license`'s "rights to USE") and Cycle 119 (TRUTH —
    # the SIGNAL-level relabel-invariance guard, with a synthetic surface seating the host
    # INSIDE the provenance evidence). This is the THIRD full COVERAGE->TRUTH->READOUT arc
    # on a NON-metered_api archetype (after subscription's free-trial 114/115/116 and
    # digital_good's own output-license rights leg), and digital_good's SECOND prose leg.
    # The "verify the deliverable's provenance so an agent can trust what it obtained" leg
    # was pinned in code + tests but NEVER surfaced in prose a critic can read — a reader
    # could not learn WHY a generated deliverable that ships with embedded provenance is
    # MORE agent-completable, or how it is the authenticity mirror of owning the output.
    # The paragraph must (a) frame it as the authenticity mirror of owning the deliverable
    # — an agent can hold the render and a licence to use it yet still not prove it genuine
    # — and name the failure (a render that cannot be provenance-checked has not completed
    # the commercial job); (b) name the vendor-neutral OPEN-STANDARD provenance vocabulary
    # the offering signal anchors on as open conventions — C2PA, Content Credentials, a
    # media/output provenance manifest/metadata record; (c) keep the signal's PRECISION
    # honesty — a bare `provenance`/`credentials` word (art/wine/supply-chain provenance,
    # data provenance, login credentials, a hosted model's "watermarking for provenance"
    # feature) is not a deliverable-provenance grant and is read as no signal; (d) say
    # recognition keys on the PROVENANCE the offer grants not who grants it and is pinned
    # by an identity-relabel executable regression test; and (e) stay HONEST about scope —
    # this offering read is diagnostic, off the scoring path, not a scored pillar (the same
    # scored-vs-diagnostic line the sibling offer-side prose keeps). Vendor-neutral throughout.
    print("test_methodology_documents_content_provenance")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the output-license /
    # free-trial guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Trusting the deliverable", "authenticity mirror",
                   "provenance-aware pipeline", "not completed the commercial job",
                   "provenance the offer grants, not who grants it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents content-provenance: {phrase!r}")
    # The vendor-neutral open-standard provenance vocabulary the offering signal bank
    # anchors on must appear as open conventions, never a vendor product: the C2PA
    # standard, the Content Credentials mark, a provenance manifest / metadata record.
    for token in ("C2PA", "Content Credentials", "provenance manifest",
                  "content credentials"):
        _check(token in collapsed,
               f"methodology names provenance convention {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-word guard — a bare
    # `provenance`/`credentials` word (art/wine/supply-chain provenance, data provenance,
    # login credentials, "watermarking for provenance") is not a deliverable-provenance
    # grant and is read as no signal.
    for token in ("bare", "no signal", "supply-chain", "data provenance",
                  "watermarking for provenance"):
        _check(token in collapsed,
               f"methodology keeps content-provenance precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate"):
        _check(banned not in text,
               f"content-provenance prose names no vendor/domain ({banned!r})")


def test_methodology_documents_priced_listing() -> None:
    # Cycle 124 (READOUT): the READOUT leg CLOSING the priced-listing arc opened by
    # Cycle 122 (COVERAGE — the `priced-listing` offering signal added to the
    # PHYSICAL_GOOD archetype bank: the "understand the offer" PRICE leg, a decimal
    # amount quoted directly beside an in-stock / add-to-cart control) and Cycle 123
    # (TRUTH — the SIGNAL-level relabel-invariance guard, physical_good's FIRST relabel
    # leg, with a synthetic retail surface seating the host INSIDE the priced-listing
    # evidence). This COMPLETES the FIRST full COVERAGE->TRUTH->READOUT arc on the
    # physical_good archetype (after subscription's free-trial 114/115/116 and
    # digital_good's output-license + content-provenance 118/119/120 arcs). The
    # "read the concrete price to decide + fulfill a physical purchase" leg was pinned
    # in code + tests but NEVER surfaced in prose a critic can read — a reader could not
    # learn WHY a listing whose price is machine-legible beside its availability is MORE
    # agent-completable, or how it is the physical-good mirror of the offer-side legs on
    # the other archetypes. The paragraph must (a) frame it as finishing on the
    # physical-good side — an agent can browse a catalog, see it is in stock and has an
    # add-to-cart control, yet still not be able to DECIDE whether to buy — and name the
    # failure (a catalog whose price an agent cannot read has not completed the
    # commercial job); (b) name the vendor-neutral priced-listing SHAPE the offering
    # signal anchors on (a decimal amount adjacent to an in-stock / add-to-cart control);
    # (c) keep the signal's PRECISION honesty — a bare currency amount is no signal (a
    # metered "per API call" price, a subscription "per month" fee sit nowhere near
    # availability language), so the price must sit immediately beside the availability
    # control, and a price alone can never conjure a physical good on an API storefront
    # (it stays NA); (d) say recognition keys on the PRICE the offer lists not who lists
    # it and is pinned by an identity-relabel executable regression test; and (e) stay
    # HONEST about scope — this offering read is diagnostic, off the scoring path, not a
    # scored pillar (the same scored-vs-diagnostic line the sibling offer-side prose
    # keeps). Vendor-neutral throughout.
    print("test_methodology_documents_priced_listing")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    # Match on the whitespace-collapsed text (same technique as the content-provenance /
    # free-trial guards) so wording, not source wrapping, is what the guard pins.
    collapsed = " ".join(text.split())
    for phrase in ("Reading the price to fulfill", "physical-good",
                   "priced catalog listing", "priced-listing shape",
                   "not completed the commercial job",
                   "price the offer lists, not who lists it",
                   "relabels the storefront", "executable regression test",
                   "off the scoring path", "diagnostic"):
        _check(phrase in collapsed,
               f"methodology documents priced-listing: {phrase!r}")
    # The vendor-neutral priced-listing vocabulary the offering signal keys on: a decimal
    # amount adjacent to in-stock / add-to-cart availability language.
    for token in ("in stock", "add-to-cart", "decide", "fulfill"):
        _check(token in collapsed,
               f"methodology names priced-listing vocabulary {token!r}")
    # PRECISION honesty: the prose must preserve the signal's bare-amount guard — a bare
    # currency amount (a metered per-call price, a subscription per-month fee) sitting
    # nowhere near availability is no signal, and a price alone can never conjure a
    # physical good (it stays NA on an API storefront).
    for token in ("bare", "no signal", "per API call", "per month", "NA"):
        _check(token in collapsed,
               f"methodology keeps priced-listing precision note: {token!r}")
    # Vendor-neutral: no scored domain/product/brand named on the page.
    for banned in ("drift-flight", "driftflight", "replicate", "toscrape"):
        _check(banned not in text,
               f"priced-listing prose names no vendor/domain ({banned!r})")


def test_methodology_documents_calibration() -> None:
    # Cycle 68 (READOUT): the READOUT complement to Cycle 67's calibration guard
    # (tests/test_calibration.py — the first static-vs-behavioral VALIDITY axis).
    # Every prior methodology argument is internal-consistency (earned-dominance,
    # weight-robustness) or reproducibility (section 7 = reliability, "is the
    # number stable?"). None surfaces the distinct VALIDITY question Cycle 67 made
    # executable: does the static score PREDICT what a live agent experiences? The
    # page must now name, in prose a critic can read, that the static agent-native
    # payment prediction is behaviorally corroborated at the outcome checkpoints,
    # that the agreement is discriminating (real FAILs + separates tiers), the
    # honest one-domain/$0 scope, and that it is test-pinned. Vendor-neutral.
    # Cycle 72 (READOUT): the negative anchor landed (Cycle 71's two-sided
    # calibration guard — moleskine no-rails retail behaviorally FAILS the same
    # payment checkpoints the with-rails side PASSES), so the page must now surface
    # calibration as a TWO-SIDED property, not positive-only.
    print("test_methodology_documents_calibration")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_methodology_page(Path(d))).read_text()
    for phrase in ("Calibration", "valid", "astrology", "agent-native payment",
                   "machine-payable path", "behaviorally corroborated",
                   "discriminating", "separates tiers", "two-sided",
                   "no-rails retail storefront",
                   "free tier", "executable regression test"):
        _check(phrase in text, f"methodology documents calibration: {phrase!r}")
    # The two-sided claim must be explicit: prediction tracks experience both ways.
    collapsed = " ".join(text.split())
    _check("tracks the experience in" in collapsed and "both directions" in collapsed,
           "calibration states the prediction tracks experience in both directions")
    # It must frame the number-vs-experience agreement as the validity claim, and
    # state the honest scope (two-sided anchors, one storefront per direction, $0).
    _check("predict" in text, "calibration framed as prediction/validity")
    _check("$0 free" in text, "calibration scope bounded to the $0 free tier")
    # The negative direction must be behaviorally CONFIRMED, not merely a stalled
    # prediction: a legible FAIL (evidence of absence), not an untestable blank.
    _check("legible, not a blank" in text,
           "negative calibration failure framed as legible evidence, not a null")
    # The old positive-only honest limit must be GONE (the mirror case now runs).
    _check("one with-rails storefront" not in collapsed,
           "stale positive-only anchor claim removed")
    _check("not yet run end-to-end" not in collapsed,
           "stale 'mirror case not yet run' claim removed")
    # Vendor-neutral: no domain/product/brand named on the page.
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


# ---------------------------------------------------------------------------
# Cycle 76 (READOUT): the calibration LEADERBOARD page. A benchmark needs a
# population, not one pair — the local runner commits a dated static $0 sweep of
# real domains; `_write_calibration_page` renders the newest committed dataset as
# a ranked leaderboard. These pin the READOUT semantics (the sweep math itself is
# `experiments/calibration_sweep.py`, a [LOCAL] harness, not asserted here):
#   - scored members are ranked by overall DESC (a property of the scores);
#   - a member the crawl could not reach is NOT SCORABLE — named separately, given
#     NO rank, framed as reachability not a site failure (attribution honesty);
#   - grade bands come LIVE from load_rubric (no drift), and a dataset scored on a
#     different rubric version is flagged (comparability only within a version);
#   - an absent/empty dataset renders an honest "no population yet" card;
#   - vendor-neutral: domains appear only as DATA, never in scored-check prose.

def _fake_sweep() -> dict:
    """A synthetic sweep with a deliberate NON-leaderboard row order (so a passing
    ranking test proves the page re-sorts, not that it echoes input order) plus a
    not-scorable member — the shapes `_write_calibration_page` must handle."""
    return {
        "ts": "20260728T234815Z",
        "kind": "calibration-sweep",
        "rubric_version": "0.7",
        "n_total": 4, "n_scored": 3, "n_not_scorable": 1, "n_error": 0,
        "rows": [
            {"domain": "low-store.test", "segment": "control:non-storefront",
             "scored": True, "overall": 22.5, "grade": "F",
             "pillars": {"access": 100.0, "legibility": 40.0, "transactability": 0.0,
                         "trust": 30.0, "outcome": None},
             "claimed_archetypes": [], "error": None},
            {"domain": "rails-store.test", "segment": "api-storefront:rails-anchor",
             "scored": True, "overall": 85.5, "grade": "B",
             "pillars": {"access": 100.0, "legibility": 90.9, "transactability": 87.5,
                         "trust": 60.0, "outcome": None},
             "claimed_archetypes": ["metered_api", "digital_good", "subscription"],
             "error": None},
            {"domain": "blocked-store.test", "segment": "retail:no-rails",
             "scored": False, "overall": None, "grade": "N/A",
             "pillars": None, "claimed_archetypes": [], "error": None},
            {"domain": "mid-store.test", "segment": "retail:emerging-rails",
             "scored": True, "overall": 61.9, "grade": "D",
             "pillars": {"access": 100.0, "legibility": 72.0, "transactability": 40.0,
                         "trust": 55.0, "outcome": None},
             "claimed_archetypes": ["physical_good"], "error": None},
        ],
    }


def test_calibration_page_ranks_scored_by_overall() -> None:
    print("test_calibration_page_ranks_scored_by_overall")
    with tempfile.TemporaryDirectory() as d:
        path = scorecard._write_calibration_page(Path(d), sweep=_fake_sweep())
        _check(Path(path).name == "calibration.html", "writes calibration.html")
        text = Path(path).read_text()
    _check("Calibration leaderboard" in text, "titled as the calibration leaderboard")
    # Ranked by overall DESC despite the input row order being low/high/blocked/mid.
    i_hi, i_mid, i_lo = (text.index("rails-store.test"),
                         text.index("mid-store.test"), text.index("low-store.test"))
    _check(i_hi < i_mid < i_lo, "scored rows ranked by overall descending (85.5>61.9>22.5)")
    # The top row carries its overall, grade, a pillar value and its claimed archetypes.
    _check("85.5" in text and "metered_api" in text,
           "top scored row shows overall + claimed archetypes")
    _check("3 scored" in text, "leaderboard names how many scored members it ranks")


def test_calibration_ranking_is_permutation_invariant() -> None:
    # Cycle 77 (METHOD): a readiness RANKING is a property of the scores, not of the
    # order the sweep happened to record its rows in — the READOUT analog of the
    # battery aggregation's presentation-order invariance (Cycle 73). The page's own
    # comment claims the ranking is "reproducible from the raw data"; this pins it as
    # an executable invariant, INCLUDING the tie case a plain stable sort would leak:
    # two members with the SAME overall must rank deterministically (by domain), not
    # echo whichever arrived first in `rows`.
    print("test_calibration_ranking_is_permutation_invariant")

    def _sweep(order):
        # Two GENUINELY TIED members (both 61.9) plus a clear top and a not-scorable
        # member — the tie is the load-bearing case: a stable sort on overall alone
        # would order the tied pair by input position, so the ranking would depend on
        # `order`. `by[d]` is rebuilt per call so no dict is shared across renders.
        by = {
            "top.test": {"domain": "top.test", "segment": "s", "scored": True,
                         "overall": 85.0, "grade": "B",
                         "pillars": {"access": 100.0, "legibility": 90.0,
                                     "transactability": 87.0, "trust": 60.0, "outcome": None},
                         "claimed_archetypes": [], "error": None},
            "aaa.test": {"domain": "aaa.test", "segment": "s", "scored": True,
                         "overall": 61.9, "grade": "D",
                         "pillars": {"access": 100.0, "legibility": 70.0,
                                     "transactability": 40.0, "trust": 55.0, "outcome": None},
                         "claimed_archetypes": [], "error": None},
            "zzz.test": {"domain": "zzz.test", "segment": "s", "scored": True,
                         "overall": 61.9, "grade": "D",
                         "pillars": {"access": 100.0, "legibility": 70.0,
                                     "transactability": 40.0, "trust": 55.0, "outcome": None},
                         "claimed_archetypes": [], "error": None},
            "gone.test": {"domain": "gone.test", "segment": "s", "scored": False,
                          "overall": None, "grade": "N/A", "pillars": None,
                          "claimed_archetypes": [], "error": None},
        }
        return {"ts": "20260728T000000Z", "rubric_version": "0.7",
                "rows": [by[d] for d in order]}

    scored_doms = ["top.test", "aaa.test", "zzz.test"]

    def _ranked(order):
        with tempfile.TemporaryDirectory() as d:
            text = Path(scorecard._write_calibration_page(Path(d), sweep=_sweep(order))).read_text()
        # The ranked order is the order the scored domains appear in the rendered page.
        return sorted(scored_doms, key=lambda x: text.index(x))

    # Several genuinely-different input row orders, including the tie pair swapped.
    orders = [
        ["top.test", "aaa.test", "zzz.test", "gone.test"],
        ["zzz.test", "aaa.test", "gone.test", "top.test"],  # tied pair swapped
        ["gone.test", "zzz.test", "top.test", "aaa.test"],
        ["aaa.test", "gone.test", "zzz.test", "top.test"],
    ]
    # Non-vacuity: the input orders really do differ (so a PASS is not because we fed
    # identical inputs), and at least one swaps the tied pair's arrival order.
    _check(len({tuple(o) for o in orders}) == len(orders),
           "the permutation inputs are genuinely distinct row orders")

    rankings = [_ranked(o) for o in orders]
    first = rankings[0]
    _check(all(r == first for r in rankings),
           f"ranking is identical under every row permutation, got {rankings}")
    # And it is the CORRECT deterministic ranking: top by overall, tie broken by
    # domain ASC (aaa before zzz) — a property of the data, not the input order.
    _check(first == ["top.test", "aaa.test", "zzz.test"],
           f"tie broken deterministically by domain (overall DESC, domain ASC), got {first}")


def test_calibration_page_separates_not_scorable() -> None:
    # Attribution honesty (invariant #4): an unreachable member is NEVER in the
    # ranking and NEVER gets a rank number — it is named in its own section as a
    # reachability fact, not a site failure.
    print("test_calibration_page_separates_not_scorable")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_calibration_page(Path(d), sweep=_fake_sweep())).read_text()
    _check("Not scorable" in text, "a separate Not-scorable section exists")
    ns_idx = text.index("Not scorable")
    # The blocked domain appears ONLY after the Not-scorable header, i.e. not in the
    # ranked leaderboard table above it.
    _check(text.index("blocked-store.test") > ns_idx,
           "the unreachable member is listed under Not scorable, not in the ranking")
    _check("reachability" in text and "not a site" in text,
           "framed as reachability, not a site failure")


def test_calibration_page_bands_live_and_version_flagged() -> None:
    # Grade bands are pulled LIVE from the rubric (no-drift), and a dataset scored on
    # a DIFFERENT rubric version than the current one is flagged for comparability.
    print("test_calibration_page_bands_live_and_version_flagged")
    from asrs.scoring import load_rubric
    live_version = str(load_rubric().get("version", ""))
    # Same-version dataset: no version-mismatch note.
    same = _fake_sweep()
    same["rubric_version"] = live_version
    with tempfile.TemporaryDirectory() as d:
        text_same = Path(scorecard._write_calibration_page(Path(d), sweep=same)).read_text()
    _check(f"live from rubric\nv{live_version}" in text_same
           or f"live from rubric v{live_version}" in text_same,
           "grade-band legend names the live rubric version")
    _check("Version note" not in text_same, "no version note when dataset matches live rubric")
    # Mismatched-version dataset: the comparability note fires.
    stale = _fake_sweep()
    stale["rubric_version"] = "0.001"
    with tempfile.TemporaryDirectory() as d:
        text_stale = Path(scorecard._write_calibration_page(Path(d), sweep=stale)).read_text()
    _check("Version note" in text_stale and "0.001" in text_stale,
           "a dataset on a different rubric version is flagged")


def test_calibration_page_empty_renders_gracefully() -> None:
    # No committed dataset -> an honest "no population yet" card, never a crash or a
    # fabricated empty ranking.
    print("test_calibration_page_empty_renders_gracefully")
    with tempfile.TemporaryDirectory() as d:
        text = Path(scorecard._write_calibration_page(Path(d), sweep={"rows": []})).read_text()
    _check("No population sweep yet" in text, "empty dataset -> honest no-data card")
    _check("Not scorable" not in text, "no not-scorable section when there is no data")


def test_calibration_page_published_and_linked() -> None:
    # build_scorecard publishes calibration.html next to the card and the footer
    # links to it — alongside the three existing prose pages (unchanged).
    print("test_calibration_page_published_and_linked")
    rep = _report([])
    with tempfile.TemporaryDirectory() as d:
        rp = Path(d) / "rep.json"
        rp.write_text(rep.to_json())
        out = scorecard.build_scorecard([str(rp)], out_path=str(Path(d) / "card.html"))
        _check((Path(d) / "calibration.html").exists(),
               "calibration.html published next to the card")
        _check((Path(d) / "canonical-history.html").exists(),
               "canonical-history.html still published (unchanged)")
        _check((Path(d) / "methodology.html").exists(), "methodology.html still published")
        _check('href="calibration.html"' in Path(out).read_text(),
               "the card footer links to calibration.html")


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
        test_methodology_documents_check_layer_honesty,
        test_methodology_documents_payment_rail_neutrality,
        test_methodology_documents_async_job_contract,
        test_methodology_documents_api_auth_scheme,
        test_methodology_documents_error_contract,
        test_methodology_documents_offering_relative_battery,
        test_methodology_documents_output_license,
        test_methodology_documents_test_mode,
        test_methodology_documents_pagination,
        test_methodology_documents_cancel_job,
        test_methodology_documents_streaming_response,
        test_methodology_documents_webhook_verification,
        test_methodology_documents_output_resolution,
        test_methodology_documents_payment_receipt,
        test_methodology_documents_failure_not_billed,
        test_methodology_documents_reserve_and_settle,
        test_methodology_documents_plan_purchase,
        test_methodology_documents_free_trial,
        test_methodology_documents_self_provisioning,
        test_methodology_documents_content_provenance,
        test_methodology_documents_priced_listing,
        test_methodology_documents_calibration,
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
        test_calibration_page_ranks_scored_by_overall,
        test_calibration_ranking_is_permutation_invariant,
        test_calibration_page_separates_not_scorable,
        test_calibration_page_bands_live_and_version_flagged,
        test_calibration_page_empty_renders_gracefully,
        test_calibration_page_published_and_linked,
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
