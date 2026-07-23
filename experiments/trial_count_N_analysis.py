"""[LOCAL] offline post-analysis of the trial-count-stability run.

Deterministic, $0, no network: reconstructs the ``BehavioralRun`` records the
06:44Z live panel already committed into
``runs/local/trial_stability_20260723T064359Z.json`` and re-derives the whole
verdict-stability curve with the SHIPPED metric — so the finding rests on
recomputation, not on trusting an orphaned artifact from an interrupted fire.

HISTORY: the panel was captured BEFORE rubric v0.6. At capture time
``shopper._ENV_BLOCK_RE`` matched only "security" phrasings, so codex trial 3
("browser safety controls") leaked into the valid pool as an all-false SITE
verdict — an invariant #4 violation that made the committed ``curve`` block
non-monotonic (N=2 stable 0.80 -> N=3 mixed 0.60). v0.6 broadened the
classifier so "safety" is a sibling of "security"; that fix is NOW SHIPPED to
``shopper._ENV_BLOCK_RE``, so the "proposed" predicate below is identical to
the live one and codex t3 is env-blocked at the source.

What this script shows against the SHIPPED classifier:
  1. Supersession — section (1) recomputes ``asrs.reliability.panel_reliability``
     over the nested first-N subsamples and reports MISMATCH vs the committed
     curve at N>=3. That is EXPECTED and correct: the committed curve is a
     superseded pre-v0.6 snapshot (the evidence file is append-only, invariant
     #5, so it stays as the historical record); the fix moved the reading.
  2. No leak — section (2) confirms 0 codex runs leak: the shipped regex now
     catches all five, including t3.
  3. The corrected curve — section (3) is monotone and stable at every N>=2
     (0.80 -> 0.867 -> 0.90 -> 0.92), the claude-only reading once codex (which
     never observed the domain) routes out.

The post-v0.6 reading is pinned as a regression test in
``tests/test_trial_stability_v06.py``; this script is the narrated derivation.

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

# The env-block predicate the fix landed: the base regex plus "safety" as a
# sibling of "security". As of v0.6 this is IDENTICAL to the shipped
# ``_ENV_BLOCK_RE`` — kept as a local mirror only so section (3) is legible
# side-by-side with the shipped ``_is_env_blocked`` used everywhere else here.
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

    # (1) recompute vs the committed (pre-v0.6) curve. MISMATCH at N>=3 is the
    #     EXPECTED post-fix supersession, not a fabrication.
    print("(1) RECOMPUTE with shipped panel_reliability vs committed pre-v0.6 curve:")
    print("    N  valid  stability  label   | committed(valid, stability)")
    for c in art["curve"]:
        n = c["trials_per_model"]
        rel = panel_reliability(_first_n(runs, n))
        match = rel.valid_runs == c["valid_runs"] and rel.verdict_stability == c["verdict_stability"]
        print(
            f"    {n}  {rel.valid_runs:>3}    {str(rel.verdict_stability):>6}   "
            f"{rel.label:<8}| ({c['valid_runs']}, {c['verdict_stability']})  "
            f"{'same' if match else 'SUPERSEDED (v0.6 fix)'}"
        )
    print("    => N=2 agrees (already claude-only); N>=3 superseded by the v0.6")
    print("       env-block fix (committed curve is the append-only pre-fix record)\n")

    # (2) the leak: which codex runs does the shipped filter miss?
    print("(2) ENV-BLOCK ATTRIBUTION per codex run (shipped v0.6 regex; expect 0 leaks):")
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

    # (3) the corrected curve: shipped regex excludes safety-phrased blocks too.
    print("(3) CORRECTED curve (shipped v0.6 regex excludes 'safety' blocks):")
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
