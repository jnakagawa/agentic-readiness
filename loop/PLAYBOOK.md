# ASRS Improvement Loop — Playbook

This file is the loop's constitution. It is authoritative over the routine
prompt. One cycle = one fire of the hourly routine. Read STATE.md and
BACKLOG.md after this file, then run exactly one cycle.

Division of labor: hourly cycles run on Opus and do the improvement work;
structural redesigns of the rubric go through peer-gated PRs like any other
scoring change (with a Slack note for visibility). Jonah is informed, never
waited on — he vetoes by commenting or reverting, and silence is consent.

## North star

Make ASRS the **go-to, scientifically credible benchmark for agentic-commerce
readiness** — the number people cite when they ask "can this storefront sell
to AI agents?". As agentic commerce becomes real, the benchmark must get more
flexible (many storefront types, many task intents, many payment rails) and
more rigorous (variance-aware, evidence-linked, reproducible) at once. Every
cycle moves at least one of: methodological rigor, measurement coverage/
flexibility, readout clarity.

## The capability lens (read this twice)

The rubric measures what agent-native rails let an agent actually DO: reach
the site, understand the offer, pay programmatically, provision without a
human, complete the job. Implementations like ZeroClick-style rails score
well **because they deliver those capabilities** — that is the honest version
of "the with-rails side should win big." Protect the delta's credibility,
never manufacture it:

- Checks are worded by capability, never by vendor. No special-casing any
  domain or product, favorable or hostile.
- The canonical pair (drift-flight.org vs driftflight.com) is re-scored
  (static) every shipping cycle as a REGRESSION SIGNAL. If the delta moves
  sharply in either direction, the LOG entry must explain it in capability
  terms — or the change does not ship.
- If a rigor improvement narrows the delta because the real capability gap is
  narrower than we measured, that ships. Truth outranks the pitch; a rigged
  benchmark is worthless to the pitch anyway.

## Invariants (violating any of these = do not ship; flag instead)

1. **$0-only transactions.** No code path may sign a nonzero-value
   authorization, pay, or create accounts. One free-tier attempt per scored
   run. Ephemeral keys only. Changes to payment/signing code are human-gated.
2. **Versioned comparability.** Any change to scoring semantics (weights,
   max_points, check add/remove, cap values, aggregation rules) bumps the
   rubric version with a dated changelog entry. Scores are only comparable
   within a version.
3. **Evidence or it didn't happen.** Every scored claim traces to committed
   artifacts (reports, transcripts, tests). New probes are verified live on
   at least 2 real domains before shipping. Tests pass before every commit.
4. **Attribution honesty.** Agent-side environment failures are never scored
   as site evidence (and site failures are never excused as environment).
   When in doubt, CANT_TEST — a site is never punished for what couldn't be
   observed.
5. **No history rewrites.** Never force-push, never amend published commits,
   never edit existing LOG entries or evidence files (append only).

## Cycle protocol (ONE improvement per fire)

1. `git pull`. Read STATE.md (cycle counter, focus pointer, open questions)
   and BACKLOG.md. Skim the last 3 LOG.md entries.
2. Pick exactly ONE item — highest leverage toward the north star. Rotate
   across four tracks so none starves (pointer in STATE.md):
   - **METHOD** — measurement rigor: variance, trials, attribution, controls.
   - **COVERAGE** — new checks, rails (ACP/UCP/MPP live handshakes), task
     battery breadth, storefront types.
   - **TRUTH** — calibration against reality: real-domain sweeps, panel
     verdict stability, does the score predict what an agent experiences?
   - **READOUT** — card, rubric page, leaderboard, evidence links, prose.
3. Implement the smallest scientifically meaningful unit, with tests.
   Full suite must pass: `python tests/test_free_tier.py` plus any suite the
   repo has grown. Match existing code style and module conventions.
4. Validate: static-score the canonical pair; record overall, pillars, and
   delta in the LOG entry. If the change touches probes, also verify against
   2+ unrelated live domains.
