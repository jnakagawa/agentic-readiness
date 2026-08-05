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

The acceptance criterion has TWO named halves — "driftflight.com shows
physical_good = NA ...; a retail storefront shows the inverse." The canonical
half is pinned above; the RETAIL INVERSE is pinned by
`test_retail_inverse_offering` below, replaying a committed static-crawl fixture
of a real book-catalog storefront (books.toscrape.com) and asserting the mirror
image — physical_good CLAIMED (on anchored "In stock"/"Add to basket" evidence,
never bare "ship") and the API/subscription/digital archetypes (exactly the ones
the canonical pair CLAIMS) all NA. Same offering pipeline, opposite verdict,
proving the claimed/NA partition tracks the storefront TYPE, not the domain.

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
    classify_offering,
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
# The RETAIL INVERSE — the operator directive's OTHER named acceptance case.
#
# The directive's acceptance criterion is two-sided: "driftflight.com shows
# physical_good = NA ...; a retail storefront shows the inverse." The guards
# above pin the first half (an agent-native image API -> physical_good NA). This
# pins the SECOND: a real retail storefront -> physical_good CLAIMED and the
# API / subscription / digital-good archetypes — exactly the ones the canonical
# pair CLAIMS — all NA. Same discover_offering pipeline, opposite verdict, so the
# claimed/NA partition demonstrably tracks the storefront's TYPE (what it sells),
# not its identity.
#
# Fixture captured [LOCAL] 2026-07-24 via a STATIC $0 crawl of books.toscrape.com
# (a stable, public book-catalog scraping sandbox — no API, no subscription, no
# generated media), replayed here through the REAL discovery path with NO network.
# Its homepage lists priced catalog items with unambiguous fulfillment language
# ("In stock" / "Add to basket") — the exact anchored signals `physical_good`
# requires — which is why the metaphorical-"ship" false positive the canonical
# pair guards against does NOT apply here: this storefront genuinely fulfills a
# physical good, and the classifier says so from evidence.
#
# Maintenance contract mirrors the canonical guard: if a signal-bank change
# LEGITIMATELY moves what this fixture claims, re-capture it [LOCAL]
# (`asrs.cli score books.toscrape.com --record-fixture
# fixtures/canonical/books.toscrape.com.json`) and update the expected sets below
# in the SAME PR.
# ---------------------------------------------------------------------------
_RETAIL = "books.toscrape.com"
# What the retail storefront CLAIMS: physical fulfillment only.
_RETAIL_CLAIMED = {"physical_good"}
# The MIRROR of the canonical `_MUST_BE_NA`: the archetypes the agent-native
# canonical pair CLAIMS are all NA on the retail storefront (it sells none of them).
_RETAIL_MUST_BE_NA = {"metered_api", "subscription", "digital_good"}
# The anchored fulfillment signals that make physical_good non-vacuous here (the
# specific labels the precision guard requires — never bare "ship"). Includes
# `priced-listing` (a decimal price quoted beside an in-stock / add-to-cart
# control — "£51.77 In stock"), the "understand the offer" price leg: the retail
# catalog quotes concrete prices, an agent-native API quotes bare metered
# per-call prices with no in-stock listing (priced-listing stays NA on the
# canonical pair — pinned by the org/com guards above).
_RETAIL_PHYSICAL_LABELS = {"add-to-cart", "stock", "priced-listing"}


def _assert_retail_inverse() -> None:
    profile, _ = _discover(_RETAIL)
    claimed = set(profile.archetypes)
    unclaimed = set(profile.unclaimed)

    _check(
        "homepage" in profile.surfaces_seen,
        f"{_RETAIL}: homepage surface was read (discovery had real evidence)",
    )

    # (a) The claimed SET is exactly physical_good — no spurious API/subscription
    # claim. Exact equality is the regression signal in BOTH directions: a
    # dropped physical_good OR a spurious API claim both fail here.
    _check(
        claimed == _RETAIL_CLAIMED,
        f"{_RETAIL}: claimed archetypes == {sorted(_RETAIL_CLAIMED)} (got {sorted(claimed)})",
    )

    # claimed and unclaimed partition the fixed template bank exactly (no leaks).
    _check(
        claimed | unclaimed == set(ARCHETYPES) and not (claimed & unclaimed),
        f"{_RETAIL}: claimed+unclaimed partition the archetype bank "
        f"(claimed {sorted(claimed)}, unclaimed {sorted(unclaimed)})",
    )

    # (b) The INVERSE of the canonical acceptance criterion: the archetypes the
    # agent-native canonical pair CLAIMS are all NA on the retail storefront.
    _check(
        _RETAIL_MUST_BE_NA <= unclaimed,
        f"{_RETAIL}: {sorted(_RETAIL_MUST_BE_NA)} are all NA/unclaimed "
        f"(got unclaimed {sorted(unclaimed)}) — a book catalog exposes no API, "
        "subscription, or generated-media surface",
    )
    _check(
        profile.claims("physical_good"),
        f"{_RETAIL}: physical_good CLAIMED (operator acceptance, inverse half) — "
        "a book catalog fulfills a physical good",
    )
    _check(
        not profile.claims("metered_api"),
        f"{_RETAIL}: metered_api = NA — a retail catalog is not a programmatic API",
    )

    # Non-vacuous: the physical_good claim rests on ANCHORED fulfillment evidence
    # ("In stock" / "Add to basket"), the specific signals the precision guard
    # requires — NOT bare "ship" (which stays NA on the canonical pair above). So
    # this is a genuine physical storefront, not a same-word coincidence.
    phys = next(c for c in profile.claimed if c.archetype == "physical_good")
    labels = {s.label for s in phys.signals}
    _check(
        _RETAIL_PHYSICAL_LABELS <= labels,
        f"{_RETAIL}: physical_good rests on anchored fulfillment evidence "
        f"{sorted(_RETAIL_PHYSICAL_LABELS)} (got labels {sorted(labels)})",
    )


def test_retail_inverse_offering() -> None:
    print("test_retail_inverse_offering")
    _assert_retail_inverse()


# ---------------------------------------------------------------------------
# TEETH for the `test-mode` metered_api signal, on REAL captured evidence.
#
# The test-mode signal (an API sandbox / test-key / dry-run capability) keys on
# a precision-critical word: books.toscrape.com's page TITLE literally reads
# "Books to Scrape - Sandbox" (a demo-site name, not an API sandbox). A naive
# `\bsandbox\b` anchor would fire on that title and FALSELY claim metered_api for
# a pure-retail book catalog — the exact battery-polluting false positive the
# operator directive removes. The anchored signal must dodge it: this pins that
# the retail fixture's real bare-"Sandbox" title does NOT trip test-mode (and so
# does not spuriously add metered_api, already NA via test_retail_inverse_offering).
# Non-vacuous: the raw trap word IS present (a bare anchor WOULD fire), so the
# precision guard is doing real work, exercised on captured bytes not a synthetic.
# ---------------------------------------------------------------------------
_BARE_SANDBOX_RE = re.compile(r"\bsandbox\b", re.IGNORECASE)


def test_retail_sandbox_title_does_not_trip_test_mode() -> None:
    print("test_retail_sandbox_title_does_not_trip_test_mode")
    profile, ctx = _discover(_RETAIL)
    home = ctx.homepage(ua="browser")
    prose = strip_html(getattr(home, "text", "") or "")

    # The substrate really does contain the trap word (else the test is vacuous):
    # the "Books to Scrape - Sandbox" page title.
    _check(
        bool(_BARE_SANDBOX_RE.search(prose)),
        f"{_RETAIL}: homepage prose contains the bare 'Sandbox' trap word (the title)",
    )

    # ...yet no claim on the retail storefront rests on the test-mode signal.
    fired = {s.label for c in profile.claimed for s in c.signals}
    _check(
        "test-mode" not in fired,
        f"{_RETAIL}: bare 'Sandbox' in the page title does NOT trip test-mode "
        f"(precision guard holds on real captured evidence; fired labels {sorted(fired)})",
    )
    # ...and consequently no spurious metered_api claim from a sandbox title.
    _check(
        not profile.claims("metered_api"),
        f"{_RETAIL}: metered_api stays NA — a demo-site named 'Sandbox' is not an API",
    )


# ---------------------------------------------------------------------------
# The SERVICE-BOOKING anchor — the FIRST committed fixture to CLAIM service_booking.
#
# service_booking is one of the two tied-thinnest offering archetypes and, until
# this fixture, had ZERO committed evidence: it is NA on ALL five prior canonical
# fixtures (`_MUST_BE_NA` above pins it NA on the API pair; `_RETAIL` claims only
# physical_good; example.com claims nothing), so a NEW capability-worded
# service_booking signal could not be added or verified non-vacuously in-cloud
# (the [LOCAL] enabler this discharges — BACKLOG "capture a fixture that CLAIMS
# service_booking", open since Cycle 114). This fixture — a real appointment-
# booking storefront (Acuity Scheduling) captured [LOCAL] via a static $0 crawl —
# is that first anchor: it lets a future COVERAGE cycle mine service_booking for a
# genuinely distinct capability leg (a confirmation / reschedule / availability
# control) against REAL evidence, with the same non-vacuous read-live guard the
# metered_api signals got.
#
# It also makes the operator directive's NA machinery TWO-SIDED on the booking
# axis: the API pair and the retail fixture both show service_booking = NA (a
# programmatic API and a book catalog do not book a service), while this booking
# storefront shows it CLAIMED — proving the claimed/NA partition tracks the
# storefront TYPE, the same way `_RETAIL` proved it for physical_good.
#
# HONEST full classification: Acuity CLAIMS {subscription, service_booking,
# metered_api} — a subscription-priced ($16/mo, 7-day free trial) booking service
# with a real developer API. Pinned as an exact set so a spurious ADD (notably a
# false data_retrieval, the sibling thin archetype — the `lookup` precision family
# must NOT fire here) or a DROPPED archetype both fail. The other two thin
# archetypes (physical_good, data_retrieval) are asserted NA: this anchor gives
# service_booking its first evidence WITHOUT falsely conjuring its siblings.
#
# NON-VACUOUS by anchored evidence: service_booking rests on GENUINE bookable-
# service signals (book / appointment / schedule) drawn from real prose — "Online
# Booking & Appointment Scheduling Software" (homepage) and "How To Schedule an
# Appointment with the Acuity Scheduling API" (developer llms.txt) — NONE of which
# is the excluded B2B sales-CTA family ("book a demo" / "schedule a call") the
# Cycle-190/194 precision guards strip. So this is a real reservation storefront,
# not a same-word coincidence.
#
# Maintenance contract mirrors the canonical/retail guards: if a signal-bank
# change LEGITIMATELY moves what this fixture claims, re-capture it [LOCAL]
# (`asrs.cli score acuityscheduling.com --record-fixture
# fixtures/canonical/acuityscheduling.com.json`, static $0) and update the
# expected sets below in the SAME PR.
#
# Fixture captured [LOCAL] 2026-08-05 (this cycle) — the live discover_offering
# classification was reproduced byte-faithfully by the offline replay before
# recording (honest ordering, invariant #4); ephemeral set-cookie headers stripped
# for determinism, matching the sibling fixtures' zero-set-cookie convention.
# ---------------------------------------------------------------------------
_BOOKING = "acuityscheduling.com"
# What the booking storefront CLAIMS: a subscription-priced service with an API.
_BOOKING_CLAIMED = {"subscription", "service_booking", "metered_api"}
# The thin archetypes this anchor does NOT claim — service_booking gets its first
# evidence without falsely conjuring its sibling thin archetypes (physical_good is
# not fulfilled; data_retrieval must stay NA — the `lookup` family must not fire).
_BOOKING_MUST_BE_NA = {"physical_good", "data_retrieval"}
# The genuine bookable-service CREATE signals that make service_booking non-vacuous
# here (real reservation prose, never the excluded "book a demo"/"schedule a call"
# CTA) — the MAKE-a-booking act.
_BOOKING_CREATE_LABELS = {"book", "appointment", "schedule"}
# The DISTINCT lifecycle-management leg mined from this anchor's real prose
# (Cycle 248): reschedule/cancel an EXISTING booking — the "operate without a human"
# leg, not the create act. Every fired service_booking label must be one of these
# genuine signals (create ∪ manage), so a future spurious signal on the anchor fails.
_BOOKING_MANAGE_LABELS = {"manage-booking"}
# The DISTINCT closed-loop FOLLOW-THROUGH leg mined from this anchor's real prose
# (Cycle 252): the booking is automatically CONFIRMED and its reminders handled
# without a human — the "provision + complete the job without a human" completion-
# acknowledgment leg (the service_booking analog of metered_api's payment-receipt),
# distinct from both the create act and the reschedule/cancel management leg.
_BOOKING_NOTIFY_LABELS = {"booking-notification"}
# The DISTINCT data-collection PRECONDITION leg mined from this anchor's real
# prose (Cycle 256): the storefront gathers what a booked service needs via a
# custom INTAKE FORM — the "collect what the job needs / provision without a
# human" leg, distinct from the create act, the reschedule/cancel management leg
# and the confirm/remind follow-through leg.
_BOOKING_INTAKE_LABELS = {"intake-form"}
_BOOKING_SERVICE_LABELS = (
    _BOOKING_CREATE_LABELS
    | _BOOKING_MANAGE_LABELS
    | _BOOKING_NOTIFY_LABELS
    | _BOOKING_INTAKE_LABELS
)


def _assert_service_booking_anchor() -> None:
    profile, _ = _discover(_BOOKING)
    claimed = set(profile.archetypes)
    unclaimed = set(profile.unclaimed)

    _check(
        "homepage" in profile.surfaces_seen,
        f"{_BOOKING}: homepage surface was read (discovery had real evidence)",
    )

    # (a) The claimed SET is exactly {subscription, service_booking, metered_api}.
    # Exact equality is the regression signal in BOTH directions: a spurious ADD
    # (a false data_retrieval from the `lookup` family, the sibling thin archetype)
    # or a DROPPED archetype both fail here.
    _check(
        claimed == _BOOKING_CLAIMED,
        f"{_BOOKING}: claimed archetypes == {sorted(_BOOKING_CLAIMED)} "
        f"(got {sorted(claimed)})",
    )

    # claimed and unclaimed partition the fixed template bank exactly (no leaks).
    _check(
        claimed | unclaimed == set(ARCHETYPES) and not (claimed & unclaimed),
        f"{_BOOKING}: claimed+unclaimed partition the archetype bank "
        f"(claimed {sorted(claimed)}, unclaimed {sorted(unclaimed)})",
    )

    # (b) The whole point: service_booking is CLAIMED — the FIRST committed fixture
    # to do so (it is NA on all five prior canonical fixtures).
    _check(
        profile.claims("service_booking"),
        f"{_BOOKING}: service_booking CLAIMED — a real appointment-booking "
        "storefront books a service (the first committed service_booking anchor)",
    )

    # (c) The sibling thin archetypes stay NA: this anchor does not falsely conjure
    # its neighbours (physical_good fulfillment / a data_retrieval `lookup`).
    _check(
        _BOOKING_MUST_BE_NA <= unclaimed,
        f"{_BOOKING}: {sorted(_BOOKING_MUST_BE_NA)} are all NA/unclaimed "
        f"(got unclaimed {sorted(unclaimed)}) — service_booking's first evidence "
        "does not falsely claim its sibling thin archetypes",
    )

    # (d) Non-vacuous: service_booking rests on ANCHORED bookable-service evidence
    # (book / appointment / schedule), the genuine reservation signals — NOT the
    # excluded sales-CTA family. At least two distinct genuine CREATE labels fire,
    # every fired label is one of the genuine set (create ∪ manage, no unexpected
    # signal), and each has a non-empty quote.
    booking = next(c for c in profile.claimed if c.archetype == "service_booking")
    labels = {s.label for s in booking.signals}
    _check(
        len(labels & _BOOKING_CREATE_LABELS) >= 2,
        f"{_BOOKING}: service_booking rests on >=2 genuine bookable-service CREATE "
        f"signals {sorted(_BOOKING_CREATE_LABELS)} (got labels {sorted(labels)})",
    )
    _check(
        labels <= _BOOKING_SERVICE_LABELS,
        f"{_BOOKING}: every service_booking signal is a genuine bookable-service "
        f"label (got {sorted(labels)}, expected subset of "
        f"{sorted(_BOOKING_SERVICE_LABELS)})",
    )
    # (e) The NEW lifecycle-management leg (Cycle 248) fires NON-VACUOUSLY on this
    # anchor's real prose — reschedule/cancel an existing appointment — the DISTINCT
    # "operate without a human" capability, not merely another create signal.
    _check(
        _BOOKING_MANAGE_LABELS <= labels,
        f"{_BOOKING}: the manage-booking lifecycle leg fires on real "
        f"rescheduling/cancellation prose (got labels {sorted(labels)})",
    )
    # (f) The NEW closed-loop follow-through leg (Cycle 252) fires NON-VACUOUSLY on
    # this anchor's real prose — automated confirmation/reminder of a booking — the
    # DISTINCT "complete the job without a human" completion-acknowledgment leg, not
    # a create signal and not the reschedule/cancel management leg.
    _check(
        _BOOKING_NOTIFY_LABELS <= labels,
        f"{_BOOKING}: the booking-notification follow-through leg fires on real "
        f"automated confirmation/reminder prose (got labels {sorted(labels)})",
    )
    # (g) The NEW data-collection precondition leg (Cycle 256) fires NON-VACUOUSLY
    # on this anchor's real prose — a custom intake form the storefront uses to
    # collect what a booked service needs — the DISTINCT "collect what the job
    # needs / provision without a human" leg, not a create signal, not the
    # reschedule/cancel management leg, and not the confirm/remind follow-through leg.
    _check(
        _BOOKING_INTAKE_LABELS <= labels,
        f"{_BOOKING}: the intake-form data-collection leg fires on real "
        f"custom-intake-form prose (got labels {sorted(labels)})",
    )
    _check(
        all(s.quote and s.quote.strip() for s in booking.signals),
        f"{_BOOKING}: every service_booking signal carries quoted evidence",
    )


def test_service_booking_anchor_offering() -> None:
    print("test_service_booking_anchor_offering")
    _assert_service_booking_anchor()


def test_service_booking_partition_tracks_storefront_type() -> None:
    """TEETH: service_booking is CLAIMED on the booking storefront yet NA on the
    with-rails API pair and the retail catalog — the claimed/NA partition tracks
    the storefront TYPE, not a same-word coincidence."""
    print("test_service_booking_partition_tracks_storefront_type")
    booking, _ = _discover(_BOOKING)
    _check(
        booking.claims("service_booking"),
        f"{_BOOKING}: books a service -> service_booking CLAIMED",
    )
    for other in ("driftflight.com", _RETAIL):
        prof, _ = _discover(other)
        _check(
            not prof.claims("service_booking"),
            f"{other}: does not book a service -> service_booking NA (a "
            "programmatic API / book catalog is not a reservation storefront)",
        )


# ---------------------------------------------------------------------------
# The data_retrieval ANCHOR — the FIRST committed fixture that CLAIMS
# data_retrieval, the SIBLING thin archetype to service_booking. Before this
# capture data_retrieval had ZERO committed evidence (NA on all six prior
# canonical fixtures), so no data_retrieval signal could be added or verified
# non-vacuously in-cloud — the exact gap the service_booking anchor
# (acuityscheduling.com) closed for its sibling. This anchor closes it for
# data_retrieval, the second-thinnest archetype, so an in-cloud COVERAGE cycle
# can now mine it for a genuinely distinct capability leg (a records-lookup
# response contract, a dataset-download/licence control, ...) against REAL prose.
#
# ipinfo.io is an IP-data storefront: a metered API over a data-retrieval product
# (IP geolocation / carrier / privacy lookups), sold both as a subscription and as
# downloadable databases (a digital good). data_retrieval is claimed on ALL FOUR of
# its bank signals drawn from real prose — lookup ("every IP lookup"), enrich
# ("batch-enrichment-api"), dataset ("download the sample datasets"), data-service
# ("IP data enrichment" / "WHOIS Data API Reverse Domains API") — the widest genuine
# data_retrieval evidence available, and none of it the excluded provenance/internals
# senses the Cycle-186/198 precision guards strip (no "trained on a dataset", no
# "lookup table"). So this is a real data-retrieval product, not a same-word
# coincidence. The sibling thin archetypes stay NA: it fulfills no physical good and
# books no service.
#
# Maintenance contract mirrors the canonical/retail/booking guards: if a signal-bank
# change LEGITIMATELY moves what this fixture claims, re-capture it [LOCAL]
# (a static $0 discover_offering crawl -> save_fixture) and update the expected sets
# below in the SAME PR.
#
# Fixture captured [LOCAL] 2026-08-05 (this cycle) via a single live discover_offering
# crawl — the live classification was reproduced byte-faithfully by the offline replay
# before recording (honest ordering, invariant #4); ipinfo serves no set-cookie on
# these surfaces (zero stripped), matching the sibling fixtures' zero-set-cookie
# convention.
# ---------------------------------------------------------------------------
_DATA = "ipinfo.io"
# What the data storefront CLAIMS: a metered, subscription-priced data-retrieval
# API whose datasets are also sold as a downloadable digital good.
_DATA_CLAIMED = {"metered_api", "data_retrieval", "subscription", "digital_good"}
# The thin archetypes this anchor does NOT claim — data_retrieval gets its first
# evidence without falsely conjuring its sibling thin archetypes (nothing is
# physically fulfilled; no service is booked).
_DATA_MUST_BE_NA = {"physical_good", "service_booking"}
# The genuine data-retrieval signals that make data_retrieval non-vacuous here (real
# lookup/enrichment/dataset prose, never the excluded provenance/internals senses).
_DATA_RETRIEVAL_LABELS = {"lookup", "enrich", "dataset", "data-service", "batch-retrieval"}


def _assert_data_retrieval_anchor() -> None:
    profile, _ = _discover(_DATA)
    claimed = set(profile.archetypes)
    unclaimed = set(profile.unclaimed)

    _check(
        "homepage" in profile.surfaces_seen,
        f"{_DATA}: homepage surface was read (discovery had real evidence)",
    )

    # (a) The claimed SET is exactly {metered_api, data_retrieval, subscription,
    # digital_good}. Exact equality is the regression signal in BOTH directions: a
    # spurious ADD (a false physical_good/service_booking, the sibling thin
    # archetypes) or a DROPPED archetype both fail here.
    _check(
        claimed == _DATA_CLAIMED,
        f"{_DATA}: claimed archetypes == {sorted(_DATA_CLAIMED)} "
        f"(got {sorted(claimed)})",
    )

    # claimed and unclaimed partition the fixed template bank exactly (no leaks).
    _check(
        claimed | unclaimed == set(ARCHETYPES) and not (claimed & unclaimed),
        f"{_DATA}: claimed+unclaimed partition the archetype bank "
        f"(claimed {sorted(claimed)}, unclaimed {sorted(unclaimed)})",
    )

    # (b) The whole point: data_retrieval is CLAIMED — the FIRST committed fixture
    # to do so (it is NA on all six prior canonical fixtures).
    _check(
        profile.claims("data_retrieval"),
        f"{_DATA}: data_retrieval CLAIMED — a real IP-data storefront retrieves "
        "data (the first committed data_retrieval anchor)",
    )

    # (c) The sibling thin archetypes stay NA: this anchor does not falsely conjure
    # its neighbours (no physical fulfillment, no service booking).
    _check(
        _DATA_MUST_BE_NA <= unclaimed,
        f"{_DATA}: {sorted(_DATA_MUST_BE_NA)} are all NA/unclaimed "
        f"(got unclaimed {sorted(unclaimed)}) — data_retrieval's first evidence "
        "does not falsely claim its sibling thin archetypes",
    )

    # (d) Non-vacuous: data_retrieval rests on ANCHORED data-retrieval evidence
    # (lookup / enrich / dataset / data-service), the genuine record-retrieval
    # signals — NOT the excluded provenance/internals senses. At least two distinct
    # genuine labels fire, every fired label is one of the genuine set (no unexpected
    # signal), and each has a non-empty quote.
    data = next(c for c in profile.claimed if c.archetype == "data_retrieval")
    labels = {s.label for s in data.signals}
    _check(
        len(labels & _DATA_RETRIEVAL_LABELS) >= 2,
        f"{_DATA}: data_retrieval rests on >=2 genuine data-retrieval signals "
        f"{sorted(_DATA_RETRIEVAL_LABELS)} (got labels {sorted(labels)})",
    )
    _check(
        labels <= _DATA_RETRIEVAL_LABELS,
        f"{_DATA}: every data_retrieval signal is a genuine data-retrieval label "
        f"(got {sorted(labels)}, expected subset of "
        f"{sorted(_DATA_RETRIEVAL_LABELS)})",
    )
    _check(
        all(s.quote and s.quote.strip() for s in data.signals),
        f"{_DATA}: every data_retrieval signal carries quoted evidence",
    )


def test_data_retrieval_anchor_offering() -> None:
    print("test_data_retrieval_anchor_offering")
    _assert_data_retrieval_anchor()


def test_data_retrieval_partition_tracks_storefront_type() -> None:
    """TEETH: data_retrieval is CLAIMED on the IP-data storefront yet NA on the
    with-rails API pair, the retail catalog, and the booking storefront — the
    claimed/NA partition tracks the storefront TYPE, not a same-word coincidence."""
    print("test_data_retrieval_partition_tracks_storefront_type")
    data, _ = _discover(_DATA)
    _check(
        data.claims("data_retrieval"),
        f"{_DATA}: retrieves data -> data_retrieval CLAIMED",
    )
    for other in ("driftflight.com", _RETAIL, _BOOKING):
        prof, _ = _discover(other)
        _check(
            not prof.claims("data_retrieval"),
            f"{other}: does not vend a data-retrieval product -> data_retrieval NA "
            "(an image API / book catalog / booking storefront is not a data service)",
        )


# ---------------------------------------------------------------------------
# The MIXED storefront ANCHOR — the FIRST committed fixture that claims TWO
# storefront-TYPE archetypes at once: a physical_good RETAILER that has ALSO
# stood up agent-native commerce RAILS (metered_api). Every prior fixture is
# single-type on this axis: the canonical pair + api.replicate.com are
# metered_api with physical_good NA (an API fulfills no physical good); the
# retail catalog is physical_good with metered_api NA (a book catalog is not a
# programmatic API). So the claimed/NA partition had never been exercised on a
# storefront that is BOTH — leaving unproven that the classifier represents a
# genuinely MIXED offering rather than forcing an either/or. This fixture closes
# that gap.
#
# www.allbirds.com is a real DTC shoe retailer (physical fulfillment) whose own
# agent surfaces publish a live agent-native commerce rail: an llms.txt "Agent
# Instructions" doc advertising a UCP merchant profile (`GET /.well-known/ucp`),
# an MCP endpoint (`POST .../api/mcp`), and Buyer-approved Shop Pay checkout, plus
# a refund policy and order tracking. So it CLAIMS {metered_api, physical_good} —
# the retail half from anchored fulfillment nouns (homepage "free shipping", the
# llms.txt agentic-checkout "shipping address"), the rails half from the documented
# programmatic surface (a `GET/POST https://...` endpoint + a "Respect rate limits"
# instruction). Pinned as an exact set so a spurious ADD (a false subscription /
# data_retrieval) or a DROPPED archetype both fail.
#
# It advances the north star's "many storefront types" + "agentic commerce becoming
# real" axes at once — the first REAL (non-synthetic, non-driftflight) agent-native
# commerce storefront in the corpus, and a MIXED retail+API TYPE distinct from the
# no-rails retail (books.toscrape / moleskine) and the pure-API pair. It is also the
# [LOCAL] enabler the "capture a RICH retail fixture for physical_good fulfillment
# legs" backlog item (open since Cycle 118) asked for: its surfaces carry genuine
# fulfillment prose (refund policy, order tracking, shipping address, an agentic
# checkout flow) a future in-cloud COVERAGE cycle can mine for a NEW capability-worded
# physical_good leg (an order-tracking / returns-window signal) against REAL evidence —
# without the score-path risk, exactly as the service_booking / data_retrieval anchors
# enabled their siblings.
#
# The two thin archetypes (service_booking, data_retrieval) — and subscription /
# digital_good — are asserted NA: this MIXED anchor gives the retail+API coexistence
# its first evidence WITHOUT falsely conjuring any neighbour. NON-VACUOUS by anchored
# evidence: physical_good rests on genuine fulfillment nouns ("free shipping" /
# "shipping address"), never bare metaphorical "ship"; metered_api on a documented
# programmatic endpoint + rate-limit instruction, never a bare login.
#
# Maintenance contract mirrors the canonical/retail/booking/data guards: if a
# signal-bank change LEGITIMATELY moves what this fixture claims (e.g. a NEW
# physical_good fulfillment signal this anchor was captured to enable), re-capture it
# [LOCAL] (`python -m experiments.capture_offering_fixture www.allbirds.com
# fixtures/canonical/www.allbirds.com.json`, static $0) and update the expected sets
# below in the SAME PR.
#
# Fixture captured [LOCAL] 2026-08-05 (Cycle 261) via a single live discover_offering
# crawl (experiments/capture_offering_fixture.py) — the live classification was
# reproduced byte-faithfully by the offline replay before recording (honest ordering,
# invariant #4; zero replay-miss); 14 ephemeral set-cookie headers stripped, matching
# the sibling fixtures' zero-set-cookie convention.
# ---------------------------------------------------------------------------
_MIXED = "www.allbirds.com"
# What the MIXED storefront CLAIMS: physical fulfillment AND a programmatic rail.
_MIXED_CLAIMED = {"metered_api", "physical_good"}
# The archetypes this anchor does NOT claim — the MIXED coexistence gets its first
# evidence without falsely conjuring a subscription, a digital good, or either thin
# archetype (service_booking / data_retrieval).
_MIXED_MUST_BE_NA = {"subscription", "digital_good", "service_booking", "data_retrieval"}
# The anchored fulfillment signals that make physical_good non-vacuous here (real
# fulfillment nouns, never bare "ship"). Open subset: a future physical_good leg this
# anchor was captured to enable may ADD a label without dropping the claim.
# `order-tracking` (Cycle 266) is the post-purchase order-lifecycle leg this MIXED
# anchor was captured to enable — pinned here on the real llms.txt evidence
# ("... and track orders", the "Order tracking" capability bullet).
_MIXED_PHYSICAL_LABELS = {"free-shipping", "shipping-noun", "order-tracking"}
# The anchored programmatic signals that make metered_api non-vacuous here (a
# documented endpoint + a rate-limit instruction, never a bare login).
_MIXED_API_LABELS = {"post-endpoint", "rate-limited"}


def _assert_mixed_anchor() -> None:
    profile, _ = _discover(_MIXED)
    claimed = set(profile.archetypes)
    unclaimed = set(profile.unclaimed)

    _check(
        "homepage" in profile.surfaces_seen,
        f"{_MIXED}: homepage surface was read (discovery had real evidence)",
    )

    # (a) The claimed SET is exactly {metered_api, physical_good}. Exact equality is
    # the regression signal in BOTH directions: a spurious ADD (a false subscription /
    # data_retrieval) or a DROPPED archetype both fail here.
    _check(
        claimed == _MIXED_CLAIMED,
        f"{_MIXED}: claimed archetypes == {sorted(_MIXED_CLAIMED)} (got {sorted(claimed)})",
    )

    # claimed and unclaimed partition the fixed template bank exactly (no leaks).
    _check(
        claimed | unclaimed == set(ARCHETYPES) and not (claimed & unclaimed),
        f"{_MIXED}: claimed+unclaimed partition the archetype bank "
        f"(claimed {sorted(claimed)}, unclaimed {sorted(unclaimed)})",
    )

    # (b) The whole point: BOTH storefront-type archetypes are CLAIMED at once — the
    # FIRST committed fixture where physical fulfillment and a programmatic rail
    # coexist (every prior fixture claims one with the other NA).
    _check(
        profile.claims("physical_good") and profile.claims("metered_api"),
        f"{_MIXED}: physical_good AND metered_api both CLAIMED — a real retailer that "
        "has stood up an agent-native commerce rail (the first MIXED anchor)",
    )

    # (c) The other archetypes stay NA: the MIXED coexistence does not falsely conjure
    # a subscription, a digital good, or either thin archetype (service_booking /
    # data_retrieval).
    _check(
        _MIXED_MUST_BE_NA <= unclaimed,
        f"{_MIXED}: {sorted(_MIXED_MUST_BE_NA)} are all NA/unclaimed "
        f"(got unclaimed {sorted(unclaimed)}) — the MIXED anchor claims exactly its "
        "two storefront-type archetypes, conjuring no neighbour",
    )

    # (d) Non-vacuous, both halves. physical_good rests on anchored fulfillment nouns
    # and metered_api on a documented programmatic surface — open subsets, so a future
    # signal this anchor enables may add a label without dropping the claim. Every
    # fired signal carries quoted evidence.
    phys = next(c for c in profile.claimed if c.archetype == "physical_good")
    phys_labels = {s.label for s in phys.signals}
    _check(
        _MIXED_PHYSICAL_LABELS <= phys_labels,
        f"{_MIXED}: physical_good rests on anchored fulfillment evidence "
        f"{sorted(_MIXED_PHYSICAL_LABELS)} (got labels {sorted(phys_labels)})",
    )
    api = next(c for c in profile.claimed if c.archetype == "metered_api")
    api_labels = {s.label for s in api.signals}
    _check(
        _MIXED_API_LABELS <= api_labels,
        f"{_MIXED}: metered_api rests on anchored programmatic evidence "
        f"{sorted(_MIXED_API_LABELS)} (got labels {sorted(api_labels)})",
    )
    _check(
        all(s.quote and s.quote.strip() for c in profile.claimed for s in c.signals),
        f"{_MIXED}: every fired signal carries quoted evidence",
    )


def test_mixed_storefront_anchor_offering() -> None:
    print("test_mixed_storefront_anchor_offering")
    _assert_mixed_anchor()


def test_mixed_partition_tracks_storefront_type() -> None:
    """TEETH: the retail+API storefront claims BOTH metered_api and physical_good,
    whereas the with-rails API pair claims metered_api WITHOUT physical_good and the
    retail catalog claims physical_good WITHOUT metered_api — the claimed/NA partition
    represents a genuinely MIXED offering, not a forced either/or."""
    print("test_mixed_partition_tracks_storefront_type")
    mixed, _ = _discover(_MIXED)
    _check(
        mixed.claims("metered_api") and mixed.claims("physical_good"),
        f"{_MIXED}: sells a physical good over an agent-native rail -> BOTH claimed",
    )
    api_pair, _ = _discover("driftflight.com")
    _check(
        api_pair.claims("metered_api") and not api_pair.claims("physical_good"),
        "driftflight.com: a programmatic image API -> metered_api CLAIMED, "
        "physical_good NA (the MIXED coexistence is not an artifact of over-matching)",
    )
    retail, _ = _discover(_RETAIL)
    _check(
        retail.claims("physical_good") and not retail.claims("metered_api"),
        f"{_RETAIL}: a book catalog -> physical_good CLAIMED, metered_api NA "
        "(the other single-type pole)",
    )


# ---------------------------------------------------------------------------
# The EMPTY offering — a site that sells nothing. The two guards above pin the
# poles of the classifier (an agent-native API -> physical_good NA; a retail shop
# -> physical_good CLAIMED, APIs NA). This pins the THIRD, degenerate case the
# operator directive's NA semantics must handle honestly: a non-storefront that
# claims NO archetype at all. Its battery is legitimately EMPTY — every archetype
# NA, excluded from every mean/spread, never a fabricated task or a penalty. This
# is the offering-layer companion to the zero-commerce scoring baseline in
# test_canonical_replay (example.com, 22.5 F): the same committed static-crawl
# fixture, read through the offering pipeline, must produce nothing to assess.
#
# Regression value: a signal-bank change that started matching generic prose
# (an over-eager archetype anchor) would spuriously CLAIM an archetype on a bare
# documentation page and fail here — the classifier must stay precision-first,
# emitting an honest empty profile rather than inventing an offering.
#
# Fixture captured [LOCAL] 2026-07-24 via `asrs.cli score example.com
# --record-fixture fixtures/canonical/example.com.json` (static $0 crawl).
# ---------------------------------------------------------------------------
_NONSTOREFRONT = "example.com"


def test_nonstorefront_empty_offering() -> None:
    print("test_nonstorefront_empty_offering")
    profile, _ = _discover(_NONSTOREFRONT)

    # Discovery drew on real evidence (the homepage was read), so an empty result
    # is a genuine "nothing offered", not a failed/empty crawl.
    _check(
        "homepage" in profile.surfaces_seen,
        f"{_NONSTOREFRONT}: homepage surface was read (discovery had real evidence)",
    )

    # No archetype is claimed — the site sells nothing the battery can instantiate.
    _check(
        profile.archetypes == [],
        f"{_NONSTOREFRONT}: claims NO archetype (got {profile.archetypes}) — a bare "
        "documentation page is not a storefront",
    )

    # Every archetype is therefore NA: the whole template bank is unclaimed, so the
    # offering-relative battery is honestly empty (no fabricated task, no penalty).
    _check(
        set(profile.unclaimed) == set(ARCHETYPES),
        f"{_NONSTOREFRONT}: every archetype is NA/unclaimed "
        f"(got {sorted(profile.unclaimed)}, want {sorted(ARCHETYPES)})",
    )


# ---------------------------------------------------------------------------
# Machine-surface-FIRST storefront — the OpenAPI spec IS the agent-facing
# self-description, pinned on REAL captured data.
#
# `_SURFACE_DOCS` grew to read the machine API CONTRACT (/openapi.json, Cycle 34)
# and the agent-plugin descriptor (/.well-known/ai-plugin.json, Cycle 42) so an
# API-FIRST storefront that serves NO marketing homepage or llms.txt — only its
# spec — is classified from that surface, not mis-read as offering nothing. Until
# now that path was exercised only against SYNTHETIC surfaces (test_offering.py);
# the committed canonical fixtures predate both surfaces (a replay-miss on them).
# This replays a committed fixture of a REAL such storefront — api.replicate.com,
# a metered model-inference API whose homepage is a bare `{}` and whose only
# agent-facing self-description is its /openapi.json — captured [LOCAL] 2026-07-27,
# and pins that the spec was READ and DROVE the classification.
#
# It also pins a PRECISION FIX the live capture surfaced: Replicate's spec says
# "The SKU for the hardware used to run the model" — a COMPUTE/GPU hardware SKU.
# The old `sku-inventory` signal matched a bare "\bSKU\b", so it falsely claimed
# physical_good on a pure API storefront (an irrelevant fulfillment intent — the
# battery pollution the operator directive removes). The signal now anchors to
# unambiguous RETAIL phrasing, so physical_good stays NA. NON-VACUOUS: the
# compute-SKU trap phrase is asserted PRESENT in the surface below, so the guard
# proves the fix keeps physical_good NA, not that the trap phrase is absent.
#
# Maintenance: like the canonical fixtures, if a legitimate signal-bank change
# alters what this storefront claims, re-capture the fixture [LOCAL] and update
# the expectation here in the same PR.
# ---------------------------------------------------------------------------
_MACHINE_SURFACE = "api.replicate.com"


