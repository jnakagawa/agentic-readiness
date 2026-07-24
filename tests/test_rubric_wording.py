"""Vendor-neutral WORDING guard — the capability-lens invariant, made executable.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_rubric_wording.py

The playbook's capability lens (PLAYBOOK.md) states the invariant twice:

    "Checks are worded by capability, never by vendor. No special-casing any
     domain or product, favorable or hostile."

Cycle 21 made the vendor-neutral SCORING half executable: `test_canonical_replay`'s
domain-relabeling invariance proves the +39.4 delta is a property of the capability
EVIDENCE, not the storefront's identity — relabel a fixture's host everywhere and
the score / pillars / statuses are byte-for-byte identical. But that guard proves
the MATH is identity-blind; it says nothing about whether the check DESCRIPTIONS —
which `asrs.scorecard._write_rubric_page` renders VERBATIM on the public rubric
page — read neutrally to a skeptic. The wording half was unguarded, and it had
drifted: the `bhv_no_human_gate` check description carried "The Exa lesson —",
naming a specific scored commercial storefront in a scored check's wording (the
exact "special-casing a domain or product" the invariant forbids). Cycle 29
reworded it to capability language ("business-rule gates ... stop an agent as
surely as a technical one") and added this guard so the regression cannot silently
return.

WHAT THIS GUARDS: every SCORED check's `id` + `desc` (the machine-parsed
`checks:` list, exactly what `scoring.load_rubric` reads and the rubric page
renders) is scanned for the name of any SCORED STOREFRONT / PRODUCT the benchmark
evaluates — the class of name whose presence would be special-casing a domain.
The denylist is the storefronts we have actually scored (the canonical pair) plus
"Exa" (the name that had leaked). A future cycle that scores a new named
storefront should ADD its name here, so the name can never leak into check wording.

WHAT THIS DOES NOT CLAIM: this is a denylist tripwire against RE-INTRODUCING a
KNOWN scored-storefront name, not a proof of universal prose neutrality — a novel
vendor name not on the list would pass. It complements, and does not replace,
Cycle 21's relabel-invariance (neutral scoring) and the standing "prose re-read"
referee pass (neutral reading). Its job is narrow and durable: make the specific
regression that just happened impossible to ship unnoticed.

SCOPE — SCORED CHECKS ONLY, NOT COMMENTS. `load_rubric` parses `checks:`; it does
not parse the YAML changelog comments. Those comments DO name the canonical test
pair and "Shopify" — but to DOCUMENT mechanism and score-neutrality (why a change
is monotone / why the canonical delta is unchanged), which is engineering history,
a distinct category from wording a SCORED check around a specific storefront. This
guard deliberately keys on the parsed, scored text — the crisp boundary that
matches what the scoring engine sees.

DELIBERATELY vendor-neutral about the MEASUREMENT INSTRUMENT: the denylist does
NOT include the panel model names (Claude, Codex) or the AI-crawler UA tokens
(GPTBot, ClaudeBot, OAI-SearchBot, PerplexityBot, Google-Extended). Those name the
measuring apparatus and the crawler POPULATION a robots.txt policy must address —
listed symmetrically, favoring none — which is the capability being measured, not
a scored storefront being special-cased. Flagging them would be a false positive.

Non-vacuous: a negative control feeds the SAME scanner a synthetic check whose
desc says "The Exa lesson" and asserts the scanner flags it — so a green run means
the real rubric is clean, not that the scanner never fires. A second structural
test asserts the scanner actually saw the full parsed check set (not an empty
list) so the pass cannot be vacuous.

Rubric-wording only: this test reads no score and touches no scoring path. The
Cycle-29 reword is display-only (`desc` is rendered on the rubric page but never
read by `scoring.score`, which keys on `id`/`pillar`/`max_points`), so the rubric
stays v0.7 and the canonical delta is unchanged — re-confirmed by
`tests/test_canonical_replay.py` in the same suite.
"""

from __future__ import annotations

import os
import re
import sys

# Make the worktree's asrs importable when run as a bare script.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from asrs.scoring import load_rubric  # noqa: E402

