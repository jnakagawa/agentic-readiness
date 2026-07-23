# Cycle log (append-only; never edit past entries)

Format per entry: `## Cycle N — <UTC timestamp> — <track>` then: what/why,
evidence paths, canonical-pair numbers (overall a/b, delta), next hypothesis.

## Cycle 1 — 2026-07-23T01:18Z — METHOD (human-gated PR)

**What.** NOT-SCORABLE attribution fix. When NO pillar is observable (every
check NA/CANT_TEST/absent), the roll-up used to collapse to overall **0.0 /
grade F** — the worst-possible-storefront score — for a domain nobody could
even reach. It now reports NOT SCORABLE: `overall_score=None`, `grade="N/A"`,
new report field `scored=False`. Rubric bumped v0.4 -> v0.5 (aggregation-rule
change; dated changelog added).

**Why.** This is the aggregate-level expression of the attribution-honesty
invariant the per-check layer already honored ("a site is never punished for
what couldn't be observed"). A down/DNS-failing/probe-firewalled domain was
being mislabeled as a real F, indistinguishable from a genuinely failing
storefront — a false negative that pollutes any future leaderboard/population.
Discovered empirically: running the mandated canonical re-score in this
cloud env returned exactly this degenerate all-CANT_TEST result.

**Human-gated** per playbook ship-rule 5 (scoring-semantics/aggregation +
version bump). Branch `loop/not-scorable-attribution`, PR
[#1](https://github.com/jnakagawa/agentic-readiness/pull/1), Slack flagged.

**Scope.** asrs/{scoring,types,report,scorecard}.py, rubric/rubric_v0.yaml,
tests/test_scoring.py (new — first unit tests for the roll-up engine; 7 tests).
Strict no-op for any domain with >=1 observable pillar (branch unreachable when
weight_total > 0), so no real score moves.

**Evidence.**
- Tests: `tests/test_scoring.py` 7/7 PASS, `tests/test_free_tier.py` 8/8 PASS.
- Before/after render on the canonical pair (unreachable in-cloud): was
  "OVERALL 0.0/100 GRADE F", now "NOT SCORABLE — no observable pillars".
- Regression tests pin scorable scoring unchanged: single-pillar=100.0/A+,
  mixed=38.5/F, cap binds at 69.0.
- HTML scorecard renders null overall as "n/a" / "Grade N/A" (no crash).

**Canonical pair (regression signal).** LIVE static re-score is BLOCKED in this
cloud env: the agent proxy denies CONNECT to drift-flight.org / driftflight.com
/ any external host (403 — see loop/STATE.md). In-cloud both returned
NOT SCORABLE (all pillars unobservable). Delta unchanged is proven by
construction, not measured: the changed branch is unreachable for any domain
with an observable pillar, and a networked score of either canonical domain has
observable pillars. The live delta re-score is queued [LOCAL] for merge-time.

**Next hypothesis.** The stderr coverage-warning flood (one line per absent
rubric check, every run) is noise that will drown real signal once the battery
lands — a static-mode run legitimately omits all behavioral checks. Candidate
READOUT/METHOD cycle: suppress expected-absent warnings (behavioral checks in
static mode), keep only genuinely-unexpected ones.
