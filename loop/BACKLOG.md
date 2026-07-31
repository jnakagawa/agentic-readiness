# Backlog (prioritized; prune every cycle)

`[LOCAL]` = needs Jonah's machine (codex CLI / zero CLI / paid probes) —
design in-cloud, execute locally.

## P0

- **[LOCAL] Verify the driftflight.com LIVE transactability drop (canonical-anchor divergence)** (TRUTH,
  opened Cycle 126). The LOCAL runner RECOVERED this fire (`runs/local/verify_20260731T085248Z.json`,
  08:52Z Jul-31, attempts=1) and its LIVE static re-score shows driftflight.com **76.2 C / delta +30.1**
  vs the frozen fixture's **85.5 B / +39.4** — the entire ~9pt drop is **transactability 87.5 → 62.5**
  (legibility 90.9 / access 100 / trust 60 all unchanged). This is the live with-rails anchor's
  agent-native payment evidence weakening between the Jul-23 fixture and the Jul-31 live crawl. n=1 from a
  just-recovered runner, so it may be a transient partial-fetch during the wake/network recovery OR a real
  3-day change. NEXT LOCAL FIRE: read the newest 1-2 `verify_*.json` artifacts — (a) if the drop is GONE
  (transactability back to 87.5), it was transient wake-recovery noise → note + close; (b) if 76.2/62.5
  PERSISTS, re-score live (`asrs.cli score driftflight.com`) and DIFF the transactability checks against
  the committed fixture to name WHICH check flipped (candidates: x402-live challenge, a commerce-protocol
  surface, machine-payable evidence), then capture a fresh fixture
  (`asrs.cli score driftflight.com --record-fixture fixtures/canonical/driftflight.com.json`) — but note
  re-capturing MOVES the replay-guard EXPECTED (85.5→~76.2), so it is a peer-gated canonical re-baseline
  (bump the guard's EXPECTED in the SAME PR per the Cycle-17 maintenance contract) and the LOG must
  explain the delta move in capability terms. The in-cloud replay guard (24/24, 46.1 F / 85.5 B / +39.4)
  stays the frozen regression signal until then. FLAG the divergence + the runner recovery in the next
  16:00 UTC digest (~16:1xZ Jul-31).

<!-- DONE 2026-07-28T17:27Z (local fire, SELF-HEALING/METHOD, direct-to-main): "[LOCAL] Local
     verify runner STALLED past the 6h floor" ROOT-CAUSED + FIXED. The cloud's Cycle-51→62
     diagnosis ("launchd not firing / machine asleep") was WRONG — only a local fire could see it.
     The runner's heartbeat log + the unpushed local runs/local/verify_*.json artifacts
     (234101Z/034100Z/110146Z/170500Z) prove the launchd job (org.pie.asrs-local-cycle, :41) FIRES
     every wake; each artifact carries git_pull.ok=false, "Could not resolve host: github.com".
     ROOT CAUSE — a WAKE/NETWORK RACE: launchd runs the missed :41 job on machine WAKE (artifacts at
     odd minutes 14:44/16:56/11:01/17:05 = wake instants), before WiFi/DNS is up, so `git pull` fails
     in the SAME SECOND it starts (vs ~5s on a successful fire) and the runner bailed on that first
     miss with ZERO retry — writing a git-pull-failed artifact it also couldn't push. FIX:
     loop/local_verify.py git_pull_with_retry (bounded wait-for-network, 5×15s ≈60s; still fixed-verb,
     only `pull` hardened) + tests/test_local_verify.py (4). Resynced the pinned
     ~/.local/bin/asrs_local_verify.py from the committed repo copy (self-healing law). EXECUTED the
     repair live (not assumed): the fixed runner pulled on attempt 1 (fast-forwarded Cycle 63), 20
     suites green, canonical 46.1 F / 85.5 B / +39.4, artifact verify_20260728T172734Z.json
     (records attempts:1) pushed + mirrored → the ~18.5h stall CLEARED, live canonical signal restored.
     Score-neutral (git diff -- asrs/ rubric/ EMPTY; rubric v0.7; replay guard 23/23 / +39.4).
     Suite 19→20 files (+test_local_verify, 4). See LOG (Local cycle — 17:27Z). WATCH (folded into the
     runner-health STATE note, not a fresh P0): a wake with a very slow (>60s) network would still
     miss — watch the artifact `attempts` field over the next day; escalate to a longer/adaptive
     backoff or a DNS pre-flight only if it recurs. -->
<!-- DONE 2026-07-28T18:55Z (local fire, COVERAGE, direct-to-main, score-neutral): "[LOCAL] acceptance
     rerun — offering-relative live battery" DISCHARGED on the WITH-RAILS API side — the FIRST end-to-end
     offering-relative LIVE battery. `asrs score driftflight.com --behavioral --battery auto --models
     claude --trials 2` (claude-only: codex reputation-gates BOTH canonical domains 4/4 per the 11:42Z
     characterization, and the offering-relative STRUCTURE under test does not need cross-model — the item
     authorized exactly this). OVERALL 87.8 B / rubric v0.7 / CITABLE (verdict stability 1.00, 2 valid
     runs). OPERATOR ACCEPTANCE CONFIRMED on REAL data, all three criteria on BOTH surfaces:
     (1) driftflight.com physical_good = NA (live discovery claimed {metered_api,subscription,digital_good};
     na_archetypes {physical_good,service_booking,data_retrieval}); (2) spreads over CLAIMED archetypes ONLY
     (cross-task 0.00, between-archetype 0.00 "generalist", NA excluded from every mean/spread);
     (3) NA shown "not offered" on the terminal TASK BATTERY block AND the HTML card Offering-relative
     sub-block (chip na = the 3 NA archetypes). First LIVE between_kind_spread (0.00) + all 3 intents 100%
     completion on real multi-kind data — folds in the two "[LOCAL] Eyeball the battery card" P2 items + the
     between-pill live-eyeball. Hermetic fix (Cycle 32) LIVE-confirmed (--strict-mcp-config, empty fleet).
     Invariant #1 held (agent reached only the FREE tier — 3 free images — blockers note a paid call needs a
     funded wallet, free-tier probe fired once, no nonzero auth). Score-neutral: git diff -- asrs/ rubric/
     tests/ EMPTY (ran the shipped pipeline) → rubric v0.7; canonical PAIR unchanged (18:41Z verify 46.1 F /
     85.5 B / +39.4, replay guard green; behavioral 87.8 is the --behavioral superset of static 85.5:
     +Outcome pillar 100.0 + live trust panel, does NOT move the static delta). Evidence (force-added):
     runs/local/acceptance_battery_driftflightcom_20260728T184325Z.{report.json,log,card.html}. See LOG
     (Local cycle — 18:55Z). The RETAIL-INVERSE behavioral half is the new P0 below. -->
