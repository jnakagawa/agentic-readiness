"""JSON persistence + terminal report card for ASRS.

Plain ASCII only, stdlib only — the report card is meant to render in any
terminal and paste cleanly into a chat. ``save`` writes the machine-readable
JSON; ``render`` / ``render_compare`` produce the human view.
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path


# Pillar display order + labels (keys must match rubric pillar ids).
_PILLAR_ORDER = ("access", "legibility", "transactability", "trust", "outcome")
_PILLAR_LABEL = {
    "access": "Access",
    "legibility": "Legibility",
    "transactability": "Transactability",
    "trust": "Trust",
    "outcome": "Outcome",
}

_BAR_WIDTH = 20

# Behavioral checkpoint ladder (order matters for the summary table).
_CHECKPOINTS = (
    "found_product",
    "understood_pricing",
    "found_purchase_path",
    "machine_payable_path",
    "no_human_gate",
)


# --------------------------------------------------------------------------
# persistence
# --------------------------------------------------------------------------

def save(report, out_dir: str = "runs") -> str:
    """Write ``report`` as JSON to ``<out_dir>/<domain>_<ts>.json``.

    Domain dots become underscores; timestamp is derived from the report's
    ``generated_at`` when parseable, else now(). Returns the path written.
    """
    os.makedirs(out_dir, exist_ok=True)

    safe_domain = report.domain.replace(".", "_").replace("/", "_")
    ts = _filename_ts(getattr(report, "generated_at", "") or "")
    filename = f"{safe_domain}_{ts}.json"
    path = os.path.join(out_dir, filename)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report.to_json())
    return str(Path(path))


def _filename_ts(generated_at: str) -> str:
    """YYYYMMDDTHHMMSS from an ISO generated_at, falling back to now()."""
    try:
        dt = datetime.fromisoformat(generated_at)
    except (ValueError, TypeError):
        dt = datetime.utcnow()
    return dt.strftime("%Y%m%dT%H%M%S")


# --------------------------------------------------------------------------
# rendering helpers
# --------------------------------------------------------------------------

def _bar(score, width: int = _BAR_WIDTH) -> str:
    """A [####----] style bar for a 0-100 score. n/a -> empty track."""
    if score is None:
        return "[" + " " * width + "]"
    frac = max(0.0, min(1.0, score / 100.0))
    filled = int(round(frac * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _fmt_score(score) -> str:
    return "n/a" if score is None else f"{score:5.1f}"


def _status_value(status) -> str:
    return getattr(status, "value", status)


def _rule(char: str = "-", width: int = 60) -> str:
    return char * width


def _failing_checks(report):
    """FAIL/PARTIAL checks sorted by lost points (max - earned) desc."""
    out = [
        c for c in report.checks
        if _status_value(c.status) in ("fail", "partial")
    ]
    out.sort(key=lambda c: (c.max_points - c.points), reverse=True)
    return out


def _cant_test_checks(report):
    return [c for c in report.checks if _status_value(c.status) == "cant_test"]


# --------------------------------------------------------------------------
# single report card
# --------------------------------------------------------------------------

def render(report) -> str:
    """A clean terminal report card for one Report."""
    lines: list[str] = []

    # -- header --
    lines.append(_rule("="))
    lines.append(f"  ASRS  {report.domain}")
    lines.append(
        f"  OVERALL {report.overall_score:.1f}/100   GRADE {report.grade or '?'}"
    )
    lines.append(
        f"  rubric v{report.rubric_version}   {report.generated_at}"
    )
    lines.append(_rule("="))

    # -- caps --
    if report.caps_applied:
        lines.append("")
        lines.append("  ! GRADE CAPPED by critical findings:")
        for slug in report.caps_applied:
            lines.append(f"      - {slug}")

    # -- pillars --
    lines.append("")
    lines.append("  PILLARS")
    for pillar in _PILLAR_ORDER:
        if pillar not in report.pillar_scores:
            continue
        pscore = report.pillar_scores[pillar]
        label = _PILLAR_LABEL.get(pillar, pillar).ljust(16)
        lines.append(f"    {label} {_bar(pscore)} {_fmt_score(pscore)}")
    # Any pillars present in scores but not in the known order (defensive).
    for pillar, pscore in report.pillar_scores.items():
        if pillar in _PILLAR_ORDER:
            continue
        label = pillar.ljust(16)
        lines.append(f"    {label} {_bar(pscore)} {_fmt_score(pscore)}")

    # -- findings --
    failing = _failing_checks(report)
    lines.append("")
    lines.append("  FINDINGS")
    if not failing:
        lines.append("    (none — no failed or partial checks)")
    else:
        for c in failing:
            lost = c.max_points - c.points
            remediation = c.remediation or "(no remediation given)"
            lines.append(f"    [-{lost:.1f} pts] {c.finding} — {remediation}")

    # -- can't-test --
    cant = _cant_test_checks(report)
    if cant:
        lines.append("")
        lines.append("  CANT_TEST (excluded from scoring)")
        for c in cant:
            note = c.finding or c.check_id
            lines.append(f"    - {c.check_id}: {note}")

    # -- trust panel --
    if report.trust_panel:
        lines.append("")
        lines.append("  TRUST PANEL (would you transact here?)")
        for v in report.trust_panel:
            verdict = "willing" if v.willing else "refused"
            concerns = "; ".join(v.concerns) if v.concerns else "none"
            lines.append(
                f"    {v.model:<8} {verdict:<8} "
                f"(conf {v.confidence:.2f}) — {concerns}"
            )

    # -- behavioral checkpoints --
    if report.behavioral_runs:
        lines.append("")
        lines.append("  BEHAVIORAL CHECKPOINTS")
        lines.extend(_behavioral_table(report.behavioral_runs))

    lines.append("")
    return "\n".join(lines)


def _behavioral_table(runs) -> list[str]:
    """Compact per-run checkpoint grid: Y/./? per checkpoint."""
    # Short headers for the ladder.
    short = {
        "found_product": "prod",
        "understood_pricing": "price",
        "found_purchase_path": "path",
        "machine_payable_path": "pay",
        "no_human_gate": "nogate",
    }
    header = "    " + "model/trial".ljust(16)
    for cp in _CHECKPOINTS:
        header += short[cp].center(8)
    out = [header]
    for r in runs:
        row = "    " + f"{r.model}#{r.trial}".ljust(16)
        for cp in _CHECKPOINTS:
            val = r.checkpoints.get(cp)
            mark = "Y" if val is True else ("." if val is False else "?")
            row += mark.center(8)
        out.append(row)
        if r.blockers:
            out.append("      blockers: " + "; ".join(r.blockers))
    return out


# --------------------------------------------------------------------------
# compare view
# --------------------------------------------------------------------------

def render_compare(a, b, label_a: str = "without", label_b: str = "with") -> str:
    """Side-by-side delta between two reports."""
    lines: list[str] = []
    delta = b.overall_score - a.overall_score

    lines.append(_rule("="))
    lines.append("  ASRS DELTA")
    lines.append(
        f"  {label_a} {a.domain} = {a.overall_score:.1f} ({a.grade or '?'})"
        f"  ->  {label_b} {b.domain} = {b.overall_score:.1f} ({b.grade or '?'})"
    )
    lines.append(f"  (delta {delta:+.1f})")
    lines.append(_rule("="))

    # -- per-pillar two-column table --
    lines.append("")
    col_a = label_a[:12]
    col_b = label_b[:12]
    lines.append(
        "  " + "PILLAR".ljust(16) + col_a.rjust(9) + col_b.rjust(11) + "   DELTA"
    )
    lines.append("  " + _rule("-", 46))
    all_pillars = list(_PILLAR_ORDER)
    for pillar in a.pillar_scores:
        if pillar not in all_pillars:
            all_pillars.append(pillar)
    for pillar in b.pillar_scores:
        if pillar not in all_pillars:
            all_pillars.append(pillar)

    for pillar in all_pillars:
        sa = a.pillar_scores.get(pillar)
        sb = b.pillar_scores.get(pillar)
        if sa is None and sb is None and pillar not in a.pillar_scores and pillar not in b.pillar_scores:
            continue
        label = _PILLAR_LABEL.get(pillar, pillar).ljust(16)
        d_str = _pillar_delta_str(sa, sb)
        lines.append(
            "  " + label + _fmt_score(sa).rjust(9) + _fmt_score(sb).rjust(11)
            + "   " + d_str
        )

    # -- findings unique to each side --
    a_fail = {c.finding for c in a.checks if _status_value(c.status) == "fail"}
    b_fail = {c.finding for c in b.checks if _status_value(c.status) == "fail"}
    only_a = sorted(a_fail - b_fail)[:8]
    only_b = sorted(b_fail - a_fail)[:8]

    lines.append("")
    lines.append(f"  FAILING ONLY in {label_a} ({a.domain})")
    if only_a:
        for slug in only_a:
            lines.append(f"    - {slug}")
    else:
        lines.append("    (none)")

    lines.append("")
    lines.append(f"  FAILING ONLY in {label_b} ({b.domain})")
    if only_b:
        for slug in only_b:
            lines.append(f"    - {slug}")
    else:
        lines.append("    (none)")

    lines.append("")
    return "\n".join(lines)


def _pillar_delta_str(sa, sb) -> str:
    if sa is None and sb is None:
        return "n/a"
    if sa is None:
        return "new"
    if sb is None:
        return "gone"
    return f"{sb - sa:+.1f}"


# --------------------------------------------------------------------------
# shared: rough tag stripper (used by CLI for homepage excerpt)
# --------------------------------------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_tags(html: str) -> str:
    """Very rough HTML -> text: drop script/style, strip tags, squeeze WS."""
    if not html:
        return ""
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text.strip()
