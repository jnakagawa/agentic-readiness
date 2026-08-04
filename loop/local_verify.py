"""Local verification companion for the ASRS improvement loop.

The cloud loop has no outbound network to external domains, so the live parts
of its regression protocol run here, on a networked machine, on a fixed
schedule (launchd, hourly). FIXED VERBS ONLY — this script never executes
instructions from the backlog; it always does exactly:

  1. git pull (fast-forward only; self-heal a divergence of our OWN un-pushed
     heartbeats — see below)
  2. run the repo's test suites
  3. live static re-score of the canonical pair
  4. write runs/local/verify_<ts>.json + append a short LOG.md entry
  5. commit + push the artifact

Cloud cycles read the newest runs/local/verify_*.json as their live
canonical-delta signal. One-off [LOCAL] experiments stay manual.

Divergence self-heal (the 2026-08 3-day stranding incident): step 5 commits a
heartbeat THEN pushes, so if the cloud pushes between our pull and our push the
push is rejected (non-fast-forward) and we're left with a divergent commit. The
old runner then bailed on EVERY subsequent fire at the --ff-only pull, stranding
the floor for days. `recover_from_own_divergence` heals this: when the pull
fails because the branch diverged, and every commit we're ahead by is one of our
own `loop: local verification` heartbeats (un-pushed, disposable — the cloud
never saw it, and this fire writes a fresh one), we discard them and realign to
origin. Strictly guarded: any un-pushed NON-heartbeat commit is preserved and we
bail as before, so no real work is ever lost. A lost push race now costs one
skipped heartbeat, never a cascade.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# The runner is PINNED outside the repo (~/.local/bin), so the repo location
# must not be derived from __file__ — that resolved to ~/.local and sent every
# launchd fire into a silent no-op (the 2026-07-23 "floor down" incident).
REPO = Path(os.environ.get("ASRS_REPO", str(Path.home() / "github" / "agentic-readiness")))
PY = REPO / ".venv" / "bin" / "python"
PAIR = ("drift-flight.org", "driftflight.com")


def log(msg: str) -> None:
    """Heartbeat to stdout — the launchd log must never be silently empty."""
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}", flush=True)


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)[-4000:]


def run_stdout(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    """Like run(), but returns ONLY stdout (probes log warnings to stderr)."""
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout.strip()


def _pull_once() -> tuple[int, str]:
    return run(["git", "pull", "--ff-only", "origin", "main"])


def git_pull_with_retry(pull=_pull_once, attempts: int = 5, delay: int = 15,
                        sleep=time.sleep) -> tuple[int, str, int]:
    """Pull with bounded retry over transient wake/network races.

    launchd runs a missed :41 job on machine WAKE, when WiFi/DNS may not be up
    yet, so the first `git pull` fails instantly with 'Could not resolve host'
    and the runner used to bail — writing a useless git-pull-failed artifact it
    also couldn't push (the 2026-07-27/28 ~18h "runner stalled" incident: the
    launchd job fired reliably every wake, but raced the network with no retry).
    A few short waits let the network associate before giving up. Returns
    (rc, tail, attempts_made); attempts_made == 1 when the network is already up.
    """
    rc, tail = 1, ""
    for i in range(attempts):
        rc, tail = pull()
        if rc == 0:
            return rc, tail, i + 1
        log(f"git pull attempt {i + 1}/{attempts} failed: {tail[-120:].strip()}")
        if i < attempts - 1:
            sleep(delay)
    return rc, tail, attempts


# The heartbeat commit subject (see main()); un-pushed heartbeats are the ONLY
# thing the divergence self-heal is ever allowed to discard.
_HEARTBEAT_PREFIX = "loop: local verification "


def _is_diverged(tail: str) -> bool:
    """True when a --ff-only pull failed because the branch has diverged (our
    un-pushed commit vs the cloud's), NOT because of a transient network error."""
    t = tail.lower()
    return (
        "not possible to fast-forward" in t
        or "diverging branches" in t
        or "non-fast-forward" in t
    )


def _fetch_origin() -> tuple[int, str]:
    return run(["git", "fetch", "origin", "main"])


def _ahead_subjects() -> list[str]:
    """Subjects of the commits HEAD is ahead of origin/main by (our un-pushed
    commits), newest first. Empty when we are not ahead."""
    rc, out = run(["git", "log", "--format=%s", "origin/main..HEAD"])
    return [s for s in out.splitlines() if s.strip()] if rc == 0 else []


def _reset_to_origin() -> tuple[int, str]:
    return run(["git", "reset", "--hard", "origin/main"])


def recover_from_own_divergence(
    fetch=_fetch_origin, ahead=_ahead_subjects, reset=_reset_to_origin,
) -> tuple[bool, str]:
    """Heal a divergence caused ONLY by our own un-pushed heartbeat commits.

    Fetch origin, then look at what HEAD is ahead of origin/main by. Recover
    (discard those commits, realign to origin) ONLY if there is at least one
    such commit AND every one is a `loop: local verification` heartbeat — the
    cloud never saw them and this fire writes a fresh one, so they are
    disposable. Any un-pushed NON-heartbeat commit (or nothing ahead) → do not
    touch anything; return False so the caller bails and preserves the tree.
    Returns (recovered, human-readable note for the artifact/log).
    """
    fetch()
    subjects = ahead()
    if not subjects:
        return False, "divergence is not from our un-pushed commits (nothing ahead of origin)"
    if not all(s.startswith(_HEARTBEAT_PREFIX) for s in subjects):
        return False, f"preserving {len(subjects)} un-pushed non-heartbeat commit(s); not ours to discard"
    rc, tail = reset()
    if rc != 0:
        return False, f"reset --hard origin/main failed: {tail[-120:].strip()}"
    return True, f"discarded {len(subjects)} un-pushed heartbeat(s), realigned to origin/main"


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out: dict = {"ts": ts, "kind": "local-verify"}
    log(f"start — repo={REPO}")
    if not (REPO / ".git").is_dir():
        log(f"FATAL: {REPO} is not a git checkout")
        out["fatal"] = f"{REPO} is not a git checkout"
        _write(out)
        return 1

    rc, tail, tries = git_pull_with_retry()
    if rc != 0 and _is_diverged(tail):
        # A prior fire's heartbeat push lost the race with the cloud and left a
        # divergent commit. Self-heal it (guarded) instead of stranding the floor.
        recovered, note = recover_from_own_divergence()
        log(f"divergence self-heal: {note}")
        out["divergence_recovery"] = note
        if recovered:
            rc, tail, tries = git_pull_with_retry()
    out["git_pull"] = {"ok": rc == 0, "attempts": tries, "tail": tail[-300:]}
    if rc != 0:
        # Do not verify a tree we couldn't sync; report and bail.
        log(f"git pull failed after {tries} attempts: {tail[-160:]}")
        _write(out)
        return 1

    tests = {}
    for suite in sorted(glob.glob(str(REPO / "tests" / "test_*.py"))):
        rc, tail = run([str(PY), suite])
        tests[Path(suite).name] = {"ok": rc == 0, "tail": tail[-200:]}
    out["tests"] = tests
    out["tests_ok"] = all(t["ok"] for t in tests.values())
    log(f"tests_ok={out['tests_ok']} ({len(tests)} suites)")

    scores = {}
    for domain in PAIR:
        rc, stdout = run_stdout([str(PY), "-m", "asrs", "score", domain, "--json-only"])
        report_path = stdout.splitlines()[-1] if rc == 0 and stdout else ""
        entry: dict = {"ok": rc == 0}
        try:
            rep = json.loads((REPO / report_path).read_text())
            entry.update(
                overall=rep["overall_score"], grade=rep["grade"],
                rubric=rep["rubric_version"], scored=rep.get("scored", True),
                pillars={k: v for k, v in rep["pillar_scores"].items()},
            )
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
            entry["ok"] = False
        scores[domain] = entry
    out["scores"] = scores
    a, b = (scores.get(d, {}) for d in PAIR)
    if a.get("ok") and b.get("ok") and a.get("overall") is not None and b.get("overall") is not None:
        out["delta"] = round(b["overall"] - a["overall"], 1)

    _write(out)

    line = (
        f"\n## Local verification — {ts}\n\n"
        f"tests_ok={out['tests_ok']} | "
        + " | ".join(
            f"{d}: {scores[d].get('overall', 'ERR')} {scores[d].get('grade', '')}".strip()
            for d in PAIR
        )
        + (f" | delta {out['delta']:+.1f}" if "delta" in out else "")
        + f" | artifact runs/local/verify_{ts}.json\n"
    )
    with open(REPO / "loop" / "LOG.md", "a", encoding="utf-8") as fh:
        fh.write(line)

    run(["git", "add", "loop/LOG.md", f"runs/local/verify_{ts}.json", "-f"])
    run(["git", "commit", "-m", f"loop: local verification {ts}"])
    rc, tail = run(["git", "push", "origin", "main"])
    out["pushed"] = rc == 0
    # Mirror to the org repo (visibility copy; origin stays canonical because
    # the cloud loop's push access is proven there). Failure is logged, never
    # fatal — the mirror lags rather than blocking verification.
    rc_m, _ = run(["git", "push", "piedotorg", "main"])
    out["mirrored"] = rc_m == 0
    log(f"done — delta={out.get('delta', 'n/a')} pushed={out['pushed']} mirrored={out['mirrored']}")
    return 0 if out["tests_ok"] else 2


def _write(out: dict) -> None:
    d = REPO / "runs" / "local"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"verify_{out['ts']}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — a crash must still leave a trace
        log(f"CRASH: {type(exc).__name__}: {exc}")
        try:
            _write({"ts": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                    "kind": "local-verify", "crash": f"{type(exc).__name__}: {exc}"})
        except Exception:
            pass
        sys.exit(3)
