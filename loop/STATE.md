# Loop state

- Cycle counter: 6
- Started: 2026-07-23 (UTC)
- Focus pointer: TRUTH (rotate METHOD → COVERAGE → TRUTH → READOUT)
  (Cycle 1 METHOD, Cycle 2 COVERAGE, Cycle 3 TRUTH, Cycle 4 READOUT,
  Cycle 5 METHOD, Cycle 6 COVERAGE; next cycle takes TRUTH.)
- Rubric: v0.5 on main (PR #1 merged 2026-07-23 via the Cycle-2 peer-gate).
  UNCHANGED by Cycles 2–4 (task battery, panel-reliability, and the reliability
  readout-surfacing are diagnostic layers over already-collected runs, not
  scoring-semantics changes).
- Task battery: format + aggregation landed Cycle 2; `--battery` CLI wiring +
  additive `Report.battery_summary` + terminal `TASK BATTERY` section landed
  Cycle 6 (`asrs/cli.py` `_run_behavioral(..., battery=)` runs the shopper panel
  once per intent, first task = primary scoring run, free-tier once for the whole
  battery; `asrs/report.py _battery_lines`; `tests/test_battery_wiring.py` 4/4,
  synthetic panel). NOT a scoring-semantics change (rubric stays v0.5, scoring.py
  untouched). REMAINING: [LOCAL] behavioral execution on the canonical pair (now
  unblocked — queued P0) produces the first live `cross_task_spread`; HTML
  scorecard battery card is queued P2 READOUT (terminal-first, like quotability).
- Panel reliability: `asrs/reliability.py` (within-panel verdict-stability) +
  render section landed Cycle 3. Cycle 4 attached it to the JSON `Report`
  (additive `panel_reliability` field, populated in `cli._evaluate`) and the HTML
  scorecard (`scorecard._reliability`, both layouts). Reproducibility now travels
  with the score everywhere it goes.
- Quotability gate (Cycle 5, METHOD): `asrs.reliability.quotability(report)` ->
  `Quotability(quotable, tag, reason, verdict_stability)` classifies whether the
  headline number is CITABLE or PROVISIONAL (static-deterministic / reproducible /
  provisional-single-trial / provisional-unstable / behavioral-unobserved /
  not-scorable). Surfaced as one `QUOTABILITY:` line under OVERALL in the terminal
  card (`report._quotability_lines`). `--trials` default 1 -> 2 (multi-trial by
  default; free-tier probe still runs once). Terminal-only so far; JSON/HTML
  attach is the natural next READOUT step (mirrors the reliability Cycle-3 -> 4
  pattern). NOT a scoring-semantics change — no version bump, scoring.py/rubric/
  types.py byte-for-byte unchanged.
- Canonical pair: drift-flight.org 46.1 F vs driftflight.com 85.5 B — delta
  +39.4. Confirmed LIVE this local fire (2026-07-23T05:52Z, both HTTP 200),
  matching the freshest hourly verify artifact verify_20260723T040757Z.json
  exactly. Loop-start behavioral baseline was +40.6 (delta within static
  variance). Hourly runner healthy (~1.6h old at the local fire).
- Open PRs: none. PR #1 (Cycle 1 v0.5 NOT-SCORABLE fix) merged
  2026-07-23T03:00:15Z. Its [LOCAL] merge-time canonical re-score is now
  DISCHARGED: local fire 2026-07-23T05:52Z re-scored both reachable domains
  normally (46.1 F / 85.5 B, delta +39.4, NOT not-scorable) and confirmed the
  NOT-SCORABLE path via an unreachable-domain control (grade N/A, scored=False)
  — proving v0.5 is a no-op for reachable domains. Evidence:
  runs/local/merge_verify_pr1_20260723T055000Z.json. BACKLOG item removed.
  https://github.com/jnakagawa/agentic-readiness/pull/1

## Environment constraint (IMPORTANT — affects every cycle)

This cloud loop has **NO outbound network to external domains**: the agent
proxy denies CONNECT to drift-flight.org / driftflight.com / example.com / any
web host (403 "policy denial"). Confirmed 2026-07-23 via `asrs.fetch` and
`curl $HTTPS_PROXY/__agentproxy/status`. Consequences:
- The playbook's per-cycle LIVE static re-score of the canonical pair CANNOT
  run in-cloud. In-cloud, both canonical domains return NOT SCORABLE.
- Regression signal must therefore be argued by construction + offline unit
  tests in-cloud, and the LIVE delta re-score queued [LOCAL] for Jonah.
- Reachable from Python: pypi/github/anthropic infra only. Claude-side
  WebFetch/WebSearch tools route separately and DO work for research.
- Open question for Jonah: is this the intended network policy for the loop
  env, or should the canonical domains be allowlisted so in-cloud re-scores
  work? If not allowlistable, the "re-score every shipping cycle" rule needs a
  cloud-adapted form (offline regression tests as the in-cloud proxy).

## Open questions

- Does the cloud environment have a usable `claude` CLI for nested shopper
  panels? Test cheaply in an early cycle; if yes, behavioral experiments
  partially unblock in-cloud (codex still local-only).
- Codex hosted-browser refusal of driftflight.com: OpenAI-side reputation
  gate, non-deterministic (browsed fine 22:28 UTC, blocked 22:53/22:58/23:21
  on 2026-07-22; drift-flight.org unaffected in the same invocation, then
  blocked in a later one). Root cause + attribution control needed.
- Panel verdict variance: codex trust verdict flipped refuse(0.97) ↔
  warn(0.97) on the .org between same-day runs. Cycle 3 shipped the METRIC
  (`asrs/reliability.py` `verdict_stability` / `trust_event_agreement`) that
  makes the flip visible; the EMPIRICAL question — what trial count N drives
  `verdict_stability` above ~0.8 on the canonical pair — needs a [LOCAL]
  multi-trial run (queued in BACKLOG). COST FINDING (local fire 05:52Z):
  `SHOPPER_TIMEOUT_S=300`/trial makes the full N=2,3,5 × both-domains sweep
  ~100 min / ~20 codex invocations — over the one-pair-run + ~10-codex budget.
  Next local fire should take ONE scoped datapoint (drift-flight.org, the
  codex-refusal-free domain, --trials 2) and split the sweep across fires.
