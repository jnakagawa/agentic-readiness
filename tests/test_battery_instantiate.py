"""Tests for offering-relative battery instantiation (asrs/battery.py, brick 2).

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_battery_instantiate.py

Brick 2 of the operator directive: turn discovered offering archetypes
(:mod:`asrs.offering`) into the battery's task set, so a site is only ever
probed with intents it actually offers. Covered here with SYNTHETIC surfaces /
profiles (no network, no CLIs):

  - an image-API offering yields the metered/subscription/digital intents and NO
    physical-good task — the operator's core acceptance, expressed in task
    SELECTION terms (physical_good is simply not a task, so it can never pollute
    a mean or spread);
  - a retail offering is the inverse (a physical-good task, no metered/digital);
  - an offering that claims nothing yields an EMPTY battery (honest "nothing to
    assess", never a fabricated task);
  - generated intents are vendor-neutral (the site's own domain never appears in
    an intent) and the digital_good intent is parameterized from discovered,
    vendor-neutral media language ("generated image" / "translated document" /
    generic "digital output" fallback);
  - task ids ARE the archetype names, in fixed template-bank order regardless of
    claim strength — so the same archetype lines up across sites (comparability).

The Driftflight-flavoured API strings appear ONLY as fixture text (the spec
permits vendor details in tests); they mirror the live canonical surfaces so the
offline test tracks what the live classifier + instantiator actually produce.
"""

from __future__ import annotations

import os
import sys

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.battery import (  # noqa: E402
    Battery,
    BatteryTask,
    _digital_good_descriptor,
    instantiate_battery,
)
from asrs.offering import (  # noqa: E402
    ARCHETYPES,
    ArchetypeClaim,
    ArchetypeSignal,
    OfferingProfile,
    classify_offering,
)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


# --- Fixtures: synthetic surfaces mirroring real archetypes -------------------

# An agent-native text-to-image API storefront: metered API + subscription +
# digital good (image generation), and deliberately NO physical-fulfillment
# language, so physical_good must stay unclaimed.
IMAGE_API_HOMEPAGE = """
<html><body>
<h1>Drift Flight — text-to-image API</h1>
<p>POST https://api.drift-flight.test/v1/images/generate with a prompt.
This is a pay-per-call image generation API, usage-based and billed per image.</p>
<p>Pricing: Hobby $5 per month, 100 generations / month. Subscription plans for
every pipeline. Outputs are hosted output URLs, downloadable and rendered fast.</p>
</body></html>
"""

# A translation-flavoured digital-good site (no media noun in the digital claim,
# but the translation signal fires) — exercises the "translated document"
# descriptor branch.
TRANSLATION_HOMEPAGE = """
<html><body>
<h1>Lingua — translation API</h1>
<p>GET https://api.lingua.test/v1/translate — pay per request, usage-based.
We translate a short document between two languages. Subscription $9 per month.</p>
</body></html>
"""

# A physical retail storefront: the inverse. Free shipping / add to cart / in
# stock / SKU — and no API / subscription / digital-generation language.
RETAIL_HOMEPAGE = """
<html><body>
<h1>Nimbus Goods</h1>
<p>Free shipping on every order. Add to cart to check out. In stock now.
Physical products with a returns policy; each SKU tracked in inventory.</p>
</body></html>
"""


def _profile(domain: str, homepage: str) -> OfferingProfile:
    return classify_offering(domain, {"homepage": homepage})


# --- Tests --------------------------------------------------------------------

def test_image_api_gets_offering_relative_tasks():
    prof = _profile("drift-flight.test", IMAGE_API_HOMEPAGE)
    _check("physical_good" not in prof.archetypes,
           f"image API does not claim physical_good, claimed={prof.archetypes}")

    bat = instantiate_battery(prof)
    kinds = [t.kind for t in bat.tasks]
    # Exactly the claimed archetypes become tasks — no physical-good intent to
    # pollute the means/spreads.
    _check(set(kinds) == set(prof.archetypes),
           f"tasks cover exactly the claimed archetypes, got {kinds}")
    _check("physical_good" not in kinds,
           "NO physical_good task is generated for an image API (operator acceptance)")
    # The digital_good intent is parameterized from discovered media language.
    dg = next(t for t in bat.tasks if t.kind == "digital_good")
    _check("generated image" in dg.intent,
           f"digital_good intent specialized to the discovered media, got: {dg.intent!r}")


def test_retail_is_the_inverse():
    prof = _profile("nimbus.test", RETAIL_HOMEPAGE)
    bat = instantiate_battery(prof)
    kinds = [t.kind for t in bat.tasks]
    _check("physical_good" in kinds, f"retail site gets a physical_good task, got {kinds}")
    _check("metered_api" not in kinds and "digital_good" not in kinds,
           f"retail site gets no metered/digital intents (the inverse), got {kinds}")
    phys = next(t for t in bat.tasks if t.kind == "physical_good")
    _check("physical product" in phys.intent,
           f"physical_good intent references the site's physical product, got: {phys.intent!r}")


