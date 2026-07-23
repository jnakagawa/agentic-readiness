"""Record/replay fidelity tests for ``asrs.fetch.FetchContext`` (v0.7 infra).

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_fetch_replay.py

The loop's standing open question (STATE.md) is that the cloud env has no
outbound network, so the playbook's per-cycle LIVE canonical re-score cannot
run in-cloud — it needs "offline regression tests as the in-cloud proxy". This
pins the enabling mechanism: a live crawl's response cache can be serialized to
a fixture (``save_fixture``) and replayed offline (``from_fixture``) with byte-
for-byte fidelity and NO network, so a canonical-pair fixture captured [LOCAL]
once can be re-scored in-cloud every cycle as a deterministic regression signal.

No network. Fixtures are hand-authored, minimal, and grounded in the real probe
paths (homepage + an /api 402 x402 handshake vs a bare homepage).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.fetch import FetchContext, FetchResult  # noqa: E402
from asrs.probes import protocols as P  # noqa: E402


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _result(url: str, status: int | None, text: str = "", headers=None,
            error: str | None = None) -> dict:
    return {
        "url": url, "final_url": url if status is not None else "",
        "status": status, "headers": headers or {}, "text": text,
        "error": error,
    }


def _write_fixture(path: str, domain: str, base_url: str, entries: list) -> None:
    payload = {
        "fixture_version": 1, "domain": domain, "base_url": base_url,
        "entries": [
            {"method": m, "url": u, "ua": ua, "result": r} for (m, u, ua, r) in entries
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


# An x402 payment-requirements body (canonical `accepts` shape).
X402_BODY = json.dumps({
    "x402Version": 1,
    "accepts": [{"scheme": "exact", "payTo": "0xabc", "maxAmountRequired": "0"}],
})


# ---------------------------------------------------------------------------
# 1. Round-trip fidelity: save_fixture -> from_fixture reproduces every result
#    exactly, and replay serves them without touching the network.
# ---------------------------------------------------------------------------
def test_round_trip_fidelity() -> None:
    print("test_round_trip_fidelity")
    # Build a context and inject a cache the way a live crawl would have.
    live = FetchContext("rails.test")
    live.base_url = "https://rails.test"
    live._base_resolved = True
    live._cache[("GET", "https://rails.test", "browser")] = FetchResult(
        url="https://rails.test", final_url="https://rails.test", status=200,
        headers={"content-type": "text/html"}, text="<html>home</html>", error=None,
    )
    live._cache[("GET", "https://rails.test/api", "browser")] = FetchResult(
        url="https://rails.test/api", final_url="https://rails.test/api", status=402,
        headers={"content-type": "application/json"}, text=X402_BODY, error=None,
    )

    with tempfile.TemporaryDirectory() as d:
        fx = os.path.join(d, "rails.json")
        n = live.save_fixture(fx)
        _check(n == 2, f"save_fixture wrote 2 entries, got {n}")

        replay = FetchContext.from_fixture(fx)
        _check(replay._replay is True, "replay context is in replay mode")
        _check(replay.base_url == "https://rails.test", "base_url restored from fixture")

        home = replay.homepage()
        _check(home.status == 200 and home.text == "<html>home</html>",
               "replayed homepage is byte-identical")
        api = replay.get("/api")
        _check(api.status == 402 and api.text == X402_BODY,
               "replayed /api 402 body is byte-identical")
        _check(api.headers.get("content-type") == "application/json",
               "replayed headers preserved")


# ---------------------------------------------------------------------------
# 2. Replay is a closed world: an unrecorded request is a clean replay-miss
#    (status None, error set), never a crash and never a network call.
# ---------------------------------------------------------------------------
def test_replay_miss_is_clean() -> None:
    print("test_replay_miss_is_clean")
    with tempfile.TemporaryDirectory() as d:
        fx = os.path.join(d, "min.json")
        _write_fixture(fx, "bare.test", "https://bare.test", [
            ("GET", "https://bare.test", "browser", _result("https://bare.test", 200, "<html>hi</html>")),
        ])
        replay = FetchContext.from_fixture(fx)
        miss = replay.get("/nope")
        _check(miss.status is None, "replay miss has status None")
        _check(miss.error is not None and "replay-miss" in miss.error,
               f"replay miss carries a replay-miss error, got {miss.error!r}")
        _check(miss.ok is False, "replay miss is not ok")
        # A POST miss is equally clean (no network handshake escapes).
        pm = replay.post_empty("/api")
        _check(pm.status is None and "replay-miss" in (pm.error or ""),
               "replayed POST miss is clean")


# ---------------------------------------------------------------------------
# 3. END-TO-END regression proxy: replaying a recorded x402 handshake through
#    the REAL protocols pipeline yields x402-live PASS 8.0; replaying a bare
#    homepage yields no-agent-native-payment FAIL 0.0. This is the capability
#    delta (rails side earns the payment capability, bare side does not) pinned
#    as an offline, network-free guard — the shape the canonical re-score takes.
# ---------------------------------------------------------------------------
def _x402(cr) -> "tuple":
    return (cr.status.value, cr.points, cr.finding)


def test_end_to_end_x402_live_vs_bare() -> None:
    print("test_end_to_end_x402_live_vs_bare")
    with tempfile.TemporaryDirectory() as d:
        # Rails side: homepage 200 + /api returns a live x402 challenge.
        rails_fx = os.path.join(d, "rails.json")
        _write_fixture(rails_fx, "rails.test", "https://rails.test", [
            ("GET", "https://rails.test", "browser",
             _result("https://rails.test", 200, "<html><body>Pay-per-call API</body></html>")),
            ("GET", "https://rails.test/api", "browser",
             _result("https://rails.test/api", 402, X402_BODY,
                     headers={"content-type": "application/json"})),
        ])
        rails = FetchContext.from_fixture(rails_fx)
        results = {c.check_id: c for c in P.run(rails)}
        _check("x402_probe" in results, "x402_probe emitted on replay")
        st, pts, finding = _x402(results["x402_probe"])
        _check(finding == "x402-live", f"rails side -> x402-live, got {finding}")
        _check(pts == 8.0, f"rails side full transactability points, got {pts}")

        # Bare side: homepage only, no payment surface anywhere.
        bare_fx = os.path.join(d, "bare.json")
        _write_fixture(bare_fx, "bare.test", "https://bare.test", [
            ("GET", "https://bare.test", "browser",
             _result("https://bare.test", 200, "<html><body>Welcome</body></html>")),
        ])
        bare = FetchContext.from_fixture(bare_fx)
        bresults = {c.check_id: c for c in P.run(bare)}
        st, pts, finding = _x402(bresults["x402_probe"])
        _check(finding == "no-agent-native-payment",
               f"bare side -> no-agent-native-payment, got {finding}")
        _check(pts == 0.0, f"bare side zero transactability points, got {pts}")

        # The capability delta the benchmark exists to measure, pinned offline.
        _check(results["x402_probe"].points - bresults["x402_probe"].points == 8.0,
               "x402 capability delta is the full 8.0 (rails earns it, bare does not)")


def main() -> int:
    tests = [
        test_round_trip_fidelity,
        test_replay_miss_is_clean,
        test_end_to_end_x402_live_vs_bare,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL: {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
