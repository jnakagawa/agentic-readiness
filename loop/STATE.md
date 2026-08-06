# Loop state

- Cycle counter: 281
- CYCLE 281 — 2026-08-06T06:2xZ (COVERAGE, cloud, direct-to-main, score-neutral). FIRST duty (infra health +
  peer-gate review): `list_pull_requests` state=open → `[]` (no open peer-gated PR). Cloud started detached at
  origin/main `3a31524` with local `main` at stale `3e318f1` (Cycle-276 tip); realigned local `main` to
  origin/main (benign, HEAD already matched, no history rewrite). **INFRA HEALTHY:** newest verify by FILENAME
  `runs/local/verify_20260806T054102Z.json` (05:41Z, tests_ok=true, 46.1 F / 85.5 B / +39.4), ~37min old at fire
  (06:18Z 08-06), well inside the 6h floor; :41 cadence holding (03:41Z→04:41Z→05:41Z) → RUNNER-HEALTH WATCH
  NORMAL. Bench up (venv+pip); full suite 36/36 green before the change. **TRACK:** cloud pointer COVERAGE next
  (Cycle 279 READOUT → COVERAGE); highest unblocked = the `waitlist` signal on the simplybook.me anchor, named
  NEXT-COVERAGE since Cycle 273 and unblocked in-cloud since that fire's real waiting-list-prose capture (the
  Cycle-256 candidate was parked on acuity's image-only `waitlist.png`). **IMPROVEMENT (COVERAGE — service_booking
  8→9, the scarcity-queue leg):** NEW `waitlist` signal — the FIFTH distinct service_booking leg beyond create
  (book/appointment/reservation/schedule/availability), manage-booking, booking-notification, intake-form: "join a
  queue for a fully-booked slot / provision without a human under contention". PRECISION-CRITICAL (bare
  waitlist/waiting-list is the ubiquitous SaaS growth CTA "join our early-access waitlist"): NEVER a bare token —
  requires a BOOKING NOUN (appointment/booking/reservation/slot) within a ≤40-char same-clause window either order.
  **EMPIRICAL:** fires 26 spans on simplybook.me, 0 on all TEN other fixtures — crucially 0 on acuity (image-only
  waitlist.png, no booking-noun context) and 0 on the canonical pair → service_booking stays NA there by
  construction. Tests: NEW `test_service_booking_waitlist_precision_synthetic` (5 booking-context positives fire /
  6 early-access/beta/newsletter/webinar/demo noise dodge) + NEW `test_waitlist_fires_on_real_captured_surfaces`
  (real discover_offering on simplybook fires w/ quote; acuity does NOT fire; pair+retail+null+api ABSENT, claimed
  SET+ORDER pinned) → test_offering 109→111. `_ALL_SERVICE_BOOKING_LABELS` += waitlist + `_BOOKING2_DISTINCT_LEGS`
  += waitlist + `_ISOLATION_EVIDENCE["waitlist"]` (claims exactly service_booking) → test_offering_canonical 70/70.
  Bank now metered_api 26 / digital_good 11 / physical_good 10 / subscription 10 / service_booking 9 /
  data_retrieval 7. **SCORE-NEUTRAL:** classifier OFF the scoring path (grep-verified: offering.py not imported by
  scoring.py/report.py/probes); scoring-path diff EMPTY (only asrs/offering.py + 2 tests); suite 36/36 green.
  **CANONICAL UNMOVED:** in-fire replay 26/26, 46.1 F / 85.5 B / +39.4 (concurs 05:41Z floor); service_booking NA
  on both canonical fixtures → a service_booking signal cannot move either score. Invariants #1 ($0 — classifier
  regex + read-only tests)–#5 all held; zero codex, zero paid ops. NO DM (score-neutral COVERAGE, not
  sensitive-class; no digest due — 06:2xZ precedes 16:00 UTC on 08-06). See LOG Cycle 281.
