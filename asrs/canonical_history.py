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
from datetime import datetime, timezone
from statistics import pstdev

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
# The in-band width is not just an assumption: ``noise_floor`` measures the actual
# at-rest dispersion of the in-band readings, and on the committed series every
# in-band re-score reproduces the pinned delta EXACTLY (σ=0), so the band is
# absorbing real-world site transients, not measurement noise — see NoiseFloor.
_BAND_IN = 2.0
_BAND_DRIFT = 8.0

BAND_NO_DATA = "no-data"
BAND_IN = "in-band"
BAND_DRIFTING = "drifting"
BAND_DIVERGED = "diverged"

# A trailing out-of-band run of this length is treated as SUSTAINED (a real-world
# move) rather than jitter — the same cutoff the render's "sustained"/"recent"
# wording uses, and the gate the re-capture recommendation waits on before advising
# any action on the pinned baseline.
_SUSTAINED_MIN = 3

# Re-capture recommendation codes — the DECISION the drift diagnostics feed: given
# the live series, does the committed canonical fixture still represent the true
# capability gap, or should it be re-captured [LOCAL]? Synthesizes band +
# sustained-run + divergence CAUSE; never re-captures anything itself (moving the
# pinned baseline is a [LOCAL], comparability-affecting step), only advises.
REC_NO_DATA = "no-data"
REC_VALID = "baseline-valid"
REC_WAIT = "wait-not-yet-sustained"
REC_DEFER = "defer-reference-degraded"
REC_RECAPTURE = "recapture-candidate"
REC_REVIEW = "review-no-anchor"
REC_AMBIGUOUS = "review-side-ambiguous"

_SPARK = "▁▂▃▄▅▆▇█"


# A per-pillar move smaller than this (in pillar-score points, 0–100) is treated
# as noise and not reported as a "mover" — keeps the attribution to the pillar(s)
# that actually shifted, not float dust. Pillar overalls are exact renormalized
# ratios, so real moves are many points; this only filters exact-0.0 no-movers.
_PILLAR_MOVE_EPS = 0.1

# Dispersion at or below this (in overall-score points) is treated as no measurable
# noise — the in-band re-score reproduced the pinned delta exactly. Small because the
# static re-score is a deterministic function of the crawl; genuine jitter, when it
# exists, is a whole point or more (a pillar softening), never float dust.
_NOISE_EPS = 1e-6

# A live re-score older than this (hours) means the newest observation is no longer
# current, so the latest reading's verdict (band, re-capture advice) describes a
# STALE crawl, not the reference pair's state right now. This is the SAME 6-hour
# floor the playbook's self-healing law uses to declare the local verify runner
# down ("newest runs/local/verify_*.json older than 6 hours → the verify floor is
# down"). Surfacing it here keeps the history readout from presenting a stale
# in-band all-clear as a fresh one — the runner can stall while the last thing it
# saw was healthy, and a reader must not mistake age for confirmation.
_STALE_FLOOR_HOURS = 6.0


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
class ReadingTop:
    """The top pillar-mover at ONE reading of the trailing out-of-band run.

    ``top`` is that reading's largest-|change| pillar vs the shared in-band anchor,
    or None when the reading's overall moved but no pillar was observable on either
    side (the same honest-None ``_attribute`` applies, per reading)."""

    ts: str
    top: PillarMove | None


@dataclass
class AttributionStability:
    """Whether the fingered pillar is STABLE across the trailing out-of-band run.

    ``PillarAttribution`` fingers the drifting pillar from the LATEST reading vs the
    last in-band anchor — a single snapshot. This asks the harder question that
    snapshot cannot: does EVERY reading of the trailing out-of-band run finger the
    SAME (domain, pillar), or does the top mover WANDER reading to reading? A driver
    claim an operator acts on ("the reference SOFTENED on transactability") is only
    as credible as its stability — a fingered pillar that flips between consecutive
    re-scores is noise-dominated, not a sustained real-world site move.

    Computed against the SAME in-band anchor ``_attribute`` uses (``points[-(run+1)]``)
    over every reading of the trailing out-of-band run (``points[-run:]``, oldest
    first). ``readings`` records each reading's top mover; ``stable`` is True iff every
    reading isolated a top mover AND they all agree on one (domain, pillar) — the
    signed magnitude may vary between readings, only the fingered pillar must hold. A
    reading that isolates NO pillar (top None) makes the run NOT stable: an
    unconfirmable pillar is not a confirmed-same one (attribution honesty).

    Distinct from not-stable, the whole object is None when the run is too short to be
    a stability question (< 2 out-of-band readings — one reading cannot wander) or no
    in-band anchor exists in the live series — the same gates ``_attribute`` honours."""

    anchor_ts: str
    readings: list[ReadingTop] = field(default_factory=list)

    @property
    def movers(self) -> set[tuple[str, str]]:
        """The distinct (domain, pillar) tops across the run (None tops excluded)."""
        return {(r.top.domain, r.top.pillar) for r in self.readings if r.top is not None}

    @property
    def stable(self) -> bool:
        """True iff every reading isolated a top mover and they all agree on the
        same (domain, pillar)."""
        if any(r.top is None for r in self.readings):
            return False
        return len(self.movers) == 1

    @property
    def fingered(self) -> tuple[str, str] | None:
        """The single (domain, pillar) the whole run agrees on, else None."""
        if not self.stable:
            return None
        return next(iter(self.movers))


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

    @property
    def side_ambiguous(self) -> bool:
        """True iff both references moved by EQUAL magnitude in OPPOSITE directions,
        so the gap genuinely moved but which SIDE drove it is a tie that ``driver``
        resolves — conservatively, but arbitrarily — to the no-rails floor.

        This is the one case where the ``driver`` convention is a coin-flip rather
        than a measurement: the no-rails move and the with-rails move are exactly
        as large, so reading it as "the no-rails floor GAINED capability" would hide
        an equal-and-opposite with-rails softening of the same magnitude. The
        recommendation stays conservative here (``reference_degraded`` is False on a
        tie, so re-capture is not deferred), but the READOUT must SAY the side is
        unattributed rather than silently present the tie as a confident floor move.
        Requires an actual gap change (equal-and-SAME-sign moves cancel to no
        divergence, which is not an ambiguous attribution — it is no attribution).

        Equality is rounding-tolerant (to 4 dp, mirroring ``gap_change``): two side
        moves that are equal to the scores' own 1-decimal precision but differ only
        in float noise are a genuine tie, and must not slip through to the confident
        no-rails prose on a sub-rounding artifact.
        """
        return (
            round(abs(self.with_rails_change) - abs(self.no_rails_change), 4) == 0
            and self.gap_change != 0
        )