<!-- DONE 2026-07-28T23:10Z (local fire, COVERAGE+TRUTH, direct-to-main, score-neutral): "[LOCAL] acceptance
     rerun — the RETAIL-INVERSE half" + "the calibration NEGATIVE half" BOTH DISCHARGED in one run on a REAL
     no-rails retail store. Domain selection was the work: a run needs a domain reachable by BOTH the python
     discovery path AND the shopper's WebFetch path, with NO agentic rails, a REAL checkout (backlog steered
     away from the books.toscrape sandbox's fake basket). Screened 12+ real retailers — most block agent
     fetchers (lush WebFetch-403; uniqlo agent-ua-hard-blocked -10 + WebFetch-timeout; thriftbooks python-406;
     hydroflask 403) or have ADDED agentic rails (deathwishcoffee llms.txt advertises a UCP merchant profile +
     MCP endpoint + Shop Pay agent checkout → claims metered_api; warbyparker ai-plugin/agent-card/openapi;
     muji/allbirds/misen/leatherman llms.txt → metered_api). Picked `www.moleskine.com` (both gates HTTP 200,
     no llms.txt/no rails, Access 100 = agent-UA reachable NOT env-blocked, physical_good CLAIMED on real
     free-shipping/stock nouns, API archetypes NA; static 49.8 F, transactability 18.8, no-agent-native-payment
     FAIL = the no-rails shape). `asrs score www.moleskine.com --behavioral --battery auto --models claude
     --trials 2` → OVERALL 38.8 F, rubric v0.7, CITABLE (verdict stability 1.00, 2 valid). OPERATOR
     RETAIL-INVERSE ACCEPTANCE CONFIRMED, all three criteria on BOTH surfaces (mirror of 18:55Z .com):
     (1) physical_good CLAIMED/assessed (60% completion), NOT NA (subscription also claimed; na_archetypes =
     {metered_api,digital_good,service_booking,data_retrieval}); (2) spreads over the CLAIMED set only
     (cross-task 0.30, between-archetype 0.30 "somewhat type-dependent", NA excluded); (3) NA shown "not
     offered" on terminal TASK BATTERY block AND HTML card Offering-relative sub-block (chip na = 4 NA
     archetypes, verified in rendered card). CALIBRATION NEGATIVE HALF CONFIRMED (mirror of Cycle 67's positive
     with-rails anchor): static no-agent-native-payment FAIL / transactability 18.8 → behavioral
     machine_payable_path FALSE + no_human_gate FALSE, Outcome 0.0, REPRODUCIBLY (both trials unanimous "no
     machine-payable path — retail purchases are browser-only"). Non-vacuous: physical_good battery intent
     reached 60% (agent CAN browse the store) yet hit the machine-payable + human-gate walls. Invariant #1 held
     (no free tier / no x402 → free-tier probe found nothing to call, x402_live=false, no
     settle/authorization/max_pay/paid; read-only hermetic shopper). Score-neutral (git diff -- asrs/ rubric/
     tests/ EMPTY, ran shipped pipeline) → rubric v0.7; canonical PAIR unchanged (verify_20260728T224103Z
     46.1 F / 85.5 B / +39.4; replay guard 24/24, offering guard 12/12). Evidence force-added:
     runs/local/acceptance_battery_moleskine_20260728T225939Z.{report.json,log,card.html}. See LOG (Local cycle
     — 23:10Z). The cloud-doable follow-up (wire the negative calibration guard against this committed report)
     is the new P0 below. -->
<!-- DONE 2026-07-29T01:1xZ (Cycle 71, TRUTH, direct-to-main, tests-only/score-neutral): "Wire the NEGATIVE
     calibration guard" SHIPPED. `tests/test_calibration.py` +4 (4→8), the executable mirror of Cycle 67's
     positive with-rails anchor, replaying the committed moleskine.com no-rails retail behavioral report:
     (5) negative prediction behaviorally corroborated (static x402_probe not-PASS / x402_live=False /
     transactability 18.75 → NO agent-native payment; behavioral purchase_path/machine_payable/no_human_gate
     all FAIL, Outcome 0.0; free_tier_transaction NA not a wall); (6) genuine reachable retail not a null
     (Access 100, physical_good CLAIMED + API archetypes NA, agent browsed 60% yet hit the payment wall —
     invariant #4); (7) reproducible (both trials FALSE, verdict_stability 1.0); (8) TWO-SIDED capstone (same
     payment checkpoints PASS with-rails / FAIL no-rails, both rubric v0.7, Outcome 100.0 vs 0.0). Calibration
     is now a two-sided property. Tests-only, git diff -- asrs/ rubric/ fixtures/ EMPTY → rubric v0.7, replay
     guard 24/24 / 46.1 F / 85.5 B / +39.4. Suite 240→244. See LOG Cycle 71. The static-fixture cross-validation
     for the negative side is the [LOCAL] follow-up below. -->
- **[LOCAL] Capture a moleskine.com static fixture for the negative calibration anchor** (TRUTH, follow-up to
  Cycle 71). The negative calibration guard (Cycle 71) reads moleskine.com's STATIC prediction from the static
  checks embedded in the committed behavioral report — it has no separate offline replay to cross-validate
  against, unlike the with-rails anchor (tests 1/4 replay `fixtures/canonical/driftflight.com.json`). Capture
  the fixture LIVE — `asrs.cli score www.moleskine.com --record-fixture fixtures/canonical/www.moleskine.com.json`
  (static $0 crawl, needs network → [LOCAL]) — then extend `test_calibration.py` so the negative side gets the
  SAME two-crawl cross-validation: a `_static_report("www.moleskine.com")` replay whose static-observable
  pillars (access/legibility/transactability) match the behavioral report's within 1e-9 (the negative mirror of
  `test_calibration_rests_on_a_shared_static_base`). This proves the negative prediction rests on the same
  static evidence across two independent crawls, closing the honest-scope gap the docstring names.

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
  SEVENTH SURFACE — Cycle 70 (COVERAGE, direct-to-main, score-neutral): the PRICING / BILLING page
  `/pricing` is now read. `asrs/offering._SURFACE_DOCS` gains it — the "understand the offer" surface
  where the per-month / per-generation / pay-as-you-go / seat / credit-metered / volume-tier billing
  prose the signal bank already anchors on most conventionally lives; a site that documents its billing
  ONLY on `/pricing` (thin homepage, no billing detail in llms.txt/OpenAPI) was under-classified. HTML,
  so HTML-stripped (same `_is_html_document` path as `/docs`); SAME precision-guarded signal bank, no new
  signal. Score-neutral VERIFIED NON-VACUOUSLY on committed evidence (unlike a 404-absent surface): the
  canonical `/pricing` is a real 200 — `discover_offering` through `from_fixture` reads it (surfaces_seen
  gains `/pricing`) and reinforces the three already-claimed archetypes, claimed SET+ORDER byte-identical
  `['metered_api','digital_good','subscription']` on both. Off the scoring path (grep-verified; scoring
  probe's `protocols._AGENT_SURFACE_DOCS` untouched); rubric v0.7, replay guard 24/24 / +39.4, canonical
  OFFERING guard 12/12 unchanged. New guard `test_pricing_surface_is_read_live` + wiring test extended;
  `test_offering.py` 23→24; suite 240 tests. See LOG Cycle 70.

- **[LOCAL] Wire + verify the STRUCTURED catalog / pricing JSON surfaces** (COVERAGE, follow-up to Cycle
  70's `/pricing`). The directive names "manifest/**catalog**"; `/catalog.json`, `/pricing.json`, `/plans`
  are conventional structured-JSON offering/billing docs but 404 on EVERY committed fixture, so adding them
  is UNVERIFIABLE in-cloud (a vacuous absent case — cannot prove the read works or is score-neutral).
  Capture a fixture from a real site that serves a structured catalog or pricing JSON (`asrs.cli score
  <domain> --record-fixture fixtures/canonical/<domain>.json`, LIVE → [LOCAL]), then add the path(s) to
  `_SURFACE_DOCS` and wire a read-live guard the same way `/pricing` was (surface read, ≥1 sourced signal
  reaches classification, claimed set unchanged on the canonical pair). Off the scoring path, score-neutral.
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
<!-- SUPERSEDED 2026-07-28T23:57Z (local fire) — "[LOCAL] Second cross_task_spread datapoint" is
     obsoleted by the offering-relative `--battery auto` work. Its goal (a SECOND live spread datapoint,
     exercising per_kind + between_kind_spread on multi-kind data) is DISCHARGED: the 18:55Z with-rails
     driftflight.com run gave between_kind_spread 0.00 ("generalist", 3 claimed archetypes) and the 23:10Z
     moleskine run gave 0.30 ("somewhat type-dependent", 2 claimed archetypes) — a live PAIR of spreads
     across two storefront TYPES. Its remaining sub-goal (b) — force the fixed 5-intent
     `batteries/default_v1.yaml` on drift-flight.org for text_translation/data_enrichment — would REGRESS
     to the pre-directive battery-mismatch the operator explicitly fixed (probing a 3-archetype API with
     tasks it does not claim pollutes the means); NOT worth running. Fixed-YAML multi-kind coverage of the
     two never-claimed archetypes is only meaningful on a site that genuinely CLAIMS them — fold into a
     future population member that does, not a forced mismatch. -->
- **[LOCAL] Grow the calibration population + re-run the sweep on a cadence** (TRUTH, follow-up to the
  first population dataset shipped 2026-07-28T23:57Z, `runs/local/calibration_sweep_20260728T234815Z.json`).
  The first sweep landed 13 scored real domains (rubric v0.7) via `experiments/calibration_sweep.py`. Two
  increments: (a) broaden `POPULATION` toward the item's 15–20 target and better spectrum coverage — add
  more genuine agent-native storefronts (ACP/UCP/MPP merchants, x402-live sites) and more no-rails
  retailers that are agent-fetch reachable (rei.com env-blocked this run; several retailers block agent
  UAs — record which, it is itself a reachability signal); (b) re-run on a weekly cadence and diff against
  the prior dated dataset so population DRIFT is visible (a domain adding/removing rails moves its score).
  Static $0, reuse the shipped harness (`.venv/bin/python -m experiments.calibration_sweep`); force-add the
  dated JSON to `runs/local/`. Keep it vendor-neutral (uniform probes; `segment` is read-only context).
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

- **[LOCAL] Capture a fixture that CLAIMS service_booking and/or data_retrieval** (COVERAGE enabler, from
  Cycle 114's audit). The two weakest offering archetypes — `service_booking` (5 legs: book / appointment /
  reservation / schedule / availability) and `data_retrieval` (5 legs: enrich / dataset / lookup /
  data-service / query-records) — cannot get a NEW capability-worded signal added in-cloud, because NO
  committed fixture claims either (the canonical pair + api.replicate claim metered_api/subscription/
  digital_good; books.toscrape claims physical_good; example.com claims nothing). Adding a signal to a
  never-claimed archetype is UNVERIFIABLE here (a vacuous case — cannot prove it fires non-vacuously or is
  score-neutral). Capture a fixture LIVE from a real agent-facing site that genuinely claims one of these —
  a booking/reservation storefront (a hotel/restaurant/appointment API with `book`/`availability`/`time
  slots`) or a data-enrichment/lookup API (a records-enrichment or dataset-query service) — via
  `asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json` (static $0, needs network →
  [LOCAL]). Then a future COVERAGE cycle can add ONE capability leg to the claimed archetype (e.g.
  service_booking: a `confirmation`/booking-reference or a `reschedule`/cancel-booking control leg;
  data_retrieval: a `bulk-export`/structured-output-format or a `filter`/query-parameter leg) with the same
  non-vacuous read-live guard the metered_api signals got. Off the scoring path, score-neutral.

<!-- TRUTH HALF DONE 2026-07-30T~19:2xZ (Cycle 115, branch+PR+self-merge, tests-only/score-neutral):
     "pin `free-trial` as RELABEL-INVARIANT" SHIPPED. `test_offering_relabel_invariance_free_trial` +
     `_free_trial_signals` in `tests/test_offering_canonical.py` (28→29) extend the signal-level relabel
     family to its THIRD archetype (subscription), after metered_api ×7 + digital_good's output-license.
     Because the real-fixture free-trial evidence is host-FREE (verified live: fires on /llms.txt / /pricing
     / homepage with the host in neither surface key nor quote → a whole-fixture relabel would be VACUOUS),
     the guard scans a SYNTHETIC subscription surface seating the host inside the trial evidence (surface-key
     prefix + adjacent to the trial phrase → in the padded quote window), relabels everywhere, and asserts
     identity-invariance: same match count (1), same host-normalized surface, quote still matches the live
     `free-trial` regex, host absent. TEETH: bare-"trial" distractor (clinical / on trial / trial and error)
     fires ZERO. Off scoring path (scoring.py 0 offering refs) → score-neutral, NOT peer-gated; git diff over
     asrs/ rubric/ fixtures/ EMPTY; PR #79 (squash f220ea6). Replay guard 24/24, 46.1 F / 85.5 B / +39.4;
     rubric v0.7. See LOG Cycle 115. The READOUT half is the P1 below. -->
<!-- DONE 2026-07-30T~23:1xZ (Cycle 116, READOUT, branch+PR+self-merge, display+tests-only/score-neutral):
     "Complete the free-trial arc — the READOUT leg" SHIPPED. Added ONE capability-worded, vendor-neutral
     `<p>` ("Evaluating a subscription at $0 first") to `_write_methodology_page` (`asrs/scorecard.py`) after
     the digital_good "Owning the deliverable" paragraph + a content-presence guard
     `test_methodology_documents_free_trial` in `tests/test_readout.py` (55→56). This is the FIRST
     subscription-archetype offer-side leg to complete a full COVERAGE→TRUTH→READOUT arc (COVERAGE 114 signal
     → TRUTH 115 relabel-invariance → READOUT 116), after seven metered_api arcs (payment-rail 78/79/80,
     async-job 82/83/84, api-auth 86/87/88, error-contract 90/91/92, test-mode 102/103/104, pagination
     106/107/108, cancel-job 110/111/112) + the digital_good rights leg (100). Frames trying the RECURRING
     plan at $0 before any charge begins tied to the $0-only ethos (failure = commit to recurring billing
     sight-unseen); names vendor-neutral trial-offer vocabulary as open conventions (free trial / trial
     period / N-day trial / trial account-allowance / "start your free trial" / "try it free for N days");
     keeps the bare-`trial` precision note (clinical/court/"trial and error" senses = no signal); recognition
     keys on the trial the offer grants not who grants it, pinned by an identity-relabel executable
     regression test; honest scope (diagnostic, off the scoring path). The subscription-side MIRROR of the
     metered_api test-mode leg. Display + tests-only, off the scoring path (`scoring.py` 0 offering refs) →
     score-neutral, NOT peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY. PR #81 (squash
     3067382, merged commit = exactly `asrs/scorecard.py` + `tests/test_readout.py`, +88 lines). Full suite
     green (22 files); replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. See LOG Cycle 116. The
     free-trial arc is now closed at ALL THREE layers (signal 114 / relabel 115 / readout 116). Next COVERAGE
     frontier on the thin archetypes (service_booking / data_retrieval) is [LOCAL]-blocked — see the P1 below. -->
<!-- DONE 2026-07-31T07:12Z (Cycle 124, READOUT, branch+PR+self-merge, display+tests-only/score-neutral):
     "the priced-listing arc has ONE layer left — READOUT" DISCHARGED. Added ONE capability-worded,
     vendor-neutral `<p>` ("Reading the price to fulfill") to `_write_methodology_page`
     (`asrs/scorecard.py`) after the subscription free-trial paragraph + a content-presence guard
     `test_methodology_documents_priced_listing` in `tests/test_readout.py` (57→58). COMPLETES the FIRST
     full COVERAGE→TRUTH→READOUT arc on physical_good (COVERAGE 122 signal → TRUTH 123 relabel-invariance
     → READOUT 124). Frames "read the concrete price beside the item's availability to decide + fulfill a
     physical purchase" as the physical_good mirror of the free-trial-116 / content-provenance-120 prose;
     keeps the bare-amount precision note (a metered per-call / subscription per-month price sits nowhere
     near availability → physical_good stays NA on an API storefront); recognition keys on the price the
     offer lists not who lists it, pinned by the identity-relabel regression test; honest scope
     (diagnostic, off the scoring path). Off the scoring path (`scoring.py` 0 offering refs) →
     score-neutral, NOT peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/ asrs/offering.py`
     EMPTY; --name-only = `asrs/scorecard.py` + `tests/test_readout.py` ONLY. PR #97 (squash 2ccadae,
     merged commit = exactly the two files). Full suite green (22 files); replay guard 24/24, 46.1 F /
     85.5 B / +39.4; offering canonical guard 33/33 (physical_good NA preserved); rubric v0.7. See LOG
     Cycle 124. -->
- **[in-cloud] frontier note (post-Cycle-124): all four CLAIMED archetypes now span COVERAGE→TRUTH→READOUT.**
  physical_good's priced-listing arc is CLOSED at all three layers (SIGNAL 122, TRUTH-relabel 123, READOUT
  prose 124), joining digital_good (content-provenance 118/119/120, output-license 99/100+prose,
  generate-media 94/95/96), subscription (free-trial 114/115/116), and metered_api (7 saturated arcs). Next
  in-cloud COVERAGE candidates on physical_good: further CATALOG legs verifiable on books (a variant/edition
  leg, a product-title/detail leg). service_booking (5 legs) and data_retrieval (5 legs) remain ALL
  [LOCAL]-blocked — no committed fixture claims them richly enough (see the P1 [LOCAL] fixture-capture items).
  METAMORPHIC-AXIS GRID STATE (post-Cycle-125, so a METHOD cycle doesn't re-cover the same cell): FIVE axes
  now exist. RELABEL — org/com/machine/retail/nonstorefront (whole-fixture) + signal-level metered_api ×7,
  digital_good ×2 (output-license, content-provenance), subscription ×1 (free-trial), physical_good ×1
  (priced-listing, Cycle 123 — synthetic surface): DENSE. NOISE-SURFACE — org/com/retail: COVERED (Cycle
  117 added retail). CONTENT-SCALE — org/com/retail: COVERED (Cycle 121 added retail). LISTING-ORDER
  (intra-surface, the FIFTH axis, Cycle 125) — physical_good priced-listing on the synthetic retail pole
  ONLY. Thinnest axis remains SURFACE-ORDER (whole-surface read order) — only output-license (com) + org
  whole-fixture; com/retail/machine whole-fixture and every other signal family UNCOVERED. Next METHOD
  candidates (Cycle 129 is the next METHOD fire): (a) mirror LISTING-ORDER onto a with-rails MACHINE surface
  — do the metered_api endpoints' ORDER within one OpenAPI spec matter to the claim? (multi-endpoint reorder
  within one spec, machine pole); (b) extend surface-ORDER (whole-surface read order) to the .com/machine
  half (retail is single-surface so read-order needs a NA-rails-stay-NA framing, not a permutation);
  (c) a cross-fixture invariant over the now-dense digital_good signal family.

<!-- REVISED 2026-07-31 (Cycle 118 COVERAGE finding): "[COVERAGE, in-cloud] a physical_good FULFILLMENT
     leg on the committed retail fixture" (from Cycle 117's audit) was DEMOTED to [LOCAL]. In-cloud
     verification found the only committed physical_good fixture `books.toscrape.com` is TOO THIN: it trips
     physical_good with ONLY `add-to-cart` + `stock`, its `/llms.txt` + `/llms-full.txt` are REAL 404s, and it
     carries none of the shipping-address / order-tracking / order-status / returns-policy prose a fulfillment
     leg would need (its product-detail inventory tables were not crawled). So a physical_good fulfillment
     signal is UNVERIFIABLE in-cloud (vacuous — cannot prove non-vacuous firing), the same trap as
     service_booking / data_retrieval. See the P1 [LOCAL] rich-retail-fixture item below. Cycle 118 pivoted to
     digital_good `content-provenance` instead (fires non-vacuously on the canonical pair). -->
- **[LOCAL] Capture a RICH retail fixture for physical_good fulfillment legs** (COVERAGE enabler, from
  Cycle 118's in-cloud finding). The committed `books.toscrape.com` retail fixture is too thin to add a NEW
  physical_good signal non-vacuously (only `add-to-cart` + `stock` fire; no shipping/tracking/returns prose;
  llms.txt 404). Capture a fixture LIVE from a real agent-fetch-reachable retailer with a genuine checkout
  that documents fulfillment — shipping options / delivery estimate / order confirmation / order tracking /
  returns policy — via `asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json` (static
  $0, needs network → [LOCAL]; several retailers block agent UAs, so record which — a reachability signal in
  itself). Then a future in-cloud COVERAGE cycle can add ONE capability-worded, vendor-neutral fulfillment leg
  to physical_good with the metered_api non-vacuous shape: a `shipping-address` leg (an agent can supply a
  delivery destination — NB `shipping (address|cost|rates|options|...)` already exists; a NEW leg must be
  distinct), an `order-tracking` / `order-status` leg (confirm fulfillment progress after purchase — NB
  `fulfillment` already matches "tracking number"), or a `returns-window` leg. Precision: `returns` must
  anchor on a genuine return/refund policy, not "returns to the homepage"; `track` on an order, not a music
  track. Off the scoring path, score-neutral.

<!-- TRUTH HALF DONE 2026-07-31T~02:1xZ (Cycle 119, TRUTH, branch+PR+self-merge, tests-only/score-neutral):
     "pin content-provenance as RELABEL-INVARIANT" SHIPPED. `test_offering_relabel_invariance_content_provenance`
     + `_provenance_signals` in `tests/test_offering_canonical.py` (30→31) extend the signal-level relabel family
     to digital_good's SECOND leg (tenth leg overall: metered_api ×7 + output-license + free-trial + this).
     VERIFIED live that content-provenance evidence (C2PA / content credentials / records provenance) is host-FREE
     on all five committed fixtures — the host never lands in the quote window (even on `agents.driftflight.com/*`
     it sits only in the surface KEY) → a whole-fixture relabel would be VACUOUS (free-trial-115 failure mode). So
     the guard scans a SYNTHETIC digital_good surface (host `acme-renders.example`) seating the host INSIDE the
     C2PA evidence (surface-key prefix + padded quote window, asserted non-vacuous), relabels end-to-end, asserts
     identity-invariance (same match count 1, same host-normalized surface, quote still matches the live regex,
     host absent). TEETH: a bare-`provenance`/`credentials` distractor (art/wine/data provenance, login
     credentials, api.replicate-style "watermarking for provenance" model-feature) fires ZERO. Off scoring path
     (`scoring.py` 0 offering refs) → score-neutral, NOT peer-gated; git diff over `asrs/ rubric/ fixtures/`
     EMPTY; PR #87 (squash a8363d3, merged commit = exactly the one test file). Replay guard 24/24, 46.1 F /
     85.5 B / +39.4; rubric v0.7. See LOG Cycle 119. The READOUT half is the item below. -->
- **[READOUT, in-cloud] CLOSE the content-provenance arc — the READOUT leg** (from Cycle 118 COVERAGE / Cycle
  119 TRUTH; the third and final layer of the digital_good `content-provenance` arc, mirroring free-trial 116 +
  output-license prose). Surface "verify the deliverable's provenance at $0" in the public methodology prose
  (`_write_methodology_page`, `asrs/scorecard.py`) — a capability-worded, vendor-neutral `<p>` after the
  digital_good "Owning the deliverable" (output-license) paragraph: frame an agent confirming a generated
  render is genuine (C2PA content credentials / a media-output provenance record) before using it in a
  provenance-aware pipeline; name the open conventions (C2PA / CAI Content Credentials / a media-output
  provenance manifest) as open, never a vendor; keep the precision honesty (bare "provenance"/"credentials" —
  art/wine/data provenance, login credentials — is no signal); honest scope (diagnostic, off the scoring path).
  GUARD: `test_methodology_documents_content_provenance` in `tests/test_readout.py`, same content-presence shape
  as the free-trial/test-mode/cancel-job guards. Display + tests-only, off the scoring path, score-neutral, NOT
  peer-gated. This makes content-provenance the THIRD full COVERAGE→TRUTH→READOUT arc on a non-metered_api
  archetype (after free-trial + output-license) — the natural next READOUT-track pick.

<!-- DONE 2026-07-30T04:16Z (Cycle 97, METHOD, branch+PR+self-merge, tests-only/score-neutral):
     "Pin the digital_good DESCRIPTOR derivation as relabel/identity-invariant" SHIPPED. New guards in
     `tests/test_battery_instantiate.py` (9→12) classify a synthetic surface that names the host INSIDE the
     digital_good evidence, extract the real claim via `classify_offering`, relabel the host everywhere +
     re-classify, and assert the derived descriptor is BYTE-IDENTICAL — the descriptor-layer analog of the
     signal-level relabel guards in `test_offering_canonical.py`. Covers the media-noun branch (relabel →
     still "generated image") AND the translation-LABEL branch (relabel → "translated document"); NON-VACUOUS
     (host genuinely in the base evidence + relabel genuinely rewrites the quotes, both asserted; neutral
     host carries no media word); TEETH (`test_descriptor_relabel_has_teeth` — a host-keyed descriptor stub
     IS caught by the same comparison). Makes the Cycle-96 methodology claim ("the noun comes from the site,
     not ASRS" / "injection-safe") an executable tripwire at the descriptor layer. Tests-only, off scoring
     path → rubric v0.7, git diff over scoring path EMPTY, git diff --name-only = the one test file. NOT
     peer-gated; PR #43 (squash 4340200). Replay guard 24/24, 46.1 F / 85.5 B / +39.4. INFRA folded in: the
     ephemeral container was missing optional `eth-account` (in requirements.txt) → test_free_tier 10/11;
     `pip install eth-account` → 11/11 (environment-only, nothing to commit). See LOG Cycle 97. -->
<!-- P1 FRONTIER (post-Cycle-97): the generate-media arc is now closed at ALL layers — SIGNAL (94),
     DESCRIPTOR (95), READOUT (96), and DESCRIPTOR-RELABEL-INVARIANCE (97). Next METHOD candidate is a fresh
     perturbation AXIS on the offering/battery path (label/scale) now the order- + relabel-invariance
     families are complete, OR a NEW archetype/signal (COVERAGE). Not yet a firm backlog item; promote when
     a concrete gap is identified. -->

<!-- DONE 2026-07-30T11:12Z (Cycle 104, READOUT, branch+PR+self-merge, display+tests-only/
     score-neutral): "[READOUT] Surface the `test-mode` metered_api 'try the call SAFELY first, at $0'
     leg in the public methodology prose" SHIPPED — the READOUT complement CLOSING the test-mode arc
     (COVERAGE 102 → TRUTH-relabel 103 → READOUT 104), the FIFTH metered_api leg to complete the full
     COVERAGE→TRUTH→READOUT arc (after payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88,
     error-contract 90/91/92). Added ONE capability-worded, vendor-neutral `<p>` to the methodology "What
     the score answers" card (`_write_methodology_page`, `asrs/scorecard.py`), between the error-contract
     paragraph and "Owning the deliverable", alongside the four metered_api offer-side legs + the
     digital_good output-license leg (C100). Frames it as rehearsing the call safely first at $0 before a
     real charge (tied to ASRS's $0-only ethos); names the vendor-neutral test-facility vocabulary as open
     conventions (sandbox environment / test-mode flag / test API key / dry-run / `_test_`/`_sandbox_` key
     convention); KEEPS the precision note (bare `sandbox`/`test` — demo-site title / sandboxed iframe /
     `unit_test_runner` — is no signal); names the Cycle-103 identity+key-prefix relabel regression test;
     stays HONEST about scope (diagnostic, off the scoring path, not a scored pillar). New content-presence
     guard `test_methodology_documents_test_mode` in `tests/test_readout.py` (52→53) mirrors
     `test_methodology_documents_output_license`; rendered-page neutral-scan stays clean 4/4. Display +
     tests-only, off the scoring path → NOT peer-gated (git diff --name-only = asrs/scorecard.py +
     tests/test_readout.py ONLY, scoring-path diff EMPTY). Cloud bridge blocks direct main push → branch
     loop/test-mode-methodology-prose + PR + self-merge (squash). Full suite green (test_free_tier 11/11);
     replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. See LOG Cycle 104. -->
<!-- P1 FRONTIER (post-Cycle-104): the test-mode arc is now closed at COVERAGE (102) / TRUTH-relabel (103)
     / READOUT (104) — the fifth metered_api leg to complete the full arc. The test-mode
     surface-read-ORDER-invariance METHOD guard was SUPERSEDED by Cycle 105's stronger whole-profile `.org`
     order guard (see the SUPERSEDED note below); the order-/relabel-invariance families are now COMPLETE
     across both canonical pair-halves. Next candidates are a NEW archetype/signal (COVERAGE) or a
     genuinely NEW perturbation axis (label/scale) on the offering/battery path. -->

<!-- SUPERSEDED 2026-07-30T12:2xZ (Cycle 105, METHOD): "[METHOD] test-mode surface-read-ORDER-invariance
     guard" is FOLDED INTO the stronger whole-profile guard shipped this cycle. As the item itself warned,
     test-mode's non-vacuity is weak (fires ×1 on a single surface `/docs`, so a reorder cannot migrate it).
     Rather than a single-surface bystander test, Cycle 105 shipped `test_offering_surface_order_invariance_org`
     — the "broader per-signal order-stability property" the item named as the alternative: it pins the
     COMPLETE per-archetype (label, surface) evidence map invariant under full surface-read reversal on
     drift-flight.org (which reads 4 surfaces / 41 (label,surface) pairs, incl. test-mode on metered_api),
     so test-mode's order-invariance is now covered AS PART OF the whole-profile map. This also closed the
     pair asymmetry (whole-profile order-invariance previously only on .com; relabel family already spanned
     both). Tests-only, off scoring path, rubric v0.7, replay 24/24 / +39.4. PR #59 (squash 89f2636). See
     LOG Cycle 105. -->
<!-- INVARIANCE FAMILIES COMPLETE (post-Cycle-109): both canonical pair-halves now carry THREE whole-profile
     invariance axes at the offering/task-selection layer — surface-read ORDER (C105 closed the pair),
     host RELABEL, and content SCALE. The SCALE axis (the "duplication stability" candidate this note named)
     SHIPPED Cycle 109: `_assert_content_scale_invariance` (K=3× surface-body duplication → whole profile
     byte-identical: ranked archetypes + per-archetype strength/(label,surface,quote) map + NA set), on
     both `_org`/`_com`, with teeth (anchor raw match count 1→3, a count-based reader WOULD differ). PR #67
     / squash 926e22f; offering canonical guard 23→25. A FURTHER METHOD axis on this path (e.g. surface-set
     robustness: does adding an irrelevant 200 surface perturb the claimed set? or truncation stability) is
     possible but lower-leverage than a NEW archetype/signal (COVERAGE). Promote only when a concrete
     non-vacuous axis is identified — do NOT add another order/relabel/scale single-signal mirror. -->

<!-- DONE 2026-07-30T14:2xZ (Cycle 107, TRUTH, branch+PR+self-merge, tests-only/score-neutral):
     "[TRUTH] Pin the new `pagination` metered_api signal as relabel-invariant" SHIPPED — the SIXTH
     metered_api signal-level relabel guard, completing the family (payment-rail C79 / async-job C83 /
     api-auth C87 / error-contract C90 / test-mode C103 / now pagination C107). New
     `test_offering_relabel_invariance_pagination` in `tests/test_offering_canonical.py` (22→23). It
     mirrors the async-job guard rather than error-contract as the item first sketched: pagination fires
     ONCE on `api.replicate.com`'s `/openapi.json` with a HOST-FREE quote ("A URL pointing to the next
     page of collection objects") AND a relative `/openapi.json` surface, so it is a SURFACE-PRESENCE
     invariance anchored at the FIXTURE level (assert the host IS present in the fixture surfaces the
     classifier fetches → the whole-fixture relabel does real work), not a quote-anchored one. Under
     `api.replicate.com`→`vendor-neutral.test` relabel: SAME count (1), SAME host-normalized surface, each
     quote STILL matching the live pagination regex, vendor host absent. Tests-only, off the scoring path
     (`scoring.py` does not import `offering` — grep-verified) → score-neutral, NOT peer-gated. git diff --
     asrs/ rubric/ fixtures/ EMPTY; git diff --name-only = tests/test_offering_canonical.py ONLY. Cloud
     bridge blocks direct main push → branch loop/pagination-relabel-invariance + PR #63 + self-merge
     (squash 94fca4a). Full suite clean; test_free_tier 11/11 (after `pip install eth-account`,
     environment-only). Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. See LOG
     Cycle 107. The READOUT leg closing the arc is the item below. -->
<!-- DONE 2026-07-30T15:16Z (Cycle 108, READOUT, branch+PR+self-merge, display+tests-only/score-neutral):
     "[READOUT] Surface the `pagination` 'walk the paged collection to completion' leg in the methodology
     prose" SHIPPED — the READOUT complement CLOSING the pagination arc (COVERAGE 106 → TRUTH-relabel 107 →
     READOUT 108), the SIXTH metered_api leg to complete the full COVERAGE→TRUTH→READOUT arc (after
     payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88, error-contract 90/91/92, test-mode
     102/103/104). Added ONE capability-worded, vendor-neutral `<p>` ("Walking the whole collection") to the
     methodology "What the score answers" card (`_write_methodology_page`, `asrs/scorecard.py`), between the
     error-contract paragraph and "Trying the call safely first". Frames walking a multi-page result set to
     completion (cursor param carrying a value / next-previous page URL / paginated collection response);
     names the under-completion failure (stop at page one → partial answer reported as whole); KEEPS the
     precision note (bare `next`/`cursor` — retail product link / "next campaign" banner / text cursor /
     "next page of the novel" — is no signal); names the identity-relabel regression test; stays HONEST
     about scope (diagnostic, off the scoring path, not a scored pillar). New content-presence guard
     `test_methodology_documents_pagination` in `tests/test_readout.py` (53→54) mirrors
     `test_methodology_documents_test_mode`; neutral-scan clean. Display + tests-only, off the scoring path
     → NOT peer-gated (git diff --name-only = asrs/scorecard.py + tests/test_readout.py ONLY; scoring-path
     diff EMPTY). Cloud bridge blocks direct main push → branch loop/pagination-methodology-prose + PR #65
     + self-merge (squash 82eacd1). Full suite green (test_free_tier 11/11); replay guard 24/24, 46.1 F /
     85.5 B / +39.4, 0 replay-miss; rubric v0.7. See LOG Cycle 108. -->

<!-- P1 FRONTIER (post-Cycle-108): the metered_api COLLECTION-retrieval (`pagination`) arc is now closed at
     ALL layers — SIGNAL (C106), TRUTH-relabel (C107), READOUT (C108) — the sixth full metered_api arc. The
     order-/relabel-invariance families are complete across both canonical pair-halves. Remaining COVERAGE
     frontier is a NEW archetype/signal (the thin service_booking / data_retrieval banks need a fixture that
     CLAIMS them — [LOCAL] fixture capture — before any signal there is non-vacuous in-cloud). The fresh
     METHOD perturbation axis this note named (label/scale) was DISCHARGED Cycle 109 (content-SCALE
     invariance, PR #67) — see the INVARIANCE-FAMILIES-COMPLETE note above; the invariance families are now
     three-fold and pair-symmetric, so COVERAGE (a new archetype/signal) now outranks another offering-path
     METHOD mirror. ACP/UCP/MPP + free-tier live-wiring stays [LOCAL]. -->

<!-- DONE 2026-07-30T~17:2xZ (Cycle 111, TRUTH, branch+PR+self-merge, tests-only/score-neutral): "[TRUTH]
     Pin the new `cancel-job` metered_api signal as RELABEL-INVARIANT" SHIPPED — the SEVENTH metered_api
     signal-level relabel guard (after payment-rail 79 / async-job 83 / api-auth 87 / error-contract 91 /
     test-mode 103 / pagination 107), completing the metered_api signal-level relabel family for every
     signal landed through Cycle 110. New `test_offering_relabel_invariance_cancel_job` in
     `tests/test_offering_canonical.py`, a close mirror of the pagination/async-job guards (surface-presence,
     host-free): fires ×1 on `api.replicate.com`'s `/openapi.json` (a real `Cancel-After` header), quote +
     relative surface name no vendor → non-vacuity anchored at the FIXTURE level (host present in fetched
     surfaces → whole-fixture relabel to `vendor-neutral.test` genuinely rewrites classifier input); under
     relabel SAME count (1), SAME host-normalized surface, each quote STILL matching the live cancel-job
     regex, vendor host absent. Tests-only, off scoring path (`scoring.py` does not import `offering`) →
     score-neutral, NOT peer-gated: git diff over `asrs/ rubric/ fixtures/` EMPTY, git diff --name-only =
     `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct main push → branch
     loop/cancel-job-relabel-invariance + PR #71 + self-merge (squash 98f2b27). offering canonical guard
     25→26; full suite 22 files green (test_free_tier 11/11 after env-only `pip install eth-account`).
     Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
     rubric v0.7). See LOG Cycle 111. The READOUT leg below completes the cancel-job arc. -->

<!-- DONE 2026-07-30T~17:3xZ (Cycle 112, READOUT, branch+PR+self-merge, display+tests-only/score-neutral):
     "[READOUT] Surface the `cancel-job` metered_api capability in the public methodology prose" SHIPPED —
     the READOUT leg CLOSING the cancel-job arc (COVERAGE 110 → TRUTH-relabel 111 → READOUT 112), the
     SEVENTH metered_api offer-side leg to complete the full COVERAGE→TRUTH→READOUT arc (after payment-rail
     78/79/80, async-job 82/83/84, api-auth 86/87/88, error-contract 90/91/92, test-mode 102/103/104,
     pagination 106/107/108). Added ONE capability-worded, vendor-neutral `<p>` ("Aborting a runaway job")
     to the methodology "What the score answers" card (`_write_methodology_page`, `asrs/scorecard.py`),
     placed after the async-job "Finishing the job" paragraph as the CONTROL leg of the same asynchronous
     contract: a long-running job keeps BILLING while it runs, so an agent that cannot STOP a runaway/wrong
     job keeps paying for compute it no longer wants — an offer that documents a cancellation contract lets
     the agent BOUND its own spend (the same $0-only capital-safety ethos ASRS holds). Names the
     vendor-neutral REST cancellation vocabulary (a `.../cancel` endpoint on a job resource, a `Cancel-After`
     deadline header, a `canceled` job state); KEEPS the precision note (bare `cancel` — "cancel your
     subscription", a cancellation policy, "cancel your order", a canceled flight — is no signal); names the
     Cycle-111 identity-relabel regression test; HONEST scope (diagnostic, off the scoring path, not a scored
     pillar). New content-presence guard `test_methodology_documents_cancel_job` (test_readout.py 53→54)
     mirrors the pagination/test-mode guards; rendered-page neutral-scan (test_readout_wording) stays clean.
     Display+tests-only, off scoring path → NOT peer-gated: git diff over asrs/scoring.py/asrs/offering.py/
     rubric/fixtures EMPTY; git diff --name-only = asrs/scorecard.py + tests/test_readout.py ONLY. Cloud
     bridge blocks direct main push → branch loop/cancel-job-methodology-prose + PR #73 + self-merge (squash
     f0e5ba0). Full suite green 306→307 (test_free_tier 11/11 after env-only `pip install eth-account`);
     replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. See LOG Cycle 112. -->
<!-- P1 FRONTIER (post-Cycle-113): the offering-path invariance family is now FOUR-fold and pair-symmetric —
     RELABEL (host rename) / ORDER (surface-read reversal) / SCALE (content duplication) / NOISE (Cycle 113:
     a signal-free added surface leaves the capability profile byte-identical). The genuinely-new-perturbation-
     axis METHOD lever is now well-exercised; the strongest UNTAPPED leverage has shifted to COVERAGE. Concrete
     candidate (COVERAGE, next non-METHOD cycle): the metered_api bank has SEVEN offer-side legs
     (payment-rail / async-job / api-auth / error-contract / test-mode / pagination / cancel-job) each with a
     full COVERAGE→TRUTH→READOUT arc, while `subscription`, `service_booking`, and `data_retrieval` are
     THINLY signalled by comparison. Audit `asrs/offering._SIGNALS` for the weakest-covered archetype and add
     ONE capability-worded, vendor-neutral signal to it (precision-guarded, ≥7 positives / ≥8 negatives,
     off the scoring path so score-neutral) — this broadens measurement coverage across archetypes instead of
     deepening the already-deep metered_api bank. Promote to a firm P1 item once the specific archetype+signal
     is chosen. ACP/UCP/MPP handshakes + free-tier live-wiring stay [LOCAL]. -->


<!-- DONE 2026-07-30T06:2xZ (Cycle 99, TRUTH, branch+PR+self-merge, tests-only/score-neutral): "Pin the
     new `output-license` digital_good signal as HOST/VENDOR relabel-invariant" SHIPPED. New guard
     `test_offering_relabel_invariance_output_license` in `tests/test_offering_canonical.py` (17→18) — the
     FIRST extension of the signal-level relabel family (payment-rail C79 / async-job C83 / api-auth C87 /
     error-contract C90, all metered_api) off metered_api into digital_good. SURFACE-PRESENCE invariance
     mirroring `error-contract`: rights vocabulary (commercial licence / royalty-free / usage rights / "you
     own the output") is HOST-FREE so the fired QUOTES carry no host; non-vacuity anchors on the host inside
     the surface KEYS — `output-license` fires 6× on driftflight.com, 3 surfaces embed the host
     (`agents.driftflight.com/llms.txt`, `.../llms-full.txt`, `.../manifest.json`), so a whole-fixture relabel
     rewrites the surfaces the signal reads. Under relabel: same count (6), same host-normalized surfaces,
     each quote still matching the live regex, vendor host `vendor-neutral.test` absent from all evidence; a
     commercial-USE licence grant asserted present in base evidence. Tests-only, off scoring path → rubric
     v0.7 → NOT peer-gated: git diff over scoring/rubric/probes/protocols/fetch/offering/battery/fixtures/
     batteries EMPTY; git diff --name-only = tests/test_offering_canonical.py ONLY. Cloud bridge blocks direct
     push → branch loop/output-license-relabel-invariance + PR #47 + self-merge (squash c52f082). Canonical
     PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss); full suite
     22 files green (test_free_tier 11/11 after env-only `pip install eth-account`). See LOG Cycle 99. -->
<!-- DONE 2026-07-30T07:16Z (Cycle 100, READOUT, branch+PR+self-merge, display-only + tests-only/
     score-neutral): "Surface the digital_good `output-license` RIGHTS leg in the public methodology prose"
     SHIPPED — the READOUT complement CLOSING the deliverable-rights arc (Cycle 98 COVERAGE signal + Cycle 99
     TRUTH relabel guard + this READOUT). Added ONE capability-worded, vendor-neutral paragraph to the
     methodology "What the score answers" card (`_write_methodology_page`, `asrs/scorecard.py`), placed
     alongside the four metered_api offer-side legs (payment-rail/auth/async-job/error-contract): ASRS reads
     whether a generation storefront grants usage rights on its output (a commercial licence / royalty-free
     terms / stated usage rights / ownership — "you own the output"), because an agent handed a render it has
     NO licence to USE has not completed the commercial job. Preserves the signal's bare-`license` PRECISION
     note (a software/business/hosted-model licence is no signal) and names the identity-relabel executable
     regression test that pins vendor-neutrality. New guard `test_methodology_documents_output_license`
     (test_readout.py 51→52). Display+tests-only, off scoring path → NOT peer-gated: git diff over
     scoring.py/rubric*/rubric/probes.py/protocols.py/fetch.py/offering.py/battery.py/fixtures/batteries
     EMPTY; git diff --name-only = asrs/scorecard.py + tests/test_readout.py ONLY. Cloud bridge blocks direct
     main push → branch loop/output-license-methodology + PR #49 + self-merge (squash 40b1ac4). Full suite 22
     files green (test_free_tier 11/11 after env-only `pip install eth-account`); replay guard 24/24,
     46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. See LOG Cycle 100. The output-license
     COVERAGE→TRUTH→READOUT arc is now complete at all three layers (98/99/100), mirroring the four
     metered_api legs. -->
<!-- DONE 2026-07-30T09:24Z (Cycle 102, COVERAGE, branch+PR+self-merge, score-neutral): "a NEW
     metered_api signal" SHIPPED — a `test-mode` signal (API SANDBOX / test-key / dry-run facility) in the
     `metered_api` bank of `asrs/offering.py`, the first new metered_api capability signal since
     error-contract (the output-license digital_good arc closed at 98–101). An agent that obtains a
     test/sandbox credential validates its integration + dry-runs a call at ZERO cost before authorizing
     anything real — the "provision + complete the job safely, without a human" capability, aligned with
     ASRS's $0-only ethos; distinct from api-auth/rate-limited/async-job/error-contract (none said whether
     an agent can TRY the call safely first). Vendor-neutral, precision-critical: never matches bare
     `sandbox`/`test` (books.toscrape's "Books to Scrape - Sandbox" TITLE trips a bare anchor 3×), requires
     a named testing facility / `test mode` / `dry-run` / the `<prefix>_test_`/`_sandbox_` key convention
     with a masked-ellipsis or digit-bearing stub (`df_test_...` fires, `unit_test_runner` does not). Fires
     on BOTH canonical `/docs`, ZERO on api.replicate/books/example. Off scoring path → score-neutral, NOT
     peer-gated (Cycle-98 class); PR #53 (squash 4da5024). Tests +3 (test_offering 38→40,
     test_offering_canonical 19→20). Canonical claimed SET+ORDER byte-identical; replay guard 24/24 / 46.1 F
     / 85.5 B / +39.4. SECRET-SCANNING lesson: initial push declined on a synthetic `sk_test_…` example key
     → replaced with neutral `kv_test_…`, amended the UNPUBLISHED commit (did NOT bypass the scanner). See
     LOG Cycle 102. TRUTH follow-up (below). -->