- FOCUS POINTER (Cycle 281 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  RUNNER STALL fully RESOLVED + GUARDED (Cycle 261 fix + 263 pin); WATCH stays NORMAL — re-escalate ONLY on a fresh
  >6h no-artifact gap. Cloud track rotation: Cycle 281 was COVERAGE → **TRUTH next** (METHOD → COVERAGE → TRUTH →
  READOUT). **service_booking is now well-mined across all FIVE lifecycle legs** (create / manage / notify / intake
  / waitlist) on both its anchors (acuity + simplybook.me). NEXT in-cloud COVERAGE (still open): a subscription
  PAUSE/RESUME leg (polar `subscription.paused`/uncancel — suspend-without-terminating, distinct from Cycle-276's
  cancel) IF precision-guardable; data_retrieval DATA-FRESHNESS/update-cadence (ipinfo "Daily Data Refresh");
  physical_good RETURNS-WINDOW (allbirds/moleskine). NEXT METHOD: host-environment reproducibility is SATURATED
  across all four axes (hash-seed 267 / timezone 271 / default-encoding 277 / system-locale 280) — the next NEW
  METHOD seam must move OFF host-environment reproducibility (probe-order independence of the aggregate, or
  fixture-capture determinism). NEXT calibration cadence: population 18 (target 15–20); next broadening = a genuine
  ACP/UCP/MPP merchant or a 2nd x402-live site (scarce — record reachability as its own signal). NEXT READOUT: a
  population-median/band overlay across sweeps once ≥3 sweeps carry a stable non-anchor overlap; or a one-line
  gap-held/moved verdict badge on the main card. Substantive [LOCAL] frontier: codex-dependent items stay gated —
  driftflight.com (WITH side) still codex-blocked → cross-model N-curve / LIVE behavioral delta blocked on WITH-side
  reachability (drift-flight.org t2 IS reachable); a THIRD calibration anchor / 2nd x402-live merchant;
  render-generation digital_good (Cycle-168); structured catalog/pricing JSON (Cycle-70).
- CYCLE 280 — 2026-08-06T05:5xZ (METHOD, LOCAL, direct-to-main, tests-only, score-neutral). FIRST duty
  (infra health + peer-gate review): `gh pr list --state open` → `[]` (no open peer-gated PR). HEAD ==
  origin/main == local `main` all at `b5dfcd7` (clean, no stale-orphan realign). **INFRA HEALTHY:** newest
  verify by FILENAME `runs/local/verify_20260806T054102Z.json` (05:41Z, tests_ok=true 35 suites, 46.1 F /
  85.5 B / +39.4), ~1min old at fire (05:42Z 08-06), deep inside the 6h floor; :41 cadence holding
  (03:41Z→04:41Z→05:41Z) → RUNNER-HEALTH WATCH NORMAL. `codex`/`zero`/`.venv` resolve; full suite 35/35 green
  before the change. **TRACK (LOCAL METHOD):** the LOCALE reproducibility axis Cycle 277 spun out as [LOCAL]
  (cloud `locale -a` = C/C.utf8/POSIX only, `setlocale` raises for de_DE/tr_TR) — confirmed OPEN on this host
  (`de_DE.UTF-8` + `tr_TR.UTF-8` installed, `setlocale` succeeds). Codex reachability already characterized ~6h
  ago (four runs 20:45→23:45Z 08-05, `_ENV_BLOCK_RE` fix shipped Cycle 269) → re-run would be monitoring not
  improvement; chose the axis that leaves a permanent teeth-bearing artifact. **IMPROVEMENT (METHOD — the FOURTH
  host-environment reproducibility axis, after hash-seed 267 / timezone 271 / default-encoding 277):** NEW
  `tests/test_locale_reproducibility.py` (5 guards, structural mirror of the encoding suite) re-scores the whole
  6-fixture replay-clean population in SUBPROCESSES under C / de_DE.UTF-8 / tr_TR.UTF-8, each child ACTIVATING the
  env locale via `setlocale(LC_ALL, "")` so `LC_NUMERIC` genuinely bites, asserting the serialized report is
  byte-identical across all three (`generated_at` pinned). Scoring path is invariant TODAY (numbers via
  locale-INDEPENDENT `json.dumps`/`repr(float)`/codepoint `sorted()`) — this VERIFIES the previously-assumed
  property. TEETH (guard 3): de_DE proven active in-child (thousands|decimal `.|,` ≠ C `|.`); locale-AWARE
  `"{:n}".format(1234567)` = `1.234.567` (de) ≠ `1234567` (C) → a leak the guard catches; locale-INDEPENDENT
  `str()` identical. Guard 5 pins `_POPULATION` == live 0-replay-miss set ⊇ pair (self-maintaining). **GRACEFUL
  [LOCAL] GATE:** guards 1-3 probe locale availability in a child and SKIP LOUDLY where absent (the cloud
  container), guards 4-5 (child-scores-real-pipeline / population-replay-clean) run everywhere → file exits 0 in
  BOTH the local run (5/5 full teeth) AND a cloud-sim (foreign locales → non-existent names → availability=False,
  guards 1-3 SKIP, 4-5 pass, exit 0) — does NOT redden the cloud suite. **VALIDATION:** suite 35/35 → 36/36 green
  (new suite 5/5; `test_runner_registration` green, auto-discovered by the glob). **SCORE-NEUTRAL:** scoring-path
  diff (`git diff -- asrs/ rubric/ fixtures/ batteries/ loop/local_verify.py`) EMPTY (only the new test file).
  **CANONICAL UNMOVED:** in-fire LIVE re-score 46.1 F / 85.5 B / +39.4 (pillars concur the 05:41Z floor); the
  new guard's offline digests `c54f611d…`/`9bbd1027…` match the committed baseline. Invariants #1 ($0 read-only
  test)–#5 all held; zero codex, zero paid ops. NO DM (score-neutral tests-only METHOD, not sensitive-class; no
  digest due — 05:5xZ precedes 16:00 UTC on 08-06). See LOG Cycle 280.
