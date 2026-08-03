"""Static-prediction vs behavioral-reality calibration guard.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_calibration.py

THE VALIDITY QUESTION.  Every other in-cloud regression guard
(``test_canonical_replay``) is STATIC-vs-STATIC: it re-scores committed fixtures
and pins that the number is stable, earned, identity-invariant, weight-robust.
None of them answers the benchmark's north-star validity question —

    does the STATIC score predict what an AGENT actually experiences?

A number that no agent's lived experience corroborates is astrology, however
internally consistent.  This file is the first CALIBRATION axis: it holds the
static score up against a committed LIVE behavioral run and asserts the two
AGREE where the score makes a falsifiable claim.

THE ANCHOR.  On 2026-07-28T18:55Z a [LOCAL] fire executed the operator-directive
acceptance battery — the first end-to-end offering-relative LIVE behavioral run —
against the with-rails API storefront driftflight.com
(``asrs score driftflight.com --behavioral --battery auto --models claude
--trials 2``), and force-committed the report under ``runs/local/`` (git-tracked,
so this guard is deterministic in-cloud with no network).  Its static half is the
committed ``fixtures/canonical/driftflight.com.json`` replay pinned at 85.5 B.

THE CLAIM UNDER TEST.  The static score PREDICTS that an agent can pay
programmatically here — ``x402_probe`` PASSES and ``self_serve_payg`` records a
live x402 rail, so the transactability pillar credits agent-native payment.  The
behavioral run CORROBORATES it: the shopper actually reached a machine-payable
path with no human gate and completed the free-tier transaction, so the Outcome
pillar's payment checks all PASS — reproducibly across both trials.  Prediction
== experience.  If a future change ever made the static score claim payability on
evidence the behavioral run contradicts (or vice versa), that mismatch is a
calibration defect this guard fails on.

THE NEGATIVE ANCHOR (the symmetric half — landed).  Calibration is only
trustworthy if the score's NEGATIVE prediction is also behaviorally real: a site
the score says an agent CANNOT pay programmatically must actually stop the agent.
On 2026-07-28T23:10Z a [LOCAL] fire ran the same offering-relative acceptance
battery against a no-rails retail storefront (``www.moleskine.com``) and
force-committed the report.  Its static half predicts NO agent-native payment
(``x402_probe`` does not pass, ``self_serve_payg`` records x402_live=False,
transactability at the no-rails floor); its behavioral half CORROBORATES the
wall (``machine_payable_path`` and ``no_human_gate`` FALSE across both trials,
Outcome pillar 0.0), reproducibly.  Prediction == experience on the negative
side too.  Together the two anchors make calibration a TWO-SIDED property:
positive payability real on the with-rails API storefront, negative wall real on
the no-rails retail storefront — a prediction that points OPPOSITE ways on the
two, not a universal pass that would "agree" with anything.

HONEST SCOPE (attribution invariant, applied to calibration).
- The negative anchor has no committed static fixture (moleskine.com is not in
  ``fixtures/canonical/``; capturing one needs network -> [LOCAL]).  Its static
  PREDICTION is therefore read from the static checks embedded in the behavioral
  report's own full-probe crawl, not cross-validated against a separate offline
  replay the way the with-rails anchor is (tests 1/4).  Capturing the fixture to
  give the negative side the same two-crawl cross-validation is a [LOCAL]
  follow-up, not a blocker on the two-sided property.
- The negative FAILs are attribution-honest: Access is fully credited (the agent
  reached the site) and the physical_good battery intent reached partial
  completion (the agent BROWSED the store) — the wall is the payment path, not
  un-reachability.  A no-rails retailer has no free tier, so
  bhv_free_tier_transaction is (honestly) not_applicable, not a scored FAIL.
- The positive corroboration is precisely scoped to what the agent DID: it
  reached the machine-payable PATH and completed the FREE-tier transaction
  (invariant #1 — no nonzero-value call was made; both trials' blockers record
  that a paid call needs a funded wallet).  "Agent-native payment REACHABLE",
  never "a paid purchase was executed".
"""

from __future__ import annotations

import json
import os
import sys

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs import scoring  # noqa: E402
from asrs import scorecard  # noqa: E402
from asrs.cli import _run_probes  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.types import Status  # noqa: E402

_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# The committed LIVE behavioral acceptance anchor (force-added; ``runs/`` is
# otherwise gitignored).  When a fresh acceptance battery supersedes it, point
# this constant at the new committed report and re-confirm the numbers.
_BEHAVIORAL_REPORT = os.path.join(
    _REPO_ROOT,
    "runs",
    "local",
    "acceptance_battery_driftflightcom_20260728T184325Z.report.json",
)

# The behavioral domain and the static fixture that models it — they MUST be the
# same storefront for the comparison to be like-for-like.
_ANCHOR_DOMAIN = "driftflight.com"

# The Outcome-pillar checks that OPERATIONALIZE the static "agent can pay
# programmatically" prediction — the behavioral shopper actually doing what the
# score says is possible.  bhv_free_tier_transaction is the invariant-#1-safe
# corroboration (a completed $0 transaction, not a paid call).
_PAYMENT_OUTCOME_CHECKS = (
    "bhv_purchase_path",
    "bhv_machine_payable",
    "bhv_no_human_gate",
    "bhv_free_tier_transaction",
)

# The committed LIVE behavioral NEGATIVE anchor — a no-rails retail storefront
# where the static score predicts NO agent-native payment (force-added at the
# 2026-07-28T23:10Z local fire; ``runs/`` is otherwise gitignored).  Same rubric
# v0.7 as the positive anchor, so the two are like-for-like.  moleskine.com has
# NO committed static fixture (capturing one needs network -> [LOCAL]), so its
# static prediction is read from the static checks embedded in this behavioral
# report rather than from a separate offline replay.
_NEGATIVE_REPORT = os.path.join(
    _REPO_ROOT,
    "runs",
    "local",
    "acceptance_battery_moleskine_20260728T225939Z.report.json",
)
_NEGATIVE_DOMAIN = "www.moleskine.com"

