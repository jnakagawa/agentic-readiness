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

## Merge review — PR #1 (loop/not-scorable-attribution) — 2026-07-23T03:05Z

Reviewed and merged by the local operator (Fable session, networked machine)
under the new peer-gate policy. Live verification the authoring cycle could
not run in-cloud: tests 7/7 + 8/8 PASS on the branch; canonical pair static
re-score UNCHANGED vs the v0.4 baseline (drift-flight.org 46.1 F,
driftflight.com 85.5 B — exact no-op confirmed); degenerate case verified
live (unreachable domain now reports NOT SCORABLE instead of 0.0/F).
Refutation attempts: vendor-neutrality (clean — no domain named), attribution
honesty (this IS the invariant, aggregate level), version discipline (v0.5
bump + dated changelog present). Merged.

## Cycle 3 — 2026-07-23T03:16Z — TRUTH (direct to main)

**What.** Within-panel verdict-stability metric: `asrs/reliability.py`
(`panel_reliability(runs) -> PanelReliability`) + `tests/test_reliability.py`
(8 tests) + a PANEL RELIABILITY section in `report.render`. Over the VALID
shopper runs for one task (all model x trial draws that observed the site), it
computes per-checkpoint agreement (`max(pass, n-pass)/n`), a headline
`verdict_stability = 1 - 2*mean(minority_fraction)` in [0,1], the list of
`flipped_checkpoints`, `flip_rate`, and a separate `trust_event_agreement`
(the refuse/warn <-> clean flip). < 2 valid runs -> `single_trial`, all metrics
None, label `single-trial`/`no-signal` — the honest "not quotable yet" state.

**Why (TRUTH).** The open question in STATE: a same-day codex trust verdict
flipped refuse(0.97) <-> warn(0.97), and checkpoints can pass one trial and fail
the next. When the valid runs disagree, the aggregate the overall score quotes
is a point estimate over an unstable distribution and a single-trial number
overstates its own confidence. This makes reproducibility a first-class, visible
readout: does the panel say the same thing when you just run it again? It is the
WITHIN-PANEL complement to Cycle 2's CROSS-TASK battery spread — battery asks
"does readiness depend on the intent", reliability asks "does it reproduce on the
same intent". Directly serves "does the score predict what an agent experiences".

**Invariant discipline (mirrors Cycle 2 battery).** Rubric UNCHANGED — adds NO
check, weight, or cap and does NOT feed the overall score; a diagnostic layer
over the `BehavioralRun` records the panel already emits, so NO version bump and
direct-to-main. "Valid run" is imported from `asrs.behavioral.shopper`
(`_is_env_blocked`, `_CHECKPOINT_KEYS`) — single source of truth, so reliability
and the per-task score never diverge on what observed the site (env-blocked +
failed runs excluded identically). Vendor-neutral: no domain/brand string
anywhere; metric is pure arithmetic over checkpoint booleans. $0-only / free-tier
path untouched (consumes already-collected runs). Display-only render change.

**Scope.** `asrs/reliability.py` (new), `tests/test_reliability.py` (new),
`asrs/report.py` (render: new `_reliability_lines`, called after the behavioral
table). scoring.py / rubric_v0.yaml / types.py / cli.py / scorecard.py
byte-for-byte UNCHANGED (`git diff --stat` empty for all five).

**Evidence.**
- Full suite GREEN: test_scoring 7/7, test_free_tier 8/8, test_battery 6/6,
  test_reliability 8/8 (29/29). (free_tier needed `pip install -r
  requirements.txt` — `eth-account` absent in the fresh cloud container; a
  pre-existing env gap, not this change: 7/8 on clean main before install too.)
- Math pinned in-test: 2 unanimous runs -> stability 1.0 / flip_rate 0; one
  split checkpoint (1/2) -> stability 0.8, that checkpoint in `flipped_checkpoints`
  (ladder order); all-5-split -> 0.0; 3-run 2-split -> 0.733 "mixed"; trust flip
  is a SEPARATE dimension (checkpoints unanimous -> stability still 1.0);
  env-blocked + failed runs excluded from the valid denominator (mirrors shopper).
- Render smoke: a 2-run panel with one checkpoint + the trust signal flipping
  renders "verdict stability 0.80 (stable)", "flipped between runs:
  machine_payable_path", "trust signal flipped (agreement 0.50)".

**Canonical pair (regression signal).** UNCHANGED by construction, not merely
unmeasured: the scoring path (scoring.py, rubric, types.py, cli.py, scorecard.py)
is byte-for-byte untouched this cycle, so no domain's overall/pillars/delta can
move. Live in-cloud re-score remains BLOCKED (agent proxy denies external
CONNECT, STATE network policy); last known static-equivalent delta +40.6, live
re-score queued [LOCAL].

**Next hypothesis (READOUT is next in rotation).** Reliability is computed only
in `render` today — the JSON Report and the HTML scorecard don't carry it.
Next READOUT cycle: attach `PanelReliability` (and the Cycle-2 `BatterySummary`)
to `Report` as additive fields and surface a reliability row on the HTML card,
so JSON/leaderboard consumers see reproducibility, not just the terminal. Still
additive, no version bump. Open science question for a [LOCAL] run: what trial
count N drives `verdict_stability` above ~0.8 on the canonical pair — the
empirical answer to "what N stabilizes it".

## Local verification — 20260723T040714Z

tests_ok=True | drift-flight.org: ERR | driftflight.com: ERR | artifact runs/local/verify_20260723T040714Z.json

## Local verification — 20260723T040757Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T040757Z.json

## Cycle 4 — 2026-07-23T04:15Z — READOUT (direct to main)

**What.** Surfaced the within-panel verdict-reliability metric — computed only
inside the terminal renderer since Cycle 3 — in the JSON `Report` and the HTML
scorecard. `Report` gains one ADDITIVE field, `panel_reliability: dict | None`
(the `asrs.reliability.PanelReliability` as a plain dict). `cli._evaluate`
populates it after scoring from the SAME `behavioral_runs` via the SAME pure
`panel_reliability()` the terminal calls, so JSON/HTML and the terminal card
never diverge. `scorecard._reliability(rep)` renders a brand-styled "Panel
reliability" card (stability number + band pill, flipped checkpoints shown by
human label, the trust-signal flip note) wired into both the single-domain
column and the side-by-side compare layout. `tests/test_readout.py` (5 tests).

**Why (READOUT).** The reliability signal answered "does the panel reproduce on
the same task?" but only in the terminal — the JSON a leaderboard/consumer reads
and the hosted HTML card carried the high-delta number with no reproducibility
context beside it. A quoted stability that lives only in a terminal a human ran
once is not a benchmark readout. This puts reproducibility next to the score
everywhere the score travels, so a reader sees whether a number rests on runs
that agree or runs that flip between trials. Serves readout clarity directly.

**Scope decision (why reliability only, not battery too).** The backlog item
paired reliability + battery attach. `BatterySummary` has NO populated source in
the current pipeline — `--battery` wiring is `[LOCAL]`-gated behavioral work — so
attaching it now would create a permanently-null dead field. `PanelReliability`
is genuinely populatable in-cloud today (`behavioral_runs` sit on every
behavioral Report), so it is the smallest scientifically meaningful unit that
actually carries data. Battery-attach stays queued behind `--battery`.

**Invariant discipline.** Rubric UNCHANGED — adds NO check, weight, or cap and
does NOT feed the overall score. `git diff --stat asrs/scoring.py rubric/` is
EMPTY (byte-for-byte). The new `types.py` field is optional, default None,
scoring-irrelevant → NO rubric version bump, direct-to-main. Vendor-neutral: the
card is pure arithmetic over checkpoint booleans, no domain/brand string; the
smoke render used driftflight.com only as a fixture label. $0-only / free-tier
path untouched (consumes already-collected runs). Static reports carry
`panel_reliability = None` — no invented reproducibility for a panel that never
ran (attribution honesty).

**Evidence.**
- Full suite GREEN 34/34: test_readout 5/5, test_reliability 8/8, test_battery
  6/6, test_scoring 7/7, test_free_tier 8/8 (free_tier needed `pip install -r
  requirements.txt` — `eth-account` absent in the fresh cloud container, the
  same pre-existing env gap logged in Cycle 3; 7/8 before install, 8/8 after).
- test_readout pins: a 2-run panel (one checkpoint split) round-trips through
  `to_json`/`json.loads` with `verdict_stability` 0.8 and
  `flipped_checkpoints == ["machine_payable_path"]`; the stored dict is
  byte-for-byte `panel_reliability(runs).to_dict()` (one source of truth); a
  static report serializes `panel_reliability = None`; the HTML card shows
  "0.80"/"Stable"/"Machine-payable" and never leaks the raw key; single-trial →
  "Single trial"/"not assessed" (no fake number); absent field → empty string
  (static scorecards byte-identical).
- End-to-end smoke: `build_scorecard` on a synthetic behavioral report emits the
  "Panel reliability" card with stability 0.80 and the flipped-checkpoint chip.

**Canonical pair (regression signal).** UNCHANGED by construction: the scoring
path (scoring.py, rubric, plus the scoring-relevant types.py fields) is
byte-for-byte untouched, so no domain's overall/pillar/delta can move. LIVE
signal from the freshest local-verify artifact (runs/local/verify_20260723T040757Z.json,
~7 min old at cycle time — runner healthy): drift-flight.org 46.1 F vs
driftflight.com 85.5 B, delta +39.4 — matching the by-construction expectation
of no movement.

**Next hypothesis (METHOD is next in rotation).** With reproducibility now
visible in the JSON, the natural METHOD step is to make trials>=2 the behavioral
default and gate the QUOTABILITY of a single number on `single_trial` /
`verdict_stability` (a readout-level "provisional (single trial)" tag, NOT a
score change). Open [LOCAL] science question unchanged: what trial count N drives
`verdict_stability` above ~0.8 on the canonical pair. Battery attach remains
queued behind `--battery` wiring (COVERAGE, partially in-cloud testable with a
synthetic panel).

## Cycle 5 — 2026-07-23T05:20Z — METHOD (direct to main)

**What.** A quotability gate: a display-only readout that tells a reader, in one
bit, whether a Report's headline number is safe to CITE or only PROVISIONAL,
and defaulted behavioral `--trials` to 2 so a quoted behavioral number is
reproducibility-checked by default instead of a single draw. New pure function
`asrs.reliability.quotability(report)` -> `Quotability(quotable, tag, reason,
verdict_stability)`, classifying six honest states over the runs the score
already used: `static-deterministic` (no panel -> reproducible by construction ->
CITABLE), `reproducible` (multi-trial panel agreed -> CITABLE), `provisional-
single-trial` (one valid draw -> reproducibility unmeasured), `provisional-
unstable` (multi-trial panel whose runs disagree, `verdict_stability` < 0.8),
`behavioral-unobserved` (`--behavioral` asked but every run env-blocked/failed),
`not-scorable` (no observable pillar -> no number to quote). Surfaced as one
`QUOTABILITY:` line under the OVERALL header in the terminal card
(`report._quotability_lines`). `--trials` default 1 -> 2.

**Why (METHOD).** The Cycle-3/4 reliability metric made verdict flips *visible*
but left the interpretation to the reader: a card could print a high delta next
to a stability of 0.0 and still read as authoritative. This operationalizes the
loop's own finding — the observed same-day refuse<->warn flip at equal
confidence proves a single trial is not quotable — into a verdict the readout
states itself. "Multi-trial the scored default for anything quoted" (backlog
METHOD item) is now the literal default: a bare `--behavioral` run collects 2
trials, and if it still can't reproduce, the number self-flags PROVISIONAL. This
is the honest gate between "we measured it once" and "cite this."

**Invariant discipline.** NOT a scoring-semantics change -> NO version bump,
direct-to-main. `git diff --stat asrs/scoring.py rubric/` is EMPTY (byte-for-
byte); `types.py` untouched. Quotability does NOT feed the score — `render`
shows the SAME `overall_score`, asserted unchanged in-test. Vendor-neutral: pure
arithmetic over checkpoint booleans + panel counts, no domain/brand string.
$0-only preserved: `--trials 2` repeats ONLY the read-only shopper panel; the
free-tier transaction probe still runs at most ONCE per scoring run (it sits
outside the trials loop in `cli._run_behavioral`; help text now says so
explicitly). Attribution honesty: a static-only score is `static-deterministic`
(CITABLE, never flagged), and an all-env-blocked panel is scoped to
`behavioral-unobserved` — it judges the behavioral dimension, NOT the static
floor the overall degrades to; a not-scorable report prints no quotability line.
Terminal-only this cycle (mirrors the Cycle-3 reliability pattern: metric +
terminal card first, JSON/HTML attach next READOUT cycle) — JSON `to_json()`
byte-identical, so the local-verify artifact contract is unchanged.

**Scope.** `asrs/reliability.py` (+`Quotability` dataclass + `quotability()`),
`asrs/report.py` (`_quotability_lines`, one line under the header),
`asrs/cli.py` (`--trials` default 1->2 + help text), `tests/test_quotability.py`
(new, 8 tests). 3 source files + 1 test; scoring.py/rubric/types.py/scorecard.py
UNCHANGED.

**Evidence.**
- Full suite GREEN 42/42: test_quotability 8/8, test_readout 5/5,
  test_reliability 8/8, test_battery 6/6, test_scoring 7/7, test_free_tier 8/8
  (free_tier needs `pip install -r requirements.txt` — `eth-account` absent in
  the fresh cloud container, the same pre-existing env gap logged Cycles 3-4).
- Render smoke (LOG evidence): a static B report prints "QUOTABILITY: CITABLE
  (static-deterministic)" beside an unchanged "OVERALL 85.5/100"; a single-trial
  behavioral report prints "QUOTABILITY: PROVISIONAL (provisional-single-trial)
  … re-run with --trials>=2"; a two-run disagreeing panel prints "PROVISIONAL
  (provisional-unstable) — verdict stability 0.00 < 0.80".
- test_quotability pins: static -> CITABLE/no stability; not-scorable -> no
  QUOTABILITY line in the card; 1 valid run -> provisional-single-trial with the
  --trials>=2 pointer; 2 disagreeing runs -> provisional-unstable carrying
  stability 0.0; 2 agreeing runs -> reproducible carrying 1.0; all-env-blocked ->
  behavioral-unobserved scoped to the behavioral dimension; overall score
  byte-unchanged in the rendered card; CLI `--trials` default parses to 2.

**Canonical pair (regression signal).** UNCHANGED by construction: scoring.py,
rubric, and types.py are byte-for-byte untouched, so no domain's overall/pillar/
delta can move. LIVE signal from the freshest local-verify artifact
(runs/local/verify_20260723T040757Z.json, ~1h old at cycle time — runner
healthy): drift-flight.org 46.1 F vs driftflight.com 85.5 B, delta +39.4 —
matching the by-construction expectation of no movement (both re-scored static:
outcome pillar None on each, so both read `static-deterministic` / CITABLE, and
the delta is unaffected). Live in-cloud re-score remains BLOCKED (network policy);
`[LOCAL]` re-score stays queued.

**Next hypothesis (COVERAGE is next in rotation).** With quotability + trials>=2
default landed, the outstanding METHOD `[LOCAL]` question is empirical: what
trial count N drives `verdict_stability` >= 0.8 on the canonical pair (queued).
COVERAGE next: the `--battery` wiring (synthetic-panel testable in-cloud) is the
oldest COVERAGE follow-up and would let a per-task quotability/reliability grid
travel with the score — the natural COVERAGE companion to this cycle's METHOD
gate.

