"""Probe-order independence of the scored aggregate (METHOD track).

Runnable directly, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_probe_order_reproducibility.py

This suite closes the last open axis of static-path reproducibility. The
host-ENVIRONMENT axes are already guarded per-cycle — the process cannot smuggle
a nondeterministic serialization in through its startup choices: PYTHONHASHSEED
(test_hashseed_reproducibility), timezone (test_timezone_reproducibility),
encoding (test_encoding_reproducibility) and locale (test_locale_reproducibility)
each re-score the committed fixtures under a varied host setting and assert the
serialized report is invariant. The sibling axis those leave open is INTERNAL:
the ORDER in which CheckResults arrive at the scorer.

Today ``asrs.cli._run_probes`` emits checks in a fixed module order
(``_PROBE_MODULES``), and within each module in a fixed order — so in practice
the arrival order is deterministic and the committed reports reproduce. But that
determinism is a property of the CURRENT probe wiring, not of the SCORER. The
scientifically meaningful invariant is stronger and belongs to
``scoring.score`` itself: the SCORED AGGREGATE — every number a reader cites
(overall, grade, per-pillar scores, the set of binding caps, scorable-or-not) —
must be a pure fold over the checks, INDEPENDENT of the order they arrive in. If
a future aggregation refinement ever became order-sensitive (a first-match-wins
dedup, a positional tie-break, a running max that reads list position), a mere
reordering of the probe list would silently move committed evidence — or a score
— while every fixed-order number-pinning guard in test_canonical_replay stayed
green. This suite converts "the scorer is a pure count-based fold" from an
assumed property into a VERIFIED, per-cycle one.

It asserts two things over the whole replay-clean population, scoring each
fixture's real checks under many deterministic permutations (reverse + seeded
shuffles):

  1. the scored AGGREGATE is byte-identical across every order, and
  2. once the two fields that legitimately FOLLOW arrival order (the ``checks``
     array and ``caps_applied``) are canonicalized, the FULL serialized report
     is byte-identical across every order — i.e. arrival order reaches ONLY
     those two presentation fields and nothing that survives into a scored or
     evidence value.

Guard 3 documents the ONE latent arrival-order dependence the scorer still
carries: ``caps_applied`` is appended in check-arrival order (scoring.py), so
with >=2 binding caps its LIST order flips under a reordering even though the
capped ``overall`` (a min over cap values) and the cap SET do not. It never
bites today (no committed fixture has >=2 binding caps — every real
``caps_applied`` is empty), so this suite's aggregate comparison uses the cap
SET and its byte comparison sorts ``caps_applied``; the teeth prove that
distinction is load-bearing, and a peer-gated follow-up (sort ``caps_applied``
in scoring.py so the raw report is byte-reproducible too) is queued in BACKLOG.

Off the scoring path, tests-only: rubric version, probes, scoring code, and the
canonical delta are untouched. The teeth run the REAL scorer on a synthetic
two-cap input, so the invariance guards cannot vacuously pass.
"""

from __future__ import annotations

import dataclasses
import glob
import hashlib
import json
import os
import random
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")
sys.path.insert(0, _REPO_ROOT)

from asrs import scoring  # noqa: E402
from asrs.cli import _run_probes  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.types import CheckResult, Status  # noqa: E402

# The regression-signal pair — the two API storefronts (with vs without
# agent-native rails). Named by capability role, never special-cased.
_CANONICAL = ("driftflight.com", "drift-flight.org")

# The FULL reproducibility population: every committed fixture that full-re-scores
# with 0 replay-misses (guard 4 pins this to the LIVE-computed set, exactly like
# test_hashseed_reproducibility, so a [LOCAL] re-capture that promotes a
# classification-only fixture is forced in rather than lagging silently). The
# retail catalog / booking SaaS / physical-goods / null fixtures fire probe paths
# the API pair never does, so an order-sensitive aggregation on one of THOSE paths
# is caught too.
_POPULATION = (
    "acuityscheduling.com",
    "api.replicate.com",
    "books.toscrape.com",
    "drift-flight.org",
    "driftflight.com",
    "example.com",
    "ipinfo.io",
    "www.moleskine.com",
)

# Deterministic shuffle seeds (NOT unseeded randomness — the permutations must be
# reproducible so a red is reproducible). Reverse is added on top of these.
_SHUFFLE_SEEDS = (1, 2, 3, 17, 101)

# Serialization params MUST mirror Report.to_json (asrs/types.py) so the byte
# comparison exercises the same serialization path the committed reports use.
_JSON_KW = dict(indent=2, default=str)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _real_checks(domain: str) -> list:
    """The domain's real CheckResult list, in native probe-arrival order."""
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
    return _run_probes(ctx)


