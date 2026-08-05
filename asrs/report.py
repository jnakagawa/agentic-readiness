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

# The payment-corroboration state -> terminal text, shared by the single card's
# sub-line and the compare view's per-side annotation so every terminal readout
# spells the SAME state identically (they can never phrase the same signal two
# ways). Kept byte-identical to the Cycle-258 single-card wording.
_PAYMENT_CORROB_TEXT = {
    "good": "behaviorally corroborated — reached a machine-payable path "
            "in every valid trial",
    "neutral": "no payment, as predicted — hit the payment wall in every "
               "valid trial",
    "warn": "NOT corroborated — static prediction and lived experience "
            "disagree across trials",
}


def _payment_corroboration_state_for(report) -> str | None:
    """The payment-corroboration DECISION for one report — ``"good"`` /
    ``"neutral"`` / ``"warn"``, or ``None`` when there is nothing to corroborate
    (no valid behavioral run, or the ``x402_probe`` prediction check is absent).

    The single extraction shared by the single-card sub-line and the compare
    view's per-side annotation, so every terminal payment-corroboration readout
    reads the SAME signal — the static ``x402_probe`` status and the
    ``machine_payable_path`` checkpoint across VALID behavioral trials — via the
    pure decision in :func:`asrs.scorecard.payment_corroboration_state` (the same
    decision the HTML card's badge and the calibration guard consume). Pure /
    read-only: it moves no score and bumps no rubric version.
    """
    # Lazy import: keep the report module light and avoid importing the heavy
    # HTML scorecard module at load time (matches the reliability lazy-imports).
    from .scorecard import (  # noqa: PLC0415
        _PAYMENT_EXPERIENCE_CHECKPOINT,
        _PAYMENT_PREDICTION_CHECK,
        payment_corroboration_state,
    )

    valid = [r for r in report.behavioral_runs if r.checkpoints]
    if not valid:
        return None
    prediction = None
    for c in report.checks:
        if c.check_id == _PAYMENT_PREDICTION_CHECK:
            prediction = _status_value(c.status)
            break
    if prediction is None:
        return None
    predicted_payable = prediction == "pass"
    reached = [bool(r.checkpoints.get(_PAYMENT_EXPERIENCE_CHECKPOINT)) for r in valid]
    return payment_corroboration_state(predicted_payable, reached)


def _payment_corroboration_line(report) -> list[str]:
    """Terminal analog of the HTML card's payment-corroboration badge: one
    indented sub-line under the Transactability row saying whether the
    shopper's LIVED payment experience corroborates the static transactability
    PREDICTION. Reads the SAME data the HTML badge and the calibration guard
    read — the static ``x402_probe`` status and the ``machine_payable_path``
    checkpoint across VALID behavioral trials — via the shared decision in
    :func:`asrs.scorecard.payment_corroboration_state`, so the two readouts can
    never disagree.

    Display-only: it moves no score and bumps no rubric version. Empty (no
    line) when no valid behavioral run exists (a static-only card has no lived
    experience to corroborate against) or the prediction check is absent (an
    older/partial report) — mirroring the HTML badge's suppression, so static
    cards are byte-for-byte unchanged.
    """
    state = _payment_corroboration_state_for(report)
    if state is None:
        return []
    return [f"      payment corroboration: {_PAYMENT_CORROB_TEXT[state]}"]


def _earner_rep(report) -> dict:
    """The minimal ``{"checks": [...]}`` dict :func:`_pillar_top_earner` reads,
    built from the Report's own checks. The four fields carry the SAME values the
    JSON the HTML card renders from carries, so the terminal and the card feed the
    identical earner selector — the coupling the parity guard pins."""
    return {
        "checks": [
            {
                "pillar": c.pillar,
                "points": c.points,
                "finding": c.finding,
                "check_id": c.check_id,
            }
            for c in (getattr(report, "checks", None) or [])
        ]
    }


