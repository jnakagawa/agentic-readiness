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
        test_non_storefront_claims_nothing,
        test_strength_counts_distinct_signals_and_orders_claims,
        test_classification_is_surface_read_order_invariant,
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
        test_pagination_metering_precision_synthetic,
        test_pagination_fires_on_real_captured_openapi,
        test_cancel_job_metering_precision_synthetic,
        test_cancel_job_fires_on_real_captured_openapi,
        test_streaming_response_metering_precision_synthetic,
        test_streaming_response_fires_on_real_captured_openapi,
        test_self_provisioning_precision_synthetic,
        test_self_provisioning_fires_on_real_captured_surfaces,
        test_free_trial_subscription_precision_synthetic,
        test_free_trial_fires_on_real_captured_subscription_prose,
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
