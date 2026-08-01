"""Meta-test: no silent dead tests in the hand-maintained runner lists.

Runnable directly, no pytest required:

    python tests/test_runner_registration.py

Every suite in tests/ is run by a hand-maintained explicit ``tests = [...]``
list inside its ``main()`` — there is no pytest collection. A ``def test_*``
that is defined but never added to that list is INVISIBLE: it raises no
collection error and no failure, it simply never runs. Cycle 140 shipped
``test_methodology_documents_output_resolution`` this way; it was dead for four
cycles until Cycle 144 found it by eye and registered it. Cycle 145 found TWO
more the same way (``test_webhook_verification_*`` in test_offering.py, dead
since their arc landed) — proof that eyeballing does not scale.

This guard closes the hole mechanically. It parses each suite's SOURCE with
``ast`` (never imports it, so a broken import in one suite can't mask another)
and asserts, per module:

  * every top-level ``def test_*`` appears in that module's ``tests`` list
    (no silent dead test), and
  * every name in the ``tests`` list resolves to a real top-level ``def test_*``
    (no ghost / typo'd / removed entry).

Off the scoring path, tests-only: rubric version, probes, and the canonical
delta are untouched. The detector's teeth are proven on synthetic sources so
the guard cannot vacuously pass.
"""
from __future__ import annotations

import ast
import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SELF = os.path.basename(__file__)


def _test_modules() -> list[str]:
    """Every runnable suite in tests/ (files named test_*.py)."""
    return sorted(
        os.path.join(_TESTS_DIR, f)
        for f in os.listdir(_TESTS_DIR)
        if f.startswith("test_") and f.endswith(".py")
    )


def _defined_tests(tree: ast.Module) -> set[str]:
    """Module-level ``def test_*`` names (the functions a suite could run)."""
    return {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }


def _registered_tests(tree: ast.Module) -> set[str]:
    """Names collected from every ``tests = [ ... ]`` list assignment.

    Walks the whole tree because the convention puts the list inside
    ``main()``, not at module scope. Only bare ``Name`` elements count — the
    runner lists are plain lists of function references.
    """
    registered: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(t, ast.Name) and t.id == "tests" for t in node.targets
        ):
            continue
        if isinstance(node.value, ast.List):
            for el in node.value.elts:
                if isinstance(el, ast.Name):
                    registered.add(el.id)
    return registered


def _parse(path: str) -> ast.Module:
    with open(path, encoding="utf-8") as fh:
        return ast.parse(fh.read())


def test_every_defined_test_is_registered():
    # The core guard: a defined-but-unregistered test is a SILENT dead test.
    # This is the mechanical form of the Cycle-140/144/145 bug.
    offenders = {}
    for path in _test_modules():
        tree = _parse(path)
        missing = _defined_tests(tree) - _registered_tests(tree)
        if missing:
            offenders[os.path.basename(path)] = sorted(missing)
    assert not offenders, f"silent dead tests (defined, never registered): {offenders}"
    print(f"  ok: every def test_* is registered in its runner list across {len(_test_modules())} suites")


def test_no_registered_ghost_names():
    # The inverse rot: a name in the tests list that no longer resolves to a
    # top-level def (typo, or a test renamed/removed but left in the list) —
    # it would raise NameError at import, but this names it precisely.
    ghosts = {}
    for path in _test_modules():
        tree = _parse(path)
        extra = _registered_tests(tree) - _defined_tests(tree)
        if extra:
            ghosts[os.path.basename(path)] = sorted(extra)
    assert not ghosts, f"registered names with no matching def test_*: {ghosts}"
    print("  ok: every registered name resolves to a real top-level def test_*")


def test_every_suite_has_a_nonempty_runner_list():
    # A suite with no discoverable tests list runs nothing — the whole-file
    # version of a dead test. Guards against a future suite forgetting main().
    empty = []
    for path in _test_modules():
        if not _registered_tests(_parse(path)):
            empty.append(os.path.basename(path))
    assert not empty, f"suites with no non-empty tests=[...] runner list: {empty}"
    print(f"  ok: all {len(_test_modules())} suites carry a non-empty runner list")


def test_detector_has_teeth():
    # Non-vacuous: prove the diff logic actually catches a dead test and does
    # NOT false-positive on a clean module. Synthetic sources only — no local
    # variable is named `tests` here, so the real-module scan above is unaffected.
    dead_src = (
        "def test_alpha():\n    pass\n"
        "def test_beta():\n    pass\n"  # defined but omitted below == dead
        "def main():\n    runner = [test_alpha]\n"
    ).replace("runner", "tests")
    dead_tree = ast.parse(dead_src)
    assert _defined_tests(dead_tree) == {"test_alpha", "test_beta"}
    assert _registered_tests(dead_tree) == {"test_alpha"}
    assert (_defined_tests(dead_tree) - _registered_tests(dead_tree)) == {"test_beta"}
    print("  ok: detector flags a defined-but-unregistered test (has teeth)")

    clean_src = (
        "def test_alpha():\n    pass\n"
        "def test_beta():\n    pass\n"
        "def main():\n    tests = [test_alpha, test_beta]\n"
    )
    clean_tree = ast.parse(clean_src)
    assert not (_defined_tests(clean_tree) - _registered_tests(clean_tree))
    print("  ok: detector does NOT fire on a fully-registered module (no false positive)")

    # A ghost: a name in the list with no matching def.
    ghost_src = (
        "def test_alpha():\n    pass\n"
        "def main():\n    tests = [test_alpha, test_gone]\n"
    )
    ghost_tree = ast.parse(ghost_src)
    assert (_registered_tests(ghost_tree) - _defined_tests(ghost_tree)) == {"test_gone"}
    print("  ok: detector flags a ghost registered name (has teeth)")


def main() -> int:
    tests = [
        test_every_defined_test_is_registered,
        test_no_registered_ghost_names,
        test_every_suite_has_a_nonempty_runner_list,
        test_detector_has_teeth,
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
