"""Rubric roll-up for the Agentic Selling Readiness Score.

Turns a flat list of ``CheckResult`` records into a scored ``Report``:
per-pillar scores (excluding NA/CANT_TEST from the denominator), a
weight-renormalized overall, grade caps for critical findings, and a
letter grade. The rubric (``rubric/rubric_v0.yaml``) is the single source
of truth for weights, per-check max points, caps, and grade bands.

Scoring rules (see README "Design notes"):
- A pillar with no applicable (PASS/PARTIAL/FAIL) max is None and dropped
  from the overall; its weight is not counted (renormalization).
- The outcome pillar is behavioral-only, so in static mode it is entirely
  absent -> None -> dropped. That is the intended "static-only mode".
- Caps LIMIT the overall (min), they never add points.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RUBRIC_PATH = Path(__file__).resolve().parent.parent / "rubric" / "rubric_v0.yaml"

# Statuses that contribute to a pillar's earned/max sums. NA and CANT_TEST
# are excluded from both numerator and denominator (they shrink the pillar,
# never punish it).
_SCORED_STATUSES = frozenset({"pass", "partial", "fail"})


def load_rubric(path: str | Path | None = None) -> dict:
    """Load and index the rubric YAML.

    Returns the parsed mapping augmented with a ``_checks_by_id`` index for
    O(1) lookup by the scoring engine.
    """
    import yaml  # lazy: keep module import cheap

    rubric_path = Path(path) if path is not None else DEFAULT_RUBRIC_PATH
    with open(rubric_path, "r", encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)

    checks = rubric.get("checks") or []
    rubric["_checks_by_id"] = {c["id"]: c for c in checks}
    return rubric


def _status_value(status: Any) -> str:
    """Normalize a Status enum or raw string to its string value."""
    return getattr(status, "value", status)


def _grade_for(overall: float, grade_bands: list) -> str:
    """First band (sorted by lower bound desc) whose lower bound <= overall."""
    # grade_bands entries are [lower_bound, "grade"]; sort desc so the first
    # match is the highest qualifying band.
    for lower, grade in sorted(grade_bands, key=lambda b: b[0], reverse=True):
        if overall >= lower:
            return grade
    # Defensive: bands should always cover down to 0, but never crash.
    return grade_bands[-1][1] if grade_bands else ""


def score(
    checks: list,
    rubric: dict,
    domain: str,
    trust_panel: list | None = None,
    behavioral_runs: list | None = None,
):
    """Roll a list of CheckResults up into a scored Report.

    See module docstring for the rules. ``trust_panel`` and
    ``behavioral_runs`` are attached verbatim to the returned Report.
    """
    from .types import PILLARS, Report  # lazy: avoid import cycles at module load

    checks = list(checks or [])
    trust_panel = list(trust_panel or [])
    behavioral_runs = list(behavioral_runs or [])

    checks_by_id = rubric.get("_checks_by_id")
    if checks_by_id is None:
        checks_by_id = {c["id"]: c for c in (rubric.get("checks") or [])}

    # --- (a) coverage warnings ------------------------------------------
    result_ids = [c.check_id for c in checks]
    result_id_set = set(result_ids)
    for cid in result_ids:
        if cid not in checks_by_id:
            print(
                f"[asrs.scoring] warning: check_id {cid!r} not in rubric "
                f"(version {rubric.get('version')!r}) — its points are still counted",
                file=sys.stderr,
            )
    for rid in checks_by_id:
        if rid not in result_id_set:
            # Missing rubric checks are simply absent — their pillar max
            # shrinks. Not an error, but worth surfacing.
            print(
                f"[asrs.scoring] warning: rubric check {rid!r} has no result "
                "— absent (pillar max shrinks)",
                file=sys.stderr,
            )

    # --- (b) per-pillar scores ------------------------------------------
    pillar_scores: dict[str, float | None] = {}
    earned: dict[str, float] = {p: 0.0 for p in PILLARS}
    possible: dict[str, float] = {p: 0.0 for p in PILLARS}

    for c in checks:
        pillar = c.pillar
        if pillar not in earned:
            # A check for an unknown pillar — count it under its own bucket
            # so it isn't silently dropped, and warn.
            print(
                f"[asrs.scoring] warning: check {c.check_id!r} has unknown "
                f"pillar {pillar!r}",
                file=sys.stderr,
            )
            earned.setdefault(pillar, 0.0)
            possible.setdefault(pillar, 0.0)
        if _status_value(c.status) in _SCORED_STATUSES:
            earned[pillar] += c.points
            possible[pillar] += c.max_points

    for pillar in earned:
        if possible[pillar] > 0:
            pillar_scores[pillar] = 100.0 * earned[pillar] / possible[pillar]
        else:
            # No applicable checks -> pillar entirely NA/CANT_TEST/absent.
            pillar_scores[pillar] = None

    # --- (c) overall: weight-renormalized over applicable pillars -------
    weights = rubric.get("pillar_weights") or {}
    weighted_sum = 0.0
    weight_total = 0.0
    for pillar, pscore in pillar_scores.items():
        if pscore is None:
            continue
        w = float(weights.get(pillar, 0.0))
        weighted_sum += w * pscore
        weight_total += w

    overall = (weighted_sum / weight_total) if weight_total > 0 else 0.0

    # --- (d) caps: critical findings limit the overall ------------------
    # A cap is recorded as applied only when it BINDS (it is below the
    # pre-cap overall) — a non-binding cap must not show up as "grade capped".
    caps = rubric.get("caps") or {}
    caps_applied: list[str] = []
    overall_pre_cap = overall
    for c in checks:
        slug = c.finding
        if slug in caps:
            cap_value = float(caps[slug])
            if cap_value < overall_pre_cap and slug not in caps_applied:
                caps_applied.append(slug)
            if overall > cap_value:
                overall = cap_value

    # --- (e) grade ------------------------------------------------------
    grade = _grade_for(overall, rubric.get("grade_bands") or [])

    # --- (f) assemble Report --------------------------------------------
    return Report(
        domain=domain,
        rubric_version=str(rubric.get("version", "")),
        generated_at=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        checks=checks,
        pillar_scores=pillar_scores,
        overall_score=round(overall, 1),
        grade=grade,
        caps_applied=caps_applied,
        trust_panel=trust_panel,
        behavioral_runs=behavioral_runs,
    )
