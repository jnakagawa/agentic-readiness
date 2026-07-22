"""Trust pillar probes (static half): will an agent believe this is legit?

Checks (the behavioral trust_panel_willingness check lives elsewhere):
  - https_hsts         — valid HTTPS + HSTS header
  - org_identity       — verifiable org/company identity + contact
  - policies_present   — terms + privacy + refund/cancellation policies
  - reputation_signals — reviews/AggregateRating markup or 3rd-party presence

All emit pillar="trust". Network failure/ambiguity => CANT_TEST.
"""

from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

from asrs.fetch import FetchContext, FetchResult
from asrs.types import CheckResult, Status

PILLAR = "trust"

_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.I)
_TAG_RE = re.compile(r"<[^>]+>")

_COMPANY_SUFFIX_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9&.\-]+(?:\s+[A-Z][A-Za-z0-9&.\-]+)*,?\s*"
    r"(?:Inc\.?|LLC|L\.L\.C\.|Ltd\.?|GmbH|Corp\.?|Corporation|Co\.|B\.V\.|S\.A\.|Pty\.?|Limited|PBC)\b"
)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9.\s]{3,40}\b(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Blvd\.?|Suite|Ste\.?|Floor|Fl\.?)\b",
    re.I,
)


def run(ctx: FetchContext) -> list[CheckResult]:
    ctx.homepage()
    home = ctx.homepage(ua="browser")
    # https_hsts still runs on an unreachable homepage (it distinguishes
    # http-only / cert-failure / down); the content-derived checks can't.
    if home.error is not None or home.status is None:
        return [
            _https_hsts(ctx, home),
            _unreachable("org_identity", 4.0),
            _unreachable("policies_present", 3.0),
            _unreachable("reputation_signals", 3.0),
        ]
    return [
        _https_hsts(ctx, home),
        _org_identity(ctx, home),
        _policies_present(ctx, home),
        _reputation_signals(ctx, home),
    ]


def _unreachable(check_id: str, max_points: float) -> CheckResult:
    return CheckResult(
        check_id, PILLAR, Status.CANT_TEST, 0.0, max_points,
        finding="site-unreachable",
        remediation="Site did not respond; confirm it is reachable before "
        "assessing trust signals.",
        evidence={},
    )


# ---------------------------------------------------------------------------
# https_hsts
# ---------------------------------------------------------------------------


def _https_hsts(ctx: FetchContext, home: FetchResult) -> CheckResult:
    max_points, check_id = 5.0, "https_hsts"

    base = ctx.base_url
    is_https = urlparse(base).scheme == "https"

    # A cert error surfaces as a transport error on the homepage fetch. If the
    # https homepage failed, retry once over http to distinguish "http-only"
    # from "site down".
    if not home.ok:
        http_res = ctx.get(f"http://{ctx.domain}", ua="browser")
        if http_res.is_success and urlparse(http_res.final_url or "").scheme == "http":
            return CheckResult(
                check_id, PILLAR, Status.FAIL, 0.0, max_points,
                finding="no-https",
                remediation="Serve the site over HTTPS with a valid certificate "
                "(currently HTTP-only or the TLS handshake failed).",
                evidence={"base_url": base, "https_error": home.error, "http_status": http_res.status},
            )
        return CheckResult(
            check_id, PILLAR, Status.CANT_TEST, 0.0, max_points,
            finding="https-unverifiable",
            remediation="Could not complete an HTTPS handshake to verify TLS; "
            "confirm the site is reachable over HTTPS.",
            evidence={"base_url": base, "error": home.error},
        )

    # Homepage succeeded. If the final URL is http, treat as no-https.
    final_scheme = urlparse(home.final_url or base).scheme
    if not is_https or final_scheme == "http":
        return CheckResult(
            check_id, PILLAR, Status.FAIL, 0.0, max_points,
            finding="no-https",
            remediation="Redirect all traffic to HTTPS (the site resolves over HTTP).",
            evidence={"base_url": base, "final_url": home.final_url},
        )

    hsts = home.headers.get("strict-transport-security")
    if hsts:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="https-hsts", remediation="",
            evidence={"base_url": base, "strict_transport_security": hsts[:120]},
        )
    return CheckResult(
        check_id, PILLAR, Status.PARTIAL, 3.0, max_points,
        finding="https-no-hsts",
        remediation="Add a Strict-Transport-Security header to enforce HTTPS on "
        "every request (HTTPS works but HSTS is not set).",
        evidence={"base_url": base, "final_url": home.final_url},
    )


