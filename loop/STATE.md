# Loop state

- Cycle counter: 14
- Started: 2026-07-23 (UTC)
- Focus pointer: TRUTH (rotate METHOD → COVERAGE → TRUTH → READOUT)
  (Cycle 1 METHOD, Cycle 2 COVERAGE, Cycle 3 TRUTH, Cycle 4 READOUT,
  Cycle 5 METHOD, Cycle 6 COVERAGE, Cycle 7 TRUTH, Cycle 8 READOUT,
  Cycle 9 METHOD, Cycle 10 COVERAGE, Cycle 11 TRUTH (cloud: trial-count panel
  pinning) + local fire 11:42Z TRUTH (codex reachability investigation, ran
  concurrently), Cycle 12 READOUT (task-battery card on the HTML scorecard),
  Cycle 13 METHOD (coverage-warning noise fixed at source — logging + behavioral-only
  classifier; unblocks the local runner's re-score capture),
  Cycle 14 COVERAGE (commerce-protocol ACP/UCP credit requires a validated manifest —
  peer-gated PR #3, rubric v0.6→v0.7); next cycle takes TRUTH — BUT its FIRST duty is
  the fresh-context adversarial review + self-merge of PR #3 before picking TRUTH work.)
- Rubric: **v0.6 on main** (PR #2 MERGED 2026-07-23T~09:47Z, merge commit 8fe9f46,
  clean fast-forward). v0.6 broadens the env-block classifier to recognize
  "safety"-phrased hosted-browser refusals (aggregation rule → version bump).
  RECONCILED (10:13Z local cycle): PR #2 was reviewed + merged by THIS LOCAL FIRE's
  first-duty peer-gate review — the playbook-mandated fresh-context adversarial
  review DID run (fixtures traced to committed evidence per invariant #3, full
  suite 58/58 on the branch, a LIVE old-vs-new regex A/B confirming the negative
  direction — site-side 403/CF/429/CAPTCHA/robots/WAF + reputation-gate phrasings
  still NOT excused, and a LIVE static re-score 46.1/85.5 delta +39.4 with reports
  now embedding "0.6"). The concurrent Cycle-9 cloud addendum (a70923f, fired
  ~simultaneously at 09:47Z) labeled the merge "external / peer-review bypassed"
  because it could not observe the local review; that characterization is
  SUPERSEDED — the review was performed, and the post-merge sanity-check P0 it
  queued is DISCHARGED (see LOG + BACKLOG). One residual (site-side "…safety/
  security policy" false-positive surface) is pre-existing/symmetric with the
  shipped "security" handling, logged P1. Rubric was UNCHANGED by Cycles 2–4/6/8
  (diagnostic/readout layers, not scoring-semantics changes).
- Task battery: format + aggregation landed Cycle 2; `--battery` CLI wiring +
  additive `Report.battery_summary` + terminal `TASK BATTERY` section landed
  Cycle 6 (`asrs/cli.py` `_run_behavioral(..., battery=)` runs the shopper panel
  once per intent, first task = primary scoring run, free-tier once for the whole
  battery; `asrs/report.py _battery_lines`; `tests/test_battery_wiring.py` 4/4,
  synthetic panel). NOT a scoring-semantics change (rubric stays v0.5, scoring.py
  untouched). FIRST LIVE RUN DONE (local cycle 2026-07-23T10:13Z): a trimmed
  3-archetype battery (`batteries/trimmed_v1.yaml`) × {claude,codex} × 2 trials on
  drift-flight.org produced the benchmark's first `cross_task_spread` = **0.089**
  ("consistent across intents"; image_generation 53% / api_subscription 60% /
  physical_good 40% avg completion, 3/3 observed; primary 45.1 F / panel 0.87
  stable / quotability CITABLE; invariant #1 held — exactly 1 free-tier tx for the
  whole battery). Evidence:
  `runs/local/battery_trimmed_driftflightorg_20260723T101121Z.{json,card.txt}`.
  REMAINING: a SECOND cross_task_spread datapoint (driftflight.com / the full
  5-intent battery — P0 [LOCAL]). The HTML scorecard battery card SHIPPED Cycle 12
  (see below), so the only battery gap left is live multi-kind data on a real card.
  Cycle 10 (COVERAGE) added the PER-ARCHETYPE (`kind`) rollup the module docstring
  + battery YAML had promised but never implemented: `BatteryKindResult` +
  additive `BatterySummary.per_kind` (`asrs/battery.py` `_per_kind_results` /
  shared `_cross_task_spread` helper) + a `by archetype:` terminal sub-block
  (`report._battery_lines`, shown only when >1 kind). Lets the SAME run read
  "strong on digital_service, weak on physical_good" instead of one battery-wide
  spread — north-star storefront-type flexibility. Diagnostic-only (rubric stays
  v0.6, scoring.py/static path untouched → canonical delta unchanged by
  construction); direct-to-main. `tests/test_battery.py` 6/6 → 8/8; suite 58 → 60.
  Per-kind ships terminal + JSON; the HTML by-archetype grid joins the queued P2.
- Task-battery HTML card (Cycle 12, READOUT): `scorecard._battery(rep)` renders the
  additive `battery_summary` on the HTML scorecard — a "Task battery" card with a
  cross-task-spread verdict pill (Consistent / Somewhat / Intent-dependent, thresholds
  0.15/0.35 mirroring the terminal `report._battery_lines`), a per-intent coverage grid
  (intent, archetype chip, completion bar + %, valid-run count; no-signal -> "no signal"),
  and the Cycle-10 `per_kind` by-archetype rollup (completion + within-kind spread +
  intents), shown only when >1 kind. Wired into BOTH layouts (`_domain_column`,
  `_section_rows`), placed after Panel reliability. Same terminal->JSON->HTML deferral
  quotability/reliability took; the battery card was the last diagnostic still
  terminal/JSON-only. Additive/display-only -> rubric stays v0.6, scoring path
  byte-for-byte untouched (canonical delta unchanged by construction); direct-to-main.
  `tests/test_readout.py` 8/8 -> 12/12; suite 64 -> 68. The queued [LOCAL] second
  cross_task_spread datapoint will be the first live report carrying per_kind, so the
  by-archetype grid can finally be eyeballed on a real card.
- Coverage-warning noise (Cycle 13, METHOD): fixed AT THE SOURCE. `asrs/scoring.py`
  no longer `print(..., file=sys.stderr)`s coverage warnings — they route through
  `logging.getLogger("asrs.scoring")`, and the noisy "absent rubric check" warning is
  split by a new `_is_behavioral_only(check)` classifier (whole `outcome` pillar +
  `trust_panel_willingness`/`trust_live_session`): behavioral-only absences → DEBUG
  (expected in static mode, silent under Python's default WARNING-level lastResort),
  genuine static gaps → WARNING (still on stderr, unchanged). A realistic static run now
  emits ZERO warning lines (was ~12), so real gaps aren't buried AND the `local_verify.py`
  runner's stderr-into-score-path leak (the ESCALATED Cycle-8 downstream bug) has no
  source to leak — WHEN the runner is restarted its live re-score capture will work.
  NOT a scoring-semantics change (warning routing + a verbosity classifier never read by
  the math; scoring arithmetic byte-for-byte unchanged, rubric stays v0.6, canonical delta
  unchanged by construction); direct-to-main. `tests/test_scoring.py` 7/7 → 11/11 (+4,
  logger-capture handler); suite 68 → 72.
- Attribution boundary (Cycle 7, TRUTH): `tests/test_attribution.py` (8/8) pins
  invariant #4 directly for the first time — `asrs/behavioral/shopper._is_env_blocked`
  (`_ENV_BLOCK_RE`) + `_aggregate` denominator routing. Adds the previously-zero
  negative-direction coverage (site-side 403/Cloudflare/429/CAPTCHA NOT excused as
  environment) and pins the v0.4 env-blocked→reachability routing + all-blocked→
  CANT_TEST-not-FAIL. Test #8 documents the OPEN gap as an executable spec: codex
  hosted-browser REPUTATION-gate refusals ("flagged as unsafe" / "unable to browse")
  lack the security-* vocabulary and are NOT yet classified env-blocked — deliberately
  not regex-broadened in-cloud (no committed transcript; blind broadening risks
  excusing real site blocks). Tests-only, no scoring-semantics change, rubric stays
  v0.5. Resolving #8 is the queued [LOCAL] codex investigation.
- Panel reliability: `asrs/reliability.py` (within-panel verdict-stability) +
  render section landed Cycle 3. Cycle 4 attached it to the JSON `Report`
  (additive `panel_reliability` field, populated in `cli._evaluate`) and the HTML
  scorecard (`scorecard._reliability`, both layouts). Reproducibility now travels
  with the score everywhere it goes.
- Quotability gate (Cycle 5, METHOD): `asrs.reliability.quotability(report)` ->
  `Quotability(quotable, tag, reason, verdict_stability)` classifies whether the
  headline number is CITABLE or PROVISIONAL (static-deterministic / reproducible /
  provisional-single-trial / provisional-unstable / behavioral-unobserved /
  not-scorable). Surfaced as one `QUOTABILITY:` line under OVERALL in the terminal
  card (`report._quotability_lines`). `--trials` default 1 -> 2 (multi-trial by
  default; free-tier probe still runs once). NOT a scoring-semantics change — no
  version bump, scoring.py/rubric untouched.
  Cycle 8 (READOUT) attached it to the JSON `Report` (additive `quotability` field,
  populated in `cli._evaluate` from the same pure function for every mode) and the
  HTML scorecard (`scorecard._quotability` + `_QUOTABILITY_BANDS`: a Citable/
  Provisional pill card under the overview in BOTH layouts; not-scorable/absent ->
  no card). Same terminal->JSON->HTML deferral the reliability metric took
  (Cycle 3->4). Additive/display-only; rubric stays v0.5, scoring source
  byte-for-byte unchanged (score-unchanged pinned by test_quotability + an
  end-to-end smoke). tests/test_readout.py now 8/8 (+3 quotability surfacing
  tests). Suite 54 -> 57. The quotability code path is now fully surfaced
  everywhere the score travels (terminal + JSON + HTML), matching reliability.
- Canonical pair: drift-flight.org 46.1 F vs driftflight.com 85.5 B — delta
  +39.4. Confirmed LIVE again this local fire (2026-07-23T07:50Z, both HTTP 200),
  identical to the 05:52Z merge-verify and the hourly verify artifact
  verify_20260723T040757Z.json. Loop-start behavioral baseline was +40.6 (delta
  within static variance). UNCHANGED BY CONSTRUCTION at Cycle 8, Cycle 9 (PR #2
  behavioral-only), and Cycle 10 (per-kind battery rollup is diagnostic-only;
  scoring.py/static path untouched → static delta cannot move). The 10:13Z local
  cycle re-confirmed the delta LIVE on the v0.6 PR branch as the merge-gate
  re-score (46.1 F / 85.5 B, +39.4; reports now embed rubric "0.6", version bump
  propagates). RE-CONFIRMED AGAIN LIVE 2026-07-23T11:50Z (local fire, both HTTP
  200): 46.1 F / 85.5 B, delta **+39.4** on rubric v0.6 — the codex-reachability
  experiment touched no scoring code, so the delta is unchanged by construction AND
  measured; doubles as a fresh live signal while the runner is down. RUNNER HEALTH
  (11:42Z, re-confirmed): **STILL DOWN.** Newest verify artifact is
  verify_20260723T040757Z (04:07Z, rubric 0.5) — now **~7.7h old, well past the 6h
  threshold**; no :41 artifact 05:00–11:00Z. The local `local_verify.py` runner
  (launchd, hourly :41 on Jonah's machine) appears stopped. To be flagged in the
  next Slack daily digest (first cycle after 16:00 UTC) per the comms policy — the
  next live canonical re-score signal depends on it or on a manual local fire.
  RE-CONFIRMED DOWN Cycle 11 (11:15Z): newest still verify_20260723T040757Z, now
  ~7h08m old. RE-CONFIRMED DOWN Cycle 13 (13:18Z): newest still verify_20260723T040757Z,
  now **~9.2h old** (past 6h); still before 16:00 UTC so no digest yet — folds into the
  next post-16:00 Slack digest.
  SEPARATE BUG (the coverage-warning stderr leak): FIXED AT SOURCE Cycle 13. The runner's
  `scores` block recorded FileNotFoundError because `[asrs.scoring]` stderr coverage-warning
  lines leaked into the score-path argument; `asrs/scoring.py` no longer prints those lines
  on a normal static run (routed to logging; behavioral-only absences → DEBUG). So WHEN the
  launchd runner is restarted, its live re-score capture will work. Its TEST block was
  already green; the live delta stays confirmed by the manual local fires. Residual belt-
  and-suspenders (runner should not merge stderr into a path arg) is a [LOCAL] follow-up.
- Trial-count post-v0.6 (Cycle 11, TRUTH): the OFFLINE (data-recompute) half of
  the "confirm the trial-count panel reads stable post-v0.6" P0 is now DISCHARGED
  in-cloud and pinned. `tests/test_trial_stability_v06.py` (4/4) recomputes the
  committed 06:44Z panel through the SHIPPED `panel_reliability`/`_is_env_blocked`:
  all 5 codex runs (incl. t3, the original "safety controls" leak) are env-blocked,
  valid pool is claude-only, and the corrected curve is monotone + "stable" at every
  N>=2 (0.80 → 0.867 → 0.90 → 0.92) — vs the artifact's superseded pre-v0.6 curve
  (0.80 → 0.60 → 0.68 → 0.733) at N>=3. `experiments/trial_count_N_analysis.py`
  de-staled (its "proposed (not shipped)" fix is now the shipped regex; section (1)
  reads "SUPERSEDED (v0.6 fix)" not "reproduction FAILED"). No scoring semantics;
  suite 60 → 64; direct-to-main. REMAINING [LOCAL]: a FRESH live 5-trial panel and
  the still-open CROSS-MODEL question (codex has never reached a canonical domain).
- Trial-count / panel-stability (local fire 2026-07-23T07:50Z, TRUTH/METHOD):
  executed the P0 [LOCAL] N-sweep item via an orphaned live claude+codex×5 panel
  on drift-flight.org (interrupted ~06:44Z fire; artifact adopted after
  adversarial provenance + deterministic reproduction — see LOG + experiments/).
  FINDING: the panel's verdict-stability curve was corrupted by an env-block
  attribution LEAK — codex trial 3 said its browser "safety controls" blocked the
  site, but `shopper._ENV_BLOCK_RE` matches only "security" phrasings, so that
  all-false verdict (agent saw NOTHING) leaked into the scoring pool (invariant #4
  violation). With the leak excluded the curve is monotone + stable
  (N=2 0.80 → 5 0.92); drift-flight.org converges from N=2 (claude-only, since
  codex was fully env-blocked). Fix (broaden the regex to cover "safety") is a
  scoring-semantics/aggregation change → PEER-GATED + version bump, queued P0 in
  BACKLOG with exact spec. Sole residual claude flip: found_purchase_path
  (t1 false vs t2–5 true) — legibility ambiguity, not noise.
- Rubric: **v0.7 on main** (PR #3 MERGED 2026-07-23T~14:2xZ, merge commit 72a2e5b).
  v0.7 requires a VALIDATED commerce manifest for the ACP/UCP partial on `x402_probe`
  (`_parse_commerce_manifest`, mirroring `_parse_x402`) — a real UCP service/capability
  manifest or ACP checkout payload, not any HTTP 200; a bare-200 SPA index/soft-404 at
  `/.well-known/ucp|agentic-commerce` no longer false-positives to 4.0. Validated hit
  relabeled `commerce-protocol-live`; marker tiers + ceiling unchanged; direction monotone
  non-increasing. (Rubric title-comment de-staled v0.6→v0.7 post-merge, same commit as this
  reconcile — the `version:` field was already 0.7.)
- Open PRs: **none.** PR #3 `loop/commerce-manifest-validation` (Cycle 14, COVERAGE,
  sensitive class: partial-credit rule + rubric v0.6→v0.7) was **MERGED EXTERNALLY**
  2026-07-23T~14:2xZ (commit 72a2e5b) — Jonah/an operator merged it directly during the
  SAME cloud fire that opened it, BEFORE the mandated next-cycle fresh-context adversarial
  review could run (exactly the Cycle-9/PR-#2 pattern). An external merge is ACTIVE consent
  (stronger than the veto-silence the playbook relies on), so this is not a bypass on the
  loop's part. RECONCILED post-merge THIS fire: pulled main, full suite **79/79 green** on
  the merge commit, v0.7 + `_parse_commerce_manifest` confirmed on main. Because the
  fresh-context review was pre-empted, it converts to a POST-merge duty for the NEXT cycle's
  FIRST duty: adversarially sanity-check v0.7 (retain-or-revert, not a pre-merge gate) AND
  run the queued P0 **[LOCAL] live v0.7 canonical re-score** (confirm 46.1 F / 85.5 B,
  +39.4, reports embed 0.7, no `commerce-protocol-*` on either canonical domain). Delta
  argued UNCHANGED by committed evidence (.com→x402-live never reaches the branch;
  .org→FAIL 0.0 no-agent-native-payment, `_commerce_protocol_evidence` already None); LIVE
  confirmation is the remaining check. https://github.com/jnakagawa/agentic-readiness/pull/3
- Prior PRs closed: PR #2 `loop/env-block-safety-phrasing` (Cycle 9, METHOD,
  sensitive class: aggregation rule + v0.5→v0.6) MERGED 2026-07-23T~09:47Z
  (commit 8fe9f46) by THIS local cycle's first-duty peer-gate review (adversarial
  review PASSED — see the Rubric bullet + LOG). The concurrent cloud addendum's
  "merged externally / review bypassed" note is superseded; the post-merge
  sanity-check P0 it queued is DISCHARGED. The [LOCAL] live behavioral re-score is
  now PARTIALLY discharged (this fire's battery run confirmed a "safety"-blocked
  codex run routes to reachability live); the trial-count-panel-stable confirmation
  remains queued. https://github.com/jnakagawa/agentic-readiness/pull/2
- PR #1 (Cycle 1 v0.5 NOT-SCORABLE fix) merged
  2026-07-23T03:00:15Z. Its [LOCAL] merge-time canonical re-score is now
  DISCHARGED: local fire 2026-07-23T05:52Z re-scored both reachable domains
  normally (46.1 F / 85.5 B, delta +39.4, NOT not-scorable) and confirmed the
  NOT-SCORABLE path via an unreachable-domain control (grade N/A, scored=False)
  — proving v0.5 is a no-op for reachable domains. Evidence:
  runs/local/merge_verify_pr1_20260723T055000Z.json. BACKLOG item removed.
  https://github.com/jnakagawa/agentic-readiness/pull/1

## Environment constraint (IMPORTANT — affects every cycle)

This cloud loop has **NO outbound network to external domains**: the agent
proxy denies CONNECT to drift-flight.org / driftflight.com / example.com / any
web host (403 "policy denial"). Confirmed 2026-07-23 via `asrs.fetch` and
`curl $HTTPS_PROXY/__agentproxy/status`. Consequences:
- The playbook's per-cycle LIVE static re-score of the canonical pair CANNOT
  run in-cloud. In-cloud, both canonical domains return NOT SCORABLE.
- Regression signal must therefore be argued by construction + offline unit
  tests in-cloud, and the LIVE delta re-score queued [LOCAL] for Jonah.
- Reachable from Python: pypi/github/anthropic infra only. Claude-side
  WebFetch/WebSearch tools route separately and DO work for research.
- Open question for Jonah: is this the intended network policy for the loop
  env, or should the canonical domains be allowlisted so in-cloud re-scores
  work? If not allowlistable, the "re-score every shipping cycle" rule needs a
  cloud-adapted form (offline regression tests as the in-cloud proxy).

## Open questions

- Does the cloud environment have a usable `claude` CLI for nested shopper
  panels? Test cheaply in an early cycle; if yes, behavioral experiments
  partially unblock in-cloud (codex still local-only).
- Codex hosted-browser refusal: OpenAI-side reputation gate, non-deterministic.
  driftflight.com blocked 22:53/22:58/23:21 on 2026-07-22. UPDATE (07:50Z fire):
  drift-flight.org is NO LONGER refusal-free — codex env-blocked it on ALL 5
  trials of the ~06:44Z panel, citing it as a 2-day-old domain (registered
  2026-07-20) with no independent footprint. So BOTH canonical domains now trip
  the codex reputation gate; drift-flight.org can no longer be used as the
  "codex-refusal-free" control. Root cause + attribution control (feed codex
  pre-fetched content when its browser is gated, marked assisted) still needed —
  and is now the blocker on any cross-model panel-stability measurement.
  UPDATE (10:13Z battery run): on drift-flight.org codex was safety-blocked on
  trial 1 ("rejected by the browser's site-safety policy") but REACHED normally on
  trial 2 (found product + price) — so the reputation gate is NON-DETERMINISTIC
  per-trial, not a hard per-domain block.
  CHARACTERIZED (11:42Z local fire, `experiments/codex_reachability.py`, 5 codex
  invocations, all domains HTTP 200): codex refused **4/4 canonical trials** (both
  domains ×2), every refusal a REPUTATION gate keyed on domain age (.com 7d / .org
  3d) + absent footprint but ALWAYS surfaced with browser-{safety,security}
  vocabulary. **v0.6 caught 4/4** (`_is_env_blocked` True → routed to reachability,
  none mis-scored as FAIL) — first LIVE validation of the v0.6 broadening on FRESH
  transcripts. **Reputable control example.com was NOT blocked** (browser works,
  correctly reported "no storefront") → the canonical refusals are codex's own
  reputation gate, not a broken browser. NO pure semantic-reputation phrasing
  ("flagged as unsafe"/"unable to browse" WITHOUT browser-safety words) was captured
  → test #8 stays an open spec, and NO regex broadening is warranted (v0.6 is
  sufficient for every observed refusal; broadening blindly would risk excusing real
  site blocks). The gate is now CLOSED on BOTH canonical domains this fire (was
  per-trial-open at 10:13Z → time-varying, currently fully gated). Evidence:
  `runs/local/codex_reachability_20260723T114225Z/{summary.json,transcripts/}`.
  Still missing for the harder test-#8 case: a committed FULL transcript of a
  SEMANTIC reputation-gate refusal that lacks the browser-{security,safety}
  vocabulary — none observed yet across all live fires.
- Panel verdict variance: EMPIRICAL question — what trial count N drives
  `verdict_stability` above ~0.8 on the canonical pair — got its first LIVE
  datapoint (07:50Z fire, drift-flight.org). ANSWER (claude-only, codex fully
  env-blocked): stable from N=2, converging 0.80 → 0.92 by N=5 once the
  env-block leak (above) is removed. This validates the Cycle 3–5 reliability +
  quotability code on real panel data for the first time. STILL OPEN: the
  CROSS-MODEL agreement question is unmeasured — codex never reached the site, so
  this is single-model reproducibility only. It is now GATED on codex
  reachability (the control-storefront/pre-fetched-content fix) — RE-CONFIRMED
  blocked at 11:42Z: codex gated on BOTH canonical domains (4/4), so no cross-model
  panel can be run on either right now. The 11:42Z example.com control PROVES the
  fix's premise — codex's browser works on a reputable domain, so the variable is
  domain reputation, addressable by a reputable agent-native control storefront or
  marked-assisted pre-fetched content. Cost still holds:
  `SHOPPER_TIMEOUT_S=300`/trial; the nested first-N subsample design
  (`experiments/trial_count_N.py`) gets the whole N-curve from ONE 5-trial run
  (~5 codex + 5 claude), not 2+3+5 separate runs — reuse it for the next domain.
