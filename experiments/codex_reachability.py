"""[LOCAL] experiment — characterize the codex hosted-browser refusal.

Answers the standing TRUTH open question (STATE.md / BACKLOG P0 "Codex
reachability investigation"): when codex's hosted browser refuses a canonical
domain, WHAT vocabulary does it use, and is that refusal a REPUTATION gate
(domain age / no independent footprint) rather than the "browser security"
vocabulary that ``shopper._ENV_BLOCK_RE`` already recognizes?

This is the [LOCAL] evidence-gathering step the cloud cannot run: it needs the
codex CLI + live network. It runs codex through the SAME path the scorer uses
(``shopper._run_one`` -> ``_codex_cmd`` -> ``run_cli`` from a scratch cwd,
network on, web_search on), so the refusal captured here is byte-for-byte the
refusal a real behavioral run would hit — attribution honesty (invariant #4)
demands the characterization come from the real code path, not a hand-rolled
one.

For each domain it ALSO records the plain HTTP homepage status (via the same
``asrs.fetch`` the static scorer uses). A domain that answers HTTP 200 while
codex refuses to browse it is the crux: the SITE is up, so the refusal is
codex's own gate, not a site-side block — exactly the case invariant #4 says
must route to reachability, never to a site FAIL.

Reputable control (example.com): old, universally-trusted, no storefront. If
codex browses it and refuses the freshly-registered canonical domains, the
refusal is a reputation gate, not a broken browser — that contrast is the
experiment's control.

$0: read-only recon only. No free-tier probe, no zero CLI, no signing path.
Does NOT modify ``_ENV_BLOCK_RE`` — that regex change is peer-gated scoring
semantics; this run only produces the committed transcript + fixture a future
peer-gated PR needs.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict
from datetime import datetime, timezone

from asrs.behavioral.shopper import _is_env_blocked, _run_one
from asrs.behavioral.trust_probe import is_codex_usable
from asrs.fetch import FetchContext

TASK = "purchase this site's primary product or service"

# (domain, trials). Canonical pair x2 for determinism; reputable control x1.
TARGETS: list[tuple[str, int]] = [
    ("driftflight.com", 2),    # the good-rails canonical .com
    ("drift-flight.org", 2),   # the poor-rails canonical .org (both freshly registered)
    ("example.com", 1),        # reputable control: browser works => gate is reputation
]

# Report-only lexicon (NOT a scoring change): markers of a REPUTATION/safety
# gate as distinct from the "browser security" family the regex already catches.
# Used purely to characterize the captured transcripts for the LOG + the
# next-cycle peer-gated regex fixture.
_REPUTATION_MARKERS = [
    r"reputation", r"flagged", r"\bunsafe\b", r"not safe", r"phishing", r"scam",
    r"malicious", r"suspicious", r"newly registered", r"recently registered",
    r"registered (?:on|in)\b", r"domain age", r"no (?:independent )?footprint",
    r"unable to browse", r"can(?:no|')t (?:help|browse|verify)", r"won't be able",
    r"not able to (?:browse|access)", r"legitimacy", r"\bsafety\b", r"\bunverified\b",
]
_REP_RE = re.compile("|".join(_REPUTATION_MARKERS), re.I)

# The narrow "browser security" family already covered by shopper._ENV_BLOCK_RE.
_SECURITY_FAMILY_RE = re.compile(r"browser security|security (?:policy|controls|grounds)", re.I)


def _blocker_sentences(run) -> list[str]:
    """The refusal/blocker text the classifier actually keys on."""
    return [s for s in (run.blockers + run.trust_events) if s.strip()]


def _classify(run) -> dict:
    text = " ".join(_blocker_sentences(run))
    rep_hits = sorted({m.group(0).lower() for m in _REP_RE.finditer(text)})
    return {
        "any_checkpoint_passed": bool(run.checkpoints and any(run.checkpoints.values())),
        "checkpoints": dict(run.checkpoints),
        "blockers": list(run.blockers),
        "trust_events": list(run.trust_events),
        # Does the CURRENT shipped regex call this env-blocked?
        "is_env_blocked_current": _is_env_blocked(run),
        # Does it use the narrow "browser security" family the regex covers?
        "matches_security_family": bool(_SECURITY_FAMILY_RE.search(text)),
        # Does it read as a reputation/safety gate (the test #8 coverage gap)?
        "reputation_markers": rep_hits,
        "transcript_path": run.transcript_path,
    }


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join("runs", "local", f"codex_reachability_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    print(f"[codex-reach] usability check...", flush=True)
    codex_ok = is_codex_usable()
    print(f"[codex-reach] codex usable: {codex_ok}", flush=True)
    if not codex_ok:
        print("[codex-reach] codex not usable — aborting (nothing to characterize).", flush=True)
        return 2

    records = []
    for domain, trials in TARGETS:
        # HTTP reachability first: proves the SITE is up when codex refuses.
        fr = FetchContext(domain).homepage()
        http = {"status": fr.status, "is_success": fr.is_success, "final_url": fr.final_url,
                "error": fr.error}
        print(f"\n[codex-reach] {domain}: HTTP {fr.status} (success={fr.is_success})", flush=True)

        for trial in range(1, trials + 1):
            print(f"[codex-reach]   codex trial {trial}/{trials} ...", flush=True)
            run = _run_one(domain, TASK, "codex", trial, out_dir, codex_ok=True)
            cls = _classify(run)
            records.append({"domain": domain, "trial": trial, "http": http,
                            "run": asdict(run), "classification": cls})
            cp = "OBSERVED" if cls["any_checkpoint_passed"] else "nothing-observed"
            print(f"[codex-reach]     -> {cp}; env_blocked_current={cls['is_env_blocked_current']}; "
                  f"security_family={cls['matches_security_family']}; "
                  f"reputation_markers={cls['reputation_markers']}", flush=True)

    # Attribution-honesty summary: which refusals are a REPUTATION gate the
    # current regex misses on an UP site (the invariant-#4 leak surface).
    leaks = [
        r for r in records
        if r["http"]["is_success"]                                  # site is up
        and not r["classification"]["any_checkpoint_passed"]        # codex saw nothing
        and not r["classification"]["is_env_blocked_current"]       # not routed to reachability
        and (r["classification"]["reputation_markers"]              # reads as reputation gate
             or not r["classification"]["matches_security_family"])
    ]

    artifact = {
        "ts": ts,
        "kind": "codex-reachability",
        "task": TASK,
        "targets": [{"domain": d, "trials": t} for d, t in TARGETS],
        "records": records,
        "leak_candidates": [
            {"domain": r["domain"], "trial": r["trial"],
             "reputation_markers": r["classification"]["reputation_markers"],
             "blockers": r["classification"]["blockers"],
             "trust_events": r["classification"]["trust_events"]}
            for r in leaks
        ],
    }
    out_path = os.path.join(out_dir, "summary.json")
    with open(out_path, "w") as fh:
        json.dump(artifact, fh, indent=1)

    print("\n[codex-reach] domain            trial  http  observed  env_blk  sec_fam  rep_markers", flush=True)
    for r in records:
        c = r["classification"]
        print(f"[codex-reach] {r['domain']:<17} {r['trial']:>4}  {str(r['http']['status']):>4}  "
              f"{'yes' if c['any_checkpoint_passed'] else 'no ':>8}  "
              f"{str(c['is_env_blocked_current']):>7}  {str(c['matches_security_family']):>7}  "
              f"{','.join(c['reputation_markers']) or '-'}", flush=True)
    print(f"\n[codex-reach] leak candidates (up-site refusals the regex misses): {len(leaks)}", flush=True)
    print(f"[codex-reach] artifact: {out_path}", flush=True)
    print(f"[codex-reach] transcripts: {out_dir}/transcripts/", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
