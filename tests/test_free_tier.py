"""Smoke tests for the free-tier transaction probe (rubric v0.4).

Runnable directly with the venv python, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_free_tier.py

Covers the load-bearing behaviours with FAKE fixtures (no network):
  - a ZERO-value challenge -> we sign, and the signed x-payment recovers to the
    ephemeral signer with value 0;
  - a NONZERO challenge -> the settle path REFUSES to sign (the safety property);
  - no free tier advertised -> the check is NA;
  - allowance exhausted -> its finding + PARTIAL;
  - discovery scrapes the opt-in header + allowance count from docs, generically.

Driftflight specifics appear ONLY as fixture data (the spec permits hardcoding
vendor details in tests), captured from the live 402 on 2026-07-22.
"""

from __future__ import annotations

import base64
import json
import os
import sys

# Make the worktree's asrs importable when run as a bare script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.behavioral import free_tier as ft  # noqa: E402
from asrs.types import Status  # noqa: E402


# --- Fixtures captured live from agents.driftflight.com on 2026-07-22 ---------

# The zc-mode: free 402 body — a ZERO-VALUE identity challenge.
ZERO_CHALLENGE_BODY = json.dumps({
    "x402Version": 2,
    "error": "payment_required",
    "resource": {"url": "https://agents.driftflight.com/v1/images/generate"},
    "accepts": [{
        "scheme": "exact",
        "network": "eip155:8453",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "amount": "0",
        "payTo": "0x0000000000000000000000000000000000000000",
        "maxTimeoutSeconds": 300,
        "extra": {"name": "USD Coin", "version": "2",
                  "zeroclick": {"kind": "identity"}},
    }],
    "reason": "identity_required",
})

# The bare (paid) 402 body — a NONZERO challenge ($0.01). We must NEVER sign this.
NONZERO_CHALLENGE_BODY = json.dumps({
    "x402Version": 2,
    "error": "payment_required",
    "accepts": [{
        "scheme": "exact",
        "network": "eip155:8453",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "amount": "10000",
        "payTo": "0xb02bf44f8d442c22eab16371b105dabdf84bac72",
        "extra": {"name": "USD Coin", "version": "2",
                  "zeroclick": {"kind": "transaction"}},
    }],
})

# Discovery docs, trimmed from the live llms.txt + manifest.json.
LLMS_TXT = (
    "# Driftflight\n\n"
    "## Free allowance - try it before any payment\n"
    "This API includes 3 free images (sketch) per account. The free allowance "
    "needs no funding and no signup: an autonomous agent can provision its own "
    "identity, send the `zc-mode: free` request header, and covered calls are "
    "served free.\n\n"
    "POST https://agents.driftflight.com/v1/images/generate\n"
)
MANIFEST = {
    "name": "Driftflight",
    "plans": [{
        "slug": "pay-as-you-go",
        "prices": [
            {"serviceSlug": "images", "meterSlug": "sketch", "priceUsd": "0.010000",
             "includedUnits": 3, "unit": "image"},
            {"serviceSlug": "images", "meterSlug": "studio", "priceUsd": "0.060000",
             "includedUnits": 0},
        ],
    }],
}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


