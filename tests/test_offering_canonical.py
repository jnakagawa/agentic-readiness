"""Canonical offering-discovery guard — the operator acceptance criterion, made executable.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_offering_canonical.py

The operator directive (2026-07-23, BACKLOG P0) makes the task battery
OFFERING-RELATIVE: a site is probed only with intents for the archetypes it
actually CLAIMS to serve, and archetypes it does NOT serve are marked NA
(excluded from the completion means and both spread signals, never penalized).
The directive's stated acceptance criterion is concrete:

    "driftflight.com shows physical_good = NA (not a completion number) with
     spreads over claimed archetypes only; a retail storefront shows the inverse."

Bricks 1–3 (`asrs.offering.discover_offering` / `classify_offering`, the NA-aware
`aggregate_battery`, and `--battery auto` wiring) shipped that machinery, and it
was live-validated [LOCAL] on four real domains. But the canonical criterion —
physical_good = NA on the flight-themed storefront pair — had NO in-cloud
regression guard: it lived only in a [LOCAL] run log. This test closes that gap.

It replays each committed canonical fixture through the REAL discovery path
(`FetchContext.from_fixture -> discover_offering`, no network) and pins the
classification, so a future change to the signal bank or discovery logic that
spuriously flipped physical_good to CLAIMED on the canonical pair — the exact
pollution the operator directive removes — fails a test in-cloud instead of
shipping silently.

NON-VACUOUS by substrate: both canonical homepages are flight-/shipping-themed
and literally say "ship" three times ("for every image you ship", "Teams that
ship images daily") — all metaphorical (shipping software output, not physical
fulfillment). The physical_good signals require unambiguous fulfillment nouns
("free shipping" / "add to cart" / "in stock" / "shipping address", never bare
"ship"), so the correct answer is NA. This is precisely the precision-critical
false positive `asrs.offering` guards against, exercised on REAL captured
evidence rather than a synthetic fixture (which `tests/test_offering.py` covers).

Discovery-only: this test reads the same committed fixtures as
`tests/test_canonical_replay.py` but exercises the SCORE-NEUTRAL offering
pipeline (no check, weight, cap, or aggregation rule) — it moves no canonical
score and the rubric stays untouched.

Maintenance contract (mirrors test_canonical_replay): if a signal-bank change
LEGITIMATELY changes what a canonical domain claims, re-capture the fixtures
[LOCAL] and update EXPECTED_CLAIMED below in the SAME PR — the guard tracks
intended change, it does not forbid it. A canonical domain gaining physical_good
is NOT a legitimate change absent new fulfillment evidence: it is the regression
this guard exists to catch.

No network: discovery serves every surface from the fixture's recorded response
cache. Unlike the scoring re-score, discovery TOLERATES a missing surface by
design (a 404/error/replay-miss surface is simply absent — a site that serves
only a homepage is classified from the homepage alone), so this guard pins the
classification OUTCOME, not fixture coverage: the canonical fixtures were
captured for the scoring crawl, so a discovery-only surface (e.g. /llms-full.txt)
may legitimately be absent without changing the claimed set.
"""

from __future__ import annotations

import os
import re
import sys

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs.fetch import FetchContext  # noqa: E402
from asrs.offering import ARCHETYPES, discover_offering, strip_html  # noqa: E402

_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# What each canonical domain CLAIMS to serve, from its committed surfaces —
# validated [LOCAL] (2026-07-23T23:49Z, brick 1) on the live crawl and reproduced
# here byte-faithfully offline. Both are agent-native image-generation storefronts:
# a metered API, a subscription, and a digital good (the generated image); NEITHER
# fulfills a physical good, books a service, or is a data-retrieval product.
EXPECTED_CLAIMED = {
    "drift-flight.org": {"metered_api", "subscription", "digital_good"},
    "driftflight.com": {"metered_api", "subscription", "digital_good"},
}
# The operator directive's acceptance criterion, named explicitly: on BOTH
# canonical storefronts these archetypes are NOT offered -> NA in the battery.
_MUST_BE_NA = {"physical_good", "service_booking", "data_retrieval"}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _discover(domain: str):
    """Replay ``fixtures/canonical/<domain>.json`` through the real discovery path."""
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    return discover_offering(ctx), ctx


