"""[LOCAL] experiment — what shopper trial count N stabilizes the panel?

Answers the standing open question (STATE.md): "what N drives
``verdict_stability`` above ~0.8 on the canonical pair." Designed in-cloud
(Cycle 3), executed on the networked machine (needs the claude + codex CLIs).

Design — nested subsampling, NOT independent re-runs. The backlog's literal
recipe was three separate runs (``--trials 2``, ``3``, ``5``), which spends
2+3+5 = 10 codex calls AND confounds the effect of N with between-invocation
drift (each run is a fresh draw). Instead we run the panel ONCE at trials=5 and
compute ``panel_reliability`` over the first-N trials of each model
(N in {2,3,4,5}). The subsamples are NESTED (first-2 subset of first-3 subset
of first-5), so stability(N) isolates the effect of trial count from the noise
of separate draws, and the whole curve costs 5 codex + 5 claude sessions
(half the per-cycle codex ceiling). Trials are i.i.d., so "first N" is a valid
random subsample.

Reuses the SAME pure metric the score/report use (``asrs.reliability`` /
``asrs.behavioral.shopper``), so the experiment and the shipped readout can
never diverge on what "stable" means. $0: no free-tier probe, no zero CLI, no
signing path is touched — only the read-only shopper panel runs.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone

from asrs.behavioral.shopper import run_panel
from asrs.reliability import panel_reliability

DOMAIN = "drift-flight.org"  # the refusal-free canonical domain (STATE open Qs)
TASK = "purchase this site's primary product or service"
MODELS = ["claude", "codex"]
MAX_TRIALS = 5
SUBSAMPLE_NS = [2, 3, 4, 5]
STABLE_MIN = 0.8


def _first_n_per_model(runs, n):
    """Nested subsample: every run whose 1-indexed trial is <= n."""
    return [r for r in runs if r.trial <= n]


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"[trial-N] panel on {DOMAIN}: {MODELS} x {MAX_TRIALS} trials", flush=True)

    runs, _checks = run_panel(DOMAIN, TASK, trials=MAX_TRIALS, models=MODELS, out_dir="runs")

    curve = []
    for n in SUBSAMPLE_NS:
        subset = _first_n_per_model(runs, n)
        rel = panel_reliability(subset)
        curve.append(
            {
                "trials_per_model": n,
                "attempted_runs": len(subset),
                "valid_runs": rel.valid_runs,
                "verdict_stability": rel.verdict_stability,
                "flip_rate": rel.flip_rate,
                "flipped_checkpoints": rel.flipped_checkpoints,
                "trust_event_agreement": rel.trust_event_agreement,
                "trust_events_unanimous": rel.trust_events_unanimous,
                "label": rel.label,
            }
        )

    stable_ns = [
        c["trials_per_model"]
        for c in curve
        if c["verdict_stability"] is not None and c["verdict_stability"] >= STABLE_MIN
    ]
    smallest_stable_n = min(stable_ns) if stable_ns else None

    artifact = {
        "ts": ts,
        "kind": "trial-count-stability",
        "domain": DOMAIN,
        "task": TASK,
        "models": MODELS,
        "max_trials": MAX_TRIALS,
        "stable_min": STABLE_MIN,
        "smallest_stable_n": smallest_stable_n,
        "curve": curve,
        "runs": [asdict(r) for r in runs],
    }

    out_path = f"runs/local/trial_stability_{ts}.json"
    with open(out_path, "w") as fh:
        json.dump(artifact, fh, indent=1)

    print(f"\n[trial-N] N   valid  stability  flip_rate  label", flush=True)
    for c in curve:
        vs = "None " if c["verdict_stability"] is None else f"{c['verdict_stability']:.3f}"
        fr = "None " if c["flip_rate"] is None else f"{c['flip_rate']:.3f}"
        print(
            f"[trial-N] {c['trials_per_model']}   {c['valid_runs']:>3}    "
            f"{vs:>6}     {fr:>5}     {c['label']}",
            flush=True,
        )
    print(f"\n[trial-N] smallest N with stability >= {STABLE_MIN}: {smallest_stable_n}", flush=True)
    print(f"[trial-N] artifact: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
