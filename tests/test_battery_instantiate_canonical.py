"""Canonical offering-relative BATTERY guard — the operator directive's core
deliverable (task SELECTION), made executable on REAL committed evidence.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_battery_instantiate_canonical.py

The operator directive (2026-07-23, BACKLOG P0) makes the task battery
OFFERING-RELATIVE: a site is probed only with intents for the archetypes it
actually CLAIMS, and archetypes it does NOT serve are omitted (later marked NA,
excluded from every mean/spread, never penalized). Its stated acceptance is:

    "driftflight.com shows physical_good = NA (not a completion number) with
     spreads over claimed archetypes only; a retail storefront shows the inverse.
     Card and terminal readouts show NA archetypes as 'not offered'."

Two layers realize that: `discover_offering` / `classify_offering` decides WHICH
archetypes a site claims, and `instantiate_battery` turns that profile into the
battery's actual TASK SET — one parameterized intent per claimed archetype, in
fixed template-bank order for cross-site comparability, omitting the rest.

`tests/test_offering_canonical.py` (Cycle 27/31) pins the DISCOVERY layer on the
committed fixtures. But `instantiate_battery` — the step that turns the operator
criterion into the battery an agent actually runs — was pinned only against
SYNTHETIC profiles (`tests/test_battery_instantiate.py`, hand-built homepages),
and end-to-end on REAL storefronts only in transient [LOCAL] behavioral run logs
(`runs/local/acceptance_battery_*`, gitignored). This test closes that gap: it
replays each committed fixture through the FULL real pipeline
(`FetchContext.from_fixture -> discover_offering -> instantiate_battery`, no
network) and pins the generated TASK SET, so the acceptance criterion —
driftflight instantiates NO physical-good task, a retail storefront instantiates
ONLY a physical-good task — is an in-cloud per-cycle tripwire, not a run-log fact.

Real storefront TYPES covered (task-battery breadth, the COVERAGE north star):
  - the agent-native image-generation API pair (drift-flight.org / driftflight.com)
    -> {metered_api, subscription, digital_good} tasks, NO physical/booking/data
       task, and the digital_good intent PARAMETERIZED to "generated image" from
       the site's OWN discovered media evidence (the operator's literal example,
       "buy an AI-generated image for an image API");
  - a real book-catalog retail storefront (books.toscrape.com) -> ONLY a
    physical_good task (the operator's "a retail storefront shows the inverse");
  - a real generic model-inference API (api.replicate.com, machine-surface-first)
    -> ONLY a metered_api task — the compute-SKU precision boundary
    (test_offering_canonical) carried through to task selection, so a generic
    inference platform gets no spurious fulfillment intent;
  - a non-storefront documentation page (example.com) -> an EMPTY battery (an
    honest "nothing to assess", never a fabricated task).

NON-VACUOUS: the digital_good descriptor is asserted to be the evidence-derived
"generated image", NOT the generic "digital output" fallback — proving the intent
was parameterized from the site's DISCOVERED offering, not a static template; and
the retail/replicate/empty cases prove the pipeline is not a constant function.

Vendor-neutral: intents reference the offering GENERICALLY ("the service", "the
site's primary physical product") — this test asserts no generated intent contains
the storefront's domain or host label, so the battery text is capability-worded,
never vendor-worded. Domains appear here only as committed fixture PATHS (the same
domain-as-data pattern as test_offering_canonical), never as scored-check prose.

Score-neutral: `instantiate_battery` performs task SELECTION only — it touches no
check, weight, cap, aggregation rule, or the scoring path (grep-verifiable: this
change is tests-only, `git diff -- asrs/ rubric/` is empty). It moves no canonical
score and the rubric stays untouched.

Maintenance contract (mirrors test_offering_canonical): if a signal-bank or
template change LEGITIMATELY alters what a canonical domain claims (and thus its
task set), re-capture the fixtures [LOCAL] and update the EXPECTED_TASKS below in
the SAME PR. A canonical image-gen domain gaining a physical_good task absent new
fulfillment evidence is NOT a legitimate change: it is the battery-pollution
regression the operator directive removed, and this guard exists to catch it.

No network: every surface is served from the fixture's recorded response cache.
Discovery TOLERATES a missing surface by design, so this guard pins the TASK-SET
outcome, not fixture coverage.
"""

from __future__ import annotations

import os
import sys

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs.battery import instantiate_battery  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.offering import ARCHETYPES, discover_offering  # noqa: E402

