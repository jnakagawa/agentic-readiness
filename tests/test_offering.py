"""Unit tests for offering relevance discovery (asrs/offering.py).

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_offering.py

Covers the load-bearing behaviours with SYNTHETIC surfaces (no network):
  - an agent-native API storefront claims metered_api / digital_good /
    subscription and NOT physical_good — including the precision guard that a
    metaphorical "every image you ship" is NOT read as physical fulfillment;
  - a physical retail storefront claims physical_good and NOT metered_api (the
    inverse), so the fixed template bank marks the other archetypes NA;
  - a non-storefront claims nothing (no false archetypes);
  - service_booking and data_retrieval each fire on their own language;
  - evidence is quoted + auditable, strength counts DISTINCT signals, and the
    unclaimed set is the exact NA complement of the claimed set;
  - homepage HTML is stripped (script/style/tags never leak into evidence) and a
    site that only serves a homepage is classified from it alone.

The Driftflight-flavoured strings appear ONLY as fixture text (the spec permits
vendor details in tests); they mirror the live 2026-07-23 canonical surfaces so
the offline test tracks what the live classifier actually sees.
"""

from __future__ import annotations

import json
import os
import re
import sys

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import offering  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.offering import ARCHETYPES, classify_offering, strip_html  # noqa: E402

_FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures", "canonical"
)


def _fixture_entry_text(domain: str, url_suffix: str) -> str:
    """Recorded response text of the committed fixture GET entry whose URL ends with ``url_suffix``.

    Reads the fixture's raw recorded responses directly (not through
    ``FetchContext.get``) so any surface — including one only reachable through a
    ``FetchContext`` path/URL resolution — is available as REAL captured bytes for
    classifier-layer tests.
    """
    with open(os.path.join(_FIXTURE_DIR, f"{domain}.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    for entry in data["entries"]:
        if entry.get("method", "GET") == "GET" and entry.get("url", "").endswith(url_suffix):
            return (entry.get("result") or {}).get("text", "") or ""
    return ""


# --- Fixtures: synthetic surfaces mirroring real archetypes -------------------

# An agent-native text-to-image API storefront. Note the metaphorical "ship"
# ("every image you ship", "ship images daily") — the physical-good precision
# trap that the live canonical pair also contains.
API_HOMEPAGE = """
<!doctype html><html><head>
<title>Driftflight — one visual language for every image you ship</title>
<style>.x{color:red} /* add to cart nonsense in a style block */</style>
<script>var s = "in stock add to basket";</script>
</head><body>
<h1>Every image on brand.</h1>
<p>Driftflight is a text-to-image API built for campaigns. Teams that ship
images daily rely on it. POST https://api.example-imaging.test/v1/images/generate
with a prompt and get hosted output URLs back. Overage is billed per generation.</p>
<h2>Pricing</h2>
<p>Hobby $5 per month, 100 generations / month. Studio $29 per month. Annual
billing saves 20%.</p>
</body></html>
"""

# A physical retail storefront (the inverse): product catalog language.
RETAIL_HOMEPAGE = """
<!doctype html><html><body>
<h1>Northloom Goods</h1>
<ul>
<li>A Light in the Attic — £51.77 — In stock — Add to basket</li>
<li>Tipping the Velvet — £53.74 — Out of stock</li>
</ul>
<p>Free shipping on orders over £40. See our return policy and shipping options.</p>
</body></html>
"""

# A service-booking storefront.
BOOKING_HOMEPAGE = """
<html><body><h1>Harbor Clinic</h1>
<p>Book an appointment online. Check availability and reserve a time slot that
works for you. Same-day bookings when open.</p></body></html>
"""

# A data-retrieval / enrichment service.
DATA_HOMEPAGE = """
<html><body><h1>Recordsmith</h1>
<p>Enrich a list of records against our datasets. Query the database over a
data API and pay per lookup.</p></body></html>
"""

# A non-storefront (example.com-like): no commerce language at all.
NULL_HOMEPAGE = """
<html><body><h1>Example Domain</h1>
<p>This domain is for use in illustrative examples in documents.</p></body></html>
"""

# An agent-surface llms.txt with explicit subscription + agentic-commerce prose.
API_LLMS = """
# Driftflight
> Driftflight is an AI image generation studio: text-to-image over a simple
> HTTP API, with hosted output URLs and commercial licensing.
## Plans (human, monthly)
- Hobby: $5/month - 100 generations
- Studio: $29/month - 750 generations
Agents can purchase autonomously through an x402 handshake; live per-generation
pricing at /plans.
"""

# A machine API CONTRACT (OpenAPI spec) served WITHOUT any llms.txt or marketing
# homepage — the API-first storefront that motivates adding the OpenAPI surface:
# its only machine-readable self-description is the spec. Vendor-neutral commerce
# language lives in the operation summary / description and the pricing note; no
# new signal is needed, only for the surface to be read.
API_OPENAPI = """
{
  "openapi": "3.1.0",
  "info": {
    "title": "Northlight Imaging",
    "description": "A text-to-image inference API. Agents pay-per-generation via an x402 handshake; no account required."
  },
  "servers": [{"url": "https://api.northlight.test/v1"}],
  "paths": {
    "/images/generate": {
      "post": {
        "summary": "Generate an image from a prompt",
        "description": "Returns a hosted output URL. Billed per generation (usage-based)."
      }
    }
  }
}
"""


# An AGENT-PLUGIN DESCRIPTOR (`/.well-known/ai-plugin.json`) served WITHOUT a
# marketing homepage, llms.txt, or OpenAPI spec — the open, vendor-neutral
# manifest a storefront publishes so an AI agent knows what it is and how to use
# it. Its `description_for_model` is a hand-written model-facing SUMMARY of the
# offering in exactly the natural-language commerce prose the signal bank anchors
# on; distinct from the terse OpenAPI contract. No new signal is needed, only for
# the surface to be read.
API_AI_PLUGIN = """
{
  "schema_version": "v1",
  "name_for_model": "northgale_imaging",
  "name_for_human": "Northgale Imaging",
  "description_for_human": "Generate on-brand images from a prompt.",
  "description_for_model": "A text-to-image inference API for agents. Generate an image from a prompt and receive a hosted output URL. Usage-based: agents pay-per-generation via an x402 handshake, no account required.",
  "api": {"type": "openapi", "url": "https://api.northgale.test/openapi.json"},
  "contact_email": "support@northgale.test"
}
"""


# An A2A (Agent2Agent) AGENT CARD served WITHOUT a marketing homepage, llms.txt,
# OpenAPI spec, or ai-plugin descriptor — the open, vendor-neutral manifest an
# agent-native storefront publishes at a well-known URI so another agent can
# discover what it does. Its top-level `description` + per-`skill` descriptions are
# a hand-written, model-facing account of the offering in exactly the natural-
# language capability prose the signal bank anchors on. A DATA/metered agent here
# (distinct from the imaging descriptor above), so the surface is exercised on more
# than one archetype. No new signal is needed, only for the surface to be read.
DATA_AGENT_CARD = """
{
  "protocolVersion": "0.3.0",
  "name": "Ledger Enrichment Agent",
  "description": "An agent that enriches company records against a proprietary dataset. Look up a firm by domain and receive structured fields. Metered API: agents pay-per-request via an x402 handshake, usage-based, no account required.",
  "url": "https://api.ledgerenrich.test/a2a",
  "skills": [
    {
      "id": "enrich_company",
      "name": "Enrich company",
      "description": "Enrich a company record and query the dataset over a REST API.",
      "tags": ["data", "enrichment"]
    }
  ]
}
"""


# A rendered HTML API-REFERENCE PAGE served at /docs — the human/agent-facing
# docs an API-first storefront most commonly exposes at a conventional /docs (or
# /api-docs, /reference) path, distinct from the machine well-known JSON docs. It
# is HTML, so discover_offering must HTML-STRIP it (as it does the homepage)
# before scanning. NON-VACUOUS on the strip: the <style>/<script> blocks carry
# RETAIL DECOY words ("out of stock", "shopping cart") — exactly the shape present
# on the real canonical /docs page — which, scanned RAW, would false-positive
# physical_good on a pure API storefront (the battery pollution the directive
# removes); stripped, they never reach the scanner. The visible prose documents a
# metered API (endpoints + rate limits + per-generation billing) and image
# generation (digital_good).
DOCS_HTML = """
<!doctype html><html><head>
<title>Northpeak API reference</title>
<style>.cart::after{content:"add to cart"} /* out of stock decoy */</style>
<script>var x = "shopping cart checkout, out of stock, shipping address";</script>
</head><body>
<main>
<h1 id="overview">Northpeak API</h1>
<p>Generate an image from a text prompt over a simple REST API. POST
https://api.northpeak.test/v1/images/generate with a prompt and receive a hosted
output URL. Billed per generation; usage-based.</p>
<h2 id="rate-limits">Rate limits</h2>
<p>Free tier: 20 requests per minute. Bursts beyond the limit queue.</p>
</main>
</body></html>
"""


def test_api_storefront_claims_agent_native_not_physical():
    prof = classify_offering("example-imaging.test", {"homepage": API_HOMEPAGE})
    claimed = set(prof.archetypes)
    assert "metered_api" in claimed, prof.archetypes
    assert "digital_good" in claimed, prof.archetypes
    assert "subscription" in claimed, prof.archetypes
    print(f"  ok: API storefront claims agent-native archetypes, got {prof.archetypes}")
    # THE precision guard: metaphorical "ship" must not read as physical.
    assert not prof.claims("physical_good"), (
        "false-positive physical_good from metaphorical 'ship'"
    )
    assert not prof.claims("service_booking")
    assert not prof.claims("data_retrieval")
    print("  ok: metaphorical 'ship' does NOT trigger physical_good (precision)")


def test_retail_storefront_is_the_inverse():
    prof = classify_offering("northloom.test", {"homepage": RETAIL_HOMEPAGE})
    assert prof.claims("physical_good"), prof.archetypes
    assert not prof.claims("metered_api"), prof.archetypes
    assert not prof.claims("subscription"), prof.archetypes
    print(f"  ok: retail storefront claims physical_good only, got {prof.archetypes}")
    # The template bank marks everything it does not claim as NA (never scored).
    assert set(prof.unclaimed) == set(ARCHETYPES) - {"physical_good"}
    print(f"  ok: unclaimed = NA complement, got {prof.unclaimed}")


def test_sku_inventory_is_retail_sense_not_compute():
    # PRECISION (surfaced live on api.replicate.com, 2026-07-27): a COMPUTE/GPU
    # hardware "SKU" must not read as a physical good. An inference API's OpenAPI
    # spec says "The SKU for the hardware used to run the model"; the old
    # bare-"\bSKU\b" signal falsely claimed physical_good, running an irrelevant
    # fulfillment intent on a pure API storefront — the exact battery pollution
    # the operator directive removes. `test_offering_canonical.py` pins this on
    # the real captured fixture; here it is pinned on a synthetic surface.
    compute = classify_offering(
        "compute-api.test",
        {
            "/openapi.json": (
                '{"info":{"description":"A text-to-image inference API, billed per '
                'generation."},"components":{"schemas":{"hardware":{"description":'
                '"The SKU for the hardware used to run the model."}}}}'
            )
        },
    )
    assert compute.claims("metered_api"), compute.archetypes
    assert not compute.claims("physical_good"), (
        "compute/GPU hardware SKU falsely read as a physical good"
    )
    print("  ok: a compute hardware 'SKU' does NOT trigger physical_good (precision)")

    # The RETAIL sense still fires via sku-inventory alone (no add-to-cart / stock
    # / shipping present), so the precision tightening did not gut recall.
    retail = classify_offering(
        "catalog.test",
        {
            "homepage": (
                "Browse our catalog. Every product SKU is listed; check inventory "
                "levels before you order."
            )
        },
    )
    assert retail.claims("physical_good"), retail.archetypes
    labels = {
        s.label
        for c in retail.claimed
        if c.archetype == "physical_good"
        for s in c.signals
    }
    assert "sku-inventory" in labels, labels
    print("  ok: retail 'product SKU' / 'inventory levels' still fires sku-inventory")


def test_priced_listing_precision_synthetic():
    # PRICED CATALOG LISTING — a concrete decimal price quoted directly beside a
    # purchasable item's availability / add-to-cart control is the "understand the
    # offer" price leg for a physical good: an agent must read the item's PRICE to
    # decide and fulfill a physical purchase, and none of the sibling legs
    # (add-to-cart = the ACTION, stock = WHETHER available, sku-inventory =
    # inventory management) guarantees a readable price. Each POSITIVE is a real,
    # vendor-neutral priced-listing shape; each NEGATIVE is price-SHAPED noise that
    # must NOT fire it (the precision traps: metered per-call / per-period API
    # pricing, a subscription fee, a bare marketing price, and "in stock" with no
    # price — none of which is a priced catalog listing).
    positives = {
        "pound in stock": "A Light in the Attic £51.77 In stock",
        "dollar add to cart": "Ceramic mug $12.99 Add to cart",
        "euro in stock": "Wool scarf 24,95 In stock",  # comma decimal, no glyph
        "add to basket": "Field notebook 9.50 Add to basket",
        "add to bag": "Canvas tote 18.00 Add to bag",
    }
    for name, text in positives.items():
        prof = classify_offering("shop.test", {"homepage": text})
        assert prof.claims("physical_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "physical_good"
            for s in c.signals
        }
        assert "priced-listing" in labels, (name, labels)
    print(f"  ok: {len(positives)} real priced-listing phrasings each fire priced-listing")

    negatives = {
        "metered per-call": "Pricing: $0.01 per API call, billed monthly.",
        "subscription fee": "Just $29.00 / month, cancel anytime.",
        "per-1k requests": "$5.00 per 1,000 requests on the metered tier.",
        "bare marketing price": "Pricing starts at $99.99 for the pro plan.",
        "stock without price": "This model is currently in stock and ready to run.",
        "price then sentence break": "Total was 19.95. In stock levels vary by region.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "priced-listing" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} price-shaped noise strings do NOT fire priced-listing (precision)"
    )


def test_priced_listing_fires_on_real_captured_retail():
    # Real-evidence, NON-VACUOUS, END-TO-END: the priced-listing signal fires on the
    # GENUINE product catalog captured live from a real retail storefront —
    # books.toscrape.com's homepage lists each in-stock title beside its price
    # ("£51.77 In stock"), captured verbatim in the committed fixture. Run the REAL
    # discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would, the same real-data non-vacuity move
    # test_pagination_fires_on_real_captured_openapi makes.
    #
    # SCORE-NEUTRAL by construction: books.toscrape.com already claims ONLY
    # physical_good (its strongest and only archetype), so a priced-catalog signal on
    # its homepage can only deepen that claim's evidence — never add an archetype or
    # reorder. The classifier is off the scoring path; the canonical pair (which
    # quotes bare metered per-call prices with NO in-stock listing) is unchanged
    # (priced-listing fires on neither driftflight surface — pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    home = _fixture_entry_text("books.toscrape.com", "books.toscrape.com")
    assert home, "fixture lost its homepage entry"
    assert "In stock" in strip_html(home), "fixture homepage lost its priced in-stock listings"

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "books.toscrape.com.json"))
    prof = offering.discover_offering(ctx)

    assert prof.claims("physical_good"), prof.archetypes
    phys = next(c for c in prof.claimed if c.archetype == "physical_good")
    pl = [s for s in phys.signals if s.label == "priced-listing"]
    assert pl, {s.label for s in phys.signals}
    quote = pl[0].quote.lower()
    assert "in stock" in quote or "add to" in quote, pl[0].quote
    # The canonical pair carries bare currency amounts but no priced in-stock
    # listing, so the signal must NOT fire there (non-vacuous NA guard).
    for api in ("drift-flight.org", "driftflight.com"):
        actx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{api}.json"))
        aprof = offering.discover_offering(actx)
        alabels = {s.label for c in aprof.claimed for s in c.signals}
        assert "priced-listing" not in alabels, (api, alabels)
    print(f"  ok: priced-listing fires on REAL captured retail catalog — quote: {pl[0].quote!r}")


def test_credit_metered_precision_synthetic():
    # Credit-based metering — prepay a balance, spend N credits per call — is the
    # dominant billing convention for generative / agent-native APIs, but bare
    # "credit(s)" is a false-positive minefield. Each POSITIVE is a real credit-
    # billing phrasing that must claim metered_api via the new credit-metered
    # signal; each NEGATIVE is credit-shaped noise (the C2PA metadata field, a
    # wallet balance, a refund, feature-flag names, the payment instrument, store
    # credit) that must NOT fire credit-metered. The negatives are drawn from the
    # exact traps present in the committed canonical fixtures.
    positives = {
        "buy a credit plan": "Prepay once: buy a credit plan and call until it runs out.",
        "credit ran out": "Error usage_exhausted: your plan's credit ran out. Top up to continue.",
        "credits per call": "Metered billing: 1 credit per API call, deducted from your balance.",
        "purchase credits": "Purchase credits in bundles; no subscription required.",
        "credit balance": "Check your credit balance before a large batch job.",
        "credit-based": "Simple credit-based pricing — spend credits as you go.",
        "api credits": "Agents authenticate and spend API credits per request.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "credit-metered" in labels, (name, labels)
    print(f"  ok: {len(positives)} real credit-billing phrasings each fire credit-metered")

    negatives = {
        "C2PA metadata field": '{"licence":"commercial","credits":"C2PA content credentials embedded"}',
        "wallet balance": "An unspent ceiling can never get stuck as seller credit.",
        "camelCase field": '{"includedCreditUsd":null,"remainingCreditUsd":"25.000000"}',
        "refund": "A failed delivery is credited back in full.",
        "feature-flag name": '{"name":"credits-v2-jul-2026","enabled":true}',
        "flag exhaustion": '{"name":"disable-workflows-on-credit-exhaustion"}',
        "payment instrument": "We accept any major credit card at checkout.",
        "store credit": "Refunds are issued as store credit toward your next order.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "credit-metered" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} credit-shaped noise strings do NOT fire credit-metered (precision)"
    )


def test_credit_metered_fires_on_real_captured_billing_prose():
    # Real-evidence, NON-VACUOUS validation of the credit-metered signal — it fires
    # on GENUINE credit-billing prose captured live from a real storefront, and does
    # NOT fire on that SAME storefront's credit-shaped metadata trap.
    #
    # driftflight.com documents credit billing on its agent docs: "buy a credit or
    # subscription plan", "your plan's credit ran out", "minimumUsd for credit
    # plans" — captured in the committed canonical fixture on the docs subdomain
    # agents.driftflight.com/llms-full.txt. discover_offering now crawls that doc
    # subdomain (see test_doc_subdomain_surfaces_are_read_live); here we exercise
    # the classifier directly on the captured bytes, the surface the signal reads.
    billing = _fixture_entry_text("driftflight.com", "/llms-full.txt")
    assert "credit" in billing.lower(), "fixture llms-full.txt lost its credit-billing prose"
    prof = classify_offering("driftflight.com", {"/llms-full.txt": billing})
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    cred = [s for s in metered.signals if s.label == "credit-metered"]
    assert cred, {s.label for s in metered.signals}
    assert "credit" in cred[0].quote.lower(), cred[0].quote
    print(f"  ok: credit-metered fires on REAL captured billing prose — quote: {cred[0].quote!r}")

    # Precision on real noise: the committed homepage carries the C2PA metadata
    # field ('"credits": "C2PA content credentials embedded"') — captured live — and
    # that credit-shaped text must NOT read as credit metering.
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    home = ctx.homepage(ua="browser").text or ""
    assert "credit" in home.lower(), "homepage lost its credit-shaped C2PA trap"
    home_prof = classify_offering("driftflight.com", {"homepage": home})
    home_labels = {s.label for c in home_prof.claimed for s in c.signals}
    assert "credit-metered" not in home_labels, home_labels
    print("  ok: the homepage C2PA 'credits' metadata does NOT fire credit-metered (real-data precision)")


def test_rate_limit_metering_precision_synthetic():
    # A documented rate limit / request quota is a defining feature of a metered
    # programmatic API — it tells an agent how fast/how often it may call, the
    # "understand the offer" capability. Each POSITIVE is real API rate-limit /
    # quota language that must claim metered_api via the new rate-limited signal;
    # each NEGATIVE is rate/quota-SHAPED noise that must NOT fire it (the precision
    # traps: "flat rate", "unlimited", a disk/storage/free quota, a steady rate).
    positives = {
        "rate limits heading": "Rate limits: Hobby tier allows 2 concurrent renders.",
        "rate-limited": "The endpoint is rate-limited to protect shared capacity.",
        "requests per minute": "Free tier: 20 requests per minute; Pro lifts the cap.",
        "req/s notation": "Sustained throughput up to 100 req/s on the growth plan.",
        "calls slash day": "Sandbox keys are capped at 500 calls/day.",
        "api quota": "Each key carries a monthly API quota; overage is billed.",
        "quota resets": "Your quota resets at 00:00 UTC every day.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "rate-limited" in labels, (name, labels)
    print(f"  ok: {len(positives)} real rate-limit/quota phrasings each fire rate-limited")

    negatives = {
        "flat rate pricing": "Simple flat rate pricing — one price, no surprises.",
        "unlimited requests": "Unlimited image downloads on every paid plan.",
        "steady rate": "Frames render at a steady rate throughout the job.",
        "disk quota": "Each workspace ships with a 10 GB disk quota for assets.",
        "free quota bare": "Try it within your free quota; no card required.",
        "exchange rate": "Prices shown convert at the daily exchange rate.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "rate-limited" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} rate/quota-shaped noise strings do NOT fire rate-limited (precision)"
    )


def test_rate_limit_fires_on_real_captured_api_docs():
    # Real-evidence, NON-VACUOUS validation: the rate-limited signal fires on the
    # GENUINE "Rate limits" API-docs section captured live from a real storefront —
    # driftflight.com publishes a `<h2 id="rate-limits">Rate limits</h2>` block
    # (per-tier concurrent-render limits, "no quota use") on its /docs surface,
    # captured verbatim in the committed canonical fixture. Exercise the classifier
    # directly on those captured bytes (the surface the signal reads), the same
    # real-data non-vacuity move test_credit_metered_fires_on_real_captured_billing_prose
    # makes on /llms-full.txt.
    #
    # SCORE-NEUTRAL by construction: this evidence lives on /docs. discover_offering
    # now DOES crawl /docs (added to _SURFACE_DOCS this cycle — HTML-stripped like the
    # homepage), so the canonical discovery classification is UNCHANGED: metered_api is
    # already the strongest claim on the pair, so the crawled hit only deepens its
    # evidence, never adds an archetype or reorders (the claimed SET+ORDER are pinned
    # green by tests/test_offering_canonical.py (12/12) and test_docs_surface_is_read_live
    # below). This test exercises the classifier directly on the captured /docs bytes.
    docs = _fixture_entry_text("driftflight.com", "/docs")
    assert "rate limit" in docs.lower(), "fixture /docs lost its Rate limits section"
    prof = classify_offering("driftflight.com", {"/docs": docs})
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    rl = [s for s in metered.signals if s.label == "rate-limited"]
    assert rl, {s.label for s in metered.signals}
    assert "rate" in rl[0].quote.lower() or "quota" in rl[0].quote.lower(), rl[0].quote
    print(f"  ok: rate-limited fires on REAL captured API-docs prose — quote: {rl[0].quote!r}")


def test_tiered_volume_metering_precision_synthetic():
    # Committed-use / tiered-volume pricing is a defining metered-API billing
    # convention (billing scales with committed or cumulative volume), distinct
    # from the flat per-call rate. Each POSITIVE is real volume/tier billing prose
    # that must claim metered_api via the new tiered-volume signal; each NEGATIVE
    # is volume/tier-SHAPED noise that must NOT fire it (the precision traps: audio
    # "volume control", a support "tier 1", "top tier", "committed to use").
    positives = {
        "committed use": "Prepay a committed-use plan for a lower per-call rate.",
        "committed use spaced": "Save with committed use discounts on annual spend.",
        "volume discount": "High callers get an automatic volume discount at scale.",
        "volume tiers": "Refused content is never counted against volume tiers.",
        "volume pricing": "Ask about volume pricing for over 1M generations/month.",
        "tiered pricing": "Simple tiered pricing: pay less per unit as you grow.",
        "usage tiers": "Billing moves through usage tiers as monthly calls rise.",
        "pricing tiers": "Three pricing tiers scale the per-request price down.",
        "tier price": "tier 3: $0.002 per image once you pass 500k generations.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "tiered-volume" in labels, (name, labels)
    print(f"  ok: {len(positives)} real volume/tier billing phrasings each fire tiered-volume")

    negatives = {
        "volume control": "A slider in the corner adjusts the playback volume control.",
        "high volume of": "We process a high volume of images every hour.",
        "tier 1 support": "Paid plans include tier 1 support and a shared inbox.",
        "top tier": "A top tier design studio trusts our brand kit.",
        "committed to use": "Our team is committed to use only renewable power.",
        "first tier bare": "The first tier of the cake was three layers tall.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "tiered-volume" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} volume/tier-shaped noise strings do NOT fire tiered-volume (precision)"
    )


def test_tiered_volume_fires_on_real_captured_billing_prose():
    # Real-evidence, NON-VACUOUS validation: the tiered-volume signal fires on the
    # GENUINE volume-tier billing language captured live from the canonical
    # driftflight.com homepage — "Refused content is never billed and never counted
    # against volume tiers" — a real usage-metered-by-volume-tier statement,
    # captured verbatim in the committed fixture. Exercise the classifier directly
    # on those captured bytes, the same real-data non-vacuity move
    # test_rate_limit_fires_on_real_captured_api_docs makes.
    #
    # SCORE-NEUTRAL by construction: metered_api is ALREADY the strongest claim on
    # the canonical pair, so a new metered_api signal only DEEPENS its evidence — it
    # never adds an archetype or reorders the claimed set (pinned green by
    # tests/test_offering_canonical.py). Discovery is off the scoring path, so the
    # scored canonical delta is untouched.
    home = _fixture_entry_text("driftflight.com", "driftflight.com")
    assert "volume tier" in home.lower(), "fixture homepage lost its volume-tier billing prose"
    prof = classify_offering("driftflight.com", {"homepage": home})
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    tv = [s for s in metered.signals if s.label == "tiered-volume"]
    assert tv, {s.label for s in metered.signals}
    assert "volume tier" in tv[0].quote.lower(), tv[0].quote
    print(f"  ok: tiered-volume fires on REAL captured billing prose — quote: {tv[0].quote!r}")


def test_test_mode_metering_precision_synthetic():
    # A TEST / SANDBOX mode is a defining agent-completion capability of a metered
    # API: an agent can validate its integration and dry-run a call at ZERO cost
    # (no real charge, no quota use) before authorizing anything real — the
    # "provision + complete the job safely, without a human" capability, aligned
    # with ASRS's own $0-only ethos. Each POSITIVE is real test/sandbox facility
    # prose that must claim metered_api via the new test-mode signal; each NEGATIVE
    # is sandbox/test-SHAPED noise that must NOT fire it (the precision traps: a
    # demo-site named "Sandbox", a sandboxed iframe, a sandbox game, a
    # `unit_test_runner` filename, a "test drive").
    positives = {
        "test mode": "Flip the API into test mode to validate your integration for free.",
        "sandbox environment": "A full sandbox environment mirrors production with no billing.",
        "sandbox api": "Point requests at the sandbox API before you go live.",
        "sandbox endpoint": "Every route has a sandbox endpoint that returns simulated output.",
        "test api key": "Generate a test API key from the dashboard to try it.",
        "sandbox credentials": "Request sandbox credentials to exercise the full flow.",
        "sandbox key": "Use your sandbox key to preview responses at no charge.",
        "dry run": "Every call supports a dry run that returns a simulated response.",
        "dry-run flag": "Add ?dry-run=true to preview a request without charging.",
        "test key convention": "Test keys look like kv_test_a1b2c3d4e5f6g7h8.",
        "masked test stub": "Issue keys shaped df_test_... in the sandbox before df_live_....",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "test-mode" in labels, (name, labels)
    print(f"  ok: {len(positives)} real test/sandbox facility phrasings each fire test-mode")

    negatives = {
        "demo site name": "All products | Books to Scrape - Sandbox",
        "sandboxed iframe": "The widget renders inside a sandboxed iframe for safety.",
        "sandbox game": "Our sandbox game lets kids build whole worlds from blocks.",
        "playground sandbox": "The children played in a sandbox at the park all afternoon.",
        "unit test file": "Run unit_test_runner and smoke_test_suite before every deploy.",
        "test drive": "Book a test drive of the new model this weekend.",
        "test the waters": "Test the water temperature before you dive in.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "test-mode" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} sandbox/test-shaped noise strings do NOT fire test-mode (precision)"
    )


def test_test_mode_fires_on_real_captured_api_docs():
    # Real-evidence, NON-VACUOUS validation: the test-mode signal fires on the
    # GENUINE test/live credential dichotomy captured live from the canonical
    # driftflight.com /docs surface — "Keys look like df_live_... (production) or
    # df_test_... (sandbox: watermarked output, no quota use)" — a real sandbox /
    # test-key capability, captured verbatim in the committed fixture. Exercise the
    # classifier directly on those captured bytes (the surface the signal reads),
    # the same real-data non-vacuity move test_rate_limit_fires_on_real_captured_api_docs
    # makes on the same /docs surface.
    #
    # SCORE-NEUTRAL by construction: metered_api is ALREADY the strongest claim on
    # the canonical pair, so a new metered_api signal only DEEPENS its evidence — it
    # never adds an archetype or reorders the claimed set (pinned green by
    # tests/test_offering_canonical.py). Discovery is off the scoring path, so the
    # scored canonical delta is untouched.
    docs = _fixture_entry_text("driftflight.com", "/docs")
    assert "df_test_" in docs, "fixture /docs lost its test/sandbox key dichotomy"
    prof = classify_offering("driftflight.com", {"/docs": strip_html(docs)})
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    tm = [s for s in metered.signals if s.label == "test-mode"]
    assert tm, {s.label for s in metered.signals}
    assert "test" in tm[0].quote.lower() or "sandbox" in tm[0].quote.lower(), tm[0].quote
    print(f"  ok: test-mode fires on REAL captured /docs prose — quote: {tm[0].quote!r}")


def test_seat_licensing_subscription_precision_synthetic():
    # Seat / per-user licensing is the dominant SaaS-subscription billing
    # convention (a recurring price per user seat). Each POSITIVE is real seat /
    # per-user licensing prose that must claim subscription via the new
    # seat-licensing signal; each NEGATIVE is seat-SHAPED noise that must NOT fire
    # it (the precision traps: a window seat, a seat belt, theatre seats).
    positives = {
        "per seat month": "Team plan: $12 per seat per month, billed to the org.",
        "per user per month": "Pro is priced per user per month with no minimum.",
        "dollar per seat": "$8 per seat unlocks the shared workspace.",
        "per-seat pricing": "We use simple per-seat pricing — add users as you grow.",
        "seat-based billing": "Seat-based billing scales with your team size.",
        "seats included": "The Growth plan has 10 seats included, add more anytime.",
        "per seat license": "Enterprise is licensed per seat with SSO.",
    }
    for name, text in positives.items():
        prof = classify_offering("saas.test", {"homepage": text})
        assert prof.claims("subscription"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "subscription"
            for s in c.signals
        }
        assert "seat-licensing" in labels, (name, labels)
    print(f"  ok: {len(positives)} real seat/per-user licensing phrasings each fire seat-licensing")

    negatives = {
        "window seat": "Choose a window seat for the best view on your flight.",
        "seat belt": "Fasten your seat belt before the aircraft departs.",
        "take a seat": "Take a seat in the lobby and we will call your name.",
        "seats at table": "The venue has 8 seats at the table for your party.",
        "front seat": "The front seat reclines fully for the red-eye leg.",
        "reserve a seat": "Reserve a seat on the 9am departure.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "seat-licensing" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} seat-shaped noise strings do NOT fire seat-licensing (precision)"
    )


def test_free_trial_subscription_precision_synthetic():
    # A FREE TRIAL is the subscription-archetype mirror of metered_api's test-mode:
    # an agent can EVALUATE the recurring offer at ZERO cost before committing to
    # billing — the "understand + provision the offer safely, without a human"
    # capability, aligned with ASRS's $0-only ethos. Each POSITIVE is real trial-offer
    # prose that must claim subscription via the new free-trial signal; each NEGATIVE
    # is trial-SHAPED noise that must NOT fire it (the precision traps: a clinical
    # trial, a court trial, "trial and error", "trial by fire").
    positives = {
        "free trial": "Start with a free trial, no card required.",
        "free-trial hyphen": "Every plan includes a free-trial week.",
        "trial period": "The trial period runs for 30 days before billing begins.",
        "trial account": "Create a trial account to explore the workspace.",
        "trial allowance": "Your trial allowance lets you evaluate it before any payment.",
        "trial membership": "A trial membership unlocks the library for two weeks.",
        "n-day trial": "Get a 14-day free trial on the Pro plan.",
        "n day trial": "Enjoy a 30 day trial with full access.",
        "start your trial": "Start your free trial and cancel anytime.",
        "try free for days": "Try it free for 14 days, then $9/month.",
    }
    for name, text in positives.items():
        prof = classify_offering("saas.test", {"homepage": text})
        assert prof.claims("subscription"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "subscription"
            for s in c.signals
        }
        assert "free-trial" in labels, (name, labels)
    print(f"  ok: {len(positives)} real free-trial phrasings each fire free-trial")

    negatives = {
        "clinical trial": "The clinical trial enrolled 200 patients last spring.",
        "court trial": "The court trial lasted a full week in October.",
        "trial and error": "We found the recipe through trial and error.",
        "trial by fire": "His first project was a real trial by fire.",
        "on trial": "The new policy is on trial for the next quarter.",
        "free shipping": "Enjoy free shipping on every order over $50.",
        "free image": "Your first generated image is free to download.",
        "free allowance": "A generous free allowance covers early testing.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "free-trial" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} trial-shaped noise strings do NOT fire free-trial (precision)"
    )


def test_free_trial_fires_on_real_captured_subscription_prose():
    # Real-evidence, NON-VACUOUS validation: the free-trial signal fires on the
    # GENUINE trial offer captured live from the canonical driftflight.com homepage
    # — "Driftflight includes a free trial allowance, so an agent can evaluate it
    # before any payment - the trial needs no funding and no signup" — a real
    # evaluate-at-$0-before-committing capability, captured verbatim in the committed
    # fixture. Exercise the classifier directly on those captured bytes (the surface
    # the signal reads), the same real-data non-vacuity move the metered_api
    # _fires_on_real_captured tests make.
    #
    # SCORE-NEUTRAL by construction: driftflight.com ALREADY claims subscription, so
    # a new subscription signal only DEEPENS its evidence — it never adds an archetype
    # or reorders the claimed set (pinned green by tests/test_offering_canonical.py:
    # metered_api > digital_good > subscription is unchanged, subscription still last).
    # The trial-free .org side keeps subscription at its prior strength (asymmetric
    # evidence, identical claimed set). Discovery is off the scoring path, so the
    # scored canonical delta is untouched.
    home = _fixture_entry_text("driftflight.com", "driftflight.com")
    assert "free trial" in home.lower(), "fixture homepage lost its free-trial offer"
    prof = classify_offering("driftflight.com", {"homepage": home})
    assert prof.claims("subscription"), prof.archetypes
    sub = next(c for c in prof.claimed if c.archetype == "subscription")
    ft = [s for s in sub.signals if s.label == "free-trial"]
    assert ft, {s.label for s in sub.signals}
    assert "trial" in ft[0].quote.lower(), ft[0].quote
    print(f"  ok: free-trial fires on REAL captured homepage prose — quote: {ft[0].quote!r}")


def test_booking_and_data_archetypes_fire():
    booking = classify_offering("harbor.test", {"homepage": BOOKING_HOMEPAGE})
    assert booking.claims("service_booking"), booking.archetypes
    assert not booking.claims("physical_good")
    print(f"  ok: booking storefront claims service_booking, got {booking.archetypes}")

    data = classify_offering("recordsmith.test", {"homepage": DATA_HOMEPAGE})
    assert data.claims("data_retrieval"), data.archetypes
    print(f"  ok: data service claims data_retrieval, got {data.archetypes}")


def test_data_retrieval_precision_synthetic():
    # data_retrieval is one of the two thinnest archetypes, so a FALSE claim here
    # does maximum damage: the site gets probed with a lookup/enrichment intent it
    # does not serve (the exact archetype pollution this module removes). Its two
    # cheapest bare-word signals — "enrich" and "dataset" — are precision-hardened
    # so a common ML/marketing word can no longer conjure the whole archetype. Each
    # POSITIVE is genuine data-retrieval OFFERING prose that must still claim
    # data_retrieval; each NEGATIVE is enrich/dataset-SHAPED noise that must NOT.
    positives = {
        "enrich records": "Enrich a list of records against our data API.",
        "enriches records": "The agent enriches company records and returns fields.",
        "enrich contacts": "Enrich your contacts with firmographic data.",
        "data enrichment": "A data enrichment endpoint for your CRM.",
        "query dataset": "Query the dataset over a REST API and pay per lookup.",
        "download dataset": "Download the full dataset or subscribe to the feed.",
        "dataset api": "Our dataset API returns structured records by domain.",
        "against datasets": "Match your rows against our proprietary datasets.",
    }
    for name, text in positives.items():
        prof = classify_offering("data.test", {"homepage": text})
        assert prof.claims("data_retrieval"), (name, prof.archetypes)
    print(f"  ok: {len(positives)} genuine data-retrieval phrasings each claim data_retrieval")

    negatives = {
        "training dataset": "Our model is trained on a proprietary dataset of 100M images.",
        "dataset of prompts": "Fine-tuned on a diverse dataset of prompts and captions.",
        "enriched experience": "We deliver an enriched, delightful user experience.",
        "enriching partnership": "Join us for an enriching, long-term partnership.",
        "enrich workflow": "Enrich your creative workflow with new presets.",
        "culture enrichment": "We fund enrichment of our company culture.",
        "dataset provenance": "Every render's dataset provenance is documented for audit.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        assert not prof.claims("data_retrieval"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} enrich/dataset-shaped noise strings do NOT claim data_retrieval (precision)"
    )


def test_data_retrieval_precision_is_canonical_invariant_on_real_fixtures():
    # Real-evidence regression guard: the precision hardening leaves every committed
    # fixture's CLAIMED SET byte-identical — data_retrieval stays NA on all five
    # (none of them serves a queryable dataset or a record-enrichment API), and no
    # other archetype moves. Runs the FULL live discovery path (from_fixture ->
    # discover_offering) so the guard exercises the real captured surfaces, not a
    # hand-built map. This pins that narrowing the two bare-word signals could not
    # have silently dropped (or conjured) a claim on the real anchors. Off the
    # scoring path, so the scored canonical delta is untouched.
    expected = {
        "api.replicate.com": ["metered_api"],
        "books.toscrape.com": ["physical_good"],
        "drift-flight.org": ["metered_api", "digital_good", "subscription"],
        "driftflight.com": ["metered_api", "digital_good", "subscription"],
        "example.com": [],
    }
    for domain, archetypes in expected.items():
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.archetypes == archetypes, (domain, prof.archetypes)
        assert "data_retrieval" not in prof.archetypes, domain
    print("  ok: all 5 committed fixtures keep their exact claimed set; data_retrieval stays NA")


def test_service_booking_book_precision_synthetic():
    # service_booking is tied with data_retrieval for the thinnest archetype, so a
    # FALSE claim here does maximum damage: the site gets probed with a reservation
    # intent it does not serve (the exact archetype pollution this module removes).
    # Its cheapest signal — the bare "book a ..." verb — collides with the single
    # most common B2B SALES CTA ("book a demo / call / meeting / walkthrough /
    # briefing"), which is NOT a bookable service. The guard strips those
    # unambiguous sales-CTA objects while keeping every genuine bookable service.
    # Each POSITIVE is genuine booking prose that must still claim service_booking
    # via the book signal; each NEGATIVE is a book-a-<CTA> string that must NOT
    # conjure service_booking on its own.
    positives = {
        "book a table": "Book a table for dinner at your preferred time.",
        "book a room": "Book a room online for your next stay.",
        "book an appointment": "Book an appointment with one of our stylists.",
        "book a session": "Book a session with a certified trainer today.",
        "book a consultation": "Book a consultation to discuss your options.",
        "book a class": "Book a class in our weekly schedule.",
        "book now": "Ready when you are — book now.",
        "booking noun": "Complete your booking in just a few seconds.",
    }
    for name, text in positives.items():
        prof = classify_offering("booking.test", {"homepage": text})
        assert prof.claims("service_booking"), (name, prof.archetypes)
    print(f"  ok: {len(positives)} genuine bookable-service phrasings each claim service_booking")

    negatives = {
        "book a demo": "Book a demo to see the API in action.",
        "book a call": "Book a call with our sales team.",
        "book a meeting": "Book a meeting to learn more.",
        "book a walkthrough": "Book a walkthrough of the platform.",
        "book a walk-through": "Book a walk-through with an engineer.",
        "book a briefing": "Book a briefing with our solutions team.",
        "book demos plural": "Book your demos with the team this quarter.",
    }
    for name, text in negatives.items():
        prof = classify_offering("saas.test", {"homepage": text})
        assert not prof.claims("service_booking"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} book-a-<sales-CTA> strings do NOT claim service_booking (precision)"
    )


def test_service_booking_schedule_precision_synthetic():
    # The DIRECT SIBLING of test_service_booking_book_precision_synthetic: the
    # `schedule` signal carried the identical unfixed sales-CTA gap that Cycle 190
    # closed for `book`. Bare "schedule a/an/your <x>" fired on the same B2B SALES CTA
    # family ("schedule a demo / call / meeting / walkthrough / briefing"), falsely
    # claiming service_booking (tied-thinnest archetype -> maximum damage) on a
    # pure-API / SaaS storefront. The guard strips those unambiguous sales-CTA objects
    # while keeping every genuine scheduled service. Each POSITIVE is schedule-ONLY
    # prose (no sibling service_booking signal rescues it), so it exercises the
    # narrowed schedule branch directly; each NEGATIVE is a schedule-a-<CTA> string
    # that must NOT conjure service_booking on its own.
    positives = {
        "schedule a session": "Schedule a session with a certified trainer today.",
        "schedule a consultation": "Schedule a consultation to discuss your options.",
        "schedule a table": "Schedule a table for your dinner party.",
        "schedule a pickup": "Schedule a pickup at your local branch.",
        "schedule your visit": "Schedule your visit to the clinic online.",
        "schedule a fitting": "Schedule a fitting with one of our tailors.",
    }
    for name, text in positives.items():
        prof = classify_offering("booking.test", {"homepage": text})
        assert prof.claims("service_booking"), (name, prof.archetypes)
    print(f"  ok: {len(positives)} genuine scheduled-service phrasings each claim service_booking")

    negatives = {
        "schedule a demo": "Schedule a demo to see the API in action.",
        "schedule a call": "Schedule a call with our sales team.",
        "schedule a meeting": "Schedule a meeting to learn more.",
        "schedule a walkthrough": "Schedule a walkthrough of the platform.",
        "schedule a walk-through": "Schedule a walk-through with an engineer.",
        "schedule a briefing": "Schedule a briefing with our solutions team.",
        "schedule demos plural": "Schedule your demos with the team this quarter.",
    }
    for name, text in negatives.items():
        prof = classify_offering("saas.test", {"homepage": text})
        assert not prof.claims("service_booking"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} schedule-a-<sales-CTA> strings do NOT claim service_booking (precision)"
    )


def test_data_retrieval_lookup_precision_synthetic():
    # The THIRD data_retrieval bare-word signal hardened (siblings: enrich/dataset,
    # Cycle 186). `lookup` is one of the two thinnest archetypes' cheapest signals,
    # so a FALSE claim does maximum damage: the site gets probed with a records-
    # lookup intent it does not serve. Bare "\blook ?ups?\b" collides with the
    # DATA-STRUCTURE / INTERNALS vocabulary that saturates API & engineering docs
    # ("lookup table", "hash / cache / index / key / symbol / array / in-memory
    # lookup") — every one an internal mechanism or performance descriptor, NOT a
    # data-retrieval OFFERING. The guard strips those unambiguous internals
    # collocations while keeping every genuine record-retrieval sense. Each POSITIVE
    # is lookup-ONLY prose (no sibling data_retrieval signal rescues it), so it
    # exercises the narrowed lookup branch directly; each NEGATIVE is an internals
    # collocation that must NOT conjure data_retrieval on its own.
    positives = {
        "phone lookup": "A phone lookup service returning carrier and line-type data.",
        "reverse ip lookup": "Reverse IP lookup over a simple REST endpoint.",
        "address lookup": "Address lookup by postal code, one call per query.",
        "domain lookup": "Domain lookup returns registration records for any host.",
        "company lookup": "Company lookup by name or registration ID.",
        "whois lookup": "WHOIS lookup for any registered domain.",
        "look up a customer": "Look up a customer record by email address.",
        "look up a reservation": "Look up a table reservation by confirmation code.",
    }
    for name, text in positives.items():
        prof = classify_offering("data.test", {"homepage": text})
        assert prof.claims("data_retrieval"), (name, prof.archetypes)
    print(f"  ok: {len(positives)} genuine record-lookup phrasings each claim data_retrieval")

    negatives = {
        "lookup table": "Values are stored in a lookup table for fast access.",
        "lookup tables": "We ship precomputed lookup tables with the SDK.",
        "hash lookup": "Records are found via a hash lookup in constant time.",
        "cache lookup": "A cache lookup avoids the network round trip.",
        "index lookup": "The query planner performs an index lookup internally.",
        "key lookup": "A key lookup returns the stored value.",
        "symbol lookup": "Dynamic symbol lookup happens at load time.",
        "array lookup": "An array lookup by offset is constant time.",
        "in-memory lookup": "Config resolves with an in-memory lookup.",
    }
    for name, text in negatives.items():
        prof = classify_offering("internals.test", {"homepage": text})
        assert not prof.claims("data_retrieval"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} data-structure/internals lookup strings do NOT claim data_retrieval (precision)"
    )


def test_batch_retrieval_precision_synthetic():
    # A NEW data_retrieval capability signal: BATCH / BULK RETRIEVAL — the agent
    # submits MANY records / lookups / queries in ONE call and gets them all back.
    # This is the "complete the job AT SCALE" leg for data_retrieval (the analog of
    # metered_api's `concurrency-limit`), DISTINCT from every existing signal, each
    # of which describes a SINGLE-item retrieval: `enrich` submits records but is
    # silent on bulk; `lookup` retrieves ONE datum by key; `dataset` queries a
    # dataset; `query-records`/`data-service` name a records API — NONE says the
    # agent can amortize a large job over one batch request. Precision is the whole
    # game — data_retrieval is one of the two thinnest archetypes, so a FALSE claim
    # does maximum damage (the site gets probed with a records-lookup intent it does
    # not serve). Bare "batch"/"bulk" is a two-family minefield: the metered_api
    # COMPUTE sense (batch inference / batch prediction / a batch JOB / "a batch of
    # images" / a generic "batch processing pipeline" — a generative/ML API runs
    # batch JOBS, not data retrieval) and the physical_good/retail BULK sense ("buy
    # in bulk" / a "bulk discount" / a "bulk order" / "bulk email" / a "fresh batch
    # of cookies" / a "batch number"). So the signal NEVER matches a bare token — it
    # requires batch/bulk to NAME a data-retrieval object (a batch/bulk ENRICHMENT /
    # LOOKUP / GEOLOCATION, a "batch/bulk IP <processing|lookup|data|...>"), or a
    # data-retrieval VERB/OBJECT (enrich / look up / query / retrieve / records /
    # contacts / leads) done "in batches" / "in bulk". Each POSITIVE fires
    # `batch-retrieval` (non-vacuous); each NEGATIVE must NOT claim data_retrieval on
    # its own.
    #
    # Canonical-invariant by construction: the signal fires on the committed
    # data_retrieval anchor (ipinfo.io — "Batch Enrichment API" / "Bulk Enrichment" /
    # the `/batch` endpoint that "speeds up bulk IP processing"), which ALREADY claims
    # data_retrieval via lookup/enrich/dataset/data-service → no new archetype, no
    # reorder; and on ZERO of the seven other committed fixtures (none carries any
    # "batch"/"bulk" prose — pinned by tests/test_offering_canonical.py). Off the
    # scoring path.
    positives = {
        # The real captured ipinfo.io /docs prose (verbatim shapes).
        "batch enrichment api": "Read the Batch Enrichment API guide to get started.",
        "bulk enrichment": "See Bulk Enrichment in the developer docs.",
        "bulk ip processing": "This significantly speeds up bulk IP processing.",
        "batch lookup": "The default endpoint uses a standard batch lookup.",
        # Genuine bulk-retrieval vocabulary from other real data services.
        "bulk lookup": "Bulk lookup of up to 1,000 addresses in one call.",
        "batch geolocation": "Run batch geolocation for millions of IPs.",
        "enrich records in bulk": "Enrich your records in bulk with a single request.",
        "look up in batches": "Look up thousands of IPs in batches over the API.",
        "query records in bulk": "Query records in bulk over a REST endpoint.",
        "retrieve contacts in bulk": "Retrieve matching contacts in bulk by domain.",
    }
    for name, text in positives.items():
        prof = classify_offering("scale.test", {"homepage": text})
        assert prof.claims("data_retrieval"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "data_retrieval"
            for s in c.signals
        }
        assert "batch-retrieval" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} batch/bulk-retrieval phrasings each fire batch-retrieval")

    negatives = {
        # metered_api COMPUTE batch — a batch JOB, NOT a data retrieval.
        "batch inference": "Run batch inference on your prompts overnight.",
        "batch prediction": "Submit a batch prediction job to the model.",
        "batch of images": "Generate a batch of images from one prompt.",
        "batch processing pipeline": "Our batch processing pipeline renders overnight.",
        "batch job": "Kick off a batch job for the training run.",
        "batch generation": "Queue a batch generation of renders.",
        # physical_good / retail BULK.
        "buy in bulk": "Buy in bulk and save 20 percent.",
        "bulk discount": "A bulk discount applies on orders over 50 units.",
        "bulk order": "Place a bulk order for your whole team.",
        "bulk email": "Send bulk email campaigns to your list.",
        "fresh batch": "A fresh batch of cookies every morning.",
        "batch number": "Check the batch number printed on the label.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("data_retrieval"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} compute-batch / retail-bulk strings do NOT claim data_retrieval (precision)"
    )


