"""Canonical-pair replay regression guard — the in-cloud proxy for the live re-score.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_canonical_replay.py

The playbook's per-cycle rule is to LIVE-static-re-score the canonical pair
(drift-flight.org vs driftflight.com) every shipping cycle as a REGRESSION
SIGNAL. The cloud loop has no outbound network (STATE.md environment
constraint), so that live re-score cannot run in-cloud — both canonical hosts
return NOT SCORABLE. Cycle 15 built ``FetchContext`` record/replay as the
offline proxy; a [LOCAL] fire (2026-07-23T16:46Z) captured the two committed
fixtures below from ONE live static crawl of each domain (46.1 F / 85.5 B on
rubric v0.7).

This test is the last piece: it replays each committed fixture through the
CURRENT probe + scoring pipeline (no network) and asserts the canonical numbers.
It converts the per-cycle "delta unchanged by construction" PROSE into an
EXECUTABLE guard — the cloud-adapted form of "re-score every shipping cycle".
Any scoring/probe change that would have moved the canonical score now fails a
test instead of shipping silently.

When a rubric version bump LEGITIMATELY moves the canonical score, the fixtures
are re-captured [LOCAL] (``asrs.cli score --record-fixture``) and the EXPECTED
numbers below are updated in the SAME PR — the guard tracks intended change,
it does not forbid it.

No network: every request is served from the fixture's recorded response cache;
a request the fixture does not cover surfaces as a ``replay-miss`` (asserted
absent below — a miss means a probe changed WHAT it fetches, which must fail
loudly rather than silently rescore against a partial fixture).
"""

from __future__ import annotations

import dataclasses
import glob
import json
import os
import sys
import tempfile

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs import scoring  # noqa: E402
from asrs.cli import _run_probes  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.types import CheckResult, Status  # noqa: E402

_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# The canonical numbers pinned on rubric v0.7 (captured LIVE [LOCAL] 16:46Z and
# reproduced byte-faithfully offline). Update these — and re-capture the fixtures
# — together, in the same PR, whenever a version bump legitimately moves a score.
EXPECTED = {
    "drift-flight.org": {
        "overall": 46.1,
        "grade": "F",
        "rubric_version": "0.7",
        "pillars": {
            "access": 100.0,
            "legibility": 36.36363636363637,
            "transactability": 18.75,
            "trust": 60.0,
            "outcome": None,
        },
    },
    "driftflight.com": {
        "overall": 85.5,
        "grade": "B",
        "rubric_version": "0.7",
        "pillars": {
            "access": 100.0,
            "legibility": 90.9090909090909,
            "transactability": 87.5,
            "trust": 60.0,
            "outcome": None,
        },
    },
    # A THIRD real-domain calibration datapoint — a traditional RETAIL storefront
    # (a public book catalog, captured LIVE [LOCAL] 2026-07-24T07:47Z, 41 GET / 0
    # POST). It GENUINELY sells physical goods (the offering layer classifies it
    # physical_good = CLAIMED — see test_offering_canonical) yet exposes NO
    # agent-native payment rail, so it earns 0 transactability. It broadens the
    # regression guard past the single canonical pair to a structurally DIFFERENT
    # site type (a browser-checkout shop, not an API storefront), and it is the
    # capability-lens MIRROR of the +39.4 pair: proof that transactability credit
    # is gated on agent-native CAPABILITY (can an agent pay programmatically?), not
    # on whether the site sells things. Re-capture + update together on a version
    # bump, same contract as the pair above.
    "books.toscrape.com": {
        "overall": 29.5,
        "grade": "F",
        "rubric_version": "0.7",
        "pillars": {
            "access": 100.0,
            "legibility": 18.181818181818183,
            "transactability": 0.0,
            "trust": 33.333333333333336,
            "outcome": None,
        },
    },
    # A FOURTH real-domain calibration datapoint — the ZERO-COMMERCE baseline. Not
    # a storefront at all: a bare documentation page (the IANA example domain) that
    # sells NOTHING (the offering layer classifies it as claiming NO archetype — see
    # test_offering_canonical), captured LIVE [LOCAL] 2026-07-24 via a static $0
    # crawl (41 GET / 0 POST, no secrets). Distinct from books.toscrape.com: the
    # retail shop sells physical goods to humans but not to agents; this site sells
    # to no one. Both sit at the transactability FLOOR (0), but this one earns it
    # from the total absence of any commerce surface — the honest bottom of the
    # scale a benchmark needs so the with-rails delta is measured against a real
    # low anchor, not just other storefronts. Re-capture + update together on a
    # version bump, same contract as the domains above.
    "example.com": {
        "overall": 22.5,
        "grade": "F",
        "rubric_version": "0.7",
        "pillars": {
            "access": 100.0,
            "legibility": 0.0,
            "transactability": 0.0,
            "trust": 20.0,
            "outcome": None,
        },
    },
}
EXPECTED_DELTA = 39.4  # driftflight.com (rails) - drift-flight.org (no rails)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _score_fixture(domain: str):
    """Replay ``fixtures/canonical/<domain>.json`` through the real pipeline.

    Returns ``(report, replay_misses)`` where ``replay_misses`` is the list of
    cache keys whose recorded/served result carries a ``replay-miss`` error —
    i.e. probe requests the fixture does not cover.
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


def _assert_domain(domain: str) -> None:
    exp = EXPECTED[domain]
    report, misses = _score_fixture(domain)

    # (a) The fixture must cover every probe request — a miss means a probe
    # changed WHAT it fetches, so the score is no longer a like-for-like re-score.
    _check(not misses, f"{domain}: no replay-miss (fixture covers every probe request)")

    # (b) The headline number, grade, and rubric version are the pinned canonical values.
    _check(
        report.overall_score == exp["overall"],
        f"{domain}: overall_score == {exp['overall']} (got {report.overall_score})",
    )
    _check(
        report.grade == exp["grade"],
        f"{domain}: grade == {exp['grade']!r} (got {report.grade!r})",
    )
    _check(
        report.rubric_version == exp["rubric_version"],
        f"{domain}: rubric_version == {exp['rubric_version']!r} "
        f"(got {report.rubric_version!r})",
    )
    _check(report.scored is True, f"{domain}: report is scored (not NOT-SCORABLE)")

    # (c) Pillar scores unchanged — a finer regression signal than the roll-up:
    # a probe change could move a pillar while leaving the rounded overall equal.
    for pillar, want in exp["pillars"].items():
        got = report.pillar_scores.get(pillar)
        if want is None:
            _check(got is None, f"{domain}: pillar {pillar} is None (no result)")
        else:
            _check(
                got is not None and abs(got - want) < 1e-6,
                f"{domain}: pillar {pillar} == {want} (got {got})",
            )


# ---------------------------------------------------------------------------
# 1. Each canonical fixture replays to its pinned score on rubric v0.7.
# ---------------------------------------------------------------------------
def test_canonical_org_replays_46_1() -> None:
    print("test_canonical_org_replays_46_1")
    _assert_domain("drift-flight.org")


def test_canonical_com_replays_85_5() -> None:
    print("test_canonical_com_replays_85_5")
    _assert_domain("driftflight.com")


# ---------------------------------------------------------------------------
# 2. The capability DELTA (the number the benchmark exists to defend) is +39.4:
#    the with-rails side wins by the recorded margin, pinned offline. If a rigor
#    change narrows or widens this, THIS test is the tripwire that forces the
#    LOG entry to explain it in capability terms (or not ship).
# ---------------------------------------------------------------------------
def test_canonical_delta_is_39_4() -> None:
    print("test_canonical_delta_is_39_4")
    org, org_misses = _score_fixture("drift-flight.org")
    com, com_misses = _score_fixture("driftflight.com")
    _check(not org_misses and not com_misses, "no replay-miss on either domain")
    delta = round(com.overall_score - org.overall_score, 1)
    _check(
        delta == EXPECTED_DELTA,
        f"canonical delta (.com - .org) == {EXPECTED_DELTA} (got {delta})",
    )


# ---------------------------------------------------------------------------
# 3. The delta is defended IN CAPABILITY TERMS, not merely as a number. The
#    playbook's capability lens requires every canonical re-score to explain
#    the delta by what agent-native rails let an agent actually DO — and the
#    single largest driver of this +39.4 is the ability to PAY PROGRAMMATICALLY
#    (transactability, weight 0.30 — the heaviest observed pillar — contributes
#    ~26 of the 39.4 weighted points). Guards 1–2 pin the numbers; this pins the
#    CAPABILITY behind them as an executable fact, so the LOG's "with-rails wins
#    because it delivers agent-native payment" stops being unverifiable prose:
#    the with-rails fixture delivers agent-native payment (x402 live), the
#    no-rails fixture does not. A probe change that flipped WHICH capability
#    fires while arithmetic happened to preserve a pillar total would slip past
#    the number-only guards above but fail HERE. Worded by capability, never by
#    vendor — it asks "is agent-native payment present?", not "is this domain X?".
# ---------------------------------------------------------------------------
def _by_id(report, check_id):
    for c in report.checks:
        if c.check_id == check_id:
            return c
    raise AssertionError(f"check {check_id!r} absent from {report.domain} report")


def test_canonical_delta_is_agent_native_payment() -> None:
    print("test_canonical_delta_is_agent_native_payment")
    com, com_misses = _score_fixture("driftflight.com")   # with agent-native rails
    org, org_misses = _score_fixture("drift-flight.org")  # no agent-native rails
    _check(not com_misses and not org_misses, "no replay-miss on either domain")

    # With-rails side: agent-native programmatic payment is PRESENT.
    _check(
        _by_id(com, "x402_probe").status is Status.PASS,
        "driftflight.com: x402_probe PASSES — agent-native payment reachable",
    )
    _check(
        _by_id(com, "self_serve_payg").evidence.get("x402_live") is True,
        "driftflight.com: self_serve_payg records x402_live=True",
    )

    # No-rails side: agent-native programmatic payment is ABSENT (the capability
    # gap, not an environment failure — the fixture is a clean live crawl).
    _check(
        _by_id(org, "x402_probe").status is not Status.PASS,
        "drift-flight.org: x402_probe does NOT pass — no agent-native payment",
    )
    _check(
        _by_id(org, "self_serve_payg").evidence.get("x402_live") is False,
        "drift-flight.org: self_serve_payg records x402_live=False",
    )

    # The capability gap manifests as the transactability pillar gap — pin that
    # the with-rails side strictly dominates by the recorded margin, so a future
    # probe change can't quietly rebalance the pillar while the overall holds.
    gap = round(com.pillar_scores["transactability"] - org.pillar_scores["transactability"], 2)
    _check(
        gap == 68.75,
        f"transactability capability gap (.com - .org) == 68.75 (got {gap})",
    )


# ---------------------------------------------------------------------------
# 4. Domain-relabeling INVARIANCE — the executable form of the vendor-neutrality
#    invariant ("checks worded by capability, never by vendor; no special-casing
#    any domain, favorable or hostile"). Guards 1–3 pin that the recorded EVIDENCE
#    produces the canonical numbers; this pins that the numbers depend ONLY on the
#    evidence, never on the storefront's IDENTITY. We relabel a canonical fixture's
#    host — in the request keys AND every response byte (URLs, final_url, headers,
#    bodies) — to a neutral placeholder, then re-score. A capability-only scorer
#    MUST return the identical overall/grade/pillars/per-check-status: renaming the
#    shop changes nothing. If any probe or scoring branch keyed on the literal
#    domain (a favorable OR hostile special-case), the relabeled run would diverge
#    and fail HERE — the first executable test of vendor-neutrality, complementing
#    the capability-delta guard above.
#
#    Faithfulness: the relabel is a whole-fixture string substitution (so a probe
#    that follows a body-embedded absolute URL still hits the rewritten cache — no
#    replay-miss), written to a temp file and replayed through the REAL
#    ``FetchContext.from_fixture`` → ``_run_probes`` → ``scoring.score`` path, the
#    same pipeline guards 1–3 use. The neutral host is a different LENGTH than the
#    original, so the invariance is not a same-length coincidence.
# ---------------------------------------------------------------------------
_NEUTRAL_HOST = "neutral-storefront.test"  # reserved .test TLD; not a real domain


def _score_relabeled(domain: str, new_host: str):
    """Replay ``<domain>.json`` with its host relabeled to ``new_host`` everywhere.

    Returns ``(report, replay_misses)``. The substitution rewrites request keys
    and response bytes together, so evidence is byte-identical up to the host
    label; a capability-only scorer must reproduce the un-relabeled score.
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    relabeled = raw.replace(domain, new_host)
    _check(
        domain not in relabeled,
        f"{domain}: every occurrence of the original host was relabeled",
    )
    tmp = tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(relabeled)
        tmp.close()
        ctx = FetchContext.from_fixture(tmp.name)
        checks = _run_probes(ctx)
        report = scoring.score(checks, scoring.load_rubric(None), new_host)
    finally:
        os.unlink(tmp.name)
    misses = [
        key for key, res in ctx._cache.items()
        if res.error and "replay-miss" in res.error
    ]
    return report, misses


