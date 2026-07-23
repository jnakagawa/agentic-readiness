"""Shared contracts for the Agentic Selling Readiness Score (ASRS).

Every probe and behavioral runner emits CheckResult records; the scoring
engine rolls them up per the rubric (rubric/rubric_v0.yaml). Keep this file
dependency-free (stdlib only) — every module imports it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    # Excluded from scoring (pillar max shrinks); NA = doesn't apply,
    # CANT_TEST = couldn't determine — flagged in the report, never punished.
    NA = "not_applicable"
    CANT_TEST = "cant_test"


PILLARS = ("access", "legibility", "transactability", "trust", "outcome")


@dataclass
class CheckResult:
    check_id: str  # must match a check id in the rubric
    pillar: str  # one of PILLARS
    status: Status
    points: float  # earned, 0..max_points (PARTIAL earns a fraction)
    max_points: float
    finding: str  # named slug for the observed state, e.g. "robots-blocks-all-ai-crawlers"
    remediation: str  # concrete fix; "" when PASS/NA
    evidence: dict[str, Any] = field(default_factory=dict)  # urls, headers, snippets


@dataclass
class ModelTrustVerdict:
    model: str  # e.g. "claude" | "codex"
    # Under an explicit user directive to buy here, what does the model do?
    # "proceed" | "proceed_with_warning" | "refuse" (rubric v0.2 directive framing).
    # ``willing`` is kept as the derived boolean (decision != "refuse") so old
    # reports and renderers keep working.
    willing: bool
    confidence: float  # 0..1
    concerns: list[str] = field(default_factory=list)
    decision: str = ""  # "" only in pre-v0.2 reports; derive from willing then


@dataclass
class BehavioralRun:
    model: str
    trial: int
    # Checkpoint ladder (Luke's milestones, read-only v0):
    # found_product, understood_pricing, found_purchase_path,
    # machine_payable_path, no_human_gate
    checkpoints: dict[str, bool] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    trust_events: list[str] = field(default_factory=list)  # hesitation/refusal/warn-user
    transcript_path: str = ""


@dataclass
class Report:
    domain: str
    rubric_version: str
    generated_at: str  # ISO 8601 UTC
    checks: list[CheckResult] = field(default_factory=list)
    pillar_scores: dict[str, float | None] = field(default_factory=dict)  # 0-100; None = pillar entirely NA
    # None (with scored=False) when NO pillar was observable — the domain could
    # not be scored at all, distinct from a real 0.0. See scoring.py.
    overall_score: float | None = 0.0  # 0-100, reweighted over applicable pillars
    grade: str = ""  # A+ .. F, or "N/A" when not scorable
    caps_applied: list[str] = field(default_factory=list)  # cap slugs that limited the grade
    trust_panel: list[ModelTrustVerdict] = field(default_factory=list)
    behavioral_runs: list[BehavioralRun] = field(default_factory=list)
    # False when no pillar was observable (every check NA/CANT_TEST/absent):
    # the report carries no score, only findings. Attribution honesty — a site
    # is never punished for what couldn't be observed (rubric invariant).
    scored: bool = True

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)
