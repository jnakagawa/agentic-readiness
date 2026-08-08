"""Hash-seed reproducibility of the committed static evidence (TRUTH track).

Runnable directly, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_hashseed_reproducibility.py

Invariant #3 is "evidence or it didn't happen": every scored claim travels to
committed artifacts (reports, transcripts) as the serialized ``Report.to_json``.
For that committed evidence to be REPRODUCIBLE — the same fixture re-scored on
another machine/process yielding the byte-identical report — the serialization
must not depend on anything the process chooses at startup.

The behavioral half of this reproducibility question is closed along the
ARRIVAL-ORDER axis: Cycles 253/255/257/262 sorted every panel-arrival-ordered
evidence projection (shopper ``by_run`` / ``block_statements`` / ``refusing_
models`` / trust ``per_model``) so a panel re-run in a different arrival order
quotes byte-identical evidence. This suite closes the sibling axis on the STATIC
scoring path: ``PYTHONHASHSEED``. Python randomizes ``str``/``bytes`` hashing per
process (PEP 456), so **set iteration order over strings varies from run to
run**. A probe that ever emitted ``list(a_set_of_strings)`` into a CheckResult's
evidence would leave the SCORE untouched (scoring is count-based, so every
number-pinning guard in test_canonical_replay stays green) while making the
committed evidence bytes differ between two machines scoring the same fixture —
a silent reproducibility regression exactly analogous to the arrival-order leaks.

Today the property HOLDS (the offering/probe layers project sets through
``sorted(...)`` or use them only for membership tests, and ``AI_CRAWLERS`` is a
tuple). This suite converts that from an assumed property into a VERIFIED,
per-cycle one: it re-scores the canonical pair in SUBPROCESSES under several
distinct ``PYTHONHASHSEED`` values (the only way to vary the seed — it is fixed
at interpreter startup) and asserts the full serialized report is byte-identical
across every seed. The moment a future probe introduces a hash-seed-dependent
evidence projection, this suite reddens even though the canonical numbers do not.

Off the scoring path, tests-only: rubric version, probes, and the canonical
delta are untouched. The detector's teeth are proven with a committed injection
(a real ``list(set(...))`` payload that DOES reorder across the pinned seeds),
so the invariance above cannot vacuously pass.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import subprocess
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# The regression-signal pair. Two structurally different API storefronts (with
# vs without agent-native rails) exercise the richest probe set — x402, commerce
# manifests, protocol discovery — so they are the surface most likely to grow a
# set-backed evidence projection. Named by capability role, never special-cased.
_CANONICAL = ("driftflight.com", "drift-flight.org")

# The FULL reproducibility population: every committed fixture that covers the
# whole current probe set (0 replay-misses), so a full re-score is faithful. The
# canonical pair is only the two API storefronts; the retail catalog
# (books.toscrape.com), the appointment-booking SaaS (acuityscheduling.com), the
# physical-goods retailer (www.moleskine.com) and the null storefront
# (example.com) each fire probe paths — add-to-cart/stock, service-booking
# surfaces, returns/fulfillment prose — that the API pair NEVER exercises. A
# hash-seed-dependent evidence projection living on one of THOSE paths would slip
# past a pair-only guard; guard 1 below re-scores every one of them.
#
# This mirrors the replay-integrity partition in test_canonical_replay
# (``_REPLAY_CLEAN``): a classification-only fixture (www.allbirds.com /
# simplybook.me / polar.sh) records only a SUBSET of the
# scoring surface, so a full re-score misses dozens of requests — those are NOT
# faithful re-scores and are excluded here. Guard 5 pins this set to the
# LIVE-computed 0-miss set so a future [LOCAL] full-score re-capture that promotes
# a fixture forces its inclusion here (the guard reddens until it is added),
# never leaving reproducibility coverage silently behind the fixture population.
# ipinfo.io (Local cycle 20260807T094104Z) and api.replicate.com (Local cycle
# 20260807T114104Z) were promoted this way: re-captured full-score and added below.
_POPULATION = (
    "acuityscheduling.com",
    "api.replicate.com",
    "api.x402oracle.com",
    "books.toscrape.com",
    "drift-flight.org",
    "driftflight.com",
    "exa.ai",
    "example.com",
    "ipinfo.io",
    "thebotwire.com",
    "www.moleskine.com",
)


def _committed_domains() -> list[str]:
    """Every committed canonical fixture, by bare domain, sorted."""
    return sorted(
        os.path.basename(p)[:-5]
        for p in glob.glob(os.path.join(_FIXTURE_DIR, "*.json"))
    )


def _replay_miss_count(domain: str) -> int:
    """In-process full re-score of a committed fixture; count replay-misses.

    A miss means a probe requested a URL the fixture never recorded — i.e. the
    fixture does not cover the full scoring surface, so a full re-score of it is
    NOT faithful. This is the same replay-miss signal test_canonical_replay uses
    to partition the population; computed here so guard 5 is self-verifying.
    """
    sys.path.insert(0, _REPO_ROOT)
    from asrs import scoring
    from asrs.cli import _run_probes
    from asrs.fetch import FetchContext

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
    checks = _run_probes(ctx)
    scoring.score(checks, scoring.load_rubric(None), domain)
    return sum(
        1 for res in ctx._cache.values()
        if res.error and "replay-miss" in res.error
    )

# Distinct hash seeds. 0 and 1 are pinned as the teeth basis below (a synthetic
# string set is empirically verified to reorder between them); the extras widen
# the net for the real reports without changing the property being asserted.
_SEEDS = ("0", "1", "2", "12345")

# A synthetic evidence-like payload for the teeth test. Eight short AI-agent
# UA tokens: enough distinct strings that ``list(set(...))`` iteration order
# DIFFERS between PYTHONHASHSEED=0 and =1 (verified deterministically — the order
# is a pure function of (seed, contents)). This is the exact shape a careless
# probe would emit: a set projected to a list without sorting.
_TEETH_STRINGS = [
    "gptbot", "claudebot", "perplexitybot", "oai-searchbot",
    "google-extended", "bingbot", "ccbot", "amazonbot",
]

# Serialization params MUST mirror Report.to_json (asrs/types.py) so the teeth
# exercise the same serialization path the real reports use.
_JSON_KW = dict(indent=2, default=str)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run_seeded(payload: str, seed: str, extra_env: dict | None = None) -> str:
    """Run ``payload`` in a fresh interpreter under PYTHONHASHSEED=seed.

    Returns the subprocess stdout (stripped). Raises loudly on a non-zero exit
    or empty output so a crashing child can never masquerade as "invariant".
    """
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = seed
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "-c", payload],
        capture_output=True, text=True, env=env, cwd=_REPO_ROOT,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"seeded subprocess (PYTHONHASHSEED={seed}) failed rc={proc.returncode}: "
            f"{proc.stderr.strip()[-400:]}"
        )
    out = proc.stdout.strip()
    if not out:
        raise AssertionError(f"seeded subprocess (PYTHONHASHSEED={seed}) produced no output")
    return out


# The child that re-scores one canonical fixture and prints the sha256 of the
# full serialized report with the ONE non-reproducible field (the wall-clock
# timestamp) pinned, so only evidence ORDERING can move the digest.
_SCORE_CHILD = r"""
import hashlib, os, sys
sys.path.insert(0, os.environ["ASRS_HS_ROOT"])
from asrs import scoring
from asrs.cli import _run_probes
from asrs.fetch import FetchContext
ctx = FetchContext.from_fixture(os.environ["ASRS_HS_PATH"])
checks = _run_probes(ctx)
rep = scoring.score(checks, scoring.load_rubric(None), os.environ["ASRS_HS_DOMAIN"])
rep.generated_at = "FIXED"          # the only intentionally time-varying field
sys.stdout.write(hashlib.sha256(rep.to_json().encode("utf-8")).hexdigest())
"""


def _report_digest(domain: str, seed: str) -> str:
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    env = {"ASRS_HS_ROOT": _REPO_ROOT, "ASRS_HS_PATH": path, "ASRS_HS_DOMAIN": domain}
    out = _run_seeded(_SCORE_CHILD, seed, extra_env=env)
    _check_is_digest(out, f"{domain}@seed{seed}")
    return out


def _check_is_digest(s: str, label: str) -> None:
    if len(s) != 64 or any(c not in "0123456789abcdef" for c in s):
        raise AssertionError(f"{label}: expected a sha256 hex digest, got {s!r}")


# ---------------------------------------------------------------------------
# 1. The committed static report is byte-identical across hash seeds — the
#    static-path sibling of the arrival-order reproducibility guards. Re-scoring
#    ANY full-scorable committed fixture under any PYTHONHASHSEED serializes the
#    SAME report. Covers the whole replay-clean population, not just the API
#    pair, so a set-backed evidence projection on a retail / booking / null probe
#    path is caught too.
# ---------------------------------------------------------------------------
def test_committed_report_serialization_is_hashseed_invariant() -> None:
    print("test_committed_report_serialization_is_hashseed_invariant")
    for domain in _POPULATION:
        digests = {seed: _report_digest(domain, seed) for seed in _SEEDS}
        distinct = set(digests.values())
        _check(
            len(distinct) == 1,
            f"{domain}: serialized report byte-identical across "
            f"{len(_SEEDS)} hash seeds {list(_SEEDS)} "
            f"(digests: { {s: d[:12] + '…' for s, d in digests.items()} })",
        )


# ---------------------------------------------------------------------------
# 2. The pair's reproducibility is JOINT — both regression-signal storefronts
#    reproduce, so a leak on EITHER side (with-rails or no-rails) is caught, not
#    only on whichever domain a spot check happened to pick.
# ---------------------------------------------------------------------------
def test_both_regression_signal_sides_reproduce() -> None:
    print("test_both_regression_signal_sides_reproduce")
    # Each domain's own digest is seed-stable (guard 1), AND the two domains
    # produce DISTINCT reports (non-vacuous: we are comparing two real, different
    # scores, not the same empty report twice).
    per_domain = {}
    for domain in _CANONICAL:
        s0, s1 = _report_digest(domain, "0"), _report_digest(domain, "1")
        _check(s0 == s1, f"{domain}: digest seed-stable ({s0[:12]}… == {s1[:12]}…)")
        per_domain[domain] = s0
    _check(
        len(set(per_domain.values())) == len(_CANONICAL),
        f"the two sides serialize to DISTINCT reports (non-vacuous): {per_domain}",
    )


# ---------------------------------------------------------------------------
# 3. TEETH — the subprocess digest-diff mechanism actually catches a hash-seed-
#    dependent serialization, and sorting is the fix. Had a probe emitted
#    ``list(a_set)`` into evidence, guard 1 would redden; this proves it, without
#    touching the real scorer. A leaky payload (set projected to a list) is
#    serialized under the SAME json params Report.to_json uses, in two children
#    at seeds 0 and 1: its digest DIFFERS (the leak is detectable). The sorted
#    payload over the identical contents is INVARIANT (the fix works).
# ---------------------------------------------------------------------------
_TEETH_CHILD = r"""
import hashlib, json, os, sys
STRINGS = json.loads(os.environ["ASRS_HS_STRINGS"])
if sys.argv[1] == "leaky":
    payload = {"agents": list(set(STRINGS))}      # hash-seed-dependent order