@dataclass
class NoiseFloor:
    """The measured MEASUREMENT-noise floor of the live re-score, from the readings
    the band already calls in-band.

    The divergence bands (``_BAND_IN`` etc.) assume a separation between ordinary
    measurement jitter and a real site move. This turns that assumption into a
    measured number: over the readings within the in-band width
    (``|delta - baseline| <= _BAND_IN``), how much does the delta ACTUALLY vary? The
    static canonical re-score is a deterministic function of the live crawl, so at
    rest — when the reference sites are up and unchanged — every re-score should
    reproduce the pinned delta exactly, i.e. the at-rest dispersion should be ~0.
    When it is, the band is demonstrably absorbing real-world site TRANSIENTS (the
    out-of-band readings), not measurement noise — the honest reading of what the
    band is for, replacing the docstring's bare assertion of "ordinary jitter".

    ``n_in_band`` : how many in-band readings the floor is measured over (>= 2).
    ``stddev``    : population stddev of their delta values (the at-rest dispersion).
    ``max_abs_divergence`` : the worst |delta - baseline| observed at rest.
    ``no_rails_stddev`` / ``with_rails_stddev`` : population stddev of EACH SIDE's
        overall score over the same in-band readings — the at-rest dispersion of the
        two storefronts individually, not just their difference.

    Why measure the sides, not only the delta: a deterministic delta (``stddev``≈0)
    is consistent with BOTH sides being fixed at rest AND with both sides jittering
    in lock-step so their difference cancels — the delta-only measure cannot tell
    those apart. Since ``delta = with_rails - no_rails``, per-side determinism
    (both side stddevs ≈ 0) IMPLIES delta determinism but not vice versa, so the
    per-side measure is the strictly stronger calibration fact: it refutes the
    "two correlated drifts that cancel" hypothesis a critic could raise about a
    stable delta, proving each reference storefront reproduces its pinned overall
    exactly at rest rather than the pair merely reproducing its gap.

    Read-only, no score. The bands are clipped, so this dispersion is a truncated
    (lower-biased) estimate of true jitter — fine as a calibration floor: if even
    the clipped at-rest dispersion crowds the band, the band is certainly too tight.
    """

    n_in_band: int
    stddev: float
    max_abs_divergence: float
    no_rails_stddev: float
    with_rails_stddev: float

    @property
    def deterministic(self) -> bool:
        """True iff the in-band re-score shows no measurable dispersion — every
        in-band reading reproduced the pinned delta exactly. When true, the band is
        absorbing real-world site TRANSIENTS, not measurement noise."""
        return self.stddev <= _NOISE_EPS and self.max_abs_divergence <= _NOISE_EPS

    @property
    def sides_deterministic(self) -> bool:
        """True iff BOTH sides show no measurable at-rest dispersion — each
        reference storefront reproduced its pinned overall exactly across the
        in-band readings. Strictly stronger than ``deterministic``: it implies the
        delta is deterministic AND that the delta's stability is genuine per-side
        determinism, not two lock-step drifts cancelling in the difference."""
        return (
            self.no_rails_stddev <= _NOISE_EPS
            and self.with_rails_stddev <= _NOISE_EPS
        )

    @property
    def band_well_separated(self) -> bool:
        """True iff the in-band threshold comfortably clears observed jitter — three
        sigma of the at-rest dispersion still fits inside the in-band width, so
        ordinary noise cannot be misread as drift. Trivially true when deterministic;
        False would mean the band is calibrated TOO TIGHT for the measured noise."""
        return 3.0 * self.stddev <= _BAND_IN


@dataclass
class PillarNoiseFloor:
    """The at-rest dispersion of ONE side's ONE pillar over the in-band readings —
    the pillar-granularity counterpart of ``NoiseFloor``.

    ``NoiseFloor`` proves the OVERALL delta is deterministic at rest, so the in-band
    band is absorbing site TRANSIENTS, not measurement jitter. But the drift the
    benchmark ATTRIBUTES and an operator ACTS on is at the PILLAR level — WHICH
    (domain, pillar) softened — and nothing at that granularity says the fingered
    move is above pillar jitter. A −25-point transactability drop is only a credible
    real-world site move if, at rest, THAT SAME pillar reproduces its value exactly;
    otherwise the "drop" could be ordinary per-pillar noise that the coarser overall
    measure happens to cancel. This closes that gap: over the readings the band calls
    in-band, how much does the given side's given pillar ACTUALLY vary?

    On the committed series the fingered pillar (driftflight.com transactability) is
    87.5 across every in-band reading, so the at-rest dispersion is 0 and the tracked
    −25 move dwarfs it — the pillar-level proof that the attributed drop is signal,
    not jitter, mirroring what ``band_clears_the_observed_noise`` proves for the
    overall delta.

    Measured only over in-band readings where the pillar is NUMERIC on that side (a
    pillar recorded None — unobserved on an error crawl — is dropped, never counted
    as a zero). Read-only, no score.

    ``domain`` / ``pillar`` : which side's which pillar this floor measures.
    ``n_in_band``           : in-band readings the floor is measured over (>= 2).
    ``stddev``              : population stddev of the pillar's value at rest.
    ``max_abs_divergence``  : the worst |value - mean| observed at rest.
    """

    domain: str
    pillar: str
    n_in_band: int
    stddev: float
    max_abs_divergence: float

    @property
    def deterministic(self) -> bool:
        """True iff the pillar shows no measurable at-rest dispersion — every in-band
        reading reproduced its value exactly. When true, any appreciable out-of-band
        move on this pillar is a real change, not pillar-level measurement jitter."""
        return self.stddev <= _NOISE_EPS and self.max_abs_divergence <= _NOISE_EPS


@dataclass
class Liveness:
    """How CURRENT the latest live re-score is — is the newest observation fresh
    enough that its verdict describes the reference pair NOW, or stale?

    Every other field in ``CanonicalHistory`` describes the latest READING (its
    band, its re-capture advice, which side moved). None of them say how long ago
    that reading was taken. But the local verify runner can stall (or the machine
    sleep) while the last thing it recorded was perfectly in-band — leaving a
    healthy-looking "baseline valid" verdict that is hours old. A reader who acts on
    that verdict is trusting an observation that may no longer hold. This makes the
    age of the newest re-score an explicit, honest fact: the same 6-hour floor the
    playbook uses to declare the runner down (``_STALE_FLOOR_HOURS``), applied to
    the calibration signal itself.

    Computed only when the caller supplies a reference ``now`` (the CLI passes the
    wall clock); the core ``summarize`` stays a pure function of the point series
    when ``now`` is None, making no clock-dependent claim it cannot support — the
    same honest-None discipline attribution and the noise floor already follow.

    ``latest_ts``         : the newest re-score's timestamp (as recorded).
    ``age_hours``         : hours between that timestamp and ``now`` (>= 0; a
        future-dated artifact clamps to 0 rather than reporting a negative age).
    ``stale_floor_hours`` : the freshness floor this age is judged against.
    """

    latest_ts: str
    age_hours: float
    stale_floor_hours: float = _STALE_FLOOR_HOURS

    @property
    def fresh(self) -> bool:
        """True iff the newest re-score is within the freshness floor — its verdict
        is a current observation. False = STALE: the verdict describes an old crawl
        and the local verify runner may be down; do not read it as a fresh
        confirmation of the reference pair's present state."""
        return self.age_hours <= self.stale_floor_hours


