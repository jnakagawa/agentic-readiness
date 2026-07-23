"""Transactability pillar probes: can an agent pay + provision WITHOUT a human?

Checks (rubric v0.3 — scored for agentic services, not retail webshops):
  - x402_probe     — agent-native payment: live HTTP 402 handshake (full), or
                     documented x402 / ACP/UCP commerce surface (partial)
  - mcp_surface    — BONUS: MCP server discoverable (worth little; a per-service
                     MCP server duplicates generic HTTP + a 402 handshake)
  - self_serve_payg — provisioning tiers: no-signup (full) > self-serve signup
                     (partial) > sales-gated (fail)

All emit pillar="transactability". Network failure/ambiguity => CANT_TEST.
"""

from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

from asrs.fetch import FetchContext, FetchResult
from asrs.types import CheckResult, Status

PILLAR = "transactability"

_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.I)
_DOCS_LINK_RE = re.compile(r"/?(docs|api|developer|developers|reference)\b", re.I)


_PROTOCOL_CHECKS = (
    ("x402_probe", 8.0),
    ("mcp_surface", 2.0),
    ("self_serve_payg", 6.0),
)


def run(ctx: FetchContext) -> list[CheckResult]:
    ctx.homepage()
    home = ctx.homepage(ua="browser")
    # If the site itself is unreachable, we can't probe any protocol surface.
    if home.error is not None or home.status is None:
        return [
            CheckResult(
                cid, PILLAR, Status.CANT_TEST, 0.0, mp,
                finding="site-unreachable",
                remediation="Site did not respond; confirm it is reachable before "
                "probing payment/agent protocols.",
                evidence={"url": home.url, "error": home.error},
            )
            for cid, mp in _PROTOCOL_CHECKS
        ]
    # Gather the pooled text an agent would read (homepage + docs + llms.txt) once.
    docs = _fetch_docs_pages(ctx, home)
    llms = ctx.get("/llms.txt", ua="browser")
    corpus = _corpus(home, docs, llms)
    # Agent-surface subdomains (agents.<domain> etc.) referenced from the
    # homepage or llms.txt — where sites like the ZeroClick template keep the
    # actual payment rails. Follow the breadcrumbs the way an agent would.
    agent_bases = _agent_surface_bases(ctx, home, llms)
    agent_pages = _fetch_agent_surface_pages(ctx, agent_bases)
    corpus = "\n".join([corpus] + [p.text or "" for p in agent_pages])
    # self_serve_payg looks at homepage + pricing pages specifically, and a
    # live 402 handshake is itself proof of no-signup provisioning.
    pricing = _fetch_pricing_pages(ctx, home)
    payg_corpus = "\n".join([corpus] + [p.text or "" for p in pricing])
    x402 = _x402_probe(ctx, home, docs, corpus, agent_bases, agent_pages)
    return [
        x402,
        _mcp_surface(ctx, corpus),
        _self_serve_payg(ctx, home, pricing, payg_corpus, x402_live=x402.finding == "x402-live"),
    ]


# ---------------------------------------------------------------------------
# x402_probe
# ---------------------------------------------------------------------------


