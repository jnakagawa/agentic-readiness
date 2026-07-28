"""Offering relevance discovery — classify what a storefront CLAIMS to sell.

The task battery scores a storefront across DIVERSE agent intents. Today that
intent list is FIXED: every site is probed with the same five tasks, so an
image-generation API gets judged on "order a physical good" and its partial
completion pollutes the completion means and both spread signals. That measures
the battery's MISMATCH with the site, not the site's readiness (operator
directive, 2026-07-23).

The fix makes the battery OFFERING-RELATIVE. This module is its foundational
brick: given a storefront's own agent-facing surfaces (homepage, ``llms.txt`` /
``llms-full.txt``, ``manifest.json``, its ``.well-known/ai-plugin.json`` agent
descriptor, and its OpenAPI / Swagger spec — the surface classes the operator
directive names, plus the agent-plugin manifest), decide which capability ARCHETYPES
the site claims to serve — a metered API call, a subscription, a digital good, a
physical good, a service booking, a data-retrieval job — each backed by QUOTED
machine evidence from the site's own text. A later brick instantiates the fixed
archetype TEMPLATE bank against the discovered offering (so task prompts are
parameterized by what the site actually sells) and marks UNCLAIMED archetypes NA
(excluded from completion means and both spreads — never penalized, never counted
as signal, same attribution-honesty invariant applied to tasks).

Design boundaries (loop invariants):
  - Discovery-only. This module adds NO check, weight, cap, or aggregation rule
    and does not feed the overall score or the battery math yet. It is a
    diagnostic surface (COVERAGE/METHOD), score-neutral by construction — the
    scoring-semantics change (NA-aware aggregation) is a later, peer-gated brick.
  - Vendor-neutral. Archetypes are named by CAPABILITY; signals are generic
    commerce/agent-surface language, never a vendor or domain string. Every
    claim carries the exact quoted evidence that triggered it, so a skeptic can
    audit whether the site really claims that archetype.
  - Precision over recall. A FALSE archetype claim would make the battery run an
    irrelevant intent — the very pollution we are removing — while a MISSED
    archetype only leaves a servable intent untested (conservative). So signals
    are anchored and specific: e.g. a metaphorical "every image you ship" must
    NOT read as physical fulfillment; only "free shipping" / "add to cart" /
    "in stock" style language does.
  - $0-only. Discovery is read-only GETs of public surfaces; it never POSTs,
    signs, or transacts.

Pure stdlib + dataclasses; unit-testable with synthetic surfaces, no network.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlparse

# The fixed archetype template bank (the operator directive's taxonomy). Order
# is the stable readout order; it is also the tie-break when two archetypes have
# equal signal strength.
ARCHETYPES: tuple[str, ...] = (
    "metered_api",
    "subscription",
    "digital_good",
    "physical_good",
    "service_booking",
    "data_retrieval",
)

# Agent-surface docs, in the order an agent reads them. The homepage is fetched
# separately (and HTML-stripped) by :func:`discover_offering`.
#
# The operator directive (2026-07-23) names the discovery surfaces explicitly:
# "llms.txt, manifest/catalog, OpenAPI, homepage". The natural-language docs
# (llms.txt / manifest) and the homepage were covered from brick 1; the machine
# API CONTRACT — an OpenAPI / Swagger spec — was added next. It is the surface an
# API-FIRST storefront is most likely to expose (a metered-API product may serve
# NO llms.txt or marketing homepage, only its spec), so without it such a site is
# classified from its homepage alone and can be mis-read as offering nothing. The
# spec's own path list, `servers` URLs, and operation summaries are exactly the
# vendor-neutral "qualified API" / "pay-per-*" / generated-media language the
# signal bank already anchors on, so it needs no new signals — only to be read.
#
# The AGENT-PLUGIN DESCRIPTOR (`/.well-known/ai-plugin.json`) is added here: the
# open, vendor-neutral manifest a storefront publishes to tell an AI agent what it
# is and how to use it. Unlike the OpenAPI spec (a terse machine CONTRACT — paths
# and operations), the descriptor carries a hand-written model-facing SUMMARY of
# the offering (`description_for_model` / `description_for_human`) in exactly the
# natural-language commerce/capability prose the signal bank anchors on. It is a
# distinct surface: a site may serve a rich descriptor even when its spec summaries
# are one-liners, so reading it improves recall for the "understand the offer"
# capability without any new signal. Same tolerance as every other doc — a 404 is
# simply an absent surface.
#
# The A2A (Agent2Agent) AGENT CARD (`/.well-known/agent.json`, and the newer
# `/.well-known/agent-card.json`) is added next: the open, vendor-neutral manifest
# an agent-native storefront publishes at a well-known URI so ANOTHER agent can
# discover what it does and how to reach it. It carries a top-level `description`
# plus a list of `skills`, each with its own name/description — a hand-written,
# model-facing account of the offering in the same natural-language capability prose
# the signal bank already anchors on (an image-generation agent's card says
# "generate an image", a data agent's says "enrich records against a dataset").
# As agent-to-agent commerce grows, a storefront may expose ONLY its agent card
# (no marketing homepage, no llms.txt, no OpenAPI spec) — the exact "classified from
# the homepage alone, mis-read as offering nothing" failure the OpenAPI/ai-plugin
# surfaces fixed, now for the agent-card surface. No new signal is needed, only for
# the surface to be read; a 404 is simply an absent surface as always.
#
# Well-known JSON conventions, most-specific first; a surface that 404s is simply
# absent (discovery tolerates a missing surface, same as any other doc).
_SURFACE_DOCS: tuple[str, ...] = (
    "/llms.txt",
    "/llms-full.txt",
    "/manifest.json",
    "/.well-known/ai-plugin.json",
    "/.well-known/agent.json",
    "/.well-known/agent-card.json",
    "/openapi.json",
    "/.well-known/openapi.json",
    "/swagger.json",
)

# Conventional agent/API DOC SUBDOMAINS. A real, common pattern for API-first
# storefronts is to serve their rich agent docs on a dedicated subdomain of their
# OWN registrable domain (agents. / docs. / developers. / api.) rather than the
# apex — e.g. a storefront whose apex is marketing prose but whose llms-full.txt /
# OpenAPI spec / billing docs live on ``agents.<domain>`` / ``api.<domain>``. Until
# now :func:`discover_offering` read ``_SURFACE_DOCS`` only on the storefront's apex
# host, so such a site was classified from its bare apex + on-apex ``/llms.txt``
# alone — a thin subset of what it actually publishes (the canonical driftflight.com
# serves its credit-billing agent docs at ``agents.driftflight.com/llms-full.txt``,
# never crawled). Discovery now ALSO tries ``_SURFACE_DOCS`` on a small allowlist of
# these conventional subdomains, so a site whose only rich self-description lives on
# a doc subdomain is no longer under-classified.
#
# PRECISION-FIRST / SSRF-safe: the subdomains are constructed HERE from the site's
# OWN resolved host, never from a ``url`` field in fetched page content (which could
# redirect discovery to an arbitrary third-party host). A subdomain that does not
# resolve or 404s is simply an absent surface — the same tolerance every other doc
# gets. Score-neutral: discovery is off the scoring path (``--battery auto`` only);
# adding surfaces can only reinforce archetypes the site already documents, and on
# the canonical pair the claimed SET is unchanged (guarded by
# tests/test_offering_canonical.py).
_DOC_SUBDOMAINS: tuple[str, ...] = ("agents", "docs", "developers", "api")

_F = re.IGNORECASE


# Signal bank: archetype -> [(label, pattern), ...]. Each pattern is anchored to
# high-precision, vendor-neutral language. A match records the archetype, the
# surface, the matched phrase (with a little surrounding context) and the label,
# so every claim is auditable evidence, not a bare boolean.
_SIGNALS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "metered_api": [
        # A documented programmatic call — the strongest machine evidence that an
        # agent can invoke this over HTTP.
        ("post-endpoint", re.compile(r"\b(POST|GET|PUT)\s+https?://\S+", _F)),
        ("qualified-api", re.compile(r"\b(text-to-image|HTTP|REST|GraphQL|web|image|inference)\s+API\b", _F)),
        ("api-reference", re.compile(r"\bAPI (reference|endpoint|over a\b)", _F)),
        # Usage-metered billing.
        ("pay-as-you-go", re.compile(r"\bpay[- ]?as[- ]?you[- ]?go\b", _F)),
        ("pay-per", re.compile(r"\bpay[- ]per[- ](call|request|use|token|unit|image|generation)\b", _F)),
        ("billed-per", re.compile(r"\bbilled per [a-z]+\b", _F)),
        ("per-unit-rate", re.compile(r"\bper[- ](generation|call|request|token|render|unit)\b", _F)),
        ("usage-based", re.compile(r"\b(usage[- ]based|metered|overage)\b", _F)),
        # Credit-based metering — the dominant billing convention for generative
        # and agent-native APIs (prepay a credit balance, spend N credits per
        # call/image/generation). PRECISION-CRITICAL: bare "\bcredits?\b" is a
        # false-positive minefield present in the very fixtures we validate on —
        # the C2PA metadata field ("credits": "C2PA content credentials"), a wallet
        # balance ("seller credit", camelCase "includedCreditUsd"), a refund
        # ("credited back in full"), feature-flag names ("credits-v2-jul-2026"),
        # and the ubiquitous payment instrument ("credit card"). So anchor to
        # billing CONTEXT: a credit followed by a metering word (per / plan /
        # balance / pack / based / ran out) or a verb that spends/buys it
        # (buy / purchase / prepay / redeem / spend credits). Real credit-billing
        # prose ("buy a credit plan", "your plan's credit ran out") matches; the
        # metadata/wallet/card noise does not.
        ("credit-metered", re.compile(
            r"\bcredits?\s+(?:per|remaining|left|pack|bundle|balance)\b"
            r"|\b(?:buy|buys|buying|purchas(?:e|es|ing)|prepay|prepaid|redeem|spend|top[- ]?up|out of|remaining|low on)\s+credits?\b"
            r"|\bcredit\s+(?:plan|plans|balance|pricing|bundle|pack)\b"
            r"|\bcredits?\s+(?:ran|runs?|running)\s+out\b"
            r"|\bapi\s+credits?\b"
            r"|\bcredit[- ]based\b", _F)),
        # Agent-native payment rail.
        ("x402", re.compile(r"\b(x402|HTTP\s*402)\b", _F)),
    ],
    "subscription": [
        ("subscription", re.compile(r"\bsubscription\b|\bsubscribe\b", _F)),
        ("per-month-price", re.compile(r"\$\s?\d[\d,.]*\s*(?:/|per)\s*month\b", _F)),
        ("per-month", re.compile(r"\bper month\b|\b/mo\b|\bmonthly\b", _F)),
        ("recurring", re.compile(r"\brecurring\b", _F)),
        ("annual-billing", re.compile(r"\bannual billing\b|\bbilling cycle\b", _F)),
    ],
    "digital_good": [
        ("generation", re.compile(r"\b(text-to-image|image|video|audio|art)\s+generation\b", _F)),
        ("generate-media", re.compile(r"\bgenerate(s|d)?\s+(an?\s+)?(image|video|audio|art)\b", _F)),
        ("generations", re.compile(r"\bgenerations?\b", _F)),
        ("render", re.compile(r"\brenders?\b|\brendering\b", _F)),
        ("translation", re.compile(r"\btranslat(e|es|ion|ing)\b", _F)),
        ("hosted-output", re.compile(r"\bhosted (output )?URLs?\b|\bimageUrls?\b|\bdownloadable\b", _F)),
    ],
    "physical_good": [
        # PRECISION-CRITICAL: bare "ship" is metaphorical on many agent-native
        # sites ("every image you ship"); require unambiguous fulfillment nouns.
        ("free-shipping", re.compile(r"\bfree shipping\b", _F)),
        ("shipping-noun", re.compile(r"\bshipping (address|cost|rates?|options?|method|fee|policy)\b", _F)),
        ("add-to-cart", re.compile(r"\badd to (cart|bag|basket)\b|\bshopping cart\b", _F)),
        ("stock", re.compile(r"\b(in|out of|back in) stock\b", _F)),
        ("fulfillment", re.compile(r"\bfulfil?lment\b|\bwarehouse\b|\bdelivery address\b|\bhome delivery\b|\btracking number\b", _F)),
        # SKU / inventory, RETAIL sense only. A bare "\bSKU\b" over-matched the
        # COMPUTE sense — an inference API's OpenAPI spec says "The SKU for the
        # hardware used to run the model" (a GPU/hardware SKU), and bare
        # "inventory" reads on a data/API product ("inventory API") — both would
        # falsely claim physical_good and run an irrelevant fulfillment intent
        # (the pollution this module removes). Anchor to unambiguous retail
        # phrasing instead (surfaced live on api.replicate.com, 2026-07-27); a
        # real shop trips add-to-cart / stock / shipping anyway, so the recall
        # loss on a bare token is immaterial.
        ("sku-inventory", re.compile(
            r"\b(product|item|per|each|retail)\s+SKUs?\b"
            r"|\bSKUs?\s+(number|code|count|list|catalog)\b"
            r"|\binventory\s+(count|levels?|on[- ]hand|management|status)\b"
            r"|\b(manage|track|update|check|low|remaining|out of)\s+inventory\b"
            r"|\bin[- ]stock\s+inventory\b", _F)),
        ("returns", re.compile(r"\breturns? (policy|&|and) (exchanges?|refunds?)\b|\breturn policy\b", _F)),
        ("physical-descriptor", re.compile(r"\bphysical (product|good|item)s?\b", _F)),
    ],
    "service_booking": [
        ("book", re.compile(r"\bbook (a|an|your|now|online)\b|\bbooking\b", _F)),
        ("appointment", re.compile(r"\bappointments?\b", _F)),
        ("reservation", re.compile(r"\breservations?\b|\breserve (a|an|your|now)\b", _F)),
        ("schedule", re.compile(r"\bschedule (a|an|your)\b", _F)),
        ("availability", re.compile(r"\bcheck availability\b|\bavailable (times|slots)\b|\btime slots?\b", _F)),
    ],
    "data_retrieval": [
        ("enrich", re.compile(r"\benrich(es|ed|ment)?\b", _F)),
        ("dataset", re.compile(r"\bdatasets?\b", _F)),
        ("lookup", re.compile(r"\blook ?ups?\b", _F)),
        ("data-service", re.compile(r"\bdata (feed|api|enrichment|records)\b|\brecords against\b", _F)),
        ("query-records", re.compile(r"\bquery (records|the database|a dataset)\b", _F)),
    ],
}


# ---------------------------------------------------------------------------
# result types
# ---------------------------------------------------------------------------
@dataclass
class ArchetypeSignal:
    """One matched piece of evidence for an archetype claim."""

    archetype: str
    surface: str  # which surface the evidence came from (homepage, /llms.txt, ...)
    label: str  # the signal that fired (for auditability)
    quote: str  # the matched phrase with a little surrounding context


@dataclass
class ArchetypeClaim:
    """An archetype the site claims to serve, with its supporting evidence."""

    archetype: str
    signals: list[ArchetypeSignal] = field(default_factory=list)

    @property
    def strength(self) -> int:
        """Number of DISTINCT signal labels that fired (not raw match count).

        Distinct labels, not raw hits, so a page that repeats "per month" ten
        times does not out-rank a page that names three different subscription
        signals once each.
        """
        return len({s.label for s in self.signals})


@dataclass
class OfferingProfile:
    """What a storefront claims to sell, from its own surfaces.

    ``claimed`` lists the archetypes with at least one signal, strongest first.
    ``unclaimed`` is the rest of the template bank — the archetypes a future
    offering-relative battery would mark NA for this site (never penalized).
    """

    domain: str
    claimed: list[ArchetypeClaim] = field(default_factory=list)
    surfaces_seen: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def archetypes(self) -> list[str]:
        return [c.archetype for c in self.claimed]

    @property
    def unclaimed(self) -> list[str]:
        served = set(self.archetypes)
        return [a for a in ARCHETYPES if a not in served]

    def claims(self, archetype: str) -> bool:
        return archetype in self.archetypes

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# classification (pure)
# ---------------------------------------------------------------------------
_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
_WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Reduce an HTML document to its visible prose for scanning.

    Drops script/style blocks then tags, collapses whitespace. A no-op on text
    that has no tags (llms.txt / plain manifests pass through unchanged).
    """
    if not text or "<" not in text:
        return (text or "").strip()
    stripped = _SCRIPT_STYLE_RE.sub(" ", text)
    stripped = _TAG_RE.sub(" ", stripped)
    return _WS_RE.sub(" ", stripped).strip()


