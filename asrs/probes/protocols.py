"""Transactability pillar probes: can an agent pay programmatically?

Checks:
  - x402_probe                — live HTTP 402 x402 handshake, or documented x402
  - mcp_surface               — MCP server discoverable
  - commerce_protocol_signals — ACP/UCP markers, or platform inheritance (Shopify)
  - self_serve_payg           — self-serve pay-as-you-go path vs sales-gated only

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
    ("x402_probe", 6.0),
    ("mcp_surface", 5.0),
    ("commerce_protocol_signals", 4.0),
    ("self_serve_payg", 5.0),
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
    # self_serve_payg looks at homepage + pricing pages specifically.
    pricing = _fetch_pricing_pages(ctx, home)
    payg_corpus = "\n".join([corpus] + [p.text or "" for p in pricing])
    return [
        _x402_probe(ctx, home, docs, corpus),
        _mcp_surface(ctx, corpus),
        _commerce_protocol_signals(ctx, home, corpus),
        _self_serve_payg(ctx, home, pricing, payg_corpus),
    ]


# ---------------------------------------------------------------------------
# x402_probe
# ---------------------------------------------------------------------------


def _x402_probe(ctx: FetchContext, home: FetchResult, docs: list[FetchResult], corpus: str) -> CheckResult:
    max_points, check_id = 6.0, "x402_probe"

    targets = ["/api", "/api/v1", "/v1"]
    targets += _api_bases_from_docs(docs)
    targets += _paths_near_keyword(corpus, "x402")
    targets = _dedupe(targets)

    probed: list[dict] = []
    saw_402 = False
    for target in targets[:12]:
        res = ctx.get(target, ua="browser")
        probed.append({"url": res.url, "status": res.status})
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
            check_id, PILLAR, Status.PARTIAL, 3.0, max_points,
            finding="http-402-no-x402-payload",
            remediation="An endpoint returns HTTP 402 but without a parseable x402 "
            "payment-requirements payload; emit the accepts/payTo/maxAmountRequired body.",
            evidence={"probed": probed[:8]},
        )
    if "x402" in corpus.lower():
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 3.0, max_points,
            finding="x402-documented-not-probed",
            remediation="x402 is mentioned in your docs but no probed endpoint "
            "returned a live 402; expose a discoverable x402-gated endpoint.",
            evidence={"probed": probed[:8], "mention": _mention_snippet(corpus, "x402")},
        )
    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-x402-surface",
        remediation="Offer an x402-payable endpoint (HTTP 402 + payment-requirements) "
        "so agents can pay per-request without an account.",
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
    max_points, check_id = 5.0, "mcp_surface"

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
            check_id, PILLAR, Status.PARTIAL, 2.5, max_points,
            finding="mcp-documented-only",
            remediation="MCP is referenced in your docs but no MCP endpoint was "
            "discoverable; publish /.well-known/mcp.json or a live /mcp handshake.",
            evidence={"probed": probed, "mention": _mention_snippet(corpus, "mcp")},
        )
    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-mcp-surface",
        remediation="Expose an MCP server (e.g. /.well-known/mcp.json or a /mcp "
        "endpoint) so agents can call your tools programmatically.",
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


def _commerce_protocol_signals(ctx: FetchContext, home: FetchResult, corpus: str) -> CheckResult:
    max_points, check_id = 4.0, "commerce_protocol_signals"

    # Well-known commerce profiles.
    for path in ("/.well-known/ucp", "/.well-known/agentic-commerce"):
        res = ctx.get(path, ua="browser")
        if res.ok and res.status == 200 and len((res.text or "").strip()) > 10:
            return CheckResult(
                check_id, PILLAR, Status.PASS, max_points, max_points,
                finding="commerce-protocol-well-known", remediation="",
                evidence={"url": res.final_url or res.url},
            )

    low = corpus.lower()
    matched_phrase = next((p for p in _COMMERCE_PHRASES if p in low), None)
    if matched_phrase:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="commerce-protocol-documented", remediation="",
            evidence={"phrase": matched_phrase, "mention": _mention_snippet(corpus, matched_phrase)},
        )

    # Shopify platform fingerprint => inherits UCP/catalog rails.
    if _is_shopify(home):
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 2.0, max_points,
            finding="commerce-protocol-via-platform",
            remediation="Storefront runs on Shopify (inherits agentic-commerce/catalog "
            "rails); enable/advertise the agentic checkout surface explicitly to score full.",
            evidence={"platform": "shopify", "signals": _shopify_signals(home)},
        )

    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-commerce-protocol-signals",
        remediation="Adopt an agentic commerce protocol (ACP/UCP checkout-session "
        "endpoints or a well-known profile) so agents can complete purchases.",
        evidence={"probed": ["/.well-known/ucp", "/.well-known/agentic-commerce"]},
    )


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


def _self_serve_payg(
    ctx: FetchContext, home: FetchResult, pricing: list[FetchResult], corpus: str
) -> CheckResult:
    max_points, check_id = 5.0, "self_serve_payg"

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
    self_serve = [p for p in _SELF_SERVE_PHRASES if p in visible]
    has_stripe = "stripe.com/checkout" in low or "checkout.stripe.com" in low or "buy.stripe.com" in low
    link_pool = list(_all_links(home))
    for p in pricing:
        link_pool.extend(_all_links(p))
    cta_links = [h for h in _dedupe(link_pool) if _SELF_SERVE_LINK_RE.search(h)]
    sales = [p for p in _SALES_PHRASES if p in visible]

    self_serve_present = bool(self_serve or has_stripe or cta_links)
    ev = {
        "self_serve_phrases": self_serve[:5],
        "stripe_checkout": has_stripe,
        "cta_links": cta_links[:5],
        "sales_phrases": sales[:5],
        "pricing_pages": [p.final_url or p.url for p in pricing][:3],
    }

    if self_serve_present and not sales:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="self-serve-payg", remediation="", evidence=ev,
        )
    if self_serve_present and sales:
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 2.5, max_points,
            finding="self-serve-plus-sales-gate",
            remediation="Some tiers are self-serve but a sales gate is also present; "
            "ensure at least one full purchase path needs no human contact.",
            evidence=ev,
        )
    if sales and not self_serve_present:
        return CheckResult(
            check_id, PILLAR, Status.FAIL, 0.0, max_points,
            finding="sales-gated-only",
            remediation="Add a self-serve purchase path (checkout or API-key buy) so "
            "agents can transact without a 'contact sales' step.",
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