def test_machine_surface_openapi_storefront() -> None:
    print("test_machine_surface_openapi_storefront")
    profile, ctx = _discover(_MACHINE_SURFACE)
    claimed = set(profile.archetypes)

    # The machine API CONTRACT was read (the surface Cycle 34 added), on REAL data.
    _check(
        "/openapi.json" in profile.surfaces_seen,
        f"{_MACHINE_SURFACE}: /openapi.json surface was READ "
        f"(got surfaces_seen {profile.surfaces_seen})",
    )

    # A metered API is claimed — and the OpenAPI spec DROVE it: this storefront's
    # homepage is a bare `{}`, so classification rests on the machine surface.
    _check(
        claimed == {"metered_api"},
        f"{_MACHINE_SURFACE}: claimed == {{'metered_api'}} (got {sorted(claimed)}) — "
        "an API-first storefront classified from its spec alone",
    )
    metered = profile.claimed[0]
    _check(
        any(s.surface == "/openapi.json" for s in metered.signals),
        f"{_MACHINE_SURFACE}: the metered_api claim is driven by the /openapi.json "
        f"surface (signal surfaces {sorted({s.surface for s in metered.signals})})",
    )

    # Machine-surface-FIRST: the homepage was fetched but carries NO archetype
    # signal (it is a bare `{}`), so the classification rests entirely on the spec.
    _check(
        "homepage" in profile.surfaces_seen,
        f"{_MACHINE_SURFACE}: homepage was fetched (discovery had real evidence)",
    )
    home_signals = [
        s.label for c in profile.claimed for s in c.signals if s.surface == "homepage"
    ]
    _check(
        home_signals == [],
        f"{_MACHINE_SURFACE}: no archetype signal comes from the thin homepage "
        f"(got {home_signals}) — the spec is the agent-facing self-description",
    )

    # THE precision guard (surfaced live): a compute/GPU hardware "SKU" must NOT
    # read as a physical good. NON-VACUOUS — the trap phrase is present in the spec.
    spec_text = ctx.get("/openapi.json", ua="browser").text
    _check(
        "SKU for the hardware" in spec_text,
        f"{_MACHINE_SURFACE}: the compute-SKU trap phrase is present in the spec "
        "(so the physical_good=NA assertion below is non-vacuous)",
    )
    _check(
        not profile.claims("physical_good"),
        f"{_MACHINE_SURFACE}: physical_good = NA despite 'The SKU for the hardware' "
        "— a compute/GPU hardware SKU is not retail inventory (precision fix)",
    )


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


def _assert_offering_relabel_invariant(domain: str, exp: set | None = None) -> None:
    base, _ = _discover(domain)
    if exp is None:
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


# The machine-surface-FIRST storefront joins the quote-anchored relabel family.
# The claimed set of `api.replicate.com` (the third committed offering fixture) is
# {metered_api}.
_MACHINE_CLAIMED = {"metered_api"}


def test_offering_relabel_invariance_machine() -> None:
    """A machine-surface-first storefront's task set is identity-invariant.

    `api.replicate.com` — a real metered model-inference API whose homepage is a
    bare `{}` and whose only agent-facing self-description is its /openapi.json — is
    the one committed offering fixture whose metered_api claim is driven by the
    machine CONTRACT rather than marketing prose (pinned by
    `test_machine_surface_openapi_storefront` above). Its `post-endpoint` evidence
    quote literally embeds the host (`curl -X POST https://api.replicate.com/v1/…`),
    so it shares the SAME quote-anchored non-vacuity substrate as the canonical pair
    — the host really is inside the classifier's matched evidence, so relabeling
    genuinely changes classifier input.

    This proves the metered_api task selection keys on the endpoint STRUCTURE (a POST
    to a versioned API path), not the vendor's NAME: relabel the host everywhere and
    the claimed set ([metered_api]) and the NA set (every other archetype, excluded
    from every mean/spread, never penalized) are byte-identical. The relabel guards
    above cover the two flight-themed fixtures; this extends the quote-anchored family
    to the machine-contract-driven storefront, the classification path that a
    homepage-only relabel could not exercise.
    """
    print("test_offering_relabel_invariance_machine")
    _assert_offering_relabel_invariant(_MACHINE_SURFACE, _MACHINE_CLAIMED)


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


# ---------------------------------------------------------------------------
# Relabel-invariance at the EVIDENCE layer — finer than the set/order guards.
#
# `_assert_offering_relabel_invariant` pins that the CLAIMED archetype list
# (ordered) and the NA/unclaimed set are identity-invariant. That catches an
# identity-keyed special-case only when it CHANGES which archetypes are claimed
# (the negative control above force-adds a whole physical_good claim). It is
# blind to a subtler vendor-rigging: a favorable special-case that pads an
# ALREADY-claimed archetype's evidence — extra signal labels, a higher
# `strength` (distinct-label count) — WITHOUT flipping the claimed set or its
# order. Yet `strength` and the fired-label set are exactly what the classifier
# surfaces to the operator (`profile.evidence["claimed"][*]["strength"|"labels"]`)
# as HOW WELL a capability is supported — so a host-keyed strength/label boost
# would make a favored storefront's claims read as better-evidenced purely on
# its NAME. The capability lens forbids special-casing "favorable OR hostile";
# this drops the invariance one layer, to the per-archetype evidence itself.
#
# For every claimed archetype it asserts the (strength, sorted signal-label set)
# is byte-identical under a whole-fixture host relabel. Same non-vacuity
# substrate as the set/order guard — the host is inside the classifier's matched
# quotes (asserted), so relabeling genuinely rewrites classifier input — and
# `test_offering_relabel_evidence_negative_control` proves this catches a rig the
# coarser set/order guard PASSES.
# ---------------------------------------------------------------------------
def _claim_evidence_fingerprint(profile) -> dict:
    """``archetype -> (strength, sorted fired-label tuple)`` for a profile.

    The per-archetype evidence the classifier exposes to the readout — finer
    than the claimed SET (which archetypes) the coarser guard pins.
    """
    return {
        c.archetype: (c.strength, tuple(sorted(s.label for s in c.signals)))
        for c in profile.claimed
    }


def _assert_offering_relabel_evidence_invariant(domain: str) -> None:
    base, _ = _discover(domain)

    # Non-vacuity: the classifier's OWN matched evidence contains the host, so a
    # relabel genuinely changes the text classification reads (not a no-op) — the
    # same substrate the set/order guard rests on, re-asserted here so this guard
    # stands on its own.
    _check(
        any(domain in s.quote for c in base.claimed for s in c.signals),
        f"{domain}: the host appears in the classifier's matched evidence "
        "(relabel genuinely changes classifier input — the test is non-vacuous)",
    )

    relab = _discover_relabeled(domain, _NEUTRAL_HOST)
    base_fp = _claim_evidence_fingerprint(base)
    relab_fp = _claim_evidence_fingerprint(relab)

    # Same archetypes carry evidence on both sides (implied by the set guard, but
    # re-checked so the per-archetype comparison below is total, not partial).
    _check(
        set(base_fp) == set(relab_fp),
        f"{domain}: the same archetypes carry evidence under relabel "
        f"(base {sorted(base_fp)}, relabel {sorted(relab_fp)})",
    )
    for archetype in base_fp:
        b_strength, b_labels = base_fp[archetype]
        r_strength, r_labels = relab_fp[archetype]
        _check(
            b_strength == r_strength,
            f"{domain}: {archetype} strength invariant under relabel "
            f"({b_strength} -> {r_strength})",
        )
        _check(
            b_labels == r_labels,
            f"{domain}: {archetype} fired-label set invariant under relabel "
            f"(base {list(b_labels)}, relabel {list(r_labels)})",
        )


def test_offering_relabel_evidence_invariance_org() -> None:
    print("test_offering_relabel_evidence_invariance_org")
    _assert_offering_relabel_evidence_invariant("drift-flight.org")


def test_offering_relabel_evidence_invariance_com() -> None:
    print("test_offering_relabel_evidence_invariance_com")
    _assert_offering_relabel_evidence_invariant("driftflight.com")


def test_offering_relabel_evidence_invariance_machine() -> None:
    print("test_offering_relabel_evidence_invariance_machine")
    _assert_offering_relabel_evidence_invariant(_MACHINE_SURFACE)


def test_offering_relabel_evidence_negative_control() -> None:
    """The evidence guard catches a rig the coarser set/order guard PASSES.

    Monkeypatch a FAVORABLE identity-keyed special-case that pads an ALREADY-
    claimed archetype: when the domain is the canonical identity, add one extra
    signal label to ``metered_api`` (the strongest claim by a wide margin, so the
    pad neither flips the claimed SET nor its ORDER nor the NA set). Under this
    rig:

      (a) `_assert_offering_relabel_invariant` — the coarser set/order guard —
          STILL PASSES, because claimed archetypes, their order, and the NA set
          are all unchanged (metered_api was already first). This proves the
          gap is real: identity-rigging can hide from the coarser guard.
      (b) `_assert_offering_relabel_evidence_invariant` — this cycle's finer
          guard — RAISES, because metered_api's (strength, label set) diverges
          between the canonical-host base and the neutral-host relabel.

    So the evidence guard refutes a real failure mode (a host-keyed evidence
    boost making a favored storefront's claims read as better-supported) that the
    archetype-set guard cannot see. Restores the real classifier in a finally.
    """
    print("test_offering_relabel_evidence_negative_control")
    real = _offering.classify_offering
    _PAD_LABEL = "rigged-strength-pad"

    def rigged(domain, surfaces):
        prof = real(domain, surfaces)
        # Keyed on the storefront's IDENTITY, not its evidence — the anti-pattern,
        # but this time padding an already-claimed archetype rather than adding one.
        if "driftflight" in domain.replace("-", ""):
            claim = next(
                (c for c in prof.claimed if c.archetype == "metered_api"), None
            )
            if claim is not None and all(s.label != _PAD_LABEL for s in claim.signals):
                claim.signals.append(
                    ArchetypeSignal(
                        archetype="metered_api",
                        surface="homepage",
                        label=_PAD_LABEL,
                        quote="strength padded on domain identity",
                    )
                )
        return prof

    _offering.classify_offering = rigged
    try:
        # (a) The coarser set/order guard PASSES under the rig — the pad is
        # invisible to it (claimed set, order, and NA all unchanged).
        _assert_offering_relabel_invariant("driftflight.com")
        _check(
            True,
            "coarser set/order relabel guard PASSES under the strength-pad rig "
            "(the pad hides from it — the gap is real)",
        )
        # (b) The finer evidence guard CATCHES it — metered_api's fingerprint
        # diverges between the canonical-host base and the neutral-host relabel.
        caught = False
        try:
            _assert_offering_relabel_evidence_invariant("driftflight.com")
        except AssertionError:
            caught = True
        _check(
            caught,
            "the evidence guard CATCHES the identity-keyed strength/label pad "
            "(divergence the set/order guard misses)",
        )
    finally:
        _offering.classify_offering = real
    _check(
        _offering.classify_offering is real,
        "real classify_offering restored after the evidence negative control",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the agent-native payment RAIL claim.
#
# The relabel guards above assert the claimed ARCHETYPE partition is
# identity-invariant. This one drops a layer: the specific `agent-payment-rail`
# metered_api signal (Cycle 78 — x402/MPP/ACP/UCP/AP2 in two high-precision
# forms, a structured `"protocol":"<rail>"` manifest entry OR a rail name paired
# with its on-chain settlement asset in a `(… USDC …)` parenthetical) must key
# on that PROTOCOL/SETTLEMENT structure, never on who published it. An
# agent-native payment rail is a property of what a storefront declares
# programmatically, not of its domain.
#
# The rail signal fires on driftflight.com's OWN agent surfaces — the
# settlement-asset form on `/llms-full.txt` ("x402 (Base USDC) and MPP (Tempo
# USDC)") and the structured form on `/manifest.json`
# (`"paymentProtocols":[{"protocol":"x402",…}]`). Those surface KEYS embed the
# host (`agents.driftflight.com/…`), so a whole-fixture host relabel genuinely
# rewrites the classifier's input on the very surfaces the signal reads — the
# non-vacuity anchor. Under relabel the signal must survive with the SAME match
# count, on the SAME host-normalized surfaces, each quote still satisfying a
# high-precision protocol form with the vendor host gone.
#
# Byte-equality of the quotes modulo the host string is NOT asserted: the host
# lengths differ (`driftflight.com` 15 chars vs `vendor-neutral.test` 19), which
# shifts the fixed-width quote WINDOW by a few characters (`.com/openapi.json` ->
# `test/openapi.json`). The structural invariant — the fired form is still a
# valid rail match, re-verified by re-running the live signal regex on each
# relabeled quote — is the honest, robust assertion.
# ---------------------------------------------------------------------------
_RAIL_LABEL = "agent-payment-rail"


def _rail_signals(prof) -> list:
    """The (surface, quote) pairs where the agent-payment-rail signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _RAIL_LABEL
    )


def test_offering_relabel_invariance_payment_rail() -> None:
    """The agent-native payment-rail claim keys on protocol structure, not host."""
    print("test_offering_relabel_invariance_payment_rail")
    base, _ = _discover("driftflight.com")
    base_rails = _rail_signals(base)

    # The signal genuinely fires on real captured evidence — and BOTH high-precision
    # forms are exercised (structured protocol declaration + settlement-asset name).
    _check(
        len(base_rails) >= 2,
        "agent-payment-rail fires on >=2 real driftflight.com surfaces "
        f"(got {len(base_rails)}: {[s for s, _ in base_rails]})",
    )
    joined = " ".join(q for _, q in base_rails).lower()
    _check(
        '"protocol"' in joined,
        'a structured "protocol":"<rail>" declaration is among the rail evidence',
    )
    _check(
        "usdc" in joined,
        "a rail name paired with its on-chain settlement asset (USDC) is among the "
        "rail evidence",
    )

    # Non-vacuity: the host is present in every surface that carries the rail signal,
    # so the whole-fixture relabel genuinely rewrites the classifier's input on those
    # very surfaces (not a no-op).
    _check(
        all("driftflight.com" in surf for surf, _ in base_rails),
        "each rail-signal surface embeds the host — relabel rewrites real input "
        f"(surfaces {[s for s, _ in base_rails]})",
    )

    relab = _discover_relabeled("driftflight.com", _NEUTRAL_HOST)
    relab_rails = _rail_signals(relab)

    # (1) Same number of rail matches — the signal is neither lost nor conjured.
    _check(
        len(relab_rails) == len(base_rails),
        "agent-payment-rail match count invariant under relabel "
        f"(base {len(base_rails)}, relabel {len(relab_rails)})",
    )
    # (2) The SAME logical surfaces carry the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    base_surf = sorted(s.replace("driftflight.com", _NEUTRAL_HOST) for s, _ in base_rails)
    relab_surf = sorted(s for s, _ in relab_rails)
    _check(
        relab_surf == base_surf,
        "rail signal fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies a high-precision protocol/settlement
    # form (re-run the live signal regex to prove the fired form is structural) and
    # no longer names the vendor host — the match keyed on structure, not identity.
    rail_re = dict(_offering._SIGNALS["metered_api"])[_RAIL_LABEL]
    for surf, quote in relab_rails:
        _check(
            rail_re.search(quote) is not None,
            f"relabeled rail quote still matches the protocol-structural signal: {quote!r}",
        )
        _check(
            "driftflight.com" not in quote and "driftflight.com" not in surf,
            f"vendor host absent from relabeled rail evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the async long-running-job contract.
#
# The companion to `test_offering_relabel_invariance_payment_rail` above, for the
# OTHER metered_api signal that landed recently: `async-job` (Cycle 82 — a
# webhook CALLBACK / status-endpoint POLL / async-endpoint contract, the "complete
# the job" capability of an agent-native API whose work does not finish in the
# request/response round-trip: image/video generation, a training run, a batch
# inference job). It fires on `api.replicate.com`'s `/openapi.json` — a genuine
# async prediction contract ("An HTTPS URL for receiving a webhook when the
# prediction has new output"). A long-running-job contract is a property of the
# integration STRUCTURE a storefront documents (webhook / poll / async endpoint),
# never of who published it, so the signal must be identity-invariant.
#
# Honest scope — WHY this is surface-presence, not quote-anchored: unlike the
# payment-rail signal (whose evidence SURFACES embed the host,
# `agents.driftflight.com/…`), the async-job contract vocabulary is host-free by
# nature — the fired quote carries webhook/poll/async words, not the vendor's
# name, and the surface is the relative `/openapi.json`. The non-vacuity anchor is
# therefore at the FIXTURE level (asserted below): the host IS present in the
# fixture surfaces the classifier fetches, so a whole-fixture relabel genuinely
# rewrites the classifier's overall input; the async-contract signal survives
# because the webhook/poll structure it keys on never named the vendor to begin
# with. Under relabel the signal must fire the SAME number of times, on the SAME
# surface, each quote STILL satisfying the live async-job regex, with the vendor
# host absent from every piece of rail evidence.
#
# This drops the machine-surface fixture's relabel coverage (whole-archetype,
# `test_offering_relabel_invariance_machine`) a layer down to the specific
# "complete the job" signal the growing class of long-running agent-native APIs
# rests on — the same move Cycle 79 made for `agent-payment-rail`.
# ---------------------------------------------------------------------------
_ASYNC_LABEL = "async-job"


def _async_signals(prof) -> list:
    """The (surface, quote) pairs where the async-job signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _ASYNC_LABEL
    )


