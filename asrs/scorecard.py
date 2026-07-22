"""HTML scorecard renderer — on-brand (ZeroClick design system).

Turns one or two saved report JSONs into a self-contained HTML scorecard:
scores, pillar breakdowns, recommendations, trust panel, behavioral
checkpoints — and, with two reports, the without/with delta hero.

Brand: zeroclick-ui tokens (monochrome ink; DM Sans display, Inter body,
DM Mono; color only for status). Values from packages/tokens + packages/css.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

PILLAR_LABELS = {
    "access": "Access",
    "legibility": "Legibility",
    "transactability": "Transactability",
    "trust": "Agent Trust",
    "outcome": "Outcome",
}
PILLAR_QUESTIONS = {
    "access": "Can an agent get in?",
    "legibility": "Can an agent understand the offer?",
    "transactability": "Can an agent pay programmatically?",
    "trust": "Will an agent believe it's legitimate?",
    "outcome": "Did shopper agents get the job done?",
}
CHECKPOINT_LABELS = [
    ("found_product", "Found product"),
    ("understood_pricing", "Understood pricing"),
    ("found_purchase_path", "Purchase path"),
    ("machine_payable_path", "Machine-payable"),
    ("no_human_gate", "No human gate"),
]
CAP_EXPLANATIONS = {
    "agent-ua-hard-blocked": "A bot wall blocks agent user-agents while browsers pass.",
    "no-https": "The site does not serve valid HTTPS.",
    "trust-panel-refusal": "A panel model confidently refused to transact here on a user's behalf.",
    "human-gate-required": "Purchase is impossible without a human-only step.",
}

ZERO_MARK = (
    '<svg viewBox="0 0 364 364" fill="none" xmlns="http://www.w3.org/2000/svg" class="mark">'
    '<path d="M329.494 27.2427C318.43 16.1787 305.406 7.85613 290.995 2.17837C347.418 58.7853 '
    "329.345 168.447 250.575 247.218C171.747 326.045 61.9843 344.087 5.41306 287.516C2.91376 "
    "285.017 0.560893 282.413 -1.64834 279.713C3.79266 298.637 13.3585 315.61 27.2429 329.494C"
    "86.5964 388.848 202.374 369.302 285.838 285.837C369.302 202.373 388.848 86.596 329.494 "
    "27.2427ZM262.329 47.3952C223.378 8.44495 143.687 24.9832 84.3349 84.3354C24.9825 143.688 "
    "8.44439 223.379 47.3948 262.329C65.4145 280.349 92.153 286.491 121.564 282.014C113.326 "
    "278.633 105.844 273.767 99.4444 267.368C65.1311 233.054 74.9035 167.647 121.272 121.278C"
    "167.641 74.9094 233.049 65.1364 267.362 99.4498C273.764 105.851 278.631 113.335 282.012 "
    '121.575C286.492 92.1604 280.351 65.417 262.329 47.3952Z" fill="currentColor"/></svg>'
)

CSS = """
:root{
  --text-primary:#141414;--text-secondary:#424242;--text-tertiary:#525252;
  --text-quaternary:#737373;--bg-primary:#ffffff;--bg-secondary:#f7f7f7;
  --bg-subtle:#fcfcfc;--bg-quaternary:#e5e5e5;--border-primary:#d6d6d6;
  --border-secondary:#e5e5e5;--ink:#000000;--ink-soft:#404040;
  --success:#079455;--success-bg:#ecfdf3;--success-dot:#17b26a;
  --warning:#dc6803;--warning-bg:#fffaeb;--warning-dot:#f79009;
  --error:#d92d20;--error-bg:#fef3f2;--error-dot:#f04438;
  --font-display:"DM Sans",sans-serif;--font-body:"Inter",sans-serif;
  --font-mono:"DM Mono",monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg-secondary);color:var(--text-primary);
  font-family:var(--font-body);font-size:14px;line-height:20px;
  -webkit-font-smoothing:antialiased}
.page{max-width:1280px;margin:0 auto;padding:32px;display:flex;
  flex-direction:column;gap:24px}
.num{font-variant-numeric:tabular-nums}
h1,h2,h3{font-family:var(--font-display);margin:0}
.masthead{display:flex;align-items:center;gap:16px}
.mark{width:36px;height:36px;color:var(--text-primary);flex:none}
.masthead h1{font-size:24px;line-height:32px;font-weight:600}
.masthead .sub{color:var(--text-quaternary);font-size:14px;margin-top:2px}
.card{background:var(--bg-primary);border:1px solid var(--border-secondary);
  border-radius:12px}
