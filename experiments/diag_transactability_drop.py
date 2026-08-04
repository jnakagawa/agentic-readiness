"""[LOCAL] CHECK-level diagnosis of the driftflight.com transactability drop.

Opened as a [LOCAL] item Cycle 126: the live static re-score of the with-rails
canonical anchor (driftflight.com) shows transactability 87.5 -> 62.5 vs the
frozen Jul-23 fixture, dropping the overall 85.5 B -> 76.2 C. The pillar-level
attribution is pinned in-cloud (test_canonical_history); the remaining [LOCAL]
work is strictly CHECK-level: re-score LIVE and diff WHICH transactability check
flipped (x402_probe / mcp_surface / self_serve_payg).

This script replays the committed fixture (frozen) and scores the domain LIVE
through the SAME probe + scoring pipeline, then prints a per-check diff of the
transactability pillar. Static crawl only ($0, invariant #1: no --behavioral, no
nonzero auth). Diagnosis only — it changes no scoring semantics.

Run:  .venv/bin/python experiments/diag_transactability_drop.py
"""

from __future__ import annotations

import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs import scoring  # noqa: E402
from asrs.cli import _run_probes  # noqa: E402
from asrs.fetch import FetchContext  # noqa: E402

_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")
DOMAIN = "driftflight.com"
_TX = "transactability"


def _tx_checks(checks):
    out = {}
    for c in checks:
        if c.pillar == _TX:
            out[c.check_id] = c
    return out


def _row(c):
    return {
        "status": c.status.value if hasattr(c.status, "value") else str(c.status),
        "points": c.points,
        "max_points": c.max_points,
        "finding": c.finding,
        "evidence_keys": sorted(c.evidence.keys()) if c.evidence else [],
    }


def _score_fixture(domain):
    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
    checks = _run_probes(ctx)
    report = scoring.score(checks, scoring.load_rubric(None), domain)
    return report, checks


def _score_live(domain):
    ctx = FetchContext(domain)
    checks = _run_probes(ctx)
    report = scoring.score(checks, scoring.load_rubric(None), domain)
    return report, checks


def main():
    frozen_report, frozen_checks = _score_fixture(DOMAIN)
    print(f"[frozen fixture] {DOMAIN}: overall {frozen_report.overall_score} "
          f"{frozen_report.grade}  tx pillar "
          f"{frozen_report.pillar_scores.get(_TX)}")

    live_report, live_checks = _score_live(DOMAIN)
    print(f"[LIVE crawl]     {DOMAIN}: overall {live_report.overall_score} "
          f"{live_report.grade}  tx pillar "
          f"{live_report.pillar_scores.get(_TX)}")
    print()

    frozen = _tx_checks(frozen_checks)
    live = _tx_checks(live_checks)
    all_ids = sorted(set(frozen) | set(live))

    diff = {}
    print("=== transactability per-check diff (frozen -> LIVE) ===")
    for cid in all_ids:
        f = frozen.get(cid)
        l = live.get(cid)
        fr = _row(f) if f else None
        lr = _row(l) if l else None
        flipped = (fr != lr)
        diff[cid] = {"frozen": fr, "live": lr, "flipped": flipped}
        marker = "  <== FLIPPED" if flipped else ""
        fp = fr["points"] if fr else None
        lp = lr["points"] if lr else None
        fs = fr["status"] if fr else None
        ls = lr["status"] if lr else None
        print(f"  {cid:18s} points {fp} -> {lp}   status {fs} -> {ls}{marker}")

    print()
    print("=== detail on flipped checks ===")
    for cid, d in diff.items():
        if d["flipped"]:
            print(f"\n--- {cid} ---")
            print("  frozen:", json.dumps(d["frozen"], indent=2))
            print("  live:  ", json.dumps(d["live"], indent=2))
            # dump the live check's full evidence for capability-terms explanation
            lc = live.get(cid)
            if lc and lc.evidence:
                print("  live evidence:", json.dumps(lc.evidence, indent=2, default=str)[:2000])
            fc = frozen.get(cid)
            if fc and fc.evidence:
                print("  frozen evidence:", json.dumps(fc.evidence, indent=2, default=str)[:2000])

    summary = {
        "domain": DOMAIN,
        "frozen_overall": frozen_report.overall_score,
        "live_overall": live_report.overall_score,
        "frozen_tx_pillar": frozen_report.pillar_scores.get(_TX),
        "live_tx_pillar": live_report.pillar_scores.get(_TX),
        "per_check": diff,
    }
    return summary


if __name__ == "__main__":
    s = main()
    out = os.environ.get("DIAG_OUT")
    if out:
        with open(out, "w") as fh:
            json.dump(s, fh, indent=2, default=str)
        print(f"\n[wrote] {out}")