def _x402_probe(
    ctx: FetchContext,
    home: FetchResult,
    docs: list[FetchResult],
    corpus: str,
    agent_bases: list[str] | None = None,
    agent_pages: list[FetchResult] | None = None,
) -> CheckResult:
    max_points, check_id = 8.0, "x402_probe"
    agent_bases = agent_bases or []
    agent_pages = agent_pages or []

    targets = ["/api", "/api/v1", "/v1"]
    targets += _api_bases_from_docs(docs)
    targets += _paths_near_keyword(corpus, "x402")
    # Concrete endpoints on the agent surface: API paths named in its
    # discovery docs ("POST /generate", openapi paths), joined to each base.
    agent_targets = _agent_surface_targets(ctx, agent_bases, agent_pages)
    targets += agent_targets
    targets = _dedupe(targets)

    # Payment-gated endpoints usually challenge only on their real (POST)
    # method — a GET just 404s. Empty-body POST is a safe handshake probe,
    # but only where the surface itself documents x402 (an expected 402).
    surface_documents_x402 = "x402" in "\n".join(p.text or "" for p in agent_pages).lower()
    post_ok = set(agent_targets) if surface_documents_x402 else set()

    probed: list[dict] = []
    saw_402 = False
    for target in targets[:16]:
        res = ctx.get(target, ua="browser")
        probed.append({"url": res.url, "status": res.status, "method": "GET"})
        if res.status != 402 and target in post_ok:
            res = ctx.post_empty(target, ua="browser")
            probed.append({"url": res.url, "status": res.status, "method": "POST"})
        if res.status == 402:
            saw_402 = True
            payload = _parse_x402(res)
            if payload:
                return CheckResult(
                    check_id, PILLAR, Status.PASS, max_points, max_points,
                    finding="x402-live", remediation="",
                    evidence={"url": res.final_url or res.url, "x402": payload},
                )

    if saw_402:
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 4.0, max_points,
            finding="http-402-no-x402-payload",
            remediation="An endpoint returns HTTP 402 but without a parseable x402 "
            "payment-requirements payload; emit the accepts/payTo/maxAmountRequired body.",
            evidence={"probed": probed[:8]},
        )
    if "x402" in corpus.lower():
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 4.0, max_points,
            finding="x402-documented-not-probed",
            remediation="x402 is mentioned in your docs but no probed endpoint "
            "returned a live 402; expose a discoverable x402-gated endpoint.",
            evidence={"probed": probed[:8], "mention": _mention_snippet(corpus, "x402")},
        )

    # ACP/UCP commerce protocols earn partial credit here (for services the
    # 402 handshake IS the commerce protocol; these are the retail-side kin).
    commerce = _commerce_protocol_evidence(ctx, home, corpus)
    if commerce is not None:
        finding, pts, ev = commerce
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, pts, max_points,
            finding=finding,
            remediation="A commerce-protocol surface exists but there is no "
            "agent-native payment handshake; expose an HTTP-402 payment-"
            "requirements endpoint (x402/MPP) so agents can pay per-request.",
            evidence={**ev, "probed": probed[:8]},
        )

    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-agent-native-payment",
        remediation="Offer an agent-native payment endpoint (HTTP 402 + "
        "payment-requirements, x402/MPP) so agents can pay per-request "
        "without an account.",
        evidence={"probed": probed[:8]},
    )


def _parse_x402(res: FetchResult) -> dict | None:
    """Return x402 requirement fields if the 402 body/headers look like x402."""
    # Header-based signals.
    hdrs = {k: v for k, v in res.headers.items() if "x402" in k or "payment" in k}
    body_signal = None
    text = (res.text or "").strip()
    if text:
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            data = None
        if isinstance(data, dict):
            keys = {"accepts", "payto", "maxamountrequired", "x402version", "paymentrequirements"}
            lower_keys = {k.lower() for k in data.keys()}
            if lower_keys & keys:
                body_signal = {k: data[k] for k in list(data.keys())[:6]}
            # Nested accepts array is the canonical x402 shape.
            elif isinstance(data.get("accepts"), list):
                body_signal = {"accepts": data["accepts"][:2]}
    if body_signal or hdrs:
        out: dict = {}
        if body_signal:
            out["body"] = json.loads(json.dumps(body_signal))
            out["snippet"] = json.dumps(body_signal)[:300]
        if hdrs:
            out["headers"] = hdrs
        return out
    return None


# ---------------------------------------------------------------------------
# mcp_surface
# ---------------------------------------------------------------------------


