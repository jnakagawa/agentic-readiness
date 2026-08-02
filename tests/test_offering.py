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
        # is single-surface.
        "homepage": "Our plans are billed monthly. Book a demo appointment.",
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
        test_non_storefront_claims_nothing,
        test_strength_counts_distinct_signals_and_orders_claims,
        test_classification_is_surface_read_order_invariant,
        test_classification_is_whitespace_reflow_invariant,
        test_classification_is_html_entity_decode_invariant,
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