def _pillar_earner_line(earner_rep: dict, pillar: str, pscore) -> list[str]:
    """Terminal analog of the HTML card's per-pillar "earned by" caption: one
    indented sub-line naming the single check that contributes the MOST raw points
    to ``pillar``, so the score is ATTRIBUTABLE (not a diffuse aggregate) — the
    Cycle-191 calibration insight surfaced in the terminal, the counterpart to the
    HTML caption added in Cycle 192.

    Reads the SAME :func:`asrs.scorecard._pillar_top_earner` the HTML card reads,
    so the two surfaces can never name a different earner (pinned by the
    terminal<->HTML parity guard). Display-only: it moves no score and bumps no
    rubric version; vendor-neutral (names whichever check earns the most, never a
    fixed one). Empty (no line) when the pillar is n/a (None score) or nothing
    earns credit — a genuinely unearned score names nothing, mirroring the HTML
    card's omission, so those rows are unchanged.
    """
    if pscore is None:
        return []
    # Lazy import: keep the report module light, matching the corroboration line.
    from .scorecard import _pillar_top_earner  # noqa: PLC0415

    top = _pillar_top_earner(earner_rep, pillar)
    if top is None:
        return []
    finding, pts = top
    return [f"      earned by {finding} +{pts:g}"]


def render(report) -> str:
    """A clean terminal report card for one Report."""
    lines: list[str] = []

    # -- header --
    lines.append(_rule("="))
    lines.append(f"  ASRS  {report.domain}")
    if getattr(report, "scored", True) and report.overall_score is not None:
        lines.append(
            f"  OVERALL {report.overall_score:.1f}/100   GRADE {report.grade or '?'}"
        )
    else:
        # No observable pillar — not scorable (never a punitive 0.0/F).
        lines.append(
            "  NOT SCORABLE — no observable pillars (every check NA/CANT_TEST)"
        )
    lines.append(
        f"  rubric v{report.rubric_version}   {report.generated_at}"
    )
    # -- quotability: is the headline number reproducible enough to cite? --
    # Display-only annotation (never a score gate); makes a single-trial or
    # unstable panel self-flag as provisional right next to the number it taints.
    lines.extend(_quotability_lines(report))
    lines.append(_rule("="))

    # -- caps --
    if report.caps_applied:
        lines.append("")
        lines.append("  ! GRADE CAPPED by critical findings:")
        for slug in report.caps_applied:
            lines.append(f"      - {slug}")

    # -- pillars --
    # The Transactability row carries a display-only behavioral-corroboration
    # sub-line when a panel has run — the terminal analog of the HTML card's
    # badge, reading the SAME signal (see :func:`_payment_corroboration_line`).
    corrob_line = _payment_corroboration_line(report)
    earner_rep = _earner_rep(report)
    lines.append("")
    lines.append("  PILLARS")
    for pillar in _PILLAR_ORDER:
        if pillar not in report.pillar_scores:
            continue
        pscore = report.pillar_scores[pillar]
        label = _PILLAR_LABEL.get(pillar, pillar).ljust(16)
        lines.append(f"    {label} {_bar(pscore)} {_fmt_score(pscore)}")
        # "earned by" caption BEFORE the corroboration line, matching the HTML
        # card's name-span order ({earner}{badge}).
        lines.extend(_pillar_earner_line(earner_rep, pillar, pscore))
        if pillar == "transactability":
            lines.extend(corrob_line)
    # Any pillars present in scores but not in the known order (defensive).
    for pillar, pscore in report.pillar_scores.items():
        if pillar in _PILLAR_ORDER:
            continue
        label = pillar.ljust(16)
        lines.append(f"    {label} {_bar(pscore)} {_fmt_score(pscore)}")
        lines.extend(_pillar_earner_line(earner_rep, pillar, pscore))

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
        lines.append("  TRUST PANEL (user directed the purchase — what does the agent do?)")
        decision_labels = {
            "proceed": "proceed",
            "proceed_with_warning": "warn+go",
            "refuse": "refused",
        }
        for v in report.trust_panel:
            decision = getattr(v, "decision", "") or ("proceed" if v.willing else "refuse")
            verdict = decision_labels.get(decision, decision)
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
        lines.extend(_reliability_lines(report.behavioral_runs))

    # -- task battery (cross-intent coverage/reliability) --
    battery = getattr(report, "battery_summary", None)
    if battery:
        lines.extend(_battery_lines(battery))

    lines.append("")
    return "\n".join(lines)


