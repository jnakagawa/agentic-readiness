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

<!-- DONE 2026-07-23T10:13Z (local cycle, COVERAGE): "[LOCAL] Task battery — first
     live behavioral run" EXECUTED on drift-flight.org. Budget-trimmed to a new
     3-archetype battery (batteries/trimmed_v1.yaml: digital_service / subscription
     / physical_good) × {claude,codex} × 2 trials = 12 panels / 6 codex (under cap).
     FIRST live cross_task_spread = 0.089 ("consistent across intents"): readiness
     holds across intents (image_generation 53% / api_subscription 60% /
     physical_good 40% avg checkpoint completion; 3/3 intents observed). Primary
     (image_generation) overall 45.1 F (rubric 0.6), panel_reliability 0.87 stable,
     quotability = CITABLE (reproducible). Invariant #1 verified: EXACTLY ONE
     free-tier transaction for the whole battery (blob count 7->8). Also live-validated
     the just-merged v0.6: codex#1's "rejected by the browser's site-safety policy"
     was correctly excluded from the denominator (4->3 valid) and routed to
     hosted-agent reachability. NOTE: run predates the Cycle-10 per_kind rollup (its
     report has no per_kind block; cross_task_spread is unaffected). Evidence
     (force-added; runs/ is gitignored):
     runs/local/battery_trimmed_driftflightorg_20260723T101121Z.{json,card.txt}.
     See LOG. Follow-up candidate below. -->
- **[LOCAL] Second cross_task_spread datapoint** (COVERAGE, follow-up to the first
  live battery run): one datapoint is not a population. Re-run the battery on (a)
  the canonical `.com` (driftflight.com — does the with-rails side hold the same
  cross-intent consistency, and at what completion level? one pair of spreads makes
  the delta a STRUCTURAL claim, not a per-task artifact) and/or (b) the full
  5-intent `batteries/default_v1.yaml` on drift-flight.org for the two dropped
  archetypes (text_translation, data_enrichment). This ALSO exercises the Cycle-10
  `per_kind` rollup on live multi-kind data for the first time. Budget: ONE domain
  per fire, trimmed battery preferred. Reuse the first-run pattern (`--battery <yaml>
  --models claude,codex --trials 2`); force-add the report to `runs/local/`
  (`runs/` is gitignored).
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
  family as "security", not a semantic reputation gate) — SHIPPED as PR #2 (Cycle 9,
  v0.6) and is now MERGED to main (reviewed + merged by the 10:13Z local cycle;
  live-validated same fire — codex "site-safety policy" routed to reachability).
  This item retains ONLY the HARDER semantic reputation-gate case (test #8:
  "flagged as unsafe" / "unable to browse"), which still needs a committed codex
  transcript before its regex fixture can be added. NEW EVIDENCE (10:13Z battery
  run): codex#2 REACHED drift-flight.org normally on the same fire codex#1 was
  safety-blocked — so the `.org` reputation gate is NON-DETERMINISTIC per-trial,
  not a hard block (updates the open question).
<!-- MERGED 2026-07-23T~09:47Z (PR #2, commit 8fe9f46): "Env-block attribution leak
     — broaden `_ENV_BLOCK_RE` to cover 'safety' phrasing" is on main as rubric v0.6.
     Regex extended so "safety" is a sibling of "security" in both alternations;
     tests/test_attribution.py +test #9 (fixtures verbatim from
     runs/local/trial_stability_20260723T064359Z.json). Suite 58/58 at merge (60 after
     Cycle 10). Reviewed + merged by the 10:13Z local cycle's first-duty peer-gate
     review (the concurrent cloud addendum's "merged externally / review bypassed"
     framing is superseded — the review WAS performed; see the DONE note below). -->
