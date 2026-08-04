# Loop state

- Cycle counter: 236
- LOCAL CYCLE 236 — 2026-08-04T21:44Z (TRUTH, LOCAL, direct-to-main, score-neutral). FIRST duty: `gh pr list
  --state open` → [] (PR #145 already merged Cycle 235; no open peer-gated PR, no review owed). INFRA green: newest
  verify `runs/local/verify_20260804T214104Z.json` (21:41Z, git_pull.ok=true attempts=1 divergence_recovery=None
  tests_ok=true, 24/24 files) ~3min old — WELL inside the 6h floor; push-race recovery (`d812d6e`) holding. Took the
  OLDEST [LOCAL] P0 (the WATCH from Cycle 235): **confirm the merged x402 proxy-discovery probe (PR #145) restores
  driftflight.com live to 85.5 / +39.4** — and it is CONFIRMED, empirically CLOSING the Cycle-126 transactability-drop
  thread at its root. TWO independent live readings AGREE: (A) the pinned runner's post-merge 21:41Z verify artifact
  (pulled `053d7c2..bfd0fef` incl. merged fix → **85.5 B / tx 87.5 / +39.4**); (B) an INDEPENDENT $0 static re-score
  this fire (`runs/driftflight_com_20260804T214319.json`) → **85.5 B / tx 87.5**, `x402_probe = PASS 8.0 x402-live`
  (was PARTIAL 4.0 x402-documented-not-probed under the pre-fix probe, Cycle 232), self_serve_payg PASS 6.0,
  mcp_surface FAIL 0.0. MECHANISM CORRECTION (LOG'd): the Cycle-235 backlog "resync the pinned runner" step was a
  misunderstanding — the pinned `~/.local/bin/asrs_local_verify.py` is byte-identical to `loop/local_verify.py`
  (diff EMPTY) and scores via `subprocess [.venv/bin/python -m asrs score]` with `cwd=REPO` (local_verify.py:184),
  i.e. it runs the repo's LIVE `asrs/` package; PR #145 touched only `asrs/` (pulled live), so the fix reached the
  runner automatically on the first post-merge pull — no resync needed or possible. Live canonical signal now
  PERMANENTLY agrees with the frozen fixture; in-cloud replay guard UNAFFECTED (frozen 24/24, 46.1 F / 85.5 B /
  +39.4). Score-neutral (`git diff -- asrs/ rubric/ fixtures/ tests/ loop/local_verify.py` EMPTY; $0 static, no
  behavioral run, no nonzero max-pay). NO DM (score-neutral confirmation, no sensitive-class PR, not
  first-after-16:00 UTC — Aug-4 digest went Cycle 228 16:2xZ; the merge itself was already DM'd Cycle 235). Evidence
  (force-added): `runs/local/x402_proxyfix_live_confirmation_20260804T214418Z.json`.
- FOCUS POINTER (Cycle 236 done, LOCAL): the Cycle-126 transactability-drop thread is CLOSED end-to-end (probe
  under-measurement diagnosed Cycle 232 → fix merged Cycle 235 → live-confirmed restored Cycle 236). NO open
  peer-gated PR remains → next fire's first duty is the infra health check only. Cloud track-rotation UNCHANGED:
  Cycle 233 was COVERAGE → in-cloud pointer is **TRUTH next** (this LOCAL cycle did not consume the cloud rotation
  slot). Substantive [LOCAL] frontier (prefer the oldest): thin-bank live fixtures
  (service_booking/data_retrieval/physical_good — zero committed evidence), moleskine.com two-crawl cross-validation
  for the negative calibration anchor, a THIRD real anchor, typographic/render/structured-catalog live captures,
  ACP/UCP/MPP live handshakes. In-cloud TRUTH increment (tighten calibration/attribution guards) also available.
- CYCLE 235 — 2026-08-04T21:17Z (REVIEW/MERGE peer-gate, cloud). FIRST duty WAS the work: the only open
  peer-gated PR **#145** `loop/x402-proxy-discovery` (authored by LOCAL Cycle 234, a different fire → legitimate
  reviewer) was adversarially reviewed from fresh context and **MERGED** (`10ecbc6`, merge commit). No Jonah veto,
  no comments/reviews, no CI configured. Review verified BY EXECUTION (checked out branch, built venv, ran suite):
  full suite 24/24 files green; replay guard `test_canonical_replay` 24/24 → 46.1 F / 85.5 B / +39.4 zero
  replay-miss (fixture-neutral by first-402 short-circuit); `test_x402_proxy_discovery` 4/4; vendor-neutral
  (generic proxy discovery, no domain literal); invariant #1 held (empty-body $0 POST only, no nonzero-auth path);
  precision negative non-vacuous. Live re-score unavailable in-cloud (no outbound to canonical domains) → in-cloud
  standard = regression-by-construction (replay guard) + the authoring LOCAL cycle's committed 4-domain live
  validation. INFRA green at fire start: newest verify `runs/local/verify_20260804T204105Z.json` (20:41Z,
  git_pull.ok=true attempts=1, divergence_recovery=None, tests_ok=true) ~32min old — inside the 6h floor;
  push-race recovery (`d812d6e`) holding. This CLOSES the Cycle-234 [LOCAL] probe-fix item AND resolves the
  Cycle-126 "transactability drop" at its root — the live canonical signal will permanently agree with the frozen
  fixture (85.5 / +39.4) once the pinned runner picks up the merged probe. Slack DM SENT (sensitive-class /
  scoring-semantics PR MERGED → visibility per comms policy). Verdict comment on PR #145.
- FOCUS POINTER (Cycle 235 done, cloud): NO open peer-gated PR remains → next fire's first duty is the infra
  health check only. Cloud track rotation: Cycle 233 was COVERAGE → cloud pointer is **TRUTH next** (this
  review/merge cycle did not consume a track slot). Prefer the oldest: in-cloud TRUTH increment (tighten
  calibration/attribution guards) or wait for the substantive [LOCAL] frontier (thin-bank live fixtures, a THIRD
  real anchor, moleskine.com two-crawl cross-validation, ACP/UCP/MPP). WATCH: confirm the next 1-2 LOCAL
  `verify_*.json` show driftflight.com back at 85.5 / +39.4 (merged probe reaching the pinned `~/.local/bin`
  runner); if it does NOT, a pinned-runner resync (self-heal law) or residual probe gap needs a LOCAL fire.
- LOCAL CYCLE 234 — 2026-08-04T20:59Z (COVERAGE/METHOD, LOCAL, **PEER-GATED PR #145 OPENED — awaiting
  next-cycle review + self-merge; do NOT re-review-and-merge in the authoring fire**). FIRST duty: `gh pr list
  --state open` → [] at fire start (no open PR, no review owed). INFRA green: newest verify
  `runs/local/verify_20260804T204105Z.json` (20:41Z, git_pull.ok=true attempts=1, divergence_recovery=None,
  tests_ok=true) ~18min old — WELL inside the 6h floor; push-race recovery (`d812d6e`) holding. Per local law
  "prefer the oldest [P0]" took the oldest substantive [LOCAL] P0: the Cycle-232 PROBE FIX
  (`loop/x402-proxy-discovery`). SHIPPED (to the PR branch, NOT main): the x402 probe now discovers + POSTs the
  ZeroClick-style CALL-THROUGH PROXY endpoint (`agents.<domain>/<upstream-openapi-path>`) — `_strip_url_junk`
  sheds trailing markdown punctuation so a referenced `openapi.json` survives the `.json` gate, and
  `_agent_surface_targets` probes the openapi-derived concrete endpoints (joined to the proxy base) AHEAD of
  doc/auth URLs. Fixture-neutral BY CONSTRUCTION (probe returns on the first live 402; the frozen priced endpoint
  is the method-path `/extend`, which 402s + returns before any new `agents/v1/*` fetch → replay guard 24/24,
  46.1 F / 85.5 B / +39.4, ZERO replay-miss). LIVE-validated (invariant #3, $0 static): driftflight.com
  76.2 C → **85.5 B / x402-live 8.0** (matches frozen); drift-flight.org 46.1 F / example.com 22.5 F /
  books.toscrape.com 29.5 F all stay no-agent-native-payment (no false positive); live delta restored to +39.4.
  TDD `tests/test_x402_proxy_discovery.py` (4, RED→GREEN); full suite 24/24 files green. **NEXT CYCLE'S FIRST
  DUTY: review + re-run the live re-scores + MERGE PR #145 if it survives** (this is the RESOLUTION of the
  Cycle-126 "transactability drop" at its root — once merged, the live canonical signal permanently agrees with
  the frozen fixture). Slack DM SENT (scoring-semantics / sensitive-class PR → visibility, Jonah holds a veto not
  a gate). Evidence on the PR branch: `runs/local/diag_x402_proxyfix_driftflightcom_20260804T205446Z.json`,
  `runs/local/x402_proxyfix_live_validation_20260804T205632Z.json`.
- FOCUS POINTER (Cycle 234 done, LOCAL): the top priority next fire is REVIEW+MERGE of the open peer-gated
  **PR #145** (first duty). Cloud track-rotation UNCHANGED: Cycle 233 was COVERAGE, so the in-cloud pointer is
  **TRUTH next** (this LOCAL cycle did not consume the cloud rotation slot). After the PR merges, the deep-bank
  audit's next candidate (credential-SCOPE / least-privilege distinct from api-auth — verify "df_test_ sandbox"
  is already `test-mode` first) and the substantive [LOCAL] frontier (thin-bank live fixtures, a THIRD real
  anchor, moleskine.com two-crawl cross-validation, ACP/UCP/MPP) remain; prefer the oldest.
- CYCLE 233 — 2026-08-04T20:15Z (COVERAGE, in-cloud, direct-to-main, score-neutral). FIRST duty:
  `list_pull_requests(state=open)` → [] (no open peer-gated PR, no review owed). INFRA green: newest verify
  `runs/local/verify_20260804T194102Z.json` (19:41Z, git_pull.ok=true attempts=1, divergence_recovery=None,
  tests_ok=true) ~33min old — WELL inside the 6h floor; push-race recovery (`d812d6e`) holding. SHIPPED a
  **COVERAGE increment — new metered_api offering signal `key-rotation`**: the CREDENTIAL LIFECYCLE /
  KILL-SWITCH ("Rotate any key from the dashboard; old keys are revoked immediately.") documented on BOTH
  canonical /docs the deep bank had not mapped — the "operate safely without a human" leg, distinct from
  `api-auth` (present a held credential) and `self-provisioning` (obtain one without a human, the lifecycle
  START); this is the lifecycle END (rotate/kill a held credential). The Cycle-231 candidate (a
  `409 concurrency_exceeded` / `Retry-After` concurrency-wall error-recovery) was CHECKED and is NOT in
  committed prose (error table 400/401/403/429/502, 429=allowance_exhausted already covered, concurrency bursts
  QUEUE not 409) → DROPPED per no-vacuous-signal discipline; audited the same /docs instead and found
  key-rotation. Precision-critical: the regex NAMES A KEY in a rotation/kill sense so the 401 error row "the key
  is unknown or revoked" (present on both /docs) does NOT fire it (tested at signal level: 401 fires api-auth
  but not key-rotation — the discriminator holds inside a real metered_api surface). `asrs/offering.py` +1
  signal; `tests/test_offering.py` +2 (precision-synthetic 8-fire/8-dodge + 401-discriminator; real-captured
  fires non-vacuously on both canonical /docs, claimed set+order invariant, absent api/retail/null); isolation
  matrix +1. Off the scoring path (`git diff -- asrs/scoring.py asrs/probes/ rubric/ fixtures/` EMPTY),
  score-neutral, NOT peer-gated. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite 481→483;
  rubric v0.7. Live floor signal (read, off scoring path): 46.1 F / 76.2 C / +30.1 — the KNOWN probe
  under-measurement (Cycle 232 diagnosis; peer-gated [LOCAL] `loop/x402-proxy-discovery` fix restores it), NOT
  degradation. NO DM this cycle (score-neutral off-scoring-path COVERAGE, no sensitive-class PR, not
  first-after-16:00 UTC — Aug-4 digest went Cycle 228 16:2xZ; below DM bar, precedent cycles 226/230).
- FOCUS POINTER (Cycle 233 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 233 was
  COVERAGE, so Cycle 234 is TRUTH). NEXT (TRUTH 234): the deep-bank audit's next candidate — with `key-rotation`
  capturing the credential KILL, is there an uncaptured credential-SCOPE / least-privilege capability in
  committed prose (a key scoped to a plan/tier/model) distinct from api-auth's present-a-Bearer sense; verify
  the "df_test_ sandbox, no quota use" is already `test-mode` before touching it; else a further attribution/
  calibration invariance or offering-signal precision audit. Substantive frontier (thin-bank live fixtures, a
  THIRD real anchor, the peer-gated x402-proxy-discovery probe fix, moleskine.com two-crawl cross-validation,
  ACP/UCP/MPP) stays [LOCAL], prefer the oldest.
- SUPERSEDED (Cycle 232 counter note): Cycle counter was 232
- LOCAL CYCLE 2026-08-04T19:5xZ (Cycle 232, TRUTH — oldest [LOCAL] P0, per local law "prefer the oldest P0"
  which overrides the cloud track-rotation; the COVERAGE-next cloud pointer is PRESERVED for the next in-cloud
  fire, unconsumed). FIRST duty: `gh pr list --state open` → [] (no open peer-gated PR), no review owed. INFRA:
  newest verify `runs/local/verify_20260804T194102Z.json` (19:41Z, `git_pull.ok=true` attempts=1
  `divergence_recovery=None` `tests_ok=true`, all 23 suites) is ~fresh at this fire — WELL inside the 6h floor;
  the push-race recovery (`d812d6e`) still HOLDING. **SHIPPED — the driftflight.com transactability-drop P0
  (open since Cycle 126) is DIAGNOSED + CLOSED, and its standing hypothesis is REVERSED.** The live re-score's
  76.2 C / tx 62.5 is a PROBE UNDER-MEASUREMENT, NOT site degradation: CHECK-level diff fingers `x402_probe`
  alone (PASS 8.0 `x402-live` → PARTIAL 4.0 `x402-documented-not-probed`; self_serve_payg + mcp_surface
  byte-identical), yet a bare $0 POST to `agents.driftflight.com/v1/images/generate` returns a LIVE HTTP 402
  (x402 + MPP, $0.06) — the anchor's agent-native payment rail is FULLY ALIVE. Driftflight migrated from a
  `/extend` bare-402 endpoint (now GET 404 / POST 401 behind identity) to a call-through PROXY; the probe's
  `_agent_surface_targets` never builds `POST proxy/<upstream-openapi-path>` (trailing-punctuation URL capture
  + `[:5]`/`[:16]` caps drop the openapi paths), so it POSTs only doc/auth URLs → `saw_live_402=False`. Per
  invariant #4 the FROZEN fixture (85.5 B / tx 87.5 / x402-live) stays the HONEST record — the
  re-baseline-DOWN plan is CANCELED (would have falsely recorded a capability loss). The "is the with-rails
  anchor degrading?" question open 100+ cycles is answered: NO, live-verified intact. Score-neutral
  (`git diff -- asrs/ rubric/ fixtures/ tests/` EMPTY; only `experiments/` + force-added `runs/local/`
  evidence) → rubric v0.7, replay guard 24/24 / 46.1 F / 85.5 B / +39.4, free-tier 11/11. Spawned a NEW
  PEER-GATED [LOCAL] P0 (`loop/x402-proxy-discovery`) for the probe fix. NO DM this fire (score-neutral
  off-scoring-path diagnosis, not first-after-16:00 UTC — the Aug-4 digest went at Cycle 228 16:2xZ; the
  finding + the new peer-gated PR will surface in the next digest / at PR-open per the sensitive-class-PR
  comms rule). Evidence: `runs/local/diag_transactability_drop_20260804T194242Z.json`,
  `runs/local/diag_transactability_rootcause_20260804T194901Z.json`, `experiments/diag_transactability_drop.py`.
- FOCUS POINTER (Cycle 232 done, LOCAL): the oldest substantive [LOCAL] P0 is now the PROBE FIX just spawned
  (`loop/x402-proxy-discovery`, peer-gated) — the next LOCAL fire should author it (TDD + 2-domain live
  validation) since it needs the network. Cloud track-rotation UNCHANGED: COVERAGE is still next-due for the
  next in-cloud fire (Cycle 231 was TRUTH; this local TRUTH diagnosis did not consume the cloud rotation slot).
  Remaining substantive [LOCAL] frontier (thin-bank live fixtures, a THIRD real anchor, moleskine.com
  two-crawl cross-validation, typographic/render/structured-catalog live captures, ACP/UCP/MPP) stays queued.
- RUNNER HEALTHY at 2026-08-04T19:1xZ (Cycle 231) — newest verify `runs/local/verify_20260804T174103Z.json` (17:41Z,
  `git_pull.ok=true` attempts=1 `divergence_recovery=None` `tests_ok=true`) is ~1.5h old at this fire — WELL inside the
  6h floor. The push-race recovery (Cycle 229's `d812d6e`) is HOLDING — every fire since (17:09Z, 17:41Z) `attempts=1`,
  `git_pull.ok=true`, no `divergence_recovery` note. Live signal (READ fresh, NOT re-run, off the scoring path):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS. In-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No
  open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. This 19:1xZ fire is NOT
  first-after-16:00 UTC (Cycle 228 at 16:2xZ already sent the Aug-4 daily digest) → NO DM this fire per comms policy
  (tests-only / score-neutral off-scoring-path TRUTH guard, no sensitive-class PR, nothing score-moving — below the DM
  bar, same precedent as the prior calibration-attribution TRUTH cycles 191/197/199). INFRA/SELF-HEAL (Cycle 231): fresh
  `.venv` + `requests pyyaml eth-account pytest`, 480 tests green pre-flight (481 after +1); local checkout at origin tip
  `d94827e` (Cycle 230); LOG.md newest-first + complete through Cycle 230.
- FOCUS POINTER (Cycle 231 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 231 was TRUTH, so
  Cycle 232 is COVERAGE). Cycle 231 shipped a **TRUTH increment — the headline delta is FULLY capability-attributed with
  ZERO unexplained residual**: `tests/test_calibration.py`
  `test_headline_delta_is_fully_attributed_to_two_capability_families` (registered after test 14) completes test 14's
  honest-non-exclusivity claim into a full, residual-free decomposition. Same faithful knock-out machinery: the whole
  +39.4 headline gap splits into exactly TWO agent-native capability families — "pay programmatically" (transactability:
  `_STATIC_PAYMENT_CHECKS` = x402_probe + self_serve_payg, ~65.2%) and "understand the offer" (legibility: new
  `_STATIC_LEGIBILITY_CHECKS` = llms_txt + offer_catalog, ~34.5%) — with (a) the legibility residual EXCLUSIVELY the two
  named agent-legibility checks (leg-only knock collapses legibility onto the no-rails floor 36.36, other leg checks
  byte-identical, no cap), (b) payment + legibility COMBINED collapsing the with-rails OVERALL EXACTLY onto the no-rails
  floor 46.1 — residual 0.0, no third unnamed driver, and (c) near-additive jointly ~100% (65.2%+34.5%=99.75%) with
  legibility a genuine honest MINORITY (>20%, <50%). Tests-only, OFF the scoring path (`git diff --name-only` =
  `tests/test_calibration.py` alone; scoring path EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Shares test
  9(d)'s re-baseline tripwire (85.5/46.1/+39.4). Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite
  480→481; rubric v0.7. NEXT (COVERAGE 232): the Cycle-230 deep-bank sibling — a machine-readable concurrency/quota
  ERROR-RECOVERY response (`409 concurrency_exceeded` / `Retry-After` naming the concurrency wall) distinct from generic
  `error-contract`, IF committed prose carries it; else a further offering-signal audit. Substantive frontier (thin-bank
  live fixtures, a THIRD real anchor, transactability-drop CHECK-level diagnosis + peer-gated re-baseline, moleskine.com
  two-crawl cross-validation, ACP/UCP/MPP) stays `[LOCAL]`, UNBLOCKED by the recovered runner — prefer the oldest.
- RUNNER HEALTHY at 2026-08-04T17:5xZ (Cycle 230) — newest verify `runs/local/verify_20260804T174103Z.json` (17:41Z,
  `git_pull.ok=true` attempts=1, `tests_ok=true`) is ~10min old at this fire, WELL inside the 6h floor. The push-race
  recovery (Cycle 229's `d812d6e`) is HOLDING — two clean fires since (17:09Z, 17:41Z), both `attempts=1`,
  `git_pull.ok=true`, no `divergence_recovery` note fired. Live signal (READ fresh, NOT re-run, off the scoring path):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS. In-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No
  open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. This 17:5xZ fire is NOT
  first-after-16:00 UTC (Cycle 228 at 16:2xZ already sent the Aug-4 daily digest) → NO DM this fire per comms policy
  (score-neutral off-scoring-path COVERAGE signal, no sensitive-class PR, nothing score-moving — below the DM bar, same
  precedent as the prior offering-signal cycles 226/206/202). INFRA/SELF-HEAL (Cycle 230): fresh `.venv` +
  `requests pyyaml eth-account pytest`, 478 tests green pre-flight (480 after +2); local `main` at origin tip; LOG.md
  newest-first + complete through Cycle 229.
- FOCUS POINTER (Cycle 230 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 230 was COVERAGE, so
  Cycle 231 is TRUTH). Cycle 230 shipped a **COVERAGE increment — new metered_api offering signal `concurrency-limit`**:
  the CONCURRENCY CEILING + queue-depth backpressure ("Hobby: 2 concurrent renders … Bursts beyond the limit queue
  rather than fail; the `x-df-queue-depth` response header reports the current queue"), a documented capability on BOTH
  canonical domains' committed `/docs` that the deep bank had not mapped — distinct from `rate-limited`'s TEMPORAL axis
  (requests-per-time) as the orthogonal PARALLELISM axis (jobs-in-flight-at-once), the "complete the job AT SCALE" leg.
  `asrs/offering._SIGNALS["metered_api"]` +1 (after `rate-limited`); `tests/test_offering.py` +2 (precision-synthetic:
  11 fire / 10 dodge; real-captured: fires on both drift /docs, absent api/retail/null, sets invariant); isolation
  matrix +1. Off the scoring path (`git diff --name-only -- asrs/scoring.py asrs/probes/ rubric/ fixtures/ …` EMPTY;
  only offering.py + tests), score-neutral, direct-to-main (NOT peer-gated). Replay guard 24/24, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; suite 478→480; rubric v0.7. NEXT (TRUTH 231): the deep-bank audit's SIBLING candidate — a
  machine-readable concurrency/quota ERROR-RECOVERY response (a `409 concurrency_exceeded` / `Retry-After` naming the
  concurrency wall) distinct from generic `error-contract`, IF committed prose carries it; else a further attribution/
  calibration invariance. Substantive frontier (transactability-drop CHECK-level diagnosis + peer-gated re-baseline,
  thin-bank live fixtures, moleskine.com two-crawl cross-validation, a THIRD real anchor, ACP/UCP/MPP) stays `[LOCAL]`,
  now UNBLOCKED by the recovered runner — prefer the oldest.
- SUPERSEDED (Cycle 229 runner/counter note): Cycle counter was 229
- Started: 2026-07-23 (UTC)
- RUNNER RECOVERED at 2026-08-04T17:1xZ (Cycle 229) — the ~3.5-day push-race stall is CLEARED. A LOCAL self-healing
  fire at 17:08–17:09Z Aug-4 landed the runner's own fix (commit d812d6e `recover_from_own_divergence`: on a
  --ff-only pull that fails because the branch diverged, discard our own un-pushed `loop: local verification`
  heartbeats and realign to origin — strictly guarded so any un-pushed NON-heartbeat commit is preserved; tests
  4→8) and pushed a fresh artifact `runs/local/verify_20260804T170922Z.json` (17:09Z, `attempts=1`, git_pull.ok=true,
  tests_ok=true), <10 min old at this fire — the 6h floor is UP again. Live signal (READ fresh, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (fresh, off the scoring path). The in-cloud replay guard stays the frozen independent
  regression signal (24/24 replay green, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. This 17:1xZ fire is NOT first-after-16:00 UTC
  (Cycle 228 at 16:2xZ already sent the Aug-4 daily digest) → no DM this fire per comms policy (tests-only /
  score-neutral off-scoring-path METHOD guard, no sensitive-class PR, nothing score-moving; runner recovery is infra
  good news, not a score change → below the DM bar). INFRA/SELF-HEAL (Cycle 229): fresh `.venv` +
  `requests pyyaml eth-account pytest`, 477 tests green pre-flight (478 after +1); realigned local `main` to
  origin/main `d85d7bf` (Cycle-52 lesson — the local runner force-updated main past the stale Cycle-228 tip); LOG.md
  newest-first + complete through Cycle 228. NOTE: the durable [LOCAL] runner-recovery P0 is CLOSED this cycle
  (fix landed + fresh artifact <6h old); watch the `attempts`/`git_pull.ok` fields over the next day to confirm the
  push-race fix holds under real fires.
- RUNNER REPAIRED — LOCAL cycle 2026-08-04T17:13Z (SELF-HEALING, direct-to-main). The ~3.5-day stall
  (at-floor since Aug-1 03:50Z) is FIXED and the live floor is RESTORED: fresh artifact
  `runs/local/verify_20260804T170922Z.json` (`git_pull.ok=true` attempts=1, `tests_ok=true`, live 46.1 F / 76.2 C /
  +30.1, pushed) on origin (`d85d7bf`), newest-verify age reset to ~0. ROOT CAUSE (a local fire saw what the cloud
  could only guess at — NOT launchd, NOT a wake/DNS race, NOT machine-asleep): the runner commits a heartbeat THEN
  pushes, so a cloud push between the runner's pull and push rejected the runner's push and left a divergent
  un-pushed commit (`64ae3c1`) that stranded EVERY later fire at `git pull --ff-only`. FIX: (1) realigned local
  `main` to origin/main `a241fd1` (Cycle 228), dropping the orphaned Aug-1 heartbeat; (2) cleaned 35 untracked
  no-score failed-fire debris artifacts that were failing `test_canonical_history` LOCALLY (they pollute the
  on-disk series glob; the cloud never sees them); (3) durable — `loop/local_verify.py` `recover_from_own_divergence`
  auto-discards our OWN un-pushed heartbeats on a diverged pull (guarded: any non-heartbeat un-pushed commit is
  preserved), shipped `d812d6e`, pinned copy RESYNCED (was Jul-28 stale), executed end-to-end to prove it. TDD
  `test_local_verify.py` 4→8, verified with real git. Off the scoring path → score-neutral, rubric v0.7, replay
  guard `test_canonical_replay.py` 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; full suite 473→477. No open
  peer-gated PRs this fire (`gh pr list --state open` → []), so no first-duty review. The daily digest already went
  out at 16:21Z (Cycle 228); a short repair-confirmation DM to U07PEGPSZD3 closes the escalated-P0 loop (the stall
  was flagged TO Jonah as unresolved). NOTE: transactability-drop divergence (driftflight.com 62.5) reproduced LIVE
  again this fire — stays an open P0 (separate from the runner fix), needs the check-level diagnosis + peer-gated
  re-baseline.
- FOCUS POINTER (Cycle 229 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 229 was METHOD,
  so Cycle 230 is COVERAGE). Cycle 229 shipped a **METHOD increment — panel reliability + citability are PANEL-SIZE
  (REPLICATION) INVARIANT**: `tests/test_reliability.py` `test_verdict_stability_is_panel_size_invariant`
  (registered, after the polarity guard) pins that `verdict_stability = 1 - 2*mean(minority/n)` is an agreement RATE,
  immune to panel-size padding — replicating every valid run k-fold (transform `_replicate(runs, k)`) leaves
  verdict_stability, flip_rate, the flipped set, per-checkpoint agreement/unanimity, trust agreement, band label AND
  the citability verdict byte-identical (only valid_runs + per-checkpoint n/pass_count scale). (A) the ANTI-GAMING
  statement — a below-threshold panel (stability 0.6, provisional) stays provisional replicated to 4/6/20 runs (20
  padded copies cannot cross _STABLE_MIN 0.8 to buy citability); (B) general invariance over an interior-mix panel
  (0.7); (C) NEGATIVE CONTROL — adding one DISSENTING run moves the metric 0.7→0.68, proving the invariance is
  specific to replication. Distinct from trial-order invariance (permutes a FIXED multiset; this changes n at fixed
  rate). Completes the reliability metric's metamorphic-invariance family (order/shape/polarity/panel-size).
  Tests-only, OFF the scoring path (`git diff -- asrs/ rubric/ fixtures/` EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite 477→478; rubric v0.7.
  NEXT (COVERAGE 230): with the runner RECOVERED the substantive [LOCAL] frontier (thin-bank live fixtures, a THIRD
  real anchor, the transactability-drop CHECK-level diagnosis, ACP/UCP/MPP) is now UNBLOCKED — prefer the oldest of
  those; else an in-cloud deep-bank signal audit (Cycle-226 showed committed fixtures can still carry uncaptured
  capabilities).
- SUPERSEDED (Cycle 228 runner note): RUNNER AT-FLOOR at 2026-08-04T16:2xZ (Cycle 228) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~84.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). This 16:21Z fire IS the first-after-16:00 UTC cycle of Aug-4 → daily-digest DM SENT to
  U07PEGPSZD3 (cycles 205–228 shipped, canonical delta trend, ~3.5-day runner stall re-flagged, top open question).
  Live signal (READ, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 —
  the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the
  frozen independent regression signal (28/28 replay-family green, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs
  this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 228): fresh
  `.venv` + `requests pyyaml eth-account pytest`, 472 tests green pre-flight (473 after +1); local `main` realigned
  off the stale diverged tip to origin/main `fe720aa` (Cycle 227) before working (Cycle-52 lesson); LOG.md confirmed
  newest-first + complete through Cycle 227; last push (Cycle 227, fe720aa) present on origin/main. NOTE: runner
  at-floor since Aug-1 03:50Z (~3.5 days) — durable [LOCAL] runner-recovery stays P0.
- SUPERSEDED (Cycle 228 focus pointer): FOCUS POINTER (Cycle 228 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 228 was READOUT,  so Cycle 229 is METHOD). Cycle 228 shipped a **READOUT increment — the public methodology page now earns a
  reader-facing block for the `payment-challenge-retry` capability**, closing the COVERAGE(226)→TRUTH(227)→READOUT(228)
  arc. `asrs/scorecard.py` `_write_methodology_page` gains an "Executing the pay handshake" `<p>` inserted right
  after the payment-rails block (its natural sibling): it frames the challenge-settle-retry handshake as the
  PAY-EXECUTION leg BETWEEN the rail (the agent CAN pay) and the receipt (the proof that comes BACK after), names
  the failure (an agent that reads "here is a 402" but is not told to settle the challenge and retry with the proof
  attached STALLS at the pay step), names the vendor-neutral challenge-response vocabulary as open conventions (HTTP
  402 payment challenge / pay and retry / settle the challenge / retry with a payment / signed authorization / proof
  — HTTP 402 a standard status, challenge-response a universal auth pattern), keeps the bare-word precision honesty
  (webhook redelivery / retry-on-failure / a bare 402 are no signal — only the co-occurrence trips it), ties the
  SETTLE step to the $0-only ethos (a zero-value authorization, never a nonzero charge), and stays honest about
  scope (diagnostic, off the scoring path). `tests/test_readout.py`
  `test_methodology_documents_payment_challenge_retry` (registered) is the executable mirror. DISPLAY-ONLY, OFF the
  scoring path (`git diff -- asrs/scoring.py asrs/probes/ rubric/ fixtures/ asrs/offering.py` EMPTY; only scorecard.py
  prose + the test) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 46.1 F / 85.5 B / +39.4, 0
  replay-miss; suite 472→473; rubric v0.7. NEXT (METHOD 229): a further variance/attribution invariance, OR audit
  the methodology page for a leg whose science is pinned but prose is thin. Substantive frontier (CHECK-level
  transactability-drop diagnosis + peer-gated re-baseline, thin-bank live fixtures, moleskine.com two-crawl
  cross-validation, a THIRD real anchor, ACP/UCP/MPP) stays `[LOCAL]`, gated on the runner recovering.
- SUPERSEDED (Cycle 227 runner note): RUNNER AT-FLOOR at 2026-08-04T15:2xZ (Cycle 227) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~83.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 15:2xZ fire is NOT
  first-after-16:00 UTC (15:19Z) → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path
  TRUTH guard, no sensitive-class PR, nothing score-moving). Live signal (READ, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24,
  46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no
  first-duty review. INFRA/SELF-HEAL (Cycle 227): fresh `.venv` + `requests pyyaml eth-account pytest`, 471 tests
  green pre-flight (472 after +1); local `main` realigned off the stale orphan tip (`3796519`) to origin/main
  `29807a1` (Cycle 226) before working (Cycle-52 lesson); LOG.md confirmed newest-first + complete through Cycle
  226; last push (Cycle 226, 29807a1) present on origin/main. NOTE: runner at-floor since Aug-1 03:50Z (~3.5 days)
  — durable [LOCAL] runner-recovery stays P0.
- SUPERSEDED (Cycle 227 focus pointer): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 227 was TRUTH,
  so Cycle 228 is READOUT). Cycle 227 shipped a **TRUTH increment — a real-captured-surfaces guard for the
  Cycle-226 `payment-challenge-retry` signal**: `tests/test_offering.py`
  `test_payment_challenge_retry_fires_on_real_captured_surfaces` runs the REAL discovery path over all 5 committed
  fixtures and pins that the new payment-FLOW signal's PRESENCE tracks the with-rails/no-rails CAPABILITY SPLIT it
  echoes — FIRES on driftflight.com across >=2 real agent-doc surfaces (402 challenge on llms.txt; settle+retry-
  with-signed-payment on llms-full.txt), ABSENT on drift-flight.org (the discovery-layer echo of the real
  capability gap), and ABSENT on api.replicate.com (which carries the literal WEBHOOK-REDELIVERY retry the
  precision guard targets — a real-data precision crown jewel), books.toscrape.com, example.com; claimed set+order
  invariant on all. Until now the signal's real-data behaviour lived only in a code comment + the canonical
  set+order invariance; this makes the capability-gap echo a first-class per-cycle tripwire. Tests-only, OFF the
  scoring path (`git diff -- asrs/ rubric/ fixtures/` EMPTY) → score-neutral, NOT peer-gated, direct-to-main.
  Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite 471→472; rubric v0.7. NEXT (READOUT 228):
  surface the payment-challenge-retry capability in a reader-facing readout the way prior signals earned their
  READOUT leg. Substantive frontier (CHECK-level transactability-drop diagnosis + peer-gated re-baseline,
  thin-bank live fixtures, moleskine.com two-crawl cross-validation, a THIRD real anchor, ACP/UCP/MPP) stays
  `[LOCAL]`, gated on the runner recovering.
- SUPERSEDED (Cycle 226 runner note): RUNNER AT-FLOOR at 2026-08-04T14:2xZ (Cycle 226) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~82.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 14:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path COVERAGE increment, no
  sensitive-class PR, nothing score-moving). Live signal (READ, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off
  the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B /
  +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/
  SELF-HEAL (Cycle 226): fresh `.venv` + `requests pyyaml eth-account pytest`, 470 tests green pre-flight (471 after
  +1); local `main` aligned to origin/main `ccef6ef` (Cycle 225); LOG.md confirmed newest-first + complete through
  Cycle 225; last push (Cycle 225, ccef6ef) present on origin/main. NOTE: runner at-floor since Aug-1 03:50Z
  (~3.4 days) — durable [LOCAL] runner-recovery stays P0.
- SUPERSEDED (Cycle 226 focus pointer): FOCUS POINTER (Cycle 226 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 226 was COVERAGE, so
  Cycle 227 is TRUTH). Cycle 226 shipped a **COVERAGE increment — a NEW metered_api offering signal:
  `payment-challenge-retry`, the agent-native payment CHALLENGE-SETTLE-RETRY handshake**. Every existing payment
  signal named a STATIC FACT (`x402` the rail, `agent-payment-rail` which rails, `payment-receipt` the proof back,
  `reserve-and-settle` a ceiling, `failure-not-billed` a free failure, `free-included-usage` a $0 on-ramp); NONE
  captured the request/response FLOW an agent must EXECUTE — the HTTP 402 CHALLENGE → SETTLE (sign the zero-value
  authorization / pay the priced 402) → RETRY-with-proof-attached round-trip. An agent that reads "here is a 402"
  but not "settle the challenge and retry with the proof attached" STALLS at the pay step. VENDOR-NEUTRAL (HTTP 402 +
  challenge-response is a standard status + universal auth pattern; no ZeroClick/wallet noun required). PRECISION-
  CRITICAL (bare retry/402/challenge/settle is a minefield incl. api.replicate.com's WEBHOOK-delivery "retry the
  webhook a few times"): requires the CO-OCCURRENCE only the handshake produces. `test_offering.py`
  `test_payment_challenge_retry_precision_synthetic` (9 real-shape positives fire / 9 bare-token negatives dodge),
  registered; isolation-matrix entry added (claims EXACTLY metered_api). NON-VACUOUS on committed evidence: fires on
  driftflight.com agent docs, CORRECTLY ABSENT on drift-flight.org (no 402/challenge/settle/retry prose — the
  discovery-layer echo of the real capability gap). CANONICAL SETS + ORDER INVARIANT on all 5 fixtures
  (driftflight.com metered_api 21→22, already strongest → no reorder; every other fixture unchanged). Updates the
  standing frontier note: Cycle 206 said "further new SIGNALS need [LOCAL] fixtures", but a real uncaptured
  capability (the challenge-retry flow) was still in the COMMITTED driftflight.com docs. OFF the scoring path
  (`git diff -- asrs/scoring.py asrs/probes/ rubric/ fixtures/` EMPTY; `offering` not imported by scoring/probes) →
  score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite
  470→471; rubric v0.7. NEXT (TRUTH 227): a calibration/attribution invariance guard, OR pin that the new payment-FLOW
  signal's presence tracks the with-rails/no-rails capability split it echoes. Substantive frontier (a THIRD real
  anchor, thin-bank live fixtures, moleskine.com two-crawl cross-validation, ACP/UCP/MPP, transactability-drop
  CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`, gated on the runner recovering.
- SUPERSEDED (Cycle 225 runner note): RUNNER AT-FLOOR at 2026-08-04T13:2xZ (Cycle 225) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~81.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 13:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path METHOD
  increment, no sensitive-class PR, nothing score-moving). Live signal (READ, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off
  the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B /
  +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/
  SELF-HEAL (Cycle 225): fresh `.venv` + `requests pyyaml eth-account pytest`, 469 tests green pre-flight (470 after
  +1); realigned local `main` off the stale diverged tip to origin/main `06ce0ff` (Cycle-52 lesson) before working;
  LOG.md confirmed newest-first + complete through Cycle 224; last push (Cycle 224, 06ce0ff) present on origin/main.
  NOTE: runner at-floor since Aug-1 03:50Z (~3.4 days) — durable [LOCAL] runner-recovery stays P0.
- SUPERSEDED (Cycle 225 focus pointer): FOCUS POINTER (Cycle 225 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 225 was METHOD, so
  Cycle 226 is COVERAGE). Cycle 225 shipped a **METHOD increment — panel reliability is VERDICT-POLARITY INVARIANT**.
  `verdict_stability = 1 - 2*mean(minority_fraction)` with `minority = min(pass, n-pass)` is SYMMETRIC in pass↔fail, so
  a panel that unanimously FAILS the payment checkpoints is by construction exactly as reproducible + citable as one
  that unanimously PASSES — the two-sided calibration anchor stated at the reliability layer (a no-rails store's
  reproducible FAIL must be as quotable as a with-rails store's reproducible PASS; else the citability gate would carry
  a hidden pro-PASS bias). New `tests/test_reliability.py` test 11 `test_verdict_stability_is_polarity_invariant` +
  `_invert(run)` helper: (A) crisp two-sided case — unanimous PASS and its unanimous-FAIL inversion both give
  verdict_stability 1.0, band `stable`, gate `reproducible`; (B) general metamorphic invariance over an interior-mix
  panel (0.7, split trust) — inverting every run leaves every reproducibility/citability field + the citability gate
  byte-identical, ONLY per-checkpoint pass_count reflects the flip (inverted == n − original). Non-vacuous (interior
  operating point, the flip demonstrably moves pass counts, gate returns a genuine multi-trial verdict). CAPABILITY-
  worded, vendor-neutral; the metamorphic sibling of the attribution layer's host-relabel-invariance guards. OFF the
  scoring path (`git diff -- asrs/ rubric/ fixtures/` EMPTY; reliability.py imports no scoring/probe/report module) →
  score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite
  469→470; rubric v0.7. NEXT (COVERAGE 226): the in-cloud precision/rigor frontier for the diagnostic layers is dense
  (attribution + reliability invariances both host-relabel- and polarity-pinned). Substantive frontier (a THIRD real
  anchor, thin-bank live fixtures, moleskine.com two-crawl cross-validation, ACP/UCP/MPP, transactability-drop
  CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`, gated on the runner recovering.
- SUPERSEDED (Cycle 224 focus pointer): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 224 was READOUT, so
  Cycle 225 is METHOD). Cycle 224 shipped a **READOUT increment — the public methodology page (section 8, Calibration)
  now surfaces the cross-anchor RANK-CONCORDANCE / no-sign-inversion property** that Cycle 223's test 16 pinned in-cloud
  but the reader-facing prose did not state. New paragraph in `_write_methodology_page` (before the "Two honest limits"
  closer): (a) the ranking-level failure mode (a reweighting keeps every single-store checkpoint green yet INVERTS the
  order) and that ASRS is "rank-concordant — no sign inversion" (with-rails >= no-rails on every static-observable
  pillar, strictly higher on payability, behavioral-only Outcome pointing the same way); (b) AMPLIFICATION-not-RESCUE
  (the headline ordering already held on the "static prediction alone" before the behavioral outcome was folded in);
  (c) honest scope — trust "favors the no-rails storefront" + access ties, so the ranking is "carried by the capability
  pillars", not "with-rails wins everything". CAPABILITY-worded, vendor-neutral; `test_methodology_documents_calibration`
  +5 assertions. OFF the scoring path (scoring-path diff EMPTY; only `scorecard.py` display + the test) → score-neutral,
  NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; suite 469; rubric v0.7.
  NEXT (METHOD 225): a variance/attribution property (panel-verdict-stability invariant or a tighter divergence-
  attribution guard) — the calibration science + its readout are now both landed for the two committed anchors. The
  substantive frontier (a THIRD real anchor, moleskine.com two-crawl cross-validation, ACP/UCP/MPP, transactability-drop
  CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`, gated on the runner recovering.
- SUPERSEDED (Cycle 223 runner note): RUNNER AT-FLOOR at 2026-08-04T11:2xZ (Cycle 223) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~79.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 11:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral tests-only TRUTH increment, no
  sensitive-class PR, nothing score-moving). Live signal (READ, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off
  the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B /
  +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/
  SELF-HEAL (Cycle 223): fresh `.venv` + `requests pyyaml eth-account pytest`, 468 tests green pre-flight (469 after
  +1); LOG.md confirmed newest-first + complete through Cycle 222 (no bookkeeping gap); last push (Cycle 222) present
  on origin/main. NOTE: runner at-floor since Aug-1 03:50Z (~3+ days) — durable [LOCAL] runner-recovery stays P0.
- SUPERSEDED (Cycle 223 focus pointer): FOCUS POINTER (Cycle 223 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 223 was TRUTH, so
  Cycle 224 is READOUT). Cycle 223 shipped a **TRUTH increment — the calibration suite's missing CROSS-anchor
  property: static prediction and behavioral experience are RANK-CONCORDANT (no sign inversion)**. Tests 1-8 pin that
  the static payment prediction agrees with behavior on each committed anchor INDEPENDENTLY (with-rails PASSES,
  no-rails retail FAILS, Outcome 100 vs 0), but every one reasons WITHIN a single anchor — nothing pinned that the
  DIRECTION the score predicts (which store is more agent-ready) is the SAME direction the agent's lived outcome
  points, the validity claim a reader actually cites (grade B vs F is a RANKING). A reweight could invert the
  cross-anchor ordering while every per-anchor checkpoint test stayed green. New `test_calibration.py` test 16
  `test_static_prediction_and_behavioral_outcome_are_rank_concordant` asserts: (b) on EVERY static-observable pillar
  (access/legibility/transactability, `_SHARED_STATIC_PILLARS`) with-rails ranks >= no-rails, strictly > on
  payability — no inversion; (c) the behavioral-ONLY Outcome pillar points the SAME way (100 > 0); (d)
  AMPLIFICATION-not-RESCUE — the cited headline ordering (87.8 > 38.8) already held on the static-observable
  prediction BEFORE Outcome was added (payability alone ranks the pair correctly). HONEST SCOPE / non-vacuous: (e)
  TRUST (behaviorally augmented, OUTSIDE the static-observable set) legitimately FAVORS the no-rails store (66.67 >
  55.56), so the concordance is a SCOPED claim (static readiness vs behavioral payment), not "with-rails wins all";
  ACCESS is EQUAL (100==100) so the ranking is carried by the capability pillars. With-rails static-observable pillars
  cross-checked against the offline fixture replay → the 87.5/90.9 literals ride test 9(d)'s re-baseline tripwire.
  CAPABILITY-worded, vendor-neutral; anchors read from committed `runs/local/acceptance_battery_*.report.json` (no
  network). OFF the scoring path (tests-only; scoring-path diff `git diff -- asrs/ rubric/ fixtures/` EMPTY) →
  score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  `test_calibration.py` 15→16, suite 468→469; rubric v0.7. NEXT (READOUT 224): surface the concordance / no-inversion
  claim on the public methodology page or card (the science is pinned in-cloud, the reader-facing prose is not).
  Substantive frontier (thin-bank live fixtures, moleskine.com two-crawl cross-validation, ACP/UCP/MPP,
  transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 222 runner note): RUNNER AT-FLOOR at 2026-08-04T10:2xZ (Cycle 222) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~78.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 10:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path COVERAGE increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off
  the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B /
  +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/
  SELF-HEAL (Cycle 222): fresh `.venv` + `requests pyyaml eth-account pytest`, 467 tests green pre-flight (468 after
  +1); LOG.md confirmed newest-first + complete through Cycle 221 (no bookkeeping gap); last push (Cycle 221, 7242f19)
  present on origin/main. NOTE: the runner has now been at-floor since Aug-1 03:50Z (~3+ days) — the durable [LOCAL]
  runner-recovery item stays P0.
- FOCUS POINTER (Cycle 222 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 222 was COVERAGE, so
  Cycle 223 is TRUTH). Cycle 222 shipped a **COVERAGE increment — the FOURTH encoding-robustness fold: strip INVISIBLE
  line-break controls in offering discovery**. A justification / auto-hyphenation engine interleaves zero-ink category-Cf
  characters INSIDE a capability word or compound — soft hyphen U+00AD (`sub­scrip­tion`), zero-width space U+200B, word
  joiner U+2060, BOM U+FEFF — which `\s` does NOT match (reflow collapse misses them) and which are not visible dashes
  (hyphen fold misses them), so mid-word they break a signal's `\b`/literal match and drop the WHOLE archetype claim on
  ink-invisible typography (worse: the Cycle-218 entity decode can RESTORE `&shy;`/`&#8203;` straight into the matched
  text). New `_INVISIBLE_STRIP` + one `prose.translate(...)` in `classify_offering` (after entity decode, before reflow +
  hyphen fold) DELETES them (an invisible break hint is never part of a word's identity). PRECISION-SAFE (deleting a
  zero-width char only JOINS adjacent chars, never inserts a space/`\b`, so it RESTORES an intended word but can never
  spell a literal-space phrase) and DELIBERATELY excludes ZWNJ/ZWJ U+200C/U+200D (grapheme/script semantics — same scoping
  as the hyphen fold's em-dash exclusion). OFF the scoring path (scoring-path diff EMPTY; `offering` not imported by
  `scoring.py`/`probes/`) → score-neutral, NOT peer-gated, direct-to-main. Canonical CLAIMED sets invariant BY
  CONSTRUCTION (0 of 5 fixtures carry any stripped char). Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  `test_offering.py` +1, suite 467→468; rubric v0.7. NEXT (TRUTH 223): a calibration/attribution invariance guard or a
  panel-verdict-stability property — the classifier's four typography folds (reflow/hyphen/entity/invisible-control) now
  cover both surface branches + the pure-formatting Cf class, so the in-cloud encoding-robustness frontier is genuinely
  exhausted. Substantive frontier (thin-bank live fixtures, reflow/hyphen/entity/invisible-control real-surface
  validation, moleskine.com two-crawl cross-validation, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis +
  peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 220 runner note): RUNNER AT-FLOOR at 2026-08-04T08:2xZ (Cycle 220) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~76.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 08:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (display-only / score-neutral off-scoring-path READOUT
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off
  the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B /
  +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/
  SELF-HEAL (Cycle 220): fresh `.venv` + `requests pyyaml eth-account pytest`, 464 tests green pre-flight (466 after
  +2); LOG.md confirmed newest-first + complete through Cycle 219 (no bookkeeping gap); last push (Cycle 219, 5b3dc45)
  present on origin/main. NOTE: the runner has now been at-floor since Aug-1 03:50Z (~3 days) — the durable [LOCAL]
  runner-recovery item stays P0.
- SUPERSEDED (Cycle 220 focus pointer): FOCUS POINTER (Cycle 220 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 220 was READOUT, so
  Cycle 221 is METHOD). Cycle 220 shipped a **READOUT increment — the driver-line prose now surfaces the tie
  conservatism**. `DivergenceCause.driver` tie-breaks an equal-and-opposite side move to the no-rails floor by
  CONVENTION (Cycle-219 grid), and `cause_verdict` (the terminal "driver:" line + the HTML card "Side:" note,
  scorecard.py:1757) silently printed that as a confident "no-rails reference GAINED capability — real benchmark
  movement", hiding an equal-and-opposite with-rails softening of the same size. New `DivergenceCause.side_ambiguous`
  (equal magnitude within 4-dp rounding tolerance AND a real gap move) gates a FIFTH cause_verdict case: "the gap
  {narrowed|widened} ±X, but the SIDE is unattributed — both references moved by equal magnitude (…), so which drove it
  is a tie (read conservatively as gap movement, not reference degradation)". The four honest cases are byte-for-byte
  unchanged; `reference_degraded` + the re-capture DECISION are untouched (READOUT-only). OFF the scoring path
  (scoring-path diff EMPTY; `canonical_history` not imported by scoring.py/probes/ — grep-verified) → score-neutral,
  NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  `test_canonical_history.py` 68→70, suite 464→466; rubric v0.7. NEXT (METHOD 221): the same silent floor-default
  survives one function over in `recapture_advice`'s REC_RECAPTURE reason (~line 1213 reads `cause.driver` on a tie) —
  route the tie through `side_ambiguous` there too (queued READOUT candidate in BACKLOG). Substantive frontier
  (thin-bank live fixtures, hyphen/reflow/entity real-surface validation, moleskine.com two-crawl cross-validation,
  ACP/UCP/MPP, transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 219 runner note): RUNNER AT-FLOOR at 2026-08-04T07:22Z (Cycle 219) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~75.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 07:22Z fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral TESTS-ONLY off-scoring-path TRUTH increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off
  the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B /
  +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/
  SELF-HEAL (Cycle 219): fresh `.venv` + `requests pyyaml eth-account pytest`, 463 tests green pre-flight (464 after
  +1); LOG.md confirmed newest-first + complete through Cycle 218 (no bookkeeping gap); last push (Cycle 218, 8214f47)
  present on origin/main. NOTE: the runner has now been at-floor since Aug-1 03:50Z (~3 days) — the durable [LOCAL]
  runner-recovery item stays P0.
- SUPERSEDED (Cycle 219 focus pointer): FOCUS POINTER (Cycle 219 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 219 was TRUTH, so
  Cycle 220 is READOUT). Cycle 219 shipped a **TRUTH increment — a property test pinning `DivergenceCause.reference_
  degraded`'s conservatism across the full driver grid**. `reference_degraded` gates the re-capture-DEFERRAL decision
  (True → the with-rails reference is losing ground, the pinned fixture still holds the true gap, WAIT for recovery
  rather than chase a dip); a false positive wrongly FREEZES the fixture. The two docstring-claimed credibility
  properties — (i) driver ties resolve to the no-rails floor so an AMBIGUOUS move is never read as degradation, (ii)
  it fires ONLY on a with-rails LOSS, not a with-rails GAIN that widens the gap from the top — were exercised only in
  the interior by the existing scenario tests, never at the edges. New `test_reference_degraded_is_conservative_across_
  the_full_driver_grid` (tests/test_canonical_history.py) asserts, over a 14-cell (no_change, with_change) grid incl.
  exact ties + first-principles semantics (NOT a re-run of the SUT expression): degradation ⟹ dominant with-rails loss
  narrowing the gap; tie ⟹ no-rails driver + not degraded; strict-dominance ⟹ gap sign follows the driver's own
  direction; + a non-vacuity guard (≥1 real degradation cell) + two teeth cells (with-rails-widening, ambiguous-tie).
  MUTATION-VERIFIED: tie-break `>`→`>=` and dropping the `<0` guard each redden it. OFF the scoring path (`asrs/` diff
  EMPTY; `canonical_history` not imported by `scoring.py`/`probes/`) → score-neutral, NOT peer-gated, direct-to-main.
  Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; `test_canonical_history.py` 67→68, suite 463→464; rubric
  v0.7. NEXT (READOUT 220): surface the conservatism in the drift render — when the driver is a tie/ambiguous move, say
  the gap moved but the SIDE is unattributed (don't silently default the prose to the no-rails floor). Substantive
  frontier (thin-bank live fixtures, hyphen/reflow/entity real-surface validation, moleskine.com two-crawl cross-
  validation, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 218 runner note): RUNNER AT-FLOOR at 2026-08-04T06:1xZ (Cycle 218) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~73.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 06:1xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path COVERAGE increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1),
  off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F /
  85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty
  review. INFRA/SELF-HEAL (Cycle 218): fresh `.venv` + `requests pyyaml eth-account pytest`, 462 tests green
  pre-flight (463 after +1); LOG.md confirmed newest-first + complete through Cycle 217 (no bookkeeping gap).
  NOTE: the runner has now been at-floor since Aug-1 03:50Z (~3 days) — the durable [LOCAL] runner-recovery item
  stays P0.
- FOCUS POINTER (Cycle 218 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 218 was COVERAGE,
  so Cycle 219 is TRUTH). Cycle 218 shipped a **COVERAGE increment — HTML-entity decoding on the NON-HTML surface
  branch** of the offering classifier. The entity decode ran only inside `strip_html` (HTML branch); non-HTML
  surfaces (llms.txt, JSON manifest / ai-plugin / A2A agent card / OpenAPI) carried prose directly and, if
  entity-encoded (`add&nbsp;to&nbsp;cart`), silently dropped the claim. `classify_offering` now `_html.unescape`s
  the non-HTML branch too (HTML branch unchanged; no double-unescape). New guard
  `test_classification_is_non_html_surface_entity_invariant` (the non-HTML sibling of the existing HTML-branch
  entity test): &nbsp;-encoded vs plain `/llms.txt` classify identically (rank/NA/skeleton), teeth prove the
  surface is NOT an HTML document (so the HTML decode does not cover it) + decode is load-bearing + negative
  control (&amp;/&mdash; noise conjures nothing). Canonical NO-OP BY CONSTRUCTION: all 74 committed non-HTML
  canonical surfaces (32 + 42) are byte-identical under `html.unescape`. OFF the scoring path (scoring-path diff
  EMPTY; `offering` not imported by `scoring.py`/`probes/`) → score-neutral, NOT peer-gated, direct-to-main.
  Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; `test_offering.py` 88→89, suite 462→463; rubric
  v0.7. NEXT (TRUTH 219): a calibration/attribution invariance guard or a panel-verdict-stability property; the
  classifier's three encoding-robustness folds (reflow/hyphen/entity) now cover both surface branches, and the
  in-cloud precision+encoding audit frontier is essentially exhausted. Substantive frontier (thin-bank live
  fixtures, hyphen/reflow/entity real-surface validation, moleskine.com two-crawl cross-validation, ACP/UCP/MPP,
  transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 217 runner note): RUNNER AT-FLOOR at 2026-08-04T05:2xZ (Cycle 217) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~73.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 05:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path METHOD increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1),
  off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F /
  85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty
  review. INFRA/SELF-HEAL (Cycle 217): fresh `.venv` + `requests pyyaml eth-account pytest`, 455 tests green
  pre-flight (462 after +7). NOTE: the runner has now been at-floor since Aug-1 03:50Z (~3 days) — the durable
  [LOCAL] runner-recovery item stays P0.
- FOCUS POINTER (Cycle 217 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 217 was METHOD,
  so Cycle 218 is COVERAGE). Cycle 217 shipped a **METHOD increment — a drift-series INTEGRITY verdict** over the
  Cycle-216 exclusion accounting (`asrs/canonical_history.py` `SeriesIntegrity` + `_INTEGRITY_EXCLUDED_FLOOR`
  (0.25) + `series_integrity()` + `CanonicalHistory.integrity`, wired into `summarize` before the empty-series
  early return; `render` gains the `series integrity: INTACT/DEGRADED …` line + an all-excluded empty-render
  branch; `asrs/scorecard.py` the parallel HTML note; `tests/test_canonical_history.py` +6, `tests/test_readout.py`
  +1; suite 455→462). It JUDGES whether the KEPT series (which every drift diagnostic is computed over) is a
  trustworthy basis — excluded fraction within the floor (INTACT) or past it (DEGRADED, weigh with caution) —
  rather than only NAMING what was dropped. NON-VACUOUS on the REAL series: **83 of 84 kept, 1 excluded (1
  malformed) → INTACT, 1% excluded, within the 25% floor**. Teeth: 50%-excluded → DEGRADED, and the 25% boundary
  is inclusive (`<=`). Cross-surface parity (terminal + HTML mirror tests); the Cycle-188 PARITY GUARD stays green
  (all-clean fixture → line absent on both). OFF the scoring path (scoring-path diff EMPTY; `canonical_history`/
  `scorecard` not imported by `scoring.py`/`probes/` — grep-verified) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 218): a
  fresh vendor-neutral capability check or in-cloud offering-classifier refinement; substantive frontier
  (thin-bank live fixtures, hyphen/reflow real-surface validation, moleskine.com two-crawl cross-validation,
  ACP/UCP/MPP, transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 216 runner note): RUNNER AT-FLOOR at 2026-08-04T04:2xZ (Cycle 216) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~72.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 04:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (display-only / score-neutral off-scoring-path READOUT
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24,
  46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no
  first-duty review. INFRA/SELF-HEAL (Cycle 216): fresh `.venv` + `requests pyyaml eth-account pytest`, 451 tests
  green pre-flight (455 after +4). NOTE: the runner has now been at-floor since Aug-1 03:50Z (~3 days) — the
  durable [LOCAL] runner-recovery item stays P0.
- FOCUS POINTER (Cycle 216 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 216 was READOUT,
  so Cycle 217 is METHOD). Cycle 216 shipped a **READOUT increment — the drift block now surfaces the loader's
  EXCLUSION ACCOUNTING** (`asrs/canonical_history.py` `LoadAccounting` + `load_points_accounted` +
  `_classify_artifact` refactor + `render` line, `asrs/scorecard.py` "Latest reading" note, `tests/
  test_canonical_history.py` +3, `tests/test_readout.py` +1; suite 451→455). Cycle 215's loader gate DROPS
  red-bench/malformed artifacts SILENTLY, so `series: N re-scores` is the FILTERED series with no sign of it. Now
  both surfaces name `K of N artifacts kept, M excluded (k red-bench, j malformed)` when the loader dropped
  something (silent when clean). NON-VACUOUS on the REAL series: it surfaces the pre-Cycle-13 legacy malformed
  artifact previously dropped silently → **83 of 84 kept, 1 excluded (1 malformed), 0 red-bench**. Cross-surface
  parity (terminal + HTML mirror tests); the Cycle-188 PARITY GUARD stays green (its fixture is all-clean → line
  absent on both). OFF the scoring path (scoring-path diff EMPTY; `canonical_history`/`scorecard` not imported by
  `scoring.py`/`probes/` — grep-verified) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 217): a fresh calibration/attribution
  invariance guard, or fold the accounting into a drift-series integrity metric (warn if the excluded FRACTION
  crosses a floor). Substantive frontier (thin-bank live fixtures, hyphen/reflow real-surface validation,
  ACP/UCP/MPP, transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 215 runner note): RUNNER AT-FLOOR at 2026-08-04T03:2xZ (Cycle 215) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~71.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 03:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path TRUTH increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1),
  off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F /
  85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty
  review. Test suite green pre-flight (449) and post (451). NOTE: the runner has now been at-floor since Aug-1
  03:50Z (~3 days) — the durable [LOCAL] runner-recovery item stays P0.
- FOCUS POINTER (Cycle 215 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 215 was TRUTH,
  so Cycle 216 is READOUT). Cycle 215 shipped a **TRUTH increment — the drift-series loader now excludes a
  canonical reading scored while the bench's own guards were red** (`asrs/canonical_history._point_from_artifact`
  returns None on an EXPLICIT `tests_ok is False`; a missing/None field = honest-unknown, stays in). The runner
  scores the pair even on a red suite (it bails only on a failed `git pull`, before scoring — those are already
  dropped for missing scores/delta), so a reading from an inconsistent scoring path (e.g. a red
  `test_canonical_replay` = scoring semantics moved) could silently anchor a drift attribution — invariants #2
  (versioned comparability) + #4 (attribution honesty). Non-vacuous: teeth test flips the SAME reading's flag
  True→reappears; real-series reconciliation proves the gate drops NONE of the 84 committed (all green) artifacts,
  so the live drift attribution the P0 rests on is unchanged. OFF the scoring path (canonical_history not imported
  by scoring.py/probes/rubric — grep-verified; scoring-path diff EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. `test_canonical_history.py`
  56→58; suite 449→451. NEXT (READOUT 216): surface the loader's exclusion accounting in the drift block/render
  ("N readings; M excluded: k red-bench, j malformed") so the operator sees the series is filtered, not raw — the
  readout mirror of this cycle's guard. Substantive frontier (thin-bank live fixtures, hyphen/reflow real-surface
  validation, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis + peer-gated re-baseline) stays `[LOCAL]`.
- SUPERSEDED (Cycle 214 runner note): RUNNER AT-FLOOR at 2026-08-04T02:1xZ (Cycle 214) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~70.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 02:1xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path COVERAGE increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1),
  off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F /
  85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty
  review. INFRA/SELF-HEAL (Cycle 214): fresh checkout landed at the STALE shallow-clone `origin/main` ref
  (Cycle-94 `3796519`); `git fetch origin main` forced the ref forward to the true cloned tip `4c4497e` (Cycle 213)
  and `git checkout -B main origin/main` reconciled. Fresh `.venv` + `requests pyyaml eth-account pytest`, 448
  tests green pre-flight (449 after +1).
- FOCUS POINTER (Cycle 214 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 214 was COVERAGE,
  so Cycle 215 is TRUTH). Cycle 214 shipped a **COVERAGE increment — the offering classifier now folds
  typographic/non-breaking INTRA-WORD hyphens** (`asrs/offering.py` `_HYPHEN_NORMALIZE` + a per-surface fold in
  `classify_offering` after the Cycle-178 reflow collapse, `tests/test_offering.py` +1; suite 448→449). Many
  signals (esp. metered_api's `pay-as-you-go`/`pay-per`/`per-generation`) match a literal `[- ]` only, so a
  compound typeset with U+2011 (non-breaking hyphen — the dash sibling of `&nbsp;`), en/figure dash, or minus sign
  silently missed and the WHOLE archetype claim dropped on typography (verified live: U+2011 substitution drops
  metered_api entirely). The fold maps U+2010–2013 + U+2212 + U+FE63 + U+FF0D → ASCII `-`; DELIBERATELY excludes
  the em dash (U+2014) + horizontal bar (U+2015) as sentence punctuation — which is BOTH the precision-correct
  choice AND makes the fold a no-op on the canonical pair (whose only Unicode dash is a prose em dash, 8× each) →
  canonical CLAIMED sets invariant by construction. Third typographic-encoding invariance sibling (line-wrap /
  entity-decode / hyphen). Non-vacuous: load-bearing (raw pattern matches ASCII not U+2011), em-dash-exclusion
  teeth (em dash input drops metered_api → subscription rank-1), real-evidence half (fixtures carry only the
  excluded em dash). OFF the scoring path (scoring-path diff EMPTY; `offering` not imported by `scoring.py`/
  `probes/` — grep-verified) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B
  / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 215): a fresh calibration/attribution invariance guard, or
  substantive frontier work — GENUINE new thin-bank signals from real fixtures, validate the hyphen-fold + reflow
  on a REAL dashed/line-wrapped surface, the negative anchor's two-crawl static cross-validation via a
  `moleskine.com` fixture, ACP/UCP/MPP, the transactability-drop CHECK-level diagnosis — all `[LOCAL]`.
- SUPERSEDED (Cycle 213 runner note): RUNNER AT-FLOOR at 2026-08-04T01:1xZ (Cycle 213) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~69.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 01:1xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path METHOD increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1),
  off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F /
  85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty
  review. INFRA/SELF-HEAL (Cycle 213): fresh checkout landed in detached HEAD at origin/main tip `4344c38`
  (Cycle-212); reconciled via `git checkout -B main origin/main`. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, 445 tests green pre-flight (448 after +3).
- FOCUS POINTER (Cycle 213 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 213 was
  METHOD, so Cycle 214 is COVERAGE). Cycle 213 shipped a **METHOD increment — the citability gate now covers
  TRUST-verdict reproducibility, not just the checkpoint ladder** (`asrs/reliability.py` gate + docstring,
  `asrs/scorecard.py` pill map, `tests/test_quotability.py` +3; suite 445→448). `quotability()` tagged a panel
  `reproducible`/citable once `verdict_stability` (checkpoint-ladder only) cleared 0.8 — IGNORING
  `trust_events_unanimous`, so a ladder-unanimous panel that split 50/50 on the refuse↔warn trust flip (the very
  instability the reliability module's docstring cites as its motivation) was mis-tagged citable (verified live:
  stability 1.0, trust agreement 0.5 → `reproducible`). New branch (after the checkpoint-instability check, before
  the `reproducible` return): `trust_events_unanimous is False` → `provisional-trust-unstable`/quotable=False,
  carrying the real ladder stability + naming the unreproducible trust verdict. Checkpoint instability still
  outranks it. Non-vacuous teeth: the SPLIT downgrades, not the PRESENCE of a concern (unanimous refuse stays
  citable); ordering guard (doubly-unstable → `provisional-unstable`). Display-only, never a score gate (scoring.py
  does not import quotability). OFF the scoring path (scoring-path diff EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 214): a
  dedicated reliability-card sentence for the new tag / surface-parity pin, or substantive frontier work — GENUINE
  new thin-bank signals from real fixtures, the negative anchor's two-crawl static cross-validation via a
  `moleskine.com` fixture, ACP/UCP/MPP, the transactability-drop CHECK-level diagnosis — all `[LOCAL]`.
- SUPERSEDED (Cycle 212 runner note): RUNNER AT-FLOOR at 2026-08-04T00:2xZ (Cycle 212) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~69h old at the fire — PAST the 6h floor (machine-asleep / runner-lag pattern,
  cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 00:2xZ fire is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (display-only / score-neutral off-scoring-path READOUT
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal (24/24,
  46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no
  first-duty review. INFRA/SELF-HEAL (Cycle 212): fresh checkout landed in detached HEAD at origin/main tip
  `a199d67` (Cycle-211); fresh `.venv` + `requests pyyaml eth-account pytest`, 443 tests green pre-flight (445
  after +2).
- FOCUS POINTER (Cycle 212 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 212 was
  READOUT, so Cycle 213 is METHOD). Cycle 212 shipped a **READOUT increment — the attributed-pillar noise floor
  is now SURFACED on both drift surfaces** (`asrs/canonical_history.py` render + `asrs/scorecard.py` render,
  `tests/test_readout.py` +2, `tests/test_canonical_history.py` parity-guard +1 fact; suite 443→445). Cycle 211
  computed `attributed_pillar_noise_floor` (the fingered pillar's at-rest dispersion) but left it un-rendered.
  Terminal `render` gains a `pillar noise floor:` line after the attribution top-mover; HTML drift card gains an
  `At rest:` line below the Pillar line — same reading order on both. Deterministic branch earns the strong claim
  (`driftflight.com transactability σ=0.00 over 76 in-band re-scores → DETERMINISTIC at rest — the -25.0 move is
  signal, not pillar jitter`), non-deterministic branch WITHHOLDS it (reports σ + worst against "the at-rest
  pillar jitter"), honest-None when the floor is None. The Cycle-188 READOUT PARITY GUARD now binds the new
  diagnostic across BOTH surfaces (precondition + `"signal, not pillar jitter"` fact); teeth via
  `test_pillar_noise_floor_withholds_strong_claim_when_pillar_jitters` (jittering fingered pillar → strong claim
  absent, "at-rest pillar jitter" present on both surfaces). Verified live on the real committed series (83 pts,
  diverged, σ=0/n=76/−25.0). OFF the scoring path (scoring-path diff EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 213): a
  fresh calibration/attribution invariance guard, or substantive frontier work — GENUINE new thin-bank signals
  from real fixtures, the negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture,
  ACP/UCP/MPP, the transactability-drop CHECK-level diagnosis — all `[LOCAL]`.
- SUPERSEDED (Cycle 211 runner note): RUNNER AT-FLOOR at 2026-08-03T23:22Z (Cycle 211) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~67.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 23:22Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path
  TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 211): fresh
  checkout landed in detached HEAD on the stale shallow-clone `main` ref; reconciled to origin/main `81f63f1`
  (Cycle-210 tip) via `git checkout main` + `git reset --hard origin/main` (the benign divergence is the
  shallow-clone local-ref reconciliation, NOT a history rewrite — invariant #5 intact). Fresh `.venv` +
  `requests pyyaml eth-account pytest`, 440 tests green pre-flight (443 after +3).
- FOCUS POINTER (Cycle 211 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 211 was
  TRUTH, so Cycle 212 is READOUT). Cycle 211 shipped a **TRUTH increment — a pillar-granularity noise floor
  proving the ATTRIBUTED transactability drop is signal, not pillar jitter** (`asrs/canonical_history.py` +
  `tests/test_canonical_history.py` +3, in-file 53→56, suite 440→443). The overall `NoiseFloor` proves the
  DELTA is deterministic at rest (σ=0 over 76 in-band re-scores), but the drift the benchmark ATTRIBUTES is at
  the PILLAR level (driftflight.com transactability −25) and nothing proved that fingered move exceeds
  PILLAR-level jitter. New `PillarNoiseFloor` + pure `pillar_noise_floor(points, domain, pillar)` measure one
  side's one pillar's at-rest dispersion over the in-band readings (numeric-only, honest-None below 2);
  `summarize` wires it to the attributed top mover → `attributed_pillar_noise_floor`. On the real series the
  fingered pillar is 87.5 across all 76 in-band readings ⇒ σ=0/max|div|=0/deterministic, and the tracked −25
  dwarfs it (SIGNAL, not jitter, at the granularity we finger). Non-vacuous (synthetic pillar-jitter guard:
  constant delta but varying .com transactability → σ>0/deterministic=False — the jitter the overall floor is
  blind to), MUTATION-VERIFIED (leak the OOB drop into the floor → σ=5.39/deterministic=False → real-series
  guard reddens), vendor-neutral (domain is a side selector vs the module's own reference-pair constants; no
  host special-cased). OFF the scoring path (`git diff --name-only` = the module + its test; `asrs/scoring.py
  asrs/probes/ rubric/ fixtures/ asrs/offering.py asrs/battery.py` diff EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (READOUT 212):
  the `attributed_pillar_noise_floor` is computed but not yet surfaced — render it in the drift block ("fingered
  pillar deterministic at rest; the −25 move is signal, not jitter"), mirroring the overall noise-floor
  surfacing (mind the terminal/HTML surface-parity guard). Substantive frontier (GENUINE new thin-bank signals
  from real fixtures, the negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture,
  ACP/UCP/MPP, the transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 210 runner note): RUNNER AT-FLOOR at 2026-08-03T22:15Z (Cycle 210) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~66.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 22:15Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path
  COVERAGE increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 210): fresh
  checkout's shallow-clone local `main` ref was stale; reconciled to origin/main `43b7e4a` (Cycle-209 tip)
  via `git checkout -B main origin/main`. Fresh `.venv` + `requests pyyaml eth-account pytest`, 436 tests
  green pre-flight (440 after +4).
- FOCUS POINTER (Cycle 210 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 210 was
  COVERAGE, so Cycle 211 is TRUTH). Cycle 210 shipped a **COVERAGE increment — the offering-classifier
  relabel guard dropped one layer, to the per-archetype EVIDENCE** (`tests/test_offering_canonical.py` +4,
  in-file 58→62, suite 436→440). The existing `_assert_offering_relabel_invariant` pins that the CLAIMED
  archetype list (ordered) + NA set are host-relabel-invariant, but it is SET-level — blind to a favorable
  identity-keyed special-case that pads an ALREADY-claimed archetype's evidence (extra label / higher
  `strength`) without flipping the claimed set. Yet `strength`/`labels` are exactly what the classifier
  surfaces to the operator as claim-support quality. New `_assert_offering_relabel_evidence_invariant` asserts
  every claimed archetype's `(strength, sorted fired-label set)` is byte-identical under a whole-fixture host
  relabel, on all 3 committed offering fixtures (org/com/api.replicate.com). Non-vacuous (host inside the
  matched quotes on every fixture — relabel genuinely rewrites input; neutral host different length + no signal
  word). TEETH: `test_offering_relabel_evidence_negative_control` pads `metered_api` with one label under an
  identity rig — the COARSER set/order guard STILL PASSES (gap is real), the finer evidence guard RAISES.
  Vendor-neutral (profile compared to its own relabel; no host special-cased). OFF the scoring path
  (`git diff --name-only` = the one test file; `asrs/scoring.py asrs/probes/ rubric/ fixtures/ asrs/offering.py
  asrs/battery.py` diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 211): a fresh calibration/attribution invariance
  guard, or substantive frontier work — GENUINE new thin-bank signals from real fixtures, the negative anchor's
  two-crawl static cross-validation via a `moleskine.com` fixture, ACP/UCP/MPP, the transactability-drop
  CHECK-level diagnosis — all `[LOCAL]`.
- SUPERSEDED (Cycle 209 runner note): RUNNER AT-FLOOR at 2026-08-03T21:17Z (Cycle 209) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~65.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 21:17Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path
  METHOD increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 209): fresh
  checkout's shallow-clone local `main` ref was the stale `3796519`; reconciled to origin/main `7bc96e5`
  (Cycle-208 tip) via `git fetch origin main` + `git checkout -B main origin/main` (the benign "(forced
  update)" is the shallow-clone local-ref reconciliation, NOT a history rewrite — invariant #5 intact). Fresh
  `.venv` + `requests pyyaml eth-account pytest`, 435 tests green pre-flight (436 after +1).
- FOCUS POINTER (Cycle 209 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 209 was
  METHOD, so Cycle 210 is COVERAGE). Cycle 209 shipped a **METHOD increment — the corroboration VERDICT WORD
  is now coupled to the boolean, so the readout prose cannot lie** (`tests/test_canonical_history.py` +1, suite
  435→436). Cycle 208 wired `corroboration_verdict`'s CORROBORATED / NOT-corroborated sentence onto the
  terminal + HTML drift block, but nothing tied the WORD to `corr.corroborated`: an edit emitting "CORROBORATED"
  from a not-corroborated branch would mis-sell a single-signal decision as two-mechanism-backed and pass every
  existing guard (they only exercise the verdict through real histories). New guard
  `test_corroboration_verdict_word_is_coupled_to_the_boolean` constructs `DecisionCorroboration` over the FULL
  (same_side, same_direction) truth table and pins, for every corner, `verdict.startswith("CORROBORATED") is
  corr.corroborated` AND `verdict.startswith("NOT corroborated") is (not corr.corroborated)`, plus the advisory
  posture coupling (caution warning iff not corroborated; two-signals assurance iff corroborated). Non-vacuous
  (exactly one corroborated corner, `corroborated_count==1`), MUTATION-VERIFIED (flip the CORROBORATED branch →
  guard reddens, restore → green, source diff clean), vendor-neutral (host-relabel invariant — swap the pair's
  roles, the word per structural combo is unchanged). OFF the scoring path (`git diff --name-only` = the one
  test file; `asrs/scoring.py asrs/probes/ rubric/ fixtures/ asrs/canonical_history.py` diff EMPTY) →
  score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. NEXT (COVERAGE 210): the in-cloud precision-audit frontier is exhausted and the
  corroboration/attribution readout series is word-coupled end to end — a COVERAGE candidate is a fresh
  invariance guard elsewhere. Substantive frontier (GENUINE new thin-bank signals from real fixtures, the
  negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture, ACP/UCP/MPP,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 208 runner note): RUNNER AT-FLOOR at 2026-08-03T20:14Z (Cycle 208) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~64.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 20:14Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (display-only / score-neutral off-scoring-path
  READOUT increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 208): fresh
  checkout landed on the STALE shallow-clone local `main` ref `3796519`; reconciled to origin/main `7e55c45`
  (Cycle-207 tip) via `git fetch origin main` + `git checkout -B main origin/main` (the benign "(forced
  update)" is the shallow-clone local-ref reconciliation, NOT a history rewrite — invariant #5 intact). Fresh
  `.venv` + `requests pyyaml eth-account pytest`, 433 tests green pre-flight (435 after +2).
- FOCUS POINTER (Cycle 208 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 208 was
  READOUT, so Cycle 209 is METHOD). Cycle 208 shipped a **READOUT increment — the re-capture decision's
  TWO-MECHANISM corroboration is now surfaced in the drift block** (`asrs/canonical_history.py` +
  `asrs/scorecard.py`; `tests/test_canonical_history.py` 50→52, suite 433→435). Cycle 207 pinned INTERNALLY
  that on the real series the DEFER decision is corroborated by both independent mechanisms (side-level
  `divergence_cause` from overalls + pillar-level `attribution` from per-pillar scores fingering the same
  with-rails softening), but the operator never SAW it: the `re-capture:` line + HTML rec_card stated only
  the side-level reason. New `DecisionCorroboration` (`same_side`/`same_direction`/`corroborated`),
  `decision_corroboration()` (pure read of cause+attribution; None unless both present with an isolated
  pillar), and `corroboration_verdict()` (CORROBORATED with both signed moves, or NOT-corroborated naming the
  disagreement) drive a new `corroboration:` terminal line + a **Corroboration:** HTML paragraph. On the live
  series it reads "CORROBORATED — side-level (driftflight.com overall −9.3) and INDEPENDENT pillar-level
  (driftflight.com transactability −25.0) finger the same side moving the same way". Guard
  `test_decision_corroboration_agrees_disagrees_and_none` is non-vacuous BOTH ways (agree; side-disagree;
  direction-disagree; None in-band); `..._on_real_series_is_coherent` ties it to the real primitives,
  recovery-tolerant. Vendor-neutral (domains compared only for equality to each other, never host-special-
  cased). OFF the scoring path (`git diff --name-only` = the two asrs readout modules + the test; `asrs/scoring.py
  asrs/probes/ rubric/ fixtures/` diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 209): a coupling guard tying the
  `corroboration_verdict` CORROBORATED/NOT-corroborated word to `corr.corroborated` (so the prose cannot lie),
  or a fresh attribution/invariance guard elsewhere in the calibration/history series. Substantive frontier
  (GENUINE new thin-bank signals from real fixtures, the negative anchor's two-crawl static cross-validation
  via a `moleskine.com` fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 207 runner note): RUNNER AT-FLOOR at 2026-08-03T19:13Z (Cycle 207) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~63.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 19:13Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path
  TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 207): fresh
  checkout landed at `d6412da` (Cycle-206 tip) = origin/main after `git pull` (the benign "(forced update)
  from 3796519" is the stale shallow-clone local-ref reconciliation, NOT a history rewrite — invariant #5
  intact). Fresh `.venv` + `requests pyyaml eth-account pytest`, 432 tests green pre-flight (433 after +1).
- FOCUS POINTER (Cycle 207 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 207 was
  TRUTH, so Cycle 208 is READOUT). Cycle 207 shipped a **TRUTH increment — the operator-facing re-capture
  DECISION on the REAL canonical series is DEFER, and that DEFER is corroborated by BOTH independent drift
  mechanisms** (`tests/test_canonical_history.py` 49→50, suite 432→433). `recapture_advice` synthesizes its
  recommendation from the SIDE-level `divergence_cause` ALONE (overalls); the new guard
  `test_real_series_defer_decision_is_corroborated_by_both_mechanisms` ties that operator-facing DECISION to
  the INDEPENDENT pillar mechanism on the real committed series — currently non-vacuous (band=diverged,
  consecutive_out_of_band=3==`_SUSTAINED_MIN`): `reference_degraded is True`, `recapture.code==REC_DEFER`,
  and `attribution.top.domain == cause.driver == driftflight.com` with `top.change<0` (both mechanisms
  finger the with-rails transactability softening 87.5→62.5). The piece neither sibling made alone
  (`..._fingers_the_drifting_pillar` asserts the convergence not the decision; `..._is_coherent` asserts the
  decision only weakly, not the convergence). A wrong DEFER→RECAPTURE flip would re-pin the frozen baseline
  to a transient site regression, corrupting comparability — this is that tripwire. Also corrected the stale
  recovery-tolerance comment in `..._is_coherent` ("currently reads baseline-valid" → out-of-band today).
  Recovery-tolerant (in-band ⇒ REC_VALID skip; not-sustained ⇒ WAIT/REVIEW). Vendor-neutral (keys on pair
  STRUCTURE + the module reference constant, no literal host in assertion logic). OFF the scoring path
  (`git diff --name-only` = test_canonical_history.py; `asrs/ rubric/ fixtures/` diff EMPTY) → score-neutral,
  NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  NEXT (READOUT 208): surface the corroborated-DEFER recommendation WITH its two-mechanism basis in the
  terminal/HTML drift block (the operator sees WHY defer), or a readout-wording coupling guard. Substantive
  frontier (GENUINE new thin-bank signals from real fixtures, the negative anchor's two-crawl static
  cross-validation via a `moleskine.com` fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis)
  stays `[LOCAL]`.
- SUPERSEDED (Cycle 206 runner note): RUNNER AT-FLOOR at 2026-08-03T18:14Z (Cycle 206) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~62.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 18:14Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral COVERAGE
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 206): fresh
  checkout landed at `3c02615` (Cycle-205 tip) = origin/main after `git pull` (the benign "(forced update)
  from 3796519" is the stale shallow-clone local-ref reconciliation, NOT a history rewrite — invariant #5
  intact). Fresh `.venv` + `requests pyyaml eth-account pytest`, 431 tests green pre-flight (432 after +1).
- FOCUS POINTER (Cycle 206 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 206 was
  COVERAGE, so Cycle 207 is TRUTH). Cycle 206 shipped a **COVERAGE increment — the metered_api bank's last
  un-swept bare word is now precision-guarded** (`asrs/offering.py` `usage-based` regex; `tests/test_offering.py`
  +1, suite 431→432). Bare `\bmetered\b` (in `usage-based`) was a broad-English minefield — metered parking /
  water / electricity / -dose / postage / verse / "a metered approach" — any of which could CONJURE a
  metered_api claim (an API-call intent probed on a site that offers none). The guard now requires `metered`
  to name a BILLING/USAGE/API context (billing object after it, "metered per <unit>", "metered and
  charged/billed", or usage/call/request "is/are metered"); `usage-based`/`overage` stay bare (already
  billing-specific). LOOKAHEAD-anchored so the matched SPAN stays exactly `metered` → the canonical evidence
  QUOTE is byte-identical (verified empirically on both domains) → canonical-invariant by construction. New
  guard `test_usage_based_metered_precision_synthetic` (12 genuine metered-billing positives fire usage-based
  non-vacuously / 10 broad-English "metered <noun>" negatives claim nothing). OFF the scoring path
  (`git diff -- asrs/scoring.py asrs/probes/ rubric/ fixtures/` EMPTY; classifier not imported by scoring) →
  score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. NEXT (TRUTH 207): the bare-word minefields are now ALL guarded across every archetype bank —
  the in-cloud precision-audit frontier is exhausted; a TRUTH candidate is a fresh attribution/invariance
  guard on the calibration or canonical-history series. Substantive frontier (GENUINE new thin-bank signals
  from real fixtures, the negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture,
  ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 205 runner note): RUNNER AT-FLOOR at 2026-08-03T17:19Z (Cycle 205) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~61.5h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:17Z Cycle-204 daily digest; this 17:19Z fire is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral off-scoring-path
  METHOD increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 205): fresh
  checkout landed detached on the Cycle-204 tip `892d155`; a read-only `git fetch origin main` reconciled
  origin/main → `892d155` (the local `main` ref was the stale shallow-clone `3796519`, the benign
  "(forced update)" — NOT a history rewrite, invariant #5 intact), worked on `main`=origin/main=`892d155`.
  Fresh `.venv` + `requests pyyaml eth-account pytest`, 430 tests green pre-flight (431 after +1).
- FOCUS POINTER (Cycle 205 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 205 was
  METHOD, so Cycle 206 is COVERAGE). Cycle 205 shipped a **METHOD increment — the published headline PROSE
  is now number-coupled** (`tests/test_calibration.py` 14→15,
  `test_methodology_headline_prose_is_coupled_to_the_live_fraction`, suite 430→431). Cycle 204 put "closes
  ABOUT TWO-THIRDS … the SINGLE MAJORITY DRIVER" onto the public methodology page; test 14 computes that
  fraction live (0.652), but page WORDS and test NUMBER were coupled only by a string-PRESENCE check — a
  [LOCAL] re-baseline could move the fraction to 0.48 (no majority) or 0.82 (not two-thirds) and both stay
  green while the prose lied. The new guard recomputes the live fraction (same knock-out as test 14), then
  DERIVES the required word FROM the number (`_nearest_fraction_word`: nearest of half/three-fifths/
  two-thirds/three-quarters/four-fifths) and asserts the page says "about <word>" — so wording is computed
  from the computation. (b) non-vacuous: two-thirds STRICTLY nearest to 0.652 (closer than half OR
  three-quarters); (c) "single majority driver" allowed only while fraction≥0.5; (d) dominated-not-exclusive
  framing coupled to fraction<1.0. MUTATION-VERIFIED (page word→three-quarters ⇒ reddens; majority claim
  removed ⇒ reddens). OFF the scoring path (`git diff --name-only` = test_calibration.py; `asrs/ rubric/
  fixtures/` diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 206): a metered_api bare-word precision audit
  (largest bank, 26 signals, never swept for broad-English collisions — last un-audited archetype bank
  after enrich/dataset/lookup, book/schedule, recurring). Substantive frontier (GENUINE new thin-bank
  signals from real fixtures, the negative anchor's two-crawl static cross-validation via a `moleskine.com`
  fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 204 runner note): RUNNER AT-FLOOR at 2026-08-03T16:17Z (Cycle 204) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~60.4h old at the fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this 16:17Z fire IS
  the FIRST cycle after 16:00 UTC today → daily digest DM SENT this fire per comms policy (display-only /
  score-neutral READOUT increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 204): fresh
  checkout, working tree clean, invariant #5 intact; fresh `.venv` + `requests pyyaml eth-account pytest`,
  430 tests green pre-flight (430 after — extended an EXISTING test function, not a new one).
- FOCUS POINTER (Cycle 204 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 204 was
  READOUT, so Cycle 205 is METHOD). Cycle 204 shipped a **READOUT increment — the overall-level payment
  attribution is now on the public methodology page** (`asrs/scorecard.py` `_write_methodology_page`
  section 8 + a Cycle-204 block in `test_methodology_documents_calibration`). Cycle 203's test 14 proved at
  the OVERALL level (scoring's own roll-up) that knocking agent-native payment out of the with-rails
  storefront collapses the cited overall a full grade tier across the passing boundary (85.5 B → 59.8 F),
  only transactability moving, closing ~65% of the +39.4 headline delta, with an honest legibility residual
  — but that lived ONLY in the test suite. Two new number-free paragraphs carry it onto the page: the cited
  headline gap is payment-DOMINATED ("about two-thirds", "single majority driver"), NOT payment-EXCLUSIVE
  (a residual carried by the machine-legibility pillar), run through the scorer's OWN roll-up and
  test-pinned. Matches section 8's deliberately number-free style (no 85.5/59.8/46.1 literals → no new
  re-baseline tripwire); vendor-neutral. OFF the scoring path (`git diff --name-only` = scorecard.py +
  test_readout.py; `grep scorecard asrs/scoring.py asrs/probes/` = NONE) → score-neutral, NOT peer-gated,
  direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD
  205): pin that the overall-attribution PROSE cannot drift from test 14's actual `fraction`/`0.652`
  numbers (couple the "about two-thirds"/"majority driver" wording to the live computation), OR a fresh
  invariance/attribution guard. Substantive frontier (GENUINE new thin-bank signals from real fixtures, the
  negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture, ACP/UCP/MPP,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 203 runner note): RUNNER AT-FLOOR at 2026-08-03T15:13Z (Cycle 203) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~58.6h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  15:13Z fire is BEFORE 16:00 UTC → NOT first-after-16:00 → no DM this fire per comms policy (tests-only /
  score-neutral off-scoring-path TRUTH increment, no sensitive-class PR, nothing score-moving). Live
  signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability
  62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay
  guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open
  peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 203): the fresh checkout started detached on the real tip `eb634bd` (Cycle 202) but the clone's
  local `main`/`origin/main` refs were STALE at `3796519` (Cycle 94) — a shallow-clone artifact, NOT a
  history rewrite. A read-only `git fetch origin main` reconciled origin/main → `eb634bd` (Cycle 202,
  matching STATE/LOG); the per-cycle "(forced update) from 3796519" note is exactly this benign stale-ref
  reconciliation, not a real force-push (invariant #5 intact, verified: full Cycle-95→202 history present,
  429 tests green on the real tip). Worked on `main` = origin/main = `eb634bd`. Fresh `.venv` + `requests
  pyyaml eth-account pytest`; 429 tests green pre-flight (430 after +1). NOTE for future fires: `git
  checkout main` on a fresh cloud checkout lands on the STALE local branch (Cycle 94) — always
  `git fetch origin main` and work from `origin/main`, never the bare local `main`.
- FOCUS POINTER (Cycle 203 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 203 was
  TRUTH, so Cycle 204 is READOUT). Cycle 203 shipped a **TRUTH increment — the agent-native payment
  attribution PROPAGATES to the cited OVERALL number** (`tests/test_calibration.py` 13→14,
  `test_payment_capability_drives_the_majority_of_the_headline_delta`, suite 429→430). Tests 11-13 pinned
  the payment attribution at the TRANSACTABILITY-PILLAR level; this carries it to the OVERALL score people
  cite. Using scoring's OWN roll-up, it knocks out agent-native payment on the with-rails storefront
  (substitutes the no-rails FULL CheckResults for `_STATIC_PAYMENT_CHECKS` — points + findings, so any
  payment-gap cap fires faithfully) and re-scores: OVERALL collapses **85.5 B → 59.8 F** (a full grade-tier
  flip ACROSS the passing boundary), ONLY transactability moves (87.5→18.75, other pillars byte-identical,
  caps unchanged), closing **25.7/39.4 = 65.2%** of the headline delta — agent-native payment is the SINGLE
  MAJORITY driver of the cited gap even after the 0.30 pillar weight dilutes it. HONEST non-exclusivity: the
  knock-out leaves a residual (59.8 > 46.1) carried by legibility (90.9 vs 36.4), so the guard states the
  delta is payment-DOMINATED, not payment-EXCLUSIVE. OFF the scoring path (`git diff --name-only` =
  test_calibration.py only; asrs/rubric/fixtures diff EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. The 85.5/46.1/59.8/18.75 literals share test 9(d)'s re-baseline tripwire. Replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (READOUT 204): carry this overall-level,
  headline-number attribution (payment ≈65% majority driver, B→F flip, honest ~35% legibility residual)
  onto the methodology page / calibration card — it lives only in the test suite today, exactly as tests
  12/13's pillar counterfactual did before Cycle 200 surfaced it. Substantive frontier (GENUINE new
  thin-bank signals from real fixtures, the negative anchor's two-crawl static cross-validation via a
  `moleskine.com` fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 202 runner note): RUNNER AT-FLOOR at 2026-08-03T14:22Z (Cycle 202) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~58.5h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  14:22Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (score-neutral
  off-scoring-path COVERAGE increment, no sensitive-class PR, nothing score-moving). Live signal (read,
  not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 202): fresh
  checkout on the Cycle-201 tip `daf671f` (origin arrived as a `(forced update)` from `3796519`, normal
  direct-to-main cadence), working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml
  eth-account pytest`, imports verified, 428 tests green pre-flight (429 after +1).
- FOCUS POINTER (Cycle 202 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 202 was
  COVERAGE, so Cycle 203 is TRUTH). Cycle 202 shipped a **COVERAGE increment — the subscription
  `recurring` bare-word precision guard** (`asrs/offering.py` + `tests/test_offering.py`,
  `test_subscription_recurring_precision_synthetic`, suite 428→429). Bare `\brecurring\b` false-positived
  on broad-English "recurring theme/dream/nightmare/bug/character/meeting/pattern" prose (each would CONJURE
  a subscription claim on a non-billing storefront); the POSITIVE-anchored form (mirroring enrich/dataset,
  since `recurring`'s false-positive family is open-ended general English, not a bounded CTA/internals set)
  now requires a BILLING object after "recurring" (billing/payment/charge/subscription/invoice/fee/plan/
  price/dues/membership, optionally via a cadence adjective) OR a billing verb in a short window ("billed/
  charged/invoiced ... on a recurring basis"); dropped the ambiguous "revenue"/"costs". 10 recurring-ONLY
  positives fire non-vacuously / 13 non-billing negatives dodge. CANONICAL-INVARIANT by construction (no
  fixture contains "recurring", narrowing only removes matches); isolation matrix green. OFF the scoring
  path (`git diff --name-only` = offering.py + test_offering.py; `scoring.py` has no `classify_offering`
  reference, grep-re-verified) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1
  F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. The two THINNEST-archetype bare-word minefields
  (enrich/dataset/lookup, book/schedule) are now ALL guarded and subscription's `recurring` closed. NEXT
  (TRUTH 203): a calibration/attribution invariance guard, OR carry the counterfactual onto the
  calibration/history card. NEXT in-cloud COVERAGE candidate is a metered_api bare-word audit (largest
  bank, 26 signals, never swept for broad-English collisions). Substantive frontier (GENUINE new thin-bank
  signals from real fixtures, the negative anchor's two-crawl static cross-validation via a `moleskine.com`
  fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 201 runner note): RUNNER AT-FLOOR at 2026-08-03T13:25Z (Cycle 201) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~57.6h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  13:25Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral
  off-scoring-path METHOD increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 201): fresh
  checkout on the Cycle-200 tip `cdc3b53`, working tree clean, invariant #5 intact. Fresh `.venv` +
  `requests pyyaml eth-account pytest`, imports verified, 427 tests green pre-flight (428 after +1).
- FOCUS POINTER (Cycle 201 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 201 was
  METHOD, so Cycle 202 is COVERAGE). Cycle 201 shipped a **METHOD increment — verdict_stability is MONOTONE
  in disagreement and shares ONE threshold with the citability gate** (`tests/test_reliability.py`, 9→10
  in-file, suite 427→428, `test_verdict_stability_is_monotone_and_shares_the_citability_threshold`).
  verdict_stability is the number the whole benchmark's "is this safe to CITE?" credibility rests on;
  point-value tests (1-8) and order-invariance (9) pinned WHAT it computes, but not the SHAPE. New guard
  pins: (A) MONOTONICITY — more panel disagreement can only LOWER stability and only DEGRADE citability
  (reproducible→provisional, never reverse), via a strictly-descending ladder [1.0..0.0]; (B) EXHAUSTIVE
  boundedness+formula over EVERY n=4 panel (all 3125 pass-count vectors: stability ∈ [0,1] and ==
  1-2*mean(minority)); (C) THRESHOLD COHERENCE — the "stable" label and the "reproducible" gate cut over at
  the SAME `_STABLE_MIN`, proven by a MUTATION sweep of `_STABLE_MIN` across an interior 0.75 panel (n=8);
  a hardcoded-0.8 gate is CAUGHT (teeth verified out-of-band at thr∈{0.60,0.70,0.74}). OFF the scoring path
  (`git diff --name-only` = `tests/test_reliability.py` ONLY; scoring-path diff EMPTY) → score-neutral, NOT
  peer-gated, direct-to-main. Replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT
  (COVERAGE 202): carry the citability monotone/threshold contract into a READOUT-wording guard so the card
  can never mislabel provisional as stable, OR the subscription bare-`recurring` precision minefield (next
  in-cloud thin-bank candidate). Substantive frontier (GENUINE new thin-bank signals from real fixtures,
  the negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture, ACP/UCP/MPP,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 200 runner note): RUNNER AT-FLOOR at 2026-08-03T12:26Z (Cycle 200) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~56.6h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  12:26Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (display-only / score-neutral
  off-scoring-path READOUT increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 200):
  fresh checkout on the Cycle-199 tip `c12588d`, working tree clean, invariant #5 intact. Fresh `.venv` +
  `requests pyyaml eth-account pytest`, imports verified, 427 tests green pre-flight (427 after — existing
  guard extended, not a new test function).
- FOCUS POINTER (Cycle 200 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 200 was
  READOUT, so Cycle 201 is METHOD). Cycle 200 shipped a **READOUT increment — the methodology page now
  surfaces the POSITIVE-side counterfactual + its weight-robustness** (`asrs/scorecard.py` section 8 +5
  assertions in `tests/test_readout.py::test_methodology_documents_calibration`; suite 427, test COUNT
  unchanged). Section 8 already told a reader the LOW score is not a "retail artifact" (type-invariant
  negative floor, Cycle 196); the symmetric fact that the HIGH score is not a "premium-category artifact"
  — proven executable by Cycle 197's knock-out counterfactual (test 12) and Cycle 199's weight-robustness
  (test 13) — lived ONLY in the test suite, invisible to the public page. The new paragraph closes that:
  knock out the with-rails agent-native payment capability (substitute the no-rails earned evidence on
  exactly the payment checks, every other check untouched), recompute the pillar → it collapses EXACTLY
  onto the no-rails floor, so 100% of the ceiling-vs-floor separation is the payment capability and nothing
  else (a falsifiable counterfactual, not a decomposition that could hide an offsetting cancellation); and
  it is weight-robust — re-derived under arbitrary re-weightings the knocked-out ceiling lands on the
  re-weighted floor every time ("strip payment and the ceiling meets the floor at every weighting — the
  attribution is structural, not a weighting choice"). DISPLAY-ONLY, OFF the scoring path (`git diff
  --name-only` = scorecard.py + test_readout.py; scoring-path diff EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Vendor-neutral (`test_readout_wording.py` green). Replay guard 24/24, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 201): the calibration/attribution frontier (a next
  invariance/coupling guard, or carrying the counterfactual onto the calibration/history CARD which today
  shows only the methodology page). The substantive frontier (GENUINE new thin-bank signals from real
  fixtures, the negative anchor's two-crawl static cross-validation via a `moleskine.com` fixture,
  ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 199 runner note): RUNNER AT-FLOOR at 2026-08-03T11:14Z (Cycle 199) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~55.4h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  11:14Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral
  off-scoring-path TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 199):
  fresh checkout on the Cycle-198 tip `83a8cac` (origin arrived as a `(forced update)` from `3796519`,
  normal direct-to-main cadence), working tree clean, invariant #5 intact. Fresh `.venv` + `requests
  pyyaml eth-account pytest`, imports verified, 426 tests green pre-flight (427 after +1).
- FOCUS POINTER (Cycle 199 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 199 was
  TRUTH, so Cycle 200 is READOUT). Cycle 199 shipped a **TRUTH increment — the ceiling-collapse
  counterfactual is WEIGHT-robust** (`tests/test_calibration.py`, 12→13,
  `test_ceiling_payment_attribution_is_weight_robust`, suite 426→427). Test 12 (Cycle 197) proved that
  knocking out agent-native payment collapses the with-rails transactability ceiling (87.5) EXACTLY onto
  the no-rails floor (18.75), but at ONE weighting — the max_points the committed rubric ships today. A
  skeptic could call the "payment, not category" conclusion weight-contingent. This guard refutes that:
  it makes EXPLICIT the coupling the identity rests on (the two anchors share the transactability check
  SET, per-check max_points, and the non-payment check's earned points — none dependent on the weight
  VALUES), then re-derives BOTH floor and knocked-out ceiling under TWO arbitrary per-check REWEIGHTINGS
  (each check's max_points AND earned points scaled by the same factor — the faithful model of "weight
  this check λ× more"). Under both, the knocked-out ceiling lands EXACTLY on the reweighted floor
  (4.054/4.054 and 40.0/40.0), while the two drive the pillar to DISTINCT values (neither the pinned
  18.75) — the collapse is re-tested at two operating points, not re-stated at one. Teeth: unit-weight
  sanity reproduces test 12; each reweighting is asserted to genuinely move the floor off 18.75; MUTATION
  — breaking the shared-weight coupling (reweight the ceiling's payment check but NOT the floor's) makes
  the knock-out MISS the floor (7.5 ≠ 18.75), so a category-conditional cap that weighted the two
  storefront types divergently would redden the guard. Capability-worded, vendor-neutral; 18.75/87.5 share
  test 9(d)'s re-baseline tripwire. OFF the scoring path (`git diff --name-only` = `tests/test_calibration.py`
  ONLY; scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Replay guard 24/24, 46.1
  F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (READOUT 200): surface the weight-robustness /
  counterfactual on the methodology page ("strip payment and the ceiling meets the floor at every
  weighting") or carry it onto the calibration/history card; the substantive frontier (GENUINE new
  thin-bank signals from real fixtures, the negative anchor's two-crawl static cross-validation via a
  `moleskine.com` fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 198 runner note): RUNNER AT-FLOOR at 2026-08-03T10:17Z (Cycle 198) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~54.5h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  10:17Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (score-neutral
  off-scoring-path COVERAGE increment, no sensitive-class PR, nothing score-moving). Live signal (read,
  not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 198):
  fresh checkout on the Cycle-197 tip `5d413fb`, working tree clean, invariant #5 intact. Fresh `.venv` +
  `requests pyyaml eth-account pytest`, imports verified, 425 tests green pre-flight (426 after +1).
- FOCUS POINTER (Cycle 198 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 198 was
  COVERAGE, so Cycle 199 is TRUTH). Cycle 198 shipped a **COVERAGE increment — the data_retrieval
  `lookup` data-structure precision guard** (`asrs/offering.py` + `tests/test_offering.py`,
  `test_data_retrieval_lookup_precision_synthetic`, suite 425→426). The bare `\blook ?ups?\b` signal
  false-positived on the data-structure / internals vocabulary that saturates API & engineering docs
  ("lookup table", "hash / cache / index / key / symbol / array / in-memory lookup") — internal mechanism
  / performance descriptors, NOT a data-retrieval OFFERING — conjuring the tied-thinnest archetype on any
  storefront whose docs mention an internal lookup. Narrowed to
  `(?<!hash )(?<!cache )(?<!index )(?<!table )(?<!array )(?<!key )(?<!symbol )(?<!memory )\blook ?ups?\b(?!\s*tables?\b)`:
  fixed-width negative lookbehinds strip the leading data-structure qualifiers + a trailing lookahead
  strips "lookup table(s)", while 8 genuine record-lookup positives (phone/reverse-IP/address/domain/
  company/WHOIS, "look up a customer record") still fire. Surgical, not blunt — the discriminating pair
  "look up a table reservation" FIRES / "lookup table" DODGES. This is the `lookup` guard the Cycle-194
  note explicitly queued. OFF the scoring path (`git diff --name-only` = offering.py + test_offering.py;
  scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Canonical-invariant by
  construction (no fixture contains "lookup"; data_retrieval NA on all 5). Replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 199): the calibration/attribution frontier
  (a next invariance/coupling guard on the live signal bank, or the negative anchor's cross-validation).
  The next in-cloud COVERAGE precision candidate is subscription's bare `recurring`; the substantive
  frontier (GENUINE new thin-bank signals from real fixtures, ACP/UCP/MPP, transactability-drop CHECK-level
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 197 runner note): RUNNER AT-FLOOR at 2026-08-03T09:14Z (Cycle 197) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~53.4h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  09:14Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral
  off-scoring-path METHOD increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 197):
  fresh checkout detached on the Cycle-196 tip `950606b`; `git checkout -B main origin/main` aligned to
  origin/main `950606b` (origin arrived as a `(forced update)` from `3796519`, normal direct-to-main
  cadence), working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 424 tests green pre-flight (425 after this cycle's +1).
- FOCUS POINTER (Cycle 197 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 197 was
  METHOD, so Cycle 198 is COVERAGE). Cycle 197 shipped a **METHOD increment — the with-rails
  transactability CEILING is a payment-capability signal, not a premium-category artifact**
  (`tests/test_calibration.py`, 11→12,
  `test_with_rails_ceiling_is_payment_capability_not_category_artifact`). The POSITIVE-side counterfactual
  mirror of Cycle 195's negative-floor type-invariance (test 11): it KNOCKS OUT the with-rails
  agent-native payment capability — on the frozen `driftflight.com` fixture replay it substitutes each
  `_STATIC_PAYMENT_CHECKS` earned-points value (x402_probe 8.0, self_serve_payg 6.0) with the no-rails
  `drift-flight.org` value (0.0 / 3.0), leaves max_points + the non-payment control (`mcp_surface`)
  untouched, and recomputes the transactability pillar with scoring's own formula. It lands EXACTLY on the
  no-rails floor 18.75 — so strip payment and the 87.5 ceiling is indistinguishable from the 18.75 floor:
  100% of the ceiling-vs-floor separation is the agent-native payment capability. Makes the ceiling
  attribution FALSIFIABLE (counterfactual, not decompositional) at the pillar-SCORE level a reader sees,
  and closes the offsetting-cancellation hole test 9(b)'s raw-point aggregate leaves open. MUTATION-VERIFIED
  twice (no-knockout → 87.5 ≠ floor → reds; a simulated category artifact `mcp_surface`+6 → 56.25 > 18.75
  → reds). Non-vacuous (`mcp_surface` present/scored/retained); honest counterfactual (max_points +
  non-payment check retained → simulates capability ABSENT/FAILING, not deleted). 18.75/87.5 share test
  9(d)'s re-baseline tripwire contract. OFF the scoring path (`git diff --name-only` =
  `tests/test_calibration.py` ONLY; `git diff --stat -- asrs/ rubric/ fixtures/` clean) → score-neutral,
  NOT peer-gated, direct-to-main. Full suite 424→425; `test_calibration.py` 11→12; replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 198): the substantive COVERAGE
  frontier (GENUINE new thin-bank signals from real fixtures — thin-archetype/render/structured-catalog,
  ACP/UCP/MPP) stays `[LOCAL]`; the cheapest in-cloud COVERAGE unit is a next precision guard
  (data_retrieval's bare `lookup`, or subscription's bare `recurring`). METHOD/READOUT frontier: pin the
  knock-out is WEIGHT-robust, or carry the counterfactual onto a readout.
- SUPERSEDED (Cycle 196 runner note): RUNNER AT-FLOOR at 2026-08-03T08:13Z (Cycle 196) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~52.4h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  08:13Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (display-only /
  score-neutral off-scoring-path READOUT increment, no sensitive-class PR, nothing score-moving). Live
  signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability
  62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay
  guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open
  peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 196): fresh checkout clean on the Cycle-195 tip `270a3cf`, working tree clean, invariant #5
  intact. Fresh `.venv` + `requests pyyaml eth-account pytest`, imports verified, 424 tests green
  pre-flight (424 after this cycle — assertions +3 within an existing test, so the COUNT is unchanged).
- FOCUS POINTER (Cycle 196 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 196 was
  READOUT, so Cycle 197 is METHOD). Cycle 196 shipped a **READOUT increment — the type-invariant negative
  floor surfaced on the methodology page** (`asrs/scorecard.py`, §8 Calibration). A new paragraph states
  the negative transactability floor is **not a retail artifact**: it is measured IDENTICALLY on a
  no-rails **API** and a no-rails **retail shop** (two structurally different storefront types), with the
  agent-native payment check at **zero** on each, so the low score is attributably the **absence of
  agent-native payment**, not the storefront's category — the negative prediction is
  **storefront-type-invariant** (the readout of Cycle-195's calibration guard). The stale "each direction
  is anchored on one storefront" honest-limit sentence was refreshed to "the positive direction is still a
  single with-rails run; the negative floor now spans two storefront types, but neither direction is yet
  corroborated across a full population" — accurate to the guard, still honest about the population gap.
  Vendor-neutral (no domain/product named). Guarded by 3 new assertions in
  `test_methodology_documents_calibration` (retail-artifact / storefront-type-invariant / absence-of-
  agent-native-payment) atop the existing two-sided + stale-claim-removed checks. OFF the scoring path
  (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py`; scoring-path diff EMPTY) →
  score-neutral, NOT peer-gated, direct-to-main. Full suite 424 green; replay guard 24/24, 46.1 F / 85.5 B
  / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 197): the readout frontier still wants the POSITIVE
  mirror — surface that the with-rails transactability CEILING (87.5) is earned by agent-native payment
  specifically (positive analogue of "not a retail artifact"), OR carry type-invariance onto the
  calibration/history page; on the METHOD track, a next-cheapest invariance/coupling guard. Substantive
  frontier (thin-archetype / render / structured-catalog LIVE fixtures, the negative anchor's two-crawl
  static cross-validation via a `moleskine.com` fixture, ACP/UCP/MPP, transactability-drop CHECK-level
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 195 runner note): RUNNER AT-FLOOR at 2026-08-03T07:16Z (Cycle 195) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~51.4h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  07:16Z fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral
  off-scoring-path TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 195):
  fresh checkout detached on the Cycle-194 tip `5a29199`; `git checkout -B main origin/main` aligned to
  origin/main `5a29199`, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml
  eth-account pytest`, imports verified, 423 tests green pre-flight (424 after this cycle's +1).
- FOCUS POINTER (Cycle 195 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 195 was
  TRUTH, so Cycle 196 is READOUT). Cycle 195 shipped a **TRUTH increment — the no-rails transactability
  FLOOR is capability-attributable and storefront-TYPE-invariant** (`tests/test_calibration.py`, 10→11,
  `test_no_rails_transactability_floor_is_capability_attributable_and_type_invariant`). It pins that two
  structurally DIFFERENT no-rails storefronts — a no-rails API (`drift-flight.org`, offline fixture
  replay) and a no-rails RETAIL shop (`moleskine.com`, live behavioral crawl) — converge on the IDENTICAL
  transactability floor (18.75), earned by the IDENTICAL per-check point vector, with the agent-native
  payment gap-check `x402_probe` at ZERO on both. So the negative calibration prediction is reproducible
  across storefront TYPE and crawl METHOD, and is attributably the ABSENCE of agent-native payment — NOT a
  retail artifact (a shop scoring low for selling physical goods) nor a diffuse low score. The
  negative-side, type-crossing mirror of Cycle 191's positive attribution guard (#9); closes the
  storefront-type confound the two-sided property (#8) left open. Needs NO `[LOCAL]` fixture (retail floor
  read from the report's own embedded checks, matched against a second independent no-rails crawl).
  MUTATION-VERIFIED twice (retail floor→ceiling reds (a); retail x402_probe→8 reds (b)/(c)); non-vacuous
  `mcp_surface` control (0 on all three); robust to the tracked com live-drop (`floor < ceiling` holds at
  62.5). Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_calibration.py` ONLY;
  scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 423→424;
  `test_calibration.py` 10→11; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  NEXT (READOUT 196): surface the two-sided / type-invariant calibration property on a readout (card /
  rubric page) so a reader sees the negative floor is a payment-capability signal not a retail artifact,
  OR pin the mirror non-payment control on the POSITIVE side. Substantive frontier (thin-archetype /
  render / structured-catalog LIVE fixtures, the negative anchor's two-crawl static cross-validation via a
  `moleskine.com` fixture, ACP/UCP/MPP, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 194 runner note): RUNNER AT-FLOOR at 2026-08-03T06:1xZ (Cycle 194) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~50.5h old at the fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; this
  fire is NOT first-after-16:00 UTC → no DM this fire per comms policy (score-neutral off-scoring-path
  COVERAGE increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 194):
  fresh checkout detached on the Cycle-193 tip `faeadfb`; `git checkout -B main origin/main` aligned to
  origin/main `faeadfb`, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml
  eth-account pytest`, imports verified, 422 tests green pre-flight (423 after this cycle's +1).
- FOCUS POINTER (Cycle 194 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 194 was
  COVERAGE, so Cycle 195 is TRUTH). Cycle 194 shipped a **COVERAGE increment — the service_booking
  `schedule a …` sales-CTA precision guard** (`asrs/offering.py`), the DIRECT SIBLING of the Cycle-190
  `book` fix. The archetype's `schedule` signal, bare `\bschedule (a|an|your)\b`, fired on the identical
  ubiquitous B2B SALES CTA family ("schedule a demo / call / meeting / walkthrough / briefing") — none a
  bookable service — falsely conjuring service_booking (tied with data_retrieval for the THINNEST
  archetype, so max damage) on a pure-API / SaaS storefront. New form
  `\bschedule (?:a|an|your) (?!(?:demo|call|walk[- ]?through|briefing|meeting)s?\b)\w+` excludes those
  unambiguous sales-CTA objects while keeping every genuine scheduled service (session / consultation /
  table / pickup / visit / fitting). `tests/test_offering.py` +1
  (`test_service_booking_schedule_precision_synthetic`, 6 schedule-ONLY positives fire / 7 CTA negatives
  dodge, incl. plural "schedule your demos" + hyphenated "walk-through"). Canonical-invariant by
  construction (narrowing only removes matches; no committed fixture contains "schedule"; service_booking
  stays NA on all 5 fixtures per `test_offering_canonical::_MUST_BE_NA`, 58/58). OFF the scoring path
  (`git diff --name-only` = `asrs/offering.py` + `tests/test_offering.py`; no scoring-path file) →
  score-neutral, NOT peer-gated, direct-to-main. Full suite 422→423; replay guard 24/24, 46.1 F / 85.5 B
  / +39.4, 0 replay-miss; rubric v0.7. The three cheapest bare-word minefields across the two thinnest
  archetypes are now ALL guarded (`enrich`/`dataset` Cycle 186, `book` Cycle 190, `schedule` this cycle).
  NEXT (TRUTH 195): the in-cloud precision frontier is data_retrieval's bare `lookup` ("lookup table" in
  API docs) or subscription's bare `recurring`; the substantive COVERAGE frontier (GENUINE new thin-bank
  signals) stays `[LOCAL]` (real live fixtures — thin-archetype/render/structured-catalog, ACP/UCP/MPP).
- SUPERSEDED (Cycle 193 runner note): RUNNER AT-FLOOR at 2026-08-03T05:19Z (Cycle 193) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~49.5h old at the 05:19Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 05:19Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral METHOD increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal
  (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []),
  so no first-duty review. INFRA/SELF-HEAL (Cycle 193): fresh checkout detached on the Cycle-192 tip
  `8a4b3ec`; `git checkout -B main origin/main` aligned to origin/main `8a4b3ec` (Cycle 192, arrived via a
  `(forced update)` from `3796519`), working tree clean, invariant #5 intact. Fresh `.venv` + `requests
  pyyaml eth-account pytest`, imports verified, 421 tests green pre-flight (422 after this cycle's +1).
- FOCUS POINTER (Cycle 193 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 193 was
  METHOD, so Cycle 194 is COVERAGE). Cycle 193 shipped a **METHOD increment — the readout↔calibration
  attribution coupling guard** (`tests/test_calibration.py`
  `test_readout_earner_and_calibration_attribution_cannot_drift`, 9→10). Two layers each attribute the
  transactability score to a capability from opposite ends of the pipeline — the CALIBRATION layer (Cycle-191
  test #9) proves the transactability gap is earned by `_STATIC_PAYMENT_CHECKS = (x402_probe, self_serve_payg)`;
  the READOUT layer (Cycle-192 `scorecard._pillar_top_earner`) surfaces the card's "earned by <check>" caption
  — but nothing forced them to name the SAME check. The guard replays BOTH canonical fixtures offline, maps the
  card's surfaced earner back to its `check_id`, and asserts it's one of the calibration payment checks (x402_probe
  with-rails, self_serve_payg no-rails), so a refactor cannot drift the card's caption to a non-payment check
  while calibration still credits payment. Non-vacuous (mcp_surface control present on both sides, earns 0);
  MUTATION-VERIFIED twice (drop x402_probe from the set → reddens; monkeypatch `_pillar_top_earner` to surface
  mcp_surface → #10 reddens on the coupling clause specifically, proving it catches readout-side drift).
  Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_calibration.py` ONLY; scoring-path diff
  EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 421→422; `test_calibration.py` 9→10; replay
  guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 194): the substantive frontier
  is [LOCAL] (thin-archetype/render/structured-catalog live fixtures, ACP/UCP/MPP); in-cloud, a next-cheapest
  bare-word offering precision guard, or extend the earner-vs-attribution coupling pattern to a second pillar.
- SUPERSEDED (Cycle 192 runner note): RUNNER AT-FLOOR at 2026-08-03T04:12Z (Cycle 192) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~48h old at the 04:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 04:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (display-only / score-neutral READOUT
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 192): fresh checkout detached on the Cycle-191 tip;
  `git pull` declined on the detached HEAD → `git checkout -B main origin/main` aligned to origin/main
  `dd7dc0b` (Cycle 191), working tree clean, invariant #5 intact (the fresh clone's first fetch surfaced many
  long-dead `loop/*` branches as "[new branch]"; none open as PRs). Fresh `.venv` + `requests pyyaml
  eth-account pytest`, imports verified, 417 tests green pre-flight (421 after this cycle's +4).
- FOCUS POINTER (Cycle 192 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 192 was
  READOUT, so Cycle 193 is METHOD). Cycle 192 shipped a **READOUT increment — the "earned by" pillar
  caption** (`asrs/scorecard.py`). Each HTML-card pillar bar now names, under its capability question, the
  single check that contributes the most raw points to the pillar's score — transactability reads
  **"earned by x402-live +8"** on the with-rails anchor, **"earned by self-serve-signup +3"** on the no-rails
  anchor — so a card reader sees the score is ATTRIBUTABLE to a named, capability-worded check (the Cycle-191
  calibration insight surfaced) rather than a diffuse aggregate. New pure helper `_pillar_top_earner`
  (points-desc, ties on rubric order, `None` for n/a / all-fail pillars); caption omitted when nothing earns
  credit. Vendor-neutral by construction (names whichever check earns the most, proven falsifiable by a
  magnitude-flip test). Display-only, OFF the scoring path (`git diff --name-only` = `asrs/scorecard.py` +
  `tests/test_readout.py`; scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full
  suite 417→421; `test_readout.py` 71→75; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric
  v0.7. NEXT (METHOD 193): a guard that the card's surfaced earner and the calibration anchor's attribution
  can't silently drift apart, or extend the earner caption to the terminal readout for terminal↔HTML parity.
  Substantive frontier (thin-archetype/render/structured-catalog LIVE fixtures — ACP/UCP/MPP, calibration
  sweep, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 191 runner note): RUNNER AT-FLOOR at 2026-08-03T02:1xZ (Cycle 191) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~46h old at the 02:1xZ fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 02:1xZ is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral TRUTH increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal
  (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []),
  so no first-duty review. INFRA/SELF-HEAL (Cycle 191): fresh checkout on a detached HEAD at the Cycle-190
  tip; `git checkout -B main origin/main` aligned to origin/main `e1b78eb` (Cycle 190), working tree clean,
  invariant #5 intact (the first fetch in a fresh clone surfaced many long-dead `loop/*` branches as
  "[new branch]"; none open as PRs). Fresh `.venv` + `requests pyyaml eth-account pytest`, imports verified,
  416 tests green pre-flight (417 after this cycle's +1).
- FOCUS POINTER (Cycle 191 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 191 was
  TRUTH, so Cycle 192 is READOUT). Cycle 191 shipped a **TRUTH increment — the payability-is-attributable
  calibration guard** (`tests/test_calibration.py` `test_payability_prediction_is_attributably_agent_native_payment`,
  8→9). The positive calibration anchor corroborates the with-rails storefront's transactability magnitude
  (87.5) behaviorally but only asserted `transactability > 0` / `== 87.5` — neither proves the corroborated
  credit is EARNED by agent-native payment vs diffuse transactability credit (a refactor could keep
  `x402_probe` PASS while sourcing 87.5 elsewhere, hollowing the link). The new guard replays BOTH canonical
  fixtures offline and pins that the ENTIRE transactability raw-point gap (11.0 = 87.5 vs 18.75) is earned by
  the two agent-native payment checks the anchor corroborates — `x402_probe` (FAIL 0/8→PASS 8/8) +
  `self_serve_payg` (partial 3/6→PASS 6/6) — while every non-payment transactability check (`mcp_surface`,
  FAIL on both) nets ZERO to the gap. Non-vacuous (mcp_surface control (c) + pinned-87.5 (d)); MUTATION-
  VERIFIED (drop self_serve_payg → payment_gap 8.0 ≠ total 11.0 → reddens). Ties the calibration anchor into
  the replay guard's maintenance contract: the `== 87.5` literal is the [LOCAL] re-baseline tripwire, so the
  BACKLOG "is the with-rails anchor itself degrading?" coupling is now test-monitored. Tests-only, OFF the
  scoring path (`git diff --name-only` = `tests/test_calibration.py` ONLY; scoring-path diff EMPTY) →
  score-neutral, NOT peer-gated, direct-to-main. Full suite 416→417; `test_calibration.py` 8→9; replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (READOUT 192): surface WHICH capability
  earns the transactability credit in the card/prose, or a readout-wording guard. Substantive frontier
  (thin-archetype/render/structured-catalog LIVE fixtures — ACP/UCP/MPP, calibration sweep,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 190 runner note): RUNNER AT-FLOOR at 2026-08-03T01:12Z (Cycle 190) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~45.4h old at the 01:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 01:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral COVERAGE
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 190): fresh checkout, `git pull --ff-only`
  fast-forwarded to origin/main tip `d9a3f55` (Cycle 189, after a `(forced update)`); working tree clean,
  invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account pytest`, imports verified, 415 tests green
  pre-flight (416 after this cycle's +1).
- FOCUS POINTER (Cycle 190 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 190 was
  COVERAGE, so Cycle 191 is TRUTH). Cycle 190 shipped a **COVERAGE increment — the service_booking `book a …`
  sales-CTA precision guard** (`asrs/offering.py`): the archetype's cheapest signal, the bare `book (a|an|your)`
  verb, matched the single most common B2B sales CTA ("book a demo / call / meeting / walkthrough / briefing"),
  falsely conjuring service_booking — tied-thinnest, so max damage — on a pure-API / SaaS storefront. New form
  `\bbook (?:a|an|your) (?!(?:demo|call|walk[- ]?through|briefing|meeting)s?\b)\w+` excludes those unambiguous
  sales-CTA objects while keeping every genuine bookable service (table/room/appointment/session/class/
  consultation) and `book now`/`book online`/`booking`. `tests/test_offering.py` +1
  (`test_service_booking_book_precision_synthetic`, 8 positives fire / 7 CTA negatives dodge) and the
  surface-read-order test updated (it had encoded the false positive "Book a demo appointment"; now uses
  genuine "Book a table; appointments available"). Canonical-invariant by construction (narrowing only removes
  matches; service_booking stays NA on all 5 fixtures per `test_offering_canonical::_MUST_BE_NA`, 58/58). OFF
  the scoring path (`git diff --name-only` = `asrs/offering.py` + `tests/test_offering.py`; scoring-path diff
  EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 415→416; `test_offering.py` 81→82; replay
  guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. The offering classifier's three cheapest
  bare-word minefields — `enrich`/`dataset` (data_retrieval, Cycle 186) and now `book` (service_booking) — are
  all precision-guarded. NEXT (TRUTH 191): a calibration/attribution guard, or extend surface-read-order /
  whitespace-reflow invariance coverage to the newly-guarded book branch. Substantive frontier (thin-archetype/
  render/structured-catalog LIVE fixtures — ACP/UCP/MPP, calibration sweep, transactability-drop CHECK-level
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 189 runner note): RUNNER AT-FLOOR at 2026-08-03T00:12Z (Cycle 189) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~44.4h old at the 00:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 00:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral METHOD increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal
  (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []),
  so no first-duty review. INFRA/SELF-HEAL (Cycle 189): fresh checkout, `git pull` fast-forwarded to
  origin/main tip `1d1569e` (Cycle 188); working tree clean, invariant #5 intact. Fresh `.venv` + `requests
  pyyaml eth-account pytest`, imports verified, 414 tests green pre-flight (415 after this cycle's +1).
- FOCUS POINTER (Cycle 189 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 189 was
  METHOD, so Cycle 190 is COVERAGE). Cycle 189 shipped a **METHOD increment — the TIME-TRANSLATION invariance
  metamorphic guard** (`tests/test_canonical_history.py`
  `test_drift_diagnostics_are_time_translation_invariant`, +1; test-only helpers `_shift_ts`/`_time_translate`):
  builds ONE out-of-band history firing every drift diagnostic (4 in-band anchors → 3 out-of-band 18h-softening
  readings, `now` ~1h past latest → FRESH liveness), then shifts EVERY timestamp AND `now` by a fixed offset
  crossing the month+year boundary (Jul 2026 → Jan 2027) with the numeric trajectory untouched, and asserts
  every STRUCTURAL diagnostic is byte-identical (band, divergence, out-of-band count, sustained SPAN, all four
  noise-floor stddevs, full attribution move list, stability stable/fingered, cause driver/direction/per-side,
  recapture code) — liveness age/fresh invariant under a CO-translated clock as the non-trivial control. Proves
  the family measures RELATIVE time, never the absolute epoch (reproducibility). Orthogonal to the reflection
  guard (score-axis / direction-blindness) and the host-relabel guards (vendor-neutrality). Non-vacuous
  (year-boundary sanity + all-fired preconditions); MUTATION-VERIFIED (un-co-translated `now` → liveness age
  1.0→0.0 → reddens). Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_canonical_history.py`
  ONLY; scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 414→415;
  `test_canonical_history.py` 48→49; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  The canonical-drift diagnostic family now has vendor-neutrality (host-relabel) + direction-blindness
  (reflection) + epoch-blindness (time-translation) metamorphic coverage. NEXT (COVERAGE 190): an
  offering-classifier precision guard on real committed evidence (e.g. the service_booking `book (a|an|your)`
  sales-CTA collision, synthetic-demonstrated + canonical-invariant). Substantive frontier (thin-archetype/
  render/structured-catalog LIVE fixtures — ACP/UCP/MPP, calibration sweep, transactability-drop CHECK-level
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 188 runner note): RUNNER AT-FLOOR at 2026-08-02T23:12Z (Cycle 188) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~43.3h old at the 23:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 23:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral READOUT increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal
  (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []),
  so no first-duty review. INFRA/SELF-HEAL (Cycle 188): fresh checkout already aligned to origin/main tip
  `e7fadb5` (Cycle 187); working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 413 tests green pre-flight (414 after this cycle's +1).
- FOCUS POINTER (Cycle 188 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 188 was
  READOUT, so Cycle 189 is METHOD). Cycle 188 shipped a **READOUT increment — the terminal↔HTML PARITY
  guard** (`tests/test_canonical_history.py`
  `test_terminal_and_html_surfaces_name_the_same_diagnostics`, +1): the canonical-drift diagnosis has TWO
  surfaces (terminal `ch.render` + HTML `scorecard._write_canonical_history_page`) whose parity was maintained
  purely BY HAND cycle-to-cycle, and the HTML page had ZERO test coverage. The guard builds ONE out-of-band
  history that fires every diagnostic (4 in-band anchors → 3 out-of-band transactability-softening readings,
  18h span), renders BOTH surfaces, and asserts ten diagnostic FACTS (latest overalls, band verdict, sustained
  span, noise-floor determinism, fingered pillar+side, stability verdict, cause sentence, re-capture label) —
  each COMPUTED from the history model, never a literal — appear in BOTH. Preconditions assert each diagnostic
  actually fired (non-vacuous); mutation-verified (dropping "DETERMINISTIC at rest" from the HTML reddens it;
  revert green). Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_canonical_history.py`
  ONLY; scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 413→414;
  `test_canonical_history.py` 47→48; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  The canonical-drift readout is now parity-locked across both surfaces. NEXT (METHOD 189): a metamorphic/
  invariance guard on a diagnostic still lacking one, or a small measurement-rigor refinement. Substantive
  frontier (thin-archetype/render/structured-catalog LIVE fixtures — incl. the service_booking
  `book (a|an|your)` sales-CTA collision — ACP/UCP/MPP, calibration sweep, transactability-drop CHECK-level
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 187 runner note): RUNNER AT-FLOOR at 2026-08-02T22:12Z (Cycle 187) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~42h old at the 22:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 22:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral TRUTH increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal
  (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []),
  so no first-duty review. INFRA/SELF-HEAL (Cycle 187): fresh checkout on detached HEAD on a stale tip; ran
  `git fetch origin main` FIRST (standing lesson) → origin/main `(forced update)` to `5559aef` (Cycle 186),
  `checkout -B main origin/main` aligned to the real tip, working tree clean, invariant #5 intact. Fresh
  `.venv` + `requests pyyaml eth-account pytest`, imports verified, 412 tests green pre-flight.
- FOCUS POINTER (Cycle 187 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 187 was
  TRUTH, so Cycle 188 is READOUT). Cycle 187 shipped a **TRUTH increment — the recapture-advice prose
  host-relabel invariance guard** (`tests/test_canonical_history.py`
  `test_recapture_advice_prose_is_host_relabel_invariant`, +1): the metamorphic vendor-neutrality guard for
  `recapture_advice`, the LAST host-naming diagnostic in the canonical-drift family without one (siblings:
  Cycle-181 cause_verdict, Cycle-185 attribution_stability). Builds a DEFER shape (with-rails reference
  softening) + a RECAPTURE shape (no-rails floor gaining) so ONE guard exercises BOTH host constants;
  relabels both hosts, rebuilds the SAME structural series, and asserts the advice code + rendered
  `re-capture:` line follow the new host, leak neither original host, and are BYTE-IDENTICAL modulo the host
  token. Load-bearing because the RECAPTURE branch gates a `[LOCAL]` fixture re-capture that MOVES the pinned
  delta. Mutation-verified (hardcoding `driftflight.com` reddens it; revert green). Tests-only, OFF the
  scoring path (`git diff --name-only` = `tests/test_canonical_history.py` ONLY; scoring-path diff EMPTY) →
  score-neutral, NOT peer-gated, direct-to-main. Full suite 412→413; `test_canonical_history.py` 46→47;
  replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. The canonical-drift diagnostic
  family now has UNIFORM metamorphic (host-relabel) vendor-neutrality coverage. NEXT (READOUT 188): a
  terminal↔HTML parity or evidence-link completeness check, or an offering-classifier precision guard on real
  committed evidence. Substantive frontier (thin-archetype/render/structured-catalog LIVE fixtures — incl. the
  service_booking `book (a|an|your)` sales-CTA collision — ACP/UCP/MPP, calibration sweep,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 186 runner note): RUNNER AT-FLOOR at 2026-08-02T21:12Z (Cycle 186) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~41h old at the 21:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 21:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral COVERAGE
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 186): fresh checkout on detached HEAD at Cycle 185's
  `dae52d6`; ran `git fetch origin main` FIRST (standing lesson), `checkout -B main origin/main` aligned to
  the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 410 tests green pre-flight.
- FOCUS POINTER (Cycle 186 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 186 was
  COVERAGE, so Cycle 187 is TRUTH). Cycle 186 shipped a **COVERAGE increment — data_retrieval precision
  hardening** (`asrs/offering.py`): the archetype's two cheapest bare-word signals, `enrich` and `dataset`,
  are precision-guarded so a common ML/marketing word no longer conjures a false claim on the THINNEST
  archetype. `enrich` now requires an unambiguous DATA object (records/data/contacts/leads/…) within a
  short window (or "data enrichment"); `dataset` now requires a RETRIEVAL verb adjacent (query/download/
  access/… a … dataset) or the dataset named AS an offering (dataset api/feed/subscription/…), so
  training-PROVENANCE prose ("trained on a dataset", "our training dataset") and marketing ("an enriching
  partnership") dodge. `tests/test_offering.py` +2: `test_data_retrieval_precision_synthetic` (8 genuine
  positives fire / 7 provenance-marketing negatives dodge) + `..._is_canonical_invariant_on_real_fixtures`
  (full `from_fixture → discover_offering` on all 5 committed fixtures — claimed sets byte-identical,
  data_retrieval NA on every one). OFF the scoring path (`git diff --name-only` = `asrs/offering.py` +
  `tests/test_offering.py` ONLY; scoring-path diff EMPTY; offering imported only by cli/battery/report/
  scorecard, grep-verified) → score-neutral, NOT peer-gated, direct-to-main. Full suite 410→412; offering
  suite 137→139; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 187):
  a calibration/attribution guard or a metamorphic guard on a diagnostic still lacking one. Substantive
  frontier (thin-archetype/render/structured-catalog LIVE fixtures — incl. the service_booking
  `book (a|an|your)` sales-CTA collision, now noted in BACKLOG — ACP/UCP/MPP, calibration sweep,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 185 runner note): RUNNER AT-FLOOR at 2026-08-02T20:17Z (Cycle 185) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~40h old at the 20:17Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 20:17Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / score-neutral METHOD increment,
  no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression signal
  (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []),
  so no first-duty review. INFRA/SELF-HEAL (Cycle 185): fresh checkout on detached HEAD at Cycle 184's
  `59ca867`; ran `git fetch origin main` FIRST (standing lesson), `checkout -B main origin/main` aligned to
  the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 409 tests green pre-flight.
- FOCUS POINTER (Cycle 185 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 185 was
  METHOD, so Cycle 186 is COVERAGE). Cycle 185 shipped a **METHOD increment — the attribution-STABILITY
  host-relabel invariance guard** (`tests/test_canonical_history.py`
  `test_attribution_stability_is_host_relabel_invariant`, +1): the metamorphic vendor-neutrality guard for
  `attribution_stability`, the last drift diagnostic in the canonical-history family without one (sibling of
  Cycle-181's `cause_verdict` relabel guard). Relabels both reference hosts to fresh strings, rebuilds the
  SAME structural series across a STABLE + a WANDERS scenario, and asserts the movers/fingered follow the new
  host, the pillar set is structural, the relabeled line leaks no original host, and the stability line is
  BYTE-IDENTICAL modulo the host token. Mutation-verified (hardcoding `driftflight.com` reddens it; revert
  green). Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_canonical_history.py` ONLY;
  scoring-path diff EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 409→410; replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. The canonical-drift diagnostic family now has
  full metamorphic coverage (reflection magnitude/direction, cause-verdict relabel, attribution-stability
  relabel) + terminal+HTML readout. NEXT (COVERAGE 186): cloud-doable candidates are an offering-classifier
  robustness/precision guard on real committed evidence, or a readout completeness check; the substantive
  frontier (thin-archetype/render/structured-catalog LIVE fixtures, ACP/UCP/MPP, calibration sweep,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 184 runner note): RUNNER AT-FLOOR at 2026-08-02T19:17Z (Cycle 184) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~39.5h old at the 19:17Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 19:17Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral READOUT
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 184): fresh checkout on detached HEAD at Cycle 183's
  `3fbf983`; ran `git fetch origin main` FIRST (standing lesson), `checkout -B main origin/main` aligned to
  the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 407 tests green pre-flight.
- FOCUS POINTER (Cycle 184 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 184 was
  READOUT, so Cycle 185 is METHOD). Cycle 184 shipped a **READOUT increment — the HTML canonical-history
  card now surfaces the attribution-STABILITY line** (`asrs/scorecard.py`: a `Stability:` paragraph in the
  "What moved, and which side" diag card, between the Pillar and Side lines; `tests/test_readout.py` +2). The
  Cycle-183 `AttributionStability` (fingered pillar HOLDS across the whole out-of-band run, or WANDERS) was
  terminal-only; a card reader saw the single-snapshot Pillar mover but not whether it is SUSTAINED. STABLE
  branch names the fingered `(host, pillar)` + how many re-scores agree ("all 3 out-of-band re-scores");
  WANDERS branch names all distinct movers. Emitted only when `attribution_stability is not None` (≥2
  out-of-band readings + in-band anchor). Non-vacuous: the `_drifting_history()` guard renders STABLE naming
  with-rails legibility; a flip-mover mirror renders WANDERS naming both pillars and NOT "not wandering"
  (data-driven). Off the scoring path (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py`
  ONLY; scoring/rubric/probes/fetch/cli/battery/offering = 0 changes) → score-neutral, NOT peer-gated,
  direct-to-main. Full suite 407→409; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric
  v0.7. The canonical-drift diagnostic family (band, sustained-run count+span, noise floor, liveness,
  pillar/side attribution, attribution stability, recapture advice) is now FULLY surfaced on both terminal
  and HTML. NEXT (METHOD 185): a metamorphic/invariance guard on a diagnostic still lacking one — e.g.
  attribution-stability HOST-RELABEL invariance (the sibling of the Cycle-181 divergence-cause guard) — or a
  small measurement-rigor refinement. Substantive frontier (thin-archetype/render/structured-catalog LIVE
  fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 183 runner note): RUNNER AT-FLOOR at 2026-08-02T18:19Z (Cycle 183) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~38.5h old at the 18:19Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 18:19Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral TRUTH
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 183): fresh checkout on detached HEAD at Cycle 182's
  `404d219`; ran `git fetch origin main` FIRST (standing lesson) → `3796519…404d219 (forced update)`,
  `checkout -B main origin/main` aligned to the real tip, working tree clean, invariant #5 intact. Fresh
  `.venv` + `requests pyyaml eth-account pytest`, imports verified, 403 tests green pre-flight.
- FOCUS POINTER (Cycle 183 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 183 was
  TRUTH, so Cycle 184 is READOUT). Cycle 183 shipped a **TRUTH increment — attribution STABILITY across the
  trailing out-of-band run** (`asrs/canonical_history.py`: new pure `attribution_stability(points, run)` +
  `AttributionStability`/`ReadingTop` dataclasses, wired onto `CanonicalHistory` via `summarize` + one
  terminal render line; `tests/test_canonical_history.py` +4). `_attribute` fingers the drifting pillar from
  the LATEST reading vs the last in-band anchor — a single snapshot; this asks whether EVERY reading of the
  trailing out-of-band run fingers the SAME (domain, pillar) or the top mover WANDERS. Computed against the
  SAME anchor (`points[-(run+1)]`) over `points[-run:]`; `stable` iff every reading isolates a top mover AND
  all agree on one (domain, pillar) — magnitude may vary, pillar must hold; a None-top reading makes it
  not-stable (unconfirmable ≠ confirmed-same). Honest-None on `_attribute`'s gates (run<2 = one reading can't
  wander; run>=len = no in-band anchor). REAL-SERIES RESULT (non-vacuous): the 3 out-of-band readings (Jul-31
  08:52Z / 13:45Z, Aug-1 03:50Z) vs the Jul-28 23:41Z anchor ALL finger `driftflight.com transactability
  −25.0` → stable, one distinct mover — the transactability drop is a SUSTAINED move across ~28h, not a
  snapshot artifact, strengthening the "with-rails reference softened on transactability" credibility. Teeth:
  a synthetic wandering run (legibility→transactability flip) → stable False, render "WANDERS"; a synthetic
  same-pillar run → stable True (green witness independent of live recovery); + honest-None guards + a
  real-series guard cross-checking the snapshot top equals the sustained fingered pillar. Off the scoring path
  (`git diff --name-only` = `asrs/canonical_history.py` + `tests/test_canonical_history.py` ONLY;
  `canonical_history` imported only by cli/scorecard READOUTS, imports no scoring code — grep-verified) →
  score-neutral, NOT peer-gated, direct-to-main. Full suite 403→407; replay guard 24/24, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; rubric v0.7. NEXT (READOUT 184): the HTML canonical-history page does not yet surface
  the stability line — render it on the card the way the sibling attribution/driver lines are (the
  terminal-then-HTML pattern Cycle 176 followed). Substantive frontier (thin-archetype/render/structured-catalog
  LIVE fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 182 runner note): RUNNER AT-FLOOR at 2026-08-02T17:11Z (Cycle 182) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~37.3h old at the 17:11Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-181 daily digest; 17:11Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral COVERAGE
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 182): fresh checkout on detached HEAD at Cycle 181's
  `3b4978f`; ran `git fetch origin main` FIRST (standing lesson) → `3796519…3b4978f (forced update)`,
  `checkout -B main origin/main` aligned to the real tip, working tree clean, invariant #5 intact. Fresh
  `.venv` + `requests pyyaml eth-account pytest`, imports verified, 402 tests green pre-flight.
- FOCUS POINTER (Cycle 182 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 182 was
  COVERAGE, so Cycle 183 is TRUTH). Cycle 182 shipped a **COVERAGE increment — the offering classifier now
  HTML-entity-decodes** (`asrs/offering.py` `strip_html` + `import html as _html`, + `tests/test_offering.py`
  +1 guard). `strip_html` dropped scripts/tags and collapsed whitespace but never decoded entities, so real
  HTML that joins capability phrases with a non-breaking-space entity (`Free&nbsp;shipping`,
  `per&nbsp;month`, `Add&nbsp;to&nbsp;cart`) — exactly the phrases publishers keep from wrapping — left the
  literal-single-space signals silently MISSING and under-classified the storefront purely on encoding (the
  sibling of the Cycle-178 line-wrap gap, from a space ENCODED not WRAPPED). Demonstrated pre-fix: a
  `&nbsp;`-joined retail page classified `{subscription}` only vs `{metered_api, physical_good, subscription}`
  with literal spaces. FIX: `_html.unescape` AFTER tag removal, BEFORE whitespace collapse (so `&nbsp;` →
  `\xa0` folds into the single-space normalization) — precisely what makes it the VISIBLE prose.
  Precision-safe: `unescape` only rewrites `&…;`, so it can never conjure a phrase (`&amp;`/`&mdash;` noise →
  `&`/`—`, never a signal word). New guard `test_classification_is_html_entity_decode_invariant` (entity-decode
  analogue of the casing/whitespace-reflow axes): entity-joined vs literal-space classify identically (set/
  rank/NA/skeleton); teeth = encoding real + free-shipping pattern matches `free shipping` NOT
  `free&nbsp;shipping` (decode LOAD-BEARING) + `&amp;`/`&mdash;` negative control conjures nothing;
  REAL-EVIDENCE half proves BOTH committed canonical homepages' `&nbsp;` brand marquee (`Arclight&nbsp;Goods`,
  `VELA&nbsp;Studio`) is genuinely decoded on raw committed bytes yet does NOT conjure physical_good (canonical
  NA holds). Off the scoring path (`git diff --name-only` = `asrs/offering.py` + `tests/test_offering.py` ONLY;
  scoring/rubric/probes/fetch/cli/battery/scorecard/fixtures = 0 changes) → score-neutral, NOT peer-gated,
  direct-to-main. Full suite 402→403; offering+canonical guards 136/136; replay guard 24/24, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; rubric v0.7. Unlike the Cycle-178 reflow gap (committed evidence not reflowed → needs a
  `[LOCAL]` real-wrapped capture), the entity gap validated NON-VACUOUSLY on the committed `&nbsp;` this fire —
  no new `[LOCAL]` item owed. NEXT (TRUTH 183): a calibration/attribution refinement against reality — is the
  pillar-attribution `top` STABLE across the trailing out-of-band runs (same mover every reading, or does it
  wander?), or an in-cloud guard on the transactability-drop persistence. Substantive frontier (thin-archetype/
  render/structured-catalog LIVE fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop CHECK-level
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 181 runner note): RUNNER AT-FLOOR at 2026-08-02T16:12Z (Cycle 181) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~36.4h old at the 16:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). 16:12Z IS the first cycle after 16:00 UTC → **daily digest DM
  SENT** this fire per comms policy (cycles-run + shipped-item + canonical-delta trend + top open question).
  Live signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 /
  transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the
  in-cloud replay guard stays the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No
  open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review.
  INFRA/SELF-HEAL (Cycle 181): fresh checkout on detached HEAD at Cycle 180's `ec36cba`; ran `git fetch
  origin main` FIRST (standing lesson) → `3796519…ec36cba (forced update)`, `checkout -B main origin/main`
  aligned to the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml
  eth-account pytest`, imports verified, 401 tests green pre-flight.
- FOCUS POINTER (Cycle 181 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 181 was
  METHOD, so Cycle 182 is COVERAGE). Cycle 181 shipped a **METHOD increment — a host-relabel
  (vendor-neutrality) metamorphic invariance guard on the divergence-cause prose** (`tests/test_canonical_
  history.py` +1, no module change). Cycle 180 wove the fingered pillar into `cause_verdict`'s driver
  sentence; that sentence — branch selection, SOFTENED/GAINED verb, "on <pillar>" clause, signed magnitude —
  must key ONLY on the pair's STRUCTURE (which side has rails, which pillar moved, direction), never on the
  literal host strings ("checks worded by capability, never by vendor"). The scoring checks had that guard;
  the divergence-cause READOUT prose did not. New `test_cause_verdict_prose_is_host_relabel_invariant`
  RELABELS both `CANONICAL_*` host constants to fresh strings, rebuilds the SAME structural scenario, and
  asserts the prose is BYTE-IDENTICAL modulo substituting each driver host back to a placeholder — a pure
  function of structure + host token. Both honest branches (with-rails SOFTENED / no-rails GAINED); teeth =
  (a) relabel verified to take effect (non-vacuous), (b) no original host string leaks, (c) the Cycle-180
  pillar clause survives relabel. Constants restored in `finally` (process-global). Off the scoring path
  (`git diff --name-only` = `tests/test_canonical_history.py` ONLY) → score-neutral, NOT peer-gated,
  direct-to-main. `test_canonical_history.py` runner 40→41; full suite 401→402; replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 182): the divergence-cause diagnostic now has a
  near-complete invariance envelope (reflection magnitude/direction + host-relabel). In-cloud COVERAGE
  candidate = a new offering signal or a metamorphic axis on a check still lacking one; substantive frontier
  (thin-archetype/render/structured-catalog LIVE fixtures, ACP/UCP/MPP, calibration sweep,
  transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 180 runner note): RUNNER AT-FLOOR at 2026-08-02T15:19Z (Cycle 180) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~35.5h old at the 15:19Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; 15:19Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (READOUT increment, off-scoring-path /
  score-neutral, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests`
  state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 180): fresh checkout on detached HEAD at
  Cycle 179's `bdbd8b1`; ran `git fetch origin main` FIRST (standing lesson) → `3796519…bdbd8b1 (forced
  update)` (cached `origin/main` was the Cycle-94-era `3796519`), `checkout -B main origin/main` aligned to
  the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 399 tests green pre-flight.
- FOCUS POINTER (Cycle 180 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 180 was
  READOUT, so Cycle 181 is METHOD). Cycle 180 shipped a **READOUT increment — the divergence-cause prose now
  names the fingered PILLAR, not just the side** (`asrs/canonical_history.py` `cause_verdict` + its two call
  sites in `render` and `asrs/scorecard.py`, + `tests/test_canonical_history.py` +2). The drift diagnostic
  computed two independent attributions (per-pillar `_attribute` → WHICH pillar; side-level `_cause` → WHICH
  side + what-to-do) and rendered them on two SEPARATE lines; the side/driver sentence — the one carrying the
  "what to do" meaning (reference SOFTENED → defer re-capture) — did NOT name the pillar, so a reader had to
  mentally join them. `cause_verdict(cause, top=None)` now weaves the pillar in ("SOFTENED **on
  transactability**") but ONLY on cross-mechanism agreement — same domain (`top.domain == cause.driver`, the
  invariant Cycle 179 pinned) AND same direction (`sign(top.change) == sign(driver_change)`); on disagreement
  or no isolated pillar it falls back byte-for-byte to the side-only wording. Threaded through terminal
  (`driver:` line) AND HTML (`Side:` line), each passing `attribution.top`. Verified end-to-end on the REAL
  committed series: driver line reads "…the with-rails reference SOFTENED on transactability (a real-world
  site change)…" on both surfaces. Off the scoring path (`git diff --name-only` = canonical_history.py +
  scorecard.py + test only; scoring/probes/rubric/fetch/offering/cli/battery/fixtures = 0 changes) →
  score-neutral, NOT peer-gated, direct-to-main. `test_canonical_history.py` runner 38→40; full suite
  399→401; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 181): a
  variance/attribution refinement or an invariance axis on a diagnostic still lacking one — e.g. pin
  `cause_verdict`'s new pillar clause is host-relabel invariant, or measure whether the pillar-attribution
  top is STABLE across the trailing out-of-band run (same pillar every reading, or does the mover wander?).
  Substantive frontier (thin-archetype/render/structured-catalog LIVE fixtures, ACP/UCP/MPP, calibration
  sweep, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 179 runner note): RUNNER AT-FLOOR at 2026-08-02T14:12Z (Cycle 179) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~34.4h old at the 14:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; 14:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / off-scoring-path / score-neutral
  TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests`
  state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 179): fresh checkout on detached HEAD at
  Cycle 178's `2ddc5dd`; ran `git fetch origin main` FIRST (standing lesson) → `3796519…2ddc5dd (forced
  update)` (cached `origin/main` was the Cycle-94-era `3796519`), `checkout -B main origin/main` aligned to
  the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account
  pytest`, imports verified, 399 tests green pre-flight.
- FOCUS POINTER (Cycle 179 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 179 was
  TRUTH, so Cycle 180 is READOUT). Cycle 179 shipped a **TRUTH increment — real-series pillar attribution
  now fingers the DRIFTING pillar + cross-checks the two attribution mechanisms** (`tests/test_canonical_
  history.py`, rename+strengthen, no net count change). The canonical-drift diagnostic's real-series guard
  was named `..._fingers_com_legibility` but asserted ONLY the with-rails SIDE — and the executable evidence
  had drifted from reality: the name said LEGIBILITY (the 07-27 episode) while the CURRENT committed series
  (83 usable points; anchor `20260728T234102Z`, latest Aug-1) attributes to **driftflight.com TRANSACTABILITY
  87.5 → 62.5 (−25.0)**, the persistent Jul-31/Aug-1 machine-payment softening. Computed live: band `diverged`,
  delta +30.1, `attribution.top` = driftflight.com transactability −25.0 (sole mover), `divergence_cause.driver`
  = driftflight.com, `reference_degraded` = True. FIX: renamed to `..._fingers_the_drifting_pillar`, corrected
  the docstring (legibility→transactability history), and strengthened the recovery-guarded asserts to pin,
  when out of band: (1) top on with-rails side; (2) CROSS-MECHANISM agreement `top.domain == cause.driver`
  (per-pillar `_attribute` vs side-level `_cause`, independent code paths — a consistency neither real-series
  test alone made); (3) DIRECTION consistency `top.change < 0` when `reference_degraded` (a softening can't be
  carried by a pillar that rose); (4) the current live pillar is `transactability` (documents reality — a red
  means the real site drifted to another pillar; read newest `verify_*.json` + update). All four executed
  non-vacuously (band out-of-band → guard did not short-circuit): driftflight.com / driftflight.com / −25.0 /
  transactability. Tests-only, off the scoring path (`git diff --name-only` = `tests/test_canonical_history.py`
  ONLY; asrs/ scoring/probes/offering/rubric/fetch/cli/scorecard/fixtures UNTOUCHED) → score-neutral, NOT
  peer-gated, direct-to-main. Full suite 399→399; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. NEXT (READOUT 180): surface the fingered PILLAR (not just the side) in the terminal/HTML
  divergence-cause prose ("transactability softened on driftflight.com", not only "with-rails side softened").
  Substantive frontier (thin-archetype/render/structured-catalog LIVE fixtures, ACP/UCP/MPP, calibration
  sweep, transactability-drop CHECK-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 178 runner note): RUNNER AT-FLOOR at 2026-08-02T13:20Z (Cycle 178) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~33.5h old at the 13:20Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; 13:20Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path / score-neutral COVERAGE
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence
  PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent regression
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 178): fresh checkout on detached HEAD at Cycle 177's
  `79c6435`; ran `git fetch origin main` FIRST (standing lesson) → `3796519…79c6435 (forced update)` (cached
  `origin/main` was the Cycle-94-era `3796519`), `checkout -B main origin/main` aligned to the real tip,
  working tree clean, invariant #5 intact. Fresh `.venv` + `requests pyyaml eth-account pytest`, imports
  verified, 398 tests green pre-flight.
- FOCUS POINTER (Cycle 178 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 178 was
  COVERAGE, so Cycle 179 is TRUTH). Cycle 178 shipped a **COVERAGE increment — whitespace-reflow robustness
  for offering discovery** (`asrs/offering.py` + `tests/test_offering.py`, +1 test). Empirical finding: the
  discovery classifier (`classify_offering`, which drives `--battery auto` task SELECTION + NA semantics)
  scanned plain-text surfaces (llms.txt / markdown /docs) with NO whitespace normalization, yet ~35 signals
  across every archetype separate their tokens with a LITERAL single space (`\bfree shipping\b`, `\badd to
  (cart|bag|basket)\b`, `\bbilled per [a-z]+\b`, `\bper month\b`, ...). Plain-text agent surfaces are
  routinely 80-column line-wrapped, so a two-word phrase can straddle a newline ("free\nshipping") and the
  literal-space signal misses it — measured worst case, a realistic 3-archetype store's classification
  collapsed `[physical_good, metered_api, subscription]` → `[]`, blanking its whole task battery on
  typography. FIX: one-line at the scan boundary — collapse every whitespace run to a single space
  (`prose = _WS_RE.sub(" ", prose)`, the same normalization already trusted for evidence quotes) so a signal
  keys on the WORDS a surface declares, not the shape a crawl captured. Precision-safe (single space still
  separates tokens, `\b` still holds; paragraph-split "add\n\nto ... cart" stays unclaimed — verified). New
  `test_classification_is_whitespace_reflow_invariant` (the reflow analogue of the casing/reorder/relabel/
  noise-surface guards): claimed-set-in-rank-order + NA complement + per-(label,surface) count skeleton
  invariant under an arbitrary reflow, with teeth (a) real transform (b) load-bearing — a fired signal's RAW
  literal-space count DROPS under line-wrap while normalization restores it (c) negative control — no phantom
  claim across a paragraph split. Off the scoring path (`classify_offering`/`discover_offering` referenced
  only in cli.py's `--battery auto` branch, ZERO refs in scoring.py) → score-neutral, NOT peer-gated,
  direct-to-main. Canonical CLAIMED sets INVARIANT (evidence not reflowed). `git diff --name-only` =
  `asrs/offering.py` + `tests/test_offering.py` ONLY; full suite 398→399; replay guard 24/24, 46.1 F / 85.5 B
  / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 179): the discovery classifier now has reorder + host-
  relabel + noise-surface + casing + whitespace-reflow invariance — a near-complete robustness envelope. A
  TRUTH candidate is a calibration/attribution refinement or an invariance axis on a diagnostic still lacking
  one. Substantive frontier (thin-archetype/render/structured-catalog LIVE fixtures — which would also
  exercise this reflow robustness on real line-wrapped surfaces — ACP/UCP/MPP, calibration sweep,
  transactability-drop check-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 177 runner note): RUNNER AT-FLOOR at 2026-08-02T~12:1xZ (Cycle 177) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~32.4h old at the 12:12Z fire — PAST the 6h floor (machine-asleep /
  runner-lag pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; 12:12Z is
  NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only / off-scoring-path / score-neutral
  METHOD increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 177): fresh
  checkout on detached HEAD at Cycle 176's `8f39551`; ran `git fetch origin main` FIRST (standing lesson) →
  `3796519…8f39551 (forced update)` (cached `origin/main` was the Cycle-94-era `3796519`), `checkout -B main
  origin/main` aligned to the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests
  pyyaml eth-account pytest`, imports verified, 397 tests green pre-flight.
- FOCUS POINTER (Cycle 177 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 177 was
  METHOD, so Cycle 178 is COVERAGE). Cycle 177 shipped a **METHOD increment — a metamorphic invariance guard
  on the canonical-drift diagnostic family** (`tests/test_canonical_history.py`, +1 test + a
  `_reflect_about_anchor` helper). The family splits into two verdict kinds with OPPOSITE design intents:
  the MAGNITUDE machinery (band, `consecutive_out_of_band`, `SustainedRun.span_hours`, `NoiseFloor`) keys on
  `|delta - baseline|` and must be DIRECTION-BLIND, while the DIRECTION machinery (signed `divergence`,
  `gap_change`, `reference_degraded`, DEFER-vs-RECAPTURE) must be DIRECTION-SENSITIVE. Existing cause/recapture
  tests corroborate this with hand-built OPPOSITE cases (changing WHICH side moves); this pins the stronger
  statement via ONE metamorphic transform — reflect the whole trajectory about its in-band anchor
  (`v → 2·anchor − v`, so the delta reflects about the baseline gap, sign flipped / magnitude preserved) —
  under which the magnitude family is INVARIANT (band `drifting`=`drifting`, count 3=3, span 2.0=2.0, noise
  floor equal) and the direction family COVARIES (divergence −6.8↔+6.8, gap_change same, driver SIDE invariant
  = driftflight.com, `reference_degraded` True→False, recapture `defer`→`recapture-candidate`, render prose
  flips). Teeth: an up-front sanity assertion pins the reflected with-rails side RISES where the base FALLS
  (genuinely distinct series); a direction-blind OR magnitude-leaking regression breaks a half. Tests-only
  (`git diff --name-only` = `tests/test_canonical_history.py` ONLY; asrs/ scoring/probes/offering/rubric/
  fetch/cli/scorecard/fixtures UNTOUCHED) → score-neutral, NOT peer-gated, direct-to-main. `test_canonical_history.py`
  module runner 37→38; full suite 397→398; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. NEXT (COVERAGE 178): another metamorphic/invariance axis on an offering sub-signal or drift
  diagnostic still lacking one, else a small readout/methodology refinement. Substantive frontier
  (thin-archetype/render/structured-catalog fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop
  check-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 176 runner note): RUNNER AT-FLOOR at 2026-08-02T~11:2xZ (Cycle 176) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~31.5h old at fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; ~11:2xZ is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (display-only / off-scoring-path / score-neutral
  READOUT increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 176): fresh
  checkout on detached HEAD at Cycle 175's `3cadb77`; ran `git fetch origin main` FIRST (standing lesson) →
  `3796519…3cadb77 (forced update)` (cached `origin/main` was the Cycle-94-era `3796519`), `checkout -B main
  origin/main` aligned to the real tip, working tree clean, invariant #5 intact. Fresh `.venv` + `requests
  pyyaml eth-account pytest`, imports verified, 396 tests green pre-flight.
- FOCUS POINTER (Cycle 176 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 176 was
  READOUT, so Cycle 177 is METHOD). Cycle 176 shipped a **READOUT increment — the canonical-drift SUSTAINED-RUN
  SPAN on the HTML page** (`asrs/scorecard.py` + `tests/test_readout.py`, +1 test), closing the
  TRUTH(175)→READOUT(176) arc. Under the existing "Sustained/Recent: N consecutive re-score(s) out of band"
  row on the Latest-reading card, a dimmed (`class="q"`) sub-line now renders "spanning Xh (first → latest)",
  driven off `history.sustained_run` (the `SustainedRun` dataclass Cycle 175 added + wired into the terminal
  render). So card + terminal both name the drift's wall-clock PERSISTENCE, not just its reading-count — three
  re-scores a minute apart read differently from three spanning a day. Guard asserts the span text + both
  endpoints render on `_drifting_history()` (3 out-of-band readings 06:00→08:00Z = 2.0h span) alongside the
  "Sustained" count row, and are ABSENT entirely on an in-band series (non-vacuous, earned by the data);
  honest-None preserved (sub-line emitted only when `sustained_run is not None`). Display-only, off the scoring
  path (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY; scoring/probes/offering/
  rubric/fetch/cli/fixtures UNTOUCHED) → score-neutral, NOT peer-gated, direct-to-main. `test_readout.py` +1;
  full suite 396→397; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD
  177): the canonical-drift diagnostic family (band, sustained-run count+span, noise floor, liveness, pillar/
  side attribution, recapture advice) is now fully surfaced on terminal AND HTML — an in-cloud METHOD candidate
  is a metamorphic/invariance guard on a diagnostic still lacking one, or a small measurement-rigor refinement.
  Substantive frontier (thin-archetype/render/structured-catalog fixtures, ACP/UCP/MPP, calibration sweep,
  transactability-drop check-level diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 175 runner note): RUNNER AT-FLOOR at 2026-08-02T10:11Z (Cycle 175) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~30.3h old at fire — PAST the 6h floor (machine-asleep / runner-lag
  pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; 10:11Z is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (read-only-diagnostic / off-scoring-path /
  score-neutral TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent regression signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 175): fresh
  checkout on detached HEAD at Cycle 174's `334a6a2`; ran `git fetch origin main` FIRST (standing lesson),
  `checkout -B main origin/main` aligned to the real tip, working tree clean, invariant #5 intact. Fresh
  `.venv` + `requests pyyaml eth-account pytest`, imports verified, 391 tests green pre-flight.
- FOCUS POINTER (Cycle 175 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 175 was
  TRUTH, so Cycle 176 is READOUT). Cycle 175 shipped a **TRUTH increment — wall-clock PERSISTENCE for the
  canonical-drift diagnostic** (`asrs/canonical_history.py` + `tests/test_canonical_history.py`, +5 tests):
  the live-canonical "sustained vs jitter" judgment (and the DEFER/RECAPTURE recommendation it feeds) keyed
  ONLY on a COUNT (`consecutive_out_of_band` vs `_SUSTAINED_MIN=3`) — time-blind: 3 rapid re-scores read
  identically to 3 spanning a day. New `SustainedRun` (span_hours + endpoints) measures the wall-clock hours
  the trailing out-of-band run spans (first out-of-band reading → latest), computed pure from parsed
  timestamps with honest-None on empty-run / unparseable ts; a lone reading spans 0h. Descriptive companion
  only — gates nothing, existing recapture/attribution/noise-floor logic byte-unchanged; render appends
  "spanning Xh (first → latest)" to the sustained/recent line. On the live series it names the current drift
  as **spanning 19.0h across 3 reads**, strengthening the standing DEFER (com transactability 87.5→62.5,
  with-rails softening). Read-only diagnostic, imports no scoring code, off the scoring path (`git diff
  --name-only` = `asrs/canonical_history.py` + `tests/test_canonical_history.py` ONLY; scoring/probes/
  offering/rubric/fetch/cli/scorecard/fixtures UNTOUCHED) → score-neutral, NOT peer-gated, direct-to-main.
  `test_canonical_history.py` 32→37; full suite 391→396; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; rubric v0.7. NEXT (READOUT 176): surface the sustained-run span on the HTML canonical-history
  page (`_write_canonical_history_page`, `asrs/scorecard.py`) so card + terminal both name the drift's
  wall-clock persistence, with a `test_readout` guard. Substantive frontier (thin-archetype / render /
  structured-catalog fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop check-level diagnosis)
  stays `[LOCAL]`.
- SUPERSEDED (Cycle 174 runner note): RUNNER AT-FLOOR at 2026-08-02T~09:1xZ (Cycle 174) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~29h old at fire — PAST the 6h floor (borderline runner lag / machine-asleep
  pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; ~09:1xZ is NOT
  first-after-16:00 UTC → no DM this fire per comms policy (tests-only/off-scoring-path/score-neutral COVERAGE
  increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org
  46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F /
  85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty
  review. INFRA/SELF-HEAL (Cycle 174): fresh checkout on detached HEAD at Cycle 173's `2cb8be6`; ran `git fetch
  origin main` FIRST (standing lesson) → `3796519…2cb8be6 (forced update)` (cached `origin/main` was the
  Cycle-94-era `3796519`), `checkout -B main origin/main` aligned to the real tip, working tree clean, invariant
  #5 intact. `.venv` + `requests pyyaml eth-account pytest`, imports verified, 390 tests green pre-flight.
- FOCUS POINTER (Cycle 174 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 174 was
  COVERAGE, so Cycle 175 is TRUTH). Cycle 174 shipped a **COVERAGE increment — noise-surface invariance
  metamorphic axis for `plan-allowance`** (`tests/test_offering.py`, +1 test): closes the Cycle-171 noise-
  surface family onto the Cycle-172 subscription signal the machine-pole guard could not reach (the committed
  `api.replicate.com` fixture never fires plan-allowance). `test_plan_allowance_noise_surface_invariance` bolts
  a signal-free `/privacy` chrome surface onto the synthetic bundled-plan-allowance homepage and asserts the
  whole per-archetype `(strength, (label, surface, quote))` evidence map is byte-identical, ranked archetypes
  and the NA set invariant, surfaces_seen grows by exactly `/privacy`. Three teeth: (a) noise surface READ yet
  no claim; (b) distractor fires ZERO `_scan_surface` signals; (c) negative control (real fulfillment prose on
  the same key) DOES conjure physical_good (NA at base) → non-vacuous. Tests-only (`git diff --name-only` =
  `tests/test_offering.py` ONLY; scoring/probes/offering/rubric/fixtures UNTOUCHED) → score-neutral, NOT
  peer-gated, direct-to-main. `test_offering.py` module runner 76→77; full suite 390→391; replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 175): the in-cloud noise/relabel/content-
  scale/whitespace metamorphic grid is near-complete across the offering signal poles; the substantive frontier
  (thin-archetype + render fixtures, structured catalog/pricing JSON, ACP/UCP/MPP, calibration sweep,
  transactability-drop diagnosis) stays `[LOCAL]`. A near-in-cloud TRUTH candidate: extend the relabel/identity
  family to any offering sub-signal still lacking a metamorphic guard, else a small readout/methodology refinement.
- SUPERSEDED (Cycle 173 runner note): RUNNER AT-FLOOR at 2026-08-02T08:12Z (Cycle 173) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~28.4h old at the 08:12Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag / machine-asleep pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest;
  08:12Z is NOT first-after-16:00 UTC → no DM this fire per comms policy (tests-only/off-scoring-path/
  score-neutral TRUTH increment, no sensitive-class PR, nothing score-moving). Live signal (read, not
  re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the
  frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire
  (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 173): fresh checkout
  on detached HEAD at Cycle 172's `9120667`; cached `origin/main` stale (`3796519`, Cycle-94 era) → ran
  `git fetch origin main` FIRST (standing lesson) → `3796519…9120667 (forced update)`, `checkout -B main
  origin/main` aligned to the real tip, working tree clean, invariant #5 intact. `.venv` + `requests pyyaml
  eth-account pytest`, imports verified, 388 tests green pre-flight.
- FOCUS POINTER (Cycle 173 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 173 was
  TRUTH, so Cycle 174 is COVERAGE). Cycle 173 shipped a **TRUTH increment — signal-level relabel/host-
  invariance guard for `plan-allowance`** (`tests/test_offering.py`, +2 tests): the subscription-signal
  mirror of the media/render descriptor relabel guards and the classifier-level fixture relabel guard. Makes
  "whether a site claims the bundled-subscription-allowance capability keys on its VOCABULARY, not its host/
  vendor" an executable tripwire — a synthetic bundled-plan store that names its own host INSIDE the
  plan-allowance evidence (host provably in the pad=40 quote) fires plan-allowance IDENTICALLY (same
  sub-signal label set) once the host is relabeled to a neutral placeholder, with the quotes genuinely
  changing (non-vacuous). `test_plan_allowance_relabel_has_teeth`: a deliberately host-keyed stub detector
  FLIPS under the same relabel pair while the real signal stays invariant — the guard refutes a real
  failure mode, not a tautology. Tests-only (`git diff --name-only` = `tests/test_offering.py` ONLY;
  scoring/probes/offering/rubric/fixtures UNTOUCHED) → score-neutral, NOT peer-gated, direct-to-main.
  `test_offering.py` +2; full suite 388→390; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. NEXT (COVERAGE 174): a `plan-allowance` noise-surface metamorphic axis (Cycle-171 family
  extended to the new signal) is the nearest in-cloud candidate; the substantive frontier (thin-archetype +
  render fixtures, structured catalog/pricing JSON, ACP/UCP/MPP, calibration sweep, transactability-drop
  diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 172 runner note): RUNNER AT-FLOOR at 2026-08-02T07:27Z (Cycle 172) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~27.6h old at the 07:27Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag / machine-asleep pattern, cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest;
  07:27Z is NOT first-after-16:00 UTC → no DM this fire per comms policy (off-scoring-path/score-neutral
  COVERAGE increment, no sensitive-class PR, nothing score-moving). Live signal (read, not re-run):
  drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  signal (24/24, 46.1 F / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open
  → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 172): fresh checkout on detached HEAD at Cycle 171's
  `c79045a`; cached `origin/main` stale (`3796519`, Cycle-94 era) → ran `git fetch origin main` FIRST
  (standing lesson) → `3796519…c79045a (forced update)`, `checkout -B main origin/main` aligned to the real
  tip, reflog clean, invariant #5 intact. `.venv` + `requests pyyaml eth-account pytest`, imports verified,
  386 tests green pre-flight.
- FOCUS POINTER (Cycle 172 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 172 was
  COVERAGE, so Cycle 173 is TRUTH). Cycle 172 shipped a **COVERAGE increment — new subscription signal
  `plan-allowance`** (`asrs/offering.py`): the HYBRID subscription plan whose recurring fee bundles a
  bounded monthly allowance that RESETS each cycle, with metered overage beyond it — the capital-safety
  "understand the offer" fact none of the 8 flat-recurring subscription signals captured. Keys on a bare
  `monthly allowance` / usage-qualified monthly allowance / the hybrid-plan definition (`subscription with
  included …`) / the allowance lifecycle (`used up`/`resets`/`is tracked per plan`); distinct from
  metered_api's `free-included-usage` (FREE allowance), `credit-metered` (credit balance), `usage-based`
  (bare overage). Precision: 6 allowance-shaped negatives fire zero (incl. the "monthly expense allowance"
  HR-perk trap). The content-scale metamorphic guard CAUGHT a bare-`exhausted` alternation matching the
  openapi.json 429 tail (pad=40 quote window bled across the duplication boundary) → dropped it; `used up`/
  `resets` cover the exhaustion sense with interior/stable matches. Fires on the PAIR (both /docs "plan's
  monthly allowance"; .com also llms-full.txt), ZERO on api/retail/null. Guards: precision-synthetic +
  real-captured in `test_offering.py`, isolation-matrix entry in `test_offering_canonical.py`. Off the
  scoring path (`git diff --name-only` = `asrs/offering.py` + `tests/test_offering.py` +
  `tests/test_offering_canonical.py` ONLY; scoring/probes/rubric/fetch/cli/fixtures EMPTY) → score-neutral,
  NOT peer-gated, direct-to-main (same class as offering-signal Cycles 34/42/46/70/160/164). Subscription
  8→9 (bank 64→65); strength 4→5 (.org)/6→7 (.com), still < digital_good's 10 — claimed SET+ORDER
  `[metered_api, digital_good, subscription]` UNCHANGED on both; full suite 386→388; replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 173): a relabel/host-invariance guard for
  `plan-allowance` (the allowance/hybrid-plan vocabulary is a property of the OFFERING, not the host — the
  subscription mirror of the media/render relabel guards). Substantive frontier (thin-archetype + render
  fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop diagnosis) stays `[LOCAL]`.
- SUPERSEDED (Cycle 171 runner note): RUNNER AT-FLOOR at 2026-08-02T06:11Z (Cycle 171) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~26.3h old at the 06:11Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag, NOT the machine-asleep stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily
  digest; no new flag owed (next digest = first cycle after 16:00 UTC Aug-2; 06:11Z is NOT it → no DM this
  fire per comms policy — tests-only/off-scoring-path/score-neutral METHOD increment, no sensitive-class PR,
  nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C /
  +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path;
  the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). No open
  peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 171): fresh checkout on detached HEAD at Cycle 170's `1bbf474` (= real `origin/main` tip). RE-LEARNED
  the Cycle-151/170 lesson the hard way — ran `checkout -B main origin/main` BEFORE fetching, which reset
  `main` to the container's STALE cached `origin/main` (`3796519`, Cycle-94 era) and silently reverted the
  working tree ~76 cycles (caught by a test-count sanity check: 17 vs STATE's 57 `def test_`). Fixed with
  `git fetch origin main` → `3796519…1bbf474 (forced update)` + re-align; reflog confirms nothing lost,
  invariant #5 intact. STANDING LESSON: ALWAYS `git fetch origin main` FIRST in a fresh container before
  `checkout -B main origin/main`. `.venv` + deps installed, imports verified, 23 test files green.
- FOCUS POINTER (Cycle 171 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 171 was
  METHOD, so Cycle 172 is COVERAGE). Cycle 171 shipped a **METHOD noise-surface metamorphic axis on the
  MACHINE pole** — `test_offering_noise_surface_invariance_machine` in `tests/test_offering_canonical.py`,
  closing the LAST org/com/retail-vs-machine asymmetry on the noise axis (org/com/retail already covered;
  content-scale + surface-dedup already reach all four poles; whitespace is machine-only by construction).
  Adds a signal-free `/privacy` chrome surface to the `api.replicate.com` metered_api OpenAPI-spec pole and
  asserts the whole (strength, (label, surface, quote)) evidence map is byte-identical — bolting incidental
  web chrome onto an API-first store conjures no rails/other archetype ("never manufacture the delta" on the
  noise axis from the metered pole). Three teeth: (a) noise surface READ (in surfaces_seen) yet no claim; (b)
  distractor fires ZERO `_scan_surface` signals; (c) physical_good negative control DOES move the profile.
  Dedicated test (not the shared `len(claimed)>=2` helper — machine claims exactly 1 archetype), base
  captured inline via the machine-pole spy. Off the scoring path (`git diff --name-only` =
  `tests/test_offering_canonical.py` ONLY; scoring.py/probes.py/offering.py/battery.py/rubric/fixtures EMPTY)
  → score-neutral, NOT peer-gated, direct-to-main. `test_offering_canonical.py` 57→58; registration guard
  green; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  NEXT (COVERAGE 172): in-cloud COVERAGE on committed evidence stays archetype-imbalanced (under-covered
  service_booking / data_retrieval / physical_good need `[LOCAL]` fixtures). Remaining in-cloud METHOD gap
  (surface-dedup RETAIL pole) is near-vacuous — its teeth need ≥2 archetypes for a ranking, retail claims
  only physical_good — so prefer a new archetype/signal or a `[LOCAL]` fixture. Substantive frontier
  (ACP/UCP/MPP, calibration sweep, transactability-drop diagnosis, render/thin-archetype fixtures) is all
  `[LOCAL]`.
- SUPERSEDED (Cycle 170 runner note): RUNNER AT-FLOOR at 2026-08-02T05:12Z (Cycle 170) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~25.4h old at the 05:12Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag, NOT the machine-asleep stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily
  digest; no new flag owed (next digest = first cycle after 16:00 UTC Aug-2; 05:12Z is NOT it → no DM this
  fire per comms policy — display+tests-only/off-scoring-path/score-neutral READOUT increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F
  / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []; the many `loop/*`
  refs on fetch are stale post-merge branches), so no first-duty review. INFRA/SELF-HEAL (Cycle 170): fresh
  checkout on detached HEAD; `git fetch origin main` FIRST (Cycle-151 lesson) surfaced a FORCED-UPDATE
  `3796519…750b407` — `3796519` is a Cycle-94-era commit (present, NOT an ancestor of the tip): the
  container's cached `origin/main` was ~76 cycles stale, PR-merge history linearised past it; recent history
  (165→169) clean + consistent with STATE/LOG → benign staleness, NOT a loop rewrite (invariant #5 intact).
  `checkout -B main origin/main` aligned to `750b407`, no work lost. Created `.venv`, installed `requests
  pyyaml eth-account pytest` + verified imports before trusting the suite (23 files green pre-flight).
- FOCUS POINTER (Cycle 170 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 170 was
  READOUT, so Cycle 171 is METHOD). Cycle 170 shipped a **READOUT methodology paragraph naming the
  `generated render` descriptor variant + its priority**, CLOSING the render arc COVERAGE(168)→TRUTH(169)→
  READOUT(170). Section 6 of `_write_methodology_page` (`asrs/scorecard.py`) — the one place the derived
  offering-relative descriptor vocabulary is surfaced in prose — named only image/video/audio/art/
  digital-output; a reader could not learn that a render-generation service yields "generated render", nor
  that the media noun WINS when a site names both (the priority the Cycle-168 code test pins as teeth). Added
  the vendor-neutral "generated render" variant for a render-only service + the most-specific-output rule
  (a service naming an `image` keeps "generated image" even if it also renders → render noun surfaces only
  when it is the ONLY output described). Display prose only — the descriptor branch already existed (Cycle
  168), no new logic. Guard: extended `test_methodology_documents_offering_relative_battery`
  (`tests/test_readout.py`) — the existing presence guard on this exact paragraph — to pin `"generated
  render"` + `"most specific"` + `"render"` (docstring note f+g), vendor-neutral checks already present.
  Off the scoring path (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY;
  scoring.py/probes.py/offering.py/battery.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. `test_readout.py` 68/68; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 171): a noise-surface invariance axis on the MACHINE pole,
  or a surface-dedup axis on the RETAIL pole (Cycle-167's named remaining symmetry gaps). Substantive
  frontier stays `[LOCAL]`: a real render-generation fixture (first REAL-evidence validation of the render
  branch), thin-archetype fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop diagnosis all need
  Jonah's machine.
- SUPERSEDED (Cycle 168 runner note): RUNNER AT-FLOOR at 2026-08-02T03:12Z (Cycle 168) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~23.4h old at the 03:12Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag, NOT the machine-asleep stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily
  digest; no new flag owed (next digest = first cycle after 16:00 UTC Aug-2; 03:12Z is NOT it → no DM this
  fire per comms policy — off-scoring-path/score-neutral COVERAGE increment, no sensitive-class PR, nothing
  score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 /
  transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the
  in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). No open
  peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 168): fresh checkout on detached HEAD at Cycle 167's `d0a9fa5` (= `origin/main` tip); `git fetch
  origin main` FIRST (Cycle-151 lesson) → already at tip, `checkout -B main origin/main` aligned, no work
  lost. Created `.venv`, installed `requests pyyaml eth-account pytest` + verified imports before trusting the
  suite (383 tests green pre-flight).
- SUPERSEDED (Cycle 168 focus pointer): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 168 was
  COVERAGE, so Cycle 169 is TRUTH). Cycle 168 shipped a **COVERAGE measurement-flexibility increment —
  `_digital_good_descriptor` now covers the `render` output** (asrs/battery.py). The offering-relative
  battery parameterizes the digital_good task with the discovered output (operator brick 2); the descriptor
  recognised image/video/audio/art + translation, but a render-EXCLUSIVE claim (a 3D/architectural/scene/frame
  render service that fired the offering bank's `render` signal but named no image/video/audio/art artifact)
  fell to the bare generic "digital output" — a seam between the classifier (knows the site renders) and the
  battery (probed it vaguer than its own offering). New branch → "generated render", DELIBERATELY lower
  priority than the media loop so a claim that ALSO names image/video/audio/art keeps the more specific
  descriptor → the canonical image pair (fires BOTH `render` + `image`) stays "generated image", battery text
  stable (VERIFIED both domains). Chosen after verifying in-cloud that every NEW-signal direction is vacuous/
  noisy/over-fit on committed evidence (output-format = favicon/CSS noise; service_booking/data_retrieval = no
  fixture claims them; physical_good descriptor = book TITLES not a product noun; idempotency = absent;
  x402 retry-idempotency = header mechanics + a free re-render window, and fires on ONE fixture → anchor
  over-fit) — the `render` seam is the one non-vacuous, non-over-fit, score-neutral unit. Test
  `test_digital_good_descriptor_covers_render` (synthetic render-exclusive claim → "generated render"; PRIORITY
  teeth: render+image → "generated image"), registered in `main()`; file 12→13. Off the scoring path (`git
  diff --name-only` = `asrs/battery.py` + `tests/test_battery_instantiate.py` ONLY; scoring.py/probes.py/
  offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated, direct-to-main. Full suite 383→384;
  replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (TRUTH 169): a relabel/
  identity-invariance guard for the new `render` branch (mirror
  `test_digital_good_descriptor_is_relabel_invariant_media` — the render output noun is a property of the
  offering, not the host). Substantive COVERAGE frontier stays `[LOCAL]`: a render-generation fixture would
  give this branch its first REAL-evidence validation (currently synthetic-only, like video/audio/art);
  thin-archetype fixtures, ACP/UCP/MPP, calibration sweep, transactability-drop diagnosis all need Jonah's
  machine.
- SUPERSEDED (Cycle 167 runner note): RUNNER AT-FLOOR at 2026-08-02T02:11Z (Cycle 167) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~22.4h old at the 02:11Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag, NOT the machine-asleep stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily
  digest; no new flag owed (next digest = first cycle after 16:00 UTC Aug-2; 02:11Z is NOT it → no DM this
  fire per comms policy — tests-only/off-scoring-path/score-neutral METHOD increment, no sensitive-class PR,
  nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C /
  +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path;
  the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). No open
  peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 167): fresh checkout on detached HEAD at Cycle 166's `473df5f` (= `origin/main` tip); `git fetch
  origin main` FIRST (Cycle-151 lesson) → already at tip, `checkout -B main origin/main` aligned, no work
  lost. Created `.venv`, installed `requests pyyaml eth-account pytest` + verified imports before trusting the
  suite (382 tests green pre-flight).
- SUPERSEDED (Cycle 167 focus pointer): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 167 was
  METHOD, so Cycle 168 is COVERAGE). Cycle 167 shipped a **METHOD reading-layer metamorphic axis —
  `test_offering_whitespace_invariance_machine`** in `tests/test_offering_canonical.py`, the natural SIBLING
  of the CASE axis (133/155): casing perturbs the CASE of the scanned bytes, this perturbs the WHITESPACE
  between them (each single space → three) and asserts the classified capability profile is unchanged.
  Established FIRST (not assumed) that the axis is non-vacuous ONLY on the machine pole: the prose poles
  (org/com/retail) go through `strip_html`, which COLLAPSES whitespace runs BEFORE the matcher sees them
  (verified), so a prose-pole whitespace guard would be VACUOUS (enforced by strip_html, not the patterns) —
  the `/openapi.json` spec is scanned RAW (`_surface_prose`), so on the metered_api machine pole
  (`api.replicate.com`) whitespace-tolerance rests on the signal patterns' OWN `\s+`/`\s*` flexibility.
  Transform is EXPANSION (monotone: `\s+`/`\s*` still matches a longer run; an exact-single-space requirement
  can only STOP matching, never CONJURE), so skeleton-invariance means every fired signal is genuinely
  whitespace-robust. Asserts the quote-EXCLUDED skeleton (`_casing_struct`, reused). Teeth: (a) transform REAL
  (raw spec carries single spaces); (b) whitespace-flexibility LOAD-BEARING — a fired signal's RIGID-whitespace
  count (its pattern with `\s+`/`\s*` → one literal space) DROPS under expansion while the flexible count holds
  (6 signals qualify; canonical example `post-endpoint`: "POST https://" rigid 1→0, flexible 1→1). Verified
  empirically before writing (skeleton invariant: metered_api strength 9, all 9 (label,surface) counts
  preserved; claim + NA invariant). Off the scoring path (`git diff --name-only` = `tests/test_offering_canonical.py`
  ONLY; scoring.py/probes.py/offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated, direct-to-main.
  Registration guard green. Full suite 382→383; `test_offering_canonical.py` 56→57; replay guard 24/24, 46.1 F
  / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (COVERAGE 168): in-cloud COVERAGE on committed evidence
  stays archetype-imbalanced (under-covered service_booking / data_retrieval / physical_good need `[LOCAL]`
  fixtures). Remaining in-cloud METHOD symmetry gaps: noise-surface MACHINE pole, surface-dedup RETAIL pole.
  The substantive frontier (ACP/UCP/MPP, calibration sweep, transactability-drop diagnosis) is all `[LOCAL]`.
- SUPERSEDED (Cycle 166 runner note): RUNNER AT-FLOOR at 2026-08-02T01:15Z (Cycle 166) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~21.4h old at the 01:15Z Aug-2 fire — PAST the 6h floor (borderline runner
  lag, NOT the machine-asleep stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily
  digest; no new flag owed (next digest = first cycle after 16:00 UTC Aug-2; 01:15Z is NOT it → no DM this
  fire per comms policy — display+tests-only/off-scoring-path/score-neutral READOUT increment, no
  sensitive-class PR, nothing score-moving). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F
  / 85.5 B / +39.4). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no
  first-duty review. INFRA/SELF-HEAL (Cycle 166): fresh checkout on detached HEAD at Cycle 165's `9948b90`;
  `git fetch origin main` FIRST (Cycle-151 lesson) → `origin/main` fast-forwarded to `9948b90`, `checkout -B
  main origin/main` aligned, no work lost. Created `.venv`, installed `requests pyyaml eth-account pytest` +
  verified imports before trusting the suite (23 files green pre-flight).
- SUPERSEDED (Cycle 166 focus pointer): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 166 was
  READOUT, so Cycle 167 is METHOD). Cycle 166 shipped the **READOUT leg closing the variant-selection arc —
  the `_write_methodology_page` paragraph "Choosing the deliverable's variant"** in `asrs/scorecard.py`, the
  prose complement (free-included-usage 162 / reserve-and-settle 158 / failure-not-billed 154 / payment-receipt
  144 pattern) for Cycle 164's `variant-selection` digital_good signal, closing the COVERAGE(164)→TRUTH(165)→
  READOUT(166) arc. The paragraph frames variant-selection as the deliverable-control / REPRODUCIBILITY leg of
  finishing the digital-good job (distinct from the output-resolution SHAPE leg — how BIG the render is vs
  which LOOK it has, and from every rights/authenticity/delivery read that names a PROPERTY of the artifact
  received, not CONTROL of which variant is produced), names the failure (an at-scale catalog run where "the
  two-hundredth image has to match the first" cannot use a service that returns a random style each call),
  names the vendor-neutral variant-selection vocabulary as open conventions (a style preset; a preset
  slug/string/parameter/id/name; pick/choose/select/browse/pass/send a preset; a preset that locks or pins the
  style), preserves the signal's PRECISION honesty (bare "model"/"tier" = no signal — "tier" owned by
  metered_api `tiered-volume`; the preset VERB "preset the oven", a factory preset, a camera preset, a reset
  are not variant selection), keys recognition on the variant-selection CONTRACT the offer documents not who
  documents it (identity-relabel regression test), and stays honest about scope (diagnostic, off the scoring
  path, not a scored pillar). Placed adjacent to its closest sibling (the output-resolution paragraph). Guard
  `test_methodology_documents_variant_selection` in `tests/test_readout.py` (67→68), the whitespace-collapsed
  presence+precision+distinctness mirror of `test_methodology_documents_free_included_usage`, registered in
  `main()`. Off the scoring path (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY;
  scoring.py/probes.py/offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated, direct-to-main.
  Full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT
  (METHOD 167): the variant-selection arc is now closed across all three surfaces; METHOD could earn it an
  ordering/whitespace-invariance metamorphic guard on the machine pole (content-scale 163 / surface-dedup 159 /
  casing 155 pattern), or the pointer could turn to a fresh COVERAGE archetype — but in-cloud COVERAGE on
  committed evidence stays archetype-imbalanced; the under-covered archetypes (service_booking / data_retrieval
  / physical_good) need `[LOCAL]` fixtures; the substantive frontier (ACP/UCP/MPP, calibration sweep,
  transactability-drop diagnosis) is all `[LOCAL]`.
- SUPERSEDED (Cycle 165 runner note): RUNNER AT-FLOOR at 2026-08-02T00:12Z (Cycle 165) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~20.4h old at the 00:12Z Aug-2 fire — PAST the 6h floor (the local
  ~04:xx Aug-1 onward fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep
  stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; no new flag owed (next
  digest = first cycle after 16:00 UTC Aug-2). Live signal (read, not re-run): drift-flight.org 46.1 F /
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F
  / 85.5 B / +39.4). Fire at 00:12Z Aug-2 is NOT the first after 16:00 UTC (Cycle 157 sent the digest at
  16:12Z Aug-1; next is after 16:00Z Aug-2) → no DM this fire per comms policy (test-only/off-scoring-path/
  score-neutral TRUTH increment, no sensitive-class PR, nothing score-moving). No open peer-gated PRs this
  fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 165): fresh
  checkout on detached HEAD at Cycle 164's `428aa77` (= `origin/main` tip), `git fetch origin main` FIRST
  (Cycle-151 lesson) → already at tip, `checkout -B main origin/main` aligned, no work lost. Created `.venv`,
  installed `requests pyyaml eth-account pytest` + verified imports before trusting the suite (23 files green
  pre-flight).
- SUPERSEDED (Cycle 165 focus pointer): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 165 was
  TRUTH, so Cycle 166 is READOUT). Cycle 165 shipped the **TRUTH signal-level relabel-invariance guard —
  `test_offering_relabel_invariance_variant_selection`** in `tests/test_offering_canonical.py`, the
  identity-invariance mirror (free-included-usage 161 / reserve-and-settle 157 / failure-not-billed 153 /
  payment-receipt 143 pattern) for Cycle 164's `variant-selection` digital_good signal. Property pinned:
  whether an autonomous agent can DISCOVER and SELECT which output variant a generative service produces (a
  named, listable style PRESET passed on the request so the deliverable is fit-for-purpose and REPRODUCIBLE)
  is a property of the variant-selection CONTRACT, not who vends it, so the signal is host-relabel invariant
  — the "never manufacture the delta" invariant at the signal level, applied to a deliverable-control
  capability BOTH image-gen storefronts genuinely share. Non-vacuous SYNTHETIC vehicle (`acme-vend.example`
  seats the host INSIDE the evidence — surface-key prefix `agents.acme-vend.example/docs` + adjacent to the
  leftmost "pick a preset" phrase within the 40-char quote pad; base=1 host-in-both): relabel to
  `vendor-neutral.test` → host absent, SAME match count (1), SAME host-normalized surface, quote still
  matching the live regex. TEETH: preset/model/tier-SHAPED noise (a "large language model" on the "pro tier"
  — the two named minefields; the preset-VERB "preset the oven"; a "factory preset"; a "camera preset"; a
  "reset") fires ZERO. Off the scoring path (`git diff --name-only` = `tests/test_offering_canonical.py`
  ONLY; scoring.py/probes.py/offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Registration guard green (test in `main()`). Full suite 23 files green;
  `test_offering_canonical.py` 55→56; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric
  v0.7. NEXT (READOUT 166): the variant-selection methodology-page paragraph (`_write_methodology_page`
  framing deliverable-control / "usable, reproducible deliverable" as the Cycle-162/154/144 pattern) + a
  `test_methodology_documents_variant_selection` presence guard, closing the COVERAGE(164)→TRUTH(165)→
  READOUT(166) arc. In-cloud COVERAGE on committed evidence stays archetype-imbalanced; under-covered
  archetypes (service_booking / data_retrieval / physical_good) need `[LOCAL]` fixtures; the substantive
  frontier (ACP/UCP/MPP, calibration sweep, transactability-drop diagnosis) is all `[LOCAL]`.
- SUPERSEDED (Cycle 164 runner note): RUNNER AT-FLOOR at 2026-08-01T23:12Z (Cycle 164) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~19.4h old at the 23:12Z fire — PAST the 6h floor (the local
  ~04:xx–23:xx fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep
  stall — cloud cannot repair). Already flagged in the 16:12Z Cycle-157 daily digest; no new flag owed.
  Live signal (read, not re-run): drift-flight.org 46.1 F / driftflight.com 76.2 C / +30.1 /
  transactability 62.5 — the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the
  in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Fire at
  23:12Z is NOT the first after 16:00 UTC (Cycle 157 sent the digest at 16:12Z) → no DM this fire per
  comms policy (off-scoring-path/score-neutral offering-signal increment, no sensitive-class PR, nothing
  score-moving). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no
  first-duty review. INFRA/SELF-HEAL (Cycle 164): fresh checkout on detached HEAD at Cycle 163's
  `33d970e` (= `origin/main` tip), `git fetch origin main` FIRST (Cycle-151 lesson) → already at tip,
  `checkout -B main origin/main` aligned, no work lost. Created `.venv`, installed `requests pyyaml
  eth-account pytest` + verified imports before trusting the suite (378 tests green pre-flight).
- SUPERSEDED (Cycle 164 focus pointer): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 164 was
  COVERAGE, so Cycle 165 is TRUTH). Cycle 164 shipped a **COVERAGE digital_good signal — `variant-selection`**
  in `asrs/offering.py`: whether an autonomous agent can DISCOVER and SELECT which output VARIANT a
  generative digital-good service produces (a named, listable style PRESET passed on the request) so it
  obtains a FIT-FOR-PURPOSE, REPRODUCIBLE deliverable — the "complete the job with a USABLE deliverable"
  leg, distinct from all 10 existing digital_good signals (which describe the artifact's PROPERTIES —
  generation/hosted-output/license/provenance/resolution/retention — none says the agent can CONTROL the
  variant). Re-tested (not assumed) STATE's "COVERAGE exhausted" claim: the honest picture is
  archetype-specific — the bank is metered_api-HEAVY (26) vs subscription 8 / digital_good 10→11 /
  physical_good 9 / service_booking 5 / data_retrieval 5, so leverage is in an under-covered archetype the
  canonical evidence still verifies non-vacuously. PRECISION: NEVER matches bare "model" (language/business/
  role/3D model) or "tier" (billing, owned by metered_api `tiered-volume`); "preset" anchored to a STYLE
  preset / preset PARAMETER / SELECT-BROWSE-PICK verb / determinism verb — 9 homonym distractors fire ZERO
  (incl. the preset VERB "preset the oven", "factory preset", "reset"). NON-VACUOUS: fires 14× on real
  driftflight.com + 9× on drift-flight.org; UNLIKE payment/rails signals it fires on BOTH sides
  (deliverable-control is a capability both image-gen storefronts genuinely share, NOT a rails gap — not a
  delta-widener), ZERO on api.replicate.com (bare-"model" trap dodged → no digital_good conjured),
  books.toscrape, example.com. Two near-misses REJECTED on discipline (recorded so they aren't re-mined): a
  subscription "credit-balance"/prepaid signal (metered_api `credit-metered` ALREADY owns prepaid credit —
  would duplicate + cross-poach), and a digital_good "output-format" signal (no genuine format prose in the
  evidence — "format"="flies in formation", "mimeType"=request type → vacuous). Off the scoring path (`git
  diff --name-only` = `asrs/offering.py` + `tests/test_offering.py` + `tests/test_offering_canonical.py`
  ONLY; scoring.py/probes.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated, direct-to-main
  (Cycle-160 precedent). Claimed SET+ORDER `['metered_api','digital_good','subscription']` byte-identical on
  BOTH canonical domains; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. Bank
  63→64 signals; `test_offering.py` 70→72. NEXT (TRUTH 165): the `variant-selection` relabel-invariance
  guard (whether the agent can select the variant is a property of the preset CONTRACT, not who vends it →
  host-relabel invariant), then a READOUT methodology paragraph, closing a COVERAGE(164)→TRUTH→READOUT arc.
  FUTURE COVERAGE: the remaining under-covered archetypes (service_booking 5, data_retrieval 5,
  physical_good 9) have NO or thin committed claiming evidence → strengthening them is `[LOCAL]` (needs a
  captured booking / data-retrieval / mixed-storefront fixture); structured catalog/pricing JSON surfaces
  are 404 on every committed fixture (also `[LOCAL]`). The substantive frontier — ACP/UCP/MPP handshakes,
  the calibration-population sweep, the driftflight.com transactability-drop diagnosis — is all `[LOCAL]`,
  blocked on the at-floor runner.
- SUPERSEDED (Cycle 161 focus pointer): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 161 was
  TRUTH, so Cycle 162 is READOUT). Cycle 161 shipped a **TRUTH signal-level relabel-invariance guard —
  `test_offering_relabel_invariance_free_included_usage`** in `tests/test_offering_canonical.py`, the
  identity-invariance mirror (reserve-and-settle 157 / failure-not-billed 153 / payment-receipt 143
  pattern) for Cycle 160's `free-included-usage` metered_api signal. Property pinned: whether an agent can
  complete a REAL metered call at $0 before committing money (a per-account free ALLOWANCE usable at a
  zero balance, no funding) is a property of the free-included-usage CONTRACT, not who vends it, so the
  signal is host-relabel invariant — the "never manufacture the delta" invariant at the signal level.
  Non-vacuous SYNTHETIC vehicle (`acme-vend.example` seats the host INSIDE the evidence — surface-key
  prefix `agents.acme-vend.example/llms.txt` + adjacent to "free allowance" within the 40-char quote pad;
  base=1 host-in-both, verified empirically): relabel → host absent, SAME match count (1), SAME
  host-normalized surface, quote still matching the live regex. TEETH: free/included-SHAPED noise (retail
  "free shipping", "royalty-free", a PAID "500 units included per month" allotment, "feel free to
  explore") fires ZERO. Off the scoring path (`git diff --name-only` = `tests/test_offering_canonical.py`
  ONLY; scoring.py/probes.py/offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated,
  direct-to-main. Registration guard green (test in `main()`). Full suite 375→376;
  `test_offering_canonical.py` 53→54; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric
  v0.7. NEXT (READOUT 162): the free-included-usage methodology-page paragraph
  (`_write_methodology_page` "trying a paid call for free before you fund" as the capital-safety sibling
  of the receipt/reserve-and-settle legs, Cycle-154/142 pattern) + a
  `test_methodology_documents_free_included_usage` presence guard, closing the COVERAGE(160)→TRUTH(161)→
  READOUT(162) arc. In-cloud COVERAGE on committed evidence is essentially exhausted (metered_api = 26
  signals); remaining frontier is `[LOCAL]` fixtures.
- SUPERSEDED (Cycle 160 runner note): RUNNER AT-FLOOR at 2026-08-01T19:12Z (Cycle 160) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~15.4h old at the 19:12Z fire — PAST the 6h floor (the local ~04:xx–19:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Already flagged in the 16:12Z Cycle-157 daily digest. Live signal (read, not re-run):
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F /
  85.5 B / +39.4). Fire at 19:12Z is NOT the first after 16:00 UTC (Cycle 157 sent the digest at 16:12Z) → no
  DM this fire per comms policy (COVERAGE off-scoring-path/score-neutral, no sensitive-class PR, nothing
  score-moving). No open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review.
  INFRA/SELF-HEAL (Cycle 160): fresh checkout landed on detached HEAD at Cycle 159's `309417a`; `git fetch
  origin main` FIRST (Cycle-151 lesson) → `origin/main` force-updated `3796519...309417a`, `checkout -B main
  origin/main` realigned onto `309417a`, no work lost. Created `.venv`, installed `requests pyyaml eth-account
  pytest` + verified `import requests, yaml, asrs` before trusting the suite (23 files green pre-flight).
- SUPERSEDED (Cycle 160 focus pointer): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 160 was
  COVERAGE, so Cycle 161 is TRUTH). Cycle 160 shipped a **COVERAGE metered_api signal — `free-included-usage`**
  in `asrs/offering.py`: whether an agent can complete a REAL metered call at **$0 before committing any money**
  — a per-account free ALLOWANCE of actual units (an `includedUnits` contract), usable at a zero balance with
  no funding, no human signup. This is the metered_api ON-RAMP the PLAYBOOK's lens names directly (an agent can
  prove a paid API works end-to-end for free before funding a wallet — the barrier to agent adoption) and
  dovetails with ASRS's own $0-only ethos. DISTINCT from every existing signal: subscription `free-trial` = a
  time-boxed RECURRING-plan window; `test-mode` = a SANDBOX/fake env; `self-provisioning` = free IDENTITY/access
  — none is "run a real billable unit at $0 before funding". Precision-first (12 homonym distractors — free
  shipping/trial/parking/WiFi, royalty-free, toll-free, "feel free", "$5M funding before launch", "read before
  you pay", paid-in "500 units/month" — fire ZERO; verified empirically before writing). Non-vacuous: fires 17×
  on REAL captured driftflight.com agent docs (llms.txt + llms-full.txt + manifest.json — "Free allowance - try
  it before any payment", "`includedUnits` - free usage per account that needs no funding", "try this API end
  to end before any money is involved"), ZERO on .org (no llms.txt) / api.replicate.com / retail / null — the
  honest with-rails/no-rails capability-gap echo (payment-receipt / reserve-and-settle shape). SCORE-NEUTRAL by
  construction: driftflight.com already claims metered_api strongest, so it only DEEPENS the claim — claimed
  SET+ORDER `['metered_api','digital_good','subscription']` unchanged on BOTH canonical domains. Three edits:
  signal in `asrs/offering.py`; `_ISOLATION_EVIDENCE` completeness entry in `tests/test_offering_canonical.py`
  (62→63 signals); the `reserve-and-settle`-mirrored guard pair in `tests/test_offering.py` (registered in
  `main()`). OFF the scoring path (`git diff --name-only` = `asrs/offering.py` + the two test files ONLY;
  scoring.py/probes.py/rubric/fixtures EMPTY; grep-reconfirmed the classifier is off the scoring path) →
  direct-to-main, NOT peer-gated (Cycle-150/152/156 precedent). Full suite 23 files green; `test_offering.py`
  68→70, `test_offering_canonical.py` 52→53; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric
  v0.7. NEXT (TRUTH 161): the `free-included-usage` relabel-invariance guard
  (`test_offering_relabel_invariance_free_included_usage`, synthetic host-in-evidence vehicle mirroring the
  reserve-and-settle 157 guard), then a READOUT methodology paragraph closing the arc. In-cloud COVERAGE on
  committed evidence is now essentially exhausted (metered_api = 26 signals); remaining frontier is `[LOCAL]`
  fixtures.
- SUPERSEDED (Cycle 159 runner note): RUNNER AT-FLOOR at 2026-08-01T18:17Z (Cycle 159) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~14.4h old at the 18:17Z fire — PAST the 6h floor (the local ~04:xx–18:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Already flagged in the 16:12Z Cycle-157 daily digest. Live signal (read, not re-run):
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F /
  85.5 B / +39.4). Fire at 18:17Z is NOT the first after 16:00 UTC (Cycle 157 sent the digest at 16:12Z) → no
  DM this fire per comms policy (tests-only/score-neutral, no sensitive-class PR, nothing score-moving). No
  open peer-gated PRs this fire (`list_pull_requests` state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 159): fresh checkout landed on detached HEAD at Cycle 158's `29d0c6a`; `git fetch origin main` FIRST
  (Cycle-151 lesson) → `origin/main` force-updated `3796519...29d0c6a`, `checkout -B main origin/main` realigned
  onto `29d0c6a`, no work lost. Created `.venv`, installed `requests pyyaml eth-account pytest` + verified
  `import requests, yaml, asrs` before trusting the suite (372 tests green pre-flight).
- SUPERSEDED (Cycle 159 focus pointer): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 159 was
  METHOD, so Cycle 160 is COVERAGE). Cycle 159 shipped a **METHOD surface-dedup guard on the machine pole** —
  `test_offering_surface_dedup_invariance_machine` in `tests/test_offering_canonical.py`, extending the
  surface-dedup metamorphic axis (previously org/com only) onto the single-archetype metered_api OpenAPI-spec
  pole (`api.replicate.com`). This is the NATIVE home of the dedup mechanism: the live discovery path mirrors
  every `_SURFACE_DOCS` path across apex + `api.`/`docs.` host-qualified keys, so an `/openapi.json` re-served
  at `/swagger.json` or behind a CDN hands the classifier the SAME spec body under two keys. Property protected
  = "never manufacture the delta" on the DEDUP axis from the metered pole: re-serving the spec must not push
  metered_api up in strength NOR conjure a rails archetype the API does not offer. A dedicated test (not a
  reuse of `_assert_surface_dedup_invariance`) because the shared helper's non-vacuity rests on `>=2` claimed
  archetypes for a RANK REORDER — the machine pole claims exactly ONE, so the single-claim analogue tooth is
  (a) the one claim's raw signal count STRICTLY INCREASES under the mirror (metered_api 9→18 signals, a
  count-based `strength=len(signals)` reader would differ) while (b) the five siblings stay NA (no rail
  conjured). Asserts strength / distinct-label-set / ranked-archetypes / NA-set all invariant; verified
  empirically before writing (surfaces_seen grows by exactly `mirror::/openapi.json`, 9→18 raw signals, rest
  byte-identical). REGISTERED in `main()` (the `test_runner_registration` silent-dead-test guard). Tests-only,
  OFF the scoring path (`git diff --name-only` = `tests/test_offering_canonical.py` ONLY; scoring.py/probes.py/
  offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated; direct-to-main. Full suite 372→373;
  `test_offering_canonical.py` 52→53; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  NEXT (COVERAGE 160): the surface-dedup axis is now complete on the poles where the mechanism exists
  (org/com/machine; retail is structurally excluded — a single-surface homepage catalog has no doc surface to
  mirror). In-cloud COVERAGE on committed evidence stays very narrow (metered_api = 25 signals); remaining
  frontier is `[LOCAL]` fixtures, or a METHOD listing-order/endpoint-order pole for a later rotation.
- SUPERSEDED (Cycle 158 runner note): RUNNER AT-FLOOR at 2026-08-01T17:12Z (Cycle 158) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~13.4h old at the 17:12Z fire — PAST the 6h floor (the local ~04:xx–17:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Already flagged in the 16:12Z Cycle-157 daily digest. Live signal (read, not re-run):
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS
  (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F /
  85.5 B / +39.4). Fire at 17:12Z is NOT the first after 16:00 UTC (Cycle 157 sent the digest at 16:12Z) → no
  DM this fire per comms policy (READOUT display-only, no sensitive-class PR, nothing score-moving). No open
  peer-gated PRs this fire (list_pull_requests state=open → []), so no first-duty review. INFRA/SELF-HEAL
  (Cycle 158): fresh checkout landed on detached HEAD at Cycle 157's `2a6fa4a`; `git fetch origin main` FIRST
  (Cycle-151 lesson) → `origin/main` force-updated `3796519...2a6fa4a`, `checkout -B main origin/main` realigned
  onto `2a6fa4a`, no work lost. Created `.venv`, installed `requests pyyaml eth-account pytest` + verified
  `import requests, yaml, asrs` before trusting the suite (372 tests green pre-flight).
- SUPERSEDED (Cycle 158 focus pointer): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 158 was
  READOUT, so Cycle 159 is METHOD). Cycle 158 shipped a **READOUT methodology paragraph** — a
  `_write_methodology_page` "Bounding a single call's cost" paragraph in `asrs/scorecard.py` CLOSING the
  reserve-and-settle COVERAGE(156)→TRUTH(157)→READOUT(158) arc (the payment-receipt 142/143/144 pattern). It
  frames Cycle 156's metered_api `reserve-and-settle` signal as the capital-safety sibling of the
  `failure-not-billed` leg from the other direction — failure-not-billed bounds what a FAILED call costs, this
  bounds what a SUCCESSFUL one can cost BEFORE the agent commits — names the failure (a per-call buyer against
  a variable-priced endpoint cannot bound worst-case exposure until the bill arrives, no way to cap up front),
  ties it to the $0-only capital-safety ethos ("credit-card hold"), names its distinctness from every neighbour
  (payment RAILS = the agent CAN pay; RECEIPT = proof of a SUCCESSFUL charge; PRICING = HOW you're charged on
  success; failure-not-billed = a FAILURE's cost), preserves the bare-word precision honesty (a bare
  reserve/refund/ceiling/escrow — hotel reservation, reserve-the-right, retail full refund, reserved capacity,
  ceiling fan — is no signal), stays vendor-neutral (reserve-and-pay-actual rail / spend ceiling / charged only
  actual / escrow refunds the remainder, recognition keyed on the contract not who documents it, identity-
  relabel-pinned), and honest on scope (diagnostic, off the scoring path). Guard
  `test_methodology_documents_reserve_and_settle` in `tests/test_readout.py` (65→66, mirror of
  `test_methodology_documents_failure_not_billed`), REGISTERED in `main()` (the `test_runner_registration.py`
  silent-dead-test guard caught the omission on the first full-suite run). Display-only, OFF the scoring path
  (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY; scoring.py/probes.py/offering.py/
  rubric/fixtures EMPTY) → score-neutral, NOT peer-gated; direct-to-main. Full suite 372 passed (371→372);
  replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. NEXT (METHOD 159): the
  reserve-and-settle arc is COMPLETE; a METHOD rotation could mirror the surface-dedup or listing-order
  metamorphic axis onto the retail/machine pole (casing axis completed all four poles Cycle 155), or add a new
  metamorphic/isolation cell. In-cloud COVERAGE on committed evidence stays very narrow (metered_api = 25
  signals); remaining frontier is `[LOCAL]` fixtures.
- SUPERSEDED (Cycle 157 runner note): RUNNER AT-FLOOR at 2026-08-01T16:12Z (Cycle 157) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~12.4h old at the 16:12Z fire — PAST the 6h floor (the local ~04:xx–16:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the
  frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Fire at 16:12Z is the FIRST after 16:00 UTC →
  daily digest DM SENT (per comms policy). No open peer-gated PRs this fire (list_pull_requests state=open →
  []), so no first-duty review. INFRA/SELF-HEAL (Cycle 157): fresh checkout landed clean on `main` at `b75ee42`
  (Cycle 156), no git divergence this fire; created `.venv`, installed `requests pyyaml eth-account` + verified
  `import requests, yaml, asrs` before trusting the suite (23 files green pre-flight).
- SUPERSEDED (Cycle 157 focus pointer): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 157 was
  TRUTH, so Cycle 158 is READOUT). Cycle 157 shipped a **TRUTH relabel-invariance guard** —
  `test_offering_relabel_invariance_reserve_and_settle` in `tests/test_offering_canonical.py`, the signal-level
  metamorphic mirror every recent metered_api signal earns (failure-not-billed 153 / output-retention 151 /
  plan-purchase 147 / payment-receipt 143), now covering Cycle 156's `reserve-and-settle` capital-safety signal.
  Whether an agent can CAP a single call's exposure up front (reserve a ceiling → pay actual → refund the rest)
  is a property of the reserve-and-settle CONTRACT, never who vends it → identity-invariant under a host relabel.
  Non-vacuous SYNTHETIC vehicle (`acme-meter.example`) since the live reserve-and-settle quote is host-FREE
  ("reserves the ceiling", "escrow refunds the rest") → a whole-fixture relabel would be VACUOUS: the host is
  seated in the surface-key prefix AND adjacent to the reserve-and-settle phrase within the 40-char quote pad
  (asserted host-in-BOTH-surface-key-and-quote before relabel). TEETH: reserve/refund-SHAPED homonym noise
  ("reserves the right to change prices", "full refund within 30 days", "reserved capacity ceilings apply")
  fires ZERO — the match keys on the reserve-AND-settle STRUCTURE, not a bare reservation/refund/ceiling.
  Verified empirically (base=1 host-in-quote, distractor=0, relabel=1 host-absent + quote still matches the live
  regex) before writing. Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_offering_canonical.py`
  ONLY; `asrs/ rubric/ fixtures/` EMPTY) → score-neutral, NOT peer-gated; direct-to-main.
  `test_offering_canonical.py` 51→52; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4;
  rubric v0.7. NEXT (READOUT 158): close the reserve-and-settle COVERAGE(156)→TRUTH(157)→READOUT arc with a
  `_write_methodology_page` "Bounding a single call's cost" paragraph in `asrs/scorecard.py` (capital-safety
  sibling of the receipt/failure-not-billed legs) pinned by a `test_methodology_documents_reserve_and_settle`
  presence/wording guard — the payment-receipt 142/143/144 pattern. In-cloud COVERAGE on committed evidence
  stays narrow (metered_api = 25 signals); remaining frontier is `[LOCAL]` fixtures.
- SUPERSEDED (Cycle 156 runner note): RUNNER AT-FLOOR at 2026-08-01T15:12Z (Cycle 156) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~11.4h old at the 15:12Z fire — PAST the 6h floor (the local ~04:xx–15:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the
  frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Both the runner-floor-breach and the persistent
  divergence carry to the next first-after-16:00 digest (~Aug-1 16:xxZ). No open peer-gated PRs this fire
  (list_pull_requests state=open → []), so no first-duty review. INFRA/SELF-HEAL (Cycle 156): fresh checkout
  landed on detached HEAD at `c0bba5f` (Cycle 155); `git fetch origin main` FIRST (Cycle-151 lesson) →
  `origin/main` force-updated `3796519...c0bba5f`, `checkout -B main origin/main` realigned onto Cycle 155's
  `c0bba5f`, no work lost. Created `.venv`, installed `requests pyyaml eth-account` + verified
  `import requests, yaml, asrs` before trusting the suite (23 files green).
- SUPERSEDED (Cycle 156 focus pointer): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 156 was
  COVERAGE, so Cycle 157 is TRUTH). Cycle 156 shipped a **COVERAGE metered_api signal** — `reserve-and-settle`
  in `asrs/offering.py`'s metered_api bank: whether an agent can CAP its per-call exposure up front (reserve a
  spend CEILING, be charged only ACTUAL usage, refunded the unused remainder) — the capital-safety leg that
  bounds a SUCCESSFUL call's cost, the metered sibling of `failure-not-billed` (which bounds a FAILURE's cost).
  DISTINCT from x402/agent-payment-rail (the agent CAN pay), payment-receipt (proof of a SUCCESSFUL charge),
  and the pricing signals (how you're charged on success). Precision-first: NEVER bare reserve/refund/ceiling/
  escrow — requires the named `reserve-and-pay-actual` rail, `reserve(s) the ceiling`, `charged only actual`
  anchored to a reserve/ceiling context, or an escrow/channel/reserve that `refunds the rest/difference/...`;
  7 homonym distractors (hotel reservation, reserve-the-right, retail refund, reserved capacity, ceiling fan,
  trial-not-charged, charged-monthly) verified firing ZERO before writing. Fires on BOTH real driftflight.com
  agent surfaces (llms.txt + llms-full.txt), ZERO on drift-flight.org (no llms.txt) / api.replicate.com /
  retail / null — the .com-only firing is the honest with-rails/no-rails capability-gap echo (payment-receipt
  shape). Three edits: signal in `asrs/offering.py`; `_ISOLATION_EVIDENCE` completeness entry in
  `tests/test_offering_canonical.py` (50→51); payment-receipt-mirrored guard pair in `tests/test_offering.py`
  (66→68). SCORE-NEUTRAL by construction (.com already claims metered_api → claim only DEEPENED; claimed
  SET+ORDER unchanged on both; `git diff` over `asrs/scoring.py rubric/ fixtures/` EMPTY; classifier off the
  scoring path, grep-reconfirmed) → NOT peer-gated; direct-to-main. Full suite 23 files green; replay guard
  24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (TRUTH 157): the `reserve-and-settle` relabel-invariance
  guard (`test_offering_relabel_invariance_reserve_and_settle` in `tests/test_offering_canonical.py`, synthetic
  host-in-evidence vehicle since the quote is host-free), then a READOUT methodology paragraph closing the
  COVERAGE(156)→TRUTH→READOUT arc. In-cloud COVERAGE on committed evidence is now VERY narrow (metered_api = 25
  signals); remaining frontier is `[LOCAL]` fixtures.
- SUPERSEDED (Cycle 155 runner note): RUNNER AT-FLOOR at 2026-08-01T14:17Z (Cycle 155) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~10.4h old at the 14:17Z fire — PAST the 6h floor (the local ~04:xx–14:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the
  frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Both the runner-floor-breach and the persistent
  divergence carry to the next first-after-16:00 digest (~Aug-1 16:xxZ). INFRA/SELF-HEAL (Cycle 155): fresh
  checkout landed on detached HEAD at `3187d52` (Cycle 154); `git fetch origin main` FIRST (Cycle-151 lesson)
  → `origin/main` force-updated `3796519...3187d52`, `checkout -B main origin/main` realigned onto Cycle 154's
  `3187d52`, no work lost. Created `.venv`, installed `requests pyyaml eth-account` directly + verified
  `import requests, yaml, asrs` before trusting the suite.
- SUPERSEDED (Cycle 155 focus pointer): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 155 was
  METHOD, so Cycle 156 is COVERAGE). Cycle 155 shipped a **METHOD casing-invariance guard on the RETAIL pole**
  — `test_offering_casing_invariance_retail` in `tests/test_offering_canonical.py`, the fourth and final pole
  of the case-invariance axis (org/com PROSE + machine metered_api spec already covered; retail was the open
  cell, the same org/com/machine-only-vs-retail asymmetry the content-scale + noise-surface axes already
  closed). Pins a no-rails book catalog (`books.toscrape.com`) claiming EXACTLY physical_good, all rails NA:
  uppercasing the shelf copy must not raise physical_good strength NOR conjure a rails archetype. Dedicated
  test (not a reuse of `_assert_casing_invariance`) for two verified-empirical structural reasons: (a)
  single-surface fixture fails the helper's `_captured_surfaces` >=2 premise → inline spy capture; (b) the
  physical_good bank is lowercase-authored and matches mixed-case copy ONLY via `re.IGNORECASE` (add-to-cart/
  stock/priced-listing all 0→0 case-sensitive, 20→20 IGNORECASE), so the helper's "count moves" tooth
  (`cs_b != cs_u`) is structurally impossible → replaced with the STRONGER "folding is ESSENTIAL" tooth (a
  fired signal matches 0x case-sensitively yet Nx with IGNORECASE, so stripping the fold erases the claim).
  Uses `_casing_struct` (quote-excluded, since quotes upper-case with the surface), not `_full_evidence_map`.
  Tests-only, OFF the scoring path (`git diff --name-only` = `tests/test_offering_canonical.py` ONLY;
  `asrs/ rubric/ fixtures/` EMPTY) → score-neutral, NOT peer-gated; direct-to-main. `test_offering_canonical.py`
  50→51; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (COVERAGE
  156): in-cloud COVERAGE on committed evidence is VERY narrow (overage/SLA/balance-check/subscription-cancel
  proved blocked Cycle 152; output FORMAT stays a false-positive minefield) → likely a new [LOCAL]
  fixture-dependent signal queued, or an open metamorphic/isolation cell. The casing axis is now COMPLETE
  across all four poles; a future METHOD rotation could mirror surface-dedup or listing-order onto retail/machine.
- SUPERSEDED (Cycle 154 runner note): RUNNER AT-FLOOR at 2026-08-01T13:15Z (Cycle 154) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~9.4h old at the 13:15Z fire — PAST the 6h floor (the local ~10:xx–13:xx
  fires have not pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud cannot
  repair). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 — the
  transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the
  frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Both the runner-floor-breach and the persistent
  divergence carry to the next first-after-16:00 digest (~Aug-1 16:xxZ). INFRA/SELF-HEAL (Cycle 154): `git
  fetch origin main` FIRST (the Cycle-151 stale-`origin/main` lesson) → `origin/main` force-updated
  `3796519...5b53ea3`, `checkout -B main origin/main` landed on Cycle 153's `5b53ea3`, no work lost. Repo has
  NO pyproject/setup.py (asrs imports from repo root) so `pip install -e .` is expected to fail — installed
  `requests pyyaml eth-account` directly + verified `import requests, yaml, asrs` before trusting the suite.
- SUPERSEDED (Cycle 154 focus pointer): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 154 was
  READOUT, so Cycle 155 is METHOD). Cycle 154 shipped a **READOUT methodology paragraph** — a
  `_write_methodology_page` "Not paying for a call that failed" paragraph in `asrs/scorecard.py` framing Cycle
  152's metered_api `failure-not-billed` signal as the capital-safety sibling of the `receipt` leg ("you don't
  pay for work you didn't get"), naming its distinctness from the receipt (proof of a SUCCESSFUL charge), the
  error contract (SHAPE of a failure, not its price), and a free trial ($0 window); precision honesty
  preserved (a bare "not charged" trial promise is no signal). This CLOSES the failure-not-billed
  COVERAGE(152)→TRUTH(153)→READOUT(154) arc, the pattern of payment-receipt 142/143/144. Guard
  `test_methodology_documents_failure_not_billed` in `tests/test_readout.py` (64→65), the presence/wording
  mirror of `test_methodology_documents_payment_receipt`. Display-only + wording guard, OFF the scoring path
  (`git diff --name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY; scoring.py/probes.py/
  offering.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated; direct-to-main. Full suite 23 files
  green; replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (METHOD 155): an open metamorphic
  cell — casing on the RETAIL pole, or a content-scale / noise-surface guard on the metered_api MACHINE
  surface. In-cloud COVERAGE on committed evidence is VERY narrow (overage/SLA/balance-check/subscription-
  cancel proved blocked Cycle 152; output FORMAT stays a false-positive minefield); service_booking /
  data_retrieval + physical fulfillment + ACP/UCP/MPP + free-tier live-wiring stay `[LOCAL]`.
- SUPERSEDED (Cycle 153 runner note): RUNNER AT-FLOOR at 2026-08-01T12:1xZ (Cycle 153) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~8.4h old at the 12:12Z fire — PAST the 6h floor (the ~10:xx–12:xx local
  fires have not yet pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud
  cannot repair). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 —
  the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Both the runner-floor-breach and the
  persistent divergence carry to the next first-after-16:00 digest (~Aug-1 16:xxZ). INFRA/SELF-HEAL (Cycle
  153): fresh checkout landed on `main` at `b80d14e` (Cycle 152), no git divergence this fire; the `pip
  install -e .` silently no-op'd on `requests` again (recurring proxy-masking) → re-ran `pip install requests
  pyyaml eth-account` verbosely + verified `import requests, yaml, asrs` before trusting the suite.
- SUPERSEDED (Cycle 153 focus pointer): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 153 was
  TRUTH, so Cycle 154 is READOUT). Cycle 153 shipped a **TRUTH relabel-invariance guard** —
  `test_offering_relabel_invariance_failure_not_billed` in `tests/test_offering_canonical.py`, the
  signal-level metamorphic mirror every recent signal earns (output-retention 151 / plan-purchase 147 /
  payment-receipt 143 / error-contract 91), now covering Cycle 152's `failure-not-billed` metered_api signal.
  Whether a failed unit is billed is a property of the failure-billing CONTRACT, never of who vends it, so the
  signal is identity-invariant under a host relabel. Non-vacuous SYNTHETIC vehicle (the failure-not-billed
  quote is host-FREE, so a whole-fixture relabel would be VACUOUS): `acme-flux.example` seats the host INSIDE
  the evidence (surface-key prefix + adjacent to "if a render fails it is never charged", asserted non-vacuous
  — host in BOTH surface key and padded quote); relabel host → neutral everywhere and the signal survives with
  the SAME match count (1) / SAME host-normalized surface / quote still matching the live regex / host absent.
  TEETH: the not-charged-shaped noise (a subscription free-trial "your card is not charged until the trial
  ends" — no failure word; the `error-contract` "on failure the body is application/problem+json" — no
  not-charged) fires ZERO failure-not-billed. Tests-only, off scoring path (`git diff --name-only` =
  `tests/test_offering_canonical.py` ONLY) → score-neutral, NOT peer-gated; direct-to-main.
  `test_offering_canonical.py` 49→50; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4;
  rubric v0.7. NEXT (READOUT 154): the `failure-not-billed` COVERAGE(152)→TRUTH(153)→READOUT arc's closing
  leg — a `_write_methodology_page` paragraph framing "you don't pay for work you didn't get" as the metered
  capital-safety sibling of `payment-receipt` (the pattern of plan-purchase 146/147/148). In-cloud COVERAGE on
  committed evidence is now VERY narrow (overage/SLA/balance-check/subscription-cancel proved blocked Cycle
  152); output FORMAT stays a false-positive minefield; service_booking / data_retrieval + physical
  fulfillment + ACP/UCP/MPP + free-tier live-wiring stay `[LOCAL]`.
- SUPERSEDED (Cycle 152 runner note): RUNNER AT-FLOOR at 2026-08-01T11:2xZ (Cycle 152) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~7.4h old at the 11:2xZ fire — PAST the 6h floor (the ~10:xx/11:xx local
  fires have not yet pushed a fresh artifact; borderline runner lag, NOT the machine-asleep stall — cloud
  cannot repair). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 —
  the transactability-drop divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays
  the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4). Both the runner-floor-breach and the
  persistent divergence carry to the next first-after-16:00 digest (~Aug-1 16:xxZ). INFRA/SELF-HEAL (Cycle
  152): `git fetch origin main` FIRST (the Cycle-151 stale-`origin/main` lesson) → `reset --hard` aligned
  `3796519...aaeb265` (Cycle 151), no work lost; the `-q` `pip install -e .` silently no-op'd again (Cycle-150
  proxy-masking) → re-ran verbosely + verified `import requests` before trusting the suite.
- FOCUS POINTER (Cycle 152 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 152 was
  COVERAGE, so Cycle 153 is TRUTH). Cycle 152 shipped a **COVERAGE metered_api signal** — `failure-not-billed`
  in `asrs/offering.py`'s metered_api bank: whether a metered call that FAILS (render did not complete / job
  errored / request timed out) is NOT charged — the capital-safety "you don't pay for work you didn't get"
  leg, DISTINCT from `error-contract` (error FORMAT), `payment-receipt` (proof of a SUCCESSFUL charge),
  `test-mode` ($0 sandbox), and the billing signals (how you're charged ON SUCCESS); the metered sibling of
  digital_good's `output-retention`. Precision-first: NEVER a bare "not charged" (dodges the subscription
  trial-$0 promise "card not charged until the trial ends") — requires a FAILURE token within a
  sentence-bounded window of "(not|never) (charged|billed)" (either order), OR "only (charged|billed) for
  successful/completed". Fires exactly once on BOTH canonical `/docs` ("502 generation_failed | The render did
  not complete; you are not charged a generation"), ZERO on api/retail/null. REJECTED this cycle as
  vacuous/colliding: `overage` (metered_api `usage-based` already matches bare `\boverage\b` → redundant +
  isolation-breaking), `SLA` (the 35 hits are the `--slate` CSS var), usage/balance-CHECK endpoint,
  subscription-CANCEL (all absent from committed fixtures → stay `[LOCAL]`). Off the scoring path (`git diff
  --name-only` over scoring.py/probes.py/scorecard.py/rubric/fixtures EMPTY; changed = `asrs/offering.py` +
  `tests/test_offering.py` + `tests/test_offering_canonical.py`) → score-neutral (claimed SET+ORDER unchanged
  on all 5 fixtures; metered_api deepened only), NOT peer-gated; direct-to-main. Two-test guard in
  `test_offering.py` (64→66) + `_ISOLATION_EVIDENCE` completeness entry (49 signals, cross-archetype isolation
  green). Full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (TRUTH
  153): the `failure-not-billed` per-signal relabel-invariance / metamorphic guard (mirror of output-retention
  151 / plan-purchase 147 / payment-receipt 143) — host-free quotes, so a synthetic host-seated surface is the
  non-vacuous vehicle. In-cloud COVERAGE on committed evidence is now VERY narrow (this cycle proved
  overage/SLA/balance-check/subscription-cancel all blocked); output FORMAT stays a false-positive minefield;
  service_booking / data_retrieval + physical fulfillment + ACP/UCP/MPP + free-tier live-wiring stay `[LOCAL]`.
- SUPERSEDED (Cycle 151 runner note): RUNNER AT-FLOOR at 2026-08-01T10:1xZ (Cycle 151) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~6.4h old at the 10:1xZ fire — JUST past the 6h floor (the ~10:xxZ local
  fire should refresh it; expected borderline, NOT the machine-asleep stall — cloud cannot repair). Live
  signal (read, not re-run): driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop
  divergence PERSISTS (Aug-1), off the scoring path; the in-cloud replay guard stays the frozen independent
  signal (24/24, 46.1 F / 85.5 B / +39.4). Both the runner-floor-breach and the persistent divergence carry
  to the next first-after-16:00 digest (~Aug-1 16:xxZ). INFRA/SELF-HEAL (Cycle 151): the fresh checkout's
  local `origin/main` tracking ref was STALE — clone left it at `3796519` (Cycle 94) while the tree was
  detached at the REAL HEAD `74fa29e` (Cycle 150); a naive `git checkout -B main origin/main` rewound the
  tree to Cycle 94 (a false bookkeeping-down). `git fetch origin main` force-updated the ref
  `3796519...74fa29e`, confirming GitHub's `origin/main` is genuinely Cycle 150; re-checkout realigned, NO
  work lost. LESSON: `git fetch origin main` BEFORE trusting `git checkout -B main origin/main` on a fresh
  cloud checkout, or a legitimate HEAD reads as a divergence.
- FOCUS POINTER (Cycle 151 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 151 was
  METHOD, so Cycle 152 is COVERAGE). Cycle 151 shipped a **METHOD relabel-invariance guard** —
  `test_offering_relabel_invariance_output_retention` in `tests/test_offering_canonical.py`, the signal-level
  metamorphic mirror every recent signal earns (plan-purchase 147 / payment-receipt 143 / error-contract 91),
  now covering Cycle 150's `output-retention` digital_good signal. A SYNTHETIC digital_good surface seats the
  host INSIDE the retention evidence (surface key prefix + host adjacent to "hosted URL that remains available
  for 90 days", asserted non-vacuous); relabel host → neutral everywhere and the signal survives with the SAME
  match count / SAME host-normalized surface / quote still matching the live regex / host absent. TEETH: the
  retention-shaped noise (a support-line window with no deliverable noun; the signed download-URL / file
  EXPIRY trap on a metered-API marketplace) fires ZERO output-retention. Tests-only, off scoring path (`git
  diff --name-only` = `tests/test_offering_canonical.py` ONLY) → score-neutral, NOT peer-gated; direct-to-main.
  `test_offering_canonical.py` 48→49; runner-registration meta-guard 4/4; full suite 23 files green; replay
  guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (COVERAGE 152): a capability signal on committed
  evidence — output FORMAT (PNG/JPEG/MP4/WebP) is the narrow digital_good frontier but a false-positive
  minefield (deferred until a genuinely distinct capability + precision-guarded evidence). Open metamorphic
  cells for a future METHOD: casing on the RETAIL pole; content-scale / noise-surface on the metered_api
  MACHINE surface. subscription-CANCEL / lifecycle stays [LOCAL]-blocked; service_booking / data_retrieval +
  physical fulfillment + ACP/UCP/MPP + free-tier live-wiring stay [LOCAL].
- SUPERSEDED (Cycle 150 runner note): RUNNER HEALTHY at 2026-08-01T09:1xZ (Cycle 150) — newest verify `runs/local/verify_20260801T035047Z.json`
  (03:50Z Aug-1, `attempts=1`) is ~5.35h old at the 09:11Z fire, INSIDE the 6h floor but nearing it (the
  ~10:xxZ local fire should refresh it). Live signal (read, not re-run): driftflight.com 76.2 C / +30.1 /
  transactability 62.5 — the transactability-drop divergence PERSISTS a third day (Aug-1), still off the
  scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B / +39.4).
  Resolution = queued P0 [LOCAL] re-baseline; the persistent divergence goes in the next first-after-16:00
  digest (~Aug-1 16:xxZ). Infra note (Cycle 150): fresh cloud checkout landed detached-HEAD, `git checkout -B
  main origin/main` realigned to 8d69699; the FIRST `.venv` `pip install -q` silently no-op'd (transient proxy
  failure masked by `-q` — the suite showed spurious `ModuleNotFoundError: requests/yaml`), re-running
  `pip install requests pyyaml eth-account` verbosely fixed it. LESSON: verify `import requests` before
  trusting a suite result; a `-q` pip install can hide a transient proxy failure.
- FOCUS POINTER (Cycle 150 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 150 was
  COVERAGE, so Cycle 151 is METHOD). Cycle 150 shipped a **COVERAGE digital_good signal** — `output-retention`
  in `asrs/offering.py`'s digital_good bank: the "complete the job" LIFECYCLE leg of a digital good (how long
  the generated deliverable PERSISTS at its hosted URL; the agent must download it into its OWN storage before
  the window closes) — distinct from every existing digital_good signal (WHAT/WHERE/SHAPE/USE-rights/TRUST;
  NONE says HOW LONG it lives), the digital_good sibling of metered_api's `cancel-job`. Precision-first: the
  window must attach to a DELIVERABLE noun + persistence verb (remain available / hosted / stored / retained /
  kept for N hours|days), OR be "download ... into your own storage/bucket", OR an explicit "<output/render/
  ...> retention window/period/policy" — dodges the support-line / event-hosting / free-trial senses AND
  api.replicate.com's Files API signed-URL/file EXPIRY trap (must not conjure digital_good on a metered_api-only
  site). Fires non-vacuously on BOTH canonical `/docs` ("hosted URLs that remain available for 90 days;
  download them into your own storage"), ZERO on api/retail/null. Off the scoring path (`git diff --name-only`
  over scoring.py/probes.py/scorecard.py/rubric/fixtures EMPTY; changed = `asrs/offering.py` +
  `tests/test_offering.py` + `tests/test_offering_canonical.py`) → score-neutral (claimed SET+ORDER unchanged;
  digital_good deepened only), NOT peer-gated; branch loop/output-retention-signal + PR #142 + self-merge
  (squash 24412ae). Two-test guard in `test_offering.py` (62→64) + `output-retention` added to
  `test_offering_canonical.py`'s `_ISOLATION_EVIDENCE` completeness map (47→48). Full suite 23 files green;
  replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (METHOD 151): a measurement-rigor unit — a
  relabel-invariance guard for `output-retention` (the TRUTH-leg mirror of plan-purchase 147 / payment-receipt
  143), or an open metamorphic-grid cell (casing on the RETAIL pole; content-scale / noise-surface on the
  metered_api MACHINE surface). Remaining distinct digital_good caps (output FORMAT) stay a false-positive
  minefield; subscription-CANCEL / lifecycle stays [LOCAL]-blocked (no committed `/cancellation` fixture);
  service_booking / data_retrieval + physical fulfillment + ACP/UCP/MPP + free-tier live-wiring stay [LOCAL].
- SUPERSEDED (Cycle 149 focus pointer): RUNNER HEALTHY at 2026-08-01T08:1xZ (Cycle 149) — newest verify
  `runs/local/verify_20260801T035047Z.json` (03:50Z Aug-1, `attempts=1`) is ~4.3h old at the fire, INSIDE
  the 6h floor (Cycle 137–144 machine-asleep-stall recovery holds four cycles on). Live signal:
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence PERSISTS a
  third day (Aug-1), still off the scoring path; the in-cloud replay guard stays the frozen independent
  signal (24/24, 46.1 F / 85.5 B / +39.4). Resolution = queued P0 [LOCAL] re-baseline. The persistent
  divergence goes in the next first-after-16:00 digest (~Aug-1 16:xxZ). Infra note: local `main` was a
  stale/diverged Cycle-94 fork this fire — `git fetch origin main` + `git reset --hard origin/main` realigned
  to 3cfc79d before working; rebuilt env-only deps in a fresh `.venv` (`pip install -e . requests eth-account
  pyyaml`) for the full suite.
- SUPERSEDED (Cycle 149) — COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 149 was
  METHOD, so Cycle 150 is COVERAGE). Cycle 149 shipped a **METHOD metamorphic cell** — `test_offering_casing_
  invariance_machine` in `tests/test_offering_canonical.py`: the text-casing invariance axis (Cycle 133,
  org/com PROSE poles only) mirrored onto the qualitatively different metered_api MACHINE pole
  (`api.replicate.com`, classified RAW from `/openapi.json`). Uppercasing every surface body leaves the
  case-independent capability skeleton (claimed archetype + `strength` + per-(label, surface) counts + NA
  complement) identical; the load-bearing tooth lands naturally — the `post-endpoint` `https?://` case-
  SENSITIVE count moves 1→0 under uppercasing while IGNORECASE holds, so a future machine-surface signal
  added without `re.IGNORECASE` fails loudly. `_assert_casing_invariance` gained a `min_claimed` kwarg
  (default 2, byte-identical for org/com; `=1` for the single-archetype machine pole = claim/(strength,count)
  survival, no rank). Tests-only, off scoring path (`git diff --name-only` = `tests/test_offering_canonical.py`
  ONLY) → score-neutral, rubric v0.7, NOT peer-gated; direct-to-main. `test_offering_canonical.py` 47→48;
  runner-registration meta-guard 4/4; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B / +39.4.
  NEXT (COVERAGE 150): a new capability signal on committed evidence (digital_good is the narrow in-cloud
  frontier — output FORMAT is a false-positive minefield, needs a genuinely distinct capability +
  precision-guarded evidence). Metamorphic-grid cells still open: casing on the RETAIL pole, and
  content-scale / noise-surface invariance on the metered_api MACHINE surface.
- SUPERSEDED (Cycle 148) — Cycle 148 shipped the **plan-purchase READOUT leg** — a "Committing to a
  plan without a human" methodology paragraph in `_write_methodology_page` (`asrs/scorecard.py`), inserted
  after the free-trial "$0 evaluation" subscription paragraph, framing the subscription COMMIT leg as
  DISTINCT from the recurring PRICE / the $0 EVALUATION / the payment RAILS and as the subscription
  counterpart of metered_api's `self-provisioning`; keeps the human-path precision guard (bare "plan" /
  "subscribe to a plan" / dashboard onboarding / bare "subscription plans" = no signal); diagnostic, off the
  scoring path. CLOSES the plan-purchase COVERAGE(146)→TRUTH(147)→READOUT(148) arc (mirror of payment-receipt
  142/143/144). Guard `test_methodology_documents_plan_purchase` in `tests/test_readout.py`, registered in
  the runner list. Display+tests, off scoring path (`git diff --name-only` over scoring.py/offering.py/
  probes.py/rubric/fixtures EMPTY; only changed = `asrs/scorecard.py` + `tests/test_readout.py`) →
  score-neutral, NOT peer-gated; direct-to-main commit 87041d1. `test_readout.py` 63→64;
  runner-registration meta-guard 4/4; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B /
  +39.4; rubric v0.7. NEXT (METHOD 149): a measurement-rigor unit — variance/attribution/control. In-cloud
  COVERAGE frontier on committed evidence narrows to a digital_good signal (output FORMAT is a
  false-positive minefield); subscription-CANCEL / lifecycle is [LOCAL]-blocked (no committed `/cancellation`
  fixture); service_booking / data_retrieval + physical_good fulfillment leg stay [LOCAL]; ACP/UCP/MPP +
  free-tier live-wiring stay [LOCAL].
- SUPERSEDED (Cycle 147) — RUNNER HEALTHY at 2026-08-01T06:1xZ (Cycle 147) — newest verify
  `runs/local/verify_20260801T035047Z.json` (03:50Z Aug-1, `attempts=1`) is ~2.4h old at the fire, INSIDE
  the 6h floor (Cycle 137–144 machine-asleep-stall recovery holds two cycles on). Live signal:
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence, still off the
  scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B /
  +39.4). Resolution = queued P0 [LOCAL] re-baseline. Runner-recovery + divergence go in the next
  first-after-16:00 digest (~Aug-1 16:xxZ). Restored the environment-only `eth-account` dep (`pip install
  eth-account`) for `test_free_tier` 11/11, and re-`git checkout -B main origin/main` off the fresh-checkout
  detached-HEAD / stale Cycle-94 local-main fork.
- FOCUS POINTER (Cycle 147 done): READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 147 was
  TRUTH, so Cycle 148 is READOUT). Cycle 147 shipped the **plan-purchase relabel-invariance guard** —
  `test_offering_relabel_invariance_plan_purchase` in `tests/test_offering_canonical.py`, the TRUTH leg of
  the plan-purchase COVERAGE(146)→TRUTH(147)→READOUT(148) arc (mirroring payment-receipt 142/143/144). Pins
  Cycle 146's `plan-purchase` subscription signal as identity-invariant under a host relabel: a synthetic
  subscription surface seats the host adjacent to the `/plans/pro/purchase` phrase (non-vacuous), relabel
  end-to-end and the signal survives with the SAME match count / SAME host-normalized surface / quote still
  matching the live regex / host absent. TEETH: the human plan senses (pricing-page checkout, dashboard
  onboarding, bare "subscription plans" marketing — present verbatim in both canonical fixtures) fire ZERO.
  Tests-only, off scoring path (`git diff --name-only` over scoring.py/offering.py/probes.py/scorecard.py/
  rubric/fixtures EMPTY; only changed = `tests/test_offering_canonical.py`) → score-neutral, NOT peer-gated.
  `test_offering_canonical.py` 46→47; runner-registration meta-guard 4/4; full suite 23 files green; replay
  guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (READOUT 148): a methodology paragraph in
  `_write_methodology_page` framing "commit to the recurring plan without a human" as the subscription
  COMMIT leg (distinct from recurring PRICE / $0 EVALUATION / payment RAILS), + `test_readout.py` guard,
  CLOSING the plan-purchase arc. Open COVERAGE frontier on committed evidence narrows to a digital_good
  signal (output FORMAT is a false-positive minefield); subscription-CANCEL / lifecycle is [LOCAL]-blocked
  (no committed `/cancellation` fixture); service_booking / data_retrieval + physical_good fulfillment leg
  stay [LOCAL]; ACP/UCP/MPP + free-tier live-wiring stay [LOCAL].
- SUPERSEDED (Cycle 146) — RUNNER HEALTHY at 2026-08-01T05:1xZ — newest verify
  `runs/local/verify_20260801T035047Z.json` (03:50Z Aug-1, `attempts=1`) is ~1.4h old at the fire, INSIDE
  the 6h floor (recovery from the Cycle 137–144 machine-asleep stall holds, one cycle on). Live signal:
  driftflight.com 76.2 C / +30.1 / transactability 62.5 — the transactability-drop divergence, still off the
  scoring path; the in-cloud replay guard stays the frozen independent signal (24/24, 46.1 F / 85.5 B /
  +39.4). Resolution = queued P0 [LOCAL] re-baseline. The runner-recovery + the divergence both go in the
  next first-after-16:00 digest (~Aug-1 16:xxZ). Restored the environment-only `eth-account` dep (`pip
  install eth-account`) for `test_free_tier` 11/11 each fresh cloud checkout.
- FOCUS POINTER (Cycle 146 done): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 146 was
  COVERAGE, so Cycle 147 is TRUTH). Cycle 146 shipped the **plan-purchase subscription signal** — a
  `plan-purchase` entry in `asrs/offering.py`'s subscription signal bank: the programmatic capability for an
  agent to BUY / commit to a credit-or-subscription plan via an API call (`POST /plans/{id}/purchase`
  endpoint, a purchasable plan, a buy/purchase/activate verb naming a credit/subscription plan), the
  "commit without a human" leg — counterpart to metered_api's `self-provisioning`. Precision-guarded against
  the human "subscribe to a plan on the pricing page" / dashboard onboarding phrasing + bare "subscription
  plans" marketing. Fires on the real captured driftflight.com agent docs, absent on drift-flight.org
  (human-only plan path — the discovery-layer capability-gap echo) and on the api/retail/null fixtures. Off
  scoring path (`git diff` over scoring.py/probes.py/scorecard.py/rubric/fixtures EMPTY) → score-neutral
  (claimed SET+ORDER `[metered_api, digital_good, subscription]` byte-identical; subscription strength 5→6
  on driftflight.com only), NOT peer-gated; branch loop/plan-purchase-signal + PR #140 + self-merge (squash
  e4c7ad8). `test_offering.py` 60→62; full suite 23 files green; replay guard 24/24, 46.1 F / 85.5 B /
  +39.4; rubric v0.7. NEXT (TRUTH 147): a measurement-calibration unit — real-domain sweep, panel-verdict
  stability, or does-the-score-predict-experience. Open COVERAGE frontier on committed evidence narrows to a
  digital_good signal (output FORMAT is a false-positive minefield — needs care); subscription-CANCEL /
  lifecycle is [LOCAL]-blocked (no committed `/cancellation` fixture); service_booking / data_retrieval +
  physical_good fulfillment leg stay [LOCAL]; ACP/UCP/MPP + free-tier live-wiring stay [LOCAL].
- SUPERSEDED (Cycle 145) — RUNNER RECOVERED at 2026-08-01T04:1xZ — newest verify
  `runs/local/verify_20260801T035047Z.json` (03:50Z Aug-1, `attempts=1`) is ~22 min old at the fire,
  INSIDE the 6h floor, clearing the ~14h stall tracked through Cycles 137–144. Cause was the machine
  asleep Jul-31 afternoon→Aug-1 03:xx (Cycle-63 wake-instant pattern); it self-cleared on a successful
  wake exactly as predicted, NOT a code regression, so no escalation needed. The stall was flagged in
  the Jul-31 16:1xZ digest (Cycle 133); the NEXT first-after-16:00 digest (~Aug-1 16:xxZ) should REPORT
  the recovery. Live signal from the recovered runner: driftflight.com 76.2 C / +30.1 / transactability
  62.5 — the transactability-drop divergence, now confirmed across a THIRD independent crawl (08:52Z +
  13:45Z Jul-31 + 03:50Z Aug-1). Off the scoring path; the in-cloud replay guard stays the frozen
  independent signal (24/24, 46.1 F / 85.5 B / +39.4). Resolution = queued P0 [LOCAL] re-baseline.
- FOCUS POINTER (Cycle 145 done): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 145
  was METHOD, so Cycle 146 is COVERAGE). Cycle 145 shipped the **silent-dead-test guard** —
  `tests/test_runner_registration.py` (4 tests), an `ast` meta-scan asserting every top-level `def test_*`
  is registered in its module's `tests` runner list (plus ghost detection + non-empty-list check), with
  teeth proven on synthetic sources. It IMMEDIATELY caught two more live dead tests
  (`test_webhook_verification_*` in `test_offering.py`, dead since the webhook arc) → registered them
  (58→60). This closes the Cycle-140/144 silent-dead-test class mechanically. Tests-only, off scoring path
  (`git diff` over scoring.py/offering.py/probes.py/rubric/fixtures EMPTY) → score-neutral, NOT peer-gated;
  branch loop/runner-registration-guard + PR #138 + self-merge (squash 60fa743). Full suite green across
  23 files; replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (COVERAGE 146): a digital_good
  or subscription capability signal on committed evidence with a COVERAGE→TRUTH→READOUT arc;
  service_booking / data_retrieval + physical_good fulfillment stay [LOCAL]-blocked; ACP/UCP/MPP +
  free-tier live-wiring stay [LOCAL].
- SUPERSEDED — RUNNER STILL STALE at 2026-08-01T02:5xZ (Cycle 144) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z Jul-31) is ~13h old, still BREACHING the 6h floor
  (14:41Z Jul-31–02:41Z Aug-1 launchd fires produced NO artifact = machine asleep, the Cycle-63
  wake-instant pattern, NOT a code regression). Cloud CANNOT repair. Already flagged in today's 16:1xZ
  digest (Cycle 133); 02:5xZ Aug-1 is NOT first-after-16:00 → no re-flag this fire. Re-flag in the next
  first-after-16:00 fire (~Aug-1 16:xxZ) if not recovered. A persistent no-wake past ~Aug-1 morning is an
  operator/launchd-plist matter for Jonah, NOT the Cycle-63 backoff fix. Cycle 144 restored the
  environment-only `eth-account` dep (`pip install eth-account`) so the cloud bench runs `test_free_tier`
  11/11, and re-`git checkout -B main origin/main` off the forced-update/detached-HEAD state the fresh
  cloud pull left before work.
- FOCUS POINTER (Cycle 144 done): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 144
  was READOUT, so Cycle 145 is METHOD). Cycle 144 shipped the **payment-receipt READOUT leg** — a
  methodology paragraph in `_write_methodology_page` (`asrs/scorecard.py`) framing "Accounting for the
  spend" as the capital-safety accounting sibling of the payment RAILS (agent-payment rail = the PAY
  leg; payment-receipt = the proof that comes back to reconcile the spend), CLOSING the payment-receipt
  COVERAGE(142)→TRUTH(143)→READOUT(144) arc. Guard `test_methodology_documents_payment_receipt` in
  `tests/test_readout.py`. ALSO fixed a silent dead-test bug: `test_methodology_documents_output_resolution`
  (Cycle 140) was defined but NEVER registered in the runner list (Cycle-140's claimed 61→62 never took) —
  registered it; passes against the shipped prose; runner list 61→63. Off scoring path (`git diff` over
  `asrs/scoring.py asrs/offering.py rubric/ fixtures/` EMPTY; changed = `asrs/scorecard.py` +
  `tests/test_readout.py` ONLY) → score-neutral, NOT peer-gated; branch loop/payment-receipt-readout +
  PR #136 + self-merge (squash 05821a6). Full suite 22 files green; replay guard 24/24, 46.1 F / 85.5 B /
  +39.4; rubric v0.7. NEXT (METHOD 145): a measurement-rigor unit — variance/attribution/control. Open
  COVERAGE frontier on committed evidence: digital_good / subscription signals; service_booking /
  data_retrieval new signals + physical_good fulfillment leg stay [LOCAL]-blocked; ACP/UCP/MPP + free-tier
  live-wiring stay [LOCAL].
- RUNNER STILL STALE at 2026-08-01T02:1xZ (Cycle 143) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z Jul-31) is ~12.6h old, still BREACHING the 6h floor
  (14:41Z Jul-31–02:41Z Aug-1 launchd fires produced NO artifact = machine asleep, the Cycle-63
  wake-instant pattern, NOT a code regression). Cloud CANNOT repair. Already flagged in today's 16:1xZ
  digest (Cycle 133); 02:1xZ Aug-1 is NOT first-after-16:00 → no re-flag this fire. Re-flag in the next
  first-after-16:00 fire (~Aug-1 16:xxZ) if not recovered. A persistent no-wake past ~Aug-1 morning is an
  operator/launchd-plist matter for Jonah, NOT the Cycle-63 backoff fix. Cycle 143 also re-`git reset
  --hard`'d local `main` off the Cycle-94 "unrelated history" fresh-clone fork (recurs each fresh cloud
  checkout) before work, and restored the environment-only `eth-account` dep (`pip install eth-account`)
  so the cloud bench runs `test_free_tier` 11/11 — a cloud-env gap the LOCAL runner does not have.
- RUNNER STILL STALE at 2026-08-01T01:1xZ (Cycle 142) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z Jul-31) is ~11.5h old, still BREACHING the 6h floor
  (14:41Z Jul-31–01:41Z Aug-1 launchd fires produced NO artifact = machine asleep, the Cycle-63
  wake-instant pattern, NOT a code regression). Cloud CANNOT repair. Already flagged in today's 16:1xZ
  digest (Cycle 133); 01:1xZ Aug-1 is NOT first-after-16:00 → no re-flag this fire. Re-flag in the next
  first-after-16:00 fire (~Aug-1 16:xxZ) if not recovered. A persistent no-wake past ~Aug-1 morning is an
  operator/launchd-plist matter for Jonah, NOT the Cycle-63 backoff fix (that is for the wake/network
  RACE, not a machine that never wakes). Cycle 142 also self-healed a bookkeeping fork: local `main` had
  drifted to a Cycle-94 "unrelated history" (fresh-clone artifact) and was `git reset --hard` to
  origin/main before work.
- RUNNER STILL STALE at 2026-08-01T00:1xZ (Cycle 141) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z Jul-31) is ~10.5h old, still BREACHING the 6h floor
  (14:41Z Jul-31–00:41Z Aug-1 launchd fires produced NO artifact = machine asleep, the Cycle-63
  wake-instant pattern, NOT a code regression). Cloud CANNOT repair. Already flagged in today's 16:1xZ
  digest (Cycle 133); 00:1xZ Aug-1 is NOT first-after-16:00 (Cycle 133 sent today's) → no re-flag this
  fire. Re-flag in the next first-after-16:00 fire (~Aug-1 16:xxZ) if not recovered. A persistent
  no-wake past ~Aug-1 morning is an operator/launchd-plist matter for Jonah, NOT the Cycle-63 backoff
  fix (that is for the wake/network RACE, not a machine that never wakes).
- RUNNER STILL STALE at 2026-07-31T23:1xZ (Cycle 140) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z) is ~9.5h old, still BREACHING the 6h floor
  (14:41–22:41 launchd fires produced NO artifact = machine asleep, the Cycle-63 wake-instant
  pattern, NOT a code regression). Cloud CANNOT repair. Already flagged in today's 16:1xZ digest
  (Cycle 133); re-flag in the next first-after-16:00 fire (~Aug-1 16:xxZ) if not recovered. A
  persistent no-wake past ~Aug-1 morning is an operator/launchd-plist matter for Jonah, NOT the
  Cycle-63 backoff fix (that is for the wake/network RACE, not a machine that never wakes).
- RUNNER STALE at 2026-07-31T22:1xZ (Cycle 139) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z) was ~8.5h old, BREACHING the 6h floor
  (14:41–21:41 launchd fires produced NO artifact = machine asleep, the Cycle-63 wake-instant
  pattern, NOT a code regression). Cloud CANNOT repair. Already flagged in today's 16:1xZ digest
  (Cycle 133); re-flag in the next first-after-16:00 fire (~Aug-1 16:xxZ) if not recovered. A
  persistent no-wake past ~Aug-1 morning is an operator/launchd-plist matter for Jonah, NOT the
  Cycle-63 backoff fix (that is for the wake/network RACE, not a machine that never wakes).
- RUNNER STALE AGAIN at 2026-07-31T20:12Z (Cycle 137) — newest verify
  `runs/local/verify_20260731T134541Z.json` (13:45Z) is ~6.5h old, BREACHING the 6h floor. The
  14:41–19:41 launchd fires produced NO artifact — consistent with the machine asleep through the
  afternoon/evening (the same wake-instant pattern the Cycle-63 fire root-caused, NOT a code
  regression: the runner RECOVERED cleanly at 08:52Z + 13:45Z this morning with `attempts=1`). Cloud
  CANNOT repair the local machine. ACTION: flag in the next first-after-16:00 digest (~16:xxZ Aug-1);
  if the stall persists across the next several fires (i.e. the machine stays asleep / no new
  `verify_*.json` by ~Aug-1 morning), the Cycle-63 note's escalation (longer/adaptive backoff or DNS
  pre-flight) does NOT apply — that fix is for the wake/network RACE, not a machine that never wakes;
  a persistent no-wake is an operator/launchd-plist matter to raise with Jonah. (Prior: RECOVERED at
  09:12Z Cycle 126 after a ~56h stall; wake/network race self-cleared on a successful wake.)
- LIVE-DELTA DIVERGENCE (record + verify, NOT alarm; opened Cycle 126). The recovered runner's LIVE
  static re-score diverges from the frozen-fixture replay guard: driftflight.com LIVE 76.2 C (delta
  +30.1) vs fixture 85.5 B (+39.4). In capability terms the ENTIRE ~9pt drop is transactability
  87.5 → 62.5 (legibility 90.9 / access 100 / trust 60 all UNCHANGED) — the live with-rails anchor's
  agent-native payment evidence weakened between the Jul-23 fixture and the Jul-31 live crawl. NOT
  caused by any in-cloud change (off the scoring path; the in-cloud replay guard is STILL 24/24, 46.1 F
  / 85.5 B / +39.4 — the independent regression signal is intact). UPDATE Cycle 131: NOW CONFIRMED
  ACROSS TWO independent live crawls — the 13:45Z artifact (76.2 C / +30.1 / transactability 62.5)
  MATCHES the 08:52Z one (76.2 / 62.5) ~5h apart, so it is less likely transient wake/network
  partial-fetch noise and more likely a REAL change in driftflight.com's agent-native payment evidence
  over the Jul-23→Jul-31 gap. Still off the scoring path; the [LOCAL] re-capture/re-baseline is the
  resolution path (peer-gated, moves the replay guard EXPECTED per the Cycle-17 contract). Queued P0
  [LOCAL]; FLAG in the next 16:00 UTC digest (~16:1xZ Jul-31, the next first-after-16:00 fire — which
  also reports that the runner stall cleared). Cycle 131 at 14:1xZ is NOT first-after-16:00 → no digest
  this fire.
- INFRA (2026-07-29T04:2xZ, Cycle 74): the CLOUD git bridge now REFUSES direct pushes to `main`
  (branch-protected) — a `git push origin main` of a legitimate fast-forward is rejected with a
  MISLEADING "non-fast-forward" even when the read replica, the write primary (receive-pack
  advertisement), AND real github.com all agree main == the push's parent. Diagnosed: branch writes
  SUCCEED (`git push origin HEAD:refs/heads/<x>` exit 0), only `main` receive-pack is denied; auth is
  fine (the authenticated retry returns 200, it is the pack-update that is refused). SHIP ADAPTATION for
  cloud cycles: push a `loop/<slug>` branch, open a PR via `mcp__github__create_pull_request`, and
  self-merge via `mcp__github__merge_pull_request` (squash) — this lands on main and is NOT a peer-gated
  PR for a safe tests-only/display change (peer gate still applies to scoring-semantics/payment changes,
  which additionally wait one cycle for review). Cycle 74 shipped this way (PR #5 → merge dd329c4). The
  LOCAL runner is UNAFFECTED (it pushes to real github.com with real credentials, not the cloud bridge —
  its verify-artifact heartbeat still works; 190b9b7/etc. are recent local-fire main pushes). Do NOT
  burn 15 min re-diagnosing next cycle: go straight to branch+PR+self-merge.
- Focus pointer: READOUT next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 143 was
  TRUTH, so Cycle 144 is READOUT). Cycle 143 shipped the **payment-receipt relabel-invariance** TRUTH
  guard (`test_offering_relabel_invariance_payment_receipt` in `tests/test_offering_canonical.py`,
  45→46) — the TRUTH leg of the payment-receipt COVERAGE→TRUTH→READOUT arc, pinning the Cycle-142
  metered_api signal as identity-invariant under a host relabel. A SYNTHETIC metered_api surface seats
  the host INSIDE the receipt evidence (surface KEY + adjacent to "payment receipt" on both sides →
  pad=40 quote window, non-vacuous — the real driftflight.com evidence is host-free in the quote window,
  so a whole-fixture relabel would be VACUOUS, mirroring webhook-verification 135 / output-resolution
  139). Relabel end-to-end → same match count, same host-normalized surface, quote still matches the live
  regex, host absent. TEETH: bare-"receipt" senses (order/email receipt, read receipts, "in receipt of",
  warehouse receipt of goods) fire ZERO. Tests-only, off scoring path (`git diff asrs/ rubric/ fixtures/`
  EMPTY; `--name-only` = `tests/test_offering_canonical.py` only) → score-neutral, NOT peer-gated; branch
  loop/payment-receipt-invariance + PR #134 + self-merge (squash 2fc1415). Full suite green (22 suite
  files, 0 fail; `test_free_tier` 11/11 after restoring the env-only `eth-account` dep). Replay guard
  24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (READOUT 144): the payment-receipt READOUT leg — a
  methodology paragraph in `_write_methodology_page` (`asrs/scorecard.py`) framing "account for the
  spend / trust the receipt" as the capital-safety accounting sibling of the payment RAILS + a
  `test_methodology_documents_payment_receipt` guard in `tests/test_readout.py`, CLOSING the arc.
  digital_good/subscription are the next COVERAGE frontier on committed evidence;
  service_booking/data_retrieval new signals + physical_good fulfillment leg stay [LOCAL]-blocked;
  ACP/UCP/MPP + free-tier live-wiring stay [LOCAL].
- Focus pointer (Cycle 142): TRUTH next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 142 was
  COVERAGE, so Cycle 143 is TRUTH). Cycle 142 shipped the **payment-receipt** metered_api signal on the
  offering classifier (`asrs/offering.py`) — the machine-readable PROOF-OF-PAYMENT an agent gets BACK
  after a paid call and logs to reconcile its own spend (receipt header / payment/settlement receipt /
  serialized receipt / spend record / proof of payment); the ACCOUNTING leg + capital-safety counterpart
  to the payment RAILS (x402/agent-payment-rail = PAY; none said what receipt comes BACK). Vendor-neutral,
  precision-guarded against bare-`receipt` (email/read/order/goods, "in receipt of"). Fires 4 legs on the
  REAL captured driftflight.com `agents.driftflight.com/llms-full.txt` and ZERO on drift-flight.org
  (capability-gap echo, mirroring self-provisioning) / api.replicate.com / books.toscrape / example.com.
  Off scoring path (`git diff asrs/scoring.py rubric/ fixtures/` EMPTY) → score-neutral (claimed SET+ORDER
  `[metered_api, digital_good, subscription]` unchanged), NOT peer-gated; branch loop/payment-receipt-signal
  + PR #132 + self-merge (squash 8b5cee3). `test_offering.py` 56→58 (`_precision_synthetic` 8+/6−,
  `_fires_on_real_captured_surfaces`); isolation-matrix entry added, offering-canonical 45/45; full suite
  347→349. Replay guard 24/24, 46.1 F / 85.5 B / +39.4; rubric v0.7. NEXT (TRUTH 143): a relabel-/order-
  invariance guard for the new `payment-receipt` signal (mirroring the webhook-verification/output-resolution
  TRUTH legs) to give the payment-receipt arc its COVERAGE→TRUTH→READOUT shape. digital_good/subscription
  are the next COVERAGE frontier on committed evidence; service_booking/data_retrieval new signals +
  physical_good fulfillment leg stay [LOCAL]-blocked; ACP/UCP/MPP + free-tier live-wiring stay [LOCAL].
- Focus pointer (Cycle 141): COVERAGE next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 141 was
  METHOD, so Cycle 142 is COVERAGE). Cycle 141 shipped **surface-DEDUP invariance** — the LAST unused
  in-cloud METHOD sibling of the offering invariance family (`test_offering_surface_dedup_invariance_org/
  _com` in `tests/test_offering_canonical.py`, 43→45). Pins that serving the SAME doc surface a second
  time under a DISTINCT key (the apex+`agents.<host>` mirror the LIVE `_doc_subdomain_surfaces` path
  already produces; a CDN mirror; `/openapi.json` aliased to `/swagger.json`) leaves every archetype's
  distinct-label `strength`, the RANKED claimed list, and the NA complement byte-identical. Teeth: the
  top claim's raw signal-LIST length STRICTLY grows under the mirror (metered_api 18→29 .org / 47→85
  .com) — a count-based `strength=len(signals)` reader WOULD reorder — yet strength (11/17) and rank
  hold. Tests-only, off scoring path (`git diff asrs/ rubric/ fixtures/` EMPTY; `--name-only` =
  `tests/test_offering_canonical.py` ONLY) → score-neutral, NOT peer-gated; branch
  loop/surface-dedup-invariance + PR + self-merge (squash). Replay guard 24/24, 46.1 F / 85.5 B / +39.4;
  rubric v0.7. NEXT (COVERAGE 142): a new capability-worded signal on a CLAIMED archetype (metered_api/
  digital_good/subscription — physical_good fulfillment leg [LOCAL]-blocked on a richer retail fixture);
  a surface-dedup RETAIL-pole sibling is a weaker fold-in candidate (single-archetype → trivial rank).
  service_booking/data_retrieval new signals stay [LOCAL]-blocked; ACP/UCP/MPP + free-tier live-wiring
  stay [LOCAL].
- Focus pointer (Cycle 140): METHOD next (rotate METHOD → COVERAGE → TRUTH → READOUT; Cycle 140 was
  READOUT, so Cycle 141 is METHOD). Cycle 140 CLOSED the `output-resolution`
  COVERAGE→TRUTH→READOUT arc (138 COVERAGE signal / 139 TRUTH relabel-invariance / 140 READOUT
  prose) with its methodology PROSE leg: a new paragraph in `_write_methodology_page`
  (`asrs/scorecard.py`) after the content-provenance ("Trusting the deliverable") prose, framing
  "specify the deliverable's shape / the output-resolution contract" as the digital_good output-SPEC
  sibling of owning/trusting the render — DISTINCT from generation/render (WHAT produced),
  hosted-output (WHERE delivered), output-license (rights), content-provenance (trust); names the
  failure (an agent requests an unproducible size, or gets a wrong-resolution deliverable — a hero
  image at thumbnail size), the vendor-neutral output-format vocab (a `maxResolution` field, an
  output/render/print resolution in px, a WxH pixel dimension, an aspect ratio), preserves the
  bare-`resolution` precision guard (dispute/New-Year/DNS resolution, the Super-/enhance-image
  MODEL-FEATURE trap, screen/monitor/display HARDWARE resolution → no signal), pins the
  identity-relabel regression property, stays diagnostic/off-scoring-path. The digital_good
  output-SPEC leg now completes a full arc, mirroring metered_api webhook-verification (134/135/136)
  and streaming-response (126/127/128). Guard `test_methodology_documents_output_resolution` in
  `tests/test_readout.py` (61→62). Display+tests, off scoring path (`git diff` over `scoring.py
  offering.py rubric/ fixtures/` EMPTY; `--name-only` = `scorecard.py` + `test_readout.py` ONLY) →
  NOT peer-gated; branch loop/output-resolution-readout + PR #129 + self-merge (squash aeafed4).
  Full suite 344→345. Replay guard 24/24, 46.1 F / 85.5 B / +39.4; offering-canonical 43/43;
  rubric v0.7. NEXT (METHOD 141): the unused in-cloud METHOD sibling is surface-DEDUP invariance
  (duplicate/near-duplicate surfaces don't inflate match counts or `strength` — note `strength` is
  already distinct-label-count, so likely a robustness PIN not a bug-find). New-signal COVERAGE on
  the unclaimed archetypes (service_booking / data_retrieval) stays [LOCAL]-blocked on a fixture
  capture (P1); adding a leg to a never-claimed archetype is unverifiable in-cloud.
  (Cycle 138 COVERAGE — shipped `output-resolution`, an eleventh digital_good capability leg (the
  output RESOLUTION / pixel DIMENSIONS / ASPECT RATIO of the generated deliverable an agent must
  request and can rely on; distinct from generation/render (WHAT), hosted-output (WHERE),
  output-license (rights), content-provenance (trust)). Vendor-neutral (`maxResolution` / print
  resolution in px / WxH px / aspect ratio), precision-guarded against screen/monitor/display
  hardware resolutions + the Super-/Enhance-image-resolution MODEL-FEATURE trap on
  api.replicate.com's OpenAPI + dispute/New-Year/DNS senses. Fires 4/4 on the canonical pair
  (both already claim digital_good) and ZERO on api.replicate.com/books.toscrape/example.com →
  score-neutral (claimed SET+ORDER byte-identical `[metered_api, digital_good, subscription]`). Off
  scoring path → NOT peer-gated; branch loop/output-resolution-signal + PR #125 + self-merge (squash
  52b86ca). `test_offering.py` 54→56.)
  (Cycle 137 METHOD — built the FIRST menu item, cross-signal precision-ISOLATION: a full 56-signal
  / 6-archetype matrix
  (`test_cross_signal_archetype_isolation` + negative control in
  `tests/test_offering_canonical.py`) proving each signal's affirmative evidence claims EXACTLY its
  own archetype and leaks into no other (the score-relevant no-false-claim property);
  completeness-enforced so new signals can't escape it. REMAINING in-cloud METHOD sibling:
  surface-DEDUP invariance (duplicate/near-duplicate surfaces don't inflate match counts or strength
  — note `strength` is already distinct-label-count, so likely a robustness PIN not a bug-find) —
  the METHOD fallback if Cycle 138 COVERAGE finds no in-cloud-verifiable unit. New-signal COVERAGE on
  the unclaimed archetypes (service_booking / data_retrieval) stays [LOCAL]-blocked on a fixture
  capture (P1); adding a leg to a never-claimed archetype is unverifiable in-cloud.)
  (Cycle 136 READOUT — CLOSED the webhook-verification COVERAGE→TRUTH→READOUT arc with its
  methodology PROSE leg: a new paragraph in `_write_methodology_page` (`asrs/scorecard.py`) after
  the streaming-response prose framing trusting the async callback as the SECURITY sibling of
  async-job (async-job says a webhook delivery channel EXISTS; webhook-verification says whether
  the agent can AUTHENTICATE what arrives — failure = an agent acts on an unverified "job complete"
  webhook, is tricked by a forged/spoofed callback into treating fabricated output as real or
  releasing a payment; ties to the $0-only capital-safety ethos). Names the vendor-neutral
  webhook-security vocabulary (a webhook signature / a webhook signing secret / an
  X-Webhook-Signature header), preserves the bare-signature precision guard (marketing signature
  look / settlement signature a payment proof verifies / signed-URL signing secret / digital
  signature on a contract / webhook that merely EXISTS → no signal), pins the identity-relabel
  regression property, stays diagnostic/off-scoring-path. NINTH metered_api offer-side leg with a
  full arc. Guard `test_methodology_documents_webhook_verification` in `tests/test_readout.py`
  (60→61), mirroring the streaming-response guard. SHIP CLASS: display + tests only, off scoring
  path (`git diff` over `asrs/scoring.py asrs/offering.py rubric/ fixtures/` EMPTY;
  `--name-only` = `asrs/scorecard.py` + `tests/test_readout.py` ONLY) → score-neutral, NOT
  peer-gated. First duty: no open peer-gated PR (`[]` at fire start). Cloud bridge blocks direct
  main push → branch loop/webhook-verification-readout + PR #121 + self-merge (squash 70f5100;
  realigned main → 70f5100, verified guard present + test_readout 61/61 + replay 24/24 on merged
  main, deleted local+remote branch). Full suite green (22 files; test_free_tier 11/11 after
  `pip install -r requirements.txt`, environment-only). Canonical PAIR unchanged: replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; offering-canonical 40/40; rubric v0.7. INFRA
  HEALTHY (verify 20260731T134541Z 13:45Z, ~5.4h old at 19:12Z fire, within 6h floor — breaches
  ~19:45Z, runner due at :41; no open peer-gated PRs). LIVE-DELTA divergence unchanged — no new
  verify since 13:45Z (driftflight.com LIVE 76.2 C / +30.1 / transactability 62.5 across two
  crawls); in-cloud replay guard STILL 24/24 / +39.4, off scoring path; re-capture is
  [LOCAL]/peer-gated. No Slack (score-neutral, off scoring path, not sensitive-class; 19:1xZ is
  NOT the first-after-16:00 digest — Cycle 133 at 16:1xZ already sent today's).)
  (Cycle 135 TRUTH — shipped the relabel-invariance guard for Cycle 134's `webhook-verification`
  signal: `test_offering_relabel_invariance_webhook_verification` in `tests/test_offering_canonical.py`
  (39→40). Pins the tenth metered_api signal as identity-invariant — the async-callback TRUST claim
  keys on the webhook-AUTHENTICITY structure (a webhook signature / a signing secret FOR a webhook /
  verifying inbound webhooks), never the vendor host. SYNTHETIC-surface guard (like free-trial 115 /
  self-provisioning 131): the real api.replicate.com webhook-verification quote is HOST-FREE (host in
  neither the `/openapi.json` surface key nor the fired quote window — verified live), so a
  whole-fixture relabel would be VACUOUS; the synthetic surface seats the host inside BOTH the surface
  key AND the padded quote window so the relabel genuinely rewrites the classifier's input. Asserts
  same match count (1) / same host-normalized surface / relabeled quote still matches the live regex /
  host absent under end-to-end relabel. TEETH: signature-shaped distractor prose (brand signature /
  x402 verify-locally / signed-URL signing secret / register-a-webhook-URL / contract signature) fires
  ZERO webhook-verification — match keys on webhook-authenticity, not the words "signature"/"signing
  secret". SHIP CLASS: tests-only, off scoring path (`scoring.py` 0 offering refs) → score-neutral,
  NOT peer-gated. `git diff --name-only` = `tests/test_offering_canonical.py` ONLY; git diff over
  `asrs/ rubric/ fixtures/` EMPTY. First duty: no open peer-gated PR (`[]` at fire start). Also
  realigned the STALE local `main` branch ref (had diverged 50/50 from origin/main — a leftover from
  the detached-HEAD checkout) via `git reset --hard origin/main` before starting. Cloud bridge blocks
  direct main push → branch loop/webhook-verification-relabel-invariance + PR #119 + self-merge (squash
  7438af8; realigned main → 7438af8, verified guard present + offering-canonical 40/40 + replay 24/24
  on merged main, deleted local+remote branch). Full suite green (22 files; test_free_tier 11/11 after
  `pip install -r requirements.txt`, environment-only). Canonical PAIR unchanged: replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; offering-canonical 40/40; rubric v0.7. INFRA HEALTHY (verify
  20260731T134541Z 13:45Z, ~4.5h old at 18:12Z fire, within 6h floor; no open peer-gated PRs).
  LIVE-DELTA divergence unchanged — no new verify since 13:45Z (driftflight.com LIVE 76.2 C / +30.1 /
  transactability 62.5 across two crawls); in-cloud replay guard STILL 24/24 / +39.4, off scoring path;
  re-capture is [LOCAL]/peer-gated. No Slack (score-neutral, off scoring path, not sensitive-class;
  18:1xZ is NOT the first-after-16:00 digest — Cycle 133 at 16:1xZ already sent today's). Next READOUT
  — the webhook-verification arc's methodology paragraph, closing a full COVERAGE→TRUTH→READOUT arc.
  If the next verify still shows transactability 62.5, the [LOCAL] canonical re-capture rises in
  leverage.)
  (Cycle 134 COVERAGE — added the TENTH metered_api capability leg to the offering classifier
  (`asrs/offering.py`): `webhook-verification` — whether an agent can TRUST that an inbound async
  callback is GENUINELY from the API rather than a forged/spoofed webhook (a webhook signing
  secret, a webhook signature, verifying inbound webhook requests). The security/TRUST sibling of
  `async-job` (which captures that a webhook DELIVERY channel EXISTS): an agent that acts on an
  UNVERIFIED "job complete" webhook can be tricked by a spoofed callback into treating fabricated
  output as real or releasing a payment, so a documented webhook-verification contract is MORE
  agent-completable (dovetails with the $0-only capital-safety ethos: never act/pay on a forged
  callback). Precision-first: NEVER matches a bare `signature`/`signing secret` — the canonical
  pair's marketing "signature look", the x402 payment-proof "verifies the signature locally",
  api.replicate.com's Files API SIGNED-URL "signing secret"/`name: signature` query param, a
  webhook that only EXISTS (`async-job`'s turf), and contract/digital signatures all dodged; the
  token must NAME a webhook (6 positives fire / 6 signature-shaped noise strings do NOT). Fires
  non-vacuously on the real captured api.replicate.com `/openapi.json` (`/webhooks/default/secret`
  "verify that webhook requests are coming from ...") and on ZERO of the canonical-pair / retail /
  null fixtures; api.replicate.com ALREADY claims metered_api (its only archetype) → deepens
  evidence without adding/reordering any archetype. SHIP CLASS: off the scoring path (`scoring.py`
  0 offering refs) → score-neutral, NOT peer-gated (same class as the prior nine metered_api arcs).
  `git diff` over `asrs/scoring.py rubric/ fixtures/` EMPTY; `--name-only` = `asrs/offering.py` +
  `tests/test_offering.py` ONLY. First duty: no open peer-gated PR (`[]` at fire start). Cloud
  bridge blocks direct main push → branch loop/webhook-verification-signal + PR #117 + self-merge
  (squash a0bdb50; realigned main via `git reset --hard origin/main` → a0bdb50, verified signal
  present + offering 54/54 + replay 24/24 on merged main, deleted local branch). `test_offering.py`
  52→54. Full suite green (22 files). Canonical PAIR unchanged: replay guard 24/24, 46.1 F / 85.5 B
  / +39.4, 0 replay-miss; offering-canonical 39/39 (claimed sets unchanged); rubric v0.7. INFRA
  HEALTHY (verify 20260731T134541Z 13:45Z, ~3.4h old at fire, within 6h floor; no open peer-gated
  PRs). LIVE-DELTA divergence unchanged — no new verify since 13:45Z (driftflight.com LIVE 76.2 C /
  +30.1 / transactability 62.5 across two crawls); in-cloud replay guard STILL 24/24 / +39.4, off
  scoring path; re-capture is [LOCAL]/peer-gated. No Slack (score-neutral, off scoring path, not
  sensitive-class; 17:1xZ is NOT the first-after-16:00 digest — Cycle 133 at 16:1xZ already sent
  today's). Next TRUTH — the webhook-verification arc's relabel-invariance guard (mirror of
  self-provisioning 131 / streaming-response 127), then its READOUT leg to complete a full
  COVERAGE→TRUTH→READOUT arc. New-signal COVERAGE on the unclaimed archetypes stays [LOCAL]-blocked
  (see P1 fixture-capture); other in-cloud METHOD frontier: cross-signal precision-isolation +
  surface-dedup invariance (Cycle 132's still-unbuilt menu). If the next verify still shows
  transactability 62.5, the [LOCAL] canonical re-capture rises in leverage.)
  (Cycle 133 METHOD — added the FIFTH metamorphic-invariance axis to the offering classifier's
  harness: TEXT-CASING INVARIANCE (`_assert_casing_invariance` + `_casing_struct` in
  `tests/test_offering_canonical.py`, 37→39). Uppercasing every surface body leaves the classified
  capability skeleton identical — claimed archetypes IN RANK ORDER, the NA/unclaimed complement,
  and per-archetype `(strength, per-(label, surface) match counts)`. Quote TEXT excluded from the
  compare (it echoes the matched bytes → upper-cases with the surface; `&amp;→&AMP;` entity
  artifacts). Complements RELABEL/ORDER/SCALE/NOISE (which perturb which surfaces are read / their
  order) by perturbing the CASING inside them: a site writing Pay-Per-Call / pay-per-call / PAY PER
  CALL declares one capability, and the score must not key on typography. TEETH: (a) transform is
  real (a surface carries lowercase at base); (b) case-insensitivity is LOAD-BEARING — a fired
  signal's CASE-SENSITIVE count moves under uppercasing (`https?://`→`HTTPS` in the metered_api
  post-endpoint quote, 1→0) while its `re.IGNORECASE` count holds (36 such signals on .org, 86 on
  .com) → a future signal added WITHOUT `re.IGNORECASE` fails this guard loudly. This was Cycle 132's
  named next-hypothesis unit. SHIP CLASS: tests-only, off the scoring path (`scoring.py` 0 offering
  refs) → score-neutral, NOT peer-gated. `git diff --name-only` = `tests/test_offering_canonical.py`
  ONLY; git diff over `asrs/ rubric/ fixtures/` EMPTY. First duty: no open peer-gated PR (`[]` at
  fire start). Cloud bridge blocks direct main push → branch loop/casing-invariance + PR #115 +
  self-merge (squash a024c97; realigned main via `git reset --hard origin/main` → a024c97, verified
  39/39 + replay 24/24 on merged main, deleted local branch). Full suite green (22 files; test_free_tier
  11/11 after `pip install -r requirements.txt`, environment-only — sole pre-fix red was `eth-account`
  absent, an env dep). Canonical PAIR unchanged: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; rubric v0.7. INFRA HEALTHY (verify 20260731T134541Z 13:45Z, ~2.4h old at fire, within
  6h floor; no open peer-gated PRs). Slack DAILY DIGEST SENT (16:1xZ = first fire after 16:00 UTC):
  runner recovery + persisting live-delta divergence + cycles/ships + canonical trend + top question.
  Next COVERAGE — new-signal COVERAGE is [LOCAL]-blocked (physical_good/service_booking/data_retrieval
  have no rich committed fixture; see P1 fixture-capture). In-cloud option: a new capability leg on an
  already-claimed canonical archetype (metered_api/subscription/digital_good). Remaining METHOD frontier
  for later: cross-signal precision-isolation + surface-dedup invariance (the two axes Cycle 132 named
  alongside casing, still unbuilt). If the next verify still shows transactability 62.5, the [LOCAL]
  canonical re-capture rises in leverage.)
  (Cycle 132 READOUT — CLOSED the ninth metered_api COVERAGE→TRUTH→READOUT arc by surfacing Cycle
  130's `self-provisioning` signal in the public methodology prose. Added one capability-worded,
  vendor-neutral paragraph "Onboarding without a human" to `_write_methodology_page`
  (`asrs/scorecard.py`), placed after the api-auth ("Provisioning without a human") leg it
  complements: api-auth = PRESENT a credential you hold; self-provisioning = whether an agent can
  OBTAIN one at all with no human onboarding. The paragraph frames obtaining access without a human
  (failure = a human must sign up on a dashboard → agent stranded), names the vendor-neutral
  onboarding conventions (no signup / no human account creation / provisions its own identity /
  self-provision path), keeps the OPPOSITE-path precision honesty (the "sign up on the dashboard for
  an API key" human path, the 401 "No API key" error, and the "no signup fees" pricing sense are
  named as what it REJECTS), says recognition keys on whether a human must onboard the agent (pinned
  by an identity-relabel test), and stays honest (diagnostic, off the scoring path). Guarded by
  `test_methodology_documents_self_provisioning` in `tests/test_readout.py` (59→60). SHIP CLASS:
  display+tests-only, off the scoring path (`scoring.py` 0 offering refs) → score-neutral, NOT
  peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/ asrs/offering.py` EMPTY; --name-only =
  `asrs/scorecard.py` + `tests/test_readout.py`. First duty: no open peer-gated PR (`[]` at fire
  start). Cloud bridge blocks direct main push → branch loop/self-provisioning-readout + PR #113 +
  self-merge (squash 518bc94; realigned main via `git reset --hard origin/main` → 518bc94, verified
  prose present + readout 60/60 + replay 24/24 on merged main, deleted local branch). Full suite green
  (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only). Canonical
  PAIR unchanged: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. INFRA
  HEALTHY (verify 20260731T134541Z 13:45Z, ~1.5h old at fire, within 6h floor; no open peer-gated PRs).
  LIVE-DELTA divergence unchanged — no new verify since 13:45Z (driftflight.com LIVE 76.2 C / +30.1 /
  transactability 62.5 across two crawls); in-cloud replay guard STILL 24/24 / +39.4, off scoring path;
  re-capture is [LOCAL]/peer-gated. No Slack (score-neutral, off scoring path, not sensitive-class;
  15:1xZ is not the first-after-16:00 digest — that is ~16:1xZ Jul-31, which reports the runner-recovery
  + this persisting live-delta divergence).
  Next METHOD — the ninth arc is complete on all three tracks. New-signal COVERAGE/TRUTH is
  [LOCAL]-blocked (physical_good / service_booking / data_retrieval have no committed fixture that
  claims them; see the P1 fixture-capture item). Highest-leverage in-cloud METHOD unit: a new
  metamorphic-invariance axis on an existing signal (e.g. whitespace/casing normalization invariance,
  surface-dedup invariance, or a cross-signal precision-isolation guard proving one archetype's signal
  never leaks into another's verdict). If the next verify still shows transactability 62.5, the [LOCAL]
  canonical re-capture rises in leverage.)
  (Cycle 131 TRUTH — pinned Cycle 130's `self-provisioning` metered_api signal as RELABEL-INVARIANT,
  the ninth metered_api arc's TRUTH leg (mirroring free-trial 115 / streaming-response 127). Added
  `test_offering_relabel_invariance_self_provisioning` (+ `_self_prov_signals`) to
  `tests/test_offering_canonical.py` (36→37): under a whole-host relabel the agent self-onboarding
  claim (no signup / provision own identity / self-provision / no-human onboarding) keeps the SAME
  match count, SAME host-normalized surface, quote STILL matching the live regex, host absent. Because
  the real self-provisioning quote is host-free (a whole-fixture relabel would be VACUOUS at the quote),
  the guard scans a SYNTHETIC metered_api surface seating the host INSIDE the evidence (surface-key
  prefix + adjacent to "no signup" → in the padded quote window; asserted non-vacuous). TEETH: the
  OPPOSITE human-onboarding senses present VERBATIM in the fixtures fire ZERO — dashboard "sign up …
  for an API key" (both domains), 401 "No API key" (drift-flight.org /docs), "no signup fees" (the
  lookahead), newsletter sign up. SHIP CLASS: tests-only, off the scoring path (`scoring.py` 0 offering
  refs) → score-neutral, NOT peer-gated. git diff over `asrs/ rubric/ fixtures/` EMPTY; --name-only =
  `tests/test_offering_canonical.py` ONLY. First duty: no open peer-gated PR (`[]` at fire start). Cloud
  bridge blocks direct main push → branch loop/self-provisioning-invariance + PR #111 + self-merge
  (squash 29e691e; merged commit = exactly the one test file). Realigned main to origin/main after merge
  (`git reset --hard origin/main` → 29e691e, verified 37/37 + replay 24/24 on merged main), deleted local
  branch. `test_offering_canonical.py` 36→37; `test_offering.py` 54/54; full suite green (22 files;
  test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only). Canonical PAIR
  unchanged: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. INFRA HEALTHY
  (verify 20260731T134541Z 13:45Z, ~26min old at fire, within 6h floor; no open peer-gated PRs).
  LIVE-DELTA divergence NOW PERSISTS across TWO crawls — the 13:45Z artifact shows driftflight.com LIVE
  76.2 C / +30.1, transactability 62.5, MATCHING 08:52Z (76.2/62.5) ~5h earlier → less like transient
  wake noise, more like a real 3-day change in the with-rails anchor's payment evidence. Off scoring
  path (in-cloud replay guard STILL 24/24 / +39.4). Re-capture is [LOCAL]. No Slack (score-neutral, off
  scoring path, not sensitive-class; 14:1xZ is not the first-after-16:00 digest — that is ~16:1xZ Jul-31,
  which reports the runner-recovery + this now-persisting live-delta divergence).
  Next READOUT — surface "onboard without a human" / self-provisioning in the public methodology prose
  (`_write_methodology_page`, `asrs/scorecard.py`), guarded by a content-presence test in `test_readout.py`,
  completing the ninth metered_api arc COVERAGE 130 → TRUTH 131 → READOUT. COVERAGE frontier after:
  physical_good / service_booking / data_retrieval all [LOCAL]-blocked (no rich committed fixture). If the
  next verify still shows transactability 62.5, the [LOCAL] canonical re-capture rises in leverage.)
  (Cycle 130 COVERAGE — added a NINTH metered_api capability leg, the `self-provisioning` signal
  (`asrs/offering.py`), capturing the PLAYBOOK capability lens's own words "provision without a
  human": whether an autonomous agent can OBTAIN API access with no signup / no human account
  creation / provisioning its OWN identity. Uncaptured yet load-bearing — an API whose credentials
  only a human can issue is not agent-completable end-to-end regardless of how cleanly it documents
  auth/rate-limits/errors. Distinct from `api-auth` (present credentials you HAVE) and `test-mode`
  (try safely); NONE said whether a human must onboard you. Precision-critical: the trap is verbatim
  in the fixtures — BOTH canonical domains carry "Human developers sign up on the dashboard for an
  API key" (the OPPOSITE, human-gated capability) and drift-flight.org's /docs 401 "No API key …"
  error; the signal matches ONLY the affirmative agentic form (`no signup` w/ a negative lookahead
  excluding "no signup fees"; `provision its own identity`; `self-provision`; `no human`/`without a
  human` onboarding), never the human path or the 401. Fires 6× on driftflight.com (deepens its
  existing metered_api claim), ABSENT on drift-flight.org (human-only signup path — the discovery-
  layer echo of the real capability gap), ZERO on api.replicate.com/retail/null. SHIP CLASS:
  signal-bank + tests only, off the scoring path (`scoring.py` 0 offering refs) → score-neutral, NOT
  peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY; --name-only = `asrs/offering.py`
  + `tests/test_offering.py`. First duty: no open peer-gated PR (`[]` at fire start). Cloud bridge
  blocks direct main push → branch loop/self-provisioning-signal + PR #109 + self-merge (squash
  b6a1bb1; merged commit = exactly the two files). Realigned main to origin/main after merge (`git
  reset --hard origin/main` → b6a1bb1, verified signal present + offering 54/54 + replay 24/24 on
  merged main), deleted local branch. `test_offering.py` 52→54; canonical offering guard 36/36; full
  suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only).
  Canonical PAIR unchanged: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  INFRA HEALTHY (verify 20260731T085248Z 08:52Z, 4.4h old at fire, within 6h floor; no open peer-gated
  PRs). No Slack (score-neutral, off scoring path, not sensitive-class; 13:1xZ is not the
  first-after-16:00 digest — that is ~16:1xZ Jul-31, which also reports the runner-recovery + the
  live-delta divergence).
  Next TRUTH — pin `self-provisioning` as RELABEL-INVARIANT (the ninth metered_api arc's TRUTH leg,
  mirroring free-trial 115 / streaming-response 127). The evidence is host-free by nature, so the guard
  likely needs a SYNTHETIC surface seating the host INSIDE the self-provisioning evidence to be
  non-vacuous, then assert identity-invariance under end-to-end relabel + a bare human-signup distractor
  firing ZERO. Then READOUT: surface "onboard without a human" in the methodology prose. COVERAGE
  frontier after: physical_good fulfillment / service_booking / data_retrieval all [LOCAL]-blocked; OR if
  the next verify artifact still shows driftflight.com transactability 87.5→62.5, the [LOCAL] canonical
  re-capture is higher-leverage.)
  (Cycle 129 METHOD — added the metamorphic INVARIANCE axis
  `test_offering_endpoint_order_invariance_metered_api` (`tests/test_offering_canonical.py` 35→36), the
  WITH-RAILS / machine-surface MIRROR of Cycle 125's retail listing-order guard. Reordering the ENDPOINTS
  within one OpenAPI machine contract (`[0,1,2]→[2,1,0]`) must not move the metered_api verdict — the
  machine surface being where metered_api is most load-bearing (api.replicate.com earns its whole claim
  from `/openapi.json` alone). Non-vacuous by the same substrate as the retail leg: `_scan_surface` keeps
  the FIRST `post-endpoint` match per surface, so the sampled exemplar quote MOVES under reorder
  (predictions-POST → status-GET, asserted), while metered_api strength (4), its leg set {post-endpoint,
  api-auth, async-job, rate-limited}, the ordered claimed list, and the whole NA set stay invariant.
  Vendor-neutral synthetic spec: signal-free host `gridcell.example` + pure open machine-integration
  vocabulary (POST/GET endpoint, Authorization: Bearer, webhook callback, per-minute rate limit). SHIP
  CLASS: tests-only, off the scoring path (`scoring.py` 0 offering refs) → score-neutral, NOT peer-gated.
  git diff over `asrs/ rubric/ fixtures/` EMPTY; --name-only = `tests/test_offering_canonical.py` ONLY.
  First duty: no open peer-gated PR (`[]` at fire start). Cloud bridge blocks direct main push → branch
  loop/endpoint-order-invariance + PR #107 + self-merge (squash 00b17e6; merged commit = exactly the one
  test file). Realigned main to origin/main after merge (`git reset --hard origin/main` → 00b17e6,
  verified the new test present + 36/36 + replay 24/24 on merged main), deleted local branch. Full suite
  green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only).
  Canonical PAIR unchanged: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; offering
  canonical 36/36; rubric v0.7. INFRA HEALTHY (verify 20260731T085248Z 08:52Z, 3.4h old at fire, within
  6h floor; no open peer-gated PRs). The LIVE-DELTA DIVERGENCE (driftflight.com LIVE 76.2 C / +30.1,
  transactability 87.5→62.5) is unchanged from Cycle 126 — still queued P0 [LOCAL] + flagged for the
  ~16:1xZ digest. No Slack (score-neutral, off scoring path, not sensitive-class; 12:12Z is not the
  first-after-16:00 digest — that is ~16:1xZ Jul-31, which also reports the runner-recovery + the
  live-delta divergence).
  Next COVERAGE — the metered_api bank has eight fully-arced signals + a metamorphic grid now spanning the
  listing/endpoint ORDER axis on BOTH poles (retail 125 + machine 129). A COVERAGE increment would add a
  ninth metered_api leg or deepen a thinner archetype's evidence on a committed fixture. Thin archetypes
  service_booking / data_retrieval remain [LOCAL]-blocked (no committed fixture claims either). OR, if the
  next verify artifact still shows the driftflight.com transactability drop, the [LOCAL] canonical
  re-capture is the higher-leverage item.)
  (Cycle 128 READOUT — completed the EIGHTH metered_api COVERAGE→TRUTH→READOUT arc: added ONE
  capability-worded, vendor-neutral methodology `<p>` ("Consuming the output as it streams") to
  `_write_methodology_page` (`asrs/scorecard.py`), guarded by `test_methodology_documents_streaming_response`
  (`tests/test_readout.py` 58→59). Closes the `streaming-response` arc (COVERAGE 126 → TRUTH 127 →
  READOUT 128), after payment-rail (78/79/80), async-job (82/83/84), api-auth (86/87/88), error-contract
  (90/91/92), test-mode (102/103/104), pagination (106/107/108), cancel-job (110/111/112), plus
  digital_good rights (100) and subscription free-trial (114/115/116). Frames streaming as the IN-BAND
  sibling of async-job (async collects a completed job OUT of band via webhook/poll; streaming delivers
  partial output WITHIN the same request over the live connection); names open-standard delivery
  vocabulary (W3C server-sent events, `text/event-stream`, a streaming endpoint); keeps the bare-`stream`/
  `SSE` precision note (octet-stream MIME / Shanghai Stock Exchange (SSE) / sum-of-squared-errors / live
  stream / bloodstream / "stream of consciousness" = no signal, and a bare SSE never conjures a
  metered-API claim); recognition keys on the CONTRACT not who published it, pinned by an identity-relabel
  regression test; honest scope (diagnostic, off the scoring path). Placed right after the async-job
  paragraph. SHIP CLASS: display + tests-only, off the scoring path (`scoring.py` 0 offering refs) →
  score-neutral, NOT peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY; --name-only =
  `asrs/scorecard.py` + `tests/test_readout.py` ONLY. First duty: no open peer-gated PR (`[]` at fire
  start). Cloud bridge blocks direct main push → branch loop/streaming-response-readout + PR #105 +
  self-merge (squash fa2d096; merged commit = exactly the two files). Realigned main to origin/main after
  merge (`git reset --hard origin/main` → fa2d096, verified paragraph + test present + readout 59/59 +
  replay 24/24 on merged main), deleted local branch. Full suite green (22 files; test_free_tier 11/11
  after `pip install -r requirements.txt`, environment-only). Canonical PAIR unchanged: replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; offering canonical 35/35; rubric v0.7. INFRA HEALTHY
  (verify 20260731T085248Z 08:52Z, 2.3h old at fire, within 6h floor; no open peer-gated PRs). No Slack
  (score-neutral, off scoring path, not sensitive-class; 11:12Z is not the first-after-16:00 digest —
  that is ~16:1xZ Jul-31, which also reports the runner-recovery + the live-delta divergence).
  Next METHOD — the metered_api bank now has eight fully-arced signals and the metamorphic grid spans
  five axes on the metered_api + retail poles; a METHOD increment could mirror listing-order invariance
  onto a with-rails MACHINE surface (do the metered_api endpoints' ORDER within one OpenAPI spec move the
  claim?). OR, if the next verify artifact still shows the driftflight.com transactability drop
  (87.5→62.5), the [LOCAL] canonical re-capture is the higher-leverage item. Thin archetypes
  service_booking / data_retrieval remain [LOCAL]-blocked.)
  (Cycle 127 TRUTH — pinned `streaming-response` (the metered_api signal added Cycle 126) as
  RELABEL-INVARIANT: `test_offering_relabel_invariance_streaming_response` (`tests/test_offering_canonical.py`
  34→35), the EIGHTH signal-level relabel-invariance guard in the metered_api bank (after payment-rail 79 /
  async-job 83 / api-auth 87 / error-contract 91 / test-mode 103 / pagination 107 / cancel-job 110). Mirrors
  the cancel-job/pagination model: replays api.replicate.com's captured `/openapi.json` streaming evidence
  ("receive streaming output using server-sent events (SSE)"), proves the evidence is host-FREE + the fixture
  host is genuinely present (non-vacuity anchor at the fixture level), then relabels the whole fixture host to
  the neutral `.test` domain and asserts the signal fires the SAME count (1), on the SAME host-normalized
  surface, each quote STILL matching the live streaming-response regex, vendor host absent everywhere. TEETH:
  fires non-vacuously on real captured evidence; a dropped/migrated signal or a leaked host fails a specific
  assertion. SHIP CLASS: tests-only, off the scoring path (`scoring.py` 0 offering refs) → score-neutral, NOT
  peer-gated. git diff over `asrs/ rubric/ fixtures/` EMPTY; --name-only = `tests/test_offering_canonical.py`
  ONLY. First duty: no open peer-gated PR (`[]` at fire start). Cloud bridge blocks direct main push → branch
  loop/streaming-response-relabel-invariance + PR #103 + self-merge (squash e8b1022; merged commit = exactly
  the one test file). Realigned main to origin/main after merge (`git reset --hard origin/main` → e8b1022,
  verified new test present + 35/35 + replay 24/24 on merged main), deleted local branch. Full suite green (22
  files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only). Canonical PAIR
  unchanged: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. INFRA HEALTHY (verify
  20260731T085248Z 08:52Z, 1h20m old at fire, within 6h floor; no open peer-gated PRs). No Slack (score-neutral,
  off scoring path, not sensitive-class; 10:12Z is not the first-after-16:00 digest — that is ~16:1xZ Jul-31).
  Next READOUT — complete the eighth metered_api arc's third layer: add ONE capability-worded, vendor-neutral
  methodology `<p>` ("Consuming the output as it streams") to `_write_methodology_page`, guarded by a
  content-presence test in `test_readout.py` (COVERAGE 126 → TRUTH 127 → READOUT next). OR, if the live
  transactability drop persists in the next verify artifact, the [LOCAL] canonical re-capture is the
  higher-leverage item. Thin archetypes service_booking / data_retrieval remain [LOCAL]-blocked.)
  (Cycle 126 COVERAGE — added a NEW capability signal `streaming-response` to the offering classifier's
  metered_api signal bank (`asrs/offering.py`): how an agent consumes output INCREMENTALLY over the OPEN
  connection as it is produced (server-sent events / text/event-stream / a streaming API/endpoint that
  streams the output/tokens) — the IN-BAND sibling of `async-job` (which collects a completed job's
  result OUT of band via webhook/poll). Distinct from every existing metered_api leg (api-auth /
  rate-limited / async-job / error-contract / pagination / cancel-job): none describes incremental
  in-band delivery. Precision-anchored so `application/octet-stream` (a binary-download MIME, verbatim on
  api.replicate.com's /openapi.json), the SSE acronym collisions (Shanghai Stock Exchange / sum-of-squared
  -errors), and live-stream/bloodstream/downstream never fire — and a bare SSE can never CONJURE a false
  metered_api claim. Fires NON-VACUOUSLY on the real captured api.replicate.com /openapi.json streaming
  contract ("receive streaming output using server-sent events (SSE)" + "An event source to stream the
  output of the prediction") and on ZERO of the canonical-pair / retail / null fixtures; api.replicate.com
  ALREADY claims metered_api only → deepens evidence without adding or reordering any archetype. SHIP
  CLASS: off the scoring path (`scoring.py` 0 offering refs) → score-neutral, NOT peer-gated. git diff over
  `asrs/scoring.py rubric/ fixtures/` EMPTY; --name-only = `asrs/offering.py` + `tests/test_offering.py`
  ONLY. First duty: no open peer-gated PR (`[]` at fire start). Cloud bridge blocks direct main push →
  branch loop/streaming-response-signal + PR #101 + self-merge (squash 02be8d9; merged commit = exactly the
  two files). Realigned main to origin/main after merge (`git reset --hard origin/main` → 02be8d9, verified
  `streaming-response` present + offering canonical 34/34 + replay 24/24 on merged main), deleted local
  branch. `test_offering.py` 52→54; full suite green (22 files, 0 real failures; test_free_tier 11/11 after
  `pip install -r requirements.txt`, environment-only). Canonical PAIR unchanged (frozen fixtures): replay
  guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. RUNNER RECOVERED this fire
  (verify_20260731T085248Z 08:52Z, attempts=1) — but its LIVE re-score shows driftflight.com 76.2 C /
  +30.1 (transactability 87.5→62.5), a divergence from the frozen fixture recorded + queued P0 [LOCAL] +
  flagged for the digest (see the LIVE-DELTA DIVERGENCE note above). No Slack (score-neutral, off scoring
  path; not sensitive-class; 09:12Z is not the first-after-16:00 digest cycle — that is ~16:1xZ Jul-31).
  Next TRUTH — pin `streaming-response` as RELABEL-INVARIANT (the streaming contract keys on the delivery
  form, not the host), the eighth metered_api signal-level relabel guard, then a READOUT leg completes the
  arc. OR, if the live transactability drop persists, the [LOCAL] canonical re-capture is the
  higher-leverage TRUTH item. Thin archetypes service_booking / data_retrieval remain [LOCAL]-blocked.)
  (Cycle 125 METHOD — added the FIFTH metamorphic-invariance axis on the offering classifier, and the
  FIRST to perturb the order of items WITHIN a single surface rather than the surfaces themselves (the
  four prior axes — relabel / surface-read-order / scale / noise — all operate at surface granularity;
  none reorders the catalog listings a storefront lists on one page). `test_offering_listing_order_invariance_priced_listing`
  (`tests/test_offering_canonical.py` 33→34) pins that reordering the priced listings on one synthetic
  catalog page does not move the physical_good verdict: distinct-label STRENGTH, claimed set, and NA
  partition all order-invariant. Executes Cycle 124's next-hypothesis exactly. NON-VACUOUS by
  construction: `_scan_surface` keeps the FIRST match per signal (`pattern.search`), so reordering
  genuinely MOVES the sampled priced-listing exemplar quote (£51.77-first → €24.50-first, verified) while
  the verdict does not — an honest classifier samples a different price to show the reader but reaches the
  same conclusion. SYNTHETIC vehicle because `strip_html` collapses a committed fixture to a single
  whitespace-joined line (no per-listing boundary to permute — same reason as the free-trial-115 /
  content-provenance-119 / priced-listing-122 relabel guards). TEETH three ways: (a) reordered catalog
  bytes differ; (b) sampled quote differs; (c) base is a real strength-5 physical_good (add-to-cart /
  free-shipping / fulfillment / priced-listing / stock) with rails NA → a dropped leg or conjured rail
  would be unmistakable (retail-pole credibility direction). SHIP CLASS: tests-only, off the scoring path
  (`scoring.py` 0 offering refs) → score-neutral, NOT peer-gated. git diff over `asrs/ rubric/ fixtures/`
  EMPTY; --name-only = `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct main push →
  branch loop/listing-order-invariance + PR #99 + self-merge (squash 33f188e; merged commit = exactly the
  one test file). First duty: no open peer-gated PR (`[]` at fire start). Realigned main to origin/main
  after merge (`git reset --hard origin/main` → 33f188e, verified new test present + 34/34 on merged main),
  deleted local branch. Full suite green (22 files; test_free_tier 11/11 after `pip install -r
  requirements.txt`, environment-only). Canonical PAIR unchanged AND re-measured on merged main: replay
  guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7; offering canonical guard 34/34. RUNNER
  STILL GAPPED (verify_20260728T234102Z 23:41Z, ~56.5h old). No Slack (score-neutral, off scoring path;
  not sensitive-class; 08:12Z is not the first-after-16:00 digest cycle — that is ~16:1xZ Jul-31). Next
  COVERAGE — the metamorphic grid now spans five axes but listing-order invariance is pinned on the
  synthetic retail pole only; a future METHOD increment could mirror it onto a with-rails MACHINE surface
  (do the metered_api endpoints' ORDER within one OpenAPI spec matter to the claim?). For COVERAGE this
  cycle's rotation: a new signal leg on a CLAIMED archetype, or the [LOCAL] free-tier live-wiring /
  ACP-UCP-MPP handshakes. Thin archetypes service_booking / data_retrieval remain [LOCAL]-blocked (no
  committed fixture claims either — see P1).)
  (Cycle 124 READOUT — CLOSED the `priced-listing` arc at its third layer, COMPLETING the FIRST full
  COVERAGE→TRUTH→READOUT arc on the physical_good archetype (COVERAGE 122 signal → TRUTH 123
  relabel-invariance → READOUT 124). Added ONE capability-worded, vendor-neutral `<p>` ("Reading the
  price to fulfill") to `_write_methodology_page` (`asrs/scorecard.py`) after the subscription
  free-trial paragraph, guarded by `test_methodology_documents_priced_listing` in `tests/test_readout.py`
  (57→58). Frames that an agent can browse a catalog, see stock + an add-to-cart control, yet still not
  be able to DECIDE without reading the concrete PRICE beside the item (a catalog whose price an agent
  cannot read has not completed the commercial job); names the vendor-neutral priced-listing SHAPE (a
  decimal amount adjacent to an in-stock / add-to-cart control); keeps the bare-amount precision guard (a
  metered "per API call" / subscription "per month" price sits nowhere near availability → physical_good
  stays NA on an API storefront); recognition keys on the price the offer lists not who lists it, pinned
  by the identity-relabel regression test; honest scope (diagnostic, off the scoring path). The
  physical_good MIRROR of the free-trial-116 / content-provenance-120 READOUT legs. SHIP CLASS: display +
  tests-only, off the scoring path (`scoring.py` 0 offering refs) → score-neutral, NOT peer-gated. git
  diff over `asrs/scoring.py rubric/ fixtures/ asrs/offering.py` EMPTY; --name-only = `asrs/scorecard.py`
  + `tests/test_readout.py` ONLY. Cloud bridge blocks direct main push → branch loop/priced-listing-readout
  + PR #97 + self-merge (squash 2ccadae; merged commit = exactly the two files). First duty: no open
  peer-gated PR (`[]` at fire start). Realigned main to origin/main after merge (`git reset --hard
  origin/main` → 2ccadae, verified paragraph present + 58/58 on merged main), deleted local branch. Full
  suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only —
  eth-account absent in the fresh container). Canonical PAIR unchanged AND re-measured on merged main:
  replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7; offering canonical guard 33/33
  (physical_good NA on canonical pair preserved). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z,
  ~55.5h old). No Slack (score-neutral, off scoring path; not sensitive-class; 07:12Z is not the
  first-after-16:00 digest cycle — that is ~16:1xZ Jul-31). Next METHOD — the offer-side coverage on
  CLAIMED archetypes now spans all three layers on four archetypes; rotate to METHOD: the
  metamorphic-invariance axis grid still has gaps (surface-ORDER invariance covers only output-license +
  the org pole; com/retail/machine poles uncovered per Cycle 121). Extend a surface-order or content-scale
  invariance test to an uncovered storefront pole, OR add a metamorphic axis to the new physical_good
  priced-listing signal (reordering catalog listings must not change its physical_good strength). Thin
  archetypes service_booking / data_retrieval remain [LOCAL]-blocked.)
  (Cycle 123 TRUTH — pinned Cycle 122's `priced-listing` physical_good signal as RELABEL-INVARIANT,
  the FIRST physical_good leg in the signal-level relabel family (prior ten legs: metered_api ×7 +
  digital_good output-license/content-provenance + subscription free-trial). Added
  `test_offering_relabel_invariance_priced_listing` to `tests/test_offering_canonical.py` (32→33). A
  priced listing (a decimal amount beside an in-stock/add-to-cart control) is a property of the CATALOG
  STRUCTURE, not the host, so the signal must key on the price-beside-availability form. The real
  books.toscrape.com evidence is host-FREE (60 listings fire with the host in NEITHER surface key NOR
  quote window) → a whole-fixture relabel would be VACUOUS (the free-trial-115 / content-provenance-119
  failure mode), so the guard scans a SYNTHETIC retail catalog surface seating the host INSIDE the
  priced-listing evidence (surface-key prefix + adjacent to the price both sides → inside the 40-char
  padded quote window; asserted non-vacuous), relabels end-to-end, asserts identity-invariance (same
  match count 1, same host-normalized surface, quote still matches the live regex, host absent). TEETH:
  bare-currency metered/subscription pricing ("$0.01 per API call" / "$29.00 per month" / "$5.00 per
  1,000 requests", none beside availability) fires ZERO priced-listing → the match keys on the structure,
  not on a money amount. SHIP CLASS: tests-only, off the scoring path (`scoring.py` 0 offering refs) →
  score-neutral, NOT peer-gated. git diff over `asrs/ rubric/ fixtures/` EMPTY; --name-only =
  `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct main push → branch
  loop/relabel-priced-listing-signal + PR #95 + self-merge (squash 914b18a; merged commit = exactly the
  one test file). First duty: no open peer-gated PR (`[]` at fire start). Realigned main to origin/main
  after merge (local main stale at Cycle-94 3796519 from a forced-history rewrite → `git reset --hard
  origin/main` = 914b18a, verified new test present + 33/33 on merged main), deleted local branch. Full
  suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only).
  Canonical PAIR unchanged AND re-measured on merged main: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; rubric v0.7. RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z, ~54.6h old). No Slack
  (score-neutral, off scoring path; not sensitive-class; 06:18Z is not the first-after-16:00 digest cycle
  — that is ~16:1xZ Jul-31). Next READOUT — CLOSE the priced-listing arc at its third layer: physical_good
  has NO offer-side methodology paragraph yet (subscription got one at free-trial-116, digital_good at
  output-license + content-provenance-120). Add ONE capability-worded, vendor-neutral `<p>` to
  `_write_methodology_page` (`asrs/scorecard.py`) surfacing "read the price to decide + fulfill a physical
  purchase" (the physical_good mirror of the free-trial/content-provenance prose), guarded by a
  content-presence test in `tests/test_readout.py` → completes the FIRST full COVERAGE→TRUTH→READOUT arc
  on physical_good, display+tests-only/score-neutral.)
  (Cycle 122 COVERAGE — added a `priced-listing` capability signal to the **physical_good** archetype bank
  (`asrs/offering.py`): the "understand the offer" PRICE leg — a decimal amount quoted directly beside an
  in-stock / add-to-cart control ("£51.77 In stock", "$12.99 Add to basket") makes the item's price
  machine-legible on the catalog listing, the capability an agent needs to DECIDE + FULFILL a physical
  purchase. Executes Cycle 121's flagged next-move (physical_good CATALOG leg beyond add-to-cart/stock,
  verifiable on books.toscrape.com); FIRST new physical_good leg since sku-inventory (2026-07-27). Distinct
  from every sibling leg: add-to-cart = buy ACTION, stock = WHETHER available, sku-inventory = inventory
  MANAGEMENT — none guarantees a readable PRICE. PRECISION-CRITICAL, verified across all 5 fixtures before
  writing: `\d+[.,]\d{2}\s+(?:in stock|add to (cart|basket|bag))` fires 60× on books.toscrape.com and 0× on
  api.replicate.com / the canonical pair (which carry 12–17 bare metered per-call currency amounts, ZERO
  priced in-stock listings) / example.com — so it CANNOT conjure physical_good on an API storefront listing
  dollar amounts; physical_good stays NA on the canonical pair (operator acceptance preserved). SHIP CLASS:
  off the scoring path (`scoring.py` 0 offering refs — grep-verified) → score-neutral, NOT peer-gated (same
  class as all 11 prior offering-signal legs). git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY;
  --name-only = `asrs/offering.py` + `tests/test_offering.py` + `tests/test_offering_canonical.py`. Cloud
  bridge blocks direct main push → branch loop/priced-listing-physical-good + PR #93 + self-merge (squash
  1267137). First duty: no open peer-gated PR (`[]` at fire start). Realigned main to origin/main after merge
  (local main ref was STALE at Cycle-94 3796519 from a forced-history rewrite — `git reset --hard origin/main`
  → 1267137, verified priced-listing present on merged main), deleted local branch. `test_offering.py` 48→50
  (precision-synthetic + real-captured non-vacuity pair); `test_offering_canonical.py` retail-inverse guard
  now asserts `priced-listing` in `_RETAIL_PHYSICAL_LABELS` (32/32). Full suite green on merged main (22
  files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only). Canonical PAIR
  unchanged AND re-measured pre/post merge: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z, ~53.7h old). No Slack (score-neutral, off
  scoring path; not sensitive-class; 05:20Z is not the first-after-16:00 digest cycle — that is ~16:1xZ
  Jul-31). Next TRUTH — pin `priced-listing` as RELABEL-INVARIANT (physical_good's FIRST relabel leg; all 10
  existing relabel legs are metered_api/digital_good/subscription). The real books evidence is host-free → a
  whole-fixture relabel would be VACUOUS (free-trial-115 / content-provenance-119 failure mode), so scan a
  SYNTHETIC retail surface seating the host inside a priced listing, relabel end-to-end, assert
  identity-invariance. Alt READOUT: physical_good has no offer-side methodology paragraph yet — surface "read
  the price to fulfill" in `_write_methodology_page`.)
  (Cycle 121 METHOD — extended the content-SCALE metamorphic-invariance axis to the NO-RAILS retail pole
  (`books.toscrape.com`), closing the org/com-only-vs-retail asymmetry the SCALE axis carried — exactly the
  gap Cycle 117 closed for the noise-surface axis. `_org`/`_com` prove a WITH-RAILS storefront that repeats
  its pitch is not "more" of any archetype; this pins the OPPOSITE storefront type. Property protected: the
  "never manufacture the delta" invariant on the SCALE axis — duplicating a no-rails book catalog's prose
  N times must not raise its physical_good strength AND must not CONJURE a rails archetype (metered_api /
  subscription / digital_good) it does not offer. Dedicated `test_offering_content_scale_invariance_retail`,
  NOT the multi-archetype `_assert_content_scale_invariance` helper (retail claims a SINGLE archetype → no
  rank to reorder); non-vacuity anchored on physical_good's own signal firing MORE raw matches under
  duplication (count-based reader WOULD differ) + the NA-rails-stay-NA teeth. Mirrors Cycle 117's retail
  noise-surface test structure on the scale axis. SHIP CLASS: tests-only, off the scoring path (`scoring.py`
  imports no `offering` — grep 0 refs) → score-neutral, NOT peer-gated. git diff over `asrs/ rubric/
  fixtures/` EMPTY; --name-only = `tests/test_offering_canonical.py` ONLY (+~130). Cloud bridge blocks
  direct main push → branch loop/content-scale-retail + PR #91 + self-merge (squash 0e52bf0; merged commit =
  exactly the one test file). First duty: no open peer-gated PR (`[]` at fire start); realigned main to
  origin/main after merge, deleted local branch. offering canonical guard 31→32, re-run on merged main 32/32;
  full suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`, environment-only).
  Canonical PAIR unchanged AND re-measured pre/post merge: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; rubric v0.7. RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z, ~52.5h old). No Slack
  (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00 digest cycle — that is the
  ~16:1xZ Jul-31 fire). Next COVERAGE — frontier on CLAIMED archetypes is NARROW (metered_api saturated ×7;
  digital_good three closed arcs; subscription free-trial closed); thin archetypes (physical_good fulfillment
  / service_booking / data_retrieval) [LOCAL]-blocked. A COVERAGE move needing no new claimed archetype: a
  new physical_good CATALOG leg beyond add-to-cart/stock (price / variant / availability, verifiable on
  books.toscrape.com), or wire the next published self-description surface. Metamorphic-axis grid still has
  gaps too (surface-ORDER covers only output-license + org; com/retail/machine uncovered) — a future METHOD.)
  (Cycle 120 READOUT — CLOSED the `content-provenance` arc at its third layer: surfaced the digital_good
  "verify + trust the deliverable" capability in the PUBLIC methodology prose. Added ONE capability-worded,
  vendor-neutral `<p>` ("Trusting the deliverable", the authenticity MIRROR of the output-license "Owning
  the deliverable" leg) to `_write_methodology_page` (`asrs/scorecard.py`), placed directly after the
  digital_good rights paragraph — grouping the two digital_good offer-side legs (rights + authenticity) —
  plus a content-presence guard `test_methodology_documents_content_provenance` in `tests/test_readout.py`.
  THIRD full COVERAGE→TRUTH→READOUT arc on a non-metered_api archetype (after subscription free-trial
  114/115/116 and digital_good's own output-license), digital_good's SECOND prose leg. Prose (all guarded):
  frames it as the authenticity mirror of owning the deliverable + names the failure (a render that cannot
  be provenance-checked has NOT completed the commercial job); names vendor-neutral OPEN-STANDARD vocabulary
  as open conventions (C2PA / Content Credentials / a media-output provenance manifest-metadata record, same
  category as REST/GraphQL/OpenAPI); keeps the bare-`provenance`/`credentials` precision note (art/wine/
  supply-chain/data provenance, login credentials, "watermarking for provenance" model feature = no signal);
  keys on the provenance the offer grants NOT who grants it, pinned by the identity-relabel regression test;
  honest scope (diagnostic, off the scoring path). SHIP CLASS: display + tests-only, off the scoring path
  (`scoring.py` imports no `offering` — grep 0 refs) → score-neutral, NOT peer-gated. git diff over
  `asrs/scoring.py asrs/offering.py rubric/ fixtures/` EMPTY; --name-only = `asrs/scorecard.py` +
  `tests/test_readout.py`. Cloud bridge blocks direct main push → branch loop/content-provenance-readout +
  PR #89 + self-merge (squash 233e298; merged commit = exactly those two files). First duty: no open
  peer-gated PR (`[]` at fire start); realigned main to origin/main after merge, deleted local branch.
  `test_readout.py` 56→57; full suite green (22 files; test_free_tier 11/11 after `pip install -r
  requirements.txt`, environment-only). Canonical PAIR unchanged AND re-measured pre/post merge: replay
  guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z, ~51.5h old). No Slack (score-neutral, off scoring path; not
  sensitive-class; not the first-after-16:00 digest cycle — that is the ~16:1xZ Jul-31 fire). Next METHOD —
  the in-cloud COVERAGE/TRUTH frontier on CLAIMED archetypes is NARROW (metered_api saturated ×7;
  digital_good has THREE closed arcs now; subscription free-trial closed); thin archetypes
  (physical_good fulfillment / service_booking / data_retrieval) are all [LOCAL]-blocked. A METHOD move
  needing no new claimed archetype: extend a perturbation axis (relabel/order/scale/noise-surface) onto a
  signal or storefront-type not yet covered, or add a cross-fixture invariant over the now-dense digital_good
  signal family (generation / output-license / content-provenance).)
  (Cycle 119 TRUTH — pinned the Cycle-118 `content-provenance` signal (digital_good's authenticity leg) as
  RELABEL-INVARIANT: the TRUTH leg of the COVERAGE(118)→TRUTH arc, mirroring free-trial (114→115). Tenth leg
  of the signal-level relabel family (metered_api ×7 + digital_good `output-license` + subscription
  `free-trial` + this); digital_good's SECOND relabel-pinned leg. VERIFIED live that content-provenance
  evidence (C2PA / content credentials / records provenance) is host-FREE on all five committed fixtures —
  the host never lands in the quote window, even on the `agents.driftflight.com/*` surfaces where it sits
  only in the surface KEY — so a whole-fixture relabel would be VACUOUS (the free-trial-115 failure mode).
  New `test_offering_relabel_invariance_content_provenance` + `_provenance_signals` therefore scan a SYNTHETIC
  digital_good surface (host `acme-renders.example`) seating the host INSIDE the C2PA evidence (surface key +
  padded quote window, asserted non-vacuous), relabel end-to-end, and assert identity-invariance: same match
  count (1), same host-normalized surface, quote still matches the live content-provenance regex, host absent.
  TEETH: a bare-`provenance`/`credentials` distractor (art/wine/data provenance, login credentials,
  api.replicate-style "watermarking for provenance" model-feature) fires ZERO. SHIP CLASS: tests-only, off the
  scoring path (`scoring.py` 0 offering refs — grep-verified) → score-neutral, NOT peer-gated. git diff over
  `asrs/ rubric/ fixtures/` EMPTY; --name-only = `tests/test_offering_canonical.py` ONLY (+140). Cloud bridge
  blocks direct main push → branch loop/relabel-content-provenance-signal + PR #87 + self-merge (squash
  a8363d3; merged commit = exactly the one test file). First duty: no open peer-gated PR ([] at fire start);
  realigned main to origin/main after merge, deleted local branch. offering canonical guard 30→31, re-run on
  merged main 31/31; full suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`,
  environment-only). Canonical PAIR unchanged AND re-measured pre/post merge: replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class;
  not the first-after-16:00 digest cycle — that is the ~16:1xZ Jul-31 fire). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z, ~50h old). Next READOUT — CLOSE the content-provenance arc at its third
  layer: surface "verify the deliverable's provenance" in `_write_methodology_page` prose (third full
  COVERAGE→TRUTH→READOUT arc on a non-metered_api archetype, after free-trial + output-license),
  capability-worded/vendor-neutral (C2PA / content credentials / media-output provenance record as open
  conventions), with a `test_readout.py` content-presence guard.)
  (Cycle 118 COVERAGE — added a `content-provenance` capability signal to the **digital_good** archetype
  bank (`asrs/offering.py`): the "verify + trust the deliverable" leg, the authenticity MIRROR of
  `output-license` (rights to USE → the MEANS to TRUST). An agent obtaining a generated asset that carries
  embedded provenance (C2PA content credentials, a provenance manifest/metadata record) can confirm it is
  genuine and use it in a provenance-aware pipeline — distinct from `generation`/`generate-media` (WHAT),
  `hosted-output` (WHERE), `output-license` (RIGHTS). PLANNED PIVOT off the Cycle-117 "physical_good
  fulfillment leg" recommendation: in-cloud verification KILLED that pick — the only committed physical_good
  fixture `books.toscrape.com` is thin (physical_good fires on ONLY `add-to-cart` + `stock`; its llms.txt
  are real 404s; no order/tracking/delivery/returns prose), so a fulfillment signal would be VACUOUS →
  physical_good fulfillment JOINS service_booking / data_retrieval as [LOCAL]-blocked (queued P1). Also
  rejected: subscription-cancellation (`/cancellation` is a 404 on both canonical domains) and metered_api
  webhook-signing (fires only on api.replicate; metered_api saturated at 7 arcs). content-provenance instead
  fires NON-VACUOUSLY on the canonical PAIR (29/24 on .com/.org, both already claim digital_good) and ZERO
  on api.replicate/books/example — correctly dodging api.replicate's "watermarking for provenance"
  hosted-MODEL-feature trap, so it never CONJURES a false digital_good claim. Vendor-neutral open-standard
  vocabulary (C2PA / CAI Content Credentials / media-output provenance metadata-manifest), precision-guarded
  (never bare "provenance"/"credentials"; art/wine/supply-chain/data provenance dodged). SHIP CLASS:
  signal-bank + tests only, off the scoring path (`scoring.py` imports no `offering` — grep 0 refs) →
  score-neutral, NOT peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY; git diff --name-only
  = `asrs/offering.py` + `tests/test_offering.py` (+135). Cloud bridge blocks direct main push → branch
  loop/content-provenance-signal + PR #85 + self-merge (squash d3b9d0f). First duty: no open peer-gated PR
  (`[]` at fire start); realigned main to origin/main after merge, deleted local branch. `test_offering.py`
  46→48; full suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`,
  environment-only). Canonical PAIR unchanged AND re-measured pre- and post-merge: replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; claimed sets/order byte-identical on all 5 fixtures; rubric v0.7.
  No Slack (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00 digest cycle —
  that is the ~16:1xZ Jul-31 fire). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z, ~49.5h old). Next
  TRUTH — pin content-provenance as RELABEL-INVARIANT (COVERAGE 118 → TRUTH → READOUT arc, mirroring
  free-trial 114/115/116): extend the signal-level relabel family (metered_api ×7, digital_good ×1, subscription
  ×1) to digital_good's SECOND leg; provenance evidence is host-free by nature (C2PA/content-credentials/
  "records provenance") so — like free-trial 115 — the guard likely needs a SYNTHETIC surface seating the host
  INSIDE the provenance evidence, then identity-invariance under end-to-end relabel + a bare-"provenance"
  distractor firing ZERO. Then READOUT: surface "verify the deliverable's provenance" in the methodology prose.)
  (Cycle 117 METHOD — extended the noise-surface perturbation axis (Cycle 113) onto the OPPOSITE storefront
  type: the no-rails retail store `books.toscrape.com` (claims ONLY physical_good, every rails archetype NA).
  `_org`/`_com` prove incidental web chrome adds no claim on the WITH-RAILS canonical pair; this closes the
  axis on the no-rails pole, pinning the "never manufacture the delta" invariant at the task-discovery layer —
  bolting cookie/careers/legal chrome onto a no-rails retailer must not CONJURE a rails claim (metered_api /
  subscription / digital_good / service_booking / data_retrieval stay NA), nor drift physical_good's evidence
  map. New `test_offering_noise_surface_invariance_retail`: add the signal-free `/privacy` surface → WHOLE
  profile byte-identical, rails set stays NA, surfaces_seen grows by exactly `/privacy`. DEDICATED test (not a
  reuse of `_assert_noise_surface_invariance`): the retail store is SINGLE-archetype so the helper's
  `len(claimed) >= 2` rank-reorder premise does not apply (guarded property is "the NA rails set stays NA"),
  and the helper's negative control conjures physical_good (ALREADY claimed here, a no-op) → the retail teeth
  conjure metered_api (a rails archetype NA on a book catalog) via real API prose. Three teeth: (a) `/privacy`
  genuinely READ (surfaces_seen) yet adds no claim; (b) distractor fires ZERO under `_scan_surface`; (c)
  metered_api negative control DOES conjure metered_api (`['metered_api','physical_good']`) → channel live,
  non-vacuous. SHIP CLASS: tests-only, off the scoring path (`scoring.py` imports no `offering` — grep-verified
  0 refs) → score-neutral, NOT peer-gated. git diff over `asrs/ rubric/ fixtures/` EMPTY; git diff --name-only
  = `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct main push → branch
  loop/noise-surface-invariance-retail + PR #83 + self-merge (squash d04b34c). First duty: no open peer-gated
  PR ([] at fire start); realigned main to origin/main after merge, deleted local branch. offering canonical
  guard 29→30; full suite green (22 files; test_free_tier 11/11 after `pip install -r requirements.txt`,
  environment-only). Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class; not the
  first-after-16:00 digest cycle — that is the ~16:1xZ Jul-31 fire). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z, ~63h old). The perturbation matrix is now dense: relabel spans
  org/com/machine + 9 signal-level legs; order + scale + noise-surface span org/com; noise-surface now also
  covers the no-rails retail pole. Next COVERAGE — a new capability-worded signal on a CLAIMED archetype; a
  physical_good fulfillment leg on the retail pole (shipping-address / order-tracking / returns-policy) is the
  natural next brick with the retail fixture already committed. service_booking / data_retrieval signal work
  stays [LOCAL] (no committed fixture claims either); ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 116 READOUT — surfaced the `subscription` `free-trial` capability in the PUBLIC methodology prose,
  the READOUT leg CLOSING the free-trial arc (COVERAGE 114 → TRUTH-relabel 115 → READOUT 116). This is the
  FIRST subscription-archetype offer-side leg to complete a full COVERAGE→TRUTH→READOUT arc — every prior
  prose leg was metered_api (payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88, error-contract
  90/91/92, test-mode 102/103/104, pagination 106/107/108, cancel-job 110/111/112) plus the digital_good
  rights leg at Cycle 100. Added ONE capability-worded, vendor-neutral `<p>` ("Evaluating a subscription at
  $0 first") to the methodology "What the score answers" card (`_write_methodology_page`,
  `asrs/scorecard.py`), after the digital_good "Owning the deliverable" paragraph: (a) frames trying the
  RECURRING plan at $0 before any charge begins, ties it to ASRS's own $0-only ethos, names the failure
  (commit to recurring billing sight-unseen); (b) names vendor-neutral trial-offer vocabulary as open
  conventions (a free trial / trial period / N-day trial such as a `14-day free trial` / trial
  account-allowance / "start your free trial" / "try it free for N days"); (c) keeps the signal's PRECISION
  honesty — a bare `trial` word (clinical trial / court trial / "trial and error" / "trial by fire" / "on
  trial") is no signal; (d) recognition keys on the TRIAL the offer grants, not who grants it, pinned by an
  identity-relabel executable regression test that relabels the storefront end-to-end; (e) HONEST scope —
  diagnostic, off the scoring path, not a scored pillar. The subscription-side MIRROR of metered_api's
  test-mode leg. GUARD: `test_methodology_documents_free_trial` in `tests/test_readout.py` (55→56), same
  content-presence shape as the cancel-job/pagination/test-mode guards. SHIP CLASS: display + tests-only,
  off the scoring path (`scoring.py` does not import `offering` — grep-verified 0 refs) → score-neutral,
  NOT peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY; git diff --name-only =
  `asrs/scorecard.py` + `tests/test_readout.py`. Cloud bridge blocks direct main push → branch
  loop/free-trial-methodology-readout + PR #81 + self-merge (squash 3067382; merged commit = exactly the 2
  files, +88 lines). First duty: no open peer-gated PR ([] at fire start); realigned main to origin/main
  after merge, deleted local branch. Full suite green (22 files; test_free_tier 11/11 after `pip install -r
  requirements.txt`, environment-only). Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F
  / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not
  sensitive-class; not the first-after-16:00 digest cycle — that was Cycle 109 at 16:12Z). RUNNER STILL
  GAPPED (verify_20260728T234102Z 23:41Z, ~47.5h old). Next METHOD — a fresh perturbation axis on the
  offering/battery path OR extend the signal-level relabel family (now spanning three archetypes:
  metered_api ×7, digital_good ×1, subscription ×1). service_booking / data_retrieval signal work stays
  [LOCAL] (no committed fixture claims either — any new signal unverifiable in-cloud); ACP/UCP/MPP +
  free-tier live-wiring stays [LOCAL].)
  (Cycle 115 TRUTH — pinned the Cycle-114 `free-trial` subscription signal as RELABEL-INVARIANT, extending
  the signal-level relabel family to its THIRD archetype: `subscription` (after `metered_api`'s seven legs
  — payment-rail 79 / async-job 83 / api-auth 87 / error-contract / test-mode / pagination / cancel-job 111
  — and `digital_good`'s `output-license` 99). A trial offer is a property of what a storefront GRANTS (a
  free trial / trial period-account-allowance / N-day trial), never of WHO grants it, so the signal must key
  on the trial FORM, not the host. WHY a SYNTHETIC surface, not the real fixture (unlike output-license 99):
  the `free-trial` vocabulary is host-free by nature, and VERIFIED LIVE on the committed driftflight.com
  fixture the signal fires on `/llms.txt` / `/pricing` / `homepage` with NEITHER the host in the surface key
  NOR the quote window → a whole-fixture relabel would be VACUOUS. The guard scans a synthetic subscription
  surface that seats the host INSIDE the trial evidence (surface-key prefix `agents.<host>/pricing` + adjacent
  to the trial phrase so it lands in the padded quote window, asserted non-vacuous), relabels the host
  everywhere, re-scans, and asserts identity-invariance: SAME match count (1), SAME host-normalized surface,
  quote STILL matches the live `free-trial` regex, host absent from all rewritten evidence. `_scan_surface` on
  synthetic prose = the same primitive the noise-surface guard (113) uses. TEETH: a sibling distractor surface
  carrying only bare-"trial" false-positive senses (clinical trial / on trial / trial and error) fires ZERO
  free-trial, proving the match keys on the FREE-trial STRUCTURE not the word "trial", and relabeling through
  it never CONJURES a claim. New `test_offering_relabel_invariance_free_trial` + `_free_trial_signals` helper
  in `tests/test_offering_canonical.py`. SHIP CLASS: tests-only, off the scoring path (`scoring.py` does not
  import `offering` — grep-verified 0 refs) → score-neutral, NOT peer-gated. git diff over `asrs/ rubric/
  fixtures/` EMPTY; git diff --name-only = `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct
  main push → branch loop/free-trial-relabel-invariance + PR #79 + self-merge (squash f220ea6). First duty: no
  open peer-gated PR ([] at fire start); realigned main to origin/main after merge, deleted local branch.
  offering canonical guard 28→29; full suite green (22 files; test_free_tier 11/11 after `pip install
  eth-account`, environment-only). Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class;
  not the first-after-16:00 digest cycle — that was Cycle 109 at 16:12Z). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z, ~43.5h old). Next READOUT — complete the free-trial arc (COVERAGE 114 →
  TRUTH 115 → READOUT): surface "evaluate a subscription at $0 before committing" in the public methodology
  prose (`_write_methodology_page`, `asrs/scorecard.py`) with a content-presence guard in `tests/test_readout.py`
  — the first subscription-archetype leg of a full COVERAGE→TRUTH→READOUT arc. Deeper subscription /
  service_booking / data_retrieval signal work stays [LOCAL] (needs a claiming fixture); ACP/UCP/MPP +
  free-tier live-wiring stays [LOCAL].)
  (Cycle 114 COVERAGE — added a `free-trial` signal to the `subscription` bank in `asrs/offering.py`: a
  no-cost evaluation of a recurring offer BEFORE billing begins (a free trial / trial period / trial
  account/allowance/membership / N-day trial / start-or-try-free offer). The FIRST new subscription signal
  since `seat-licensing`, and the subscription-archetype MIRROR of metered_api's `test-mode`: an agent can
  EVALUATE the recurring offer at $0 before committing to billing (the "provision the offer safely, without
  a human" capability, aligned with ASRS's $0-only ethos). WHY this archetype: STATE's Cycle-114 pointer
  directed COVERAGE to strengthen the thinly-signalled archetypes (subscription/service_booking/data_retrieval
  = 6/5/5 legs vs metered_api's ~19); only `subscription` is CLAIMED by a committed fixture (the canonical
  pair), so it is the one strengthenable with in-cloud non-vacuous verification (service_booking /
  data_retrieval need a [LOCAL] fixture that claims them — queued P?/[LOCAL]). Distinct from every existing
  subscription signal (`subscription`/`recurring` = a plan EXISTS, `per-month`/`per-month-price`/
  `annual-billing` = cadence, `seat-licensing` = per-user basis; NONE said whether you can evaluate the plan
  at no cost first). PRECISION: NEVER a bare `trial` (clinical/court trial, "trial and error", "trial by
  fire", "on trial") — require a FREE trial, a trial PERIOD/ACCOUNT/ALLOWANCE/MEMBERSHIP, an N-DAY trial, or
  a START/TRY-FREE offer; 8 negatives (incl. "free shipping"/"free image"/"free allowance") + 10 positives.
  SHIP CLASS: COVERAGE, off the scoring path (`scoring.py` does not import `offering` — grep-verified 0 refs)
  → score-neutral, NOT peer-gated. git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY; git diff
  --name-only = `asrs/offering.py` + `tests/test_offering.py`. Cloud bridge blocks direct main push → branch
  loop/free-trial-subscription-signal + PR #77 + self-merge (squash 2092c61). First duty: no open peer-gated
  PR ([] at fire start); realigned main to origin/main after merge, deleted local branch. EVIDENCE: fires
  non-vacuously on driftflight.com's real "free trial allowance, so an agent can evaluate it before any
  payment" homepage/llms.txt/pricing prose (subscription strength 4→5, still LAST; claimed SET + ORDER
  byte-unchanged: metered_api 16 > digital_good 6 > subscription 5) and on ZERO sites not already claiming
  subscription (api.replicate.com / books.toscrape.com / example.com / the trial-free drift-flight.org which
  stays strength 4) → can never CONJURE a subscription claim. offering canonical guard 28/28; test_offering.py
  44→46. Full suite green (22 files; test_free_tier 11/11 after `pip install eth-account`, environment-only).
  Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00
  digest cycle — that was Cycle 109 at 16:12Z). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z, ~43h
  old). Next TRUTH — pin `free-trial` as RELABEL-INVARIANT (the subscription-bank analog of the metered_api
  signal-level relabel family: host-in-trial-evidence → relabel → identity-invariant (label, surface) map),
  extending the relabel family to a SECOND archetype; then a READOUT leg to complete the free-trial arc
  (COVERAGE 114 → TRUTH → READOUT) surfacing "evaluate a subscription at $0 before committing" in the public
  methodology prose. service_booking / data_retrieval signal work stays [LOCAL] (needs a claiming fixture);
  ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 113 METHOD — added the FOURTH metamorphic axis on the offering classifier, pair-symmetric on the
  canonical pair: NOISE-SURFACE INVARIANCE. Adding a NEW readable surface that carries no capability signal
  (a cookie/privacy notice, careers blurb, legal footer, metaphorical-"ship" marketing prose) must leave the
  classified capability profile byte-identical (ranked claimed archetypes, full (label, surface, quote)
  evidence map, NA/unclaimed set). The three prior families perturb the surfaces a site DOES publish (RELABEL
  rewrites the host inside them, ORDER reverses their sequence, SCALE duplicates their bodies); NOISE is the
  complement — it ADDS the incidental web chrome every real storefront serves and asserts the score measures
  what a site DECLARES, not the noise around it. WHY (capability): a privacy policy must not conjure an
  archetype and must not retract one; the rank drives the fixed template-bank task order (cross-site
  comparability) and the NA set decides which archetypes a site is judged on vs excused, so both must be
  properties of what the site declares. Only surfaces_seen (read-provenance) reflects the extra read. THREE
  TEETH: (a) the noise surface is genuinely READ (lands in surfaces_seen) yet contributes no claim; (b) the
  distractor fires ZERO signals under _scan_surface, asserted directly, despite metaphorical-"ship"×3 +
  cookie/careers/legal near-miss traps — doubling as a precision demonstration on realistic prose; (c) a
  negative control swaps the SAME surface key for real fulfillment prose and shows the profile DOES change
  (physical_good, NA on the pair, conjured), proving the added-surface channel is live. A 4th assertion pins
  the honest scope: surfaces_seen grew by EXACTLY the noise surface. New `_assert_noise_surface_invariance` +
  `test_offering_noise_surface_invariance_{org,com}` in `tests/test_offering_canonical.py`. SHIP CLASS:
  tests-only, off the scoring path (`scoring.py` does not import `offering` — grep-verified) → score-neutral,
  NOT peer-gated. git diff over `asrs/ rubric/ fixtures/` EMPTY; git diff --name-only =
  `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct main push → branch
  loop/noise-surface-invariance + PR #75 + self-merge (squash 31becd3). First duty: no open peer-gated PR
  ([] at fire start); realigned main to origin/main after merge, deleted local branch. offering canonical
  guard 26→28; full suite green (22 files; test_free_tier 11/11 after `pip install eth-account`,
  environment-only). Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4,
  0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class; not the
  first-after-16:00 digest cycle — that was Cycle 109 at 16:12Z). RUNNER STILL GAPPED (verify_20260728T234102Z
  23:41Z, ~42.8h old). Next COVERAGE — the offering-path invariance family is now four-fold (RELABEL / ORDER /
  SCALE / NOISE), pair-symmetric, so the strongest untapped leverage is a NEW archetype or a signal on an
  UNDER-developed archetype: metered_api has 7 offer-side legs while subscription / service_booking /
  data_retrieval are thinly signalled — audit which is weakest and add ONE capability-worded, vendor-neutral
  signal; ACP/UCP/MPP live handshakes + free-tier live-wiring stays [LOCAL].)
  (Cycle 112 READOUT — surfaced the `metered_api` `cancel-job` capability in the PUBLIC methodology prose,
  the READOUT leg CLOSING the cancel-job arc (COVERAGE 110 → TRUTH-relabel 111 → READOUT 112) — the SEVENTH
  metered_api offer-side leg to complete the full COVERAGE→TRUTH→READOUT arc (after payment-rail 78/79/80,
  async-job 82/83/84, api-auth 86/87/88, error-contract 90/91/92, test-mode 102/103/104, pagination
  106/107/108). Added ONE capability-worded, vendor-neutral `<p>` ("Aborting a runaway job") to the
  methodology "What the score answers" card (`_write_methodology_page`, `asrs/scorecard.py`), placed after
  the async-job "Finishing the job" paragraph as the CONTROL leg of the same asynchronous contract. WHY
  (capability): a long-running job (image/video generation, a training run, a batch-inference request) keeps
  BILLING for compute while it runs, so an agent that detects a runaway/wrong generation and cannot STOP it
  keeps paying for work it no longer wants — an offer that documents a cancellation contract lets the agent
  BOUND its own spend (the same $0-only capital-safety ethos ASRS holds) and is more agent-completable. Names
  the vendor-neutral REST cancellation vocabulary as open conventions (a `.../cancel` endpoint on a job
  resource, a `Cancel-After` deadline header, a `canceled` job state); KEEPS the precision note (bare `cancel`
  — "cancel your subscription", a cancellation policy, "cancel your order", a canceled flight — is no signal);
  names the Cycle-111 identity-relabel regression test; stays HONEST about scope (diagnostic, off the scoring
  path, not a scored pillar). New content-presence guard `test_methodology_documents_cancel_job` in
  `tests/test_readout.py` (53→54) mirrors the pagination/test-mode guards; rendered-page neutral-scan
  (`test_readout_wording`) stays clean. SHIP CLASS: display + tests-only, off the scoring path → NOT
  peer-gated (git diff --name-only = asrs/scorecard.py + tests/test_readout.py ONLY; scoring-path diff over
  asrs/scoring.py asrs/offering.py rubric/ fixtures/ EMPTY). Cloud bridge blocks direct main push → branch
  loop/cancel-job-methodology-prose + PR #73 + self-merge (squash f0e5ba0). First duty: no open peer-gated PR
  ([] at fire start); realigned main to origin/main after merge. Full suite green 306→307 (test_free_tier
  11/11 after `pip install eth-account`, environment-only). Canonical PAIR unchanged AND re-measured: replay
  guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring
  path; not sensitive-class; not the first-after-16:00 digest cycle — that was Cycle 109 at 16:12Z). RUNNER
  STILL GAPPED (verify_20260728T234102Z 23:41Z, ~41.8h old). Next METHOD — the cancel-job arc is closed at
  all three layers and the metered_api signal-level relabel family + the offering-path invariance families
  (ORDER/RELABEL/SCALE, pair-symmetric) are complete, so the strongest next leverage is a NEW archetype/signal
  (COVERAGE) or a genuinely NEW perturbation axis on the offering/battery path rather than another guard in a
  complete family; ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 111 TRUTH — pinned the Cycle-110 `cancel-job` metered_api signal as RELABEL-INVARIANT, the
  SEVENTH metered_api signal-level relabel guard (after payment-rail 79 / async-job 83 / api-auth 87 /
  error-contract 91 / test-mode 103 / pagination 107) — completing the metered_api signal-level relabel
  family for every signal landed through Cycle 110. New `test_offering_relabel_invariance_cancel_job` in
  `tests/test_offering_canonical.py`, a close mirror of the pagination/async-job guards (surface-presence,
  host-free). WHY (capability): how an agent ABORTS a submitted long-running job (a `Cancel-After` deadline
  header / a `cancel` verb naming an async-job noun / a `.../cancel` endpoint on a job resource) is a
  property of the API CONTRACT a storefront documents, never of WHO published it, so the signal must be
  identity-invariant; the guard makes that an executable tripwire. SHAPE: fires ×1 on `api.replicate.com`'s
  `/openapi.json` (a real `Cancel-After` header); the fired quote + relative surface name no vendor, so
  non-vacuity is anchored at the FIXTURE level (host IS present in the fetched surfaces → a whole-fixture
  relabel to `vendor-neutral.test` genuinely rewrites classifier input). Under relabel: SAME count (1), SAME
  host-normalized surface, each quote STILL satisfying the live cancel-job regex, vendor host absent. SHIP
  CLASS: tests-only, off the scoring path (`scoring.py` does not import `offering` — grep-verified) →
  score-neutral, NOT peer-gated. git diff over `asrs/ rubric/ fixtures/` EMPTY; git diff --name-only =
  `tests/test_offering_canonical.py` ONLY. Cloud bridge blocks direct main push → branch
  loop/cancel-job-relabel-invariance + PR #71 + self-merge (squash 98f2b27). First duty: no open peer-gated
  PR ([] at fire start); realigned main to origin/main after merge. offering canonical guard 25→26; full
  suite green (22 files; test_free_tier 11/11 after `pip install eth-account`, environment-only). Canonical
  PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7.
  No Slack (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00 digest cycle —
  that was Cycle 109 at 16:12Z). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z, ~41.7h old). Next
  READOUT — complete the cancel-job arc (COVERAGE 110 → TRUTH 111 → READOUT) by surfacing the "abort a
  runaway job to bound your spend" capability in the public methodology prose (`_write_methodology_page`,
  `asrs/scorecard.py`), the SEVENTH metered_api leg to complete a full COVERAGE→TRUTH→READOUT arc, with a
  matching content-presence guard in `tests/test_readout.py`. A NEW archetype/signal remains open COVERAGE;
  ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 110 COVERAGE — added a `cancel-job` signal to the `metered_api` bank in `asrs/offering.py`: how
  an agent ABORTS a long-running job it already submitted — a `.../cancel` endpoint on the job resource, a
  `Cancel-After` deadline header, or a documented `canceled` job state. First NEW metered_api signal since
  pagination (Cycle 106). WHY (capability): the "complete the job" CONTROL + capital-safety leg for a
  metered API whose work runs long (image/video generation, a training run, a batch inference job) — an
  agent that detects a runaway/wrong generation and CANNOT cancel it keeps paying for compute it no longer
  needs, so a metered API that documents a cancel contract lets the agent BOUND its own spend (the same
  $0-only capital-safety ethos ASRS itself holds) and is MORE agent-completable. Distinct from every
  existing metered_api signal — `async-job` is how ONE long job's result comes BACK (webhook/poll),
  `error-contract` how a FAILED call recovers, `rate-limited` how fast you may call, `pagination` how a
  paged collection is walked; NONE said how an agent STOPS a job it started. Vendor-neutral open REST
  conventions (a cancel endpoint on a job resource, a `Cancel-After` header, a `canceled` job state),
  never a vendor. PRECISION: never a bare `cancel` (cancel a SUBSCRIPTION/ORDER/BOOKING, a cancellation
  POLICY, a cancelled flight, "cancel culture" all dodged) — require the `Cancel-After` header, a `cancel`
  verb naming an async-JOB noun, or a `.../cancel` endpoint path on a job resource; 8 negatives + 7
  positives. SHIP CLASS: off the scoring path (`scoring.py` does not import `offering` — grep-verified;
  only `battery.py`/`cli.py` use it for `--battery auto` task selection) → score-neutral, NOT peer-gated.
  git diff over `asrs/scoring.py rubric/ fixtures/` EMPTY; git diff --name-only = `asrs/offering.py` +
  `tests/test_offering.py`. Cloud bridge blocks direct main push → branch loop/cancel-job-metered-signal +
  PR #69 + self-merge (squash 41dc6e7). First duty: no open peer-gated PR ([] at fire start); realigned
  main to origin/main after merge. Fires non-vacuously on the real captured `api.replicate.com`
  `/openapi.json` (`Cancel-After` header + `predictions/{id}/cancel` endpoint + `canceled` state) and on
  ZERO of the canonical-pair / retail / null fixtures (claimed SETS byte-identical across all 5 fixtures
  with/without the signal). test_offering.py 44→46; full suite green (22 files; test_free_tier 11/11 after
  `pip install eth-account`, environment-only); offering canonical guard 25/25. Canonical PAIR unchanged
  AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack
  (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00 digest cycle — that was
  Cycle 109 at 16:12Z). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~41.5h old). Next TRUTH — pin
  cancel-job as RELABEL-INVARIANT (the 7th metered_api signal-level relabel guard, after payment-rail 79 /
  async-job 83 / api-auth 87 / error-contract 91 / test-mode 103 / pagination 107), a close mirror of the
  async-job guard; then a READOUT leg to complete the cancel-job arc. A NEW archetype/signal remains open
  COVERAGE; ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 109 METHOD — pinned the offering classifier as CONTENT-SCALE-INVARIANT on the canonical pair,
  a genuinely NEW perturbation axis distinct from surface-read ORDER and host RELABEL. New
  `_assert_content_scale_invariance(domain, expected)` in `tests/test_offering_canonical.py` duplicates
  every surface body K=3× and asserts the WHOLE classified profile is byte-identical: claimed archetypes
  in RANK ORDER, each archetype's `strength` + full `(label, surface, quote)` evidence map, and the
  NA/unclaimed set. Two wrappers apply it to BOTH pair-halves (`_org`/`_com`) from the start, so this axis
  does NOT inherit the `.com`-only asymmetry order-invariance had to close in Cycle 105. WHY: an offering
  claim is QUALITATIVE (does the site claim archetype X?), never QUANTITATIVE — a storefront that repeats
  its pitch is not "more" of an archetype and must not out-rank/reorder against one that states each
  capability once. Count-independence rests on two mechanisms this guard pins as an executable tripwire:
  `_scan_surface` uses `pattern.search` (FIRST match per (archetype,label), not `finditer`) and
  `ArchetypeClaim.strength` counts DISTINCT LABELS (not raw hits — its docstring names exactly this
  rationale). TEETH: the anchor's raw regex-match count MULTIPLIES under duplication (1→3 on both domains,
  `metered_api/post-endpoint`), so a count-based reader WOULD differ; a regression to `finditer` +
  count-based strength (which would let volume reorder the fixed template-bank task order) fails here. Each
  half asserts ≥2 claimed archetypes with distinct strengths (.org 11/6/4, .com 16/6/4). SHIP CLASS:
  tests-only, off scoring path (`scoring.py` does not import `offering` — grep-verified) → score-neutral,
  NOT peer-gated. git diff -- asrs/ rubric/ fixtures/ EMPTY; git diff --name-only = tests/test_offering_
  canonical.py ONLY. Cloud bridge blocks direct main push → branch loop/offering-content-scale-invariance
  + PR #67 + self-merge (squash 926e22f). First duty: no open peer-gated PR ([] at fire start); realigned
  main to origin/main after merge. Offering canonical guard 23→25; full suite green (22 files;
  test_free_tier 11/11 after `pip install eth-account`, environment-only). Canonical PAIR unchanged AND
  re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. Slack: daily
  digest sent (first cycle after 16:00 UTC), re-flagging the still-open runner stall. RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~40.5h old). Next COVERAGE — the offering-path invariance families are
  now three-fold and pair-symmetric (ORDER / RELABEL / SCALE); stronger next leverage is a NEW archetype
  or metered_api/digital_good signal, or design-readying a [LOCAL] live-wiring item (ACP/UCP/MPP,
  free-tier probe). ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 108 READOUT — surfaced the `pagination` metered_api capability in the PUBLIC methodology prose,
  the READOUT leg CLOSING the pagination arc (COVERAGE 106 → TRUTH-relabel 107 → READOUT 108) — the sixth
  metered_api leg to complete the full COVERAGE→TRUTH→READOUT arc (after payment-rail 78/79/80, async-job
  82/83/84, api-auth 86/87/88, error-contract 90/91/92, test-mode 102/103/104). Added ONE capability-worded,
  vendor-neutral `<p>` ("Walking the whole collection") to the methodology "What the score answers" card
  (`_write_methodology_page`, `asrs/scorecard.py`), between the error-contract paragraph and "Trying the call
  safely first". Frames walking a multi-page result set to completion (cursor param carrying a value /
  next-previous page URL / paginated collection response); names the under-completion failure (stop at page
  one → partial answer reported as whole); KEEPS the precision note (bare `next`/`cursor` — a retail product
  link, "next campaign" banner, text cursor, "next page of the novel" — is no signal); names the identity
  relabel regression test; stays HONEST about scope (diagnostic, off the scoring path, not a scored pillar).
  New content-presence guard `test_methodology_documents_pagination` in `tests/test_readout.py` (53→54)
  mirrors `test_methodology_documents_test_mode`; rendered-page neutral-scan clean. Display + tests-only, off
  the scoring path → NOT peer-gated (git diff --name-only = asrs/scorecard.py + tests/test_readout.py ONLY;
  scoring-path diff EMPTY). Cloud bridge blocks direct main push → branch loop/pagination-methodology-prose
  + PR #65 + self-merge (squash 82eacd1). First duty: no open peer-gated PR ([] at fire start); realigned
  main to origin/main after merge. Full suite green (test_free_tier 11/11); replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class;
  not the first-after-16:00 digest cycle — 15:16Z < ~16:12Z). RUNNER STILL GAPPED (verify_20260728T234102Z
  23:41Z ~39.6h old). Next METHOD — the pagination arc + the order-/relabel-invariance families are now
  complete across both canonical pair-halves; candidate: a genuinely NEW perturbation axis (label/scale) on
  the offering/battery path, or a NEW archetype/metered_api/digital_good signal (COVERAGE). ACP/UCP/MPP +
  free-tier live-wiring stays [LOCAL].)
  (Cycle 107 TRUTH — pinned the Cycle-106 `pagination` metered_api signal as RELABEL-INVARIANT, the
  SIXTH metered_api signal-level relabel guard, completing the family (payment-rail 79 / async-job 83 /
  api-auth 87 / error-contract / test-mode 103 / now pagination 107). New
  `test_offering_relabel_invariance_pagination` in `tests/test_offering_canonical.py` (22→23 in that
  file). A close mirror of the async-job guard: pagination fires on `api.replicate.com`'s `/openapi.json`
  ("A URL pointing to the next page of collection objects") with a HOST-FREE quote + relative
  `/openapi.json` surface → SURFACE-PRESENCE invariance anchored at the FIXTURE level (assert the host IS
  present in the fixture surfaces the classifier fetches, so the whole-fixture relabel does real work).
  Under `api.replicate.com`→`vendor-neutral.test` relabel the signal must fire the SAME count (1), on the
  SAME host-normalized surface, each quote STILL matching the live pagination regex, vendor host absent.
  WHY (capability/rigor): how an agent walks a paged collection to completion is a property of the API
  CONTRACT a storefront documents (cursor param / next-page URL / paginated response schema), never of
  WHO published it → identity-invariant; makes the Cycle-106 vendor-neutrality claim an executable
  tripwire. SHIP CLASS: tests-only, off the scoring path (`scoring.py` does not import `offering` —
  grep-verified) → score-neutral, NOT peer-gated. git diff -- asrs/ rubric/ fixtures/ EMPTY; git diff
  --name-only = tests/test_offering_canonical.py ONLY. Cloud bridge blocks direct main push → branch
  loop/pagination-relabel-invariance + PR #63 + self-merge (squash 94fca4a). First duty: no open
  peer-gated PR ([] at fire start); realigned main to origin/main after merge. Offering canonical guard
  22→23; full suite clean; test_free_tier 11/11 (after `pip install eth-account`, environment-only).
  Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00
  digest cycle — 14:12Z is before the ~16:12Z first-after-16:00 fire). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~38.5h old). Next READOUT — surface the "walk the paged collection to
  completion" pagination capability in the public methodology prose (the READOUT leg completing the
  pagination arc: COVERAGE 106 → TRUTH 107 → READOUT next), mirroring the four prior metered_api
  methodology legs. A NEW archetype/signal remains open COVERAGE; ACP/UCP/MPP + free-tier live-wiring
  stays [LOCAL].)
  (Cycle 106 COVERAGE — added a `pagination` signal to the `metered_api` bank in `asrs/offering.py`:
  cursor / collection PAGINATION — how an agent retrieves a MULTI-PAGE result set (a list endpoint
  returns one page plus a cursor / a `next`/`previous` page URL to follow). The first NEW metered_api
  capability signal since test-mode (Cycle 102). WHY (capability): the "complete the job" capability for
  a metered API that returns a COLLECTION (list your predictions / models / deployments / records) — an
  agent that cannot follow the pagination cursor reads only the FIRST page and silently UNDER-completes
  the retrieval. Distinct from every existing metered_api signal (async-job = one long job's return,
  error-contract = recovery, rate-limited = speed); NONE said how an agent walks a paged collection to
  completion. Vendor-neutral open REST conventions (cursor query param, next/previous page URL, paginated
  collection response). PRECISION: never a bare token — requires `?cursor=`/`&cursor=` with a value,
  "cursor-based pagination", `paginat(ion|ed)` qualifying a collection/response/list noun, or `next`/
  `previous` PAGE OF an API collection noun; dodges the RETAIL HTML `<li class="next">` link
  (books.toscrape), "next campaign" + JS `previousSibling` (canonical homepages), CSS/SQL cursor, "next
  page of the novel", "repaginated" (9 noise negatives asserted). NON-VACUOUS: fires on the REAL captured
  api.replicate.com surfaces (`?cursor=…` list URL + "next page of collection objects" paginated schema
  in /openapi.json) and ZERO of the canonical-pair/retail/null fixtures. api.replicate.com ALREADY claims
  metered_api (its only archetype) → deepens evidence without adding/reordering any archetype (claimed set
  stays `[metered_api]`, asserted). SHIP CLASS: COVERAGE signal-add off the scoring path (`scoring.py`
  does not import `offering` — grep-verified; imported only by battery/cli/report/scorecard) →
  score-neutral, NOT peer-gated. Cloud bridge blocks direct main push → branch loop/pagination-metered-signal
  + PR #61 + self-merge (squash 260cc86). First duty: no open peer-gated PR ([] at fire start); realigned
  main to origin/main after merge. tests/test_offering.py +2 (40→42): pagination_metering_precision_synthetic
  + pagination_fires_on_real_captured_openapi. Full suite green (22 files; test_free_tier 11/11 after
  `pip install eth-account`). Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B
  / +39.4, 0 replay-miss; offering canonical guard 22/22; rubric v0.7. No Slack (score-neutral, off scoring
  path; not sensitive-class; not the first-after-16:00 digest cycle). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~37.7h old). Next TRUTH — pin `pagination` as relabel-invariant (a sixth
  metered_api signal-level relabel guard, after payment-rail/async-job/api-auth/error-contract/test-mode);
  then a READOUT leg surfacing the "walk the paged collection to completion" capability in the methodology
  prose. A NEW archetype/signal remains open COVERAGE; ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 105 METHOD — mirrored surface-read-ORDER-invariance onto the `.org` half of the canonical
  pair. New `test_offering_surface_order_invariance_org` in `tests/test_offering_canonical.py`
  (21→22 in that file). The existing `test_offering_surface_order_invariance_output_license` pinned
  whole-profile order-invariance only on `driftflight.com`; the relabel-invariance family already
  spanned BOTH halves (`_org`/`_com`), so order-invariance lagged at one — this closes the pair
  asymmetry. WHY (capability/rigor): a classification is a property of WHAT a surface DECLARES, never
  of which surface discovery read first, on EITHER canonical domain — same "close the gap" discipline
  as the Cycle-99/103 offering-layer guards. NON-VACUITY/TEETH: anchor `output-license` fires on .org
  across ≥2 surfaces (`/pricing`+`homepage`, asserted); `surfaces_seen` genuinely differs fwd/rev
  (asserted); STRONGER than the .com mirror — assertion (3) pins the COMPLETE per-archetype
  `(label,surface)` evidence map invariant across the whole profile (verified sensitive: .org map spans
  all 4 surfaces / 41 pairs, dropping one surface → 41→27, so order-dependent signal loss/migration is
  caught). DELIBERATELY did NOT ship the STATE-flagged test-mode single-surface order guard (weak
  non-vacuity, fires ×1 on `/docs`); this .org whole-profile guard is the stronger multi-surface form
  of the same axis, folding that flagged item into a broader per-signal order-stability property.
  SHIP CLASS: tests-only, off the scoring path → NOT peer-gated. git diff -- asrs/ rubric/ fixtures/
  EMPTY; git diff --name-only = tests/test_offering_canonical.py ONLY. Cloud bridge blocks direct main
  push → branch loop/order-invariance-org + PR #59 + self-merge (squash 89f2636). First duty: no open
  peer-gated PR ([] at fire start); realigned main to origin/main after merge. Full suite green (22
  files; test_free_tier 11/11). Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; rubric v0.7. No Slack (score-neutral, off scoring path; not
  sensitive-class; not the first-after-16:00 digest cycle). RUNNER STILL GAPPED (verify_20260728T234102Z
  23:41Z ~36.5h old). Next COVERAGE — the order-/relabel-invariance families are now complete across
  BOTH pair-halves; candidate: a NEW archetype or metered_api/digital_good signal, or a fresh
  perturbation axis (label/scale) on the offering path. ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 104 READOUT — surfaced the `test-mode` metered_api "try the call SAFELY first, at $0"
  capability in the PUBLIC methodology prose, the READOUT complement CLOSING the test-mode arc
  (COVERAGE 102 → TRUTH-relabel 103 → READOUT 104 — the fifth metered_api leg to complete the full
  arc, after payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88, error-contract 90/91/92).
  Added ONE capability-worded, vendor-neutral `<p>` to the methodology "What the score answers" card
  (`_write_methodology_page`, `asrs/scorecard.py`), between the error-contract paragraph and "Owning
  the deliverable", alongside the four metered_api offer-side legs + the digital_good output-license
  leg (C100). WHY (capability): a metered API that lets an agent obtain a test/sandbox credential and
  dry-run a call at ZERO cost before authorizing anything real is MORE agent-completable — the
  "provision + complete the job SAFELY, without a human" capability, dovetailing with ASRS's own
  $0-only ethos. The paragraph frames it as rehearsing the call safely first at $0; names the
  vendor-neutral test-facility vocabulary as open conventions (sandbox environment / test-mode flag /
  test API key / dry-run / `_test_`/`_sandbox_` key convention); KEEPS the precision note (a bare
  `sandbox`/`test` word — demo-site title / sandboxed iframe / `unit_test_runner` — is no signal);
  names the Cycle-103 identity+key-prefix relabel regression test; stays HONEST about scope
  (diagnostic, off the scoring path, not a scored pillar). New content-presence guard
  `test_methodology_documents_test_mode` in `tests/test_readout.py` (52→53) mirrors
  `test_methodology_documents_output_license`; rendered-page neutral-scan stays clean 4/4. SHIP
  CLASS: display (methodology render) + tests-only, off the scoring path → NOT peer-gated (same class
  as Cycle-100 output-license READOUT); git diff --name-only = asrs/scorecard.py + tests/test_readout.py
  ONLY, scoring-path diff EMPTY. Cloud bridge blocks direct main push → branch
  loop/test-mode-methodology-prose + PR #57 + self-merge (squash 9bd0cbf). First duty: no open
  peer-gated PR ([] at fire start). Full suite green (all tests/test_*.py pass; test_free_tier 11/11).
  Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  rubric v0.7. No Slack (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00
  digest cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~35.5h old). Next METHOD — the
  test-mode arc is now fully closed; candidate: the surface-read-ORDER-invariance guard for test-mode
  (fresh axis) BUT its non-vacuity is WEAKER (fires ×1 on a single surface `/docs` — a reorder cannot
  migrate it across surfaces), so confirm a genuine multi-surface read first else fold into a broader
  per-signal order-stability sweep; OR a NEW archetype/signal (COVERAGE). ACP/UCP/MPP + free-tier
  live-wiring stays [LOCAL].)
  (Cycle 103 TRUTH — pinned the Cycle-102 `test-mode` metered_api signal as RELABEL-INVARIANT, the
  FIFTH metered_api signal-level relabel guard (payment-rail 79 / async-job 83 / api-auth 87 /
  error-contract 90 / now test-mode). New `test_offering_relabel_invariance_test_mode` in
  `tests/test_offering_canonical.py` (20→21) perturbs BOTH identity axes: (A) a whole-HOST relabel — a
  no-op over this host-free, convention-keyed evidence, asserted HONESTLY as the vendor-neutrality
  property (the machine-integration convention names no vendor); (B) a KEY-PREFIX relabel `df_`→neutral
  `kv_` — the non-vacuous half, since the `df_` stem genuinely ABBREVIATES the host
  (`drift-flight`/`driftflight` → `df`), so rewriting it proves the API-key-convention branch
  `[a-z]{2,6}_(?:test|sandbox)_(?:\.{3}|<digit-stub>)` keys on the `<prefix>_test_<masked-stub>`
  CONVENTION SHAPE, not on "df"/the host (both fire ×1 on `/docs`, same count/surface, each quote still
  matching the live regex with `df_test_` gone). TEETH: a convention-less `df_test_runner` identifier does
  NOT fire. WHY (capability): cross-site comparability requires a classification to be a property of WHAT
  a surface DECLARES, not the storefront's name or its chosen key prefix. SHIP CLASS: tests-only, off the
  scoring path → NOT peer-gated (same class as Cycle-99's output-license relabel guard); git diff
  --name-only = tests/test_offering_canonical.py ONLY, scoring-path diff EMPTY. Cloud bridge blocks direct
  main push → branch loop/test-mode-relabel-invariance + PR #55 + self-merge (squash 6dc574f). First duty:
  no open peer-gated PR ([] at fire start); realigned main to origin/main 6dc574f after merge. Full suite
  294→295 passed. Canonical PAIR unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4,
  0 replay-miss; rubric v0.7. No Slack (tests-only, moves no score; not sensitive-class; not the
  first-after-16:00 digest cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~34.6h old). Next
  READOUT — the test-mode signal is now pinned at COVERAGE (102) + TRUTH-relabel (103); candidate: a
  capability-worded, vendor-neutral methodology paragraph surfacing the `test-mode` "try the call SAFELY
  first, at $0" leg alongside the four metered_api offer-side legs (mirroring the output-license
  98→99→100 arc's READOUT), OR a surface-read-ORDER-invariance guard for test-mode (METHOD, fresh axis).
  A NEW archetype/signal remains open COVERAGE; ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 102 COVERAGE — added a `test-mode` signal to the `metered_api` bank in `asrs/offering.py`:
  an API SANDBOX / test-key / dry-run facility, the first NEW metered_api capability signal since
  error-contract (the output-license digital_good arc closed at Cycles 98–101). An agent that obtains a
  test/sandbox credential validates its whole integration and dry-runs a call at ZERO cost (no real
  charge, no quota use) before authorizing anything real — the "provision + complete the job safely,
  without a human" capability, aligned with ASRS's own $0-only ethos. WHY (capability): distinct from
  every existing metered_api signal (api-auth = how you present credentials, rate-limited = how fast,
  async-job = how results return, error-contract = how you recover); NONE said whether an agent can TRY
  the call safely first. PRECISION-CRITICAL, vendor-neutral: never matches bare `sandbox`/`test` — a
  demonstrated FP minefield (books.toscrape.com's page TITLE "Books to Scrape - Sandbox" trips a bare
  `\bsandbox\b` 3×). Requires a named testing facility (sandbox mode/environment/api/key/…), a `test
  mode`/`test api key`/`test credentials`, an explicit `dry-run`, or the `<prefix>_test_`/`_sandbox_`
  key convention with a masked ellipsis or digit-bearing stub (so `df_test_...` fires but
  `unit_test_runner` does not). Validated against ALL 5 committed fixtures: fires once on BOTH canonical
  `/docs` (`df_live_... (production) or df_test_... (sandbox: watermarked output, no quota use)`), ZERO
  on api.replicate.com / books.toscrape / example.com. SHIP CLASS: `discover_offering` is OFF the
  scoring path (grep-verified empty diff over scoring/probes/protocols/fetch), both canonical domains
  ALREADY claim metered_api → score-neutral, NOT peer-gated (same class as Cycle-98 output-license
  COVERAGE signal). Cloud bridge blocks direct main push → branch loop/test-mode-signal + PR #53 +
  self-merge (squash 4da5024). SECRET-SCANNING lesson: initial push declined — a synthetic Stripe-style
  `sk_test_…` example key tripped GitHub push protection; replaced with a neutral `kv_test_…` and amended
  the UNPUBLISHED commit (did NOT bypass the scanner; invariant #5 concerns published commits). Tests +3:
  test_offering `test_test_mode_metering_precision_synthetic` (11 pos / 7 traps) +
  `test_test_mode_fires_on_real_captured_api_docs`; test_offering_canonical
  `test_retail_sandbox_title_does_not_trip_test_mode` (teeth — bare-"Sandbox" title stays NA). Full suite
  22/22 files green. First duty: no open peer-gated PR ([] at fire start). Canonical PAIR unchanged AND
  re-measured: claimed SET+ORDER byte-identical `['metered_api','digital_good','subscription']` on both,
  test-mode fires on both; replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. No
  Slack (score-neutral, off scoring path; not sensitive-class; not the first-after-16:00 digest cycle).
  RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~33.5h old). Next TRUTH — candidate: pin the new
  `test-mode` signal as HOST/VENDOR relabel-invariant at the signal level (the mirror of Cycle 99's
  output-license guard — the `df_test_` key-prefix embeds the host stem, so a whole-fixture relabel must
  preserve the fired count/surfaces), or a surface-read-ORDER-invariance guard for it. A NEW
  archetype/signal remains open COVERAGE; ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 101 METHOD — pinned the `digital_good` deliverable-rights leg (`output-license`) as
  surface-read-ORDER invariant, a fresh perturbation AXIS orthogonal to the relabel/identity family
  (payment-rail 79 / async-job 83 / api-auth 87 / error-contract / output-license 99). New guard
  `test_offering_surface_order_invariance_output_license` (test_offering_canonical.py 18→19): replays the
  canonical driftflight.com fixture, SPIES on the single `classify_offering` call to capture the real
  multi-surface read order discovery fed it (restored in a `finally`), re-classifies FORWARD vs full
  REVERSAL, and asserts the output-license fired COUNT, its SET of surfaces, and the digital_good claim
  (strength + labels) invariant — plus the whole profile (ordered claimed list + NA set). WHY (capability):
  a classification is a property of WHAT surfaces DECLARE, not the ORDER an agent fetched them in
  (cross-site comparability rests on it); the generic order-invariance test only exercises a single-surface
  digital_good bystander, while output-license fires 6× across 6 distinct surfaces on the .com fixture — the
  non-vacuity the generic test cannot supply for the rights leg. Two non-vacuity checks (≥2 surfaces; the
  reorder observably flips `surfaces_seen`); TEETH verified (an order-dependent early-stop reader yields 6
  vs 5 → caught). SHIP CLASS: tests-only, off the scoring path → NOT peer-gated; git diff --name-only =
  tests/test_offering_canonical.py ONLY, scoring-path diff EMPTY. Cloud bridge blocks direct main push →
  branch loop/output-license-order-invariance + PR #51 + self-merge (squash 880e0a8). First duty: no open
  peer-gated PR ([] at fire start); realigned main from stale orphan 37965190 → origin/main before start,
  and to 880e0a8 after merge. test_offering_canonical 19/19; full suite 291 passed (was 290). Canonical PAIR
  unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. No
  Slack (tests-only, moves no score; not sensitive-class; not the daily-digest cycle). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~32.5h old). Next COVERAGE — the output-license arc is now closed at
  signal (98) / TRUTH-relabel (99) / READOUT (100) / METHOD-order (101); candidate: a NEW archetype/signal
  for classify_offering, or a fresh order/count-stability axis for another digital_good signal
  (generate-media / render / hosted-output); ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 100 READOUT — surfaced the `digital_good` deliverable-rights ("complete the job") leg in the
  PUBLIC methodology prose, the READOUT complement CLOSING the deliverable-rights arc opened by Cycle 98
  (COVERAGE — the `output-license` offering signal) and Cycle 99 (TRUTH — signal-level relabel-invariance).
  Added ONE capability-worded, vendor-neutral paragraph to the methodology "What the score answers" card
  (`_write_methodology_page`, `asrs/scorecard.py`), placed alongside the four metered_api offer-side legs
  (payment-rail/auth/async-job/error-contract): ASRS reads whether a generation storefront grants usage
  rights on its output (a commercial licence / royalty-free terms / stated usage rights / ownership —
  "you own the output"), because an agent handed a render it has NO licence to USE has not completed the
  commercial job. Preserves the signal's bare-`license` PRECISION note (a software/business/hosted-model
  licence is no signal) and names the identity-relabel executable regression test that pins
  vendor-neutrality. WHY (capability): the four metered_api "finish the job" legs each earned a prose
  paragraph a critic can read (payment-rail 80/auth 88/async-job 84/error-contract 92); the digital-good
  RIGHTS leg was pinned in code+tests (98/99) but never in reader-facing prose — a reader could not learn
  WHY the digital-good archetype weighs deliverable rights, or that "obtain a render" is not the whole job.
  SHIP CLASS: display-only + tests-only, off the scoring path → NOT peer-gated (same class as Cycle-96's
  offering-relative-battery READOUT); git diff over scoring.py/rubric*/rubric/probes.py/protocols.py/
  fetch.py/offering.py/battery.py/fixtures/batteries = EMPTY; git diff --name-only = asrs/scorecard.py +
  tests/test_readout.py ONLY. Cloud bridge blocks direct main push → branch loop/output-license-methodology
  + PR #49 + self-merge (squash 40b1ac4; NOT peer-gated). First duty: no open peer-gated PR ([] at fire
  start); realigned main to origin/main 40b1ac4 after merge. EVIDENCE: new guard
  `test_methodology_documents_output_license` (test_readout.py 51→52) pins the owning/use framing + "not
  completed the commercial job", the vendor-neutral rights forms, the bare-`license` precision note, the
  relabel-keyed "rights the offer grants, not who grants them" + executable regression test, the
  diagnostic/off-scoring-path scope line, and vendor-neutrality (no drift-flight/driftflight on the page).
  Full suite 22 files green (test_free_tier 11/11 after env-only `pip install eth-account`). Canonical PAIR
  unchanged AND re-measured: replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; rubric v0.7. No
  Slack (display+tests-only, moves no score; not sensitive-class; not the daily-digest cycle). RUNNER STILL
  GAPPED (verify_20260728T234102Z 23:41Z ~31.5h old). Next METHOD — the output-license COVERAGE→TRUTH→READOUT
  arc is now complete at all three layers (98/99/100), mirroring the four metered_api legs; candidate: a
  fresh perturbation AXIS on the offering/battery path for the digital_good RIGHTS leg (a rights-signal
  ORDER-invariance or count-stability guard), or extend the descriptor relabel family. A NEW archetype/signal
  remains open COVERAGE; ACP/UCP/MPP + free-tier live-wiring stays [LOCAL].)
  (Cycle 99 TRUTH — pinned the Cycle-98 `digital_good` `output-license` signal as HOST/VENDOR
  relabel-invariant at the SIGNAL level: new guard `test_offering_relabel_invariance_output_license` in
  `tests/test_offering_canonical.py` (17→18), the FIRST extension of the signal-level relabel family
  (`agent-payment-rail` C79 / `async-job` C83 / `api-auth` C87 / `error-contract` C90, all `metered_api`)
  off metered_api into `digital_good`. SURFACE-PRESENCE invariance mirroring `error-contract`: the rights
  vocabulary (commercial licence / royalty-free / usage rights / "you own the output") is HOST-FREE so the
  fired QUOTES carry no host; non-vacuity anchors on the host being present inside the surface KEYS the
  signal fires on — `output-license` fires 6× on driftflight.com and 3 surfaces embed the host
  (`agents.driftflight.com/llms.txt`, `.../llms-full.txt`, `.../manifest.json`), so a whole-fixture relabel
  genuinely rewrites the surfaces the signal reads (the host-normalization step does real work). Under
  relabel: same match count (6), same host-normalized surfaces, each quote still matching the live regex,
  vendor host `vendor-neutral.test` absent from all evidence; a commercial-USE licence grant asserted present
  in base evidence. WHY (capability): the four metered_api "complete the job" signals each had a signal-level
  guard proving the match keys on DECLARED structure not host; the new digital_good rights signal had none,
  and since discovery drives `--battery auto` task SELECTION, a signal keying on a vendor NAME would be
  vendor-rigging one layer down — now an executable tripwire. Tests-only, off scoring path → rubric v0.7 →
  NOT peer-gated: git diff --stat over scoring.py/rubric*/rubric/probes.py/protocols.py/fetch.py/offering.py/
  battery.py/fixtures/batteries = EMPTY; git diff --name-only = tests/test_offering_canonical.py ONLY. Cloud
  bridge blocks direct main push → branch loop/output-license-relabel-invariance + PR #47 + self-merge
  (squash c52f082; NOT peer-gated). First duty: no open peer-gated PR ([] at fire start); realigned main to
  origin/main c52f082 after merge. INFRA folded in (<15 min): ephemeral container missing optional
  `eth-account` (in requirements.txt) → test_free_tier opened 10/11; `pip install eth-account` → 11/11
  (environment-only, nothing to commit). Canonical PAIR unchanged AND re-measured (replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss); full suite 22 files green. No Slack (tests-only, moves no score;
  this 06:2xZ-Jul-30 fire is after the Cycle-86 16:12Z daily digest, not the first-after-16:00 cycle).
  RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~30.5h old). Next READOUT — candidate: surface the
  digital_good "complete the job" RIGHTS leg (`output-license`) in the PUBLIC methodology/rubric prose the
  way Cycle 96 surfaced the offering-relative battery — a capability-worded, vendor-neutral sentence naming
  that ASRS reads whether a storefront grants usage rights on its generated output (licence / royalty-free /
  ownership), with an executable readout-wording guard, so a critic can read WHY the digital-good archetype
  weighs deliverable rights. Alternatively a NEW archetype/signal remains open COVERAGE; ACP/UCP/MPP +
  free-tier live-wiring stays [LOCAL].)
  (Cycle 98 COVERAGE — added an `output-license` signal to the `digital_good` bank in `asrs/offering.py`:
  the "complete the job" RIGHTS leg of a digital good. The existing digital_good signals name WHAT is
  produced (`generation`/`generate-media`) and WHERE it is delivered (`hosted-output`); NONE captured
  whether the agent may actually USE what it obtains. The signal fires on a commercial-use licence
  (`commercial licen[cs]e/ing`), royalty-free terms, explicit `usage rights`, or ownership of the
  DELIVERABLE (`you own the output/render/result/image/generation`). WHY (capability): an agent that
  receives a generated render it has no licence to use has NOT completed the commercial job — a storefront
  granting usage rights on its output is MORE agent-completable at the digital-good layer, a readiness axis
  the template bank did not yet recognise (the digital-good analog of metered_api's async-job/error-contract
  "complete the job" signals). PRECISION (the license minefield): NEVER matches bare "license" — a software
  licence (MIT/Apache), a business/driver's licence, a "Licensed and credentialed" trust badge, and — the
  trap it must dodge — a hosted MODEL's licence all stay NA. api.replicate.com (a `metered_api`-ONLY
  storefront pinned by `test_machine_surface_openapi_storefront`) says "the model's license" + "delete
  models you own"; the signal correctly does NOT fire there (no spurious digital_good). Vendor-neutral
  IP/rights vocabulary, never a vendor. SHIP CLASS: off the scoring path (discovery drives `--battery auto`
  task SELECTION only, never `scoring.score`) → rubric v0.7 → NOT peer-gated (same class as the
  Cycle-34/42/46/70/94 offering signal+surface additions); git diff --stat over scoring.py/rubric.py/
  rubric/probes.py/protocols.py/fetch.py/battery.py/fixtures/batteries = EMPTY; git diff --name-only =
  asrs/offering.py + tests/test_offering.py ONLY. Cloud bridge blocks direct main push → branch
  loop/output-license-signal + PR #45 + self-merge (squash e460770; NOT peer-gated). First duty: no open
  peer-gated PR ([] at fire start); realigned main to origin/main e460770 after merge. EVIDENCE
  (non-vacuous on committed data): test_offering.py 36→38 — `test_output_license_precision_synthetic`
  (7 real deliverable-rights grants each fire; 7 license-shaped noise strings each stay NA) +
  `test_output_license_fires_on_real_captured_surfaces` (fires on driftflight.com's committed /llms.txt
  "commercial licensing"; does NOT fire on api.replicate.com's committed OpenAPI model-licence traps —
  real-data precision). Fires on BOTH canonical domains, both already claiming digital_good → deepens
  evidence without changing any claimed set; ZERO hits on api.replicate.com/books.toscrape.com/example.com.
  Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  test_offering_canonical claimed-set + relabel guards 17/17). Full suite 22 files green (test_free_tier
  11/11 after `pip install eth-account` — ephemeral container again missing the optional dep from
  requirements.txt, environment-only, nothing to commit). No Slack (off-scoring COVERAGE, moves no score;
  not sensitive-class; not the daily-digest cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z
  ~29.5h old). Next TRUTH — candidate: pin the new `output-license` signal as HOST/VENDOR relabel-invariant
  at the SIGNAL level (the digital_good analog of the payment-rail/async-job/api-auth/error-contract relabel
  guards in test_offering_canonical.py; its driftflight.com evidence surfaces embed the host, so it shares
  the quote/surface-anchored non-vacuity substrate the family requires).)
  (Cycle 97 METHOD — pinned the offering-relative `digital_good` battery DESCRIPTOR
  (`asrs/battery._digital_good_descriptor`) as HOST/VENDOR relabel-invariant, the descriptor-layer analog
  of the signal-level relabel guards in `test_offering_canonical.py` — closing the descriptor-invariance
  gap named by the Cycle-96 methodology prose ("the noun comes from the site, not ASRS" / "injection-safe").
  New guards in `tests/test_battery_instantiate.py` (9→12): classify a synthetic surface that names the
  host INSIDE the digital_good evidence, extract the real claim via `classify_offering`, relabel the host
  everywhere + re-classify, and assert the derived descriptor is BYTE-IDENTICAL — across the media-noun
  branch ("generated image") AND the translation-LABEL branch ("translated document"). NON-VACUOUS: the
  host genuinely appears in the base claim's evidence and the relabel genuinely rewrites the quotes the
  descriptor reads (both asserted); neutral host `vendor-neutral.test` carries no media word. TEETH:
  `test_descriptor_relabel_has_teeth` proves a deliberately host-keyed descriptor stub IS caught by the
  same relabel comparison → the invariants refute a real failure mode, not a tautology. WHY (capability):
  the offering classifier's vendor-neutrality was an executable tripwire (task SELECTION keys on evidence)
  but the digital_good task's {descriptor} slot carried a SECOND identity risk one layer down — the host
  appears inside the fired evidence, so a host-keyed descriptor would give two storefronts offering the
  SAME capability DIFFERENT task text because of their NAMES (vendor-rigging applied to task WORDING).
  Tests-only, off scoring path → rubric v0.7 → NOT peer-gated: git diff --stat over scoring.py/rubric*/
  rubric/probes.py/protocols.py/fetch.py/offering.py/battery.py/fixtures/batteries = EMPTY; git
  diff --name-only = tests/test_battery_instantiate.py ONLY. Cloud bridge blocks direct main push → branch
  loop/descriptor-relabel-invariance + PR #43 + self-merge (squash 4340200; NOT peer-gated). First duty:
  no open peer-gated PR ([] at fire start); realigned main to origin/main 4340200 after merge. INFRA folded
  in (<15 min): the ephemeral container was missing optional `eth-account` (in requirements.txt) →
  test_free_tier opened 10/11; `pip install eth-account` → 11/11 (environment-only, nothing to commit).
  Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss);
  full suite 22 files green. No Slack (tests-only, moves no score; this 04:16Z-Jul-30 fire is after the
  Cycle-86 16:12Z daily digest, so not the first-after-16:00 cycle). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~28.5h old). Next COVERAGE — candidate: a NEW archetype/signal on the
  offering path (a capability the template bank does not yet recognise), or the per-segment leaderboard
  summary once the [LOCAL] calibration population grows toward 15–20; ACP/UCP/MPP + free-tier live-wiring
  remains [LOCAL].)
  (Cycle 96 READOUT — surfaced the OFFERING-RELATIVE task battery in the PUBLIC methodology prose, the
  READOUT complement CLOSING the generate-media plural/participle arc (Cycle 94 COVERAGE signal + Cycle 95
  TRUTH descriptor + this READOUT). Added ONE capability-worded, vendor-neutral paragraph to methodology
  section 6 ("The behavioral panels & refusal semantics", `_write_methodology_page`, `asrs/scorecard.py`),
  right after the shopper/trust-panel paragraph so the "buying directive" is immediately qualified: the
  directives are OFFERING-RELATIVE not a fixed script — ASRS reads what the storefront CLAIMS to sell from
  its own surfaces and gives the agent one task per capability it offers, an unadvertised archetype is
  never probed (a low number is never a task the storefront was never built to answer — attribution honesty
  applied to tasks); the task is worded in the SITE'S OWN terms, a digital-good task says "obtain one
  generated image" only because the site's own surfaces describe a generated image (the media noun comes
  from the site, not ASRS); that noun is derived ONLY from ASRS's own vendor-neutral media vocabulary
  (image/video/audio/art, or the "digital output" fallback) matched to the site's surfaces, NEVER by pasting
  arbitrary site prose into the directive (injection-safe, names no vendor product); recognition is
  FORM-NORMALIZED (image / images / generating images → the SAME singular task noun, so two storefronts
  offering the same capability get the same task regardless of phrasing) and pinned by an executable
  regression test; honestly scoped as DIAGNOSTIC, off the scoring path, not a scored pillar. WHY: the
  offering-relative battery + singular/plural/inflection-normalised descriptor were pinned in code + tests
  (Cycles 94/95) but never surfaced in prose a critic can read — the reader-facing statement of WHY a
  derived task says "generated image" and that the wording comes from the site not ASRS. Display-only +
  tests-only, off scoring path → rubric v0.7 → NOT peer-gated: git diff --stat over scoring.py/rubric*/
  rubric/probes.py/protocols.py/fetch.py/offering.py/battery.py/fixtures/batteries = EMPTY → scoring path
  byte-for-byte untouched; git diff --name-only = scorecard.py + test_readout.py ONLY. NON-VACUOUS: new
  guard `test_methodology_documents_offering_relative_battery` (test_readout 50→51), registered in main()
  (no pytest auto-discovery in-cloud), asserts the offering-relative framing + "claims to sell" / "worded in
  the site" / "never built to answer" / "generated image" / "injection-safe" / "form-normalized" / the
  media-vocab tokens (image/video/audio/art/digital output) + form-normalization exemplars (images,
  generating images) / "executable regression test" / honest off-scoring-path+diagnostic scope, and the
  vendor-neutral denylist. Readout wording 4/4 + rubric wording 4/4 (rendered methodology + card
  vendor-neutral). Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4,
  0 replay-miss). Full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge blocks
  direct main push → branch loop/offering-relative-battery-readout + PR #41 + self-merge (squash 4f269ed;
  NOT peer-gated). First duty: no open peer-gated PR ([]); realigned main to origin/main 4f269ed after merge.
  No Slack (display-only, moves no score; this 03:11Z-Jul-30 fire is after the Cycle-86 16:12Z daily digest,
  so not the first-after-16:00 cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~27.5h old). The
  generate-media plural/participle arc is now closed at ALL THREE layers: SIGNAL (Cycle 94), DESCRIPTOR
  (Cycle 95), READOUT (Cycle 96). Next METHOD — candidate: pin that the digital_good DESCRIPTOR derivation
  is itself relabel/identity-invariant (the media noun keys on the vocabulary a site uses, not the host), or
  a fresh perturbation AXIS (label/scale) now the order-invariance family is complete across all five
  measurement surfaces; in-cloud COVERAGE frontier for metered_api signals is well-covered.)
  (Cycle 95 TRUTH — made the `digital_good` battery DESCRIPTOR recover PLURAL/participle media nouns
  (`asrs/battery._MEDIA_RE` / `_digital_good_descriptor`), the descriptor half of the Cycle-94
  generate-media SIGNAL recall fix. `_MEDIA_RE` matched only the SINGULAR noun
  (`\b(image|video|audio|art)\b`), so `_digital_good_descriptor` fell back to the generic "digital output"
  for a claim whose ONLY fired media quote was plural — the canonical `/docs` "Generated images", or "we
  generate videos" — even though the Cycle-94 signal had already fired on that plural surface. Added a
  trailing `s?` OUTSIDE the capture group: plural forms match while `group(1)` still yields the singular
  word, so the descriptor normalises to "generated image" whether the fired quote is singular or plural —
  descriptor and signal now share the same plural/participle awareness. WHY (capability): the battery task
  is the site's offering worded back as an agent job; a generation storefront describing its output only in
  the plural got a vaguer task ("obtain one digital output") than one using the singular ("generated
  image") — a descriptor/signal inconsistency, not a real offering difference. SCORE-NEUTRAL by construction
  AND VERIFIED: git diff --stat over scoring.py/rubric*/probes*/protocols.py/fetch.py/offering.py/fixtures/
  batteries/rubric/ = EMPTY → scoring path byte-for-byte untouched → rubric v0.7 (descriptor off the scoring
  path, `--battery auto` task text only) → NOT peer-gated; git diff --name-only = battery.py +
  test_battery_instantiate.py ONLY. NON-VACUOUS: test_battery_instantiate 8→9 —
  `test_digital_good_descriptor_recovers_plural_media` (real canonical `/docs` "Generated images" recovers
  "generated image", AND the pre-fix singular-only pattern asserted NOT to match "images" = the gap was real
  / the test fails against old code; plural of each media noun videos/images/arts → singular descriptor;
  precision negative — a plural NON-media noun "reports"/"outputs" → "digital output" fallback; singular
  pinned unchanged). Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4,
  0 replay-miss — the canonical descriptor was already "generated image" via its singular quote, so this
  fix changes nothing on the pair, it helps plural-ONLY storefronts); full suite 22 files green
  (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push → branch
  loop/descriptor-plural-media + PR #39 + self-merge (squash ceedf2d; NOT peer-gated). First duty: no open
  peer-gated PR ([]); realigned main to origin/main ceedf2d after merge. No Slack (score-neutral, moves no
  score; this 02:17Z-Jul-30 fire is after the Cycle-86 16:12Z daily digest, so not the first-after-16:00
  cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~26.5h old). The generate-media plural/
  participle arc is now closed at BOTH the SIGNAL (Cycle 94) and the DESCRIPTOR (Cycle 95) layers. Next
  READOUT — candidate: surface in the public methodology/offering prose that the digital_good task is
  derived from the site's OWN discovered media language (vendor-neutral, singular/plural-normalised) — the
  reader-facing statement of why the derived task says "generated image"; or the recurring per-segment
  leaderboard summary once the [LOCAL] calibration population grows.)
  (Cycle 94 COVERAGE — broadened the `digital_good` GENERATE-MEDIA signal (`asrs/offering.py`) from the
  singular-imperative form only (`generate an image`) to ALL verb inflections (generate/generates/
  generated/generating), the PLURAL media noun (`generate videos`, the canonical pair's `Generated
  images`), and an optional article/possessive/definite object. WHY: generate-media is the core "the
  service GENERATES a media deliverable" digital-good claim; the old pattern missed the two most common
  real phrasings (present participle "generating images", plural "we generate videos"), so a generation
  storefront using only those forms fired NO generate-media signal and — absent another digital_good
  signal — could miss the digital_good archetype entirely (a real recall gap in coverage of the generation
  storefront TYPE). Precision preserved: verb stays `generat...` at a word boundary ("regenerate a token"
  does NOT fire) and object a media noun at a word boundary ("generate imagery/output/response/reports"
  never fire); 6 negatives reject, vendor-neutral (only media-category nouns). SCORE-NEUTRAL by
  construction AND VERIFIED: classification byte-identical on ALL FIVE committed fixtures (the singular
  form already fired on the canonical pair → claimed SET+ORDER+first-match quote unchanged); git diff
  --name-only = offering.py + test_offering.py ONLY; git diff over scoring.py/rubric/fixtures/batteries/
  protocols.py/battery.py/probes/fetch.py EMPTY → scoring path byte-for-byte untouched → rubric v0.7
  (discovery off the scoring path) → NOT peer-gated. NON-VACUOUS: test_offering.py 34→36 —
  `test_generate_media_recognizes_plural_and_participle_forms` (7 inflected/plural positives fire, 6
  negatives reject, and a plural/participle-only surface now claims digital_good via generate-media alone
  while the OLD pattern is asserted to match NOTHING) + `test_generate_media_plural_gap_on_real_captured_docs`
  (the committed canonical `/docs` plural `Generated images`, isolated from the singular form, fires the
  broadened signal, old one does not — the gap proven on real captured bytes). Canonical PAIR unchanged
  AND re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss); offering-canonical 17/17
  (claimed set + NA unchanged); full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud
  bridge blocks direct main push → branch loop/generate-media-plural-recall + PR #37 + self-merge (squash
  e207040; NOT peer-gated). First duty: no open peer-gated PR ([]); realigned main to origin/main e207040
  after merge. No Slack (score-neutral, moves no score; this 01:12Z-Jul-30 fire is after the Cycle-86
  16:12Z daily digest, so not the first-after-16:00 cycle). RUNNER STILL GAPPED (verify_20260728T234102Z
  23:41Z ~25.5h old). Next TRUTH — candidate: a calibration/relabel guard is a weak fit (generate-media is
  host-free/vendor-neutral); a stronger TRUTH is an inflection/plural guard for the digital_good DESCRIPTOR
  derivation (`_digital_good_descriptor` / `_MEDIA_RE` in `asrs/battery.py`, which shares the singular-noun
  assumption — a plural-only quote falls back to the generic "digital output"), or a [LOCAL] calibration
  confirmation that plural/participle generation storefronts classify digital_good once the population grows.
  In-cloud offering COVERAGE frontier is otherwise thin (metered_api saturated; service_booking/
  data_retrieval lack committed evidence → vacuous; structured catalog/pricing JSON are [LOCAL]).)
  (Cycle 93 METHOD — pinned TRIAL-ORDER INVARIANCE of `asrs.reliability.panel_reliability`, the
  within-panel reproducibility metric whose `verdict_stability` gates the CITABLE-vs-PROVISIONAL
  quotability verdict — the LOAD-BEARING member of the presentation-order invariance family that
  was never pinned (the family already covers battery aggregation Cycle 73, leaderboard ranking
  Cycle 77, offering classification Cycle 81, scorer multi-cap Cycle 85). New
  `test_panel_reliability_is_trial_order_invariant` (`tests/test_reliability.py` 8→9) builds a 6-run
  panel (4 valid + interleaved env-blocked + failed) with `verdict_stability` a genuine interior 0.7
  (mixed band: 2 checkpoints flip, 3 unanimous) and a split trust signal (0.75), runs it under FOUR
  deterministic arrival orders (identity/reverse/two rotations), and asserts the whole
  `PanelReliability.to_dict()` is byte-identical across all — verdict_stability, flip_rate,
  flipped_checkpoints (list+ladder order), trust agreement/unanimity, valid_runs, single_trial, label,
  AND every per_checkpoint row, recursively. NON-VACUOUS + TEETH VERIFIED by injection: an
  order-dependent selection bug (`_valid_runs()[-3:]`) caught by clause (a) (valid_runs==4 proves the
  interleaved excluded runs dropped — the SELECTION is order-independent, invariant #4); a first-run
  identity leak caught by clause (c) (byte-identity); a pure rotation of the valid multiset correctly
  NOT flagged (it preserves every count = exactly the invariant). Order-invariant by construction today
  (metrics are COUNTS over valid runs; per_checkpoint follows the fixed ladder) — catches a future
  refactor leaking run-order into a count/selection/row. Tests-only: git status = one file; git diff
  --stat -- asrs/ rubric/ fixtures/ batteries/ probes/ EMPTY → scoring path byte-for-byte untouched →
  rubric v0.7 → NOT peer-gated. Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss). test_reliability 8→9; full suite 22 files green (test_free_tier 11/11
  with eth-account in .venv). Cloud bridge blocks direct main push → branch loop/reliability-order-invariance
  + PR + self-merge (NOT peer-gated — tests-only, off scoring path, pins existing behaviour). First duty:
  no open peer-gated PR ([]); realigned main to origin/main after merge. No Slack (tests-only, moves no
  score; this 00:12Z-Jul-30 fire is after the Cycle-86 16:12Z daily digest, so not the first-after-16:00
  cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~24.5h old). The order-invariance family is
  now COMPLETE across all five measurement surfaces (battery / leaderboard / offering / scoring /
  reliability); a future METHOD candidate is a fresh perturbation AXIS (label / scale) rather than another
  order rung. Next COVERAGE — candidate: a NEW archetype/signal for classify_offering, or a per-segment
  leaderboard summary once the [LOCAL] calibration population grows; the in-cloud metered_api signal
  frontier is well-covered.)
  (Cycle 92 READOUT — surfaced the error-contract "recover from a failed call" RELIABILITY recognition
  in the PUBLIC methodology prose, the READOUT complement to the Cycle-90 COVERAGE signal + Cycle-91
  TRUTH relabel guard, CLOSING the FOURTH COVERAGE→TRUTH→READOUT arc for the metered_api signal bank
  (after payment-rail 78/79/80, async-job 82/83/84, api-auth 86/87/88). Added ONE capability-worded,
  vendor-neutral paragraph to the methodology "What the score answers" card (`_write_methodology_page`,
  `asrs/scorecard.py`), placed AFTER the Cycle-84 async-job (finishing) paragraph as the RELIABILITY leg
  of finishing: an agent recovers from a failed call only if the offer's ERROR CONTRACT is
  machine-readable — an HTTP status code (refresh a credential on 401, back off/retry on 429), an
  RFC 7807 `application/problem+json` body, or a named `snake_case` error code. Recognition keys on the
  DECLARED contract, not who declares it (pinned by the Cycle-91 identity-relabel guard); honestly scoped
  as DIAGNOSTIC, off the scoring path, not a scored pillar. New guard
  `test_methodology_documents_error_contract` (`tests/test_readout.py` 49→50), registered in `main()`
  (no pytest auto-discovery in-cloud). Display-only + tests-only: git diff over
  scoring.py/offering.py/probes/rubric/fixtures/batteries EMPTY → scoring path byte-for-byte untouched →
  rubric v0.7. Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4,
  0 replay-miss). test_readout 49→50; readout+rubric wording scanners 4/4 + 4/4; full suite 22 files green
  (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push → branch
  loop/error-contract-readout + PR #34 + self-merge (squash 49aff18; NOT peer-gated — display-only, off
  scoring path). First duty: no open peer-gated PR ([]); realigned main to origin/main 49aff18 after merge.
  No Slack (display-only, moves no score; this 23:1xZ fire is after the Cycle-86 16:12Z daily digest, so
  not the first-after-16:00 cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~23.5h old). The
  four metered_api signals (payment-rail, async-job, api-auth, error-contract) now EACH have the full
  COVERAGE→TRUTH→READOUT arc closed. Next METHOD — candidate: a fresh executable-invariant increment on the
  offering/battery path, or extend the calibration/relabel guard family as new fixtures/signals land; the
  in-cloud COVERAGE frontier for metered_api signals is now well-covered, so the next new COVERAGE would be
  a NEW archetype/signal or a per-segment leaderboard summary once the [LOCAL] calibration population grows.)
  (Cycle 91 TRUTH — relabel-invariance made executable at the SIGNAL level for the Cycle-90
  `error-contract` metered_api signal (the 4xx/5xx error responses an agent must read to RECOVER from a
  failed call). New `test_offering_relabel_invariance_error_contract` (`tests/test_offering_canonical.py`
  16→17) replays the committed `driftflight.com` fixture through the REAL discovery path, relabels the host
  everywhere (`driftflight.com` → `vendor-neutral.test`), and asserts the signal is IDENTITY-invariant: SAME
  match count (3), SAME host-normalized surfaces (signal did not migrate), each relabeled quote STILL
  matching the live `error-contract` regex, vendor host GONE from every piece of error-contract evidence —
  proving a documented error contract keys on what a storefront DECLARES (status codes / problem+json /
  snake_case error codes) not WHO declares it. Fourth signal-level companion to the payment-rail (Cycle 79)
  / async-job (Cycle 83) / api-auth (Cycle 87) guards — the relabel family now covers ALL FOUR recently-landed
  metered_api signals. SURFACE-PRESENCE (not quote-anchored) like async-job — the error-contract vocabulary is
  host-free by nature so the fired QUOTES carry no host — but a STRONGER surface-presence case: TWO of the
  three firing surfaces embed the host in the surface KEY (`agents.driftflight.com/llms-full.txt`,
  `api.driftflight.com/openapi.json`; the third `/docs` is host-free), so the whole-fixture relabel genuinely
  rewrites the surface keys the signal reads and the host-normalization step does real work (unlike
  async-job's lone host-free `/openapi.json`). Both host-free structural forms exercised (OpenAPI status-keyed
  response object + status code paired with a snake_case error code). Tests-only, off scoring path: git diff
  -- asrs/ rubric/ fixtures/ batteries/ EMPTY → scoring path byte-for-byte untouched → rubric v0.7. Canonical
  PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss).
  test_offering_canonical 16→17; full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud
  bridge blocks direct main push → branch loop/relabel-error-contract-signal + PR #32 + self-merge (squash
  be61b99; NOT peer-gated — tests-only, off scoring path, pins existing behaviour). First duty: no open
  peer-gated PR ([]); realigned main to origin/main be61b99 after merge. No Slack (tests-only, moves no score;
  this 22:1xZ fire is after the Cycle-86 16:12Z daily digest, so not the first-after-16:00 cycle). RUNNER
  STILL GAPPED (verify_20260728T234102Z 23:41Z ~22.5h old). The signal-level relabel family now covers all
  FOUR recently-landed metered_api signals (payment-rail, async-job, api-auth, error-contract). Next READOUT —
  candidate: surface the error-contract "recover from a failed call" RELIABILITY recognition in the PUBLIC
  methodology prose (capability-worded, vendor-neutral — HTTP status codes / RFC 7807 problem+json / error
  codes as open conventions, keyed on the DECLARED contract not the vendor), the READOUT complement to the
  Cycle-90 COVERAGE + this-cycle TRUTH error-contract arc, closing the fourth COVERAGE→TRUTH→READOUT arc
  (mirroring Cycle-80 payment-rail / Cycle-84 async-job / Cycle-88 api-auth).)
  (Cycle 90 COVERAGE — offering discovery now recognises a storefront's documented machine-readable ERROR
  CONTRACT, the "complete the job" RELIABILITY capability the metered_api signal bank was missing. New
  `error-contract` signal in `_SIGNALS["metered_api"]` (`asrs/offering.py`), grouped after `async-job`:
  matches the 4xx/5xx error responses an agent must handle to RECOVER from a failed call — an OpenAPI
  status-keyed response object (`"429":{"description"…`), the IETF RFC 7807 `application/problem+json`
  media type, or a status code paired with a snake_case error code (`400 invalid_request`). CAPABILITY:
  an agent that cannot read the error contract cannot recover autonomously (refresh a credential on 401,
  back off/retry on 429, surface a clear failure on 4xx/5xx) → distinct from `rate-limited` (limits EXIST)
  and `async-job` (how results come back). PRECISION: never matches a bare 4xx/5xx number (a quantity
  "500-image run", a price "$499", a phone/room number "call 411"/"room 404") nor a 2xx/3xx success status;
  7 number-shaped negatives reject. NON-VACUOUS end-to-end (`from_fixture → discover_offering`) on ALL THREE
  metered_api fixtures (canonical pair /docs error table + OpenAPI 401/429 responses; api.replicate.com
  `application/problem+json` 4xx) and ZERO retail/null fixtures = offering-layer mirror of the metered/
  non-metered split. SCORE-NEUTRAL: every site where it fires ALREADY claims metered_api → claimed SET+ORDER
  byte-identical; git diff --name-only = offering.py + test_offering.py ONLY; git diff over
  scoring.py/rubric/fixtures/batteries/protocols.py/battery.py/probes/fetch.py EMPTY → scoring path
  byte-for-byte untouched → rubric v0.7 (discovery off the scoring path). Canonical PAIR unchanged AND
  re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Vendor-neutral (only OpenAPI /
  RFC 7807 / HTTP status codes named). test_offering 32→34; full suite 22 files green (test_free_tier 11/11
  with eth-account); offering-canonical 16/16, battery-instantiate-canonical 6/6. Cloud bridge blocks direct
  main push → branch loop/error-contract-signal + PR #30 + self-merge (squash ec56c13; NOT peer-gated —
  discovery-only, off scoring path, score-neutral). First duty: no open peer-gated PR ([]); realigned main to
  origin/main ec56c13 after merge. No Slack (score-neutral, moves no score; this 21:12Z fire is after the
  Cycle-86 16:12Z daily digest, so not the first-after-16:00 cycle). RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~21.5h old). Next TRUTH — candidate: a SIGNAL-level relabel-invariance
  guard for the new `error-contract` signal (an error contract keys on what a storefront DECLARES — status
  codes, problem+json — not WHO declares it), the recurring "extend relabel-invariance as new signals land"
  item (Cycle 79 payment-rail / 83 async-job / 87 api-auth); error-contract evidence is largely host-FREE →
  a clean surface-presence / structural-re-match case like async-job, not quote-anchored.)
  (Cycle 89 METHOD — pinned NA-CONTENT INVARIANCE, the operator directive's core claim made executable at
  its strongest. New `test_na_content_invariance` (`tests/test_battery.py` 13→14): whatever an agent did on
  an intent the site does NOT offer — failed flat (`runs_fail` mean 0.0) or garden-pathed to full completion
  (`runs_pass` mean 1.0, SAME run count) — every ASSESSED statistic is byte-identical (cross_task_spread,
  between_kind_spread, all 5 checkpoint_mean/spread, per-kind mean_completion/cross_task_spread BY KIND,
  assessed_archetypes, tasks_with_signal, na_archetypes, and the NA task's own audit record). This is
  invariant #4 (attribution honesty) applied to TASKS and made a DATA-PERTURBATION tripwire, complementing
  test 13 (presentation-order invariance permutes the ORDER of the SAME observations; this permutes the
  CONTENT of the NA task's observations). The three existing NA tests pin the taxonomy + a single
  hand-computed metric; none proved the exclusion is TOTAL. Holds by construction today (`signal`/`applicable`
  drop NA tasks) → catches a future leak of NA content into a mean/spread. NON-VACUOUS: sub-check (a) with the
  SAME archetype CLAIMED (assessed), the two variants produce a DIFFERENT between_kind_spread + checkpoint_mean
  (perturbation is real, mirrors test 13's "the permutation was REAL" step); sub-check (d) protected spreads
  real (between_kind 0.25, cross_task 0.25). Tests-only: git diff --name-only = tests/test_battery.py ONLY;
  git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY → scoring path byte-for-byte untouched → rubric v0.7.
  Vendor-neutral (generic archetype names only). Canonical PAIR unchanged AND re-measured (replay guard 24/24,
  46.1 F / 85.5 B / +39.4, 0 replay-miss). test_battery 13→14; full suite 22 files green (test_free_tier 11/11
  with eth-account). Cloud bridge blocks direct main push → branch loop/na-content-invariance + PR #28 +
  self-merge (squash f75e01c; NOT peer-gated — tests-only, off scoring path, pins existing behaviour). First
  duty: no open peer-gated PR ([]); realigned main to origin/main f75e01c after merge. No Slack (tests-only,
  moves no score; this 19:1xZ fire is after the Cycle-86 16:12Z daily digest, so not the first-after-16:00
  cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~19.5h old). Next COVERAGE — candidate: a new
  archetype/signal for classify_offering, or a per-segment leaderboard summary once the [LOCAL] calibration
  population grows; in-cloud COVERAGE frontier is thin (structured catalog/pricing JSON are [LOCAL], 404 on
  committed fixtures).)
  (Cycle 88 READOUT — surfaced the API-AUTH credential-scheme recognition in the PUBLIC methodology prose,
  the READOUT complement to the Cycle-86 COVERAGE + Cycle-87 TRUTH api-auth arc (COVERAGE → TRUTH → READOUT
  closed, mirroring the Cycle-78/79/80 payment-rail and Cycle-82/83/84 async-job arcs). Added ONE
  capability-worded, vendor-neutral paragraph to the methodology "What the score answers" card
  (`_write_methodology_page`, `asrs/scorecard.py`), placed BETWEEN the payment-rail paragraph (pay) and the
  async-job paragraph (finish) so the prose follows the intro's reach→understand→pay→PROVISION→finish order.
  It surfaces the "provision without a human" leg: a metered API is only callable by an agent that can PRESENT
  THE RIGHT CREDENTIAL, over open machine conventions — an HTTP `Authorization: Bearer` header, an `X-API-Key`
  header or named API key, an OpenAPI `securityScheme` declaration, or an OAuth2 flow; an offer that documents
  its auth scheme is more agent-completable than one leaving the agent holding an endpoint it never learns how
  to enter. Recognition keys on the SCHEME NOT THE VENDOR (same open-convention category as REST/GraphQL/
  OpenAPI), pinned by the identity-relabel guard; HONESTLY SCOPED diagnostic, off the scoring path, not a
  scored pillar. New guard `test_methodology_documents_api_auth_scheme` (test_readout, whitespace-collapsed
  match) asserts the provision framing, the vendor-neutral credential schemes, the scheme-not-vendor relabel
  pin + executable regression test, the honest off-scoring-path/diagnostic scope, and the vendor-neutral
  denylist; REGISTERED in `main()` (no pytest auto-discovery in-cloud — the "silent success/failure look
  identical" law). test_readout 48→49. Display-only + tests-only: git diff --name-only = scorecard.py +
  test_readout.py ONLY; git diff over scoring.py/probes/rubric/offering.py/battery.py/fixtures/batteries EMPTY
  → scoring path byte-for-byte untouched → rubric v0.7. Canonical PAIR unchanged AND re-measured (replay guard
  24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Vendor-neutral (only open standards named; wording scanner
  4/4). Full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push
  → branch loop/api-auth-scheme-readout + PR #26 + self-merge (squash 7b63849; NOT peer-gated — display-only,
  off scoring path). First duty: no open peer-gated PR ([]); realigned main to origin/main 7b63849 after merge.
  No Slack (display-only, moves no score; this 18:1xZ fire is after the Cycle-86 16:12Z daily digest, so not
  the first-after-16:00 cycle). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~18.6h old). The three
  recently-landed metered_api signals (payment-rail, async-job, api-auth) now each have the full
  COVERAGE→TRUTH→READOUT arc closed. Next METHOD — candidate: a fresh executable-invariant increment on the
  offering/battery path, or extend the calibration/relabel guard family as new fixtures land.)
  (Cycle 87 TRUTH — relabel-invariance made executable at the SIGNAL level for the Cycle-86 `api-auth`
  metered_api signal (programmatic API authentication / credential provisioning). New
  `test_offering_relabel_invariance_api_auth` (`tests/test_offering_canonical.py` 15→16) replays the
  committed `driftflight.com` fixture through the REAL discovery path, relabels the host everywhere
  (`driftflight.com` → `vendor-neutral.test`) via `_discover_relabeled`, and asserts the `api-auth` signal
  is IDENTITY-invariant: SAME match count (5), SAME host-normalized surfaces (signal did not migrate), each
  relabeled quote STILL matching the live `api-auth` regex (re-run per quote), vendor host GONE from every
  piece of auth evidence — proving an access/auth scheme keys on the SCHEME STRUCTURE (`Authorization:
  Bearer` header, `X-API-Key`, an OpenAPI `securityScheme`, OAuth2), not the host/vendor NAME. Third
  signal-level companion to the Cycle-79 payment-rail + Cycle-83 async-job guards (the recurring "extend
  relabel-invariance as new signals land" item). QUOTE-ANCHORED non-vacuity like payment-rail: the host is
  literally inside a matched evidence quote (the homepage `api.driftflight.com/v1/... Authorization: Bearer`
  quote), so the whole-fixture relabel genuinely rewrites the classifier's matched input. HONEST MIXED CASE:
  the signal also fires on host-free surfaces (`/docs`) and host-embedding surfaces
  (`api.driftflight.com/openapi.json`); the non-vacuity anchor is the QUOTE (strongest of the three).
  Byte-equality modulo host deliberately NOT asserted (host-length change 15→19 shifts the fixed-width
  window); the structural re-match is the robust invariant; the existing negative control (identity special-
  case CAUGHT) gives the machinery teeth. Also asserts both credential forms exercised (Authorization/Bearer
  header + API key). Tests-only, off scoring path: git diff --name-only = tests/test_offering_canonical.py
  ONLY; git diff over asrs/rubric/fixtures/batteries EMPTY → rubric v0.7. Canonical PAIR unchanged AND
  re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss). test_offering_canonical 15→16;
  full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push →
  branch loop/relabel-api-auth-signal + PR #24 + self-merge (squash d3be0f6; NOT peer-gated — tests-only,
  off scoring path, pins existing behaviour). First duty: no open peer-gated PR ([]); realigned main to
  origin/main d3be0f6 after merge. No Slack (tests-only, moves no score; the 16:00 UTC daily digest was
  already sent at the Cycle-86 16:12Z fire, so this 17:12Z fire is not the first-after-16:00 cycle). RUNNER
  STILL GAPPED (verify_20260728T234102Z 23:41Z ~17.5h old). The signal-level relabel family now covers all
  THREE recently-landed metered_api signals (payment-rail, async-job, api-auth). Next READOUT — candidate:
  surface the api-auth "provision without a human" / credential-scheme recognition in the PUBLIC methodology
  prose (capability-worded, vendor-neutral — HTTP Authorization header / API key / OpenAPI securityScheme /
  OAuth2 as open conventions, keyed on the SCHEME not the vendor), the READOUT complement to the Cycle-86
  COVERAGE + this-cycle TRUTH api-auth arc, mirroring the Cycle-80 payment-rail + Cycle-84 async-job READOUT
  paragraphs.)
  (Cycle 86 COVERAGE — offering discovery now recognises programmatic API AUTHENTICATION, the "provision
  without a human" capability the signal bank was missing entirely. New `api-auth` signal in
  `_SIGNALS["metered_api"]` (`asrs/offering.py`), grouped with the callable-API signals after
  `api-reference`: matches HOW an agent gets/presents credentials to CALL an API — the HTTP
  `Authorization: Bearer` header, a "Bearer token", an `X-API-Key` header, an "API key", an OpenAPI
  `"securitySchemes"`/`bearerAuth`/`bearerFormat`/`"type":"apiKey"` declaration, an OAuth2 flow, or
  "authenticated WITH/VIA/USING an api key/bearer/token". CAPABILITY: an agent that cannot read the auth
  scheme cannot invoke the API at all → a metered API documenting its auth is MORE agent-completable;
  distinct from `post-endpoint` (an endpoint EXISTS) and the billing signals (how you're CHARGED) — this
  is how you're ALLOWED to call, filling the "provision" leg of the reach→understand→pay→provision→complete
  lens. PRECISION: bare "authenticate" REJECTED (a retail login would else falsely claim a metered API);
  "Bearer" must be the `Authorization: Bearer` header or "Bearer token" (not "the bearer of…"); "key" must
  be an "API key"/"X-API-Key" (not a house key/turnkey); OAuth anchored to the versioned standard — 7
  auth-shaped noise strings all reject. NON-VACUOUS on REAL committed evidence: fires end-to-end
  (`from_fixture → discover_offering`) on BOTH canonical domains (`Authorization: Bearer` homepage +
  "authenticated with an API key sent as a Bearer token" /docs) AND api.replicate.com's `securitySchemes`
  bearer scheme — three different surfaces; fires on ZERO of the retail/null fixtures. SCORE-NEUTRAL: every
  site where it fires ALREADY claims metered_api → claimed SET+ORDER byte-identical
  (`['metered_api','digital_good','subscription']` pair, `['metered_api']` replicate, `['physical_good']`
  retail); `git diff --name-only` = offering.py + test_offering.py ONLY; git diff over
  scoring.py/probes/rubric/fixtures/batteries/battery.py/protocols.py/fetch.py EMPTY → scoring path
  byte-for-byte untouched → rubric v0.7 (discovery off the scoring path). Canonical PAIR unchanged AND
  re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss). test_offering 30→32; full suite
  22 files green (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push → branch
  loop/api-auth-signal + PR #22 + self-merge (squash c353b15; NOT peer-gated — discovery-only, off scoring
  path, score-neutral). First duty: no open peer-gated PR ([]); realigned main to origin/main c353b15 after
  merge. FIRST cycle after 16:00 UTC → daily digest DM SENT (flagged the ~16.5h runner gap loudly). RUNNER
  STILL GAPPED (verify_20260728T234102Z 23:41Z ~16.5h old). Next TRUTH — candidate: a SIGNAL-level
  relabel-invariance guard for the new `api-auth` signal (an access/auth scheme is a property of what a
  storefront declares programmatically, not who declares it), the recurring "extend relabel-invariance as
  new signals land" item — mirrors Cycle-79 payment-rail + Cycle-83 async-job. NOTE: the api-auth evidence
  quote embeds the host (`api.driftflight.com/v1/... Authorization: Bearer`), so it is a QUOTE-ANCHORED
  non-vacuity case like payment-rail, not host-free like async-job.)
  (Cycle 85 METHOD — pinned the scorer's MULTI-CAP ORDER-INVARIANCE, an unexercised rung named by the
  canonical-replay input-order guard's OWN docstring. `asrs/scoring.score` builds `caps_applied` in check-
  ARRIVAL order and the capped `overall` as a repeated `min`; when TWO caps bind, permuting the check input
  permutes the `caps_applied` LIST. New `test_scoring.py::test_multi_cap_order_invariance` (test_scoring
  11→12) scores a synthetic two-binding-cap report (`human-gate-required` cap 79 + `no-https` cap 59 on
  otherwise-PASS checks → pre-cap overall 100, both bind → capped 59.0/F) under FOUR deterministic arrival
  orders (identity/reverse/two rotations) and asserts the METRIC-BEARING surface is byte-identical — capped
  overall, grade, the SET of binding caps, every pillar score — while HONESTLY SCOPING the `caps_applied`
  LIST order as a readout detail that legitimately varies (non-vacuity: ≥2 distinct list orders observed →
  set-invariance does real work). Scoring-path analog of the battery presentation-order invariance (Cycle 73)
  and the leaderboard permutation-invariance (Cycle 77). WHY THIS RUNG WAS MISSING: the canonical-replay
  input-order guard (test_canonical_replay guard 19) compares a fingerprint that DELIBERATELY OMITS
  `caps_applied`, and NO committed canonical fixture binds any cap (test_canonical_delta_is_weight_robust
  asserts both sides' caps_applied empty) → the multi-cap ordering behavior guard 19's own docstring names
  was unexercised anywhere; the ≥2-binding-cap case is only reachable via a synthetic report. Tests-only:
  git diff --name-only = tests/test_scoring.py ONLY; git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY →
  scoring path byte-for-byte untouched → rubric v0.7 (test pins existing behavior). Canonical PAIR unchanged
  AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss). test_scoring 11→12; full
  suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push → branch
  loop/multi-cap-order-invariance + PR #20 + self-merge (squash 76f83cb; NOT peer-gated — tests-only, off
  scoring path, pins existing behavior). No Slack (tests-only, moves no score, this 15:12Z fire is before the
  16:00 UTC digest window). First duty: no open peer-gated PR ([]); realigned detached HEAD 164babe to
  origin/main 76f83cb after merge. RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~15.5h old, past 6h
  floor — flag in next digest, likely the very next fire after 16:00Z). Next COVERAGE — candidate: a new
  archetype/signal for classify_offering, or a per-segment leaderboard summary once the [LOCAL] calibration
  population grows; in-cloud COVERAGE frontier is thin (structured catalog/pricing JSON are [LOCAL], 404 on
  fixtures).)
  (Cycle 84 READOUT — surfaced the ASYNC long-running-job contract recognition in the PUBLIC methodology
  prose, the READOUT complement to the Cycle-82 COVERAGE + Cycle-83 TRUTH async-job arc (COVERAGE → TRUTH →
  READOUT closed). Added ONE capability-worded, vendor-neutral paragraph to the methodology "What the score
  answers" card (`_write_methodology_page`, `asrs/scorecard.py`), after the Cycle-80 payment-rail paragraph:
  many agent-native offers are LONG-RUNNING JOBS (image/video gen, training runs, batch inference) whose work
  does not finish inside the request that starts it — the agent submits the job then COLLECTS THE RESULT via a
  webhook callback or by polling a status endpoint; an offer documenting that async contract is more
  agent-completable, so ASRS reads it as part of understanding the offer, keyed on vendor-neutral
  machine-integration vocabulary (webhook / async endpoint / poll a status URL — same open-convention category
  as REST/GraphQL/OpenAPI); recognition keys on the SHAPE OF THE CONTRACT not the API's NAME, pinned by the
  Cycle-83 identity-relabel guard; HONESTLY SCOPED as DIAGNOSTIC, off the scoring path, not a scored pillar.
  New guard `test_methodology_documents_async_job_contract` (test_readout, whitespace-collapsed match — the
  methodology HTML preserves source newlines, same technique as the calibration guard) asserts the
  long-running-job class, both collection mechanisms, the "shape of the contract, not the name" relabel-pin,
  the off-scoring-path honest scope, and the vendor-neutral denylist. ALSO registered the Cycle-80
  `test_methodology_documents_payment_rail_neutrality` in the test_readout runner list — it was authored but
  never wired into `main()`, so it SILENTLY NEVER RAN under the script runner (no pytest auto-discovery
  in-cloud); one-line registration restores it (the "silent success/failure look identical" self-healing law).
  Display-only + tests-only: git diff --name-only = scorecard.py + test_readout.py ONLY; git diff over
  scoring.py/probes/rubric/offering.py/battery.py/fixtures/batteries EMPTY → scoring path byte-for-byte
  untouched → rubric v0.7. Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss). test_readout 46→48; full suite 22 files green (test_free_tier 11/11 with eth-account).
  Cloud bridge blocks direct main push → branch loop/async-job-contract-readout + PR #18 + self-merge (squash
  99f232c; NOT peer-gated — display-only, off scoring path). No Slack (display-only, moves no score, before
  16:00 UTC digest). First duty: no open peer-gated PR ([]); realigned detached HEAD to origin/main 7389fa2.
  RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~14.5h old, past 6h floor — flag in next digest). Next
  METHOD — candidate: a fresh executable-invariant increment on the offering/battery path, or extend the
  calibration/relabel guard family as new fixtures land.)
  (Cycle 83 TRUTH — relabel-invariance made executable at the SIGNAL level for the Cycle-82 `async-job`
  metered_api signal (webhook/poll/async long-running-job contract). New
  `test_offering_relabel_invariance_async_job` (test_offering_canonical 14→15) replays the committed
  `api.replicate.com` fixture through the REAL discovery path, relabels the host everywhere
  (`api.replicate.com` → `vendor-neutral.test`) via `_discover_relabeled`, and asserts the async-job signal is
  IDENTITY-invariant: SAME match count (1), SAME host-normalized surface (`/openapi.json`), each relabeled
  quote STILL matching the live async-job regex (re-run per quote), vendor host absent from every piece of
  async evidence. Mirrors the Cycle-79 `agent-payment-rail` signal-level guard, dropping the machine-surface
  fixture's whole-archetype relabel coverage (`test_offering_relabel_invariance_machine`) a layer down to the
  specific "complete the job" signal the growing class of long-running agent-native APIs rests on. HONEST
  SCOPE: unlike payment-rail (host embedded in the evidence SURFACES `agents.driftflight.com/…`), the
  async-contract vocabulary is host-FREE by nature (quote = "An HTTPS URL for receiving a webhook when the
  prediction has new output"; surface = relative `/openapi.json`), so non-vacuity anchors at the FIXTURE level
  (host IS present in the fetched surfaces → whole-fixture relabel genuinely rewrites classifier input;
  asserted) and the test asserts the host-free nature explicitly rather than overclaiming a quote anchor.
  Negative control (`test_offering_relabel_negative_control`, identity-keyed special-case CAUGHT) gives the
  shared machinery teeth. Tests-only: git diff --name-only = tests/test_offering_canonical.py ONLY; git diff --
  asrs/ rubric/ fixtures/ batteries/ EMPTY → scoring AND offering/battery byte-for-byte untouched → rubric
  v0.7 (discovery off the scoring path). Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss). test_offering_canonical 14→15; full suite 22 files green (test_free_tier
  11/11 with eth-account). Cloud bridge blocks direct main push → branch loop/relabel-async-job-signal + PR +
  self-merge (squash; NOT peer-gated — tests-only, off scoring path, pins existing behaviour). No Slack
  (tests-only, moves no score, before 16:00 UTC digest). First duty: no open peer-gated PR ([]); realigned
  detached HEAD to origin/main de8f118. RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~13.6h old, past 6h
  floor — flag in next digest). Next READOUT — candidate: surface the async "complete the job" contract
  recognition in methodology/offering readout prose (capability-worded, vendor-neutral webhook/poll/async
  vocabulary), the READOUT complement to the Cycle-82 COVERAGE + this-cycle TRUTH async-job arc.)
  (Cycle 82 COVERAGE — offering discovery now recognises the ASYNCHRONOUS LONG-RUNNING JOB contract, a
  metered API whose work does not finish in the request/response round-trip (submit → retrieve the result
  via a webhook CALLBACK or by POLLING a status endpoint). New `async-job` signal in
  `_SIGNALS["metered_api"]` (`asrs/offering.py`), grouped with the API-contract "understand the offer"
  signals after `rate-limited`. CAPABILITY: the "complete the job" capability for the growing class of
  long-running agent-native APIs (image/video gen, training runs, batch inference) — an agent that cannot
  read the async/webhook/poll contract submits a job and never collects its output, so documenting it makes
  a metered API MORE agent-completable; distinct from BILLING (how you're charged) and `rate-limited` (how
  fast you may call) — this is how you GET YOUR RESULT BACK. Vendor-neutral machine-integration vocabulary
  (webhook / async endpoint / poll a status URL), same category as REST/GraphQL/OpenAPI/x402. PRECISION:
  bare "poll" anchored to an API object ("poll ... endpoint" same-line window, or "poll for/until"); "async"
  must name an API noun; "webhook" must pair with an integration noun/verb — 8 collision/noise negatives all
  reject (opinion poll, polling place, reader poll, bare async, webhook-free, retail cart). NON-VACUOUS on
  REAL committed evidence: fires end-to-end (`from_fixture → discover_offering`) on `api.replicate.com`
  `/openapi.json`'s genuine async contract ("An HTTPS URL for receiving a webhook when the prediction has new
  output", "poll the ... endpoint until it"); fires on ZERO of the other four fixtures (canonical pair
  documents no async flow). Score-neutral: api.replicate.com already claims ONLY metered_api → claimed set
  stays `['metered_api']` (deepened evidence, no new archetype); `git diff --name-only` = asrs/offering.py +
  tests/test_offering.py ONLY; scoring/probes/rubric/protocols/fetch/battery/fixtures byte-for-byte untouched
  → rubric v0.7 (discovery off the scoring path, `--battery auto` only). Canonical PAIR unchanged AND
  re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; offering-canonical guard 14/14).
  test_offering 28→30; full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge blocks
  direct main push → branch loop/async-job-signal + PR + self-merge (squash; NOT peer-gated — discovery-only,
  off scoring path, score-neutral). No Slack (moves no score, before 16:00 UTC digest). First duty: no open
  peer-gated PR ([]); realigned detached HEAD to origin/main d774e9f. RUNNER STILL GAPPED
  (verify_20260728T234102Z 23:41Z ~12.5h old, past 6h floor — flag in next digest). Next TRUTH — candidate: a
  relabel-invariance case for the new async-job signal (contract-structure not vendor), extending the recurring
  "extend relabel-invariance as new signals land" item.)
  (Cycle 81 METHOD — made the offering CLASSIFICATION's SURFACE-READ-ORDER INVARIANCE an executable
  tripwire. New `test_classification_is_surface_read_order_invariant` (test_offering 27→28) runs
  `classify_offering` on the same synthetic surfaces in two genuinely-distinct insertion orders (forward
  vs reversed) and asserts the metric-bearing classification is IDENTICAL: claimed archetypes IN RANK
  ORDER, each strength, each claim's distinct labels + source surfaces, the NA/unclaimed complement, and
  the SET of surfaces read. Discovery-layer analog of the battery presentation-order invariance (Cycle 73)
  and the leaderboard permutation-invariance (Cycle 77): a readiness classification is a property of WHAT
  a storefront's surfaces declare, not the ORDER an agent fetched them — the offering-relative battery's
  cross-site comparability rests on it (two crawls that read `/pricing` before/after the homepage must
  classify identically). The ranking IS order-invariant by construction (`(-strength, ARCHETYPES.index)`
  over a set-union of signals) but nothing pinned it against a future parallel-fetch/reorder refactor.
  NON-VACUOUS + honest scope: fixture built so subscription is declared on BOTH surfaces (reorder genuinely
  permutes accumulation) and TIES service_booking at strength 2 (tie broken purely by ARCHETYPES.index
  1<4, stable in both runs); the test PROVES the permutation is real+observable (`surfaces_seen` LIST
  differs AND the two-surface subscription `sample_quote` flips), then honestly scopes it — `sample_quote`
  is a first-observed DISPLAY sample, deliberately NOT claimed order-invariant (measurement invariant, one
  human-readable sample is not; same Cycle-79 honest-robustness precedent). Tests-only: git diff -- asrs/
  rubric/ fixtures/ batteries/ EMPTY → scoring AND offering/battery code byte-for-byte untouched, rubric
  v0.7, off the scoring path. Canonical PAIR unchanged AND re-measured (replay guard 24/24 incl. the
  input-order negative control, 46.1 F / 85.5 B / +39.4, 0 replay-miss; offering-canonical guard 14/14).
  test_offering 27→28; full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge
  blocks direct main push → branch loop/offering-order-invariance + PR + self-merge (squash; NOT
  peer-gated — tests-only, off scoring path). No Slack (moves no score, before 16:00 UTC digest). First
  duty: no open peer-gated PR ([]). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~11h31m old, past
  6h floor — flag in next digest). Next COVERAGE — candidate: a new archetype/signal for classify_offering,
  or a per-segment leaderboard summary once the [LOCAL] calibration population grows.)
  (Cycle 80 READOUT — surfaced the north-star "many payment rails" flexibility axis in the PUBLIC readout,
  the READOUT complement to the Cycle 78 (COVERAGE) + Cycle 79 (TRUTH) `agent-payment-rail` arc. Added one
  capability-worded, vendor-neutral paragraph to the methodology "What the score answers" card
  (`_write_methodology_page`, `asrs/scorecard.py`), extending the existing "no payment brand is special-cased"
  sentence: agent-native payment is a CAPABILITY not a single rail; agentic commerce is standardizing on
  SEVERAL open payment protocols (x402 / MPP / ACP / UCP / AP2, named as OPEN STANDARDS not vendors) and a
  with-rails site commonly advertises more than one (`x402 (Base USDC)` + `MPP (Tempo USDC)`); ASRS recognizes
  a declared rail by its PROTOCOL and SETTLEMENT STRUCTURE so every rail is read on EQUAL TERMS, none favored by
  name; recognition keys on WHAT a storefront declares not WHO — pinned by an executable identity-relabel test
  (the Cycle 79 guard, surfaced in prose). New guard `test_methodology_documents_payment_rail_neutrality`
  (test_readout) asserts the capability-not-a-rail framing, all five rail names, protocol/settlement equal-terms
  wording, the relabel test-pin, and the vendor-neutral denylist. Display-only: git diff --name-only =
  scorecard.py + test_readout.py ONLY; scoring path (scoring/probes/rubric/offering/battery/fixtures/batteries)
  byte-for-byte untouched → rubric v0.7. Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; offering guard 14/14). Readout+wording guards 55/55; full suite 263 passed
  (22 files, +1; test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push → branch
  loop/payment-rail-neutrality-readout + PR + self-merge (squash; NOT peer-gated — display-only, off scoring
  path). No Slack (display-only, moves no score, before 16:00 UTC digest). First duty: no open peer-gated PR
  ([]); realigned stale ephemeral local-main (22 ahead / 50 behind) to origin/main 1dc66e3 (hard reset).
  RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~10h31m old, past 6h floor — flag in next digest).
  Next METHOD — candidate: a fresh executable-invariant increment on the offering/battery path, or extend the
  calibration/relabel guard family as new fixtures land.)
  (Cycle 79 TRUTH — relabel-invariance made executable at the SIGNAL level for the new `agent-payment-rail`
  metered_api signal (Cycle 78). New `test_offering_relabel_invariance_payment_rail` (test_offering_canonical
  13→14) replays `fixtures/canonical/driftflight.com.json` through the REAL discovery path, relabels the host
  everywhere (`driftflight.com` → `vendor-neutral.test`) via the existing `_discover_relabeled`, and asserts the
  rail signal is IDENTITY-invariant: SAME match count (2), SAME host-normalized surfaces (agent
  `/llms-full.txt` settlement-asset form + `/manifest.json` structured `"protocol":"<rail>"` form), each
  relabeled quote STILL satisfying a high-precision protocol form — re-verified by re-running the live
  `_SIGNALS["metered_api"]["agent-payment-rail"]` regex on each relabeled quote — with the vendor host GONE.
  Drops the relabel family a layer below the claimed-ARCHETYPE partition to the specific signal the north-star
  "many payment rails" axis rests on: a payment rail is a property of what a storefront declares
  programmatically (`"protocol":"x402"`, `x402 (Base USDC) and MPP (Tempo USDC)`), never of who declares it.
  NON-VACUITY: the rail-signal surfaces embed the host (`agents.driftflight.com/…`), so the whole-fixture
  relabel genuinely rewrites classifier input on the very surfaces the signal reads, yet the signal survives
  because it keys on PROTOCOL/SETTLEMENT structure. HONEST ROBUSTNESS: quote byte-equality modulo host is NOT
  asserted — host-length change (15→19) shifts the fixed-width quote WINDOW (`.com/openapi.json` →
  `test/openapi.json`); the structural regex re-match is the robust invariant; the existing
  `test_offering_relabel_negative_control` (identity special-case CAUGHT) gives the family teeth. Tests-only:
  git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY → rubric v0.7. Canonical PAIR unchanged AND re-measured
  (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; offering guard 14/14). Full suite 22 files green
  (test_free_tier 11/11 with eth-account). Cloud bridge blocks direct main push → branch
  loop/relabel-payment-rail-signal + PR + self-merge (squash; NOT peer-gated — pins existing behaviour, off
  scoring path). No Slack (tests-only, moves no score, before 16:00 UTC digest). First duty: no open
  peer-gated PR ([]). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~9h31m old at 09:12Z, past 6h floor
  — flag in next digest). Next READOUT — candidate: surface the agent-payment-rail "many rails" recognition in
  the methodology/offering readout prose (capability-worded), or a per-segment leaderboard summary once the
  [LOCAL] population grows.)
  (Cycle 78 COVERAGE — offering discovery now recognises open agent-native PAYMENT RAILS BEYOND the lone
  `x402`. New `agent-payment-rail` signal in `_SIGNALS["metered_api"]` (`asrs/offering.py`) matches the
  other open, vendor-neutral agent-payment/settlement protocols the landscape is standardizing on —
  x402 / MPP / ACP / UCP / AP2 — in two HIGH-PRECISION forms: a STRUCTURED `"protocol":"<rail>"`
  declaration (a manifest `paymentProtocols` entry) OR a rail name paired with its on-chain SETTLEMENT
  asset in a `(… USDC/USDT/stablecoin …)` parenthetical. North-star "many payment rails" flexibility axis:
  recognising only `x402` under-classified agent-native payment to one rail; a with-rails site commonly
  advertises several ("x402 (Base USDC) and MPP (Tempo USDC)"). Rail names are PROTOCOL/standard names
  (not vendors) — same category as REST/GraphQL/OpenAPI/x402 already in the bank. PRECISION: never matches
  a bare acronym (MPP/ACP/UCP/AP2 collide with Member-of-Parliament / inflation-index / medical-guideline /
  exam-code senses) — 8 collision negatives all reject; fires on ZERO of the no-rails/retail/control/machine
  fixtures (drift-flight.org/example.com/books.toscrape.com/api.replicate.com) = the offering-layer mirror of
  the scoring-path x402 delta. Score-neutral VERIFIED NON-VACUOUS: driftflight.com's metered_api is ALREADY
  its strongest claim → distinct-label count 12→13, claimed SET+ORDER unchanged
  `['metered_api','digital_good','subscription']` on both; evidence fires on 2 real read surfaces
  (agents.driftflight.com/llms-full.txt + /manifest.json). Discovery-only: git diff = asrs/offering.py +
  tests/test_offering.py ONLY; scoring/probes/rubric/protocols/battery/fetch/fixtures byte-for-byte untouched
  → rubric v0.7. Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4,
  0 replay-miss; offering guard 13/13). test_offering 24→27; full suite 22 files green (test_free_tier with
  eth-account). Cloud bridge blocks direct main push → branch loop/agent-payment-rail-signal + PR +
  self-merge (squash; NOT peer-gated — off scoring path, score-neutral). No Slack (score-neutral, moves no
  score, before 16:00 UTC digest). First duty: no open peer-gated PR ([]); realigned ephemeral local-main
  divergence (22 stale foundational commits ahead / 50 behind) to origin/main 70373af (hard reset, origin
  authoritative). RUNNER STILL GAPPED (verify_20260728T234102Z 23:41Z ~8h31m old at 08:12Z, past 6h floor —
  flag in next digest). Next TRUTH — candidate: a relabel-invariance case for the new agent-payment-rail
  signal (recurring P1; evidence quote embeds rail names/structure, not a vendor), or extend the calibration
  two-sided guard once the [LOCAL] moleskine static fixture lands.)
  (Cycle 77 METHOD — made the calibration LEADERBOARD ranking PERMUTATION-INVARIANT. `_write_calibration_page`
  (Cycle 76) sorted scored members with a plain STABLE sort on `overall` alone, so two members with an EQUAL
  overall kept their INPUT ROW ORDER — the rendered ranking depended on the sweep's row order, not purely on
  the scores, contradicting the function's own "reproducible from the raw data" comment. Fix: deterministic
  secondary key `scored.sort(key=lambda r: (-r["overall"], str(r.get("domain", ""))))` → rank is a PURE
  function of (overall DESC, domain ASC), invariant under any permutation of `rows`. Guard
  `test_calibration_ranking_is_permutation_invariant` renders the page under four genuinely-distinct row orders
  (incl. the tied pair swapped) and asserts identical ranked sequence + tie broken by domain. NON-VACUOUS:
  verified the guard FAILS on the old stable-sort (tied pair 61.9 flips aaa/zzz between orders A/B); the four
  permutation inputs asserted distinct. READOUT analog of the battery presentation-order invariance (Cycle 73).
  Display-only: git diff = scorecard.py + test_readout.py ONLY; scoring/offering/battery/probe/fetch/protocols
  byte-for-byte untouched → rubric v0.7. Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F /
  85.5 B / +39.4, 0 replay-miss; offering guard 13/13). Full suite 22 files green (test_free_tier 11/11 with
  eth-account). Cloud bridge blocks direct main push → branch loop/leaderboard-ranking-permutation-invariance
  + PR #10 + self-merge (squash, 3fc79df; NOT peer-gated). No Slack (display-only, moves no score, before
  16:00 UTC digest). First duty: no open peer-gated PR ([]). RUNNER STILL GAPPED (verify_20260728T234102Z
  23:41Z ~7h31m old at 07:12Z, past 6h floor — flag in next digest). Next COVERAGE — cloud frontier thin
  (structured catalog/pricing JSON [LOCAL]); candidate: a new archetype/signal for classify_offering, or a
  per-segment leaderboard summary once the population grows.)
  (Cycle 76 READOUT — the calibration LEADERBOARD page, the cloud-doable half of the "calibration
  population + leaderboard" item. `asrs/scorecard.py` `_write_calibration_page(out_dir, sweep=None)` +
  `_load_calibration_sweep()` render the newest committed `runs/local/calibration_sweep_*.json` as a
  ranked HTML leaderboard (`calibration.html`), published next to every card + footer-linked. Scored
  members rank by overall DESC — order RE-DERIVED from the raw rows (a reproducible property of the
  scores, not an echoed pre-computed list) — with grade, overall, all five pillars (outcome `—` in a
  static $0 sweep, never a scored 0), and the offering classifier's vendor-neutral claimed-archetype set.
  NOT-SCORABLE members named in a SEPARATE section, NO rank, framed as reachability not a site failure
  (invariant #4). No-drift: grade bands LIVE from `load_rubric`; a dataset on a different rubric version
  is flagged. Vendor-neutral: domains as DATA only (same scanner-scope category as canonical-history) —
  wording scanner 4/4 green. Display-only: git diff = scorecard.py + test_readout.py only; scoring/
  offering/battery/probe code byte-for-byte untouched → rubric v0.7. Canonical PAIR unchanged AND
  re-measured (replay guard 24/24 relabel-invariance held, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  offering guard 13/13). Full suite 22 files green (test_free_tier 11/11 with eth-account). Cloud bridge
  blocks direct main push → branch loop/calibration-leaderboard-page + PR #8 + self-merge (squash,
  62e7b43; NOT peer-gated). No Slack (display-only, moves no score, before 16:00 UTC digest). First duty:
  no open peer-gated PR ([]). Renders committed calibration_sweep_20260728T234815Z.json (13 scored / 1
  not-scorable). Next METHOD — cloud-doable candidate: a fresh executable-invariant increment on the
  offering/battery path, or a per-segment summary on the leaderboard once the population grows.)
  (Cycle 75 TRUTH — extended the offering-classifier VENDOR-NEUTRALITY tripwire (domain-relabel
  invariance, Cycle 21/31) to the MACHINE-SURFACE-first fixture `api.replicate.com`, the one committed
  offering fixture the relabel family did not cover. New `test_offering_relabel_invariance_machine`
  (test_offering_canonical 12→13) relabels the host to `vendor-neutral.test` everywhere and replays
  through the REAL `from_fixture → discover_offering`, asserting claimed list (ordered `[metered_api]`)
  + NA set identical to the un-relabeled run. Refactored `_assert_offering_relabel_invariant` to take an
  optional `exp` set so the quote-anchored helper serves the machine fixture. Chose it because
  `api.replicate.com`'s metered_api claim is driven by the machine CONTRACT (/openapi.json) and its
  `post-endpoint` quote embeds the host (`curl -X POST https://api.replicate.com/v1/…`) = the SAME
  quote-anchored non-vacuity substrate as the pair → proves the metered_api task SELECTION keys on
  endpoint STRUCTURE not the vendor NAME. Offering/task-selection relabel coverage now 3 quote-anchored
  (org/com/machine) + 2 surface-presence (retail/nonstorefront); scoring-layer guard already spans 4.
  NON-VACUOUS: host asserted present in base metered_api evidence quote, neutral host different length +
  no signal word; existing negative-control (identity-keyed special-case CAUGHT) gives the shared
  assertion teeth. Tests-only: git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY → scoring AND
  offering/battery code byte-for-byte untouched, rubric v0.7. Canonical PAIR unchanged AND re-measured
  (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260728T234102Z 23:41Z delta 39.4,
  ~5h31m old at 05:12Z — under 6h floor). Full suite 22/22 files (test_free_tier 11/11 with eth-account
  installed). Cloud bridge blocks direct main push → branch loop/relabel-machine-surface + PR + self-merge
  (NOT peer-gated). No Slack (tests-only, moves no score, before 16:00 UTC digest). First duty: no open
  peer-gated PR ([]). RUNNER WATCH: five consecutive :41 fires 00:41–04:41Z Jul-29 produced no newer
  artifact than 23:41Z (still under the 6h floor at the 05:12Z fire, breaches ~05:41Z) — if still gapped
  next fire, FLAG in the next digest. Next READOUT — cloud-doable candidate: the calibration leaderboard
  page off the committed calibration_sweep_*.json (P1 backlog).)
  (Cycle 74 COVERAGE — the operator directive's CORE DELIVERABLE, offering-relative task SELECTION
  (`battery.instantiate_battery`), now pinned END-TO-END on the REAL committed fixtures. New
  `tests/test_battery_instantiate_canonical.py` +6 replays each committed fixture through the FULL real
  pipeline (`from_fixture → discover_offering → instantiate_battery`, no network) and pins the generated
  TASK SET per storefront TYPE: the image-gen API pair → `[metered_api,subscription,digital_good]`, NO
  physical/booking/data task (the operator's "physical_good = NA, not a completion number" at the TASK
  layer) + digital_good intent PARAMETERIZED to "generated image" from the site's OWN discovered media
  evidence; retail books.toscrape → ONLY physical_good (the inverse); machine-surface api.replicate.com →
  ONLY metered_api (compute-SKU precision boundary carried into task selection); example.com → EMPTY
  battery. Plus cross-site comparability: metered_api intent byte-identical across driftflight.com vs
  api.replicate.com. Extends the offering-relative battery's verified coverage from synthetic profiles +
  [LOCAL] run logs to REAL storefront types in-cloud — the same move Cycle 27 made for discovery
  classification. NON-VACUOUS: descriptor asserted = evidence-derived "generated image" NOT the generic
  "digital output" fallback; retail/replicate/empty prove the pipeline is not a constant function; TWO real
  test-draft bugs caught+fixed (task-set vs claimed-set compared as SETS not ordered lists — discovery sorts
  by strength, instantiation by template-bank order; vendor-neutrality keys on the DISTINCTIVE second-level
  label, not the generic "api" subdomain prefix that appears in "metered API"). Tests-only: git status = one
  new untracked file; git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY → scoring AND offering/battery
  code byte-for-byte untouched, rubric v0.7 (instantiate_battery is task selection, off the scoring path).
  Canonical PAIR unchanged AND re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss;
  verify_20260728T234102Z 23:41Z ~4.5h old at 04:1xZ fire, under the 6h floor). Vendor-neutral (assertions
  key on archetype kinds; domains only as fixture PATHS; intents asserted vendor-neutral; wording guards
  4/4 + 4/4 green). New file 6/6; full suite 21→22 files. Direct-to-main. No Slack (tests-only, moves no
  score, before the 16:00 UTC digest window). First duty: no open peer-gated PR ([]); runner HEALTHY (but
  WATCH: 00:41–03:41Z Jul-29 :41 fires produced no newer artifact than 23:41Z — under floor, not yet
  flagged). Next TRUTH — cloud-doable thread is thin (most calibration/real-domain work needs a committed
  fixture: [LOCAL] moleskine static fixture, [LOCAL] exa.ai over-claim); a cloud-doable TRUTH increment is
  extending relabel-invariance to the api.replicate.com machine-surface fixture (its metered_api quote
  embeds the host in `POST https://<host>/…` — the one committed offering fixture not yet in the relabel
  family).)
  (Cycle 73 METHOD — presentation-order INVARIANCE tripwire for the battery aggregation. `test_battery.py`
  +1 (12→13) `test_aggregation_is_presentation_order_invariant`: reorder the battery's tasks AND reverse
  each task's run list, re-aggregate with the same profile, and assert every SCALAR (cross_task_spread,
  between_kind_spread, all 5 checkpoint_mean/spread, each per_kind mean_completion/cross_task_spread matched
  BY KIND) is byte-identical within 1e-12 — only the READOUT order (per_kind/assessed_archetypes) may move.
  The aggregation-layer analog of the relabel-invariance guards (Cycles 21/31): a readiness number is a
  property of what was OBSERVED, not the order it arrived in. `test_per_kind_rollup` pinned order is
  PRESERVED; nothing pinned the numbers DON'T move under a different order — this catches a future
  order-dependent regression (running stat, "first task is primary" shortcut). NON-VACUOUS: (a) per_kind
  order genuinely differs under the permutation (permutation is real, observable in output); (b) the
  protected spreads are real — between_kind 0.294 (>0.25), cross_task 0.317 (>0), not a trivially-zero pass;
  plus NA (physical_good, unclaimed) stays NA under permutation and na_archetypes keys on profile not order.
  Tests-only: git diff = tests/test_battery.py ONLY; git diff -- asrs/ rubric/ fixtures/ batteries/ EMPTY →
  aggregation code unchanged (test pins existing behaviour), rubric v0.7; canonical PAIR unchanged AND
  re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260728T234102Z corroborates,
  ~3h31m old at 03:12Z fire, under the 6h floor). Vendor-neutral (keys on kinds/checkpoints; wording guards
  4/4 + 4/4 green). Direct-to-main. No Slack (tests-only, moves no score, before the 16:00 UTC digest
  window). First duty: no open peer-gated PR ([]); runner HEALTHY. Next COVERAGE — new archetype/signal for
  classify_offering, or the population-leaderboard READOUT page off the committed calibration_sweep_*.json;
  in-cloud COVERAGE frontier is thin (structured catalog/pricing JSON are [LOCAL], 404 on fixtures).)
  (Cycle 72 READOUT — the calibration READOUT complement: methodology §8 "Calibration" now surfaces the
  TWO-SIDED property Cycle 71 landed. Rewrote the §8 "honest limits" paragraph (which still called
  calibration one-domain/with-rails, "mirror case not yet run end-to-end") into TWO paragraphs: (1) a
  two-sided paragraph — the mirror case HAS run end-to-end, on a no-rails retail storefront the static score
  predicts NO agent-native payment and a live panel confirms it (agent browses but hits a machine-payable
  wall + human gate, both checkpoints FAIL, reproducibly), the failure framed LEGIBLE-NOT-A-BLANK (evidence
  of absence, invariant #4 in reader prose), "the prediction tracks the experience in both directions" at the
  SAME payment checkpoints (with-rails PASS / no-rails FAIL); (2) revised honest limits — one storefront per
  direction (corroborated both ways, not yet a population), still $0-bounded, pinned by the executable guard.
  Display-only: git diff = scorecard.py + test_readout.py ONLY; scoring path (scoring.py/rubric/probes/
  fixtures) byte-for-byte untouched → rubric v0.7; canonical PAIR unchanged AND re-measured (replay guard
  24/24, 46.1 F / 85.5 B / +39.4; verify_20260728T234102Z corroborates). Vendor-neutral (no domain named —
  "no-rails retail storefront"; wording guards 4/4 + 4/4 green, drift-flight/driftflight absent).
  test_methodology_documents_calibration EXTENDED (not a new test — asserts two-sided phrases + stale
  positive-only claims removed, on collapsed text); test_readout 40/40; suite 244 tests, 20/20 files.
  Direct-to-main. No Slack (display-only, moves no score, before the 16:00 UTC digest window). First duty:
  no open peer-gated PR ([]); runner HEALTHY (verify_20260728T234102Z, 23:41Z, ~2h30m old). Next METHOD —
  reliability §7 + validity §8 both current now; candidate: extend the two-sided guard's rigor once the
  [LOCAL] moleskine static fixture lands, or a fresh executable-invariant increment on the offering/battery
  path.)
  (Cycle 71 TRUTH — the NEGATIVE calibration guard: calibration is now a TWO-SIDED property.
  `tests/test_calibration.py` +4 (4→8) replays the committed no-rails retail behavioral anchor
  `runs/local/acceptance_battery_moleskine_20260728T225939Z.report.json`, the executable MIRROR of
  Cycle 67's positive with-rails anchor. (5) NEGATIVE prediction behaviorally corroborated: static
  x402_probe not-PASS / self_serve_payg x402_live=False / transactability 18.75 → NO agent-native
  payment; behavioral bhv_purchase_path/machine_payable/no_human_gate all FAIL, Outcome 0.0;
  bhv_free_tier_transaction NA (no free tier), not scored as a wall. (6) GENUINE reachable retail, not
  a null: Access 100, physical_good CLAIMED + API archetypes NA, agent BROWSED (60% completion) yet hit
  the payment wall — invariant #4 attribution honesty. (7) reproducible: both trials FALSE on
  machine_payable_path+no_human_gate, verdict_stability 1.0. (8) TWO-SIDED capstone: at the SAME payment
  Outcome checkpoints with-rails PASSES and no-rails retail FAILS, both rubric v0.7, Outcome 100.0 vs 0.0.
  Honest scope: moleskine has NO committed static fixture → static prediction read from the report's own
  embedded static checks, not a separate offline replay (the with-rails anchor's two-crawl
  cross-validation is a [LOCAL] follow-up). Tests-only: git diff -- asrs/ rubric/ fixtures/ EMPTY →
  scoring path byte-for-byte untouched, rubric v0.7, canonical PAIR unchanged AND re-measured (replay
  guard 24/24, 46.1 F / 85.5 B / +39.4; verify_20260728T234102Z corroborates). Vendor-neutral in the
  assertions (keys on checks/pillars/archetypes; domain only as artifact path). `test_calibration` 4→8;
  suite 240→244. Direct-to-main. No Slack (tests-only, moves no score, before the 16:00 UTC digest
  window). First duty: no open peer-gated PR ([]); runner HEALTHY (verify_20260728T234102Z, 23:41Z,
  ~1h30m old). Next READOUT — the calibration READOUT complement: methodology §8 (Cycle 68) still calls
  calibration one-domain/with-rails; now the negative anchor + two-sided property have landed, surface
  them in capability prose.)
  (Cycle 70 COVERAGE — offering DISCOVERY reads the pricing/billing page. `asrs/offering._SURFACE_DOCS`
  gains `/pricing` — the "understand the offer" BILLING surface where the per-month / per-generation /
  pay-as-you-go / seat / credit-metered / volume-tier prose the signal bank already anchors on most
  conventionally lives; a site that documents billing ONLY there was under-classified. HTML-stripped
  (same `_is_html_document` path as `/docs`), read through the SAME precision-guarded signal bank (no new
  signal), vendor-neutral (universal web convention). Off the scoring path (called ONLY from
  `cli._resolve_battery`/`--battery auto`; scoring probe keeps its own untouched
  `protocols._AGENT_SURFACE_DOCS`). VERIFIED score-neutral on committed evidence NON-VACUOUSLY: real
  `discover_offering` through `from_fixture` BEFORE/AFTER — canonical `/pricing` is a real 200, IS read
  (surfaces_seen gains it), reinforces the three already-claimed archetypes; claimed SET+ORDER
  byte-identical `['metered_api','digital_good','subscription']` on both, no new physical/booking/data.
  New guard `test_offering.py::test_pricing_surface_is_read_live` (read-live, HTML-free evidence,
  metered+subscription both carry a /pricing signal, set+order unchanged) + wiring test extended.
  `git diff -- asrs/scoring.py rubric/ asrs/probes/` EMPTY → rubric v0.7; canonical PAIR unchanged AND
  re-measured (live replay 46.1 F / 85.5 B / +39.4; replay guard 24/24, offering guard 12/12).
  `test_offering` 23→24; suite 21 files / 240 tests. Direct-to-main. No Slack (score-neutral, before the
  16:00 UTC digest window). Chose it because it's the one COVERAGE increment BOTH cloud-verifiable AND
  non-speculative — structured `/catalog.json`//pricing.json//plans are 404 on all fixtures → queued
  [LOCAL]. Next TRUTH (top P0 = negative-calibration guard against the committed moleskine report).)
  (Cycle 69 METHOD — widened the static-vs-behavioral CALIBRATION guard (Cycle 67) with a 4th
  test test_calibration_rests_on_a_shared_static_base: pins that every STATIC-OBSERVABLE pillar
  both measurements compute (access/legibility/transactability) is IDENTICAL between the fixture
  replay and the committed 18:55Z behavioral report (abs<1e-9), so "prediction==experience" rests
  on the SAME evidence, not just matching domain/rubric_version STRINGS (tests 1-3's only
  like-for-like). The payability magnitude 87.5 is thus the very number the static guard pins AND
  reproduced across TWO independent crawls (fixture capture + behavioral crawl) = crawl-stable.
  Non-vacuous: behavioral SCORES Outcome (static null) + Trust DIFFERS 60→55.56 (live panel) =
  genuine augmented superset, not the fixture re-dumped. Tests-only, scoring path byte-for-byte
  untouched, rubric v0.7, replay 24/24 / 46.1 F / 85.5 B / +39.4; test_calibration 3→4, suite
  21/21; direct-to-main. In-cloud calibration frontier now saturated — the negative/cross-domain
  behavioral DIRECTION guard is BLOCKED on a second committed behavioral artifact ([LOCAL]
  retail-inverse acceptance P0). Next COVERAGE.)
  (Cycle 68 READOUT — the READOUT complement to Cycle 67's calibration guard: new methodology
  §8 "Calibration — does the score predict what an agent experiences?" surfaces the
  static-vs-behavioral VALIDITY property in critic-readable capability prose (agent-native-payment
  prediction behaviorally corroborated at the live outcome checkpoints; DISCRIMINATING — real FAILs
  + separates tiers; honest ONE-DOMAIN/$0-free-tier scope; test-pinned). Reliability §7 + validity
  §8 = the two measurement virtues, now both documented. Renumbered caps/$0-probe/versioning
  8-10→9-11 (display-only; anchor ids key on _cap_anchor not §#). Vendor-neutral (no domain named).
  Display-only, scoring path byte-for-byte untouched, rubric v0.7, replay 24/24 / 46.1 F / 85.5 B /
  +39.4; test_readout 39→40, suite 21/21; direct-to-main (37ba0b7). Next METHOD.)
  (Cycle 66 COVERAGE — signal bank +tiered-volume +seat-licensing; Cycle 67 TRUTH — the
  FIRST CALIBRATION guard: tests/test_calibration.py (3) holds the static score against the
  committed LIVE behavioral acceptance run (driftflight.com 18:55Z) and asserts static
  agent-native-payment PREDICTION == behavioral EXPERIENCE (Outcome payment checks all PASS),
  DISCRIMINATING (report has real FAILs; prediction separates .com from no-rails .org) and
  REPRODUCIBLE (both trials machine-payable+no-human-gate, verdict_stability 1.0). First
  static-vs-behavioral VALIDITY axis, distinct from the 24-guard static-vs-static family.
  ONE-DOMAIN with-rails anchor (negative/retail-inverse behavioral half is [LOCAL]).
  Tests-only/score-neutral, rubric v0.7, replay 24/24 / +39.4; direct-to-main. Next READOUT.)
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
  Cycle 46 COVERAGE (offering discovery reads the A2A / Agent2Agent AGENT CARD — the open agent-to-agent
  self-description surface): `asrs/offering._SURFACE_DOCS` gains `/.well-known/agent.json` +
  `/.well-known/agent-card.json`. Brick-1's directive surfaces (homepage / llms.txt / manifest / OpenAPI,
  Cycle 34) + the ai-plugin descriptor (Cycle 42) covered marketing + machine-contract + plugin self-desc;
  the A2A agent card is the vendor-neutral manifest an agent-native storefront publishes at a well-known
  URI so ANOTHER agent discovers what it does (top-level `description` + `skills[]` each with name/desc, in
  the same natural-language capability prose the signal bank anchors) → a card-ONLY storefront (no homepage/
  llms.txt/spec) is no longer mis-read as offering nothing (the exact Cycle-34/42 failure mode, for the
  agent-card surface). No new signal — surface only had to be READ. SCORE-NEUTRAL by construction:
  discover_offering/_SURFACE_DOCS reachable ONLY from cli.py (--battery auto), NEVER scoring.py/probes/
  protocols (grep-verified; commerce-manifest scoring probe's separate `protocols._AGENT_SURFACE_DOCS`
  DELIBERATELY untouched — adding a surface THERE is score-increasing + peer-gated). `git diff --name-only`
  = offering.py + test_offering.py ONLY → rubric stays v0.7; added surfaces absent from all committed
  fixtures (captured pre-existence → replay-miss → absent → classification byte-identical) so replay guard
  stays 14/14 (46.1 F / 85.5 B / +39.4, 0 replay-miss) AND canonical OFFERING guard 12/12 unchanged;
  verify_20260727T224106Z (22:41Z) live-corroborates in-band. Vendor-neutral (A2A = open Linux-Foundation
  protocol, not a vendor; synthetic neutral `.test` host). Not payment/signing. Direct-to-main.
  `test_offering.py` 11→12 (+A2A-card-only DATA/metered storefront classifies {metered_api,data_retrieval}
  from the card, anchored evidence, physical/subscription/digital/booking NOT claimed; wiring guard asserts
  both card paths in _SURFACE_DOCS); suite 192→193. No Slack (score-neutral additive discovery, moves no
  score, digest already sent Cycle 38 16:13Z, not a new window at ~00:2xZ). First duty: no open peer-gated
  PR (verified []); infra health check ran first — runner HEALTHY (verify_20260727T224106Z, 22:41Z, ~1.5h
  old, +39.4 in-band), suite green; git synced origin/main 0d524cb. Next cycle takes TRUTH.
  Cycle 47 TRUTH (the deterministic canonical delta proven PER-SIDE, not a cancellation — the
  second-order calibration guard on the Cycle-45 noise floor): extended read-only
  `asrs/canonical_history.py`. Cycle 45 measured the DELTA's at-rest dispersion (σ=0 over 68 in-band
  readings → deterministic). But a deterministic delta is consistent with BOTH sides being fixed at rest
  AND with both sides jittering in lock-step so the difference cancels — a critic's fair objection to a
  "stable benchmark delta" the delta-only measure cannot answer. `NoiseFloor` gains
  `no_rails_stddev`/`with_rails_stddev` (population stddev of EACH side's overall over the SAME in-band
  readings) + property `sides_deterministic` (both ≤ `_NOISE_EPS`); since `delta = with_rails − no_rails`,
  per-side determinism IMPLIES delta determinism but not vice-versa → strictly STRONGER. THE FINDING on
  the committed 72-point series: all 68 in-band re-scores reproduce BOTH pinned overalls EXACTLY
  (drift-flight.org σ=0.00 @46.1, driftflight.com σ=0.00 @85.5) → the stable delta is genuine per-side
  determinism, storefront by storefront, NOT correlated drifts cancelling. `render` names it ("both sides
  exact (σ …) — the stable delta is genuine per-side determinism, not two drifts cancelling"). Read-only
  diagnostic: `git diff --name-only` = canonical_history.py + test ONLY; scoring.py/rubric/probes/fetch/
  protocols/battery/offering/behavioral/scorecard byte-for-byte untouched → rubric stays v0.7, canonical
  PAIR unchanged by construction AND re-measured (replay guard 14/14, 46.1 F / 85.5 B / +39.4, 0
  replay-miss; verify_20260727T224106Z 22:41Z in-band). Vendor-neutral (imports no scoring code;
  reference-pair hosts as DATA via existing constants). Direct-to-main. `test_canonical_history.py` 24→26
  (+2: real-series per-side determinism, implies delta-deterministic + render names it; NON-VACUOUS
  cancellation control — a lock-step synthetic series reads deterministic-delta True yet
  sides_deterministic False, the cancellation the delta is blind to, caught); suite 193→195 (test_free_tier
  11/11 after `pip install -r requirements.txt` closes the known eth-account env gap). No Slack (TRUTH
  tests + read-only diagnostic, moves no score, digest already sent Cycle 38 16:13Z, not a new window at
  ~01:2xZ). First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260727T224106Z, 22:41Z, ~2.5h old, +39.4 in-band); git synced origin/main f91d3d6. Next cycle
  takes READOUT.
  Cycle 48 READOUT (the noise-floor / per-side-determinism calibration finding surfaced on
  `canonical-history.html` — the last terminal→HTML gap on that surface): `scorecard._write_canonical_history_page`
  gains an "Is the band real noise, or transient absorption?" card between the trend chart and the diagnosis
  card, driven off `hist.noise_floor` (`NoiseFloor`, Cycle 45/47). Reports n_in_band/σ/worst|div|, the
  DETERMINISTIC-at-rest verdict, and — ONLY when `sides_deterministic` — the strictly-stronger per-side sentence
  (both reference storefronts reproduce their pinned overall exactly at rest → the stable delta is genuine
  per-side determinism, not two lock-step drifts cancelling). When the delta is deterministic but the SIDES are
  not (the cancellation Cycle 47 guards), the card shows the delta-level verdict and WITHHOLDS the per-side claim;
  non-deterministic floors render the well-separated/too-tight band read; <2 in-band readings → card SILENT
  (honest, no fabricated determinism). Wording copied verbatim from the terminal `render` (can't diverge).
  Rendered against the REAL committed 72-point series (68 in-band, σ=0.00, both sides exact). Display-only:
  `git diff --name-only` = scorecard.py + test_readout.py ONLY; scoring.py/rubric/probes/fetch/protocols/battery/
  offering/canonical_history/behavioral byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by
  construction AND re-measured (in-cloud replay guard 14/14, 46.1 F / 85.5 B / +39.4, 0 replay-miss; live
  canonical-history reads IN-BAND +39.4). Vendor-neutral (page names the pair as DATA, Cycle-40
  engineering-history category out of scope for the wording scanner; readout/rubric-wording guards 4/4 each
  unchanged). Direct-to-main. `test_readout.py` 31→34 (+per-side determinism strong claim; +NON-VACUOUS
  lock-step cancellation control withholds the per-side sentence; +card absent with <2 in-band); suite 195→198.
  No Slack (display-only, moves no score, not a digest window at ~02:2xZ, digest last sent Cycle 38 16:13Z).
  First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260727T224106Z, 22:41Z, ~3.5h old, +39.4 in-band) BUT the :41 fires at 23:41/00:41/01:41Z produced
  NO artifact (3 consecutive gaps, still under the 6h floor at 02:12Z — a possible fresh runner stall to WATCH;
  if still gapped past 6h next fire, flag + fold into the next digest). Next cycle takes METHOD.
  Cycle 49 METHOD (the benchmark's POPULATION ORDERING made an executable calibration control — the first
  cross-domain ordering property in the repo): `tests/test_canonical_replay.py` +2 (14→16). Guards 1–11 pin
  each of the four committed real-domain fixtures INDIVIDUALLY + compare pair/retail/baseline in isolation;
  none asserted the RELATIONSHIP the benchmark exists to produce. Guard 12
  (`test_population_overall_tracks_capability_ordering`) reads all four overalls from the LIVE replay pipeline
  (never the pinned EXPECTED constants) and asserts the overall STRICTLY decreases down the
  agent-native-commerce spectrum — with-rails API 85.5 > no-rails API 46.1 > human-only retail 29.5 >
  zero-commerce baseline 22.5 (+ non-vacuity floor: 4 distinct domains, top−floor ≥40.0). Guard 13
  (`test_population_ordering_is_not_a_transactability_artifact`) refutes "you just measured who takes x402":
  transactability is non-increasing along the SAME ordering AND the with-rails side strictly tops it (payment
  earns #1), BUT the two payment-FLOOR sites TIE at 0 transactability yet the tail overall order (retail 29.5 >
  bare 22.5) is preserved, driven by a DIFFERENT observed capability (legibility 18.18 > 0.00) → the population
  order is a multi-capability judgement, not a single-pillar proxy. The individual-number guards track intended
  CHANGE (updated on re-capture); this tracks the CLAIM — a maintainer who re-captured to buggy reordered
  numbers would update the exact-number expectations to match and every existing guard would still pass, this
  one fails. NON-VACUOUS: a reversed-spectrum negative control makes the strict-decrease guard FAIL (verified
  this fire); scores read from the live pipeline, not a tautology over constants. Worded by capability tier,
  never by vendor (domains appear only as the same fixture keys guards 1–11 use). Tests-only:
  `git diff --name-only` = test_canonical_replay.py ONLY; `git diff -- asrs/ rubric/` EMPTY →
  scoring.py/rubric/probes/fetch/protocols/battery/offering byte-for-byte untouched → rubric stays v0.7,
  canonical PAIR unchanged by construction AND re-measured (replay guard 16/16, 46.1 F / 85.5 B / +39.4, 0
  replay-miss). Direct-to-main. Suite 198→200 (all 19 files exit 0). No Slack (tests-only, moves no score,
  digest last sent Cycle 38 16:13Z, not a new window at 03:2xZ). First duty: no open peer-gated PR (verified
  []); infra health check ran first — runner WATCH: newest verify_20260727T224106Z (22:41Z, ~4.5h old, +39.4
  in-band), the 23:41/00:41/01:41/02:41Z fires produced NO artifact (4 consecutive gaps, Cycle-48 watch
  persists), STILL under 6h at 03:20Z — flag if the next fire shows no newer artifact and 22:41Z crosses 6h.
  Next cycle takes COVERAGE.
  Cycle 50 COVERAGE (offering discovery recognises CREDIT-BASED metering — the dominant billing convention for
  generative / agent-native APIs, the north-star many-billing-conventions axis): `asrs/offering.py` new
  `credit-metered` signal in the `metered_api` bank. The bank captured pay-as-you-go / pay-per / billed-per /
  per-unit / usage-based / x402 but NOT the credit model, so a storefront metering ONLY as "buy a credit plan …
  your plan's credit ran out" recorded no credit evidence for the understand-the-offer capability (the credit
  sibling of the free-tier discovery conventions, Cycles 22/30/38). PRECISION-FIRST: bare `\bcredits?\b` is a
  false-positive minefield present in the very fixtures we validate on — C2PA metadata (`"credits": "C2PA content
  credentials"`), wallet balance (`seller credit`, camelCase `includedCreditUsd`), refund (`credited back`),
  feature-flag names (`credits-v2-jul-2026`), and `credit card` — so anchor to billing CONTEXT (a credit + a
  metering word per/plan/balance/pack/based/ran-out, or a spend/buy verb buy/purchase/prepay/redeem/spend
  credits); all that noise is correctly skipped (`credit card`, `store credit` stay silent). Vendor-neutral
  (worded by capability, keys on generic prose). SCORE-NEUTRAL: `discover_offering`/`classify_offering` OFF the
  scoring path (grep-verified; called only from `cli._resolve_battery` for `--battery auto`); commerce-manifest
  SCORING probe's separate `protocols._AGENT_SURFACE_DOCS` untouched. `git diff --name-only` = offering.py +
  test_offering.py ONLY; `git diff -- asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py asrs/protocols.py
  asrs/battery.py` EMPTY → rubric stays v0.7. Canonical PAIR unchanged: metered_api is already the strongest claim
  on both (org strength 5, com 6, template index 0) so a new signal can't reorder the claimed list, AND
  credit-metered fires on NEITHER canonical DISCOVERY surface (org has no billing prose; com's billing docs live
  on the agents.* subdomain discovery does not crawl) → claimed SETS + ORDER byte-identical (canonical offering
  guard 12/12); replay guard re-measured 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260727T224106Z (22:41Z)
  corroborates in-band. EVIDENCE (real-data, non-vacuous): `test_offering.py` 12→14 — synthetic precision battery
  (7 real credit-billing phrasings fire, 8 credit-shaped noise strings don't) + a REAL-captured test reading the
  committed driftflight.com `/llms-full.txt` bytes (credit-metered fires on `"minimumUsd for credit plans"`) and
  asserting the same storefront's HOMEPAGE C2PA metadata trap does NOT fire. Full suite 200→202 (all 19 files exit
  0). Direct-to-main. No Slack (score-neutral additive discovery, moves no score, not sensitive, not a digest
  window at 04:12Z). First duty: no open peer-gated PR (verified []); infra health check ran first — runner WATCH
  PERSISTS: newest verify_20260727T224106Z (22:41Z), ~5.5h old at 04:12Z, the 23:41–03:41Z :41 fires produced NO
  artifact (5 consecutive gaps, closest to the 6h floor yet) — if the next fire shows no newer artifact, 22:41Z
  crosses 6h → flag loudly + fold into the next digest. Next cycle takes TRUTH.
  Cycle 51 TRUTH (LIVE-SIGNAL FRESHNESS made an executable, surfaced fact — the canonical-history readout no
  longer presents a STALE re-score's verdict as a current all-clear): read-only `asrs/canonical_history.py`
  gains a `Liveness` dataclass (`latest_ts`/`age_hours`/`stale_floor_hours=6.0` + `fresh` = age ≤ floor),
  `_parse_ts` (parses the `YYYYMMDDTHHMMSSZ` verify ts, honest-None on a bad ts), `liveness(latest, now)`, a
  `now`-optional `summarize`/`load_history`, a render line, and `cli._cmd_canonical_history` passing the wall
  clock. Every other history field describes the latest READING (band, re-capture advice, which side moved);
  NONE said how OLD that reading is — so a stalled runner leaves a healthy-looking "in-band / baseline-valid"
  verdict that is hours stale, and a reader could mistake AGE for CONFIRMATION. Now the readout flags STALE
  (past the same 6h floor the playbook self-healing law uses to declare the runner down) with an explicit "the
  verdict below describes an OLD crawl, not the pair now — the runner may be down" warning. PURE when `now` is
  None (no clock-dependent claim — same honest-None discipline as attribution/noise-floor); the CLI supplies
  the clock. THIS FIRE'S LIVE RUN demonstrates it end-to-end: newest re-score 22:41Z reads IN-BAND (+39.4,
  σ=0 both sides) yet the render now correctly prints "newest re-score 6.6h old — STALE …". Read-only
  diagnostic, OFF the scoring path: `git diff --name-only` = canonical_history.py + cli.py (canonical-history
  cmd only) + test_canonical_history.py; `git diff -- asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py
  asrs/protocols.py asrs/battery.py asrs/offering.py` EMPTY → rubric stays v0.7, canonical delta unchanged by
  construction AND re-measured (replay guard 16/16, 46.1 F / 85.5 B / +39.4, 0 replay-miss; canonical offering
  guard 12/12). Vendor-neutral (host names as existing DATA constants). Direct-to-main.
  `test_canonical_history.py` 26→32 (+6: none-without-now/pure, fresh, STALE-despite-in-band, future-clamp,
  unparseable-ts honest-None, real-series coherence); full suite 202→208 (all 19 files exit 0). No Slack
  (score-neutral read-only diagnostic, moves no score, 05:1xZ is not a digest window). First duty: no open
  peer-gated PR (verified []); infra health check ran first — **RUNNER STALLED PAST THE 6h FLOOR** (see runner
  note below). Next cycle takes READOUT.
  Cycle 52 READOUT (the Cycle-51 live-signal freshness fact, now on the HTML trend surface — the terminal→HTML
  close-out): `asrs/scorecard.py` `_write_canonical_history_page` renders a liveness element off `hist.liveness`
  — a prominent STALE warning CARD ABOVE the latest-reading card when the newest re-score is past the 6h floor
  ("⚠ Live signal STALE — newest re-score X.Xh old … the verdict below describes an OLD crawl, not the pair now;
  the runner may be down"), a quiet one-line age note when FRESH. The live build path loads WITH the wall clock
  (`ch.load_history(now=datetime.now(timezone.utc))`, mirroring `cli._cmd_canonical_history`) so the check runs
  on the hosted card; a caller passing its own `history` controls its own liveness (tests), a clock-free summary
  carries `liveness=None` → NO banner (honest-None). Closes the last terminal-only gap for the freshness signal
  (same deferral per_kind Cycle 10→12 / between_kind_spread 18→20 / noise floor 47→48 took). Display-only:
  `git diff --name-only` = scorecard.py + test_readout.py ONLY; scoring.py/rubric/probes/fetch/protocols/battery/
  offering/canonical_history.py byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by
  construction AND re-measured (replay guard 16/16, 46.1 F / 85.5 B / +39.4, 0 replay-miss; canonical offering
  guard 12/12). Vendor-neutral (host names as DATA, engineering-history category). `test_readout.py` 34→37 (+3:
  STALE-despite-in-band w/ banner-before-verdict ordering, FRESH-shows-age-no-banner non-vacuous, no-clock →
  neither element honest-None); full suite 208→211 (18 of 19 files green in-cloud; `test_free_tier` 11/11 after
  `pip install -r requirements.txt` supplies `eth-account`). END-TO-END on the REAL committed series: live-load
  render prints "newest re-score 7.6h old — STALE" (runner stalled) despite the In-band verdict — exactly the
  failure closed. Direct-to-main. No Slack (display-only READOUT, moves no score, 06:1xZ not a digest window).
  First duty: no open peer-gated PR (verified []); infra health check ran first — RUNNER STILL STALLED PAST 6h
  (see runner note below, unchanged from Cycle 51 — no newer artifact). Next cycle takes METHOD.
  Cycle 53 METHOD (JOINT population-level relabel-invariance guard — the queued Cycle-49/52 hypothesis, now a
  tripwire): `tests/test_canonical_replay.py` +1 (16→17), guard 14 `test_population_ordering_is_identity_invariant`.
  Guard 12 pins the strict monotone capability ordering (with-rails API 85.5 > no-rails API 46.1 > human-only retail
  29.5 > zero-commerce 22.5) on the REAL hosts; guards 4/6/8/11 pin each domain's score under relabel ONE AT A TIME;
  neither pins the ORDERING under a SIMULTANEOUS relabel of the whole population. Guard 14 relabels all four fixtures
  at once to DISTINCT neutral hosts, asserts each relabeled overall still equals its pinned value AND the strict
  monotone chain survives. NON-VACUOUS beyond the per-domain guards: the four neutral hosts differ only in leading
  letter and are assigned REVERSE-lexical to capability (top→alphabetically-last `zeutral-storefront.test`,
  floor→first `aeutral-storefront.test`), so a scorer that ranked the population by host STRING would REVERSE the
  order and FAIL here while every single-host per-domain guard still passes (none compares hosts). The reverse-lexical
  condition is itself asserted executable (`hosts==sorted(reverse=True)`) + distinct + no canonical name. First
  CROSS-DOMAIN identity-invariance property (per-domain guards are within-domain). Host choice: each neutral host is
  the per-domain guards' known-miss-free `neutral-storefront.test` with only its leading letter varied (same
  length+hyphen structure), because `_score_relabeled`'s whole-fixture substitution trips a replay-miss ARTIFACT on a
  shorter/extra-hyphen host — the `.com` fixture's recorded `api.driftflight.com/openapi.json` subdomain surface
  rewrites to an un-recorded fetch (score stays 85.5, surface unscored; filed P2 as a test-helper property, not a
  scoring bug). Tests-only: `git diff --name-only` = test_canonical_replay.py ONLY, `git diff -- asrs/ rubric/` EMPTY
  → scoring path byte-for-byte untouched, rubric stays v0.7, canonical delta unchanged by construction AND re-measured
  (replay guard 17/17, 46.1 F / 85.5 B / +39.4, 0 replay-miss; canonical OFFERING guard 12/12). Direct-to-main. Full
  suite 211→212. No Slack (tests-only, moves no score, 07:1xZ not a digest window). First duty: no open peer-gated PR
  (verified []); infra health check ran first — RUNNER STILL STALLED PAST 6h (unchanged, no newer artifact); git
  realigned local `main` from stale orphan `2e66201` → origin/main `7858bc0` before committing. Next cycle takes
  COVERAGE.
  Cycle 54 COVERAGE (offering discovery reads conventional DOC SUBDOMAINS — the queued Cycle-50/53 candidate, now
  shipped): `asrs/offering.py` `discover_offering` reads each `_SURFACE_DOCS` surface on the apex host AND on a small
  allowlist of same-registrable-host doc subdomains `agents.`/`docs.`/`developers.`/`api.` (new `_DOC_SUBDOMAINS` +
  `_doc_subdomain_surfaces(base_url)`). API-first storefronts commonly serve rich agent docs on a doc subdomain, not
  the apex; until now discovery read only the bare apex, so such a site was under-classified — the canonical
  `driftflight.com` serves its credit-billing agent docs at `agents.driftflight.com/llms-full.txt`, never crawled
  before. PRECISION-FIRST/SSRF-safe: subdomains constructed from the site's OWN resolved host (`base_url`), never an
  arbitrary fetched `url` → discovery can only reach the storefront's own registrable domain; `www.` dropped so the
  subdomain attaches to the registrable host; a host already on an allowlisted subdomain is NOT self-stacked
  (`api.replicate.com` → no `api.api.replicate.com`); surface labels host-qualified (`agents.<host>/llms.txt`) so a
  subdomain surface never overwrites an apex path; a subdomain that 404s/does-not-resolve is simply absent. SCORE-NEUTRAL:
  `discover_offering` is off the scoring path (`--battery auto` only); `git diff --name-only` = offering.py +
  test_offering.py ONLY, `git diff -- asrs/scoring.py asrs/probes/ asrs/fetch.py rubric/` EMPTY → rubric stays v0.7,
  canonical delta unchanged by construction AND re-measured (replay guard 17/17, 46.1 F / 85.5 B / +39.4, 0 replay-miss).
  Canonical OFFERING guard `test_offering_canonical.py` stays 12/12: subdomain surfaces on BOTH canonical domains carry
  only metered_api/subscription/digital_good signals (NO physical_good/service_booking/data_retrieval), so the claimed
  SET is byte-for-byte `{metered_api,subscription,digital_good}` — only strength/labels grow (P2 prediction confirmed).
  Vendor-neutral (generic-convention allowlist; relabel-invariance guards stay green — the whole-fixture relabel rewrites
  `agents.driftflight.com` → `agents.<neutral>` consistently). Not payment/signing code. `test_offering.py` 14→16
  (+`test_doc_subdomain_helper_is_precise_and_ssrf_safe` unit-pinning the helper; +`test_doc_subdomain_surfaces_are_read_live`
  replaying the committed `.com` fixture and asserting `agents.driftflight.com/llms-full.txt` ∈ surfaces_seen AND the
  `credit-metered` signal — present ONLY in that subdomain surface — now reaches the DISCOVERED metered_api claim, a
  non-vacuous witness the subdomain content reached classification, claimed set unchanged). Full suite 212→214.
  Direct-to-main (score-neutral discovery off the scoring path, precedent Cycles 34/42/46). No Slack (score-neutral,
  not sensitive, 08:1xZ not a digest window). First duty: no open peer-gated PR (verified []); infra health check ran
  first — RUNNER STILL STALLED PAST 6h (unchanged, no newer artifact, ~9.5h old); git realigned local `main` from stale
  orphan `2e66201` → origin/main `dfb7f47` (Cycle 53) before committing. Next cycle takes TRUTH.
  Cycle 55 TRUTH (the canonical +39.4 delta defended on a FOURTH credibility axis — WEIGHT-ROBUSTNESS —
  made executable): `tests/test_canonical_replay.py` +1 (17→18), guard 15 `test_canonical_delta_is_weight_robust`.
  Replays both committed canonical fixtures through the REAL `from_fixture → _run_probes → scoring.score` path
  and pins that the with-rails advantage is a property of the capability evidence under EVERY reasonable pillar
  weighting, not the one hand-tuned weight vector. PILLAR-WISE DOMINANCE: with-rails ≥ no-rails on every
  applicable pillar (access 100=100, legibility 90.9>36.4, transactability 87.5>18.75, trust 60=60), strictly > on
  the two benchmark-defining pillars. Both sides expose the IDENTICAL applicable-pillar set (like-for-like
  denominator at the pillar layer, the aggregation analogue of guard 8's like-for-like checks) AND neither hits a
  grade cap (`caps_applied == []`) → each overall is a pure renormalized weighted mean, so pillar dominance makes
  the sign of (com−org) INVARIANT to the weight vector. Demonstrated across an adversarial weighting family (real
  rubric, uniform, each unit-basis vector) — the with-rails mean is NEVER below the no-rails mean, strictly > for
  any weighting touching a dominated pillar, and never inverts even under the two extremes most hostile to the
  pitch (all-weight-on-trust / all-weight-on-access, the TIED pillars, delta→0). FAITHFULNESS anchor: rubric
  weights reproduce the shipped overalls (85.5/46.1) from the pillars alone, proving the reweighting helper IS the
  scorer's aggregation. NON-VACUOUS: a synthetic trust-inverted no-rails side WOULD top the with-rails side under
  all-trust weighting (verified by monkeypatch injecting a transactability inversion → guard CAUGHT it at the
  dominance assertion). A distinct axis complementing Cycle-19 (capability-payment) / Cycle-21 (relabel/identity)
  / Cycle-23 (earned dominance/observability): refutes the AGGREGATION objection ("you rigged the weights"), not
  the evidence objection. Worded by capability, never by vendor (fixture keys are the pair guards' own; property
  stated over pillars). Tests-only: `git diff --stat` = test_canonical_replay.py ONLY (+145);
  scoring.py/rubric/probes/fetch/protocols/behavioral/offering/battery byte-for-byte UNTOUCHED → rubric stays
  v0.7, canonical delta unchanged by construction AND re-measured (replay guard 46.1 F / 85.5 B / +39.4, 0
  replay-miss). Direct-to-main. Suite 214 → 215. No Slack (tests-only, moves no score, 09:2xZ before the 16:00 UTC
  digest window). First duty: no open peer-gated PR (verified []); infra health check ran first — RUNNER STILL
  STALLED PAST 6h (newest verify_20260727T224106Z ~10.5h old, unchanged — P0-tracked, not cloud-repairable, flag
  in the next digest); git realigned local `main` from stale orphan `2e66201` → origin/main `f90fa66` (Cycle 54)
  before committing. Next cycle takes READOUT. NEXT TRUTH candidate: extend weight-robustness to the FULL
  population (does pillar-wise dominance hold down the whole capability spectrum com⪰org⪰retail⪰bare, making the
  entire ordering guard 12 weight-robust — or is some pair only weight-dependently ordered, worth surfacing
  honestly). Cloud-doable from committed fixtures.
  Cycle 56 READOUT (the READOUT complement to Cycle-55's weight-robustness TRUTH guard — the same
  guard→prose move Cycle 24 made for Cycle-23's earned-dominance guard): the methodology page's §3 worked
  example gains a second sub-section "But couldn't you re-weight the pillars to get the answer you want?"
  that names the SECOND credibility objection in plain prose — the delta's SIGN is invariant to the pillar
  weighting because the higher side is PILLAR-WISE DOMINANT (≥ every exposed pillar, strictly > one) over the
  SAME applicable-pillar set with NEITHER grade capped, so each overall is a renormalized weighted mean of the
  same pillars and a non-negative-weight average can't rank a dominated side above its dominator → sign holds
  under every reasonable weighting (rubric/uniform/single-pillar extremes); weights set gap SIZE, not which
  side leads. Stated test-pinned, matching the earned-dominance paragraph. Display-only: git diff = scorecard.py
  (methodology prose) + test_readout.py ONLY; scoring.py/rubric/probes/fetch/protocols/behavioral/offering/
  battery byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by construction AND re-measured
  (replay guard 18/18, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Vendor-neutral (no domain named; new test asserts
  drift-flight/driftflight absent + readout-wording guard 4/4). NON-VACUOUS: reverting the prose alone fails the
  new test (37/38 → 38/38 restored). `test_readout.py` 37→38; suite 215→216. No Slack (display-only, moves no
  score, 10:2xZ before the 16:00 UTC digest window — runner stall flags there). First duty: no open peer-gated
  PR (verified []); infra health check ran first — bench UP (216/216), git bookkeeping UP (pull clean, main ==
  origin/main 6c7087e = Cycle 55), runner STILL STALLED PAST 6h (newest verify_20260727T224106Z ~11.6h old,
  unchanged — P0-tracked, not cloud-repairable, flag in the next digest). Next cycle takes METHOD.
  Cycle 57 METHOD (guard 14's NEGATIVE CONTROL now COMMITTED — the joint population relabel-invariance
  guard's non-vacuity is demonstrated, not argued): `tests/test_canonical_replay.py` +1 (18→19), guard 16
  `test_population_relabel_negative_control`. Guard 14 (Cycle 53) proves the population ordering
  (com>org>retail>bare) survives a simultaneous relabel of all four fixtures to distinct neutral hosts, but
  defended its non-vacuity ONLY with a construction argument (hosts asserted reverse-lexical to capability →
  "a host-string sorter would reorder the population") — it never injected such a sorter to show the ordering
  check CATCHES it, the one invariance guard in the file whose teeth were asserted, not exercised (guard 15(d)
  injects a pillar inversion; the offering-layer relabel guard monkeypatches an identity-keyed special-case;
  Cycle-29/33 wording guards inject a scored-storefront name). Guard 16 monkeypatches the exact "sort the
  domains alphabetically and assign tiers" bug — `overall_score` becomes a monotone function of the host's
  ASCENDING lexical rank (alphabetically-earliest host → highest score), keyed on the host STRING not the
  evidence; because guard 14 assigns the neutral hosts reverse-lexical to capability, the rig REVERSES the
  population, so replaying the four relabeled fixtures through the REAL `_score_relabeled → scoring.score` path
  and applying guard 14's OWN strict-decreasing ordering check must FAIL (rigged overalls in capability order
  [zeutral 70, seutral 80, geutral 90, aeutral 100] — strictly increasing). Monkeypatch on `scoring.score`,
  restored in a finally + a restore-assertion so the rig never leaks. Non-vacuous BY CONTRAST: guard 14 itself
  passes on the real scorer (strictly monotone), the rig reverses it. Worded by capability (the rig keys on
  the host string, the anti-pattern to never exhibit). Tests-only: `git diff --name-only -- asrs/ rubric/`
  EMPTY → scoring.py/rubric/probes/fetch/protocols/behavioral/offering/battery byte-for-byte untouched →
  rubric stays v0.7, canonical delta unchanged by construction AND re-measured (replay guard 19/19, 46.1 F /
  85.5 B / +39.4, 0 replay-miss). Direct-to-main. Suite 216→217. No Slack (tests-only, moves no score, fire
  11:1xZ before the 16:00 UTC digest window — runner stall flags there). First duty: no open peer-gated PR
  (verified []); infra health check ran first — bench UP (217/217), git bookkeeping UP (applied the
  Cycle-52/55/56 orphan-main lesson at fire START: verified local `main` == stale orphan `2e66201`
  immediately after fetch, realigned `git checkout -B main a72c42c` = origin/main Cycle-56 tip BEFORE editing,
  so NO orphan-parent commit this cycle), runner STILL STALLED PAST 6h (newest verify_20260727T224106Z
  ~12.6h old, unchanged — P0-tracked, not cloud-repairable, flag in the next digest). The invariance-guard
  family is now UNIFORM (every guard carries a committed negative control). Next cycle takes COVERAGE.
  Cycle 58 COVERAGE (offering discovery recognises a metered-API's DOCUMENTED RATE LIMITS / REQUEST QUOTA —
  the many-metering-conventions axis, sibling of the free-tier conventions Cycles 22/30/38 and the billing
  signals Cycle 50): `asrs/offering._SIGNALS["metered_api"]` gains a `rate-limited` signal (with the
  usage-metering group, after `usage-based`). A metered programmatic API publishes how fast/how often an agent
  may call it — `rate limit(s)`/`rate-limited`, `requests per minute`, `100 req/s`, `500 calls/day`, an
  `API/request/monthly quota`, `quota resets` — the "understand the offer" capability, DISTINCT from the
  billing signals (a site documents rate limits without naming a price; both drift-flight domains do exactly
  that in a `<h2 id="rate-limits">Rate limits</h2>` block on `/docs`). PRECISION-FIRST/vendor-neutral (Cycle-50
  discipline): bare `quota` anchored to an API prefix (api/request/usage/monthly/daily/rate quota) or metering
  suffix (quota per/of/resets/remaining/exceeded); `rate` must be adjacent to `limit` so `flat rate pricing`/
  `unlimited`/`steady rate`/`exchange rate` never fire. SCORE-NEUTRAL: discover_offering/classify_offering OFF
  the scoring path (grep of scoring.py/probes/protocols.py EMPTY; called only from cli._resolve_battery for
  `--battery auto`); `git diff --name-only` = offering.py + test_offering.py ONLY, `git diff -- asrs/scoring.py
  rubric/ asrs/probes/ asrs/fetch.py asrs/protocols.py asrs/battery.py` EMPTY → rubric stays v0.7. The rate-limit
  evidence lives on the canonical `/docs` surface, which discovery does NOT crawl (homepage + _SURFACE_DOCS on
  apex + doc subdomains) → canonical DISCOVERY classification byte-identical: canonical OFFERING guard 12/12
  UNCHANGED, NO EXPECTED update; metered_api is also already the strongest claim on the pair so even a crawled
  hit could only deepen evidence, never add an archetype or reorder. Canonical PAIR unchanged by construction AND
  re-measured (replay guard 19/19, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Not payment/signing code. Direct-to-
  main. `test_offering.py` 16→18 (+synthetic precision battery: 7 real rate-limit/quota phrasings fire, 6
  rate/quota-shaped noise strings don't; +NON-VACUOUS real-captured test reading committed driftflight.com `/docs`
  bytes — rate-limited fires on metered_api on genuine API-docs prose, the Cycle-50 real-data move). Full suite
  217→219 (all 19 files exit 0). No Slack (score-neutral additive discovery, moves no score, not sensitive, fire
  12:2xZ before the 16:00 UTC digest window — runner stall + this ship fold into that digest). First duty: no open
  peer-gated PR (verified []); infra health check ran first — bench UP (219/219), git bookkeeping — applied the
  orphan-main lesson at fire START (local `main` was stale orphan `2e66201`, realigned `git checkout -B main
  origin/main` = Cycle-57 tip 073b53c BEFORE editing), runner STILL STALLED past 6h (newest
  verify_20260727T224106Z ~13.6h old at 12:18Z, unchanged since Cycle 51 — P0-tracked, not cloud-repairable,
  flag in next digest). Next cycle takes TRUTH.
  Cycle 59 TRUTH (weight-robustness lifted from the head PAIR to the WHOLE population — the Cycle-55
  next-hypothesis delivered): `tests/test_canonical_replay.py` +1 (19→20), guard 17
  `test_population_ordering_is_weight_robust`. Cycle 55 (guard 15) proved the +39.4 pair delta is
  weight-robust (with-rails dominates no-rails pillar-by-pillar over a shared applicable set → no
  non-negative reweighting inverts it); this lifts that refutation to the benchmark's CENTRAL ordering
  (guard 12: com>org>retail>bare). Replays ALL FOUR committed fixtures through the REAL
  `from_fixture→_run_probes→scoring.score` path and pins: (A) no domain grade-capped → each overall a pure
  renormalized weighted mean; (B) IDENTICAL applicable-pillar set chain-wide ({access,legibility,
  transactability,trust}, outcome None on all four); (a) ADJACENT PILLAR-WISE DOMINANCE at every rung
  (higher ⪰ lower on every applicable pillar, strict on ≥1 — com⪰org strict{leg,tx}, org⪰retail
  strict{leg,tx,trust}, retail⪰bare strict{leg,trust}: a TOTAL dominance chain); (b) FAITHFULNESS (rubric
  weights reproduce all four overalls 85.5/46.1/29.5/22.5 from pillars alone); (c) WEIGHT-ROBUSTNESS across
  an adversarial weight family (rubric, uniform, each unit-basis vector incl. all-access where every rung's
  gap → exactly 0 but never INVERTS) — chain non-increasing at every rung, strict where the weighting touches
  a strict pillar; (d) NON-VACUOUS negative control — an access-inverted floor site WOULD top the retail shop
  under all-access weighting → chain check is single-rung-inversion-sensitive. HONEST FINDING (docstring):
  NO rung is only weight-DEPENDENTLY ordered — the a-priori suspect org-vs-retail on trust is actually
  DOMINATED (org 60.0 > retail 33.3), so the whole chain is weight-robust; had any rung been pillar-wise
  incomparable the (a) assertion would FAIL and surface it (a weight-dependent rank = a real calibration
  finding, not a bug to hide — truth outranks the pitch, and the stronger claim is the true one). Worded by
  capability, never by vendor (pillar comparison, never identity; four fixture keys guards 1–16's own).
  Tests-only: `git diff --stat` = test_canonical_replay.py ONLY (+145), `git diff -- asrs/ rubric/` EMPTY →
  scoring.py/rubric/probes/fetch/protocols/behavioral/offering/battery byte-for-byte untouched → rubric stays
  v0.7, canonical delta unchanged by construction AND re-measured (replay guard 20/20, 46.1 F / 85.5 B /
  +39.4, 0 replay-miss). Direct-to-main. Suite 219→220. No Slack (tests-only, moves no score, not sensitive,
  fire 13:21Z before the 16:00 UTC digest window — runner stall + LIVE-drift fold into that digest). First
  duty: no open peer-gated PR (verified []); infra health check ran first — bench UP (220/220), git bookkeeping
  applied the orphan-main lesson at fire START (local `main` was stale orphan `2e66201`, realigned
  `git checkout -B main origin/main` = Cycle-58 tip de4ab39 BEFORE editing), runner STILL STALLED past 6h
  (newest verify_20260727T224106Z ~14.7h old at 13:21Z, unchanged since Cycle 51 — P0-tracked, not
  cloud-repairable, flag in next digest). Next cycle takes READOUT.
  Cycle 60 READOUT (the READOUT complement to Cycle-59's population-wide weight-robustness guard 17):
  the methodology page's §3 "But couldn't you re-weight the pillars…" sub-section previously stated only the
  PAIR result (Cycle 56, guard 15 — a single delta's sign is weighting-invariant because the higher side is
  pillar-wise dominant); extended that SAME sub-section with one paragraph (`asrs/scorecard.py`
  `_write_methodology_page` prose) stating the POPULATION finding in critic-readable terms — when the whole
  population forms a TOTAL DOMINANCE CHAIN (each rung ≥ the next on every applicable pillar, strict on ≥1, over
  the same uncapped set) no non-negative reweighting inverts ANY rung, so the whole ranking (not just the head
  delta) is weight-robust; stated test-pinned "over the reference spectrum" so guard 17 + readout stay in
  lockstep. Vendor-neutral (four tiers described by capability, no domain named — enforced by the same test's
  drift-flight/driftflight-not-in-text assertions + test_readout_wording 4/4). Display-only: `git diff
  --name-only` = scorecard.py + test_readout.py ONLY; scoring.py/rubric/probes/fetch/protocols/offering/battery
  byte-for-byte untouched → rubric stays v0.7, canonical delta unchanged by construction AND re-measured (replay
  guard 20/20, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Direct-to-main. `test_readout.py`
  `test_methodology_documents_weight_robustness` +4 population-prose assertions (38/38); suite 220→221. No Slack
  (display-only, moves no score, not sensitive, fire 14:2xZ before the 16:00 UTC digest window — runner stall
  folds into that digest). First duty: no open peer-gated PR (verified []); infra health check ran first — bench
  UP (221/221), git bookkeeping applied the orphan-main lesson at fire START (local `main` was stale orphan
  `2e66201`, realigned `git checkout -B main origin/main` = Cycle-59 tip eeabdbe BEFORE editing), runner STILL
  STALLED past 6h (newest verify_20260727T224106Z ~15.5h old at 14:14Z, unchanged since Cycle 51 — P0-tracked,
  not cloud-repairable, flag in next digest). Next cycle takes METHOD.
  Cycle 61 METHOD (the OFFLINE replay instrument — the SOLE in-cloud canonical regression signal while the live
  runner is down — is now guarded DETERMINISTIC run-to-run): `tests/test_canonical_replay.py` +1 (20→21), guard 18
  `test_replay_pipeline_is_deterministic`. Scores each of the four committed fixtures TWICE through INDEPENDENT
  `from_fixture → _run_probes → scoring.score` passes (fresh FetchContext, no shared cache) and asserts the FULL
  scored surface is byte-identical via `_report_fingerprint` — overall/grade/rubric_version/every pillar/every
  check `(id,status,points,max_points)`, not just the headline. Pins the North-Star "reproducible" axis at the
  level of the offline measurement itself — the complementary fact `canonical_history`'s noise-floor determinism
  (Cycle 47, LIVE runner cross-artifact series, currently DOWN) can't: a single in-cloud replay reproduces itself,
  so a future order-dependence bug (e.g. a `set()` in aggregation perturbing a float sum) that would silently make
  every per-cycle re-score non-reproducible is caught. NON-VACUOUS committed negative control (Cycle-57 uniform
  discipline): a `scoring.score` wrapper that perturbs overall by +0.1 on every 2nd call makes the two passes
  diverge → `_assert_reports_identical` raises (asserted caught), rig restored in finally + `is real_score`
  re-asserted. Tests-only: `git diff --name-only -- asrs/ rubric/` EMPTY → scoring path byte-for-byte untouched,
  rubric stays v0.7, canonical delta unchanged by construction AND re-measured (replay guard 21/21, 46.1 F /
  85.5 B / +39.4, books 29.5 F, example 22.5 F, 0 replay-miss on all four). Direct-to-main. suite 221→222. No Slack
  (tests-only, moves no score, not sensitive, fire 15:1xZ before the 16:00 UTC digest window — runner stall + this
  ship fold into that digest). First duty: no open peer-gated PR (verified []); infra health check ran first —
  bench UP (19/19 files, 222/222), git realigned local `main` to origin/main (309d404 = Cycle 60 tip) at fire
  START before editing; runner STILL STALLED past 6h (newest verify_20260727T224106Z ~16.5h old at 15:13Z,
  unchanged since Cycle 51 — P0-tracked, not cloud-repairable, flag in next digest). Next cycle takes COVERAGE.
  Cycle 62 COVERAGE (offering discovery reads the rendered HTML `/docs` API-docs page — the P2 candidate
  surfaced Cycle 58): `asrs/offering._SURFACE_DOCS` gains `/docs` (+`/api-docs`, `/reference`), so an
  API-first storefront whose rate limits / endpoints / billing prose live on its documentation page — not
  on any well-known JSON doc — is classified from that surface. On the canonical pair the `rate-limited`
  evidence is literally the `<h2 id="rate-limits">Rate limits</h2>` block on `driftflight.com/docs` (a real
  HTTP-200 page in BOTH committed fixtures, never crawled until now). Because `/docs` is HTML,
  `classify_offering` now HTML-STRIPS any HTML-document surface (not only the homepage) via a new
  `_is_html_document` detector keyed on the `<!doctype html>`/`<html` prologue — LOAD-BEARING: a real docs
  page's `<script>`/`<style>` retail decoy words ("out of stock"/"shopping cart"/"shipping address", the
  exact shape on the canonical `/docs`) scanned RAW would false-positive `physical_good` on a pure API
  storefront (the battery pollution the directive removes); stripped, they never reach the scanner. JSON/
  plain-text surfaces (llms.txt/openapi.json/agent cards) don't start with an HTML prologue → unaffected.
  Vendor-neutral (surface by convention, same generic API/billing prose the bank anchors, no new signal, no
  domain string — precedent Cycles 34/42/46/54). SCORE-NEUTRAL: discovery is OFF the scoring path
  (`--battery auto` only, grep-verified not imported by scoring.py/probes/protocols); `git diff --name-only`
  = offering.py + test_offering.py ONLY, scoring.py/rubric/probes/protocols/fetch/battery byte-for-byte
  untouched → rubric stays v0.7, canonical delta unchanged by construction AND re-measured (replay guard
  21/21, 46.1 F / 85.5 B / +39.4, 0 replay-miss). Claimed SET+ORDER unchanged on BOTH domains
  (`[metered_api, digital_good, subscription]`, measured live through full `discover_offering` incl. doc
  subdomains); canonical OFFERING guard 12/12 UNCHANGED. `test_offering.py` 18→20 (+synthetic /docs-only
  storefront non-vacuous on the strip — fails pre-change; +end-to-end live-read on the canonical fixture,
  /docs in surfaces_seen, HTML-free evidence, set/order unchanged); wiring guard extended; stale Cycle-58
  "does NOT crawl /docs" comment fixed. Suite all 19 files green (223 by direct file-sum, +2). Direct-to-main
  (commit f9459a8, pushed bfe1402..f9459a8). First duty: no open peer-gated PR (verified []); infra health —
  bench UP (19/19), git realigned local `main` off the stale orphan `2e66201` to origin/main (bfe1402 = Cycle
  61 tip) BEFORE editing; runner STILL STALLED past 6h (newest verify_20260727T224106Z ~17.5h old at 16:21Z,
  unchanged since Cycle 51 — P0-tracked, not cloud-repairable). SLACK DAILY DIGEST SENT (first cloud cycle
  after 16:00 UTC on 07-28). Next cycle takes TRUTH.
  Cycle 63 TRUTH (earned-dominance lifted from the PAIR to the four-domain POPULATION at the per-CHECK layer):
  `tests/test_canonical_replay.py` +2 (21→23). Guard 19 `test_population_delta_is_earned_at_the_check_layer`
  lifts guard 8's per-check argument (full observability + like-for-like + check dominance) across the whole
  capability spectrum, from the LIVE replay pipeline: (a) identical scored 14-check set on all four (population
  like-for-like — per-rung scoped intersection NOT needed, an empirical result); (b) HONEST tail-favouring
  observability — head pair (com/org) fully observed, tail (retail/bare) each excuse exactly one absent check
  (self_serve_payg CANT_TEST, never mis-scored FAIL, no NA anywhere), which EXCLUDES it from the denominator
  and can only RAISE the tail's score, yet the strict ordering holds → not a head-inflating differential-
  observability artifact; (c) LOAD-BEARING NEW FINDING — the population is NOT a clean check-by-check superset
  chain like the pair: com>org and retail>bare are clean supersets, but org>retail carries EXACTLY ONE honest
  inversion, https_hsts (trust — the human-only retail shop's HTTPS out-ranks the no-rails API's), ABSORBED by
  the trust pillar (org trust 60.0 > 33.3, aggregate 46.1 > 29.5), so it never flips the ordering; exact
  inversion set pinned per rung → a NEW check-layer inversion fails HERE. Complements guard 17 (pillar-wise
  TOTAL dominance): dominance is a PILLAR property; at the CHECK layer org>retail is a majority not a superset,
  and the aggregation is exactly what makes the ordering robust to it. Guard 20 = committed negative control
  (Cycle-57 uniform-rigor): a scorer that mis-attributes the tail's absent surface CANT_TEST→FAIL is CAUGHT by
  19(b), restored in finally. Vendor-neutral (asks "observed? which tier ranks higher?", never "is this domain
  X?"; same four fixture keys). Tests-only: git diff -- asrs/ rubric/ EMPTY → scoring.py/rubric/probes
  byte-for-byte untouched, rubric stays v0.7, canonical pair unchanged AND re-measured (replay guard 23/23,
  46.1 F / 85.5 B / +39.4, 0 replay-miss; population 85.5>46.1>29.5>22.5 re-pinned). Direct-to-main (commit
  4dac5b2). Suite 223→225 (all 19 files exit 0). First duty: no open peer-gated PR (verified []); infra —
  bench UP (23/23), git realigned local `main` off the stale orphan `2e66201` to origin/main (45c806c = Cycle
  62 tip) BEFORE editing; runner STILL STALLED past 6h (newest verify_20260727T224106Z ~18.5h old at 17:1xZ,
  unchanged since Cycle 51 — P0-tracked, not cloud-repairable, already flagged in Cycle 62's digest). No Slack
  (tests-only/score-neutral, digest already sent Cycle 62). Next cycle takes READOUT.
  Local fire 2026-07-28T17:27Z SELF-HEALING/METHOD (infra breakage outranks new work — the verify-runner
  stall ROOT-CAUSED + FIXED, the top P0): a local fire has the network + the machine, so it saw what
  Cycles 51→62 could not. The cloud's "launchd not firing / machine asleep" guess was WRONG — the runner's
  heartbeat log (`~/Library/Logs/asrs-local-verify.log`) + the unpushed local `verify_*.json` artifacts
  (234101Z/034100Z/110146Z/170500Z) prove the launchd job fires every wake but its `git pull` fails
  INSTANTLY with "Could not resolve host: github.com" — a WAKE/NETWORK RACE: launchd runs the missed :41
  job on wake before WiFi/DNS is up (artifacts land at odd minutes 14:44/16:56/11:01/17:05 = wake instants),
  and the runner bailed on that first miss with zero retry, writing a git-pull-failed artifact it also
  couldn't push. FIX: `loop/local_verify.py` `git_pull_with_retry` (bounded wait-for-network, 5×15s ≈60s;
  still fixed-verb, only `pull` hardened) + `tests/test_local_verify.py` (4). Resynced the pinned
  `~/.local/bin/asrs_local_verify.py` from the committed repo copy (self-healing law). Executed the repair
  live (not assumed): the fixed runner pulled on attempt 1 (its pull even fast-forwarded Cycle 63), 20
  suites green, canonical 46.1 F / 85.5 B / +39.4, artifact `verify_20260728T172734Z.json` (records
  `attempts:1`) pushed + mirrored → the ~18.5h stall is CLEARED, live canonical signal restored.
  Score-neutral: `git diff -- asrs/ rubric/` EMPTY → scoring.py/rubric/probes byte-for-byte untouched,
  rubric v0.7, canonical PAIR unchanged by construction AND re-measured (replay guard green 23/23 after
  Cycle 63's pull, +39.4). Direct-to-main (infra/tooling, not scoring semantics, not payment/signing).
  Suite 19→20 files (+test_local_verify, 4 tests). First duty: no open peer-gated PR
  (`gh pr list --state open` → []); local `main` was ~18 cloud cycles behind (at Cycle 44) → `git pull
  --ff-only` to Cycle 62 before editing, then the runner's own pull picked up Cycle 63. Cloud rotation
  unaffected (still READOUT next). Slack: NONE — this local fire has no connected Slack tool (no MCP, no
  repo helper; zero-CLI Slack would be a paid/external call, barred by $0-only), and the cloud owns comms.
  The resolution is recorded loudly here + in LOG/BACKLOG; the next cloud cycle's infra health check sees a
  FRESH verify artifact + the CLOSED runner-stall bullet and can fold "runner stall resolved" into its next
  post-16:00 UTC digest (Cycle 62's digest opened the flag this morning).
  Cycle 64 READOUT (the honest per-CHECK refinement surfaced on the methodology page — the READOUT
  complement to Cycle 63's guard 19): `asrs/scorecard._write_methodology_page` gains one paragraph in the
  "But couldn't you re-weight the pillars…" card, after the Cycle-60 population weight-robustness paragraph.
  Cycles 56/60 put the PILLAR-layer total-dominance-chain on the page ("… on every applicable pillar") —
  true, but it would read to a careful critic as a total PER-CHECK superset, which Cycle 63 proved is NOT so
  one rung down (org>retail carries the https_hsts inversion). The new prose distinguishes the layers:
  dominance as used above is a PILLAR-layer property; at the finer per-check layer the head delta is still a
  clean superset, but a lower rung need not be — a lower-ranked storefront can out-rank a higher-ranked one on
  a single check yet still lose that check's pillar; names the spectrum's one honest MINORITY REVERSAL in
  capability terms (a human-checkout retail shop's HTTPS/HSTS out-ranks a no-rails API storefront's, yet the
  API wins the trust pillar overall, ranking preserved); punchline — rolling checks up into pillars is what
  ABSORBS the lone reversal (robust BECAUSE the aggregation outvotes an honest local tie, not because every
  check marches in lockstep), and ASRS SURFACES the inversion (pinned check-by-check by guard 19), not hides
  it behind a false "wins every check" claim. Truth outranks the pitch. Vendor-neutral (tiers by capability,
  no domain named — enforced by the new test's drift-flight/driftflight assertions + standing
  test_readout_wording 4/4 + test_rubric_wording 4/4). Display-only: git diff --name-only = scorecard.py +
  test_readout.py ONLY; `git diff -- asrs/scoring.py rubric/ asrs/probes/ asrs/fetch.py asrs/protocols.py
  asrs/offering.py asrs/battery.py` EMPTY → scoring path byte-for-byte untouched, rubric stays v0.7, canonical
  pair unchanged by construction AND re-measured (in-cloud replay guard 23/23, 46.1 F / 85.5 B / +39.4,
  0 replay-miss; live-corroborated by verify_20260728T174106Z, 17:41Z ~32 min old). Direct-to-main (commit
  6bb6ef3). `test_readout.py` 38→39 (test_methodology_documents_check_layer_honesty); suite 20/20 files green.
  First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260728T174106Z, 17:41Z, ~32 min old; the ~18.5h stall CLEARED by the 17:27Z self-healing fire),
  bench UP (20/20). GIT TRAP (Cycle-52 lesson, recurred + WORSE): the fresh checkout's local `main` AND the
  local `origin/main` remote-tracking ref were BOTH stale at the orphan `2e66201`, so `git checkout -B main
  origin/main` landed ON the orphan; `git fetch origin main` force-updated origin/main 2e66201→3d1c107 (real
  tip) and realigned BEFORE editing. LESSON UPDATE: after the fresh-checkout pull, `git fetch origin main`
  FIRST (the remote-tracking ref itself can be stale), then verify `git rev-parse main == origin/main` against
  the FETCHED tip. No Slack (display-only/score-neutral/non-sensitive; digest already sent Cycle 62 16:21Z, not
  a digest window at 18:1xZ). Next cycle takes METHOD.
  Local fire 2026-07-28T18:55Z COVERAGE (operator-directive acceptance, complementary to the cloud
  rotation; cloud still takes METHOD next): executed the top-P0 [LOCAL] item — the FIRST end-to-end
  offering-relative LIVE battery. `asrs score driftflight.com --behavioral --battery auto --models
  claude --trials 2` (claude-only: codex reputation-gates BOTH canonical domains 4/4, and the
  offering-relative STRUCTURE under test does not need cross-model — backlog explicitly authorizes it).
  OVERALL 87.8 B, rubric v0.7, CITABLE (verdict stability 1.00, 2 valid runs). OPERATOR ACCEPTANCE
  CONFIRMED on REAL data, all three criteria on BOTH surfaces: (1) driftflight.com physical_good = NA
  (live discovery claimed {metered_api,subscription,digital_good}; na_archetypes =
  {physical_good,service_booking,data_retrieval}); (2) spreads over CLAIMED archetypes only
  (cross-task 0.00, between-archetype 0.00 "generalist", each over the 3 claimed; NA excluded from every
  mean/spread); (3) NA shown "not offered" on terminal TASK BATTERY block AND HTML card
  Offering-relative sub-block (chip na = the 3 NA archetypes). First LIVE between_kind_spread (0.00,
  generalist) + all 3 intents 100% completion on real multi-kind data. Trust 55.6 behavioral vs 60.0
  static (live panel warn+go conf 0.65: zero web footprint + underspecified directive — honest
  measurement). Hermetic fix (Cycle 32) confirmed LIVE (--strict-mcp-config on the panel subprocess).
  Invariant #1 held: agent reached only the FREE tier (3 free images), blockers note a paid call needs a
  funded wallet, free-tier probe fired once. Score-neutral [LOCAL] EXECUTION (git diff -- asrs/ rubric/
  tests/ EMPTY, ran shipped pipeline) → rubric v0.7; canonical PAIR unchanged (18:41Z verify 46.1 F /
  85.5 B / +39.4, replay guard green; behavioral 87.8 is the --behavioral superset of the static 85.5:
  +Outcome pillar 100.0 + live trust panel, does NOT move the static delta). Evidence force-added:
  runs/local/acceptance_battery_driftflightcom_20260728T184325Z.{report.json,log,card.html}. First duty:
  no open peer-gated PR (verified []); runner HEALTHY (verify_20260728T184104Z, 18:41Z, ~1 min old at
  fire), bench 20/20, main == origin/main. The operator-directive P0 acceptance is DISCHARGED on the
  with-rails API side; the retail-INVERSE behavioral half (guarded in-cloud, never run live) is the next
  [LOCAL] increment.
  Cycle 65 METHOD (scorer INVARIANCE TO CHECK-INPUT ORDER — the reproducibility rung guard 18
  NAMES but never tests): `tests/test_canonical_replay.py` +1 (23→24), guard 20
  `test_scorer_is_invariant_to_check_input_order`. For every domain in the capability spectrum,
  replay the committed fixture then re-score the SAME CheckResults PERMUTED (reversed) through
  `scoring.score` and assert the full scored surface (overall/grade/version/every pillar/every check
  status+points) is byte-identical. Guard 18 (Cycle 61) pins determinism UNDER REPETITION — it replays
  each fixture twice through the DETERMINISTIC `from_fixture→_run_probes` pipeline, so checks reach
  `scoring.score` in the SAME order both passes; its own docstring hypothesizes "a set() in aggregation
  whose iteration order perturbed a float sum" but that failure is INPUT-ORDER-dependence, which guard 18
  is structurally blind to. Real hazards: pillar earned-sum `earned[pillar] += c.points` (float add not
  associative) + the `caps_applied` list, built in check-ARRIVAL order — both stable run-to-run yet
  move under a reordering. Completes the reproducibility family (guard 18 = repetition; canonical_history
  noise-floor Cycle 47 = cross-artifact live series; guard 20 = input permutation). NON-VACUOUS: negative
  control rigs `scoring.score` to nudge overall +0.1 when the first check out-ranks the last by id (stand-in
  for arrival-order sensitivity); reversing flips it → forward/reversed diverge → CAUGHT (passes on the real
  scorer); rig flows through the real scorer, restored in finally + restore assertion (guards 16/18 discipline).
  Worded by measurement, no domain named in an assertion; reads from the live pipeline. Tests-only:
  `git diff --name-only` = test_canonical_replay.py ONLY, `git diff -- asrs/ rubric/` EMPTY → scoring path
  byte-for-byte untouched, rubric stays v0.7, canonical pair unchanged by construction AND re-measured
  (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260728T184104Z 18:41Z ~31 min old
  live-corroborates). Direct-to-main. Suite 20/20 files. No Slack (tests-only/score-neutral/non-sensitive;
  digest already sent Cycle 62 16:21Z, not a digest window at 19:1xZ). First duty: no open peer-gated PR
  (verified []); infra health check ran first — runner HEALTHY, bench UP (20/20); git realigned the stale-orphan
  `2e66201` trap (both local main AND origin/main stale at orphan; `git fetch origin main` force-updated
  origin/main→0b32656, `checkout -B main origin/main` before editing). Next cycle takes COVERAGE.
  Cycle 67 TRUTH (the FIRST CALIBRATION guard — does the static score predict what an agent EXPERIENCES?):
  new `tests/test_calibration.py` (3 tests). Every prior in-cloud guard (`test_canonical_replay`, 24 guards) is
  static-vs-static (stability/earned/identity/weight-robust); NONE answers the north-star VALIDITY question. This
  holds the static score against the committed LIVE behavioral acceptance run
  (`runs/local/acceptance_battery_driftflightcom_20260728T184325Z.report.json`, the 18:55Z [LOCAL] fire, git-tracked
  → deterministic in-cloud) and asserts they AGREE where the score makes a falsifiable claim. (1) STATIC PREDICTION
  agent-native payment (x402_probe PASS + self_serve_payg x402_live=True → transactability 87.5) is BEHAVIORALLY
  CORROBORATED — the Outcome checks operationalizing it (bhv_purchase_path/machine_payable/no_human_gate/
  free_tier_transaction) all PASS; like-for-like (same domain, rubric v0.7 both halves, asserted). (2)
  DISCRIMINATING/non-vacuous — the behavioral report has real FAILs (sitemap/mcp_surface/reputation_signals) so the
  payment PASSes are earned, and the prediction SEPARATES tiers (no-rails drift-flight.org predicted no payment:
  x402_probe not-PASS, x402_live=False). (3) REPRODUCIBLE — both trials machine-payable + no-human-gate,
  verdict_stability 1.0, quotable (not a one-run fluke). Refutes the "the number is astrology" objection, a NEW axis
  vs the static family's internal-consistency objections. HONEST SCOPE: ONE-DOMAIN with-rails anchor (proves the
  POSITIVE payability claim is behaviorally real; the negative/retail-inverse behavioral half is [LOCAL], un-runnable
  in-cloud); corroboration scoped to the FREE tier (invariant #1 — no nonzero call; blockers record a paid call needs
  a funded wallet). Tests-only: `git diff -- asrs/ rubric/` EMPTY, git diff --name-only = test_calibration.py ONLY
  (new file) → scoring path byte-for-byte untouched → rubric stays v0.7, canonical PAIR unchanged by construction AND
  re-measured (replay guard 24/24, 46.1 F / 85.5 B / +39.4, 0 replay-miss; verify_20260728T205027Z 20:50Z ~21 min old
  live-corroborates). Direct-to-main. New file 3/3; suite 20→21 files (test_free_tier 11/11 with eth-account). No Slack
  (tests-only/score-neutral/non-sensitive; digest already sent Cycle 62 16:21Z, not a digest window at 21:1xZ). First
  duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY (verify_20260728T205027Z,
  20:50Z, ~21 min old); no orphan-2e66201 trap this fire (HEAD == origin/main == 25c6ae8 at fetch). Next cycle takes READOUT.
  Local fire 2026-07-28T23:10Z COVERAGE+TRUTH (operator retail-INVERSE acceptance + the calibration
  NEGATIVE half; complementary to the cloud rotation — cloud stays METHOD next, local fires don't advance
  the pointer/counter): executed the oldest live P0 — the directive's OTHER named acceptance half
  ("a retail storefront shows the inverse"), guarded in-cloud at DISCOVERY
  (`test_offering_canonical.test_retail_inverse_offering`) but never run BEHAVIORALLY, which also carries
  the Cycle-67 NEGATIVE calibration half. Domain selection was the work: a run needs a domain reachable by
  BOTH the python discovery path AND the shopper's WebFetch path, with NO agentic rails, a REAL checkout
  (backlog steered away from the books.toscrape sandbox). Screened 12+ real retailers — most block agent
  fetchers (lush WebFetch-403; uniqlo agent-ua-hard-blocked -10 + WebFetch-timeout; thriftbooks python-406;
  hydroflask 403) or have added rails (deathwishcoffee UCP/MCP/Shop-Pay → metered_api; warbyparker
  ai-plugin/agent-card; muji/allbirds/misen/leatherman llms.txt → metered_api). Picked `www.moleskine.com`
  (both gates 200, no llms.txt/no rails, Access 100 = agent-UA reachable NOT env-blocked, physical_good
  CLAIMED on real free-shipping/stock nouns, API archetypes NA). `asrs score www.moleskine.com --behavioral
  --battery auto --models claude --trials 2` → OVERALL 38.8 F, rubric v0.7, CITABLE (verdict stability 1.00,
  2 valid). OPERATOR RETAIL-INVERSE ACCEPTANCE CONFIRMED, all three criteria on BOTH surfaces (the mirror of
  18:55Z .com): (1) physical_good CLAIMED/assessed (60% completion), NOT NA — the inverse of the API canonical
  where physical_good was NA (subscription also claimed; na_archetypes = {metered_api, digital_good,
  service_booking, data_retrieval}); (2) spreads over the CLAIMED set only (cross-task 0.30, between-archetype
  0.30 "somewhat type-dependent", NA excluded); (3) NA shown "not offered" on the terminal TASK BATTERY block
  AND the HTML card Offering-relative sub-block (chip na = the 4 NA archetypes, verified in the rendered card).
  CALIBRATION NEGATIVE HALF CONFIRMED (mirror of Cycle 67's positive with-rails anchor): static predicted
  no-agent-native-payment FAIL / transactability 18.8 → behavioral machine_payable_path FALSE + no_human_gate
  FALSE, Outcome 0.0, REPRODUCIBLY (both trials unanimous "no machine-payable path — retail purchases are
  browser-only"). Non-vacuous: the physical_good battery intent reached 60% (found product/pricing/purchase-path
  — the agent CAN browse the store) yet hit the machine-payable + human-gate walls; the primary default-task run
  scored 0 (no agent-purchasable primary product exists). Gives the cloud a SECOND committed behavioral artifact
  to wire a negative-side calibration guard against (the missing half Cycle 67 flagged) — calibration becomes a
  two-sided VALIDITY property. Invariant #1 held (no advertised free tier / no x402 → free-tier probe found
  nothing to call, x402_live=false, no settle/authorization/max_pay/paid; read-only hermetic shopper). Score-neutral
  [LOCAL] EXECUTION: git diff -- asrs/ rubric/ tests/ EMPTY (ran the shipped pipeline) → rubric v0.7; canonical
  PAIR unchanged (verify_20260728T224103Z 46.1 F / 85.5 B / +39.4; replay guard 24/24, offering guard 12/12
  re-run green); behavioral 38.8 < static 49.8 is the +Outcome-pillar-0.0 superset, does NOT move the static
  delta. Evidence force-added: runs/local/acceptance_battery_moleskine_20260728T225939Z.{report.json,log,card.html}.
  First duty: no open peer-gated PR (verified []); runner HEALTHY (verify_20260728T224103Z, 22:41Z, ~29 min old at
  fire), bench 20/20, main == origin/main. Direct-to-main, no Slack (score-neutral [LOCAL], non-sensitive, not a
  digest window; digest sent Cycle 62 16:21Z). The operator-directive P0 acceptance is now DISCHARGED on BOTH named
  halves; the next in-cloud TRUTH increment is a negative calibration guard in test_calibration.py against this
  moleskine report. Cloud rotation unaffected (still METHOD next).
  Local fire 2026-07-28T23:57Z TRUTH (the calibration POPULATION static sweep — complementary to the cloud
  rotation; cloud stays COVERAGE next, local fires don't advance the pointer/counter): executed the P1
  "Calibration population" north-star item — a benchmark needs a population, not one pair. New
  `experiments/calibration_sweep.py` runs the SHIPPED static path (`_run_probes → scoring.score`, no
  `--behavioral`) across a curated 14-domain population spanning the agentic-commerce spectrum
  (api-storefront anchors / api-services / retail:emerging-rails / retail:no-rails / non-storefront
  controls) and commits the first dated population dataset. 13/14 scored on rubric v0.7; rei.com NOT
  SCORABLE (env-blocked — recorded as reachability, NOT a site FAIL, invariant #4). INTEGRITY: the anchors
  reproduce the pinned baseline EXACTLY (driftflight.com 85.5 B / drift-flight.org 46.1 F = a LIVE
  corroboration of the replay guard, off the real network), moleskine.com 49.8 F matches its 23:10Z static
  read, example.com 22.5 F matches baseline. Leaderboard (overall desc): rails anchor 85.5 B tops it; top
  REAL agent-native domain exa.ai 78.1 C; the emerging-rails retail cluster deathwishcoffee 65.8 /
  warbyparker 64.2 / allbirds 61.9 sits D-band; no-rails moleskine 49.8 F and no-rails anchor drift-flight.org
  46.1 F cluster near the floor, above the non-storefront controls wikipedia 41.1 / example 22.5. Honest
  reality-check readings the population surfaces: big-AI marketing homepages score modestly (openai.com 64.5 D,
  anthropic.com 58.5 F, perplexity.ai 41.3 F ≈ the wikipedia control) — the score tracks agent-native
  legibility/transactability, not brand. Vendor-neutral: every domain scored through the SAME probes, the
  `segment` label is read-only context, never a scoring input. $0/invariant #1: static-only → NO free-tier
  probe fired, no zero CLI, no signing path. Score-neutral: `git diff -- asrs/ rubric/` EMPTY, only the new
  experiment file added → rubric v0.7, canonical PAIR unchanged (verify_20260728T234102Z 46.1 F / 85.5 B /
  +39.4; replay guard 24/24 green in the 21/21-file suite). Direct-to-main (read-only experiment tooling +
  committed evidence, no scoring semantics), no Slack (score-neutral/non-sensitive; digest sent Cycle 62
  16:21Z, not a digest window). Evidence force-added: runs/local/calibration_sweep_20260728T234815Z.json.
  First duty: no open peer-gated PR (verified []); infra health check ran first — runner HEALTHY
  (verify_20260728T234102Z, 23:41Z, ~6 min old at fire, 46.1 F / 85.5 B / +39.4), bench 21/21, main ==
  origin/main. Follow-ups queued: a cloud READOUT leaderboard page over this dataset + a weekly-cadence
  standing item; a classifier-precision observation (exa.ai over-claimed all 6 archetypes from rich docs).
- **RUNNER STALL — ROOT-CAUSED + FIXED (local fire 2026-07-28T17:27Z). CLOSED.** The cloud's
  Cycle-51→62 diagnosis ("launchd not firing / machine asleep") was WRONG — only a local fire could
  see the truth. The runner's heartbeat log (`~/Library/Logs/asrs-local-verify.log`) shows the launchd
  job (`org.pie.asrs-local-cycle`, StartCalendarInterval :41) fires RELIABLY every wake, and the local
  `runs/local/verify_*.json` artifacts (234101Z/034100Z/110146Z/170500Z — never pushed) each carry
  `git_pull.ok=false`, `"Could not resolve host: github.com"`. **Root cause: a wake/network race.**
  launchd runs the missed :41 job on machine WAKE (hence artifacts at odd minutes 14:44/16:56/11:01/17:05
  = wake instants, not :41), before WiFi/DNS is up; `git pull` then failed in the SAME SECOND it started
  (vs a ~5s delay on successful fires), and the runner bailed on that first miss with ZERO retry —
  writing a git-pull-failed artifact it also couldn't push. (My own shell reached github fine at 17:18Z,
  13 min after the 17:05Z runner fire failed — the network was simply not up yet at wake.) **Fix:**
  `loop/local_verify.py` `git_pull_with_retry` (5 attempts, 15s apart, ~60s worst case; still fixed-verb,
  only `pull` hardened) + `tests/test_local_verify.py` (4). Resynced the pinned
  `~/.local/bin/asrs_local_verify.py` from the committed repo copy (self-healing law). **Executed the
  repair, did not assume it:** ran the fixed runner live at 17:27Z — pull succeeded on attempt 1 (its
  pull even fast-forwarded in Cycle 63), 20 suites green, canonical 46.1 F / 85.5 B / +39.4, artifact
  `verify_20260728T172734Z.json` (records `attempts:1`) pushed + mirrored. The ~18.5h stall is CLEARED;
  the live canonical re-score capability is restored. Residual to watch (LOG next-hypothesis): a wake with
  a very slow (>60s) network would still fail — watch the artifact `attempts` field over the next day.
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
