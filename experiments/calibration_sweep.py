"""[LOCAL] experiment — the calibration POPULATION static sweep.

Answers the standing TRUTH/north-star gap (BACKLOG P1 "Calibration population"):
the benchmark's credibility rests on more than the canonical pair. This runs the
SHIPPED static scoring path (`asrs.cli._run_probes` -> `asrs.scoring.score`, the
exact pipeline `asrs score <domain>` uses, no `--behavioral`) across a curated
population of real domains spanning the agentic-commerce spectrum — agent-native
API storefronts, retail with emerging rails, retail without rails, and
non-storefront controls — and commits a dated dataset. It is the first
population artifact: "a benchmark needs a population, not one pair."

Why [LOCAL]: the cloud env cannot reach these domains (the canonical pair and
most real hosts return NOT SCORABLE in-cloud per the network policy in STATE.md),
so a live multi-domain sweep is the networked half of the loop. $0: static
recon only — no `--behavioral`, so NO free-tier probe fires, no zero CLI, no
signing path (invariant #1 holds by construction; the free-tier transaction
only runs in behavioral mode).

Vendor-neutral by construction: every domain is scored through the SAME probes
with NO special-casing. The `segment` label is context for reading the spread
(where a domain sits on the spectrum), NOT an input to scoring — the number
comes only from the evidence the probes find.

Attribution honesty (invariant #4): a domain that is unreachable / env-blocked
records `scored=False` (NOT SCORABLE) and is kept OUT of the leaderboard — a
site is never punished for what could not be observed. Reachability is reported
as its own count, distinct from a real low score.

Score-neutral: this only READS the shipped scoring path; it changes no scoring
semantics, adds no probe, and bumps no rubric version. The committed dataset is
evidence, force-added under runs/local/ (runs/ is gitignored).
"""

from __future__ import annotations

import glob
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

from asrs import scoring
from asrs.cli import _normalize_domain, _run_probes
from asrs.fetch import FetchContext