- **Pin the `test-mode` metered_api signal as HOST/VENDOR relabel-invariant** (TRUTH, follow-up to Cycle
  102, IN-CLOUD doable — the TRUTH mirror of Cycle 99's output-license guard). The new `test-mode` signal's
  key-prefix branch matches the canonical `df_test_...` stub, and `df` is the host stem (drift**f**light) —
  so unlike the surface-presence signals (error-contract/output-license), the FIRED QUOTE here can embed
  the host. Add `test_offering_relabel_invariance_test_mode` to `tests/test_offering_canonical.py`: replay
  the canonical driftflight.com fixture, relabel the host everywhere, re-classify, and assert the test-mode
  signal fires the SAME count on the SAME (host-normalized) surfaces with the digital-good/metered claim
  invariant — proving the match keys on the DECLARED test/live credential DICHOTOMY, not on the vendor's
  name. Non-vacuity: the `df_test_`/`df_live_` stubs carry the host stem, so the relabel does real work.
  Tests-only, off scoring path → NOT peer-gated. Alternatively a surface-read-ORDER-invariance guard (the
  Cycle-101 axis) for test-mode.
<!-- P1 FRONTIER (post-Cycle-101): the deliverable-rights (`output-license`) arc is now closed at ALL layers
     — SIGNAL (98), TRUTH-relabel (99), READOUT (100), and METHOD surface-read-ORDER-invariance (Cycle 101,
     `test_offering_surface_order_invariance_output_license`, PR #51 / 880e0a8). The rights leg's two
     offering/battery perturbation axes (identity-relabel + surface-read-order) are both covered. Next METHOD
     candidate is an order/count-stability axis for ANOTHER digital_good signal that fires multi-surface
     (generate-media / render / hosted-output), OR a NEW archetype/signal (COVERAGE — the frontier the
     rotation now points at). Not yet a firm backlog item; promote when a concrete gap is identified. -->
<!-- P1 FRONTIER (post-Cycle-100): the deliverable-rights (`output-license`) arc is closed at SIGNAL (98),
     TRUTH-relabel (99) and READOUT (100). Next METHOD candidate is a fresh perturbation AXIS on the
     offering/battery path for the digital_good RIGHTS leg (a rights-signal ORDER-invariance or
     count-stability guard, the digital_good analog of the metered_api signal families) — SHIPPED Cycle 101.
     Superseded by the post-Cycle-101 frontier note above. -->
- **[LOCAL] Cross-validate the `output-license` READOUT + signal on a REAL captured fixture** (TRUTH/METHOD,
  optional hardening, follow-up to Cycles 98–100). The signal + descriptor + methodology prose are all pinned
  in-cloud against the committed canonical fixtures + synthetic surfaces. For parity with the negative
  calibration anchor, capture a fresh generation storefront whose surfaces grant explicit usage rights on
  their output (`asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json`, LIVE → [LOCAL]),
  and confirm on a THIRD independent crawl that `output-license` fires with a real deliverable-rights quote
  and that the digital_good task is derived + rights-surfaced end-to-end. Off scoring path, score-neutral.
  Low priority — the in-cloud guards already exercise the full path; this adds real-crawl substrate.
- **[LOCAL] Extend descriptor relabel-invariance to a REAL captured fixture** (METHOD, follow-up to Cycle 97,
  optional hardening). Cycle 97 pins descriptor relabel-invariance through a SYNTHETIC surface in
  `test_battery_instantiate.py` (no network). For parity with the signal-level guards — which replay the
  committed canonical fixtures — capture a real generation storefront's fixture whose digital_good evidence
  embeds the host in its media quote (`asrs.cli score <domain> --record-fixture
  fixtures/canonical/<domain>.json`, LIVE → [LOCAL]), then add a fixture-replaying descriptor-invariance
  guard in `test_offering_canonical.py` alongside the classification-invariance ones. Off scoring path,
  score-neutral. Low priority — the synthetic guard already exercises the full classify→descriptor path;
  this only adds real-crawl substrate.

<!-- DONE 2026-07-30T03:1xZ (Cycle 96, READOUT, branch+PR+self-merge, display-only + tests-only/score-neutral):
     "surface the offering-relative digital_good task derivation in public methodology prose" SHIPPED —
     the READOUT complement CLOSING the generate-media plural/participle arc (Cycle 94 COVERAGE signal +
     Cycle 95 TRUTH descriptor + this READOUT). Added ONE capability-worded, vendor-neutral paragraph to
     methodology section 6 (`_write_methodology_page`, `asrs/scorecard.py`): the buying directives are
     OFFERING-RELATIVE (one task per capability the site CLAIMS to sell, unadvertised archetypes never probed
     — attribution honesty applied to tasks); the digital-good task is worded in the SITE'S OWN terms
     ("generated image" comes from the site, drawn from ASRS's vendor-neutral media vocabulary
     image/video/audio/art or the "digital output" fallback matched to the site, NEVER by injecting arbitrary
     site prose → injection-safe, no vendor product); recognition is form-normalized (image / images /
     generating images → same singular task noun) and pinned by an executable regression test; honestly
     scoped as diagnostic, off the scoring path. Score-neutral: git diff over scoring path
     (scoring/rubric/probes/offering/battery/fixtures/batteries) EMPTY → rubric v0.7 (not peer-gated);
     replay guard 24/24, 46.1 F / 85.5 B / +39.4. test_readout 50→51 (new guard
     test_methodology_documents_offering_relative_battery, registered in main()); readout/rubric wording 4/4
     each. PR #41 (squash 4f269ed). See LOG Cycle 96. Follow-up (descriptor relabel-invariance) is the P1
     item above. -->

<!-- DONE 2026-07-30T02:17Z (Cycle 95, TRUTH, branch+PR+self-merge, descriptor-only/score-neutral):
     "digital_good DESCRIPTOR shares the singular-media-noun assumption" CLOSED. Extended
     `asrs/battery._MEDIA_RE` from `\b(image|video|audio|art)\b` to `\b(image|video|audio|art)s?\b` (the
     `s?` OUTSIDE the capture group, so plural forms match while `group(1)` still yields the singular word).
     A digital_good claim whose ONLY fired media quote is plural (the canonical `/docs` "Generated images",
     "we generate videos") now yields "generated image" instead of the generic "digital output" fallback —
     descriptor and the Cycle-94 generate-media SIGNAL now share the same plural/participle awareness.
     Score-neutral: git diff --stat over scoring.py/rubric*/probes*/offering.py/fixtures/batteries EMPTY →
     rubric v0.7 (descriptor off the scoring path, `--battery auto` only); replay guard 24/24, 46.1 F /
     85.5 B / +39.4 (canonical descriptor already "generated image" via its singular quote → unchanged on
     the pair). test_battery_instantiate 8→9 (non-vacuous: real `/docs` "Generated images" recovers
     "generated image", pre-fix singular-only pattern proven not to match "images"; plural of each media
     noun; precision negative for plural non-media nouns; singular pinned). PR #39 (squash ceedf2d). See LOG
     Cycle 95. NOTE: the generate-media plural/participle arc is now closed at BOTH signal (Cycle 94) and
     descriptor (Cycle 95) layers; the READOUT complement (surface in methodology prose that the
     digital_good task is derived from the site's own discovered, singular/plural-normalised media language)
     is a Cycle-95 "Next READOUT" candidate, not yet a backlog item. -->


<!-- DONE 2026-07-30T01:12Z (Cycle 94, COVERAGE, branch+PR+self-merge, discovery-only/score-neutral):
     generate-media plural/participle RECALL GAP closed. Broadened the digital_good generate-media signal
     from singular-imperative only (`generate an image`) to all verb inflections + plural media noun +
     optional article/possessive object. A generation storefront using only "we generate videos" /
     "generating images" previously fired NO generate-media signal (could miss digital_good entirely); now
     recognised. Precision preserved (regenerate/imagery/output/response/reports reject). Score-neutral:
     classification byte-identical on all five committed fixtures (singular already fired on canonical →
     claimed set/order/quote unchanged); rubric v0.7 untouched, replay guard 46.1 F / 85.5 B / +39.4.
     test_offering 34→36 (precision+non-vacuity guard + real-captured-/docs plural anchor). PR #37 (squash
     e207040). See LOG Cycle 94. Follow-up (descriptor plural) is the P1 item above. -->

<!-- DONE 2026-07-29T05:1xZ (Cycle 75, TRUTH, branch+PR+self-merge, tests-only/score-neutral):
     "Relabel-invariance for the api.replicate.com machine-surface fixture" SHIPPED. New
     `test_offering_relabel_invariance_machine` (test_offering_canonical 12→13) relabels the host to
     `vendor-neutral.test` everywhere and replays through the REAL `from_fixture → discover_offering`,
     asserting claimed list (ordered `[metered_api]`) + NA set identical to the un-relabeled run —
     proving the metered_api task SELECTION keys on the endpoint STRUCTURE (POST to a versioned API path)
     not the vendor NAME. Quote-anchored non-vacuity (host in the base `post-endpoint` metered_api
     evidence quote), same substrate as the pair; existing negative-control gives the shared assertion
     teeth. `_assert_offering_relabel_invariant` refactored to take an optional `exp` set. Offering
     relabel coverage now 3 quote-anchored (org/com/machine) + 2 surface-presence (retail/nonstorefront).
     Tests-only, git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY → rubric v0.7, replay guard 24/24 /
     46.1 F / 85.5 B / +39.4. See LOG Cycle 75. Folds into the recurring "extend relabel-invariance to
     more fixtures as they land" item. -->
<!-- DONE 2026-07-29 (Cycle 85, METHOD, branch+PR+self-merge, tests-only, off scoring path): the scorer's
     MULTI-CAP ORDER-INVARIANCE is now pinned. `test_scoring.py::test_multi_cap_order_invariance` (11→12)
     scores a synthetic two-binding-cap report under FOUR deterministic arrival orders and asserts the
     metric-bearing surface (capped overall 59.0, grade F, SET of binding caps, pillar scores) is byte-
     identical, honestly scoping the `caps_applied` LIST order as a readout detail that varies. Closes the
     rung the canonical-replay input-order guard (guard 19) names but cannot reach — its fingerprint omits
     caps_applied and no committed fixture binds a cap. Rubric v0.7, replay 24/24 / 46.1 F / 85.5 B / +39.4.
     PR #20 (squash 76f83cb). NOTE for a future cycle: do NOT "tighten guard 19's fingerprint to include
     sorted(caps_applied)" — it would be VACUOUS on the canonical population (caps_applied is empty on all
     four fixtures), which is exactly why the ≥2-binding-cap case needs a synthetic report; guard 19 stays
     as-is. See LOG Cycle 85. -->
- **Extend relabel-invariance as new offering fixtures land** (TRUTH/METHOD, cloud-doable, recurring —
  sub-item of the Adversarial referee pass). `test_offering_canonical.py`'s relabel family now covers all
  FIVE committed offering fixtures (pair + machine quote-anchored; retail + non-storefront surface-presence,
  Cycle 75). When a NEW committed offering fixture lands (e.g. a structured-catalog capture, or a new
  archetype anchor), add its relabel case — quote-anchored (`_assert_offering_relabel_invariant(domain,
  exp)`) if the classifier's evidence quote embeds the host, else surface-presence
  (`_assert_offering_relabel_general`). Keeps the vendor-neutrality tripwire spanning the full fixture set.
  DONE 2026-07-29 (Cycle 79, TRUTH, branch+PR+self-merge, tests-only/score-neutral): the Cycle-78
  `agent-payment-rail` candidate SHIPPED as a SIGNAL-level relabel guard —
  `test_offering_relabel_invariance_payment_rail` (test_offering_canonical 13→14) relabels driftflight.com's
  host everywhere and asserts the rail signal survives with the same match count (2), the same host-normalized
  surfaces (agent `/llms-full.txt` settlement-asset form + `/manifest.json` structured `"protocol":"<rail>"`
  form), each relabeled quote still matching the live signal regex with the vendor host gone — proving the
  rail claim keys on PROTOCOL/SETTLEMENT structure, not the host/vendor NAME. NOTE: the quote does NOT embed
  the FULL host (`.com/openapi.json` is a truncated window fragment, not `driftflight.com`); non-vacuity
  anchors on the rail-signal SURFACES (`agents.driftflight.com/…`) instead, and quote byte-equality modulo
  host is deliberately not asserted (host-length change shifts the fixed-width window). Tests-only, rubric
  v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4. See LOG Cycle 79. Item stays OPEN for the NEXT new
  offering fixture (structured-catalog capture / new archetype anchor).
  DONE 2026-07-29 (Cycle 83, TRUTH, branch+PR+self-merge, tests-only/score-neutral): the Cycle-82
  `async-job` candidate SHIPPED as a SIGNAL-level relabel guard —
  `test_offering_relabel_invariance_async_job` (test_offering_canonical 14→15) relabels the committed
  `api.replicate.com` fixture host everywhere and asserts the async-job signal survives with the same match
  count (1), the same host-normalized surface (`/openapi.json`), each relabeled quote still matching the live
  async-job regex, vendor host absent from every piece of async evidence — proving the async-contract claim
  keys on the CONTRACT STRUCTURE (webhook/poll/async vocabulary), not the host/vendor NAME. Clean
  surface-presence / structural-re-match case: the async-contract quote is host-FREE by nature (webhook/poll
  words, relative `/openapi.json` surface), so non-vacuity anchors at the FIXTURE level (host present in the
  fetched surfaces) and the test asserts the host-free nature explicitly rather than overclaiming a quote
  anchor. Tests-only, rubric v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4. See LOG Cycle 83. Item stays
  OPEN for the NEXT new offering fixture (structured-catalog capture / new archetype anchor) or new signal.
  DONE 2026-07-29 (Cycle 87, TRUTH, branch+PR+self-merge, tests-only/score-neutral): the Cycle-86 `api-auth`
  candidate SHIPPED as a SIGNAL-level relabel guard — `test_offering_relabel_invariance_api_auth`
  (test_offering_canonical 15→16) relabels driftflight.com's host everywhere and asserts the api-auth signal
  survives with the same match count (5), the same host-normalized surfaces (signal did not migrate), each
  relabeled quote still matching the live `api-auth` regex, and the vendor host gone from every piece of auth
  evidence — proving an access/auth scheme keys on the SCHEME STRUCTURE (`Authorization: Bearer` header,
  `X-API-Key`, an OpenAPI securityScheme, OAuth2), not the host/vendor NAME. QUOTE-ANCHORED non-vacuity like
  payment-rail (the homepage evidence quote embeds `api.driftflight.com/v1/... Authorization: Bearer`); HONEST
  MIXED CASE (the signal also fires on host-free `/docs` and host-embedding `api.driftflight.com/openapi.json`
  surfaces — the non-vacuity anchor is the QUOTE that embeds the host). Byte-equality modulo host deliberately
  not asserted (host-length change shifts the fixed-width window); structural re-match is the robust invariant.
  Tests-only, rubric v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4. PR #24 (squash d3be0f6). See LOG
  Cycle 87. The signal-level relabel family now covers all THREE recently-landed metered_api signals
  (payment-rail, async-job, api-auth). Item stays OPEN for the NEXT new offering fixture (structured-catalog
  capture / new archetype anchor) or new signal.
  DONE 2026-07-29 (Cycle 91, TRUTH, branch+PR+self-merge, tests-only/score-neutral): the Cycle-90
  `error-contract` candidate SHIPPED as a SIGNAL-level relabel guard —
  `test_offering_relabel_invariance_error_contract` (test_offering_canonical 16→17) relabels driftflight.com's
  host everywhere and asserts the error-contract signal survives with the same match count (3), the same
  host-normalized surfaces (signal did not migrate), each relabeled quote still matching the live
  `error-contract` regex, and the vendor host gone from every piece of error-contract evidence — proving a
  documented error contract keys on WHAT is declared (status codes / `application/problem+json` / snake_case
  error codes) not WHO declares it. SURFACE-PRESENCE like async-job (host-free QUOTES) but a STRONGER case:
  two of the three firing surfaces embed the host in the surface KEY
  (`agents.driftflight.com/llms-full.txt`, `api.driftflight.com/openapi.json`; the third `/docs` is
  host-free), so the whole-fixture relabel genuinely rewrites the surface keys the signal reads and the
  host-normalization step does real work (unlike async-job's lone host-free `/openapi.json`). Both host-free
  structural forms exercised (OpenAPI status-keyed response object + status code paired with a snake_case
  error code). Tests-only, rubric v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4. PR #32 (squash
  be61b99). See LOG Cycle 91. The signal-level relabel family now covers all FOUR recently-landed metered_api
  signals (payment-rail, async-job, api-auth, error-contract). Item stays OPEN for the NEXT new offering
  fixture (structured-catalog capture / new archetype anchor) or new signal — none currently pending
  in-cloud (the next COVERAGE signal is [LOCAL]-gated on a fixture capture; the in-cloud frontier is thin).
  ARC NOTE (Cycle 92, READOUT): the READOUT complement for error-contract shipped (PR #34, squash 49aff18,
  methodology prose paragraph + `test_methodology_documents_error_contract`), so all FOUR metered_api signals
  now have the full COVERAGE→TRUTH→READOUT arc closed — no in-cloud READOUT candidate remains pending for
  them. The next READOUT work is a NEW signal's arc or a per-segment leaderboard summary once the [LOCAL]
  calibration population grows.

<!-- DONE 2026-07-29T04:1xZ (Cycle 74, COVERAGE, direct-to-main, tests-only/score-neutral): the
     offering-relative BATTERY-INSTANTIATION layer (`battery.instantiate_battery`, the operator directive's
     core task-selection deliverable) is now pinned END-TO-END on the REAL committed fixtures. New
     `tests/test_battery_instantiate_canonical.py` (6 tests) replays each committed fixture through
     `from_fixture → discover_offering → instantiate_battery` and pins the TASK SET per storefront type:
     image-gen API pair → [metered_api,subscription,digital_good] (NO physical/booking/data task; digital_good
     intent parameterized to "generated image" from real media evidence, NOT the "digital output" fallback);
     retail books.toscrape → ONLY physical_good; machine-surface api.replicate.com → ONLY metered_api;
     example.com → empty battery. Plus cross-site comparability (metered_api intent identical across
     driftflight.com vs api.replicate.com). Converts the operator acceptance criterion at the INSTANTIATION
     layer from synthetic-only (test_battery_instantiate) + transient [LOCAL] run logs into an in-cloud
     per-cycle tripwire — the same move Cycle 27 made for the DISCOVERY layer. Tests-only, git diff -- asrs/
     rubric/ EMPTY → rubric v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4. Suite 21→22 files. See LOG
     Cycle 74. This further discharges the operator directive's "[LOCAL] acceptance rerun" verification for
     the task-selection layer (the BEHAVIORAL half remains [LOCAL], but the STRUCTURE is now guarded in-cloud). -->

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
  FIRST DATASET SHIPPED 2026-07-28T23:57Z (local fire, TRUTH, direct-to-main, score-neutral).
  `experiments/calibration_sweep.py` runs the shipped static path (`_run_probes → scoring.score`,
  no `--behavioral`, so $0 / no free-tier probe / invariant #1 by construction) across a curated
  14-domain population spanning the spectrum (api-storefront anchors / api-services /
  retail:emerging-rails / retail:no-rails / non-storefront controls). 13/14 scored on rubric v0.7,
  rei.com NOT SCORABLE (env-blocked — reachability, not a site FAIL, invariant #4). Anchors reproduce
  the pinned baseline EXACTLY (driftflight.com 85.5 B / drift-flight.org 46.1 F = live replay-guard
  corroboration); leaderboard tops at the rails anchor 85.5, top real agent-native exa.ai 78.1 C,
  emerging-rails retail D-band (deathwishcoffee 65.8 / warbyparker 64.2 / allbirds 61.9), no-rails floor
  moleskine 49.8 / drift-flight.org 46.1 above the non-storefront controls (wikipedia 41.1 / example
  22.5). Vendor-neutral (uniform probes; `segment` is read-only context). Evidence:
  `runs/local/calibration_sweep_20260728T234815Z.json`. See LOG (Local cycle — 20260728T235720Z). The
  GROW-the-population + re-run-on-a-cadence half is the new [LOCAL] P0 above; the "+ leaderboard page"
  half is the cloud READOUT follow-up below.
<!-- DONE 2026-07-29T06:1xZ (Cycle 76, READOUT, branch+PR#8+self-merge 62e7b43, display-only/score-neutral):
     "Calibration leaderboard READOUT page" SHIPPED (the HTML half). `asrs/scorecard.py`
     `_write_calibration_page(out_dir, sweep=None)` + `_load_calibration_sweep()` render the newest
     committed `runs/local/calibration_sweep_*.json` as a ranked `calibration.html`, published next to
     every card + footer-linked. Scored members rank by overall DESC (order RE-DERIVED from raw rows), with
     grade/overall/all-5-pillars (outcome `—`, never a scored 0)/vendor-neutral claimed archetypes.
     NOT-SCORABLE members named in a SEPARATE section, NO rank, framed reachability-not-failure (invariant
     #4). Grade bands LIVE from load_rubric (no-drift); a dataset on a different rubric version is flagged.
     Vendor-neutral (domains as DATA, same scanner-scope as canonical-history; wording scanner 4/4). Display-
     only: git diff = scorecard.py + test_readout.py only; scoring/offering/battery/probe untouched → rubric
     v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4, offering guard 13/13. test_readout 40→45; suite 22
     files green. Renders calibration_sweep_20260728T234815Z.json (13 scored / 1 not-scorable). See LOG
     Cycle 76. TERMINAL leaderboard readout (the "/terminal" half of the original item) not built — the HTML
     page is the higher-leverage surface; a `python -m asrs calibration` terminal command is a small
     cloud-doable READOUT follow-up if wanted. A per-segment summary block is a natural next increment once
     the population grows (kept with the GROW-population [LOCAL] P0). -->
- **Calibration leaderboard — terminal readout + per-segment summary** (READOUT, cloud-doable follow-ups to
  Cycle 76's `calibration.html`). Two small optional increments: (a) a `python -m asrs calibration` terminal
  command rendering the same newest committed sweep as a text leaderboard (mirrors the
  `canonical-history` terminal/HTML pairing); (b) a per-segment roll-up on the HTML page (median/spread of
  overall within each `segment`) so the reader sees the rails-anchor vs no-rails-retail vs control bands as
  aggregates, not just a flat ranking — most valuable once the population passes ~15 members. Both display-
  only, off the scoring path; render off `_load_calibration_sweep()`.
- **[LOCAL] Offering-classifier precision — the exa.ai over-claim** (COVERAGE/METHOD, observation from
  the 23:57Z sweep). `discover_offering` classified exa.ai (a search/retrieval API) as claiming ALL SIX
  archetypes incl. physical_good + service_booking, from its rich docs. Diagnostic-only (offering feeds no
  score — the sweep row is unaffected), but a false-positive worth a precision pass: the physical_good /
  service_booking signals likely over-trigger on marketing prose. Design a tighter guard (as the
  metaphorical-"ship" physical_good guard already does for the canonical pair), verify on 2+ real domains,
  keep it off the scoring path. Not urgent (score-neutral); catch it before the population grows.
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
  storefront/fixture as they land. PROGRESS 2026-07-28T03:20Z (Cycle 49, METHOD): the benchmark's
  POPULATION ORDERING is now an executable calibration control — `tests/test_canonical_replay.py` +2
  (14→16). Guard 12 pins the overall STRICTLY decreasing down the agent-native-commerce spectrum
  (with-rails API 85.5 > no-rails API 46.1 > human-only retail 29.5 > zero-commerce 22.5), read from
  the LIVE pipeline not the pinned constants (so a re-capture to buggy reordered numbers fails HERE
  even after the exact-number expectations are updated to match); guard 13 proves the order is NOT a
  transactability artifact (the two payment-floor sites tie at 0 tx yet the tail order is preserved by
  legibility). Non-vacuous (reversed-spectrum negative control fails). First cross-domain ordering
  property in the repo. PROGRESS 2026-07-28T07:1xZ (Cycle 53, METHOD): the JOINT population-level
  relabel-invariance guard SHIPPED — `tests/test_canonical_replay.py` +1 (16→17), guard 14
  `test_population_ordering_is_identity_invariant`. Relabels ALL FOUR fixtures simultaneously to DISTINCT
  neutral hosts and asserts the strict monotone capability ordering (guard 12) survives AND each relabeled
  overall equals its pinned value — the ORDERING, not just per-domain scores, is identity-invariant.
  Non-vacuous BEYOND the per-domain guards: the four hosts differ only in leading letter, assigned
  REVERSE-lexical to capability (top→`zeutral-storefront.test`, floor→`aeutral-storefront.test`), so a
  host-string sorter would reverse the population and fail here while every single-host per-domain guard
  passes; the reverse-lexical + distinct + no-canonical-name conditions are themselves asserted executable.
  First CROSS-DOMAIN identity-invariance property. Tests-only, score-neutral (git diff -- asrs/ rubric/
  EMPTY; rubric v0.7, replay guard 17/17 / +39.4, offering guard 12/12); suite 211→212.
  PROGRESS 2026-07-28T11:1xZ (Cycle 57, METHOD): the SECOND Cycle-53 candidate — guard 14's COMMITTED
  NEGATIVE CONTROL — SHIPPED. `tests/test_canonical_replay.py` +1 (18→19), guard 16
  `test_population_relabel_negative_control` monkeypatches the "sort the domains alphabetically and assign
  tiers" bug into `scoring.score` (overall keyed on the host's ASCENDING lexical rank, not the evidence);
  because guard 14 assigns the neutral hosts reverse-lexical to capability, the rig REVERSES the population,
  so guard 14's own strict-decreasing ordering check FAILS on it (proven by contrast: guard 14 passes on the
  real scorer). Brings the invariance-guard family to UNIFORM rigor — every guard (15(d) pillar inversion,
  offering-layer identity special-case, Cycle-29/33 wording injections, now guard 14) carries a committed
  injection proving it catches the anti-pattern it names, not just a construction argument. Restored in a
  finally + restore-assertion so the rig never leaks. Tests-only, score-neutral (git diff -- asrs/ rubric/
  EMPTY; rubric v0.7, replay guard 19/19 / +39.4); suite 216→217.
  The FIRST Cycle-53 candidate (joint per-check STATUS identity-invariance) is DE-PRIORITIZED as largely
  redundant: `_score_relabeled` scores each fixture INDEPENDENTLY (own temp file + own FetchContext, no
  cross-fixture state), so a "joint" per-check-status assertion equals the per-domain per-check-status the
  relabel guards 4/6/8/11 (`_assert_relabel_invariant`) already assert one host at a time — the joint form
  adds no NEW coverage over the scoring path. Not worth a cycle unless the scoring path ever gains
  cross-domain state.
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

- **[METHOD, cloud-doable] Audit the test-runner registration lists for authored-but-unregistered
  guards** (observation, Cycle 84). The in-cloud suites run via each `tests/test_*.py`'s own `main()`
  test LIST (no pytest auto-discovery — `local_verify.py` invokes `python tests/test_X.py`). Cycle 84
  found `test_methodology_documents_payment_rail_neutrality` (authored Cycle 80) was never added to
  test_readout's `main()` list, so it silently never ran for four cycles — the "silent success/failure
  look identical" failure mode. Fixed for that guard. Sweep the other suites: for each `test_*.py`,
  diff the set of `def test_*` functions against the names in its `main()` list and register any orphans
  (or add a tiny meta-guard that asserts the two sets match, so a future orphan fails loudly). Tests-only,
  off the scoring path.

- **[CANDIDATE, READOUT] Card-level "behaviorally corroborated" calibration badge** (follow-up to
  Cycle 68). Cycle 68 documented the static-vs-behavioral VALIDITY property in methodology-page
  PROSE (§8). The terminal→JSON→HTML surface it doesn't yet reach is the CARD: a payment-capable
  storefront whose static transactability prediction is behaviorally confirmed (Outcome payment
  checkpoints PASS across trials) could carry a small "behaviorally corroborated" affordance next to
  the transactability pill — the same terminal→JSON→HTML closure per_kind (Cycle 10→12),
  between_kind_spread (18→20), and NA (25→28) each took. Display-only/score-neutral when done.
  NOW UNBLOCKED (2026-07-29): the SECOND committed behavioral report landed — the no-rails retail negative
  anchor (moleskine, committed 2026-07-28T23:10Z) is now wired into the two-sided calibration guard
  (Cycle 71) AND surfaced in §8 prose (Cycle 72). The badge can therefore render BOTH the positive
  corroboration (with-rails: payment checkpoints PASS) AND its honest ABSENCE (no-rails: predicted no
  payment, live wall confirmed — no corroboration to show), so it no longer over-claims. Remaining work is
  the report-shape decision + the terminal→JSON→HTML closure; a strong future READOUT pick.

<!-- DONE 2026-07-28T16:21Z (Cycle 62, COVERAGE, direct-to-main, score-neutral):
     "[CANDIDATE] Offering discovery should read the /docs API-docs surface" SHIPPED. `/docs`
     (+`/api-docs`, `/reference`) added to `asrs/offering._SURFACE_DOCS`; `classify_offering` now
     HTML-strips ANY HTML-document surface (new `_is_html_document` detector on the `<!doctype html>`/
     `<html` prologue), not only the homepage — load-bearing because a real docs page's `<script>`/
     `<style>` retail decoys ("out of stock"/"shopping cart") scanned RAW would false-positive
     physical_good. VERIFIED on the committed pair: claimed SET+ORDER unchanged on BOTH domains
     (`[metered_api, digital_good, subscription]` via full discover_offering incl. doc subdomains), so
     the canonical OFFERING guard EXPECTED needed NO re-derivation (12/12 unchanged). Off the scoring
     path (grep-verified) → rubric v0.7, replay guard 21/21 / +39.4 / 0 replay-miss, scoring path
     byte-for-byte untouched. `test_offering.py` 18→20 (synthetic /docs-only non-vacuous-on-strip +
     end-to-end live-read on the canonical fixture); wiring guard extended; stale Cycle-58 comment fixed.
     Commit f9459a8. See LOG Cycle 62. -->
<!-- DONE 2026-07-28T20:1xZ (Cycle 66, COVERAGE, direct-to-main, score-neutral): "Further
     metered/subscription billing conventions" SHIPPED. `asrs/offering._SIGNALS` gains
     `tiered-volume` (metered_api: committed-use / volume|usage|pricing tiers / per-tier price) and
     `seat-licensing` (subscription: per-seat / per-user recurring pricing). Precision-first exactly as
     the item asked: `volume`/`tier` anchored to a pricing word ("volume control" / "tier 1 support" /
     "committed **to** use" never fire); `seat` anchored to a period/price/per-user/licensing word (a
     window seat, a seat belt, "8 seats at the table" never fire). VALIDATED: `tiered-volume` fires on
     the pair (real captured "never counted against **volume tiers**" on driftflight.com homepage) but
     only DEEPENS metered_api — already the strongest claim → canonical OFFERING guard 12/12 UNCHANGED,
     SET+ORDER `{metered_api,subscription,digital_good}` did NOT reorder (did not overtake, as the item
     flagged to check); `seat-licensing` does not fire on the pair. Off the scoring path (grep-verified;
     scoring probe's `protocols._AGENT_SURFACE_DOCS` untouched) → rubric v0.7, replay guard 24/24 / +39.4
     / 0 replay-miss, scoring path byte-for-byte untouched. `test_offering.py` 20→23 (+tiered-volume
     precision battery 9 pos/6 neg, +tiered-volume real-captured on the fixture, +seat-licensing precision
     battery 7 pos/6 neg); suite 231→234. See LOG Cycle 66. FOLLOW-UP below (seat real-data leg). -->
- **[LOCAL / CANDIDATE, COVERAGE] Real-data non-vacuity leg for `seat-licensing`** (follow-up to Cycle 66).
  `tiered-volume` earned a real-captured non-vacuity test (fires on the committed driftflight.com
  homepage's "volume tiers" prose), but `seat-licensing` shipped with the SYNTHETIC precision battery
  ONLY — no committed fixture carries seat/per-user licensing prose. When a seat-priced SaaS storefront
  is captured (a real per-seat plan, e.g. via `asrs.cli score <domain> --record-fixture
  fixtures/canonical/<domain>.json` [LOCAL]), add a real-captured test mirroring
  `test_tiered_volume_fires_on_real_captured_billing_prose`. Low urgency; the synthetic battery already
  pins precision on the named traps.

<!-- DONE 2026-07-28T14:2xZ (Cycle 60, READOUT, direct-to-main, display-only, score-neutral):
     "[READOUT — surface the whole-chain weight-robustness finding on the methodology page]" SHIPPED,
     completing the follow-up to Cycle 59 (TRUTH half was guard 17, below). The methodology §3
     "But couldn't you re-weight the pillars…" sub-section stated only the PAIR result (Cycle 56);
     `asrs/scorecard._write_methodology_page` gains one paragraph extending it to the POPULATION —
     when the whole population is a TOTAL DOMINANCE CHAIN (each rung ≥ next on every applicable pillar,
     strict on ≥1, over the same uncapped set) no non-negative reweighting inverts ANY rung, so the
     whole ranking (not just the head delta) is weight-robust; stated test-pinned "over the reference
     spectrum" so guard 17 + readout stay in lockstep. Vendor-neutral (four tiers by capability, no
     domain named — enforced by the test's drift-flight/driftflight-not-in-text assertions +
     test_readout_wording 4/4). Display-only: git diff = scorecard.py + test_readout.py ONLY;
     scoring/rubric/probes/offering/battery untouched → rubric v0.7, replay guard 20/20 / +39.4 / 0
     replay-miss. `test_readout.py` `test_methodology_documents_weight_robustness` +4 assertions (38/38);
     suite 220→221. See LOG Cycle 60. -->
  <!-- TRUTH HALF DONE 2026-07-28T13:2xZ (Cycle 59, TRUTH, direct-to-main, tests-only, score-neutral):
       "Population-wide WEIGHT-ROBUSTNESS" SHIPPED as `tests/test_canonical_replay.py` guard 17
       `test_population_ordering_is_weight_robust` (19→20). Confirmed EMPIRICALLY the Cycle-55 next-
       hypothesis: pillar-wise dominance holds down the WHOLE capability spectrum — com⪰org (strict
       leg,tx), org⪰retail (strict leg,tx,trust), retail⪰bare (strict leg,trust), a TOTAL dominance
       chain over an identical uncapped applicable-pillar set ({access,legibility,transactability,trust},
       outcome None on all four). So the entire population ordering (guard 12) is weight-robust: chain
       non-increasing under EVERY non-negative weighting (rubric/uniform/each unit-basis incl. the
       all-access extreme where each rung's gap→0 but never inverts), strict where the weighting touches
       a strict pillar. HONEST FINDING: the a-priori suspect org-vs-retail on trust is DOMINATED (org 60
       > retail 33.3), NOT weight-dependent → no rung is merely weight-dependently ordered (the guard's
       (a) assertion would have surfaced it if one were). Faithfulness leg pins the rubric weights
       reproduce all four overalls (85.5/46.1/29.5/22.5); (d) non-vacuous negative control (access-
       inverted floor site tops retail under all-access). git diff -- asrs/ rubric/ EMPTY → rubric v0.7,
       replay guard 20/20 / +39.4 / 0 replay-miss. Suite 219→220. See LOG Cycle 59. -->
<!-- DONE 2026-07-28T17:1xZ (Cycle 63, TRUTH, direct-to-main, tests-only, score-neutral):
     "Population-wide observability / like-for-like at the CHECK layer" SHIPPED as
     `tests/test_canonical_replay.py` guard 19 `test_population_delta_is_earned_at_the_check_layer`
     + guard 20 its committed negative control (21→23). Lifts guard 8's per-CHECK earned-dominance
     argument from the PAIR to the four-domain population from the LIVE pipeline: (a) identical
     scored 14-check set on all four (population like-for-like — the "watch the tail, may need
     per-rung scoped intersection" caveat resolved by MEASUREMENT: the sets are in fact identical,
     no intersection needed); (b) honest tail-favouring observability — head fully observed, tail
     each excuse exactly one absent check (self_serve_payg CANT_TEST, never mis-scored FAIL, no NA
     anywhere), which can only RAISE the tail's score yet the ordering holds → no head-inflating
     observability artifact; (c) LOAD-BEARING FINDING — the population is NOT a clean check-by-check
     superset chain like the pair: com>org & retail>bare are clean supersets but org>retail carries
     EXACTLY ONE honest inversion, https_hsts (trust, retail HTTPS > no-rails API HTTPS), ABSORBED
     by the trust pillar (60.0 > 33.3) so it never flips the ordering — surfaced honestly, not forced
     into a total-superset claim. Complements guard 17 (pillar-wise TOTAL dominance): dominance is a
     PILLAR property; at the check layer that rung is a majority. Guard 20 catches a mis-attribution
     (tail CANT_TEST→FAIL) rig. Score-neutral (git diff -- asrs/ rubric/ EMPTY; rubric v0.7, replay
     guard 23/23 / +39.4 / 0 replay-miss); suite 223→225. See LOG Cycle 63. FOLLOW-ONS: the READOUT of
     the honest check-layer refinement on the methodology page is DONE (Cycle 64, direct-to-main,
     display-only: `_write_methodology_page` gains the pillar-layer-vs-per-check paragraph naming the one
     absorbed https_hsts minority reversal in capability terms; test_readout.py 38→39
     test_methodology_documents_check_layer_honesty; scoring untouched, rubric v0.7, replay 23/23 / +39.4;
     commit 6bb6ef3; see LOG Cycle 64). REMAINING follow-on: extend guard 19 to the 5th committed fixture
     (api.replicate.com) once its tier + expected statuses are pinned. -->
- **[CANDIDATE, TRUTH] Extend guard 19 (population check-layer earned-dominance) to `api.replicate.com`**
  — a 5th real fixture (`fixtures/canonical/api.replicate.com.json`) is already committed but not in the
  capability-spectrum guards (12/17/19). Pin its capability tier + expected per-check statuses (a real
  agent-native / metered API storefront), slot it into `_CAPABILITY_SPECTRUM`, and re-derive guard 19's
  per-rung inversion sets. Adds a SECOND API-storefront data point to the population, strengthening the
  ordering + earned-dominance claims beyond the single synthetic canonical pair. Cloud-doable from the
  committed fixture; tests-only, score-neutral — but verify its overall/pillars/statuses live first
  (the fixture may not yet have a pinned EXPECTED entry).

- **[CANDIDATE, METHOD] Exercise the `caps_applied` arrival-order path directly** (reproducibility,
  follow-up to Cycle 65's guard 20). Guard 20 pins that `scoring.score` is invariant to check-INPUT
  order over the full scored surface, but its caps leg is LATENT: no grade cap binds on any committed
  domain (the weight-robust guard's precondition A confirms `not com.caps_applied and not org.caps_applied`),
  so `caps_applied` — which `scoring.score` builds in check-ARRIVAL order — is empty everywhere and its
  order-sensitivity is never actually driven. Build a small synthetic fixture (or a unit test feeding a
  hand-built `CheckResult` list) whose rubric forces TWO caps to bind, then assert `caps_applied` is a
  SET-equal (not order-sensitive) output under a reversed input. Cloud-doable, tests-only, score-neutral;
  low urgency (caps don't bind on any committed domain today, so this is latent-not-live).

<!-- DONE 2026-07-28T06:1xZ (Cycle 52, READOUT, direct-to-main, display-only, score-neutral):
     "Live-signal FRESHNESS banner on canonical-history.html" SHIPPED. `asrs/scorecard.py`
     `_write_canonical_history_page` renders a liveness element off `hist.liveness` (the Cycle-51
     `Liveness`): a prominent STALE warning CARD above the latest-reading card when the newest
     re-score is past the 6h floor (runner-down warning + "OLD crawl, not the pair now"), a quiet
     age note when FRESH. Live build path loads WITH the wall clock (mirroring
     `cli._cmd_canonical_history`); clock-free summary → liveness None → no banner (honest-None).
     Closes the last terminal-only gap for the freshness signal (same terminal→HTML deferral
     per_kind Cycle 10→12 / noise floor 47→48 took). Display-only: git diff = scorecard.py +
     test_readout.py only; scoring/rubric/probes/offering/canonical_history.py untouched → rubric
     v0.7, replay guard 16/16 (46.1 F / 85.5 B / +39.4), offering guard 12/12. Demonstrated
     end-to-end on the REAL committed series (STALE banner "7.6h old" while verdict In-band).
     `test_readout.py` 34→37; suite 208→211. See LOG Cycle 52. -->

- **`_score_relabeled` host-sensitivity: whole-fixture substitution trips a spurious replay-miss on
  a shorter/extra-hyphen neutral host** (METHOD/test-hygiene, surfaced Cycle 53 — LOW urgency, not a
  scoring bug). `tests/test_canonical_replay._score_relabeled` does a naive `raw.replace(domain, new_host)`
  over the whole fixture. On the `driftflight.com` fixture this rewrites the recorded
  `api.driftflight.com/openapi.json` SUBDOMAIN-surface reference; a probe then reconstructs a fetch whose
  URL only stays in-cache when the new host is (empirically) as long as the original AND has the same hyphen
  count — a shorter or extra-hyphen host produces `https://<host>/api.<host>/openapi.json`, an un-recorded
  fetch → a replay-miss ARTIFACT of the relabel. It does NOT move the score (85.5 in every case — the
  OpenAPI subdomain surface is unscored), but it trips the file's "no replay-miss" convention, so guard 14
  (and any future relabel) must hand-pick neutral hosts derived from the known-good `neutral-storefront.test`.
  Cloud-doable hardening idea: make `_score_relabeled` substitute ONLY the host in the recorded request KEYS
  and response `final_url`/URL fields (a structured relabel keyed on the fixture's URL schema), not a blind
  whole-string `.replace`, so ANY neutral host relabels byte-clean and the host-length/hyphen constraint
  disappears. Then guard 4/6/8/11/14 could use arbitrary neutral hosts and the reverse-lexical assignment
  wouldn't need the length caveat. Test-helper only (no `asrs/` change) → direct-to-main when done; verify
  all existing relabel guards stay green + 0 replay-miss across a range of host lengths.
<!-- DONE 2026-07-28T08:1xZ (Cycle 54, COVERAGE, direct-to-main, score-neutral): "Offering discovery
     reads conventional DOC SUBDOMANS" SHIPPED. `asrs/offering.py` `discover_offering` now reads each
     `_SURFACE_DOCS` surface on the apex host AND on a small allowlist of same-registrable-host doc
     subdomains `agents.`/`docs.`/`developers.`/`api.` (new `_DOC_SUBDOMAINS` +
     `_doc_subdomain_surfaces(base_url)`). PRECISION-FIRST/SSRF-safe exactly as scoped: subdomains built
     from the site's OWN resolved host (never a fetched `url`), `www.` dropped to attach to the
     registrable host, no self-stacking (`api.replicate.com` → no `api.api.*`), host-qualified surface
     labels so subdomain surfaces don't overwrite apex paths, a non-resolving/404 subdomain simply absent.
     The P2 prediction held: on driftflight.com the subdomain `agents.driftflight.com/llms-full.txt` is now
     READ (credit-metered signal reaches the DISCOVERED metered_api claim) but the claimed SET is UNCHANGED
     `{metered_api,subscription,digital_good}` (subdomain surfaces on both canonical domains carry only
     those three archetypes' signals) — so the canonical OFFERING guard stays 12/12 with NO EXPECTED update
     needed, and the fixture base-host routing resolved as noted (`FetchContext.from_fixture` served the
     recorded `agents.driftflight.com`/`api.driftflight.com` entries). Score-neutral (off the scoring path;
     `git diff -- asrs/scoring.py asrs/probes/ asrs/fetch.py rubric/` EMPTY; rubric v0.7, replay guard 17/17
     / +39.4). `test_offering.py` 14→16 (+helper precision/SSRF unit test, +live-read non-vacuity test on the
     committed fixture); suite 212→214. See LOG Cycle 54. Follow-up candidate (TRUTH): a canonical OFFERING
     guard asserting the subdomain surface is read on the pair (mirror of the new live-read test). -->

- **Per-side noise floor: verify it stays SILENT under a real transient** (TRUTH, Cycle-47
  follow-up — PARKED until a fresh OOB stretch lands). Cycle 47 added
  `NoiseFloor.no_rails_stddev`/`with_rails_stddev` + `sides_deterministic`, proving on the committed
  series that each reference storefront reproduces its pinned overall EXACTLY at rest (σ=0), so the
  deterministic delta is genuine per-side determinism, not two lock-step drifts cancelling. By
  construction an out-of-band reading is EXCLUDED from the in-band set, so a genuine site transient can
  never inflate the at-rest per-side σ — but the existing 07-27 transient already recovered, so a test
  asserting "per-side σ stays 0 even while an OOB reading is present in the series" is vacuous on the
  current series. When the live series next carries an OOB stretch alongside in-band readings, add a
  real-series case pinning that the per-side floor is measured only over the in-band subset (a transient
  is signal excluded from the floor, not noise inflating it). No new code — a test + a fresh artifact.

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
  OPTIONAL): the methodology page now carries the earned-dominance worked example AND (Cycle 56)
  a weight-robustness sub-section (§3, both answering "is this delta rigged?" — observation half +
  aggregation-weights half). A small next unit would anchor-link a compared-pair card's overview (or
  the delta shown on a `compare` card) to that methodology section, so a reader looking at a large
  delta can jump straight to "why this delta is earned, not a blind spot, and not a weight artifact".
  No scoring semantics; direct-to-main.
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
<!-- DONE 2026-07-28T02:2xZ (Cycle 48, READOUT, direct-to-main, display-only, score-neutral):
     "Noise-floor on canonical-history.html" SHIPPED — and extended to the Cycle-47 PER-SIDE
     determinism finding, closing the LAST terminal→HTML gap on that surface.
     `scorecard._write_canonical_history_page` gains an "Is the band real noise, or transient
     absorption?" card (between the trend chart and the diagnosis card), driven off
     `hist.noise_floor`: reports n_in_band / σ / worst|div|, the DETERMINISTIC-at-rest verdict,
     and — ONLY when `sides_deterministic` — the strictly-stronger per-side sentence (both
     reference storefronts reproduce their pinned overall exactly at rest → genuine per-side
     determinism, not two lock-step drifts cancelling). Delta-deterministic-but-sides-not (the
     cancellation Cycle 47 guards) shows the delta verdict and WITHHOLDS the per-side claim;
     non-deterministic → well-separated/too-tight band read; <2 in-band → card SILENT (honest).
     Wording copied verbatim from the terminal `render`. Rendered on the REAL committed 72-point
     series (68 in-band, σ=0.00, both sides exact). git diff = scorecard.py + test_readout.py ONLY
     → rubric v0.7, replay guard 14/14 / +39.4, readout/rubric-wording 4/4 each. test_readout.py
     31→34 (per-side strong claim; NON-VACUOUS lock-step cancellation control; card-absent-<2-in-band);
     suite 195→198. See LOG Cycle 48. REMAINING noise-floor follow-ups distinct: the drifting/diverged
     cutoff calibration (below) + the per-side-silent-under-transient guard (P2, parked). -->
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
