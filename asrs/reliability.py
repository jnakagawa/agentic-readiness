"""Panel reliability — how reproducible are the shopper panel's verdicts?

The shopper panel scores a domain from a handful of ``model x trial`` runs and
the overall score quotes their aggregate. But a single draw can flip: a same-day
codex trust verdict flipped refuse <-> warn at equal confidence, and a checkpoint
can pass in one trial and fail the next. When the valid runs disagree, the
aggregate is a point estimate over an unstable distribution and a single-trial
score overstates its own confidence.

This module measures WITHIN-PANEL reproducibility: for ONE task, across the valid
runs (every ``model x trial`` draw that observed the site), how much do the runs
agree on each checkpoint? It is the complement of the battery's CROSS-TASK spread
(:mod:`asrs.battery`, same checkpoint across different intents): here the intent
is held fixed and the variation being measured is the panel itself. Together they
answer two different "is this quotable?" questions — battery: does readiness
depend on the intent; reliability: does it reproduce when you just run it again.

Design boundaries (loop invariants), identical to :mod:`asrs.battery`:
  - Adds NO check, weight, or cap and does NOT feed the overall score. A
    diagnostic readout over the ``BehavioralRun`` records the panel already
    emits — no rubric version bump.
  - "Valid run" (a parsed verdict that was not env-blocked) is defined ONCE in
    :mod:`asrs.behavioral.shopper` and imported here, so reliability and the
    per-task score never diverge on what counts as observing the site.
  - Consumes already-collected runs; touches no payment / free-tier path.

Pure stdlib + dataclasses; unit-testable with synthetic runs, no network.
"""

from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass, field
from typing import Any

# Single source of truth for the checkpoint ladder and for what counts as a run
# that actually observed the site — imported, not re-listed, so reliability and
# the per-task score stay in lockstep (mirrors asrs/battery.py).
from asrs.behavioral.shopper import _CHECKPOINT_KEYS, _is_env_blocked
from asrs.types import BehavioralRun

# Descriptive stability bands (display only — NOT a scoring threshold). A run is
# never scored against these; they just name the reproducibility a human is
# looking at so the readout reads at a glance.
_STABLE_MIN = 0.8
_MIXED_MIN = 0.5


@dataclass
class CheckpointReliability:
    checkpoint: str
    n: int  # valid runs voting on this checkpoint
    pass_count: int
    # Fraction of valid runs at the MAJORITY verdict: max(pass, n-pass)/n, in
    # [0.5, 1]. 1.0 = every run agreed; 0.5 = a perfect split.
    agreement: float
    unanimous: bool


@dataclass
class PanelReliability:
    valid_runs: int
    # < 2 valid runs: reproducibility is not assessable from a single draw. The
    # metrics below are None in that case (a site is never charged for it).
    single_trial: bool
    per_checkpoint: list[CheckpointReliability] = field(default_factory=list)
    # Checkpoints (ladder order) where the valid runs did NOT all agree.
    flipped_checkpoints: list[str] = field(default_factory=list)
    # Fraction of checkpoints that were not unanimous. 0 = fully reproducible.
    flip_rate: float | None = None
    # Headline: 1 - 2 * mean(minority_fraction) over the checkpoints, in [0, 1].
    # 1.0 = every run agreed on every checkpoint; 0.0 = every checkpoint split
    # 50/50. Higher = the panel reproduces. None when single_trial.
    verdict_stability: float | None = None
    # Did the valid runs agree on whether the site raised a trust concern during
    # the session (the refuse/warn <-> clean flip)? max(warned, clean)/n.
    trust_event_agreement: float | None = None
    trust_events_unanimous: bool | None = None
    # Descriptive band for the readout (display only, never a score gate):
    # "no-signal" | "single-trial" | "stable" | "mixed" | "unstable".
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Quotability:
    """Is the report's quoted number safe to CITE, given how the evidence held up?

    A companion readout to :class:`PanelReliability`. Reliability measures *how*
    reproducible the panel is; quotability turns that into the one bit a reader
    actually needs before citing a headline number: reproducible, or provisional.

    Display-only (never a score gate). The overall score itself is unchanged in
    every case — this only annotates whether that number is quotable yet. The
    honest states, in words a card can print:
      - ``reproducible`` — a multi-trial panel that agreed; cite it.
      - ``provisional-single-trial`` — one valid draw; reproducibility unmeasured
        (the observed same-day refuse<->warn flip is exactly this risk).
      - ``provisional-unstable`` — a multi-trial panel whose runs disagreed; the
        number is a point estimate over a flipping distribution.
      - ``behavioral-unobserved`` — ``--behavioral`` was asked for but every run
        was env-blocked/failed, so the behavioral pillars rest on nothing; the
        behavioral dimension is not quotable (the static floor is not judged here).
      - ``static-deterministic`` — no behavioral panel; the score is static
        probes only, reproducible by construction; quotable.
      - ``not-scorable`` — no observable pillar; there is no number to quote.
    """

    quotable: bool
    tag: str
    reason: str
    # Carried through when a multi-trial panel ran, else None (single/no panel).
    verdict_stability: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def quotability(report: Any) -> Quotability:
    """Classify whether ``report``'s headline number is reproducible enough to cite.

    Duck-typed over the Report (``overall_score``, ``scored``, ``behavioral_runs``)
    so :mod:`asrs.reliability` stays free of a scoring/report import. Pure over the
    already-collected runs — reads state, never a network or the score itself.
    """
    scored = getattr(report, "scored", True) and getattr(report, "overall_score", None) is not None
    if not scored:
        return Quotability(
            quotable=False,
            tag="not-scorable",
            reason="No observable pillar — there is no number to quote.",
        )

    runs = list(getattr(report, "behavioral_runs", None) or [])
    if not runs:
        # No panel ran: the overall rests on deterministic static probes, which
        # reproduce by construction. Quotable — and NOT flagged provisional.
        return Quotability(
            quotable=True,
            tag="static-deterministic",
            reason="Static score — deterministic probes, no panel variance to reproduce.",
        )

    rel = panel_reliability(runs)
    if rel.valid_runs == 0:
        # --behavioral was requested but nothing observed the site (all runs
        # env-blocked/failed). Attribution honesty: this judges only the
        # behavioral dimension, NOT the static floor the overall degrades to.
        return Quotability(
            quotable=False,
            tag="behavioral-unobserved",
            reason="Behavioral panel produced no valid run — the behavioral "
            "dimension was not observed (all runs env-blocked or failed).",
        )
    if rel.single_trial:
        return Quotability(
            quotable=False,
            tag="provisional-single-trial",
            reason="Single valid trial — reproducibility unmeasured; re-run with "
            "--trials>=2 before quoting the behavioral number.",
        )
    if rel.verdict_stability is not None and rel.verdict_stability < _STABLE_MIN:
        return Quotability(
            quotable=False,
            tag="provisional-unstable",
            reason=f"Panel unstable (verdict stability {rel.verdict_stability:.2f} "
            f"< {_STABLE_MIN:.2f}) — the runs disagree, so the number is a point "
            "estimate over a flipping distribution.",
            verdict_stability=rel.verdict_stability,
        )
    return Quotability(
        quotable=True,
        tag="reproducible",
        reason=f"Panel reproduces (verdict stability {rel.verdict_stability:.2f}) "
        f"over {rel.valid_runs} valid runs.",
        verdict_stability=rel.verdict_stability,
    )


