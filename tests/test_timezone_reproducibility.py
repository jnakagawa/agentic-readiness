"""Timezone / wall-clock reproducibility of the committed static evidence (METHOD track).

Runnable directly, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_timezone_reproducibility.py

Invariant #3 is "evidence or it didn't happen": every scored claim travels to
committed artifacts as the serialized ``Report.to_json``. For that committed
evidence to be REPRODUCIBLE — the same fixture re-scored on another machine
yielding the byte-identical report — the serialization must not depend on
anything the HOST ENVIRONMENT chooses. Cycle 267 closed the ``PYTHONHASHSEED``
axis of that guarantee (set-iteration order over strings, PEP 456). This suite
closes the SIBLING host-environment axis: the system CLOCK and TIMEZONE.

The scoring path reads the wall clock in exactly one place per report —
``scoring.score`` stamps ``generated_at`` — and it reads it as EXPLICIT UTC
(``datetime.now(timezone.utc)``); every other clock/date read in the codebase
(``report``'s render timestamp, ``canonical_history``'s ``strptime``, ``cli``'s
history writer) is likewise explicit-UTC or explicit-``%Y%m%dT%H%M%SZ``. So the
SCORE and all scored evidence are invariant to the machine's ``TZ`` today — but
that is an ASSUMED property, never verified, exactly the situation the hash-seed
suite converted for its axis. The moment a future probe derives a scored datum
from LOCAL wall-clock instead of explicit UTC — a "freshness"/"cache-age" leg
computed from ``date.today()``, a naive ``datetime.now()`` offset/tzname string,
an evidence timestamp formatted in local time — a report scored in ``Asia/
Kolkata`` (+05:30) or on the +14/-12 date-line fringes would differ from one
scored in UTC, and this suite reddens even though the canonical NUMBERS do not.

This suite re-scores the canonical pair in SUBPROCESSES under several distinct
``TZ`` values (the only way to vary the interpreter's notion of local time — the
C library reads ``TZ`` at ``tzset()``) and asserts the full serialized report is
byte-identical across every zone. The zones are picked to MAXIMIZE divergence: a
fractional offset (+05:30, catches naive local formatting) and the two date-line
extremes (+14 / -12, so a ``date.today()`` leak flips the calendar date at nearly
any UTC instant). The one intentionally time-varying field, ``generated_at``, is
pinned to a constant before hashing — so ONLY a genuine local-time-dependent
evidence projection can move the digest.

Off the scoring path, tests-only: rubric version, probes, and the canonical
delta are untouched. The detector's teeth are proven with a committed payload
(a real ``datetime.now().astimezone()`` offset string that DOES differ across the
pinned zones), so the invariance above cannot vacuously pass.
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
# vs without agent-native rails) exercise the richest probe set, so they are the
# surface most likely to grow a wall-clock-backed evidence projection. Named by
# capability role, never special-cased.
_CANONICAL = ("driftflight.com", "drift-flight.org")

# The FULL reproducibility population: every committed fixture that covers the
# whole current probe set (0 replay-misses), so a full re-score is faithful. The
# canonical pair is only the two API storefronts; the retail catalog
# (books.toscrape.com), the appointment-booking SaaS (acuityscheduling.com), the
# physical-goods retailer (www.moleskine.com) and the null storefront
# (example.com) each fire probe paths — add-to-cart/stock, service-booking
# surfaces, returns/fulfillment prose — that the API pair NEVER exercises. A
# local-wall-clock-dependent evidence projection living on one of THOSE paths
# would slip past a pair-only guard; guard 1 below re-scores every one of them.
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
    "checkout.coffeecircle.com",
    "drift-flight.org",
    "driftflight.com",
    "exa.ai",
    "example.com",
    "gymshark.com",
    "hardgraft.com",
    "ipinfo.io",
    "thebotwire.com",
    "www.moleskine.com",
    "x402deploy.vercel.app",
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

# Distinct timezones as POSIX ``TZ`` strings (interpreted by the C library with
# NO tzdata dependency, so the guard runs on a minimal container). POSIX sign is
# INVERTED — "IST-5:30" means UTC+05:30. Chosen to maximize divergence from UTC:
#   UTC0      the reference
#   IST-5:30  a fractional offset (catches naive local date/time FORMATTING)
#   LINT-14   UTC+14 (Line Islands) — local "today" runs AHEAD of the UTC date
#   AoE12     UTC-12 (Anywhere-on-Earth) — local "today" runs BEHIND the UTC date
# All four are fixed-offset (no DST rule) so each zone's offset is itself a
# constant, keeping the teeth below a pure function of TZ, not of the instant.
_ZONES = ("UTC0", "IST-5:30", "LINT-14", "AoE12")

# Serialization params MUST mirror Report.to_json (asrs/types.py) so the teeth
# exercise the same serialization path the real reports use.
_JSON_KW = dict(indent=2, default=str)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run_in_zone(payload: str, tz: str, extra_env: dict | None = None) -> str:
    """Run ``payload`` in a fresh interpreter under TZ=tz.

    Returns the subprocess stdout (stripped). Raises loudly on a non-zero exit
    or empty output so a crashing child can never masquerade as "invariant".
    """
    env = dict(os.environ)
    env["TZ"] = tz
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "-c", payload],
        capture_output=True, text=True, env=env, cwd=_REPO_ROOT,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"zoned subprocess (TZ={tz}) failed rc={proc.returncode}: "
            f"{proc.stderr.strip()[-400:]}"
        )
    out = proc.stdout.strip()
    if not out:
        raise AssertionError(f"zoned subprocess (TZ={tz}) produced no output")
    return out


# The child that re-scores one canonical fixture and prints the sha256 of the
# full serialized report with the ONE non-reproducible field (the wall-clock
# timestamp) pinned, so only a genuine local-time-dependent evidence projection
# can move the digest. ``time.tzset()`` activates the injected TZ before scoring,
# so the zone is LIVE for every clock/date read the probes make.
_SCORE_CHILD = r"""
import hashlib, os, sys, time
time.tzset()
sys.path.insert(0, os.environ["ASRS_TZ_ROOT"])
from asrs import scoring
from asrs.cli import _run_probes
from asrs.fetch import FetchContext
ctx = FetchContext.from_fixture(os.environ["ASRS_TZ_PATH"])
checks = _run_probes(ctx)
rep = scoring.score(checks, scoring.load_rubric(None), os.environ["ASRS_TZ_DOMAIN"])
rep.generated_at = "FIXED"          # the only intentionally time-varying field
sys.stdout.write(hashlib.sha256(rep.to_json().encode("utf-8")).hexdigest())
"""


def _report_digest(domain: str, tz: str) -> str:
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    env = {"ASRS_TZ_ROOT": _REPO_ROOT, "ASRS_TZ_PATH": path, "ASRS_TZ_DOMAIN": domain}
    out = _run_in_zone(_SCORE_CHILD, tz, extra_env=env)
    _check_is_digest(out, f"{domain}@{tz}")
    return out


def _check_is_digest(s: str, label: str) -> None:
    if len(s) != 64 or any(c not in "0123456789abcdef" for c in s):
        raise AssertionError(f"{label}: expected a sha256 hex digest, got {s!r}")


# ---------------------------------------------------------------------------
# 1. The committed static report is byte-identical across timezones — the
#    host-environment sibling of the hash-seed reproducibility guard. Re-scoring
#    ANY full-scorable committed fixture under any TZ serializes the SAME report.
#    Covers the whole replay-clean population, not just the API pair, so a
#    local-wall-clock projection on a retail / booking / null probe path is
#    caught too.
# ---------------------------------------------------------------------------
def test_committed_report_serialization_is_timezone_invariant() -> None:
    print("test_committed_report_serialization_is_timezone_invariant")
    for domain in _POPULATION:
        digests = {tz: _report_digest(domain, tz) for tz in _ZONES}
        distinct = set(digests.values())
        _check(
            len(distinct) == 1,
            f"{domain}: serialized report byte-identical across "
            f"{len(_ZONES)} timezones {list(_ZONES)} "
            f"(digests: { {tz: d[:12] + '…' for tz, d in digests.items()} })",
        )


# ---------------------------------------------------------------------------
# 2. The pair's reproducibility is JOINT — both regression-signal storefronts
#    reproduce, so a leak on EITHER side (with-rails or no-rails) is caught, not
#    only on whichever domain a spot check happened to pick.
# ---------------------------------------------------------------------------
def test_both_regression_signal_sides_reproduce() -> None:
    print("test_both_regression_signal_sides_reproduce")
    # Each domain's own digest is zone-stable (guard 1), AND the two domains
    # produce DISTINCT reports (non-vacuous: we are comparing two real, different
    # scores, not the same empty report twice).
    per_domain = {}
    for domain in _CANONICAL:
        a, b = _report_digest(domain, "UTC0"), _report_digest(domain, "LINT-14")
        _check(a == b, f"{domain}: digest zone-stable ({a[:12]}… == {b[:12]}…)")
        per_domain[domain] = a
    _check(
        len(set(per_domain.values())) == len(_CANONICAL),
        f"the two sides serialize to DISTINCT reports (non-vacuous): "
        f"{ {d: h[:12] + '…' for d, h in per_domain.items()} }",
    )


# ---------------------------------------------------------------------------
# 3. TEETH — the subprocess digest-diff mechanism actually catches a local-time-
#    dependent serialization, and reading explicit UTC is the fix. Had a probe
#    emitted a naive ``datetime.now().astimezone()`` offset/tzname into evidence,
#    guard 1 would redden; this proves it, without touching the real scorer. The
#    leaky payload reads the LOCAL wall-clock offset; the fixed payload reads
#    explicit UTC — both serialized under the SAME json params Report.to_json
#    uses, in children under two zones whose offsets differ. The leaky digest
#    DIFFERS (the leak is detectable); the UTC digest is INVARIANT (the fix).
# ---------------------------------------------------------------------------
_TEETH_CHILD = r"""
import hashlib, json, os, sys, time
from datetime import datetime, timezone
time.tzset()
if sys.argv[1] == "leaky":
    val = datetime.now().astimezone().strftime("%z")   # LOCAL offset: +0000/+0530/+1400/-1200
