"""Free-tier transaction probe — exercise an advertised $0 allowance for real.

This is the one probe in ASRS that *transacts*. Every other check reads: it
fetches pages, elicits a 402 handshake, asks a model panel what it would do.
This one does what a real agent does when it trials a service before spending —
discover the advertised free allowance, make the documented call, receive the
HTTP 402 identity/zero-value challenge, settle it with a ZERO-VALUE signed
authorization from a *fresh ephemeral wallet*, and verify a real 200 with actual
content. It measures the Execution/Outcome rungs for real instead of read-only
recon (rubric v0.4).

The one hard safety property: **we only ever sign a ZERO-VALUE authorization.**
The challenge amount is parsed before anything is signed; if it is not exactly
zero the probe records ``free-tier-not-zero-cost`` and returns without signing.
There is deliberately no code path from a nonzero challenge to a signature
(:func:`_settle_zero_value` re-asserts ``value == 0`` and raises otherwise), and
that invariant is unit-tested (``tests/test_free_tier.py``).

Everything else is vendor-neutral and discovered, not hardcoded:
  - the free-tier opt-in header (e.g. ``zc-mode: free``) is scraped from the
    target's own agent-surface docs (``llms.txt`` / ``llms-full.txt`` /
    ``manifest.json``) via :func:`discover_free_tier`, never assumed;
  - the free allowance is read from manifest ``includedUnits`` / ``freeQuantity``
    style fields;
  - the 402 challenge shape drives the signed payload (x402 v2 ``exact`` scheme,
    EIP-3009 ``transferWithAuthorization`` typed data), read live from the target.

Emits exactly one :class:`~asrs.types.CheckResult` (``bhv_free_tier_transaction``,
pillar ``outcome``, max 5) with checkpoint partial credit:
    advertised (1) -> challenge received (1) -> settled $0 (2) -> content (1).
When NO free tier is advertised the status is NA — a site is never punished for
not offering one. At most ONE transaction attempt runs per scoring call (it
consumes the target's allowance); ``--trials`` does not multiply it.

Everything network/signing is wrapped: a failure becomes a CANT_TEST-style
finding, never an exception, matching the other probe modules.
"""

from __future__ import annotations

import base64
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from asrs.types import CheckResult, Status

PILLAR = "outcome"
CHECK_ID = "bhv_free_tier_transaction"
MAX_POINTS = 5.0

# Checkpoint partial credit (sums to MAX_POINTS). Each rung is only reachable
# once the previous one is: you cannot receive a challenge you never called for,
# settle a challenge you never received, or get content you never settled.
_PTS_ADVERTISED = 1.0  # a free tier is advertised in the target's own docs
_PTS_CHALLENGE = 1.0  # the documented free-mode call returned a 402 challenge
_PTS_SETTLED = 2.0  # a ZERO-VALUE authorization was accepted (identity proven)
_PTS_CONTENT = 1.0  # the retry returned a real 200 with actual content

# Network / HTTP budget. One call + one retry; generous for a proxied backend.
_HTTP_TIMEOUT_S = 30.0
# EIP-3009 validity window. The facilitator requires validBefore >= now + a few
# seconds; 300s mirrors the challenge's typical maxTimeoutSeconds.
_AUTH_WINDOW_S = 300

# Agent-surface discovery docs, in the order an agent reads them.
_DISCOVERY_DOCS = ("/llms.txt", "/llms-full.txt", "/manifest.json")

# Manifest keys that carry a free allowance count (vendor-neutral: any of these
# conventions signals "N free units"). Matched case-insensitively on JSON keys.
_FREE_QUANTITY_KEYS = (
    "includedunits",
    "freequantity",
    "freeunits",
    "freeallowance",
    "freetier",
    "included_units",
    "free_quantity",
)

# Opt-in header instruction, discovered from docs prose. Matches phrasings like
# "send the `zc-mode: free` request header" or "header X-Free-Mode: true". The
# header name is [A-Za-z0-9-], the value a short token; we require the word
# "free"/"header"/"allowance" nearby (enforced by the caller's windowing) so we
# do not grab arbitrary "Content-Type: application/json" mentions.
_HEADER_INSTRUCTION_RE = re.compile(
    r"[`\"']?([A-Za-z][A-Za-z0-9-]{1,40})[`\"']?\s*:\s*[`\"']?([A-Za-z0-9_.-]{1,40})[`\"']?",
)
# A header instruction only counts when it sits near free-allowance language.
_FREE_CONTEXT_RE = re.compile(r"free|allowance|included|no[\s-]?cost|trial", re.I)
# Header names that are obviously HTTP plumbing, not an opt-in signal — never
# treat these as the free-tier header even if they appear near "free".
_HEADER_NAME_DENYLIST = frozenset(
    {
        "content-type",
        "accept",
        "authorization",
        "x-payment",
        "www-authenticate",
        "payment-required",
        "user-agent",
        "host",
        "cache-control",
        "content-length",
    }
)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
@dataclass
class FreeTierDiscovery:
    """What the target's own docs advertise about a free tier.

    ``advertised`` is the gate: when False the probe is NA (no free tier to
    exercise). ``opt_in_header`` is ``(name, value)`` if the docs document one.
    ``free_slugs`` are the service/meter identifiers the free allowance covers,
    used to pick the right callable endpoint (control-plane paths like /extend
    do not match a service slug and are deprioritized).
    """

    advertised: bool = False
    opt_in_header: tuple[str, str] | None = None
    free_units: int | None = None
    endpoint_hint: str | None = None  # best documented POST path for the free tier
    free_slugs: list[str] = field(default_factory=list)
    candidate_paths: list[str] = field(default_factory=list)
    openapi_ref: str | None = None  # referenced upstream OpenAPI spec URL
    evidence: dict[str, Any] = field(default_factory=dict)


