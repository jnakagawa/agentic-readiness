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
    # retail with emerging agentic rails (llms.txt / agent manifests / agent checkout)
    ("deathwishcoffee.com", "retail:emerging-rails"),
    ("warbyparker.com", "retail:emerging-rails"),
    ("allbirds.com", "retail:emerging-rails"),
    # retail without agentic rails (browser-only checkout)
    ("moleskine.com", "retail:no-rails"),
    ("rei.com", "retail:no-rails"),
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
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
