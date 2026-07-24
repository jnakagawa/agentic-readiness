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
from asrs.offering import ArchetypeClaim, OfferingProfile  # noqa: E402
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
# 3. --battery in static mode is a no-op (warn + (None, None)), not a failure.
#    A YAML path in behavioral mode resolves to (battery, None) — no profile, so
#    the aggregation stays byte-for-byte pre-brick-3 (nothing marked NA).
# ---------------------------------------------------------------------------
def test_static_mode_battery_noop() -> None:
    print("test_static_mode_battery_noop")

    default_path = str(
        __import__("asrs.battery", fromlist=["DEFAULT_BATTERY_PATH"]).DEFAULT_BATTERY_PATH
    )

    class _Args:
        battery = default_path
        behavioral = False

    bat, prof = cli._resolve_battery(_Args(), _FakeCtx())
    _check(bat is None and prof is None, "static-mode --battery returns (None, None) (no-op)")

    class _Args2:
        battery = None
        behavioral = True

    _check(cli._resolve_battery(_Args2(), _FakeCtx()) == (None, None), "no --battery -> (None, None)")

    class _Args3:
        battery = default_path
        behavioral = True

    bat3, prof3 = cli._resolve_battery(_Args3(), _FakeCtx())
    _check(bat3 is not None and bat3.tasks, "YAML path in behavioral mode loads a battery")
    _check(prof3 is None, "a static YAML battery carries no offering profile (aggregation stays pre-brick-3)")


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


# ---------------------------------------------------------------------------
# 5. --battery auto: discovery -> offering-relative battery (+ profile).
#    Wires discover_offering -> instantiate_battery: one task per CLAIMED
#    archetype, in template-bank order, and the profile is threaded back so the
#    aggregation can NA-exclude the unclaimed archetypes (brick 3).
# ---------------------------------------------------------------------------
class _AutoCtx:
    domain = "shop.example"


def _patch_discovery(profile):
    """Monkeypatch asrs.offering.discover_offering to return ``profile``.

    ``_resolve_battery`` does ``from .offering import discover_offering`` per
    call, so patching the module attribute is picked up. Returns a restore().
    """
    import asrs.offering as off

    orig = off.discover_offering
    off.discover_offering = lambda ctx: profile
    return lambda: setattr(off, "discover_offering", orig)


def _image_api_profile() -> OfferingProfile:
    # A discovered image API: claims metered_api + digital_good, nothing else.
    return OfferingProfile(
        domain="shop.example",
        claimed=[ArchetypeClaim(archetype="metered_api"),
                 ArchetypeClaim(archetype="digital_good")],
    )


def test_battery_auto_discovers_offering_relative() -> None:
    print("test_battery_auto_discovers_offering_relative")
    profile = _image_api_profile()
    restore = _patch_discovery(profile)
    try:
        class _Args:
            battery = "auto"
            behavioral = True

        battery, prof = cli._resolve_battery(_Args(), _AutoCtx())
    finally:
        restore()
    kinds = [t.kind for t in battery.tasks]
    _check(kinds == ["metered_api", "digital_good"],
           f"one task per claimed archetype, template-bank order, got {kinds}")
    _check(all(t.intent for t in battery.tasks), "each generated task carries a non-empty intent")
    _check(prof is profile, "the discovered profile is threaded back for NA-aware aggregation")
    _check("physical_good" in prof.unclaimed,
           "unclaimed archetypes (e.g. physical_good) available to mark NA")


# ---------------------------------------------------------------------------
# 6. --battery auto end-to-end: the profile threads into aggregate_battery, so a
#    site that does not claim physical_good never gets a physical-good task AND
#    the summary records the unclaimed archetypes NA (operator directive: the
#    battery measures readiness for what a site OFFERS, not its mismatch).
# ---------------------------------------------------------------------------
def test_battery_auto_threads_na_into_summary() -> None:
    print("test_battery_auto_threads_na_into_summary")
    profile = _image_api_profile()
    restore = _patch_discovery(profile)
    try:
        class _Args:
            battery = "auto"
            behavioral = True

        battery, prof = cli._resolve_battery(_Args(), _AutoCtx())
        with _Recorder() as rec:
            checks, verdicts, runs, summary = cli._run_behavioral(
                "shop.example", _FakeCtx(), "IGNORED", trials=1,
                models=["claude"], battery=battery, profile=prof,
            )
    finally:
        restore()
    # Only the claimed archetypes ran as tasks — no mismatched intent to score.
    _check(rec.shopper_tasks == [t.intent for t in battery.tasks],
           "shopper ran once per claimed-archetype intent")
    _check("physical_good" not in [t.kind for t in battery.tasks],
           "no physical-good task for a site that does not claim it")
    # ...and the summary marks every unclaimed archetype NA (brick 3 end-to-end).
    _check(summary is not None, "battery_summary attached")
    _check("physical_good" in summary["na_archetypes"],
           f"unclaimed physical_good recorded NA, got {summary['na_archetypes']}")
    _check(set(summary["assessed_archetypes"]) <= {"metered_api", "digital_good"},
           f"assessed names claimed archetypes only, got {summary['assessed_archetypes']}")
    _check(summary["battery_semantics_version"] == "b1",
           "offering-relative aggregation stamps battery_semantics_version b1")


# ---------------------------------------------------------------------------
# 7. --battery auto with a null offering: empty battery + profile, not a crash.
#    A site that claims nothing yields zero tasks; the profile still records
#    every archetype as unclaimed so the run is honest ("nothing to assess"),
#    never a fabricated task.
# ---------------------------------------------------------------------------
def test_battery_auto_empty_offering() -> None:
    print("test_battery_auto_empty_offering")
    profile = OfferingProfile(domain="bare.example", claimed=[])
    restore = _patch_discovery(profile)
    try:
        class _Args:
            battery = "auto"
            behavioral = True

        battery, prof = cli._resolve_battery(_Args(), _AutoCtx())
    finally:
        restore()
    _check(battery is not None and battery.tasks == [],
           "null offering -> empty battery (no fabricated tasks)")
    _check(prof is profile and len(prof.unclaimed) > 0,
           "profile still threaded so the summary can record every archetype NA")


def main() -> int:
    tests = [
        test_battery_runs_panel_per_task,
        test_no_battery_single_panel,
        test_static_mode_battery_noop,
        test_render_includes_battery_section,
        test_battery_auto_discovers_offering_relative,
        test_battery_auto_threads_na_into_summary,
        test_battery_auto_empty_offering,
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
