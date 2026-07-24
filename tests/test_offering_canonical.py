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
import tempfile

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

import asrs.offering as _offering  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.offering import (  # noqa: E402
    ARCHETYPES,
    ArchetypeClaim,
    ArchetypeSignal,
    discover_offering,
    strip_html,
)

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


# ---------------------------------------------------------------------------
# Vendor-neutrality of the OFFERING classifier — domain-relabeling invariance.
#
# `tests/test_canonical_replay.py` (Cycle 21) made vendor-neutrality an executable
# tripwire for the SCORING path: relabel a canonical fixture's host everywhere and
# the overall/pillars/per-check-status are identical, proving the +39.4 rests on
# EVIDENCE, not the storefront's IDENTITY. The OFFERING classifier — which drives
# the operator directive's task SELECTION (which archetypes get intents) and NA
# semantics (which are excluded from every mean/spread, never penalized) — carried
# no such guard, even though `classify_offering(domain, surfaces)` takes the domain
# as an argument and the host string appears inside the classifier's own matched
# evidence (e.g. the `metered_api` "post-endpoint" quote is `POST https://<host>/…`).
# If classification ever keyed on the domain — a favorable OR hostile special-case —
# a site's TASK SET (and thus which archetypes it is judged on vs excused as NA)
# would depend on its NAME, not what it actually claims to sell. That is exactly the
# vendor-rigging the directive's "vendor-neutral, never a vendor or domain string"
# boundary forbids, applied to the battery-selection layer.
#
# This relabels each canonical fixture's host to a neutral placeholder — request
# keys AND response bytes together, a whole-fixture string sub (so a body-embedded
# absolute URL still resolves against the rewritten cache), written to a temp file
# and replayed through the REAL `FetchContext.from_fixture -> discover_offering`
# path — and asserts the CLAIMED archetype list (ordered — order drives the fixed
# template-bank task order for cross-site comparability) and the UNCLAIMED/NA set
# are IDENTICAL to the un-relabeled discovery. Renaming the shop changes nothing.
#
# NON-VACUOUS by substrate: the base discovery's own evidence quotes contain the
# host (asserted below), so the relabel genuinely changes the text the classifier
# reads; the neutral host is a different LENGTH and carries no archetype-signal
# word, so invariance is neither a same-length coincidence nor a neutral-host
# artifact. And `test_offering_relabel_negative_control` proves the assertion has
# teeth: a monkeypatched identity-keyed special-case IS caught by it.
# ---------------------------------------------------------------------------
_NEUTRAL_HOST = "vendor-neutral.test"  # reserved .test TLD; no archetype-signal word


