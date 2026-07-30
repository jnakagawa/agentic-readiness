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
# specific labels the precision guard requires — never bare "ship").
_RETAIL_PHYSICAL_LABELS = {"add-to-cart", "stock"}


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


def main() -> int:
    tests = [
        test_canonical_org_offering,
        test_canonical_com_offering,
        test_canonical_metaphorical_ship_stays_na_org,
        test_canonical_metaphorical_ship_stays_na_com,
        test_retail_inverse_offering,
        test_retail_sandbox_title_does_not_trip_test_mode,
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
        test_offering_relabel_invariance_output_license,
        test_offering_surface_order_invariance_output_license,
        test_offering_relabel_invariance_retail,
        test_offering_relabel_invariance_nonstorefront,
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
