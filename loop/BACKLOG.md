# Backlog (prioritized; prune every cycle)

`[LOCAL]` = needs Jonah's machine (codex CLI / zero CLI / paid probes) —
design in-cloud, execute locally.

## P0

- **Task battery** (COVERAGE): score across a battery of diverse purchase
  intents (image generation, translation, data enrichment, a physical-goods
  intent, an API subscription) instead of a single task. Per-task checkpoint
  results, cross-task variance as a reliability signal. Rubric stays
  task-agnostic; the battery is a CLI flag (`--battery`). Design the battery
  file format + aggregation first; behavioral execution is `[LOCAL]`.
- **Codex reachability investigation** (TRUTH): characterize the hosted-
  browser refusal — determinism, domain features (age, TLD, content
  patterns), retry behavior. Build the control-storefront attribution fix
  from the v0 notes (feed codex pre-fetched content when its browser is
  gated, marked as assisted). Repro matrix is `[LOCAL]`; analysis + design
  in-cloud from committed transcripts.
- **trials ≥ 2 + variance readout** (METHOD): make multi-trial the scored
  default for anything quoted; verdict-stability metric (flip rate) on the
  card. Observed same-day refuse↔warn flip at equal confidence — a single
  trial is not quotable.

## P1

- **Calibration population** (TRUTH): weekly static sweep of 15–20 real
  domains (exa.ai, deepai.org, perplexity.ai, a Shopify store, a mainstream
  retailer, agentic-native services) committed as a dated dataset +
  leaderboard page. A benchmark needs a population, not one pair.
- **Live handshakes for other rails** (COVERAGE): ACP/UCP checkout-session
  and MPP-only elicitation parity with the x402 probe (currently markers/
  partial credit only).
- **Adversarial referee pass** (METHOD): a recurring self-audit — "would a
  critic call this check vendor-rigged?" — rewording and evidence-
  strengthening without losing capability substance.

## P2

- **Evidence links on the card** (READOUT): each check row links to its
  evidence blob; publish evidence alongside the hosted card.
- **Score-over-time trend page** (READOUT): per-domain history from the
  dated reports; error bars once trials ≥ 2 lands.
- **Free-tier probe generalization** (COVERAGE): more opt-in conventions
  (query param, path-based), non-EVM zero-value schemes.
- **Methodology prose page** (READOUT): how the panels work, refusal
  semantics, attribution rules, what CANT_TEST means — the "read the paper"
  page behind the rubric page.
