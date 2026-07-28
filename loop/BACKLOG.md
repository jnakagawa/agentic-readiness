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
  SURFACE COVERAGE COMPLETED — Cycle 34 (COVERAGE, direct-to-main, score-neutral): the
  directive's FOURTH named surface, the OpenAPI / Swagger spec, is now read.
  `asrs/offering._SURFACE_DOCS` gains `/openapi.json`, `/.well-known/openapi.json`,
  `/swagger.json` — so an API-FIRST storefront that exposes only its machine contract (no
  homepage/llms.txt) is classified from the spec, not mis-read as offering nothing. No new
  signal needed (the spec's servers/paths/summaries carry the vendor-neutral qualified-API /
  pay-per / generated-media / x402 language the bank already anchors). Score-neutral
  (`discover_offering` is off the scoring path — grep-verified; commerce-manifest scoring probe
  keeps its own untouched `protocols._AGENT_SURFACE_DOCS`); rubric v0.7, replay guard 8/8 /
  +39.4, canonical OFFERING guard 8/8 unchanged (surfaces absent from committed fixtures).
  `test_offering.py` 7→9; suite 145→147. All FOUR directive surfaces (homepage / natural-language
  docs / OpenAPI / — the manifest) now read. See LOG Cycle 34.
  SIXTH SURFACE — Cycle 46 (COVERAGE, direct-to-main, score-neutral): the A2A / Agent2Agent
  AGENT CARD `/.well-known/agent.json` + `/.well-known/agent-card.json` is now read.
  `asrs/offering._SURFACE_DOCS` gains both — the open, vendor-neutral manifest an agent-native
  storefront publishes at a well-known URI so ANOTHER agent discovers what it does (top-level
  `description` + `skills[]` each with name/desc, in the SAME natural-language capability prose the
  bank already anchors); a card-ONLY storefront (no homepage/llms.txt/spec/descriptor) is no longer
  mis-read as offering nothing (the Cycle-34/42 failure mode, for the agent-card surface). No new
  signal. Score-neutral (off the scoring path — grep-verified; scoring probe's separate
  `protocols._AGENT_SURFACE_DOCS` untouched); rubric v0.7, replay guard 14/14 / +39.4, canonical
  OFFERING guard 12/12 unchanged (surfaces absent from committed fixtures). Vendor-neutral (A2A =
  open Linux-Foundation protocol, not a vendor). `test_offering.py` 11→12; suite 192→193. See LOG
  Cycle 46. The agentic-commerce landscape's published self-description surfaces (homepage / llms.txt /
  manifest / OpenAPI / ai-plugin / A2A agent card) are now ALL read; remaining COVERAGE frontier is
  score-increasing ([LOCAL] free-tier live-wiring, ACP/UCP/MPP handshakes) or a new archetype/signal.
  FIFTH SURFACE (beyond the directive's named four) — Cycle 42 (COVERAGE, direct-to-main,
  score-neutral): the agent-plugin descriptor `/.well-known/ai-plugin.json` is now read.
  `asrs/offering._SURFACE_DOCS` gains it — the open, vendor-neutral manifest a storefront publishes
  so an AI agent knows what it is / how to use it; its `description_for_model`/`description_for_human`
  carry the SAME natural-language capability prose the bank already anchors on, so a descriptor-only
  site (no homepage/llms.txt/reachable spec) is no longer mis-read as offering nothing (the exact
  Cycle-34 failure mode, for the descriptor surface). No new signal. Score-neutral (off the scoring
  path — grep-verified; commerce-manifest scoring probe's `protocols._AGENT_SURFACE_DOCS` untouched);
  rubric v0.7, replay guard 14/14 / +39.4, canonical OFFERING guard 11/11 unchanged (surface absent
  from committed fixtures). `test_offering.py` 9→10; suite 176→177. See LOG Cycle 42.
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
  now a tripwire, non-vacuous per a negative control). PROGRESS 2026-07-24T05:12Z
  (Cycle 29): the vendor-neutral WORDING half of the referee pass is now EXECUTABLE
  for the PARSED RUBRIC — `tests/test_rubric_wording.py` (4 tests) scans every scored
  check's id+desc for a denylist of scored storefront/product names and asserts none
  appear; it caught + drove the fix of the one live violation ("The Exa lesson —" in
  `bhv_no_human_gate.desc`, reworded to capability language), and is non-vacuous
  (negative control), anti-vacuous (full parsed set), and false-positive-guarded
  (instrument/crawler names not flagged). REMAINING half (a) — the HAND-AUTHORED-readout
  prose re-read — is now EXECUTABLE (Cycle 33, see below), not a manual pass. STILL recurring:
  (b) extend BOTH the relabel-invariance guard AND BOTH wording denylists (parsed-check +
  the new readout scanner) to more fixtures/storefronts as they land (see the third-control-domain
  P2 item; add any newly-scored storefront's name to `_SCORED_STOREFRONT_NAMES` — the ONE denylist
  now backs both wording surfaces). PROGRESS 2026-07-24T09:12Z (Cycle 33, METHOD): the
  HAND-AUTHORED-readout half of (a) shipped as `tests/test_readout_wording.py` (4 tests) —
  renders the public readout for a NEUTRAL domain (`example.test`) via `build_scorecard` and scans
  the rendered `methodology.html` + card `card.html` with the SAME denylist + matcher (factored
  into a shared `_scan_text_for_scored_storefront` in `test_rubric_wording.py`, behavior-preserving).
  Domain-as-data handled by the neutral domain; rubric.html deliberately excluded (verbatim-YAML
  changelog names = the Cycle-29 engineering-history category) AND reused as a LIVE non-vacuous
  control (scanner asserted to FIRE on it: `['driftflight','drift-flight']`). Score-neutral
  (git diff -- asrs/ rubric/ EMPTY; rubric v0.7, replay guard 8/8 / +39.4); suite 141→145. PROGRESS
  2026-07-24T07:20Z (Cycle 31, TRUTH): relabel-invariance now covers a SECOND
  LAYER — the OFFERING classifier / task-selection path, not just scoring.
  `tests/test_offering_canonical.py` +3 (4→7): relabel each committed canonical
  fixture's host to `vendor-neutral.test` and assert the CLAIMED archetype list
  (ordered) + NA set are identical through the REAL `from_fixture ->
  discover_offering` path — the claimed/NA partition (which archetypes get tasks
  vs are excused NA) keys on EVIDENCE, not identity. Non-vacuous (host appears in
  the classifier's own matched evidence) + a negative control (an identity-keyed
  favorable special-case is CAUGHT). Score-neutral, rubric v0.7, replay guard 8/8
  / +39.4. PROGRESS 2026-07-24T11:12Z (Cycle 35, TRUTH): the SCORING-layer relabel guard now
  covers a THIRD real domain — the retail storefront `books.toscrape.com`
  (`test_relabel_invariance_retail`, 29.5 F identity-invariant). PROGRESS 2026-07-27T~19:30Z
  (Cycle 41, METHOD): leg (b) DISCHARGED for the cloud-doable domains — the OFFERING-layer relabel
  guard now spans ALL FOUR real domains, matching the scoring-layer guard.
  `tests/test_offering_canonical.py` +2 (9→11): `test_offering_relabel_invariance_retail`
  (books.toscrape.com → {physical_good}, all else NA, invariant) +
  `test_offering_relabel_invariance_nonstorefront` (example.com → honest-empty offering, all NA,
  invariant) via a shared `_assert_offering_relabel_general`. Honest non-vacuity anchored on
  fixture-SURFACE presence (the pair's host-in-evidence-QUOTE mechanism doesn't hold for host-free
  retail prose or the empty non-storefront); the empty case pins the full-NA partition invariant.
  Tests-only, score-neutral (rubric v0.7, replay guard 14/14 / +39.4); suite 174→176. Still
  recurring: (a) the hand-authored-prose re-read (EXECUTABLE since Cycle 33 — run it when new
  readout prose lands); extend BOTH the relabel guards AND the wording denylist to any NEWLY-scored
  storefront/fixture as they land.
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
<!-- DONE 2026-07-24T08:52Z (local fire, METHOD): "Nested shopper spawns the full user MCP
     fleet" FIXED. Both `asrs/behavioral/shopper._claude_cmd` AND `trust_probe._claude_cmd`
     now pass `--strict-mcp-config`, so the nested `claude -p` panels no longer inherit the
     operator's GLOBAL `~/.claude.json` MCP fleet (`trigger/unityMCP/linear-server/hex/posthog/
     motherduck` — the exact set the 10:13Z battery saw booting ~1 min/panel). Strict + no
     `--mcp-config` == empty fleet; the shopper needs only WebFetch/WebSearch. Behavioral-
     execution plumbing only (a CLI flag) → scoring.py/rubric/probes untouched, rubric v0.7,
     canonical delta unchanged (replay guard 8/8, 46.1 F / 85.5 B / +39.4). Direct-to-main.
     `tests/test_shopper_hermetic.py` 4/4 (new, non-vacuous — pre-fix builders fail it); suite
     137 → 141. LIVE-verified: one real `shopper._run_one` on driftflight.com browsed fine
     (10 turns, 5/5 checkpoints) and its transcript shows `mcp_servers == []` — hermetic on the
     actual fixed path. This de-contaminates + speeds EVERY future behavioral run (the honest
     prerequisite for the top-P0 `--battery auto` acceptance rerun). Evidence:
     runs/local/hermetic_shopper_verify_20260724T084946Z/. See LOG (Local cycle — 08:52Z). -->
- **[LOCAL] Wall-clock A/B of the hermetic fix on the operator's real fleet** (METHOD, optional
  follow-up to the 08:52Z hermetic fix). This fire's live proof was the panel transcript's
  `mcp_servers == []`; a headless `-p` timing A/B could not reproduce the boot delta because that
  subprocess env surfaced `mcp_servers=[]` even pre-flag. When a full `--battery auto` acceptance
  rerun runs next, capture the per-panel wall time and confirm the ~1 min/panel MCP-boot savings
  the 10:13Z observation implied (folds into the acceptance-rerun P0; no new code — a timing note).

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

<!-- DONE 2026-07-24T07:47Z (local fire, TRUTH): "[LOCAL] Retail-INVERSE offering fixture"
     EXECUTED — the operator's "a shop shows the inverse" acceptance half is now an in-cloud
     tripwire. Captured fixtures/canonical/books.toscrape.com.json via a STATIC $0 crawl
     (asrs.cli score books.toscrape.com --record-fixture … — 41 GET entries, 0 POST, public
     book-catalog sandbox, no secrets), then wired test_retail_inverse_offering into
     tests/test_offering_canonical.py (7 → 8): replays the committed fixture through the REAL
     FetchContext.from_fixture → discover_offering path (no network) and asserts the MIRROR of
     the canonical NA guard — claimed == {physical_good} EXACTLY, and {metered_api, subscription,
     digital_good} (exactly what the canonical pair CLAIMS) all NA. Non-vacuous: physical_good
     rests on ANCHORED fulfillment evidence (labels add-to-cart + stock from "In stock"/"Add to
     basket"), pinned explicitly — the exact complement of the canonical pair's metaphorical-
     "ship" NA case. (No relabel case added: the host is absent from physical_good's prose
     evidence → relabel would be vacuous here; the canonical pair's relabel guard covers
     identity-independence where non-vacuous.) Score-neutral: git diff -- asrs/ rubric/ EMPTY →
     rubric v0.7, canonical delta unchanged (replay guard 8/8, 46.1 F / 85.5 B / +39.4). Direct
     to main. Suite 132 → 133. See LOG (Local cycle — 07:47Z). The example.com non-storefront
     control replay/relabel case (P2 below) remains the last offering-layer fixture gap. -->

<!-- DONE 2026-07-27T18:11Z (local fire — RECONCILIATION ship): "[LOCAL] Third-control-domain
     replay fixture" LANDED. The fixture capture + all four test cases were authored + validated by
     the 2026-07-24T11:48Z local fire (see LOG that date), but that fire's CODE commit was lost — only
     its LOG.md entry was swept up by the 12:41Z verify runner (2cf0cef), leaving the tests + fixture
     uncommitted in the working tree while the committed LOG claimed the ship. This fire re-validated
     the surviving WIP against the CURRENT suite and committed it, reconciling git history with the
     already-committed 07-24 LOG entry. Landed: `fixtures/canonical/example.com.json` (41 GET / 0 POST,
     the plain IANA example page, no auth/secret tokens) + `test_canonical_replay.py` 11→14
     (`test_nonstorefront_replays_22_5` pins 22.5 F / access 100 / legibility 0 / transactability 0 /
     trust 20 / outcome None, 0 replay-miss; `test_nonstorefront_earns_no_agent_native_payment` — the
     capability-floor MIRROR: no storefront earns EXACTLY 0 transactability + no `commerce-protocol-*`/
     `x402-live`, with the honest CANT_TEST-self_serve_payg-yet-still-0 attribution nuance;
     `test_relabel_invariance_nonstorefront`) + `test_offering_canonical.py` 8→9
     (`test_nonstorefront_empty_offering` — sells nothing → `archetypes == []`, all six NA). The
     regression + vendor-neutrality signal now spans FOUR real domains across the commerce spectrum
     (46.1 / 85.5 API storefronts, 29.5 retail floor, 22.5 zero-commerce baseline). Score-neutral:
     `git diff -- asrs/ rubric/` EMPTY → rubric v0.7, canonical PAIR unchanged by construction AND
     re-measured (replay guard now 14/14, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Full suite 164→168.
     Direct-to-main. See LOG (Local cycle — 18:11Z). REMAINING follow-ups are distinct items below/at
     the referee-pass entry: the OpenAPI-spec-only fixture, and extending the OFFERING-layer relabel
     guard to the retail + non-storefront domains (only the SCORING-layer relabel covers all four). -->

<!-- OpenAPI HALF DONE 2026-07-27T20:54Z (local fire, TRUTH, direct-to-main, score-neutral): the
     machine-surface-only storefront fixture landed for the OPENAPI surface, and live calibration
     surfaced + fixed a precision bug. Captured `fixtures/canonical/api.replicate.com.json` — a REAL
     API-first storefront (metered model-inference API, homepage a bare `{}`, agent-facing
     self-description IS its /openapi.json; 8 GET / 0 POST, 92 KB public spec, no secrets). The live
     crawl caught a FALSE POSITIVE: `discover_offering` classified it `['metered_api','physical_good']`
     because the `sku-inventory` signal (bare `\bSKU\b|\binventory\b`) matched "The SKU for the hardware
     used to run the model" — a COMPUTE/GPU hardware SKU, not retail inventory. Fixed `asrs/offering.py`:
     re-anchored `sku-inventory` to the RETAIL sense only (product/item/per/each SKU; SKU number/code/
     count; inventory count/levels/on-hand/management; manage/track/check inventory; in-stock inventory).
     Nearly redundant for recall (books.toscrape.com's physical_good rests on add-to-cart+stock;
     sku-inventory fires on NONE of the four committed fixtures) → no real recall lost; api.replicate.com
     now `['metered_api']`, driven by /openapi.json. Tests: `test_offering_canonical.py` 11→12
     (`test_machine_surface_openapi_storefront` — /openapi.json READ + DROVE classification,
     machine-surface-first with a zero-signal homepage, physical_good=NA NON-VACUOUS on the trap phrase
     asserted present), `test_offering.py` 10→11 (synthetic compute-vs-retail SKU precision). Score-neutral
     (classify/discover off the scoring path; git diff -- scoring.py/rubric/probes/fetch/protocols/battery/
     behavioral EMPTY → rubric v0.7, no battery_semantics_version bump); canonical pair 46.1 F / 85.5 B /
     +39.4 unchanged (replay guard 14/14, verify_20260727T204103Z in-band); suite 177→179. See LOG
     (Local cycle — 20:54Z). REMAINING — the ai-plugin-DESCRIPTOR half — is the narrowed item below. -->
- **[LOCAL] ai-plugin-DESCRIPTOR-only storefront fixture** (TRUTH, Cycle-42 + 2026-07-27 follow-up):
  the OpenAPI machine surface now has a real-data guard (api.replicate.com, above), but Cycle 42's
  `/.well-known/ai-plugin.json` descriptor surface is still verified only against a SYNTHETIC surface
  (`test_offering.py::test_ai_plugin_descriptor_alone_classifies_storefront`). Capture a fixture for a
  real storefront whose agent-facing self-description is its ai-plugin descriptor (ideally a thin/absent
  homepage) — probe candidates with `FetchContext(dom).get("/.well-known/ai-plugin.json")` for a 200
  application/json with capability prose, then capture via a live `discover_offering` + `ctx.save_fixture(
  "fixtures/canonical/<domain>.json")` (LIVE, [LOCAL]). Add a `test_offering_canonical` case replaying it
  and asserting `"/.well-known/ai-plugin.json" in profile.surfaces_seen` drove the claimed archetypes.
  NOTE: post-ChatGPT-plugins many ai-plugin.json endpoints are dead — the 2026-07-27 probe sweep found
  openrouter.ai served an HTML SPA fallback (not real JSON) at that path; budget a short candidate search
  and, if none is cleanly reachable, log the miss rather than force a bad fixture.

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
  Low priority — the prose exists; this is a navigation nicety. The SIBLING cap-chip anchor-link
  (link a card's "Grade capped" chip to its methodology §8 cap row) is now DONE — Cycle 32
  (READOUT, direct-to-main): `scorecard._cap_anchor` (one source of truth for both surfaces) +
  `id="cap-<slug>"` on each methodology cap row + `<a class="chip" href="methodology.html#cap-<slug>">`
  on the card alert; `test_readout.py` 19→23 (incl. a cannot-drift test), suite 133→137, replay
  guard 8/8 / +39.4. This compare-card-delta half remains as the last cross-link nicety.
- **Evidence links on the card** (READOUT): each check row links to its
  evidence blob; publish evidence alongside the hosted card.
- **Score-over-time trend page** (READOUT): per-domain history from the
  dated reports; error bars once trials ≥ 2 lands. PROGRESS 2026-07-27T14:21Z
  (Cycle 36): the CANONICAL-PAIR half landed as a TERMINAL readout — `asrs
  canonical-history` (`asrs/canonical_history.py`) reads the committed
  `runs/local/verify_*.json` series into a delta trend + sustained-drift alert
  vs the fixture baseline (+39.4), with a sparkline. REMAINING: (a) an HTML
  trend surface — **DONE 2026-07-27T18:14Z (Cycle 40, READOUT)**: `canonical-history.html`
  (`scorecard._write_canonical_history_page`) renders the full diagnosis — delta trend SVG,
  band, sustained-drift run, PILLAR attribution + SIDE/direction cause — next to every card,
  footer cross-linked (see the DONE note above; `test_readout.py` 23→29, suite 164→170,
  replay guard 11/11 / +39.4). REMAINING: (b) per-DOMAIN
  history beyond the canonical pair (needs committed dated reports for other
  domains — currently only the verify series is committed); (c) error bars once
  multi-trial series land.
- **Noise-floor on `canonical-history.html`** (READOUT, Cycle-45 follow-up): the measured
  measurement-noise floor (`CanonicalHistory.noise_floor` — `n_in_band`, σ, worst |div|,
  deterministic / band_well_separated) now renders in the TERMINAL `asrs canonical-history`
  block but not on the HTML page. Surface it on `canonical-history.html`
  (`scorecard._write_canonical_history_page`) — the same terminal→HTML deferral the drift
  diagnostics took (pillar/side/re-capture, Cycles 37/39/43 → 40/44). Display-only,
  score-neutral, direct-to-main; a render + a `test_readout.py` case.
- **Validate the drifting/diverged cutoffs against observed transient magnitudes** (METHOD,
  Cycle-45 follow-up): Cycle 45 measured the AT-REST noise floor (σ=0 → the in-band `_BAND_IN=2.0`
  band is well-separated from measurement noise). The `_BAND_DRIFT=8.0` cutoff that splits
  "drifting" from "diverged" is still an ASSUMED constant. Measure the distribution of the
  observed OUT-OF-BAND transient magnitudes (the committed series carries the 07-27 `.com`
  outage: |div| 3.9→? / 30.1 / 32.6) and check the drifting/diverged split is calibrated to real
  transient sizes rather than picked. Read-only diagnostic on `canonical_history`, score-neutral,
  direct-to-main. Honest caveat: only ~4 transients observed so far — a small sample; the guard
  should be a coherence check (all observed transients land in a sane band), not an over-fit.
<!-- DONE 2026-07-27T15:14Z (Cycle 37, METHOD): "Canonical-history pillar attribution" SHIPPED,
     direct-to-main, score-neutral. `asrs/canonical_history.py`: `CanonicalPoint` now carries
     `no_rails_pillars`/`with_rails_pillars` (per-side per-pillar overalls, NUMERIC entries only —
     `None` pillars dropped, attribution honesty at the pillar layer); `PillarMove`/
     `PillarAttribution` (`anchor_ts`, `moves` largest-|change|-first, `.top`); `summarize` computes
     `attribution` via `_attribute` ONLY when latest is out of band AND an in-band anchor exists
     (`points[-(run+1)]`), else honest None; `render` names the top mover (+ up to 2 secondary).
     On the REAL committed series it reproduces the Cycle-36 hand-written note EXACTLY:
     `driftflight.com legibility fell 90.9 → 63.6 (-27.3) — the largest pillar move`. So the
     playbook's "explain the delta in capability terms" duty is now COMPUTED. Reads committed
     evidence only; imports no scoring code; vendor-neutral. scoring.py/rubric/probes/… untouched →
     rubric v0.7, canonical pair 46.1 F / 85.5 B / +39.4, replay guard 11/11. `test_canonical_history.py`
     6→10; suite 156→160. See LOG Cycle 37. -->
<!-- DONE 2026-07-27T18:14Z (Cycle 40, READOUT, direct-to-main, display-only/score-neutral):
     "Canonical-history attribution: HTML trend surface" SHIPPED. `scorecard._write_canonical_history_page`
     renders `canonical-history.html` next to every card (published by `build_scorecard` alongside rubric/
     methodology, footer cross-link) surfacing the FULL `asrs canonical-history` diagnosis off the committed
     verify series — latest reading, divergence + band verdict, sustained-drift run, PILLAR attribution
     (Cycle 37) AND SIDE/direction cause (Cycle 39) — plus a single-series delta-over-time SVG trend
     (`_history_trend_svg`: live delta per re-score vs a dashed pinned-fixture baseline, each point colored
     by its divergence BAND, latest direct-labeled, band legend). New public `canonical_history.band_for_delta`
     = one source of truth for the point-band thresholds (terminal + chart classify identically). dataviz
     skill loaded (ONE series → no identity legend; per-point band = reserved STATUS encoding shipped WITH a
     named legend, never color-alone); rendered + eyeballed via Chromium. Vendor-neutral: names the reference
     pair as DATA (page is ABOUT those two domains) — SAME engineering-history category as rubric.html,
     deliberately OUT OF SCOPE for the wording scanner (which guards capability-worded CHECK prose on
     methodology+card); `test_readout_wording` unchanged/green. Score-neutral: git diff = canonical_history.py
     + scorecard.py + test_readout.py ONLY; scoring/rubric/probes/… untouched → rubric v0.7, replay guard
     11/11, 46.1 F / 85.5 B / +39.4. `test_readout.py` 23→29; suite 164→170. See LOG Cycle 40. This discharges
     remaining item (a) of the "Score-over-time trend page" P2 below. -->
<!-- DONE 2026-07-27T22:2xZ (Cycle 44, READOUT, direct-to-main, display-only): "Surface the re-capture
     recommendation on the canonical-history HTML page" SHIPPED. `_write_canonical_history_page` gains a
     "Re-capture decision" card driven off `hist.recapture` (code label via `ch._REC_LABEL` + full reason),
     rendered whenever there is a reading (any code but the REC_NO_DATA sentinel); a new `_HISTORY_REC_COLOR`
     colours the label chip by code (green baseline-valid / amber wait+defer / red recapture-candidate /
     neutral review — reusing the band inks so the surface reads as one system), NEVER colour-alone (label +
     reason always render). The card states re-capture is a DECISION not an action ([LOCAL], comparability-
     affecting). Closes the last terminal→HTML gap for the Cycles-36→43 drift arc (same deferral the battery
     diagnostics took, 10→12 / 18→20 / 25→28). Display-only: git diff = scorecard.py + test_readout.py ONLY;
     scoring.py/rubric/probes/canonical_history byte-for-byte untouched → rubric v0.7, replay guard 14/14 /
     +39.4. LIVE 69-point series reads `baseline-valid` (green). `test_readout.py` 29→31 (+DEFER render on the
     drifting series; +NON-VACUOUS in-band data-driven control); suite 185→187. See LOG Cycle 44. -->
- **[LOCAL] Eyeball the canonical-history card on the operator's hosted deploy** (READOUT, Cycle-40 follow-up,
  optional): the HTML canonical-history page renders correctly in-cloud (Chromium screenshot, real committed
  series). A next visual check would confirm it reads well hosted next to a real published scorecard, and that
  the footer cross-link resolves. No new code — a render + visual check.
- **[LOCAL] Decide on canonical fixture re-capture once driftflight.com settles**
  (TRUTH, Cycle-36 follow-up to the LIVE CANONICAL DRIFT). The live `.com`
  score has drifted below the pinned fixture (85.5 B → ~78.7 C, legibility
  regressed) and is still fluctuating fire-to-fire. Do NOT re-capture while
  unstable. When the live series reads in-band-stable for several consecutive
  fires at a NEW level (watch `asrs canonical-history`), decide whether the site
  change is durable; if so, re-capture (`asrs.cli score driftflight.com
  --record-fixture fixtures/canonical/driftflight.com.json`, LIVE → [LOCAL]) and
  update EXPECTED in `test_canonical_replay.py` + `FIXTURE_BASELINE_DELTA` in
  `canonical_history.py` in the SAME commit (the documented drift-move contract).
  If the drift is transient and the site recovers to 85.5 B, no action. DECISION AID (Cycle 39):
  `asrs canonical-history` now COMPUTES `divergence_cause.reference_degraded` — True means the gap
  narrowed from the WITH-RAILS reference softening (a real-world regression), so the pinned fixture
  still represents the true capability gap and re-capture should WAIT; it is currently True (`.com`
  overall fell -6.8, `.org` flat). Only when the cause flips to the no-rails side GAINING capability
  (`reference_degraded=False`, a genuine gap-closing) — or `.com` settles durably at a new in-band
  level — is a re-capture warranted.
  DECISION NOW COMPUTED (Cycle 43, TRUTH): `asrs canonical-history` prints a `re-capture:` line —
  `canonical_history.recapture_advice(history) -> RecaptureAdvice(code, reason)` synthesizes band +
  sustained-run + `divergence_cause` into the single recommendation this item asks a human to make:
  `baseline-valid` (in-band, no action) / `wait-not-yet-sustained` / `defer-reference-degraded`
  (the reference softened — WAIT) / `recapture-candidate` (durable baseline move — DO the [LOCAL]
  re-capture above) / `review-no-anchor`. It NEVER re-captures (that stays [LOCAL]); it names the
  call. STATUS as of Cycle 41: the drift RECOVERED — `.com` back at 85.5 B, delta +39.4 in-band —
  so the recommendation now reads `baseline-valid`: **no re-capture, the pinned fixture is faithful.**
  This item stays [LOCAL]-parked as the standing playbook for the NEXT drift; the recommendation
  tells the operator which branch to take.
- **Free-tier probe generalization** (COVERAGE): more opt-in conventions
  (query param, path-based), non-EVM zero-value schemes. PROGRESS 2026-07-23T22:12Z
  (Cycle 22): the **query-param** opt-in DISCOVERY half SHIPPED in-cloud (direct-to-main,
  score-neutral). `asrs/behavioral/free_tier.py` now scans doc prose for a documented
  `?tier=free`/`?mode=free`/`?free=true` opt-in (`_scan_query_param_instruction`) and records
  it as `FreeTierDiscovery.opt_in_query` + an `opt_in_query` evidence key — but does NOT yet
  gate `advertised` or drive the live free-mode call (deliberately score-neutral, test-pinned).
  PROGRESS 2026-07-24T06:18Z (Cycle 30): the **path-based** opt-in DISCOVERY half SHIPPED
  in-cloud (direct-to-main, score-neutral). `asrs/behavioral/free_tier.py`
  `_scan_path_instruction` recognises a documented free-mode endpoint whose path carries a
  conventional free segment (`/free/…`, `/v1/free/…`, `/api/free-tier/call`) → additive
  `FreeTierDiscovery.opt_in_path` + an `opt_in_path` evidence key; precision-first exact
  free-mode ALLOWLIST (bare substring "free" never trips — `/freedom`/`/free-shipping`
  rejected), host consumed-not-captured, non-vacuous context gate (path excised). Like the
  query-param half it does NOT gate `advertised` or drive the live call (test-pinned
  score-neutral). `test_free_tier.py` 9→10; suite 128→129.
  PROGRESS 2026-07-27T16:13Z (Cycle 38): the **request-body-field** opt-in DISCOVERY half
  SHIPPED in-cloud (direct-to-main, score-neutral). `asrs/behavioral/free_tier.py`
  `_scan_body_field_instruction` recognises a documented JSON body-field free-mode opt-in
  (`{"tier":"free"}`/`{"mode":"free"}`/`{"free_tier":true}`) → additive
  `FreeTierDiscovery.opt_in_body` + an `opt_in_body` evidence key. Precision-first: the IN-OBJECT
  gate (double-quoted JSON key inside an open `{…}`) distinguishes a request BODY field from a
  header (`Name: value`) or query (`?name=value`) — both verified None; free-context + explicit
  free-hint gates; plumbing-field denylist. Like the query/path halves it does NOT gate
  `advertised` or drive the live call (test-pinned via the `{"free_tier":true}` fixture the header
  scanner does not also catch). `test_free_tier.py` 10→11; suite 160→161.
  REMAINING: (a) **[LOCAL], score-increasing → invariant #3 live-verify on ≥2 real domains**
  — wire `opt_in_query` AND `opt_in_path` AND `opt_in_body` into the `advertised` gate AND the
  live call path (append the query param / route to the free path / add the body field alongside
  the header; keep the $0-only settle safety byte-for-byte intact), then confirm on ≥2 real
  storefronts that the probe opts in and exercises the $0 allowance correctly; likely peer-gated
  when the scoring path changes. (b) **non-EVM zero-value schemes** (still open). All FOUR
  DOCUMENTED opt-in conventions (header/query-param/path/body-field) are now DISCOVERED in-cloud;
  the remaining generalization is the shared [LOCAL] live-wiring + non-EVM.

- **Header scanner over-catches JSON body fields** (METHOD/attribution precision, Cycle-38
  observation; P1). The existing `_scan_header_instruction` `name: value` regex ALSO matches a
  double-quoted JSON body field like `{"tier": "free"}` (returning it as `opt_in_header`), because
  it allows optional quotes around the name and does not require the field be OUTSIDE a `{…}`
  object. Pre-existing (not introduced by Cycle 38's body-field scanner), and `opt_in_body` itself
  is never read by the `advertised` gate so it moves no score — BUT `opt_in_header` IS gated, so a
  body-only storefront can currently read as header-advertised. Disambiguation (require the header
  match NOT sit inside a `{…}` object, symmetric with the body scanner's in-object gate) is
  score-AFFECTING → peer-gated + [LOCAL] live-verify on ≥2 real domains that the header gate is
  unchanged for genuine header docs and only tightened for JSON-body-only docs. Low urgency (no
  observed real mis-attribution — the canonical pair documents a real header), but it is the honest
  known imprecision of the header/body boundary.
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
  card" item) nor to the relevant methodology section. DONE (the cap-chip half): Cycle 32
  (READOUT) anchor-linked a card's "Grade capped" chip to its methodology §8 cap row via the
  shared `scorecard._cap_anchor` (can't drift; `test_readout.py` 19→23 with a cannot-drift
  test, suite 133→137, replay guard 8/8 / +39.4). REMAINING: the per-check-ROW → evidence-blob /
  methodology-section link (folds into "Evidence links on the card"). No scoring semantics; direct-to-main.

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
