"""Legibility pillar probes: can an agent understand what's for sale?

Checks:
  - llms_txt                 — /llms.txt or /llms-full.txt present + non-trivial
  - sitemap                  — sitemap.xml discoverable (direct or via robots)
  - product_schema           — schema.org Product/Offer/Service JSON-LD w/ price
  - pricing_machine_readable — a price visible in server-rendered HTML (no JS)
  - api_docs_surface         — public docs/API reference discoverable

All emit pillar="legibility". Network failure/ambiguity => CANT_TEST.
"""

from __future__ import annotations

import json
import re

from asrs.fetch import FetchContext, FetchResult
from asrs.types import CheckResult, Status

# Homepage/llms.txt links matching these hint at a product/pricing surface.
_PRODUCT_LINK_RE = re.compile(r"/?(pricing|product|products|shop|store|plans|api)\b", re.I)
_DOCS_LINK_RE = re.compile(r"/?(docs|api|developer|developers|reference)\b", re.I)

# A recognizable price in raw HTML: currency+amount, "per month", "/mo", credits,
# or a free-tier phrase. Server-side visible pricing = agent-legible pricing.
_PRICE_RE = re.compile(
    r"(?:[$€£]\s?\d[\d,]*(?:\.\d{2})?)"
    r"|(?:\bper\s+(?:month|year|credit|seat|user|request|call)\b)"
    r"|(?:\b\d[\d,]*\s*(?:credits?|tokens?)\b)"
    r"|(?:/\s?mo\b|/\s?month\b|/\s?yr\b)"
    r"|(?:\bfree\s+tier\b)"
    r"|(?:\bpricing\b.{0,40}?[$€£]\d)",
    re.I,
)

_PRODUCT_LD_TYPES = {"product", "offer", "aggregateoffer", "service", "softwareapplication"}


_LEGIBILITY_CHECKS = (
    ("llms_txt", 5.0),
    ("sitemap", 3.0),
    ("product_schema", 8.0),
    ("pricing_machine_readable", 5.0),
    ("api_docs_surface", 4.0),
)


def run(ctx: FetchContext) -> list[CheckResult]:
    ctx.homepage()  # resolve base_url first
    home = ctx.homepage(ua="browser")
    # If the site itself is unreachable, nothing is testable — emit CANT_TEST for
    # every check rather than punishing an absence we couldn't have observed.
    if home.error is not None or home.status is None:
        return [
            CheckResult(
                cid, "legibility", Status.CANT_TEST, 0.0, mp,
                finding="site-unreachable",
                remediation="Site did not respond; confirm it is reachable before "
                "assessing legibility.",
                evidence={"url": home.url, "error": home.error},
            )
            for cid, mp in _LEGIBILITY_CHECKS
        ]
    robots = ctx.get("/robots.txt", ua="browser")
    llms = _fetch_llms(ctx)
    candidates = _candidate_product_pages(ctx, home, llms)
    return [
        _llms_txt(llms),
        _sitemap(ctx, robots),
        _product_schema(ctx, candidates),
        _pricing_machine_readable(ctx, candidates),
        _api_docs_surface(ctx, home),
    ]


# ---------------------------------------------------------------------------
# llms_txt
# ---------------------------------------------------------------------------


def _fetch_llms(ctx: FetchContext) -> FetchResult | None:
    """Return the first present llms file (llms.txt then llms-full.txt), else None."""
    for path in ("/llms.txt", "/llms-full.txt"):
        res = ctx.get(path, ua="browser")
        if res.ok and res.status == 200 and _looks_texty(res):
            return res
    return None


def _llms_txt(llms: FetchResult | None) -> CheckResult:
    max_points, check_id, pillar = 5.0, "llms_txt", "legibility"
    if llms is None:
        return CheckResult(
            check_id, pillar, Status.FAIL, 0.0, max_points,
            finding="llms-txt-missing",
            remediation="Publish an /llms.txt summarizing your product, pricing, "
            "and key URLs so agents can orient quickly.",
            evidence={"probed": ["/llms.txt", "/llms-full.txt"]},
        )
    body = (llms.text or "").strip()
    ev = {"url": llms.final_url or llms.url, "length": len(body), "snippet": body[:300]}
    if len(body) < 200:
        return CheckResult(
            check_id, pillar, Status.PARTIAL, 2.5, max_points,
            finding="llms-txt-trivial",
            remediation="Expand /llms.txt with concrete product, pricing, and "
            "navigation detail (it is currently near-empty).",
            evidence=ev,
        )
    return CheckResult(
        check_id, pillar, Status.PASS, max_points, max_points,
        finding="llms-txt-present", remediation="", evidence=ev,
    )


# ---------------------------------------------------------------------------
# sitemap
# ---------------------------------------------------------------------------