def test_batch_retrieval_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of the synthetic
    # precision guard. It pins that the new batch-retrieval signal fires on the
    # GENUINE bulk-retrieval prose captured live from the committed data_retrieval
    # anchor's /docs surface (ipinfo.io — "Batch Enrichment API" / "Bulk Enrichment"
    # / the `/batch` endpoint that "significantly speeds up bulk IP processing"), run
    # through the REAL discovery path (from_fixture -> discover_offering) exactly as a
    # live crawl would.
    #
    # SCORE-NEUTRAL by construction: ipinfo.io ALREADY claims data_retrieval (via
    # lookup/enrich/dataset/data-service), so the batch evidence can only DEEPEN that
    # claim — never add an archetype or reorder. The classifier is off the scoring
    # path; the anchor's claimed SET is unchanged (pinned by
    # tests/test_offering_canonical.py).
    docs = _fixture_entry_text("ipinfo.io", "/docs")
    assert "bulk ip processing" in docs.lower(), "ipinfo /docs lost its bulk-retrieval prose"
    prof = classify_offering("ipinfo.io", {"/docs": docs})
    assert prof.claims("data_retrieval"), prof.archetypes
    data = next(c for c in prof.claimed if c.archetype == "data_retrieval")
    br = [s for s in data.signals if s.label == "batch-retrieval"]
    assert br, {s.label for s in data.signals}
    # Non-vacuity beyond the single recorded hit: the SAME captured /docs documents
    # the FULL bulk-retrieval contract an agent needs at scale — a Batch Enrichment
    # API, a Bulk Enrichment guide, and the `/batch` endpoint that speeds up bulk IP
    # processing — each an independent branch of the signal (proven against the
    # fixture bytes, since the classifier records only the first-firing instance).
    assert "batch enrichment" in docs.lower(), "ipinfo"
    assert "bulk enrichment" in docs.lower(), "ipinfo"
    print(f"  ok: batch-retrieval fires on REAL captured ipinfo.io /docs — quote: {br[0].quote!r}")

    # Full-discovery claimed-SET invariance on the anchor (score-neutrality): the new
    # signal deepens data_retrieval without adding or dropping any archetype.
    ictx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "ipinfo.io.json"))
    iprof = offering.discover_offering(ictx)
    assert set(iprof.archetypes) == {
        "metered_api", "data_retrieval", "subscription", "digital_good"
    }, iprof.archetypes

    # NON-VACUOUS negatives on REAL data: the metered_api pair + marketplace, the
    # retail catalog, the booking storefront, and the null site carry no batch/bulk
    # prose — the signal must be absent and conjure or reorder no archetype.
    for dom, expected in (
        ("driftflight.com", ["metered_api", "digital_good", "subscription"]),
        ("drift-flight.org", ["metered_api", "digital_good", "subscription"]),
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "batch-retrieval" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: batch-retrieval is ABSENT on the api-pair / marketplace / retail / null fixtures (non-vacuous, score-neutral)")


def test_service_booking_manage_precision_synthetic():
    # The FIRST lifecycle-management signal for service_booking (Cycle 248), the
    # DISTINCT "operate without a human" leg: reschedule or cancel an EXISTING
    # booking (vs the five create signals — book/appointment/reservation/schedule/
    # availability — which all describe MAKING one). service_booking is tied with
    # data_retrieval for the thinnest archetype, so a FALSE claim does maximum
    # damage. The two verbs are minefields left bare: "cancel" is broad-English /
    # billing ("cancel your subscription", "cancel anytime", "cancel your order",
    # "cancel a running job"), and "reschedule" collides with the SAME B2B sales-CTA
    # family the book/schedule signals strip ("reschedule a demo / call / meeting").
    # The guard NEVER matches a bare verb — it requires the reschedule/cancel verb
    # within a short window of an unambiguous BOOKING NOUN (appointment / booking /
    # reservation), in either order. Each POSITIVE is management prose that must fire
    # manage-booking (non-vacuous); each NEGATIVE carries a bare verb with NO booking
    # noun and must NOT claim service_booking on its own.
    positives = {
        # Real captured acuityscheduling.com shapes (verbatim-faithful).
        "appointment rescheduling and cancellations": "Appointment rescheduling and cancellations are built in.",
        "rescheduled and canceled appointments": "Notify staff of new, rescheduled, and canceled appointments.",
        # Genuine management vocabulary from other real booking services.
        "reschedule or cancel your appointment": "Reschedule or cancel your appointment anytime online.",
        "reschedule a booking": "Clients can reschedule a booking without calling.",
        "cancel a reservation": "Cancel a reservation up to 24 hours in advance.",
        "change or cancel your appointment": "Change or cancel your appointment through the portal.",
        "reschedule bookings": "Reschedule bookings straight from the confirmation email.",
    }
    for name, text in positives.items():
        prof = classify_offering("manage.test", {"homepage": text})
        assert prof.claims("service_booking"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "service_booking"
            for s in c.signals
        }
        assert "manage-booking" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} reschedule/cancel-a-booking phrasings each fire manage-booking")

    negatives = {
        # billing / broad-English cancel — no booking noun.
        "cancel your subscription": "Cancel your subscription anytime from settings.",
        "cancel anytime": "Cancel anytime — no long-term contract.",
        "cancel your order": "Cancel your order for a full refund.",
        "cancel a running job": "Cancel a running prediction job at any time.",
        "cancel the meeting": "We had to cancel the meeting on short notice.",
        # sales-CTA reschedule — the book/schedule minefield, no booking noun.
        "reschedule a demo": "Reschedule a demo with our sales team.",
        "reschedule your call": "Reschedule your call with an advisor.",
        "reschedule a meeting": "Need to reschedule a meeting? Use the link.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("service_booking"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} bare-cancel / sales-CTA-reschedule strings do NOT claim service_booking (precision)"
    )


def test_manage_booking_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of the synthetic
    # precision guard. It pins that manage-booking fires on the GENUINE lifecycle-
    # management prose captured live from the committed service_booking anchor
    # (acuityscheduling.com — "Appointment rescheduling and cancellations",
    # "Notify staff of new, rescheduled, and canceled appointments"), run through
    # the REAL discovery path (from_fixture -> discover_offering) exactly as a live
    # crawl would.
    #
    # SCORE-NEUTRAL by construction: acuityscheduling.com ALREADY claims
    # service_booking (via book/appointment/schedule), so the management evidence
    # can only DEEPEN that claim — never add an archetype or reorder. The classifier
    # is off the scoring path; the anchor's claimed SET is unchanged (pinned by
    # tests/test_offering_canonical.py).
    actx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "acuityscheduling.com.json"))
    aprof = offering.discover_offering(actx)
    assert aprof.claims("service_booking"), aprof.archetypes
    sb = next(c for c in aprof.claimed if c.archetype == "service_booking")
    mb = [s for s in sb.signals if s.label == "manage-booking"]
    assert mb, {s.label for s in sb.signals}
    assert mb[0].quote and mb[0].quote.strip(), "manage-booking quote empty"
    print(f"  ok: manage-booking fires on REAL captured acuityscheduling.com — quote: {mb[0].quote!r}")

    # Full-discovery claimed-SET invariance on the anchor (score-neutrality): the new
    # signal deepens service_booking without adding or dropping any archetype.
    assert set(aprof.archetypes) == {
        "subscription", "service_booking", "metered_api"
    }, aprof.archetypes

    # NON-VACUOUS negatives on REAL data: the metered_api pair + marketplace, the
    # retail catalog, the data anchor, and the null site carry no reschedule/cancel-a-
    # booking prose — the signal must be absent and conjure or reorder no archetype.
    for dom, expected in (
        ("driftflight.com", ["metered_api", "digital_good", "subscription"]),
        ("drift-flight.org", ["metered_api", "digital_good", "subscription"]),
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "manage-booking" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: manage-booking is ABSENT on the api-pair / marketplace / retail / null fixtures (non-vacuous, score-neutral)")


def test_service_booking_notification_precision_synthetic():
    # The closed-loop FOLLOW-THROUGH signal for service_booking (Cycle 252), a THIRD
    # distinct capability leg beyond the five create signals (book/appointment/
    # reservation/schedule/availability — MAKE a booking) and manage-booking
    # (reschedule/cancel — MODIFY one): the booking is automatically CONFIRMED and its
    # reminders handled WITHOUT a human — the "provision + complete the job without a
    # human" completion-acknowledgment leg, the service_booking analog of metered_api's
    # payment-receipt. service_booking is tied with data_retrieval for the thinnest
    # archetype, so a FALSE claim does maximum damage. All three tokens are minefields
    # left bare: "confirmation" is order/email/UI ("order confirmation", "confirm your
    # email", "confirmation dialog"); "notification"/"reminder" is restock/UI/system
    # ("restockNotificationsEnabled", "undelivered notifications", "a gentle reminder").
    # The guard NEVER matches a bare confirm/remind token — it requires the token within
    # a short window of an unambiguous BOOKING NOUN (appointment / booking / reservation),
    # in either order, OR the fixed "appointment reminder(s)" collocation. Each POSITIVE
    # is booking-notification prose that must fire booking-notification (non-vacuous);
    # each NEGATIVE carries a bare confirm/notify/remind token with NO booking noun and
    # must NOT claim service_booking on its own.
    positives = {
        # Real captured acuityscheduling.com shapes (verbatim-faithful).
        "appointment reminders": "We send automated appointment reminders.",
        "booking triggers a confirmation": "Every booking triggers a confirmation email.",
        "reminder before the appointment": "Reminder emails go out before the appointment.",
        # Genuine confirmation/reminder vocabulary from other real booking services.
        "confirmation for your appointment": "You get a confirmation for your appointment instantly.",
        "reminder before your booking": "We send a reminder before your booking.",
        "reservation confirmation email": "A reservation confirmation email is sent automatically.",
    }
    for name, text in positives.items():
        prof = classify_offering("notify.test", {"homepage": text})
        assert prof.claims("service_booking"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "service_booking"
            for s in c.signals
        }
        assert "booking-notification" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} confirm/remind-a-booking phrasings each fire booking-notification")

    negatives = {
        # order / email / UI confirmation — no booking noun.
        "order confirmation email": "Your order confirmation email is on its way.",
        "confirm your email": "Please confirm your email address to continue.",
        "confirmation dialog": "Click OK in the confirmation dialog to proceed.",
        # restock / system / broad-English reminder — no booking noun.
        "restock notifications": "restockNotificationsEnabled is false in the config.",
        "gentle reminder password": "A gentle reminder to update your password.",
        "reminder invoice due": "We'll send a reminder when your invoice is due.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("service_booking"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} bare-confirm / restock-notify / broad-reminder strings do NOT claim service_booking (precision)"
    )


def test_booking_notification_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of the synthetic
    # precision guard. It pins that booking-notification fires on the GENUINE
    # confirmation/reminder prose captured live from the committed service_booking
    # anchor (acuityscheduling.com — "Confirmations and reminders sent automatically",
    # "Every booking triggers a confirmation email. Reminder emails go out before the
    # appointment", "appointment reminders"), run through the REAL discovery path
    # (from_fixture -> discover_offering) exactly as a live crawl would.
    #
    # SCORE-NEUTRAL by construction: acuityscheduling.com ALREADY claims
    # service_booking (via book/appointment/schedule), so the follow-through evidence
    # can only DEEPEN that claim — never add an archetype or reorder. The classifier is
    # off the scoring path; the anchor's claimed SET is unchanged (pinned by
    # tests/test_offering_canonical.py).
    actx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "acuityscheduling.com.json"))
    aprof = offering.discover_offering(actx)
    assert aprof.claims("service_booking"), aprof.archetypes
    sb = next(c for c in aprof.claimed if c.archetype == "service_booking")
    bn = [s for s in sb.signals if s.label == "booking-notification"]
    assert bn, {s.label for s in sb.signals}
    assert bn[0].quote and bn[0].quote.strip(), "booking-notification quote empty"
    print(f"  ok: booking-notification fires on REAL captured acuityscheduling.com — quote: {bn[0].quote!r}")

    # Full-discovery claimed-SET invariance on the anchor (score-neutrality): the new
    # signal deepens service_booking without adding or dropping any archetype.
    assert set(aprof.archetypes) == {
        "subscription", "service_booking", "metered_api"
    }, aprof.archetypes

    # NON-VACUOUS negatives on REAL data: the metered_api pair + marketplace, the retail
    # catalog, and the null site carry no confirm/remind-a-booking prose — the signal
    # must be absent and conjure or reorder no archetype. (The canonical flight pair is
    # the critical case: a flight API is not a reschedulable appointment storefront, so
    # service_booking must stay NA there and the score stays invariant.)
    for dom, expected in (
        ("driftflight.com", ["metered_api", "digital_good", "subscription"]),
        ("drift-flight.org", ["metered_api", "digital_good", "subscription"]),
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "booking-notification" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: booking-notification is ABSENT on the api-pair / marketplace / retail / null fixtures (non-vacuous, score-neutral)")


def test_service_booking_intake_form_precision_synthetic():
    # The data-collection PRECONDITION signal for service_booking (Cycle 256), a
    # FOURTH distinct capability leg beyond the five create signals (book/appointment/
    # reservation/schedule/availability — MAKE a booking), manage-booking
    # (reschedule/cancel — MODIFY one) and booking-notification (confirm/remind —
    # FOLLOW THROUGH): the storefront gathers what a booked service needs via a custom
    # INTAKE FORM — the "collect what the job needs / provision without a human" leg.
    # service_booking is tied with data_retrieval for the thinnest archetype, so a
    # FALSE claim does maximum damage. Both tokens are minefields left bare: "form" is
    # web-wide (contact form, sign-up form, "form field", an HTML <form>); "intake" is
    # broad English (calorie/water intake, "the intake process"). The guard NEVER
    # matches a bare token — it requires the fixed unambiguous "intake form(s)"
    # collocation. Each POSITIVE is intake-form prose that must fire intake-form
    # (non-vacuous); each NEGATIVE carries a bare form/intake token with no such
    # collocation and must NOT claim service_booking on its own.
    positives = {
        # Real captured acuityscheduling.com shapes (verbatim-faithful).
        "custom intake forms": "Collect client info with custom intake forms.",
        "fill out any intake forms": "Fill out any intake forms you've set up.",
        # Genuine intake-form vocabulary from other real booking services.
        "complete the intake form": "Complete the intake form before your appointment.",
        "submit an intake form": "Clients submit an intake form when they book.",
        "intake forms plural": "We use intake forms to gather what your session needs.",
    }
    for name, text in positives.items():
        prof = classify_offering("intake.test", {"homepage": text})
        assert prof.claims("service_booking"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "service_booking"
            for s in c.signals
        }
        assert "intake-form" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} intake-form phrasings each fire intake-form")

    negatives = {
        # bare "form" — no intake collocation.
        "contact form": "Fill out the contact form to reach us.",
        "form field required": "Every form field on the page is required.",
        "sign-up form": "Submit the sign-up form to create an account.",
        # bare "intake" — no form collocation.
        "calorie intake": "Track your daily calorie intake in the app.",
        "intake process": "The patient intake process takes only minutes.",
        "water intake": "Increase your water intake for better health.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("service_booking"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} bare-form / bare-intake strings do NOT claim service_booking (precision)"
    )