def _assert_relabel_invariant(domain: str) -> None:
    exp = EXPECTED[domain]
    base, base_misses = _score_fixture(domain)
    relab, relab_misses = _score_relabeled(domain, _NEUTRAL_HOST)

    _check(
        not base_misses and not relab_misses,
        f"{domain}: no replay-miss before or after relabeling",
    )
    # Headline number and grade are identical — and equal to the pinned canonical
    # value, so this also re-affirms guards 1–2 through the relabeled path.
    _check(
        relab.overall_score == base.overall_score == exp["overall"],
        f"{domain}: overall_score invariant under relabel "
        f"(base {base.overall_score}, relabel {relab.overall_score}, pinned {exp['overall']})",
    )
    _check(
        relab.grade == base.grade == exp["grade"],
        f"{domain}: grade invariant under relabel "
        f"(base {base.grade!r}, relabel {relab.grade!r})",
    )
    # Every pillar is bit-for-bit identical — a finer signal than the roll-up.
    for pillar in exp["pillars"]:
        b = base.pillar_scores.get(pillar)
        r = relab.pillar_scores.get(pillar)
        _check(
            b == r,
            f"{domain}: pillar {pillar} invariant under relabel (base {b}, relabel {r})",
        )
    # Every check's STATUS is unchanged — no probe flipped on the host label.
    base_status = {c.check_id: c.status for c in base.checks}
    relab_status = {c.check_id: c.status for c in relab.checks}
    status_diffs = {
        k: (base_status[k].name, relab_status[k].name if k in relab_status else None)
        for k in set(base_status) | set(relab_status)
        if base_status.get(k) != relab_status.get(k)
    }
    _check(
        not status_diffs,
        f"{domain}: every check status invariant under relabel (diffs: {status_diffs})",
    )


def test_relabel_invariance_org() -> None:
    print("test_relabel_invariance_org")
    _assert_relabel_invariant("drift-flight.org")


def test_relabel_invariance_com() -> None:
    print("test_relabel_invariance_com")
    _assert_relabel_invariant("driftflight.com")


def test_relabeled_delta_still_39_4() -> None:
    """The capability delta is a property of the EVIDENCE, not the two famous names.

    Relabel each side to a DISTINCT neutral host and confirm the with-rails side
    still beats the no-rails side by exactly +39.4. Two anonymous storefronts with
    the same recorded capabilities reproduce the delta — it cannot be an artifact
    of the specific domains ``drift-flight.org`` / ``driftflight.com``.
    """
    print("test_relabeled_delta_still_39_4")
    com, com_misses = _score_relabeled("driftflight.com", "rails-anon.test")
    org, org_misses = _score_relabeled("drift-flight.org", "norails-anon.test")
    _check(not com_misses and not org_misses, "no replay-miss on either relabeled domain")
    delta = round(com.overall_score - org.overall_score, 1)
    _check(
        delta == EXPECTED_DELTA,
        f"relabeled canonical delta == {EXPECTED_DELTA} (got {delta})",
    )


# ---------------------------------------------------------------------------
# 5. The delta is EARNED, not an attribution artifact — the executable form of
#    invariant #4 (attribution honesty) applied to the canonical delta. Guards
#    1–4 pin the numbers, the payment capability, and vendor-neutrality. This
#    guard pins the TRUTH-track calibration question ("does the score reflect a
#    real capability gap, or an accounting one?"): a delta can be inflated two
#    dishonest ways that leave the headline numbers looking fine —
#      (i) DIFFERENTIAL OBSERVABILITY — the no-rails side is scored against a
#          DIFFERENT (smaller) set of checks than the with-rails side, so the
#          two overalls are not like-for-like; or
#      (ii) MIS-ATTRIBUTED ABSENCE — a capability the no-rails side genuinely
#           lacks is recorded as CANT_TEST (absence-of-evidence, EXCLUDED from
#           the denominator) on ONE side but FAIL (evidence-of-absence, scored
#           0 IN the denominator) on the other, silently penalizing one side for
#           a gap the other is excused for.
#    Neither can happen here, and this proves it from the committed evidence:
#      (a) FULL OBSERVABILITY — no static check on EITHER canonical domain is
#          CANT_TEST or NA (both fixtures are clean live crawls, HTTP 200), so
#          every recorded FAIL is genuine evidence-of-absence in the denominator,
#          never a gap excused as un-observable.
#      (b) LIKE-FOR-LIKE DENOMINATOR — both domains are scored over the IDENTICAL
#          set of scored check_ids, so +39.4 compares the same checks on both
#          sides, not one side over fewer checks.
#      (c) CHECK-BY-CHECK DOMINANCE, NO INVERSION — at every matched check the
#          with-rails side's capability rank (PASS>PARTIAL>FAIL) is >= the
#          no-rails side's, and STRICTLY greater at >=1 check. The advantage is a
#          capability SUPERSET at matched, fully-observed checks — not a single
#          pillar masking a regression elsewhere, and not a tie the rounding
#          inflated.
#    A probe that mis-attributed the no-rails side's missing payment as CANT_TEST
#    (excusing it) instead of FAIL would still leave the pillar arithmetic looking
#    plausible but would FAIL (a) here; a check that inverted (no-rails beating
#    with-rails somewhere) would slip the aggregate-only guards but FAIL (c).
#    Worded by capability throughout — it asks "was this capability observed, and
#    which side ranks higher?", never "is this domain X?".
# ---------------------------------------------------------------------------
# Capability ranking for a like-for-like comparison. NA / CANT_TEST are NOT in
# this map on purpose: they are "unobserved" (excluded from scoring), and (a)
# below asserts they never occur on the canonical pair — so reaching them here
# is itself a failure, not a rank.
_CAP_RANK = {Status.PASS: 2, Status.PARTIAL: 1, Status.FAIL: 0}
_UNOBSERVED = {Status.NA, Status.CANT_TEST}


def test_canonical_delta_is_earned_dominance() -> None:
    print("test_canonical_delta_is_earned_dominance")
    com, com_misses = _score_fixture("driftflight.com")   # with agent-native rails
    org, org_misses = _score_fixture("drift-flight.org")  # no agent-native rails
    _check(not com_misses and not org_misses, "no replay-miss on either domain")

    com_status = {c.check_id: c.status for c in com.checks}
    org_status = {c.check_id: c.status for c in org.checks}

    # (a) Full observability — nothing on either side is excused as un-observable,
    # so every recorded FAIL is scored evidence-of-absence, not excluded absence.
    com_unobserved = {k for k, s in com_status.items() if s in _UNOBSERVED}
    org_unobserved = {k for k, s in org_status.items() if s in _UNOBSERVED}
    _check(
        not com_unobserved and not org_unobserved,
        "no canonical check is CANT_TEST/NA on either side "
        f"(com {com_unobserved}, org {org_unobserved}) — the delta rests on "
        "observed evidence, not differential observability",
    )

    # (b) Like-for-like denominator — both sides scored over the SAME check_ids.
    _check(
        set(com_status) == set(org_status),
        "both canonical domains are scored over the identical check_id set "
        f"(com-only {set(com_status) - set(org_status)}, "
        f"org-only {set(org_status) - set(com_status)})",
    )

    # (c) Check-by-check dominance with no inversion, strict at >=1 check.
    inversions = {}
    strict_wins = []
    for cid in set(com_status) & set(org_status):
        rc, ro = _CAP_RANK[com_status[cid]], _CAP_RANK[org_status[cid]]
        if rc < ro:
            inversions[cid] = (org_status[cid].name, com_status[cid].name)  # org beats com
        elif rc > ro:
            strict_wins.append(cid)
    _check(
        not inversions,
        f"with-rails side dominates at every matched check — no inversion "
        f"(checks where no-rails outranks with-rails: {inversions})",
    )
    _check(
        len(strict_wins) >= 1,
        "the delta is driven by matched-check capability gaps — with-rails "
        f"strictly outranks no-rails at >=1 check (strict wins: {sorted(strict_wins)})",
    )


# ---------------------------------------------------------------------------
# 6. THIRD-DOMAIN CALIBRATION — the guard beyond the pair. Guards 1–5 pin the two
#    canonical storefronts; a benchmark needs more than one pair to claim it
#    measures a real, transferable capability. This replays a committed fixture
#    for a traditional RETAIL storefront (a public book catalog) through the same
#    real pipeline and pins its score on rubric v0.7 — a structurally different
#    site type (browser-checkout shop, not an API storefront) in the regression
#    signal, so a probe/scoring change that quietly moved a real retail site's
#    number fails here too, not only on the two API storefronts.
# ---------------------------------------------------------------------------
def test_retail_storefront_replays_29_5() -> None:
    print("test_retail_storefront_replays_29_5")
    _assert_domain("books.toscrape.com")


