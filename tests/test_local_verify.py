"""Runner-robustness test for the local verify floor (infra self-healing).

Runnable directly, no pytest required:

    python tests/test_local_verify.py

The launchd verify runner fires a missed :41 job on machine WAKE, before
WiFi/DNS is up, so `git pull` fails instantly with 'Could not resolve host'.
The runner used to bail on that first miss — the 2026-07-27/28 ~18h "runner
stalled" incident: it fired reliably every wake but raced the network with no
retry, writing git-pull-failed artifacts it also couldn't push. The cloud
mis-diagnosed it as "launchd not firing"; the heartbeat log proved otherwise.

`git_pull_with_retry` adds a bounded wait-for-network retry to the pull verb.
This pins that behavior with injected fakes — no network, no real sleeping.
The runner is fixed-verb (pull, test, score, push); this only hardens `pull`.
"""
from __future__ import annotations

import importlib.util
import os
import sys

_RUNNER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "loop", "local_verify.py"
)
_spec = importlib.util.spec_from_file_location("asrs_local_verify", _RUNNER)
lv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lv)  # __name__ != "__main__" -> main() does not run


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def test_success_on_first_attempt_never_sleeps() -> None:
    """Network already up (the common case): one pull, zero waiting."""
    slept: list[int] = []
    rc, tail, tries = lv.git_pull_with_retry(
        pull=lambda: (0, "Already up to date."), attempts=5, delay=15, sleep=slept.append)
    _check(rc == 0, f"network up => rc 0, got {rc}")
    _check(tries == 1, f"succeeds on the first attempt, got {tries}")
    _check(slept == [], f"no wait when the network is already up, got {slept}")


def test_transient_wake_race_recovers() -> None:
    """The bug's exact shape: first 2 pulls fail on a cold network, then it comes up."""
    calls = {"n": 0}

    def pull() -> tuple[int, str]:
        calls["n"] += 1
        if calls["n"] <= 2:
            return 128, "fatal: unable to access ... Could not resolve host: github.com"
        return 0, "Fast-forward"

    slept: list[int] = []
    rc, tail, tries = lv.git_pull_with_retry(pull=pull, attempts=5, delay=15, sleep=slept.append)
    _check(rc == 0, f"recovers once the network associates, rc {rc}")
    _check(tries == 3, f"succeeds on attempt 3 (2 misses + 1), got {tries}")
    _check(slept == [15, 15], f"waited between the 2 failed attempts only, got {slept}")


def test_persistent_failure_bails_after_budget() -> None:
    """Network genuinely down: give up after the budget, no infinite loop, tail preserved."""
    slept: list[int] = []
    rc, tail, tries = lv.git_pull_with_retry(
        pull=lambda: (128, "Could not resolve host: github.com"),
        attempts=4, delay=15, sleep=slept.append)
    _check(rc != 0, f"gives up with the failure rc, got {rc}")
    _check(tries == 4, f"tried the full budget, got {tries}")
    _check(len(slept) == 3, f"slept between attempts but not after the last, got {len(slept)}")
    _check("Could not resolve host" in tail, "surfaces the underlying failure tail")


def test_default_pull_stays_ff_only() -> None:
    """The retry hardens pull WITHOUT changing what it does — still ff-only origin main."""
    seen: dict = {}
    orig = lv.run

    def fake_run(cmd, timeout: int = 600) -> tuple[int, str]:
        seen["cmd"] = cmd
        return 0, "ok"

    lv.run = fake_run
    try:
        rc, tail = lv._pull_once()
    finally:
        lv.run = orig
    _check(seen["cmd"] == ["git", "pull", "--ff-only", "origin", "main"],
           f"_pull_once is a fast-forward-only pull of origin main, got {seen['cmd']}")
    _check(rc == 0, "returns the underlying pull result")


def test_is_diverged_distinguishes_divergence_from_network_failure() -> None:
    """The self-heal must fire on a DIVERGED tree, never on a transient network
    failure (that path is git_pull_with_retry's, not ours)."""
    # The exact tail the 2026-08 stranding wrote to every verify_*.json:
    _check(lv._is_diverged("Not possible to fast-forward, aborting."),
           "recognizes the --ff-only divergence abort")
    _check(lv._is_diverged("hint: Diverging branches can't be fast-forwarded"),
           "recognizes the diverging-branches hint")
    _check(not lv._is_diverged("Could not resolve host: github.com"),
           "a network failure is NOT a divergence")
    _check(not lv._is_diverged("Already up to date."),
           "a clean pull is NOT a divergence")


def test_recovers_only_from_our_own_heartbeat_divergence() -> None:
    """The common case: a prior fire's heartbeat push lost the race with the
    cloud. Every un-pushed commit is one of ours -> discard + realign."""
    calls = {"fetch": 0, "reset": 0}

    def fetch() -> tuple[int, str]:
        calls["fetch"] += 1
        return 0, ""

    def ahead() -> list[str]:
        return ["loop: local verification 20260804T170000Z"]

    def reset() -> tuple[int, str]:
        calls["reset"] += 1
        return 0, ""

    recovered, note = lv.recover_from_own_divergence(fetch=fetch, ahead=ahead, reset=reset)
    _check(recovered, f"recovers from our own un-pushed heartbeat, note={note!r}")
    _check(calls["fetch"] == 1, "fetched origin before inspecting the divergence")
    _check(calls["reset"] == 1, "reset --hard origin/main exactly once")


def test_preserves_unpushed_non_heartbeat_commit() -> None:
    """Safety guard: if ANY un-pushed commit is not our heartbeat, discard
    NOTHING — real work is never lost to the self-heal."""
    calls = {"reset": 0}

    def reset() -> tuple[int, str]:
        calls["reset"] += 1
        return 0, ""

    recovered, note = lv.recover_from_own_divergence(
        fetch=lambda: (0, ""),
        ahead=lambda: ["loop: local verification 20260804T170000Z", "fix: real work"],
        reset=reset,
    )
    _check(not recovered, "does NOT recover when a non-heartbeat commit is ahead")
    _check(calls["reset"] == 0, "never resets when real work would be lost")
    _check("preserving" in note, f"note explains the preservation, got {note!r}")


def test_no_recovery_when_divergence_is_not_ours() -> None:
    """Nothing ahead of origin (e.g. origin rewound, or a non-ours state): do
    not reset on a guess."""
    calls = {"reset": 0}
    recovered, note = lv.recover_from_own_divergence(
        fetch=lambda: (0, ""),
        ahead=lambda: [],
        reset=lambda: (calls.__setitem__("reset", calls["reset"] + 1), (0, ""))[1],
    )
    _check(not recovered, "no recovery when we are not ahead of origin")
    _check(calls["reset"] == 0, "never resets when the divergence is not our commits")


def main() -> int:
    tests = [
        test_success_on_first_attempt_never_sleeps,
        test_transient_wake_race_recovers,
        test_persistent_failure_bails_after_budget,
        test_default_pull_stays_ff_only,
        test_is_diverged_distinguishes_divergence_from_network_failure,
        test_recovers_only_from_our_own_heartbeat_divergence,
        test_preserves_unpushed_non_heartbeat_commit,
        test_no_recovery_when_divergence_is_not_ours,
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