- FOCUS POINTER (Cycle 280 done, LOCAL): NO open peer-gated PR → next fire's first duty is the infra health
  check. RUNNER STALL fully RESOLVED + GUARDED (Cycle 261 fix + 263 pin); WATCH stays NORMAL — re-escalate ONLY
  on a fresh >6h no-artifact gap. Cloud track rotation UNCHANGED (this LOCAL cycle did not consume the cloud
  slot): cloud pointer remains **COVERAGE next** per Cycle 279 (METHOD → COVERAGE → TRUTH → READOUT). **METHOD
  host-environment reproducibility is now SATURATED across ALL FOUR axes** — hash-seed (267) + timezone (271) +
  default-encoding (277) + system-locale (280, this cycle, the last [LOCAL]-gated member). The next genuinely-NEW
  METHOD seam must move OFF host-environment reproducibility: candidates are probe-order independence of the
  aggregate (reverse/shuffle the probe list, assert the serialized report is invariant — a determinism property
  of the scorer's own composition) or fixture-capture determinism (two live captures of the same surface produce
  the same committed bytes modulo timestamps). NEXT in-cloud COVERAGE (highest, unblocked): the `waitlist` signal
  on the simplybook.me anchor (service_booking 8→9) — anchor `waiting list`/`waitlist`/`waiting-list` to a BOOKING
  context, ABSENT on the pair + retail + null + api fixtures, fires NON-VACUOUSLY on simplybook.me, add `waitlist`
  to `_ALL_SERVICE_BOOKING_LABELS` in the same change. Also open COVERAGE: a subscription PAUSE/RESUME leg (polar
  `subscription.paused`/uncancel, distinct from Cycle-276's cancel) IF precision-guardable; data_retrieval
  DATA-FRESHNESS/update-cadence (ipinfo "Daily Data Refresh"); physical_good RETURNS-WINDOW (allbirds/moleskine).
  NEXT calibration cadence: population 18 (target 15–20); next broadening = a genuine ACP/UCP/MPP merchant or a
  2nd x402-live site (scarce — record reachability as its own signal). NEXT READOUT: a population-median/band
  overlay across sweeps once ≥3 sweeps carry a stable non-anchor overlap; or a one-line gap-held/moved verdict
  badge on the main card. Substantive [LOCAL] frontier: codex-dependent items stay gated — driftflight.com (WITH
  side) still codex-blocked → cross-model N-curve / LIVE behavioral delta blocked on WITH-side reachability
  (drift-flight.org t2 IS reachable); a THIRD calibration anchor / 2nd x402-live merchant; render-generation
  digital_good (Cycle-168); structured catalog/pricing JSON (Cycle-70). LOCALE axis is now DONE (this cycle).
- CYCLE 279 — 2026-08-06T05:1xZ (READOUT, cloud, direct-to-main, display-only, score-neutral). FIRST duty
  (infra health + peer-gate review): `mcp__github__list_pull_requests` state=open → `[]` (no open peer-gated
  PR). Cloud started detached at origin/main `9cead29` with local `main` ref at stale `3e318f1`; realigned local
  `main` to origin/main (benign, HEAD already matched, no history rewrite). **INFRA HEALTHY:** newest verify by
  FILENAME `runs/local/verify_20260806T044102Z.json` (04:41Z, tests_ok=true 35 suites, 46.1 F / 85.5 B / +39.4),
  ~36min old at fire (05:17Z 08-06), well inside the 6h floor; :41 cadence holding (02:41Z→03:41Z→04:41Z) →
  RUNNER-HEALTH WATCH NORMAL. Bench brought up (venv + pip); full suite 35/35 green before the change.
  **TRACK:** READOUT least-recently-worked (last 246/264/270) AND its long-owed item (population-drift TREND
  across ≥3 sweeps, cloud-owed since Cycle 246) is NOW UNBLOCKED — Cycle 278 committed the 3rd dated sweep
  (20260728/20260805/20260806). **IMPROVEMENT (READOUT — reference-pair trend sparkline):** the single-cadence
  drift card (Cycle 246) shows only this-vs-prior; this zooms out to the WHOLE committed cadence. New
  `asrs/scorecard.py`: `_load_all_calibration_sweeps` (reads every committed sweep oldest-first) +
  `_anchor_trend_series` (pulls the canonical anchors — segment endswith `anchor` — keyed by DOMAIN from data,
  not-scorable reading → gap not 0) + `_anchor_trend_svg` (fixed 0–100-overall multi-series sparkline mirroring
  `_history_trend_svg`; line breaks at a not-scorable gap; top↔bottom anchor gap bracketed) +
  `_calibration_anchor_trend_card` (named legend swatch per anchor so identity ≠ color-alone; gap-HELD/gap-MOVED
  summary from first-vs-last common gap; version-isolation note). Wired into `_write_calibration_page` before the
  drift card (new optional `sweeps=` param; production loads all, unit tests pass explicit list → hermetic). Real
  render: **the reference gap HELD at +39.4 across all 3 v0.7 sweeps** (85.5 with-rails vs 46.1 no-rails). Design
  honors inv #2 (only newest-version sweeps plotted; older-version counted+named-omitted) + inv #4 (not-scorable =
  gap, never a fabricated 0), both test-pinned with teeth. **VALIDATION:** 5 new tests_readout (trend/gap-held +
  gap-moved-flagged + not-scorable-gap-not-zero + version-isolation + <2-sweeps-no-card); test_readout 94→99;
  suite 35/35 green. **SCORE-NEUTRAL:** scoring-path diff (`git diff -- asrs/scoring.py asrs/report.py asrs/probes
  rubric/ fixtures/ batteries/ loop/local_verify.py`) EMPTY (only scorecard.py + test_readout.py). **CANONICAL
  UNMOVED:** in-fire offline replay 46.1 F / 85.5 B / +39.4 (concurs 04:41Z floor). Invariants #1 ($0 — pure
  readout of committed data, no probe)–#5 all held. NO DM (score-neutral READOUT, not sensitive-class; no digest
  due — 05:1xZ precedes 16:00 UTC on 08-06). See LOG Cycle 279.