def test_intake_form_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of the synthetic
    # precision guard. It pins that intake-form fires on the GENUINE custom-intake-form
    # prose captured live from the committed service_booking anchor
    # (acuityscheduling.com — "collect client info with custom intake forms", "fill out
    # any intake forms you've set up"), run through the REAL discovery path
    # (from_fixture -> discover_offering) exactly as a live crawl would.
    #
    # SCORE-NEUTRAL by construction: acuityscheduling.com ALREADY claims
    # service_booking (via book/appointment/schedule), so the intake evidence can only
    # DEEPEN that claim — never add an archetype or reorder. The classifier is off the
    # scoring path; the anchor's claimed SET is unchanged (pinned by
    # tests/test_offering_canonical.py).
    actx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "acuityscheduling.com.json"))
    aprof = offering.discover_offering(actx)
    assert aprof.claims("service_booking"), aprof.archetypes
    sb = next(c for c in aprof.claimed if c.archetype == "service_booking")
    intake = [s for s in sb.signals if s.label == "intake-form"]
    assert intake, {s.label for s in sb.signals}
    assert intake[0].quote and intake[0].quote.strip(), "intake-form quote empty"
    print(f"  ok: intake-form fires on REAL captured acuityscheduling.com — quote: {intake[0].quote!r}")

    # Full-discovery claimed-SET invariance on the anchor (score-neutrality): the new
    # signal deepens service_booking without adding or dropping any archetype.
    assert set(aprof.archetypes) == {
        "subscription", "service_booking", "metered_api"
    }, aprof.archetypes

    # NON-VACUOUS negatives on REAL data: the metered_api pair + marketplace, the retail
    # catalog, and the null site carry no intake-form prose — the signal must be absent
    # and conjure or reorder no archetype. (The canonical flight pair is the critical
    # case: a flight API is not an appointment storefront collecting service intake, so
    # service_booking must stay NA there and the score stays invariant.)
    for dom, expected in (
        ("driftflight.com", ["metered_api", "digital_good", "subscription"]),
        ("drift-flight.org", ["metered_api", "digital_good", "subscription"]),
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "intake-form" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: intake-form is ABSENT on the api-pair / marketplace / retail / null fixtures (non-vacuous, score-neutral)")


def test_subscription_recurring_precision_synthetic():
    # The last cheap bare-word subscription signal hardened (siblings: enrich/
    # dataset/lookup for data_retrieval, book/schedule for service_booking). Bare
    # "\brecurring\b" is a broad-ENGLISH minefield: "a recurring theme", "a
    # recurring dream/nightmare", "a recurring bug/issue", "a recurring character/
    # role", "a recurring meeting", "a recurring pattern" — none says a plan bills
    # on a cadence, yet each would CONJURE a subscription claim (probing a site with
    # a plan-purchase intent it does not serve). The guard requires a BILLING object
    # after "recurring" (billing/payment/charge/subscription/invoice/fee/plan/price/
    # dues/membership, optionally through a cadence adjective) OR a billing VERB in a
    # short window ("billed / charged / invoiced ... on a recurring basis"). Each
    # POSITIVE is recurring-ONLY prose (fires the `recurring` label with no sibling
    # subscription signal rescuing it), so it exercises the narrowed branch directly;
    # each NEGATIVE is a non-billing "recurring <noun>" that must NOT claim
    # subscription on its own.
    positives = {
        "recurring plan": "We offer a recurring plan for regular users.",  # isolation-matrix phrase
        "recurring billing": "Access continues under recurring billing.",
        "recurring payments": "Set up recurring payments for uninterrupted access.",
        "recurring charge": "A recurring charge keeps your workspace active.",
        "recurring invoice": "You receive a recurring invoice each period.",
        "recurring fee": "Membership carries a recurring fee.",
        "recurring pricing": "Our recurring pricing keeps things simple.",
        "recurring membership dues": "Cover your recurring membership dues automatically.",
        "billed on a recurring basis": "Your card is billed on a recurring basis.",
        "charged on a recurring basis": "You are charged on a recurring basis until you cancel.",
    }
    for name, text in positives.items():
        prof = classify_offering("sub.test", {"homepage": text})
        assert prof.claims("subscription"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "subscription"
            for s in c.signals
        }
        assert "recurring" in fired, (name, sorted(fired))  # non-vacuous: THIS branch fired
    print(f"  ok: {len(positives)} genuine recurring-billing phrasings each claim subscription via `recurring`")

    negatives = {
        "recurring theme": "A recurring theme in our renders is soft light.",
        "recurring dream": "The app helps you journal a recurring dream.",
        "recurring nightmare": "Debugging this was a recurring nightmare.",
        "recurring bug": "We fixed a recurring bug in the parser.",
        "recurring issue": "Latency was a recurring issue last quarter.",
        "recurring character": "Meet Ada, a recurring character in the tutorial.",
        "recurring role": "She plays a recurring role in the demo videos.",
        "recurring meeting": "Add a recurring meeting to your calendar.",
        "recurring pattern": "The dataset shows a recurring pattern of spikes.",
        "recurring motif": "Circles are a recurring motif in the brand art.",
        "recurring headache": "Config drift was a recurring headache.",
        "recurring costs": "We help you cut the recurring costs of your servers.",
        "recurring basis, no verb": "We meet on a recurring basis to review progress.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("subscription"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} non-billing 'recurring <noun>' strings do NOT claim subscription (precision)"
    )


def test_usage_based_metered_precision_synthetic():
    # The metered_api bank's last cheap bare-word signal hardened (siblings:
    # enrich/dataset/lookup for data_retrieval, book/schedule for service_booking,
    # recurring for subscription). The `usage-based` signal's bare "\bmetered\b"
    # alternative is a BROAD-ENGLISH minefield: metered parking, a metered water /
    # electricity UTILITY, a metered-dose inhaler, metered postage, metered verse,
    # "a metered approach" — none says a metered API bills by usage, yet each would
    # CONJURE a metered_api claim (probing a site with an API-call intent it does not
    # serve — the exact battery-mismatch the offering-relative directive removes).
    # The guard requires "metered" to name a BILLING/USAGE/API context (a billing
    # object after it, "metered per <unit>", "metered and charged/billed", or a
    # usage/call/request subject that "is/are metered"); the `usage-based`/`overage`
    # alternatives are already billing-specific and stay bare. Each POSITIVE fires
    # the `usage-based` label with no other metered_api signal rescuing it, so it
    # exercises the narrowed branch directly; each NEGATIVE is a broad-English
    # "metered <noun>" that must NOT claim metered_api on its own.
    #
    # The `metered` branches are LOOKAHEAD-anchored so the matched SPAN stays
    # exactly "metered" — the canonical evidence quote is byte-identical (pinned by
    # tests/test_offering_canonical.py + the replay guard); narrowing only, so this
    # is canonical-invariant by construction.
    positives = {
        "metered billing": "Access runs on metered billing.",
        "metered pricing": "We use metered pricing for the service.",
        "metered API": "This is a metered API.",
        "metered usage": "Your invoice reflects metered usage.",
        "metered tier": "Requests fall on the metered tier.",  # priced-listing NEG shape
        "metered and charged": "Usage beyond the plan is metered and charged.",  # canonical .com shape
        "metered per API call": "Metered per API call, no monthly minimum.",  # test-4548 shape
        "metered per request": "Compute is metered per request.",
        "usage is metered": "Your usage is metered.",
        "calls are metered": "All calls are metered.",
        "overage stays bare": "Overage applies past your quota.",  # bare alt untouched
        "usage-based stays bare": "Simple usage-based billing.",  # bare alt untouched
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "usage-based" in fired, (name, sorted(fired))  # non-vacuous: THIS signal fired
    print(f"  ok: {len(positives)} genuine metered-billing phrasings each fire usage-based")

    negatives = {
        "metered parking": "Downtown offers metered parking near the venue.",
        "metered water": "The city bills metered water to each home.",
        "metered electricity": "Homes with metered electricity save money.",
        "metered-dose": "A metered-dose inhaler delivers a fixed dose.",
        "metered dose": "Take one metered dose twice daily.",
        "metered postage": "We print metered postage for bulk mail.",
        "metered verse": "The poem is written in metered verse.",
        "metered approach": "We take a metered approach to rollouts.",
        "metered rhythm": "The track has a slow, metered rhythm.",
        "water is metered": "In this town the water is metered.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("metered_api"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} broad-English 'metered <noun>' strings do NOT claim metered_api (precision)"
    )


def test_payment_challenge_retry_precision_synthetic():
    # A NEW metered_api capability signal: the agent-native payment CHALLENGE-SETTLE-
    # RETRY handshake — the request/response FLOW an agent must EXECUTE to pay
    # programmatically (the endpoint answers with an HTTP 402 challenge; the agent
    # settles/signs it and retries the same request with the payment proof attached).
    # Distinct from every static payment FACT already in the bank (`x402` names the
    # rail, `agent-payment-rail` which rails exist, `payment-receipt` the proof BACK,
    # `reserve-and-settle` a ceiling, `failure-not-billed` a free failure): those say
    # a rail EXISTS, this says how the agent DRIVES it to completion. Precision is the
    # whole game — bare "retry"/"402"/"challenge"/"settle" is a false-positive
    # minefield (a WEBHOOK-delivery retry present verbatim on api.replicate.com, a
    # generic "please retry", a "coding challenge", "settle a dispute", a phone-number
    # 402) — so the signal requires the CO-OCCURRENCE only the payment handshake
    # produces. Each POSITIVE fires `payment-challenge-retry` with no other metered_api
    # signal rescuing it (so it exercises the branch directly); each NEGATIVE must NOT
    # claim metered_api on its own.
    #
    # Canonical-invariant by construction (the signal fires ONLY on driftflight.com,
    # already metered_api's strongest archetype → strength 21->22, no reorder; ABSENT
    # on drift-flight.org, which carries no 402/challenge/settle/retry prose — the
    # discovery-layer echo of the real capability gap; ZERO on the api/retail/null
    # fixtures — pinned by tests/test_offering_canonical.py). Off the scoring path.
    positives = {
        # The real captured driftflight.com agent-docs prose (verbatim shapes).
        "settle via the challenge and retry": "Settle it via the challenge and retry with the proof attached.",
        "retry with signed payment attached": "Retry the same request with the signed payment attached.",
        "retry with the proof attached": "Then retry the same request with the proof attached.",
        "sign the 402 authorization and retry": "Sign the zero-value x402 authorization (free) and retry.",
        "priced 402, pay and retry": "Each call returns one priced 402 with the exact amount; pay and retry.",
        "402 top up and retry": "An exhausted balance surfaces as a 402 - top up and retry.",
        "settle its priced 402 then retry": "Route it as a paid request: settle its priced 402, then retry.",
        "payment challenge direct": "The endpoint answers with a payment challenge.",
        "402 challenge direct": "You receive a 402 challenge on the first call.",
    }
    for name, text in positives.items():
        prof = classify_offering("pay.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "payment-challenge-retry" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} payment challenge-settle-retry phrasings each fire payment-challenge-retry")

    negatives = {
        # The api.replicate.com webhook-redelivery retry — the precision target.
        "webhook redelivery retry": "If there are network problems, we will retry the webhook a few times.",
        "generic retry request": "Please retry the request if it fails.",
        "retry a search": "Retry your search with different filters.",
        "coding challenge": "Join our monthly coding challenge and win prizes.",
        "challenge of scaling": "The challenge of scaling infrastructure is real.",
        "settle a dispute": "We settle disputes within thirty days.",
        "settle down": "Settle down and enjoy the flight.",
        "extension 402": "Call us at extension 402 for support.",
        "retry the payment page": "If the page errors, refresh and try again later.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("metered_api"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} bare retry/402/challenge/settle strings do NOT claim metered_api (precision)"
    )


def test_payment_challenge_retry_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of Cycle 226's
    # SYNTHETIC precision guard (test_payment_challenge_retry_precision_synthetic).
    # It pins that the new payment-FLOW signal's PRESENCE tracks the real
    # with-rails/no-rails CAPABILITY SPLIT it echoes — on committed evidence, run
    # through the REAL discovery path (from_fixture -> discover_offering) exactly as
    # a live crawl would, the same real-data non-vacuity move
    # test_reserve_and_settle_fires_on_real_captured_surfaces / _free_included_usage_
    # make. Until now the signal's real-data behaviour lived only in a COMMENT +
    # test_offering_canonical.py's set+order invariance; this guard makes the
    # discovery-layer echo of the capability gap a first-class per-cycle tripwire.
    #
    # SCORE-NEUTRAL by construction: driftflight.com already claims metered_api (its
    # strongest archetype), so the challenge-settle-retry evidence can only deepen
    # that claim — never add an archetype or reorder. The classifier is off the
    # scoring path; the canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    pcr = [s for s in metered.signals if s.label == "payment-challenge-retry"]
    assert pcr, {s.label for s in metered.signals}
    # The with-rails anchor documents the FULL handshake across >=2 real agent-doc
    # surfaces (the 402 challenge on llms.txt, the settle+retry-with-proof round-trip
    # on llms-full.txt) — a stronger non-vacuity than a single hit, and the shape a
    # storefront that is genuinely agent-completable at the pay leg exhibits.
    surfaces = {s.surface for s in pcr}
    assert len(surfaces) >= 2, sorted(surfaces)
    quotes = " ".join(s.quote.lower() for s in pcr)
    assert ("challenge" in quotes and "retry" in quotes), [s.quote for s in pcr]
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    print(
        f"  ok: payment-challenge-retry fires on {len(pcr)} REAL captured driftflight.com "
        f"agent-doc surfaces {sorted(surfaces)}"
    )

    # PRECISION-CRITICAL on real data: drift-flight.org — the no-rails-side canonical
    # anchor — carries NO 402/challenge/settle/retry prose at all (it publishes no
    # agent docs). The signal must be ABSENT there and .org's claimed set unchanged.
    # This is the discovery-layer echo of the real capability gap: the with-rails .com
    # documents the machine-payable challenge-settle-retry round-trip an agent must
    # drive to complete the pay leg, the .org does not (mirroring payment-receipt /
    # reserve-and-settle / free-included-usage / self-provisioning).
    octx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "drift-flight.org.json"))
    oprof = offering.discover_offering(octx)
    all_labels = {s.label for c in oprof.claimed for s in c.signals}
    assert "payment-challenge-retry" not in all_labels, all_labels
    assert oprof.archetypes == ["metered_api", "digital_good", "subscription"], oprof.archetypes
    print("  ok: payment-challenge-retry is ABSENT on drift-flight.org (real-data precision / capability gap)")

    # NON-VACUOUS negatives on REAL data — the strongest one is api.replicate.com,
    # which carries the very WEBHOOK-REDELIVERY retry ("we will retry the webhook a
    # few times") the synthetic precision guard targets: on real captured prose the
    # signal correctly DODGES it (a redelivery, not a payment handshake). A real
    # retail storefront (books.toscrape.com) and a null site (example.com) document
    # no challenge-settle-retry handshake either — absent on all three, conjuring or
    # reordering no archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "payment-challenge-retry" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print(
        "  ok: payment-challenge-retry is ABSENT on the api (webhook-retry) / retail / "
        "null fixtures (non-vacuous real-data precision, score-neutral)"
    )


def test_non_storefront_claims_nothing():
    prof = classify_offering("example.test", {"homepage": NULL_HOMEPAGE})
    assert prof.archetypes == [], prof.archetypes
    assert set(prof.unclaimed) == set(ARCHETYPES)
    print("  ok: non-storefront claims no archetypes (no false positives)")


def test_strength_counts_distinct_signals_and_orders_claims():
    # Add llms.txt: more distinct metered_api + subscription evidence.
    prof = classify_offering(
        "example-imaging.test", {"homepage": API_HOMEPAGE, "/llms.txt": API_LLMS}
    )
    assert set(prof.surfaces_seen) == {"homepage", "/llms.txt"}, prof.surfaces_seen
    # metered_api should be strongest (most distinct signals) → first.
    assert prof.archetypes[0] == "metered_api", prof.archetypes
    metered = prof.claimed[0]
    # strength is DISTINCT labels, never raw hit count.
    assert metered.strength == len({s.label for s in metered.signals})
    assert metered.strength >= 3, metered.strength
    print(f"  ok: metered_api strongest (strength {metered.strength}), claims ordered by strength")
    # x402 from the llms.txt is captured as a metered_api signal.
    assert any(s.label == "x402" for s in metered.signals), "x402 rail evidence missing"
    print("  ok: x402 agentic-payment rail recorded as metered_api evidence")


def test_classification_is_surface_read_order_invariant():
    # A readiness classification is a property of WHAT a storefront's surfaces
    # DECLARE, not the ORDER an agent happened to fetch them in. This is the
    # discovery-layer analog of the battery presentation-order invariance
    # (test_battery.py) and the leaderboard permutation-invariance
    # (test_readout.py): the claimed-archetype set, its strength ranking, each
    # claim's distinct labels and source surfaces, and the NA complement the
    # offering-relative battery excludes from every mean/spread must ALL be
    # identical under any permutation of the surface-read order. Cross-site
    # comparability rests on it — two crawls of the same site that read /pricing
    # before or after the homepage must classify identically.
    surfaces = {
        # subscription is declared on BOTH surfaces (so a reorder genuinely
        # permutes the per-archetype signal accumulation, not merely the dict);
        # service_booking ties subscription at strength 2 (a tie broken by
        # ARCHETYPES.index, never by which surface arrived first); digital_good
        # is single-surface. service_booking fires TWO genuine bookable-service
        # signals here — "book a table" (book) + "appointments" (appointment) —
        # deliberately NOT the sales-CTA "book a demo" the precision guard strips.
        "homepage": "Our plans are billed monthly. Book a table; appointments available.",
        "/pricing": "Recurring billing. We generate an image for you.",
    }
    forward = classify_offering("shop.test", dict(surfaces))
    reverse = classify_offering("shop.test", dict(reversed(list(surfaces.items()))))

    def _signature(p):
        return [
            (
                c.archetype,
                c.strength,
                tuple(sorted({s.label for s in c.signals})),
                tuple(sorted({s.surface for s in c.signals})),
            )
            for c in p.claimed
        ]

    # (1) The metric-bearing classification is identical under reorder: claimed
    # archetypes IN RANK ORDER, each strength, each claim's distinct labels, and
    # each claim's source surfaces.
    assert _signature(forward) == _signature(reverse), (_signature(forward), _signature(reverse))
    # (2) The NA complement (what the offering-relative battery marks NA and
    # excludes from every mean/spread) is identical — order cannot add or drop a
    # claim.
    assert forward.unclaimed == reverse.unclaimed, (forward.unclaimed, reverse.unclaimed)
    # (3) The SET of surfaces read is identical.
    assert set(forward.surfaces_seen) == set(reverse.surfaces_seen)
    # The strength tie is real and broken by taxonomy index, not arrival order:
    # subscription (ARCHETYPES index 1) and service_booking (index 4) both fire
    # at strength 2, and subscription ranks first in BOTH runs.
    strengths = {c.archetype: c.strength for c in forward.claimed}
    assert strengths.get("subscription") == strengths.get("service_booking") == 2, strengths
    assert forward.archetypes.index("subscription") < forward.archetypes.index("service_booking")
    print("  ok: claimed set / rank / strengths / labels / surfaces / NA invariant under surface reorder")

    # NON-VACUITY: the reorder is REAL and OBSERVABLE — surfaces_seen is a
    # different LIST and the representative sample_quote of the two-surface
    # subscription claim genuinely flips. sample_quote is a first-observed
    # DISPLAY sample, deliberately NOT claimed order-invariant (honest scope:
    # the measurement is invariant; one human-readable evidence sample is not).
    assert forward.surfaces_seen != reverse.surfaces_seen, "reorder not observable"
    f_sub = next(c for c in forward.evidence["claimed"] if c["archetype"] == "subscription")
    r_sub = next(c for c in reverse.evidence["claimed"] if c["archetype"] == "subscription")
    assert f_sub["sample_quote"] != r_sub["sample_quote"], "expected the sample quote to be order-sensitive"
    print("  ok: reorder is observable (surfaces_seen list + subscription sample_quote differ) — non-vacuous")


def _wsr_struct(prof) -> dict:
    """archetype -> (strength, sorted ((label, surface), count)) — the whitespace-independent skeleton.

    The reflow analogue of ``_casing_struct`` in test_offering_canonical.py: excludes
    the quote text (which echoes the matched bytes and so reflows with the surface) and
    keeps the per-(label, surface) match MULTIPLICITY, so a signal that fired N times
    must still fire N times after the whitespace transform.
    """
    from collections import Counter

    return {
        c.archetype: (
            round(c.strength, 9),
            sorted(Counter((s.label, s.surface) for s in c.signals).items()),
        )
        for c in prof.claimed
    }


def _signal_pattern(archetype: str, label: str):
    """The compiled pattern behind one fired (archetype, label) signal, or None."""
    for lbl, pat in offering._SIGNALS.get(archetype, []):
        if lbl == label:
            return pat
    return None


