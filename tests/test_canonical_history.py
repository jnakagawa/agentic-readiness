"""Tests for the canonical-delta HISTORY readout (asrs/canonical_history.py).

Runnable directly, no pytest required:

    python tests/test_canonical_history.py

The local runner commits ``runs/local/verify_<ts>.json`` every fire — a live
static re-score of the reference pair. ``canonical_history`` reads that committed
series and surfaces the delta TREND + a sustained-drift alert vs the committed-
fixture baseline the in-cloud replay guard pins (+39.4). These tests pin:

  - the loader parses a well-formed artifact and SKIPS malformed ones (the early
    pre-Cycle-13 FileNotFoundError artifacts, any run where a domain isn't
    ``ok``, and any run scored while the bench's own guards were red
    (``tests_ok`` False)) — attribution honesty + versioned comparability: an
    unobserved re-score, or one from an inconsistent scoring path, is not a data
    point;
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
from datetime import datetime, timedelta, timezone

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


def _shift_ts(ts: str, delta) -> str:
    """Translate a ``YYYYMMDDTHHMMSSZ`` timestamp by a fixed ``timedelta``,
    reformatting in the same verify-artifact format so the loader still parses it."""
    when = datetime.strptime(ts, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return (when + delta).strftime("%Y%m%dT%H%M%SZ")


def _time_translate(rows: list[dict], delta) -> list[dict]:
    """Shift every row's timestamp by ``delta`` (numeric trajectory untouched).

    The metamorphic transform for TIME-TRANSLATION invariance: the drift
    diagnostics measure RELATIVE time (durations, ordering, freshness-vs-``now``),
    never the absolute epoch, so translating the whole series in time — even across
    a month/year boundary — must leave every structural verdict identical. Pillars,
    overalls, grades and deltas are carried through unchanged; only the ``ts`` moves."""
    out: list[dict] = []
    for r in rows:
        s = r["scores"]
        out.append(
            _artifact(
                _shift_ts(r["ts"], delta),
                s[ch.CANONICAL_NO_RAILS]["overall"],
                s[ch.CANONICAL_WITH_RAILS]["overall"],
                r["delta"],
                org_pillars=s[ch.CANONICAL_NO_RAILS].get("pillars"),
                com_pillars=s[ch.CANONICAL_WITH_RAILS].get("pillars"),
            )
        )
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


def test_loader_skips_a_reading_from_a_red_bench() -> None:
    print("test_loader_skips_a_reading_from_a_red_bench")
    with tempfile.TemporaryDirectory() as tmp:
        # Two identical, otherwise-usable readings; one was scored while the
        # bench's own guards were red. A tests-red fire still writes a full
        # score (the runner bails only on a failed git pull, before scoring),
        # but its scoring path may be in an unexpected state — not comparable
        # within the version, so it must not anchor a drift point.
        clean = _artifact("20260727T010000Z", 46.1, 85.5, 39.4)
        red_bench = _artifact("20260727T020000Z", 46.1, 62.5, 16.4)
        red_bench["tests_ok"] = False
        # a reading with NO tests_ok field is the honest-unknown case: stays in.
        legacy_no_field = _artifact("20260727T030000Z", 46.1, 85.5, 39.4)
        del legacy_no_field["tests_ok"]
        _write_series(tmp, [clean, red_bench, legacy_no_field])
        pts = ch.load_points(tmp)
        kept = {p.ts for p in pts}
        _check(
            kept == {"20260727T010000Z", "20260727T030000Z"},
            f"the red-bench reading is dropped, unknown stays; kept {sorted(kept)}",
        )
        # Non-vacuous / has teeth: without the guard the red reading WOULD load
        # (it is otherwise well-formed) — flip its flag True and it reappears.
        red_bench["tests_ok"] = True
        _write_series(tmp, [clean, red_bench, legacy_no_field])
        _check(
            len(ch.load_points(tmp)) == 3,
            "same reading loads once its bench is green — the flag is what excludes",
        )


def test_real_committed_series_is_all_green_bench() -> None:
    print("test_real_committed_series_is_all_green_bench")
    # The exclusion is defense-in-depth: every committed artifact today was
    # scored on a green bench, so the guard drops NONE of the real series (the
    # live drift attribution the P0 rests on is unchanged). If a future artifact
    # lands with tests_ok False, this reconciles loaded-points vs raw-usable.
    import glob as _glob

    runs = os.path.join(_REPO, "runs", "local")
    raw_usable = red = 0
    for path in sorted(_glob.glob(os.path.join(runs, "verify_*.json"))):
        with open(path, encoding="utf-8") as fh:
            obj = json.load(fh)
        base = dict(obj)
        base.pop("tests_ok", None)  # neutralize the new gate to count raw-usable
        if ch._point_from_artifact(base) is not None:
            raw_usable += 1
            if obj.get("tests_ok") is False:
                red += 1
    loaded = len(ch.load_points())
    _check(red == 0, f"no committed reading was scored on a red bench, got {red}")
    _check(
        loaded == raw_usable,
        f"the bench gate drops nothing on the real series: loaded {loaded} == usable {raw_usable}",
    )


def test_load_accounting_counts_exclusions_by_reason() -> None:
    print("test_load_accounting_counts_exclusions_by_reason")
    # The Cycle-215 loader gate drops artifacts silently; Cycle 216 ACCOUNTS for
    # them by reason so the readout can show the series is FILTERED, not raw. Build
    # a directory with one clean reading, one red-bench (tests_ok False), and two
    # malformed (one missing scores, one unparseable JSON) and assert the counts +
    # the closure invariant included + red + malformed == total.
    with tempfile.TemporaryDirectory() as tmp:
        clean = _artifact("20260727T010000Z", 46.1, 85.5, 39.4)
        red_bench = _artifact("20260727T020000Z", 46.1, 62.5, 16.4)
        red_bench["tests_ok"] = False
        malformed = {"ts": "20260727T030000Z", "kind": "local-verify"}  # no scores/delta
        _write_series(tmp, [clean, red_bench, malformed])
        # a file that is not valid JSON at all -> counted malformed (an artifact we
        # saw but could not use), never crashes the loader.
        with open(os.path.join(tmp, "verify_20260727T040000Z.json"), "w") as fh:
            fh.write("{not json")
        pts, acct = ch.load_points_accounted(tmp)
        _check(len(pts) == 1, f"only the clean reading loads, got {len(pts)}")
        _check(acct.total == 4, f"all four artifacts are counted, got {acct.total}")
        _check(acct.included == 1, f"one included, got {acct.included}")
        _check(acct.excluded_red_bench == 1, f"one red-bench, got {acct.excluded_red_bench}")
        _check(acct.excluded_malformed == 2, f"two malformed, got {acct.excluded_malformed}")
        _check(acct.excluded == 3, f"three excluded total, got {acct.excluded}")
        _check(acct.any_excluded, "any_excluded is True when the series was filtered")
        _check(
            acct.included + acct.excluded_red_bench + acct.excluded_malformed == acct.total,
            "the accounting closes: included + red + malformed == total",
        )
        # Teeth: flip the red-bench flag green and it reclassifies as INCLUDED, not
        # red-bench — the flag is what moves it between the buckets.
        red_bench["tests_ok"] = True
        _write_series(tmp, [clean, red_bench, malformed])
        _, acct2 = ch.load_points_accounted(tmp)
        _check(
            acct2.included == 2 and acct2.excluded_red_bench == 0,
            f"green bench -> included, not red-bench; got {acct2.included}/{acct2.excluded_red_bench}",
        )


def test_load_accounting_clean_series_reports_zero_excluded() -> None:
    print("test_load_accounting_clean_series_reports_zero_excluded")
    # A series with nothing to drop: accounting must report 0 excluded and
    # any_excluded False, so the readout stays silent (raw == filtered). This is
    # the state of the real committed series today.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 4)]
        _write_series(tmp, rows)
        pts, acct = ch.load_points_accounted(tmp)
        _check(acct.total == 3 and acct.included == 3, "all three kept")
        _check(acct.excluded == 0 and not acct.any_excluded, "nothing excluded, any_excluded False")
    # The real committed series carries the loader accounting, and it is
    # non-vacuous: no artifact was ever scored on a red bench (0 red-bench, matching
    # test_real_committed_series_is_all_green_bench), but the early pre-Cycle-13
    # legacy FileNotFoundError artifact(s) ARE malformed and were previously dropped
    # SILENTLY — the accounting now surfaces exactly them, which is the point of the
    # increment. The closure invariant holds on the real data.
    hist = ch.load_history()
    ra = hist.load_accounting
    _check(ra is not None, "load_history attaches the loader accounting")
    _check(ra.included == len(hist.points), "included matches the loaded point count")
    _check(ra.excluded_red_bench == 0, f"no committed reading is red-bench, got {ra.excluded_red_bench}")
    _check(
        ra.included + ra.excluded_red_bench + ra.excluded_malformed == ra.total,
        "the accounting closes on the real committed series",
    )


def test_render_names_exclusion_accounting_when_filtered() -> None:
    print("test_render_names_exclusion_accounting_when_filtered")
    # The terminal render must NAME the exclusion accounting when the series was
    # filtered (so the operator sees it is not raw), and stay silent when it wasn't.
    with tempfile.TemporaryDirectory() as tmp:
        clean = _artifact("20260727T010000Z", 46.1, 85.5, 39.4)
        clean2 = _artifact("20260727T020000Z", 46.1, 85.5, 39.4)
        red_bench = _artifact("20260727T030000Z", 46.1, 62.5, 16.4)
        red_bench["tests_ok"] = False
        _write_series(tmp, [clean, clean2, red_bench])
        out = ch.render(ch.load_history(tmp))
        _check("series filtered" in out, "render names the filtered series")
        _check("2 of 3 artifacts kept" in out, f"render names kept/total counts:\n{out}")
        # The reason parenthetical lists only the non-zero causes: 1 red-bench, and
        # NOT a "0 malformed" entry (the phrase "(1 red-bench)" is exact).
        _check("(1 red-bench)" in out, f"render lists only the non-zero reason:\n{out}")
    # Clean series -> no filtered line at all.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 4)]
        _write_series(tmp, rows)
        out = ch.render(ch.load_history(tmp))
        _check("series filtered" not in out, "an unfiltered series shows no filtered line")


def test_series_integrity_intact_within_floor() -> None:
    print("test_series_integrity_intact_within_floor")
    # Cycle 216 NAMES what the loader dropped; Cycle 217 JUDGES whether the drop
    # compromises the series the drift verdict is drawn from. A small excluded
    # fraction (within the floor) is ordinary attrition -> intact. Build 4 clean +
    # 1 red-bench = 1/5 = 20% excluded, at/below the 25% floor.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        red_bench = _artifact("20260727T050000Z", 46.1, 62.5, 16.4)
        red_bench["tests_ok"] = False
        _write_series(tmp, rows + [red_bench])
        hist = ch.load_history(tmp)
        integ = hist.integrity
        _check(integ is not None, "load_history attaches the series integrity verdict")
        _check(integ.total == 5 and integ.excluded == 1, "5 total, 1 excluded")
        _check(abs(integ.excluded_fraction - 0.2) < 1e-9, f"20% excluded, got {integ.excluded_fraction}")
        _check(abs(integ.red_bench_fraction - 0.2) < 1e-9, "the sole exclusion is red-bench")
        _check(integ.intact, "20% excluded is within the 25% floor -> intact")


def test_series_integrity_degraded_past_floor() -> None:
    print("test_series_integrity_degraded_past_floor")
    # The teeth: when so much of the committed series is filtered that the excluded
    # fraction CROSSES the floor, the kept remnant is not a trustworthy basis and the
    # verdict must read DEGRADED. Build 2 clean + 1 red-bench + 1 malformed = 2/4 =
    # 50% excluded, PAST the 25% floor. Included stays >= 1 so there is still a series.
    with tempfile.TemporaryDirectory() as tmp:
        clean = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 3)]
        red_bench = _artifact("20260727T030000Z", 46.1, 62.5, 16.4)
        red_bench["tests_ok"] = False
        malformed = {"ts": "20260727T040000Z", "kind": "local-verify"}  # no scores/delta
        _write_series(tmp, clean + [red_bench, malformed])
        hist = ch.load_history(tmp)
        integ = hist.integrity
        _check(integ is not None and integ.total == 4 and integ.excluded == 2, "4 total, 2 excluded")
        _check(abs(integ.excluded_fraction - 0.5) < 1e-9, f"50% excluded, got {integ.excluded_fraction}")
        _check(not integ.intact, "50% excluded is past the 25% floor -> DEGRADED")
    # Boundary: exactly AT the floor is still intact (<=), not degraded — the floor
    # is the discriminator. 3 distinct clean + 1 red-bench = 1/4 = 25%.
    with tempfile.TemporaryDirectory() as tmp:
        clean3 = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 4)]
        red = _artifact("20260727T040000Z", 46.1, 62.5, 16.4)
        red["tests_ok"] = False
        _write_series(tmp, clean3 + [red])
        integ2 = ch.load_history(tmp).integrity
        _check(integ2.total == 4 and integ2.excluded == 1, "4 total, 1 excluded at the boundary")
        _check(abs(integ2.excluded_fraction - 0.25) < 1e-9, "at the 25% floor exactly")
        _check(integ2.intact, "exactly at the floor is intact (<=), the boundary is inclusive")


def test_series_integrity_none_without_accounting_or_artifacts() -> None:
    print("test_series_integrity_none_without_accounting_or_artifacts")
    # Honest-None discipline: no loader accounting (a bare point list a test builds
    # directly) -> no integrity claim; and an empty runs dir (0 artifacts found) ->
    # None, nothing to judge.
    pts = [ch.CanonicalPoint("20260727T010000Z", 46.1, "F", 85.5, "B", 39.4)]
    _check(ch.summarize(pts).integrity is None, "a bare point summary makes no integrity claim")
    _check(ch.series_integrity(None) is None, "series_integrity(None) is None")
    with tempfile.TemporaryDirectory() as tmp:
        _check(ch.load_history(tmp).integrity is None, "an empty runs dir yields no integrity verdict")


def test_series_integrity_on_real_series_is_intact() -> None:
    print("test_series_integrity_on_real_series_is_intact")
    # Non-vacuous on the REAL committed series: the loader drops the pre-Cycle-13
    # legacy malformed artifact(s) but keeps the overwhelming majority, so the real
    # verdict is INTACT with a small excluded fraction — the drift verdict the P0
    # rests on is drawn from a representative series, and this asserts it on real data.
    hist = ch.load_history()
    integ = hist.integrity
    _check(integ is not None, "the real committed series carries an integrity verdict")
    _check(integ.included == len(hist.points), "included matches the loaded point count")
    _check(integ.intact, f"the real series is intact, excluded={integ.excluded_fraction:.3f}")
    _check(
        integ.excluded_fraction < integ.floor,
        f"the real excluded fraction {integ.excluded_fraction:.3f} is below the {integ.floor} floor",
    )


def test_render_names_series_integrity_when_filtered() -> None:
    print("test_render_names_series_integrity_when_filtered")
    # The terminal render must NAME the integrity verdict when the series was filtered
    # (intact vs degraded), and stay silent when nothing was dropped. Intact path:
    # 4 clean + 1 red-bench (20%).
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        red_bench = _artifact("20260727T050000Z", 46.1, 62.5, 16.4)
        red_bench["tests_ok"] = False
        _write_series(tmp, rows + [red_bench])
        out = ch.render(ch.load_history(tmp))
        _check("series integrity: INTACT" in out, f"render names the intact verdict:\n{out}")
        _check("within the 25% floor" in out, "render names the floor")
        _check("red-bench" in out, "render names the red-bench exclusion in the integrity line")
    # Degraded path: 2 clean + 3 red-bench (60%).
    with tempfile.TemporaryDirectory() as tmp:
        clean = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 3)]
        reds = []
        for i in range(3, 6):
            r = _artifact(f"20260727T0{i}0000Z", 46.1, 62.5, 16.4)
            r["tests_ok"] = False
            reds.append(r)
        _write_series(tmp, clean + reds)
        out = ch.render(ch.load_history(tmp))
        _check("series integrity: DEGRADED" in out, f"render names the degraded verdict:\n{out}")
        _check("weigh it with caution" in out, "the degraded verdict warns the reader")
    # Clean series -> no integrity line at all (raw == filtered, nothing to judge).
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 4)]
        _write_series(tmp, rows)
        out = ch.render(ch.load_history(tmp))
        _check("series integrity" not in out, "an unfiltered series shows no integrity line")


def test_render_empty_series_names_all_excluded() -> None:
    print("test_render_empty_series_names_all_excluded")
    # The maximally degraded case: artifacts were found but ALL filtered out. The
    # empty render must not imply the runner produced nothing — it names the count
    # and the reasons instead.
    with tempfile.TemporaryDirectory() as tmp:
        r1 = _artifact("20260727T010000Z", 46.1, 62.5, 16.4)
        r1["tests_ok"] = False
        r2 = {"ts": "20260727T020000Z", "kind": "local-verify"}  # malformed, no scores
        _write_series(tmp, [r1, r2])
        hist = ch.load_history(tmp)
        _check(not hist.points, "no usable points survived the filter")
        out = ch.render(hist)
        _check("2 found, all 2 excluded" in out, f"empty render names the all-excluded count:\n{out}")
        _check("1 red-bench" in out and "1 malformed" in out, "names both reasons")
    # A genuinely empty runs dir still shows the plain message (no accounting to name).
    with tempfile.TemporaryDirectory() as tmp:
        out = ch.render(ch.load_history(tmp))
        _check("no usable live-verify artifacts found" in out, "empty dir -> plain message")


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


def test_reference_degraded_is_conservative_across_the_full_driver_grid() -> None:
    print("test_reference_degraded_is_conservative_across_the_full_driver_grid")
    # TRUTH (Cycle 219). reference_degraded gates the re-capture-DEFERRAL decision:
    # True means the pinned fixture still represents the true capability gap and a
    # re-capture should WAIT for the with-rails site to recover (the P2 canonical-
    # fixture item), NOT chase a dip. A FALSE POSITIVE wrongly FREEZES the fixture;
    # a false negative chases a transient. Both scenario tests above exercise only
    # the interior (with-rails softens / no-rails gains); the DivergenceCause
    # docstrings claim two credibility properties nothing pins at the EDGES:
    #   (i)  driver ties resolve to the no-rails floor, so an AMBIGUOUS move is read
    #        conservatively as gap movement, NEVER as reference degradation; and
    #   (ii) reference_degraded fires ONLY on a with-rails LOSS — the with-rails side
    #        GAINING (gap widening from the top) is not degradation even though it
    #        drives the move.
    # Pin them as a PROPERTY over directly-constructed causes (mirroring the
    # cause_verdict tests' construction), asserting semantics derived from first
    # principles — NOT a re-run of the SUT's own driver/degraded expression.
    def _sign(x: float) -> int:
        return (x > 0) - (x < 0)

    # (no_rails_change, with_rails_change) spanning every sign/magnitude regime,
    # INCLUDING exact ties (both signs) and single-side-flat moves.
    grid = [
        (0.0, -8.0),   # with-rails dominant LOSS   -> reference degraded
        (0.0,  8.0),   # with-rails dominant GAIN   -> NOT degraded (gap widens from top)
        (0.0, -3.0), (0.0, 3.0),
        (6.0,  0.0),   # no-rails dominant GAIN     -> gap closes from floor, NOT degraded
        (-6.0, 0.0),   # no-rails dominant LOSS     -> gap widens from floor, NOT degraded
        (-2.0, -9.0),  # with-rails dominant loss (both fall)    -> degraded
        (-9.0, -2.0),  # no-rails dominant loss                   -> NOT degraded
        (3.0, -1.0),   # no-rails gain dominant, with-rails dip   -> NOT degraded
        (-5.0, -5.0),  # TIE, both fall             -> no_rails driver, NOT degraded
        (5.0, -5.0),   # TIE, floor up / top down   -> AMBIGUOUS, NOT degraded
        (5.0,  5.0),   # TIE, both rise             -> NOT degraded
        (-5.0, 5.0),   # TIE, floor down / top up   -> NOT degraded
        (4.0,  4.0),
    ]
    degraded_seen = False
    for no_c, wr_c in grid:
        cause = ch.DivergenceCause(
            anchor_ts="20260101T000000Z", no_rails_change=no_c, with_rails_change=wr_c
        )
        tag = f"(no={no_c:+}, with={wr_c:+})"
        # gap_change is the delta move, coherent with the two component fields.
        _check(
            abs(cause.gap_change - round(wr_c - no_c, 4)) < 1e-9,
            f"{tag} gap_change == with_change - no_change",
        )
        _check(
            cause.driver in (ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS),
            f"{tag} driver is a reference host",
        )
        deg = cause.reference_degraded
        if deg:
            degraded_seen = True
            # A reference degradation is a coherent, DOMINANT with-rails LOSS that
            # NARROWS the gap — never anything else.
            _check(wr_c < 0, f"{tag} degraded => with-rails LOST ground")
            _check(abs(wr_c) > abs(no_c), f"{tag} degraded => with-rails move DOMINATES")
            _check(cause.gap_change < 0, f"{tag} degraded => gap NARROWED")
            _check(
                cause.driver == ch.CANONICAL_WITH_RAILS,
                f"{tag} degraded => with-rails is the driver",
            )
        # Conservatism: an AMBIGUOUS (equal-magnitude) move is never degradation.
        if abs(wr_c) == abs(no_c) and (no_c != 0.0 or wr_c != 0.0):
            _check(
                cause.driver == ch.CANONICAL_NO_RAILS,
                f"{tag} tie resolves to the no-rails floor (conservative)",
            )
            _check(deg is False, f"{tag} an ambiguous move is NOT reference degradation")
        # Strict-dominance sign invariant: when one side strictly dominates, the
        # driver's OWN direction fixes whether the gap narrows or widens (the
        # docstring's "sign(gap_change) is fixed by the driver's direction").
        if abs(wr_c) > abs(no_c):
            _check(
                _sign(cause.gap_change) == _sign(wr_c),
                f"{tag} with-rails driver: gap sign follows the with-rails move",
            )
        elif abs(no_c) > abs(wr_c):
            _check(
                _sign(cause.gap_change) == -_sign(no_c),
                f"{tag} no-rails driver: gap sign is the OPPOSITE of the floor move",
            )
    # Non-vacuity: the grid DOES contain genuine reference-degradation cases (else
    # every "degraded =>" clause above is vacuously satisfied).
    _check(degraded_seen, "grid exercises at least one real reference-degradation case")

    # TEETH — the two crisp edges the scenario tests miss, with exact expectations:
    # (A) with-rails GAINING dominant: driver IS with-rails and it drives the move,
    #     yet reference_degraded must stay False (the gap widened from the top).
    #     Drop the `with_rails_change < 0` guard and this flips True.
    widen = ch.DivergenceCause(anchor_ts="t", no_rails_change=0.0, with_rails_change=8.0)
    _check(widen.driver == ch.CANONICAL_WITH_RAILS, "with-rails gain is the driver")
    _check(abs(widen.gap_change - 8.0) < 1e-9, "gap widened +8.0")
    _check(
        widen.reference_degraded is False,
        "a with-rails GAIN widens the gap from the top — that is not degradation",
    )
    # (B) exact ambiguous tie (floor up, top down): equal magnitudes, so the move is
    #     unattributable to one side. Flip the driver tie-break to `>=` and this
    #     tie's with-rails drop would falsely read as reference degradation.
    ambiguous = ch.DivergenceCause(anchor_ts="t", no_rails_change=5.0, with_rails_change=-5.0)
    _check(ambiguous.driver == ch.CANONICAL_NO_RAILS, "the tie resolves to the no-rails floor")
    _check(
        ambiguous.reference_degraded is False,
        "an ambiguous tie is never read as reference degradation",
    )


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


def test_cause_verdict_flags_the_unattributed_tie() -> None:
    print("test_cause_verdict_flags_the_unattributed_tie")
    # READOUT (Cycle 220): DivergenceCause.driver tie-breaks an EQUAL-magnitude,
    # opposite-direction move to the no-rails floor by convention, not by evidence
    # (pinned by Cycle 219's grid). The driver-line prose keyed on that driver and
    # therefore SILENTLY reported such a tie as a confident "no-rails reference
    # GAINED capability — a real benchmark movement", hiding an equal-and-opposite
    # with-rails softening of the same magnitude. cause_verdict now detects the tie
    # (side_ambiguous) and states the gap move while calling the SIDE unattributed.

    # (1) The tie: no-rails +5.0, with-rails -5.0 -> gap NARROWED -10.0. Driver and
    #     reference_degraded are UNCHANGED (Cycle 219 semantics intact) — this is a
    #     READOUT change, not a recommendation change.
    tie = ch.DivergenceCause(anchor_ts="t", no_rails_change=5.0, with_rails_change=-5.0)
    _check(tie.side_ambiguous is True, "equal-and-opposite move is side_ambiguous")
    _check(tie.driver == ch.CANONICAL_NO_RAILS, "driver tie-break unchanged (no-rails)")
    _check(tie.reference_degraded is False, "reference_degraded stays conservative on a tie")
    verd = ch.cause_verdict(tie, None)
    _check("unattributed" in verd, f"prose calls the side unattributed, got: {verd}")
    _check("-10.0" in verd, f"prose states the gap move magnitude, got: {verd}")
    _check("narrowed" in verd, f"prose names the gap direction, got: {verd}")
    _check("tie" in verd, f"prose says it is a tie, got: {verd}")
    # The silent default it replaces MUST be gone.
    _check("GAINED capability" not in verd, f"no confident floor-gain claim on a tie, got: {verd}")
    _check("real benchmark movement" not in verd, "no movement-vs-outage claim on a tie")

    # (1b) A pillar mover on ONE side does not rescue attribution — the OVERALL tie
    #      means the side is unattributed regardless of any per-pillar signal, so the
    #      ambiguous prose fires (and ignores top) even when a top move is supplied.
    top = ch.PillarMove(ch.CANONICAL_WITH_RAILS, "transactability", 87.5, 82.5, -5.0)
    _check(ch.cause_verdict(tie, top) == verd, "a per-pillar top does not un-tie an overall tie")

    # (2) The OPPOSITE tie direction: no-rails -5.0, with-rails +5.0 -> gap WIDENED.
    tie_w = ch.DivergenceCause(anchor_ts="t", no_rails_change=-5.0, with_rails_change=5.0)
    _check(tie_w.side_ambiguous is True, "the mirror tie is also side_ambiguous")
    vw = ch.cause_verdict(tie_w, None)
    _check("widened" in vw and "+10.0" in vw, f"mirror tie names widen +10.0, got: {vw}")

    # (3) ROUNDING TOLERANCE: a tie equal to the scores' 1-decimal precision but off
    #     by float noise is still a tie, not a sub-rounding artifact that slips
    #     through to the confident prose.
    noisy = ch.DivergenceCause(anchor_ts="t", no_rails_change=5.1000000001, with_rails_change=-5.1)
    _check(noisy.side_ambiguous is True, "a sub-rounding float-noise tie still flags")

    # (4) TEETH — a STRICT-dominant no-rails GAIN is NOT a tie: side_ambiguous False,
    #     and the confident floor-gain prose the new branch could over-swallow is
    #     preserved verbatim. (Make the branch fire on this and a real attribution
    #     would be mis-reported as unattributed.)
    gain = ch.DivergenceCause(anchor_ts="t", no_rails_change=8.0, with_rails_change=0.0)
    _check(gain.side_ambiguous is False, "a dominant one-sided move is not a tie")
    gv = ch.cause_verdict(gain, None)
    _check("GAINED capability" in gv and "unattributed" not in gv,
           f"a real one-sided attribution keeps its confident prose, got: {gv}")

    # (5) EQUAL-and-SAME-SIGN is NOT ambiguous — the moves cancel to gap_change 0, so
    #     there is no divergence to attribute (not an ambiguous one).
    same = ch.DivergenceCause(anchor_ts="t", no_rails_change=5.0, with_rails_change=5.0)
    _check(abs(same.gap_change) < 1e-9, "equal-same-sign cancels to no gap move")
    _check(same.side_ambiguous is False, "no gap move is not an ambiguous attribution")

    # (6) HOST-RELABEL INVARIANCE: the ambiguous prose names the two hosts as DATA
    #     (the module constants), never a hardcoded vendor — byte-identical once the
    #     labels substitute back, the same invariant the four honest cases hold.
    orig_no, orig_with = ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS
    try:
        base = ch.cause_verdict(
            ch.DivergenceCause("t", no_rails_change=5.0, with_rails_change=-5.0), None
        )
        _check(orig_no in base and orig_with in base, "ambiguous prose names both hosts")
        ch.CANONICAL_NO_RAILS = "no-rails-store.example"
        ch.CANONICAL_WITH_RAILS = "with-rails-store.example"
        relabeled = ch.cause_verdict(
            ch.DivergenceCause("t", no_rails_change=5.0, with_rails_change=-5.0), None
        )
        _check(ch.CANONICAL_NO_RAILS in relabeled and ch.CANONICAL_WITH_RAILS in relabeled,
               "relabeled prose names the new hosts")
        subbed = relabeled.replace(ch.CANONICAL_NO_RAILS, orig_no).replace(
            ch.CANONICAL_WITH_RAILS, orig_with)
        _check(subbed == base, "ambiguous prose is a pure function of structure + host tokens")
    finally:
        ch.CANONICAL_NO_RAILS, ch.CANONICAL_WITH_RAILS = orig_no, orig_with


def test_cause_verdict_unattributed_tie_end_to_end_in_render() -> None:
    print("test_cause_verdict_unattributed_tie_end_to_end_in_render")
    # Integration: a full series whose LATEST reading is an equal-and-opposite
    # side tie must surface the unattributed wording in the terminal render's driver
    # line — confirming render threads side_ambiguous through, not just the unit. The
    # no-rails floor rises +5.0 while the with-rails reference falls -5.0 (gap 39.4 ->
    # 29.4): the confident "no-rails GAINED capability" reading would be exactly as
    # wrong as reading it as with-rails softening, so neither is asserted.
    org_p = {"access": 100.0, "legibility": 36.4, "transactability": 18.75, "trust": 60.0}
    com_p = {"access": 100.0, "legibility": 90.9, "transactability": 87.5, "trust": 60.0}
    org_up = {"access": 100.0, "legibility": 46.4, "transactability": 18.75, "trust": 60.0}
    com_dn = {"access": 100.0, "legibility": 90.9, "transactability": 62.5, "trust": 60.0}
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, org_pillars=org_p, com_pillars=com_p)
            for i in range(1, 5)
        ]
        rows += [
            _artifact("20260731T080000Z", 51.1, 80.5, 29.4, org_pillars=org_up, com_pillars=com_dn),
            _artifact("20260731T140000Z", 51.1, 80.5, 29.4, org_pillars=org_up, com_pillars=com_dn),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        cause = hist.divergence_cause
        _check(cause is not None and cause.side_ambiguous,
               f"loader builds an equal-and-opposite tie cause, got: {cause}")
        out = ch.render(hist)
        driver_lines = [l for l in out.splitlines() if l.startswith("driver:")]
        _check(len(driver_lines) == 1, f"render still names one driver line, got: {driver_lines}")
        _check("unattributed" in driver_lines[0],
               f"render's driver line calls the tie unattributed, got: {driver_lines[0]}")
        _check("GAINED capability" not in driver_lines[0],
               f"render does not present the tie as a confident floor gain, got: {driver_lines[0]}")


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


def test_drift_diagnostics_are_time_translation_invariant() -> None:
    print("test_drift_diagnostics_are_time_translation_invariant")
    # METAMORPHIC guard on a REPRODUCIBILITY property the whole drift-diagnostic
    # family rests on but no test pins: every verdict measures RELATIVE time
    # (durations, trailing-run ordering, freshness-vs-``now``), NEVER the absolute
    # epoch. So the SAME drift shape must yield the SAME diagnosis whether it happened
    # in July or the following January — a benchmark whose "sustained 18h softening"
    # verdict silently depended on the calendar (a hardcoded reference epoch, a
    # year-boundary bug in ``_parse_ts``/span arithmetic) would be irreproducible.
    # The transform: shift EVERY artifact timestamp — and the reference ``now`` — by
    # one fixed offset that crosses a month AND year boundary (Jul 2026 -> Jan 2027),
    # leaving the numeric trajectory untouched. Every STRUCTURAL diagnostic must be
    # byte-identical across the shift; only the ts LABELS (which are relative-time
    # anchors, not verdicts) may differ. Distinct from the reflection guard (which
    # transforms the SCORE axis to test direction-blindness): this transforms the TIME
    # axis to test epoch-blindness — the orthogonal metamorphic relation.
    org_p = {"access": 100.0, "legibility": 36.4, "transactability": 18.75, "trust": 60.0}
    com_anchor = {"access": 100.0, "legibility": 90.9, "transactability": 87.5, "trust": 60.0}
    com_drift = {"access": 100.0, "legibility": 90.9, "transactability": 62.5, "trust": 60.0}
    # 4 in-band anchors (deterministic noise floor) + a trailing run of 3 out-of-band
    # readings spanning ~18h (com transactability softens) so sustained-run,
    # attribution, stability, cause, re-capture AND liveness all fire.
    base = [
        _artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, org_pillars=org_p, com_pillars=com_anchor)
        for i in range(1, 5)
    ]
    base += [
        _artifact("20260731T080000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
        _artifact("20260731T140000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
        _artifact("20260801T020000Z", 46.1, 76.2, 30.1, org_pillars=org_p, com_pillars=com_drift),
    ]
    offset = timedelta(days=160, hours=3, minutes=17)  # crosses month + year boundary
    shifted = _time_translate(base, offset)
    now_b = datetime(2026, 8, 1, 3, 0, 0, tzinfo=timezone.utc)  # ~1h past the latest -> fresh
    now_s = now_b + offset
    with tempfile.TemporaryDirectory() as tb, tempfile.TemporaryDirectory() as ts:
        _write_series(tb, base)
        _write_series(ts, shifted)
        hb = ch.load_history(tb, now=now_b)
        hs = ch.load_history(ts, now=now_s)

    # sanity: the transform genuinely moved the calendar (different year), so this is
    # not comparing a series to itself; and every diagnostic actually fired (non-vacuous).
    _check(
        hb.latest.ts[:4] == "2026" and hs.latest.ts[:4] == "2027",
        f"the shift crossed the year boundary, got {hb.latest.ts} -> {hs.latest.ts}",
    )
    _check(hb.band != ch.BAND_IN, "base series is out of band (a real verdict to preserve)")
    _check(hb.attribution is not None and hb.attribution.top is not None, "attribution fired")
    _check(hb.attribution_stability is not None, "stability fired")
    _check(hb.noise_floor is not None and hb.noise_floor.deterministic, "noise floor fired")
    _check(hb.liveness is not None and hb.liveness.fresh, "liveness fired (fresh)")

    # (1) magnitude/ordering machinery — invariant.
    _check(hb.band == hs.band, f"band invariant, got {hb.band}/{hs.band}")
    _check(hb.divergence == hs.divergence, f"divergence invariant, got {hb.divergence}/{hs.divergence}")
    _check(
        hb.consecutive_out_of_band == hs.consecutive_out_of_band,
        f"out-of-band count invariant, got {hb.consecutive_out_of_band}/{hs.consecutive_out_of_band}",
    )
    _check(
        hb.sustained_run.span_hours == hs.sustained_run.span_hours,
        f"sustained-run SPAN invariant (a duration, not an epoch), got "
        f"{hb.sustained_run.span_hours}/{hs.sustained_run.span_hours}",
    )
    nb, ns = hb.noise_floor, hs.noise_floor
    _check(
        (nb.n_in_band, nb.stddev, nb.max_abs_divergence, nb.no_rails_stddev, nb.with_rails_stddev)
        == (ns.n_in_band, ns.stddev, ns.max_abs_divergence, ns.no_rails_stddev, ns.with_rails_stddev),
        "noise floor invariant (score-keyed, time-blind)",
    )

    # (2) attribution / stability / cause — the fingered pillar+side and signed moves
    # are functions of the SCORE series, not of when it was recorded.
    ab, as_ = hb.attribution, hs.attribution
    _check(
        (ab.top.domain, ab.top.pillar, ab.top.change) == (as_.top.domain, as_.top.pillar, as_.top.change),
        f"attribution top mover invariant, got {ab.top.domain}/{ab.top.pillar}/{ab.top.change}",
    )
    _check(
        [(m.domain, m.pillar, m.change) for m in ab.moves]
        == [(m.domain, m.pillar, m.change) for m in as_.moves],
        "full attribution move list invariant",
    )
    _check(
        hb.attribution_stability.stable == hs.attribution_stability.stable
        and hb.attribution_stability.fingered == hs.attribution_stability.fingered,
        "attribution stability (stable? / fingered pillar) invariant",
    )
    cb, cs = hb.divergence_cause, hs.divergence_cause
    _check(
        (cb.driver, cb.gap_change, cb.reference_degraded, cb.no_rails_change, cb.with_rails_change)
        == (cs.driver, cs.gap_change, cs.reference_degraded, cs.no_rails_change, cs.with_rails_change),
        "divergence cause (driver / direction / per-side change) invariant",
    )
    _check(
        hb.recapture.code == hs.recapture.code,
        f"re-capture recommendation invariant, got {hb.recapture.code}/{hs.recapture.code}",
    )

    # (3) liveness — age is measured against ``now``; shift BOTH the series and ``now``
    # by the same offset and the age (hence fresh/stale) is unchanged. THE control that
    # proves the invariance is non-trivial: liveness is the one time-DEPENDENT
    # diagnostic, yet it too is translation-invariant when its own clock moves with it.
    _check(
        hb.liveness.age_hours == hs.liveness.age_hours and hb.liveness.fresh == hs.liveness.fresh,
        f"liveness age/fresh invariant under co-translated clock, got "
        f"{hb.liveness.age_hours}/{hb.liveness.fresh} vs {hs.liveness.age_hours}/{hs.liveness.fresh}",
    )


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


def test_recapture_advice_flags_ambiguous_side_before_recapture() -> None:
    print("test_recapture_advice_flags_ambiguous_side_before_recapture")
    # METHOD (Cycle 221): the re-capture DECISION must not gamble on a coin-flip.
    # When the gap moves but BOTH references moved by EQUAL magnitude in opposite
    # directions (side_ambiguous), the overall scores cannot break which side drove
    # it: reading it as a no-rails FLOOR gain -> REC_RECAPTURE would re-pin the
    # baseline on a tie that is equally a with-rails SOFTENING (which -> REC_DEFER,
    # wait). The honest recommendation is a human look, NOT a confident re-capture
    # candidate. This is the decision-level sibling of the Cycle-220 cause_verdict
    # tie case: the same silent no-rails-floor default lived one function over, in
    # recapture_advice's REC_RECAPTURE fall-through, and drove the wrong action.
    with tempfile.TemporaryDirectory() as tmp:
        # 4 in-band anchors (delta 39.4), then a sustained out-of-band run whose
        # LATEST reading is an exact equal-and-opposite move vs the in-band anchor:
        # no-rails +4.0 / with-rails -4.0 (gap -8.0). The tie resolves driver to the
        # no-rails floor by CONVENTION, so reference_degraded is False and the old
        # fall-through mislabeled it a durable capability-gap change.
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 48.0, 83.6, 35.6),   # +1.9 / -1.9
            _artifact("20260727T060000Z", 49.0, 82.6, 33.6),   # +2.9 / -2.9
            _artifact("20260727T070000Z", 50.1, 81.5, 31.4),   # +4.0 / -4.0, 3rd in a row
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        cause = hist.divergence_cause
        _check(hist.consecutive_out_of_band == 3, "sustained out of band (>= _SUSTAINED_MIN)")
        _check(cause is not None and cause.side_ambiguous is True, "the latest move is an equal-and-opposite tie")
        _check(cause.reference_degraded is False, "a tie is not reference degradation (driver defaults to the floor)")
        _check(cause.driver == ch.CANONICAL_NO_RAILS, "the tie resolves the driver to the no-rails floor by convention")
        # THE DECISION: review-the-tie, NOT a confident re-capture candidate.
        _check(
            hist.recapture.code == ch.REC_AMBIGUOUS,
            f"ambiguous tie -> review (side unattributed), got {hist.recapture.code}",
        )
        _check(hist.recapture.code != ch.REC_RECAPTURE, "the coin-flip tie must NOT read as a durable baseline move")
        reason = hist.recapture.reason
        _check("unattributed" in reason and "tie" in reason, "the reason names the tie / unattributed side")
        # Vendor-neutral: the reason speaks in capability terms (no-rails / with-rails),
        # never a host string — so it is trivially host-relabel invariant.
        _check(
            ch.CANONICAL_NO_RAILS not in reason and ch.CANONICAL_WITH_RAILS not in reason,
            "the ambiguous-tie reason names no host, only the capability sides",
        )
        rendered = ch.render(hist)
        _check("review (side unattributed)" in rendered, "render surfaces the ambiguous-tie recommendation label")
        # TEETH: nudge the latest with-rails move to STRICTLY dominate (-4.1 vs +4.0)
        # and the tie breaks -> reference_degraded -> DEFER, never REC_AMBIGUOUS. This
        # confirms the branch keys on the genuine tie, not merely on being out of band.
        rows_strict = rows[:-1] + [_artifact("20260727T070000Z", 50.1, 81.4, 31.3)]
        with tempfile.TemporaryDirectory() as tmp2:
            _write_series(tmp2, rows_strict)
            hist2 = ch.load_history(tmp2)
        _check(hist2.divergence_cause.side_ambiguous is False, "a strictly dominant with-rails move is not a tie")
        _check(hist2.recapture.code == ch.REC_DEFER, f"strict with-rails softening -> defer, got {hist2.recapture.code}")


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
    # any out-of-band code never claims baseline-valid. Recovery-tolerant: the live
    # series currently sits OUT of band (the persistent Jul-31/Aug-1 with-rails
    # transactability softening), so this reads a non-VALID code today, but the
    # assertion holds whichever way the live series sits.
    hist = ch.load_history()
    adv = hist.recapture
    _check(adv is not None, "the real series gets a recommendation")
    _check(adv.code in ch._REC_LABEL, f"a known recommendation code, got {adv.code}")
    if hist.band == ch.BAND_IN:
        _check(adv.code == ch.REC_VALID, f"in-band real series -> baseline-valid, got {adv.code}")
    else:
        _check(adv.code != ch.REC_VALID, f"out-of-band real series is not baseline-valid, got {adv.code}")
    _check("re-capture:" in ch.render(hist), "the real render carries the recommendation line")


def test_real_series_defer_decision_is_corroborated_by_both_mechanisms() -> None:
    print("test_real_series_defer_decision_is_corroborated_by_both_mechanisms")
    # TRUTH (Cycle 207): the operator-facing re-capture DECISION on the REAL series,
    # and its TWO-MECHANISM corroboration, pinned as ONE fact — the piece neither
    # sibling guard makes alone.
    #
    # recapture_advice synthesizes its recommendation from the SIDE-level
    # divergence_cause ALONE (overall scores). On the current live series that
    # decision is DEFER: the with-rails reference SOFTENED, so the pinned fixture
    # still represents the true capability gap and a [LOCAL] re-capture must WAIT —
    # never chase the dip down. A wrong DEFER->RECAPTURE flip here would re-pin the
    # frozen baseline to a transient site regression, corrupting cross-version
    # comparability (the maintenance contract test_canonical_replay documents).
    #
    # The decision's TRUSTWORTHINESS rests on it not being a single-signal artifact:
    # the INDEPENDENT pillar-level attribution (_attribute, per-pillar scores) must
    # finger the SAME side softening the side-level cause (_cause, overalls) blames.
    # This guard ties the operator-facing DECISION to that convergence:
    #   - test_attribution_on_real_series_fingers_the_drifting_pillar asserts the
    #     convergence but NOT the recapture decision it should drive;
    #   - test_recapture_advice_on_real_series_is_coherent asserts the decision but
    #     only weakly (not-VALID) and does NOT tie it to the two-mechanism agreement.
    # Neither asserts "the DEFER an operator would ACT on is the one two independent
    # mechanisms support". That is this guard.
    #
    # Recovery-tolerant: if the site returns to in-band the decision is correctly
    # REC_VALID and the corroborated-DEFER claim is skipped; if it drifts out of band
    # but not yet sustained (or with no in-band anchor), the honest code is WAIT/
    # REVIEW — still non-VALID, and the corroborated-DEFER claim applies only once the
    # move is sustained with an anchor, the same discipline as the sibling guards.
    hist = ch.load_history()
    adv = hist.recapture
    _check(adv is not None, "the real series gets a recommendation")
    if hist.band == ch.BAND_IN:
        _check(adv.code == ch.REC_VALID, f"in-band real series -> baseline-valid, got {adv.code}")
        return
    if hist.consecutive_out_of_band < ch._SUSTAINED_MIN or hist.divergence_cause is None:
        # out of band but not a sustained, anchored move -> WAIT or REVIEW, never a
        # blind DEFER/RECAPTURE and never baseline-valid.
        _check(
            adv.code in (ch.REC_WAIT, ch.REC_REVIEW),
            f"out-of-band-but-not-sustained/anchorless -> wait/review, got {adv.code}",
        )
        return
    # Sustained out of band WITH an in-band anchor: the decision is DEFER (reference
    # softened) or RECAPTURE (baseline genuinely moved). On the current live series it
    # is DEFER, and BOTH independent mechanisms must corroborate the with-rails softening.
    cause = hist.divergence_cause
    _check(
        cause.reference_degraded is True,
        "the current live drift is with-rails reference softening (not the floor rising)",
    )
    _check(
        adv.code == ch.REC_DEFER,
        f"reference-softening real series -> defer, got {adv.code}",
    )
    # Independent corroboration: the pillar mechanism must finger the SAME side.
    _check(hist.attribution is not None, "a sustained, anchored drift isolates a pillar mover")
    top = hist.attribution.top
    _check(top is not None, "the drift isolates a top pillar mover")
    _check(
        top.domain == cause.driver == ch.CANONICAL_WITH_RAILS,
        f"side cause ({cause.driver}) and pillar attribution ({top.domain}) must BOTH "
        f"finger the with-rails reference, or the DEFER is single-signal",
    )
    _check(
        top.change < 0,
        f"a corroborated reference softening must be a pillar DROP, got {top.change:+}",
    )
    # The operator-facing block surfaces the DEFER decision the two mechanisms support.
    out = ch.render(hist)
    _check("defer re-capture" in out, "render surfaces the defer decision to the operator")


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


def test_decision_corroboration_agrees_disagrees_and_none() -> None:
    print("test_decision_corroboration_agrees_disagrees_and_none")
    # READOUT (Cycle 208): the re-capture DECISION's TWO-MECHANISM corroboration is
    # now an explicit, computed readout fact — does the SIDE-level cause (overalls,
    # what recapture_advice keys on) and the INDEPENDENT pillar-level attribution
    # (per-pillar scores) finger the SAME side moving the SAME way? The operator sees
    # WHY a defer/re-capture holds — two independent decompositions concurring, not
    # one number. Cycle 207 pinned that convergence INTERNALLY; this pins that it is
    # SURFACED, and — non-vacuously — that a genuine DISAGREEMENT is reported as such,
    # not papered over. The verify artifact carries `overall` and `pillars` as
    # independent fields, so a disagreement can be constructed by moving one without
    # the other (a synthetic probe of the readout, never a real scored state).
    anchor = dict(
        org_pillars={"transactability": 18.75, "legibility": 36.4},
        com_pillars={"transactability": 87.5, "legibility": 90.9},
    )

    # (a) CORROBORATED: with-rails overall falls AND its transactability pillar falls
    #     (the load-bearing 2026-07-27 real-drift shape) -> both mechanisms finger the
    #     with-rails side going down.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, **anchor) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 80.0, 33.9,
                      org_pillars=anchor["org_pillars"],
                      com_pillars={"transactability": 75.0, "legibility": 90.9}),
            _artifact("20260727T060000Z", 46.1, 78.7, 32.6,
                      org_pillars=anchor["org_pillars"],
                      com_pillars={"transactability": 62.5, "legibility": 90.9}),
            _artifact("20260727T070000Z", 46.1, 76.2, 30.1,
                      org_pillars=anchor["org_pillars"],
                      com_pillars={"transactability": 62.5, "legibility": 90.9}),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        corr = hist.corroboration
        _check(corr is not None, "sustained anchored drift with an isolated pillar -> a corroboration")
        _check(corr.driver == ch.CANONICAL_WITH_RAILS, f"side cause drives with-rails, got {corr.driver}")
        _check(corr.pillar_domain == ch.CANONICAL_WITH_RAILS, f"pillar mover on with-rails, got {corr.pillar_domain}")
        _check(corr.pillar == "transactability", f"the moving pillar is transactability, got {corr.pillar}")
        _check(corr.same_side is True, "both mechanisms finger the same side")
        _check(corr.same_direction is True, "both point the same way (down)")
        _check(corr.corroborated is True, "-> CORROBORATED")
        out = ch.render(hist)
        _check("corroboration:" in out, "render surfaces a corroboration line")
        _check("CORROBORATED" in out, "render names the decision corroborated")
        _check(hist.recapture.code == ch.REC_DEFER, f"the decision it backs is defer, got {hist.recapture.code}")

    # (b) NON-VACUOUS side disagreement: the with-rails OVERALL falls (side driver =
    #     with-rails) but the largest PILLAR move is on the no-rails side (its
    #     transactability jumps while its overall stays flat). The two mechanisms
    #     disagree on the driver -> NOT corroborated. A readout blind to this would
    #     mis-sell a single-signal decision as two-mechanism-backed.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, **anchor) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 80.0, 33.9,
                      org_pillars={"transactability": 55.0, "legibility": 36.4},
                      com_pillars=anchor["com_pillars"]),
            _artifact("20260727T060000Z", 46.1, 79.0, 32.9,
                      org_pillars={"transactability": 60.0, "legibility": 36.4},
                      com_pillars=anchor["com_pillars"]),
            _artifact("20260727T070000Z", 46.1, 78.7, 32.6,
                      org_pillars={"transactability": 60.0, "legibility": 36.4},
                      com_pillars=anchor["com_pillars"]),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        corr = hist.corroboration
        _check(corr is not None, "still a corroboration object (both mechanisms present)")
        _check(corr.driver == ch.CANONICAL_WITH_RAILS, f"side driver with-rails (its overall fell), got {corr.driver}")
        _check(corr.pillar_domain == ch.CANONICAL_NO_RAILS, f"pillar mover on no-rails, got {corr.pillar_domain}")
        _check(corr.same_side is False, "the two mechanisms disagree on the side")
        _check(corr.corroborated is False, "-> NOT corroborated")
        out = ch.render(hist)
        _check("NOT corroborated" in out, "render reports the disagreement honestly")

    # (c) NON-VACUOUS direction disagreement: with-rails drives both (its overall
    #     falls, its pillar is the largest mover) but the pillar RISES while the
    #     overall falls -> same side, opposite direction -> NOT corroborated.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, **anchor) for i in range(1, 5)]
        rows += [
            _artifact("20260727T050000Z", 46.1, 80.0, 33.9,
                      org_pillars=anchor["org_pillars"],
                      com_pillars={"transactability": 95.0, "legibility": 90.9}),
            _artifact("20260727T060000Z", 46.1, 79.0, 32.9,
                      org_pillars=anchor["org_pillars"],
                      com_pillars={"transactability": 99.0, "legibility": 90.9}),
            _artifact("20260727T070000Z", 46.1, 78.7, 32.6,
                      org_pillars=anchor["org_pillars"],
                      com_pillars={"transactability": 99.0, "legibility": 90.9}),
        ]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        corr = hist.corroboration
        _check(corr.same_side is True, "same side drives both (with-rails)")
        _check(corr.same_direction is False, "overall fell but the pillar rose -> opposite directions")
        _check(corr.corroborated is False, "-> NOT corroborated")

    # (d) None when in-band: no divergence cause, so nothing to corroborate — never a
    #     fabricated corroboration claim, and the render carries no corroboration line.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [_artifact(f"20260727T0{i}0000Z", 46.1, 85.5, 39.4, **anchor) for i in range(1, 5)]
        _write_series(tmp, rows)
        hist = ch.load_history(tmp)
        _check(hist.band == ch.BAND_IN, "the flat series is in-band")
        _check(hist.corroboration is None, "in-band -> no corroboration claim")
        _check("corroboration:" not in ch.render(hist), "render omits the corroboration line in-band")


def test_decision_corroboration_on_real_series_is_coherent() -> None:
    print("test_decision_corroboration_on_real_series_is_coherent")
    # End-to-end on the REAL committed series, recovery-tolerant: when the live drift
    # is a sustained, anchored, single-pillar move, the corroboration object must be
    # present and MUST agree with the primitives it reads (its driver == the side
    # cause's driver, its pillar side == the attribution top's side) and the render
    # must surface the line. If the site recovered to in-band (or no pillar isolated),
    # the honest state is no-corroboration and the claim is correctly skipped.
    hist = ch.load_history()
    corr = hist.corroboration
    if (
        hist.band == ch.BAND_IN
        or hist.divergence_cause is None
        or hist.attribution is None
        or hist.attribution.top is None
    ):
        _check(corr is None, "no both-mechanism state -> no corroboration claim")
        return
    _check(corr is not None, "out-of-band anchored drift with an isolated pillar gets a corroboration")
    _check(corr.driver == hist.divergence_cause.driver, "corroboration driver == side cause driver")
    _check(
        corr.pillar_domain == hist.attribution.top.domain,
        "corroboration pillar side == attribution top side",
    )
    _check(corr.pillar_change == hist.attribution.top.change, "corroboration reads the top mover's change")
    _check("corroboration:" in ch.render(hist), "the real render carries the corroboration line")


def test_corroboration_verdict_word_is_coupled_to_the_boolean() -> None:
    print("test_corroboration_verdict_word_is_coupled_to_the_boolean")
    # METHOD (Cycle 209): the PROSE CANNOT LIE. `corroboration_verdict` renders the
    # operator-facing CORROBORATED / NOT-corroborated word, and `recapture_advice`'s
    # trustworthiness for the operator rests on that word matching the computed fact
    # `corr.corroborated`. Cycle 207 pinned the convergence internally and Cycle 208
    # surfaced it, but nothing tied the WORD to the BOOLEAN: an edit that emitted
    # "CORROBORATED" from a not-corroborated branch (or the reverse) would mis-sell a
    # single-signal decision as two-mechanism-backed and pass every existing guard
    # (they exercise real histories, never the verdict function across its input
    # space). This pins the coupling over the FULL (same_side, same_direction) truth
    # table, constructing DecisionCorroboration directly so no real scored state is
    # implied — a pure probe of the readout word.
    WR, NR = ch.CANONICAL_WITH_RAILS, ch.CANONICAL_NO_RAILS

    def _corr(same_side: bool, same_direction: bool, *, driver: str, other: str):
        # driver overall always falls (-9.3, the real 2026-07-27 drift sign); the
        # pillar mover sits on the driver's side iff same_side, and moves the same
        # way (down) iff same_direction — so corroborated == same_side and same_dir.
        return ch.DecisionCorroboration(
            driver=driver,
            driver_change=-9.3,
            pillar_domain=(driver if same_side else other),
            pillar="transactability",
            pillar_change=(-25.0 if same_direction else +25.0),
        )

    combos = [(True, True), (True, False), (False, True), (False, False)]
    # non-vacuity: the truth table has exactly one corroborated corner and three not.
    corroborated_count = 0
    for same_side, same_dir in combos:
        corr = _corr(same_side, same_dir, driver=WR, other=NR)
        _check(corr.same_side is same_side, f"same_side wired as intended ({same_side})")
        _check(corr.same_direction is same_dir, f"same_direction wired as intended ({same_dir})")
        _check(
            corr.corroborated is (same_side and same_dir),
            f"corroborated == same_side and same_direction ({same_side},{same_dir})",
        )
        verdict = ch.corroboration_verdict(corr)
        # THE COUPLING: the leading word is exactly one of the two forms, and which one
        # is fixed by the boolean — startswith("CORROBORATED") iff corroborated,
        # startswith("NOT corroborated") iff not. ("NOT corroborated" begins with "NOT",
        # so the uppercase-word test cleanly discriminates the two.)
        _check(
            verdict.startswith("CORROBORATED") is corr.corroborated,
            f"the CORROBORATED word appears iff corroborated ({same_side},{same_dir}): {verdict!r}",
        )
        _check(
            verdict.startswith("NOT corroborated") is (not corr.corroborated),
            f"the NOT-corroborated word appears iff not corroborated ({same_side},{same_dir}): {verdict!r}",
        )
        # the advisory POSTURE is coupled the same way: a not-corroborated verdict warns
        # the operator to weigh the recommendation with caution; a corroborated one says
        # the decision rests on two independent signals. Neither posture may cross over.
        _check(
            ("weigh the recommendation with caution" in verdict) is (not corr.corroborated),
            f"the caution advisory appears iff not corroborated: {verdict!r}",
        )
        _check(
            ("two independent signals concurring" in verdict) is corr.corroborated,
            f"the two-signals assurance appears iff corroborated: {verdict!r}",
        )
        corroborated_count += int(corr.corroborated)
    _check(corroborated_count == 1, f"exactly one truth-table corner corroborates, got {corroborated_count}")

    # vendor-neutrality: the verdict keys on whether the two mechanisms' SIDES match,
    # never on host identity. Swap the reference pair's roles (driver drawn from the
    # no-rails constant, other from with-rails) and the word for each structurally
    # identical combo is unchanged — only the named domain differs, and both branches
    # of the coupling still hold. A regression that special-cased a host would break
    # this without touching the same-pair test above.
    for same_side, same_dir in combos:
        base = ch.corroboration_verdict(_corr(same_side, same_dir, driver=WR, other=NR))
        swapped = ch.corroboration_verdict(_corr(same_side, same_dir, driver=NR, other=WR))
        _check(
            base.startswith("CORROBORATED") == swapped.startswith("CORROBORATED"),
            f"the CORROBORATED word is host-relabel invariant ({same_side},{same_dir})",
        )
        _check(
            base.startswith("NOT corroborated") == swapped.startswith("NOT corroborated"),
            f"the NOT-corroborated word is host-relabel invariant ({same_side},{same_dir})",
        )


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


def test_pillar_noise_floor_is_deterministic_on_the_fingered_pillar_real_series() -> None:
    print("test_pillar_noise_floor_is_deterministic_on_the_fingered_pillar_real_series")
    # The pillar-granularity counterpart of the overall-delta signal proof
    # (test_band_clears_the_observed_noise). The overall noise floor proves the DELTA
    # is deterministic at rest; the drift we ATTRIBUTE is at the PILLAR level
    # (driftflight.com transactability −25). This pins that the fingered pillar is
    # ALSO deterministic at rest, so the tracked move is signal, not pillar jitter.
    hist = ch.load_history()
    # Guarded for recovery (matching the sibling real-series tests, e.g. the
    # attribution-agreement and stability guards): once the tracked drift RESOLVES
    # and the live series returns in-band, attribution is correctly None and there
    # is no fingered mover to measure a noise floor against — skip, don't assert an
    # active drift. (The Cycle-235/236 x402 proxy-discovery probe fix restored
    # driftflight.com to +39.4, resolving the Jul-31 transactability drop this test
    # was written against; the synthetic-jitter counterpart below keeps the pillar
    # noise-floor machinery under test unconditionally.)
    if hist.band == ch.BAND_IN or hist.attribution is None:
        _check(True, "live series is in-band -> no fingered mover to measure (site recovered)")
        return
    top = hist.attribution.top
    _check(top is not None, "the real series fingers a top pillar mover to measure against")
    pnf = hist.attributed_pillar_noise_floor
    _check(pnf is not None, "the fingered pillar has >= 2 in-band numeric readings -> a floor")
    # the floor measures the SAME (domain, pillar) attribution fingers
    _check(
        (pnf.domain, pnf.pillar) == (top.domain, top.pillar),
        f"the pillar floor measures the fingered mover {top.domain}/{top.pillar}, "
        f"got {pnf.domain}/{pnf.pillar}",
    )
    _check(pnf.n_in_band >= 2, f"measured over the in-band readings, got {pnf.n_in_band}")
    _check(pnf.stddev == 0.0, f"the fingered pillar is deterministic at rest (σ=0), got {pnf.stddev}")
    _check(pnf.max_abs_divergence == 0.0, f"worst at-rest |div| is 0, got {pnf.max_abs_divergence}")
    _check(pnf.deterministic is True, "the fingered pillar reproduces its value exactly at rest")
    # SIGNAL, not jitter: the tracked move dwarfs the pillar noise floor — the
    # pillar-level mirror of the overall OOB-transient-above-noise proof.
    _check(
        abs(top.change) > pnf.max_abs_divergence,
        f"tracked move |{top.change}| is above the pillar noise floor {pnf.max_abs_divergence}",
    )
    _check(
        abs(top.change) >= 20.0,
        f"the fingered move is large ({top.change}) — a check-scale drop, not sub-point jitter",
    )


def test_pillar_noise_floor_measures_synthetic_pillar_jitter() -> None:
    print("test_pillar_noise_floor_measures_synthetic_pillar_jitter")
    # NON-VACUOUS: the measure is NOT hard-coded to 0. A series whose in-band readings
    # keep the DELTA constant (both overalls flat) but whose driftflight.com
    # transactability pillar genuinely VARIES must report a positive stddev, a matching
    # worst |div|, and deterministic=False — the pillar jitter the overall floor,
    # blind to pillars, cannot see.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4, org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9, transactability=87.5)),
            _artifact("20260727T020000Z", 46.1, 85.5, 39.4, org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9, transactability=88.5)),
            _artifact("20260727T030000Z", 46.1, 85.5, 39.4, org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9, transactability=86.5)),
        ]
        _write_series(tmp, rows)
        points = ch.load_history(tmp).points
        pnf = ch.pillar_noise_floor(points, ch.CANONICAL_WITH_RAILS, "transactability")
        _check(pnf is not None, "three in-band readings carry the pillar -> a floor")
        _check(pnf.n_in_band == 3, f"all three are in-band, got {pnf.n_in_band}")
        _check(pnf.stddev > 0.0, f"varying in-band pillar -> positive dispersion, got {pnf.stddev}")
        _check(abs(pnf.max_abs_divergence - 1.0) < 1e-6, f"worst |div| about the mean is 1.0, got {pnf.max_abs_divergence}")
        _check(pnf.deterministic is False, "measurable pillar dispersion -> not deterministic")


def test_pillar_noise_floor_honest_none() -> None:
    print("test_pillar_noise_floor_honest_none")
    # Honest None on the same conditions noise_floor follows, plus the pillar-specific
    # ones: an unknown domain, and a pillar with < 2 in-band NUMERIC readings.
    with tempfile.TemporaryDirectory() as tmp:
        rows = [
            _artifact("20260727T010000Z", 46.1, 85.5, 39.4, org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9)),
            _artifact("20260727T020000Z", 46.1, 85.5, 39.4, org_pillars=_org_pillars(), com_pillars=_com_pillars(90.9)),
        ]
        _write_series(tmp, rows)
        points = ch.load_history(tmp).points
        _check(
            ch.pillar_noise_floor(points, "nobody.example", "transactability") is None,
            "an unknown domain has no side to measure -> None",
        )
        # a pillar unobserved on this side (outcome is None in _com_pillars) -> no
        # numeric in-band readings -> None (never counted as a zero).
        _check(
            ch.pillar_noise_floor(points, ch.CANONICAL_WITH_RAILS, "outcome") is None,
            "a pillar that is None on every reading has no numeric floor -> None",
        )
    # a lone in-band numeric reading is < 2 -> undefined dispersion -> None
    with tempfile.TemporaryDirectory() as tmp2:
        _write_series(tmp2, [_artifact("20260727T010000Z", 46.1, 85.5, 39.4, com_pillars=_com_pillars(90.9))])
        _check(
            ch.pillar_noise_floor(ch.load_history(tmp2).points, ch.CANONICAL_WITH_RAILS, "transactability") is None,
            "a single in-band reading -> no dispersion, None",
        )


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
        pnf = hist.attributed_pillar_noise_floor
        _check(hist.band != ch.BAND_IN, "the fixture series is out of band")
        _check(sr is not None and sr.span_hours > 0, "a sustained run with a real span fired")
        _check(nf is not None and nf.deterministic, "the at-rest noise floor is deterministic")
        _check(attr is not None and attr.top is not None, "pillar attribution isolated a top mover")
        _check(stab is not None, "attribution stability is measurable")
        _check(cause is not None, "a side/direction cause fired")
        _check(adv is not None and adv.code != ch.REC_NO_DATA, "a re-capture recommendation fired")
        _check(pnf is not None and pnf.deterministic,
               "the attributed pillar's at-rest noise floor is deterministic")

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
            ("attributed-pillar at-rest determinism", "signal, not pillar jitter"),
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
        test_loader_skips_a_reading_from_a_red_bench,
        test_real_committed_series_is_all_green_bench,
        test_load_accounting_counts_exclusions_by_reason,
        test_load_accounting_clean_series_reports_zero_excluded,
        test_render_names_exclusion_accounting_when_filtered,
        test_series_integrity_intact_within_floor,
        test_series_integrity_degraded_past_floor,
        test_series_integrity_none_without_accounting_or_artifacts,
        test_series_integrity_on_real_series_is_intact,
        test_render_names_series_integrity_when_filtered,
        test_render_empty_series_names_all_excluded,
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
        test_reference_degraded_is_conservative_across_the_full_driver_grid,
        test_cause_verdict_names_the_pillar_on_cross_mechanism_agreement,
        test_cause_verdict_flags_the_unattributed_tie,
        test_cause_verdict_unattributed_tie_end_to_end_in_render,
        test_cause_verdict_pillar_named_end_to_end_in_render,
        test_cause_verdict_prose_is_host_relabel_invariant,
        test_reflection_about_baseline_is_magnitude_invariant_direction_covariant,
        test_drift_diagnostics_are_time_translation_invariant,
        test_recapture_advice_baseline_valid_when_in_band,
        test_recapture_advice_waits_when_not_yet_sustained,
        test_recapture_advice_defers_on_reference_softening,
        test_recapture_advice_recommends_recapture_when_baseline_moved,
        test_recapture_advice_flags_ambiguous_side_before_recapture,
        test_recapture_advice_reviews_when_no_anchor,
        test_recapture_advice_on_real_series_is_coherent,
        test_real_series_defer_decision_is_corroborated_by_both_mechanisms,
        test_decision_corroboration_agrees_disagrees_and_none,
        test_decision_corroboration_on_real_series_is_coherent,
        test_corroboration_verdict_word_is_coupled_to_the_boolean,
        test_recapture_advice_prose_is_host_relabel_invariant,
        test_noise_floor_is_deterministic_on_real_series,
        test_noise_floor_sides_are_deterministic_on_real_series,
        test_noise_floor_sides_catch_a_cancelling_drift_the_delta_misses,
        test_band_clears_the_observed_noise_and_the_real_transients_are_signal,
        test_noise_floor_measures_synthetic_jitter,
        test_noise_floor_flags_a_too_tight_band,
        test_noise_floor_none_below_two_in_band,
        test_pillar_noise_floor_is_deterministic_on_the_fingered_pillar_real_series,
        test_pillar_noise_floor_measures_synthetic_pillar_jitter,
        test_pillar_noise_floor_honest_none,
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