- FOCUS POINTER (Cycle 279 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health
  check. RUNNER STALL fully RESOLVED + GUARDED (Cycle 261 fix + 263 pin); WATCH stays NORMAL — re-escalate ONLY on
  a fresh >6h no-artifact gap. Cloud track rotation: Cycle 279 was READOUT → **COVERAGE next** (METHOD → COVERAGE →
  TRUTH → READOUT); the long-owed READOUT population-drift TREND is now **DONE** (this cycle). NEXT in-cloud
  COVERAGE (highest, unblocked): the `waitlist` signal on the simplybook.me anchor (service_booking 8→9) — anchor
  `waiting list`/`waitlist`/`waiting-list` to a BOOKING context, ABSENT on the pair + retail + null + api fixtures,
  fires NON-VACUOUSLY on simplybook.me, add `waitlist` to `_ALL_SERVICE_BOOKING_LABELS` in the same change. Also
  open COVERAGE: a subscription PAUSE/RESUME leg (polar `subscription.paused`/uncancel, suspend-without-terminating,
  distinct from Cycle-276's cancel) IF precision-guardable; data_retrieval DATA-FRESHNESS/update-cadence (ipinfo
  "Daily Data Refresh"); physical_good RETURNS-WINDOW (allbirds/moleskine). NEXT METHOD: the static-evidence
  reproducibility family is SATURATED for in-cloud host axes (hash-seed 267 + timezone 271 + default-encoding 277);
  the remaining non-C system locale axis is [LOCAL]-gated; the next genuinely-NEW METHOD seam should move OFF
  host-environment reproducibility (probe-order independence of the aggregate, or fixture-capture determinism).
  NEXT calibration cadence: population now 18 (target 15–20); next broadening = a genuine ACP/UCP/MPP merchant or a
  2nd x402-live site (scarce — record reachability as its own signal). NEXT READOUT (new candidates from this
  cycle): a population-median/band overlay across sweeps (whole-cohort spread, not just the anchor pair) once ≥3
  sweeps carry a stable non-anchor overlap; or surface the trend's gap-held/moved verdict as a one-line badge on
  the main card. Substantive [LOCAL] frontier: codex-dependent items stay gated — driftflight.com (WITH side) still
  codex-blocked → cross-model N-curve / LIVE behavioral delta blocked on WITH-side reachability (drift-flight.org
  t2 IS reachable); a THIRD calibration anchor / 2nd x402-live merchant; render-generation digital_good (Cycle-168);
  structured catalog/pricing JSON (Cycle-70); the LOCALE reproducibility axis.
- CYCLE 278 — 2026-08-06T04:4xZ (TRUTH, LOCAL, direct-to-main, score-neutral). FIRST duty (infra health +
  peer-gate review): `gh pr list --state open` → `[]` (no open peer-gated PR). HEAD == origin/main == local
  `main` all at `9ab04d9` (clean, no stale-orphan realign). **INFRA HEALTHY:** newest verify by FILENAME
  `runs/local/verify_20260806T044102Z.json` (04:41Z, tests_ok=true, 46.1 F / 85.5 B / +39.4), ~1min old at fire
  (04:42Z 08-06), deep inside the 6h floor; :41 cadence holding (02:41Z→03:41Z→04:41Z) → RUNNER-HEALTH WATCH
  NORMAL. Bench up (.venv); full suite 35/35 green before the change. **WORKING-TREE PICKUP:** the fire opened
  with an uncommitted +8-line `POPULATION` broadening in `experiments/calibration_sweep.py` (simplybook.me
  `service-booking:platform` + polar.sh `subscription:mor-platform`) left un-run by a prior interrupted fire —
  the start of increment (a) of the standing [LOCAL] "Grow the calibration population" item; completed it (both
  rows point at REAL captured offering anchors, Cycles 273/275; the backlog's named next broadening step).
  **IMPROVEMENT (TRUTH — calibration-population cadence, increment (a): broaden the population):** ran the
  SHIPPED static scoring path (`_run_probes → scoring.score`, NO `--behavioral`, $0) over the broadened
  18-domain population → `runs/local/calibration_sweep_20260806T044352Z.json` (rubric v0.7): **17/18 scored, 1
  not-scorable (rei.com, agent-UA-blocked, identical to baselines, inv #4), 0 error.** Two NEW storefront TYPES
  land: simplybook.me **64.9 D** (service_booking platform; trust 93.3 / transactability 18.8 = no agent payment
  rail) + polar.sh **70.3 C** (subscription MoR; transactability 50.0; the all-6-archetype claim is the KNOWN
  exa.ai-class diagnostic over-claim, `_discover_claimed` off the scoring path). **CANONICAL UNMOVED:**
  driftflight.com 85.5 B / drift-flight.org 46.1 F / **+39.4** (concurs the 04:41Z verify floor); auto drift
  block vs `calibration_sweep_20260805T014754Z.json`: **15 compared, 0 moved, max|Δ| 0.0** over ~1 day, added
  [polar.sh, simplybook.me], removed [], status_changed [] (new members reported as membership, never averaged
  — the Cycle-245 drift guard's inv-#4 attribution). **SCORE-NEUTRAL:** harness off the scoring path;
  scoring-path diff (`git diff -- asrs/ rubric/ fixtures/ batteries/ loop/local_verify.py`) EMPTY (only
  calibration_sweep.py +8 + the force-added dataset); suite **35/35 green**. Invariants #1 ($0 static — no
  free-tier probe, no zero CLI, no signing, by construction)–#5 all held. NO DM (score-neutral TRUTH, not
  sensitive-class; no digest due — 04:4xZ precedes 16:00 UTC on 08-06). See LOG Cycle 278.
- FOCUS POINTER (Cycle 278 done, LOCAL): NO open peer-gated PR → next fire's first duty is the infra health
  check. RUNNER STALL fully RESOLVED + GUARDED (Cycle 261 fix + 263 pin); WATCH stays NORMAL — re-escalate ONLY
  on a fresh >6h no-artifact gap. Cloud track rotation UNCHANGED (this LOCAL cycle did not consume the cloud
  slot): cloud pointer remains **TRUTH next** per Cycle 277 (METHOD → COVERAGE → TRUTH → READOUT), **BUT READOUT
  IS NOW UNBLOCKED** — this cycle committed the THIRD dated calibration sweep (20260728 / 20260805 / 20260806),
  so the long-owed population-drift TREND sparkline across ≥3 sweeps (cloud-owed since Cycle 246, previously
  [LOCAL]-blocked on "only 2 committed") can finally render in-cloud from each sweep's `rows` (canonical anchors'
  `overall`). NEXT in-cloud COVERAGE (still open): the `waitlist` signal on the simplybook.me anchor
  (service_booking 8→9); a subscription PAUSE/RESUME leg (polar `subscription.paused`/uncancel — suspend-without-
  terminating, distinct from Cycle-276's cancel) IF precision-guardable; data_retrieval DATA-FRESHNESS/update-
  cadence (ipinfo "Daily Data Refresh"); physical_good RETURNS-WINDOW (allbirds/moleskine). NEXT METHOD: the
  static-evidence reproducibility family is SATURATED for in-cloud host axes (hash-seed 267 + timezone 271 +
  default-encoding 277); the remaining axis (non-C system locale de_DE/tr_TR) is [LOCAL]-gated; the next genuinely-
  NEW METHOD seam should move OFF host-environment reproducibility (probe-order independence of the aggregate, or
  fixture-capture determinism). NEXT calibration cadence: population now 18 (target 15–20, deeper in range); next
  broadening = a genuine ACP/UCP/MPP merchant or a 2nd x402-live site (scarce — record reachability as its own
  signal). Substantive [LOCAL] frontier: codex-dependent items stay gated — driftflight.com (WITH side) still
  codex-blocked → cross-model N-curve / LIVE behavioral delta blocked on WITH-side reachability (drift-flight.org
  t2 IS reachable); a THIRD calibration anchor / 2nd x402-live merchant; render-generation digital_good
  (Cycle-168); structured catalog/pricing JSON (Cycle-70); the LOCALE reproducibility axis.
- CYCLE 277 — 2026-08-06T04:2xZ (METHOD, cloud, direct-to-main, tests-only, score-neutral). FIRST duty (infra
  health + peer-gate review): `list_pull_requests` state=open → `[]` (no open peer-gated PR). Cloud started
  detached at origin/main `6c256e9` with local `main` ref at the stale `3e318f1` (Cycle-276 tip, pre the 03:41Z
  verify heartbeat); realigned local `main` to origin/main (benign; HEAD already matched, no history rewrite).
  **INFRA HEALTHY:** newest verify by FILENAME `runs/local/verify_20260806T034105Z.json` (03:41Z, tests_ok=true
  34 suites, 46.1 F / 85.5 B / +39.4), ~41min old at fire (04:22Z 08-06), well inside the 6h floor; :41 cadence
  holding (01:41Z→02:41Z→03:41Z) → RUNNER-HEALTH WATCH NORMAL. Bench brought up (venv + pip); full suite 34/34
  green before the change. **TRACK NOTE:** cloud pointer READOUT-owed but [LOCAL]-blocked (3rd sweep needs
  network) and not starving → next least-recently-worked fresh track is METHOD (last Cycle 271). METHOD's named
  frontier (LOCALE axis) CHECKED + confirmed [LOCAL]-blocked in-cloud (`locale -a` = C/C.utf8/POSIX only;
  `setlocale(LC_ALL,'de_DE.UTF-8'|'tr_TR.UTF-8')` raises → a teeth-bearing locale test cannot be verified here),
  so surfaced the adjacent in-cloud-testable seam. **IMPROVEMENT (METHOD — third host-environment reproducibility
  axis):** closed the DEFAULT-ENCODING axis of the committed static evidence, the sibling of Cycle 267 (hash-seed)
  + Cycle 271 (timezone) + Cycle 274 (population broadening). NEW `tests/test_encoding_reproducibility.py` (5
  guards, 1:1 mirror of the timezone suite) re-scores the whole 6-fixture replay-clean population in subprocesses
  under two host-INDEPENDENT default-encoding envs — explicit UTF-8 mode (`PYTHONUTF8=1`) vs forced ASCII default
  (`LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`, defeating PEP 540 + PEP 538) — asserting the serialized report is
  byte-identical (`generated_at` pinned). Every population fixture carries non-ASCII (em-dash U+2014 + middot
  U+00B7 on the pair; empirically the ASCII env makes `getpreferredencoding()`==`ANSI_X3.4-1968` and an implicit
  `open(fixture).read()` raises `UnicodeDecodeError`). Scoring path is safe TODAY (fixture read `from_fixture:162`
  + rubric read `load_rubric:68` both explicit `encoding="utf-8"`; `to_json` `ensure_ascii`) so all 6 are
  INVARIANT — this VERIFIES the previously-assumed property. TEETH (guard 3): implicit read succeeds under UTF-8,
  RAISES under ASCII; explicit utf-8 byte-identical across both. Guard 5 pins `_POPULATION` == live 0-replay-miss
  set ⊇ pair (self-maintaining, same partition as test_canonical_replay). SCORE-NEUTRAL: scoring-path diff (`git
  diff -- asrs/ rubric/ fixtures/ batteries/ loop/local_verify.py`) EMPTY, only the new test file (auto-discovered
  by the runner glob; test_runner_registration green); suite **34/34 → 35/35 green**; canonical replay **46.1 F /
  85.5 B / +39.4 UNMOVED** (fresh in-fire static re-score concurs, rubric v0.7); `driftflight.com c54f611d60c3…`
  digest matches the Cycle-274 LOG. Invariants #1–5 all held. NO DM (score-neutral tests-only METHOD, not
  sensitive-class; no digest due — 04:2xZ precedes 16:00 UTC on 08-06). See LOG Cycle 277.
- FOCUS POINTER (Cycle 277 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  RUNNER STALL fully RESOLVED + GUARDED (Cycle 261 fix + 263 pin); WATCH stays NORMAL — re-escalate ONLY on a
  fresh >6h no-artifact gap. Cloud track rotation: Cycle 277 was METHOD → cloud pointer is **TRUTH next** (METHOD →
  COVERAGE → TRUTH → READOUT), but **READOUT STILL OWED** the moment a 3rd dated sweep is committed [LOCAL]
  (population-drift TREND sparkline across ≥3 sweeps). NEXT COVERAGE (still open, in-cloud): the `waitlist` signal
  on the simplybook.me anchor (service_booking 8→9); a subscription PAUSE/RESUME leg (`subscription.paused`/uncancel
  on the polar anchor, the suspend-without-terminating leg distinct from Cycle-276's cancel) IF precision-guardable;
  data_retrieval DATA-FRESHNESS/update-cadence (ipinfo "Daily Data Refresh"); physical_good RETURNS-WINDOW leg
  (allbirds/moleskine). **NEXT TRUTH/METHOD: the static-evidence reproducibility family is now SATURATED for
  in-cloud axes — hash-seed (267) + timezone (271) + default-encoding (277) cover every host axis a minimal
  container varies WITHOUT extra installs.** The remaining reproducibility axis (a genuine non-C system locale
  de_DE/tr_TR — comma-decimal `{:n}` + dotless-i case-fold leaks the ASCII-codec axis cannot catch) is [LOCAL]-gated
  (needs the locale installed to activate via setlocale). Beyond that, the next genuinely-NEW METHOD seam should
  move OFF host-environment reproducibility (e.g. probe-order independence of the aggregate, or fixture-capture
  determinism). NEXT READOUT: population-drift TREND across ≥3 dated sweeps ([LOCAL]-gated, only 2 committed).
  Substantive [LOCAL] frontier: codex-dependent items stay gated — driftflight.com (WITH side) still codex-blocked
  → cross-model N-curve / LIVE behavioral delta blocked on WITH-side reachability (drift-flight.org t2 IS
  reachable); a THIRD calibration anchor / 2nd x402-live merchant; render-generation digital_good (Cycle-168);
  structured catalog/pricing JSON (Cycle-70); the LOCALE reproducibility axis (this cycle's [LOCAL] spinoff).
<!-- STATE COMPACTED at Cycle 260 (2026-08-05T~17:1xZ, self-healing/COVERAGE, direct-to-main, score-neutral).
     STATE.md had accreted the full per-cycle history back to ~Cycle 5 (7798 lines / ~790KB) and could no
     longer be Read in one call, degrading the playbook-mandated per-cycle "read STATE.md". Trimmed the
     rolling cycle log to the last few cycles (259→256 above; Cycle 260 prepended below); every removed cycle
     entry is preserved verbatim in loop/LOG.md (276 entries, Cycle 5→256, spot-verified) and full git
     history. STATE is mutable working state (counter + focus pointer + open questions), NOT an append-only
     LOG/evidence file, so this compaction is NOT an invariant-#5 rewrite. The stable reference sections
     (Git bookkeeping note, Environment constraint, Open questions) are retained UNCHANGED below. Recurring
     policy: prune the rolling cycle log to the last ~5 cycles whenever STATE grows past readability. -->

## Git bookkeeping note (Cycle 52, 2026-07-28T06:2xZ)

The fresh cloud checkout started with local branch `main` at the STALE ORPHAN tip
`2e66201` (unrelated history — same one Cycle 51 flagged), while origin/main was the real
line. Cycle 52's commit `c2b389d` was authored correctly (parent = origin/main `ca62669`)
but on a DETACHED HEAD, so `git push origin main` initially pushed the ORPHAN local `main`
over the real history → a genuine (self-inflicted) non-fast-forward rejection that LOOKED
like a server anomaly. Fix: `git checkout -B main c2b389d` then push (clean ff
`ca62669..c2b389d`). LESSON for next cycle: after the fresh-checkout `git pull`, VERIFY
`git rev-parse main` == `git rev-parse origin/main` before committing; if local `main` is
the orphan `2e66201`, realign first (`git checkout -B main origin/main`) so pushes target
the real history. Also: this relay REJECTS branch DELETES ("remote end hung up") — two
harmless redundant refs `loop/cycle52-probe` and `loop/cycle52-freshness-banner` (both ==
`c2b389d` == current main) were left on the server; delete them from Jonah's machine or via
the GitHub UI when convenient (they clutter the branch list but affect nothing).

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
  UPDATE (2026-08-05T21:4xZ, Cycle 268 local fire): the "none observed yet" claim is now
  SUPERSEDED — the canonical domains aged to ~20 days and the gate BOTH softened and drifted.
  `experiments/codex_reachability.py` re-run (5 codex trials, corroborated by the prior 20:45Z
  fire's run): codex REACHED drift-flight.org on trial 2 in BOTH runs (and driftflight.com t2 at
  20:45Z), so the reputation gate is no longer the 07-23 4/4 hard block — it is intermittent. AND
  the refusals that still fire now use own-tool block phrasings OUTSIDE the v0.6 `_ENV_BLOCK_RE`
  vocabulary ("Safety-controlled navigation … denied", "browser's site-permission boundary …
  denied", "web fetch … rejected as unsafe") → `_is_env_blocked`=False on genuine AGENT-side blocks
  (site HTTP 200, reached on sibling trials, example.com never gated) → the invariant-#4 leak the
  test-#8 spec describes is now LIVE on committed transcripts
  (`runs/local/codex_reachability_20260805T{204555,214534}Z/`). The `_ENV_BLOCK_RE` broadening is
  now WARRANTED (no longer "on speculation") and queued as a peer-gated P0 (BACKLOG). Broaden
  CAREFULLY — it must NOT route site-side 403s/Cloudflare challenges to reachability (attribution
  honesty cuts both ways).
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