# ---------------------------------------------------------------------------
# org_identity
# ---------------------------------------------------------------------------


def _org_identity(ctx: FetchContext, home: FetchResult) -> CheckResult:
    max_points, check_id = 4.0, "org_identity"

    paths = ["/about", "/contact", "/company", "/legal", "/imprint"]
    for href in _footer_links(home):
        if re.search(r"/?(about|contact|company|legal|imprint|about-us|contact-us)\b", href, re.I):
            paths.append(href)

    pages: list[FetchResult] = []
    seen: set[str] = set()
    for p in _dedupe(paths)[:10]:
        res = ctx.get(p, ua="browser")
        key = res.final_url or res.url
        if key in seen:
            continue
        seen.add(key)
        if res.ok and res.status == 200:
            pages.append(res)

    # Also scan the homepage itself (footers often carry the entity + email).
    scan_pages = [home] + pages if home.ok else pages

    named: list[str] = []
    contact_bits: list[str] = []
    for res in scan_pages:
        text = _visible_text(res.text)
        m = _COMPANY_SUFFIX_RE.search(text)
        if m:
            named.append(m.group(0).strip()[:100])
        # Also accept an org name from JSON-LD Organization.
        for obj in _jsonld(res.text):
            if _is_org_ld(obj) and obj.get("name"):
                named.append(str(obj["name"])[:100])
        em = _EMAIL_RE.search(text)
        if em and not em.group(0).lower().startswith(("example@", "you@", "name@")):
            contact_bits.append(em.group(0))
        addr = _ADDRESS_RE.search(text)
        if addr:
            contact_bits.append(addr.group(0).strip()[:80])

    ev = {
        "identity_pages": [r.final_url or r.url for r in pages][:5],
        "company_names": _dedupe(named)[:3],
        "contact_signals": _dedupe(contact_bits)[:3],
    }

    if named or contact_bits:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="org-identity-present", remediation="", evidence=ev,
        )
    if pages:
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 2.0, max_points,
            finding="org-identity-thin",
            remediation="About/contact pages exist but name no real company entity "
            "or reachable contact; add a legal name and a contact email/address.",
            evidence=ev,
        )
    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-org-identity",
        remediation="Publish an about/contact page with a real company name and a "
        "reachable contact (email or address) so agents can verify legitimacy.",
        evidence=ev,
    )


def _is_org_ld(obj: dict) -> bool:
    t = obj.get("@type") or obj.get("type")
    types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
    return any(isinstance(x, str) and x.lower() in ("organization", "corporation", "localbusiness")
               for x in types)


# ---------------------------------------------------------------------------
# policies_present
# ---------------------------------------------------------------------------


def _policies_present(ctx: FetchContext, home: FetchResult) -> CheckResult:
    max_points, check_id = 3.0, "policies_present"

    footer = _footer_links(home)
    found: dict[str, str] = {}

    def _probe(kinds: dict[str, list[str]]):
        for kind, candidate_paths in kinds.items():
            if kind in found:
                continue
            # Footer link matching the kind wins first.
            for href in footer:
                if re.search(rf"/?({'|'.join(candidate_paths)})\b", href, re.I):
                    found[kind] = href
                    break
            if kind in found:
                continue
            for path in candidate_paths:
                res = ctx.get(f"/{path}", ua="browser")
                if res.ok and res.status == 200 and len((res.text or "").strip()) > 200:
                    found[kind] = res.final_url or res.url
                    break

    _probe({
        "terms": ["terms", "tos", "terms-of-service", "terms-and-conditions"],
        "privacy": ["privacy", "privacy-policy"],
        "refund": ["refund", "refunds", "refund-policy", "cancellation", "returns"],
    })

    ev = {"found": found, "footer_scanned": len(footer)}
    have = set(found.keys())

    if {"terms", "privacy", "refund"} <= have:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="policies-present", remediation="", evidence=ev,
        )
    if {"terms", "privacy"} <= have:
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 2.0, max_points,
            finding="no-refund-policy",
            remediation="Terms and privacy exist; add a refund/cancellation policy "
            "so agents know the reversal terms before purchasing.",
            evidence=ev,
        )
    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="policies-missing",
        remediation="Publish terms of service, a privacy policy, and a "
        "refund/cancellation policy (found: "
        f"{', '.join(sorted(have)) or 'none'}).",
        evidence=ev,
    )


