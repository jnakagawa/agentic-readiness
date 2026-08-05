"""BACKLOG.md readability guard (bookkeeping self-healing).

Runnable directly, no pytest required:

    python tests/test_backlog_hygiene.py

The playbook mandates that every cycle read BACKLOG.md to pick work, and its
own header says "prioritized; prune every cycle". BACKLOG is MUTABLE working
state, not the append-only history (that lives in loop/LOG.md + git). The
per-cycle discipline is: when a cycle CLOSES an item it leaves a short
transitional `<!-- DONE ... -->` marker so the next cycle's reviewer sees it
was closed, and a later cycle PRUNES that marker (the full record is already
in loop/LOG.md + git). By Cycle 265 that pruning had lapsed: 98 completed-item
markers (DONE / PRUNED / SUPERSEDED / MERGED / EXECUTED) had accreted to
~149KB — 60% of a 273KB file — pushing it past the Read tool's 256KB
single-read limit and silently degrading the mandated per-cycle read. Cycle 265
pruned them (open items untouched — only completed-item comment blocks removed,
120KB result) and added this guard so the file can never re-balloon past
readability unnoticed, and so completed-item markers cannot re-accrete: a fire
that lets either grow too large fails the suite and MUST prune before it can
commit its own work.

These are hygiene thresholds, not scoring semantics — no rubric version is
implicated. Bump the caps here (with a note) only if the loop deliberately
decides BACKLOG should carry more standing context.

This is the BACKLOG sibling of tests/test_state_hygiene.py; the two guard the
two mutable working-state files the loop depends on every fire.
"""
from __future__ import annotations

import os
import re
import sys

_BACKLOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "loop", "BACKLOG.md"
)

# Hard ceiling: must stay comfortably under the Read tool's 256KB single-read
# limit so a fresh fire can always `Read` BACKLOG.md in one call. BACKLOG is a
# legitimately long prioritized list (many open items), so this is looser than
# STATE's ceiling — but still a firm readability backstop.
_MAX_BYTES = 220_000

# Completed-item markers are the specific failure mode that broke readability:
# they are transitional and belong in loop/LOG.md + git, not accreted here. A
# modest budget lets a cycle note a just-closed item without letting them
# re-accrete into the six-figure bloat Cycle 265 removed. This trips long
# before the byte ceiling, pointing straight at the fix.
_MAX_CLOSED_MARKER_BYTES = 24_000
_CLOSED_KEYWORDS = ("DONE", "PRUNED", "SUPERSEDED", "MERGED", "EXECUTED")

# Priority sections a compaction must never drop — losing any would strip the
# prioritization the whole file exists to carry.
_REQUIRED_MARKERS = (
    "# Backlog",
    "## P0",
    "## P1",
    "## P2",
)


def _read():
    with open(_BACKLOG, "r", encoding="utf-8") as fh:
        return fh.read()


def _closed_marker_bytes(text: str) -> int:
    """Total bytes of `<!-- DONE/PRUNED/SUPERSEDED/MERGED/EXECUTED ... -->`
    comment blocks — the completed-item markers that belong in LOG.md + git."""
    total = 0
    for m in re.finditer(r"<!--.*?-->", text, flags=re.DOTALL):
        block = m.group(0)
        if any(k in block[:60] for k in _CLOSED_KEYWORDS):
            total += len(block.encode("utf-8"))
    return total


def test_backlog_exists_and_nonempty():
    assert os.path.exists(_BACKLOG), "loop/BACKLOG.md is missing"
    assert os.path.getsize(_BACKLOG) > 0, "loop/BACKLOG.md is empty"


def test_backlog_stays_readable_in_one_call():
    size = os.path.getsize(_BACKLOG)
    assert size < _MAX_BYTES, (
        f"loop/BACKLOG.md is {size} bytes (>= {_MAX_BYTES}); it is growing past what "
        "the Read tool can load in one call. Prune completed-item markers and stale "
        "items (history is preserved in loop/LOG.md + git) before committing."
    )


def test_completed_markers_do_not_accrete():
    n = _closed_marker_bytes(_read())
    assert n < _MAX_CLOSED_MARKER_BYTES, (
        f"loop/BACKLOG.md carries {n} bytes of completed-item comment markers "
        f"(DONE/PRUNED/SUPERSEDED/MERGED/EXECUTED, >= {_MAX_CLOSED_MARKER_BYTES}). "
        "These are transitional — prune them; the full record lives in loop/LOG.md + git."
    )


def test_priority_sections_survive():
    text = _read()
    for marker in _REQUIRED_MARKERS:
        assert marker in text, (
            f"loop/BACKLOG.md is missing the required section marker {marker!r}; a "
            "compaction must retain the prioritized P0/P1/P2 structure."
        )


def test_guards_have_teeth():
    # Synthetic bloat trips both size guards; a clean synthetic passes neither
    # trip — so the guards are non-vacuous (they detect the Cycle-265 failure
    # mode, not just describe it).
    bloated = "## P0\n" + ("<!-- DONE filler %d " % 0) + "x" * _MAX_CLOSED_MARKER_BYTES + " -->\n"
    assert _closed_marker_bytes(bloated) >= _MAX_CLOSED_MARKER_BYTES, (
        "teeth: an over-budget DONE-marker blob must be detected"
    )
    clean = "## P0\n- **[LOCAL] a real open item** — do the thing\n"
    assert _closed_marker_bytes(clean) == 0, (
        "teeth: a marker-free backlog must read as zero closed-marker bytes"
    )
    # A single small recent DONE note is under budget (the workflow the budget
    # is meant to allow).
    one_note = "## P0\n<!-- DONE Cycle 999: shipped X, see LOG -->\n- **open** — y\n"
    assert 0 < _closed_marker_bytes(one_note) < _MAX_CLOSED_MARKER_BYTES, (
        "teeth: one small DONE note is allowed, not zero, not over budget"
    )


def main() -> int:
    tests = [
        test_backlog_exists_and_nonempty,
        test_backlog_stays_readable_in_one_call,
        test_completed_markers_do_not_accrete,
        test_priority_sections_survive,
        test_guards_have_teeth,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL: {t.__name__}: {type(exc).__name__}: {exc}")
        else:
            print(f"  ok: {t.__name__}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
