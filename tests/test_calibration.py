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

HONEST SCOPE (attribution invariant, applied to calibration).
- This is a ONE-DOMAIN anchor on the WITH-RAILS side.  It proves the score's
  positive payability claim is behaviorally real on the domain that makes it; it
  does NOT yet prove the no-rails / retail sides fail behaviorally where the
  score predicts they will.  That symmetric half needs a live behavioral run on
  a no-rails or retail storefront — queued [LOCAL] (the retail-inverse behavioral
  acceptance item), un-runnable in-cloud (no network / no claude CLI for nested
  panels).
- The corroboration is precisely scoped to what the agent DID: it reached the
  machine-payable PATH and completed the FREE-tier transaction (invariant #1 —
  no nonzero-value call was made; both trials' blockers record that a paid call
  needs a funded wallet).  "Agent-native payment REACHABLE", never "a paid
  purchase was executed".
"""

from __future__ import annotations

import json
import os
import sys

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs import scoring  # noqa: E402
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


def main() -> int:
    tests = [
        test_static_payment_prediction_is_behaviorally_corroborated,
        test_calibration_anchor_is_discriminating,
        test_behavioral_corroboration_is_reproducible,
        test_calibration_rests_on_a_shared_static_base,
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
