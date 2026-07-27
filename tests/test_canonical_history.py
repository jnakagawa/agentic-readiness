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


def _artifact(ts: str, org: float, com: float, delta, ok: bool = True) -> dict:
    def side(overall, grade):
        return {"ok": ok, "overall": overall, "grade": grade, "scored": True}
    return {
        "ts": ts,
        "kind": "local-verify",
        "tests_ok": True,
        "scores": {
            ch.CANONICAL_NO_RAILS: side(org, "F"),
            ch.CANONICAL_WITH_RAILS: side(com, "B"),
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
