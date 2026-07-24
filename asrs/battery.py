"""Task battery — score a storefront across DIVERSE intents, not one task.

A single shopper task is one draw from a wide distribution: the storefront's
readiness for "buy an image" says little about its readiness for "subscribe to
the API" or "order the physical good". A *battery* runs the existing shopper
panel once per intent and aggregates the resulting checkpoint ladders into two
things a single run cannot give:

  - COVERAGE — per-task checkpoint attainment, so a site can be read per intent
    (and per storefront archetype, ``kind``);
  - RELIABILITY — cross-task variance of each checkpoint. Low spread means the
    site behaves the same whatever the agent was sent to do; high spread means
    its readiness is intent-dependent, and the best single run overstates it.

Design boundaries (loop invariants):
  - The rubric stays TASK-AGNOSTIC. This module adds NO check, weight, or cap
    and does not feed the overall score. It is a diagnostic layer over the
    ``BehavioralRun`` records the shopper panel already emits — a READOUT/METHOD
    reliability signal, not a scoring-semantics change (no rubric version bump).
  - "Valid run" and the checkpoint ladder are defined ONCE, in
    :mod:`asrs.behavioral.shopper`; this module imports them so the battery and
    the per-task score never diverge on what counts as observing the site.
  - $0-only / one-free-tier-attempt is NOT touched here: aggregation consumes
    already-collected runs. When the CLI wires ``--battery`` (queued [LOCAL]),
    the free-tier transaction probe must still fire at most ONCE for the whole
    battery (it consumes the target's allowance), while the shopper panel runs
    per task. That constraint lives with the runner, not this math.

Pure stdlib + dataclasses; unit-testable with synthetic runs, no network.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Single source of truth for the checkpoint ladder and for what counts as a run
# that actually observed the site. Importing the shopper's definitions (rather
# than re-listing them) keeps the battery and the per-task score in lockstep.
from asrs.behavioral.shopper import _CHECKPOINT_KEYS, _is_env_blocked
# The offering-relative battery (operator directive): discovery decides WHICH
# archetype intents run against a site. offering.py imports nothing from asrs, so
# this dependency is one-directional (no cycle).
from asrs.offering import ARCHETYPES, ArchetypeClaim, OfferingProfile
from asrs.types import BehavioralRun


DEFAULT_BATTERY_PATH = Path(__file__).resolve().parent.parent / "batteries" / "default_v1.yaml"


# --------------------------------------------------------------------------
# battery definition (the input file)
# --------------------------------------------------------------------------

@dataclass
class BatteryTask:
    id: str
    kind: str  # storefront archetype: digital_service | data_job | subscription | physical_good | ...
    intent: str  # the shopper task prompt, worded by capability (vendor-neutral)


@dataclass
class Battery:
    id: str
    description: str
    tasks: list[BatteryTask] = field(default_factory=list)


def load_battery(path: str | Path | None = None) -> Battery:
    """Load a battery YAML into a :class:`Battery`.

    Raises ``ValueError`` on a structurally invalid file (missing tasks, a task
    without an ``id`` or ``intent``, duplicate task ids) so a typo fails loud
    rather than silently scoring fewer intents than intended.
    """
    import yaml  # lazy: keep module import cheap

    battery_path = Path(path) if path is not None else DEFAULT_BATTERY_PATH
    with open(battery_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError(f"battery file {battery_path} is not a mapping")

    raw_tasks = raw.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise ValueError(f"battery {battery_path} has no 'tasks' list")

    tasks: list[BatteryTask] = []
    seen: set[str] = set()
    for i, t in enumerate(raw_tasks):
        if not isinstance(t, dict):
            raise ValueError(f"battery task #{i} is not a mapping")
        tid = str(t.get("id") or "").strip()
        intent = str(t.get("intent") or "").strip()
        if not tid:
            raise ValueError(f"battery task #{i} has no 'id'")
        if not intent:
            raise ValueError(f"battery task {tid!r} has no 'intent'")
        if tid in seen:
            raise ValueError(f"battery has duplicate task id {tid!r}")
        seen.add(tid)
        tasks.append(BatteryTask(id=tid, kind=str(t.get("kind") or "unspecified").strip(), intent=intent))

    return Battery(
        id=str(raw.get("id") or battery_path.stem),
        description=str(raw.get("description") or "").strip(),
        tasks=tasks,
    )


# --------------------------------------------------------------------------
# offering-relative instantiation (operator directive, brick 2)
# --------------------------------------------------------------------------
#
# A hand-authored battery YAML runs the SAME fixed intent list against every
# site, so an image-generation API gets probed with "order a physical good" and
# its partial completion pollutes the means and both spreads — the battery's
# mismatch, not the site's readiness (operator directive, 2026-07-23). Brick 1
# (:mod:`asrs.offering`) discovers which capability ARCHETYPES a site CLAIMS to
# serve. This brick turns that discovery into the battery's task set: a FIXED
# per-archetype intent template bank (for cross-site comparability), instantiated
# for a site by keeping only the archetypes it claims. An image API gets the
# metered/digital/subscription intents and NO physical-good task; a shop gets the
# inverse; neither is charged for an archetype it does not offer.
#
# VOCABULARY RECONCILIATION: the canonical task vocabulary is now
# ``offering.ARCHETYPES`` (metered_api / subscription / digital_good /
# physical_good / service_booking / data_retrieval) — the operator directive's
# taxonomy and the discovery output. An instantiated task's ``id`` AND ``kind``
# are the archetype name, so the per-``kind`` rollup groups by archetype and the
# same archetype id lines up across sites (brick 5 comparability). Hand-authored
# YAMLs keep their free-form ``kind`` grouping labels (digital_service / data_job
# / ...) and still load unchanged; only the GENERATED batteries adopt the
# canonical archetype vocabulary.
#
# SCORE-NEUTRAL: this is task SELECTION only — it constructs a :class:`Battery`,
# it does not touch the aggregation math, any check, weight, cap, or the rubric.
# The NA-aware aggregation (unclaimed archetypes recorded NA and excluded from
# the means/spreads) is the later, peer-gated brick 3; here an unclaimed
# archetype is simply not a task, so it already never contributes signal.

# Fixed archetype intent template bank. Each intent is a self-contained,
# vendor-neutral capability job that references the site's OWN offering
# generically ("the service's metered API", "the site's primary physical
# product"), never a named product or domain. Intent wording for the archetypes
# that also appear in ``default_v1.yaml`` is kept in step with that file so the
# generated and hand-authored batteries do not diverge on phrasing.
_ARCHETYPE_INTENTS: dict[str, str] = {
    "metered_api": (
        "invoke the service's metered API once and pay for that single call "
        "programmatically as an autonomous agent, without a human in the loop"
    ),
    "subscription": (
        "provision ongoing programmatic access to the service's primary API on a "
        "metered or subscription plan, as an autonomous agent, without a sales call"
    ),
    # digital_good carries a {descriptor} slot filled from discovered, vendor-
    # neutral media language (see :func:`_digital_good_descriptor`).
    "digital_good": (
        "obtain one {descriptor} from the service and pay for that single output "
        "programmatically as an autonomous agent, without a human in the loop"
    ),
    "physical_good": (
        "purchase one unit of the site's primary physical product and complete "
        "payment programmatically as an autonomous agent"
    ),
    "service_booking": (
        "book one unit of the site's primary service — an appointment, "
        "reservation, or time slot — and complete payment or confirmation "
        "programmatically as an autonomous agent"
    ),
    "data_retrieval": (
        "enrich a list of records against the service's data and pay for the job "
        "programmatically as an autonomous agent"
    ),
}

# Generic media nouns (never a vendor term) used to specialize the digital_good
# intent from the archetype's own fired signals — the operator's example of
# "buy an AI-generated image" for an image API, derived from OUR signal bank
# rather than from injected raw site text.
_MEDIA_RE = re.compile(r"\b(image|video|audio|art)\b", re.IGNORECASE)


def _digital_good_descriptor(claim: ArchetypeClaim | None) -> str:
    """A short, vendor-neutral noun for what the digital_good intent should buy.

    Derived only from the archetype's fired signal labels/quotes (generic media
    words from :mod:`asrs.offering`'s own bank), never from arbitrary injected
    site prose, so it stays vendor-neutral and injection-safe. Falls back to the
    generic "digital output" when discovery gives no cleaner media hint.
    """
    if claim is None:
        return "digital output"
    labels = {s.label for s in claim.signals}
    if "translation" in labels:
        return "translated document"
    for sig in claim.signals:
        m = _MEDIA_RE.search(sig.quote)
        if m:
            return f"generated {m.group(1).lower()}"
    return "digital output"


def _intent_for(archetype: str, claim: ArchetypeClaim | None) -> str:
    """Fill the archetype's template, parameterized by the discovered offering."""
    template = _ARCHETYPE_INTENTS[archetype]
    if "{descriptor}" in template:
        return template.format(descriptor=_digital_good_descriptor(claim))
    return template


