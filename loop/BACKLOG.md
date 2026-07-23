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

- **Task battery — wire `--battery` into the pipeline** (COVERAGE, Cycle 2
  follow-up). Format + loader + cross-task aggregation SHIPPED Cycle 2
  (`asrs/battery.py`, `batteries/default_v1.yaml`, `tests/test_battery.py`).
  Remaining, IN-CLOUD-testable with a synthetic panel (monkeypatch
  `shopper.run_panel`):
  - Add `--battery <path>` to `score`/`compare`. In behavioral mode: run static
    probes ONCE, run the shopper panel ONCE PER TASK, run the free-tier
    transaction probe AT MOST ONCE for the whole battery (it consumes the
    allowance — invariant #1; do NOT loop it per task). In static mode
    `--battery` is a no-op (static probes are task-independent) — warn + proceed.
  - Attach the `BatterySummary` to `Report` as a NEW additive field (like
    `trust_panel`/`behavioral_runs`) — additive, NOT a scoring-semantics change,
    NO version bump. Render a reliability row (`cross_task_spread` + per-task
    completion) in `report.render` and the HTML scorecard — mirror the Cycle-4
    `panel_reliability` surfacing (additive `Report` field populated in
    `cli._evaluate`; `scorecard._reliability` card wired into both layouts) as
    the template for a `BatterySummary` field + card.
  - `[LOCAL]` behavioral execution once wired:
    ```
    git checkout main && git pull
    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m asrs score drift-flight.org --behavioral \
      --battery batteries/default_v1.yaml --models claude,codex --trials 2
    # Expect: per-task checkpoint grid + a cross_task_spread reliability number;
    # exactly ONE free-tier transaction attempt in runs/ for the whole battery.
    ```
- **Codex reachability investigation** (TRUTH): characterize the hosted-
  browser refusal — determinism, domain features (age, TLD, content
  patterns), retry behavior. Build the control-storefront attribution fix
  from the v0 notes (feed codex pre-fetched content when its browser is
  gated, marked as assisted). Repro matrix is `[LOCAL]`; analysis + design
  in-cloud from committed transcripts.
- **[LOCAL] What trial count N stabilizes the panel** (TRUTH/METHOD, Cycle 3
  follow-up): the reliability metric now quantifies flips, but the empirical
  answer to "what N drives `verdict_stability` above ~0.8" needs real multi-trial
  runs. Exact commands (networked machine w/ claude+codex CLIs):
  ```
  git checkout main && git pull
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  for N in 2 3 5; do
    .venv/bin/python -m asrs score drift-flight.org --behavioral \
      --models claude,codex --trials $N
  done
  # Read the PANEL RELIABILITY section per N; record verdict_stability(N) and
  # flipped_checkpoints. Report the smallest N with stability >= 0.8 for each
  # canonical domain. Feeds the "trials >= 2 default" METHOD item above.
  ```

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

- **Quotability on the JSON/HTML card** (READOUT, Cycle 5 follow-up): the
  quotability gate (`asrs.reliability.quotability`) ships terminal-only. Attach
  it to `Report` as an additive field (populate in `cli._evaluate` from the same
  function) and render a CITABLE/PROVISIONAL pill on the HTML scorecard — exactly
  the Cycle-3→4 reliability pattern (`scorecard._reliability` is the template).
  Additive, no version bump; so a leaderboard consumer sees "is this citable?"
  next to the number, not only a terminal a human ran once.

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