def _sitemap(ctx: FetchContext, robots: FetchResult) -> CheckResult:
    max_points, check_id, pillar = 3.0, "sitemap", "legibility"

    # 1) Sitemap: directive in robots.txt.
    robots_sitemaps: list[str] = []
    if robots.ok and robots.status == 200:
        for line in (robots.text or "").splitlines():
            s = line.strip()
            if s.lower().startswith("sitemap:"):
                robots_sitemaps.append(s.split(":", 1)[1].strip())
    if robots_sitemaps:
        return CheckResult(
            check_id, pillar, Status.PASS, max_points, max_points,
            finding="sitemap-present", remediation="",
            evidence={"source": "robots.txt", "sitemaps": robots_sitemaps[:5]},
        )

    # 2) /sitemap.xml directly.
    sm = ctx.get("/sitemap.xml", ua="browser")
    if sm.ok and sm.status == 200 and ("<urlset" in sm.text.lower() or "<sitemapindex" in sm.text.lower()):
        return CheckResult(
            check_id, pillar, Status.PASS, max_points, max_points,
            finding="sitemap-present", remediation="",
            evidence={"source": "/sitemap.xml", "url": sm.final_url or sm.url},
        )

    return CheckResult(
        check_id, pillar, Status.FAIL, 0.0, max_points,
        finding="sitemap-missing",
        remediation="Publish a sitemap.xml (and reference it via a Sitemap: line "
        "in robots.txt) so agents can enumerate your pages.",
        evidence={"probed": ["/sitemap.xml", "robots.txt Sitemap:"], "sitemap_status": sm.status},
    )


# ---------------------------------------------------------------------------
# product_schema
# ---------------------------------------------------------------------------


def _product_schema(ctx: FetchContext, candidates: list[FetchResult]) -> CheckResult:
    max_points, check_id, pillar = 8.0, "product_schema", "legibility"

    if not candidates:
        return CheckResult(
            check_id, pillar, Status.CANT_TEST, 0.0, max_points,
            finding="pages-unreachable",
            remediation="No candidate product/pricing page could be fetched to "
            "inspect for structured data; confirm those pages are reachable.",
            evidence={},
        )

    any_jsonld = False
    for res in candidates:
        blocks = _extract_jsonld(res.text)
        for obj in blocks:
            any_jsonld = True
            found_type = _product_type_with_price(obj)
            if found_type:
                return CheckResult(
                    check_id, pillar, Status.PASS, max_points, max_points,
                    finding="product-schema-present", remediation="",
                    evidence={
                        "page": res.final_url or res.url,
                        "type": found_type,
                        "snippet": json.dumps(obj)[:300],
                    },
                )

    if any_jsonld:
        return CheckResult(
            check_id, pillar, Status.PARTIAL, 4.0, max_points,
            finding="jsonld-present-no-offer",
            remediation="Add schema.org Product/Offer JSON-LD with a price to your "
            "product/pricing pages (JSON-LD is present but has no offer/price).",
            evidence={"pages": [r.final_url or r.url for r in candidates][:5]},
        )
    return CheckResult(
        check_id, pillar, Status.FAIL, 0.0, max_points,
        finding="no-structured-product-data",
        remediation="Add schema.org Product/Offer/Service JSON-LD (with price and "
        "availability) so agents can parse what you sell.",
        evidence={"pages_checked": [r.final_url or r.url for r in candidates][:5]},
    )


# ---------------------------------------------------------------------------
# pricing_machine_readable
# ---------------------------------------------------------------------------


def _pricing_machine_readable(ctx: FetchContext, candidates: list[FetchResult]) -> CheckResult:
    max_points, check_id, pillar = 5.0, "pricing_machine_readable", "legibility"

    # Whether any candidate is actually a pricing/product-ish page.
    priced_pages = [c for c in candidates if _is_product_url(c.final_url or c.url)]
    search_set = priced_pages or candidates

    if not search_set:
        return CheckResult(
            check_id, pillar, Status.FAIL, 0.0, max_points,
            finding="no-pricing-page-found",
            remediation="Publish a reachable pricing/product page (none was found "
            "from homepage or llms.txt links).",
            evidence={},
        )

    for res in search_set:
        m = _PRICE_RE.search(_visible_text(res.text))
        if m:
            return CheckResult(
                check_id, pillar, Status.PASS, max_points, max_points,
                finding="pricing-visible-server-side", remediation="",
                evidence={
                    "page": res.final_url or res.url,
                    "match": m.group(0)[:120],
                },
            )

    return CheckResult(
        check_id, pillar, Status.FAIL, 0.0, max_points,
        finding="pricing-requires-js-or-absent",
        remediation="Render at least one concrete price in server-side HTML "
        "(current pricing appears to require JS or is absent).",
        evidence={"pages_checked": [r.final_url or r.url for r in search_set][:5]},
    )


# ---------------------------------------------------------------------------
# api_docs_surface
# ---------------------------------------------------------------------------