def _assert_offering(domain: str) -> None:
    profile, ctx = _discover(domain)
    claimed = set(profile.archetypes)
    unclaimed = set(profile.unclaimed)
    exp = EXPECTED_CLAIMED[domain]

    # Discovery drew on real evidence, not an empty/failed crawl.
    _check(
        "homepage" in profile.surfaces_seen,
        f"{domain}: homepage surface was read (discovery had real evidence)",
    )

    # (a) The claimed archetype SET is exactly the [LOCAL]-validated set. Exact
    # equality (not subset) is the regression signal: a spurious ADDED archetype
    # (the pollution the directive removes) or a DROPPED one both fail here.
    _check(
        claimed == exp,
        f"{domain}: claimed archetypes == {sorted(exp)} (got {sorted(claimed)})",
    )

    # claimed and unclaimed partition the fixed template bank exactly (no leaks).
    _check(
        claimed | unclaimed == set(ARCHETYPES) and not (claimed & unclaimed),
        f"{domain}: claimed+unclaimed partition the archetype bank "
        f"(claimed {sorted(claimed)}, unclaimed {sorted(unclaimed)})",
    )

    # (b) The operator acceptance criterion: the not-offered archetypes are NA.
    _check(
        _MUST_BE_NA <= unclaimed,
        f"{domain}: {sorted(_MUST_BE_NA)} are all NA/unclaimed "
        f"(got unclaimed {sorted(unclaimed)})",
    )
    _check(
        not profile.claims("physical_good"),
        f"{domain}: physical_good = NA (operator acceptance criterion) — "
        "an agent-native image API does not fulfill a physical good",
    )


def test_canonical_org_offering() -> None:
    print("test_canonical_org_offering")
    _assert_offering("drift-flight.org")


def test_canonical_com_offering() -> None:
    print("test_canonical_com_offering")
    _assert_offering("driftflight.com")


# ---------------------------------------------------------------------------
# Non-vacuity: physical_good stays NA DESPITE real metaphorical "ship" prose.
# This is the precision-critical false positive `asrs.offering` is built to
# avoid, exercised on the REAL captured homepage (not a synthetic surface): the
# flight-themed storefronts say "ship" (metaphorically — shipping images), which
# a naive classifier would read as physical fulfillment. If a future signal-bank
# change relaxed the physical_good anchors to match bare "ship", THIS test — and
# the acceptance guards above — would catch it on the canonical pair.
# ---------------------------------------------------------------------------
_BARE_SHIP_RE = re.compile(r"\bship(s|ping|ped)?\b", re.IGNORECASE)


def _assert_metaphorical_ship_not_physical(domain: str) -> None:
    profile, ctx = _discover(domain)
    home = ctx.homepage(ua="browser")
    prose = strip_html(getattr(home, "text", "") or "")

    # The substrate really does contain the trap word (else the test is vacuous).
    _check(
        bool(_BARE_SHIP_RE.search(prose)),
        f"{domain}: homepage prose contains metaphorical 'ship' (the trap word)",
    )
    # ...yet none of it counts as physical fulfillment.
    _check(
        not profile.claims("physical_good"),
        f"{domain}: metaphorical 'ship' does NOT trip physical_good "
        "(precision guard holds on real captured evidence)",
    )


def test_canonical_metaphorical_ship_stays_na_org() -> None:
    print("test_canonical_metaphorical_ship_stays_na_org")
    _assert_metaphorical_ship_not_physical("drift-flight.org")


def test_canonical_metaphorical_ship_stays_na_com() -> None:
    print("test_canonical_metaphorical_ship_stays_na_com")
    _assert_metaphorical_ship_not_physical("driftflight.com")


def main() -> int:
    tests = [
        test_canonical_org_offering,
        test_canonical_com_offering,
        test_canonical_metaphorical_ship_stays_na_org,
        test_canonical_metaphorical_ship_stays_na_com,
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