_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# The offering-relative TASK SET each committed storefront instantiates, in fixed
# template-bank order (ARCHETYPES order — `instantiate_battery` iterates the bank,
# so the order is stable for cross-site comparability regardless of claim strength).
# Reproduced byte-faithfully from the committed fixtures via the real pipeline; the
# same evidence the [LOCAL] acceptance runs (18:55Z .com / 23:10Z retail) confirmed
# behaviorally.
EXPECTED_TASKS: dict[str, list[str]] = {
    # Agent-native image-generation APIs: metered call, subscription, generated
    # image — NEVER a physical good, service booking, or data-retrieval intent.
    "drift-flight.org": ["metered_api", "subscription", "digital_good"],
    "driftflight.com": ["metered_api", "subscription", "digital_good"],
    # Retail book catalog: the operator's inverse — ONLY a physical-good intent.
    "books.toscrape.com": ["physical_good"],
    # Generic model-inference API (machine-surface-first): ONLY a metered call —
    # the compute-SKU precision boundary keeps it from a spurious fulfillment task.
    "api.replicate.com": ["metered_api"],
    # A bare documentation page is not a storefront: an honest empty battery.
    "example.com": [],
}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _instantiate(domain: str):
    """Replay ``<domain>.json`` through discover_offering -> instantiate_battery."""
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    profile = discover_offering(ctx)
    battery = instantiate_battery(profile)
    return profile, battery


def _assert_task_set(domain: str) -> None:
    profile, battery = _instantiate(domain)
    kinds = [t.kind for t in battery.tasks]
    expected = EXPECTED_TASKS[domain]

    # The battery instantiates EXACTLY the claimed archetypes, in template-bank
    # order — one task per claimed archetype, none for the unclaimed rest.
    _check(
        kinds == expected,
        f"{domain}: battery task kinds == {expected} (got {kinds}) — one intent per "
        "CLAIMED archetype, in fixed template-bank order",
    )

    # Every task's id equals its kind equals an archetype (cross-site comparable).
    _check(
        all(t.id == t.kind and t.kind in ARCHETYPES for t in battery.tasks),
        f"{domain}: every task id==kind and names an archetype "
        f"(got {[(t.id, t.kind) for t in battery.tasks]})",
    )

    # The task set is exactly the claimed set: what the site instantiates is what
    # discovery said it claims (the two layers agree on REAL evidence). Compared as
    # SETS — discovery orders by claim STRENGTH, instantiation by fixed template-bank
    # order, so the members must match though the orders legitimately differ.
    _check(
        set(kinds) == set(profile.archetypes),
        f"{domain}: task set == discovered claimed set {sorted(set(profile.archetypes))} "
        f"(got {sorted(set(kinds))}) — instantiation tracks discovery",
    )

    # The NOT-instantiated archetypes are exactly the site's unclaimed set — the
    # future-NA archetypes, omitted (never a fabricated task, never a penalty).
    not_instantiated = [a for a in ARCHETYPES if a not in kinds]
    _check(
        not_instantiated == profile.unclaimed,
        f"{domain}: NOT-instantiated archetypes == unclaimed/NA set "
        f"{profile.unclaimed} (got {not_instantiated})",
    )

    # Vendor-neutral: no generated intent embeds the storefront's domain, its
    # registrable host, or its DISTINCTIVE second-level label — intents reference
    # the offering generically ("the service"). We key on the second-level label
    # (replicate / driftflight / drift-flight / toscrape), NOT a generic subdomain
    # prefix like "api", which is a capability word that legitimately appears in
    # "metered API" and is not a vendor identity.
    host = domain[4:] if domain.startswith("www.") else domain
    labels = host.split(".")
    sld = labels[-2] if len(labels) >= 2 else host  # the distinctive vendor token
    vendor_tokens = {domain, host, sld}
    for t in battery.tasks:
        low = t.intent.lower()
        leaked = sorted(v for v in vendor_tokens if v in low)
        _check(
            not leaked,
            f"{domain}: task '{t.kind}' intent is vendor-neutral (no domain/host/vendor "
            f"token {leaked}): {t.intent!r}",
        )


def test_canonical_image_api_pair_task_set() -> None:
    """The image-gen API pair instantiates metered/subscription/digital, no physical."""
    print("test_canonical_image_api_pair_task_set")
    for domain in ("drift-flight.org", "driftflight.com"):
        _assert_task_set(domain)
        # The operator's named criterion at the TASK layer: physical_good yields
        # NO task (it is NA, "not a completion number"), likewise booking/data.
        _, battery = _instantiate(domain)
        kinds = {t.kind for t in battery.tasks}
        for na in ("physical_good", "service_booking", "data_retrieval"):
            _check(
                na not in kinds,
                f"{domain}: no {na} task instantiated — the operator's "
                f"'physical_good = NA, not a completion number' at the task layer",
            )


