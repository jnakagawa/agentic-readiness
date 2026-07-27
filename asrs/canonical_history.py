"""Canonical-pair delta HISTORY — a READOUT over the committed live-verify series.

The local companion runner (``loop/local_verify.py``, hourly on Jonah's machine)
pushes ``runs/local/verify_<ts>.json`` to main every fire: a live static re-score
of the benchmark's own reference pair (drift-flight.org, no agent-native rails, vs
driftflight.com, with rails). Those artifacts are committed, so the series is a
real, growing time-series of the canonical delta.

This module reads that committed series and surfaces the delta TREND plus a
sustained-drift alert: when the LIVE delta diverges from the committed-fixture
baseline the in-cloud replay guard pins (``fixtures/canonical/*`` ->
``EXPECTED_DELTA`` +39.4 in ``tests/test_canonical_replay.py``), is it a one-off
blip (live/static jitter) or a sustained move (the real-world site changed under
the benchmark)? A single reading can't tell them apart; N consecutive out-of-band
readings can.

Read-only diagnostic: imports no scoring code, moves no score, touches no rubric.
The reference-pair host names appear here only as DATA (the series is *about* those
two domains, exactly as the committed fixtures and ``test_canonical_replay`` name
them) — never as scored-check wording.
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field

# The committed-fixture canonical delta the in-cloud replay guard pins
# (driftflight.com rails - drift-flight.org no-rails). Kept as a plain constant
# for a dependency-free readout; tests/test_canonical_history.py cross-checks it
# against the live fixture replay (test_canonical_replay.EXPECTED_DELTA) so it
# CANNOT silently drift — if a version bump legitimately re-captures the fixtures
# and moves the delta, that cross-check goes red, the same maintenance contract
# test_canonical_replay documents.
FIXTURE_BASELINE_DELTA = 39.4

CANONICAL_NO_RAILS = "drift-flight.org"
CANONICAL_WITH_RAILS = "driftflight.com"

# Divergence bands on abs(live_delta - baseline_delta), in overall-score points.
# in-band  : within ordinary static/live jitter of the pinned delta
# drifting : a notable but partial move (one pillar softened, or mid-deploy)
# diverged : a large move — the reference pair no longer reproduces the delta live
_BAND_IN = 2.0
_BAND_DRIFT = 8.0

BAND_NO_DATA = "no-data"
BAND_IN = "in-band"
BAND_DRIFTING = "drifting"
BAND_DIVERGED = "diverged"

_SPARK = "▁▂▃▄▅▆▇█"


@dataclass
class CanonicalPoint:
    """One live re-score of the reference pair, from a verify_<ts>.json artifact."""

    ts: str
    no_rails_overall: float
    no_rails_grade: str
    with_rails_overall: float
    with_rails_grade: str
    delta: float  # with_rails - no_rails, as recorded by the runner


@dataclass
class CanonicalHistory:
    points: list[CanonicalPoint] = field(default_factory=list)
    baseline_delta: float = FIXTURE_BASELINE_DELTA
    latest: CanonicalPoint | None = None
    divergence: float | None = None  # latest.delta - baseline_delta (signed)
    band: str = BAND_NO_DATA
    # trailing run of readings whose |delta - baseline| exceeds the in-band
    # threshold — 1 reading is jitter, N>=3 is a sustained real-world move.
    consecutive_out_of_band: int = 0


def _band_for(abs_divergence: float) -> str:
    if abs_divergence <= _BAND_IN:
        return BAND_IN
    if abs_divergence <= _BAND_DRIFT:
        return BAND_DRIFTING
    return BAND_DIVERGED


def _repo_root() -> str:
    # This module lives INSIDE the repo (asrs/), so deriving the root from
    # __file__ is safe here — unlike the pinned local runner, which lives
    # outside the checkout and must read ASRS_REPO (playbook self-healing law).
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _point_from_artifact(obj: dict) -> CanonicalPoint | None:
    """Parse one verify artifact into a CanonicalPoint, or None if unusable.

    Early artifacts (pre-Cycle-13, before the stderr-leak fix) recorded a
    FileNotFoundError instead of a score and carry no top-level ``delta``; those
    are skipped rather than scored as a zero — attribution honesty applies to the
    history readout too (a run we couldn't observe is not a data point).
    """
    ts = obj.get("ts")
    scores = obj.get("scores")
    delta = obj.get("delta")
    if not ts or not isinstance(scores, dict) or not isinstance(delta, (int, float)):
        return None
    no_rails = scores.get(CANONICAL_NO_RAILS)
    with_rails = scores.get(CANONICAL_WITH_RAILS)
    if not isinstance(no_rails, dict) or not isinstance(with_rails, dict):
        return None
    if not (no_rails.get("ok") and with_rails.get("ok")):
        return None
    no_o = no_rails.get("overall")
    with_o = with_rails.get("overall")
    if not isinstance(no_o, (int, float)) or not isinstance(with_o, (int, float)):
        return None
    return CanonicalPoint(
        ts=ts,
        no_rails_overall=float(no_o),
        no_rails_grade=str(no_rails.get("grade", "?")),
        with_rails_overall=float(with_o),
        with_rails_grade=str(with_rails.get("grade", "?")),
        delta=float(delta),
    )


def load_points(runs_dir: str | None = None) -> list[CanonicalPoint]:
    """Load every usable verify artifact as a CanonicalPoint, ordered by ts."""
    if runs_dir is None:
        runs_dir = os.path.join(_repo_root(), "runs", "local")
    points: list[CanonicalPoint] = []
    for path in sorted(glob.glob(os.path.join(runs_dir, "verify_*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                obj = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        pt = _point_from_artifact(obj)
        if pt is not None:
            points.append(pt)
    points.sort(key=lambda p: p.ts)
    return points


def summarize(
    points: list[CanonicalPoint], baseline_delta: float = FIXTURE_BASELINE_DELTA
) -> CanonicalHistory:
    """Roll a point series up into a CanonicalHistory (latest + drift verdict)."""
    hist = CanonicalHistory(points=list(points), baseline_delta=baseline_delta)
    if not points:
        return hist
    latest = points[-1]
    hist.latest = latest
    hist.divergence = round(latest.delta - baseline_delta, 4)
    hist.band = _band_for(abs(hist.divergence))
    run = 0
    for pt in reversed(points):
        if abs(pt.delta - baseline_delta) > _BAND_IN:
            run += 1
        else:
            break
    hist.consecutive_out_of_band = run
    return hist


def load_history(runs_dir: str | None = None) -> CanonicalHistory:
    return summarize(load_points(runs_dir))


def _spark(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return _SPARK[0] * len(values)
    span = hi - lo
    out = []
    for v in values:
        idx = int((v - lo) / span * (len(_SPARK) - 1) + 0.5)
        out.append(_SPARK[idx])
    return "".join(out)


_BAND_VERDICT = {
    BAND_NO_DATA: "no live re-scores recorded yet",
    BAND_IN: "live delta reproduces the pinned fixture delta (within jitter)",
    BAND_DRIFTING: "live delta has moved off the pinned fixture delta — notable but partial",
    BAND_DIVERGED: "live delta no longer reproduces the pinned fixture delta",
}


def _short_ts(ts: str) -> str:
    # 20260727T134147Z -> 2026-07-27T13:41Z
    if len(ts) >= 13 and ts[8] == "T":
        return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}T{ts[9:11]}:{ts[11:13]}Z"
    return ts


def _fmt_delta(d: float) -> str:
    return f"{d:+.1f}"


def render(history: CanonicalHistory, window: int = 24) -> str:
    """Render the history as a terminal block."""
    lines = ["CANONICAL DELTA HISTORY", "-" * 23]
    pts = history.points
    if not pts:
        lines.append("(no usable live-verify artifacts found)")
        return "\n".join(lines)
    lines.append(
        f"series: {len(pts)} live re-scores  "
        f"{_short_ts(pts[0].ts)} → {_short_ts(pts[-1].ts)}"
    )
    lines.append(
        f"baseline (committed fixtures): {_fmt_delta(history.baseline_delta)}  "
        f"[{CANONICAL_NO_RAILS} no-rails vs {CANONICAL_WITH_RAILS} rails]"
    )
    latest = history.latest
    assert latest is not None
    lines.append(
        f"latest: {_short_ts(latest.ts)}   "
        f"{CANONICAL_NO_RAILS} {latest.no_rails_overall:.1f} {latest.no_rails_grade}  |  "
        f"{CANONICAL_WITH_RAILS} {latest.with_rails_overall:.1f} {latest.with_rails_grade}  |  "
        f"delta {_fmt_delta(latest.delta)}"
    )
    div = history.divergence
    lines.append(
        f"divergence from baseline: {_fmt_delta(div)}  "
        f"({history.band.upper()} — {_BAND_VERDICT[history.band]})"
    )
    if history.consecutive_out_of_band >= 1:
        n = history.consecutive_out_of_band
        kind = "sustained" if n >= 3 else "recent"
        lines.append(
            f"{kind}: {n} consecutive re-score(s) out of band "
            f"(|delta - baseline| > {_BAND_IN:.1f})"
        )
    tail = pts[-window:]
    lines.append(
        f"delta trend (last {len(tail)}): {_spark([p.delta for p in tail])}"
    )
    return "\n".join(lines)