def test_offering_relabel_invariance_async_job() -> None:
    """The async long-running-job claim keys on contract structure, not host."""
    print("test_offering_relabel_invariance_async_job")
    base, _ = _discover(_MACHINE_SURFACE)
    base_async = _async_signals(base)

    # The signal genuinely fires on real captured evidence — the async prediction
    # contract in the storefront's own OpenAPI spec.
    _check(
        len(base_async) >= 1,
        f"async-job fires on >=1 real {_MACHINE_SURFACE} surface "
        f"(got {len(base_async)}: {[s for s, _ in base_async]})",
    )
    joined = " ".join(q for _, q in base_async).lower()
    _check(
        "webhook" in joined or "poll" in joined or "async" in joined,
        "the async-job evidence carries webhook/poll/async contract vocabulary "
        f"(got {[q for _, q in base_async]})",
    )

    # Honest scope: unlike the payment-rail signal, the async-contract evidence is
    # host-FREE (the fired quote and its relative /openapi.json surface name no
    # vendor), so non-vacuity cannot anchor on the host being inside the quote.
    _check(
        all(
            _MACHINE_SURFACE not in surf and _MACHINE_SURFACE not in quote
            for surf, quote in base_async
        ),
        "the async-job evidence is host-free (webhook/poll structure, not a vendor "
        "name) — so this is a surface-presence, not a quote-anchored, invariance",
    )

    # Non-vacuity anchor (fixture level): the host IS present in the fixture
    # surfaces the classifier fetches, so a whole-fixture relabel genuinely rewrites
    # the classifier's overall input — the async-contract signal surviving is not a
    # no-op over an absent host.
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    _check(
        _MACHINE_SURFACE in raw,
        f"{_MACHINE_SURFACE}: host present in the fixture surfaces (relabel rewrites "
        "real classifier input — the test is non-vacuous)",
    )

    relab = _discover_relabeled(_MACHINE_SURFACE, _NEUTRAL_HOST)
    relab_async = _async_signals(relab)

    # (1) Same number of async-job matches — the signal is neither lost nor conjured.
    _check(
        len(relab_async) == len(base_async),
        "async-job match count invariant under relabel "
        f"(base {len(base_async)}, relabel {len(relab_async)})",
    )
    # (2) The SAME (host-normalized) surfaces carry the signal — it did not migrate.
    base_surf = sorted(s.replace(_MACHINE_SURFACE, _NEUTRAL_HOST) for s, _ in base_async)
    relab_surf = sorted(s for s, _ in relab_async)
    _check(
        relab_surf == base_surf,
        "async-job fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live async-job regex (proving the
    # fired form is structural — webhook/poll/async vocabulary) and names no vendor
    # host — the match keyed on the integration contract, not identity.
    async_re = dict(_offering._SIGNALS["metered_api"])[_ASYNC_LABEL]
    for surf, quote in relab_async:
        _check(
            async_re.search(quote) is not None,
            f"relabeled async-job quote still matches the contract-structural signal: {quote!r}",
        )
        _check(
            _MACHINE_SURFACE not in quote and _MACHINE_SURFACE not in surf,
            f"vendor host absent from relabeled async-job evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the programmatic API-AUTH scheme.
#
# The third signal-level companion to the payment-rail and async-job guards
# above, for the metered_api signal that landed most recently: `api-auth`
# (Cycle 86 — how an agent GETS/PRESENTS a credential to CALL the API: the HTTP
# `Authorization: Bearer` header, a "Bearer token", an `X-API-Key` header, an
# "API key", an OpenAPI `"securitySchemes"`/`bearerAuth` declaration, an OAuth2
# flow, or "authenticated WITH/VIA/USING an api key/bearer/token"). It is the
# "provision without a human" leg of the reach->understand->pay->provision->
# complete lens: an agent that cannot read the auth scheme cannot invoke the API
# at all. An access/auth scheme is a property of what a storefront declares
# programmatically, never of who declares it, so the signal must be
# identity-invariant.
#
# QUOTE-ANCHORED non-vacuity, like payment-rail (NOT surface-presence like
# async-job): the api-auth signal fires on driftflight.com's homepage with the
# host literally inside the matched evidence quote — `.../api.driftflight.com/v1/
# images/generate Authorization: Bearer df_live_...` — so a whole-fixture host
# relabel genuinely rewrites the text the classifier matched, not just a surface
# key it fetched. (It is an HONEST mixed case: this signal also fires on
# host-free surfaces like `/docs` — "authenticated with an API key sent as a
# Bearer token" — and on host-embedding surfaces like `api.driftflight.com/
# openapi.json`; the non-vacuity anchor is the QUOTE that embeds the host, the
# strongest of the three, asserted below.) Under relabel the signal must survive
# with the SAME match count, on the SAME host-normalized surfaces, each quote
# still satisfying the live api-auth regex, with the vendor host gone from every
# piece of auth evidence.
#
# Byte-equality of the quotes modulo the host is NOT asserted (the host-length
# change `driftflight.com` 15 -> `vendor-neutral.test` 19 shifts the fixed-width
# quote window); the structural invariant — the fired form is still a valid
# api-auth match, re-verified by re-running the live signal regex on each
# relabeled quote — is the honest, robust assertion. This drops the relabel
# family one more layer, to the specific "provision" signal an agent needs to
# authenticate a metered call, the same move Cycle 79 made for `agent-payment-rail`
# and Cycle 83 for `async-job`.
# ---------------------------------------------------------------------------
_AUTH_LABEL = "api-auth"


def _auth_signals(prof) -> list:
    """The (surface, quote) pairs where the api-auth signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _AUTH_LABEL
    )


def test_offering_relabel_invariance_api_auth() -> None:
    """The programmatic API-auth scheme keys on scheme structure, not host."""
    print("test_offering_relabel_invariance_api_auth")
    base, _ = _discover("driftflight.com")
    base_auth = _auth_signals(base)

    # The signal genuinely fires on real captured evidence — and BOTH high-precision
    # credential forms are exercised (an HTTP Authorization/Bearer header + an API key).
    _check(
        len(base_auth) >= 2,
        "api-auth fires on >=2 real driftflight.com surfaces "
        f"(got {len(base_auth)}: {[s for s, _ in base_auth]})",
    )
    joined = " ".join(q for _, q in base_auth).lower()
    _check(
        "authorization" in joined or "bearer" in joined,
        "an HTTP Authorization/Bearer credential form is among the auth evidence",
    )
    _check(
        "api key" in joined or "api-key" in joined or "x-api-key" in joined,
        "an API-key credential form is among the auth evidence",
    )

    # Non-vacuity (QUOTE-anchored, like payment-rail): the host appears INSIDE at
    # least one matched evidence quote (the homepage `Authorization: Bearer` quote
    # embeds `api.driftflight.com/v1/...`), so the whole-fixture relabel genuinely
    # rewrites the very text the classifier matched — not merely a surface key.
    _check(
        any("driftflight.com" in q for _, q in base_auth),
        "the host appears inside an api-auth evidence quote — relabel rewrites "
        "matched classifier input (quote-anchored non-vacuity)",
    )

    relab = _discover_relabeled("driftflight.com", _NEUTRAL_HOST)
    relab_auth = _auth_signals(relab)

    # (1) Same number of auth matches — the signal is neither lost nor conjured.
    _check(
        len(relab_auth) == len(base_auth),
        "api-auth match count invariant under relabel "
        f"(base {len(base_auth)}, relabel {len(relab_auth)})",
    )
    # (2) The SAME logical surfaces carry the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    base_surf = sorted(s.replace("driftflight.com", _NEUTRAL_HOST) for s, _ in base_auth)
    relab_surf = sorted(s for s, _ in relab_auth)
    _check(
        relab_surf == base_surf,
        "api-auth fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live api-auth regex (proving the
    # fired form is structural — an Authorization header / Bearer token / API key /
    # securityScheme / OAuth2) and names no vendor host — the match keyed on the
    # credential SCHEME, not identity.
    auth_re = dict(_offering._SIGNALS["metered_api"])[_AUTH_LABEL]
    for surf, quote in relab_auth:
        _check(
            auth_re.search(quote) is not None,
            f"relabeled api-auth quote still matches the scheme-structural signal: {quote!r}",
        )
        _check(
            "driftflight.com" not in quote and "driftflight.com" not in surf,
            f"vendor host absent from relabeled api-auth evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the documented ERROR CONTRACT.
#
# The fourth signal-level companion to the payment-rail / async-job / api-auth
# guards above, for the metered_api signal that landed most recently:
# `error-contract` (Cycle 90 — the 4xx/5xx error responses an agent must read to
# RECOVER from a failed call, in three high-precision forms: an OpenAPI
# status-keyed response object `"429":{"description"…`, the IETF RFC 7807
# `application/problem+json` media type, or a status code paired with a
# snake_case error code `400 invalid_request`). It is the "complete the job"
# RELIABILITY leg: an agent that cannot read the error contract cannot recover
# autonomously (refresh a credential on 401, back off/retry on 429, surface a
# clear failure on 4xx/5xx). An error contract is a property of what a storefront
# DECLARES — status codes, problem+json, error codes — never of WHO declares it,
# so the signal must be identity-invariant.
#
# SURFACE-PRESENCE, not quote-anchored (like async-job, NOT payment-rail): the
# error-contract vocabulary is host-free by nature — a status code, a media type,
# and a snake_case error code name no vendor, so the fired QUOTES carry no host
# (asserted below). But this fixture is a STRONGER surface-presence case than
# async-job: it fires 3 times on driftflight.com, and TWO of those three surfaces
# embed the host in the surface KEY (`agents.driftflight.com/llms-full.txt`,
# `api.driftflight.com/openapi.json`; the third, `/docs`, is host-free). So the
# whole-fixture relabel genuinely rewrites the surface keys the signal fires on —
# the host-normalization step of the surface assertion does real work here, unlike
# async-job's lone host-free `/openapi.json` surface. Under relabel the signal must
# survive with the SAME match count, on the SAME host-normalized surfaces, each
# quote STILL satisfying the live error-contract regex, with the vendor host absent
# from every piece of error-contract evidence.
#
# This drops the relabel family one more layer, to the specific "recover from a
# failed call" signal the growing class of long-running agent-native APIs rests
# on, the same move Cycle 79 made for `agent-payment-rail`, Cycle 83 for
# `async-job`, and Cycle 87 for `api-auth`.
# ---------------------------------------------------------------------------
_ERROR_LABEL = "error-contract"


def _error_signals(prof) -> list:
    """The (surface, quote) pairs where the error-contract signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _ERROR_LABEL
    )


def test_offering_relabel_invariance_error_contract() -> None:
    """The documented error contract keys on declared status codes, not host."""
    print("test_offering_relabel_invariance_error_contract")
    base, _ = _discover("driftflight.com")
    base_err = _error_signals(base)

    # The signal genuinely fires on real captured evidence — and BOTH host-free
    # structural forms are exercised (an OpenAPI status-keyed response object AND a
    # status code paired with a snake_case error code).
    _check(
        len(base_err) >= 2,
        "error-contract fires on >=2 real driftflight.com surfaces "
        f"(got {len(base_err)}: {[s for s, _ in base_err]})",
    )
    joined = " ".join(q for _, q in base_err)
    _check(
        '":{"description"' in joined or '": {"description"' in joined
        or re.search(r'"(?:4\d\d|5\d\d)"\s*:\s*\{', joined) is not None,
        "an OpenAPI status-keyed response object is among the error evidence",
    )
    _check(
        re.search(r"\b(?:4\d\d|5\d\d)\s+[a-z][a-z0-9]*_[a-z0-9_]+\b", joined) is not None,
        "a status code paired with a snake_case error code is among the error evidence",
    )

    # Honest scope: the error-contract evidence is host-FREE (a status code, a media
    # type, a snake_case error code name no vendor), so non-vacuity cannot anchor on
    # the host being inside the quote — this is a surface-presence invariance.
    _check(
        all("driftflight.com" not in quote for _, quote in base_err),
        "the error-contract evidence is host-free (status codes / problem+json / "
        "error codes, not a vendor name) — so this is a surface-presence, not a "
        "quote-anchored, invariance",
    )

    # Non-vacuity anchor (surface level, STRONGER than async-job's fixture-level
    # anchor): the host is present INSIDE the surface KEYS the signal fires on, so a
    # whole-fixture relabel genuinely rewrites the very surfaces the signal reads —
    # the host-normalization step of assertion (2) below does real work, it is not a
    # no-op over host-free surfaces.
    _check(
        any("driftflight.com" in surf for surf, _ in base_err),
        "the host appears inside >=1 error-contract surface key — relabel rewrites "
        f"real surface input (surfaces {[s for s, _ in base_err]})",
    )

    relab = _discover_relabeled("driftflight.com", _NEUTRAL_HOST)
    relab_err = _error_signals(relab)

    # (1) Same number of error-contract matches — the signal is neither lost nor conjured.
    _check(
        len(relab_err) == len(base_err),
        "error-contract match count invariant under relabel "
        f"(base {len(base_err)}, relabel {len(relab_err)})",
    )
    # (2) The SAME logical surfaces carry the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    base_surf = sorted(s.replace("driftflight.com", _NEUTRAL_HOST) for s, _ in base_err)
    relab_surf = sorted(s for s, _ in relab_err)
    _check(
        relab_surf == base_surf,
        "error-contract fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live error-contract regex (proving
    # the fired form is structural — a status-keyed response object / problem+json /
    # status+error-code) and names no vendor host — the match keyed on the DECLARED
    # error contract, not identity.
    err_re = dict(_offering._SIGNALS["metered_api"])[_ERROR_LABEL]
    for surf, quote in relab_err:
        _check(
            err_re.search(quote) is not None,
            f"relabeled error-contract quote still matches the structural signal: {quote!r}",
        )
        _check(
            "driftflight.com" not in quote and "driftflight.com" not in surf,
            f"vendor host absent from relabeled error-contract evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# The FIFTH metered_api signal-level relabel guard, for the newest metered_api
# capability signal: `test-mode` (Cycle 102 — a non-production SANDBOX / test-key /
# dry-run facility where an agent validates its integration and dry-runs a call at
# ZERO cost before authorizing anything real — the "provision + complete the job
# SAFELY, without a human" capability at the offering-understanding layer).
#
# The vendor-neutrality worry this guard exists to REFUTE is specific to the
# API-KEY-CONVENTION branch, `[a-z]{2,6}_(?:test|sandbox)_(?:\.{3}|<digit-stub>)`:
# on BOTH canonical fixtures test-mode fires on `/docs` via `df_test_...`, and the
# `df_` prefix genuinely ABBREVIATES the host stem (`drift-flight`/`driftflight` ->
# `df`). A naive reader could suspect the branch is matching a host-DERIVED prefix
# — i.e. that a differently-named shop with a different key prefix would score
# differently. It does not: the `[a-z]{2,6}` class matches ANY 2–6-char lowercase
# prefix; the signal keys on the `<prefix>_test_<masked-stub>` CONVENTION SHAPE, not
# on "df" and not on the host.
#
# So this guard perturbs BOTH identity axes and pins invariance under each:
#   (A) HOST relabel (the standard family perturbation): rewrite the host everywhere
#       -> test-mode fires with the same count on the same surface. For this signal
#       the fired quote AND surface (`/docs`) are host-FREE, so the host relabel is a
#       no-op over the test-mode evidence — that is itself the vendor-neutrality
#       property (the machine-integration convention names no vendor), asserted
#       honestly rather than dressed up as doing work it does not.
#   (B) KEY-PREFIX relabel (the perturbation that actually bites): rewrite the key
#       stem `df_` -> a neutral `kv_` throughout the fixture -> test-mode STILL fires,
#       same count, same surface, each quote still matching the live regex. THIS is
#       the non-vacuous half: it genuinely rewrites the matched text, proving the
#       branch keys on the convention, not on the host-abbreviating "df".
#
# Teeth: a convention-LESS stub (`df_test_runner` — no digit body, no `...` mask)
# does NOT fire, so the guard is not merely rubber-stamping any `<prefix>_test_`.
# ---------------------------------------------------------------------------
_TEST_MODE_LABEL = "test-mode"


def _test_mode_signals(prof) -> list:
    """The (surface, quote) pairs where the test-mode signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _TEST_MODE_LABEL
    )


def _discover_prefix_relabeled(domain: str, old_prefix: str, new_prefix: str):
    """Replay ``<domain>.json`` with the API-key stem ``old_prefix`` -> ``new_prefix``.

    Rewrites only the key-convention stem (e.g. ``df_`` -> ``kv_``) in both the live
    and test key examples, leaving the host untouched, then replays through the real
    ``FetchContext.from_fixture -> discover_offering`` path. A convention-keyed signal
    must fire identically; a signal secretly keyed on the host-abbreviating "df" stem
    would not.
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    relabeled = raw.replace(f"{old_prefix}live_", f"{new_prefix}live_").replace(
        f"{old_prefix}test_", f"{new_prefix}test_"
    )
    _check(
        relabeled != raw,
        f"{domain}: the key-prefix relabel {old_prefix!r}->{new_prefix!r} "
        "genuinely rewrites the fixture (non-vacuous)",
    )
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    try:
        tmp.write(relabeled)
        tmp.close()
        ctx = FetchContext.from_fixture(tmp.name)
        return discover_offering(ctx)
    finally:
        os.unlink(tmp.name)


def test_offering_relabel_invariance_test_mode() -> None:
    """test-mode keys on the ``<prefix>_test_<stub>`` convention, not host or "df"."""
    print("test_offering_relabel_invariance_test_mode")
    base, _ = _discover("driftflight.com")
    base_tm = _test_mode_signals(base)
    tm_re = dict(_offering._SIGNALS["metered_api"])[_TEST_MODE_LABEL]

    # The signal fires on real captured evidence, via the API-KEY convention branch
    # (a `<prefix>_test_<masked-stub>` credential), not merely a bare "sandbox"/"test".
    _check(
        len(base_tm) >= 1,
        f"test-mode fires on real driftflight.com evidence (got {len(base_tm)})",
    )
    joined = " ".join(q for _, q in base_tm)
    _check(
        re.search(r"\b[a-z]{2,6}_test_(?:\.{3}|[A-Za-z0-9]*\d)", joined) is not None,
        "the fired evidence is the `<prefix>_test_<masked-stub>` key convention "
        f"(not a bare sandbox/test word): {joined!r}",
    )

    # Honest scope: the fired quote is host-FREE (a `df_test_...` key credential names
    # no vendor host), so non-vacuity for this signal cannot anchor on the host being
    # inside the quote — a plain HOST relabel is a no-op over the test-mode evidence.
    _check(
        all("driftflight.com" not in quote for _, quote in base_tm),
        "the test-mode evidence is host-free (a key-convention credential, not a "
        "vendor name) — so a host relabel is a no-op here; the KEY-PREFIX relabel "
        "below is what genuinely perturbs the match",
    )

    # Non-vacuity substrate for axis (B): the `df_` stem genuinely abbreviates the
    # host, so the concern the prefix relabel refutes is real, not hypothetical.
    _check(
        any("df_test_" in quote for _, quote in base_tm),
        "the fired credential uses the `df_` prefix, which abbreviates the host stem "
        "(drift-flight/driftflight -> df) — the exact stem a prefix relabel perturbs",
    )

    # (A) HOST relabel: the machine-integration convention names no vendor, so the
    # signal survives a whole-host relabel unchanged (count + surface invariant).
    host_relab = _test_mode_signals(_discover_relabeled("driftflight.com", _NEUTRAL_HOST))
    _check(
        len(host_relab) == len(base_tm),
        "test-mode match count invariant under HOST relabel "
        f"(base {len(base_tm)}, relabel {len(host_relab)})",
    )
    _check(
        sorted(s for s, _ in host_relab) == sorted(s for s, _ in base_tm),
        "test-mode fires on the same surface under HOST relabel "
        f"(base {[s for s, _ in base_tm]}, relabel {[s for s, _ in host_relab]})",
    )

    # (B) KEY-PREFIX relabel `df_` -> neutral `kv_` (the code comment's own neutral
    # example prefix): this genuinely rewrites the matched credential text, so
    # invariance here proves the branch keys on the CONVENTION SHAPE, not on the
    # host-abbreviating "df" stem.
    pref_relab = _test_mode_signals(
        _discover_prefix_relabeled("driftflight.com", "df_", "kv_")
    )
    _check(
        len(pref_relab) == len(base_tm),
        "test-mode match count invariant under KEY-PREFIX relabel df_->kv_ "
        f"(base {len(base_tm)}, relabel {len(pref_relab)})",
    )
    _check(
        sorted(s for s, _ in pref_relab) == sorted(s for s, _ in base_tm),
        "test-mode fires on the same surface under KEY-PREFIX relabel "
        f"(base {[s for s, _ in base_tm]}, relabel {[s for s, _ in pref_relab]})",
    )
    for surf, quote in pref_relab:
        _check(
            tm_re.search(quote) is not None,
            f"prefix-relabeled test-mode quote still matches the convention signal: {quote!r}",
        )
        _check(
            "df_test_" not in quote,
            "the prefix-relabeled quote no longer carries the `df_` stem, yet still "
            f"fires — the match is convention-keyed, not stem-keyed: {quote!r}",
        )

    # Teeth: a convention-LESS `<prefix>_test_` stub (a plain identifier, no digit
    # body and no `...` mask) must NOT fire — the guard is not rubber-stamping any
    # `<prefix>_test_` occurrence.
    _check(
        tm_re.search("run the df_test_runner helper before deploy") is None,
        "a convention-less df_test_runner identifier does NOT fire test-mode "
        "(the key-convention branch requires a masked/digit-bearing stub)",
    )


# ---------------------------------------------------------------------------
# The SIXTH metered_api signal-level relabel guard, for the newest metered_api
# capability signal: `pagination` (Cycle 106 — a cursor / collection PAGINATION
# contract: how an agent walks a MULTI-PAGE result set to completion. A list
# endpoint returns one page plus a cursor / a `next`/`previous` page URL to
# follow; an agent that cannot follow the cursor reads only the FIRST page and
# silently UNDER-completes the retrieval. It is the "complete the job" leg for a
# metered API returning a COLLECTION — distinct from async-job (one long job's
# return), error-contract (recovery), and api-auth (provision).) It fires on
# `api.replicate.com`'s `/openapi.json` — a genuine cursor-pagination contract
# ("A URL pointing to the next page of collection objects"). How an agent
# paginates a collection is a property of the API CONTRACT a storefront
# documents (cursor param / next-page URL / paginated response schema), never of
# who published it, so the signal must be identity-invariant.
#
# SURFACE-PRESENCE, not quote-anchored (the async-job / error-contract shape, NOT
# payment-rail): the pagination contract vocabulary is host-free by nature — the
# fired quote carries `next page of collection` / a `?cursor=` param, not the
# vendor's name, and the surface is the relative `/openapi.json`. The non-vacuity
# anchor is therefore at the FIXTURE level (asserted below): the host IS present
# in the fixture surfaces the classifier fetches, so a whole-fixture relabel
# genuinely rewrites the classifier's overall input; the pagination signal
# survives because the cursor/next-page structure it keys on never named the
# vendor to begin with. Under relabel the signal must fire the SAME number of
# times, on the SAME surface, each quote STILL satisfying the live pagination
# regex, with the vendor host absent from every piece of pagination evidence.
#
# This drops the machine-surface fixture's relabel coverage (whole-archetype,
# `test_offering_relabel_invariance_machine`) a layer down to the specific
# "walk the paged collection to completion" signal a metered API returning a
# COLLECTION rests on — the same move Cycle 79 made for `agent-payment-rail`,
# Cycle 83 for `async-job`, and Cycle 103 for `test-mode`.
# ---------------------------------------------------------------------------
_PAGINATION_LABEL = "pagination"


def _pagination_signals(prof) -> list:
    """The (surface, quote) pairs where the pagination signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _PAGINATION_LABEL
    )


def test_offering_relabel_invariance_pagination() -> None:
    """The cursor/collection pagination claim keys on contract structure, not host."""
    print("test_offering_relabel_invariance_pagination")
    base, _ = _discover(_MACHINE_SURFACE)
    base_pg = _pagination_signals(base)

    # The signal genuinely fires on real captured evidence — the cursor-pagination
    # contract in the storefront's own OpenAPI spec.
    _check(
        len(base_pg) >= 1,
        f"pagination fires on >=1 real {_MACHINE_SURFACE} surface "
        f"(got {len(base_pg)}: {[s for s, _ in base_pg]})",
    )
    joined = " ".join(q for _, q in base_pg).lower()
    _check(
        "cursor=" in joined or "page of" in joined or "paginat" in joined,
        "the pagination evidence carries cursor / next-page / paginated contract "
        f"vocabulary (got {[q for _, q in base_pg]})",
    )

    # Honest scope: like async-job (not payment-rail), the pagination evidence is
    # host-FREE (the fired quote and its relative /openapi.json surface name no
    # vendor), so non-vacuity cannot anchor on the host being inside the quote.
    _check(
        all(
            _MACHINE_SURFACE not in surf and _MACHINE_SURFACE not in quote
            for surf, quote in base_pg
        ),
        "the pagination evidence is host-free (cursor/next-page structure, not a "
        "vendor name) — so this is a surface-presence, not a quote-anchored, invariance",
    )

    # Non-vacuity anchor (fixture level): the host IS present in the fixture
    # surfaces the classifier fetches, so a whole-fixture relabel genuinely rewrites
    # the classifier's overall input — the pagination signal surviving is not a
    # no-op over an absent host.
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    _check(
        _MACHINE_SURFACE in raw,
        f"{_MACHINE_SURFACE}: host present in the fixture surfaces (relabel rewrites "
        "real classifier input — the test is non-vacuous)",
    )

    relab = _discover_relabeled(_MACHINE_SURFACE, _NEUTRAL_HOST)
    relab_pg = _pagination_signals(relab)

    # (1) Same number of pagination matches — the signal is neither lost nor conjured.
    _check(
        len(relab_pg) == len(base_pg),
        "pagination match count invariant under relabel "
        f"(base {len(base_pg)}, relabel {len(relab_pg)})",
    )
    # (2) The SAME (host-normalized) surfaces carry the signal — it did not migrate.
    base_surf = sorted(s.replace(_MACHINE_SURFACE, _NEUTRAL_HOST) for s, _ in base_pg)
    relab_surf = sorted(s for s, _ in relab_pg)
    _check(
        relab_surf == base_surf,
        "pagination fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live pagination regex (proving the
    # fired form is structural — a cursor param / next-page URL / paginated response)
    # and names no vendor host — the match keyed on the collection contract, not identity.
    pg_re = dict(_offering._SIGNALS["metered_api"])[_PAGINATION_LABEL]
    for surf, quote in relab_pg:
        _check(
            pg_re.search(quote) is not None,
            f"relabeled pagination quote still matches the contract-structural signal: {quote!r}",
        )
        _check(
            _MACHINE_SURFACE not in quote and _MACHINE_SURFACE not in surf,
            f"vendor host absent from relabeled pagination evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the async job-CANCELLATION contract.
#
# The SEVENTH signal-level companion in the metered_api bank (after payment-rail
# Cycle 79, async-job 83, api-auth 87, error-contract 91, test-mode 103, and
# pagination 107), for the signal that landed most recently: `cancel-job`
# (Cycle 110 — how an agent ABORTS a long-running job it already submitted: a
# `Cancel-After` deadline header, a `cancel` VERB naming an async-job noun
# (cancel the prediction/job/run/training/...), or a `.../cancel` ENDPOINT PATH
# on a job resource (`predictions/{id}/cancel`). It is the "complete the job"
# CONTROL + capital-safety leg for a metered API whose work runs long: an agent
# that detects a runaway or wrong generation and CANNOT stop it keeps paying for
# compute it no longer needs, so a metered API that documents a cancel contract
# lets the agent BOUND its own spend and is more agent-completable. Distinct from
# async-job (how one long job's result comes BACK), error-contract (how a FAILED
# call recovers), and pagination (how a paged collection is WALKED).) It fires on
# `api.replicate.com`'s `/openapi.json` — a genuine `Cancel-After` deadline
# header. How an agent cancels a submitted job is a property of the API CONTRACT a
# storefront documents (deadline header / cancel endpoint / cancel verb), never of
# who published it, so the signal must be identity-invariant.
#
# SURFACE-PRESENCE, not quote-anchored (the async-job / pagination shape, NOT
# payment-rail): the cancel-contract vocabulary is host-free by nature — the fired
# quote carries the `Cancel-After` header structure, not the vendor's name, and
# the surface is the relative `/openapi.json`. The non-vacuity anchor is therefore
# at the FIXTURE level (asserted below): the host IS present in the fixture
# surfaces the classifier fetches, so a whole-fixture relabel genuinely rewrites
# the classifier's overall input; the cancel-job signal survives because the
# deadline-header / cancel-endpoint structure it keys on never named the vendor to
# begin with. Under relabel the signal must fire the SAME number of times, on the
# SAME surface, each quote STILL satisfying the live cancel-job regex, with the
# vendor host absent from every piece of cancel evidence.
#
# This drops the machine-surface fixture's relabel coverage (whole-archetype,
# `test_offering_relabel_invariance_machine`) a layer down to the specific
# "abort a submitted job" signal a metered API whose work runs long rests on —
# the same move Cycle 79 made for `agent-payment-rail`, Cycle 83 for `async-job`,
# and Cycle 107 for `pagination`. It completes the metered_api signal-level
# relabel family for every signal that landed through Cycle 110.
# ---------------------------------------------------------------------------
_CANCEL_LABEL = "cancel-job"


def _cancel_signals(prof) -> list:
    """The (surface, quote) pairs where the cancel-job signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _CANCEL_LABEL
    )


def test_offering_relabel_invariance_cancel_job() -> None:
    """The async job-cancellation claim keys on contract structure, not host."""
    print("test_offering_relabel_invariance_cancel_job")
    base, _ = _discover(_MACHINE_SURFACE)
    base_cx = _cancel_signals(base)

    # The signal genuinely fires on real captured evidence — the job-cancellation
    # contract in the storefront's own OpenAPI spec.
    _check(
        len(base_cx) >= 1,
        f"cancel-job fires on >=1 real {_MACHINE_SURFACE} surface "
        f"(got {len(base_cx)}: {[s for s, _ in base_cx]})",
    )
    joined = " ".join(q for _, q in base_cx).lower()
    _check(
        "cancel-after" in joined or "/cancel" in joined or "cancel" in joined,
        "the cancel-job evidence carries cancel-after / cancel-endpoint / cancel-verb "
        f"contract vocabulary (got {[q for _, q in base_cx]})",
    )

    # Honest scope: like async-job / pagination (not payment-rail), the cancel-job
    # evidence is host-FREE (the fired quote and its relative /openapi.json surface
    # name no vendor), so non-vacuity cannot anchor on the host being inside the quote.
    _check(
        all(
            _MACHINE_SURFACE not in surf and _MACHINE_SURFACE not in quote
            for surf, quote in base_cx
        ),
        "the cancel-job evidence is host-free (deadline-header/cancel-endpoint "
        "structure, not a vendor name) — so this is a surface-presence, not a "
        "quote-anchored, invariance",
    )

    # Non-vacuity anchor (fixture level): the host IS present in the fixture
    # surfaces the classifier fetches, so a whole-fixture relabel genuinely rewrites
    # the classifier's overall input — the cancel-job signal surviving is not a
    # no-op over an absent host.
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    _check(
        _MACHINE_SURFACE in raw,
        f"{_MACHINE_SURFACE}: host present in the fixture surfaces (relabel rewrites "
        "real classifier input — the test is non-vacuous)",
    )

    relab = _discover_relabeled(_MACHINE_SURFACE, _NEUTRAL_HOST)
    relab_cx = _cancel_signals(relab)

    # (1) Same number of cancel-job matches — the signal is neither lost nor conjured.
    _check(
        len(relab_cx) == len(base_cx),
        "cancel-job match count invariant under relabel "
        f"(base {len(base_cx)}, relabel {len(relab_cx)})",
    )
    # (2) The SAME (host-normalized) surfaces carry the signal — it did not migrate.
    base_surf = sorted(s.replace(_MACHINE_SURFACE, _NEUTRAL_HOST) for s, _ in base_cx)
    relab_surf = sorted(s for s, _ in relab_cx)
    _check(
        relab_surf == base_surf,
        "cancel-job fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live cancel-job regex (proving the
    # fired form is structural — a deadline header / cancel endpoint / cancel verb)
    # and names no vendor host — the match keyed on the job-control contract, not identity.
    cx_re = dict(_offering._SIGNALS["metered_api"])[_CANCEL_LABEL]
    for surf, quote in relab_cx:
        _check(
            cx_re.search(quote) is not None,
            f"relabeled cancel-job quote still matches the contract-structural signal: {quote!r}",
        )
        _check(
            _MACHINE_SURFACE not in quote and _MACHINE_SURFACE not in surf,
            f"vendor host absent from relabeled cancel-job evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the streaming-response delivery form.
#
# The EIGHTH signal-level companion in the metered_api bank (after payment-rail
# Cycle 79, async-job 83, api-auth 87, error-contract 91, test-mode 103,
# pagination 107, and cancel-job 110), for the signal that landed most recently:
# `streaming-response` (Cycle 126 — how an agent consumes a metered API's output
# INCREMENTALLY over the OPEN connection as it is produced: the W3C Server-Sent
# Events standard, its `text/event-stream` media type, a `stream`/`streaming` VERB
# naming an output noun (stream the output / streaming responses / stream tokens),
# a `streaming` API/ENDPOINT/MODE, or the `SSE` acronym ONLY in a streaming
# context. It is the "understand + complete the job" delivery leg for a metered API
# whose work produces output progressively: an agent that cannot open a documented
# streaming/SSE flow blocks on a long call it could have consumed incrementally, so
# a metered API that documents a streaming contract is MORE agent-completable.
# Distinct from every other metered_api leg — async-job collects a completed job's
# result OUT of band via webhook/poll; streaming-response is the IN-BAND sibling
# that delivers partial output WITHIN the same open connection.) It fires on
# `api.replicate.com`'s `/openapi.json` — a genuine `stream` field documenting
# "receive streaming output using server-sent events (SSE)". How an agent consumes
# an API's output as it is produced is a property of the delivery CONTRACT a
# storefront documents (SSE / text/event-stream / a streaming endpoint), never of
# who published it, so the signal must be identity-invariant.
#
# SURFACE-PRESENCE, not quote-anchored (the async-job / pagination / cancel-job
# shape, NOT payment-rail): the streaming vocabulary is host-free by nature — the
# fired quote carries the SSE/streaming-delivery structure, not the vendor's name,
# and the surface is the relative `/openapi.json`. The non-vacuity anchor is
# therefore at the FIXTURE level (asserted below): the host IS present in the
# fixture surfaces the classifier fetches, so a whole-fixture relabel genuinely
# rewrites the classifier's overall input; the streaming-response signal survives
# because the SSE/streaming structure it keys on never named the vendor to begin
# with. Under relabel the signal must fire the SAME number of times, on the SAME
# surface, each quote STILL satisfying the live streaming-response regex, with the
# vendor host absent from every piece of streaming evidence.
#
# This drops the machine-surface fixture's relabel coverage (whole-archetype,
# `test_offering_relabel_invariance_machine`) a layer down to the specific
# "consume output as it streams" signal a metered API whose output is progressive
# rests on — the same move Cycle 79 made for `agent-payment-rail`, 83 for
# `async-job`, 107 for `pagination`, and 110 for `cancel-job`. It completes the
# metered_api signal-level relabel family for every signal that landed through
# Cycle 126.
# ---------------------------------------------------------------------------
_STREAM_LABEL = "streaming-response"


def _stream_signals(prof) -> list:
    """The (surface, quote) pairs where the streaming-response signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _STREAM_LABEL
    )


def test_offering_relabel_invariance_streaming_response() -> None:
    """The incremental-delivery claim keys on the SSE/streaming contract, not host."""
    print("test_offering_relabel_invariance_streaming_response")
    base, _ = _discover(_MACHINE_SURFACE)
    base_st = _stream_signals(base)

    # The signal genuinely fires on real captured evidence — the streaming-delivery
    # contract in the storefront's own OpenAPI spec.
    _check(
        len(base_st) >= 1,
        f"streaming-response fires on >=1 real {_MACHINE_SURFACE} surface "
        f"(got {len(base_st)}: {[s for s, _ in base_st]})",
    )
    joined = " ".join(q for _, q in base_st).lower()
    _check(
        "sse" in joined or "event-stream" in joined or "stream" in joined,
        "the streaming-response evidence carries SSE / text-event-stream / "
        f"streaming-delivery vocabulary (got {[q for _, q in base_st]})",
    )

    # Honest scope: like async-job / pagination / cancel-job (not payment-rail), the
    # streaming-response evidence is host-FREE (the fired quote and its relative
    # /openapi.json surface name no vendor), so non-vacuity cannot anchor on the host
    # being inside the quote.
    _check(
        all(
            _MACHINE_SURFACE not in surf and _MACHINE_SURFACE not in quote
            for surf, quote in base_st
        ),
        "the streaming-response evidence is host-free (SSE/event-stream/streaming "
        "delivery structure, not a vendor name) — so this is a surface-presence, not "
        "a quote-anchored, invariance",
    )

    # Non-vacuity anchor (fixture level): the host IS present in the fixture surfaces
    # the classifier fetches, so a whole-fixture relabel genuinely rewrites the
    # classifier's overall input — the streaming-response signal surviving is not a
    # no-op over an absent host.
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    _check(
        _MACHINE_SURFACE in raw,
        f"{_MACHINE_SURFACE}: host present in the fixture surfaces (relabel rewrites "
        "real classifier input — the test is non-vacuous)",
    )

    relab = _discover_relabeled(_MACHINE_SURFACE, _NEUTRAL_HOST)
    relab_st = _stream_signals(relab)

    # (1) Same number of streaming-response matches — neither lost nor conjured.
    _check(
        len(relab_st) == len(base_st),
        "streaming-response match count invariant under relabel "
        f"(base {len(base_st)}, relabel {len(relab_st)})",
    )
    # (2) The SAME (host-normalized) surfaces carry the signal — it did not migrate.
    base_surf = sorted(s.replace(_MACHINE_SURFACE, _NEUTRAL_HOST) for s, _ in base_st)
    relab_surf = sorted(s for s, _ in relab_st)
    _check(
        relab_surf == base_surf,
        "streaming-response fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live streaming-response regex
    # (proving the fired form is structural — an SSE/event-stream/streaming-endpoint
    # delivery contract) and names no vendor host — the match keyed on the delivery
    # contract, not identity.
    st_re = dict(_offering._SIGNALS["metered_api"])[_STREAM_LABEL]
    for surf, quote in relab_st:
        _check(
            st_re.search(quote) is not None,
            f"relabeled streaming-response quote still matches the contract-structural signal: {quote!r}",
        )
        _check(
            _MACHINE_SURFACE not in quote and _MACHINE_SURFACE not in surf,
            f"vendor host absent from relabeled streaming-response evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# The FIRST signal-level companion in the digital_good bank (the four above all
# live in metered_api): `output-license` (Cycle 98 — the deliverable-RIGHTS leg
# of a digital good, in four host-free forms: a commercial-use licence
# ("commercial licen[cs]e/ing"), royalty-free terms, an explicit "usage rights"
# grant, or ownership of the produced artifact ("you own the output/render/…")).
# It is the digital-good "complete the job" RIGHTS leg: an agent that receives a
# generated render it has no licence to USE has not completed the commercial job,
# so a storefront granting usage rights on its output is more agent-completable at
# the digital-good layer. Deliverable rights are a property of what a storefront
# GRANTS — a licence, royalty-free terms, ownership of the render — never of WHO
# grants them, so the signal must be identity-invariant.
#
# SURFACE-PRESENCE, not quote-anchored (like error-contract / async-job, NOT
# payment-rail): the rights vocabulary is host-free by nature — "commercial
# licence", "royalty-free", "you own the output" name no vendor, so the fired
# QUOTES carry no host (asserted below). But driftflight.com is a STRONG
# surface-presence case: the signal fires on many surfaces and SEVERAL of them
# embed the host in the surface KEY (`agents.driftflight.com/llms.txt`,
# `.../llms-full.txt`, `.../manifest.json`). So the whole-fixture relabel
# genuinely rewrites the surface keys the signal fires on — the host-normalization
# step of the surface assertion does real work here, exactly as it does for
# error-contract, not a no-op over host-free surfaces. Under relabel the signal
# must survive with the SAME match count, on the SAME host-normalized surfaces,
# each quote STILL satisfying the live output-license regex, with the vendor host
# absent from every piece of rights evidence.
#
# This is the digital_good analog of the metered_api relabel guards
# (payment-rail Cycle 79, async-job 83, api-auth 87, error-contract this file):
# the first extension of the signal-level relabel family off the metered_api bank.
# ---------------------------------------------------------------------------
_LICENSE_LABEL = "output-license"


def _license_signals(prof) -> list:
    """The (surface, quote) pairs where the output-license signal fired, sorted."""
    return sorted(
        (s.surface, s.quote)
        for c in prof.claimed
        for s in c.signals
        if s.label == _LICENSE_LABEL
    )


def test_offering_relabel_invariance_output_license() -> None:
    """The digital-good rights grant keys on the licence/ownership form, not host."""
    print("test_offering_relabel_invariance_output_license")
    base, _ = _discover("driftflight.com")
    base_lic = _license_signals(base)

    # The signal genuinely fires on real captured evidence, and a commercial-USE
    # licence grant (the precision-critical form the signal must catch WITHOUT
    # firing on a bare software/model licence) is among it.
    _check(
        len(base_lic) >= 2,
        "output-license fires on >=2 real driftflight.com surfaces "
        f"(got {len(base_lic)}: {[s for s, _ in base_lic]})",
    )
    joined = " ".join(q for _, q in base_lic).lower()
    _check(
        re.search(r"\bcommercial licen[cs](?:e|es|ed|ing)\b", joined) is not None,
        "a commercial-use licence grant is among the output-license evidence",
    )

    # Honest scope: the rights evidence is host-FREE ("commercial licence",
    # "royalty-free", "you own the output" name no vendor), so non-vacuity cannot
    # anchor on the host being inside the quote — this is a surface-presence
    # invariance, like error-contract.
    _check(
        all("driftflight.com" not in quote for _, quote in base_lic),
        "the output-license evidence is host-free (licence / royalty-free / usage "
        "rights / ownership vocabulary, not a vendor name) — so this is a "
        "surface-presence, not a quote-anchored, invariance",
    )

    # Non-vacuity anchor (surface level, as for error-contract): the host is present
    # INSIDE the surface KEYS the signal fires on, so a whole-fixture relabel
    # genuinely rewrites the very surfaces the signal reads — the host-normalization
    # step of assertion (2) below does real work, not a no-op over host-free surfaces.
    _check(
        any("driftflight.com" in surf for surf, _ in base_lic),
        "the host appears inside >=1 output-license surface key — relabel rewrites "
        f"real surface input (surfaces {[s for s, _ in base_lic]})",
    )

    relab = _discover_relabeled("driftflight.com", _NEUTRAL_HOST)
    relab_lic = _license_signals(relab)

    # (1) Same number of output-license matches — the signal is neither lost nor conjured.
    _check(
        len(relab_lic) == len(base_lic),
        "output-license match count invariant under relabel "
        f"(base {len(base_lic)}, relabel {len(relab_lic)})",
    )
    # (2) The SAME logical surfaces carry the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    base_surf = sorted(s.replace("driftflight.com", _NEUTRAL_HOST) for s, _ in base_lic)
    relab_surf = sorted(s for s, _ in relab_lic)
    _check(
        relab_surf == base_surf,
        "output-license fires on the same (host-normalized) surfaces under relabel "
        f"(base {base_surf}, relabel {relab_surf})",
    )
    # (3) Each relabeled quote STILL satisfies the live output-license regex (proving
    # the fired form is a structural rights grant — a commercial licence / royalty-free
    # / usage rights / ownership of the deliverable) and names no vendor host — the
    # match keyed on the GRANTED right, not identity.
    lic_re = dict(_offering._SIGNALS["digital_good"])[_LICENSE_LABEL]
    for surf, quote in relab_lic:
        _check(
            lic_re.search(quote) is not None,
            f"relabeled output-license quote still matches the rights-structural signal: {quote!r}",
        )
        _check(
            "driftflight.com" not in quote and "driftflight.com" not in surf,
            f"vendor host absent from relabeled output-license evidence (surface {surf!r})",
        )


# ---------------------------------------------------------------------------
# The SECOND signal-level companion off the metered_api bank — and the THIRD
# archetype to join the signal-level relabel family (after metered_api's seven
# legs and digital_good's `output-license`): the subscription bank's `free-trial`
# (Cycle 114 — a no-cost evaluation of a recurring offer BEFORE billing begins).
# It is the subscription-archetype "provision the offer safely, without a human"
# leg: an agent that can start a free trial evaluates the whole recurring plan at
# $0 before committing to billing, so a subscription offer documenting one is more
# agent-completable. A trial offer is a property of what a storefront GRANTS — a
# free trial, a trial period/account/allowance, an N-day trial — never of WHO
# grants it, so the signal must be identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (unlike output-license, which
# rides driftflight.com's captured evidence): the `free-trial` vocabulary is
# host-free by nature ("free trial", "14-day trial account"), and on the real
# canonical fixture the signal fires on the /llms.txt, /pricing and homepage
# surfaces with NEITHER the host in the surface key NOR the host in the quote
# window (verified live) — so a whole-fixture relabel would leave the free-trial
# evidence byte-identical and the invariance would be VACUOUS. To make the relabel
# genuinely rewrite the classifier's input at the free-trial signal, this guard
# scans a synthetic subscription surface that deliberately seats the host INSIDE
# the trial evidence: the host is the surface KEY prefix AND sits adjacent to the
# trial phrase, so it lands inside the padded quote window (asserted non-vacuous
# below). Relabel the host everywhere, re-scan, and the free-trial signal must
# survive with the SAME match count, on the SAME host-normalized surface, its quote
# STILL satisfying the live free-trial regex, with the vendor host absent from all
# rewritten evidence. `_scan_surface` on synthetic prose is the same primitive the
# noise-surface guard uses directly.
#
# TEETH (precision, the free-trial signal's defining risk): a sibling synthetic
# surface carrying only the bare-"trial" false-positive senses the signal must
# REFUSE — a clinical trial, a court trial "on trial", "trial and error" — fires
# ZERO free-trial signals, proving the match keys on the FREE-trial STRUCTURE (a
# free / N-day / period-account-allowance trial, or a start/try-free offer), not on
# the word "trial"; and relabeling the host through that same distractor prose never
# CONJURES a free-trial claim.
# ---------------------------------------------------------------------------
_FREE_TRIAL_LABEL = "free-trial"
_FT_HOST = "acme-trials.example"  # a host bearing no archetype-signal word
_FT_SURFACE = f"agents.{_FT_HOST}/pricing"
# Host seated adjacent to the trial phrase so it lands in the padded quote window.
_FT_PROSE = (
    f"Start your {_FT_HOST} free trial today. {_FT_HOST} gives every new agent a "
    f"14-day trial account at no cost, so an agent can evaluate the {_FT_HOST} plan "
    f"before any recurring subscription charge begins."
)
# The bare-"trial" false-positive senses the free-trial signal must never match.
_FT_DISTRACTOR_SURFACE = f"agents.{_FT_HOST}/legal"
_FT_DISTRACTOR_PROSE = (
    f"The {_FT_HOST} clinical trial began last spring; the defendant remains on "
    f"trial. {_FT_HOST} learned this the hard way, through trial and error."
)


def _free_trial_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the subscription free-trial signal fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "subscription" and s.label == _FREE_TRIAL_LABEL
    )


def test_offering_relabel_invariance_free_trial() -> None:
    """The subscription free-trial offer keys on the trial form, not the host."""
    print("test_offering_relabel_invariance_free_trial")
    base = _free_trial_signals(_FT_SURFACE, _FT_PROSE)

    # The signal genuinely fires on the synthetic subscription evidence.
    _check(
        len(base) == 1,
        f"free-trial fires exactly once on the synthetic subscription surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's free-trial input
    # — this is not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _FT_HOST in base_surf and _FT_HOST in base_quote,
        f"the host is inside the free-trial surface key AND quote window — relabel "
        f"rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the bare-"trial" false-positive senses (clinical / court / error) fire
    # ZERO free-trial — the signal keys on the FREE-trial structure, not "trial".
    _check(
        _free_trial_signals(_FT_DISTRACTOR_SURFACE, _FT_DISTRACTOR_PROSE) == [],
        "bare-'trial' distractor prose (clinical trial / on trial / trial and error) "
        "fires no free-trial signal — the match is structural, not the word 'trial'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _FT_SURFACE.replace(_FT_HOST, _NEUTRAL_HOST)
    relab_prose = _FT_PROSE.replace(_FT_HOST, _NEUTRAL_HOST)
    _check(
        _FT_HOST not in relab_surface and _FT_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _free_trial_signals(relab_surface, relab_prose)

    # (1) Same match count — the free-trial signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"free-trial match count invariant under relabel (base {len(base)}, relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_FT_HOST, _NEUTRAL_HOST),
        "free-trial fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live free-trial regex (the fired
    # form is a structural trial offer — a free / 14-day / trial-account offer, not
    # the host) and names no vendor host — the match keyed on the GRANTED trial.
    ft_re = dict(_offering._SIGNALS["subscription"])[_FREE_TRIAL_LABEL]
    _check(
        ft_re.search(relab_quote) is not None,
        f"relabeled free-trial quote still matches the trial-structural signal: {relab_quote!r}",
    )
    _check(
        _FT_HOST not in relab_quote and _FT_HOST not in relab_surf,
        f"vendor host absent from relabeled free-trial evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# metered_api's NINTH signal-level companion (Cycle 130's `self-provisioning`,
# whose relabel-invariance TRUTH leg this is) — the agent-onboarding leg: whether
# an autonomous agent can OBTAIN API access with no human in the loop (no signup /
# provision its own identity / self-provision / no-human onboarding). It is the
# load-bearing precondition for every other metered_api leg — an API whose
# credentials only a human can issue is not agent-completable end-to-end no matter
# how cleanly it documents auth, rate limits, or errors. Self-provisioning is a
# property of what a storefront GRANTS an agent — the ability to onboard itself —
# never of WHO grants it, so the signal must be identity-invariant under a host
# relabel.
#
# Why a SYNTHETIC surface, not the real fixture (like free-trial / content-
# provenance, unlike output-license which rides driftflight.com's captured
# evidence): the `self-provisioning` vocabulary is host-free by nature ("no
# signup", "provision its own identity"), and on driftflight.com the signal fires
# on the homepage / agents.* docs surfaces with the host in the surface KEY but the
# fired QUOTE host-free (verified live) — so a whole-fixture relabel would leave the
# self-provisioning quote byte-identical and the invariance would be VACUOUS at the
# quote. To make the relabel genuinely rewrite the classifier's input at the
# self-provisioning signal, this guard scans a synthetic metered_api surface that
# deliberately seats the host INSIDE the self-provisioning evidence: the host is the
# surface KEY prefix AND sits adjacent to the "no signup" phrase, so it lands inside
# the padded quote window (asserted non-vacuous below). Relabel the host everywhere,
# re-scan, and the self-provisioning signal must survive with the SAME match count,
# on the SAME host-normalized surface, its quote STILL satisfying the live
# self-provisioning regex, with the vendor host absent from all rewritten evidence.
#
# TEETH (precision, the self-provisioning signal's defining risk — the OPPOSITE
# human-onboarding phrasing lives verbatim in the very fixtures it validates on): a
# sibling synthetic surface carrying only the human-gated / error / pricing / list
# senses the signal must REFUSE — "Human developers sign up on the dashboard for an
# API key" (the human path, present on BOTH canonical domains), the 401 "No API key,
# or the key is unknown or revoked" error (drift-flight.org's /docs row), "no signup
# fees" (the pricing sense the negative lookahead excludes), and "sign up for our
# newsletter" — fires ZERO self-provisioning signals, proving the match keys on the
# AFFIRMATIVE agentic self-provisioning STRUCTURE (no signup / provision its own
# identity / self-provision / no-human onboarding), never a bare "sign up" or a bare
# "no API key"; and relabeling the host through that same distractor prose never
# CONJURES a metered_api self-provisioning claim.
# ---------------------------------------------------------------------------
_SELF_PROV_LABEL = "self-provisioning"
_SP_HOST = "acme-agents.example"  # a host bearing no archetype-signal word
_SP_SURFACE = f"agents.{_SP_HOST}/docs"
# Host seated adjacent to the "no signup" phrase so it lands in the padded quote window.
_SP_PROSE = (
    f"{_SP_HOST} needs no signup: an autonomous agent can provision its own "
    f"identity and call the {_SP_HOST} metered API programmatically, paying per "
    f"request. There is no human onboarding."
)
# The human-onboarding / error / pricing / list senses self-provisioning must never
# match — the exact inverse phrasings present verbatim in the canonical fixtures.
_SP_DISTRACTOR_SURFACE = f"agents.{_SP_HOST}/signup"
_SP_DISTRACTOR_PROSE = (
    f"Human developers sign up on the {_SP_HOST} dashboard for an API key. No API "
    f"key, or the key is unknown or revoked, returns 401. Our plans have no signup "
    f"fees. Sign up for our newsletter."
)


def _self_prov_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the metered_api self-provisioning fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "metered_api" and s.label == _SELF_PROV_LABEL
    )


def test_offering_relabel_invariance_self_provisioning() -> None:
    """The agent self-onboarding claim keys on the no-signup structure, not host."""
    print("test_offering_relabel_invariance_self_provisioning")
    base = _self_prov_signals(_SP_SURFACE, _SP_PROSE)

    # The signal genuinely fires on the synthetic metered_api evidence.
    _check(
        len(base) == 1,
        f"self-provisioning fires exactly once on the synthetic metered_api surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's self-provisioning
    # input — this is not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _SP_HOST in base_surf and _SP_HOST in base_quote,
        f"the host is inside the self-provisioning surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the OPPOSITE human-onboarding / 401 / pricing / list senses fire ZERO
    # self-provisioning — the signal keys on the AFFIRMATIVE agentic self-onboarding
    # structure, never on a bare "sign up" or a bare "no API key".
    _check(
        _self_prov_signals(_SP_DISTRACTOR_SURFACE, _SP_DISTRACTOR_PROSE) == [],
        "human-onboarding distractor prose (dashboard sign up / 401 no API key / "
        "no signup fees / newsletter sign up) fires no self-provisioning signal — the "
        "match is the affirmative agentic structure, not the words 'sign up'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _SP_SURFACE.replace(_SP_HOST, _NEUTRAL_HOST)
    relab_prose = _SP_PROSE.replace(_SP_HOST, _NEUTRAL_HOST)
    _check(
        _SP_HOST not in relab_surface and _SP_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _self_prov_signals(relab_surface, relab_prose)

    # (1) Same match count — the self-provisioning signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"self-provisioning match count invariant under relabel (base {len(base)}, relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_SP_HOST, _NEUTRAL_HOST),
        "self-provisioning fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live self-provisioning regex (the
    # fired form is the structural no-signup / provision-own-identity capability, not
    # the host) and names no vendor host — the match keyed on the GRANTED self-onboarding.
    sp_re = dict(_offering._SIGNALS["metered_api"])[_SELF_PROV_LABEL]
    _check(
        sp_re.search(relab_quote) is not None,
        f"relabeled self-provisioning quote still matches the onboarding-structural signal: {relab_quote!r}",
    )
    _check(
        _SP_HOST not in relab_quote and _SP_HOST not in relab_surf,
        f"vendor host absent from relabeled self-provisioning evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# metered_api's TENTH signal-level companion (Cycle 134's `webhook-verification`,
# whose relabel-invariance TRUTH leg this is) — the async-callback TRUST leg: the
# security sibling of `async-job`. Where `async-job` says a webhook DELIVERY
# channel EXISTS (a webhook url/endpoint, register/configure a webhook), NONE of
# the other legs says whether the agent can TRUST that an inbound callback is
# GENUINELY from the API rather than a forged/spoofed webhook. An agent that acts
# on an UNVERIFIED "job complete" webhook can be tricked by a spoofed callback into
# treating fabricated output as real or releasing a payment, so a documented
# webhook-verification contract (a webhook signing secret, a webhook signature,
# verifying that inbound webhooks are authentic) is MORE agent-completable — and
# it dovetails with the $0-only capital-safety ethos: never act or pay on a forged
# callback. Webhook authenticity is a property of the async CONTRACT a storefront
# publishes — a signing secret, a signature to check — never of WHO publishes it,
# so the signal must be identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (like free-trial / self-
# provisioning / content-provenance, unlike output-license which rides
# driftflight.com's captured evidence): the `webhook-verification` vocabulary is
# host-free by nature ("a webhook signature", "verify that inbound webhooks are
# authentic"), and on the real api.replicate.com fixture the signal fires on the
# /openapi.json surface with the host in NEITHER the surface key NOR the fired
# quote window (verified live — the `/webhooks/default/secret` "signing secret ...
# used to verify that webhook requests are coming from ..." description) — so a
# whole-fixture relabel would leave the webhook-verification evidence byte-identical
# and the invariance would be VACUOUS. To make the relabel genuinely rewrite the
# classifier's input at the webhook-verification signal, this guard scans a
# synthetic metered_api surface that deliberately seats the host INSIDE the
# webhook-verification evidence: the host is the surface KEY prefix AND sits
# adjacent to the "webhook signature" phrase, so it lands inside the padded quote
# window (asserted non-vacuous below). Relabel the host everywhere, re-scan, and
# the webhook-verification signal must survive with the SAME match count, on the
# SAME host-normalized surface, its quote STILL satisfying the live
# webhook-verification regex, with the vendor host absent from all rewritten
# evidence.
#
# TEETH (precision, the webhook-verification signal's defining risk — a
# signature/secret is a heavily overloaded token): a sibling synthetic surface
# carrying only the signature-shaped senses the signal must REFUSE — a brand
# "signature look", the x402 payment-proof "verifies the signature locally", a
# SIGNED-URL "signing secret" + `name: signature` query param (URL signing, not a
# webhook), a webhook that only EXISTS ("register a webhook URL", `async-job`'s
# turf), and a contract/digital signature — fires ZERO webhook-verification
# signals, proving the match keys on the webhook-AUTHENTICITY STRUCTURE (a
# webhook-signature / a signing secret FOR a webhook / verifying inbound webhooks /
# webhook requests are authentic), never a bare "signature" or "signing secret"
# untethered from a webhook; and relabeling the host through that same distractor
# prose never CONJURES a metered_api webhook-verification claim.
# ---------------------------------------------------------------------------
_WEBHOOK_VERIFY_LABEL = "webhook-verification"
_WV_HOST = "acme-hooks.example"  # a host bearing no archetype-signal word
_WV_SURFACE = f"agents.{_WV_HOST}/docs"
# Host seated adjacent to the "webhook signature" phrase so it lands in the padded
# quote window.
_WV_PROSE = (
    f"Every {_WV_HOST} callback carries a webhook signature, so an autonomous agent "
    f"can verify that inbound webhooks from {_WV_HOST} are authentic before acting on "
    f"a job-complete notification."
)
# The signature-shaped false-positive senses webhook-verification must never match —
# a brand signature, an x402 payment-proof signature, a SIGNED-URL signing secret, a
# webhook that only EXISTS, and a contract signature.
_WV_DISTRACTOR_SURFACE = f"agents.{_WV_HOST}/legal"
_WV_DISTRACTOR_PROSE = (
    f"The {_WV_HOST} brand signature look is unmistakable. The x402 client verifies "
    f"the signature locally. Download via a signed URL whose signing secret is rotated "
    f"hourly; the name: signature query param authenticates the link. Register a webhook "
    f"URL to receive callbacks. Sign the digital contract with your signature."
)


def _webhook_verify_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the metered_api webhook-verification fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "metered_api" and s.label == _WEBHOOK_VERIFY_LABEL
    )


def test_offering_relabel_invariance_webhook_verification() -> None:
    """The async-callback trust claim keys on the webhook-authenticity form, not host."""
    print("test_offering_relabel_invariance_webhook_verification")
    base = _webhook_verify_signals(_WV_SURFACE, _WV_PROSE)

    # The signal genuinely fires on the synthetic metered_api evidence.
    _check(
        len(base) == 1,
        f"webhook-verification fires exactly once on the synthetic metered_api surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's webhook-verification
    # input — this is not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _WV_HOST in base_surf and _WV_HOST in base_quote,
        f"the host is inside the webhook-verification surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the signature-shaped false-positive senses (brand signature / x402 verify /
    # signed-URL signing secret / webhook-exists / contract signature) fire ZERO
    # webhook-verification — the signal keys on the webhook-AUTHENTICITY structure,
    # never on a bare "signature" or "signing secret" untethered from a webhook.
    _check(
        _webhook_verify_signals(_WV_DISTRACTOR_SURFACE, _WV_DISTRACTOR_PROSE) == [],
        "signature-shaped distractor prose (brand signature / x402 verify-locally / "
        "signed-URL signing secret / register-a-webhook-URL / contract signature) fires "
        "no webhook-verification signal — the match is the webhook-authenticity structure, "
        "not the words 'signature'/'signing secret'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _WV_SURFACE.replace(_WV_HOST, _NEUTRAL_HOST)
    relab_prose = _WV_PROSE.replace(_WV_HOST, _NEUTRAL_HOST)
    _check(
        _WV_HOST not in relab_surface and _WV_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _webhook_verify_signals(relab_surface, relab_prose)

    # (1) Same match count — the webhook-verification signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"webhook-verification match count invariant under relabel (base {len(base)}, relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_WV_HOST, _NEUTRAL_HOST),
        "webhook-verification fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live webhook-verification regex (the
    # fired form is the structural webhook-authenticity contract — a webhook signature /
    # verify inbound webhooks, not the host) and names no vendor host — the match keyed
    # on the async-callback TRUST contract, not identity.
    wv_re = dict(_offering._SIGNALS["metered_api"])[_WEBHOOK_VERIFY_LABEL]
    _check(
        wv_re.search(relab_quote) is not None,
        f"relabeled webhook-verification quote still matches the authenticity-structural signal: {relab_quote!r}",
    )
    _check(
        _WV_HOST not in relab_quote and _WV_HOST not in relab_surf,
        f"vendor host absent from relabeled webhook-verification evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# digital_good's SECOND signal-level companion — and the tenth leg of the
# signal-level relabel family (metered_api's seven + digital_good's
# `output-license` + subscription's `free-trial`): the digital_good bank's
# `content-provenance` (Cycle 118 — the trust/authenticity leg, the MEANS to
# verify a generated deliverable is genuine, MIRROR of `output-license`'s RIGHT
# to use it). An agent that obtains a render carrying embedded C2PA content
# credentials / a provenance manifest can confirm the asset's origin and use it
# in a provenance-aware pipeline, so a storefront that records provenance on its
# output is more agent-completable at the digital-good layer. Provenance is a
# property of the DELIVERABLE — C2PA credentials, a content/media provenance
# record — never of WHO vends it, so the signal must be identity-invariant under
# a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (like `free-trial`, unlike
# `output-license` which rides driftflight.com's captured evidence): the
# `content-provenance` vocabulary is host-free by nature ("C2PA content
# credentials", "records provenance metadata"), and on the real canonical pair
# the signal fires on the homepage / /docs / /pricing / /llms.txt surfaces with
# the host in NEITHER the quote window NOR (mostly) the surface key — even on the
# `agents.driftflight.com/*` surfaces the host sits in the surface KEY but the
# C2PA quote is host-free (verified live). So a whole-fixture relabel would leave
# the provenance evidence byte-identical and the invariance would be VACUOUS. To
# genuinely rewrite the classifier's input at the provenance signal, this guard
# scans a synthetic digital_good surface that deliberately seats the host INSIDE
# the provenance evidence: the host is the surface KEY prefix AND sits adjacent to
# the C2PA phrase, so it lands inside the padded quote window (asserted
# non-vacuous below). Relabel the host everywhere, re-scan, and the
# content-provenance signal must survive with the SAME match count, on the SAME
# host-normalized surface, its quote STILL satisfying the live content-provenance
# regex, with the vendor host absent from all rewritten evidence.
#
# TEETH (precision, the content-provenance signal's defining risk): a sibling
# synthetic surface carrying only the bare-"provenance"/"credentials"
# false-positive senses the signal must REFUSE — art & wine provenance, "data
# provenance" (a data_retrieval concern), login "credentials", and the
# api.replicate-style "watermarking for provenance" hosted-MODEL-feature phrasing
# — fires ZERO content-provenance signals, proving the match keys on the
# content-authenticity STRUCTURE (C2PA / content credentials / a media-output
# provenance record), not on the words "provenance"/"credentials"; and relabeling
# the host through that distractor prose never CONJURES a digital_good claim.
# ---------------------------------------------------------------------------
_PROVENANCE_LABEL = "content-provenance"
_CP_HOST = "acme-renders.example"  # a host bearing no content-provenance signal word
_CP_SURFACE = f"agents.{_CP_HOST}/docs"
# Host seated adjacent to the C2PA phrase so it lands in the padded quote window.
_CP_PROSE = (
    f"{_CP_HOST} embeds C2PA content credentials on every render, so an agent can "
    f"verify the {_CP_HOST} asset is genuine before use."
)
# The bare-"provenance"/"credentials" false-positive senses it must never match.
_CP_DISTRACTOR_SURFACE = f"agents.{_CP_HOST}/legal"
_CP_DISTRACTOR_PROSE = (
    f"The {_CP_HOST} sommelier documents each bottle provenance; a museum verified "
    f"the painting provenance. Users sign in with their credentials. The model "
    f"embeds invisible watermarking for provenance on all generated images, and "
    f"data provenance is logged downstream."
)


def _provenance_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the digital_good content-provenance fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "digital_good" and s.label == _PROVENANCE_LABEL
    )


def test_offering_relabel_invariance_content_provenance() -> None:
    """The digital_good content-provenance keys on the C2PA form, not the host."""
    print("test_offering_relabel_invariance_content_provenance")
    base = _provenance_signals(_CP_SURFACE, _CP_PROSE)

    # The signal genuinely fires on the synthetic digital_good evidence.
    _check(
        len(base) == 1,
        f"content-provenance fires exactly once on the synthetic surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's provenance input
    # — this is not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _CP_HOST in base_surf and _CP_HOST in base_quote,
        f"the host is inside the content-provenance surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the bare-"provenance"/"credentials" senses (art / wine / login /
    # data provenance / "watermarking for provenance" model-feature) fire ZERO —
    # the signal keys on the content-authenticity structure, not the words.
    _check(
        _provenance_signals(_CP_DISTRACTOR_SURFACE, _CP_DISTRACTOR_PROSE) == [],
        "bare-'provenance'/'credentials' distractor prose (art/wine/data provenance, "
        "login credentials, watermarking-for-provenance) fires no content-provenance "
        "signal — the match is structural, not the word 'provenance'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _CP_SURFACE.replace(_CP_HOST, _NEUTRAL_HOST)
    relab_prose = _CP_PROSE.replace(_CP_HOST, _NEUTRAL_HOST)
    _check(
        _CP_HOST not in relab_surface and _CP_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _provenance_signals(relab_surface, relab_prose)

    # (1) Same match count — the provenance signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"content-provenance match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_CP_HOST, _NEUTRAL_HOST),
        "content-provenance fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live content-provenance regex (the
    # fired form is a C2PA / content-credentials record, not the host) and names no
    # vendor host — the match keyed on the DELIVERABLE's provenance, not who vends it.
    cp_re = dict(_offering._SIGNALS["digital_good"])[_PROVENANCE_LABEL]
    _check(
        cp_re.search(relab_quote) is not None,
        f"relabeled content-provenance quote still matches the authenticity-structural "
        f"signal: {relab_quote!r}",
    )
    _check(
        _CP_HOST not in relab_quote and _CP_HOST not in relab_surf,
        f"vendor host absent from relabeled content-provenance evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the digital_good OUTPUT RESOLUTION
# leg (Cycle 138 COVERAGE, PR #125). The eleventh digital_good signal to join
# the signal-level relabel family and the TRUTH leg of the output-resolution
# COVERAGE→TRUTH→READOUT arc (mirroring webhook-verification 134/135/136 and
# free-trial 114/115/116). It is the digital_good output-SPEC leg: the
# physical SHAPE of the deliverable — its output RESOLUTION / pixel DIMENSIONS
# / ASPECT RATIO — an agent must parameterize its request with and can rely on
# (distinct from generation/render = WHAT is produced, hosted-output = WHERE
# delivered, output-license = rights, content-provenance = trust). The output
# resolution of a generated deliverable is a property of the DELIVERABLE's
# spec (a `maxResolution` field, a print resolution in px, a WxH pixel
# dimension, an aspect ratio), never of who vends it, so the signal must be
# identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (mirroring free-trial 115 /
# content-provenance 119, NOT output-license which rides captured evidence):
# the output-resolution vocabulary is host-FREE by nature — the fired quote
# carries a resolution/dimension token (`maxResolution of 4096px`), not the
# vendor's name — and on the real canonical pair the signal fires (the /docs
# `"maxResolution"` block + the homepage "print resolution") with the host in
# NEITHER the surface key NOR the quote window, so a whole-fixture relabel
# would leave the resolution evidence byte-identical and the invariance would
# be VACUOUS. To make the relabel genuinely rewrite the classifier's input at
# THIS signal, this guard scans a synthetic generation-storefront surface that
# deliberately seats the host INSIDE the resolution evidence: the host is the
# surface KEY prefix AND sits adjacent to the `maxResolution` phrase on both
# sides, so it lands inside the padded quote window (asserted non-vacuous
# below). Relabel the host everywhere, re-scan, and the output-resolution
# signal must survive with the SAME match count, on the SAME host-normalized
# surface, its quote STILL satisfying the live output-resolution regex, with
# the vendor host absent from all rewritten evidence.
#
# TEETH (precision, the output-resolution signal's defining risk): a sibling
# synthetic surface carrying only the bare-"resolution" false-positive senses
# the signal must REFUSE — "dispute resolution", a "New Year resolution",
# "DNS resolution", the api.replicate-style hosted-MODEL-feature phrasing
# ("Super resolution", "Enhance image resolution"), and the screen / monitor /
# display HARDWARE resolutions (the viewer's device, not the deliverable's
# spec) — fires ZERO output-resolution signals, proving the match keys on the
# output-SPEC structure (a `maxResolution` key / a print or explicit-pixel
# resolution / a WxH dimension / an aspect ratio), not on the word
# "resolution"; and relabeling the host through that distractor prose never
# CONJURES a digital_good claim on a site that merely says "resolution".
# ---------------------------------------------------------------------------
_OR_LABEL = "output-resolution"
_OR_HOST = "acme-studio.example"  # a host bearing no archetype-signal word
_OR_SURFACE = f"agents.{_OR_HOST}/docs"
# Host seated adjacent to the maxResolution phrase on both sides so it lands in
# the padded quote window (not merely in the surface key).
_OR_PROSE = f"{_OR_HOST} documents a maxResolution of 4096px for {_OR_HOST} renders."
# The bare-"resolution" false-positive senses the output-resolution signal must
# never match: dispute/New-Year/DNS resolution, the hosted-model-feature
# "Super resolution"/"Enhance image resolution" trap, and screen/monitor/display
# HARDWARE resolutions (the viewer's device, not the deliverable's output spec).
_OR_DISTRACTOR_SURFACE = f"agents.{_OR_HOST}/hardware"
_OR_DISTRACTOR_PROSE = (
    f"{_OR_HOST} offers dispute resolution and DNS resolution; a New Year "
    f"resolution too. The hosted model does Super resolution and can Enhance "
    f"image resolution. View on a screen resolution of 1080px or a monitor "
    f"resolution 2560px display."
)


def _output_resolution_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the digital_good output-resolution fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "digital_good" and s.label == _OR_LABEL
    )


def test_offering_relabel_invariance_output_resolution() -> None:
    """The digital_good output-resolution keys on the output-spec form, not the host."""
    print("test_offering_relabel_invariance_output_resolution")
    base = _output_resolution_signals(_OR_SURFACE, _OR_PROSE)

    # The signal genuinely fires on the synthetic generation-storefront evidence.
    _check(
        len(base) == 1,
        f"output-resolution fires exactly once on the synthetic surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's resolution
    # input — not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _OR_HOST in base_surf and _OR_HOST in base_quote,
        f"the host is inside the output-resolution surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the bare-"resolution" senses (dispute / New Year / DNS resolution,
    # the Super-/Enhance-image-resolution model-feature trap, and screen/monitor/
    # display HARDWARE resolutions) fire ZERO — the signal keys on the output-spec
    # structure, not the word "resolution".
    _check(
        _output_resolution_signals(_OR_DISTRACTOR_SURFACE, _OR_DISTRACTOR_PROSE) == [],
        "bare-'resolution' distractor prose (dispute/New-Year/DNS resolution, "
        "Super-/Enhance-image-resolution model feature, screen/monitor/display "
        "hardware resolution) fires no output-resolution signal — the match is "
        "structural (output-spec), not the word 'resolution'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _OR_SURFACE.replace(_OR_HOST, _NEUTRAL_HOST)
    relab_prose = _OR_PROSE.replace(_OR_HOST, _NEUTRAL_HOST)
    _check(
        _OR_HOST not in relab_surface and _OR_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _output_resolution_signals(relab_surface, relab_prose)

    # (1) Same match count — the output-resolution signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"output-resolution match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_OR_HOST, _NEUTRAL_HOST),
        "output-resolution fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live output-resolution regex (the
    # fired form is an output-spec token — a maxResolution/pixel/dimension/aspect —
    # not the host) and names no vendor host — the match keyed on the DELIVERABLE's
    # output spec, not who vends it.
    or_re = dict(_offering._SIGNALS["digital_good"])[_OR_LABEL]
    _check(
        or_re.search(relab_quote) is not None,
        f"relabeled output-resolution quote still matches the output-spec signal: {relab_quote!r}",
    )
    _check(
        _OR_HOST not in relab_quote and _OR_HOST not in relab_surf,
        f"vendor host absent from relabeled output-resolution evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the physical_good PRICED CATALOG
# LISTING. The FIRST physical_good leg to join the signal-level relabel family
# (the ten prior legs are metered_api's seven + digital_good's `output-license`
# and `content-provenance` + subscription's `free-trial`): the physical_good
# bank's `priced-listing` (Cycle 122 — a decimal money amount quoted directly
# beside an in-stock / add-to-cart control, "£51.77 In stock", "$12.99 Add to
# basket"). It is the physical_good "understand the offer" PRICE leg: to DECIDE
# and FULFILL a physical purchase an agent must read the concrete price of a
# purchasable, in-stock catalog item. A priced listing is a property of the
# CATALOG STRUCTURE a storefront publishes (an amount adjacent to availability),
# never of who published it, so the signal must be identity-invariant under a
# host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (mirroring free-trial 115 and
# content-provenance 119, NOT output-license which rides captured evidence): the
# priced-listing vocabulary is host-FREE by nature — the fired quote carries a
# price + availability phrase ("£51.77 In stock"), not the vendor's name — and on
# the real books.toscrape.com fixture the 60 priced listings fire with the host in
# NEITHER the surface key NOR the quote window, so a whole-fixture relabel would
# leave the priced-listing evidence byte-identical and the invariance would be
# VACUOUS. To make the relabel genuinely rewrite the classifier's input at THIS
# signal, this guard scans a synthetic retail catalog surface that deliberately
# seats the host INSIDE the priced-listing evidence: the host is the surface KEY
# prefix AND sits adjacent to the price on both sides, so it lands inside the
# padded quote window (asserted non-vacuous below). Relabel the host everywhere,
# re-scan, and the priced-listing signal must survive with the SAME match count,
# on the SAME host-normalized surface, its quote STILL satisfying the live
# priced-listing regex, with the vendor host absent from all rewritten evidence.
# `_scan_surface` on synthetic prose is the same primitive the noise-surface and
# free-trial guards use directly.
#
# TEETH (precision, the priced-listing signal's defining risk): a sibling synthetic
# surface carrying only BARE currency amounts in metered/subscription pricing prose
# — "$0.01 per API call", "$29.00 per month", "$5.00 per 1,000 requests", none
# adjacent to in-stock / add-to-cart availability — must fire ZERO priced-listing
# signals, proving the match keys on the PRICED-CATALOG-LISTING structure (a decimal
# amount beside availability), not on the presence of a money amount; and relabeling
# the host through that same distractor prose never CONJURES a physical_good claim on
# an API storefront that merely lists dollar amounts (the operator NA-preservation
# the signal's canonical guard already pins on the real fixtures).
# ---------------------------------------------------------------------------
_PL_LABEL = "priced-listing"
_PL_HOST = "acme-goods.example"  # a host bearing no archetype-signal word
_PL_SURFACE = f"agents.{_PL_HOST}/catalog"
# Host seated adjacent to the priced listing on both sides so it lands in the
# padded quote window (not merely in the surface key).
_PL_PROSE = (
    f"At {_PL_HOST}: hardcover novel £51.77 In stock at {_PL_HOST}, add to "
    f"basket to ship it from the warehouse."
)
# The bare-currency false-positive senses the priced-listing signal must never
# match: metered/subscription pricing with decimal amounts NOT beside availability.
_PL_DISTRACTOR_SURFACE = f"agents.{_PL_HOST}/pricing"
_PL_DISTRACTOR_PROSE = (
    f"{_PL_HOST} bills $0.01 per API call and $29.00 per month; volume plans run "
    f"$5.00 per 1,000 requests. No physical goods are stocked by {_PL_HOST}."
)


def _priced_listing_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the physical_good priced-listing signal fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "physical_good" and s.label == _PL_LABEL
    )


def test_offering_relabel_invariance_priced_listing() -> None:
    """The physical_good priced-listing keys on the price+availability form, not the host."""
    print("test_offering_relabel_invariance_priced_listing")
    base = _priced_listing_signals(_PL_SURFACE, _PL_PROSE)

    # The signal genuinely fires on the synthetic retail catalog evidence.
    _check(
        len(base) == 1,
        f"priced-listing fires exactly once on the synthetic catalog surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's priced-listing
    # input — not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _PL_HOST in base_surf and _PL_HOST in base_quote,
        f"the host is inside the priced-listing surface key AND quote window — relabel "
        f"rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: bare-currency metered/subscription pricing prose (per API call / per
    # month / per 1,000 requests, none beside availability) fires ZERO priced-listing
    # — the signal keys on the priced-catalog-listing structure, not a money amount.
    _check(
        _priced_listing_signals(_PL_DISTRACTOR_SURFACE, _PL_DISTRACTOR_PROSE) == [],
        "bare-currency distractor prose ($0.01 per API call / $29.00 per month / "
        "$5.00 per 1,000 requests) fires no priced-listing signal — the match is "
        "structural (price beside availability), not the presence of a money amount",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _PL_SURFACE.replace(_PL_HOST, _NEUTRAL_HOST)
    relab_prose = _PL_PROSE.replace(_PL_HOST, _NEUTRAL_HOST)
    _check(
        _PL_HOST not in relab_surface and _PL_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _priced_listing_signals(relab_surface, relab_prose)

    # (1) Same match count — the priced-listing signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"priced-listing match count invariant under relabel (base {len(base)}, relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_PL_HOST, _NEUTRAL_HOST),
        "priced-listing fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live priced-listing regex (the fired
    # form is a structural price-beside-availability listing, not the host) and names
    # no vendor host — the match keyed on the PRICED CATALOG LISTING, not identity.
    pl_re = dict(_offering._SIGNALS["physical_good"])[_PL_LABEL]
    _check(
        pl_re.search(relab_quote) is not None,
        f"relabeled priced-listing quote still matches the price-structural signal: {relab_quote!r}",
    )
    _check(
        _PL_HOST not in relab_quote and _PL_HOST not in relab_surf,
        f"vendor host absent from relabeled priced-listing evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the metered_api PAYMENT RECEIPT leg
# (Cycle 142 COVERAGE, PR #132). The newest metered_api signal to join the
# signal-level relabel family and the TRUTH leg of the payment-receipt
# COVERAGE→TRUTH→READOUT arc (mirroring webhook-verification 134/135/136 and
# output-resolution 138/139/140). It is the metered_api ACCOUNTING leg — the
# capital-safety COUNTERPART to the payment RAILS (x402 / agent-payment-rail say
# an agent can PAY; payment-receipt is the machine-readable proof-of-payment
# that comes BACK, which the agent logs to reconcile its own spend). The receipt
# an agent gets back is a property of the paid-response CONTRACT (a receipt
# header, a payment/settlement receipt, a serialized receipt, a spend record, an
# explicit proof of payment), never of WHO vends it, so the signal must be
# identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (mirroring webhook-verification
# 135 / output-resolution 139, NOT output-license which rides captured
# evidence): the payment-receipt vocabulary is host-FREE by nature — the fired
# quote carries a receipt/spend-record token ("a payment receipt", "a receipt
# header"), not the vendor's name — and on the real captured driftflight.com
# agent docs (agents.driftflight.com/llms-full.txt) the signal fires with the
# host in the surface KEY but NOT the quote window, so a whole-fixture relabel
# would leave the receipt evidence byte-identical and the invariance would be
# VACUOUS. To make the relabel genuinely rewrite the classifier's input at THIS
# signal, this guard scans a synthetic metered_api surface that deliberately
# seats the host INSIDE the receipt evidence: the host is the surface KEY prefix
# AND sits adjacent to the payment-receipt phrase on both sides, so it lands in
# the padded quote window (asserted non-vacuous below). Relabel the host
# everywhere, re-scan, and the payment-receipt signal must survive with the SAME
# match count, on the SAME host-normalized surface, its quote STILL satisfying
# the live payment-receipt regex, with the vendor host absent from all rewritten
# evidence.
#
# TEETH (precision, the payment-receipt signal's defining risk — a bare
# "receipt" is a false-positive minefield): a sibling synthetic surface carrying
# only the bare-"receipt" senses the signal must REFUSE — an EMAIL/ORDER receipt
# at retail checkout, a READ receipt ("enable read receipts"), "in receipt of
# your message", a warehouse "receipt of goods" — fires ZERO payment-receipt
# signals, proving the match keys on the proof-of-payment STRUCTURE (a receipt
# HEADER / a payment/settlement receipt / a serialized receipt / a spend record /
# proof of payment), not on the bare word "receipt"; and relabeling the host
# through that distractor prose never CONJURES a metered_api claim on a site that
# merely says "receipt".
# ---------------------------------------------------------------------------
_PR_LABEL = "payment-receipt"
_PR_HOST = "acme-meter.example"  # a host bearing no payment-receipt signal word
_PR_SURFACE = f"agents.{_PR_HOST}/llms-full.txt"
# Host seated adjacent to the payment-receipt phrase on both sides so it lands in
# the padded quote window (not merely in the surface key).
_PR_PROSE = f"{_PR_HOST} returns a payment receipt on every paid {_PR_HOST} response."
# The bare-"receipt" false-positive senses the payment-receipt signal must never
# match: an email/order receipt at checkout, a read receipt, "in receipt of", a
# warehouse receipt of goods.
_PR_DISTRACTOR_SURFACE = f"agents.{_PR_HOST}/support"
_PR_DISTRACTOR_PROSE = (
    f"{_PR_HOST} emails an order receipt at checkout; enable read receipts for "
    f"chat. We are in receipt of your message. A warehouse notes receipt of goods."
)


def _payment_receipt_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the metered_api payment-receipt fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "metered_api" and s.label == _PR_LABEL
    )


def test_offering_relabel_invariance_payment_receipt() -> None:
    """The metered_api payment-receipt keys on the proof-of-payment form, not the host."""
    print("test_offering_relabel_invariance_payment_receipt")
    base = _payment_receipt_signals(_PR_SURFACE, _PR_PROSE)

    # The signal genuinely fires on the synthetic metered_api evidence.
    _check(
        len(base) == 1,
        f"payment-receipt fires exactly once on the synthetic metered_api surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's payment-receipt
    # input — not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _PR_HOST in base_surf and _PR_HOST in base_quote,
        f"the host is inside the payment-receipt surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the bare-"receipt" senses (order/email receipt at checkout, read
    # receipt, "in receipt of", warehouse receipt of goods) fire ZERO — the signal
    # keys on the proof-of-payment structure, never on the bare word "receipt".
    _check(
        _payment_receipt_signals(_PR_DISTRACTOR_SURFACE, _PR_DISTRACTOR_PROSE) == [],
        "bare-'receipt' distractor prose (order/email receipt at checkout, read "
        "receipts, 'in receipt of', warehouse receipt of goods) fires no "
        "payment-receipt signal — the match is the proof-of-payment structure "
        "(receipt header / payment-settlement receipt / serialized receipt / spend "
        "record / proof of payment), not the word 'receipt'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _PR_SURFACE.replace(_PR_HOST, _NEUTRAL_HOST)
    relab_prose = _PR_PROSE.replace(_PR_HOST, _NEUTRAL_HOST)
    _check(
        _PR_HOST not in relab_surface and _PR_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _payment_receipt_signals(relab_surface, relab_prose)

    # (1) Same match count — the payment-receipt signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"payment-receipt match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_PR_HOST, _NEUTRAL_HOST),
        "payment-receipt fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live payment-receipt regex (the
    # fired form is a proof-of-payment token — a payment receipt / receipt header /
    # spend record — not the host) and names no vendor host — the match keyed on
    # the paid-response ACCOUNTING contract, not who vends it.
    pr_re = dict(_offering._SIGNALS["metered_api"])[_PR_LABEL]
    _check(
        pr_re.search(relab_quote) is not None,
        f"relabeled payment-receipt quote still matches the proof-of-payment signal: {relab_quote!r}",
    )
    _check(
        _PR_HOST not in relab_quote and _PR_HOST not in relab_surf,
        f"vendor host absent from relabeled payment-receipt evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the subscription PLAN-PURCHASE leg
# (Cycle 146 COVERAGE, PR #140). The newest subscription signal to join the
# signal-level relabel family and the TRUTH leg of the plan-purchase
# COVERAGE→TRUTH(→READOUT) arc (mirroring payment-receipt 142/143/144 and
# output-resolution 138/139/140). It is the subscription-archetype COMMIT leg —
# the counterpart to metered_api's `self-provisioning`: `subscription` /
# `per-month` / `seat-licensing` all say the site documents a recurring PRICE,
# and `free-trial` says it can be evaluated at $0, but NONE says the agent can
# autonomously COMMIT to the recurring plan. plan-purchase is that "take on the
# recurring commitment without a human" leg — a `/plans/{id}/purchase` endpoint,
# a purchasable plan, a BUY/PURCHASE/ACTIVATE verb naming a credit-or-
# subscription plan. Whether an agent can programmatically commit to a plan is a
# property of the plan-purchase CONTRACT the site exposes, never of WHO vends
# it, so the signal must be identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (mirroring payment-receipt 143 /
# webhook-verification 135 / output-resolution 139, NOT output-license which
# rides captured evidence): the plan-purchase vocabulary is host-FREE by nature —
# the fired quote carries an endpoint path / a purchasable-plan / a buy-a-plan
# token, not the vendor's name — and on the real captured driftflight.com agent
# docs (agents.driftflight.com/llms-full.txt) the signal fires with the host in
# the surface KEY but NOT the quote window, so a whole-fixture relabel would
# leave the plan-purchase evidence byte-identical and the invariance would be
# VACUOUS. To make the relabel genuinely rewrite the classifier's input at THIS
# signal, this guard scans a synthetic subscription surface that deliberately
# seats the host INSIDE the plan-purchase evidence: the host is the surface KEY
# prefix AND sits adjacent to the `/plans/{id}/purchase` phrase (asserted
# non-vacuous below). Relabel the host everywhere, re-scan, and the plan-purchase
# signal must survive with the SAME match count, on the SAME host-normalized
# surface, its quote STILL satisfying the live plan-purchase regex, with the
# vendor host absent from all rewritten evidence.
#
# TEETH (precision, the plan-purchase signal's defining risk — bare "plan" /
# "subscribe to a plan" / "subscription plans" is a false-positive minefield
# present verbatim in BOTH canonical fixtures' human-checkout prose): a sibling
# synthetic surface carrying only the human, non-programmatic senses the signal
# must REFUSE — "subscribe to a plan on the pricing page" (the human checkout,
# the exact inverse of the capability), "issued on the dashboard after
# subscribing to a plan" (dashboard onboarding), and bare "subscription plans"
# marketing — fires ZERO plan-purchase signals, proving the match keys on the
# PROGRAMMATIC purchase STRUCTURE (a `/plans/{id}/purchase` endpoint / a
# purchasable plan / a buy-or-activate verb over a credit-or-subscription plan),
# not on the bare word "plan"; and relabeling the host through that human prose
# never CONJURES a plan-purchase claim on a site whose only plan path is a human
# clicking through a checkout.
# ---------------------------------------------------------------------------
_PP_LABEL = "plan-purchase"
_PP_HOST = "acme-vend.example"  # a host bearing no plan-purchase signal word
_PP_SURFACE = f"agents.{_PP_HOST}/llms-full.txt"
# Host seated adjacent to the `/plans/{id}/purchase` phrase (surface key prefix +
# the sentence subject) so it lands in the padded quote window, not merely the
# surface key.
_PP_PROSE = (
    f"{_PP_HOST} exposes POST /plans/pro/purchase so an agent can buy a "
    f"subscription plan on {_PP_HOST}."
)
# The human, non-programmatic plan senses the plan-purchase signal must never
# match: the pricing-page human checkout, the dashboard onboarding path after
# subscribing, and bare "subscription plans" marketing.
_PP_DISTRACTOR_SURFACE = f"agents.{_PP_HOST}/pricing"
_PP_DISTRACTOR_PROSE = (
    f"{_PP_HOST} lists subscription plans on its pricing page; subscribe to a "
    f"plan on the pricing page, or finish onboarding on the dashboard after "
    f"subscribing to a plan."
)


def _plan_purchase_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the subscription plan-purchase fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "subscription" and s.label == _PP_LABEL
    )


def test_offering_relabel_invariance_plan_purchase() -> None:
    """The subscription plan-purchase keys on the programmatic-commit form, not the host."""
    print("test_offering_relabel_invariance_plan_purchase")
    base = _plan_purchase_signals(_PP_SURFACE, _PP_PROSE)

    # The signal genuinely fires on the synthetic subscription evidence.
    _check(
        len(base) == 1,
        f"plan-purchase fires exactly once on the synthetic subscription surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's plan-purchase
    # input — not a no-op over host-free evidence (the real-fixture failure mode).
    _check(
        _PP_HOST in base_surf and _PP_HOST in base_quote,
        f"the host is inside the plan-purchase surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the human plan senses (pricing-page checkout, dashboard onboarding,
    # bare "subscription plans" marketing) fire ZERO — the signal keys on the
    # programmatic-purchase structure, never on the bare word "plan".
    _check(
        _plan_purchase_signals(_PP_DISTRACTOR_SURFACE, _PP_DISTRACTOR_PROSE) == [],
        "human plan distractor prose ('subscribe to a plan on the pricing page', "
        "dashboard onboarding after subscribing, bare 'subscription plans' "
        "marketing) fires no plan-purchase signal — the match is the programmatic "
        "purchase structure (a /plans/{id}/purchase endpoint / a purchasable plan "
        "/ a buy-or-activate verb over a credit-or-subscription plan), not 'plan'",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _PP_SURFACE.replace(_PP_HOST, _NEUTRAL_HOST)
    relab_prose = _PP_PROSE.replace(_PP_HOST, _NEUTRAL_HOST)
    _check(
        _PP_HOST not in relab_surface and _PP_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _plan_purchase_signals(relab_surface, relab_prose)

    # (1) Same match count — the plan-purchase signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"plan-purchase match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_PP_HOST, _NEUTRAL_HOST),
        "plan-purchase fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live plan-purchase regex (the
    # fired form is a programmatic-commit token — a /plans/{id}/purchase endpoint /
    # a buy-a-subscription-plan verb — not the host) and names no vendor host — the
    # match keyed on the plan-purchase CONTRACT, not who vends it.
    pp_re = dict(_offering._SIGNALS["subscription"])[_PP_LABEL]
    _check(
        pp_re.search(relab_quote) is not None,
        f"relabeled plan-purchase quote still matches the programmatic-commit signal: {relab_quote!r}",
    )
    _check(
        _PP_HOST not in relab_quote and _PP_HOST not in relab_surf,
        f"vendor host absent from relabeled plan-purchase evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance at the SIGNAL level — the digital_good OUTPUT-RETENTION
# leg (Cycle 150 COVERAGE, PR #142). The newest digital_good signal to join the
# signal-level relabel family and the METHOD/TRUTH mirror every recent signal
# earned (plan-purchase 147 / payment-receipt 143 / error-contract 91). It is
# the digital_good "complete the job" LIFECYCLE leg — the counterpart to
# metered_api's `cancel-job`: `generation`/`generate-media`/`render` say WHAT is
# produced, `hosted-output` WHERE it is delivered, `output-resolution` its SHAPE,
# `output-license` whether the agent may USE it, `content-provenance` whether it
# can TRUST it — NONE says HOW LONG the hosted deliverable lives or that the agent
# must copy it out before the link expires. output-retention is that
# "collect the finished job's deliverable in time" leg — a delivery-window on a
# hosted output ("hosted URLs that remain available for N days"), the
# download-into-your-own-storage step, or an explicit output retention
# window/period/policy. Whether an agent can retrieve its output before it expires
# is a property of the retention CONTRACT the site exposes, never of WHO vends it,
# so the signal must be identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (mirroring plan-purchase 147 /
# payment-receipt 143 / webhook-verification 135, NOT output-license which rides
# captured evidence): the output-retention vocabulary is host-FREE by nature — the
# fired quote carries an artifact-lifecycle window (a media/deliverable noun + a
# persistence verb + "for N days", or "download ... into your own storage"), not
# the vendor's name — and on the real captured canonical /docs the signal fires
# with the host in the surface KEY but NOT the quote window, so a whole-fixture
# relabel would leave the output-retention evidence byte-identical and the
# invariance would be VACUOUS. To make the relabel genuinely rewrite the
# classifier's input at THIS signal, this guard scans a synthetic digital_good
# surface that deliberately seats the host INSIDE the retention evidence: the host
# is the surface KEY prefix AND sits adjacent to the "hosted URL that remains
# available for 90 days" phrase (asserted non-vacuous below). Relabel the host
# everywhere, re-scan, and the output-retention signal must survive with the SAME
# match count, on the SAME host-normalized surface, its quote STILL satisfying the
# live output-retention regex, with the vendor host absent from all rewritten
# evidence.
#
# TEETH (precision, the output-retention signal's defining risk — a bare time
# window is a false-positive minefield): a sibling synthetic surface carrying only
# the retention-SHAPED noise the signal must REFUSE — a SUPPORT-line window
# ("support agents remain available for 24 hours", no deliverable noun) and the
# metered-API marketplace trap, a signed download-URL / file EXPIRY ("expiration
# date of this download URL", a signed-URL expiry, NOT a hosted-deliverable
# retention window) — fires ZERO output-retention signals, proving the match keys
# on the artifact-lifecycle STRUCTURE (a hosted DELIVERABLE that persists for a
# window / a download-into-your-own-storage step / an output retention policy),
# never on a bare "available for N hours" window or a URL-expiry; and relabeling
# the host through that noise never CONJURES a digital_good claim on a site whose
# only "window" is a support line or a signed-URL expiry.
# ---------------------------------------------------------------------------
_OR_LABEL = "output-retention"
_OR_HOST = "acme-forge.example"  # a host bearing no output-retention (or other) signal word
_OR_SURFACE = f"agents.{_OR_HOST}/docs"
# Host seated adjacent to the "hosted URL that remains available for 90 days"
# phrase (surface key prefix + the sentence subject and trailer) so it lands in
# the padded quote window, not merely the surface key.
_OR_PROSE = (
    f"{_OR_HOST} returns each render as a hosted URL that remains "
    f"available for 90 days on {_OR_HOST}."
)
# The retention-SHAPED noise the output-retention signal must never match: a
# SUPPORT-line time window (no deliverable noun) and the signed download-URL /
# file EXPIRY trap on a metered-API marketplace.
_OR_DISTRACTOR_SURFACE = f"agents.{_OR_HOST}/openapi"
_OR_DISTRACTOR_PROSE = (
    f"{_OR_HOST} support agents remain available for 24 hours; a Unix "
    f"timestamp gives the expiration date of this download URL on {_OR_HOST}."
)


def _output_retention_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the digital_good output-retention fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "digital_good" and s.label == _OR_LABEL
    )


def test_offering_relabel_invariance_output_retention() -> None:
    """The digital_good output-retention keys on the retention contract, not the host."""
    print("test_offering_relabel_invariance_output_retention")
    base = _output_retention_signals(_OR_SURFACE, _OR_PROSE)

    # The signal genuinely fires on the synthetic digital_good evidence.
    _check(
        len(base) == 1,
        f"output-retention fires exactly once on the synthetic digital_good surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's
    # output-retention input — not a no-op over host-free evidence (the
    # real-fixture failure mode named above).
    _check(
        _OR_HOST in base_surf and _OR_HOST in base_quote,
        f"the host is inside the output-retention surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the retention-shaped noise (support-line window with no deliverable
    # noun, signed download-URL / file expiry) fires ZERO — the signal keys on the
    # hosted-deliverable retention STRUCTURE, never on a bare "available for N
    # hours" window or a URL expiry.
    _check(
        _output_retention_signals(_OR_DISTRACTOR_SURFACE, _OR_DISTRACTOR_PROSE) == [],
        "retention-shaped noise ('support agents remain available for 24 hours', "
        "'expiration date of this download URL') fires no output-retention signal — "
        "the match is the hosted-deliverable retention structure (a deliverable that "
        "persists for a window / a download-into-your-own-storage step / an output "
        "retention policy), not a bare time window or a signed-URL expiry",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _OR_SURFACE.replace(_OR_HOST, _NEUTRAL_HOST)
    relab_prose = _OR_PROSE.replace(_OR_HOST, _NEUTRAL_HOST)
    _check(
        _OR_HOST not in relab_surface and _OR_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _output_retention_signals(relab_surface, relab_prose)

    # (1) Same match count — the output-retention signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"output-retention match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_OR_HOST, _NEUTRAL_HOST),
        "output-retention fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live output-retention regex (the
    # fired form is an artifact-lifecycle window — a hosted deliverable that remains
    # available for N days — not the host) and names no vendor host — the match
    # keyed on the retention CONTRACT, not who vends it.
    or_re = dict(_offering._SIGNALS["digital_good"])[_OR_LABEL]
    _check(
        or_re.search(relab_quote) is not None,
        f"relabeled output-retention quote still matches the retention-window signal: {relab_quote!r}",
    )
    _check(
        _OR_HOST not in relab_quote and _OR_HOST not in relab_surf,
        f"vendor host absent from relabeled output-retention evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Signal-level relabel-invariance — the metered_api failure-not-billed leg
# (Cycle 152 COVERAGE, direct-to-main). The newest metered_api signal to join
# the signal-level relabel family and the TRUTH/METHOD mirror every recent
# signal earns (output-retention 151 / plan-purchase 147 / payment-receipt 143
# / error-contract 91). It is the metered_api capital-safety leg the PLAYBOOK's
# lens names directly: an autonomous agent paying per call must know that a
# FAILED unit (the render did not complete, the job errored, the request timed
# out) does not silently burn money — "you don't pay for work you didn't get" —
# or it cannot bound its spend against a flaky endpoint. It is DISTINCT from the
# other metered_api legs: `error-contract` names the machine-readable failure
# FORMAT (how a failure is REPORTED), `payment-receipt` is proof of a SUCCESSFUL
# charge, `test-mode` is a $0 SANDBOX, and `usage-based`/`billed-per`/
# `per-unit-rate`/`credit-metered` describe how you are charged ON SUCCESS —
# NONE says whether a FAILURE costs money. Whether a failed unit is billed is a
# property of the failure-billing CONTRACT the site exposes, never of WHO vends
# it, so the signal must be identity-invariant under a host relabel.
#
# Why a SYNTHETIC surface, not the real fixture (mirroring output-retention 151
# / plan-purchase 147 / payment-receipt 143): the failure-not-billed vocabulary
# is host-FREE by nature — the fired quote carries a failure token adjacent to a
# not-charged/not-billed guarantee, not the vendor's name — and on the real
# captured canonical /docs the signal fires with the host in the surface KEY but
# NOT the quote window, so a whole-fixture relabel would leave the evidence
# byte-identical and the invariance would be VACUOUS. To make the relabel
# genuinely rewrite the classifier's input at THIS signal, this guard scans a
# synthetic metered_api surface that deliberately seats the host INSIDE the
# failure-billing evidence: the host is the surface KEY prefix AND sits adjacent
# to the "if a render fails it is never charged" phrase (asserted non-vacuous
# below). Relabel the host everywhere, re-scan, and the failure-not-billed
# signal must survive with the SAME match count, on the SAME host-normalized
# surface, its quote STILL satisfying the live failure-not-billed regex, with
# the vendor host absent from all rewritten evidence.
#
# TEETH (precision, the failure-not-billed signal's defining risk — a bare "not
# charged" is a false-positive minefield): a sibling synthetic surface carrying
# only the not-charged-SHAPED noise the signal must REFUSE — a SUBSCRIPTION
# free-trial $0-eval promise ("your card is not charged until the trial ends",
# a not-charged with no failure word) and the `error-contract` trap ("on failure
# the body is application/problem+json", a failure word with no not-charged) —
# fires ZERO failure-not-billed signals, proving the match keys on the
# failure-billing STRUCTURE (a failure token WITHIN a short window of a
# not/never-charged guarantee, or "only charged for successful"), never on a
# bare trial promise or a bare failure format; and relabeling the host through
# that noise never CONJURES a metered_api failure-billing claim.
# ---------------------------------------------------------------------------
_FNB_LABEL = "failure-not-billed"
_FNB_HOST = "acme-flux.example"  # a host bearing no failure-not-billed (or other) signal word
_FNB_SURFACE = f"api.{_FNB_HOST}/docs"
# Host seated adjacent to the "if a render fails it is never charged" phrase
# (surface key prefix + the sentence subject and trailer) so it lands in the
# padded quote window, not merely the surface key.
_FNB_PROSE = (
    f"On {_FNB_HOST}, if a render fails it is never charged; "
    f"{_FNB_HOST} bills only for renders it completed."
)
# The not-charged-SHAPED noise the failure-not-billed signal must never match: a
# SUBSCRIPTION free-trial $0-eval promise (not-charged, no failure word) and the
# `error-contract` failure-FORMAT trap (failure word, no not-charged).
_FNB_DISTRACTOR_SURFACE = f"api.{_FNB_HOST}/pricing"
_FNB_DISTRACTOR_PROSE = (
    f"{_FNB_HOST} free trial: your card is not charged until the trial ends. "
    f"On failure the {_FNB_HOST} API returns application/problem+json."
)


def _failure_not_billed_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the metered_api failure-not-billed fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "metered_api" and s.label == _FNB_LABEL
    )


def test_offering_relabel_invariance_failure_not_billed() -> None:
    """The metered_api failure-not-billed keys on the failure-billing contract, not the host."""
    print("test_offering_relabel_invariance_failure_not_billed")
    base = _failure_not_billed_signals(_FNB_SURFACE, _FNB_PROSE)

    # The signal genuinely fires on the synthetic metered_api evidence.
    _check(
        len(base) == 1,
        f"failure-not-billed fires exactly once on the synthetic metered_api surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's
    # failure-not-billed input — not a no-op over host-free evidence (the
    # real-fixture failure mode named above).
    _check(
        _FNB_HOST in base_surf and _FNB_HOST in base_quote,
        f"the host is inside the failure-not-billed surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the not-charged-shaped noise (a subscription free-trial $0 promise
    # with no failure word, an error-contract failure FORMAT with no not-charged)
    # fires ZERO — the signal keys on the failure-billing STRUCTURE, never on a
    # bare trial promise or a bare failure format.
    _check(
        _failure_not_billed_signals(_FNB_DISTRACTOR_SURFACE, _FNB_DISTRACTOR_PROSE) == [],
        "not-charged-shaped noise ('your card is not charged until the trial ends', "
        "'on failure the body is application/problem+json') fires no failure-not-billed "
        "signal — the match is the failure-billing structure (a failure token within a "
        "short window of a not/never-charged guarantee, or 'only charged for successful'), "
        "not a bare trial promise or a bare failure format",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _FNB_SURFACE.replace(_FNB_HOST, _NEUTRAL_HOST)
    relab_prose = _FNB_PROSE.replace(_FNB_HOST, _NEUTRAL_HOST)
    _check(
        _FNB_HOST not in relab_surface and _FNB_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _failure_not_billed_signals(relab_surface, relab_prose)

    # (1) Same match count — the failure-not-billed signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"failure-not-billed match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_FNB_HOST, _NEUTRAL_HOST),
        "failure-not-billed fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live failure-not-billed regex
    # (the fired form is a failure token adjacent to a not/never-charged
    # guarantee, not the host) and names no vendor host — the match keyed on the
    # failure-billing CONTRACT, not who vends it.
    fnb_re = dict(_offering._SIGNALS["metered_api"])[_FNB_LABEL]
    _check(
        fnb_re.search(relab_quote) is not None,
        f"relabeled failure-not-billed quote still matches the failure-billing signal: {relab_quote!r}",
    )
    _check(
        _FNB_HOST not in relab_quote and _FNB_HOST not in relab_surf,
        f"vendor host absent from relabeled failure-not-billed evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel invariance — the metered_api reserve-and-settle CAPITAL-SAFETY leg
# (Cycle 156's signal; the metered sibling of failure-not-billed).
#
# The signal-level metamorphic mirror every recent signal earns (failure-not-
# billed / output-retention / plan-purchase / payment-receipt / error-contract):
# whether an agent can CAP a single call's exposure up front — reserve a spend
# ceiling, be charged only actual usage, be refunded the unused remainder — is a
# property of the reserve-and-settle CONTRACT, never of who vends it, so the
# signal is identity-invariant under a host relabel.
#
# NON-VACUITY (same real-fixture failure mode the FNB guard names): the live
# reserve-and-settle quote is host-FREE ("reserves the ceiling", "escrow refunds
# the rest"), so a whole-fixture relabel would be VACUOUS over host-free evidence.
# A SYNTHETIC vehicle seats the host INSIDE the evidence — surface-key prefix AND
# adjacent to the reserve-and-settle phrase (within the 40-char quote pad) — so a
# host relabel genuinely rewrites the classifier's reserve-and-settle input, then
# the signal must survive with the SAME match count, on the SAME host-normalized
# surface, its quote STILL satisfying the live reserve-and-settle regex, with the
# vendor host absent from all rewritten evidence.
#
# TEETH (precision, the reserve-and-settle signal's defining risk — bare reserve/
# refund/ceiling/escrow is a homonym minefield): a sibling synthetic surface
# carrying only the reserve/refund-SHAPED noise the signal must REFUSE — a
# "reserves the right to change prices" boilerplate line, a plain retail "full
# refund within 30 days", and "reserved capacity ceilings" — fires ZERO
# reserve-and-settle signals, proving the match keys on the reserve-AND-settle
# STRUCTURE (a reserved ceiling charged only actual, or an escrow/reserve that
# refunds the unused remainder), never on a bare reservation, a bare refund, or a
# bare ceiling; and relabeling the host through that noise never CONJURES a
# metered_api capital-safety claim.
# ---------------------------------------------------------------------------
_RS_LABEL = "reserve-and-settle"
_RS_HOST = "acme-meter.example"  # a host bearing no reserve-and-settle (or other) signal word
_RS_SURFACE = f"api.{_RS_HOST}/docs"
# Host seated adjacent to the "reserves the ceiling" phrase (surface key prefix +
# the sentence subject and a trailing repeat) so it lands in the padded quote
# window, not merely the surface key.
_RS_PROSE = (
    f"On {_RS_HOST}, your wallet reserves the ceiling up front; "
    f"{_RS_HOST} then charges only actual usage and the escrow refunds the rest."
)
# The reserve/refund-SHAPED noise the reserve-and-settle signal must never match:
# a "reserves the right" boilerplate (reserve, no ceiling/settle), a plain retail
# refund (refund, no escrow/reserve+remainder), and "reserved capacity ceilings"
# (reserve + ceiling, but no charged-only-actual / refund-the-remainder settle).
_RS_DISTRACTOR_SURFACE = f"api.{_RS_HOST}/pricing"
_RS_DISTRACTOR_PROSE = (
    f"{_RS_HOST} reserves the right to change prices. Full refund within 30 days. "
    f"Reserved capacity ceilings apply."
)


def _reserve_and_settle_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the metered_api reserve-and-settle fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "metered_api" and s.label == _RS_LABEL
    )


def test_offering_relabel_invariance_reserve_and_settle() -> None:
    """The metered_api reserve-and-settle keys on the capital-safety contract, not the host."""
    print("test_offering_relabel_invariance_reserve_and_settle")
    base = _reserve_and_settle_signals(_RS_SURFACE, _RS_PROSE)

    # The signal genuinely fires on the synthetic metered_api evidence.
    _check(
        len(base) == 1,
        f"reserve-and-settle fires exactly once on the synthetic metered_api surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's
    # reserve-and-settle input — not a no-op over host-free evidence (the
    # real-fixture failure mode named above).
    _check(
        _RS_HOST in base_surf and _RS_HOST in base_quote,
        f"the host is inside the reserve-and-settle surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the reserve/refund-SHAPED noise (a "reserves the right" boilerplate,
    # a plain retail refund, "reserved capacity ceilings") fires ZERO — the signal
    # keys on the reserve-AND-settle STRUCTURE, never on a bare reservation, a bare
    # refund, or a bare ceiling.
    _check(
        _reserve_and_settle_signals(_RS_DISTRACTOR_SURFACE, _RS_DISTRACTOR_PROSE) == [],
        "reserve/refund-shaped noise ('reserves the right to change prices', 'full "
        "refund within 30 days', 'reserved capacity ceilings apply') fires no "
        "reserve-and-settle signal — the match is the reserve-and-settle structure "
        "(a reserved ceiling charged only actual, or an escrow/reserve that refunds "
        "the unused remainder), not a bare reservation, refund, or ceiling",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _RS_SURFACE.replace(_RS_HOST, _NEUTRAL_HOST)
    relab_prose = _RS_PROSE.replace(_RS_HOST, _NEUTRAL_HOST)
    _check(
        _RS_HOST not in relab_surface and _RS_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _reserve_and_settle_signals(relab_surface, relab_prose)

    # (1) Same match count — the reserve-and-settle signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"reserve-and-settle match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_RS_HOST, _NEUTRAL_HOST),
        "reserve-and-settle fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live reserve-and-settle regex
    # (the fired form is a reserved ceiling / escrow-refund clause, not the host)
    # and names no vendor host — the match keyed on the capital-safety CONTRACT,
    # not who vends it.
    rs_re = dict(_offering._SIGNALS["metered_api"])[_RS_LABEL]
    _check(
        rs_re.search(relab_quote) is not None,
        f"relabeled reserve-and-settle quote still matches the capital-safety signal: {relab_quote!r}",
    )
    _check(
        _RS_HOST not in relab_quote and _RS_HOST not in relab_surf,
        f"vendor host absent from relabeled reserve-and-settle evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel invariance — the metered_api free-included-usage ON-RAMP leg
# (Cycle 160's signal; the metered_api $0 on-ramp the playbook's lens names).
#
# The signal-level metamorphic mirror every recent signal earns (reserve-and-
# settle / failure-not-billed / output-retention / plan-purchase / payment-
# receipt): whether an agent can complete a REAL metered call at $0 before
# committing any money — a per-account free ALLOWANCE of actual units, usable at
# a zero balance with no funding — is a property of the free-included-usage
# CONTRACT, never of who vends it, so the signal is identity-invariant under a
# host relabel.
#
# NON-VACUITY (same real-fixture failure mode the RS/FNB guards name): the live
# free-included-usage quotes are host-FREE ("Free allowance - try it before any
# payment", "`includedUnits` - free usage per account"), so a whole-fixture
# relabel would be VACUOUS over host-free evidence. A SYNTHETIC vehicle seats the
# host INSIDE the evidence — surface-key prefix AND adjacent to the free-allowance
# phrase (within the 40-char quote pad) — so a host relabel genuinely rewrites the
# classifier's free-included-usage input, then the signal must survive with the
# SAME match count, on the SAME host-normalized surface, its quote STILL
# satisfying the live free-included-usage regex, with the vendor host absent from
# all rewritten evidence.
#
# TEETH (precision, the free-included-usage signal's defining risk — bare free/
# included/units is a homonym minefield): a sibling synthetic surface carrying
# only the free/included-SHAPED noise the signal must REFUSE — retail "free
# shipping on every order", "royalty-free stock images", a PAID "500 units
# included per month" allotment (included units, but NOT free), and "feel free to
# explore" — fires ZERO free-included-usage signals, proving the match keys on the
# free-USAGE STRUCTURE (a free usage/allowance, free units per account/period, an
# includedUnits allotment that is FREE, or try/use it before any money), never on
# a bare "free", a bare "included units", or a PAID included allotment; and
# relabeling the host through that noise never CONJURES a metered_api $0-on-ramp
# claim.
# ---------------------------------------------------------------------------
_FIU_LABEL = "free-included-usage"
_FIU_HOST = "acme-vend.example"  # a host bearing no free/included/usage (or other) signal word
_FIU_SURFACE = f"agents.{_FIU_HOST}/llms.txt"
# Host seated adjacent to the "free allowance" phrase (surface-key prefix + the
# sentence subject and a trailing repeat) so it lands in the padded quote window,
# not merely the surface key.
_FIU_PROSE = (
    f"On {_FIU_HOST}, every account gets a free allowance you can spend before "
    f"funding a wallet; {_FIU_HOST} bills nothing until that free allowance runs out."
)
# The free/included-SHAPED noise the free-included-usage signal must never match:
# a retail "free shipping" (free, no usage/allowance/units), "royalty-free" images
# (free, no included-usage), a PAID "500 units included per month" allotment
# (included units, but NOT free), and "feel free" (free, no usage sense).
_FIU_DISTRACTOR_SURFACE = f"agents.{_FIU_HOST}/pricing"
_FIU_DISTRACTOR_PROSE = (
    f"{_FIU_HOST} offers free shipping on every order. Royalty-free stock images "
    f"included. 500 units included per month on the paid plan. Feel free to explore."
)


def _free_included_usage_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the metered_api free-included-usage fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "metered_api" and s.label == _FIU_LABEL
    )


def test_offering_relabel_invariance_free_included_usage() -> None:
    """The metered_api free-included-usage keys on the $0-on-ramp contract, not the host."""
    print("test_offering_relabel_invariance_free_included_usage")
    base = _free_included_usage_signals(_FIU_SURFACE, _FIU_PROSE)

    # The signal genuinely fires on the synthetic metered_api evidence.
    _check(
        len(base) == 1,
        f"free-included-usage fires exactly once on the synthetic metered_api surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's
    # free-included-usage input — not a no-op over host-free evidence (the
    # real-fixture failure mode named above).
    _check(
        _FIU_HOST in base_surf and _FIU_HOST in base_quote,
        f"the host is inside the free-included-usage surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the free/included-SHAPED noise (retail free shipping, royalty-free
    # images, a PAID included-units allotment, "feel free") fires ZERO — the signal
    # keys on the free-USAGE STRUCTURE, never on a bare "free", a bare "included
    # units", or a PAID included allotment.
    _check(
        _free_included_usage_signals(_FIU_DISTRACTOR_SURFACE, _FIU_DISTRACTOR_PROSE) == [],
        "free/included-shaped noise ('free shipping on every order', 'royalty-free "
        "stock images', 'included. 500 units included per month on the paid plan', "
        "'feel free to explore') fires no free-included-usage signal — the match is "
        "the free-usage structure (a free usage/allowance, free units per "
        "account/period, an includedUnits allotment that is FREE, or try/use it "
        "before any money), not a bare 'free', a bare 'included units', or a PAID "
        "included allotment",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _FIU_SURFACE.replace(_FIU_HOST, _NEUTRAL_HOST)
    relab_prose = _FIU_PROSE.replace(_FIU_HOST, _NEUTRAL_HOST)
    _check(
        _FIU_HOST not in relab_surface and _FIU_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _free_included_usage_signals(relab_surface, relab_prose)

    # (1) Same match count — the free-included-usage signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"free-included-usage match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_FIU_HOST, _NEUTRAL_HOST),
        "free-included-usage fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live free-included-usage regex
    # (the fired form is a free-allowance clause, not the host) and names no vendor
    # host — the match keyed on the $0-on-ramp CONTRACT, not who vends it.
    fiu_re = dict(_offering._SIGNALS["metered_api"])[_FIU_LABEL]
    _check(
        fiu_re.search(relab_quote) is not None,
        f"relabeled free-included-usage quote still matches the $0-on-ramp signal: {relab_quote!r}",
    )
    _check(
        _FIU_HOST not in relab_quote and _FIU_HOST not in relab_surf,
        f"vendor host absent from relabeled free-included-usage evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Relabel invariance — the digital_good variant-selection DELIVERABLE-CONTROL leg
# (Cycle 164's signal; the "complete the job with a USABLE deliverable" leg).
#
# The signal-level metamorphic mirror every recent signal earns (free-included-
# usage / reserve-and-settle / failure-not-billed / output-retention / payment-
# receipt): whether an autonomous agent can DISCOVER and SELECT which output
# variant a generative service produces — a named, listable style PRESET passed
# on the request so the deliverable is fit-for-purpose and REPRODUCIBLE across a
# catalog run — is a property of the variant-selection CONTRACT the offer
# publishes, never of who vends it, so the signal is identity-invariant under a
# host relabel.
#
# NON-VACUITY (same real-fixture failure mode the FIU/RS/FNB guards name): the
# live variant-selection quotes are host-FREE ("Pick a preset", "style presets",
# "A style preset slug"), so a whole-fixture relabel would be VACUOUS over
# host-free evidence. A SYNTHETIC vehicle seats the host INSIDE the evidence —
# surface-key prefix AND adjacent to the "pick a preset" phrase (within the
# 40-char quote pad) — so a host relabel genuinely rewrites the classifier's
# variant-selection input, then the signal must survive with the SAME match
# count, on the SAME host-normalized surface, its quote STILL satisfying the live
# variant-selection regex, with the vendor host absent from all rewritten
# evidence.
#
# TEETH (precision, the variant-selection signal's DEFINING risk — bare "model"
# and "tier" are false-positive minefields the signal must REFUSE): a sibling
# synthetic surface carrying only the preset/model/tier-SHAPED noise — a "large
# language model" on the "pro tier", the preset-VERB ("preset the oven"), a
# "factory preset", a "camera preset", and a "reset" — fires ZERO
# variant-selection signals, proving the match keys on the deliverable-control
# STRUCTURE (a STYLE preset, a preset slug/param/id/name, a pick/choose/select/
# browse verb naming a preset, or a preset that locks/pins the style), never on a
# bare "model", a bare billing "tier", the preset VERB, a factory/camera preset,
# or "reset"; and relabeling the host through that noise never CONJURES a
# digital_good variant-selection claim.
# ---------------------------------------------------------------------------
_VS_LABEL = "variant-selection"
_VS_HOST = "acme-vend.example"  # a host bearing no preset/style/select (or other) signal word
_VS_SURFACE = f"agents.{_VS_HOST}/docs"
# Host seated adjacent to the "pick a preset" phrase (surface-key prefix + the
# sentence subject and a trailing repeat) so it lands in the padded quote window,
# not merely the surface key.
_VS_PROSE = (
    f"On {_VS_HOST}, pick a preset to lock the render style before you generate; "
    f"{_VS_HOST} lists every style preset it ships in the catalog."
)
# The preset/model/tier-SHAPED noise the variant-selection signal must never
# match: a bare "model" and billing "tier" (the two named minefields; "tier" is
# owned by metered_api `tiered-volume`), the preset-VERB, a factory/camera
# preset, and "reset".
_VS_DISTRACTOR_SURFACE = f"agents.{_VS_HOST}/pricing"
_VS_DISTRACTOR_PROSE = (
    f"{_VS_HOST} runs a large language model on the pro tier. Preset the oven to "
    f"200C; the camera's factory preset and a full reset are unrelated."
)


def _variant_selection_signals(surface: str, text: str) -> list:
    """The (surface, quote) pairs where the digital_good variant-selection fired."""
    return sorted(
        (s.surface, s.quote)
        for s in _offering._scan_surface(surface, text)
        if s.archetype == "digital_good" and s.label == _VS_LABEL
    )


def test_offering_relabel_invariance_variant_selection() -> None:
    """The digital_good variant-selection keys on the deliverable-control contract, not the host."""
    print("test_offering_relabel_invariance_variant_selection")
    base = _variant_selection_signals(_VS_SURFACE, _VS_PROSE)

    # The signal genuinely fires on the synthetic digital_good evidence.
    _check(
        len(base) == 1,
        f"variant-selection fires exactly once on the synthetic digital_good surface (got {len(base)})",
    )
    base_surf, base_quote = base[0]

    # Non-vacuity: the host sits inside BOTH the surface key AND the padded quote
    # window, so a host relabel genuinely rewrites the classifier's
    # variant-selection input — not a no-op over host-free evidence (the
    # real-fixture failure mode named above).
    _check(
        _VS_HOST in base_surf and _VS_HOST in base_quote,
        f"the host is inside the variant-selection surface key AND quote window — "
        f"relabel rewrites real signal input (surface {base_surf!r}, quote {base_quote!r})",
    )

    # TEETH: the preset/model/tier-SHAPED noise (a bare "model", a billing "tier",
    # the preset VERB, a factory/camera preset, a "reset") fires ZERO — the signal
    # keys on the deliverable-control STRUCTURE, never on a bare "model", a bare
    # "tier", or the preset VERB.
    _check(
        _variant_selection_signals(_VS_DISTRACTOR_SURFACE, _VS_DISTRACTOR_PROSE) == [],
        "preset/model/tier-shaped noise ('a large language model on the pro tier', "
        "'preset the oven to 200C', 'the camera's factory preset', 'a full reset') "
        "fires no variant-selection signal — the match is the deliverable-control "
        "structure (a style preset, a preset slug/param/id/name, a pick/choose/select/"
        "browse verb naming a preset, or a preset that locks/pins the style), not a "
        "bare 'model', a billing 'tier', the preset verb, or a factory/camera preset",
    )

    # Relabel the host everywhere (surface key + prose) and re-scan.
    relab_surface = _VS_SURFACE.replace(_VS_HOST, _NEUTRAL_HOST)
    relab_prose = _VS_PROSE.replace(_VS_HOST, _NEUTRAL_HOST)
    _check(
        _VS_HOST not in relab_surface and _VS_HOST not in relab_prose,
        "every occurrence of the original host was relabeled out of the synthetic input",
    )
    relab = _variant_selection_signals(relab_surface, relab_prose)

    # (1) Same match count — the variant-selection signal is neither lost nor conjured.
    _check(
        len(relab) == len(base) == 1,
        f"variant-selection match count invariant under relabel (base {len(base)}, "
        f"relabel {len(relab)})",
    )
    relab_surf, relab_quote = relab[0]

    # (2) The SAME logical surface carries the signal once the host label is
    # normalized away — the signal did not migrate to a different surface.
    _check(
        relab_surf == base_surf.replace(_VS_HOST, _NEUTRAL_HOST),
        "variant-selection fires on the same (host-normalized) surface under relabel "
        f"(base {base_surf!r}, relabel {relab_surf!r})",
    )
    # (3) The relabeled quote STILL satisfies the live variant-selection regex
    # (the fired form is a pick-a-preset clause, not the host) and names no vendor
    # host — the match keyed on the deliverable-control CONTRACT, not who vends it.
    vs_re = dict(_offering._SIGNALS["digital_good"])[_VS_LABEL]
    _check(
        vs_re.search(relab_quote) is not None,
        f"relabeled variant-selection quote still matches the deliverable-control signal: {relab_quote!r}",
    )
    _check(
        _VS_HOST not in relab_quote and _VS_HOST not in relab_surf,
        f"vendor host absent from relabeled variant-selection evidence (surface {relab_surf!r})",
    )


# ---------------------------------------------------------------------------
# Surface-read ORDER invariance — the digital_good deliverable-RIGHTS leg.
#
# A fresh perturbation AXIS orthogonal to the relabel/identity family above. The
# relabel guards (payment-rail 79 / async-job 83 / api-auth 87 / error-contract /
# output-license 99) pin that a signal keys on its STRUCTURAL form, not the host
# LABEL. This pins the ORTHOGONAL property for the digital_good rights leg: a
# readiness classification is a property of WHAT a storefront's surfaces DECLARE,
# not the ORDER an agent happened to fetch them in — two crawls that read /pricing
# before or after the apex homepage (or a doc-subdomain surface before the apex)
# must classify identically. Cross-site comparability rests on it.
#
# test_offering.test_classification_is_surface_read_order_invariant already pins
# surface-read-order invariance GENERICALLY, but on a SYNTHETIC two-surface fixture
# where digital_good fires a SINGLE signal (generate-media) on ONE surface — an
# order bystander, not a genuine multi-surface accumulation. The output-license
# rights leg is the opposite case: on the canonical .com fixture it fires SIX times
# across SIX distinct surfaces (homepage / /llms.txt / /pricing /
# agents.<host>/{llms.txt,llms-full.txt,manifest.json}). So a surface-read reorder
# genuinely permutes the per-archetype signal accumulation for THIS signal on REAL
# captured evidence — the non-vacuity the generic single-surface test cannot supply
# for the rights leg. Under a full reversal of the surface-read order, the rights
# signal's fired COUNT, the SET of surfaces it fires on, and the digital_good claim
# (strength + distinct labels) must all be identical, and the whole classified
# profile (ordered claimed list + NA complement) invariant.
#
# The maintenance contract matches the other offering guards: a signal-bank change
# that legitimately alters what driftflight.com claims is re-captured [LOCAL] and
# EXPECTED updated in the same PR; an order-DEPENDENT classification is the
# regression this guard exists to catch.
# ---------------------------------------------------------------------------
def _captured_surfaces(domain: str) -> dict:
    """The exact surface-name -> text map (in READ order) discovery feeds the classifier.

    ``discover_offering`` builds its surfaces dict by fetching the fixture in a
    fixed order and hands it to ``classify_offering``; the surface-read order is
    that dict's insertion order. Spy on that single call to recover the real,
    multi-surface map so its order can be permuted deterministically offline — no
    network, byte-identical to what the live discovery path scanned. Restores the
    real ``classify_offering`` in a ``finally`` so the patch cannot leak.
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)  # dict preserves insertion (read) order
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        discover_offering(ctx)
    finally:
        _offering.classify_offering = real
    _check(
        len(captured) >= 2,
        f"{domain}: discovery read >=2 surfaces (a reorder is meaningful) "
        f"(got {list(captured)})",
    )
    return captured


def test_offering_surface_order_invariance_output_license() -> None:
    """The digital-good rights leg fires the same regardless of surface-read order."""
    print("test_offering_surface_order_invariance_output_license")
    surfaces = _captured_surfaces("driftflight.com")

    forward = _offering.classify_offering("driftflight.com", dict(surfaces))
    reverse = _offering.classify_offering(
        "driftflight.com", dict(reversed(list(surfaces.items())))
    )

    fwd_lic = _license_signals(forward)
    rev_lic = _license_signals(reverse)
    fwd_surfaces = {s for s, _ in fwd_lic}

    # Non-vacuity (a): the rights signal genuinely fires across MULTIPLE surfaces,
    # so a reorder permutes a REAL per-archetype accumulation — not a single-surface
    # bystander as in the generic order-invariance test.
    _check(
        len(fwd_surfaces) >= 2,
        "output-license fires on >=2 distinct surfaces (a real multi-surface "
        f"accumulation, so the reorder is meaningful) (got {sorted(fwd_surfaces)})",
    )
    # Non-vacuity (b): the reorder is REAL and OBSERVABLE — the surface arrival
    # order actually differs between the two runs. An order-INSENSITIVE reader
    # (e.g. one that sorted surfaces before scanning) would make the invariance
    # below vacuously true; surfaces_seen is the read order, and a full reversal
    # flips it.
    _check(
        list(forward.surfaces_seen) != list(reverse.surfaces_seen),
        "the surface-read order genuinely differs between the two runs "
        f"(forward head {list(forward.surfaces_seen)[:2]}, reverse head "
        f"{list(reverse.surfaces_seen)[:2]}) — the invariance is non-vacuous",
    )

    # (1) The rights signal fires the SAME number of times under reorder — neither
    # lost nor conjured by which surface arrived first.
    _check(
        len(rev_lic) == len(fwd_lic),
        "output-license match count invariant under surface-read reorder "
        f"(forward {len(fwd_lic)}, reverse {len(rev_lic)})",
    )
    # (2) It fires on the SAME set of surfaces — order cannot migrate the signal to
    # a different surface.
    _check(
        {s for s, _ in rev_lic} == fwd_surfaces,
        "output-license fires on the same set of surfaces under reorder "
        f"(forward {sorted(fwd_surfaces)}, reverse {sorted({s for s, _ in rev_lic})})",
    )
    # (3) The digital_good CLAIM itself — its distinct-signal strength and the SET
    # of labels that fired — is order-invariant, and the rights leg is actually part
    # of it (so the property under test is present, not vacuously absent).
    dg_f = next(c for c in forward.claimed if c.archetype == "digital_good")
    dg_r = next(c for c in reverse.claimed if c.archetype == "digital_good")
    _check(
        dg_f.strength == dg_r.strength
        and {s.label for s in dg_f.signals} == {s.label for s in dg_r.signals},
        "the digital_good claim (strength + distinct labels) is invariant under "
        f"surface-read reorder (strength {dg_f.strength}/{dg_r.strength})",
    )
    _check(
        _LICENSE_LABEL in {s.label for s in dg_f.signals},
        "the output-license label is part of the digital_good claim (the leg under "
        "test is actually present, not a vacuous no-op)",
    )
    # (4) The WHOLE classified profile is order-invariant: the claimed archetypes IN
    # RANK ORDER (which drives the fixed template-bank task order for cross-site
    # comparability) and the NA complement (excluded from every mean/spread, never
    # penalized) do not depend on surface-read order.
    _check(
        forward.archetypes == reverse.archetypes,
        "claimed archetypes (ordered) invariant under surface-read reorder "
        f"(forward {forward.archetypes}, reverse {reverse.archetypes})",
    )
    _check(
        set(forward.unclaimed) == set(reverse.unclaimed),
        "NA/unclaimed set invariant under surface-read reorder "
        f"(forward {sorted(forward.unclaimed)}, reverse {sorted(reverse.unclaimed)})",
    )


def test_offering_surface_order_invariance_org() -> None:
    """Order-invariance mirrored onto the .org half of the canonical pair.

    ``test_offering_surface_order_invariance_output_license`` above pins the
    surface-read-order-invariance of the WHOLE classified profile — but only on
    ``driftflight.com``. The relabel-invariance family already spans BOTH halves
    of the canonical pair (``_org``/``_com``); order-invariance lagged at one.
    This closes that asymmetry the same way the offering-layer relabel guards
    closed the two-vs-four gap against the scoring layer: a classification must
    not depend on which surface the discovery path happened to read first, on
    EITHER canonical domain.

    Non-vacuity is anchored on ``output-license``, which fires on drift-flight.org
    across >=2 distinct surfaces (``/pricing`` + ``homepage``), so a full read-order
    reversal permutes a REAL multi-surface accumulation — not a single-surface
    bystander. The .org fixture also reads MORE archetypes' multi-surface signals
    than .com's output-license alone, so the whole-profile assertions below carry
    genuine teeth on this half.
    """
    print("test_offering_surface_order_invariance_org")
    surfaces = _captured_surfaces("drift-flight.org")

    forward = _offering.classify_offering("drift-flight.org", dict(surfaces))
    reverse = _offering.classify_offering(
        "drift-flight.org", dict(reversed(list(surfaces.items())))
    )

    fwd_lic = _license_signals(forward)
    rev_lic = _license_signals(reverse)
    fwd_surfaces = {s for s, _ in fwd_lic}

    # Non-vacuity (a): the anchor signal genuinely fires across MULTIPLE surfaces
    # on THIS domain, so the reorder permutes a real per-archetype accumulation.
    _check(
        len(fwd_surfaces) >= 2,
        "output-license fires on >=2 distinct surfaces on drift-flight.org (a real "
        f"multi-surface accumulation, so the reorder is meaningful) (got {sorted(fwd_surfaces)})",
    )
    # Non-vacuity (b): the reorder is REAL and OBSERVABLE — surfaces_seen (the read
    # order) actually differs, so an order-INSENSITIVE reader would NOT make the
    # invariance below vacuously true.
    _check(
        list(forward.surfaces_seen) != list(reverse.surfaces_seen),
        "the surface-read order genuinely differs between the two runs "
        f"(forward head {list(forward.surfaces_seen)[:2]}, reverse head "
        f"{list(reverse.surfaces_seen)[:2]}) — the invariance is non-vacuous",
    )

    # (1) The anchor signal fires the SAME number of times under reorder.
    _check(
        len(rev_lic) == len(fwd_lic),
        "output-license match count invariant under surface-read reorder "
        f"(forward {len(fwd_lic)}, reverse {len(rev_lic)})",
    )
    # (2) It fires on the SAME set of surfaces — order cannot migrate the signal.
    _check(
        {s for s, _ in rev_lic} == fwd_surfaces,
        "output-license fires on the same set of surfaces under reorder "
        f"(forward {sorted(fwd_surfaces)}, reverse {sorted({s for s, _ in rev_lic})})",
    )
    # (3) STRONGER than the .com mirror: the COMPLETE evidence map — every claimed
    # archetype's (label, surface) pairs across the WHOLE profile — is invariant
    # under read-order reversal. No signal on ANY archetype is dropped, conjured,
    # or migrated to a different surface by which surface arrived first.
    def _evidence_map(prof):
        return {
            c.archetype: {(s.label, s.surface) for s in c.signals}
            for c in prof.claimed
        }

    fwd_map, rev_map = _evidence_map(forward), _evidence_map(reverse)
    _check(
        fwd_map == rev_map,
        "the complete per-archetype (label, surface) evidence map is invariant "
        "under surface-read reorder on drift-flight.org "
        f"(archetypes forward {sorted(fwd_map)}, reverse {sorted(rev_map)})",
    )
    # (4) The WHOLE classified profile is order-invariant: claimed archetypes IN
    # RANK ORDER (drives the fixed template-bank task order for cross-site
    # comparability) and the NA complement (excluded from every mean/spread) do
    # not depend on surface-read order.
    _check(
        forward.archetypes == reverse.archetypes,
        "claimed archetypes (ordered) invariant under surface-read reorder "
        f"(forward {forward.archetypes}, reverse {reverse.archetypes})",
    )
    _check(
        set(forward.unclaimed) == set(reverse.unclaimed),
        "NA/unclaimed set invariant under surface-read reorder "
        f"(forward {sorted(forward.unclaimed)}, reverse {sorted(reverse.unclaimed)})",
    )
    # (5) The anchor leg is actually PRESENT (property under test not vacuously
    # absent): output-license is part of the .org digital_good claim.
    dg_f = next(c for c in forward.claimed if c.archetype == "digital_good")
    _check(
        _LICENSE_LABEL in {s.label for s in dg_f.signals},
        "the output-license label is part of the drift-flight.org digital_good "
        "claim (the anchor leg is present, not a vacuous no-op)",
    )


# ---------------------------------------------------------------------------
# Content-SCALE invariance — a genuinely NEW perturbation axis on the offering
# path, distinct from surface-read ORDER (which surface arrives first) and host
# RELABEL (what the storefront is named). An offering claim is QUALITATIVE — does
# the site claim to serve archetype X? — never QUANTITATIVE. A storefront that
# repeats its pitch (says "per month" ten times, duplicates a section across a
# rebuild, mirrors the same prose on two surfaces) is not "more" of an archetype
# and MUST NOT out-rank or reorder against one that states each capability once.
# Two collaborating mechanisms make classification count-independent:
# `_scan_surface` takes the FIRST match per (archetype, label) via
# `pattern.search` (not `finditer`), and `ArchetypeClaim.strength` counts DISTINCT
# signal LABELS (not raw hits) — its docstring names exactly this "a page that
# repeats 'per month' ten times does not out-rank" rationale. This guard pins that
# rationale as an executable tripwire on REAL canonical evidence: duplicating every
# surface body must leave the WHOLE classified profile byte-identical.
#
# Teeth: the anchor's raw regex-match count genuinely MULTIPLIES under the
# duplication (n -> K*n), so a count-based reader WOULD see a difference — proving
# the reported invariance is a real property of the classifier, not a vacuous
# no-op. A regression to `finditer` + count-based strength (which would let volume
# reorder the ranking that drives the fixed template-bank task order) fails here.
# Mirrored onto BOTH canonical pair-halves from the start, so this axis does not
# inherit the .com-only asymmetry order-invariance had to close in Cycle 105.
# ---------------------------------------------------------------------------

_SCALE_K = 3  # duplicate each surface body this many times


def _dup_surface(raw: str) -> str:
    """Repeat a surface body ``_SCALE_K`` times, separated by blank lines.

    The blank-line separator cannot bridge two copies into a spurious new match
    (signals anchor on contiguous phrases), and ``strip_html`` collapses it away,
    so the doubled prose simply contains each real signal ``_SCALE_K`` times.
    """
    return ("\n\n").join([raw] * _SCALE_K)


def _surface_prose(surface: str, raw: str) -> str:
    """Reproduce ``classify_offering``'s per-surface prose derivation (for teeth counting)."""
    return (
        strip_html(raw)
        if (surface == "homepage" or _offering._is_html_document(raw))
        else raw
    )


def _signal_pattern(archetype: str, label: str):
    """The compiled pattern for one ``(archetype, label)`` signal, or ``None``."""
    for lbl, pat in _offering._SIGNALS[archetype]:
        if lbl == label:
            return pat
    return None


def _full_evidence_map(prof) -> dict:
    """archetype -> (strength, its full sorted (label, surface, quote) evidence)."""
    return {
        c.archetype: (
            c.strength,
            sorted((s.label, s.surface, s.quote) for s in c.signals),
        )
        for c in prof.claimed
    }


def _assert_content_scale_invariance(domain: str, expected_claimed: set) -> None:
    """Duplicating every surface body leaves the whole classified profile identical."""
    surfaces = _captured_surfaces(domain)
    base = _offering.classify_offering(domain, dict(surfaces))

    # The property under test is genuinely present: the domain claims the expected
    # multi-archetype set, RANKED, so a count-based reorder would be observable.
    _check(
        set(base.archetypes) == expected_claimed,
        f"{domain}: base claimed set == {sorted(expected_claimed)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        len(base.claimed) >= 2,
        f"{domain}: >=2 archetypes claimed, so the ranking a volume regression could "
        f"reorder is real (got {base.archetypes})",
    )

    dup_surfaces = {s: _dup_surface(r) for s, r in surfaces.items()}
    # Non-vacuity: the duplication genuinely enlarged every surface the classifier
    # reads — its input really changed.
    _check(
        all(len(dup_surfaces[s]) > len(surfaces[s]) for s in surfaces),
        f"{domain}: every surface body grew under {_SCALE_K}x duplication "
        "(the perturbation is real, not a no-op)",
    )
    # TEETH: a count-based reader WOULD see strictly more. The anchor archetype's
    # first signal fires K times as many RAW matches after duplication, yet the
    # classifier below reports the SAME single signal / strength / rank — proving
    # count-independence is a real property, not a vacuous invariance.
    anchor = base.claimed[0].signals[0]
    pat = _signal_pattern(anchor.archetype, anchor.label)
    _check(pat is not None, f"{domain}: anchor signal pattern resolvable")
    n_base = len(pat.findall(_surface_prose(anchor.surface, surfaces[anchor.surface])))
    n_dup = len(pat.findall(_surface_prose(anchor.surface, dup_surfaces[anchor.surface])))
    _check(
        n_base >= 1 and n_dup > n_base,
        f"{domain}: the anchor signal ({anchor.archetype}/{anchor.label}) fires MORE raw "
        f"matches under duplication ({n_base} -> {n_dup}) — a count-based reader would differ",
    )

    dup = _offering.classify_offering(domain, dict(dup_surfaces))

    # (1) The WHOLE classified profile is byte-identical: every archetype's strength
    # AND its complete (label, surface, quote) evidence survive duplication unchanged
    # — no signal multiplied, no quote drifted, no archetype conjured.
    _check(
        _full_evidence_map(dup) == _full_evidence_map(base),
        f"{domain}: complete per-archetype (strength, (label, surface, quote)) evidence "
        "map invariant under content duplication",
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order (cross-site comparability), so volume must not
    # reorder it.
    _check(
        dup.archetypes == base.archetypes,
        f"{domain}: claimed archetypes (ranked) invariant under duplication "
        f"(base {base.archetypes}, dup {dup.archetypes})",
    )
    # (3) The NA/unclaimed set (excluded from every mean/spread, never penalized) is
    # invariant — which archetypes a site is judged on vs excused as NA is a property
    # of WHAT it claims, not how many times it says it.
    _check(
        set(dup.unclaimed) == set(base.unclaimed),
        f"{domain}: NA/unclaimed set invariant under duplication "
        f"(base {sorted(base.unclaimed)}, dup {sorted(dup.unclaimed)})",
    )


def test_offering_content_scale_invariance_org() -> None:
    """A storefront that repeats its pitch is not "more" of any archetype (.org)."""
    print("test_offering_content_scale_invariance_org")
    _assert_content_scale_invariance("drift-flight.org", EXPECTED_CLAIMED["drift-flight.org"])


def test_offering_content_scale_invariance_com() -> None:
    """Content-scale invariance mirrored onto the .com half of the canonical pair."""
    print("test_offering_content_scale_invariance_com")
    _assert_content_scale_invariance("driftflight.com", EXPECTED_CLAIMED["driftflight.com"])


# ---------------------------------------------------------------------------
# Content-scale invariance on the NO-RAILS retail store — the credibility-
# protecting direction of the SCALE axis, closing the same org/com-only-vs-retail
# asymmetry the noise-surface axis closed one increment earlier. `_org`/`_com`
# above prove a WITH-RAILS storefront that repeats its pitch is not "more" of any
# archetype (multi-archetype, ranked); this pins the OPPOSITE storefront type: a
# pure book catalog that claims ONLY physical_good with every rails archetype NA
# (metered_api / subscription / digital_good). The property it protects is the
# "never manufacture the delta" invariant applied to the SCALE axis: duplicating a
# no-rails retailer's catalog prose N times must not push its physical_good claim
# up in strength AND must not CONJURE a rails archetype it does not offer. The
# classified delta between a rails storefront and a no-rails one has to come from
# real published capability, never from how much a store repeats itself.
#
# Two structural differences from `_assert_content_scale_invariance` force a
# dedicated test rather than a reuse of the canonical helper:
#   * the retail store claims a SINGLE archetype, so the helper's `len(claimed)
#     >= 2` rank-reorder premise does not apply (there is no multi-archetype
#     ranking to perturb — the guarded property is instead "strength holds and the
#     NA rails set stays NA");
#   * non-vacuity is therefore anchored on physical_good's own signals, which fire
#     MORE raw matches under duplication (a count-based reader would differ), plus
#     the NA-rails-stay-NA teeth, rather than on an observable rank reorder.
# ---------------------------------------------------------------------------


def test_offering_content_scale_invariance_retail() -> None:
    """Repeating a no-rails catalog is not "more" physical_good — and conjures no rails."""
    print("test_offering_content_scale_invariance_retail")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface premise: the retail fixture is a
    # single-surface homepage catalog, and the scale axis duplicates whatever base
    # the store publishes.)
    path = os.path.join(_FIXTURE_DIR, f"{_RETAIL}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_RETAIL, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # physical_good, with every rails archetype NA — so a rails claim conjured by
    # sheer repetition would be unmistakably observable.
    _check(
        set(base.archetypes) == _RETAIL_CLAIMED,
        f"{_RETAIL}: base claimed set == {sorted(_RETAIL_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        _RETAIL_MUST_BE_NA <= set(base.unclaimed),
        f"{_RETAIL}: the rails archetypes {sorted(_RETAIL_MUST_BE_NA)} are all NA at "
        f"base (got unclaimed {sorted(base.unclaimed)}) — the no-rails property the "
        "duplication must not overturn is present",
    )

    dup_surfaces = {s: _dup_surface(r) for s, r in captured.items()}
    # Non-vacuity: the duplication genuinely enlarged every surface the classifier
    # reads — its input really changed.
    _check(
        all(len(dup_surfaces[s]) > len(captured[s]) for s in captured),
        f"{_RETAIL}: every surface body grew under {_SCALE_K}x duplication "
        "(the perturbation is real, not a no-op)",
    )
    # TEETH: a count-based reader WOULD see strictly more. physical_good's first
    # signal fires K times as many RAW matches after duplication, yet the classifier
    # below reports the SAME single signal / strength / claim — proving count-
    # independence is a real property on the retail pole, not a vacuous invariance.
    anchor = base.claimed[0].signals[0]
    _check(
        anchor.archetype == "physical_good",
        f"{_RETAIL}: the anchor signal is a physical_good leg (got {anchor.archetype})",
    )
    pat = _signal_pattern(anchor.archetype, anchor.label)
    _check(pat is not None, f"{_RETAIL}: anchor signal pattern resolvable")
    n_base = len(pat.findall(_surface_prose(anchor.surface, captured[anchor.surface])))
    n_dup = len(pat.findall(_surface_prose(anchor.surface, dup_surfaces[anchor.surface])))
    _check(
        n_base >= 1 and n_dup > n_base,
        f"{_RETAIL}: the anchor signal ({anchor.archetype}/{anchor.label}) fires MORE raw "
        f"matches under duplication ({n_base} -> {n_dup}) — a count-based reader would differ",
    )

    dup = _offering.classify_offering(_RETAIL, dict(dup_surfaces))

    # (1) The WHOLE classified profile is byte-identical: physical_good's strength
    # AND its complete (label, surface, quote) evidence survive duplication unchanged
    # — no signal multiplied, no quote drifted, no rails archetype conjured.
    _check(
        _full_evidence_map(dup) == _full_evidence_map(base),
        f"{_RETAIL}: complete per-archetype (strength, (label, surface, quote)) evidence "
        "map invariant under content duplication",
    )
    # (2) Claimed archetypes invariant — still EXACTLY physical_good. Repetition
    # conjured no rails claim; the "never manufacture the delta" property on the
    # SCALE axis.
    _check(
        dup.archetypes == base.archetypes,
        f"{_RETAIL}: claimed archetypes invariant under duplication "
        f"(base {base.archetypes}, dup {dup.archetypes})",
    )
    # (3) The rails archetypes stay NA and the whole NA set is invariant — which
    # archetypes a no-rails store is excused on as NA is a property of WHAT it
    # claims, never of how many times it says it.
    _check(
        _RETAIL_MUST_BE_NA <= set(dup.unclaimed)
        and set(dup.unclaimed) == set(base.unclaimed),
        f"{_RETAIL}: the rails archetypes stay NA and the whole NA set is invariant "
        f"under duplication (base {sorted(base.unclaimed)}, dup {sorted(dup.unclaimed)})",
    )


# ---------------------------------------------------------------------------
# Content-scale invariance on the MACHINE (API-first) pole — closing the same
# org/com/retail-vs-machine asymmetry the surface-dedup axis already closed
# (Cycle 159), now for the SCALE axis. `_org`/`_com` pin the multi-archetype
# PROSE pole, `_retail` the single-archetype no-rails catalog; this pins the
# single-archetype metered_api OpenAPI-spec pole (`api.replicate.com`, which
# claims ONLY metered_api off its `/openapi.json` doc surface). This is the
# NATIVE home of the metered claim — the one committed machine-contract
# storefront earns its metered_api from that spec ALONE (pinned by
# `test_machine_surface_openapi_storefront`) — so a volume dependence here would
# corrupt the archetype on its home turf. The property it protects is the "never
# manufacture the delta" invariant on the SCALE axis, from the metered pole:
# repeating a spec's prose N times (an endpoint block copy-pasted across a
# rebuild, the same `POST` echoed in overview + reference) must not push
# metered_api up in strength AND must not CONJURE a rails archetype
# (subscription / physical_good / ...) the API does not offer. An API is not
# "more" metered — nor suddenly a shop — because its one spec repeats itself.
#
# Two structural differences from `_assert_content_scale_invariance` force a
# dedicated test rather than a reuse of the canonical helper (the same two the
# surface-dedup machine pole names):
#   * the shared helper's non-vacuity rests on `len(base.claimed) >= 2` so a
#     count-driven RANK REORDER is observable; the machine pole claims exactly
#     ONE archetype, so "reorder" is structurally impossible and would be the
#     wrong non-vacuity proof. The single-claim analogue below is stronger in the
#     credibility direction: the teeth are (a) the anchor metered_api signal
#     fires MORE raw matches under duplication (a count-based reader would
#     differ), and (b) the five sibling archetypes stay NA — no rail is conjured
#     by repetition;
#   * `_captured_surfaces` requires `>=2` READ surfaces for a reorder to matter;
#     the machine pole reads exactly {homepage, /openapi.json}, so the base is
#     captured inline (the same spy pattern the casing / surface-dedup machine
#     poles use) and the scale axis duplicates whatever body the store publishes.
# ---------------------------------------------------------------------------


def test_offering_content_scale_invariance_machine() -> None:
    """Repeating an API-first store's one spec is not "more" metered_api — and conjures no rails."""
    print("test_offering_content_scale_invariance_machine")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface reorder premise: the machine pole
    # reads {homepage, /openapi.json} and the scale axis duplicates the spec body.)
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_MACHINE_SURFACE, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # metered_api, with every other archetype NA — so a rails claim conjured by
    # sheer repetition, or a strengthened metered_api, would be observable.
    _check(
        set(base.archetypes) == _MACHINE_CLAIMED,
        f"{_MACHINE_SURFACE}: base claimed set == {sorted(_MACHINE_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    machine_must_be_na = set(_offering.ARCHETYPES) - _MACHINE_CLAIMED
    _check(
        machine_must_be_na <= set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes {sorted(machine_must_be_na)} are "
        f"all NA at base (got unclaimed {sorted(base.unclaimed)}) — the single-claim "
        "property the duplication must not overturn is present",
    )

    dup_surfaces = {s: _dup_surface(r) for s, r in captured.items()}
    # Non-vacuity: the duplication genuinely enlarged every surface the classifier
    # reads — its input really changed.
    _check(
        all(len(dup_surfaces[s]) > len(captured[s]) for s in captured),
        f"{_MACHINE_SURFACE}: every surface body grew under {_SCALE_K}x duplication "
        "(the perturbation is real, not a no-op)",
    )
    # TEETH: a count-based reader WOULD see strictly more. metered_api's anchor
    # signal fires K times as many RAW matches after duplication, yet the classifier
    # below reports the SAME single signal / strength / claim — proving count-
    # independence is a real property on the machine pole, not a vacuous invariance.
    anchor = base.claimed[0].signals[0]
    _check(
        anchor.archetype == "metered_api",
        f"{_MACHINE_SURFACE}: the anchor signal is a metered_api leg (got {anchor.archetype})",
    )
    pat = _signal_pattern(anchor.archetype, anchor.label)
    _check(pat is not None, f"{_MACHINE_SURFACE}: anchor signal pattern resolvable")
    n_base = len(pat.findall(_surface_prose(anchor.surface, captured[anchor.surface])))
    n_dup = len(pat.findall(_surface_prose(anchor.surface, dup_surfaces[anchor.surface])))
    _check(
        n_base >= 1 and n_dup > n_base,
        f"{_MACHINE_SURFACE}: the anchor signal ({anchor.archetype}/{anchor.label}) fires MORE "
        f"raw matches under duplication ({n_base} -> {n_dup}) — a count-based reader would differ",
    )

    dup = _offering.classify_offering(_MACHINE_SURFACE, dict(dup_surfaces))

    # (1) The WHOLE classified profile is byte-identical: metered_api's strength AND
    # its complete (label, surface, quote) evidence survive duplication unchanged —
    # no signal multiplied, no quote drifted, no rails archetype conjured.
    _check(
        _full_evidence_map(dup) == _full_evidence_map(base),
        f"{_MACHINE_SURFACE}: complete per-archetype (strength, (label, surface, quote)) "
        "evidence map invariant under content duplication",
    )
    # (2) Claimed archetypes invariant — still EXACTLY metered_api. Repetition
    # conjured no rails claim; the "never manufacture the delta" property on the
    # SCALE axis, from the machine pole.
    _check(
        dup.archetypes == base.archetypes,
        f"{_MACHINE_SURFACE}: claimed archetypes invariant under duplication "
        f"(base {base.archetypes}, dup {dup.archetypes})",
    )
    # (3) The non-metered archetypes stay NA and the whole NA set is invariant —
    # which archetypes an API-first store is excused on as NA is a property of WHAT
    # it claims, never of how many times its spec says it.
    _check(
        machine_must_be_na <= set(dup.unclaimed)
        and set(dup.unclaimed) == set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes stay NA and the whole NA set is "
        f"invariant under duplication (base {sorted(base.unclaimed)}, dup {sorted(dup.unclaimed)})",
    )


# ---------------------------------------------------------------------------
# Noise-surface invariance — the FOURTH metamorphic axis on the classifier.
#
# The three families above perturb the surfaces a site DOES publish: RELABEL
# rewrites the host inside them, ORDER reverses the sequence they arrive in,
# SCALE duplicates their bodies. This axis is the complement: it ADDS a NEW
# readable surface that carries NO capability signal — the cookie/privacy notice,
# the careers blurb, the legal footer, the metaphorical-"ship" marketing prose
# every real storefront also serves — and asserts the classified CAPABILITY
# profile is byte-identical. The score must measure what a site DECLARES it can
# do, not how much incidental web chrome surrounds it; a privacy policy must not
# conjure an archetype, and it must not retract one. Only ``surfaces_seen`` (a
# read-provenance record, not a capability claim) may reflect the extra read.
#
# Non-vacuity has three teeth, mirroring the SCALE test's structure:
#   (a) the noise surface is genuinely READ — it lands in ``surfaces_seen`` — so
#       the invariance is "noise contributes no claim", not "the classifier
#       skipped an empty surface";
#   (b) the distractor prose fires ZERO signals under ``_scan_surface`` (asserted
#       directly), despite being loaded with the exact near-miss traps the
#       precision guards dodge (metaphorical "ship" ×3, cookie/careers/legal
#       boilerplate) — so this doubles as a precision demonstration on realistic
#       chrome;
#   (c) a negative control swaps the SAME surface key's body for real fulfillment
#       prose and shows the profile DOES change — proving the added-surface channel
#       can move the classification, so the invariance for noise is meaningful.
# ---------------------------------------------------------------------------

# A realistic non-commerce web-chrome blob: cookie/privacy notice, an about/careers
# page, a legal footer. Loaded with the precision-critical near-miss vocabulary the
# signal bank must NOT fire on — "ship" three times (all metaphorical: shipping
# ideas/creativity, never a physical good), "dream", "value", "informational" —
# yet it declares no archetype. If a future signal-bank change makes this fire, the
# direct ``_scan_surface`` assertion below fails loudly: that is either a new
# legitimate signal (re-curate the distractor) or a precision regression (fix it).
_NOISE_PROSE = (
    "Privacy & Cookies. We use cookies to remember your preferences and improve "
    "your experience. By continuing to browse you accept our cookie notice. You "
    "may adjust your choices at any time from the footer. We never sell your "
    "personal data.\n\n"
    "About us. We are a small remote team who love to ship ideas, not boxes — we "
    "ship creativity and dream big. Our culture is built on curiosity and craft.\n\n"
    "Careers. We are hiring! Join a friendly, mission-driven crew. We value "
    "kindness, ownership, and a growth mindset. Read employee stories on our blog.\n\n"
    "Legal. All trademarks belong to their respective owners. This notice is "
    "provided for informational purposes only and does not constitute advice."
)
# The negative control: real physical-fulfillment prose on the SAME surface key.
# It MUST fire (physical_good is NA on the canonical pair, so a claim it conjures
# is unmistakably observable) — proving an added surface can move the profile.
_NOISE_TEETH_PROSE = (
    "Add to cart. In stock now — we offer free shipping on all physical orders "
    "to your shipping address."
)
_NOISE_SURFACE = "/privacy"


def _assert_noise_surface_invariance(domain: str, expected_claimed: set) -> None:
    """Adding a signal-free readable surface leaves the capability profile identical."""
    surfaces = _captured_surfaces(domain)
    base = _offering.classify_offering(domain, dict(surfaces))

    # The property under test is genuinely present: the domain claims the expected
    # multi-archetype set, RANKED, so an added surface that perturbed a claim or a
    # rank would be observable.
    _check(
        set(base.archetypes) == expected_claimed,
        f"{domain}: base claimed set == {sorted(expected_claimed)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        len(base.claimed) >= 2,
        f"{domain}: >=2 archetypes claimed, so the ranking an added surface could "
        f"reorder is real (got {base.archetypes})",
    )
    # The extra surface key does not collide with a real captured surface (adding it
    # is a genuine ADDITION, not an overwrite that could hide a change).
    _check(
        _NOISE_SURFACE not in surfaces,
        f"{domain}: the noise surface key {_NOISE_SURFACE!r} is new, not an overwrite "
        f"(captured surfaces: {list(surfaces)})",
    )

    # TEETH (b): the distractor carries NO capability signal at all, despite its
    # near-miss vocabulary. This is what makes the invariance below "noise adds no
    # claim" rather than "we added a signal that happened to match an existing one".
    _check(
        _offering._scan_surface(_NOISE_SURFACE, _NOISE_PROSE) == [],
        f"{domain}: the distractor prose fires ZERO archetype signals "
        f"(got {[(s.archetype, s.label) for s in _offering._scan_surface(_NOISE_SURFACE, _NOISE_PROSE)]})",
    )

    noisy = _offering.classify_offering(
        domain, {**surfaces, _NOISE_SURFACE: _NOISE_PROSE}
    )

    # TEETH (a): the noise surface was genuinely READ — it reached the scanner and
    # landed in the read-provenance record — yet it contributed no claim. So the
    # invariance is non-vacuous: the classifier ingested the extra input.
    _check(
        _NOISE_SURFACE in noisy.surfaces_seen,
        f"{domain}: the noise surface {_NOISE_SURFACE!r} was read "
        f"(surfaces_seen {noisy.surfaces_seen})",
    )

    # (1) The WHOLE classified capability profile is byte-identical: every
    # archetype's strength AND its complete (label, surface, quote) evidence survive
    # the added surface unchanged — no signal conjured, no quote drifted, no
    # archetype added or retracted.
    _check(
        _full_evidence_map(noisy) == _full_evidence_map(base),
        f"{domain}: complete per-archetype (strength, (label, surface, quote)) "
        "evidence map invariant under a signal-free added surface",
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order (cross-site comparability), so incidental chrome must
    # not reorder it.
    _check(
        noisy.archetypes == base.archetypes,
        f"{domain}: claimed archetypes (ranked) invariant under a signal-free added "
        f"surface (base {base.archetypes}, noisy {noisy.archetypes})",
    )
    # (3) The NA/unclaimed set (excluded from every mean/spread, never penalized) is
    # invariant — which archetypes a site is judged on vs excused as NA is a property
    # of WHAT it declares, not what boilerplate surrounds it.
    _check(
        set(noisy.unclaimed) == set(base.unclaimed),
        f"{domain}: NA/unclaimed set invariant under a signal-free added surface "
        f"(base {sorted(base.unclaimed)}, noisy {sorted(noisy.unclaimed)})",
    )
    # (4) The ONLY thing that changed is the read-provenance: surfaces_seen grew by
    # exactly the noise surface. This pins the honest scope of the invariance — the
    # classifier records that it read the extra surface, and records nothing else
    # from it.
    _check(
        set(noisy.surfaces_seen) == set(base.surfaces_seen) | {_NOISE_SURFACE},
        f"{domain}: surfaces_seen grew by exactly {_NOISE_SURFACE!r} and nothing else "
        f"(base {sorted(base.surfaces_seen)}, noisy {sorted(noisy.surfaces_seen)})",
    )

    # TEETH (c): the negative control — swap the SAME surface key for real
    # fulfillment prose. The profile MUST change (physical_good, NA on the canonical
    # pair, is conjured), proving an added surface CAN move the classification, so
    # the invariance for the distractor is meaningful, not a channel the classifier
    # ignores.
    teeth = _offering.classify_offering(
        domain, {**surfaces, _NOISE_SURFACE: _NOISE_TEETH_PROSE}
    )
    _check(
        _full_evidence_map(teeth) != _full_evidence_map(base)
        and "physical_good" in teeth.archetypes,
        f"{domain}: a signal-BEARING added surface DOES move the profile "
        f"(physical_good conjured: {'physical_good' in teeth.archetypes}) — the "
        "added-surface channel is live, so noise-invariance is non-vacuous",
    )


def test_offering_noise_surface_invariance_org() -> None:
    """Incidental web chrome (privacy/careers/legal) conjures no archetype (.org)."""
    print("test_offering_noise_surface_invariance_org")
    _assert_noise_surface_invariance("drift-flight.org", EXPECTED_CLAIMED["drift-flight.org"])


def test_offering_noise_surface_invariance_com() -> None:
    """Noise-surface invariance mirrored onto the .com half of the canonical pair."""
    print("test_offering_noise_surface_invariance_com")
    _assert_noise_surface_invariance("driftflight.com", EXPECTED_CLAIMED["driftflight.com"])


# ---------------------------------------------------------------------------
# Noise-surface invariance on the NO-RAILS retail store — the credibility-
# protecting direction of this axis. `_org`/`_com` above prove incidental chrome
# adds no claim on the WITH-RAILS canonical pair (multi-archetype, ranked). This
# closes the axis onto the OPPOSITE storefront type: a pure book catalog that
# claims ONLY physical_good and has EVERY rails archetype NA (metered_api /
# subscription / digital_good / service_booking / data_retrieval). The property
# it pins is exactly the "never manufacture the delta" invariant applied to task
# discovery: bolting incidental web chrome onto a no-rails retailer must not
# CONJURE a rails claim it does not make — the classified delta between a rails
# storefront and a no-rails one has to come from real published capability, never
# from how much boilerplate surrounds the catalog.
#
# Two structural differences from the canonical helper force a dedicated test
# rather than a reuse of `_assert_noise_surface_invariance`:
#   * the retail store claims a SINGLE archetype, so the helper's `len(claimed)
#     >= 2` rank-reorder premise does not apply (there is no ranking to perturb —
#     the guarded property is instead "the NA rails set stays NA");
#   * the helper's negative control conjures `physical_good`, which is ALREADY
#     claimed here, so it would be a no-op. The retail-appropriate teeth conjure
#     `metered_api` — a rails archetype that IS NA on this store — so a signal-
#     bearing added surface observably moves the profile, proving the added-
#     surface channel is live and the chrome-invariance below is non-vacuous.
#
# Non-vacuity mirrors the canonical guard's three teeth: (a) the noise surface is
# genuinely READ (lands in surfaces_seen) yet contributes no claim; (b) the
# distractor prose fires ZERO signals under `_scan_surface`; (c) the metered_api
# negative control DOES move the profile.
# ---------------------------------------------------------------------------

# A rails-bearing added surface: real programmatic-API prose (auth + metered
# billing + rate limits) for a metered_api archetype that is NA on the retail
# store. It MUST fire (metered_api is NA on a book catalog, so a claim it conjures
# is unmistakably observable) — proving an added surface can move the profile.
_RETAIL_NOISE_TEETH_PROSE = (
    "POST /v1/generate. Authenticate with your API key as a Bearer token. "
    "Billed per request, metered per API call. Rate limits apply."
)


def test_offering_noise_surface_invariance_retail() -> None:
    """Incidental web chrome conjures no RAILS claim on a no-rails retail store."""
    print("test_offering_noise_surface_invariance_retail")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface premise: the retail fixture is a
    # single-surface homepage catalog, and the noise axis only needs to ADD one
    # surface to whatever base the store publishes.)
    path = os.path.join(_FIXTURE_DIR, f"{_RETAIL}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_RETAIL, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # physical_good, with every rails archetype NA — so a conjured rails claim
    # would be unmistakably observable.
    _check(
        set(base.archetypes) == _RETAIL_CLAIMED,
        f"{_RETAIL}: base claimed set == {sorted(_RETAIL_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        _RETAIL_MUST_BE_NA <= set(base.unclaimed),
        f"{_RETAIL}: the rails archetypes {sorted(_RETAIL_MUST_BE_NA)} are all NA at "
        f"base (got unclaimed {sorted(base.unclaimed)}) — the no-rails property the "
        "noise must not overturn is present",
    )
    # The extra surface key is a genuine ADDITION, not an overwrite that could hide
    # a change.
    _check(
        _NOISE_SURFACE not in captured,
        f"{_RETAIL}: the noise surface key {_NOISE_SURFACE!r} is new, not an overwrite "
        f"(captured surfaces: {list(captured)})",
    )

    # TEETH (b): the distractor carries NO capability signal, despite its near-miss
    # vocabulary (metaphorical "ship", cookie/careers/legal chrome) — so the
    # invariance is "noise adds no claim", not "we matched an existing signal".
    _check(
        _offering._scan_surface(_NOISE_SURFACE, _NOISE_PROSE) == [],
        f"{_RETAIL}: the distractor prose fires ZERO archetype signals "
        f"(got {[(s.archetype, s.label) for s in _offering._scan_surface(_NOISE_SURFACE, _NOISE_PROSE)]})",
    )

    noisy = _offering.classify_offering(
        _RETAIL, {**captured, _NOISE_SURFACE: _NOISE_PROSE}
    )

    # TEETH (a): the noise surface was genuinely READ — it reached the scanner and
    # landed in the read-provenance record — yet contributed no claim.
    _check(
        _NOISE_SURFACE in noisy.surfaces_seen,
        f"{_RETAIL}: the noise surface {_NOISE_SURFACE!r} was read "
        f"(surfaces_seen {noisy.surfaces_seen})",
    )

    # (1) The WHOLE classified profile is byte-identical: physical_good's strength
    # AND its complete (label, surface, quote) evidence survive the added surface
    # unchanged — no signal conjured, no quote drifted, no archetype added.
    _check(
        _full_evidence_map(noisy) == _full_evidence_map(base),
        f"{_RETAIL}: complete per-archetype (strength, (label, surface, quote)) "
        "evidence map invariant under a signal-free added surface",
    )
    # (2) Claimed archetypes invariant (still exactly physical_good — no rails claim
    # conjured by the chrome).
    _check(
        noisy.archetypes == base.archetypes,
        f"{_RETAIL}: claimed archetypes invariant under a signal-free added surface "
        f"(base {base.archetypes}, noisy {noisy.archetypes})",
    )
    # (3) The rails archetypes stay NA — the "never manufacture the delta" property:
    # incidental boilerplate cannot push a no-rails store toward a rails claim.
    _check(
        _RETAIL_MUST_BE_NA <= set(noisy.unclaimed)
        and set(noisy.unclaimed) == set(base.unclaimed),
        f"{_RETAIL}: the rails archetypes stay NA and the whole NA set is invariant "
        f"under a signal-free added surface (base {sorted(base.unclaimed)}, "
        f"noisy {sorted(noisy.unclaimed)})",
    )
    # (4) The ONLY change is read-provenance: surfaces_seen grew by exactly the noise
    # surface and nothing else.
    _check(
        set(noisy.surfaces_seen) == set(base.surfaces_seen) | {_NOISE_SURFACE},
        f"{_RETAIL}: surfaces_seen grew by exactly {_NOISE_SURFACE!r} and nothing else "
        f"(base {sorted(base.surfaces_seen)}, noisy {sorted(noisy.surfaces_seen)})",
    )

    # TEETH (c): the retail-appropriate negative control — swap the SAME surface key
    # for real programmatic-API prose. metered_api (NA on this book catalog) MUST be
    # conjured, proving an added surface CAN move the classification, so the chrome-
    # invariance above is meaningful, not a channel the classifier ignores.
    teeth = _offering.classify_offering(
        _RETAIL, {**captured, _NOISE_SURFACE: _RETAIL_NOISE_TEETH_PROSE}
    )
    _check(
        _full_evidence_map(teeth) != _full_evidence_map(base)
        and "metered_api" in teeth.archetypes,
        f"{_RETAIL}: a rails-BEARING added surface DOES move the profile "
        f"(metered_api conjured: {'metered_api' in teeth.archetypes}) — the "
        "added-surface channel is live, so noise-invariance is non-vacuous",
    )


# ---------------------------------------------------------------------------
# Noise-surface invariance on the MACHINE (API-first) pole — closing the last
# org/com/retail-vs-machine asymmetry on the NOISE axis (the content-scale and
# surface-dedup axes already reach all four poles; the whitespace axis is
# machine-only by construction). `_org`/`_com` pin the multi-archetype PROSE
# pole, `_retail` the single-archetype no-rails catalog; this pins the single-
# archetype metered_api OpenAPI-spec pole (`api.replicate.com`, which claims ONLY
# metered_api off its `/openapi.json` doc surface — its NATIVE home, pinned by
# `test_machine_surface_openapi_storefront`). The property it protects is the
# "never manufacture the delta" invariant on the NOISE axis, from the metered
# pole: bolting incidental web chrome (a cookie/privacy notice, a careers blurb,
# a legal footer) onto an API-first storefront must not CONJURE a rails archetype
# (subscription / physical_good / ...) the spec does not offer, nor strengthen or
# retract the metered_api claim. An API is not suddenly a shop — nor "more"
# metered — because a privacy page sits next to its spec.
#
# Two structural differences from `_assert_noise_surface_invariance` force a
# dedicated test rather than a reuse of the canonical helper (the same two the
# content-scale / surface-dedup machine poles name):
#   * the shared helper's non-vacuity rests on `len(base.claimed) >= 2` so an
#     added surface that REORDERED the ranking would be observable; the machine
#     pole claims exactly ONE archetype, so "reorder" is structurally impossible
#     and would be the wrong non-vacuity proof. The single-claim analogue below
#     is the credibility-direction one the retail pole uses: the guarded property
#     is "the rails/other archetypes stay NA", and the negative-control teeth
#     conjure a NON-metered archetype (physical_good, NA here) so a signal-bearing
#     added surface observably moves the profile;
#   * `_captured_surfaces` requires `>=2` READ surfaces for a reorder to matter;
#     the machine pole reads exactly {homepage, /openapi.json}, so the base is
#     captured inline (the same spy pattern the content-scale / whitespace machine
#     poles use) and the noise axis adds one signal-free surface to it.
#
# Non-vacuity mirrors the canonical guard's three teeth: (a) the noise surface is
# genuinely READ (lands in surfaces_seen) yet contributes no claim; (b) the
# distractor prose fires ZERO signals under `_scan_surface`; (c) the physical_good
# negative control DOES move the profile — the added-surface channel is live.
# The whole per-archetype (strength, (label, surface, quote)) evidence map is
# asserted byte-identical (not the quote-excluded skeleton the whitespace axis
# must fall back to): unlike a reflow, an ADDED signal-free surface never touches
# the bytes of the surfaces the fired evidence is quoted from, so the sampled
# quotes cannot drift.
# ---------------------------------------------------------------------------


def test_offering_noise_surface_invariance_machine() -> None:
    """Incidental web chrome conjures no rails claim on an API-first metered store."""
    print("test_offering_noise_surface_invariance_machine")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface reorder premise: the machine pole
    # reads {homepage, /openapi.json} and the noise axis adds one signal-free surface.)
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_MACHINE_SURFACE, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # metered_api, with every other archetype NA — so a rails claim conjured by
    # incidental chrome, or a strengthened metered_api, would be observable.
    _check(
        set(base.archetypes) == _MACHINE_CLAIMED,
        f"{_MACHINE_SURFACE}: base claimed set == {sorted(_MACHINE_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    machine_must_be_na = set(_offering.ARCHETYPES) - _MACHINE_CLAIMED
    _check(
        machine_must_be_na <= set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes {sorted(machine_must_be_na)} are "
        f"all NA at base (got unclaimed {sorted(base.unclaimed)}) — the single-claim "
        "property the noise must not overturn is present",
    )
    # The extra surface key is a genuine ADDITION, not an overwrite that could hide
    # a change.
    _check(
        _NOISE_SURFACE not in captured,
        f"{_MACHINE_SURFACE}: the noise surface key {_NOISE_SURFACE!r} is new, not an "
        f"overwrite (captured surfaces: {list(captured)})",
    )

    # TEETH (b): the distractor carries NO capability signal, despite its near-miss
    # vocabulary (metaphorical "ship", cookie/careers/legal chrome) — so the
    # invariance is "noise adds no claim", not "we matched an existing signal".
    _check(
        _offering._scan_surface(_NOISE_SURFACE, _NOISE_PROSE) == [],
        f"{_MACHINE_SURFACE}: the distractor prose fires ZERO archetype signals "
        f"(got {[(s.archetype, s.label) for s in _offering._scan_surface(_NOISE_SURFACE, _NOISE_PROSE)]})",
    )

    noisy = _offering.classify_offering(
        _MACHINE_SURFACE, {**captured, _NOISE_SURFACE: _NOISE_PROSE}
    )

    # TEETH (a): the noise surface was genuinely READ — it reached the scanner and
    # landed in the read-provenance record — yet contributed no claim.
    _check(
        _NOISE_SURFACE in noisy.surfaces_seen,
        f"{_MACHINE_SURFACE}: the noise surface {_NOISE_SURFACE!r} was read "
        f"(surfaces_seen {noisy.surfaces_seen})",
    )

    # (1) The WHOLE classified profile is byte-identical: metered_api's strength AND
    # its complete (label, surface, quote) evidence survive the added surface
    # unchanged — no signal conjured, no quote drifted, no rails archetype added.
    _check(
        _full_evidence_map(noisy) == _full_evidence_map(base),
        f"{_MACHINE_SURFACE}: complete per-archetype (strength, (label, surface, quote)) "
        "evidence map invariant under a signal-free added surface",
    )
    # (2) Claimed archetypes invariant — still EXACTLY metered_api. The chrome
    # conjured no rails claim; the "never manufacture the delta" property on the
    # NOISE axis, from the machine pole.
    _check(
        noisy.archetypes == base.archetypes,
        f"{_MACHINE_SURFACE}: claimed archetypes invariant under a signal-free added "
        f"surface (base {base.archetypes}, noisy {noisy.archetypes})",
    )
    # (3) The non-metered archetypes stay NA and the whole NA/unclaimed set is
    # invariant — which archetypes an API-first store is excused on as NA is a
    # property of WHAT its spec declares, never of what boilerplate surrounds it.
    _check(
        machine_must_be_na <= set(noisy.unclaimed)
        and set(noisy.unclaimed) == set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes stay NA and the whole NA set is "
        f"invariant under a signal-free added surface (base {sorted(base.unclaimed)}, "
        f"noisy {sorted(noisy.unclaimed)})",
    )
    # (4) The ONLY change is read-provenance: surfaces_seen grew by exactly the noise
    # surface and nothing else.
    _check(
        set(noisy.surfaces_seen) == set(base.surfaces_seen) | {_NOISE_SURFACE},
        f"{_MACHINE_SURFACE}: surfaces_seen grew by exactly {_NOISE_SURFACE!r} and nothing "
        f"else (base {sorted(base.surfaces_seen)}, noisy {sorted(noisy.surfaces_seen)})",
    )

    # TEETH (c): the negative control — swap the SAME surface key for real
    # fulfillment prose. physical_good (NA on this API-first store) MUST be
    # conjured, proving an added surface CAN move the classification, so the chrome-
    # invariance above is meaningful, not a channel the classifier ignores.
    teeth = _offering.classify_offering(
        _MACHINE_SURFACE, {**captured, _NOISE_SURFACE: _NOISE_TEETH_PROSE}
    )
    _check(
        _full_evidence_map(teeth) != _full_evidence_map(base)
        and "physical_good" in teeth.archetypes,
        f"{_MACHINE_SURFACE}: a signal-BEARING added surface DOES move the profile "
        f"(physical_good conjured: {'physical_good' in teeth.archetypes}) — the "
        "added-surface channel is live, so noise-invariance is non-vacuous",
    )


# ---------------------------------------------------------------------------
# Listing-ORDER invariance — the FIFTH metamorphic axis on the classifier, and
# the FIRST that perturbs the order of items WITHIN a single surface rather than
# the surfaces themselves. The four axes above all operate at surface
# granularity: RELABEL rewrites the host inside a surface, surface-read ORDER
# reverses the sequence surfaces ARRIVE in, SCALE duplicates a surface body,
# NOISE adds a signal-free surface. None reorders the catalog listings a single
# storefront page publishes. This one does: a retail catalog lists its goods in
# SOME order (newest-first, best-selling, alphabetical, a shuffle per request),
# and which listing sits at the top is a merchandising choice, never a readiness
# property. Reordering the priced listings on one page must not change WHICH
# archetype the store is judged to claim, nor the STRENGTH of that claim.
#
# Why this axis has teeth here specifically: `_scan_surface` keeps the FIRST
# match of each signal per surface (`pattern.search`), so the sampled evidence
# QUOTE for `physical_good`'s `priced-listing` leg is anchored on whichever
# priced listing appears first in the page. Reordering the listings therefore
# GENUINELY moves the classifier's sampled exemplar (asserted below: the base
# and reordered priced-listing quotes differ) — the perturbation is real and
# observable, not a no-op the scanner ignores. The metamorphic property under
# test is that this movement of the exemplar changes NOTHING that a readout or
# the battery consumes: the distinct-label STRENGTH, the claimed set, and the NA
# partition are all order-invariant. An honest classifier samples a different
# price to show the reader but reaches the same verdict.
#
# A SYNTHETIC multi-listing catalog is the right vehicle (as for free-trial 115 /
# content-provenance 119 / priced-listing 122's own relabel guard): `strip_html`
# collapses a real fixture's prose to a single whitespace-joined line, so there
# is no per-listing boundary to permute on the committed retail fixture without
# re-segmenting HTML heuristically. The synthetic page seats three DISTINCT
# priced listings (different amounts + currencies) among catalog chrome, each
# also tripping a sibling physical_good leg, so the claim rests on a multi-label
# strength (>1) that a dropped or conjured label would visibly move.
#
# TEETH / non-vacuity, three ways: (a) the reordered catalog string genuinely
# differs from the base; (b) the sampled priced-listing quote differs between the
# two orders (the first-match exemplar really moved); (c) the base claim is a
# real, multi-label physical_good with every rails archetype NA, so a reorder
# that dropped a leg (lower strength) or conjured a rail (metered_api /
# subscription / digital_good out of NA) would be unmistakable. The
# credibility-protecting direction, mirroring the retail-pole scale/noise guards:
# the classified delta between storefront types must come from published
# capability, never from the order a store lists its shelf in.
# ---------------------------------------------------------------------------
_LO_HOST = "market-goods.example"  # a host bearing no archetype-signal word
_LO_CHROME_HEAD = "<header>Marketplace catalog — browse our in-store goods.</header>"
_LO_CHROME_FOOT = "<footer>Cookie notice. Careers. (c) market-goods.</footer>"
# Three distinct priced catalog listings. Each quotes a decimal amount beside an
# in-stock / add-to-cart control (the `priced-listing` form) with a DIFFERENT
# amount + currency, so which one `pattern.search` samples first is observable;
# each also trips a sibling physical_good leg (add-to-cart / fulfillment / free-
# shipping) so the claim rests on a multi-label strength, not a lone signal.
_LO_LISTINGS = [
    "<article><h3>Hardcover novel</h3><p>£51.77 In stock. Add to basket.</p></article>",
    "<article><h3>Ceramic mug</h3><p>$12.99 In stock. Ships from the warehouse.</p></article>",
    "<article><h3>Wool scarf</h3><p>&euro;24.50 In stock. Free shipping applies.</p></article>",
]


def _catalog(order: list[int]) -> str:
    """A synthetic homepage catalog with the listings in the given order."""
    return _LO_CHROME_HEAD + "".join(_LO_LISTINGS[i] for i in order) + _LO_CHROME_FOOT


def _pg_claim(prof):
    """The physical_good claim on a profile, or ``None`` if unclaimed."""
    return next((c for c in prof.claimed if c.archetype == "physical_good"), None)


def test_offering_listing_order_invariance_priced_listing() -> None:
    """Reordering the priced listings on one catalog page does not move the verdict."""
    print("test_offering_listing_order_invariance_priced_listing")

    base_order = [0, 1, 2]
    reordered = [2, 1, 0]  # a genuine permutation whose first listing differs
    base = _offering.classify_offering(_LO_HOST, {"homepage": _catalog(base_order)})
    perm = _offering.classify_offering(_LO_HOST, {"homepage": _catalog(reordered)})

    # The property under test is genuinely present: the synthetic catalog claims
    # physical_good on a MULTI-label strength, with every rails archetype NA — so a
    # dropped leg or a conjured rail would be unmistakable.
    b, p = _pg_claim(base), _pg_claim(perm)
    _check(
        b is not None and b.strength >= 2,
        f"{_LO_HOST}: base claims physical_good on >=2 distinct legs "
        f"(strength {b.strength if b else None}, labels "
        f"{sorted({s.label for s in b.signals}) if b else None})",
    )
    _RAILS = {"metered_api", "subscription", "digital_good"}
    _check(
        _RAILS <= set(base.unclaimed),
        f"{_LO_HOST}: the rails archetypes {sorted(_RAILS)} are all NA at base "
        f"(got unclaimed {sorted(base.unclaimed)}) — the no-rails property a reorder "
        "must not overturn is present",
    )

    # Non-vacuity (a): the reorder is a REAL perturbation — the catalog page bytes
    # genuinely differ, so the classifier reads a different input.
    _check(
        _catalog(base_order) != _catalog(reordered),
        f"{_LO_HOST}: the reordered catalog differs from the base (the perturbation "
        "is real, not a no-op)",
    )
    # Non-vacuity (b): the reorder is OBSERVABLE at THIS signal — `_scan_surface`
    # keeps the FIRST priced listing per surface, so moving a different listing to
    # the top moves the sampled exemplar quote. If the quotes matched, the reorder
    # would be invisible to the scanner and the invariance below vacuous.
    plq = lambda c: next(s.quote for s in c.signals if s.label == "priced-listing")
    _check(
        plq(b) != plq(p),
        f"{_LO_HOST}: the sampled priced-listing quote MOVED under reorder "
        f"(base {plq(b)!r}, reordered {plq(p)!r}) — the first-match exemplar really "
        "changed, so order-invariance of the verdict is non-vacuous",
    )

    # (1) The distinct-label STRENGTH of the physical_good claim is invariant — no
    # leg was lost or gained by reshuffling the shelf.
    _check(
        p is not None and p.strength == b.strength,
        f"{_LO_HOST}: physical_good strength invariant under listing reorder "
        f"(base {b.strength}, reordered {p.strength if p else None})",
    )
    # (2) The SET of physical_good legs is identical — the same evidence fired,
    # only its text position moved.
    _check(
        {s.label for s in p.signals} == {s.label for s in b.signals},
        f"{_LO_HOST}: the set of physical_good legs is invariant under reorder "
        f"(base {sorted({s.label for s in b.signals})}, reordered "
        f"{sorted({s.label for s in p.signals})})",
    )
    # (3) Claimed archetypes IN ORDER invariant — order drives the fixed template-
    # bank task order (cross-site comparability), so a reorder of the shelf must not
    # reorder the battery.
    _check(
        perm.archetypes == base.archetypes,
        f"{_LO_HOST}: claimed archetypes (ordered) invariant under listing reorder "
        f"(base {base.archetypes}, reordered {perm.archetypes})",
    )
    # (4) The rails archetypes stay NA and the whole NA set is invariant — no
    # archetype is conjured by how the catalog is ordered; the credibility-
    # protecting direction of this axis.
    _check(
        _RAILS <= set(perm.unclaimed) and set(perm.unclaimed) == set(base.unclaimed),
        f"{_LO_HOST}: the rails archetypes stay NA and the whole NA set is invariant "
        f"under reorder (base {sorted(base.unclaimed)}, reordered {sorted(perm.unclaimed)})",
    )


# ---------------------------------------------------------------------------
# Listing-order invariance EXTENDED to the with-rails MACHINE surface.
#
# `test_offering_listing_order_invariance_priced_listing` (Cycle 125) pins the
# RETAIL pole of this metamorphic axis: reordering the priced listings on ONE
# catalog page does not move the physical_good verdict. This mirrors it onto the
# WITH-RAILS pole — reordering the ENDPOINTS within ONE OpenAPI machine contract
# must not move the metered_api verdict. The machine surface is where the
# metered_api archetype is most load-bearing: the one committed machine-contract
# storefront (api.replicate.com) earns its metered_api claim from its
# /openapi.json ALONE (pinned by `test_machine_surface_openapi_storefront`), so an
# order dependence here would corrupt the archetype on its home turf.
#
# Mechanism mirror (same substrate as the retail leg): `_scan_surface` keeps the
# FIRST regex match per signal in a surface, so which endpoint leads the spec text
# is OBSERVABLE at `post-endpoint` — moving a different endpoint to the top moves
# the sampled exemplar quote. The invariance is therefore non-vacuous: a real
# perturbation the scanner genuinely sees, which must NOT change the claim.
#
# Vendor-neutral by construction: the host bears no archetype-signal word and the
# endpoints carry only open machine-integration vocabulary (a POST/GET endpoint,
# an Authorization: Bearer credential, a webhook callback, a per-minute rate
# limit) — the same open-convention category the signal bank already anchors on,
# never a vendor.
# ---------------------------------------------------------------------------
_MO_HOST = "gridcell.example"  # a host bearing no archetype-signal word
# Three endpoint blocks for one OpenAPI-style machine contract. Each carries a
# DISTINCT metered_api leg (async webhook / Bearer auth / per-minute rate limit)
# AND its own POST/GET line, so which endpoint leads the spec is observable at the
# `post-endpoint` signal. Together they claim metered_api on a multi-label
# strength with every OTHER archetype NA, so a dropped leg or a conjured non-API
# archetype under reorder would be unmistakable. Pure machine-integration prose —
# no fulfillment / booking / dataset / subscription / generation words — so only
# metered_api fires.
_MO_ENDPOINTS = [
    '{"path":"/v1/predictions","op":"POST https://%s/v1/predictions",'
    '"desc":"Create a prediction, then receive a webhook callback when it completes."}' % _MO_HOST,
    '{"path":"/v1/completions","op":"POST https://%s/v1/completions",'
    '"desc":"Call with Authorization: Bearer <api token> to run the model."}' % _MO_HOST,
    '{"path":"/v1/status","op":"GET https://%s/v1/status",'
    '"desc":"Poll usage; the rate limit is 60 requests per minute per key."}' % _MO_HOST,
]


def _spec(order: list[int]) -> str:
    """A synthetic OpenAPI-style machine contract with its endpoints in ``order``."""
    return (
        '{"openapi":"3.0.0","info":{"title":"Model service API"},"paths":['
        + ",".join(_MO_ENDPOINTS[i] for i in order)
        + "]}"
    )


def _ma_claim(prof):
    """The metered_api claim on a profile, or ``None`` if unclaimed."""
    return next((c for c in prof.claimed if c.archetype == "metered_api"), None)


def test_offering_endpoint_order_invariance_metered_api() -> None:
    """Reordering the endpoints within one OpenAPI spec does not move the verdict."""
    print("test_offering_endpoint_order_invariance_metered_api")

    base_order = [0, 1, 2]
    reordered = [2, 1, 0]  # a genuine permutation whose leading endpoint differs
    base = _offering.classify_offering(_MO_HOST, {"/openapi.json": _spec(base_order)})
    perm = _offering.classify_offering(_MO_HOST, {"/openapi.json": _spec(reordered)})

    # The property under test is genuinely present: the synthetic spec claims
    # metered_api on a MULTI-leg strength with every OTHER archetype NA — so a
    # dropped leg or a conjured non-API archetype under reorder would be unmistakable.
    b, p = _ma_claim(base), _ma_claim(perm)
    _check(
        b is not None and b.strength >= 2,
        f"{_MO_HOST}: base claims metered_api on >=2 distinct legs "
        f"(strength {b.strength if b else None}, labels "
        f"{sorted({s.label for s in b.signals}) if b else None})",
    )
    _OTHERS = {"subscription", "digital_good", "physical_good", "service_booking", "data_retrieval"}
    _check(
        _OTHERS <= set(base.unclaimed),
        f"{_MO_HOST}: every non-API archetype {sorted(_OTHERS)} is NA at base "
        f"(got unclaimed {sorted(base.unclaimed)}) — the single-archetype property a "
        "reorder must not overturn is present",
    )

    # Non-vacuity (a): the reorder is a REAL perturbation — the spec bytes genuinely
    # differ, so the classifier reads a different input.
    _check(
        _spec(base_order) != _spec(reordered),
        f"{_MO_HOST}: the reordered spec differs from the base (the perturbation is "
        "real, not a no-op)",
    )
    # Non-vacuity (b): the reorder is OBSERVABLE at this signal — `_scan_surface`
    # keeps the FIRST `post-endpoint` match per surface, so moving a different
    # endpoint to the top moves the sampled exemplar quote. If the quotes matched,
    # the reorder would be invisible to the scanner and the invariance below vacuous.
    peq = lambda c: next(s.quote for s in c.signals if s.label == "post-endpoint")
    _check(
        peq(b) != peq(p),
        f"{_MO_HOST}: the sampled post-endpoint quote MOVED under reorder "
        f"(base {peq(b)!r}, reordered {peq(p)!r}) — the first-match exemplar really "
        "changed, so order-invariance of the verdict is non-vacuous",
    )

    # (1) The distinct-label STRENGTH of the metered_api claim is invariant — no leg
    # was lost or gained by reshuffling the endpoint list.
    _check(
        p is not None and p.strength == b.strength,
        f"{_MO_HOST}: metered_api strength invariant under endpoint reorder "
        f"(base {b.strength}, reordered {p.strength if p else None})",
    )
    # (2) The SET of metered_api legs is identical — the same evidence fired, only
    # its text position moved.
    _check(
        {s.label for s in p.signals} == {s.label for s in b.signals},
        f"{_MO_HOST}: the set of metered_api legs is invariant under reorder "
        f"(base {sorted({s.label for s in b.signals})}, reordered "
        f"{sorted({s.label for s in p.signals})})",
    )
    # (3) Claimed archetypes IN ORDER invariant — order drives the fixed template-
    # bank task order (cross-site comparability), so a reorder of the spec must not
    # reorder the battery.
    _check(
        perm.archetypes == base.archetypes,
        f"{_MO_HOST}: claimed archetypes (ordered) invariant under endpoint reorder "
        f"(base {base.archetypes}, reordered {perm.archetypes})",
    )
    # (4) Every non-API archetype stays NA and the whole NA set is invariant — no
    # archetype is conjured by how the spec is ordered; the credibility-protecting
    # direction of this axis.
    _check(
        _OTHERS <= set(perm.unclaimed) and set(perm.unclaimed) == set(base.unclaimed),
        f"{_MO_HOST}: the non-API archetypes stay NA and the whole NA set is invariant "
        f"under reorder (base {sorted(base.unclaimed)}, reordered {sorted(perm.unclaimed)})",
    )


# ---------------------------------------------------------------------------
# Relabel-invariance EXTENDED to the retail + non-storefront domains.
#
# The two invariance tests above cover only the canonical PAIR, because their
# non-vacuity mechanism ("the host appears in the classifier's matched evidence
# QUOTE") holds only there — the `metered_api` post-endpoint quote is literally
# `POST https://<host>/…`. The retail storefront's physical_good rests on prose
# anchors ("In stock" / "Add to basket") that carry no host, and the
# non-storefront claims nothing at all, so neither has the host in its evidence
# quotes. That is why the retail-inverse fixture landed WITHOUT a relabel case
# (documented in the [LOCAL] 2026-07-24 capture): a quote-anchored relabel would
# be vacuous there.
#
# But the vendor-neutrality property still MUST hold for them — a book catalog's
# task set (physical_good, everything else NA) and a bare page's honest-empty
# offering must not depend on the domain NAME any more than the pair's does. The
# SCORING-layer relabel guard (`tests/test_canonical_replay.py`) already spans all
# four real domains (org/com/retail/non-storefront); the OFFERING/task-selection
# layer lagged at two. This closes that gap with an honest, domain-appropriate
# non-vacuity: the host really is present in the FETCHED SURFACES the classifier
# reads (the homepage URL/response in the fixture), and the relabel rewrites every
# occurrence, so the classifier's input genuinely changes — the invariance is not
# a no-op. (The identity-keyed special-case is still proven catchable by
# `test_offering_relabel_negative_control` above, which uses the same
# `_discover` / `_discover_relabeled` divergence these tests rely on.)
# ---------------------------------------------------------------------------


def _assert_offering_relabel_general(domain: str, expected_claimed: set) -> None:
    """Relabel-invariance with SURFACE-presence non-vacuity (host not in evidence quote).

    Unlike ``_assert_offering_relabel_invariant`` (which anchors non-vacuity on the
    host appearing inside a matched evidence quote — true only for the API pair),
    this anchors it on the host appearing in the fixture surfaces the classifier
    fetches, then asserts the claimed (ordered) and NA sets are invariant under a
    whole-fixture relabel to a neutral host. Used for domains whose classification
    evidence is host-free (retail prose anchors, or nothing at all).
    """
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    # Non-vacuity: the host is genuinely present in the surfaces the classifier
    # reads, so relabeling rewrites real classifier input (not a no-op). Without
    # this, a host absent from the fixture would make the relabel — and the
    # invariance below — vacuously true.
    _check(
        domain in raw,
        f"{domain}: host present in the fixture surfaces (relabel rewrites real "
        "classifier input — the test is non-vacuous)",
    )

    base, _ = _discover(domain)
    _check(
        set(base.archetypes) == expected_claimed,
        f"{domain}: base claimed == {sorted(expected_claimed)} (got {sorted(base.archetypes)})",
    )

    relab = _discover_relabeled(domain, _NEUTRAL_HOST)
    # Ordered claimed list invariant — order drives the fixed template-bank task
    # order (cross-site comparability), so a reorder would reorder the battery.
    _check(
        relab.archetypes == base.archetypes,
        f"{domain}: claimed archetypes (ordered) invariant under relabel "
        f"(base {base.archetypes}, relabel {relab.archetypes})",
    )
    _check(
        set(relab.archetypes) == expected_claimed,
        f"{domain}: relabeled claimed set == {sorted(expected_claimed)} "
        f"(got {sorted(set(relab.archetypes))})",
    )
    # The NA set (excluded from every mean/spread, never penalized) is invariant —
    # which archetypes the site is judged on vs excused as NA depends on evidence,
    # not identity.
    _check(
        set(relab.unclaimed) == set(base.unclaimed),
        f"{domain}: NA/unclaimed set invariant under relabel "
        f"(base {sorted(base.unclaimed)}, relabel {sorted(relab.unclaimed)})",
    )


# ---------------------------------------------------------------------------
# Text-casing invariance — a metamorphic axis on the classifier's READING layer.
#
# The families above perturb WHICH surfaces the classifier reads or in what order
# (RELABEL rewrites the host, ORDER reverses the read sequence, SCALE duplicates
# the bodies, NOISE adds a signal-free surface). This axis perturbs the CASING of
# the text inside them: uppercase every surface body and assert the classified
# CAPABILITY profile is unchanged. A storefront that writes "Pay-Per-Call",
# "pay-per-call", and "PAY PER CALL" declares the same capability all three ways;
# the score must key on what a site says it can DO, never on its typography.
#
# What is asserted invariant is the case-INDEPENDENT skeleton of the profile —
# claimed archetypes IN RANK ORDER, the NA/unclaimed complement, and per-archetype
# (strength, per-(label, surface) match counts). The quote TEXT is deliberately
# excluded from the comparison: a signal's quote echoes the bytes it matched, so it
# legitimately upper-cases with the surface (and HTML-entity artifacts like
# ``&amp; -> &AMP;`` mean the quote is not expected to differ by case alone). The
# invariant is "the SAME signals fire on the SAME surfaces the SAME number of
# times", not "the captured evidence is byte-identical".
#
# Non-vacuity has two teeth:
#   (a) the transform is REAL — some surface body carries lowercase at base, so
#       uppercasing genuinely changes the bytes the matcher scans;
#   (b) case-insensitivity is LOAD-BEARING — for the fired evidence there exists a
#       signal whose CASE-SENSITIVE match count on its surface differs between the
#       base and uppercased prose (e.g. the ``https?://`` in a POST-endpoint quote,
#       whose case-sensitive form stops matching once the scheme upper-cases), while
#       the real (``re.IGNORECASE``) matcher's count is unchanged. So the invariance
#       rests on the classifier's case-folding, not on the text happening to already
#       be case-uniform. If a future signal is added WITHOUT ``re.IGNORECASE``, its
#       count will move under this transform and the structural assertion fails loudly.
# ---------------------------------------------------------------------------


def _casing_struct(prof) -> dict:
    """archetype -> (strength, sorted ((label, surface), count)) — the case-independent skeleton.

    Excludes the quote text (which echoes the matched bytes and so upper-cases with
    the surface); keeps the per-(label, surface) match MULTIPLICITY so a signal that
    fired N times must still fire N times after the case transform.
    """
    from collections import Counter

    return {
        c.archetype: (
            round(c.strength, 9),
            sorted(Counter((s.label, s.surface) for s in c.signals).items()),
        )
        for c in prof.claimed
    }


def _assert_casing_invariance(domain: str, expected_claimed: set, *, min_claimed: int = 2) -> None:
    """Uppercasing every surface body leaves the classified capability skeleton identical.

    ``min_claimed`` is the number of archetypes the pole is expected to claim. On a
    MULTI-archetype pole (the org/com prose pair, ``min_claimed=2``) the non-vacuity is
    that a casing change could perturb a claim OR reorder the RANK. On a SINGLE-archetype
    pole (the metered_api MACHINE surface, ``min_claimed=1``) there is no rank to reorder,
    so the non-vacuity is that the lone claim rests on real fired evidence whose (strength,
    per-(label, surface) counts) a casing change could perturb — the load-bearing tooth (b)
    below still proves the invariance rests on case-folding, not on case-uniform text.
    """
    surfaces = _captured_surfaces(domain)
    base = _offering.classify_offering(domain, dict(surfaces))

    # The property under test is genuinely present: the domain claims the expected
    # archetype set, RANKED, so a casing change that perturbed a claim or a rank would
    # be observable.
    _check(
        set(base.archetypes) == expected_claimed,
        f"{domain}: base claimed set == {sorted(expected_claimed)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    if min_claimed >= 2:
        _check(
            len(base.claimed) >= 2,
            f"{domain}: >=2 archetypes claimed, so the ranking a casing change could "
            f"reorder is real (got {base.archetypes})",
        )
    else:
        # Single-archetype pole: no rank to reorder, but the lone claim must rest on real
        # fired signals — otherwise the (strength, count) skeleton a casing change could
        # perturb would be empty and the invariance vacuous.
        _check(
            len(base.claimed) == 1 and any(c.signals for c in base.claimed),
            f"{domain}: exactly 1 archetype claimed on real fired evidence, so the "
            f"(strength, per-(label, surface) counts) a casing change could perturb is "
            f"real (got {base.archetypes})",
        )

    up_surfaces = {s: r.upper() for s, r in surfaces.items()}
    # TEETH (a): the transform is REAL — at least one surface carries lowercase at
    # base, so uppercasing genuinely alters the bytes the classifier scans (not a
    # no-op on already-uppercase text).
    _check(
        any(up_surfaces[s] != surfaces[s] for s in surfaces),
        f"{domain}: uppercasing genuinely changed >=1 surface body "
        "(the perturbation is real, not a no-op)",
    )

    # TEETH (b): case-insensitivity is LOAD-BEARING. Among the fired evidence there
    # is a signal whose CASE-SENSITIVE match count on its own surface differs between
    # the base and uppercased prose, while the real IGNORECASE matcher's count is
    # unchanged — so the invariance below rests on the classifier's case-folding, not
    # on the text already being case-uniform.
    load_bearing = None
    for c in base.claimed:
        for s in c.signals:
            pat = _signal_pattern(c.archetype, s.label)
            if pat is None:
                continue
            case_sensitive = re.compile(pat.pattern)  # SAME source, no re.IGNORECASE
            b_prose = _surface_prose(s.surface, surfaces[s.surface])
            u_prose = _surface_prose(s.surface, up_surfaces[s.surface])
            cs_b, cs_u = len(case_sensitive.findall(b_prose)), len(case_sensitive.findall(u_prose))
            ic_b, ic_u = len(pat.findall(b_prose)), len(pat.findall(u_prose))
            if cs_b != cs_u and ic_b == ic_u:
                load_bearing = (c.archetype, s.label, cs_b, cs_u)
                break
        if load_bearing:
            break
    _check(
        load_bearing is not None,
        f"{domain}: a fired signal's CASE-SENSITIVE count moves under uppercasing "
        "while its IGNORECASE count holds — case-folding is load-bearing, so the "
        "invariance is non-vacuous",
    )

    up = _offering.classify_offering(domain, dict(up_surfaces))

    # (1) The case-independent capability skeleton is identical: every archetype's
    # strength AND its per-(label, surface) match counts survive the casing change —
    # no signal lost or conjured, no count drifted, by mere typography.
    _check(
        _casing_struct(up) == _casing_struct(base),
        f"{domain}: per-archetype (strength, per-(label, surface) counts) skeleton "
        "invariant under uppercasing",
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order (cross-site comparability), so casing must not
    # reorder it.
    _check(
        up.archetypes == base.archetypes,
        f"{domain}: claimed archetypes (ranked) invariant under uppercasing "
        f"(base {base.archetypes}, up {up.archetypes})",
    )
    # (3) The NA/unclaimed set (excluded from every mean/spread, never penalized) is
    # invariant — which archetypes a site is judged on vs excused as NA depends on
    # WHAT it declares, not on the case it declares it in.
    _check(
        set(up.unclaimed) == set(base.unclaimed),
        f"{domain}: NA/unclaimed set invariant under uppercasing "
        f"(base {sorted(base.unclaimed)}, up {sorted(up.unclaimed)})",
    )


def test_offering_casing_invariance_org() -> None:
    """A storefront's declared capabilities do not depend on text casing (.org)."""
    print("test_offering_casing_invariance_org")
    _assert_casing_invariance("drift-flight.org", EXPECTED_CLAIMED["drift-flight.org"])


def test_offering_casing_invariance_com() -> None:
    """Casing-invariance mirrored onto the .com half of the canonical pair."""
    print("test_offering_casing_invariance_com")
    _assert_casing_invariance("driftflight.com", EXPECTED_CLAIMED["driftflight.com"])


def test_offering_casing_invariance_machine() -> None:
    """Casing-invariance mirrored onto the metered_api MACHINE pole.

    The org/com casing guards (Cycle 133) cover only the PROSE half of the canonical
    pair — natural-language homepage/llms.txt storefronts. This mirrors the same axis
    onto the qualitatively different MACHINE surface: an API-first storefront classified
    from its ``/openapi.json`` spec (``api.replicate.com``, the fixture behind
    ``test_machine_surface_openapi_storefront``). That surface is scanned RAW (not
    HTML-stripped), and its metered_api evidence is endpoint/scheme prose
    (``POST https://…``) rather than marketing copy — a distinct byte shape for the
    case-folding to hold across. The load-bearing tooth (b) lands naturally here: the
    ``post-endpoint`` signal's ``https?://`` stops matching case-SENSITIVELY once the
    scheme upper-cases (count 1 -> 0), while its ``re.IGNORECASE`` count holds — so the
    invariance rests on the classifier's case-folding, and a future machine-surface
    signal added without ``re.IGNORECASE`` fails loudly. Single-archetype pole, so the
    property is claim + (strength, count) SURVIVAL, not rank stability (``min_claimed=1``).
    """
    print("test_offering_casing_invariance_machine")
    _assert_casing_invariance(_MACHINE_SURFACE, _MACHINE_CLAIMED, min_claimed=1)


# ---------------------------------------------------------------------------
# Casing invariance on the NO-RAILS retail store — the credibility-protecting
# direction of the CASE axis, closing the same org/com/machine-only-vs-retail
# asymmetry the content-scale and noise-surface axes already closed. `_org`/`_com`
# pin the multi-archetype PROSE pole and `_machine` the single-archetype metered_api
# spec pole; this pins the OPPOSITE storefront type — a pure book catalog that claims
# ONLY physical_good with every rails archetype NA. The property it protects is the
# "never manufacture the delta" invariant applied to the CASE axis: shouting a
# no-rails retailer's shelf copy in all-caps must not push its physical_good claim
# up in strength AND must not CONJURE a rails archetype it does not offer. The delta
# between a rails storefront and a no-rails one has to come from real published
# capability, never from the typography a store happens to publish it in.
#
# Two structural differences from `_assert_casing_invariance` force a dedicated test
# rather than a reuse of the shared casing helper:
#   * the retail store is a SINGLE-surface homepage catalog, so the helper's
#     `_captured_surfaces` >=2-surface premise does not hold — the base is captured
#     inline (the same spy pattern the content-scale / noise-surface retail poles use);
#   * the shared helper's tooth (b) requires a fired signal whose CASE-SENSITIVE count
#     MOVES under uppercasing (cs_b != cs_u). The physical_good bank is authored
#     lowercase and matches the mixed-case shelf copy ("Add to basket", "In stock")
#     ONLY through re.IGNORECASE, so every fired signal's case-sensitive count is
#     already 0 at base and stays 0 — a "count moves" tooth is structurally impossible
#     here. The retail-appropriate tooth (b) below is instead the STRONGER "folding is
#     essential" form: a fired signal matches 0x case-sensitively yet Nx with
#     IGNORECASE, so stripping the fold would erase the physical_good claim outright.
# ---------------------------------------------------------------------------


def test_offering_casing_invariance_retail() -> None:
    """Shouting a no-rails catalog in all-caps is not "more" physical_good — and conjures no rails."""
    print("test_offering_casing_invariance_retail")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface premise: the retail fixture is a
    # single-surface homepage catalog, and the case axis uppercases whatever base the
    # store publishes.)
    path = os.path.join(_FIXTURE_DIR, f"{_RETAIL}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_RETAIL, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # physical_good, with every rails archetype NA — so a rails claim conjured by
    # sheer typography would be unmistakably observable.
    _check(
        set(base.archetypes) == _RETAIL_CLAIMED,
        f"{_RETAIL}: base claimed set == {sorted(_RETAIL_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        _RETAIL_MUST_BE_NA <= set(base.unclaimed),
        f"{_RETAIL}: the rails archetypes {sorted(_RETAIL_MUST_BE_NA)} are all NA at "
        f"base (got unclaimed {sorted(base.unclaimed)}) — the no-rails property the "
        "casing must not overturn is present",
    )

    up_surfaces = {s: r.upper() for s, r in captured.items()}
    # TEETH (a): the transform is REAL — the base carries lowercase, so uppercasing
    # genuinely alters the bytes the classifier scans (not a no-op on all-caps text).
    _check(
        any(up_surfaces[s] != captured[s] for s in captured),
        f"{_RETAIL}: uppercasing genuinely changed >=1 surface body "
        "(the perturbation is real, not a no-op)",
    )

    # TEETH (b): case-folding is not merely load-bearing here but ESSENTIAL. The
    # retail catalog's physical_good signals are authored lowercase yet match the
    # mixed-case shelf copy ("Add to basket", "In stock") ONLY through the
    # classifier's re.IGNORECASE — so at base a fired signal matches ZERO times
    # case-SENSITIVELY while firing N>0 times case-insensitively (strip the fold and
    # the physical_good claim vanishes outright), and that IGNORECASE count survives
    # the uppercase transform. This is the retail pole's analogue of the machine
    # surface's count-moves tooth: on the spec a case-sensitive `https://` match is
    # BROKEN by uppercasing (1 -> 0); here no fired signal ever matched
    # case-sensitively to begin with, so a "count moves" tooth is structurally
    # impossible and would be the wrong non-vacuity proof.
    essential = None
    for c in base.claimed:
        for s in c.signals:
            pat = _signal_pattern(c.archetype, s.label)
            if pat is None:
                continue
            case_sensitive = re.compile(pat.pattern)  # SAME source, no re.IGNORECASE
            b_prose = _surface_prose(s.surface, captured[s.surface])
            u_prose = _surface_prose(s.surface, up_surfaces[s.surface])
            cs_b = len(case_sensitive.findall(b_prose))
            ic_b = len(pat.findall(b_prose))
            ic_u = len(pat.findall(u_prose))
            if cs_b == 0 and ic_b > 0 and ic_b == ic_u:
                essential = (c.archetype, s.label, ic_b)
                break
        if essential:
            break
    _check(
        essential is not None,
        f"{_RETAIL}: a fired signal matches 0x case-SENSITIVELY yet Nx with "
        "re.IGNORECASE at base (and that count survives uppercasing) — case-folding "
        "is essential to the physical_good claim, so the invariance is non-vacuous "
        f"(essential signal: {essential})",
    )

    up = _offering.classify_offering(_RETAIL, dict(up_surfaces))

    # (1) The case-independent capability skeleton is identical: physical_good's
    # strength AND its per-(label, surface) match counts survive the casing change —
    # no signal lost or conjured, no count drifted, by mere typography. (The quote
    # text itself upper-cases with the surface, so `_casing_struct` — not
    # `_full_evidence_map` — is the case-independent invariant here.)
    _check(
        _casing_struct(up) == _casing_struct(base),
        f"{_RETAIL}: per-archetype (strength, per-(label, surface) counts) skeleton "
        "invariant under uppercasing",
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — still EXACTLY physical_good.
    # Shouting the catalog conjured no rails claim; the "never manufacture the delta"
    # property on the CASE axis.
    _check(
        up.archetypes == base.archetypes,
        f"{_RETAIL}: claimed archetypes (ranked) invariant under uppercasing "
        f"(base {base.archetypes}, up {up.archetypes})",
    )
    # (3) The rails archetypes stay NA and the whole NA/unclaimed set is invariant —
    # which archetypes a no-rails store is excused as NA depends on WHAT it declares,
    # not on the case it declares it in.
    _check(
        _RETAIL_MUST_BE_NA <= set(up.unclaimed)
        and set(up.unclaimed) == set(base.unclaimed),
        f"{_RETAIL}: the rails archetypes stay NA and the whole NA set is invariant "
        f"under uppercasing (base {sorted(base.unclaimed)}, up {sorted(up.unclaimed)})",
    )


def test_offering_relabel_invariance_retail() -> None:
    """A retail storefront's task set (physical_good, all else NA) is identity-invariant."""
    print("test_offering_relabel_invariance_retail")
    _assert_offering_relabel_general(_RETAIL, _RETAIL_CLAIMED)


def test_offering_relabel_invariance_nonstorefront() -> None:
    """A non-storefront's honest-empty offering is identity-invariant.

    Renaming a bare documentation page must not conjure an offering: the relabeled
    discovery claims NOTHING and every archetype stays NA, exactly as the un-relabeled
    run. The concrete full-NA structure asserted here (all six archetypes unclaimed,
    both before and after) is non-empty and specific — and the retail/pair invariance
    tests in this same suite prove the classifier is NOT a constant all-NA function, so
    this is invariance of a real classification, not a degenerate constant.
    """
    print("test_offering_relabel_invariance_nonstorefront")
    _assert_offering_relabel_general(_NONSTOREFRONT, set())
    # The full-NA partition is invariant too (renaming invents no offering).
    relab = _discover_relabeled(_NONSTOREFRONT, _NEUTRAL_HOST)
    _check(
        set(relab.unclaimed) == set(ARCHETYPES),
        f"{_NONSTOREFRONT}: every archetype stays NA under relabel "
        f"(got {sorted(relab.unclaimed)}, want {sorted(ARCHETYPES)}) — renaming a "
        "bare page invents no offering",
    )


# ---------------------------------------------------------------------------
# Cross-signal precision-ISOLATION matrix (METHOD, Cycle 137).
#
# Every relabel/precision guard above pins ONE signal against its OWN
# false-positive minefield. This matrix pins the COMPLEMENTARY property across
# the WHOLE signal bank at once: each signal's affirmative evidence must claim
# EXACTLY its own archetype and leak into NO OTHER — no signal poaches a sibling
# archetype's turf.
#
# Why cross-ARCHETYPE (not cross-signal within an archetype): a within-archetype
# co-fire only DEEPENS the same claim (e.g. "pay-per-call" trips both `pay-per`
# and `per-unit-rate`, both metered_api — harmless, strength is distinct-label
# count). The SCORE-RELEVANT harm is a signal firing on a DIFFERENT archetype's
# evidence, which CONJURES a false archetype claim — the site then gets probed
# with an intent it never offered, polluting the completion means (the exact
# battery-mismatch the offering-relative directive removes). This guard makes
# that failure mode a per-cycle tripwire: broaden any regex until it starts
# matching a sibling archetype's vocabulary and it fails loudly here.
#
# One minimal affirmative snippet per signal, drawn from that signal's OWN
# vendor-neutral vocabulary. COMPLETENESS is asserted (below): the map must cover
# exactly the live signal bank, so a newly added signal cannot escape the matrix.
_ISOLATION_EVIDENCE: dict[str, str] = {
    # metered_api
    "post-endpoint": "POST https://api.example.com/v1/generate",
    "qualified-api": "a REST API for developers",
    "api-reference": "see the API reference for details",
    "api-auth": "send the Authorization: Bearer token header",
    "pay-as-you-go": "simple pay-as-you-go billing",
    "pay-per": "you are billed pay-per-call",
    "billed-per": "you are billed per invocation",
    "per-unit-rate": "priced per token consumed",
    "usage-based": "usage-based overage applies",
    "rate-limited": "the endpoint is rate-limited to protect capacity",
    "concurrency-limit": "a concurrency limit of four applies",
    "async-job": "poll for the outcome until it is ready",
    "webhook-verification": (
        "verify that webhook requests are authentic with the "
        "webhook-signature header"
    ),
    "streaming-response": "responses arrive as server-sent events",
    "error-contract": "on failure the body is application/problem+json",
    "test-mode": "try calls safely in sandbox mode first",
    "pagination": "walk results with cursor-based pagination",
    "cancel-job": "you can cancel a running prediction at any time",
    "self-provisioning": "an agent can provision its own identity, no sign-up",
    "key-rotation": "rotate your api key from the dashboard",
    "credit-metered": "each call spends credits remaining in your balance",
    "tiered-volume": "committed-use volume discounts apply",
    "x402": "the endpoint answers with HTTP 402",
    "agent-payment-rail": "settle via x402 (usdc) on the base network",
    "payment-challenge-retry": "settle the payment challenge and retry with the proof attached",
    "payment-receipt": "log the receipt header for your spend records",
    "failure-not-billed": "if the request failed you are not charged",
    "reserve-and-settle": "you reserve the ceiling up front and are charged only actual",
    "free-included-usage": "included units are free per account",
    # subscription
    "subscription": "start a subscription today",
    "per-month-price": "$29 per month",
    "per-month": "billed monthly",
    "recurring": "a recurring plan",
    "annual-billing": "your billing cycle renews",
    "seat-licensing": "$10 per seat per month",
    "free-trial": "start a free trial",
    "plan-purchase": "purchasable plans carry a purchase object",
    "plan-allowance": "your plan's monthly allowance resets each cycle",
    # digital_good
    "generation": "image generation for creators",
    "generate-media": "generate an image from a prompt",
    "generations": "your recent generations",
    "render": "download the finished render",
    "translation": "translate the passage",
    "hosted-output": "we return hosted output URLs",
    "output-license": "you own the output you make",
    "content-provenance": "each asset carries content credentials",
    "output-resolution": "the maximum output resolution is 4096px",
    "output-retention": "renders remain available for 90 days",
    "variant-selection": "choose a style preset for your render",
    # physical_good
    "free-shipping": "enjoy free shipping",
    "shipping-noun": "choose a shipping method",
    "add-to-cart": "add to cart",
    "stock": "in stock now",
    "priced-listing": "24.99 in stock",
    "fulfillment": "ships from our warehouse",
    "sku-inventory": "manage inventory levels",
    "returns": "see our return policy",
    "order-tracking": "track your order after checkout",
    "physical-descriptor": "a physical product",
    # service_booking
    "book": "book a session online",
    "appointment": "schedule appointments",
    "reservation": "make a reservation",
    "schedule": "schedule your visit",
    "availability": "check availability",
    "manage-booking": "reschedule or cancel your appointment",
    "booking-notification": "an appointment reminder is sent automatically",
    "intake-form": "fill out the intake form",
    # data_retrieval
    "enrich": "we enrich your records",
    "dataset": "download the dataset",
    "lookup": "a phone lookup service",
    "data-service": "a data feed for analysts",
    "query-records": "query records in bulk",
    "batch-retrieval": "bulk enrichment of your records",
}


def _signal_archetype() -> dict[str, str]:
    """label -> archetype, over the live signal bank."""
    return {
        name: arch
        for arch, sigs in _offering._SIGNALS.items()
        for name, _ in sigs
    }


def test_cross_signal_archetype_isolation() -> None:
    """No metered_api/subscription/... signal poaches a DIFFERENT archetype's turf.

    For every signal in the live bank, its curated affirmative snippet is scored
    through the REAL ``classify_offering`` path (a passthrough ``/llms.txt``
    surface, so no HTML-stripping intervenes) and must:
      (a) claim EXACTLY its own archetype — leaking into no other (the
          cross-archetype isolation property that protects the claimed SET), and
      (b) fire its OWN signal label — so the snippet genuinely exercises THIS
          signal, not merely lands on the right archetype via some sibling
          (non-vacuity: an affirmative that fired the wrong label would pass a
          set-only check while proving nothing about the named signal).

    COMPLETENESS is enforced: the evidence map must cover exactly the live signal
    bank, so a future COVERAGE cycle that adds a signal cannot silently escape the
    isolation matrix. The companion negative-control test proves the check has
    teeth (a deliberately poaching snippet claims two archetypes and would fail
    (a)), so this is isolation of a real, discriminating classifier — not a
    degenerate always-one-archetype function.
    """
    print("test_cross_signal_archetype_isolation")
    sig_arch = _signal_archetype()

    # COMPLETENESS — the map covers exactly the live bank (no new signal escapes).
    _check(
        set(_ISOLATION_EVIDENCE) == set(sig_arch),
        "isolation evidence covers exactly the live signal bank "
        f"(missing {sorted(set(sig_arch) - set(_ISOLATION_EVIDENCE))}, "
        f"extra {sorted(set(_ISOLATION_EVIDENCE) - set(sig_arch))})",
    )

    cross_leaks: list[str] = []
    vacuous: list[str] = []
    for label, arch in sig_arch.items():
        snippet = _ISOLATION_EVIDENCE[label]
        prof = classify_offering("iso.example", {"/llms.txt": snippet})
        claimed = set(prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == arch
            for s in c.signals
        }
        if claimed != {arch}:
            cross_leaks.append(f"{arch}/{label}: claimed {sorted(claimed)}")
        if label not in fired:
            vacuous.append(f"{arch}/{label}: fired {sorted(fired)}")

    _check(
        not cross_leaks,
        "every signal's evidence claims ONLY its own archetype — no "
        f"cross-archetype poaching (leaks: {cross_leaks})",
    )
    _check(
        not vacuous,
        "every signal's evidence fires its OWN label (non-vacuous affirmative) "
        f"(misses: {vacuous})",
    )
    _check(
        len(_ISOLATION_EVIDENCE) == len(sig_arch) >= 55,
        f"full bank exercised ({len(sig_arch)} signals across "
        f"{len(set(sig_arch.values()))} archetypes)",
    )


def test_cross_signal_isolation_negative_control() -> None:
    """TEETH: a deliberately cross-archetype-poaching surface claims MORE than one.

    If the isolation check could never fail, it would prove nothing. A surface
    that mixes a physical_good phrase ("add to cart") with a metered_api one
    ("billed per token") must classify to BOTH archetypes — so the isolation
    assertion (claimed == a single archetype) genuinely discriminates, and a real
    regex that started matching a sibling archetype's words would be caught.
    """
    print("test_cross_signal_isolation_negative_control")
    prof = classify_offering("neg.example", {"/llms.txt": "add to cart, then billed per token"})
    claimed = set(prof.archetypes)
    _check(
        {"physical_good", "metered_api"} <= claimed,
        "a mixed-archetype surface claims BOTH physical_good and metered_api "
        f"(got {sorted(claimed)}) — the isolation check has teeth",
    )
    _check(
        len(claimed) >= 2,
        f"the poaching surface trips >1 archetype ({sorted(claimed)}), so "
        "single-archetype isolation is a falsifiable property",
    )


# ---------------------------------------------------------------------------
# Surface-DEDUP invariance — a genuinely NEW perturbation axis on the offering
# path, the last unused in-cloud METHOD sibling of the invariance family (host
# RELABEL / surface-read ORDER / content SCALE / NOISE surface / listing &
# endpoint ORDER / CASE fold). It is distinct from content-SCALE, its closest
# relative: content-scale grows every surface BODY K-fold within a FIXED surface
# SET (raw hits multiply INSIDE one surface); this adds a whole DUPLICATE SURFACE
# under a DISTINCT key (the SAME signal-bearing body served a second time from a
# second location). That is not a synthetic contortion — it is exactly what the
# LIVE discovery path already produces: `discover_offering` reads each
# `_SURFACE_DOCS` path on the apex host AND on the `agents.`/`docs.`/`developers.`/
# `api.` doc subdomains (`_doc_subdomain_surfaces`), so a storefront that mirrors
# its `llms.txt` / OpenAPI spec / `/pricing` on `agents.<host>` (as the canonical
# driftflight.com does) hands the classifier the SAME body under two distinct
# host-qualified surface keys. A CDN mirror, an `/openapi.json` also served at
# `/swagger.json`, or an `llms.txt` duplicated as `llms-full.txt` are the same
# shape. None of that should make a site "more" of any archetype.
#
# WHY this is a robustness PIN, not a bug-find: a duplicate surface has a DISTINCT
# key, so `classify_offering` ADDS it (a dict never overwrites a new key) and
# `_scan_surface` stamps its signals with the mirror surface — so the per-claim
# `signals` LIST genuinely GROWS (the same labels fire again on the mirror). The
# ranking quantity survives because `ArchetypeClaim.strength` counts DISTINCT
# signal LABELS (`len({s.label for s in self.signals})`), not raw list length —
# its docstring names exactly this "does not out-rank" rationale. This guard turns
# that rationale into an executable tripwire for the DEDUP axis on REAL canonical
# evidence: mirroring every doc surface must leave the strength of every archetype,
# the RANKED claimed list (which drives the fixed template-bank task order for
# cross-site comparability), and the NA complement byte-identical.
#
# TEETH / non-vacuity: the mirror really reaches the classifier (`surfaces_seen`
# grows by exactly the mirror keys), and the top-ranked claim's raw `len(signals)`
# STRICTLY INCREASES under the mirror — so a count-based reader (a regression that
# defined `strength = len(self.signals)`, letting a mirrored surface reorder the
# ranking) WOULD see a difference and could flip the task order, yet the
# distinct-label `strength` and the rank below do not move. Mirrored onto BOTH
# canonical pair-halves from the start, so this axis does not inherit the .com-only
# asymmetry surface-read-order had to close later. The homepage is deliberately NOT
# mirrored: `_doc_subdomain_surfaces` mirrors only `_SURFACE_DOCS` (never the apex
# homepage), and a non-"homepage"-keyed HTML body is stripped only via
# `_is_html_document`, so restricting the mirror to the doc surfaces keeps each
# duplicate's scan byte-faithful to its original AND models the real mechanism.
# ---------------------------------------------------------------------------
_MIRROR_PREFIX = "mirror::"  # a sentinel key prefix; never collides with a real surface


def _mirror_doc_surfaces(surfaces: dict) -> dict:
    """``{mirror-key: original-key}`` for every doc surface (homepage excluded).

    Each doc surface (everything the discovery path reads beyond the apex homepage)
    gets a duplicate under a distinct ``mirror::`` key carrying the SAME body — the
    apex+subdomain / CDN / spec-alias mirror the live discovery path already yields.
    """
    return {f"{_MIRROR_PREFIX}{s}": s for s in surfaces if s != "homepage"}


def _assert_surface_dedup_invariance(domain: str, expected_claimed: set) -> None:
    """Serving the same doc surface a second time changes no archetype claim."""
    surfaces = _captured_surfaces(domain)
    base = _offering.classify_offering(domain, dict(surfaces))

    # The property under test is genuinely present: the domain claims the expected
    # multi-archetype set, RANKED, so a count-driven reorder would be observable.
    _check(
        set(base.archetypes) == expected_claimed,
        f"{domain}: base claimed set == {sorted(expected_claimed)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        len(base.claimed) >= 2,
        f"{domain}: >=2 archetypes claimed, so the ranking a dedup regression could "
        f"reorder is real (got {base.archetypes})",
    )

    mirror_keys = _mirror_doc_surfaces(surfaces)
    _check(
        bool(mirror_keys),
        f"{domain}: >=1 doc surface exists to mirror (got surfaces {list(surfaces)})",
    )
    mirrored = dict(surfaces)
    for mk, src in mirror_keys.items():
        _check(mk not in mirrored, f"{domain}: mirror key {mk!r} is new, not an overwrite")
        mirrored[mk] = surfaces[src]  # byte-identical duplicate under a distinct key
    # Non-vacuity: the mirror genuinely enlarged the surface MAP the classifier reads.
    _check(
        len(mirrored) == len(surfaces) + len(mirror_keys),
        f"{domain}: the surface map grew by exactly the mirror keys "
        f"({len(surfaces)} -> {len(mirrored)}) — the perturbation is real",
    )

    dup = _offering.classify_offering(domain, mirrored)

    # The mirror really reached classification: surfaces_seen grew by exactly the
    # mirror keys and nothing else (each duplicate carried non-empty prose, so it
    # was read — not silently dropped, which would make the invariance vacuous).
    _check(
        set(dup.surfaces_seen) == set(base.surfaces_seen) | set(mirror_keys),
        f"{domain}: surfaces_seen grew by exactly the mirror keys "
        f"(base {sorted(base.surfaces_seen)}, dup {sorted(dup.surfaces_seen)})",
    )

    # TEETH: the top-ranked claim's raw signal-LIST length STRICTLY INCREASES under
    # the mirror (its labels fired again on the mirror surfaces), so a count-based
    # `strength = len(self.signals)` reader WOULD see more and could reorder the
    # ranking — yet the distinct-label strength and the rank below do not move. This
    # is why the invariance is a real property of the classifier, not a no-op.
    def _sig_count(prof, arch: str) -> int:
        return len(next(c for c in prof.claimed if c.archetype == arch).signals)

    mirror_src = set(mirror_keys.values())
    top = base.claimed[0]
    top_mirrorable = sum(1 for s in top.signals if s.surface in mirror_src)
    _check(
        top_mirrorable >= 1,
        f"{domain}: the top-ranked claim ({top.archetype}) has >=1 signal on a "
        f"mirrored doc surface (got {top_mirrorable}) — the count teeth are real",
    )
    _check(
        _sig_count(dup, top.archetype) > _sig_count(base, top.archetype),
        f"{domain}: the top claim ({top.archetype}) fires MORE raw signals under the "
        f"mirror ({_sig_count(base, top.archetype)} -> {_sig_count(dup, top.archetype)}) "
        "— a count-based strength reader would differ",
    )

    # (1) Per-archetype STRENGTH (distinct-label count — the ranking quantity) is
    # byte-identical: a duplicate surface adds no distinct label, so no claim gets
    # stronger and none can leapfrog another in the rank.
    base_strength = {c.archetype: c.strength for c in base.claimed}
    dup_strength = {c.archetype: c.strength for c in dup.claimed}
    _check(
        dup_strength == base_strength,
        f"{domain}: per-archetype strength invariant under surface dedup "
        f"(base {base_strength}, dup {dup_strength})",
    )
    # (2) The distinct-label SET per archetype (the substrate strength counts) is
    # identical — the mirror re-fired the SAME labels, conjured no new one.
    base_labels = {c.archetype: {s.label for s in c.signals} for c in base.claimed}
    dup_labels = {c.archetype: {s.label for s in c.signals} for c in dup.claimed}
    _check(
        dup_labels == base_labels,
        f"{domain}: per-archetype distinct-label set invariant under surface dedup",
    )
    # (3) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order (cross-site comparability), so a mirrored surface must
    # not reorder it.
    _check(
        dup.archetypes == base.archetypes,
        f"{domain}: claimed archetypes (ranked) invariant under surface dedup "
        f"(base {base.archetypes}, dup {dup.archetypes})",
    )
    # (4) The NA/unclaimed set (excluded from every mean/spread, never penalized) is
    # invariant — which archetypes a site is judged on vs excused as NA is a property
    # of WHAT it claims, not how many places it says it.
    _check(
        set(dup.unclaimed) == set(base.unclaimed),
        f"{domain}: NA/unclaimed set invariant under surface dedup "
        f"(base {sorted(base.unclaimed)}, dup {sorted(dup.unclaimed)})",
    )


def test_offering_surface_dedup_invariance_org() -> None:
    """A doc surface served twice is not "more" of any archetype (.org)."""
    print("test_offering_surface_dedup_invariance_org")
    _assert_surface_dedup_invariance("drift-flight.org", EXPECTED_CLAIMED["drift-flight.org"])


def test_offering_surface_dedup_invariance_com() -> None:
    """Surface-dedup invariance mirrored onto the .com half of the canonical pair."""
    print("test_offering_surface_dedup_invariance_com")
    _assert_surface_dedup_invariance("driftflight.com", EXPECTED_CLAIMED["driftflight.com"])


# ---------------------------------------------------------------------------
# Surface-dedup invariance on the MACHINE (API-first) pole — closing the same
# org/com-only-vs-machine asymmetry the casing axis already closed (Cycle 155),
# now for the DEDUP axis. `_org`/`_com` pin the multi-archetype PROSE pole; this
# pins the single-archetype metered_api OpenAPI-spec pole (`api.replicate.com`,
# which claims ONLY metered_api off its `/openapi.json` doc surface). This is the
# NATIVE home of the dedup mechanism, not a contortion: the live discovery path
# mirrors every `_SURFACE_DOCS` path across apex + `api.`/`docs.` host-qualified
# keys, and an `/openapi.json` re-served at `/swagger.json` or behind a CDN hands
# the classifier the SAME spec body under two distinct keys — exactly what an
# API-first storefront produces. The property it protects is the "never manufacture
# the delta" invariant on the DEDUP axis, from the metered pole: re-serving a spec
# must not push metered_api up in strength AND must not CONJURE a rails archetype
# (subscription / physical_good / ...) the API does not offer. A storefront is not
# "more" metered — nor suddenly a shop — because its one spec is mirrored twice.
#
# Two structural differences from `_assert_surface_dedup_invariance` force a
# dedicated test rather than a reuse of the shared dedup helper:
#   * the shared helper's non-vacuity rests on `len(base.claimed) >= 2` so a
#     count-driven RANK REORDER is observable; the machine pole claims exactly ONE
#     archetype, so "reorder" is structurally impossible and would be the wrong
#     non-vacuity proof. The single-claim analogue below is stronger in the
#     credibility direction: the teeth are (a) the raw signal count of the one claim
#     STRICTLY INCREASES under the mirror (a count-based reader would differ), and
#     (b) the five sibling archetypes stay NA — no rail is conjured by duplication;
#   * `_captured_surfaces` requires `>=2` READ surfaces for a reorder to matter; the
#     machine pole reads exactly {homepage, /openapi.json}, so the base is captured
#     inline (the same spy pattern the casing/content-scale machine poles use) and
#     the single doc surface is the one that gets mirrored.
# ---------------------------------------------------------------------------


def test_offering_surface_dedup_invariance_machine() -> None:
    """Mirroring an API-first store's one spec is not "more" metered_api — and conjures no rails."""
    print("test_offering_surface_dedup_invariance_machine")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface reorder premise: the machine pole
    # reads {homepage, /openapi.json} and the dedup axis mirrors the doc surface.)
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_MACHINE_SURFACE, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # metered_api, with every other archetype NA — so a rails claim conjured by a
    # mere duplicate surface, or a strengthened metered_api, would be observable.
    _check(
        set(base.archetypes) == _MACHINE_CLAIMED,
        f"{_MACHINE_SURFACE}: base claimed set == {sorted(_MACHINE_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    machine_must_be_na = set(_offering.ARCHETYPES) - _MACHINE_CLAIMED
    _check(
        machine_must_be_na <= set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes {sorted(machine_must_be_na)} are "
        f"all NA at base (got unclaimed {sorted(base.unclaimed)}) — the single-claim "
        "property the dedup must not overturn is present",
    )

    mirror_keys = _mirror_doc_surfaces(captured)
    _check(
        bool(mirror_keys),
        f"{_MACHINE_SURFACE}: >=1 doc surface exists to mirror (got surfaces {list(captured)})",
    )
    mirrored = dict(captured)
    for mk, src in mirror_keys.items():
        _check(mk not in mirrored, f"{_MACHINE_SURFACE}: mirror key {mk!r} is new, not an overwrite")
        mirrored[mk] = captured[src]  # byte-identical duplicate under a distinct key
    # Non-vacuity: the mirror genuinely enlarged the surface MAP the classifier reads.
    _check(
        len(mirrored) == len(captured) + len(mirror_keys),
        f"{_MACHINE_SURFACE}: the surface map grew by exactly the mirror keys "
        f"({len(captured)} -> {len(mirrored)}) — the perturbation is real",
    )

    dup = _offering.classify_offering(_MACHINE_SURFACE, mirrored)

    # The mirror really reached classification: surfaces_seen grew by exactly the
    # mirror keys and nothing else (the duplicate carried non-empty spec prose, so it
    # was read — not silently dropped, which would make the invariance vacuous).
    _check(
        set(dup.surfaces_seen) == set(base.surfaces_seen) | set(mirror_keys),
        f"{_MACHINE_SURFACE}: surfaces_seen grew by exactly the mirror keys "
        f"(base {sorted(base.surfaces_seen)}, dup {sorted(dup.surfaces_seen)})",
    )

    def _sig_count(prof, arch: str) -> int:
        return len(next(c for c in prof.claimed if c.archetype == arch).signals)

    # TEETH (a): the one claim's raw signal-LIST length STRICTLY INCREASES under the
    # mirror (its labels fired again on the duplicate spec), so a count-based
    # `strength = len(self.signals)` reader WOULD see more metered_api — yet the
    # distinct-label strength below does not move. This is the single-claim pole's
    # analogue of the multi-archetype rank tooth: no rank to flip, but the same
    # count-inflation a naive reader would mistake for a stronger claim.
    top = base.claimed[0]
    mirror_src = set(mirror_keys.values())
    top_mirrorable = sum(1 for s in top.signals if s.surface in mirror_src)
    _check(
        top_mirrorable >= 1,
        f"{_MACHINE_SURFACE}: the metered_api claim has >=1 signal on a mirrored doc "
        f"surface (got {top_mirrorable}) — the count teeth are real",
    )
    _check(
        _sig_count(dup, "metered_api") > _sig_count(base, "metered_api"),
        f"{_MACHINE_SURFACE}: metered_api fires MORE raw signals under the mirror "
        f"({_sig_count(base, 'metered_api')} -> {_sig_count(dup, 'metered_api')}) — a "
        "count-based strength reader would differ",
    )

    # (1) Per-archetype STRENGTH (distinct-label count — the ranking quantity) is
    # byte-identical: a duplicate spec adds no distinct label, so metered_api gets no
    # stronger by mere duplication.
    base_strength = {c.archetype: c.strength for c in base.claimed}
    dup_strength = {c.archetype: c.strength for c in dup.claimed}
    _check(
        dup_strength == base_strength,
        f"{_MACHINE_SURFACE}: per-archetype strength invariant under surface dedup "
        f"(base {base_strength}, dup {dup_strength})",
    )
    # (2) The distinct-label SET per archetype is identical — the mirror re-fired the
    # SAME labels, conjured no new one.
    base_labels = {c.archetype: {s.label for s in c.signals} for c in base.claimed}
    dup_labels = {c.archetype: {s.label for s in c.signals} for c in dup.claimed}
    _check(
        dup_labels == base_labels,
        f"{_MACHINE_SURFACE}: per-archetype distinct-label set invariant under surface dedup",
    )
    # (3) Claimed archetypes IN RANK ORDER invariant — still EXACTLY metered_api.
    # Duplicating the spec conjured no rail; the "never manufacture the delta"
    # property on the DEDUP axis, from the single-archetype metered pole.
    _check(
        dup.archetypes == base.archetypes,
        f"{_MACHINE_SURFACE}: claimed archetypes (ranked) invariant under surface dedup "
        f"(base {base.archetypes}, dup {dup.archetypes})",
    )
    # (4) The non-metered archetypes stay NA and the whole NA/unclaimed set is
    # invariant — which archetypes an API-first store is excused as NA depends on WHAT
    # it declares, not how many times its one spec is served.
    _check(
        machine_must_be_na <= set(dup.unclaimed)
        and set(dup.unclaimed) == set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes stay NA and the whole NA set is "
        f"invariant under surface dedup (base {sorted(base.unclaimed)}, dup {sorted(dup.unclaimed)})",
    )


# ---------------------------------------------------------------------------
# Whitespace invariance on the MACHINE (API-first) pole — a SECOND reading-layer
# metamorphic axis, the natural sibling of the CASE axis (Cycle 133/155). Casing
# perturbs the CASE of the bytes the matcher scans; this perturbs the WHITESPACE
# between them: expand every inter-token space and assert the classified
# capability profile is unchanged. A storefront that writes "POST https://…" with
# one space, two, or a line-break declares the same endpoint all three ways; the
# score must key on what a spec says the API can DO, never on how its author
# happened to lay the bytes out.
#
# This axis lands ONLY on the machine pole, and that scope is the science, not a
# shortcut. On the PROSE poles (org/com/retail) every surface is HTML and runs
# through `strip_html`, which COLLAPSES whitespace runs to single spaces BEFORE
# the matcher sees them (verified: `strip_html('pay   per     call')` inside markup
# -> 'pay per call'); a whitespace perturbation there is normalized away by the
# reader, so the invariance would hold VACUOUSLY — enforced by strip_html, not by
# the signal patterns. The `/openapi.json` spec is scanned RAW (not HTML-stripped,
# per `_surface_prose`), so on the machine pole whitespace-tolerance rests on the
# signal patterns' OWN `\s+`/`\s*` flexibility — the load-bearing mechanism this
# guard actually pins. That is why the metered_api spec pole is the native (and
# only non-vacuous) home for the whitespace axis.
#
# The transform is EXPANSION (each single space -> three), which is monotone in the
# credibility-safe direction: a `\s+`/`\s*` matcher still matches the longer run,
# while a pattern that required an EXACT single space can only STOP matching — it can
# never CONJURE a new match. So skeleton-invariance under expansion is a strong
# statement: every fired signal on the machine pole is genuinely whitespace-robust,
# and none silently leans on an exact single space (which a reformat / minifier /
# pretty-printer would break in the wild).
#
# What is asserted invariant is the quote-EXCLUDED skeleton (`_casing_struct`, shared
# with the case axis): archetypes in rank order, the NA complement, and per-(label,
# surface) match multiplicity. The quote TEXT is excluded for the SAME reason as in
# the case axis — a signal's quote echoes a fixed byte WINDOW around its match, so it
# legitimately shifts when whitespace changes the byte offsets; "the same signals fire
# on the same surfaces the same number of times" is the invariant, not byte-identical
# evidence.
#
# Non-vacuity has two teeth:
#   (a) the transform is REAL — the raw spec carries single spaces, so expanding them
#       genuinely changes the bytes the classifier scans;
#   (b) whitespace-tolerance is LOAD-BEARING — among the fired evidence there is a
#       signal whose RIGID-whitespace count (its pattern with every `\s+`/`\s*` rewritten
#       to a single literal space) DROPS under expansion, while the real (flexible)
#       matcher's count holds. The canonical example is `post-endpoint`
#       (`\b(POST|GET|PUT)\s+https?://\S+`): the space in "POST https://" expands to
#       three, the rigid literal-space form stops matching (count 1 -> 0) while `\s+`
#       holds (1 -> 1). So the invariance rests on the patterns' whitespace-flexibility,
#       and a future machine-surface signal written with an exact space would move its
#       count under this transform and fail loudly.
# ---------------------------------------------------------------------------
_WS_RIGID_RE = re.compile(r"\\s[+*]")


def _expand_whitespace(text: str) -> str:
    """Expand every single space into three (monotone: can only DROP literal-space matches)."""
    return text.replace(" ", "   ")


def test_offering_whitespace_invariance_machine() -> None:
    """Reformatting an API-first store's spec whitespace is not "more" metered_api — and conjures no rails."""
    print("test_offering_whitespace_invariance_machine")

    # Capture the base surfaces exactly as discovery feeds them to the classifier.
    # (Unlike `_captured_surfaces`, no >=2-surface reorder premise: the machine pole
    # reads {homepage, /openapi.json} and the whitespace axis reflows the spec body.)
    path = os.path.join(_FIXTURE_DIR, f"{_MACHINE_SURFACE}.json")
    ctx = FetchContext.from_fixture(path)
    captured: dict = {}
    real = _offering.classify_offering

    def _spy(dom, surfaces):
        captured.clear()
        captured.update(surfaces)
        return real(dom, surfaces)

    _offering.classify_offering = _spy
    try:
        _offering.discover_offering(ctx)
    finally:
        _offering.classify_offering = real

    base = _offering.classify_offering(_MACHINE_SURFACE, dict(captured))

    # The property under test is genuinely present: the store claims EXACTLY
    # metered_api on real fired evidence, with every other archetype NA — so a rails
    # claim conjured by a reflow, or a strengthened/weakened metered_api, would be
    # observable.
    _check(
        set(base.archetypes) == _MACHINE_CLAIMED,
        f"{_MACHINE_SURFACE}: base claimed set == {sorted(_MACHINE_CLAIMED)} "
        f"(got {sorted(set(base.archetypes))})",
    )
    _check(
        len(base.claimed) == 1 and any(c.signals for c in base.claimed),
        f"{_MACHINE_SURFACE}: exactly 1 archetype claimed on real fired evidence, so the "
        f"(strength, per-(label, surface) counts) skeleton a reflow could perturb is real "
        f"(got {base.archetypes})",
    )
    machine_must_be_na = set(_offering.ARCHETYPES) - _MACHINE_CLAIMED
    _check(
        machine_must_be_na <= set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes {sorted(machine_must_be_na)} are "
        f"all NA at base (got unclaimed {sorted(base.unclaimed)}) — the single-claim "
        "property the reflow must not overturn is present",
    )

    ws_surfaces = {s: _expand_whitespace(r) for s, r in captured.items()}
    # TEETH (a): the transform is REAL — at least one surface carries single spaces at
    # base, so expanding them genuinely alters the bytes the classifier scans (not a
    # no-op on already-space-free text).
    _check(
        any(ws_surfaces[s] != captured[s] for s in captured),
        f"{_MACHINE_SURFACE}: whitespace expansion genuinely changed >=1 surface body "
        "(the perturbation is real, not a no-op)",
    )

    # TEETH (b): whitespace-tolerance is LOAD-BEARING. Among the fired evidence there is
    # a signal whose RIGID-whitespace count (its pattern with every `\s+`/`\s*` rewritten
    # to a single literal space) DROPS under expansion, while the real flexible matcher's
    # count holds — so the invariance below rests on the patterns' `\s+`/`\s*` flexibility,
    # not on the spec happening to be single-spaced everywhere its signals match.
    load_bearing = None
    for c in base.claimed:
        for s in c.signals:
            pat = _signal_pattern(c.archetype, s.label)
            if pat is None:
                continue
            rigid_src = _WS_RIGID_RE.sub(" ", pat.pattern)  # \s+/\s* -> one literal space
            if rigid_src == pat.pattern:
                continue  # no flexible-whitespace token to make rigid — cannot be the tooth
            try:
                rigid = re.compile(rigid_src, re.IGNORECASE)
            except re.error:
                continue
            b_prose = _surface_prose(s.surface, captured[s.surface])
            w_prose = _surface_prose(s.surface, ws_surfaces[s.surface])
            rig_b, rig_w = len(rigid.findall(b_prose)), len(rigid.findall(w_prose))
            flex_b, flex_w = len(pat.findall(b_prose)), len(pat.findall(w_prose))
            if rig_b > rig_w and flex_b == flex_w:
                load_bearing = (c.archetype, s.label, rig_b, rig_w)
                break
        if load_bearing:
            break
    _check(
        load_bearing is not None,
        f"{_MACHINE_SURFACE}: a fired signal's RIGID-whitespace count DROPS under expansion "
        "while its flexible count holds — whitespace-flexibility is load-bearing, so the "
        "invariance is non-vacuous",
    )

    ws = _offering.classify_offering(_MACHINE_SURFACE, dict(ws_surfaces))

    # (1) The quote-excluded capability skeleton is identical: metered_api's strength AND
    # its per-(label, surface) match counts survive the reflow — no signal lost or
    # conjured, no count drifted, by mere whitespace.
    _check(
        _casing_struct(ws) == _casing_struct(base),
        f"{_MACHINE_SURFACE}: per-archetype (strength, per-(label, surface) counts) skeleton "
        "invariant under whitespace expansion",
    )
    # (2) Claimed archetypes invariant — still EXACTLY metered_api. The reflow conjured
    # no rails claim; the "never manufacture the delta" property on the WHITESPACE axis,
    # from the machine pole.
    _check(
        ws.archetypes == base.archetypes,
        f"{_MACHINE_SURFACE}: claimed archetypes invariant under whitespace expansion "
        f"(base {base.archetypes}, ws {ws.archetypes})",
    )
    # (3) The non-metered archetypes stay NA and the whole NA/unclaimed set is invariant
    # — which archetypes an API-first store is excused on as NA is a property of WHAT its
    # spec declares, never of how its author spaced it.
    _check(
        machine_must_be_na <= set(ws.unclaimed) and set(ws.unclaimed) == set(base.unclaimed),
        f"{_MACHINE_SURFACE}: the non-metered archetypes stay NA and the whole NA set is "
        f"invariant under whitespace expansion (base {sorted(base.unclaimed)}, ws {sorted(ws.unclaimed)})",
    )


def main() -> int:
    tests = [
        test_canonical_org_offering,
        test_canonical_com_offering,
        test_canonical_metaphorical_ship_stays_na_org,
        test_canonical_metaphorical_ship_stays_na_com,
        test_retail_inverse_offering,
        test_retail_sandbox_title_does_not_trip_test_mode,
        test_service_booking_anchor_offering,
        test_service_booking_partition_tracks_storefront_type,
        test_data_retrieval_anchor_offering,
        test_data_retrieval_partition_tracks_storefront_type,
        test_nonstorefront_empty_offering,
        test_machine_surface_openapi_storefront,
        test_offering_relabel_invariance_org,
        test_offering_relabel_invariance_com,
        test_offering_relabel_invariance_machine,
        test_offering_relabel_invariance_payment_rail,
        test_offering_relabel_invariance_async_job,
        test_offering_relabel_invariance_api_auth,
        test_offering_relabel_invariance_error_contract,
        test_offering_relabel_invariance_test_mode,
        test_offering_relabel_invariance_pagination,
        test_offering_relabel_invariance_cancel_job,
        test_offering_relabel_invariance_streaming_response,
        test_offering_relabel_invariance_output_license,
        test_offering_relabel_invariance_free_trial,
        test_offering_relabel_invariance_self_provisioning,
        test_offering_relabel_invariance_webhook_verification,
        test_offering_relabel_invariance_content_provenance,
        test_offering_relabel_invariance_output_resolution,
        test_offering_relabel_invariance_priced_listing,
        test_offering_relabel_invariance_payment_receipt,
        test_offering_relabel_invariance_plan_purchase,
        test_offering_relabel_invariance_output_retention,
        test_offering_relabel_invariance_failure_not_billed,
        test_offering_relabel_invariance_reserve_and_settle,
        test_offering_relabel_invariance_free_included_usage,
        test_offering_relabel_invariance_variant_selection,
        test_offering_surface_order_invariance_output_license,
        test_offering_surface_order_invariance_org,
        test_offering_content_scale_invariance_org,
        test_offering_content_scale_invariance_com,
        test_offering_content_scale_invariance_retail,
        test_offering_content_scale_invariance_machine,
        test_offering_noise_surface_invariance_org,
        test_offering_noise_surface_invariance_com,
        test_offering_noise_surface_invariance_retail,
        test_offering_noise_surface_invariance_machine,
        test_offering_listing_order_invariance_priced_listing,
        test_offering_endpoint_order_invariance_metered_api,
        test_offering_casing_invariance_org,
        test_offering_casing_invariance_com,
        test_offering_casing_invariance_machine,
        test_offering_casing_invariance_retail,
        test_offering_surface_dedup_invariance_org,
        test_offering_surface_dedup_invariance_com,
        test_offering_surface_dedup_invariance_machine,
        test_offering_whitespace_invariance_machine,
        test_offering_relabel_invariance_retail,
        test_offering_relabel_invariance_nonstorefront,
        test_offering_relabel_negative_control,
        test_offering_relabel_evidence_invariance_org,
        test_offering_relabel_evidence_invariance_com,
        test_offering_relabel_evidence_invariance_machine,
        test_offering_relabel_evidence_negative_control,
        test_mixed_storefront_anchor_offering,
        test_mixed_partition_tracks_storefront_type,
        test_cross_signal_archetype_isolation,
        test_cross_signal_isolation_negative_control,
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