def _find_free_quantity(obj: Any, _depth: int = 0) -> int | None:
    """Recursively find a positive free-allowance count in a manifest object."""
    if _depth > 6:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in _FREE_QUANTITY_KEYS:
                try:
                    n = int(v)
                except (TypeError, ValueError):
                    continue
                if n > 0:
                    return n
        for v in obj.values():
            found = _find_free_quantity(v, _depth + 1)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_free_quantity(v, _depth + 1)
            if found is not None:
                return found
    return None


def _scan_header_instruction(text: str) -> tuple[str, str] | None:
    """Scan doc prose for a free-tier opt-in header instruction.

    Looks for ``name: value`` patterns whose surrounding ~120 chars mention
    free/allowance/trial, skipping HTTP-plumbing header names. Returns the first
    plausible ``(name, value)`` or None.
    """
    if not text:
        return None
    for m in _HEADER_INSTRUCTION_RE.finditer(text):
        name, value = m.group(1), m.group(2)
        if name.lower() in _HEADER_NAME_DENYLIST:
            continue
        # A bare "version: 2" or "http: //" style match is noise unless it is a
        # real header-looking token AND sits in free-allowance context.
        window = text[max(0, m.start() - 100): m.end() + 100]
        if not _FREE_CONTEXT_RE.search(window):
            continue
        # The value "free" (or a header literally named for free mode) is the
        # strongest signal; require either the value or name to hint free mode
        # to avoid grabbing an unrelated "X-Api-Version: 2" near the word free.
        if "free" in value.lower() or "free" in name.lower() or "mode" in name.lower():
            return (name, value)
    return None


def discover_free_tier(docs: dict[str, str], manifest: Any | None) -> FreeTierDiscovery:
    """Decide whether a free tier is advertised, from the target's own docs.

    ``docs`` maps a doc path (e.g. ``/llms.txt``) to its text; ``manifest`` is
    the parsed manifest JSON (or None). Discovery is generic — no vendor names.
    """
    disc = FreeTierDiscovery()
    corpus = "\n".join(docs.values())

    free_units = _find_free_quantity(manifest) if manifest is not None else None
    header = _scan_header_instruction(corpus)
    mentions_free = bool(
        re.search(r"free\s+(allowance|tier|image|unit|includ|call)", corpus, re.I)
        or re.search(r"included\s*units", corpus, re.I)
    )

    # A free tier is "advertised" when the docs describe a free allowance AND
    # give us a way to opt in (a header instruction) or a positive unit count.
    disc.advertised = bool((header is not None or (free_units and free_units > 0)) and mentions_free)
    disc.opt_in_header = header
    disc.free_units = free_units
    disc.free_slugs = _free_slugs(manifest)
    disc.candidate_paths = _all_post_paths(corpus)
    disc.openapi_ref = _openapi_ref(corpus, manifest)
    # Best-effort pick from prose alone (the orchestration layer may refine this
    # with OpenAPI paths once it has a live session).
    disc.endpoint_hint = _rank_endpoint(disc.candidate_paths, disc.free_slugs)
    disc.evidence = {
        "opt_in_header": list(header) if header else None,
        "free_units": free_units,
        "free_slugs": disc.free_slugs,
        "mentions_free": mentions_free,
        "docs_seen": sorted(docs.keys()),
    }
    return disc


def _free_slugs(manifest: Any | None) -> list[str]:
    """Service/meter slugs that carry a positive free allowance, from a manifest.

    Generic: any object with a positive ``includedUnits``-style count contributes
    its ``serviceSlug``/``meterSlug``/``slug``/``service`` values.
    """
    slugs: list[str] = []

    def walk(obj: Any, depth: int = 0) -> None:
        if depth > 6 or obj is None:
            return
        if isinstance(obj, dict):
            has_free = any(
                isinstance(k, str) and k.lower() in _FREE_QUANTITY_KEYS
                and _positive_int(obj.get(k))
                for k in obj
            )
            if has_free:
                for key in ("serviceSlug", "meterSlug", "service", "meter", "slug"):
                    val = obj.get(key)
                    if isinstance(val, str) and val:
                        slugs.append(val.lower())
            for v in obj.values():
                walk(v, depth + 1)
        elif isinstance(obj, list):
            for v in obj:
                walk(v, depth + 1)

    walk(manifest)
    # dedupe, preserve order
    seen: set[str] = set()
    out: list[str] = []
    for s in slugs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _positive_int(v: Any) -> bool:
    try:
        return int(v) > 0
    except (TypeError, ValueError):
        return False