## Local cycle — 2026-07-23T05:52Z — METHOD (merge-verify; no code change)

**What.** Discharged the oldest P0: the `[LOCAL]` merge-time canonical re-score
for PR [#1](https://github.com/jnakagawa/agentic-readiness/pull/1)
(`loop/not-scorable-attribution`, v0.5 NOT SCORABLE), which was peer-gated and
merged 2026-07-23T03:00:15Z **without** its required live canonical-delta
verification — the cloud env has no outbound network to the canonical domains,
so that sensitive-class merge check was queued for a networked operator. This
local (networked) fire ran it deliberately and live.

**Why.** v0.5 was a scoring-semantics/aggregation change. The playbook's
sensitive-class rule (weights/caps/removals + version bump) requires the live
canonical-delta effect be shown at merge time; it had only ever been argued
by construction + the automated hourly runner, never recorded as the deliberate
peer-gate verification. Recording it closes the audit gap for a merged
scoring-semantics PR.

**Method + evidence.**
- Full suite GREEN 42/42 (`.venv`, eth-account present locally): test_battery
  6/6, test_free_tier 8/8, test_quotability 8/8, test_readout 5/5,
  test_reliability 8/8, test_scoring 7/7.
- Live static re-score (this machine; both domains HTTP 200 in <1s):
  drift-flight.org **46.1 F** (scored) vs driftflight.com **85.5 B** (scored),
  delta **+39.4**. Reachable domains score NORMALLY — not NOT-SCORABLE —
  proving the v0.5 change is a no-op for them.
- Unreachable-domain CONTROL (`*.invalid`): overall=None, grade=N/A,
  scored=False -> NOT SCORABLE. Demonstrates the v0.5 path fires ONLY when no
  pillar is observable (the change's exact claimed semantics).
- Evidence: `runs/local/merge_verify_pr1_20260723T055000Z.json`; report blobs
  `runs/drift-flight_org_20260723T054805.json`,
  `runs/driftflight_com_20260723T054811.json`,
  `runs/asrs-nonexistent-control-20260723_invalid_20260723T054831.json`.

**Canonical pair (regression signal).** 46.1 F / 85.5 B, delta +39.4 — matches
the freshest hourly verify artifact (`verify_20260723T040757Z.json`) exactly and
sits within static variance of the loop-start baseline +40.6. No regression;
delta explained in capability terms — access/trust identical (100/60 each on
both), the +39.4 is entirely the .com's agent-native legibility (90.9 vs 36.4)
and transactability (87.5 vs 18.8) the .org lacks.

**Ship.** Direct-to-main (verification + evidence artifact + LOG/STATE/BACKLOG
only; `asrs/` untouched — no source/scoring change). Oldest P0 removed from
BACKLOG. Cloud cycle counter (5) and focus pointer (COVERAGE) unchanged — a
local fire executes queued `[LOCAL]` work, it does not rotate the cloud track.

**Cost finding (steers the next local fire).** `SHOPPER_TIMEOUT_S = 300` per
model×trial makes the queued behavioral experiments multi-cycle-scale: the
N-sweep item as written (N=2,3,5 × claude,codex on both domains) is ~100 min and
~20 codex invocations — over both the "one behavioral pair run" and "~10 codex"
budgets. Recommend the next local fire take a SINGLE scoped datapoint
(drift-flight.org, `--trials 2`, claude,codex ≈ 15-20 min) — the first N=2
reliability + quotability observation on LIVE data (validating the Cycle 3-5
metrics for the first time on real panels) — and split the N-sweep across fires.
Run drift-flight.org (the codex-refusal-free canonical domain) first so codex
browser refusals don't confound the timing.

## Cycle 6 — 2026-07-23T06:15Z — COVERAGE (direct to main)

**What.** Wired `--battery <path>` into the `score`/`compare` pipeline, closing
the Cycle-2 follow-up: the battery MATH (`asrs/battery.py`, shipped Cycle 2) now
has a runner. In behavioral mode with `--battery`, the shopper panel runs ONCE
PER intent, the first task is the primary scoring run, and the additive
`Report.battery_summary` (the `BatterySummary` as a plain dict) travels with the
JSON + a new terminal `TASK BATTERY` section. This is the COVERAGE capability the
loop's north star names — "many task intents" — made executable end-to-end.

**Why.** A single shopper task is one draw from a wide intent distribution; "buy
an image" says little about "subscribe to the API" or "order the physical good".
The battery turns that into per-intent coverage + a cross-task reliability spread
(0 = readiness holds across intents; high = the best single run overstates it).
Until this cycle the aggregation existed but nothing fed it — a measurement
capability with no pipeline. Mirrors the Cycle 3→4 reliability pattern (metric
first, then attach-to-Report + render).

**How (invariants honoured).**
- Shopper panel runs once per battery task (each task's `intent`); the FIRST
  task's runs are the primary scoring run, so `scoring.score()` sees a single
  real task panel — UNCHANGED semantics, no aggregation over a new run
  population, no version bump.
- Free-tier transaction probe fires AT MOST ONCE for the whole battery
  (invariant #1 — it consumes the target's allowance); the per-task loop never
  multiplies it. Trust panel runs once (site-trust is task-independent).
- `--battery` in STATIC mode is a no-op (warn + proceed) — static probes are
  task-independent. A malformed battery file raises loud (loader `ValueError`),
  never silently scores fewer intents.
- Additive-only: `battery_summary` defaults None; scoring.py, the rubric, and
  every scoring field of types.py are byte-for-byte unchanged.

**Evidence.**
- New `tests/test_battery_wiring.py` (4/4) — SYNTHETIC panel (monkeypatched
  shopper/trust/free-tier, no network/CLIs): asserts one panel per intent, first
  task is primary, free-tier fires exactly once, trust once, summary attached +
  populated, static-mode no-op, and the `TASK BATTERY` render section appears
  only when a summary is present.
- Full suite: test_battery 6/6, test_battery_wiring 4/4, test_quotability 8/8,
  test_readout 5/5, test_reliability 8/8, test_scoring 7/7. test_free_tier 7/8 —
  the single miss is `test_zero_value_signs_and_recovers`, which needs
  `eth-account` (absent in this cloud env; the local venv has it → 8/8).
  PRE-EXISTING and env-only: reproduced on a clean `git stash` tree; my diff
  touches none of the free-tier path.
- `python -m asrs score --help` shows the `--battery` option; `asrs.{cli,report,
  battery,types}` import clean.

**Canonical pair (regression signal).** Live in-cloud re-score is blocked (no
outbound network to the canonical domains — see STATE). Regression BY
CONSTRUCTION: the canonical pair is scored STATICALLY (no `--behavioral`, no
`--battery`), a path that never enters the battery code — `battery_summary`
stays None → the render section emits nothing, and scoring.py/rubric are
untouched. Delta unchanged from the freshest live signal
(`runs/local/merge_verify_pr1_20260723T055000Z.json`): drift-flight.org **46.1 F**
vs driftflight.com **85.5 B**, delta **+39.4**. `test_no_battery_single_panel`
proves the non-battery behavioral path is byte-identical to prior behaviour.

**Ship.** Direct-to-main — additive diagnostic field + CLI flag + render + tests;
no scoring-semantics change, no version bump (rubric stays v0.5). Per the
playbook's Cycle-protocol ship rules (additive `Report` field mirroring
`panel_reliability`).

**Next hypothesis.** The HTML scorecard should carry a battery card too (READOUT
follow-up, queued P2 — same terminal-first-then-HTML deferral quotability took).
And the `[LOCAL]` behavioral execution of `--battery` (real per-intent panels on
the canonical pair) is now UNBLOCKED by this wiring — queued P0 with the exact
command; it will produce the first real `cross_task_spread` on a live storefront.

## Cycle 7 — 2026-07-23T07:16Z — TRUTH (direct to main)

**What.** A dedicated regression suite (`tests/test_attribution.py`, 8/8) for
the behavioral **attribution boundary** — invariant #4 (agent-side environment
failures are never scored as site evidence; site failures are never excused as
environment; when in doubt, CANT_TEST). It pins two load-bearing but previously
untested pieces of `asrs/behavioral/shopper.py`: the `_is_env_blocked`
classifier (`_ENV_BLOCK_RE`) and `_aggregate`'s denominator routing.

**Why (TRUTH).** This boundary is the mechanism that makes a behavioral score
*truthful about the site rather than the agent's environment* — a mis-attributed
codex hosted-browser refusal either punishes a healthy storefront (error #1) or
excuses a genuinely agent-hostile one (error #2, which silently inflates the
score and is the more corrosive failure for a benchmark's credibility). Yet the
classifier was exercised only INDIRECTLY — through reliability/quotability/
battery consumers — all reusing a single happy-path phrase ("navigation blocked
by browser security policy"). The negative direction (a 403 / Cloudflare / 429 /
CAPTCHA is a REAL access finding and must NOT be excused) had zero coverage, and
the v0.4 denominator-routing fix (env-blocked runs leave outcome/trust, surface
as `hosted_agent_reachability`) was asserted nowhere directly. Untested
invariant code regresses silently; this makes the boundary a hard, executable
contract.

**What the suite pins (synthetic `BehavioralRun` fixtures — no network/CLI).**
1. Positive classification across the security-* vocabulary and BOTH phrase
   orderings, whether the refusal lands in `blockers` OR `trust_events` (a codex
   refusal can surface as either).
2. **Negative (new coverage):** site-side blocks — 403, Cloudflare challenge,
   429, robots disallow, CAPTCHA wall — are NOT excused as environment.
3. Guard: a run that passed any checkpoint keeps its verdict despite block
   language (a partial block ≠ a full block).
4. A crashed/unparsed run (no checkpoints dict) is a plain failure, not an
   env-block, even if its error text says "security".
5. **Denominator routing:** 1 valid (2 checkpoints) + 1 env-blocked → outcome
   fractions over n=1 (passed checkpoint reads PASS, not the 1/2 PARTIAL a leak
   would give); the env-blocked run surfaces as `hosted_agent_reachability`
   PARTIAL with the blocked model attributed.
6. **All env-blocked → CANT_TEST, never FAIL:** every outcome check + trust
   CANT_TEST, reachability FAIL/0 — invariant #4 "when in doubt, CANT_TEST"
   applied end-to-end.
7. All reached → reachability full PASS, full valid denominator.
8. **Documented coverage boundary (feeds the [LOCAL] codex investigation):** a
   hosted-browser REPUTATION-gate refusal ("this domain is flagged as unsafe" /
   "I'm unable to browse that URL") lacks the security-* vocabulary and is
   currently NOT classified env-blocked. Pinned DELIBERATELY: broadening the
   regex blind — without the real codex transcript — would risk error #2 (test
   #2). Resolving it is `[LOCAL]`: capture the transcript, extend the pattern
   with a fixture from it, and update this assertion in lockstep — its failure
   is the intended signal that the boundary moved. This converts the STATE
   open-question ("root cause + attribution control needed") into an executable
   spec with the exact input the [LOCAL] work must supply.

**Evidence.**
- `tests/test_attribution.py` 8/8.
- Full suite GREEN: test_attribution 8/8, test_battery 6/6, test_battery_wiring
  4/4, test_quotability 8/8, test_readout 5/5, test_reliability 8/8, test_scoring
  7/7. test_free_tier 7/8 — the single miss is `test_zero_value_signs_and_recovers`
  (needs `eth-account`, absent in this cloud env; local venv → 8/8). PRE-EXISTING,
  env-only, and untouched by this diff (which adds one file under `tests/`).

**Canonical pair (regression signal).** In-cloud live re-score blocked (no
outbound network to the canonical domains — STATE). Regression BY CONSTRUCTION:
the diff is a single new file under `tests/`; `asrs/` (scoring.py, rubric,
shopper.py, types.py) is byte-for-byte unchanged, so no scored path can move.
Delta unchanged from the freshest live artifact
(`runs/local/verify_20260723T040757Z.json`): drift-flight.org **46.1 F** vs
driftflight.com **85.5 B**, delta **+39.4**.

**Ship.** Direct-to-main — tests only, no scoring semantics, no version bump
(rubric stays v0.5). Per the Cycle-protocol ship rules (tests are direct-to-main).

**Next hypothesis.** The reputation-gate gap (test #8) is the highest-leverage
attribution question left, and it is now a precise `[LOCAL]` target: one codex
`exec` against driftflight.com capturing the raw refusal text is enough to
calibrate a vendor-neutral pattern extension (worded by capability — "the
hosting stack's own reputation layer refused the URL" — never by vendor). Queued
in BACKLOG. Next cycle rotates to READOUT.

## Local cycle — 2026-07-23T07:50Z — TRUTH/METHOD (trial-count run: env-block attribution leak found)

**What.** Executed the oldest P0 `[LOCAL]` item — "what trial count N stabilizes
the panel" — by adopting and adversarially verifying an ORPHANED result from the
interrupted ~06:44Z fire: `runs/local/trial_stability_20260723T064359Z.json` +
`experiments/trial_count_N.py`, both uncommitted (`runs/` is gitignored, so a
`git clean` would have destroyed them). That fire ran a live claude+codex ×5
shopper panel on drift-flight.org and computed a nested first-N verdict-stability
curve, then died before committing/logging. Verifying it surfaced a real
attribution bug in the shopper's env-block filter.

**Provenance (adversarial check before trusting orphaned work).**
- Artifact `ts` (06:43:59Z) is stamped at `main()` start; transcripts were written
  live 06:46–07:02Z UTC during the run (machine is PDT −0700, reconciling the
  apparent 7h mtime gap). The claude_t1 transcript's embedded verdict matches
  artifact `run[0]` in substance — a real live panel, not a replay.
- `experiments/trial_count_N_analysis.py` (committed, deterministic, $0)
  reconstructs the `BehavioralRun` records from the artifact and re-derives the
  whole curve with the SHIPPED `panel_reliability`: reproduction CONFIRMED —
  valid_runs 2/4/5/6, stability 0.80/0.60/0.68/0.733 exactly. Not fabricated.

**Finding (the real story behind a non-monotonic curve).** The curve looked
paradoxical — N=2 "stable" 0.80 → N=3 "mixed" 0.60, i.e. MORE trials → LESS
stable. Cause: exactly one env-blocked codex run leaks into the valid pool.
Codex trial 3 reported its browser "**safety** controls" blocked the site, but
`shopper._ENV_BLOCK_RE` only matches "security" phrasings (`browser security` /
`security policy|controls|grounds`), NOT "safety". So codex t3's all-false
verdict — from an agent that observed NOTHING (its own URL-safety layer refused
navigation) — is scored as a site verdict, dragging down found_product /
understood_pricing / found_purchase_path. That is an **invariant #4** violation
(agent-side env failure scored as site evidence). With the leak correctly
excluded (proposed regex also covering "safety"), the curve is monotone and
stable: N=2 0.80 → 3 0.867 → 4 0.90 → 5 0.92.

**Answer to the standing open question (with caveat).** On drift-flight.org the
panel is verdict-stable (≥0.8) from N=2 upward and CONVERGES with N once the leak
is removed — the sole residual flip is `found_purchase_path` (claude t1=false vs
t2–t5=true), a genuine legibility ambiguity, not noise. CAVEAT: codex's hosted
browser env-blocked drift-flight.org on ALL 5 trials, so this is claude-only
(single-model) reproducibility, NOT cross-model panel agreement. STATE's premise
that drift-flight.org is "codex-refusal-free" is now FALSE — codex refused it as a
2-day-old domain (registered 2026-07-20). The cross-model N-curve stays blocked on
codex reachability.

**Direction of the fix.** Broadening the env-block regex only ever stops
UNDER-crediting a site for an agent that never saw it (moves codex t3 from the
outcome denominator to the reachability signal); it is behavioral-only and
vendor-neutral (keys on block phrasing, not the domain). It is a
scoring-semantics/aggregation change → **peer-gated + rubric version bump**,
queued with exact spec in BACKLOG (P0). NOT applied this fire (one-item
discipline; local fires surface + queue scoring-semantics changes, they do not
push them to main).

**Ties to Cycle 7 (rebased onto this fire).** Cycle 7 pinned invariant #4 in
`tests/test_attribution.py` and left test #8 as an executable spec for the OPEN
gap: codex refusals that lack the "security-*" vocabulary are not yet env-blocked,
and it deliberately did NOT broaden `_ENV_BLOCK_RE` in-cloud because "blind
broadening risks excusing real site blocks" without a committed transcript. This
fire supplies that committed transcript evidence — but for the SAFE lexical subset:
"browser **safety** controls" is the same env-block family as "browser security
controls" (confirmed by the same codex agent's sibling trials t1/t2/t4/t5 on the
same domain all saying "security"), NOT the harder semantic reputation-gate
phrasings ("flagged as unsafe" / "unable to browse") that test #8 targets. So the
queued fix is the narrow, evidence-backed first step of Cycle 7's deferred
broadening; the reputation-gate remainder stays with the codex-reachability item.

**Canonical pair (regression signal).** Static re-score this fire (both HTTP 200):
drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4** —
identical to `verify_20260723T040757Z.json` and the 05:52Z merge-verify, within
static variance of the +40.6 loop-start baseline. No regression; this fire touched
no `asrs/` code (experiments/ + docs only), so scores are unchanged by
construction. Access/trust identical on both (100/60); the +39.4 is entirely the
.com's legibility (90.9 vs 36.4) and transactability (87.5 vs 18.8).

**Evidence.** `runs/local/trial_stability_20260723T064359Z.json` (force-added),
`experiments/trial_count_N.py`, `experiments/trial_count_N_analysis.py`;
transcripts on local disk (gitignored, established practice) at
`runs/transcripts/drift-flight.org_{claude,codex}_t{1..5}.json`. Full suite GREEN
54/54 (post-rebase onto Cycle 6/7: incl. test_attribution 8/8, test_battery_wiring
4/4).

**Ship.** Direct-to-main (experiment harness + analysis + evidence artifact +
LOG/STATE/BACKLOG; no scoring source touched). Rebased onto Cycle 6/7 before push;
cloud cycle counter (7) and focus pointer (READOUT) unchanged — a local fire
executes queued `[LOCAL]` work, it does not rotate the cloud track. No Slack
(before 16:00Z; no sensitive PR opened/merged; no score change shipped — the fix's
Slack visibility comes when its peer-gated PR opens).

**Next.** (1) Peer-gate the `_ENV_BLOCK_RE` "safety" fix (P0, queued with exact
regex + test + version-bump note; resolves the safe subset of Cycle 7's test #8
spec). (2) Cross-model N-curve needs codex to reach the site — blocked on the
codex-reachability/control-storefront item (feed codex pre-fetched content when its
browser is gated, marked assisted). (3) Verify runner: newest `verify_*.json` is
04:07Z (~3.7h at this fire); no :41 artifact at 05/06 — watch, flag if >6h next
fire.

## Cycle 8 — 2026-07-23T08:15Z — READOUT (direct to main)

**What.** Surfaced the quotability verdict — the one-bit "is the headline number
safe to CITE?" — to the JSON `Report` and the HTML scorecard. It shipped
terminal-only in Cycle 5; this is the same terminal→JSON→HTML deferral the
reliability metric took in Cycles 3→4. Three additive edits: (1) `Report`
gains a `quotability: dict | None` field (`asrs/types.py`); (2) `cli._evaluate`
populates it from the SAME pure `asrs.reliability.quotability(report)` the
terminal card uses, for every mode (static→`static-deterministic`, panel→
`reproducible`/`provisional-*`, unscorable→`not-scorable`); (3) a new
`scorecard._quotability(rep)` renders a **Citable / Provisional** pill + reason
card, placed right under the overview so the citability verdict sits next to the
grade, wired into BOTH layouts (`_domain_column` single + `_section_rows`
compare). not-scorable and an absent field render no card (the grade already
carries N/A — same suppression as the terminal line).

**Why (READOUT, north-star: readout clarity).** A leaderboard/HTML consumer
could already see the number and its reproducibility band, but not the single
bit a citer actually needs before quoting it. Quotability collapses reliability
+ mode into Citable-or-Provisional; travelling with the JSON means an automated
consumer (future leaderboard, trend page) gets the same gate a human running the
terminal got, so a provisional single-trial number can't be quoted as settled.

**Not a scoring-semantics change.** Display-only and additive by construction:
`scoring.py`, the rubric, `types.py`'s scoring fields, and all probes are
byte-for-byte untouched (`git diff --name-only` = types/cli/scorecard/test only).
`quotability()` reads `overall_score`/`scored`/`behavioral_runs` and returns a
classification — it never writes the score back. Rubric stays **v0.5**, no
version bump. `test_quotability` already pins "OVERALL unchanged by the
annotation"; the smoke below re-confirms scores 46.1/85.5 survive the attach.

**Evidence.** `asrs/types.py` (+field), `asrs/cli.py` (+attach, mirrors the
reliability attach), `asrs/scorecard.py` (`_quotability` + `_QUOTABILITY_BANDS`
+ both layout insertions), `tests/test_readout.py` (+3 tests: JSON round-trip
byte-for-byte the pure metric for static & panel modes; Citable/Provisional pill
render; not-scorable/absent → no card). Full suite **57/57** (was 54; +3).
End-to-end scorecard smoke: single layout → Quotability card + Citable pill, not
provisional; compare layout → 2 quotability cards, 2 Citable pills; overall
scores 46.1 / 85.5 intact through the attach.

**Canonical pair (regression signal).** UNCHANGED BY CONSTRUCTION — this cycle
touched no scoring source and quotability is display-only, so the STATIC delta
cannot move. Last live re-score (07:50Z local fire, LOG above + newest scoreable
signal): drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta
**+39.4**. In-cloud live re-score remains network-blocked; the by-construction
argument (no scoring.py/rubric/probe bytes changed; score-unchanged pinned by
test_quotability + the smoke) is the in-cloud regression proof per the playbook's
cloud-adapted rule.

**Runner health.** Newest hourly `runs/local/verify_*.json` is
`verify_20260723T040757Z` (04:07Z), ~4.1h old at this fire (08:15Z) — under the
6h "runner down" threshold but WATCH: no :41 artifact appeared at 05/06/07/08.
Also NOTE a pre-existing bug in that runner's score capture: its `scores` block
records `FileNotFoundError` because the `[asrs.scoring]` stderr coverage-warning
lines (the P2 "coverage-warning noise" backlog item) leak into the score path
argument. The runner's TEST block is green and its live re-score is separately
confirmed by the 05:52Z/07:50Z manual local fires, so the canonical signal is
intact — but the automated score capture is broken and should be fixed. Queued
observation in BACKLOG. If the next cloud fire still sees a 04:07Z artifact,
it crosses 6h → flag "runner down" in the next Slack digest.

**Ship.** Direct-to-main (readout + additive field + tests; no scoring semantics,
no payment/signing, no version bump — squarely in the direct-to-main tier). No
Slack: not a sensitive-class PR, not a score/capability change, and 08:15Z is not
the first cycle after 16:00Z (no daily digest due).

**Next.** (1) READOUT track next rotates in 4 cycles; the sibling P2 "Task battery
on the HTML card" is the natural next terminal→HTML lift (same `scorecard`
template now has two examples: `_reliability` and `_quotability`). (2) The
P0 peer-gated `_ENV_BLOCK_RE` "safety" fix (v0.5→v0.6) is still queued and is
the next scoring-semantics PR. (3) Fix the local verify runner's stderr→score-path
leak (the coverage-warning suppression P2 would also fix it at the source).

## Cycle 9 — 2026-07-23T09:15Z — METHOD (peer-gated PR #2)

**First duty (open-PR review).** None open at fire start (PR #1 merged; STATE
confirmed, `list_pull_requests` empty). Proceeded to pick work.

**What.** Broadened the env-block attribution classifier
(`asrs.behavioral.shopper._ENV_BLOCK_RE`) so `"safety"`-phrased hosted-browser
refusals are recognized as environment blocks, not only `"security"` ones.
`"safety"` is now a lexical sibling of `"security"` in BOTH alternations
(`browser (?:security|safety)` and `(?:security|safety) (?:policy|controls|
grounds)`). Rubric bumped **v0.5 → v0.6** (aggregation-rule change; dated
changelog). Opened as peer-gated PR #2 `loop/env-block-safety-phrasing` for
next-cycle adversarial review + self-merge.

**Why (METHOD, attribution honesty — invariant #4).** `_is_env_blocked` gates
which shopper runs enter the outcome/trust scoring denominator vs. route to
`hosted_agent_reachability`. The SAME hosted-browser URL-safety layer surfaces
its block as either word: committed evidence
(`runs/local/trial_stability_20260723T064359Z.json`) shows codex on the
canonical `.org` reporting *"blocked by browser safety controls"* /
*"Browser safety controls explicitly blocked the domain."* in one trial while
its sibling trials on the same domain said *"security"*. Under the old regex
that one all-false verdict (the agent saw NOTHING about the site) LEAKED into
the outcome/trust pool — under-crediting the site (invariant #4 violation) and
corrupting `panel_reliability`. Discovered in the 07:50Z local trial-count fire;
validated pattern is `experiments/trial_count_N_analysis.py::_ENV_BLOCK_FIXED`.
This is the narrow, evidence-backed subset of Cycle 7's deferred broadening
(test #8) — the "safety" family, same env-block family as "security", NOT the
harder semantic reputation-gate ("flagged as unsafe" / "unable to browse"),
which stays out of scope and with the `[LOCAL]` codex-reachability item.

**Negative direction preserved (verified).** Site-side blocks (403 / Cloudflare
/ 429 / CAPTCHA / robots.txt) are STILL NOT excused as environment, and
reputation-gate phrasings lacking the `browser-{security,safety}` vocabulary
remain out of scope. Confirmed by a pre-edit regex A/B (both old+new reject all
five site-side and both reputation-gate fixtures) and by test #2 / test #8
staying green.

**Evidence.** `asrs/behavioral/shopper.py` (regex + comment), `rubric/rubric_v0.yaml`
(v0.6 changelog + `version: "0.6"`), `tests/test_attribution.py` (+test #9
`test_env_block_safety_phrasing_covered`, fixtures VERBATIM from the committed
trial-stability artifact per invariant #3; asserts positive classification in
both orderings × {blockers, trust_events} AND denominator routing). Full suite
**58/58** (attribution 9/9 was 8/8; free-tier 8/8 after `pip install eth-account`
in the cloud venv — the sole prior failure was a missing dep, pre-existing on
main, not a regression).

**Canonical pair (regression signal).** UNCHANGED BY CONSTRUCTION. Behavioral-
only: static mode runs no panel, and `asrs/scoring.py` never imports the
classifier (it consumes a pre-computed `behavioral_runs` list), so the static
delta cannot move — the only change to a static report is the embedded
`rubric_version` string. Last confirmed live static delta (07:50Z local fire):
drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4**.
In-cloud live re-score network-blocked; by-construction argument is the cloud-
adapted regression proof (playbook §Ship). Live BEHAVIORAL re-score on a
codex-reachable domain is queued `[LOCAL]`.

**Runner health (WATCH → near-threshold).** Newest hourly `verify_*.json` is
still `verify_20260723T040714Z` (04:07Z) at this fire (09:15Z) — ~5h08m old, no
`:41` artifact at 05/06/07/08/09. Under the 6h "runner down" threshold but one
hour from crossing it; the next cloud fire (~10:xx) that still sees 04:07Z
should flag "runner down" in the Slack digest. Also the known coverage-warning
leak bug persists: this artifact's `scores` block is `FileNotFoundError` (the
`[asrs.scoring]` stderr lines leak into the score-path arg), so it yields NO
usable live delta regardless of age — the P2 coverage-warning suppression fixes
it at the source. Both noted in the sensitive-PR Slack DM for Jonah's visibility.

**Ship.** Peer-gated PR #2 (aggregation rule + version bump — sensitive class).
Bookkeeping (LOG/STATE/BACKLOG) direct-to-main. Slack DM sent (sensitive-class
PR opened — visibility for veto, not approval; runner-health folded in).

**Next hypothesis.** Once PR #2 merges (next cycle's first duty), `panel_reliability`
on the drift-flight.org trial-count panel should read stable/monotone
(N=2 0.80 → 5 0.92) instead of "mixed" — the leak fix is what makes the Cycle 3–5
reliability code report the true single-model curve. The cross-model N-curve
stays blocked on codex reachability.

### Cycle 9 addendum — 2026-07-23T09:2xZ — PR #2 merged externally (same fire)

PR #2 (env-block "safety" phrasing, v0.5→v0.6) was MERGED during this same fire
(merge commit 8fe9f46, clean fast-forward) — NOT by a loop self-merge; the
webhook reported it merged and auto-unsubscribed. v0.6 is now on main; full suite
re-run on merged main is **58/58** green. CAVEAT recorded in STATE + BACKLOG: the
external merge bypassed the playbook's fresh-context adversarial peer review (which
was to be the next cycle's first duty). Authoring-time self-review was thorough
(regex A/B across positive/negative/reputation-gate cases, fixtures traced to
committed evidence, static-isolation by construction) and merged main is green, so
risk is low — but a POST-MERGE adversarial sanity check is queued P0 (revert on
main per invariant #5 if any real defect surfaces; no force-push, no history
rewrite). The [LOCAL] live behavioral re-score of v0.6 is queued as the empirical
confirmation. No new Slack DM (the sensitive-PR DM already sent on open covers the
change; the merge is Jonah's own action). Ledger reconciled; this remains ONE
improvement for the fire.

## Cycle 10 — 2026-07-23T10:12Z — COVERAGE

**First duty (open-PR review).** None open at fire start (`list_pull_requests`
empty; STATE confirmed PR #1/#2 both merged). Proceeded to pick work on the
COVERAGE track.

**What.** Added a per-storefront-archetype (`kind`) rollup to the task battery.
`asrs/battery.py`: new `BatteryKindResult` dataclass + additive
`BatterySummary.per_kind` field, populated by `_per_kind_results` (groups the
per-task results by `kind`, insertion-ordered by first appearance, computes each
archetype's mean completion and within-archetype reliability spread over its
SIGNAL tasks only). Factored the battery-wide spread math into a shared
`_cross_task_spread` helper so a per-kind slice is computed identically to the
whole. `asrs/report.py`: `_battery_lines` prints a `by archetype:` sub-block
when the battery spans >1 kind (suppressed for a single archetype, where it would
just restate the battery-wide number). `tests/test_battery.py`: +2 tests
(`test_per_kind_rollup`, `test_per_kind_no_signal`) — grouping/order,
mean_completion, within-kind spread (single-task kind -> 0.0, no-signal kind ->
None not 0.0), and `to_dict()` serialization.

**Why (COVERAGE — north star "many storefront types").** The battery module
docstring AND `batteries/default_v1.yaml` both PROMISED a site could be read
"per storefront archetype (`kind`)" — but `kind` was only stored per task and
never rolled up; the implementation delivered per-task and battery-wide numbers
only. A site is rarely uniformly agent-ready (it can ace digital metered
services yet stumble on physical goods); the per-kind rollup lets the SAME run
be read one archetype at a time ("strong on digital_service, weak on
physical_good") instead of collapsing to one battery-wide spread. Closes the gap
between the documented design and the code, and makes the benchmark more flexible
across storefront types — exactly the north star's coverage axis. Attribution
honesty preserved: an archetype whose only intents produced no valid run is
reported as 0-signal with None stats, never charged completion or variance for an
intent nobody could observe (mirrors the battery-wide "no signal" convention).

**Evidence.** `asrs/battery.py` (BatteryKindResult, per_kind, _per_kind_results,
_cross_task_spread), `asrs/report.py` (`_battery_lines` by-archetype block),
`tests/test_battery.py` (+2 tests; 6/6 -> 8/8). Full suite **60/60**
(was 58/58 on merged main; +2 battery tests). eth-account installed into the
cloud `.venv` so test_free_tier is 8/8 (the sole non-installed-dep failure is a
fresh-container env artifact, not a regression — matches Cycle 9's note).
Render smoke: a synthetic 3-archetype battery renders the `by archetype:` block
and serializes `per_kind` to JSON correctly.

**Canonical pair (regression signal).** UNCHANGED BY CONSTRUCTION. The battery is
a diagnostic layer that does NOT feed the overall score, and static mode runs no
battery at all; `asrs/scoring.py` and the rubric are untouched (stays **v0.6**,
no version bump — additive/diagnostic, not a scoring-semantics change). A static
score of either canonical domain is therefore byte-for-byte unchanged. Last
confirmed LIVE static delta (07:50Z local fire): drift-flight.org **46.1 F** /
driftflight.com **85.5 B**, delta **+39.4**. In-cloud live re-score remains
network-blocked (agent proxy denies CONNECT to external hosts); by-construction +
offline tests are the cloud-adapted regression proof (playbook §Ship). No new
[LOCAL] live re-score is queued for this change — the static path cannot move.

**Runner health (CROSSED THRESHOLD).** Newest hourly `runs/local/verify_*.json` is
STILL `verify_20260723T040714Z` (04:07Z). At this fire (10:12Z) that is
**~6h05m old — past the 6h "runner down" threshold** the playbook sets. No `:41`
artifact appeared at 05/06/07/08/09/10. The local `local_verify.py` runner
(launchd on Jonah's machine, hourly :41) appears DOWN. Recorded in STATE; will be
flagged in the next Slack daily digest (first cycle after 16:00 UTC) per the
comms policy — not a standalone DM (runner-health goes in the digest). The
separate pre-existing bug (its `scores` block records FileNotFoundError because
`[asrs.scoring]` stderr coverage-warning lines leak into the score-path argument)
still stands; the P2 coverage-warning suppression fixes it at the source.

**Ship.** Direct-to-main (additive diagnostic field + terminal render + tests; no
scoring semantics, no payment/signing, no version bump — squarely the
direct-to-main tier). Bookkeeping (LOG/STATE/BACKLOG) same commit. No Slack:
not a sensitive-class PR, not a score change, and 10:12Z is not the first cycle
after 16:00Z (no digest due yet — the runner-down flag rides the 16:00 digest).

**Next hypothesis.** The per-kind rollup is terminal + JSON now; the natural
READOUT follow-up (queued P2, alongside the existing "Task battery on the HTML
card") is to render the by-archetype grid on the HTML scorecard — same
terminal-first-then-HTML deferral quotability/reliability took. Empirically, once
the [LOCAL] first live battery run executes, the per-kind spread should reveal
whether drift-flight.org's readiness is archetype-dependent (digital_service vs
physical_good) — a sharper reliability read than the single battery-wide spread.

## Local cycle — 2026-07-23T10:13Z — first duty: review+merge PR #2; then COVERAGE ([LOCAL] battery first live run)

**Reconciliation note (read first).** This local fire ran concurrently with the
Cycle-9 addendum and Cycle 10 (both above). The addendum labeled PR #2 "merged
externally / fresh-context peer review bypassed" — that is SUPERSEDED: PR #2 was
reviewed AND merged BY THIS LOCAL FIRE as its playbook-mandated first duty (the
local cycle's job is to "adversarially review + merge any open peer-gated PR").
The full fresh-context adversarial review DID run (below); the "post-merge sanity
check" P0 the addendum queued is DISCHARGED here, not deferred. The addendum's and
Cycle 10's append-only LOG entries stay as the historical record; only the living
STATE/BACKLOG lines were corrected. Cycle 10 (per-kind rollup) landed on main
mid-fire and was integrated cleanly (additive; my `cross_task_spread` is unaffected).

**First duty — adversarial review + MERGE of peer-gated PR #2**
(`loop/env-block-safety-phrasing`, Cycle 9, sensitive class: aggregation rule +
v0.5→v0.6). From fresh context, with the network the authoring cloud cycle lacked:
- **Invariant #3 (evidence)**: both test #9 fixtures ("blocked by browser safety
  controls" / "Browser safety controls explicitly blocked the domain") appear
  VERBATIM in runs/local/trial_stability_20260723T064359Z.json (grep-confirmed;
  2 "safety" / 8 "security" mentions). Not fabricated.
- **Full suite 58/58** on the branch (attribution 9/9). [60 on main after Cycle 10.]
- **Invariant #4 negative direction (LIVE regex A/B)**: ran old (v0.5) vs new
  (v0.6) `_ENV_BLOCK_RE` side by side. Committed site-side blocks
  (403/Cloudflare/429/CAPTCHA/robots/WAF) stay `False` on NEW; reputation-gate
  phrasings ("flagged as unsafe"/"unable to browse") stay `False`; the four
  committed "safety" fixtures flip `False→True` as intended.
- **Live static re-score (merge gate)**: drift-flight.org 46.1 F / driftflight.com
  85.5 B, delta **+39.4** — identical to baseline; reports now embed rubric "0.6".
  Static delta unchanged, version bump propagates.
- **Residual (non-blocking, logged BACKLOG P1)**: a hypothetical site-side block
  worded "…blocked by our safety policy" WOULD be mis-excused — but this is
  PRE-EXISTING and SYMMETRIC (the identical "…security policy" already matches on
  v0.5), not a regression from v0.6, and the classifier reads the agent's narration
  of its OWN tool gate (real site blocks narrate as HTTP/CF/CAPTCHA, pinned by
  test #2). Future hardening: agent-tool self-reference proximity anchor.
- **Verdict: SURVIVES → MERGED** (merge commit 8fe9f46; branch deleted). v0.6 on
  main. Slack DM sent (sensitive-class merge — visibility for veto, not approval).

**What (the [LOCAL] item).** Executed the oldest P0 `[LOCAL]` — "Task battery —
first live behavioral run" (COVERAGE). Budget-trimmed to a NEW 3-archetype battery
`batteries/trimmed_v1.yaml` (image_generation / api_subscription / physical_good —
one intent per distinct storefront kind) × {claude,codex} × 2 trials = 12 panels /
6 codex (under the ~10 cap; the full 5-intent battery would be 20 panels / 10 codex,
at the cap). Ran on drift-flight.org.

**Why.** A single shopper task is one draw from a wide distribution. The battery
turns "did it work once" into the benchmark's first `cross_task_spread` — is a
site's readiness intent-dependent, or does it hold across the KINDS of job an agent
might be sent to do? Measurement-flexibility + rigor (both north-star axes), and it
validates the Cycle-2/6 battery machinery on real panel data for the first time.

**Results.**
- **First live `cross_task_spread` = 0.089** ("consistent across intents"):
  drift-flight.org's readiness holds across intents — it is uniformly a
  subscription-gated, human-checkout storefront regardless of the job. Per-intent
  avg checkpoint completion: image_generation 53% (3 valid), api_subscription 60%
  (2 valid), physical_good 40% (2 valid); 3/3 intents observed (none "no signal").
- Primary task (image_generation): overall **45.1 F** (rubric 0.6),
  `panel_reliability` **0.87 stable** over 3 valid runs, quotability **CITABLE**
  (reproducible). (45.1 behavioral vs 46.1 static — outcome pillar drags slightly;
  no autonomous purchase possible, only human-browser card subscription.)
- **Invariant #1 verified**: EXACTLY ONE free-tier transaction for the whole
  3-intent battery (free-tier blob count 7→8; one `free_tier` reference in report).
- **v0.6 live-validated same fire**: codex#1 reported "rejected by the browser's
  site-safety policy" — a "safety" phrasing — and the merged v0.6 classifier
  correctly EXCLUDED it from the outcome denominator (4→3 valid) and surfaced it as
  a `hosted-agent-blocked` reachability finding, NOT a site FAIL. The exact leak the
  PR fixed, confirmed on live data.
- **Codex reachability datapoint**: codex#2 REACHED drift-flight.org normally
  (found product + price) on the same fire codex#1 was safety-blocked → the
  reputation gate is NON-DETERMINISTIC per-trial, not a hard per-domain block.
- The run predates Cycle 10's `per_kind` rollup, so its report has no per_kind block
  (cross_task_spread unaffected). The queued second datapoint will exercise per_kind
  on live multi-kind data.

**Evidence.** `batteries/trimmed_v1.yaml` (new, vendor-neutral, capability-worded,
intent strings verbatim from default_v1); report + terminal card force-added
(runs/ is gitignored):
runs/local/battery_trimmed_driftflightorg_20260723T101121Z.{json,card.txt}.

**Canonical pair (regression signal).** UNCHANGED — 46.1 F / 85.5 B, delta
**+39.4** (the merge-gate live re-score above). v0.6 is behavioral-only; static
delta cannot move.

**Runner health — DOWN (>6h).** Already flagged by Cycle 10; re-confirmed here:
newest `verify_*.json` is verify_20260723T040757Z (04:07Z), 6.10h old at 10:13Z.
Folded into this fire's Slack DM alongside the v0.6-merge notice. I did NOT chase
the launchd runner — outside the one-item mandate and the repo checkout.

**New observations → BACKLOG.** (1) The nested `claude -p` shopper spawns the
operator's FULL MCP fleet (trigger.dev/unity/linear/motherduck) before browsing —
~1 min startup per panel + unrelated external connections in the measurement
environment; should run minimal/empty MCP config. (2) The env-block "safety/
security policy" site-side hardening residual from the PR #2 review.

**Ship.** Direct-to-main: the battery execution is COVERAGE `[LOCAL]` work over an
already-shipped task-agnostic diagnostic (no scoring semantics; `trimmed_v1.yaml`
is a data file), plus LOG/STATE/BACKLOG + force-added evidence + ledger
reconciliation. The v0.6 merge (sensitive class) landed via the peer gate as the
first duty. Slack DM sent (v0.6 merged + first cross_task_spread + runner-down).

**Next hypothesis.** A SECOND `cross_task_spread` datapoint on driftflight.com (the
with-rails side) is the highest-value COVERAGE follow-up: if the rails side's
spread is also ~0 but at much higher completion, that is the cleanest statement of
the capability delta — "consistently ready across every intent" vs "consistently
gated across every intent" — and it exercises the Cycle-10 per_kind rollup on live
multi-kind data. One pair of spreads makes readiness intent-STABILITY a structural
claim, not a per-task artifact.

## Cycle 11 — 2026-07-23T11:15Z — TRUTH (direct to main)

**First duty (peer gate).** No open PRs (PR #1, PR #2 both merged). Nothing to review.

**What.** Pinned the POST-v0.6 reading of the committed trial-count panel as a
regression test on real panel data, and de-staled the analysis script that still
narrated the v0.6 fix as "proposed (not shipped)".
- NEW `tests/test_trial_stability_v06.py` (4/4): loads the append-only 06:44Z
  artifact `runs/local/trial_stability_20260723T064359Z.json`, reconstructs its
  `BehavioralRun`s, and recomputes the panel through the SHIPPED
  `asrs.reliability.panel_reliability` / `shopper._is_env_blocked`. Pins: (a) all
  5 codex runs — including t3, the former "browser safety controls" leak — are now
  env-blocked; (b) the valid pool is claude-only (codex observed nothing); (c) the
  corrected trial-count curve is monotone non-decreasing and "stable" at every N>=2
  (0.80 → 0.867 → 0.90 → 0.92); (d) it DIFFERS from the artifact's committed
  pre-v0.6 curve at N>=3 (documents supersession without editing the evidence file).
- Updated `experiments/trial_count_N_analysis.py` docstring + section labels: the
  "proposed" env-block predicate is now identical to the shipped `_ENV_BLOCK_RE`;
  section (1)'s prior "reproduction FAILED" now correctly reads "N>=3 SUPERSEDED
  (v0.6 fix)" — the committed curve is the append-only pre-fix record, not a
  fabrication. No behavior change to the derivation.

**Why (TRUTH).** v0.6 shipped the env-block "safety" broadening as a peer-gated
scoring-semantics change, but its effect had only been *simulated* offline
(analysis script) and *live-validated* on ONE new codex trial (the 10:13Z battery,
which routed a fresh "site-safety policy" refusal to reachability). The original
corrupting datapoint — codex t3 of the trial-count panel that first exposed the
leak — had never been re-read through the shipped classifier. This closes that
loop: the exact run that motivated v0.6 now reads correctly under v0.6, on
committed data, pinned so a future regex regression re-breaks the test. It also
converts the P0 "confirm the trial-count panel reads stable post-v0.6" from a
narrative claim into an executable one for the offline (data-recompute) half; only
a FRESH live 5-trial panel remains genuinely [LOCAL].

**Evidence.** `tests/test_trial_stability_v06.py` (new, 4/4);
`experiments/trial_count_N_analysis.py` (updated); source artifact
`runs/local/trial_stability_20260723T064359Z.json` (unchanged, append-only).
Full suite 60 → 64.

**Canonical pair (regression signal).** UNCHANGED BY CONSTRUCTION — this cycle
touches only `tests/` and `experiments/`; `scoring.py`, the rubric, and the static
scoring path are byte-for-byte untouched, so the static delta cannot move. Last
confirmed live: 46.1 F / 85.5 B, delta **+39.4** (10:13Z local merge-gate re-score,
rubric 0.6). In-cloud live re-score remains network-blocked (policy denial).

**Runner health — STILL DOWN (>7h).** Newest `verify_*.json` is
verify_20260723T040757Z (04:07Z) — 7h08m old at 11:15Z, no :41 artifact since.
Already flagged in STATE; belongs in the next Slack daily digest (first cycle after
16:00 UTC). Its live-re-score capture also remains broken by the coverage-warning
stderr leak (BACKLOG P2/coverage-warning).

**Ship.** Direct to main: tests + experiment-script narration, no scoring
semantics, no version bump. Not a capability/score change and pre-16:00 UTC → no
Slack DM (comms policy: quiet).

**Next hypothesis.** The offline half of the post-v0.6 stability confirmation is now
pinned; the remaining open TRUTH question is CROSS-MODEL — codex has never reached a
canonical domain in a full panel, so every stability curve to date is single-model
(claude-only) reproducibility. The codex-reachability/control-storefront attribution
fix (feed codex pre-fetched content when its browser is gated, marked assisted) is
the blocker; until it lands, "N stabilizes the panel" is answered only for claude.

## Local cycle — 2026-07-23T11:42Z — TRUTH ([LOCAL] codex reachability investigation)

**First duty — peer-gated PR review.** NONE open (PR #2 merged last fire, #1
earlier). Nothing to review/merge; proceeded to the one `[LOCAL]` item.

**What.** Executed the oldest P0 `[LOCAL]` TRUTH item — "Codex reachability
investigation" — via the committed harness `experiments/codex_reachability.py`
(previously written but uncommitted in the tree). It runs codex through the SAME
scorer path (`shopper._run_one → _codex_cmd`, network on, web_search on) against
the canonical pair ×2 each + a reputable control (example.com ×1) = **5 codex
invocations** (under the ~10 cap), records each domain's live HTTP status, and
classifies every refusal against (a) the SHIPPED `_ENV_BLOCK_RE` and (b) a
report-only reputation-marker lexicon. $0 read-only recon — no free-tier probe,
no zero CLI, no signing path, no regex/scoring change.

**Why.** The standing TRUTH open question ("codex hosted-browser refusal —
determinism, domain features, is it a reputation gate?") blocked the cross-model
panel-stability N-curve and had only anecdotal datapoints. Attribution honesty
(invariant #4) needs the characterization to come from the REAL code path on
COMMITTED transcripts, not hand-rolled prose — so a mis-attributed refusal can
never leak into a scoring denominator.

**Results (all 5 domains returned HTTP 200 — sites are UP).**
- **codex refused ALL 4 canonical trials** (driftflight.com t1/t2, drift-flight.org
  t1/t2). Every refusal is a REPUTATION gate keyed on domain age + absent footprint
  — trust_events cite ".com created 2026-07-16, seven days" and ".org indexed only
  2026-07-20, three days … no independently verifiable footprint" — but the BLOCK
  itself always narrates with browser-{safety,security} vocabulary ("blocked by
  browser and web safety controls as unsafe", "refused by the browser's security
  policy", "blocked by the browser safety layer", "Browser security controls
  blocked …"). The reputation assessment and the browser-safety block are the SAME
  surfaced mechanism, not two separable phrasings.
- **v0.6 classifier caught 4/4** (`_is_env_blocked` True on every canonical trial)
  → all routed to hosted-agent reachability, NONE mis-scored as a site FAIL. First
  LIVE validation of the merged v0.6 "safety" broadening on FRESH transcripts
  (2 trials narrate "safety" only [sec_family False], 2 narrate "security" — v0.6
  catches both alternations; v0.5 would have leaked the two "safety"-only trials).
- **Reputable control (example.com) NOT blocked** (`_is_env_blocked` False, zero
  reputation markers): codex browsed it fine and correctly reported "IANA-reserved
  documentation domain … no product for sale." This is the crux control — codex's
  browser WORKS on a trusted domain, so the canonical refusals are its own
  REPUTATION gate (fresh domain / no footprint), not a broken browser.
- **No pure semantic reputation-gate phrasing captured** (the test #8 case:
  "flagged as unsafe" / "unable to browse" WITHOUT browser-safety vocabulary).
  Every observed refusal carries the browser-{security,safety} vocabulary v0.6
  already covers → NO regex broadening is warranted from this evidence, and blindly
  adding bare "unsafe"/"flagged" would risk excusing real site blocks (the exact
  hazard STATE flagged). Test #8 stays an open spec awaiting a committed transcript
  of the harder case; this run did not produce one.
- **"1 leak candidate" is a FALSE POSITIVE of the report-only leak heuristic** — it
  is example.com (the control), flagged only because it is up + observed-nothing +
  not-env-blocked + not-security-family. But example.com is NOT a refusal (codex
  correctly found no storefront). NOT a real attribution leak; `_is_env_blocked`
  behaves correctly (example.com was never blocked). The heuristic's `or not
  matches_security_family` clause over-catches legitimate "nothing to buy" runs —
  a diagnostic-only weakness, noted for the harness, not a scoring bug.

**Determinism update.** At the 10:13Z battery fire codex REACHED drift-flight.org
on one trial → "non-deterministic per-trial". At 11:42Z BOTH canonical domains were
gated on 100% of trials (4/4). So the gate is time-varying but currently CLOSED on
both — neither canonical domain is codex-reachable right now. Cross-model panel
stability stays BLOCKED on the control-storefront / pre-fetched-content fix; the
example.com control now proves that fix's premise (codex's browser works on
reputable domains → the variable is domain reputation, addressable by a reputable
agent-native control storefront or marked-assisted pre-fetched content).

**Canonical pair (regression signal).** Fresh LIVE static re-score this fire
(11:50Z, both HTTP 200): drift-flight.org **46.1 F** / driftflight.com **85.5 B**,
delta **+39.4** — identical to the 10:13Z merge-gate score; reports embed rubric
"0.6". This diagnostic experiment touches no scoring code, so the delta is unchanged
by construction AND re-confirmed live. Doubles as a fresh live canonical signal
while the launchd runner is down (see below).

**Runner health — STILL DOWN (>6h).** Newest `verify_*.json` is verify_20260723T040757Z
(04:07Z, rubric 0.5) — ~7.7h old at this fire, well past the 6h threshold; no :41
artifact 05:00–11:00Z. This fire is BEFORE 16:00 UTC, so no digest yet; to be folded
into the next post-16:00 Slack digest per comms policy. Did NOT chase the launchd
runner (outside the one-item mandate / repo checkout).

**Evidence.** Harness committed: `experiments/codex_reachability.py`. Artifacts
force-added (runs/ is gitignored): `runs/local/codex_reachability_20260723T114225Z/
summary.json` + 5 raw codex transcripts under `.../transcripts/`.

**Ship.** Direct-to-main: evidence-gathering + a new experiment harness + LOG/STATE/
BACKLOG. NO scoring semantics changed (no regex change — the run's finding is that
v0.6 is SUFFICIENT for every observed refusal; scoring.py/`_ENV_BLOCK_RE`
byte-for-byte unchanged, full suite 60/60 green pre-commit).

**Next hypothesis.** The cross-model N-curve cannot advance until codex can reach a
storefront. Highest-value next TRUTH step is to BUILD the control-storefront /
pre-fetched-content attribution fix (feed codex the statically-fetched homepage +
docs when its browser gate fires, mark the run `assisted`, and keep it OUT of the
unassisted reachability denominator) — design in-cloud from these committed
transcripts, execute `[LOCAL]`. Separately, COVERAGE's second `cross_task_spread`
datapoint no longer needs codex (claude reaches both domains), so it stays runnable.

## Cycle 12 — 2026-07-23T12:18Z — READOUT (direct to main)

**First duty.** No open peer-gated PR (PR #2 merged 09:47Z; PR #1 merged 03:00Z).
Nothing to review — proceeded to the one improvement.

**Track.** READOUT (rotation: …Cycle 11 TRUTH → Cycle 12 READOUT). Focus pointer
in STATE named READOUT for this cycle.

**What.** The task battery's cross-intent readout (`battery_summary`) now renders on
the HTML scorecard. It already shipped terminal (Cycle 6) + JSON (`Report.battery_summary`,
types.py) but stopped at the HTML card — so the one place a leaderboard reader looks
never saw whether a site's readiness holds across intents. Added `scorecard._battery(rep)`:
a "Task battery" card with (a) a cross-task-spread verdict pill (Consistent /
Somewhat intent-dependent / Intent-dependent, thresholds 0.15/0.35 **mirroring the
terminal `report._battery_lines` exactly**), (b) a per-intent coverage grid (intent,
archetype chip, completion bar + %, valid-run count; no-signal intents shown as "no
signal", never a site failure), (c) the Cycle-10 `per_kind` by-archetype rollup
(completion + within-kind spread + intents), shown only when the battery spans >1
kind — same suppression the terminal uses. Wired into BOTH layouts (`_domain_column`
single, `_section_rows` compare), placed after Panel reliability. Same
terminal→JSON→HTML deferral quotability (Cycle 8) and reliability (Cycle 3→4) took.

**Why.** North-star readout clarity + storefront-type flexibility: the cross_task_spread
signal (whether the single-task headline overstates readiness) and the per-archetype
slice ("strong on digital_service, weak on physical_good") now travel with the score
everywhere it goes — terminal, JSON, and the hosted card — instead of only the two
machine-readable surfaces. The battery card was the last diagnostic still terminal/JSON-only.

**Invariants.** Additive/display-only. rubric **v0.6 UNCHANGED** — scoring.py, the
rubric YAML, probes, and payment/signing code are byte-for-byte untouched (`git diff
--name-only` = asrs/scorecard.py + tests/test_readout.py only). NOT a scoring-semantics
change → no version bump, no peer gate; direct-to-main per the readout+tests rule.
Capability-worded, vendor-neutral (no domain/vendor special-casing; renders whatever
`battery_summary` the pipeline produced). Evidence: the card reads only the additive
`battery_summary` dict the Report already carries — nothing invented.

**Tests.** `tests/test_readout.py` 8/8 → **12/12** (+4): battery_summary round-trips
through JSON; multi-kind battery renders header + each intent row + By-archetype rollup
+ each archetype + the spread value; single-kind battery renders the card but suppresses
the rollup (mirrors terminal); absent/None battery_summary → empty string (no card).
Fixtures built through the real `asrs.battery.aggregate_battery` on synthetic runs, not
hand-typed dicts, so the render test tracks the true aggregation shape. Full suite
64 → **68/68** (all files green; free-tier 8/8 with eth-account installed in a fresh
.venv). End-to-end `build_scorecard` sanity: battery card renders in single + compare
layouts, and a report WITHOUT a battery correctly renders no battery card.

**Canonical pair (regression signal).** UNCHANGED BY CONSTRUCTION — display-only,
scoring path byte-for-byte untouched, so the static delta cannot move. In-cloud live
re-score remains blocked (network policy denies canonical domains); the standing live
signal is the manual local fires: drift-flight.org **46.1 F** / driftflight.com
**85.5 B**, delta **+39.4** on rubric v0.6 (STATE, re-confirmed live 11:50Z). Runner
still DOWN (newest verify_20260723T040757Z, 04:07Z, now ~8h old — past 6h); to be
flagged in the next post-16:00 Slack digest per comms policy (this fire is before 16:00 UTC).

**Ship.** Direct-to-main: readout + tests + LOG/STATE/BACKLOG, no scoring semantics.

**Next hypothesis.** The battery card now needs REAL multi-kind battery data to prove
itself on a hosted card — the queued [LOCAL] second cross_task_spread datapoint (driftflight.com
or the full 5-intent battery on drift-flight.org) will be the first live run whose report
carries per_kind, so the by-archetype grid can be eyeballed on an actual scorecard. No
new code needed for that; it exercises this cycle's render path on live data.

## Cycle 13 — 2026-07-23T13:18Z — METHOD (direct to main)

**First duty.** No open peer-gated PR (`list_pull_requests` open = []; PR #2 merged
09:47Z, PR #1 merged 03:00Z). Nothing to review — proceeded to the one improvement.

**Track.** METHOD (rotation: …Cycle 12 READOUT → Cycle 13 METHOD). Focus pointer in
STATE named METHOD for this cycle.

**What.** Fixed the coverage-warning noise AT THE SOURCE (`asrs/scoring.py`). The
roll-up emitted one raw `print(..., file=sys.stderr)` per rubric check with no result;
in a static run ALL ~8 behavioral-only checks are legitimately absent, so every static
run spewed ~12 `[asrs.scoring] warning:` stderr lines — noise that buried genuinely-
unexpected gaps AND leaked into the local verify runner's captured score-path argument
(the ESCALATED Cycle-8 downstream bug). Change: route the three coverage warnings
through `logging.getLogger("asrs.scoring")` instead of raw stderr, and split the
"absent rubric check" warning by a new `_is_behavioral_only(check)` classifier —
behavioral-only checks (the whole `outcome` pillar, per the rubric's own "outcome
(behavioral only)" structure, plus `trust_panel_willingness` / `trust_live_session`
from the live panel) log at DEBUG (expected absent in static mode); a genuine static
gap still logs at WARNING. Under Python's default logging (no basicConfig, WARNING-level
lastResort handler → stderr), DEBUG is dropped and WARNING still reaches stderr — so a
realistic static run now emits ZERO warning lines while genuine gaps stay visible,
unchanged. No `basicConfig` added; visibility of real warnings is preserved exactly.

**Why.** North-star methodological rigor + measurement-infra reliability. (1) Legibility:
a normal run's stderr no longer carries ~12 false-alarm lines, so a real coverage gap
(a crashed static probe, an unknown pillar, a result not in the rubric) is no longer
buried. (2) It fixes the hourly `local_verify.py` runner's broken live-canonical re-score
capture at the source — its `scores` block recorded FileNotFoundError because those
`[asrs.scoring] warning:` lines leaked into the path it passed; a normal static score
now produces zero such lines. (Any residual runner-side robustness — the runner should
not merge stderr into a path arg — is a separate item, but the noise SOURCE is gone.)

**Invariants.** (#2 versioned comparability) NOT a scoring-semantics change — this
touches ONLY warning routing (print→logger) + a warning-verbosity classifier that is
NEVER read by the scoring math. rubric **v0.6 UNCHANGED**; `git diff` on the scoring
arithmetic is empty (verified: every changed line is a warning/logger/comment/blank —
no weight, max_points, cap, aggregation, or renormalization line touched). Scores are
byte-for-byte identical (pinned by new test #11 + the existing regression tests #3–#6,
all green). Capability-worded, vendor-neutral (the classifier keys on pillar/check-id
structure, no domain or vendor). (#3 evidence) new tests trace to the bundled rubric's
real check set, not hand-typed. Direct-to-main per the "probe bug-fixes that don't
change scoring semantics" + tests rule.

**Tests.** `tests/test_scoring.py` 7/7 → **11/11** (+4, framework-free capture handler on
the `asrs.scoring` logger): (a) a realistic full static run emits ZERO warnings and the
behavioral-only absences are still recorded at DEBUG (visible under -v, not swallowed);
(b) an absent STATIC check (x402_probe dropped) STILL warns, and behavioral-only checks
never warn even alongside other absences; (c) a result not in the rubric AND an unknown
pillar both still warn (genuinely-unexpected → loud); (d) warning routing does not change
the score (71.4 for the same observable pillars). Empirically confirmed out-of-band: a
realistic static score (all 15 static checks present, all behavioral absent) prints an
EMPTY stderr. Full suite 68 → **72/72** (all files green; free-tier 8/8 with eth-account
0.13.7 installed).

**Canonical pair (regression signal).** UNCHANGED BY CONSTRUCTION — warning-routing-only,
scoring arithmetic byte-for-byte untouched, so the static delta cannot move. In-cloud
live re-score remains blocked (network policy denies canonical domains); the standing
live signal is the manual local fires: drift-flight.org **46.1 F** / driftflight.com
**85.5 B**, delta **+39.4** on rubric v0.6 (STATE, last live-confirmed 11:50Z).

**Runner health — STILL DOWN (>6h).** Newest `verify_*.json` is verify_20260723T040757Z
(04:07Z, rubric 0.5) — **9.2h old at this fire** (measured 13:18Z), well past the 6h
threshold; no :41 artifact since 04:00Z. This fire is BEFORE 16:00 UTC → no digest yet;
to be folded into the next post-16:00 Slack digest per comms policy. This cycle's fix
means that WHEN the launchd runner is restarted, its live re-score capture will work (the
stderr leak source is removed) — a concrete unblock for the runner, not just cleanup.

**Ship.** Direct-to-main: scoring warning-routing bug-fix + tests + LOG/STATE/BACKLOG,
no scoring semantics. No Slack DM (no sensitive PR, no score/capability change, before
16:00 UTC) per the quiet-comms policy.

**Next hypothesis.** Two follow-ons: (1) the runner-side robustness (don't merge stderr
into a path arg) is a belt-and-suspenders [LOCAL] fix once the runner is restarted;
(2) the P1 "nested shopper spawns the full user MCP fleet" cleanliness fix is the next
METHOD-flavored measurement-hygiene win (direct-to-main plumbing, [LOCAL] panel to
verify identical checkpoints).

## Cycle 14 — 2026-07-23T14:22Z — COVERAGE (peer-gated PR #3)

**First duty.** No open peer-gated PR at cycle start (`list_pull_requests` open = [];
PR #2 merged 09:47Z, PR #1 merged 03:00Z). Nothing to review — proceeded to the one
improvement. (PR #3, below, is THIS cycle's output; it is reviewed+merged NEXT cycle,
never in the same fire.)

**Track.** COVERAGE (rotation: …Cycle 13 METHOD → Cycle 14 COVERAGE). Focus pointer in
STATE named COVERAGE for this cycle.

**What.** Gave the ACP/UCP payment rail parity in KIND with the x402 handshake: the
commerce-protocol partial on `x402_probe` now REQUIRES a validated manifest, not any
HTTP 200. `asrs.probes.protocols._commerce_protocol_evidence` previously awarded 4.0
whenever `/.well-known/ucp` or `/.well-known/agentic-commerce` returned a 200 with >10
chars of ANY body — a catch-all SPA index or soft-404 page served at those paths
false-positived as a live commerce rail. New `_parse_commerce_manifest` (mirroring
`_parse_x402`) grants credit only when the body parses as a real UCP service/capability
manifest (`services`/`capabilities`/`payment`/`endpoints`, or reverse-domain `dev.ucp.*`
capability ids) or an ACP checkout payload (`line_items`/`payment_provider`/
`checkout_session*`) — grounded in the published specs (Google "Under the Hood: UCP" +
ucp.dev; Stripe ACP + OpenAI Agentic Checkout). A validated hit is relabeled
`commerce-protocol-live` (an ELICITED manifest, parity in kind with `x402-live`); the
marker tiers `commerce-protocol-only` (doc phrase) and `commerce-protocol-via-platform`
(Shopify fingerprint) are UNCHANGED. Points ceiling unchanged (still 4.0 partial — the
rubric reserves full `x402_probe` marks for a live x402 handshake).

**Why.** North-star measurement coverage/flexibility (many payment rails) + rigor. This
is the standing P1 COVERAGE item ("ACP/UCP checkout-session … parity with the x402 probe,
currently markers/partial credit only"), scoped to its smallest scientifically meaningful
slice. Capability lens: a machine can only transact against a commerce protocol if the
merchant serves a real, parseable manifest; a bare 200 at a well-known path gives an agent
nothing to act on, so crediting it OVERSTATED readiness. The fix measures the rail's
actual capability (does it serve a validated manifest?) and removes an inflating false
positive as the dividend.

**Invariants.** (#2 versioned comparability) partial-credit rule changed → rubric
**v0.6 → v0.7** with a dated changelog; pillar weights, caps, grade bands, and the
`x402_probe` ceiling untouched. (#1 $0-only) NO POST/signing added — the parser only GETs
and JSON-parses well-known paths. Vendor-neutral / capability-worded: keys on protocol
manifest STRUCTURE only, never a vendor or domain (`ucp`/`acp` are protocol identifiers
like the existing `x402`/`mcp`). Direction MONOTONE NON-INCREASING on the well-known
branch — no domain with a genuine manifest loses credit.

**Tests.** `tests/test_protocols.py` (**7/7**, new — no dedicated protocols test existed
before): validated UCP manifest → `commerce-protocol-live` 4.0; validated ACP payload →
live 4.0; **bare-200 SPA index → no credit** (the false-positive fix, was 4.0);
non-commerce JSON / array / empty / non-200 → not a manifest; doc-phrase marker tier
preserved; canonical `.org` shape → `None` (FAIL 0.0 upstream); reverse-domain `dev.ucp.*`
ids recognized. Fixtures fake, grounded in the published UCP/ACP shapes. Full suite
72 → **79/79** (all files green; free-tier 8/8 with eth-account in a fresh `.venv`).

**Canonical pair (regression signal) — UNCHANGED, by COMMITTED EVIDENCE (not just
construction).** In-cloud live re-score blocked by network policy (external domains
denied; re-confirmed this fire: both canonical domains return NOT SCORABLE, `x402_probe`
= site-unreachable, report embeds rubric v0.7 once the branch is checked out). But the
delta is provably unmoved from committed reports:
- **driftflight.com** (85.5 B) earns `x402-live` (transactability 87.5%) and returns from
  `_x402_probe` BEFORE reaching the commerce branch → unaffected.
- **drift-flight.org** (46.1 F) already scores `x402_probe` = FAIL 0.0 /
  no-agent-native-payment (`runs/local/battery_trimmed_driftflightorg_20260723T101121Z.json`)
  — i.e. `_commerce_protocol_evidence` is already `None` for it (no well-known manifest, no
  phrases, not Shopify), today AND after. Pinned by `test_canonical_org_unchanged`.
So the static delta **+39.4** cannot move. A LIVE pair re-score on v0.7 is requested at
merge-time review (peer cycle with network) / queued `[LOCAL]`.

**Runner health — STILL DOWN (>10h).** Newest `verify_*.json` is verify_20260723T040757Z
(04:07Z, rubric 0.5), now ~10.3h old at this fire — well past the 6h threshold; no :41
artifact since 04:00Z. This fire is BEFORE 16:00 UTC → to be folded into the next
post-16:00 Slack daily digest per comms policy.

**Ship.** Peer-gated PR #3 `loop/commerce-manifest-validation` (scoring-semantics: a
partial-credit rule + rubric version bump — sensitive class). Opened this fire; the NEXT
cycle's first duty is the fresh-context adversarial review + self-merge. No CI configured
in the repo (no `.github/workflows`), so no CI gate to drive. Loop bookkeeping
(LOG/STATE/BACKLOG) direct to main so the next cycle sees the open PR. Slack DM sent
(sensitive-class PR opened — visibility for veto, not approval).
https://github.com/jnakagawa/agentic-readiness/pull/3

**Next hypothesis.** (1) Next cycle reviews+merges PR #3 (run the live pair re-score on
v0.7 if networked — confirm +39.4 holds and reports embed 0.7). (2) The BROADENING
direction of this rail (catch MORE real ACP/UCP surfaces that currently score 0 — more
well-known paths, a live ACP `checkout_sessions` elicitation) is score-INCREASING and
needs live verification on 2+ real domains → a distinct [LOCAL]-verified follow-up, not
folded here (this cycle was deliberately the non-inflating, offline-verifiable half).

### Cycle 14 addendum — 2026-07-23T~14:3xZ — PR #3 merged externally (same fire)

PR #3 (commerce-manifest validation, v0.6→v0.7) was **MERGED during this same fire**
(merge commit 72a2e5b), before the mandated next-cycle fresh-context adversarial review
could run — Jonah/an operator merged it directly. This is the exact Cycle-9/PR-#2 pattern.
An external merge is ACTIVE consent (stronger than the veto-silence the playbook relies
on), so it is not a bypass on the loop's part; I did NOT merge my own fire's PR.
Post-merge reconciliation THIS fire (bookkeeping only, not a second improvement cycle):
pulled main, ran the FULL suite on the merge commit → **79/79 green**; confirmed v0.7 and
`_parse_commerce_manifest` on main. De-staled the rubric title comment v0.6→v0.7 (the
`version:` field was already 0.7; header line lagged). Because the fresh-context review
was pre-empted, it converts to the NEXT cycle's FIRST duty as a POST-merge sanity check
(retain-or-revert, per the sensitive-class post-merge rule) PLUS the queued P0 [LOCAL]
live v0.7 canonical re-score. Canonical delta still argued UNCHANGED by committed evidence
(.com→x402-live never reaches the branch; .org→FAIL 0.0 no-agent-native-payment); the LIVE
v0.7 re-score is the remaining confirmation. No Slack DM for the merge itself — the actor
IS the DM recipient, so a "your PR merged" ping would be noise; it folds into the next
post-16:00 UTC digest. Session auto-unsubscribed from PR #3 activity (merged = final).

## Cycle 15 — 2026-07-23T15:18Z — TRUTH (direct to main)

**First duty — post-merge sanity check of v0.7 (PR #3), RETAIN.** PR #3
(commerce-manifest validation, v0.6→v0.7) was MERGED EXTERNALLY during the Cycle-14
fire (commit 72a2e5b), pre-empting the mandated fresh-context pre-merge review — so per
STATE it converts to this cycle's FIRST duty as a POST-merge retain-or-revert sanity
check. Ran it from fresh context and it SURVIVES → RETAIN:
- **Vendor-neutral / capability-worded.** `_parse_commerce_manifest` keys ONLY on
  protocol STRUCTURE: `_UCP_MANIFEST_KEYS` (services/capabilities/payment[s]/endpoints)
  and `_ACP_PAYLOAD_KEYS` (line_items/payment_provider/checkout_session*), plus
  reverse-domain `dev.ucp.*` capability ids. No vendor or domain string anywhere; `ucp`/
  `acp` are protocol identifiers like the existing `x402`/`mcp`. Passes the "would a
  critic call this vendor-rigged?" test.
- **Direction monotone NON-INCREASING** on the well-known branch — a genuine manifest
  still earns 4.0; only the bare-200 false positive loses it. No domain with a real
  manifest can lose credit. `$0`-only intact (parser only GETs + JSON-parses; no POST/
  signing added). Ceiling unchanged (4.0 partial).
- **Test coverage complete.** `tests/test_protocols.py` (7/7): validated UCP→live 4.0,
  validated ACP→live 4.0, bare-200 SPA index→no credit (the fix), random/array/empty/
  non-200→not a manifest, doc-phrase marker preserved, canonical `.org` shape→None,
  reverse-domain caps recognized.
- **Canonical delta unchanged — confirmed by COMMITTED evidence, not just construction.**
  The committed `.org` report
  (`runs/local/battery_trimmed_driftflightorg_20260723T101121Z.json`) shows `x402_probe`
  = FAIL 0.0 / `no-agent-native-payment` — i.e. `_commerce_protocol_evidence` already
  returned None under v0.6 (no validated OR bare manifest served at the well-known paths;
  they 404). So under v0.7 it still returns None → still FAIL 0.0. `.com` (85.5 B) earns
  `x402-live` and returns from `_x402_probe` BEFORE the commerce branch → unaffected.
  Static delta **+39.4** cannot move. Pinned by `test_canonical_org_unchanged`. LIVE v0.7
  re-score on main stays the queued [LOCAL] P0 (network-blocked in-cloud).
- Full suite **79/79 green** on the merge commit at cycle start.

**Track.** TRUTH (rotation: …Cycle 14 COVERAGE → Cycle 15 TRUTH). Focus pointer in STATE
named TRUTH for this cycle.

**What.** Built a faithful **record/replay** capability on `asrs.fetch.FetchContext` so a
live crawl's response cache can be serialized to a fixture (`save_fixture`) and replayed
offline with byte-for-byte fidelity and ZERO network (`from_fixture` → replay mode). A
new `replay: bool` (default False) makes `_fetch` return a clean `replay-miss` FetchResult
(status None, error set) on any unrecorded request instead of touching the network — a
replayed crawl is a closed world, and a miss is itself a signal that a probe changed WHAT
it fetches. `save_fixture`/`from_fixture` round-trip the cache (`(method, url, ua)` →
`FetchResult`) through JSON, restoring `base_url` so probe path resolution reproduces the
original cache keys.

**Why.** This directly discharges the loop's standing OPEN QUESTION (STATE): the cloud
env has no outbound network, so the playbook's per-cycle LIVE canonical re-score cannot
run in-cloud and the regression signal has been HAND-ARGUED "by construction" every cycle.
Record/replay is the enabling infrastructure for the cloud-adapted form the playbook calls
for — "offline regression tests as the in-cloud proxy": a canonical-pair fixture captured
[LOCAL] once can be re-scored in-cloud EVERY cycle as a deterministic, executable guard,
converting the prose argument into a test that fails if a scoring/probe change moves the
delta against frozen inputs. North-star rigor: reproducible, evidence-linked, network-free.

**Invariants.** NOT a scoring-semantics change — `asrs/scoring.py` and `rubric/` are
byte-for-byte untouched (`git status` clean on both), so the canonical delta is unchanged
BY CONSTRUCTION AND the new code is dormant on every existing path (`replay` defaults
False; live/static fetching is byte-identical). (#1 $0-only) replay NEVER opens a socket;
a POST miss is a clean replay-miss, no handshake escapes. (#3 evidence) the mechanism is
verified end-to-end below; the REAL canonical fixture capture is queued [LOCAL]. No
version bump (no rubric semantics touched). Direct-to-main (fetch-layer plumbing + tests).

**Tests.** `tests/test_fetch_replay.py` (**3/3**, new): (1) round-trip fidelity —
save→from_fixture reproduces every result byte-identically and restores base_url; (2)
replay-miss is clean — an unrecorded GET/POST returns status None + `replay-miss` error,
never a crash, never a network call; (3) END-TO-END regression proxy — replaying a
recorded x402 handshake through the REAL `protocols.run` pipeline yields `x402-live` PASS
8.0, replaying a bare homepage yields `no-agent-native-payment` FAIL 0.0, and the x402
capability delta (the thing the benchmark exists to measure — rails side earns the payment
capability, bare side does not) is pinned at the full 8.0 OFFLINE. Full suite 79 → **82**
(11 files all green; free-tier 8/8 in a fresh `.venv` with eth-account).

**Canonical pair (regression signal) — UNCHANGED, by construction.** In-cloud live
re-score network-blocked (both canonical domains NOT SCORABLE in-cloud). scoring.py +
rubric v0.7 + probes/protocols.py all byte-for-byte unchanged this cycle → delta cannot
move. Last committed live signal: `.org` 46.1 F / `.com` 85.5 B, delta **+39.4** (rubric
0.5 verify artifact `verify_20260723T040757Z.json`; re-confirmed +39.4 on v0.6 at the
10:13Z local merge-verify; argued unchanged on v0.7 above).

**Runner health — STILL DOWN (>11h).** Newest committed `verify_*.json` is
verify_20260723T040757Z (04:07Z, rubric 0.5) — now ~11.2h old, well past the 6h
threshold; no `:41` artifact since 04:00Z. This fire is at 15:18Z (BEFORE 16:00 UTC) → to
be flagged in the next post-16:00 UTC Slack daily digest per comms policy, together with
the queued [LOCAL] v0.7 live re-score.

**Ship.** Direct-to-main (no scoring semantics; additive fetch-layer capability + tests).
No Slack DM: not a sensitive-class change, not a score change, and before 16:00 UTC — it
folds into the next digest. No CI configured in the repo.

**Next hypothesis.** (1) [LOCAL] capture the canonical-pair fixtures — one full scoring
crawl each of drift-flight.org and driftflight.com with `save_fixture`, committed to
`fixtures/canonical/` — so a cloud cycle can then wire `test_canonical_replay.py` that
replays both through the CURRENT scoring pipeline and asserts overall 46.1 F / 85.5 B /
delta +39.4 on rubric v0.7. That is the true in-cloud proxy for the live re-score the
playbook wants. (2) Once the fixture lands, EVERY future scoring-semantics change gets an
executable canonical regression guard instead of a prose "by construction" argument.
## Local cycle — 2026-07-23T15:43Z — TRUTH (PR #3 LIVE re-score half)

**Reconciliation with the concurrent cloud Cycle 15 (15:18Z).** This local fire started
from a checkout that predated cloud Cycle 15's push; on rebase they merged cleanly and
COMPLEMENTARILY. Cloud Cycle 15 did the OFFLINE half of the PR #3 post-merge verification
(fresh-context sanity check → RETAIN, argued by committed evidence) and built the
`FetchContext` record/replay infra so a future canonical fixture can guard the delta
in-cloud with no network. This local fire does the half the cloud cannot: the NETWORKED
LIVE re-score. Together they fully discharge the PR #3 post-merge P0 (offline RETAIN +
live confirmation).

**First duty (peer gate) — NOTHING open.** PR #3 `loop/commerce-manifest-validation`
(Cycle 14, v0.6→v0.7 commerce-manifest validation) is **already MERGED**
(2026-07-23T14:45:30Z, merge commit `72a2e5b`, `gh` state MERGED). Per the Cycle-14
addendum it was merged EXTERNALLY (operator, active consent — stronger than veto-silence),
pre-empting the pre-merge review, which converted to cloud Cycle 15's post-merge
retain-or-revert sanity check (RETAIN). The merge commit message carries a peer-gate
verdict either way. No other open PRs (`gh pr list --state open` empty) — first duty
discharged, nothing to review this fire.

**What.** Executed the LIVE half of the post-merge P0 `[LOCAL]` — the canonical re-score
for PR #3 on **v0.7 (now on main)** — independently, from fresh context (playbook: "post-
merge, queue a `[LOCAL]` live verification"). Ran the full suite, then static-scored both
canonical domains + one third-domain spot-check.

**What.** Executed the oldest P0 `[LOCAL]` — the merge-time LIVE canonical re-score for
PR #3 on **v0.7 (now on main)** — independently, from fresh context, discharging the
queued post-merge verification (playbook: "post-merge, queue a `[LOCAL]` live
verification"). Ran the full suite, then static-scored both canonical domains + one
third-domain spot-check.

**Why.** TRUTH / live calibration. The merge commit CLAIMED the delta was unchanged on
v0.7; an independent post-merge re-score confirms the merge was sound and — with the local
`local_verify.py` runner DOWN (>11h) — produces a fresh LIVE canonical signal the down
runner isn't emitting. Also confirms PR #3's tightening (commerce-protocol credit now
requires a VALIDATED manifest, not a bare 200) introduced no regression and no false
positive on reachable domains.

**Evidence.**
- Full suite **79/79** green pre-flight (attribution 9, battery 8, battery_wiring 4,
  free_tier 8, protocols 7, quotability 8, readout 12, reliability 8, scoring 11,
  trial_stability_v06 4).
- Live static re-scores (both HTTP 200, rubric **v0.7** embedded, `scored=True`):
  `runs/local/merge_verify_pr3_v07_driftflightorg_20260723T154332Z.json` (46.1 F),
  `runs/local/merge_verify_pr3_v07_driftflightcom_20260723T154332Z.json` (85.5 B).
- `x402_probe` findings UNCHANGED and NO `commerce-protocol-*` false positive on either:
  `.org` → `no-agent-native-payment` (FAIL 0.0, falls through the commerce branch → None,
  no `x402-live`, no `commerce-protocol-*`); `.com` → `x402-live` (transactability 87.5%,
  returns before the commerce branch, no `commerce-protocol-*`). Confirmed by JSON token
  scan.
- Third-domain spot-check (regression on the false-positive removal): `example.com` →
  22.5 F, rubric v0.7, `scored=True`, NO `commerce-protocol-*`, NO `x402-live` — the v0.7
  probe path runs cleanly on an unrelated reachable non-commerce domain and awards no
  spurious commerce credit.

**Canonical pair (regression signal).** drift-flight.org **46.1 F** / driftflight.com
**85.5 B**, delta **+39.4** — LIVE on v0.7 at 15:43Z, IDENTICAL to the v0.6 delta and every
prior fire (loop-start behavioral +40.6, within static variance). The commerce-manifest
tightening is monotone non-increasing by construction (new credit-set ⊆ old) and pinned by
`tests/test_protocols.py` (`test_canonical_org_unchanged`); the ONLY domains that can lose
credit are those relying on the removed bare-200 false positive, so a valid-manifest domain
keeps its credit. Delta confirmed unmoved LIVE, not just by construction.

**Runner health — STILL DOWN (>11h).** Newest `verify_*.json` is verify_20260723T040757Z
(04:07Z, rubric 0.5), ~11.6h old at this fire — well past the 6h threshold; no :41
artifact since 04:00Z. This fire (15:43Z) is BEFORE 16:00 UTC → folds into the next
post-16:00 Slack daily digest per comms policy (down-runner flag + v0.7 delta trend).

**Ship.** Direct to main — this cycle is a live verification + loop bookkeeping
(LOG/STATE/BACKLOG), no scoring-semantics change (scoring source byte-for-byte untouched;
rubric stays v0.7). No Slack DM (nothing sensitive opened/merged this fire; before 16:00
UTC so no digest yet).

**Next hypothesis.** With PR #3's merge independently verified, the next TRUTH/COVERAGE
leverage is the score-INCREASING half of the commerce rail (live ACP `checkout_sessions`
$0 elicitation + broader well-known path coverage, needs 2+ live real domains) and the
still-open second `cross_task_spread` datapoint (structural cross-intent claim). Both are
`[LOCAL]` P0/P1. The down runner remains the top operational risk — a manual local fire is
the only live canonical signal until launchd `:41` is restarted. Also: cloud Cycle 15's
`save_fixture` infra means the very next `[LOCAL]` win is capturing the canonical-pair
fixtures (`fixtures/canonical/`) so this live re-score becomes a permanent in-cloud replay
guard instead of a per-fire manual run.

## Cycle 16 — 2026-07-23T16:11Z — READOUT (direct to main)

**First duty (peer gate) — NOTHING open.** `list_pull_requests(state=open)` empty
(re-confirmed via GitHub MCP). PR #3 already MERGED (72a2e5b, v0.7); its post-merge
verification was fully discharged across Cycle 15 (offline RETAIN) + the 15:43Z local fire
(LIVE re-score, +39.4 on v0.7). No open peer-gated PR to review — first duty discharged.

**Track.** READOUT (rotation: …Cycle 15 TRUTH → Cycle 16 READOUT). Focus pointer in STATE
named READOUT for this cycle. Next cycle takes METHOD.

**What.** Shipped the **methodology page** (`methodology.html`) — the "read the paper" doc
behind the rubric page (long-standing P2 READOUT item). The rubric page shows WHAT is
scored (checks + weights, YAML verbatim); this new page explains the MEASUREMENT SEMANTICS
a critic needs before trusting the number, in ten sections: the capability lens; the five
pillars + weights; pillar/overall aggregation + weight renormalization; **FAIL vs
CANT_TEST** (evidence-of-absence scores 0 in the denominator; absence-of-evidence shrinks
the pillar, excluded from both numerator AND denominator — "never punished for what
couldn't be observed"); **NOT SCORABLE vs an F** (N/A grade when no pillar was observable,
vs a measured worst-storefront F); **attribution honesty** (agent-side hosting-stack
blocks routed to hosted-agent-reachability, site-side 403/CF/CAPTCHA/429/WAF scored as site
evidence); the shopper + trust panels and **refusal semantics** (directed-refusal caps,
warnings only deduct); reproducibility (trials / verdict stability / **quotability**
Citable-vs-Provisional); grade bands + the four caps; the **$0 free-tier probe**; and
versioned comparability + evidence traceability. Implemented as `scorecard.
_write_methodology_page(out_dir)`, published next to every card by `build_scorecard`
alongside `rubric.html`; cross-linked both directions (card footer → methodology + rubric;
rubric page → methodology; methodology → rubric + back-to-card). Weights, caps, and grade
bands are pulled **LIVE from `load_rubric()`** — nothing hardcoded, so the page reflows on
any version bump and can never drift from the scoring it documents.

**Why.** North-star readout clarity + scientific credibility. The single most common way a
benchmark misleads is conflating "tested and absent" (FAIL) with "couldn't observe"
(CANT_TEST), and inventing a 0/F where the honest answer is N/A. ASRS keeps those strictly
separate in code; until now that rigor was invisible to anyone reading a card. This page is
the citable artifact that lets a skeptic verify the measurement is honest — the "read the
paper" surface a go-to benchmark needs.

**Invariants.** Display-only — `asrs/scoring.py`, `rubric/`, and every probe are
byte-for-byte UNTOUCHED this cycle (`git status`: only `asrs/scorecard.py` +
`tests/test_readout.py` modified). No new scored claim, no weight/cap/check/version change
→ NO version bump (rubric stays **v0.7**); canonical delta unchanged BY CONSTRUCTION.
(#2 versioned comparability) the page READS the version, never sets it. (#3 evidence) the
page documents existing semantics; it makes no scored claim of its own. (#5 no rewrites)
append-only. Direct-to-main (readout/docs, no scoring semantics).

**Tests.** `tests/test_readout.py` 12 → **15** (+3): (1) the page is written as
`methodology.html` and documents the credibility-critical distinctions by name (FAIL,
CANT_TEST, NOT SCORABLE, agent-side, site-side, $0, "comparable only", capability);
(2) it tracks the LIVE rubric — the version string, the transactability weight rendered as
a %, and every cap slug all pulled from `load_rubric()`, so a future version bump can't
leave the page stale; (3) `build_scorecard` publishes `methodology.html` next to the card
(and still `rubric.html`), and the card footer links to it. Full suite **82 → 85**, all 11
files green (free-tier 8/8 after `pip install eth-account` in this cloud python — the sole
red before install was the missing optional signer dep, unrelated to this display change).

**Canonical pair (regression signal) — UNCHANGED, by construction.** In-cloud live re-score
network-blocked (both domains NOT SCORABLE in-cloud, unchanged env policy). scoring.py +
rubric v0.7 + probes byte-for-byte unchanged this cycle → delta cannot move. Last LIVE
signal: `.org` 46.1 F / `.com` 85.5 B, delta **+39.4** on v0.7 (local fire 2026-07-23T15:43Z
merge-verify; also every prior fire). The Cycle-15 record/replay infra + the queued [LOCAL]
canonical-fixture capture remain the path to making this an executable in-cloud guard.

**Runner health — STILL DOWN (>12h).** Newest committed `verify_*.json` is
verify_20260723T040757Z (04:07Z, rubric 0.5) — now ~12.1h old at this fire (16:11Z), well
past the 6h threshold; no `:41` artifact since 04:00Z. FLAGGED in this cycle's Slack daily
digest (this is the first cycle after 16:00 UTC).

**Ship.** Direct-to-main (readout/docs + tests; no scoring semantics). Slack DM SENT — this
is the first cycle after 16:00 UTC, so the daily digest is due (cycles run, shipped items,
canonical delta trend, top open question) AND it carries the mandated runner-down flag +
the queued [LOCAL] v0.7 live re-score note. No CI configured in the repo.

**Next hypothesis.** METHOD next cycle. Highest-leverage cloud-doable items: the P1
`--record-fixture` CLI hook (wires `FetchContext.save_fixture` into the score path so the
[LOCAL] canonical-fixture capture becomes a one-liner — the last cloud-side step before the
in-cloud canonical replay guard the playbook's re-score rule needs). A future READOUT could
add a short prose intro block to the top of the methodology page's rendered form, or link
each card check row to its evidence blob (the P2 evidence-links item) — but the [LOCAL]
canonical fixture + runner restart remain the top operational priorities.

## Local cycle — 2026-07-23T16:46Z — TRUTH

**What.** Captured the canonical-pair replay fixtures (the top P0 `[LOCAL]`) — the missing
input for the in-cloud canonical regression guard. Wired a dormant `--record-fixture <path>`
hook into `asrs.cli score` (this ALSO discharges the P1 "`--record-fixture` CLI hook" item),
then did ONE live static crawl of each canonical domain, dumping its per-`(method,url,ua)`
fetch cache to a committed fixture via the Cycle-15 `FetchContext.save_fixture`.

**Why.** The playbook's per-cycle LIVE canonical re-score cannot run in-cloud (network policy
denies CONNECT to the canonical hosts). Cycle 15 built `FetchContext` record/replay as the
offline proxy but had no recorded canonical responses to replay. This fire — the networked
half — supplies them: a cloud cycle can now `from_fixture` + `_run_probes` + `scoring.score`
and reproduce 46.1 / 85.5 / +39.4 with NO network, replacing the per-cycle "delta unchanged
by construction" prose with an executable guard.

**Scope.** `asrs/cli.py` (+1 dormant flag on `score`, +1 post-scoring `save_fixture` call in
`_evaluate` guarded by `getattr(args, "record_fixture", None)`),
`fixtures/canonical/{drift-flight.org,driftflight.com}.json` (new, committed — NOT gitignored).
No edits to `scoring.py` / `rubric/` / probes.

**Evidence.**
- Fixtures: `fixtures/canonical/drift-flight.org.json` (37 entries), `.../driftflight.com.json`
  (48 entries). Recorded HTTP RESPONSES only — the auth-looking strings are the storefronts'
  OWN public homepage API-doc examples (`Authorization: Bearer df_live_4kq2...`, a truncated
  placeholder) and the x402 `402` `www-authenticate: Payment id=… realm=agents.driftflight.com`
  challenge header any client receives — i.e. the legibility/protocol evidence itself, not
  secrets (scrubbing them would break score reproduction).
- Live crawl (this fire, both HTTP 200): `.org` 46.1 F, `.com` 85.5 B on **rubric v0.7**.
- OFFLINE replay validation (`FetchContext.from_fixture` → `_run_probes` → `scoring.score`,
  never touches the network): reproduces overall **46.1 F / 85.5 B**, delta **+39.4** EXACTLY,
  pillars identical (access 100/100, legibility 36.36/90.91, transactability 18.75/87.5,
  trust 60/60, outcome None/None), and **0 replay-miss on both** — every probe request was
  recorded, so the fixtures are complete, not partial.
- Full suite **85/85** (11 files) green after the change; dormant path confirmed (a `score`
  run WITHOUT the flag writes no fixture; the hook runs strictly AFTER `scoring.score()` → it
  cannot move a score).

**Canonical pair (regression signal).** 46.1 F / 85.5 B, delta **+39.4** on v0.7 — UNCHANGED,
now BOTH measured LIVE this fire AND pinned as a committed offline fixture that reproduces it
byte-faithfully. Scoring path byte-for-byte unchanged (additive dormant CLI hook) → the delta
cannot move by construction either.

**Ship.** Direct-to-main (additive dormant CLI hook + committed public-response fixtures; no
scoring semantics, rubric stays v0.7). No Slack DM — not a sensitive-class change and it does
not move any score; the daily digest was already sent by Cycle 16 (first cycle after 16:00
UTC). Runner STILL DOWN (>12h; newest `verify_20260723T040757Z`) — already flagged in Cycle
16's digest; folds into the next digest if still down.

**Next hypothesis.** One cloud step remains to make this permanent: wire
`tests/test_canonical_replay.py` (replay each committed fixture through the CURRENT pipeline,
assert 46.1 F / 85.5 B / +39.4 on v0.7). That converts these fixtures into a CI-style
regression guard the playbook's "re-score every shipping cycle" rule needs in cloud-adapted
form. Queued P0.

## Cycle 17 — 2026-07-23T17:15Z — METHOD (direct to main)

**Track.** METHOD (rotation: Cycle 16 READOUT → this cycle METHOD; next COVERAGE).

**First duty.** No open peer-gated PR (`list_pull_requests state=open` → `[]`; STATE
already showed NONE). Nothing to adversarially review/merge → proceeded to work.

**What.** Wired `tests/test_canonical_replay.py` (3 tests, +3 → suite 85→88) — the last
step turning the [LOCAL]-captured canonical fixtures into a PERMANENT in-cloud regression
guard. For each committed `fixtures/canonical/{drift-flight.org,driftflight.com}.json`:
`FetchContext.from_fixture(path)` → `asrs.cli._run_probes(ctx)` → `scoring.score(checks,
load_rubric(None), domain)`, then asserts overall_score (46.1 / 85.5), grade (F / B),
`rubric_version == "0.7"`, `scored is True`, all five pillar_scores (finer than the roll-up
— a probe change could move a pillar while leaving the rounded overall equal), the capability
DELTA (+39.4), AND that no cache entry carries a `replay-miss` error (proves the fixture still
covers every probe request — a miss = a probe changed WHAT it fetches, must fail loudly).

**Why.** The playbook's per-cycle rule is to LIVE-re-score the canonical pair every shipping
cycle as a regression signal. The cloud loop has no outbound network (STATE env constraint),
so that re-score has been argued "by construction + prose" in-cloud for 16 cycles. Cycle 15
built record/replay; the 16:46Z local fire captured the fixtures; this cycle makes the
re-score EXECUTABLE — the cloud-adapted form of "re-score every shipping cycle". Any future
scoring/probe change that would move the canonical score now trips a test instead of shipping
silently. The docstring pins the maintenance contract: when a version bump LEGITIMATELY moves
the score, re-capture the fixtures [LOCAL] and update the EXPECTED numbers in the SAME PR — the
guard tracks intended change, it does not forbid it.

**Scope.** `tests/test_canonical_replay.py` (new, 1 file). No edits to `asrs/` — scoring path
byte-for-byte untouched.

**Evidence.**
- New test green: `python3 tests/test_canonical_replay.py` → 3/3 (both domains + delta).
- Full suite **88/88** (12 files, 0 failing). Note: `test_free_tier.py` needs the optional
  `eth-account` dependency (ephemeral $0-signer path); absent by default in this fresh cloud
  checkout → `pip install eth-account` (pypi reachable) makes it 8/8. That failure was a
  MISSING-DEPENDENCY environment gap (invariant #4: agent-side env failure, never scored as
  evidence), pre-existing and unrelated to this tests-only change.

**Canonical pair (regression signal).** 46.1 F / 85.5 B, delta **+39.4** on rubric v0.7,
0 replay-miss on either domain — UNCHANGED, and now pinned as an EXECUTABLE offline re-score
that runs every cloud cycle (no longer prose). Scoring path untouched → delta cannot move by
construction; the new test is the tripwire if that construction is ever violated.

**Ship.** Direct-to-main (tests-only, no scoring semantics, rubric stays v0.7). No Slack DM —
not a sensitive-class change, moves no score; the daily digest was already sent by Cycle 16
(first cycle after 16:00 UTC), and 17:15Z is not a new digest window.

**Runner health.** Newest verify artifact still `verify_20260723T040757Z` (04:07Z, rubric
0.5) — now ~13.1h old, well past 6h. STILL DOWN; already flagged in Cycle 16's digest. Folds
into the next post-16:00-UTC digest if still down. (The canonical replay guard shipped this
cycle is the durable mitigation — the in-cloud canonical re-score no longer depends on the
launchd runner being up at all.)

**Next hypothesis.** COVERAGE next cycle. The replay guard is now permanent; the remaining
canonical-re-score fragility is entirely operational (runner restart), not code. A natural
METHOD follow-up (future): extend the same fixture-replay pattern to a THIRD control domain
(e.g. example.com, already spot-checked 22.5 F [LOCAL]) so the guard pins a NON-storefront
baseline too, not just the canonical pair — but capture is [LOCAL]. For COVERAGE, the live
ACP `checkout_sessions` $0 elicitation parity (P1) remains the highest-leverage rail item,
though its score-increasing half needs [LOCAL] live verification.

## Cycle 18 — 2026-07-23T18:18Z — COVERAGE (direct to main)

**What.** Storefront-TYPE specialization signal for the task battery. New
`BatterySummary.between_kind_spread` (`asrs/battery.py` `_between_kind_spread`):
the population stddev of the per-kind `mean_completion` values across archetypes
with signal. It decomposes the battery-wide `cross_task_spread` — which conflated
two different variance sources — into its two named halves: WITHIN-type noise
(the existing `per_kind[].cross_task_spread`, "does the site vary across intents
of the SAME kind" = reliability) and BETWEEN-type specialization (this, "does
readiness DEPEND on which storefront type the agent was sent to buy"). Terminal
readout gains a `between-archetype spread X.XX — <verdict>` line (uniform
generalist <0.15 / somewhat type-dependent <0.35 / type-specialized) rendered
only when ≥2 archetypes produced signal; JSON carries it via `asdict`.

**Why (north star).** The benchmark's storefront-type flexibility axis. A site
that is uniformly strong on digital metered services and uniformly weak on
physical goods shows a HIGH battery-wide spread that reads as "unreliable" when
it is actually "type-specialized" — a real, citable property an overall number
hides. Separating between-type from within-type variance lets a reader ask "is
this a generalist or a specialist storefront?", which is exactly the question a
population of many storefront types will need answered. Renders correctly on a
synthetic 3-archetype site (digital 100% / data_job 40% / physical 0%):
within-kind spreads all 0.00, between-archetype spread **0.41** → "type-
specialized", vs the battery-wide 0.47 that alone couldn't attribute the cause.

**Attribution honesty (invariant #4).** `between_kind_spread` is None when fewer
than 2 archetypes have signal — with a single storefront type observed,
between-type variance is not a measurable property, so None (unobservable) rather
than a 0.0 that would read as "measured uniform across types". Deliberately
different from the within-checkpoint convention (single task → defined 0.0),
documented in code and pinned by test.

**Invariant discipline.** Diagnostic-only: the battery adds no check/weight/cap
and never feeds the overall score (it aggregates already-collected `BehavioralRun`
records). `asrs/scoring.py` + `rubric/` byte-for-byte untouched → rubric stays
**v0.7**, NO version bump, canonical delta unchanged BY CONSTRUCTION. Direct to
main (new diagnostic field + math + report line + tests; no scoring semantics, no
payment/signing code). Pure stdlib aggregation, unit-tested with synthetic runs —
the established `test_battery.py` pattern; invariant #3's "new PROBES verified
live on 2 real domains" governs fetching probes, not a pure aggregation (same as
`cross_task_spread`/`per_kind` shipped Cycles 2/10 without live domains).

**Scope.** `asrs/battery.py` (field + `_between_kind_spread` helper + wire into
`aggregate_battery`), `asrs/report.py` (`_battery_lines` +1 conditional line),
`tests/test_battery.py` (+1 test, +assertions in 2 existing tests).

**Evidence.**
- `python tests/test_battery.py` 8/8 → **9/9** (`test_between_kind_spread` pins:
  per-kind 1.0/0.4/0.0 → pstdev 0.411; single signal archetype → None; no signal
  → None; survives `to_dict()`).
- Full suite **88 → 89** (12 files, 0 failing). `test_free_tier.py` 8/8 with
  `eth-account` installed (the pre-existing optional-dependency env gap; 7/8 in a
  bare checkout — invariant #4, not a code regression).
- Terminal render verified: the new line appears after `by archetype:` and before
  `cross-task spread`, suppressed when <2 archetypes have signal.

**Canonical pair (regression signal).** In-cloud replay guard
(`tests/test_canonical_replay.py`, the Cycle-17 executable re-score):
drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4** on
rubric v0.7, 0 replay-miss on either domain — UNCHANGED, measured (not just
argued): the scoring path is byte-for-byte untouched so the delta cannot move,
and the guard confirms it.

**Ship.** Direct-to-main. No Slack DM — diagnostic-only, moves no score, adds no
capability check; the daily digest was already sent by Cycle 16 (first cycle
after 16:00 UTC) and this fire is not a new digest window.

**Runner health.** Newest verify artifact still `verify_20260723T040757Z` (04:07Z,
rubric 0.5) — now ~13h+ old, STILL DOWN; already flagged in Cycle 16's digest,
and the Cycle-17 replay guard means the in-cloud canonical signal no longer
depends on it. Folds into the next post-16:00-UTC digest if still down.

**Next hypothesis.** TRUTH next cycle (rotation METHOD→COVERAGE→**TRUTH**→READOUT).
The between-archetype spread is a construct that wants live multi-kind data to
mean anything — its first real number needs the [LOCAL] second cross_task_spread
datapoint (P0), which will be the first live report to carry per_kind AND now
between_kind_spread. A cloud-doable TRUTH follow-up: add a THIRD control-domain
replay fixture case (example.com, 22.5 F) to the canonical guard once the fixture
is captured [LOCAL], widening the offline regression signal to a low-capability
baseline. The HTML battery card should surface between_kind_spread as a pill —
queued P2 (same terminal→JSON→HTML deferral per_kind took Cycle 10→12).

## Local verification — 20260723T184927Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T184927Z.json

## Cycle 19 — 2026-07-23T19:12Z — TRUTH (direct to main)

**What.** Made the canonical replay guard defend the delta IN CAPABILITY TERMS,
not just as a number. `tests/test_canonical_replay.py` gains a 4th test,
`test_canonical_delta_is_agent_native_payment`: it replays both committed
fixtures through the real probe+scoring pipeline (no network) and asserts the
CAPABILITY FACTS that produce the +39.4 — the with-rails fixture
(driftflight.com) delivers agent-native programmatic payment (`x402_probe` PASS,
`self_serve_payg` evidence `x402_live=True`); the no-rails fixture
(drift-flight.org) does not (`x402_probe` not-PASS, `x402_live=False`); and the
capability gap manifests as a transactability pillar gap of exactly 68.75.

**Why (TRUTH).** The playbook's capability lens requires every shipping cycle's
canonical re-score to explain the delta "in capability terms — or the change
does not ship." Until now that explanation lived only as prose in each LOG
entry; the executable guard (Cycle 17) pinned the aggregate numbers
(overall/grade/pillars/delta) but was silent on WHICH capability produced them.
Those two facts can drift apart: a probe change that flips which capability
fires while arithmetic happens to preserve a rounded pillar total would pass the
number-only guards yet break the honest story. This closes that gap — the
"with-rails wins because it can pay programmatically" claim is now a tripwire,
not an assertion of good faith. Agent-native payment is the single largest
driver of the delta: transactability (weight 0.30, the heaviest observed pillar
with `outcome` unobservable on both) contributes ~25.8 of the 39.4 weighted
points (~65%; legibility carries the rest). Worded by capability throughout —
the test asks "is agent-native payment present?", never "is this domain X?".

**Invariant discipline.** Tests-only. `asrs/scoring.py`, `rubric/`, and every
probe are byte-for-byte untouched — the new test only READS the scored report's
`.checks`/`.pillar_scores`. No check add/remove, no weight/cap change, no
version bump → rubric stays **v0.7**, canonical delta unchanged BY CONSTRUCTION
and re-measured green. No payment/signing code (the test asserts ABSENCE of a
nonzero path is irrelevant here — it reads recorded fixture responses only).
Direct to main (tests + docstring; no scoring semantics).

**Evidence.**
- `python tests/test_canonical_replay.py` 3/3 → **4/4** (new capability test
  green: `.com` x402 PASS + x402_live=True; `.org` x402 not-PASS + x402_live=False;
  transactability gap 68.75).
- Full suite **89 → 90** (12 files, 0 failing): attribution 9, battery 9,
  battery_wiring 4, canonical_replay 4, fetch_replay 3, free_tier 8 (eth-account
  installed), protocols 7, quotability 8, readout 15, reliability 8, scoring 11,
  trial_stability_v06 4.

**Canonical pair (regression signal).** In-cloud replay guard, rubric v0.7:
drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4**, 0
replay-miss on either — UNCHANGED and re-measured (scoring path byte-for-byte
untouched). Independently corroborated by the freshly-recovered local runner:
`runs/local/verify_20260723T184927Z.json` (18:49Z) reads 46.1 F / 85.5 B / +39.4.

**Infra health (self-healing check, ran first).** Runner RECOVERED: the
15-hour floor outage (`__file__`-derived repo path in the pinned runner) was
fixed on main (commit 5f4e4c0, `loop: fix verify-floor path bug + self-healing
law`) and the runner is heartbeating again — newest artifact
`verify_20260723T184927Z.json` is ~23 min old at fire time (was >14h stale
through Cycle 18), well under the 6h threshold. No repair needed this fire. No
open peer-gated PR (`list_pull_requests state=open` → []). Was in detached HEAD
on checkout; reset to `main` and fast-forwarded 43 commits before working.

**Ship.** Direct-to-main. No Slack DM — tests-only, moves no score, adds no
capability check; the daily digest was already sent Cycle 16 and this fire
(19:12Z) is not a new digest window. (The runner-recovery is good news but not a
human-gate/notable-ship/digest trigger — it self-healed on main, already logged
there.)

**Next hypothesis.** READOUT next cycle (rotation
METHOD→COVERAGE→TRUTH→**READOUT**). Cloud-doable READOUT candidate: the
`between_kind_spread` HTML pill (Cycle-18 follow-up, P2) — surface the
storefront-type specialization signal on the scorecard battery card, same
terminal→JSON→HTML deferral `per_kind` took. The capability-guard pattern shipped
here also wants a THIRD control-domain case (example.com, 22.5 F) once that
fixture is captured [LOCAL] — it would pin that a LOW-capability baseline earns
NO agent-native payment credit, guarding against a probe that spuriously inflates
a bare site.