# (domain, segment). `segment` positions the domain on the agentic-commerce
# spectrum for READING the population — it is never read by the scorer. The
# canonical pair are included as anchors that tie the sweep to the pinned
# 46.1 / 85.5 baseline the in-cloud replay guard defends.
POPULATION: list[tuple[str, str]] = [
    # agent-native API storefronts / AI services
    ("driftflight.com", "api-storefront:rails-anchor"),
    ("drift-flight.org", "api-storefront:no-rails-anchor"),
    ("exa.ai", "api-service"),
    ("deepai.org", "api-service"),
    ("perplexity.ai", "api-service"),
    ("openai.com", "api-service"),
    ("anthropic.com", "api-service"),
    # data-retrieval / records-enrichment API storefront (the data_retrieval
    # offering anchor captured LOCAL Cycle 242, fixtures/canonical/ipinfo.io.json)
    ("ipinfo.io", "data-retrieval:api"),
    # appointment / service-booking SaaS storefront (the service_booking offering
    # anchor captured LOCAL Cycle 240, fixtures/canonical/acuityscheduling.com.json)
    ("acuityscheduling.com", "service-booking:saas"),
    # the two newest agent-native offering anchors, captured LOCAL Cycles 273/275
    # (increment (a): broaden toward the 15-20 target with genuinely new storefront
    # TYPES). A multi-archetype agent-native booking platform, agent surfaces under
    # agents.simplybook.me/* (fixtures/canonical/simplybook.me.json), and a
    # Merchant-of-Record subscription commerce platform publishing llms.txt + an
    # OpenAPI + an A2A agent-card (fixtures/canonical/polar.sh.json).
    ("simplybook.me", "service-booking:platform"),
    ("polar.sh", "subscription:mor-platform"),
    # retail with emerging agentic rails (llms.txt / agent manifests / agent checkout)
    ("deathwishcoffee.com", "retail:emerging-rails"),
    ("warbyparker.com", "retail:emerging-rails"),
    ("allbirds.com", "retail:emerging-rails"),
    # retail without agentic rails (browser-only checkout)
    ("moleskine.com", "retail:no-rails"),
    ("rei.com", "retail:no-rails"),
    # a stable static retail catalog (scraping sandbox) — carries a committed
    # replay baseline (tests/test_canonical_replay.EXPECTED, overall 29.5, the
    # transactability floor) but was ABSENT from every prior sweep. Adding it here
    # (LOCAL cadence, increment (a)) gives the 2nd non-anchor cross-path weld
    # candidate its first live-sweep presence, so a future TRUTH cycle can weld it
    # replay-baseline vs sweep off the two famous anchors (see
    # tests/test_calibration_anchor_agreement._NON_ANCHOR_WELDED).
    ("books.toscrape.com", "retail:no-rails"),
    # a PURE single-archetype metered_api compute / model-inference API storefront
    # (a 5th structurally-distinct storefront TYPE) — carries a committed replay
    # baseline (tests/test_canonical_replay.EXPECTED, overall 29.5, the low-legibility
    # inference-API shape) pinned LOCAL cycle 20260807T114104Z, but was ABSENT from
    # every prior sweep. Adding it here (LOCAL cadence, increment (a)) gives the 5th
    # non-anchor cross-path weld candidate its first live-sweep presence, so a future
    # TRUTH cycle can weld it replay-baseline vs sweep off the two famous anchors (the
    # books.toscrape.com pattern; see tests/test_calibration_anchor_agreement.
    # _NON_ANCHOR_WELDED).
    ("api.replicate.com", "metered-api:inference-platform"),
    # the three non-anchor storefronts with a GENUINE LIVE x402 handshake, pinned as
    # frozen-replay baselines LOCAL cycles 20260808T054613Z / 065659Z / 074103Z
    # (thebotwire.com 86.0, api.x402oracle.com 64.4, x402deploy.vercel.app 73.9 — the
    # first non-anchor points on the live/upper scale, spanning two transactability
    # shapes: tx 100.0 on thebotwire/x402deploy, tx 87.5 on the oracle). They carry a
    # committed replay baseline but were ABSENT from every prior sweep. Adding them
    # here (LOCAL cadence, the books.toscrape.com / api.replicate.com prerequisite
    # pattern) gives each its first live-sweep presence, so a future TRUTH cycle can
    # weld them into tests/test_calibration_anchor_agreement._NON_ANCHOR_WELDED
    # non-vacuously — extending the cross-path weld to LIVE-rail storefront TYPES
    # (the seven current welded witnesses all carry NO live rail). Because the rails
    # are LIVE (volatile), a member whose live score DIVERGES from its frozen floor
    # this run is an honest live-rail-drift signal, not silently averaged in.
    ("thebotwire.com", "x402-live:news-data-wire"),
    ("api.x402oracle.com", "x402-live:trust-oracle"),
    ("x402deploy.vercel.app", "x402-live:web-data-tools"),
    # a REAL coffee merchant's UCP (Universal Commerce Protocol) checkout surface,
    # pinned as the THIRTEENTH frozen-replay baseline LOCAL cycle 20260808T104105Z
    # (checkout.coffeecircle.com 57.4 F). It is the FIRST non-anchor point on a
    # structurally NEW agent-native rail TYPE: GET /.well-known/ucp answers a $0
    # read with a valid dev.ucp.* capability manifest, so the scorer's x402_probe
    # reads commerce-protocol-live PARTIAL 4.0/8.0 — the MIDDLE rung of the
    # commerce-protocol ladder, distinct from every x402/no-rail witness above
    # (honest {metered_api, physical_good}, no over-claim). It carries a committed
    # replay baseline but was ABSENT from every prior sweep. Adding it here (LOCAL
    # cadence, the api.replicate.com / three-x402-witnesses prerequisite pattern)
    # gives it its first live-sweep presence, so a future TRUTH cycle can weld it
    # into tests/test_calibration_anchor_agreement._NON_ANCHOR_WELDED
    # non-vacuously — the FIRST welded member on the UCP commerce-protocol rail.
    # Because the UCP manifest is LIVE (a served well-known JSON, volatile), a
    # member whose live score DIVERGES from its frozen floor this run is an honest
    # manifest-drift signal, not silently averaged in.
    ("checkout.coffeecircle.com", "ucp-live:coffee-merchant"),
    # a mainstream consumer apparel brand (Shopify storefront) on the SAME live UCP
    # rail, pinned as the FOURTEENTH frozen-replay baseline LOCAL cycle
    # 20260808T140228Z (gymshark.com 62.4 D). It is the SECOND non-anchor point on
    # the UCP rail and adds retail DEPTH (a distinct storefront TYPE from the
    # coffee-merchant checkout.coffeecircle.com): GET /.well-known/ucp answers a $0
    # read with a valid dev.ucp.* service manifest, so the scorer's x402_probe reads
    # commerce-protocol-live PARTIAL 4.0/8.0 — the SAME UCP middle rung as
    # coffeecircle (honest {metered_api, physical_good}, no over-claim). Its
    # calibration value is a CONTROLLED single-pillar isolation: vs coffeecircle
    # (57.4) it holds access/legibility/transactability BYTE-IDENTICAL and moves
    # ONLY trust (33.33 -> 60.0), lifting overall 57.4 -> 62.4 — the "UCP rail
    # necessary but not SUFFICIENT" statement. It carries a committed replay
    # baseline but was ABSENT from every prior sweep. Adding it here (LOCAL cadence,
    # the checkout.coffeecircle.com prerequisite pattern) gives it its first
    # live-sweep presence, so a future TRUTH cycle can weld it into
    # tests/test_calibration_anchor_agreement._NON_ANCHOR_WELDED non-vacuously — the
    # SECOND welded member on the UCP commerce-protocol rail. Because the UCP
    # manifest is LIVE (a served well-known JSON, volatile), a member whose live
    # score DIVERGES from its frozen floor this run is an honest manifest-drift
    # signal, not silently averaged in.
    ("gymshark.com", "ucp-live:apparel-retail"),
    # a premium leather-goods merchant on the SAME live UCP rail, pinned as the
    # FIFTEENTH frozen-replay baseline LOCAL cycle 20260808T165732Z (hardgraft.com
    # 66.9 D). It is the THIRD non-anchor point on the UCP rail and adds further
    # retail DEPTH: GET /.well-known/ucp answers a $0 read with a valid dev.ucp.*
    # service manifest, so the scorer's x402_probe reads commerce-protocol-live
    # PARTIAL 4.0/8.0 — the SAME UCP middle rung as checkout.coffeecircle.com and
    # gymshark.com (honest {metered_api, physical_good}, no over-claim). Its
    # calibration value GENERALIZES the "UCP necessary but not SUFFICIENT" story
    # from a LINE to a PLANE: coffeecircle (57.4) and gymshark (62.4) share the
    # IDENTICAL legibility 54.55 and separate PURELY on trust; hardgraft holds the
    # SAME tx-50.0 rung but sits at a DISTINCT legibility (50.0) AND the HIGHEST
    # trust of the three (90.0), scoring 66.9 — so the three UCP points span a 2-D
    # (legibility x trust) region at the fixed tx rung. It carries a committed
    # replay baseline but was ABSENT from every prior sweep. Adding it here (LOCAL
    # cadence, the gymshark.com prerequisite pattern) gives it its first live-sweep
    # presence, so a future TRUTH cycle can weld it into
    # tests/test_calibration_anchor_agreement._NON_ANCHOR_WELDED non-vacuously — the
    # THIRD welded member on the UCP commerce-protocol rail. Because the UCP
    # manifest is LIVE (a served well-known JSON, volatile), a member whose live
    # score DIVERGES from its frozen floor this run is an honest manifest-drift
    # signal, not silently averaged in.
    ("hardgraft.com", "ucp-live:leather-goods"),
    # a curated apparel/lifestyle merchant on the SAME live UCP rail, pinned as the
    # SIXTEENTH frozen-replay baseline LOCAL cycle 20260809T040201Z (kith.com 70.3 C).
    # It is the FOURTH non-anchor point on the UCP rail and the HIGH-LEGIBILITY corner
    # of the UCP plane: GET /.well-known/ucp answers a $0 read with a valid dev.ucp.*
    # merchant manifest, so the scorer's x402_probe reads commerce-protocol-live
    # PARTIAL 4.0/8.0 — the SAME UCP middle rung as coffeecircle / gymshark / hardgraft
    # (transactability 50.0, honest {metered_api, physical_good}, no over-claim). Its
    # calibration value EXTENDS the UCP plane along the legibility axis: the first
    # three UCP points cluster at legibility 50.0 -> 54.55, but kith holds the SAME
    # tx-50.0 rung at a DISTINCT, far HIGHER legibility (86.36) with trust 60.0,
    # scoring 70.3 — the HIGHEST UCP overall of the four, showing a UCP merchant can
    # ALSO be highly legible (the rail fixes transactability while legibility ranges
    # 50.0 -> 86.36 at the fixed rung). It carries a committed replay baseline but was
    # ABSENT from every prior sweep. Adding it here (LOCAL cadence, the
    # gymshark.com / hardgraft.com prerequisite pattern) gives it its first live-sweep
    # presence, so a future TRUTH cycle can weld it into
    # tests/test_calibration_anchor_agreement._NON_ANCHOR_WELDED non-vacuously — the
    # FOURTH welded member on the UCP commerce-protocol rail. Because the UCP manifest
    # is LIVE (a served well-known JSON, volatile), a member whose live score DIVERGES
    # from its frozen floor this run is an honest manifest-drift signal, not silently
    # averaged in.
    ("kith.com", "ucp-live:apparel-lifestyle"),
    # non-storefront controls (zero-commerce baseline)
    ("example.com", "control:non-storefront"),
    ("wikipedia.org", "control:non-storefront"),
]

