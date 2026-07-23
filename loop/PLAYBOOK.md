# ASRS Improvement Loop — Playbook

This file is the loop's constitution. It is authoritative over the routine
prompt. One cycle = one fire of the hourly routine. Read STATE.md and
BACKLOG.md after this file, then run exactly one cycle.

Division of labor: hourly cycles run on Opus and do the improvement work;
architecture and scoring-semantics decisions land through the human-gated
PRs, reviewed by Jonah (driving Fable in-session). If a cycle finds itself
redesigning the rubric's structure rather than improving within it, that is
a PR + Slack flag, not a cycle ship.

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
5. Ship rules (three tiers — most changes must NOT wait on Jonah):
   - **Direct to main**: docs, readout, tests, backlog/log/state, probe
     bug-fixes that don't change scoring semantics.
   - **Peer gate (next-cycle review, then SELF-MERGE)**: scoring-semantics
     changes that are not human-gated below — check additions, aggregation
     refinements, rubric version bumps that accompany them. Open a PR named
     `loop/<slug>` with full evidence. The NEXT cycle's FIRST duty, before
     picking new work: adversarially review every open peer-gated PR from
     its fresh context — actively try to refute it against the invariants
     (vendor-neutrality, capability wording, attribution honesty, canonical-
     delta explanation, test coverage; run the live re-scores the authoring
     cycle couldn't if the environment allows). If it survives, MERGE it and
     record the review verdict in LOG.md; if not, request changes or close
     with reasons. Never review-and-merge your own cycle's PR in the same
     fire. A PR that Jonah has commented on is FROZEN until his comment is
     resolved. A peer-gated PR still open after 3 cycles = escalate in the
     next Slack digest.
   - **Human gate (Jonah merges)**: payment/signing code or anything
     touching the $0-only property; pillar weight changes; cap value
     changes; check REMOVALS. These are identity-level decisions.
   When in-cloud network policy blocks live re-scoring, the in-cloud
   standard is regression-by-construction plus offline tests, and the live
   canonical re-score becomes part of the merge-time review (peer cycle if
   it has network, otherwise a `[LOCAL]` reviewer).
6. Append a LOG.md entry: cycle number, track, what/why, evidence paths,
   canonical-pair numbers, next hypothesis. Update STATE.md (counter, focus
   pointer, open questions). Prune BACKLOG.md — delete stale items, add new
   observations as candidates.
7. Push. If push fails after retrying, put the entire LOG entry in the Slack
   DM and flag the failure loudly.

## Comms (keep it quiet)

Slack DM to U07PEGPSZD3 (channel D07PH9VLZEX) ONLY when:
- a human gate is needed (include the PR link and the one-paragraph case),
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
