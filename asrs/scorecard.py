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
  overflow-wrap:anywhere;max-width:100%;box-sizing:border-box}
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
        f'<tr><td><span class="chip">{_esc(slug)}</span></td>'
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
regardless of trial count &mdash; see section 9.)</p>
</div>

<div class="card">
<h2><span class="n">8</span>Grade bands &amp; caps</h2>
<p>Points map to a letter grade by these bands: {band_str}. But critical
failures <b>cap</b> the grade regardless of points &mdash; averages hide
showstoppers, so a single fatal defect limits the letter (the SSL&nbsp;Labs
pattern):</p>
<table><tr><th>Cap finding</th><th class="num">Grade ceiling</th><th>Why</th></tr>{cap_rows}</table>
</div>

<div class="card">
<h2><span class="n">9</span>The $0 free-tier probe</h2>
<p>Where a site advertises a free-tier or zero-value allowance, one scored run
may make <b>exactly one real transaction &mdash; and only at $0</b>. No code path
signs a nonzero-value authorization, funds a wallet, or creates an account;
probe keys are ephemeral. This keeps the transactability evidence real (an
agent genuinely completed a machine-payable path) without ever spending money or
leaving a footprint on the merchant.</p>
</div>

<div class="card">
<h2><span class="n">10</span>Versioned comparability &amp; evidence</h2>
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
        out.append(
            f'<div class="alert"><span class="icon">!</span><div>'
            f"<b>Grade capped</b> by <span class=\"chip\">{_esc(slug)}</span> — {_esc(why)}"
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
        per_kind_html = (
            '<div><div class="desc" style="margin-bottom:8px;font-weight:600">'
            "By archetype</div>"
            '<table><tr><th>Archetype</th>'
            '<th style="text-align:right">Completion</th>'
            '<th style="text-align:right">Within-kind spread</th>'
            '<th style="text-align:right">Intents</th></tr>'
            + "".join(krows)
            + "</table></div>"
        )

    return (
        '<div class="card"><div class="card-header"><div><h2>Task battery</h2>'
        f'<div class="desc">Does readiness hold across intents? '
        f'{signal}/{n} intent{"s" if n != 1 else ""} observed.</div>'
        f"</div>{pill}</div>"
        '<div class="card-body" style="display:flex;flex-direction:column;gap:16px">'
        + grid
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
    return out_path
