"""x402 call-through PROXY discovery tests (rubric v0.7 probe fix).

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_x402_proxy_discovery.py

Pins the Cycle-234 fix to ``asrs.probes.protocols._agent_surface_targets`` /
``_x402_probe``: a ZeroClick-style call-through proxy fronts the bare-POST 402
at ``agents.<domain>/<upstream-openapi-path>`` (the request an agent actually
sends to pay), not at a dedicated endpoint. The probe must (a) shed trailing
markdown/sentence punctuation off URLs pulled from prose so a referenced
``openapi.json`` survives the ``.json`` gate, and (b) join the upstream openapi
operation paths to the agent PROXY base and probe those concrete endpoints
AHEAD of doc/auth URLs (which never 402), so the proxy handshake is observed as
``x402-live`` rather than under-scored as ``x402-documented-not-probed``.

Diagnosis that motivated this: Local Cycle 232 (driftflight.com migrated from a
dedicated ``/extend`` bare-402 endpoint to the call-through proxy; the live rail
returns HTTP 402 at ``POST agents.driftflight.com/v1/images/generate`` while the
probe scored it 76.2 C / x402-documented-not-probed). Fixtures here are FAKE,
grounded in that observed proxy shape. No network.
"""

from __future__ import annotations

import os
import sys

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json  # noqa: E402

from asrs.fetch import FetchResult  # noqa: E402
from asrs.probes import protocols as P  # noqa: E402
from asrs.types import Status  # noqa: E402


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _fr(url: str, status: int | None = 200, text: str = "", headers=None) -> FetchResult:
    return FetchResult(
        url=url,
        final_url=url,
        status=status,
        headers=headers or {},
        text=text,
        error=None if status is not None else "boom",
    )


class _ProxyCtx:
    """FetchContext stand-in that serves GET/POST canned responses by URL.

    Keys on the exact ``path_or_url`` string the probe requests (absolute for
    the agent/api hosts, relative for the scored-domain base paths). Anything
    unrecorded is a 404 — the closed-world default a real crawl would see.
    """

    domain = "shop.test"
    base_url = "https://shop.test"

    def __init__(self, get_map: dict[str, FetchResult], post_map: dict[str, FetchResult]) -> None:
        self._get = get_map
        self._post = post_map
        self.fetched: list[tuple[str, str]] = []

    def get(self, url: str, ua: str = "browser") -> FetchResult:
        self.fetched.append(("GET", url))
        return self._get.get(url, _fr(url, status=404, text="not found"))

    def post_empty(self, url: str, ua: str = "browser") -> FetchResult:
        self.fetched.append(("POST", url))
        return self._post.get(url, _fr(url, status=404, text="not found"))


# --- Fixtures (fake, grounded in the observed ZeroClick proxy shape) ---------

# The upstream OpenAPI the agent surface references — its operation paths are
# the concrete endpoints the proxy fronts.
OPENAPI = json.dumps({
    "openapi": "3.0.0",
    "servers": [{"url": "https://api.shop.test"}],
    "paths": {
        "/v1/presets": {"get": {"summary": "list presets"}},
        "/v1/models": {"get": {"summary": "list models"}},
        "/v1/images/generate": {"post": {"summary": "generate an image (priced)"}},
    },
})

# An agent-surface llms.txt where every URL is wrapped in markdown backticks and
# trailed by sentence punctuation — the exact shape that broke the extractor.
# The openapi ref ends in "`." so a naive extractor fails the ".json" gate.
AGENT_LLMS = (
    "ZeroClick is a paid, transparent proxy in front of the upstream API.\n"
    "Send the same method, path, and body to `https://agents.shop.test`.\n"
    "- API reference (upstream OpenAPI): `https://api.shop.test/openapi.json`.\n"
    "- Auth details: `https://agents.shop.test/auth.md`, identity at "
    "`https://agents.shop.test/agent/identity`.\n"
    "Paying the priced 402 (x402 / MPP) proves wallet control by itself.\n"
    "- `POST /extend`: add credit to an active plan.\n"
)

# The live x402 challenge the proxy returns on a bare POST to the priced path.
X402_BODY = json.dumps({
    "x402Version": 1,
    "accepts": [{
        "scheme": "exact",
        "maxAmountRequired": "60000",
        "payTo": "0xabc0000000000000000000000000000000000000",
        "asset": "USDC",
    }],
})
X402_HEADERS = {"www-authenticate": "Payment", "content-type": "application/json"}


def _agent_pages() -> list[FetchResult]:
    return [_fr("https://agents.shop.test/llms.txt", 200, AGENT_LLMS)]


def _get_map(live_proxy_402: bool) -> dict[str, FetchResult]:
    m = {
        # the referenced openapi.json (fetched by _openapi_paths)
        "https://api.shop.test/openapi.json": _fr(
            "https://api.shop.test/openapi.json", 200, OPENAPI),
        # doc/auth pages: reachable but never a payment gate
        "https://agents.shop.test/auth.md": _fr("https://agents.shop.test/auth.md", 200, "auth"),
        "https://agents.shop.test/agent/identity": _fr(
            "https://agents.shop.test/agent/identity", 404, "no"),
        # the priced path GETs 404 (payment gates challenge on POST, not GET)
        "https://agents.shop.test/v1/images/generate": _fr(
            "https://agents.shop.test/v1/images/generate", 404, "method not allowed"),
    }
    return m


