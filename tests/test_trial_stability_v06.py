"""Post-v0.6 regression test on the committed trial-count panel (invariant #4).

Runnable directly, no pytest required:

    python tests/test_trial_stability_v06.py

TRUTH check — does the SHIPPED score read stable on REAL committed panel data?

The 06:44Z live claude+codex x5 panel on drift-flight.org
(``runs/local/trial_stability_20260723T064359Z.json``) was captured BEFORE
rubric v0.6 shipped. At capture time ``shopper._ENV_BLOCK_RE`` matched only
"security" phrasings, so codex trial 3 — which said its browser "safety
controls" blocked the site — leaked into the valid pool as an all-false SITE
verdict (invariant #4 violation). That leak is why the artifact's committed
``curve`` block is non-monotonic: N=2 stable 0.80 -> N=3 mixed 0.60.

v0.6 broadened the classifier so "safety" is a sibling of "security". This
test recomputes the panel over the committed runs with the SHIPPED
``asrs.reliability.panel_reliability`` (which routes env-blocked runs out
through the same ``_is_env_blocked``) and pins three facts about the fix on
real data:

  1. Every codex run in the panel — including t3, the former leak — is now
     env-blocked, so the valid pool is claude-only (the honest reading: codex
     never observed this domain, its hosting stack refused).
  2. With the leak removed the trial-count curve is monotone non-decreasing
     and reads "stable" at every N>=2 (0.80 -> 0.867 -> 0.90 -> 0.92).
  3. The post-v0.6 curve DIFFERS from the artifact's committed pre-v0.6 curve
     at N>=3 — documenting that the committed ``curve`` block is a superseded
     pre-fix snapshot, not a fabrication. The evidence file is append-only
     (invariant #5) and stays as the historical record; this test is where the
     corrected reading lives.

No network, no CLIs: pure offline recomputation over committed evidence.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.behavioral.shopper import _is_env_blocked  # noqa: E402
from asrs.reliability import panel_reliability  # noqa: E402
from asrs.types import BehavioralRun  # noqa: E402

ARTIFACT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "runs", "local", "trial_stability_20260723T064359Z.json",
)

# Post-v0.6 corrected curve: (trials_per_model, valid_runs, verdict_stability).
# Claude-only after every codex run routes out as env-blocked.
_EXPECTED_POSTV06 = [
    (2, 2, 0.8),
    (3, 3, 0.867),
    (4, 4, 0.9),
    (5, 5, 0.92),
]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _load_runs() -> tuple[dict, list[BehavioralRun]]:
    art = json.load(open(ARTIFACT))
    return art, [BehavioralRun(**r) for r in art["runs"]]


def _first_n(runs: list[BehavioralRun], n: int) -> list[BehavioralRun]:
    return [r for r in runs if r.trial <= n]


def test_all_codex_runs_env_blocked_under_v06() -> None:
    """Every codex run — including t3, the former 'safety' leak — is env-blocked."""
    _art, runs = _load_runs()
    codex = [r for r in runs if r.model == "codex"]
    _check(len(codex) == 5, f"panel has 5 codex runs, got {len(codex)}")
    leaked = [r for r in codex if not _is_env_blocked(r)]
    _check(not leaked,
           "no codex run leaks into the valid pool under shipped v0.6 "
           f"(leaks: {[f'codex t{r.trial}' for r in leaked]})")
    t3 = next(r for r in codex if r.trial == 3)
    _check(_is_env_blocked(t3),
           "codex t3 ('browser safety controls') is now env-blocked, not a site verdict")


def test_valid_pool_is_claude_only() -> None:
    """After env-block routing the panel measures claude only — codex saw nothing."""
    _art, runs = _load_runs()
    valid = [r for r in runs if r.checkpoints and not _is_env_blocked(r)]
    models = {r.model for r in valid}
    _check(models == {"claude"},
           f"valid pool is claude-only, got models {sorted(models)}")


def test_postv06_curve_is_monotone_and_stable() -> None:
    """The corrected trial-count curve is monotone non-decreasing and stable at every N>=2."""
    _art, runs = _load_runs()
    prev = -1.0
    for n, exp_valid, exp_stab in _EXPECTED_POSTV06:
        rel = panel_reliability(_first_n(runs, n))
        _check(rel.valid_runs == exp_valid,
               f"N={n}: {exp_valid} valid runs (claude-only), got {rel.valid_runs}")
        _check(rel.verdict_stability == exp_stab,
               f"N={n}: verdict_stability {exp_stab}, got {rel.verdict_stability}")
        _check(rel.label == "stable", f"N={n}: label 'stable', got {rel.label!r}")
        _check(rel.verdict_stability >= prev,
               f"N={n}: curve non-decreasing ({prev} -> {rel.verdict_stability})")
        prev = rel.verdict_stability


def test_postv06_curve_supersedes_committed_prefix_curve() -> None:
    """The recomputed curve differs from the artifact's pre-v0.6 curve at N>=3."""
    art, runs = _load_runs()
    committed = {c["trials_per_model"]: c["verdict_stability"] for c in art["curve"]}
    # N=2 was claude-only even pre-fix (both codex t1/t2 already matched "security"),
    # so it agrees; N>=3 is where the leaked codex t3 moved the reading.
    rel2 = panel_reliability(_first_n(runs, 2))
    _check(rel2.verdict_stability == committed[2],
           f"N=2 unchanged by the fix (both {committed[2]})")
    moved = []
    for n in (3, 4, 5):
        rel = panel_reliability(_first_n(runs, n))
        if rel.verdict_stability != committed[n]:
            moved.append(n)
    _check(moved == [3, 4, 5],
           f"N>=3 readings moved after the fix (committed curve superseded), moved={moved}")
    _check(committed[3] < 0.8,
           f"committed pre-v0.6 N=3 was mixed ({committed[3]} < 0.8) — the leak")


def main() -> int:
    tests = [
        test_all_codex_runs_env_blocked_under_v06,
        test_valid_pool_is_claude_only,
        test_postv06_curve_is_monotone_and_stable,
        test_postv06_curve_supersedes_committed_prefix_curve,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL: {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
