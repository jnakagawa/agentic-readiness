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
import re
from datetime import datetime, timezone
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


def _cap_anchor(slug: str) -> str:
    """The methodology-page fragment id for a cap slug. ONE source of truth so
    the card's "Grade capped" link and the methodology cap-row id can never
    drift: the methodology row sets ``id=_cap_anchor(slug)`` and the card links
    to ``methodology.html#{_cap_anchor(slug)}``. Slug is lowercased and any
    non-alphanumeric run collapses to a single '-' so a future odd slug still
    yields a valid, matching anchor on both sides."""
    frag = re.sub(r"[^a-z0-9]+", "-", str(slug).lower()).strip("-")
    return f"cap-{frag}"

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
.page{max-width:none;margin:0 auto;padding:32px;display:flex;
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
  padding:2px 8px;color:var(--text-secondary);display:inline-block;
  overflow-wrap:anywhere;max-width:100%;box-sizing:border-box;text-decoration:none}
a.chip:hover{box-shadow:inset 0 0 0 1px var(--text-tertiary);color:var(--text-primary)}
.chip.na{color:var(--text-quaternary);opacity:.7;background:transparent}
.chip-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:4px}
.alert{display:flex;gap:12px;padding:14px 16px;border-radius:12px;
  background:var(--error-bg);box-shadow:inset 0 0 0 1px #fda29b;
  color:var(--text-primary)}
.alert .icon{color:var(--error);font-weight:700;font-family:var(--font-display)}
.alert b{font-family:var(--font-display)}
.pillars{display:flex;flex-direction:column;gap:14px}
.pillar-row{display:grid;grid-template-columns:150px 1fr 52px;gap:12px;
  align-items:center}
.pillar-row.wd{grid-template-columns:150px 1fr 52px 52px}
.pillar-row .name{font-weight:500;color:var(--text-secondary)}
.pillar-row .name small{display:block;font-weight:400;font-size:12px;
  color:var(--text-quaternary)}
.pillar-row .name small.earner{color:var(--text-tertiary);margin-top:2px}
.pillar-row .name small.earner b{font-weight:600;color:var(--text-secondary)}
.pillar-row .name small.corrob{display:inline-block;margin-top:4px;font-weight:600;
  font-size:11px;padding:1px 8px;border-radius:9999px}
