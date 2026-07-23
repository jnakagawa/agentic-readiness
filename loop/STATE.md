# Loop state

- Cycle counter: 2
- Started: 2026-07-23 (UTC)
- Focus pointer: TRUTH (rotate METHOD → COVERAGE → TRUTH → READOUT)
  (Cycle 1 METHOD, Cycle 2 COVERAGE; next cycle takes TRUTH.)
- Rubric: v0.5 on main (PR #1 merged 2026-07-23 via the Cycle-2 peer-gate).
  UNCHANGED by Cycle 2 (task battery is a diagnostic layer, not a
  scoring-semantics change).
- Task battery: format + aggregation landed on main (Cycle 2). `--battery` CLI
  wiring + behavioral execution queued [LOCAL] in BACKLOG.
- Canonical pair at loop start (behavioral, reports T233804/T235048):
  drift-flight.org 45.7 F vs driftflight.com 86.3 B — delta +40.6
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
  warn(0.97) on the .org between same-day runs. What N stabilizes it?