def _battery_lines(summary) -> list[str]:
    """Cross-intent coverage + reliability from a task battery.

    A single shopper task is one draw from a wide distribution of intents; the
    battery ran the panel once per intent so a site's readiness can be read per
    intent and, across them, as a reliability spread. Diagnostic only — it does
    not feed the score (the header number came from the primary task). The math
    lives in :mod:`asrs.battery`; this only prints the already-aggregated dict.
    """
    n = summary.get("n_tasks", 0)
    signal = summary.get("tasks_with_signal", 0)
    out = [
        "",
        f"  TASK BATTERY (does readiness hold across intents?  "
        f"{signal}/{n} intents observed)",
    ]
    for tr in summary.get("per_task", []) or []:
        tid = tr.get("task_id", "?")
        kind = tr.get("kind", "") or "unspecified"
        if tr.get("valid_runs", 0) > 0:
            mc = tr.get("mean_completion")
            frac = f"{mc:.0%}" if isinstance(mc, (int, float)) else "n/a"
            detail = f"{frac} avg checkpoint completion ({tr.get('valid_runs')} valid)"
        else:
            detail = "no signal (no valid run — not a site failure)"
        out.append(f"    {tid:<20} [{kind}]  {detail}")

    # Offering-relative comparability (brick 3): when discovery drove the
    # battery, name WHICH archetypes the numbers are over and which the site does
    # not offer, so a mean is never read across mismatched task sets. Both lines
    # render only when an offering profile marked something NA (na_archetypes
    # populated) — a hand-authored battery with no discovery prints neither.
    na = summary.get("na_archetypes", []) or []
    if na:
        assessed = summary.get("assessed_archetypes", []) or []
        out.append(
            "    assessed over: " + (", ".join(assessed) if assessed else "none")
        )
        out.append("    not offered (NA, excluded): " + ", ".join(na))

    # Per storefront archetype: a site can be strong on one kind and weak on
    # another; only print the rollup when it splits into >1 archetype (with a
    # single kind the per-kind line just restates the battery-wide number).
    per_kind = summary.get("per_kind", []) or []
    if len(per_kind) > 1:
        out.append("    by archetype:")
        for kr in per_kind:
            kind = kr.get("kind", "") or "unspecified"
            if kr.get("tasks_with_signal", 0) > 0:
                mc = kr.get("mean_completion")
                frac = f"{mc:.0%}" if isinstance(mc, (int, float)) else "n/a"
                ks = kr.get("cross_task_spread")
                spread_txt = f", spread {ks:.2f}" if isinstance(ks, (int, float)) else ""
                detail = f"{frac} avg completion ({kr.get('tasks_with_signal')}/{kr.get('n_tasks')} intents{spread_txt})"
            else:
                detail = f"no signal (0/{kr.get('n_tasks')} intents observed)"
            out.append(f"      {kind:<18} {detail}")

    # Between-archetype spread: how much of the variance is storefront-TYPE
    # specialization vs within-type noise. Only a number when >=2 archetypes had
    # signal (you can't observe type-specialization from a single type).
    bks = summary.get("between_kind_spread")
    if isinstance(bks, (int, float)):
        if bks < 0.15:
            kinterp = "uniform across storefront types (generalist)"
        elif bks < 0.35:
            kinterp = "somewhat type-dependent"
        else:
            kinterp = "type-specialized — an overall number hides which storefront types work"
        out.append(f"    between-archetype spread {bks:.2f} — {kinterp}")

    spread = summary.get("cross_task_spread")
    if isinstance(spread, (int, float)):
        # 0 = identical across intents; higher = readiness is intent-dependent
        # and the best single run overstates it.
        if spread < 0.15:
            interp = "consistent across intents"
        elif spread < 0.35:
            interp = "somewhat intent-dependent"
        else:
            interp = "strongly intent-dependent — single-task scores overstate readiness"
        out.append(f"    cross-task spread {spread:.2f} — {interp}")
    else:
        out.append("    cross-task spread: n/a (fewer than 1 intent observed)")
    return out