.card-header{padding:20px 24px;border-bottom:1px solid var(--border-secondary);
  display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.card-header h2{font-size:16px;line-height:21px;font-weight:600}
.card-header .desc{color:var(--text-tertiary);font-size:14px;margin-top:2px}
.card-body{padding:24px}
.hero{display:grid;grid-template-columns:1fr auto 1fr;gap:24px;
  align-items:center;padding:32px 24px}
.hero.single{grid-template-columns:1fr}
.scorebox{text-align:center;display:flex;flex-direction:column;gap:6px}
.scorebox .label{font-size:12px;font-weight:600;letter-spacing:.06em;
  text-transform:uppercase;color:var(--text-quaternary)}
.scorebox .domain{font-family:var(--font-mono);font-size:15px;
  color:var(--text-secondary)}
.score-lockup{display:flex;align-items:baseline;justify-content:center;gap:12px}
.score-lockup .value{font-family:var(--font-display);font-weight:600;
  font-size:60px;line-height:1;letter-spacing:-.02em}
.score-lockup .of{color:var(--text-quaternary);font-size:14px}
.delta-arrow{display:flex;flex-direction:column;align-items:center;gap:8px;
  color:var(--text-quaternary);font-size:24px}
.pill{display:inline-flex;align-items:center;gap:6px;border-radius:9999px;
  min-height:24px;padding:0 10px;font-size:13px;font-weight:600;
  font-family:var(--font-display)}
.pill .dot{width:6px;height:6px;border-radius:9999px}
.pill.good{background:var(--success-bg);color:var(--success);
  box-shadow:inset 0 0 0 1px #a6f4c5}.pill.good .dot{background:var(--success-dot)}
.pill.warn{background:var(--warning-bg);color:var(--warning);
  box-shadow:inset 0 0 0 1px #fedf89}.pill.warn .dot{background:var(--warning-dot)}
.pill.bad{background:var(--error-bg);color:var(--error);
  box-shadow:inset 0 0 0 1px #fda29b}.pill.bad .dot{background:var(--error-dot)}
.pill.neutral{background:var(--bg-secondary);color:var(--text-secondary);
  box-shadow:inset 0 0 0 1px var(--border-secondary)}
.chip{font-family:var(--font-mono);font-size:12px;background:var(--bg-secondary);
  box-shadow:inset 0 0 0 1px var(--border-secondary);border-radius:6px;
  padding:2px 8px;color:var(--text-secondary);white-space:nowrap}
.alert{display:flex;gap:12px;padding:14px 16px;border-radius:12px;
  background:var(--error-bg);box-shadow:inset 0 0 0 1px #fda29b;
  color:var(--text-primary)}
.alert .icon{color:var(--error);font-weight:700;font-family:var(--font-display)}
.alert b{font-family:var(--font-display)}
.pillars{display:flex;flex-direction:column;gap:14px}
.pillar-row{display:grid;grid-template-columns:150px 1fr 52px;gap:12px;
  align-items:center}
.pillar-row .name{font-weight:500;color:var(--text-secondary)}
.pillar-row .name small{display:block;font-weight:400;font-size:12px;
  color:var(--text-quaternary)}
.track{background:var(--bg-quaternary);border-radius:9999px;height:8px;
  overflow:hidden}
.fill{height:100%;border-radius:9999px}
.fill.good{background:var(--success)}.fill.warn{background:var(--warning)}
.fill.bad{background:var(--error)}.fill.na{background:transparent}
.pillar-row .val{text-align:right;font-weight:600;font-family:var(--font-display)}
.pillar-row .val.na{color:var(--text-quaternary);font-weight:400}
table{width:100%;border-collapse:collapse}
th{font-size:12px;font-weight:600;color:var(--text-quaternary);text-align:left;
  padding:10px 16px;border-bottom:1px solid var(--border-secondary)}
td{font-size:14px;color:var(--text-tertiary);padding:12px 16px;
  border-bottom:1px solid var(--border-secondary);vertical-align:top}
tr:last-child td{border-bottom:none}
td.impact{font-family:var(--font-display);font-weight:600;white-space:nowrap;
  color:var(--error)}
td.impact.minor{color:var(--warning)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}
.stack{display:flex;flex-direction:column;gap:24px;min-width:0}
.verdict{display:flex;flex-direction:column;gap:8px;padding:14px 16px;
  border:1px solid var(--border-secondary);border-radius:12px}
.verdict .head{display:flex;align-items:center;gap:10px}
.verdict .model{font-family:var(--font-mono);font-size:13px;
  color:var(--text-primary)}
.verdict ul{margin:0;padding-left:18px;color:var(--text-tertiary);
  font-size:13px;line-height:19px;display:flex;flex-direction:column;gap:4px}
.verdicts{display:flex;flex-direction:column;gap:12px}
.checks td,.checks th{text-align:center;padding:10px 8px}
.checks td:first-child,.checks th:first-child{text-align:left;
  font-family:var(--font-mono);font-size:13px}
.mini-dot{display:inline-block;width:10px;height:10px;border-radius:9999px}
.mini-dot.y{background:var(--success-dot)}
.mini-dot.n{background:var(--error-dot)}
.mini-dot.skip{background:var(--bg-quaternary)}
.blockers{margin:4px 0 0;padding-left:18px;font-size:13px;line-height:19px;
  color:var(--text-quaternary)}
.deltas{display:flex;flex-direction:column;gap:10px;max-width:560px}
.delta-line.head{border-bottom:1px solid var(--border-secondary);
  padding-bottom:8px}
.delta-line.head .n,.delta-line.head .d{font-family:var(--font-mono);
  font-size:11px;color:var(--text-quaternary);font-weight:400}
.delta-line{display:grid;grid-template-columns:1fr auto auto auto;gap:10px;
  align-items:center;font-size:13px}
.delta-line .p{color:var(--text-secondary)}
.delta-line .n{font-family:var(--font-display);font-weight:600;text-align:right;
  min-width:38px}
.delta-line .d{min-width:52px;text-align:right;font-weight:600;
  font-family:var(--font-display)}
.d.up{color:var(--success)}.d.down{color:var(--error)}.d.flat{color:var(--text-quaternary)}
footer{color:var(--text-quaternary);font-size:12px;line-height:18px;
  padding:0 4px 16px}
details summary{cursor:pointer;color:var(--text-quaternary);font-size:13px;
  padding:10px 16px}
@media (max-width:900px){.grid2{grid-template-columns:1fr}
  .hero{grid-template-columns:1fr;gap:16px}
  .delta-arrow{transform:rotate(90deg)}}
"""


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _band(score: float | None) -> str:
    if score is None:
        return "na"
    return "good" if score >= 80 else ("warn" if score >= 60 else "bad")


def _grade_pill(grade: str) -> str:
    cls = "good" if grade in ("A+", "A", "B") else ("warn" if grade == "C" else "bad")
    return f'<span class="pill {cls}"><span class="dot"></span>Grade {_esc(grade)}</span>'


def _score_box(rep: dict, label: str | None) -> str:
    label_html = f'<div class="label">{_esc(label)}</div>' if label else ""
    return (
        f'<div class="scorebox">{label_html}'
        f'<div class="domain">{_esc(rep["domain"])}</div>'
        f'<div class="score-lockup"><span class="value num">{rep["overall_score"]:.0f}</span>'
        f'<span class="of">/ 100</span></div>'
        f"<div>{_grade_pill(rep['grade'])}</div></div>"
    )


def _hero(reports: list[dict], labels: list[str | None]) -> str:
    if len(reports) == 1:
        return f'<div class="card"><div class="hero single">{_score_box(reports[0], labels[0])}</div></div>'
    a, b = reports
    d = b["overall_score"] - a["overall_score"]
    dcls = "up" if d > 0 else ("down" if d < 0 else "flat")
    lines = [
        '<div class="delta-line head"><span class="p"></span>'
        f'<span class="n">{_esc(a["domain"])}</span>'
        f'<span class="n">{_esc(b["domain"])}</span>'
        '<span class="d">&Delta;</span></div>'
    ]
    for p in PILLAR_LABELS:
        sa, sb = a["pillar_scores"].get(p), b["pillar_scores"].get(p)
        if sa is None and sb is None:
            continue
        pd = (sb or 0) - (sa or 0)
        pcls = "up" if pd > 0 else ("down" if pd < 0 else "flat")
        lines.append(
            f'<div class="delta-line"><span class="p">{PILLAR_LABELS[p]}</span>'
            f'<span class="n num">{"—" if sa is None else f"{sa:.0f}"}</span>'
            f'<span class="n num">{"—" if sb is None else f"{sb:.0f}"}</span>'
            f'<span class="d num {pcls}">{pd:+.0f}</span></div>'
        )
    return (
        '<div class="card"><div class="hero">'
        + _score_box(a, labels[0] or "Without")
        + f'<div class="delta-arrow"><span>&#8594;</span>'
        f'<span class="pill {"good" if d > 0 else "bad" if d < 0 else "neutral"}">'
        f'<span class="dot"></span><span class="num">{d:+.1f}</span></span></div>'
        + _score_box(b, labels[1] or "With")
        + "</div>"
        + '<div class="card-body" style="border-top:1px solid var(--border-secondary)">'
        + '<div class="deltas">'
        + "".join(lines)
        + "</div></div></div>"
    )


def _caps_alerts(rep: dict) -> str:
    out = []
    for slug in rep.get("caps_applied", []):
        why = CAP_EXPLANATIONS.get(slug, "")
        out.append(
            f'<div class="alert"><span class="icon">!</span><div>'
            f"<b>Grade capped</b> by <span class=\"chip\">{_esc(slug)}</span> — {_esc(why)}"
            "</div></div>"
        )
    return "".join(out)


def _pillars(rep: dict) -> str:
    rows = []
    for p, label in PILLAR_LABELS.items():
        s = rep["pillar_scores"].get(p)
        band = _band(s)
        width = 0 if s is None else max(2, round(s))
        val = '<span class="val na">n/a</span>' if s is None else f'<span class="val num">{s:.0f}</span>'
        rows.append(
            f'<div class="pillar-row"><span class="name">{label}'
            f"<small>{PILLAR_QUESTIONS[p]}</small></span>"
            f'<div class="track"><div class="fill {band}" style="width:{width}%"></div></div>{val}</div>'
        )
    return f'<div class="pillars">{"".join(rows)}</div>'


def _recommendations(rep: dict, fold_after: int = 7) -> str:
    items = [
        c
        for c in rep["checks"]
        if c["status"] in ("fail", "partial") and (c["max_points"] - c["points"]) > 0
    ]
    items.sort(key=lambda c: c["max_points"] - c["points"], reverse=True)
    if not items:
        return '<div class="card-body">No open recommendations — all applicable checks passed.</div>'

    def row(c):
        lost = c["max_points"] - c["points"]
        minor = " minor" if lost < 3 else ""
        return (
            f'<tr><td class="impact num{minor}">&minus;{lost:g} pts</td>'
            f'<td><span class="chip">{_esc(c["finding"])}</span></td>'
            f"<td>{_esc(c['remediation'])}</td></tr>"
        )

    head = "<tr><th>Impact</th><th>Finding</th><th>Recommendation</th></tr>"
    top = "".join(row(c) for c in items[:fold_after])
    rest = items[fold_after:]
    fold = ""
    if rest:
        fold = (
            f"<details><summary>{len(rest)} more lower-impact recommendation"
            f'{"s" if len(rest) > 1 else ""}</summary><table>'
            + "".join(row(c) for c in rest)
            + "</table></details>"
        )
    return f"<table>{head}{top}</table>{fold}"


def _trust_panel(rep: dict) -> str:
    panel = rep.get("trust_panel") or []
    if not panel:
        return ""
    cards = []
    # Three-way directive verdict (rubric v0.2); pre-v0.2 reports carry only
    # the boolean, which maps to the two outer states.
    decisions = {
        "proceed": ("good", "Proceeds as directed"),
        "proceed_with_warning": ("warn", "Proceeds, warns the user"),
        "refuse": ("bad", "Refuses despite directive"),
    }
    for v in panel:
        decision = v.get("decision") or ("proceed" if v.get("willing") else "refuse")
        cls, label = decisions.get(decision, ("neutral", _esc(decision)))
        pill = (
            f'<span class="pill {cls}"><span class="dot"></span>'
            f'{label}'
            f'&nbsp;·&nbsp;<span class="num">{v["confidence"]:.2f}</span></span>'
        )
        concerns = "".join(f"<li>{_esc(c)}</li>" for c in v.get("concerns", [])[:4])
        cards.append(
            f'<div class="verdict"><div class="head"><span class="model">{_esc(v["model"])}</span>{pill}</div>'
            + (f"<ul>{concerns}</ul>" if concerns else "")
            + "</div>"
        )
    return (
        '<div class="card"><div class="card-header"><div><h2>Agent trust panel</h2>'
        '<div class="desc">The user has directed the purchase — does this model '
        "proceed, warn, or refuse?</div></div></div>"
        f'<div class="card-body"><div class="verdicts">{"".join(cards)}</div></div></div>'
    )


def _checkpoints(rep: dict) -> str:
    runs = rep.get("behavioral_runs") or []
    valid = [r for r in runs if r.get("checkpoints")]
    if not runs:
        return ""
    header = "<tr><th>Shopper run</th>" + "".join(
        f"<th>{label}</th>" for _, label in CHECKPOINT_LABELS
    ) + "</tr>"
    rows, notes = [], []
    for r in runs:
        cells = []
        for key, _ in CHECKPOINT_LABELS:
            if not r.get("checkpoints"):
                cells.append('<td><span class="mini-dot skip" title="run failed"></span></td>')
            else:
                ok = r["checkpoints"].get(key)
                cells.append(
                    f'<td><span class="mini-dot {"y" if ok else "n"}" '
                    f'title="{"pass" if ok else "fail"}"></span></td>'
                )
        rows.append(f'<tr><td>{_esc(r["model"])}&nbsp;#{r["trial"]}</td>{"".join(cells)}</tr>')
        if r.get("blockers"):
            items = "".join(f"<li>{_esc(b)}</li>" for b in r["blockers"][:3])
            notes.append(
                f'<div style="padding:0 16px 12px"><span class="chip">{_esc(r["model"])}&nbsp;#{r["trial"]}'
                f" blockers</span><ul class=\"blockers\">{items}</ul></div>"
            )
    legend = (
        '<div class="desc">Read-only recon runs. '
        '<span class="mini-dot y"></span> pass &nbsp;<span class="mini-dot n"></span> fail'
        + (' &nbsp;<span class="mini-dot skip"></span> run failed (excluded)' if len(valid) < len(runs) else "")
        + "</div>"
    )
    return (
        '<div class="card"><div class="card-header"><div><h2>Behavioral checkpoints</h2>'
        + legend
        + "</div></div>"
        f'<table class="checks">{header}{"".join(rows)}</table>{"".join(notes)}</div>'
    )


def _domain_column(rep: dict, label: str | None) -> str:
    title = f'{_esc(rep["domain"])}'
    sub = f'{_esc(label)} · scored {rep["generated_at"][:10]}' if label else f'scored {rep["generated_at"][:10]}'
    caps = _caps_alerts(rep)
    return (
        '<div class="stack">'
        f'<div class="card"><div class="card-header"><div><h2>{title}</h2>'
        f'<div class="desc">{sub}</div></div>{_grade_pill(rep["grade"])}</div>'
        '<div class="card-body" style="display:flex;flex-direction:column;gap:16px">'
        + caps
        + _pillars(rep)
        + "</div></div>"
        + f'<div class="card"><div class="card-header"><div><h2>Recommendations</h2>'
        f'<div class="desc">Sorted by score impact — each finding names its fix.</div></div></div>'
        + _recommendations(rep)
        + "</div>"
        + _trust_panel(rep)
        + _checkpoints(rep)
        + "</div>"
    )


def build_scorecard(
    report_paths: list[str],
    labels: list[str | None] | None = None,
    out_path: str | None = None,
) -> str:
    reports = [json.loads(Path(p).read_text()) for p in report_paths]
    labels = (labels or [None] * len(reports))[: len(reports)]
    while len(labels) < len(reports):
        labels.append(None)

    if len(reports) == 2:
        columns = f'<div class="grid2">{_domain_column(reports[0], labels[0])}{_domain_column(reports[1], labels[1])}</div>'
        title = f'{reports[0]["domain"]} vs {reports[1]["domain"]}'
    else:
        columns = _domain_column(reports[0], labels[0])
        title = reports[0]["domain"]

    rv = reports[0]["rubric_version"]
    gen = reports[0]["generated_at"][:16].replace("T", " ")
    models = sorted({v["model"] for r in reports for v in (r.get("trust_panel") or [])})
    panel_note = f' Behavioral panel: {", ".join(models)}.' if models else ""
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic Readiness Scorecard — {_esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><div class="page">
<div class="masthead">{ZERO_MARK}<div><h1>Agentic Readiness Scorecard</h1>
<div class="sub">ZeroClick · rubric v{_esc(rv)} · {_esc(gen)} UTC</div></div></div>
{_hero(reports, labels)}
{columns}
<footer>ASRS rubric v{_esc(rv)} — scores are comparable only within a rubric
version. Grade caps apply for critical failures regardless of points.
Pillar scores exclude checks that could not be tested.{_esc(panel_note)}</footer>
</div></body></html>"""

    if out_path is None:
        out_path = str(Path("runs") / f"scorecard_{'_vs_'.join(r['domain'].replace('.', '_') for r in reports)}.html")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(doc)
    return out_path
