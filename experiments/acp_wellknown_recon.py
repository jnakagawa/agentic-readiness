#!/usr/bin/env python3
"""[LOCAL] $0 recon: is a LIVE ACP (Agentic Commerce Protocol) surface pinnable?

The shipped scorer probes only ``_COMMERCE_WELL_KNOWN = ("/.well-known/ucp",
"/.well-known/agentic-commerce")`` and validates a hit against
``_ACP_PAYLOAD_KEYS`` (checkout-session-shaped) or ``_UCP_MANIFEST_KEYS``.
Ecosystem sources place the real ACP discovery manifest at the DIFFERENT path
``/.well-known/acp/manifest.json`` — which the scorer does NOT probe. This
recon asks, at $0 with the scorer's own fetch + validator (byte-faithful):

  * Does ANY real merchant/platform serve a valid ACP payload at the scorer's
    path ``/.well-known/agentic-commerce``? (→ scorer already detects it.)
  * Does ANY serve one at the ecosystem path ``/.well-known/acp/manifest.json``?
    (→ re-pathing the scorer's well-known list is the peer-gated unlock, IF
    >=2 live surfaces validate — inv #3.)
  * For comparison, does it serve ``/.well-known/ucp`` instead? (the rail we
    already pin.)

Read-only GETs only. No payment, no POST, no --behavioral, no zero CLI. inv #1
by construction.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from asrs.fetch import FetchContext  # noqa: E402
from asrs.probes.protocols import (  # noqa: E402
    _ACP_PAYLOAD_KEYS,
    _UCP_MANIFEST_KEYS,
    _parse_commerce_manifest,
)

# Scorer's two commerce well-known paths + the ecosystem-documented ACP path
# the scorer does NOT probe.
SCORER_ACP_PATH = "/.well-known/agentic-commerce"
ECOSYSTEM_ACP_PATH = "/.well-known/acp/manifest.json"
UCP_PATH = "/.well-known/ucp"
PATHS = (SCORER_ACP_PATH, ECOSYSTEM_ACP_PATH, UCP_PATH)

# Real domains across the ACP/agentic-commerce ecosystem: co-authors + infra,
# announced ACP merchants, big retail long-shots, and known UCP merchants as a
# comparison control (they should answer /.well-known/ucp, not ACP).
CANDIDATES = [
    # ACP co-authors / spec / infra
    ("stripe.com", "acp-coauthor"),
    ("openai.com", "acp-coauthor"),
    ("chatgpt.com", "acp-surface"),
    ("agenticcommerce.dev", "acp-spec-home"),
    # ACP-announced / Instant-Checkout merchants
    ("etsy.com", "acp-announced-merchant"),
    ("instacart.com", "acp-announced-merchant"),
    # Big retail long-shots
    ("walmart.com", "retail-longshot"),
    ("target.com", "retail-longshot"),
    ("bestbuy.com", "retail-longshot"),
    ("wayfair.com", "retail-longshot"),
    # Shopify ecosystem
    ("shop.app", "shopify-platform"),
    ("shopify.com", "shopify-platform"),
    # Agent-commerce infra
    ("crossmint.com", "agent-commerce-infra"),
    ("skyfire.xyz", "agent-commerce-infra"),
    # Known UCP merchants (comparison control — expect UCP, not ACP)
    ("gymshark.com", "ucp-merchant-control"),
    ("hardgraft.com", "ucp-merchant-control"),
    ("checkout.coffeecircle.com", "ucp-merchant-control"),
    ("allbirds.com", "ucp-merchant-control"),
    ("skims.com", "ucp-merchant-control"),
    ("glossier.com", "ucp-merchant-control"),
    # --- Cadence broadening (Local cycle 20260809T02xxxxZ): FRESH candidates so
    # each re-run genuinely hunts for a NEW live ACP surface instead of repeating
    # the same 20-domain null. A per-domain exception is caught, so a
    # non-resolving domain records an error and never kills the sweep. ---
    # Big-retail ACP long-shots (would announce an Instant-Checkout surface).
    ("nike.com", "retail-longshot"),
    ("sephora.com", "retail-longshot"),
    ("lululemon.com", "retail-longshot"),
    ("chewy.com", "retail-longshot"),
    # Named in agentic-commerce / ChatGPT-commerce announcements — ACP long-shots.
    ("doordash.com", "agentic-announced-longshot"),
    ("expedia.com", "agentic-announced-longshot"),
    # Fresh Shopify/UCP merchant scouts (hunt a new UCP (legibility×trust) point
    # AND catch any merchant that flips to ACP).
    ("spanx.com", "ucp-merchant-scout"),
    ("kith.com", "ucp-merchant-scout"),
    ("brooklinen.com", "ucp-merchant-scout"),
    ("ruggable.com", "ucp-merchant-scout"),
    # x402 infra long-shots — do they ALSO publish a commerce well-known manifest?
    ("coinbase.com", "x402-infra-longshot"),
    ("x402.org", "x402-infra-longshot"),
    # --- Cadence broadening (Local cycle 20260811T144xxxZ): a FRESH cohort sourced
    # from CURRENT (2026) live agentic-commerce announcements, so this re-run hunts
    # NEW surfaces instead of repeating the 32-domain null. Two named-live cohorts:
    # Google's UCP checkout pilot retailers (live on Search/Gemini) and fresh ACP /
    # Adyen-Agentic announced merchants. AP2 (the 3rd stack rail) deliberately NOT
    # probed: it defines NO merchant-side well-known discovery path (payment-auth
    # only) — probing a non-existent path would be 404 noise, not signal. ---
    # Google UCP checkout pilot retailers (named live on Search + the Gemini app).
    ("petco.com", "ucp-google-pilot"),
    ("elfcosmetics.com", "ucp-google-pilot"),
    ("samsonite.com", "ucp-google-pilot"),
    ("lowes.com", "ucp-google-pilot"),
    ("michaels.com", "ucp-google-pilot"),
    ("poshmark.com", "ucp-google-pilot"),
    ("reebok.com", "ucp-google-pilot"),
    # Fresh ACP-announced merchants (Instant-Checkout / ChatGPT-commerce cohort).
    ("vuoriclothing.com", "acp-announced-merchant"),
    ("fanatics.com", "acp-announced-merchant"),
    ("quince.com", "acp-announced-merchant"),
    # Adyen Agentic launch partners — do they self-publish a commerce well-known?
    ("sezane.com", "adyen-agentic-partner"),
    ("scheels.com", "adyen-agentic-partner"),
]


def _probe_domain(domain: str) -> dict:
    ctx = FetchContext(domain, timeout=8.0)
    out: dict = {}
    for path in PATHS:
        res = ctx.get(path, ua="browser")
        entry: dict = {"status": res.status, "error": res.error}
        text = (res.text or "").strip()
        # Raw top-level JSON keys (what is ACTUALLY served), independent of
        # whether they match the scorer's key sets.
        top_keys: list[str] | None = None
        if res.ok and res.status == 200 and text:
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    top_keys = sorted(str(k) for k in data)[:20]
            except (ValueError, TypeError):
                top_keys = None
        entry["json_top_keys"] = top_keys
        # Byte-faithful scorer validation.
        manifest = _parse_commerce_manifest(res)
        entry["scorer_manifest"] = manifest  # {protocol, fields, ...} or None
        out[path] = entry
    return out


def main() -> int:
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results: dict = {}
    for domain, tag in CANDIDATES:
        try:
            probed = _probe_domain(domain)
        except Exception as exc:  # never let one domain kill the sweep
            probed = {"_exception": repr(exc)}
        results[domain] = {"tag": tag, "paths": probed}
        # progress line
        acp_scorer = probed.get(SCORER_ACP_PATH, {}).get("scorer_manifest")
        acp_eco = probed.get(ECOSYSTEM_ACP_PATH, {})
        acp_eco_keys = acp_eco.get("json_top_keys")
        ucp = probed.get(UCP_PATH, {}).get("scorer_manifest")
        print(
            f"{domain:32s} {tag:24s} "
            f"scorerACP={_fmt(acp_scorer)}  "
            f"ecoACP200keys={'yes' if acp_eco_keys else '-'}  "
            f"UCP={_fmt(ucp)}"
        )

    # Aggregate the finding.
    acp_scorer_hits = [
        d for d, r in results.items()
        if (r["paths"].get(SCORER_ACP_PATH, {}) or {}).get("scorer_manifest", {})
        and r["paths"][SCORER_ACP_PATH]["scorer_manifest"].get("protocol") == "acp"
    ]
    acp_eco_valid = [
        d for d, r in results.items()
        if _eco_is_valid_acp(r["paths"].get(ECOSYSTEM_ACP_PATH, {}))
    ]
    ucp_hits = [
        d for d, r in results.items()
        if (r["paths"].get(UCP_PATH, {}) or {}).get("scorer_manifest", {})
        and r["paths"][UCP_PATH]["scorer_manifest"].get("protocol") == "ucp"
    ]

    summary = {
        "ts": ts,
        "kind": "acp-wellknown-recon",
        "spend": "$0 (read-only GETs; no payment/POST/behavioral/zero-CLI)",
        "scorer_acp_path": SCORER_ACP_PATH,
        "ecosystem_acp_path": ECOSYSTEM_ACP_PATH,
        "acp_payload_keys": sorted(_ACP_PAYLOAD_KEYS),
        "ucp_manifest_keys": sorted(_UCP_MANIFEST_KEYS),
        "n_candidates": len(CANDIDATES),
        "acp_at_scorer_path": acp_scorer_hits,
        "acp_at_ecosystem_path_valid": acp_eco_valid,
        "ucp_at_scorer_path": ucp_hits,
        "results": results,
    }
    outdir = Path(__file__).resolve().parent.parent / "runs" / "local"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"acp_wellknown_recon_{ts}.json"
    outpath.write_text(json.dumps(summary, indent=1), encoding="utf-8")

    print("\n=== FINDING ===")
    print(f"ACP valid at scorer path {SCORER_ACP_PATH}: {acp_scorer_hits or 'NONE'}")
    print(f"ACP valid at ecosystem path {ECOSYSTEM_ACP_PATH}: {acp_eco_valid or 'NONE'}")
    print(f"UCP valid at {UCP_PATH}: {ucp_hits or 'NONE'}")
    n_acp = len(set(acp_scorer_hits) | set(acp_eco_valid))
    print(
        f"\nLive ACP surfaces found: {n_acp} "
        f"({'>=2 -> re-pathing peer-gated unit is validatable (inv #3)' if n_acp >= 2 else '<2 -> ACP remains un-pinnable $0; scorer unchanged'})"
    )
    print(f"\nEvidence: {outpath}")
    return 0


def _eco_is_valid_acp(entry: dict) -> bool:
    m = (entry or {}).get("scorer_manifest")
    return bool(m and m.get("protocol") == "acp")


def _fmt(manifest: dict | None) -> str:
    if not manifest:
        return "-"
    return f"{manifest.get('protocol')}:{','.join(manifest.get('fields', []))[:24]}"


if __name__ == "__main__":
    raise SystemExit(main())