# ---------------------------------------------------------------------------
# reputation_signals
# ---------------------------------------------------------------------------

_REVIEW_SITES = ("trustpilot.com", "g2.com", "producthunt.com", "capterra.com", "getapp.com")
_TESTIMONIAL_RE = re.compile(r"\b(testimonial|what our customers say|loved by|trusted by|customer stories|reviews?)\b", re.I)


def _reputation_signals(ctx: FetchContext, home: FetchResult) -> CheckResult:
    max_points, check_id = 3.0, "reputation_signals"

    if not home.ok:
        return CheckResult(
            check_id, PILLAR, Status.CANT_TEST, 0.0, max_points,
            finding="homepage-unreachable",
            remediation="Homepage could not be fetched to look for reputation "
            "signals; confirm the site is reachable.",
            evidence={"error": home.error},
        )

    html = home.text or ""
    # 1) AggregateRating / Review JSON-LD == strongest.
    for obj in _jsonld(html):
        if _has_rating_ld(obj):
            return CheckResult(
                check_id, PILLAR, Status.PASS, max_points, max_points,
                finding="reputation-signals-present", remediation="",
                evidence={"source": "jsonld", "snippet": json.dumps(obj)[:300]},
            )

    # 2) Links to credible third-party review sites.
    ext_links = [h for h in _all_links(home) if any(site in h.lower() for site in _REVIEW_SITES)]
    if ext_links:
        return CheckResult(
            check_id, PILLAR, Status.PASS, max_points, max_points,
            finding="reputation-signals-present", remediation="",
            evidence={"source": "third-party", "links": ext_links[:5]},
        )

    # 3) Testimonial section only == weak.
    text = _visible_text(html)
    if _TESTIMONIAL_RE.search(text):
        return CheckResult(
            check_id, PILLAR, Status.PARTIAL, 1.5, max_points,
            finding="self-reported-reputation-only",
            remediation="Only self-hosted testimonials were found; add "
            "AggregateRating markup or a credible third-party profile (G2, Trustpilot).",
            evidence={"match": (_TESTIMONIAL_RE.search(text).group(0))},
        )

    return CheckResult(
        check_id, PILLAR, Status.FAIL, 0.0, max_points,
        finding="no-reputation-signals",
        remediation="Add reputation signals — AggregateRating/Review schema.org "
        "markup or links to a credible third-party review profile.",
        evidence={},
    )


def _has_rating_ld(obj: dict) -> bool:
    types = obj.get("@type") or obj.get("type")
    types = [types] if isinstance(types, str) else (types if isinstance(types, list) else [])
    if any(isinstance(t, str) and t.lower() in ("aggregaterating", "review") for t in types):
        return True
    if isinstance(obj.get("aggregateRating"), dict):
        return True
    if isinstance(obj.get("review"), (dict, list)):
        return True
    return False


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

_SCRIPT_LD_RE = re.compile(
    r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)


def _jsonld(html: str) -> list[dict]:
    out: list[dict] = []
    for m in _SCRIPT_LD_RE.finditer(html or ""):
        raw = m.group(1).strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            continue
        out.extend(_flatten(data))
    return out


def _flatten(data) -> list[dict]:
    out: list[dict] = []
    if isinstance(data, list):
        for item in data:
            out.extend(_flatten(item))
    elif isinstance(data, dict):
        out.append(data)
        graph = data.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                out.extend(_flatten(item))
    return out


def _all_links(res: FetchResult) -> list[str]:
    out: list[str] = []
    base = res.final_url or res.url
    for m in _HREF_RE.finditer(res.text or ""):
        href = m.group(1).strip()
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        out.append(urljoin(base or "", href))
    return out


def _footer_links(res: FetchResult) -> list[str]:
    """All homepage links (footer links are the common home for these; scanning
    the whole page is a safe superset and keeps the heuristic simple)."""
    return _all_links(res)


def _visible_text(html: str) -> str:
    if not html:
        return ""
    no_script = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    return _TAG_RE.sub(" ", no_script)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it and it not in seen:
            seen.add(it)
            out.append(it)
    return out
