# Backlog (prioritized; prune every cycle)

`[LOCAL]` = needs Jonah's machine (codex CLI / zero CLI / paid probes) —
design in-cloud, execute locally.

## P0

- **[OPERATOR DIRECTIVE — Jonah, 2026-07-23] The battery must be
  OFFERING-RELATIVE, not fixed.** Observed: the current battery judges every
  site against one static intent list — an image-generation API gets probed
  with "order a physical good" and its partial completion (40% on the .org
  run) pollutes the completion means and both spread signals. That measures
  the battery's mismatch, not the site's readiness. Jonah's requirement:
  "super flexible and generalized — not specific to this instance."
  Redesign (COVERAGE + METHOD; the aggregation-semantics part is peer-gated):
  1. **Relevance discovery**: classify what the storefront CLAIMS to sell
     from its own surfaces (llms.txt, manifest/catalog, OpenAPI, homepage)
     into capability archetypes (metered API call, subscription, digital
     good, physical fulfillment, service booking, data retrieval, ...).
     Machine evidence required (quoted fields/lines); vendor-neutral.
  2. **Intent instantiation**: keep a fixed archetype TEMPLATE bank for
     cross-site comparability, but generate each site's task prompts by
     parameterizing templates with the DISCOVERED offering ("buy an
     AI-generated image" for an image API; "order <their product>" for a
     shop) — no static per-product YAML.
  3. **NA semantics**: archetypes the site does not claim to serve are NA —
     excluded from completion means, cross_task_spread, and
     between_kind_spread. Never penalized, never counted as signal. (Same
     attribution-honesty invariant as everywhere else, applied to tasks.)
  4. **Out-of-scope handling (unscored diagnostic, optional)**: when an
     agent asks for something the site does not sell, does it fail legibly
     (clear machine-readable decline) or garden-path the agent? Evidence
     only — a real readiness signal, but do not score it without a
     separate proposal.
  5. **Comparability**: every battery readout must name WHICH archetypes
     were assessed, so numbers compare within-archetype across sites, never
     as raw means over different task sets.
  Acceptance: rerun the canonical batteries — driftflight.com shows
  physical_good = NA (not a completion number) with spreads over claimed
  archetypes only; a retail storefront shows the inverse. Card and terminal
  readouts show NA archetypes as "not offered".

  ACCEPTANCE GUARD (canonical NA half) NOW EXECUTABLE IN-CLOUD — Cycle 27 (TRUTH,
  direct-to-main): `tests/test_offering_canonical.py` (4 tests) replays both committed
  canonical fixtures through the REAL discovery path and pins the classification —
  exact claimed SET `{metered_api,subscription,digital_good}` on both + `physical_good`
  (and service_booking, data_retrieval) NA on BOTH, so the directive's
  `driftflight.com physical_good = NA` is a per-cycle tripwire, not a [LOCAL] run-log
  fact. Non-vacuous: metaphorical "ship" ×3 on both flight-themed homepages stays NA
  (precision guard on real evidence); negative control (bare-"ship" signal) flips both
  → caught. Score-neutral (rubric v0.7, replay guard 8/8 / +39.4). Suite 118→122. The
  RETAIL-INVERSE half still needs live data / a fixture (see the P2 item below).

  PROGRESS — BRICK 1 (relevance discovery) SHIPPED 2026-07-23T23:49Z (local fire,
  COVERAGE/METHOD, direct-to-main, score-neutral). `asrs/offering.py`:
  `discover_offering(ctx)` reads a storefront's own surfaces (homepage + llms.txt /
  llms-full.txt / manifest.json, $0 GETs) and `classify_offering(domain, surfaces)`
  (pure) emits `OfferingProfile` — which capability ARCHETYPES the site CLAIMS to
  serve, from the fixed template bank `metered_api / subscription / digital_good /
  physical_good / service_booking / data_retrieval`, each with QUOTED machine
  evidence + source surface; `.unclaimed` = the NA complement. Precision-first,
  vendor-neutral; the metaphorical-"ship" physical_good false-positive is guarded
  (requires unambiguous fulfillment nouns). LIVE-VALIDATED on 4 real domains
  (invariant #3): drift-flight.org {metered_api,subscription,digital_good} +
  driftflight.com {metered_api,digital_good,subscription} both physical_good=NA
  (acceptance met); example.com {} (null); books.toscrape.com {physical_good}
  (inverse). `test_offering.py` 7/7; suite 96→103. Evidence:
  runs/local/offering_discovery_20260723T234942Z.json. See LOG (Local cycle 23:49Z).
  PROGRESS — BRICK 2 (intent instantiation) SHIPPED 2026-07-24T00:49Z (local fire,
  COVERAGE, direct-to-main, score-neutral). `asrs/battery.py`
  `instantiate_battery(profile)` + a fixed per-archetype intent TEMPLATE bank
  (`_ARCHETYPE_INTENTS`) turn brick-1 discovery into the battery's TASK SET: one
  `BatteryTask` per CLAIMED archetype (id=kind=archetype, fixed template-bank order
  for cross-site comparability), omitting unclaimed archetypes. Vocabulary
  RECONCILED: canonical task vocab is now `offering.ARCHETYPES`; generated tasks use
  archetype names, hand-authored YAMLs keep their free-form `kind` labels and still
  load. Parameterized: digital_good `{descriptor}` slot filled from the archetype's
  own vendor-neutral media signals ("obtain one generated image …" — operator's
  example; translation → "translated document"; else "digital output"),
  injection-safe. LIVE-validated on 4 real domains (invariant #3): both driftflight
  domains → NO physical_good task (operator acceptance met), books.toscrape.com →
  physical_good task (inverse), example.com → empty battery; all 4 acceptance
  assertions pass. Score-neutral (task selection only; `aggregate_battery`/scoring.py/
  rubric/probes untouched → rubric v0.7, canonical delta unchanged, replay guard
  46.1 F / 85.5 B / +39.4). `test_battery_instantiate.py` 8/8; suite 104 → 112.
  Evidence: runs/local/offering_battery_instantiate_20260724T004927Z.json. See LOG
  (Local cycle 00:49Z).
  BRICK 3 — NA-aware aggregation: **MERGED 2026-07-24T02:12Z (Cycle 26 first-duty peer-gate review,
  merge commit bec1dc0 — SURVIVED fresh-context adversarial review; PR #4, authored Cycle 25).**
  (A concurrent local fire pushed a `reconcile PR #4 external merge` note reading bec1dc0 as an
  external operator merge; that is superseded — the merge WAS Cycle 26's mandated fresh-context
  review, not an external merge, so no separate post-merge sanity check is pending.)
  `aggregate_battery(..., *, profile=OfferingProfile|None)`
  marks archetypes a site does NOT claim (`profile.unclaimed`) NA and EXCLUDES them from
  `mean_completion`/`cross_task_spread`/`between_kind_spread`; NA is DISTINCT from no-signal
  (structural not-offered vs offered-but-unobserved) and recorded (`na_archetypes` /
  `assessed_archetypes`) so the readout names both. `BatteryTaskResult.na`;
  `battery_semantics_version="b1"` (battery-diagnostic version, DELIBERATELY not the rubric
  version — flagged in PR); `report._battery_lines` names assessed + not-offered (offering-
  relative mode only). WITHOUT a profile = byte-for-byte pre-brick-3 (backward-compat pinned).
  Vendor-neutral (NA keys on archetype-claim structure; non-canonical kinds never NA).
  scoring.py/rubric/probes/fetch/offering.py untouched → rubric v0.7, canonical delta unchanged
  (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss). `test_battery.py` 9→12; suite 112→115.
  PR: https://github.com/jnakagawa/agentic-readiness/pull/4 — MERGED Cycle 26. See LOG Cycle 25/26.
  BRICK 5 — comparability readout: **DONE across two surfaces.** Terminal (`report._battery_lines`
  names "assessed over" / "not offered (NA, excluded)") shipped with brick 3 (Cycle 25). HTML
  (`scorecard._battery` "Offering-relative" sub-block — Assessed-over chips + dimmed Not-offered
  `.chip.na` chips + interpretation, driven off `na_archetypes`/`assessed_archetypes`, renders only
  in offering-relative mode) shipped **Cycle 28 (READOUT, direct-to-main, display-only, score-neutral;
  `test_readout.py` 17→19, suite 122→124, replay guard 8/8 / +39.4)**. The directive's requirement 5
  ("every battery readout must name WHICH archetypes were assessed") now holds on terminal AND card.
  REMAINING brick (next increment):
  - **BRICK 4 — out-of-scope legibility** (unscored diagnostic, optional): when an agent asks for
    something the site does not sell, does it fail legibly (machine-readable decline) or garden-path
    the agent? Evidence-only per the directive; design a separate proposal before scoring anything.
  - **`--battery auto` run-path wiring: SHIPPED 2026-07-24T02:12Z (Cycle 26, COVERAGE,
    direct to main).** `asrs/cli.py` `_resolve_battery(args, ctx)` (replacing
    `_load_battery_arg`) returns `(Battery|None, OfferingProfile|None)`: `--battery auto`
    runs `discover_offering → instantiate_battery` and threads the profile into
    `aggregate_battery(..., profile=)` (NA-aware, brick 3); `--battery <path>` stays
    `(battery, None)` (aggregation byte-for-byte pre-brick-3); empty offering → empty
    battery + profile (honest "nothing to assess"). `--battery` help now `PATH|auto`.
    Score-neutral (task selection + CLI wiring; scoring/rubric/probes untouched → rubric
    v0.7, replay guard 46.1 F / 85.5 B / +39.4). `test_battery_wiring.py` 4→7; suite
    115→118. The BEHAVIORAL EXECUTION of `--battery auto` is [LOCAL] (needs claude/codex
    + network) — the acceptance rerun below.
  - **[LOCAL] acceptance rerun** (now unblocked — bricks 1–3 merged + `auto` wiring shipped):
    run `asrs score <domain> --behavioral --battery auto --models claude,codex --trials 2`
    LIVE on the canonical pair + a retail control, and confirm the operator acceptance
    criteria on REAL data — driftflight physical_good = NA with spreads over claimed
    archetypes only, a retail storefront the inverse, and NA shown as "not offered" on the
    card + terminal. Force-add the reports to `runs/local/` (`runs/` is gitignored). This
    is the first end-to-end offering-relative live battery; it also finally eyeballs the
    per-intent grid / by-archetype + between-archetype pills on real multi-kind data
    (folds in the two "[LOCAL] Eyeball the battery card" P2 items).

<!-- DONE 2026-07-23 (two complementary fires): "[LOCAL] POST-merge live canonical re-score
     for v0.7 (PR #3, MERGED 72a2e5b)" FULLY DISCHARGED.
     (a) SANITY-CHECK HALF — 2026-07-23T15:18Z (Cycle 15, first duty): fresh-context
     adversarial post-merge sanity check of v0.7 SURVIVED → RETAIN — vendor-neutral, monotone
     non-increasing, $0-only intact, test_protocols.py 7/7, canonical delta unchanged by
     committed evidence (.org x402_probe FAIL 0.0 → _commerce_protocol_evidence already None
     under v0.6 so v0.7 still None; .com x402-live before the commerce branch). See LOG Cycle 15.
     (b) LIVE RE-SCORE HALF — 2026-07-23T15:43Z (local fire): re-scored both canonical domains
     LIVE on v0.7 (now on main). Suite 79/79 green pre-flight. drift-flight.org 46.1 F
     (x402_probe → no-agent-native-payment, NO commerce-protocol-*), driftflight.com 85.5 B
     (x402-live, NO commerce-protocol-*), delta +39.4 UNCHANGED; reports embed rubric "0.7".
     Third-domain spot-check example.com 22.5 F, v0.7, NO commerce-protocol-*/x402-live — probe
     path clean, no spurious credit. Monotone non-increasing by construction so only
     bare-200-false-positive domains lose credit; valid-manifest domains keep it
     (test_protocols.py). Evidence: runs/local/merge_verify_pr3_v07_driftflight{org,com}_
     20260723T154332Z.json. See LOG (Local cycle — 15:43Z). Also reconciled the stale
     bookkeeping (STATE listed PR #3 "Open"). The durable follow-up is the Cycle-15
     fixture-capture item below (`save_fixture`), which converts this into a permanent
     in-cloud offline guard instead of a per-fire manual re-score. -->


<!-- DONE 2026-07-23T16:46Z (local fire, TRUTH): "[LOCAL] Capture the canonical-pair replay
     fixtures" EXECUTED. Landed a dormant `--record-fixture <path>` hook on `asrs.cli score`
     (asrs/cli.py; also discharges the P1 CLI-hook item below), then did ONE live static crawl
     of each canonical domain and dumped its fetch cache. Committed:
     fixtures/canonical/drift-flight.org.json (37 entries), driftflight.com.json (48 entries) —
     recorded HTTP responses only (the Bearer/Authorization strings are the storefronts' OWN
     public API-doc examples + the x402 402 www-authenticate challenge = scoring evidence, not
     secrets). Live crawl 46.1 F / 85.5 B on v0.7. OFFLINE replay validation (FetchContext.
     from_fixture → _run_probes → scoring.score, no network) reproduces 46.1 F / 85.5 B / +39.4
     EXACTLY with 0 replay-miss on both (fixtures complete). Suite 85/85 green; dormant path
     confirmed (no flag → no fixture; hook runs after scoring.score so it can't move a score).
     See LOG (Local cycle — 16:46Z). The cloud test-wiring follow-up is now the top P0 below. -->

<!-- DONE 2026-07-23T17:15Z (Cycle 17, METHOD): "Wire tests/test_canonical_replay.py" SHIPPED —
     the network-blocked per-cycle canonical re-score is now EXECUTABLE in-cloud. 3 tests replay
     each committed fixtures/canonical/{drift-flight.org,driftflight.com}.json through
     from_fixture → asrs.cli._run_probes → scoring.score(load_rubric(None)) and assert
     overall_score 46.1(.org)/85.5(.com), grade F/B, rubric_version "0.7", scored True, all five
     pillar_scores (finer than the roll-up), delta +39.4, AND no cache entry carries a replay-miss
     (fixture still covers every probe request — a miss = a probe changed WHAT it fetches, fails
     loudly). Docstring pins the maintenance contract: a legitimate version-bump score move =
     re-capture [LOCAL] + update EXPECTED in the same PR. Tests-only, scoring path byte-for-byte
     untouched, rubric stays v0.7, canonical delta unchanged; direct-to-main. Suite 85 → 88.
     See LOG Cycle 17. This is the permanent cloud-adapted form of "re-score every shipping
     cycle" — the in-cloud regression signal no longer depends on the launchd runner. -->

- **[LOCAL] Re-capture canonical fixtures on any version-bump score move** (METHOD, standing
  maintenance for the Cycle-17 replay guard). `tests/test_canonical_replay.py` pins 46.1/85.5/
  +39.4 on v0.7. When a peer-gated scoring change LEGITIMATELY moves a canonical score, the
  guard will (correctly) go red until the fixtures are re-captured and EXPECTED updated in the
  SAME PR: `asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json` (LIVE,
  needs network → [LOCAL]), then update the numbers. This is not pending work — it is the
  documented upkeep step so a future cycle knows the red is intended, not a regression.

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
  `per_kind` rollup AND the Cycle-18 `between_kind_spread` (storefront-type
  specialization signal) on live multi-kind data for the first time — a multi-kind
  live report is the ONLY way either construct earns a real number. Budget: ONE
  domain per fire, trimmed battery preferred. Reuse the first-run pattern (`--battery <yaml>
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

<!-- DONE 2026-07-23T16:46Z (local fire, TRUTH): "`--record-fixture` CLI hook" LANDED as part
     of the canonical-fixture capture (P0 above). `asrs/cli.py`: `--record-fixture <path>` on
     the `score` subparser + a post-scoring `ctx.save_fixture(path)` in `_evaluate` guarded by
     `getattr(args, "record_fixture", None)`. Additive/dormant (no scoring semantics, rubric
     untouched), verified the no-flag path writes nothing and the hook runs after scoring.score
     so it can't move a score; suite 85/85. Direct-to-main. See LOG (Local cycle — 16:46Z). -->

- **Calibration population** (TRUTH): weekly static sweep of 15–20 real
  domains (exa.ai, deepai.org, perplexity.ai, a Shopify store, a mainstream
  retailer, agentic-native services) committed as a dated dataset +
  leaderboard page. A benchmark needs a population, not one pair.
- **Live handshakes for other rails** (COVERAGE): ACP/UCP checkout-session
  and MPP-only elicitation parity with the x402 probe. VALIDATION HALF addressed
  by PR #3 (Cycle 14, pending merge): a well-known ACP/UCP manifest must now PARSE
  (`_parse_commerce_manifest`) to earn the partial, and a validated hit is labeled
  `commerce-protocol-live` — parity in KIND with `x402-live`, killing the bare-200
  false positive. REMAINING (score-INCREASING → needs live verification on 2+ real
  domains, so distinct [LOCAL]-verified follow-up, NOT foldable into the non-inflating
  cloud half): (a) a LIVE ACP `checkout_sessions` POST elicitation (empty-item/`$0`
  handshake, analogous to the x402 empty-POST probe — must respect invariant #1: never
  POST a nonzero-value item), (b) MPP-only elicitation parity, (c) broaden well-known
  path coverage to catch MORE real commerce surfaces that currently score 0. Each of
  these can raise a domain's score, so gate on live evidence before shipping.
- **Adversarial referee pass** (METHOD, recurring): a self-audit — "would a
  critic call this check vendor-rigged?" — rewording and evidence-strengthening
  without losing capability substance. PROGRESS 2026-07-23T21:13Z (Cycle 21):
  shipped the FIRST EXECUTABLE instance — domain-relabeling invariance
  (`tests/test_canonical_replay.py`, +3 tests). Relabeling a canonical fixture's
  host everywhere and re-scoring yields the IDENTICAL score/pillars/statuses,
  proving the +39.4 delta is a property of the capability EVIDENCE, not the
  storefront's identity ("no special-casing any domain, favorable or hostile" is
  now a tripwire, non-vacuous per a negative control). REMAINING (still recurring):
  a prose re-read of each check's WORDING for vendor-leaning phrasing (the
  invariance guard proves the SCORING is neutral, not that the DESCRIPTIONS read
  neutrally to a skeptic); and extend the invariance guard to more fixtures as
  they land (see the third-control-domain P2 item).
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

- **[LOCAL] Retail-INVERSE offering fixture** (TRUTH, Cycle-27 follow-up — the operator's
  "a shop shows the inverse" half). Cycle 27 pinned the canonical NA half in-cloud
  (`tests/test_offering_canonical.py`). The mirror is unpinned: capture a fixture for a
  retail storefront (e.g. `books.toscrape.com`, already [LOCAL]-validated → physical_good
  CLAIMED) via `asrs.cli score books.toscrape.com --record-fixture fixtures/canonical/
  books.toscrape.com.json` (LIVE, needs network → [LOCAL]), then add a cloud-doable case to
  `test_offering_canonical.py` asserting the INVERSE — physical_good CLAIMED and the
  API/subscription archetypes NA — so the vendor-neutral "storefront TYPE drives the
  claimed set, not the domain" property is a tripwire in BOTH directions. Capture is
  [LOCAL]; the test wiring is cloud-doable once the fixture lands.
- **[LOCAL] Third-control-domain replay fixture** (METHOD/TRUTH, Cycle-17 + Cycle-19 follow-up):
  the canonical replay guard pins only the storefront PAIR. Capture a fixture for a NON-storefront
  control (example.com, already spot-checked 22.5 F [LOCAL] 15:43Z) via
  `asrs.cli score example.com --record-fixture fixtures/canonical/example.com.json`, then add a
  small `test_canonical_replay` case pinning 22.5 F / no commerce credit. NOW ALSO extend the
  Cycle-19 CAPABILITY-assertion pattern to it: pin that this low-capability baseline earns NO
  agent-native payment (`x402_probe` not-PASS, `self_serve_payg` x402_live=False, NO
  `commerce-protocol-*`/`x402-live`) — guards against a probe that spuriously INFLATES a bare
  site with payment credit it hasn't earned, the mirror of the +39.4 pair's capability guard.
  Capture is [LOCAL] (live crawl); the test wiring is cloud-doable once the fixture lands.
  ALSO (Cycle-21 follow-up): add a domain-relabeling invariance case for it too
  (`_assert_relabel_invariant("example.com")`), so the vendor-neutrality tripwire covers a
  non-storefront control, not just the canonical pair.

<!-- DONE 2026-07-23T20:12Z (Cycle 20, READOUT): "HTML battery card: between-archetype spread pill"
     SHIPPED. `asrs/scorecard.py`: `_battery_between_band` (Generalist <0.15 / Somewhat type-dependent
     <0.35 / Type-specialized ≥0.35, css good/warn/bad — thresholds/wording copied from the terminal
     report._battery_lines between-archetype line) drives a second header pill next to the cross-task
     pill + a one-line interpretation under the by-archetype sub-block. Both render ONLY when
     between_kind_spread is non-None (≥2 signal archetypes) → honest-None single-type case shows no
     pill, mirroring the aggregation and the terminal readout. Closes the last terminal→JSON→HTML gap
     for the battery diagnostics (same deferral per_kind took, Cycle 10→12). Display-only:
     scoring.py/rubric/probes/battery.py byte-for-byte untouched → rubric stays v0.7, canonical delta
     unchanged by construction AND re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss);
     direct-to-main. test_readout.py 15 → 16 (+between-kind pill test; single-kind test extended to
     assert no pill on honest-None); suite 90 → 91. See LOG Cycle 20. The live-data eyeball folds into
     the [LOCAL] second cross_task_spread datapoint (P0) — the first live report to carry the field. -->

- **Battery card between-pill: live-data eyeball** (READOUT, Cycle-20 follow-up): the between-archetype
  pill now renders but has only ever seen synthetic fixtures. When the [LOCAL] second cross_task_spread
  datapoint runs (P0), pass its report through `scorecard.build_scorecard` and confirm the between-pill
  + interpretation line read correctly on real multi-kind data. No new code — a render + visual check
  (fold into the existing "[LOCAL] Eyeball the battery card" item above).
<!-- DONE 2026-07-24T00:17Z (Cycle 24, READOUT): "Surface the earned-dominance / observability
     property in the readout" SHIPPED. methodology.html section 3 (FAIL vs CANT_TEST) gains a
     "worked example — when is a low score earned evidence, not a blind spot?" sub-section naming
     the three facts that make a two-site delta trustworthy, in the SAME capability language as
     Cycle-23's test_canonical_delta_is_earned_dominance: full observability (each 0 is a
     tested-and-absent FAIL, not an un-observed check) / like-for-like denominator / check-by-check
     dominance-no-inversion (capability SUPERSET) — and states the property is pinned by an
     executable regression test (enforced, not asserted). Vendor-neutral: reference pair described
     by capability, no domain/product/brand named (test-pinned drift-flight/driftflight absent).
     asrs/scorecard.py (prose + minimal h3/ul/li styling in shared _PROSE_HEAD) + tests/test_readout.py
     only; scoring.py/rubric/probes/fetch/protocols/battery byte-for-byte untouched → display-only,
     rubric stays v0.7, canonical delta unchanged (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss).
     Direct-to-main. test_readout.py 16 → 17; suite 103 → 104. See LOG Cycle 24. -->

- **Worked-observability example: card annotation cross-link** (READOUT, Cycle-24 follow-up,
  OPTIONAL): the methodology page now carries the earned-dominance worked example (section 3). A
  small next unit would anchor-link a compared-pair card's overview (or the delta shown on a
  `compare` card) to that methodology sub-section, so a reader looking at a large delta can jump
  straight to "why this delta is earned, not a blind spot". No scoring semantics; direct-to-main.
  Low priority — the prose exists; this is a navigation nicety, adjacent to the cap-chip anchor-link
  item below.
- **Evidence links on the card** (READOUT): each check row links to its
  evidence blob; publish evidence alongside the hosted card.
- **Score-over-time trend page** (READOUT): per-domain history from the
  dated reports; error bars once trials ≥ 2 lands.
- **Free-tier probe generalization** (COVERAGE): more opt-in conventions
  (query param, path-based), non-EVM zero-value schemes. PROGRESS 2026-07-23T22:12Z
  (Cycle 22): the **query-param** opt-in DISCOVERY half SHIPPED in-cloud (direct-to-main,
  score-neutral). `asrs/behavioral/free_tier.py` now scans doc prose for a documented
  `?tier=free`/`?mode=free`/`?free=true` opt-in (`_scan_query_param_instruction`) and records
  it as `FreeTierDiscovery.opt_in_query` + an `opt_in_query` evidence key — but does NOT yet
  gate `advertised` or drive the live free-mode call (deliberately score-neutral, test-pinned).
  REMAINING: (a) **[LOCAL], score-increasing → invariant #3 live-verify on ≥2 real domains**
  — wire `opt_in_query` into the `advertised` gate AND the live call path (append the param to
  the request URL instead of / alongside the header; keep the $0-only settle safety byte-for-byte
  intact), then confirm on ≥2 real storefronts that document a query-param free tier that the
  probe opts in and exercises the $0 allowance correctly; likely peer-gated when the scoring path
  changes. (b) **path-based** opt-in convention (e.g. a documented `/free/…` or `/v1/free/…`
  endpoint) — the next in-cloud COVERAGE increment, same discovery-only/score-neutral shape as the
  query-param half, follow-up live-wiring [LOCAL]. (c) **non-EVM zero-value schemes** (still open).
<!-- DONE 2026-07-23T16:11Z (Cycle 16, READOUT): "Methodology prose page" SHIPPED as
     methodology.html. `scorecard._write_methodology_page(out_dir)` renders the "read the
     paper" doc behind the rubric page — ten sections: capability lens; five pillars +
     weights; aggregation + renormalization; FAIL vs CANT_TEST; NOT SCORABLE vs an F;
     attribution honesty (agent-side vs site-side); shopper+trust panels + refusal semantics;
     reproducibility (trials/verdict-stability/quotability); grade bands + caps; the $0
     free-tier probe; versioned comparability + evidence. Published next to every card by
     build_scorecard alongside rubric.html; cross-linked both ways. Weights/caps/grade-bands
     pulled LIVE from load_rubric() (nothing hardcoded → can't drift on a version bump).
     Display-only: scoring.py/rubric/probes byte-for-byte untouched, rubric stays v0.7,
     canonical delta unchanged by construction; direct-to-main. tests/test_readout.py 12 → 15;
     suite 82 → 85. See LOG Cycle 16. FOLLOW-UP candidate below (evidence-links + a top-of-page
     prose intro remain separate READOUT items). -->

- **Methodology page follow-ups** (READOUT, Cycle-16 follow-up): the methodology page exists
  and documents the semantics, but (a) it renders straight to `methodology.html` with no
  hosted deploy step of its own — fine while it ships next to the card; and (b) each scorecard
  check ROW still doesn't link to its evidence blob (the separate P2 "Evidence links on the
  card" item) nor to the relevant methodology section. Small next unit: anchor-link the four
  cap chips on a card's "grade capped" alert to the corresponding methodology cap row, so a
  reader who sees a cap can jump straight to why it caps. No scoring semantics; direct-to-main.

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