else:
    val = datetime.now(timezone.utc).strftime("%z")    # explicit UTC: always +0000 (the fix)
payload = {"stamp": val}
blob = json.dumps(payload, indent=2, default=str).encode("utf-8")
sys.stdout.write(hashlib.sha256(blob).hexdigest())
"""


def _teeth_digest(kind: str, tz: str) -> str:
    # kind is passed as argv[1]; embed it by wrapping the child invocation.
    payload = _TEETH_CHILD.replace("sys.argv[1]", repr(kind))
    out = _run_in_zone(payload, tz)
    _check_is_digest(out, f"teeth-{kind}@{tz}")
    return out


def test_timezone_guard_has_teeth() -> None:
    print("test_timezone_guard_has_teeth")
    # Sanity: the very construct a careless probe would use — a naive local
    # ``astimezone()`` offset — genuinely differs across two zones when
    # serialized the same way Report.to_json serializes evidence. If this ever
    # stopped differing, the teeth would be vacuous, so assert the DIFFERENCE.
    leaky_utc, leaky_lint = _teeth_digest("leaky", "UTC0"), _teeth_digest("leaky", "LINT-14")
    _check(
        leaky_utc != leaky_lint,
        "a local-wall-clock offset serializes DIFFERENTLY across UTC vs +14 "
        f"({leaky_utc[:12]}… != {leaky_lint[:12]}…) — guard 1's mechanism has teeth",
    )
    # And the fix — reading explicit UTC — is invariant across the same zones.
    fixed_utc, fixed_lint = _teeth_digest("fixed", "UTC0"), _teeth_digest("fixed", "LINT-14")
    _check(
        fixed_utc == fixed_lint,
        "the explicit-UTC stamp is zone-INVARIANT across UTC vs +14 "
        f"({fixed_utc[:12]}… == {fixed_lint[:12]}…) — explicit UTC is the fix the guard rewards",
    )


# ---------------------------------------------------------------------------
# 4. The child actually exercised the REAL scorer — a guard against the whole
#    suite silently passing because the subprocess no-op'd. Confirm the digest
#    a child computes matches an IN-PROCESS serialization of the same report
#    (this runner's own zone), so the children are scoring, not echoing.
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

    child = _report_digest(domain, "UTC0")
    _check(
        in_proc == child,
        f"{domain}: in-process digest matches the zoned child's "
        f"({in_proc[:12]}… == {child[:12]}…) — children score the real pipeline",
    )


# ---------------------------------------------------------------------------
# 5. The reproducibility population is EXACTLY the set of committed fixtures that
#    faithfully full-re-score (0 replay-misses), and it is strictly broader than
#    the regression pair. This makes guard 1's coverage self-maintaining:
#      - a NEW full-scorable fixture (or a [LOCAL] re-capture that promotes a
#        classification-only one to full coverage) is NOT in _POPULATION → this
#        reddens, forcing it into the timezone guarantee rather than letting
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
        test_committed_report_serialization_is_timezone_invariant,
        test_both_regression_signal_sides_reproduce,
        test_timezone_guard_has_teeth,
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