# ---------------------------------------------------------------------------
# 7. The MIRROR capability guard — transactability credit is gated on agent-native
#    CAPABILITY, not on whether a site sells things. Guard 3 pins that the
#    with-rails canonical side EARNS agent-native payment (x402 live). This pins
#    the complement, on a real domain that would break a store-type heuristic: a
#    genuine retail storefront (it sells physical books — the offering layer
#    classifies it physical_good = CLAIMED) that exposes NO agent-native payment
#    rail earns EXACTLY 0 transactability. A probe that credited "looks like a
#    shop" (product pages, prices, add-to-cart) as programmatic payability would
#    inflate this site and slip guards 1–6 (the overall could still round plausibly)
#    but FAIL here. The attribution-honesty flip side of the +39.4 delta: this
#    retail shop — the site that most obviously "sells things" — is the
#    transactability FLOOR, earning EXACTLY 0 and scoring even LOWER than the
#    no-rails API storefront (which retains a partial self-serve pay-as-you-go
#    signal). Both are scored over the IDENTICAL check set, so the gap is a
#    capability fact, not a denominator artifact: a browser-checkout shop offers
#    an agent nothing to pay with programmatically. Worded by capability
#    throughout — it asks "is agent-native payment present?", never "is this
#    domain X?".
# ---------------------------------------------------------------------------
def test_retail_storefront_earns_no_agent_native_payment() -> None:
    print("test_retail_storefront_earns_no_agent_native_payment")
    retail, retail_misses = _score_fixture("books.toscrape.com")
    org, org_misses = _score_fixture("drift-flight.org")  # no-rails API storefront
    _check(not retail_misses and not org_misses, "no replay-miss on either domain")

    # No agent-native programmatic payment is reachable — x402 does not pass and
    # the pay-as-you-go check records no live x402 payment (evidence-of-absence).
    _check(
        _by_id(retail, "x402_probe").status is not Status.PASS,
        "books.toscrape.com: x402_probe does NOT pass — no agent-native payment",
    )
    _check(
        _by_id(retail, "self_serve_payg").evidence.get("x402_live") is not True,
        "books.toscrape.com: self_serve_payg records no live x402 payment",
    )

    # No probe awarded live programmatic-commerce credit anywhere (no validated
    # commerce-protocol manifest, no x402-live label) — a genuine shop is NOT
    # mistaken for an agent-native-payable one.
    retail_ids = {c.check_id for c in retail.checks}
    _check(
        not any("commerce-protocol" in cid or cid == "x402-live" for cid in retail_ids),
        "books.toscrape.com: no commerce-protocol-*/x402-live credit awarded to a "
        "browser-checkout retail shop",
    )

    # The capability gap manifests as an EXACTLY-zero transactability pillar — a
    # real storefront that sells things but cannot be paid programmatically.
    _check(
        retail.pillar_scores["transactability"] == 0.0,
        f"books.toscrape.com: transactability == 0.0 "
        f"(got {retail.pillar_scores['transactability']})",
    )

    # Attribution-honesty flip side of the delta: the retail shop and the no-rails
    # API storefront are scored over the IDENTICAL check set, so the comparison is
    # like-for-like — yet the shop, the site that most obviously "sells things",
    # scores STRICTLY LOWER on transactability (it is the floor: 0 vs the .org's
    # residual partial self-serve signal). The pillar keys on agent-native payment
    # presence, not on whether the site is a store.
    _check(
        {c.check_id for c in retail.checks} == {c.check_id for c in org.checks},
        "retail shop and no-rails API storefront scored over the identical check "
        "set (like-for-like transactability comparison)",
    )
    _check(
        retail.pillar_scores["transactability"] < org.pillar_scores["transactability"],
        "books.toscrape.com is the transactability floor — scores strictly lower "
        f"than the no-rails API storefront ({retail.pillar_scores['transactability']} "
        f"< {org.pillar_scores['transactability']}); selling things != agent-native payable",
    )


# ---------------------------------------------------------------------------
# 8. Vendor-neutrality extended to the third domain — the relabel-invariance
#    tripwire (guard 4) applied to the retail storefront, so "no special-casing
#    any domain, favorable or hostile" is enforced on a real site OUTSIDE the
#    famous canonical pair. Relabeling the shop's host everywhere reproduces the
#    identical 29.5 / F / pillars / per-check statuses: its score depends on the
#    recorded capability evidence, not on its identity.
# ---------------------------------------------------------------------------
def test_relabel_invariance_retail() -> None:
    print("test_relabel_invariance_retail")
    _assert_relabel_invariant("books.toscrape.com")


# ---------------------------------------------------------------------------
# 9. ZERO-COMMERCE BASELINE — a fourth real domain, the honest bottom anchor.
#    Guards 1–8 pin two API storefronts and a retail shop; all three are places
#    that sell something. A benchmark also needs the floor: a bare site that sells
#    NOTHING, so the with-rails delta is measured against a real low anchor, not
#    only against other storefronts. This replays a committed fixture for a plain
#    documentation page (the IANA example domain) and pins its score on rubric
#    v0.7 — a structurally different, non-commercial site in the regression signal.
# ---------------------------------------------------------------------------
def test_nonstorefront_replays_22_5() -> None:
    print("test_nonstorefront_replays_22_5")
    _assert_domain("example.com")


# ---------------------------------------------------------------------------
# 10. The MIRROR capability guard on the zero-commerce baseline — a bare site is
#     not spuriously credited with payment capability it never had. Guard 3 pins
#     the with-rails side EARNS agent-native payment; guard 7 pins a real retail
#     shop earns 0. This pins the extreme case: a site with no storefront at all
#     earns EXACTLY 0 transactability and NO payment credit of any kind. A probe
#     that hallucinated an agent-native rail from a bare page (e.g. mis-reading a
#     generic 402/401 or a stray link as a payment handshake) would inflate this
#     site and slip guards 1–9 but FAIL here. Attribution-honesty detail worth
#     pinning: the pay-as-you-go check is CANT_TEST (the bare site has no purchase
#     path to evaluate — honestly EXCLUDED, never penalized), yet transactability
#     is still 0 because the agent-native-payment probe FAILs on recorded
#     evidence-of-absence — absence excused where unobservable, scored where
#     observed. Worded by capability throughout.
# ---------------------------------------------------------------------------
def test_nonstorefront_earns_no_agent_native_payment() -> None:
    print("test_nonstorefront_earns_no_agent_native_payment")
    bare, bare_misses = _score_fixture("example.com")
    _check(not bare_misses, "example.com: no replay-miss")

    # No agent-native programmatic payment is reachable.
    _check(
        _by_id(bare, "x402_probe").status is not Status.PASS,
        "example.com: x402_probe does NOT pass — no agent-native payment",
    )
    _check(
        _by_id(bare, "self_serve_payg").evidence.get("x402_live") is not True,
        "example.com: self_serve_payg records no live x402 payment",
    )

    # No probe awarded live programmatic-commerce credit anywhere — a bare page is
    # not mistaken for an agent-native-payable storefront.
    bare_ids = {c.check_id for c in bare.checks}
    _check(
        not any("commerce-protocol" in cid or cid == "x402-live" for cid in bare_ids),
        "example.com: no commerce-protocol-*/x402-live credit awarded to a "
        "non-commercial page",
    )

    # The capability floor manifests as an EXACTLY-zero transactability pillar.
    _check(
        bare.pillar_scores["transactability"] == 0.0,
        f"example.com: transactability == 0.0 "
        f"(got {bare.pillar_scores['transactability']})",
    )


# ---------------------------------------------------------------------------
# 11. Vendor-neutrality extended to the fourth domain — the relabel-invariance
#     tripwire (guard 4) applied to the zero-commerce baseline, so "no
#     special-casing any domain, favorable or hostile" is enforced on a
#     non-storefront too. Relabeling the host everywhere reproduces the identical
#     22.5 / F / pillars / per-check statuses: even the floor score depends on the
#     recorded evidence, not on the domain's identity.
# ---------------------------------------------------------------------------
def test_relabel_invariance_nonstorefront() -> None:
    print("test_relabel_invariance_nonstorefront")
    _assert_relabel_invariant("example.com")


# ---------------------------------------------------------------------------
# 12. POPULATION ORDERING — the benchmark's central claim, made executable across
#     the whole committed population. Guards 1–11 pin each domain's score
#     individually and compare the pair / retail / baseline in isolation; none
#     asserts the RELATIONSHIP the benchmark exists to produce. This guard pins it:
#     the overall score is strictly MONOTONE along the agent-native-commerce
#     capability spectrum — with-rails API storefront > no-rails API storefront >
#     human-only retail shop > zero-commerce baseline. It reads the scores from the
#     LIVE replay pipeline (never from the pinned EXPECTED constants), so a scoring/
#     probe change that reordered any pair — e.g. crediting a browser-checkout shop
#     above an API storefront — fails HERE even if a maintainer updated the
#     exact-number expectations to match the bug. The individual-number guards track
#     intended change; this ordering guard tracks the intended CLAIM, which must
#     survive any legitimate re-capture or version bump. Worded by capability tier,
#     never by vendor: the sites are ranked by what an agent can DO with them, not
#     by their identity — the same four fixture keys guards 1–11 already use.
# ---------------------------------------------------------------------------
# Ordered most- to least-capable for agent-native commerce, by recorded evidence.
_CAPABILITY_SPECTRUM = [
    ("driftflight.com", "with-rails API storefront (agent-native payment present)"),
    ("drift-flight.org", "no-rails API storefront (API legible, no agent-native payment)"),
    ("books.toscrape.com", "human-only retail shop (sells goods, not agent-payable)"),
    ("example.com", "zero-commerce baseline (sells nothing)"),
]


def test_population_overall_tracks_capability_ordering() -> None:
    print("test_population_overall_tracks_capability_ordering")
    scored = []
    for dom, tier in _CAPABILITY_SPECTRUM:
        rep, misses = _score_fixture(dom)
        _check(not misses, f"{dom}: no replay-miss")
        scored.append((dom, tier, rep.overall_score))

    # The overall score STRICTLY decreases at every step down the spectrum — the
    # benchmark ranks the population by agent-native capability, not by chance.
    for (hd, ht, hs), (ld, lt, ls) in zip(scored, scored[1:]):
        _check(
            hs > ls,
            f"overall strictly decreases: {hd} ({ht}) {hs} > {ld} ({lt}) {ls}",
        )

    # Non-vacuous: four DISTINCT domains spanning a real range (top >> floor), so
    # the chain above is an ordering over a genuine spread, not a near-tie artifact.
    _check(len({d for d, _, _ in scored}) == 4, "four distinct domains in the spectrum")
    _check(
        scored[0][2] - scored[-1][2] >= 40.0,
        f"the spectrum spans a real range (top {scored[0][2]} − floor "
        f"{scored[-1][2]} = {round(scored[0][2] - scored[-1][2], 1)} >= 40.0)",
    )


# ---------------------------------------------------------------------------
# 13. THE ORDERING IS NOT A TRANSACTABILITY ARTIFACT — the honest decomposition
#     behind guard 12. Transactability (agent-native payment) is the heaviest,
#     benchmark-defining pillar, so a critic could dismiss the whole ordering as
#     "you just measured who takes x402". This guard refutes that from the recorded
#     evidence: transactability is non-increasing along the same spectrum AND the
#     with-rails side strictly tops it (payment capability is what earns the #1
#     slot) — but the two payment-FLOOR sites (retail shop, bare page) TIE at 0
#     transactability, yet the overall order between them is still preserved, driven
#     by OTHER observed capability (the shop's product legibility over the bare
#     page's none). So the benchmark separates two equally-unpayable sites by a
#     different, real capability, in the sensible direction — the ordering is a
#     multi-capability judgement, not a single-pillar proxy. Read from the live
#     pipeline; worded by capability throughout.
# ---------------------------------------------------------------------------
def test_population_ordering_is_not_a_transactability_artifact() -> None:
    print("test_population_ordering_is_not_a_transactability_artifact")
    tx, ov, leg = {}, {}, {}
    for dom, _tier in _CAPABILITY_SPECTRUM:
        rep, misses = _score_fixture(dom)
        _check(not misses, f"{dom}: no replay-miss")
        tx[dom] = rep.pillar_scores["transactability"]
        ov[dom] = rep.overall_score
        leg[dom] = rep.pillar_scores["legibility"]
    order = [d for d, _ in _CAPABILITY_SPECTRUM]

    # (a) transactability is non-increasing along the same capability ordering.
    for hi, lo in zip(order, order[1:]):
        _check(
            tx[hi] >= tx[lo],
            f"transactability non-increasing: {hi} {tx[hi]} >= {lo} {tx[lo]}",
        )

    # (b) agent-native payment is what earns the top slot: the with-rails side's
    # transactability STRICTLY exceeds every other domain's.
    top = order[0]
    for other in order[1:]:
        _check(
            tx[top] > tx[other],
            f"{top} transactability strictly tops {other} ({tx[top]} > {tx[other]})",
        )

    # (c) the two payment-floor sites tie at 0 transactability, yet the overall
    # order between them is preserved — so the tail ranking is NOT a transactability
    # artifact. It is driven by OTHER observed capability: the retail shop's product
    # legibility strictly exceeds the bare page's, in the sensible direction.
    retail, bare = order[2], order[3]
    _check(
        tx[retail] == 0.0 and tx[bare] == 0.0,
        f"both floor sites are payment-floor (0 transactability: "
        f"{retail} {tx[retail]}, {bare} {tx[bare]})",
    )
    _check(
        ov[retail] > ov[bare],
        f"tail overall order preserved despite equal transactability: "
        f"{retail} {ov[retail]} > {bare} {ov[bare]}",
    )
    _check(
        leg[retail] > leg[bare],
        f"the tail is separated by a DIFFERENT capability — legibility: "
        f"{retail} {leg[retail]:.2f} > {bare} {leg[bare]:.2f}",
    )


