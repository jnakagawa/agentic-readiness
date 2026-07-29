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
        test_seat_licensing_subscription_precision_synthetic,
        test_booking_and_data_archetypes_fire,
        test_non_storefront_claims_nothing,
        test_strength_counts_distinct_signals_and_orders_claims,
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
