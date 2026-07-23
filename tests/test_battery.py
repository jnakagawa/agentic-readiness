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
    # Only one archetype (digital_service) produced signal -> between-kind
    # spread is unobservable -> None (not a measured-uniform 0.0).
    _check(summ.between_kind_spread is None,
           "single signal archetype -> between_kind_spread None (unobservable)")


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


# ---------------------------------------------------------------------------
# 7. Per-archetype (kind) rollup: same run, read one storefront type at a time.
# ---------------------------------------------------------------------------
def test_per_kind_rollup() -> None:
    print("test_per_kind_rollup")
    # Two digital_service intents (one perfectly reliable, one intent-dependent)
    # and one physical_good intent — the classic "strong on X, weak on Y" split.
    bat = Battery(id="t", description="", tasks=[
        BatteryTask("t1", "digital_service", "a"),
        BatteryTask("t2", "digital_service", "b"),
        BatteryTask("t3", "physical_good", "c"),
    ])
    runs = {
        # t1: found_product + no_human_gate both 1.0 -> mean_completion 0.4
        "t1": [_run(found_product=True, no_human_gate=True),
               _run(found_product=True, no_human_gate=True)],
        # t2: found_product 1.0 only -> mean_completion 0.2
        "t2": [_run(found_product=True), _run(found_product=True)],
        # t3: nothing reached -> mean_completion 0.0
        "t3": [_run(), _run()],
    }
    summ = B.aggregate_battery(bat, runs)
    pk = {kr.kind: kr for kr in summ.per_kind}
    _check(set(pk) == {"digital_service", "physical_good"}, f"two archetypes, got {sorted(pk)}")
    # Insertion order preserved (digital_service first appears before physical_good).
    _check([kr.kind for kr in summ.per_kind] == ["digital_service", "physical_good"],
           "per_kind ordered by first appearance")

    ds = pk["digital_service"]
    _check(ds.n_tasks == 2 and ds.tasks_with_signal == 2, "digital_service: 2/2 signal")
    # mean_completion = mean(0.4, 0.2) = 0.3
    _check(abs(ds.mean_completion - 0.3) < 1e-9, f"digital_service mean_completion 0.3, got {ds.mean_completion}")
    # Within-kind spread: no_human_gate differs (1.0 vs 0.0) -> pstdev 0.5;
    # found_product identical (1.0 vs 1.0) -> 0; others 0. mean over 5 keys = 0.1.
    _check(abs(ds.cross_task_spread - 0.1) < 1e-9,
           f"digital_service within-kind spread 0.1, got {ds.cross_task_spread}")

    pg = pk["physical_good"]
    _check(pg.n_tasks == 1 and pg.tasks_with_signal == 1, "physical_good: 1/1 signal")
    _check(pg.mean_completion == 0.0, f"physical_good mean_completion 0.0, got {pg.mean_completion}")
    # A single signal task in the archetype -> spread 0.0 (no variance yet), not None/crash.
    _check(pg.cross_task_spread == 0.0, f"single-task kind spread 0.0, got {pg.cross_task_spread}")

    # Between-archetype spread decomposes storefront-TYPE specialization:
    # per-kind completions are digital_service 0.3 vs physical_good 0.0 ->
    # pstdev([0.3, 0.0]) = 0.15 (mean 0.15, each 0.15 off).
    _check(abs(summ.between_kind_spread - 0.15) < 1e-9,
           f"between_kind_spread over 0.3/0.0 archetypes -> 0.15, got {summ.between_kind_spread}")


# ---------------------------------------------------------------------------
# 8. A kind whose only intents had no valid run is reported, never a failure.
# ---------------------------------------------------------------------------
def test_per_kind_no_signal() -> None:
    print("test_per_kind_no_signal")
    bat = Battery(id="t", description="", tasks=[
        BatteryTask("t1", "digital_service", "a"),
        BatteryTask("t2", "physical_good", "b"),
    ])
    runs = {
        "t1": [_run(found_product=True), _run(found_product=True)],  # signal
        "t2": [_env_blocked_run(), _failed_run()],                   # no signal
    }
    summ = B.aggregate_battery(bat, runs)
    pk = {kr.kind: kr for kr in summ.per_kind}
    _check(set(pk) == {"digital_service", "physical_good"},
           "both archetypes present even when one has no signal")
    pg = pk["physical_good"]
    _check(pg.n_tasks == 1 and pg.tasks_with_signal == 0, "physical_good: 0/1 signal")
    _check(pg.mean_completion is None, "no-signal kind mean_completion None")
    _check(pg.cross_task_spread is None, "no-signal kind cross_task_spread None (not 0.0)")
    # Serialization carries per_kind (JSON Report surfacing).
    _check(any(k.get("kind") == "physical_good" for k in summ.to_dict()["per_kind"]),
           "per_kind survives to_dict()")


# ---------------------------------------------------------------------------
# 9. Between-archetype spread: the storefront-type specialization signal.
# ---------------------------------------------------------------------------
def test_between_kind_spread() -> None:
    print("test_between_kind_spread")
    # Three archetypes with DIFFERENT completion levels — a type-specialized
    # site (aces digital, so-so on data, misses physical).
    bat = Battery(id="t", description="", tasks=[
        BatteryTask("t1", "digital_service", "a"),
        BatteryTask("t2", "data_job", "b"),
        BatteryTask("t3", "physical_good", "c"),
    ])
    runs = {
        # digital_service: all 5 checkpoints -> mean_completion 1.0
        "t1": [_run(**{k: True for k in _KEYS}), _run(**{k: True for k in _KEYS})],
        # data_job: found_product + understood_pricing -> mean_completion 0.4
        "t2": [_run(found_product=True, understood_pricing=True),
               _run(found_product=True, understood_pricing=True)],
        # physical_good: nothing reached -> mean_completion 0.0
        "t3": [_run(), _run()],
    }
    summ = B.aggregate_battery(bat, runs)
    # per-kind completions 1.0 / 0.4 / 0.0 -> pstdev = 0.4 (mean 0.4666..).
    import statistics as _stat
    expected = _stat.pstdev([1.0, 0.4, 0.0])
    _check(abs(summ.between_kind_spread - expected) < 1e-9,
           f"between_kind_spread over 1.0/0.4/0.0 archetypes -> {expected:.4f}, got {summ.between_kind_spread}")
    # Positive and substantial: this site's readiness clearly depends on
    # storefront type (1.0 vs 0.4 vs 0.0 per archetype).
    _check(summ.between_kind_spread > 0.3,
           f"type-specialized site -> sizeable between-archetype spread, got {summ.between_kind_spread}")
    # Serialization carries the new field.
    _check("between_kind_spread" in summ.to_dict(), "between_kind_spread survives to_dict()")

    # No signal anywhere -> None (not 0.0).
    empty = B.aggregate_battery(bat, {})
    _check(empty.between_kind_spread is None, "no signal -> between_kind_spread None")


def main() -> int:
    tests = [
        test_load_default_battery,
        test_malformed_batteries_raise,
        test_task_result_excludes_noise,
        test_no_signal_task,
        test_cross_task_spread,
        test_missing_task_runs,
        test_per_kind_rollup,
        test_per_kind_no_signal,
        test_between_kind_spread,
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