def test_empty_profile_yields_empty_battery():
    prof = OfferingProfile(domain="example.test", claimed=[])
    bat = instantiate_battery(prof)
    _check(bat.tasks == [], "a site that claims nothing yields an empty battery (nothing fabricated)")
    _check("none" in bat.description,
           f"empty battery description names its (absence of) archetypes, got: {bat.description!r}")


def test_generated_intents_are_vendor_neutral():
    for domain, home in (("drift-flight.test", IMAGE_API_HOMEPAGE), ("nimbus.test", RETAIL_HOMEPAGE)):
        prof = _profile(domain, home)
        bat = instantiate_battery(prof)
        for t in bat.tasks:
            _check(domain not in t.intent,
                   f"intent for {t.kind} never names the site's own domain")
    print("  ok: no generated intent leaks a domain/vendor string")


def test_ids_are_archetypes_in_template_bank_order():
    prof = _profile("drift-flight.test", IMAGE_API_HOMEPAGE)
    # Discovery sorts claimed by strength; instantiation must NOT — ids follow the
    # fixed ARCHETYPES order so the same archetype lines up across sites.
    bat = instantiate_battery(prof)
    ids = [t.id for t in bat.tasks]
    _check(all(t.id == t.kind for t in bat.tasks), "each task's id IS its archetype (== kind)")
    expected = [a for a in ARCHETYPES if a in set(prof.archetypes)]
    _check(ids == expected,
           f"tasks are in fixed template-bank order, got {ids} vs {expected}")


def test_same_archetype_is_comparable_across_sites():
    # Both sites claim subscription; the task id must be identical so a battery
    # readout compares within-archetype across sites (brick 5 comparability).
    a = instantiate_battery(_profile("drift-flight.test", IMAGE_API_HOMEPAGE))
    b = instantiate_battery(_profile("lingua.test", TRANSLATION_HOMEPAGE))
    sub_a = next(t for t in a.tasks if t.kind == "subscription")
    sub_b = next(t for t in b.tasks if t.kind == "subscription")
    _check(sub_a.id == sub_b.id == "subscription",
           "the subscription archetype has the same task id on both sites")
    _check(sub_a.intent == sub_b.intent,
           "the subscription intent is identical across sites (fixed template)")


def test_digital_good_descriptor_branches():
    # translation signal -> translated document (even without a media noun)
    prof_tr = _profile("lingua.test", TRANSLATION_HOMEPAGE)
    tr_claim = next((c for c in prof_tr.claimed if c.archetype == "digital_good"), None)
    _check(tr_claim is not None and _digital_good_descriptor(tr_claim) == "translated document",
           "translation signal -> 'translated document' descriptor")

    # a media noun in the fired signal -> 'generated <noun>'
    media_claim = ArchetypeClaim(
        archetype="digital_good",
        signals=[ArchetypeSignal("digital_good", "homepage", "generation", "fast image generation for agents")],
    )
    _check(_digital_good_descriptor(media_claim) == "generated image",
           "media noun -> 'generated image' descriptor")

    # no media noun / no translation -> generic fallback
    plain_claim = ArchetypeClaim(
        archetype="digital_good",
        signals=[ArchetypeSignal("digital_good", "homepage", "hosted-output", "hosted output URLs, downloadable")],
    )
    _check(_digital_good_descriptor(plain_claim) == "digital output",
           "no media/translation hint -> 'digital output' fallback")
    _check(_digital_good_descriptor(None) == "digital output",
           "a missing claim -> 'digital output' fallback (never crashes)")


def test_instantiation_touches_no_scoring_state():
    # Sanity: instantiate_battery returns a Battery of BatteryTask and nothing
    # more — it constructs a definition, it does not score. (The aggregation math
    # and the rubric are untouched; brick 3 is the peer-gated aggregation change.)
    bat = instantiate_battery(_profile("drift-flight.test", IMAGE_API_HOMEPAGE))
    _check(isinstance(bat, Battery) and all(isinstance(t, BatteryTask) for t in bat.tasks),
           "instantiate_battery yields a Battery of BatteryTask (task selection only)")


def main() -> int:
    tests = [
        test_image_api_gets_offering_relative_tasks,
        test_retail_is_the_inverse,
        test_empty_profile_yields_empty_battery,
        test_generated_intents_are_vendor_neutral,
        test_ids_are_archetypes_in_template_bank_order,
        test_same_archetype_is_comparable_across_sites,
        test_digital_good_descriptor_branches,
        test_instantiation_touches_no_scoring_state,
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
