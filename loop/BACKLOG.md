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
<!-- DONE 2026-07-23T11:42Z (local fire, TRUTH): "Codex reachability investigation —
     CHARACTERIZE" discharged via experiments/codex_reachability.py (committed;
     5 codex invocations, canonical pair ×2 + example.com control ×1, all HTTP 200).
     FINDINGS: (1) codex refused 4/4 canonical trials, every refusal a REPUTATION
     gate (domain age .com 7d/.org 3d + absent footprint) but ALWAYS surfaced with
     browser-{safety,security} vocabulary. (2) v0.6 caught 4/4 (_is_env_blocked True
     → reachability, none mis-scored FAIL) — first LIVE validation of v0.6 on fresh
     transcripts. (3) Reputable control example.com NOT blocked (browser works) → the
     refusals are codex's own reputation gate, not a broken browser. (4) NO pure
     semantic-reputation phrasing captured → test #8 stays open; NO regex broadening
     warranted (v0.6 sufficient; blind broadening would risk excusing real site
     blocks). (5) The harness's "1 leak candidate" was a FALSE POSITIVE (example.com;
     report-only heuristic over-catches "nothing to buy" runs — diagnostic-only, not
     scoring). Evidence: runs/local/codex_reachability_20260723T114225Z/
     {summary.json,transcripts/}. See LOG. REMAINING work (the BUILD) is now its own
     item below; the test-#8 regex fixture stays PARKED until a semantic transcript
     appears (none across all fires to date). -->
- **[LOCAL] Build the codex control-storefront / pre-fetched-content attribution
  fix** (TRUTH; unblocks the cross-model N-curve). The 11:42Z characterization
  proved codex's browser WORKS on a reputable domain (example.com) and gates BOTH
  fresh canonical domains — so the variable is domain reputation, not codex. Build
  the v0-notes fix: when codex's browser gate fires (`_is_env_blocked` True), feed
  it the statically-fetched homepage + docs (via `asrs.fetch`), mark the run
  `assisted`, and keep assisted runs OUT of the UNASSISTED reachability denominator
  (do not let assisted evidence inflate a site's autonomous-reachability score).
  Design in-cloud from the committed transcripts; execute `[LOCAL]`. This is
  scoring-adjacent (adds an evidence provenance dimension) → likely peer-gated when
  the scoring path changes; the fetch-and-mark plumbing itself can land direct.
  test-#8 regex fixture stays PARKED — no semantic reputation-gate transcript
  ("flagged as unsafe"/"unable to browse" WITHOUT browser-safety words) has ever
  been observed; do NOT broaden `_ENV_BLOCK_RE` on speculation.
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
  what N) is unmeasured and BLOCKED on codex reachability — RE-CONFIRMED blocked
  at 11:42Z (codex gated 4/4 on BOTH canonical domains). Do the "Build the codex
  control-storefront / pre-fetched-content attribution fix" item above FIRST, then
  re-run the nested-subsample harness on a domain codex can actually reach:
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

<!-- DONE 2026-07-23T12:18Z (Cycle 12, READOUT): "Task battery on the HTML card"
     SHIPPED. `scorecard._battery(rep)` renders a "Task battery" card — cross-task-spread
     verdict pill (Consistent/Somewhat/Intent-dependent, thresholds 0.15/0.35 mirroring
     the terminal `report._battery_lines`), a per-intent coverage grid (intent, archetype
     chip, completion bar + %, valid-run count; no-signal -> "no signal"), AND the Cycle-10
     `per_kind` by-archetype rollup (completion + within-kind spread + intents), shown only
     when >1 kind. Wired into BOTH layouts (`_domain_column`, `_section_rows`), after Panel
     reliability. Additive/display-only, rubric stays v0.6, scoring path byte-for-byte
     untouched (canonical delta unchanged by construction); direct-to-main.
     tests/test_readout.py 8/8 -> 12/12; suite 64 -> 68. Live-data follow-up folded into
     the [LOCAL] second cross_task_spread datapoint (P0) — the first live report to carry
     per_kind, so the by-archetype grid can be eyeballed on a real card. See LOG Cycle 12. -->

- **[LOCAL] Eyeball the battery card on a real multi-kind report** (READOUT, Cycle 12
  follow-up): the HTML battery card now exists but has only ever rendered synthetic
  fixtures. When the [LOCAL] second cross_task_spread datapoint runs (below/P0), pass its
  report through `scorecard.build_scorecard` and confirm the per-intent grid + by-archetype
  rollup read correctly on real multi-kind data. No new code — a render + visual check.

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

<!-- DONE 2026-07-23T13:18Z (Cycle 13, METHOD): "Coverage-warning noise" fixed AT SOURCE.
     asrs/scoring.py routes the three coverage warnings through logging.getLogger(
     "asrs.scoring") instead of raw print(file=sys.stderr); the noisy "absent rubric check"
     warning is split by _is_behavioral_only(check) (whole outcome pillar +
     trust_panel_willingness/trust_live_session) → behavioral-only absences at DEBUG
     (expected absent in static, silent under Python's default WARNING lastResort), genuine
     static gaps at WARNING (still on stderr). A realistic static run now emits ZERO warning
     lines (was ~12) → real gaps un-buried AND the local_verify.py stderr→score-path leak
     (the escalated Cycle-8 downstream bug) has no source; the runner's re-score capture will
     work when it's restarted. NOT a scoring-semantics change (arithmetic byte-for-byte
     unchanged, rubric v0.6, canonical delta unchanged by construction); direct-to-main.
     tests/test_scoring.py 7/7 → 11/11 (+4, logger-capture handler); suite 68 → 72. See LOG. -->

- **[LOCAL] Runner robustness: don't merge stderr into the score-path arg** (METHOD,
  Cycle 13 follow-up — belt-and-suspenders after the source fix above). The Cycle-13 fix
  removed the coverage-warning SOURCE, so a normal static run's stderr is now clean and the
  `local_verify.py` re-score capture should succeed. But the runner is still fragile: it
  builds the score-path from captured output, so ANY future stderr line (a genuine coverage
  WARNING, a probe-crash line, a deprecation) would re-break it. Harden the runner to read
  the score JSON from a known path / stdout-only channel rather than parsing mixed
  stdout+stderr. Needs the runner restarted first (currently DOWN, >9h). Execute [LOCAL] on
  Jonah's machine.
