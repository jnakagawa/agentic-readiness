"""Tests for the task battery (rubric-agnostic reliability layer, Cycle 2).

Runnable directly, no pytest required:

    python tests/test_battery.py

Covers the load-bearing behaviours with synthetic ``BehavioralRun`` fixtures
(no network, no CLIs):
  - load_battery parses the shipped default_v1.yaml and rejects malformed files;
  - per-task checkpoint fractions over VALID runs only (env-blocked + failed
    runs are excluded, exactly as the per-task score excludes them);
  - a task with no valid run is "no signal", never a site failure, and is
    dropped from the cross-task mean/spread;
  - cross-task spread is the reliability signal: 0 when a checkpoint behaves
    identically across intents, positive when it is intent-dependent;
  - a single signal task has spread 0 (no variance to observe yet), not a crash.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import battery as B  # noqa: E402
from asrs.battery import Battery, BatteryTask  # noqa: E402
from asrs.types import BehavioralRun  # noqa: E402

_KEYS = ["found_product", "understood_pricing", "found_purchase_path",
         "machine_payable_path", "no_human_gate"]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(model="claude", trial=1, **cp) -> BehavioralRun:
    """A valid run: checkpoints default False, override by keyword."""
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(model=model, trial=trial, checkpoints=checkpoints)


def _env_blocked_run(model="codex", trial=1) -> BehavioralRun:
    """All-False checkpoints + own-stack block language -> excluded as env-blocked."""
    return BehavioralRun(
        model=model, trial=trial,
        checkpoints={k: False for k in _KEYS},
        blockers=["navigation blocked by browser security policy"],
    )


def _failed_run(model="codex", trial=1) -> BehavioralRun:
    """No verdict -> empty checkpoints -> excluded."""
    return BehavioralRun(model=model, trial=trial, checkpoints={},
                         blockers=["run-failed: cli-error"])


# ---------------------------------------------------------------------------
# 1. Shipped battery loads and is vendor-neutral.
# ---------------------------------------------------------------------------
def test_load_default_battery() -> None:
    print("test_load_default_battery")
    bat = B.load_battery()  # default path -> batteries/default_v1.yaml
    _check(bat.id == "default_v1", f"id is default_v1, got {bat.id!r}")
    _check(len(bat.tasks) == 5, f"5 tasks, got {len(bat.tasks)}")
    ids = [t.id for t in bat.tasks]
    _check(len(set(ids)) == 5, "task ids are unique")
    _check(all(t.intent for t in bat.tasks), "every task has an intent")
    kinds = {t.kind for t in bat.tasks}
    _check("physical_good" in kinds and "digital_service" in kinds,
           f"battery spans archetypes: {sorted(kinds)}")
    # Vendor neutrality: no intent may name the canonical domains or a product brand.
    blob = " ".join(t.intent.lower() for t in bat.tasks)
    for banned in ("drift", "driftflight", ".com", ".org", "http"):
        _check(banned not in blob, f"no vendor/domain token {banned!r} in intents")


# ---------------------------------------------------------------------------
# 2. Malformed batteries fail loud.
# ---------------------------------------------------------------------------
def test_malformed_batteries_raise(tmp=None) -> None:
    print("test_malformed_batteries_raise")
    import tempfile

    def _write(text: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        return path

    cases = {
        "no tasks list": "id: x\ndescription: y\n",
        "task without id": "id: x\ntasks:\n  - intent: do a thing\n",
        "task without intent": "id: x\ntasks:\n  - id: t1\n",
        "duplicate id": "id: x\ntasks:\n  - id: t1\n    intent: a\n  - id: t1\n    intent: b\n",
    }
    for label, text in cases.items():
        path = _write(text)
        raised = False
        try:
            B.load_battery(path)
        except ValueError:
            raised = True
        finally:
            os.unlink(path)
        _check(raised, f"malformed battery ({label}) raises ValueError")


# ---------------------------------------------------------------------------
# 3. Per-task fractions over valid runs; env-blocked/failed excluded.
# ---------------------------------------------------------------------------
def test_task_result_excludes_noise() -> None:
    print("test_task_result_excludes_noise")
    bat = Battery(id="t", description="", tasks=[BatteryTask("t1", "digital_service", "do x")])
    runs = {
        "t1": [
            _run(found_product=True, understood_pricing=True),   # valid
            _run(found_product=True),                            # valid
            _env_blocked_run(),                                  # excluded
            _failed_run(),                                       # excluded
        ]
    }
    summ = B.aggregate_battery(bat, runs)
    tr = summ.per_task[0]
    _check(tr.attempted_runs == 4, "attempted counts every run")
    _check(tr.valid_runs == 2, f"only 2 valid runs counted, got {tr.valid_runs}")
    _check(tr.checkpoint_fractions["found_product"] == 1.0, "found_product 2/2 -> 1.0")
    _check(tr.checkpoint_fractions["understood_pricing"] == 0.5, "understood_pricing 1/2 -> 0.5")
    _check(tr.checkpoint_fractions["no_human_gate"] == 0.0, "no_human_gate 0/2 -> 0.0")
    # mean_completion = mean(1.0, 0.5, 0, 0, 0) = 0.3
    _check(abs(tr.mean_completion - 0.3) < 1e-9, f"mean_completion 0.3, got {tr.mean_completion}")


# ---------------------------------------------------------------------------
# 4. No valid run -> no signal, excluded from cross-task stats.
# ---------------------------------------------------------------------------
def test_no_signal_task() -> None:
    print("test_no_signal_task")
    bat = Battery(id="t", description="", tasks=[
        BatteryTask("t1", "digital_service", "do x"),
        BatteryTask("t2", "physical_good", "buy y"),
    ])
    runs = {
        "t1": [_run(found_product=True), _run(found_product=True)],  # signal
        "t2": [_env_blocked_run(), _failed_run()],                   # no signal
    }
    summ = B.aggregate_battery(bat, runs)
    _check(summ.tasks_with_signal == 1, f"one task has signal, got {summ.tasks_with_signal}")
    t2 = next(tr for tr in summ.per_task if tr.task_id == "t2")
    _check(not t2.has_signal, "t2 flagged no-signal")
    _check(t2.checkpoint_fractions["found_product"] is None, "no-signal task fractions are None")
    _check(t2.mean_completion is None, "no-signal task mean_completion None")
    # Cross-task stats computed over the ONE signal task -> spread 0.
    _check(summ.checkpoint_mean["found_product"] == 1.0, "mean over signal tasks only")
    _check(summ.cross_task_spread == 0.0, "single signal task -> spread 0.0, not crash")


# ---------------------------------------------------------------------------
# 5. Cross-task spread IS the reliability signal.
# ---------------------------------------------------------------------------
def test_cross_task_spread() -> None:
    print("test_cross_task_spread")
    bat = Battery(id="t", description="", tasks=[
        BatteryTask("t1", "digital_service", "a"),
        BatteryTask("t2", "physical_good", "b"),
    ])
    # found_product: fully reliable (1.0 both). no_human_gate: intent-dependent
    # (1.0 vs 0.0). Everything else 0 in both.
    runs = {
        "t1": [_run(found_product=True, no_human_gate=True),
               _run(found_product=True, no_human_gate=True)],
        "t2": [_run(found_product=True, no_human_gate=False),
               _run(found_product=True, no_human_gate=False)],
    }
    summ = B.aggregate_battery(bat, runs)
    _check(summ.checkpoint_spread["found_product"] == 0.0,
           "found_product identical across intents -> spread 0")
    _check(abs(summ.checkpoint_spread["no_human_gate"] - 0.5) < 1e-9,
           f"no_human_gate 1.0 vs 0.0 -> pstdev 0.5, got {summ.checkpoint_spread['no_human_gate']}")
    _check(summ.checkpoint_mean["no_human_gate"] == 0.5, "no_human_gate mean 0.5")
    # cross_task_spread = mean of per-checkpoint spreads = (0+0+0+0+0.5)/5 = 0.1
    _check(abs(summ.cross_task_spread - 0.1) < 1e-9,
           f"cross_task_spread 0.1, got {summ.cross_task_spread}")


# ---------------------------------------------------------------------------
# 6. Missing task in runs map -> attempted 0, no signal (no crash).
# ---------------------------------------------------------------------------
def test_missing_task_runs() -> None:
    print("test_missing_task_runs")
    bat = Battery(id="t", description="", tasks=[BatteryTask("t1", "k", "x")])
    summ = B.aggregate_battery(bat, {})  # no runs provided at all
    tr = summ.per_task[0]
    _check(tr.attempted_runs == 0 and tr.valid_runs == 0, "missing task -> 0/0")
    _check(summ.tasks_with_signal == 0, "no signal anywhere")
    _check(summ.cross_task_spread is None, "no signal -> cross_task_spread None")


def main() -> int:
    tests = [
        test_load_default_battery,
        test_malformed_batteries_raise,
        test_task_result_excludes_noise,
        test_no_signal_task,
        test_cross_task_spread,
        test_missing_task_runs,
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
