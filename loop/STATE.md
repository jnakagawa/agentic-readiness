# Loop state

- Cycle counter: 260
- CYCLE 260 — 2026-08-05T~17:1xZ (COVERAGE/SELF-HEALING, cloud, direct-to-main, score-neutral).
  FIRST duty (infra health check): no open peer-gated PR (`list_pull_requests` state=open `[]`); HEAD realigned to
  origin/main at Cycle 259 (`bb9e1a2`; detached-start realign via `git fetch origin main` + `git checkout -B main
  origin/main`, benign forced-update of the stale local ref). **LOCAL VERIFY RUNNER STALL PERSISTS — 6h floor still
  breached:** newest verify STILL `runs/local/verify_20260805T024100Z.json` (02:41Z, div_recovery=None, tests_ok=true,
  reads 46.1 F / 85.5 B / +39.4), ~14.6h old at fire (17:14Z); 14+ consecutive missed :41 slots (03:41–16:41).
  NO-NEW-ARTIFACT stall, NOT cloud-diagnosable → P0 [LOCAL] runner-stall diagnosis (queued Cycle 251) stands.
  Regression-by-construction stands in for the live re-score (playbook). `pip install eth-account` + `pytest`
  (agent-side dependency gaps) → test_free_tier 11/11. **DIGEST NOT OWED this fire:** the daily digest was already
  SENT Cycle 259 in this same ≥16:00 UTC window (17:14Z Aug-5); next digest owed at the next ≥16:00 UTC fire after a
  fresh window. SHIPPED (self-healing/COVERAGE, off scoring path → score-neutral, direct-to-main): **compacted
  STATE.md 7798 lines / ~790KB → 297 lines / 29KB** — the file had accreted the full per-cycle history back to
  ~Cycle 5 and EXCEEDED the 256KB single-`Read` limit, silently degrading the mandated per-cycle "read STATE.md".
  Trimmed the rolling cycle log to the last cycles (259→256; this Cycle 260 prepended), kept the operative FOCUS
  POINTER + active RUNNER-HEALTH WATCH, and retained the stable reference sections (Git bookkeeping note,
  Environment constraint, Open questions) UNCHANGED. Every removed narrative is preserved verbatim in loop/LOG.md
  (276 entries, Cycle 5→256 spot-verified) + git → NOT an invariant-#5 rewrite (STATE is mutable working state).
  Made it DURABLE: NEW `tests/test_state_hygiene.py` (+4) guards STATE under a 200KB single-`Read` ceiling + a
  600-line early-warning cap + retention of its stable-section markers, so a future fire that lets STATE re-balloon
  fails the suite and MUST prune before committing. MUTATION-TESTED (bloat trips the byte+line guards; dropping a
  required marker trips the structural guard; real STATE passes 4/4). SCORE-NEUTRAL: scoring-path diff
  (`asrs/scoring.py rubric/ fixtures/ batteries/ asrs/offering.py asrs/probes/ asrs/scorecard.py`) EMPTY; canonical
  scored statically, replay **26/26**, **46.1 F / 85.5 B / +39.4 UNMOVED**; full suite **539 passed** (535→539).
  Invariants #1–#5 all held (compaction touches only working state, executes nothing; no scoring-semantics → no
  version bump; removed history traces to LOG.md + git; env failures attributed to agent/LOCAL; append-only history
  preserved — STATE is not append-only evidence). NO DM (score-neutral self-healing, not sensitive-class, digest
  already sent this window). See LOG Cycle 260.