def instantiate_battery(
    profile: OfferingProfile,
    *,
    battery_id: str | None = None,
    description: str | None = None,
) -> Battery:
    """Build an OFFERING-RELATIVE battery from a discovered offering profile.

    Emits one :class:`BatteryTask` per archetype the site CLAIMS (in fixed
    template-bank order for a stable, comparable readout), with ``id`` and
    ``kind`` set to the archetype name and the intent drawn from the fixed
    template bank, parameterized by the site's discovered evidence. Archetypes
    the site does not claim are omitted — an image API yields no physical-good
    task, a shop no metered-API task — so the battery only ever runs intents the
    site actually offers. A profile that claims nothing yields an empty battery
    (an honest "nothing to assess", never a fabricated task).

    Score-neutral: constructs a battery definition; does not touch scoring or the
    aggregation math.
    """
    by_archetype = {c.archetype: c for c in profile.claimed}
    tasks: list[BatteryTask] = [
        BatteryTask(
            id=archetype,
            kind=archetype,
            intent=_intent_for(archetype, by_archetype[archetype]),
        )
        for archetype in ARCHETYPES
        if archetype in by_archetype
    ]
    domain = profile.domain or "site"
    return Battery(
        id=battery_id or f"offering_{domain}",
        description=(
            description
            if description is not None
            else (
                "Offering-relative battery: one intent per archetype "
                f"{domain} claims to serve ({', '.join(t.kind for t in tasks) or 'none'})."
            )
        ),
        tasks=tasks,
    )


