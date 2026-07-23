# Loop state

- Cycle counter: 0 (no cycles run yet)
- Started: 2026-07-23 (UTC)
- Focus pointer: METHOD (rotate METHOD → COVERAGE → TRUTH → READOUT)
- Rubric at loop start: v0.4
- Canonical pair at loop start (behavioral, reports T233804/T235048):
  drift-flight.org 45.7 F vs driftflight.com 86.3 B — delta +40.6

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