_OPENAPI_REF_RE = re.compile(r"https?://[^\s`\"'<>)]+openapi[^\s`\"'<>)]*\.json", re.I)


def _openapi_ref(corpus: str, manifest: Any | None) -> str | None:
    """URL of a referenced OpenAPI spec (the real callable paths often live there)."""
    if isinstance(manifest, dict):
        ref = manifest.get("openapi")
        if isinstance(ref, str) and ref.startswith("http"):
            return ref
    m = _OPENAPI_REF_RE.search(corpus or "")
    return m.group(0) if m else None


# Match "POST /path" or "POST https://host/path" and capture the PATH only.
# The optional URL prefix consumes scheme+host (up to but not including the
# first "/" of the path) so the captured path keeps its full depth.
_METHOD_PATH_RE = re.compile(
    r"\bPOST\s+(?:https?://[A-Za-z0-9.\-]+)?(/[A-Za-z0-9_\-/{}.]*[A-Za-z0-9}])"
)


# Control-plane / account-management paths a ZeroClick-style proxy documents.
# These are NOT the service call an agent trials — deprioritize them so the
# free-tier probe hits the actual metered endpoint, not /extend or /purchase.
_CONTROL_PLANE_RE = re.compile(
    r"/(extend|purchase|plans?|access|account|auth|register|claim|billing|topup|top-up)\b",
    re.I,
)