@dataclass
class SustainedRun:
    """Wall-clock PERSISTENCE of the trailing out-of-band run.

    ``consecutive_out_of_band`` counts how many trailing re-scores are out of band,
    and ``_SUSTAINED_MIN`` gates the "sustained" verdict (and the re-capture
    decision) on that COUNT. But a count says nothing about the wall-clock TIME the
    run spans: three readings a minute apart (the local runner briefly firing in a
    burst) are far weaker evidence of a durable real-world change than three spanning
    a day. This measures that span — the hours from the FIRST reading of the trailing
    out-of-band run to the latest — so "sustained" is corroborated by DURATION, not
    reading-count alone. It is a descriptive companion to the count, not a new gate:
    it never re-classifies a run or changes a recommendation, it makes the run's real
    persistence an explicit, honest fact for a reader (and the re-capture decision it
    feeds) to weigh — the wall-clock analogue of ``Liveness`` for the drift itself.

    Computed from parsed artifact timestamps; None when the run is empty or either
    endpoint timestamp is unparseable (the same honest-None discipline the loader,
    attribution, noise floor, and liveness follow — never a fabricated duration).

    ``n``          : readings in the trailing out-of-band run (== consecutive_out_of_band).
    ``span_hours`` : wall-clock hours first-run-reading -> latest (>= 0; 0 for a lone reading).
    ``first_ts`` / ``latest_ts`` : the run's endpoints, as recorded.
    """

    n: int
    span_hours: float
    first_ts: str
    latest_ts: str


@dataclass
class RecaptureAdvice:
    """Whether the pinned canonical fixture still represents the true gap.

    The single DECISION the drift diagnostics (band, sustained run, pillar
    attribution, side/direction cause) exist to inform: is the committed fixture
    baseline still faithful to the real capability gap, or has the reference pair
    moved durably enough that the pinned delta should be re-captured [LOCAL]? This
    computes the recommendation the operator has been reasoning out by hand every
    time the live series drifts. It NEVER re-captures anything — moving the pinned
    baseline is a [LOCAL], comparability-affecting step (the maintenance contract
    ``test_canonical_replay`` documents) — it only names the honest recommendation.
    """

    code: str
    reason: str


@dataclass
class DecisionCorroboration:
    """Whether the re-capture DECISION rests on BOTH independent drift mechanisms.

    ``recapture_advice`` synthesizes its recommendation from the SIDE-level
    ``DivergenceCause`` ALONE — each reference storefront's OVERALL score. The
    pillar-level ``PillarAttribution`` is an INDEPENDENT decomposition (per-pillar
    scores, a different arithmetic on a finer signal). When the pillar mechanism's
    single largest mover lands on the SAME domain the side-level cause blames AND
    moves the SAME direction as that side's overall, the two mechanisms CORROBORATE
    the decision — it rests on two independent computations concurring, not one
    number. That corroboration is what makes a DEFER (or a RECAPTURE) trustworthy to
    an operator, and it is the convergence the real-series guard
    (``test_real_series_defer_decision_is_corroborated_by_both_mechanisms``) pins
    internally; this names it on the READOUT so the operator sees WHY a recommendation
    holds, not only what it is.

    Computed only when BOTH mechanisms are present and the pillar mechanism isolates a
    single top mover — out of band, with an in-band anchor, a pillar observable on the
    moving side. None otherwise: the same honest-None discipline the attribution and
    the cause already follow — a decision the two mechanisms cannot both speak to is
    never CLAIMED corroborated (nor falsely claimed contradicted).

    Vendor-neutral: the domains are the module's reference-pair constants, compared
    only for EQUALITY to each other (does the pillar side match the cause side), never
    special-cased by host identity.
    """

    driver: str  # the side-level cause driver (dominant OVERALL mover)
    driver_change: float
    pillar_domain: str  # the pillar-level top mover's domain
    pillar: str
    pillar_change: float

    @property
    def same_side(self) -> bool:
        """True iff the pillar mechanism's top mover sits on the same domain the
        side-level cause blames."""
        return self.pillar_domain == self.driver

    @property
    def same_direction(self) -> bool:
        """True iff the fingered pillar moved the same way as that side's overall —
        the same sign test ``cause_verdict`` uses before it may name the pillar."""
        return (self.pillar_change < 0) == (self.driver_change < 0)

    @property
    def corroborated(self) -> bool:
        """True iff the two independent decompositions concur on side AND direction —
        the decision rests on two signals, not one."""
        return self.same_side and self.same_direction


@dataclass
class LoadAccounting:
    """How many verify artifacts the loader saw, KEPT, and EXCLUDED — and why.

    ``load_points`` silently drops artifacts it cannot use: an incomplete/unusable
    file (``_EXCL_MALFORMED`` — bad JSON, missing/invalid score or delta, a side
    that didn't score) or a run scored while the bench's own guards were red
    (``_EXCL_RED_BENCH`` — the Cycle-215 versioned-comparability gate). Silent
    exclusion means the ``series: N re-scores`` line a reader sees is the FILTERED
    series, not the raw one, with no sign that anything was dropped. This records
    the accounting so the readout can NAME it — the operator sees the series is
    filtered, not raw, and on what grounds (the readout mirror of the Cycle-215
    loader gate, the same terminal->HTML close-out the other drift diagnostics
    took).

    ``total``     : verify_*.json files found (parsed or not).
    ``included``  : usable readings that became points.
    ``excluded_red_bench`` : dropped for ``tests_ok`` explicitly False.
    ``excluded_malformed`` : dropped as unusable. By construction
        ``included + excluded_red_bench + excluded_malformed == total``.
    """

    total: int
    included: int
    excluded_red_bench: int
    excluded_malformed: int

    @property
    def excluded(self) -> int:
        return self.excluded_red_bench + self.excluded_malformed

    @property
    def any_excluded(self) -> bool:
        """True iff the loader dropped at least one artifact — the series a reader
        sees is FILTERED, not the raw set of committed re-scores."""
        return self.excluded > 0


# Fraction of the committed verify series the loader may EXCLUDE before the KEPT
# remnant is no longer a trustworthy basis for the drift verdict. Every drift
# diagnostic (band, sustained run, attribution, noise floor) is computed over the
# INCLUDED points only; below this floor a few dropped artifacts (e.g. the fixed
# pre-Cycle-13 legacy malformed one) are ordinary attrition, but above it so much of
# the series was filtered that those diagnostics rest on a thinned/biased remnant and
# a reader should distrust the verdict. Set to 0.25: the sustained-run gate already
# needs 3 readings, so losing more than a quarter of the series materially thins the
# evidence any verdict stands on. A floor on the FRACTION (not a raw count) so it does
# not tighten as the series legitimately grows.
_INTEGRITY_EXCLUDED_FLOOR = 0.25


@dataclass
class SeriesIntegrity:
    """Whether the KEPT drift series is a trustworthy basis for the verdict, or so
    much was filtered that the remnant is thinned/biased.

    ``LoadAccounting`` NAMES what the loader dropped and why; this JUDGES whether the
    drop compromises the series the drift diagnostics are computed over. The band,
    sustained run, pillar attribution and noise floor all read the INCLUDED points
    only — a divergence verdict drawn from a series with most of its artifacts
    filtered out rests on a remnant, not the raw record, and a reader acting on it
    should know. This turns the Cycle-216 accounting into a single integrity verdict:
    is the excluded FRACTION within the floor (``intact``) or past it (degraded)?

    Vendor-neutral, read-only, no score — a pure function of the loader counts.

    ``floor`` is the excluded-fraction threshold; ``excluded_fraction`` the observed
    one; ``red_bench_fraction`` the version-comparability-relevant subset (runs scored
    while the bench's own guards were red — the Cycle-215 gate), surfaced separately
    because a red-bench exclusion signals the scoring path itself may have been in
    flux, a sharper concern than a benign legacy malformed artifact.
    """

    total: int
    included: int
    excluded_red_bench: int
    excluded_malformed: int
    floor: float = _INTEGRITY_EXCLUDED_FLOOR

    @property
    def excluded(self) -> int:
        return self.excluded_red_bench + self.excluded_malformed

    @property
    def any_excluded(self) -> bool:
        return self.excluded > 0

    @property
    def excluded_fraction(self) -> float:
        """Fraction of the committed series the loader dropped (0.0 when none found)."""
        return self.excluded / self.total if self.total else 0.0

    @property
    def red_bench_fraction(self) -> float:
        """Fraction dropped specifically as red-bench (scored while the bench's own
        guards were red) — the version-comparability-relevant exclusions."""
        return self.excluded_red_bench / self.total if self.total else 0.0

    @property
    def intact(self) -> bool:
        """True iff the excluded fraction stays within the floor — the kept series is
        a representative basis for the drift verdict. False = DEGRADED: enough of the
        committed series was filtered that the verdict rests on a thinned/biased
        remnant; weigh it with caution."""
        return self.excluded_fraction <= self.floor