def _quote(text: str, start: int, end: int, pad: int = 40) -> str:
    """A short, whitespace-normalized window around a match, for evidence."""
    window = text[max(0, start - pad): end + pad]
    return _WS_RE.sub(" ", window).strip()


def _scan_surface(surface: str, text: str) -> list[ArchetypeSignal]:
    """All archetype signals that fire in one surface's text."""
    signals: list[ArchetypeSignal] = []
    if not text:
        return signals
    for archetype, patterns in _SIGNALS.items():
        for label, pattern in patterns:
            m = pattern.search(text)
            if m is None:
                continue
            signals.append(
                ArchetypeSignal(
                    archetype=archetype,
                    surface=surface,
                    label=label,
                    quote=_quote(text, m.start(), m.end()),
                )
            )
    return signals


def classify_offering(domain: str, surfaces: dict[str, str]) -> OfferingProfile:
    """Classify claimed archetypes from a map of surface-name -> text.

    ``surfaces`` maps a surface label (e.g. ``"homepage"``, ``"/llms.txt"``) to
    its text; homepage HTML is stripped to prose here, so callers may pass raw
    HTML. Pure and deterministic: no network, no vendor names.
    """
    scanned: dict[str, list[ArchetypeSignal]] = {}
    seen: list[str] = []
    for surface, text in surfaces.items():
        prose = strip_html(text) if surface == "homepage" else (text or "")
        if not prose:
            continue
        seen.append(surface)
        for sig in _scan_surface(surface, prose):
            scanned.setdefault(sig.archetype, []).append(sig)

    claims: list[ArchetypeClaim] = [
        ArchetypeClaim(archetype=a, signals=scanned[a]) for a in ARCHETYPES if a in scanned
    ]
    # Strongest first (distinct-signal count), template-bank order as tie-break.
    claims.sort(key=lambda c: (-c.strength, ARCHETYPES.index(c.archetype)))

    profile = OfferingProfile(domain=domain, claimed=claims, surfaces_seen=seen)
    profile.evidence = {
        "claimed": [
            {
                "archetype": c.archetype,
                "strength": c.strength,
                "labels": sorted({s.label for s in c.signals}),
                "sample_quote": c.signals[0].quote if c.signals else "",
                "surfaces": sorted({s.surface for s in c.signals}),
            }
            for c in claims
        ],
        "unclaimed": profile.unclaimed,
        "surfaces_seen": seen,
    }
    return profile


