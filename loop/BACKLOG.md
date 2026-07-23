# Backlog (prioritized; prune every cycle)

`[LOCAL]` = needs Jonah's machine (codex CLI / zero CLI / paid probes) —
design in-cloud, execute locally.

## P0

- **[LOCAL] Merge-time canonical re-score for PR loop/not-scorable-attribution**
  (METHOD, Cycle 1 follow-up). The cloud env can't reach the canonical domains,
  so the regression re-score for the v0.5 NOT-SCORABLE PR must run on Jonah's
  networked machine before merge. Exact commands:
  ```
  git checkout loop/not-scorable-attribution
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  .venv/bin/python tests/test_scoring.py && .venv/bin/python tests/test_free_tier.py
  .venv/bin/python -m asrs compare drift-flight.org driftflight.com --json-only
  # Expect: both domains still score normally (delta ~ +40.6 static-equivalent),
  # NOT "not scorable" — proving the change is a no-op for reachable domains.
  ```
  Delete this item once the re-score is recorded and the PR merges.

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
  page behind the rubric page. NOTE: now also document NOT-SCORABLE (v0.5) —
  the difference between "F" and "N/A".

- **Coverage-warning noise** (READOUT/METHOD, Cycle 1 observation): scoring
  prints one stderr line per absent rubric check on every run. In static mode
  ALL behavioral checks are legitimately absent, so a normal run emits ~12
  warnings — noise that will bury genuinely-unexpected gaps. Suppress
  expected-absent warnings (behavioral checks when not in --behavioral mode);
  keep warnings only for a check that's absent when it should have run. Small,
  direct-to-main safe (no scoring-semantics change).
