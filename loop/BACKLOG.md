# Backlog (prioritized; prune every cycle)

`[LOCAL]` = needs Jonah's machine (codex CLI / zero CLI / paid probes) —
design in-cloud, execute locally.

## P0


- **[LOCAL] Post-merge live verification of the PR #147 `_ENV_BLOCK_RE` near-miss fix** (METHOD /
  attribution honesty, invariant #4). PR #147 was adversarially reviewed + SELF-MERGED Cycle 285 (cloud,
  merge `60c1a0f`) — the deterministic half is DONE (independent differential leak scan over all 19 committed
  transcripts flips EXACTLY driftflight.com codex t2, zero collateral; committed re-aggregation
  `runs/local/env_block_nearmiss_reaggregate_20260806T075510Z.json` confirms WITH-side `bhv_found_product`
  valid_runs 3→2, PASS, reachability blocked 1→2). What REMAINS is the live confirmation the cloud can't run:
  re-run `compare drift-flight.org driftflight.com --behavioral --trials 2 --models claude,codex` on Jonah's
  machine and confirm the SHIPPED code now records `driftflight.com valid_runs=2` (own-tool codex refusals
  routed to reachability, not scored as site evidence) and a wider behavioral delta than the pre-fix +34.8.
  Static $0 (no signing). See LOG Cycle 285 (review+merge) / Cycle 284 (fix) / Cycle 282 (RESULT 4, origin).
  SCOPE follow-up (future, carefully-guarded proposal only): the SECOND missed sentence in the same transcript
  — *"…classified driftflight.com as unsafe and blocked access."* — is a genuine own-tool block but in the
  ambiguous reputation-"unsafe" vocabulary (test-#8 family); attempt it ONLY with a disambiguating own-apparatus
  SUBJECT anchor so a site-side WAF "flagged unsafe" is never excused.

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

- **[LOCAL] Strengthen the UNDER-COVERED archetypes (service_booking / data_retrieval / physical_good)**
  (COVERAGE, opened Cycle 164). PROGRESS — Cycle 248 (2026-08-05, COVERAGE, in-cloud, direct-to-main,
  score-neutral): **service_booking got its FIRST genuinely-distinct NEW capability signal** mined from the
  acuityscheduling.com anchor — `manage-booking` (reschedule/cancel an EXISTING booking, the LIFECYCLE-MANAGEMENT
  "operate without a human" leg, the service_booking analog of metered_api's Cycle-233 `key-rotation`), DISTINCT
  from all 5 existing signals (book/appointment/reservation/schedule/availability all describe MAKING a booking),
  precision-guarded (never a bare verb — reschedule/cancel must sit ≤40 chars from an unambiguous booking noun
  appointment/booking/reservation, so bare-cancel subscription/order/job + sales-CTA-reschedule demo/call/meeting
  trip nothing), firing NON-VACUOUSLY on the committed anchor (service_booking strength 3→4, claimed SET+ORDER
  [subscription, service_booking, metered_api] UNCHANGED) and ABSENT on all 7 other fixtures. `test_offering.py`
  97→99 (precision-synthetic + real-captured guard pair) + `_ISOLATION_EVIDENCE` row (bank 69→70) + the anchor
  genuine-label maintenance contract split into `_BOOKING_CREATE_LABELS` ∪ `_BOOKING_MANAGE_LABELS`. So
  service_booking now grows 5→6 signals. UPDATE Cycle 252 (COVERAGE, in-cloud, direct-to-main, score-neutral):
  the REMINDER/NOTIFICATION candidate below is now SHIPPED as `booking-notification` (the booking is automatically
  CONFIRMED + reminded WITHOUT a human — the completion-acknowledgment leg, the service_booking analog of
  metered_api's `payment-receipt`), fired NON-VACUOUSLY on the committed anchor (52 hits), ABSENT on all 7 others
  incl. the canonical pair, precision-guarded (confirm/remind token ≤40 chars from a booking noun, or the fixed
  "appointment reminder(s)" collocation) against bare order/UI-confirmation + restock/system-notification +
  broad-reminder collisions. `test_offering.py` 99→101 + `_ISOLATION_EVIDENCE` row + `_BOOKING_NOTIFY_LABELS` leg
  (f). So service_booking now grows 6→7 signals. REMAINING in-cloud service_booking candidates: an INTAKE-FORM
  data-collection control ("custom intake forms" — the collect-what-the-job-needs leg) or a WAITLIST/slot capability
  ("Clients join a waitlist for fully booked times"), each IF precision-guardable against generic marketing prose.
  UPDATE Cycle 256 (COVERAGE, in-cloud, direct-to-main, score-neutral): INTAKE-FORM is now SHIPPED as `intake-form`
  (the DATA-COLLECTION PRECONDITION "collect what the job needs / provision without a human" leg, distinct from
  create/manage/notify), 39 `\bintake forms?\b` hits on the anchor, ABSENT on all 7 others incl. the canonical pair,
  guarded against bare "form"/bare "intake" (fixed collocation only). `test_offering.py` 101->103 + isolation row
  (bank 71->72) + `_BOOKING_INTAKE_LABELS` leg (g). service_booking grows 7->8. The last thin candidate WAITLIST was
  IMAGE-ONLY on the acuity anchor (`waitlist.png`, no prose) -> deferred to a [LOCAL] richer-booking-fixture capture.
  UPDATE Cycle 273 (2026-08-06, COVERAGE, LOCAL, direct-to-main, score-neutral): that [LOCAL] capture is DONE — a
  SECOND service_booking anchor `fixtures/canonical/simplybook.me.json` landed (an agent-native multi-archetype
  booking platform claiming {service_booking, subscription, metered_api}, agent surfaces under `agents.simplybook.me/*`)
  whose committed prose carries a genuine WAITING-LIST capability (73 `waiting list` occurrences: "group booking,
  classes, tickets & events, waiting list, recurring services" + a homepage "Waiting list" feature). Captured via
  `experiments/capture_offering_fixture` (66 entries, honest-replay verified byte-faithful, inv #4); pinned by
  `test_simplybook_anchor_offering` (test_offering_canonical 68->69) which also asserts the `waiting list` prose is
  present (future-mine evidence) + installs the `_ALL_SERVICE_BOOKING_LABELS` maintenance hook; simplybook.me added
  to `_CLASSIFICATION_ONLY` in test_canonical_replay (50 full-scorer misses -> quarantined from scoring). So the
  WAITLIST mine SHIPPED Cycle 281 (2026-08-06, COVERAGE, cloud, direct-to-main, score-neutral): `waitlist` added to
  service_booking (8->9) — the scarcity-QUEUE "join a queue for a fully-booked slot / provision without a human under
  contention" leg, DISTINCT from create/manage/notify/intake. Precision-guarded (NEVER a bare token — requires a
  BOOKING NOUN appointment/booking/reservation/slot within a <=40-char same-clause window either order), so the SaaS
  "join our early-access waitlist" growth CTA dodges. Fires 26 spans on simplybook.me, 0 on all TEN other fixtures —
  crucially 0 on acuity (its waitlist is image-only `waitlist.png`, no booking-noun context) and 0 on the canonical
  pair (service_booking NA there by construction). Tests: `test_service_booking_waitlist_precision_synthetic`
  (5 positives fire / 6 noise dodge) + `test_waitlist_fires_on_real_captured_surfaces` (real simplybook fires; acuity
  does NOT; pair+retail+null+api ABSENT) → test_offering 109->111; `_ALL_SERVICE_BOOKING_LABELS` + `_BOOKING2_DISTINCT_LEGS`
  + `_ISOLATION_EVIDENCE` updated → test_offering_canonical 70/70. So service_booking is now well-mined across ALL FIVE
  lifecycle legs (create/manage/notify/intake/waitlist) on both anchors. See LOG Cycle 281.
  See LOG Cycle 248/252/256/273/281.
  EARLIER — Cycle 243 (2026-08-05, COVERAGE, in-cloud, direct-to-main,
  score-neutral): **data_retrieval got its FIRST genuinely-distinct NEW capability signal** mined from the
  fresh ipinfo.io anchor — `batch-retrieval` (BATCH/BULK data retrieval, the "complete the job AT SCALE" leg,
  the data_retrieval analog of metered_api's Cycle-230 `concurrency-limit`), DISTINCT from all 5 single-item
  existing signals, precision-guarded against the metered_api compute-batch and retail-bulk collision families,
  firing NON-VACUOUSLY on the committed ipinfo.io `/docs` and ABSENT on all 7 other fixtures (data_retrieval
  strength 4→5, claimed SET unchanged, no reorder). `test_offering.py` 95→97 (precision-synthetic +
  real-captured guard pair) + `_ISOLATION_EVIDENCE` row + `_DATA_RETRIEVAL_LABELS` maintenance-contract update.
  So data_retrieval now grows from 5→6 signals. UPDATE Cycle 272 (COVERAGE, in-cloud, direct-to-main,
  score-neutral): the Cycle-243 "next hypothesis" DATASET-FORMAT / DOWNLOAD-CONTRACT signal is now SHIPPED as
  `dataset-format` (the delivery-format leg — the site delivers data as a DOWNLOADABLE DATASET/DATABASE in a
  NAMED machine-consumable format CSV/JSON/MMDB/Parquet/NDJSON/GeoJSON, so an agent picks the ingest format;
  DISTINCT from `dataset` existence + `batch-retrieval` call-shape). Three anchored branches (format-named-AS-
  downloadable-database; "data/database/dataset download" NOUN compound sentence-bounded beside a format/
  "formats"; "downloadable dataset" in a named format) — NEVER a bare CSV/JSON/Parquet token, guarding the
  worst minefield in the bank (JSON responses, `*.json` specs/manifests, `Content-Type: application/json`,
  dashboard "export to CSV"). Fires NON-VACUOUSLY on ipinfo.io (homepage "data downloads in different formats"
  + /docs "Database Downloads … in CSV, JSON, MMDB, or Parquet formats"), ABSENT on all 8 others, claimed
  SET+ORDER byte-identical (ipinfo already claims data_retrieval → deepens only). `test_offering.py` 105→107
  (precision-synthetic 9-fire/10-dodge + real-captured) + `_ISOLATION_EVIDENCE` row + `_DATA_RETRIEVAL_LABELS`
  update. So data_retrieval grows 6→7 signals. NEXT in-cloud data_retrieval candidate (Cycle-272 LOG "next
  hypothesis"): a DATA-FRESHNESS / update-cadence signal (ipinfo /docs "Daily Data Refresh" — the "how current
  is the corpus" leg, distinct from delivery format) IF precision-guardable against generic "fresh"/"updated"
  marketing prose. See LOG Cycle 272. **service_booking's anchor
  (acuityscheduling.com) got its FIRST distinct signal `manage-booking` in Cycle 248** (above) — it still carries
  un-mined capabilities distinct from create+manage (reminder/notification, intake-form, waitlist). See LOG Cycle 243.
  EARLIER — LOCAL Cycle 242 (2026-08-05): **data_retrieval unblocked
  in-cloud** — its first committed fixture (`fixtures/canonical/ipinfo.io.json`, a real IP-data storefront claiming
  {metered_api, data_retrieval, subscription, digital_good} with data_retrieval on ALL FOUR bank signals
  lookup/enrich/dataset/data-service) landed this fire, the direct mirror of Cycle 240's service_booking capture, pinned
  by `test_data_retrieval_anchor_offering` + `test_data_retrieval_partition_tracks_storefront_type`. So BOTH previously
  zero-evidence thin archetypes now have anchors — an in-cloud COVERAGE cycle can now mine data_retrieval (a
  records-lookup response contract, a dataset-download/licence control — ipinfo /docs carries dataset formats
  CSV/MMDB/JSON/Parquet + a batch-enrichment API) OR service_booking (a confirmation/booking-reference or
  reschedule/availability-check control) for a genuinely distinct capability leg against REAL evidence, the way Cycle 164
  did for digital_good. See LOG Cycle 242. EARLIER — LOCAL Cycle 240: **service_booking** unblocked via
  `fixtures/canonical/acuityscheduling.com.json` (a real appointment-booking storefront claiming {subscription,
  service_booking, metered_api}). Remaining thin gap: **physical_good** got its FIRST post-purchase signal in
  Cycle 266 — `order-tracking` (the order-lifecycle "operate without a human" leg, mined from allbirds' llms.txt
  "track orders" / "Order tracking" + moleskine's "Check Your Order Status"), DISTINCT from `fulfillment`'s static
  "tracking number" datum. So physical_good grows 9→10. REMAINING in-cloud physical_good candidate (Cycle-266 LOG
  "next hypothesis"): a RETURNS-WINDOW / return-authorization leg (the return-lifecycle capability, distinct from
  the static `returns` policy-page signal) IF committed retail prose (allbirds/moleskine) carries a machine-readable
  return window; secondary the agent-native RETAIL rail surfaces (UCP `/.well-known/ucp`, MCP) as classification
  evidence distinct from driftflight. The offering signal bank is metered_api-HEAVY: metered_api 26, digital_good
  11 (post-Cycle-164 `variant-selection`), physical_good 10 (post-Cycle-266 `order-tracking`), subscription 10
  (post-Cycle-276 `subscription-cancel`), service_booking 9 (post-Cycle-281 `waitlist`), data_retrieval 7
  (post-Cycle-272 `dataset-format`). NOTE (superseded by Cycles 240/242/243): the
  claim below that service_booking/data_retrieval "CANNOT be strengthened non-vacuously in-cloud" held only until their
  first committed anchors landed (acuityscheduling.com / ipinfo.io) — data_retrieval has since gained `batch-retrieval`
  against real evidence; service_booking's anchor is still un-mined. The three thin archetypes originally could not be
  strengthened non-vacuously in-cloud — no committed
  fixture CLAIMED service_booking or data_retrieval at all, and the only physical_good fixture
  (books.toscrape.com) is a ~3.4KB retail catalog whose fulfillment prose is already fully mined
  (add-to-cart / stock / priced-listing). To close the imbalance and move the north-star's "many storefront
  types" axis, capture LIVE fixtures from real storefronts that genuinely claim these archetypes —
  e.g. a booking/reservation service (restaurant/salon/clinic booking API), a data-retrieval/enrichment
  API (records lookup / dataset feed), and a MIXED storefront (retail + API) to exercise multi-archetype
  classification — via `asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json` (static
  $0), then mine each for genuinely distinct, precision-guarded capability signals the same way Cycle 164
  did for digital_good. Off the scoring path, score-neutral; each new signal needs the isolation-matrix
  entry + a precision/real-evidence guard pair. Prefer the booking fixture first (service_booking is tied
  for thinnest and has zero committed evidence). UPDATE Cycle 186 (COVERAGE, in-cloud, direct-to-main): the
  data_retrieval PRECISION half is DONE — `enrich` and `dataset`, the two cheapest bare-word signals, are
  now provenance/marketing-collision-hardened (a naive "trained on a dataset" / "an enriching partnership"
  no longer conjures the archetype), pinned by `test_data_retrieval_precision_synthetic` +
  `..._is_canonical_invariant_on_real_fixtures`. This does NOT close the item: the thin banks still want
  GENUINE NEW signals from real fixtures ([LOCAL], unchanged). NOTE the mirror gap this surfaced —
  service_booking's `book (a|an|your)` signal was UN-guarded and false-positived on the ubiquitous B2B
  sales CTA "book a demo" / "book a call" / "book a walkthrough" (conjuring service_booking on a pure-API
  storefront). DONE Cycle 190 (COVERAGE, in-cloud, direct-to-main, score-neutral): the guard
  `\bbook (?:a|an|your) (?!(?:demo|call|walk[- ]?through|briefing|meeting)s?\b)\w+` now excludes those
  unambiguous sales-CTA objects while KEEPING genuine bookable services (table/room/appointment/session/
  class/consultation) and `book now`/`book online`/`booking`; `test_service_booking_book_precision_synthetic`
  (8 genuine positives fire / 7 book-a-<CTA> negatives dodge, incl. the "book your demos" plural + hyphenated
  "walk-through") + canonical-invariant by construction (narrowing only removes matches; service_booking stays
  NA on all 5 fixtures per `test_offering_canonical::_MUST_BE_NA`, 58/58); the surface-read-order test that
  had inadvertently ENCODED this false positive ("Book a demo appointment") was corrected to genuine
  two-signal booking prose. DONE Cycle 194 (COVERAGE, in-cloud, direct-to-main, score-neutral): the
  service_booking `schedule` signal — the DIRECT SIBLING of `book`, with the identical unfixed sales-CTA
  gap — is now guarded. Bare `\bschedule (a|an|your)\b` fired on the same "schedule a demo / call /
  meeting / walkthrough / briefing" family (verified live at fire start); new form
  `\bschedule (?:a|an|your) (?!(?:demo|call|walk[- ]?through|briefing|meeting)s?\b)\w+` excludes them
  while keeping genuine scheduled services (session/consultation/table/pickup/visit/fitting);
  `test_service_booking_schedule_precision_synthetic` (6 schedule-ONLY positives fire / 7 CTA negatives
  dodge) + canonical-invariant by construction (no fixture contains "schedule"; service_booking NA on all
  5, 58/58). DONE Cycle 198 (COVERAGE, in-cloud, direct-to-main, score-neutral): the data_retrieval
  `lookup` signal — the last cheap bare-word minefield across the two thinnest archetypes — is now guarded.
  Bare `\blook ?ups?\b` false-positived on the data-structure / internals vocabulary that saturates API &
  engineering docs ("lookup table", "hash / cache / index / key / symbol / array / in-memory lookup" —
  internal mechanism / performance descriptors, verified firing live at fire start); new form
  `(?<!hash )(?<!cache )(?<!index )(?<!table )(?<!array )(?<!key )(?<!symbol )(?<!memory )\blook ?ups?\b(?!\s*tables?\b)`
  (fixed-width negative lookbehinds strip the leading data-structure qualifiers + a trailing lookahead
  strips "lookup table(s)") excludes them while KEEPING every genuine record-retrieval sense
  (phone/reverse-IP/address/domain/company/WHOIS lookup, "look up a customer record");
  `test_data_retrieval_lookup_precision_synthetic` (8 record-lookup positives fire / 9 internals negatives
  dodge, incl. the discriminating pair "look up a table reservation" FIRES / "lookup table" DODGES) +
  canonical-invariant by construction (no fixture contains "lookup"; data_retrieval NA on all 5, and the
  isolation matrix's "a phone lookup service" still fires). The bare-word minefields across the two THINNEST
  archetypes are now ALL precision-guarded: `enrich`/`dataset` (data_retrieval, Cycle 186), `book` +
  `schedule` (service_booking, Cycles 190/194), `lookup` (data_retrieval, Cycle 198). DONE Cycle 202
  (COVERAGE, in-cloud, direct-to-main, score-neutral): subscription's bare `recurring` — the cheapest
  subscription signal, false-positiving on broad-English "recurring theme/dream/nightmare/bug/character/
  meeting/pattern" prose (each CONJURING a subscription claim on a non-billing storefront) — is now
  POSITIVE-anchored (mirroring enrich/dataset, since its false-positive family is open-ended general
  English, not a bounded CTA/internals set): fires only on a BILLING object after "recurring" (billing/
  payment/charge/subscription/invoice/fee/plan/price/dues/membership ±cadence) or a billing verb in a short
  window ("billed/charged/invoiced ... on a recurring basis"); `test_subscription_recurring_precision_synthetic`
  (10 recurring-ONLY positives fire non-vacuously / 13 non-billing negatives dodge, incl. "recurring
  revenue/costs" + the no-verb "recurring basis") + canonical-invariant by construction (no fixture contains
  "recurring"; subscription claimed on the pair via `subscription`/`per-month`/`annual-billing`). The
  bare-word minefields across the two THINNEST archetypes AND subscription's cheapest signal are now ALL
  guarded. Next in-cloud precision candidate is a metered_api bare-word audit (largest bank, 26 signals,
  never swept for broad-English collisions). This does NOT close the parent item — the thin banks still
  want GENUINE NEW signals from real fixtures ([LOCAL], unchanged). DONE Cycle 206 (COVERAGE, in-cloud,
  direct-to-main, score-neutral): the metered_api bare-word audit is COMPLETE — `usage-based`'s bare
  `\bmetered\b` (the largest bank's last un-swept broad-English collision: metered parking / water /
  electricity / -dose / postage / verse / "a metered approach") is now anchored to a BILLING/USAGE/API
  context (billing object after it / "metered per <unit>" / "metered and charged" / usage-call-request
  "is/are metered"); `usage-based` + `overage` stay bare (already billing-specific). LOOKAHEAD-anchored so
  the matched span stays exactly `metered` → the canonical evidence QUOTE is byte-identical (verified on
  both domains) → canonical-invariant by construction. `test_usage_based_metered_precision_synthetic` (12
  metered-billing positives fire usage-based / 10 broad-English "metered <noun>" negatives claim nothing).
  With this, the bare-word minefields are now ALL precision-guarded across EVERY archetype bank
  (enrich/dataset/lookup + subscription's recurring + service_booking's book/schedule + metered_api's
  metered) — the in-cloud precision-audit frontier is EXHAUSTED; further COVERAGE wanting new SIGNALS (not
  precision) needs real fixtures ([LOCAL]). Does NOT close the parent item — the thin banks still want
  GENUINE NEW signals from real fixtures ([LOCAL], unchanged). QUALIFICATION Cycle 226 (COVERAGE, in-cloud,
  direct-to-main, score-neutral): the "further new SIGNALS need [LOCAL] fixtures" claim held only for the THIN
  archetypes — it was too strong for the DEEP banks. Cycle 226 added `payment-challenge-retry` to metered_api
  (the agent-native payment CHALLENGE-SETTLE-RETRY handshake — the request/response FLOW an agent executes,
  distinct from the STATIC rail facts x402/agent-payment-rail/payment-receipt/reserve-and-settle) firing
  NON-VACUOUSLY on the COMMITTED driftflight.com agent docs and ABSENT on drift-flight.org (the with/no-rails
  capability-gap echo), canonical SETS+ORDER invariant on all 5. So the in-cloud new-signal lever is NOT fully
  exhausted for the deep banks: a committed fixture can still carry a documented CAPABILITY not yet mapped to a
  signal (audit metered_api/digital_good/subscription committed prose for uncaptured FLOW/lifecycle/safety
  capabilities before assuming [LOCAL] is required). The thin banks (service_booking/data_retrieval/physical_good)
  DO still need real fixtures ([LOCAL], unchanged) — no committed fixture claims them to mine.
  QUALIFICATION Cycle 230 (COVERAGE, in-cloud, direct-to-main, score-neutral): the deep-bank new-signal lever produced
  again — `concurrency-limit` added to metered_api (the CONCURRENCY CEILING + queue-depth backpressure: "2 concurrent
  renders … Bursts beyond the limit queue rather than fail; the `x-df-queue-depth` response header reports the current
  queue" on BOTH canonical `/docs`), a capability distinct from `rate-limited`'s TEMPORAL axis (requests-per-time) —
  the orthogonal PARALLELISM axis (jobs-in-flight-at-once), the "complete the job AT SCALE" leg. Fires NON-VACUOUSLY on
  the committed pair (a SHARED capability like output-resolution/variant-selection, both already claim metered_api → no
  reorder), ABSENT on api/retail/null; precision-synthetic 11-fire/10-dodge + real-captured guard + isolation-matrix
  entry (suite 478→480). So the deep banks STILL have uncaptured committed capabilities to mine in-cloud — NEXT
  candidate (Cycle-230 LOG "next hypothesis"): a concurrency/quota ERROR-RECOVERY response (`409 concurrency_exceeded` /
  a `Retry-After` naming the concurrency wall) distinct from generic `error-contract`, IF committed prose carries it.
  The thin banks (service_booking/data_retrieval/physical_good) DO still need real fixtures ([LOCAL], unchanged).
  QUALIFICATION Cycle 233 (COVERAGE, in-cloud, direct-to-main, score-neutral): the Cycle-230/231 concurrency/quota
  ERROR-RECOVERY candidate was CHECKED against committed prose and is NOT present (error table 400/401/403/429/502 with
  429=`allowance_exhausted` already-covered quota exhaustion; concurrency bursts QUEUE rather than fail per
  `concurrency-limit`, no 409/`Retry-After`) → DROPPED per the no-vacuous-signal discipline. Auditing the same committed
  /docs surfaced a DIFFERENT uncaptured deep-bank capability: `key-rotation` added to metered_api — the CREDENTIAL
  LIFECYCLE / KILL-SWITCH ("Rotate any key from the dashboard; old keys are revoked immediately." on BOTH canonical
  /docs), the "operate safely without a human" leg, distinct from `api-auth` (present a held credential) and
  `self-provisioning` (obtain one without a human, the lifecycle START) — this is the lifecycle END. Precision NAMES a
  key in a rotation/kill sense so the 401 error row "the key is unknown or revoked" (on both /docs) does NOT fire it
  (signal-level discriminator: 401 fires api-auth but not key-rotation). Fires NON-VACUOUSLY on the pair (SHARED
  credential-safety capability, both already metered_api → no reorder), ABSENT on api/retail/null; precision-synthetic
  8-fire/8-dodge + 401-discriminator + real-captured guard + isolation-matrix entry (suite 481→483). So the deep-bank
  new-signal lever produced AGAIN in-cloud. NEXT candidate (Cycle-233 LOG "next hypothesis"): a credential-SCOPE /
  least-privilege capability (a key scoped to a plan/tier/model) distinct from api-auth, IF committed prose carries it
  (verify "df_test_ sandbox, no quota use" is already `test-mode` first). The thin banks
  (service_booking/data_retrieval/physical_good) DO still need real fixtures ([LOCAL], unchanged).

- **[LOCAL] Validate the typographic-encoding robustness fixes on REAL surfaces (line-wrap + intra-word hyphen + non-HTML entity + invisible line-break control)**
  (COVERAGE, follow-up to Cycles 178 + 214 + 218 + 222). FOUR sibling in-cloud fixes are exercised only SYNTHETICALLY today
  because the committed evidence is not reflowed/dashed/entity-encoded/invisible-char-laden: (a) Cycle 178 made `classify_offering` collapse
  whitespace runs before scanning so literal-space signals (`\bfree shipping\b`, `\bper month\b`, `\badd to
  cart\b`, ~35 total) survive an 80-column line-wrap ("free\nshipping"); (b) Cycle 214 added `_HYPHEN_NORMALIZE`
  folding the intra-word hyphen family (U+2011 non-breaking hyphen, en/figure dash, minus) to ASCII `-` so
  hyphenated compounds (`pay-as-you-go`, `pay-per-call`, `per-generation`) survive a publisher's non-breaking
  hyphen — the canonical pair is invariant by construction (its only Unicode dash is the deliberately-excluded em
  dash); (c) Cycle 218 extended HTML-entity decoding to the NON-HTML surface branch (`_html.unescape` on
  llms.txt / JSON manifest / ai-plugin / A2A card / OpenAPI, not just the strip_html HTML branch) so an
  entity-encoded phrase (`add&nbsp;to&nbsp;cart`, `pay&#8209;per&#8209;call`) on a non-HTML surface no longer
  drops the claim — canonical no-op by construction (all 74 committed non-HTML canonical surfaces are
  unescape-identical); (d) Cycle 222 added `_INVISIBLE_STRIP` DELETING the invisible line-break controls a
  justification / auto-hyphenation engine interleaves mid-word (soft hyphen U+00AD `sub­scrip­tion`, zero-width
  space U+200B, word joiner U+2060, BOM U+FEFF — category Cf, so neither the reflow `\s` collapse nor the visible
  hyphen fold reaches them; ZWNJ/ZWJ U+200C/U+200D deliberately excluded) — canonical no-op by construction (0 of
  5 fixtures carry any stripped char). Capture a fixture from a real storefront whose `llms.txt` / markdown `/docs` genuinely
  (a) line-wraps across a capability phrase AND/OR (b) typesets a billing compound with a non-breaking/
  typographic hyphen AND/OR (c) serves an entity-encoded capability phrase on a NON-HTML surface (a JSON
  manifest/ai-plugin `description` field HTML-escaped by a framework, or an llms.txt exported from HTML)
  AND/OR (d) carries an auto-hyphenated / soft-hyphenated capability word or a leading BOM (a CMS-exported
  `/pricing` or `/docs` page is the likeliest to carry U+00AD; an exported llms.txt often opens with a U+FEFF BOM)
  (`asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json`, static $0 → [LOCAL]), then add a
  read-live guard asserting the wrapped/dashed/entity-encoded/invisible-char'd phrase's archetype still classifies (the
  real-evidence mirror of the four synthetic guards `test_classification_is_whitespace_reflow_invariant` +
  `test_classification_is_intra_word_hyphen_invariant` + `test_classification_is_non_html_surface_entity_invariant` +
  `test_classification_is_invisible_formatting_invariant`).
  Off the scoring path, score-neutral. Naturally folds into the thin-archetype / render / structured-catalog live
  captures above (any real llms.txt-bearing site will do; a `/pricing` page with `per‑month` non-breaking hyphens
  is especially likely to exercise the hyphen fold; a JSON manifest field is the most likely to carry entities; a
  CMS-exported `/docs` or BOM-prefixed llms.txt is the likeliest to exercise the invisible-control strip).
  UPDATE Cycle 238 (TRUTH, LOCAL, direct-to-main, score-neutral): part (d) is PARTIALLY discharged on REAL evidence.
  The `www.moleskine.com` fixture captured this cycle (for the negative calibration anchor) carries a genuine ZWSP
  (U+200B) inside an `<img>` filename, so `test_classification_is_invisible_formatting_invariant`'s real-evidence
  half was converted from assert-absence (invariant BY CONSTRUCTION — no fixture carries a stripped char) to
  verify-invariance (BY VERIFICATION — classify each char-carrying fixture with `_INVISIBLE_STRIP` disabled vs
  shipped, assert identical archetypes/NA). moleskine now exercises that branch clean. BUT this is the HARMLESSNESS
  case only (the ZWSP sits in an image filename, NOT inside a capability signal), so the strip is proven a no-op on
  real evidence that INCIDENTALLY carries the char. The phrase-RESCUE case — an invisible control INSIDE a capability
  WORD such that the strip is LOAD-BEARING for a real claim — is still synthetic-only and remains the open [LOCAL]
  work here (as do reflow (a) / hyphen (b) / entity (c), all still synthetic).

- **[LOCAL] Capture a RENDER-generation digital_good fixture to validate the Cycle-168 descriptor branch on
  REAL evidence** (COVERAGE, follow-up to Cycle 168). `_digital_good_descriptor` (asrs/battery.py) now maps a
  render-EXCLUSIVE digital_good claim → "generated render", but the ONLY committed digital_good fixtures are
  the driftflight image pair (both fire BOTH `render` and `image`, so `image` wins by design) — the render
  branch is currently synthetic-test-only, exactly like the video/audio/art branches. Capture a fixture from
  a real render-generation storefront that claims digital_good via `render` WITHOUT an image/video/audio/art
  artifact noun (a 3D / architectural-viz / scene-render / video-render-farm API) via `asrs.cli score
  <domain> --record-fixture fixtures/canonical/<domain>.json` (static $0 → [LOCAL]), then add a read-live
  guard asserting `discover_offering → _digital_good_descriptor` yields "generated render" on real evidence
  (the render-branch mirror of the image branch's live validation). Off the scoring path, score-neutral.
  UPDATE Cycle 169 (TRUTH, direct-to-main): the in-cloud half of the render-branch validation is now DONE —
  `test_digital_good_descriptor_is_relabel_invariant_render` pins the branch's host/vendor identity-invariance
  on a synthetic render-exclusive claim (the sibling of the media/translation relabel guards). What remains
  HERE is strictly the REAL-evidence half — a live render-generation fixture — which stays `[LOCAL]` (the
  render branch is synthetic-test-only until a real fixture claims render WITHOUT an image/video/audio/art
  artifact noun).

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


- **[LOCAL] Re-capture canonical fixtures on any version-bump score move** (METHOD, standing
  maintenance for the Cycle-17 replay guard). `tests/test_canonical_replay.py` pins 46.1/85.5/
  +39.4 on v0.7. When a peer-gated scoring change LEGITIMATELY moves a canonical score, the
  guard will (correctly) go red until the fixtures are re-captured and EXPECTED updated in the
  SAME PR: `asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json` (LIVE,
  needs network → [LOCAL]), then update the numbers. This is not pending work — it is the
  documented upkeep step so a future cycle knows the red is intended, not a regression.


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
  PROGRESS — LOCAL Cycle 244 (2026-08-05, TRUTH, direct-to-main, score-neutral): the cadence re-run is DONE
  (prior dataset was ~8 days old) and BOTH increments advanced. (b) is now AUTOMATIC and no longer a manual
  step: `experiments/calibration_sweep.py` gained `_load_baseline` + `_compute_drift`, so every future run
  emits a `drift` block (per-domain overall Δ for domains scored in both datasets; scored↔not-scorable
  transitions reported separately per invariant #4; added/removed members listed) and prints a drift summary.
  (a) POPULATION broadened 14→16 (target 15–20 HIT) with two NEW storefront TYPES absent from it — `ipinfo.io`
  (`data-retrieval:api`, the Cycle-242 offering anchor) + `acuityscheduling.com` (`service-booking:saas`, the
  Cycle-240 anchor), both already reachability-validated. Latest dataset `runs/local/calibration_sweep_20260805T014754Z.json`
  (rubric v0.7): 15/16 scored, 1 not-scorable (rei.com, same as baseline), 0 error; **canonical pair byte-stable
  85.5 B / 46.1 F / +39.4** (regression signal unmoved); drift vs 2026-07-28 = 11/13 IDENTICAL over 8 days, 2
  moved (both upward, single-pillar): deepai.org +6.8 (all legibility 72.7→100.0), allbirds.com +5.0 (all trust
  33.3→60.0). This item STAYS OPEN as the standing cadence (re-run weekly; the drift block reads itself). NEXT
  broadening step toward the upper 15–20: a genuine ACP/UCP/MPP merchant or a 2nd x402-live site (both scarce —
  record reachability as its own signal). Off the scoring path, score-neutral (`git diff -- asrs/ rubric/`
  EMPTY; only `experiments/calibration_sweep.py`).
  PROGRESS — Cycle 245 (2026-08-05, TRUTH, cloud, direct-to-main, score-neutral): the Cycle-244 drift diff is now
  TEST-GUARDED — `tests/test_calibration_drift.py` (5 tests) pins `_compute_drift` against BOTH committed dated
  sweeps (real-evidence: 13 scored-in-both, 2 moved [deepai +6.8, allbirds +5.0], canonical pair delta 0.0 =
  the frozen +39.4 seen from the sweep, rei.com in neither list) AND a synthetic invariant-#4 negative control
  (a scored↔NOT SCORABLE flip lands in `status_changed`, never `moved`; a naive not-scorable-as-0.0 impl would
  report max_abs_delta 90.0, the guard pins 5.0 → leak caught numerically). So the drift signal is now trustworthy
  before the next cadence run reads it. NEW READOUT FOLLOW-UP (candidate below): the drift block is a [LOCAL]
  stderr readout only — surface the population + its cadence drift trend on the rubric/leaderboard page or card
  (which storefront TYPES scored, the drift trend) to turn the committed dataset into a citable readout.
  DONE — Cycle 246 (2026-08-05, READOUT, cloud, direct-to-main, score-neutral): the drift block is now a citable
  **Population drift** card on `calibration.html`. `scorecard._calibration_drift_card(drift)` (wired into
  `_write_calibration_page`) renders from the committed `sweep["drift"]`, all from data: baseline diffed against,
  summary (N/M moved, max|Δ|, K steady), a signed per-domain moved table (up green / down red), the canonical
  anchors' own Δ0.0 steadiness as the population echo of the frozen reference delta, and added/dropped members as
  membership (never averaged in). Attribution honesty is the load-bearing design: a scored↔not-scorable flip
  renders in a SEPARATE "Reachability changes" block, NOT a capability move, magnitude never a score Δ (invariant
  #4, test-pinned). Real render of the newest committed sweep: "2 of 13 moved (max|Δ| 6.8); 11 held steady" —
  deepai +6.8, allbirds +5.0, anchors Δ0.0, new: acuityscheduling.com + ipinfo.io. `test_readout.py` 80→83;
  score-neutral (`git diff -- asrs/scoring.py rubric/ fixtures/` EMPTY; replay guard 25/25, 46.1 F / 85.5 B /
  +39.4 UNMOVED). REMAINING READOUT candidate: the drift card is a
  SINGLE-cadence diff (this sweep vs the immediately prior); surface the drift TREND across ALL committed sweeps —
  a sparkline of the canonical anchors' overall across every dated dataset, the population analog of
  canonical-history.html's per-cycle trend. **DONE Cycle 279 (READOUT, cloud, direct-to-main, display-only,
  score-neutral):** `calibration.html` gains a **Reference-pair trend** card rendering the two canonical anchors'
  overall across all committed dated sweeps as a fixed-0–100 multi-series sparkline (`_load_all_calibration_sweeps`
  + `_anchor_trend_series` + `_anchor_trend_svg` + `_calibration_anchor_trend_card`, mirroring `_history_trend_svg`).
  Real render: the reference gap HELD at +39.4 across all 3 v0.7 sweeps (85.5 with-rails vs 46.1 no-rails). Invariant
  #2 (only newest-version sweeps plotted, older-version counted+named-omitted) + #4 (not-scorable reading = gap, never
  a fabricated 0) test-pinned with teeth; 5 new tests (test_readout 94→99); suite 35/35; scoring-path diff EMPTY;
  canonical replay 46.1 F / 85.5 B / +39.4 UNMOVED. NEXT READOUT candidates (new): a population-median/band overlay
  across sweeps (whole-cohort spread, not just the anchor pair) once ≥3 sweeps carry a stable non-anchor overlap; or
  a one-line gap-held/moved verdict badge on the main card. See LOG Cycle 279.
  PROGRESS — Cycle 278 (2026-08-06, TRUTH, LOCAL, direct-to-main, score-neutral): the cadence's increment (a)
  advanced again — POPULATION broadened 16→18 (deeper into the 15–20 target) with two more NEW storefront TYPES
  absent from every prior sweep: `simplybook.me` (`service-booking:platform`, the Cycle-273 offering anchor) +
  `polar.sh` (`subscription:mor-platform`, the Cycle-275 anchor). This completed a working-tree change left by a
  prior interrupted fire (the +8-line `POPULATION` broadening was already staged; nothing else). Latest dataset
  `runs/local/calibration_sweep_20260806T044352Z.json` (rubric v0.7): 17/18 scored, 1 not-scorable (rei.com,
  agent-UA-blocked, same as baseline), 0 error; **canonical pair byte-stable 85.5 B / 46.1 F / +39.4** (regression
  signal unmoved, concurs the 04:41Z verify floor); the two new members score simplybook.me 64.9 D / polar.sh
  70.3 C. Auto drift vs 2026-08-05 = 15/15 IDENTICAL over ~1 day (0 moved, max|Δ| 0.0), added [polar.sh,
  simplybook.me] as membership (never averaged). This item STAYS OPEN as the standing cadence. NEXT broadening
  step toward the ceiling: still a genuine ACP/UCP/MPP merchant or a 2nd x402-live site (both scarce — record
  reachability as its own signal). Off the scoring path, score-neutral (`git diff -- asrs/ rubric/` EMPTY; only
  `experiments/calibration_sweep.py` +8). See LOG Cycle 278.
  CROSS-PATH WELD — Cycle 283 (2026-08-06, TRUTH, cloud, direct-to-main, tests-only, score-neutral): the committed
  sweeps and the OFFLINE fixture-replay baseline were two independent measurement paths of the two canonical anchors
  that NOTHING coupled — now welded by `tests/test_calibration_anchor_agreement.py` (7 guards): every scored,
  same-version live anchor's `overall` must equal `test_canonical_replay.EXPECTED` (imported as the ONE source of
  truth → self-maintaining on a version-bump re-capture). REAL EVIDENCE: 3 committed v0.7 sweeps → 6 (sweep,anchor)
  pairs compared, 0 divergences, live com−org gap +39.4 on all three. TEETH: not-scorable anchor skipped not
  diverged (inv #4); an 85.5→70.0 drift caught as one divergence; a `0.8` sweep never diffed against v0.7 (inv #2).
  So a future live re-capture that drifts from the fixture floor (site changed → fixtures stale, or crawl unstable)
  is now a red test in EITHER direction — a 2nd independent witness for the canonical-delta check. Suite 36→37,
  scoring-path diff EMPTY, canonical 46.1/85.5/+39.4 unmoved. NEXT (TRUTH): widen the weld to a NON-anchor member
  once ≥2 committed sweeps share a stable reachable non-anchor scored under the same rubric AND a committed offline
  replay baseline exists for it (books.toscrape.com / ipinfo.io candidates — [LOCAL]-gated on that baseline landing).
  See LOG Cycle 283.

<!-- DONE Cycle 269 (2026-08-05 cloud) + MERGED same fire (external merge by owner):
     [PEER-GATE] Broaden `_ENV_BLOCK_RE` for codex's drifted own-tool refusal vocabulary.
     Shipped on branch loop/env-block-vocab-drift, PR #146 — three self-qualified alternatives
     (own browser gate / browser's own boundary / safety-controlled navigation layer), each with a
     negative lookahead `_NOT_SITE_ATTRIBUTED` rejecting site-side attribution; domain-dot-tolerant
     sentence-bounded gap; NEW test_attribution.py #12 (verbatim transcripts + v0.6 pre-broadening teeth
     + site-attributed/cross-sentence/example.com NOT-excused + denominator routing). PR MERGED
     externally (owner) the same fire; the peer-gate rule held (Cycle 269 did NOT self-merge). Post-merge
     verification on merged main 8c89718: 33/33 suites, attribution 12/12, replay 26/26 46.1/85.5/+39.4
     UNMOVED. test #8's pure-semantic reputation gap intentionally kept. Recorded in LOG Cycle 269 + git. -->

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
  UPDATE Cycle 268 (2026-08-05 local): the test-#8 fixture is UNPARKED. The 21:45Z + 20:45Z
  reachability re-runs (canonical domains now ~20d old) captured own-tool refusals whose vocabulary
  drifted OFF v0.6's "browser {security,safety} controls" — "Safety-controlled navigation … denied",
  "browser's site-permission boundary … denied", "web fetch … rejected as unsafe" — all AGENT-side
  (site HTTP 200, reached on sibling trials, example.com never gated) yet `_is_env_blocked`=False →
  the invariant-#4 leak is now LIVE on committed transcripts. The `_ENV_BLOCK_RE` broadening is
  therefore WARRANTED (no longer speculation) and split into its own peer-gated P0 item below. Note
  codex ALSO now REACHES the aged canonical .org on t2 → the reputation gate softened from the 07-23
  4/4 hard block, so this item's pre-fetched-content attribution fix is now needed LESS urgently
  (codex reaches on some trials); the `_ENV_BLOCK_RE` correctness fix is the priority.


- **[LOCAL] Fresh live 5-trial panel post-v0.6** (METHOD follow-up; the LIVE half
  remaining after Cycle 11 pinned the offline recompute). Re-run
  `experiments/trial_count_N.py` on a NEW drift-flight.org 5-trial panel and confirm
  the verdict-stability curve reads monotone/stable END-TO-END under merged v0.6 on
  fresh runs (not just recomputed from the 06:44Z artifact). Distinct value over the
  offline pin: catches any live env-block phrasing the fixture set doesn't cover.
  Budget: one panel (reuses the ONE-run N-curve harness).


- **[LOCAL] Cross-model panel-stability N-curve** (TRUTH/METHOD, remaining half of
  the trial-count item): the 07:50Z run measured claude-only reproducibility
  because codex env-blocked drift-flight.org on all 5 trials. The CROSS-MODEL
  agreement question (do claude and codex converge on the same verdict, and at
  what N) is unmeasured and BLOCKED on codex reachability — RE-CONFIRMED blocked
  at 11:42Z (codex gated 4/4 on BOTH canonical domains). UPDATE Cycle 268 (2026-08-05):
  codex reachability is now INTERMITTENTLY OPEN on the aged canonical pair — it REACHED
  drift-flight.org on t2 in BOTH 08-05 runs (20:45Z + 21:45Z) — so this P0 is PARTIALLY
  unblocked; `trial_count_N.py` can now sample codex-reachable trials on the aged .org,
  though cross-model verdict AGREEMENT still needs enough REACHED trials (t2-only today,
  ~1/2 reach rate). Do the "Build the codex
  control-storefront / pre-fetched-content attribution fix" item above FIRST, then
  re-run the nested-subsample harness on a domain codex can actually reach:
  ```
  git checkout main && git pull
  .venv/bin/python -m experiments.trial_count_N   # reuse the ONE-run N-curve harness
  # (edit DOMAIN to a codex-reachable storefront; ~5 codex + 5 claude, within budget)
  ```

## P1


- **[OBSERVATION — Cycle 267, UPDATED Cycles 271/274/277, CLOSED Cycle 280] Evidence-reproducibility: ALL host axes
  (in-cloud AND the [LOCAL] one) are now CLOSED — the family is FULLY SATURATED.** The committed `Report.to_json`
  evidence is proven invariant along every host axis a machine can vary: ARRIVAL-ORDER on the behavioral path (Cycles
  253/255/257/262 — every panel-arrival projection sorted); and on the static path, over the whole full-scorable
  fixture population (Cycle 274 broadened all three in-cloud axes from the pair to `acuityscheduling.com`/
  `books.toscrape.com`/`example.com`/`www.moleskine.com` + the pair), HASH-SEED (Cycle 267 —
  `test_hashseed_reproducibility.py`, 4 `PYTHONHASHSEED` values, teeth by a real set-leak mutation), TIMEZONE /
  wall-clock (Cycle 271 — `test_timezone_reproducibility.py`, 4 POSIX `TZ` strings
  `UTC0`/`IST-5:30`/`LINT-14`=+14/`AoE12`=-12, teeth by a real local-wall-clock leak), DEFAULT-ENCODING (Cycle 277 —
  `test_encoding_reproducibility.py`, explicit UTF-8 mode `PYTHONUTF8=1` vs a forced ASCII default `LC_ALL=C
  PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`, teeth by an IMPLICIT `open(path).read()` that succeeds under UTF-8 but raises
  `UnicodeDecodeError` under ASCII), and — the final, [LOCAL]-gated axis — SYSTEM-LOCALE (Cycle 280 —
  `tests/test_locale_reproducibility.py`, re-scores the population under C / `de_DE.UTF-8` / `tr_TR.UTF-8` with each
  child ACTIVATING the env locale via `setlocale(LC_ALL, "")` so `LC_NUMERIC` bites, teeth by a locale-AWARE
  `"{:n}".format(1234567)` = `1.234.567` under de_DE ≠ `1234567` under C vs the locale-INDEPENDENT `str()` identical
  across both). The locale suite GRACEFULLY SKIPS its three foreign-locale guards where the locales are absent (the
  cloud container — `setlocale` raises there per Cycle 277), while its two host-independent guards
  (child-scores-real-pipeline, population-is-replay-clean) run everywhere, so it exits 0 in-cloud AND does its real
  teeth-bearing work on the local runner (which has the locales). A future METHOD/TRUTH cycle should NOT add another
  host-environment reproducibility guard (arrival-order / hash-seed / timezone / encoding / locale) — the family is
  DONE. Reach instead for a genuinely NEW METHOD/TRUTH seam OFF host-environment reproducibility: **probe-order
  independence of the aggregate** (reverse/shuffle the probe list, assert the serialized report is invariant — a
  determinism property of the scorer's own composition, not the host) or **fixture-capture determinism** (two live
  captures of the same surface yield the same committed bytes modulo timestamps — the honest-replay property the
  offering captures already assert informally). Both are in-cloud-testable (no [LOCAL] gate).

- **[OBSERVATION — Cycle 185] Canonical-drift diagnostic family metamorphic axis is EXHAUSTED in-cloud.**
  With the Cycle-185 `test_attribution_stability_is_host_relabel_invariant`, every drift diagnostic now has a
  metamorphic guard: reflection magnitude/direction (Cycle-179ish `test_reflection_about_baseline_...`),
  cause-verdict host-relabel (Cycle 181), and attribution-stability host-relabel (Cycle 185); attribution and
  divergence-cause are additionally pinned on the real committed series. A future METHOD cycle should NOT add
  another relabel/reflection guard on this family (diminishing returns) — reach instead for a NEW diagnostic,
  a measurement-rigor refinement (e.g. a variance/trial-count method), or the offering-classifier precision
  guards. The substantive drift work (CHECK-level transactability-drop diagnosis + peer-gated re-baseline)
  stays `[LOCAL]` and is tracked in the P0 canonical-anchor item.


<!-- COVERAGE-IN-CLOUD EXHAUSTION (recorded Cycle 152; UPDATED Cycle 156 — reserve-and-settle was a second
     distinct signal found after this note, so the frontier is narrower now but was NOT fully dry): a broad
     capability-vocabulary sweep of the rich committed fixtures (drift pair + api.replicate.com) this cycle
     REJECTED as vacuous-or-colliding: (a) `overage`/quota-boundary billing — metered_api's `usage-based`
     regex ALREADY matches bare `\boverage\b`, so any overage prose already claims metered_api; a
     subscription "overage-rate" signal would break the Cycle-137 cross-signal isolation matrix AND be
     redundant (matches ⊂ usage-based's). (b) `SLA` — the 35 "SLA" hits on the drift pair are the `--slate`
     CSS color variable, NOT a service-level capability. (c) usage/balance-CHECK endpoint (GET /usage,
     /balance, remaining-quota read) — absent from every committed fixture. (d) billing-on-failure was the
     ONE genuinely distinct, non-colliding, non-vacuous capability found → SHIPPED as `failure-not-billed`
     (Cycle 152). The remaining in-cloud COVERAGE frontier on committed evidence is output FORMAT
     (false-positive minefield, deferred); everything else needs new [LOCAL] fixtures. -->

<!-- METHOD METAMORPHIC-GRID STATE (updated Cycle 159): CASING = COMPLETE across all four poles (Cycle 155);
     SURFACE-DEDUP now = org/com/machine (Cycle 159 added the metered_api /openapi.json pole,
     `test_offering_surface_dedup_invariance_machine`) and is COMPLETE on the poles where the mechanism
     exists — retail is STRUCTURALLY EXCLUDED (a single-surface homepage catalog has no `_SURFACE_DOCS` doc
     surface to mirror; `_doc_subdomain_surfaces` never mirrors the apex homepage). Cross-axis coverage map
     for a future METHOD rotation: (a) content-scale = org/com/retail (no MACHINE pole); (b) noise-surface =
     org/com/retail (no MACHINE pole); (c) casing = org/com/machine/retail (COMPLETE); (d) surface-dedup =
     org/com/machine (COMPLETE where mechanism exists); (e) surface-ORDER = org (+ per-signal cells) — extend
     to the machine/.com pole; (f) listing-order = priced_listing single cell / endpoint-order = metered_api
     single cell — mirror onto a SECOND signal/pole. Candidate open cells, smallest-meaningful-unit each:
     content-scale/noise-surface on the MACHINE pole; surface-ORDER on the machine or .com pole; a second
     listing-order/endpoint-order pole. Each needs the same pole-specific tooth care casing-retail /
     dedup-machine did — verify the load-bearing tooth EMPIRICALLY before writing (a single-surface pole
     breaks the >=2 reorder premise → use the count-increase + no-conjured-archetype teeth; a
     lowercase-authored-bank pole breaks the count-moves tooth → use the folding-essential form).
     UPDATE Cycle 163: content-scale MACHINE pole DONE (`test_offering_content_scale_invariance_machine`).
     UPDATE Cycle 167: a SECOND reading-layer axis, WHITESPACE, opened on the MACHINE pole
     (`test_offering_whitespace_invariance_machine`) — sibling of CASE. Established the axis is non-vacuous
     ONLY on the machine pole (the prose poles go through `strip_html`, which collapses whitespace before the
     matcher → a prose whitespace guard is VACUOUS; the raw `/openapi.json` spec is where `\s+`/`\s*`
     flexibility is load-bearing). So the whitespace axis is COMPLETE where the mechanism exists (machine
     only) — do NOT add prose/retail whitespace poles (they would be strip_html-enforced, not pattern-tested).
     Remaining smallest-unit open cells for a future METHOD rotation: (b) noise-surface MACHINE pole; (d)
     surface-dedup RETAIL is STRUCTURALLY EXCLUDED (no doc surface to mirror); surface-ORDER on the machine/.com
     pole; a second listing-order/endpoint-order pole. Each still needs the empirical pole-specific tooth check. -->

- **DONE (COVERAGE) — subscription-CANCEL signal, opened Cycle 146, CLOSED end-to-end.** Capture: LOCAL Cycle
  275 landed `fixtures/canonical/polar.sh.json` (a Merchant-of-Record billing platform with programmatic
  `cancel_at_period_end` / `/v1/subscriptions/` / Cancel-Revoke-Subscription prose, zero "cancel anytime" human
  marketing). Mine: cloud Cycle 276 added the `subscription-cancel` signal (subscription 9→10) — four anchored
  branches (`cancel_at_period_end` param / `subscription.canceled`/`.revoked` event / `subscriptions/{id}/cancel`
  endpoint / adjacent `cancel|revoke subscription(s)` operation), tightened vs the pointer to require ADJACENCY so
  simplybook.me's HUMAN "cancel or downgrade your subscription" dodges; empirical precision 86 spans on polar / 0
  elsewhere; NEW precision-synthetic + real-captured tests; score-neutral (off scoring path, 46.1/85.5/+39.4
  unmoved). See LOG Cycles 275+276. Follow-on candidate (a NEW item, not this one): subscription PAUSE/RESUME
  (`subscription.paused`/uncancel on the polar anchor), the suspend-without-terminating leg distinct from cancel,
  IF precision-guardable.


  <!-- OPEN COVERAGE FRONTIER (post-output-retention, in-cloud on committed evidence): the DIGITAL_GOOD bank
       is now DEEP — 11 signals (generation / generate-media / generations / render / translation /
       hosted-output / output-license / content-provenance / output-resolution + `output-retention`, Cycle
       150, the LIFECYCLE/delivery-window leg). subscription is well-covered (8 signals incl. plan-purchase,
       Cycle 146) with its COVERAGE(146)→TRUTH(147)→READOUT(148) arc CLOSED. The remaining IN-CLOUD
       strengthenable digital_good unit is output FORMAT (PNG/JPEG/MP4/WebP) — a false-positive minefield
       (badge SVGs, thumbnail JPGs, content-type headers everywhere in the fixtures), so it needs a genuinely
       distinct capability + precision-guarded evidence and is DEFERRED, not attempted. output-retention's
       RELABEL-INVARIANCE guard (the METHOD/TRUTH mirror of plan-purchase Cycle 147 / payment-receipt Cycle
       143) SHIPPED Cycle 151 (see the DONE note below). A
       subscription-CANCEL / lifecycle-management signal (agent bounds its own recurring spend) is
       [LOCAL]-blocked: the canonical `/cancellation` surface is NOT in any committed fixture (capture one
       [LOCAL] first). service_booking / data_retrieval new signals + the physical_good fulfillment leg stay
       [LOCAL]-blocked (no committed fixture claims them); ACP/UCP/MPP live handshakes + free-tier
       live-wiring stay [LOCAL]. -->

  


<!-- READOUT candidate (opened Cycle 215, for Cycle 216): surface the loader's EXCLUSION accounting in the
     drift block / `canonical_history.render` — e.g. "N readings; M excluded (k red-bench, j malformed)" — so
     the operator sees the drift series is FILTERED (per-side-not-ok + red-bench + malformed dropped), not raw.
     The READOUT mirror of Cycle 215's TRUTH guard (`_point_from_artifact` now drops tests_ok=False). Off the
     scoring path, display+tests only → score-neutral, direct-to-main. -->

  <!-- STANDING METHOD-hygiene note: `test_runner_registration.py` (Cycle 145) now fails loudly on any
       future defined-but-unregistered or ghost test, so an arc-closing leg can no longer silently skip
       its guard. No further work — this is the closed form of the hygiene concern. -->


- **[LOCAL] Capture a fixture that CLAIMS data_retrieval** (COVERAGE enabler, from
  Cycle 114's audit). **SERVICE_BOOKING HALF DONE — LOCAL Cycle 240 (2026-08-05T00:06Z, COVERAGE, direct-to-main,
  score-neutral): `fixtures/canonical/acuityscheduling.com.json` (NEW) is the FIRST committed fixture that CLAIMS
  service_booking** — a real appointment-booking storefront (claims {subscription, service_booking, metered_api};
  service_booking on 3 genuine signals book/appointment/schedule), chosen by a $0 static screen of 7 booking domains
  (`experiments/probe_service_booking_candidates.py`) that rejected cal.com (false data_retrieval on "deployment lookup"
  + noisy digital_good) and simplybook.me (soft-404 boilerplate). Pinned by `test_offering_canonical.py::
  test_service_booking_anchor_offering` + `...partition_tracks_storefront_type` (62→64). So a future in-cloud COVERAGE
  cycle CAN now add a genuinely distinct service_booking leg (confirmation/booking-reference or reschedule/availability
  control) against real evidence. See LOG Cycle 240. **REMAINING: data_retrieval still has ZERO committed evidence** —
  its 5 legs (enrich / dataset / lookup / data-service / query-records) still
  cannot get a NEW capability-worded signal added in-cloud, because NO
  committed fixture claims it (the canonical pair + api.replicate claim metered_api/subscription/
  digital_good; books.toscrape claims physical_good; example.com claims nothing). Adding a signal to a
  never-claimed archetype is UNVERIFIABLE here (a vacuous case — cannot prove it fires non-vacuously or is
  score-neutral). Capture a fixture LIVE from a real data-enrichment/lookup API (a records-enrichment or
  dataset-query service that genuinely claims data_retrieval) — via
  `asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json` (static $0, needs network →
  [LOCAL]). Then a future COVERAGE cycle can add ONE capability leg to the claimed archetype (e.g.
  data_retrieval: a `bulk-export`/structured-output-format or a `filter`/query-parameter leg) with the same
  non-vacuous read-live guard the metered_api signals got. Off the scoring path, score-neutral. NOTE (Cycle 240):
  the 7 booking domains screened for the service_booking capture (cal.com/cronofy/acuity/savvycal/setmore/
  fresha/simplybook) claim data_retrieval NOT at all (cal.com's was a FALSE `lookup` on "deployment lookup"), so
  a DEDICATED data-API domain is needed — screen records-enrichment / dataset-marketplace / reverse-lookup APIs
  (e.g. a WHOIS/company-enrichment or a dataset-feed service) with the same probe tool.


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

- **[in-cloud, COVERAGE] Mine the allbirds MIXED anchor for a NEW physical_good fulfillment leg** (from Cycle 261,
  the discharge above). `fixtures/canonical/www.allbirds.com.json` is now a committed MIXED retail+API anchor whose
  llms.txt carries genuine fulfillment prose ("Refund policy", "track orders", "shipping address", an agentic
  checkout flow) — the REAL evidence the thin physical_good bank (9 signals, only `free-shipping` + `shipping-noun`
  firing on allbirds) needs to grow ONE distinct, capability-worded fulfillment leg the metered_api way: an
  `order-tracking` / `order-status` signal (confirm fulfillment progress after purchase — distinct from
  `fulfillment`'s "tracking number") OR a `returns-window` signal (a genuine return/refund POLICY). NB a
  `shipping-address` leg is redundant (`shipping (address|cost|rates|options|...)` already exists). Precision:
  `returns` must NOT fire on "returns to the homepage"; `track` must name an ORDER, not a music track. Each new
  signal needs the isolation-matrix entry (`_ISOLATION_EVIDENCE`) + a precision-synthetic guard (positives fire /
  broad-English negatives dodge) + a real-captured guard (fires on allbirds, ABSENT on the API pair / booking /
  data / null fixtures) + the `_MIXED_PHYSICAL_LABELS` maintenance-contract update in test_offering_canonical.py.
  Off the scoring path, score-neutral. Prefer this over the still-thin service_booking WAITLIST candidate —
  physical_good is the thinnest archetype that now has an enriched anchor.


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


<!-- P1 FRONTIER (post-Cycle-97): the generate-media arc is now closed at ALL layers — SIGNAL (94),
     DESCRIPTOR (95), READOUT (96), and DESCRIPTOR-RELABEL-INVARIANCE (97). Next METHOD candidate is a fresh
     perturbation AXIS on the offering/battery path (label/scale) now the order- + relabel-invariance
     families are complete, OR a NEW archetype/signal (COVERAGE). Not yet a firm backlog item; promote when
     a concrete gap is identified. -->


<!-- P1 FRONTIER (post-Cycle-104): the test-mode arc is now closed at COVERAGE (102) / TRUTH-relabel (103)
     / READOUT (104) — the fifth metered_api leg to complete the full arc. The test-mode
     surface-read-ORDER-invariance METHOD guard was SUPERSEDED by Cycle 105's stronger whole-profile `.org`
     order guard (see the SUPERSEDED note below); the order-/relabel-invariance families are now COMPLETE
     across both canonical pair-halves. Next candidates are a NEW archetype/signal (COVERAGE) or a
     genuinely NEW perturbation axis (label/scale) on the offering/battery path. -->


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


<!-- P1 FRONTIER (post-Cycle-108): the metered_api COLLECTION-retrieval (`pagination`) arc is now closed at
     ALL layers — SIGNAL (C106), TRUTH-relabel (C107), READOUT (C108) — the sixth full metered_api arc. The
     order-/relabel-invariance families are complete across both canonical pair-halves. Remaining COVERAGE
     frontier is a NEW archetype/signal (the thin service_booking / data_retrieval banks need a fixture that
     CLAIMS them — [LOCAL] fixture capture — before any signal there is non-vacuous in-cloud). The fresh
     METHOD perturbation axis this note named (label/scale) was DISCHARGED Cycle 109 (content-SCALE
     invariance, PR #67) — see the INVARIANCE-FAMILIES-COMPLETE note above; the invariance families are now
     three-fold and pair-symmetric, so COVERAGE (a new archetype/signal) now outranks another offering-path
     METHOD mirror. ACP/UCP/MPP + free-tier live-wiring stays [LOCAL]. -->


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

- **Calibration leaderboard — terminal readout + per-segment summary** (READOUT, cloud-doable follow-ups to
  Cycle 76's `calibration.html`). Two small optional increments: (a) a `python -m asrs calibration` terminal
  command rendering the same newest committed sweep as a text leaderboard (mirrors the
  `canonical-history` terminal/HTML pairing); (b) a per-segment roll-up on the HTML page (median/spread of
  overall within each `segment`) so the reader sees the rails-anchor vs no-rails-retail vs control bands as
  aggregates, not just a flat ranking — most valuable once the population passes ~15 members. Both display-
  only, off the scoring path; render off `_load_calibration_sweep()`.
- **Attribution-stability HOST-RELABEL invariance guard** (METHOD, candidate opened Cycle 184). Cycle 183
  added `attribution_stability` (does the fingered drift pillar HOLD across the whole out-of-band run or
  WANDER?) and Cycle 184 surfaced it on the HTML card, but — unlike the divergence-cause prose, which got a
  host-relabel metamorphic guard in Cycle 181 — the stability computation + its terminal/HTML prose have no
  vendor-neutrality invariance guard. Add `test_attribution_stability_is_host_relabel_invariant`: relabel
  both `CANONICAL_*` host constants, rebuild the SAME structural stable/wandering scenario, and assert
  `stable`/`fingered`/`movers` (and the rendered STABLE/WANDERS prose modulo the substituted host token) are
  invariant — the sibling of `test_cause_verdict_prose_is_host_relabel_invariant`. Off the scoring path,
  tests-only, score-neutral, direct-to-main. A clean in-cloud METHOD unit for Cycle 185.
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

- **[LOCAL] Wall-clock A/B of the hermetic fix on the operator's real fleet** (METHOD, optional
  follow-up to the 08:52Z hermetic fix). This fire's live proof was the panel transcript's
  `mcp_servers == []`; a headless `-p` timing A/B could not reproduce the boot delta because that
  subprocess env surfaced `mcp_servers=[]` even pre-flag. When a full `--battery auto` acceptance
  rerun runs next, capture the per-panel wall time and confirm the ~1 min/panel MCP-boot savings
  the 10:13Z observation implied (folds into the acceptance-rerun P0; no new code — a timing note).

## P2


- **[CANDIDATE, COVERAGE/in-cloud] data_retrieval `lookup` false-positives on the generic "&lt;noun&gt; lookup"
  admin-search sense** (observation, LOCAL Cycle 240). While screening booking domains for the service_booking
  capture, cal.com's real llms-full.txt tripped a FALSE `data_retrieval` claim: the Cycle-198 `lookup` signal fired
  on "Self-hosted deployment **lookup**" (an internal admin/config search feature, NOT a records-retrieval OFFERING an
  agent buys). The Cycle-198 lookbehind bank strips the data-structure senses (hash/cache/index/table/array/key/symbol/
  memory lookup) but NOT the generic product/feature-search sense ("deployment lookup", plausibly "log lookup" /
  "config lookup" / "user lookup" in an admin UI). Since data_retrieval is one of the two tied-thinnest archetypes, a
  false claim does maximum damage (probes a booking/SaaS storefront with an irrelevant records-lookup intent). Extend
  the `lookup` precision — anchor to a genuine record-retrieval object (phone/email/company/domain/WHOIS/address/person
  record) or exclude the admin-feature qualifiers — pinned by a precision-synthetic test (deployment/config/log lookup
  DODGE, "look up a customer record" FIRES) + canonical-invariant by construction (no committed fixture contains
  "lookup"; acuity's data_retrieval already NA). In-cloud, off the scoring path, score-neutral. NOTE: this is a
  precision NARROWING — verify it does not drop the genuine data_retrieval evidence a future [LOCAL] data-API fixture
  will carry.


- **[LOCAL, OPEN QUESTION — Cycle 261] Overnight coverage while the machine sleeps.** The watchdog stops a suspended
  agent from WEDGING the loop, but it does not make launchd FIRE while the machine is asleep — so an overnight sleep
  still yields a legitimate gap in local `verify_*.json` (the cloud's in-cloud replay-by-construction remains the
  regression signal during that window, per playbook). NOT a bug (a closed laptop can't run jobs); noted so a future
  fire does not re-diagnose an expected overnight gap as a stall. If continuous overnight coverage is ever wanted, the
  durable lever is a `pmset repeat wake` schedule (system power config, outside the repo) — deliberately NOT done here.

- **[CANDIDATE, COVERAGE] subscription bare-`recurring` precision guard** (observation, carried from Cycle
  198). `\brecurring\b` false-positives on non-billing prose ("recurring theme", "recurring bug"); it is the
  next in-cloud thin-bank bare-word minefield after enrich/dataset/book/schedule/lookup. Needs a
  billing-context guard + a precision/canonical-invariant synthetic guard pair, same shape as Cycles
  186/190/194/198. In-cloud, off the scoring path, score-neutral.

- **[CANDIDATE, METHOD] Metamorphic grid — remaining axes/poles** (observation, Cycle 129;
  updated Cycle 133). A SIXTH axis now exists — TEXT-CASING invariance (Cycle 133,
  `test_offering_casing_invariance_org`/`_com`, `_assert_casing_invariance` + `_casing_struct`):
  uppercasing every surface body leaves the case-independent capability skeleton (archetypes ranked,
  NA complement, per-archetype strength + per-(label, surface) counts) identical, with load-bearing
  teeth (a fired signal's CASE-SENSITIVE count moves under uppercasing while its `re.IGNORECASE` count
  holds → a future signal added without `re.IGNORECASE` fails loudly). The intra-surface ORDER axis
  spans BOTH poles: retail listing-order on physical_good (Cycle 125,
  `test_offering_listing_order_invariance_priced_listing`) and endpoint-order on the metered_api
  MACHINE surface (Cycle 129, `test_offering_endpoint_order_invariance_metered_api`). The family also
  has relabel-invariance (signal-level ×8 metered_api + digital_good/subscription legs), content-scale,
  and noise-surface invariance across the org/com/retail poles. Open frontier for a future METHOD
  cycle: (a) content-scale or noise-surface invariance on the metered_api MACHINE surface (only the
  prose poles are covered); (b) a cross-SURFACE order axis — does the ORDER in which surfaces are read
  (homepage vs /openapi.json vs /llms.txt) move a multi-surface claim? (partially pinned by
  `test_offering_surface_order_invariance_*` on the org pole — extend to the machine pole); (c) casing
  invariance — the MACHINE pole is now DONE (Cycle 149, `test_offering_casing_invariance_machine`,
  metered_api `/openapi.json`, single-archetype via `_assert_casing_invariance(min_claimed=1)`, load-bearing
  `post-endpoint` `https?://` tooth); the RETAIL pole (physical_good) is the one remaining casing cell
  (Cycle 133 covered org/com prose only). NOTE the retail casing tooth is harder — physical_good prose
  nouns ("Add to basket", "£51.77") may not carry a naturally case-sensitive signal like the machine
  `https?://`, so its load-bearing tooth (b) needs verification (or a `min_claimed=1` single-archetype
  adaptation like the machine pole); (d) SURFACE-DEDUP invariance — DONE (already shipped as
  `test_offering_surface_dedup_invariance_org`/`_com`, registered in `main()`). [cross-signal
  PRECISION-ISOLATION — the sibling axis — SHIPPED Cycle 137: a full 56-signal /
  6-archetype matrix `test_cross_signal_archetype_isolation` + negative control in
  `tests/test_offering_canonical.py`, proving each signal's affirmative evidence claims EXACTLY its own
  archetype and leaks into no other, completeness-enforced.] All tests-only, off the scoring path,
  in-cloud-doable on committed fixtures.


<!-- DONE Cycle 270 (2026-08-05 cloud, READOUT, direct-to-main, display-only, score-neutral):
     [CANDIDATE, READOUT] HTML compare card — baseline-side payment badge (follow-up to Cycle 264).
     `_pillars(rep, baseline)` now ALSO surfaces the baseline side's payment corroboration on the
     transactability delta row (`base_corrob = _payment_corroboration(baseline)` when baseline present),
     as a visually-secondary `corrob baseline` badge — so the HTML compare card is symmetric with the
     terminal render_compare per-side annotation. Suppression guard held (a baseline with no valid panel
     adds no badge); baseline=None is a byte-for-byte no-op on single/static cards. test_readout.py +2
     (real-anchor non-vacuity + synthetic teeth/scoping/no-op), 33/33 suite green, 46.1/85.5/+39.4 UNMOVED.
     Recorded in LOG Cycle 270 + git. -->


- **[LOCAL / CANDIDATE, COVERAGE] Real-data non-vacuity leg for `seat-licensing`** (follow-up to Cycle 66).
  `tiered-volume` earned a real-captured non-vacuity test (fires on the committed driftflight.com
  homepage's "volume tiers" prose), but `seat-licensing` shipped with the SYNTHETIC precision battery
  ONLY — no committed fixture carries seat/per-user licensing prose. When a seat-priced SaaS storefront
  is captured (a real per-seat plan, e.g. via `asrs.cli score <domain> --record-fixture
  fixtures/canonical/<domain>.json` [LOCAL]), add a real-captured test mirroring
  `test_tiered_volume_fires_on_real_captured_billing_prose`. Low urgency; the synthetic battery already
  pins precision on the named traps.


  

- **[LOCAL] Re-capture `api.replicate.com` (+ `ipinfo.io`) full-score, THEN extend the population guards to a
  2nd API storefront** (TRUTH). REVISED Cycle 249 (2026-08-05, TRUTH, in-cloud, direct-to-main, tests-only,
  score-neutral): the "Cloud-doable from the committed fixture" claim was WRONG and is now DISPROVEN by
  measurement — `_score_fixture('api.replicate.com')` yields **10.80 with 35 replay-misses** (and `ipinfo.io`
  **40.30 with 46 misses**). Both fixtures were captured via the offering/battery CLASSIFICATION path, whose
  probe surface is a strict SUBSET of the full scoring path, so a full score-replay requests dozens of URLs the
  fixture never recorded (robots.txt, homepage under claudebot/gptbot UAs, the trust/legal surface sweep,
  sitemap, pricing.json/catalog.json, cross-domain review URLs) → misses. So neither can drive a replay-SCORE
  guard (`_CAPABILITY_SPECTRUM` / calibration) as a like-for-like re-score UNTIL re-captured full-score. This is
  now GUARDED in-cloud: `test_canonical_replay.py::test_committed_fixtures_are_partitioned_by_replay_integrity`
  partitions every committed fixture into `_REPLAY_CLEAN` (6, all verified 0-miss) vs `_CLASSIFICATION_ONLY`
  ({api.replicate.com, ipinfo.io}, quarantined) — a naive add to the spectrum now fails leg (b) with a clear
  "re-capture first" message instead of exploding every population guard with a cryptic miss.
  NEXT (needs Jonah's machine — outbound network): `asrs.cli score api.replicate.com --record-fixture
  fixtures/canonical/api.replicate.com.json` (and the same for ipinfo.io) to capture the FULL scoring surface;
  the re-captured fixture replays 0-miss by construction → the quarantine tripwire (leg c) reddens → PROMOTE the
  domain to `_REPLAY_CLEAN`, pin its overall/pillars/per-check statuses (an EXPECTED entry), then slot it into
  `_CAPABILITY_SPECTRUM` at its capability rung and re-derive guards 12/13/17/19 (the tail-index + per-rung
  inversion logic hard-codes the current 4-domain shape — inserting a 5th touches all four). Adds a SECOND
  API-storefront data point to the population, strengthening the ordering + earned-dominance claims beyond the
  single synthetic canonical pair. See LOG Cycle 249.


- **[LOCAL] Exercise a MULTI-cap-value grade cap on a real captured fixture** (METHOD, follow-up to Cycle 241,
  LOW urgency). Cycle 241 pins `caps_applied` order-invariance SYNTHETICALLY (no committed fixture binds a
  cap). If a real storefront ever earns a critical finding the rubric caps (e.g. a hostile robots/agent-block),
  capture it and add a read-live guard that a REAL binding cap reproduces the synthetic invariant — closing the
  latent-not-live gap the same way the transactability/legibility anchors were closed on real evidence.


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


- **[LOCAL] Eyeball the battery card on a real multi-kind report** (READOUT, Cycle 12
  follow-up): the HTML battery card now exists but has only ever rendered synthetic
  fixtures. When the [LOCAL] second cross_task_spread datapoint runs (below/P0), pass its
  report through `scorecard.build_scorecard` and confirm the per-intent grid + by-archetype
  rollup read correctly on real multi-kind data. No new code — a render + visual check.


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


- **Battery card between-pill: live-data eyeball** (READOUT, Cycle-20 follow-up): the between-archetype
  pill now renders but has only ever seen synthetic fixtures. When the [LOCAL] second cross_task_spread
  datapoint runs (P0), pass its report through `scorecard.build_scorecard` and confirm the between-pill
  + interpretation line read correctly on real multi-kind data. No new code — a render + visual check
  (fold into the existing "[LOCAL] Eyeball the battery card" item above).


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

- **Validate the drifting/diverged cutoffs against observed transient magnitudes** (METHOD,
  Cycle-45 follow-up): Cycle 45 measured the AT-REST noise floor (σ=0 → the in-band `_BAND_IN=2.0`
  band is well-separated from measurement noise). The `_BAND_DRIFT=8.0` cutoff that splits
  "drifting" from "diverged" is still an ASSUMED constant. Measure the distribution of the
  observed OUT-OF-BAND transient magnitudes (the committed series carries the 07-27 `.com`
  outage: |div| 3.9→? / 30.1 / 32.6) and check the drifting/diverged split is calibrated to real
  transient sizes rather than picked. Read-only diagnostic on `canonical_history`, score-neutral,
  direct-to-main. Honest caveat: only ~4 transients observed so far — a small sample; the guard
  should be a coherence check (all observed transients land in a sane band), not an over-fit.


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


- **Methodology page follow-ups** (READOUT, Cycle-16 follow-up): the methodology page exists
  and documents the semantics, but (a) it renders straight to `methodology.html` with no
  hosted deploy step of its own — fine while it ships next to the card; and (b) each scorecard
  check ROW still doesn't link to its evidence blob (the separate P2 "Evidence links on the
  card" item) nor to the relevant methodology section. DONE (the cap-chip half): Cycle 32
  (READOUT) anchor-linked a card's "Grade capped" chip to its methodology §8 cap row via the
  shared `scorecard._cap_anchor` (can't drift; `test_readout.py` 19→23 with a cannot-drift
  test, suite 133→137, replay guard 8/8 / +39.4). REMAINING: the per-check-ROW → evidence-blob /
  methodology-section link (folds into "Evidence links on the card"). No scoring semantics; direct-to-main.


- **[LOCAL] Runner robustness: don't merge stderr into the score-path arg** (METHOD,
  Cycle 13 follow-up — belt-and-suspenders after the source fix above). The Cycle-13 fix
  removed the coverage-warning SOURCE, so a normal static run's stderr is now clean and the
  `local_verify.py` re-score capture should succeed. But the runner is still fragile: it
  builds the score-path from captured output, so ANY future stderr line (a genuine coverage
  WARNING, a probe-crash line, a deprecation) would re-break it. Harden the runner to read
  the score JSON from a known path / stdout-only channel rather than parsing mixed
  stdout+stderr. Needs the runner restarted first (currently DOWN, >9h). Execute [LOCAL] on
  Jonah's machine.
