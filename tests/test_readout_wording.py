"""Vendor-neutral WORDING guard — extended from the parsed rubric to the RENDERED
readout prose the public actually reads.

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_readout_wording.py

Cycle 29 made the vendor-neutral WORDING invariant executable for the PARSED
rubric — ``tests/test_rubric_wording.py`` scans every scored check's id/desc for
the name of any scored storefront/product (the class of name whose presence is
"special-casing a domain or product", which the capability lens forbids). But
that guard covers only the machine-parsed ``checks:`` list. The HAND-AUTHORED
readout PROSE — the "read the paper" methodology page and the card's own
``<div class="desc">`` explanation strings — is rendered VERBATIM to a reader and
was UNguarded, exactly the surface the "The Exa lesson" leak lived on before it
was reworded. This is the READOUT half of the standing referee-pass invariant,
made a tripwire instead of a manual prose re-read.

WHAT THIS GUARDS: the rendered ``methodology.html`` and the rendered card
(``build_scorecard`` output) are scanned with the SAME denylist + SAME matcher
Cycle 29 uses (imported from ``test_rubric_wording`` — one source of truth), and
must contain no scored-storefront name. A future cycle that drops "the Exa
lesson" into a card desc or a methodology paragraph fails this test instead of
shipping it to the public page.

DOMAIN-AS-DATA — why a NEUTRAL domain: a scorecard is ABOUT a specific storefront,
so that storefront's domain legitimately appears as DATA (title, hero, column
header). Scanning a canonical-pair card would drown in true positives that are
not vendor-special-casing at all. We therefore render the readout for a NEUTRAL
placeholder domain (``example.test``, not on the denylist): any denylisted name
that appears then cannot have come from the data — it can only be baked into the
hand-authored TEMPLATE prose, which is precisely the leak we want to catch.

SCOPE — rubric.html is DELIBERATELY EXCLUDED. ``_write_rubric_page`` renders the
rubric YAML VERBATIM, changelog comments and all; those comments name the
canonical test pair (and "Shopify") to DOCUMENT mechanism and score-neutrality —
engineering history, the separately-adjudicated category Cycle 29 already carved
out for the parsed rubric (it scans ``checks:``, never the comments). Scanning
the verbatim-YAML page would flag that legitimate history as a violation. Better:
the rendered rubric.html serves here as a LIVE NON-VACUOUS control — the scanner
is shown to fire on it (its changelog names the canonical pair), proving a green
card/methodology run means the prose is clean, not that the scanner never fires
on rendered HTML.

Readout-wording only: this test reads no score and touches no scoring path. The
methodology page and card desc strings are rendered but never read by
``scoring.score`` (which keys on ``id``/``pillar``/``max_points``), so the rubric
stays v0.7 and the canonical delta is unchanged — re-confirmed by
``tests/test_canonical_replay.py`` in the same suite.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Repo root (for asrs) and the tests dir (to import the sibling Cycle-29 module).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from asrs import scorecard  # noqa: E402
from asrs.reliability import quotability  # noqa: E402
from asrs.types import Report  # noqa: E402
from test_rubric_wording import (  # noqa: E402  (one source of truth for the denylist + matcher)
    _SCORED_STOREFRONT_NAMES,
    _scan_text_for_scored_storefront,
)

# A neutral placeholder domain: not on the denylist, so any denylisted hit in a
# render for it comes from hand-authored template prose, never from the data.
_NEUTRAL_DOMAIN = "example.test"


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _render_readout(tmp: Path) -> dict[str, str]:
    """Render the full public readout set for a NEUTRAL-domain report and return
    {filename: rendered_text}. Mirrors ``cli._evaluate`` only in the additive
    surfacing (quotability attached for every mode) — no rubric assertion here.
    """
    rep = Report(
        domain=_NEUTRAL_DOMAIN,
        rubric_version="0.7",
        generated_at="2026-07-24T00:00:00",
        behavioral_runs=[],
        overall_score=50.0,
        grade="F",
    )
    rep.quotability = quotability(rep).to_dict()
    rp = tmp / "rep.json"
    rp.write_text(rep.to_json())
    out = scorecard.build_scorecard([str(rp)], out_path=str(tmp / "card.html"))
    return {
        "card.html": Path(out).read_text(),
        "methodology.html": (tmp / "methodology.html").read_text(),
        "rubric.html": (tmp / "rubric.html").read_text(),
    }


def test_methodology_prose_is_vendor_neutral() -> None:
    """The rendered methodology page names no scored storefront/product."""
    print("test_methodology_prose_is_vendor_neutral")
    with tempfile.TemporaryDirectory() as d:
        rendered = _render_readout(Path(d))
        hits = _scan_text_for_scored_storefront(rendered["methodology.html"])
        _check(
            hits == [],
            "methodology.html names no scored storefront/product "
            f"(vendor-neutral prose); found {hits!r}",
        )


def test_card_hand_authored_prose_is_vendor_neutral() -> None:
    """The rendered card (neutral domain) names no scored storefront/product —
    so any hit would come from hand-authored template prose, not the data."""
    print("test_card_hand_authored_prose_is_vendor_neutral")
    with tempfile.TemporaryDirectory() as d:
        rendered = _render_readout(Path(d))
        card = rendered["card.html"]
        # The neutral domain itself is present as data (sanity: the render is
        # genuinely ABOUT example.test) but is not on the denylist.
        _check(_NEUTRAL_DOMAIN in card, "card renders the neutral domain as data")
        hits = _scan_text_for_scored_storefront(card)
        _check(
            hits == [],
            "card hand-authored prose names no scored storefront/product; "
            f"found {hits!r}",
        )


def test_scanner_fires_on_rendered_html_non_vacuous() -> None:
    """Non-vacuous, two ways: (1) a synthetic prose blob with a re-introduced
    'Exa' reference is flagged by the SAME matcher; (2) the rendered rubric.html
    — the DELIBERATELY out-of-scope surface whose changelog comments name the
    canonical pair — is shown to trip the scanner, proving it genuinely fires on
    real rendered readout HTML (so the clean card/methodology runs above mean the
    prose is neutral, not that the matcher is dead)."""
    print("test_scanner_fires_on_rendered_html_non_vacuous")
    injected = (
        "<div class=\"desc\">No human-only gate. The Exa lesson &mdash; "
        "business-rule gates are readiness factors.</div>"
    )
    _check(
        _scan_text_for_scored_storefront(injected) == ["exa"],
        "synthetic 'The Exa lesson' readout prose is flagged by the shared matcher",
    )
    with tempfile.TemporaryDirectory() as d:
        rendered = _render_readout(Path(d))
        rubric_hits = _scan_text_for_scored_storefront(rendered["rubric.html"])
        _check(
            "driftflight" in rubric_hits or "drift-flight" in rubric_hits,
            "rubric.html (verbatim YAML, out of scope) trips the scanner on its "
            f"changelog names — live proof the matcher fires on rendered HTML; "
            f"found {rubric_hits!r}",
        )


def test_readout_surfaces_are_substantive() -> None:
    """Guard against a vacuous pass from an empty/degenerate render: the scanned
    surfaces must carry substantial prose, and every denylist entry must be a
    non-empty word-boundary token (so the matcher can actually match)."""
    print("test_readout_surfaces_are_substantive")
    with tempfile.TemporaryDirectory() as d:
        rendered = _render_readout(Path(d))
        _check(
            len(rendered["methodology.html"]) >= 4000,
            f"methodology.html is substantive ({len(rendered['methodology.html'])} chars) "
            "— an empty render can't vacuously pass the neutrality scan",
        )
        _check(
            len(rendered["card.html"]) >= 4000,
            f"card.html is substantive ({len(rendered['card.html'])} chars)",
        )
    _check(
        bool(_SCORED_STOREFRONT_NAMES)
        and all(n and n.strip() for n in _SCORED_STOREFRONT_NAMES),
        "the denylist is non-empty and every entry is a real token",
    )


def main() -> int:
    tests = [
        test_methodology_prose_is_vendor_neutral,
        test_card_hand_authored_prose_is_vendor_neutral,
        test_scanner_fires_on_rendered_html_non_vacuous,
        test_readout_surfaces_are_substantive,
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