.pillar-row .name small.corrob.good{background:var(--success-bg);color:var(--success);
  box-shadow:inset 0 0 0 1px #a6f4c5}
.pillar-row .name small.corrob.warn{background:var(--warning-bg);color:var(--warning);
  box-shadow:inset 0 0 0 1px #fedf89}
.pillar-row .name small.corrob.neutral{background:var(--bg-secondary);
  color:var(--text-secondary);box-shadow:inset 0 0 0 1px var(--border-secondary)}
/* Compare mode only: the baseline side's corroboration, shown alongside this
   card's own so the transactability DELTA is self-contained. Kept visually
   secondary (dimmed, offset) — it qualifies the delta's anchor, it is not this
   side's own verdict. */
.pillar-row .name small.corrob.baseline{opacity:.72;margin-left:6px}
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
  border-bottom:1px solid var(--border-secondary);vertical-align:top;
  overflow-wrap:break-word}
tr:last-child td{border-bottom:none}
td.impact{font-family:var(--font-display);font-weight:600;white-space:nowrap;
  color:var(--error)}
td.impact.minor{color:var(--warning)}
td.pillar-tag{font-size:12px;white-space:nowrap}
.ptag{display:inline-block;font:500 12px/18px Inter,sans-serif;
  padding:2px 10px;border-radius:9999px}
.ptag.access{background:#eff8ff;color:#175cd3;box-shadow:inset 0 0 0 1px #b2ddff}
.ptag.legibility{background:#f9f5ff;color:#6941c6;box-shadow:inset 0 0 0 1px #e9d7fe}
.ptag.transactability{background:#f0fdf9;color:#107569;box-shadow:inset 0 0 0 1px #99f6e0}
.ptag.trust{background:#fdf2fa;color:#c11574;box-shadow:inset 0 0 0 1px #fcceee}
.ptag.outcome{background:#eef4ff;color:#3538cd;box-shadow:inset 0 0 0 1px #c7d7fe}
table.recs{table-layout:fixed}
table.recs th:nth-child(1){width:62px}
table.recs th:nth-child(2){width:130px}
table.recs th:nth-child(3){width:26%}
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
table.checks{display:block;overflow-x:auto}
.checks td,.checks th{text-align:center;padding:10px 8px}
.checks td:first-child,.checks th:first-child{text-align:left;
  font-family:var(--font-mono);font-size:13px}
.mini-dot{display:inline-block;width:10px;height:10px;border-radius:9999px}
.mini-dot.y{background:var(--success-dot)}
.mini-dot.n{background:var(--error-dot)}
.mini-dot.skip{background:var(--bg-quaternary)}
.blockers{margin:4px 0 0;padding-left:18px;font-size:13px;line-height:19px;
  color:var(--text-quaternary)}
.pillar-row .d{text-align:right;font-weight:600;font-family:var(--font-display);
  font-size:13px}
.d.up{color:var(--success)}.d.down{color:var(--error)}.d.flat{color:var(--text-quaternary)}
footer{color:var(--text-quaternary);font-size:12px;line-height:18px;
  padding:0 4px 16px}
footer a{color:var(--text-secondary)}
details summary{cursor:pointer;color:var(--text-quaternary);font-size:13px;
  padding:10px 16px}
@media (max-width:900px){.grid2{grid-template-columns:1fr}
  .hero{grid-template-columns:1fr;gap:16px}
  .delta-arrow{transform:rotate(90deg)}}
"""


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _write_rubric_page(out_dir: Path) -> str:
    """Render the bundled rubric YAML as rubric.html next to the card.

    The YAML's changelog comments ARE the scoring-logic documentation, so the
    page shows a short orientation followed by the rubric verbatim.
    """
    from .scoring import DEFAULT_RUBRIC_PATH, load_rubric

    yaml_text = Path(DEFAULT_RUBRIC_PATH).read_text()
    version = load_rubric().get("version", "")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ASRS rubric v{_esc(version)} — scoring logic</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--text-primary:#0c111d;--text-secondary:#475467;--text-tertiary:#667085;
--border:#e5e5e5;--bg:#fafafa}}
body{{margin:0;background:var(--bg);color:var(--text-primary);
font:400 15px/23px Inter,sans-serif}}
.wrap{{max-width:860px;margin:0 auto;padding:40px 20px}}
h1{{font:700 24px/30px "DM Sans",sans-serif;margin:0 0 6px}}
.sub{{color:var(--text-secondary);margin:0 0 24px}}
.card{{background:#fff;border:1px solid var(--border);border-radius:12px;
padding:20px 24px;margin-bottom:20px}}
h2{{font:600 16px/22px "DM Sans",sans-serif;margin:0 0 8px}}
p{{margin:0 0 10px;color:var(--text-secondary)}}
pre{{font:400 12px/19px "DM Mono",monospace;white-space:pre-wrap;
overflow-wrap:anywhere;background:#fff;border:1px solid var(--border);
border-radius:12px;padding:20px 24px;margin:0}}
a{{color:var(--text-secondary)}}
</style></head><body><div class="wrap">
<h1>ASRS — Agentic Selling Readiness Score</h1>
<p class="sub">Rubric v{_esc(version)} · how the score works</p>
<div class="card">
<h2>Reading a score</h2>
<p>Five pillars, each scored 0&ndash;100 from named checks, then combined by
the pillar weights below. Checks that could not be tested shrink their
pillar&rsquo;s denominator &mdash; a site is never punished for what
couldn&rsquo;t be observed. Critical failures cap the letter grade regardless
of points. Scores are comparable only within a rubric version.</p>
<p>Static checks probe the site directly; BEHAVIORAL checks come from live
shopper and trust panels (headless agents working the site under a user
directive), including one real zero-value free-tier transaction where the
site advertises an allowance.</p>
</div>
<p class="sub" style="margin:-14px 0 24px"><a href="methodology.html">New here? Read how the score is measured &rarr;</a></p>
<h2 style="margin:0 0 10px">The rubric, verbatim</h2>
<pre>{html.escape(yaml_text)}</pre>
<p class="sub" style="margin-top:16px"><a href="javascript:history.back()">&larr; back to the scorecard</a></p>
</div></body></html>"""
    path = out_dir / "rubric.html"
    path.write_text(doc)
    return str(path)


# Shared shell for the two prose pages (rubric + methodology) so they read as
# siblings. Kept minimal and self-contained — same look as _write_rubric_page.
_PROSE_HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--text-primary:#0c111d;--text-secondary:#475467;--text-tertiary:#667085;
--border:#e5e5e5;--bg:#fafafa}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text-primary);
font:400 15px/23px Inter,sans-serif}}
.wrap{{max-width:860px;margin:0 auto;padding:40px 20px}}
h1{{font:700 24px/30px "DM Sans",sans-serif;margin:0 0 6px}}
.sub{{color:var(--text-secondary);margin:0 0 24px}}
.card{{background:#fff;border:1px solid var(--border);border-radius:12px;
padding:20px 24px;margin-bottom:20px}}
h2{{font:600 16px/22px "DM Sans",sans-serif;margin:0 0 8px}}
h2 .n{{color:var(--text-tertiary);font-weight:500;margin-right:8px}}
p{{margin:0 0 10px;color:var(--text-secondary)}}
p:last-child{{margin-bottom:0}}
h3{{font:600 14px/20px "DM Sans",sans-serif;margin:16px 0 6px;color:var(--text-primary)}}
ul{{margin:0 0 10px;padding-left:20px;color:var(--text-secondary)}}
li{{margin:0 0 6px}}
li:last-child{{margin-bottom:0}}
b{{color:var(--text-primary)}}
table{{width:100%;border-collapse:collapse;margin:4px 0 2px}}
td,th{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--border);
vertical-align:top}}
td.num{{text-align:right;font:500 14px/20px "DM Mono",monospace;white-space:nowrap}}
.q{{color:var(--text-tertiary);font-size:13px;line-height:18px}}
.chip{{font:500 12px/18px "DM Mono",monospace;background:#f2f4f7;
border-radius:6px;padding:1px 7px;color:var(--text-secondary)}}
a{{color:var(--text-secondary)}}
.nav{{margin:0 0 20px;font-size:14px}}
.nav a{{margin-right:14px}}
</style></head><body><div class="wrap">"""


def _write_methodology_page(out_dir: Path) -> str:
    """Render methodology.html — the "read the paper" page behind the rubric.

    The rubric page shows WHAT is scored (checks + weights, the YAML verbatim).
    This page explains the MEASUREMENT SEMANTICS a critic needs before trusting
    the number: the capability lens, how pillars aggregate and renormalize, the
    difference between a check that FAILS and one that CANT_TEST, NOT SCORABLE
    vs an F grade, attribution honesty (agent-side vs site-side blocks), how the
    behavioral panels and refusal semantics work, reproducibility (trials /
    verdict stability / quotability), the grade caps, and the $0 free-tier probe.

    Pillar weights, caps, and grade bands are pulled LIVE from the loaded rubric
    so the page can never drift from the scoring it documents — a version bump
    reflows this page automatically. Display-only; no scoring semantics here.
    """
    from .scoring import load_rubric

    rubric = load_rubric()
    version = rubric.get("version", "")
    weights = rubric.get("pillar_weights", {})
    caps = rubric.get("caps", {})
    bands = rubric.get("grade_bands", [])

    def grade_for(score: float) -> str:
        for lb, g in bands:
            if score >= lb:
                return g
        return "F"

    pillar_rows = "".join(
        f'<tr><td><b>{_esc(PILLAR_LABELS.get(p, p))}</b>'
        f'<div class="q">{_esc(PILLAR_QUESTIONS.get(p, ""))}</div></td>'
        f'<td class="num">{w:.0%}</td></tr>'
        for p, w in sorted(weights.items(), key=lambda kv: -kv[1])
    )
    cap_rows = "".join(
        f'<tr id="{_cap_anchor(slug)}"><td><span class="chip">{_esc(slug)}</span></td>'
        f'<td class="num">&le; {_esc(limit)} &middot; max {_esc(grade_for(limit))}</td>'
        f'<td>{_esc(CAP_EXPLANATIONS.get(slug, ""))}</td></tr>'
        for slug, limit in caps.items()
    )
    band_str = " &middot; ".join(f"{_esc(g)}&nbsp;&ge;&nbsp;{_esc(lb)}" for lb, g in bands)

    head = _PROSE_HEAD.format(
        title=f"ASRS methodology — how the score is measured (v{_esc(version)})"
    )
    body = f"""
<div class="nav"><a href="javascript:history.back()">&larr; Back to the scorecard</a>
<a href="rubric.html">Rubric &amp; checks</a></div>
<h1>How ASRS measures agentic selling readiness</h1>
<p class="sub">Methodology behind the number &middot; rubric v{_esc(version)}</p>

<div class="card">
<h2>What the score answers</h2>
<p>ASRS asks one question: <b>can an AI agent, acting for a person, actually
sell-side interact with this storefront &mdash; reach it, understand the offer,
pay programmatically, provision without a human, and finish the job?</b>
Every check is worded by <b>capability</b>, never by vendor: no domain, product,
or payment brand is special-cased, favorable or hostile. An implementation
scores well only because it delivers those capabilities to an agent.</p>
<p><b>Agent-native payment</b> makes that neutrality concrete, because payment is
where a benchmark is most tempted to pick a winner. Paying programmatically is a
<b>capability</b>, not a rail: agentic commerce is standardizing on <b>several
open payment protocols</b> &mdash; x402, MPP, ACP, UCP and AP2 are open standards,
not any one vendor&rsquo;s product &mdash; and a with-rails storefront commonly
advertises <b>more than one</b> (for example an <code>x402 (Base&nbsp;USDC)</code>
rail alongside an <code>MPP (Tempo&nbsp;USDC)</code> one). ASRS recognizes a
declared rail by its <b>protocol and settlement structure</b> &mdash; a
<code>&quot;protocol&quot;</code> declaration, or a rail named with its on-chain
settlement asset &mdash; so every open rail is read on <b>equal terms</b> and none
is favored by name. Recognition keys on <b>what</b> a storefront declares, never
on <b>who</b> declares it: that property is pinned by an <b>executable regression
test</b> that relabels the storefront&rsquo;s identity end-to-end and confirms the
rail is still recognized, unchanged, with the vendor&rsquo;s name gone.</p>
<p><b>Executing the pay handshake</b> is the leg <b>between</b> having a rail and
getting a receipt, and it is where an agent that <b>can</b> pay still <b>stalls</b>:
the rails above say a rail <b>exists</b> &mdash; that the agent is <b>able</b> to pay
&mdash; but nothing there says <b>how the payment is driven as a request/response
sequence</b>. An agent that reads &ldquo;here is a <code>402</code>&rdquo; but is never
told to settle the challenge and retry with the proof attached has the rail and <b>no
sequence to run it</b> &mdash; it stops at the pay step. An offer that documents the
challenge-settle-retry handshake &mdash; an HTTP <code>402</code>
<b>payment challenge</b>, then <b>settle</b> it (sign the <b>zero-value
authorization</b>, or pay the priced <code>402</code>), then retry the request with the
payment proof attached &mdash; hands the agent the <b>exact round-trip</b> it must
perform, so it is more agent-completable than one that leaves the agent holding a rail
with no documented way to <b>drive it to a paid response</b>. The <b>settle</b> step is
where ASRS&rsquo;s own <b>$0-only</b> ethos lives: the signable step is a <b>zero-value
authorization</b>, never a nonzero charge. It is <b>distinct</b> from every neighbour:
the payment <b>rails</b> (x402, a machine-payable endpoint) say the agent <b>can
pay</b>; the <b>receipt</b> is the proof that comes <b>back after</b> a paid call; this
is the <b>flow in between that actually spends</b> &mdash; the <b>PAY-execution leg</b>,
not the pay <b>ability</b> before and not the <b>accounting</b> after. So ASRS reads the
documented handshake as part of understanding the metered offer, keyed on vendor-neutral
<b>challenge-response vocabulary</b> (an HTTP <code>402</code> payment challenge, <b>pay
and retry</b>, settle the challenge, retry with a payment / signed authorization / proof
attached), the same category of open convention as REST, GraphQL, OpenAPI or x402
&mdash; HTTP <code>402 Payment&nbsp;Required</code> is a standard status and
challenge-response is a universal auth pattern, never a vendor&rsquo;s product. The read
is <b>precision-guarded</b>: a <b>bare</b> <code>retry</code>, <code>402</code>,
<code>challenge</code> or <code>settle</code> word is <b>no signal</b> &mdash; a
<b>webhook redelivery</b> (&ldquo;we retry the webhook a few times&rdquo;), a generic
&ldquo;retry on failure&rdquo;, or a <code>402</code> merely <b>mentioned</b> without the
settle-and-retry sequence must never trip it &mdash; so the phrasing must show the
<b>co-occurrence</b> only the handshake produces: pay or settle a <code>402</code> or
challenge <b>and retry</b>, or retry with a payment / proof / signed authorization
attached. Recognition keys on the <b>handshake the offer documents, not who documents
it</b>: that property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the handshake is still recognized,
unchanged, with the vendor&rsquo;s name gone. This read is <b>diagnostic</b> &mdash; it
names whether the offer lets an agent <b>drive a payment challenge to a paid
response</b>, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Provisioning without a human</b> sits between paying and finishing, and it
is the leg an agent silently fails before it can do either: a metered API is only
callable by an agent that can <b>present the right credential</b>. Agent-native
offers hand that credential over open machine conventions &mdash; an HTTP
<code>Authorization: Bearer</code> header, an <code>X-API-Key</code> header or a
named API key, an OpenAPI <code>securityScheme</code> declaration, or an
<b>OAuth2</b> flow &mdash; standards for how a caller authenticates, not any one
vendor&rsquo;s login. An offer that <b>documents its auth scheme</b> is more
agent-completable than one that leaves the agent holding an endpoint it never
learns how to enter &mdash; so ASRS reads the credential scheme as part of
provisioning the offer, keyed on the vendor-neutral <b>access convention</b> (a
bearer token, an API key, an OpenAPI security scheme, OAuth2), the same category
of open convention as REST, GraphQL or OpenAPI. Recognition keys on the
<b>scheme, not the vendor</b>: that property is pinned by an <b>executable
regression test</b> that relabels the API&rsquo;s identity end-to-end and confirms
the auth scheme is still recognized, unchanged, with the vendor&rsquo;s name gone.
This read is <b>diagnostic</b> &mdash; it names how the offer is entered, <b>off
the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Onboarding without a human</b> comes <b>before</b> a credential can even be
presented, and it is the leg that decides whether a metered API is
agent-completable <b>end-to-end</b>: presenting a bearer token or an API key only
helps an agent that already <b>holds</b> one. If the sole way to obtain that
credential is a <b>human signing up on a dashboard</b>, an autonomous agent is
stranded at the door however cleanly the offer documents its auth scheme, its
errors, or its async contract. An offer that lets the agent <b>provision its own
access</b> &mdash; <b>no signup</b>, no human account creation, an agent that
<b>provisions its own identity</b>, an explicit <b>self-provision</b> path, or
credentials issued <b>without a human</b> in the onboarding loop &mdash; is more
agent-completable than one whose first step is a person filling in a form. So
ASRS reads the documented onboarding path as part of provisioning the offer,
keyed on vendor-neutral <b>agent-onboarding vocabulary</b> (no signup, no human
account creation, an agent provisioning its own identity, a self-provision path),
the same category of open convention as REST, GraphQL or OpenAPI. The read is
<b>precision-guarded</b>: it recognizes <b>only</b> the affirmative agentic path
and never the OPPOSITE human one &mdash; a &ldquo;<b>sign up on the dashboard for
an API key</b>&rdquo; instruction, a <code>401 No API key</code> error, or the
pricing sense &ldquo;<b>no signup fees</b>&rdquo; must never be read as
self-provisioning. Recognition keys on <b>whether a human must onboard the agent,
not who runs the API</b>: that property is pinned by an <b>executable regression
test</b> that relabels the API&rsquo;s identity end-to-end and confirms the
self-provisioning claim is still recognized, unchanged, with the vendor&rsquo;s
name gone. This read is <b>diagnostic</b> &mdash; it names whether an agent can
get in without a human, <b>off the scoring path</b> &mdash; not a scored
pillar.</p>
<p><b>Finishing the job</b> has the same shape on the offer side, and it is
where a metered API can quietly strand an agent. Many agent-native offers are
<b>long-running jobs</b> &mdash; image or video generation, a training run, a
batch-inference request &mdash; whose work does not finish inside the request
that starts it: the agent submits the job and must then <b>collect the
result</b>, either from a <b>webhook callback</b> the API delivers or by
<b>polling a status endpoint</b> until the job completes. An offer that
documents that <b>asynchronous contract</b> is more agent-completable than one
that leaves the agent holding a job id it never learns how to redeem &mdash; so
ASRS reads the contract as part of understanding the offer, keyed on
vendor-neutral machine-integration vocabulary (a webhook, an async endpoint,
polling a status URL), the same category of open convention as REST, GraphQL or
OpenAPI. Recognition keys on the <b>shape of the contract, not the name of the
API</b>: that property is pinned by an <b>executable regression test</b> that
relabels the API&rsquo;s identity end-to-end and confirms the async contract is
still recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names what the offer requires, <b>off the scoring
path</b> &mdash; not a scored pillar.</p>
<p><b>Consuming the output as it streams</b> is the <b>in-band sibling</b> of
collecting an async job, and it is where a metered API that produces its answer
<b>incrementally</b> can either free an agent or block it. Where an async job
hands back a completed result <b>out of band</b> &mdash; a webhook fires, the
agent polls a status URL after the request returns &mdash; a <b>streaming</b>
offer delivers partial output <b>within the same request</b>, over the open
connection, while the work is still running. An agent that cannot read the
<b>streaming contract</b> either blocks on a long call it could have consumed
progressively, or is handed a <code>stream</code> URL it never learns how to
open &mdash; so an offer that documents how its output streams is more
agent-completable than one whose only mode is wait-for-the-whole-thing. So ASRS
reads the documented streaming contract as part of finishing the offer, keyed on
vendor-neutral open-standard delivery vocabulary (the W3C <b>server-sent
events</b> standard, its <code>text/event-stream</code> media type, a
<b>streaming endpoint</b> that streams the output or tokens as they are
produced), the same category of open convention as REST, GraphQL or OpenAPI. The
read is <b>precision-guarded</b>: a <b>bare</b> <code>stream</code> or
<code>SSE</code> token is <b>no signal</b> &mdash; an
<code>application/octet-stream</code> binary-download MIME type, the <b>Shanghai
Stock Exchange</b> (SSE) or &ldquo;sum of squared errors (SSE)&rdquo;, a live
stream, the bloodstream, or a &ldquo;stream of consciousness&rdquo; must never
trip it, and a bare <code>SSE</code> must never <b>conjure a metered-API
claim</b> on a stock-exchange page &mdash; so the phrasing must name an actual
streaming delivery (spelled-out server-sent events, the
<code>text/event-stream</code> type, a stream verb naming an output noun, a
streaming API or endpoint, or <code>SSE</code> only in a streaming context).
Recognition keys on the <b>contract the API documents, not who published it</b>:
that property is pinned by an <b>executable regression test</b> that relabels the
API&rsquo;s identity end-to-end and confirms the streaming contract is still
recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names whether the offer lets an agent consume output
as it is produced, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Trusting the async callback</b> is the <b>security sibling</b> of collecting
an async job, and it is where an agent that acts on <b>what arrives</b> can be
<b>deceived</b>. Where the async-job leg says a webhook <b>delivery channel
exists</b> &mdash; a callback fires, the agent is notified a job is done &mdash;
<b>nothing there says whether the agent can authenticate what lands on it</b>. An
autonomous agent that acts on an <b>unverified &ldquo;job complete&rdquo;
webhook</b> can be tricked by a <b>forged or spoofed callback</b> into <b>treating
fabricated output as real</b>, or &mdash; worse &mdash; <b>releasing a payment</b>
for work that never happened. So an offer that documents how an agent <b>verifies
an inbound webhook is authentic</b> before acting on it is more agent-completable,
and it dovetails with the same <b>$0-only capital-safety</b> ethos ASRS itself
holds: never act, and never pay, on a forged callback. ASRS reads the documented
verification contract as part of finishing the offer, keyed on vendor-neutral
<b>webhook-security vocabulary</b> (a <b>webhook signature</b>, a <b>webhook
signing secret</b> to verify inbound requests, an
<code>X-Webhook-Signature</code> header, webhook requests that are <b>authentic</b>
or <b>signed</b>), the same category of open convention as REST, GraphQL or
OpenAPI. The read is <b>precision-guarded</b>: a <b>bare</b> <code>signature</code>
or <code>signing secret</code> is <b>no signal</b> &mdash; a marketing
&ldquo;signature look&rdquo;, a <b>settlement signature</b> a payment proof
verifies locally, a <b>signed-URL</b> signing secret for file access, a <b>digital
signature</b> on a contract, and a webhook that merely <b>exists</b> (the
async-job leg&rsquo;s turf) must never trip it &mdash; so the phrasing must name a
<b>webhook</b> whose authenticity is being verified, not the words
&ldquo;signature&rdquo; or &ldquo;signing secret&rdquo; alone. Recognition keys on
the <b>contract the API documents, not who published it</b>: that property is
pinned by an <b>executable regression test</b> that relabels the API&rsquo;s
identity end-to-end and confirms the verification contract is still recognized,
unchanged, with the vendor&rsquo;s name gone. This read is <b>diagnostic</b>
&mdash; it names whether the offer lets an agent trust an inbound callback before
acting on it, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Accounting for the spend</b> is the <b>capital-safety accounting sibling</b>
of the payment <b>rails</b>, and it is where an agent that <b>pays</b> can lose
track of <b>what it was charged</b>. Where an <b>agent-payment rail</b> &mdash; an
<b>x402</b> challenge, a machine-payable endpoint &mdash; lets an agent settle a
metered call, <b>nothing there says what proof comes back</b> so the agent can
<b>reconcile its own spend</b>. An autonomous agent that pays and gets no
<b>machine-readable receipt</b> cannot <b>reconcile its own spend</b> &mdash; it
has spent capital it can neither confirm nor dispute &mdash; so a metered offer
that returns a <b>receipt the agent can log</b> is more agent-completable, and it
dovetails with the same <b>$0-only capital-safety</b> ethos ASRS itself holds:
account for what every call cost. Where the rail is the <b>PAY leg</b>, the receipt
is the <b>proof that comes back to reconcile the spend</b>. So ASRS reads the
documented receipt grant as part of understanding the metered offer, keyed on
vendor-neutral <b>proof-of-payment vocabulary</b> (a <b>receipt header</b> on the
paid response, a <b>payment / settlement receipt</b>, a <b>serialized receipt</b>,
a <b>spend record</b> the agent keeps, explicit <b>proof of payment</b>), the same
category of open convention as REST, GraphQL or OpenAPI &mdash; never on a
vendor&rsquo;s name. The read is <b>precision-guarded</b>: a <b>bare</b>
<code>receipt</code> word is <b>no signal</b> &mdash; an <b>email receipt</b>, a
<b>read receipt</b> (&ldquo;enable read receipts&rdquo;), an <b>order receipt</b>
on a retail checkout, &ldquo;<b>in receipt of</b>&rdquo; a message, and a warehouse
<b>receipt of goods</b> must never trip it &mdash; so the phrasing must name a
receipt header, a payment or settlement receipt, a serialized receipt, a spend
record, or an explicit proof of payment the agent can log. Recognition keys on the
<b>receipt the offer returns, not who returns it</b>: that property is pinned by an
<b>executable regression test</b> that relabels the storefront&rsquo;s identity
end-to-end and confirms the receipt grant is still recognized, unchanged, with the
vendor&rsquo;s name gone. This read is <b>diagnostic</b> &mdash; it names whether
the offer lets an agent <b>account for what it spent</b>, <b>off the scoring
path</b> &mdash; not a scored pillar.</p>
<p><b>Aborting a runaway job</b> is the control leg of that same asynchronous
contract, and it is where a metered API can quietly <b>bleed an agent&rsquo;s
budget</b>: a long-running job &mdash; an image or video generation, a training
run, a batch-inference request &mdash; keeps <b>billing for compute</b> while it
runs, so an agent that detects a <b>runaway or wrong</b> generation and cannot
<b>stop</b> it keeps paying for work it no longer wants. An offer that documents a
<b>cancellation contract</b> &mdash; a <code>.../cancel</code> endpoint on the job
resource, a <b>deadline header</b> that auto-cancels the job after a bound (a
<code>Cancel-After</code> header), or a documented <b>terminal
<code>canceled</code> state</b> &mdash; lets an agent <b>bound its own spend</b>
and is more agent-completable than one that leaves it watching the meter run with
no way to pull the plug. That capital-safety leg dovetails with ASRS&rsquo;s own
<b>$0-only</b> ethos: an agent that can call a stop on its own spending is
finishing the job on its own terms. So ASRS reads the documented cancellation
contract as part of finishing the offer, keyed on vendor-neutral REST conventions
(a cancel endpoint on a job resource, a <code>Cancel-After</code> deadline header,
a <code>canceled</code> job state), the same category of open convention as REST,
GraphQL or OpenAPI. The read is <b>precision-guarded</b>: a bare <code>cancel</code>
word is <b>no signal</b> &mdash; &ldquo;cancel your subscription&rdquo;, &ldquo;cancel
anytime&rdquo;, a retail &ldquo;cancel your order&rdquo;, a <b>cancellation policy</b>,
&ldquo;cancel your booking&rdquo;, or &ldquo;the flight was canceled&rdquo; must never
trip it &mdash; so the phrasing must name an actual job-cancellation facility (a
<code>Cancel-After</code> header, a cancel verb naming an <b>async-job</b> noun, or a
<code>.../cancel</code> endpoint on a job resource). Recognition keys on the
<b>contract the API documents, not who published it</b>: that property is pinned by an
<b>executable regression test</b> that relabels the API&rsquo;s identity end-to-end and
confirms the cancellation contract is still recognized, unchanged, with the
vendor&rsquo;s name gone. This read is <b>diagnostic</b> &mdash; it names whether the
offer lets an agent stop a job it started to bound its spend, <b>off the scoring
path</b> &mdash; not a scored pillar.</p>
<p><b>Recovering from a failed call</b> is the last leg of finishing, and it is
where an agent that has done everything else right still strands: calls fail
&mdash; a credential expires, a rate limit trips, a request is malformed &mdash;
and an agent can only <b>recover autonomously</b> if it can read <b>what went
wrong</b> in a form it did not have to guess. An offer that documents its
<b>error contract</b> &mdash; the <b>4xx/5xx</b> responses a call can return
&mdash; is more agent-completable than one that answers a failure with an opaque
body: an HTTP <b>status code</b> tells the agent whether to refresh a credential
(on a <code>401</code>), back off and retry (on a <code>429</code>), or surface a
clear failure; an <b>RFC&nbsp;7807</b> <code>application/problem+json</code> body,
or a machine-readable <b>error code</b> (a status paired with a
<code>snake_case</code> identifier such as <code>invalid_request</code>), tells it
<b>why</b>. So ASRS reads the documented error contract as part of understanding
the offer, keyed on vendor-neutral machine conventions (an HTTP status code, an
RFC&nbsp;7807 problem body, a named error code), the same category of open
convention as REST, GraphQL or OpenAPI. Recognition keys on the <b>declared
contract, not who declares it</b>: that property is pinned by an <b>executable
regression test</b> that relabels the API&rsquo;s identity end-to-end and confirms
the error contract is still recognized, unchanged, with the vendor&rsquo;s name
gone. This read is <b>diagnostic</b> &mdash; it names how the offer reports a
failure, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Not paying for a call that failed</b> is the <b>capital-safety sibling</b> of
the <b>receipt</b> leg, one step earlier: the receipt lets an agent <b>account for
what a successful call cost</b>, but <b>nothing there says what a FAILED call
costs</b>. A metered endpoint bills per call, and calls fail &mdash; a render does
not complete, a job errors, a request times out. An autonomous per-call buyer that
cannot tell whether a <b>failed unit</b> is <b>silently charged</b> anyway cannot
<b>bound its own spend</b> against a flaky endpoint: every retry against a failing
service might be burning money for work it never received. An offer that documents
that a <b>failed call is not billed</b> &mdash; &ldquo;<b>you are not charged</b>
for a failed generation&rdquo;, &ldquo;you are <b>only billed for completed</b>
jobs&rdquo; &mdash; is more agent-completable, and it dovetails with the same
<b>$0-only capital-safety</b> ethos ASRS itself holds: <b>you don&rsquo;t pay for
work you didn&rsquo;t get</b>. It is the metered <b>failure-billing</b> leg, distinct
from every neighbour: the <b>receipt</b> is proof of a <b>successful</b> charge, the
<b>error contract</b> is the <b>shape</b> of a failure (not its price), and a
<b>free trial</b> is a subscription&rsquo;s $0 evaluation window. So ASRS reads the
documented failure-billing grant as part of finishing the metered offer, keyed on
vendor-neutral <b>failure-billing vocabulary</b> (a <b>failure token</b> &mdash;
failed, errored, did not complete, timed out &mdash; joined to <b>not / never
charged or billed</b>, or an explicit <b>only charged for successful / completed</b>
calls), the same category of open convention as REST, GraphQL or OpenAPI &mdash;
never on a vendor&rsquo;s name. The read is <b>precision-guarded</b>: a <b>bare</b>
&ldquo;<b>not charged</b>&rdquo; is <b>no signal</b> &mdash; a subscription&rsquo;s
&ldquo;<b>your card is not charged until the trial ends</b>&rdquo; or &ldquo;you are
not charged during the free trial&rdquo; is a <b>$0-evaluation promise</b>, not a
failure guarantee, and an <b>error contract</b> that names a failure without saying
it is free must never trip it &mdash; so the phrasing must join a <b>failure
token</b> to a <b>not-charged / not-billed</b> clause, or name being charged
<b>only</b> for successful calls. Recognition keys on the <b>failure-billing contract
the offer documents, not who documents it</b>: that property is pinned by an
<b>executable regression test</b> that relabels the storefront&rsquo;s identity
end-to-end and confirms the failure-billing grant is still recognized, unchanged,
with the vendor&rsquo;s name gone. This read is <b>diagnostic</b> &mdash; it names
whether the offer lets an agent <b>bound its spend against a failing endpoint</b>,
<b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Bounding a single call&rsquo;s cost</b> is the <b>capital-safety sibling</b> of
the <b>failure-not-billed</b> leg from the other direction: failure-not-billed bounds
what a <b>FAILED</b> call costs, this bounds what a <b>SUCCESSFUL</b> one can cost
<b>before</b> the agent commits to it. A metered endpoint whose price varies with the
request &mdash; tokens consumed, seconds of compute, output size &mdash; leaves an
autonomous per-call buyer unable to know its <b>worst-case exposure</b> until the bill
arrives: a single call against a variable-priced service might cost far more than the
agent budgeted, and it has <b>no way to cap that up front</b> before it authorizes.
An offer that documents a <b>reserve-and-settle</b> contract &mdash; <b>reserve a
spend ceiling</b> up front, be <b>charged only actual</b> usage, the unused remainder
<b>refunded</b> &mdash; lets the agent <b>bound its worst-case cost per request</b> the
way a human sets a <b>credit-card hold</b>: it never overpays for a call that turned
out cheaper than the ceiling, and it never authorizes a call whose ceiling it cannot
afford. That dovetails with the same <b>$0-only capital-safety</b> ethos ASRS holds
&mdash; an agent that can cap its exposure per call spends deliberately, not blindly.
It is <b>distinct</b> from every neighbour: the payment <b>rails</b> (x402, a
machine-payable endpoint) say the agent <b>can pay</b>; the <b>receipt</b> is proof of
a <b>successful</b> charge after the fact; the <b>pricing</b> signals say <b>how</b>
you are charged on success; and <b>failure-not-billed</b> bounds a
<b>failure&rsquo;s</b> cost &mdash; this bounds a <b>success&rsquo;s</b>. So ASRS reads
the documented reserve-and-settle grant as part of finishing the metered offer, keyed
on vendor-neutral <b>reserve-and-settle vocabulary</b> (a <b>reserve-and-pay-actual</b>
rail, <b>reserving a spend ceiling</b>, being <b>charged only actual</b> against a
reserved ceiling, an <b>escrow</b> or <b>channel that refunds the remainder</b>), the
same category of open convention as REST, GraphQL or OpenAPI &mdash; never on a
vendor&rsquo;s name. The read is <b>precision-guarded</b>: a <b>bare</b>
<code>reserve</code>, <code>refund</code>, <code>ceiling</code> or <code>escrow</code>
word is <b>no signal</b> &mdash; a hotel <b>reservation</b>, &ldquo;we <b>reserve the
right</b>&rdquo;, a retail <b>full refund within 30 days</b>, cloud <b>reserved
capacity</b>, or a <b>ceiling fan</b> must never trip it &mdash; so the phrasing must
name the reserve-<b>and</b>-settle structure: a named reserve-and-pay-actual rail,
reserving a <b>spend</b> ceiling, being charged only actual against a reserved ceiling,
or an escrow/channel that refunds the <b>remainder</b>. Recognition keys on the
<b>reserve-and-settle contract the offer documents, not who documents it</b>: that
property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the reserve-and-settle grant is
still recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names whether the offer lets an agent <b>cap a single
call&rsquo;s cost up front</b>, <b>off the scoring path</b> &mdash; not a scored
pillar.</p>
<p><b>Walking the whole collection</b> is the finishing leg for a metered API that
answers with a <b>list</b> &mdash; your predictions, your models, your deployments,
your records &mdash; because such an endpoint rarely returns everything at once: it
hands back <b>one page</b> plus a way to fetch the rest, and an agent that stops at
the first page silently <b>under-completes the retrieval</b>, reporting a partial
answer as if it were the whole. An offer that documents its <b>pagination
contract</b> &mdash; a <b>cursor</b> query parameter to pass back for the next
slice, a <code>next</code>/<code>previous</code> <b>page URL</b> to follow, or a
<b>paginated collection response</b> that names where the next page lives &mdash; is
more agent-completable than one that leaves the agent guessing whether the list it
received was complete. So ASRS reads the documented pagination contract as part of
finishing the offer, keyed on vendor-neutral collection conventions (a cursor
parameter carrying a value, a next/previous page URL, a paginated collection
response), the same category of open convention as REST, GraphQL or OpenAPI. The
read is <b>precision-guarded</b>: a bare <code>next</code> or <code>cursor</code>
word is <b>no signal</b> &mdash; a retail &ldquo;<code>next</code>&rdquo; product
link, a &ldquo;next campaign&rdquo; banner, a text cursor, or the &ldquo;next page
of the novel&rdquo; must never trip it &mdash; so the phrasing must name an actual
API pagination facility (a cursor carrying a value, cursor-based pagination, or a
next/previous page <b>of an API collection</b>). Recognition keys on the
<b>contract the API documents, not who published it</b>: that property is pinned by
an <b>executable regression test</b> that relabels the API&rsquo;s identity
end-to-end and confirms the pagination contract is still recognized, unchanged,
with the vendor&rsquo;s name gone. This read is <b>diagnostic</b> &mdash; it names
whether the offer lets an agent walk a multi-page result set to completion, <b>off
the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Trying the call safely first</b> comes <b>before</b> any of the other legs,
because an agent that can rehearse the whole flow at <b>zero cost</b> completes
the job without a human standing by to catch a first-attempt mistake. A metered
API that offers a <b>test facility</b> &mdash; a <b>sandbox environment</b>, a
<b>test-mode</b> flag, a <b>test API key</b> or test credentials, an explicit
<b>dry-run</b>, or the widely-used <code>&lt;prefix&gt;_test_</code> /
<code>&lt;prefix&gt;_sandbox_</code> key convention (for example a credential
dichotomy of a <code>_live_</code> production key beside a <code>_test_</code>
sandbox one) &mdash; lets an agent <b>validate its integration and dry-run a
call</b> without spending real money, consuming quota, or producing a billable
output. That is the <b>provision-and-finish-safely</b> capability read at the
offer layer, and it dovetails with ASRS&rsquo;s own <b>$0-only</b> ethos: an
offer that an agent can exercise at zero cost before it authorizes a real charge
is more agent-completable than one that forces the first call to be a paid one.
So ASRS reads the documented test facility as part of understanding the metered
offer, keyed on vendor-neutral machine-integration vocabulary (a sandbox
environment, a test-mode flag, a test credential, a dry-run, the
<code>_test_</code>/<code>_sandbox_</code> key convention), the same category of
open convention as REST, GraphQL or OpenAPI. The read is
<b>precision-guarded</b>: a bare <code>sandbox</code> or <code>test</code> word
is <b>no signal</b> &mdash; a demo site titled &ldquo;Sandbox&rdquo;, a sandboxed
iframe, or a <code>unit_test_runner</code> filename must never trip it &mdash; so
the word must name an actual testing facility, a mode, a credential, or the
masked-stub key convention. Recognition keys on the <b>facility the offer
provides, not who provides it</b>: that property is pinned by an <b>executable
regression test</b> that relabels the API&rsquo;s identity <b>and its key
prefix</b> end-to-end and confirms the test facility is still recognized,
unchanged, with the vendor&rsquo;s name gone. This read is <b>diagnostic</b>
&mdash; it names whether the offer lets an agent rehearse the call at $0, <b>off
the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Trying a paid call for free before you fund</b> is the <b>capital-safety
sibling</b> of the <b>receipt</b> and <b>reserve-and-settle</b> legs from the
on-ramp direction: those bound what a call <b>costs</b> once money is in play,
this asks whether the agent can prove the paid endpoint <b>works end to end at
$0</b> &mdash; before it funds a wallet at all. An autonomous per-call buyer that
must move money into a metered service <b>sight unseen</b>, on the promise the API
will do what it claims, is exposed the way anyone is who <b>pays before they can
verify</b>; an offer that documents a <b>free included allowance</b> &mdash; a
per-account grant of <b>real billable units</b> usable at a <b>zero balance</b>
with no funding, an <code>includedUnits</code> allotment named as free, or an
explicit invitation to <b>try / call the API before any money or funding</b>
&mdash; lets the agent run a genuine metered call, confirm the integration, and
<b>only then</b> decide to fund. That dovetails directly with ASRS&rsquo;s own
<b>$0-only</b> ethos: the offer an agent can exercise <b>for real</b> at zero cost
before committing capital is the most agent-completable on-ramp there is. It is
<b>distinct</b> from every neighbour: <b>test-mode</b> rehearses the call in a
<b>sandbox / fake environment</b> (no real output, no real billing), a
subscription <b>free trial</b> is a <b>time-boxed window</b> on a recurring plan,
and <b>self-provisioning</b> grants free <b>identity or access</b> &mdash; none of
them is a <b>real billable unit run at $0 against production before funding</b>.
So ASRS reads the documented free-allowance grant as part of understanding the
metered offer, keyed on vendor-neutral <b>free-usage vocabulary</b> (a <b>free
usage / allowance</b>, <b>free units per account or period</b>, an
<code>includedUnits</code> allotment named free, or an explicit try/call
<b>before any money or funding</b>), the same category of open convention as REST,
GraphQL or OpenAPI &mdash; never on a vendor&rsquo;s name. The read is
<b>precision-guarded</b>: a <b>bare</b> &ldquo;<b>free</b>&rdquo; is <b>no
signal</b> &mdash; <b>free shipping</b>, a <b>royalty-free</b> licence,
<b>toll-free</b>, <b>free parking</b>, &ldquo;<b>feel free</b>&rdquo;, or a
<b>paid</b> &ldquo;500 units <b>included</b> per month&rdquo; allotment must never
trip it &mdash; so the phrasing must name a free <b>usage/allowance</b>, free
<b>units per account/period</b>, an <code>includedUnits</code> grant joined to
<b>free</b>, or trying the call <b>before any money/funding</b>. Recognition keys
on the <b>free-usage contract the offer documents, not who documents it</b>: that
property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the free-allowance grant is
still recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names whether the offer lets an agent <b>run a real
paid call at $0 before funding</b>, <b>off the scoring path</b> &mdash; not a
scored pillar.</p>
<p><b>Owning the deliverable</b> is finishing on the <b>digital-good</b> side,
where an agent can obtain exactly the render it asked for and still not be able to
<b>use</b> it. A generation storefront returns an image, a video, an audio clip or
a document; whether the agent may put that output to work &mdash; ship it in a
product, resell it, publish it &mdash; turns on the <b>usage rights</b> the offer
grants. An offer that documents a <b>commercial licence</b> on its output,
<b>royalty-free</b> terms, explicit <b>usage rights</b>, or plain ownership of the
deliverable (&ldquo;<b>you own the output</b>&rdquo;) is more agent-completable
than one that hands back a render the agent has no licence to use &mdash; an agent
that cannot legally use what it obtained has <b>not completed the commercial
job</b>. So ASRS reads the documented rights grant as part of understanding the
digital-good offer, keyed on vendor-neutral <b>rights vocabulary</b> (a commercial
licence, royalty-free terms, stated usage rights, ownership of the output), never
on a vendor&rsquo;s name &mdash; and never on a bare <code>license</code> word,
since a software licence, a business licence, or a hosted <b>model&rsquo;s own
licence</b> is not a grant of rights in the deliverable and is read as no signal.
Recognition keys on the <b>rights the offer grants, not who grants them</b>: that
property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the rights grant is still
recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names whether the offer lets an agent use what it
buys, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Trusting the deliverable</b> is the authenticity mirror of owning it: on the
<b>digital-good</b> side an agent can obtain exactly the render it asked for, hold a
licence to use it, and still not be able to <b>prove it is genuine</b>. As synthetic
media proliferates, a generated deliverable that carries embedded <b>provenance</b>
&mdash; <b>C2PA content credentials</b>, a <b>provenance manifest</b> or metadata
record of how the asset was produced &mdash; lets the agent verify the output and
carry it into a <b>provenance-aware pipeline</b> (disclosure, attribution, downstream
trust), whereas a render an agent cannot provenance-check has <b>not completed the
commercial job</b> in any workflow that must vouch for what it ships. So ASRS reads a
documented provenance record as part of understanding the digital-good offer, keyed on
vendor-neutral <b>open-standard provenance vocabulary</b> (the <b>C2PA</b> Coalition
for Content Provenance and Authenticity standard, the <b>Content Credentials</b> mark,
a media/output <b>provenance manifest</b> or metadata record), the same category of
open convention as REST, GraphQL or OpenAPI &mdash; never on a vendor&rsquo;s name. The
read is <b>precision-guarded</b>: a bare <code>provenance</code> or
<code>credentials</code> word is <b>no signal</b> &mdash; art, wine or supply-chain
provenance, <b>data provenance</b>, login credentials, or a hosted model&rsquo;s own
&ldquo;watermarking for provenance&rdquo; feature must never trip it &mdash; so the
phrasing must name the C2PA standard, the content-credentials mark, a media/output
noun qualifying provenance, or a provenance metadata/record grant on the deliverable.
Recognition keys on the <b>provenance the offer grants, not who grants it</b>: that
property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the provenance record is still
recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names whether the offer lets an agent trust what it
obtained, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Specifying the deliverable&rsquo;s shape</b> is the <b>output-spec sibling</b>
of owning and trusting the render: on the <b>digital-good</b> side an agent can
obtain a render it holds a licence to use and can prove is genuine, and still get
it back at the <b>wrong size</b> to use. A generation storefront returns an image,
a video or a document, but <b>what</b> it produces, <b>where</b> it delivers it and
whether the agent may <b>use</b> it all say nothing about the physical <b>shape</b>
of the deliverable &mdash; its <b>output resolution</b>, its <b>pixel dimensions</b>,
its <b>aspect ratio</b> &mdash; the one parameter the agent must set on the request
itself. An agent that cannot read the documented <b>output-resolution contract</b>
either requests a size the API cannot produce (a failed or clipped generation) or is
handed a deliverable at the <b>wrong resolution for its downstream use</b> &mdash; a
hero image delivered at thumbnail size &mdash; so an offer that documents its output
resolutions and dimensions is more agent-completable than one that leaves the agent
guessing what size it will be handed back. So ASRS reads the documented output spec
as part of understanding the digital-good offer, keyed on vendor-neutral
<b>output-format vocabulary</b> (a <code>maxResolution</code> field, an output /
render / print resolution in pixels, a <b>WxH pixel dimension</b>, an
<b>aspect ratio</b>), the same category of open convention as REST, GraphQL or
OpenAPI &mdash; never on a vendor&rsquo;s name. The read is <b>precision-guarded</b>:
a bare <code>resolution</code> word is <b>no signal</b> &mdash; <b>dispute
resolution</b>, a New-Year resolution, DNS resolution, a hosted model&rsquo;s own
<b>Super-resolution</b> or &ldquo;enhance image resolution&rdquo; <b>feature</b>
(what the model does, not a deliverable the storefront vends), and a <b>screen /
monitor / display</b> resolution (the viewer&rsquo;s hardware, not the deliverable)
must never trip it &mdash; so the phrasing must name an actual output spec (a
<code>maxResolution</code> field, a print resolution, a resolution in explicit
pixels, an output/render/canvas/generation/target resolution or dimensions, a WxH
pixel dimension, or an aspect ratio). Recognition keys on the <b>shape the offer
documents, not who documents it</b>: that property is pinned by an <b>executable
regression test</b> that relabels the storefront&rsquo;s identity end-to-end and
confirms the output spec is still recognized, unchanged, with the vendor&rsquo;s
name gone. This read is <b>diagnostic</b> &mdash; it names whether the offer lets an
agent request the render at the size it needs, <b>off the scoring path</b> &mdash;
not a scored pillar.</p>
<p><b>Choosing the deliverable&rsquo;s variant</b> is the <b>deliverable-control
sibling</b> of specifying its shape: on the <b>digital-good</b> side an agent can
obtain a render at the right size, hold a licence to use it and prove it is genuine,
and still be handed a <b>different look every call</b>. Every other digital-good read
names a <b>property of the artifact the agent receives</b> &mdash; that the media is
<b>generated</b>, how it is <b>delivered</b>, what <b>rights</b> attach, whether it is
<b>authentic</b>, how large it is, how long it <b>persists</b> &mdash; and none of them
says whether the agent can <b>control which variant gets produced</b>. An agent
generating <b>at scale</b> &mdash; a catalog run where <b>the two-hundredth image has to
match the first</b> &mdash; cannot use a service that returns a <b>random style each
call</b>; a generative offer that documents <b>programmatic variant selection</b> &mdash;
a selectable <b>style preset</b> the agent passes on the request that <b>locks palette,
lighting and rendering style</b> &mdash; hands back a <b>fit-for-purpose, reproducible</b>
deliverable, so it is <b>more agent-completable</b> than one that leaves the look to
chance. That makes it the <b>reproducibility leg</b> of finishing the digital-good job,
distinct from the shape leg (<b>output resolution</b> is <b>how big</b> the render is;
variant selection is <b>which look</b> it has) and from every rights / authenticity /
delivery read. So ASRS reads the documented variant-selection facility as part of
understanding the digital-good offer, keyed on vendor-neutral <b>variant-selection
vocabulary</b> (a <b>style preset</b>, a preset <b>slug / string / parameter / id /
name</b>, an explicit <b>pick / choose / select / browse / pass / send a preset</b>, a
preset that <b>locks or pins the style</b>), the same category of open convention as
REST, GraphQL or OpenAPI &mdash; never on a vendor&rsquo;s name. The read is
<b>precision-guarded</b>: a bare <code>model</code> or <code>tier</code> word is <b>no
signal</b> &mdash; a language, business, role or 3D <b>model</b> and a <b>billing
tier</b> (owned by the metered-API <b>tiered-volume</b> read) appear all over these docs
and must never trip it &mdash; and the <b>preset verb</b> (&ldquo;<b>preset</b> the oven
to 200C&rdquo;), a <b>factory preset</b>, a <b>camera preset</b> and a <b>reset</b> are
not variant selection either, so the phrasing must name a <b>style preset</b>, a preset
<b>parameter</b>, an explicit <b>select / browse a preset</b> verb, or a preset that
<b>locks or pins the style</b>. Recognition keys on the <b>variant-selection contract the
offer documents, not who documents it</b>: that property is pinned by an <b>executable
regression test</b> that relabels the storefront&rsquo;s identity end-to-end and confirms
the variant-selection facility is still recognized, unchanged, with the vendor&rsquo;s
name gone. This read is <b>diagnostic</b> &mdash; it names whether the offer lets an
agent obtain a <b>usable, reproducible deliverable</b>, <b>off the scoring path</b>
&mdash; not a scored pillar.</p>
<p><b>Evaluating a subscription at $0 first</b> is finishing on the
<b>subscription</b> side, where the thing an agent must commit to is not a single
call but a <b>recurring charge</b> that renews on its own. An agent asked to
provision a plan cannot responsibly authorize open-ended billing it has never
exercised; a subscription offer that lets it try the plan at <b>zero cost before
any charge begins</b> &mdash; a <b>free trial</b>, a <b>trial period</b>, an
<b>N-day trial</b>, or a <b>trial account</b> or allowance &mdash; lets the agent
evaluate the whole subscription and then decide, rather than commit to
<b>recurring billing sight-unseen</b>. That is the subscription-side mirror of
trying a metered call safely first, and it dovetails with ASRS&rsquo;s own
<b>$0-only</b> ethos: an offer an agent can evaluate at zero cost before it
commits to a renewing charge is more agent-completable than one whose only door
is a paid signup. So ASRS reads the documented <b>trial offer</b> as part of
understanding the subscription offer, keyed on vendor-neutral <b>trial-offer
vocabulary</b> (a free trial, a trial period, an N-day trial such as a
<code>14-day free trial</code>, a trial account or allowance, &ldquo;start your
free trial&rdquo;, &ldquo;try it free for N days&rdquo;), the same category of
open convention as REST, GraphQL or OpenAPI. The read is
<b>precision-guarded</b>: a bare <code>trial</code> word is <b>no signal</b>
&mdash; a <b>clinical trial</b>, a court trial, &ldquo;trial and error&rdquo;,
&ldquo;trial by fire&rdquo;, or a defendant &ldquo;on trial&rdquo; must never
trip it &mdash; so the phrasing must name an actual free-trial offer (a free
trial, a trial period/account/allowance, an N-day trial, or a start/try-free
offer). Recognition keys on the <b>trial the offer grants, not who grants it</b>:
that property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the trial offer is still
recognized, unchanged, with the vendor&rsquo;s name gone. This read is
<b>diagnostic</b> &mdash; it names whether the offer lets an agent evaluate a
subscription at $0 before committing, <b>off the scoring path</b> &mdash; not a
scored pillar.</p>
<p><b>Committing to a plan without a human</b> is the <b>commit leg</b> of that same
<b>subscription</b> offer, and it is where an agent that can already read a plan&rsquo;s
price and even try it free still cannot <b>take on the recurring commitment</b> on its
own. The two subscription legs read so far say what a plan <b>costs</b> (the recurring
price an agent reads) and let it <b>evaluate the plan at $0</b> before any charge (the
free-trial leg); <b>neither says whether the agent can actually buy the plan</b>. A
subscription whose only path to commit runs a <b>human through a pricing-page checkout
or a dashboard onboarding flow</b> is not agent-completable at the commit step, however
cleanly it documents its cadence &mdash; the agent is stranded one step short of the
recurring offer it was sent to provision. So a subscription that exposes a
<b>programmatic plan-purchase path</b> &mdash; a <code>/plans/{id}/purchase</code>
endpoint, a <b>purchasable plan</b>, a <b>buy / purchase / activate</b> verb naming a
<b>credit or subscription plan</b> &mdash; is <b>more agent-completable</b>, and it is
the load-bearing <b>commit</b> leg of agent-native commerce: take on the recurring
commitment without a human. It is the subscription-archetype counterpart of the
metered-API archetype&rsquo;s <b>self-provisioning</b> (obtain API access without a
human), one archetype over. This commit leg is also <b>distinct from the payment
rails</b> &mdash; an <b>x402</b> challenge or a machine-payable endpoint is the <b>PAY
leg</b> (whether the agent <b>can pay at all</b>); plan-purchase is <b>which recurring
thing it commits that payment to</b>. So ASRS reads the documented plan-purchase path as
part of understanding the subscription offer, keyed on vendor-neutral
<b>plan-commitment vocabulary</b> (a plan-purchase endpoint on the plan resource, a
purchasable plan, a buy/purchase/activate verb naming a credit or subscription plan),
the same category of open convention as REST, GraphQL or OpenAPI &mdash; never on a
vendor&rsquo;s name. The read is <b>precision-guarded</b>: a <b>bare</b>
<code>plan</code> word is <b>no signal</b> &mdash; &ldquo;<b>subscribe to a plan</b>&rdquo;
on a pricing page, a <b>dashboard onboarding</b> flow, and bare &ldquo;<b>subscription
plans</b>&rdquo; marketing are all the <b>human</b> path and must never trip it &mdash;
so the phrasing must name a programmatic purchase of the plan (a plan-purchase endpoint,
a purchasable plan, or a buy/purchase/activate verb on a credit or subscription plan).
Recognition keys on the <b>plan the offer lets an agent buy, not who sells it</b>: that
property is pinned by an <b>executable regression test</b> that relabels the
storefront&rsquo;s identity end-to-end and confirms the plan-purchase path is still
recognized, unchanged, with the vendor&rsquo;s name gone. This read is <b>diagnostic</b>
&mdash; it names whether the offer lets an agent <b>commit to a recurring plan without a
human</b>, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
<p><b>Reading the price to fulfill</b> is finishing on the <b>physical-good</b>
side, where an agent can browse a catalog, read that an item is <b>in stock</b>
and see an <b>add-to-cart</b> control, and still not be able to <b>decide</b>
whether to buy it. To decide on and then <b>fulfill</b> a physical purchase an
agent must read the <b>concrete price</b> of the purchasable item; a storefront
that quotes a decimal money amount <b>directly beside</b> the item&rsquo;s
availability or add-to-cart control &mdash; a <b>priced catalog listing</b> such
as &ldquo;<code>&pound;51.77 In stock</code>&rdquo; or &ldquo;<code>$12.99 Add to
basket</code>&rdquo; &mdash; makes that price <b>machine-legible on the
listing</b>, whereas a catalog whose price an agent cannot read beside the item
has <b>not completed the commercial job</b>: the agent can put the thing in a
cart but cannot decide whether it is worth buying. So ASRS reads the priced
listing as part of understanding the physical-good offer, keyed on the
vendor-neutral <b>priced-listing shape</b> (a decimal amount adjacent to an
in-stock or add-to-cart/basket/bag control), never on a vendor&rsquo;s name. The
read is <b>precision-guarded</b>: a <b>bare</b> currency amount is <b>no
signal</b> &mdash; a metered API&rsquo;s &ldquo;<code>$0.01 per API call</code>&rdquo;
or &ldquo;<code>$5 per 1,000 requests</code>&rdquo;, or a subscription&rsquo;s
&ldquo;<code>$29 per month</code>&rdquo; fee, sits <b>nowhere near</b> in-stock or
add-to-cart availability language &mdash; so the amount must sit <b>immediately
beside</b> the availability control to count, and a price alone can never conjure
a physical good on an API storefront that merely lists dollar amounts (it stays
<b>NA</b> there). Recognition keys on the <b>price the offer lists, not who lists
it</b>: that property is pinned by an <b>executable regression test</b> that
relabels the storefront&rsquo;s identity end-to-end and confirms the priced
listing is still recognized, unchanged, with the vendor&rsquo;s name gone. This
read is <b>diagnostic</b> &mdash; it names whether the offer lets an agent read
what a physical item costs before buying, <b>off the scoring path</b> &mdash; not
a scored pillar.</p>
</div>

<div class="card">
<h2><span class="n">1</span>The five pillars</h2>
<p>Each pillar is scored 0&ndash;100 from its named checks, then combined by the
weights below. Transactability carries the most weight because paying and
provisioning without a human is the heart of agentic commerce.</p>
<table><tr><th>Pillar</th><th class="num">Weight</th></tr>{pillar_rows}</table>
</div>

<div class="card">
<h2><span class="n">2</span>How a pillar and the overall score are computed</h2>
<p>A pillar score is <b>points earned &divide; points applicable</b>. Only checks
with a real observation count toward the denominator. The overall is the
weight-renormalized average of the pillars that were observable: if a whole
pillar could not be tested (e.g. the <b>outcome</b> pillar in static-only mode,
with no live shopper panel), its weight is <b>dropped and the remaining weights
renormalize</b> &mdash; the score is always over what was actually measured,
never diluted by blanks.</p>
</div>

<div class="card">
<h2><span class="n">3</span>FAIL vs CANT_TEST &mdash; the two ways a check can not-pass</h2>
<p>A <b>FAIL</b> is evidence: the capability was tested and is absent. It earns
0 points and <b>stays in the denominator</b>, so it pulls the pillar down.</p>
<p>A <b>CANT_TEST</b> (or NA) is the absence of evidence: the probe could not
observe the capability at all. It is excluded from <b>both</b> the numerator and
the denominator &mdash; it shrinks the pillar rather than scoring it. A site is
<b>never punished for what couldn&rsquo;t be observed</b>. Confusing these two is
the most common way benchmarks lie; ASRS keeps them strictly separate.</p>
<h3>A worked example &mdash; when is a low score earned evidence, not a blind spot?</h3>
<p>Suppose two storefronts are compared and one scores far below the other. That
gap only means something if the low number is <b>earned evidence</b> and not the
probe&rsquo;s own blind spot. ASRS treats a delta between two sites as
trustworthy only when three properties hold together:</p>
<ul>
<li><b>Full observability.</b> Every check on the lower-scoring side was actually
observed (a clean crawl, nothing CANT_TEST). So each 0 is a
<b>tested-and-absent</b> capability &mdash; a FAIL above, evidence of absence
&mdash; never an <b>un-observed</b> check quietly held against the site.</li>
<li><b>Like-for-like denominator.</b> Both sides are scored over the
<b>identical set of checks</b>, so the gap compares the same capabilities on
each, not a different question asked of one and not the other.</li>
<li><b>Check-by-check dominance, no inversion.</b> The higher-scoring side ranks
at least as high (PASS&nbsp;&gt;&nbsp;PARTIAL&nbsp;&gt;&nbsp;FAIL) at
<b>every</b> shared check, and strictly higher on at least one. The gap is a
capability <b>superset</b> &mdash; the lower side does nothing the higher side
doesn&rsquo;t &mdash; not a mix of wins and losses that happens to net out.</li>
</ul>
<p>Together these say a large delta is an <b>earned</b> capability difference at
matched, fully-observed checks, not an artifact of differential observability or
a masked inversion. On the benchmark&rsquo;s reference pair this property is
pinned by an executable regression test, so it is <b>enforced every cycle</b>,
not merely asserted.</p>
<h3>But couldn&rsquo;t you re-weight the pillars to get the answer you want?</h3>
<p>The worked example above answers <i>&ldquo;did you rig which checks you
observe?&rdquo;</i>. A separate objection targets the last step: the overall is a
<b>weighted average of the pillars</b> (see section&nbsp;1) &mdash; so could the
weights themselves be tuned to hand one side the win? For a delta to be credible,
its <b>sign</b> must not depend on that choice.</p>
<p>It does not, and for a structural reason. When the higher-scoring side is
<b>pillar-wise dominant</b> &mdash; at least as high on <b>every</b> pillar both
sides actually expose, strictly higher on at least one &mdash; over the
<b>same applicable-pillar set</b>, with <b>neither side&rsquo;s grade capped</b>,
then each overall is a plain renormalized weighted mean of the <i>same</i>
pillars. A weighted average with non-negative weights can never rank a
dominated side above the side that dominates it. So the delta keeps its sign
under <b>every reasonable weighting</b> &mdash; not just the rubric&rsquo;s, but
the uniform weighting and even the extremes that pile all the weight onto a
single pillar. The weights set how <i>large</i> the gap is; they cannot flip
<i>which</i> side is ahead. This too is pinned by an executable regression test
on the reference pair, including an adversarial family of weightings.</p>
<p>The same reasoning scales past a single pair to the <b>whole ranking</b>.
When a population of storefronts &mdash; from full agent-native rails, down
through a legible API with no agent-native payment, a human-checkout retail
shop, to a page that sells nothing &mdash; forms a <b>total dominance chain</b>
(each rung at least as high as the next on <b>every</b> applicable pillar,
strictly higher on at least one, over the same uncapped pillar set), then no
non-negative reweighting can invert <b>any</b> rung, not merely the head delta.
The entire ordering &mdash; not just who wins the headline comparison &mdash; is
weight-robust: non-increasing under the rubric weighting, the uniform weighting,
and every unit-basis extreme, and strictly decreasing wherever the weighting
touches a pillar on which a rung genuinely dominates. This population-wide
property has its own executable regression test over the reference spectrum, so
the credibility of the leaderboard&rsquo;s <i>shape</i>, not just its top pair,
is enforced every cycle.</p>
<p>One honest refinement keeps that chain from over-claiming. Dominance as used
above is a <b>pillar-layer</b> property &mdash; it compares the rolled-up pillar
scores. At the finer <b>per-check</b> layer the head delta is still a clean
superset, but a rung lower down the chain need not be: a lower-ranked storefront
can out-rank a higher-ranked one on a single check yet still lose the pillar that
check belongs to. On the reference spectrum exactly one such <b>minority
reversal</b> occurs &mdash; a human-checkout retail shop presents stronger
transport security (HTTPS&nbsp;/&nbsp;HSTS) than a legible API storefront that
offers no agent-native payment, yet the API storefront still wins the <b>trust</b>
pillar overall, so the ranking holds. Rolling checks up into pillars is exactly
what <b>absorbs</b> that lone reversal &mdash; the ordering is robust <i>because</i>
the aggregation outvotes an honest local tie, not because every check marches in
lockstep. ASRS <b>surfaces</b> the inversion, pinned check by check by the same
executable regression test, rather than hiding it behind a false
&ldquo;wins&nbsp;every&nbsp;check&rdquo; claim; a benchmark that reports its one
honest reversal earns more trust than one that pretends none exists.</p>
</div>

<div class="card">
<h2><span class="n">4</span>NOT SCORABLE vs an F</h2>
<p>An <b>F</b> is the worst kind of real storefront: it was measured and largely
cannot serve an agent. <b>NOT SCORABLE</b> (grade <span class="chip">N/A</span>,
overall shown as <b>n/a</b>) is different &mdash; it means <b>no pillar was
observable at all</b> (for example, a domain that never loaded in static-only
mode). Reporting that as a 0/F would invent a verdict the evidence doesn&rsquo;t
support, so ASRS shows N/A instead. Any domain with even one observable pillar
gets a real score, so this path never touches normally-reachable sites.</p>
</div>

<div class="card">
<h2><span class="n">5</span>Attribution honesty &mdash; agent-side vs site-side</h2>
<p>Behavioral runs use headless shopper agents. When an agent&rsquo;s <b>own
hosting stack</b> refuses to load the site (its browser sandbox blocks the
navigation), that run observed <b>nothing about the site</b>. It is excluded
from the outcome and trust denominators and surfaced instead as a
<b>hosted-agent-reachability</b> access signal &mdash; an agent-side failure is
never scored as if it were the site&rsquo;s fault.</p>
<p>The reverse is enforced just as hard: a <b>site-side</b> block &mdash; a 403
to agent user-agents, a Cloudflare challenge, a CAPTCHA wall, a 429, a WAF
rule &mdash; <b>is</b> the site&rsquo;s evidence and is scored as such. When in
doubt, a run is CANT_TEST, never a fabricated FAIL.</p>
</div>

<div class="card">
<h2><span class="n">6</span>The behavioral panels &amp; refusal semantics</h2>
<p>The <b>shopper panel</b> is a set of headless agents given a real buying
directive; their run produces the outcome checkpoints (found product, understood
pricing, found a purchase path, a machine-payable path, no human gate). The
<b>trust panel</b> asks whether an agent, explicitly <b>directed by its user to
buy here</b>, will proceed. A confident refusal <b>despite that directive</b> is
a genuine trust signal and caps the grade (see below); a mere warning deducts
points but never caps. Refusals caused by the agent&rsquo;s own environment are
attribution-routed per section 5, not counted as the site refusing.</p>
<p>Those directives are <b>offering-relative</b>, not a fixed script. Before the
panel runs, ASRS reads what the storefront <b>claims to sell</b> from its own
published surfaces and gives the agent one task per capability it actually offers
&mdash; an archetype the site does <b>not</b> advertise is never probed, so a low
number is never a task the storefront was never built to answer (the same
attribution honesty as section&nbsp;5, applied to tasks). The task is also
<b>worded in the site&rsquo;s own terms</b>: a digital-good task asks the agent to
&ldquo;obtain one <b>generated image</b>&rdquo; only because the storefront&rsquo;s
own surfaces describe a generated image &mdash; the media noun comes from the
site, not from ASRS. That noun is derived <b>only</b> from ASRS&rsquo;s own
vendor-neutral media vocabulary (a generic <code>image</code>, <code>video</code>,
<code>audio</code> or <code>art</code>; a <b>generated render</b> for a
render-generation service that names no other medium; or a plain <b>digital
output</b> when the site gives no cleaner hint) matched against the
site&rsquo;s surfaces &mdash; never by pasting arbitrary site prose into the
agent&rsquo;s directive, so the task stays <b>injection-safe</b> and names no
vendor product. The descriptor takes the <b>most specific</b> output the site
claims: a service that names an <code>image</code> keeps &ldquo;generated
image&rdquo; even if it also advertises a render, so the render noun surfaces
only when it is the <b>only</b> output the site describes. Recognition is
<b>form-normalized</b>: a storefront that describes its output as an
<code>image</code>, as <code>images</code>, or as <code>generating images</code>
yields the <b>same</b> singular task noun, so two storefronts offering the same
capability get the <b>same task</b> regardless of how each phrases it &mdash; a
property pinned by an <b>executable regression test</b>. This battery is
<b>diagnostic</b> &mdash; it measures readiness within the archetypes a site
serves, <b>off the scoring path</b> &mdash; not a scored pillar.</p>
</div>

<div class="card">
<h2><span class="n">7</span>Reproducibility &mdash; is the number safe to cite?</h2>
<p>Behavioral panels run <b>multiple trials by default</b>. ASRS reports a
within-panel <b>verdict stability</b> (do the trials agree on the same task
outcome?) and a one-bit <b>quotability</b> verdict &mdash; <b>Citable</b> when
the headline is static-deterministic or reproducible across trials,
<b>Provisional</b> when it rests on a single trial or an unstable panel. The
number travels with its own reproducibility so a reader knows how much to lean
on it. (The one real free-tier transaction still runs only once per scored run,
regardless of trial count &mdash; see section 10.)</p>
</div>

<div class="card">
<h2><span class="n">8</span>Calibration &mdash; does the score predict what an agent experiences?</h2>
<p>Section&nbsp;7 asks whether the number is <b>stable</b> &mdash; do repeated
trials agree? A harder question is whether it is <b>valid</b>: does a static score
computed from a storefront&rsquo;s <b>published surfaces</b> actually predict what
a <b>live agent encounters</b> when it tries to buy? A benchmark can be perfectly
reproducible and still measure the wrong thing &mdash; the <i>&ldquo;the number is
astrology&rdquo;</i> objection. ASRS answers it by holding a static prediction up
against a real behavioral run and checking the two <b>agree</b>.</p>
<p>The load-bearing static claim is <b>agent-native payment</b>: the
transactability signal predicts an agent can pay programmatically. On a reference
storefront the static score marks payment-capable, a live shopper panel is run and
its outcome checkpoints &mdash; found a purchase path, reached a
<b>machine-payable path</b>, hit no human gate, completed a real free-tier
transaction &mdash; all <b>pass</b>. The static prediction is
<b>behaviorally corroborated</b>, not merely internally consistent: the number
matches the experience.</p>
<p>The agreement is <b>discriminating</b>, not a rubber stamp. The same behavioral
run carries genuine <b>failures</b> on other checks, so the payment passes are
<b>earned</b> rather than a panel that approves everything; and the static
prediction <b>separates tiers</b> &mdash; a no-rails storefront is predicted to
have <b>no</b> agent-native payment, which is exactly where a live agent hits a
wall. The corroboration is itself reproducible: both trials agreed on the
machine-payable verdict.</p>
<p>The check is now <b>two-sided</b>. The mirror case has been run end-to-end: on a
<b>no-rails retail storefront</b> the static score predicts <b>no</b> agent-native
payment, and a live shopper panel confirms it &mdash; the agent genuinely browses
the store but hits a <b>machine-payable</b> wall and a <b>human gate</b>, both
outcome checkpoints <b>fail</b>, reproducibly across trials. That failure is
<b>legible, not a blank</b>: the storefront is reachable and the agent completes
real browsing, so the stall is <i>evidence</i> the site lacks agent-native payment,
never something that couldn&rsquo;t be observed. At the <b>same payment
checkpoints</b>, the with-rails storefront <b>passes</b> and the no-rails one
<b>fails</b> &mdash; the prediction tracks the experience in <b>both
directions</b>.</p>
<p>The negative floor is not a <b>retail artifact</b> &mdash; a shop marked down
merely for selling physical goods. It has been measured on two structurally
different no-rails storefronts &mdash; a no-rails <b>API</b> and a no-rails
<b>retail shop</b> &mdash; and both land on the <b>identical</b> transactability
floor, earned by the identical per-check evidence, with the agent-native payment
check at <b>zero</b> on each. So the low score is attributably the <b>absence of
agent-native payment</b>, not the storefront&rsquo;s category: the negative
prediction is <b>storefront-type-invariant</b>.</p>
<p>The mirror holds for the <b>ceiling</b>. Just as the low score is not a category
artifact, the high one is not a <b>premium-category artifact</b> &mdash; a rich
storefront rated well merely for being sophisticated. Take the with-rails
storefront and <b>knock out its agent-native payment capability</b> &mdash;
substitute the no-rails storefront&rsquo;s earned evidence on exactly the payment
checks, leaving every other check untouched &mdash; then recompute the pillar with
the scorer&rsquo;s own formula: it <b>collapses exactly onto the no-rails
floor</b>. So <b>all</b> of the ceiling&rsquo;s separation from the floor is the
agent-native payment capability and nothing else &mdash; a falsifiable
<b>counterfactual</b>, not a decomposition of totals that could hide an offsetting
cancellation. And it is not an artifact of the shipped rubric&rsquo;s weights:
re-derived under <b>arbitrary re-weightings</b> of the transactability checks, the
knocked-out ceiling lands on the re-weighted floor <b>every time</b>. Strip payment
and the ceiling meets the floor at <b>every weighting</b> &mdash; the attribution is
<b>structural</b>, not a weighting choice.</p>
<p>That counterfactual lands on the transactability <b>pillar</b>, but the number a
reader actually <b>cites</b> is the <b>overall</b> score, which the rubric rolls up
across five weighted pillars &mdash; transactability is only <b>0.30</b> of it. A
skeptic could grant the pillar attribution yet argue the <b>headline</b> gap is
really carried by other pillars once that weight dilutes payment. So run the same
knock-out through the scorer&rsquo;s <b>own roll-up</b>, not a pillar in isolation:
substitute the no-rails storefront&rsquo;s earned evidence on the payment checks,
leave every other check untouched, and re-score. The with-rails overall <b>collapses
a full grade tier across the passing boundary</b> &mdash; a passing storefront turns
failing &mdash; while every non-payment pillar stays byte-identical and no cap
changes, so the entire drop flows through the payment-driven transactability
collapse and nothing else. That single capability closes <b>about two-thirds</b> of
the with-rails/no-rails headline gap: agent-native payment is the <b>single majority
driver</b> of the number people quote, not a minor contributor the pillar weights
bury.</p>
<p>The honest complement matters as much as the claim. Stripping payment does
<b>not</b> drag the with-rails overall all the way down to the no-rails score &mdash;
a residual gap remains, carried by a <b>non-payment</b> pillar: the with-rails
storefront documents its offer far more machine-<b>legibly</b> (it publishes the
machine-readable agent guide the no-rails store lacks). Run the same knock-out on
<b>that</b> family &mdash; substitute the no-rails evidence on the two
agent-legibility checks and re-score through the roll-up &mdash; and it closes
<b>about one-third</b> of the headline gap, the near-exact complement of
payment&rsquo;s two-thirds: the two capability families are <b>near-additive</b> and
together account for the <b>whole</b> delta, with <b>no third, unnamed driver</b>
hiding in the weighted roll-up. So the headline delta is payment-<b>dominated</b>,
not payment-<b>exclusive</b>: roughly two-thirds agent-native payment, about
one-third an earned <b>legibility</b> difference &mdash; the honest minority the
pitch does not get to claim. And that minority is not a paper advantage. On the live
behavioral run the with-rails shopper actually <b>found the product</b> and
<b>understood the pricing</b>, while the no-rails shopper did <b>neither</b> &mdash;
Access fully credited on both, so the no-rails failure is a comprehension wall, not
un-observability. So the &ldquo;understand the offer&rdquo; third is <b>two-sided in
experience</b>, the same way agent-native payment is &mdash; a lived capability
difference, not merely a static residual. Like the pillar counterfactual, both the
one-third fraction and the two-sided experience are pinned by <b>executable
regression tests</b> &mdash; so &ldquo;payment drives the majority, legibility the
honest rest&rdquo; is <b>checked, not asserted</b>.</p>
<p>Everything so far checks the number against the experience on each storefront
<b>separately</b>. But the claim a reader actually <b>cites</b> is a <b>ranking</b>
&mdash; a grade of <b>B versus F</b>, which storefront is more agent-ready &mdash; and a
ranking has its own failure mode: a reweighting could keep every single-storefront
checkpoint green yet <b>invert the order</b>, so the score names one winner while the
agent&rsquo;s lived outcome names the other. It does not. The static prediction and the
behavioral outcome are <b>rank-concordant &mdash; no sign inversion</b>: on <b>every</b>
static-observable pillar the with-rails side ranks at least as high as the no-rails side
and <b>strictly higher on payability</b>, and the behavioral-only <b>outcome</b> pillar
points the <b>same way</b> (a completed machine-payable transaction versus a hard stall).
Crucially this is <b>amplification, not rescue</b>: the cited headline ordering already
held on the <b>static prediction alone</b>, before the behavioral outcome was folded in
&mdash; the live run <b>confirms</b> the direction the static number already pointed, it
does not manufacture it. And the concordance is <b>honestly scoped</b>, not
&ldquo;the with-rails side wins everything&rdquo;: one behaviorally augmented pillar
&mdash; <b>trust</b> &mdash; legitimately <b>favors the no-rails storefront</b>, and
access is a <b>tie</b>, so the ranking is carried by the <b>capability pillars</b>,
exactly where agent-native payment lives. Like the rest of this section, the
no-inversion property is pinned by an <b>executable regression test</b>.</p>
<p>Two honest limits keep this from over-claiming. The positive direction is still
anchored on a <b>single with-rails run</b>; the negative floor now spans <b>two
storefront types</b>, but neither direction is yet corroborated across a full
<b>population</b> of real merchants.
And the whole check stays inside the <b>$0 free tier</b> (section&nbsp;10): the
agent completes a real machine-payable path, or is confirmed to have none, without
ever signing a nonzero-value authorization. Within that scope the two-sided
property is pinned by an <b>executable regression test</b>, enforced every cycle
&mdash; so &ldquo;the score predicts the experience&rdquo; is <b>checked, not
asserted</b>.</p>
</div>

<div class="card">
<h2><span class="n">9</span>Grade bands &amp; caps</h2>
<p>Points map to a letter grade by these bands: {band_str}. But critical
failures <b>cap</b> the grade regardless of points &mdash; averages hide
showstoppers, so a single fatal defect limits the letter (the SSL&nbsp;Labs
pattern):</p>
<table><tr><th>Cap finding</th><th class="num">Grade ceiling</th><th>Why</th></tr>{cap_rows}</table>
</div>

<div class="card">
<h2><span class="n">10</span>The $0 free-tier probe</h2>
<p>Where a site advertises a free-tier or zero-value allowance, one scored run
may make <b>exactly one real transaction &mdash; and only at $0</b>. No code path
signs a nonzero-value authorization, funds a wallet, or creates an account;
probe keys are ephemeral. This keeps the transactability evidence real (an
agent genuinely completed a machine-payable path) without ever spending money or
leaving a footprint on the merchant.</p>
</div>

<div class="card">
<h2><span class="n">11</span>Versioned comparability &amp; evidence</h2>
<p>Every report embeds the rubric version, and <b>scores are comparable only
within a version</b> (the SSL&nbsp;Labs / Euro&nbsp;NCAP pattern): any change to
a weight, cap, or check bumps the version with a dated changelog entry. Every
scored claim traces to a committed artifact &mdash; a probe report, a panel
transcript, or a test. If it wasn&rsquo;t observed, it wasn&rsquo;t scored.</p>
</div>

<p class="sub" style="margin-top:16px">
<a href="rubric.html">Read the rubric &amp; every check, verbatim &rarr;</a></p>
</div></body></html>"""
    path = out_dir / "methodology.html"
    path.write_text(head + body)
    return str(path)


# Status inks for the canonical-delta bands — reserved status colors (never a
# categorical series hue), each shipped WITH its band label so the encoding is
# never color-alone. Read straight off canonical_history's band names.
_HISTORY_BAND_COLOR = {
    "in-band": "#067647",   # green — live delta reproduces the pinned fixture delta
    "drifting": "#b54708",  # amber — notable but partial move off the baseline
    "diverged": "#b42318",  # red — live delta no longer reproduces the pinned delta
    "no-data": "#667085",   # neutral tertiary — no reading
}
_HISTORY_BAND_LABEL = {
    "in-band": "In-band",
    "drifting": "Drifting",
    "diverged": "Diverged",
}

# Colour for the synthesized re-capture recommendation chip, keyed on the
# canonical_history REC_* code. Reuses the band inks so the surface reads as one
# system: green = no action (baseline valid), amber = hold (jitter not yet
# sustained, or defer to a recovering reference), red = a real move that is a
# [LOCAL] re-capture candidate, neutral = needs a human look. Never colour-alone —
# the label text and the full reason always render alongside it.
_HISTORY_REC_COLOR = {
    "baseline-valid": "#067647",
    "wait-not-yet-sustained": "#b54708",
    "defer-reference-degraded": "#b54708",
    "recapture-candidate": "#b42318",
    "review-no-anchor": "#667085",
    "review-side-ambiguous": "#667085",
}


def _history_trend_svg(points: list, baseline: float) -> str:
    """A single-series change-over-time trend: the live canonical delta per re-score,
    with the pinned-fixture baseline as a dashed reference line. One series, so no
    legend for identity; each point is colored by its divergence BAND (a reserved
    status encoding, named in the band legend below the chart, never color-alone).
    """
    from . import canonical_history as ch

    if not points:
        return ""
    W, H = 780.0, 220.0
    padL, padR, padT, padB = 48.0, 18.0, 16.0, 30.0
    deltas = [p.delta for p in points]
    vals = deltas + [baseline]
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        lo, hi = lo - 1.0, hi + 1.0
    pad = (hi - lo) * 0.10
    lo, hi = lo - pad, hi + pad
    span = hi - lo
    n = len(points)

    def x_of(i: int) -> float:
        if n == 1:
            return (padL + (W - padR)) / 2.0
        return padL + (W - padR - padL) * i / (n - 1)

    def y_of(v: float) -> float:
        return (H - padB) - (v - lo) / span * (H - padB - padT)

    # y-axis reference labels: the plot floor, the baseline, and the plot ceiling.
    yticks = sorted({lo + pad, baseline, hi - pad})
    axis = "".join(
        f'<line x1="{padL:.1f}" y1="{y_of(t):.1f}" x2="{W - padR:.1f}" '
        f'y2="{y_of(t):.1f}" stroke="#eef0f3" stroke-width="1"/>'
        f'<text x="{padL - 6:.1f}" y="{y_of(t) + 3.5:.1f}" text-anchor="end" '
        f'font-family="DM Mono,monospace" font-size="10" fill="#667085">'
        f'{t:+.1f}</text>'
        for t in yticks
    )
    # Baseline (pinned-fixture delta) as a dashed reference line, labeled at the end.
    base_y = y_of(baseline)
    baseline_mark = (
        f'<line x1="{padL:.1f}" y1="{base_y:.1f}" x2="{W - padR:.1f}" '
        f'y2="{base_y:.1f}" stroke="#98a2b3" stroke-width="1.5" '
        f'stroke-dasharray="5 4"/>'
        f'<text x="{W - padR:.1f}" y="{base_y - 6:.1f}" text-anchor="end" '
        f'font-family="Inter,sans-serif" font-size="11" fill="#667085">'
        f'baseline {baseline:+.1f}</text>'
    )
    # The delta series: a recessive connecting line, then a status-colored dot per
    # reading. 2px surface ring on each dot so overlapping points stay separable.
    poly = " ".join(f"{x_of(i):.1f},{y_of(p.delta):.1f}" for i, p in enumerate(points))
    line = (
        f'<polyline points="{poly}" fill="none" stroke="#d0d5dd" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    dots = []
    for i, p in enumerate(points):
        band = ch.band_for_delta(p.delta, baseline)
        color = _HISTORY_BAND_COLOR.get(band, "#667085")
        last = i == n - 1
        r = 4.5 if last else 3.0
        dots.append(
            f'<circle cx="{x_of(i):.1f}" cy="{y_of(p.delta):.1f}" r="{r:.1f}" '
            f'fill="{color}" stroke="#fff" stroke-width="2">'
            f'<title>{_esc(ch._short_ts(p.ts))}: delta {p.delta:+.1f} '
            f'({_HISTORY_BAND_LABEL.get(band, band)})</title></circle>'
        )
    # Direct-label the latest point only (never a number on every point).
    lastp = points[-1]
    lx, ly = x_of(n - 1), y_of(lastp.delta)
    anchor = "end" if n > 1 else "middle"
    lxoff = -8 if n > 1 else 0
    last_label = (
        f'<text x="{lx + lxoff:.1f}" y="{ly - 9:.1f}" text-anchor="{anchor}" '
        f'font-family="DM Mono,monospace" font-size="11" font-weight="500" '
        f'fill="#0c111d">{lastp.delta:+.1f}</text>'
    )
    return (
        f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" '
        f'style="max-width:{W:.0f}px;height:auto" role="img" '
        f'aria-label="Live canonical delta per re-score versus the pinned '
        f'fixture baseline of {baseline:+.1f}">'
        f'{axis}{baseline_mark}{line}{"".join(dots)}{last_label}</svg>'
    )


def _write_canonical_history_page(out_dir: Path, history=None) -> str:
    """Render canonical-history.html — the HTML surface for the live canonical-delta
    trend the terminal ``asrs canonical-history`` computes.

    The local verify runner commits a live static re-score of the benchmark's own
    reference pair every fire; ``asrs.canonical_history`` reads that committed series
    into a delta trend, a divergence band, a sustained-drift run, PILLAR attribution
    (which pillar moved) and a SIDE/direction cause (no-rails gaining vs with-rails
    softening). That whole diagnosis was terminal-only; this renders it so a reader
    eyeballs the curve, the named mover, and which side drove it.

    Reference-pair host names appear here only as DATA — the page is literally ABOUT
    those two domains, exactly as the committed fixtures, the verify series, and
    ``test_canonical_replay`` name them. This is the SAME engineering-history category
    as ``rubric.html`` (whose changelog names the pair): both are deliberately OUT OF
    SCOPE for the vendor-neutral-wording scanner, which guards the capability-worded
    CHECK prose (methodology + card), not pages that report on the reference pair.
    Display-only: imports no scoring code, moves no score, rubric untouched.
    """
    from . import canonical_history as ch

    # When loading the live series ourselves (the hosted build_scorecard path),
    # supply the wall clock so the freshness check runs — the same clock the CLI
    # passes to ``asrs canonical-history``. A caller that hands us a ``history``
    # controls its own liveness (tests summarize with an explicit ``now``); a
    # series summarized without a clock carries liveness=None and shows no age
    # qualifier (honest — no clock-dependent claim).
    hist = (
        history
        if history is not None
        else ch.load_history(now=datetime.now(timezone.utc))
    )
    head = _PROSE_HEAD.format(title="ASRS — live canonical-delta history")
    nav = (
        '<div class="nav"><a href="javascript:history.back()">&larr; Back to the '
        'scorecard</a><a href="methodology.html">Methodology</a>'
        '<a href="rubric.html">Rubric &amp; checks</a></div>'
    )
    intro = f"""<h1>Live canonical-delta history</h1>
<p class="sub">The benchmark reading its own regression signal over time</p>
<div class="card">
<h2>What this tracks</h2>
<p>Every hour a companion runner re-scores the benchmark&rsquo;s reference pair
live &mdash; a storefront <b>without</b> agent-native rails against one <b>with</b>
them &mdash; and commits the result. The gap between them (the <b>delta</b>) is the
benchmark&rsquo;s headline claim; the committed fixtures pin it at
<span class="chip">{ch._fmt_delta(hist.baseline_delta)}</span>. This page reads that
committed series and asks one question a single reading can&rsquo;t answer: is a move
off the pinned delta ordinary live/static <b>jitter</b>, or a <b>sustained</b>
real-world change under the benchmark? One out-of-band reading is jitter; several in
a row is a real move.</p>
<p>A move is read in <b>capability terms</b>, not by identity: which pillar shifted,
and which <b>side</b> drove it &mdash; the no-rails floor <b>gaining</b> capability
(the real gap closing) or the with-rails reference <b>softening</b> (a site
regression, where the pinned fixture still represents the true gap). The pinned
delta is unchanged by this page; the in-cloud replay guard reproduces it from the
committed fixtures regardless of what the live site does today.</p>
</div>"""

    if hist.latest is None:
        body = f"""{nav}{intro}
<div class="card"><h2>No readings yet</h2>
<p>No usable live re-score artifacts were found, so there is no trend to show.</p></div>
<p class="sub" style="margin-top:16px">
<a href="methodology.html">How the score is measured &rarr;</a></p>
</div></body></html>"""
        path = out_dir / "canonical-history.html"
        path.write_text(head + body)
        return str(path)

    latest = hist.latest
    div = hist.divergence
    band = hist.band
    band_color = _HISTORY_BAND_COLOR.get(band, "#667085")
    verdict = ch._BAND_VERDICT.get(band, "")
    window = 60
    tail = hist.points[-window:]
    chart = _history_trend_svg(tail, hist.baseline_delta)

    # Band legend — the reserved status encoding, named so the chart is never
    # color-alone (the one accessibility obligation of a status-colored series).
    legend_items = "".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:16px;'
        f'font-size:12px;color:#475467"><span style="width:10px;height:10px;'
        f'border-radius:50%;background:{_HISTORY_BAND_COLOR[k]};'
        f'display:inline-block;margin-right:6px"></span>{_esc(v)}</span>'
        for k, v in _HISTORY_BAND_LABEL.items()
    )

    # Cycle 51 made the newest re-score's AGE an executable, surfaced fact in the
    # TERMINAL readout: a stalled verify runner can leave a healthy-looking, in-band
    # verdict that is hours stale, and a reader who mistakes AGE for CONFIRMATION is
    # trusting an observation that may no longer hold. That freshness signal was
    # terminal-only. Surface it here so a web reader sees the same qualifier BEFORE
    # the (possibly stale) verdict — the same terminal->HTML close-out per_kind
    # (Cycle 10->12), between_kind_spread (Cycle 18->20) and the noise floor
    # (Cycle 47->48) took. Renders only when the caller supplied a clock (liveness
    # computed); a pure point-series summary makes no clock-dependent claim, so no
    # banner. STALE is a prominent warning card ABOVE the latest reading (warn
    # before the stale content); FRESH is a quiet one-line age note.
    liveness_banner = ""
    live = hist.liveness
    if live is not None:
        floor = live.stale_floor_hours
        if not live.fresh:
            stale_color = _HISTORY_BAND_COLOR["diverged"]
            liveness_banner = (
                f'<div class="card" style="border-color:{stale_color};'
                f'background:#fffafa">'
                f'<h2 style="color:{stale_color}">&#9888; Live signal STALE '
                f'&mdash; newest re-score {live.age_hours:.1f}h old</h2>'
                f'<p>The newest live re-score is past the {floor:.0f}h freshness '
                f'floor &mdash; the same floor the playbook uses to declare the '
                f'verify runner down. <b>The verdict below describes an OLD crawl, '
                f'not the reference pair now</b>; the local verify runner may be '
                f'down. Read the age, not just the band.</p></div>'
            )
        else:
            in_color = _HISTORY_BAND_COLOR["in-band"]
            liveness_banner = (
                f'<p class="sub" style="margin:-6px 0 20px;color:{in_color}">'
                f'Live signal: newest re-score {live.age_hours:.1f}h old '
                f'&mdash; fresh (within the {floor:.0f}h floor); the verdict below '
                f'is a current reading.</p>'
            )

    # The loader silently drops artifacts scored on a red bench (Cycle-215
    # versioned-comparability gate) or malformed, so the "N live re-scores" count is
    # the FILTERED series, not the raw one. Surface the exclusion accounting so a web
    # reader sees the series is filtered and on what grounds — the terminal->HTML
    # close-out of the Cycle-216 loader-accounting readout. Renders only when the
    # loader actually dropped something (accounting present with excluded > 0); a
    # clean load shows nothing (raw == filtered, honest silence).
    acct = hist.load_accounting
    series_filtered_note = ""
    if acct is not None and acct.any_excluded:
        series_filtered_note = (
            f'<p class="q" style="margin-top:-8px">Series filtered: '
            f'{acct.included} of {acct.total} artifacts kept, {acct.excluded} '
            f'excluded ({_esc(ch._exclusion_phrase(acct))}) &mdash; red-bench '
            f'readings were scored while the bench&rsquo;s own guards were red (not '
            f'comparable within the version); malformed ones were unusable.</p>'
        )
        # The counts NAME what was dropped; this JUDGES whether the drop compromises
        # the series the drift verdict is drawn from (Cycle 217 METHOD) — the
        # terminal->HTML close-out of the integrity verdict, mirroring ch.render.
        integ = hist.integrity
        if integ is not None:
            rb = (
                f", {integ.excluded_red_bench} of them red-bench"
                if integ.excluded_red_bench
                else ""
            )
            if integ.intact:
                series_filtered_note += (
                    f'<p class="q" style="margin-top:-8px">Series integrity: '
                    f'<b>intact</b> &mdash; {integ.excluded}/{integ.total} '
                    f'({integ.excluded_fraction * 100:.0f}%) excluded{rb}, within the '
                    f'{integ.floor * 100:.0f}% floor; the drift verdict rests on a '
                    f'representative series.</p>'
                )
            else:
                series_filtered_note += (
                    f'<p class="q" style="margin-top:-8px;color:'
                    f'{_HISTORY_BAND_COLOR["diverged"]}">Series integrity: '
                    f'<b>DEGRADED</b> &mdash; {integ.excluded}/{integ.total} '
                    f'({integ.excluded_fraction * 100:.0f}%) of the committed series '
                    f'excluded{rb}, past the {integ.floor * 100:.0f}% floor; the drift '
                    f'verdict rests on a thinned/biased remnant &mdash; weigh it with '
                    f'caution.</p>'
                )
    latest_card = f"""<div class="card">
<h2>Latest reading</h2>
<p style="margin-bottom:14px">{_esc(ch._short_ts(latest.ts))} &middot;
{len(hist.points)} live re-scores over
{_esc(ch._short_ts(hist.points[0].ts))} &rarr; {_esc(ch._short_ts(latest.ts))}</p>
{series_filtered_note}
<table>
<tr><th>Side</th><th class="num">Overall</th><th>Grade</th></tr>
<tr><td>{_esc(ch.CANONICAL_NO_RAILS)} <span class="q">(no rails)</span></td>
<td class="num">{latest.no_rails_overall:.1f}</td><td>{_esc(latest.no_rails_grade)}</td></tr>
<tr><td>{_esc(ch.CANONICAL_WITH_RAILS)} <span class="q">(with rails)</span></td>
<td class="num">{latest.with_rails_overall:.1f}</td><td>{_esc(latest.with_rails_grade)}</td></tr>
<tr><td><b>Delta</b> <span class="q">(with &minus; without)</span></td>
<td class="num"><b>{ch._fmt_delta(latest.delta)}</b></td><td></td></tr>
</table>
<p style="margin-top:12px">Divergence from the pinned baseline
<span class="chip">{ch._fmt_delta(hist.baseline_delta)}</span>:
<b style="color:{band_color}">{ch._fmt_delta(div)}</b> &mdash;
<b style="color:{band_color}">{_esc(_HISTORY_BAND_LABEL.get(band, band.upper()))}</b>,
{_esc(verdict)}.</p>"""
    if hist.consecutive_out_of_band >= 1:
        nrun = hist.consecutive_out_of_band
        kind = "sustained" if nrun >= 3 else "recent"
        latest_card += (
            f'<p><b>{_esc(kind.title())}:</b> {nrun} consecutive re-score(s) '
            f'out of band (|delta &minus; baseline| &gt; {ch._BAND_IN:.1f}).</p>'
        )
        # The count says HOW MANY trailing readings are out of band; the span says
        # over how much WALL-CLOCK TIME they persist (SustainedRun, TRUTH Cycle 175):
        # three readings a minute apart are far weaker evidence of a durable real-world
        # change than three spanning a day. Surface the span as a dimmed sub-line so the
        # card names the drift's persistence in time, not just its reading-count. Omitted
        # (honest-None) when either endpoint timestamp is unparseable — the same
        # discipline the terminal render follows.
        sr = hist.sustained_run
        if sr is not None:
            latest_card += (
                f'<p class="q" style="margin-top:-6px">spanning {sr.span_hours:.1f}h '
                f'({_esc(ch._short_ts(sr.first_ts))} &rarr; '
                f'{_esc(ch._short_ts(sr.latest_ts))}).</p>'
            )
    latest_card += "</div>"

    chart_card = f"""<div class="card">
<h2>Delta trend</h2>
<p style="margin-bottom:10px">Live canonical delta per re-score (last
{len(tail)}), against the dashed pinned-fixture baseline. Each point is colored by
its divergence band; hover a point for its timestamp and value.</p>
{chart}
<div style="margin-top:10px">{legend_items}</div>
</div>"""

    # Cycle 45 measured whether the ±band is genuine site-transient absorption or just
    # measurement noise; Cycle 47 measured the strictly stronger fact — whether the
    # stable delta is PER-SIDE determinism or two lock-step drifts merely cancelling in
    # the difference (the fair objection a critic raises about any "stable benchmark
    # delta"). That whole calibration was terminal-only. Surface it here so a reader who
    # never opens a terminal sees WHY the band is trustworthy. Renders whenever the floor
    # is measurable (>= 2 in-band readings); silent otherwise (honest — no floor to show).
    noise_card = ""
    nf = hist.noise_floor
    if nf is not None:
        if nf.deterministic:
            headline = (
                f'<b style="color:{_HISTORY_BAND_COLOR["in-band"]}">DETERMINISTIC at rest'
                f'</b> &mdash; the &plusmn;{ch._BAND_IN:.1f} band absorbs real-world site '
                f'transients, not measurement noise'
            )
            # Per-side determinism is STRICTLY STRONGER than a deterministic delta: a
            # deterministic delta is also consistent with two lock-step drifts cancelling,
            # which the delta-only measure cannot rule out. Only claim it when BOTH sides
            # are exact; otherwise stay silent on it (the cancellation case Cycle 47 guards).
            sides = ""
            if nf.sides_deterministic:
                sides = (
                    f'<p style="margin-top:10px"><b>Per-side:</b> both reference '
                    f'storefronts reproduce their pinned overall <b>exactly</b> at rest '
                    f'(&sigma; {_esc(ch.CANONICAL_NO_RAILS)}={nf.no_rails_stddev:.2f}, '
                    f'{_esc(ch.CANONICAL_WITH_RAILS)}={nf.with_rails_stddev:.2f}) &mdash; '
                    f'the stable delta is genuine per-side determinism, not two drifts '
                    f'cancelling in the difference.</p>'
                )
        else:
            sep = (
                "comfortably clears the observed jitter"
                if nf.band_well_separated
                else "is <b>too tight</b> for the observed jitter"
            )
            headline = f'the &plusmn;{ch._BAND_IN:.1f} in-band band {sep}'
            sides = ""
        noise_card = f"""<div class="card">
<h2>Is the band real noise, or transient absorption?</h2>
<p>A single reading can&rsquo;t say whether a move off the pinned delta is measurement
noise or a real change. This measures the at-rest dispersion of the reference pair over
its <b>{nf.n_in_band}</b> in-band re-scores: &sigma;={nf.stddev:.2f}, worst divergence
{nf.max_abs_divergence:.2f}. {headline}.</p>
{sides}
</div>"""

    diag_card = ""
    attr = hist.attribution
    cause = hist.divergence_cause
    if attr is not None or cause is not None:
        diag_card = '<div class="card"><h2>What moved, and which side</h2>'
        if attr is not None and attr.top is not None:
            top = attr.top
            verb = "fell" if top.change < 0 else "rose"
            diag_card += (
                f'<p><b>Pillar:</b> {_esc(top.domain)} {_esc(top.pillar)} {verb} '
                f'{top.before:.1f} &rarr; {top.after:.1f} '
                f'({top.change:+.1f}) &mdash; the largest pillar move '
                f'(vs the last in-band reading {_esc(ch._short_ts(attr.anchor_ts))}).</p>'
            )
            others = attr.moves[1:3]
            if others:
                more = "; ".join(
                    f"{_esc(m.domain)} {_esc(m.pillar)} "
                    f"{m.before:.1f}&rarr;{m.after:.1f} ({m.change:+.1f})"
                    for m in others
                )
                diag_card += f'<p class="q">Also: {more}</p>'
        elif attr is not None:
            diag_card += (
                '<p><b>Pillar:</b> the overall delta moved but no single pillar '
                'isolated (a pillar was unobserved on one side).</p>'
            )
        # The at-rest dispersion of THAT fingered pillar (attributed_pillar_noise_floor,
        # TRUTH Cycle 211): the overall noise-floor card above proves the DELTA is
        # deterministic at rest, but the drift the benchmark ATTRIBUTES and an operator
        # acts on is at the PILLAR level. This proves the SAME fingered pillar reproduces
        # its value exactly at rest, so the attributed move is signal, not pillar-level
        # jitter — the pillar-granularity mirror of the overall noise-floor card.
        # Rendered right below the Pillar line it qualifies (attr.top gives the move
        # magnitude). None (and so omitted) unless >= 2 in-band readings carry the pillar.
        pnf = hist.attributed_pillar_noise_floor
        if pnf is not None and attr is not None and attr.top is not None:
            move = attr.top.change
            if pnf.deterministic:
                diag_card += (
                    f'<p><b>At rest:</b> {_esc(pnf.domain)} {_esc(pnf.pillar)} is '
                    f'<b style="color:{_HISTORY_BAND_COLOR["in-band"]}">DETERMINISTIC</b> '
                    f'across its {pnf.n_in_band} in-band re-scores '
                    f'(&sigma;={pnf.stddev:.2f}) &mdash; the {move:+.1f} move is '
                    f'<b>signal, not pillar jitter</b>.</p>'
                )
            else:
                diag_card += (
                    f'<p><b>At rest:</b> {_esc(pnf.domain)} {_esc(pnf.pillar)} varies '
                    f'&sigma;={pnf.stddev:.2f} (worst {pnf.max_abs_divergence:.2f}) over '
                    f'its {pnf.n_in_band} in-band re-scores &mdash; the {move:+.1f} move '
                    f'against the at-rest pillar jitter.</p>'
                )
        # Whether that fingered pillar HOLDS across the whole trailing out-of-band
        # run or WANDERS reading-to-reading (AttributionStability, TRUTH Cycle 183) —
        # the credibility measure on the single-snapshot Pillar line above. Rendered
        # between the Pillar (what moved) and Side (which side) lines so the card
        # reads in the same order the terminal readout does. None (and so omitted)
        # unless the run is >= 2 out-of-band readings with an in-band anchor.
        stab = hist.attribution_stability
        if stab is not None:
            if stab.stable and stab.fingered is not None:
                dom, pil = stab.fingered
                diag_card += (
                    f'<p><b>Stability:</b> {_esc(dom)} {_esc(pil)} fingered by all '
                    f'{len(stab.readings)} out-of-band re-scores &mdash; '
                    f'<b>STABLE</b>, not wandering.</p>'
                )
            else:
                movers = (
                    "; ".join(f"{_esc(d)} {_esc(p)}" for d, p in sorted(stab.movers))
                    or "no single pillar isolated"
                )
                diag_card += (
                    f'<p><b>Stability:</b> the top mover <b>WANDERS</b> across '
                    f'{len(stab.readings)} out-of-band re-scores ({movers}) '
                    f'&mdash; the fingered pillar is not sustained.</p>'
                )
        if cause is not None:
            c_top = attr.top if attr is not None else None
            diag_card += f'<p><b>Side:</b> {_esc(ch.cause_verdict(cause, c_top))}.</p>'
        diag_card += "</div>"

    # The synthesized DECISION the drift diagnostics feed (Cycle 43): given the live
    # series, does the committed fixture still represent the true capability gap, or
    # should the pinned delta be re-captured [LOCAL]? Surfaced here so the HTML page
    # shows the same `re-capture:` line the terminal readout does — the recommendation,
    # never an action (moving the pinned baseline is a [LOCAL], comparability-affecting
    # step). Rendered whenever there is a reading (any code but the no-data sentinel).
    rec_card = ""
    adv = hist.recapture
    if adv is not None and adv.code != ch.REC_NO_DATA:
        rec_color = _HISTORY_REC_COLOR.get(adv.code, "#667085")
        rec_label = ch._REC_LABEL.get(adv.code, adv.code)
        # Whether that decision is CORROBORATED by both independent drift mechanisms —
        # the side-level cause (overalls) and the pillar-level attribution (per-pillar)
        # fingering the same side moving the same way (Cycle 208). It surfaces WHY the
        # recommendation holds — two independent decompositions concurring, not one
        # number — the crux the real-series guard pins internally. None (and so
        # omitted) unless both mechanisms are present with an isolated pillar.
        corr = hist.corroboration
        corr_p = ""
        if corr is not None:
            corr_p = (
                f'\n<p style="margin-top:12px"><b>Corroboration:</b> '
                f'{_esc(ch.corroboration_verdict(corr))}.</p>'
            )
        rec_card = f"""<div class="card">
<h2>Re-capture decision</h2>
<p>Does the committed fixture still represent the true capability gap, or has the
reference pair moved durably enough that the pinned delta should be re-captured?
This synthesizes the band, sustained-run, pillar and side diagnostics above into one
recommendation &mdash; a decision, never an action (re-capturing the pinned baseline
is a <span class="chip">[LOCAL]</span>, comparability-affecting step).</p>
<p style="margin-top:12px"><b style="color:{rec_color}">{_esc(rec_label)}</b>
&mdash; {_esc(adv.reason)}.</p>{corr_p}
</div>"""

    body = f"""{nav}{intro}
{liveness_banner}
{latest_card}
{chart_card}
{noise_card}
{diag_card}
{rec_card}
<p class="sub" style="margin-top:16px">
Read this live in a terminal: <span class="chip">python -m asrs canonical-history</span>
&middot; <a href="methodology.html">How the score is measured &rarr;</a></p>
</div></body></html>"""
    path = out_dir / "canonical-history.html"
    path.write_text(head + body)
    return str(path)


def _load_calibration_sweep() -> dict | None:
    """Read the NEWEST committed ``runs/local/calibration_sweep_*.json`` sweep, or
    None if none is present. The local runner half of the loop commits a dated
    static $0 population sweep; this module lives inside the repo so deriving the
    root from ``__file__`` is safe here (unlike the pinned runner)."""
    runs_dir = Path(__file__).resolve().parent.parent / "runs" / "local"
    paths = sorted(runs_dir.glob("calibration_sweep_*.json"))
    if not paths:
        return None
    try:
        return json.loads(paths[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_all_calibration_sweeps() -> list:
    """Read EVERY committed ``runs/local/calibration_sweep_*.json`` sweep, oldest
    first, skipping any that will not parse. The single-cadence drift card reads only
    the newest sweep's ``drift`` block (this-vs-prior); the population TREND across the
    whole committed cadence needs them all. Filenames are dated (``..._<ts>.json``) so
    sorting the glob is chronological. Same in-repo root as ``_load_calibration_sweep``."""
    runs_dir = Path(__file__).resolve().parent.parent / "runs" / "local"
    out = []
    for p in sorted(runs_dir.glob("calibration_sweep_*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out


# Static-sweep pillar order for the leaderboard columns — the same five pillars,
# outcome last (a static $0 sweep never runs a live shopper panel, so outcome is
# always null here; shown as "—", never a scored 0 — attribution honesty).
_SWEEP_PILLARS = ("access", "legibility", "transactability", "trust", "outcome")


def _fmt_sweep_ts(ts: str) -> str:
    """20260728T234815Z -> '20260728 234815' (display only)."""
    ts = str(ts or "")
    return f"{ts[:8]} {ts[9:15]}" if len(ts) >= 15 else ts


def _calibration_drift_card(drift) -> str:
    """Render the population-DRIFT card for calibration.html.

    The calibration sweep is re-run on a cadence; each dated dataset carries a
    ``drift`` block diffing it against the prior sweep (``experiments/
    calibration_sweep.py::_compute_drift``). That block was terminal/stderr-only
    until now — a committed dataset a reader could not see. A domain that ADDS or
    REMOVES agent-native rails moves its overall score between runs: a real
    capability change, the population-scale echo of the canonical pair's per-cycle
    regression check. A member that flips scored <-> not-scorable is a REACHABILITY
    change, never a capability move (invariant #4) — surfaced in its own row, never
    counted as a score delta. New / dropped members are listed, never averaged in (a
    broadened population is not a move). Display-only: reads the committed drift
    block, moves no score. Returns "" when there is no baseline (a first sweep).
    """
    if not isinstance(drift, dict):
        return ""
    base_disp = _fmt_sweep_ts(drift.get("baseline_ts", ""))
    n_compared = int(drift.get("n_compared", 0) or 0)
    n_moved = int(drift.get("n_moved", 0) or 0)
    max_abs = float(drift.get("max_abs_delta", 0.0) or 0.0)
    n_steady = max(n_compared - n_moved, 0)
    moved = [m for m in (drift.get("moved") or []) if m.get("delta")]
    moved.sort(key=lambda m: abs(float(m.get("delta", 0.0))), reverse=True)
    status_changed = drift.get("status_changed") or []
    added = drift.get("added_members") or []
    removed = drift.get("removed_members") or []

    # The canonical anchors' own per-cadence movement, straight from the data — the
    # population echo of the frozen reference delta the in-cloud replay guard defends.
    anchors = [
        m for m in (drift.get("moved") or [])
        if str(m.get("segment", "")).endswith("anchor")
    ]
    anchor_note = ""
    if anchors and all(not a.get("delta") for a in anchors):
        anchor_note = (
            '<p><b>Reference anchors held steady.</b> Both canonical anchors moved '
            '&Delta;&nbsp;0.0 across this cadence &mdash; the frozen reference delta the '
            'replay guard defends, seen through the population sweep.</p>'
        )

    if moved:
        def _delta_cell(d: float) -> str:
            color = "#067647" if d > 0 else "#b42318"
            return f'<td class="num" style="color:{color}">{d:+.1f}</td>'
        mv_rows = "".join(
            f'<tr><td><b>{_esc(m.get("domain", ""))}</b>'
            f'<div class="q">{_esc(m.get("segment", ""))}</div></td>'
            f'<td class="num">{float(m["baseline"]):.1f} &rarr; {float(m["current"]):.1f}</td>'
            f'{_delta_cell(float(m["delta"]))}</tr>'
            for m in moved
        )
        moved_block = (
            '<table><tr><th>Domain &amp; segment</th>'
            '<th class="num">Overall: was &rarr; now</th>'
            '<th class="num">&Delta;</th></tr>' + mv_rows + '</table>'
        )
    else:
        moved_block = (
            '<p>No domain scored in both sweeps moved &mdash; the whole population held '
            'its score across the cadence.</p>'
        )

    if status_changed:
        sc_rows = "".join(
            f'<tr><td><b>{_esc(s.get("domain", ""))}</b>'
            f'<div class="q">{_esc(s.get("segment", ""))}</div></td>'
            f'<td class="num">{_esc(str(s.get("baseline")))} &rarr; '
            f'{_esc(str(s.get("current")))}</td></tr>'
            for s in status_changed
        )
        status_block = (
            '<p style="margin-top:16px"><b>Reachability changes.</b> These members '
            'crossed the scored / not-scorable line between sweeps. That is an '
            '<b>observation</b> change (an agent-UA block appearing or lifting), '
            '<b>not</b> a capability move &mdash; listed here, never counted as a score '
            '&Delta; (attribution honesty).</p>'
            '<table><tr><th>Domain &amp; segment</th>'
            '<th class="num">Scorability: was &rarr; now</th></tr>' + sc_rows + '</table>'
        )
    else:
        status_block = ""

    membership = ""
    if added or removed:
        parts = []
        if added:
            parts.append(
                '<b>New to the population this run:</b> '
                + ", ".join(f'<span class="chip">{_esc(a)}</span>' for a in added)
            )
        if removed:
            parts.append(
                '<b>Dropped from the population:</b> '
                + ", ".join(f'<span class="chip">{_esc(r)}</span>' for r in removed)
            )
        membership = (
            '<p style="margin-top:16px">' + ' &middot; '.join(parts)
            + ' &mdash; new / dropped members are listed, never averaged into the drift '
            '(a broadened population is not a score move).</p>'
        )

    plural = "s" if n_compared != 1 else ""
    summary = (
        f'{n_moved} of {n_compared} domain{plural} scored in both sweeps moved '
        f'(max&nbsp;|&Delta;|&nbsp;{max_abs:.1f}); {n_steady} held steady.'
    )
    return f"""<div class="card">
<h2>Population drift <span style="color:#667085;font-weight:500">&middot; vs {_esc(base_disp)} UTC</span></h2>
<p>The sweep is re-run on a cadence; this compares it to the prior dated dataset. A
domain that <b>adds or removes agent-native rails</b> moves its overall score between
runs &mdash; a real capability change, the population-scale echo of the canonical
pair&rsquo;s per-cycle regression check. {summary}</p>
{anchor_note}
{moved_block}
{status_block}
{membership}
</div>"""


# Categorical hues for the reference-pair trend series — a small, fixed, brand-neutral
# palette assigned by RANK (highest-scoring anchor first), NOT by domain, so no series
# is favored by identity. Never color-alone: every series is named in the HTML legend.
_ANCHOR_TREND_COLORS = ("#175cd3", "#b54708", "#6941c6", "#0e7490")


def _sweep_date(ts: str) -> str:
    """20260728T234815Z -> '2026-07-28' (x-axis tick, display only)."""
    ts = str(ts or "")
    return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ts


def _anchor_trend_series(sweeps: list):
    """From an ordered (oldest-first) list of sweeps sharing ONE rubric version, pull
    the canonical ANCHORS' overall per sweep as aligned series.

    Anchors are the rows whose ``segment`` ends in ``anchor`` (the WITH-rails and
    no-rails reference storefronts the whole population sweep is calibrated around) —
    keyed by DOMAIN, so the series are read from the data, never a hard-coded name. A
    sweep in which an anchor is NOT SCORABLE contributes ``None`` at that index (a gap
    in the line), NEVER a 0 — attribution honesty: an unreachable anchor is an
    observation gap, not a score of zero. Returns ``(series, dates)`` where each series
    is ``{"domain", "segment", "points": [float|None, ...]}`` ordered by the anchor's
    LATEST scored overall descending (highest first), and ``dates`` is the per-sweep
    x-axis label list. Anchors with fewer than 2 scored points are dropped (no trend)."""
    dates = [_sweep_date(s.get("ts", "")) for s in sweeps]
    # domain -> {"segment": str, "points": [float|None per sweep]}
    by_domain: dict = {}
    for i, s in enumerate(sweeps):
        for r in s.get("rows", []) if isinstance(s, dict) else []:
            seg = str(r.get("segment", ""))
            if not seg.endswith("anchor"):
                continue
            dom = str(r.get("domain", ""))
            rec = by_domain.setdefault(dom, {"segment": seg, "points": [None] * len(sweeps)})
            ov = r.get("overall")
            if r.get("scored") and ov is not None:
                rec["points"][i] = float(ov)
    series = []
    for dom, rec in by_domain.items():
        scored = [p for p in rec["points"] if p is not None]
        if len(scored) < 2:
            continue
        latest = next((p for p in reversed(rec["points"]) if p is not None), None)
        series.append({"domain": dom, "segment": rec["segment"],
                       "points": rec["points"], "_latest": latest})
    series.sort(key=lambda x: (-(x["_latest"] or 0.0), x["domain"]))
    return series, dates


def _population_band_series(sweeps: list) -> list:
    """From an ordered (oldest-first) list of sweeps sharing ONE rubric version, reduce
    each sweep's WHOLE scored cohort to a spread summary — the population context the
    two-anchor trend sits inside.

    For each sweep, aggregates over the rows that ACTUALLY SCORED (``scored`` true and
    ``overall`` not None): a NOT-SCORABLE member contributes to neither ``n`` nor the
    band (attribution honesty, invariant #4 — an unreachable member is an observation
    gap, never a 0 that would drag the median or widen the spread). Returns a list
    ALIGNED to ``sweeps`` (same length/order); each entry is ``None`` when that sweep
    scored nobody, else ``{"n", "median", "lo", "hi", "q1", "q3"}`` where ``lo``/``hi``
    are the cohort min/max (the whole-cohort spread envelope) and ``q1``/``q3`` the
    inclusive quartiles (the robust central half, tooltip detail). Pure/deterministic:
    reads committed ``overall`` values, moves no score."""
    import statistics

    out: list = []
    for s in sweeps:
        rows = s.get("rows", []) if isinstance(s, dict) else []
        vals = sorted(
            float(r["overall"]) for r in rows
            if r.get("scored") and r.get("overall") is not None
        )
        if not vals:
            out.append(None)
            continue
        if len(vals) >= 2:
            q1, _, q3 = statistics.quantiles(vals, n=4, method="inclusive")
        else:
            q1 = q3 = vals[0]
        out.append({
            "n": len(vals),
            "median": statistics.median(vals),
            "lo": vals[0],
            "hi": vals[-1],
            "q1": q1,
            "q3": q3,
        })
    return out


def _anchor_trend_svg(series: list, dates: list, bands: list | None = None) -> str:
    """A multi-series overall-vs-cadence trend for the canonical anchors (y is the
    0-100 overall scale, fixed so the gap between anchors reads honestly rather than
    an auto-zoomed wiggle). One recessive connecting line + a dot per SCORED reading
    per series; a not-scorable reading breaks the line (no dot). The latest scored
    point of each series is direct-labeled; the gap between the top and bottom anchor
    at the newest all-scored sweep is bracketed and labeled (the population-scale view
    of the frozen reference delta). Colors identify series but the HTML legend names
    them, so identity never rests on color alone.

    When ``bands`` (from :func:`_population_band_series`, aligned to ``dates``) is
    given, a recessive whole-cohort overlay is drawn BEHIND the anchor lines: a shaded
    min-max envelope + a dashed median line, so the anchor gap reads against where the
    WHOLE scored population sits, not just the two reference storefronts. A sweep with
    no band (nobody scored) breaks the envelope — never interpolated across a gap.
    ``bands=None`` reproduces the anchor-only chart byte-for-byte (backward compat)."""
    n = len(dates)
    if not series or n < 2:
        return ""
    W, H = 780.0, 250.0
    padL, padR, padT, padB = 46.0, 92.0, 20.0, 40.0
    lo, hi = 0.0, 100.0

    def x_of(i: int) -> float:
        return padL + (W - padR - padL) * i / (n - 1)

    def y_of(v: float) -> float:
        return (H - padB) - (v - lo) / (hi - lo) * (H - padB - padT)

    # Horizontal gridlines + y labels at 0/25/50/75/100.
    axis = "".join(
        f'<line x1="{padL:.1f}" y1="{y_of(t):.1f}" x2="{W - padR:.1f}" '
        f'y2="{y_of(t):.1f}" stroke="#eef0f3" stroke-width="1"/>'
        f'<text x="{padL - 6:.1f}" y="{y_of(t) + 3.5:.1f}" text-anchor="end" '
        f'font-family="DM Mono,monospace" font-size="10" fill="#667085">{t:.0f}</text>'
        for t in (0.0, 25.0, 50.0, 75.0, 100.0)
    )
    # X-axis: a dated tick per sweep.
    xaxis = "".join(
        f'<text x="{x_of(i):.1f}" y="{H - padB + 16:.1f}" text-anchor="middle" '
        f'font-family="DM Mono,monospace" font-size="10" fill="#667085">{_esc(d)}</text>'
        for i, d in enumerate(dates)
    )

    # Whole-cohort overlay (behind the anchor lines): a shaded min-max spread envelope
    # + a dashed median line, so the two-anchor gap reads against where the WHOLE
    # scored population sits. Drawn over contiguous runs of banded sweeps so a
    # nobody-scored sweep is a gap, never interpolated (mirrors the anchor-line gaps).
    band_svg = ""
    if bands and len(bands) == n:
        run: list = []
        runs: list = []
        for i, b in enumerate(bands):
            if b is None:
                if len(run) >= 2:
                    runs.append(run)
                run = []
            else:
                run.append((i, b))
        if len(run) >= 2:
            runs.append(run)
        parts: list = []
        for r in runs:
            top = " ".join(f"{x_of(i):.1f},{y_of(b['hi']):.1f}" for i, b in r)
            bot = " ".join(f"{x_of(i):.1f},{y_of(b['lo']):.1f}" for i, b in reversed(r))
            parts.append(
                f'<polygon points="{top} {bot}" fill="#98a2b3" fill-opacity="0.13" '
                f'stroke="none"/>'
            )
            med = " ".join(f"{x_of(i):.1f},{y_of(b['median']):.1f}" for i, b in r)
            parts.append(
                f'<polyline points="{med}" fill="none" stroke="#667085" '
                f'stroke-width="1.5" stroke-dasharray="5 3" stroke-linejoin="round"/>'
            )
        # A dot + tooltip at every banded sweep (including lone points a run skips);
        # a lone banded sweep also gets a thin min-max whisker so its spread still reads.
        banded_idx = {i for r in runs for i, _ in r}
        for i, b in enumerate(bands):
            if b is None:
                continue
            if i not in banded_idx:
                parts.append(
                    f'<line x1="{x_of(i):.1f}" y1="{y_of(b["lo"]):.1f}" '
                    f'x2="{x_of(i):.1f}" y2="{y_of(b["hi"]):.1f}" stroke="#98a2b3" '
                    f'stroke-width="1.5"/>'
                )
            parts.append(
                f'<circle cx="{x_of(i):.1f}" cy="{y_of(b["median"]):.1f}" r="3" '
                f'fill="#667085" stroke="#fff" stroke-width="1.5">'
                f'<title>population median ({_esc(dates[i])}): {b["median"]:.1f} '
                f'&mdash; {b["n"]} scored, spread {b["lo"]:.1f}&ndash;{b["hi"]:.1f} '
                f'(IQR {b["q1"]:.1f}&ndash;{b["q3"]:.1f})</title></circle>'
            )
        band_svg = "".join(parts)

    lines = []
    for si, s in enumerate(series):
        color = _ANCHOR_TREND_COLORS[si % len(_ANCHOR_TREND_COLORS)]
        pts = s["points"]
        # Break the polyline at every not-scorable gap so an unreachable sweep is a
        # gap, not an interpolated straight line across missing data.
        run: list = []
        segs: list = []
        for i, v in enumerate(pts):
            if v is None:
                if len(run) >= 2:
                    segs.append(run)
                run = []
            else:
                run.append((i, v))
        if len(run) >= 2:
            segs.append(run)
        for run in segs:
            poly = " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in run)
            lines.append(
                f'<polyline points="{poly}" fill="none" stroke="{color}" '
                f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
            )
        last_i = None
        for i, v in enumerate(pts):
            if v is None:
                continue
            last_i = i
            lines.append(
                f'<circle cx="{x_of(i):.1f}" cy="{y_of(v):.1f}" r="3.5" '
                f'fill="{color}" stroke="#fff" stroke-width="2">'
                f'<title>{_esc(s["domain"])} ({_esc(dates[i])}): overall {v:.1f}</title></circle>'
            )
        # Direct-label the latest scored reading, to the right of the plot.
        if last_i is not None:
            lv = pts[last_i]
            lines.append(
                f'<text x="{x_of(last_i) + 8:.1f}" y="{y_of(lv) + 3.5:.1f}" '
                f'text-anchor="start" font-family="DM Mono,monospace" font-size="11" '
                f'font-weight="500" fill="{color}">{lv:.1f}</text>'
            )

    # Gap bracket at the newest sweep where the top AND bottom anchors both scored —
    # the population-scale picture of the reference delta the replay guard freezes.
    gap_mark = ""
    if len(series) >= 2:
        top, bot = series[0]["points"], series[-1]["points"]
        gi = None
        for i in range(n - 1, -1, -1):
            if top[i] is not None and bot[i] is not None:
                gi = i
                break
        if gi is not None:
            gx = x_of(gi)
            ty, by = y_of(top[gi]), y_of(bot[gi])
            gap = top[gi] - bot[gi]
            gap_mark = (
                f'<line x1="{gx:.1f}" y1="{ty:.1f}" x2="{gx:.1f}" y2="{by:.1f}" '
                f'stroke="#98a2b3" stroke-width="1.5" stroke-dasharray="4 3"/>'
                f'<text x="{gx - 6:.1f}" y="{(ty + by) / 2 + 3.5:.1f}" text-anchor="end" '
                f'font-family="DM Mono,monospace" font-size="11" font-weight="600" '
                f'fill="#475467">+{gap:.1f}</text>'
            )

    names = ", ".join(s["domain"] for s in series)
    band_label = (
        " with whole-cohort median and min-max spread band" if band_svg else ""
    )
    return (
        f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" '
        f'style="max-width:{W:.0f}px;height:auto" role="img" '
        f'aria-label="Canonical anchor overall scores across {n} dated population '
        f'sweeps ({_esc(names)}){band_label}, 0 to 100 scale">'
        f'{axis}{xaxis}{band_svg}{"".join(lines)}{gap_mark}</svg>'
    )


def _reference_gap_verdict(series: list, dates: list) -> dict | None:
    """Pure verdict of whether the reference gap between the top and bottom anchor
    HELD or MOVED across the committed cadence — the single datum both the calibration
    trend card and the main-card headline badge render, extracted so the two surfaces
    can never disagree about the population-scale echo of the frozen reference delta.

    ``series``/``dates`` come from :func:`_anchor_trend_series` (already
    version-isolated + oldest-first). Returns ``None`` unless there are >=2 anchor
    series that BOTH score at >=1 common sweep (no common reading = no verdict, never
    an invented one). Otherwise a dict: ``status`` "held" (|delta| < 0.05) or "moved",
    ``first_gap``/``last_gap`` (top-minus-bottom anchor overall at the oldest/newest
    COMMON-scored sweep), ``delta`` (last-first), ``span`` (count of common-scored
    sweeps). A not-scorable reading is a gap in a line, never a 0 (attribution
    honesty): it simply is not a common-scored index, so it can never fabricate a
    moved verdict."""
    if len(series) < 2:
        return None
    top, bot = series[0]["points"], series[-1]["points"]
    commons = [i for i in range(len(dates)) if top[i] is not None and bot[i] is not None]
    if not commons:
        return None
    first_gap = top[commons[0]] - bot[commons[0]]
    last_gap = top[commons[-1]] - bot[commons[-1]]
    delta = last_gap - first_gap
    return {
        "status": "held" if abs(delta) < 0.05 else "moved",
        "first_gap": first_gap,
        "last_gap": last_gap,
        "delta": delta,
        "span": len(commons),
    }


def _reference_gap_badge_from_sweeps(sweeps: list) -> str:
    """A one-line population-cadence verdict badge for the MAIN card hero: does the
    reference gap the per-cycle regression check freezes HOLD across the WHOLE
    committed population cadence, not just the single pair on this card?

    Mirrors the calibration trend card's version isolation (invariant #2 — only sweeps
    on the newest sweep's rubric version are compared) and reads the SAME
    :func:`_reference_gap_verdict`, so the headline badge can never drift from the
    calibration page it links to. Returns "" when there is no multi-sweep same-version
    trend yet (no badge rather than a premature verdict). Display-only; reads committed
    ``overall`` values, moves no score."""
    dated = [s for s in sweeps if isinstance(s, dict) and s.get("rows")]
    dated.sort(key=lambda s: str(s.get("ts", "")))
    if len(dated) < 2:
        return ""
    ref_version = str(dated[-1].get("rubric_version", ""))
    same = [s for s in dated if str(s.get("rubric_version", "")) == ref_version]
    if len(same) < 2:
        return ""
    series, dates = _anchor_trend_series(same)
    verdict = _reference_gap_verdict(series, dates)
    if verdict is None:
        return ""
    span = verdict["span"]
    if verdict["status"] == "held":
        bg, bd, fg = "#ecfdf3", "#abefc6", "#067647"
        body = (
            f'<b>Population check:</b> the reference gap held at '
            f'<b>+{verdict["last_gap"]:.1f}</b> across {span} same-version sweeps'
        )
    else:
        bg, bd, fg = "#fffaeb", "#fedf89", "#b54708"
        body = (
            f'<b>Population check:</b> the reference gap moved '
            f'+{verdict["first_gap"]:.1f}&rarr;+{verdict["last_gap"]:.1f} '
            f'(&Delta;&nbsp;{verdict["delta"]:+.1f}) across {span} same-version sweeps'
        )
    return (
        f'<div style="margin-top:14px;padding:8px 12px;border:1px solid {bd};'
        f'background:{bg};color:{fg};border-radius:8px;font-size:13px">'
        f'{body} &middot; <a href="calibration.html" style="color:{fg};font-weight:600">'
        f'reference-pair trend &rarr;</a></div>'
    )


def _calibration_anchor_trend_card(sweeps: list, live_version: str) -> str:
    """Render the reference-pair TREND card for calibration.html — the population
    analog of canonical-history.html's per-cycle delta trend.

    The single-cadence drift card (``_calibration_drift_card``) shows this-sweep vs
    the immediately prior one. This card zooms out to the WHOLE committed cadence: the
    two canonical anchors' overall on every dated sweep, so a reader sees the
    reference gap (the +39.4 the replay guard freezes) HOLD — or move — across the
    population runs, not just the latest step. Scores compare only within a rubric
    version (invariant #2), so only sweeps sharing the NEWEST sweep's rubric version
    are plotted; older-version sweeps are counted and named, never mixed onto the same
    axis. Display-only: reads committed ``overall`` values, moves no score. Returns ""
    unless at least 2 same-version sweeps carry an anchor with 2+ scored points (a
    single sweep, or a single reading, is not a trend)."""
    dated = [s for s in sweeps if isinstance(s, dict) and s.get("rows")]
    dated.sort(key=lambda s: str(s.get("ts", "")))
    if len(dated) < 2:
        return ""
    ref_version = str(dated[-1].get("rubric_version", ""))
    same = [s for s in dated if str(s.get("rubric_version", "")) == ref_version]
    excluded = len(dated) - len(same)
    if len(same) < 2:
        return ""
    series, dates = _anchor_trend_series(same)
    bands = _population_band_series(same)
    svg = _anchor_trend_svg(series, dates, bands)
    if not svg:
        return ""

    # Legend: a named swatch per series (never color-alone).
    legend = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px">'
        f'<span style="width:12px;height:12px;border-radius:3px;background:'
        f'{_ANCHOR_TREND_COLORS[si % len(_ANCHOR_TREND_COLORS)]};display:inline-block">'
        f'</span><b>{_esc(s["domain"])}</b>'
        f'<span class="q" style="margin:0">{_esc(s["segment"])}</span></span>'
        for si, s in enumerate(series)
    )
    # Two more swatches for the whole-cohort overlay (median line + spread band),
    # only when the band actually rendered, so identity never rests on color alone.
    if any(b is not None for b in bands):
        legend += (
            '<span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px">'
            '<span style="width:12px;height:0;border-top:1.5px dashed #667085;'
            'display:inline-block"></span><b>population median</b></span>'
            '<span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px">'
            '<span style="width:12px;height:12px;border-radius:3px;background:#98a2b3;'
            'opacity:0.4;display:inline-block"></span>'
            '<b>whole-cohort spread</b><span class="q" style="margin:0">min&ndash;max of scored members</span></span>'
        )

    # Gap-held summary, straight from the data: the anchor delta at the first vs the
    # last sweep where both anchors scored. Shared with the main-card badge via
    # _reference_gap_verdict so the two surfaces can never disagree.
    gap_note = ""
    verdict = _reference_gap_verdict(series, dates)
    if verdict is not None:
        first_gap, last_gap, span = verdict["first_gap"], verdict["last_gap"], verdict["span"]
        if verdict["status"] == "held":
            gap_note = (
                f'<p><b>The reference gap held.</b> The capability delta between the '
                f'two anchors is <b>+{last_gap:.1f}</b> at the newest sweep and was '
                f'<b>+{first_gap:.1f}</b> at the oldest of {span} same-version sweeps '
                f'&mdash; the population-scale echo of the frozen reference delta the '
                f'replay guard defends, unmoved across the cadence.</p>'
            )
        else:
            gap_note = (
                f'<p><b>The reference gap moved.</b> The delta between the two anchors '
                f'went from <b>+{first_gap:.1f}</b> to <b>+{last_gap:.1f}</b> '
                f'(&Delta;&nbsp;{verdict["delta"]:+.1f}) across {span} same-version sweeps &mdash; a '
                f'move in the reference gap the LOG must explain in capability terms.</p>'
            )

    # Whole-cohort note: where the WHOLE scored population sits behind the two anchors,
    # and whether its median moved across the cadence — straight from the band data.
    band_note = ""
    banded = [(i, b) for i, b in enumerate(bands) if b is not None]
    if len(banded) >= 2:
        (_, first_b), (_, last_b) = banded[0], banded[-1]
        med_move = last_b["median"] - first_b["median"]
        moved = (
            f'rose from <b>{first_b["median"]:.1f}</b> to <b>{last_b["median"]:.1f}</b> '
            f'(&Delta;&nbsp;{med_move:+.1f})' if abs(med_move) >= 0.05
            else f'held at <b>{last_b["median"]:.1f}</b>'
        )
        band_note = (
            f'<p><b>The whole cohort, not just the pair.</b> The shaded band is the '
            f'min&ndash;max spread of every <b>scored</b> member (a not-scorable member '
            f'is an observation gap, never a 0 dragging the band); the dashed line is the '
            f'population <b>median</b>, which {moved} across {len(banded)} same-version '
            f'sweeps as the cohort grew to <b>{last_b["n"]}</b> scored members. The '
            f'with-rails anchor sits at the top of that spread (<b>{last_b["hi"]:.1f}</b>, '
            f'the cohort max) while the no-rails anchor sits near the median &mdash; the '
            f'reference gap is a real capability spread across the population, not an '
            f'artifact of the two chosen storefronts.</p>'
        )

    version_note = ""
    if excluded:
        version_note = (
            f'<p style="margin-top:12px;font-size:13px;color:#667085">'
            f'{excluded} committed sweep{"s" if excluded != 1 else ""} on a different '
            f'rubric version {"are" if excluded != 1 else "is"} omitted from this trend '
            f'&mdash; scores compare only within a rubric version.</p>'
        )

    return f"""<div class="card">
<h2>Reference-pair trend <span style="color:#667085;font-weight:500">&middot; {len(same)} dated sweeps &middot; rubric v{_esc(ref_version)}</span></h2>
<p>Zooming out from the single-cadence drift above: the two canonical <b>anchors</b>
&mdash; the with-rails and no-rails reference storefronts the whole population is
calibrated around &mdash; scored on <b>every</b> committed dated sweep. The gap between
them is the reference delta the per-cycle regression check freezes; this shows whether
it holds across the population cadence. Overall is the 0&ndash;100 scale; a not-scorable
reading breaks the line (never a zero &mdash; attribution honesty).</p>
<div style="overflow-x:auto">{svg}</div>
<p style="margin-top:8px">{legend}</p>
{gap_note}
{band_note}
{version_note}</div>"""


def _write_calibration_page(out_dir: Path, sweep=None, sweeps=None) -> str:
    """Render calibration.html — the population leaderboard behind the reference pair.

    A benchmark needs a POPULATION, not one pair. The local runner commits a dated
    static $0 sweep of real domains scored through the SAME probe path as every
    card; this page renders the newest committed dataset as a ranked leaderboard so
    a reader sees where real storefronts land on the scale, not just the two anchors.

    Attribution honesty (invariant #4) is the load-bearing design choice: only
    SCORED members are ranked. A member the crawl could not reach is NOT SCORABLE —
    a reachability fact about the observation, never a site FAILURE — and is named
    in a SEPARATE section, never mixed into the ranking or given a rank number.

    Grade bands come LIVE from ``load_rubric`` so the on-page legend can never drift
    from the scoring; the sweep's own recorded ``rubric_version`` is surfaced and, if
    it differs from the current rubric, the page says so (scores compare only within
    a version). Domains appear here purely as DATA — the page is literally ABOUT this
    population, the same engineering-report category as the canonical-history page;
    this is deliberately out of scope for the vendor-neutral-wording scanner, which
    guards capability-worded CHECK prose, not pages that report on named domains.
    Display-only: moves no score, rubric untouched.
    """
    from .scoring import load_rubric

    if sweep is None:
        sweep = _load_calibration_sweep()
        # Production path: the multi-sweep TREND reads the whole committed cadence.
        # When a caller passes an explicit `sweep` (unit tests) it may pass `sweeps`
        # too to exercise the trend; otherwise the trend is simply absent.
        if sweeps is None:
            sweeps = _load_all_calibration_sweeps()
    rubric = load_rubric()
    live_version = str(rubric.get("version", ""))
    bands = rubric.get("grade_bands", [])
    band_legend = " &middot; ".join(
        f"{_esc(g)}&nbsp;&ge;&nbsp;{_esc(lb)}" for lb, g in bands
    )

    head = _PROSE_HEAD.format(title="ASRS — calibration leaderboard (population sweep)")
    nav = (
        '<div class="nav"><a href="javascript:history.back()">&larr; Back to the '
        'scorecard</a><a href="methodology.html">Methodology</a>'
        '<a href="rubric.html">Rubric &amp; checks</a></div>'
    )

    rows = sweep.get("rows", []) if isinstance(sweep, dict) else []
    if not isinstance(sweep, dict) or not rows:
        body = f"""{nav}<h1>Calibration leaderboard</h1>
<p class="sub">A benchmark needs a population, not one pair</p>
<div class="card"><h2>No population sweep yet</h2>
<p>No committed <span class="chip">calibration_sweep_*.json</span> dataset was
found, so there is no population to rank. The local runner commits a dated static
$0 sweep; this page renders the newest one.</p></div>
<p class="sub" style="margin-top:16px">
<a href="methodology.html">How the score is measured &rarr;</a></p>
</div></body></html>"""
        path = out_dir / "calibration.html"
        path.write_text(head + body)
        return str(path)

    sweep_version = str(sweep.get("rubric_version", ""))
    ts = str(sweep.get("ts", ""))
    ts_disp = f"{ts[:8]} {ts[9:15]}" if len(ts) >= 15 else ts
    scored = [r for r in rows if r.get("scored") and r.get("overall") is not None]
    not_scorable = [r for r in rows if not (r.get("scored") and r.get("overall") is not None)]
    # Re-derive the ranking from the rows themselves (highest overall first) rather
    # than trusting a pre-computed order — the page's ranking is a property of the
    # scores, reproducible from the raw data. A plain stable sort on overall alone
    # would leave EQUAL-overall members in their input row order, so two datasets
    # that differ only in row order would render different rankings for a tie; the
    # secondary domain-ASC key makes rank a PURE function of the data (overall DESC,
    # then domain), so the leaderboard is invariant under any permutation of `rows`.
    scored.sort(key=lambda r: (-r["overall"], str(r.get("domain", ""))))

    version_note = ""
    if sweep_version and sweep_version != live_version:
        version_note = (
            f'<p><b>Version note.</b> This dataset was scored on rubric '
            f'v{_esc(sweep_version)}; the current rubric is v{_esc(live_version)}. '
            f'Scores are comparable only within a rubric version &mdash; treat the '
            f'ranking as a v{_esc(sweep_version)} population.</p>'
        )

    intro = f"""<h1>Calibration leaderboard</h1>
<p class="sub">Where real storefronts land &middot; static $0 population sweep &middot;
rubric v{_esc(sweep_version or live_version)}{f" &middot; {_esc(ts_disp)} UTC" if ts_disp else ""}</p>
<div class="card">
<h2>What this is</h2>
<p>A benchmark needs a <b>population</b>, not one reference pair. This is a static,
<b>$0</b> sweep of {len(rows)} real domains scored through the <b>same probe path</b>
as every scorecard &mdash; no behavioral panel, so the <b>outcome</b> pillar is not
measured here (shown as &ldquo;&mdash;&rdquo;, never a scored 0). Domains span the
spectrum from agent-native storefronts through emerging-rails retail to no-rails
retail and non-storefront controls; the <b>segment</b> column is read-only context,
not an input to any score &mdash; every domain gets the <b>identical</b> vendor-neutral
probes.</p>
<p><b>Only reachable domains are ranked.</b> A member the crawl could not observe is
<b>not scorable</b> &mdash; a fact about the observation, never a site failure
(attribution honesty) &mdash; and is listed separately below, never mixed into the
ranking.</p>
{version_note}</div>"""

    def _num(v) -> str:
        return "&mdash;" if v is None else f"{float(v):.1f}"

    def _pill_cell(v) -> str:
        if v is None:
            return '<td class="num" style="color:#98a2b3">&mdash;</td>'
        cls = _band(v)
        color = {"good": "#067647", "warn": "#b54708", "bad": "#b42318"}.get(cls, "#475467")
        return f'<td class="num" style="color:{color}">{float(v):.0f}</td>'

    pillar_head = "".join(
        f'<th class="num" title="{_esc(PILLAR_QUESTIONS.get(p, ""))}">'
        f'{_esc(PILLAR_LABELS.get(p, p))}</th>'
        for p in _SWEEP_PILLARS
    )
    lb_rows = ""
    for i, r in enumerate(scored, 1):
        pillars = r.get("pillars") or {}
        pill_cells = "".join(_pill_cell(pillars.get(p)) for p in _SWEEP_PILLARS)
        archs = r.get("claimed_archetypes") or []
        arch_html = (
            "".join(f'<span class="chip">{_esc(a)}</span> ' for a in archs)
            if archs
            else '<span style="color:#98a2b3">none claimed</span>'
        )
        lb_rows += (
            f'<tr><td class="num">{i}</td>'
            f'<td><b>{_esc(r.get("domain", ""))}</b>'
            f'<div class="q">{_esc(r.get("segment", ""))}</div></td>'
            f'<td>{_grade_pill(r.get("grade", "N/A"))}</td>'
            f'<td class="num"><b>{_num(r.get("overall"))}</b></td>'
            f'{pill_cells}'
            f'<td style="line-height:22px">{arch_html}</td></tr>'
        )

    table = f"""<div class="card">
<h2>Leaderboard <span style="color:#667085;font-weight:500">&middot; {len(scored)} scored</span></h2>
<div style="overflow-x:auto">
<table><tr><th class="num">#</th><th>Domain &amp; segment</th><th>Grade</th>
<th class="num">Overall</th>{pillar_head}<th>Claims to sell</th></tr>
{lb_rows}</table></div>
<p style="margin-top:12px;font-size:13px">Grade bands (live from rubric
v{_esc(live_version)}): {band_legend}. Pillar cells are 0&ndash;100; a green cell is
&ge;80, amber &ge;60, red below. &ldquo;Claims to sell&rdquo; is the offering
classifier&rsquo;s vendor-neutral archetype set &mdash; diagnostic context, off the
scoring path.</p>
</div>"""

    if not_scorable:
        ns_rows = "".join(
            f'<tr><td><b>{_esc(r.get("domain", ""))}</b>'
            f'<div class="q">{_esc(r.get("segment", ""))}</div></td>'
            f'<td>{_esc(r.get("error") or "unreachable by the agent crawl")}</td></tr>'
            for r in not_scorable
        )
        ns_card = f"""<div class="card">
<h2>Not scorable <span style="color:#667085;font-weight:500">&middot; {len(not_scorable)}</span></h2>
<p>These members could not be observed by the agent crawl (an agent-UA block, a
timeout, or an environment error). That is a <b>reachability</b> fact, not a site
<b>failure</b> &mdash; they earn no grade and are <b>excluded from the ranking</b>
rather than scored as a zero. Whether a store blocks agent user-agents is itself a
readiness signal, but it is not the same as a low score.</p>
<table><tr><th>Domain &amp; segment</th><th>Why not scored</th></tr>{ns_rows}</table>
</div>"""
    else:
        ns_card = ""

    trend_card = _calibration_anchor_trend_card(sweeps or [], live_version)
    drift_card = _calibration_drift_card(sweep.get("drift"))

    body = f"""{nav}{intro}{table}{ns_card}{trend_card}{drift_card}
<p class="sub" style="margin-top:16px">
Scores are comparable only within a rubric version.
&middot; <a href="methodology.html">How the score is measured &rarr;</a>
&middot; <a href="canonical-history.html">Live canonical-delta trend &rarr;</a></p>
</div></body></html>"""
    path = out_dir / "calibration.html"
    path.write_text(head + body)
    return str(path)


def _band(score: float | None) -> str:
    if score is None:
        return "na"
    return "good" if score >= 80 else ("warn" if score >= 60 else "bad")


def _grade_pill(grade: str) -> str:
    if grade in ("A+", "A", "B"):
        cls = "good"
    elif grade == "C":
        cls = "warn"
    elif grade in ("N/A", "", None):
        # Not scorable — neutral, not a red "bad" grade.
        cls = "neutral"
    else:
        cls = "bad"
    return f'<span class="pill {cls}"><span class="dot"></span>Grade {_esc(grade or "N/A")}</span>'


def _score_box(rep: dict, label: str | None) -> str:
    label_html = f'<div class="label">{_esc(label)}</div>' if label else ""
    ov = rep.get("overall_score")
    # None (scored is False) -> the domain had no observable pillar; show "n/a"
    # rather than a punitive 0. Attribution honesty.
    value_html = f"{ov:.0f}" if ov is not None else "n/a"
    return (
        f'<div class="scorebox">{label_html}'
        f'<div class="domain">{_esc(rep["domain"])}</div>'
        f'<div class="score-lockup"><span class="value num">{value_html}</span>'
        f'<span class="of">/ 100</span></div>'
        f"<div>{_grade_pill(rep['grade'])}</div></div>"
    )


def _hero(reports: list[dict], labels: list[str | None], badge: str = "") -> str:
    if len(reports) == 1:
        return f'<div class="card"><div class="hero single">{_score_box(reports[0], labels[0])}</div>{badge}</div>'
    a, b = reports
    oa, ob = a.get("overall_score"), b.get("overall_score")
    # A delta is only meaningful between two scored domains; if either side had
    # no observable pillar, show a neutral "n/a" rather than an invented number.
    if oa is not None and ob is not None:
        d = ob - oa
        delta_pill = (
            f'<span class="pill {"good" if d > 0 else "bad" if d < 0 else "neutral"}">'
            f'<span class="dot"></span><span class="num">{d:+.1f}</span></span>'
        )
    else:
        delta_pill = (
            '<span class="pill neutral"><span class="dot"></span>'
            '<span class="num">n/a</span></span>'
        )
    # Per-pillar deltas render inline in the right domain column (baseline
    # deltas next to the bars), so the hero carries only the overall delta.
    return (
        '<div class="card"><div class="hero">'
        + _score_box(a, labels[0] or "Without")
        + f'<div class="delta-arrow"><span>&#8594;</span>{delta_pill}</div>'
        + _score_box(b, labels[1] or "With")
        + "</div>" + badge + "</div>"
    )


def _caps_alerts(rep: dict) -> str:
    out = []
    for slug in rep.get("caps_applied", []):
        why = CAP_EXPLANATIONS.get(slug, "")
        # Link the cap chip to its row in the methodology page so a reader who
        # sees a capped grade can jump straight to why that finding caps.
        chip = (
            f'<a class="chip" href="methodology.html#{_cap_anchor(slug)}">'
            f"{_esc(slug)}</a>"
        )
        out.append(
            f'<div class="alert"><span class="icon">!</span><div>'
            f"<b>Grade capped</b> by {chip} — {_esc(why)}"
            "</div></div>"
        )
    return "".join(out)


def _pillar_top_earner(rep: dict, pillar: str) -> tuple[str, float] | None:
    """The single check that contributes the MOST raw points to ``pillar`` — the
    dominant capability behind that pillar's score. Returns ``(finding, points)``
    or ``None`` when no check in the pillar earns any credit.

    This makes a pillar score attributable in the readout: the number is not a
    diffuse aggregate but is *earned by* a named, capability-worded check (the
    Cycle-191 calibration insight, surfaced for the reader). Vendor-neutral —
    it reads whichever check happens to earn the most, never a fixed one — and
    display-only (it reads the same ``checks``/``points`` the score is built
    from and cannot move a score). Deterministic: on tied points, ``max``
    keeps the first earner in rubric-check order (the rubric's own priority)."""
    earners = [
        c
        for c in rep.get("checks", [])
        if c.get("pillar") == pillar and (c.get("points") or 0) > 0
    ]
    if not earners:
        return None
    top = max(earners, key=lambda c: c.get("points") or 0)
    return (top.get("finding") or top.get("check_id") or "", float(top.get("points") or 0))


# The static agent-native-payment PREDICTION check and the behavioral payment
# EXPERIENCE checkpoint — the SAME operationalization the calibration guard
# (tests/test_calibration.py) pins: ``x402_probe`` PASS <=> the score claims a
# machine-payable rail is reachable; ``machine_payable_path`` True across valid
# trials <=> the shopper actually reached one. Named here (not vendor-worded) so
# the card's corroboration badge and the calibration guard read the SAME signal.
_PAYMENT_PREDICTION_CHECK = "x402_probe"
_PAYMENT_EXPERIENCE_CHECKPOINT = "machine_payable_path"


def payment_corroboration_state(predicted_payable: bool, reached: list[bool]) -> str:
    """The 3-state payment-corroboration DECISION, shared by every readout so
    the HTML card's badge and the terminal card's line can never disagree —
    they are the SAME signal, presented differently. Pure: takes the static
    PREDICTION (did the score claim agent-native payment?) and the per-valid-
    trial EXPERIENCE (did the shopper reach a machine-payable path?), returns
    one of ``"good"`` / ``"neutral"`` / ``"warn"``. Callers own presentation.

    Callers pass a NON-EMPTY ``reached`` (a valid behavioral run exists);
    ``all([])``/``any([])`` would otherwise read "good"/"neutral" vacuously.
    """
    if predicted_payable and all(reached):
        return "good"  # prediction lived out in every valid trial
    if not predicted_payable and not any(reached):
        return "neutral"  # predicted floor confirmed (honest absence)
    return "warn"  # prediction and lived experience disagree / trials split


def _payment_corroboration(rep: dict) -> tuple[str, str, str] | None:
    """Does the shopper's LIVED payment experience corroborate the static
    transactability PREDICTION? Returns ``(css_class, label, title)`` for the
    transactability-pillar badge, or ``None`` when there is nothing to
    corroborate against.

    Display-only calibration affordance (the Cycle-68 static-vs-behavioral
    validity property, surfaced on the CARD): it reads the SAME data the score
    and the calibration guard already carry — the static ``x402_probe`` status
    (the PREDICTION) and the ``machine_payable_path`` checkpoint across VALID
    behavioral trials (the EXPERIENCE) — and cannot move a score.

    Three honest states, never over-claiming:
    - **good** — the score predicts agent-native payment AND every valid trial
      reached a machine-payable path (prediction lived out);
    - **neutral** — the score predicts NO agent-native payment AND every valid
      trial hit the payment wall (the honest ABSENCE: predicted floor confirmed,
      no positive corroboration to show);
    - **warn** — the prediction and the lived experience disagree, or the trials
      split — the number is not (yet) behaviorally corroborated.

    ``None`` when no valid behavioral run exists (a static-only report has no
    lived experience to corroborate against) or the prediction check is absent
    (an older/partial report) — no invented corroboration, mirroring the
    reliability/quotability cards' suppression."""
    valid = [r for r in (rep.get("behavioral_runs") or []) if r.get("checkpoints")]
    if not valid:
        return None
    prediction = None
    for c in rep.get("checks", []):
        if c.get("check_id") == _PAYMENT_PREDICTION_CHECK:
            prediction = c.get("status")
            break
    if prediction is None:
        return None
    predicted_payable = prediction == "pass"
    reached = [bool(r["checkpoints"].get(_PAYMENT_EXPERIENCE_CHECKPOINT)) for r in valid]
    state = payment_corroboration_state(predicted_payable, reached)
    return {
        "good": (
            "good",
            "behaviorally corroborated",
            "The score predicts agent-native payment; the shopper reached a "
            "machine-payable path in every valid trial.",
        ),
        "neutral": (
            "neutral",
            "no payment, as predicted",
            "The score predicts no agent-native payment; the shopper hit the "
            "payment wall in every valid trial (prediction confirmed).",
        ),
        "warn": (
            "warn",
            "not corroborated",
            "The static payment prediction and the shopper's lived experience "
            "disagree across trials.",
        ),
    }[state]


def _pillars(rep: dict, baseline: dict | None = None) -> str:
    """Pillar bar rows. With ``baseline``, each row also shows the per-pillar
    delta vs the baseline report (the compare card's right column). The
    transactability row carries a display-only behavioral-corroboration badge
    when a panel has run (see :func:`_payment_corroboration`)."""
    corrob = _payment_corroboration(rep)
    # Compare mode: the transactability row carries the DELTA — the with/without
    # pitch headline. Surface the BASELINE side's corroboration next to this
    # side's own, so the delta is read self-contained (mirrors the terminal
    # render_compare per-side annotation, Cycle 264): a +delta over an
    # UN-corroborated baseline anchor should be read with that caution, without
    # hunting to the other card. None (and thus a no-op) on single/static cards.
    base_corrob = _payment_corroboration(baseline) if baseline is not None else None
    rows = []
    for p, label in PILLAR_LABELS.items():
        s = rep["pillar_scores"].get(p)
        # Bars stay band-colored (score quality); the pillar TITLE carries the
        # category hue, matching the recommendation tags.
        fill_cls = _band(s)
        width = 0 if s is None else max(2, round(s))
        val = '<span class="val na">n/a</span>' if s is None else f'<span class="val num">{s:.0f}</span>'
        delta = ""
        row_cls = "pillar-row"
        if baseline is not None:
            row_cls = "pillar-row wd"
            sb = baseline["pillar_scores"].get(p)
            if s is None or sb is None:
                delta = '<span class="d flat num"></span>'
            else:
                d = s - sb
                dcls = "up" if d > 0 else ("down" if d < 0 else "flat")
                delta = f'<span class="d {dcls} num">{d:+.0f}</span>'
        # "Earned by" caption — name the dominant capability behind the score so
        # the number is attributable, not diffuse. Omitted when the pillar is
        # n/a or nothing earns credit (a genuinely unearned score names nothing).
        earner = ""
        if s is not None:
            top = _pillar_top_earner(rep, p)
            if top is not None:
                finding, pts = top
                earner = (
                    f'<small class="earner">earned by <b>{_esc(finding)}</b> '
                    f"<span class=\"num\">+{pts:g}</span></small>"
                )
        # Behavioral-corroboration badge — only on the transactability row, only
        # when a panel has run (None otherwise, so static cards are unchanged).
        badge = ""
        if p == "transactability":
            if corrob is not None:
                b_cls, b_label, b_title = corrob
                badge = (
                    f'<small class="corrob {b_cls}" title="{_esc(b_title)}">'
                    f"{_esc(b_label)}</small>"
                )
            if base_corrob is not None:
                bb_cls, bb_label, bb_title = base_corrob
                badge += (
                    f'<small class="corrob baseline {bb_cls}" '
                    f'title="Baseline — {_esc(bb_title)}">'
                    f"baseline: {_esc(bb_label)}</small>"
                )
        rows.append(
            f'<div class="{row_cls}"><span class="name"><span class="ptag {_esc(p)}">{label}</span>'
            f"<small>{PILLAR_QUESTIONS[p]}</small>{earner}{badge}</span>"
            f'<div class="track"><div class="fill {fill_cls}" style="width:{width}%"></div></div>{val}{delta}</div>'
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
        pillar = PILLAR_LABELS.get(c["pillar"], c["pillar"])
        return (
            f'<tr><td class="impact num{minor}">&minus;{lost:g} pts</td>'
            f'<td class="pillar-tag"><span class="ptag {_esc(c["pillar"])}">{_esc(pillar)}</span></td>'
            f'<td><span class="chip">{_esc(c["finding"])}</span></td>'
            f"<td>{_esc(c['remediation'])}</td></tr>"
        )

    head = "<tr><th>Impact</th><th>Pillar</th><th>Finding</th><th>Recommendation</th></tr>"
    top = "".join(row(c) for c in items[:fold_after])
    rest = items[fold_after:]
    fold = ""
    if rest:
        fold = (
            f"<details><summary>{len(rest)} more lower-impact recommendation"
            f'{"s" if len(rest) > 1 else ""}</summary><table class="recs">'
            + "".join(row(c) for c in rest)
            + "</table></details>"
        )
    return f'<table class="recs">{head}{top}</table>{fold}'


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


_RELIABILITY_BANDS = {
    "stable": ("good", "Stable"),
    "mixed": ("warn", "Mixed"),
    "unstable": ("bad", "Unstable"),
    "single-trial": ("neutral", "Single trial"),
    "no-signal": ("neutral", "No signal"),
}
_CHECKPOINT_LABEL_BY_KEY = dict(CHECKPOINT_LABELS)


# Quotability tag -> (pill css class, pill label). "Citable" vs "Provisional" is
# the one bit a reader needs; the tag names WHY. not-scorable is not in the map —
# it renders no card at all (the grade already says N/A; a second "no number to
# quote" pill would be noise, mirroring the terminal's suppression).
_QUOTABILITY_BANDS = {
    "static-deterministic": ("good", "Citable"),
    "reproducible": ("good", "Citable"),
    "provisional-single-trial": ("warn", "Provisional"),
    "behavioral-unobserved": ("warn", "Provisional"),
    "provisional-unstable": ("bad", "Provisional"),
    "provisional-trust-unstable": ("bad", "Provisional"),
}


def _quotability(rep: dict) -> str:
    """Is-this-number-citable card: the one-bit verdict, placed by the headline.

    Reads the ADDITIVE ``quotability`` dict the Report now carries (the
    :class:`asrs.reliability.Quotability`). Diagnostic only — never part of the
    score; it tells a leaderboard reader whether the number above is reproducible
    enough to cite or still provisional. A not-scorable report (or one with the
    field absent, e.g. an older JSON) renders no card — the grade already carries
    that, exactly like the terminal card's suppression.
    """
    q = rep.get("quotability")
    if not q:
        return ""
    tag = q.get("tag", "")
    band = _QUOTABILITY_BANDS.get(tag)
    if band is None:  # not-scorable or an unknown tag -> no card
        return ""
    band_cls, band_label = band
    pill = f'<span class="pill {band_cls}"><span class="dot"></span>{band_label}</span>'
    reason = _esc(q.get("reason", ""))
    return (
        '<div class="card"><div class="card-header"><div><h2>Quotability</h2>'
        '<div class="desc">Is the headline number safe to cite?</div>'
        f"</div>{pill}</div>"
        f'<div class="card-body"><div class="desc">{reason}</div></div></div>'
    )


def _reliability(rep: dict) -> str:
    """Within-panel reproducibility card: did the runs agree on the same task?

    Reads the ADDITIVE ``panel_reliability`` dict the Report now carries (the
    :class:`asrs.reliability.PanelReliability`). Absent (static-only report) ->
    no card. Diagnostic only — never part of the score; it tells a reader whether
    a quoted number rests on runs that reproduce or runs that flip between trials.
    """
    rel = rep.get("panel_reliability")
    if not rel:
        return ""

    band_cls, band_label = _RELIABILITY_BANDS.get(rel.get("label", ""), ("neutral", "—"))

    if rel.get("single_trial"):
        n = rel.get("valid_runs", 0)
        if n == 0:
            body = (
                '<div class="desc">No run observed the site, so reproducibility '
                "could not be assessed.</div>"
            )
        else:
            body = (
                '<div class="desc">Only one run observed the site — reproducibility '
                "is not assessed from a single draw. Re-run with more trials to quote "
                "a stability number.</div>"
            )
        pill = f'<span class="pill {band_cls}"><span class="dot"></span>{band_label}</span>'
        return (
            '<div class="card"><div class="card-header"><div><h2>Panel reliability</h2>'
            '<div class="desc">Do the shopper runs reproduce on the same task?</div>'
            f"</div>{pill}</div>"
            f'<div class="card-body">{body}</div></div>'
        )

    stability = rel.get("verdict_stability")
    stability_str = "n/a" if stability is None else f"{stability:.2f}"
    n = rel.get("valid_runs", 0)
    pill = (
        f'<span class="pill {band_cls}"><span class="dot"></span>{band_label}'
        f'&nbsp;·&nbsp;<span class="num">{stability_str}</span></span>'
    )

    flipped = rel.get("flipped_checkpoints") or []
    if flipped:
        chips = "".join(
            f'<span class="chip">{_esc(_CHECKPOINT_LABEL_BY_KEY.get(k, k))}</span>'
            for k in flipped
        )
        flipped_html = (
            '<div style="display:flex;flex-direction:column;gap:6px">'
            '<div class="desc">Flipped between runs (a checkpoint that passed in one '
            "run and failed in another):</div>"
            f'<div style="display:flex;flex-wrap:wrap;gap:6px">{chips}</div></div>'
        )
    else:
        flipped_html = '<div class="desc">Every checkpoint was unanimous across the runs.</div>'

    trust_html = ""
    if rel.get("trust_events_unanimous") is False:
        agree = rel.get("trust_event_agreement")
        agree_str = "" if agree is None else f" (agreement {agree:.2f})"
        trust_html = (
            f'<div class="desc">Trust signal flipped{agree_str} — some runs raised a '
            "trust concern during the session, others did not.</div>"
        )

    body = (
        '<div style="display:flex;flex-direction:column;gap:12px">'
        f'<div class="desc">Verdict stability <b class="num">{stability_str}</b> over '
        f"{n} valid runs &mdash; 1.0 means every run agreed on every checkpoint.</div>"
        f"{flipped_html}{trust_html}</div>"
    )
    return (
        '<div class="card"><div class="card-header"><div><h2>Panel reliability</h2>'
        '<div class="desc">Do the shopper runs reproduce on the same task?</div>'
        f"</div>{pill}</div>"
        f'<div class="card-body">{body}</div></div>'
    )


# Cross-task spread band -> (pill css class, pill label). Lower spread is BETTER
# (the site behaves the same whatever the agent was sent to do), so a small
# spread is the "good" band. Thresholds mirror the terminal `report._battery_lines`
# exactly so the two readouts never disagree on the verdict.
_BATTERY_SPREAD_BANDS = [
    (0.15, "good", "Consistent"),
    (0.35, "warn", "Somewhat intent-dependent"),
    (float("inf"), "bad", "Intent-dependent"),
]


def _battery_spread_band(spread: float) -> tuple[str, str]:
    for thresh, cls, label in _BATTERY_SPREAD_BANDS:
        if spread < thresh:
            return cls, label
    return "bad", "Intent-dependent"


# Between-archetype (storefront-TYPE) spread band -> (pill css class, label).
# Decomposes the battery-wide cross-task spread into within-type noise vs
# between-type SPECIALIZATION. Lower = a generalist (readiness is uniform across
# storefront types); higher = type-specialized (an overall number hides which
# types work). Thresholds/wording mirror the terminal `report._battery_lines`
# between-archetype line exactly so the two readouts never disagree.
_BATTERY_BETWEEN_BANDS = [
    (0.15, "good", "Generalist"),
    (0.35, "warn", "Somewhat type-dependent"),
    (float("inf"), "bad", "Type-specialized"),
]


def _battery_between_band(spread: float) -> tuple[str, str]:
    for thresh, cls, label in _BATTERY_BETWEEN_BANDS:
        if spread < thresh:
            return cls, label
    return "bad", "Type-specialized"


def _battery(rep: dict) -> str:
    """Cross-intent coverage + reliability card from a task battery.

    Reads the ADDITIVE ``battery_summary`` dict the Report carries (the
    :class:`asrs.battery.BatterySummary`). Absent (single-task / static report)
    -> no card. Diagnostic only — never part of the score; it tells a reader
    whether a site's readiness holds across intents or whether the headline
    (one task) overstates it. Mirrors the terminal ``report._battery_lines`` so
    the HTML and terminal readouts never diverge on interpretation.
    """
    summary = rep.get("battery_summary")
    if not summary:
        return ""
    n = summary.get("n_tasks", 0)
    signal = summary.get("tasks_with_signal", 0)

    spread = summary.get("cross_task_spread")
    if isinstance(spread, (int, float)):
        band_cls, band_label = _battery_spread_band(spread)
        pill = (
            f'<span class="pill {band_cls}"><span class="dot"></span>{band_label}'
            f'&nbsp;·&nbsp;<span class="num">{spread:.2f}</span></span>'
        )
        if spread < 0.15:
            interp = "behaves consistently whatever the agent was sent to do."
        elif spread < 0.35:
            interp = "is somewhat intent-dependent — some intents fare better than others."
        else:
            interp = (
                "is strongly intent-dependent — the single-task headline "
                "overstates readiness."
            )
        foot = (
            f'<div class="desc">Cross-task spread <b class="num">{spread:.2f}</b> '
            f"&mdash; 0 means identical across every intent. This site {interp}</div>"
        )
    else:
        pill = '<span class="pill neutral"><span class="dot"></span>n/a</span>'
        foot = (
            '<div class="desc">Fewer than one intent was observed, so cross-task '
            "spread could not be assessed.</div>"
        )

    # Between-archetype spread pill (Cycle 20, READOUT): the storefront-TYPE
    # specialization signal that already ships terminal + JSON (Cycle 18). Only a
    # number when >=2 archetypes had signal (between-type variance is unobservable
    # from a single type observed), so the pill renders only when it's non-None.
    bks = summary.get("between_kind_spread")
    if isinstance(bks, (int, float)):
        bcls, blabel = _battery_between_band(bks)
        between_pill = (
            f'<span class="pill {bcls}"><span class="dot"></span>{blabel}'
            f'&nbsp;·&nbsp;<span class="num">{bks:.2f}</span></span>'
        )
    else:
        between_pill = ""

    # Per-intent coverage grid: one row per battery task, a bar for how far
    # agents got. No-signal intents show "no signal" (never a site failure).
    rows = []
    for tr in summary.get("per_task", []) or []:
        tid = _esc(tr.get("task_id", "?"))
        kind = _esc(tr.get("kind", "") or "unspecified")
        mc = tr.get("mean_completion")
        if tr.get("valid_runs", 0) > 0 and isinstance(mc, (int, float)):
            pct = round(mc * 100)
            bar = (
                f'<div class="track"><div class="fill {_band(pct)}" '
                f'style="width:{max(2, pct)}%"></div></div>'
            )
            comp = f'<span class="num">{pct}%</span>'
            valid = f'<span class="num">{tr.get("valid_runs")}</span>'
        else:
            bar = '<div class="track"><div class="fill na" style="width:0%"></div></div>'
            comp = '<span class="val na">no signal</span>'
            valid = '<span class="val na">0</span>'
        rows.append(
            f'<tr><td>{tid}</td><td><span class="chip">{kind}</span></td>'
            f"<td>{bar}</td><td style=\"text-align:right\">{comp}</td>"
            f'<td style="text-align:right">{valid}</td></tr>'
        )
    grid = (
        '<table><tr><th>Intent</th><th>Archetype</th><th>Coverage</th>'
        '<th style="text-align:right">Completion</th>'
        '<th style="text-align:right">Valid runs</th></tr>'
        + "".join(rows)
        + "</table>"
    )

    # Offering-relative comparability (operator directive brick 5, READOUT): when
    # discovery drove the battery, name WHICH archetypes the numbers are over and
    # which the site does not offer, so a reader never reads a mean across
    # mismatched task sets. Renders ONLY when an offering profile marked something
    # NA (na_archetypes populated) — a hand-authored battery with no discovery has
    # na_archetypes empty and shows neither, mirroring the terminal
    # report._battery_lines. Not-offered archetypes are excluded from every
    # mean/spread, never penalized (attribution honesty applied to tasks).
    na = summary.get("na_archetypes", []) or []
    offering_html = ""
    if na:
        assessed = summary.get("assessed_archetypes", []) or []
        assessed_chips = (
            "".join(f'<span class="chip">{_esc(a)}</span>' for a in assessed)
            if assessed
            else '<span class="val na">none</span>'
        )
        na_chips = "".join(f'<span class="chip na">{_esc(a)}</span>' for a in na)
        offering_html = (
            '<div><div class="desc" style="margin-bottom:8px;font-weight:600">'
            "Offering-relative</div>"
            '<div class="desc"><b>Assessed over</b>'
            f'<div class="chip-row">{assessed_chips}</div></div>'
            '<div class="desc" style="margin-top:8px"><b>Not offered</b> '
            "(NA &mdash; excluded from every mean and spread, never penalized)"
            f'<div class="chip-row">{na_chips}</div></div>'
            '<div class="desc" style="margin-top:8px">Readiness is measured '
            "within the archetypes this site claims to serve; a mean is never "
            "read across intents it never advertised.</div></div>"
        )

    # Per-storefront-archetype rollup — only when the battery spans >1 kind
    # (with a single kind this just restates the battery-wide number), mirroring
    # the terminal "by archetype:" sub-block.
    per_kind = summary.get("per_kind", []) or []
    per_kind_html = ""
    if len(per_kind) > 1:
        krows = []
        for kr in per_kind:
            kind = _esc(kr.get("kind", "") or "unspecified")
            mc = kr.get("mean_completion")
            ks = kr.get("cross_task_spread")
            if kr.get("tasks_with_signal", 0) > 0 and isinstance(mc, (int, float)):
                comp = f'<span class="num">{round(mc * 100)}%</span>'
                spread_txt = (
                    f'<span class="num">{ks:.2f}</span>'
                    if isinstance(ks, (int, float))
                    else '<span class="val na">n/a</span>'
                )
            else:
                comp = '<span class="val na">no signal</span>'
                spread_txt = '<span class="val na">n/a</span>'
            intents = f'{kr.get("tasks_with_signal", 0)}/{kr.get("n_tasks", 0)}'
            krows.append(
                f'<tr><td><span class="chip">{kind}</span></td>'
                f'<td style="text-align:right">{comp}</td>'
                f'<td style="text-align:right">{spread_txt}</td>'
                f'<td style="text-align:right"><span class="num">{_esc(intents)}</span></td></tr>'
            )
        # Between-archetype interpretation, adjacent to the by-archetype table it
        # summarizes. Only when >=2 archetypes had signal (bks non-None) — mirrors
        # the terminal "between-archetype spread X.XX — <verdict>" line.
        if isinstance(bks, (int, float)):
            if bks < 0.15:
                binterp = "uniform across storefront types — a generalist."
            elif bks < 0.35:
                binterp = "somewhat type-dependent."
            else:
                binterp = (
                    "type-specialized — an overall number hides which storefront "
                    "types work."
                )
            between_desc = (
                f'<div class="desc">Between-archetype spread '
                f'<b class="num">{bks:.2f}</b> &mdash; how much of the variance is '
                f"storefront-<i>type</i> specialization vs within-type noise. "
                f"This site is {binterp}</div>"
            )
        else:
            between_desc = ""
        per_kind_html = (
            '<div><div class="desc" style="margin-bottom:8px;font-weight:600">'
            "By archetype</div>"
            '<table><tr><th>Archetype</th>'
            '<th style="text-align:right">Completion</th>'
            '<th style="text-align:right">Within-kind spread</th>'
            '<th style="text-align:right">Intents</th></tr>'
            + "".join(krows)
            + "</table>"
            + between_desc
            + "</div>"
        )

    return (
        '<div class="card"><div class="card-header"><div><h2>Task battery</h2>'
        f'<div class="desc">Does readiness hold across intents? '
        f'{signal}/{n} intent{"s" if n != 1 else ""} observed.</div>'
        f"</div>{pill}{between_pill}</div>"
        '<div class="card-body" style="display:flex;flex-direction:column;gap:16px">'
        + grid
        + offering_html
        + per_kind_html
        + foot
        + "</div></div>"
    )


def _overview_card(rep: dict, label: str | None, baseline: dict | None = None) -> str:
    title = f'{_esc(rep["domain"])}'
    sub = f'{_esc(label)} · scored {rep["generated_at"][:10]}' if label else f'scored {rep["generated_at"][:10]}'
    return (
        f'<div class="card"><div class="card-header"><div><h2>{title}</h2>'
        f'<div class="desc">{sub}</div></div>{_grade_pill(rep["grade"])}</div>'
        '<div class="card-body" style="display:flex;flex-direction:column;gap:16px">'
        + _caps_alerts(rep)
        + _pillars(rep, baseline=baseline)
        + "</div></div>"
    )


def _recs_card(rep: dict, titled: bool = False) -> str:
    title = f'Recommendations — {_esc(rep["domain"])}' if titled else "Recommendations"
    return (
        f'<div class="card"><div class="card-header"><div><h2>{title}</h2>'
        '<div class="desc">Sorted by score impact — each finding names its fix.</div></div></div>'
        + _recommendations(rep)
        + "</div>"
    )


def _domain_column(rep: dict, label: str | None, baseline: dict | None = None) -> str:
    return (
        '<div class="stack">'
        + _overview_card(rep, label, baseline)
        + _quotability(rep)
        + _recs_card(rep)
        + _trust_panel(rep)
        + _checkpoints(rep)
        + _reliability(rep)
        + _battery(rep)
        + "</div>"
    )


def _section_rows(a: dict, b: dict, labels: list[str | None]) -> str:
    """Compare layout: one grid row per SECTION so panels sit side by side
    even when one is taller than the other (top-aligned per row).
    Recommendations go full-width (one card per domain, stacked) — their
    tables need the room; half-width forces heavy wrapping."""
    sections = [
        (_overview_card(a, labels[0]), _overview_card(b, labels[1], baseline=a)),
        (_quotability(a), _quotability(b)),
        (_recs_card(a, titled=True), _recs_card(b, titled=True)),
        (_trust_panel(a), _trust_panel(b)),
        (_checkpoints(a), _checkpoints(b)),
        (_reliability(a), _reliability(b)),
        (_battery(a), _battery(b)),
    ]
    rows = []
    for left, right in sections:
        if not left and not right:
            continue
        rows.append(f'<div class="grid2">{left or "<div></div>"}{right or "<div></div>"}</div>')
    return "".join(rows)


def build_scorecard(
    report_paths: list[str],
    labels: list[str | None] | None = None,
    out_path: str | None = None,
    _sweeps: list | None = None,
) -> str:
    reports = [json.loads(Path(p).read_text()) for p in report_paths]
    labels = (labels or [None] * len(reports))[: len(reports)]
    while len(labels) < len(reports):
        labels.append(None)

    if len(reports) == 2:
        columns = _section_rows(reports[0], reports[1], labels)
        title = f'{reports[0]["domain"]} vs {reports[1]["domain"]}'
    else:
        columns = _domain_column(reports[0], labels[0])
        title = reports[0]["domain"]

    rv = reports[0]["rubric_version"]
    gen = reports[0]["generated_at"][:16].replace("T", " ")
    models = sorted({v["model"] for r in reports for v in (r.get("trust_panel") or [])})
    panel_note = f' Behavioral panel: {", ".join(models)}.' if models else ""
    # Headline population-cadence verdict: does the reference gap hold across the whole
    # committed sweep cadence, not just this pair? Auto-loads committed sweeps in
    # production; tests pass ``_sweeps`` explicitly for hermeticity. "" until a
    # multi-sweep same-version trend exists.
    gap_badge = _reference_gap_badge_from_sweeps(
        _load_all_calibration_sweeps() if _sweeps is None else _sweeps
    )
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
{_hero(reports, labels, gap_badge)}
{columns}
<footer>ASRS rubric v{_esc(rv)} — scores are comparable only within a rubric
version. Grade caps apply for critical failures regardless of points.
Pillar scores exclude checks that could not be tested.{_esc(panel_note)}
&nbsp;<a href="methodology.html">How the score is measured &rarr;</a>
&nbsp;&middot;&nbsp;<a href="rubric.html">The full rubric &amp; every check &rarr;</a>
&nbsp;&middot;&nbsp;<a href="canonical-history.html">Live canonical-delta trend &rarr;</a>
&nbsp;&middot;&nbsp;<a href="calibration.html">Population leaderboard &rarr;</a>
&nbsp;&middot;&nbsp;<a href="https://github.com/jnakagawa/agentic-readiness">Run this yourself &rarr;</a></footer>
</div></body></html>"""

    if out_path is None:
        out_path = str(Path("runs") / f"scorecard_{'_vs_'.join(r['domain'].replace('.', '_') for r in reports)}.html")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(doc)
    # The footer links to the rubric and methodology pages — publish both next
    # to every card so the scoring logic AND its measurement semantics ship with
    # the score (locally and when hosted).
    _write_rubric_page(Path(out_path).parent)
    _write_methodology_page(Path(out_path).parent)
    _write_canonical_history_page(Path(out_path).parent)
    _write_calibration_page(Path(out_path).parent)
    return out_path
