# Loop state

- Cycle counter: 5
- Started: 2026-07-23 (UTC)
- Focus pointer: COVERAGE (rotate METHOD → COVERAGE → TRUTH → READOUT)
  (Cycle 1 METHOD, Cycle 2 COVERAGE, Cycle 3 TRUTH, Cycle 4 READOUT,
  Cycle 5 METHOD; next cycle takes COVERAGE.)
- Rubric: v0.5 on main (PR #1 merged 2026-07-23 via the Cycle-2 peer-gate).
  UNCHANGED by Cycles 2–4 (task battery, panel-reliability, and the reliability
  readout-surfacing are diagnostic layers over already-collected runs, not
  scoring-semantics changes).
- Task battery: format + aggregation landed on main (Cycle 2). `--battery` CLI
  wiring + behavioral execution queued [LOCAL] in BACKLOG. Battery attach to the
  JSON/HTML Report waits on that wiring (no populated source in-cloud yet).
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
- Canonical pair (freshest local-verify artifact verify_20260723T040757Z.json):
  drift-flight.org 46.1 F vs driftflight.com 85.5 B — delta +39.4. Runner
  healthy (~1h old at Cycle 5). Loop-start behavioral baseline was +40.6.
- Open PRs: none. PR #1 (Cycle 1 v0.5 NOT-SCORABLE fix) merged 2026-07-23.
  Its [LOCAL] merge-time canonical re-score verification stays queued in
  BACKLOG until a networked operator records it (cloud env can't re-score).
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
  multi-trial run (queued in BACKLOG).