def test_classification_is_whitespace_reflow_invariant():
    # A readiness classification is a property of the WORDS a storefront's surfaces
    # DECLARE, not the TYPOGRAPHY a crawl happened to capture. Plain-text surfaces
    # (llms.txt, a markdown docs page) are routinely line-wrapped, and HTML-stripped
    # prose can carry runs of layout whitespace — so a two-word capability phrase can
    # straddle a newline ("free\nshipping", "per\nmonth") or gain a double space.
    # MANY signals separate their tokens with a LITERAL single space ("free shipping",
    # "add to cart", "billed per <unit>", "per month"), which a line-wrap silently
    # defeats. Before the Cycle-178 normalization, that dropped the claim — and with
    # it the site's whole offering-relative task battery — purely on layout. This is
    # the whitespace-reflow analogue of the casing invariance
    # (test_offering_canonical.py) and the surface-read-order invariance above: the
    # claimed archetypes IN RANK ORDER, the NA/unclaimed complement, and per-archetype
    # (strength, per-(label, surface) match counts) must ALL survive an arbitrary
    # whitespace reflow. Cross-crawl comparability rests on it: two crawls of the same
    # site, one line-wrapped at 80 columns and one not, must classify identically.
    #
    # The prose exercises three archetypes whose fired signals key on literal-space
    # phrases, so a reflow that broke any of them would perturb a claim OR reorder the
    # rank observably.
    flat = (
        "Store notes: we offer free shipping on every physical order. "
        "Add to cart when ready. Programmatic access is billed per call. "
        "Membership renews per month on each billing cycle."
    )
    base = classify_offering("shop.test", {"/llms.txt": flat})

    # Substrate: the property under test is genuinely present — a RANKED multi-archetype
    # classification a reflow could perturb.
    assert len(base.claimed) >= 2, (
        f"substrate: >=2 archetypes claimed so the rank a reflow could reorder is real "
        f"(got {base.archetypes})"
    )
    assert {"physical_good", "metered_api", "subscription"} <= set(base.archetypes), (
        f"substrate: the three literal-space archetypes all claim on the flat prose "
        f"(got {base.archetypes})"
    )

    # A worst-case line-wrap: every space becomes a newline, so EVERY literal-space
    # phrase straddles a line break. TEETH (a): the transform is REAL — the reflowed
    # bytes differ from the flat bytes.
    reflowed = flat.replace(" ", "\n")
    assert reflowed != flat, "the reflow genuinely changed the surface bytes (non-vacuous)"

    # TEETH (b): whitespace normalization is LOAD-BEARING. Among the fired evidence
    # there is a signal whose RAW pattern (a literal-space matcher) match count on the
    # reflowed surface DROPS below its count on the flat surface — i.e. the line-wrap
    # genuinely defeats the literal-space form — so the invariance below rests on the
    # classifier's whitespace-folding, not on the phrases happening to survive reflow.
    load_bearing = None
    for c in base.claimed:
        for s in c.signals:
            pat = _signal_pattern(c.archetype, s.label)
            if pat is None:
                continue
            flat_n = len(pat.findall(flat))
            reflowed_n = len(pat.findall(reflowed))
            if reflowed_n < flat_n:
                load_bearing = (c.archetype, s.label, flat_n, reflowed_n)
                break
        if load_bearing:
            break
    assert load_bearing is not None, (
        "a fired signal's RAW-pattern match count drops under the line-wrap reflow, so "
        "whitespace-folding is load-bearing — the invariance is non-vacuous"
    )

    reflow_prof = classify_offering("shop.test", {"/llms.txt": reflowed})

    # (1) The whitespace-independent capability skeleton is identical: every archetype's
    # strength AND its per-(label, surface) match counts survive the reflow — no signal
    # lost or conjured, no count drifted, by mere line-wrapping.
    assert _wsr_struct(reflow_prof) == _wsr_struct(base), (
        f"per-archetype (strength, per-(label, surface) counts) skeleton invariant "
        f"under whitespace reflow (base {_wsr_struct(base)}, reflow {_wsr_struct(reflow_prof)})"
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order, so a line-wrap must not reorder the battery.
    assert reflow_prof.archetypes == base.archetypes, (
        f"claimed archetypes (ranked) invariant under whitespace reflow "
        f"(base {base.archetypes}, reflow {reflow_prof.archetypes})"
    )
    # (3) The NA/unclaimed complement (excluded from every mean/spread, never penalized)
    # is invariant — which archetypes a site is excused on as NA depends on what it
    # declares, not how a crawl wrapped it.
    assert set(reflow_prof.unclaimed) == set(base.unclaimed), (
        f"NA/unclaimed set invariant under whitespace reflow "
        f"(base {sorted(base.unclaimed)}, reflow {sorted(reflow_prof.unclaimed)})"
    )
    print(
        f"  ok: claimed set / rank / strengths / labels / NA invariant under whitespace "
        f"reflow (load-bearing signal {load_bearing[0]}/{load_bearing[1]}: raw count "
        f"{load_bearing[2]}->{load_bearing[3]} on reflow, normalization restores it)"
    )

    # TEETH (c): the negative control — whitespace-folding must NOT bridge a real
    # paragraph boundary into a phantom phrase. "add" and "to cart" split across a blank
    # line are two unrelated sentences; collapsing runs to a single space keeps them a
    # sentence apart (the \n\n becomes " "), and physical_good's add-to-cart must NOT
    # fire. So the normalization repairs line-wrap WITHOUT manufacturing a claim.
    bridge = "Please add\n\nto our list. Your cart of ideas awaits — nothing to buy here."
    bridge_prof = classify_offering("noise.test", {"/llms.txt": bridge})
    assert "physical_good" not in bridge_prof.archetypes, (
        f"whitespace-folding must not bridge a paragraph split into a phantom 'add to "
        f"cart' claim (got {bridge_prof.archetypes})"
    )
    print("  ok: reflow does not conjure a claim across a paragraph boundary — precision-safe")


def test_classification_is_html_entity_decode_invariant():
    # A readiness classification is a property of the VISIBLE words a storefront
    # renders, not the ENCODING a crawl captured. Real HTML joins the exact two-word
    # capability phrases a publisher will not let line-wrap with a non-breaking-space
    # entity ("Free&nbsp;shipping", "per&nbsp;month", "Add&nbsp;to&nbsp;cart") and
    # escapes ampersands/quotes/dashes ("&amp;", "&#39;", "&mdash;"). Left literal,
    # "Free&nbsp;shipping" is NOT the string "free shipping", so the many
    # literal-single-space signals ("free shipping", "add to cart", "per month",
    # "billed per <unit>") silently miss and the storefront is under-classified purely
    # on encoding. That is the sibling failure to the Cycle-178 line-wrap gap — from a
    # space that was ENCODED rather than WRAPPED — and strip_html now HTML-entity-decodes
    # as part of reducing a page to its VISIBLE prose. This pins the invariance: the
    # SAME storefront, capability phrases entity-joined vs literal-space, classifies
    # identically (claimed archetypes in rank order, the NA complement, and the
    # per-(label, surface) skeleton). It is the entity-decode analogue of the casing
    # (test_offering_canonical.py) and whitespace-reflow (above) axes.
    decoded = (
        "<!doctype html><html><body><p>"
        "Free shipping on every physical order. Add to cart when ready. "
        "Programmatic access is billed per call. Membership renews per month."
        "</p></body></html>"
    )
    encoded = (
        decoded.replace("Free shipping", "Free&nbsp;shipping")
        .replace("Add to cart", "Add&nbsp;to&nbsp;cart")
        .replace("billed per call", "billed&nbsp;per&nbsp;call")
        .replace("per month", "per&nbsp;month")
    )
    base = classify_offering("shop.test", {"homepage": decoded})
    ent = classify_offering("shop.test", {"homepage": encoded})

    # Substrate: the property under test is genuinely present — a RANKED multi-archetype
    # classification an encoding difference could perturb, over three literal-space
    # archetypes.
    assert {"physical_good", "metered_api", "subscription"} <= set(base.archetypes), (
        f"substrate: the three literal-space archetypes all claim on the decoded prose "
        f"(got {base.archetypes})"
    )

    # TEETH (a): the transform is REAL — the encoded bytes differ and carry the entity.
    assert encoded != decoded and "&nbsp;" in encoded, "the encoding genuinely changed the bytes (non-vacuous)"

    # TEETH (b): entity DECODING is LOAD-BEARING. A literal-space signal's raw pattern
    # matches the decoded phrase but NOT the entity-joined form, so without the decode
    # the encoded surface would drop the claim — the invariance below rests on
    # strip_html's unescape, not on the phrases surviving by luck. (physical_good's
    # free-shipping is authored with a literal single space.)
    fs_pat = _signal_pattern("physical_good", "free-shipping")
    assert fs_pat is not None, "free-shipping signal exists"
    assert fs_pat.search("free shipping") is not None, "free-shipping matches the literal-space form"
    assert fs_pat.search("free&nbsp;shipping") is None, (
        "free-shipping does NOT match the entity-joined form — so decoding is load-bearing"
    )

    # (1) The encoding-independent capability skeleton is identical: every archetype's
    # strength AND its per-(label, surface) match counts survive the entity encoding —
    # no signal lost or conjured, no count drifted, by mere &nbsp;-joining.
    assert _wsr_struct(ent) == _wsr_struct(base), (
        f"per-archetype (strength, per-(label, surface) counts) skeleton invariant under "
        f"HTML-entity encoding (decoded {_wsr_struct(base)}, encoded {_wsr_struct(ent)})"
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order, so encoding must not reorder the battery.
    assert ent.archetypes == base.archetypes, (
        f"claimed archetypes (ranked) invariant under HTML-entity encoding "
        f"(decoded {base.archetypes}, encoded {ent.archetypes})"
    )
    # (3) The NA/unclaimed complement (excluded from every mean/spread, never penalized)
    # is invariant — which archetypes a site is excused on as NA depends on what it
    # declares, not how a crawl encoded it.
    assert set(ent.unclaimed) == set(base.unclaimed), (
        f"NA/unclaimed set invariant under HTML-entity encoding "
        f"(decoded {sorted(base.unclaimed)}, encoded {sorted(ent.unclaimed)})"
    )
    print("  ok: claimed set / rank / strengths / labels / NA invariant under &nbsp; entity encoding (decode is load-bearing)")

    # TEETH (c): the negative control — entity DECODING must NOT conjure a claim from
    # entity-shaped noise. "Terms & conditions" / "Q & A" escape their ampersands as
    # "&amp;"; unescape rewrites them to "&", never to a signal word, so no archetype
    # is manufactured. Decoding repairs the encoded phrase WITHOUT inventing one.
    noise = (
        "<!doctype html><html><body><p>"
        "Terms &amp; conditions apply. Q &amp; A &mdash; read the FAQ. About &amp; contact."
        "</p></body></html>"
    )
    noise_prof = classify_offering("noise.test", {"homepage": noise})
    assert noise_prof.claimed == [], (
        f"entity decoding must not conjure a claim from &amp;/&mdash; noise (got {noise_prof.archetypes})"
    )
    print("  ok: entity decoding does not conjure a claim from &amp;/&mdash; noise — precision-safe")

    # REAL-EVIDENCE half: the fix runs NON-VACUOUSLY on committed canonical evidence.
    # Both canonical homepages carry a brand-logo marquee whose names are joined with
    # &nbsp; ("Arclight&nbsp;Goods", "VELA&nbsp;Studio"). strip_html must DECODE them
    # (so the marquee reads as visible prose) WITHOUT the decoded "Goods"/"Studio"
    # tokens conjuring physical_good — the canonical operator-acceptance NA — which is
    # exactly why decoding is safe on the canonical pair (guarded set-level in
    # test_offering_canonical.py; here we prove the decode genuinely fired on the raw
    # committed bytes).
    for domain in ("drift-flight.org", "driftflight.com"):
        path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
        raw = json.load(open(path))
        homepage = next(
            (e["result"].get("text", "") for e in raw["entries"]
             if e.get("url", "").rstrip("/").endswith(domain.replace("www.", ""))
             and isinstance(e.get("result"), dict) and "&nbsp;" in (e["result"].get("text") or "")),
            "",
        )
        assert "&nbsp;" in homepage, f"{domain}: committed homepage carries a raw &nbsp; (non-vacuous)"
        stripped = strip_html(homepage)
        assert "&nbsp;" not in stripped, f"{domain}: strip_html DECODED the committed &nbsp; (fix ran on real evidence)"
        # The decoded marquee reads as visible prose (brand names space-joined), and the
        # canonical NA is preserved: no physical_good conjured from "Goods"/"Studio".
        prof = classify_offering(domain, {"homepage": homepage})
        assert "physical_good" not in prof.archetypes, (
            f"{domain}: decoding the brand marquee must not conjure physical_good (canonical NA) "
            f"(got {prof.archetypes})"
        )
    print("  ok: committed canonical &nbsp; marquee is decoded on real evidence, physical_good stays NA")


def test_classification_is_non_html_surface_entity_invariant():
    # The sibling test above pins HTML-entity decoding on the HTML branch (a
    # "homepage"/HTML-document surface routed through strip_html, which unescapes as
    # part of reducing markup to visible prose). But a storefront's NON-HTML surfaces
    # — llms.txt, a JSON manifest / ai-plugin descriptor / A2A agent card / OpenAPI
    # spec — carry their capability prose DIRECTLY and never see strip_html, yet they
    # can STILL arrive entity-encoded: a framework HTML-escapes a JSON
    # `description`/`description_for_model` field, or an llms.txt was exported from an
    # HTML source, so a capability phrase's separators survive as "&nbsp;". Left
    # undecoded on the non-HTML branch, "add&nbsp;to&nbsp;cart" is NOT "add to cart"
    # and the literal-single-space signals silently miss — dropping the claim, and
    # with it the site's whole offering-relative battery, purely on the encoding of a
    # surface class the HTML-branch decode never touched. classify_offering now
    # unescapes the non-HTML branch too. This pins the invariance for that branch:
    # the SAME storefront, capability phrases entity-joined vs literal-space on an
    # llms.txt, classifies identically (claimed archetypes in rank order, the NA
    # complement, and the per-(label, surface) skeleton).
    flat = (
        "Store notes: we offer free shipping on every physical order. "
        "Add to cart when ready. Programmatic access is billed per call. "
        "Membership renews per month on each billing cycle."
    )
    base = classify_offering("shop.test", {"/llms.txt": flat})

    # Substrate: the property under test is genuinely present — a RANKED multi-archetype
    # classification an encoding difference could perturb, over three literal-space
    # archetypes.
    assert {"physical_good", "metered_api", "subscription"} <= set(base.archetypes), (
        f"substrate: the three literal-space archetypes all claim on the flat llms.txt "
        f"(got {base.archetypes})"
    )

    # An &nbsp;-encoding of exactly the two-word phrases a publisher will not let
    # line-wrap — the same encoding real HTML uses, but here on a plain-text surface.
    encoded = (
        flat.replace("free shipping", "free&nbsp;shipping")
        .replace("Add to cart", "Add&nbsp;to&nbsp;cart")
        .replace("billed per call", "billed&nbsp;per&nbsp;call")
        .replace("per month", "per&nbsp;month")
    )
    ent = classify_offering("shop.test", {"/llms.txt": encoded})

    # TEETH (a): the transform is REAL — the encoded bytes differ and carry the entity.
    assert encoded != flat and "&nbsp;" in encoded, "the encoding genuinely changed the bytes (non-vacuous)"

    # TEETH (b): this is the NON-HTML branch specifically — the surface is NOT an HTML
    # document, so the HTML-branch strip_html decode (the sibling test) never runs on
    # it, and the invariance rests entirely on the new non-HTML unescape. And that
    # decode is LOAD-BEARING: a literal-space signal's raw pattern matches the decoded
    # phrase but NOT the entity-joined form.
    assert offering._is_html_document(encoded) is False, (
        "the encoded llms.txt is NOT an HTML document — so it takes the non-HTML branch, "
        "and strip_html's decode does not cover it (this is the gap under test)"
    )
    fs_pat = _signal_pattern("physical_good", "free-shipping")
    assert fs_pat is not None, "free-shipping signal exists"
    assert fs_pat.search("free shipping") is not None, "free-shipping matches the literal-space form"
    assert fs_pat.search("free&nbsp;shipping") is None, (
        "free-shipping does NOT match the entity-joined form — so the non-HTML decode is load-bearing"
    )

    # (1) The encoding-independent capability skeleton is identical: every archetype's
    # strength AND its per-(label, surface) match counts survive the entity encoding —
    # no signal lost or conjured, no count drifted, by mere &nbsp;-joining.
    assert _wsr_struct(ent) == _wsr_struct(base), (
        f"per-archetype (strength, per-(label, surface) counts) skeleton invariant under "
        f"non-HTML-surface entity encoding (decoded {_wsr_struct(base)}, encoded {_wsr_struct(ent)})"
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order, so encoding must not reorder the battery.
    assert ent.archetypes == base.archetypes, (
        f"claimed archetypes (ranked) invariant under non-HTML-surface entity encoding "
        f"(decoded {base.archetypes}, encoded {ent.archetypes})"
    )
    # (3) The NA/unclaimed complement (excluded from every mean/spread, never penalized)
    # is invariant — which archetypes a site is excused on as NA depends on what it
    # declares, not how a crawl encoded it.
    assert set(ent.unclaimed) == set(base.unclaimed), (
        f"NA/unclaimed set invariant under non-HTML-surface entity encoding "
        f"(decoded {sorted(base.unclaimed)}, encoded {sorted(ent.unclaimed)})"
    )
    print("  ok: claimed set / rank / strengths / labels / NA invariant under &nbsp; on a non-HTML surface (non-HTML decode is load-bearing)")

    # TEETH (c): the negative control — decoding a non-HTML surface must NOT conjure a
    # claim from entity-shaped noise. "Terms & conditions" / "Q & A" escape their
    # ampersands as "&amp;"; unescape rewrites them to "&", never to a signal word, so
    # no archetype is manufactured. Decoding repairs the encoded phrase WITHOUT
    # inventing one.
    noise = "Terms &amp; conditions apply. Q &amp; A &mdash; read the FAQ. About &amp; contact."
    noise_prof = classify_offering("noise.test", {"/llms.txt": noise})
    assert noise_prof.claimed == [], (
        f"non-HTML entity decoding must not conjure a claim from &amp;/&mdash; noise (got {noise_prof.archetypes})"
    )
    print("  ok: non-HTML entity decoding does not conjure a claim from &amp;/&mdash; noise — precision-safe")

    # REAL-EVIDENCE half: the non-HTML decode is a NO-OP on committed canonical
    # evidence, so the canonical CLAIMED sets are invariant BY CONSTRUCTION. Every
    # non-HTML surface both canonical crawls fetched (llms.txt, JSON manifests, agent
    # cards, OpenAPI, ...) is byte-identical under html.unescape — none carries a
    # decodable entity — so extending the decode to the non-HTML branch cannot move a
    # canonical claim. This is the non-HTML-surface mirror of the em-dash exclusion
    # that keeps the hyphen fold a canonical no-op.
    import html as _html
    for domain in ("drift-flight.org", "driftflight.com"):
        path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
        raw = json.load(open(path))
        n_nonhtml = 0
        for e in raw["entries"]:
            result = e.get("result")
            if not isinstance(result, dict):
                continue
            body = result.get("text") or ""
            if not body or offering._is_html_document(body):
                continue
            n_nonhtml += 1
            assert _html.unescape(body) == body, (
                f"{domain}: non-HTML surface {e.get('url')!r} changes under unescape — "
                f"canonical invariance is no longer by construction"
            )
        assert n_nonhtml > 0, f"{domain}: committed evidence has non-HTML surfaces to check (non-vacuous)"
    print("  ok: every committed canonical non-HTML surface is unescape-identical — decode is a no-op there (invariant by construction)")


def test_classification_is_intra_word_hyphen_invariant():
    # A readiness classification is a property of the WORDS a storefront declares,
    # not the DASH GLYPH a crawl captured. Compound capability terms are routinely
    # joined with a NON-breaking or typographic hyphen rather than an ASCII
    # hyphen-minus — "pay‑as‑you‑go" (U+2011, the dash sibling of the &nbsp; a
    # publisher uses to keep the SAME compound off a line-wrap), "per‑generation"
    # (an en/figure dash from a word-processor autocorrect or a decoded &ndash;
    # entity). MANY signals — especially the billing-central metered_api bank —
    # match a LITERAL "[- ]" (ASCII hyphen or space) only, so such a term silently
    # misses and the WHOLE archetype claim is dropped on pure typography. That is
    # the encoding sibling of the Cycle-178 line-wrap (above) and the HTML-entity
    # (above) gaps, and classify_offering now folds the intra-word hyphen family
    # to ASCII "-" per-surface. This pins the invariance: the SAME storefront,
    # hyphenated compounds joined with a non-breaking hyphen vs an ASCII hyphen,
    # classifies identically (claimed archetypes in rank order, the NA complement,
    # and the per-(label, surface) skeleton).
    flat = (
        "Programmatic access is billed pay-as-you-go, charged pay-per-call at a low "
        "per-generation rate. A monthly subscription is available; subscribe any time."
    )
    base = classify_offering("shop.test", {"/llms.txt": flat})

    # Substrate: the property under test is genuinely present — a RANKED
    # multi-archetype classification a dash-glyph difference could perturb, led by
    # metered_api on THREE hyphenated-compound signals.
    assert {"metered_api", "subscription"} <= set(base.archetypes), (
        f"substrate: metered_api + subscription both claim on the ASCII-hyphen prose "
        f"(got {base.archetypes})"
    )
    assert base.archetypes[0] == "metered_api", (
        f"substrate: metered_api ranks first on its three hyphenated signals "
        f"(got {base.archetypes})"
    )

    # A non-breaking hyphen (U+2011) substituted for every ASCII hyphen — exactly
    # what a publisher types to keep "pay-as-you-go" off a line-wrap.
    nbh = flat.replace("-", "‑")
    hyph = classify_offering("shop.test", {"/llms.txt": nbh})

    # TEETH (a): the transform is REAL — the bytes differ and carry the U+2011.
    assert nbh != flat and "‑" in nbh, "the hyphen substitution genuinely changed the bytes (non-vacuous)"

    # TEETH (b): hyphen-FOLDING is LOAD-BEARING. A metered_api compound signal's raw
    # pattern matches the ASCII-hyphen form but NOT the non-breaking-hyphen form, so
    # without the fold the substituted surface would drop the claim — the invariance
    # below rests on classify_offering's dash normalization, not on the phrases
    # surviving by luck.
    pay_pat = _signal_pattern("metered_api", "pay-as-you-go")
    assert pay_pat is not None, "pay-as-you-go signal exists"
    assert pay_pat.search("pay-as-you-go") is not None, "pay-as-you-go matches the ASCII-hyphen form"
    assert pay_pat.search("pay‑as‑you‑go") is None, (
        "pay-as-you-go does NOT match the non-breaking-hyphen form — so folding is load-bearing"
    )

    # (1) The dash-independent capability skeleton is identical: every archetype's
    # strength AND its per-(label, surface) match counts survive the substitution —
    # no signal lost or conjured, no count drifted, by mere non-breaking-hyphen joining.
    assert _wsr_struct(hyph) == _wsr_struct(base), (
        f"per-archetype (strength, per-(label, surface) counts) skeleton invariant under "
        f"intra-word hyphen substitution (ASCII {_wsr_struct(base)}, nbhyphen {_wsr_struct(hyph)})"
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order, so a dash glyph must not reorder the battery.
    assert hyph.archetypes == base.archetypes, (
        f"claimed archetypes (ranked) invariant under intra-word hyphen substitution "
        f"(ASCII {base.archetypes}, nbhyphen {hyph.archetypes})"
    )
    # (3) The NA/unclaimed complement (excluded from every mean/spread, never penalized)
    # is invariant — which archetypes a site is excused on as NA depends on what it
    # declares, not the dash glyph a crawl captured.
    assert set(hyph.unclaimed) == set(base.unclaimed), (
        f"NA/unclaimed set invariant under intra-word hyphen substitution "
        f"(ASCII {sorted(base.unclaimed)}, nbhyphen {sorted(hyph.unclaimed)})"
    )
    print("  ok: claimed set / rank / strengths / labels / NA invariant under non-breaking-hyphen joining (fold is load-bearing)")

    # TEETH (c): the em dash (U+2014) is DELIBERATELY NOT folded — it is SENTENCE
    # punctuation, never an intra-word joiner. Substituting it for the ASCII hyphens
    # (an implausible-but-adversarial input) leaves the metered_api compounds broken,
    # so the metered_api claim DROPS and subscription becomes the rank-1 archetype.
    # This proves the fold is scoped to the intra-word hyphen family, not a blanket
    # dash-to-hyphen rewrite — the exact scoping that keeps the canonical pair, whose
    # only Unicode dash is a prose em dash, invariant by construction.
    emd = flat.replace("-", "—")
    emd_prof = classify_offering("shop.test", {"/llms.txt": emd})
    assert "metered_api" not in emd_prof.archetypes, (
        f"em dash is not folded, so the broken metered_api compounds do NOT claim "
        f"(got {emd_prof.archetypes})"
    )
    assert emd_prof.archetypes[0] != "metered_api", "em-dash input reorders away from metered_api"
    print("  ok: em dash is NOT folded (sentence punctuation, not a compound joiner) — precision-safe")

    # REAL-EVIDENCE half: the fold is a NO-OP on committed canonical evidence, so the
    # canonical CLAIMED sets are invariant BY CONSTRUCTION. Both canonical fixtures
    # carry Unicode dashes, but ONLY the em dash (U+2014, prose sentence breaks) —
    # which the fold deliberately excludes — and NONE of the intra-word hyphen family.
    INTRA_WORD = "‐‑‒–−﹣－"
    for domain in ("drift-flight.org", "driftflight.com"):
        path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
        raw = open(path, encoding="utf-8").read()
        present = {ch for ch in raw if ch in INTRA_WORD}
        assert not present, (
            f"{domain}: committed evidence carries an intra-word hyphen the fold WOULD rewrite "
            f"({[hex(ord(c)) for c in present]}) — canonical invariance is no longer by construction"
        )
        assert "—" in raw, f"{domain}: committed evidence carries the excluded em dash (non-vacuous)"
    print("  ok: committed canonical evidence carries only the excluded em dash — fold is a no-op there (invariant by construction)")


def test_classification_is_invisible_formatting_invariant():
    # A readiness classification is a property of the WORDS a storefront declares,
    # not the INVISIBLE line-break controls a CMS interleaved. A justification /
    # auto-hyphenation engine sprinkles zero-ink characters INSIDE a word or
    # compound — the soft hyphen U+00AD ("sub­scrip­tion"), the zero-width space
    # U+200B, the word joiner U+2060, the BOM / zero-width no-break space U+FEFF
    # (often a leading byte on an exported surface). A human sees the intact word,
    # but these are Unicode category Cf: `\s` does NOT match them (the reflow
    # collapse misses them) and they are not visible dashes (the hyphen fold misses
    # them), so mid-word they break a signal's \b/literal match and drop the WHOLE
    # archetype claim on ink-invisible typography — the encoding sibling of the
    # Cycle-178 line-wrap, the Cycle-214 hyphen, and the Cycle-218 entity gaps.
    # classify_offering now DELETES the invisible line-break family per-surface (see
    # _INVISIBLE_STRIP). This pins the invariance: the SAME storefront, capability
    # words interleaved with invisible break controls vs clean, classifies
    # identically (claimed archetypes in rank order, the NA complement, and the
    # per-(label, surface) skeleton).
    flat = (
        "Programmatic access is billed pay-as-you-go, charged pay-per-call at a low "
        "per-generation rate. A monthly subscription is available; subscribe any time."
    )
    base = classify_offering("shop.test", {"/llms.txt": flat})

    # Substrate: the property under test is genuinely present — a RANKED
    # multi-archetype classification an invisible-char difference could perturb,
    # led by metered_api on its hyphenated-compound signals.
    assert {"metered_api", "subscription"} <= set(base.archetypes), (
        f"substrate: metered_api + subscription both claim on the clean prose "
        f"(got {base.archetypes})"
    )
    assert base.archetypes[0] == "metered_api", (
        f"substrate: metered_api ranks first on its compound signals "
        f"(got {base.archetypes})"
    )

    # Invisible line-break controls interleaved inside the very words the signals
    # key on — one of EACH stripped char (soft hyphen, zero-width space, word
    # joiner) mid-compound, plus a leading BOM exactly as an exported surface
    # carries one.
    SHY, ZWSP, WJ, BOM = "­", "​", "⁠", "﻿"
    # Pin the (invisible) literals to their code points AND to the SUT's strip set,
    # so an editor that mangles a zero-ink glyph, or a change to _INVISIBLE_STRIP,
    # reddens here instead of silently weakening the test.
    assert [ord(c) for c in (SHY, ZWSP, WJ, BOM)] == [0x00AD, 0x200B, 0x2060, 0xFEFF]
    assert set(offering._INVISIBLE_STRIP) == {0x00AD, 0x200B, 0x2060, 0xFEFF}, (
        "test exercises exactly the chars _INVISIBLE_STRIP deletes"
    )
    inv = flat
    inv = inv.replace("pay-as-you-go", "pay-as-you-g" + SHY + "o")
    inv = inv.replace("pay-per-call", "pay-p" + ZWSP + "er-call")
    inv = inv.replace("per-generation", "per-gen" + WJ + "eration")
    inv = inv.replace("subscription", "sub" + SHY + "scrip" + ZWSP + "tion")
    inv = BOM + inv
    prof = classify_offering("shop.test", {"/llms.txt": inv})

    # TEETH (a): the transform is REAL — the bytes differ and carry all four
    # invisible controls the fold targets.
    assert inv != flat, "the invisible-char injection genuinely changed the bytes (non-vacuous)"
    assert all(ch in inv for ch in (SHY, ZWSP, WJ, BOM)), (
        "all four stripped invisible controls are present in the injected surface"
    )

    # TEETH (b): the STRIP is LOAD-BEARING. A signal's raw pattern matches the clean
    # word but NOT the zero-width-interrupted form, so without the strip the injected
    # surface would drop the claim — the invariance below rests on classify_offering's
    # invisible-char deletion, not on the phrases surviving by luck.
    sub_pat = _signal_pattern("subscription", "subscription")
    assert sub_pat is not None, "subscription signal exists"
    assert sub_pat.search("a subscription plan") is not None, "matches the clean word"
    assert sub_pat.search("a sub​scrip​tion plan") is None, (
        "does NOT match the zero-width-interrupted word — so the strip is load-bearing"
    )

    # (1) The invisible-char-independent capability skeleton is identical: every
    # archetype's strength AND its per-(label, surface) match counts survive — no
    # signal lost or conjured, no count drifted, by mere break-control interleaving.
    assert _wsr_struct(prof) == _wsr_struct(base), (
        f"per-archetype (strength, per-(label, surface) counts) skeleton invariant under "
        f"invisible-char interleaving (clean {_wsr_struct(base)}, injected {_wsr_struct(prof)})"
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order, so an invisible char must not reorder the battery.
    assert prof.archetypes == base.archetypes, (
        f"claimed archetypes (ranked) invariant under invisible-char interleaving "
        f"(clean {base.archetypes}, injected {prof.archetypes})"
    )
    # (3) The NA/unclaimed complement (excluded from every mean/spread, never
    # penalized) is invariant — what a site is excused on as NA depends on what it
    # declares, not the break controls a crawl captured.
    assert set(prof.unclaimed) == set(base.unclaimed), (
        f"NA/unclaimed set invariant under invisible-char interleaving "
        f"(clean {sorted(base.unclaimed)}, injected {sorted(prof.unclaimed)})"
    )
    print("  ok: claimed set / rank / strengths / labels / NA invariant under soft-hyphen/ZWSP/WJ/BOM interleaving (strip is load-bearing)")

    # TEETH (c): the zero-width non-joiner / joiner (U+200C / U+200D) are DELIBERATELY
    # NOT stripped — unlike the pure line-break controls above, they carry
    # grapheme-cluster / script semantics (Persian/Indic shaping, emoji ZWJ
    # sequences), so deleting them is not a safe no-op. Interleaving a ZWNJ into the
    # SAME metered_api compounds (an adversarial input) leaves them broken, so the
    # metered_api claim DROPS and it is no longer the rank-1 archetype. This proves
    # the strip is scoped to the pure line-break family, not a blanket zero-width
    # rewrite — the exact scoping (mirroring the hyphen fold's em-dash exclusion)
    # that keeps the canonical pair invariant by construction.
    ZWNJ = "‌"
    znj = flat
    znj = znj.replace("pay-as-you-go", "pay-as-you-g" + ZWNJ + "o")
    znj = znj.replace("pay-per-call", "pay-p" + ZWNJ + "er-call")
    znj = znj.replace("per-generation", "per-gen" + ZWNJ + "eration")
    znj_prof = classify_offering("shop.test", {"/llms.txt": znj})
    assert "metered_api" not in znj_prof.archetypes, (
        f"ZWNJ is not stripped, so the broken metered_api compounds do NOT claim "
        f"(got {znj_prof.archetypes})"
    )
    assert znj_prof.archetypes[0] != "metered_api", "ZWNJ input reorders away from metered_api"
    print("  ok: ZWNJ / ZWJ are NOT stripped (script/grapheme semantics, not line-break controls) — precision-safe")

    # REAL-EVIDENCE half: the strip is a classification NO-OP on every committed
    # canonical fixture. A fixture that carries NONE of the stripped chars is
    # invariant BY CONSTRUCTION (nothing to delete). A fixture that DOES carry one —
    # a genuine CMS/CDN artifact, e.g. the ZWSP a retail crawl captured INSIDE an
    # <img> filename on www.moleskine.com — is invariant BY VERIFICATION: classifying
    # it with the strip DISABLED (an empty str.translate table) yields the IDENTICAL
    # archetypes and NA complement, so deleting the char never moves a real canonical
    # claim. This is the real-evidence mirror of the synthetic invariance above
    # (harmlessness on an incidental invisible char; the phrase-RESCUE case — a
    # capability word itself broken mid-signal by an invisible control — is still
    # synthetic-only, [LOCAL] until a fixture carries one inside a signal).
    STRIPPED = "­​⁠﻿"
    verified = 0  # fixtures that carry a stripped char, checked by verification
    for name in sorted(os.listdir(_FIXTURE_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(_FIXTURE_DIR, name)
        raw = open(path, encoding="utf-8").read()
        present = {ch for ch in raw if ch in STRIPPED}
        if not present:
            continue  # invariant by construction — nothing for the strip to delete
        shipped = offering.discover_offering(FetchContext.from_fixture(path))
        _saved = offering._INVISIBLE_STRIP
        try:
            offering._INVISIBLE_STRIP = {}  # str.translate no-op == strip disabled
            unstripped = offering.discover_offering(FetchContext.from_fixture(path))
        finally:
            offering._INVISIBLE_STRIP = _saved
        assert (
            shipped.archetypes == unstripped.archetypes
            and set(shipped.unclaimed) == set(unstripped.unclaimed)
        ), (
            f"{name}: strip is NOT a no-op on real evidence carrying "
            f"{[hex(ord(c)) for c in present]} — classification moves "
            f"(shipped {shipped.archetypes}, strip-disabled {unstripped.archetypes})"
        )
        verified += 1
    assert verified >= 1, (
        "no committed fixture carries a stripped invisible char — the by-verification "
        "branch is vacuous; a real CMS/CDN surface must exercise it (see www.moleskine.com)"
    )
    print(f"  ok: strip is a classification no-op on all committed canonical evidence "
          f"({verified} char-carrying fixture(s) checked by verification, rest by construction)")


def test_evidence_is_quoted_and_surface_tagged():
    prof = classify_offering("example-imaging.test", {"homepage": API_HOMEPAGE})
    for claim in prof.claimed:
        for sig in claim.signals:
            assert sig.quote and sig.quote.strip(), f"empty quote for {sig.label}"
            assert sig.surface == "homepage"
            # HTML must be stripped — no raw tags leak into the evidence quote.
            assert "<" not in sig.quote and ">" not in sig.quote, sig.quote
    # to_dict round-trips and carries an auditable evidence block.
    d = prof.to_dict()
    assert d["evidence"]["claimed"][0]["labels"], d["evidence"]
    assert d["evidence"]["unclaimed"] == prof.unclaimed
    print("  ok: every claim carries a quoted, HTML-free, surface-tagged evidence snippet")


def test_openapi_spec_alone_classifies_api_first_storefront():
    # The coverage gap the OpenAPI surface closes: a storefront whose ONLY
    # machine-readable surface is its API spec (no llms.txt, no marketing
    # homepage). Before OpenAPI was a discovered surface such a site was
    # classified from its homepage alone and could be mis-read as offering
    # nothing. The spec's own summary/description carry the vendor-neutral
    # "inference API" / "pay-per-generation" / "generate an image" / x402 /
    # usage-based language the existing signal bank already anchors on.
    prof = classify_offering("northlight.test", {"/openapi.json": API_OPENAPI})
    assert prof.surfaces_seen == ["/openapi.json"], prof.surfaces_seen
    claimed = set(prof.archetypes)
    assert "metered_api" in claimed, prof.archetypes
    assert "digital_good" in claimed, prof.archetypes
    print(f"  ok: an OpenAPI-spec-only storefront is classified, got {prof.archetypes}")
    # Precision holds: a JSON API contract is NOT physical fulfillment or a
    # subscription (no "add to cart" / "$X per month" language in the spec).
    assert not prof.claims("physical_good"), prof.archetypes
    assert not prof.claims("subscription"), prof.archetypes
    # The metered_api claim rests on real anchored evidence from the spec surface.
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    assert all(s.surface == "/openapi.json" for s in metered.signals), metered.signals
    assert metered.strength >= 2, metered.strength
    print(f"  ok: metered_api rests on {metered.strength} distinct spec signals (x402/pay-per/qualified-api)")


def test_ai_plugin_descriptor_alone_classifies_storefront():
    # The coverage gap the agent-plugin descriptor closes: a storefront whose
    # agent-facing self-description is its `/.well-known/ai-plugin.json` manifest
    # (no marketing homepage, no llms.txt, no reachable OpenAPI spec). The
    # descriptor's `description_for_model` carries the vendor-neutral "inference
    # API" / "generate an image" / "pay-per-generation" / x402 / usage-based prose
    # the existing signal bank already anchors on — so the surface only had to be
    # read; it needs no new signal.
    prof = classify_offering(
        "northgale.test", {"/.well-known/ai-plugin.json": API_AI_PLUGIN}
    )
    assert prof.surfaces_seen == ["/.well-known/ai-plugin.json"], prof.surfaces_seen
    claimed = set(prof.archetypes)
    assert "metered_api" in claimed, prof.archetypes
    assert "digital_good" in claimed, prof.archetypes
    print(f"  ok: an ai-plugin-descriptor-only storefront is classified, got {prof.archetypes}")
    # Precision holds: a plugin manifest is NOT physical fulfillment (no
    # "add to cart" / stock language) nor a subscription (no "$X per month").
    assert not prof.claims("physical_good"), prof.archetypes
    assert not prof.claims("subscription"), prof.archetypes
    # The metered_api claim rests on real anchored evidence FROM the descriptor.
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    assert all(s.surface == "/.well-known/ai-plugin.json" for s in metered.signals), metered.signals
    assert metered.strength >= 2, metered.strength
    print(f"  ok: metered_api rests on {metered.strength} distinct descriptor signals (x402/pay-per/usage-based)")


def test_a2a_agent_card_alone_classifies_storefront():
    # The coverage gap the A2A agent card closes: an agent-native storefront whose
    # only self-description is its `/.well-known/agent.json` card (no marketing
    # homepage, no llms.txt, no OpenAPI spec, no ai-plugin descriptor). The card's
    # top-level `description` + per-skill descriptions carry the vendor-neutral
    # "enrich records" / "dataset" / "query" / "REST API" / "pay-per-request" / x402
    # / usage-based prose the existing signal bank already anchors on — so the
    # surface only had to be read; it needs no new signal.
    prof = classify_offering(
        "ledgerenrich.test", {"/.well-known/agent.json": DATA_AGENT_CARD}
    )
    assert prof.surfaces_seen == ["/.well-known/agent.json"], prof.surfaces_seen
    claimed = set(prof.archetypes)
    assert "metered_api" in claimed, prof.archetypes
    assert "data_retrieval" in claimed, prof.archetypes
    print(f"  ok: an agent-card-only storefront is classified, got {prof.archetypes}")
    # Precision holds: a data/API agent card is NOT physical fulfillment (no
    # "add to cart" / stock language), a subscription (no "$X per month"), or
    # digital media generation (no "generate an image" / render / translate).
    assert not prof.claims("physical_good"), prof.archetypes
    assert not prof.claims("subscription"), prof.archetypes
    assert not prof.claims("digital_good"), prof.archetypes
    assert not prof.claims("service_booking"), prof.archetypes
    # Both claims rest on real anchored evidence FROM the agent-card surface.
    for arch in ("metered_api", "data_retrieval"):
        claim = next(c for c in prof.claimed if c.archetype == arch)
        assert all(s.surface == "/.well-known/agent.json" for s in claim.signals), claim.signals
        assert claim.strength >= 2, (arch, claim.strength)
    print("  ok: metered_api + data_retrieval each rest on >=2 distinct card signals")


def test_html_docs_page_alone_classifies_storefront():
    # The coverage gap the /docs API-docs page closes: a storefront whose
    # agent-facing self-description is its rendered HTML documentation page (no
    # llms.txt, no reachable JSON well-known doc, a thin marketing homepage). The
    # page's endpoints / rate limits / per-generation billing prose is the same
    # vendor-neutral language the signal bank already anchors on — so the surface
    # only had to be READ and (being HTML) HTML-STRIPPED; it needs no new signal.
    prof = classify_offering("northpeak.test", {"/docs": DOCS_HTML})
    assert prof.surfaces_seen == ["/docs"], prof.surfaces_seen
    claimed = set(prof.archetypes)
    assert "metered_api" in claimed, prof.archetypes
    assert "digital_good" in claimed, prof.archetypes
    print(f"  ok: an HTML /docs-page-only storefront is classified, got {prof.archetypes}")
    # THE load-bearing guard: the /docs page is HTML-STRIPPED, so the <style>/
    # <script> retail decoy words ("out of stock" / "shopping cart" / "shipping
    # address") do NOT read as physical fulfillment. Scanned RAW they WOULD — this
    # is precisely why an HTML doc surface must be stripped, not read verbatim.
    assert not prof.claims("physical_good"), (
        "raw <script>/<style> retail decoys leaked as physical_good — /docs not stripped"
    )
    # Evidence is HTML-free: tags are stripped from the /docs surface, not only the
    # homepage (mirrors test_evidence_is_quoted_and_surface_tagged for a doc page).
    for c in prof.claimed:
        for s in c.signals:
            assert "<" not in s.quote and ">" not in s.quote, s.quote
    # The rate-limits section drove the metered_api rate-limited signal, from /docs.
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    m_labels = {s.label for s in metered.signals}
    assert "rate-limited" in m_labels, m_labels
    print("  ok: /docs is HTML-stripped — retail decoys stay NA, rate-limits drives metered_api")


def test_openapi_surface_is_wired_for_live_discovery():
    # A structural guard: the OpenAPI conventions, the agent-plugin descriptor, the
    # A2A agent card, AND the rendered HTML API-docs page are actually in the surface
    # list `discover_offering` fetches live (not merely handled by the pure
    # classifier). Without this, a spec-only / descriptor-only / agent-card-only /
    # docs-page-only site would never be READ. The natural-language docs remain
    # covered too (no regression to the surface set).
    docs = offering._SURFACE_DOCS
    for path in ("/openapi.json", "/.well-known/openapi.json", "/swagger.json"):
        assert path in docs, f"{path} missing from discovery surfaces: {docs}"
    assert "/.well-known/ai-plugin.json" in docs, f"ai-plugin descriptor missing: {docs}"
    for path in ("/.well-known/agent.json", "/.well-known/agent-card.json"):
        assert path in docs, f"A2A agent card {path} missing from discovery surfaces: {docs}"
    for path in ("/docs", "/api-docs", "/reference"):
        assert path in docs, f"HTML API-docs page {path} missing from discovery surfaces: {docs}"
    assert "/pricing" in docs, f"pricing/billing page missing from discovery surfaces: {docs}"
    for path in ("/llms.txt", "/llms-full.txt", "/manifest.json"):
        assert path in docs, f"regressed natural-language surface {path}: {docs}"
    print(f"  ok: OpenAPI/Swagger + ai-plugin + A2A agent-card + /docs + /pricing surfaces wired, got {docs}")


def test_strip_html_drops_script_style_and_tags():
    out = strip_html(API_HOMEPAGE)
    # The <script>/<style> commerce-word noise must NOT survive stripping — else
    # it would false-positive physical_good on this API site.
    assert "var s" not in out and "color:red" not in out, out[:200]
    assert "<" not in out and ">" not in out
    # Plain text passes through unchanged (llms.txt has no tags).
    assert strip_html("plain text, no tags") == "plain text, no tags"
    print("  ok: strip_html removes script/style/tags, passes plain text through")


def test_doc_subdomain_helper_is_precise_and_ssrf_safe():
    # The doc-subdomain expansion is constructed HERE from the site's own host, so
    # it must (a) attach the allowlisted subdomains to the REGISTRABLE host (www.
    # dropped), (b) never STACK a subdomain onto a host already on one (no
    # api.api.x.com), (c) stay entirely within the storefront's own registrable
    # domain (SSRF-safe — never an arbitrary host), and (d) label each surface
    # host-qualified so it can't overwrite an apex surface of the same path.
    surfaces_n = len(offering._SURFACE_DOCS)
    subs = set(offering._DOC_SUBDOMAINS)

    apex = offering._doc_subdomain_surfaces("https://driftflight.com")
    hosts = {label.split("/")[0] for label, _ in apex}
    assert hosts == {f"{s}.driftflight.com" for s in subs}, hosts
    assert len(apex) == len(subs) * surfaces_n, (len(apex), len(subs), surfaces_n)
    # (a) www. is dropped so the subdomain attaches to the registrable host.
    www = offering._doc_subdomain_surfaces("https://www.driftflight.com")
    assert {l.split("/")[0] for l, _ in www} == hosts, www
    # (c) every constructed URL is https and stays within the registrable domain —
    # nothing can point discovery at a third-party host.
    for label, url in apex:
        assert url.startswith("https://"), url
        host = url.split("://", 1)[1].split("/", 1)[0]
        assert host.endswith(".driftflight.com"), host
        # (d) host-qualified label, distinct from any bare apex path.
        assert label.startswith(host) and label not in offering._SURFACE_DOCS, label
    print(f"  ok: doc-subdomain expansion is registrable-host-only + host-qualified ({len(apex)} urls)")

    # (b) a host already ON an allowlisted subdomain does not stack it onto itself.
    onapi = offering._doc_subdomain_surfaces("https://api.replicate.com")
    onapi_hosts = {l.split("/")[0] for l, _ in onapi}
    assert "api.api.replicate.com" not in onapi_hosts, onapi_hosts
    assert onapi_hosts == {f"{s}.api.replicate.com" for s in subs if s != "api"}, onapi_hosts
    print("  ok: a host already on an allowlisted subdomain is not stacked (no api.api.*)")

    # A hostless / dotless base yields nothing to try (no bare-host expansion).
    assert offering._doc_subdomain_surfaces("") == []
    assert offering._doc_subdomain_surfaces("https://localhost") == []
    print("  ok: hostless / dotless base -> no subdomain surfaces")


def test_doc_subdomain_surfaces_are_read_live():
    # END-TO-END, on REAL captured bytes: discovery now reads the surface docs on
    # the storefront's conventional doc subdomains, not just its apex. The canonical
    # driftflight.com serves its rich agent docs (with credit-billing prose) at
    # agents.driftflight.com/llms-full.txt — a surface the apex crawl never reached.
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)

    # The doc-subdomain surface was READ (it is in surfaces_seen, host-qualified).
    assert "agents.driftflight.com/llms-full.txt" in prof.surfaces_seen, prof.surfaces_seen

    # NON-VACUOUS: `credit-metered` is present ONLY in the subdomain llms-full.txt
    # (the apex /llms.txt and the homepage do NOT carry it — the homepage's C2PA
    # 'credits' metadata is precision-guarded, see
    # test_credit_metered_fires_on_real_captured_billing_prose). So finding it in the
    # DISCOVERED profile proves the subdomain content actually reached classification
    # — before this surface was crawled, discovery could not have seen it.
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    cred = [s for s in metered.signals if s.label == "credit-metered"]
    assert cred, {s.label for s in metered.signals}
    assert cred[0].surface == "agents.driftflight.com/llms-full.txt", cred[0].surface
    assert "credit" in cred[0].quote.lower(), cred[0].quote
    print(f"  ok: doc-subdomain agent docs reach classification (credit-metered from {cred[0].surface})")

    # SCORE-NEUTRAL by construction: reading richer docs can only REINFORCE archetypes
    # the storefront already documents — the claimed SET is unchanged (the exact
    # regression the canonical offering guard pins). No new archetype, no false
    # physical_good/service_booking/data_retrieval from the extra prose.
    assert set(prof.archetypes) == {"metered_api", "subscription", "digital_good"}, prof.archetypes
    print("  ok: the richer doc-subdomain evidence does NOT change the claimed set (score-neutral)")


def test_docs_surface_is_read_live():
    # END-TO-END, on REAL captured bytes: discovery now reads the rendered HTML
    # API-docs page (/docs) added to _SURFACE_DOCS this cycle. The canonical
    # driftflight.com serves a `<h2 id="rate-limits">Rate limits</h2>` API-reference
    # at /docs — a surface the apex JSON-docs crawl never reached — and it is HTML,
    # so it is HTML-stripped before scanning.
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)

    # The /docs surface was READ (it is in surfaces_seen).
    assert "/docs" in prof.surfaces_seen, prof.surfaces_seen

    # NON-VACUOUS: the /docs page really did reach classification — its evidence
    # appears in the discovered profile (at least one signal is surface-tagged /docs),
    # and every /docs-sourced evidence quote is HTML-FREE (the page was stripped, not
    # scanned raw — so its <script>/<style> decoy words never entered evidence).
    docs_sigs = [s for c in prof.claimed for s in c.signals if s.surface == "/docs"]
    assert docs_sigs, "no /docs-sourced signal reached classification"
    for s in docs_sigs:
        assert "<" not in s.quote and ">" not in s.quote, s.quote
    print(f"  ok: /docs reaches classification, HTML-stripped ({len(docs_sigs)} signals)")

    # SCORE-NEUTRAL by construction: reading the richer /docs prose can only REINFORCE
    # archetypes the storefront already documents — the claimed SET AND ORDER are
    # unchanged (the exact regression the canonical offering guard pins). No new
    # archetype, no false physical_good from the docs page's retail decoy words.
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    assert not prof.claims("physical_good"), prof.archetypes
    print("  ok: /docs evidence does NOT change the claimed set/order (score-neutral)")


def test_agent_payment_rail_precision_synthetic():
    # Agentic commerce is standardizing on SEVERAL open payment/settlement rails an
    # agent can drive (x402, MPP, ACP, UCP, AP2), not just x402. The new
    # agent-payment-rail signal recognises them in two high-precision forms — a
    # structured `"protocol":"<rail>"` declaration, or a rail name paired with its
    # on-chain settlement asset — so a site advertising MULTIPLE rails is credited
    # for the "many payment rails" capability. Each POSITIVE is real agent-payment
    # prose that must fire the signal; each NEGATIVE is an acronym COLLISION that
    # must NOT (bare MPP/ACP/UCP/AP2 in an unrelated sense — the precision trap).
    positives = {
        "structured mpp": '{"protocol":"mpp","asset":"USDC"}',
        "structured acp": '"paymentProtocols":[{"protocol":"acp"}]',
        "structured ucp": 'config = {"protocol": "ucp", "network": "base"}',
        "structured ap2": '{"protocol":"ap2","asset":"USDC"}',
        "rail plus asset mpp": "Payment methods today are x402 (Base USDC) and MPP (Tempo USDC).",
        "rail plus asset ucp": "Settle via UCP (USDC) or the legacy card rail.",
    }
    for name, text in positives.items():
        prof = classify_offering("rails.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "agent-payment-rail" in labels, (name, labels)
    print(f"  ok: {len(positives)} agent-payment-rail phrasings each fire the signal")

    negatives = {
        "member of parliament": "Our MPP (Member of Parliament) endorsed the campaign.",
        "inflation index": "The UCP inflation index rose 2% last quarter.",
        "medical guideline": "Follow the ACP anesthesia guidelines during the procedure.",
        "exam code": "AP2 exam prep bundles ship in the fall catalog.",
        "wrong protocol value": 'The handshake used {"protocol":"tls"} for transport.',
        "bare x402 route": "The x402 route returns a friendly not-found page.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "agent-payment-rail" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} acronym-collision noise strings do NOT fire agent-payment-rail (precision)"
    )


def test_agent_payment_rail_fires_on_real_captured_surfaces():
    # END-TO-END, on REAL captured bytes: the canonical with-rails driftflight.com
    # advertises MORE than one open agent-native payment rail — its agent docs name
    # "x402 (Base USDC) and MPP (Tempo USDC)" and its manifest declares a structured
    # `"protocol":"x402"` paymentProtocols entry. Until this cycle the metered_api
    # bank recognised only the lone x402 token, so the MPP rail and the structured
    # multi-rail declaration were invisible to offering discovery.
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)

    # NON-VACUOUS: the new signal really fires on the real captured surfaces, and its
    # evidence is quoted + surface-tagged (auditable machine evidence, not a bare bool).
    rail_sigs = [
        s
        for c in prof.claimed
        if c.archetype == "metered_api"
        for s in c.signals
        if s.label == "agent-payment-rail"
    ]
    assert rail_sigs, "agent-payment-rail did not fire on driftflight.com's captured surfaces"
    for s in rail_sigs:
        assert s.quote, s
    print(
        f"  ok: agent-payment-rail fires on {len({s.surface for s in rail_sigs})} real surface(s) "
        f"({len(rail_sigs)} signal(s))"
    )

    # SCORE-NEUTRAL by construction AND re-measured: the with-rails side ALREADY claims
    # metered_api (its strongest claim), so recognising an additional rail can only
    # REINFORCE it — the claimed SET AND ORDER are unchanged (the exact regression the
    # canonical offering guard pins). Discovery is off the scoring path, so the overall
    # score and the canonical delta are untouched.
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes


def test_no_rails_side_claims_no_agent_payment_rail():
    # The capability CONTRAST that makes the signal meaningful: the no-rails
    # drift-flight.org serves the SAME product docs but advertises NO agent-native
    # payment rail — so the agent-payment-rail signal must NOT fire on it (nor on the
    # retail / control / machine-surface fixtures). This is the offering-layer mirror
    # of the scoring-path x402 delta: with-rails has an agent-payable rail, no-rails
    # does not. A false fire here would erase that contrast.
    for dom in (
        "drift-flight.org.json",
        "example.com.json",
        "books.toscrape.com.json",
        "api.replicate.com.json",
    ):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, dom))
        prof = offering.discover_offering(ctx)
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "agent-payment-rail" not in labels, (dom, labels, prof.archetypes)
    print("  ok: agent-payment-rail fires on ZERO no-rails/retail/control/machine fixtures")


def test_pricing_surface_is_read_live():
    # END-TO-END, on REAL captured bytes: discovery now reads the rendered HTML
    # PRICING page (/pricing) added to _SURFACE_DOCS this cycle — the "understand
    # the offer" BILLING surface where a storefront states how it charges. The
    # canonical driftflight.com serves a real 200 /pricing page (per-month /
    # per-generation / usage-based billing prose); it is HTML, so it is HTML-stripped
    # before scanning. NON-VACUOUS unlike a 404-absent surface: /pricing genuinely
    # reaches classification here.
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)

    # The /pricing surface was READ (it is in surfaces_seen) — a real 200, not absent.
    assert "/pricing" in prof.surfaces_seen, prof.surfaces_seen

    # NON-VACUOUS: the /pricing page really did reach classification — its evidence
    # appears in the discovered profile (at least one signal is surface-tagged
    # /pricing), and every /pricing-sourced evidence quote is HTML-FREE (the page was
    # stripped, not scanned raw — so its <script>/<style> decoy words never entered
    # evidence).
    pricing_sigs = [s for c in prof.claimed for s in c.signals if s.surface == "/pricing"]
    assert pricing_sigs, "no /pricing-sourced signal reached classification"
    for s in pricing_sigs:
        assert "<" not in s.quote and ">" not in s.quote, s.quote
    print(f"  ok: /pricing reaches classification, HTML-stripped ({len(pricing_sigs)} signals)")

    # The billing prose reinforces the BILLING archetypes — metered_api and
    # subscription both carry a /pricing-sourced signal (this is the recall the
    # surface adds: a site that documents its billing only on /pricing is no longer
    # under-classified).
    pricing_archetypes = {s.archetype for s in pricing_sigs}
    assert {"metered_api", "subscription"} <= pricing_archetypes, pricing_archetypes

    # SCORE-NEUTRAL by construction AND re-measured: reading the richer /pricing prose
    # can only REINFORCE archetypes the storefront already documents — the claimed SET
    # AND ORDER are unchanged (the exact regression the canonical offering guard pins).
    # No new archetype, no false physical_good from the pricing page's decoy words.
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    assert not prof.claims("physical_good"), prof.archetypes
    print("  ok: /pricing evidence does NOT change the claimed set/order (score-neutral)")


def test_async_job_metering_precision_synthetic():
    # An asynchronous long-running job — submit, then retrieve the result via a
    # webhook callback or by polling a status endpoint — is the defining contract of
    # an agent-native API whose work does not finish in the request/response
    # round-trip (image/video generation, a training run, a batch job). It is the
    # "complete the job" capability, so it must claim metered_api via the new
    # async-job signal. Each POSITIVE is real async/webhook/poll API vocabulary; each
    # NEGATIVE is poll/async-SHAPED noise that must NOT fire it (the precision traps:
    # an opinion poll, a polling place, a reader poll, a bare "async is nice").
    positives = {
        "receive a webhook": "An HTTPS URL for receiving a webhook when the render is ready.",
        "webhook url": "Configure a webhook URL to be notified when the job completes.",
        "webhook notifications": "We send webhook notifications for every prediction event.",
        "poll the endpoint": "Or poll the get-a-prediction endpoint until it finishes.",
        "poll for result": "Submit the job, then poll for the result every few seconds.",
        "poll until": "Long jobs run in the background; polling until complete is fine.",
        "async prediction": "Start an asynchronous prediction endpoint for batch work.",
        "async job": "Every request is an async job with an id you fetch later.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "async-job" in labels, (name, labels)
    print(f"  ok: {len(positives)} real async/webhook/poll phrasings each fire async-job")

    negatives = {
        "opinion poll": "The latest opinion poll shows renewed optimism this quarter.",
        "polling place": "Head to your polling place before 8pm to cast your vote.",
        "poll results": "Reader poll results were released on the blog this morning.",
        "reader poll": "Take our reader poll and tell us which cover you prefer.",
        "bare async": "The async workflow of our design team is honestly a joy.",
        "webhook-free": "A webhook-free integration is not something we offer today.",
        "retail cart": "Add to cart, then check out — free shipping on every order.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "async-job" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} poll/async-shaped noise strings do NOT fire async-job (precision)"
    )


def test_async_job_fires_on_real_captured_openapi():
    # Real-evidence, NON-VACUOUS, END-TO-END: the async-job signal fires on the
    # GENUINE async-prediction contract captured live from a real machine-surface
    # storefront — api.replicate.com's /openapi.json documents a `webhook` field ("An
    # HTTPS URL for receiving a webhook when the prediction has new output") and a
    # `poll the ... endpoint` flow, captured verbatim in the committed fixture. Run the
    # REAL discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would, the same real-data non-vacuity move
    # test_agent_payment_rail_fires_on_real_captured_surfaces makes.
    #
    # SCORE-NEUTRAL by construction: api.replicate.com already claims ONLY metered_api
    # (its strongest and only archetype), so an async contract on its spec can only
    # deepen that claim's evidence — never add an archetype or reorder. The classifier
    # is off the scoring path; the canonical pair (which does NOT document an async
    # flow) is unchanged (async-job fires on neither driftflight surface — pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    openapi = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "webhook" in openapi.lower(), "fixture /openapi.json lost its webhook contract"

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "api.replicate.com.json"))
    prof = offering.discover_offering(ctx)

    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    aj = [s for s in metered.signals if s.label == "async-job"]
    assert aj, {s.label for s in metered.signals}
    quote = aj[0].quote.lower()
    assert "webhook" in quote or "poll" in quote or "async" in quote, aj[0].quote
    print(f"  ok: async-job fires on REAL captured OpenAPI contract — quote: {aj[0].quote!r}")

    # NON-VACUOUS + score-neutral: the machine storefront's claimed SET is exactly
    # [metered_api] — the async contract deepened the metered_api evidence without
    # adding a spurious archetype (no false digital_good/service_booking from "render"
    # or "training" prose reaching a wrong bank).
    assert prof.archetypes == ["metered_api"], prof.archetypes
    print("  ok: async-job evidence does NOT change the claimed set (score-neutral)")


def test_api_auth_precision_synthetic():
    # Programmatic AUTHENTICATION / credential provisioning — HOW an agent obtains
    # and presents credentials to call an API (an API key sent as a Bearer token, an
    # OAuth2 flow, an X-API-Key header, a declared OpenAPI securityScheme) — is the
    # "provision without a human" capability at the offering layer: an agent that
    # cannot read the auth scheme cannot invoke the API at all, so it claims
    # metered_api via the new api-auth signal. Each POSITIVE is real, vendor-neutral
    # auth vocabulary; each NEGATIVE is auth-SHAPED noise that must NOT fire it (the
    # precision traps: a retail LOGIN, "the bearer of ...", a house key, a turnkey
    # solution, an "OAuthenticate" typo).
    positives = {
        "auth header": "POST https://x.test/v1/images/generate Authorization: Bearer df_live_4kq2",
        "api key prose": "Sign up on the dashboard for an API key; usage bills monthly.",
        "authenticated with": "Requests are authenticated with an API key sent as a Bearer token.",
        "bearer token": "Send your credential as a Bearer token in the request header.",
        "openapi securityschemes": '"securitySchemes":{"bearerAuth":{"bearerFormat":"JWT"}}',
        "apikey scheme": '"type":"apiKey","in":"header","name":"X-Api-Key"',
        "x-api-key header": "Pass credentials in the X-API-Key request header.",
        "oauth2": "Authenticate the agent with an OAuth 2.0 client-credentials flow.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "api-auth" in labels, (name, labels)
    print(f"  ok: {len(positives)} real API-auth phrasings each fire api-auth")

    negatives = {
        "retail login": "Authenticate your account at checkout to see your saved bag.",
        "bearer of news": "The courier was the bearer of the invitation to the gala.",
        "house key": "Leave the spare key with a neighbor; free shipping on all locks.",
        "keychain": "Our leather keychain holds up to five keys in style.",
        "oauthenticate typo": "Please OAuthenticate soon (bad marketing copy).",
        "turnkey": "Turnkey solutions for your whole team, no api involved.",
        "retail cart": "Add to cart, then check out — free shipping on every order.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "api-auth" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} auth-shaped noise strings do NOT fire api-auth (precision)"
    )


def test_api_auth_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the api-auth signal fires on the
    # GENUINE authentication contracts captured live from the real metered_api
    # storefronts — the canonical pair documents `Authorization: Bearer <token>` on
    # its homepage and "authenticated with an API key sent as a Bearer token" on
    # /docs, and api.replicate.com's /openapi.json declares a `securitySchemes`
    # bearer scheme — all captured verbatim in the committed fixtures. Run the REAL
    # discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would, the same real-data non-vacuity move
    # test_async_job_fires_on_real_captured_openapi makes.
    #
    # SCORE-NEUTRAL by construction: every domain where api-auth fires ALREADY
    # claims metered_api (its strongest archetype on all three), so an auth scheme
    # can only deepen that claim's evidence — never add an archetype or reorder. The
    # classifier is off the scoring path; the canonical pair's claimed SET+ORDER is
    # unchanged (pinned by tests/test_offering_canonical.py and the replay guard).
    for domain in ("driftflight.com", "drift-flight.org", "api.replicate.com"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.claims("metered_api"), (domain, prof.archetypes)
        metered = next(c for c in prof.claimed if c.archetype == "metered_api")
        auth = [s for s in metered.signals if s.label == "api-auth"]
        assert auth, (domain, {s.label for s in metered.signals})
        q = auth[0].quote.lower()
        assert (
            "bearer" in q or "api key" in q or "apikey" in q or "securityscheme" in q
            or "x-api-key" in q or "oauth" in q
        ), (domain, auth[0].quote)
    print("  ok: api-auth fires on REAL captured auth contracts (both canonical domains + machine surface)")

    # NON-VACUOUS negative: a real retail storefront (books.toscrape.com) documents
    # NO API auth — api-auth must be absent there, so it is a metered-API signal, not
    # a match-anything token. (This is the offering-layer mirror of the scoring-path
    # asymmetry: agent-callable API sites document auth, a browser-only shop does not.)
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "books.toscrape.com.json"))
    retail = offering.discover_offering(ctx)
    assert retail.archetypes == ["physical_good"], retail.archetypes
    all_labels = {s.label for c in retail.claimed for s in c.signals}
    assert "api-auth" not in all_labels, all_labels
    print("  ok: api-auth is ABSENT on a real no-API retail storefront (non-vacuous)")


def test_error_contract_precision_synthetic():
    # A documented ERROR CONTRACT — the machine-readable 4xx/5xx error responses an
    # agent must handle to recover from a failed call (refresh a credential on a 401,
    # back off and retry on a 429, surface a clear failure on a 4xx/5xx) — is the
    # "complete the job" reliability capability at the offering layer: an agent that
    # cannot read the error contract cannot recover autonomously, so it claims
    # metered_api via the new error-contract signal. Each POSITIVE is real,
    # vendor-neutral error-documentation vocabulary (an OpenAPI status-keyed response
    # object, RFC 7807 problem+json, a status code paired with a snake_case error
    # code); each NEGATIVE is number-SHAPED noise that must NOT fire it (the precision
    # traps: a quantity, a price, a phone/room number, a success status).
    positives = {
        "openapi 429 response": '"429":{"description":"Plan generation allowance exceeded"}',
        "openapi 401 response": '"401":{"description":"Missing or invalid API key"}',
        "openapi 404 content": '"404":{"content":{"application/json":{"schema":{}}}}',
        "problem+json": "On error the endpoint returns application/problem+json with details.",
        "error table": "Errors Status Code Meaning 400 invalid_request Missing field",
        "allowance code": "429 allowance_exhausted Monthly generation allowance used up.",
        "server error code": "502 generation_failed The render did not complete; retry.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "error-contract" in labels, (name, labels)
    print(f"  ok: {len(positives)} real error-contract phrasings each fire error-contract")

    negatives = {
        "quantity": "Across a 500-image catalog run we measure the drift.",
        "throughput quantity": "We processed 500 images and 429 renders today.",
        "price": "The pro plan is $499 per year, billed once.",
        "phone number": "Call 411 for support anytime, day or night.",
        "room number": "Meet us in room 404 down the hall for a demo.",
        "success status": "Every call returns HTTP 200 OK on success.",
        "rate limit prose": "You may send 429 requests per minute on this plan.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "error-contract" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} number-shaped noise strings do NOT fire error-contract (precision)"
    )


def test_error_contract_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the error-contract signal fires on the
    # GENUINE machine-readable error documentation captured live from the real
    # metered_api storefronts — the canonical pair documents a `Status Code Meaning`
    # error table on /docs (400 invalid_request, 401 unauthorized, 429
    # allowance_exhausted, 502 generation_failed) and status-keyed 401/429 response
    # objects in its OpenAPI spec, and api.replicate.com's /openapi.json returns RFC
    # 7807 `application/problem+json` 4xx responses — all captured verbatim in the
    # committed fixtures. Run the REAL discovery path (from_fixture ->
    # discover_offering) so the signal is exercised exactly as a live crawl would, the
    # same real-data non-vacuity move test_api_auth_fires_on_real_captured_surfaces
    # makes.
    #
    # SCORE-NEUTRAL by construction: every domain where error-contract fires ALREADY
    # claims metered_api (its strongest archetype on all three), so a documented error
    # contract can only deepen that claim's evidence — never add an archetype or
    # reorder. The classifier is off the scoring path; the canonical pair's claimed
    # SET+ORDER is unchanged (pinned by tests/test_offering_canonical.py and the
    # replay guard).
    for domain in ("driftflight.com", "drift-flight.org", "api.replicate.com"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.claims("metered_api"), (domain, prof.archetypes)
        metered = next(c for c in prof.claimed if c.archetype == "metered_api")
        err = [s for s in metered.signals if s.label == "error-contract"]
        assert err, (domain, {s.label for s in metered.signals})
        q = err[0].quote.lower()
        # The matched evidence is a real error-contract form: a status-keyed response
        # object, the RFC 7807 media type, or a status code + snake_case error code.
        assert (
            "problem+json" in q
            or re.search(r'"(?:4\d\d|5\d\d)"\s*:\s*\{', q)
            or re.search(r"\b(?:4\d\d|5\d\d)\s+[a-z][a-z0-9]*_[a-z0-9_]+", q)
        ), (domain, err[0].quote)
    print("  ok: error-contract fires on REAL captured error docs (both canonical domains + machine surface)")

    # NON-VACUOUS negative: a real retail storefront (books.toscrape.com) documents
    # NO machine-readable error contract — error-contract must be absent there, so it
    # is a metered-API signal, not a match-anything token. (Offering-layer mirror of
    # the scoring-path asymmetry: an agent-callable API documents its errors, a
    # browser-only shop does not.)
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "books.toscrape.com.json"))
    retail = offering.discover_offering(ctx)
    assert retail.archetypes == ["physical_good"], retail.archetypes
    all_labels = {s.label for c in retail.claimed for s in c.signals}
    assert "error-contract" not in all_labels, all_labels
    print("  ok: error-contract is ABSENT on a real no-API retail storefront (non-vacuous)")


def test_generate_media_recognizes_plural_and_participle_forms():
    # The generate-media digital_good signal is the core "the service GENERATES a
    # media deliverable" claim. It previously matched ONLY the singular imperative
    # form ("generate an image"); the inflected verb ("generating", "generates",
    # "generated") and the PLURAL media noun ("generate videos", "Generated images")
    # were invisible to it. Each POSITIVE below is a real, common generation phrasing
    # that must now fire generate-media; each NEGATIVE is generate-shaped noise that
    # must NOT (a non-media object, or a "generat" substring inside another word).
    # The verb must still be `generat...` at a word boundary and the object one of
    # the vendor-neutral media nouns at a word boundary.
    old = re.compile(r"\bgenerate(s|d)?\s+(an?\s+)?(image|video|audio|art)\b", re.IGNORECASE)

    positives = {
        "plural imperative": "We generate videos for your storefront on demand.",
        "participle plural": "Our GPUs are busy generating images right now.",
        "participle singular": "The endpoint returns while generating an image.",
        "past-tense plural": "Generated images remain hosted for 90 days.",
        "possessive object": "Generate your art directly from a text prompt.",
        "definite object": "Generate the audio track from a script, programmatically.",
        "plural audio": "The API generates audio clips per request.",
    }
    for name, text in positives.items():
        prof = classify_offering("gen.test", {"homepage": text})
        assert prof.claims("digital_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "digital_good"
            for s in c.signals
        }
        assert "generate-media" in labels, (name, labels)
    print(f"  ok: {len(positives)} inflected/plural generation phrasings each fire generate-media")

    negatives = {
        "non-media object": "We generate reports and generate revenue every quarter.",
        "generic output": "Call the endpoint to generate output as JSON.",
        "response noun": "The model will generate a response to your prompt.",
        "regenerate token": "Rotate the key: regenerate a token from the dashboard.",
        "imagery (no boundary)": "The prompt can generate imagery of any style.",
        "smart-not-art": "Generate a smart summary of the document.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "generate-media" not in labels, (name, labels, prof.archetypes)
    print(f"  ok: {len(negatives)} generate-shaped noise strings do NOT fire generate-media (precision)")

    # NON-VACUOUS: the broadening does real work. A surface that carries ONLY the
    # plural/participle form — and NO other digital_good signal (no "generation(s)",
    # no "render", no "hosted URL") — would have claimed NOTHING under the old
    # singular-only pattern; it now correctly claims digital_good. Proven by
    # confirming the OLD pattern misses the very text the new signal fires on, so a
    # real generation storefront using plural/participle copy is no longer
    # under-classified to no archetype at all.
    plural_only = "We generate videos and stream generated images to agents on demand."
    assert old.search(plural_only) is None, "guard vacuous: old pattern already matched the plural form"
    prof = classify_offering("plural.test", {"homepage": plural_only})
    assert prof.archetypes == ["digital_good"], prof.archetypes
    dg_labels = {s.label for c in prof.claimed for s in c.signals}
    assert dg_labels == {"generate-media"}, dg_labels
    print("  ok: a plural/participle-only surface now claims digital_good via generate-media (old pattern: NO match)")


def test_generate_media_plural_gap_on_real_captured_docs():
    # Real-evidence, NON-VACUOUS anchor: the recall gap was real on CAPTURED bytes,
    # not just synthetic. Both canonical /docs pages carry the plural "Generated
    # images" (captured verbatim in the committed fixtures) — a media-generation
    # claim the OLD singular-only generate-media pattern could not match. The
    # broadened pattern matches it; the old one does not. (The canonical pages ALSO
    # carry the singular "Generate an image" earlier in the same surface, so this
    # deepens generate-media's recall without changing the claimed SET, ORDER, or the
    # first-match evidence quote — score-neutrality is pinned byte-for-byte by
    # tests/test_offering_canonical.py and the classification is off the scoring path.)
    old = re.compile(r"\bgenerate(s|d)?\s+(an?\s+)?(image|video|audio|art)\b", re.IGNORECASE)
    new = dict(offering._SIGNALS["digital_good"])["generate-media"]
    seen = 0
    for domain in ("driftflight.com", "drift-flight.org"):
        docs = _fixture_entry_text(domain, "/docs")
        prose = strip_html(docs)
        assert "Generated images" in prose, (domain, "fixture /docs lost its plural media prose")
        # Isolate the plural claim (drop the singular that also appears on the page)
        # to prove the broadening — not the pre-existing singular — is what matches it.
        idx = prose.index("Generated images")
        window = prose[idx: idx + len("Generated images")]
        assert new.search(window), (domain, window)
        assert old.search(window) is None, (domain, "old pattern unexpectedly matched the plural form")
        seen += 1
    assert seen == 2
    print("  ok: the canonical /docs plural 'Generated images' fires the broadened generate-media (old: NO match)")


def test_output_license_precision_synthetic():
    # Output USAGE-RIGHTS / license — the "complete the job" RIGHTS leg of a digital
    # good (the agent obtains a deliverable it may actually USE). Bare
    # "license"/"licensed" is a false-positive minefield, so each POSITIVE is a real
    # deliverable-rights grant that must claim digital_good via the new output-license
    # signal; each NEGATIVE is license-shaped noise — a SOFTWARE licence, a hosted
    # MODEL's licence, "models you own", a driver's/business licence, a "Licensed and
    # credentialed" trust badge — that must NOT fire output-license. The model-license
    # and "models you own" negatives are the exact traps present in the committed
    # api.replicate.com fixture (a metered_api-ONLY storefront that must not gain
    # digital_good).
    positives = {
        "commercial licence (en)": "Every paid render carries a commercial licence.",
        "commercial license (us)": "Each generation ships with a commercial license.",
        "commercial licensing": "Hosted output URLs, style presets, and commercial licensing.",
        "royalty-free": "All outputs are royalty-free for commercial use.",
        "usage rights": "You receive full usage rights to every image you generate.",
        "you own the output": "No attribution required — you own the output.",
        "you own the renders": "Cancel anytime; you own the renders you create.",
    }
    for name, text in positives.items():
        prof = classify_offering("gen.test", {"homepage": text})
        assert prof.claims("digital_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "digital_good"
            for s in c.signals
        }
        assert "output-license" in labels, (name, labels)
    print(f"  ok: {len(positives)} real deliverable-rights grants each fire output-license")

    negatives = {
        "software licence (MIT)": "This project is released under the MIT license.",
        "model's licence": "Check the model's license before you deploy it.",
        "models you own": "You can only delete models you own.",
        "driver's licence": "Upload a photo of your driver's license to verify your identity.",
        "business licence": "We hold a valid business license in every state we operate.",
        "trust badge": "Licensed and credentialed operators only.",
        "royalty (not free)": "Contributors receive a royalty on every sale.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "output-license" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} license-shaped noise strings do NOT fire output-license (precision)"
    )


def test_output_license_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS validation of output-license — it fires on GENUINE
    # deliverable-rights prose captured live from a real generation storefront, and
    # does NOT fire on a DIFFERENT real storefront's model-license / "models you own"
    # trap.
    #
    # driftflight.com grants a commercial licence on its output: its committed
    # /llms.txt says "hosted output URLs, style presets, and commercial licensing";
    # discover_offering reads that surface (see test_doc_subdomain_surfaces_are_read_live),
    # and both canonical homepages carry "commercial licence on every image" /
    # "you own the output". The storefront already claims digital_good, so this
    # DEEPENS its evidence without changing the claimed set (score-neutrality pinned
    # byte-for-byte by tests/test_offering_canonical.py; classification is off the
    # scoring path).
    billing = _fixture_entry_text("driftflight.com", "/llms.txt")
    assert "commercial licensing" in billing.lower(), "fixture /llms.txt lost its licensing prose"
    prof = classify_offering("driftflight.com", {"/llms.txt": billing})
    assert prof.claims("digital_good"), prof.archetypes
    dg = next(c for c in prof.claimed if c.archetype == "digital_good")
    lic = [s for s in dg.signals if s.label == "output-license"]
    assert lic, {s.label for s in dg.signals}
    assert "licen" in lic[0].quote.lower(), lic[0].quote
    print(f"  ok: output-license fires on REAL captured licensing prose — quote: {lic[0].quote!r}")

    # Precision on real noise: api.replicate.com — a metered_api-ONLY storefront
    # (pinned by test_machine_surface_openapi_storefront) — carries BOTH license traps
    # in its committed OpenAPI spec: "the model's license" (a hosted MODEL's licence,
    # not the deliverable's) and "delete models you own" (ownership of MODELS, not
    # output). Neither is a usage-rights grant on a produced deliverable, so
    # output-license must NOT fire — the spec must not gain a spurious digital_good.
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "model's license" in spec and "models you own" in spec, "fixture lost its license traps"
    spec_prof = classify_offering("api.replicate.com", {"/openapi.json": spec})
    spec_labels = {s.label for c in spec_prof.claimed for s in c.signals}
    assert "output-license" not in spec_labels, spec_labels
    assert not spec_prof.claims("digital_good"), spec_prof.archetypes
    print("  ok: the model-license / 'models you own' traps do NOT fire output-license (real-data precision)")


def test_content_provenance_precision_synthetic():
    # Output CONTENT-PROVENANCE is the "verify + trust the deliverable" leg of a
    # digital good — the trust/authenticity mirror of output-license (which grants the
    # RIGHT to use; this grants the MEANS to trust). An agent that can provenance-check
    # a generated asset (embedded C2PA content credentials, a provenance manifest /
    # metadata record) can use it in a provenance-aware pipeline, so it must claim
    # digital_good via the new content-provenance signal. Each POSITIVE is real
    # provenance vocabulary; each NEGATIVE is provenance-SHAPED noise that must NOT fire
    # it (the precision traps: art / wine / supply-chain provenance, "data provenance"
    # for a data service, and the "watermarking for provenance" MODEL-FEATURE phrasing
    # on a metered-API marketplace).
    positives = {
        "c2pa": "Every render ships with embedded C2PA metadata for authenticity.",
        "content credentials": "Each image carries Content Credentials so you can verify its origin.",
        "content credential singular": "A content credential is embedded in every export.",
        "image provenance": "We attach image provenance to each generated asset.",
        "output provenance": "The output provenance travels with the file downstream.",
        "render provenance": "Render provenance is baked into every delivered frame.",
        "provenance metadata": "Provenance metadata records how the image was produced.",
        "provenance manifest": "A provenance manifest accompanies each generation.",
        "records provenance": "Embedded credentials record provenance without limiting your rights.",
    }
    for name, text in positives.items():
        prof = classify_offering("studio.test", {"homepage": text})
        assert prof.claims("digital_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "digital_good"
            for s in c.signals
        }
        assert "content-provenance" in labels, (name, labels)
    print(f"  ok: {len(positives)} real content-provenance phrasings each fire content-provenance")

    negatives = {
        "art provenance": "The painting's provenance traces back to a 1920s collector.",
        "wine provenance": "We document the provenance of every bottle in the cellar.",
        "supply-chain provenance": "Blockchain gives full provenance across the supply chain.",
        "data provenance": "Our pipeline tracks data provenance for every record.",
        "watermark-for-provenance model": "The model embeds invisible watermarking for provenance on all generated images.",
        "bare credentials": "Authenticate with the credentials issued to your account.",
        "bare content": "This content is available in several languages.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "content-provenance" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} provenance-shaped noise strings do NOT fire content-provenance (precision)"
    )


def test_content_provenance_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS validation of content-provenance — it fires on GENUINE
    # deliverable-provenance prose captured live from a real generation storefront, and
    # does NOT fire on a DIFFERENT real storefront's "watermarking for provenance"
    # MODEL-FEATURE trap.
    #
    # BOTH canonical homepages carry embedded content-provenance prose captured live:
    # "Every paid render carries a commercial licence and embedded C2PA content
    # credentials" and "C2PA credentials record provenance without limiting your
    # rights". The storefront already claims digital_good, so this DEEPENS its evidence
    # without changing the claimed set (score-neutrality pinned byte-for-byte by
    # tests/test_offering_canonical.py; classification is off the scoring path).
    for domain in ("driftflight.com", "drift-flight.org"):
        home = _fixture_entry_text(domain, domain)
        assert "c2pa" in home.lower(), f"{domain} homepage lost its C2PA provenance prose"
        prof = classify_offering(domain, {"homepage": home})
        assert prof.claims("digital_good"), (domain, prof.archetypes)
        dg = next(c for c in prof.claimed if c.archetype == "digital_good")
        prov = [s for s in dg.signals if s.label == "content-provenance"]
        assert prov, (domain, {s.label for s in dg.signals})
        q = prov[0].quote.lower()
        assert "c2pa" in q or "provenance" in q or "content credential" in q, prov[0].quote
        print(f"  ok: content-provenance fires on REAL captured {domain} prose — quote: {prov[0].quote!r}")

    # Precision on real noise: api.replicate.com — a metered_api-ONLY storefront (pinned
    # by test_machine_surface_openapi_storefront) — describes a HOSTED MODEL that can
    # "Embed invisible SynthID watermarking for provenance on all generated ... images"
    # in its committed OpenAPI spec. That is a model FEATURE, not a deliverable the
    # storefront itself vends, so content-provenance must NOT fire — the spec must not
    # gain a spurious digital_good.
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "watermarking for provenance" in spec, "fixture lost its watermark-for-provenance trap"
    spec_prof = classify_offering("api.replicate.com", {"/openapi.json": spec})
    spec_labels = {s.label for c in spec_prof.claimed for s in c.signals}
    assert "content-provenance" not in spec_labels, spec_labels
    assert not spec_prof.claims("digital_good"), spec_prof.archetypes
    print("  ok: the 'watermarking for provenance' model-feature does NOT fire content-provenance (real-data precision)")


def test_output_resolution_precision_synthetic():
    # Output SPECIFICATION is the "understand + specify the offer" leg of a digital
    # good — the concrete output RESOLUTION / pixel DIMENSIONS / ASPECT RATIO of the
    # generated deliverable an agent must request and can rely on. An agent that can
    # read the output-resolution contract requests a producible size at the right
    # resolution for its downstream use, so it must claim digital_good via the new
    # output-resolution signal. Each POSITIVE is real output-spec vocabulary; each
    # NEGATIVE is resolution-SHAPED noise that must NOT fire it (the precision traps:
    # a SCREEN / MONITOR / DISPLAY hardware resolution, the "Super resolution" /
    # "Enhance image resolution" MODEL-FEATURE phrasing on a metered-API marketplace,
    # and the dispute / New-Year / DNS senses of "resolution").
    positives = {
        "maxResolution field": 'The models endpoint returns {"maxResolution": "4096px"}.',
        "output resolution px": "The maximum output resolution is 4096px.",
        "print resolution": "Use the gallery preset for hero and print resolution.",
        "render dimensions": "Render dimensions up to 2048px are supported.",
        "output dimensions": "Choose your output dimensions before generating.",
        "resolution up to px": "Generations are available at resolution up to 4096px.",
        "wxh px": "Every export ships at 1024x1024 px.",
        "aspect ratio": "Pick an aspect ratio of 16:9 for the render.",
        "canvas dimensions": "Set the canvas dimensions for the generated frame.",
    }
    for name, text in positives.items():
        prof = classify_offering("studio.test", {"homepage": text})
        assert prof.claims("digital_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "digital_good"
            for s in c.signals
        }
        assert "output-resolution" in labels, (name, labels)
    print(f"  ok: {len(positives)} real output-spec phrasings each fire output-resolution")

    negatives = {
        "screen resolution": "Check your screen resolution of 1920px before starting.",
        "monitor resolution": "Set your monitor resolution to 2560px.",
        "display resolution": "The display resolution is 4096px on this laptop.",
        "super resolution model": "Super resolution upscaling improves old photos.",
        "enhance image resolution": "The model can enhance image resolution automatically.",
        "dispute resolution": "See our dispute resolution process for chargebacks.",
        "new year resolution": "Make a New Year resolution to ship more.",
        "bare resolution": "We admire your resolution and commitment.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "output-resolution" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} resolution-shaped noise strings do NOT fire output-resolution (precision)"
    )


def test_output_resolution_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS validation of output-resolution — it fires on GENUINE
    # output-specification prose captured live from a real generation storefront, and
    # does NOT fire on a DIFFERENT real storefront's "Super resolution" / "Enhance
    # image resolution" MODEL-FEATURE trap.
    #
    # BOTH canonical domains carry captured output-spec prose: the /docs models block
    # publishes each tier's `"maxResolution": "1024px|2048px|4096px"` and the homepage
    # says "gallery for hero and print resolution". The storefront already claims
    # digital_good, so this DEEPENS its evidence without changing the claimed set
    # (score-neutrality pinned byte-for-byte by tests/test_offering_canonical.py;
    # classification is off the scoring path).
    for domain in ("driftflight.com", "drift-flight.org"):
        docs = _fixture_entry_text(domain, "/docs")
        assert "maxResolution" in docs, f"{domain} /docs lost its maxResolution output-spec"
        prof = classify_offering(domain, {"/docs": docs})
        assert prof.claims("digital_good"), (domain, prof.archetypes)
        dg = next(c for c in prof.claimed if c.archetype == "digital_good")
        res = [s for s in dg.signals if s.label == "output-resolution"]
        assert res, (domain, {s.label for s in dg.signals})
        assert "resolution" in res[0].quote.lower(), res[0].quote
        print(f"  ok: output-resolution fires on REAL captured {domain} /docs — quote: {res[0].quote!r}")

    # Precision on real noise: api.replicate.com — a metered_api-ONLY storefront (pinned
    # by test_machine_surface_openapi_storefront) — hosts models whose committed OpenAPI
    # spec describes "Super resolution" and "Enhance image resolution" FEATURES. Those are
    # model features, not a deliverable the storefront itself vends at a documented
    # output resolution, so output-resolution must NOT fire — the spec must not gain a
    # spurious digital_good.
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "resolution" in spec.lower(), "fixture lost its resolution model-feature trap"
    spec_prof = classify_offering("api.replicate.com", {"/openapi.json": spec})
    spec_labels = {s.label for c in spec_prof.claimed for s in c.signals}
    assert "output-resolution" not in spec_labels, spec_labels
    assert not spec_prof.claims("digital_good"), spec_prof.archetypes
    print("  ok: the 'Super/Enhance image resolution' model-features do NOT fire output-resolution (real-data precision)")


def test_output_retention_precision_synthetic():
    # Output DELIVERY-WINDOW / retention is the "complete the job" LIFECYCLE leg of a
    # digital good — how long the generated deliverable PERSISTS at its hosted URL and
    # that the agent must retrieve it (download it into its OWN storage) before the
    # window closes. An agent that reads the retention contract copies its output out
    # in time instead of silently losing it when the hosted link expires, so it must
    # claim digital_good via the new output-retention signal. Each POSITIVE is real
    # artifact-lifecycle vocabulary; each NEGATIVE is retention-SHAPED noise that must
    # NOT fire it (the precision traps: a SUPPORT-line / EVENT / FREE-TRIAL time window
    # with no deliverable noun, and — the trap on a metered-API marketplace — a signed
    # download-URL / API-key EXPIRY, which is not a hosted-deliverable retention window).
    positives = {
        "urls remain available": "Renders come back as hosted URLs that remain available for 90 days.",
        "output hosted for": "Output images are hosted for 30 days before deletion.",
        "files stored for": "Generated files are stored for 7 days on our CDN.",
        "asset kept for": "Each asset is kept for 24 hours after the job completes.",
        "download into own storage": "Download them into your own storage for anything long-lived.",
        "download images into bucket": "Download the images into your own bucket before they expire.",
        "retention policy": "See our output retention policy for how long renders live.",
        "render retention window": "The render retention window is 14 days.",
    }
    for name, text in positives.items():
        prof = classify_offering("studio.test", {"homepage": text})
        assert prof.claims("digital_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "digital_good"
            for s in c.signals
        }
        assert "output-retention" in labels, (name, labels)
    print(f"  ok: {len(positives)} real output-retention phrasings each fire output-retention")

    negatives = {
        "support line window": "Our support agents remain available for 24 hours a day.",
        "event hosted window": "The conference is hosted for 3 days in June.",
        "free trial window": "This plan is free for 30 days, no card required.",
        "seats available window": "Seats are available for 5 users on the team plan.",
        "file expiry trap": "A Unix timestamp with expiration date of this download URL.",
        "when file expires": "expires_at: When the file expires.",
        "download a file": "Download a file by providing its ID.",
        "retained counsel": "We retained counsel for the dispute last year.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "output-retention" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} retention-shaped noise strings do NOT fire output-retention (precision)"
    )


def test_output_retention_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS validation of output-retention — it fires on GENUINE
    # delivery-window prose captured live from a real generation storefront, and does
    # NOT fire on a DIFFERENT real storefront's signed-URL / file-EXPIRY trap.
    #
    # BOTH canonical domains carry captured retention prose on their /docs: generated
    # renders are "returned as hosted URLs that remain available for 90 days; download
    # them into your own storage for anything long-lived". The storefront already claims
    # digital_good, so this DEEPENS its evidence without changing the claimed set
    # (score-neutrality pinned byte-for-byte by tests/test_offering_canonical.py;
    # classification is off the scoring path).
    for domain in ("driftflight.com", "drift-flight.org"):
        docs = _fixture_entry_text(domain, "/docs")
        assert "remain available for 90 days" in docs, f"{domain} /docs lost its retention-window prose"
        prof = classify_offering(domain, {"/docs": docs})
        assert prof.claims("digital_good"), (domain, prof.archetypes)
        dg = next(c for c in prof.claimed if c.archetype == "digital_good")
        ret = [s for s in dg.signals if s.label == "output-retention"]
        assert ret, (domain, {s.label for s in dg.signals})
        quotes = " ".join(s.quote.lower() for s in ret)
        assert "remain available" in quotes or "own storage" in quotes, quotes
        print(f"  ok: output-retention fires on REAL captured {domain} /docs — quotes: {[s.quote for s in ret]!r}")

    # Precision on real noise: api.replicate.com — a metered_api-ONLY storefront (pinned
    # by test_machine_surface_openapi_storefront) — exposes a Files API whose committed
    # OpenAPI spec says "When the file expires" and "a Unix timestamp with expiration
    # date of this download URL". That is a SIGNED-URL / file expiry, not a hosted
    # deliverable's retention window (no deliverable noun + retention verb, no
    # download-into-your-own-storage step), so output-retention must NOT fire — the spec
    # must not gain a spurious digital_good.
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "expiration date of this download URL" in spec, "fixture lost its file-expiry trap"
    spec_prof = classify_offering("api.replicate.com", {"/openapi.json": spec})
    spec_labels = {s.label for c in spec_prof.claimed for s in c.signals}
    assert "output-retention" not in spec_labels, spec_labels
    assert not spec_prof.claims("digital_good"), spec_prof.archetypes
    print("  ok: the Files API signed-URL/file-expiry prose does NOT fire output-retention (real-data precision)")


def test_pagination_metering_precision_synthetic():
    # Cursor / collection PAGINATION — how an agent retrieves a MULTI-PAGE result
    # set (a list endpoint returns one page plus a cursor / a `next`/`previous` page
    # URL to follow) — is the "complete the job" capability for a metered API that
    # returns a COLLECTION, so it must claim metered_api via the new pagination
    # signal. Each POSITIVE is real, vendor-neutral pagination vocabulary; each
    # NEGATIVE is pagination-SHAPED noise that must NOT fire it (the precision traps:
    # a RETAIL catalog's HTML `next` link, a marketing "next campaign", a DOM
    # `previousSibling`, a CSS/SQL cursor, "the next page of the novel").
    positives = {
        "cursor param": "Fetch the next page: GET /v1/models?cursor=cD0yMDIzLTA2LTA2",
        "amp cursor param": "Follow the link &cursor=eyJvZmZzZXQiOjUwfQ== to continue.",
        "cursor-based": "The list endpoints use cursor-based pagination for large sets.",
        "pagination object": "The response is a pagination object containing a list of items.",
        "paginated collection": "Returns a paginated collection response with next/previous URLs.",
        "next page of collection": "`next`: A URL pointing to the next page of collection objects.",
        "previous page of results": "`previous`: A URL for the previous page of results, if any.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "pagination" in labels, (name, labels)
    print(f"  ok: {len(positives)} real cursor/pagination phrasings each fire pagination")

    negatives = {
        "retail next link": '<li class="next"><a href="catalogue/page-2.html">next</a></li>',
        "next campaign": "Ship your next campaign in formation, ready in 24 hours.",
        "dom previoussibling": "var g=c.previousSibling,h=0;do{if(c)",
        "css cursor": "button { cursor: pointer; } .link { cursor: default; }",
        "sql cursor": "Open a database cursor and iterate over the rows.",
        "novel page": "Turn to the next page of the novel to find out.",
        "next steps page": "See the next page for setup, then read the previous chapter.",
        "repaginated": "The report was repaginated overnight by the layout team.",
        "retail cart": "Add to cart, then check out — free shipping on every order.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "pagination" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} pagination-shaped noise strings do NOT fire pagination (precision)"
    )


def test_pagination_fires_on_real_captured_openapi():
    # Real-evidence, NON-VACUOUS, END-TO-END: the pagination signal fires on the
    # GENUINE cursor-pagination contract captured live from a real machine-surface
    # storefront — api.replicate.com's /openapi.json documents a `next`/`previous`
    # paginated collection response ("A URL pointing to the next page of collection
    # objects") and a `?cursor=…` list URL, captured verbatim in the committed
    # fixture. Run the REAL discovery path (from_fixture -> discover_offering) so the
    # signal is exercised exactly as a live crawl would, the same real-data
    # non-vacuity move test_async_job_fires_on_real_captured_openapi makes.
    #
    # SCORE-NEUTRAL by construction: api.replicate.com already claims ONLY metered_api
    # (its strongest and only archetype), so a pagination contract on its spec can
    # only deepen that claim's evidence — never add an archetype or reorder. The
    # classifier is off the scoring path; the canonical pair (which does NOT document
    # a pagination contract) is unchanged (pagination fires on neither driftflight
    # surface — pinned by tests/test_offering_canonical.py and the canonical replay
    # guard).
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "next page of collection" in spec.lower(), "fixture /openapi.json lost its pagination contract"

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "api.replicate.com.json"))
    prof = offering.discover_offering(ctx)

    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    pg = [s for s in metered.signals if s.label == "pagination"]
    assert pg, {s.label for s in metered.signals}
    quote = pg[0].quote.lower()
    assert "cursor=" in quote or "page of" in quote or "paginat" in quote, pg[0].quote
    print(f"  ok: pagination fires on REAL captured OpenAPI contract — quote: {pg[0].quote!r}")


def test_cancel_job_metering_precision_synthetic():
    # Job CANCELLATION — how an agent ABORTS a long-running job it already submitted
    # (a `.../cancel` endpoint on the job resource, a `Cancel-After` deadline header,
    # a documented `canceled` job state) — is the "complete the job" CONTROL +
    # capital-safety capability for a metered API whose work runs long: an agent that
    # detects a runaway/wrong generation and cannot cancel it keeps paying for compute
    # it no longer needs, so it must claim metered_api via the new cancel-job signal.
    # Each POSITIVE is real, vendor-neutral job-cancellation vocabulary; each NEGATIVE
    # is cancel-SHAPED noise that must NOT fire it (the precision traps: cancelling a
    # SUBSCRIPTION, an ORDER, a BOOKING; a cancellation POLICY; a cancelled flight;
    # "cancel culture").
    positives = {
        "cancel-after header": 'The `Cancel-After` header bounds how long the prediction may run.',
        "cancel the prediction": "POST to abort: cancel the prediction to stop billing immediately.",
        "cancel a job": "You can cancel a job at any time before it reaches a terminal state.",
        "cancel a running training": "Send a request to cancel the running training run.",
        "cancel your queued task": "An agent may cancel your queued task if the deadline slips.",
        "cancel endpoint path": "Call `POST /v1/predictions/{prediction_id}/cancel` to stop it.",
        "cancel training url": "The `cancel` field is a URL to cancel the training.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "cancel-job" in labels, (name, labels)
    print(f"  ok: {len(positives)} real job-cancellation phrasings each fire cancel-job")

    negatives = {
        "cancel subscription": "Cancel your subscription anytime from the billing page.",
        "cancel anytime": "No contracts — cancel anytime, no questions asked.",
        "cancel order": "You can cancel your order within 24 hours of purchase.",
        "cancel booking": "To cancel your booking, call the front desk.",
        "cancellation policy": "Read our cancellation policy before you reserve a room.",
        "cancelled flight": "We regret that we canceled the flight due to weather.",
        "cancel culture": "An essay on cancel culture and public discourse.",
        "cancel plan": "Downgrade or cancel your plan whenever you like.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "cancel-job" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} cancel-shaped noise strings do NOT fire cancel-job (precision)"
    )


def test_cancel_job_fires_on_real_captured_openapi():
    # Real-evidence, NON-VACUOUS, END-TO-END: the cancel-job signal fires on the
    # GENUINE job-cancellation contract captured live from a real machine-surface
    # storefront — api.replicate.com's /openapi.json documents a `Cancel-After`
    # deadline header, a `predictions/{id}/cancel` endpoint, and a `canceled`
    # prediction state, captured verbatim in the committed fixture. Run the REAL
    # discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would, the same real-data non-vacuity move
    # test_pagination_fires_on_real_captured_openapi makes.
    #
    # SCORE-NEUTRAL by construction: api.replicate.com already claims ONLY metered_api
    # (its strongest and only archetype), so a cancellation contract on its spec can
    # only deepen that claim's evidence — never add an archetype or reorder. The
    # classifier is off the scoring path; the canonical pair (whose `/cancellation`
    # surface is a subscription cancel with no job vocabulary) is unchanged (cancel-job
    # fires on neither driftflight surface — pinned by tests/test_offering_canonical.py
    # and the canonical replay guard).
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "Cancel-After" in spec, "fixture /openapi.json lost its job-cancellation contract"

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "api.replicate.com.json"))
    prof = offering.discover_offering(ctx)

    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    cj = [s for s in metered.signals if s.label == "cancel-job"]
    assert cj, {s.label for s in metered.signals}
    quote = cj[0].quote.lower()
    assert "cancel" in quote, cj[0].quote
    print(f"  ok: cancel-job fires on REAL captured OpenAPI contract — quote: {cj[0].quote!r}")

    # NON-VACUOUS + score-neutral: the machine storefront's claimed SET is exactly
    # [metered_api] — the pagination contract deepened the metered_api evidence
    # without adding a spurious archetype (no false data_retrieval from "collection"
    # or "records" prose reaching a wrong bank).
    assert prof.archetypes == ["metered_api"], prof.archetypes
    print("  ok: pagination evidence does NOT change the claimed set (score-neutral)")

    # Precision on real retail noise: books.toscrape.com paginates its HTML catalog
    # with `<li class="next"><a href="catalogue/page-2.html">next</a></li>` — a bare
    # "next" link, NOT an API pagination contract. pagination must NOT fire there, so
    # the retail storefront keeps its physical_good-only claim and gains no spurious
    # metered_api.
    retail = classify_offering(
        "books.toscrape.com",
        {"homepage": _fixture_entry_text("books.toscrape.com", "")
         or '<li class="next"><a href="catalogue/page-2.html">next</a></li>'},
    )
    retail_labels = {s.label for c in retail.claimed for s in c.signals}
    assert "pagination" not in retail_labels, retail_labels
    print("  ok: the retail HTML 'next' catalog link does NOT fire pagination (real-data precision)")


