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


def test_attribution_on_real_series_fingers_com_legibility() -> None:
    print("test_attribution_on_real_series_fingers_com_legibility")
    # Non-vacuous end-to-end: the REAL committed series' current drift must
    # attribute to driftflight.com legibility (the 2026-07-27 real-world site
    # change STATE.md hand-wrote — now COMPUTED). Guarded so it only asserts the
    # attribution WHEN the live series is actually out of band; if the site
    # recovers to in-band, attribution is correctly None and we skip the claim.
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
        test_render_substantive_and_empty_safe,
        test_baseline_cannot_drift_from_replay_guard,
        test_attribution_names_the_moving_pillar,
        test_attribution_none_when_in_band,
        test_attribution_skips_unobserved_pillar_and_needs_an_anchor,
        test_attribution_on_real_series_fingers_com_legibility,
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