def _orderings(checks: list) -> list[list]:
    """Native order + reverse + several deterministic shuffles of ``checks``."""
    orders = [list(checks), list(reversed(checks))]
    for seed in _SHUFFLE_SEEDS:
        c = list(checks)
        random.Random(seed).shuffle(c)
        orders.append(c)
    return orders


def _aggregate(rep) -> tuple:
    """The scored aggregate — every cited number — as an order-canonical tuple.

    ``caps_applied`` is compared as a SET (its list order legitimately follows
    arrival order, see guard 3); everything else is a pure fold and compared
    directly. pillar_scores is sorted by key so a (fixed-order) dict never masks
    a value change.
    """
    return (
        rep.overall_score,
        rep.grade,
        tuple(sorted((rep.pillar_scores or {}).items(), key=lambda kv: kv[0])),
        frozenset(rep.caps_applied or []),
        rep.scored,
    )


def _raw_digest(rep) -> str:
    """sha256 of the report serialized EXACTLY as to_json does (order-sensitive)."""
    d = dataclasses.asdict(rep)
    d["generated_at"] = "FIXED"  # the only intentionally time-varying field
    return hashlib.sha256(json.dumps(d, **_JSON_KW).encode("utf-8")).hexdigest()


def _canonical_digest(rep) -> str:
    """sha256 after canonicalizing the two arrival-order-following fields.

    ``checks`` (serialized in input order) and ``caps_applied`` (appended in
    arrival order) are the ONLY fields that legitimately track input order; sort
    both, fix the timestamp, and any REMAINING difference across orderings is a
    genuine order-dependence in a scored/evidence value.
    """
    d = dataclasses.asdict(rep)
    d["generated_at"] = "FIXED"
    d["checks"] = sorted(d["checks"], key=lambda c: (c["check_id"], c.get("pillar", "")))
    d["caps_applied"] = sorted(d["caps_applied"])
    return hashlib.sha256(json.dumps(d, **_JSON_KW).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 1. The scored AGGREGATE is invariant to probe/check arrival order. Every
#    fixture's real checks are scored under native + reverse + seeded-shuffle
#    orders; the cited numbers (overall/grade/pillars/cap-set/scorable) are
#    identical across all of them. A future order-sensitive aggregation reddens
#    here even though the fixed-order canonical-replay numbers stay green.
# ---------------------------------------------------------------------------
def test_scored_aggregate_is_probe_order_invariant() -> None:
    print("test_scored_aggregate_is_probe_order_invariant")
    rub = scoring.load_rubric(None)
    for domain in _POPULATION:
        checks = _real_checks(domain)
        aggs = {
            i: _aggregate(scoring.score(order, rub, domain))
            for i, order in enumerate(_orderings(checks))
        }
        distinct = {a for a in aggs.values()}
        _check(
            len(distinct) == 1,
            f"{domain}: scored aggregate identical across {len(aggs)} probe orders "
            f"(overall={next(iter(distinct))[0]}, grade={next(iter(distinct))[1]})",
        )


# ---------------------------------------------------------------------------
# 2. Once the two arrival-order-FOLLOWING fields are canonicalized, the FULL
#    serialized report is byte-identical across every order — arrival order
#    reaches only ``checks``-array and ``caps_applied`` order, nothing that
#    survives into a scored or evidence value. Non-vacuous: the RAW (un-
#    canonicalized) report genuinely DIFFERS across orders, so the canonical
#    invariance is doing real work, not comparing identical bytes.
# ---------------------------------------------------------------------------
def test_serialized_report_is_canonical_form_invariant() -> None:
    print("test_serialized_report_is_canonical_form_invariant")
    rub = scoring.load_rubric(None)
    saw_raw_difference = False
    for domain in _POPULATION:
        checks = _real_checks(domain)
        orders = _orderings(checks)
        reps = [scoring.score(order, rub, domain) for order in orders]
        canon = {_canonical_digest(r) for r in reps}
        _check(
            len(canon) == 1,
            f"{domain}: canonicalized report byte-identical across {len(orders)} "
            f"probe orders ({next(iter(canon))[:12]}…)",
        )
        raw = {_raw_digest(r) for r in reps}
        if len(checks) >= 2:
            _check(
                len(raw) > 1,
                f"{domain}: the RAW report DOES differ across orders "
                f"({len(raw)} distinct of {len(orders)}) — canonicalization is "
                f"non-vacuous (checks serialize in arrival order)",
            )
            saw_raw_difference = True
    _check(
        saw_raw_difference,
        "at least one population member has >=2 checks and a genuinely "
        "order-varying raw report (the invariance above is non-vacuous)",
    )


# ---------------------------------------------------------------------------
# 3. TEETH — the ONE latent arrival-order dependence the scorer carries, proven
#    on the REAL scorer with a synthetic two-cap input. ``caps_applied`` is
#    appended in check-arrival order (scoring.py), so with two binding caps its
#    LIST order flips forward vs reversed — while the capped ``overall`` (a min
#    over cap values) and the cap SET are invariant. This proves: (a) the scored
#    aggregate stays safe under reordering even WITH binding caps (guard 1's
#    property holds on the caps path, not just the empty-cap fixtures), and (b)
#    the SET/sorted canonicalization guards 1 and 2 use is load-bearing — a naive
#    raw-list comparison of caps_applied would flag a false regression. It never
#    bites today (no committed fixture has >=2 binding caps), and the peer-gated
#    fix (sort caps_applied in scoring.py) is queued in BACKLOG.
# ---------------------------------------------------------------------------
def test_caps_applied_list_order_is_arrival_order_dependent_teeth() -> None:
    print("test_caps_applied_list_order_is_arrival_order_dependent_teeth")
    # A minimal synthetic rubric with TWO binding caps. Single pillar so the
    # pre-cap overall is a clean 100.0, well above both cap values.
    rub = {
        "version": "teeth",
        "pillar_weights": {"access": 1.0},
        "grade_bands": [[0.0, "F"], [50.0, "C"], [90.0, "A"]],
        "caps": {"cap_a": 30.0, "cap_b": 20.0},
        "checks": [{"id": "chk_a"}, {"id": "chk_b"}],
    }
    c_a = CheckResult("chk_a", "access", Status.PASS, 10.0, 10.0, "cap_a", "")
    c_b = CheckResult("chk_b", "access", Status.PASS, 10.0, 10.0, "cap_b", "")

    fwd = scoring.score([c_a, c_b], rub, "synthetic.example")
    rev = scoring.score([c_b, c_a], rub, "synthetic.example")

    # (a) the capped overall + grade are order-invariant (min over cap values).
    _check(
        fwd.overall_score == rev.overall_score == 20.0,
        f"capped overall is order-invariant at the min cap (20.0): "
        f"fwd={fwd.overall_score} rev={rev.overall_score}",
    )
    _check(
        fwd.grade == rev.grade,
        f"grade is order-invariant under two binding caps ({fwd.grade})",
    )
    # (b) the cap SET is order-invariant — both caps bind either way.
    _check(
        set(fwd.caps_applied) == set(rev.caps_applied) == {"cap_a", "cap_b"},
        f"the binding-cap SET is order-invariant: fwd={set(fwd.caps_applied)} "
        f"rev={set(rev.caps_applied)}",
    )
    # (c) the teeth: the caps_applied LIST order genuinely FLIPS with arrival
    #     order — so an aggregate/byte comparison MUST canonicalize it (which
    #     guards 1 and 2 do). If a future scoring change sorted caps_applied,
    #     this would go green-by-equality and the BACKLOG follow-up is done.
    _check(
        fwd.caps_applied == ["cap_a", "cap_b"] and rev.caps_applied == ["cap_b", "cap_a"],
        f"caps_applied LIST order follows arrival order (fwd={fwd.caps_applied} "
        f"!= rev={rev.caps_applied}) — the latent dependence the SET/sorted "
        f"canonicalization neutralizes",
    )


# ---------------------------------------------------------------------------
# 4. The reproducibility population is EXACTLY the committed fixtures that
#    full-re-score with 0 replay-misses, and it is strictly broader than the
#    regression pair — the same self-maintaining partition
#    test_hashseed_reproducibility uses. A new full-scorable fixture (or a
#    [LOCAL] re-capture that promotes a classification-only one) is forced into
#    the guarantee; a classification-only fixture cannot sneak in.
# ---------------------------------------------------------------------------
def test_probe_order_population_is_the_replay_clean_set() -> None:
    print("test_probe_order_population_is_the_replay_clean_set")
    rub = scoring.load_rubric(None)
    committed = sorted(
        os.path.basename(p)[:-5] for p in glob.glob(os.path.join(_FIXTURE_DIR, "*.json"))
    )
    live_clean = set()
    for domain in committed:
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
        checks = _run_probes(ctx)
        scoring.score(checks, rub, domain)
        misses = sum(
            1 for res in ctx._cache.values() if res.error and "replay-miss" in res.error
        )
        if misses == 0:
            live_clean.add(domain)
    _check(
        set(_POPULATION) == live_clean,
        f"_POPULATION is exactly the 0-replay-miss committed fixtures "
        f"(pinned {sorted(_POPULATION)} vs live {sorted(live_clean)})",
    )
    _check(
        set(_CANONICAL).issubset(_POPULATION) and len(_POPULATION) > len(_CANONICAL),
        f"the population ({len(_POPULATION)}) strictly contains the regression "
        f"pair ({len(_CANONICAL)}) — the extension is non-vacuous",
    )


def main() -> int:
    tests = [
        test_scored_aggregate_is_probe_order_invariant,
        test_serialized_report_is_canonical_form_invariant,
        test_caps_applied_list_order_is_arrival_order_dependent_teeth,
        test_probe_order_population_is_the_replay_clean_set,
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
