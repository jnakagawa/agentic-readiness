#!/usr/bin/env python3
"""Detached, heartbeated PR #148 post-merge behavioral verification launcher.

Runs the codex-only shopper+trust panel over the canonical pair and confirms
the v0.7(d) `_ENV_BLOCK_RE` fix routes any fresh "denied by the browser
permission boundary/policy" codex refusal to reachability (attribution
honesty, invariant #4) rather than scoring it as site evidence.

WHY DETACHED. The codex-only pair panel can take up to ~24 min worst-case
(SHOPPER_TIMEOUT_S=300 x 2 trials + TRUST_TIMEOUT_S=120, x 2 domains), which
exceeds one local-cycle wall-clock. Launched INLINE it dies with the fire:
every `runs/local/pr148_postmerge_*/compare.log` before this launcher is
START-only or 0-byte (9 consecutive stalls, Cycles up to Local 175200Z). A
classic double-fork into a new session (os.setsid) reparents the worker to
init so it SURVIVES the fire; the NEXT fire harvests the COMPLETED,
heartbeated artifact (END: exit=<rc> + report.txt). See loop/PLAYBOOK.md
(Local cycle) and the PR #148 item in loop/BACKLOG.md.

$0-ONLY (invariant #1). The panels are read-only model investigations; the
free-tier probe attempts the target's own allowance AT MOST once. No signing
path, no nonzero --max-pay, no wallet touch. codex-only also halves runtime
vs claude,codex (claude is the rarely-refusing control) while still
exercising the fix's target model.

Usage: run_pr148_verify.py <rundir>   (the launching process returns at once)
"""
import datetime
import os
import pathlib
import subprocess
import sys

REPO = os.environ.get("ASRS_REPO", "/Users/jonahnakagawa/github/agentic-readiness")
# Fixed-verb command: never parameterised by anything a caller can inject.
CMD = [
    "compare", "drift-flight.org", "driftflight.com",
    "--behavioral", "--trials", "2", "--models", "codex",
]


def _ts() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(rundir: str) -> None:
    logp = pathlib.Path(rundir, "compare.log")
    with open(logp, "a") as lg:
        lg.write(f"START: {_ts()} cmd: {' '.join(CMD)}\n")
        lg.flush()
    rc = 99
    try:
        with open(pathlib.Path(rundir, "report.txt"), "w") as out, \
                open(pathlib.Path(rundir, "compare.err"), "w") as err:
            rc = subprocess.call(
                [os.path.join(REPO, ".venv/bin/python"), "-m", "asrs", *CMD],
                cwd=REPO, stdout=out, stderr=err, stdin=subprocess.DEVNULL,
            )
    finally:
        with open(logp, "a") as lg:
            lg.write(f"END: {_ts()} exit={rc}\n")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: run_pr148_verify.py <rundir>")
    rundir = sys.argv[1]
    os.makedirs(rundir, exist_ok=True)
    # Double-fork daemonisation: original parent returns to the caller at once;
    # the session leader exits; the grandchild — reparented to init, its own
    # session, no controlling tty — outlives this fire and does the work.
    if os.fork() > 0:
        os._exit(0)
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    try:
        _run(rundir)
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