# ---------------------------------------------------------------------------
# 1. ZERO-value challenge -> we sign, payload is well-formed & recovers.
# ---------------------------------------------------------------------------
def test_zero_value_signs_and_recovers() -> None:
    print("test_zero_value_signs_and_recovers")
    ch = ft.parse_challenge(402, ZERO_CHALLENGE_BODY)
    _check(ch is not None, "zero-value challenge parses")
    _check(ch.is_zero_value, "challenge is recognized as zero-value")
    _check(ch.chain_id == 8453, "chain id parsed from eip155:8453")

    address, signer = ft.new_ephemeral_address_and_signer()
    _check(signer is not None, "ephemeral signer created (eth-account present)")
    _check(address.startswith("0x") and len(address) == 42, "ephemeral address well-formed")

    x_payment = ft._settle_zero_value(ch, address, signer)
    decoded = json.loads(base64.b64decode(x_payment))
    _check(decoded["x402Version"] == 2, "payload x402Version 2")
    # V2 envelope: scheme/network live under the echoed `accepted` requirements,
    # not flat at the top level (this is what the facilitator verifies against).
    _check(decoded["accepted"]["scheme"] == "exact", "accepted.scheme exact")
    _check(decoded["accepted"]["network"] == "eip155:8453", "accepted.network eip155:8453")
    _check(decoded["accepted"]["amount"] == "0", "accepted.amount echoed as 0")
    auth = decoded["payload"]["authorization"]
    _check(auth["value"] == "0", "signed authorization value is exactly '0'")
    _check(auth["to"] == "0x" + "0" * 40, "authorization to the zero address")
    _check(auth["from"].lower() == address.lower(), "authorization from == ephemeral addr")
    _check(decoded["payload"]["signature"].startswith("0x"), "signature present")

    # The signature must recover to the ephemeral signer over the SAME typed data.
    from eth_account import Account
    from eth_account.messages import encode_typed_data
    typed = ft._build_transfer_authorization_typed_data(ch, address)
    # Rebuild message from the payload so we verify the emitted authorization,
    # not a freshly-generated nonce/timestamp.
    typed["message"] = {
        "from": auth["from"], "to": auth["to"], "value": int(auth["value"]),
        "validAfter": int(auth["validAfter"]), "validBefore": int(auth["validBefore"]),
        "nonce": auth["nonce"],
    }
    recovered = Account.recover_message(
        encode_typed_data(full_message=typed),
        signature=decoded["payload"]["signature"],
    )
    _check(recovered.lower() == address.lower(), "signature recovers to ephemeral signer")


# ---------------------------------------------------------------------------
# 2. NONZERO challenge -> settle REFUSES (the safety property).
# ---------------------------------------------------------------------------
def test_nonzero_challenge_refuses_to_sign() -> None:
    print("test_nonzero_challenge_refuses_to_sign")
    ch = ft.parse_challenge(402, NONZERO_CHALLENGE_BODY)
    _check(ch is not None, "nonzero challenge parses")
    _check(not ch.is_zero_value, "challenge is recognized as NONZERO")

    address, signer = ft.new_ephemeral_address_and_signer()

    refused = False
    try:
        ft._settle_zero_value(ch, address, signer)
    except ft.NonZeroChallengeError:
        refused = True
    _check(refused, "_settle_zero_value RAISES on a nonzero challenge")

    # The typed-data builder must also refuse — no signable data for value != 0.
    refused2 = False
    try:
        ft._build_transfer_authorization_typed_data(ch, address)
    except ft.NonZeroChallengeError:
        refused2 = True
    _check(refused2, "_build_transfer_authorization_typed_data RAISES on nonzero")

    # And the source must contain no path that signs a nonzero value: assert the
    # guard is present in both functions (structural tripwire against edits).
    src = open(ft.__file__, encoding="utf-8").read()
    _check(src.count("is_zero_value") >= 3, "multiple is_zero_value gates in source")


# ---------------------------------------------------------------------------
# 3. Discovery scrapes header + allowance generically.
# ---------------------------------------------------------------------------
def test_discovery_from_docs() -> None:
    print("test_discovery_from_docs")
    disc = ft.discover_free_tier({"/llms.txt": LLMS_TXT}, MANIFEST)
    _check(disc.advertised, "free tier detected as advertised")
    _check(disc.opt_in_header == ("zc-mode", "free"),
           f"opt-in header discovered generically: {disc.opt_in_header}")
    _check(disc.free_units == 3, f"free unit count read from manifest: {disc.free_units}")
    _check(disc.endpoint_hint == "/v1/images/generate",
           f"POST path discovered: {disc.endpoint_hint}")

    # No docs at all -> not advertised.
    disc_none = ft.discover_free_tier({}, None)
    _check(not disc_none.advertised, "no docs => not advertised")


# ---------------------------------------------------------------------------
# 3b. Query-param opt-in convention discovery (COVERAGE, additive/score-neutral).
#     A second opt-in convention alongside the request header: storefronts that
#     document `?tier=free` rather than a header. Discovery-only — recording it
#     does NOT gate `advertised` or the live call yet (that is a live-verified
#     [LOCAL] follow-up), so it must not move any score.
# ---------------------------------------------------------------------------
QUERY_OPTIN_DOCS = (
    "# Sketchbird\n\n"
    "## Free allowance\n"
    "Every account gets a free tier of 5 included images. To use it, append the "
    "`?tier=free` query parameter to your request; no header, no signup.\n\n"
    "POST https://api.sketchbird.example/v1/render?tier=free\n"
)