def _mcp_surface(ctx: FetchContext, corpus: str) -> CheckResult:
    # BONUS check (v0.3): a per-service MCP server mostly duplicates what
    # generic HTTP + a 402 handshake gives an agent — detect it, reward it a
    # little, never treat its absence as a defect.
    max_points, check_id = 2.0, "mcp_surface"

    probed: list[dict] = []

    # /.well-known/mcp.json — a hit is a 200 with JSON.
    wk = ctx.get("/.well-known/mcp.json", ua="browser")
    probed.append({"url": wk.url, "status": wk.status})
    if wk.ok and wk.status == 200 and _looks_json(wk):
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="mcp-server-discoverable", remediation="",
            evidence={"url": wk.final_url or wk.url, "snippet": (wk.text or "")[:300]},
        )

    # /mcp and /api/mcp — a JSON-RPC-ish error or 405/406 also proves a server.
    for path in ("/mcp", "/api/mcp"):
        res = ctx.get(path, ua="browser")
        probed.append({"url": res.url, "status": res.status})
        if _mcp_endpoint_hit(res):
            return CheckResult(
                check_id, PILLAR, Status.PASS, max_points, max_points,
                finding="mcp-server-discoverable", remediation="",
                evidence={"url": res.final_url or res.url, "status": res.status,
                          "snippet": (res.text or "")[:300]},
            )

    if _mentions_mcp(corpus):
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 1.0, max_points,
            finding="mcp-documented-only",
            remediation="MCP is referenced in your docs but no MCP endpoint was "
            "discoverable; publish /.well-known/mcp.json or a live /mcp handshake.",
            evidence={"probed": probed, "mention": _mention_snippet(corpus, "mcp")},
        )
    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-mcp-surface",
        remediation="Optional: expose an MCP server (/.well-known/mcp.json or a "
        "/mcp endpoint). Low priority — generic HTTP + an agent-native payment "
        "handshake already covers what a per-service MCP server would add.",
        evidence={"probed": probed},
    )


def _mcp_endpoint_hit(res: FetchResult) -> bool:
    if res.error is not None or res.status is None:
        return False
    if res.status in (405, 406):
        return True
    if res.status == 200 and _looks_json(res):
        return True
    low = (res.text or "").lower()
    # JSON-RPC / MCP error shapes are strong evidence a server exists.
    if '"jsonrpc"' in low or "jsonrpc" in low or "invalid session" in low or "mcp-session" in low:
        return True
    if res.headers.get("mcp-session-id") or res.headers.get("mcp-protocol-version"):
        return True
    return False


def _mentions_mcp(corpus: str) -> bool:
    low = corpus.lower()
    return "mcp server" in low or "model context protocol" in low or "\"mcp\"" in low or "/mcp" in low


# ---------------------------------------------------------------------------
# commerce_protocol_signals
# ---------------------------------------------------------------------------

_COMMERCE_PHRASES = (
    "agentic checkout",
    "agentic commerce protocol",
    "universal commerce protocol",
    "checkout_sessions",
    "checkout-sessions",
    "/checkout_sessions",
)

# Well-known commerce-manifest paths, and the structural keys each protocol's
# own published manifest carries. Keyed by the protocol's capability shape,
# never by a vendor. Grounded in the published specs:
#   UCP  — /.well-known/ucp declares services/capabilities/payment/endpoints,
#          capabilities named reverse-domain (e.g. dev.ucp.shopping.checkout)
#          (developers.googleblog.com "Under the Hood: UCP"; ucp.dev).
#   ACP  — checkout payload carries line_items/payment_provider/currency+status
#          (docs.stripe.com/agentic-commerce; developers.openai.com/commerce).
_COMMERCE_WELL_KNOWN = ("/.well-known/ucp", "/.well-known/agentic-commerce")
_UCP_MANIFEST_KEYS = frozenset(
    {"capabilities", "services", "payment", "payments", "endpoints"}
)
_ACP_PAYLOAD_KEYS = frozenset(
    {"line_items", "payment_provider", "checkout_session",
     "checkout_sessions", "checkout_session_id"}
)