def series_integrity(
    accounting: LoadAccounting | None,
) -> SeriesIntegrity | None:
    """Judge whether the kept series is a trustworthy basis for the drift verdict.

    None when no loader accounting is available (a bare point list — no loader ran)
    or no artifacts were found at all (``total == 0`` — nothing to judge). Pure, no
    score, no side effects.
    """
    if accounting is None or accounting.total == 0:
        return None
    return SeriesIntegrity(
        total=accounting.total,
        included=accounting.included,
        excluded_red_bench=accounting.excluded_red_bench,
        excluded_malformed=accounting.excluded_malformed,
    )


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
    # wall-clock persistence of that trailing out-of-band run (first out-of-band
    # reading -> latest) — the DURATION behind the count. None when in-band (no run)
    # or an endpoint timestamp is unparseable. Descriptive only; gates nothing.
    sustained_run: SustainedRun | None = None
    # which pillar(s) drove the latest divergence, vs the last in-band reading;
    # None when in-band (nothing to explain) or when no in-band anchor exists in
    # the live series (we never observed a stable baseline to attribute against).
    attribution: PillarAttribution | None = None
    # whether the fingered pillar is STABLE across the trailing out-of-band run
    # (every reading fingers the same domain+pillar) or WANDERS — a credibility
    # measure on the single-snapshot attribution above. None when < 2 out-of-band
    # readings (too short to wander) or no in-band anchor exists in the live series.
    attribution_stability: AttributionStability | None = None
    # which SIDE drove the latest divergence (no-rails gaining vs with-rails
    # softening) — same anchor/gate as ``attribution``; None on the same conditions.
    divergence_cause: DivergenceCause | None = None
    # the synthesized re-capture recommendation (baseline-valid / wait / defer /
    # recapture-candidate / review) — always present once there is a latest point.
    recapture: RecaptureAdvice | None = None
    # whether that decision is CORROBORATED by both independent drift mechanisms —
    # the side-level cause (overalls) and the pillar-level attribution (per-pillar)
    # fingering the same side moving the same way. None unless both mechanisms are
    # present with an isolated pillar (out of band, in-band anchor); it never claims
    # a decision the two mechanisms cannot both speak to as corroborated.
    corroboration: DecisionCorroboration | None = None
    # the measured measurement-noise floor over the in-band readings — validates
    # that the in-band band absorbs site transients, not measurement jitter. None
    # when fewer than 2 in-band readings exist (dispersion is undefined).
    noise_floor: NoiseFloor | None = None
    # the at-rest dispersion of the ATTRIBUTED pillar (the fingered top mover) over
    # the in-band readings — the pillar-granularity noise floor proving the tracked
    # drop is signal, not pillar jitter. None when there is no isolated top mover to
    # measure (in-band, no in-band anchor, or the fingered pillar has < 2 in-band
    # numeric readings).
    attributed_pillar_noise_floor: PillarNoiseFloor | None = None
    # how current the latest re-score is (fresh within the 6h floor vs stale). None
    # when no reference ``now`` was supplied (a pure point-series summary) or the
    # latest timestamp is unparseable — never a fabricated freshness claim.
    liveness: Liveness | None = None
    # the loader's exclusion accounting (how many artifacts were seen, KEPT, and
    # dropped as red-bench / malformed) — lets the readout show the series is
    # FILTERED, not raw. None when summarized from a bare point list (no loader
    # ran), e.g. a test constructing points directly; present via ``load_history``.
    load_accounting: LoadAccounting | None = None
    # whether the KEPT series is a trustworthy basis for the drift verdict (the
    # excluded fraction within the integrity floor) or DEGRADED (too much of the
    # committed series filtered out) — the JUDGMENT over the accounting's counts.
    # None when no loader accounting is present or no artifacts were found at all.
    integrity: SeriesIntegrity | None = None


def _band_for(abs_divergence: float) -> str:
    if abs_divergence <= _BAND_IN:
        return BAND_IN
    if abs_divergence <= _BAND_DRIFT:
        return BAND_DRIFTING
    return BAND_DIVERGED


def band_for_delta(
    delta: float, baseline_delta: float = FIXTURE_BASELINE_DELTA
) -> str:
    """Band a SINGLE delta reading against the baseline — the band a readout should
    color one point by. Same thresholds ``summarize`` bands the latest reading with,
    kept here so the terminal block and any other surface (the HTML trend) classify a
    point identically instead of re-deriving the cutoffs. Read-only, no score.
    """
    return _band_for(abs(delta - baseline_delta))


def _repo_root() -> str:
    # This module lives INSIDE the repo (asrs/), so deriving the root from
    # __file__ is safe here — unlike the pinned local runner, which lives
    # outside the checkout and must read ASRS_REPO (playbook self-healing law).
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Exclusion reason codes for the loader accounting — WHY an artifact was dropped.
# red-bench = scored while the bench's own guards were red (tests_ok False, the
# Cycle-215 versioned-comparability gate); malformed = otherwise unusable.
_EXCL_RED_BENCH = "red-bench"
_EXCL_MALFORMED = "malformed"