def test_query_param_optin_discovery() -> None:
    print("test_query_param_optin_discovery")
    # Direct scanner unit: extracts the documented (name, value).
    _check(ft._scan_query_param_instruction(QUERY_OPTIN_DOCS) == ("tier", "free"),
           "?tier=free extracted from prose")
    # Value-hint and name-hint variants both count.
    _check(ft._scan_query_param_instruction(
        "free allowance: call with ?mode=free to opt in") == ("mode", "free"),
        "?mode=free (value hint) extracted")
    _check(ft._scan_query_param_instruction(
        "free tier: pass ?free=true on the request") == ("free", "true"),
        "?free=true (name hint) extracted")

    # Noise the scanner must NOT mistake for an opt-in:
    #   - a non-free plan value near free-tier prose (?plan=pro)
    _check(ft._scan_query_param_instruction(
        "the free tier is generous; upgrade later with ?plan=pro") is None,
        "?plan=pro near free prose is not an opt-in")
    #   - ordinary plumbing params (?page, ?api_key) even worded with 'free'
    _check(ft._scan_query_param_instruction(
        "free tier docs, paginate with ?page=1") is None,
        "?page=1 (plumbing) skipped")
    _check(ft._scan_query_param_instruction(
        "free allowance; auth via ?api_key=free_key_123") is None,
        "?api_key= (denylisted) skipped even with 'free' in value")
    #   - a non-free param name/value sitting near free-tier prose is not grabbed
    #     (neither name nor value literally hints "free")
    _check(ft._scan_query_param_instruction(
        "the free allowance is generous; select a plan via ?tier=starter") is None,
        "?tier=starter near free prose is not an opt-in (no free hint)")

    # Surfaced through discover_free_tier, into evidence.
    disc = ft.discover_free_tier({"/llms.txt": QUERY_OPTIN_DOCS}, None)
    _check(disc.opt_in_query == ("tier", "free"),
           f"opt_in_query populated by discovery: {disc.opt_in_query}")
    _check(disc.evidence.get("opt_in_query") == ["tier", "free"],
           "opt_in_query surfaced in discovery evidence")

    # SCORE-NEUTRALITY (the load-bearing invariant of this additive change):
    # a query-param opt-in with NO header and NO manifest unit count must NOT
    # flip `advertised` — advertised stays exactly what it was before the field
    # existed (False here), so no behavioral score can move on its account.
    _check(not disc.advertised,
           "query-param opt-in alone does NOT make the tier 'advertised' (score-neutral)")
    _check(disc.opt_in_header is None, "query-only doc surfaces no header")

    # And adding a query param to the header-based doc leaves `advertised`
    # identical — the gate is byte-for-byte independent of the new field.
    base = ft.discover_free_tier({"/llms.txt": LLMS_TXT}, MANIFEST)
    plus_q = ft.discover_free_tier(
        {"/llms.txt": LLMS_TXT + "\nAlternatively append ?tier=free.\n"}, MANIFEST)
    _check(base.advertised == plus_q.advertised is True,
           "adding a documented query-param opt-in does not change `advertised`")


# ---------------------------------------------------------------------------
# 3c. Path-based opt-in convention discovery (COVERAGE, additive/score-neutral).
#     A THIRD opt-in convention alongside the header and query param: storefronts
#     that route the free tier through a dedicated URL path segment (`/free/…`,
#     `/v1/free/…`) rather than a header or query param. Discovery-only — like
#     `opt_in_query`, recording it does NOT gate `advertised` or the live call
#     yet (a live-verified [LOCAL] follow-up), so it must not move any score.
# ---------------------------------------------------------------------------
PATH_OPTIN_DOCS = (
    "# Paperwing\n\n"
    "## Free allowance\n"
    "New agents get a free tier of 5 included images with no signup. To use it, "
    "call the dedicated free endpoint:\n\n"
    "POST https://api.paperwing.example/v1/free/generate\n"
)