# ---------------------------------------------------------------------------
# live discovery (network, $0 GETs only)
# ---------------------------------------------------------------------------
def _doc_subdomain_surfaces(base_url: str) -> list[tuple[str, str]]:
    """``(surface-label, absolute-url)`` pairs to try on conventional doc subdomains.

    For each prefix in :data:`_DOC_SUBDOMAINS` and each path in
    :data:`_SURFACE_DOCS`, build the absolute URL on a subdomain of the site's OWN
    resolved host (a leading ``www.`` is dropped so the subdomain attaches to the
    registrable host, and a host already ON one of these subdomains is not stacked
    onto itself — ``api.x.com`` does not spawn ``api.api.x.com``). The surface label
    is host-qualified (``agents.<host>/llms.txt``) so a subdomain surface is DISTINCT
    from — and never silently overwrites — an apex surface of the same path.

    Constructed purely from ``base_url``; never follows a URL taken from fetched
    page content, so discovery can only reach the storefront's own registrable
    domain (SSRF-safe). Returns ``[]`` for a hostless/dotless base (nothing to try).
    """
    parsed = urlparse(base_url or "")
    scheme = parsed.scheme or "https"
    host = parsed.netloc
    if not host or "." not in host:
        return []
    base_host = host[4:] if host.startswith("www.") else host
    first_label = base_host.split(".")[0]
    out: list[tuple[str, str]] = []
    for sub in _DOC_SUBDOMAINS:
        if first_label == sub:  # already on this subdomain — don't stack it
            continue
        sub_host = f"{sub}.{base_host}"
        for path in _SURFACE_DOCS:
            out.append((f"{sub_host}{path}", f"{scheme}://{sub_host}{path}"))
    return out