def _classify_artifact(obj: dict) -> tuple[CanonicalPoint | None, str | None]:
    """Parse one verify artifact, returning ``(point, None)`` if usable or
    ``(None, reason)`` naming WHY it was excluded.

    Early artifacts (pre-Cycle-13, before the stderr-leak fix) recorded a
    FileNotFoundError instead of a score and carry no top-level ``delta``; those
    are ``_EXCL_MALFORMED`` rather than scored as a zero — attribution honesty
    applies to the history readout too (a run we couldn't observe is not a data
    point).

    A run whose OWN bench guards were red (``tests_ok`` explicitly False) is
    likewise not a clean data point — ``_EXCL_RED_BENCH``. The runner scores the
    pair even when the suite fails (it bails only on a failed ``git pull``, before
    scoring — those artifacts carry no ``scores``/``delta`` and are already
    ``_EXCL_MALFORMED`` above), so a tests-red fire still writes a full score. But
    if the bench is red the scoring path may itself be in an unexpected state (e.g.
    a red ``test_canonical_replay`` means the scoring semantics moved), so that
    reading is NOT comparable within the version and must not silently anchor a
    drift attribution — versioned comparability + attribution honesty (invariants
    #2 / #4). Only an EXPLICIT ``tests_ok == False`` excludes: a missing/None field
    (pre-``tests_ok`` artifacts) is the honest-unknown case and stays in, never
    fabricated red.

    The returned reason drives the loader's exclusion accounting
    (``LoadAccounting``) so the readout can show the series is FILTERED, not raw —
    surfacing what was previously a silent drop.
    """
    ts = obj.get("ts")
    scores = obj.get("scores")
    delta = obj.get("delta")
    if not ts or not isinstance(scores, dict) or not isinstance(delta, (int, float)):
        return None, _EXCL_MALFORMED
    if obj.get("tests_ok") is False:
        return None, _EXCL_RED_BENCH
    no_rails = scores.get(CANONICAL_NO_RAILS)
    with_rails = scores.get(CANONICAL_WITH_RAILS)
    if not isinstance(no_rails, dict) or not isinstance(with_rails, dict):
        return None, _EXCL_MALFORMED
    if not (no_rails.get("ok") and with_rails.get("ok")):
        return None, _EXCL_MALFORMED
    no_o = no_rails.get("overall")
    with_o = with_rails.get("overall")
    if not isinstance(no_o, (int, float)) or not isinstance(with_o, (int, float)):
        return None, _EXCL_MALFORMED
    return (
        CanonicalPoint(
            ts=ts,
            no_rails_overall=float(no_o),
            no_rails_grade=str(no_rails.get("grade", "?")),
            with_rails_overall=float(with_o),
            with_rails_grade=str(with_rails.get("grade", "?")),
            delta=float(delta),
            no_rails_pillars=_numeric_pillars(no_rails),
            with_rails_pillars=_numeric_pillars(with_rails),
        ),
        None,
    )


def _point_from_artifact(obj: dict) -> CanonicalPoint | None:
    """Parse one verify artifact into a CanonicalPoint, or None if unusable.

    Thin points-only wrapper over ``_classify_artifact`` preserving the historical
    signature for callers that only care WHETHER an artifact is usable; see that
    function for the full exclusion rationale (malformed vs red-bench).
    """
    pt, _ = _classify_artifact(obj)
    return pt


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


def load_points_accounted(
    runs_dir: str | None = None,
) -> tuple[list[CanonicalPoint], LoadAccounting]:
    """Load every usable verify artifact as a CanonicalPoint AND account for the
    ones EXCLUDED (red-bench / malformed), ordered by ts.

    ``load_points`` is the points-only view of this; the accounting lets the
    readout show the series is FILTERED, not raw. A file that fails to open or
    parse as JSON is counted ``malformed`` (it is an artifact we saw but could not
    use), so ``total`` is every ``verify_*.json`` found and the accounting closes:
    ``included + excluded_red_bench + excluded_malformed == total``.
    """
    if runs_dir is None:
        runs_dir = os.path.join(_repo_root(), "runs", "local")
    points: list[CanonicalPoint] = []
    total = red = malformed = 0
    for path in sorted(glob.glob(os.path.join(runs_dir, "verify_*.json"))):
        total += 1
        try:
            with open(path, encoding="utf-8") as fh:
                obj = json.load(fh)
        except (OSError, json.JSONDecodeError):
            malformed += 1
            continue
        pt, reason = _classify_artifact(obj)
        if pt is not None:
            points.append(pt)
        elif reason == _EXCL_RED_BENCH:
            red += 1
        else:
            malformed += 1
    points.sort(key=lambda p: p.ts)
    accounting = LoadAccounting(
        total=total,
        included=len(points),
        excluded_red_bench=red,
        excluded_malformed=malformed,
    )
    return points, accounting


def load_points(runs_dir: str | None = None) -> list[CanonicalPoint]:
    """Load every usable verify artifact as a CanonicalPoint, ordered by ts."""
    points, _ = load_points_accounted(runs_dir)
    return points