def test_path_optin_discovery() -> None:
    print("test_path_optin_discovery")
    # Direct scanner unit: extracts the documented free-mode path.
    _check(ft._scan_path_instruction(PATH_OPTIN_DOCS) == "/v1/free/generate",
           "/v1/free/generate extracted from prose")
    # A bare `/free/…` and `-`/`_`-joined free-mode variants all count.
    _check(ft._scan_path_instruction(
        "free allowance: POST /free/render to try it") == "/free/render",
        "/free/render extracted")
    _check(ft._scan_path_instruction(
        "the free tier lives at /api/free-tier/call") == "/api/free-tier/call",
        "/api/free-tier/call (hyphen variant) extracted")

    # Noise the scanner must NOT mistake for a free-mode opt-in path:
    #   - a substring "free" that is NOT an exact free-mode segment
    _check(ft._scan_path_instruction(
        "the free tier is generous; read /freedom/manifesto") is None,
        "/freedom (substring, not a free-mode segment) is not an opt-in path")
    #   - a retail free-shipping checkout path near free-tier prose
    _check(ft._scan_path_instruction(
        "free shipping on all orders via /cart/free-shipping/apply") is None,
        "/free-shipping (retail, not in the allowlist) is not an opt-in path")
    #   - a free-mode path with NO adjacent free-allowance prose (the path's own
    #     'free' segment is excised from the context window, so it cannot count)
    _check(ft._scan_path_instruction("GET /v1/free/generate") is None,
        "/v1/free/generate with no adjacent free-tier prose is not matched")
    #   - a plain endpoint with no free segment at all
    _check(ft._scan_path_instruction(
        "free allowance docs; call POST /v1/images/generate") is None,
        "/v1/images/generate (no free segment) is not matched")

    # Surfaced through discover_free_tier, into evidence.
    disc = ft.discover_free_tier({"/llms.txt": PATH_OPTIN_DOCS}, None)
    _check(disc.opt_in_path == "/v1/free/generate",
           f"opt_in_path populated by discovery: {disc.opt_in_path}")
    _check(disc.evidence.get("opt_in_path") == "/v1/free/generate",
           "opt_in_path surfaced in discovery evidence")

    # SCORE-NEUTRALITY (the load-bearing invariant of this additive change):
    # a path-based opt-in with NO header and NO manifest unit count must NOT flip
    # `advertised` — it stays exactly what it was before the field existed
    # (False here), so no behavioral score can move on its account.
    _check(not disc.advertised,
           "path-based opt-in alone does NOT make the tier 'advertised' (score-neutral)")
    _check(disc.opt_in_header is None, "path-only doc surfaces no header")

    # And adding a free-mode path to the header-based doc leaves `advertised`
    # identical — the gate is byte-for-byte independent of the new field.
    base = ft.discover_free_tier({"/llms.txt": LLMS_TXT}, MANIFEST)
    plus_p = ft.discover_free_tier(
        {"/llms.txt": LLMS_TXT + "\nOr call the free endpoint POST /v1/free/generate.\n"},
        MANIFEST)
    _check(base.advertised == plus_p.advertised is True,
           "adding a documented path-based opt-in does not change `advertised`")
    _check(plus_p.opt_in_path == "/v1/free/generate",
           "the added free-mode path is still discovered alongside the header")


# ---------------------------------------------------------------------------
# 4. No free tier advertised -> the check is NA.
# ---------------------------------------------------------------------------
def test_no_free_tier_is_na() -> None:
    print("test_no_free_tier_is_na")
    out = ft.ProbeOutcome(advertised=False, finding="no-free-tier-advertised")
    check = ft.build_check(out)
    _check(check.status == Status.NA, "not-advertised => Status.NA")
    _check(check.points == 0.0, "NA earns 0 points (but shrinks denominator)")
    _check(check.remediation == "", "NA carries no remediation (never a defect)")
    _check(check.check_id == "bhv_free_tier_transaction", "correct check id")
    _check(check.pillar == "outcome", "pillar is outcome")


