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


# A per-pillar move smaller than this (in pillar-score points, 0–100) is treated
# as noise and not reported as a "mover" — keeps the attribution to the pillar(s)
# that actually shifted, not float dust. Pillar overalls are exact renormalized
# ratios, so real moves are many points; this only filters exact-0.0 no-movers.
_PILLAR_MOVE_EPS = 0.1


@dataclass
class CanonicalPoint:
    """One live re-score of the reference pair, from a verify_<ts>.json artifact."""

    ts: str
    no_rails_overall: float
    no_rails_grade: str
    with_rails_overall: float
    with_rails_grade: str
    delta: float  # with_rails - no_rails, as recorded by the runner
    # Per-pillar overalls (0–100) for each side, NUMERIC entries only — a pillar
    # recorded None (unobserved: outcome in static, or a pillar that CANT_TEST on
    # an error crawl) is dropped, never attributed a move. Empty on pre-pillar
    # artifacts. Keys: access/legibility/transactability/trust/outcome.
    no_rails_pillars: dict[str, float] = field(default_factory=dict)
    with_rails_pillars: dict[str, float] = field(default_factory=dict)


@dataclass
class PillarMove:
    """One pillar's score change on one side of the pair, anchor -> latest."""

    domain: str
    pillar: str
    before: float
    after: float
    change: float  # after - before (signed)


@dataclass
class PillarAttribution:
    """Which pillar(s) drove the latest divergence, vs the last in-band reading.

    Computed only when the latest reading is out of band AND an earlier in-band
    reading exists to anchor against — the live series' own pre-drift baseline.
    ``moves`` lists the pillars that shifted appreciably, largest |change| first;
    ``top`` is the single largest mover (None only if no pillar moved, e.g. the
    overall shifted but every pillar was unobserved on one side).
    """

    anchor_ts: str
    moves: list[PillarMove] = field(default_factory=list)

    @property
    def top(self) -> PillarMove | None:
        return self.moves[0] if self.moves else None


@dataclass
class DivergenceCause:
    """Which SIDE of the pair drove the latest divergence, and what it means.

    ``PillarAttribution`` says WHAT changed on a domain (which pillar); this says
    which DOMAIN moved the delta and in which direction — a distinct fact the
    benchmark's credibility turns on. The reference delta can narrow two OPPOSITE
    ways, and conflating them mis-tells an operator what to do:

      - the no-rails side GAINING capability (the real capability gap is genuinely
        closing — a benchmark movement; a durable move is a re-capture candidate), or
      - the with-rails side LOSING ground (a real-world site regression on the
        reference storefront — the pinned fixture still represents the TRUE gap, so
        re-capture should WAIT for the site to recover, not chase the dip).

    Computed on the SAME anchor as ``PillarAttribution`` (the last in-band reading),
    from each side's OVERALL score — numeric on every scored artifact, so unlike the
    pillar attribution this is never None-on-one-side. Vendor-neutral: the host names
    are the module's existing reference-pair constants, used only as data.
    """

    anchor_ts: str
    no_rails_change: float  # latest.no_rails_overall - anchor.no_rails_overall
    with_rails_change: float  # latest.with_rails_overall - anchor.with_rails_overall

    @property
    def gap_change(self) -> float:
        """Change in the delta (with_rails - no_rails), anchor -> latest.

        Negative = the gap narrowed; positive = the gap widened. Equals the change
        in ``divergence`` by construction.
        """
        return round(self.with_rails_change - self.no_rails_change, 4)

    @property
    def driver(self) -> str:
        """The domain whose OVERALL score moved more, anchor -> latest.

        Ties resolve to the no-rails (capability-floor) side, so an ambiguous move
        is read conservatively as gap movement rather than reference degradation.
        Because the driver is the dominant side, ``sign(gap_change)`` is fixed by
        the driver's own direction (no-rails up / with-rails down both NARROW).
        """
        return (
            CANONICAL_WITH_RAILS
            if abs(self.with_rails_change) > abs(self.no_rails_change)
            else CANONICAL_NO_RAILS
        )

    @property
    def driver_change(self) -> float:
        return (
            self.with_rails_change
            if self.driver == CANONICAL_WITH_RAILS
            else self.no_rails_change
        )

    @property
    def reference_degraded(self) -> bool:
        """True iff the divergence is driven by the WITH-RAILS reference LOSING
        ground (the gap narrowing from the top, not the floor rising).

        This is the case where the pinned fixture still represents the true
        capability gap and a re-capture should wait for the site to recover — as
        opposed to the no-rails side gaining capability, where the real gap is
        genuinely closing. The single crispest signal for the deferred re-capture
        decision (the P2 canonical-fixture item).
        """
        return self.driver == CANONICAL_WITH_RAILS and self.with_rails_change < 0


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
    # which pillar(s) drove the latest divergence, vs the last in-band reading;
    # None when in-band (nothing to explain) or when no in-band anchor exists in
    # the live series (we never observed a stable baseline to attribute against).
    attribution: PillarAttribution | None = None
    # which SIDE drove the latest divergence (no-rails gaining vs with-rails
    # softening) — same anchor/gate as ``attribution``; None on the same conditions.
    divergence_cause: DivergenceCause | None = None


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
        no_rails_pillars=_numeric_pillars(no_rails),
        with_rails_pillars=_numeric_pillars(with_rails),
    )