def _parse_commerce_manifest(res: FetchResult) -> dict | None:
    """Validate that a well-known response is a real commerce-protocol manifest.

    Returns the identifying structural fields (bounded) or None. A well-known
    path that merely 200s (a catch-all SPA index, a soft-404 page) is NOT a
    commerce surface; credit requires the response to actually parse as a
    UCP service/capability manifest or an ACP checkout payload. Mirrors the
    way ``_parse_x402`` validates a 402 body rather than trusting the status.
    Keys on protocol structure only — no vendor or domain string.
    """
    if not (res.ok and res.status == 200):
        return None
    text = (res.text or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    keys_lower = {k.lower() for k in data}
    protocol: str | None = None
    matched: list[str] = []
    if keys_lower & _UCP_MANIFEST_KEYS:
        protocol, matched = "ucp", sorted(keys_lower & _UCP_MANIFEST_KEYS)
    elif keys_lower & _ACP_PAYLOAD_KEYS:
        protocol, matched = "acp", sorted(keys_lower & _ACP_PAYLOAD_KEYS)
    elif "dev.ucp." in json.dumps(data).lower():
        # Reverse-domain UCP capability identifiers nested anywhere in the body.
        protocol, matched = "ucp", ["capabilities"]
    if protocol is None:
        return None
    out: dict = {"protocol": protocol, "fields": matched}
    for k in data:
        if k.lower() in ("version", "protocol_version", "ucp_version"):
            out["version"] = str(data[k])[:40]
            break
    out["snippet"] = json.dumps(data)[:300]
    return out


def _commerce_protocol_evidence(
    ctx: FetchContext, home: FetchResult, corpus: str
) -> tuple[str, float, dict] | None:
    """ACP/UCP surface evidence for x402_probe partial credit (v0.3, v0.7).

    Returns ``(finding, points, evidence)`` or None. For services the 402
    handshake is the commerce protocol; the retail-side protocols earn
    partial credit on the same check instead of their own line.

    v0.7 tightens the well-known branch: a validated commerce manifest earns
    the partial as ``commerce-protocol-live`` (elicited, like x402-live), while
    a bare 200 at a well-known path no longer counts (it was a false positive —
    a catch-all index that 200s /.well-known/ucp is not a commerce surface).
    """
    for path in _COMMERCE_WELL_KNOWN:
        res = ctx.get(path, ua="browser")
        manifest = _parse_commerce_manifest(res)
        if manifest is not None:
            return (
                "commerce-protocol-live", 4.0,
                {"url": res.final_url or res.url, "manifest": manifest},
            )

    low = corpus.lower()
    matched_phrase = next((p for p in _COMMERCE_PHRASES if p in low), None)
    if matched_phrase:
        return (
            "commerce-protocol-only", 4.0,
            {"phrase": matched_phrase, "mention": _mention_snippet(corpus, matched_phrase)},
        )

    # Shopify platform fingerprint => inherits UCP/catalog rails.
    if _is_shopify(home):
        return (
            "commerce-protocol-via-platform", 3.0,
            {"platform": "shopify", "signals": _shopify_signals(home)},
        )
    return None


def _is_shopify(home: FetchResult) -> bool:
    return bool(_shopify_signals(home))


def _shopify_signals(home: FetchResult) -> list[str]:
    signals: list[str] = []
    for hdr in ("x-shopid", "x-shopify-stage", "x-sorting-hat-shopid", "powered-by"):
        val = home.headers.get(hdr)
        if val and ("shop" in hdr or "shopify" in str(val).lower()):
            signals.append(f"header:{hdr}")
    if "cdn.shopify.com" in (home.text or "").lower() or "shopify" in (home.headers.get("x-powered-by", "").lower()):
        signals.append("cdn.shopify.com")
    return signals


# ---------------------------------------------------------------------------
# self_serve_payg
# ---------------------------------------------------------------------------

# Visible-text CTA phrases that signal a self-serve purchase/provisioning path.
_SELF_SERVE_PHRASES = (
    "pay as you go",
    "pay-as-you-go",
    "no credit card required",
    "get api key",
    "get your api key",
    "get an api key",
    "sign up",
    "signup",
    "sign-up",
    "create account",
    "create an account",
    "start for free",
    "get started free",
    "get started",
    "buy now",
    "buy an",
    "add to cart",
    "start free trial",
    "subscribe",
    "self-serve",
    "self serve",
)
# Same signals when they appear inside a link href.
_SELF_SERVE_LINK_RE = re.compile(
    r"(sign[-\s]?up|signup|register|get[-\s]?started|get[-\s]?api[-\s]?key|checkout|"
    r"/buy\b|purchase|subscribe|add[-\s]?to[-\s]?cart)",
    re.I,
)
_SALES_PHRASES = (
    "contact sales",
    "book a demo",
    "request a demo",
    "request access",
    "talk to sales",
    "get a quote",
    "contact us for pricing",
)
# Language promising provisioning with no account at all — the top tier.
# Deliberately excludes "no api key" alone: it appears in signup-flow copy
# ("No API key yet? Sign up") and false-positives sites with account gates.
_NO_SIGNUP_PHRASES = (
    "no signup",
    "no sign-up",
    "no sign up",
    "without signup",
    "without a signup",
    "no account required",
    "without an account",
    "no registration",
)


def _self_serve_payg(
    ctx: FetchContext,
    home: FetchResult,
    pricing: list[FetchResult],
    corpus: str,
    x402_live: bool = False,
) -> CheckResult:
    """Provisioning tiers (v0.3): no-signup > self-serve signup > sales-gated.

    Full marks are reserved for a path where an agent can pay and call with no
    account creation at all — the thing that lets it transact where it
    otherwise couldn't. A live 402 handshake is itself proof of that tier.
    """
    max_points, check_id = 6.0, "self_serve_payg"

    if not home.ok:
        return CheckResult(
            check_id, PILLAR, Status.CANT_TEST, 0.0, max_points,
            finding="homepage-unreachable",
            remediation="Homepage could not be fetched to assess the purchase path; "
            "confirm the site is reachable.",
            evidence={"error": home.error},
        )

    # Scan visible text (buttons/CTAs live in text, not hrefs) across homepage +
    # pricing pages, plus any self-serve hrefs and stripe checkout links.
    visible = _visible_text(corpus).lower()
    low = corpus.lower()
    no_signup = [p for p in _NO_SIGNUP_PHRASES if p in visible]
    self_serve = [p for p in _SELF_SERVE_PHRASES if p in visible]
    has_stripe = "stripe.com/checkout" in low or "checkout.stripe.com" in low or "buy.stripe.com" in low
    link_pool = list(_all_links(home))
    for p in pricing:
        link_pool.extend(_all_links(p))
    cta_links = [h for h in _dedupe(link_pool) if _SELF_SERVE_LINK_RE.search(h)]
    sales = [p for p in _SALES_PHRASES if p in visible]

    self_serve_present = bool(self_serve or has_stripe or cta_links)
    ev = {
        "x402_live": x402_live,
        "no_signup_phrases": no_signup[:5],
        "self_serve_phrases": self_serve[:5],
        "stripe_checkout": has_stripe,
        "cta_links": cta_links[:5],
        "sales_phrases": sales[:5],
        "pricing_pages": [p.final_url or p.url for p in pricing][:3],
    }

    if x402_live or no_signup:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="no-signup-provisioning", remediation="", evidence=ev,
        )
    if self_serve_present:
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 3.0, max_points,
            finding="self-serve-signup",
            remediation="Self-serve exists but requires creating an account first; "
            "add a no-signup programmatic path (HTTP-402 payment challenges) so "
            "an agent can transact without provisioning an identity.",
            evidence=ev,
        )
    if sales:
        return CheckResult(
            check_id, PILLAR, Status.FAIL, 0.0, max_points,
            finding="sales-gated-only",
            remediation="Add a self-serve purchase path (ideally no-signup via "
            "HTTP-402; at minimum checkout or API-key buy) so agents can "
            "transact without a 'contact sales' step.",
            evidence=ev,
        )
    # Neither signal present: can't tell what the purchase path is.
    return CheckResult(
        check_id, PILLAR, Status.CANT_TEST, 0.0, max_points,
        finding="purchase-path-indeterminate",
        remediation="No clear self-serve or sales-gated purchase signal was found; "
        "surface a purchase/API-key CTA so the path is discoverable.",
        evidence=ev,
    )


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------