FETCH_TIMEOUT_S = 12.0


def _discover_claimed(ctx) -> list[str] | None:
    """Best-effort offering archetypes (which archetypes the site CLAIMS).

    Ties the population to the offering-relative work: for each member we record
    what it claims to sell. Best-effort — a discovery failure must not drop the
    row (the static score is the primary datum), so it returns None on error.
    """
    try:
        from asrs.offering import discover_offering

        return discover_offering(ctx).archetypes
    except Exception:  # noqa: BLE001 — diagnostic annotation only
        return None


def _score_one(domain: str, segment: str, rubric) -> dict:
    raw = _normalize_domain(domain)
    row: dict = {"domain": raw, "segment": segment}
    t0 = time.time()
    try:
        ctx = FetchContext(raw, timeout=FETCH_TIMEOUT_S)
        checks = _run_probes(ctx)
        report = scoring.score(checks, rubric, raw)
        quot = None
        try:
            from asrs.reliability import quotability

            quot = quotability(report).to_dict().get("verdict")
        except Exception:  # noqa: BLE001
            quot = None
        row.update(
            {
                "scored": report.scored,
                "overall": report.overall_score,
                "grade": report.grade,
                "rubric_version": report.rubric_version,
                "pillars": report.pillar_scores,
                "caps_applied": report.caps_applied,
                "quotability": quot,
                "claimed_archetypes": _discover_claimed(ctx),
                "error": None,
            }
        )
    except Exception as exc:  # noqa: BLE001 — reachability failure, not a site FAIL
        row.update(
            {
                "scored": False,
                "overall": None,
                "grade": "N/A",
                "rubric_version": str(rubric.get("version", "")),
                "pillars": {},
                "caps_applied": [],
                "quotability": None,
                "claimed_archetypes": None,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
    row["elapsed_s"] = round(time.time() - t0, 2)
    return row


def _load_baseline(current_ts: str) -> dict | None:
    """Newest prior calibration-sweep artifact, for the drift diff.

    Increment (b) of the calibration-population item: re-run on a cadence and
    diff against the prior dated dataset so population DRIFT (a domain adding or
    removing agentic rails moves its score) is VISIBLE, not buried. Best-effort —
    a missing / unreadable baseline just yields no drift block (the fresh sweep
    is the primary datum). Skips the artifact this run is about to write.
    """
    paths = sorted(glob.glob(os.path.join("runs", "local", "calibration_sweep_*.json")))
    for path in reversed(paths):
        if f"calibration_sweep_{current_ts}.json" in path:
            continue
        try:
            with open(path) as fh:
                base = json.load(fh)
            base["_path"] = os.path.basename(path)
            return base
        except Exception:  # noqa: BLE001 — diagnostic annotation only
            continue
    return None


def _compute_drift(rows: list[dict], baseline: dict | None) -> dict | None:
    """Per-domain overall-score movement vs the baseline sweep.

    Only domains present in BOTH datasets and scored in both contribute a delta;
    a scored<->not-scorable transition is reported separately (a reachability
    change, not a capability move — invariant #4). New / dropped members are
    listed so a broadened population is legible, not silently averaged in.
    """
    if not baseline:
        return None
    base_rows = {r["domain"]: r for r in baseline.get("rows", [])}
    now_domains = {r["domain"] for r in rows}
    moved: list[dict] = []
    status_changed: list[dict] = []
    for r in rows:
        b = base_rows.get(r["domain"])
        if b is None:
            continue  # a newly added member — reported under added_members
        now_scored = bool(r["scored"]) and r["overall"] is not None
        base_scored = bool(b.get("scored")) and b.get("overall") is not None
        if now_scored and base_scored:
            moved.append(
                {
                    "domain": r["domain"],
                    "segment": r["segment"],
                    "baseline": b["overall"],
                    "current": r["overall"],
                    "delta": round(r["overall"] - b["overall"], 1),
                }
            )
        elif now_scored != base_scored:
            status_changed.append(
                {
                    "domain": r["domain"],
                    "segment": r["segment"],
                    "baseline": b["overall"] if base_scored else "NOT SCORABLE",
                    "current": r["overall"] if now_scored else "NOT SCORABLE",
                }
            )
    moved.sort(key=lambda m: abs(m["delta"]), reverse=True)
    return {
        "baseline_ts": baseline.get("ts"),
        "baseline_path": baseline.get("_path"),
        "n_compared": len(moved),
        "n_moved": sum(1 for m in moved if m["delta"] != 0.0),
        "max_abs_delta": max((abs(m["delta"]) for m in moved), default=0.0),
        "moved": moved,
        "status_changed": status_changed,
        "added_members": sorted(now_domains - set(base_rows)),
        "removed_members": sorted(set(base_rows) - now_domains),
    }


def run() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rubric = scoring.load_rubric(None)
    rows: list[dict] = []
    for domain, segment in POPULATION:
        row = _score_one(domain, segment, rubric)
        rows.append(row)
        tag = (
            f"{row['overall']} {row['grade']}"
            if row["scored"]
            else ("NOT SCORABLE" if not row["error"] else f"ERR {row['error']}")
        )
        print(
            f"  {row['domain']:<24} {row['segment']:<28} {tag}",
            file=sys.stderr,
        )

    scored = [r for r in rows if r["scored"] and r["overall"] is not None]
    not_scorable = [r for r in rows if not r["scored"] and not r["error"]]
    errored = [r for r in rows if r["error"]]
    leaderboard = sorted(scored, key=lambda r: r["overall"], reverse=True)

    payload = {
        "ts": ts,
        "kind": "calibration-sweep",
        "rubric_version": str(rubric.get("version", "")),
        "n_total": len(rows),
        "n_scored": len(scored),
        "n_not_scorable": len(not_scorable),
        "n_error": len(errored),
        "leaderboard": [
            {"domain": r["domain"], "segment": r["segment"], "overall": r["overall"], "grade": r["grade"]}
            for r in leaderboard
        ],
        "drift": _compute_drift(rows, _load_baseline(ts)),
        "rows": rows,
    }
    return payload


def main() -> int:
    payload = run()
    out_dir = os.path.join("runs", "local")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"calibration_sweep_{payload['ts']}.json")
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=1)

    print(
        f"\ncalibration sweep v{payload['rubric_version']} — "
        f"{payload['n_scored']}/{payload['n_total']} scored, "
        f"{payload['n_not_scorable']} not-scorable, {payload['n_error']} error",
        file=sys.stderr,
    )
    print("leaderboard (scored, overall desc):", file=sys.stderr)
    for r in payload["leaderboard"]:
        print(f"  {r['overall']:>5} {r['grade']:<3} {r['domain']:<24} {r['segment']}", file=sys.stderr)

    drift = payload.get("drift")
    if drift:
        print(
            f"\ndrift vs {drift['baseline_ts']} ({drift['baseline_path']}): "
            f"{drift['n_moved']}/{drift['n_compared']} moved, max |Δ| {drift['max_abs_delta']}",
            file=sys.stderr,
        )
        for m in drift["moved"]:
            if m["delta"]:
                print(
                    f"  Δ {m['delta']:+6.1f}  {m['domain']:<24} {m['baseline']} -> {m['current']}",
                    file=sys.stderr,
                )
        for s in drift["status_changed"]:
            print(f"  status   {s['domain']:<24} {s['baseline']} -> {s['current']}", file=sys.stderr)
        if drift["added_members"]:
            print(f"  added: {', '.join(drift['added_members'])}", file=sys.stderr)
        if drift["removed_members"]:
            print(f"  removed: {', '.join(drift['removed_members'])}", file=sys.stderr)

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
