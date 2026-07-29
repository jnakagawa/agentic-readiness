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
<p>Two honest limits keep this from over-claiming. Each direction is anchored on
<b>one storefront</b> &mdash; a single with-rails run and a single no-rails run
&mdash; so the property is corroborated both ways but not yet across a population.
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

    latest_card = f"""<div class="card">
<h2>Latest reading</h2>
<p style="margin-bottom:14px">{_esc(ch._short_ts(latest.ts))} &middot;
{len(hist.points)} live re-scores over
{_esc(ch._short_ts(hist.points[0].ts))} &rarr; {_esc(ch._short_ts(latest.ts))}</p>
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
        if cause is not None:
            diag_card += f'<p><b>Side:</b> {_esc(ch.cause_verdict(cause))}.</p>'
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
        rec_card = f"""<div class="card">
<h2>Re-capture decision</h2>
<p>Does the committed fixture still represent the true capability gap, or has the
reference pair moved durably enough that the pinned delta should be re-captured?
This synthesizes the band, sustained-run, pillar and side diagnostics above into one
recommendation &mdash; a decision, never an action (re-capturing the pinned baseline
is a <span class="chip">[LOCAL]</span>, comparability-affecting step).</p>
<p style="margin-top:12px"><b style="color:{rec_color}">{_esc(rec_label)}</b>
&mdash; {_esc(adv.reason)}.</p>
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


# Static-sweep pillar order for the leaderboard columns — the same five pillars,
# outcome last (a static $0 sweep never runs a live shopper panel, so outcome is
# always null here; shown as "—", never a scored 0 — attribution honesty).
_SWEEP_PILLARS = ("access", "legibility", "transactability", "trust", "outcome")


def _write_calibration_page(out_dir: Path, sweep=None) -> str:
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

    sweep = _load_calibration_sweep() if sweep is None else sweep
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

    body = f"""{nav}{intro}{table}{ns_card}
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


def _hero(reports: list[dict], labels: list[str | None]) -> str:
    if len(reports) == 1:
        return f'<div class="card"><div class="hero single">{_score_box(reports[0], labels[0])}</div></div>'
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
        + "</div></div>"
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


def _pillars(rep: dict, baseline: dict | None = None) -> str:
    """Pillar bar rows. With ``baseline``, each row also shows the per-pillar
    delta vs the baseline report (the compare card's right column)."""
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
        rows.append(
            f'<div class="{row_cls}"><span class="name"><span class="ptag {_esc(p)}">{label}</span>'
            f"<small>{PILLAR_QUESTIONS[p]}</small></span>"
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