_ABS_URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+")
# "POST /generate", "ANY /<path>" style method+path mentions in agent docs.
_METHOD_PATH_RE = re.compile(r"\b(?:GET|POST|PUT|PATCH|ANY)\s+(/[A-Za-z0-9_\-/.]*[A-Za-z0-9])")
# Discovery docs an agent surface serves at well-known paths.
_AGENT_SURFACE_DOCS = ("/llms.txt", "/llms-full.txt", "/manifest.json")


def _agent_surface_bases(ctx: FetchContext, home: FetchResult, llms: FetchResult | None) -> list[str]:
    """Same-registrable-domain subdomain origins linked from homepage/llms.txt.

    agents.<domain> and friends — where the ZeroClick template (and pattern-
    alike storefronts) keep the actual agent rails. Never leaves the scored
    domain: a host qualifies only when it is a subdomain of the apex.
    """
    apex = ctx.domain.lower()
    if apex.startswith("www."):
        apex = apex[4:]
    skip_hosts = {apex, f"www.{apex}", urlparse(ctx.base_url).netloc.lower()}

    candidates = list(_all_links(home))
    if llms is not None and llms.ok and llms.status == 200:
        candidates += [m.group(0) for m in _ABS_URL_RE.finditer(llms.text or "")]

    bases: list[str] = []
    for url in candidates:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if not host or host in skip_hosts or not host.endswith(f".{apex}"):
            continue
        bases.append(f"{parsed.scheme or 'https'}://{host}")
    # agents.* first — the conventional home for the payment surface.
    bases = sorted(_dedupe(bases), key=lambda b: (0 if urlparse(b).netloc.startswith("agent") else 1, b))
    return bases[:3]


