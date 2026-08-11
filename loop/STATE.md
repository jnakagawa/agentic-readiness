# Loop state

- Cycle counter: 336
- **✅ PEER-GATED PR #165 AUTHORED — WELD aloyoga.com (81.2 B) as the 15th non-anchor / 5th UCP-rail cross-path member
  (the HIGH CORNER of the UCP plane); no first-duty review owed (NO open PR at fire start); bench GREEN 38/38 (Local
  20260811T044102Z, COVERAGE — weld PR peer-gated, loop docs direct-to-main).** FIRST DUTY: none owed — `gh pr list
  --state open` empty (PR #164 merged LAST fire). Executed the ONE `[LOCAL]` item = the P1 forward weld. All
  prerequisites were discharged over prior fires (PIN 20260810T174412Z / POPULATION add 20260810T200452Z / the
  weld-visible on-glob `calibration_sweep_20260811T034627Z.json` committed LAST fire, aloyoga 81.2 byte-on-floor).
  **Verified load-bearing:** `replay.EXPECTED['aloyoga.com']` = 81.2 v0.7 (100.0/100.0/50.0/100.0); the on-glob sweep
  034627Z rows it `scored=True overall=81.2` seg `ucp-live:apparel-retail`, pillars byte-identical → non-vacuous
  (`n_compared=1`, agrees with the frozen floor). **Authoring live $0 re-confirm** (`asrs.cli score aloyoga.com
  --json-only`, static, NO `--behavioral`/`--max-pay`/codex/zero-CLI/signing — inv #1 by construction) →
  `runs/aloyoga_com_20260811T044511.json`: **live 81.2 B == frozen 81.2 == EXPECTED 81.2**, all four non-null pillars
  byte-identical (100.0/100.0/50.0/100.0), `caps_applied` empty, honest `{metered_api, physical_good}`. **Change:**
  added `"aloyoga.com"` to `_NON_ANCHOR_WELDED` (14→15) + docstring + load-bearing
  `test_aloyoga_fifteenth_non_anchor_is_welded_nonvacuously` (teeth: synthetic drift 81.2→92.0 caught vs the 81.2
  floor) + registration — **off the static scoring path** (`asrs/rubric/scoring/probes/fixtures` UNCHANGED, grep-verified;
  test-file-only edit + one evidence JSON). Branch suite: weld **31/31** (was 30/30), full **38/38**, runner-registration
  green. **Opened PEER-GATED PR #165** (`loop/aloyoga-ucp-weld`, https://github.com/jnakagawa/agentic-readiness/pull/165);
  branch carries ONLY the test edit + evidence JSON; **review + self-merge owed NEXT cycle** (the UCP rail is volatile → the
  reviewing cycle re-runs the $0 live re-score as the regression check; a divergence there is REAL UCP-manifest drift, not a
  code regression). **Direct-to-main this fire:** loop docs + the evidence JSON ONLY — **main's weld test stays 30/30 (14
  members) until the peer gate merges**; `asrs/rubric/scoring/probes/fixtures` UNCHANGED on main; full suite 38/38; frozen
  +39.4 UNMOVED / live +30.1 (`verify_20260811T044102Z`; org 46.1 / com 76.2). Slack DM sent (weld = scoring-semantics
  change → veto visibility, not a gate). This MERGE (next fire) closes the UCP-rail weld campaign at 5 points (coffeecircle
  57.4 / gymshark 62.4 / hardgraft 66.9 / kith 70.3 / aloyoga 81.2 — the plane spanned on legibility 50.0→100.0 and trust
  33.33→100.0 at the fixed tx-50.0 rung). Evidence `runs/local/aloyoga_ucp_weld_confirm_20260811T044102Z.json`; PR #165;
  see LOG Local cycle 20260811T044102Z + BACKLOG P1.
- **✅ FIRST DUTY DONE — PEER-GATED PR #164 (thebotwire.com 404-dark ledger) REVIEWED SOUND + MERGED (`9b33da1`,
  2026-08-11T03:59:47Z); THEN the ONE [LOCAL] item committed the clean weld-visible cadence sweep ON-glob →
  UNLOCKS the aloyoga weld; bench GREEN 38/38 (Local 20260811T040401Z, TRUTH/INFRA — merge is the peer-gated
  first duty; on-glob sweep direct-to-main).** FIRST DUTY: adversarially reviewed PR #164 (opened LAST fire, so
  eligible now) on all three checklist legs. (1) OFF the static scoring path — three-dot diff since merge-base
  `8004739` = ONLY `experiments/documented_live_drift.json` (+15) + the obs-6 evidence JSON (+1024);
  asrs/rubric/scoring/probes/fixtures UNCHANGED. (2) LIVE RE-SCORE — ran a fresh $0 static cadence sweep
  (`experiments/calibration_sweep.py`, `_run_probes`→`scoring.score`, no `--behavioral`/`--max-pay`/zero-CLI/
  signing, inv #1) → `calibration_sweep_20260811T034627Z.json`: **thebotwire.com 25.0 F at OBS 7** (access 100.0/
  legibility 0.0/tx 0.0/trust 33.33, `claimed_archetypes` `[]`, caps empty) — **BYTE-IDENTICAL to obs 1–6** →
  persistence HOLDS (NOT recovered), documented-dark window now **~8h02m** (19:44:27Z→03:46:27Z), well past the
  driftflight ~7h precedent → correct to MERGE, not close. (3) TEETH re-derived on the BRANCH ledger via the REAL
  committed helpers (`_accepted_overalls`/`_divergences`): thebotwire accepts EXACTLY **[86.0 floor, 25.0 doc]**;
  live 25.0 accepted + genuinely compared (n_compared=1); recovery to 86.0 accepted (never masks a fix); a drift
  PAST 25.0 (tested 20.0) STILL FIRES; an undocumented value (tested 60.0) STILL FIRES. **VERDICT SOUND → MERGED**
  (`gh pr merge 164 --merge`). Main ledger now `{driftflight.com 76.2, thebotwire.com 25.0}`; Slack DM sent (merge
  visibility — a weld-teeth change; veto, not a gate). **THE ONE [LOCAL] ITEM (TRUTH, direct-to-main) — P1 step (3),
  the clean weld-visible sweep:** with thebotwire now ledgered on main, the fresh obs-7 sweep was committed ON the
  `calibration_sweep_*` weld glob (`calibration_sweep_20260811T034627Z.json`, force-added; 27/28 scored, rei.com
  not-scorable inv #4, 0 errors) — **thebotwire 25.0** (ledger-tolerated), **driftflight 76.2** (ledger-tolerated),
  **aloyoga.com 81.2 B BYTE-ON-FLOOR** a 7th time (access 100.0/legibility 100.0/tx 50.0/trust 100.0, honest
  `{physical_good, metered_api}`, caps empty) under `added_members`. Sweep drift vs the prior on-glob baseline
  `calibration_sweep_20260809T064456Z.json`: **2/26 moved, max |Δ| 61.0** — the ledgered `Δ -61.0 thebotwire
  86.0→25.0` + `Δ +4.6 wikipedia.org 41.1→45.7` (the KNOWN bistable 41.1↔45.7 non-storefront-control oscillation,
  not a pinned/welded asset, inv #4); every OTHER member **delta 0.0** (both anchors, all five UCP rails, the other
  two x402 rails, every frozen baseline, controls), `status_changed`/`removed` empty. **Full suite 38/38 WITH the
  on-glob sweep present** (weld tolerates both ledgered rails; aloyoga on-floor as a non-welded witness). This
  DISCHARGES the P2 aloyoga sweep-add DELIVERABLE → **UNLOCKS a future PEER-GATED aloyoga weld** (aloyoga →
  `_NON_ANCHOR_WELDED`, the 15th non-anchor / 5th UCP-rail member; n_compared=1 at 81.2, teeth = synthetic drift
  caught) — NOW the next cycle's forward item. Off-scoring-SEMANTICS on main = the MERGED ledger entry (peer-gated,
  reviewed) + the weld-visible sweep (evidence); asrs/rubric/scoring/probes/fixtures UNCHANGED; frozen +39.4
  UNMOVED / live +30.1 (`verify_20260811T034105Z`; org 46.1 / com 76.2). Evidence
  `runs/local/calibration_sweep_20260811T034627Z.json`; PR #164 (MERGED `9b33da1`); see LOG Local cycle
  20260811T040401Z + BACKLOG P1/P2.