def _valid_runs(runs: list[BehavioralRun]) -> list[BehavioralRun]:
    """Runs that observed the site: a parsed verdict AND not env-blocked.

    Mirrors ``shopper._aggregate`` / ``battery._valid_runs`` exactly — a run
    whose own hosting stack refused the site observed nothing about it and is
    dropped, so reliability measures the SAME runs the score measured.
    """
    return [r for r in runs if r.checkpoints and not _is_env_blocked(r)]


def _label(single_trial: bool, valid_runs: int, verdict_stability: float | None) -> str:
    if valid_runs == 0:
        return "no-signal"
    if single_trial or verdict_stability is None:
        return "single-trial"
    if verdict_stability >= _STABLE_MIN:
        return "stable"
    if verdict_stability >= _MIXED_MIN:
        return "mixed"
    return "unstable"


def panel_reliability(runs: list[BehavioralRun]) -> PanelReliability:
    """Within-panel verdict reproducibility over the valid shopper runs.

    ``runs`` is the ``BehavioralRun`` list a single shopper panel produced for
    one task (across models x trials). Returns a :class:`PanelReliability`. With
    fewer than 2 valid runs reproducibility cannot be observed, so the metrics
    are None and ``single_trial`` is set — the honest "not quotable yet" state.
    """
    valid = _valid_runs(runs)
    n = len(valid)

    if n < 2:
        # 0 valid = nothing observed; 1 valid = one draw. Either way a single
        # draw carries no reproducibility signal — never a site failure.
        return PanelReliability(
            valid_runs=n,
            single_trial=True,
            per_checkpoint=[],
            flipped_checkpoints=[],
            flip_rate=None,
            verdict_stability=None,
            trust_event_agreement=None,
            trust_events_unanimous=None,
            label=_label(True, n, None),
        )

    per_checkpoint: list[CheckpointReliability] = []
    flipped: list[str] = []
    minority_fractions: list[float] = []
    for key in _CHECKPOINT_KEYS:
        pass_count = sum(1 for r in valid if r.checkpoints.get(key))
        majority = max(pass_count, n - pass_count)
        minority = min(pass_count, n - pass_count)
        agreement = majority / n
        unanimous = minority == 0
        minority_fractions.append(minority / n)
        if not unanimous:
            flipped.append(key)
        per_checkpoint.append(
            CheckpointReliability(
                checkpoint=key,
                n=n,
                pass_count=pass_count,
                agreement=round(agreement, 3),
                unanimous=unanimous,
            )
        )

    # minority_fraction in [0, 0.5] per checkpoint; 2 * mean maps to [0, 1].
    verdict_stability = round(1.0 - 2.0 * statistics.fmean(minority_fractions), 3)
    flip_rate = round(len(flipped) / len(_CHECKPOINT_KEYS), 3)

    warned = sum(1 for r in valid if r.trust_events)
    clean = n - warned
    trust_event_agreement = round(max(warned, clean) / n, 3)
    trust_events_unanimous = min(warned, clean) == 0

    return PanelReliability(
        valid_runs=n,
        single_trial=False,
        per_checkpoint=per_checkpoint,
        flipped_checkpoints=flipped,
        flip_rate=flip_rate,
        verdict_stability=verdict_stability,
        trust_event_agreement=trust_event_agreement,
        trust_events_unanimous=trust_events_unanimous,
        label=_label(False, n, verdict_stability),
    )
