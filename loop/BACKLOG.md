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
  NOTE: the NARROW lexical subset — "browser **safety** controls" (same env-block
  family as "security", not a semantic reputation gate) — SHIPPED in PR #2
  (Cycle 9, v0.6, awaiting merge). This item retains ONLY the HARDER semantic
  reputation-gate case (test #8: "flagged as unsafe" / "unable to browse"), which
  still needs a committed codex transcript before its regex fixture can be added.
<!-- MERGED 2026-07-23 (PR #2, commit 8fe9f46): "Env-block attribution leak —
     broaden `_ENV_BLOCK_RE` to cover 'safety' phrasing" is now on main as rubric
     v0.6. Regex extended so "safety" is a sibling of "security" in both
     alternations; tests/test_attribution.py +test #9 (fixtures verbatim from
     runs/local/trial_stability_20260723T064359Z.json). Suite 58/58 on merged main.
     NOTE: merged externally mid-fire, so the loop's fresh-context peer review was
     bypassed — hence the post-merge sanity check below. -->
- **Post-merge adversarial sanity check for v0.6 (PR #2)** (METHOD, peer-gate
  hygiene). PR #2 was merged externally before the loop's fresh-context review
  could run. Next cycle (or whenever convenient) should adversarially re-verify
  from scratch: (a) vendor-neutral wording — keys on phrasing, never a domain;
  (b) negative direction intact — site-side 403/Cloudflare/429/CAPTCHA/robots and
  reputation-gate phrasings ("flagged as unsafe"/"unable to browse") still NOT
  excused (tests #2/#8 green); (c) fixtures trace to committed evidence; (d) static
  canonical delta unchanged (scoring.py never imports the classifier). If a real
  defect surfaces, revert on main (invariant #5: revert, never force-push) and
  reopen as a fresh PR. Cheap — offline, no network.
- **[LOCAL] Live behavioral re-score of v0.6** (METHOD follow-up; v0.6 is now on
  main): run one behavioral panel on a domain and confirm a "safety"-blocked codex
  run routes to `hosted_agent_reachability` (not outcome) LIVE, and that
  `panel_reliability` on the drift-flight.org trial-count panel reads
  stable/monotone (N=2 0.80 → 5 0.92) rather than "mixed". Reuse
  `experiments/trial_count_N.py`. Budget: one panel.

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

<!-- DONE 2026-07-23T08:15Z (Cycle 8, READOUT): "Quotability on the JSON/HTML card"
     SHIPPED. Additive `Report.quotability` field (asrs/types.py), populated in
     cli._evaluate from the same pure `asrs.reliability.quotability` for every mode;
     `scorecard._quotability` + `_QUOTABILITY_BANDS` render a Citable/Provisional
     pill card under the overview in BOTH layouts (not-scorable/absent -> no card).
     Display-only, rubric stays v0.5, scoring source byte-for-byte unchanged.
     tests/test_readout.py 8/8 (+3); suite 54 -> 57. See LOG Cycle 8. -->

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
  ESCALATED (Cycle 8): this noise now causes a DOWNSTREAM BUG, not just clutter.
  The hourly `loop/local_verify.py` runner's live-re-score capture is BROKEN — its
  `scores` block records `FileNotFoundError` because the `[asrs.scoring] warning:`
  stderr lines leak into the score-path argument it passes (seen in
  verify_20260723T040714Z / …040757Z.json). The runner's TEST block is green and
  the live delta is still confirmed by manual local fires, but its automated
  canonical re-score is non-functional. Suppressing the expected-absent warnings
  (route them through a logger, not raw stderr, or gate on --behavioral) fixes the
  runner AT THE SOURCE — bumped in priority for that reason.
