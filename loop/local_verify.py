"""Local verification companion for the ASRS improvement loop.

The cloud loop has no outbound network to external domains, so the live parts
of its regression protocol run here, on a networked machine, on a fixed
schedule (launchd, hourly). FIXED VERBS ONLY — this script never executes
instructions from the backlog; it always does exactly:

  1. git pull (fast-forward only)
  2. run the repo's test suites
  3. live static re-score of the canonical pair
  4. write runs/local/verify_<ts>.json + append a short LOG.md entry
  5. commit + push the artifact

Cloud cycles read the newest runs/local/verify_*.json as their live
canonical-delta signal. One-off [LOCAL] experiments stay manual.
"""
from __future__ import annotations

import glob
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = REPO / ".venv" / "bin" / "python"
PAIR = ("drift-flight.org", "driftflight.com")


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)[-4000:]


def run_stdout(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    """Like run(), but returns ONLY stdout (probes log warnings to stderr)."""
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout.strip()


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out: dict = {"ts": ts, "kind": "local-verify"}

    rc, log = run(["git", "pull", "--ff-only", "origin", "main"])
    out["git_pull"] = {"ok": rc == 0, "tail": log[-300:]}
    if rc != 0:
        # Do not verify a tree we couldn't sync; report and bail.
        _write(out)
        return 1

    tests = {}
    for suite in sorted(glob.glob(str(REPO / "tests" / "test_*.py"))):
        rc, log = run([str(PY), suite])
        tests[Path(suite).name] = {"ok": rc == 0, "tail": log[-200:]}
    out["tests"] = tests
    out["tests_ok"] = all(t["ok"] for t in tests.values())

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
    rc, log = run(["git", "push", "origin", "main"])
    out["pushed"] = rc == 0
    return 0 if out["tests_ok"] else 2


def _write(out: dict) -> None:
    d = REPO / "runs" / "local"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"verify_{out['ts']}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