def _fetch_agent_surface_pages(ctx: FetchContext, bases: list[str]) -> list[FetchResult]:
    """Fetch each agent base's discovery docs (llms.txt / llms-full.txt / manifest.json)."""
    out: list[FetchResult] = []
    for base in bases:
        for path in _AGENT_SURFACE_DOCS:
            res = ctx.get(base + path, ua="browser")
            if res.ok and res.status == 200 and (res.text or "").strip():
                out.append(res)
    return out


def _agent_surface_targets(
    ctx: FetchContext, bases: list[str], pages: list[FetchResult]
) -> list[str]:
    """Concrete probe-able endpoints on the agent surface.

    Pulls API paths the surface's own docs name — "POST /generate" mentions,
    absolute URLs on an agent host, and paths from a referenced openapi.json —
    and joins the relative ones to each base.
    """
    if not bases:
        return []
    text = "\n".join(p.text or "" for p in pages)
    base_hosts = {urlparse(b).netloc for b in bases}

    paths = [m.group(1) for m in _METHOD_PATH_RE.finditer(text)]

    targets: list[str] = []
    for m in _ABS_URL_RE.finditer(text):
        parsed = urlparse(m.group(0))
        if parsed.netloc in base_hosts and len(parsed.path.strip("/")) > 0:
            # Their own docs pages aren't API endpoints.
            if not any(parsed.path.endswith(d) for d in _AGENT_SURFACE_DOCS):
                targets.append(f"{parsed.scheme}://{parsed.netloc}{parsed.path}")
        elif "openapi" in parsed.path.lower() and parsed.path.lower().endswith(".json"):
            paths += _openapi_paths(ctx, m.group(0))

    for base in bases:
        for path in _dedupe(paths)[:5]:
            if "{" not in path and "<" not in path:
                targets.append(base + path)
    return _dedupe(targets)[:8]


def _openapi_paths(ctx: FetchContext, url: str) -> list[str]:
    """Operation paths from an openapi.json the agent surface references."""
    res = ctx.get(url, ua="browser")
    if not (res.ok and res.status == 200):
        return []
    try:
        spec = json.loads(res.text or "")
    except (ValueError, TypeError):
        return []
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return []
    return [p for p in list(paths.keys())[:5] if isinstance(p, str) and p.startswith("/")]


