# agentic-readiness (ASRS)

**Agentic Selling Readiness Score** — how ready is a storefront/API to sell to
AI agents? A series of probes and live shopper agents evaluate a domain and
roll findings into a 0-100 score + letter grade across five pillars:

| Pillar | Question |
|---|---|
| Access | Can an agent get in at all? (bot walls, robots.txt AI policy) |
| Legibility | Can an agent understand what's for sale? (llms.txt, schema.org, machine-readable pricing) |
| Transactability | Can an agent pay programmatically? (x402, MCP, ACP/UCP, self-serve PAYG) |
| Trust | When a user directs an agent to buy here, does it proceed, warn, or refuse? (static signals + directive-framed model panel + in-session trust events) |
| Outcome | Do shopper agents actually get the job done, repeatedly? (checkpoint ladder, multi-trial) |

The flagship use case is the **delta**: score a storefront's legacy surface vs
its agent storefront (e.g. with vs without ZeroClick) side by side —
the quantified version of the demo.zeroclick.io comparison.

## Quickstart

```bash
.venv/bin/python -m asrs score example.com                # static probes only
.venv/bin/python -m asrs score example.com --behavioral \
    --task "buy an AI-generated image" --trials 2         # + live shopper panel
.venv/bin/python -m asrs compare deepai.org driftflight.com \
    --task "get an AI-generated image"                    # side-by-side + delta
```

Reports land in `runs/` as JSON; a report card renders to the terminal.

## Design notes

- **Rubric is versioned** (`rubric/rubric_v0.yaml`); every report embeds the
  version. Scores are only comparable within a version.
- **Critical failures cap the grade** (SSL Labs pattern) — a bot wall or a
  panel-model refusal limits the grade no matter the points. Only caps that
  actually bind (lower the pre-cap score) are reported as applied.
- **Trust is measured under a directive** (rubric v0.2) — the panel is told the
  user already said "go buy here" and reports what it does next: `proceed`,
  `proceed_with_warning`, or `refuse`. Refusal-despite-directive caps the
  grade; warnings only deduct. The shopper's in-task `trust_events` are scored
  too (`trust_live_session`) — live evidence can resolve concerns a static
  homepage excerpt cannot, matching how real directed sessions behave.
- **Can't-test is first-class** — `not_applicable` / `cant_test` shrink the
  denominator instead of counting as failures (OpenSSF Scorecard pattern).
- **Every failed check is a named finding with a remediation**
  (Mozilla Observatory pattern) — the report doubles as a fix list.
- **Behavioral layer** drives headless `claude -p` and `codex exec` as the
  shopper/trust panel — the two model families expected to carry most real
  agent traffic. v0 runs are read-only recon (no accounts created, no payments).

## Layout

```
asrs/types.py        shared contracts (CheckResult, Report, ...)
asrs/fetch.py        HTTP client with per-UA fetching + cache
asrs/probes/         access, legibility, protocols, trust_static
asrs/behavioral/     shopper panel + trust probe (claude/codex CLIs)
asrs/scoring.py      rubric roll-up: pillar scores, caps, grade
asrs/report.py       JSON + terminal report card + compare view
rubric/              versioned rubric YAML
runs/                report output (gitignored)
```