# ---------------------------------------------------------------------------
# 14. JOINT POPULATION RELABEL-INVARIANCE — the population ORDERING (guard 12),
#     not just each score in isolation (guards 4/6/8/11), is a property of the
#     recorded capability EVIDENCE, never of the four hosts' identities. Guard 12
#     pins the strict capability ordering on the REAL hosts; guards 4/6/8/11 pin
#     each domain's score under relabel ONE AT A TIME. Neither pins the
#     RELATIONSHIP the benchmark exists to produce under a SIMULTANEOUS relabel of
#     the whole population. This guard relabels all four fixtures at once to
#     DISTINCT neutral hosts and asserts the benchmark's central claim — the strict
#     monotone capability ordering — survives, and each relabeled overall still
#     equals its pinned value (tying the population claim back to guards 1/9/12).
#
#     Non-vacuous BEYOND the per-domain guards: the neutral hosts are assigned so
#     their LEXICOGRAPHIC order is the REVERSE of the capability order — the most
#     agent-capable storefront gets the alphabetically-LAST host, the zero-commerce
#     floor the FIRST. A scorer that secretly ranked the population by host string
#     (a "sort the domains and assign tiers" bug) rather than by evidence would
#     REVERSE the ordering under this relabel and FAIL here — yet every per-domain
#     guard (a single fixed host, no cross-host comparison) would still pass, since
#     none of them ever compares one host against another. Worded by capability
#     tier, never by vendor: the same four fixture keys guards 1–12 already use.
# ---------------------------------------------------------------------------
# (domain, capability tier, neutral host) in capability-DESCENDING order. Each
# neutral host is the per-domain guards' known-miss-free ``neutral-storefront.test``
# with ONLY its leading letter varied, so the four are DISTINCT yet each behaves
# identically to a host the per-domain relabel guards already prove byte-clean on
# every fixture (same length + hyphen structure — the whole-fixture string
# substitution is sensitive to both: a shorter or extra-hyphenated host rewrites a
# subdomain surface reference into an un-recorded fetch, a replay-miss artifact of
# the relabel, not a scoring change). The leading letters are host-DESCENDING
# (z > s > g > a) as capability descends, so the hosts' lexical order is the
# REVERSE of capability (the floor's host sorts FIRST, the top's LAST) — the
# property that makes this guard catch a host-string sorter the per-domain guards
# cannot.
_JOINT_RELABEL = [
    ("driftflight.com", "with-rails API storefront (agent-native payment present)", "zeutral-storefront.test"),
    ("drift-flight.org", "no-rails API storefront (API legible, no agent-native payment)", "seutral-storefront.test"),
    ("books.toscrape.com", "human-only retail shop (sells goods, not agent-payable)", "geutral-storefront.test"),
    ("example.com", "zero-commerce baseline (sells nothing)", "aeutral-storefront.test"),
]


def test_population_ordering_is_identity_invariant() -> None:
    print("test_population_ordering_is_identity_invariant")
    scored = []
    for dom, tier, host in _JOINT_RELABEL:
        rep, misses = _score_relabeled(dom, host)
        _check(not misses, f"{dom}->{host}: no replay-miss under relabel")
        # Each relabeled score equals the pinned canonical value — the population
        # claim rests on the same numbers guards 1/9/12 pin individually.
        _check(
            rep.overall_score == EXPECTED[dom]["overall"],
            f"{dom} relabeled to {host}: overall == {EXPECTED[dom]['overall']} "
            f"(got {rep.overall_score})",
        )
        scored.append((dom, host, tier, rep.overall_score))

    # The benchmark's central claim — the strict monotone capability ordering
    # (guard 12) — survives the SIMULTANEOUS relabel of the whole population.
    for (hd, hh, ht, hs), (ld, lh, lt, ls) in zip(scored, scored[1:]):
        _check(
            hs > ls,
            f"ordering identity-invariant: {hd}->{hh} ({ht}) {hs} > "
            f"{ld}->{lh} ({lt}) {ls}",
        )

    # Non-vacuous vs the per-domain guards: confirm the neutral hosts really are
    # assigned in the REVERSE lexicographic order of capability (capability-
    # descending == host-ascending), so a host-string sorter would reorder the
    # population here even though it slips every single-host per-domain guard.
    hosts_in_cap_order = [h for _, h, _, _ in scored]
    _check(
        hosts_in_cap_order == sorted(hosts_in_cap_order, reverse=True),
        f"neutral hosts assigned reverse-lexical to capability (a host-string "
        f"sorter would reorder the population): {hosts_in_cap_order}",
    )
    # Four distinct anonymous hosts, none carrying a canonical domain name.
    canon_names = {d for d, _, _, _ in scored}
    _check(
        len(set(hosts_in_cap_order)) == 4
        and not any(cn in h for h in hosts_in_cap_order for cn in canon_names),
        "four distinct neutral hosts, none carrying a canonical domain name",
    )


# ---------------------------------------------------------------------------
# 15. WEIGHT-ROBUSTNESS — the with-rails advantage is NOT an artifact of the
#     pillar weight vector. The single most common critique of a rails-favouring
#     benchmark is "you rigged the weights so the agent-native rail wins." Guards
#     3/8 refute the EVIDENCE objection (the delta is earned check-by-check); this
#     refutes the AGGREGATION objection. On the recorded evidence the with-rails
#     side DOMINATES the no-rails side PILLAR-BY-PILLAR: it is >= on every observed
#     pillar (strictly > on the two benchmark-defining pillars, legibility and
#     transactability; tied on access and trust). Both sides expose the IDENTICAL
#     applicable-pillar set (like-for-like denominator at the pillar layer — the
#     aggregation-level analogue of guard 8's like-for-like checks), and NEITHER
#     side hits a grade cap, so each overall equals a pure renormalized weighted
#     mean of those pillars. Pillar-wise dominance over a shared applicable set
#     therefore makes the sign of (with-rails − no-rails) INVARIANT to the weight
#     vector: under ANY non-negative pillar weighting the with-rails mean is >= the
#     no-rails mean, and strictly > whenever the weighting places positive weight on
#     a strictly-dominated pillar. This guard demonstrates it across a family of
#     ADVERSARIAL weightings — including the two extremes most hostile to the pitch
#     (all weight on trust / all weight on access, the TIED pillars, where the delta
#     collapses to exactly 0) — where the with-rails side is NEVER worse. The delta
#     is a property of the capability evidence under every reasonable weighting, not
#     of one hand-tuned weight vector.
#
#     Worded by capability, never by vendor: the two fixture keys are the same the
#     pair guards already use; the property is stated over pillars (what an agent
#     can DO), never over identities.
# ---------------------------------------------------------------------------
def _renorm_weighted_mean(pillars: dict, weights: dict) -> float:
    """Renormalized weighted mean over pillars carrying BOTH a numeric score and a
    positive weight — the exact (uncapped) overall aggregation ``asrs.scoring.score``
    uses. Raises if no positive weight applies (callers guarantee it does)."""
    num = 0.0
    den = 0.0
    for p, s in pillars.items():
        if s is None:
            continue
        w = float(weights.get(p, 0.0))
        num += w * s
        den += w
    if den <= 0:
        raise ValueError("no positive weight over applicable pillars")
    return num / den


def test_canonical_delta_is_weight_robust() -> None:
    print("test_canonical_delta_is_weight_robust")
    com, com_miss = _score_fixture("driftflight.com")
    org, org_miss = _score_fixture("drift-flight.org")
    _check(not com_miss and not org_miss, "canonical pair: no replay-miss")

    # Precondition A — no grade cap binds on either side, so each overall IS a pure
    # renormalized weighted mean of its applicable pillars (a binding cap could
    # otherwise clamp the top and break the weight-invariance argument).
    _check(
        not com.caps_applied and not org.caps_applied,
        f"neither canonical side is grade-capped (com {com.caps_applied}, "
        f"org {org.caps_applied}) — overall is a pure weighted pillar mean",
    )

    # Precondition B — identical applicable-pillar set (numeric on BOTH). Like-for-
    # like denominator at the pillar layer: the reweighting family below reweights
    # the SAME pillars on each side, never a different set.
    com_appl = {p for p, s in com.pillar_scores.items() if s is not None}
    org_appl = {p for p, s in org.pillar_scores.items() if s is not None}
    _check(
        com_appl == org_appl and len(com_appl) >= 2,
        f"identical applicable-pillar set on both sides ({sorted(com_appl)})",
    )
    applicable = sorted(com_appl)

    # (a) PILLAR-WISE DOMINANCE — with-rails >= no-rails on EVERY applicable pillar,
    # strictly > on at least one. The load-bearing tripwire: an inversion on any
    # single pillar (a probe change letting the no-rails side out-score the
    # with-rails side somewhere) breaks it.
    strict = []
    for p in applicable:
        cs, os_ = com.pillar_scores[p], org.pillar_scores[p]
        _check(cs >= os_ - 1e-9, f"with-rails >= no-rails on {p} ({cs} >= {os_})")
        if cs > os_ + 1e-9:
            strict.append(p)
    _check(
        len(strict) >= 1,
        f"with-rails strictly exceeds no-rails on >=1 pillar (strict: {strict})",
    )
    # The strict wins are the benchmark-defining capability pillars — named so a
    # regression that narrowed dominance to only the TIED pillars is caught here.
    for p in ("legibility", "transactability"):
        if p in applicable:
            _check(p in strict, f"with-rails strictly dominates on {p} (capability pillar)")

    # (b) FAITHFULNESS — the real rubric weight vector reproduces the shipped
    # overalls from these pillars alone, so ``_renorm_weighted_mean`` IS the
    # scorer's aggregation and the reweighting family below re-runs the real overall
    # computation, not a lookalike.
    rubric_w = scoring.load_rubric(None).get("pillar_weights") or {}
    for rep, side in ((com, "with-rails"), (org, "no-rails")):
        recomputed = round(_renorm_weighted_mean(rep.pillar_scores, rubric_w), 1)
        _check(
            abs(recomputed - rep.overall_score) < 1e-9,
            f"rubric weights reproduce {side} overall from pillars "
            f"({recomputed} == {rep.overall_score})",
        )

    # (c) WEIGHT-ROBUSTNESS — across a family of ADVERSARIAL weight vectors the
    # with-rails mean is NEVER below the no-rails mean. The family: the real rubric
    # weights, a uniform weighting, and each unit-basis vector (ALL weight on one
    # pillar) — the unit vectors include the extremes most hostile to the pitch
    # (all weight on a TIED pillar, where the delta collapses to exactly 0).
    families = {"rubric": rubric_w, "uniform": {p: 1.0 for p in applicable}}
    for p in applicable:
        families[f"all-{p}"] = {p: 1.0}
    for name, w in families.items():
        cm = _renorm_weighted_mean(com.pillar_scores, w)
        om = _renorm_weighted_mean(org.pillar_scores, w)
        _check(
            cm >= om - 1e-9,
            f"weighting '{name}': with-rails mean {cm:.3f} >= no-rails {om:.3f} "
            f"(the delta never inverts under this reweighting)",
        )
        # Any weighting that touches a strictly-dominated pillar is STRICTLY pro-rails.
        if any(w.get(p, 0.0) > 0 for p in strict):
            _check(
                cm > om + 1e-9,
                f"weighting '{name}' touches a dominated pillar -> strictly "
                f"pro-rails ({cm:.3f} > {om:.3f})",
            )

    # (d) NON-VACUOUS — the aggregation IS sensitive to an inversion, so the
    # all-pass above is meaningful (not a helper that always returns the same sign).
    # Synthesize a no-rails variant that BEATS the with-rails side on the tied
    # 'trust' pillar and confirm the all-trust weighting would then favour the
    # synthetic side — exactly the inversion this guard catches on real data.
    if "trust" in applicable:
        inverted = dict(org.pillar_scores)
        inverted["trust"] = com.pillar_scores["trust"] + 10.0
        w_trust = {"trust": 1.0}
        _check(
            _renorm_weighted_mean(inverted, w_trust)
            > _renorm_weighted_mean(com.pillar_scores, w_trust),
            "negative control: a trust-inverted no-rails side WOULD top the "
            "with-rails side under all-trust weighting (guard is inversion-sensitive)",
        )