# Names of SCORED commercial storefronts / products the benchmark evaluates.
# Presence of any of these in a scored check's id/desc = special-casing a domain
# or product, which the capability-lens invariant forbids. Add a new storefront's
# name here whenever a cycle scores one by name.
_SCORED_STOREFRONT_NAMES = ["exa", "driftflight", "drift-flight"]


def _scan_checks_for_scored_storefront(checks: list[dict]) -> list[tuple[str, str]]:
    """Return (check_id, offending_term) for every denylisted name found in a
    check's ``id`` or ``desc``.

    Word-boundary, case-insensitive: matches "Exa" in "The Exa lesson" but not
    "exa" inside "example"/"Texas"/"hexadecimal". This is the SINGLE scanner used
    by both the real-rubric assertion and the negative control, so the control
    validates the same code the guard relies on.
    """
    patterns = [
        (name, re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE))
        for name in _SCORED_STOREFRONT_NAMES
    ]
    hits: list[tuple[str, str]] = []
    for check in checks:
        cid = str(check.get("id", ""))
        text = f"{cid} {check.get('desc', '')}"
        for name, pat in patterns:
            if pat.search(text):
                hits.append((cid, name))
    return hits


def test_no_scored_storefront_named_in_check_wording() -> None:
    """No scored check's id/desc special-cases a scored storefront by name."""
    rubric = load_rubric()
    checks = rubric.get("checks") or []
    hits = _scan_checks_for_scored_storefront(checks)
    assert not hits, (
        "scored check wording names a scored storefront/product (violates the "
        "capability-lens 'never by vendor / no special-casing a domain' invariant): "
        + ", ".join(f"{cid!r} contains {term!r}" for cid, term in hits)
    )


def test_scanner_is_non_vacuous_negative_control() -> None:
    """The SAME scanner flags a re-introduced 'Exa' reference — so a green real
    run means clean wording, not a scanner that never fires."""
    injected = [
        {"id": "bhv_no_human_gate", "desc": "No human-only gate. The Exa lesson — "
                                            "business-rule gates are readiness factors."},
    ]
    hits = _scan_checks_for_scored_storefront(injected)
    assert hits == [("bhv_no_human_gate", "exa")], (
        f"negative control did not fire as expected: {hits!r}"
    )


def test_guard_scanned_the_full_parsed_check_set() -> None:
    """Guard against a vacuous pass: the scan must cover every parsed check, and
    the parsed set must be non-empty and match the scored rubric's real size."""
    rubric = load_rubric()
    checks = rubric.get("checks") or []
    # The scanner reads id/desc off the SAME list scoring indexes by id.
    assert len(checks) == len(rubric.get("_checks_by_id", {})), (
        "parsed check list and scoring index disagree — the guard would scan a "
        "different set than the scorer uses"
    )
    assert len(checks) >= 20, (
        f"expected the full rubric check set (>=20 checks), saw {len(checks)} — "
        "a truncated rubric would make the wording guard vacuously pass"
    )
    # Every scanned check actually carries wording to inspect.
    assert all(c.get("desc") for c in checks), "a scored check has an empty desc"


def test_measurement_instrument_names_are_not_flagged() -> None:
    """The denylist must NOT catch the measuring apparatus — panel model names and
    AI-crawler UA tokens name the instrument / crawler population, not a scored
    storefront. Flagging them would be a false positive that pressures true
    capability wording out of the rubric."""
    instrument = [
        {"id": "robots_ai_crawlers", "desc": "robots.txt policy for GPTBot, "
                                             "ClaudeBot, OAI-SearchBot, PerplexityBot, Google-Extended."},
        {"id": "trust_panel_willingness", "desc": "the model panel (Claude, Codex) "
                                                  "is told the user directed the purchase."},
    ]
    hits = _scan_checks_for_scored_storefront(instrument)
    assert hits == [], (
        f"instrument/crawler names were wrongly flagged as scored storefronts: {hits!r}"
    )


def main() -> int:
    tests = [
        test_no_scored_storefront_named_in_check_wording,
        test_scanner_is_non_vacuous_negative_control,
        test_guard_scanned_the_full_parsed_check_set,
        test_measurement_instrument_names_are_not_flagged,
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
