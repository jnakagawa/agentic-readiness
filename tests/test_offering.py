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
        test_booking_and_data_archetypes_fire,
        test_non_storefront_claims_nothing,
        test_strength_counts_distinct_signals_and_orders_claims,
        test_evidence_is_quoted_and_surface_tagged,
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
