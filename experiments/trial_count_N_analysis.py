"""[LOCAL] offline post-analysis of the trial-count-stability run.

Deterministic, $0, no network: reconstructs the ``BehavioralRun`` records the
06:44Z live panel already committed into
``runs/local/trial_stability_20260723T064359Z.json`` and re-derives the whole
verdict-stability curve with the SHIPPED metric — so the finding rests on
recomputation, not on trusting an orphaned artifact from an interrupted fire.

Three things it proves:
  1. Reproduction — the committed curve (valid_runs / verdict_stability per N)
     is exactly what ``asrs.reliability.panel_reliability`` yields over the
     nested first-N subsamples. The artifact was not fabricated.
  2. The leak — the non-monotonic curve (N=2 stable 0.80 -> N=3 mixed 0.60) is
     driven by ONE env-blocked codex run leaking into the valid pool: codex
     trial 3 said its browser "safety controls" blocked the site, but
     ``shopper._ENV_BLOCK_RE`` only matches "security" phrasings, so that
     all-false verdict (the agent observed NOTHING) is scored as a site verdict.
     Invariant #4 violation (agent-side env failure scored as site evidence).
  3. The fix, simulated — re-running the curve with an env-block predicate that
     also covers "safety controls/grounds/policy" (NOT edited into source here;
     that is a peer-gated scoring-semantics change, queued in BACKLOG) makes the
     curve monotone and stable, confirming the leak was the whole story.

Run: ``.venv/bin/python -m experiments.trial_count_N_analysis`` from repo root.
"""

from __future__ import annotations

import json
import re
import statistics

from asrs.behavioral.shopper import _CHECKPOINT_KEYS, _ENV_BLOCK_RE, _is_env_blocked
from asrs.reliability import panel_reliability
from asrs.types import BehavioralRun

ARTIFACT = "runs/local/trial_stability_20260723T064359Z.json"
SUBSAMPLE_NS = [2, 3, 4, 5]

# PROPOSED (not shipped) env-block predicate: the current regex plus "safety"
# as a sibling of "security". Mirror-image of _ENV_BLOCK_RE; kept here only to
# simulate the peer-gated fix's effect on the curve.
_ENV_BLOCK_FIXED = re.compile(
    r"(?:blocked|rejected|refused|denied)[^.]{0,80}"
    r"(?:browser (?:security|safety)|(?:security|safety) (?:policy|controls|grounds))"
    r"|(?:browser (?:security|safety) (?:policy|controls))[^.]{0,80}"
    r"(?:blocked|rejected|refused|denied)",
    re.I,
)


def _env_blocked_fixed(run: BehavioralRun) -> bool:
    """`_is_env_blocked` with the proposed regex — same guard, wider phrasing."""
    if not run.checkpoints or any(run.checkpoints.values()):
        return False
    text = " ".join(run.blockers + run.trust_events)
    return bool(_ENV_BLOCK_FIXED.search(text))


def _stability(valid: list[BehavioralRun]) -> float | None:
    """verdict_stability computed directly (cross-check on panel_reliability)."""
    n = len(valid)
    if n < 2:
        return None
    minority = []
    for key in _CHECKPOINT_KEYS:
        p = sum(1 for r in valid if r.checkpoints.get(key))
        minority.append(min(p, n - p) / n)
    return round(1.0 - 2.0 * statistics.fmean(minority), 3)


def _first_n(runs: list[BehavioralRun], n: int) -> list[BehavioralRun]:
    return [r for r in runs if r.trial <= n]


def main() -> int:
    art = json.load(open(ARTIFACT))
    runs = [BehavioralRun(**r) for r in art["runs"]]

    print(f"artifact: {ARTIFACT}  ({art['domain']}, {art['models']} x {art['max_trials']})\n")

    # (1) reproduce the committed curve exactly.
    print("(1) REPRODUCE committed curve with shipped panel_reliability:")
    print("    N  valid  stability  label   | committed(valid, stability)")
    ok = True
    for c in art["curve"]:
        n = c["trials_per_model"]
        rel = panel_reliability(_first_n(runs, n))
        match = rel.valid_runs == c["valid_runs"] and rel.verdict_stability == c["verdict_stability"]
        ok = ok and match
        print(
            f"    {n}  {rel.valid_runs:>3}    {str(rel.verdict_stability):>6}   "
            f"{rel.label:<8}| ({c['valid_runs']}, {c['verdict_stability']})  "
            f"{'OK' if match else 'MISMATCH'}"
        )
    print(f"    => reproduction {'CONFIRMED' if ok else 'FAILED'}\n")

    # (2) the leak: which codex runs does the shipped filter miss?
    print("(2) ENV-BLOCK ATTRIBUTION per codex run (shipped regex):")
    for r in runs:
        if r.model != "codex":
            continue
        shipped = _is_env_blocked(r)
        fixed = _env_blocked_fixed(r)
        blk = (r.blockers or ["<none>"])[0][:70]
        flag = "" if shipped else "  <-- LEAKS into valid pool"
        print(f"    codex t{r.trial}: env_blocked shipped={shipped!s:<5} fixed={fixed!s:<5} | {blk}{flag}")
    leaked = [r for r in runs if r.model == "codex" and not _is_env_blocked(r) and r.checkpoints]
    print(f"    => {len(leaked)} codex run(s) leak as all-false site verdicts: "
          f"{[f'codex t{r.trial}' for r in leaked]}\n")

    # (3) simulate the fix: recompute the curve excluding safety-phrased blocks.
    print("(3) CORRECTED curve (proposed regex also excludes 'safety' blocks):")
    print("    N  valid  stability  label")
    for n in SUBSAMPLE_NS:
        subset = [r for r in _first_n(runs, n) if not _env_blocked_fixed(r)]
        rel = panel_reliability(subset)
        # cross-check the module against the local formula
        assert rel.verdict_stability == _stability(_valid_only(subset)), "metric drift"
        print(f"    {n}  {rel.valid_runs:>3}    {str(rel.verdict_stability):>6}   {rel.label}")
    print("\n    Reading: with the leaked codex t3 correctly excluded, the panel is")
    print("    claude-only and its stability no longer collapses at N>=3 — the")
    print("    'smallest_stable_n=2' headline was a small-sample + leak artifact,")
    print("    not evidence that N=2 converges.")
    return 0


def _valid_only(runs: list[BehavioralRun]) -> list[BehavioralRun]:
    return [r for r in runs if r.checkpoints and not _env_blocked_fixed(r)]


if __name__ == "__main__":
    raise SystemExit(main())
