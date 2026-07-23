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
from asrs.types import Status  # noqa: E402

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


def main() -> int:
    tests = [
        test_canonical_org_replays_46_1,
        test_canonical_com_replays_85_5,
        test_canonical_delta_is_39_4,
        test_canonical_delta_is_agent_native_payment,
        test_relabel_invariance_org,
        test_relabel_invariance_com,
        test_relabeled_delta_still_39_4,
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