def discover_offering(ctx) -> OfferingProfile:
    """Fetch a storefront's surfaces and classify what it claims to sell.

    Reads the homepage plus the agent-surface docs (``llms.txt`` /
    ``llms-full.txt`` / ``manifest.json``), the agent-plugin descriptor
    (``.well-known/ai-plugin.json``), the A2A agent card
    (``.well-known/agent.json`` / ``.well-known/agent-card.json``), and the machine
    API contract (``openapi.json`` / ``.well-known/openapi.json`` / ``swagger.json``)
    via the shared :class:`FetchContext` — read-only, $0. Each surface doc is read
    on the storefront's apex host AND on a small allowlist of conventional doc
    SUBDOMAINS of the same registrable host (``agents.`` / ``docs.`` / ``developers.``
    / ``api.``), so a site whose rich agent docs live on a doc subdomain is not
    under-classified from its bare apex alone. Surfaces that 404 or error are simply
    absent (a site that only serves a homepage is classified from the homepage alone;
    a site that only serves an OpenAPI spec, a plugin descriptor, or an agent card is
    classified from it). Never raises: a fetch failure yields an empty surface, not
    an exception.
    """
    domain = getattr(ctx, "domain", "") or ""
    surfaces: dict[str, str] = {}

    try:
        home = ctx.homepage(ua="browser")
        if getattr(home, "is_success", False) and getattr(home, "text", ""):
            surfaces["homepage"] = home.text
    except Exception:
        pass

    for path in _SURFACE_DOCS:
        try:
            r = ctx.get(path, ua="browser")
        except Exception:
            continue
        if getattr(r, "is_success", False) and getattr(r, "text", "").strip():
            surfaces[path] = r.text

    # Also read the surface docs on conventional doc subdomains of the same
    # registrable host (agents. / docs. / developers. / api.). A subdomain that
    # does not resolve or 404s is simply absent — same tolerance as any apex doc.
    base_url = getattr(ctx, "base_url", "") or (f"https://{domain}" if domain else "")
    for label, url in _doc_subdomain_surfaces(base_url):
        try:
            r = ctx.get(url, ua="browser")
        except Exception:
            continue
        if getattr(r, "is_success", False) and getattr(r, "text", "").strip():
            surfaces[label] = r.text

    return classify_offering(domain, surfaces)