def test_webhook_verification_precision_synthetic():
    # WEBHOOK AUTHENTICITY VERIFICATION — whether an agent can TRUST that an inbound
    # async callback is GENUINELY from the API rather than a forged/spoofed webhook
    # (a webhook signing secret to verify inbound requests, a webhook signature to
    # check) — is the security/TRUST leg of the async contract for a metered API: an
    # agent that acts on an UNVERIFIED "job complete" webhook can be tricked by a
    # spoofed callback into treating fabricated output as real or releasing a payment,
    # so a documented webhook-verification contract makes it claim metered_api via the
    # new webhook-verification signal. Each POSITIVE is real, vendor-neutral
    # webhook-security vocabulary; each NEGATIVE is signature/signing-SHAPED noise that
    # must NOT fire it (the precision traps: a marketing "signature look", an x402
    # PAYMENT-proof signature, a file SIGNED-URL "signing secret", a bare webhook that
    # only EXISTS — `async-job`'s turf — and generic contract/digital signatures).
    positives = {
        "webhook signature": "Verify the webhook signature before trusting the callback.",
        "signing secret for webhook": "Get the signing secret for the default webhook endpoint.",
        "verify that webhook requests": "This is used to verify that webhook requests are authentic.",
        "verify the webhook payload": "You must verify the webhook payload with your signing key.",
        "webhook events are signed": "All webhook events are signed so an agent can confirm origin.",
        "X-Webhook-Signature header": "Check the X-Webhook-Signature header on each delivery.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "webhook-verification" in labels, (name, labels)
    print(f"  ok: {len(positives)} real webhook-verification phrasings each fire webhook-verification")

    negatives = {
        "signature look marketing": "your product line, your palette, your signature look.",
        "x402 payment signature": "ZeroClick verifies the signature locally, so nothing settles on-chain.",
        "file url signing secret": 'generated with the Files API signing secret","in":"query","name":"signature"',
        "webhook exists only": "Register a webhook endpoint to receive prediction events.",
        "sign the contract": "Please sign the contract and return it.",
        "digital signature doc": "The document requires a digital signature.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "webhook-verification" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} signature/signing-shaped noise strings do NOT fire webhook-verification (precision)"
    )


def test_webhook_verification_fires_on_real_captured_openapi():
    # Real-evidence, NON-VACUOUS, END-TO-END: the webhook-verification signal fires on
    # the GENUINE webhook-authenticity contract captured live from a real machine-surface
    # storefront — api.replicate.com's /openapi.json documents a
    # `/webhooks/default/secret` endpoint whose description reads "Get the signing secret
    # for the default webhook endpoint. This is used to verify that webhook requests are
    # coming from ...", captured verbatim in the committed fixture. Run the REAL discovery
    # path (from_fixture -> discover_offering) so the signal is exercised exactly as a
    # live crawl would, the same real-data non-vacuity move
    # test_cancel_job_fires_on_real_captured_openapi makes.
    #
    # SCORE-NEUTRAL by construction: api.replicate.com already claims ONLY metered_api
    # (its strongest and only archetype), so a webhook-verification contract on its spec
    # can only deepen that claim's evidence — never add an archetype or reorder. The
    # classifier is off the scoring path; the canonical pair (whose webhook/signature
    # prose is marketing "signature look" + x402 payment-proof verification, no webhook
    # authenticity contract) is unchanged (webhook-verification fires on neither
    # driftflight surface — pinned by tests/test_offering_canonical.py and the canonical
    # replay guard).
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "signing secret for the default webhook" in spec, (
        "fixture /openapi.json lost its webhook-verification contract"
    )

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "api.replicate.com.json"))
    prof = offering.discover_offering(ctx)

    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    wv = [s for s in metered.signals if s.label == "webhook-verification"]
    assert wv, {s.label for s in metered.signals}
    quote = wv[0].quote.lower()
    assert "webhook" in quote, wv[0].quote
    print(f"  ok: webhook-verification fires on REAL captured OpenAPI contract — quote: {wv[0].quote!r}")

    # NON-VACUOUS + score-neutral: the machine storefront's claimed SET is exactly
    # [metered_api] — the webhook-verification contract deepened the metered_api
    # evidence without adding a spurious archetype.
    assert prof.archetypes == ["metered_api"], prof.archetypes
    print("  ok: webhook-verification evidence does NOT change the claimed set (score-neutral)")

    # Precision on the real canonical pair: both driftflight surfaces carry a
    # "signature" (the marketing "your palette, your signature look" and the x402
    # payment-proof "ZeroClick verifies the signature locally") but NO webhook
    # authenticity contract. webhook-verification must NOT fire on either, so the
    # canonical pair gains no spurious signal (the driftflight metered_api claim rests
    # on its own — unrelated — evidence, unchanged).
    for dom in ("drift-flight.org", "driftflight.com"):
        canon = offering.discover_offering(
            FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        )
        canon_labels = {s.label for c in canon.claimed for s in c.signals}
        assert "webhook-verification" not in canon_labels, (dom, canon_labels)
    print("  ok: the canonical pair's marketing/payment 'signature' prose does NOT fire webhook-verification (real-data precision)")