<!-- DONE 2026-07-23T10:13Z (local cycle): "Post-merge adversarial sanity check for
     v0.6 (PR #2)" DISCHARGED — this WAS the local fire's first-duty peer-gate
     review (not a bypassed merge). Verified from fresh context: (a) vendor-neutral
     (keys on phrasing, no domain/vendor); (b) NEGATIVE DIRECTION intact — a LIVE
     old-vs-new regex A/B confirmed committed site-side blocks
     (403/CF/429/CAPTCHA/robots/WAF) AND reputation-gate phrasings ("flagged as
     unsafe"/"unable to browse") stay NOT-excused (tests #2/#8 green); (c) both
     test #9 fixtures trace VERBATIM to runs/local/trial_stability_20260723T064359Z.json
     (invariant #3); (d) LIVE static canonical re-score unchanged (46.1/85.5, +39.4;
     reports now embed rubric "0.6"). One residual → P1 (site-side "…safety/security
     policy" false-positive is pre-existing/symmetric, not a regression). Verdict:
     SURVIVED → merged. See LOG. -->
<!-- OFFLINE HALF DONE 2026-07-23T11:15Z (Cycle 11, TRUTH): the data-recompute half
     of "Confirm the trial-count panel reads stable post-v0.6" is DISCHARGED in-cloud.
     tests/test_trial_stability_v06.py (4/4) recomputes the committed 06:44Z panel
     through the SHIPPED panel_reliability/_is_env_blocked: all 5 codex runs (incl.
     t3, the original leak) env-blocked, valid pool claude-only, corrected curve
     monotone + "stable" at every N>=2 (0.80 → 0.867 → 0.90 → 0.92), superseding the
     artifact's pre-v0.6 curve at N>=3. trial_count_N_analysis.py de-staled. See LOG. -->
- **[LOCAL] Fresh live 5-trial panel post-v0.6** (METHOD follow-up; the LIVE half
  remaining after Cycle 11 pinned the offline recompute). Re-run
  `experiments/trial_count_N.py` on a NEW drift-flight.org 5-trial panel and confirm
  the verdict-stability curve reads monotone/stable END-TO-END under merged v0.6 on
  fresh runs (not just recomputed from the 06:44Z artifact). Distinct value over the
  offline pin: catches any live env-block phrasing the fixture set doesn't cover.
  Budget: one panel (reuses the ONE-run N-curve harness).

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
- **Env-block classifier: harden against site-side "safety/security policy"**
  (METHOD, attribution honesty — residual from the PR #2 adversarial review,
  2026-07-23T10:13Z). The review confirmed `_ENV_BLOCK_RE` correctly rejects the
  committed site-side fixtures (403/Cloudflare/429/CAPTCHA/robots/WAF) AND that the
  "safety" broadening is symmetric with the already-shipped "security" handling —
  but a HYPOTHETICAL site-side block worded "…blocked by our safety policy" /
  "…security controls" would still be mis-excused as environment. This is a
  PRE-EXISTING approximation (not introduced by v0.6): the classifier reads the
  agent's narration of ITS OWN tool gate, and genuine site blocks narrate as
  HTTP-status/CF/CAPTCHA (test #2). Hardening idea: require agent-tool
  self-reference proximity (anchor "browser"/"my browser"/tool name near the block
  phrase) so "OUR safety policy" (site-side) is distinguished from "the BROWSER's
  safety policy" (agent-side). Scoring-adjacent → peer-gated + version bump when
  done. Low urgency (no observed real mis-attribution yet), but it is the honest
  known limit of the classifier.
- **Nested shopper spawns the full user MCP fleet** (METHOD/efficiency, observed
  2026-07-23T10:13Z during the battery run). Each `claude -p` shopper subprocess
  (`asrs.behavioral.shopper._claude_cmd`) inherits the operator's full MCP config —
  it was seen spawning trigger.dev, mcp-for-unity, linear, and motherduck servers
  before browsing, adding ~1 min of startup PER PANEL (12 panels ≈ 12 min of pure
  MCP boot) and pulling unrelated external connections into the measurement
  environment. The shopper only needs to browse a storefront; it should run with a
  minimal/empty MCP config (`--mcp-config` none / `--strict-mcp-config`) for speed
  AND cleanliness. Behavioral-execution-only (no scoring semantics) →
  direct-to-main safe; verify a panel still produces identical checkpoints after.

## P2

<!-- DONE 2026-07-23T08:15Z (Cycle 8, READOUT): "Quotability on the JSON/HTML card"
     SHIPPED. Additive `Report.quotability` field (asrs/types.py), populated in
     cli._evaluate from the same pure `asrs.reliability.quotability` for every mode;
     `scorecard._quotability` + `_QUOTABILITY_BANDS` render a Citable/Provisional
     pill card under the overview in BOTH layouts (not-scorable/absent -> no card).
     Display-only, rubric stays v0.5, scoring source byte-for-byte unchanged.
     tests/test_readout.py 8/8 (+3); suite 54 -> 57. See LOG Cycle 8. -->

- **Task battery on the HTML card** (READOUT, Cycle 6/10 follow-up): the
  `battery_summary` ships terminal + JSON only. Render a per-intent coverage grid
  + `cross_task_spread` pill on the HTML scorecard (`scorecard._reliability` is
  the template; both layouts) — same terminal-first-then-HTML deferral quotability
  took. Additive, no version bump. NOW ALSO render the Cycle-10 `per_kind`
  by-archetype rollup (mean completion + within-kind spread per storefront type),
  shown only when the battery spans >1 kind — mirrors the terminal
  `by archetype:` sub-block (`report._battery_lines`).

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
