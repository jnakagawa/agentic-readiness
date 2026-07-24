"""Tests that the nested claude panels run HERMETIC — no operator MCP fleet.

Runnable directly, no pytest required:

    python tests/test_shopper_hermetic.py

Both behavioral panels spawn a headless ``claude -p`` subprocess
(:func:`asrs.behavioral.shopper._claude_cmd` for the shopper,
:func:`asrs.behavioral.trust_probe._claude_cmd` for the trust probe). By
default ``claude -p`` inherits the operator's filesystem MCP configuration, so
each subprocess was observed booting the machine's full MCP fleet
(trigger.dev / mcp-for-unity / linear / motherduck / ...) BEFORE it browsed —
~1 min of pure MCP startup PER PANEL and, worse, unrelated external
connections pulled into the measurement environment. That is a measurement-
validity problem: the shopper should measure the *storefront*, in a clean
environment, not the operator's incidental MCP setup.

The fix is ``--strict-mcp-config`` (claude: "Only use MCP servers from
--mcp-config, ignoring all other MCP configurations"). Passed WITHOUT any
``--mcp-config``, it yields ZERO MCP servers — a hermetic panel. The shopper
needs only ``WebFetch``/``WebSearch`` (its ``--allowedTools``), so nothing of
value is lost.

These are pure command-construction assertions — no subprocess, no CLI, no
network. They pin the flag so a future edit can't silently drop it and let the
fleet back in. Non-vacuous: the pre-fix builders (no ``--strict-mcp-config``)
fail every ``_carries_strict`` assertion below.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.behavioral import shopper as SH  # noqa: E402
from asrs.behavioral import trust_probe as TP  # noqa: E402


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _adjacent(cmd: list[str], a: str, b: str) -> bool:
    """True if flag ``a`` is immediately followed by value ``b`` in ``cmd``."""
    return any(cmd[i] == a and cmd[i + 1] == b for i in range(len(cmd) - 1))


def test_shopper_panel_is_hermetic() -> None:
    cmd = SH._claude_cmd("browse example.com and buy a widget")
    _check("--strict-mcp-config" in cmd,
           "shopper claude cmd carries --strict-mcp-config (no operator MCP fleet)")
    # strict + NO --mcp-config == zero MCP servers. If a future edit adds an
    # --mcp-config it must be a deliberate, reviewed choice, not the fleet.
    _check("--mcp-config" not in cmd,
           "shopper claude cmd loads no --mcp-config, so strict == empty fleet")


def test_trust_panel_is_hermetic() -> None:
    cmd = TP._claude_cmd("would you complete this purchase?")
    _check("--strict-mcp-config" in cmd,
           "trust-probe claude cmd carries --strict-mcp-config (no operator MCP fleet)")
    _check("--mcp-config" not in cmd,
           "trust-probe claude cmd loads no --mcp-config, so strict == empty fleet")


def test_shopper_still_headless_json_and_browse_only() -> None:
    """The hermetic change must not disturb the rest of the panel contract."""
    cmd = SH._claude_cmd("PROMPT")
    _check(cmd[0] == "claude" and "-p" in cmd, "shopper still runs `claude -p`")
    _check("PROMPT" in cmd, "the shopper prompt is still passed through")
    _check(_adjacent(cmd, "--output-format", "json"),
           "shopper still requests --output-format json (verdict is parseable)")
    _check(_adjacent(cmd, "--model", SH.CLAUDE_MODEL),
           f"shopper still pins --model {SH.CLAUDE_MODEL}")
    # The shopper's only capabilities are web reconnaissance — no MCP tools.
    _check("--allowedTools" in cmd and "WebFetch" in cmd and "WebSearch" in cmd,
           "shopper still restricts tools to WebFetch/WebSearch")


def test_trust_probe_still_headless_json() -> None:
    cmd = TP._claude_cmd("PROMPT")
    _check(cmd[0] == "claude" and "-p" in cmd, "trust probe still runs `claude -p`")
    _check("PROMPT" in cmd, "the trust-probe prompt is still passed through")
    _check(_adjacent(cmd, "--output-format", "json"),
           "trust probe still requests --output-format json")
    _check(_adjacent(cmd, "--model", TP.CLAUDE_MODEL),
           f"trust probe still pins --model {TP.CLAUDE_MODEL}")


def main() -> int:
    tests = [
        test_shopper_panel_is_hermetic,
        test_trust_panel_is_hermetic,
        test_shopper_still_headless_json_and_browse_only,
        test_trust_probe_still_headless_json,
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
