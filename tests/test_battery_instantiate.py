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


def test_digital_good_descriptor_recovers_plural_media():
    """A PLURAL-only fired media quote yields the SAME singular 'generated <noun>'
    descriptor as the singular form — the descriptor half of the Cycle-94
    generate-media plural/participle recall fix.

    Before this, ``_MEDIA_RE`` recognised only the SINGULAR media noun, so a
    digital_good claim whose ONLY fired quote was plural ("Generated images",
    "we generate videos") fell back to the generic "digital output" descriptor
    even though the generate-media SIGNAL (asrs/offering.py) had fired on that
    same plural surface — a vaguer battery task than the site's own offering
    warranted. The descriptor now matches the signal: plural in, singular
    "generated <noun>" out. Off the scoring path (``--battery auto`` task text).
    """
    import re as _re

    # (a) The REAL canonical /docs phrasing ("Generated images", Cycle 94) as the
    #     ONLY fired media quote -> the descriptor recovers "generated image",
    #     NOT the generic fallback.
    plural_claim = ArchetypeClaim(
        archetype="digital_good",
        signals=[ArchetypeSignal("digital_good", "/docs", "generate-media",
                                 "Generated images are returned as hosted URLs")],
    )
    _check(_digital_good_descriptor(plural_claim) == "generated image",
           "a plural-only media quote ('Generated images') -> 'generated image' descriptor")

    # TEETH / non-vacuity: the pre-fix SINGULAR-ONLY pattern does NOT match that
    # quote, so this recovery closes a REAL gap (the test would fail against the
    # old code — it is not vacuously green).
    _old_singular_only = _re.compile(r"\b(image|video|audio|art)\b", _re.IGNORECASE)
    _check(_old_singular_only.search("Generated images are returned as hosted URLs") is None,
           "the pre-fix singular-only media pattern does NOT match 'images' (the gap was real)")

    # (b) Each media noun recovers its SINGULAR descriptor from the plural form.
    for quote, noun in (
        ("we generate videos on demand", "video"),
        ("stream generated images to agents", "image"),
        ("a gallery of generative arts", "art"),
    ):
        c = ArchetypeClaim(
            archetype="digital_good",
            signals=[ArchetypeSignal("digital_good", "homepage", "generate-media", quote)],
        )
        _check(_digital_good_descriptor(c) == f"generated {noun}",
               f"plural in {quote!r} -> 'generated {noun}' descriptor")

    # PRECISION: a plural NON-media noun ('reports'/'outputs') still falls back —
    # the trailing ``s?`` pluralises only the media bank, it never invents a
    # media descriptor from a non-media word.
    non_media = ArchetypeClaim(
        archetype="digital_good",
        signals=[ArchetypeSignal("digital_good", "homepage", "hosted-output",
                                 "generated reports and outputs, downloadable")],
    )
    _check(_digital_good_descriptor(non_media) == "digital output",
           "a plural NON-media noun ('reports'/'outputs') -> 'digital output' fallback (precision)")

    # The SINGULAR form is unchanged (regression pin for the existing branch).
    singular = ArchetypeClaim(
        archetype="digital_good",
        signals=[ArchetypeSignal("digital_good", "homepage", "generate-media", "fast image generation for agents")],
    )
    _check(_digital_good_descriptor(singular) == "generated image",
           "the singular media noun still -> 'generated image' (unchanged)")


# --- Descriptor relabel-invariance (the descriptor-layer vendor-neutrality guard) -
#
# `test_offering_canonical.py` makes the offering CLASSIFIER vendor-neutral an
# executable tripwire: relabel a fixture's host everywhere and the CLAIMED/NA
# partition is identical, proving task SELECTION keys on evidence, not identity.
# The offering-relative digital_good BATTERY task carries a second identity risk
# one layer down: its {descriptor} slot (`_digital_good_descriptor`) derives the
# media noun ("generated image" / "translated document") from the fired signal's
# label + quote — and the host string appears INSIDE that evidence (the canonical
# generate-media / hosted-output quotes embed `…api.<host>/…`). If the descriptor
# ever keyed on the host — deriving the task noun from a domain word — two
# storefronts offering the same capability would get DIFFERENT task text because
# of their NAMES, the vendor-rigging the directive forbids, applied to the task
# WORDING rather than task selection. The methodology prose now CLAIMS the noun
# "comes from the site, not ASRS" and is "injection-safe" (Cycle 96); this makes
# that claim an executable tripwire at the descriptor layer — the descriptor-level
# analog of the signal-level relabel guards.
#
# Method (mirrors `_assert_offering_relabel_invariant`): classify a synthetic
# surface that names the host INSIDE the digital_good evidence, extract the real
# claim, relabel the host everywhere and re-classify, and assert the derived
# descriptor is byte-identical. NON-VACUOUS by substrate: the host genuinely
# appears in the base claim's evidence and the relabel genuinely changes the quote
# text the descriptor reads (both asserted), and the neutral host carries no media
# word — so invariance is real, not a no-op. `_descriptor_relabel_has_teeth`
# proves the assertion can fail: a host-keyed descriptor IS caught by it.
_NEUTRAL_HOST = "vendor-neutral.test"  # reserved .test TLD; no media-bank word