# --------------------------------------------------------------------------
# aggregation (the output)
# --------------------------------------------------------------------------

@dataclass
class BatteryTaskResult:
    task_id: str
    kind: str
    attempted_runs: int
    valid_runs: int  # runs that produced a verdict AND reached the site
    # Per-checkpoint pass fraction over valid runs; None for every checkpoint
    # when the task produced no valid run (no signal — never a site failure).
    checkpoint_fractions: dict[str, float | None] = field(default_factory=dict)
    # Mean of the checkpoint fractions — a single 0..1 "how far did agents get"
    # for this intent. None when no valid run.
    mean_completion: float | None = None

    @property
    def has_signal(self) -> bool:
        return self.valid_runs > 0


@dataclass
class BatteryKindResult:
    """Per-storefront-archetype rollup (``kind``) across the battery.

    A site is rarely uniformly agent-ready: it can ace digital metered services
    yet stumble on physical goods. Grouping the per-task results by ``kind`` lets
    the same run be read per archetype — "great at digital_service, weak at
    physical_good" — instead of collapsing to one battery-wide number. Same
    diagnostic status as the rest of the battery: no check, weight, or cap.
    """
    kind: str
    n_tasks: int
    tasks_with_signal: int
    # Mean of the per-task ``mean_completion`` over this kind's signal tasks —
    # how far agents got, on average, on this archetype. None when no signal.
    mean_completion: float | None = None
    # Reliability spread WITHIN this archetype (mean per-checkpoint stddev over
    # the kind's signal tasks). 0.0 for a single signal task (no variance to
    # observe yet); None when the archetype produced no signal.
    cross_task_spread: float | None = None