# ---------------------------------------------------------------------------
# 16. GUARD 14'S NEGATIVE CONTROL — the joint ordering-invariance assertion has
#     teeth, demonstrated not merely argued. Guard 14 proves the population
#     ORDERING survives a simultaneous relabel, and defends its non-vacuity with a
#     CONSTRUCTION argument: the neutral hosts are assigned REVERSE-lexical to
#     capability, so "a host-string sorter would reorder the population." Every
#     other invariance guard in this file backs its non-vacuity with a committed
#     INJECTION (guard 15(d) synthesizes a pillar inversion; the offering-layer
#     relabel guard monkeypatches an identity-keyed special-case) — guard 14 was
#     the one that only asserted its setup was correct, never that its ordering
#     check actually CATCHES the bug it names. This closes that gap.
#
#     Monkeypatch the exact "sort the domains alphabetically and assign tiers" bug
#     into the scorer: overall_score becomes a monotone function of the fixture
#     host's lexical rank (alphabetically-EARLIEST host -> HIGHEST score),
#     independent of the capability evidence. Because guard 14 assigns the neutral
#     hosts reverse-lexical to capability (floor host sorts first, top host last),
#     this bug REVERSES the population — so replaying the four relabeled fixtures
#     through the rigged scorer and applying guard 14's OWN strict-decreasing
#     ordering check must FAIL. If the ordering guard were vacuous (never actually
#     comparing one host's score against another's) this reversal would slip
#     through. The bug flows through the REAL ``_score_relabeled`` -> ``scoring.score``
#     path guard 14 uses, and the real scorer is restored in a finally block.
#     Worded by capability throughout — the rig keys on the host STRING, the
#     anti-pattern the benchmark must never exhibit.
# ---------------------------------------------------------------------------
def test_population_relabel_negative_control() -> None:
    print("test_population_relabel_negative_control")
    real_score = scoring.score
    # Assign overalls by ASCENDING lexical rank of the neutral host — the
    # alphabetically-first host earns the top score, keyed on identity not evidence.
    ascending = sorted(host for _, _, host in _JOINT_RELABEL)
    rigged_overall = {h: 100.0 - 10.0 * i for i, h in enumerate(ascending)}

    def rigged(checks, rubric, domain):
        report = real_score(checks, rubric, domain)
        if domain in rigged_overall:  # host-string-keyed override — the anti-pattern
            report.overall_score = rigged_overall[domain]
        return report

    scoring.score = rigged
    try:
        scored = []
        for dom, tier, host in _JOINT_RELABEL:
            rep, misses = _score_relabeled(dom, host)
            _check(not misses, f"{dom}->{host}: no replay-miss (rig only touches overall)")
            scored.append((dom, host, rep.overall_score))
        # Guard 14's OWN strict-decreasing ordering check, applied to the rigged
        # scores, must NOT hold — the host-string sorter reversed the population.
        monotone = all(hi[2] > lo[2] for hi, lo in zip(scored, scored[1:]))
        _check(
            not monotone,
            "negative control: a host-string-keyed scorer reverses the population, "
            "so guard 14's strict-decreasing ordering assertion FAILS on it "
            f"(rigged overalls in capability order: {[(h, s) for _, h, s in scored]}) "
            "— the ordering guard is non-vacuous",
        )
    finally:
        scoring.score = real_score
    # Guard against leaking the rig into later tests.
    _check(
        scoring.score is real_score,
        "real scoring.score restored after the negative control",
    )


# ---------------------------------------------------------------------------
# 17. POPULATION-WIDE WEIGHT-ROBUSTNESS — the WHOLE capability ordering (guard 12),
#     not just the head pair (guard 15), is invariant to the pillar weight vector.
#     Guard 15 refutes the "you rigged the weights" objection for the +39.4 PAIR:
#     the with-rails side dominates the no-rails side PILLAR-BY-PILLAR over a shared
#     applicable set, so no non-negative reweighting inverts that one rung. This
#     guard extends the refutation to the ENTIRE population — on the recorded
#     evidence EVERY adjacent rung of the capability spectrum is a pillar-wise
#     dominance step (the higher site is >= the lower on every applicable pillar,
#     strictly > on at least one), so the whole chain (com >= org >= retail >= bare)
#     is non-increasing under ANY non-negative pillar weighting, and strictly
#     decreasing at a rung whenever the weighting places positive weight on a pillar
#     where that rung is strict. The benchmark's central ordering (guard 12) is
#     therefore a property of the capability evidence under every reasonable
#     weighting, not of one hand-tuned weight vector — the aggregation-level analogue
#     of guard 15, lifted from the pair to the population.
#
#     HONEST FINDING pinned here: there is NO adjacent rung that is only weight-
#     DEPENDENTLY ordered. The one a-priori suspect was org-vs-retail on trust, but
#     the no-rails API storefront dominates the retail shop on trust (60.0 > 33.3)
#     as well as legibility and transactability — a TOTAL pillar-wise dominance
#     chain. Were any rung only weight-dependently ordered (pillar-wise
#     incomparable), the dominance assertion in (a) would fail on that rung and
#     surface it — a weight-dependent rank is a real calibration finding about the
#     benchmark, not a bug to suppress.
#
#     Worded by capability throughout: sites are compared by what an agent can DO
#     (their pillar scores), never by identity; the four fixture keys are the same
#     guards 1-16 already use, read from the LIVE replay pipeline.
# ---------------------------------------------------------------------------
def test_population_ordering_is_weight_robust() -> None:
    print("test_population_ordering_is_weight_robust")
    order = [d for d, _ in _CAPABILITY_SPECTRUM]
    reps = {}
    for dom in order:
        rep, misses = _score_fixture(dom)
        _check(not misses, f"{dom}: no replay-miss")
        reps[dom] = rep

    # Precondition A — no grade cap binds on ANY domain, so each overall IS a pure
    # renormalized weighted mean of its applicable pillars (a binding cap would clamp
    # a site's overall and break the weight-invariance argument for its rung).
    for dom in order:
        _check(
            not reps[dom].caps_applied,
            f"{dom} is not grade-capped ({reps[dom].caps_applied}) — overall is a "
            "pure weighted pillar mean",
        )

    # Precondition B — IDENTICAL applicable-pillar set across the WHOLE population
    # (numeric on every domain). Like-for-like denominator at the pillar layer: the
    # reweighting family below reweights the SAME pillars on every site, never a
    # different set on one rung.
    appl_sets = [
        frozenset(p for p, s in reps[dom].pillar_scores.items() if s is not None)
        for dom in order
    ]
    _check(
        len(set(appl_sets)) == 1 and len(appl_sets[0]) >= 2,
        f"identical applicable-pillar set across the population "
        f"({sorted(appl_sets[0])})",
    )
    applicable = sorted(appl_sets[0])

    # (a) ADJACENT PILLAR-WISE DOMINANCE — at every rung the higher site is >= the
    # lower on EVERY applicable pillar, strictly > on at least one. The load-bearing
    # tripwire: an inversion on any single pillar at any rung (a probe change letting
    # a lower-tier site out-score a higher one somewhere) breaks it — and would be
    # the HONEST signal that that rung's rank is weight-dependent, not a bug to hide.
    strict_by_rung = {}
    for hi, lo in zip(order, order[1:]):
        ph, pl = reps[hi].pillar_scores, reps[lo].pillar_scores
        strict = []
        for p in applicable:
            _check(
                ph[p] >= pl[p] - 1e-9,
                f"{hi} >= {lo} on {p} ({ph[p]:.3f} >= {pl[p]:.3f}) — rung is "
                "pillar-wise ordered, not weight-dependent",
            )
            if ph[p] > pl[p] + 1e-9:
                strict.append(p)
        _check(
            len(strict) >= 1,
            f"{hi} strictly exceeds {lo} on >=1 pillar (strict: {strict})",
        )
        strict_by_rung[(hi, lo)] = strict

    # (b) FAITHFULNESS — the real rubric weight vector reproduces every shipped
    # overall from these pillars alone, so ``_renorm_weighted_mean`` IS the scorer's
    # aggregation and the reweighting family below re-runs the real overall
    # computation on each site, not a lookalike.
    rubric_w = scoring.load_rubric(None).get("pillar_weights") or {}
    for dom in order:
        recomputed = round(_renorm_weighted_mean(reps[dom].pillar_scores, rubric_w), 1)
        _check(
            abs(recomputed - reps[dom].overall_score) < 1e-9,
            f"rubric weights reproduce {dom} overall from pillars "
            f"({recomputed} == {reps[dom].overall_score})",
        )

    # (c) WEIGHT-ROBUSTNESS — across a family of ADVERSARIAL weight vectors the WHOLE
    # chain's weighted means are non-increasing (every rung holds), and strictly
    # decreasing at a rung whenever the weighting touches a pillar where that rung is
    # strict. The family: the real rubric weights, a uniform weighting, and each
    # unit-basis vector (ALL weight on one pillar) — including the extremes most
    # hostile to the pitch (all weight on a TIED pillar like access, where a rung's
    # gap can collapse to exactly 0 but must never INVERT).
    families = {"rubric": rubric_w, "uniform": {p: 1.0 for p in applicable}}
    for p in applicable:
        families[f"all-{p}"] = {p: 1.0}
    for name, w in families.items():
        means = {dom: _renorm_weighted_mean(reps[dom].pillar_scores, w) for dom in order}
        for hi, lo in zip(order, order[1:]):
            _check(
                means[hi] >= means[lo] - 1e-9,
                f"weighting '{name}': {hi} mean {means[hi]:.3f} >= {lo} "
                f"{means[lo]:.3f} — the ordering never inverts at this rung",
            )
            if any(w.get(p, 0.0) > 0 for p in strict_by_rung[(hi, lo)]):
                _check(
                    means[hi] > means[lo] + 1e-9,
                    f"weighting '{name}' touches a dominated pillar at rung "
                    f"{hi}>{lo} -> strictly ordered ({means[hi]:.3f} > {means[lo]:.3f})",
                )

    # (d) NON-VACUOUS — the chain-wide check IS sensitive to a single-rung inversion,
    # so the all-pass above is meaningful. Inject an inversion at ONE rung on the
    # tied 'access' pillar (give the LOWER site of the retail>bare rung more access
    # than the higher) and confirm the all-access weighting would then rank the floor
    # site ABOVE the retail shop — exactly the inversion this guard's (c) check
    # catches at that rung on real data. Synthetic pillars only; real reports untouched.
    if "access" in applicable and len(order) >= 4:
        retail, bare = order[2], order[3]
        rigged_bare = dict(reps[bare].pillar_scores)
        rigged_bare["access"] = reps[retail].pillar_scores["access"] + 10.0
        w_access = {"access": 1.0}
        _check(
            _renorm_weighted_mean(rigged_bare, w_access)
            > _renorm_weighted_mean(reps[retail].pillar_scores, w_access),
            "negative control: an access-inverted floor site WOULD top the retail "
            "shop under all-access weighting (the chain check is inversion-sensitive)",
        )


