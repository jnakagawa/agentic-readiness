"""Tests for the ``--battery`` pipeline wiring (Cycle 6, COVERAGE).

Runnable directly, no pytest required:

    python tests/test_battery_wiring.py

The battery *math* is covered by tests/test_battery.py. This file covers the
CLI/pipeline WIRING that feeds that math, with a SYNTHETIC shopper panel
(monkeypatched — no network, no claude/codex CLIs). The load-bearing
invariants a battery run must honour:

  - the shopper panel runs ONCE PER battery task (each task's intent);
  - the FIRST task is the primary scoring run (``runs`` returned to scoring is
    that task's runs, so the score is a single real task panel — unchanged
    semantics, no version bump);
  - the free-tier transaction probe fires AT MOST ONCE for the whole battery
    (invariant #1 — it consumes the target's allowance; the per-task loop must
    never multiply it), and the trust panel runs once;
  - the additive ``battery_summary`` dict is attached and populated;
  - a battery in STATIC mode is a no-op (warn + proceed), not a hard failure;
  - the terminal card renders a TASK BATTERY section when the summary is present.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs import cli  # noqa: E402
from asrs.battery import Battery, BatteryTask  # noqa: E402
from asrs.types import BehavioralRun, Report  # noqa: E402

_KEYS = ["found_product", "understood_pricing", "found_purchase_path",
         "machine_payable_path", "no_human_gate"]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(**cp) -> BehavioralRun:
    checkpoints = {k: bool(cp.get(k, False)) for k in _KEYS}
    return BehavioralRun(model="claude", trial=1, checkpoints=checkpoints)


class _FakeCtx:
    """Enough of FetchContext for _homepage_excerpt: a .homepage() with .text."""

    class _Res:
        text = "<html>hello</html>"

    def homepage(self):
        return self._Res()


class _Recorder:
    """Monkeypatches the three behavioral modules and records how they're called."""

    def __init__(self):
        self.shopper_tasks: list[str] = []
        self.free_tier_calls = 0
        self.trust_calls = 0
        self._orig: dict = {}

    def __enter__(self):
        import asrs.behavioral.shopper as sh
        import asrs.behavioral.trust_probe as tp
        import asrs.behavioral.free_tier as ft

        self._orig = {
            (sh, "run_panel"): sh.run_panel,
            (tp, "run_panel"): tp.run_panel,
            (ft, "run_probe"): ft.run_probe,
        }

        def fake_shopper(domain, task, trials=1, models=("claude",), out_dir="runs"):
            self.shopper_tasks.append(task)
            # Distinct checkpoints per intent so a spread is observable: the
            # "human-gated" intent never clears no_human_gate.
            gate = "gated" not in task
            runs = [_run(found_product=True, no_human_gate=gate)]
            return runs, []  # no aggregated checks needed for wiring assertions

        def fake_trust(domain, excerpt, models=("claude",)):
            self.trust_calls += 1
            return [], []

        def fake_free_tier(ctx, out_dir="runs"):
            self.free_tier_calls += 1
            return []

        sh.run_panel = fake_shopper
        tp.run_panel = fake_trust
        ft.run_probe = fake_free_tier
        return self

    def __exit__(self, *exc):
        for (mod, name), fn in self._orig.items():
            setattr(mod, name, fn)
        return False


def _battery() -> Battery:
    return Battery(id="b", description="", tasks=[
        BatteryTask("buy_digital", "digital_service", "buy the primary product"),
        BatteryTask("subscribe", "subscription", "subscribe to the api (gated)"),
    ])