def _post_map(live_proxy_402: bool) -> dict[str, FetchResult]:
    m = {
        # /extend has MIGRATED behind agent-identity — no longer the 402 endpoint
        "https://agents.shop.test/extend": _fr("https://agents.shop.test/extend", 401, "identity"),
        "https://agents.shop.test/auth.md": _fr("https://agents.shop.test/auth.md", 404, "no"),
    }
    if live_proxy_402:
        # the bare-POST 402 now lives at the proxy-fronted upstream path
        m["https://agents.shop.test/v1/images/generate"] = _fr(
            "https://agents.shop.test/v1/images/generate", 402, X402_BODY, X402_HEADERS)
    return m


# ---------------------------------------------------------------------------
# 1. THE FIX: the probe discovers + POSTs the call-through proxy endpoint and
#    scores x402-live, even though every URL is punctuation-wrapped and the
#    dedicated /extend endpoint has migrated behind identity.
# ---------------------------------------------------------------------------
def test_proxy_endpoint_scores_x402_live() -> None:
    print("test_proxy_endpoint_scores_x402_live")
    ctx = _ProxyCtx(_get_map(True), _post_map(True))
    home = _fr("https://shop.test", 200, "<html>home</html>")
    res = P._x402_probe(ctx, home, docs=[], corpus="x402",
                        agent_bases=["https://agents.shop.test"], agent_pages=_agent_pages())
    _check(res.finding == "x402-live", f"finding is x402-live, got {res.finding!r}")
    _check(res.status == Status.PASS, f"status PASS, got {res.status}")
    _check(res.points == 8.0, f"full 8.0 points, got {res.points}")
    posted = [u for (m, u) in ctx.fetched if m == "POST"]
    _check("https://agents.shop.test/v1/images/generate" in posted,
           "the proxy-fronted upstream path was actually POSTed")
    _check(res.evidence.get("x402") is not None, "x402 payload captured in evidence")


# ---------------------------------------------------------------------------
# 2. THE CORE DISCOVERY UNIT: _agent_surface_targets builds the proxy endpoint
#    from a punctuation-wrapped openapi ref, concrete API paths BEFORE doc URLs.
# ---------------------------------------------------------------------------
def test_agent_surface_targets_builds_proxy_endpoint() -> None:
    print("test_agent_surface_targets_builds_proxy_endpoint")
    ctx = _ProxyCtx(_get_map(True), _post_map(True))
    targets = P._agent_surface_targets(ctx, ["https://agents.shop.test"], _agent_pages())
    _check("https://agents.shop.test/v1/images/generate" in targets,
           f"openapi path joined to proxy base is a target, got {targets}")
    # concrete API paths must lead so a cap never starves the endpoint that 402s
    gen = targets.index("https://agents.shop.test/v1/images/generate")
    auth = targets.index("https://agents.shop.test/auth.md") \
        if "https://agents.shop.test/auth.md" in targets else len(targets)
    _check(gen < auth, "concrete openapi endpoints are ordered ahead of doc/auth URLs")


# ---------------------------------------------------------------------------
# 3. _strip_url_junk: trailing markdown/sentence punctuation is shed; a clean
#    URL (and a legitimately path-terminal segment) is untouched.
# ---------------------------------------------------------------------------
def test_strip_url_junk() -> None:
    print("test_strip_url_junk")
    _check(P._strip_url_junk("https://api.shop.test/openapi.json`.") ==
           "https://api.shop.test/openapi.json", "sheds trailing backtick + period")
    _check(P._strip_url_junk("https://agents.shop.test/auth.md`") ==
           "https://agents.shop.test/auth.md", "sheds a trailing backtick")
    _check(P._strip_url_junk("https://api.shop.test/openapi.json,") ==
           "https://api.shop.test/openapi.json", "sheds a trailing comma")
    _check(P._strip_url_junk("https://api.shop.test/openapi.json") ==
           "https://api.shop.test/openapi.json", "a clean URL is untouched")


# ---------------------------------------------------------------------------
# 4. PRECISION NEGATIVE: a docs-only site (mentions x402, exposes no live 402)
#    still scores x402-documented-not-probed — the fix does not conjure a live
#    handshake from mere punctuation-wrapped URLs.
# ---------------------------------------------------------------------------
def test_docs_only_stays_documented_not_probed() -> None:
    print("test_docs_only_stays_documented_not_probed")
    ctx = _ProxyCtx(_get_map(False), _post_map(False))  # no endpoint returns 402
    home = _fr("https://shop.test", 200, "<html>home</html>")
    res = P._x402_probe(ctx, home, docs=[], corpus="x402",
                        agent_bases=["https://agents.shop.test"], agent_pages=_agent_pages())
    _check(res.finding == "x402-documented-not-probed",
           f"stays documented-not-probed, got {res.finding!r}")
    _check(res.status == Status.PARTIAL and res.points == 4.0,
           f"partial 4.0, got {res.status} {res.points}")
    # even so, the probe MUST have tried the proxy path (discovery worked; only
    # the live 402 was absent) — proving the negative is non-vacuous.
    posted = [u for (m, u) in ctx.fetched if m == "POST"]
    _check("https://agents.shop.test/v1/images/generate" in posted,
           "the proxy path was probed even when it did not 402 (non-vacuous)")


def main() -> int:
    tests = [
        test_proxy_endpoint_scores_x402_live,
        test_agent_surface_targets_builds_proxy_endpoint,
        test_strip_url_junk,
        test_docs_only_stays_documented_not_probed,
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
