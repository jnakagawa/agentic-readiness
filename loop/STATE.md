# Loop state

- Cycle counter: 45
- Started: 2026-07-23 (UTC)
- Focus pointer: COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT)
  (Cycle 1 METHOD, Cycle 2 COVERAGE, Cycle 3 TRUTH, Cycle 4 READOUT,
  Cycle 5 METHOD, Cycle 6 COVERAGE, Cycle 7 TRUTH, Cycle 8 READOUT,
  Cycle 9 METHOD, Cycle 10 COVERAGE, Cycle 11 TRUTH (cloud: trial-count panel
  pinning) + local fire 11:42Z TRUTH (codex reachability investigation, ran
  concurrently), Cycle 12 READOUT (task-battery card on the HTML scorecard),
  Cycle 13 METHOD (coverage-warning noise fixed at source — logging + behavioral-only
  classifier; unblocks the local runner's re-score capture),
  Cycle 14 COVERAGE (commerce-protocol ACP/UCP credit requires a validated manifest —
  peer-gated PR #3, rubric v0.6→v0.7),
  Cycle 15 TRUTH (FetchContext record/replay — `save_fixture`/`from_fixture` + a `replay`
  mode, the offline in-cloud proxy for the network-blocked canonical re-score; first duty
  = post-merge sanity check of v0.7/PR #3 → RETAIN); next cycle takes READOUT.
  Local fire 2026-07-23T15:43Z TRUTH (complementary to cloud Cycle 15): ran the NETWORKED
  half cloud Cycle 15 could not — the LIVE post-merge canonical re-score on v0.7
  (46.1 F / 85.5 B, +39.4 unchanged) — and reconciled the stale "PR #3 Open" bookkeeping.
  No open peer-gated PR remains.
  Cycle 16 READOUT (methodology page — the "read the paper" doc behind the rubric page;
  weights/caps/bands pulled live from load_rubric so it can't drift; display-only, rubric
  stays v0.7, canonical delta unchanged by construction; direct to main. First cycle after
  16:00 UTC → daily digest DM sent); next cycle takes METHOD.
  Local fire 2026-07-23T16:46Z TRUTH (the networked half of the canonical-replay guard):
  executed the top P0 [LOCAL] — captured `fixtures/canonical/{drift-flight.org,driftflight.com}.json`
  via a new dormant `--record-fixture` hook on `asrs.cli score` (also discharges the P1 CLI-hook
  item). Live crawl 46.1 F / 85.5 B on v0.7; OFFLINE replay through the real probe path
  reproduces 46.1 / 85.5 / +39.4 EXACTLY with 0 replay-miss on both. One cloud step left:
  `tests/test_canonical_replay.py`.
  Cycle 17 METHOD (canonical replay guard COMPLETED — the network-blocked per-cycle re-score is
  now EXECUTABLE in-cloud): `tests/test_canonical_replay.py` (3 tests) replays each committed
  canonical fixture through `from_fixture → _run_probes → scoring.score` and asserts overall
  (46.1/85.5), grade (F/B), rubric_version "0.7", scored, all five pillar_scores, delta +39.4,
  AND no replay-miss. Converts 16 cycles of "delta unchanged by construction" PROSE into a
  tripwire. Tests-only, scoring path byte-for-byte untouched, rubric stays v0.7, canonical delta
  unchanged; direct-to-main. Suite 85 → 88. No Slack (not sensitive, moves no score, digest
  already sent Cycle 16). First duty: no open peer-gated PR (verified []). Next cycle takes
  COVERAGE. NOTE: `test_free_tier.py` needs optional `eth-account` (fresh cloud checkout lacks
  it → 7/8; `pip install eth-account` → 8/8) — a missing-dependency ENV gap (invariant #4),
  pre-existing and unrelated to this change.
  Cycle 18 COVERAGE (storefront-TYPE specialization signal for the task battery):
  `BatterySummary.between_kind_spread` (`asrs/battery.py` `_between_kind_spread`) = population
  stddev of the per-kind `mean_completion` across signal archetypes. Decomposes the battery-wide
  `cross_task_spread` into WITHIN-type noise (existing `per_kind[].cross_task_spread` = reliability)
  vs BETWEEN-type specialization (this = "does readiness depend on which storefront TYPE"), the
  north-star many-storefront-types axis. None when <2 archetypes have signal (between-type variance
  is unobservable with one type observed → honest None, not a measured-uniform 0.0). Terminal line
  `between-archetype spread X.XX — <verdict>` shown only when ≥2 archetypes have signal; JSON via
  asdict; HTML card pill queued P2. Diagnostic-only (battery feeds no score) → rubric stays v0.7,
  scoring.py/rubric byte-for-byte untouched, canonical delta unchanged by construction AND measured
  (in-cloud replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss); direct-to-main. `test_battery.py`
  8/8 → 9/9; suite 88 → 89. No Slack (diagnostic, moves no score, digest already sent Cycle 16, not
  a new digest window at 18:18Z). First duty: no open peer-gated PR (verified []). Next cycle takes
  TRUTH.
  Cycle 19 TRUTH (canonical replay guard now defends the delta IN CAPABILITY TERMS):
  `tests/test_canonical_replay.py` +1 test (`test_canonical_delta_is_agent_native_payment`, 3/3→4/4)
  replays both committed fixtures and asserts the CAPABILITY FACTS behind +39.4 — with-rails
  driftflight.com delivers agent-native payment (`x402_probe` PASS, `self_serve_payg` x402_live=True),
  no-rails drift-flight.org does not (`x402_probe` not-PASS, x402_live=False), transactability gap
  exactly 68.75. Converts the playbook's per-cycle "explain the delta in capability terms" from LOG
  prose into an executable tripwire; agent-native payment is the single largest delta driver
  (transactability weight 0.30 → ~25.8 of 39.4 weighted pts, ~65%). Worded by capability, never by
  vendor. Tests-only, scoring.py/rubric/probes byte-for-byte untouched, rubric stays v0.7, canonical
  delta unchanged by construction AND re-measured (46.1 F / 85.5 B / +39.4, 0 replay-miss);
  direct-to-main. Suite 89 → 90. No Slack (tests-only, moves no score, not a digest window at 19:12Z).
  First duty: no open peer-gated PR (verified []); infra health check ran first — RUNNER RECOVERED
  (see runner-health note below). Next cycle takes READOUT.
  Cycle 20 READOUT (storefront-TYPE specialization on the HTML card — the between-archetype pill):
  `scorecard._battery` now renders `between_kind_spread` (shipped terminal+JSON Cycle 18) as a second
  header pill (`_battery_between_band`: Generalist <0.15 / Somewhat type-dependent <0.35 /
  Type-specialized ≥0.35, css good/warn/bad — thresholds/wording copied from the terminal
  `report._battery_lines`) + a one-line interpretation under the by-archetype sub-block. Both render
  ONLY when between_kind_spread is non-None (≥2 signal archetypes) → the honest-None single-type case
  shows no pill, mirroring the aggregation. Closes the last terminal→JSON→HTML gap for the battery
  diagnostics (same deferral `per_kind` took, Cycle 10→12). Display-only: scoring.py/rubric/probes/
  battery.py byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by construction
  AND re-measured (in-cloud replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss); direct-to-main.
  `test_readout.py` 15/15 → 16/16 (+1 between-kind pill test, single-kind test extended to assert no
  pill on honest-None); suite 90 → 91. No Slack (display-only, moves no score, digest already sent
  Cycle 16, not a new digest window at 20:12Z). First duty: no open peer-gated PR (verified []); infra
  health check ran first — runner HEALTHY (newest verify_20260723T194101Z, 19:41Z, ~31 min old).
  Next cycle takes METHOD.
  Cycle 21 METHOD (VENDOR-NEUTRALITY made executable — domain-relabeling invariance):
  `tests/test_canonical_replay.py` +3 tests (4→7). Each relabels a committed canonical fixture's host
  (request keys AND every response byte — URLs/final_url/headers/bodies, whole-fixture string sub to a
  different-length neutral `.test` host, temp-file copy, no committed fixture touched) and replays through
  the REAL `from_fixture → _run_probes → scoring.score` path, asserting overall/grade/ALL five pillars/
  every check STATUS are IDENTICAL to the un-relabeled run. `test_relabel_invariance_org` (46.1 F),
  `_com` (85.5 B), `test_relabeled_delta_still_39_4` (each side to a distinct anon host → delta still +39.4).
  Converts the "no special-casing any domain, favorable or hostile" invariant from prose into a tripwire
  (same move Cycle 17 made for "delta unchanged", Cycle 19 for "delta in capability terms"): proves the
  +39.4 comes from EVIDENCE, not the storefront's IDENTITY. NON-VACUOUS — negative control: a monkeypatched
  favorable special-case (x402_probe→PASS only when the literal canonical host is cached) is CAUGHT by the
  per-check-status assertion (PASS→FAIL diff), and it slipped the numeric pillar checks in that rig, so the
  status assertion earns its place. Tests-only: scoring.py/rubric/probes/fetch.py byte-for-byte untouched →
  rubric stays v0.7, canonical delta unchanged by construction AND re-measured (in-cloud replay guard
  46.1 F / 85.5 B / +39.4, 0 replay-miss). Direct-to-main. Suite 91 → 94. No Slack (tests-only, moves no
  score, digest already sent Cycle 16, not a new digest window at 21:13Z). First duty: no open peer-gated
  PR (verified []); infra health check ran first — runner HEALTHY (newest verify_20260723T204104Z, 20:41Z,
  ~32 min old). Next cycle takes COVERAGE.
  Cycle 22 METHOD→COVERAGE (free-tier opt-in DISCOVERY broadened to a second convention —
  the URL query parameter): `asrs/behavioral/free_tier.py` `_scan_query_param_instruction`
  (mirrors `_scan_header_instruction`: `[?&]name=value` token, free-context window, plumbing-param
  denylist, requires an explicit "free" hint in name/value → `?plan=pro`/`?tier=starter` near free
  prose rejected) + additive `FreeTierDiscovery.opt_in_query` field + `opt_in_query` evidence key,
  populated by `discover_free_tier`. Recognizes+records that a site advertises its free tier by
  query param (currently mis-discovered as "opt-in-undiscoverable") — north-star many-conventions
  axis. DELIBERATELY SCORE-NEUTRAL: the field is NOT in the `advertised` gate and NOT consumed by
  the live-call path (test-pinned: query-only doc keeps advertised=False; adding `?tier=free` to the
  header fixture leaves advertised identical). NOT signing/payment code — diff confined to the
  discovery region; `parse_challenge`/settle/sign/amount + the nonzero-refusal safety property
  byte-for-byte untouched (sentinel grep clean). No scoring semantics, rubric stays v0.7; canonical
  delta unchanged by construction AND re-measured (in-cloud replay guard 46.1 F / 85.5 B / +39.4,
  0 replay-miss). Direct-to-main. `test_free_tier.py` 8→9 (+query-param discovery test: extraction,
  4 negative controls, evidence surfacing, score-neutrality); suite 94 → 95. No Slack (score-neutral
  additive discovery, moves no score, digest already sent Cycle 16, not a new digest window at 22:12Z).
  First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (newest verify_20260723T214103Z, 21:41Z, ~30 min old). The live wiring (fold opt_in_query into
  `advertised` + the free-mode call) + 2-domain verification is queued [LOCAL] (score-increasing,
  invariant #3); path-based opt-in is the next COVERAGE increment. Next cycle takes TRUTH.
  Cycle 23 TRUTH (canonical delta defended as EARNED — attribution honesty made executable on +39.4):
  `tests/test_canonical_replay.py` +1 test (`test_canonical_delta_is_earned_dominance`, 7→8). Replays
  both committed fixtures through the REAL `from_fixture → _run_probes → scoring.score` path and pins
  three facts from recorded evidence that the aggregate-only guards can't: (a) FULL OBSERVABILITY — no
  static check on either canonical domain is CANT_TEST/NA (clean HTTP-200 crawls) → every FAIL is
  evidence-of-absence scored 0 in the denominator, nothing excused as un-observable; (b) LIKE-FOR-LIKE
  DENOMINATOR — identical scored check_id set on both sides → +39.4 compares the same checks;
  (c) CHECK-BY-CHECK DOMINANCE, NO INVERSION — with-rails capability rank (PASS>PARTIAL>FAIL) ≥ no-rails
  at every matched check, strictly greater at ≥1 (strict wins: llms_txt, offer_catalog, self_serve_payg,
  x402_probe). Proves the delta is a capability SUPERSET at matched/observed checks, not differential
  observability, a masked inversion, or a rounding tie — a THIRD distinct axis complementing Cycle-19
  (capability-payment, one pillar) + Cycle-21 (relabel-invariance, identity). NON-VACUOUS: mis-attributing
  the no-rails `x402_probe` FAIL→CANT_TEST is caught by (a); inverting one check is caught by (c) — both
  slip the number-only guards. Worded by capability, never by vendor. Tests-only:
  scoring.py/rubric/probes/fetch.py byte-for-byte untouched → rubric stays v0.7, canonical delta
  unchanged by construction AND re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss).
  Direct-to-main. Suite 95 → 96. No Slack (tests-only, moves no score, digest already sent Cycle 16, not
  a new digest window at 23:14Z). First duty: no open peer-gated PR (verified []); infra health check ran
  first — runner HEALTHY (newest verify_20260723T224105Z, 22:41Z, ~31 min old). Next cycle takes READOUT.
  Local fire 2026-07-23T23:49Z COVERAGE/METHOD (operator-directive brick 1): shipped `asrs/offering.py`
  — offering RELEVANCE DISCOVERY, the input the offering-relative battery needs. `discover_offering(ctx)`
  reads a storefront's own surfaces ($0 GETs) and `classify_offering` (pure) decides which capability
  ARCHETYPES it CLAIMS to serve (`metered_api/subscription/digital_good/physical_good/service_booking/
  data_retrieval`), each with QUOTED machine evidence; `OfferingProfile.unclaimed` = the NA complement.
  Precision-first + vendor-neutral: the load-bearing guard is that both canonical homepages' metaphorical
  "every image you **ship**" does NOT trip `physical_good` (requires "free shipping"/"add to cart"/"in
  stock"/SKU). Live-validated on 4 real domains (invariant #3): drift-flight.org
  {metered_api,subscription,digital_good} + driftflight.com {metered_api,digital_good,subscription} both
  physical_good=NA (operator acceptance met); example.com {} (null); books.toscrape.com {physical_good}
  (inverse control). Discovery-only/score-neutral — TWO new files only, scoring.py/rubric/probes/battery.py
  byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged (replay guard 46.1 F/85.5 B/+39.4,
  0 replay-miss) AND corroborated by verify_20260723T234102Z. Direct-to-main. `test_offering.py` 7/7; suite
  96 → 103. First duty: no open peer-gated PR (verified []); runner HEALTHY (verify_20260723T234102Z, 23:41Z,
  ~8 min old). Evidence: runs/local/offering_discovery_20260723T234942Z.json. Bricks 2 (intent
  instantiation) + 3 (NA-aware aggregation, PEER-GATED) are the next increments; cloud rotation unaffected.
  Cycle 24 READOUT (earned-dominance property surfaced in the methodology readout — the READOUT
  complement to Cycle-23's TRUTH guard): `methodology.html` section 3 (FAIL vs CANT_TEST) gains a
  "worked example — when is a low score earned evidence, not a blind spot?" sub-section naming the three
  facts that make a two-site delta trustworthy in the SAME capability language as
  `test_canonical_delta_is_earned_dominance` — full observability / like-for-like denominator /
  check-by-check dominance-no-inversion (capability SUPERSET) — and stating the property is pinned by an
  executable regression test (enforced, not asserted). Vendor-neutral by construction: the reference pair
  is described by capability, no domain/product/brand named (test-pinned: `drift-flight`/`driftflight`
  never appear on the page). Closes the Cycle-23 follow-up. `asrs/scorecard.py` (methodology prose +
  minimal h3/ul/li styling in the shared `_PROSE_HEAD`) + `tests/test_readout.py` only; scoring.py/rubric/
  probes/fetch.py/protocols.py/battery.py byte-for-byte untouched (grep clean) → display-only, rubric
  stays v0.7, canonical delta unchanged by construction AND re-measured (replay guard 46.1 F / 85.5 B /
  +39.4, 0 replay-miss). Direct-to-main. `test_readout.py` 16 → 17; suite 103 → 104. No Slack (display-only,
  moves no score, before the next 16:00 UTC digest window). First duty: no open peer-gated PR (verified
  `[]`); infra health check ran first — runner HEALTHY (newest verify_20260723T234102Z, 23:41Z, ~31 min
  old). NOTE: fresh cloud checkout now runs `test_free_tier.py` 9/9 once `pip install -r requirements.txt`
  installs `eth-account` (requirements pins it) — the invariant-#4 env gap noted at Cycle 17 is closed by
  the requirements install. Next cycle takes METHOD.
  Local fire 2026-07-24T00:49Z COVERAGE ([LOCAL] operator directive BRICK 2 — offering-relative intent
  instantiation): shipped `asrs/battery.py` `instantiate_battery(profile)` + a fixed per-archetype intent
  TEMPLATE bank (`_ARCHETYPE_INTENTS`). Turns brick-1 discovery into the battery's TASK SET: one `BatteryTask`
  per CLAIMED archetype (id=kind=archetype, fixed template-bank order for cross-site comparability), omitting
  unclaimed archetypes — so an image API gets metered/subscription/digital intents and NO physical-good task,
  a shop the inverse, a null site an empty battery. Vocabulary reconciled: canonical task vocab is now
  `offering.ARCHETYPES`; generated tasks use archetype names, hand-authored YAMLs keep their free-form `kind`
  labels and still load. Parameterized (not just selected): digital_good `{descriptor}` slot filled from the
  archetype's own vendor-neutral media signals -> "obtain one generated image ..." (operator's literal
  example), translation -> "translated document", else "digital output"; injection-safe (from OUR signal
  labels, never raw site prose). SCORE-NEUTRAL (task selection only; `aggregate_battery`/scoring.py/rubric/
  probes byte-for-byte untouched -> rubric stays v0.7, canonical delta unchanged by construction AND
  re-measured — replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss; corroborated by verify_20260724T004105Z).
  Direct-to-main. `test_battery_instantiate.py` 8/8; suite 104 -> 112. LIVE-validated on 4 real domains
  (invariant #3): both driftflight domains -> NO physical_good task (operator acceptance met),
  books.toscrape.com -> physical_good task (inverse control), example.com -> empty battery; all 4 acceptance
  assertions pass. Evidence: runs/local/offering_battery_instantiate_20260724T004927Z.json. First duty: no
  open peer-gated PR (verified empty); runner HEALTHY (verify_20260724T004105Z, 00:41Z, ~8 min old). Brick 3
  (NA-aware aggregation, PEER-GATED) + the [LOCAL] acceptance rerun are the next increments; cloud rotation
  unaffected (still METHOD).
  Cycle 25 METHOD (operator directive BRICK 3 — NA-aware battery aggregation, PEER-GATED PR #4):
  `aggregate_battery(..., *, profile=OfferingProfile|None)` marks archetypes a site does NOT claim
  (`profile.unclaimed`) NA and EXCLUDES them from `mean_completion`/`cross_task_spread`/`between_kind_spread`
  — the operator's image-API-vs-physical-good complaint made a tripwire. NA (structural not-offered) is DISTINCT
  from no-signal (offered-but-unobserved); both excluded, readout names which (`assessed_archetypes` = what the
  numbers are over, `na_archetypes` = not offered). `BatteryTaskResult.na`; `BatterySummary` +na_archetypes/
  assessed_archetypes/`battery_semantics_version="b1"`; `report._battery_lines` names both (offering-relative
  mode only). WITHOUT a profile the aggregation is byte-for-byte the pre-brick-3 behaviour (backward-compat
  pinned). VERSIONING: bumps the BATTERY-diagnostic semantics version (b1), DELIBERATELY not the rubric version —
  the battery feeds no score, so a rubric bump would falsely signal the scored number moved (flagged in PR for
  reviewer). Vendor-neutral (NA keys on archetype-claim structure, no domain/vendor string; non-canonical kinds
  never NA). scoring.py/rubric/probes/fetch/offering.py byte-for-byte untouched → rubric stays v0.7, canonical
  delta unchanged by construction AND re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss).
  PEER-GATED → branch `loop/na-aware-battery-aggregation`, PR #4 opened with reviewer checklist, NOT self-merged;
  next cycle's first duty reviews+merges. No CI on repo (get_status total_count 0). `test_battery.py` 9→12; suite
  112→115. Slack DM SENT (sensitive-class PR visibility). Infra health check ran first — ALL GREEN (runner
  HEALTHY, verify_20260724T004105Z 00:41Z ~31 min old + clean scores; bench 112/112; ephemeral local-main
  divergence realigned to origin d33129f). Next cycle takes COVERAGE.
  Cycle 26 COVERAGE (operator directive — `--battery auto` run-path wiring, direct to main): first duty
  MERGED peer-gated PR #4 (NA-aware battery aggregation, brick 3) after fresh-context adversarial review —
  all four checklist items re-derived independently (profile=None byte-for-byte pre-brick-3; NA keys only on
  `profile.unclaimed` ⊆ ARCHETYPES so non-canonical kinds never NA, vendor-neutral; replay guard 8/8 delta
  unchanged; battery_semantics_version b1 not rubric); non-vacuous (spread-change >1e-6 pinned); suite 115/115
  on branch → SURVIVED → merge commit bec1dc0. Then the improvement: bricks 1–3 were all on main but nothing
  CALLED them together — `--battery` still loaded a static YAML only. `asrs/cli.py` `_load_battery_arg(args)`
  → `_resolve_battery(args, ctx)` returning `(Battery|None, OfferingProfile|None)`: `--battery auto` runs
  `discover_offering → instantiate_battery` and threads the profile into
  `aggregate_battery(..., profile=)` (NA-aware); `--battery <path>` stays `(battery, None)` (aggregation
  byte-for-byte pre-brick-3); empty offering → empty battery + profile (honest "nothing to assess", every
  archetype NA, no fabricated task). Makes the offering-relative battery REAL end-to-end (operator directive
  core deliverable). Behavioral execution of `--battery auto` is [LOCAL]. Score-neutral: scoring.py/rubric/
  probes/fetch/protocols byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by
  construction AND re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260724T004105Z
  live-confirms). `asrs/cli.py` + `tests/test_battery_wiring.py` only; direct-to-main. `test_battery_wiring.py`
  4→7 (+3 auto-mode: discovery→instantiate, end-to-end NA threading, null offering); suite 115→118. No Slack
  (direct-to-main, score-neutral, not sensitive, not a digest window at 02:12Z). Next cycle takes TRUTH.
  Cycle 27 TRUTH (operator ACCEPTANCE CRITERION made an executable in-cloud guard):
  `tests/test_offering_canonical.py` (4 tests) replays each committed canonical fixture through the REAL
  discovery path (`FetchContext.from_fixture -> discover_offering`, no network) and pins the classification:
  exact claimed SET `{metered_api,subscription,digital_good}` on both (exact equality -> a spurious ADDED or
  DROPPED archetype fails), claimed-union-unclaimed partition the template bank, and the operator's criterion —
  `{physical_good,service_booking,data_retrieval}` all NA on BOTH (physical_good called out). Converts the
  directive's `driftflight.com physical_good = NA` from a [LOCAL] run-log fact into a per-cycle tripwire
  (same move Cycles 17/19/21/23 made for the SCORING re-score). NON-VACUOUS: both flight-themed homepages
  say metaphorical "ship" x3 yet physical_good stays NA (the precision-critical false positive, on REAL
  captured evidence) — 2 extra tests pin it; negative control (offline, uncommitted) appending a bare-"ship"
  physical_good signal flips BOTH to CLAIMED -> caught. Discovery-only/score-neutral: `git diff --stat` empty
  but the new test; scoring.py/rubric/probes/fetch/offering.py byte-for-byte untouched -> rubric stays v0.7,
  canonical delta unchanged by construction AND re-measured (replay guard 8/8, 46.1 F / 85.5 B / +39.4,
  0 replay-miss; verify_20260724T004105Z 00:41Z ~2.5h live-confirms). Direct-to-main. Suite 118->122. No Slack
  (tests-only, moves no score, before the 16:00 UTC digest window). First duty: no open peer-gated PR
  (verified []); infra health check ran first — runner HEALTHY (verify_20260724T004105Z, 00:41Z, ~2.5h old),
  bench 118/118, ephemeral local-main divergence reset to origin/main 6f49f4b. NOTE: the retail-INVERSE half
  (a `books.toscrape.com`-class fixture pinning physical_good CLAIMED + API archetypes NA — the operator's
  "a shop shows the inverse") needs a [LOCAL] fixture capture; queued. Next cycle takes READOUT.
  Cycle 28 READOUT (operator directive BRICK 5 — comparability naming on the HTML battery card):
  `scorecard._battery` now renders an "Offering-relative" sub-block — "Assessed over" (claimed archetype
  chips) + "Not offered (NA — excluded from every mean/spread, never penalized)" (dimmed `.chip.na`) + a
  one-line interpretation — driven off `summary["na_archetypes"]`/`["assessed_archetypes"]` (brick 3,
  merged Cycle 26), placed after the per-intent grid, mirroring the terminal `report._battery_lines` order
  (Cycle 25). Renders ONLY when na_archetypes is populated (offering-relative discovery drove the battery);
  a hand-authored `--battery <path>` run has na_archetypes empty -> neither block renders = byte-for-byte the
  pre-brick-3 readout. Closes the last terminal->HTML gap for the NA-aware battery (same deferral per_kind
  Cycle 10->12 / between_kind_spread Cycle 18->20 took). Non-vacuous: the NA-naming test asserts every NA
  archetype renders including metered_api/subscription/service_booking/data_retrieval which have NO task and
  appear ONLY via this block; negative test pins na_archetypes==[] -> neither block. Display-only:
  `git diff --name-only` = scorecard.py + test_readout.py ONLY; scoring.py/rubric/probes/fetch/protocols/
  battery.py/offering.py/report.py byte-for-byte untouched -> rubric stays v0.7, canonical delta unchanged by
  construction AND re-measured (in-cloud replay guard 8/8, 46.1 F / 85.5 B / +39.4, 0 replay-miss).
  Direct-to-main. `test_readout.py` 17 -> 19; suite 122 -> 124. No Slack (display-only, moves no score, not a
  digest window at 04:12Z, digest last sent Cycle 16). First duty: no open peer-gated PR (verified []); infra
  health check ran first — runner HEALTHY (verify_20260724T004105Z, 00:41Z, ~3.5h old, 46.1 F/85.5 B/+39.4)
  BUT the :41 fires at 01/02/03:41Z produced NO artifact (3 consecutive gaps — not yet past the 6h floor, a
  possible fresh runner stall to WATCH; if still gapped past 6h next fire, flag + fold into post-16:00 digest).
  git realigned (origin/main force-updated to f48e2fd = Cycle 27; detached HEAD reset to it). Next cycle takes METHOD.
  Cycle 29 METHOD (vendor-neutral WORDING invariant made executable — the "Adversarial referee pass"
  wording half): `tests/test_rubric_wording.py` (4 tests) + a one-line rubric reword. Cycle 21 made
  vendor-neutral SCORING a tripwire (relabel-invariance); the WORDING half — "checks are worded by
  capability, never by vendor; no special-casing any domain or product" — was unguarded and had drifted:
  `bhv_no_human_gate.desc` carried "The Exa lesson —", naming a SCORED storefront in text
  `scorecard._write_rubric_page` renders VERBATIM to the public. Reworded to capability language
  ("Business-rule gates — a mandatory sales call or identity check — stop an agent as surely as a
  technical one …"), then guarded: a shared `_scan_checks_for_scored_storefront` scans every scored
  check's id+desc (the `checks:` list load_rubric parses) for a word-boundary denylist of SCORED
  storefront/product names (exa/driftflight/drift-flight). NON-VACUOUS (same scanner flags an injected
  "The Exa lesson" desc), anti-vacuous (scan covers the full parsed set == scoring index, ≥20 checks),
  and false-positive-guarded (does NOT flag the MEASUREMENT INSTRUMENT — panel models Claude/Codex or
  crawler tokens GPTBot/ClaudeBot/… which name the apparatus/crawler population, not a scored storefront).
  Scope = parsed scored checks only, NOT the changelog comments (which legitimately name the canonical
  pair + Shopify to document mechanism/score-neutrality). Honest limit: denylist tripwire against
  RE-INTRODUCING a KNOWN name, not a proof of universal neutrality — complements, not replaces, the
  relabel guard + standing prose re-read. Display-only: `desc` is rendered but never read by
  `scoring.score` (keys on id/pillar/max_points); scoring.py/probes/fetch/protocols/battery/offering
  byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by construction AND re-measured
  (replay guard 8/8, 46.1 F / 85.5 B / +39.4, 0 replay-miss). git diff = the desc prose lines only
  (version/max_points/weights/caps/grade_bands untouched). Direct-to-main. Suite 124 → 128. No Slack
  (display-only, moves no score, before the 16:00 UTC digest window). First duty: no open peer-gated PR
  (verified []); infra health check ran first — runner STALLED-BUT-UNDER-FLOOR (see runner note below).
  Next cycle takes COVERAGE.
  Cycle 30 COVERAGE (free-tier opt-in DISCOVERY broadened to a THIRD convention — the URL PATH):
  `asrs/behavioral/free_tier.py` `_scan_path_instruction` recognises a documented free-mode
  endpoint whose path carries a conventional free segment (`/free/…`, `/v1/free/…`,
  `/api/free-tier/call`), mirroring the header scanner + the query-param scanner (Cycle 22).
  Additive `FreeTierDiscovery.opt_in_path: str|None` + `opt_in_path` evidence key, populated by
  `discover_free_tier`. So a site advertising its free tier by a dedicated path endpoint (currently
  mis-discovered as "opt-in-undiscoverable") is now RECOGNISED — north-star many-conventions axis.
  PRECISION-FIRST/vendor-neutral: exact free-mode ALLOWLIST (`free/freetier/free-tier/free_tier/
  freemode/free-mode/free_mode`) so a bare substring "free" never trips (`/freedom`, `/freelance`,
  retail `/free-shipping` rejected); `scheme://host` prefix consumed-not-captured (host never a path
  segment); NON-VACUOUS context gate — free-tier prose checked with the matched path EXCISED, so a
  `/free/…` path alone (no adjacent free language) does NOT match. DELIBERATELY SCORE-NEUTRAL: not in
  the `advertised` gate (reads only header/free_units), not consumed by the live call (test-pinned:
  path-only doc keeps advertised=False; adding a free path to the header fixture leaves advertised
  byte-for-byte identical) — live wiring is score-increasing → queued [LOCAL] with the query-param
  half. NOT signing/payment code (diff confined to discovery region; parse_challenge/settle/sign +
  nonzero-refusal byte-for-byte untouched, sentinel grep clean). No scoring semantics, rubric stays
  v0.7; scoring.py/rubric/probes/protocols/fetch/offering/battery/scorecard untouched (git diff =
  free_tier.py + test_free_tier.py only); canonical delta unchanged by construction AND re-measured
  (in-cloud replay guard 8/8, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Direct-to-main.
  `test_free_tier.py` 9→10 (+path-discovery test: 3 extraction forms, 4 negative controls, evidence
  surfacing, score-neutrality); suite 128 → 129. No Slack (score-neutral additive discovery, moves no
  score, before the 16:00 UTC digest window). First duty: no open peer-gated PR (verified []); infra
  health check ran first — runner RECOVERED (newest verify_20260724T054104Z, 05:41Z, ~31 min old,
  46.1 F / 85.5 B / +39.4) → the 01–04:41Z stall Cycle 28/29 flagged has self-cleared; runner-stall
  watch CLOSED. Next cycle takes TRUTH.
  Cycle 31 TRUTH (offering-classifier VENDOR-NEUTRALITY made executable — domain-relabeling
  invariance for the task-selection layer): `tests/test_offering_canonical.py` +3 tests (4->7).
  Cycle 21 made vendor-neutral SCORING a tripwire (relabel-invariance in test_canonical_replay);
  the OFFERING classifier — which drives the operator directive's TASK SELECTION + NA semantics —
  was unguarded, even though `classify_offering(domain, surfaces)` takes the domain and the host
  string sits INSIDE the classifier's own matched evidence (`metered_api` post-endpoint quote =
  `POST https://<host>/…`, 2 quotes .org / 4 .com). Each new test relabels a committed canonical
  fixture's host to `vendor-neutral.test` (request keys + response bytes, whole-fixture sub, temp
  file, REAL `from_fixture -> discover_offering`) and asserts the CLAIMED archetype list (ordered)
  + UNCLAIMED/NA set are IDENTICAL to the un-relabeled discovery — proving the claimed/NA partition
  keys on EVIDENCE, not identity (a site's task set can't depend on its NAME). NON-VACUOUS: each
  test first asserts the host appears in the base evidence (relabel genuinely changes classifier
  input); neutral host is a different length + carries no signal word; and
  `test_offering_relabel_negative_control` monkeypatches a FAVORABLE identity-keyed special-case
  (force-add physical_good when "driftflight" in domain) -> CAUGHT (claimed sets diverge), then
  restores + asserts the restore. Worded by capability, never by vendor. Tests-only: git diff =
  test_offering_canonical.py only; scoring.py/rubric/probes/fetch/offering.py byte-for-byte
  untouched (`git diff --name-only -- asrs/ rubric/` empty) -> rubric stays v0.7, canonical delta
  unchanged by construction AND re-measured (replay guard 8/8, 46.1 F / 85.5 B / +39.4, 0
  replay-miss). Direct-to-main. Suite 129 -> 132. No Slack (tests-only, moves no score, before the
  16:00 UTC digest window). First duty: no open peer-gated PR (verified []); infra health check ran
  first — runner HEALTHY (newest verify_20260724T064105Z, 06:41Z, ~30 min old, 46.1 F / 85.5 B /
  +39.4). Next cycle takes READOUT.
  Local fire 2026-07-24T07:47Z TRUTH (complementary to the cloud rotation; cloud still on
  READOUT): executed the [LOCAL] "Retail-INVERSE offering fixture" item — the operator
  acceptance criterion's OTHER named half ("a retail storefront shows the inverse"), now an
  in-cloud tripwire. Captured `fixtures/canonical/books.toscrape.com.json` via a STATIC $0
  crawl (41 GET, 0 POST, public book-catalog sandbox, no secrets) + wired
  `test_retail_inverse_offering` into `tests/test_offering_canonical.py` (7 → 8): replays the
  committed fixture through the REAL `from_fixture → discover_offering` path and asserts the
  MIRROR of Cycle-27's canonical NA guard — claimed == {physical_good} EXACTLY, {metered_api,
  subscription, digital_good} (what the canonical pair CLAIMS) all NA; non-vacuous on ANCHORED
  fulfillment evidence (add-to-cart + stock from "In stock"/"Add to basket"), the exact
  complement of the pair's metaphorical-"ship" NA case. Score-neutral: `git diff -- asrs/
  rubric/` empty → rubric v0.7, canonical delta unchanged (replay guard 8/8, 46.1 F / 85.5 B /
  +39.4; corroborated by verify_20260724T074105Z). Direct-to-main. Suite 132 → 133. First duty:
  no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260724T074105Z, 07:41Z, ~40s old at fire). The offering acceptance criterion is now
  guarded in-cloud on BOTH sides; the last offering-layer fixture gap is the example.com
  non-storefront control (empty offering), folded into the Third-control-domain [LOCAL] item.
  Cycle 32 READOUT (methodology page made navigable FROM a card's cap alert — the long-standing
  cap-chip anchor-link follow-up): each `methodology.html` §8 cap row now carries `id="cap-<slug>"`
  and a card's "Grade capped by <slug>" chip renders as `<a class="chip"
  href="methodology.html#cap-<slug>">`, so a reader who sees a capped grade jumps straight to why
  it caps. ONE source of truth (`scorecard._cap_anchor`, sanitizing + shared by both surfaces →
  can't drift) + a `.chip` `text-decoration:none`/`a.chip:hover` affordance. Display-only:
  `git diff --name-only` = scorecard.py + test_readout.py ONLY; scoring.py/rubric/probes/fetch/
  protocols/behavioral/offering/battery 0 files changed → rubric stays v0.7, canonical delta
  unchanged by construction AND re-measured (replay guard 8/8, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; corroborated by verify_20260724T074105Z). Vendor-neutral (links key on the
  rubric's own capability-worded cap slugs, no domain/vendor string). Direct-to-main.
  `test_readout.py` 19 → 23 (+4: sanitizer, methodology rows carry ids, card chip links + no-cap
  no-op, and the load-bearing CANNOT-DRIFT test tying each rubric cap's rendered card link to an
  id present in the rendered methodology page); suite 133 → 137. No Slack (display-only, moves no
  score, before the 16:00 UTC digest window at 08:12Z, digest last sent Cycle 16). First duty: no
  open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260724T074105Z, 07:41Z, ~31 min old, 46.1 F / 85.5 B / +39.4); git realigned (stale
  Jul-22 divergent local `main` tip `2e66201` reset to origin `0cf1a98`). Next cycle takes METHOD.
  Local fire 2026-07-24T08:52Z METHOD (complementary to the cloud rotation; cloud still takes
  METHOD next): executed the P1 [LOCAL] "Nested shopper spawns the full user MCP fleet" — made the
  nested `claude -p` panels HERMETIC. Both `asrs/behavioral/shopper._claude_cmd` AND
  `trust_probe._claude_cmd` now pass `--strict-mcp-config`, so a shopper/trust subprocess no longer
  inherits the operator's GLOBAL `~/.claude.json` MCP fleet
  (`trigger/unityMCP/linear-server/hex/posthog/motherduck` — the exact set the 10:13Z battery saw
  booting ~1 min/panel before browsing). The shopper needs only WebFetch/WebSearch; strict + no
  `--mcp-config` == empty fleet. LIVE-verified on Jonah's machine: one real `shopper._run_one`
  on driftflight.com browsed fine (10 turns, all 5 checkpoints TRUE, coherent wallet/browser-gate
  blockers) and its REAL panel transcript shows `mcp_servers == []` — hermetic on the actual fixed
  path. Behavioral-execution plumbing only (a CLI flag on the nested agent): git diff = shopper.py
  + trust_probe.py + new `tests/test_shopper_hermetic.py` (4 tests) — scoring.py/rubric/probes/
  fetch/offering/battery byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by
  construction AND re-measured (replay guard 8/8, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  live-corroborated by verify_20260724T084104Z). Direct-to-main. Suite 137 → 141 (16 → 17 files).
  Evidence: runs/local/hermetic_shopper_verify_20260724T084946Z/. First duty: no open peer-gated PR
  (verified []); runner HEALTHY (verify_20260724T084104Z, 08:41Z, ~1 min old at fire). This
  de-contaminates + speeds EVERY future behavioral run — the honest prerequisite for the top-P0
  operator `--battery auto` acceptance rerun (now runs hermetic + faster). Cloud rotation unaffected.
  Cycle 33 METHOD (vendor-neutral WORDING invariant extended from the parsed rubric to the RENDERED
  readout prose — the referee-pass READOUT half): `tests/test_readout_wording.py` (4 tests) renders the
  public readout for a NEUTRAL domain (`example.test`) via `build_scorecard` and scans the rendered
  `methodology.html` + card `card.html` for scored-storefront names using the SAME denylist + matcher
  Cycle 29 uses — factored into a shared `_scan_text_for_scored_storefront(text)` in
  `test_rubric_wording.py` (behavior-preserving: `_scan_checks_for_scored_storefront` delegates, 4/4
  unchanged). Cycle 29 guarded the parsed `checks:` list only; the HAND-AUTHORED methodology prose + card
  `<div class="desc">` strings (the surface the "Exa lesson" leak lived on) were unguarded. DOMAIN-AS-DATA
  handled by the neutral domain (a card is ABOUT a storefront -> its domain appears as data; a denylisted
  hit for `example.test` can only be baked-in template prose). rubric.html DELIBERATELY EXCLUDED (renders
  YAML verbatim incl. changelog comments that legitimately name the canonical pair — Cycle-29's
  engineering-history category) AND reused as a LIVE non-vacuous control: the test asserts the scanner
  FIRES on rubric.html (`['driftflight','drift-flight']`) -> proof the matcher fires on rendered HTML, so
  the clean card/methodology zeros are meaningful; second non-vacuous leg = synthetic "The Exa lesson"
  desc blob flagged; substantiveness guard (>=4000 chars) blocks an empty-render vacuous pass. Tests-only:
  `git diff --name-only -- asrs/ rubric/` EMPTY -> scoring.py/rubric/probes/scorecard byte-for-byte
  untouched, rubric stays v0.7, canonical delta unchanged by construction AND re-measured (replay guard
  8/8, 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260724T084104Z live-corroborates). Direct-to-main.
  `test_readout_wording.py` 4/4 (new) + `test_rubric_wording.py` 4/4 (refactor); suite 141 -> 145 (17 -> 18
  files). No Slack (tests-only, moves no score, before the 16:00 UTC digest window, digest last sent
  Cycle 16). First duty: no open peer-gated PR (verified []); infra health check ran first — runner
  HEALTHY (verify_20260724T084104Z, 08:41Z, ~31 min old, 46.1 F / 85.5 B / +39.4); git realigned (detached
  HEAD from forced origin/main update 0b0ad41 -> main = origin/main). Next cycle takes COVERAGE.
  Cycle 34 COVERAGE (offering discovery reads the OpenAPI / Swagger spec — the operator
  directive's FOURTH named surface): `asrs/offering._SURFACE_DOCS` gains `/openapi.json`,
  `/.well-known/openapi.json`, `/swagger.json`. Brick 1 covered homepage + the natural-language
  docs (llms.txt/llms-full/manifest) but NOT the machine API CONTRACT the directive names
  ("llms.txt, manifest/catalog, OpenAPI, homepage") — the surface an API-FIRST storefront is
  most likely to expose (a metered-API product may serve no homepage/llms.txt, only its spec →
  was classified from homepage alone, mis-readable as offering nothing). NO new signal needed:
  the spec's servers URLs / path list / operation summaries carry exactly the vendor-neutral
  "qualified API"/"pay-per-*"/usage-based/generated-media/x402 language the signal bank already
  anchors on — only the surface had to be READ; a spec that 404s is simply absent (discovery
  tolerates a missing surface). SCORE-NEUTRAL by construction: `discover_offering` is called ONLY
  from `cli._resolve_battery` (`--battery auto`), NEVER on the scoring path (grep-verified); the
  commerce-manifest SCORING probe keeps its OWN separate `protocols._AGENT_SURFACE_DOCS` (original
  three docs, DELIBERATELY untouched — OpenAPI there would be score-increasing + peer-gated).
  `git diff --name-only -- asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py` EMPTY → rubric stays
  v0.7; canonical delta unchanged by construction AND re-measured (replay guard 8/8, 46.1 F /
  85.5 B / +39.4, 0 replay-miss) AND the canonical OFFERING guard `test_offering_canonical.py` 8/8
  UNCHANGED (added surfaces absent from the committed fixtures → replay-miss → absent → canonical
  classification byte-identical); live-corroborated by verify_20260724T094103Z (09:41Z). Not
  payment/signing code. Direct-to-main. `test_offering.py` 7→9 (+OpenAPI-spec-only classification
  test on 6 distinct spec signals with physical_good/subscription correctly NA; +structural wiring
  guard); suite 145 → 147 (all 18 files exit 0). No Slack (score-neutral additive discovery, moves
  no score, before the 16:00 UTC digest window, digest last sent Cycle 16). First duty: no open
  peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260724T094103Z, 09:41Z, ~31 min old, 46.1 F / 85.5 B / +39.4); git on main =
  origin/main (dcb2a90, detached HEAD from the local-verify push realigned). Next cycle takes TRUTH.
  Cycle 35 TRUTH (the canonical replay REGRESSION guard grows a THIRD real domain — a retail
  storefront as the transactability FLOOR): `tests/test_canonical_replay.py` +3 tests (8→11), wiring
  the already-committed `fixtures/canonical/books.toscrape.com.json` ([LOCAL] 07:47Z capture, until
  now used ONLY by the offering-classifier guard) into the SCORING replay path. (6)
  `test_retail_storefront_replays_29_5` pins overall 29.5 F / rubric 0.7 / all 5 pillars / 0
  replay-miss — a browser-checkout SHOP (structurally ≠ the two API storefronts) now in the
  regression signal, so a benchmark claim rests on >1 pair. (7)
  `test_retail_storefront_earns_no_agent_native_payment` — the MIRROR of the +39.4 capability guard
  (Cycle 19/23): a genuine physical-goods storefront (physical_good CLAIMED) earns EXACTLY 0
  transactability (x402_probe FAIL, self_serve_payg no live x402, NO commerce-protocol-*/x402-live);
  scored over the IDENTICAL 14-check set as the no-rails canonical .org yet STRICTLY LOWER (0.0 vs
  18.75 — .org keeps a residual PARTIAL self-serve signal) → the site that most obviously "sells
  things" is the transactability floor, proving the pillar is capability-gated (can an agent pay
  programmatically?), not store-type-gated; catches a probe that credited "looks-like-a-shop" as
  payability. (8) `test_relabel_invariance_retail` extends the Cycle-21 vendor-neutrality relabel
  tripwire to the third domain (29.5 F identity-invariant). Worded by capability, never by vendor.
  Tests-only: `git diff -- asrs/ rubric/` EMPTY → scoring path byte-for-byte untouched, rubric stays
  v0.7, canonical PAIR unchanged by construction AND re-measured (replay guard 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; verify_20260724T104103Z 10:41Z live-corroborates). Direct-to-main. Suite
  147 → 150. No Slack (tests-only, moves no score, before the 16:00 UTC digest window, digest last
  sent Cycle 16). First duty: no open peer-gated PR (verified []); infra health check ran first —
  runner HEALTHY (verify_20260724T104103Z, 10:41Z, ~31 min old, 46.1 F / 85.5 B / +39.4); git
  realigned to origin/main (3e12924, detached HEAD from the forced-update local-verify push reset to
  main). REMAINING TRUTH frontier: the example.com non-storefront control (fourth point, zero-commerce
  baseline — needs a [LOCAL] fixture capture; test wiring cloud-doable once it lands). Next cycle takes READOUT.
  Cycle 36 READOUT (canonical-delta HISTORY readout — the benchmark can now READ its own regression signal over time):
  new pure/stdlib/read-only `asrs/canonical_history.py` (`load_points`/`summarize`/`render` + `asrs canonical-history`
  CLI) reads the 66 committed `runs/local/verify_*.json` live re-scores into a `CanonicalHistory` — latest point,
  `divergence` = live delta − fixture baseline (+39.4), 3-band verdict (in-band ≤2.0 / drifting ≤8.0 / diverged), a
  TRAILING `consecutive_out_of_band` run (1=jitter, N≥3=sustained real move), and a delta sparkline. Skips malformed
  artifacts (pre-Cycle-13 FileNotFoundError / non-ok domains) — attribution honesty applied to the history. Baseline
  constant cross-checked against `test_canonical_replay.EXPECTED_DELTA` (can't silently drift). **This immediately
  surfaced a LIVE CANONICAL DRIFT — see the prominent note below.** Score-neutral (git diff -- scoring.py/rubric/probes/
  fetch/behavioral/offering/battery EMPTY → rubric v0.7, replay guard 11/11, canonical PAIR 46.1 F / 85.5 B / +39.4
  unchanged by construction). Direct-to-main. `test_canonical_history.py` 6/6 (new); suite 150 → 156. No Slack (score-
  neutral ship; live drift folds into the next post-16:00 UTC digest, this fire 14:21Z). First duty: no open peer-gated
  PR (verified []); infra health check ran first — runner HEALTHY (verify_20260727T134147Z, 13:41Z, ~33 min old). NOTE:
  no CLOUD cycle fired between Cycle 35 (07-24T11:12Z) and this fire (07-27T14:21Z) — only the local verify runner
  heartbeated for ~3 days; cloud loop resumed this fire. Next cycle takes METHOD.
  Cycle 37 METHOD (pillar-level ATTRIBUTION of a canonical divergence — the "explain the delta in capability terms"
  duty is now COMPUTED, not hand-written): extended the read-only `asrs/canonical_history.py` (Cycle 36) so a
  divergence is attributed to the pillar that drove it. `CanonicalPoint` now carries `no_rails_pillars`/
  `with_rails_pillars` (per-side per-pillar overalls, NUMERIC entries only — a `None` pillar, e.g. the 07:40Z
  transient's CANT_TEST legibility/transactability, is DROPPED, never credited a move → attribution honesty at the
  pillar layer); `PillarMove`/`PillarAttribution` (`anchor_ts`, `moves` largest-|change|-first, `.top`);
  `summarize` computes `attribution` via `_attribute` ONLY when latest is out of band AND an earlier in-band anchor
  exists (`points[-(run+1)]`) — else honest `None` (in-band = nothing to explain; whole series OOB = no stable
  baseline observed live). `render` names it. On the REAL committed series the computed line reproduces the Cycle-36
  HAND-WRITTEN note EXACTLY: `driftflight.com legibility fell 90.9 → 63.6 (-27.3) — the largest pillar move`; flat
  pillars correctly not movers. Score-neutral (`git diff --name-only` = canonical_history.py + test only;
  scoring.py/rubric/probes/fetch/protocols/behavioral/offering/battery byte-for-byte untouched → rubric v0.7,
  canonical PAIR unchanged by construction AND re-measured — replay guard 11/11, 46.1 F / 85.5 B / +39.4, 0
  replay-miss). Vendor-neutral (imports no scoring code; reference-pair hosts as DATA via existing constants).
  Direct-to-main. `test_canonical_history.py` 6 → 10 (+4: real-drift mirror w/ flat-pillar non-vacuous control;
  in-band → None; unobserved-pillar-skip + no-anchor → None; real series fingers `.com`, recovery-guarded); suite
  156 → 160. No Slack (score-neutral/non-sensitive; fire 15:14Z before the 16:00 UTC digest window — the open live
  drift + this ship fold into that digest). First duty: no open peer-gated PR (verified []); infra health check ran
  first — runner HEALTHY (verify_20260727T134147Z, 13:41Z, ~1.5h old). Next cycle takes COVERAGE.
  Cycle 38 COVERAGE (free-tier opt-in DISCOVERY broadened to a FOURTH convention — the JSON REQUEST-BODY field):
  `asrs/behavioral/free_tier.py` `_scan_body_field_instruction` recognises a storefront that documents its free tier as
  a JSON body field (`{"tier":"free"}`/`{"mode":"free"}`/`{"free_tier":true}`), mirroring the header/query-param/path
  scanners → additive `FreeTierDiscovery.opt_in_body: tuple[str,str]|None` + an `opt_in_body` evidence key, populated by
  `discover_free_tier`. Precision-first/vendor-neutral: the load-bearing distinguisher from the header scanner (bare
  `Name: value`) is the IN-OBJECT gate — a body field must be a DOUBLE-QUOTED JSON key inside an open `{…}` object (so a
  header `` `zc-mode: free` `` and a query `?tier=free` are never misread → both verified None); free-context gate +
  explicit "free" hint in name/value (no "mode" fallback, so `{"tier":"starter"}` near free prose is not the opt-in);
  plumbing-field denylist (`{"model":"free-tier-v2"}` skipped). DELIBERATELY SCORE-NEUTRAL (same as Cycles 22/30): not in
  the `advertised` gate (reads only header/free_units), not consumed by the live call — test-pinned via the
  `{"free_tier":true}` fixture the HEADER scanner does NOT also catch: body-only doc keeps advertised=False; adding a body
  field to the header+manifest fixture leaves advertised byte-identical. OBSERVATION (queued P1, not fixed): the existing
  header scanner OVER-CATCHES a `{"tier":"free"}` body field as a header (pre-existing; opt_in_body never read by the gate
  so moves no score; disambiguation is score-affecting → peer-gated/[LOCAL]). NOT signing/payment code (parse_challenge/
  settle/sign/probe byte-for-byte unchanged, sentinel grep of the diff clean). No scoring semantics, rubric stays v0.7;
  git diff over scoring.py/rubric/probes/fetch/protocols/offering/battery/scorecard EMPTY → canonical delta unchanged by
  construction AND re-measured (in-cloud replay guard 11/11, 46.1 F / 85.5 B / +39.4, 0 replay-miss; free_tier is
  behavioral-only, off the static replay path). Direct-to-main (git diff --stat = free_tier.py + test_free_tier.py only).
  `test_free_tier.py` 10→11 (+body-field discovery test: 3 extraction forms, 5 negative controls, evidence surfacing,
  score-neutrality pair); suite 160 → 161. First duty: no open peer-gated PR (verified []); infra health check ran first —
  runner HEALTHY (verify_20260727T134147Z, 13:41Z, ~2.5h old). DAILY DIGEST DM SENT this fire (first cycle after 16:00 UTC,
  16:13Z) — carries the open LIVE CANONICAL DRIFT + this ship. Live-wiring (fold query/path/body into advertised + the
  free-mode call) remains the shared [LOCAL] score-increasing follow-up. Next cycle takes TRUTH.
  Cycle 39 TRUTH (canonical divergence attributed to a SIDE — no-rails gaining vs with-rails softening,
  computed not hand-written): extended read-only `asrs/canonical_history.py` (Cycle 36/37). Cycle 37 made
  the PILLAR computed (`.com` legibility fell 90.9→63.6); the STATE drift note still HAND-WROTE the layer
  above — "the delta narrowed because the RAILS side softened, not the no-rails side improving." The delta
  can narrow two OPPOSITE ways (no-rails floor GAINING capability = real gap closing, a re-capture candidate;
  vs with-rails reference LOSING ground = a real-world site regression, pinned fixture still the TRUE gap →
  wait). `DivergenceCause` (`no_rails_change`/`with_rails_change` overall moves vs the last in-band anchor;
  `gap_change`, `driver`, `driver_change`, `reference_degraded`) + `_cause` (SAME anchor/gate as `_attribute`,
  from OVERALL scores so never None-on-one-side) + `cause_verdict` (4 honest cases keyed on driver+direction)
  + a `driver:` render line. On the REAL series reproduces STATE EXACTLY: `driftflight.com overall fell -6.8
  — the gap narrowed because the with-rails reference SOFTENED …, the pinned fixture still represents the
  true gap` (no-rails 0.0, with-rails -6.8, reference_degraded True). Non-vacuous: +test pins the OPPOSITE
  case (no-rails RISES → driver no-rails, reference_degraded False, "GAINED capability — a real benchmark
  movement"); in-band → cause None, no `driver:` line; real-series recovery-guarded. Vendor-neutral (imports
  no scoring code; hosts as DATA via existing `CANONICAL_*` constants). Score-neutral: `git diff --name-only`
  = canonical_history.py + test only; scoring.py/rubric/probes/… byte-for-byte untouched → rubric v0.7,
  canonical delta unchanged by construction AND re-measured (replay guard 11/11, 46.1 F / 85.5 B / +39.4,
  0 replay-miss). Direct-to-main. `test_canonical_history.py` 10→13; suite 161→164. No Slack (tests +
  read-only diagnostic, moves no score, digest already sent Cycle 38 16:13Z, this fire 17:13Z not a new
  window). First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260727T134147Z, 13:41Z, ~3.5h old, under 6h floor) BUT the 14/15/16:41Z fires produced NO
  artifact (3 consecutive gaps, as at Cycle 28 — a possible fresh runner stall to WATCH; flag if still
  gapped past 6h next fire). Next cycle takes READOUT.
  Local fire 2026-07-27T18:11Z TRUTH (BOOKKEEPING RECONCILIATION + ship — the networked/self-healing
  half): landed the example.com zero-commerce baseline whose CODE was lost on 07-24. Root cause: the
  2026-07-24T11:48Z local fire authored + validated `fixtures/canonical/example.com.json` + the four
  test cases and wrote its LOG entry, but its CODE commit never happened — only LOG.md was swept up by
  the 12:41Z verify runner (commit 2cf0cef), so the committed LOG claimed a ship whose tests/fixture sat
  UNCOMMITTED in the working tree for ~3 days (the cloud loop was paused 07-24→07-27; only the verify
  runner heartbeated). Bookkeeping-down per self-healing → repaired FIRST: re-validated the surviving WIP
  against the CURRENT suite (all green), then committed it, making git history consistent with the
  already-committed 07-24 LOG (append-only respected — the 07-24 entry is UNEDITED; a new LOG entry
  documents the reconcile). Landed `test_canonical_replay.py` 11→14 (nonstorefront replays 22.5 F /
  earns-no-agent-native-payment capability-floor mirror / relabel-invariance) + `test_offering_canonical.py`
  8→9 (nonstorefront empty offering). Score-neutral: `git diff -- asrs/ rubric/` EMPTY → rubric v0.7,
  canonical PAIR unchanged by construction AND re-measured (replay guard 14/14, 46.1 F / 85.5 B / +39.4,
  0 replay-miss); fixture is 41 GET / 0 POST (invariant #1 clean). Full suite 164→168. Direct-to-main.
  The regression + vendor-neutrality signal now spans FOUR real domains (two API storefronts 46.1/85.5,
  a retail floor 29.5, this zero-commerce baseline 22.5). First duty: no open peer-gated PR
  (`gh pr list --state open` → []). Git hygiene: local main was 4 commits behind (Cycles 36–39 shipped
  while this checkout sat at the 13:41Z verify commit); stashed the WIP, fast-forwarded to origin
  (0757fa1), restored the WIP cleanly (origin never touched the three WIP files), then shipped.
  INFRA WATCH (not a floor breach yet): the verify runner's last three fires (14:44/16:56/17:41Z) FAILED
  `git_pull` with "Could not resolve host: github.com" (transient machine DNS/network — github is reachable
  again this fire) so they could not push; newest SUCCESSFULLY-pushed verify is verify_20260727T134147Z
  (13:41Z), ~4.5h old at this fire — still UNDER the 6h floor. If the runner's next :41 fire still can't
  pull and the 13:41Z artifact crosses 6h, flag it. No code repair (Cycle-19 crash-wrapper/heartbeat is
  working — it correctly recorded the failures; the block is transient network, self-clearing). The
  Cycle-17 replay guard is the in-cloud canonical signal regardless. Cloud rotation unaffected (still READOUT).
  Cycle 40 READOUT (the canonical-history diagnosis becomes an HTML SURFACE — the last terminal→HTML gap
  for the benchmark reading its own regression signal): new `scorecard._write_canonical_history_page`
  renders `canonical-history.html` next to every card (published by `build_scorecard` alongside rubric/
  methodology, footer cross-link) surfacing the FULL `asrs canonical-history` diagnosis off the committed
  `runs/local/verify_*.json` series — latest reading, divergence + band verdict, sustained-drift run,
  PILLAR attribution (Cycle 37) AND SIDE/direction cause (Cycle 39) — plus a single-series delta-over-time
  SVG trend (`_history_trend_svg`: live delta per re-score vs a dashed pinned-fixture baseline, each point
  colored by its divergence BAND, latest direct-labeled, band legend). New public
  `canonical_history.band_for_delta` (one source of truth for the point-band thresholds, shared by terminal
  + chart). dataviz skill loaded: form = change-over-time/ONE series → no identity legend; per-point band =
  reserved STATUS encoding shipped WITH a named legend (never color-alone); status inks in-band #067647 /
  drifting #b54708 / diverged #b42318; rendered + eyeballed via Chromium (SVG coords within plot bounds).
  Vendor-neutral: names the reference pair as DATA (page is ABOUT those two domains) — SAME
  engineering-history category as rubric.html, deliberately OUT OF SCOPE for the wording scanner (guards
  capability-worded CHECK prose on methodology+card); `test_readout_wording` unchanged/green. Score-neutral:
  `git diff --name-only` = canonical_history.py + scorecard.py + test_readout.py ONLY; scoring.py/rubric/
  probes/fetch/protocols/battery/offering/behavioral byte-for-byte untouched → rubric stays v0.7, canonical
  PAIR unchanged by construction AND re-measured (replay guard 11/11, 46.1 F / 85.5 B / +39.4, 0 replay-miss).
  Direct-to-main. `test_readout.py` 23→29 (+6: written+linked, drift diagnosis rendered, in-band non-vacuous
  control, SVG band-coloring+baseline+latest-label, empty-series graceful, names-pair-as-data); suite 164→170.
  No Slack (READOUT display-only + tests, moves no score, digest already sent Cycle 38 16:13Z, this fire
  ~18:14Z not a new window). First duty: no open peer-gated PR (verified []); infra health check ran first —
  runner HEALTHY (verify_20260727T134147Z, 13:41Z, ~4.5h old, under 6h floor) BUT the 14/15/16/17:41Z fires
  produced NO artifact (4 consecutive gaps — the Cycle-39 stall persists; still under 6h, flag if past 6h
  next fire); git realigned (detached HEAD from forced origin/main update reset to main = 0757fa1). Next
  cycle takes METHOD. (Rebased onto the concurrent 18:11Z local fire; its more-informed infra note — the
  runner's :41 failures are a TRANSIENT github.com DNS block, not a code stall — supersedes the "stall
  persists" read above. Its example.com baseline ship also moved the pre-change suite baseline: 168, not
  164 — so this cycle's true suite move is 168 → 174 after the +6 readout tests.)
  Cycle 41 METHOD (OFFERING-layer vendor-neutrality guard extended to all FOUR real domains — the
  adversarial-referee-pass leg (b)): `tests/test_offering_canonical.py` +2 (9→11).
  `test_offering_relabel_invariance_retail` (books.toscrape.com → claimed {physical_good}, all else NA,
  identity-invariant) + `test_offering_relabel_invariance_nonstorefront` (example.com → honest-empty
  offering, every archetype NA, invariant — renaming a bare page invents no offering), via a shared
  `_assert_offering_relabel_general(domain, expected_claimed)` that relabels the whole fixture to
  `vendor-neutral.test` and asserts CLAIMED (ordered) + NA sets identical through the REAL
  `from_fixture → discover_offering` path. The SCORING-layer relabel guard (test_canonical_replay) has
  spanned all four since Cycle 35+18:11Z; the OFFERING/task-selection classifier was relabel-guarded only
  on the pair (Cycle 31) — now matched. HONEST non-vacuity: the pair anchors on host-in-evidence-QUOTE
  (metered_api `POST https://<host>/…`), which does NOT hold for retail (host-free "In stock"/"Add to
  basket" prose) or the empty non-storefront — so the new helper anchors non-vacuity on the host being
  present in the FETCHED SURFACES (`domain in raw` + `_discover_relabeled` rewrites every occurrence);
  the empty case additionally pins the full-NA partition (all six archetypes unclaimed before AND after,
  a concrete non-empty structure, and the retail/pair tests prove the classifier isn't constant all-NA);
  the pre-existing negative control (identity-keyed special-case CAUGHT) still gives the shared machinery
  teeth. Tests-only: `git diff -- asrs/ rubric/` EMPTY → scoring.py/rubric/probes/fetch/offering.py
  byte-for-byte untouched → rubric v0.7, canonical PAIR unchanged by construction AND re-measured (replay
  guard 14/14, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Direct-to-main. Full suite 174 → 176. No Slack
  (tests-only, moves no score, digest already sent Cycle 38 16:13Z, not a new window). First duty: no open
  peer-gated PR (verified []); infra health check ran first — runner HEALTHY (verify_20260727T184100Z,
  18:41Z, fresh) AND the LIVE CANONICAL DRIFT RECOVERED (that artifact reads .com back at 85.5 B, legibility
  90.9 / transactability 87.5 at baseline, delta +39.4 in-band — self-cleared from ~78.7 C); bench green
  after `pip install -r requirements.txt` closed the known eth-account gap (test_free_tier 10/11→11/11).
  Next cycle takes COVERAGE.
  Cycle 42 COVERAGE (offering discovery reads a FIFTH agent-facing surface — the agent-plugin descriptor
  `/.well-known/ai-plugin.json`): `asrs/offering._SURFACE_DOCS` gains that path (ordered after the
  natural-language docs, before the OpenAPI contract). Brick 1 read homepage + natural-language docs
  (llms.txt/llms-full/manifest); Cycle 34 added the machine API CONTRACT (OpenAPI/Swagger); this adds the
  open, vendor-neutral manifest a storefront publishes so an AI agent knows what it is / how to use it. Its
  `description_for_model`/`description_for_human` are a hand-written model-facing SUMMARY of the offering in
  exactly the natural-language commerce/capability prose ("inference API"/"generate an image"/
  "pay-per-generation"/"usage-based"/x402) the signal bank already anchors on → NO new signal, only the
  surface had to be READ; a descriptor-only site (no homepage/llms.txt/reachable spec) was previously
  mis-readable as offering nothing (the exact failure Cycle 34's OpenAPI addition fixed for spec-only sites).
  SCORE-NEUTRAL by construction: `discover_offering` is called ONLY from `cli._resolve_battery`
  (`--battery auto`), NEVER on the scoring path (grep-verified: absent from scoring.py/probes/; the
  commerce-manifest SCORING probe keeps its own separate `protocols._AGENT_SURFACE_DOCS`, DELIBERATELY
  untouched — a surface there would be score-increasing + peer-gated). `git diff --name-only -- scoring.py
  rubric/ probes/ fetch.py protocols.py battery.py` EMPTY → rubric stays v0.7; not payment/signing code
  (read-only `ctx.get` GETs, $0/invariant-#1 clean, no POST/sign added). Committed canonical fixtures predate
  this surface → replay-miss/absent on them → canonical delta unchanged by construction AND re-measured
  (replay guard 14/14, 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260727T194100Z 19:41Z in-band
  live-corroborates) AND `test_offering_canonical.py` byte-identically 11/11 UNCHANGED (same property Cycle 34
  relied on). Direct-to-main. `test_offering.py` 9→10 (+descriptor-only classification test on 5 distinct
  descriptor signals, physical_good/subscription correctly NOT claimed; wiring guard extended to assert the
  ai-plugin path is in the live surface set); suite 176 → 177 (all 19 files exit 0). No Slack (score-neutral
  additive discovery, moves no score, digest already sent Cycle 38 16:13Z, not a new window at 20:16Z). First
  duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260727T194100Z, 19:41Z, fresh, delta +39.4 in-band). All FIVE agent-facing surface classes
  (homepage / natural-language docs / agent-plugin descriptor / OpenAPI contract / manifest) now read. Next
  cycle takes TRUTH.
  Local fire 2026-07-27T20:54Z TRUTH (machine-surface fixture + offering-classifier precision fix,
  direct-to-main, score-neutral): executed the [LOCAL] "Machine-surface-only storefront fixture" item —
  the calibration follow-up to Cycles 34 (OpenAPI) + 42 (ai-plugin), whose surface-reading was tested only
  synthetically (committed fixtures predate both). Live-probed real API-first storefronts; captured
  `fixtures/canonical/api.replicate.com.json` (8 GET / 0 POST, homepage `{}` + 92 KB public OpenAPI spec, no
  secrets — Authorization strings are `$REPLICATE_API_TOKEN` placeholders, blobs are public spec examples).
  The live crawl SURFACED A FALSE POSITIVE: `discover_offering` classified api.replicate.com
  `['metered_api','physical_good']` because the `sku-inventory` signal (bare `\bSKU\b|\binventory\b`) matched
  "The SKU for the hardware used to run the model" — a COMPUTE/GPU hardware SKU, not retail inventory (a
  physical_good task there would garden-path an agent, the exact battery pollution the operator directive
  removes). FIXED `asrs/offering.py`: re-anchored `sku-inventory` to the RETAIL sense only (product/item/per/
  each SKU; SKU number/code/count; inventory count/levels/on-hand/management; manage/track/check inventory;
  in-stock inventory) — every compute-SKU form now rejected, every retail form kept; nearly-redundant for
  recall (books.toscrape.com's physical_good rests on add-to-cart+stock; sku-inventory fires on NONE of the
  four committed fixtures). api.replicate.com now `['metered_api']`, driven by `/openapi.json`. Tests:
  `test_offering_canonical.py` 11→12 (`test_machine_surface_openapi_storefront` — openapi READ + DROVE
  classification, machine-surface-first with a zero-signal homepage, physical_good=NA NON-VACUOUS on the
  trap phrase asserted present); `test_offering.py` 10→11 (synthetic compute-vs-retail SKU precision).
  Score-neutral: `discover_offering`/`classify_offering` off the scoring path (grep-verified);
  `git diff --name-only -- asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py asrs/protocols.py asrs/battery.py
  asrs/behavioral/` EMPTY → rubric v0.7, no `battery_semantics_version` bump. Canonical pair 46.1 F / 85.5 B /
  +39.4 unchanged by construction AND re-measured (replay guard 14/14, 0 replay-miss; verify_20260727T204103Z
  20:41Z in-band); four committed domains' offering classification byte-identical. Suite 177→179 (all 19 exit
  0). First duty: no open peer-gated PR (`[]`); infra HEALTHY (verify_20260727T204103Z, ~35 s old at fire).
  Cloud rotation unaffected (still TRUTH next).
  Cycle 43 TRUTH (the canonical re-capture DECISION is now COMPUTED, not hand-reasoned — the capstone of the
  Cycles 36→41 drift-diagnostic arc): new pure `asrs/canonical_history.recapture_advice(history) ->
  RecaptureAdvice(code, reason)`, stored on `CanonicalHistory.recapture` in `summarize`, rendered as a
  `re-capture:` line. Every prior layer (band 36 / pillar attribution 37 / side-cause 39 / HTML 40) feeds ONE
  decision — does the committed fixture still represent the true capability gap, or should the pinned delta be
  re-captured [LOCAL]? — which the STATE drift note hand-reasoned FIVE times during the 07-27 `.com` drift. Now
  synthesized into five honest codes (NEVER an action; moving the pinned baseline is [LOCAL]/comparability-
  affecting): `baseline-valid` (in-band, no re-capture) / `wait-not-yet-sustained` (out of band, run < 3, could
  be jitter) / `defer-reference-degraded` (sustained, with-rails reference SOFTENED = real-world site change,
  pinned fixture still the true gap → DEFER — the load-bearing 07-27 case, VINDICATED by the Cycle-41 recovery) /
  `recapture-candidate` (sustained AND the baseline genuinely moved — no-rails gaining or reference durably
  improving → a [LOCAL] re-capture re-pins it) / `review-no-anchor` (sustained but no in-band anchor in the
  series → human look). Refactored the render's literal `3` → `_SUSTAINED_MIN` (behavior-preserving, one source
  of truth). Read-only diagnostic: `git diff --name-only` = canonical_history.py + test ONLY; scoring.py/rubric/
  probes/fetch/protocols/battery/offering/behavioral/scorecard byte-for-byte untouched → rubric stays v0.7,
  canonical PAIR unchanged by construction AND re-measured (replay guard 14/14, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; verify_20260727T204103Z 20:41Z in-band). On the REAL committed series (69 points) the
  recommendation reads `baseline-valid` — the honest no-action state matching the recovered drift. Direct-to-
  main. `test_canonical_history.py` 13→19 (+6: one per code incl. a NON-VACUOUS direction control that a
  direction-blind recommendation would fail + a recovery-tolerant real-series code↔band coherence test); suite
  179→185. No Slack (read-only diagnostic + tests, moves no score, digest already sent Cycle 38 16:13Z, not a new
  window at 21:17Z). First duty: no open peer-gated PR (verified []); infra health check ran first — runner
  HEALTHY (verify_20260727T204103Z, 20:41Z, ~37 min old, +39.4 in-band); git realigned to origin/main 4b1d1e3.
  Next cycle takes READOUT. Follow-up (queued P2 READOUT): surface `recapture` on `canonical-history.html`
  (Cycle-40 page) — the same terminal→HTML deferral the battery diagnostics took.
  Cycle 44 READOUT (the Cycle-43 re-capture DECISION surfaced on `canonical-history.html` — the last
  terminal→HTML gap for the drift arc): `scorecard._write_canonical_history_page` gains a "Re-capture
  decision" card driven off `hist.recapture` (computed in `summarize`, Cycle 43) — the recommendation
  label (`ch._REC_LABEL`) + full reason, rendered whenever there is a reading (any code but the
  `REC_NO_DATA` sentinel). New `_HISTORY_REC_COLOR` colours the label chip by code, REUSING the band inks
  so the surface reads as one system (green `baseline-valid` no-action / amber `wait`+`defer` hold / red
  `recapture-candidate` a `[LOCAL]` re-capture candidate / neutral `review`); NEVER colour-alone — label
  text + full reason always render alongside. Card states in prose that re-capture is a DECISION not an
  action (moving the pinned baseline is a `[LOCAL]`, comparability-affecting step). Closes the same
  deferral the battery diagnostics took (per_kind 10→12, between_kind 18→20, NA-naming 25→28), now for
  the Cycles-36→43 drift arc (trend+band+sustained+pillar+side/cause were on the page; the DECISION they
  feed was terminal-only). Display-only: `git diff --name-only` = scorecard.py + test_readout.py ONLY;
  scoring.py/rubric/probes/fetch/protocols/battery/offering/behavioral/canonical_history byte-for-byte
  untouched (verified empty diff) → rubric stays v0.7, canonical PAIR unchanged by construction AND
  re-measured (replay guard 14/14, 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260727T215839Z 21:58Z
  in-band live-corroborates). Reference-pair hosts as DATA (same engineering-history category as
  rubric.html, out of scope for the wording scanner; `test_readout_wording` unchanged/green). LIVE page
  off the committed 69-point series reads `baseline-valid` (green) — the honest no-action state matching
  the recovered/stable drift. Direct-to-main. `test_readout.py` 29→31 (+recapture-DEFER render on the
  drifting series; +NON-VACUOUS data-driven control — in-band renders `baseline valid`, NOT the DEFER
  label); suite 185→187. No Slack (display-only, moves no score, digest already sent Cycle 38 16:13Z,
  not a new window at ~22:2xZ). First duty: no open peer-gated PR (verified []); infra health check ran
  first — runner HEALTHY (verify_20260727T215839Z, 21:58Z, fresh, +39.4 in-band). Next cycle takes METHOD.
  Cycle 45 METHOD (the divergence band's noise assumption made a MEASURED, guarded number — the first
  variance/calibration guard in the repo): the drift arc (Cycles 36→44) rests on the bands
  `_BAND_IN=2.0`/`_BAND_DRIFT=8.0`, ASSUMED constants justified only by the docstring's "within ordinary
  static/live jitter" prose with NO test validating them against the series' actual observed noise —
  a distinct KIND of rigor (all prior arc work was diagnostics, none calibration-validation). New
  read-only `NoiseFloor` + `noise_floor(points, baseline)` (`asrs/canonical_history.py`) measures the
  AT-REST dispersion of the delta over the readings the band already calls in-band
  (`|delta-baseline|<=_BAND_IN`): `n_in_band`, population `stddev`, `max_abs_divergence`; properties
  `deterministic` (σ+worst|div| ≤ `_NOISE_EPS=1e-6`) and `band_well_separated` (3σ fits `_BAND_IN` →
  noise can't be misread as drift; False = TOO TIGHT). Wired into `summarize` as
  `CanonicalHistory.noise_floor` (None <2 in-band, honest-None); `noise floor:` render line. THE FINDING
  on the committed 72-point series: all **68 in-band re-scores reproduce +39.4 EXACTLY** (σ=0.00, worst
  |div|=0.00, deterministic) — the static canonical re-score is deterministic at rest, so the in-band
  band demonstrably absorbs real-world site TRANSIENTS (the 4 OOB readings 3.9/30.1/32.6, the 07-27 `.com`
  outage), NOT measurement noise; the docstring's bare "ordinary jitter" claim is now a measured fact.
  Read-only diagnostic: `git diff --name-only` = canonical_history.py + test ONLY; scoring.py/rubric/
  probes/fetch/protocols/battery/offering/behavioral/scorecard byte-for-byte untouched → rubric stays
  v0.7, canonical PAIR unchanged by construction AND re-measured (replay guard 14/14, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; verify_20260727T224106Z 22:41Z in-band). Vendor-neutral (imports no scoring code;
  reference-pair hosts as DATA). Direct-to-main. `test_canonical_history.py` 19→24 (+5: real-series
  deterministic finding; calibration validation both directions — 3σ fits the band AND real transients
  are signal-not-noise; NON-VACUOUS synthetic-jitter σ>0; too-tight-band alarm makes band_well_separated
  non-vacuous; honest-None <2 in-band); suite 187→192 (test_free_tier 11/11 after
  `pip install -r requirements.txt` closes the known eth-account env gap). No Slack (METHOD tests +
  read-only diagnostic, moves no score, digest already sent Cycle 38 16:13Z, not a new window at ~23:1xZ).
  First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260727T224106Z, 22:41Z, ~31 min old, +39.4 in-band); git reset to origin/main 5411e2b. Next
  cycle takes COVERAGE.
- **LIVE CANONICAL DRIFT (open, for the next post-16:00 UTC digest) — surfaced by the Cycle-36 history readout.**
  The live canonical delta held **+39.4** (46.1 F / 85.5 B) for days through `verify_20260727T054339Z`, then MOVED:
  07:40Z fire driftflight.com collapsed to 50.0 F (delta +3.9 — transient error crawl, transactability CANT_TEST /
  legibility 0), recovering to 76.2 C (09:51Z, +30.1) and **78.7 C (13:41Z, +32.6)**. Current `.com` state:
  transactability RECOVERED to 87.5 (= baseline) but **legibility fell 90.9 → 63.6**, and pillars still fluctuate
  fire-to-fire → a REAL-WORLD site change (deploy / intermittent availability), NOT a code regression. drift-flight.org
  flat at 46.1 F throughout — the delta narrowed because the RAILS side softened, not the no-rails side improving. The
  committed fixtures still pin 46.1/85.5/+39.4 so the in-cloud replay guard is green and the PAIR is unchanged BY
  CONSTRUCTION; this is a LIVE-signal divergence the fixture guard is (correctly) blind to. Read it live any cycle:
  `python -m asrs canonical-history`. Decisions deferred until the site settles: (a) whether to re-capture the canonical
  fixture (moves the pinned baseline — [LOCAL], deliberately NOT while fluctuating); (b) pillar-level attribution in the
  readout (name WHICH pillar drove the move — here `.com` legibility). To be flagged in the next daily digest.
  UPDATE (Cycle 37, METHOD): pillar-level attribution (b) is now COMPUTED — `asrs canonical-history` prints
  `attribution (vs last in-band 2026-07-27T05:43Z): driftflight.com legibility fell 90.9 → 63.6 (-27.3) — the
  largest pillar move`, so the "which pillar" fact is read live off the committed series, not hand-written.
  Decision (a) — canonical fixture re-capture — remains deferred [LOCAL] until the site reads in-band-stable at a
  new level (do NOT re-capture while fluctuating).
  UPDATE (Cycle 39, TRUTH): the SIDE-and-direction of the drift is now COMPUTED too — `asrs canonical-history`
  prints `driver: driftflight.com overall fell -6.8 — the gap narrowed because the with-rails reference SOFTENED
  (a real-world site change), not because the no-rails side gained capability — the pinned fixture still
  represents the true gap` (`reference_degraded=True`). This is the decision-relevant read for (a): the gap
  narrowed from the RAILS side softening, NOT the no-rails floor rising, so the pinned fixture still represents
  the true capability gap → re-capture stays deferred until the site recovers or settles durably at a new level.
  The drift is now fully diagnosed in-cloud off the committed series: band + sustained run + PILLAR (Cycle 37,
  `.com` legibility) + SIDE/direction (this cycle).
  FLAGGED in the 2026-07-27T16:13Z daily digest (Cycle 38, first cycle after 16:00 UTC). Live state at that fire:
  `.com` 78.7 C, delta +32.6, DRIFTING (3 consecutive out-of-band re-scores; `.com` legibility 90.9 → 63.6 the named
  mover), `.org` flat at 46.1 F — the delta narrowed because the RAILS side softened, a real-world site change, not a
  code regression; committed fixtures still pin +39.4 so the replay guard is (correctly) green. Decision (a) still
  deferred [LOCAL] until stable; will re-flag in the next digest if still open.
  UPDATE (Cycle 41, 2026-07-27 ~19:30Z): **DRIFT RECOVERED / IN-BAND.** `verify_20260727T184100Z` (18:41Z) reads
  driftflight.com back at **85.5 B** — legibility RECOVERED 63.6 → 90.9 and transactability 87.5, both at the pinned
  baseline — so the live delta is **+39.4** in-band again (drift-flight.org flat at 46.1 F throughout). The site
  change was TRANSIENT (a real-world deploy/availability blip), not a durable regression, which VINDICATES the
  Cycle-39 decision to keep the fixture pinned (`reference_degraded=True` said the with-rails side softened; it has
  now un-softened). Decision (a) [LOCAL] canonical fixture re-capture: NO ACTION needed — the site returned to the
  pinned level, so the committed +39.4 baseline still represents the true capability gap. This note is CLOSED unless
  the live series diverges again; a positive (not flag) mention for the next digest.
- Rubric: **v0.7 on main** (PR #3 MERGED 2026-07-23T14:45:30Z, merge commit 72a2e5b —
  merged EXTERNALLY during the Cycle-14 fire (operator/active consent), pre-empting the
  pre-merge review, which converted to cloud Cycle 15's post-merge retain-or-revert sanity
  check → RETAIN; the merge commit carries a peer-gate verdict). v0.7 requires a VALIDATED
  ACP/UCP manifest for commerce-protocol partial credit (kills the bare-200 false positive;
  see the Cycle-14 note below). INDEPENDENTLY RE-VERIFIED LIVE 2026-07-23T15:43Z (local
  fire, the queued post-merge `[LOCAL]` live re-score): both canonical domains re-scored
  LIVE on v0.7 — 46.1 F / 85.5 B, delta +39.4 unchanged, reports embed rubric "0.7", NO
  `commerce-protocol-*` false positive on either (.org no-agent-native-payment / .com
  x402-live), example.com spot-check clean (22.5 F, no spurious commerce credit).
  PRIOR: v0.6 (PR #2 MERGED 2026-07-23T~09:47Z, merge commit 8fe9f46,
  clean fast-forward) broadened the env-block classifier to recognize
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
- Methodology page (Cycle 16, READOUT): `scorecard._write_methodology_page(out_dir)` renders
  `methodology.html` — the "read the paper" doc behind the rubric page (long-standing P2). Ten
  sections explain the MEASUREMENT SEMANTICS: capability lens; five pillars + weights; pillar/
  overall aggregation + renormalization; FAIL vs CANT_TEST (evidence-of-absence scores 0 in the
  denominator vs absence-of-evidence excluded from both numerator+denominator); NOT SCORABLE vs
  an F (N/A when no pillar observable); attribution honesty (agent-side hosting block → hosted-
  agent-reachability, site-side 403/CF/CAPTCHA/429/WAF → site evidence); shopper+trust panels +
  refusal semantics (directed-refusal caps, warnings only deduct); reproducibility (trials/
  verdict-stability/quotability); grade bands + caps; the $0 free-tier probe; versioned
  comparability + evidence. `build_scorecard` publishes it next to every card alongside
  `rubric.html`; cross-linked both ways (card footer → methodology + rubric; rubric page →
  methodology; methodology → rubric + back-to-card). Weights/caps/grade-bands pulled LIVE from
  `load_rubric()` (nothing hardcoded → reflows on any version bump, can't drift). Display-only:
  scoring.py/rubric/probes byte-for-byte untouched → rubric stays v0.6→**v0.7** unchanged,
  canonical delta unchanged by construction; direct-to-main. `tests/test_readout.py` 12 → 15
  (+3: page-written+covers-semantics, tracks-live-rubric, build_scorecard-publishes+links);
  suite 82 → 85.
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
- Fetch record/replay (Cycle 15, TRUTH): `asrs/fetch.py` `FetchContext` grew a faithful
  record/replay capability — `save_fixture(path)` serializes the per-`(method,url,ua)`
  response cache to JSON, `from_fixture(path)` reconstructs a `replay=True` context that
  serves recorded `FetchResult`s byte-identically and returns a clean `replay-miss` (status
  None, error set) on any unrecorded request WITHOUT touching the network. This is the
  enabling infra for the loop's standing open question ("offline regression tests as the
  in-cloud proxy" for the network-blocked canonical re-score): a canonical-pair fixture
  captured [LOCAL] once can be re-scored in-cloud EVERY cycle as a deterministic executable
  guard, replacing the per-cycle prose "delta unchanged by construction" argument. NOT a
  scoring-semantics change — `asrs/scoring.py` + `rubric/` byte-for-byte untouched, `replay`
  defaults False so every live/static path is byte-identical (canonical delta unchanged by
  construction); direct-to-main. `tests/test_fetch_replay.py` (3/3, new): round-trip
  fidelity, clean replay-miss (GET+POST), and an END-TO-END proxy replaying a recorded x402
  handshake through the REAL `protocols.run` → `x402-live` PASS 8.0 vs a bare homepage →
  `no-agent-native-payment` FAIL 0.0 (the 8.0 capability delta pinned offline). Suite
  79 → 82. NEXT: [LOCAL] capture `fixtures/canonical/{drift-flight.org,driftflight.com}.json`,
  then a cloud cycle wires `test_canonical_replay.py` asserting 46.1 F / 85.5 B / +39.4 on v0.7.
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
  RE-CONFIRMED DOWN Cycle 15 (15:18Z): newest STILL verify_20260723T040757Z, now **~11.2h
  old**; still before 16:00 UTC (this fire 15:18Z) so no digest yet — the next fire after
  16:00 UTC carries the digest and MUST flag the runner-down + the queued [LOCAL] v0.7 live
  re-score. NOTE: the Cycle-15 record/replay infra is the durable fix for this class of pain
  — once a canonical fixture is captured [LOCAL], the in-cloud canonical re-score no longer
  depends on the launchd runner being up at all.
  RE-CONFIRMED LIVE + RUNNER STILL DOWN (local fire 2026-07-23T15:43Z): the queued [LOCAL]
  v0.7 live re-score above is now DONE — canonical delta **+39.4** measured LIVE on v0.7
  (46.1 F / 85.5 B, both HTTP 200) as the PR #3 post-merge re-score; the merged
  commerce-manifest tightening moved no canonical score (monotone non-increasing by
  construction AND measured). Newest verify artifact STILL verify_20260723T040757Z (04:07Z,
  rubric 0.5), now **~11.6h old**; no :41 artifact 05:00–15:00Z. This fire (15:43Z) is
  ~17 min BEFORE 16:00 UTC → the down-runner flag + v0.7 delta trend fold into the next
  post-16:00 Slack daily digest (first cycle after 16:00 UTC), not yet due.
  RE-CONFIRMED DOWN + FLAGGED Cycle 16 (16:11Z, first cycle after 16:00 UTC): newest STILL
  verify_20260723T040757Z, now **~12.1h old**. Daily digest DM SENT this fire per comms
  policy — carries the runner-down flag AND the still-queued [LOCAL] canonical-fixture
  capture. Next live canonical signal depends on the launchd :41 runner being restarted or a
  manual local fire.
  RE-CONFIRMED DOWN Cycle 17 (17:15Z): newest STILL verify_20260723T040757Z, now ~13.1h old.
  Already flagged in Cycle 16's digest; folds into the next post-16:00-UTC digest if still down.
  RE-CONFIRMED DOWN Cycle 18 (18:18Z): newest STILL verify_20260723T040757Z, now ~14.2h old.
  Already flagged (Cycle 16 digest); the Cycle-17 replay guard means the in-cloud canonical signal
  no longer depends on it. Folds into the next post-16:00-UTC digest if still down at that fire.
  **RUNNER RECOVERED Cycle 19 (19:12Z).** Root cause was FIXED on main (commit 5f4e4c0,
  `loop: fix verify-floor path bug + self-healing law`, authored 11:50 local): the pinned
  `local_verify.py` derived REPO from `__file__` → resolved to `~/.local` when pinned, so every
  :41 fire git-pulled in a non-repo, failed silently, and wrote failure artifacts to `~/.local/runs/`
  with zero log output — the 15h silent outage. Fix: repo path from `ASRS_REPO` env (default
  `~/github/agentic-readiness`) + hard is-a-repo check, per-fire heartbeat logging (silence now
  impossible), crash wrapper that always leaves an artifact, pinned copy resynced. The runner is
  HEARTBEATING again: newest artifact `verify_20260723T184927Z.json` (18:49Z) is ~23 min old at
  this fire — well under 6h. Live delta on it: 46.1 F / 85.5 B / +39.4, matching the in-cloud replay
  guard. No further flag needed (self-healed on main, logged there); the runner-down thread is
  CLOSED. NOTE: even with the runner back, the Cycle-17 replay guard remains the primary in-cloud
  canonical signal — the runner is now the FRESH-recapture path for legitimate version-bump score
  moves, not the per-cycle regression check.
  NOTE: the Cycle-17 canonical replay guard (`tests/test_canonical_replay.py`) now runs the
  canonical re-score OFFLINE in-cloud every cycle from the committed fixtures — the in-cloud
  regression signal no longer depends on the launchd runner at all; the runner remains only for
  a FRESH live re-capture when a version bump legitimately moves a canonical score.
  RUNNER STALL WATCH (Cycle 29, 05:12Z): newest artifact STILL `verify_20260724T004105Z` (00:41Z,
  46.1 F / 85.5 B / +39.4) — now ~4h31m old, STILL UNDER the 6h floor, but the :41 fires at
  01/02/03/04:41Z produced NO artifact (4 consecutive gaps — the fresh stall Cycle 28 flagged). At
  the next fire the 00:41Z artifact is ~5.5h; the fire after, >6h → if still gapped THEN, this
  crosses the floor: flag the runner in STATE + fold into the post-16:00 UTC digest. The Cycle-17
  replay guard is the primary in-cloud canonical signal regardless, so no work is blocked.
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
- Open PRs: **NONE.** PR #4 `loop/na-aware-battery-aggregation` (Cycle 25, METHOD, sensitive
  class: battery aggregation-semantics — NA-aware exclusion + `battery_semantics_version` b1) was
  **MERGED Cycle 26 (2026-07-24T02:12Z, merge commit bec1dc0)** as the first-duty peer-gate review.
  SURVIVED fresh-context adversarial review: all four checklist items re-derived independently
  (profile=None byte-for-byte pre-brick-3, pinned; NA keys only on `profile.unclaimed` ⊆ ARCHETYPES
  → non-canonical kinds never NA, vendor-neutral; replay guard 8/8 delta unchanged = battery
  decoupled from scoring; battery-semantics version b1 not rubric = correct, battery feeds no score);
  non-vacuous (spread-change >1e-6 pinned); suite 115/115 on branch. No CI on repo. Was Slack-flagged
  at open (veto visibility, not approval). (A concurrent local fire `5ddb89a` read bec1dc0 as an
  "external merge" needing a future post-merge sanity check — SUPERSEDED: bec1dc0 was Cycle 26's own
  mandated fresh-context review-then-merge, the normal peer-gate flow; nothing pending. See LOG Cycle
  26 reconciliation.) https://github.com/jnakagawa/agentic-readiness/pull/4
  PRIOR (all closed): PR #3
  `loop/commerce-manifest-validation` (Cycle 14, COVERAGE, sensitive class: partial-credit
  rule + rubric v0.6→v0.7) was **MERGED EXTERNALLY** 2026-07-23T14:45:30Z (commit 72a2e5b)
  — an operator merged it directly during the SAME cloud fire that opened it, BEFORE the
  mandated next-cycle fresh-context adversarial review could run (the Cycle-9/PR-#2
  pattern). An external merge is ACTIVE consent (stronger than veto-silence), so not a
  bypass on the loop's part. Because the pre-merge review was pre-empted, it converted to a
  POST-merge duty, now FULLY DISCHARGED across two complementary fires:
  **(a) OFFLINE — Cycle 15 (first duty): fresh-context adversarial sanity check of v0.7
  SURVIVED → RETAIN** — vendor-neutral (`_parse_commerce_manifest` keys only on protocol
  STRUCTURE, no vendor/domain string), direction monotone non-increasing (only the bare-200
  false positive loses credit), `$0`-only intact (parser only GETs), test coverage complete
  (`test_protocols.py` 7/7), canonical delta UNCHANGED by COMMITTED evidence (.org report
  `x402_probe` FAIL 0.0 → `_commerce_protocol_evidence` already None under v0.6, so v0.7
  still None; .com earns x402-live before the commerce branch). See LOG Cycle 15.
  **(b) LIVE — local fire 2026-07-23T15:43Z: the queued P0 [LOCAL] live v0.7 canonical
  re-score DISCHARGED** — 46.1 F / 85.5 B, delta +39.4 unchanged on v0.7, reports embed
  rubric "0.7", NO `commerce-protocol-*` false positive on either canonical domain (.org
  no-agent-native-payment / .com x402-live), example.com spot-check clean (22.5 F). Suite
  79/79 green pre-flight. Evidence:
  `runs/local/merge_verify_pr3_v07_driftflight{org,com}_20260723T154332Z.json`. See LOG
  (Local cycle — 15:43Z). The Cycle-15 record/replay infra remains the path to making this
  a permanent in-cloud offline guard once the canonical fixture is captured [LOCAL].
  https://github.com/jnakagawa/agentic-readiness/pull/3
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
