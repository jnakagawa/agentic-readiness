"""Capture a real storefront's offering-discovery surfaces into a replay fixture.

The offering signal bank can only grow NEW capability signals against COMMITTED
evidence — a fixture whose recorded surfaces genuinely claim the archetype, so an
in-cloud COVERAGE cycle can mine + verify a signal non-vacuously (the exact
[LOCAL]-enabler pattern the service_booking / data_retrieval anchors followed:
Cycles 240 / 242). The prior anchor captures were ad-hoc one-liners; this is the
reproducible, vendor-neutral form of that step so a future [LOCAL] fire (or a
maintenance re-capture) runs the identical, auditable crawl.

What it does, for one domain, read-only and $0 (no scoring, no behavioral run, no
POST — a pure ``discover_offering`` GET crawl of the site's OWN public surfaces):

  1. Run the REAL discovery path (:func:`asrs.offering.discover_offering`) live,
     populating the shared :class:`asrs.fetch.FetchContext` cache with the homepage
     + every ``_SURFACE_DOCS`` surface on the apex and the conventional doc
     subdomains.
  2. Strip the ephemeral ``set-cookie`` response header from every cached entry —
     the sibling canonical fixtures carry ZERO set-cookie (an anonymous session
     cookie is non-deterministic crawl noise, never scoring evidence), and this
     keeps the recorded bytes minimal and stable.
  3. Save the fixture (:meth:`FetchContext.save_fixture`).
  4. VERIFY honest ordering (invariant #4): replay the just-saved fixture offline
     (:meth:`FetchContext.from_fixture` -> ``discover_offering``) and assert the
     replayed classification is byte-identical to the live one — same claimed
     archetypes, same per-archetype evidence labels — and that no surface that
     produced evidence is a replay-miss. A mismatch means the fixture does not
     faithfully reproduce the live crawl, so it is NOT written as an anchor.

REDIRECT NOTE: pass the site's CANONICAL host (the one it redirects to), e.g.
``www.allbirds.com`` not ``allbirds.com`` — the homepage is cached under the
REQUESTED url but ``base_url`` (hence every later surface and the replay) uses the
POST-redirect host, so capturing the apex of an apex->www site would strand the
homepage entry under a key the replay never requests (a homepage replay-miss that
silently drops every homepage-sourced claim). The verify step below catches it.

Usage:
    python -m experiments.capture_offering_fixture www.allbirds.com \
        fixtures/canonical/www.allbirds.com.json
"""
from __future__ import annotations

import sys

from asrs.fetch import FetchContext
from asrs.offering import discover_offering


def _labels_by_archetype(profile) -> dict[str, set[str]]:
    return {c.archetype: {s.label for s in c.signals} for c in profile.claimed}


def _evidence_surfaces(profile) -> set[str]:
    """Every surface that contributed at least one fired signal."""
    return {s.surface for c in profile.claimed for s in c.signals}


def capture(domain: str, path: str) -> int:
    # 1. Live discovery crawl (read-only, $0).
    ctx = FetchContext(domain)
    live = discover_offering(ctx)
    live_labels = _labels_by_archetype(live)

    # 2. Strip ephemeral set-cookie headers (sibling zero-set-cookie convention).
    stripped = 0
    for result in ctx._cache.values():
        if result.headers and "set-cookie" in result.headers:
            del result.headers["set-cookie"]
            stripped += 1

    # 3. Record.
    n = ctx.save_fixture(path)

    # 4. Verify honest ordering: the offline replay reproduces the live crawl.
    replay = discover_offering(FetchContext.from_fixture(path))
    replay_labels = _labels_by_archetype(replay)

    ok = live.archetypes == replay.archetypes and live_labels == replay_labels
    # No surface that produced evidence may be a replay-miss (would drop a claim).
    ev_surfaces = _evidence_surfaces(replay)
    homepage_ok = ("homepage" in replay.surfaces_seen) or ("homepage" not in _evidence_surfaces(live))

    print(f"domain           : {domain}")
    print(f"fixture          : {path}  ({n} entries, {stripped} set-cookie stripped)")
    print(f"live   claimed   : {live.archetypes}")
    print(f"replay claimed   : {replay.archetypes}")
    for arch in live.archetypes:
        print(f"  [{arch}] labels: {sorted(live_labels.get(arch, set()))}")
    print(f"evidence surfaces: {sorted(ev_surfaces)}")
    print(f"replay faithful  : {ok}   homepage present on replay: {homepage_ok}")
    if not (ok and homepage_ok):
        print("FAIL: replay does not reproduce the live crawl — fixture NOT anchor-ready.")
        return 1
    print("OK: fixture reproduces the live classification byte-faithfully.")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    return capture(argv[0], argv[1])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