# A generation storefront that names its own host inside the digital_good
# evidence — so relabeling the host genuinely rewrites the quote the descriptor
# reads (the media noun "images" is what should drive the descriptor, not the host).
_MEDIA_HOST_HOMEPAGE = """
<html><body>
<h1>Acme — text-to-image API</h1>
<p>POST https://api.acme-vendor.test/v1/images/generate with a prompt.
Pay per call. Generated images are returned as hosted URLs from api.acme-vendor.test.</p>
<p>Subscription $5 per month.</p>
</body></html>
"""
# A translation storefront that names its host inside the digital_good evidence —
# the "translated document" branch keys on the `translation` LABEL, also not the host.
_TRANSLATE_HOST_HOMEPAGE = """
<html><body>
<h1>Lingua — translation API on api.acme-vendor.test</h1>
<p>GET https://api.acme-vendor.test/v1/translate — pay per request. We translate a
short document between two languages at api.acme-vendor.test. Subscription $9 per month.</p>
</body></html>
"""
_HOST = "acme-vendor.test"


def _digital_good_claim(domain: str, homepage: str) -> ArchetypeClaim:
    prof = classify_offering(domain, {"homepage": homepage})
    claim = next((c for c in prof.claimed if c.archetype == "digital_good"), None)
    _check(claim is not None, f"{domain}: a digital_good claim is discovered (test substrate is real)")
    return claim


def _assert_descriptor_relabel_invariant(homepage: str, expected: str) -> None:
    base = _digital_good_claim(f"api.{_HOST}", homepage)
    base_desc = _digital_good_descriptor(base)
    _check(base_desc == expected,
           f"base descriptor is {expected!r} (got {base_desc!r})")

    # Non-vacuity: the host appears in the digital_good evidence the descriptor
    # reads, so relabeling genuinely changes that input (not a no-op).
    host_in_evidence = any(_HOST in s.quote or _HOST in s.label for s in base.signals)
    _check(host_in_evidence,
           f"the host appears in the digital_good evidence (relabel changes descriptor "
           "input — the guard is non-vacuous)")

    relabeled_home = homepage.replace(_HOST, _NEUTRAL_HOST)
    relab = _digital_good_claim(f"api.{_NEUTRAL_HOST}", relabeled_home)
    _check(all(_HOST not in s.quote for s in relab.signals),
           "every occurrence of the host was relabeled out of the evidence")
    _check([s.quote for s in relab.signals] != [s.quote for s in base.signals],
           "the relabel genuinely changed the evidence quotes (non-vacuous)")

    relab_desc = _digital_good_descriptor(relab)
    _check(relab_desc == base_desc,
           f"digital_good descriptor is IDENTITY-invariant under host relabel "
           f"(base {base_desc!r}, relabel {relab_desc!r}) — the media noun keys on "
           "the site's VOCABULARY, not its host/vendor")


def test_digital_good_descriptor_is_relabel_invariant_media():
    # The 'generated image' (media-noun) branch: the descriptor keys on the media
    # word 'images' in the fired quote, not the host embedded alongside it.
    _assert_descriptor_relabel_invariant(_MEDIA_HOST_HOMEPAGE, "generated image")


def test_digital_good_descriptor_is_relabel_invariant_translation():
    # The 'translated document' branch: the descriptor keys on the `translation`
    # signal LABEL, not the host embedded in the fired quote.
    _assert_descriptor_relabel_invariant(_TRANSLATE_HOST_HOMEPAGE, "translated document")


def test_descriptor_relabel_has_teeth():
    # The relabel-invariance assertion is only meaningful if a host-keyed descriptor
    # WOULD be caught. Simulate one (deriving the noun from the host string) and
    # confirm base vs relabel descriptors DIFFER under it — so the invariant tests
    # above are refuting a real failure mode, not asserting a tautology.
    base = _digital_good_claim(f"api.{_HOST}", _MEDIA_HOST_HOMEPAGE)
    relab = _digital_good_claim(
        f"api.{_NEUTRAL_HOST}", _MEDIA_HOST_HOMEPAGE.replace(_HOST, _NEUTRAL_HOST))

    def _host_keyed_descriptor(claim):
        # A DELIBERATELY vendor-rigged descriptor: the exact failure the real
        # descriptor must not have — noun taken from a host word in the evidence.
        for sig in claim.signals:
            if "acme" in sig.quote:
                return "acme output"
            if "neutral" in sig.quote:
                return "neutral output"
        return "digital output"

    _check(_host_keyed_descriptor(base) != _host_keyed_descriptor(relab),
           "a host-keyed descriptor is caught by the relabel comparison (the guard has teeth)")
    # ...while the REAL descriptor is invariant on the same pair (the property held).
    _check(_digital_good_descriptor(base) == _digital_good_descriptor(relab),
           "the real descriptor stays invariant on the same relabel pair the stub flips")


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
        test_digital_good_descriptor_recovers_plural_media,
        test_digital_good_descriptor_is_relabel_invariant_media,
        test_digital_good_descriptor_is_relabel_invariant_translation,
        test_descriptor_relabel_has_teeth,
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