def test_streaming_response_metering_precision_synthetic():
    # STREAMING response delivery — how an agent consumes output INCREMENTALLY over
    # the OPEN connection as it is produced (token-by-token generation, progressive
    # job output), the IN-BAND sibling of async-job. A metered API that documents a
    # streaming / server-sent-events flow is more agent-completable, so it claims
    # metered_api via the new streaming-response signal. Each POSITIVE is real,
    # vendor-neutral streaming vocabulary; each NEGATIVE is streaming-SHAPED noise
    # that must NOT fire it (the precision traps: an `application/octet-stream`
    # binary-download MIME type, the Shanghai Stock Exchange / "sum of squared
    # errors" (SSE) acronym collisions, a live stream, the bloodstream, a stream of
    # consciousness, downstream/upstream).
    positives = {
        "server-sent events": "Request a URL to receive streaming output using server-sent events (SSE).",
        "stream the output": "An event source to stream the output of the prediction via API.",
        "event-stream media": "Responses use the text/event-stream media type for incremental delivery.",
        "streaming api": "Use the streaming API to read tokens as they are produced.",
        "stream tokens": "The endpoint can stream tokens back as the model generates them.",
        "streaming responses": "Enable streaming responses to consume partial output early.",
        "via SSE": "Consume the incremental output via SSE from the events endpoint.",
        "SSE stream noun": "Open an SSE stream to receive tokens live.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "streaming-response" in labels, (name, labels)
    print(f"  ok: {len(positives)} real streaming/SSE phrasings each fire streaming-response")

    negatives = {
        "octet-stream mime": "The content / MIME type for the file (defaults to application/octet-stream).",
        "live stream": "Watch our product launch live stream this Friday at noon.",
        "stock exchange sse": "The Shanghai Stock Exchange (SSE) composite index rose 2% today.",
        "sum squared errors": "We minimize the SSE (sum of squared errors) during training.",
        "bloodstream": "Absorbed directly into the bloodstream within minutes.",
        "stream of consciousness": "The novel is written in a stream of consciousness style.",
        "downstream": "This affects downstream services and upstream providers.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "streaming-response" not in labels, (name, labels, prof.archetypes)
    # The acronym-collision negatives must not even CONJURE a metered_api claim —
    # a bare "SSE" on a stock-exchange page would be worse than noise here.
    for name in ("stock exchange sse", "sum squared errors"):
        prof = classify_offering("noise.test", {"homepage": negatives[name]})
        assert not prof.claims("metered_api"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} streaming-shaped noise strings do NOT fire streaming-response (precision)"
    )


def test_streaming_response_fires_on_real_captured_openapi():
    # Real-evidence, NON-VACUOUS, END-TO-END: the streaming-response signal fires on
    # the GENUINE streaming contract captured live from a real machine-surface
    # storefront — api.replicate.com's /openapi.json documents a `stream` field whose
    # description reads "receive streaming output using server-sent events (SSE)" and
    # "An event source to stream the output of the prediction", captured verbatim in
    # the committed fixture. Run the REAL discovery path (from_fixture ->
    # discover_offering) so the signal is exercised exactly as a live crawl would, the
    # same real-data non-vacuity move test_cancel_job_fires_on_real_captured_openapi
    # makes.
    #
    # SCORE-NEUTRAL by construction: api.replicate.com already claims ONLY metered_api
    # (its strongest and only archetype), so a streaming contract on its spec can only
    # deepen that claim's evidence — never add an archetype or reorder. The classifier
    # is off the scoring path; the canonical pair (whose surfaces document no streaming
    # flow) is unchanged (streaming-response fires on neither driftflight surface —
    # pinned by tests/test_offering_canonical.py and the canonical replay guard).
    spec = _fixture_entry_text("api.replicate.com", "/openapi.json")
    assert "server-sent events" in spec.lower(), "fixture /openapi.json lost its streaming contract"

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "api.replicate.com.json"))
    prof = offering.discover_offering(ctx)

    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    sr = [s for s in metered.signals if s.label == "streaming-response"]
    assert sr, {s.label for s in metered.signals}
    quote = sr[0].quote.lower()
    assert "stream" in quote or "sse" in quote or "server-sent" in quote, sr[0].quote
    print(f"  ok: streaming-response fires on REAL captured OpenAPI contract — quote: {sr[0].quote!r}")

    # NON-VACUOUS + score-neutral: the machine storefront's claimed SET is exactly
    # [metered_api] — the streaming contract deepened the metered_api evidence without
    # adding a spurious archetype (no false digital_good from "output"/"generation"
    # prose reaching a wrong bank).
    assert prof.archetypes == ["metered_api"], prof.archetypes
    print("  ok: streaming-response evidence does NOT change the claimed set (score-neutral)")

    # Precision on real noise: the SAME spec carries `application/octet-stream` (a
    # binary-download MIME type, NOT a streaming RESPONSE). The streaming-response
    # quote must be a genuine streaming phrase, never the octet-stream MIME — proof the
    # signal keys on the streaming CONTRACT, not on any "stream" substring.
    assert "octet-stream" not in quote, sr[0].quote
    print("  ok: the octet-stream binary MIME does NOT masquerade as streaming (real-data precision)")


def test_self_provisioning_precision_synthetic():
    # AGENT SELF-PROVISIONING — whether an autonomous agent can OBTAIN access to the
    # API WITHOUT a human in the loop (no signup, no human account creation, the agent
    # provisions its OWN identity). This is the "provision without a human" capability
    # the PLAYBOOK's capability lens names, and it is the load-bearing precondition
    # for every other metered_api leg: an API whose credentials only a human can
    # obtain is not agent-completable end-to-end. A metered API that lets an agent
    # self-provision claims metered_api via the new self-provisioning signal. Each
    # POSITIVE is real, vendor-neutral agent-onboarding vocabulary; each NEGATIVE is
    # onboarding-SHAPED noise that must NOT fire it (the precision traps: the OPPOSITE
    # human-onboarding path "Human developers sign up …", a 401 "No API key" error
    # message, a "no signup fees" pricing statement, a "sign up for our newsletter"
    # prompt).
    positives = {
        "no signup heading": "Driftflight sells to AI agents - free trial, no signup.",
        "no signup and no api key": "There is no signup and no API key: agents pay per use.",
        "provision own identity": "an autonomous agent can provision its own identity and start calling.",
        "no funding and no signup": "The free allowance needs no funding and no signup.",
        "no signup comma": "No signup, no API key: you authenticate by signing payment challenges.",
        "self-provision": "Agents self-provision an account with no human in the loop.",
        "without a human account": "Onboard without a human account creation step.",
        "no human signup": "Access requires no human signup — the agent registers itself.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "self-provisioning" in labels, (name, labels)
    print(f"  ok: {len(positives)} real self-provisioning phrasings each fire self-provisioning")

    negatives = {
        # The OPPOSITE capability — a human-gated onboarding — present verbatim on
        # BOTH canonical domains. Misreading it as self-provisioning would invert the
        # signal's meaning, so it must fire NOTHING here.
        "human signup path": "Human developers sign up on the dashboard for an API key; usage bills monthly.",
        "401 no-api-key error": "401 unauthorized No API key, or the key is unknown or revoked.",
        "no signup fee pricing": "Good news: there are no signup fees or setup charges on any plan.",
        "newsletter signup": "Sign up for our newsletter to get 10% off your first order.",
        "human artist": "Made by a human artist — sign up for a studio tour.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "self-provisioning" not in labels, (name, labels, prof.archetypes)
    # NOTE: the "human signup path" and "401 no-api-key error" negatives DO contain a
    # literal "API key", which legitimately trips the SEPARATE `api-auth` signal (an
    # API with a key IS a metered API) — so metered_api may well be claimed here. That
    # is correct and orthogonal: the precision point this signal must hold is that the
    # human-onboarding / error phrasing never fires SELF-PROVISIONING (asserted above),
    # not that the surrounding text conjures no other archetype.
    print(
        f"  ok: {len(negatives)} onboarding-shaped noise strings do NOT fire self-provisioning (precision)"
    )


def test_self_provisioning_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the self-provisioning signal fires on
    # the GENUINE agent-onboarding prose captured live from driftflight.com — the apex
    # homepage/pricing "free trial, no signup" heading and the agents.driftflight.com
    # agent docs "There is no signup and no API key … an autonomous agent can provision
    # its own identity" — all captured verbatim in the committed fixture. Run the REAL
    # discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would, the same real-data non-vacuity move
    # test_api_auth_fires_on_real_captured_surfaces makes.
    #
    # SCORE-NEUTRAL by construction: driftflight.com already claims metered_api (its
    # strongest archetype), so self-provisioning evidence can only deepen that claim —
    # never add an archetype or reorder. The classifier is off the scoring path; the
    # canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    sp = [s for s in metered.signals if s.label == "self-provisioning"]
    assert sp, {s.label for s in metered.signals}
    q = sp[0].quote.lower()
    assert "no signup" in q or "provision" in q or "no sign-up" in q, sp[0].quote
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    print(f"  ok: self-provisioning fires on REAL captured driftflight.com prose — quote: {sp[0].quote!r}")

    # PRECISION-CRITICAL on real data: drift-flight.org's ONLY signup phrasing is the
    # human-gated dashboard path ("Human developers sign up on the dashboard for an API
    # key") plus a 401 "No API key" error — NEITHER is agent self-provisioning. The
    # signal must be ABSENT there even though the trap words ("sign up", "No API key")
    # are present verbatim, and .org's claimed set must be unchanged. This is the
    # discovery-layer echo of the real capability gap: the with-rails .com documents
    # autonomous onboarding, the .org does not.
    org_docs = _fixture_entry_text("drift-flight.org", "/docs")
    assert "sign up" in org_docs.lower() or "no api key" in org_docs.lower(), (
        "fixture lost the human-onboarding / 401 trap words the precision guard needs"
    )
    octx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "drift-flight.org.json"))
    oprof = offering.discover_offering(octx)
    all_labels = {s.label for c in oprof.claimed for s in c.signals}
    assert "self-provisioning" not in all_labels, all_labels
    assert oprof.archetypes == ["metered_api", "digital_good", "subscription"], oprof.archetypes
    print("  ok: self-provisioning is ABSENT on drift-flight.org's human-only signup path (real-data precision)")

    # NON-VACUOUS negative: a real retail storefront documents no agent onboarding —
    # self-provisioning must be absent there and must not conjure a metered_api claim.
    rctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "books.toscrape.com.json"))
    retail = offering.discover_offering(rctx)
    assert retail.archetypes == ["physical_good"], retail.archetypes
    rlabels = {s.label for c in retail.claimed for s in c.signals}
    assert "self-provisioning" not in rlabels, rlabels
    print("  ok: self-provisioning is ABSENT on a real retail storefront (non-vacuous)")