def _fetch_docs_pages(ctx: FetchContext, home: FetchResult) -> list[FetchResult]:
    """Fetch a couple of docs/api pages so protocol mentions can be scanned."""
    targets = ["/docs", "/api", "/developers"]
    for href in _all_links(home):
        if _DOCS_LINK_RE.search(href):
            targets.append(href)
    out: list[FetchResult] = []
    seen: set[str] = set()
    for t in _dedupe(targets)[:5]:
        res = ctx.get(t, ua="browser")
        key = res.final_url or res.url
        if key in seen:
            continue
        seen.add(key)
        if res.ok and res.status == 200:
            out.append(res)
    return out


_PRICING_LINK_RE = re.compile(r"/?(pricing|plans|product|products|shop|store|buy|checkout)\b", re.I)


def _fetch_pricing_pages(ctx: FetchContext, home: FetchResult) -> list[FetchResult]:
    """Fetch homepage-linked pricing/product pages (self-serve signals live there)."""
    targets = ["/pricing", "/plans"]
    for href in _all_links(home):
        if _PRICING_LINK_RE.search(href):
            targets.append(href)
    out: list[FetchResult] = []
    seen: set[str] = set()
    for t in _dedupe(targets)[:4]:
        res = ctx.get(t, ua="browser")
        key = res.final_url or res.url
        if key in seen:
            continue
        seen.add(key)
        if res.ok and res.status == 200:
            out.append(res)
    return out


def _api_bases_from_docs(docs: list[FetchResult]) -> list[str]:
    """Pull absolute api.* base URLs mentioned in docs pages."""
    bases: list[str] = []
    for d in docs:
        for m in re.finditer(r"https?://[^\s\"'<>]+", d.text or ""):
            url = m.group(0)
            parsed = urlparse(url)
            if parsed.netloc.startswith("api.") or "/api" in parsed.path:
                bases.append(f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/"))
    return bases[:5]


def _paths_near_keyword(corpus: str, keyword: str) -> list[str]:
    """Extract URL-ish paths appearing within ~200 chars of a keyword mention."""
    out: list[str] = []
    low = corpus.lower()
    kw = keyword.lower()
    idx = low.find(kw)
    while idx != -1 and len(out) < 6:
        window = corpus[max(0, idx - 200): idx + 200]
        for m in re.finditer(r"(?:https?://[^\s\"'<>]+|/[A-Za-z0-9_\-/.]+)", window):
            frag = m.group(0)
            if any(x in frag for x in ("/api", "/v1", "/pay", "/paid", "402")):
                out.append(frag)
        idx = low.find(kw, idx + 1)
    return _dedupe(out)


def _corpus(home: FetchResult, docs: list[FetchResult], llms: FetchResult) -> str:
    parts = []
    if home.ok:
        parts.append(home.text or "")
    for d in docs:
        parts.append(d.text or "")
    if llms.ok and llms.status == 200:
        parts.append(llms.text or "")
    return "\n".join(parts)


def _all_links(res: FetchResult) -> list[str]:
    out: list[str] = []
    base = res.final_url or res.url
    for m in _HREF_RE.finditer(res.text or ""):
        href = m.group(1).strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        out.append(urljoin(base or "", href))
    return out


_TAG_RE = re.compile(r"<[^>]+>")


def _visible_text(html: str) -> str:
    """Strip script/style bodies and tags so phrase matching sees rendered text."""
    if not html:
        return ""
    no_script = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    return _TAG_RE.sub(" ", no_script)


def _looks_json(res: FetchResult) -> bool:
    ct = (res.headers.get("content-type") or "").lower()
    if "json" in ct:
        return True
    t = (res.text or "").lstrip()
    return t.startswith("{") or t.startswith("[")


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def _mention_snippet(corpus: str, keyword: str, limit: int = 300) -> str:
    low = corpus.lower()
    idx = low.find(keyword.lower())
    if idx == -1:
        return ""
    start = max(0, idx - 80)
    return corpus[start: idx + 120].strip()[:limit]