def _all_post_paths(corpus: str) -> list[str]:
    """All documented, non-templated ``POST /path`` values (deduped, in order)."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _METHOD_PATH_RE.finditer(corpus or ""):
        path = m.group(1)
        if "{" in path or "<" in path:  # skip templated paths
            continue
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def _rank_endpoint(paths: list[str], free_slugs: list[str]) -> str | None:
    """Pick the best callable endpoint for the free tier from candidate paths.

    Ranking (highest first):
      2 — path contains a free-allowance service/meter slug (the metered call);
      1 — a plain service path that is not control-plane;
      0 — control-plane (/extend, /plans/.../purchase, ...).
    Ties break on declaration order. Returns None when there are no candidates.
    """
    if not paths:
        return None

    def score(path: str) -> int:
        low = path.lower()
        if any(slug and slug in low for slug in free_slugs):
            return 2
        if _CONTROL_PLANE_RE.search(low):
            return 0
        return 1

    ranked = sorted(range(len(paths)), key=lambda i: (-score(paths[i]), i))
    best = paths[ranked[0]]
    # If the only candidates are control-plane, we have no real service endpoint.
    if score(best) == 0:
        return None
    return best


# ---------------------------------------------------------------------------
# Challenge parsing + the $0 safety gate
# ---------------------------------------------------------------------------
@dataclass
class Challenge:
    """The parsed x402 ``exact``-scheme entry we intend to settle."""

    x402_version: int
    scheme: str
    network: str  # CAIP-2, e.g. "eip155:8453"
    asset: str  # token contract address
    amount: str  # atomic-unit amount as a string; "0" is the free-tier gate
    pay_to: str
    token_name: str
    token_version: str
    raw_accepts: dict[str, Any]

    @property
    def chain_id(self) -> int | None:
        """Numeric EVM chain id from the CAIP-2 ``eip155:<id>`` network."""
        m = re.match(r"eip155:(\d+)", self.network or "")
        return int(m.group(1)) if m else None

    @property
    def is_zero_value(self) -> bool:
        """True iff the amount is exactly zero. THE gate for signing."""
        try:
            return int(self.amount) == 0
        except (TypeError, ValueError):
            return False


def parse_challenge(status: int, body_text: str) -> Challenge | None:
    """Parse an x402 v2 ``exact`` challenge out of a 402 JSON body.

    Returns None when the response is not a parseable x402 exact challenge (a
    non-402, non-JSON, or a body with no ``exact`` entry in ``accepts``). Picks
    the EVM ``exact`` entry — that is the one we can settle with a zero-value
    EIP-3009 authorization.
    """
    if status != 402:
        return None
    try:
        data = json.loads(body_text or "")
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    accepts = data.get("accepts")
    if not isinstance(accepts, list):
        return None
    for entry in accepts:
        if not isinstance(entry, dict):
            continue
        if entry.get("scheme") != "exact":
            continue
        network = str(entry.get("network", ""))
        if not network.startswith("eip155:"):  # EVM only for this signer
            continue
        extra = entry.get("extra") if isinstance(entry.get("extra"), dict) else {}
        return Challenge(
            x402_version=int(data.get("x402Version", 2)),
            scheme="exact",
            network=network,
            asset=str(entry.get("asset", "")),
            amount=str(entry.get("amount", "")),
            pay_to=str(entry.get("payTo", "")),
            token_name=str(extra.get("name", "USD Coin")),
            token_version=str(extra.get("version", "2")),
            raw_accepts=entry,
        )
    return None


# ---------------------------------------------------------------------------
# Ephemeral key + ZERO-VALUE signing (behind a clean interface)
# ---------------------------------------------------------------------------
class NonZeroChallengeError(Exception):
    """Raised if a settle is attempted on a nonzero-value challenge.

    This should be impossible to trigger via :func:`run` (the caller checks
    ``challenge.is_zero_value`` first and records ``free-tier-not-zero-cost``
    without calling the signer). The guard inside :func:`_settle_zero_value` is
    the structural backstop that makes "never sign value != 0" a property of the
    code, not just of the caller's discipline.
    """


def new_ephemeral_address_and_signer():
    """Create a fresh in-process EVM key; return ``(address, signer_callable)``.

    The private key never leaves this function's closure and is discarded when
    the run ends — we log only the address. We never read the user's wallets,
    keychains, ``~/.zero``, or any env key.

    Returns ``(None, None)`` if ``eth-account`` is unavailable so the caller can
    degrade to a ``settle-unverified`` finding rather than crash.
    """
    try:
        from eth_account import Account
    except Exception:  # pragma: no cover - import guard
        return None, None

    acct = Account.create()  # fresh entropy, zero-balance, single-use

    def _sign_typed(typed_data: dict) -> str:
        signed = acct.sign_typed_data(full_message=typed_data)
        return "0x" + signed.signature.hex().removeprefix("0x")

    return acct.address, _sign_typed


def _build_transfer_authorization_typed_data(
    challenge: Challenge, from_address: str
) -> dict:
    """EIP-712 ``TransferWithAuthorization`` typed data for a ZERO-VALUE settle.

    Mirrors the x402 ``exact`` EVM scheme: EIP-3009 transferWithAuthorization on
    the challenge's USDC contract, ``value: 0``, ``to`` the zero address, a
    random 32-byte nonce, validity ``[0, now+window]``. Domain name/version come
    from the challenge's ``extra`` (verified live) so the signature matches what
    the facilitator recomputes.
    """
    if not challenge.is_zero_value:
        # Defence in depth: this function is only called on a zero-value
        # challenge, but never build signable data for a nonzero one.
        raise NonZeroChallengeError(
            f"refusing to build authorization for nonzero amount {challenge.amount!r}"
        )
    chain_id = challenge.chain_id
    if chain_id is None:
        raise ValueError(f"non-EVM or malformed network {challenge.network!r}")

    now = int(time.time())
    nonce = "0x" + os.urandom(32).hex()
    zero_addr = "0x0000000000000000000000000000000000000000"
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "domain": {
            "name": challenge.token_name,
            "version": challenge.token_version,
            "chainId": chain_id,
            "verifyingContract": challenge.asset,
        },
        "primaryType": "TransferWithAuthorization",
        "message": {
            "from": from_address,
            "to": zero_addr,
            "value": 0,  # HARD ZERO — the safety property, in the signed struct
            "validAfter": 0,
            "validBefore": now + _AUTH_WINDOW_S,
            "nonce": nonce,
        },
    }


def _settle_zero_value(challenge: Challenge, from_address: str, signer) -> str:
    """Build + sign the ZERO-VALUE authorization; return the ``x-payment`` value.

    Refuses (raises :class:`NonZeroChallengeError`) unless the challenge amount
    is exactly zero. Produces the base64-encoded x402 v2 PaymentPayload the
    server expects in the ``x-payment`` header.
    """
    if not challenge.is_zero_value:
        raise NonZeroChallengeError(
            f"refusing to settle nonzero challenge amount {challenge.amount!r}"
        )
    typed = _build_transfer_authorization_typed_data(challenge, from_address)
    signature = signer(typed)
    msg = typed["message"]
    # x402 v2 PaymentPayload envelope (camelCase, matching the SDK's
    # BaseX402Model.to_camel serialization): {x402Version, payload, accepted}.
    # ``accepted`` echoes the challenge's accepts[] entry verbatim — that is the
    # requirements object the facilitator binds the signature to; a flat
    # scheme/network at the top level fails verification (identity_invalid).
    payment_payload = {
        "x402Version": challenge.x402_version,
        "payload": {
            "signature": signature,
            "authorization": {
                "from": msg["from"],
                "to": msg["to"],
                "value": str(msg["value"]),  # "0"
                "validAfter": str(msg["validAfter"]),
                "validBefore": str(msg["validBefore"]),
                "nonce": msg["nonce"],
            },
        },
        "accepted": _accepted_requirements(challenge),
    }
    encoded = base64.b64encode(
        json.dumps(payment_payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    return encoded


def _accepted_requirements(challenge: Challenge) -> dict:
    """The PaymentRequirements object to echo as ``accepted`` in the payload.

    Prefer the challenge's exact accepts[] entry (so every field the facilitator
    hashed round-trips); fall back to reconstructing the canonical fields.
    """
    raw = challenge.raw_accepts
    if isinstance(raw, dict) and raw:
        return raw
    return {
        "scheme": challenge.scheme,
        "network": challenge.network,
        "asset": challenge.asset,
        "amount": challenge.amount,
        "payTo": challenge.pay_to,
        "maxTimeoutSeconds": 300,
        "extra": {"name": challenge.token_name, "version": challenge.token_version},
    }


# ---------------------------------------------------------------------------
# Live probe orchestration
# ---------------------------------------------------------------------------
@dataclass
class ProbeOutcome:
    """Result of one end-to-end free-tier attempt (checkpoint ladder)."""

    advertised: bool = False
    challenge_received: bool = False
    settled: bool = False
    delivered: bool = False
    finding: str = ""
    remediation: str = ""
    ephemeral_address: str | None = None
    challenge_amount: str | None = None
    content_marker: str | None = None  # e.g. an imageUrl / content field name
    evidence: dict[str, Any] = field(default_factory=dict)


def _fetch_text(session: requests.Session, url: str) -> tuple[int | None, str]:
    try:
        r = session.get(url, timeout=_HTTP_TIMEOUT_S)
        return r.status_code, r.text or ""
    except requests.exceptions.RequestException:
        return None, ""
    except Exception:  # pragma: no cover - defensive
        return None, ""


def _agent_surface_base(ctx, home_text: str, llms_text: str) -> str:
    """Best agent-surface origin: the same-domain subdomain the docs link to.

    Reuses the protocols-probe convention (agents.<apex> etc.); falls back to
    the scored origin itself. Vendor-neutral — just "the agent surface the site
    points agents at".
    """
    apex = getattr(ctx, "domain", "") or ""
    if apex.startswith("www."):
        apex = apex[4:]
    text = (home_text or "") + "\n" + (llms_text or "")
    hosts = re.findall(r"https?://([A-Za-z0-9.-]+\.%s)\b" % re.escape(apex), text)
    for host in hosts:
        if host.lower() not in (apex, f"www.{apex}"):
            return f"https://{host}"
    return getattr(ctx, "base_url", f"https://{apex}")


def _gather_docs(session: requests.Session, base: str) -> tuple[dict[str, str], Any | None]:
    """Fetch the agent-surface discovery docs; return (docs_by_path, manifest)."""
    docs: dict[str, str] = {}
    manifest: Any | None = None
    for path in _DISCOVERY_DOCS:
        status, text = _fetch_text(session, base.rstrip("/") + path)
        if status == 200 and text.strip():
            docs[path] = text
            if path.endswith(".json"):
                try:
                    manifest = json.loads(text)
                except (ValueError, TypeError):
                    manifest = None
    return docs, manifest


def _openapi_post_paths(session: requests.Session, url: str) -> list[str]:
    """POST operation paths from a referenced OpenAPI spec (best-effort)."""
    status, text = _fetch_text(session, url)
    if status != 200 or not text.strip():
        return []
    try:
        spec = json.loads(text)
    except (ValueError, TypeError):
        return []
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return []
    out: list[str] = []
    for p, ops in paths.items():
        if not isinstance(p, str) or not p.startswith("/") or "{" in p:
            continue
        if isinstance(ops, dict) and "post" in {k.lower() for k in ops}:
            out.append(p)
    return out


def _resolve_endpoint(session: requests.Session, base: str, disc: FreeTierDiscovery) -> str | None:
    """The documented call to trial for the free tier.

    Candidate POST paths come from the docs prose AND the referenced upstream
    OpenAPI spec (where a proxy's real service paths usually live, while the
    prose only documents control-plane paths like /extend). Ranked so a path
    matching the free allowance's service/meter slug wins over control-plane
    paths. Vendor-neutral — no hardcoded endpoint.
    """
    candidates = list(disc.candidate_paths)
    if disc.openapi_ref:
        candidates += _openapi_post_paths(session, disc.openapi_ref)
    # dedupe preserving order
    seen: set[str] = set()
    merged: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            merged.append(c)
    best = _rank_endpoint(merged, disc.free_slugs)
    if best is None:
        return None
    return base.rstrip("/") + best


def probe_free_tier(ctx, out_dir: str = "runs") -> ProbeOutcome:
    """Run ONE end-to-end free-tier attempt. Never raises.

    Discovers the free tier from the target's own docs, makes the opt-in call,
    and — only if the returned challenge is exactly zero-value — settles it with
    a fresh ephemeral key and verifies the retry delivers content. Any failure
    is captured as a finding, not an exception.
    """
    out = ProbeOutcome()
    session = requests.Session()
    session.headers.update({"Accept": "*/*", "User-Agent": "asrs-free-tier-probe/0.4"})

    # -- discovery --
    try:
        home = ctx.homepage(ua="browser")
        home_text = getattr(home, "text", "") or ""
    except Exception:
        home_text = ""
    apex = getattr(ctx, "domain", "")
    apex_base = getattr(ctx, "base_url", f"https://{apex}")
    llms_status, llms_text = _fetch_text(session, apex_base.rstrip("/") + "/llms.txt")

    agent_base = _agent_surface_base(ctx, home_text, llms_text)
    docs, manifest = _gather_docs(session, agent_base)
    # Fall back to the apex's own docs if the agent surface had none.
    if not docs:
        docs, manifest = _gather_docs(session, apex_base)
        agent_base = apex_base

    disc = discover_free_tier(docs, manifest)
    out.advertised = disc.advertised
    out.evidence["discovery"] = disc.evidence
    out.evidence["agent_base"] = agent_base

    if not disc.advertised:
        out.finding = "no-free-tier-advertised"
        out.remediation = ""  # NA — never a defect
        return out

    if disc.opt_in_header is None:
        # Advertised (unit count) but no opt-in header we can send — we can't
        # exercise it. Not a failure of the site's rails, so CANT_TEST-style.
        out.finding = "free-tier-opt-in-undiscoverable"
        out.remediation = (
            "A free allowance is advertised but the opt-in mechanism (a request "
            "header) is not documented in the agent-surface docs; document the "
            "header an agent must send so the allowance is machine-discoverable."
        )
        return out

    endpoint = _resolve_endpoint(session, agent_base, disc)
    if endpoint is None:
        out.finding = "free-tier-endpoint-undiscoverable"
        out.remediation = (
            "A free allowance is advertised but no callable endpoint (a documented "
            "POST path) was discoverable from the docs; document the endpoint an "
            "agent should call to use the allowance."
        )
        return out

    header_name, header_value = disc.opt_in_header
    out.evidence["opt_in_header"] = [header_name, header_value]
    out.evidence["endpoint"] = endpoint

    # -- the documented free-mode call --
    call_headers = {header_name: header_value, "Content-Type": "application/json"}
    body = _example_body(manifest, disc)
    try:
        r = session.post(endpoint, headers=call_headers, data=json.dumps(body), timeout=_HTTP_TIMEOUT_S)
    except requests.exceptions.RequestException as exc:
        out.finding = "free-tier-no-response"
        out.remediation = (
            "The documented free-mode call did not respond; confirm the endpoint "
            "is reachable and returns an x402 challenge for anonymous callers."
        )
        out.evidence["error"] = f"{type(exc).__name__}: {exc}"
        return out
    except Exception as exc:  # pragma: no cover - defensive
        out.finding = "free-tier-no-response"
        out.remediation = ""
        out.evidence["error"] = f"{type(exc).__name__}: {exc}"
        return out

    out.evidence["call_status"] = r.status_code

    # A 200 straight away means an already-known wallet — but a FRESH ephemeral
    # key never is, so on our probe this is unexpected; still, treat delivered
    # content as success (defensive).
    if r.status_code == 200 and _has_content(r.text):
        out.challenge_received = False
        out.settled = True
        out.delivered = True
        out.finding = "free-tier-delivered"
        out.content_marker = _content_marker(r.text)
        out.evidence["response_snippet"] = (r.text or "")[:400]
        return out

    challenge = parse_challenge(r.status_code, r.text)
    if challenge is None:
        # Allowance already used up returns a priced 402 (or a non-challenge).
        if r.status_code == 402:
            out.finding = "free-tier-exhausted"
            out.remediation = (
                "The free allowance appears exhausted for this identity (the "
                "free-mode call returned a priced 402). The meter works; this is "
                "expected once the allowance is spent."
            )
            out.evidence["response_snippet"] = (r.text or "")[:400]
            return out
        out.finding = "free-tier-no-challenge"
        out.remediation = (
            "The documented free-mode call did not return a parseable x402 "
            "identity challenge; emit a zero-value x402 challenge (accepts[] with "
            "amount 0) so an agent can prove identity and use the allowance."
        )
        out.evidence["response_snippet"] = (r.text or "")[:400]
        return out

    out.challenge_received = True
    out.challenge_amount = challenge.amount
    out.evidence["challenge"] = {
        "amount": challenge.amount,
        "network": challenge.network,
        "asset": challenge.asset,
        "pay_to": challenge.pay_to,
        "scheme": challenge.scheme,
    }

    # -- THE SAFETY GATE: only settle a ZERO-VALUE challenge --
    if not challenge.is_zero_value:
        # A free tier whose challenge demands real payment is not actually free.
        out.finding = "free-tier-not-zero-cost"
        out.remediation = (
            "The advertised free-tier call returned a challenge demanding a "
            f"nonzero payment (amount {challenge.amount!r}); a free allowance "
            "must issue a zero-value identity challenge (amount 0). We do not "
            "sign any nonzero authorization."
        )
        return out

    # -- settle with a fresh ephemeral key --
    address, signer = new_ephemeral_address_and_signer()
    if signer is None:
        out.finding = "settle-unverified"
        out.remediation = (
            "Could not load the signing library (eth-account) to settle the "
            "zero-value challenge; install it to verify the settle end-to-end."
        )
        return out
    out.ephemeral_address = address
    out.evidence["ephemeral_address"] = address

    try:
        x_payment = _settle_zero_value(challenge, address, signer)
    except NonZeroChallengeError:
        # Unreachable given the gate above, but recorded rather than raised.
        out.finding = "free-tier-not-zero-cost"
        out.remediation = "Refused to sign a nonzero authorization."
        return out
    except Exception as exc:
        out.finding = "settle-failed"
        out.remediation = (
            "Signing the zero-value authorization failed "
            f"({type(exc).__name__}); the challenge shape may not match the x402 "
            "exact EVM scheme."
        )
        out.evidence["error"] = f"{type(exc).__name__}: {exc}"
        return out

    # -- retry with the signed proof --
    retry_headers = dict(call_headers)
    retry_headers["x-payment"] = x_payment
    try:
        r2 = session.post(endpoint, headers=retry_headers, data=json.dumps(body), timeout=_HTTP_TIMEOUT_S)
    except requests.exceptions.RequestException as exc:
        out.finding = "settle-failed"
        out.remediation = (
            "The settle retry did not respond; the signed zero-value proof could "
            "not be delivered."
        )
        out.evidence["error"] = f"{type(exc).__name__}: {exc}"
        return out
    except Exception as exc:  # pragma: no cover - defensive
        out.finding = "settle-failed"
        out.remediation = ""
        out.evidence["error"] = f"{type(exc).__name__}: {exc}"
        return out

    out.evidence["retry_status"] = r2.status_code
    out.evidence["retry_headers"] = {
        k: v for k, v in r2.headers.items()
        if k.lower() in ("payment-response", "zc-billing", "content-type")
    }

    if r2.status_code == 200 and _has_content(r2.text):
        out.settled = True
        out.delivered = True
        out.finding = "free-tier-delivered"
        out.content_marker = _content_marker(r2.text)
        out.evidence["response_snippet"] = (r2.text or "")[:600]
        _save_evidence(out_dir, apex, out, r.text, dict(r2.headers), r2.text)
        return out

    if r2.status_code == 402:
        # A second 402 after a valid-shaped settle = allowance exhausted mid-run
        # (meter counted our zero-value identity as known, then had nothing left)
        # OR the identity proof did not verify. The meter WORKED (identity was
        # accepted enough to re-challenge), so we count it settled-not-delivered.
        retry_ch = parse_challenge(r2.status_code, r2.text)
        if retry_ch is not None and not retry_ch.is_zero_value:
            out.settled = True  # identity accepted; now it's a priced call
            out.delivered = False
            out.finding = "free-tier-exhausted"
            out.remediation = (
                "The zero-value identity settled but the allowance is exhausted "
                "(the retry returned a priced 402). The meter works; this is "
                "expected once the free units are spent."
            )
            out.evidence["response_snippet"] = (r2.text or "")[:400]
            _save_evidence(out_dir, apex, out, r.text, dict(r2.headers), r2.text)
            return out
        out.settled = False
        out.finding = "settle-failed"
        out.remediation = (
            "The signed zero-value identity proof did not verify (the retry "
            "returned another identity challenge); confirm the challenge's "
            "token name/version and EIP-3009 typed-data shape."
        )
        out.evidence["response_snippet"] = (r2.text or "")[:400]
        _save_evidence(out_dir, apex, out, r.text, dict(r2.headers), r2.text)
        return out

    # Any other status: settle attempted, no content delivered.
    out.settled = False
    out.finding = "settle-failed"
    out.remediation = (
        f"The settle retry returned HTTP {r2.status_code} without content; the "
        "zero-value proof was not accepted."
    )
    out.evidence["response_snippet"] = (r2.text or "")[:400]
    _save_evidence(out_dir, apex, out, r.text, dict(r2.headers), r2.text)
    return out


def _example_body(manifest: Any | None, disc: FreeTierDiscovery) -> dict:
    """A minimal request body for the trial call.

    Prefer an example body the challenge/manifest advertises (x402 ``bazaar``
    extension carries one); otherwise a generic prompt. Vendor-neutral: we read
    the body shape from the target, not from a hardcoded vendor schema.
    """
    # x402 bazaar input example, if the manifest or a prior challenge exposed one.
    example = _find_example_body(manifest)
    if example:
        return example
    # Generic last resort: most text-in APIs accept a bare prompt; anything
    # tier- or model-specific must come from the target's own example.
    return {"prompt": "a simple test image of a paper airplane"}


def _find_example_body(obj: Any, _depth: int = 0) -> dict | None:
    """Find an example request body (bazaar ``input.body``) in a manifest."""
    if _depth > 6 or obj is None:
        return None
    if isinstance(obj, dict):
        # x402 bazaar shape: {"input": {"body": {...}, "method": "POST"}}
        inp = obj.get("input")
        if isinstance(inp, dict) and isinstance(inp.get("body"), dict):
            body = inp["body"]
            if body and "example" not in json.dumps(body).lower():
                return body
        for v in obj.values():
            found = _find_example_body(v, _depth + 1)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_example_body(v, _depth + 1)
            if found:
                return found
    return None


_CONTENT_KEYS = ("imageurl", "image_url", "url", "result", "output", "content", "data", "text")


def _has_content(text: str) -> bool:
    """True when a 200 body carries actual delivered content, not just an ack."""
    if not text or not text.strip():
        return False
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        # Non-JSON 200 with a body (e.g. an image) still counts as content.
        return len(text.strip()) > 0
    if isinstance(data, dict):
        lower = {k.lower(): v for k, v in data.items()}
        return any(lower.get(k) for k in _CONTENT_KEYS)
    return bool(data)


def _content_marker(text: str) -> str | None:
    """Name the content field we saw (for evidence), e.g. ``imageUrl``."""
    try:
        data = json.loads(text or "")
    except (ValueError, TypeError):
        return "non-json-body"
    if isinstance(data, dict):
        for k in data:
            if k.lower() in _CONTENT_KEYS and data[k]:
                return k
    return None


def _save_evidence(
    out_dir: str, domain: str, out: ProbeOutcome, challenge_body: str,
    response_headers: dict, response_body: str,
) -> str:
    """Persist raw challenge + response evidence. Never raises."""
    try:
        edir = os.path.join(out_dir, "free_tier")
        os.makedirs(edir, exist_ok=True)
        safe = domain.replace("/", "_").replace(":", "_")
        path = os.path.join(edir, f"{safe}_free_tier.json")
        payload = {
            "domain": domain,
            "finding": out.finding,
            "ephemeral_address": out.ephemeral_address,
            "challenge_amount": out.challenge_amount,
            "checkpoints": {
                "advertised": out.advertised,
                "challenge_received": out.challenge_received,
                "settled": out.settled,
                "delivered": out.delivered,
            },
            "challenge_body": _maybe_json(challenge_body),
            "response_headers": {k: v for k, v in response_headers.items()},
            "response_body": _maybe_json(response_body),
            "evidence": out.evidence,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        return path
    except OSError:
        return ""


def _maybe_json(text: str) -> Any:
    try:
        return json.loads(text or "")
    except (ValueError, TypeError):
        return (text or "")[:2000]


# ---------------------------------------------------------------------------
# Check emission
# ---------------------------------------------------------------------------
def build_check(out: ProbeOutcome) -> CheckResult:
    """Roll a :class:`ProbeOutcome` into the single ``bhv_free_tier_transaction``.

    NA when no free tier is advertised; otherwise checkpoint partial credit:
    advertised (1) + challenge (1) + settled (2) + content (1).
    """
    # No free tier advertised -> NA (never punished for its absence).
    if not out.advertised:
        return CheckResult(
            check_id=CHECK_ID, pillar=PILLAR, status=Status.NA,
            points=0.0, max_points=MAX_POINTS,
            finding="no-free-tier-advertised", remediation="",
            evidence=out.evidence,
        )

    # Undiscoverable opt-in / endpoint: advertised but we can't exercise it.
    if out.finding in ("free-tier-opt-in-undiscoverable", "free-tier-endpoint-undiscoverable"):
        return CheckResult(
            check_id=CHECK_ID, pillar=PILLAR, status=Status.CANT_TEST,
            points=0.0, max_points=MAX_POINTS,
            finding=out.finding, remediation=out.remediation,
            evidence=out.evidence,
        )

    # No response at all from the documented call.
    if out.finding == "free-tier-no-response":
        return CheckResult(
            check_id=CHECK_ID, pillar=PILLAR, status=Status.CANT_TEST,
            points=0.0, max_points=MAX_POINTS,
            finding=out.finding, remediation=out.remediation,
            evidence=out.evidence,
        )

    points = _PTS_ADVERTISED  # advertised is proven at this point
    if out.challenge_received:
        points += _PTS_CHALLENGE
    if out.settled:
        points += _PTS_SETTLED
    if out.delivered:
        points += _PTS_CONTENT

    if out.delivered:
        status = Status.PASS
    elif out.finding == "free-tier-not-zero-cost":
        # Advertised free tier that is not actually free — a real defect, but
        # we earned the "advertised" rung; it is a partial with a clear finding.
        status = Status.PARTIAL
    elif out.settled:
        status = Status.PARTIAL  # e.g. exhausted: meter worked, no content
    elif out.challenge_received:
        status = Status.PARTIAL  # got the challenge, settle failed
    else:
        status = Status.PARTIAL  # advertised only (exhausted-before-challenge)

    evidence = dict(out.evidence)
    evidence["checkpoints"] = {
        "advertised": out.advertised,
        "challenge_received": out.challenge_received,
        "settled": out.settled,
        "delivered": out.delivered,
    }
    if out.content_marker:
        evidence["content_field"] = out.content_marker
    if out.ephemeral_address:
        evidence["ephemeral_address"] = out.ephemeral_address

    return CheckResult(
        check_id=CHECK_ID, pillar=PILLAR, status=status,
        points=round(points, 3), max_points=MAX_POINTS,
        finding=out.finding or "free-tier-partial",
        remediation=out.remediation,
        evidence=evidence,
    )


def run_probe(ctx, out_dir: str = "runs") -> list[CheckResult]:
    """Public entry point: run the single free-tier attempt and emit its check.

    Guarded end-to-end — any unexpected error degrades to a CANT_TEST finding so
    a crash here never aborts the behavioral pipeline.
    """
    try:
        outcome = probe_free_tier(ctx, out_dir=out_dir)
        return [build_check(outcome)]
    except Exception as exc:  # pragma: no cover - top-level guard
        return [
            CheckResult(
                check_id=CHECK_ID, pillar=PILLAR, status=Status.CANT_TEST,
                points=0.0, max_points=MAX_POINTS,
                finding="free-tier-probe-error", remediation="",
                evidence={"error": f"{type(exc).__name__}: {exc}"},
            )
        ]