def _api_docs_surface(ctx: FetchContext, home: FetchResult) -> CheckResult:
    max_points, check_id, pillar = 4.0, "api_docs_surface", "legibility"

    probes = ["/docs", "/api", "/docs/api", "/openapi.json", "/.well-known/api-catalog"]
    # Homepage links matching docs/api/developer.
    for href in _links(home.text, home.final_url or home.url):
        if _DOCS_LINK_RE.search(href):
            probes.append(href)
    seen: set[str] = set()
    checked: list[dict] = []
    for target in probes:
        if target in seen:
            continue
        seen.add(target)
        res = ctx.get(target, ua="browser")
        checked.append({"url": res.url, "status": res.status})
        if res.ok and res.status == 200 and len((res.text or "").strip()) > 50:
            return CheckResult(
                check_id, pillar, Status.PASS, max_points, max_points,
                finding="api-docs-present", remediation="",
                evidence={"url": res.final_url or res.url, "status": res.status},
            )

    return CheckResult(
        check_id, pillar, Status.FAIL, 0.0, max_points,
        finding="no-api-docs-surface",
        remediation="Publish public API docs (e.g. /docs, an OpenAPI spec, or "
        "/.well-known/api-catalog) so agents can learn how to integrate.",
        evidence={"probed": checked[:8]},
    )


# ---------------------------------------------------------------------------
# discovery + extraction helpers
# ---------------------------------------------------------------------------


def _candidate_product_pages(
    ctx: FetchContext, home: FetchResult, llms: FetchResult | None
) -> list[FetchResult]:
    """Homepage + up to 4 discovered product/pricing pages (from links + llms.txt)."""
    pages: list[FetchResult] = []
    seen_urls: set[str] = set()
    if home.ok:
        pages.append(home)
        seen_urls.add(home.final_url or home.url)

    hrefs: list[str] = []
    for href in _links(home.text, home.final_url or home.url):
        if _PRODUCT_LINK_RE.search(href):
            hrefs.append(href)
    if llms is not None:
        for href in _urls_in_text(llms.text):
            if _PRODUCT_LINK_RE.search(href):
                hrefs.append(href)

    added = 0
    for href in hrefs:
        if added >= 4:
            break
        res = ctx.get(href, ua="browser")
        key = res.final_url or res.url
        if key in seen_urls:
            continue
        seen_urls.add(key)
        if res.ok and res.status == 200:
            pages.append(res)
            added += 1
    return pages


_SCRIPT_LD_RE = re.compile(
    r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)


def _extract_jsonld(html: str) -> list[dict]:
    """Extract JSON-LD objects, flattening arrays and @graph. Malformed => skipped."""
    objs: list[dict] = []
    for m in _SCRIPT_LD_RE.finditer(html or ""):
        raw = m.group(1).strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            continue
        for obj in _flatten_ld(data):
            if isinstance(obj, dict):
                objs.append(obj)
    return objs


def _flatten_ld(data) -> list:
    out: list = []
    if isinstance(data, list):
        for item in data:
            out.extend(_flatten_ld(item))
    elif isinstance(data, dict):
        out.append(data)
        graph = data.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                out.extend(_flatten_ld(item))
    return out


def _product_type_with_price(obj: dict) -> str | None:
    """Return the matched @type if this object is a product/offer/service with price."""
    types = _types_of(obj)
    matched = next((t for t in types if t.lower() in _PRODUCT_LD_TYPES), None)
    if matched is None:
        return None
    if _has_price(obj):
        return matched
    return None


def _types_of(obj: dict) -> list[str]:
    t = obj.get("@type") or obj.get("type")
    if isinstance(t, str):
        return [t]
    if isinstance(t, list):
        return [x for x in t if isinstance(x, str)]
    return []


def _has_price(obj: dict) -> bool:
    """True if the object (or its offers) carries a price/priceSpecification."""
    for key in ("price", "priceSpecification", "lowPrice", "highPrice"):
        if obj.get(key) not in (None, ""):
            return True
    offers = obj.get("offers")
    if isinstance(offers, dict):
        return _has_price(offers) or "price" in offers
    if isinstance(offers, list):
        return any(isinstance(o, dict) and _has_price(o) for o in offers)
    # An Offer object itself, even without an explicit price key, counts as an
    # offer signal only if it has price-ish fields (handled above).
    return False


# ---------------------------------------------------------------------------
# small shared text helpers
# ---------------------------------------------------------------------------

_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.I)
_URL_RE = re.compile(r'https?://[^\s<>")\']+')
_TAG_RE = re.compile(r"<[^>]+>")


def _looks_texty(res: FetchResult) -> bool:
    ct = (res.headers.get("content-type") or "").lower()
    if "text/html" in ct:
        # llms.txt served as HTML (a soft-404 page) doesn't count.
        return False
    if ct and not any(x in ct for x in ("text/plain", "text/markdown", "application/octet-stream", "text/")):
        return False
    low = (res.text or "").lstrip().lower()
    return not low.startswith("<!doctype") and not low.startswith("<html")


def _links(html: str, base: str):
    from urllib.parse import urljoin

    for m in _HREF_RE.finditer(html or ""):
        href = m.group(1).strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        yield urljoin(base or "", href)


def _urls_in_text(text: str):
    for m in _URL_RE.finditer(text or ""):
        yield m.group(0)


def _is_product_url(url: str) -> bool:
    return bool(_PRODUCT_LINK_RE.search(url or ""))


def _visible_text(html: str) -> str:
    """Strip tags so price regex doesn't match inside attributes/scripts noise."""
    if not html:
        return ""
    # Keep it cheap: drop script/style bodies then tags.
    no_script = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    return _TAG_RE.sub(" ", no_script)