- **✅ THEBOTWIRE.COM 404-DARK REGRESSION CROSSES THE ~7h LEDGER BAR AT OBS 6 — 25.0 again (BYTE-IDENTICAL to obs 1–5);
  documented-dark window now ~7h01m (19:44:27Z→02:45:55Z), MATCHING the driftflight ~7h ledger precedent → OPENED the
  PEER-GATED `documented_live_drift.json` ledger PR #164 (the PR #151 pattern; review + self-merge owed NEXT cycle, NOT this
  fire); aloyoga 81.2 B on-floor a 6th time; every other member byte-on-floor; bench GREEN 38/38 (Local 20260811T024555Z,
  TRUTH/INFRA — obs-6 sweep direct-to-main, ledger PR peer-gated; NO open PRs at fire start → no review owed).** Executed P1:
  ran the $0 static cadence sweep (`experiments/calibration_sweep.py`, `_run_probes`→`scoring.score`, no `--behavioral`/
  `--max-pay`/zero-CLI/signing, inv #1 by construction) → 27/28 scored, 1 not-scorable (rei.com inv #4), 0 errors →
  `calibration_sweep_20260811T024555Z.json`, immediately `mv`'d OFF the `calibration_sweep_*` weld glob to
  `runs/local/thebotwire_persistence_confirm_20260811T024555Z.json` (the obs-1..5 off-glob pattern — the down rail's honest
  fixture must not redden the weld un-ledgered; the weld tests glob the filesystem). **RESULT (obs 6, ~28 min after obs 5):**
  thebotwire.com **25.0 F** again, BYTE-IDENTICAL to obs 1–5 (leaf-by-leaf) — access **100.0** (server RESPONDS), legibility
  **0.0**, tx **0.0**, trust **33.33**, `claimed_archetypes` `[]`, caps empty → SIX consecutive byte-identical observations
  (19:44:27Z / 20:45:43Z / 21:45:53Z / 23:45:00Z / 02:17:33Z / 02:45:55Z) → the 404-dark decommission is STABLE across a
  **~7h01m** window, NOW matching the driftflight ~7h precedent. Sweep drift block (vs the newest on-glob baseline
  `calibration_sweep_20260809T064456Z.json`): **1/26 moved, max |Δ| 61.0** — SOLE mover `Δ -61.0 thebotwire 86.0 -> 25.0`;
  every OTHER member **delta 0.0** (both anchors 46.1/76.2, all FIVE UCP rails coffeecircle 57.4/gymshark 62.4/hardgraft
  66.9/kith 70.3/aloyoga 81.2, the other TWO x402 rails oracle 64.4/x402deploy 73.9, every frozen baseline, example.com 22.5
  + wikipedia 41.1 controls → no move), `status_changed` empty. **BONUS:** aloyoga.com **81.2 B BYTE-ON-FLOOR** a SIXTH
  independent time (access 100.0/legibility 100.0/tx 50.0/trust 100.0, honest `{physical_good, metered_api}`, caps empty),
  under `added_members`. **ACTION (step 2 fires — persistence crosses ~7h):** opened PEER-GATED **PR #164**
  (`loop/thebotwire-drift-ledger`, https://github.com/jnakagawa/agentic-readiness/pull/164): added a `thebotwire.com` entry to
  `experiments/documented_live_drift.json` (overall 25.0 + collapsed pillars {legibility 0.0, tx 0.0, trust 33.33} +
  `since_ts` 20260810T194427Z + a capability-term reason — total-content 404 decommission, all agent-native rails gone,
  server reachable, inv #4 — + obs-6 evidence). Re-derived `_accepted_overalls('thebotwire.com')` → **[86.0, 25.0]** and
  per-pillar accepts cover the live values; **teeth intact** (a drift PAST 25.0 [tested 20.0] still fires; a RECOVERY to 86.0
  always accepted); branch suite 38/38. Review + self-merge owed NEXT cycle (a further persistence obs IS the review's live
  re-score); Slack DM sent for veto visibility (a weld-teeth change). **Direct-to-main this fire:** obs-6 evidence (off-glob)
  + loop docs ONLY — main's `documented_live_drift.json` still carries ONLY the driftflight entry (the thebotwire entry lives
  on the PR branch until the peer gate merges it); asrs/rubric/scoring/probes/fixtures UNCHANGED on main; full suite 38/38;
  frozen +39.4 UNMOVED / live +30.1 (`verify_20260811T024104Z`). Evidence
  `runs/local/thebotwire_persistence_confirm_20260811T024555Z.json`; see LOG Local cycle 20260811T024555Z + BACKLOG P1 + PR #164.
- **✅ THEBOTWIRE.COM 404-DARK REGRESSION PERSISTS AT OBS 5 — 25.0 again (BYTE-IDENTICAL to obs 1–4); documented-dark
  window now ~6h33m (19:44:27Z→02:17:33Z), NOW within ~27m of the driftflight ~7h ledger bar → ledger PR HELD ONE more
  floor (next fire's obs 6 almost certainly crosses ~7h → then the peer-gated ledger PR); aloyoga 81.2 B on-floor a 5th
  time; every other member byte-on-floor; bench GREEN 38/38 (Local 20260811T021733Z, TRUTH/INFRA, direct-to-main — the ONE
  [LOCAL] item; NO open PRs at fire start → no review owed).** Continued P1 step (1b): re-ran the $0 static cadence sweep
  (`experiments/calibration_sweep.py`, `_run_probes`→`scoring.score`, no `--behavioral`/`--max-pay`/zero-CLI/signing, inv
  #1 by construction) → 27/28 scored, 1 not-scorable (rei.com inv #4), 0 errors → `calibration_sweep_20260811T021733Z.json`,
  immediately `git mv`'d OFF the `calibration_sweep_*` weld glob to
  `runs/local/thebotwire_persistence_confirm_20260811T021733Z.json` (the obs-1/2/3/4 off-glob pattern — the down rail's
  honest fixture must not redden the weld un-ledgered; the weld tests glob the filesystem). **RESULT (persistence, obs 5
  ~2h32m after obs 4 — the 00:41 & 01:41 improvement fires were skipped so the gap is ~2.5h not ~1h):** thebotwire.com
  **25.0 F** again, BYTE-IDENTICAL to obs 1–4 (leaf-by-leaf vs the obs-4 fixture) — access **100.0** (server RESPONDS),
  legibility **0.0**, tx **0.0**, trust **33.33**, `claimed_archetypes` `[]`, caps empty → five consecutive byte-identical
  observations (19:44:27Z / 20:45:43Z / 21:45:53Z / 23:45:00Z / 02:17:33Z) → the 404-dark decommission is STABLE across
  ~6h33m, not a flap, now ~27m short of the ~7h bar. Sweep drift block (vs the newest on-glob baseline
  `calibration_sweep_20260809T064456Z.json`, same baseline obs 1–4 used): **1/26 moved, max |Δ| 61.0** — SOLE mover
  `Δ -61.0 thebotwire 86.0 -> 25.0`; every OTHER member **delta 0.0** (both anchors 46.1/76.2, all FIVE UCP rails
  coffeecircle 57.4/gymshark 62.4/hardgraft 66.9/kith 70.3/aloyoga 81.2, the other TWO x402 rails oracle 64.4/x402deploy
  73.9, every frozen baseline, wikipedia control 41.1 low side → no move), `status_changed` empty. **BONUS:** aloyoga.com
  **81.2 B BYTE-ON-FLOOR** a FIFTH independent time (access 100.0/legibility 100.0/tx 50.0/trust 100.0, honest
  `{metered_api, physical_good}`, caps empty), under `added_members` — a fifth live witness for the pending
  (thebotwire-blocked) weld. **DECISION:** five obs across ~6h33m prove it stable and monotonic, now within ~27m of the
  driftflight precedent (~7h across floors) → HOLD the peer-gated ledger PR ONE more floor (with fires ~2.5h apart, obs 6
  next fire almost certainly crosses ~7h and becomes the trigger), keep the fresh sweep off-glob, bench stays HONESTLY
  green (pin/weld stand on the DELIBERATELY-frozen floor, inv #2). Note: the verify FLOOR only re-scores the canonical PAIR
  (thebotwire is a NON-anchor, untracked by the floor) — this manual cadence sweep is the ONLY mechanism documenting
  thebotwire's live persistence, so each fire's sweep adds a floor of record toward the ~7h bar. Step (2) — the peer-gated
  `documented_live_drift.json` ledger PR — is now queued for the NEXT fire; the aloyoga weld-unlock stays behind it.
  Off-scoring-SEMANTICS EMPTY (evidence JSON + loop docs only; experiments/asrs/rubric/scoring/probes/fixtures UNCHANGED);
  full suite 38/38; frozen +39.4 UNMOVED / live +30.1 (`verify_20260811T014104Z`). Evidence
  `runs/local/thebotwire_persistence_confirm_20260811T021733Z.json`; see LOG Local cycle 20260811T021733Z + BACKLOG P1.
- **✅ THEBOTWIRE.COM 404-DARK REGRESSION PERSISTS AT OBS 4 — 25.0 again (BYTE-IDENTICAL to obs 1, 2 & 3); documented-dark
  window now ~4h01m (19:44:27Z→23:45:00Z), STILL < the driftflight ~7h ledger bar → ledger PR HELD another floor; aloyoga
  81.2 B on-floor a 4th time; every other member byte-on-floor; bench GREEN 38/38 (Local 20260810T234500Z, TRUTH/INFRA,
  direct-to-main — the ONE [LOCAL] item; NO open PRs at fire start → no review owed).** Continued P1 step (1b): re-ran the
  $0 static cadence sweep (`experiments/calibration_sweep.py`, `_run_probes`→`scoring.score`, no `--behavioral`/`--max-pay`/
  zero-CLI/signing, inv #1 by construction) → 27/28 scored, 1 not-scorable (rei.com inv #4), 0 errors →
  `calibration_sweep_20260810T234500Z.json`, immediately `mv`'d OFF the `calibration_sweep_*` weld glob to
  `runs/local/thebotwire_persistence_confirm_20260810T234500Z.json` (the obs-1/2/3 off-glob pattern — the down rail's honest
  fixture must not redden the weld un-ledgered; the weld tests glob the filesystem). **RESULT (persistence, obs 4 ~2h after
  obs 3 — the 22:41 improvement fire was skipped so the gap is ~2h not ~1h):** thebotwire.com **25.0 F** again,
  BYTE-IDENTICAL to obs 1, 2 & 3 — access **100.0** (server RESPONDS), legibility **0.0**, tx **0.0**, trust **33.33**,
  `claimed_archetypes` `[]`, caps empty → four consecutive byte-identical observations (19:44:27Z / 20:45:43Z / 21:45:53Z /
  23:45:00Z) → the 404-dark decommission is STABLE across ~4h01m, not a flap, now past halfway to the ~7h bar. Sweep drift
  block (vs the newest on-glob baseline `calibration_sweep_20260809T064456Z.json`, same baseline obs 1–3 used): **1/26 moved,
  max |Δ| 61.0** — SOLE mover `Δ -61.0 thebotwire 86.0 -> 25.0`; every OTHER member **delta 0.0** (both anchors 46.1/76.2,
  all FIVE UCP rails coffeecircle 57.4/gymshark 62.4/hardgraft 66.9/kith 70.3/aloyoga 81.2, the other TWO x402 rails oracle
  64.4/x402deploy 73.9, every frozen baseline, wikipedia control 41.1 low side → no move). **BONUS:** aloyoga.com **81.2 B
  BYTE-ON-FLOOR** a FOURTH independent time (access 100.0/legibility 100.0/tx 50.0/trust 100.0, honest `{metered_api,
  physical_good}`, caps empty), under `added_members` — a fourth live witness for the pending (thebotwire-blocked) weld.
  **DECISION:** four obs across ~4h01m prove it is stable and monotonic, but still short of the driftflight precedent
  (~7h across floors) → HOLD the peer-gated ledger PR (step 2) another floor (~3 more at this cadence), keep the fresh sweep
  off-glob, bench stays HONESTLY green (pin/weld stand on the DELIBERATELY-frozen floor, inv #2). Note: the verify FLOOR only
  re-scores the canonical PAIR (thebotwire is a NON-anchor, untracked by the floor) — this manual cadence sweep is the ONLY
  mechanism documenting thebotwire's live persistence, so each fire's sweep adds a floor of record toward the ~7h bar.
  INFRA note: the 22:41 fire produced ONLY a verify floor (`e1b0215`), no `## Local cycle` — a single skipped improvement
  fire (~2h between improvement cycles), still UNDER the ~3h floor-only escalation bar; both intervening floors are
  `tests_ok:true` (no red accretion) → the 27h doom-loop has NOT recurred; noted, watch at each fire's infra step. Step (2)
  re-queued for a fire where persistence reaches a driftflight-comparable window; the aloyoga weld-unlock stays behind it.
  Off-scoring-SEMANTICS EMPTY (evidence JSON + loop docs only; experiments/asrs/rubric/scoring/probes/fixtures UNCHANGED);
  full suite 38/38; frozen +39.4 UNMOVED / live +30.1 (`verify_20260810T234105Z`). Evidence
  `runs/local/thebotwire_persistence_confirm_20260810T234500Z.json`; see LOG Local cycle 20260810T234500Z + BACKLOG P1.
<!-- The 20260810T214553Z thebotwire OBS-3 persistence banner (25.0 byte-identical to obs 1 & 2, documented-dark
     window ~2h01m, aloyoga 81.2 B on-floor a 3rd time, every other member byte-on-floor, ledger PR HELD another
     floor) is pruned this fire (Local cycle 20260811T044102Z) per the ~5-cycle rolling-log policy to defend STATE
     against re-accretion (the 27h doom-loop lesson) — preserved verbatim in loop/LOG.md
     (## Local cycle — 20260810T214553Z) + git history. The thebotwire regression is now MERGED-ledgered via PR #164
     across seven byte-identical observations (~8h02m); obs 4–7 banners remain above, and the aloyoga weld it
     blocked is now AUTHORED as PEER-GATED PR #165 (top banner). -->
- STATE mutable-working-state note: this compaction prunes a rolling cycle banner (NOT an append-only LOG/evidence
  file), so it is not an invariant-#5 rewrite.
<!-- The 20260810T210208Z obs-2 persistence banner (thebotwire.com 25.0 byte-identical to obs 1 ~50 min later,
     aloyoga 81.2 B on-floor a 2nd time, every other member byte-on-floor, step (1) DONE / ledger PR HELD) is pruned
     this fire (Local cycle 20260811T040401Z) per the ~5-cycle rolling-log policy to defend STATE against
     re-accretion (the 27h doom-loop lesson) — preserved verbatim in loop/LOG.md (## Local cycle — 20260810T210208Z)
     + git history. The regression is now MERGED-ledgered via PR #164 (top banner) across SEVEN byte-identical
     observations (~8h02m); obs 3–7 banners remain below. -->
- FLOOR-ONLY note (this fire): obs 7 (sweep 034627Z) landed ~1h after obs 6 (024555Z) — a normal improvement-cadence
  gap, NO new floor-only stall. The 27h doom-loop has NOT recurred; keep watching at each fire's infra step; escalate
  in the next digest if a fresh floor-only gap > ~3h appears.
<!-- The 20260810T200452Z ALOYOGA SWEEP-ADD / thebotwire-404-dark-DISCOVERY banner (obs 1: the aloyoga POPULATION add shipped
     81.2 B on-floor, AND the cadence sweep first CAUGHT thebotwire.com 86.0 → 25.0 — total-content 404 decommission, attributed
     to the SITE per inv #4 via re-score + curl; obs-1 sweep preserved off-glob as aloyoga_sweepadd_thebotwire_drift_20260810T194427Z.json)
     is pruned this fire (Local cycle 20260811T024555Z) per the ~5-cycle rolling-log policy to defend STATE against re-accretion
     (the 27h doom-loop lesson) — preserved verbatim in loop/LOG.md (## Local cycle — 20260810T200452Z) + git history. The
     regression is now documented across SIX byte-identical observations (~7h01m) and ledgered via PEER-GATED PR #164 (top
     banner); the P1 item + the thebotwire-blocked aloyoga weld-unlock live in BACKLOG. -->
<!-- The 20260810T174412Z ALOYOGA.COM 81.2 B PIN banner (COVERAGE, direct-to-main — the SEVENTEENTH frozen-replay baseline /
     FIFTH UCP-rail point / HIGH CORNER of the UCP plane: legibility 100 AND trust 100 both maxed at the fixed tx-50 rung,
     highest UCP overall of the five 81.2 > kith 70.3; guard test_ucp_retail_highcorner_storefront_replays_81_2 + EXPECTED
     + _REPLAY_CLEAN + _POPULATION ×5) is pruned this fire (Local cycle 20260811T021733Z) per the ~5-cycle rolling-log
     policy to defend STATE against re-accretion (the 27h doom-loop lesson) — preserved verbatim in loop/LOG.md
     (## Local cycle — 20260810T174412Z) + git history; the pin is DONE and its P2 frontier (a) + the (thebotwire-blocked)
     sweep-add/weld live in BACKLOG. -->
<!-- The 20260810T170728Z ALOYOGA METERED_API HONEST-CLASSIFICATION VETTING banner (COVERAGE/TRUTH, direct-to-main; verdict
     HONEST — aloyoga's metered_api = the same {post-endpoint, rate-limited} UCP class as the accepted gymshark/kith pins →
     the high-corner UCP pin UNBLOCKED [since PINNED + welded-pending]; bonus inv-#4 CATCH chubbiesshorts.com 67.1
     DISQUALIFIED, tiered-volume free-shipping-tier over-claim → the precision-guard candidate) is pruned this fire
     (Local cycle 20260810T234500Z) per the ~5-cycle rolling-log policy to defend STATE against re-accretion (the 27h
     doom-loop lesson) — preserved verbatim in loop/LOG.md (## Local cycle — 20260810T170728Z) + git history; the
     precision-guard candidate + the P2 frontier (a) detail live in BACKLOG. -->
<!-- The 20260810T144332Z INFRA SELF-HEAL banner (bench was RED ~27h from a STATE 600-line-accretion doom-loop; repaired
     per the 034d69d precedent — STATE compacted 600→~215, 28 red-bench verify_*.json git-rm'd, suite GREEN) is pruned this
     fire (Local cycle 20260810T214553Z) per the ~5-cycle rolling-log policy to defend STATE against re-accretion (the 27h
     doom-loop lesson) — preserved verbatim in loop/LOG.md (## Local cycle — 20260810T144332Z) + git history; the standing
     stall-doom-loop WATCH lives in BACKLOG. -->
<!-- STATE rolling-log COMPACTED this fire (Local cycle 20260810T144332Z) 600→~215 lines per the Cycle-260 policy
     (prune the rolling cycle log to the last ~5 cycles whenever STATE nears the 600-line hygiene cap); the pruned
     20260809T024925Z→010020Z banners + the older 2026-08-07/08 rolling entries are preserved verbatim in loop/LOG.md
     + git history. STATE is mutable working state (counter + focus pointer + open questions), NOT an append-only
     LOG/evidence file, so this compaction is NOT an invariant-#5 rewrite. -->
<!-- The 20260809T105834Z UCP TRANSACTABILITY-RUNG RECON banner (COVERAGE/TRUTH, direct-to-main; UCP served 14/18, NO
     merchant clears tx>50.0 — the tx axis is BIMODAL {50.0/43.75} on the sole `mcp_surface` sub-check, so the "distinct
     UCP tx rung" prize is $0-un-reachable for retail; surfaced aloyoga.com 81.2 B as a FUTURE pin lead — since PINNED +
     welded-pending) is pruned this fire (Local cycle 20260810T210208Z) per the ~5-cycle rolling-log policy to defend
     STATE against re-accretion (the 27h doom-loop lesson) — preserved verbatim in loop/LOG.md
     (## Local cycle — 20260809T105834Z) + git history; the structural finding lives in BACKLOG P2 step (6). -->
<!-- The two 20260809T094408Z banners (PR #163 kith-weld POST-MERGE review SOUND + the OWN-TOOL-DRIFT TRIPWIRE cadence
     GREEN, no 7th drift) are pruned this fire (Local cycle 20260810T200452Z) per the ~5-cycle rolling-log policy to
     defend STATE against re-accretion (the 27h doom-loop lesson) — both preserved verbatim in loop/LOG.md
     (## Local cycle — 20260809T094408Z) + git history. The #152–#163 non-anchor weld campaign stands COMPLETE at 14
     witnesses (UCP rail welded at 4 points); the standing own-tool-drift TRIPWIRE detail lives in the BACKLOG item. -->
<!-- kith.com precursor banners (SIXTEENTH baseline PIN 20260809T040201Z, guard
     test_ucp_retail_fourth_storefront_replays_70_3 + _REPLAY_CLEAN + _POPULATION ×5; weld-prerequisite SWEEP-ADD
     20260809T064456Z) — kith now pinned+welded+MERGED (PR #163, top banner); verbatim in loop/LOG.md + git history. -->
<!-- The 20260809T024925Z ACP/commerce-protocol well-known recon RE-RUN banner (COVERAGE/TRUTH, direct-to-main; ACP still
     0/32 at both well-known paths → the re-pathing lead stays CLOSED, UCP positive control held + grew 6→9 with fresh
     spanx/kith/brooklinen manifests) is pruned this fire (Local cycle 20260810T174412Z) per the ~5-cycle rolling-log
     policy to defend STATE against re-accretion (the 27h doom-loop lesson) — preserved verbatim in loop/LOG.md
     (## Local cycle — 20260809T024925Z) + git history. -->
<!-- The 20260809T015714Z CALIBRATION CADENCE SWEEP rolling banner (TRUTH, direct-to-main; all 15 pinned/welded members
     byte-on-floor, sole mover the wikipedia.org control's known 41.1↔45.7 oscillation) is pruned this fire (Local cycle
     20260810T170728Z) per the ~5-cycle rolling-log policy to defend STATE against re-accretion (the 27h doom-loop lesson)
     — preserved verbatim in loop/LOG.md (## Local cycle — 20260809T015714Z) + git history. -->

- FOCUS POINTER (cloud track — compacted Local cycle 20260809T064456Z to hold the STATE line cap; the full
  Cycle-295 pointer AND the 20260807T051750Z→174235Z ledger/campaign summary [PR #151 `140304e` RESOLVED the
  calibration-cadence blocker, unlocking the #152–#161 non-anchor weld + baseline-pin campaign] are preserved
  verbatim in loop/LOG.md + git history): NO open cloud peer-gated PR. Cloud rotation METHOD → COVERAGE → TRUTH →
  READOUT (Cycle 295 was METHOD → COVERAGE next). The LOCAL loop has carried the work for many cycles; if a cloud
  fire resumes, its first duty is the infra health check. The stale Cycle-295 "[LOCAL] frontier" list (add
  books.toscrape.com to the sweep, etc.) is long SUPERSEDED — the live frontier is the P2 UCP-depth / new-rail item
  in BACKLOG.

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
  UPDATE (2026-08-06T07:1xZ, Cycle 282 local fire): a FRESH full behavioral pair panel confirms the gate is
  time-varying — codex own-tool gated ALL FOUR canonical shopper trials this fire (both sides ×2; the ~20d
  reputation gate is back to fully CLOSED, vs 234505Z's t2 reach ~7h earlier). More important: a NEW near-miss
  leak phrasing slipped past even the Cycle-269 broadening — driftflight.com codex#2 "Interactive access to
  driftflight.com was denied before the homepage loaded" (the v0.7(a) alt requires "interactive BROWSER
  access"; the live phrasing dropped "browser") → counted as a valid all-false run (valid_runs=3 not 2),
  narrowing the WITH-side behavioral delta by scoring codex's own refusal as site evidence. drift-flight.org's
  two codex refusals used covered "browser security/permission" phrasing → correctly caught (valid_runs=2). So
  `_ENV_BLOCK_RE` STILL leaks; a fresh peer-gated P0 (BACKLOG top) carries the exact phrasing + guard. Evidence:
  `runs/local/behavioral_canonical_delta_20260806T064733Z/`.
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
  UPDATE (2026-08-06T07:1xZ, Cycle 282 local fire): the cross-model agreement question is now PARTLY answered
  on the TRUST axis. The trust panel runs via the separate `trust_probe` (NOT the gated hosted browser), so
  codex returned trust verdicts on BOTH canonical sides even though its shopper browser was gated 4/4. The two
  models INVERT: NO-rails drift-flight.org — claude warn+go (0.72) / codex refused (0.93); WITH-rails
  driftflight.com — claude refused (0.66, flags the agent-targeting manipulation copy) / codex warn+go (0.94,
  flags nothing). So cross-model TRUST agreement is measurable AND the models genuinely DISAGREE (weighting
  identity-verifiability vs manipulation-pattern risk differently). Still OPEN: the cross-model SHOPPER
  (checkpoint) agreement on the WITH side, blocked on codex browser reachability (RESULT 2, unchanged).
  Evidence: `runs/local/behavioral_canonical_delta_20260806T064733Z/report_*.json` (TRUST PANEL section).