# ---------------------------------------------------------------------------
# 5. Exhausted allowance -> its finding + PARTIAL (meter worked).
# ---------------------------------------------------------------------------
def test_exhausted_allowance_finding() -> None:
    print("test_exhausted_allowance_finding")
    # Settled zero-value identity, but the retry returned a priced 402.
    out = ft.ProbeOutcome(
        advertised=True, challenge_received=True, settled=True, delivered=False,
        finding="free-tier-exhausted",
        remediation="allowance exhausted",
    )
    check = ft.build_check(out)
    _check(check.status == Status.PARTIAL, "exhausted (settled, no content) => PARTIAL")
    _check(check.finding == "free-tier-exhausted", "carries free-tier-exhausted finding")
    # advertised(1) + challenge(1) + settled(2) = 4, no content(1).
    _check(abs(check.points - 4.0) < 1e-6, f"partial credit = 4.0, got {check.points}")


# ---------------------------------------------------------------------------
# 6. not-zero-cost -> PARTIAL with the free-tier-not-zero-cost finding.
# ---------------------------------------------------------------------------
def test_not_zero_cost_finding() -> None:
    print("test_not_zero_cost_finding")
    out = ft.ProbeOutcome(
        advertised=True, challenge_received=True, settled=False, delivered=False,
        finding="free-tier-not-zero-cost", challenge_amount="10000",
        remediation="nonzero",
    )
    check = ft.build_check(out)
    _check(check.status == Status.PARTIAL, "not-zero-cost => PARTIAL")
    _check(check.finding == "free-tier-not-zero-cost", "finding preserved")
    # advertised(1) + challenge(1) = 2; nothing settled/delivered.
    _check(abs(check.points - 2.0) < 1e-6, f"partial credit = 2.0, got {check.points}")


# ---------------------------------------------------------------------------
# 7. full delivery -> PASS, all 5 points.
# ---------------------------------------------------------------------------
def test_full_delivery_passes() -> None:
    print("test_full_delivery_passes")
    out = ft.ProbeOutcome(
        advertised=True, challenge_received=True, settled=True, delivered=True,
        finding="free-tier-delivered", content_marker="imageUrl",
        ephemeral_address="0x" + "a" * 40,
    )
    check = ft.build_check(out)
    _check(check.status == Status.PASS, "full delivery => PASS")
    _check(abs(check.points - 5.0) < 1e-6, f"full credit = 5.0, got {check.points}")
    _check(check.evidence["content_field"] == "imageUrl", "content field surfaced in evidence")


# ---- steering: underspecified body routes to the free meter via OpenAPI enums
def test_steer_body_to_free_slug():
    from asrs.behavioral.free_tier import FreeTierDiscovery, _steer_body_to_free_slug

    SPEC = {
        "paths": {
            "/v1/images/generate": {
                "post": {
                    "requestBody": {"content": {"application/json": {"schema": {
                        "properties": {
                            "prompt": {"type": "string"},
                            "model": {"type": "string", "enum": ["sketch", "studio", "gallery"]},
                        }}}}}
                }
            }
        }
    }

    class FakeResp:
        status_code = 200
        text = __import__("json").dumps(SPEC)

    class FakeSession:
        def get(self, url, timeout=None):
            return FakeResp()

    disc = FreeTierDiscovery()
    disc.free_slugs = ["images", "sketch"]
    disc.openapi_ref = "https://api.example.com/openapi.json"
    ep = "https://agents.example.com/v1/images/generate"

    steered = _steer_body_to_free_slug(FakeSession(), {"prompt": "x"}, disc, ep)
    assert steered == {"prompt": "x", "model": "sketch"}, steered
    # already steered -> unchanged
    same = _steer_body_to_free_slug(FakeSession(), {"prompt": "x", "model": "sketch"}, disc, ep)
    assert same == {"prompt": "x", "model": "sketch"}
    # no openapi ref -> unchanged
    disc2 = FreeTierDiscovery()
    disc2.free_slugs = ["sketch"]
    assert _steer_body_to_free_slug(FakeSession(), {"prompt": "x"}, disc2, ep) == {"prompt": "x"}
    print("  ok: steering to free meter via openapi enums")


def main() -> int:
    tests = [
        test_zero_value_signs_and_recovers,
        test_nonzero_challenge_refuses_to_sign,
        test_discovery_from_docs,
        test_query_param_optin_discovery,
        test_path_optin_discovery,
        test_no_free_tier_is_na,
        test_exhausted_allowance_finding,
        test_not_zero_cost_finding,
        test_full_delivery_passes,
        test_steer_body_to_free_slug,
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