# ---------------------------------------------------------------------------
# 1. One shopper panel per task; first task is primary; probes fire once.
# ---------------------------------------------------------------------------
def test_battery_runs_panel_per_task() -> None:
    print("test_battery_runs_panel_per_task")
    bat = _battery()
    with _Recorder() as rec:
        checks, verdicts, runs, summary = cli._run_behavioral(
            "example.com", _FakeCtx(), "IGNORED-default-task", trials=1,
            models=["claude"], battery=bat,
        )
    _check(rec.shopper_tasks == ["buy the primary product", "subscribe to the api (gated)"],
           f"shopper ran once per intent, in order: {rec.shopper_tasks}")
    _check(rec.free_tier_calls == 1,
           f"free-tier probe fired exactly once for the whole battery, got {rec.free_tier_calls}")
    _check(rec.trust_calls == 1, f"trust panel ran once, got {rec.trust_calls}")
    # Primary scoring run = FIRST task's runs (no_human_gate True for that intent).
    _check(len(runs) == 1 and runs[0].checkpoints["no_human_gate"] is True,
           "runs returned to scoring are the first task's runs")
    _check(summary is not None and summary["n_tasks"] == 2,
           "battery_summary attached with n_tasks=2")
    _check(summary["tasks_with_signal"] == 2, "both intents produced signal")
    # no_human_gate is intent-dependent (True vs False) -> positive spread.
    _check(summary["cross_task_spread"] > 0.0,
           f"cross_task_spread positive (intent-dependent), got {summary['cross_task_spread']}")


# ---------------------------------------------------------------------------
# 2. No battery -> single panel, no summary (unchanged path).
# ---------------------------------------------------------------------------
def test_no_battery_single_panel() -> None:
    print("test_no_battery_single_panel")
    with _Recorder() as rec:
        checks, verdicts, runs, summary = cli._run_behavioral(
            "example.com", _FakeCtx(), "the one task", trials=1,
            models=["claude"], battery=None,
        )
    _check(rec.shopper_tasks == ["the one task"], "shopper ran once on the given task")
    _check(rec.free_tier_calls == 1, "free-tier probe fired once")
    _check(summary is None, "no battery -> battery_summary is None")


# ---------------------------------------------------------------------------
# 3. --battery in static mode is a no-op (warn + None), not a failure.
# ---------------------------------------------------------------------------
def test_static_mode_battery_noop() -> None:
    print("test_static_mode_battery_noop")

    class _Args:
        battery = str(__import__("asrs.battery", fromlist=["DEFAULT_BATTERY_PATH"]).DEFAULT_BATTERY_PATH)
        behavioral = False

    out = cli._load_battery_arg(_Args())
    _check(out is None, "static-mode --battery returns None (no-op)")

    class _Args2:
        battery = None
        behavioral = True

    _check(cli._load_battery_arg(_Args2()) is None, "no --battery -> None")


# ---------------------------------------------------------------------------
# 4. Terminal card renders a TASK BATTERY section when a summary is present.
# ---------------------------------------------------------------------------
def test_render_includes_battery_section() -> None:
    print("test_render_includes_battery_section")
    from asrs import report as report_mod

    rpt = Report(
        domain="example.com", rubric_version="0.5", generated_at="2026-07-23T00:00:00Z",
        pillar_scores={"access": 100.0}, overall_score=50.0, grade="F",
        battery_summary={
            "battery_id": "b", "n_tasks": 2, "tasks_with_signal": 2,
            "per_task": [
                {"task_id": "buy_digital", "kind": "digital_service",
                 "valid_runs": 1, "mean_completion": 0.4},
                {"task_id": "subscribe", "kind": "subscription",
                 "valid_runs": 0, "mean_completion": None},
            ],
            "cross_task_spread": 0.42,
        },
    )
    text = report_mod.render(rpt)
    _check("TASK BATTERY" in text, "render shows a TASK BATTERY heading")
    _check("buy_digital" in text and "subscribe" in text, "per-task rows rendered")
    _check("no signal" in text, "no-signal intent labelled, not scored as failure")
    _check("intent-dependent" in text, "high spread interpreted for the reader")

    # A report with no battery must not grow a battery section.
    plain = Report(domain="x", rubric_version="0.5", generated_at="t",
                   pillar_scores={"access": 100.0}, overall_score=50.0, grade="F")
    _check("TASK BATTERY" not in report_mod.render(plain),
           "no battery_summary -> no TASK BATTERY section")


def main() -> int:
    tests = [
        test_battery_runs_panel_per_task,
        test_no_battery_single_panel,
        test_static_mode_battery_noop,
        test_render_includes_battery_section,
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