def _numeric_pillars(side: dict) -> dict[str, float]:
    """Extract a side's pillar overalls, keeping only NUMERIC entries.

    A pillar recorded None (outcome in static mode, or a pillar that came back
    CANT_TEST on an error crawl) is dropped — attribution honesty: a pillar we
    couldn't observe is not credited a move. Non-dict / absent -> {} (pre-pillar
    artifacts simply contribute no attribution, never a fabricated zero).
    """
    pillars = side.get("pillars")
    if not isinstance(pillars, dict):
        return {}
    out: dict[str, float] = {}
    for name, value in pillars.items():
        if isinstance(value, bool):  # guard: bools are ints in Python
            continue
        if isinstance(value, (int, float)):
            out[str(name)] = float(value)
    return out


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
    hist.attribution = _attribute(points, run, latest)
    hist.divergence_cause = _cause(points, run, latest)
    return hist


def _pillar_moves(
    domain: str, before: dict[str, float], after: dict[str, float]
) -> list[PillarMove]:
    """Per-pillar score changes for one side, for pillars numeric in BOTH readings."""
    moves: list[PillarMove] = []
    for pillar, b in before.items():
        a = after.get(pillar)
        if a is None:  # pillar unobserved in the latest reading -> no attribution
            continue
        change = round(a - b, 4)
        if abs(change) > _PILLAR_MOVE_EPS:
            moves.append(PillarMove(domain, pillar, b, a, change))
    return moves


def _attribute(
    points: list[CanonicalPoint], run: int, latest: CanonicalPoint
) -> PillarAttribution | None:
    """Attribute the latest divergence to the pillar(s) that moved vs the last
    in-band reading.

    Only meaningful when the latest reading is out of band (run >= 1) and an
    earlier IN-BAND reading exists to anchor against — ``points[-(run+1)]`` is the
    reading immediately before the trailing out-of-band run, in-band by that run's
    stopping condition. When the entire series is out of band (run == len), there
    is no observed stable baseline in the live series, so we make no claim (honest
    None), the same attribution discipline the loader applies to unobserved runs.
    """
    if run < 1 or run >= len(points):
        return None
    anchor = points[-(run + 1)]
    moves = _pillar_moves(
        CANONICAL_NO_RAILS, anchor.no_rails_pillars, latest.no_rails_pillars
    ) + _pillar_moves(
        CANONICAL_WITH_RAILS, anchor.with_rails_pillars, latest.with_rails_pillars
    )
    moves.sort(key=lambda m: abs(m.change), reverse=True)
    return PillarAttribution(anchor_ts=anchor.ts, moves=moves)


def _cause(
    points: list[CanonicalPoint], run: int, latest: CanonicalPoint
) -> DivergenceCause | None:
    """Attribute the latest divergence to a SIDE (no-rails vs with-rails), from
    each side's OVERALL score change vs the last in-band reading.

    Same gate as ``_attribute``: only when the latest reading is out of band and an
    earlier in-band anchor exists (``points[-(run+1)]``). Uses OVERALL scores, which
    are numeric on every scored artifact, so this is defined even on pre-pillar
    artifacts where per-pillar attribution is empty.
    """
    if run < 1 or run >= len(points):
        return None
    anchor = points[-(run + 1)]
    return DivergenceCause(
        anchor_ts=anchor.ts,
        no_rails_change=round(latest.no_rails_overall - anchor.no_rails_overall, 4),
        with_rails_change=round(
            latest.with_rails_overall - anchor.with_rails_overall, 4
        ),
    )


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


def cause_verdict(cause: DivergenceCause) -> str:
    """A capability-lens sentence naming which SIDE drove the divergence.

    Keys on (driver side, driver direction) — the four honest cases. Because the
    driver is the dominant side, its direction fixes whether the gap narrowed or
    widened, so the sentence never contradicts ``gap_change``.
    """
    driver = cause.driver
    change = cause.driver_change
    verb = "fell" if change < 0 else "rose"
    if driver == CANONICAL_NO_RAILS:
        if change > 0:
            meaning = (
                "the capability gap narrowed because the no-rails reference GAINED "
                "capability — a real benchmark movement, not a reference outage"
            )
        else:
            meaning = (
                "the gap widened because the no-rails reference LOST ground"
            )
    else:  # with-rails driver
        if change < 0:
            meaning = (
                "the gap narrowed because the with-rails reference SOFTENED "
                "(a real-world site change), not because the no-rails side gained "
                "capability — the pinned fixture still represents the true gap"
            )
        else:
            meaning = (
                "the gap widened because the with-rails reference GAINED capability"
            )
    return f"{driver} overall {verb} {change:+.1f} — {meaning}"


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
    attr = history.attribution
    if attr is not None:
        top = attr.top
        if top is not None:
            verb = "fell" if top.change < 0 else "rose"
            lines.append(
                f"attribution (vs last in-band {_short_ts(attr.anchor_ts)}): "
                f"{top.domain} {top.pillar} {verb} "
                f"{top.before:.1f} → {top.after:.1f} ({top.change:+.1f}) "
                f"— the largest pillar move"
            )
            others = attr.moves[1:3]
            if others:
                more = "; ".join(
                    f"{m.domain} {m.pillar} {m.before:.1f}→{m.after:.1f} ({m.change:+.1f})"
                    for m in others
                )
                lines.append(f"  also: {more}")
        else:
            lines.append(
                f"attribution (vs last in-band {_short_ts(attr.anchor_ts)}): "
                f"overall delta moved but no single pillar isolated "
                f"(pillar(s) unobserved on one side)"
            )
    cause = history.divergence_cause
    if cause is not None:
        lines.append(f"driver: {cause_verdict(cause)}")
    tail = pts[-window:]
    lines.append(
        f"delta trend (last {len(tail)}): {_spark([p.delta for p in tail])}"
    )
    return "\n".join(lines)