def _quotability_lines(report) -> list[str]:
    """One-line 'is this number quotable?' verdict under the header.

    Reads the same runs the score used; the classification lives in
    :mod:`asrs.reliability`. Prints nothing for a not-scorable report — that
    header already says NOT SCORABLE, and a second 'no number to quote' line
    would be noise.
    """
    from .reliability import quotability  # lazy: keep report import light

    q = quotability(report)
    if q.tag == "not-scorable":
        return []
    tag = "CITABLE" if q.quotable else "PROVISIONAL"
    return [f"  QUOTABILITY: {tag} ({q.tag}) — {q.reason}"]


def _reliability_lines(runs) -> list[str]:
    """Within-panel verdict reproducibility over the valid shopper runs.

    A diagnostic view, not a score input: how much did the panel's runs agree
    when pointed at the same task? A high-delta number built on runs that flip
    between trials is overstated confidence, and this section makes that visible.
    Rendered from the same runs; the pure metric lives in :mod:`asrs.reliability`.
    """
    from .reliability import panel_reliability  # lazy: keep report import light

    rel = panel_reliability(runs)
    out = ["", "  PANEL RELIABILITY (do the runs reproduce on the same task?)"]
    if rel.single_trial:
        if rel.valid_runs == 0:
            out.append("    no valid runs — nothing observed to assess.")
        else:
            out.append(
                "    single trial (1 valid run) — reproducibility NOT assessed; "
                "re-run with --trials>=2 to quote."
            )
        return out

    out.append(
        f"    verdict stability {rel.verdict_stability:.2f} ({rel.label}) over "
        f"{rel.valid_runs} valid runs   [1.0 = every run agreed]"
    )
    if rel.flipped_checkpoints:
        out.append(
            "    flipped between runs: " + ", ".join(rel.flipped_checkpoints)
        )
    else:
        out.append("    all checkpoints unanimous across runs.")
    if rel.trust_events_unanimous is False:
        out.append(
            f"    trust signal flipped (agreement {rel.trust_event_agreement:.2f}) "
            "— some runs raised a trust concern, others did not."
        )
    return out


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

    def _overall_str(rep) -> str:
        if getattr(rep, "scored", True) and rep.overall_score is not None:
            return f"{rep.overall_score:.1f} ({rep.grade or '?'})"
        return "n/a (not scorable)"

    a_ok = getattr(a, "scored", True) and a.overall_score is not None
    b_ok = getattr(b, "scored", True) and b.overall_score is not None

    lines.append(_rule("="))
    lines.append("  ASRS DELTA")
    lines.append(
        f"  {label_a} {a.domain} = {_overall_str(a)}"
        f"  ->  {label_b} {b.domain} = {_overall_str(b)}"
    )
    if a_ok and b_ok:
        # A delta is only meaningful between two scored domains.
        lines.append(f"  (delta {b.overall_score - a.overall_score:+.1f})")
    else:
        lines.append("  (delta n/a — a side was not scorable)")
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
        # The transactability DELTA is the headline of the with/without pitch —
        # qualify it, per side, with whether each side's LIVED payment
        # experience corroborates its static prediction (the SAME signal the
        # single card's sub-line reads, via _payment_corroboration_state_for).
        # So a reader can see the delta is behaviorally earned, not a static
        # artifact. Display-only; suppressed entirely when NEITHER side ran a
        # panel (the canonical static re-score) so static compares are unchanged.
        if pillar == "transactability":
            states = [
                (label_a, _payment_corroboration_state_for(a)),
                (label_b, _payment_corroboration_state_for(b)),
            ]
            if any(st is not None for _, st in states):
                for lbl, st in states:
                    if st is not None:
                        lines.append(
                            f"      {lbl} payment corroboration: "
                            f"{_PAYMENT_CORROB_TEXT[st]}"
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
