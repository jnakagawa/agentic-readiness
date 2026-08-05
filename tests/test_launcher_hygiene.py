"""Launcher watchdog guard (loop-infrastructure self-healing).

Runnable directly, no pytest required:

    python tests/test_launcher_hygiene.py

The local loop is driven by `loop/asrs_local_cycle.sh` (pinned on the operator
machine at ~/.local/bin/asrs_local_cycle.sh, launchd :41). It runs the verify
FLOOR (`local_verify.py`) and THEN a `claude -p` agent cycle. Cycle 261
root-caused a ~15h stall to that launcher: launchd `StartCalendarInterval` is
NON-REENTRANT — while a previous instance is still alive it SKIPS every
subsequent :41 firing. The 02:41Z agent stayed alive (suspended through an
overnight system sleep), so it wedged the launcher for ~15h and blocked 14
verify slots. The fix backgrounds the agent and bounds its AWAKE runtime with a
wall-clock watchdog (`ASRS_AGENT_TIMEOUT`, default 45min) that kills a hung
instance, so the launcher can never again wedge launchd.

That fix is load-bearing for the whole local loop but nothing pinned it: a
future edit that reverts to a bare synchronous `claude -p` (drops the `&` /
watchdog), or moves the floor AFTER the agent, would silently re-open the wedge.
This guard closes that hole. It asserts, against the repo launcher:

  * the verify floor runs BEFORE the agent (floor-first — the floor still runs
    even if the watchdog later kills the agent),
  * the agent invocation is BACKGROUNDED (a standalone trailing `&`, not a
    synchronous foreground call),
  * the agent's runtime is WATCHDOG-BOUNDED (an `ASRS_AGENT_TIMEOUT`-tunable
    `sleep`+`kill` on the captured agent PID),
  * the script parses clean under `zsh -n` (guarded — skips where zsh absent),
  * [LOCAL] the pinned ~/.local/bin copy is byte-identical to the repo copy
    (self-heal-law sync, the `local_verify.py` precedent; skips off-machine).

These are infrastructure hygiene invariants, not scoring semantics — the rubric
version, probes, and the canonical delta are untouched. The semantic detectors
are proven on a synthetic REGRESSED launcher so the guard cannot vacuously pass.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LAUNCHER = os.path.join(_REPO, "loop", "asrs_local_cycle.sh")
_PINNED = os.path.expanduser("~/.local/bin/asrs_local_cycle.sh")

# The agent invocation: a `claude`/`$CLAUDE_BIN` command carrying the `-p`
# prompt flag (the long-running step the watchdog must bound). Excludes the
# `command -v claude` discovery line (no ` -p `).
_AGENT_RE = re.compile(r"\s-p\s")
# A standalone trailing `&` (backgrounding) — NOT the `&` inside `2>&1`, which
# is preceded by `>` and not at end-of-line.
_BACKGROUND_RE = re.compile(r"(?:^|\s)&\s*$")


def _read(path: str = _LAUNCHER) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _is_agent_line(line: str) -> bool:
    return bool(_AGENT_RE.search(line)) and (
        "CLAUDE_BIN" in line or "claude" in line.lower()
    )


def _agent_line(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        if _is_agent_line(line):
            return line
    return None


def _floor_before_agent(text: str) -> bool:
    """The verify floor (`local_verify.py`) is invoked before the agent."""
    floor_i = agent_i = None
    for i, line in enumerate(text.splitlines()):
        if line.strip().startswith("#"):
            continue
        if floor_i is None and "local_verify.py" in line:
            floor_i = i
        if agent_i is None and _is_agent_line(line):
            agent_i = i
    return floor_i is not None and agent_i is not None and floor_i < agent_i


def _agent_is_backgrounded(text: str) -> bool:
    line = _agent_line(text)
    return bool(line) and bool(_BACKGROUND_RE.search(line.rstrip()))


def _is_watchdog_bounded(text: str) -> bool:
    """An `ASRS_AGENT_TIMEOUT`-tunable sleep+kill on the captured agent PID."""
    return (
        "ASRS_AGENT_TIMEOUT" in text
        and re.search(r"AGENT_PID=\$!", text) is not None
        and re.search(r'sleep\s+"?\$\{?AGENT_TIMEOUT', text) is not None
        and re.search(r"kill\b[^\n]*\bAGENT_PID\b", text) is not None
    )


def test_launcher_exists_and_nonempty():
    assert os.path.exists(_LAUNCHER), "loop/asrs_local_cycle.sh is missing"
    assert os.path.getsize(_LAUNCHER) > 0, "loop/asrs_local_cycle.sh is empty"
    print("  ok: loop/asrs_local_cycle.sh exists and is non-empty")


def test_floor_runs_before_agent():
    # Floor-first: even if the watchdog later kills the agent, the verify floor
    # for this hour has already run, so no floor coverage is ever lost.
    assert _floor_before_agent(_read()), (
        "the verify floor (local_verify.py) must be invoked BEFORE the agent in "
        "loop/asrs_local_cycle.sh — moving it after would let a bounded/killed "
        "agent skip the floor."
    )
    print("  ok: the verify floor runs before the agent (floor-first)")


def test_agent_is_backgrounded():
    # A synchronous foreground `claude -p` is what wedged launchd for ~15h
    # (Cycle 261); the agent must be backgrounded so the watchdog can bound it.
    assert _agent_is_backgrounded(_read()), (
        "the `claude -p` agent invocation must be BACKGROUNDED (trailing `&`) so "
        "the launcher does not block on it — a synchronous call re-opens the "
        "non-reentrant launchd wedge (Cycle 261)."
    )
    print("  ok: the agent invocation is backgrounded")


def test_agent_runtime_is_watchdog_bounded():
    # The watchdog is the actual wedge-preventer: it kills the captured agent
    # PID after ASRS_AGENT_TIMEOUT seconds of awake runtime.
    assert _is_watchdog_bounded(_read()), (
        "the agent must be bounded by a watchdog: an ASRS_AGENT_TIMEOUT-tunable "
        "`sleep`+`kill` on the captured $AGENT_PID. Its absence re-opens the "
        "~15h non-reentrant wedge (Cycle 261)."
    )
    print("  ok: the agent's awake runtime is watchdog-bounded (ASRS_AGENT_TIMEOUT)")


def test_launcher_parses_clean():
    # Syntax breakage would fail every fire silently (launchd swallows the error).
    zsh = shutil.which("zsh")
    if not zsh:
        print("  skip: zsh not on PATH (syntax check unavailable in this env)")
        return
    proc = subprocess.run(
        [zsh, "-n", _LAUNCHER], capture_output=True, text=True
    )
    assert proc.returncode == 0, (
        f"`zsh -n` rejected loop/asrs_local_cycle.sh: {proc.stderr.strip()}"
    )
    print("  ok: launcher parses clean under `zsh -n`")


def test_pinned_launcher_matches_repo():
    # [LOCAL] leg (c): the pinned copy launchd actually runs must match the
    # reviewed repo copy (self-heal law — the local_verify.py precedent). Skips
    # off the operator machine (in-cloud, the pinned copy does not exist).
    if not os.path.exists(_PINNED):
        print(
            "  skip: pinned ~/.local/bin/asrs_local_cycle.sh absent "
            "(in-cloud / non-operator env)"
        )
        return
    with open(_PINNED, "rb") as fh:
        pinned = fh.read()
    with open(_LAUNCHER, "rb") as fh:
        repo = fh.read()
    assert pinned == repo, (
        "pinned ~/.local/bin/asrs_local_cycle.sh differs from "
        "loop/asrs_local_cycle.sh; resync per the self-heal law (the "
        "local_verify.py precedent) so launchd runs the reviewed copy."
    )
    print("  ok: pinned launcher is byte-identical to the repo copy (leg c)")


def test_guards_have_teeth():
    # Non-vacuous: prove the semantic detectors flag a REGRESSED launcher (the
    # Cycle-261 wedge shape) and do NOT false-positive on the real one.
    regressed = (
        "#!/bin/zsh\n"
        'cd "$REPO" || exit 1\n'
        '"$PY" "$HOME/.local/bin/asrs_local_verify.py"\n'
        '"$CLAUDE_BIN" -p "run one cycle" --max-turns 120\n'  # synchronous, unbounded
    )
    assert not _agent_is_backgrounded(regressed), (
        "detector should flag a synchronous (non-backgrounded) agent"
    )
    assert not _is_watchdog_bounded(regressed), (
        "detector should flag an unbounded agent (no watchdog)"
    )
    print("  ok: detectors flag a synchronous, unbounded agent (has teeth)")

    floor_last = (
        "#!/bin/zsh\n"
        '"$CLAUDE_BIN" -p "run one cycle" &\n'
        "AGENT_PID=$!\n"
        '"$PY" local_verify.py\n'  # floor AFTER the agent
    )
    assert not _floor_before_agent(floor_last), (
        "detector should flag a floor that runs after the agent"
    )
    print("  ok: detector flags a floor-after-agent ordering (has teeth)")

    # And the real launcher passes all three semantic guards (no false positive).
    real = _read()
    assert _floor_before_agent(real)
    assert _agent_is_backgrounded(real)
    assert _is_watchdog_bounded(real)
    print("  ok: the real launcher passes all three semantic guards (no false positive)")


def main() -> int:
    tests = [
        test_launcher_exists_and_nonempty,
        test_floor_runs_before_agent,
        test_agent_is_backgrounded,
        test_agent_runtime_is_watchdog_bounded,
        test_launcher_parses_clean,
        test_pinned_launcher_matches_repo,
        test_guards_have_teeth,
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
