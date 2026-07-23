"""Commerce-protocol (ACP/UCP) evidence tests for x402_probe (rubric v0.7).

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_protocols.py

Pins the v0.7 credit-gate tightening in
``asrs.probes.protocols._commerce_protocol_evidence`` /
``_parse_commerce_manifest``: a well-known commerce path earns the x402_probe
partial only when it serves a VALIDATED manifest (a real UCP service/capability
manifest or an ACP checkout payload), not merely any HTTP 200. Marker tiers
(doc phrase / Shopify fingerprint) are unchanged.

Manifest shapes are FAKE fixtures grounded in the published specs (UCP:
developers.googleblog.com "Under the Hood: UCP", ucp.dev; ACP:
docs.stripe.com/agentic-commerce, developers.openai.com/commerce). No network.
"""

from __future__ import annotations

import json
import os
import sys

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.fetch import FetchResult  # noqa: E402
from asrs.probes import protocols as P  # noqa: E402


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


class _FakeCtx:
    """Minimal FetchContext stand-in: serves canned responses by path."""

    domain = "example.test"
    base_url = "https://example.test"

    def __init__(self, responses: dict[str, FetchResult]) -> None:
        self._responses = responses
        self.fetched: list[str] = []

    def get(self, path: str, ua: str = "browser") -> FetchResult:
        self.fetched.append(path)
        return self._responses.get(
            path, _fr(f"https://example.test{path}", status=404, text="not found")
        )


# --- Fixtures (fake, grounded in the published manifest shapes) --------------

UCP_MANIFEST = json.dumps({
    "version": "2026-01-11",
    "services": ["shopping"],
    "capabilities": [
        {"name": "dev.ucp.shopping.discovery", "version": "2026-01-11"},
        {"name": "dev.ucp.shopping.checkout", "version": "2026-01-11"},
    ],
    "payment": {"handlers": ["card", "x402"]},
    "endpoints": {"checkout": "/api/checkout"},
})

ACP_CHECKOUT = json.dumps({
    "id": "cs_abc123",
    "status": "ready_for_payment",
    "currency": "usd",
    "line_items": [{"id": "item_123", "quantity": 1, "amount": 500}],
    "payment_provider": {"provider": "stripe"},
    "totals": {"total": 500},
})

# A catch-all SPA index served at a well-known path — the false positive v0.7 kills.
SPA_INDEX = "<!doctype html><html><head><title>App</title></head><body>Loading…</body></html>"

# Non-empty JSON that carries no commerce structure at all.
RANDOM_JSON = json.dumps({"hello": "world", "count": 3, "items_seen": True})


# ---------------------------------------------------------------------------
# 1. A validated UCP manifest earns the live partial (4.0, relabeled).
# ---------------------------------------------------------------------------
def test_ucp_manifest_is_live_partial() -> None:
    print("test_ucp_manifest_is_live_partial")
    ctx = _FakeCtx({"/.well-known/ucp": _fr("https://example.test/.well-known/ucp",
                                            200, UCP_MANIFEST)})
    res = P._commerce_protocol_evidence(ctx, _fr("https://example.test", 200, "home"), "")
    _check(res is not None, "UCP manifest yields evidence")
    finding, pts, ev = res
    _check(finding == "commerce-protocol-live", f"finding is live, got {finding}")
    _check(pts == 4.0, f"partial points 4.0, got {pts}")
    _check(ev["manifest"]["protocol"] == "ucp", f"protocol ucp, got {ev['manifest']}")
    _check("capabilities" in ev["manifest"]["fields"] or "services" in ev["manifest"]["fields"],
           f"structural fields captured, got {ev['manifest']['fields']}")
    _check(ev["manifest"].get("version") == "2026-01-11", "manifest version carried")


# ---------------------------------------------------------------------------
# 2. A validated ACP checkout payload earns the live partial too.
# ---------------------------------------------------------------------------
def test_acp_payload_is_live_partial() -> None:
    print("test_acp_payload_is_live_partial")
    ctx = _FakeCtx({"/.well-known/agentic-commerce":
                    _fr("https://example.test/.well-known/agentic-commerce", 200, ACP_CHECKOUT)})
    res = P._commerce_protocol_evidence(ctx, _fr("https://example.test", 200, "home"), "")
    _check(res is not None, "ACP payload yields evidence")
    finding, pts, ev = res
    _check(finding == "commerce-protocol-live", f"finding is live, got {finding}")
    _check(pts == 4.0, f"partial points 4.0, got {pts}")
    _check(ev["manifest"]["protocol"] == "acp", f"protocol acp, got {ev['manifest']}")
    _check("line_items" in ev["manifest"]["fields"], "line_items captured")