def test_payment_receipt_precision_synthetic():
    # PAYMENT RECEIPT / spend reconciliation — the machine-readable PROOF-OF-PAYMENT
    # an agent gets BACK after a paid call and logs to RECONCILE its own spend (a
    # receipt header on the paid response, a payment/settlement receipt, a spend
    # record, proof of payment). This is the ACCOUNTING leg of an agent-native metered
    # API and the capital-safety counterpart to the payment RAILS (`x402` /
    # `agent-payment-rail` say the agent can PAY; NONE says what verifiable receipt
    # comes BACK). A metered API that returns a machine-readable payment receipt claims
    # metered_api via the new payment-receipt signal. Each POSITIVE is real,
    # vendor-neutral payment-accounting vocabulary; each NEGATIVE is receipt-SHAPED
    # noise that must NOT fire it (the precision traps: an email/read receipt, a retail
    # order receipt, "in receipt of", a warehouse "receipt of goods").
    positives = {
        "receipt header": "Every successful paid response includes a receipt header you can log.",
        "payment receipt": "The response returns a payment receipt for each settled call.",
        "payment-receipt hyphen": "MPP responses carry a `payment-receipt` header.",
        "settlement receipt": "Each paid call returns a settlement receipt the agent stores.",
        "serialized receipt": "The MPP receipt is a serialized receipt in the response header.",
        "spend records": "Log the receipt for your spend records to reconcile usage.",
        "proof of payment": "Every paid call returns proof of payment as a response header.",
        "receipt you can log": "The API returns a receipt you can log against your budget.",
    }
    for name, text in positives.items():
        prof = classify_offering("metered.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "payment-receipt" in labels, (name, labels)
    print(f"  ok: {len(positives)} real payment-receipt phrasings each fire payment-receipt")

    negatives = {
        # Non-payment "receipt" senses — misreading any as a payment receipt would
        # conjure a spurious agent-payment-accounting capability. Each must fire
        # NOTHING here.
        "email receipt": "We email a receipt to your inbox after every purchase.",
        "read receipt": "Enable read receipts so senders know you saw the message.",
        "order receipt": "Your order receipt is available in your account history.",
        "in receipt of": "We are in receipt of your support request and will reply soon.",
        "receipt of goods": "Payment is due on receipt of goods at the warehouse.",
        "receipt to log expenses": "Keep your receipt to log the expense later.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "payment-receipt" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} receipt-shaped noise strings do NOT fire payment-receipt (precision)"
    )


def test_payment_receipt_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the payment-receipt signal fires on the
    # GENUINE agent-payment-accounting prose captured live from driftflight.com — the
    # agents.driftflight.com/llms-full.txt agent docs "Every successful paid response
    # includes a receipt header you can log for your spend records: `payment-response`
    # … or `payment-receipt` (MPP, serialized receipt)" — captured verbatim in the
    # committed fixture. Run the REAL discovery path (from_fixture -> discover_offering)
    # so the signal is exercised exactly as a live crawl would, the same real-data
    # non-vacuity move test_self_provisioning_fires_on_real_captured_surfaces makes.
    #
    # SCORE-NEUTRAL by construction: driftflight.com already claims metered_api (its
    # strongest archetype), so payment-receipt evidence can only deepen that claim —
    # never add an archetype or reorder. The classifier is off the scoring path; the
    # canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    pr = [s for s in metered.signals if s.label == "payment-receipt"]
    assert pr, {s.label for s in metered.signals}
    q = pr[0].quote.lower()
    assert "receipt" in q or "spend record" in q, pr[0].quote
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    print(f"  ok: payment-receipt fires on REAL captured driftflight.com prose — quote: {pr[0].quote!r}")

    # PRECISION-CRITICAL on real data: drift-flight.org — the no-rails-side canonical
    # anchor — carries NO receipt/spend-record prose at all. The signal must be ABSENT
    # there and .org's claimed set unchanged. This is the discovery-layer echo of the
    # real capability gap: the with-rails .com documents machine-readable payment
    # receipts, the .org does not (mirroring self-provisioning).
    octx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "drift-flight.org.json"))
    oprof = offering.discover_offering(octx)
    all_labels = {s.label for c in oprof.claimed for s in c.signals}
    assert "payment-receipt" not in all_labels, all_labels
    assert oprof.archetypes == ["metered_api", "digital_good", "subscription"], oprof.archetypes
    print("  ok: payment-receipt is ABSENT on drift-flight.org (real-data precision / capability gap)")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real
    # retail storefront (books.toscrape.com), and a null site (example.com) document no
    # agent-payment receipt — payment-receipt must be absent on all three and must not
    # conjure or reorder any archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "payment-receipt" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: payment-receipt is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_plan_purchase_subscription_precision_synthetic():
    # PROGRAMMATIC PLAN PURCHASE — whether an agent can BUY / commit to a
    # credit-or-subscription plan through an API call (a `POST /plans/{id}/purchase`
    # endpoint, a purchasable plan, a buy/purchase/activate verb naming a
    # credit/subscription plan) rather than a human checkout on a pricing page. This
    # is the SUBSCRIPTION-archetype "pay programmatically + provision without a human"
    # commit leg (the counterpart to metered_api's self-provisioning), distinct from
    # the existing subscription signals that only say a plan EXISTS / its CADENCE /
    # per-user basis / free-trial. Each POSITIVE is real, vendor-neutral programmatic
    # plan-purchase vocabulary; each NEGATIVE is plan-SHAPED noise that must NOT fire
    # it (the precision traps: the HUMAN "subscribe to a plan on the pricing page" and
    # "subscribing to a plan on the dashboard", and bare "subscription plans"
    # marketing that `subscription` already covers).
    positives = {
        "purchase endpoint path": "Buy it via `POST /plans/{planId}/purchase` with the plan id.",
        "purchase endpoint short id": "Call `POST /plans/{id}/purchase` to activate.",
        "buy credit-or-subscription plan": "Purchase once to buy a credit or subscription plan.",
        "buy a subscription plan": "An agent can buy a subscription plan without a human.",
        "buy a credit plan": "Buying a credit plan draws down a prepaid balance.",
        "purchase a subscription plan": "Agents purchase a subscription plan programmatically.",
        "purchasable plans": "Purchasable plans carry a `purchase` object with amountRequired.",
        "activate subscription plan": "Activate a subscription plan by paying the challenge.",
    }
    for name, text in positives.items():
        prof = classify_offering("plans.test", {"homepage": text})
        assert prof.claims("subscription"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "subscription"
            for s in c.signals
        }
        assert "plan-purchase" in labels, (name, labels)
    print(f"  ok: {len(positives)} real plan-purchase phrasings each fire plan-purchase")

    negatives = {
        # Human-gated onboarding and bare marketing — misreading any as a programmatic
        # purchase would conjure a spurious agent-native commit capability. Each must
        # fire NOTHING here (the plan-purchase label, specifically).
        "human subscribe on pricing page": "Create an account, subscribe to a plan on the pricing page.",
        "human subscribe on dashboard": "Keys are issued on the dashboard after subscribing to a plan.",
        "bare subscription plans marketing": "We offer flexible subscription plans for every team.",
        "plan your campaign": "Plan your next campaign with our creative tools.",
        "pricing plans exist": "Compare our pricing plans and pick the one that fits.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "plan-purchase" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} plan-shaped noise strings do NOT fire plan-purchase (precision)"
    )


def test_plan_purchase_fires_on_real_captured_subscription_prose():
    # Real-evidence, NON-VACUOUS, END-TO-END: the plan-purchase signal fires on the
    # GENUINE programmatic plan-purchase prose captured live from driftflight.com — the
    # agents.driftflight.com/llms-full.txt agent docs "purchase once with `POST /plans/
    # {planId}/purchase`", "buy a credit or subscription plan", "Purchasable plans carry
    # a `purchase` object" — captured verbatim in the committed fixture. Run the REAL
    # discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would.
    #
    # SCORE-NEUTRAL by construction: driftflight.com already claims subscription (via
    # `subscription`/`per-month`/etc.), so plan-purchase evidence can only deepen that
    # claim — never add an archetype or reorder. The classifier is off the scoring path;
    # the canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)
    assert prof.claims("subscription"), prof.archetypes
    sub = next(c for c in prof.claimed if c.archetype == "subscription")
    pp = [s for s in sub.signals if s.label == "plan-purchase"]
    assert pp, {s.label for s in sub.signals}
    q = pp[0].quote.lower()
    assert "plan" in q or "purchase" in q, pp[0].quote
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    print(f"  ok: plan-purchase fires on REAL captured driftflight.com prose — quote: {pp[0].quote!r}")

    # PRECISION-CRITICAL on real data: drift-flight.org — the no-rails-side canonical
    # anchor — has ONLY the human plan path ("subscribe to a plan on the pricing page",
    # "issued on the dashboard after subscribing to a plan"), NO programmatic purchase.
    # The signal must be ABSENT there and .org's claimed set unchanged. This is the
    # discovery-layer echo of the real capability gap: the with-rails .com exposes a
    # programmatic plan-purchase endpoint, the .org gates the commit behind a human
    # (mirroring self-provisioning / payment-receipt).
    octx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "drift-flight.org.json"))
    oprof = offering.discover_offering(octx)
    all_labels = {s.label for c in oprof.claimed for s in c.signals}
    assert "plan-purchase" not in all_labels, all_labels
    assert oprof.archetypes == ["metered_api", "digital_good", "subscription"], oprof.archetypes
    print("  ok: plan-purchase is ABSENT on drift-flight.org (real-data precision / capability gap)")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real
    # retail storefront (books.toscrape.com), and a null site (example.com) document no
    # programmatic subscription-plan purchase — plan-purchase must be absent on all three
    # and must not conjure or reorder any archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "plan-purchase" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: plan-purchase is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_plan_allowance_subscription_precision_synthetic():
    # BUNDLED MONTHLY ALLOWANCE + METERED OVERAGE — the HYBRID subscription plan whose
    # recurring fee INCLUDES a bounded per-cycle allowance that RESETS each period, with
    # usage beyond it charged as metered overage. This is the subscription-archetype
    # "understand the offer" capability the flat recurring signals miss: an agent must
    # know the flat fee buys only a bounded monthly allowance and that calls past it
    # accrue per-unit overage (a capital-safety fact), and it can budget around the cycle
    # reset. Distinct from metered_api's included/credit signals by ARCHETYPE and SENSE
    # (`free-included-usage` = a FREE $0 evaluation allowance; `credit-metered` = a
    # prepaid credit balance; `usage-based` = generic "overage"). Each POSITIVE is real
    # bundled-plan-allowance prose that must claim subscription via the new plan-allowance
    # signal; each NEGATIVE is allowance-SHAPED noise that must NOT fire it (the precision
    # traps: a FREE allowance that needs no funding — `free-included-usage`'s turf — a
    # baggage allowance, a tax allowance, and the sharpest trap, a monthly EXPENSE/food
    # allowance that is an HR perk, not a recurring plan quota).
    positives = {
        "plan's monthly allowance": "Your plan's monthly allowance resets on the first of each cycle.",
        "monthly generation allowance": "The monthly generation allowance covers 500 renders per period.",
        "subscription with included": "This is a subscription with included credit; usage beyond it is metered.",
        "monthly usage allowance": "Each tier carries a monthly usage allowance for API calls.",
        "allowance used up": "Once the included allowance used up, further calls are billed as overage.",
        "allowance resets": "The plan allowance resets every billing cycle automatically.",
        "allowance tracked per plan": "On purchased plans the allowance is tracked per plan access.",
    }
    for name, text in positives.items():
        prof = classify_offering("saas.test", {"homepage": text})
        assert prof.claims("subscription"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "subscription"
            for s in c.signals
        }
        assert "plan-allowance" in labels, (name, labels)
    print(f"  ok: {len(positives)} real plan-allowance phrasings each fire plan-allowance")

    negatives = {
        # A FREE allowance is the metered_api free-included-usage capability, not a
        # recurring PLAN quota — plan-allowance must not scoop it. Baggage / tax
        # allowances are unrelated senses. The monthly EXPENSE / food allowance is the
        # sharpest trap: "monthly ... allowance" that is an HR perk, NOT a plan quota —
        # so the monthly branch requires either a bare "monthly allowance" or a USAGE
        # noun, never a bare "monthly <anything> allowance".
        "free allowance": "A generous free allowance covers early testing.",
        "baggage allowance": "Every ticket includes a 20kg baggage allowance.",
        "tax allowance": "Claim your annual tax allowance before the April deadline.",
        "monthly expense allowance": "Staff receive a monthly expense allowance for travel.",
        "monthly food allowance": "A monthly food allowance is provided on site.",
        "personal allowance": "Set a weekly personal allowance for the kids.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"homepage": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "plan-allowance" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} allowance-shaped noise strings do NOT fire plan-allowance (precision)"
    )


def test_plan_allowance_fires_on_real_captured_subscription_prose():
    # Real-evidence, NON-VACUOUS, END-TO-END: the plan-allowance signal fires on the
    # GENUINE bundled-plan-allowance prose captured live from BOTH canonical domains —
    # drift-flight.org AND driftflight.com: "your plan's monthly allowance", the 429
    # "Monthly generation allowance used up; upgrade or wait for the cycle reset" /
    # "Plan generation allowance exhausted", and on driftflight.com additionally "a
    # subscription with included credit; usage beyond it is metered and charged per call"
    # + "the allowance is tracked per plan access". Unlike the with-rails-only plan-purchase
    # signal, this HYBRID-plan structure is documented on BOTH sides (both sell the same
    # metered subscription), so the signal fires on the PAIR — not a singleton, so it is
    # not over-fit to one fixture. Run the REAL discovery path (from_fixture ->
    # discover_offering) so the signal is exercised exactly as a live crawl would.
    #
    # SCORE-NEUTRAL by construction AND re-measured: both canonical domains already claim
    # subscription (via `subscription`/`per-month`/etc.), so plan-allowance evidence can
    # only DEEPEN that claim — never add an archetype or reorder (subscription strength
    # 4->5 on .org / 6->7 on .com, still well below digital_good's 10). The classifier is
    # off the scoring path; the canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    for dom in ("drift-flight.org", "driftflight.com"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.claims("subscription"), (dom, prof.archetypes)
        sub = next(c for c in prof.claimed if c.archetype == "subscription")
        pa = [s for s in sub.signals if s.label == "plan-allowance"]
        assert pa, (dom, {s.label for s in sub.signals})
        assert "allowance" in pa[0].quote.lower() or "included" in pa[0].quote.lower(), pa[0].quote
        assert prof.archetypes == ["metered_api", "digital_good", "subscription"], (dom, prof.archetypes)
        print(f"  ok: plan-allowance fires on REAL captured {dom} prose — quote: {pa[0].quote!r}")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real retail
    # storefront (books.toscrape.com), and a null site (example.com) document no bundled
    # subscription-plan allowance — plan-allowance must be absent on all three and must not
    # conjure or reorder any archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "plan-allowance" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: plan-allowance is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


# A synthetic bundled-subscription storefront that names its OWN host INSIDE the
# plan-allowance evidence — the host sits within the ±40-char quote window of the
# `monthly allowance` / `subscription with included` matches, so relabeling the
# host genuinely rewrites the plan-allowance quote the signal records. The
# capability the signal keys on ("your plan's monthly allowance resets each cycle;
# usage beyond it is metered") is a property of the OFFERING's own vocabulary, not
# of the host — this pins that as an executable tripwire.
_PLAN_ALLOWANCE_HOST = "acme-plans.test"
_PLAN_ALLOWANCE_NEUTRAL_HOST = "vendor-neutral.test"  # reserved .test TLD; no signal word
_PLAN_ALLOWANCE_HOMEPAGE = (
    "<html><body>"
    "<h1>Acme — metered subscription on acme-plans.test</h1>"
    "<p>Subscription $9 per month. This is a subscription with included credit on "
    "acme-plans.test. Your plan's monthly allowance on acme-plans.test resets each "
    "cycle; usage beyond the acme-plans.test allowance is metered and charged per call."
    "</p></body></html>"
)


def _plan_allowance_signals(domain: str, homepage: str):
    """The plan-allowance signals fired for ``domain`` on a synthetic homepage."""
    prof = classify_offering(domain, {"homepage": homepage})
    assert prof.claims("subscription"), (domain, prof.archetypes)
    sub = next(c for c in prof.claimed if c.archetype == "subscription")
    return [s for s in sub.signals if s.label == "plan-allowance"]


def test_plan_allowance_signal_is_relabel_invariant():
    # SIGNAL-LEVEL relabel / host-invariance guard for plan-allowance — the
    # subscription mirror of the media/render descriptor relabel guards
    # (test_battery_instantiate.py) and the classifier-level fixture relabel guard
    # (test_offering_canonical.py). It makes "whether a site claims the bundled-
    # subscription-allowance capability keys on its VOCABULARY, not its host/vendor"
    # an executable tripwire at the signal layer: a storefront that names its own
    # host inside the allowance prose fires plan-allowance identically once its host
    # is relabeled to a neutral placeholder.
    base = _plan_allowance_signals(f"api.{_PLAN_ALLOWANCE_HOST}", _PLAN_ALLOWANCE_HOMEPAGE)
    assert base, "substrate: plan-allowance fires on the base homepage"

    # Non-vacuity: the host appears INSIDE the fired plan-allowance quote, so
    # relabeling genuinely changes the text the signal recorded (not a no-op).
    assert any(_PLAN_ALLOWANCE_HOST in s.quote for s in base), (
        "the host appears in the plan-allowance evidence (relabel changes signal input "
        "— the guard is non-vacuous)"
    )

    relabeled_home = _PLAN_ALLOWANCE_HOMEPAGE.replace(
        _PLAN_ALLOWANCE_HOST, _PLAN_ALLOWANCE_NEUTRAL_HOST
    )
    relab = _plan_allowance_signals(
        f"api.{_PLAN_ALLOWANCE_NEUTRAL_HOST}", relabeled_home
    )
    assert relab, "plan-allowance still fires after the host is relabeled"
    assert all(_PLAN_ALLOWANCE_HOST not in s.quote for s in relab), (
        "every occurrence of the host was relabeled out of the plan-allowance evidence"
    )
    # The relabel genuinely changed the recorded quotes (host removed) — non-vacuous.
    assert [s.quote for s in relab] != [s.quote for s in base], (
        "the relabel genuinely changed the plan-allowance quotes (non-vacuous)"
    )
    # IDENTITY-INVARIANCE: the SET of plan-allowance sub-signal labels that fired is
    # byte-identical under relabel — the same capability is recognized regardless of
    # the host embedded alongside the allowance vocabulary.
    assert (
        sorted(s.label for s in base) == sorted(s.label for s in relab)
    ), "plan-allowance fires identically under host relabel (label set invariant)"
    print(
        f"  ok: plan-allowance signal is IDENTITY-invariant under host relabel "
        f"({len(base)} sub-signal(s), host {_PLAN_ALLOWANCE_HOST!r} in evidence, "
        "keys on offering vocabulary not host)"
    )


def test_plan_allowance_relabel_has_teeth():
    # The invariance guard above is only meaningful if a HOST-KEYED plan-allowance
    # detector WOULD be caught by the same relabel comparison. Simulate one — a
    # stub that only "fires" when the host string is present in the quote — and
    # confirm base vs relabel DIFFER under it, while the REAL signal stays invariant
    # on the identical relabel pair. So the invariance test refutes a real failure
    # mode (a site's allowance claim leaking its vendor identity), not a tautology.
    base = _plan_allowance_signals(f"api.{_PLAN_ALLOWANCE_HOST}", _PLAN_ALLOWANCE_HOMEPAGE)
    relabeled_home = _PLAN_ALLOWANCE_HOMEPAGE.replace(
        _PLAN_ALLOWANCE_HOST, _PLAN_ALLOWANCE_NEUTRAL_HOST
    )
    relab = _plan_allowance_signals(
        f"api.{_PLAN_ALLOWANCE_NEUTRAL_HOST}", relabeled_home
    )

    def _host_keyed_fires(signals):
        # A DELIBERATELY vendor-rigged detector: the exact failure the real signal
        # must not have — recognition gated on the host string, not the vocabulary.
        return any(_PLAN_ALLOWANCE_HOST in s.quote for s in signals)

    assert _host_keyed_fires(base) != _host_keyed_fires(relab), (
        "a host-keyed detector is caught by the relabel comparison (the guard has teeth)"
    )
    # ...while the REAL signal is invariant on the same pair (the property held).
    assert (
        sorted(s.label for s in base) == sorted(s.label for s in relab)
    ), "the real plan-allowance signal stays invariant on the same relabel pair the stub flips"
    print("  ok: the plan-allowance relabel guard has teeth (a host-keyed detector flips)")


# A signal-free chrome surface (privacy/cookies/careers/legal boilerplate) to bolt
# onto the plan-allowance store — the noise-axis analogue of the machine-pole guard
# in test_offering_canonical.py, but on the SYNTHETIC plan-allowance homepage so the
# axis reaches the Cycle-172 subscription signal (absent from the committed machine
# fixture). The prose deliberately carries near-miss vocabulary ("we ship ideas",
# cookie/careers/legal chrome) yet claims no capability.
_PLAN_ALLOWANCE_NOISE_SURFACE = "/privacy"
_PLAN_ALLOWANCE_NOISE_PROSE = (
    "Privacy & Cookies. We use cookies to remember your preferences and improve "
    "your experience. By continuing to browse you accept our cookie notice. We "
    "never sell your personal data.\n\n"
    "Careers. We are hiring! Join a friendly, mission-driven crew who love to ship "
    "ideas, not boxes. We value kindness, ownership, and a growth mindset.\n\n"
    "Legal. All trademarks belong to their respective owners. This notice is "
    "provided for informational purposes only and does not constitute advice."
)
# The negative control: real physical-fulfillment prose on the SAME surface key.
# physical_good is NA on the plan-allowance store, so a claim it conjures is
# unmistakably observable — proving the added-surface channel is live.
_PLAN_ALLOWANCE_NOISE_TEETH_PROSE = (
    "Add to cart. In stock now — we offer free shipping on all physical orders "
    "to your shipping address."
)


def _pa_evidence_map(prof) -> dict:
    """archetype -> (strength, its full sorted (label, surface, quote) evidence)."""
    return {
        c.archetype: (
            c.strength,
            sorted((s.label, s.surface, s.quote) for s in c.signals),
        )
        for c in prof.claimed
    }


def test_plan_allowance_noise_surface_invariance():
    # NOISE-SURFACE metamorphic axis for plan-allowance — the Cycle-171 machine-pole
    # noise guard extended to the Cycle-172 subscription signal (which the committed
    # machine fixture does not claim, so the axis needs the synthetic plan-allowance
    # store). Bolting a signal-free chrome surface (/privacy: cookies/careers/legal
    # boilerplate) onto a bundled-plan-allowance storefront must leave the WHOLE
    # capability profile byte-identical: incidental web chrome conjures no archetype,
    # no signal, and does not perturb the plan-allowance evidence. "Never manufacture
    # the delta" applied to task discovery, on the noise axis, from the subscription
    # pole.
    domain = f"api.{_PLAN_ALLOWANCE_HOST}"
    base = classify_offering(domain, {"homepage": _PLAN_ALLOWANCE_HOMEPAGE})

    # The property under test is genuinely present: the store claims a RANKED
    # multi-archetype set with plan-allowance among its subscription sub-signals, so a
    # conjured claim, a reordered rank, or a perturbed plan-allowance quote would all
    # be observable.
    assert len(base.claimed) >= 2, (
        f"substrate: >=2 archetypes claimed so the rank a noise surface could reorder "
        f"is real (got {base.archetypes})"
    )
    sub = next(c for c in base.claimed if c.archetype == "subscription")
    assert "plan-allowance" in {s.label for s in sub.signals}, (
        f"substrate: plan-allowance is among the base subscription signals "
        f"(got {sorted(s.label for s in sub.signals)})"
    )
    # The noise surface key is a genuine ADDITION, not an overwrite that could hide a
    # change.
    assert _PLAN_ALLOWANCE_NOISE_SURFACE not in base.surfaces_seen, (
        f"the noise surface {_PLAN_ALLOWANCE_NOISE_SURFACE!r} is new, not an overwrite "
        f"(base surfaces_seen {base.surfaces_seen})"
    )

    # TEETH (b): the distractor carries NO capability signal at all, despite its
    # near-miss vocabulary — so the invariance below is "noise adds no claim", not
    # "we matched an existing signal".
    assert (
        offering._scan_surface(_PLAN_ALLOWANCE_NOISE_SURFACE, _PLAN_ALLOWANCE_NOISE_PROSE)
        == []
    ), (
        "the distractor prose fires ZERO archetype signals (got "
        f"{[(s.archetype, s.label) for s in offering._scan_surface(_PLAN_ALLOWANCE_NOISE_SURFACE, _PLAN_ALLOWANCE_NOISE_PROSE)]})"
    )

    noisy = classify_offering(
        domain,
        {
            "homepage": _PLAN_ALLOWANCE_HOMEPAGE,
            _PLAN_ALLOWANCE_NOISE_SURFACE: _PLAN_ALLOWANCE_NOISE_PROSE,
        },
    )

    # TEETH (a): the noise surface was genuinely READ — it reached the classifier and
    # landed in the read-provenance record — yet contributed no claim. So the
    # invariance is non-vacuous: the classifier ingested the extra input.
    assert _PLAN_ALLOWANCE_NOISE_SURFACE in noisy.surfaces_seen, (
        f"the noise surface {_PLAN_ALLOWANCE_NOISE_SURFACE!r} was read "
        f"(surfaces_seen {noisy.surfaces_seen})"
    )

    # (1) The WHOLE classified profile is byte-identical: every archetype's strength
    # AND its complete (label, surface, quote) evidence — including the plan-allowance
    # sub-signal — survive the added surface unchanged.
    assert _pa_evidence_map(noisy) == _pa_evidence_map(base), (
        "complete per-archetype (strength, (label, surface, quote)) evidence map "
        "invariant under a signal-free added surface (plan-allowance evidence intact)"
    )
    # (2) Claimed archetypes IN RANK ORDER invariant — the rank drives the fixed
    # template-bank task order, so incidental chrome must not reorder it.
    assert noisy.archetypes == base.archetypes, (
        f"claimed archetypes (ranked) invariant under a signal-free added surface "
        f"(base {base.archetypes}, noisy {noisy.archetypes})"
    )
    # (3) The NA/unclaimed set is invariant — which archetypes the store is excused on
    # as NA is a property of WHAT it declares, not what boilerplate surrounds it.
    assert set(noisy.unclaimed) == set(base.unclaimed), (
        f"NA/unclaimed set invariant under a signal-free added surface "
        f"(base {sorted(base.unclaimed)}, noisy {sorted(noisy.unclaimed)})"
    )
    # (4) The ONLY thing that changed is read-provenance: surfaces_seen grew by exactly
    # the noise surface. This pins the honest scope — the classifier records that it
    # read the extra surface, and records nothing else from it.
    assert set(noisy.surfaces_seen) == set(base.surfaces_seen) | {
        _PLAN_ALLOWANCE_NOISE_SURFACE
    }, (
        f"surfaces_seen grew by exactly {_PLAN_ALLOWANCE_NOISE_SURFACE!r} and nothing "
        f"else (base {sorted(base.surfaces_seen)}, noisy {sorted(noisy.surfaces_seen)})"
    )

    # TEETH (c): the negative control — swap the SAME surface key for real fulfillment
    # prose. physical_good (NA at base) MUST be conjured, proving an added surface CAN
    # move the classification, so the invariance for the distractor is meaningful, not
    # a channel the classifier ignores.
    teeth = classify_offering(
        domain,
        {
            "homepage": _PLAN_ALLOWANCE_HOMEPAGE,
            _PLAN_ALLOWANCE_NOISE_SURFACE: _PLAN_ALLOWANCE_NOISE_TEETH_PROSE,
        },
    )
    assert (
        _pa_evidence_map(teeth) != _pa_evidence_map(base)
        and "physical_good" in teeth.archetypes
        and "physical_good" not in base.archetypes
    ), (
        f"a signal-BEARING added surface DOES move the profile (physical_good conjured: "
        f"{'physical_good' in teeth.archetypes}) — the added-surface channel is live, so "
        "noise-invariance is non-vacuous"
    )
    print(
        f"  ok: plan-allowance profile is byte-identical under a signal-free added "
        f"surface ({base.archetypes} ranked, plan-allowance evidence intact; teeth "
        "conjure physical_good)"
    )


