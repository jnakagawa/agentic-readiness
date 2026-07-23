# Backlog (prioritized; prune every cycle)

`[LOCAL]` = needs Jonah's machine (codex CLI / zero CLI / paid probes) —
design in-cloud, execute locally.

## P0

<!-- DONE 2026-07-23T05:52Z (local fire): "[LOCAL] Merge-time canonical re-score
     for PR loop/not-scorable-attribution" discharged. Both reachable canonical
     domains re-scored normally (46.1 F / 85.5 B, delta +39.4, NOT not-scorable);
     unreachable-domain control returned NOT SCORABLE (grade N/A, scored=False).
     Evidence: runs/local/merge_verify_pr1_20260723T055000Z.json. See LOG. -->

<!-- DONE 2026-07-23T06:15Z (Cycle 6, COVERAGE): "Task battery — wire --battery
     into the pipeline" in-cloud parts SHIPPED. `--battery` on score/compare;
     shopper panel once per intent; first task = primary scoring run; free-tier
     once for the whole battery; static-mode no-op; additive
     `Report.battery_summary` + terminal `TASK BATTERY` section.
     tests/test_battery_wiring.py 4/4 (synthetic panel). No version bump.
     Only the [LOCAL] behavioral execution (below) and the HTML card (P2) remain. -->

- **[LOCAL] Task battery — first live behavioral run** (COVERAGE, Cycle 6
  follow-up; UNBLOCKED by the Cycle-6 `--battery` wiring). Produces the first
  real `cross_task_spread` on a live storefront — is a site's readiness
  intent-dependent, or does it hold across "buy the primary product" /
  "subscribe" / "order the physical good"? Run drift-flight.org first (the
  codex-refusal-free canonical domain) so browser refusals don't confound the
  per-intent grid. Budget note: 5 intents × claude,codex × 2 trials is up to 20
  panels — over the "one behavioral pair run" budget; scope to ONE domain per
  fire and, if needed, a trimmed 3-intent battery first.
  ```
  git checkout main && git pull
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  .venv/bin/python -m asrs score drift-flight.org --behavioral \
    --battery batteries/default_v1.yaml --models claude,codex --trials 2
  # Expect: TASK BATTERY section with per-intent completion + a cross_task_spread
  # number; EXACTLY ONE free-tier transaction attempt in runs/ for the whole
  # battery (grep runs/ for the free-tier blob — invariant #1 check). Record
  # cross_task_spread + which intents produced signal in the LOG.
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
  runs. SCOPING (local fire 2026-07-23T05:52Z cost finding): `SHOPPER_TIMEOUT_S
  =300`/trial makes the full N=2,3,5 × both-domains sweep ~100 min / ~20 codex
  invocations — over the "one behavioral pair run" + "~10 codex" per-cycle
  budget. Split it: ONE scoped datapoint per local fire, starting with N=2 on
  drift-flight.org (the codex-refusal-free canonical domain, so codex browser
  refusals don't confound timing). Per-fire command (networked, claude+codex):
  ```
  git checkout main && git pull
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  .venv/bin/python -m asrs score drift-flight.org --behavioral \
    --models claude,codex --trials 2   # then 3, then 5 on subsequent fires
  # Read PANEL RELIABILITY + QUOTABILITY per run; record verdict_stability(N),
  # flipped_checkpoints, and whether the headline is CITABLE/PROVISIONAL. This
  # is also the FIRST live-data validation of the Cycle 3-5 reliability +
  # quotability code. Report the smallest N with stability >= 0.8 per domain.
  # Feeds the "trials >= 2 default" METHOD item above.
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

- **Task battery on the HTML card** (READOUT, Cycle 6 follow-up): the
  `battery_summary` ships terminal + JSON only. Render a per-intent coverage grid
  + `cross_task_spread` pill on the HTML scorecard (`scorecard._reliability` is
  the template; both layouts) — same terminal-first-then-HTML deferral quotability
  took. Additive, no version bump.

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
