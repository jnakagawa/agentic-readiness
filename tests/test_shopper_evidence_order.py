"""Shopper ``by_run`` evidence must be reproducible under panel-order permutation.

Third in the arrival-order-invariance lineage that started with
``tests/test_attribution.py`` (Cycle 253, reachability ``block_statements``) and
``tests/test_trust_panel_reproducibility.py`` (Cycle 255, trust-panel
``refusing_models``). Those closed the sliced/selected surfaces; the remaining
arrival-order surfaces were the two self-labeled ``by_run`` evidence lists in
``asrs.behavioral.shopper``:

  * ``_aggregate`` (zero-valid CANT_TEST branch) — one row per attempted run,
  * ``_trust_live_check`` — one row per valid run.

Both rows carry a ``(model, trial)`` self-label, so a reader can still identify
each panelist, but the LIST ORDER was arrival order. In production ``run_panel``
builds runs in a fixed ``for model: for trial`` loop, so it is deterministic
TODAY — but the same latent hole the siblings had: if panel construction ever
parallelizes (as the earlier fixes were explicitly hardened against), two
identical panels answering in a different order would emit byte-DIFFERENT
evidence for the SAME score, violating "evidence or it didn't happen"'s
reproducibility. The fix orders both lists by the ``(model, trial)`` label — a
key that is unique and total in production — so the whole CheckResult is
byte-identical under any panel permutation.

Off the scoring path: the canonical pair is scored statically (no behavioral
runs), and points/status here are already permutation-invariant counts; only the
evidence LIST ORDER is pinned. Rubric version, probes, and the canonical delta
are untouched.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.behavioral import shopper as S  # noqa: E402
from asrs.types import BehavioralRun  # noqa: E402


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _by_id(checks):
    return {c.check_id: c for c in checks}


def _valid(model: str, trial: int, trust_events=None) -> BehavioralRun:
    """A run that observed the site (non-empty checkpoints) — counts as valid."""
    return BehavioralRun(
        model=model, trial=trial,
        checkpoints={"found_product": True, "understood_pricing": True,
                     "found_purchase_path": True, "machine_payable_path": True,
                     "no_human_gate": True},
        blockers=[], trust_events=list(trust_events or []),
        transcript_path=f"runs/{model}-{trial}.txt",
    )


def _failed(model: str, trial: int) -> BehavioralRun:
    """A run whose own stack died before a verdict: empty checkpoints, plain
    (non-env-block) blocker. Lands in neither `valid` nor `env_blocked`, so a
    whole panel of these drives `_aggregate` into the zero-valid CANT_TEST
    branch that emits the first `by_run` list."""
    return BehavioralRun(
        model=model, trial=trial, checkpoints={},
        blockers=[f"run-failed: {model} cli crashed before a verdict"],
        trust_events=[], transcript_path=f"runs/{model}-{trial}.txt",
    )


# ---------------------------------------------------------------------------
# 1. The zero-valid CANT_TEST `by_run` (one row per attempted run) must not
#    depend on the order the panel happened to be assembled in. Metamorphic
#    (forward vs reversed panel => byte-identical checks) with teeth (the raw
#    arrival-order projection the pre-fix code used DID differ under reversal).
# ---------------------------------------------------------------------------
def test_cant_test_by_run_is_order_invariant() -> None:
    print("test_cant_test_by_run_is_order_invariant")
    # Distinct (model, trial) labels so any order leak is visible in the list.
    fwd = [_failed("claude", 1), _failed("claude", 2), _failed("codex", 1)]
    rev = list(reversed(fwd))

    # NON-VACUOUS: with zero valid runs this really is the CANT_TEST branch.
    checks_fwd = _by_id(S._aggregate("x.example", fwd))
    checks_rev = _by_id(S._aggregate("x.example", rev))
    fp = checks_fwd["bhv_found_product"]
    _check(fp.status.name == "CANT_TEST" and fp.evidence["valid_runs"] == 0,
           "a fully-failed panel is the zero-valid CANT_TEST branch")
    _check(len(fp.evidence["by_run"]) == 3, "by_run carries a row per attempted run")

    # THE INVARIANT: reversing panel order changes NOTHING — every check byte-
    # identical, including the by_run list order.
    _check(checks_fwd == checks_rev,
           "CANT_TEST checks are byte-identical under panel-order reversal")

    # THE PROPERTY: rows are in (model, trial) order, not arrival order.
    labels = [(r["model"], r["trial"]) for r in fp.evidence["by_run"]]
    _check(labels == [("claude", 1), ("claude", 2), ("codex", 1)],
           "by_run rows are ordered by the (model, trial) label")

    # TEETH: the pre-fix code projected `for r in runs` (arrival order); that raw
    # projection DID differ between the two panel orders, so the invariant above
    # is a real claim about the fix, not an inert metric.
    raw_fwd = [(r.model, r.trial) for r in fwd]
    raw_rev = [(r.model, r.trial) for r in rev]
    _check(raw_fwd != raw_rev,
           "pre-fix arrival-order projection was order-sensitive (guard has teeth)")


# ---------------------------------------------------------------------------
# 2. The live-trust `by_run` (one row per valid run) has the same property on
#    the valid-panel path. Distinct trust_events per panelist so a leak would
#    show in the row payloads, not just the labels.
# ---------------------------------------------------------------------------
def test_trust_live_by_run_is_order_invariant() -> None:
    print("test_trust_live_by_run_is_order_invariant")
    fwd = [
        _valid("claude", 1, trust_events=["claude-warned-about-x"]),
        _valid("codex", 1, trust_events=["codex-warned-about-y"]),
    ]
    rev = list(reversed(fwd))

    tl_fwd = _by_id(S._aggregate("x.example", fwd))["trust_live_session"]
    tl_rev = _by_id(S._aggregate("x.example", rev))["trust_live_session"]

    # NON-VACUOUS: both runs are valid and both carry trust_events, so by_run has
    # two distinct rows whose order could leak.
    _check(len(tl_fwd.evidence["by_run"]) == 2, "by_run has a row per valid run")

    # THE INVARIANT: byte-identical under reversal, whole CheckResult.
    _check(tl_fwd == tl_rev,
           "trust_live_session is byte-identical under panel-order reversal")

    # THE PROPERTY: (model, trial) order — claude before codex regardless of input.
    labels = [(r["model"], r["trial"]) for r in tl_fwd.evidence["by_run"]]
    _check(labels == [("claude", 1), ("codex", 1)],
           "trust by_run rows are ordered by the (model, trial) label")

    # TEETH: the raw arrival-order projection differed between the two orders.
    raw_fwd = [(r.model, r.trial) for r in fwd]
    raw_rev = [(r.model, r.trial) for r in rev]
    _check(raw_fwd != raw_rev,
           "pre-fix arrival-order projection was order-sensitive (guard has teeth)")


def main() -> int:
    tests = [
        test_cant_test_by_run_is_order_invariant,
        test_trust_live_by_run_is_order_invariant,
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
    raise SystemExit(main())