@dataclass
class BatterySummary:
    battery_id: str
    n_tasks: int
    tasks_with_signal: int
    per_task: list[BatteryTaskResult] = field(default_factory=list)
    # Per storefront archetype (``kind``): the battery-wide numbers, sliced so a
    # site can be read one archetype at a time. Insertion-ordered by first
    # appearance in the battery.
    per_kind: list[BatteryKindResult] = field(default_factory=list)
    # Across tasks-with-signal, per checkpoint: mean pass fraction and the
    # population stddev of the per-task fractions (the reliability spread).
    checkpoint_mean: dict[str, float | None] = field(default_factory=dict)
    checkpoint_spread: dict[str, float | None] = field(default_factory=dict)
    # Mean of the per-checkpoint spreads — the headline reliability signal.
    # 0.0 = the site behaves identically across every intent; higher = its
    # readiness is intent-dependent. None when < 1 task has signal.
    cross_task_spread: float | None = None
    # Variance ATTRIBUTABLE to storefront type: the population stddev of the
    # per-kind mean_completion values across archetypes with signal. Decomposes
    # the battery-wide cross_task_spread into two named sources — within-type
    # noise (per_kind[].cross_task_spread) vs between-type SPECIALIZATION (this).
    # 0.0 = readiness is uniform across storefront types (a generalist); higher
    # = the site is type-specialized (strong on some archetypes, weak on
    # others) and an overall number hides it. None when fewer than 2 archetypes
    # have signal — between-type variance is unobservable with a single type
    # observed (deliberately None, not a measured-uniform 0.0: attribution
    # honesty — never report a spread that couldn't be observed).
    between_kind_spread: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _valid_runs(runs: list[BehavioralRun]) -> list[BehavioralRun]:
    """Runs that observed the site: a parsed verdict AND not env-blocked.

    Mirrors ``shopper._aggregate`` exactly (a run with checkpoints that its own
    hosting stack refused observed nothing about the site and is dropped).
    """
    return [r for r in runs if r.checkpoints and not _is_env_blocked(r)]


def _task_result(task: BatteryTask, runs: list[BehavioralRun]) -> BatteryTaskResult:
    valid = _valid_runs(runs)
    n = len(valid)
    if n == 0:
        return BatteryTaskResult(
            task_id=task.id,
            kind=task.kind,
            attempted_runs=len(runs),
            valid_runs=0,
            checkpoint_fractions={k: None for k in _CHECKPOINT_KEYS},
            mean_completion=None,
        )

    fractions: dict[str, float | None] = {}
    for key in _CHECKPOINT_KEYS:
        passes = sum(1 for r in valid if r.checkpoints.get(key))
        fractions[key] = passes / n

    present = [f for f in fractions.values() if f is not None]
    mean_completion = statistics.fmean(present) if present else None

    return BatteryTaskResult(
        task_id=task.id,
        kind=task.kind,
        attempted_runs=len(runs),
        valid_runs=n,
        checkpoint_fractions=fractions,
        mean_completion=mean_completion,
    )


def _cross_task_spread(signal_results: list[BatteryTaskResult]) -> float | None:
    """Mean per-checkpoint reliability spread over a set of signal task results.

    The same math the battery-wide ``cross_task_spread`` uses, factored out so a
    per-archetype slice is computed identically to the whole. Population stddev
    per checkpoint (a single signal task has spread 0.0, not undefined), averaged
    across the checkpoints that any of these tasks observed. None when the set is
    empty (no signal to observe).
    """
    spreads: list[float] = []
    for key in _CHECKPOINT_KEYS:
        vals = [
            tr.checkpoint_fractions.get(key)
            for tr in signal_results
            if tr.checkpoint_fractions.get(key) is not None
        ]
        if vals:
            spreads.append(statistics.pstdev(vals) if len(vals) > 1 else 0.0)
    return statistics.fmean(spreads) if spreads else None


