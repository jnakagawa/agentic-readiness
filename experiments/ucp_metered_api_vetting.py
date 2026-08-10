"""[LOCAL] experiment — honest-classification vetting of the aloyoga.com
UCP high-corner baseline candidate (invariant #4).

The BACKLOG P2 FORWARD frontier (a) flags **aloyoga.com 81.2 B** (access /
legibility / trust all 100.0, transactability 50.0) as the HIGHEST live-UCP
overall observed — above the current top UCP pin kith.com (70.3) — and therefore
a strong candidate for a NEW high-corner UCP frozen-replay baseline. But it
carries a specific invariant-#4 risk, recorded in STATE and the BACKLOG:

    "a clothing brand claiming metered_api risks a topic-word over-claim, the
     joinhexagon/thebotwire pattern."

A retail apparel brand is a `physical_good` merchant; its overall of 81.2 is
propped up by a `metered_api` claim that, if it came from a flimsy topic-word
match (a login "authenticate your account", a marketing "image", a bare "API"
in a cookie/analytics footer), would be a DISHONEST classification — the site
would be scored for a capability it does not actually offer an agent. Truth
outranks the pitch: we do NOT pin a high number built on an over-claim.

The accepted UCP pins (gymshark.com, kith.com, hardgraft.com) are ALREADY
classified `{metered_api, physical_good}` and merged; gymshark's metered_api is
recorded as coming "from its /llms.txt UCP agent-commerce endpoints" — a genuine
agent-facing programmatic surface. So the vetting bar is concrete and relative,
not subjective:

    Does aloyoga.com's metered_api evidence come from the SAME class of
    surface/signal as the already-accepted pins (a real agent-commerce / API
    surface), or from a flimsier topic-word match on a retail marketing page?

Method: for each domain, `asrs.offering.discover_offering` (read-only GETs of the
site's OWN surfaces — homepage / llms.txt / manifest / OpenAPI / agent card /
pricing / docs, $0) yields the OfferingProfile. Every archetype claim carries its
firing signals, each an (archetype, surface, label, quote) evidence tuple — so a
skeptic can read EXACTLY which signal fired on WHICH surface with WHAT quoted
text. We surface the full metered_api evidence for every domain and static-score
each ($0, shipped `_run_probes`->`scoring.score`) to confirm the candidate's
overall reproduces. The accepted pins are the honest reference distribution.

$0 (invariant #1) BY CONSTRUCTION: discovery + static score are read-only GETs;
no `--behavioral` (so no free-tier probe fires), no zero CLI, no signing path,
never a nonzero `--max-pay`.

Score-neutral: reads ONLY the shipped discovery + scoring paths; changes no
scoring semantics, adds no probe, bumps no rubric version. The committed dataset
is evidence under runs/local/.

Vendor-neutral: every domain is discovered + scored through the SAME path with NO
special-casing; the `tag` label is context for reading the result, never an input.

Why [LOCAL]: the cloud env cannot reach these domains (STATE.md network policy).

Run:  .venv/bin/python experiments/ucp_metered_api_vetting.py
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
from asrs.offering import discover_offering  # noqa: E402

FETCH_TIMEOUT_S = 12.0
_TARGET = "metered_api"

# (domain, tag). `tag` positions the candidate for READING the result; it is
# never read by the scorer/classifier. Two groups:
#   * VETTING TARGETS — the forward-frontier (a) high-corner candidates whose
#     metered_api honesty decides whether they are pinnable.
#   * ACCEPTED PINS — already-merged UCP baselines classified {metered_api,
#     physical_good}; the honest reference distribution for metered_api evidence.
CANDIDATES = [
    # --- vetting targets (forward frontier a) ---
    ("aloyoga.com", "vet:high-corner-candidate-81.2"),
    ("tecovas.com", "vet:lesser-lead-73.6"),
    ("rothys.com", "vet:lesser-lead-69.5"),
    ("chubbiesshorts.com", "vet:lesser-lead-67.1"),
    # --- accepted pins (honest metered_api reference distribution) ---
    ("gymshark.com", "ref:accepted-pin-62.4"),
    ("kith.com", "ref:accepted-pin-70.3"),
]


def _signal_rows(profile, archetype: str) -> list[dict]:
    """Every firing signal for one archetype: (surface, label, quote)."""
    rows: list[dict] = []
    for claim in profile.claimed:
        if claim.archetype != archetype:
            continue
        for s in claim.signals:
            rows.append({"surface": s.surface, "label": s.label, "quote": s.quote})
    return rows


def _all_claims(profile) -> dict:
    """archetype -> {strength, labels} for the full claimed set."""
    out: dict = {}
    for claim in profile.claimed:
        out[claim.archetype] = {
            "strength": claim.strength,
            "labels": sorted({s.label for s in claim.signals}),
        }
    return out


def _static_score(raw: str, rubric) -> dict:
    """Full static score ($0) — confirm the candidate's overall reproduces."""
    checks = _run_probes(FetchContext(raw, timeout=FETCH_TIMEOUT_S))
    report = scoring.score(checks, rubric, raw)
    return {
        "scored": report.scored,
        "overall": report.overall_score,
        "grade": report.grade,
        "pillars": report.pillar_scores,
        "caps_applied": report.caps_applied,
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
            profile = discover_offering(FetchContext(raw, timeout=FETCH_TIMEOUT_S))
            metered = _signal_rows(profile, _TARGET)
            row["surfaces_seen"] = profile.surfaces_seen
            row["archetypes"] = profile.archetypes
            row["all_claims"] = _all_claims(profile)
            row["metered_api_evidence"] = metered
            row["metered_api_labels"] = sorted({m["label"] for m in metered})
            row["metered_api_surfaces"] = sorted({m["surface"] for m in metered})
            row["claims_metered_api"] = _TARGET in profile.archetypes
            row["score"] = _static_score(raw, rubric)
            row["error"] = None
        except Exception as exc:  # noqa: BLE001 — reachability failure, not a site FAIL
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["score"] = None
        row["elapsed_s"] = round(time.time() - t0, 2)
        rows.append(row)
        sc = row.get("score")
        print(
            f"  {raw:22s} {tag:30s} "
            f"metered_api={'Y' if row.get('claims_metered_api') else '-'} "
            f"labels={row.get('metered_api_labels')} "
            f"overall={sc['overall'] if sc else '--'} {sc['grade'] if sc else ''}"
        )

    summary = {
        "n_candidates": len(CANDIDATES),
        "vetting_targets": {
            r["domain"]: {
                "overall": r["score"]["overall"] if r.get("score") else None,
                "claims_metered_api": r.get("claims_metered_api"),
                "metered_api_labels": r.get("metered_api_labels"),
                "metered_api_surfaces": r.get("metered_api_surfaces"),
            }
            for r in rows
            if r["tag"].startswith("vet:")
        },
        "accepted_pin_reference": {
            r["domain"]: {
                "overall": r["score"]["overall"] if r.get("score") else None,
                "metered_api_labels": r.get("metered_api_labels"),
                "metered_api_surfaces": r.get("metered_api_surfaces"),
            }
            for r in rows
            if r["tag"].startswith("ref:")
        },
    }

    artifact = {
        "ts": ts,
        "kind": "ucp-metered-api-vetting",
        "spend": "$0 (read-only discovery GETs + static score; no --behavioral/--max-pay/payment/zero-CLI)",
        "target_archetype": _TARGET,
        "question": (
            "Does aloyoga.com's metered_api evidence come from the same class of "
            "surface/signal as the accepted UCP pins (a real agent-commerce/API "
            "surface), or from a flimsier topic-word match on a retail marketing page?"
        ),
        "summary": summary,
        "rows": rows,
    }
    out_dir = Path("runs") / "local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ucp_metered_api_vetting_{ts}.json"
    with open(out_path, "w") as fh:
        json.dump(artifact, fh, indent=1, sort_keys=False)

    print()
    print(f"artifact: {out_path}")


if __name__ == "__main__":
    main()
