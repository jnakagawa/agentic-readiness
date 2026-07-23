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

## Cycle 2 — 2026-07-23T02:16Z — COVERAGE (direct to main)

**What.** Task-battery foundation: a battery file format + loader + cross-task
aggregation math, with tests. New `batteries/default_v1.yaml` (5 diverse
vendor-neutral intents: image gen, translation, data enrichment, API
subscription, physical good), `asrs/battery.py` (`load_battery`,
`aggregate_battery`, `Battery`/`BatteryTaskResult`/`BatterySummary`), and
`tests/test_battery.py` (6 tests). This is step one of the P0 COVERAGE battery
item ("design the format + aggregation first"); behavioral execution + the
`--battery` CLI flag stay [LOCAL] (need the claude/codex CLIs).

**Why.** A single shopper task is one draw from a wide distribution — a site's
readiness for "buy an image" says little about "subscribe to the API" or "order
the physical good." The battery turns "did it work once" into two signals a
single run can't give: COVERAGE (per-task, per-archetype checkpoint attainment)
and RELIABILITY (cross-task variance of each checkpoint). `cross_task_spread`
is the headline: 0 = the site behaves the same whatever the agent was sent to
do; higher = readiness is intent-dependent and the best single run overstates
it. Moves measurement flexibility (many intents) and rigor (variance-aware) at
once — both north-star axes.

**Invariant discipline.** Rubric is TASK-AGNOSTIC and UNCHANGED — the battery
adds NO check, weight, or cap and does not feed the overall score; it is a
diagnostic layer over the `BehavioralRun` records the shopper panel already
emits. So NO rubric version bump, and this is direct-to-main (new module +
data + tests, no scoring-semantics change, no payment/signing code). "Valid
run" + the checkpoint ladder are imported from `shopper` (single source of
truth) so the battery and the per-task score never diverge on what counts as
observing the site. The $0-only / one-free-tier-attempt property is untouched:
aggregation consumes already-collected runs. The [LOCAL] runner design (queued)
pins the constraint that the free-tier transaction probe fires at most ONCE per
battery while the shopper panel runs per task.

**Scope.** `asrs/battery.py` (new), `batteries/default_v1.yaml` (new),
`tests/test_battery.py` (new). No edits to scoring/cli/rubric/types/report — the
scoring path is byte-for-byte unchanged.

**Evidence.**
- Tests: `tests/test_battery.py` 6/6 PASS, `tests/test_free_tier.py` 8/8 PASS.
- Aggregation math pinned: env-blocked + failed runs excluded from valid (mirror
  of `shopper._aggregate`); no-valid-run task = "no signal" (None fractions),
  dropped from cross-task mean/spread, never a site failure; `pstdev` reliability
  spread (found_product identical across intents -> 0.0; 1.0-vs-0.0 intent split
  -> 0.5); single signal task -> spread 0.0 not a crash; missing task in runs
  map -> attempted 0 (no crash).
- Battery vendor-neutrality asserted in-test: no intent names a domain or brand.

**Canonical pair (regression signal).** UNCHANGED by construction, not merely
unmeasured. The scoring path imports nothing from `asrs/battery.py`; scoring.py,
cli.py, rubric_v0.yaml, types.py, report.py are untouched this cycle. No domain's
overall/pillars/delta can move. (Live re-score remains BLOCKED in-cloud per
STATE network policy; last known static-equivalent delta +40.6, queued [LOCAL].)

**Next hypothesis.** The battery only pays off once it runs. Next COVERAGE cycle
(after the TRUTH slot): wire `--battery <path>` into the behavioral pipeline —
static probes once, free-tier probe ONCE, shopper panel per task — attach the
`BatterySummary` to the Report as an additive field, and render the reliability
row. That touches the behavioral orchestration near the free-tier probe, so it
wants care but is still not a scoring-semantics change. Behavioral execution is
[LOCAL]; the CLI orchestration is testable in-cloud with a synthetic panel.