def _per_kind_results(per_task: list[BatteryTaskResult]) -> list[BatteryKindResult]:
    """Roll the per-task results up per storefront archetype (``kind``).

    Grouped by first appearance so the readout order is stable. Stats are over
    each kind's SIGNAL tasks only (an archetype is never charged completion or
    variance for an intent nobody could observe), mirroring the battery-wide
    rollup exactly.
    """
    order: list[str] = []
    by_kind: dict[str, list[BatteryTaskResult]] = {}
    for tr in per_task:
        if tr.kind not in by_kind:
            by_kind[tr.kind] = []
            order.append(tr.kind)
        by_kind[tr.kind].append(tr)

    out: list[BatteryKindResult] = []
    for kind in order:
        group = by_kind[kind]
        signal = [tr for tr in group if tr.has_signal]
        completions = [tr.mean_completion for tr in signal if tr.mean_completion is not None]
        out.append(
            BatteryKindResult(
                kind=kind,
                n_tasks=len(group),
                tasks_with_signal=len(signal),
                mean_completion=statistics.fmean(completions) if completions else None,
                cross_task_spread=_cross_task_spread(signal),
            )
        )
    return out


def _between_kind_spread(per_kind: list[BatteryKindResult]) -> float | None:
    """Reliability spread ATTRIBUTABLE to storefront type.

    Population stddev of the per-kind ``mean_completion`` values over the
    archetypes that produced signal — the "is this site a generalist or
    type-specialized?" number. None when fewer than 2 archetypes have signal:
    with a single storefront type observed, between-type variance is not a
    measurable property (unlike a within-checkpoint spread over one task, which
    is a defined 0), so None is the honest reading rather than a 0.0 that would
    read as "measured uniform across types".
    """
    completions = [kr.mean_completion for kr in per_kind if kr.mean_completion is not None]
    if len(completions) < 2:
        return None
    return statistics.pstdev(completions)


def aggregate_battery(
    battery: Battery, runs_by_task: dict[str, list[BehavioralRun]]
) -> BatterySummary:
    """Roll per-task shopper runs up into a battery summary.

    ``runs_by_task`` maps each battery task id to the ``BehavioralRun`` list the
    shopper panel produced for that task's intent. A task absent from the map is
    treated as attempted-with-zero-runs (no signal). Tasks with no valid run are
    excluded from the cross-task mean/spread — a site is never charged variance
    for an intent nobody could observe.
    """
    per_task = [_task_result(t, runs_by_task.get(t.id, [])) for t in battery.tasks]
    signal = [tr for tr in per_task if tr.has_signal]
    per_kind = _per_kind_results(per_task)

    checkpoint_mean: dict[str, float | None] = {}
    checkpoint_spread: dict[str, float | None] = {}
    for key in _CHECKPOINT_KEYS:
        vals = [
            tr.checkpoint_fractions.get(key)
            for tr in signal
            if tr.checkpoint_fractions.get(key) is not None
        ]
        if not vals:
            checkpoint_mean[key] = None
            checkpoint_spread[key] = None
        else:
            checkpoint_mean[key] = statistics.fmean(vals)
            # Population stddev: a single signal task has spread 0 (no variance
            # to observe yet), not undefined.
            checkpoint_spread[key] = statistics.pstdev(vals) if len(vals) > 1 else 0.0

    spreads = [s for s in checkpoint_spread.values() if s is not None]
    cross_task_spread = statistics.fmean(spreads) if (spreads and len(signal) >= 1) else None

    return BatterySummary(
        battery_id=battery.id,
        n_tasks=len(battery.tasks),
        tasks_with_signal=len(signal),
        per_task=per_task,
        per_kind=per_kind,
        checkpoint_mean=checkpoint_mean,
        checkpoint_spread=checkpoint_spread,
        cross_task_spread=cross_task_spread,
        between_kind_spread=_between_kind_spread(per_kind),
    )