def test_digital_good_intent_is_parameterized_from_real_evidence() -> None:
    """The digital_good intent is 'generated image', derived from the site's OWN
    discovered media evidence — the operator's 'buy an AI-generated image for an
    image API' — NOT the generic 'digital output' fallback (so it is genuinely
    parameterized by the offering, not a static template)."""
    print("test_digital_good_intent_is_parameterized_from_real_evidence")
    for domain in ("drift-flight.org", "driftflight.com"):
        _, battery = _instantiate(domain)
        dg = [t for t in battery.tasks if t.kind == "digital_good"]
        _check(len(dg) == 1, f"{domain}: exactly one digital_good task (got {len(dg)})")
        intent = dg[0].intent
        _check(
            "generated image" in intent,
            f"{domain}: digital_good intent names 'generated image' from discovered "
            f"media evidence (got {intent!r})",
        )
        # NON-VACUOUS: it is NOT the generic fallback, so the descriptor really was
        # filled from the site's evidence, not a constant template.
        _check(
            "digital output" not in intent,
            f"{domain}: digital_good intent is NOT the generic 'digital output' "
            f"fallback — it was parameterized by the offering (got {intent!r})",
        )


def test_retail_inverse_task_set() -> None:
    """A retail storefront instantiates ONLY a physical-good task — the operator's
    'a retail storefront shows the inverse', at the task layer."""
    print("test_retail_inverse_task_set")
    _assert_task_set("books.toscrape.com")
    _, battery = _instantiate("books.toscrape.com")
    kinds = {t.kind for t in battery.tasks}
    _check(
        kinds == {"physical_good"},
        f"books.toscrape.com: instantiates ONLY a physical_good task (got {sorted(kinds)}) "
        "— the inverse of the image-gen pair, which instantiates none",
    )
    for api in ("metered_api", "subscription", "digital_good"):
        _check(
            api not in kinds,
            f"books.toscrape.com: no {api} task — the archetypes the canonical pair "
            "claims are the retail store's NA set (inverse of the pair)",
        )


def test_machine_surface_api_task_set() -> None:
    """A generic model-inference API instantiates ONLY a metered_api task — the
    compute-SKU precision boundary (no spurious physical fulfillment intent)."""
    print("test_machine_surface_api_task_set")
    _assert_task_set("api.replicate.com")
    _, battery = _instantiate("api.replicate.com")
    kinds = {t.kind for t in battery.tasks}
    _check(
        kinds == {"metered_api"},
        f"api.replicate.com: instantiates ONLY a metered_api task (got {sorted(kinds)}) "
        "— a generic inference platform gets no fulfillment/booking/data intent",
    )
    _check(
        "physical_good" not in kinds,
        "api.replicate.com: no physical_good task despite the 'SKU for the hardware' "
        "compute-SKU prose — the precision boundary carries into task selection",
    )


def test_nonstorefront_empty_battery() -> None:
    """A bare documentation page yields an empty battery — no fabricated task."""
    print("test_nonstorefront_empty_battery")
    _assert_task_set("example.com")
    _, battery = _instantiate("example.com")
    _check(
        battery.tasks == [],
        f"example.com: empty battery (got {[t.kind for t in battery.tasks]}) — an "
        "honest 'nothing to assess', never a fabricated intent",
    )


def test_same_archetype_is_comparable_across_real_sites() -> None:
    """The SAME archetype yields the SAME intent across different real storefronts —
    cross-site comparability on REAL evidence: the metered_api intent an agent runs
    against an image-gen API is byte-identical to the one it runs against a generic
    inference API, so their metered-call readiness numbers compare like-for-like."""
    print("test_same_archetype_is_comparable_across_real_sites")
    _, a = _instantiate("driftflight.com")
    _, b = _instantiate("api.replicate.com")
    a_metered = next(t.intent for t in a.tasks if t.kind == "metered_api")
    b_metered = next(t.intent for t in b.tasks if t.kind == "metered_api")
    _check(
        a_metered == b_metered,
        "metered_api intent is identical across two real API storefronts "
        f"(driftflight.com vs api.replicate.com) — cross-site comparable:\n"
        f"    {a_metered!r}\n    {b_metered!r}",
    )


def main() -> int:
    tests = [
        test_canonical_image_api_pair_task_set,
        test_digital_good_intent_is_parameterized_from_real_evidence,
        test_retail_inverse_task_set,
        test_machine_surface_api_task_set,
        test_nonstorefront_empty_battery,
        test_same_archetype_is_comparable_across_real_sites,
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