# ---------------------------------------------------------------------------
# 3. THE FALSE-POSITIVE FIX: a bare-200 SPA index at a well-known path no
#    longer counts as a commerce surface (was 4.0 pre-v0.7).
# ---------------------------------------------------------------------------
def test_bare_200_index_not_credited() -> None:
    print("test_bare_200_index_not_credited")
    ctx = _FakeCtx({
        "/.well-known/ucp": _fr("https://example.test/.well-known/ucp", 200, SPA_INDEX),
        "/.well-known/agentic-commerce":
            _fr("https://example.test/.well-known/agentic-commerce", 200, SPA_INDEX),
    })
    # No phrases, not Shopify -> the whole helper must return None now.
    res = P._commerce_protocol_evidence(ctx, _fr("https://example.test", 200, "home"), "")
    _check(res is None, f"bare-200 index earns no commerce credit, got {res}")
    # And the manifest parser rejects the SPA index directly.
    _check(P._parse_commerce_manifest(_fr("u", 200, SPA_INDEX)) is None,
           "SPA index is not a manifest")


# ---------------------------------------------------------------------------
# 4. Non-commerce JSON (valid JSON, no commerce keys) is not a manifest.
# ---------------------------------------------------------------------------
def test_random_json_not_a_manifest() -> None:
    print("test_random_json_not_a_manifest")
    _check(P._parse_commerce_manifest(_fr("u", 200, RANDOM_JSON)) is None,
           "random JSON object without commerce keys -> None")
    _check(P._parse_commerce_manifest(_fr("u", 200, "[1,2,3]")) is None,
           "a JSON array is not a manifest")
    _check(P._parse_commerce_manifest(_fr("u", 200, "")) is None, "empty body -> None")
    _check(P._parse_commerce_manifest(_fr("u", 404, UCP_MANIFEST)) is None,
           "non-200 status -> None even with a manifest body")


# ---------------------------------------------------------------------------
# 5. Marker tiers are UNCHANGED: a doc-phrase mention still earns the
#    commerce-protocol-only partial (no well-known manifest present).
# ---------------------------------------------------------------------------
def test_phrase_marker_tier_unchanged() -> None:
    print("test_phrase_marker_tier_unchanged")
    ctx = _FakeCtx({})  # every well-known path -> 404
    corpus = "Our storefront supports the Agentic Commerce Protocol for AI buyers."
    res = P._commerce_protocol_evidence(ctx, _fr("https://example.test", 200, "home"), corpus)
    _check(res is not None, "phrase mention yields evidence")
    finding, pts, ev = res
    _check(finding == "commerce-protocol-only", f"marker tier preserved, got {finding}")
    _check(pts == 4.0, f"marker partial still 4.0, got {pts}")


# ---------------------------------------------------------------------------
# 6. CANONICAL REGRESSION (drift-flight.org shape): no well-known manifest,
#    no phrases, not Shopify -> None, i.e. x402_probe stays FAIL 0.0 (matches
#    the committed report). Confirms the v0.7 delta is unchanged for the pair.
# ---------------------------------------------------------------------------
def test_canonical_org_unchanged() -> None:
    print("test_canonical_org_unchanged")
    ctx = _FakeCtx({})  # nothing at any well-known path
    res = P._commerce_protocol_evidence(ctx, _fr("https://drift-flight.org", 200, "home"), "")
    _check(res is None, f"no commerce surface -> None (FAIL 0.0 upstream), got {res}")
    # Both well-known paths were still probed (behavior of the loop unchanged).
    _check("/.well-known/ucp" in ctx.fetched and "/.well-known/agentic-commerce" in ctx.fetched,
           f"both well-known paths probed, fetched={ctx.fetched}")


# ---------------------------------------------------------------------------
# 7. Reverse-domain UCP capability ids nested in a body are recognized.
# ---------------------------------------------------------------------------
def test_reverse_domain_capability_ids() -> None:
    print("test_reverse_domain_capability_ids")
    body = json.dumps({"data": {"caps": ["dev.ucp.shopping.checkout"]}})
    m = P._parse_commerce_manifest(_fr("u", 200, body))
    _check(m is not None and m["protocol"] == "ucp", f"reverse-domain cap -> ucp, got {m}")


def main() -> int:
    tests = [
        test_ucp_manifest_is_live_partial,
        test_acp_payload_is_live_partial,
        test_bare_200_index_not_credited,
        test_random_json_not_a_manifest,
        test_phrase_marker_tier_unchanged,
        test_canonical_org_unchanged,
        test_reverse_domain_capability_ids,
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