def _parse_ts(ts: str) -> datetime | None:
    """Parse a ``YYYYMMDDTHHMMSSZ`` verify-artifact timestamp to a UTC datetime, or
    None if it doesn't match (never guesses — an unparseable ts yields no freshness
    claim, the same honest-None the loader applies to unusable artifacts)."""
    try:
        return datetime.strptime(ts, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def liveness(latest: CanonicalPoint | None, now: datetime | None) -> Liveness | None:
    """How current the newest re-score is, judged against ``_STALE_FLOOR_HOURS``.

    None when there is no latest point, no reference ``now`` (a pure point-series
    summary makes no clock-dependent claim), or the latest timestamp is unparseable.
    A future-dated artifact clamps to age 0 rather than reporting a negative age.
    Pure given ``now``; no side effects, no score.
    """
    if latest is None or now is None:
        return None
    when = _parse_ts(latest.ts)
    if when is None:
        return None
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    age_hours = max(0.0, (now - when).total_seconds() / 3600.0)
    return Liveness(latest_ts=latest.ts, age_hours=round(age_hours, 3))


def summarize(
    points: list[CanonicalPoint],
    baseline_delta: float = FIXTURE_BASELINE_DELTA,
    *,
    now: datetime | None = None,
    accounting: LoadAccounting | None = None,
) -> CanonicalHistory:
    """Roll a point series up into a CanonicalHistory (latest + drift verdict).

    ``now`` (optional, tz-aware UTC) enables the freshness check on the latest
    re-score; omit it for a pure, clock-independent summary of the series.
    ``accounting`` (optional) carries the loader's exclusion accounting so the
    readout can show the series is filtered; a bare point list (no loader ran)
    leaves it None and no accounting line renders.
    """
    hist = CanonicalHistory(
        points=list(points),
        baseline_delta=baseline_delta,
        load_accounting=accounting,
    )
    # Judge the series' integrity from the accounting BEFORE the empty-series early
    # return: a series filtered all the way to empty is the MOST degraded case, and
    # the verdict is still worth carrying even when there are no points to summarize.
    hist.integrity = series_integrity(accounting)
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
    hist.sustained_run = sustained_run(points, run)
    hist.attribution = _attribute(points, run, latest)
    hist.attribution_stability = attribution_stability(points, run)
    hist.divergence_cause = _cause(points, run, latest)
    hist.recapture = recapture_advice(hist)
    hist.corroboration = decision_corroboration(hist)
    hist.noise_floor = noise_floor(points, baseline_delta)
    top = hist.attribution.top if hist.attribution else None
    hist.attributed_pillar_noise_floor = (
        pillar_noise_floor(points, top.domain, top.pillar, baseline_delta)
        if top is not None
        else None
    )
    hist.liveness = liveness(latest, now)
    return hist


def noise_floor(
    points: list[CanonicalPoint], baseline_delta: float = FIXTURE_BASELINE_DELTA
) -> NoiseFloor | None:
    """Measure the at-rest measurement-noise floor over the in-band readings.

    Dispersion of the delta among the readings the band calls in-band
    (``|delta - baseline| <= _BAND_IN``). None when fewer than 2 such readings exist
    — dispersion is undefined for a single point, and we make no measured claim we
    can't support (the same honest-None discipline attribution applies). Pure, no
    score, no side effects.
    """
    in_band = [p for p in points if abs(p.delta - baseline_delta) <= _BAND_IN]
    if len(in_band) < 2:
        return None
    deltas = [p.delta for p in in_band]
    return NoiseFloor(
        n_in_band=len(in_band),
        stddev=round(pstdev(deltas), 6),
        max_abs_divergence=round(max(abs(d - baseline_delta) for d in deltas), 6),
        no_rails_stddev=round(pstdev([p.no_rails_overall for p in in_band]), 6),
        with_rails_stddev=round(pstdev([p.with_rails_overall for p in in_band]), 6),
    )


def pillar_noise_floor(
    points: list[CanonicalPoint],
    domain: str,
    pillar: str,
    baseline_delta: float = FIXTURE_BASELINE_DELTA,
) -> PillarNoiseFloor | None:
    """At-rest dispersion of one side's one pillar over the in-band readings.

    The pillar-granularity counterpart of ``noise_floor``: over the readings the band
    calls in-band (``|delta - baseline| <= _BAND_IN``), how much does ``domain``'s
    ``pillar`` vary? ``domain`` selects the side (the with-rails vs no-rails reference
    host); readings where that side's pillar is not numeric (unobserved on an error
    crawl) are dropped, never counted as a zero. None for an unknown domain, or when
    fewer than 2 in-band readings carry the pillar — dispersion is undefined for one
    point (the same honest-None discipline ``noise_floor`` follows). Pure, no score.
    """
    if domain == CANONICAL_WITH_RAILS:
        side = lambda p: p.with_rails_pillars.get(pillar)  # noqa: E731
    elif domain == CANONICAL_NO_RAILS:
        side = lambda p: p.no_rails_pillars.get(pillar)  # noqa: E731
    else:
        return None
    values = [
        v
        for p in points
        if abs(p.delta - baseline_delta) <= _BAND_IN and (v := side(p)) is not None
    ]
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return PillarNoiseFloor(
        domain=domain,
        pillar=pillar,
        n_in_band=len(values),
        stddev=round(pstdev(values), 6),
        max_abs_divergence=round(max(abs(v - mean) for v in values), 6),
    )


def sustained_run(
    points: list[CanonicalPoint], run: int
) -> SustainedRun | None:
    """Measure the wall-clock span of the trailing out-of-band run.

    Hours from the FIRST reading of the trailing out-of-band run (``points[-run]``)
    to the latest. None when the run is empty (``run < 1`` — the series is in-band)
    or either endpoint timestamp is unparseable (honest-None, never a fabricated
    duration). A lone out-of-band reading (``run == 1``) spans 0h by construction —
    a real fact: one reading has no persistence in time. Pure, no score.
    """
    if run < 1 or run > len(points):
        return None
    first = points[-run]
    latest = points[-1]
    t0 = _parse_ts(first.ts)
    t1 = _parse_ts(latest.ts)
    if t0 is None or t1 is None:
        return None
    span = max(0.0, (t1 - t0).total_seconds() / 3600.0)
    return SustainedRun(
        n=run, span_hours=round(span, 3), first_ts=first.ts, latest_ts=latest.ts
    )


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


def attribution_stability(
    points: list[CanonicalPoint], run: int
) -> AttributionStability | None:
    """Measure whether the fingered pillar holds across the trailing out-of-band run.

    For each reading of the trailing out-of-band run (``points[-run:]``), compute its
    top pillar-mover vs the SAME in-band anchor ``_attribute`` uses
    (``points[-(run+1)]``), and record whether they all finger the same pillar.
    Gated to a genuine stability question: ``run >= 2`` (one reading cannot wander)
    AND an earlier in-band anchor exists (``run < len(points)``) — otherwise honest
    None, matching ``_attribute``'s discipline. Pure, no score, no side effects.
    """
    if run < 2 or run >= len(points):
        return None
    anchor = points[-(run + 1)]
    readings: list[ReadingTop] = []
    for pt in points[-run:]:
        moves = _pillar_moves(
            CANONICAL_NO_RAILS, anchor.no_rails_pillars, pt.no_rails_pillars
        ) + _pillar_moves(
            CANONICAL_WITH_RAILS, anchor.with_rails_pillars, pt.with_rails_pillars
        )
        moves.sort(key=lambda m: abs(m.change), reverse=True)
        readings.append(ReadingTop(ts=pt.ts, top=moves[0] if moves else None))
    return AttributionStability(anchor_ts=anchor.ts, readings=readings)


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


def recapture_advice(history: CanonicalHistory) -> RecaptureAdvice:
    """Recommend whether the pinned canonical fixture should be re-captured.

    Pure synthesis of the already-computed drift signals — a decision, never an
    action (re-capture is a [LOCAL], baseline-moving step). The honest cases:

      - in-band -> ``REC_VALID``: the live delta reproduces the pinned delta, so
        the committed baseline still represents the true capability gap.
      - out of band but the trailing run is shorter than ``_SUSTAINED_MIN`` ->
        ``REC_WAIT``: could be live/static jitter; not yet a real move, so wait.
      - sustained out of band, driven by the WITH-RAILS reference SOFTENING
        (``reference_degraded``) -> ``REC_DEFER``: a real-world site change, not the
        capability gap closing; the pinned fixture still represents the true gap, so
        DEFER re-capture until the reference recovers. (This is the case the live
        2026-07-27 drift kept hitting — and the site did recover, vindicating it.)
      - sustained out of band, but both references moved by EQUAL magnitude in
        opposite directions (``side_ambiguous``) -> ``REC_AMBIGUOUS``: the gap moved
        but the overall scores cannot break which SIDE drove it, so a confident
        re-capture would gamble on a coin-flip (a floor gain that re-pins vs a
        reference dip that should wait). Needs a human look before the
        comparability-affecting re-capture. Distinct from ``REC_REVIEW`` (which
        fires when there is NO in-band anchor at all): here the anchor exists, the
        gap move is real, only the attribution is a tie.
      - sustained out of band, the baseline genuinely moved (no-rails gaining, or
        the reference durably improving) -> ``REC_RECAPTURE``: a real capability-gap
        change, so a [LOCAL] re-capture would re-pin the baseline.
      - sustained out of band but no in-band anchor exists in the live series to
        attribute against -> ``REC_REVIEW``: needs a human look before any action.
    """
    latest = history.latest
    if latest is None:
        return RecaptureAdvice(REC_NO_DATA, "no live re-scores recorded yet")
    if history.band == BAND_IN:
        return RecaptureAdvice(
            REC_VALID,
            "the live delta reproduces the pinned fixture delta — the committed "
            "baseline still represents the true capability gap; no re-capture",
        )
    n = history.consecutive_out_of_band
    if n < _SUSTAINED_MIN:
        return RecaptureAdvice(
            REC_WAIT,
            f"the live delta is out of band but only {n} consecutive re-score(s) — "
            f"not yet sustained ({_SUSTAINED_MIN}+); could be live/static jitter, wait",
        )
    cause = history.divergence_cause
    if cause is None:
        return RecaptureAdvice(
            REC_REVIEW,
            "sustained out of band, but no in-band anchor exists in the live series "
            "to attribute the move against — a human look is needed before re-capture",
        )
    if cause.reference_degraded:
        return RecaptureAdvice(
            REC_DEFER,
            f"sustained out of band, but the {cause.driver} reference SOFTENED "
            f"({cause.driver_change:+.1f}) — a real-world site change, not the "
            "capability gap closing; the pinned fixture still represents the true "
            "gap, so DEFER re-capture until the reference recovers",
        )
    if cause.side_ambiguous:
        return RecaptureAdvice(
            REC_AMBIGUOUS,
            f"sustained out of band and the gap moved ({cause.gap_change:+.1f}), but "
            f"the SIDE is unattributed — both references moved by equal magnitude "
            f"(no-rails {cause.no_rails_change:+.1f} / with-rails "
            f"{cause.with_rails_change:+.1f}), so whether the capability FLOOR rose "
            "(a durable gap close -> re-capture) or the reference SOFTENED (a "
            "real-world dip -> defer) is a tie the overall scores cannot break; a "
            "human look is needed before the comparability-affecting re-capture",
        )
    return RecaptureAdvice(
        REC_RECAPTURE,
        f"sustained out of band and the baseline genuinely moved ({cause.driver} "
        f"{cause.driver_change:+.1f}) — a durable capability-gap change, not a "
        "reference outage; a [LOCAL] fixture re-capture would re-pin the baseline "
        "(comparability-affecting: it moves the pinned delta the replay guard asserts)",
    )


_REC_LABEL = {
    REC_NO_DATA: "no data",
    REC_VALID: "baseline valid",
    REC_WAIT: "wait",
    REC_DEFER: "defer re-capture",
    REC_RECAPTURE: "re-capture candidate",
    REC_REVIEW: "review",
    REC_AMBIGUOUS: "review (side unattributed)",
}


def decision_corroboration(
    history: CanonicalHistory,
) -> DecisionCorroboration | None:
    """Whether the re-capture decision is corroborated by both drift mechanisms.

    Pure read over the already-computed ``divergence_cause`` (side-level, OVERALL
    scores) and ``attribution`` (pillar-level, per-pillar scores). None unless BOTH
    are present and the pillar mechanism isolated a single top mover — a decision the
    two mechanisms cannot both speak to is never claimed corroborated. No score, no
    side effects.
    """
    cause = history.divergence_cause
    attr = history.attribution
    if cause is None or attr is None or attr.top is None:
        return None
    top = attr.top
    return DecisionCorroboration(
        driver=cause.driver,
        driver_change=cause.driver_change,
        pillar_domain=top.domain,
        pillar=top.pillar,
        pillar_change=top.change,
    )


def corroboration_verdict(corr: DecisionCorroboration) -> str:
    """A capability-lens sentence: do the two INDEPENDENT decompositions concur on
    the driver, and so does the re-capture decision rest on two signals or one?

    Vendor-neutral: the domains come straight from ``corr`` (the module's reference-
    pair constants), named only as data — the sentence keys on whether the two sides
    MATCH, never on which host it is.
    """
    if corr.corroborated:
        return (
            f"CORROBORATED — the side-level decomposition ({corr.driver} overall "
            f"{corr.driver_change:+.1f}) and the INDEPENDENT pillar-level decomposition "
            f"({corr.pillar_domain} {corr.pillar} {corr.pillar_change:+.1f}) finger the "
            f"same side moving the same way, so the decision rests on two independent "
            f"signals concurring, not one number"
        )
    if not corr.same_side:
        return (
            f"NOT corroborated — the side-level decomposition blames {corr.driver} "
            f"({corr.driver_change:+.1f}) but the largest pillar move is on a different "
            f"side ({corr.pillar_domain} {corr.pillar} {corr.pillar_change:+.1f}); the two "
            f"mechanisms disagree on the driver, so weigh the recommendation with caution"
        )
    return (
        f"NOT corroborated — {corr.driver} drives both decompositions, but its overall "
        f"({corr.driver_change:+.1f}) and its largest pillar move ({corr.pillar} "
        f"{corr.pillar_change:+.1f}) point OPPOSITE ways, so weigh the recommendation "
        f"with caution"
    )


def load_history(
    runs_dir: str | None = None, *, now: datetime | None = None
) -> CanonicalHistory:
    points, accounting = load_points_accounted(runs_dir)
    return summarize(points, now=now, accounting=accounting)


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


def cause_verdict(cause: DivergenceCause, top: PillarMove | None = None) -> str:
    """A capability-lens sentence naming which SIDE drove the divergence.

    Keys on (driver side, driver direction) — the four honest cases. Because the
    driver is the dominant side, its direction fixes whether the gap narrowed or
    widened, so the sentence never contradicts ``gap_change``.

    The FIFTH case is a tie (``side_ambiguous``): both references moved by equal
    magnitude in opposite directions, so ``driver`` resolves to the no-rails floor
    by convention, not by evidence. There the sentence states the gap move but
    calls the SIDE unattributed instead of asserting a confident floor gain — a
    with-rails softening of the same magnitude is exactly as consistent.

    When ``top`` (the largest per-pillar mover from ``PillarAttribution``) is
    supplied AND the two INDEPENDENT attribution mechanisms concur, the sentence
    also names the fingered PILLAR — "SOFTENED on transactability", not only "the
    with-rails side softened". Concurrence means the isolated pillar sits on the
    SAME domain the side-level cause blames (``top.domain == cause.driver`` — the
    cross-mechanism agreement the real-series guard pins) AND moved the SAME
    direction as that side's overall (``sign(top.change) == sign(driver_change)``,
    so the named pillar genuinely moved the way the verb says). When the two
    signals disagree, or no single pillar isolated (``top`` None — a pillar
    unobserved on one side, where the side cause is still defined but no pillar
    is), the prose falls back to the side-only wording, byte-for-byte the
    pre-pillar form, rather than assert a pillar the mechanisms don't corroborate.
    """
    if cause.side_ambiguous:
        # The two references moved by equal magnitude in opposite directions: the
        # gap really moved, but ``driver`` tie-breaks to the no-rails floor by
        # convention, not by evidence. Say the gap moved and that the SIDE is
        # unattributed rather than present the tie as a confident floor gain — a
        # with-rails softening of the same magnitude is exactly as consistent.
        direction = "narrowed" if cause.gap_change < 0 else "widened"
        return (
            f"the gap {direction} {cause.gap_change:+.1f}, but the SIDE is "
            f"unattributed — both references moved by equal magnitude "
            f"({CANONICAL_NO_RAILS} {cause.no_rails_change:+.1f}, "
            f"{CANONICAL_WITH_RAILS} {cause.with_rails_change:+.1f}), so which "
            f"drove it is a tie (read conservatively as gap movement, not "
            f"reference degradation)"
        )
    driver = cause.driver
    change = cause.driver_change
    verb = "fell" if change < 0 else "rose"
    on_pillar = ""
    if (
        top is not None
        and top.domain == driver
        and (top.change < 0) == (change < 0)
    ):
        on_pillar = f" on {top.pillar}"
    if driver == CANONICAL_NO_RAILS:
        if change > 0:
            meaning = (
                f"the capability gap narrowed because the no-rails reference GAINED "
                f"capability{on_pillar} — a real benchmark movement, not a reference "
                f"outage"
            )
        else:
            meaning = (
                f"the gap widened because the no-rails reference LOST ground{on_pillar}"
            )
    else:  # with-rails driver
        if change < 0:
            meaning = (
                f"the gap narrowed because the with-rails reference SOFTENED"
                f"{on_pillar} (a real-world site change), not because the no-rails "
                f"side gained capability — the pinned fixture still represents the "
                f"true gap"
            )
        else:
            meaning = (
                f"the gap widened because the with-rails reference GAINED "
                f"capability{on_pillar}"
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


def _exclusion_phrase(acct: LoadAccounting) -> str:
    """"k red-bench, j malformed" — only the non-zero reasons, in a fixed order, so
    the readout names WHY the series was filtered without listing empty causes.
    Shared by both surfaces (terminal + HTML) so they phrase the exclusion the same.
    """
    parts = []
    if acct.excluded_red_bench:
        parts.append(f"{acct.excluded_red_bench} red-bench")
    if acct.excluded_malformed:
        parts.append(f"{acct.excluded_malformed} malformed")
    return ", ".join(parts)


def render(history: CanonicalHistory, window: int = 24) -> str:
    """Render the history as a terminal block."""
    lines = ["CANONICAL DELTA HISTORY", "-" * 23]
    pts = history.points
    if not pts:
        acct0 = history.load_accounting
        if acct0 is not None and acct0.total > 0:
            # Artifacts were found but ALL filtered out — the maximally degraded
            # integrity case: name it rather than imply the runner produced nothing.
            lines.append(
                f"(no usable live-verify artifacts — {acct0.total} found, all "
                f"{acct0.excluded} excluded: {_exclusion_phrase(acct0)})"
            )
        else:
            lines.append("(no usable live-verify artifacts found)")
        return "\n".join(lines)
    lines.append(
        f"series: {len(pts)} live re-scores  "
        f"{_short_ts(pts[0].ts)} → {_short_ts(pts[-1].ts)}"
    )
    acct = history.load_accounting
    if acct is not None and acct.any_excluded:
        lines.append(
            f"series filtered: {acct.included} of {acct.total} artifacts kept, "
            f"{acct.excluded} excluded ({_exclusion_phrase(acct)}) — "
            f"red-bench = scored while the bench's own guards were red (not "
            f"comparable within the version); malformed = unusable artifact"
        )
        # The counts above say WHAT was dropped; this JUDGES whether the drop
        # compromises the series the drift verdict is drawn from (Cycle 217). Only
        # shown when something was filtered — a clean load has nothing to judge.
        integ = history.integrity
        if integ is not None:
            rb = (
                f", {integ.excluded_red_bench} of them red-bench"
                if integ.excluded_red_bench
                else ""
            )
            if integ.intact:
                lines.append(
                    f"series integrity: INTACT — {integ.excluded}/{integ.total} "
                    f"({integ.excluded_fraction * 100:.0f}%) excluded{rb}, within "
                    f"the {integ.floor * 100:.0f}% floor; the drift verdict rests on "
                    f"a representative series"
                )
            else:
                lines.append(
                    f"series integrity: DEGRADED — {integ.excluded}/{integ.total} "
                    f"({integ.excluded_fraction * 100:.0f}%) of the committed series "
                    f"excluded{rb}, PAST the {integ.floor * 100:.0f}% floor; the drift "
                    f"verdict rests on a thinned/biased remnant — weigh it with caution"
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
    live = history.liveness
    if live is not None:
        if live.fresh:
            lines.append(
                f"live signal: newest re-score {live.age_hours:.1f}h old "
                f"— FRESH (within the {live.stale_floor_hours:.0f}h floor)"
            )
        else:
            lines.append(
                f"live signal: newest re-score {live.age_hours:.1f}h old "
                f"— STALE (past the {live.stale_floor_hours:.0f}h floor): the verdict "
                f"below describes an OLD crawl, not the pair now — the local verify "
                f"runner may be down"
            )
    div = history.divergence
    lines.append(
        f"divergence from baseline: {_fmt_delta(div)}  "
        f"({history.band.upper()} — {_BAND_VERDICT[history.band]})"
    )
    if history.consecutive_out_of_band >= 1:
        n = history.consecutive_out_of_band
        kind = "sustained" if n >= _SUSTAINED_MIN else "recent"
        sr = history.sustained_run
        span = (
            f" spanning {sr.span_hours:.1f}h "
            f"({_short_ts(sr.first_ts)} → {_short_ts(sr.latest_ts)})"
            if sr is not None
            else ""
        )
        lines.append(
            f"{kind}: {n} consecutive re-score(s) out of band{span} "
            f"(|delta - baseline| > {_BAND_IN:.1f})"
        )
    nf = history.noise_floor
    if nf is not None:
        if nf.deterministic:
            sides = (
                f"  both sides exact (σ {CANONICAL_NO_RAILS}={nf.no_rails_stddev:.2f}, "
                f"{CANONICAL_WITH_RAILS}={nf.with_rails_stddev:.2f}) — the stable delta "
                f"is genuine per-side determinism, not two drifts cancelling"
                if nf.sides_deterministic
                else ""
            )
            lines.append(
                f"noise floor: {nf.n_in_band} in-band re-scores  σ={nf.stddev:.2f}  "
                f"worst |div|={nf.max_abs_divergence:.2f}  → DETERMINISTIC at rest — "
                f"the ±{_BAND_IN:.1f} band absorbs site transients, not measurement noise"
                f"{sides}"
            )
        else:
            sep = "well-separated" if nf.band_well_separated else "TOO TIGHT for observed noise"
            lines.append(
                f"noise floor: {nf.n_in_band} in-band re-scores  σ={nf.stddev:.2f}  "
                f"worst |div|={nf.max_abs_divergence:.2f}  "
                f"(±{_BAND_IN:.1f} in-band band {sep})"
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
    pnf = history.attributed_pillar_noise_floor
    if pnf is not None and attr is not None and attr.top is not None:
        move = attr.top.change
        if pnf.deterministic:
            lines.append(
                f"pillar noise floor: {pnf.domain} {pnf.pillar} σ={pnf.stddev:.2f} "
                f"over {pnf.n_in_band} in-band re-scores → DETERMINISTIC at rest — "
                f"the {move:+.1f} move is signal, not pillar jitter"
            )
        else:
            lines.append(
                f"pillar noise floor: {pnf.domain} {pnf.pillar} σ={pnf.stddev:.2f} "
                f"(worst |div|={pnf.max_abs_divergence:.2f}) over {pnf.n_in_band} "
                f"in-band re-scores — the {move:+.1f} move against the at-rest pillar jitter"
            )
    stab = history.attribution_stability
    if stab is not None:
        if stab.stable and stab.fingered is not None:
            dom, pil = stab.fingered
            lines.append(
                f"attribution stability: {dom} {pil} fingered by all "
                f"{len(stab.readings)} out-of-band re-scores — STABLE, not wandering"
            )
        else:
            movers = (
                "; ".join(f"{d} {p}" for d, p in sorted(stab.movers))
                or "no single pillar isolated"
            )
            lines.append(
                f"attribution stability: top mover WANDERS across "
                f"{len(stab.readings)} out-of-band re-scores ({movers}) "
                f"— the fingered pillar is not sustained"
            )
    cause = history.divergence_cause
    if cause is not None:
        top = attr.top if attr is not None else None
        lines.append(f"driver: {cause_verdict(cause, top)}")
    adv = history.recapture
    if adv is not None and adv.code != REC_NO_DATA:
        lines.append(f"re-capture: {_REC_LABEL.get(adv.code, adv.code)} — {adv.reason}")
        corr = history.corroboration
        if corr is not None:
            lines.append(f"corroboration: {corroboration_verdict(corr)}")
    tail = pts[-window:]
    lines.append(
        f"delta trend (last {len(tail)}): {_spark([p.delta for p in tail])}"
    )
    return "\n".join(lines)