def test_failure_not_billed_metering_precision_synthetic():
    # FAILURE NOT BILLED is the capital-safety leg of a metered call: a FAILED unit
    # (the render did not complete, the job errored, the request timed out) is NOT
    # charged, so an autonomous per-call buyer can bound its spend against a flaky
    # endpoint. Each POSITIVE is real failure-guarantee prose that must claim
    # metered_api via the new failure-not-billed signal; each NEGATIVE is not-charged
    # noise that must NOT fire it — the precision trap is the SUBSCRIPTION $0-eval
    # promise ("your card is not charged until the trial ends"), which is a not-charged
    # phrase with NO failure context.
    positives = {
        "did not complete": "The render did not complete; you are not charged a generation.",
        "failed not billed": "Failed requests are not billed to your account.",
        "errored no charge": "If the job errored you are not charged for it.",
        "only successful": "You are only billed for successful generations.",
        "timeout": "When a call times out you are not charged.",
        "reverse order": "You are not charged when a generation fails.",
        "unsuccessful": "Unsuccessful calls are never billed.",
    }
    for name, text in positives.items():
        prof = classify_offering("api.test", {"/docs": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "failure-not-billed" in labels, (name, labels)
    print(f"  ok: {len(positives)} real failure-not-billed phrasings each fire failure-not-billed")

    negatives = {
        "trial card": "Your card is not charged until the free trial ends.",
        "trial period": "You are not charged during the 14-day trial period.",
        "error-contract": "On failure the response body is application/problem+json.",
        "no setup charge": "There is no setup fee and no charge to get started.",
        "graceful failure": "We handle failure gracefully with automatic retries.",
        "successful custs": "Our successful customers love the fast API.",
        "not billed monthly": "You are not billed a monthly fee on the free tier.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"/docs": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "failure-not-billed" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} not-charged noise strings do NOT fire failure-not-billed (precision)"
    )


def test_failure_not_billed_fires_on_real_captured_api_docs():
    # Real-evidence, NON-VACUOUS, END-TO-END: the failure-not-billed signal fires on
    # the GENUINE capital-safety guarantee captured live from BOTH canonical domains'
    # /docs — "The render did not complete; you are not charged a generation" —
    # captured verbatim in the committed fixtures. Run the REAL discovery path
    # (from_fixture -> discover_offering) so the signal is exercised exactly as a live
    # crawl would.
    #
    # SCORE-NEUTRAL by construction: both canonical domains ALREADY claim metered_api,
    # so failure-not-billed evidence can only deepen that claim — never add an archetype
    # or reorder. The classifier is off the scoring path; the canonical pair's claimed
    # SET+ORDER is unchanged (pinned by tests/test_offering_canonical.py and the
    # canonical replay guard).
    for dom in ("driftflight.com", "drift-flight.org"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.claims("metered_api"), (dom, prof.archetypes)
        met = next(c for c in prof.claimed if c.archetype == "metered_api")
        fnb = [s for s in met.signals if s.label == "failure-not-billed"]
        assert fnb, (dom, {s.label for s in met.signals})
        q = fnb[0].quote.lower()
        assert ("not charged" in q or "not billed" in q), (dom, fnb[0].quote)
        assert prof.archetypes == ["metered_api", "digital_good", "subscription"], (
            dom,
            prof.archetypes,
        )
        print(f"  ok: failure-not-billed fires on REAL captured {dom} /docs — quote: {fnb[0].quote!r}")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real
    # retail storefront (books.toscrape.com), and a null site (example.com) document no
    # failure-not-billed guarantee — the signal must be absent on all three and must not
    # conjure or reorder any archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "failure-not-billed" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: failure-not-billed is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_reserve_and_settle_precision_synthetic():
    # RESERVE-AND-SETTLE is the capital-safety leg that bounds a SUCCESSFUL call's
    # cost: an agent reserves a spend CEILING up front, is charged only ACTUAL usage,
    # and is refunded the unused remainder — so an autonomous per-call buyer can cap
    # its worst-case exposure per request. Each POSITIVE is real reserve-and-settle
    # prose that must claim metered_api via the new signal; each NEGATIVE is a
    # reserve/refund/ceiling homonym that must NOT fire it — the precision traps are a
    # hotel "reservation", "we reserve the right", a retail "full refund", cloud
    # "reserved capacity", a "ceiling fan", and the subscription/failure not-charged
    # phrasings that belong to OTHER signals.
    positives = {
        "named rail": "The x402 rail uses reserve-and-pay-actual settlement.",
        "reserve ceiling": (
            "Your wallet reserves the ceiling up front, then you are charged only actual."
        ),
        "charged actual anchored": "You are charged only for actual usage against a reserved ceiling.",
        "escrow refund": "The channel closes at your actual usage so the escrow refunds the rest.",
        "refund remainder": "We reserve a per-call ceiling and refund the remainder you did not use.",
    }
    for name, text in positives.items():
        prof = classify_offering("api.test", {"/llms.txt": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "reserve-and-settle" in labels, (name, labels)
    print(f"  ok: {len(positives)} real reserve-and-settle phrasings each fire reserve-and-settle")

    negatives = {
        "hotel reservation": "Make a reservation for two at 7pm.",
        "reserve the right": "We reserve the right to change these terms at any time.",
        "retail refund": "Full refund within 30 days, no questions asked.",
        "reserved capacity": "Purchase reserved capacity for predictable cloud pricing.",
        "ceiling fan": "The ceiling fan ships in two colors.",
        "trial not charged": "Your card is not charged until the free trial ends.",
        "charged monthly": "You are charged only once per month for the plan.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"/llms.txt": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "reserve-and-settle" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} reserve/refund/ceiling homonym strings do NOT fire "
        "reserve-and-settle (precision)"
    )


def test_reserve_and_settle_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the reserve-and-settle signal fires on
    # the GENUINE reserve-and-pay-actual prose captured live from driftflight.com — the
    # agents.driftflight.com/llms.txt agent docs "your wallet reserves the ceiling up
    # front, then you are charged only actual … the escrow refunds the rest" — captured
    # verbatim in the committed fixture. Run the REAL discovery path (from_fixture ->
    # discover_offering) so the signal is exercised exactly as a live crawl would, the
    # same real-data non-vacuity move test_payment_receipt_fires_on_real_captured_surfaces
    # makes.
    #
    # SCORE-NEUTRAL by construction: driftflight.com already claims metered_api (its
    # strongest archetype), so reserve-and-settle evidence can only deepen that claim —
    # never add an archetype or reorder. The classifier is off the scoring path; the
    # canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    ras = [s for s in metered.signals if s.label == "reserve-and-settle"]
    assert ras, {s.label for s in metered.signals}
    q = ras[0].quote.lower()
    assert ("ceiling" in q or "reserve-and-pay-actual" in q or "actual" in q), ras[0].quote
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    print(f"  ok: reserve-and-settle fires on REAL captured driftflight.com prose — quote: {ras[0].quote!r}")

    # PRECISION-CRITICAL on real data: drift-flight.org — the no-rails-side canonical
    # anchor — carries NO reserve-and-settle prose at all (it publishes no llms.txt).
    # The signal must be ABSENT there and .org's claimed set unchanged. This is the
    # discovery-layer echo of the real capability gap: the with-rails .com documents a
    # reserve-and-pay-actual rail, the .org does not (mirroring payment-receipt /
    # self-provisioning).
    octx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "drift-flight.org.json"))
    oprof = offering.discover_offering(octx)
    all_labels = {s.label for c in oprof.claimed for s in c.signals}
    assert "reserve-and-settle" not in all_labels, all_labels
    assert oprof.archetypes == ["metered_api", "digital_good", "subscription"], oprof.archetypes
    print("  ok: reserve-and-settle is ABSENT on drift-flight.org (real-data precision / capability gap)")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real
    # retail storefront (books.toscrape.com), and a null site (example.com) document no
    # reserve-and-settle rail — the signal must be absent on all three and must not
    # conjure or reorder any archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "reserve-and-settle" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: reserve-and-settle is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_free_included_usage_precision_synthetic():
    # FREE-INCLUDED-USAGE is the metered_api ON-RAMP: an agent can complete a REAL
    # metered call at $0 before committing money — a per-account free ALLOWANCE of
    # actual units (an `includedUnits` contract), usable at a zero balance with no
    # funding. Each POSITIVE is real free-allowance prose that must claim metered_api
    # via the new signal; each NEGATIVE is a "free"/"trial" homonym that must NOT fire
    # it — the precision traps are free shipping (physical), a free trial (a recurring
    # subscription's window, a DIFFERENT signal), royalty-free, toll-free, "feel free",
    # free parking/WiFi, and a plan's paid-in "included units per month".
    positives = {
        "free usage per account": "Some pay-as-you-go prices carry free usage per account that needs no funding.",
        "free allowance": "The free allowance needs no funding and no human signup.",
        "includedUnits free": "A price's `includedUnits` is the number of free units per period.",
        "free included units": "Free included usage: the first N free included units cost nothing.",
        "try before money": "A zero-balance identity can try this API end to end before any money is involved.",
    }
    for name, text in positives.items():
        prof = classify_offering("api.test", {"/llms.txt": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "free-included-usage" in labels, (name, labels)
    print(f"  ok: {len(positives)} real free-allowance phrasings each fire free-included-usage")

    negatives = {
        "free shipping": "Enjoy free shipping on all orders over $50.",
        "free trial": "Start your 14-day free trial today, no card required.",
        "royalty free": "All renders are royalty-free for commercial use.",
        "toll free": "Call our toll-free support line any time.",
        "feel free": "Feel free to reach out with questions.",
        "free parking": "The venue includes free parking for guests.",
        "paid included units": "Your plan includes 500 units per month at no extra charge.",
        "read before pay": "Read the docs before you pay for a plan.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"/llms.txt": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "free-included-usage" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} free/trial/included homonym strings do NOT fire "
        "free-included-usage (precision)"
    )


def test_free_included_usage_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the free-included-usage signal fires on
    # the GENUINE free-allowance prose captured live from driftflight.com — the
    # agents.driftflight.com/llms.txt + llms-full.txt + manifest.json agent docs
    # ("`includedUnits` - free usage per account that needs no funding", "a freshly
    # provisioned identity with a zero balance ... can try this API end to end before
    # any money is involved") — captured verbatim in the committed fixture. Run the
    # REAL discovery path (from_fixture -> discover_offering) so the signal is exercised
    # exactly as a live crawl would, the same real-data non-vacuity move
    # test_reserve_and_settle_fires_on_real_captured_surfaces makes.
    #
    # SCORE-NEUTRAL by construction: driftflight.com already claims metered_api (its
    # strongest archetype), so free-included-usage evidence can only deepen that claim —
    # never add an archetype or reorder. The classifier is off the scoring path; the
    # canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "driftflight.com.json"))
    prof = offering.discover_offering(ctx)
    assert prof.claims("metered_api"), prof.archetypes
    metered = next(c for c in prof.claimed if c.archetype == "metered_api")
    fiu = [s for s in metered.signals if s.label == "free-included-usage"]
    assert fiu, {s.label for s in metered.signals}
    q = fiu[0].quote.lower()
    assert ("free" in q or "included" in q or "before" in q), fiu[0].quote
    assert prof.archetypes == ["metered_api", "digital_good", "subscription"], prof.archetypes
    print(f"  ok: free-included-usage fires on REAL captured driftflight.com prose — quote: {fiu[0].quote!r}")

    # PRECISION-CRITICAL on real data: drift-flight.org — the no-rails-side canonical
    # anchor — carries NO free-allowance prose at all (it publishes no llms.txt). The
    # signal must be ABSENT there and .org's claimed set unchanged. This is the
    # discovery-layer echo of the real capability gap: the with-rails .com documents a
    # free try-before-you-fund on-ramp, the .org does not (mirroring payment-receipt /
    # reserve-and-settle).
    octx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, "drift-flight.org.json"))
    oprof = offering.discover_offering(octx)
    all_labels = {s.label for c in oprof.claimed for s in c.signals}
    assert "free-included-usage" not in all_labels, all_labels
    assert oprof.archetypes == ["metered_api", "digital_good", "subscription"], oprof.archetypes
    print("  ok: free-included-usage is ABSENT on drift-flight.org (real-data precision / capability gap)")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real
    # retail storefront (books.toscrape.com), and a null site (example.com) document no
    # free-allowance on-ramp — the signal must be absent on all three and must not
    # conjure or reorder any archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "free-included-usage" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: free-included-usage is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_variant_selection_precision_synthetic():
    # VARIANT-SELECTION is the digital_good "complete the job with a USABLE
    # deliverable" leg: whether an agent can DISCOVER and SELECT which output variant
    # a generative service produces (a named, listable style preset it passes on the
    # request) so it obtains a fit-for-purpose, REPRODUCIBLE deliverable rather than a
    # nondeterministic one. Each POSITIVE is real variant-selection prose that must
    # claim digital_good via the new signal; each NEGATIVE is a "model"/"preset"
    # homonym that must NOT fire it — the precision traps are the bare "model"
    # minefield (a language/business/role/3D model, which is why "model" is NEVER
    # matched), a billing "tier" (owned by metered_api `tiered-volume`), the preset
    # VERB ("preset the oven"), factory/camera presets, and "reset".
    positives = {
        "style presets": "Every render uses one of our style presets for a consistent look.",
        "preset slug": "Pass a preset slug on the request to lock the look.",
        "preset string param": "preset string — a style preset slug (see presets below).",
        "pick a preset": "Pick a preset, send your prompt, and every render matches.",
        "browse presets": "Browse presets and choose the one that fits your campaign.",
        "select a preset": "Select a preset so the whole catalog stays consistent.",
        "preset locks style": "A preset locks palette, lighting, and rendering style across prompts.",
    }
    for name, text in positives.items():
        prof = classify_offering("gen.test", {"/llms.txt": text})
        assert prof.claims("digital_good"), (name, prof.archetypes)
        labels = {
            s.label
            for c in prof.claimed
            if c.archetype == "digital_good"
            for s in c.signals
        }
        assert "variant-selection" in labels, (name, labels)
    print(f"  ok: {len(positives)} real variant-selection phrasings each fire variant-selection")

    negatives = {
        "language model": "We fine-tuned a large language model on your corpus.",
        "business model": "Our business model is a flat monthly subscription.",
        "role model": "She has always been a role model for the team.",
        "3d model": "Import a 3D model of the building into the scene.",
        "model number": "The device model number is printed on the back.",
        "billing tier": "Higher volume tiers unlock committed-use discounts.",
        "preset verb oven": "Preset the oven to 200C before you start.",
        "factory preset": "Restore the factory preset to clear your changes.",
        "reset password": "Reset your password from the account page.",
    }
    for name, text in negatives.items():
        prof = classify_offering("noise.test", {"/llms.txt": text})
        labels = {s.label for c in prof.claimed for s in c.signals}
        assert "variant-selection" not in labels, (name, labels, prof.archetypes)
    print(
        f"  ok: {len(negatives)} model/preset/tier homonym strings do NOT fire "
        "variant-selection (precision)"
    )


def test_variant_selection_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the variant-selection signal fires on the
    # GENUINE preset-selection prose captured live from BOTH canonical domains — the
    # homepage/docs "Pick a preset", "style presets", "Browse presets", and the `preset`
    # request-parameter "A style preset slug" — captured verbatim in the committed
    # fixtures. Run the REAL discovery path (from_fixture -> discover_offering) so the
    # signal is exercised exactly as a live crawl would.
    #
    # UNLIKE payment/rails signals (free-included-usage, plan-purchase, self-provisioning)
    # this fires on BOTH canonical sides, NOT only .com: output-variant selection is a
    # DELIVERABLE-CONTROL capability BOTH image-generation storefronts genuinely share,
    # not a with-rails/no-rails gap. That is the honest reading — the signal is not there
    # to widen the delta, it is there to measure a real generative-good capability.
    #
    # SCORE-NEUTRAL by construction: both domains already claim digital_good, so
    # variant-selection evidence can only deepen that claim — never add an archetype or
    # reorder. The classifier is off the scoring path; the canonical pair's claimed
    # SET+ORDER is unchanged (pinned by tests/test_offering_canonical.py and the
    # canonical replay guard).
    for dom in ("driftflight.com", "drift-flight.org"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.claims("digital_good"), (dom, prof.archetypes)
        dg = next(c for c in prof.claimed if c.archetype == "digital_good")
        vs = [s for s in dg.signals if s.label == "variant-selection"]
        assert vs, (dom, {s.label for s in dg.signals})
        assert "preset" in vs[0].quote.lower(), (dom, vs[0].quote)
        assert prof.archetypes == ["metered_api", "digital_good", "subscription"], (dom, prof.archetypes)
        print(f"  ok: variant-selection fires on REAL captured {dom} prose — quote: {vs[0].quote!r}")

    # NON-VACUOUS negatives: a metered-API marketplace (api.replicate.com), a real retail
    # storefront (books.toscrape.com), and a null site (example.com) document no
    # output-variant selection — the signal must be absent on all three and must not
    # conjure or reorder any archetype (in particular it must NOT conjure digital_good on
    # the metered_api-only api.replicate.com, whose docs are full of the bare "model"
    # homonym the signal deliberately never matches).
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "variant-selection" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: variant-selection is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_concurrency_limit_precision_synthetic():
    # A NEW metered_api capability signal: the CONCURRENCY CEILING + queue-depth
    # backpressure — how many jobs an agent may run IN PARALLEL at once, and the
    # response-header signal it reads to PACE that parallelism. This is the "complete
    # the job AT SCALE" leg, DISTINCT from `rate-limited`: rate-limited is the
    # TEMPORAL axis (how OFTEN — requests per minute, a request quota), concurrency is
    # the PARALLELISM axis (how many jobs in flight at once — "2 concurrent renders").
    # The two are orthogonal quotas: an agent may be well under its per-minute rate
    # yet blocked by a 2-in-flight concurrency ceiling. Precision is the whole game —
    # bare "concurrent"/"parallel"/"queue" is a false-positive minefield (concurrent
    # jurisdiction, a parallel universe, a checkout queue, an NVMe queue-depth
    # benchmark, "concurrent users" — a seat/session concept, not job parallelism) —
    # so the signal requires a COUNT of concurrent JOB-nouns, a concurrency LIMIT/CAP,
    # a max concurrency, an `X-*-Queue-Depth` response header, or the explicit
    # BACKPRESSURE construction. Each POSITIVE fires `concurrency-limit` with no other
    # metered_api signal rescuing it (so it exercises the branch directly); each
    # NEGATIVE must NOT claim metered_api on its own.
    #
    # Canonical-invariant by construction: the signal fires on BOTH canonical domains
    # (both are image-generation storefronts whose /docs rate-limits block documents
    # a concurrency ceiling — a SHARED deliverable-scale capability, NOT a
    # payment/rails gap, mirroring output-resolution / variant-selection), each
    # already metered_api's strongest archetype → no reorder; ABSENT on the
    # api/retail/null fixtures (pinned by tests/test_offering_canonical.py). Off the
    # scoring path.
    positives = {
        # The real captured canonical /docs prose (verbatim shapes).
        "count concurrent renders": "Hobby: 2 concurrent renders. Studio: 6.",
        "queue-depth response header": "the x-df-queue-depth response header reports the current queue.",
        "queue rather than fail": "Bursts beyond the limit queue rather than fail.",
        # Genuine concurrency-capability vocabulary from other real APIs.
        "concurrency limit": "Your plan has a concurrency limit of six.",
        "concurrency cap": "A concurrency cap of 4 applies per key.",
        "max concurrent jobs": "You may run at most max concurrent jobs of 4.",
        "concurrent request cap": "A concurrent request cap applies per key.",
        "maximum concurrency": "The maximum concurrency for your tier is 10.",
        "per-plan concurrent predictions": "Studio grants 6 per-plan concurrent predictions.",
        "queued instead of rejected": "Extra calls are queued instead of rejected.",
        "generic queue-depth header": "Read the x-acme-queue-depth header to self-throttle.",
    }
    for name, text in positives.items():
        prof = classify_offering("scale.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "concurrency-limit" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} concurrency-ceiling phrasings each fire concurrency-limit")

    negatives = {
        # Broad-English "concurrent"/"parallel"/"queue" that must NOT conjure a
        # metered_api claim.
        "concurrent jurisdiction": "The courts have concurrent jurisdiction over the matter.",
        "concurrent medication": "Avoid concurrent medication without a doctor's advice.",
        "parallel universe": "Imagine a parallel universe of design.",
        "in parallel": "We run our creative process in parallel.",
        "parallel processing": "Enjoy the beauty of parallel processing of ideas.",
        "checkout queue": "Skip the checkout queue with express delivery.",
        "join the queue": "Join the queue for early access.",
        "nvme queue depth": "The SSD sustains a queue depth of 32 in benchmarks.",
        "concurrent users": "Supports up to 500 concurrent users on the site.",
        "concurrent sessions": "Two concurrent sessions per household.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("metered_api"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} bare concurrent/parallel/queue strings do NOT claim metered_api (precision)"
    )


def test_concurrency_limit_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of the synthetic
    # precision guard. It pins that the new concurrency signal fires on the GENUINE
    # concurrency-ceiling prose captured live from BOTH canonical domains' /docs
    # rate-limits block ("Hobby: 2 concurrent renders ... Bursts beyond the limit
    # queue rather than fail; the `x-df-queue-depth` response header reports the
    # current queue."), run through the REAL discovery path (from_fixture ->
    # discover_offering) exactly as a live crawl would.
    #
    # UNLIKE the with-rails/no-rails PAYMENT signals (free-included-usage,
    # payment-receipt, self-provisioning) this fires on BOTH canonical sides, NOT only
    # .com: a concurrency ceiling is a deliverable-SCALE capability BOTH image-generation
    # storefronts genuinely share, not a rails gap. That is the honest reading — the
    # signal measures a real "complete the job at scale" capability, not the delta.
    #
    # SCORE-NEUTRAL by construction: both domains already claim metered_api (their
    # strongest archetype), so the concurrency evidence can only deepen that claim —
    # never add an archetype or reorder. The classifier is off the scoring path; the
    # canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    for dom in ("driftflight.com", "drift-flight.org"):
        docs = _fixture_entry_text(dom, "/docs")
        assert "concurrent" in docs, f"{dom} /docs lost its concurrency-ceiling prose"
        prof = classify_offering(dom, {"/docs": docs})
        assert prof.claims("metered_api"), (dom, prof.archetypes)
        metered = next(c for c in prof.claimed if c.archetype == "metered_api")
        cc = [s for s in metered.signals if s.label == "concurrency-limit"]
        assert cc, (dom, {s.label for s in metered.signals})
        assert "concurrent" in cc[0].quote.lower(), cc[0].quote
        # Non-vacuity beyond the single recorded hit: the SAME captured /docs block
        # documents the FULL self-pacing contract an agent needs at scale — the
        # parallel-jobs ceiling ("N concurrent renders"), the queue-depth backpressure
        # HEADER, and the "queue rather than fail" backpressure semantics — each an
        # independent branch of the signal (proven against the fixture bytes, since the
        # classifier records only the first-firing instance per label).
        assert "x-df-queue-depth" in docs, dom
        assert "queue rather than fail" in docs.lower(), dom
        print(f"  ok: concurrency-limit fires on REAL captured {dom} /docs — quote: {cc[0].quote!r}")

    # Full-discovery claimed-set invariance on the canonical pair (score-neutrality).
    for dom in ("driftflight.com", "drift-flight.org"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.archetypes == ["metered_api", "digital_good", "subscription"], (dom, prof.archetypes)

    # NON-VACUOUS negatives on REAL data: a metered-API marketplace (api.replicate.com,
    # which carries NO concurrent/queue-depth prose), a real retail storefront
    # (books.toscrape.com), and a null site (example.com) document no concurrency
    # ceiling — the signal must be absent on all three and conjure or reorder no
    # archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "concurrency-limit" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: concurrency-limit is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def test_key_rotation_precision_synthetic():
    # A NEW metered_api capability signal: the CREDENTIAL LIFECYCLE / KILL-SWITCH —
    # whether a held API key can be ROTATED and the old one REVOKED (immediately).
    # This is the "operate safely without a human" leg: a long-running agent holds a
    # key across many calls, a key can leak, and a metered API that documents key
    # rotation + immediate revocation lets the agent (or its operator) kill the
    # compromised credential and swap a fresh one WITHOUT a human re-onboarding.
    # DISTINCT from `api-auth` (how you PRESENT a held credential) and
    # `self-provisioning` (OBTAINING one without a human — the lifecycle START): this
    # is the lifecycle END. Precision is the whole game — bare "revoke"/"rotate" is a
    # false-positive minefield (revoke consent/access/license — ToS boilerplate;
    # rotate the image/stock, a rotating carousel, crop rotation), and CRITICALLY both
    # canonical /docs carry the 401 ERROR row "the key is unknown or revoked" (an
    # error-status meaning, NOT the rotation capability) which must NOT fire — so the
    # signal requires the token to NAME A KEY in a rotation/kill sense. Each POSITIVE
    # fires `key-rotation` with no other metered_api signal rescuing it (so it
    # exercises the branch directly); each NEGATIVE must NOT claim metered_api.
    #
    # Canonical-invariant by construction: the signal fires on BOTH canonical domains
    # (both metered image APIs whose /docs document the same key-rotation lifecycle —
    # a SHARED credential-safety capability, NOT a payment/rails gap, mirroring
    # concurrency-limit / output-resolution), each already metered_api's strongest
    # archetype → no reorder; ABSENT on the api/retail/null fixtures (pinned by
    # tests/test_offering_canonical.py). Off the scoring path.
    positives = {
        # The real captured canonical /docs prose (verbatim shapes).
        "rotate any key": "Rotate any key from the dashboard; old keys are revoked immediately.",
        "old keys revoked": "Old keys are revoked immediately.",
        # Genuine key-rotation vocabulary from other real API docs.
        "rotate your api key": "You can rotate your API key at any time.",
        "rotate keys": "Rotate keys from the dashboard whenever you like.",
        "revoke a key": "Revoke a key instantly if it leaks.",
        "revoke your api key": "Revoke your API key from the dashboard to kill it.",
        "keys can be rotated": "API keys can be rotated and issued from the console.",
        "key rotation": "We support automatic API key rotation.",
    }
    for name, text in positives.items():
        prof = classify_offering("cred.test", {"homepage": text})
        assert prof.claims("metered_api"), (name, prof.archetypes)
        fired = {
            s.label
            for c in prof.claimed
            if c.archetype == "metered_api"
            for s in c.signals
        }
        assert "key-rotation" in fired, (name, sorted(fired))  # non-vacuous
    print(f"  ok: {len(positives)} key-rotation phrasings each fire key-rotation")

    negatives = {
        # Broad-English "revoke"/"rotate" that must NOT conjure a metered_api claim.
        "revoke consent": "You may revoke consent at any time.",
        "revoke access": "We may revoke access to your account.",
        "revoke license": "We reserve the right to revoke your license.",
        "rotate the image": "Rotate the image 90 degrees before uploading.",
        "rotate stock": "We rotate stock seasonally for freshness.",
        "rotating carousel": "A rotating carousel of featured banners.",
        "crop rotation": "Crop rotation improves soil yield year over year.",
        "rotate the menu": "We rotate our seasonal menu every quarter.",
    }
    for name, text in negatives.items():
        prof = classify_offering("prose.test", {"homepage": text})
        assert not prof.claims("metered_api"), (name, prof.archetypes)
    print(
        f"  ok: {len(negatives)} bare revoke/rotate strings do NOT claim metered_api (precision)"
    )

    # CRITICAL discriminator, tested at the SIGNAL level: the 401 error row present in
    # BOTH canonical /docs — "No API key, or the key is unknown or revoked" — legitimately
    # trips `api-auth` (it names an API key), so it DOES claim metered_api; the point is
    # that it must NOT fire `key-rotation` (an error-status MEANING is not the rotation
    # capability). This is the harder, honest case: the discriminator must hold even inside
    # a genuine metered_api surface, exactly as it does on the canonical pair.
    err = classify_offering("err.test", {"homepage": "No API key, or the key is unknown or revoked."})
    err_fired = {
        s.label for c in err.claimed if c.archetype == "metered_api" for s in c.signals
    }
    assert "key-rotation" not in err_fired, err_fired
    assert "api-auth" in err_fired, err_fired  # non-vacuous: it IS a metered_api surface
    print("  ok: the 401 'key ... revoked' error row fires api-auth but NOT key-rotation (discriminator)")


def test_key_rotation_fires_on_real_captured_surfaces():
    # Real-evidence, NON-VACUOUS, END-TO-END: the TRUTH mirror of the synthetic
    # precision guard. It pins that the new key-rotation signal fires on the GENUINE
    # credential-lifecycle prose captured live from BOTH canonical domains' /docs
    # ("Rotate any key from the dashboard; old keys are revoked immediately."), run
    # through the REAL discovery path (from_fixture -> discover_offering) exactly as a
    # live crawl would.
    #
    # UNLIKE the with-rails/no-rails PAYMENT signals (free-included-usage,
    # payment-receipt, self-provisioning) this fires on BOTH canonical sides, NOT only
    # .com: key rotation is a credential-SAFETY capability BOTH metered image APIs
    # genuinely share, not a rails gap. That is the honest reading — the signal
    # measures a real "operate safely" capability, not the delta.
    #
    # SCORE-NEUTRAL by construction: both domains already claim metered_api (their
    # strongest archetype), so the key-rotation evidence can only deepen that claim —
    # never add an archetype or reorder. The classifier is off the scoring path; the
    # canonical pair's claimed SET+ORDER is unchanged (pinned by
    # tests/test_offering_canonical.py and the canonical replay guard).
    for dom in ("driftflight.com", "drift-flight.org"):
        docs = _fixture_entry_text(dom, "/docs")
        assert "rotate" in docs.lower(), f"{dom} /docs lost its key-rotation prose"
        prof = classify_offering(dom, {"/docs": docs})
        assert prof.claims("metered_api"), (dom, prof.archetypes)
        metered = next(c for c in prof.claimed if c.archetype == "metered_api")
        kr = [s for s in metered.signals if s.label == "key-rotation"]
        assert kr, (dom, {s.label for s in metered.signals})
        assert "key" in kr[0].quote.lower(), kr[0].quote
        # Non-vacuity beyond the single recorded hit: the SAME captured /docs sentence
        # carries BOTH independent branches an agent reads for the lifecycle — the
        # imperative ROTATE ("Rotate any key") and the superseded-key KILL ("old keys
        # are revoked") — proven against the classifier-visible (whitespace-collapsed,
        # HTML-stripped) prose, since the raw capture line-wraps mid-phrase ("old keys\n
        # are revoked") and the classifier records only the first-firing instance per label.
        prose = " ".join(strip_html(docs).split()).lower()
        assert "rotate any key" in prose, dom
        assert "old keys are revoked" in prose, dom
        # The 401 error row ("the key is unknown or revoked") lives in the SAME /docs
        # and must NOT be what fired the signal — the recorded quote is the rotation
        # sentence, never the error row.
        assert "unknown or revoked" not in kr[0].quote.lower(), kr[0].quote
        print(f"  ok: key-rotation fires on REAL captured {dom} /docs — quote: {kr[0].quote!r}")

    # Full-discovery claimed-set invariance on the canonical pair (score-neutrality).
    for dom in ("driftflight.com", "drift-flight.org"):
        ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        prof = offering.discover_offering(ctx)
        assert prof.archetypes == ["metered_api", "digital_good", "subscription"], (dom, prof.archetypes)

    # NON-VACUOUS negatives on REAL data: a metered-API marketplace (api.replicate.com,
    # which carries NO key-rotation prose), a real retail storefront
    # (books.toscrape.com), and a null site (example.com) document no key-rotation
    # lifecycle — the signal must be absent on all three and conjure or reorder no
    # archetype.
    for dom, expected in (
        ("api.replicate.com", ["metered_api"]),
        ("books.toscrape.com", ["physical_good"]),
        ("example.com", []),
    ):
        nctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{dom}.json"))
        nprof = offering.discover_offering(nctx)
        nlabels = {s.label for c in nprof.claimed for s in c.signals}
        assert "key-rotation" not in nlabels, (dom, nlabels)
        assert nprof.archetypes == expected, (dom, nprof.archetypes)
    print("  ok: key-rotation is ABSENT on the api / retail / null fixtures (non-vacuous, score-neutral)")


def main() -> int:
    tests = [
        test_api_storefront_claims_agent_native_not_physical,
        test_retail_storefront_is_the_inverse,
        test_sku_inventory_is_retail_sense_not_compute,
        test_credit_metered_precision_synthetic,
        test_credit_metered_fires_on_real_captured_billing_prose,
        test_rate_limit_metering_precision_synthetic,
        test_rate_limit_fires_on_real_captured_api_docs,
        test_tiered_volume_metering_precision_synthetic,
        test_tiered_volume_fires_on_real_captured_billing_prose,
        test_test_mode_metering_precision_synthetic,
        test_test_mode_fires_on_real_captured_api_docs,
        test_seat_licensing_subscription_precision_synthetic,
        test_booking_and_data_archetypes_fire,
        test_data_retrieval_precision_synthetic,
        test_data_retrieval_precision_is_canonical_invariant_on_real_fixtures,
        test_service_booking_book_precision_synthetic,
        test_service_booking_schedule_precision_synthetic,
        test_data_retrieval_lookup_precision_synthetic,
        test_batch_retrieval_precision_synthetic,
        test_batch_retrieval_fires_on_real_captured_surfaces,
        test_service_booking_manage_precision_synthetic,
        test_manage_booking_fires_on_real_captured_surfaces,
        test_service_booking_notification_precision_synthetic,
        test_booking_notification_fires_on_real_captured_surfaces,
        test_service_booking_intake_form_precision_synthetic,
        test_intake_form_fires_on_real_captured_surfaces,
        test_subscription_recurring_precision_synthetic,
        test_usage_based_metered_precision_synthetic,
        test_payment_challenge_retry_precision_synthetic,
        test_payment_challenge_retry_fires_on_real_captured_surfaces,
        test_non_storefront_claims_nothing,
        test_strength_counts_distinct_signals_and_orders_claims,
        test_classification_is_surface_read_order_invariant,
        test_classification_is_whitespace_reflow_invariant,
        test_classification_is_html_entity_decode_invariant,
        test_classification_is_non_html_surface_entity_invariant,
        test_classification_is_intra_word_hyphen_invariant,
        test_classification_is_invisible_formatting_invariant,
        test_evidence_is_quoted_and_surface_tagged,
        test_openapi_spec_alone_classifies_api_first_storefront,
        test_ai_plugin_descriptor_alone_classifies_storefront,
        test_a2a_agent_card_alone_classifies_storefront,
        test_html_docs_page_alone_classifies_storefront,
        test_openapi_surface_is_wired_for_live_discovery,
        test_doc_subdomain_helper_is_precise_and_ssrf_safe,
        test_doc_subdomain_surfaces_are_read_live,
        test_docs_surface_is_read_live,
        test_agent_payment_rail_precision_synthetic,
        test_agent_payment_rail_fires_on_real_captured_surfaces,
        test_no_rails_side_claims_no_agent_payment_rail,
        test_pricing_surface_is_read_live,
        test_async_job_metering_precision_synthetic,
        test_async_job_fires_on_real_captured_openapi,
        test_api_auth_precision_synthetic,
        test_api_auth_fires_on_real_captured_surfaces,
        test_error_contract_precision_synthetic,
        test_error_contract_fires_on_real_captured_surfaces,
        test_generate_media_recognizes_plural_and_participle_forms,
        test_generate_media_plural_gap_on_real_captured_docs,
        test_output_license_precision_synthetic,
        test_output_license_fires_on_real_captured_surfaces,
        test_content_provenance_precision_synthetic,
        test_content_provenance_fires_on_real_captured_surfaces,
        test_output_resolution_precision_synthetic,
        test_output_resolution_fires_on_real_captured_surfaces,
        test_output_retention_precision_synthetic,
        test_output_retention_fires_on_real_captured_surfaces,
        test_pagination_metering_precision_synthetic,
        test_pagination_fires_on_real_captured_openapi,
        test_cancel_job_metering_precision_synthetic,
        test_cancel_job_fires_on_real_captured_openapi,
        test_streaming_response_metering_precision_synthetic,
        test_streaming_response_fires_on_real_captured_openapi,
        test_self_provisioning_precision_synthetic,
        test_self_provisioning_fires_on_real_captured_surfaces,
        test_payment_receipt_precision_synthetic,
        test_payment_receipt_fires_on_real_captured_surfaces,
        test_webhook_verification_precision_synthetic,
        test_webhook_verification_fires_on_real_captured_openapi,
        test_free_trial_subscription_precision_synthetic,
        test_free_trial_fires_on_real_captured_subscription_prose,
        test_plan_purchase_subscription_precision_synthetic,
        test_plan_purchase_fires_on_real_captured_subscription_prose,
        test_plan_allowance_subscription_precision_synthetic,
        test_plan_allowance_fires_on_real_captured_subscription_prose,
        test_plan_allowance_signal_is_relabel_invariant,
        test_plan_allowance_relabel_has_teeth,
        test_plan_allowance_noise_surface_invariance,
        test_failure_not_billed_metering_precision_synthetic,
        test_failure_not_billed_fires_on_real_captured_api_docs,
        test_reserve_and_settle_precision_synthetic,
        test_reserve_and_settle_fires_on_real_captured_surfaces,
        test_free_included_usage_precision_synthetic,
        test_free_included_usage_fires_on_real_captured_surfaces,
        test_variant_selection_precision_synthetic,
        test_variant_selection_fires_on_real_captured_surfaces,
        test_concurrency_limit_precision_synthetic,
        test_concurrency_limit_fires_on_real_captured_surfaces,
        test_key_rotation_precision_synthetic,
        test_key_rotation_fires_on_real_captured_surfaces,
        test_priced_listing_precision_synthetic,
        test_priced_listing_fires_on_real_captured_retail,
        test_strip_html_drops_script_style_and_tags,
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