# The Outcome checks that OPERATIONALIZE the NEGATIVE "an agent CANNOT pay
# programmatically here" prediction — the shopper hitting the wall the score
# predicts.  bhv_free_tier_transaction is DELIBERATELY excluded: a no-rails
# retailer has no free tier, so that check is honestly not_applicable, not a FAIL
# — asserting it FAILs would misattribute a structural NA as a payment wall.
_NEGATIVE_PAYMENT_OUTCOME_CHECKS = (
    "bhv_purchase_path",
    "bhv_machine_payable",
    "bhv_no_human_gate",
)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _static_report(domain: str):
    """Replay ``fixtures/canonical/<domain>.json`` through the real pipeline.

    Same offline path ``test_canonical_replay`` uses — no network.
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    checks = _run_probes(ctx)
    report = scoring.score(checks, scoring.load_rubric(None), domain)
    misses = [
        key for key, res in ctx._cache.items()
        if res.error and "replay-miss" in res.error
    ]
    return report, misses


def _static_check(report, check_id):
    for c in report.checks:
        if c.check_id == check_id:
            return c
    raise AssertionError(f"static check {check_id!r} absent from {report.domain} report")


def _load_behavioral():
    with open(_BEHAVIORAL_REPORT, encoding="utf-8") as fh:
        return json.load(fh)


def _load_negative():
    with open(_NEGATIVE_REPORT, encoding="utf-8") as fh:
        return json.load(fh)


def _bhv_check(report: dict, check_id: str) -> dict:
    for c in report["checks"]:
        if c["check_id"] == check_id:
            return c
    raise AssertionError(f"behavioral check {check_id!r} absent from the committed report")


# ---------------------------------------------------------------------------
# 1. The static agent-native-payment PREDICTION is behaviorally CORROBORATED.
#    The score says "an agent can pay programmatically here"; the live shopper
#    actually did it, reproducibly.  Prediction == experience.
# ---------------------------------------------------------------------------
def test_static_payment_prediction_is_behaviorally_corroborated() -> None:
    print("test_static_payment_prediction_is_behaviorally_corroborated")
    static, misses = _static_report(_ANCHOR_DOMAIN)
    bhv = _load_behavioral()

    # Like-for-like: the static fixture and the behavioral run must describe the
    # SAME storefront on the SAME rubric version, or the comparison is meaningless.
    _check(not misses, f"{_ANCHOR_DOMAIN}: static replay has no replay-miss (like-for-like)")
    _check(
        bhv["domain"] == _ANCHOR_DOMAIN == static.domain,
        f"behavioral + static describe the same domain {_ANCHOR_DOMAIN!r} "
        f"(got behavioral={bhv['domain']!r}, static={static.domain!r})",
    )
    _check(
        bhv["rubric_version"] == static.rubric_version == "0.7",
        f"behavioral + static share rubric_version 0.7 "
        f"(got behavioral={bhv['rubric_version']!r}, static={static.rubric_version!r})",
    )

    # STATIC PREDICTION: the score claims agent-native programmatic payment is
    # present — x402_probe PASSES and self_serve_payg records a live x402 rail.
    _check(
        _static_check(static, "x402_probe").status is Status.PASS,
        "static PREDICTION: x402_probe PASSES — score claims agent-native payment reachable",
    )
    _check(
        _static_check(static, "self_serve_payg").evidence.get("x402_live") is True,
        "static PREDICTION: self_serve_payg records x402_live=True",
    )
    _check(
        static.pillar_scores["transactability"] > 0,
        "static PREDICTION: transactability pillar credits the payment capability "
        f"(got {static.pillar_scores['transactability']})",
    )

    # BEHAVIORAL EXPERIENCE: the shopper actually reached the machine-payable path
    # with no human gate and completed the free-tier transaction — every Outcome
    # check that operationalizes the prediction PASSES.
    for cid in _PAYMENT_OUTCOME_CHECKS:
        bc = _bhv_check(bhv, cid)
        _check(
            bc["pillar"] == "outcome" and bc["status"] == "pass",
            f"behavioral EXPERIENCE: {cid} PASSES (agent did what the score predicted)",
        )

    # AGREEMENT: the two independent measurements — static evidence-of-capability
    # and live agent behavior — point the SAME way.  The score predicted what the
    # agent experienced.
    _check(True, "AGREEMENT: static payability prediction == behavioral payability experience")


# ---------------------------------------------------------------------------
# 2. The anchor is DISCRIMINATING, not a vacuous all-pass.  A report that credits
#    everything, or a prediction that claims payability for every site, would
#    "agree" trivially.  Pin that neither is the case.
# ---------------------------------------------------------------------------
def test_calibration_anchor_is_discriminating() -> None:
    print("test_calibration_anchor_is_discriminating")
    bhv = _load_behavioral()

    # (a) The behavioral report is NOT all-pass — it records real FAIL checks, so
    #     the Outcome PASSes above are earned, not a report that passes everything.
    fails = [c["check_id"] for c in bhv["checks"] if c["status"] == "fail"]
    _check(
        len(fails) >= 1,
        f"behavioral report has >=1 real FAIL check — the payment PASSes are discriminating "
        f"(fails: {fails})",
    )

    # (b) The static prediction SEPARATES capability tiers: the no-rails API
    #     storefront (drift-flight.org) is predicted to have NO agent-native
    #     payment — x402_probe does NOT pass, x402_live is False.  "The score
    #     predicts payability" is a claim that distinguishes .com from .org, not a
    #     universal pass that would agree with any behavioral run.
    org, org_misses = _static_report("drift-flight.org")
    _check(not org_misses, "drift-flight.org: static replay has no replay-miss")
    _check(
        _static_check(org, "x402_probe").status is not Status.PASS,
        "static PREDICTION discriminates: no-rails drift-flight.org x402_probe does NOT pass",
    )
    _check(
        _static_check(org, "self_serve_payg").evidence.get("x402_live") is False,
        "static PREDICTION discriminates: no-rails drift-flight.org x402_live=False",
    )
    # Honest scope: the negative side's BEHAVIORAL corroboration (an agent that
    # actually hits the wall the score predicts) is a [LOCAL] increment — this
    # anchor is one-sided (with-rails only).
    print(
        "  note: this is a ONE-DOMAIN with-rails anchor; the no-rails/retail "
        "behavioral half is queued [LOCAL]"
    )


# ---------------------------------------------------------------------------
# 3. The corroboration is REPRODUCIBLE, not a one-run fluke.  A single lucky
#    browse is not a calibration signal; agreement across trials with a stable
#    verdict is what makes the anchor citable (the north-star "reproducible" axis).
# ---------------------------------------------------------------------------
def test_behavioral_corroboration_is_reproducible() -> None:
    print("test_behavioral_corroboration_is_reproducible")
    bhv = _load_behavioral()

    runs = bhv.get("behavioral_runs", [])
    _check(len(runs) >= 2, f"the anchor rests on >=2 behavioral trials (got {len(runs)})")

    # Both trials independently reached the machine-payable path with no human
    # gate — the corroboration is stable across runs, not a single fortunate one.
    for i, run in enumerate(runs):
        cps = run.get("checkpoints", {})
        _check(
            cps.get("machine_payable_path") is True,
            f"trial {i} (model={run.get('model')}): machine_payable_path reached",
        )
        _check(
            cps.get("no_human_gate") is True,
            f"trial {i} (model={run.get('model')}): no_human_gate",
        )

    # The panel's own verdict-stability read agrees: the run is citable.
    quot = bhv.get("quotability") or {}
    _check(
        quot.get("quotable") is True,
        f"the behavioral anchor is quotable/citable (quotability={quot})",
    )
    _check(
        quot.get("verdict_stability") == 1.0,
        f"verdict_stability == 1.0 across the trials (got {quot.get('verdict_stability')})",
    )


# ---------------------------------------------------------------------------
# 4. The calibration rests on a SHARED STATIC BASE, not just a matching name.
#    "Prediction == experience" is only meaningful if the two measurements score
#    the SAME static evidence.  Tests 1-3 pin domain + rubric_version STRING
#    equality — but two runs can share those and still have scored different
#    crawls (e.g. a behavioral run whose transactability differs from the fixture
#    would make "the score predicts 87.5 payability" corroborate a run that
#    actually saw something else).  Pin that every STATIC-OBSERVABLE pillar the
#    two measurements share is IDENTICAL, so the prediction the anchor corroborates
#    is the very number the static guard pins — and note the reliability corollary:
#    the payability magnitude (transactability 87.5) is reproduced across TWO
#    INDEPENDENT crawls (the committed fixture capture and the 18:55Z behavioral
#    crawl), so it is crawl-stable, not a lucky snapshot.
# ---------------------------------------------------------------------------

# The pillars both measurements compute from the same static crawl.  Excluded:
# ``outcome`` (behavioral-only — the static replay scores it None) and ``trust``
# (the behavioral run augments it with a LIVE trust panel), which is exactly why
# they anchor the non-vacuity check below — the behavioral report is a genuine
# augmented SUPERSET, not the static fixture re-dumped.
_SHARED_STATIC_PILLARS = ("access", "legibility", "transactability")


def test_calibration_rests_on_a_shared_static_base() -> None:
    print("test_calibration_rests_on_a_shared_static_base")
    static, misses = _static_report(_ANCHOR_DOMAIN)
    bhv = _load_behavioral()
    _check(not misses, f"{_ANCHOR_DOMAIN}: static replay has no replay-miss (like-for-like)")

    bhv_pillars = bhv["pillar_scores"]

    # SHARED STATIC BASE: every static-observable pillar is IDENTICAL across the
    # two independent measurements — the anchor corroborates the SAME static
    # evidence the score predicts on, not a differently-scored run that merely
    # shares a name.  Includes transactability, so the payability PREDICTION
    # magnitude (87.5) the calibration rests on is provably the one the static
    # replay guard pins — and it reproduces across two independent crawls.
    for pillar in _SHARED_STATIC_PILLARS:
        s = static.pillar_scores[pillar]
        b = bhv_pillars[pillar]
        _check(
            s is not None and b is not None and abs(s - b) < 1e-9,
            f"shared static base: {pillar} identical across static replay and "
            f"behavioral run (static={s}, behavioral={b})",
        )

    # NON-VACUOUS: the behavioral report is a genuine augmented SUPERSET, not the
    # static fixture re-dumped — the identical static pillars above are an
    # agreement between two DISTINCT measurements, not a tautology.
    # (a) the Outcome pillar is SCORED behaviorally but NULL in the static replay.
    _check(
        static.pillar_scores["outcome"] is None,
        "static replay scores Outcome null (behavioral-only pillar)",
    )
    _check(
        isinstance(bhv_pillars.get("outcome"), (int, float)),
        f"behavioral run SCORES the Outcome pillar the static replay lacks "
        f"(got {bhv_pillars.get('outcome')}) — genuine behavioral superset",
    )
    # (b) the Trust pillar DIFFERS — the behavioral run adds a LIVE trust panel,
    #     so the two reports are distinct runs, not the same file twice.
    _check(
        static.pillar_scores["trust"] is not None
        and abs(static.pillar_scores["trust"] - bhv_pillars["trust"]) > 1e-9,
        f"Trust differs (static={static.pillar_scores['trust']}, "
        f"behavioral={bhv_pillars['trust']}) — behavioral augments it with a live panel",
    )


# ---------------------------------------------------------------------------
# 5. THE NEGATIVE HALF (mirror of test 1).  Calibration is only trustworthy if
#    the score's NEGATIVE prediction is also behaviorally real.  On the no-rails
#    retail anchor the static score claims NO agent-native payment; the live
#    shopper actually hit the wall — no machine-payable path, a human gate,
#    Outcome pillar 0.  Prediction == experience on the negative side too.
# ---------------------------------------------------------------------------
def test_static_no_payment_prediction_is_behaviorally_corroborated() -> None:
    print("test_static_no_payment_prediction_is_behaviorally_corroborated")
    neg = _load_negative()

    # LIKE-FOR-LIKE with the positive anchor: SAME rubric version, so "the score
    # predicts no payability" is measured on the same scale as the with-rails
    # "the score predicts payability".  (The static prediction is read from the
    # report's own embedded static checks — moleskine.com has no committed static
    # fixture; see the module docstring's HONEST SCOPE.)
    _check(
        neg["domain"] == _NEGATIVE_DOMAIN,
        f"negative anchor describes {_NEGATIVE_DOMAIN!r} (got {neg['domain']!r})",
    )
    _check(
        neg["rubric_version"] == "0.7",
        f"negative anchor shares rubric_version 0.7 with the positive anchor "
        f"(got {neg['rubric_version']!r})",
    )

    # STATIC PREDICTION: the score claims NO agent-native programmatic payment —
    # x402_probe does NOT pass and self_serve_payg records no live x402 rail, so
    # transactability credits no agent-native payment (the no-rails floor, well
    # below the with-rails anchor's 87.5).
    _check(
        _bhv_check(neg, "x402_probe")["status"] != "pass",
        "static PREDICTION: x402_probe does NOT pass — score claims no agent-native payment",
    )
    _check(
        (_bhv_check(neg, "self_serve_payg").get("evidence") or {}).get("x402_live") is False,
        "static PREDICTION: self_serve_payg records x402_live=False",
    )
    _check(
        neg["pillar_scores"]["transactability"] < 87.5,
        "static PREDICTION: transactability credits no agent-native payment "
        f"(got {neg['pillar_scores']['transactability']}, << with-rails 87.5)",
    )

    # BEHAVIORAL EXPERIENCE: the shopper hit the wall the score predicts — no
    # machine-payable path, a human gate — so every Outcome check that
    # operationalizes the negative prediction FAILS, and the Outcome pillar is 0.
    for cid in _NEGATIVE_PAYMENT_OUTCOME_CHECKS:
        bc = _bhv_check(neg, cid)
        _check(
            bc["pillar"] == "outcome" and bc["status"] == "fail",
            f"behavioral EXPERIENCE: {cid} FAILS (agent hit the wall the score predicted)",
        )
    _check(
        neg["pillar_scores"]["outcome"] == 0.0,
        f"behavioral EXPERIENCE: Outcome pillar 0.0 (got {neg['pillar_scores']['outcome']})",
    )
    # ATTRIBUTION HONESTY (invariant #1/#4): a no-rails retailer has no free tier,
    # so bhv_free_tier_transaction is not_applicable — NOT a scored FAIL.  The
    # wall is the payment path, not a missing $0 probe.
    _check(
        _bhv_check(neg, "bhv_free_tier_transaction")["status"] == "not_applicable",
        "attribution: bhv_free_tier_transaction is NA (no free tier), not scored as a wall",
    )

    _check(
        True,
        "AGREEMENT: static NO-payability prediction == behavioral NO-payability experience",
    )


# ---------------------------------------------------------------------------
# 6. The negative anchor is a GENUINE, REACHABLE retail storefront — the
#    offering-relative INVERSE of the API anchor — not an unreachable/env-blocked
#    null that would "fail" trivially.  Attribution honesty applied to the
#    negative side: the FAILs are a real payment wall, not un-observability.
# ---------------------------------------------------------------------------
def test_negative_anchor_is_a_genuine_reachable_retail_storefront() -> None:
    print("test_negative_anchor_is_a_genuine_reachable_retail_storefront")
    neg = _load_negative()

    # REACHABLE, not env-blocked: Access fully credited.  The downstream Outcome
    # FAILs are evidence of a missing PAYMENT capability, not of un-observability
    # (invariant #4 — a site is never punished for what couldn't be seen).
    _check(
        neg["pillar_scores"]["access"] == 100.0,
        f"negative anchor is reachable, not env-blocked (access={neg['pillar_scores']['access']})",
    )

    # RETAIL INVERSE of the API anchor: physical_good is CLAIMED/assessed and the
    # API archetypes are NA.  So "no agent-native payment" is measured against a
    # storefront that really sells something (a shop), not a null/non-storefront.
    bs = neg["battery_summary"]
    _check(
        "physical_good" in bs["assessed_archetypes"],
        f"negative anchor CLAIMS physical_good (retail inverse) "
        f"(assessed={bs['assessed_archetypes']})",
    )
    _check(
        set(bs["na_archetypes"]) >= {"metered_api", "digital_good", "data_retrieval"},
        f"the API archetypes are NA on the retail inverse (na={bs['na_archetypes']})",
    )

    # NON-VACUOUS: the agent actually BROWSED the store — the physical_good intent
    # reached partial completion — yet still hit the payment wall.  The negative
    # calibration is 'browsed but cannot pay programmatically', not 'never got in'.
    pg = next(k for k in bs["per_kind"] if k["kind"] == "physical_good")
    _check(
        pg["mean_completion"] > 0.0,
        f"agent made real progress on the store (physical_good completion "
        f"{pg['mean_completion']}) — the wall is payment, not reachability",
    )


# ---------------------------------------------------------------------------
# 7. The negative corroboration is REPRODUCIBLE (mirror of test 3).  One unlucky
#    browse is not a calibration signal; a wall that both trials hit with a
#    stable verdict is.
# ---------------------------------------------------------------------------
def test_negative_corroboration_is_reproducible() -> None:
    print("test_negative_corroboration_is_reproducible")
    neg = _load_negative()

    runs = neg.get("behavioral_runs", [])
    _check(len(runs) >= 2, f"the negative anchor rests on >=2 behavioral trials (got {len(runs)})")

    # Both trials independently FAILED to reach a machine-payable path and both
    # hit a human gate — the wall is stable across runs, not one unlucky browse.
    for i, run in enumerate(runs):
        cps = run.get("checkpoints", {})
        _check(
            cps.get("machine_payable_path") is False,
            f"trial {i} (model={run.get('model')}): no machine_payable_path (reproducible wall)",
        )
        _check(
            cps.get("no_human_gate") is False,
            f"trial {i} (model={run.get('model')}): human gate present (reproducible wall)",
        )

    quot = neg.get("quotability") or {}
    _check(quot.get("quotable") is True, f"the negative anchor is quotable/citable ({quot})")
    _check(
        quot.get("verdict_stability") == 1.0,
        f"verdict_stability == 1.0 across the trials (got {quot.get('verdict_stability')})",
    )


# ---------------------------------------------------------------------------
# 8. THE TWO-SIDED PROPERTY (the capstone).  With both anchors in hand,
#    calibration is no longer one-sided: at the SAME payment Outcome checkpoints,
#    the with-rails anchor PASSES and the no-rails retail anchor FAILS.  The
#    score's payability prediction points OPPOSITE ways on the two storefronts —
#    it is not a universal pass that would "agree" with any behavioral run — and
#    live behavior confirms BOTH directions.
# ---------------------------------------------------------------------------
def test_calibration_is_two_sided() -> None:
    print("test_calibration_is_two_sided")
    pos = _load_behavioral()
    neg = _load_negative()

    # Both anchors on the SAME rubric version — positive and negative calibration
    # claims are measured on one scale (like-for-like).
    _check(
        pos["rubric_version"] == neg["rubric_version"] == "0.7",
        f"both anchors on rubric 0.7 (pos={pos['rubric_version']}, neg={neg['rubric_version']})",
    )

    # OPPOSITE DIRECTIONS at the SAME checkpoints: with-rails PASSES, no-rails
    # retail FAILS.  The prediction discriminates; behavior confirms both sides.
    for cid in _NEGATIVE_PAYMENT_OUTCOME_CHECKS:
        _check(
            _bhv_check(pos, cid)["status"] == "pass",
            f"with-rails anchor: {cid} PASSES",
        )
        _check(
            _bhv_check(neg, cid)["status"] == "fail",
            f"no-rails retail anchor: {cid} FAILS (opposite direction, same checkpoint)",
        )

    # And the pillar-level summary agrees: Outcome fully credited on one, zero on
    # the other — the two-sided calibration property in one line.
    _check(
        pos["pillar_scores"]["outcome"] == 100.0 and neg["pillar_scores"]["outcome"] == 0.0,
        f"Outcome pillar: with-rails {pos['pillar_scores']['outcome']} vs "
        f"no-rails {neg['pillar_scores']['outcome']}",
    )


# ---------------------------------------------------------------------------
# 9. THE PAYABILITY PREDICTION IS ATTRIBUTABLY THE AGENT-NATIVE PAYMENT
#    CAPABILITY, not diffuse transactability credit.  Tests 1/4 corroborate the
#    with-rails anchor's transactability (87.5) behaviorally and pin it as a
#    shared static base — but "transactability > 0", even "== 87.5", does not on
#    its own prove the credit the behavioral run corroborates is EARNED by
#    agent-native payment.  A refactor could keep x402_probe PASS yet source the
#    transactability magnitude from an unrelated transactability check, silently
#    hollowing the calibration link: the score would still "predict payability"
#    while the number it rests on came from something the shopper never exercised.
#    This guard closes that gap on the canonical pair itself: the ENTIRE
#    transactability point-gap between the with-rails and no-rails storefronts is
#    earned by the agent-native payment checks the anchor corroborates
#    (x402_probe, self_serve_payg); every NON-payment transactability check
#    contributes ZERO to the gap.  So the payability magnitude the calibration
#    anchor rests on is attributably the agent-native payment capability — the
#    static counterpart of the _PAYMENT_OUTCOME_CHECKS the live shopper hit.
#
#    This ties the calibration anchor into the same maintenance contract as the
#    replay guard (test_canonical_replay) and the canonical-drift baseline: the
#    with-rails anchor and the LIVE canonical-drift subject are the SAME domain
#    and the SAME pillar (driftflight.com transactability).  If a [LOCAL]
#    re-baseline ever re-captures that fixture at the softened live value, the
#    87.5 assertion below goes red BY DESIGN, forcing this calibration anchor's
#    payability magnitude to be revisited in the same PR — the coupling the
#    BACKLOG "is the with-rails anchor itself degrading?" question needs monitored.
# ---------------------------------------------------------------------------

# The transactability checks that OPERATIONALIZE agent-native programmatic
# payment on the STATIC side — the with-rails rail the calibration anchor
# corroborates.  x402_probe (the x402 402 / machine-payable challenge) and
# self_serve_payg (self-serve pay-as-you-go) are exactly the two the module
# docstring names; they are the static counterparts of the behavioral
# _PAYMENT_OUTCOME_CHECKS.  Capability-worded, vendor-neutral.
_STATIC_PAYMENT_CHECKS = ("x402_probe", "self_serve_payg")


def test_payability_prediction_is_attributably_agent_native_payment() -> None:
    print("test_payability_prediction_is_attributably_agent_native_payment")
    com, com_misses = _static_report(_ANCHOR_DOMAIN)          # with-rails
    org, org_misses = _static_report("drift-flight.org")      # no-rails
    _check(
        not com_misses and not org_misses,
        "both canonical static replays are like-for-like (no replay-miss)",
    )

    # Same rubric -> the two sides share the transactability check SET.
    com_tx = {c.check_id: c for c in com.checks if c.pillar == "transactability"}
    org_tx = {c.check_id: c for c in org.checks if c.pillar == "transactability"}
    _check(
        set(com_tx) == set(org_tx) and bool(com_tx),
        f"both sides share the transactability check set ({sorted(com_tx)})",
    )
    for cid in _STATIC_PAYMENT_CHECKS:
        _check(
            cid in com_tx,
            f"agent-native payment check {cid!r} is a transactability check",
        )

    # (a) DISCRIMINATING: each agent-native payment check is MORE credited on the
    #     with-rails storefront than the no-rails one — the payment capability is
    #     present with-rails, absent/partial no-rails, in the predicted direction.
    for cid in _STATIC_PAYMENT_CHECKS:
        _check(
            com_tx[cid].points > org_tx[cid].points,
            f"{cid}: more credited with-rails ({com_tx[cid].points}) than "
            f"no-rails ({org_tx[cid].points}) — payability discriminates",
        )

    # (b) ATTRIBUTION: the ENTIRE transactability raw-point gap between the two
    #     storefronts is earned by the agent-native payment checks; every
    #     non-payment transactability check nets ZERO to the gap.  So the
    #     payability magnitude the anchor corroborates is attributably the
    #     agent-native payment capability, not diffuse transactability credit.
    total_gap = sum(com_tx[cid].points - org_tx[cid].points for cid in com_tx)
    payment_gap = sum(
        com_tx[cid].points - org_tx[cid].points for cid in _STATIC_PAYMENT_CHECKS
    )
    nonpayment_gap = sum(
        com_tx[cid].points - org_tx[cid].points
        for cid in com_tx
        if cid not in _STATIC_PAYMENT_CHECKS
    )
    _check(total_gap > 0, f"there IS a transactability gap to attribute (raw {total_gap})")
    _check(
        abs(payment_gap - total_gap) < 1e-9,
        f"the WHOLE transactability gap is earned by agent-native payment "
        f"(payment_gap={payment_gap}, total_gap={total_gap})",
    )
    _check(
        abs(nonpayment_gap) < 1e-9,
        f"non-payment transactability checks net ZERO to the gap "
        f"(nonpayment_gap={nonpayment_gap}) — the control",
    )

    # (c) NON-VACUOUS: a non-payment transactability check really IS in the set
    #     (mcp_surface), so (b) is "the gap is all-payment DESPITE a non-payment
    #     check existing", not the trivial "payment is the only check".
    nonpayment_ids = [cid for cid in com_tx if cid not in _STATIC_PAYMENT_CHECKS]
    _check(
        len(nonpayment_ids) >= 1,
        f"a non-payment transactability check exists as the control ({nonpayment_ids})",
    )

    # (d) The attributed capability IS the magnitude the anchor corroborates: the
    #     with-rails transactability is exactly the 87.5 tests 1/4 rest on.  This
    #     literal is the re-baseline tripwire (see the maintenance note above).
    _check(
        abs(com.pillar_scores["transactability"] - 87.5) < 1e-9,
        f"with-rails transactability is the pinned 87.5 the anchor corroborates "
        f"(got {com.pillar_scores['transactability']})",
    )


# ---------------------------------------------------------------------------
# 10. THE READOUT'S ATTRIBUTION AND THE CALIBRATION'S ATTRIBUTION CANNOT SILENTLY
#     DRIFT APART.  Two layers now each attribute the transactability score to a
#     capability, from OPPOSITE ends of the pipeline:
#       - the CALIBRATION layer (test 9) proves the with-rails/no-rails
#         transactability point-gap is earned entirely by the agent-native
#         payment checks in ``_STATIC_PAYMENT_CHECKS`` (x402_probe, self_serve_payg);
#       - the READOUT layer (scorecard._pillar_top_earner, Cycle 192) surfaces, on
#         the HTML card, the single check that earns the MOST transactability points
#         — the "earned by <check>" caption a human reads off the card.
#     Nothing yet forces these to name the SAME capability.  A refactor could keep
#     the calibration attribution intact (payment still earns the gap) while the
#     card's top-earner caption drifts to a non-payment transactability check
#     (e.g. if mcp_surface began out-earning the payment checks) — the card would
#     then tell a reader "transactability earned by <non-payment check>" while the
#     science says the payability magnitude rests on agent-native payment.  The
#     reader's mental model and the calibration attribution would silently diverge.
#     This guard closes that gap on BOTH canonical anchors: the check the readout
#     surfaces as the transactability earner IS one of the agent-native payment
#     checks the calibration attribution credits — one source of truth
#     (``_STATIC_PAYMENT_CHECKS``) shared by the card and the calibration reasoning.
#     Non-vacuous: a non-payment transactability check (mcp_surface) really is in
#     the set on both sides, so this is "the readout names a payment check DESPITE
#     a non-payment check being present", not "payment is the only check there is".
# ---------------------------------------------------------------------------
def test_readout_earner_and_calibration_attribution_cannot_drift() -> None:
    print("test_readout_earner_and_calibration_attribution_cannot_drift")
    # Both canonical storefronts: the readout must attribute transactability to the
    # SAME agent-native payment capability the calibration attribution reasons about.
    for dom in (_ANCHOR_DOMAIN, "drift-flight.org"):
        rep, misses = _static_report(dom)
        _check(not misses, f"{dom} static replay is like-for-like (no replay-miss)")
        d = json.loads(rep.to_json())

        tx_checks = [c for c in d["checks"] if c["pillar"] == "transactability"]
        _check(bool(tx_checks), f"{dom} has transactability checks to attribute")

        # The check the READOUT surfaces to a card reader as the transactability earner.
        top = scorecard._pillar_top_earner(d, "transactability")
        _check(top is not None, f"{dom} transactability names an earner on the card")
        finding, pts = top

        # Map the surfaced (finding, points) back to the concrete check the card names.
        named = [
            c for c in tx_checks
            if (c.get("finding") or c.get("check_id")) == finding
            and abs(float(c["points"]) - pts) < 1e-9
        ]
        _check(
            len(named) == 1,
            f"{dom}: the card's surfaced earner maps to exactly one transactability "
            f"check (finding={finding!r}, points={pts}, matched={[c['check_id'] for c in named]})",
        )

        # THE COUPLING: the check the readout surfaces IS one of the calibration's
        # agent-native payment checks — the two attributions share one source of truth.
        earner_id = named[0]["check_id"]
        _check(
            earner_id in _STATIC_PAYMENT_CHECKS,
            f"{dom}: the card attributes transactability to agent-native payment "
            f"({earner_id!r} in {_STATIC_PAYMENT_CHECKS}) — the readout and the "
            f"calibration attribution name the same capability",
        )

        # NON-VACUOUS: a non-payment transactability check is genuinely present and is
        # NOT what the card surfaced — the coupling holds despite a real alternative.
        nonpayment_ids = [
            c["check_id"] for c in tx_checks if c["check_id"] not in _STATIC_PAYMENT_CHECKS
        ]
        _check(
            nonpayment_ids and earner_id not in nonpayment_ids,
            f"{dom}: a non-payment transactability check exists as the control "
            f"({nonpayment_ids}) yet is not the surfaced earner",
        )


# ---------------------------------------------------------------------------
# 11. THE NO-RAILS TRANSACTABILITY FLOOR IS CAPABILITY-ATTRIBUTABLE AND
#     STOREFRONT-TYPE-INVARIANT.  Test 9 attributes the with-rails/no-rails
#     transactability GAP to agent-native payment on the canonical API PAIR
#     (driftflight.com vs drift-flight.org).  But the negative CALIBRATION anchor
#     is a genuinely different storefront TYPE — a no-rails RETAIL shop
#     (moleskine.com) — and nothing yet pins that ITS low transactability is the
#     same capability-absence floor, reached the same way, as the no-rails API
#     storefront.  If "the score predicts no agent-native payment" were a retail
#     ARTIFACT (a shop scores low because it sells physical goods, not because it
#     lacks payment rails), the negative calibration would be measuring storefront
#     CATEGORY, not payment readiness — and the two-sided property (test 8) would
#     be confounded by type.
#
#     This guard closes that gap using ONLY committed evidence (no [LOCAL]
#     fixture): the no-rails RETAIL anchor (moleskine.com, read from its LIVE
#     behavioral crawl) and the no-rails API storefront (drift-flight.org, from
#     the OFFLINE fixture replay) land on the IDENTICAL transactability floor,
#     earned by the IDENTICAL per-check point vector, with the agent-native
#     payment gap-check (x402_probe) at ZERO on both.  Two structurally different
#     storefronts, two independent crawl METHODS, one capability-attributable
#     floor.  So the negative prediction is reproducible across storefront TYPE
#     and crawl METHOD, and it is attributably the ABSENCE of agent-native payment
#     — not a retail artifact, not a diffuse low score.  It discriminates from the
#     with-rails ceiling (the payment gap-check earns full there; the floor sits
#     well below 87.5), and the behavioral shopper on the retail instance actually
#     hit the payment wall (tests 5/7), so the type-invariant static floor is
#     behaviorally real on the retail side.  This is the negative-side, type-
#     crossing mirror of test 9's positive attribution — and unlike the negative
#     anchor's absent two-crawl STATIC cross-validation (still [LOCAL]), it needs
#     no fixture: the retail floor is read from the report's own embedded checks
#     and matched against a SECOND, independent no-rails crawl.
# ---------------------------------------------------------------------------
def test_no_rails_transactability_floor_is_capability_attributable_and_type_invariant() -> None:
    print("test_no_rails_transactability_floor_is_capability_attributable_and_type_invariant")
    neg = _load_negative()                                 # no-rails RETAIL, live behavioral crawl
    org, org_misses = _static_report("drift-flight.org")   # no-rails API, offline fixture replay
    com, com_misses = _static_report(_ANCHOR_DOMAIN)       # with-rails API ceiling
    _check(
        not org_misses and not com_misses,
        "canonical static replays are like-for-like (no replay-miss)",
    )

    # LIKE-FOR-LIKE scale: all three anchors on rubric 0.7.
    _check(
        neg["rubric_version"] == org.rubric_version == com.rubric_version == "0.7",
        f"all anchors on rubric 0.7 (retail={neg['rubric_version']}, "
        f"api-norails={org.rubric_version}, api-rails={com.rubric_version})",
    )

    # NON-VACUOUS — two DISTINCT storefront types + two DISTINCT crawl methods.
    #   retail no-rails: physical_good CLAIMED, floor read from a LIVE behavioral crawl;
    #   API no-rails:    physical_good NA, floor from an OFFLINE fixture replay.
    neg_bs = neg["battery_summary"]
    _check(
        "physical_good" in neg_bs["assessed_archetypes"],
        f"retail anchor CLAIMS physical_good (a genuinely different storefront type) "
        f"(assessed={neg_bs['assessed_archetypes']})",
    )
    _check(
        len(neg.get("behavioral_runs", [])) >= 2,
        "retail floor comes from a LIVE behavioral crawl (>=2 trials), not a fixture replay",
    )

    # The transactability check vectors, keyed by check_id, for all three anchors.
    neg_tx = {
        c["check_id"]: float(c["points"])
        for c in neg["checks"]
        if c["pillar"] == "transactability"
    }
    org_tx = {c.check_id: c.points for c in org.checks if c.pillar == "transactability"}
    com_tx = {c.check_id: c.points for c in com.checks if c.pillar == "transactability"}
    _check(
        set(neg_tx) == set(org_tx) == set(com_tx) and bool(neg_tx),
        f"all three anchors share the transactability check set ({sorted(neg_tx)})",
    )
    for cid in _STATIC_PAYMENT_CHECKS:
        _check(cid in com_tx, f"agent-native payment check {cid!r} is a transactability check")

    # (a) TYPE-INVARIANT FLOOR: the no-rails RETAIL and no-rails API storefronts
    #     land on the IDENTICAL transactability pillar score — the floor does not
    #     depend on WHAT the store sells, only on the (absent) payment rails.
    neg_pillar = neg["pillar_scores"]["transactability"]
    org_pillar = org.pillar_scores["transactability"]
    _check(
        neg_pillar is not None and abs(neg_pillar - org_pillar) < 1e-9,
        f"no-rails transactability floor is storefront-type-invariant "
        f"(retail={neg_pillar}, api={org_pillar})",
    )

    # (b) EARNED THE SAME WAY: the per-check point vector is IDENTICAL across the
    #     two no-rails types — the equal floor is not a coincidence of different
    #     checks summing to the same total.
    for cid in org_tx:
        _check(
            abs(neg_tx[cid] - org_tx[cid]) < 1e-9,
            f"{cid}: identical points across no-rails retail ({neg_tx[cid]}) and "
            f"no-rails api ({org_tx[cid]}) — same floor, earned the same way",
        )

    # (c) ATTRIBUTION: the agent-native payment gap-check earns ZERO on BOTH
    #     no-rails anchors, and every agent-native payment check is credited LESS
    #     than with-rails — the floor is attributably the ABSENCE of agent-native
    #     payment, the static counterpart of the wall the retail shopper hit.
    _check(
        neg_tx["x402_probe"] == 0.0 and org_tx["x402_probe"] == 0.0,
        f"the agent-native payment gap-check earns ZERO on both no-rails anchors "
        f"(retail={neg_tx['x402_probe']}, api={org_tx['x402_probe']}) — capability absent",
    )
    for cid in _STATIC_PAYMENT_CHECKS:
        _check(
            neg_tx[cid] < com_tx[cid] and org_tx[cid] < com_tx[cid],
            f"{cid}: agent-native payment credited LESS on both no-rails anchors "
            f"(retail={neg_tx[cid]}, api={org_tx[cid]}) than with-rails ({com_tx[cid]})",
        )

    # (d) DISCRIMINATES from the with-rails ceiling: the payment gap-check earns
    #     credit there and the ceiling transactability sits well above the floor —
    #     the floor is a real payment-capability signal, not a universal low score.
    _check(
        com_tx["x402_probe"] > 0.0 and com.pillar_scores["transactability"] > neg_pillar,
        f"with-rails ceiling earns the payment gap-check ({com_tx['x402_probe']}) and "
        f"scores transactability {com.pillar_scores['transactability']} >> floor {neg_pillar}",
    )

    # (e) NON-VACUOUS CONTROL: the NON-payment transactability check(s) (mcp_surface)
    #     are identical across ALL THREE anchors, so they do NOT distinguish floor
    #     from ceiling — the discrimination in (c)/(d) is carried by the agent-native
    #     PAYMENT capability, not by some incidental transactability check.
    nonpayment_ids = [cid for cid in com_tx if cid not in _STATIC_PAYMENT_CHECKS]
    _check(
        nonpayment_ids
        and all(
            com_tx[cid] == org_tx[cid] == neg_tx[cid] for cid in nonpayment_ids
        ),
        f"non-payment transactability check(s) {nonpayment_ids} are identical across "
        f"all three anchors — the discrimination is the payment capability, not them",
    )


# ---------------------------------------------------------------------------
# 12. THE WITH-RAILS TRANSACTABILITY CEILING IS A PAYMENT-CAPABILITY SIGNAL, NOT
#     A PREMIUM-CATEGORY ARTIFACT — a KNOCK-OUT counterfactual (the positive-side
#     mirror of test 11's negative-floor type-invariance).
#
#     Test 9 attributes the with-rails/no-rails transactability point-GAP to the
#     agent-native payment checks by DECOMPOSITION (the payment point-diffs sum to
#     the whole gap; non-payment nets zero).  A decomposition of raw-point SUMS,
#     though, (i) could in principle mask OFFSETTING non-payment moves once more
#     than one non-payment check exists (two that cancel would still sum to zero),
#     and (ii) does not speak in the pillar-SCORE units a card reader actually sees.
#     Test 11 proves the no-rails FLOOR is type-invariant, but says nothing about
#     what holds the with-rails CEILING up: if the 87.5 were even partly a
#     premium-category artifact (a "fancy storefront" scoring high for something
#     OTHER than payment rails), neither test 9 nor test 11 would catch it.
#
#     This guard makes the attribution FALSIFIABLE by counterfactual instead of
#     decompositional.  Take the with-rails storefront and KNOCK OUT its agent-native
#     payment capability: replace each ``_STATIC_PAYMENT_CHECKS`` earned-points value
#     with the NO-RAILS storefront's value for the SAME check (an agent that cannot
#     pay earns what the no-rails agent earns), leaving max_points and EVERY
#     non-payment check untouched, then recompute the transactability pillar with
#     scoring's own formula.  The knocked-out score lands EXACTLY on the no-rails
#     floor (18.75): strip the payment capability and the with-rails ceiling is
#     indistinguishable from the no-rails floor, so the ENTIRE ceiling-vs-floor
#     separation is the agent-native payment capability — the ceiling is a payment
#     signal, not a category artifact.  Because we recompute the REPORTED pillar
#     score (not a raw-point sum) and require an EXACT landing, this also closes the
#     offsetting-cancellation hole test 9(b)'s aggregate leaves open: any non-payment
#     check that secretly moved would knock the landing off 18.75.
#
#     Honest counterfactual: max_points and the non-payment check (mcp_surface) are
#     RETAINED through the knock-out, so this simulates the payment capability
#     ABSENT/FAILING (0/partial earned, still counted in the denominator) — the same
#     way a real no-rails agent scores — NOT the capability deleted from the rubric
#     (which would trivially shrink the pillar).  The 18.75/87.5 literals share test
#     9(d)'s re-baseline tripwire contract (a legitimate [LOCAL] canonical re-capture
#     reddens this guard alongside ``test_canonical_replay``).
# ---------------------------------------------------------------------------
def test_with_rails_ceiling_is_payment_capability_not_category_artifact() -> None:
    print("test_with_rails_ceiling_is_payment_capability_not_category_artifact")
    com, com_misses = _static_report(_ANCHOR_DOMAIN)       # with-rails ceiling
    org, org_misses = _static_report("drift-flight.org")   # no-rails floor
    _check(
        not com_misses and not org_misses,
        "both canonical static replays are like-for-like (no replay-miss)",
    )

    com_tx = {c.check_id: c for c in com.checks if c.pillar == "transactability"}
    org_tx = {c.check_id: c for c in org.checks if c.pillar == "transactability"}
    _check(
        set(com_tx) == set(org_tx) and bool(com_tx),
        f"both sides share the transactability check set ({sorted(com_tx)})",
    )
    for cid in _STATIC_PAYMENT_CHECKS:
        _check(cid in com_tx, f"agent-native payment check {cid!r} is a transactability check")

    # The ceiling and floor are the pinned anchors (re-baseline tripwire, test 9(d)).
    ceiling = com.pillar_scores["transactability"]
    floor = org.pillar_scores["transactability"]
    _check(abs(ceiling - 87.5) < 1e-9, f"with-rails ceiling is the pinned 87.5 (got {ceiling})")
    _check(abs(floor - 18.75) < 1e-9, f"no-rails floor is the pinned 18.75 (got {floor})")

    def _scored(check) -> bool:
        return scoring._status_value(check.status) in scoring._SCORED_STATUSES

    # KNOCK-OUT: recompute the with-rails transactability pillar with scoring's OWN
    # formula, but each payment check earns what the NO-RAILS agent earns (capability
    # absent).  max_points and every non-payment check are the with-rails ones,
    # untouched — the honest "capability failed", not "check removed".
    earned = 0.0
    possible = 0.0
    for cid, c in com_tx.items():
        if not _scored(c):
            continue
        possible += c.max_points
        earned += org_tx[cid].points if cid in _STATIC_PAYMENT_CHECKS else c.points
    _check(possible > 0, "the knocked-out transactability pillar still has scored checks")
    knocked = 100.0 * earned / possible

    # THE COUNTERFACTUAL: strip agent-native payment -> the ceiling collapses to the
    # no-rails FLOOR, exactly.  So 100% of the ceiling-vs-floor separation is payment.
    _check(
        abs(knocked - floor) < 1e-9,
        f"knocking out agent-native payment collapses the with-rails ceiling to the "
        f"no-rails floor (knocked={knocked}, floor={floor}) — the ceiling is the "
        f"payment capability, not a category artifact",
    )
    _check(
        abs(knocked - 18.75) < 1e-9,
        f"the collapsed ceiling lands exactly on the pinned 18.75 floor (got {knocked})",
    )

    # DISCRIMINATING: the knock-out is a genuine collapse, not a no-op — the intact
    # ceiling sat far above (a knock-out that barely moved would prove nothing).
    _check(
        ceiling - knocked > 60.0,
        f"the knock-out is a real collapse (87.5 -> {knocked}, drop {ceiling - knocked}), "
        f"not a no-op",
    )

    # NON-VACUOUS: a real non-payment transactability check (mcp_surface) is present
    # and RETAINED through the knock-out — it is NOT what makes the ceiling collapse,
    # so the collapse is attributable to payment despite a live non-payment control.
    nonpayment_ids = [cid for cid in com_tx if cid not in _STATIC_PAYMENT_CHECKS]
    _check(
        nonpayment_ids,
        f"a non-payment transactability check exists as the control ({nonpayment_ids})",
    )
    for cid in nonpayment_ids:
        _check(
            _scored(com_tx[cid]),
            f"the non-payment control {cid!r} is scored and retained through the knock-out",
        )


def main() -> int:
    tests = [
        test_static_payment_prediction_is_behaviorally_corroborated,
        test_calibration_anchor_is_discriminating,
        test_behavioral_corroboration_is_reproducible,
        test_calibration_rests_on_a_shared_static_base,
        test_static_no_payment_prediction_is_behaviorally_corroborated,
        test_negative_anchor_is_a_genuine_reachable_retail_storefront,
        test_negative_corroboration_is_reproducible,
        test_calibration_is_two_sided,
        test_payability_prediction_is_attributably_agent_native_payment,
        test_readout_earner_and_calibration_attribution_cannot_drift,
        test_no_rails_transactability_floor_is_capability_attributable_and_type_invariant,
        test_with_rails_ceiling_is_payment_capability_not_category_artifact,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL: {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
