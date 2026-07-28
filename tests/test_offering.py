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

import os
import sys

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import offering  # noqa: E402
from asrs.offering import ARCHETYPES, classify_offering, strip_html  # noqa: E402


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


def test_openapi_surface_is_wired_for_live_discovery():
    # A structural guard: the OpenAPI conventions, the agent-plugin descriptor, AND
    # the A2A agent card are actually in the surface list `discover_offering`
    # fetches live (not merely handled by the pure classifier). Without this, a
    # spec-only / descriptor-only / agent-card-only site would never be READ. The
    # natural-language docs remain covered too (no regression to the surface set).
    docs = offering._SURFACE_DOCS
    for path in ("/openapi.json", "/.well-known/openapi.json", "/swagger.json"):
        assert path in docs, f"{path} missing from discovery surfaces: {docs}"
    assert "/.well-known/ai-plugin.json" in docs, f"ai-plugin descriptor missing: {docs}"
    for path in ("/.well-known/agent.json", "/.well-known/agent-card.json"):
        assert path in docs, f"A2A agent card {path} missing from discovery surfaces: {docs}"
    for path in ("/llms.txt", "/llms-full.txt", "/manifest.json"):
        assert path in docs, f"regressed natural-language surface {path}: {docs}"
    print(f"  ok: OpenAPI/Swagger + ai-plugin + A2A agent-card surfaces wired, got {docs}")


def test_strip_html_drops_script_style_and_tags():
    out = strip_html(API_HOMEPAGE)
    # The <script>/<style> commerce-word noise must NOT survive stripping — else
    # it would false-positive physical_good on this API site.
    assert "var s" not in out and "color:red" not in out, out[:200]
    assert "<" not in out and ">" not in out
    # Plain text passes through unchanged (llms.txt has no tags).
    assert strip_html("plain text, no tags") == "plain text, no tags"
    print("  ok: strip_html removes script/style/tags, passes plain text through")


def main() -> int:
    tests = [
        test_api_storefront_claims_agent_native_not_physical,
        test_retail_storefront_is_the_inverse,
        test_sku_inventory_is_retail_sense_not_compute,
        test_booking_and_data_archetypes_fire,
        test_non_storefront_claims_nothing,
        test_strength_counts_distinct_signals_and_orders_claims,
        test_evidence_is_quoted_and_surface_tagged,
        test_openapi_spec_alone_classifies_api_first_storefront,
        test_ai_plugin_descriptor_alone_classifies_storefront,
        test_a2a_agent_card_alone_classifies_storefront,
        test_openapi_surface_is_wired_for_live_discovery,
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
