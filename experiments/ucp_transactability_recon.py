"""[LOCAL] experiment — the UCP transactability-rung recon.

Answers the P2 UCP-depth forward frontier (BACKLOG): the UCP commerce-protocol
rail now has FOUR pinned frozen-replay baselines (checkout.coffeecircle.com 57.4,
gymshark.com 62.4, hardgraft.com 66.9, kith.com 70.3) and they ALL sit at exactly
`transactability = 50.0`. That is not a coincidence — it is the shape of the tx
pillar for a retail UCP merchant:

    transactability = x402_probe (max 8.0) + mcp_surface (max 2.0) + self_serve_payg (max 6.0)

A validated `/.well-known/ucp` manifest earns `x402_probe` the PARTIAL
`commerce-protocol-live` rung (4.0/8.0), and a retail merchant's cart/"add to
cart"/"sign up" CTAs earn `self_serve_payg` a partial — 4.0 + 4.0 + 0 = 8.0/16.0
= tx 50.0. So the UCP plane is currently pinned at the tx-50.0 rung, spanning
only legibility (50.0 -> 86.36) and trust (33.33 -> 90.0).

The explicit forward-frontier question this recon answers:

    Does ANY live UCP merchant clear tx > 50.0 — a DISTINCT tx rung on the UCP
    rail — and if so, by WHICH capability (a fuller self_serve_payg toward 6.0,
    or an mcp_surface 2.0)? Or is the UCP tx axis structurally bounded at 50.0
    for retail merchants (a real scarcity truth about the rail)?

Method: for each candidate, a $0 GET of `/.well-known/ucp`, validated byte-
faithfully via the scorer's OWN `_parse_commerce_manifest` (so "serves UCP" means
exactly what the scorer means). Every UCP-serving domain is then STATIC-scored
through the SHIPPED path (`asrs.cli._run_probes` -> `asrs.scoring.score`, the exact
pipeline `asrs score <domain>` uses, no `--behavioral`), and the transactability
CHECK breakdown (x402_probe / mcp_surface / self_serve_payg — status, points,
finding) is extracted. That breakdown is not visible in any committed artifact
today; this recon surfaces it for the whole live UCP population at once.

Why [LOCAL]: the cloud env cannot reach these domains (STATE.md network policy).

$0 (invariant #1) BY CONSTRUCTION: static recon only — no `--behavioral`, so NO
free-tier probe fires, no zero CLI, no signing path, never a nonzero `--max-pay`.
The x402 probe's empty-POST handshake fires only on an agent surface that itself
documents x402 (retail UCP merchants do not), and an empty POST is a $0 handshake,
never a payment.

Score-neutral: reads ONLY the shipped scoring path; changes no scoring semantics,
adds no probe, bumps no rubric version. The committed dataset is evidence,
force-added under runs/local/ (runs/ is gitignored).

Vendor-neutral: every candidate is probed + scored through the SAME path with NO
special-casing; the `tag` label is context for reading the result, never a scorer
input. The known controls double as a live-manifest DRIFT tripwire (a pinned UCP
rail whose manifest went down this run would surface as ucp_served=False).

Run:  .venv/bin/python experiments/ucp_transactability_recon.py
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from asrs import scoring  # noqa: E402
from asrs.cli import _normalize_domain, _run_probes  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402
from asrs.probes.protocols import _parse_commerce_manifest  # noqa: E402

UCP_PATH = "/.well-known/ucp"
FETCH_TIMEOUT_S = 12.0
_TX = "transactability"
_TX_CHECKS = ("x402_probe", "mcp_surface", "self_serve_payg")

# (domain, tag). `tag` positions the candidate for READING the result; it is
# never read by the scorer. Two groups:
#   * KNOWN UCP merchants — the reference tx-50.0 distribution + a live-manifest
#     drift tripwire (the 4 pinned baselines + the 5 surveyed-but-unpinned finds).
#   * FRESH DTC/merchant scouts — genuinely NEW candidates so this run HUNTS a
#     tx > 50.0 UCP merchant, not a rote re-score of the known set. ruggable.com
#     is a known NON-UCP control (404 last recon) proving the UCP probe
#     discriminates (a null there is a real negative, not a broken probe).
CANDIDATES = [
    # --- known live UCP merchants (reference distribution + drift tripwire) ---
    ("kith.com", "ucp-known:pinned-baseline"),           # 70.3, tx 50.0 ref
    ("hardgraft.com", "ucp-known:pinned-baseline"),      # 66.9, tx 50.0 ref
    ("spanx.com", "ucp-known:sub-rung"),                 # 60.0, tx 43.75 (the only sub-50)
    ("skims.com", "ucp-known:surveyed"),                 # 60.4
    ("glossier.com", "ucp-known:surveyed"),              # 64.9
    ("brooklinen.com", "ucp-known:surveyed"),            # 59.9
    ("allbirds.com", "ucp-known:surveyed"),              # offering-drift, pin-avoided
    # --- fresh DTC/merchant scouts (hunt a NEW UCP tx > 50.0 point) ---
    ("rothys.com", "ucp-scout:apparel-footwear"),
    ("mejuri.com", "ucp-scout:jewelry"),
    ("everlane.com", "ucp-scout:apparel"),
    ("bombas.com", "ucp-scout:apparel"),
    ("vuori.com", "ucp-scout:activewear"),
    ("aloyoga.com", "ucp-scout:activewear"),
    ("outdoorvoices.com", "ucp-scout:activewear"),
    ("tecovas.com", "ucp-scout:footwear"),
    ("mizzenandmain.com", "ucp-scout:apparel"),
    ("chubbiesshorts.com", "ucp-scout:apparel"),
    ("ruggable.com", "ucp-scout:home-NEGATIVE-control"),  # known NO-UCP
]


def _ucp_probe(ctx: FetchContext) -> dict:
    """$0 GET /.well-known/ucp; byte-faithful scorer validation."""
    res = ctx.get(UCP_PATH, ua="browser")
    manifest = _parse_commerce_manifest(res)  # {protocol, fields, ...} or None
    return {
        "status": res.status,
        "error": res.error,
        "served": manifest is not None,
        "manifest": manifest,
    }


def _tx_breakdown(checks) -> dict:
    """Extract the transactability CHECK breakdown from a scored run."""
    out: dict = {}
    for c in checks:
        if getattr(c, "pillar", None) != _TX:
            continue
        cid = c.check_id
        out[cid] = {
            "status": c.status.value if hasattr(c.status, "value") else str(c.status),
            "points": c.points,
            "max_points": c.max_points,
            "finding": c.finding,
        }
    return out


def _score_ucp_merchant(raw: str, rubric) -> dict:
    """Full static score + tx breakdown for a UCP-serving domain ($0)."""
    checks = _run_probes(FetchContext(raw, timeout=FETCH_TIMEOUT_S))
    report = scoring.score(checks, rubric, raw)
    tx = _tx_breakdown(checks)
    try:
        from asrs.offering import discover_offering

        claimed = discover_offering(FetchContext(raw, timeout=FETCH_TIMEOUT_S)).archetypes
    except Exception:  # noqa: BLE001 — diagnostic annotation only
        claimed = None
    return {
        "scored": report.scored,
        "overall": report.overall_score,
        "grade": report.grade,
        "rubric_version": report.rubric_version,
        "pillars": report.pillar_scores,
        "transactability": report.pillar_scores.get(_TX),
        "tx_checks": tx,
        "caps_applied": report.caps_applied,
        "claimed_archetypes": claimed,
    }


def main() -> None:
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rubric = scoring.load_rubric(None)
    rows: list[dict] = []
    for domain, tag in CANDIDATES:
        raw = _normalize_domain(domain)
        row: dict = {"domain": raw, "tag": tag}
        t0 = time.time()
        try:
            ucp = _ucp_probe(FetchContext(raw, timeout=FETCH_TIMEOUT_S))
            row["ucp"] = ucp
            if ucp["served"]:
                row["score"] = _score_ucp_merchant(raw, rubric)
            else:
                row["score"] = None
            row["error"] = None
        except Exception as exc:  # noqa: BLE001 — reachability failure, not a site FAIL
            row["ucp"] = None
            row["score"] = None
            row["error"] = f"{type(exc).__name__}: {exc}"
        row["elapsed_s"] = round(time.time() - t0, 2)
        rows.append(row)
        served = row.get("ucp") and row["ucp"].get("served")
        tx = row["score"]["transactability"] if row.get("score") else None
        print(
            f"  {raw:28s} {tag:32s} ucp={'Y' if served else '-'} "
            f"tx={tx if tx is not None else '--':>6} "
            f"overall={row['score']['overall'] if row.get('score') else '--'}"
        )

    # Analysis: the tx-rung distribution over the live UCP population.
    ucp_served = [r for r in rows if r.get("ucp") and r["ucp"]["served"]]
    scored = [r for r in ucp_served if r.get("score")]
    above_50 = [r for r in scored if (r["score"]["transactability"] or 0) > 50.0]
    at_50 = [r for r in scored if (r["score"]["transactability"] or 0) == 50.0]
    below_50 = [r for r in scored if (r["score"]["transactability"] or 0) < 50.0]
    fresh_ucp = [r for r in ucp_served if r["tag"].startswith("ucp-scout")]

    summary = {
        "n_candidates": len(CANDIDATES),
        "n_ucp_served": len(ucp_served),
        "n_scored": len(scored),
        "ucp_served_domains": [r["domain"] for r in ucp_served],
        "fresh_ucp_domains": [r["domain"] for r in fresh_ucp],
        "tx_above_50": [
            {"domain": r["domain"], "tx": r["score"]["transactability"], "tx_checks": r["score"]["tx_checks"]}
            for r in above_50
        ],
        "tx_at_50": [r["domain"] for r in at_50],
        "tx_below_50": [
            {"domain": r["domain"], "tx": r["score"]["transactability"]} for r in below_50
        ],
    }

    artifact = {
        "ts": ts,
        "kind": "ucp-transactability-recon",
        "spend": "$0 (read-only GETs + static score; no --behavioral/--max-pay/payment/zero-CLI)",
        "ucp_path": UCP_PATH,
        "tx_pillar_checks": {"x402_probe": 8.0, "mcp_surface": 2.0, "self_serve_payg": 6.0},
        "question": "Does any live UCP merchant clear transactability > 50.0 (a DISTINCT tx rung), and by which capability?",
        "summary": summary,
        "rows": rows,
    }
    out_dir = Path("runs") / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ucp_transactability_recon_{ts}.json"
    with open(out_path, "w") as fh:
        json.dump(artifact, fh, indent=1, sort_keys=False)

    print()
    print(f"UCP served: {len(ucp_served)}/{len(CANDIDATES)}  scored: {len(scored)}")
    print(f"  tx > 50.0 : {[r['domain'] for r in above_50]}")
    print(f"  tx = 50.0 : {[r['domain'] for r in at_50]}")
    print(f"  tx < 50.0 : {[(r['domain'], r['score']['transactability']) for r in below_50]}")
    print(f"  fresh UCP found: {[r['domain'] for r in fresh_ucp]}")
    print(f"artifact: {out_path}")


if __name__ == "__main__":
    main()
