"""STATE.md readability guard (bookkeeping self-healing).

Runnable directly, no pytest required:

    python tests/test_state_hygiene.py

The playbook mandates that every cycle "read STATE.md" — the cycle counter,
focus pointer, and open questions are how a fresh cloud fire orients before
picking work. STATE is MUTABLE working state, not the append-only history
(that lives in loop/LOG.md + git). But the per-cycle update PREPENDS a CYCLE
entry + FOCUS POINTER every fire, so without pruning STATE monotonically
grows. By Cycle 259 it had accreted the full history back to ~Cycle 5 (7798
lines / ~790KB) and could no longer be Read in a single call — the Read tool
caps a single read at 256KB — silently degrading the mandated per-cycle read.
Cycle 260 compacted it (rolling log trimmed to the last ~5 cycles; stable
reference sections retained) and added this guard so it can never re-balloon
past readability unnoticed: a fire that lets STATE grow too large fails the
suite and MUST prune before it can commit its own work.

These are hygiene thresholds, not scoring semantics — no rubric version is
implicated. Bump the caps here (with a note) only if the loop deliberately
decides STATE should carry more standing context.
"""
from __future__ import annotations

import os
import sys

_STATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "loop", "STATE.md"
)

# Hard ceiling: must stay comfortably under the Read tool's 256KB single-read
# limit so a fresh fire can always `Read` STATE.md in one call.
_MAX_BYTES = 200_000
# Soft early-warning: the rolling cycle log should be pruned to ~5 cycles, so
# STATE lives in the low hundreds of lines. This trips long before the byte
# ceiling, forcing a prune while the file is still trivially readable.
_MAX_LINES = 600

# Stable reference sections a compaction must never drop — losing any of these
# would strip standing context every cycle depends on.
_REQUIRED_MARKERS = (
    "# Loop state",
    "- Cycle counter:",
    "## Environment constraint",
    "## Open questions",
)


def _read():
    with open(_STATE, "r", encoding="utf-8") as fh:
        return fh.read()


def test_state_exists_and_nonempty():
    assert os.path.exists(_STATE), "loop/STATE.md is missing"
    assert os.path.getsize(_STATE) > 0, "loop/STATE.md is empty"


def test_state_stays_readable_in_one_call():
    size = os.path.getsize(_STATE)
    assert size < _MAX_BYTES, (
        f"loop/STATE.md is {size} bytes (>= {_MAX_BYTES}); it is growing past what the "
        "Read tool can load in one call. Prune the rolling cycle log to the last ~5 "
        "cycles (history is preserved in loop/LOG.md + git) before committing."
    )


def test_rolling_cycle_log_is_pruned():
    n = len(_read().splitlines())
    assert n < _MAX_LINES, (
        f"loop/STATE.md is {n} lines (>= {_MAX_LINES}); the rolling cycle log has "
        "accreted. Trim it to the last ~5 cycles per the Cycle-260 compaction policy."
    )


def test_stable_reference_sections_survive():
    text = _read()
    for marker in _REQUIRED_MARKERS:
        assert marker in text, (
            f"loop/STATE.md is missing the stable marker {marker!r}; a compaction must "
            "retain the counter and the standing reference sections."
        )


def main() -> int:
    tests = [
        test_state_exists_and_nonempty,
        test_state_stays_readable_in_one_call,
        test_rolling_cycle_log_is_pruned,
        test_stable_reference_sections_survive,
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