- FOCUS POINTER (Cycle 260 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  **The LOCAL verify runner is STALLED, 6h floor breached (P0 [LOCAL] queued Cycle 251) — not cloud-doable; keep the
  P0 [LOCAL] fresh and flag it LOUD in the next daily digest (owed at the next ≥16:00 UTC fire in a fresh window;
  the Cycle-259 digest already discharged this window's flag).** Cloud track rotation: Cycle 260 took the COVERAGE
  slot (self-healing STATE-compaction) → cloud pointer is **TRUTH next** (METHOD → COVERAGE → TRUTH → READOUT).
  **STATE-HYGIENE now self-enforcing** (`test_state_hygiene.py`) — future cycles PREPEND their entry and prune the
  rolling log to ~5 cycles; the suite reddens if STATE re-balloons past readability. NEXT TRUTH openings: the
  `per_model` map in `trust_probe._build_check` (arrival-order but self-labeled — a determinism guard if
  construction parallelizes). NEXT COVERAGE openings (later): service_booking anchor mining EXHAUSTED (8 signals);
  WAITLIST is IMAGE-ONLY → [LOCAL] richer-booking fixture; the ipinfo.io DATASET-FORMAT/DOWNLOAD-CONTRACT
  data_retrieval signal (Cycle-243); the deep-bank uncaptured-capability audit (Cycle 226/230/233 lineage). NEXT
  METHOD openings: METHOD TRACK IS SATURATED (reliability/quotability/scoring-cap surfaces closed, Cycle-192 earner
  arc complete) — a future METHOD cycle must SURFACE A NEW SEAM before picking. NEXT READOUT openings: the `compare`
  view (`render_compare`) transactability delta carries no corroboration for either side; population-drift TREND
  once a 3rd dated sweep lands ([LOCAL]-gated).
  **RUNNER-HEALTH WATCH (ESCALATED — FLOOR BREACHED, carried Cycle 251→260 — hold until resolved):** last artifact
  02:41Z; at the Cycle-260 fire (17:14Z) ~14.6h old = past the 6h floor, 14+ consecutive misses (03:41–16:41).
  Cloud cannot diagnose → P0 [LOCAL] with exact diagnostic steps stands.
- CYCLE 259 — 2026-08-05T~16:2xZ (METHOD, cloud, direct-to-main, score-neutral).
  FIRST duty (infra health check — no open peer-gated PR, `list_pull_requests` state=open `[]`): HEAD in sync with
  origin at Cycle 258 (`1193cf0`; `git pull origin main`, benign forced-update of the stale local ref). **LOCAL
  VERIFY RUNNER STALL PERSISTS — 6h floor still breached:** newest verify STILL `runs/local/verify_20260805T024100Z.json`
  (02:41Z, div_recovery=None, tests_ok=true, reads 46.1 F / 85.5 B / +39.4), ~13.6h old at fire (16:2xZ); 13+
  consecutive missed :41 slots (03:41–15:41). NO-NEW-ARTIFACT stall, NOT cloud-diagnosable → P0 [LOCAL] runner-stall
  diagnosis (queued Cycle 251) stands. **This fire CROSSES ≥16:00 UTC = first digest-window cycle since Cycle 228 →
  daily digest SENT this cycle, runner-stall flag DISCHARGED LOUD in it.** Regression-by-construction stands in for
  the live re-score (playbook). `pip install eth-account` (agent-side dependency gap) → test_free_tier 11/11. Took the
  METHOD slot but found BOTH nominal METHOD openings ALREADY CLOSED: (1) panel-verdict-stability / provisional-trust-
  unstable is covered (`test_quotability::test_trust_split_panel_is_provisional` + siblings; `_STABLE_MIN` boundary +
  label/gate coherence in `test_reliability`), reliability/quotability surface SATURATED; (2) the BACKLOG Cycle-192
  leg-(a) coupling guard already exists (`test_calibration.py:808`). Took the queued on-track METHOD-class artifact
  whose absence was REAL — leg-(b): the terminal↔HTML earner PARITY GUARD (Cycle-188-shape drift guard) + its
  substrate. SHIPPED (off scoring path → score-neutral, direct-to-main): `asrs/report.py` +`_earner_rep`/
  `_pillar_earner_line` — the per-pillar "earned by <finding> +N" caption now renders on the TERMINAL card too (Cycle
  192 shipped it on HTML only), reading the SAME `scorecard._pillar_top_earner` both surfaces share (parity by
  construction, omitted on n/a/unearned). NEW `tests/test_readout.py` +3 (parity on BOTH canonical storefronts every
  scored pillar + n/a-omission teeth + terminal magnitude-flip vendor-neutrality). MUTATION-TESTED (monkeypatch
  `_pillar_earner_line` → wrong finding reddens the parity guard). SCORE-NEUTRAL: scoring-path diff EMPTY; canonical
  scored statically, replay 26/26, **46.1 F / 85.5 B / +39.4 UNMOVED**; full suite **535 passed** (532→535, test_readout
  89→92). Invariants #1–#5 all held (readout reads existing evidence executes nothing; no scoring-semantics → no
  version bump; traces to committed fixtures; env failures attributed to agent/LOCAL; append-only). DM SENT (daily
  digest + runner-stall flag; NOT sensitive-class). See LOG Cycle 259.
- FOCUS POINTER (Cycle 259 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  **The LOCAL verify runner is STALLED, 6h floor breached (P0 [LOCAL] queued Cycle 251) — not cloud-doable; the
  daily-digest flag was DISCHARGED Cycle 259, so the next digest is not owed until the next ≥16:00 UTC fire after a
  new digest window; keep the P0 [LOCAL] fresh.** Cloud track rotation: Cycle 259 was METHOD → cloud pointer is
  **COVERAGE next** (METHOD → COVERAGE → TRUTH → READOUT). **METHOD TRACK IS SATURATED** — the reliability/
  quotability/scoring-cap surfaces are closed (monotonicity, threshold coherence, polarity/panel-size/order
  invariance, exhaustive formula; trust-split + boundary; caps set-invariance) and the Cycle-192 earner arc is now
  COMPLETE (leg-a Cycle-192, leg-b Cycle 259). A future METHOD cycle must SURFACE A NEW SEAM before picking (do not
  re-add relabel/reflection/order guards — diminishing returns per the Cycle-185 note). **BOOKKEEPING-DEGRADATION
  OBSERVATION:** STATE.md is 804KB / 7752 lines — it has accreted the full cycle history (back to ~Cycle 5) and is
  now too large to `Read` in one call, degrading the mandated per-cycle "read STATE.md". Queued a self-healing/
  COVERAGE STATE-compaction item in BACKLOG (compact to counter + last ~5 cycles + the stable reference sections;
  history is preserved in LOG.md + git so pruning STATE is NOT an invariant-#5 rewrite). NEXT COVERAGE openings: the
  STATE-compaction (above); service_booking anchor mining EXHAUSTED (8 signals); WAITLIST is IMAGE-ONLY → [LOCAL]
  richer-booking fixture; the ipinfo.io DATASET-FORMAT/DOWNLOAD-CONTRACT data_retrieval signal (Cycle-243); the
  deep-bank uncaptured-capability audit (Cycle 226/230/233 lineage). NEXT READOUT openings (later): the `compare`
  view (`render_compare`) transactability delta carries no corroboration for either side; population-drift TREND once
  a 3rd dated sweep lands ([LOCAL]-gated). NEXT TRUTH openings: the `per_model` map in `trust_probe._build_check`
  (arrival-order but self-labeled — a determinism guard if construction parallelizes).
  **RUNNER-HEALTH WATCH (ESCALATED — FLOOR BREACHED, carried Cycle 251→259 — hold until resolved):** last artifact
  02:41Z; at the Cycle-259 fire (16:2xZ) ~13.6h old = past the 6h floor, 13+ consecutive misses (03:41–15:41). Cloud
  cannot diagnose → P0 [LOCAL] with exact diagnostic steps stands. FLAG discharged in the Cycle-259 digest.
- CYCLE 258 — 2026-08-05T~15:2xZ (READOUT, cloud, direct-to-main, score-neutral).
  FIRST duty (infra health check — no open peer-gated PR, `list_pull_requests` state=open `[]`): HEAD realigned to
  origin/main at Cycle 257 (`a92fdd4`; detached-start realign via `git fetch origin main` + `git checkout -B main
  origin/main`, benign forced-update of local ref). **LOCAL VERIFY RUNNER STALL PERSISTS — 6h floor still breached:**
  newest verify STILL `runs/local/verify_20260805T024100Z.json` (02:41Z, div_recovery=None, tests_ok=true, reads 46.1 F
  / 85.5 B / +39.4), ~12.6h old at fire (15:20Z); 12+ consecutive missed :41 slots (03:41–14:41). Unchanged
  NO-NEW-ARTIFACT stall, NOT cloud-diagnosable → P0 [LOCAL] runner-stall diagnosis (queued Cycle 251) stands; carry
  watch + flag LOUD in next 16:00 UTC digest (fire 15:20Z STILL just before the digest window; NEXT fire crossing
  ≥16:00Z owes it — the runner-stall flag is OVERDUE the instant it opens). Regression-by-construction stands in for the
  live re-score (playbook). `pip install eth-account` (agent-side dependency gap) → test_free_tier 11/11. Took the
  READOUT slot (cloud pointer, Cycle 257 was TRUTH): the pointed in-cloud opening — the TERMINAL-card payment-
  corroboration line, counterpart to the HTML card's Cycle-254 badge. `asrs/report.py render` showed the bare
  Transactability pillar bar with no qualifier; the HTML card has since Cycle 254 carried a badge on that row saying
  whether the shopper's LIVED payment experience corroborates the static transactability PREDICTION (x402_probe status
  vs machine_payable_path across valid trials — the SAME signal the calibration guard reads). SHIPPED (readout-only,
  off scoring path → score-neutral, direct-to-main): new shared pure `payment_corroboration_state(predicted_payable,
  reached)` in `asrs/scorecard.py` (3-state good/neutral/warn DECISION), `_payment_corroboration` refactored to delegate
  to it (HTML badge tuples byte-identical), new `_payment_corroboration_line(report)` in `asrs/report.py` wired under the
  Transactability row — both readouts now read the ONE decision so the HTML badge and terminal line can never disagree.
  Display-only: suppresses (no line) on static-only or prediction-absent cards; NEW
  `tests/test_report_payment_corroboration.py` +7 (three states render distinct lines; terminal state == HTML badge
  class across all three = same-signal proof; display-only score-untouched; suppression on no-panel/no-prediction;
  teeth that the three states are distinct strings). MUTATION-TESTED (collapse the shared classifier to always-"good" →
  reddens BOTH the new terminal test AND `test_readout` 89→86; restored 7/7, 89/89). SCORE-NEUTRAL: scoring-path diff
  (`asrs/scoring.py rubric/ fixtures/ batteries/ asrs/offering.py asrs/probes/`) EMPTY; canonical scored statically
  (no behavioral runs → line suppresses on both), replay 26/26, **46.1 F / 85.5 B / +39.4 UNMOVED**; full suite **532
  passed** (525→532, exit-code-verified). Invariants #1 (readout reads existing evidence, executes nothing), #2 (no
  scoring-semantics → no version bump), #3 (traces to committed report fields, suppresses when nothing to corroborate),
  #4 (a `warn` is a display flag not a site punishment; eth-account + stall attributed to agent/LOCAL env), #5 (mutation
  on /tmp backup, restored; append-only) all held. NO DM (score-neutral READOUT, not sensitive-class, off scoring path,
  before 16:00 UTC — 15:20Z Aug-5; last digest Cycle 228). See LOG Cycle 258.