# ---------------------------------------------------------------------------
# 19. THE DELTA IS EARNED AT THE CHECK LAYER — ACROSS THE WHOLE POPULATION.
#     Guard 8 (``test_canonical_delta_is_earned_dominance``) proves the +39.4 PAIR
#     is earned, not an accounting artifact, at the finest (per-check) layer:
#     full observability + like-for-like denominator + check-by-check dominance,
#     no inversion. Guards 12/17 already lift the ORDERING and its weight-robustness
#     to the four-domain population — but only at the aggregate/PILLAR layer. This
#     guard lifts guard 8's per-CHECK earned-ness argument to the population, and in
#     doing so surfaces an HONEST refinement the pillar-layer guards cannot see: the
#     population is NOT a clean check-by-check dominance chain the way the pair is.
#
#       (a) POPULATION LIKE-FOR-LIKE DENOMINATOR — all four domains are scored over
#           the IDENTICAL scored check_id set, so every rung of the spectrum
#           ordering (guard 12) compares the SAME checks, not one tier over fewer
#           checks. Stronger than guard 8(b), which pins like-for-like for the head
#           pair only.
#       (b) HONEST, TAIL-FAVOURING OBSERVABILITY — guard 8(a) pins FULL observability
#           on the head pair (where the delta lives), and that still holds here. But
#           the tail is NOT fully observed, and that is honest, not a defect: the two
#           non-API sites each have EXACTLY ONE unobserved check — ``self_serve_payg``
#           (transactability) — recorded CANT_TEST because they expose no
#           pay-as-you-go surface to probe, EXCUSED per invariant #4, never mis-scored
#           FAIL. No check is NA on any domain (nothing structurally masked). The key
#           attribution-honesty property: excusing a check EXCLUDES it from that
#           site's denominator, which can only RAISE the tail's score — so the honest
#           observability handling FAVOURS the lower-capability sites, yet the strict
#           capability ordering (guard 12, read live) still holds. The ordering
#           therefore cannot be a differential-observability artifact inflating the
#           head: the excusal helps the losers and they lose anyway.
#       (c) CHECK-LAYER DOMINANCE IS A PILLAR-ABSORBED MAJORITY, NOT A TOTAL SUPERSET
#           — the honest lift of guard 8(c). Over each adjacent rung's shared,
#           mutually-OBSERVED checks: the head pair (com>org) and the tail rung
#           (retail>bare) are CLEAN check-by-check supersets (zero inversions, >=1
#           strict win each). The middle rung (org>retail) carries EXACTLY ONE honest
#           inversion — ``https_hsts`` (trust): the human-only retail shop's HTTPS/HSTS
#           strictly out-ranks the no-rails API storefront's — which the TRUST-pillar
#           aggregation ABSORBS (the no-rails API still wins the trust pillar,
#           60.0 > 33.3, and the aggregate, 46.1 > 29.5). So that rung's aggregate gap
#           is earned by a capability MAJORITY, surfaced honestly, not a superset. This
#           is exactly the "watch the tail — rungs may legitimately differ" caveat the
#           backlog flagged, resolved by measurement rather than forced into a false
#           total-superset claim. Pinning the exact inversion set per rung makes it a
#           tripwire: a probe change that introduced a NEW check-layer inversion at
#           any rung, or a scoring change that let an absorbed inversion flip its
#           pillar/aggregate, fails HERE — and is a real calibration finding, not a
#           bug to hide.
#
#     Read from the LIVE replay pipeline (never the pinned constants); worded by
#     capability tier throughout — the four fixture keys guards 1-17 already use.
# ---------------------------------------------------------------------------
_HEAD_DOMAINS = ("driftflight.com", "drift-flight.org")  # API storefronts, fully observed
_TAIL_DOMAINS = ("books.toscrape.com", "example.com")    # non-API, one excused check each
# The single honest check-layer inversion, by rung (higher -> lower). The retail
# shop's HTTPS/HSTS out-ranks the no-rails API's; the trust pillar absorbs it.
_EXPECTED_INVERSIONS = {
    ("driftflight.com", "drift-flight.org"): frozenset(),
    ("drift-flight.org", "books.toscrape.com"): frozenset({"https_hsts"}),
    ("books.toscrape.com", "example.com"): frozenset(),
}


def _observed_status_map(report):
    """{check_id: status} for a scored report."""
    return {c.check_id: c.status for c in report.checks}


def _rung_inversions(hi_status, lo_status):
    """Over checks OBSERVED (ranked) on BOTH sides, return (inversions, strict_wins).

    ``inversions`` = checks where the lower rung out-ranks the higher (capability
    rank PASS>PARTIAL>FAIL); ``strict_wins`` = checks where the higher strictly
    out-ranks the lower. CANT_TEST/NA are unobserved and skipped (guard 8's
    ``_UNOBSERVED``): a like-for-like check-layer comparison only ranks checks both
    sides actually exposed.
    """
    inv, strict = {}, []
    for cid in set(hi_status) & set(lo_status):
        hs, ls = hi_status[cid], lo_status[cid]
        if hs in _UNOBSERVED or ls in _UNOBSERVED:
            continue
        rh, rl = _CAP_RANK[hs], _CAP_RANK[ls]
        if rh < rl:
            inv[cid] = (ls.name, hs.name)  # lower rung beats higher
        elif rh > rl:
            strict.append(cid)
    return inv, strict


def test_population_delta_is_earned_at_the_check_layer() -> None:
    print("test_population_delta_is_earned_at_the_check_layer")
    order = [d for d, _ in _CAPABILITY_SPECTRUM]
    reps, status = {}, {}
    for dom in order:
        rep, misses = _score_fixture(dom)
        _check(not misses, f"{dom}: no replay-miss")
        reps[dom] = rep
        status[dom] = _observed_status_map(rep)

    # (a) POPULATION LIKE-FOR-LIKE DENOMINATOR — identical scored check_id set on
    # all four, so the ordering compares the same checks at every rung.
    sets = [frozenset(status[dom]) for dom in order]
    _check(
        len(set(sets)) == 1,
        "all four domains are scored over the identical check_id set — the "
        f"population ordering is like-for-like (per-domain sets differ: "
        f"{[(dom, sorted(set(sets[0]) ^ frozenset(status[dom]))) for dom in order if frozenset(status[dom]) != sets[0]]})",
    )

    # (b) HONEST, TAIL-FAVOURING OBSERVABILITY.
    # No check is NA anywhere — nothing structurally masked.
    na = {dom: {k for k, s in status[dom].items() if s is Status.NA} for dom in order}
    _check(
        not any(na.values()),
        f"no check is NA on any domain (structural masking would hide a FAIL): {na}",
    )
    # The head pair (where the delta lives) is FULLY observed — guard 8(a) holds here.
    for dom in _HEAD_DOMAINS:
        unobs = {k for k, s in status[dom].items() if s in _UNOBSERVED}
        _check(
            not unobs,
            f"{dom} (API storefront) is fully observed — every recorded FAIL is "
            f"scored evidence-of-absence, not an excused gap (unobserved: {unobs})",
        )
    # The tail's ONLY unobserved status is CANT_TEST on the absent pay-as-you-go
    # surface — honestly excused (invariant #4), never mis-scored FAIL.
    for dom in _TAIL_DOMAINS:
        unobs = {k for k, s in status[dom].items() if s in _UNOBSERVED}
        _check(
            unobs == {"self_serve_payg"},
            f"{dom} (non-API site) has exactly one unobserved check, the absent "
            f"self-serve pay-as-you-go surface (unobserved: {unobs})",
        )
        _check(
            status[dom]["self_serve_payg"] is Status.CANT_TEST,
            f"{dom}: the absent pay-as-you-go surface is EXCUSED as CANT_TEST "
            f"(excluded from the denominator), not penalised FAIL "
            f"(got {status[dom]['self_serve_payg'].name})",
        )
    # The excusal FAVOURS the tail (raises its score by shrinking its denominator),
    # yet the strict ordering holds — so it is not a head-inflating observability
    # artifact. Read the ordering live.
    for hi, lo in zip(order, order[1:]):
        _check(
            reps[hi].overall_score > reps[lo].overall_score,
            f"strict ordering holds despite tail-favouring excusal: {hi} "
            f"{reps[hi].overall_score} > {lo} {reps[lo].overall_score}",
        )

    # (c) CHECK-LAYER DOMINANCE — a pillar-absorbed majority, not a total superset.
    for hi, lo in zip(order, order[1:]):
        inv, strict = _rung_inversions(status[hi], status[lo])
        want = _EXPECTED_INVERSIONS[(hi, lo)]
        _check(
            frozenset(inv) == want,
            f"rung {hi}>{lo}: check-layer inversion set == {sorted(want)} "
            f"(got {inv}) — a NEW inversion here is a real calibration finding",
        )
        # Every rung is still driven UP by capability: at least one strict win.
        _check(
            len(strict) >= 1,
            f"rung {hi}>{lo}: the higher tier strictly out-ranks the lower at >=1 "
            f"observed check (strict wins: {sorted(strict)})",
        )
    # The middle rung's inversion is NON-EMPTY (so the clean-superset claim at the
    # other two rungs is a real, discriminating condition, not vacuously true) AND
    # ABSORBED by the trust pillar — org still wins trust and the aggregate.
    mid = ("drift-flight.org", "books.toscrape.com")
    mid_inv, _ = _rung_inversions(status[mid[0]], status[mid[1]])
    _check(
        len(mid_inv) == 1 and set(mid_inv) == {"https_hsts"},
        f"the org>retail rung has exactly one honest check-layer inversion, "
        f"https_hsts (retail HTTPS out-ranks the no-rails API's): {mid_inv}",
    )
    _check(
        reps[mid[0]].pillar_scores["trust"] > reps[mid[1]].pillar_scores["trust"],
        f"the inversion is pillar-ABSORBED: the no-rails API still wins the trust "
        f"pillar ({reps[mid[0]].pillar_scores['trust']} > "
        f"{reps[mid[1]].pillar_scores['trust']}), so it does not flip the ordering",
    )