5. Ship rules (two tiers — NOTHING waits on Jonah's approval; he holds a
   veto, not a gate):
   - **Direct to main**: docs, readout, tests, backlog/log/state, probe
     bug-fixes that don't change scoring semantics.
   - **Peer gate (next-cycle review, then SELF-MERGE)**: ALL scoring-
     semantics changes — check additions AND removals, aggregation
     refinements, pillar weight changes, cap changes, rubric version bumps,
     and payment/signing code. Open a PR named `loop/<slug>` with full
     evidence. The NEXT cycle's FIRST duty, before picking new work:
     adversarially review every open peer-gated PR from its fresh context —
     actively try to refute it against the invariants (vendor-neutrality,
     capability wording, attribution honesty, canonical-delta explanation,
     test coverage; run the live re-scores the authoring cycle couldn't if
     the environment allows). If it survives, MERGE it and record the
     review verdict in LOG.md; if not, request changes or close with
     reasons. Never review-and-merge your own cycle's PR in the same fire.
     A peer-gated PR still open after 3 cycles = escalate in the next
     Slack digest.
   Extra rigor for the sensitive classes (peer-gated, never human-blocked):
   - **Payment/signing code**: the reviewer must independently re-derive
     that no nonzero-signing path exists and that the refusal unit tests
     cover the change; post-merge, queue a `[LOCAL]` live $0 verification —
     if it ever fails, revert first, investigate second.
   - **Weights/caps/removals**: the LOG entry must argue the change in
     capability terms and show the canonical-delta effect (live when
     networked, by construction + tests when not).
   Jonah's veto: a PR or commit he comments on is FROZEN/revertable until
   resolved — but silence is consent; never wait for his approval.
   When in-cloud network policy blocks live re-scoring, the in-cloud
   standard is regression-by-construction plus offline tests, and the live
   canonical re-score becomes part of the merge-time review (peer cycle if
   it has network, otherwise queued `[LOCAL]` as post-merge monitoring —
   not a pre-merge block).

## Local cycle (the networked half of the loop — an LLM, not a cron script)

An hourly HEADLESS agent cycle runs on Jonah's machine (launchd, :41, Opus)
with what the cloud lacks: outbound network, the codex CLI, and the zero
CLI. It is governed by this same playbook — same invariants, same tracks,
same ship rules, same LOG/STATE/BACKLOG discipline. Per fire:

1. The verification artifact for this hour is already produced (the launcher
   runs `local_verify.py` first — a deterministic floor that exists even if
   this cycle fails). Do not repeat it; read it.
2. FIRST duty, same as cloud: adversarially review + merge any open
   peer-gated PR (you have the network to run its live re-scores).
3. Then execute exactly ONE `[LOCAL]` backlog item — behavioral panel runs,
   codex reachability experiments, live probe validation, anything the cloud
   designed but could not execute. Prefer the oldest P0.
4. LOG the cycle as `## Local cycle — <ts>`; update STATE/BACKLOG; push.

Local-only constraints (non-negotiable):
- **Spend nothing.** The zero CLI may be used for $0 operations only
  (free-tier probes, search/get). Never a paid capability call, never
  wallet funding, never a nonzero `--max-pay`.
- Budget: at most ONE full behavioral pair run per cycle; at most ~10 codex
  invocations per cycle.
- Touch nothing outside the repo checkout (no ~/.zero, keychains, browser
  profiles, other repos).

## Live canonical signal (local verification artifacts)

A local companion runner (`loop/local_verify.py`, launchd on Jonah's machine,
hourly at :41) executes the networked verification the cloud cannot: full
test suites + live static re-score of the canonical pair. It pushes
`runs/local/verify_<ts>.json` and a one-line LOG entry to main. Cycles MUST
read the NEWEST `runs/local/verify_*.json` as the live canonical-delta
signal instead of reporting the re-score as blocked; an artifact older than
6 hours means the local runner is down — note it in STATE and flag it in
the next Slack digest. The runner is fixed-verb (pull, test, score, push) —
never queue instructions for it; one-off `[LOCAL]` experiments remain
manual.
6. Append a LOG.md entry: cycle number, track, what/why, evidence paths,
   canonical-pair numbers, next hypothesis. Update STATE.md (counter, focus
   pointer, open questions). Prune BACKLOG.md — delete stale items, add new
   observations as candidates.
7. Push. If push fails after retrying, put the entire LOG entry in the Slack
   DM and flag the failure loudly.

## Comms (keep it quiet)

Slack DM to U07PEGPSZD3 (channel D07PH9VLZEX) ONLY when:
- a sensitive-class PR (payment/signing, weights, caps, removals) is opened
  or merged — visibility so Jonah can veto, never a request for approval,
- something shipped that changes scores or adds a capability worth knowing,
- it is the first cycle after 16:00 UTC (daily digest: cycles run, shipped
  items, canonical delta trend, top open question).
Otherwise: no DM. Never post to public channels.

## Cloud environment limits (this loop runs in Anthropic's cloud)

- **No codex CLI, no zero CLI, no local wallets** — never attempt them.
  Experiments that need them (behavioral panels, codex repro matrices, paid
  probes) are DESIGNED here and queued in BACKLOG.md tagged `[LOCAL]`, with
  exact commands, so a local operator (Jonah's machine) can execute them.
- Static probes, WebFetch/WebSearch research, python venv + pip installs,
  and the full test suite are all fair game.
- Budget: one improvement per cycle; no mass refactors; if a change balloons
  past ~10 files, cut scope and queue the rest.