def _discover_relabeled(domain: str, new_host: str):
    """Replay ``<domain>.json`` with its host relabeled to ``new_host`` everywhere.

    The substitution rewrites the stored ``domain`` field, request keys, and
    response bytes together, so ``FetchContext.from_fixture`` reconstructs a
    context whose ``domain`` is ``new_host`` and whose cache serves the same
    surfaces byte-identically up to the host label. A vendor-neutral classifier
    must reproduce the un-relabeled claimed/unclaimed partition.
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    relabeled = raw.replace(domain, new_host)
    _check(
        domain not in relabeled,
        f"{domain}: every occurrence of the original host was relabeled",
    )
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    try:
        tmp.write(relabeled)
        tmp.close()
        ctx = FetchContext.from_fixture(tmp.name)
        return discover_offering(ctx)
    finally:
        os.unlink(tmp.name)


def _assert_offering_relabel_invariant(domain: str) -> None:
    base, _ = _discover(domain)
    exp = EXPECTED_CLAIMED[domain]

    # Non-vacuity: the classifier's OWN matched evidence contains the host, so
    # relabeling genuinely changes the text classification reads (not a no-op).
    host_in_evidence = any(
        domain in s.quote for c in base.claimed for s in c.signals
    )
    _check(
        host_in_evidence,
        f"{domain}: the host appears in the classifier's matched evidence "
        "(relabeling genuinely changes classifier input — the test is non-vacuous)",
    )

    relab = _discover_relabeled(domain, _NEUTRAL_HOST)

    # Ordered claimed list identical — order is the fixed template-bank task order
    # (cross-site comparability), so an order flip would reorder the battery too.
    _check(
        relab.archetypes == base.archetypes,
        f"{domain}: claimed archetypes (ordered) invariant under relabel "
        f"(base {base.archetypes}, relabel {relab.archetypes})",
    )
    # ...and equal to the [LOCAL]-validated set, re-affirming it through the
    # relabeled path (mirrors the scoring relabel guard re-affirming the number).
    _check(
        set(relab.archetypes) == exp,
        f"{domain}: relabeled claimed set == {sorted(exp)} "
        f"(got {sorted(set(relab.archetypes))})",
    )
    # The NA set (excluded from every mean/spread, never penalized) is invariant —
    # the operator directive's NA assignment depends on evidence, not identity.
    _check(
        set(relab.unclaimed) == set(base.unclaimed),
        f"{domain}: NA/unclaimed set invariant under relabel "
        f"(base {sorted(base.unclaimed)}, relabel {sorted(relab.unclaimed)})",
    )


def test_offering_relabel_invariance_org() -> None:
    print("test_offering_relabel_invariance_org")
    _assert_offering_relabel_invariant("drift-flight.org")


def test_offering_relabel_invariance_com() -> None:
    print("test_offering_relabel_invariance_com")
    _assert_offering_relabel_invariant("driftflight.com")


def test_offering_relabel_negative_control() -> None:
    """The invariance assertion has teeth: an identity-keyed special-case is caught.

    Monkeypatch a FAVORABLE special-case into the classifier — when the domain is
    the canonical storefront's identity, force-add a ``physical_good`` claim it did
    not earn from evidence. The base (canonical-host) discovery then claims
    physical_good; the relabeled (neutral-host) discovery does not — so the claimed
    sets DIVERGE, which is exactly what ``_assert_offering_relabel_invariant`` asserts
    against. If relabel-invariance were vacuous (e.g. discovery ignored the input, or
    the relabel were a no-op) this divergence would NOT appear and the guard would be
    worthless. Restores the real classifier in a finally block.
    """
    print("test_offering_relabel_negative_control")
    real = _offering.classify_offering

    def rigged(domain, surfaces):
        prof = real(domain, surfaces)
        # Keyed on the storefront's IDENTITY, not its evidence — the anti-pattern.
        if "driftflight" in domain.replace("-", "") and not prof.claims("physical_good"):
            prof.claimed.append(
                ArchetypeClaim(
                    archetype="physical_good",
                    signals=[
                        ArchetypeSignal(
                            archetype="physical_good",
                            surface="homepage",
                            label="rigged-identity",
                            quote="special-cased on domain identity",
                        )
                    ],
                )
            )
        return prof

    _offering.classify_offering = rigged
    try:
        base, _ = _discover("driftflight.com")
        relab = _discover_relabeled("driftflight.com", _NEUTRAL_HOST)
        _check(
            base.claims("physical_good"),
            "rig active: base (canonical identity) is special-cased to claim physical_good",
        )
        _check(
            not relab.claims("physical_good"),
            "neutral-host run is NOT special-cased (classification keyed on identity)",
        )
        _check(
            set(base.archetypes) != set(relab.archetypes),
            "the identity-keyed special-case is CAUGHT — claimed sets diverge under "
            "relabel, so the invariance assertion is non-vacuous",
        )
    finally:
        _offering.classify_offering = real
    # And the real classifier is restored (guard against leaking the rig).
    _check(
        _offering.classify_offering is real,
        "real classify_offering restored after the negative control",
    )


def main() -> int:
    tests = [
        test_canonical_org_offering,
        test_canonical_com_offering,
        test_canonical_metaphorical_ship_stays_na_org,
        test_canonical_metaphorical_ship_stays_na_com,
        test_offering_relabel_invariance_org,
        test_offering_relabel_invariance_com,
        test_offering_relabel_negative_control,
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