# ---------------------------------------------------------------------------
# 20. GUARD 19'S NEGATIVE CONTROL — the observability-honesty leg (b) is a real
#     tripwire against MIS-ATTRIBUTED ABSENCE (invariant #4), not a construction
#     argument. The dishonest move guard 19(b) forbids: score a capability a site
#     genuinely cannot expose as FAIL (evidence-of-absence, scored 0 IN the
#     denominator) instead of CANT_TEST (excused, EXCLUDED) — penalising a site for
#     what could not be observed. This monkeypatches ``scoring.score`` to rewrite the
#     tail's excused ``self_serve_payg`` CANT_TEST -> FAIL and confirms guard 19(b)'s
#     "the tail's absent surface is CANT_TEST" assertion FAILS on it — so the clean
#     pass on the real scorer is meaningful. The bug flows through the REAL
#     ``_score_fixture`` -> ``scoring.score`` path guard 19 uses; the real scorer is
#     restored in a finally + a restore assertion so the rig never leaks (same
#     discipline as guards 16/18).
# ---------------------------------------------------------------------------
def test_population_check_layer_negative_control() -> None:
    print("test_population_check_layer_negative_control")
    real_score = scoring.score

    def rigged(checks, rubric, domain):
        report = real_score(checks, rubric, domain)
        if domain in _TAIL_DOMAINS:  # mis-attribute the absent surface as a failure
            for c in report.checks:
                if c.check_id == "self_serve_payg" and c.status is Status.CANT_TEST:
                    c.status = Status.FAIL
        return report

    scoring.score = rigged
    try:
        caught = False
        for dom in _TAIL_DOMAINS:
            rep, _ = _score_fixture(dom)
            st = _observed_status_map(rep)
            # Guard 19(b)'s own assertion: the tail's absent surface must be CANT_TEST.
            if st.get("self_serve_payg") is not Status.CANT_TEST:
                caught = True
        _check(
            caught,
            "negative control: a scorer that mis-attributes the tail's absent "
            "pay-as-you-go surface as FAIL is CAUGHT by guard 19(b)'s "
            "CANT_TEST-excusal assertion — the observability-honesty leg is "
            "non-vacuous",
        )
    finally:
        scoring.score = real_score
    _check(
        scoring.score is real_score,
        "the real scorer is restored after the check-layer negative control",
    )


# ---------------------------------------------------------------------------
# 21. FIXTURE REPLAY-INTEGRITY PARTITION — every committed canonical fixture is
#     EITHER score-replay-clean (covers the full current probe set: 0
#     replay-misses, so it can drive a replay-SCORE guard as a like-for-like
#     re-score) OR explicitly quarantined as classification-only (captured for
#     offering/battery classification, whose probe surface is a strict SUBSET of
#     the full scoring path, so a full score-replay requests dozens of URLs it
#     never recorded and misses them).
#
#     WHY THIS IS A TRUTH GUARD. A score-replay is only a faithful re-score when
#     the fixture covers every probe request — the _assert_domain (a)-leg pins
#     this for the FIVE pinned score domains, but nothing pinned the fixtures
#     committed for OTHER purposes. Two of them silently CANNOT replay-score:
#     api.replicate.com (35 misses) and ipinfo.io (46 misses), both captured via
#     the classification path (they miss the full scorer's robots.txt, homepage
#     under claudebot/gptbot UAs, the trust/legal surface sweep, sitemap,
#     pricing.json/catalog.json, cross-domain review URLs). The standing backlog
#     proposal to add a SECOND API storefront (api.replicate.com) to
#     _CAPABILITY_SPECTRUM would, done blindly, explode every population guard with
#     a cryptic replay-miss rather than a clear "re-capture first" signal. This
#     partition makes fixture faithfulness an EXPLICIT, self-maintaining invariant:
#       - a NEW committed fixture that is neither clean nor quarantined FAILS here,
#         forcing an eligibility decision before any guard can trust it;
#       - a quarantined fixture that a [LOCAL] full-score re-capture makes clean
#         FLIPS this guard red — the signal to promote it to _REPLAY_CLEAN and
#         decide spectrum/calibration inclusion (the backlog item, made actionable
#         instead of silently blocked).
#     Partitioned by the OPERATIONAL property (does it cover the full probe set),
#     never by vendor: acuityscheduling.com was also captured for classification
#     yet happens to be replay-clean, so it sits in the clean set on its evidence.
# ---------------------------------------------------------------------------
# Fixtures that cover the full current probe set (0 misses) — eligible to drive
# any replay-SCORE / calibration-score guard as a like-for-like re-score.
_REPLAY_CLEAN = {
    "driftflight.com",
    "drift-flight.org",
    "books.toscrape.com",
    "example.com",
    "www.moleskine.com",
    "acuityscheduling.com",
}
# Fixtures whose recorded surface is a strict subset of the full scoring path
# (captured for offering/battery classification) — NOT eligible for any
# score-replay guard until re-captured full-score [LOCAL]:
#   asrs.cli score <domain> --record-fixture fixtures/canonical/<domain>.json
_CLASSIFICATION_ONLY = {"api.replicate.com", "ipinfo.io", "www.allbirds.com"}


def test_committed_fixtures_are_partitioned_by_replay_integrity() -> None:
    print("test_committed_fixtures_are_partitioned_by_replay_integrity")
    on_disk = {
        os.path.basename(p)[:-5]
        for p in glob.glob(os.path.join(_FIXTURE_DIR, "*.json"))
    }
    # (a) The partition is TOTAL and DISJOINT over what is actually committed — a
    # new fixture can be neither silently trusted nor silently ignored.
    _check(
        _REPLAY_CLEAN.isdisjoint(_CLASSIFICATION_ONLY),
        "the two replay-integrity partitions are disjoint",
    )
    tracked = _REPLAY_CLEAN | _CLASSIFICATION_ONLY
    _check(
        on_disk == tracked,
        f"every committed fixture is partitioned exactly once "
        f"(untracked: {sorted(on_disk - tracked)}; "
        f"tracked-but-absent: {sorted(tracked - on_disk)})",
    )
    # (b) THE INVARIANT protecting every score-replay guard: each clean fixture
    # covers the FULL current probe set (0 misses). This is exactly what would
    # have caught a naive add of a classification-only fixture to the spectrum.
    for dom in sorted(_REPLAY_CLEAN):
        _rep, misses = _score_fixture(dom)
        _check(
            not misses,
            f"replay-clean fixture {dom} covers every probe request "
            f"(0 misses; got {len(misses)})",
        )
    # (c) QUARANTINE TRIPWIRE + non-vacuity: each classification-only fixture DOES
    # miss under the full scorer (documenting WHY it is quarantined, and making
    # (b) a non-trivial partition — the property is not vacuously "all clean").
    # When a [LOCAL] full-score re-capture makes one clean, this reddens: promote
    # it to _REPLAY_CLEAN and decide spectrum/calibration inclusion.
    for dom in sorted(_CLASSIFICATION_ONLY):
        _rep, misses = _score_fixture(dom)
        _check(
            len(misses) > 0,
            f"classification-only fixture {dom} is not yet score-replay-clean "
            f"({len(misses)} misses) — quarantined until [LOCAL] full-score "
            f"re-capture; promote to _REPLAY_CLEAN when this flips",
        )


# ---------------------------------------------------------------------------
# 18. THE OFFLINE REPLAY INSTRUMENT IS DETERMINISTIC — the in-cloud regression
#     signal reproduces itself run-to-run. Every shipping cycle re-measures the
#     canonical population by replaying the committed fixtures through the REAL
#     from_fixture -> _run_probes -> scoring.score path; while the launchd live
#     runner is down (P0-tracked) this offline replay is the SOLE canonical
#     regression signal. A regression signal is only trustworthy if the instrument
#     that produces it is reproducible — the North Star's "reproducible" axis, at
#     the level of the OFFLINE measurement itself. `canonical_history`'s noise-floor
#     determinism (Cycle 47) pins the LIVE runner's cross-artifact series; this pins
#     the complementary fact the runner can't: that a SINGLE in-cloud replay is
#     deterministic run-to-run over the FULL scored output — overall, grade, rubric
#     version, every pillar, AND every check's (status, points, max_points). If a
#     future scoring/probe change introduced order-dependence (e.g. a set() in
#     aggregation whose iteration order perturbed a float sum), every per-cycle
#     re-score number would silently become non-reproducible; this guard is the
#     tripwire. Read from the live pipeline; worded by measurement, not by vendor.
# ---------------------------------------------------------------------------
def _report_fingerprint(report) -> tuple:
    """The full SCORED surface of a report, in a canonical, comparison-stable form."""
    checks = tuple(
        sorted(
            (c.check_id, c.status.name, c.points, c.max_points)
            for c in report.checks
        )
    )
    pillars = tuple(sorted(report.pillar_scores.items()))
    return (report.overall_score, report.grade, report.rubric_version, pillars, checks)


def _assert_reports_identical(domain: str, a, b) -> None:
    fa, fb = _report_fingerprint(a), _report_fingerprint(b)
    _check(
        fa == fb,
        f"{domain}: two independent replays produce a byte-identical scored report "
        f"(overall/grade/version/pillars/every check status+points)",
    )


def test_replay_pipeline_is_deterministic() -> None:
    print("test_replay_pipeline_is_deterministic")
    # (a) Each fixture scored TWICE through INDEPENDENT from_fixture -> _run_probes
    # -> scoring.score passes (fresh FetchContext each time, no shared cache) yields
    # the identical scored output — the whole population's re-score is reproducible.
    for dom, _tier in _CAPABILITY_SPECTRUM:
        r1, m1 = _score_fixture(dom)
        r2, m2 = _score_fixture(dom)
        _check(not m1 and not m2, f"{dom}: no replay-miss on either pass")
        _assert_reports_identical(dom, r1, r2)

    # (b) NON-VACUOUS negative control — the identical-report check actually CATCHES
    # a scorer whose output VARIES run-to-run (the exact failure a determinism guard
    # exists to detect). Wrap scoring.score so every 2nd call perturbs the overall by
    # a hair; because guard 18(a) compares the FULL scored surface, the two passes now
    # diverge and _assert_reports_identical must raise. Monkeypatch on scoring.score
    # (the attribute _score_fixture calls), restored in a finally + a restore
    # assertion so the rig never leaks into later tests (same discipline as guard 16).
    real_score = scoring.score
    calls = {"n": 0}

    def flaky_score(checks, rubric, domain):
        rep = real_score(checks, rubric, domain)
        calls["n"] += 1
        if calls["n"] % 2 == 0 and rep.overall_score is not None:
            rep = dataclasses.replace(rep, overall_score=rep.overall_score + 0.1)
        return rep

    scoring.score = flaky_score
    try:
        r1, _ = _score_fixture("driftflight.com")
        r2, _ = _score_fixture("driftflight.com")
        caught = False
        try:
            _assert_reports_identical("driftflight.com", r1, r2)
        except AssertionError:
            caught = True
        _check(
            caught,
            "negative control: a run-varying scorer is CAUGHT by the determinism "
            "check (so the all-identical result on the real scorer is meaningful)",
        )
    finally:
        scoring.score = real_score
    _check(
        scoring.score is real_score,
        "the real scorer is restored after the determinism negative control",
    )