- FOCUS POINTER (Cycle 258 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  **BUT the LOCAL verify runner is STALLED with the 6h floor breached (P0 [LOCAL] queued Cycle 251) — not cloud-doable;
  next-fire priority is keeping the P0 [LOCAL] fresh + the 16:00 UTC digest flag (OVERDUE — the NEXT fire almost
  certainly crosses ≥16:00Z and OWES the daily digest carrying the runner-stall flag LOUDLY).** Cloud track rotation:
  Cycle 258 was READOUT → cloud pointer is **METHOD next** (METHOD → COVERAGE → TRUTH → READOUT). NEXT METHOD openings:
  panel-verdict-stability — does the reliability `stable`/`reproducible` gate (`asrs/reliability.py` `verdict_stability
  >= _STABLE_MIN`) track what an agent re-experiences across trials, or can a "stable" ladder coexist with an unstable
  trust posture a reader would still cite? (`provisional-trust-unstable` quotability branch untested vs a synthetic
  disagreeing panel). NEXT READOUT openings (later): the `compare` view (`render_compare`) shows the two-column
  transactability delta but no corroboration for EITHER side — the same affordance could qualify the with/without
  transactability rows when both sides ran panels; the population-drift TREND once a 3rd dated sweep lands
  ([LOCAL]-gated, only 2 committed). NEXT TRUTH openings: the `per_model` map in `trust_probe._build_check`
  (arrival-order but self-labeled — a determinism guard if construction parallelizes); the shopper aggregator's
  arrival-order surfaces are now CLOSED (Cycles 253/255/257). NEXT COVERAGE openings: service_booking anchor mining
  EXHAUSTED (8 signals); WAITLIST is IMAGE-ONLY → [LOCAL] richer-booking fixture; the ipinfo.io
  DATASET-FORMAT/DOWNLOAD-CONTRACT data_retrieval signal (Cycle-243); the deep-bank uncaptured-capability audit
  (Cycle 226/230/233 lineage).
  **RUNNER-HEALTH WATCH (ESCALATED — FLOOR BREACHED, carried Cycle 251→258 — hold until resolved):** last artifact
  02:41Z; at the Cycle-258 fire (15:20Z) it is ~12.6h old = past the 6h floor, 12+ consecutive misses (03:41–14:41).
  Cloud cannot diagnose (launchd-not-firing / machine-asleep / new pre-push failure indistinguishable from here) →
  P0 [LOCAL] with exact diagnostic steps stands. Distinct from the Cycle-227 push-race (`divergence_recovery` None).
  FLAG loudly in the next 16:00 UTC digest.
- CYCLE 257 — 2026-08-05T~14:2xZ (TRUTH, cloud, direct-to-main, score-neutral).
  FIRST duty (infra health check — no open peer-gated PR, `list_pull_requests` state=open `[]`): HEAD in sync with
  origin at Cycle 256 (`3683c0f`; detached-start realign via `git fetch origin main`, benign forced-update of local
  ref). **LOCAL VERIFY RUNNER STALL PERSISTS — 6h floor still breached:** newest verify STILL
  `runs/local/verify_20260805T024100Z.json` (02:41Z, div_recovery=None, tests_ok=true, reads 46.1 F / 85.5 B /
  +39.4), ~11.7h old at fire (14:21Z); 11+ consecutive missed :41 slots (03:41–13:41). Unchanged NO-NEW-ARTIFACT
  stall, NOT cloud-diagnosable → P0 [LOCAL] runner-stall diagnosis (queued Cycle 251) stands; carry watch + flag LOUD
  in next 16:00 UTC digest (fire ~14:2xZ still before the digest window; NEXT fire crossing ≥16:00Z owes it).
  Regression-by-construction stands in for the live re-score (playbook). `pip install eth-account` (agent-side
  dependency gap) → test_free_tier 11/11. Took the TRUTH slot (cloud pointer, Cycle 256 was COVERAGE): executed the
  named next-hypothesis — the LAST two arrival-order evidence surfaces after Cycles 253/255 closed the sliced/selected
  ones. Both self-labeled `by_run` lists in `asrs/behavioral/shopper.py` projected rows in ARRIVAL order:
  `_aggregate`'s zero-valid CANT_TEST branch (`for r in runs`, shopper.py:335) + `_trust_live_check` (`for r in
  valid`, shopper.py:522) — so two identical panels answering in a different order would emit byte-DIFFERENT evidence
  for the SAME score if panel construction ever parallelizes (points/status already permutation-invariant counts;
  only the citable list ORDER leaked). FIXED both to `sorted(..., key=lambda r: (r.model, r.trial))` — the
  self-label is unique+total in production, so the whole CheckResult is byte-identical under any permutation. SHIPPED
  (off the scoring path → score-neutral, direct-to-main): shopper.py two sorts + comments; NEW
  `tests/test_shopper_evidence_order.py` +2 (metamorphic `_aggregate(fwd)==_aggregate(reversed)` on both the CANT_TEST
  and valid-panel paths + `(model,trial)`-order property + teeth that the raw arrival projection differed).
  MUTATION-TESTED (revert both sorts → reddens both `==` invariants 0/2; restored 2/2). SCORE-NEUTRAL: scoring-path
  diff (`asrs/scoring.py rubric/ fixtures/ batteries/ asrs/offering.py asrs/probes/`) EMPTY; canonical scored
  statically (no behavioral runs) so `_aggregate`/`_trust_live_check` never run on that path; replay 26/26, **46.1 F /
  85.5 B / +39.4 UNMOVED**; full suite **525 passed** (523→525). Invariants #1 (probe read-only, evidence projection
  only), #2 (no scoring-semantics → no version bump), #3 (strengthens evidence reproducibility), #4 (eth-account +
  stall attributed to agent/LOCAL env not a site), #5 (mutation in working tree, restored from /tmp backup;
  append-only) all held. NO DM (score-neutral TRUTH, not sensitive-class, off scoring path, before 16:00 UTC — ~14:2xZ
  Aug-5; last digest Cycle 228). See LOG Cycle 257.
- FOCUS POINTER (Cycle 257 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  **BUT the LOCAL verify runner is STALLED with the 6h floor breached (P0 [LOCAL] queued Cycle 251) — not
  cloud-doable; next-fire priority is keeping the P0 [LOCAL] fresh + the 16:00 UTC digest flag (OVERDUE once the
  digest window opens ≥16:00Z — this cycle at ~14:2xZ is still before it, but the NEXT fire likely crosses it).**
  Cloud track rotation: Cycle 257 was TRUTH → cloud pointer is **READOUT next** (METHOD → COVERAGE → TRUTH →
  READOUT). NEXT TRUTH openings (later): panel-verdict-stability — does the reliability `stable`/`reproducible` gate
  (`asrs/reliability.py` `verdict_stability >= _STABLE_MIN`) track what an agent re-experiences across trials, or can a
  "stable" ladder coexist with an unstable trust posture a reader would still cite? (the `provisional-trust-unstable`
  quotability branch exists but is untested against a synthetic disagreeing panel); the `per_model` map in
  `trust_probe._build_check` (arrival-order but self-labeled — a guard it stays deterministic if construction
  parallelizes). The shopper aggregator's arrival-order surfaces are now CLOSED (both `by_run` + `block_statements` +
  `refusing_models` + `all_trust_events` + `per_checkpoint`). NEXT READOUT openings (pointer now): the TERMINAL-card
  corroboration line (`asrs/report.py` — Cycle 254 did the HTML card); the population-drift TREND once a 3rd dated
  sweep lands ([LOCAL]-gated, only 2 committed). NEXT COVERAGE openings (later): service_booking in-cloud anchor
  mining EXHAUSTED (8 signals); last thin candidate WAITLIST is IMAGE-ONLY → [LOCAL] richer-booking fixture; the
  ipinfo.io DATASET-FORMAT/DOWNLOAD-CONTRACT data_retrieval signal (Cycle-243); the deep-bank uncaptured-capability
  audit (Cycle 226/230/233 lineage).
  **RUNNER-HEALTH WATCH (ESCALATED — FLOOR BREACHED, carried Cycle 251→257 — hold until resolved):** last artifact
  02:41Z; at the Cycle-257 fire (14:21Z) it is ~11.7h old = past the 6h floor, 11+ consecutive misses (03:41–13:41).
  Cloud cannot diagnose (launchd-not-firing / machine-asleep / new pre-push failure indistinguishable from here) →
  P0 [LOCAL] with exact diagnostic steps stands. Distinct from the Cycle-227 push-race (`divergence_recovery` None).
  FLAG loudly in the next 16:00 UTC digest.
- CYCLE 256 — 2026-08-05T~13:2xZ (COVERAGE, cloud, direct-to-main, score-neutral).
  FIRST duty (infra health check — no open peer-gated PR, `list_pull_requests` state=open `[]`): HEAD in sync with
  origin at Cycle 255 (`7465e81`; detached-start realign via `git fetch origin main`, benign forced-update of local
  ref). **LOCAL VERIFY RUNNER STALL PERSISTS — 6h floor still breached:** newest verify STILL
  `runs/local/verify_20260805T024100Z.json` (02:41Z, div_recovery=None, tests_ok=true, reads 46.1 F / 85.5 B /
  +39.4), ~10.7h old at fire (13:22Z); 10+ consecutive missed :41 slots (03:41–12:41). Unchanged NO-NEW-ARTIFACT
  stall, NOT cloud-diagnosable → P0 [LOCAL] runner-stall diagnosis (queued Cycle 251) stands; carry watch + flag LOUD
  in next 16:00 UTC digest (fire ~13:2xZ before the digest window). Regression-by-construction stands in for the live
  re-score (playbook). `pip install eth-account` (agent-side dependency gap) → test_free_tier 11/11. Took the COVERAGE
  slot (cloud pointer, Cycle 255 was METHOD): the oldest in-cloud COVERAGE opening — a service_booking intake-form
  data-collection control. Evidence decided INTAKE-FORM over WAITLIST: the anchor states intake in real prose
  ("collect client info with custom intake forms", "fill out any intake forms you've set up"; 39 `\bintake forms?\b`
  hits) while WAITLIST is IMAGE-ONLY (`waitlist.png`, no prose → deferred to [LOCAL]). SHIPPED (off the scoring path →
  score-neutral, direct-to-main): `asrs/offering.py` +8th service_booking signal `("intake-form",
  re.compile(r"\bintake forms?\b", _F))` — the DATA-COLLECTION PRECONDITION "collect what the job needs / provision
  without a human" leg, distinct from create/manage/notify, precision-guarded against bare "form" and bare "intake"
  (fixed collocation only, mirroring booking-notification's "appointment reminder(s)"). Fired NON-VACUOUSLY on the
  anchor (39 hits), ABSENT on all 7 others incl. the canonical pair. `test_offering.py` +2 (101→103: precision-
  synthetic 5-fire/6-dodge + real-captured end-to-end) both registered; `test_offering_canonical.py`
  `_BOOKING_INTAKE_LABELS` in the genuine-label contract + anchor check (g) + `_ISOLATION_EVIDENCE` row (bank 71→72).
  MUTATION-TESTED (never-match regex reddens both offering guards + canonical (g); restored clean). SCORE-NEUTRAL:
  classifier off the static path, anchor ALREADY claims service_booking so intake only DEEPENS; canonical archetypes
  UNCHANGED (both [metered_api, digital_good, subscription]), **46.1 F / 85.5 B / +39.4 UNMOVED** (replay 26/26 pins
  v0.7); full suite **523 passed** (521→523). Invariants #1 (classifier read-only, no probe/POST/signing), #2 (no
  scoring-semantics → no version bump), #3 (real-prose mined, non-vacuous on anchor + absent on 7), #4 (eth-account +
  stall attributed to agent/LOCAL env not a site), #5 (mutation on /tmp backup, reverted; append-only) all held. NO DM
  (score-neutral COVERAGE, not sensitive-class, off scoring path, not first-after-16:00 UTC — ~13:2xZ Aug-5; last
  digest Cycle 228). See LOG Cycle 256.
- FOCUS POINTER (Cycle 256 done, cloud): NO open peer-gated PR → next fire's first duty is the infra health check.
  **BUT the LOCAL verify runner is STALLED with the 6h floor breached (P0 [LOCAL] queued Cycle 251) — not
  cloud-doable; next-fire priority is keeping the P0 [LOCAL] fresh + the 16:00 UTC digest flag (OVERDUE once the
  digest window opens ≥16:00Z — this cycle at ~13:2xZ is still before it, but the NEXT fire likely crosses it).**
  Cloud track rotation: Cycle 256 was COVERAGE → cloud pointer is **TRUTH next** (METHOD → COVERAGE → TRUTH →
  READOUT). NEXT TRUTH openings (prefer oldest, in-cloud): panel-verdict-stability (does the reliability
  `stable`/`reproducible` gate track what an agent re-experiences across trials); the remaining order-adjacent
  surfaces = the `by_run` evidence lists (shopper.py:335/522) + `per_model` (`_build_check`), arrival-order but
  self-labeled (model,trial) — a guard confirming they stay deterministic if panel construction ever parallelizes.
  NEXT COVERAGE openings (later): service_booking in-cloud anchor mining is nearly EXHAUSTED (create ∪ manage ∪
  notify ∪ intake = 8 signals); last thin candidate WAITLIST is IMAGE-ONLY on the anchor → [LOCAL] richer-booking
  fixture. Remaining in-cloud: the ipinfo.io DATASET-FORMAT/DOWNLOAD-CONTRACT data_retrieval signal (Cycle-243); the
  deep-bank uncaptured-capability audit (Cycle 226/230/233 lineage). NEXT READOUT openings: the TERMINAL-card
  corroboration line (`asrs/report.py` — Cycle 254 did the HTML card); the population-drift TREND once a 3rd dated
  sweep lands ([LOCAL]-gated, only 2 committed).
  **RUNNER-HEALTH WATCH (ESCALATED — FLOOR BREACHED, carried Cycle 251→256 — hold until resolved):** last artifact
  02:41Z; at the Cycle-256 fire (13:22Z) it is ~10.7h old = past the 6h floor, 10+ consecutive misses (03:41–12:41).
  Cloud cannot diagnose (launchd-not-firing / machine-asleep / new pre-push failure indistinguishable from here) →
  P0 [LOCAL] with exact diagnostic steps stands. Distinct from the Cycle-227 push-race (`divergence_recovery` None).
  FLAG loudly in the next 16:00 UTC digest.

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
