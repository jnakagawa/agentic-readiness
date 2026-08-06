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


# ---------------------------------------------------------------------------
# 4. Fixture-capture determinism (METHOD, Cycle 295): the serialized ``entries``
#    order must be a function of WHAT was crawled, not the ORDER it arrived in.
#    ``self._cache`` is an insertion-ordered dict, so pre-fix ``save_fixture``
#    emitted entries in probe-ARRIVAL order — deterministic today only because
#    ``probes.run`` crawls single-threaded in a fixed sequence, but a re-capture
#    under any reordering (a parallelized crawl / a reordered probe list) would
#    emit byte-DIFFERENT fixtures for IDENTICAL content, so a recapture would
#    diff dirty for no substantive reason and the committed regression artifact
#    would not be byte-reproducible. The fix sorts entries on the total, unique
#    ``(method, url, ua)`` cache key. This is the recording-side sibling of the
#    ``by_run`` evidence-order sorts (Cycles 253/255/257) and the static
#    ``caps_applied`` order finding (Cycle 291). Off the scoring path: replay
#    (``from_fixture``) rebuilds a dict keyed by the same tuple, so entry order
#    never reached any score — this only makes the RECORDED bytes reproducible.
# ---------------------------------------------------------------------------
def _ctx_with_cache(domain: str, base_url: str, items: list) -> FetchContext:
    """A live-mode context whose cache is populated in the GIVEN insertion order.

    ``items`` is a list of ``(method, url, ua, FetchResult)`` inserted in list
    order, so the caller controls the dict's insertion order — the exact axis
    ``save_fixture`` must be invariant to.
    """
    ctx = FetchContext(domain)
    ctx.base_url = base_url
    ctx._base_resolved = True
    for method, url, ua, result in items:
        ctx._cache[(method, url, ua)] = result
    return ctx


def test_save_fixture_entry_order_is_capture_order_invariant() -> None:
    print("test_save_fixture_entry_order_is_capture_order_invariant")
    base = "https://z.test"
    r = lambda u, s=200, t="x": FetchResult(  # noqa: E731 - tiny local ctor
        url=u, final_url=u, status=s, headers={}, text=t, error=None)
    # Four keys whose SORTED (method,url,ua) order differs from any insertion
    # order used below. k2 vs k3 differ ONLY by ua, so the ua field must be in
    # the sort key for the order to be total — that pair is the discriminator.
    k1 = ("GET", "https://z.test", "browser", r("https://z.test", t="home"))
    k2 = ("GET", "https://z.test/api", "browser", r("https://z.test/api", 402, "b"))
    k3 = ("GET", "https://z.test/api", "gptbot", r("https://z.test/api", 402, "g"))
    k4 = ("POST", "https://z.test/api", "browser", r("https://z.test/api", 200, "p"))
    expected_keys = [
        ["GET", "https://z.test", "browser"],
        ["GET", "https://z.test/api", "browser"],
        ["GET", "https://z.test/api", "gptbot"],
        ["POST", "https://z.test/api", "browser"],
    ]

    # Two genuinely different crawl/insertion orders of the SAME four responses.
    order_a = [k4, k3, k1, k2]
    order_b = [k2, k1, k3, k4]

    with tempfile.TemporaryDirectory() as d:
        fa, fb = os.path.join(d, "a.json"), os.path.join(d, "b.json")
        _ctx_with_cache("z.test", base, order_a).save_fixture(fa)
        _ctx_with_cache("z.test", base, order_b).save_fixture(fb)
        with open(fa, encoding="utf-8") as fh:
            pa = json.load(fh)
        with open(fb, encoding="utf-8") as fh:
            pb = json.load(fh)

        # (a) NON-VACUOUS — the two insertion orders REALLY differ, so an
        #     unsorted serializer WOULD emit different entry orders (the sort is
        #     load-bearing, not a no-op on already-ordered input).
        raw_a = [(m, u, ua) for (m, u, ua, _res) in order_a]
        raw_b = [(m, u, ua) for (m, u, ua, _res) in order_b]
        _check(raw_a != raw_b, "the two crawl orders genuinely differ (non-vacuous)")

        # (b) The serialized entries are byte-IDENTICAL across the two crawl
        #     orders — capture order does not reach the recorded fixture.
        _check(pa["entries"] == pb["entries"],
               "save_fixture entries are identical under a permuted crawl order")

        # (c) The emitted order is the CANONICAL (method,url,ua) sort (teeth: the
        #     insertion orders above are both non-sorted, so this only holds if
        #     the sort fired), and the ua-only pair k2<k3 is correctly ordered.
        got_keys = [[e["method"], e["url"], e["ua"]] for e in pa["entries"]]
        _check(got_keys == expected_keys,
               f"entries in canonical (method,url,ua) sort order, got {got_keys}")

        # (d) SCORE-NEUTRAL round-trip — replaying either fixture reconstructs the
        #     SAME response for every key (content preserved; replay is keyed by
        #     the tuple, never by entry position), so no score can move.
        rep_a = FetchContext.from_fixture(fa)
        rep_b = FetchContext.from_fixture(fb)
        for method, url, ua, res in (k1, k2, k3, k4):
            ra = rep_a._cache[(method, url, ua)]
            rb = rep_b._cache[(method, url, ua)]
            _check(ra == rb == res,
                   f"replayed {method} {url} {ua} is identical from both orders")


def main() -> int:
    tests = [
        test_round_trip_fidelity,
        test_replay_miss_is_clean,
        test_end_to_end_x402_live_vs_bare,
        test_save_fixture_entry_order_is_capture_order_invariant,
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
