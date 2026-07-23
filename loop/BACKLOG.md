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
  NOW HAS AN EXECUTABLE SPEC (Cycle 7): `tests/test_attribution.py::
  test_reputation_gate_phrasing_is_current_coverage_gap` pins that codex
  REPUTATION-gate refusals ("flagged as unsafe" / "unable to browse") are
  currently NOT caught by `_ENV_BLOCK_RE` (they lack the security-* vocabulary),
  so such a run is mis-scored as a site FAIL rather than reachability. FIRST
  `[LOCAL]` step is now tiny and precise:
  ```
  # 1 codex exec against the canonical .com, capture RAW refusal text, COMMIT it:
  codex exec --model o4 'Browse https://driftflight.com read-only and report
    whether an agent could purchase there; if you cannot browse it, say why.' \
    > runs/local/codex_refusal_driftflightcom_<ts>.txt
  ```
  Then extend `_ENV_BLOCK_RE` with a fixture drawn from the committed transcript
  (worded by CAPABILITY — "the hosting stack's own reputation layer refused the
  URL" — never by vendor), keeping test #2 (site-side 403/Cloudflare NOT excused)
  green, and update test #8 in lockstep. The regex change is scoring-adjacent
  (moves runs between denominators) → peer-gated PR, not direct-to-main.
  NOTE (07:50Z local fire): the NARROW lexical subset — "browser **safety**
  controls" (same env-block family as "security", not a semantic reputation gate)
  — now HAS committed transcript evidence and is split out as its own P0 directly
  below; this item retains the HARDER semantic reputation-gate case (test #8).
- **Env-block attribution leak — broaden `_ENV_BLOCK_RE` to cover "safety"
  phrasing** (METHOD, attribution honesty; PEER-GATED scoring-semantics change).
  DISCOVERED 2026-07-23T07:50Z local fire via the trial-count run (see LOG +
  `experiments/trial_count_N_analysis.py`). `asrs/behavioral/shopper.py`
  `_ENV_BLOCK_RE` matches only "security" phrasings, so a codex run that reported
  its browser "**safety** controls" blocked the site (codex t3 on drift-flight.org)
  is NOT recognized as env-blocked → its all-false verdict (the agent observed
  NOTHING) leaks into the outcome/trust scoring denominators instead of the
  reachability signal. Invariant #4 violation; it under-credits the site and
  corrupts `panel_reliability` (turned a stable claude-only panel "mixed").
  - FIX (exact): extend the regex so "safety" is a sibling of "security"
    (`browser (?:security|safety)` and `(?:security|safety) (?:policy|controls|
    grounds)`) in BOTH alternations. The validated pattern is in
    `experiments/trial_count_N_analysis.py` (`_ENV_BLOCK_FIXED`); it re-classifies
    codex t3 as env-blocked and makes the drift-flight.org curve monotone/stable
    (N=2 0.80 → 5 0.92). Keep it vendor-neutral: it keys on the block phrasing,
    never a domain.
  - TEST: add to `tests/test_reliability.py` (or a shopper test) a run whose
    blocker says "blocked by browser safety controls" with all-false checkpoints →
    assert `_is_env_blocked` True and that it is excluded from `_valid_runs` /
    outcome denominators and counted in `hosted_agent_reachability`.
  - WHY PEER-GATED: `_is_env_blocked` gates which runs enter the behavioral
    scoring denominator — an aggregation rule. Per invariant #2 this bumps the
    rubric version (v0.5 → v0.6, dated changelog: "env-block attribution now
    recognizes 'safety'-phrased hosted-browser refusals, not only 'security'").
    Behavioral-only: the canonical STATIC delta (+39.4) is unaffected by
    construction (static mode runs no panel) — show that in the PR.
  - Open PR `loop/env-block-safety-phrasing` with the analysis artifact as
    evidence; next cycle adversarially reviews + self-merges. Slack heads-up on
    open (sensitive class: aggregation + version bump).

<!-- EXECUTED 2026-07-23T07:50Z (local fire): "[LOCAL] What trial count N
     stabilizes the panel" — ran a live claude+codex×5 panel on drift-flight.org
     (nested first-N subsample design, experiments/trial_count_N.py). Answered
     for the single-model case: drift-flight.org is verdict-stable from N=2,
     converging 0.80→0.92 by N=5 once the env-block leak above is fixed. The run
     ALSO surfaced that leak (now the P0 above). Evidence:
     runs/local/trial_stability_20260723T064359Z.json. REMAINING work below. -->
- **[LOCAL] Cross-model panel-stability N-curve** (TRUTH/METHOD, remaining half of
  the trial-count item): the 07:50Z run measured claude-only reproducibility
  because codex env-blocked drift-flight.org on all 5 trials. The CROSS-MODEL
  agreement question (do claude and codex converge on the same verdict, and at
  what N) is unmeasured and BLOCKED on codex reachability — do the
  codex-reachability/control-storefront item FIRST (feed codex pre-fetched content
  when its browser is gated, marked assisted), then re-run the nested-subsample
  harness on a domain codex can actually reach:
  ```
  git checkout main && git pull
  .venv/bin/python -m experiments.trial_count_N   # reuse the ONE-run N-curve harness
  # (edit DOMAIN to a codex-reachable storefront; ~5 codex + 5 claude, within budget)
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
