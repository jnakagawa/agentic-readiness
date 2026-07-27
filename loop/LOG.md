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

## Cycle 20 — 2026-07-23T20:12Z — READOUT (direct to main)

**What.** Surfaced the storefront-TYPE specialization signal
(`between_kind_spread`, shipped terminal + JSON in Cycle 18) on the HTML
scorecard's Task-battery card. `asrs/scorecard.py`: a new `_battery_between_band`
helper (bands `Generalist` <0.15 / `Somewhat type-dependent` <0.35 /
`Type-specialized` ≥0.35, css good/warn/bad) drives a second header pill next to
the cross-task-spread pill, plus a one-line interpretation appended to the
by-archetype sub-block ("Between-archetype spread X.XX — how much of the variance
is storefront-TYPE specialization vs within-type noise. This site is …"). Both
render ONLY when `between_kind_spread` is non-None — i.e. ≥2 archetypes produced
signal — so the honest-None (unobservable-with-one-type) case shows no pill,
mirroring the aggregation and the terminal readout exactly.

**Why (READOUT).** This was the exact cloud-doable candidate Cycle 19's
"next hypothesis" named. Cycle 18 added the between-type decomposition — the
north-star many-storefront-types axis — but it lived only on the terminal card
and in JSON; a reader looking at the hosted HTML scorecard couldn't see whether a
site is a generalist or type-specialized. This closes the last terminal→JSON→HTML
gap for the battery diagnostics, following the same deferral `per_kind` took
(Cycle 10 terminal → Cycle 12 HTML). Thresholds and wording are copied from the
terminal `report._battery_lines` between-archetype line so the two readouts can
never disagree on the verdict.

**Invariant discipline.** Display-only. `asrs/scoring.py`, `rubric/`, every
probe, and `asrs/battery.py` (the aggregation) are byte-for-byte untouched — this
only READS the additive `battery_summary` dict and renders it. No check
add/remove, no weight/cap change, no version bump → rubric stays **v0.7**,
canonical delta unchanged BY CONSTRUCTION and re-measured green. No
payment/signing code. Diff is 2 files (`scorecard.py` render + `test_readout.py`),
+93/-3. Direct to main (readout/display, no scoring semantics).

**Evidence.**
- `python tests/test_readout.py` 15/15 → **16/16** (new `test_html_battery_between_kind_pill`:
  value + band label driven off the aggregation, not hand-typed; band thresholds
  pinned to the terminal's; `test_html_battery_single_kind_no_rollup` extended to
  assert NO between pill when the spread is honest-None).
- Full suite **90 → 91** (12 files, 0 failing): attribution 9, battery 9,
  battery_wiring 4, canonical_replay 4, fetch_replay 3, free_tier 8 (eth-account
  installed), protocols 7, quotability 8, readout **16**, reliability 8, scoring 11,
  trial_stability_v06 4.

**Canonical pair (regression signal).** In-cloud replay guard, rubric v0.7:
drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4**, 0
replay-miss on either — UNCHANGED and re-measured (scoring path byte-for-byte
untouched; the change is render-only). Corroborated by the local runner's newest
artifact `runs/local/verify_20260723T194101Z.json` (19:41Z) = 46.1 F / 85.5 B /
+39.4.

**Infra health (self-healing check, ran first).** Runner HEALTHY: newest
artifact `verify_20260723T194101Z.json` (19:41Z) is ~31 min old at fire time,
well under the 6h threshold — the runner recovered Cycle 19 and is still
heartbeating. No repair needed. No open peer-gated PR
(`list_pull_requests state=open` → []) → first-duty review has nothing pending.
Was in detached HEAD on checkout; reset to `main` and fast-forwarded before
working. Installed `eth-account` (pre-existing env gap, invariant #4) → free_tier
8/8.

**Ship.** Direct-to-main. No Slack DM — display-only, moves no score, adds no
capability check; the daily digest was already sent Cycle 16 and this fire
(20:12Z) is not a new digest window.

**Next hypothesis.** METHOD next cycle (rotation
METHOD→COVERAGE→TRUTH→READOUT; this was READOUT → next is **METHOD**).
Cloud-doable METHOD candidate: the "Adversarial referee pass" (P1) — a recurring
self-audit that re-reads the shipped checks asking "would a critic call this
vendor-rigged?", strengthening wording/evidence without losing capability
substance; tests-only or docs, direct-to-main. The between-type pill now wants
live multi-kind data to be eyeballed — folded into the [LOCAL] second
cross_task_spread datapoint (P0), the first live report to carry the field on a
real card.

## Local verification — 20260723T194101Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T194101Z.json

## Local verification — 20260723T204104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T204104Z.json

## Cycle 21 — 2026-07-23T21:13Z — METHOD (direct to main)

**What.** Made the VENDOR-NEUTRALITY invariant executable for the first time —
"checks worded by capability, never by vendor; no special-casing any domain,
favorable or hostile". Added 3 domain-relabeling INVARIANCE tests to the
canonical-guard family (`tests/test_canonical_replay.py`, 4→7). Each relabels a
committed canonical fixture's host — in the request keys AND every response byte
(URLs, `final_url`, headers, bodies), a whole-fixture string substitution to a
neutral `.test` placeholder of a DIFFERENT length — writes it to a temp file, and
replays it through the REAL `FetchContext.from_fixture → _run_probes →
scoring.score` pipeline (the same path guards 1–3 use). A capability-only scorer
MUST return the identical overall / grade / all five pillars / every check status;
renaming the shop changes nothing. `test_relabel_invariance_org` (46.1 F),
`test_relabel_invariance_com` (85.5 B), and `test_relabeled_delta_still_39_4`
(relabel EACH side to a distinct anonymous host → delta still +39.4, so the delta
is a property of the recorded evidence, not of the two famous names).

**Why (METHOD).** This was the METHOD candidate Cycle 20's "next hypothesis"
named — the adversarial-referee "would a critic call this vendor-rigged?" audit,
but converted from prose into a tripwire (the same move Cycle 17 made for "delta
unchanged" and Cycle 19 for "delta in capability terms"). Guards 1–3 pin that the
recorded EVIDENCE produces the canonical numbers; this new guard pins that the
numbers depend ONLY on the evidence, never on the storefront's IDENTITY. It is
the executable proof of the capability lens: the +39.4 delta comes from what
agent-native rails let an agent DO, not from special-casing driftflight.com
favorably or drift-flight.org hostilely. NON-VACUOUS: verified by a negative
control — a monkeypatched favorable special-case (bump `x402_probe`→PASS only when
the literal canonical host is cached) is CAUGHT by the per-check-status assertion
(`x402_probe: PASS→FAIL` base-vs-relabel diff), and note it slipped the numeric
pillar checks in that rig, so the status assertion earns its place beyond the
overall/pillar equalities.

**Invariant discipline.** Tests-only. `asrs/scoring.py`, `rubric/`, every probe,
and `asrs/fetch.py` are byte-for-byte untouched — the relabel is a pure string
substitution over a fixture COPY (temp file, unlinked in `finally`); no committed
fixture is modified (invariant #5, append-only). No check add/remove, no
weight/cap change, no version bump → rubric stays **v0.7**. $0-only intact (no
network, no payment path). Diff is 1 file (`test_canonical_replay.py`).

**Tests.** Full suite green, 12/12 files: attribution 9, battery 9,
battery_wiring 4, **canonical_replay 7** (was 4, +3 relabel-invariance),
fetch_replay 3, free_tier 8 (eth-account installed), protocols 7, quotability 8,
readout 16, reliability 8, scoring 11, trial_stability_v06 4. Suite **91 → 94**.

**Canonical pair (regression signal).** In-cloud replay guard, rubric v0.7:
drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4**, 0
replay-miss on either — UNCHANGED and re-measured (scoring path byte-for-byte
untouched; the change is test-only). Corroborated by the local runner's newest
artifact `runs/local/verify_20260723T204104Z.json` (20:41Z) = 46.1 F / 85.5 B /
+39.4. NEW this cycle: the delta is now also pinned as IDENTITY-INVARIANT — two
anonymized storefronts with the same recorded capabilities reproduce +39.4.

**Infra health (self-healing check, ran first).** Runner HEALTHY: newest
artifact `verify_20260723T204104Z.json` (20:41Z) is ~32 min old at fire time,
well under the 6h threshold — still heartbeating since the Cycle-19 recovery. No
repair needed. No open peer-gated PR (`list_pull_requests state=open` → []) →
first-duty review has nothing pending. Was in detached HEAD on checkout; reset to
`main` and fast-forwarded before working. Installed `eth-account` (pre-existing
env gap, invariant #4) → free_tier 8/8.

**Ship.** Direct-to-main. No Slack DM — tests-only, moves no score, adds no
capability check; the daily digest was already sent Cycle 16 and this fire
(21:13Z) is not a new digest window.

**Next hypothesis.** COVERAGE next cycle (rotation
METHOD→COVERAGE→TRUTH→READOUT; this was METHOD → next is **COVERAGE**). The
identity-invariance guard now covers only the canonical PAIR; a cloud-doable
COVERAGE candidate is extending the replay-guard family to a THIRD control domain
once its fixture is captured [LOCAL] (example.com, P2) — or the cloud half of the
"live handshakes for other rails" item (ACP `checkout_sessions` elicitation
parsing) that doesn't require live network. The between-type pill still wants live
multi-kind data — folded into the [LOCAL] second cross_task_spread datapoint (P0).

## Local verification — 20260723T214103Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T214103Z.json

## Cycle 22 — 2026-07-23T22:12Z — COVERAGE (direct to main)

**What.** Broadened free-tier opt-in DISCOVERY to a second convention: a URL
**query parameter** (e.g. `?tier=free` / `?mode=free` / `?free=true`), alongside
the request header the probe already recognized. Added `_scan_query_param_instruction(text)`
(mirrors `_scan_header_instruction`: a `[?&]name=value` token, gated on nearby
free-allowance language, skipping a plumbing-param denylist — `api_key`, `page`,
`token`, `signature`, …; requires an explicit "free" hint in the name or value so
`?plan=pro` / `?tier=starter` near free prose are never mistaken for an opt-in),
a new additive `FreeTierDiscovery.opt_in_query: tuple[str,str] | None` field, and
an `opt_in_query` evidence key. `discover_free_tier` now populates it.
`tests/test_free_tier.py` +1 test (`test_query_param_optin_discovery`, 8→9):
extraction (name-hint / value-hint), four negative controls (non-free value,
plumbing param, denylisted `api_key`, non-free name near free prose), evidence
surfacing, and the load-bearing SCORE-NEUTRALITY assertions.

**Why (COVERAGE).** Real agent-native storefronts advertise the free tier by
query param, not only by header; such a site currently discovers as
"opt-in-undiscoverable" (a soft site-defect nudge) even though it DID document a
machine-usable opt-in — a false negative in measurement coverage, on the
north-star "many conventions / many rails" axis. This cycle lands the DISCOVERY
+ evidence-recording half in-cloud (recognizing and reporting the convention);
acting on it (the live free-mode call + folding it into `advertised`) is
score-INCREASING and must be verified live on ≥2 real domains per invariant #3 —
queued `[LOCAL]`.

**Invariants / ship class.** DELIBERATELY SCORE-NEUTRAL by construction: the new
field is recorded but is NOT part of the `advertised` gate and is NOT consumed by
the live-call path, so no behavioral outcome can move on its account. Pinned by
test — a query-param opt-in with no header and no manifest units keeps
`advertised=False`, and adding a `?tier=free` line to the header-based fixture
leaves `advertised` identical. NOT signing/payment code: the diff is confined to
the discovery region (constants + `FreeTierDiscovery` + `discover_free_tier` +
the new scanner); `parse_challenge`, the settle/sign path, amount handling, and
the nonzero-refusal safety property are byte-for-byte untouched (sentinel grep:
no added line touches any sign/settle/amount/authorize symbol; the only "sign"
hits are the word "signal", the denylisted param name "signature", and a
docstring). No scoring semantics, no version bump → rubric stays **v0.7**;
additive discovery capability that doesn't change scoring → direct-to-main tier.
$0-only intact (no network, no payment path exercised). Diff is 2 files.

**Tests.** Full suite green, 12/12 files: attribution 9, battery 9,
battery_wiring 4, canonical_replay 7, fetch_replay 3, **free_tier 9** (was 8,
+query-param discovery; eth-account installed), protocols 7, quotability 8,
readout 16, reliability 8, scoring 11, trial_stability_v06 4. Suite **94 → 95**.

**Canonical pair (regression signal).** In-cloud replay guard (`test_canonical_replay.py`
7/7), rubric v0.7: drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta
**+39.4**, 0 replay-miss on either — UNCHANGED and re-measured. The change is
behavioral (outcome pillar); static canonical mode has `outcome=null`, so the
static score cannot move by construction, and the replay guard confirms it
byte-for-byte. Corroborated by the local runner's newest artifact
`runs/local/verify_20260723T214103Z.json` (21:41Z) = 46.1 F / 85.5 B / +39.4.

**Infra health (self-healing check, ran first).** Runner HEALTHY: newest artifact
`verify_20260723T214103Z.json` (21:41Z) is ~30 min old at fire time, well under
the 6h threshold — still heartbeating since the Cycle-19 recovery. No repair
needed. No open peer-gated PR (`list_pull_requests state=open` → []) → first-duty
review had nothing pending. Installed `eth-account` (pre-existing env gap,
invariant #4) → free_tier 9/9.

**Ship.** Direct-to-main. No Slack DM — score-neutral additive discovery, moves no
score, not a sensitive class; the daily digest was already sent Cycle 16 and this
fire (22:12Z) is not a new digest window.

**Next hypothesis.** TRUTH next cycle (rotation METHOD→COVERAGE→TRUTH→READOUT;
this was COVERAGE → next is **TRUTH**). Cloud-doable TRUTH candidates: extend the
canonical replay guard to a third control domain once its fixture is captured
[LOCAL] (example.com, P2); or a fresh-context re-read of check WORDING for
vendor-leaning phrasing (the recurring adversarial-referee prose pass — the
Cycle-21 invariance guard proves the SCORING is neutral, not that the
DESCRIPTIONS read neutrally). The query-param opt-in's live wiring + 2-domain
verification is queued [LOCAL] (P1, under the free-tier generalization item).

## Local verification — 20260723T224105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T224105Z.json

## Cycle 23 — 2026-07-23T23:14Z — TRUTH

**What/why.** The canonical delta is now defended as EARNED, not an attribution
artifact — invariant #4 (attribution honesty) made executable ON the +39.4.
`tests/test_canonical_replay.py` +1 test (`test_canonical_delta_is_earned_dominance`,
7→8). A delta can be inflated two dishonest ways that leave the headline numbers
looking fine: (i) DIFFERENTIAL OBSERVABILITY — the two sides scored over different
check sets, or (ii) MIS-ATTRIBUTED ABSENCE — a genuinely-missing capability
recorded as CANT_TEST (absence-of-evidence, EXCLUDED from the denominator) on one
side but FAIL (evidence-of-absence, scored 0 IN the denominator) on the other.
The new guard replays both committed fixtures through the REAL
`from_fixture → _run_probes → scoring.score` path and pins three facts from the
recorded evidence: (a) FULL OBSERVABILITY — no static check on EITHER canonical
domain is CANT_TEST or NA (clean HTTP-200 crawls), so every recorded FAIL is
genuine evidence-of-absence in the denominator, nothing excused as un-observable;
(b) LIKE-FOR-LIKE DENOMINATOR — both domains scored over the IDENTICAL check_id
set, so +39.4 compares the same checks on both sides; (c) CHECK-BY-CHECK
DOMINANCE, NO INVERSION — at every matched check the with-rails capability rank
(PASS>PARTIAL>FAIL) is ≥ the no-rails rank, strictly greater at ≥1 check. Result:
the with-rails side is a capability SUPERSET at matched, fully-observed checks
(strict wins: llms_txt, offer_catalog, self_serve_payg, x402_probe) — the delta is
not a single pillar masking a regression, not a rounding tie, not a scoring-
denominator asymmetry. Worded by capability throughout ("was this observed, which
side ranks higher?"), never by vendor. Complements the Cycle-19 capability-payment
guard (one pillar) and the Cycle-21 relabel-invariance guard (identity-neutrality)
with a THIRD, distinct axis: attribution-honesty of the delta.

**Non-vacuous (negative controls).** Two committed mis-attributions were verified
to trip the guard: (1) re-labeling the no-rails `x402_probe` FAIL as CANT_TEST
(excusing the missing payment as unobserved) is CAUGHT by (a); (2) inverting one
check so the no-rails side outranks the with-rails side is CAUGHT by (c). Both
slip the aggregate-only number guards but fail here.

**Evidence.** `tests/test_canonical_replay.py` (8/8). Full suite 95 → 96, all
green (`eth-account` installed for free_tier 9/9 — pre-existing env gap,
invariant #4). Tests-only: `git diff --stat` = 1 file, +94 lines;
scoring.py/rubric/probes/fetch.py byte-for-byte untouched.

**Canonical pair.** Re-measured by the replay guard itself this fire, rubric
v0.7: drift-flight.org **46.1 F** / driftflight.com **85.5 B**, delta **+39.4**,
0 replay-miss on either — UNCHANGED by construction (no scoring path touched) AND
executed. Corroborated by the local runner's newest artifact
`runs/local/verify_20260723T224105Z.json` (22:41Z) = 46.1 F / 85.5 B / +39.4.

**Infra health (self-healing check, ran first).** Runner HEALTHY: newest artifact
`verify_20260723T224105Z.json` (22:41Z) is ~31 min old at fire time, well under
the 6h threshold — heartbeating since the Cycle-19 recovery. No repair needed. No
open peer-gated PR (`list_pull_requests state=open` → []) → first-duty review had
nothing pending. Bench UP (96/96), bookkeeping consistent with git history.

**Ship.** Direct-to-main. No Slack DM — tests-only, moves no score, not a
sensitive class; the daily digest was already sent Cycle 16 and this fire
(23:14Z) is not a new digest window.

**Next hypothesis.** READOUT next cycle (rotation METHOD→COVERAGE→TRUTH→READOUT;
this was TRUTH → next is **READOUT**). Cloud-doable READOUT candidates: anchor-link
the card's cap chips to the methodology cap rows (Cycle-16 follow-up, P2); or
surface the earned-dominance / observability property on the methodology page's
FAIL-vs-CANT_TEST section as a worked canonical example. The [LOCAL] items
(third-control-domain fixture, second cross_task_spread datapoint, query-param
live wiring) remain queued for a networked fire.

## Local verification — 20260723T234102Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260723T234102Z.json

## Local cycle — 2026-07-23T23:49Z — COVERAGE/METHOD ([LOCAL] operator directive brick 1: offering relevance discovery)

**First duty.** No open peer-gated PR (`gh pr list --state open` → empty) → the
mandated fresh-context adversarial review had nothing pending. Infra health check
ran first: runner HEALTHY — newest artifact `verify_20260723T234102Z.json`
(23:41Z) is ~8 min old at fire time, well under the 6h threshold, delta +39.4;
bench UP (103/103 after this change), bookkeeping consistent with git history.

**What.** First brick of the **operator directive** (Jonah, 2026-07-23: "the
battery must be OFFERING-RELATIVE, not fixed"). New module `asrs/offering.py`:
`discover_offering(ctx)` reads a storefront's own agent surfaces (homepage +
`/llms.txt` / `/llms-full.txt` / `/manifest.json`, $0 GETs only) and
`classify_offering(domain, surfaces)` (pure) decides which capability ARCHETYPES
the site CLAIMS to serve — from a fixed template bank `metered_api / subscription
/ digital_good / physical_good / service_booking / data_retrieval` — each backed
by QUOTED machine evidence (the matched phrase + which surface it came from).
`OfferingProfile.unclaimed` is the exact NA complement of `claimed`: the
archetypes a later offering-relative battery would mark NA (excluded from
completion means + both spreads, never penalized). This is brick 1 of the
directive's five (relevance discovery); bricks 2 (intent instantiation) + 3
(NA-aware aggregation, the peer-gated part) are queued as the next increments.

**Why.** The current battery judges every site against ONE static intent list, so
an image-generation API gets probed with "order a physical good" and its partial
completion pollutes the completion means and both spread signals — measuring the
battery's MISMATCH, not the site's readiness. Offering discovery is the input that
lets the battery instantiate only the intents a site actually claims to serve.
North-star many-storefront-types axis.

**Precision-first, vendor-neutral.** A FALSE archetype claim would make the
battery run an irrelevant intent (the very pollution we are removing); a MISSED
one only leaves a servable intent untested (conservative). So signals are anchored
and specific. THE load-bearing precision guard: both canonical homepages say "one
visual language for every image you **ship**" / "Teams that **ship** images daily"
— metaphorical "ship" that must NOT read as physical fulfillment. `physical_good`
requires unambiguous fulfillment nouns ("free shipping" / "add to cart" / "in
stock" / SKU / fulfillment), so it does NOT fire on the canonical pair. Every
claim carries the exact quoted evidence so a skeptic can audit it; archetypes are
named by CAPABILITY, never by vendor/domain.

**Live-validated on 4 real domains (invariant #3, this fire has network):**
- drift-flight.org (no-rails, homepage only — llms.txt 404): claimed
  `{metered_api, subscription, digital_good}`, **physical_good NA**.
- driftflight.com (with-rails, homepage + llms.txt): claimed
  `{metered_api, digital_good, subscription}`, **physical_good NA** — the
  operator's acceptance criterion met exactly.
- example.com (null control): claims NOTHING (not a storefront).
- books.toscrape.com (physical-retail inverse control): claims `{physical_good}`
  ONLY (via "In stock" + "Add to basket") — the inverse the directive asked for.
Evidence: `runs/local/offering_discovery_20260723T234942Z.json` (force-added;
`runs/` is gitignored).

**Discovery-only / score-neutral by construction.** Adds NO check, weight, cap, or
aggregation rule; does not feed the overall score or the battery math yet (same
shape as the Cycle-22 free-tier query-param discovery half). `git status` = two
NEW files only (`asrs/offering.py`, `tests/test_offering.py`); ZERO tracked-file
modifications → scoring.py/rubric/probes/battery.py byte-for-byte untouched →
rubric stays **v0.7**, canonical delta unchanged by construction AND re-measured
(replay guard `test_canonical_replay.py` 8/8 = 46.1 F / 85.5 B / +39.4, 0
replay-miss; corroborated by `verify_20260723T234102Z.json`). Direct-to-main.

**Evidence.** `tests/test_offering.py` (7/7, synthetic surfaces, no network):
agent-native storefront claims metered_api/digital_good/subscription and NOT
physical_good (the metaphorical-"ship" precision guard baked into the fixture);
physical retail is the inverse (physical_good only, others NA); service_booking +
data_retrieval each fire on their own language; non-storefront claims nothing;
strength counts DISTINCT signal labels + orders claims; evidence is quoted, HTML
stripped, surface-tagged; strip_html drops script/style/tags. Full suite 96 → 103.

**Ship.** Direct-to-main. No Slack DM — discovery-only, moves no score, not a
sensitive class; the daily digest was already sent Cycle 16 and this fire
(23:49Z) is not a new digest window.

**Next hypothesis.** Brick 2 (intent instantiation): parameterize the fixed
archetype template bank with the discovered offering to generate each site's task
prompts, and map battery `kind` ↔ archetype so the battery consumes the profile.
Brick 3 (NA-aware aggregation: unclaimed archetypes excluded from completion means
+ both spreads) is the scoring-semantics change → PEER-GATED when it lands. The
cloud rotation is unaffected (next cloud cycle still takes READOUT).

## Local verification — 20260723T234942Z (offering-discovery live)

offering brick 1 live-validated | drift-flight.org: {metered_api,subscription,digital_good} physical_good=NA | driftflight.com: {metered_api,digital_good,subscription} physical_good=NA | example.com: {} | books.toscrape.com: {physical_good} | suite 103/103 | canonical 46.1 F / 85.5 B / +39.4 (replay guard, unchanged) | artifact runs/local/offering_discovery_20260723T234942Z.json

## Cycle 24 — 2026-07-24T00:17Z — READOUT (direct to main)

**First duty.** No open peer-gated PR (`list_pull_requests state=open` → `[]`) →
the mandated fresh-context adversarial review had nothing pending. Infra health
check ran first: runner HEALTHY — newest artifact `verify_20260723T234102Z.json`
(23:41Z) is ~31 min old at fire time, well under the 6h threshold; bench UP
(103/103 on a fresh checkout after `pip install -r requirements.txt`; note the
`test_free_tier.py` `eth-account` dependency, invariant-#4 env gap, is now
installed from requirements so the fresh cloud checkout runs 9/9 not 7/8);
bookkeeping consistent with git history (HEAD = local fire 23:49Z, STATE/LOG
match). Canonical replay guard green pre-flight: 46.1 F / 85.5 B / +39.4, 0
replay-miss.

**What/why.** The READOUT complement to Cycle 23's TRUTH work. Cycle 23 made the
"earned-dominance / observability" property an executable guard
(`test_canonical_delta_is_earned_dominance`), but a critic reading the score has
no prose that explains it — the methodology page's section 3 (FAIL vs CANT_TEST)
defines the two states abstractly and stops there. This cycle surfaces the
property in `methodology.html`: a "worked example — when is a low score earned
evidence, not a blind spot?" sub-section under section 3 that names the three facts
which make a delta between two sites trustworthy, in the SAME capability language
as the test: (a) full observability (every check on the lower side actually
observed → each 0 is a tested-and-absent FAIL, not an un-observed check held
against the site), (b) like-for-like denominator (both scored over the identical
check set), (c) check-by-check dominance / no inversion (the higher side ranks ≥
at every shared check, strictly higher on ≥1 → a capability SUPERSET, not a
net-out of wins and losses). Closes the Cycle-23 follow-up ("add a worked
canonical example there"). Moves the north-star READOUT-clarity axis: the number's
credibility argument is now legible to a reader, not just enforced in CI.

**Vendor-neutral by construction.** The worked example describes the reference
pair by CAPABILITY ("two storefronts", "the lower-scoring side") and names no
domain, product, or brand — a test assertion pins that `drift-flight`/`driftflight`
never appear on the page. It also states the property is "pinned by an executable
regression test, enforced every cycle" so the reader knows it is a guarantee, not
a claim.

**Scope / ship.** `asrs/scorecard.py` only (the methodology-page prose + minimal
`h3`/`ul`/`li` styling added to the shared `_PROSE_HEAD` — neither prose page used
those tags before; browser-default otherwise) + `tests/test_readout.py`. `git diff
--name-only` touches NEITHER scoring.py / rubric / probes / fetch.py / protocols.py
/ battery.py (grep clean) → **display-only, no scoring semantics, rubric stays
v0.7**, canonical delta unchanged by construction AND re-measured (replay guard
`test_canonical_replay.py` 8/8 = 46.1 F / 85.5 B / +39.4, 0 replay-miss).
Direct-to-main per the ship rules (readout + tests).

**Evidence.** `tests/test_readout.py` 16 → 17 (+`test_methodology_documents_earned_dominance`:
asserts the worked example names full-observability / like-for-like-denominator /
no-inversion / superset / earned / blind-spot AND that no vendor/domain string
appears). Rendered the page and eyeballed the section-3 region. Full suite 103 → 104.

**Ship / comms.** Direct-to-main. No Slack DM — display-only, moves no score, not
a sensitive class; the daily digest was already sent Cycle 16 and this fire
(00:17Z) is before the next 16:00 UTC digest window.

**Next hypothesis.** READOUT track has more Cycle-16/20/23 follow-ups queued:
anchor-link a card's cap chips to the methodology cap rows (a reader who sees a
"grade capped" alert can jump to why), and evidence-blob links on each check row.
Next cloud cycle takes METHOD.

## Local verification — 20260724T004105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T004105Z.json

## Local cycle — 2026-07-24T00:49Z — COVERAGE ([LOCAL] operator directive brick 2: offering-relative intent instantiation)

**First duty.** No open peer-gated PR (`gh pr list --state open` → empty) → the
mandated fresh-context adversarial review had nothing pending. Infra health check
ran first: runner HEALTHY — newest artifact `verify_20260724T004105Z.json`
(00:41Z) is ~0–8 min old at fire time, well under the 6h threshold; delta +39.4;
bench UP (112/112 after this change); bookkeeping consistent with git history.

**What.** Second brick of the **operator directive** (Jonah, 2026-07-23: "the
battery must be OFFERING-RELATIVE, not fixed"). `asrs/battery.py` gains
`instantiate_battery(profile)` + a FIXED per-archetype intent TEMPLATE bank
(`_ARCHETYPE_INTENTS`, one capability-worded, vendor-neutral intent per archetype
in `offering.ARCHETYPES`). Given a brick-1 `OfferingProfile`, it emits ONE
`BatteryTask` per archetype the site CLAIMS — in fixed template-bank order, `id`
and `kind` both set to the archetype name — and OMITS the archetypes the site
does not claim. So an image API yields the metered/subscription/digital intents
and NO physical-good task; a shop yields the inverse; a site that claims nothing
yields an empty battery. This is the discovery→task-set wiring brick 1 set up.

**Vocabulary reconciliation** (the directive's explicit brick-2 ask): the
canonical task vocabulary is now `offering.ARCHETYPES` (metered_api / subscription
/ digital_good / physical_good / service_booking / data_retrieval). Generated
tasks use archetype names as BOTH `id` and `kind`, so the per-`kind` rollup groups
by archetype and the same archetype id lines up across sites (brick-5
comparability). Hand-authored YAMLs keep their free-form `kind` labels
(digital_service / data_job / …) and still load unchanged — only GENERATED
batteries adopt the archetype vocabulary.

**Parameterized by the discovered offering** (not just selected): the digital_good
intent carries a `{descriptor}` slot filled from the archetype's OWN fired signal
labels/quotes — the operator's literal example, "obtain one **generated image**",
derived from `offering.py`'s vendor-neutral media bank (image/video/audio/art →
"generated <noun>"; translation → "translated document"; else generic "digital
output"). Injection-safe: the descriptor comes from OUR signal labels, never from
arbitrary injected raw site prose. The generated intents never name the site's own
domain (asserted).

**Live-validated on 4 real domains (invariant #3, this fire has network):**
`discover_offering → instantiate_battery`:
- drift-flight.org → tasks `{metered_api, subscription, digital_good}`,
  **NO physical_good task**; digital_good intent = "obtain one generated image …".
- driftflight.com → tasks `{metered_api, subscription, digital_good}`,
  **NO physical_good task** — the operator's acceptance ("driftflight.com shows
  physical_good = NA, not a completion number") met exactly, in task-selection
  terms; digital_good = "obtain one generated image …".
- books.toscrape.com (physical-retail inverse control) → `{physical_good}` task
  ("purchase one unit of the site's primary physical product …").
- example.com (null control) → EMPTY battery (claims nothing → nothing to assess).
All 4 acceptance assertions PASS. Evidence:
`runs/local/offering_battery_instantiate_20260724T004927Z.json` (force-added;
`runs/` is gitignored).

**Score-neutral by construction.** Task SELECTION only — constructs a `Battery`,
does not touch `aggregate_battery`, any check, weight, cap, or the rubric. The
diff is confined to `asrs/battery.py`'s new instantiation section + a new test
file; scoring.py/rubric/probes/fetch.py/protocols.py byte-for-byte untouched →
rubric stays **v0.7**, canonical delta unchanged by construction AND re-measured
(replay guard `test_canonical_replay.py` 8/8 = 46.1 F / 85.5 B / +39.4, 0
replay-miss; corroborated by `verify_20260724T004105Z.json`). Direct-to-main
(same class as brick 1). The NA-aware AGGREGATION (unclaimed archetypes excluded
from means + both spreads) is the scoring-semantics change → brick 3, PEER-GATED.

**Evidence.** `tests/test_battery_instantiate.py` (8/8, synthetic profiles, no
network): image API → metered/subscription/digital tasks + NO physical (operator
acceptance) + "generated image" descriptor; retail is the inverse; empty profile →
empty battery; generated intents vendor-neutral (no domain leak); ids ARE
archetypes in fixed template-bank order (not claim-strength order) →
cross-site comparability; digital_good descriptor branches
(translation/media/fallback/None-safe). Full suite 104 → 112.

**Ship.** Direct-to-main. No Slack DM — score-neutral task selection, moves no
score, not a sensitive class; daily digest already sent Cycle 16 and this fire
(00:49Z) is not a new digest window (before the next 16:00 UTC digest).

**Next hypothesis.** Brick 3 (NA-aware aggregation) is the peer-gated increment:
record unclaimed archetypes as NA in `BatterySummary` and formalize their
exclusion from `mean_completion` / `cross_task_spread` / `between_kind_spread`,
plus the brick-5 comparability readout naming WHICH archetypes were assessed. Then
the `[LOCAL]` acceptance rerun (rerun the canonical batteries end-to-end via the
instantiated task set and confirm driftflight physical_good shows as NA, not a
number). Cloud rotation unaffected (next cloud cycle still takes METHOD).

## Cycle 25 — 2026-07-24T01:12Z — METHOD (peer-gated PR #4)

**First duty.** No open peer-gated PR at fire start (`list_pull_requests
state=open` → `[]`) → the mandated fresh-context adversarial review had nothing
pending. Infra health check ran first: **all green.** Runner HEALTHY — newest
artifact `verify_20260724T004105Z.json` (00:41Z) is ~31 min old at fire (01:12Z),
well under 6h, and its scores block is CLEAN (46.1 F / 85.5 B, tests_ok True) — the
Cycle-13/19 source fix + runner recovery hold. Bench UP: full suite 112/112 on a
fresh checkout after `.venv` + `pip install -r requirements.txt` (eth-account
present → test_free_tier 9/9). Bookkeeping: the ephemeral cloud checkout's local
`main` was a stale divergent lineage ("ahead 22, behind 52"); realigned it to the
authoritative `origin/main` tip (d33129f, Cycle 24 + local fire 00:49Z) via
`git reset --hard FETCH_HEAD` — no un-pushed work on local main (all cycle work is
on the pushed branch), NOT a published-history rewrite. Canonical replay guard green
pre-flight on realigned main: 8/8 (46.1 F / 85.5 B / +39.4, 0 replay-miss).

**What/why (operator directive P0, brick 3 — NA-aware aggregation).** Bricks 1
(offering discovery) and 2 (offering-relative intent instantiation) shipped [LOCAL].
Brick 3 is the METHOD/peer-gated increment: make the battery OFFERING-RELATIVE *at
aggregation time*. An archetype a site does NOT claim to serve (from the brick-1
`OfferingProfile`) is now marked **NA** and EXCLUDED from `mean_completion`,
`cross_task_spread`, and `between_kind_spread`. This is the operator's exact
complaint made a tripwire: an image-generation API probed with "order a physical
good" no longer lets that mismatched partial completion pollute the spreads — the
battery measures readiness for what the site OFFERS, not its mismatch with intents it
never advertised. NA is DISTINCT from "no signal": NA = structural not-offered;
no-signal = an offered intent every run env-blocked (unobserved-but-offered). Both
are excluded, for different reasons, and the readout now names which is which
(comparability requirement #5: `assessed_archetypes` names what the numbers are over,
`na_archetypes` names what was not offered).

**Change.** `asrs/battery.py`: `BatteryTaskResult.na` (structural not-offered; never
counts as signal even if a garden-path run attaches); `BatterySummary` gains
`na_archetypes`, `assessed_archetypes`, `battery_semantics_version="b1"`;
`aggregate_battery(..., *, profile=OfferingProfile|None)` — with a profile, tasks whose
`kind` is `profile.unclaimed` are NA-excluded and per_kind/spreads compute over the
applicable set; **without a profile, byte-for-byte the pre-brick-3 aggregation** (a
profile is the only thing that establishes what a site does not offer). Non-canonical
hand-authored kinds (e.g. `digital_service`) are never NA. `asrs/report.py
_battery_lines` names assessed + not-offered archetypes (offering-relative mode only).

**Versioning decision.** Versions the BATTERY diagnostic semantics
(`battery_semantics_version="b1"`), DELIBERATELY NOT the rubric version. The battery
feeds no overall score, so moving the rubric version (v0.7) would falsely signal the
SCORED number changed and break canonical comparability. Invariant #2's intent
("aggregation-rule change → versioned comparability") is honored on the right artifact.
Flagged in the PR for the reviewing cycle to sanity-check.

**Vendor-neutral / attribution-honest.** NA keys ONLY on archetype-claim structure
from discovery — no domain/vendor/product string (tested: non-canonical kind never NA,
claimed archetypes never NA). NA is never a site failure (`has_signal=False`, no
completion charged) — recorded, not silently dropped.

**Scope / ship.** `asrs/battery.py` + `asrs/report.py` + `tests/test_battery.py` only.
`scoring.py`/`rubric/`/`protocols.py`/`fetch.py`/`offering.py` byte-for-byte untouched
(sentinel `git diff --quiet` clean) → **rubric stays v0.7, canonical delta unchanged by
construction AND re-measured** (replay guard 8/8 = 46.1 F / 85.5 B / +39.4, 0
replay-miss). **Peer-gated** (aggregation-semantics change) → branch
`loop/na-aware-battery-aggregation`, **PR #4** opened with full evidence + reviewer
checklist; NOT self-merged this cycle. No CI configured on the repo (`get_status`
total_count 0). Next cycle's first duty adversarially reviews + merges if it survives.

**Evidence.** `tests/test_battery.py` 9 → 12 (+3): (10) `profile=None` reproduces the
pinned `cross_task_spread=0.1` fixture byte-for-byte and marks nothing NA; (11) the
operator's image-API-vs-physical-good scenario — physical_good NA-excluded, claimed
archetypes keep IDENTICAL numbers, `between_kind_spread` demonstrably changes when the
mismatch is removed (pstdev[0.4,1.0]=0.30 vs pstdev[0.4,1.0,0.2]); (12) NA vs no-signal
vs non-canonical-kind. Full suite 112 → 115. PR: https://github.com/jnakagawa/agentic-readiness/pull/4

**Ship / comms.** Slack DM SENT — sensitive-class (aggregation-semantics) PR opened,
visibility per comms policy so Jonah can veto (not an approval request). Not a digest
window (01:12Z, before 16:00 UTC).

**Next hypothesis.** After brick 3 merges: brick 5 (surface NA/assessed on the HTML
battery card — READOUT), and the [LOCAL] `--battery auto` wiring so a live run uses
`discover_offering → instantiate_battery → aggregate_battery(profile=...)` end-to-end,
then the [LOCAL] acceptance rerun (driftflight physical_good = NA with spreads over
claimed archetypes only; a retail storefront the inverse). Next cloud cycle takes
COVERAGE.

### Merge note — PR #4 MERGED EXTERNALLY 2026-07-24 (merge commit bec1dc0)

PR #4 (Cycle 25 brick 3, NA-aware battery aggregation, sensitive class) was
MERGED EXTERNALLY shortly after opening — an operator merged it directly (merge
message "peer-gate SURVIVED"), the same active-consent pattern as PR #2 (Cycle 9)
and PR #3 (Cycle 14). An external merge is ACTIVE consent (stronger than
veto-silence), so it pre-empts — not bypasses — the mandated next-cycle
fresh-context adversarial review. Per the established pattern the pre-merge review
CONVERTS to a POST-merge retain-or-revert sanity check, now the NEXT cloud cycle's
FIRST duty (before COVERAGE work). This fire (Cycle 25) did NOT run that review
here — that would be a second cycle. Immediate post-merge health check on the
merged tip bec1dc0: bench 115/115 green, canonical replay guard 8/8 (46.1 F /
85.5 B / +39.4, 0 replay-miss) — the battery change is decoupled from scoring as
designed, canonical delta unchanged. Session auto-unsubscribed from PR #4 activity;
not reopening. STATE + BACKLOG reconciled below.

## Cycle 26 — 2026-07-24T02:12Z — COVERAGE (direct to main)

**First duty (peer-gate review + merge).** One open peer-gated PR at fire start:
**PR #4** `loop/na-aware-battery-aggregation` (Cycle 25, METHOD — NA-aware battery
aggregation, brick 3). A different fire from the authoring cycle, so the mandated
fresh-context adversarial review ran and I merged on survival. Re-derived all four
reviewer-checklist items independently: (1) **`profile=None` == pre-brick-3** — by
construction (`na_kinds` empty → every `na=False` → `applicable`==all tasks → per-kind /
spread math unchanged) AND pinned by `test_na_profile_none_is_backward_compatible`
(`cross_task_spread=0.1` on the existing fixture, byte-for-byte). (2) **NA vendor-neutral**
— `na_kinds = set(profile.unclaimed)`; verified `OfferingProfile.unclaimed = [a for a in
ARCHETYPES if a not in served]` is a strict subset of `ARCHETYPES`, so a non-canonical
hand-authored kind (e.g. `digital_service`) can NEVER be NA (pinned by test 12); no
domain/vendor string. (3) **canonical delta unchanged** — diff touches only
`asrs/battery.py` + `asrs/report.py` + `tests/test_battery.py`; `scoring.py`/`rubric/`/
`probes`/`fetch.py` untouched; replay guard `test_canonical_replay.py` 8/8 green
(46.1 F / 85.5 B / +39.4, 0 replay-miss). (4) **versioning** — `battery_semantics_version
= "b1"`, rubric stays v0.7: correct, the battery feeds no overall score so a rubric bump
would falsely signal a scored-number move. **Non-vacuous**: test 11 pins that NA exclusion
ACTUALLY changes `between_kind_spread` (`>1e-6`, pstdev[0.4,1.0] vs pstdev[0.4,1.0,0.2]),
not a no-op. Ran the full suite on the branch: **115/115 green**. Verdict: **SURVIVED →
MERGED** (merge commit `bec1dc0`, standard merge; no CI on repo). Post-merge suite 115/115
on main. No open peer-gated PR remains.

**Bookkeeping reconciliation.** A concurrent local fire (session `018Gu9…`, the PR-#4
authoring session) pushed `5ddb89a loop: reconcile PR #4 external merge` ~5 min after my
merge, reading `bec1dc0` as an EXTERNAL operator merge and queuing a next-cycle post-merge
sanity check (its append-only merge note is kept verbatim above). That reading is
SUPERSEDED: `bec1dc0` was THIS Cycle 26 fire's own mandated fresh-context review-then-merge
(the normal peer-gate flow), not an external merge — so no separate post-merge sanity check
is pending. My Cycle 26 commit was rebased onto `5ddb89a`; the STATE/BACKLOG "Open PRs" +
brick-3 lines resolve to this accurate account.

**Infra health check (ran first).** ALL GREEN. Runner HEALTHY — newest artifact
`verify_20260724T004105Z.json` (00:41Z) ~1.6h old at fire (02:12Z), well under 6h; scores
block CLEAN (46.1 F / 85.5 B, tests_ok True). Bench UP: full suite green after
`pip install -r requirements.txt`. Bookkeeping: the ephemeral cloud checkout's local `main`
was again the stale pre-loop lineage (`2e66201`); realigned to authoritative `origin/main`
(`ca3ed86`) via `git checkout -B main origin/main` — no un-pushed work on local main, NOT a
published-history rewrite (recurring cloud-checkout quirk, same as Cycle 25).

**What / why (the improvement — operator directive, `--battery auto` wiring).** Bricks 1–3
(discover → instantiate → NA-aware aggregate) were all on main after the PR #4 merge, but
NOTHING called them together — the CLI `--battery` flag still loaded a STATIC YAML only, so
the offering-relative battery existed as three library functions with no run path. This
cycle wires the discovery-driven mode end-to-end: `--battery auto` →
`discover_offering(ctx)` (the storefront's own surfaces, $0 read-only) →
`instantiate_battery(profile)` (one task per CLAIMED archetype) →
`aggregate_battery(battery, runs_by_task, profile=profile)` (unclaimed archetypes
NA-excluded from the spreads). This is the operator directive's core deliverable made real:
an image API discovered as `{metered_api, digital_good}` runs exactly those two intents and
NO physical-good task, and its summary records `physical_good` (+ the rest) NA rather than
polluting the completion means with a mismatch.

**Change.** `asrs/cli.py`: `_load_battery_arg(args)` → `_resolve_battery(args, ctx)`
returning `(Battery|None, OfferingProfile|None)` — three shapes: no `--battery` →
`(None,None)`; `--battery <path>` → `(load_battery(path), None)` (no profile → aggregation
stays byte-for-byte pre-brick-3); `--battery auto` → discover + instantiate + return the
profile so it threads to `aggregate_battery`. `_run_behavioral(..., profile=None)` passes
`profile=` into `aggregate_battery`. `_evaluate` calls `_resolve_battery(args, ctx)` (ctx
already built before the battery resolve) and threads `profile`. `--battery` help updated to
`PATH|auto`. An `auto` battery that discovers nothing warns + returns the empty battery +
profile (honest "nothing to assess", every archetype recorded NA — never a fabricated task).

**Invariants.** $0-only: no payment/signing code touched; `discover_offering` does read-only
$0 GETs; free-tier probe still fires AT MOST ONCE for the whole battery (unchanged loop).
Vendor-neutral: discovery keys on archetype-claim structure (offering.py, already reviewed);
no domain/vendor special-casing added. Score-neutral: `scoring.py`/`rubric/`/`probes`/
`fetch.py`/`protocols.py` byte-for-byte untouched (`git diff --name-only` clean of all
scoring-path files) → **rubric stays v0.7**; the overall score still comes from the first
task's panel (unchanged); the battery summary is an additive diagnostic (feeds no score).
Canonical delta unchanged by construction AND re-measured — replay guard 8/8
(46.1 F / 85.5 B / +39.4, 0 replay-miss) + newest verify artifact 00:41Z live-confirms the
same on v0.7. Behavioral execution of `--battery auto` is [LOCAL] (needs claude/codex +
network) — queued, not run in-cloud.

**Scope / ship.** `asrs/cli.py` + `tests/test_battery_wiring.py` only. No scoring semantics,
behavioral task-selection + CLI wiring → **direct to main**.

**Evidence.** `tests/test_battery_wiring.py` 4 → 7 (+3): (5) `--battery auto` discovers →
one task per claimed archetype in template-bank order, profile threaded back, unclaimed
archetypes available to mark NA; (6) end-to-end — the profile threads into
`aggregate_battery` so a site not claiming physical_good gets no physical-good task AND the
summary records it NA with `battery_semantics_version="b1"`; (7) null offering → empty
battery (no fabricated task) + profile still threaded. Updated the renamed-function test #3
to the `(battery, profile)` tuple contract (static-mode `(None,None)`; YAML path →
`(battery, None)`). `asrs score --help` renders `--battery PATH|auto`. Full suite
**115 → 118**, all green (canonical replay guard 8/8 included).

**Comms.** No Slack — direct-to-main, score-neutral, moves no score; not a sensitive-class
PR; not a digest window (02:12Z, before 16:00 UTC; digest last sent Cycle 16). The PR #4
merge is peer-gate follow-through visibility, already Slack-flagged at open (Cycle 25).

**Next hypothesis.** With the `auto` run path wired, the remaining operator-directive work is
[LOCAL] execution: run `asrs score <domain> --behavioral --battery auto` live on the
canonical pair + a retail control and confirm the acceptance criteria on real data
(driftflight physical_good = NA with spreads over claimed archetypes only; a shop the
inverse; NA shown "not offered" on card + terminal). Cloud-side, brick 5's HTML half
(surface `na_archetypes`/`assessed_archetypes` on `scorecard._battery`) is the next READOUT
increment, and brick 4 (out-of-scope legibility, unscored diagnostic) the next COVERAGE.
Next cloud cycle takes TRUTH.

---

## Cycle 27 — 2026-07-24T03:12Z (TRUTH)

**One-liner.** The operator directive's CORE acceptance criterion —
`driftflight.com physical_good = NA` — is now an EXECUTABLE in-cloud regression
guard, replayed offline from the committed canonical fixtures. Until now it lived
only in a [LOCAL] run log; a signal-bank change that spuriously flipped physical_good
on the canonical pair would have shipped silently.

**Track / why.** TRUTH — calibration against reality: does the offering-relative
machinery classify the canonical storefronts the way live discovery did, and does
the operator's acceptance criterion hold as a tripwire? The offering bricks (1–3 +
`--battery auto`) were live-validated [LOCAL] on 4 domains, but the canonical
physical_good=NA outcome had NO in-cloud guard. This converts the per-directive
acceptance prose into an offline executable check, the same move Cycles 17/19/21/23
made for the SCORING re-score (delta / capability-payment / relabel-invariance /
earned-dominance).

**What shipped.** `tests/test_offering_canonical.py` (4 tests). Replays each committed
`fixtures/canonical/{drift-flight.org,driftflight.com}.json` through the REAL discovery
path (`FetchContext.from_fixture → discover_offering`, no network) and pins:
- (a) the exact CLAIMED archetype SET `{metered_api, subscription, digital_good}` on both
  (exact equality, not subset — a spurious ADDED archetype, the pollution the directive
  removes, OR a DROPPED one both fail);
- claimed ∪ unclaimed partition the fixed template bank with no overlap;
- (b) the OPERATOR ACCEPTANCE CRITERION: `{physical_good, service_booking, data_retrieval}`
  are all NA/unclaimed on BOTH canonical domains, `physical_good` called out explicitly.

**Non-vacuous by substrate.** Both flight-themed homepages literally say "ship" three
times ("for every image you **ship**", "Teams that **ship** images daily") — all
metaphorical (shipping software output, not fulfillment). Two extra tests assert the
homepage prose CONTAINS the trap word yet physical_good stays NA — the precision-critical
false positive `asrs.offering` is built to avoid, exercised on REAL captured evidence
(not the synthetic surfaces `test_offering.py` uses). NEGATIVE CONTROL (offline, not
committed): appending a relaxed `bare-ship` physical_good signal flips BOTH canonical
domains to physical_good=CLAIMED — caught by both the exact-set and the NA assertions, so
the guard earns its place.

**Discovery-only / score-neutral.** Reads the same committed fixtures as
`test_canonical_replay.py` but exercises the SCORE-NEUTRAL offering pipeline (no check,
weight, cap, or aggregation rule). `git diff --stat` empty except the new test file;
scoring.py/rubric/probes/fetch.py/offering.py byte-for-byte untouched → **rubric stays
v0.7**, canonical delta unchanged by construction AND re-measured — replay guard 8/8
(46.1 F / 85.5 B / +39.4, 0 replay-miss); newest verify artifact
`verify_20260724T004105Z` (00:41Z, ~2.5h old) live-confirms the same on v0.7.

**Fixture-coverage note.** Discovery TOLERATES a missing surface by design (a
404/error/replay-miss surface is simply absent), so this guard pins the classification
OUTCOME, not fixture coverage — the canonical fixtures were captured for the SCORING
crawl, so a discovery-only surface (driftflight.com `/llms-full.txt`) is legitimately
absent (1 harmless replay-miss in the .com cache) without changing the claimed set.
Deliberately NOT asserting "no replay-miss" for discovery (that would couple the test to
what the scoring crawl happened to fetch); the scoring guard's no-miss assertion is the
right place for coverage.

**Maintenance contract.** Mirrors `test_canonical_replay`: a signal-bank change that
LEGITIMATELY changes what a canonical domain claims re-captures fixtures [LOCAL] and
updates `EXPECTED_CLAIMED` in the SAME PR. A canonical domain gaining physical_good
absent new fulfillment evidence is NOT legitimate — it is the regression this guard
catches.

**Scope / ship.** `tests/test_offering_canonical.py` only — tests-only, no scoring
semantics → **direct to main**. First duty: no open peer-gated PR (verified `[]`). Infra
health check ran first — runner HEALTHY (`verify_20260724T004105Z`, 00:41Z, ~2.5h old),
bench 118/118 pre-change, git realigned (ephemeral local-main divergence reset to
origin/main `6f49f4b`).

**Evidence.** Full suite **118 → 122** (+4). `python tests/test_offering_canonical.py`
4/4; canonical replay guard 8/8 (delta +39.4).

**Comms.** No Slack — tests-only, moves no score, not a sensitive-class PR; not a digest
window (03:12Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The offering-discovery guard pins the CANONICAL pair; the
[LOCAL] acceptance rerun (live `--battery auto` on the pair + a retail control) remains
the end-to-end validation on real data. Cloud-side, extend this guard to the retail
INVERSE once a `books.toscrape.com`-class fixture is captured [LOCAL] (asserting
physical_good CLAIMED + the API archetypes NA — the operator's "a shop shows the inverse"
half), and brick 5's HTML readout (`na_archetypes`/`assessed_archetypes` on
`scorecard._battery`) is the next READOUT increment. Next cloud cycle takes READOUT.

## Cycle 28 — 2026-07-24T04:12Z — READOUT (direct to main)

**One-liner.** The operator directive's comparability requirement (brick 5 —
"every battery readout must name WHICH archetypes were assessed") now holds on
the HTML battery card, not just the terminal. Closes the last terminal→HTML gap
for the NA-aware battery: a reader looking at the card can no longer mistake an
offering-relative mean for a mean across intents the site never advertised.

**Track / why.** READOUT — readout clarity. Brick 3 (NA-aware aggregation, PR #4,
merged Cycle 26) made `aggregate_battery(..., profile=)` record `na_archetypes`
(structurally not-offered, excluded) and `assessed_archetypes` (what the numbers
are over), and `report._battery_lines` names both in the terminal. The HTML
`scorecard._battery` did NOT — it showed the spreads and per-archetype rollup but
never named which archetypes were assessed vs not-offered, so the HTML card alone
could not tell a reader the mean is offering-relative. Same terminal→JSON→HTML
deferral `per_kind` (Cycle 10→12) and `between_kind_spread` (Cycle 18→20) took;
this is the mirror of the terminal block Cycle 25 shipped.

**What shipped.** `asrs/scorecard.py`:
- `_battery` renders an "Offering-relative" sub-block — "Assessed over" (the
  claimed archetype chips) + "Not offered (NA — excluded from every mean and
  spread, never penalized)" (dimmed NA chips) + a one-line interpretation —
  driven off `summary["na_archetypes"]` / `["assessed_archetypes"]`. Placed after
  the per-intent grid, before the by-archetype rollup, mirroring the terminal
  order in `report._battery_lines`.
- Renders ONLY when `na_archetypes` is populated (offering-relative discovery
  drove the battery). A hand-authored `--battery <path>` run has `na_archetypes`
  empty → neither block renders, byte-for-byte the pre-brick-3 readout (mirrors
  the terminal, which prints neither line without a profile).
- New CSS: `.chip.na` (dimmed/transparent, distinguishes not-offered from
  assessed at a glance) + a `.chip-row` flex wrapper. No other card touched.

**Non-vacuous.** `test_html_battery_offering_relative_names_na` builds the summary
through the REAL `aggregate_battery(..., profile=OfferingProfile)` with a
`digital_good`-only claim, then asserts every NA archetype from the summary
renders — including `metered_api`/`subscription`/`service_booking`/`data_retrieval`,
which have NO task and appear ONLY via this block, so their presence is a
non-trivial assertion (not the per-task grid leaking through). The chips are
driven off the aggregation's own lists, so the readout can't drift from the
numbers. `test_html_battery_no_offering_no_na_block` pins the negative: a
no-profile summary has `na_archetypes == []` and renders neither "Not offered"
nor "Offering-relative" (mirrors the terminal).

**Display-only / score-neutral.** `git diff --name-only`: `asrs/scorecard.py` +
`tests/test_readout.py` ONLY. scoring.py/rubric/probes/fetch/protocols/battery.py/
offering.py/report.py byte-for-byte untouched (grep clean) → rubric stays **v0.7**,
canonical delta unchanged by construction AND re-measured (in-cloud replay guard
8/8, **46.1 F / 85.5 B / +39.4**, 0 replay-miss).

**Ship.** Direct to main (READOUT, no scoring semantics). First duty: no open
peer-gated PR (verified `[]`). Infra health check ran first — runner HEALTHY
(`verify_20260724T004105Z`, 00:41Z, ~3.5h old, 46.1 F / 85.5 B / +39.4 live);
NOTE the :41 fires at 01/02/03:41Z produced no artifact (3 consecutive gaps) —
not yet past the 6h floor, but a possible fresh runner stall to watch. Git
realigned (origin/main force-updated to `f48e2fd` = Cycle 27; detached HEAD reset
to it).

**Evidence.** Full suite **122 → 124** (+2). `python tests/test_readout.py`
17 → 19; canonical replay guard 8/8 (delta +39.4, 0 replay-miss). Rendered-block
eyeball confirmed: assessed=`digital_good` chip, not-offered=5 dimmed NA chips.

**Comms.** No Slack — display-only, moves no score, not a sensitive-class PR; not
a digest window (04:12Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** Brick 5's readout is now complete in both surfaces; the
remaining offering-directive readout work is the [LOCAL] eyeball on REAL
multi-kind offering-relative data (the acceptance rerun) — the card has still only
rendered synthetic NA fixtures. If the 01/02/03:41Z verify gap persists past 6h at
the next fire, flag the runner in STATE and fold into the post-16:00 digest. Next
cloud cycle takes METHOD.

## Cycle 29 — 2026-07-24T05:12Z — METHOD (direct to main)

**One-liner.** The capability lens's vendor-neutral WORDING invariant ("checks are
worded by capability, never by vendor; no special-casing any domain or product")
is now an executable tripwire — and the one live violation is fixed: the
`bhv_no_human_gate` check description named a scored commercial storefront ("The
Exa lesson —") in text the rubric page renders verbatim to the public. Reworded to
capability language; guarded so it cannot silently return.

**Track / why.** METHOD — the "Adversarial referee pass" remaining half. Cycle 21
made the vendor-neutral SCORING invariant executable (relabel-invariance: relabel a
canonical fixture's host everywhere → byte-identical score/pillars/statuses, proving
the +39.4 delta is a property of capability EVIDENCE, not identity). But that guard
proves the MATH is identity-blind; it says nothing about whether the check
DESCRIPTIONS read neutrally. Those descriptions are user-facing:
`asrs.scorecard._write_rubric_page` renders the rubric YAML **verbatim** (scorecard.py
:249). The wording half was unguarded and had drifted — `bhv_no_human_gate.desc`
carried "The Exa lesson —", naming a specific scored storefront in a scored check's
wording, exactly the "special-casing a domain or product" the invariant forbids.

**What shipped.**
1. **Reword** (`rubric/rubric_v0.yaml`, `bhv_no_human_gate.desc` only): "The Exa
   lesson — business-rule gates are readiness factors." → "Business-rule gates — a
   mandatory sales call or identity check — stop an agent as surely as a technical
   one, so they count as readiness factors too." Preserves the exact capability
   substance (business-rule gates, not just technical ones, are readiness factors)
   with no vendor named. `git diff` = the desc prose lines ONLY (3 ins / 2 del);
   `id`/`pillar`/`max_points` untouched, `version: "0.7"` untouched, no
   weights/caps/grade_bands/check add-remove.
2. **Executable tripwire** (`tests/test_rubric_wording.py`, 4 tests): a shared
   `_scan_checks_for_scored_storefront` scans every SCORED check's `id`+`desc` (the
   `checks:` list `scoring.load_rubric` parses and the rubric page renders) for a
   word-boundary, case-insensitive denylist of SCORED STOREFRONT/PRODUCT names
   (`exa`, `driftflight`, `drift-flight` — the storefronts we score, plus the name
   that leaked). Tests: (a) the real rubric names none; (b) NON-VACUOUS negative
   control — the SAME scanner flags an injected "The Exa lesson" desc (so green =
   clean wording, not a scanner that never fires); (c) anti-vacuous structural check
   (parsed set == scoring index, ≥20 checks, every desc non-empty); (d) the denylist
   does NOT flag the MEASUREMENT INSTRUMENT — panel model names (Claude, Codex) or
   crawler UA tokens (GPTBot/ClaudeBot/OAI-SearchBot/PerplexityBot/Google-Extended)
   name the apparatus / crawler population measured symmetrically, not a scored
   storefront; flagging them would be a false positive.

**Scope note (why comments are out of scope).** `load_rubric` parses `checks:`, not
the YAML changelog comments. Those comments DO name the canonical pair and "Shopify"
— to DOCUMENT mechanism and score-neutrality (why a change is monotone / why the
canonical delta is unchanged), engineering history, a distinct category from wording
a SCORED check around a storefront. The guard keys on the parsed, scored text — the
crisp boundary matching what the scorer sees. Honest limit: this is a denylist
tripwire against RE-INTRODUCING a KNOWN name, not a proof of universal prose
neutrality (a novel vendor name off-list would pass); it complements, not replaces,
the relabel-invariance guard and the standing prose re-read.

**Display-only / score-neutral.** `desc` is rendered on the rubric page but never
read by `scoring.score` (which keys on `id`/`pillar`/`max_points`; `load_rubric`
indexes checks by `id` only). scoring.py/probes/fetch/protocols/battery/offering
byte-for-byte untouched → rubric stays **v0.7**, canonical delta unchanged by
construction AND re-measured (in-cloud replay guard 8/8, **46.1 F / 85.5 B /
+39.4**, 0 replay-miss).

**Ship.** Direct to main (METHOD, no scoring semantics — a display-string reword +
tests). First duty: no open peer-gated PR (verified `[]` via list_pull_requests).
Infra health check ran first — runner STALLED-BUT-UNDER-FLOOR: newest
`verify_20260724T004105Z` (00:41Z) is ~4h31m old at this 05:12Z fire, still under
the 6h floor, but the :41 fires at 01/02/03/04:41Z produced NO artifact (4
consecutive gaps — the fresh stall Cycle 28 flagged to watch). At the next fire the
00:41Z artifact will be ~5.5h; the fire after, >6h → if still gapped then, flag +
fold into the post-16:00 digest. The Cycle-17 replay guard remains the primary
in-cloud canonical signal regardless. Git realigned (origin/main force-updated to
`339698a` = Cycle 28; detached HEAD reset to it).

**Evidence.** Full suite **124 → 128** (+4). `python tests/test_rubric_wording.py`
4/4; canonical replay guard 8/8 (delta +39.4, 0 replay-miss); rubric diff confined
to the desc prose (verified `git diff` — semantics lines untouched).

**Comms.** No Slack — display-only, moves no score, not a sensitive-class PR; not a
digest window (05:12Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The wording invariant now has a floor tripwire and a prose
reference (methodology page, Cycle 16/24). The remaining referee-pass work is a
prose re-read of the METHODOLOGY page + card `desc` strings in scorecard.py for the
same lens (those are hand-authored HTML, not the parsed rubric, so out of this
guard's scope), and extending the relabel-invariance guard to the [LOCAL]
third-control fixture once captured. If the 01–04:41Z verify gap persists past 6h at
the next fire, flag the runner in STATE + the post-16:00 digest. Next cloud cycle
takes COVERAGE.

## Local verification — 20260724T054104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T054104Z.json

## Cycle 30 (COVERAGE) — 2026-07-24T06:18Z — path-based free-tier opt-in discovery (third convention)

**Track / item.** COVERAGE. Backlog P2 "Free-tier probe generalization → (b) path-based
opt-in convention (a documented `/free/…` or `/v1/free/…` endpoint) — the next in-cloud
COVERAGE increment, same discovery-only/score-neutral shape as the query-param half."

**What.** Free-tier opt-in DISCOVERY broadened to a THIRD convention — the URL PATH.
`asrs/behavioral/free_tier.py`: `_scan_path_instruction(text)` recognises a documented
free-mode endpoint whose path carries a conventional free segment (`/free/…`,
`/v1/free/…`, `/api/free-tier/call`), mirroring the header scanner (Cycle ≤14) and the
query-param scanner (`_scan_query_param_instruction`, Cycle 22). Plumbed as an additive
`FreeTierDiscovery.opt_in_path: str | None` field + an `opt_in_path` evidence key,
populated by `discover_free_tier`. So a site that advertises its free tier by a dedicated
path endpoint (currently mis-discovered as "opt-in-undiscoverable") is now RECOGNISED and
RECORDED — the north-star many-conventions axis.

**Why (capability lens).** An agent-native storefront can signal "call THIS to use the
free allowance" three documented ways: a request header, a URL query param, or a
dedicated path. The probe already discovered the first two; the path convention was a
blind spot. Recognising it is measurement COVERAGE — the benchmark sees a capability the
site actually exposes instead of scoring the site's rails absent.

**Precision-first / vendor-neutral.** The free segment must be an EXACT free-mode token
from an allowlist (`free / freetier / free-tier / free_tier / freemode / free-mode /
free_mode`), so a bare substring "free" never trips it — `/freedom`, `/freelance`, and a
retail `/free-shipping` checkout path are all rejected (negative controls in the test).
The `scheme://host` prefix is consumed but not captured (mirroring `_METHOD_PATH_RE`) so
a host is never mistaken for a path segment (`https://api.x.example/v1/free/generate` →
`/v1/free/generate`, not `/api.x.example/…`). A NON-VACUOUS second gate: the free-tier
context check runs over the surrounding prose with the matched path EXCISED, so a
`/free/…` path alone (no adjacent free-allowance language) does NOT match — the path's own
`free` segment cannot satisfy its own context requirement.

**DELIBERATELY SCORE-NEUTRAL** (the load-bearing invariant, same as Cycle 22's query-param
half). `opt_in_path` is NOT in the `advertised` gate (which reads only `header` /
`free_units`) and NOT consumed by the live-call path (test-pinned: a path-only doc keeps
`advertised=False`; adding a `/v1/free/generate` path to the header fixture leaves
`advertised` byte-for-byte identical). Wiring it into the gate + the live free-mode call is
score-increasing (invariant #3) → queued [LOCAL] alongside the query-param live-wiring.

**Safety (invariant #1).** NOT signing/payment code — the diff is confined to the
discovery region (denylist/allowlist constants, the dataclass field, the scanner, and the
`discover_free_tier` wiring). `parse_challenge` / `_settle_zero_value` /
`_build_transfer_authorization_typed_data` / the nonzero-refusal property are byte-for-byte
untouched (signing-sentinel grep over the diff clean; `test_free_tier.py`'s
`is_zero_value >= 3` structural tripwire still green).

**Score impact.** No scoring semantics; rubric stays **v0.7**. scoring.py / rubric/ /
protocols.py / fetch.py / offering.py / battery.py / scorecard.py byte-for-byte untouched
(`git diff --name-only` = `asrs/behavioral/free_tier.py` + `tests/test_free_tier.py` only).
Canonical delta unchanged by construction AND re-measured (in-cloud replay guard 8/8,
**46.1 F / 85.5 B / +39.4**, 0 replay-miss on v0.7).

**Ship.** Direct to main (COVERAGE, additive discovery, no scoring semantics). First duty:
no open peer-gated PR (verified `[]` via list_pull_requests). Infra health check ran first —
runner RECOVERED: newest `verify_20260724T054104Z` (05:41Z, 46.1 F / 85.5 B / +39.4) is
~31 min old at this fire, well under the 6h floor — the 01–04:41Z stall Cycle 28/29 flagged
has self-cleared (a fresh :41 artifact landed at 05:41Z). Runner-stall watch CLOSED.

**Evidence.** Full suite **128 → 129** (+1). `python tests/test_free_tier.py` 9/10 → 10/10
(+test_path_optin_discovery: scanner extraction of 3 free-path forms, 4 negative controls —
substring-not-segment / retail free-shipping / no-adjacent-prose / no-free-segment —,
evidence surfacing, and score-neutrality on both a path-only doc and the header fixture).
Canonical replay guard `test_canonical_replay.py` 8/8 (delta +39.4, 0 replay-miss).

**Comms.** No Slack — score-neutral additive discovery, moves no score, not a sensitive-class
PR; not a digest window (06:18Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** Discovery now covers all three documented opt-in conventions (header /
query-param / path). The remaining free-tier-generalization work is (a) [LOCAL],
score-increasing: fold `opt_in_query` AND `opt_in_path` into the `advertised` gate + the
live free-mode call (append the param / route to the path), verified on ≥2 real domains,
likely peer-gated; and (b) non-EVM zero-value settlement schemes (still open). Next cloud
cycle takes TRUTH.

## Local verification — 20260724T064105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T064105Z.json

## Cycle 31 (TRUTH) — 2026-07-24T07:20Z — offering-classifier vendor-neutrality (domain-relabeling invariance)

**Track / item.** TRUTH. Backlog "Adversarial referee pass" (recurring METHOD/TRUTH) +
the standing "extend the relabel-invariance guard to more layers/storefronts" follow-up.
Cycle 21 made vendor-neutrality an executable tripwire for the SCORING path
(`test_canonical_replay.py` relabel-invariance); the OFFERING classifier — which drives
the operator directive's TASK SELECTION and NA semantics — carried no equivalent guard.

**What.** `tests/test_offering_canonical.py` +3 tests (4 → 7). Each relabels a committed
canonical fixture's host to a neutral placeholder (`vendor-neutral.test`) — request keys
AND every response byte, a whole-fixture string sub, temp file, replayed through the REAL
`FetchContext.from_fixture -> discover_offering` path — and asserts the CLAIMED archetype
list (ORDERED — order is the fixed template-bank task order, cross-site comparability) and
the UNCLAIMED/NA set are IDENTICAL to the un-relabeled discovery, and that the relabeled
claimed set still equals the [LOCAL]-validated `{metered_api, subscription, digital_good}`.
`test_offering_relabel_invariance_org` / `_com` + `test_offering_relabel_negative_control`.

**Why (capability lens).** `classify_offering(domain, surfaces)` takes the domain as an
argument and the host string appears INSIDE the classifier's own matched evidence (the
`metered_api` "post-endpoint" quote is `POST https://<host>/…` — 2 such quotes on .org, 4
on .com). If classification ever keyed on the domain — a favorable OR hostile special-case
— a site's TASK SET (which archetypes it is judged on vs excused as NA) would depend on its
NAME, not what it claims to sell: exactly the vendor-rigging the directive's "vendor-neutral,
never a vendor or domain string" boundary forbids, at the battery-selection layer. This
proves the claimed/NA partition is a property of the EVIDENCE, not the storefront's identity
— the offering-layer complement to Cycle 21's scoring relabel guard. Worded by capability,
never by vendor.

**Non-vacuous.** (i) Each invariance test first asserts the host appears in the base
profile's matched evidence, so the relabel genuinely changes the text classification reads
(not a no-op). (ii) The neutral host is a different LENGTH and carries no archetype-signal
word, so invariance is neither a same-length coincidence nor a neutral-host artifact.
(iii) `test_offering_relabel_negative_control` monkeypatches a FAVORABLE identity-keyed
special-case (force-add `physical_good` when `"driftflight" in domain`) and confirms the
relabel-invariance assertion CATCHES it — base (canonical identity) claims physical_good,
neutral-host run does not, claimed sets diverge — then restores the real classifier and
asserts the restore. So the assertion has teeth.

**Regression / invariants.** Tests-only: `git diff --stat` = `tests/test_offering_canonical.py`
only; scoring.py / rubric / probes / fetch / offering.py byte-for-byte untouched
(`git diff --name-only -- asrs/ rubric/` empty) → rubric stays **v0.7**, canonical delta
unchanged by construction AND re-measured (in-cloud replay guard `test_canonical_replay.py`
8/8, **46.1 F / 85.5 B / +39.4**, 0 replay-miss; corroborated live by
`verify_20260724T064105Z` 06:41Z). Score-neutral (the offering pipeline feeds no score /
no aggregation math). $0-only intact (discovery is read-only GETs, replayed offline).

**Ship.** Direct to main (TRUTH, tests-only, no scoring semantics).

**Evidence.** Full suite **129 → 132** (+3). `python tests/test_offering_canonical.py`
4/4 → 7/7. Canonical replay guard 8/8 (delta +39.4, 0 replay-miss). All 16 test files pass.
First duty: no open peer-gated PR (verified `[]` via list_pull_requests). Infra health check
ran first — runner HEALTHY: newest `verify_20260724T064105Z` (06:41Z, 46.1 F / 85.5 B /
+39.4) ~30 min old at this fire, well under the 6h floor.

**Comms.** No Slack — tests-only, moves no score, not a sensitive-class PR; not a digest
window (07:20Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The vendor-neutrality tripwire now covers BOTH the scoring path
(Cycle 21) and the offering/task-selection path (this cycle) on the canonical pair. The
remaining relabel-coverage gap is a NON-STOREFRONT control (example.com) and a retail
INVERSE (books.toscrape.com) — both need a [LOCAL] fixture capture (queued P2), after which
this same offering relabel guard extends to them in-cloud. Next cloud cycle takes READOUT.

## Local verification — 20260724T074105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T074105Z.json

## Local cycle — 20260724T074745Z (TRUTH) — retail-INVERSE offering fixture: the operator acceptance criterion's OTHER half, made an in-cloud tripwire

**First duty.** No open peer-gated PR (verified `gh pr list --state open` → empty). Nothing
to review/merge.

**Infra health check (ran first).** ALL GREEN. Newest verify artifact
`verify_20260724T074105Z` (07:41Z) was ~40s old at this fire — well under the 6h floor
(runner HEALTHY; the 01–04:41Z stall Cycle 28/29 flagged self-cleared by Cycle 30, watch
CLOSED). Full suite runnable (16 files, all pass). Bookkeeping consistent: last cycle (31)
+ its verify pushed cleanly, LOG/STATE match `git log`. Canonical delta live-stable on the
artifact: 46.1 F / 85.5 B / +39.4. No repair needed.

**Item (the ONE [LOCAL] backlog item).** "[LOCAL] Retail-INVERSE offering fixture" (P2,
Cycle-27 follow-up) — the operator directive's acceptance criterion is two-sided:
"driftflight.com shows physical_good = NA …; **a retail storefront shows the inverse.**"
Cycle 27 pinned the canonical NA half in-cloud (`test_offering_canonical.py`); the retail
inverse lived only as a [LOCAL] run-log fact with no in-cloud guard. This closes that gap.
Chosen over the heavier P0 behavioral items because those are either codex-blocked on the
canonical pair (reputation gate, 4/4) or budget-busting for one headless fire; a $0 static
fixture capture + cloud-doable test wiring is the highest-certainty unit that advances the
same operator directive, and it delivers a DURABLE tripwire rather than a one-off artifact.

**What.** (1) Captured `fixtures/canonical/books.toscrape.com.json` via a STATIC $0 crawl
(`asrs.cli score books.toscrape.com --record-fixture …` — 41 GET entries, 0 POST, no
secrets: a public book-catalog scraping sandbox). (2) Wired `test_retail_inverse_offering`
into `tests/test_offering_canonical.py` (7 → 8 tests): replays the committed fixture through
the REAL `FetchContext.from_fixture → discover_offering` path (no network) and asserts the
MIRROR image of the canonical guard — claimed set == `{physical_good}` EXACTLY, and
`{metered_api, subscription, digital_good}` (exactly what the canonical pair CLAIMS) all
NA/unclaimed; plus the claimed+unclaimed partition of the archetype bank.

**Why (capability lens).** The operator directive removes battery pollution by making the
task set OFFERING-RELATIVE: a site is probed only for what it CLAIMS to sell, and unclaimed
archetypes are NA (excluded from every mean/spread, never penalized). Cycle 27 proved that
an agent-native image API → physical_good NA on real evidence. This proves the OTHER
direction on real evidence: a real retail catalog → physical_good CLAIMED, API/subscription/
digital NA. Same `discover_offering` pipeline, opposite verdict — demonstrating the
claimed/NA partition tracks the storefront's TYPE (what it sells), not its identity. The
acceptance criterion now has an executable tripwire on BOTH sides.

**Non-vacuous.** The physical_good claim rests on ANCHORED fulfillment evidence — labels
`add-to-cart` + `stock` from "In stock" / "Add to basket" on the homepage — the specific
signals the precision guard requires, asserted explicitly (`{add-to-cart, stock} <= labels`).
This is the exact complement of the canonical pair's metaphorical-"ship" NA case: books.
toscrape.com genuinely fulfills a physical good and the classifier says so from evidence,
where the flight-themed pair's metaphorical "ship" correctly does NOT trip physical_good.
(Deliberately did NOT add a relabel-invariance case for this fixture: the host string does
not appear in physical_good's prose evidence, so relabeling would be VACUOUS here — the
canonical pair's relabel guard already covers identity-independence where it is non-vacuous.)

**Regression / invariants.** `git diff --name-only -- asrs/ rubric/` EMPTY — scoring.py /
rubric / probes / fetch / offering.py byte-for-byte untouched → rubric stays **v0.7**,
canonical delta unchanged by construction AND re-measured (in-cloud replay guard
`test_canonical_replay.py` 8/8, **46.1 F / 85.5 B / +39.4**, 0 replay-miss; live-corroborated
by `verify_20260724T074105Z`). Score-neutral (offering pipeline feeds no score / no
aggregation math). $0-only intact (static read-only GET crawl, replayed offline). Fixture
carries no secrets (public sandbox, all GET, secret-string scan → only book titles e.g.
"The Dirty Little Secrets of Getting Your Dream Job").

**Ship.** Direct to main (tests + a replay fixture, NOT a scoring-semantics change — per
playbook ship rules).

**Evidence.** `tests/test_offering_canonical.py` 7/7 → 8/8; full suite **132 → 133**. All 16
test files pass. New fixture: `fixtures/canonical/books.toscrape.com.json`. (Live run report
`runs/books_toscrape_com_20260724T074402.json` is gitignored.)

**Comms.** No Slack — tests + fixture, moves no score, not a sensitive-class PR; not a digest
window (07:47Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The offering acceptance criterion is now guarded in-cloud on BOTH sides
(canonical NA + retail inverse). The remaining offering-layer [LOCAL] gaps: the non-storefront
control (example.com) replay + relabel case (P2), and — the operator directive's crown jewel
— the end-to-end LIVE `--battery auto --models claude,codex` acceptance rerun, still gated on
codex reachability for the canonical pair. Cloud rotation unaffected (next cloud cycle READOUT).


## Cycle 32 (READOUT) — 2026-07-24T08:12Z — link "Grade capped" chips to their methodology cap row

**Track.** READOUT (rotation: Cycle 31 TRUTH → this READOUT; next METHOD).

**First duty / infra health.** Git realigned: the fresh cloud checkout's local `main`
had DIVERGED (a stale Jul-22 lineage tip `2e66201` "encode the Opus-cycles / Fable-
architecture division", 22/53 split vs origin) while detached HEAD sat on origin's real
tip `0cf1a98`; that Jul-22 playbook edit is superseded by origin's reconciled version, so
`git reset --hard origin/main` → `0cf1a98`. No open peer-gated PR (`list_pull_requests`
state=open → `[]`). Infra health: newest `runs/local/verify_20260724T074105Z.json` (07:41Z)
~31 min old at fire — runner HEALTHY, live 46.1 F / 85.5 B / +39.4 on v0.7. Suite green
baseline (16 files) after `pip install -r requirements.txt` (eth-account present → 9/9 free-tier).

**What / why.** The methodology page (Cycle 16) documents WHY each critical finding caps the
grade (section 8), but a card's "Grade capped by <slug>" alert (Cycle-earlier `_caps_alerts`)
was a dead chip — a reader seeing a capped grade had no path to the explanation. Closes the
long-standing READOUT follow-up (methodology-page cap-chip anchor-link, queued P2 twice):
each cap row in `methodology.html` section 8 now carries `id="cap-<slug>"`, and the card's
capped chip renders as `<a class="chip" href="methodology.html#cap-<slug>">` pointing at it.
SINGLE SOURCE OF TRUTH: a new module-level `_cap_anchor(slug)` computes the fragment for BOTH
surfaces (the Cycle-16/20 anti-drift pattern), lowercasing + collapsing any non-alnum run so a
future odd slug still yields a valid, matching anchor on both sides. Added `text-decoration:none`
to `.chip` + an `a.chip:hover` affordance so the chip-link reads as a chip, not a blue underline.

**Regression / invariants.** `git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py`
ONLY; scoring.py / rubric / probes / fetch / protocols / behavioral / offering.py / battery.py
0 files changed → display-only, rubric stays **v0.7**, canonical delta unchanged by construction
AND re-measured (in-cloud replay guard `test_canonical_replay.py` 8/8, **46.1 F / 85.5 B / +39.4**,
0 replay-miss; live-corroborated by `verify_20260724T074105Z`). Vendor-neutral: the link keys on
the rubric's own capability-worded cap slugs, no domain/vendor string. $0-only untouched (no
payment/signing code in scope).

**Evidence.** `tests/test_readout.py` 19 → 23 (+4: `_cap_anchor` sanitizer, methodology rows carry
anchor ids, the card chip links to the anchor + no-cap → empty no-op, and the load-bearing
CANNOT-DRIFT test tying every rubric cap's rendered card link to an id actually present in the
rendered methodology page). Full suite **133 → 137**; all 16 files pass. Rendered smoke:
`<a class="chip" href="methodology.html#cap-no-https">no-https</a>`.

**Ship.** Direct to main (display-only readout, no scoring semantics — per playbook ship rules).

**Comms.** No Slack — display-only, moves no score, not a sensitive-class PR, before the 16:00 UTC
digest window (fire 08:12Z; digest last sent Cycle 16).

**Next hypothesis.** The methodology page is now navigable FROM a card's cap alert; the symmetric
remaining READOUT nicety is a per-check-row → methodology-section / evidence-blob link ("Evidence
links on the card", still P2), and the compare-card delta → earned-dominance section link (Cycle-24
follow-up). Next cloud cycle METHOD.

## Local verification — 20260724T084104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T084104Z.json

## Local cycle — 20260724T085240Z (METHOD) — hermetic nested claude panels: stop the shopper/trust subprocess inheriting the operator's MCP fleet

**First duty.** No open peer-gated PR (verified `gh pr list --state open --json …` → `[]`).
Nothing to review/merge.

**Infra health check (ran first).** ALL GREEN. Newest verify artifact
`verify_20260724T084104Z` (08:41Z) was ~1 min old at this fire — well under the 6h floor
(runner HEALTHY). Full suite runnable (16 files pre-change, all pass). Bookkeeping consistent:
Cycle 32 + its verify pushed cleanly, LOG/STATE match `git log` (HEAD `0f3695a`). Canonical
delta live-stable on the artifact: 46.1 F / 85.5 B / +39.4 on v0.7. No repair needed.

**Item (the ONE [LOCAL] backlog item).** "Nested shopper spawns the full user MCP fleet" (P1,
METHOD/efficiency — observed 2026-07-23T10:13Z during the battery run). Verifying it requires a
live `claude -p` panel, so it is [LOCAL]. Chosen over the heavier P0 behavioral items
DELIBERATELY and recorded as the honest sequencing: the top P0 is the operator-directive
end-to-end `--battery auto --models claude,codex` acceptance rerun — but that rerun's shopper
subprocesses inherit the very MCP-fleet contamination fixed here, so running the flagship
operator-acceptance validation FIRST would produce a slow (~1 min/panel MCP boot) and
measurement-CONTAMINATED artifact (unrelated trigger/unity/linear/motherduck connections pulled
into the environment). This fix is the honest prerequisite: a $0, in-budget, direct-to-main
measurement-VALIDITY unit that makes the next acceptance rerun both hermetic and faster. (The
canonical-pair NA + retail-inverse acceptance halves are already guarded in-cloud, Cycles 27 /
local-07:47Z, so no acceptance coverage is lost by sequencing the environment fix first.)

**Root cause (confirmed in code + config).** Both behavioral panels build a headless
`claude -p` command — `asrs/behavioral/shopper._claude_cmd` (the shopper) and
`asrs/behavioral/trust_probe._claude_cmd` (the trust probe) — and NEITHER passed
`--strict-mcp-config`, so each subprocess loaded the operator's filesystem MCP configuration.
`~/.claude.json` `mcpServers` (GLOBAL, applies from any cwd) is exactly
`['trigger','unityMCP','linear-server','hex','posthog','motherduck']` — the same fleet the
10:13Z run was seen booting before it browsed. The shopper's only capabilities are
`--allowedTools WebFetch WebSearch`; it needs ZERO MCP servers.

**What.** Added `--strict-mcp-config` to BOTH `_claude_cmd` builders (claude: "Only use MCP
servers from --mcp-config, ignoring all other MCP configurations"). Passed WITHOUT any
`--mcp-config`, it yields an EMPTY MCP fleet — a hermetic panel. New
`tests/test_shopper_hermetic.py` (4 tests) pins the contract on both builders: each carries
`--strict-mcp-config` and NO `--mcp-config` (so strict == empty fleet), and the rest of the
panel command is intact (`claude -p`, `--output-format json`, `--model opus`, shopper still
WebFetch/WebSearch-only). Non-vacuous by construction — the pre-fix builders (no flag) fail
every `--strict-mcp-config` assertion.

**Why (measurement rigor).** The shopper measures a STOREFRONT's agent-readiness; the trust
probe measures a panel's willingness. Neither should be measured through — or slowed by — the
operator's incidental MCP setup. Booting 6 unrelated servers per panel (~1 min each) both
inflated wall-time (12 panels ≈ 12 min of pure MCP boot in the 10:13Z battery) and pulled
external connections into the measurement environment. Hermetic panels are the north-star
"more rigorous" axis applied to the harness itself: the same storefront, measured in a clean,
reproducible environment.

**Live verification (this fire, on Jonah's machine — networked).** (a) MECHANISM: the fixed
command carries `--strict-mcp-config` (`SH._claude_cmd(...)` asserted True live). (b) FUNCTIONAL
— the backlog item's explicit "a panel still produces valid checkpoints after": ran ONE live
`shopper._run_one("driftflight.com", …, "claude", trial 1)` through the fixed path — it browsed
successfully (10 turns, 131s of BROWSING not boot), emitted all five checkpoints TRUE
(found_product / understood_pricing / found_purchase_path / machine_payable_path / no_human_gate)
with coherent, specific blockers (USDC-on-Base/Tempo wallet funding; the `df_live_` upstream key
is a browser signup gate; recon-only, nothing settled) — a fully-functional panel, not a
run-failure. (c) HERMETIC PROOF on the REAL panel transcript: `mcp_servers == []` — zero
trigger/unity/linear/motherduck/hex/posthog booted on the actual fixed code path, live.
(A trivial `-p` timing A/B could not reproduce the boot delta because this headless subprocess
env surfaced `mcp_servers=[]` even pre-flag; the 10:13Z run already empirically documented the
fleet boot, and `~/.claude.json` confirms the global config is present.)

**Regression / invariants.** `git diff --name-only` = `asrs/behavioral/shopper.py`,
`asrs/behavioral/trust_probe.py`, `tests/test_shopper_hermetic.py` only —
scoring.py / rubric / probes / fetch / offering / battery byte-for-byte untouched → rubric
stays **v0.7**, canonical delta unchanged by construction AND re-measured (in-cloud replay
guard `test_canonical_replay.py` 8/8, **46.1 F / 85.5 B / +39.4**, 0 replay-miss;
live-corroborated by `verify_20260724T084104Z`). Behavioral-execution plumbing only (a CLI
flag on the nested agent), NOT a scoring-semantics change and NOT payment/signing code. $0-only
intact (the verification panel is recon-only — did not register, call, or settle; invariant #1).

**Ship.** Direct to main (behavioral-execution plumbing + tests, no scoring semantics — per
playbook ship rules; the P1 item itself is annotated "direct-to-main safe").

**Evidence.** `tests/test_shopper_hermetic.py` 4/4 (new); full suite **137 → 141**; all 17 test
files pass. Live panel run (force-added): `runs/local/hermetic_shopper_verify_20260724T084946Z/
transcripts/driftflight.com_claude_t1.json` (`mcp_servers: []`, 5/5 checkpoints, no secret
tokens — public-storefront recon).

**Comms.** No Slack — behavioral plumbing, moves no score, not a sensitive-class PR; not a
digest window (08:52Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The measurement environment is now hermetic, so the operator-directive
crown jewel — the end-to-end LIVE `--battery auto` acceptance rerun (top P0) — will run clean
and ~1 min/panel faster next local fire. It stays gated on codex reachability for the canonical
pair (reputation gate, 4/4 at 11:42Z), but a claude-only `--battery auto` on the with-rails
`driftflight.com` (claims {metered_api, subscription, digital_good}) is now the cheapest way to
exercise the full offering-relative pipeline live + eyeball the NA-naming card. Cloud rotation
unaffected (next cloud cycle METHOD).

## Cycle 33 (METHOD) — 2026-07-24T09:12Z — vendor-neutral WORDING guard extended from the parsed rubric to the RENDERED readout prose

**Track.** METHOD (measurement rigor: the vendor-neutrality invariant, made a tripwire on
the surface a reader actually sees — the standing "Adversarial referee pass" item's READOUT half).

**What / why.** Cycle 29 made the capability-lens WORDING invariant ("checks are worded by
capability, never by vendor; no special-casing any domain or product") executable for the
PARSED rubric — `tests/test_rubric_wording.py` scans every scored check's id/desc for a
scored-storefront/product name and caught + drove the fix of the one live violation ("The Exa
lesson —"). But that guard covers only the machine-parsed `checks:` list. The HAND-AUTHORED
readout PROSE the public reads — the "read the paper" `methodology.html` and the card's own
`<div class="desc">` explanation strings (`asrs/scorecard.py`) — was UNguarded, i.e. exactly
the kind of surface the "Exa lesson" leak lived on. This cycle converts the standing manual
prose re-read into an executable tripwire for that readout layer.

`tests/test_readout_wording.py` (4 tests) renders the full public readout set for a NEUTRAL
placeholder domain (`example.test`, not on the denylist) via `scorecard.build_scorecard` and
scans the rendered `methodology.html` + card `card.html` with the SAME denylist + SAME matcher
Cycle 29 uses — factored into a shared `_scan_text_for_scored_storefront(text)` in
`test_rubric_wording.py` (behavior-preserving refactor: `_scan_checks_for_scored_storefront`
now delegates to it, existing 4/4 unchanged), imported by the new module so ONE denylist +
ONE matching primitive back both surfaces. Asserts no scored-storefront name appears.

Two design points that make the guard honest:
- **DOMAIN-AS-DATA → neutral domain.** A card is ABOUT a storefront, so that domain
  legitimately appears as DATA (title/hero/column). Scanning a canonical-pair card would
  drown in true positives. Rendering for `example.test` means any denylisted hit can only come
  from hand-authored TEMPLATE prose — precisely the leak we want.
- **rubric.html DELIBERATELY EXCLUDED, and reused as a LIVE non-vacuous control.**
  `_write_rubric_page` renders the rubric YAML verbatim, changelog comments and all; those
  comments name the canonical pair (+ "Shopify") to DOCUMENT mechanism / score-neutrality —
  the engineering-history category Cycle 29 already carved out (it scans `checks:`, never the
  comments). Scanning verbatim YAML would flag legitimate history. Instead the test ASSERTS the
  scanner fires on the rendered rubric.html (its changelog trips it: `['driftflight',
  'drift-flight']`) — live proof the matcher actually fires on rendered HTML, so the clean
  card/methodology runs mean the prose is neutral, not that the matcher is dead. A second
  non-vacuous leg: a synthetic `<div class="desc">…The Exa lesson…</div>` blob is flagged by
  the shared matcher. A `test_readout_surfaces_are_substantive` guard pins methodology + card
  render ≥4000 chars so an empty/degenerate render can't vacuously pass.

**Validation / regression.** `git diff --name-only -- asrs/ rubric/` EMPTY — scoring.py /
rubric / probes / fetch / protocols / offering / battery / scorecard byte-for-byte untouched
(the whole change is `tests/test_rubric_wording.py` refactor + new `tests/test_readout_wording.py`)
→ rubric stays **v0.7**, canonical delta unchanged by construction AND re-measured (in-cloud
replay guard `test_canonical_replay.py` 8/8, **46.1 F / 85.5 B / +39.4**, 0 replay-miss;
live-corroborated by `verify_20260724T084104Z` 08:41Z). Vendor-neutral by construction (keys on
the SAME capability-invariant denylist, worded by capability). Not payment/signing code.

**Ship.** Direct to main (tests-only, no scoring semantics — per playbook ship rules).

**Evidence.** `tests/test_readout_wording.py` 4/4 (new); `tests/test_rubric_wording.py` 4/4
(unchanged after the shared-matcher refactor); full suite **141 → 145**; all 18 test files pass.

**First duty.** No open peer-gated PR (verified `list_pull_requests` state=open → `[]`). Infra
health check ran first — runner HEALTHY (newest `verify_20260724T084104Z`, 08:41Z, ~31 min old
at fire, 46.1 F / 85.5 B / +39.4); bench 141/141 pre-change; git realigned (detached HEAD from a
forced origin/main update `0b0ad41` → checked out `main` = origin/main).

**Comms.** No Slack — tests-only, moves no score, not a sensitive-class PR; not a digest window
(09:12Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The vendor-neutrality invariant is now a tripwire on THREE layers — scoring
(relabel-invariance, Cycle 21), the parsed rubric wording (Cycle 29), and now the rendered
readout prose (this cycle). The remaining referee-pass increment is to extend BOTH relabel
guards AND both wording denylists as new scored storefronts/fixtures land (add each new name to
`_SCORED_STOREFRONT_NAMES`; wire the third-control-domain `example.com` fixture once captured
[LOCAL]). Next cloud cycle takes COVERAGE.

## Local verification — 20260724T094103Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T094103Z.json

## Cycle 34 (COVERAGE) — 2026-07-24T10:12Z — offering discovery reads the OpenAPI / Swagger spec (the operator directive's fourth surface)

**Track.** COVERAGE (measurement coverage/flexibility: broadens the offering-relevance
discovery surface set toward the north-star "many storefront types" axis).

**What / why.** The operator directive (2026-07-23, BACKLOG P0) names the discovery surfaces
explicitly: "classify what the storefront CLAIMS to sell from its own surfaces (llms.txt,
manifest/catalog, **OpenAPI**, homepage)". Brick 1 (`asrs/offering.py`, local fire 23:49Z)
covered the homepage + the natural-language docs (`/llms.txt` / `/llms-full.txt` /
`/manifest.json`) but NOT the machine API CONTRACT — the OpenAPI / Swagger spec — even though
it is the surface an API-FIRST storefront is most likely to expose. A metered-API product may
serve no marketing homepage and no llms.txt, only its spec; without reading it such a site is
classified from its homepage alone and can be mis-read as offering nothing (the exact
under-coverage that pollutes the offering-relative battery from the other direction — a servable
archetype left untested / mis-marked NA). This cycle adds the spec to the discovery surface set.

`asrs/offering._SURFACE_DOCS` gains `/openapi.json`, `/.well-known/openapi.json`, `/swagger.json`
(well-known JSON conventions, most-specific first). NO new signal is needed: an OpenAPI spec's
own `servers` URLs, path list, and operation summaries/descriptions are exactly the
vendor-neutral "qualified API" / "pay-per-*" / usage-based / generated-media / x402 language the
existing signal bank already anchors on — the surface only needed to be READ. A spec that 404s
is simply absent (discovery tolerates a missing surface by design, same as any other doc).

**Vendor-neutral / precision.** Signals key on capability language, never a vendor/domain string;
a JSON API contract with no "add to cart"/"$X per month" prose does NOT trip physical_good or
subscription (pinned). The change is purely which paths are fetched — the classification logic is
untouched.

**Score-neutral by construction.** `asrs/offering.discover_offering` is called ONLY from
`asrs/cli.py:_resolve_battery` (the `--battery auto` path) — verified by grep — and NEVER on the
scoring path. The commerce-manifest SCORING probe uses its own separate
`asrs/probes/protocols._AGENT_SURFACE_DOCS` (still the original three docs, DELIBERATELY not
touched — adding OpenAPI there would be score-increasing + peer-gated). `git diff --name-only --
asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py` EMPTY → rubric stays **v0.7**.

**Validation / regression.** Full suite **145 → 147**, all 18 files pass (exit 0). `test_offering.py`
7 → 9 (+`test_openapi_spec_alone_classifies_api_first_storefront`: an OpenAPI-spec-ONLY surface map,
no homepage/llms.txt, classifies metered_api + digital_good on 6 distinct spec signals, physical_good
+ subscription correctly NA; +`test_openapi_surface_is_wired_for_live_discovery`: structural guard the
three OpenAPI conventions are in `_SURFACE_DOCS` and the natural-language surfaces did not regress).
Canonical delta unchanged by construction AND re-measured: in-cloud replay guard
`test_canonical_replay.py` **8/8, 46.1 F / 85.5 B / +39.4**, 0 replay-miss; canonical OFFERING guard
`test_offering_canonical.py` **8/8 UNCHANGED** — the added surfaces are absent from the committed
canonical fixtures (replay-miss → absent), so the canonical classification
`{metered_api,subscription,digital_good}` / physical_good NA is byte-identical; live-corroborated by
`verify_20260724T094103Z` (09:41Z, 46.1 F / 85.5 B / +39.4). Not payment/signing code (offering
discovery is read-only $0 GETs; no parse_challenge/settle/sign path touched).

**Ship.** Direct to main (discovery-surface addition to a diagnostic-only module that feeds no
score — score-neutral, not scoring semantics, per playbook ship rules).

**Evidence.** `git diff --stat` = `asrs/offering.py` + `tests/test_offering.py` only (2 files,
+94/−7). Suite 145 → 147.

**First duty.** No open peer-gated PR (verified `list_pull_requests` state=open → `[]`). Infra
health check ran first — runner HEALTHY (newest `verify_20260724T094103Z`, 09:41Z, ~31 min old at
fire, 46.1 F / 85.5 B / +39.4, all tests green); git on `main` = origin/main (`dcb2a90`, detached
HEAD from the local-verify push realigned).

**Comms.** No Slack — score-neutral additive discovery, moves no score, not a sensitive-class PR;
not a digest window (10:12Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The three DOCUMENTED opt-in free-tier conventions are DISCOVERED and all four
offering surfaces are now read; the remaining COVERAGE frontiers are the [LOCAL] score-increasing
live-wiring (free-tier opt_in_query/opt_in_path into the `advertised` gate; ACP/UCP live handshake
parity) and non-EVM zero-value schemes. A cloud-doable next COVERAGE increment: an [LOCAL] fixture
capture of an OpenAPI-spec-only storefront would let an in-cloud test pin live spec-driven
classification end-to-end (queued P2). Next cycle takes TRUTH.

## Local verification — 20260724T104103Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T104103Z.json

## Cycle 35 (TRUTH) — 2026-07-24T11:12Z — the replay regression guard grows a THIRD real domain: a retail storefront as the transactability floor

**Track.** TRUTH (calibration against reality: does the score reflect what an agent
experiences? — extends the in-cloud regression signal beyond the single canonical pair to a
third, structurally different real domain, and pins the capability-lens claim that
transactability credit tracks agent-native payability, not "is this a store").

**What / why.** The canonical replay guard (`tests/test_canonical_replay.py`) pinned only the
two-domain PAIR (drift-flight.org vs driftflight.com). A benchmark that claims to measure a
real, transferable capability needs more than one pair. We ALREADY hold a committed fixture for
a third real domain — `fixtures/canonical/books.toscrape.com.json`, captured LIVE [LOCAL]
2026-07-24T07:47Z (41 GET / 0 POST, public book catalog) — but it was wired ONLY into the
offering-classifier guard (`test_offering_canonical`, physical_good CLAIMED), never into the
SCORING replay guard. This cycle wires it into the scoring path.

Three tests added (guards 6–8), all reusing the existing `_assert_domain` / `_by_id` /
`_assert_relabel_invariant` machinery, zero new probe/scoring code:

1. **`test_retail_storefront_replays_29_5`** — third-domain calibration pin. Replays the retail
   fixture through the REAL `from_fixture → _run_probes → scoring.score` path and pins overall
   **29.5 F**, rubric **0.7**, all five pillars (access 100 / legibility 18.18 / transactability
   0.0 / trust 33.33 / outcome None), 0 replay-miss. A browser-checkout SHOP (not an API
   storefront) is now in the regression signal, so a scoring change that quietly moved a real
   retail site's number fails here too.
2. **`test_retail_storefront_earns_no_agent_native_payment`** — the MIRROR of the +39.4
   capability guard (Cycle 19/23). A genuine storefront that sells physical goods
   (`physical_good` CLAIMED at the offering layer) earns **EXACTLY 0 transactability** because it
   exposes no agent-native payment rail: `x402_probe` FAIL (not PASS), `self_serve_payg`
   evidence records no live x402, and NO `commerce-protocol-*`/`x402-live` credit is awarded.
   Sharpest fact: scored over the IDENTICAL 14-check set as the no-rails canonical `.org`, the
   retail shop is the transactability FLOOR — it scores STRICTLY LOWER (0.0) than even the
   no-rails API storefront (18.75, which keeps a residual PARTIAL self-serve pay-as-you-go
   signal). The site that most obviously "sells things" earns the LEAST agent-native payability
   → the pillar is capability-gated, not store-type-gated. A probe that credited
   "looks-like-a-shop" (product pages, prices, add-to-cart) as programmatic payability would
   inflate this domain and slip the aggregate guards but FAIL here. Worded by capability, never
   by vendor ("is agent-native payment present?", never "is this domain X?").
3. **`test_relabel_invariance_retail`** — vendor-neutrality (Cycle 21 relabel-invariance)
   extended to the third domain. Relabeling the shop's host everywhere reproduces the identical
   29.5 / F / pillars / per-check statuses (0 replay-miss) → its score depends on recorded
   capability evidence, not identity; discharges the recurring "extend the relabel guard to more
   storefronts" referee-pass item for this real domain.

**Validation / regression.** Full suite **147 → 150**, all 18 files pass (exit 0).
`test_canonical_replay.py` **8/8 → 11/11**. Canonical PAIR unchanged by construction (scoring
path byte-for-byte untouched) AND re-measured: replay guard **46.1 F / 85.5 B / +39.4**, 0
replay-miss; live-corroborated by `verify_20260724T104103Z` (10:41Z, 46.1 F / 85.5 B / +39.4).
The third-domain 29.5 F was independently reproduced offline before pinning (0 replay-miss;
relabel invariance verified: 29.5 F base == relabel, identical pillars/statuses).

**Ship.** Direct to main (tests-only; no scoring semantics — `git diff -- asrs/ rubric/` EMPTY,
rubric stays v0.7). Not payment/signing code.

**Evidence.** `git diff --stat` = `tests/test_canonical_replay.py` ONLY (1 file, +128).
Fixture already committed (books.toscrape.com.json, [LOCAL] 07:47Z). Suite 147 → 150.

**First duty.** No open peer-gated PR (verified `list_pull_requests` state=open → `[]`). Infra
health check ran first — runner HEALTHY (newest `verify_20260724T104103Z`, 10:41Z, ~31 min old at
fire, 46.1 F / 85.5 B / +39.4, tests_ok); git realigned to origin/main (`3e12924`; detached HEAD
from the forced-update local-verify push reset to `main`).

**Comms.** No Slack — tests-only, moves no score, not a sensitive-class PR; not a digest window
(11:12Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The replay regression guard now spans THREE real domains (two API
storefronts + one retail shop) with capability + vendor-neutrality tripwires on each. The
remaining TRUTH frontier is the example.com non-storefront control (a fourth point, the
zero-commerce baseline — still needs a [LOCAL] fixture capture; the test wiring is cloud-doable
once it lands). Next cycle takes READOUT.

## Local verification — 20260724T114105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T114105Z.json

## Local cycle — 2026-07-24T11:48Z — TRUTH: the FOURTH real domain lands — a zero-commerce non-storefront baseline (example.com), captured [LOCAL] + wired in-cloud

**Track.** TRUTH (calibration against reality) — the networked half the cloud cannot run:
captured a live fixture, then converted it into four executable regression guards. Executes the
exact `[LOCAL]` item Cycle 35's "Next hypothesis" named: "the example.com non-storefront control
(a fourth point, the zero-commerce baseline — still needs a [LOCAL] fixture capture; the test
wiring is cloud-doable once it lands)."

**First duty.** No open peer-gated PR (`gh pr list --state open` → `[]`), so no review/merge.
Infra health check ran first — ALL GREEN: newest `verify_20260724T114105Z` (11:41:05Z) was ~36s
old at fire (well under the 6h floor), `tests_ok=true`, live canonical 46.1 F / 85.5 B / +39.4 on
v0.7; full suite green; `main == origin/main` (clean tree). No self-heal needed.

**What / why.** The replay regression guard and the offering-classifier guard both spanned three
real domains (two API storefronts + a retail shop, Cycle 35) — all sites that SELL something. A
benchmark needs the honest floor too: a bare site that sells NOTHING, so the with-rails +39.4
delta is measured against a real low anchor, not just against other storefronts. This lands that
fourth point.

Captured `fixtures/canonical/example.com.json` via a STATIC $0 crawl
(`asrs.cli score example.com --record-fixture …`) — **41 GET / 0 POST, no auth/secret/cookie
tokens** (the plain IANA example page). Live static score **22.5 F** on rubric v0.7, matching the
15:43Z [LOCAL] spot-check. Then wired it into the two in-cloud guards (no new probe/scoring code —
all existing `_assert_domain` / `_by_id` / `_assert_relabel_invariant` / `_discover` machinery):

`tests/test_canonical_replay.py` **11 → 14** (guards 9–11):
1. **`test_nonstorefront_replays_22_5`** — pins overall **22.5 F**, rubric 0.7, all five pillars
   (access 100 / legibility 0.0 / transactability 0.0 / trust 20.0 / outcome None), 0 replay-miss.
   A non-commercial page is now in the regression signal.
2. **`test_nonstorefront_earns_no_agent_native_payment`** — the extreme case of the capability
   mirror: a site with no storefront earns **EXACTLY 0 transactability** and NO payment credit
   (`x402_probe` FAIL not PASS; `self_serve_payg` evidence records no live x402; no
   `commerce-protocol-*`/`x402-live`). Guards against a probe hallucinating an agent-native rail
   from a bare page. Attribution-honesty detail pinned in the docstring: `self_serve_payg` is
   CANT_TEST here (no purchase path to evaluate → honestly EXCLUDED, never penalized), yet
   transactability is still 0 because the payment probe FAILs on recorded evidence-of-absence —
   absence excused where unobservable, scored where observed (invariant #4, both directions).
3. **`test_relabel_invariance_nonstorefront`** — vendor-neutrality (Cycle 21 relabel) extended to
   the fourth domain: relabeling the host everywhere reproduces identical 22.5 / F / pillars /
   per-check statuses (0 replay-miss). Even the floor score keys on evidence, not identity.

`tests/test_offering_canonical.py` **8 → 9** (`test_nonstorefront_empty_offering`): the
offering-layer companion — a site that sells nothing → **EMPTY offering** (0 archetypes claimed,
all six NA), so the offering-relative battery is honestly empty (no fabricated task, no penalty).
Guards the precision-first classifier against inventing an offering from generic prose.

All facts were pinned to the ACTUAL replayed evidence, not the backlog's guess: the backlog
predicted `self_serve_payg` FAIL with `x402_live=False`; the real replay shows it CANT_TEST
(purchase-path-indeterminate) with evidence `x402_live=False` — so the guard asserts the honest
"no live x402 payment" (`is not True`) and the CANT_TEST-but-still-zero attribution nuance above.

**Validation / regression.** Full suite **150 → 154** assertions, all 18 files exit 0.
`test_canonical_replay.py` 11 → 14, `test_offering_canonical.py` 8 → 9. Relabel invariance for
example.com verified empirically before pinning (22.5 F base == relabel, identical
pillars/statuses, 0 replay-miss; offering [] base == relabel). Scoring path byte-for-byte
untouched — `git diff --name-only -- asrs/ rubric/` EMPTY → rubric stays v0.7; canonical PAIR
unchanged by construction AND re-measured (46.1 F / 85.5 B / +39.4, 0 replay-miss;
`verify_20260724T114105Z` live-corroborates).

**Ship.** Direct to main (tests + one committed fixture; no scoring semantics). Not
payment/signing code (the fixture is GET-only, $0). `git diff --stat` = the two test files
(+150) + the new fixture only.

**Budget / constraints.** $0 (one static $0 crawl, zero codex, zero behavioral panels). Nothing
touched outside the repo checkout.

**Evidence.** `fixtures/canonical/example.com.json` (41 GET / 0 POST, committed);
`tests/test_canonical_replay.py`, `tests/test_offering_canonical.py`.

**Comms.** No Slack — tests + fixture, moves no score, not a sensitive-class PR; not a digest
window (11:48Z, before 16:00 UTC; digest last sent Cycle 16).

**Next hypothesis.** The regression + vendor-neutrality signal now spans FOUR real domains across
the full commerce spectrum: two agent-native API storefronts (46.1 / 85.5), a human-only retail
shop (29.5, transactability floor), and a zero-commerce non-storefront (22.5, the honest bottom).
Each carries a capability tripwire + a relabel-invariance tripwire; the offering layer carries the
matching classification guard (physical_good NA / CLAIMED / empty). The remaining offering-layer
gaps are the OpenAPI-spec-only storefront fixture (Cycle-34 follow-up, still synthetic-only
in-cloud) and extending the OFFERING relabel guard to the retail + non-storefront domains. The
top operator P0 — the `--battery auto` behavioral acceptance rerun — remains [LOCAL]: it is over
the ~10-codex budget as specified AND codex env-blocks both canonical domains (adds no battery
data), so a claude-only scoped slice on driftflight.com + a retail control is the budget-respecting
form for a future fire.

## Local verification — 20260724T124104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T124104Z.json

## Local verification — 20260724T134103Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T134103Z.json

## Local verification — 20260724T144105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T144105Z.json

## Local verification — 20260724T154104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T154104Z.json

## Local verification — 20260724T164100Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T164100Z.json

## Local verification — 20260724T174105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T174105Z.json

## Local verification — 20260724T184105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T184105Z.json

## Local verification — 20260724T194105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T194105Z.json

## Local verification — 20260724T204106Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T204106Z.json

## Local verification — 20260724T214106Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T214106Z.json

## Local verification — 20260724T224105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T224105Z.json

## Local verification — 20260724T234106Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260724T234106Z.json

## Local verification — 20260725T044104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T044104Z.json

## Local verification — 20260725T054105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T054105Z.json

## Local verification — 20260725T064102Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T064102Z.json

## Local verification — 20260725T074105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T074105Z.json

## Local verification — 20260725T084105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T084105Z.json

## Local verification — 20260725T094104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T094104Z.json

## Local verification — 20260725T104101Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T104101Z.json

## Local verification — 20260725T114105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T114105Z.json

## Local verification — 20260725T124101Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T124101Z.json

## Local verification — 20260725T134102Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T134102Z.json

## Local verification — 20260725T144105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T144105Z.json

## Local verification — 20260725T154105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T154105Z.json

## Local verification — 20260725T164104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T164104Z.json

## Local verification — 20260725T174105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T174105Z.json

## Local verification — 20260725T184105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T184105Z.json

## Local verification — 20260725T194105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T194105Z.json

## Local verification — 20260725T204105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T204105Z.json

## Local verification — 20260725T214105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T214105Z.json

## Local verification — 20260725T224105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T224105Z.json

## Local verification — 20260725T235528Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260725T235528Z.json

## Local verification — 20260726T060316Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T060316Z.json

## Local verification — 20260726T140344Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T140344Z.json

## Local verification — 20260726T155334Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T155334Z.json

## Local verification — 20260726T170644Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T170644Z.json

## Local verification — 20260726T180143Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T180143Z.json

## Local verification — 20260726T190844Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T190844Z.json

## Local verification — 20260726T200944Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T200944Z.json

## Local verification — 20260726T204104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 78.7 C | delta +32.6 | artifact runs/local/verify_20260726T204104Z.json

## Local verification — 20260726T214104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T214104Z.json

## Local verification — 20260726T224105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T224105Z.json

## Local verification — 20260726T234104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260726T234104Z.json

## Local verification — 20260727T004105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T004105Z.json

## Local verification — 20260727T014104Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T014104Z.json

## Local verification — 20260727T034106Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T034106Z.json

## Local verification — 20260727T044105Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T044105Z.json

## Local verification — 20260727T054339Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T054339Z.json

## Local verification — 20260727T074015Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 50.0 F | delta +3.9 | artifact runs/local/verify_20260727T074015Z.json

## Local verification — 20260727T095143Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 76.2 C | delta +30.1 | artifact runs/local/verify_20260727T095143Z.json

## Local verification — 20260727T134147Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 78.7 C | delta +32.6 | artifact runs/local/verify_20260727T134147Z.json

## Cycle 36 (READOUT) — 2026-07-27T14:21Z — canonical-delta HISTORY readout over the committed live-verify series (+ surfaces a live delta DRIFT)

**Track.** READOUT (readout clarity: turn the 66-artifact committed live-verify
series into a legible canonical-delta TREND with a sustained-drift alert — the
benchmark had no way to READ its own regression signal over time, only per-fire
LOG lines).

**What / why.** The local runner commits `runs/local/verify_<ts>.json` every fire
(a live static re-score of the reference pair). 66 usable artifacts (2026-07-23 →
07-27) are committed, but nothing READ them as a series — a delta move showed up
only as scattered one-line LOG entries. New pure, stdlib-only, read-only module
`asrs/canonical_history.py`:
- `load_points(runs_dir)` parses each verify artifact, SKIPPING malformed ones
  (early pre-Cycle-13 FileNotFoundError artifacts with no `delta`; any run where a
  domain isn't `ok`) — attribution honesty applied to the history (a re-score we
  couldn't observe is not a data point, never a scored zero).
- `summarize()` → `CanonicalHistory`: latest point, `divergence` = live delta −
  fixture baseline (+39.4), a 3-band verdict (in-band ≤2.0 / drifting ≤8.0 /
  diverged), and `consecutive_out_of_band` = the TRAILING run of readings past the
  in-band threshold (1 = jitter, N≥3 = a sustained real-world move — the signal
  that separates a blip from a site change).
- `render()` → terminal block + a delta sparkline; `asrs canonical-history` CLI.
Baseline is a plain constant `FIXTURE_BASELINE_DELTA = 39.4` cross-checked by test
against `test_canonical_replay.EXPECTED_DELTA` (single source of truth — a fixture
re-capture that legitimately moves the delta turns THAT test red, the documented
maintenance contract, so the constant can't silently drift).

**LIVE CANONICAL DRIFT surfaced (capability terms).** The new readout immediately
makes visible a real move: from loop-start through `verify_20260727T054339Z` the
live delta held **+39.4** (46.1 F / 85.5 B) for days; then at the **07:40Z fire
today** driftflight.com collapsed to 50.0 F (delta +3.9, a transient error crawl —
transactability CANT_TEST, legibility 0), recovering to 76.2 C (09:51Z, +30.1) and
**78.7 C (13:41Z, +32.6)**. Latest state: `.com` transactability RECOVERED to 87.5
(= baseline) but **legibility fell 90.9 → 63.6** — the with-rails storefront lost
machine-legibility credit; pillars are still fluctuating fire-to-fire → a
real-world site change (deploy / intermittent availability), NOT a code regression.
drift-flight.org is flat at 46.1 F throughout, so the delta narrowed because the
RAILS side softened, not because the no-rails side improved. Truth outranks the
pitch — this is an honest, legible signal, now a first-class readout. The committed
fixtures STILL pin 46.1/85.5/+39.4, so the in-cloud replay guard is green and the
canonical delta is unchanged BY CONSTRUCTION; this is a LIVE-signal divergence the
fixture-based guard is (correctly) blind to — exactly the gap this readout fills.

**Validation / regression.** Full suite **150 → 156** (new `tests/test_canonical_history.py`
6/6). `test_canonical_replay.py` **11/11** unchanged (canonical PAIR re-measured
46.1 F / 85.5 B / **+39.4**, 0 replay-miss). Scoring path byte-for-byte untouched:
`git diff --name-only -- asrs/scoring.py asrs/probes asrs/fetch.py rubric/
asrs/behavioral asrs/offering.py asrs/battery.py` EMPTY → rubric stays **v0.7**.
Free-tier test 10/10 after `pip install -r requirements.txt` (eth-account). CLI
smoke: `asrs canonical-history` renders the 66-point series, flags "DRIFTING —
3 consecutive re-scores out of band".

**Ship.** Direct to main (new READOUT diagnostic + CLI + tests; no scoring
semantics, not payment/signing). `git diff --stat` = `asrs/cli.py` (+ subcommand)
+ new `asrs/canonical_history.py` + new `tests/test_canonical_history.py`.

**Comms.** No Slack this fire: the SHIP is score-neutral/non-sensitive, and the
live drift is not "something we shipped" — per the playbook comms policy it folds
into the next post-16:00 UTC daily digest (this fire is 14:21Z, before the window).
Recorded prominently in STATE for that digest.

**First duty.** No open peer-gated PR (verified `list_pull_requests` state=open →
`[]`). Infra health check ran first — runner HEALTHY (newest
`verify_20260727T134147Z`, 13:41Z, ~33 min old at fire, tests_ok). NOTE: no CLOUD
cycle fired between Cycle 35 (2026-07-24T11:12Z) and this fire — only the local
verify runner heartbeated for ~3 days; the cloud loop resumed this fire (Cycle 36).
git realigned to origin/main (`7393cc3`; detached HEAD after a forced origin/main
update reset to `main`).

**Next hypothesis.** (1) Pillar-level ATTRIBUTION of a divergence — extend the
readout to name WHICH pillar drove the delta move (here: `.com` legibility), so the
"explain the delta in capability terms" duty is computed, not hand-written. (2) A
[LOCAL] decision, once the `.com` site settles, on whether to re-capture the
canonical fixture (moving the pinned baseline) — deliberately NOT done while the
site is still fluctuating.

## Cycle 37 (METHOD) — 2026-07-27T15:14Z — pillar-level ATTRIBUTION of a canonical divergence: WHICH pillar drove the delta move, computed not hand-written

**Track.** METHOD (measurement rigor — attribution). Cycle 36 surfaced a live
canonical DRIFT and hand-wrote its cause in STATE ("`.com` legibility fell
90.9 → 63.6"). The playbook's per-cycle duty is to "explain the delta in
capability terms" — but that explanation was PROSE a human typed, not a computed
fact. This cycle makes it computed: the readout now names the pillar(s) that
moved, so the attribution is reproducible and cannot silently disagree with the
data.

**What / why.** Extended the read-only diagnostic `asrs/canonical_history.py`
(shipped Cycle 36) so a divergence is attributed to the pillar that drove it:
- `CanonicalPoint` now carries `no_rails_pillars` / `with_rails_pillars` — each
  side's per-pillar overalls (0–100), parsed via `_numeric_pillars`, keeping
  NUMERIC entries only. A pillar recorded `None` (outcome in static mode, or a
  pillar that came back CANT_TEST on an error crawl — e.g. the 07:40Z transient
  where `.com` legibility/transactability were both `None`) is DROPPED, never
  credited a move. Attribution honesty applied to the pillar layer.
- `PillarMove` (domain, pillar, before→after, signed change) + `PillarAttribution`
  (`anchor_ts`, `moves` largest-|change|-first, `.top`).
- `summarize()` computes `CanonicalHistory.attribution` via `_attribute`: ONLY
  when the latest reading is out of band (run ≥ 1) AND an earlier IN-BAND reading
  exists to anchor against — `points[-(run+1)]`, the reading immediately before
  the trailing out-of-band run, in-band by that run's stopping condition. When the
  ENTIRE series is out of band (no stable baseline ever observed live), or the
  latest is in-band (nothing to explain), attribution is honest `None` — the same
  discipline the loader applies to unobserved runs.
- `render()` adds an `attribution (vs last in-band <ts>): <domain> <pillar>
  fell/rose X → Y (±Δ) — the largest pillar move` line (+ up to 2 secondary
  movers), only when attribution is present.

**Validation.** Run against the REAL committed 66-artifact series, the computed
attribution reproduces the Cycle-36 hand-written note EXACTLY:
`attribution (vs last in-band 2026-07-27T05:43Z): driftflight.com legibility fell
90.9 → 63.6 (-27.3) — the largest pillar move`. The flat pillars (`.org` all
pillars, `.com` transactability/access/trust) are correctly NOT reported as movers.

**Canonical pair.** Score-neutral: `git diff --name-only` = `asrs/canonical_history.py`
+ `tests/test_canonical_history.py` ONLY; scoring.py/rubric/probes/fetch/protocols/
behavioral/offering/battery byte-for-byte untouched (`git diff` over them empty) →
rubric stays **v0.7**, canonical PAIR unchanged by construction AND re-measured
(in-cloud replay guard 11/11, **46.1 F / 85.5 B / +39.4**, 0 replay-miss). The
LIVE `.com` drift (78.7 C, delta +32.6, DRIFTING) is unchanged by this cycle — the
fixture guard is (correctly) blind to it; this cycle just makes the readout NAME
its cause. `asrs/canonical_history.py` imports no scoring code (read-only over
committed artifacts); the reference-pair hosts appear only as DATA (existing module
constants), never as scored-check wording — vendor-neutral.

**Tests.** `test_canonical_history.py` 6 → 10 (+4): (1) a synthetic mirror of the
real drift asserts the top mover is `.com` legibility −27.3 and the flat pillars
are NOT movers (non-vacuous); (2) an in-band series → attribution `None`, render
omits it; (3) a latest reading with legibility `None` (unobserved) → legibility is
NOT attributed, the next observed mover wins, AND an all-out-of-band series → honest
`None` (no anchor); (4) the REAL committed series, guarded, fingers `.com` as the
drifting side (skips cleanly if the site recovers to in-band). Suite 156 → 160.

**Ship.** Direct to main (READOUT/METHOD diagnostic + tests; no scoring semantics,
not payment/signing). Per playbook ship rules (docs/readout/tests → direct).

**Comms.** No Slack this fire: score-neutral/non-sensitive. This fire is 15:14Z;
the first-cycle-after-16:00-UTC daily digest still owes a report on the live
canonical drift (open since Cycle 36) + this computed-attribution ship — folded
into that digest when the next cycle crosses the window.

**First duty.** No open peer-gated PR (`list_pull_requests` state=open → `[]`).
Infra health check ran FIRST — ALL GREEN: runner HEALTHY (newest
`verify_20260727T134147Z`, 13:41Z, ~1.5h old at fire, tests_ok, 66 usable points);
bench runnable, full suite 156/156 pre-change (now 160/160); git realigned to
origin/main (`dd449d4` = Cycle 36; detached HEAD after the forced-update local-verify
push reset to `main`).

**Next hypothesis.** (1) Surface the computed attribution on an HTML trend surface
(the Cycle-36 "score-over-time trend page" READOUT item — the terminal block +
attribution rendered into the scorecard / a standalone page). (2) [LOCAL] decision,
still deferred: whether to re-capture the `.com` canonical fixture once the live
series reads in-band-stable at a NEW level for several consecutive fires (do NOT
re-capture while fluctuating).

## Cycle 38 (COVERAGE) — 2026-07-27T16:13Z — free-tier opt-in DISCOVERY broadened to a FOURTH convention: the JSON request-body field

**Track.** COVERAGE (measurement coverage/flexibility — the north-star
many-conventions axis). Three DOCUMENTED opt-in conventions were already
discovered in-cloud, score-neutral: the request header (pre-Cycle-22), the URL
query parameter (Cycle 22, `_scan_query_param_instruction`), and the URL path
segment (Cycle 30, `_scan_path_instruction`). A real fourth convention — a
storefront that documents its free tier as a JSON field in the REQUEST BODY
(`{"tier": "free"}` / `{"mode": "free"}` / `{"free_tier": true}`) — was
UNRECOGNISED (currently mis-discovered as "opt-in-undiscoverable"). This cycle
adds `asrs/behavioral/free_tier.py` `_scan_body_field_instruction` + an additive
`FreeTierDiscovery.opt_in_body: tuple[str,str]|None` field + an `opt_in_body`
evidence key, populated by `discover_free_tier`.

**What / why.** Precision-first, vendor-neutral, mirroring the sibling scanners:
- The load-bearing distinguisher from the header scanner (which reads a bare
  `Name: value`) is the **in-object gate** — a body field must be a
  DOUBLE-QUOTED JSON key sitting inside an open `{…}` object literal (nearest
  unmatched brace before it is a `{`). So a header `` `zc-mode: free` `` and a
  query `?tier=free` are never misread as a body field (verified: both → None).
- Free-context gate (must sit near free-allowance prose) + an explicit "free"
  hint in name or value (stricter, like the query-param scanner — no "mode"
  fallback), so `{"tier": "starter"}` near free prose is NOT the opt-in.
- Plumbing body-field denylist (`prompt`/`model`/`api_key`/…) so
  `{"model": "free-tier-v2"}` is skipped even worded with "free".

**DELIBERATELY SCORE-NEUTRAL** (the load-bearing invariant, same as Cycles
22/30): `opt_in_body` is NOT in the `advertised` gate and NOT consumed by the
live-call path — the gate reads only `header` + `free_units`. Test-pinned via the
`{"free_tier": true}` fixture the HEADER scanner does NOT also catch (its regex
needs `name: value` and stops at the underscore): body-only doc keeps
`advertised=False`; adding a body field to the header+manifest fixture leaves
`advertised` byte-for-byte identical (True→True). Live wiring (fold `opt_in_body`
into `advertised` + the free-mode call) is score-INCREASING → queued [LOCAL]
alongside the query-param/path halves (invariant #3, verify on ≥2 real domains).

**OBSERVATION (queued, not fixed here).** The existing HEADER scanner
OVER-CATCHES a `{"tier": "free"}` body field as a header (its `name: value` regex
matches a double-quoted JSON key too). This is PRE-EXISTING (not introduced here)
and `opt_in_body` is never read by the gate regardless, so it moves no score —
but disambiguating the header scanner from JSON body fields is score-affecting
(header IS gated) → queued P1 as a peer-gated/[LOCAL] follow-up.

**Not payment/signing code.** Diff confined to the discovery region;
`parse_challenge`/`_settle_zero_value`/`_build_transfer_authorization_typed_data`/
`new_ephemeral_address_and_signer`/`probe_free_tier` byte-for-byte unchanged (the
$0-only nonzero-refusal safety property untouched — grep of the diff over those
fns empty; the "sign"/"amount" hits in the diff are all new comments).

**Canonical pair.** No scoring semantics, rubric stays **v0.7**. `git diff
--name-only` over scoring.py/rubric/probes/fetch/protocols/offering/battery/
scorecard EMPTY → canonical delta unchanged by construction AND re-measured
(in-cloud replay guard 11/11, **46.1 F / 85.5 B / +39.4**, 0 replay-miss).
free_tier runs only in behavioral mode (off the static scoring path the replay
guard exercises). LIVE `.com` drift (78.7 C, delta +32.6, DRIFTING) unchanged by
this cycle — see the open note in STATE / the digest below.

**Tests.** `tests/test_free_tier.py` 10 → 11 (+`test_body_field_optin_discovery`:
3 extraction forms, 5 negative controls — header/query/not-in-object/plumbing/
non-free-field, evidence surfacing, and the score-neutrality pair). Suite
160 → 161 (19 files, all exit 0).

**Ship.** Direct to main (additive discovery, no scoring semantics, not payment/
signing; `git diff --stat` = free_tier.py + test_free_tier.py only). Per playbook
ship rules (probe additions that don't change scoring semantics → direct).

**First duty.** No open peer-gated PR (`list_pull_requests` state=open → `[]`).
Infra health check ran FIRST — ALL GREEN: runner HEALTHY (newest
`verify_20260727T134147Z`, 13:41Z, ~2.5h old at fire); bench runnable, full suite
160/160 pre-change (now 161/161); git realigned to origin/main (`f4cb756` =
Cycle 37; detached HEAD after the forced-update local-verify push reset to `main`).

**Comms.** DAILY DIGEST DM SENT this fire — first cycle after 16:00 UTC
(16:13Z; Cycle 37 was 15:14Z, before the window). Carries the still-open LIVE
CANONICAL DRIFT (open since Cycle 36) + this ship.

**Next hypothesis.** COVERAGE frontier remaining after all four DOCUMENTED opt-in
conventions (header/query/path/body) are now discovered in-cloud: (1) the shared
[LOCAL] live-wiring (fold query/path/body into `advertised` + the live call,
verify ≥2 domains); (2) non-EVM zero-value schemes (still open); (3) the P1
header-scanner-vs-JSON-body disambiguation surfaced above. Next cycle takes TRUTH.

## Cycle 39 (TRUTH) — 2026-07-27T17:13Z — canonical divergence attributed to a SIDE: no-rails gaining vs with-rails softening, computed not hand-written

**Track.** TRUTH (calibration against reality — does the score honestly explain
what changed under the benchmark?). The playbook's per-cycle duty is to "explain
the delta in capability terms." Cycle 37 made the PILLAR computed (`.com`
legibility fell 90.9→63.6). But the STATE drift note still HAND-WROTE the
credibility-critical fact one layer up: *"the delta narrowed because the RAILS
side softened, not the no-rails side improving."* The reference delta can narrow
two OPPOSITE ways — (a) the no-rails floor GAINING capability (the real gap is
genuinely closing → a benchmark movement, a re-capture candidate when durable),
or (b) the with-rails reference LOSING ground (a real-world site regression → the
pinned fixture still represents the TRUE gap, so re-capture should WAIT for
recovery). Conflating them mis-tells the operator what to do. This cycle makes
the SIDE-and-direction attribution COMPUTED.

**What shipped.** Extended the read-only `asrs/canonical_history.py` (Cycle 36/37):
- `DivergenceCause` (`anchor_ts`, `no_rails_change`, `with_rails_change` — each
  side's OVERALL score move vs the last in-band reading) with properties
  `gap_change` (= change in the delta, sign = narrow/widen), `driver` (the side
  whose overall moved more; ties → no-rails, read conservatively as gap movement),
  `driver_change`, and `reference_degraded` (True iff the with-rails reference LOST
  ground — the crisp signal for the deferred re-capture decision).
- `_cause(points, run, latest)` — SAME anchor/gate as `_attribute` (out of band +
  an in-band anchor exists), from each side's OVERALL score (numeric on every
  scored artifact, so it's defined even where per-pillar attribution is empty →
  never None-on-one-side). `CanonicalHistory.divergence_cause`.
- `cause_verdict(cause)` — a capability-lens sentence keyed on (driver, direction),
  the four honest cases; because the driver dominates, its direction fixes
  narrow/widen so the sentence never contradicts `gap_change`. `render` prints a
  `driver:` line after the attribution line.

On the REAL committed series it reproduces the Cycle-36/STATE hand-write EXACTLY:
`driver: driftflight.com overall fell -6.8 — the gap narrowed because the
with-rails reference SOFTENED (a real-world site change), not because the no-rails
side gained capability — the pinned fixture still represents the true gap`
(no-rails change 0.0, with-rails change -6.8, gap_change -6.8, reference_degraded
True). So the "which side, and does the gap really close" duty is now COMPUTED,
not hand-written — the same move Cycle 37 made for the pillar.

**Non-vacuous.** A cause blind to DIRECTION would call both narrowing cases "the
gap narrowed." The +test pins the OPPOSITE case (no-rails side RISES 46.1→53.0,
with-rails flat) → `driver == no-rails`, `reference_degraded False`, render reads
"GAINED capability — a real benchmark movement, not a reference outage." In-band
series → `divergence_cause None`, render omits the `driver:` line. Real-series
test is recovery-guarded (asserts the with-rails softening only WHILE out of band).

**Vendor-neutral.** Imports no scoring code; the reference-pair hosts appear only
as DATA via the module's existing `CANONICAL_*` constants (the series is *about*
those two domains, exactly as the committed fixtures name them) — never as
scored-check wording.

**Canonical pair.** Score-neutral: `git diff --name-only` = `canonical_history.py`
+ `test_canonical_history.py` ONLY; scoring.py/rubric/probes/fetch/protocols/
behavioral/offering/battery/scorecard byte-for-byte untouched → rubric stays
**v0.7**, canonical delta unchanged by construction AND re-measured (in-cloud
replay guard 11/11, **46.1 F / 85.5 B / +39.4**, 0 replay-miss). The LIVE `.com`
drift (78.7 C, delta +32.6, DRIFTING) is unchanged by this cycle — this ships the
computed READING of it, not a change to it.

**Tests.** `tests/test_canonical_history.py` 10 → 13 (+`test_divergence_cause_
names_the_softening_side` w/ the opposite-direction non-vacuous control,
`test_divergence_cause_none_when_in_band`, `test_divergence_cause_on_real_series`
recovery-guarded). Suite 161 → 164 (19 files, all exit 0). NOTE: fresh cloud
checkout runs `test_free_tier.py` 11/11 only after `pip install eth-account`
(requirements pins it) — the standing invariant-#4 env gap, closed by the install.

**Ship.** Direct to main (read-only diagnostic / READOUT-layer, no scoring
semantics, not payment/signing). Per playbook ship rules (readout + tests → direct).

**First duty.** No open peer-gated PR (`list_pull_requests` state=open → `[]`).
Infra health check ran FIRST — runner HEALTHY (newest `verify_20260727T134147Z`,
13:41Z, ~3.5h old at fire, under the 6h floor); bench runnable, full suite
161/161 pre-change (now 164/164); replay guard 11/11 / +39.4. WATCH: the :41
fires at 14/15/16:41Z produced no artifact (3 consecutive gaps at this fire, as at
Cycle 28) — still under the 6h floor, a possible fresh runner stall to watch; if
still gapped past 6h next fire, flag + fold into the next digest.

**Comms.** No Slack (tests + read-only diagnostic, moves no score, not sensitive;
the daily digest was already sent Cycle 38 at 16:13Z — this fire 17:13Z is not a
new digest window). The open LIVE CANONICAL DRIFT is now more fully diagnosed
in-cloud (side + direction + pillar all computed) for the NEXT digest.

**Next hypothesis.** The canonical-history readout now computes: delta trend,
band, sustained-drift run, PILLAR attribution (Cycle 37), and SIDE/direction cause
(this cycle). READOUT frontier: render this trend + attribution + cause into an
HTML surface (the scorecard / a standalone page) so a reader eyeballs the curve +
the named mover, not just the terminal (P2 "Score-over-time trend page" (a) /
Cycle-37 follow-up). Next cycle takes READOUT.

## Local cycle — 2026-07-27T18:11Z — TRUTH: reconcile a lost ship — the zero-commerce baseline (example.com) code lands (its LOG was committed 07-24, its code was not)

**Track.** TRUTH (calibration against reality) via SELF-HEALING (bookkeeping
repair). This fire's one item was to reconcile a LOG/git inconsistency and ship
the code the committed history already claimed — the exact `[LOCAL]`
"Third-control-domain replay fixture" backlog item, whose fixture capture is the
networked half only a local fire can do.

**Root cause (what was inconsistent).** The committed `loop/LOG.md` carries a
detailed `## Local cycle — 2026-07-24T11:48Z` entry describing the example.com
zero-commerce baseline as SHIPPED (fixture + four test cases, suite 150→154). But
the actual code was never committed: that 07-24 fire authored `fixtures/canonical/
example.com.json` + the tests and wrote its LOG entry to disk, then only `LOG.md`
was swept into a commit — by the fixed-verb verify runner's `2cf0cef "loop: local
verification 20260724T124104Z"` (which force-adds `loop/*.md` + its `runs/local/
verify_*.json`), NOT by the fire itself. `git log -S test_nonstorefront_replays_22_5`
resolves ONLY to `2cf0cef` because the test *names are quoted in the LOG prose*; no
commit on any branch ever added the test *file* change or the fixture. The cloud loop
was then paused ~3 days (07-24→07-27; Cycle 36's note confirms no cloud cycle fired
between Cycle 35 and 14:21Z today), so the WIP sat uncommitted in the working tree
while the committed LOG claimed the ship — a bookkeeping-down condition
(LOG/STATE inconsistent with git history) the self-healing law says to repair FIRST.

**First duty.** No open peer-gated PR (`gh pr list --state open` → `[]`) — nothing
to review/merge. Infra health: see INFRA WATCH below.

**Git hygiene (handled before any edit).** This checkout's `main` was 4 commits
behind — cloud Cycles 36 (READOUT canonical-delta history), 37 (METHOD pillar
attribution), 38 (COVERAGE free-tier body-field discovery), 39 (TRUTH divergence
side/direction) had shipped to `origin/main` (0757fa1) while local sat at the 13:41Z
verify commit (7393cc3). Confirmed origin does NOT already carry the example.com
work (no duplicate), stashed the WIP (incl. the untracked fixture), fast-forwarded
to origin/main, restored the WIP cleanly (origin never touched any of the three WIP
files → no conflict).

**What / why.** Re-validated the surviving WIP against the CURRENT suite (not just
07-24's), then committed it. The regression + vendor-neutrality signal now spans
FOUR real domains across the full commerce spectrum — two agent-native API
storefronts (46.1 / 85.5), a human-only retail shop (29.5, transactability floor),
and a zero-commerce non-storefront (22.5, the honest bottom anchor) — so the
with-rails +39.4 delta is measured against a real low anchor, not only other
storefronts. Landed exactly as the 07-24 entry described:

`tests/test_canonical_replay.py` **11 → 14**:
1. `test_nonstorefront_replays_22_5` — pins overall **22.5 F**, rubric 0.7, all five
   pillars (access 100 / legibility 0.0 / transactability 0.0 / trust 20.0 / outcome
   None), 0 replay-miss. A non-commercial page joins the regression signal.
2. `test_nonstorefront_earns_no_agent_native_payment` — the capability-floor MIRROR:
   a site with no storefront earns EXACTLY 0 transactability and NO payment credit
   (`x402_probe` not PASS; `self_serve_payg` records no live x402; no
   `commerce-protocol-*`/`x402-live`). Attribution-honesty nuance pinned: here
   `self_serve_payg` is CANT_TEST (no purchase path → honestly EXCLUDED, never
   penalized) yet transactability is still 0 because the payment probe FAILs on
   recorded evidence-of-absence — absence excused where unobservable, scored where
   observed (invariant #4, both directions). Verified live in the test run.
3. `test_relabel_invariance_nonstorefront` — vendor-neutrality (Cycle 21 relabel)
   extended to the fourth domain: relabeling the host everywhere reproduces identical
   22.5 / F / pillars / per-check statuses, 0 replay-miss.

`tests/test_offering_canonical.py` **8 → 9** (`test_nonstorefront_empty_offering`):
the offering-layer companion — a site that sells nothing → EMPTY offering
(`archetypes == []`, all six NA), so the offering-relative battery is honestly empty
(no fabricated task, no penalty); guards the precision-first classifier against
inventing an offering from generic prose.

**Fixture provenance / safety.** `fixtures/canonical/example.com.json` — 41 GET /
**0 POST** (a pure static $0 crawl of the plain IANA example page), all requests
on-domain (example.com), secret-pattern scan clean (no `sk-`/`AKIA`/`ghp_`/PRIVATE
KEY). Invariant #1 clean — GET-only, no signing/payment path. Not re-captured this
fire (the committed fixture replays deterministically; spending nothing, and the
canonical-drift lesson "don't re-capture while a signal fluctuates" applies to live
signals, not to a stable committed control).

**Validation / regression.** Full suite **164 → 168** individual tests, all 19 files
exit 0 (`test_canonical_replay.py` 11→14, `test_offering_canonical.py` 8→9; every
other file unchanged). Scoring path byte-for-byte untouched —
`git diff --name-only -- asrs/ rubric/` EMPTY → rubric stays **v0.7**; canonical
PAIR unchanged by construction AND re-measured (replay guard 14/14, **46.1 F /
85.5 B / +39.4**, 0 replay-miss). Orthogonal to the open LIVE CANONICAL DRIFT: that
is a real-world change in the with-rails `.com` site read off the LIVE verify series;
this touches no canonical fixture and no scoring code, so it neither affects nor is
affected by the drift decision (fixture re-capture stays deferred [LOCAL]).

**Ship.** Direct to main (tests + one committed fixture; no scoring semantics; not a
sensitive class). Files: `tests/test_canonical_replay.py`, `tests/test_offering_canonical.py`,
`fixtures/canonical/example.com.json`, plus bookkeeping (`loop/{LOG,STATE,BACKLOG}.md`).
The 07-24 LOG entry is left UNEDITED (invariant #5, append-only); this entry records
the reconciliation.

**Budget / constraints.** $0 — zero codex, zero behavioral panels, zero live crawls
(offline replay validation only). Nothing touched outside the repo checkout.

**Evidence.** `fixtures/canonical/example.com.json` (41 GET / 0 POST, committed this
fire); the two test files; suite output 168/168; `git diff -- asrs/ rubric/` empty.

**Comms.** No Slack — tests + fixture, moves no score, not a sensitive-class PR; the
daily digest already went out Cycle 38 (16:13Z today), and the canonical drift it
carried is unchanged by this fire. The verify-runner git_pull failures are a transient
network blip (github reachable again this fire), under the 6h floor — a STATE watch,
not yet a flag.

**Next hypothesis.** With the four-domain scoring-layer guards complete, the nearest
TRUTH/METHOD frontier is the OFFERING-layer relabel guard, which still covers only the
canonical pair — extend `test_offering_canonical` relabel-invariance to
`books.toscrape.com` (retail) and `example.com` (non-storefront), now that both
fixtures are committed and cloud-doable (no capture needed). Separately, the top
operator P0 — the `--battery auto` behavioral acceptance rerun — remains [LOCAL] and
is best run as a budget-respecting claude-only slice once the with-rails `.com` site
settles out of its current live drift (running it mid-drift would fold real-world
`.com` softening into the acceptance read).

## Cycle 40 (READOUT) — 2026-07-27T18:14Z — live canonical-delta HISTORY as an HTML surface

**What.** The `asrs canonical-history` diagnosis is now an HTML page, not
terminal-only. New `asrs/scorecard.py` `_write_canonical_history_page(out_dir,
history=None)` renders `canonical-history.html` next to every card (published by
`build_scorecard` alongside rubric/methodology, cross-linked from the card
footer). It surfaces the FULL diagnosis the read-only `asrs.canonical_history`
module computes off the committed `runs/local/verify_*.json` series: latest
reading (both sides + grades + delta), divergence from the pinned-fixture
baseline + band verdict, the sustained-drift run, PILLAR attribution (Cycle 37 —
which pillar moved) AND the SIDE/direction cause (Cycle 39 — no-rails gaining vs
with-rails softening). Plus a single-series delta-over-time SVG trend
(`_history_trend_svg`): the live delta per re-score against a dashed
pinned-fixture baseline, each point colored by its divergence BAND, latest point
direct-labeled, band legend below. Added a public `canonical_history.band_for_delta`
so the terminal block and the chart classify a point by the SAME thresholds (one
source of truth).

**Why.** READOUT north star: the benchmark can now READ its own regression signal
over time, but only in a terminal. This lets a reader EYEBALL the curve, the named
pillar mover, and which SIDE drove the drift — the last terminal→HTML gap for the
canonical-history diagnostic (the same terminal→JSON→HTML deferral per_kind /
between_kind / NA-block took). Cycle 39 flagged this as the next-cycle hypothesis.

**Design (dataviz skill loaded).** Form = change-over-time, ONE series → no legend
for identity (title names it); per-point BAND is a reserved STATUS encoding, so it
ships with a named band legend (never color-alone). Status inks in-band #067647 /
drifting #b54708 / diverged #b42318, distinct + labeled. Baseline as a dashed
reference line; recessive connecting line; 2px white ring per dot; direct-label
the latest point only. Rendered + eyeballed via Chromium (SVG coords verified
within plot bounds; no collisions/overflow).

**Vendor-neutrality.** The page names the reference-pair hosts as DATA — it is
literally ABOUT those two domains, exactly as the committed fixtures, the verify
series, and `test_canonical_replay` name them. SAME engineering-history category
as `rubric.html`: deliberately OUT OF SCOPE for the vendor-neutral-wording scanner
(which guards capability-worded CHECK prose on methodology + card, NOT pages that
report on the reference pair). `test_readout_wording` unchanged and still green
(it scans card/methodology, uses rubric.html as its non-vacuous control); the new
page is documented + test-pinned as intended-naming so a future cycle doesn't
mis-fold it into the scanner.

**Validate.** Score-neutral: `git diff --name-only` = `asrs/canonical_history.py`
+ `asrs/scorecard.py` + `tests/test_readout.py` ONLY; scoring.py/rubric/probes/
fetch/protocols/battery/offering/behavioral byte-for-byte untouched (grep clean)
→ rubric stays v0.7, canonical PAIR unchanged by construction AND re-measured
(in-cloud replay guard 11/11, **drift-flight.org 46.1 F / driftflight.com 85.5 B /
delta +39.4**, 0 replay-miss). `canonical_history.py` change is additive
(`band_for_delta`, read-only, imports no scoring code). `test_readout.py` 23 → 29
(+6: page written+linked by build_scorecard; drift diagnosis rendered; in-band
non-vacuous control shows no drift/attribution markup; SVG band-coloring +
baseline + latest-label; empty-series graceful; names-pair-as-data). Full suite
**168 → 174** (all 19 files exit 0; the +6 is this cycle's readout tests — the
168 base already includes the concurrent 18:11Z local fire's example.com +4,
rebased under this commit; in isolation off the pre-local-fire 164 base this
change is 164 → 170).

**Live-signal note (unchanged by this cycle).** The page reads the LIVE series:
current `.com` 78.7 C, delta **+32.6**, DRIFTING (3 consecutive out-of-band; `.com`
legibility 90.9 → 63.6 the named mover; with-rails side SOFTENED). Committed
fixtures still pin +39.4 so the replay guard is (correctly) green; this is a
LIVE-signal divergence the fixture guard is blind to by construction — the open
drift, now readable both in-terminal and on the card.

**Ship.** Direct to main (READOUT, display-only, no scoring semantics, not
payment/signing). Per playbook ship rules (readout + tests → direct).

**First duty.** No open peer-gated PR (`list_pull_requests` state=open → `[]`).
Infra health check ran FIRST — runner HEALTHY (newest `verify_20260727T134147Z`,
13:41Z, ~4.5h old at fire, under the 6h floor); bench runnable, full suite
168/168 pre-change post-rebase (now 174/174); replay guard 11/11 / +39.4. git realigned
(detached HEAD from a forced origin/main update reset to main = origin/main
`0757fa1`). WATCH: the :41 fires at 14/15/16/17:41Z produced no artifact (4
consecutive gaps at this fire — the stall Cycle 39 flagged persists) but newest is
still only ~4.5h old, under the 6h floor; if still gapped past 6h next fire, flag
+ fold into the next digest.

**Comms.** No Slack (READOUT display-only + tests, moves no score, not sensitive;
the daily digest was already sent Cycle 38 at 16:13Z — this fire ~18:14Z is not a
new digest window). The open LIVE CANONICAL DRIFT (now surfaced on the card too)
folds into the next digest.

**Next hypothesis.** The canonical-history diagnosis now ships on the card. Next
READOUT increments (P2): (a) a `compare`-card delta → this history page cross-link
(a reader on a large delta jumps straight to "is this drift or the true gap?");
(b) per-DOMAIN history beyond the canonical pair once other domains have committed
dated reports. Next cycle takes METHOD.

## Local verification — 20260727T184100Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T184100Z.json

## Cycle 41 (METHOD) — 2026-07-27T~19:30Z — offering-layer vendor-neutrality guard extended to all four real domains

**What.** The domain-relabeling invariance (vendor-neutrality) guard on the
OFFERING / task-selection layer now covers all four committed real domains, not
just the canonical pair. `tests/test_offering_canonical.py` +2 tests (9 → 11):
`test_offering_relabel_invariance_retail` (books.toscrape.com → claimed
`{physical_good}`, all else NA, identity-invariant) and
`test_offering_relabel_invariance_nonstorefront` (example.com → honest-empty
offering, every archetype NA, identity-invariant — renaming a bare page invents
no offering). A new shared helper `_assert_offering_relabel_general(domain,
expected_claimed)` relabels the whole fixture to `vendor-neutral.test` and asserts
the CLAIMED (ordered) + NA sets are byte-identical to the un-relabeled discovery
through the REAL `FetchContext.from_fixture → discover_offering` path.

**Why.** METHOD / recurring adversarial-referee-pass leg (b). The SCORING-layer
relabel guard (`test_canonical_replay.py`) already spans all four real domains
(org/com/retail/non-storefront) since Cycle 35 + the 18:11Z reconcile, but the
OFFERING classifier — which drives the operator directive's task SELECTION (which
archetypes get intents) and NA semantics (which are excused, never penalized) —
was relabel-guarded only on the pair (Cycle 31). A book catalog's task set and a
bare page's empty offering must be identity-independent exactly as the pair's is;
this makes "no special-casing any domain, favorable or hostile" an executable
tripwire on the task-selection layer for all four.

**Honest non-vacuity (why the form differs from the pair).** The pair's invariance
tests anchor non-vacuity on the host appearing inside a matched evidence QUOTE (the
`metered_api` post-endpoint quote is literally `POST https://<host>/…`). That does
NOT hold for the two new domains — retail `physical_good` rests on host-free prose
anchors ("In stock" / "Add to basket") and the non-storefront claims nothing — which
is exactly why the retail-inverse fixture originally landed WITHOUT a relabel case
(a quote-anchored relabel would be vacuous there). The new helper anchors non-vacuity
honestly on the FETCHED SURFACES the classifier reads: it asserts the host is present
in the fixture (`domain in raw`) and that `_discover_relabeled` rewrites every
occurrence, so the relabel genuinely changes classifier input. The empty-offering
test additionally pins the full-NA partition invariant (all six archetypes unclaimed
before AND after) — a concrete non-empty structure, not a degenerate constant, and
the retail/pair invariance tests in the SAME suite prove the classifier is not a
constant all-NA function. The pre-existing `test_offering_relabel_negative_control`
(an identity-keyed special-case IS caught by the `_discover` vs `_discover_relabeled`
divergence these tests share) continues to give the machinery teeth.

**Validate.** Tests-only: `git diff --stat` = `tests/test_offering_canonical.py`
only (+110); `git diff --name-only -- asrs/ rubric/` EMPTY → scoring.py/rubric/
probes/fetch/offering.py byte-for-byte untouched → rubric stays v0.7, canonical
PAIR unchanged by construction AND re-measured (in-cloud replay guard 14/14,
**drift-flight.org 46.1 F / driftflight.com 85.5 B / delta +39.4**, 0 replay-miss).
`test_offering_canonical.py` 9 → 11; full suite **174 → 176** (all 19 files exit 0).
Direct-to-main.

**First duty.** No open peer-gated PR (`list_pull_requests` state=open → `[]`).
Infra health check ran FIRST — runner HEALTHY (newest `verify_20260727T184100Z`,
18:41Z, fresh, well under the 6h floor) AND the LIVE CANONICAL DRIFT has RECOVERED:
that artifact reads driftflight.com back at **85.5 B** (legibility 90.9,
transactability 87.5 — both at baseline), delta **+39.4** in-band, self-cleared from
the ~78.7 C drift. Bench runnable after `pip install -r requirements.txt` closed the
known `eth-account` env gap (`test_free_tier.py` 10/11 → 11/11 — invariant-#4 env
gap, pre-existing, unrelated to this change). git realigned (detached HEAD from the
forced origin/main verify push reset to main = `da99fb7`).

**Comms.** No Slack (METHOD tests-only, moves no score, not sensitive; the daily
digest was already sent Cycle 38 at 16:13Z — this fire is not a new digest window).
The live drift RECOVERY (now in-band +39.4) is a positive note for the next digest,
not a flag.

**Next hypothesis.** The OFFERING-layer relabel guard now matches the SCORING-layer
guard's four-domain coverage. Remaining referee-pass frontier: the header-scanner /
JSON-body over-catch disambiguation (P1, score-affecting → peer-gated + [LOCAL]
live-verify) and the env-block site-side "safety policy" hardening (P1, peer-gated +
version bump) are the next METHOD units, both needing more than a tests-only ship.
Next cycle takes COVERAGE.

## Local verification — 20260727T194100Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T194100Z.json

## Cycle 42 — 2026-07-27T20:16Z — COVERAGE

**What.** Offering relevance discovery now reads a FIFTH agent-facing surface —
the agent-plugin descriptor `/.well-known/ai-plugin.json`. `asrs/offering._SURFACE_DOCS`
gains that path (ordered after the natural-language docs, before the OpenAPI
contract). Brick 1 read the homepage + natural-language docs (llms.txt / llms-full /
manifest); Cycle 34 added the machine API CONTRACT (OpenAPI / Swagger). The
descriptor is a distinct surface CLASS: the open, vendor-neutral manifest a
storefront publishes so an AI agent knows what it is and how to use it. Its
`description_for_model` / `description_for_human` fields are a hand-written,
model-facing SUMMARY of the offering — exactly the natural-language commerce /
capability prose ("inference API", "generate an image", "pay-per-generation",
"usage-based", x402) the existing signal bank already anchors on. So the surface
only had to be READ; it needs NO new signal. A storefront may serve a rich
descriptor even when its OpenAPI summaries are one-liners, so reading it improves
recall for the north-star "reach the site, understand the offer" capability.

**Why.** The operator directive (2026-07-23) wants offering discovery "super flexible
and generalized". An agent-native storefront's FIRST self-description to an agent is
increasingly its plugin/tool descriptor, not a marketing homepage — and a
descriptor-only site (no homepage/llms.txt/reachable spec) was classified from
whatever else it served and could be mis-read as offering nothing (the exact
mis-classification Cycle 34's OpenAPI addition fixed for spec-only sites). This is
the same failure mode for the descriptor surface.

**Score-neutral by construction.** `discover_offering` is called ONLY from
`cli._resolve_battery` (`--battery auto`), NEVER on the scoring path
(grep-verified: not referenced in `scoring.py` or `probes/`; the commerce-manifest
SCORING probe keeps its own separate `protocols._AGENT_SURFACE_DOCS`, deliberately
untouched — adding a surface there would be score-increasing + peer-gated).
`git diff --name-only -- asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py
asrs/protocols.py asrs/battery.py` EMPTY → rubric stays **v0.7**. Not payment/signing
code — discovery is read-only `ctx.get` GETs ($0, invariant #1 clean; no POST/sign/
settle added, diff grep clean). Direct-to-main.

**Canonical pair.** drift-flight.org **46.1 F** / driftflight.com **85.5 B** / delta
**+39.4** — unchanged by construction AND re-measured: in-cloud replay guard
`test_canonical_replay.py` 14/14 (0 replay-miss), live-corroborated by
`verify_20260727T194100Z` (19:41Z, in-band). The committed canonical fixtures were
captured before this surface existed, so `/.well-known/ai-plugin.json` is a
replay-miss (absent) on them → the canonical OFFERING guard `test_offering_canonical.py`
is byte-identically **11/11 UNCHANGED** (same property Cycle 34 relied on).

**Scope / evidence.** `asrs/offering.py` (surface list + docstrings) +
`tests/test_offering.py` ONLY. `test_offering.py` 9 → 10 (+`test_ai_plugin_descriptor_alone_classifies_storefront`:
a descriptor-only storefront classifies metered_api + digital_good from real anchored
descriptor evidence — 5 distinct signals — with physical_good / subscription correctly
NOT claimed; the wiring guard `test_openapi_surface_is_wired_for_live_discovery`
extended to assert `/.well-known/ai-plugin.json` is in the live surface set). Full suite
**176 → 177** (all 19 files exit 0).

**Comms.** No Slack (score-neutral additive discovery, moves no score, not sensitive;
daily digest already sent Cycle 38 16:13Z, this fire 20:16Z is not a new digest window).

**First duty.** No open peer-gated PR (`list_pull_requests state=open` → `[]`). Infra
health check ran first — runner HEALTHY (`verify_20260727T194100Z`, 19:41Z, fresh;
46.1 F / 85.5 B / +39.4 in-band, drift recovered); bench runnable 176/176 pre-change;
git bookkeeping consistent (HEAD reset detached → main = origin/main `9c276d7`).

**Next hypothesis.** All FIVE agent-facing surface classes the directive's spirit
names (homepage / natural-language docs / agent-plugin descriptor / OpenAPI contract /
manifest) are now read. Next COVERAGE frontier that isn't score-neutral bookkeeping:
either the [LOCAL] OpenAPI-spec-only + ai-plugin-descriptor live fixture captures (pin
spec/descriptor-driven classification end-to-end on a REAL site, not just synthetic
surfaces — the committed fixtures predate both surfaces), or the operator directive's
BRICK 4 (out-of-scope legibility diagnostic — needs a separate proposal + behavioral
runs, [LOCAL]). Next cycle takes TRUTH.

## Local verification — 20260727T204103Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T204103Z.json

## Local cycle — 2026-07-27T20:54Z  (TRUTH — machine-surface fixture + offering-classifier precision fix, direct-to-main, score-neutral)

**Track / item.** TRUTH. Executed the [LOCAL] "Machine-surface-only storefront fixture
(OpenAPI spec + ai-plugin descriptor)" item (P2) — the named calibration follow-up to the
two most recent ships, Cycle 34 (OpenAPI surface) and Cycle 42 (ai-plugin descriptor),
whose surface-reading had been tested ONLY on synthetic surfaces (the committed canonical
fixtures predate both surfaces → replay-miss/absent on them). This is the local cycle's
mandate: live probe validation the cloud designed but could not execute. Chosen over the
oldest-P0 behavioral acceptance rerun because that run exceeds this fire's codex budget
(pair + retail ≈ 12 codex vs ~10 cap), codex reputation-gates the canonical domains
(degrading its cross-model value), and a 12-panel behavioral run carries real hang/timeout
risk — deferring it one fire is low-cost; the acceptance rerun stays queued as oldest P0.

**What live calibration surfaced (the TRUTH payoff).** Probed real API-first storefronts
for a root-level machine surface ($0 GETs): `api.replicate.com/openapi.json` (200,
application/json, 92 KB) is a genuine metered model-inference storefront whose homepage is a
bare `{}` — its agent-facing self-description IS its spec. Running `discover_offering` LIVE
on it classified it `['metered_api', 'physical_good']` — and the **physical_good was a FALSE
POSITIVE**: the `sku-inventory` signal matched `"hardware":{"description":"The SKU for the
hardware used to run the model."`, i.e. a COMPUTE/GPU hardware SKU, not retail inventory.
The old signal was a bare `\bSKU\b|\binventory\b`, exactly the kind of loose match the
module's own precision-first doctrine forbids ("require unambiguous fulfillment nouns"). A
`physical_good` task on Replicate would garden-path an agent — the precise battery pollution
the operator's offering-relative directive exists to remove. Calibration against reality
caught a measurement error → fixed it.

**Fix (`asrs/offering.py`, the one code change).** Re-anchored `sku-inventory` to the RETAIL
sense only — `product/item/per/each/retail SKU`, `SKU number/code/count/list/catalog`,
`inventory count/levels/on-hand/management/status`, `manage/track/update/check/low/out-of
inventory`, `in-stock inventory` — dropping the bare-token arm. Verified on a pos/neg corpus:
every compute-SKU form ("The SKU for the hardware", "hardware SKU: a100", "the SKU of the
compute instance") and bare "inventory API" now DO NOT match; every retail form still does.
`sku-inventory` is nearly redundant for recall (a real shop trips add-to-cart / stock /
shipping anyway — books.toscrape.com's physical_good rests on add-to-cart + stock, sku-inventory
fires on NONE of the four committed fixtures), so the tightening loses no real recall.
`api.replicate.com` now classifies **`['metered_api']`**, driven by the `/openapi.json` surface.

**Fixture (live evidence → permanent in-cloud guard).** Captured
`fixtures/canonical/api.replicate.com.json` (8 GET / 0 POST — invariant #1 trivially clean;
homepage `{}` + the 92 KB public OpenAPI spec + the 404 surfaces). Secret-scanned: the only
Authorization strings are placeholders (`$REPLICATE_API_TOKEN`); the long hex/base64 blobs are
public OpenAPI example values (a spec version id, a pagination cursor, an example image UUID) —
no credentials, same category as the canonical fixtures' public API-doc examples.

**Tests.** `tests/test_offering_canonical.py` 11 → 12: `test_machine_surface_openapi_storefront`
replays the committed fixture through the REAL `from_fixture → discover_offering` path (no
network) and pins — (a) `/openapi.json` was READ; (b) claimed == `{metered_api}` exactly, the
spec DROVE it (≥1 metered signal with surface `/openapi.json`); (c) machine-surface-FIRST — the
homepage was fetched but carries ZERO archetype signal; (d) `physical_good` = NA, NON-VACUOUS —
it first asserts the trap phrase "SKU for the hardware" IS present in the spec, so the guard
proves the FIX keeps it NA, not that the trap is absent. `tests/test_offering.py` 10 → 11:
`test_sku_inventory_is_retail_sense_not_compute` pins the same precision on a synthetic surface
(compute-SKU spec → metered_api, NOT physical_good; retail "product SKU" / "inventory levels" →
physical_good via the sku-inventory label — recall retained).

**Score-neutrality.** `classify_offering` / `discover_offering` is OFF the scoring path (called
only from `cli._resolve_battery` for `--battery auto` — grep-verified: absent from scoring.py /
probes/ / protocols.py). `git diff --name-only -- asrs/scoring.py rubric/ asrs/probes/
asrs/fetch.py asrs/protocols.py asrs/battery.py asrs/behavioral/` EMPTY → rubric stays **v0.7**,
no `battery_semantics_version` bump (aggregation untouched). A discovery precision fix, same
class as Cycles 34/42 → direct-to-main, not payment/signing.

**Canonical pair.** drift-flight.org **46.1 F** / driftflight.com **85.5 B** / delta **+39.4** —
unchanged by construction AND re-measured: in-cloud replay guard `test_canonical_replay.py`
14/14 (0 replay-miss), live-corroborated by `verify_20260727T204103Z` (20:41Z, in-band). The
offering classification of the four committed domains is byte-identical (books.toscrape.com still
`physical_good`, canonical pair `{metered_api,subscription,digital_good}`, example.com empty) —
the fix touches no fixture's evidence.

**Suite.** 177 → 179 (all 19 files exit 0).

**Comms.** No Slack (score-neutral discovery precision fix, moves no score, not sensitive; daily
digest already sent Cycle 38 16:13Z, this fire 20:54Z is not a new digest window).

**First duty.** No open peer-gated PR (`gh pr list --state open` → `[]`). Infra health check ran
first — runner HEALTHY (`verify_20260727T204103Z`, 20:41Z, ~35 s old at fire; 46.1 F / 85.5 B /
+39.4 in-band, drift stayed recovered), bench 177/177 pre-change, git clean on main `9567edc`.

**Next hypothesis.** The offering classifier is now calibrated against a real machine-surface
storefront on BOTH axes — surface-reading (openapi DROVE classification) and precision (compute
SKU ≠ physical good). Remaining machine-surface calibration gap: a real ai-plugin-DESCRIPTOR-only
storefront fixture (Cycle 42's surface still has no real-data guard). The oldest-P0 behavioral
`--battery auto` acceptance rerun remains queued. Cloud rotation unaffected (still TRUTH next).

## Cycle 43 (TRUTH) — 2026-07-27T21:17Z — the re-capture DECISION is now COMPUTED, not hand-reasoned

**Track.** TRUTH (rotate METHOD→COVERAGE→TRUTH→READOUT; Cycle 42 COVERAGE → this TRUTH).

**What / why.** The Cycles 36→41 diagnostic arc built the drift readout in layers — band
(36), pillar attribution (37), side/direction cause (39), HTML surface (40). Every layer feeds
ONE decision: given the live series, does the committed canonical fixture still represent the
true capability gap, or has the reference pair moved durably enough that the pinned delta should
be re-captured `[LOCAL]`? That decision — the calibration-against-reality judgment at the heart
of the benchmark's credibility — was still HAND-REASONED: the STATE drift note walked through it
by hand FIVE times (Cycles 36/37/38/39/41) during the 2026-07-27 `.com` drift. This cycle makes
it COMPUTED — the same prose→tripwire move Cycles 17/19/21/23/31/35 made for the scoring guards.

New pure `asrs/canonical_history.recapture_advice(history) -> RecaptureAdvice(code, reason)`,
stored on `CanonicalHistory.recapture` in `summarize`, rendered as a `re-capture:` line. Five
honest codes synthesized from already-computed signals (band + `consecutive_out_of_band` +
`divergence_cause`), NEVER an action (moving the pinned baseline is a `[LOCAL]`, comparability-
affecting step — the maintenance contract `test_canonical_replay` documents):
  - `baseline-valid` — in-band: the live delta reproduces the pinned delta; no re-capture.
  - `wait-not-yet-sustained` — out of band but run < `_SUSTAINED_MIN` (3): could be jitter, wait.
  - `defer-reference-degraded` — sustained, with-rails reference SOFTENED (`reference_degraded`):
    a real-world site change, not the gap closing; the pinned fixture still represents the true
    gap → DEFER. THE load-bearing case, the exact 2026-07-27 drift shape — and the site's later
    recovery (Cycle 41) VINDICATED this recommendation over chasing the dip.
  - `recapture-candidate` — sustained AND the baseline genuinely moved (no-rails gaining, or the
    reference durably improving): a real capability-gap change → a `[LOCAL]` re-capture re-pins it.
  - `review-no-anchor` — sustained but the whole series is out of band (no in-band anchor to
    attribute against) → a human look before any action.
Refactored the render's literal `3` → `_SUSTAINED_MIN` (behavior-preserving, one source of truth
for "sustained" shared by the counter line and the recommendation gate).

**Evidence / validation.** `tests/test_canonical_history.py` 13→19 (+6: one per code with the
recapture-candidate case a NON-VACUOUS direction control — a recommendation blind to direction
would DEFER where the no-rails floor genuinely gained; plus a recovery-tolerant real-series
coherence test tying code↔band). On the REAL committed series (69 points) the recommendation reads
`baseline-valid` — the honest no-action state, matching the Cycle-41 drift-recovered note.

**Canonical pair.** drift-flight.org **46.1 F** / driftflight.com **85.5 B** / delta **+39.4** —
unchanged by construction AND re-measured: in-cloud replay guard `test_canonical_replay.py` 14/14
(0 replay-miss), live-corroborated by `verify_20260727T204103Z` (20:41Z, in-band). `git diff
--name-only` = `asrs/canonical_history.py` + `tests/test_canonical_history.py` ONLY; scoring.py/
rubric/probes/fetch/protocols/battery/offering/behavioral/scorecard byte-for-byte untouched →
rubric stays **v0.7**. Read-only diagnostic (imports no scoring code, moves no score, touches no
rubric); direct-to-main.

**Suite.** 179 → 185 (all 19 files exit 0).

**Comms.** No Slack (TRUTH read-only diagnostic + tests, moves no score, not sensitive; daily
digest already sent Cycle 38 16:13Z, this fire 21:17Z is not a new digest window).

**First duty.** No open peer-gated PR (`list_pull_requests state=open` → `[]`). Infra health check
ran first — runner HEALTHY (`verify_20260727T204103Z`, 20:41Z, ~37 min old at fire; 46.1 F / 85.5 B
/ +39.4 in-band, drift stayed recovered), bench 179/179 pre-change (after `pip install requests
PyYAML eth-account`), git realigned to origin/main `4b1d1e3` (detached HEAD from the local-verify
push reset to main).

**Next hypothesis.** The re-capture decision is computed on the terminal readout; the Cycle-40 HTML
canonical-history page does NOT yet surface it — the same terminal→HTML deferral the battery
diagnostics took (Cycles 10→12, 18→20). Surfacing `recapture` on `canonical-history.html` is a
clean READOUT follow-up (queued P2). Cloud rotation → READOUT next.

## Local verification — 20260727T214106Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T214106Z.json

## Local verification — 20260727T215839Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T215839Z.json

## Cycle 44 (READOUT) — 2026-07-27T22:2xZ — re-capture recommendation surfaced on canonical-history.html

**Track.** READOUT (rotate METHOD→COVERAGE→TRUTH→READOUT; Cycle 43 TRUTH → this READOUT).

**What / why.** Cycle 43 made the canonical re-capture DECISION computed
(`canonical_history.recapture_advice` → `RecaptureAdvice`, rendered as the terminal `re-capture:`
line). But that decision — the synthesized answer to "does the committed fixture still represent the
true capability gap, or should the pinned delta be re-captured `[LOCAL]`?" — was TERMINAL-ONLY; the
Cycle-40 HTML `canonical-history.html` page rendered the band, sustained run, pillar attribution and
side/direction cause but NOT the decision they all feed. This closes that last terminal→HTML gap for
the benchmark reading its own regression signal — the SAME deferral the battery diagnostics took
(per_kind Cycle 10→12, between_kind_spread Cycle 18→20, NA-naming Cycle 25→28), now for the drift arc.

`_write_canonical_history_page` gains a "Re-capture decision" card driven off `hist.recapture`
(computed in `summarize`): the recommendation label (`ch._REC_LABEL`) + full reason, rendered
whenever there is a reading (any code but the `REC_NO_DATA` sentinel). A new `_HISTORY_REC_COLOR`
map colours the label chip by code, reusing the band inks so the surface reads as one system —
green `baseline-valid` (no action) / amber `wait`+`defer` (hold) / red `recapture-candidate` (a real
move, a `[LOCAL]` re-capture candidate) / neutral `review`. NEVER colour-alone: the label text and
the full reason always render alongside the chip. The card states in prose that re-capture is a
DECISION, never an action (moving the pinned baseline is a `[LOCAL]`, comparability-affecting step) —
the page performs nothing.

**Evidence / validation.** `tests/test_readout.py` 29→31 (+2): `test_canonical_history_page_renders_
recapture_defer` (the drifting series → `REC_DEFER`: names the "defer re-capture" label, the
"DEFER … until the reference recovers" reason, the code-keyed chip colour, and the `[LOCAL]` framing)
+ `test_canonical_history_recapture_is_data_driven` (NON-VACUOUS — an in-band series renders
`baseline valid` and does NOT show the DEFER label → the card is earned by the data, not templated).
Rendered the LIVE page off the committed 69-point series: recommendation reads `baseline-valid`
(green) — the honest no-action state matching the recovered/stable drift (Cycle 41).

**Canonical pair.** drift-flight.org **46.1 F** / driftflight.com **85.5 B** / delta **+39.4** —
unchanged by construction AND re-measured: in-cloud replay guard `test_canonical_replay.py` 14/14
(0 replay-miss), live-corroborated by `verify_20260727T215839Z` (21:58Z, in-band). `git diff
--name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY; scoring.py/rubric/probes/fetch/
protocols/battery/offering/behavioral/canonical_history byte-for-byte untouched (verified empty diff)
→ rubric stays **v0.7**. Display-only (renders an already-computed read-only diagnostic, moves no
score, touches no rubric); direct-to-main. The reference-pair hosts appear only as DATA — the SAME
engineering-history category as rubric.html, deliberately out of scope for the wording scanner
(`test_readout_wording` unchanged/green).

**Suite.** 185 → 187 (all 19 files exit 0).

**Comms.** No Slack (READOUT display-only + tests, moves no score, not sensitive; daily digest
already sent Cycle 38 16:13Z, this fire ~22:2xZ is not a new digest window).

**First duty.** No open peer-gated PR (`list_pull_requests state=open` → `[]`). Infra health check
ran first — runner HEALTHY (`verify_20260727T215839Z`, 21:58Z, fresh; 46.1 F / 85.5 B / +39.4
in-band, drift stayed recovered), bench 185/185 pre-change (after `pip install -r requirements.txt`),
git realigned to origin/main `53ed513` (detached HEAD from the local-verify push reset to main).

**Next hypothesis.** The canonical-history HTML surface is now complete (trend + band + sustained
run + pillar + side/cause + re-capture decision). READOUT frontier moves elsewhere: the compare-card
delta → methodology earned-dominance cross-link (P2, the last cross-link nicety), or evidence-blob
links on the card. Cloud rotation → METHOD next.

## Local verification — 20260727T224106Z

tests_ok=True | drift-flight.org: 46.1 F | driftflight.com: 85.5 B | delta +39.4 | artifact runs/local/verify_20260727T224106Z.json

## Cycle 45 (METHOD) — 2026-07-27T23:1xZ — the divergence band's noise assumption made a MEASURED number

**Track.** METHOD (rotate METHOD→COVERAGE→TRUTH→READOUT; Cycle 44 READOUT → this METHOD).

**What / why.** The canonical-history drift arc (Cycles 36→44: band → sustained run → pillar
attribution → side/cause → re-capture decision → HTML) rests on the divergence bands
(`_BAND_IN=2.0`, `_BAND_DRIFT=8.0`). Those thresholds were ASSUMED constants justified only by the
docstring's prose — "within ordinary static/live jitter of the pinned delta" — with NO test
validating them against the actual observed noise of the committed series. That is an unguarded
methodological assumption, and a distinct KIND of rigor from everything the arc had added so far
(all diagnostics; none calibration-validation). This cycle turns the assumption into a measured,
guarded number — the first variance/calibration guard in the repo.

`asrs/canonical_history.py` (read-only, imports no scoring code): new `NoiseFloor` dataclass +
`noise_floor(points, baseline)` measures the AT-REST dispersion of the delta over the readings the
band already calls in-band (`|delta - baseline| <= _BAND_IN`): `n_in_band`, population `stddev`, and
`max_abs_divergence` (worst at-rest |div|). Properties: `deterministic` (σ and worst |div| both ≤
`_NOISE_EPS=1e-6` → every in-band re-score reproduced the pinned delta exactly) and
`band_well_separated` (3σ of the at-rest jitter still fits inside `_BAND_IN` → ordinary noise can't be
misread as drift; False = the band is TOO TIGHT for the measured noise). Wired into `summarize` as
`CanonicalHistory.noise_floor` (None when < 2 in-band readings — dispersion undefined, the same
honest-None discipline attribution uses); rendered as a `noise floor:` line. Honest limit documented:
the in-band clip makes this a truncated (lower-biased) estimate of true jitter — fine as a calibration
FLOOR (if even the clipped dispersion crowds the band, the band is certainly too tight).

**The finding.** On the committed 72-point series, all **68 in-band re-scores reproduce +39.4
EXACTLY** — σ=0.00, worst |div|=0.00, `deterministic=True`. The static canonical re-score is
deterministic at rest, so the in-band band is demonstrably absorbing real-world site TRANSIENTS (the 4
out-of-band readings: deltas 3.9 / 30.1 / 32.6, the 2026-07-27 `.com` outage) — NOT measurement noise.
The docstring's bare "ordinary jitter" claim is now a measured fact. Render:
`noise floor: 68 in-band re-scores  σ=0.00  worst |div|=0.00  → DETERMINISTIC at rest — the ±2.0 band
absorbs site transients, not measurement noise`.

**Evidence / validation.** `tests/test_canonical_history.py` 19 → 24 (+5):
(1) `test_noise_floor_is_deterministic_on_real_series` — the load-bearing finding on the REAL series
(σ=0, worst |div|=0, deterministic, render says DETERMINISTIC);
(2) `test_band_clears_the_observed_noise_and_the_real_transients_are_signal` — calibration validation
both directions: 3σ of at-rest jitter fits the in-band band (not miscalibrated-too-tight) AND every
real out-of-band transient's |div| sits far above the noise floor (genuine SIGNAL, never a noise
false-alarm), non-vacuous when the committed series carries the transients;
(3) `test_noise_floor_measures_synthetic_jitter` — NON-VACUOUS: in-band deltas that genuinely vary
(±0.8, still in-band) report positive σ, matching worst |div|, `deterministic=False` (the measure
isn't hard-coded to 0);
(4) `test_noise_floor_flags_a_too_tight_band` — makes `band_well_separated` non-vacuous: ±1.9 jitter
crowding the whole band → 3σ > `_BAND_IN` → `band_well_separated=False`, render raises "TOO TIGHT";
(5) `test_noise_floor_none_below_two_in_band` — honest None for < 2 in-band readings (all-OOB and a
lone in-band reading).

**Canonical pair.** drift-flight.org **46.1 F** / driftflight.com **85.5 B** / delta **+39.4** —
unchanged by construction AND re-measured: in-cloud replay guard `test_canonical_replay.py` 14/14
(0 replay-miss), live-corroborated by `verify_20260727T224106Z` (22:41Z, in-band). `git diff
--name-only` = `asrs/canonical_history.py` + `tests/test_canonical_history.py` ONLY; scoring.py/rubric/
probes/fetch/protocols/battery/offering/behavioral/scorecard byte-for-byte untouched (verified empty
diff over the scoring path) → rubric stays **v0.7**. Read-only diagnostic (measures an already-committed
series, moves no score, touches no rubric); direct-to-main. Reference-pair hosts appear only as DATA
(same engineering-history category as the rest of the module).

**Suite.** 187 → 192 (all 19 files exit 0; `test_free_tier.py` 11/11 after `pip install -r
requirements.txt` closes the known `eth-account` env gap).

**Comms.** No Slack (METHOD tests + read-only diagnostic, moves no score, not sensitive; daily digest
already sent Cycle 38 16:13Z, this fire ~23:1xZ is not a new digest window).

**First duty.** No open peer-gated PR (`list_pull_requests state=open` → `[]`). Infra health check ran
first — runner HEALTHY (`verify_20260727T224106Z`, 22:41Z, ~31 min old; 46.1 F / 85.5 B / +39.4
in-band, drift stayed recovered), bench green; git reset to origin/main `5411e2b`.

**Next hypothesis.** The noise floor validates the in-band band; the drifting/diverged cutoffs
(`_BAND_DRIFT=8.0`) are still assumed. A next METHOD unit could measure the observed transient
magnitudes to check the drifting/diverged split is calibrated too, OR surface `noise_floor` on
`canonical-history.html` (READOUT, the same terminal→HTML deferral). Cloud rotation → COVERAGE next.
