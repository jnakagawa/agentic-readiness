"""Tests for the canonical-delta HISTORY readout (asrs/canonical_history.py).

Runnable directly, no pytest required:

    python tests/test_canonical_history.py

The local runner commits ``runs/local/verify_<ts>.json`` every fire — a live
static re-score of the reference pair. ``canonical_history`` reads that committed
series and surfaces the delta TREND + a sustained-drift alert vs the committed-
fixture baseline the in-cloud replay guard pins (+39.4). These tests pin:

  - the loader parses a well-formed artifact and SKIPS malformed ones (the early
    pre-Cycle-13 FileNotFoundError artifacts, and any run where a domain isn't
    ``ok``) — attribution honesty: an unobserved re-score is not a data point;
  - the drift bands + the sustained-out-of-band counter (1 reading is jitter, a
    trailing RUN is a real move) behave as documented;
  - the render block is substantive and never crashes on an empty series;
  - the baseline constant CANNOT silently drift from what the replay guard pins
    (cross-checked against ``test_canonical_replay.EXPECTED_DELTA``);
  - it runs against the REAL committed series and produces a coherent summary.

Read-only diagnostic: no scoring code is imported by the module, no score moves.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import canonical_history as ch  # noqa: E402

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _artifact(
    ts: str,
    org: float,
    com: float,
    delta,
    ok: bool = True,
    org_pillars: dict | None = None,
    com_pillars: dict | None = None,
) -> dict:
    def side(overall, grade, pillars):
        s = {"ok": ok, "overall": overall, "grade": grade, "scored": True}
        if pillars is not None:
            s["pillars"] = pillars
        return s
    return {
        "ts": ts,
        "kind": "local-verify",
        "tests_ok": True,
        "scores": {
            ch.CANONICAL_NO_RAILS: side(org, "F", org_pillars),
            ch.CANONICAL_WITH_RAILS: side(com, "B", com_pillars),
        },
        "delta": delta,
    }


def _write_series(tmp: str, rows: list[dict]) -> None:
    for i, obj in enumerate(rows):
        ts = obj.get("ts", f"20260727T{i:02d}0000Z")
        with open(os.path.join(tmp, f"verify_{ts}.json"), "w", encoding="utf-8") as fh:
            json.dump(obj, fh)


def _reflect_about_anchor(rows: list[dict]) -> list[dict]:
    """Reflect a whole series' two overall scores about the FIRST row's overalls.

    Each side ``v`` maps to ``2*anchor - v`` (a point reflection about the anchor,
    per side), so a move of ``+x`` on a side becomes ``-x`` and the delta reflects
    about the anchor gap: ``delta = with - no`` -> ``2*(anchor_with - anchor_no) -
    delta``. Because the anchor is the in-band baseline reading, this reflects each
    reading's divergence about the pinned baseline with its SIGN flipped and its
    MAGNITUDE preserved — the canonical metamorphic transform for testing that the
    drift diagnostics' magnitude machinery is direction-blind while their direction
    machinery is direction-sensitive. Timestamps and grades are carried through
    unchanged (only the numeric trajectory is reflected)."""
    a_no = rows[0]["scores"][ch.CANONICAL_NO_RAILS]["overall"]
    a_with = rows[0]["scores"][ch.CANONICAL_WITH_RAILS]["overall"]
    out: list[dict] = []
    for r in rows:
        no = r["scores"][ch.CANONICAL_NO_RAILS]["overall"]
        wi = r["scores"][ch.CANONICAL_WITH_RAILS]["overall"]
        r_no = round(2 * a_no - no, 4)
        r_wi = round(2 * a_with - wi, 4)
        out.append(_artifact(r["ts"], r_no, r_wi, round(r_wi - r_no, 4)))
    return out


def test_loader_parses_and_skips_malformed() -> None:
    print("test_loader_parses_and_skips_malformed")
    with tempfile.TemporaryDirectory() as tmp:
        good = _artifact("20260727T010000Z", 46.1, 85.5, 39.4)
        # early FileNotFoundError-style artifact: no top-level delta, ok False
        legacy = {
            "ts": "20260723T040714Z",
            "scores": {
                ch.CANONICAL_NO_RAILS: {"ok": False, "error": "FileNotFoundError"},
                ch.CANONICAL_WITH_RAILS: {"ok": False, "error": "FileNotFoundError"},
            },
        }
        # well-formed-looking but a domain didn't score ok -> skip
        half = _artifact("20260727T020000Z", 46.1, 85.5, 39.4)
        half["scores"][ch.CANONICAL_WITH_RAILS]["ok"] = False
        _write_series(tmp, [good, legacy, half])
        pts = ch.load_points(tmp)
        _check(len(pts) == 1, f"only the one usable artifact loads, got {len(pts)}")
        _check(pts[0].ts == "20260727T010000Z", "the usable point is the good one")
        _check(pts[0].delta == 39.4, f"delta parsed, got {pts[0].delta}")
        _check(pts[0].with_rails_overall == 85.5, "with-rails overall parsed")


def test_bands_and_in_band_series() -> None:
    print("test_bands_and_in_band_series")
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4),
            _artifact("20260727T020000Z", 46.1, 85.0, 38.9),  # within jitter
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.band == ch.BAND_IN, f"tiny move stays in-band, got {hist.band}")
        _check(
            hist.consecutive_out_of_band == 0,
            f"nothing out of band, got {hist.consecutive_out_of_band}",
        )
        _check(abs(hist.divergence - (-0.5)) < 1e-9, f"divergence -0.5, got {hist.divergence}")


def test_sustained_drift_counts_trailing_run() -> None:
    print("test_sustained_drift_counts_trailing_run")
    with tempfile.TemporaryDirectory() as tmp:
        # a long in-band history, then three consecutive out-of-band re-scores
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 50.0, 3.9),   # diverged
            _artifact("20260727T060000Z", 46.1, 76.2, 30.1),  # diverged
            _artifact("20260727T070000Z", 46.1, 78.7, 32.6),  # drifting
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.latest.delta == 32.6, "latest is the most recent by ts")
        _check(hist.band == ch.BAND_DRIFTING, f"latest -6.8 is drifting, got {hist.band}")
        _check(
            hist.consecutive_out_of_band == 3,
            f"three trailing out-of-band readings, got {hist.consecutive_out_of_band}",
        )
        # a single blip on an otherwise in-band tail counts as 1 (jitter, not sustained)
        rows2 = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows2.append(_artifact("20260727T050000Z", 46.1, 60.0, 13.9))
        rows2.append(_artifact("20260727T060000Z", 46.1, 85.5, 39.4))  # back in band
        with tempfile.TemporaryDirectory() as tmp2:
            _write_series(tmp2, rows2)
            h2 = ch.load_history(tmp2)
            _check(
                h2.consecutive_out_of_band == 0,
                f"a recovered tail resets the run to 0, got {h2.consecutive_out_of_band}",
            )


def test_sustained_run_spans_wall_clock() -> None:
    print("test_sustained_run_spans_wall_clock")
    # The DURATION behind the count: a trailing out-of-band run of 3 readings taken
    # over a real wall-clock span reports that span (first-run-reading -> latest), not
    # just the reading count. This is what separates a durable real-world move from a
    # burst of rapid re-scores that happen to be out of band.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260731T080000Z", 46.1, 76.2, 30.1),  # first out-of-band
            _artifact("20260731T140000Z", 46.1, 76.2, 30.1),
            _artifact("20260801T020000Z", 46.1, 76.2, 30.1),  # latest, 18h later
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        sr = hist.sustained_run
        _check(sr is not None, "an out-of-band run has a measured span")
        _check(sr.n == hist.consecutive_out_of_band == 3, f"n mirrors the count, got {sr.n}")
        _check(sr.first_ts == "20260731T080000Z", f"span starts at the first run reading, got {sr.first_ts}")
        _check(sr.latest_ts == "20260801T020000Z", f"span ends at the latest, got {sr.latest_ts}")
        _check(abs(sr.span_hours - 18.0) < 1e-6, f"first->latest is 18h, got {sr.span_hours}")
        _check("spanning 18.0h" in ch.render(hist), "render names the wall-clock span")


def test_sustained_run_none_when_in_band() -> None:
    print("test_sustained_run_none_when_in_band")
    # In-band series -> no out-of-band run -> no span (honest None, not a 0h claim).
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 4)])
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 0, "nothing out of band")
        _check(hist.sustained_run is None, "in-band -> no sustained-run span")
        _check("spanning" not in ch.render(hist), "render omits the span line when in-band")


def test_sustained_run_lone_reading_is_zero_span() -> None:
    print("test_sustained_run_lone_reading_is_zero_span")
    # A single trailing out-of-band reading spans 0h — a real fact: one reading has no
    # persistence in time, so it is the weakest possible "recent" signal, matching the
    # not-yet-sustained (< _SUSTAINED_MIN) count verdict from the other direction.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 4)]
        rows.append(_artifact("20260727T050000Z", 46.1, 60.0, 13.9))  # lone diverged tail
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 1, "one trailing out-of-band reading")
        sr = hist.sustained_run
        _check(sr is not None and sr.n == 1, "a lone reading still has a (degenerate) run")
        _check(sr.span_hours == 0.0, f"a single reading spans 0h, got {sr.span_hours}")
        _check(sr.first_ts == sr.latest_ts, "its endpoints coincide")


def test_sustained_run_none_on_unparseable_ts() -> None:
    print("test_sustained_run_none_on_unparseable_ts")
    # Honest-None: an unparseable endpoint timestamp yields no duration claim (the same
    # discipline liveness follows). Exercised directly on the pure function.
    good = ch.CanonicalPoint(
        ts="20260731T080000Z", no_rails_overall=46.1, no_rails_grade="F",
        with_rails_overall=76.2, with_rails_grade="C", delta=30.1,
    )
    bad = ch.CanonicalPoint(
        ts="not-a-timestamp", no_rails_overall=46.1, no_rails_grade="F",
        with_rails_overall=76.2, with_rails_grade="C", delta=30.1,
    )
    _check(ch.sustained_run([good, bad], 2) is None, "unparseable latest ts -> None")
    _check(ch.sustained_run([bad, good], 2) is None, "unparseable first-of-run ts -> None")
    _check(ch.sustained_run([good], 0) is None, "run < 1 -> None (in-band)")


def test_sustained_run_on_real_series_is_coherent() -> None:
    print("test_sustained_run_on_real_series_is_coherent")
    # End-to-end on the REAL committed series, recovery-tolerant: whenever the live
    # series is out of band, the span is present, non-negative, its n mirrors the
    # count, and the render surfaces it; when in-band, both are absent. Ties the new
    # measure to the same live-vs-recovered dichotomy the recapture test uses.
    hist = ch.load_history()
    if hist.consecutive_out_of_band >= 1:
        sr = hist.sustained_run
        _check(sr is not None, "an out-of-band real series has a measured span")
        _check(sr.n == hist.consecutive_out_of_band, f"n mirrors the count, got {sr.n}")
        _check(sr.span_hours >= 0.0, f"span is non-negative, got {sr.span_hours}")
        _check("spanning" in ch.render(hist), "the real render carries the span")
    else:
        _check(hist.sustained_run is None, "an in-band real series has no span")


def test_render_substantive_and_empty_safe() -> None:
    print("test_render_substantive_and_empty_safe")
    empty = ch.render(ch.summarize([]))
    _check("CANONICAL DELTA HISTORY" in empty, "empty render still has a header")
    _check("no usable" in empty.lower(), "empty render says so, does not crash")
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4),
            _artifact("20260727T070000Z", 46.1, 78.7, 32.6),
        ])
        out = ch.render(ch.load_history(tmp))
        for token in ("baseline", "latest", "divergence", "delta trend"):
            _check(token in out, f"render names '{token}'")
        _check(ch.CANONICAL_WITH_RAILS in out, "render shows the reference pair")


def test_baseline_cannot_drift_from_replay_guard() -> None:
    print("test_baseline_cannot_drift_from_replay_guard")
    # Single source of truth: the history baseline MUST equal what the in-cloud
    # canonical replay guard pins. If a version bump legitimately re-captures the
    # fixtures and moves the delta, test_canonical_replay.EXPECTED_DELTA changes
    # and this goes red — the intended tripwire, not a regression.
    sys.path.insert(0, os.path.join(_REPO, "tests"))
    import test_canonical_replay as replay  # noqa: E402
    _check(
        ch.FIXTURE_BASELINE_DELTA == replay.EXPECTED_DELTA,
        f"baseline {ch.FIXTURE_BASELINE_DELTA} == replay guard {replay.EXPECTED_DELTA}",
    )


def _com_pillars(legibility, transactability=87.5):
    # a full driftflight.com pillar block; access/trust flat, outcome unobserved
    return {
        "access": 100.0,
        "legibility": legibility,
        "transactability": transactability,
        "trust": 60.0,
        "outcome": None,
    }


def _org_pillars():
    # drift-flight.org stays flat at 46.1 F throughout the live drift
    return {
        "access": 100.0,
        "legibility": 36.36363636363637,
        "transactability": 18.75,
        "trust": 60.0,
        "outcome": None,
    }


def test_attribution_names_the_moving_pillar() -> None:
    print("test_attribution_names_the_moving_pillar")
    # Mirror the real 2026-07-27 live drift: .org flat, .com legibility collapses
    # 90.9 -> 63.6 while transactability holds -> the delta narrows and the pillar
    # attribution must finger .com legibility, not the flat pillars.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9090909090909))
            for i in range(1, 5)
        ]
        rows.append(
            _artifact("20260727T130000Z", 46.1, 78.7, 32.6,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(63.63636363636363))
        )
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        attr = hist.attribution
        _check(attr is not None, "an out-of-band latest with an in-band anchor gets attribution")
        _check(attr.anchor_ts == "20260727T040000Z", f"anchor is the last in-band reading, got {attr.anchor_ts}")
        top = attr.top
        _check(top is not None, "there is a top mover")
        _check(top.domain == ch.CANONICAL_WITH_RAILS, f"the mover is the with-rails side, got {top.domain}")
        _check(top.pillar == "legibility", f"the mover is legibility, got {top.pillar}")
        _check(abs(top.change - (-27.27)) < 0.01, f"change is 90.9->63.6 = -27.27, got {top.change}")
        # non-vacuous: the FLAT pillars are NOT reported as movers
        moved = {(m.domain, m.pillar) for m in attr.moves}
        _check((ch.CANONICAL_WITH_RAILS, "transactability") not in moved, "flat .com transactability is not a mover")
        _check((ch.CANONICAL_NO_RAILS, "legibility") not in moved, "flat .org legibility is not a mover")
        out = ch.render(hist)
        _check("attribution" in out, "the render names the attribution")
        _check("legibility" in out, "the render names the moving pillar")


def test_attribution_none_when_in_band() -> None:
    print("test_attribution_none_when_in_band")
    # nothing has drifted -> nothing to attribute (honest None, not a fabricated move)
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9090909090909)),
            _artifact("20260727T020000Z", 46.1, 85.0, 38.9,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9090909090909)),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.band == ch.BAND_IN, "series is in-band")
        _check(hist.attribution is None, "in-band series has no attribution")
        _check("attribution" not in ch.render(hist), "render omits attribution when in-band")


def test_attribution_skips_unobserved_pillar_and_needs_an_anchor() -> None:
    print("test_attribution_skips_unobserved_pillar_and_needs_an_anchor")
    # (a) latest legibility unobserved (None, an error crawl) -> legibility is NOT
    # attributed a move; the next-largest OBSERVED mover (transactability) wins.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9090909090909, 87.5))
            for i in range(1, 5)
        ]
        # latest: legibility None (unobserved), transactability dropped 87.5 -> 50.0
        rows.append(
            _artifact("20260727T130000Z", 46.1, 70.0, 23.9,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(None, 50.0))
        )
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        attr = hist.attribution
        _check(attr is not None, "out-of-band with anchor -> attribution")
        moved = {(m.domain, m.pillar) for m in attr.moves}
        _check((ch.CANONICAL_WITH_RAILS, "legibility") not in moved, "unobserved legibility is not attributed a move")
        _check(attr.top.pillar == "transactability", f"the observed mover wins, got {attr.top.pillar}")
    # (b) the ENTIRE series is out of band -> no in-band anchor observed -> honest None
    with tempfile.TemporaryDirectory() as tmp2:
        rows2 = [
            _artifact("20260727T010000Z", 46.1, 60.0, 13.9,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(70.0)),
            _artifact("20260727T020000Z", 46.1, 65.0, 18.9,
                      org_pillars=_org_pillars(), com_pillars=_com_pillars(75.0)),
        ]
        _write_series(tmp2, rows2)
        h2 = ch.load_history(tmp2)
        _check(h2.consecutive_out_of_band == 2, "both readings out of band")
        _check(h2.attribution is None, "no in-band anchor in the series -> no attribution claim")


def test_attribution_on_real_series_fingers_the_drifting_pillar() -> None:
    print("test_attribution_on_real_series_fingers_the_drifting_pillar")
    # Non-vacuous end-to-end: the REAL committed series' current drift must
    # attribute to a SPECIFIC pillar on the with-rails reference (COMPUTED from the
    # committed verify_*.json series, not hand-written). The live drift's pillar has
    # MOVED over the loop's lifetime — it was driftflight.com LEGIBILITY during the
    # 2026-07-27 episode and is driftflight.com TRANSACTABILITY now (87.5 -> 62.5,
    # the persistent Jul-31/Aug-1 machine-payment softening tracked in STATE/BACKLOG)
    # — so this guard pins the pillar the CURRENT series fingers, not a frozen name.
    # Guarded for recovery: if the site returns to in-band, attribution is correctly
    # None and the claim is skipped. Two independent mechanisms must AGREE here — the
    # per-pillar _attribute() and the side-level _cause() — a cross-check neither
    # test alone makes.
    hist = ch.load_history()
    if hist.band == ch.BAND_IN or hist.attribution is None:
        _check(True, "live series is in-band -> no attribution to check (site recovered)")
        return
    top = hist.attribution.top
    _check(top is not None, "the drifting real series isolates a top mover")
    _check(
        top.domain == ch.CANONICAL_WITH_RAILS,
        f"the real drift is on the with-rails side, got {top.domain}",
    )
    # Cross-mechanism agreement: the pillar-level attribution and the side-level
    # divergence cause are computed independently (different code paths, one on
    # per-pillar scores, one on overalls) — on the real series they must finger the
    # SAME side, or one of them is lying about what moved.
    cause = hist.divergence_cause
    _check(cause is not None, "an out-of-band real series with an anchor has a cause")
    _check(
        top.domain == cause.driver,
        f"pillar attribution ({top.domain}) and side cause ({cause.driver}) must agree",
    )
    # Direction consistency: when the with-rails reference is what SOFTENED
    # (reference_degraded), the fingered pillar's own move must be a DROP — a
    # degradation cannot be carried by a pillar that rose.
    if cause.reference_degraded:
        _check(
            top.change < 0,
            f"a reference softening must be a pillar DROP, got {top.change:+}",
        )
    # The specific pillar the CURRENT live drift fingers. If this reddens, the real
    # site drifted to a DIFFERENT pillar than transactability — read the newest
    # runs/local/verify_*.json, confirm which pillar moved, and update this name
    # (the same "executable evidence tracks reality" discipline as the family).
    _check(
        top.pillar == "transactability",
        f"the current live drift is on transactability, got {top.pillar}",
    )


# Anchor pillars shared by the synthetic stability series below: the canonical
# pre-drift shape (no-rails floor low, with-rails reference high on every pillar).
_ANCHOR_ORG_PILLARS = {
    "access": 100.0, "legibility": 36.4, "transactability": 18.8, "trust": 60.0,
}
_ANCHOR_COM_PILLARS = {
    "access": 100.0, "legibility": 90.9, "transactability": 87.5, "trust": 60.0,
}


def test_attribution_stability_catches_a_wandering_mover() -> None:
    print("test_attribution_stability_catches_a_wandering_mover")
    # Teeth: a trailing out-of-band run of TWO readings whose top mover FLIPS — the
    # first reading fingers .com legibility, the second .com transactability. The
    # single-snapshot attribution would report only the latest (transactability) and
    # look identical to a sustained move; stability must catch that the fingered
    # pillar WANDERED, so the attribution is not a sustained real-world site move.
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [
            # anchor: in-band (delta 39.4 == baseline)
            _artifact("20260727T000000Z", 46.1, 85.5, 39.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars=dict(_ANCHOR_COM_PILLARS)),
            # reading 1: .com legibility 90.9 -> 70.9 (-20), out of band (delta 32.4)
            _artifact("20260727T010000Z", 46.1, 78.5, 32.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "legibility": 70.9}),
            # reading 2: .com transactability 87.5 -> 62.5 (-25), legibility RESTORED,
            # out of band (delta 30.1) -> tops a DIFFERENT pillar than reading 1
            _artifact("20260727T020000Z", 46.1, 76.2, 30.1,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 62.5}),
        ])
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 2, "the trailing run is 2 out-of-band readings")
        stab = hist.attribution_stability
        _check(stab is not None, "a 2-reading out-of-band run gets a stability measure")
        _check(stab.anchor_ts == "20260727T000000Z", "stability anchors on the last in-band reading")
        _check(len(stab.readings) == 2, "one ReadingTop per out-of-band reading")
        _check(
            stab.movers == {(ch.CANONICAL_WITH_RAILS, "legibility"),
                            (ch.CANONICAL_WITH_RAILS, "transactability")},
            f"the two readings finger DIFFERENT pillars, got {stab.movers}",
        )
        _check(stab.stable is False, "a wandering top mover is NOT stable")
        _check(stab.fingered is None, "a wandering run has no single fingered pillar")
        out = ch.render(hist)
        _check("attribution stability" in out and "WANDERS" in out, "render names the wander")


def test_attribution_stability_stable_when_pillar_holds() -> None:
    print("test_attribution_stability_stable_when_pillar_holds")
    # Positive: a trailing out-of-band run of TWO readings that BOTH finger the same
    # pillar (.com transactability, first -17.5 then -25.0 — magnitude may differ, the
    # fingered pillar must hold). This is the shape of the REAL current drift; the
    # synthetic version pins it deterministically so the property has a green witness
    # independent of whether the live site has recovered.
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [
            _artifact("20260727T000000Z", 46.1, 85.5, 39.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars=dict(_ANCHOR_COM_PILLARS)),
            # reading 1: transactability 87.5 -> 70.0 (-17.5), out of band (delta 33.9)
            _artifact("20260727T010000Z", 46.1, 80.0, 33.9,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 70.0}),
            # reading 2: transactability 87.5 -> 62.5 (-25.0), out of band (delta 30.1)
            _artifact("20260727T020000Z", 46.1, 76.2, 30.1,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 62.5}),
        ])
        hist = ch.load_history(tmp)
        stab = hist.attribution_stability
        _check(stab is not None, "a 2-reading out-of-band run gets a stability measure")
        _check(stab.stable is True, "both readings fingering one pillar is STABLE")
        _check(
            stab.fingered == (ch.CANONICAL_WITH_RAILS, "transactability"),
            f"the fingered pillar is the shared mover, got {stab.fingered}",
        )
        _check(len(stab.movers) == 1, "a stable run has exactly one distinct mover")
        _check("STABLE, not wandering" in ch.render(hist), "render names the stable pillar")


def test_attribution_stability_none_when_short_or_no_anchor() -> None:
    print("test_attribution_stability_none_when_short_or_no_anchor")
    # (a) a LONE out-of-band reading is not a stability question — one reading cannot
    # wander. Honest None, not a fabricated "stable".
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [
            _artifact("20260727T000000Z", 46.1, 85.5, 39.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars=dict(_ANCHOR_COM_PILLARS)),
            _artifact("20260727T010000Z", 46.1, 76.2, 30.1,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 62.5}),
        ])
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 1, "the trailing run is a single out-of-band reading")
        _check(hist.attribution_stability is None, "a lone out-of-band reading -> no stability claim")
    # (b) an ALL-out-of-band series has no in-band anchor to attribute against —
    # honest None, the same discipline _attribute applies (no observed stable baseline).
    with tempfile.TemporaryDirectory() as tmp2:
        _write_series(tmp2, [
            _artifact("20260727T000000Z", 46.1, 78.5, 32.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "legibility": 70.9}),
            _artifact("20260727T010000Z", 46.1, 76.2, 30.1,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 62.5}),
        ])
        h2 = ch.load_history(tmp2)
        _check(h2.consecutive_out_of_band == 2, "both readings are out of band")
        _check(h2.attribution_stability is None, "no in-band anchor in the series -> no stability claim")


def test_attribution_stability_on_real_series_holds_the_pillar() -> None:
    print("test_attribution_stability_on_real_series_holds_the_pillar")
    # Non-vacuous end-to-end on the REAL committed series: the current transactability
    # drift is fingered by the LATEST reading (the sibling _fingers_the_drifting_pillar
    # guard) — but is it fingered by EVERY out-of-band reading, or only the latest? This
    # pins that the fingered pillar is STABLE across the whole trailing out-of-band run,
    # turning the single-snapshot claim into a sustained-move claim. Guarded three ways:
    # if the site recovered (in-band) OR the run is a single reading (< 2, no wander
    # question) OR no anchor exists, stability is correctly None and the claim is skipped.
    # If this reddens with stability NOT None and NOT stable, the real fingered pillar
    # WANDERED between readings — read the newest runs/local/verify_*.json, confirm which
    # pillars moved, and reconcile (the same "executable evidence tracks reality"
    # discipline as the attribution family).
    hist = ch.load_history()
    stab = hist.attribution_stability
    if stab is None:
        _check(True, "live run too short / recovered / no anchor -> no stability question (skip)")
        return
    _check(len(stab.readings) >= 2, "a real stability measure spans >= 2 out-of-band readings")
    _check(
        stab.stable is True,
        f"the real trailing out-of-band run fingers ONE pillar, got movers {stab.movers}",
    )
    _check(
        stab.fingered == (ch.CANONICAL_WITH_RAILS, "transactability"),
        f"the sustained real drift is with-rails transactability, got {stab.fingered}",
    )
    # Cross-check: the single-snapshot attribution top must be the SAME pillar the whole
    # run agrees on — the two computations (latest-vs-anchor and per-reading-vs-anchor)
    # must not disagree about what is drifting.
    top = hist.attribution.top if hist.attribution is not None else None
    _check(top is not None, "the drifting real series isolates a snapshot top mover")
    _check(
        (top.domain, top.pillar) == stab.fingered,
        f"snapshot top ({top.domain} {top.pillar}) must equal the sustained pillar {stab.fingered}",
    )


def test_attribution_stability_is_host_relabel_invariant() -> None:
    print("test_attribution_stability_is_host_relabel_invariant")
    # METHOD (Cycle 185): VENDOR-NEUTRALITY of the attribution-STABILITY diagnostic,
    # made executable as the metamorphic (host-relabel) invariance axis — the sibling
    # of the Cycle-181 cause_verdict guard, for the ONE drift diagnostic in the family
    # that still lacked one. attribution_stability labels each ReadingTop.top / movers
    # / fingered with PillarMove.domain, drawn from the module host constants; its
    # STABLE/WANDERS verdict and the rendered line must key ONLY on the pair's
    # STRUCTURE (which side drifts, which pillar, how many readings agree), never on
    # the literal host STRINGS. If it hardcoded "driftflight.com" the benchmark's core
    # invariant ("checks worded by capability, never by vendor") would be violated in
    # the readout. Transform: RELABEL both reference hosts to fresh, unrelated strings
    # and rebuild the SAME structural series. Invariant: the stability verdict is
    # unchanged and its rendered line is BYTE-IDENTICAL once the driver host is
    # substituted back to a neutral placeholder — a pure function of structure + token.
    def _stable_rows():
        # both out-of-band readings finger with-rails transactability (magnitudes differ)
        return [
            _artifact("20260727T000000Z", 46.1, 85.5, 39.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars=dict(_ANCHOR_COM_PILLARS)),
            _artifact("20260727T010000Z", 46.1, 80.0, 33.9,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 70.0}),
            _artifact("20260727T020000Z", 46.1, 76.2, 30.1,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 62.5}),
        ]

    def _wander_rows():
        # the two out-of-band readings finger DIFFERENT with-rails pillars
        return [
            _artifact("20260727T000000Z", 46.1, 85.5, 39.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars=dict(_ANCHOR_COM_PILLARS)),
            _artifact("20260727T010000Z", 46.1, 78.5, 32.4,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "legibility": 70.9}),
            _artifact("20260727T020000Z", 46.1, 76.2, 30.1,
                      org_pillars=dict(_ANCHOR_ORG_PILLARS),
                      com_pillars={**_ANCHOR_COM_PILLARS, "transactability": 62.5}),
        ]

    def _stab_line(hist) -> str:
        for ln in ch.render(hist).splitlines():
            if ln.startswith("attribution stability:"):
                return ln
        return ""

    orig_no, orig_with = ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS
    new_no, new_with = "no-rails-store.example", "with-rails-store.example"
    try:
        for rows_of, tag, expect_stable, expect_pillars in (
            (_stable_rows, "stable", True, {"transactability"}),
            (_wander_rows, "wander", False, {"legibility", "transactability"}),
        ):
            # (a) baseline at the REAL labels.
            with tempfile.TemporaryDirectory() as tmp:
                _write_series(tmp, rows_of())
                h1 = ch.load_history(tmp)
            s1 = h1.attribution_stability
            _check(s1 is not None, f"[{tag}] a 2-reading out-of-band run gets a stability measure")
            _check(s1.stable is expect_stable, f"[{tag}] baseline stable={expect_stable}, got {s1.stable}")
            _check({d for d, _ in s1.movers} == {orig_with},
                   f"[{tag}] baseline movers are all the real with-rails host, got {s1.movers}")
            _check({p for _, p in s1.movers} == expect_pillars,
                   f"[{tag}] baseline pillar set {expect_pillars}, got {s1.movers}")
            line1 = _stab_line(h1)
            _check(orig_with in line1, f"[{tag}] baseline render names the real driver host, got: {line1}")

            # (b) RELABEL both hosts and rebuild the SAME structural series (_artifact
            #     keys the written scores off the constants, so the new build is keyed
            #     — and loaded, attributed, rendered — entirely under the new labels).
            ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = new_no, new_with
            with tempfile.TemporaryDirectory() as tmp2:
                _write_series(tmp2, rows_of())
                h2 = ch.load_history(tmp2)
            s2 = h2.attribution_stability
            _check(s2 is not None, f"[{tag}] relabeled run still gets a stability measure")
            _check(s2.stable is expect_stable, f"[{tag}] relabel-invariant stable={expect_stable}, got {s2.stable}")

            # (c) relabel took effect — movers follow the NEW host; the pillar SET is
            #     structural, unchanged by the relabel.
            _check({d for d, _ in s2.movers} == {new_with},
                   f"[{tag}] relabel took effect — movers on the new host, got {s2.movers}")
            _check({p for _, p in s2.movers} == expect_pillars,
                   f"[{tag}] pillar set is structural, unchanged by relabel, got {s2.movers}")

            # (d) teeth: the relabeled stability line leaks NEITHER original host — a
            #     diagnostic that hardcoded the real vendor domains would fail here.
            line2 = _stab_line(h2)
            _check(orig_no not in line2 and orig_with not in line2,
                   f"[{tag}] relabeled line leaks no original host, got: {line2}")

            # (e) INVARIANCE: substitute each driver host back to one placeholder — the
            #     two stability lines are byte-identical, so the verdict prose (STABLE
            #     vs WANDERS, the fingered/mover clause, the reading count) is a pure
            #     function of structure + the host token.
            _check(line1.replace(orig_with, "<HOST>") == line2.replace(new_with, "<HOST>"),
                   f"[{tag}] stability line is host-relabel invariant modulo the host token\n"
                   f"    orig: {line1}\n    new:  {line2}")

            # (f) the fingered (host, pillar) tracks the relabel modulo the host token
            #     on the stable branch; the wander branch has no single fingered pillar.
            if expect_stable:
                _check(s1.fingered == (orig_with, "transactability"),
                       f"[{tag}] baseline fingered the real with-rails transactability, got {s1.fingered}")
                _check(s2.fingered == (new_with, "transactability"),
                       f"[{tag}] fingered host follows the new label, pillar unchanged, got {s2.fingered}")
            else:
                _check(s1.fingered is None and s2.fingered is None,
                       f"[{tag}] a wandering run has no single fingered pillar under either labelling")

            ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with
    finally:
        # Module constants are process-global; other tests depend on the real pair.
        ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with


def test_divergence_cause_names_the_softening_side() -> None:
    print("test_divergence_cause_names_the_softening_side")
    # (a) the REAL 2026-07-27 shape: .org flat at 46.1, .com falls 85.5 -> 78.7.
    # The gap narrows -6.8, and the CAUSE must be the with-rails reference SOFTENING
    # (a real-world site regression), NOT the no-rails side gaining capability — the
    # distinction STATE.md hand-wrote ("the delta narrowed because the RAILS side
    # softened, not the no-rails side improving"), now COMPUTED.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 80.0, 33.9),   # drifting
            _artifact("20260727T060000Z", 46.1, 78.7, 32.6),   # drifting
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        cause = hist.divergence_cause
        _check(cause is not None, "out-of-band latest with an in-band anchor gets a cause")
        _check(cause.anchor_ts == "20260727T040000Z", f"cause anchors on the last in-band reading, got {cause.anchor_ts}")
        _check(cause.driver == ch.CANONICAL_WITH_RAILS, f"the with-rails side drove it, got {cause.driver}")
        _check(abs(cause.no_rails_change - 0.0) < 1e-9, f"no-rails flat, got {cause.no_rails_change}")
        _check(abs(cause.with_rails_change - (-6.8)) < 1e-9, f"with-rails fell -6.8, got {cause.with_rails_change}")
        _check(abs(cause.gap_change - (-6.8)) < 1e-9, f"gap narrowed -6.8, got {cause.gap_change}")
        _check(cause.reference_degraded is True, "with-rails softening -> reference_degraded True")
        out = ch.render(hist)
        _check("driver:" in out, "render names the driver")
        _check("SOFTENED" in out, "render says the reference softened, not the gap closing")
    # (b) NON-VACUOUS opposite case: the gap narrows because the NO-RAILS side
    # GAINED capability (the bare storefront improved), with-rails flat. The cause
    # must read the gap as GENUINELY CLOSING (a real benchmark movement), NOT as
    # reference degradation — the opposite conclusion the honesty of this signal
    # rests on. A cause blind to direction would call both "the gap narrowed".
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 52.0, 85.5, 33.5),   # bare side rose
            _artifact("20260727T060000Z", 53.0, 85.5, 32.5),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        cause = hist.divergence_cause
        _check(cause is not None, "the opposite drift also has a cause")
        _check(cause.driver == ch.CANONICAL_NO_RAILS, f"the no-rails side drove it, got {cause.driver}")
        _check(abs(cause.with_rails_change - 0.0) < 1e-9, f"with-rails flat, got {cause.with_rails_change}")
        _check(cause.reference_degraded is False, "no-rails GAINING is not reference degradation")
        out = ch.render(hist)
        _check("GAINED capability" in out, "render reads the gap as genuinely closing")
        _check("real benchmark movement" in out, "render distinguishes real movement from a reference outage")


def test_divergence_cause_none_when_in_band() -> None:
    print("test_divergence_cause_none_when_in_band")
    # nothing has drifted -> no side to blame (honest None, mirroring attribution)
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4),
            _artifact("20260727T020000Z", 46.1, 85.0, 38.9),  # within jitter
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.band == ch.BAND_IN, "series is in-band")
        _check(hist.divergence_cause is None, "in-band series has no divergence cause")
        _check("driver:" not in ch.render(hist), "render omits the driver line when in-band")


def test_divergence_cause_on_real_series() -> None:
    print("test_divergence_cause_on_real_series")
    # Recovery-guarded end-to-end: WHEN the REAL committed series is out of band, the
    # cause must name the with-rails reference softening (the 2026-07-27 real-world
    # drift STATE.md hand-wrote — .org flat, .com fell, so the gap narrowed from the
    # RAILS side, not the floor rising). If the site recovers to in-band, the cause
    # is correctly None and the claim is skipped.
    hist = ch.load_history()
    if hist.band == ch.BAND_IN or hist.divergence_cause is None:
        _check(True, "live series is in-band -> no cause to check (site recovered)")
        return
    cause = hist.divergence_cause
    _check(
        cause.driver == ch.CANONICAL_WITH_RAILS,
        f"the real drift is driven by the with-rails side, got {cause.driver}",
    )
    _check(
        cause.reference_degraded is True,
        "the real drift is the reference softening, not the capability gap closing",
    )
    _check("driver:" in ch.render(hist), "the render names the driver on the real series")


def test_cause_verdict_names_the_pillar_on_cross_mechanism_agreement() -> None:
    print("test_cause_verdict_names_the_pillar_on_cross_mechanism_agreement")
    # READOUT (Cycle 180): the side/driver prose is the sentence that carries the
    # "what to do" meaning (reference SOFTENED -> defer re-capture). It named the
    # SIDE but not WHICH pillar softened — a reader had to mentally join it to the
    # separate pillar-attribution line. cause_verdict now weaves the fingered pillar
    # into that sentence, but ONLY when the two INDEPENDENT attribution mechanisms
    # concur: the isolated pillar sits on the same domain the side cause blames AND
    # moved the same direction as that side's overall. Otherwise it falls back to
    # the side-only wording rather than assert a pillar the signals don't corroborate.
    soften = ch.DivergenceCause(
        anchor_ts="20260728T234102Z",
        no_rails_change=0.0,
        with_rails_change=-9.3,   # with-rails drove it -> reference_degraded
    )
    _check(soften.driver == ch.CANONICAL_WITH_RAILS, "with-rails is the driver")
    _check(soften.reference_degraded is True, "reference softened")
    tx = ch.PillarMove(ch.CANONICAL_WITH_RAILS, "transactability", 87.5, 62.5, -25.0)

    # (1) AGREEMENT (same domain, same direction) -> the pillar is NAMED, and the
    #     side-level wording the older tests/readout grep for is preserved verbatim.
    joined = ch.cause_verdict(soften, tx)
    _check("SOFTENED on transactability" in joined, f"names the softened pillar, got: {joined}")
    _check("SOFTENED" in joined, "side-level SOFTENED wording preserved")
    _check("the pinned fixture still represents the true gap" in joined, "defer meaning preserved")

    # (2) NO PILLAR ISOLATED (top None: a pillar unobserved on one side, where the
    #     side cause is still defined) -> byte-for-byte the pre-pillar side-only form.
    side_only = ch.cause_verdict(soften, None)
    _check("on transactability" not in side_only, "no pillar named when none supplied")
    _check("SOFTENED (a real-world change" in side_only or "SOFTENED (a real-world site change" in side_only,
           f"clause reads immediately after SOFTENED with no pillar, got: {side_only}")

    # (3) DOMAIN DISAGREEMENT: the largest pillar mover is on the OTHER (no-rails)
    #     side while the side cause blames with-rails -> mechanisms disagree, so the
    #     prose must NOT graft a no-rails pillar onto the with-rails softening claim.
    other_side = ch.PillarMove(ch.CANONICAL_NO_RAILS, "legibility", 36.4, 60.0, +23.6)
    disagree = ch.cause_verdict(soften, other_side)
    _check("on legibility" not in disagree, "no pillar named across a domain disagreement")
    _check(disagree == side_only, "domain disagreement falls back to the exact side-only prose")

    # (4) DIRECTION DISAGREEMENT: right domain, but that pillar ROSE while the side's
    #     overall FELL -> naming it "SOFTENED on <pillar>" would contradict the pillar
    #     line, so the clause is withheld.
    rose = ch.PillarMove(ch.CANONICAL_WITH_RAILS, "legibility", 50.0, 80.0, +30.0)
    dir_dis = ch.cause_verdict(soften, rose)
    _check("on legibility" not in dir_dis, "no pillar named when the pillar moved the wrong way")
    _check(dir_dis == side_only, "direction disagreement falls back to the exact side-only prose")

    # (5) The OTHER honest direction: the no-rails floor GAINED capability (the gap
    #     genuinely closed). Agreement names the pillar without disturbing the
    #     "real benchmark movement" language that distinguishes it from an outage.
    gain = ch.DivergenceCause("20260728T234102Z", no_rails_change=+13.6, with_rails_change=0.0)
    _check(gain.driver == ch.CANONICAL_NO_RAILS, "no-rails is the driver")
    _check(gain.reference_degraded is False, "a floor gain is not reference degradation")
    lg = ch.PillarMove(ch.CANONICAL_NO_RAILS, "legibility", 36.4, 50.0, +13.6)
    gverd = ch.cause_verdict(gain, lg)
    _check("GAINED capability on legibility" in gverd, f"names the gained pillar, got: {gverd}")
    _check("real benchmark movement" in gverd, "movement-vs-outage language preserved")


def test_cause_verdict_pillar_named_end_to_end_in_render() -> None:
    print("test_cause_verdict_pillar_named_end_to_end_in_render")
    # Integration: a full series carrying PILLARS through the loader must surface the
    # joined "SOFTENED on <pillar>" sentence in the terminal render's driver line,
    # confirming render/scorecard actually thread PillarAttribution.top into
    # cause_verdict (not just the unit-tested function). Shape mirrors the real drift:
    # .org flat, .com softens with transactability the dominant mover.
    org_p = {"access": 100.0, "legibility": 36.4, "transactability": 18.75, "trust": 60.0}
    com_anchor = {"access": 100.0, "legibility": 90.9, "transactability": 87.5, "trust": 60.0}
    com_drift = {"access": 100.0, "legibility": 90.9, "transactability": 62.5, "trust": 60.0}
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, org_pillars=org_p, com_pillars=com_anchor)
            for i in range(1, 5)
        ]
        rows += [
            _artifact("20260731T080000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
            _artifact("20260731T140000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        top = hist.attribution.top
        _check(top is not None and top.domain == ch.CANONICAL_WITH_RAILS and top.pillar == "transactability",
               f"the loader fingers com transactability, got: {top}")
        out = ch.render(hist)
        _check("driver:" in out, "render still names the driver")
        _check("SOFTENED on transactability" in out,
               f"render's driver line names the fingered pillar, got driver line: "
               f"{[l for l in out.splitlines() if l.startswith('driver:')]}")


def test_cause_verdict_prose_is_host_relabel_invariant() -> None:
    print("test_cause_verdict_prose_is_host_relabel_invariant")
    # METHOD (Cycle 181): VENDOR-NEUTRALITY of the divergence-cause diagnostic prose,
    # made executable as a metamorphic (host-relabel) invariance axis. Cycle 180 wove
    # the fingered pillar into the driver sentence; that decision — and every other
    # part of the sentence (which side-branch fires, the SOFTENED/GAINED verb, the
    # "on <pillar>" clause, the signed magnitude) — must key ONLY on the pair's
    # STRUCTURE (which side carries rails, which pillar moved, its direction), never
    # on the literal host STRINGS. If cause_verdict hardcoded "driftflight.com" the
    # benchmark's core invariant ("checks worded by capability, never by vendor")
    # would be violated in the readout. Transform: RELABEL both reference hosts to
    # fresh, unrelated strings and rebuild the SAME structural scenario. Invariant:
    # the prose is BYTE-IDENTICAL once each host is substituted back to a neutral
    # placeholder — the sentence is a pure function of structure + the two host tokens.
    def _soften_case():
        # with-rails side SOFTENS, transactability the agreeing pillar mover.
        c = ch.DivergenceCause("20260728T234102Z", no_rails_change=0.0, with_rails_change=-9.3)
        tx = ch.PillarMove(ch.CANONICAL_WITH_RAILS, "transactability", 87.5, 62.5, -25.0)
        return c, tx, ch.CANONICAL_WITH_RAILS  # driver host

    def _gain_case():
        # no-rails FLOOR gains capability, legibility the agreeing pillar mover.
        c = ch.DivergenceCause("20260728T234102Z", no_rails_change=+13.6, with_rails_change=0.0)
        lg = ch.PillarMove(ch.CANONICAL_NO_RAILS, "legibility", 36.4, 50.0, +13.6)
        return c, lg, ch.CANONICAL_NO_RAILS  # driver host

    orig_no, orig_with = ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS
    try:
        for build, tag in ((_soften_case, "soften"), (_gain_case, "gain")):
            # (a) verdict at the REAL labels.
            cause, top, driver_host = build()
            orig = ch.cause_verdict(cause, top)
            _check(driver_host in orig, f"[{tag}] baseline prose names the driver host")

            # (b) RELABEL both hosts to fresh, structurally-identical strings and
            #     rebuild the SAME scenario against the new labels.
            ch.CANONICAL_NO_RAILS = "no-rails-store.example"
            ch.CANONICAL_WITH_RAILS = "with-rails-store.example"
            cause2, top2, driver_host2 = build()
            _check(cause2.driver == driver_host2,
                   f"[{tag}] relabel took effect — driver follows the new label, got {cause2.driver}")
            new = ch.cause_verdict(cause2, top2)

            # (c) teeth: the relabeled prose must contain NEITHER original host — a
            #     function that hardcoded the real vendor domains would fail here.
            _check(orig_no not in new and orig_with not in new,
                   f"[{tag}] relabeled prose leaks no original host string, got: {new}")

            # (d) INVARIANCE: substitute each driver host back to one placeholder — the
            #     two verdicts must be byte-identical, so the sentence's STRUCTURE (branch,
            #     verb, pillar clause, sign) is independent of the host strings.
            _check(orig.replace(driver_host, "<DRIVER>") == new.replace(driver_host2, "<DRIVER>"),
                   f"[{tag}] prose is host-relabel invariant modulo the host token\n"
                   f"    orig: {orig}\n    new:  {new}")

            # (e) the Cycle-180 pillar clause survives the relabel on BOTH honest branches.
            pillar = top.pillar
            _check(f"on {pillar}" in new, f"[{tag}] the fingered pillar clause survives relabel, got: {new}")

            ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with
    finally:
        # Module constants are process-global; other tests depend on the real pair.
        ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with


def test_reflection_about_baseline_is_magnitude_invariant_direction_covariant() -> None:
    print("test_reflection_about_baseline_is_magnitude_invariant_direction_covariant")
    # METAMORPHIC guard on the CORE design split of the drift-diagnostic family: the
    # MAGNITUDE machinery (band, out-of-band count, sustained-run span, noise floor)
    # keys on |delta - baseline| and must be DIRECTION-BLIND, while the DIRECTION
    # machinery (signed divergence, gap_change, reference_degraded, DEFER vs
    # RECAPTURE) must be DIRECTION-SENSITIVE. One transform proves both at once:
    # reflect the whole trajectory about its in-band anchor (2026-07-27 shape —
    # no-rails flat, with-rails softens 3 in a row = sustained DEFER). The reflection
    # keeps every |divergence| identical (so the magnitude family CANNOT move) while
    # flipping every sign (so the direction family MUST flip: the same reference side
    # now GAINS instead of softening -> RECAPTURE, not DEFER). Existing cause/recapture
    # tests use hand-built OPPOSITE cases that change WHICH side moves; this pins the
    # stronger statement — one metamorphic pair, same driver side, flipped direction —
    # and adds the cross-transform magnitude-INVARIANCE assertions no other test makes.
    base = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
    base += [
        _artifact("20260727T050000Z", 46.1, 80.0, 33.9),   # drifting
        _artifact("20260727T060000Z", 46.1, 79.0, 32.9),   # drifting
        _artifact("20260727T070000Z", 46.1, 78.7, 32.6),   # drifting, 3rd in a row
    ]
    refl = _reflect_about_anchor(base)
    with tempfile.TemporaryDirectory() as tb, tempfile.TemporaryDirectory() as tr:
        _write_series(tb, base)
        _write_series(tr, refl)
        hb = ch.load_history(tb)
        hr = ch.load_history(tr)

    # sanity: the two series are GENUINELY different (teeth) — the reflected with-rails
    # side rose where the base fell, so this is not comparing a series to itself.
    _check(
        hb.latest.with_rails_overall < hb.points[0].with_rails_overall
        and hr.latest.with_rails_overall > hr.points[0].with_rails_overall,
        "base softens the with-rails side; reflection lifts it — genuinely distinct series",
    )

    # (1) MAGNITUDE machinery is INVARIANT under the reflection.
    _check(hb.band == hr.band == ch.BAND_DRIFTING, f"band invariant, got {hb.band}/{hr.band}")
    _check(
        hb.consecutive_out_of_band == hr.consecutive_out_of_band == 3,
        f"out-of-band count invariant, got {hb.consecutive_out_of_band}/{hr.consecutive_out_of_band}",
    )
    _check(
        hb.sustained_run.span_hours == hr.sustained_run.span_hours == 2.0,
        f"sustained-run span invariant, got {hb.sustained_run.span_hours}/{hr.sustained_run.span_hours}",
    )
    _check(
        hb.noise_floor.stddev == hr.noise_floor.stddev
        and hb.noise_floor.max_abs_divergence == hr.noise_floor.max_abs_divergence,
        "noise floor invariant (in-band anchor readings are fixed points of the reflection)",
    )

    # (2) DIRECTION machinery is COVARIANT: every signed quantity flips, same magnitude.
    _check(
        abs(hb.divergence + hr.divergence) < 1e-9 and hb.divergence < 0 < hr.divergence,
        f"signed divergence flips sign, same magnitude, got {hb.divergence}/{hr.divergence}",
    )
    cb, cr = hb.divergence_cause, hr.divergence_cause
    _check(
        cb.driver == cr.driver == ch.CANONICAL_WITH_RAILS,
        f"driver SIDE invariant (reflection preserves |per-side move|), got {cb.driver}/{cr.driver}",
    )
    _check(
        abs(cb.gap_change + cr.gap_change) < 1e-9 and cb.gap_change < 0 < cr.gap_change,
        f"gap_change flips sign, same magnitude, got {cb.gap_change}/{cr.gap_change}",
    )
    _check(
        cb.reference_degraded is True and cr.reference_degraded is False,
        "reference_degraded flips: base = with-rails softening, reflection = with-rails gaining",
    )
    _check(
        hb.recapture.code == ch.REC_DEFER and hr.recapture.code == ch.REC_RECAPTURE,
        f"recapture flips DEFER->RECAPTURE, got {hb.recapture.code}/{hr.recapture.code}",
    )
    # the render prose flips with the verdict, too (not just the codes).
    _check("DEFER re-capture" in ch.render(hb), "base render says defer")
    _check("re-capture candidate" in ch.render(hr), "reflected render says re-capture candidate")


def test_recapture_advice_baseline_valid_when_in_band() -> None:
    print("test_recapture_advice_baseline_valid_when_in_band")
    # in-band series -> the pinned fixture still represents the true gap; no action.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4),
            _artifact("20260727T020000Z", 46.1, 85.0, 38.9),  # within jitter
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        adv = hist.recapture
        _check(adv is not None, "an in-band series still gets a recommendation")
        _check(adv.code == ch.REC_VALID, f"in-band -> baseline-valid, got {adv.code}")
        out = ch.render(hist)
        _check("re-capture:" in out, "render names the re-capture recommendation")
        _check("baseline valid" in out, "render labels the in-band case baseline-valid")


def test_recapture_advice_waits_when_not_yet_sustained() -> None:
    print("test_recapture_advice_waits_when_not_yet_sustained")
    # out of band, but only 2 trailing readings (< _SUSTAINED_MIN) -> could be
    # jitter, so WAIT, not act. A single blip must never trigger a re-capture.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 78.0, 31.9),  # drifting
            _artifact("20260727T060000Z", 46.1, 78.7, 32.6),  # drifting
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 2, "two trailing out-of-band readings")
        _check(2 < ch._SUSTAINED_MIN, "two is below the sustained cutoff")
        _check(hist.recapture.code == ch.REC_WAIT, f"not-yet-sustained -> wait, got {hist.recapture.code}")
        _check("wait" in ch.render(hist), "render labels the not-yet-sustained case wait")


def test_recapture_advice_defers_on_reference_softening() -> None:
    print("test_recapture_advice_defers_on_reference_softening")
    # THE load-bearing case, the 2026-07-27 real drift shape: sustained (3+) out of
    # band, driven by the with-rails reference SOFTENING (.org flat, .com falls). The
    # pinned fixture still represents the true gap -> DEFER re-capture, do not chase
    # the dip. This is the decision the STATE drift note reasoned out by hand each
    # fire; the site's later recovery vindicated exactly this recommendation.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 80.0, 33.9),   # drifting
            _artifact("20260727T060000Z", 46.1, 79.0, 32.9),   # drifting
            _artifact("20260727T070000Z", 46.1, 78.7, 32.6),   # drifting, 3rd in a row
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 3, f"three trailing out-of-band, got {hist.consecutive_out_of_band}")
        _check(hist.divergence_cause.reference_degraded is True, "the with-rails reference softened")
        _check(hist.recapture.code == ch.REC_DEFER, f"reference-softening -> defer, got {hist.recapture.code}")
        out = ch.render(hist)
        _check("defer re-capture" in out, "render labels the softening case defer")
        _check("DEFER re-capture" in out, "render reason says to defer, not act")


def test_recapture_advice_recommends_recapture_when_baseline_moved() -> None:
    print("test_recapture_advice_recommends_recapture_when_baseline_moved")
    # NON-VACUOUS opposite: sustained out of band because the NO-RAILS floor GAINED
    # capability (the bare storefront durably improved), with-rails flat. That is a
    # real capability-gap change, not a reference outage -> RE-CAPTURE candidate. A
    # recommendation blind to direction would (wrongly) DEFER here too.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 52.0, 85.5, 33.5),   # bare side rose
            _artifact("20260727T060000Z", 53.0, 85.5, 32.5),
            _artifact("20260727T070000Z", 54.0, 85.5, 31.5),   # 3rd in a row
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == 3, "sustained out of band")
        _check(hist.divergence_cause.driver == ch.CANONICAL_NO_RAILS, "the no-rails side drove it")
        _check(hist.divergence_cause.reference_degraded is False, "no-rails gaining is not reference degradation")
        _check(
            hist.recapture.code == ch.REC_RECAPTURE,
            f"durable baseline move -> recapture-candidate, got {hist.recapture.code}",
        )
        _check("re-capture candidate" in ch.render(hist), "render labels the durable-move case a re-capture candidate")


def test_recapture_advice_reviews_when_no_anchor() -> None:
    print("test_recapture_advice_reviews_when_no_anchor")
    # sustained out of band but the ENTIRE series is out of band -> no in-band anchor
    # to attribute against -> REVIEW (a human look), never a blind re-capture.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 70.0, 23.9) for i in range(1, 5)]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.consecutive_out_of_band == len(hist.points), "the whole series is out of band")
        _check(hist.divergence_cause is None, "no in-band anchor -> no cause")
        _check(hist.recapture.code == ch.REC_REVIEW, f"no anchor -> review, got {hist.recapture.code}")
        _check("review" in ch.render(hist), "render labels the no-anchor case review")


def test_recapture_advice_on_real_series_is_coherent() -> None:
    print("test_recapture_advice_on_real_series_is_coherent")
    # End-to-end on the REAL committed series: the recommendation must be present,
    # a known code, and CONSISTENT with the band — in-band <-> baseline-valid, and
    # any out-of-band code never claims baseline-valid. Recovery-tolerant: the site
    # recovered 2026-07-27 so this currently reads baseline-valid, but the assertion
    # holds whichever way the live series sits.
    hist = ch.load_history()
    adv = hist.recapture
    _check(adv is not None, "the real series gets a recommendation")
    _check(adv.code in ch._REC_LABEL, f"a known recommendation code, got {adv.code}")
    if hist.band == ch.BAND_IN:
        _check(adv.code == ch.REC_VALID, f"in-band real series -> baseline-valid, got {adv.code}")
    else:
        _check(adv.code != ch.REC_VALID, f"out-of-band real series is not baseline-valid, got {adv.code}")
    _check("re-capture:" in ch.render(hist), "the real render carries the recommendation line")


def test_recapture_advice_prose_is_host_relabel_invariant() -> None:
    print("test_recapture_advice_prose_is_host_relabel_invariant")
    # TRUTH (Cycle 187): VENDOR-NEUTRALITY of the re-capture DECISION prose, made
    # executable as the metamorphic (host-relabel) invariance axis — the sibling of
    # the Cycle-181 cause_verdict guard and the Cycle-185 attribution-stability guard,
    # for the LAST host-naming drift diagnostic in the family that still lacked one.
    # recapture_advice's DEFER and RECAPTURE reasons embed cause.driver (a host, drawn
    # from the module reference-pair constants) and cause.driver_change; the rendered
    # "re-capture:" line surfaces that reason. This decision is comparability-affecting
    # — RECAPTURE recommends a [LOCAL] fixture re-capture that MOVES the pinned delta
    # the replay guard asserts — so it must key ONLY on the pair's STRUCTURE (which
    # side moved, in which direction, how sustained), never on the literal host
    # STRINGS. A branch that hardcoded "driftflight.com" would violate the benchmark's
    # core invariant ("checks worded by capability, never by vendor") in the very
    # readout that gates a baseline move. The two branches name OPPOSITE sides (DEFER
    # -> the with-rails reference; RECAPTURE -> the no-rails floor), so one guard
    # exercises vendor-neutrality on BOTH host constants. Transform: RELABEL both
    # reference hosts to fresh, unrelated strings and rebuild the SAME structural
    # series. Invariant: the advice CODE is unchanged and the rendered re-capture line
    # is BYTE-IDENTICAL once the driver host is substituted back to a neutral
    # placeholder — a pure function of structure + the host token.
    def _defer_rows():
        # sustained (3+) out of band, with-rails reference SOFTENING (.org flat, .com
        # falls) -> DEFER, reason names the WITH-RAILS driver. (Mirrors the load-
        # bearing 2026-07-27 real-drift shape from the DEFER coherence test.)
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 80.0, 33.9),
            _artifact("20260727T060000Z", 46.1, 79.0, 32.9),
            _artifact("20260727T070000Z", 46.1, 78.7, 32.6),
        ]
        return rows

    def _recapture_rows():
        # sustained out of band, no-rails FLOOR gaining (with-rails flat) -> RECAPTURE,
        # reason names the NO-RAILS driver. The opposite side from DEFER.
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 52.0, 85.5, 33.5),
            _artifact("20260727T060000Z", 53.0, 85.5, 32.5),
            _artifact("20260727T070000Z", 54.0, 85.5, 31.5),
        ]
        return rows

    def _rec_line(hist) -> str:
        for ln in ch.render(hist).splitlines():
            if ln.startswith("re-capture:"):
                return ln
        return ""

    orig_no, orig_with = ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS
    new_no, new_with = "no-rails-store.example", "with-rails-store.example"
    try:
        for rows_of, tag, expect_code, driver_of in (
            (_defer_rows, "defer", ch.REC_DEFER, lambda no, wi: wi),
            (_recapture_rows, "recapture", ch.REC_RECAPTURE, lambda no, wi: no),
        ):
            orig_driver = driver_of(orig_no, orig_with)
            other_orig = orig_no if orig_driver == orig_with else orig_with

            # (a) baseline at the REAL labels: the expected branch + a named driver.
            with tempfile.TemporaryDirectory() as tmp:
                _write_series(tmp, rows_of())
                h1 = ch.load_history(tmp)
            _check(h1.recapture.code == expect_code,
                   f"[{tag}] baseline advice code {expect_code}, got {h1.recapture.code}")
            _check(h1.divergence_cause.driver == orig_driver,
                   f"[{tag}] baseline driver is the expected side, got {h1.divergence_cause.driver}")
            line1 = _rec_line(h1)
            _check(orig_driver in line1,
                   f"[{tag}] baseline re-capture line names the real driver host, got: {line1}")

            # (b) RELABEL both hosts and rebuild the SAME structural series (_artifact
            #     keys the written scores off the constants, so the rebuilt series is
            #     loaded, attributed, and rendered entirely under the new labels).
            ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = new_no, new_with
            new_driver = driver_of(new_no, new_with)
            with tempfile.TemporaryDirectory() as tmp2:
                _write_series(tmp2, rows_of())
                h2 = ch.load_history(tmp2)
            _check(h2.recapture.code == expect_code,
                   f"[{tag}] relabel-invariant advice code {expect_code}, got {h2.recapture.code}")

            # (c) relabel took effect — the reason names the NEW driver host.
            line2 = _rec_line(h2)
            _check(new_driver in line2,
                   f"[{tag}] relabeled re-capture line names the new driver host, got: {line2}")

            # (d) teeth: the relabeled line leaks NEITHER original host — a branch that
            #     hardcoded a real vendor domain would fail here.
            _check(orig_no not in line2 and orig_with not in line2,
                   f"[{tag}] relabeled line leaks no original host, got: {line2}")
            # the non-driver original host must be absent under the baseline too (the
            # reason names ONLY the driver, never the quiet side).
            _check(other_orig not in line1,
                   f"[{tag}] baseline reason names only the driver, not the quiet side, got: {line1}")

            # (e) INVARIANCE: substitute each driver host back to one placeholder — the
            #     two re-capture lines are byte-identical, so the label + reason (the
            #     verdict, the direction clause, the signed driver change) is a pure
            #     function of structure + the host token.
            _check(line1.replace(orig_driver, "<HOST>") == line2.replace(new_driver, "<HOST>"),
                   f"[{tag}] re-capture line is host-relabel invariant modulo the host token\n"
                   f"    orig: {line1}\n    new:  {line2}")

            ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with
    finally:
        # Module constants are process-global; other tests depend on the real pair.
        ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with


def test_noise_floor_is_deterministic_on_real_series() -> None:
    print("test_noise_floor_is_deterministic_on_real_series")
    # THE load-bearing calibration finding: on the committed live series every
    # in-band re-score reproduces the pinned +39.4 delta EXACTLY (σ=0, worst |div|=0)
    # — the static canonical re-score is deterministic at rest, so the in-band band
    # is demonstrably absorbing real-world site TRANSIENTS (the out-of-band readings),
    # not measurement noise. This turns the band docstring's bare "ordinary jitter"
    # assertion into a measured number.
    hist = ch.load_history()
    nf = hist.noise_floor
    _check(nf is not None, "the real series has >= 2 in-band re-scores -> a noise floor")
    _check(nf.n_in_band >= 2, f"measured over the in-band readings, got {nf.n_in_band}")
    _check(nf.stddev == 0.0, f"in-band dispersion is exactly 0 (deterministic re-score), got {nf.stddev}")
    _check(nf.max_abs_divergence == 0.0, f"worst at-rest |div| is 0, got {nf.max_abs_divergence}")
    _check(nf.deterministic is True, "the at-rest re-score is deterministic")
    _check(nf.band_well_separated is True, "a deterministic floor is trivially well-separated")
    out = ch.render(hist)
    _check("noise floor" in out, "the render surfaces the noise floor")
    _check("DETERMINISTIC" in out, "the render names the deterministic-at-rest finding")


def test_noise_floor_sides_are_deterministic_on_real_series() -> None:
    print("test_noise_floor_sides_are_deterministic_on_real_series")
    # The stronger calibration fact behind the deterministic delta: on the committed
    # series NOT ONLY the delta but EACH SIDE reproduces its pinned overall exactly
    # across the in-band readings (σ=0 per side). This refutes the "two correlated
    # drifts that cancel in the difference" reading a critic could give a stable delta
    # — the stability is genuine per-side determinism, storefront by storefront.
    hist = ch.load_history()
    nf = hist.noise_floor
    _check(nf is not None, "the real series has a measured noise floor")
    _check(nf.no_rails_stddev == 0.0, f"no-rails side dispersion is exactly 0, got {nf.no_rails_stddev}")
    _check(nf.with_rails_stddev == 0.0, f"with-rails side dispersion is exactly 0, got {nf.with_rails_stddev}")
    _check(nf.sides_deterministic is True, "both reference storefronts are deterministic at rest")
    # per-side determinism is strictly stronger — it must imply the delta is deterministic
    _check(nf.deterministic is True, "sides-deterministic implies delta-deterministic")
    out = ch.render(hist)
    _check("both sides exact" in out, "the render names the per-side determinism finding")


def test_noise_floor_sides_catch_a_cancelling_drift_the_delta_misses() -> None:
    print("test_noise_floor_sides_catch_a_cancelling_drift_the_delta_misses")
    # NON-VACUOUS + the whole point of the per-side measure: a series whose DELTA is
    # deterministic (σ=0, both sides move in lock-step so the difference is constant)
    # but whose SIDES genuinely vary. The delta-only measure reads "deterministic";
    # the per-side measure correctly reads "not sides-deterministic" — the cancellation
    # the delta is blind to.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4),   # delta 39.4
            _artifact("20260727T020000Z", 47.1, 86.5, 39.4),   # both +1.0, delta unchanged
            _artifact("20260727T030000Z", 45.1, 84.5, 39.4),   # both -1.0, delta unchanged
        ]
        _write_series(tmp, rows)
        nf = ch.load_history(tmp).noise_floor
        _check(nf is not None, "three in-band readings -> a noise floor")
        _check(nf.stddev == 0.0, f"the DELTA is deterministic (constant 39.4), got σ={nf.stddev}")
        _check(nf.deterministic is True, "delta-only measure reads deterministic")
        _check(nf.no_rails_stddev > 0.0, f"the no-rails SIDE varies, got {nf.no_rails_stddev}")
        _check(nf.with_rails_stddev > 0.0, f"the with-rails SIDE varies, got {nf.with_rails_stddev}")
        _check(nf.sides_deterministic is False, "the cancelling per-side drift is caught")


def test_band_clears_the_observed_noise_and_the_real_transients_are_signal() -> None:
    print("test_band_clears_the_observed_noise_and_the_real_transients_are_signal")
    # Calibration validation, both directions:
    #  (a) the in-band band is NOT miscalibrated-too-tight: 3-sigma of the measured
    #      at-rest jitter fits inside the in-band width, so ordinary noise can never
    #      be misread as drift.
    #  (b) the real out-of-band transients are genuine SIGNAL, not noise false-alarms:
    #      every out-of-band reading's |div| sits far above the measured noise floor.
    hist = ch.load_history()
    nf = hist.noise_floor
    _check(nf is not None, "the real series has a measured noise floor")
    _check(3.0 * nf.stddev <= ch._BAND_IN, f"3-sigma jitter fits the in-band band, got {3.0*nf.stddev}")
    _check(nf.max_abs_divergence < ch._BAND_IN, f"worst at-rest |div| is inside the band, got {nf.max_abs_divergence}")
    oob = [p for p in hist.points if abs(p.delta - hist.baseline_delta) > ch._BAND_IN]
    if oob:  # the committed series carries the 2026-07-27 transients; non-vacuous when present
        worst_noise = nf.max_abs_divergence
        for p in oob:
            div = abs(p.delta - hist.baseline_delta)
            _check(
                div > worst_noise + ch._BAND_IN,
                f"transient {p.ts} |div|={div:.1f} is far above the noise floor {worst_noise:.2f}",
            )


def test_noise_floor_measures_synthetic_jitter() -> None:
    print("test_noise_floor_measures_synthetic_jitter")
    # Non-vacuous: the measure is NOT hard-coded to 0. A series whose in-band deltas
    # genuinely vary (all still within +/-2.0 of the baseline) must report a positive
    # stddev, a matching worst |div|, and deterministic=False.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4),   # div 0.0
            _artifact("20260727T020000Z", 46.1, 86.3, 40.2),   # div +0.8 (in-band)
            _artifact("20260727T030000Z", 46.1, 84.7, 38.6),   # div -0.8 (in-band)
        ]
        _write_series(tmp, rows)
        nf = ch.load_history(tmp).noise_floor
        _check(nf is not None, "three in-band readings -> a noise floor")
        _check(nf.n_in_band == 3, f"all three are in-band, got {nf.n_in_band}")
        _check(nf.stddev > 0.0, f"varying in-band deltas -> positive dispersion, got {nf.stddev}")
        _check(abs(nf.max_abs_divergence - 0.8) < 1e-6, f"worst |div| is 0.8, got {nf.max_abs_divergence}")
        _check(nf.deterministic is False, "measurable dispersion -> not deterministic")
        _check(nf.band_well_separated is True, "0.8-scale jitter still fits the +/-2.0 band at 3-sigma")


def test_noise_floor_flags_a_too_tight_band() -> None:
    print("test_noise_floor_flags_a_too_tight_band")
    # Makes band_well_separated non-vacuous: in-band deltas that crowd the whole
    # +/-2.0 width (so 3-sigma of the at-rest jitter exceeds the band) must report
    # band_well_separated=False and render "TOO TIGHT" — the miscalibration alarm.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 87.3, 41.3),   # div +1.9 (just in-band)
            _artifact("20260727T020000Z", 46.1, 83.7, 37.5),   # div -1.9 (just in-band)
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        nf = hist.noise_floor
        _check(nf is not None, "two in-band readings -> a noise floor")
        _check(nf.deterministic is False, "1.9-point jitter is not deterministic")
        _check(3.0 * nf.stddev > ch._BAND_IN, f"3-sigma exceeds the band, got {3.0*nf.stddev}")
        _check(nf.band_well_separated is False, "the band is too tight for this jitter")
        _check("TOO TIGHT" in ch.render(hist), "the render raises the too-tight alarm")


def test_noise_floor_none_below_two_in_band() -> None:
    print("test_noise_floor_none_below_two_in_band")
    # Honest None: dispersion is undefined for < 2 in-band readings. A series that is
    # entirely out of band (no at-rest reading) has no measurable floor.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 60.0, 13.9),   # out of band
            _artifact("20260727T020000Z", 46.1, 65.0, 18.9),   # out of band
        ]
        _write_series(tmp, rows)
        _check(ch.load_history(tmp).noise_floor is None, "no in-band readings -> no noise floor")
    # a lone in-band reading is also < 2 -> undefined dispersion -> None
    with tempfile.TemporaryDirectory() as tmp2:
        _write_series(tmp2, [_artifact("20260727T010000Z", 46.1, 85.5, 39.4)])
        _check(ch.load_history(tmp2).noise_floor is None, "a single in-band reading -> no dispersion, None")


def test_liveness_none_without_now() -> None:
    print("test_liveness_none_without_now")
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [_artifact("20260728T040000Z", 46.1, 85.5, 39.4)])
        hist = ch.load_history(tmp)  # no `now` -> pure summary, no clock claim
        _check(hist.liveness is None, "no `now` -> liveness is None (pure summary)")
        _check(
            "live signal:" not in ch.render(hist),
            "render omits the live-signal line when freshness is unknown",
        )


def test_liveness_fresh_when_within_floor() -> None:
    print("test_liveness_fresh_when_within_floor")
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [_artifact("20260728T040000Z", 46.1, 85.5, 39.4)])
        now = datetime(2026, 7, 28, 5, 0, 0, tzinfo=timezone.utc)  # 1h after
        hist = ch.load_history(tmp, now=now)
        _check(hist.liveness is not None, "liveness computed when `now` supplied")
        _check(abs(hist.liveness.age_hours - 1.0) < 1e-6, f"age 1.0h, got {hist.liveness.age_hours}")
        _check(hist.liveness.fresh, "1h-old re-score is FRESH (within the 6h floor)")
        _check("FRESH" in ch.render(hist), "render names it FRESH")


def test_liveness_stale_past_floor_warns_verdict_is_old() -> None:
    print("test_liveness_stale_past_floor_warns_verdict_is_old")
    with tempfile.TemporaryDirectory() as tmp:
        # a perfectly in-band latest reading — the verdict looks healthy...
        _write_series(tmp, [_artifact("20260727T220000Z", 46.1, 85.5, 39.4)])
        now = datetime(2026, 7, 28, 5, 0, 0, tzinfo=timezone.utc)  # 7h after
        hist = ch.load_history(tmp, now=now)
        _check(hist.band == ch.BAND_IN, "the latest reading is itself in-band (healthy-looking)")
        _check(hist.liveness is not None and not hist.liveness.fresh, "...but 7h old -> STALE")
        _check(abs(hist.liveness.age_hours - 7.0) < 1e-6, f"age 7.0h, got {hist.liveness.age_hours}")
        out = ch.render(hist)
        # the stale warning fires DESPITE the in-band verdict — age is not confirmation
        _check("STALE" in out, "render warns STALE")
        _check("runner may be down" in out, "render names the likely runner stall")


def test_liveness_future_artifact_clamps_to_zero() -> None:
    print("test_liveness_future_artifact_clamps_to_zero")
    with tempfile.TemporaryDirectory() as tmp:
        _write_series(tmp, [_artifact("20260728T060000Z", 46.1, 85.5, 39.4)])
        now = datetime(2026, 7, 28, 5, 0, 0, tzinfo=timezone.utc)  # artifact is 1h ahead
        hist = ch.load_history(tmp, now=now)
        _check(hist.liveness.age_hours == 0.0, f"future ts clamps to age 0, got {hist.liveness.age_hours}")
        _check(hist.liveness.fresh, "a future-dated artifact is trivially fresh, never negative-age")


def test_liveness_none_on_unparseable_ts() -> None:
    print("test_liveness_none_on_unparseable_ts")
    pt = ch.CanonicalPoint(
        ts="not-a-timestamp",
        no_rails_overall=46.1, no_rails_grade="F",
        with_rails_overall=85.5, with_rails_grade="B", delta=39.4,
    )
    now = datetime(2026, 7, 28, 5, 0, 0, tzinfo=timezone.utc)
    _check(ch.liveness(pt, now) is None, "unparseable ts -> no freshness claim (honest None)")
    _check(ch._parse_ts("not-a-timestamp") is None, "_parse_ts rejects a bad ts")
    _check(ch._parse_ts("20260728T050000Z") is not None, "_parse_ts accepts the real format")


def test_liveness_on_real_committed_series_is_coherent() -> None:
    print("test_liveness_on_real_committed_series_is_coherent")
    now = datetime.now(timezone.utc)
    hist = ch.load_history(now=now)  # default committed runs/local
    _check(hist.liveness is not None, "the real series has a parseable latest ts")
    _check(hist.liveness.age_hours >= 0.0, f"age is non-negative, got {hist.liveness.age_hours}")
    # fresh is exactly the floor comparison — no drift between flag and number
    _check(
        hist.liveness.fresh == (hist.liveness.age_hours <= ch._STALE_FLOOR_HOURS),
        "fresh flag matches the age-vs-floor comparison",
    )


def test_terminal_and_html_surfaces_name_the_same_diagnostics() -> None:
    print("test_terminal_and_html_surfaces_name_the_same_diagnostics")
    # READOUT parity guard (Cycle 188): the canonical-delta DIAGNOSIS has two
    # surfaces — the terminal ``asrs canonical-history`` render (``ch.render``) and
    # the HTML ``canonical-history.html`` page
    # (``scorecard._write_canonical_history_page``). Every cycle that added a
    # diagnostic (sustained wall-clock span, at-rest noise floor, pillar
    # attribution, attribution stability, side/direction cause, re-capture advice)
    # had to HAND-PORT it to BOTH surfaces — the "terminal->HTML close-out" the
    # scorecard comments describe (per_kind Cycle 10->12, between_kind Cycle 18->20,
    # noise floor Cycle 47->48, liveness Cycle 51, stability Cycle 183->184). Nothing
    # kept the two from silently drifting apart: the HTML page had no test at all, so
    # a renderer dropping a line (or a sibling never gaining one) went uncaught. This
    # binds them. Build ONE out-of-band history that fires every diagnostic, render
    # BOTH surfaces, and assert each diagnostic FACT — derived from the history MODEL,
    # not hand-written — appears in BOTH. If exactly one surface loses a fact, this
    # reddens. Display-only: imports no scoring code, moves no score.
    from pathlib import Path

    from asrs import scorecard

    org_p = {"access": 100.0, "legibility": 36.4, "transactability": 18.75, "trust": 60.0}
    com_anchor = {"access": 100.0, "legibility": 90.9, "transactability": 87.5, "trust": 60.0}
    com_drift = {"access": 100.0, "legibility": 90.9, "transactability": 62.5, "trust": 60.0}
    with tempfile.TemporaryDirectory() as tmp:
        # 4 in-band anchors (both sides flat -> deterministic noise floor) + a trailing
        # run of 3 out-of-band drift readings spanning ~18h (com transactability
        # softens, mirroring the real Jul-31/Aug-1 drop) so sustained-run, attribution,
        # stability, cause and re-capture all fire.
        rows = [
            _artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4,
                      org_pillars=org_p, com_pillars=com_anchor)
            for i in range(1, 5)
        ]
        rows += [
            _artifact("20260731T080000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
            _artifact("20260731T140000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
            _artifact("20260801T020000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
        ]
        _write_series(tmp, rows)
        # No clock -> liveness None (deterministic; the liveness banner is separately
        # unit-tested and is time-dependent, so we keep it out of the parity fixture).
        hist = ch.load_history(tmp)

        # Preconditions: every diagnostic must have fired, or the parity check is
        # vacuous (both surfaces trivially agree by omitting the same absent line).
        sr = hist.sustained_run
        nf = hist.noise_floor
        attr = hist.attribution
        stab = hist.attribution_stability
        cause = hist.divergence_cause
        adv = hist.recapture
        _check(hist.band != ch.BAND_IN, "the fixture series is out of band")
        _check(sr is not None and sr.span_hours > 0, "a sustained run with a real span fired")
        _check(nf is not None and nf.deterministic, "the at-rest noise floor is deterministic")
        _check(attr is not None and attr.top is not None, "pillar attribution isolated a top mover")
        _check(stab is not None, "attribution stability is measurable")
        _check(cause is not None, "a side/direction cause fired")
        _check(adv is not None and adv.code != ch.REC_NO_DATA, "a re-capture recommendation fired")

        terminal = ch.render(hist)
        html_path = scorecard._write_canonical_history_page(Path(tmp), history=hist)
        html = Path(html_path).read_text(encoding="utf-8")

        top = attr.top
        # (label, needle) — each needle is COMPUTED from the history model, never a
        # literal, so this stays vendor-neutral and tracks the data. Both surfaces
        # must carry every one; a diagnostic present on only one side is a parity leak.
        facts = [
            ("latest no-rails overall", f"{hist.latest.no_rails_overall:.1f}"),
            ("latest with-rails overall", f"{hist.latest.with_rails_overall:.1f}"),
            ("band verdict", ch._BAND_VERDICT[hist.band]),
            ("sustained wall-clock span", f"spanning {sr.span_hours:.1f}h"),
            ("at-rest noise-floor determinism", "DETERMINISTIC at rest"),
            ("attribution: moved pillar", top.pillar),
            ("attribution: moved side", top.domain),
            ("attribution stability verdict", "STABLE" if stab.stable else "WANDERS"),
            ("side/direction cause", ch.cause_verdict(cause, top)),
            ("re-capture recommendation", ch._REC_LABEL[adv.code]),
        ]
        for label, needle in facts:
            _check(needle in terminal, f"terminal surface names the {label}: {needle!r}")
            _check(needle in html, f"HTML surface names the {label}: {needle!r}")


def test_runs_against_real_committed_series() -> None:
    print("test_runs_against_real_committed_series")
    hist = ch.load_history()  # default runs/local in this checkout
    _check(len(hist.points) >= 1, f"the committed series has points, got {len(hist.points)}")
    _check(hist.latest is not None, "there is a latest point")
    _check(hist.band in ch._BAND_VERDICT, f"latest lands in a known band, got {hist.band}")
    out = ch.render(hist)
    _check(len(out) > 120, f"real render is substantive, {len(out)} chars")


def main() -> int:
    tests = [
        test_loader_parses_and_skips_malformed,
        test_bands_and_in_band_series,
        test_sustained_drift_counts_trailing_run,
        test_sustained_run_spans_wall_clock,
        test_sustained_run_none_when_in_band,
        test_sustained_run_lone_reading_is_zero_span,
        test_sustained_run_none_on_unparseable_ts,
        test_sustained_run_on_real_series_is_coherent,
        test_render_substantive_and_empty_safe,
        test_baseline_cannot_drift_from_replay_guard,
        test_attribution_names_the_moving_pillar,
        test_attribution_none_when_in_band,
        test_attribution_skips_unobserved_pillar_and_needs_an_anchor,
        test_attribution_on_real_series_fingers_the_drifting_pillar,
        test_attribution_stability_catches_a_wandering_mover,
        test_attribution_stability_stable_when_pillar_holds,
        test_attribution_stability_none_when_short_or_no_anchor,
        test_attribution_stability_on_real_series_holds_the_pillar,
        test_attribution_stability_is_host_relabel_invariant,
        test_divergence_cause_names_the_softening_side,
        test_divergence_cause_none_when_in_band,
        test_divergence_cause_on_real_series,
        test_cause_verdict_names_the_pillar_on_cross_mechanism_agreement,
        test_cause_verdict_pillar_named_end_to_end_in_render,
        test_cause_verdict_prose_is_host_relabel_invariant,
        test_reflection_about_baseline_is_magnitude_invariant_direction_covariant,
        test_recapture_advice_baseline_valid_when_in_band,
        test_recapture_advice_waits_when_not_yet_sustained,
        test_recapture_advice_defers_on_reference_softening,
        test_recapture_advice_recommends_recapture_when_baseline_moved,
        test_recapture_advice_reviews_when_no_anchor,
        test_recapture_advice_on_real_series_is_coherent,
        test_recapture_advice_prose_is_host_relabel_invariant,
        test_noise_floor_is_deterministic_on_real_series,
        test_noise_floor_sides_are_deterministic_on_real_series,
        test_noise_floor_sides_catch_a_cancelling_drift_the_delta_misses,
        test_band_clears_the_observed_noise_and_the_real_transients_are_signal,
        test_noise_floor_measures_synthetic_jitter,
        test_noise_floor_flags_a_too_tight_band,
        test_noise_floor_none_below_two_in_band,
        test_liveness_none_without_now,
        test_liveness_fresh_when_within_floor,
        test_liveness_stale_past_floor_warns_verdict_is_old,
        test_liveness_future_artifact_clamps_to_zero,
        test_liveness_none_on_unparseable_ts,
        test_liveness_on_real_committed_series_is_coherent,
        test_terminal_and_html_surfaces_name_the_same_diagnostics,
        test_runs_against_real_committed_series,
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