else:
    payload = {"agents": sorted(set(STRINGS))}    # order-invariant (the fix)
blob = json.dumps(payload, indent=2, default=str).encode("utf-8")
sys.stdout.write(hashlib.sha256(blob).hexdigest())
"""


def _teeth_digest(kind: str, seed: str) -> str:
    env = {"ASRS_HS_STRINGS": json.dumps(_TEETH_STRINGS)}
    # kind is passed as argv[1]; embed it by wrapping the child invocation.
    payload = _TEETH_CHILD.replace("sys.argv[1]", repr(kind))
    out = _run_seeded(payload, seed, extra_env=env)
    _check_is_digest(out, f"teeth-{kind}@seed{seed}")
    return out


def test_hashseed_guard_has_teeth() -> None:
    print("test_hashseed_guard_has_teeth")
    # Sanity: the very construct a careless probe would use — list(set(...)) —
    # genuinely reorders across the two pinned seeds when serialized the same
    # way Report.to_json serializes evidence. If this ever stopped differing,
    # the teeth would be vacuous, so assert the DIFFERENCE explicitly.
    leaky0, leaky1 = _teeth_digest("leaky", "0"), _teeth_digest("leaky", "1")
    _check(
        leaky0 != leaky1,
        "a set-backed evidence projection serializes DIFFERENTLY across seeds "
        f"0 vs 1 ({leaky0[:12]}… != {leaky1[:12]}…) — guard 1's mechanism has teeth",
    )
    # And the fix — sorting the same set — is invariant across the same seeds.
    sorted0, sorted1 = _teeth_digest("sorted", "0"), _teeth_digest("sorted", "1")
    _check(
        sorted0 == sorted1,
        "the sorted projection over the identical contents is seed-INVARIANT "
        f"({sorted0[:12]}… == {sorted1[:12]}…) — sorting is the fix the guard rewards",
    )


# ---------------------------------------------------------------------------
# 4. The child actually exercised the REAL scorer — a guard against the whole
#    suite silently passing because the subprocess no-op'd. Confirm the digest
#    a child computes matches an IN-PROCESS serialization of the same report
#    (this runner's own seed), so the children are scoring, not echoing.
# ---------------------------------------------------------------------------
def test_child_digest_matches_in_process_score() -> None:
    print("test_child_digest_matches_in_process_score")
    sys.path.insert(0, _REPO_ROOT)
    from asrs import scoring
    from asrs.cli import _run_probes
    from asrs.fetch import FetchContext

    domain = _CANONICAL[0]
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    checks = _run_probes(ctx)
    rep = scoring.score(checks, scoring.load_rubric(None), domain)
    rep.generated_at = "FIXED"
    in_proc = hashlib.sha256(rep.to_json().encode("utf-8")).hexdigest()

    child = _report_digest(domain, "0")
    _check(
        in_proc == child,
        f"{domain}: in-process digest matches the seeded child's "
        f"({in_proc[:12]}… == {child[:12]}…) — children score the real pipeline",
    )


# ---------------------------------------------------------------------------
# 5. The reproducibility population is EXACTLY the set of committed fixtures that
#    faithfully full-re-score (0 replay-misses), and it is strictly broader than
#    the regression pair. This makes guard 1's coverage self-maintaining:
#      - a NEW full-scorable fixture (or a [LOCAL] re-capture that promotes a
#        classification-only one to full coverage) is NOT in _POPULATION → this
#        reddens, forcing it into the hash-seed guarantee rather than letting
#        coverage silently lag the fixture population;
#      - a classification-only fixture cannot sneak in — it misses under the full
#        scorer, so it is excluded from the live set and _POPULATION alike.
#    Non-vacuity: _POPULATION strictly contains the canonical pair (the extension
#    genuinely reaches beyond the two API storefronts).
# ---------------------------------------------------------------------------
def test_reproducibility_population_is_the_replay_clean_set() -> None:
    print("test_reproducibility_population_is_the_replay_clean_set")
    committed = _committed_domains()
    live_clean = {d for d in committed if _replay_miss_count(d) == 0}
    _check(
        set(_POPULATION) == live_clean,
        f"_POPULATION is exactly the committed fixtures that full-re-score "
        f"with 0 replay-misses (pinned {sorted(_POPULATION)} vs live "
        f"{sorted(live_clean)}) — promote/re-capture forces inclusion",
    )
    _check(
        set(_CANONICAL).issubset(_POPULATION),
        f"the regression pair {sorted(_CANONICAL)} is inside the population",
    )
    _check(
        len(_POPULATION) > len(_CANONICAL),
        f"the population ({len(_POPULATION)}) is strictly broader than the pair "
        f"({len(_CANONICAL)}) — the extension is non-vacuous",
    )


def main() -> int:
    tests = [
        test_committed_report_serialization_is_hashseed_invariant,
        test_both_regression_signal_sides_reproduce,
        test_hashseed_guard_has_teeth,
        test_child_digest_matches_in_process_score,
        test_reproducibility_population_is_the_replay_clean_set,
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
