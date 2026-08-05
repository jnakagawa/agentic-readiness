"""$0 static screen for a real storefront that CLAIMS data_retrieval.

The data_retrieval archetype has ZERO committed fixture evidence (NA on all six
prior canonical fixtures), so it cannot be strengthened in-cloud — the exact
gap the service_booking capture (Cycle 240, acuityscheduling.com) closed for its
sibling thin archetype. This probe runs the REAL discovery path
(`asrs.offering.discover_offering`) over candidate records-lookup / data-
enrichment / dataset-API storefronts and reports, for each: reachability, the
claimed archetype SET, the surfaces seen, and — for data_retrieval — exactly
which signals fired with their quoted machine evidence. Read-only, $0 (no
scoring, no behavioral run, no POST). The winner (reachable + genuine,
precision-clean data_retrieval claim with >=2 distinct signals, no false
sibling-archetype claim) becomes the first committed data_retrieval anchor.

Usage: python -m experiments.probe_data_retrieval_candidates [domain ...]
"""
from __future__ import annotations

import json
import os
import sys

from asrs.fetch import FetchContext
from asrs.offering import discover_offering

_TIMEOUT = float(os.environ.get("PROBE_TIMEOUT", "6.0"))

_DEFAULT_CANDIDATES = [
    "ipinfo.io",
    "hunter.io",
    "peopledatalabs.com",
    "opencorporates.com",
    "www.whoisxmlapi.com",
    "www.abstractapi.com",
    "opencagedata.com",
    "numverify.com",
    "data.world",
    "apilayer.com",
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
    dr = claimed.get("data_retrieval")
    if dr is not None:
        rec["data_retrieval"] = {
            "labels": sorted({s.label for s in dr.signals}),
            "evidence": [
                {"label": s.label, "surface": s.surface, "quote": s.quote[:160]}
                for s in dr.signals[:8]
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
        dr = "DR!" if r.get("data_retrieval") else ""
        print(
            f"{d:32s} {dr:4s} claimed={claimed} "
            f"surfaces={r.get('surfaces_seen')} {r.get('error', '')}",
            file=sys.stderr,
            flush=True,
        )
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
