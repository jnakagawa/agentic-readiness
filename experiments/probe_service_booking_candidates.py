"""$0 static screen for a real storefront that CLAIMS service_booking.

The service_booking archetype has ZERO committed fixture evidence (NA on all
five canonical fixtures), so it cannot be strengthened in-cloud. This probe runs
the REAL discovery path (`asrs.offering.discover_offering`) over candidate
booking/reservation storefronts and reports, for each: reachability, the claimed
archetype SET, the surfaces seen, and — for service_booking — exactly which
signals fired with their quoted machine evidence. Read-only, $0 (no scoring, no
behavioral run, no POST). The winner (reachable + genuine, precision-clean
service_booking claim) becomes the first committed service_booking anchor.

Usage: python -m experiments.probe_service_booking_candidates [domain ...]
"""
from __future__ import annotations

import json
import os
import sys

from asrs.fetch import FetchContext
from asrs.offering import discover_offering

_TIMEOUT = float(os.environ.get("PROBE_TIMEOUT", "6.0"))

_DEFAULT_CANDIDATES = [
    "cal.com",
    "www.simplybook.me",
    "acuityscheduling.com",
    "cronofy.com",
    "savvycal.com",
    "www.opentable.com",
    "www.resy.com",
    "developer.squareup.com",
]


def probe(domain: str) -> dict:
    rec: dict = {"domain": domain}
    try:
        ctx = FetchContext(domain, timeout=_TIMEOUT)
        profile = discover_offering(ctx)
    except Exception as exc:  # noqa: BLE001 - screening tool, report not raise
        rec["error"] = f"{type(exc).__name__}: {exc}"
        return rec
    claimed = {c.archetype: c for c in profile.claimed}
    rec["claimed"] = [c.archetype for c in profile.claimed]  # strongest first
    rec["surfaces_seen"] = sorted(getattr(profile, "surfaces_seen", []) or [])
    sb = claimed.get("service_booking")
    if sb is not None:
        rec["service_booking"] = {
            "labels": sorted({s.label for s in sb.signals}),
            "evidence": [
                {"label": s.label, "surface": s.surface, "quote": s.quote[:160]}
                for s in sb.signals[:8]
            ],
        }
    return rec


def main(argv: list[str]) -> int:
    domains = argv or _DEFAULT_CANDIDATES
    out = []
    for d in domains:
        r = probe(d)
        out.append(r)
        claimed = r.get("claimed")
        sb = "SB!" if r.get("service_booking") else ""
        print(
            f"{d:32s} {sb:4s} claimed={claimed} "
            f"surfaces={r.get('surfaces_seen')} {r.get('error', '')}",
            file=sys.stderr,
            flush=True,
        )
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