# ---------------------------------------------------------------------------
# 19. THE SCORER IS INVARIANT TO CHECK-INPUT ORDER — the reproducibility axis
#     guard 18's own docstring HYPOTHESIZES ("a set() in aggregation whose
#     iteration order perturbed a float sum") but does NOT actually test. Guard 18
#     replays each fixture TWICE through from_fixture -> _run_probes, a
#     deterministic pipeline, so the checks reach scoring.score in the SAME order on
#     both passes: an aggregation sensitive to check-INPUT order — the pillar
#     earned-sum ``earned[pillar] += c.points`` (float addition is not associative),
#     or the ``caps_applied`` list, which scoring.score builds in check-ARRIVAL
#     order — would be perfectly stable run-to-run yet CHANGE if the probes emitted
#     their checks in a different order, and guard 18 is structurally blind to it. A
#     per-cycle re-score number is only "reproducible" (the North Star axis) if it
#     does not depend on the order the probes happened to emit their checks; this
#     guard pins that missing rung. Score each committed fixture, then re-score the
#     SAME CheckResults PERMUTED (reversed) and assert the full scored surface
#     (overall/grade/version/pillars/every check status+points) is byte-identical.
#     Read from the live pipeline; worded by measurement, not by vendor.
# ---------------------------------------------------------------------------
def test_scorer_is_invariant_to_check_input_order() -> None:
    print("test_scorer_is_invariant_to_check_input_order")
    rubric = scoring.load_rubric(None)
    # (a) Every domain in the population: reversing the check-input order leaves the
    # scored report byte-identical over its full scored surface.
    for dom, _tier in _CAPABILITY_SPECTRUM:
        rep, misses = _score_fixture(dom)
        _check(not misses, f"{dom}: no replay-miss")
        checks = list(rep.checks)
        _check(
            len(checks) >= 2 and checks[0].check_id != checks[-1].check_id,
            f"{dom}: >=2 checks with distinct end ids, so reversing is a real "
            f"reordering ({len(checks)} checks)",
        )
        forward = scoring.score(checks, rubric, dom)
        reverse = scoring.score(list(reversed(checks)), rubric, dom)
        _assert_reports_identical(f"{dom} (reversed check-input order)", forward, reverse)

    # (b) NON-VACUOUS negative control — the reversed-order identity check actually
    # CATCHES a scorer whose output depends on check-input order (the exact failure
    # this guard exists to detect, and the one guard 18 cannot see). Rig
    # scoring.score so the overall picks up a hair whenever the FIRST check out-ranks
    # the LAST by id — a stand-in for any arrival-order-sensitive aggregation;
    # reversing the input flips that comparison, so forward and reversed diverge and
    # _assert_reports_identical must raise. The rig flows through the REAL scorer and
    # is restored in a finally + a restore assertion so it never leaks (guards 16/18).
    com_checks = list(_score_fixture("driftflight.com")[0].checks)
    real_score = scoring.score

    def order_sensitive(checks, rubric_, domain):
        rep = real_score(checks, rubric_, domain)
        checks = list(checks or [])
        if rep.overall_score is not None and len(checks) >= 2:
            bump = 0.1 if checks[0].check_id > checks[-1].check_id else 0.0
            rep = dataclasses.replace(rep, overall_score=rep.overall_score + bump)
        return rep

    scoring.score = order_sensitive
    try:
        fwd = scoring.score(com_checks, rubric, "driftflight.com")
        rev = scoring.score(list(reversed(com_checks)), rubric, "driftflight.com")
        caught = False
        try:
            _assert_reports_identical("driftflight.com", fwd, rev)
        except AssertionError:
            caught = True
        _check(
            caught,
            "negative control: an input-order-sensitive scorer is CAUGHT by the "
            "reversed-order identity check (so the all-identical result on the real "
            "scorer is meaningful)",
        )
    finally:
        scoring.score = real_score
    _check(
        scoring.score is real_score,
        "the real scorer is restored after the input-order negative control",
    )


# ---------------------------------------------------------------------------
# 20. THE APPLIED-CAPS SET IS INVARIANT TO CHECK-INPUT ORDER — the caps leg
#     guard 19 (test_scorer_is_invariant_to_check_input_order) NAMES as
#     arrival-order-sensitive in its own docstring but never actually drives.
#     ``scoring.score`` builds ``caps_applied`` by APPENDING each binding cap in
#     check-ARRIVAL order, so reversing the input reverses that LIST. On every
#     committed fixture NO grade cap binds (the weight-robust guard's precondition
#     confirms neither canonical side is capped), so ``caps_applied`` is empty
#     everywhere and guard 19's reversed-order pass exercises the caps output
#     VACUOUSLY. This guard forces the latent path live: a synthetic surface whose
#     rubric makes TWO distinct critical findings bind, scored forward and
#     reversed. The reproducibility invariant that matters — the SET of caps
#     applied, the capped overall, and the grade — must not depend on the order
#     the probes happened to emit their checks. The incidental LIST order DOES
#     flip (making the reversal a real reordering of the caps output, not a
#     no-op), which is exactly why SET-equality, not list-equality, is the honest
#     invariant here: the arrival order carries no scored meaning. Worded by
#     measurement, not by vendor.
# ---------------------------------------------------------------------------
def test_applied_caps_set_is_invariant_to_check_input_order() -> None:
    print("test_applied_caps_set_is_invariant_to_check_input_order")
    # A minimal synthetic surface: two PASS checks on two pillars, each carrying a
    # DISTINCT critical finding the rubric caps BELOW the uncapped overall, at two
    # different cap values. Pre-cap overall is 100 (both pillars 100), so BOTH caps
    # bind — the state no committed fixture reaches. ``_checks_by_id`` names both
    # ids so scoring's coverage-warning loops stay silent.
    checks = [
        CheckResult("a", "access", Status.PASS, 10.0, 10.0, "critical-x", ""),
        CheckResult("b", "transactability", Status.PASS, 10.0, 10.0, "critical-y", ""),
    ]
    rubric = {
        "version": "test-caps-order",
        "pillar_weights": {"access": 1.0, "transactability": 1.0},
        "caps": {"critical-x": 40.0, "critical-y": 25.0},
        "grade_bands": [[95, "A+"], [90, "A"], [80, "B"], [70, "C"], [60, "D"], [0, "F"]],
        "_checks_by_id": {"a": {"id": "a"}, "b": {"id": "b"}},
    }
    fwd = scoring.score(checks, rubric, "synthetic-caps")
    rev = scoring.score(list(reversed(checks)), rubric, "synthetic-caps")

    # (a) NON-VACUOUS: unlike every committed fixture, BOTH caps bind here, so
    # caps_applied is genuinely exercised (len 2, not the empty list guard 19 sees
    # everywhere) — without this the order-invariance claim would be trivially true.
    _check(
        set(fwd.caps_applied) == {"critical-x", "critical-y"}
        and len(fwd.caps_applied) == 2,
        f"forward binds BOTH caps (non-vacuous): {fwd.caps_applied}",
    )

    # (b) The reversal is a REAL reordering of the caps output — the LIST order
    # flips (append-in-arrival-order), so the set-equality below is a non-trivial
    # invariant, not a no-op (mirrors guard 19's distinct-end-ids non-vacuity).
    _check(
        fwd.caps_applied != rev.caps_applied,
        f"reversing the input reorders the caps LIST ({fwd.caps_applied} -> "
        f"{rev.caps_applied}) — a real reordering, so set-equality is non-trivial",
    )

    # (c) THE INVARIANT: the SET of applied caps, the capped overall, and the grade
    # are identical regardless of arrival order — the reproducibility property the
    # per-cycle re-score number rests on. The overall is the lowest binding cap
    # (25.0) either way; the list order carries no scored meaning.
    _check(
        set(fwd.caps_applied) == set(rev.caps_applied),
        f"applied-caps SET is order-invariant ({set(fwd.caps_applied)})",
    )
    _check(
        fwd.overall_score == rev.overall_score == 25.0,
        f"capped overall is order-invariant (fwd {fwd.overall_score}, rev "
        f"{rev.overall_score}) — the lowest binding cap",
    )
    _check(
        fwd.grade == rev.grade,
        f"grade is order-invariant (fwd {fwd.grade!r}, rev {rev.grade!r})",
    )

    # (d) NON-VACUOUS negative control — the set-equality assertion actually CATCHES
    # an order-SENSITIVE cap recorder (the failure mode guard 19 cannot see because
    # caps never bind on its fixtures). Rig scoring.score to keep only the FIRST
    # binding cap in arrival order — a plausible order-sensitive implementation;
    # forward then records {critical-x}, reversed {critical-y}, and the sets DIVERGE.
    # Flows through the REAL scorer and is restored in a finally + a restore
    # assertion so it never leaks (the guards-16/18/19 convention in this file).
    real_score = scoring.score

    def first_binding_cap_only(checks_, rubric_, domain_):
        rep = real_score(checks_, rubric_, domain_)
        if rep.caps_applied:
            rep = dataclasses.replace(rep, caps_applied=rep.caps_applied[:1])
        return rep

    scoring.score = first_binding_cap_only
    try:
        rigged_fwd = scoring.score(checks, rubric, "synthetic-caps")
        rigged_rev = scoring.score(list(reversed(checks)), rubric, "synthetic-caps")
        _check(
            set(rigged_fwd.caps_applied) != set(rigged_rev.caps_applied),
            "negative control: an order-SENSITIVE cap recorder (first binding cap "
            f"only) is CAUGHT by set-inequality (fwd {set(rigged_fwd.caps_applied)} "
            f"!= rev {set(rigged_rev.caps_applied)}) — so the real scorer's "
            "set-equality above is meaningful",
        )
    finally:
        scoring.score = real_score
    _check(
        scoring.score is real_score,
        "the real scorer is restored after the caps-order negative control",
    )


def main() -> int:
    tests = [
        test_canonical_org_replays_46_1,
        test_canonical_com_replays_85_5,
        test_canonical_delta_is_39_4,
        test_canonical_delta_is_agent_native_payment,
        test_relabel_invariance_org,
        test_relabel_invariance_com,
        test_relabeled_delta_still_39_4,
        test_canonical_delta_is_earned_dominance,
        test_retail_storefront_replays_29_5,
        test_retail_storefront_earns_no_agent_native_payment,
        test_relabel_invariance_retail,
        test_nonstorefront_replays_22_5,
        test_nonstorefront_earns_no_agent_native_payment,
        test_relabel_invariance_nonstorefront,
        test_population_overall_tracks_capability_ordering,
        test_population_ordering_is_not_a_transactability_artifact,
        test_population_ordering_is_identity_invariant,
        test_canonical_delta_is_weight_robust,
        test_population_relabel_negative_control,
        test_population_ordering_is_weight_robust,
        test_population_delta_is_earned_at_the_check_layer,
        test_population_check_layer_negative_control,
        test_committed_fixtures_are_partitioned_by_replay_integrity,
        test_replay_pipeline_is_deterministic,
        test_scorer_is_invariant_to_check_input_order,
        test_applied_caps_set_is_invariant_to_check_input_order,
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
