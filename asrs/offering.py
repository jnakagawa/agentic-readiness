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

import html as _html
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
# The human/agent API-DOCS PAGE (`/docs`, and the conventional `/api-docs` /
# `/reference` variants) is added last: the rendered documentation page an
# API-first storefront most commonly exposes for a developer OR an agent to read
# its endpoints, examples, and — crucially — its RATE LIMITS / request quotas. That
# "understand the offer" prose (how fast/how often an agent may call, per-call
# billing, generated-media output) is exactly the vendor-neutral language the
# signal bank already anchors on, and on the canonical pair it lives on
# `/docs`, NOT on any well-known JSON doc (the `rate-limited` evidence is the
# `<h2 id="rate-limits">Rate limits</h2>` block on `driftflight.com/docs`). Unlike
# the JSON docs above, this surface is HTML — so :func:`classify_offering`
# HTML-STRIPS any HTML-document surface (not just the homepage) before scanning, or
# `<script>`/`<style>` decoy words ("out of stock", "shopping cart") on a real docs
# page would leak into evidence and false-positive an archetype. No new signal; a
# 404 is an absent surface as always. Score-neutral (off the scoring path); on the
# canonical pair the claimed SET and ORDER are unchanged — reading richer docs only
# reinforces already-claimed archetypes (guarded by tests/test_offering_canonical.py
# and tests/test_offering.py::test_docs_surface_is_read_live).
#
# The PRICING PAGE (`/pricing`) is added next: the rendered page where a storefront
# states HOW it charges — the "understand the offer" BILLING surface. It is the most
# conventional home for the per-month / per-generation / pay-as-you-go / seat-priced
# / credit-metered / volume-tier prose the signal bank already anchors on, and a site
# very commonly documents its billing ONLY there (a thin marketing homepage that
# links to `/pricing`, no billing detail in llms.txt or the OpenAPI spec). Like
# `/docs` it is HTML, so it is HTML-STRIPPED (via the same `_is_html_document` path)
# before scanning — else `<script>`/`<style>` retail decoy words on a pricing page
# would false-positive physical fulfillment. It reads through the SAME precision-
# guarded signal bank, so a pure-API pricing page trips only its metered/subscription
# billing signals (no spurious physical_good/service_booking), and a retail pricing
# page that says "free shipping" correctly claims physical_good. No new signal; a 404
# is an absent surface as always. Score-neutral, VERIFIED on committed evidence: on
# the canonical pair `/pricing` IS read (it is a real 200) and reinforces the three
# already-claimed archetypes — the claimed SET AND ORDER are unchanged (guarded by
# tests/test_offering_canonical.py and test_offering.py::test_pricing_surface_is_read_live,
# a non-vacuous read-live guard, not a vacuous 404-absent case).
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
    "/docs",
    "/api-docs",
    "/reference",
    "/pricing",
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
        # Programmatic AUTHENTICATION / credential provisioning — HOW an agent
        # obtains and presents credentials to CALL this API. The "provision without
        # a human" capability at the offering-understanding layer: an agent that
        # cannot read the auth scheme (an API key presented as a Bearer token, an
        # OAuth2 flow, an X-API-Key header, or a declared OpenAPI securityScheme)
        # cannot invoke the API at all, so a metered API that documents its auth is
        # MORE agent-completable. Distinct from `post-endpoint` (that an endpoint
        # EXISTS) and from the billing signals below (how you are CHARGED): this is
        # how you are ALLOWED to call. Vendor-neutral machine-integration vocabulary
        # (the HTTP Authorization header, an API key, OAuth2, an OpenAPI
        # securityScheme) — the same open-convention category as REST/GraphQL/OpenAPI
        # already in this bank, never a vendor.
        # PRECISION-CRITICAL: bare "authenticate" is a false-positive minefield —
        # ANY site with a user LOGIN ("authenticate your account" on a retail store)
        # would falsely claim a metered API and run an irrelevant intent (the exact
        # pollution this module removes). So "authenticate" must NAME an API
        # credential (authenticated WITH/VIA/USING an api key / bearer / token);
        # "Bearer" must be the `Authorization: Bearer` HTTP header or a "Bearer
        # token" (never "the bearer of ..."); "key" must be an "API key" / "X-API-Key"
        # (never a house key or a turnkey solution); and OAuth is anchored to the
        # versioned standard ("OAuth 2" / "OAuth2"). Non-vacuous on real committed
        # evidence: fires on BOTH canonical domains (`Authorization: Bearer` on the
        # homepage, "authenticated with an API key sent as a Bearer token" on /docs)
        # and on api.replicate.com's `"securitySchemes":{"bearerAuth":...}` — all
        # already-claimed metered_api sites, so it deepens evidence without changing
        # any claimed set (score-neutral).
        ("api-auth", re.compile(
            r"\bAuthorization\s*:\s*Bearer\b"
            r"|\bBearer\s+tokens?\b"
            r"|\bX-API-Key\b"
            r"|\bAPI[- ]keys?\b"
            r'|"securitySchemes"|\bbearer(?:Auth|Format)\b|"type"\s*:\s*"apiKey"'
            r"|\bauthenticat\w+\s+(?:with|via|using)\s+(?:an?\s+)?(?:api[- ]?key|bearer|api[- ]?token|access[- ]?token)\b"
            r"|\bOAuth\s?2(?:\.0)?\b", _F)),
        # Usage-metered billing.
        ("pay-as-you-go", re.compile(r"\bpay[- ]?as[- ]?you[- ]?go\b", _F)),
        ("pay-per", re.compile(r"\bpay[- ]per[- ](call|request|use|token|unit|image|generation)\b", _F)),
        ("billed-per", re.compile(r"\bbilled per [a-z]+\b", _F)),
        ("per-unit-rate", re.compile(r"\bper[- ](generation|call|request|token|render|unit)\b", _F)),
        ("usage-based", re.compile(r"\b(usage[- ]based|metered|overage)\b", _F)),
        # Documented RATE LIMITS / request quotas — a metered programmatic API
        # publishes how fast/how often an agent may call it (rate limits, requests
        # per minute, an API/request quota) so the agent can plan its usage. This
        # is the "understand the offer" capability for a metered API: it is a
        # defining feature of an agent-callable HTTP API, distinct from the BILLING
        # signals above (a site can document rate limits without naming a price).
        # PRECISION: bare "quota" is a false-positive minefield (disk/storage/free
        # quota, "no quota use"), so anchor the quota sense to an API prefix
        # (api/request/usage/monthly/daily/rate quota) or a metering suffix (quota
        # per/of/resets/remaining/exceeded); and "rate" must be adjacent to "limit"
        # so "flat rate pricing" / "unlimited" / "at a steady rate" never fire.
        ("rate-limited", re.compile(
            r"\brate[- ]?limit(?:s|ed|ing)?\b"
            r"|\brequests?\s+per\s+(?:second|minute|hour|day|month)\b"
            r"|\b\d+\s*(?:requests?|reqs?|calls?)\s*/\s*(?:s|sec|second|min|minute|hr|hour|day|month)\b"
            r"|\b(?:api|request|usage|monthly|daily|rate)\s+quota\b"
            r"|\bquota\s+(?:per|of|resets?|remaining|exceeded)\b", _F)),
        # Asynchronous long-running job — submit a request, then RETRIEVE the
        # result later via a webhook CALLBACK or by POLLING a status endpoint. This
        # is the defining contract of an agent-native API whose work does not finish
        # in the request/response round-trip (image/video generation, a training run,
        # a batch inference job). It is a "complete the job" capability distinct from
        # the BILLING signals above and from `rate-limited`: an agent that cannot read
        # this contract submits a job and never collects its output, so a metered API
        # that documents an async/webhook/poll flow is more agent-completable, not
        # less. Vendor-neutral machine-integration vocabulary (a webhook, an async
        # endpoint, polling a status URL) — the same category as REST/GraphQL/OpenAPI
        # already in this bank, never a vendor.
        # PRECISION: bare "poll" is a false-positive minefield (an opinion poll, a
        # polling place, a reader poll), so anchor the poll sense to an API object —
        # "poll ... endpoint" within a short same-line window, or "poll for/until"
        # (poll for the result / poll until complete); "async" must name an API noun
        # (async job / asynchronous prediction endpoint) so a bare "async is nice"
        # never fires; and "webhook" must be paired with an integration noun
        # (webhook url/endpoint/notification/callback) or an integration verb
        # (receive/send/deliver/register/configure/via a webhook) so a passing
        # "webhook-free" mention does not trip it.
        ("async-job", re.compile(
            r"\bwebhooks?\s+(?:url|endpoint|events?|notifications?|callbacks?|payload)\b"
            r"|\b(?:receiv\w+|send\w*|deliver\w*|register\w*|configur\w*|via|through|using)\s+(?:an?\s+)?webhooks?\b"
            r"|\bpoll(?:ing)?\s+(?:the\s+|for\s+|your\s+)?[^\n]{0,50}?\bendpoint\b"
            r"|\bpoll(?:ing)?\s+(?:for|until)\b"
            r"|\basync(?:hronous)?\s+(?:api|jobs?|requests?|predictions?|endpoint|calls?|inference|processing|tasks?|mode)\b", _F)),
        # WEBHOOK AUTHENTICITY VERIFICATION — whether an agent can TRUST that an
        # inbound async callback is GENUINELY from the API rather than a forged or
        # spoofed webhook. This is the security/TRUST leg of the async contract, and
        # it is the direct sibling of `async-job`: where `async-job` says a webhook
        # DELIVERY channel EXISTS (a webhook url/endpoint, register/configure a
        # webhook), NONE of the existing signals says whether the agent can
        # AUTHENTICATE what arrives on it. An autonomous agent that acts on an
        # UNVERIFIED "job complete" webhook can be tricked by a spoofed callback into
        # treating fabricated output as real — or, worse, releasing a payment — so a
        # metered API that documents webhook-signature verification (a webhook signing
        # secret to verify inbound requests, a webhook signature to check) lets the
        # agent TRUST the callback before acting on it, and is MORE agent-completable.
        # This dovetails with ASRS's own $0-only capital-safety ethos: don't act, and
        # never pay, on a forged callback. Distinct from every existing metered_api
        # signal — `async-job` is that a webhook/poll channel EXISTS, `api-auth` how
        # YOU present credentials OUTBOUND, `error-contract` how a failed call
        # recovers; NONE says how an agent verifies an INBOUND webhook is authentic.
        # Vendor-neutral webhook-security vocabulary (a webhook signing secret, a
        # webhook signature, an X-Webhook-Signature header, verifying that webhook
        # requests are authentic/signed) — the same open-convention category as
        # REST/GraphQL/OpenAPI already in this bank, never a vendor.
        # PRECISION-CRITICAL: bare "\bsignature\b" / "\bsigning secret\b" is a
        # false-positive minefield present in the very fixtures we validate on — the
        # canonical pair's marketing "your palette, your signature look", the x402
        # PAYMENT-proof "ZeroClick verifies the signature locally" (a settlement
        # signature, not a webhook), api.replicate.com's Files API SIGNED-URL "signing
        # secret" + `name: signature` query param (URL signing, not a webhook), and
        # generic "digital signature" / "sign the contract" senses. So NEVER match a
        # bare "signature"/"signing secret": require the token to name a WEBHOOK — a
        # `webhook signature` / `webhook-signature` (or `X-Webhook-Signature`) header,
        # a `signing secret for/of the ... webhook`, a `verify ... webhook`, or
        # `webhook requests/events/payloads are coming/authentic/signed/verified`. The
        # marketing-signature, x402-payment-signature, file-URL-signing-secret,
        # webhook-EXISTS-only (`async-job`'s turf), and contract/digital-signature
        # senses trip none of these. Fires non-vacuously on the real captured
        # api.replicate.com `/openapi.json` (the `/webhooks/default/secret` endpoint's
        # "Get the signing secret for the default webhook endpoint. This is used to
        # verify that webhook requests are coming from ...") and on ZERO of the
        # canonical-pair, retail (books.toscrape.com), or null (example.com) fixtures.
        # api.replicate.com ALREADY claims metered_api (its only archetype), so this
        # deepens its evidence without adding or reordering any archetype
        # (score-neutral); the classifier is off the scoring path.
        ("webhook-verification", re.compile(
            r"\bwebhook[- ]signatures?\b"
            r"|\bsigning\s+secret\s+(?:for|of)\s+(?:the\s+|a\s+|your\s+)?(?:default\s+)?webhooks?\b"
            r"|\bverif\w+\s+(?:that\s+)?(?:the\s+|these\s+|inbound\s+|each\s+)?webhooks?\b"
            r"|\bwebhooks?\s+(?:requests?|events?|payloads?|deliveries|calls?)\s+(?:are\s+)?(?:coming|authentic|genuine|signed|verified|valid)\b", _F)),
        # STREAMING response delivery — how an agent consumes output INCREMENTALLY
        # over the OPEN connection as it is produced (token-by-token generation,
        # progressive job output) rather than in one terminal round-trip. This is a
        # "complete the job" delivery-mode capability, and it is the IN-BAND sibling
        # of `async-job`: where `async-job` collects a completed long job's result
        # OUT of band (a webhook fires / the agent polls a status URL AFTER the
        # request returns), streaming delivers partial output WITHIN the same
        # request while the work is still running. An agent that cannot read the
        # streaming contract either blocks on a long call it could have consumed
        # progressively, or reads a `stream` URL it does not know how to open — so a
        # metered API that documents a streaming/SSE flow is MORE agent-completable.
        # Distinct from every existing metered_api signal: `api-auth` is how you
        # PRESENT credentials, `rate-limited` how fast you may call, `async-job` how
        # a completed job's result comes back OUT of band, `error-contract` how a
        # failed call recovers, `pagination` how a paged collection is walked,
        # `cancel-job` how a job is stopped; NONE says how output is delivered
        # incrementally over the live connection. Vendor-neutral open-standard
        # streaming vocabulary — the W3C Server-Sent Events standard, its
        # `text/event-stream` media type, a documented streaming API/endpoint that
        # streams the output/response/tokens as they are produced — the same
        # open-convention category as REST/GraphQL/OpenAPI/x402 already in this bank,
        # never a vendor.
        # PRECISION-CRITICAL: bare "\bstream\b"/"\bSSE\b" is a false-positive
        # minefield present in the very fixtures we validate on — the SSE ACRONYM
        # collides with the Shanghai Stock Exchange (SSE) and "sum of squared errors
        # (SSE)"; bare "stream" reads `application/octet-stream` (a binary-download
        # MIME type, NOT a streaming RESPONSE — present verbatim on
        # api.replicate.com's /openapi.json), a "live stream", the "bloodstream", a
        # "stream of consciousness", "downstream/upstream". A bare "SSE" would be
        # WORSE than noise here: it could CONJURE a false metered_api claim on a
        # stock-exchange page (the exact archetype-pollution this module removes). So
        # NEVER match a bare token: require the spelled-out `server-sent events`, the
        # `text/event-stream` media type, a `stream`/`streaming` VERB naming an output
        # noun (stream the output / streaming responses / stream tokens / streaming
        # generations), a `streaming` API/ENDPOINT/MODE, or the `SSE` acronym ONLY in
        # a streaming context (over/via/using/through SSE, an `SSE stream/endpoint/
        # connection/events`). The octet-stream MIME, the stock exchange, the squared
        # errors, and the live-stream/bloodstream/downstream senses trip none of these.
        # Fires non-vacuously on the real captured api.replicate.com /openapi.json (the
        # `stream` field's "receive streaming output using server-sent events (SSE)" +
        # "An event source to stream the output of the prediction") and on ZERO of the
        # canonical-pair, retail (books.toscrape.com), or null (example.com) fixtures.
        # api.replicate.com ALREADY claims metered_api (its only archetype), so this
        # deepens its evidence without adding or reordering any archetype
        # (score-neutral); the classifier is off the scoring path.
        ("streaming-response", re.compile(
            r"\bserver-sent events\b"
            r"|\btext/event-stream\b"
            r"|\bstream(?:s|ing)?\s+(?:the\s+|your\s+|its\s+)?(?:output|response|responses|result|results|tokens?|completions?|events?|generations?)\b"
            r"|\bstreaming\s+(?:api|endpoint|mode|responses?|outputs?)\b"
            r"|\b(?:over|via|using|through)\s+SSE\b"
            r"|\bSSE\s+(?:stream|streaming|endpoint|connection|events?)\b", _F)),
        # Documented ERROR CONTRACT — the machine-readable HTTP error responses an
        # agent must handle to RECOVER from a failed call: the 4xx/5xx status codes
        # and error identifiers the API returns when a request is rejected. This is
        # the "complete the job" RELIABILITY capability, distinct from `rate-limited`
        # (that limits EXIST) and `async-job` (how results come back): an agent that
        # cannot read the error contract cannot recover autonomously — it does not
        # know to refresh a credential on a 401, back off and retry on a 429, or
        # surface a clear failure on a 4xx/5xx — so a metered API that documents its
        # errors machine-readably is MORE agent-completable. Vendor-neutral open
        # conventions (an OpenAPI status-keyed response object, the IETF RFC 7807
        # `application/problem+json` problem-details media type, a documented status
        # code paired with a snake_case error code) — the same open-convention
        # category as REST/GraphQL/OpenAPI already in this bank, never a vendor.
        # PRECISION-CRITICAL: a bare 4xx/5xx number is a false-positive minefield — a
        # quantity ("a 500-image catalog run", "429 renders today"), a price ("$499"),
        # a phone/room number ("call 411", "room 404"). So NEVER match a bare number:
        # require it to be a JSON RESPONSE-OBJECT KEY (`"429":{"description"|"content"|
        # "$ref"`), the RFC 7807 media type, or a status code IMMEDIATELY followed by
        # a snake_case error identifier (`400 invalid_request`, `429 allowance_exhausted`,
        # `502 generation_failed`) — a quantity/price/phone number trips none. Only
        # ERROR statuses (4xx/5xx) count, never 2xx/3xx success/redirect codes. Fires
        # non-vacuously on ALL THREE metered_api fixtures (the canonical pair's /docs
        # error table + OpenAPI 401/429 responses, and api.replicate.com's
        # `application/problem+json` 4xx responses) and on ZERO of the retail/null
        # fixtures — the offering-layer mirror of the metered/non-metered split. Every
        # site where it fires ALREADY claims metered_api, so it deepens evidence
        # without changing any claimed set (score-neutral).
        ("error-contract", re.compile(
            r'"(?:4\d\d|5\d\d)"\s*:\s*\{\s*"(?:description|content|\$ref)"'
            r"|application/problem\+json"
            r"|\b(?:4\d\d|5\d\d)\s+[a-z][a-z0-9]*_[a-z0-9_]+\b", _F)),
        # A TEST / SANDBOX mode — a non-production facility where an agent can
        # validate its integration and DRY-RUN a call WITHOUT spending real money,
        # consuming quota, or producing a billable/usable output. This is the
        # "provision + complete the job SAFELY, without a human" capability at the
        # offering-understanding layer, and it dovetails with ASRS's own $0-only
        # ethos: an agent that can obtain a test/sandbox credential (a `..._test_`
        # key, a "sandbox environment", "test mode") verifies the whole flow at zero
        # cost before it ever authorizes a real charge, so a metered API that offers
        # one is MORE agent-completable. Distinct from every existing metered_api
        # signal: `api-auth` is how you PRESENT credentials, `rate-limited` how fast
        # you may call, `async-job` how results come back, `error-contract` how you
        # recover — NONE says whether you can TRY the call safely first. Vendor-neutral
        # machine-integration vocabulary (a sandbox environment, a test-mode flag, a
        # test API key / test credentials, a dry-run, the widely-used `<prefix>_test_`
        # / `<prefix>_sandbox_` key convention) — the same open-convention category as
        # REST/GraphQL/OpenAPI already in this bank, never a vendor.
        # PRECISION-CRITICAL: bare "\bsandbox\b" / "\btest\b" is a false-positive
        # minefield present in the very fixtures we validate on — books.toscrape.com's
        # page TITLE literally reads "Books to Scrape - Sandbox" (a demo-site name, not
        # an API sandbox), and elsewhere the word means a sandboxed iframe (an HTML
        # security attribute), a child's sandbox, or a sandbox game; bare "test" reads
        # "test drive"/"test the waters"/a `unit_test_runner` filename. So NEVER match
        # bare "sandbox"/"test": require "sandbox" to name a testing facility
        # (sandbox mode/environment/api/endpoint/key/token/credentials/url/access),
        # "test" to name a MODE or a CREDENTIAL (test mode / test api key / test
        # credentials / test token), an explicit "dry run", or the API-KEY convention
        # (a short lowercased prefix + `_test_`/`_sandbox_` + a MASKED ellipsis stub
        # `...` or a digit-bearing key body, so `df_test_...` / `kv_test_a1b2c3…` fire
        # but `unit_test_runner` — no digit, no ellipsis — does not). Fires on BOTH
        # canonical domains (the /docs "Keys look like df_live_... (production) or
        # df_test_... (sandbox: watermarked output, no quota use)" credential
        # dichotomy) and on ZERO of the api/retail/null fixtures — both already claim
        # metered_api, so it deepens evidence without changing any claimed set
        # (score-neutral); books.toscrape's bare-"Sandbox" title is correctly dodged.
        ("test-mode", re.compile(
            r"\btest\s+mode\b"
            r"|\bsandbox\s+(?:mode|environment|env|api|endpoints?|keys?|tokens?|credentials?|url|access|testing)\b"
            r"|\btest\s+(?:api\s+keys?|credentials?|tokens?)\b"
            r"|\bdry[- ]?run\b"
            r"|\b[a-z]{2,6}_(?:test|sandbox)_(?:\.{3}|[A-Za-z0-9]*\d[A-Za-z0-9]{2,})", _F)),
        # Cursor / collection PAGINATION — how an agent retrieves a MULTI-PAGE
        # result set: a list endpoint returns one page plus a cursor / a `next`
        # (and `previous`) page URL the agent follows to collect the rest. This is
        # the "complete the job" capability for a metered API that returns a
        # COLLECTION (list your predictions / models / deployments / records): an
        # agent that cannot follow the pagination cursor reads only the first page
        # and silently UNDER-completes the retrieval, so a metered API that
        # documents its pagination contract is MORE agent-completable. Distinct from
        # every existing metered_api signal — `async-job` is how ONE long job's
        # result comes back (webhook/poll), `error-contract` how a failed call
        # recovers, `rate-limited` how fast you may call; NONE says how an agent
        # walks a paged COLLECTION to completion. Vendor-neutral open REST
        # conventions (a cursor query parameter, a `next`/`previous` page URL, a
        # paginated collection response) — the same open-convention category as
        # REST/GraphQL/OpenAPI already in this bank, never a vendor.
        # PRECISION-CRITICAL: bare "cursor"/"next"/"previous"/"page" is a
        # false-positive minefield present in the very fixtures we validate on — a
        # RETAIL catalog paginates its HTML with `<li class="next"><a>next</a></li>`
        # (books.toscrape.com), the canonical homepages say "your next campaign" and
        # carry a JS `previousSibling`, and elsewhere the word is a CSS `cursor:
        # pointer`, a database cursor, or "the next page of the novel". So NEVER
        # match a bare token: require a cursor QUERY PARAMETER (`?cursor=`/`&cursor=`
        # with a value), an explicit "cursor-based pagination", a `pagination` /
        # `paginated` immediately qualifying a collection/response/list noun, or a
        # `next`/`previous` PAGE OF an API collection noun (page of collection /
        # results / records / items / objects). The retail "next" link, the marketing
        # "next campaign", the DOM `previousSibling`, the CSS/SQL cursor, and "next
        # page of the novel" trip none of these. Fires non-vacuously on the real
        # captured api.replicate.com surfaces (the `?cursor=…` list URL, the "next
        # page of collection objects" `paginated` response schema) and on ZERO of the
        # canonical-pair / retail / null fixtures. api.replicate.com ALREADY claims
        # metered_api (its only archetype), so this deepens its evidence without
        # adding or reordering any archetype (score-neutral); the classifier is off
        # the scoring path.
        ("pagination", re.compile(
            r"[?&]cursor=[A-Za-z0-9%._-]{4,}"
            r"|\bcursor[- ]based\s+paginat\w*"
            r"|\bpaginat(?:ion|ed)[_\s]+(?:object|collection|response|results?|list|endpoint)"
            r"|\b(?:next|previous)\s+page\s+of\s+(?:collection|results?|records?|items?|objects?|data|entries)\b", _F)),
        # Job CANCELLATION — how an agent ABORTS a long-running job it already
        # submitted: a cancel endpoint on the job resource, a deadline header that
        # auto-cancels after a bound, or a documented `canceled` terminal state. This
        # is the "complete the job" CONTROL + capital-safety leg of an agent-native
        # API whose work does not finish in the request/response round-trip (image /
        # video generation, a training run, a batch inference job): an agent that
        # detects a runaway or wrong generation and CANNOT cancel it keeps paying for
        # compute it no longer needs, so a metered API that documents a cancel
        # contract lets the agent BOUND its own spend — the same $0-only capital-safety
        # ethos ASRS itself holds — and is MORE agent-completable. Distinct from every
        # existing metered_api signal: `async-job` is how ONE long job's result comes
        # BACK (webhook/poll), `error-contract` how a FAILED call recovers,
        # `rate-limited` how fast you may call, `pagination` how a paged collection is
        # walked; NONE says how an agent STOPS a job it started. Vendor-neutral open
        # REST conventions (a `.../cancel` endpoint on a job resource, a `Cancel-After`
        # deadline header, a `canceled` job state) — the same open-convention category
        # as REST/GraphQL/OpenAPI already in this bank, never a vendor.
        # PRECISION-CRITICAL: bare "cancel" is a false-positive minefield — "cancel
        # your subscription" / "cancel anytime" (a subscription, NOT a job), "cancel
        # your order" (retail), "cancellation policy" / "cancel your booking" (a
        # service booking), "we canceled the flight", "cancel culture". So NEVER match
        # a bare "cancel": require the `Cancel-After` deadline header, a `cancel` VERB
        # naming an async-JOB noun (cancel the/a/your ... prediction / job / run / task
        # / request / training / inference / operation / generation / batch / workflow),
        # or a `.../cancel` ENDPOINT PATH on a job resource
        # (`predictions/{id}/cancel`). "cancel your subscription/order/booking",
        # "cancellation policy", and "cancel the flight" trip none of these. Fires
        # non-vacuously on the real captured api.replicate.com `/openapi.json` (the
        # `Cancel-After` header + the `predictions/{id}/cancel` endpoint + the
        # `canceled` prediction state) and on ZERO of the canonical-pair (whose
        # `/cancellation` surface is a subscription cancel with no job vocabulary),
        # retail, or null fixtures. api.replicate.com ALREADY claims metered_api (its
        # only archetype), so this deepens its evidence without adding or reordering
        # any archetype (score-neutral); the classifier is off the scoring path.
        ("cancel-job", re.compile(
            r"\bCancel-After\b"
            r"|\bcancel(?:s|ing|led|ed)?\s+(?:(?:the|a|an|your|this|in-progress|running|pending|queued|current)\s+)*(?:prediction|job|run|task|request|training|inference|operation|generation|batch|workflow)s?\b"
            r"|\b(?:prediction|job|run|task|training|inference|operation)s?/[^\s\"']*?/cancel\b", _F)),
        # AGENT SELF-PROVISIONING — whether an autonomous agent can OBTAIN access to
        # the API WITHOUT a human in the loop: no signup, no human account creation,
        # the agent provisions its OWN identity. This is the "provision without a
        # human" capability the PLAYBOOK's capability lens names explicitly, and it is
        # currently UNCAPTURED by the bank. It is the load-bearing precondition for
        # every other metered_api leg: an API whose credentials can only be issued by
        # a human who signs up on a dashboard is NOT agent-completable end-to-end, no
        # matter how cleanly it documents its auth scheme, rate limits, or errors — a
        # human must first onboard. So a metered API that lets an agent self-provision
        # (no signup / no API key / provision its own identity) is MORE agent-
        # completable. Distinct from every existing metered_api signal: `api-auth` is
        # how you PRESENT credentials you ALREADY hold; `test-mode` is whether you can
        # TRY the call safely; NONE says whether a HUMAN must onboard you to get
        # credentials at all. Vendor-neutral agent-onboarding vocabulary (no signup /
        # no human account creation / an agent provisions its own identity /
        # self-provision), never a vendor.
        # PRECISION-CRITICAL: this signal must capture only the AFFIRMATIVE agentic
        # self-provisioning capability and NEVER the OPPOSITE human-onboarding
        # phrasing present verbatim in the very fixtures we validate on — BOTH
        # canonical domains carry "Human developers sign up on the dashboard for an
        # API key" (a human-gated onboarding, the exact inverse of the capability),
        # and drift-flight.org's /docs 401 row reads "No API key, or the key is
        # unknown or revoked" (an error message, not a no-key capability). A naive
        # "\bsign up\b" would misread the human path as self-provisioning; a bare "no
        # API key" would misread the 401 error. So NEVER match a bare "sign up" or a
        # bare "no API key": require the NEGATED onboarding ("no signup" / "no
        # sign-up", NOT the pricing sense "no signup fees/costs/charges"), an agent
        # PROVISIONING ITS OWN IDENTITY, an explicit "self-provision", or a "no
        # human"/"without a human" signup/account/onboarding/provisioning phrase. The
        # "Human developers sign up" path, the 401 "No API key" error, "no signup
        # fees", and a "sign up for our newsletter" prompt trip none of these. Fires
        # non-vacuously on driftflight.com (the apex "free trial, no signup" heading
        # and the agents.driftflight.com agent docs "There is no signup and no API
        # key … an autonomous agent can provision its own identity") and is correctly
        # ABSENT on drift-flight.org (whose ONLY signup phrasing is the human-gated
        # dashboard path) — the discovery-layer echo of the real capability gap. Both
        # already claim metered_api via other signals, so this deepens driftflight.com's
        # evidence without adding or reordering any archetype (score-neutral); it fires
        # on ZERO of the api.replicate.com (API-key required), retail
        # (books.toscrape.com), or null (example.com) fixtures, so it can never CONJURE
        # a metered_api claim on a site that does not already make one.
        ("self-provisioning", re.compile(
            r"\bno\s+sign[- ]?up(?!\s+(?:fees?|costs?|charges?))\b"
            r"|\bprovision\w*\s+(?:its|their|your|an?)\s+own\s+identit\w+"
            r"|\bself[- ]provision\w*"
            r"|\b(?:no\s+human|without\s+(?:a\s+)?human)\s+(?:sign[- ]?up|signup|account|onboarding|provisioning)\b", _F)),
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
        # Committed-use / tiered-volume billing — usage-metered pricing that scales
        # with committed or cumulative volume (a committed-use discount, a volume /
        # usage tier, a per-tier price). A defining convention for a metered API's
        # billing, distinct from the flat per-call rate above: a metered storefront
        # that meters by volume tier ("never counted against volume tiers") documents
        # its offer this way, and until now that prose was invisible to discovery.
        # PRECISION: anchor "volume"/"tier" to a pricing word so "volume control" /
        # "tier 1 support" / "top tier" never fire, and require "committed use" to be
        # adjacent (not "committed to use").
        ("tiered-volume", re.compile(
            r"\bcommitted[- ]use\b"
            r"|\bvolume\s+(?:discount|pricing|tiers?|based|commitment)\b"
            r"|\btiered\s+(?:pricing|rates?|billing|usage)\b"
            r"|\busage\s+tiers?\b"
            r"|\bpricing\s+tiers?\b"
            r"|\btier\s+\d+\s*[:\-–]\s*\$", _F)),
        # Agent-native payment rail.
        ("x402", re.compile(r"\b(x402|HTTP\s*402)\b", _F)),
        # Agent-native payment rail, BEYOND the lone x402 above. Agentic commerce
        # is standardizing on SEVERAL open, vendor-neutral payment/settlement
        # protocols an agent can drive programmatically — x402, MPP, ACP, UCP, AP2 —
        # and a storefront may advertise more than one ("payment methods today are
        # x402 (Base USDC) and MPP (Tempo USDC)") or declare them structurally in a
        # manifest (`"paymentProtocols":[{"protocol":"x402",...},{"protocol":"mpp",
        # ...}]`). Recognising only x402 under-classified a site's agent-native
        # payment capability to a single rail; this signal captures the "many rails"
        # axis (north star) as one more piece of machine evidence that an agent can
        # PAY here without a human. Like `x402`, these are PROTOCOL/standard names
        # (not vendors) — the same category as REST/GraphQL/OpenAPI already in this
        # bank. PRECISION-CRITICAL: MPP/ACP/UCP/AP2 are 3-4 char acronyms that collide
        # with unrelated senses (a Member of Parliament, an inflation index, a medical
        # guideline). So do NOT match a bare acronym — anchor to one of two
        # high-precision forms: a STRUCTURED `"protocol":"<rail>"` declaration in a
        # manifest/descriptor, or a rail name paired with its on-chain SETTLEMENT
        # asset in a `(… USDC/USDT/stablecoin …)` parenthetical. Both are unambiguous
        # agent-payment machine evidence; the collision senses trip neither.
        ("agent-payment-rail", re.compile(
            r'"protocol"\s*:\s*"(?:x402|mpp|acp|ucp|ap2)"'
            r"|\b(?:x402|mpp|acp|ucp|ap2)\b\s*\([^)]*\b(?:usdc|usdt|stablecoin)\b[^)]*\)", _F)),
        # PAYMENT RECEIPT / spend reconciliation — the machine-readable PROOF-OF-
        # PAYMENT an agent gets BACK after a paid call and logs to RECONCILE its own
        # spend: a receipt header on the successful paid response, a payment /
        # settlement receipt, a spend record it keeps. This is the ACCOUNTING leg of
        # an agent-native metered API and the capital-safety COUNTERPART to the
        # payment RAILS above — `x402` / `agent-payment-rail` say the agent can PAY;
        # NONE says the agent gets a verifiable RECEIPT back to account for what it
        # paid. An autonomous agent that pays per call but cannot obtain a
        # machine-readable receipt cannot reconcile its own spend — it has no
        # per-call proof to log against a budget, dispute a wrong charge, or
        # reconcile an invoice — so a metered API that returns a payment receipt /
        # spend record is MORE agent-completable, and it dovetails directly with
        # ASRS's own $0-only capital-safety ethos: track every unit of spend.
        # Distinct from every existing metered_api signal: `x402`/`agent-payment-rail`
        # are how you PAY, `credit-metered`/`tiered-volume`/`pay-per` how you are
        # PRICED, `test-mode` how you avoid paying while testing, `webhook-verification`
        # how you trust an INBOUND callback; NONE says what proof-of-payment comes
        # BACK on a paid response. Vendor-neutral payment-accounting vocabulary (a
        # receipt header on the paid response, a payment / settlement receipt, a
        # serialized receipt, a spend record, proof of payment) — the same open-
        # convention category as REST/GraphQL/OpenAPI/x402 already in this bank,
        # never a vendor.
        # PRECISION-CRITICAL: bare "\breceipt\b" is a false-positive minefield — an
        # EMAIL receipt / a READ receipt ("enable read receipts"), an ORDER receipt on
        # a retail checkout, "in receipt of your message", a warehouse "receipt of
        # goods". So NEVER match a bare "receipt": require a `receipt header`, a
        # `payment`/`settlement` receipt, a `serialized receipt`, a `spend record`, an
        # explicit `proof of payment`, or a receipt the agent can LOG. The email/read/
        # order/goods-receipt senses trip none of these. Fires non-vacuously on the
        # real captured driftflight.com agent docs (agents.driftflight.com/
        # llms-full.txt — "Every successful paid response includes a receipt header you
        # can log for your spend records: `payment-response` … or `payment-receipt`
        # (MPP, serialized receipt)") and on ZERO of the drift-flight.org (which carries
        # NO receipt/spend-record prose — the discovery-layer echo of the real
        # capability gap, mirroring `self-provisioning`), api.replicate.com, retail
        # (books.toscrape.com), or null (example.com) fixtures. driftflight.com ALREADY
        # claims metered_api (its strongest archetype), so this deepens its evidence
        # without adding or reordering any archetype (score-neutral); the classifier is
        # off the scoring path.
        ("payment-receipt", re.compile(
            r"\breceipt\s+headers?\b"
            r"|\b(?:payment|settlement)[- ]receipts?\b"
            r"|\bserialized\s+receipts?\b"
            r"|\bspend\s+records?\b"
            r"|\bproof\s+of\s+payment\b"
            r"|\breceipts?\s+(?:that\s+|which\s+)?(?:an?\s+agent\s+|you\s+)?(?:can\s+)?log\b", _F)),
        # FAILURE NOT BILLED — whether a metered call that FAILS (the render did not
        # complete, the job errored, the request timed out) is NOT charged. This is a
        # capital-safety leg the PLAYBOOK's lens names directly: an autonomous agent
        # paying per call must know that a FAILED unit does not silently burn money,
        # or it cannot bound its spend against a flaky endpoint — the risk of being
        # billed for work it never received. It is DISTINCT from every existing
        # metered_api signal: `error-contract` names the machine-readable error FORMAT
        # (how a failure is REPORTED), `payment-receipt` is the proof of a SUCCESSFUL
        # charge, `test-mode` is a $0 SANDBOX (not the priced path), `usage-based`/
        # `billed-per`/`per-unit-rate`/`credit-metered` describe how you are charged
        # ON SUCCESS — NONE says whether a FAILURE costs money. It is the metered
        # sibling of digital_good's `output-retention` (both are "complete the job"
        # legs): retention is HOW LONG a successful output lives, failure-not-billed is
        # whether an UNSUCCESSFUL one is free.
        # PRECISION-CRITICAL: bare "not charged"/"not billed" is a false-positive
        # minefield — "your card is not charged until the trial ends" / "you are not
        # charged during the free trial" is a SUBSCRIPTION $0-eval promise, not a
        # failure guarantee — so NEVER match a bare not-charged: require a FAILURE
        # token (fail/failed/failure/errored/did-not-complete/incomplete/unsuccessful/
        # timed-out) within a short, sentence-bounded window of "(not|never) (charged|
        # billed)" (either order), OR an explicit "only (charged|billed) for
        # successful/completed". The trial promises (no failure word), `error-contract`
        # prose ("on failure the body is application/problem+json" — a failure word but
        # no not-charged), and generic "no charge to get started" trip none of these.
        # Fires non-vacuously on BOTH canonical /docs ("The render did not complete;
        # you are not charged a generation") — both ALREADY claim metered_api, so this
        # only DEEPENS the claim without adding or reordering an archetype
        # (score-neutral) — and on ZERO of the metered-api-only (api.replicate.com),
        # retail (books.toscrape.com), or null (example.com) fixtures. Off the scoring
        # path.
        ("failure-not-billed", re.compile(
            r"\b(?:fail(?:s|ed|ure)?|errored|did not complete|does not complete"
            r"|didn.t complete|incomplete|unsuccessful|time(?:s|d)? out)\b"
            r"[^.<>]{0,60}?\b(?:not|never|aren.?t|isn.?t)\s+(?:be\s+)?(?:charged|billed)\b"
            r"|\b(?:not|never|aren.?t|isn.?t)\s+(?:be\s+)?(?:charged|billed)\b"
            r"[^.<>]{0,60}?\b(?:fail(?:s|ed|ure)?|errored|did not complete|does not complete"
            r"|didn.t complete|incomplete|unsuccessful|time(?:s|d)? out)\b"
            r"|\bonly\s+(?:charged|billed)\s+(?:for\s+)?(?:successful|completed)\b", _F)),
        # RESERVE-AND-SETTLE — whether an agent can CAP its per-call exposure up
        # front: reserve a spend CEILING before the call, then be charged only the
        # ACTUAL usage, the unused remainder refunded. This is a capital-safety leg
        # the PLAYBOOK's lens names directly — an autonomous per-call buyer that can
        # bound its WORST-CASE cost per request (reserve a ceiling, pay actual)
        # controls its exposure against a variable-priced endpoint the way a human
        # sets a credit-card hold; it never overpays for a call that turned out
        # cheaper than the ceiling. It is DISTINCT from every existing metered_api
        # signal: `x402`/`agent-payment-rail` say the agent CAN pay (which rails
        # exist), `payment-receipt` is the proof of a SUCCESSFUL charge (the
        # accounting AFTER), `failure-not-billed` is whether a FAILED call is free,
        # `credit-metered`/`pay-per`/`usage-based`/`tiered-volume` are how you are
        # PRICED on success — NONE says the agent can BOUND a single call's maximum
        # cost before making it and be refunded the difference. It is the metered
        # capital-safety sibling of `failure-not-billed`: that one bounds the cost of
        # a FAILURE, this one bounds the cost of a SUCCESS.
        # Vendor-neutral reserve-and-settle vocabulary — reserving a spend ceiling,
        # a reserve-and-pay-actual rail, being charged only actual against a reserved
        # ceiling, an escrow/channel that refunds the unused remainder — the same
        # open-convention category as REST/GraphQL/OpenAPI/x402 already in this bank,
        # never a vendor (the drift docs' MPP/USDC nouns are not required to match).
        # PRECISION-CRITICAL: bare "reserve"/"refund"/"ceiling"/"escrow" is a
        # false-positive minefield — a hotel "reservation", "we reserve the right",
        # a retail "full refund within 30 days", cloud "reserved capacity", a
        # "ceiling fan". So NEVER match a bare token: require the NAMED
        # reserve-and-pay-actual rail, an explicit "reserve(s) the ceiling" (a SPEND
        # ceiling, not a generic reservation), "charged only actual" ANCHORED to a
        # reserve/ceiling/up-front context, or an escrow/channel/reserve that
        # "refunds the (rest|difference|remainder|unused|balance)". The
        # reservation/refund-policy/reserved-capacity senses trip none of these.
        # Fires non-vacuously on the real captured driftflight.com agent docs
        # (agents.driftflight.com/llms.txt + llms-full.txt — "your wallet reserves
        # the ceiling up front, then you are charged only actual … the escrow refunds
        # the rest") and on ZERO of the drift-flight.org (which carries NO
        # reserve-and-settle prose — the discovery-layer echo of the real capability
        # gap, mirroring `payment-receipt`/`self-provisioning`), api.replicate.com,
        # retail (books.toscrape.com), or null (example.com) fixtures. driftflight.com
        # ALREADY claims metered_api (its strongest archetype), so this deepens its
        # evidence without adding or reordering any archetype (score-neutral); the
        # classifier is off the scoring path.
        ("reserve-and-settle", re.compile(
            r"\breserve[- ]and[- ]pay[- ]actual\b"
            r"|\breserves?\s+(?:the\s+|a\s+|your\s+)?ceiling\b"
            r"|\b(?:reserv\w+|ceiling|up[- ]front)\b[^.<>]{0,80}?"
            r"\bcharged\s+only\s+(?:for\s+|the\s+)?actual\b"
            r"|\bcharged\s+only\s+(?:for\s+|the\s+)?actual\b"
            r"[^.<>]{0,80}?\b(?:reserv\w+|ceiling|up[- ]front)\b"
            r"|\b(?:escrow|channel|reserv\w+)\b[^.<>]{0,80}?"
            r"\brefunds?\s+(?:the\s+)?(?:rest|difference|remainder|unused|balance)\b", _F)),
        # FREE-INCLUDED-USAGE — whether an agent can complete a REAL metered call at
        # $0 before committing any money: a per-account free ALLOWANCE of actual
        # metered units (an `includedUnits` contract), usable with a zero balance and
        # no funding and no human signup. This is the metered_api ON-RAMP the
        # PLAYBOOK's lens names directly (reach → understand → PAY → provision →
        # complete): an autonomous buyer can prove the API works end-to-end for free
        # before it ever funds a wallet, which is exactly the barrier an agent must
        # clear to adopt a paid API — and it dovetails with ASRS's own $0-only ethos
        # (the free allowance is precisely the $0 path the benchmark itself exercises).
        # It is DISTINCT from every existing signal: the subscription `free-trial` is
        # a time-boxed evaluation of a RECURRING plan (this is per-CALL free units on
        # a pay-as-you-go meter, not a trial window); `test-mode` is a SANDBOX/fake
        # environment (this is REAL production units served free, not a test key);
        # `self-provisioning` is getting IDENTITY/access without a human (WHO you are,
        # the free identity handshake) — NONE says the agent can run a real, billable
        # unit of work at zero cost before funding. It is the metered mirror of the
        # subscription `free-trial`: try the recurring OFFER free there, try the
        # metered CALL free here.
        # PRECISION-CRITICAL: bare "free" is a false-positive minefield — free
        # shipping, a free trial, royalty-free, toll-free, "feel free", free parking,
        # free WiFi, "free to cancel". So NEVER match a bare "free": require a free
        # USAGE/ALLOWANCE, free UNITS PER a billing period/account, an `includedUnits`
        # allowance NAMED as free (either order, within a clause), or an explicit
        # try/test/call/use-it BEFORE any money/funding/paying — the shipping/trial/
        # licence/parking senses trip none of these. Fires non-vacuously on the real
        # captured driftflight.com agent docs (agents.driftflight.com/llms.txt +
        # llms-full.txt + manifest.json — "Free allowance - try it before any payment",
        # "`includedUnits` - free usage per account that needs no funding", "a freshly
        # provisioned identity with a zero balance qualifies, so an agent can try this
        # API end to end before any money is involved") and on ZERO of drift-flight.org
        # (which carries NO free-allowance prose — the discovery-layer echo of the real
        # capability gap, mirroring `payment-receipt`/`reserve-and-settle`),
        # api.replicate.com, retail (books.toscrape.com), or null (example.com)
        # fixtures. driftflight.com ALREADY claims metered_api (its strongest
        # archetype), so this deepens its evidence without adding or reordering any
        # archetype (score-neutral); the classifier is off the scoring path.
        ("free-included-usage", re.compile(
            r"\bfree\s+(?:included\s+)?(?:usage|allowance)\b"
            r"|\bfree\s+units?\s+per\s+(?:account|period|month|day|week|billing)\b"
            r"|\bincluded[- ]?units?\b[^.<>]{0,40}?\bfree\b"
            r"|\bfree\b[^.<>]{0,40}?\bincluded[- ]?units?\b"
            r"|\b(?:try|test|call|use)\b[^.<>]{0,60}?"
            r"\bbefore\s+(?:any\s+)?(?:money|funding|paying)\b", _F)),
    ],
    "subscription": [
        ("subscription", re.compile(r"\bsubscription\b|\bsubscribe\b", _F)),
        ("per-month-price", re.compile(r"\$\s?\d[\d,.]*\s*(?:/|per)\s*month\b", _F)),
        ("per-month", re.compile(r"\bper month\b|\b/mo\b|\bmonthly\b", _F)),
        ("recurring", re.compile(r"\brecurring\b", _F)),
        ("annual-billing", re.compile(r"\bannual billing\b|\bbilling cycle\b", _F)),
        # Seat / per-user licensing — the dominant SaaS-subscription billing
        # convention (a recurring price per user seat), distinct from the
        # per-month / annual signals above: a seat-priced plan may quote only a
        # per-SEAT rate ("$10 per seat", "per-seat pricing", "5 seats included")
        # and never say "month", so without this it is not recognised as a
        # subscription at all. PRECISION: "seat" is a false-positive minefield (a
        # window seat, a seat belt, "take a seat", "8 seats at the table"), so
        # anchor it to a pricing PERIOD, a PRICE, a per-USER basis, or an explicit
        # licensing word — a bare seat count near none of these never fires.
        ("seat-licensing", re.compile(
            r"\bper[- ]seat\s+(?:per\s+)?(?:month|year|user|licen[cs]e[ds]?)\b"
            r"|\bper\s+user\s+per\s+(?:month|year)\b"
            r"|\$\s?\d[\d,.]*\s*(?:/|per)\s*(?:seat|user)\b"
            r"|\bper[- ]seat\s+(?:pricing|plan|billing|subscription)\b"
            r"|\bseat[- ]based\s+(?:pricing|billing|subscription|licen[cs])"
            r"|\blicen[cs]e[ds]?\s+per[- ]seat\b"
            r"|\b\d+\s+seats?\s+(?:included|per\s+(?:month|year))\b", _F)),
        # A FREE TRIAL — a no-cost evaluation of the offering BEFORE any recurring
        # charge begins. This is the "understand + provision the offer SAFELY,
        # without a human" capability for the subscription archetype, and it
        # dovetails with ASRS's own $0-only ethos: an agent that can start a free
        # trial evaluates the whole subscription at zero cost before it ever commits
        # to recurring billing, so a subscription offer that documents one is MORE
        # agent-completable. It is the subscription-archetype MIRROR of the
        # metered_api `test-mode` signal (try the metered CALL safely at $0 first) —
        # here, try the recurring OFFER safely at $0 first — and is distinct from
        # every existing subscription signal, all of which describe how you are
        # CHARGED on an ACTIVE plan (`subscription`/`recurring` that a plan exists,
        # `per-month`/`per-month-price`/`annual-billing` the cadence, `seat-licensing`
        # the per-user basis); NONE says whether you can EVALUATE the plan at no cost
        # first. Vendor-neutral trial-offer vocabulary (a free trial, a trial period,
        # an N-day trial, a trial account/allowance/membership, "start your free
        # trial", "try it free for N days"), never a vendor.
        # PRECISION-CRITICAL: bare "\btrial\b" is a false-positive minefield — a
        # clinical trial, a court trial, "trial and error", "trial by fire", "on
        # trial". So NEVER match a bare "trial": require it to name a FREE trial
        # (`free trial` / `free-trial`), a trial PERIOD/ACCOUNT/ALLOWANCE/MEMBERSHIP,
        # an explicit N-DAY trial (`14-day free trial`), or a START/TRY-FREE offer
        # (`start your free trial`, `try it free for 14 days`) — the clinical/court/
        # error/fire senses trip none of these. Fires non-vacuously on driftflight.com
        # (the homepage / llms.txt / pricing "a free trial allowance, so an agent can
        # evaluate it before any payment") — which ALREADY claims subscription, so it
        # deepens evidence without changing any claimed set (score-neutral) — and on
        # ZERO of the metered-api-only (api.replicate.com), retail (books.toscrape.com),
        # null (example.com), or trial-free (drift-flight.org) fixtures, so it can
        # never CONJURE a subscription claim on a site that does not already make one.
        ("free-trial", re.compile(
            r"\bfree[- ]trials?\b"
            r"|\btrial\s+(?:period|account|allowance|membership)\b"
            r"|\b\d+[- ]days?\s+(?:free\s+)?trial\b"
            r"|\bstart\s+(?:a|your)\s+(?:free\s+)?trial\b"
            r"|\btry\s+(?:it\s+)?free\s+for\s+\d+\s+days?\b", _F)),
        # PROGRAMMATIC PLAN PURCHASE — whether an autonomous agent can BUY / commit
        # to a credit-or-subscription plan through an API CALL (a `POST /plans/{id}/
        # purchase` endpoint on the plan resource), rather than a human checkout on a
        # pricing page. This is the "pay programmatically + provision without a human"
        # capability the PLAYBOOK's lens names, applied to the SUBSCRIPTION archetype,
        # and it is currently UNCAPTURED. Every existing subscription signal describes
        # that a plan EXISTS (`subscription`/`recurring`) or how it is PRICED
        # (`per-month`/`per-month-price`/`annual-billing` the cadence, `seat-licensing`
        # the per-user basis) or that it can be EVALUATED at $0 first (`free-trial`);
        # NONE says whether the agent can autonomously COMMIT to the recurring plan.
        # A storefront whose subscription can only be started by a human clicking
        # through a checkout is NOT agent-completable at the commit step, no matter how
        # cleanly it documents its cadence — so a subscription offer that exposes a
        # programmatic plan-purchase endpoint (buy a credit / subscription plan, a
        # `purchase` object on a purchasable plan) is MORE agent-completable, and it
        # is the load-bearing "commit" leg of the north star's agent-native commerce.
        # It is the subscription-archetype counterpart to metered_api's
        # `self-provisioning` (obtain API access without a human): here, take on the
        # recurring commitment without a human.
        # PRECISION-CRITICAL: bare "plan"/"subscribe to a plan" is a false-positive
        # minefield present verbatim in the very fixtures we validate on — BOTH
        # canonical domains' /docs read "Create an account, subscribe to a plan on the
        # pricing page" (a HUMAN checkout, the exact inverse of the capability) and
        # drift-flight.org's OpenAPI reads "issued on the dashboard after subscribing
        # to a plan" (again human-gated); bare "subscription plans" is marketing that
        # `subscription` already covers. So NEVER match a bare "plan" or a "subscribe
        # to a plan" phrase: require the PROGRAMMATIC purchase — a `/plans/{id}/
        # purchase` ENDPOINT PATH, a `purchasable plan`, or a BUY/PURCHASE/ACTIVATE
        # verb naming a CREDIT-or-SUBSCRIPTION plan (`buy a credit or subscription
        # plan`). The human "subscribe to a plan on the pricing page", the dashboard
        # onboarding path, and the bare-"subscription plans" marketing trip none of
        # these. Fires non-vacuously on driftflight.com (the agents.driftflight.com
        # llms-full.txt "purchase once with `POST /plans/{planId}/purchase`", "buy a
        # credit or subscription plan", "Purchasable plans carry a `purchase` object")
        # and is correctly ABSENT on drift-flight.org (whose ONLY plan prose is the
        # human dashboard/pricing-page path) — the discovery-layer echo of the real
        # capability gap, mirroring `self-provisioning` / `payment-receipt`.
        # driftflight.com ALREADY claims subscription via `subscription`/`per-month`/
        # etc., so this deepens its evidence without adding or reordering any archetype
        # (score-neutral); it fires on ZERO of the metered-api (api.replicate.com),
        # retail (books.toscrape.com), or null (example.com) fixtures, so it can never
        # CONJURE a subscription claim on a site that does not already make one. The
        # classifier is off the scoring path.
        ("plan-purchase", re.compile(
            r"/plans/[^\s\"'<>]*/purchase\b"
            r"|\bpurchasable\s+plans?\b"
            r"|\b(?:buy|buys|buying|purchas(?:e|es|ed|ing)|activate|activates|activating)\s+(?:once\s+)?(?:a|an|your|the)?\s*(?:(?:credit|subscription)\s+(?:or|and|/)\s+)?(?:credit|subscription)\s+plans?\b", _F)),
        # BUNDLED MONTHLY ALLOWANCE + METERED OVERAGE — the HYBRID subscription
        # plan whose recurring fee INCLUDES a bounded per-cycle allowance that
        # RESETS each billing period, with usage BEYOND it charged as metered
        # overage. This is the "understand the offer" capability for the modern
        # subscription archetype, and it is currently UNCAPTURED. Every existing
        # subscription signal describes a FLAT recurring commitment — that a plan
        # exists (`subscription`/`recurring`), its cadence (`per-month`/
        # `per-month-price`/`annual-billing`), its per-user basis (`seat-licensing`),
        # its $0 evaluation (`free-trial`), or its programmatic commit
        # (`plan-purchase`); NONE says the plan bundles a METERED quota that resets
        # and then bills overage. An autonomous agent evaluating such a plan must
        # know the flat fee buys only a bounded monthly allowance and that calls
        # past it incur per-unit overage — a load-bearing CAPITAL-SAFETY fact (a
        # bounded-then-metered plan can silently accrue overage after the included
        # units are spent), and it lets the agent budget around the cycle reset.
        # This is distinct from metered_api's included/credit signals by ARCHETYPE
        # and by SENSE: `free-included-usage` is a FREE evaluation allowance that
        # needs no funding (a $0 trial of a metered call); `credit-metered` is a
        # prepaid CREDIT balance you buy/top-up; `usage-based`'s bare "overage" is
        # generic metered billing. NONE of them is a RECURRING PLAN's bundled
        # monthly allowance with a cycle reset — the subscription-side included quota.
        # Vendor-neutral bundled-plan vocabulary (a monthly allowance, a plan's
        # included allowance that resets each cycle, "a subscription with included
        # credit; usage beyond it is metered"), never a vendor.
        # PRECISION-CRITICAL: bare "\ballowance\b" is a false-positive minefield —
        # a "free allowance" that needs no funding (`free-included-usage`'s turf),
        # a baggage allowance, a tax allowance, a monthly EXPENSE/food/travel
        # allowance (an HR perk, not a plan quota). So NEVER match a bare
        # "allowance", and NEVER match a bare "monthly <anything> allowance":
        # require either a bare "monthly allowance" ("plan's monthly allowance") or a
        # monthly allowance qualified by a USAGE noun (a monthly generation / usage /
        # api / call / request / credit / render / token / image / video / compute /
        # query / inference / prediction allowance), the HYBRID plan definition
        # (`subscription with included ...`), or the plan-allowance LIFECYCLE it is
        # spent/reset on (`allowance used up`/`allowance resets`/`allowance is
        # tracked per plan`) — quota semantics an HR/baggage/
        # tax allowance never carries. The free-allowance, baggage, tax, and
        # monthly-expense senses trip none of these. Fires non-vacuously on BOTH
        # canonical domains (drift-flight.org + driftflight.com /docs: "counts one
        # generation against your plan's monthly allowance" + the 429 "Monthly
        # generation allowance used up; upgrade or wait for the cycle reset", and on
        # driftflight.com additionally "a subscription with included credit; usage
        # beyond it is metered and charged per call" and "the allowance is tracked
        # per plan access") — a PAIR, not a singleton, so it is not over-fit to one
        # fixture — and on ZERO of the metered-api-only (api.replicate.com), retail
        # (books.toscrape.com), or null (example.com) fixtures. Both canonical
        # domains ALREADY claim subscription (via `subscription`/`per-month`/etc.),
        # so this deepens their subscription evidence without adding or reordering
        # any archetype (subscription strength 4->5 on .org / 6->7 on .com, still
        # well below digital_good's 10 — no reorder; the claimed set is unchanged) —
        # score-neutral, and it can never CONJURE a subscription claim on a site
        # that does not already make one. The classifier is off the scoring path.
        ("plan-allowance", re.compile(
            r"\bmonthly\s+allowance\b"
            r"|\bmonthly\s+(?:generation|usage|api|call|request|credit|render|token|image|video|compute|query|inference|prediction)\s+allowance\b"
            r"|\bsubscription\s+with\s+included\b"
            r"|\ballowance\s+(?:used\s+up|resets?|is\s+tracked\s+per\s+plan)\b", _F)),
    ],
    "digital_good": [
        ("generation", re.compile(r"\b(text-to-image|image|video|audio|art)\s+generation\b", _F)),
        # A verb-phrase claim that the service GENERATES a media deliverable — the
        # core "digital good" capability (the agent obtains a generated image /
        # video / audio / art asset). Recall breadth over generation phrasing: the
        # verb takes ALL its inflections (generate / generates / generated /
        # generating — "we generate videos", "generating an image", the canonical
        # pair's "Generated images"), the media noun takes its PLURAL ("generate
        # videos", "Generated images"), and a leading article/possessive/definite
        # is optional ("generate an image", "generate your art", "generate the
        # audio"). Without the inflection+plural breadth a real generation
        # storefront that says only "we generate videos" fires NO generate-media
        # signal at all (the singular-imperative form was the only one recognized),
        # so the digital_good archetype could be missed entirely on plural/participle
        # copy. PRECISION preserved: the verb must still be `generat...` at a word
        # boundary (so "regenerate a token" does NOT fire — no boundary before
        # "generat" inside "regenerate") and the object must still be one of the
        # media nouns at a word boundary (so "generate imagery" / "generate output"
        # / "generate a response" / "generate reports" never fire — "imagery" has no
        # boundary after "image", and "output"/"response"/"reports" are not media
        # nouns). Vendor-neutral: only the media-category nouns, never a product name.
        ("generate-media", re.compile(
            r"\bgenerat(?:e|es|ed|ing)\s+(?:an?\s+|your\s+|the\s+)?(?:image|video|audio|art)s?\b", _F)),
        ("generations", re.compile(r"\bgenerations?\b", _F)),
        ("render", re.compile(r"\brenders?\b|\brendering\b", _F)),
        ("translation", re.compile(r"\btranslat(e|es|ion|ing)\b", _F)),
        ("hosted-output", re.compile(r"\bhosted (output )?URLs?\b|\bimageUrls?\b|\bdownloadable\b", _F)),
        # Output USAGE-RIGHTS / license — the "complete the job" RIGHTS leg of a
        # digital good. The existing digital_good signals say WHAT is produced
        # (`generation` / `generate-media`) and WHERE it is delivered
        # (`hosted-output`); NONE says whether the agent may USE what it obtains. A
        # generation storefront that returns a render an agent has no license to use
        # has NOT completed the commercial job — so a storefront that grants a
        # commercial-use licence, royalty-free terms, explicit usage rights, or
        # ownership of the generated output is MORE agent-completable at the
        # digital-good layer. Vendor-neutral IP/rights vocabulary (a commercial
        # licence, royalty-free, usage rights, owning the output), never a vendor.
        # PRECISION-CRITICAL: bare "license"/"licensed" is a false-positive minefield
        # — a software licence (MIT/Apache), a business/driver's licence, a "Licensed
        # and credentialed" trust badge, and — the trap this signal must dodge — the
        # license of a hosted MODEL (api.replicate.com, a metered_api-ONLY storefront,
        # says "the model's license" and "delete models you own"; neither is a
        # deliverable-rights grant). So NEVER match bare "license": require
        # commercial-USE rights ("commercial licence/licensing"), royalty-free terms,
        # explicit "usage rights", or ownership of the DELIVERABLE ("you own the
        # output/render/result/image/generation"). The model-license, software-license,
        # and "models you own" senses trip none of these. Fires on BOTH canonical
        # domains (drift-flight.org homepage "commercial licence on every image";
        # driftflight.com /llms-full.txt "a commercial licence …; you own the output")
        # — both ALREADY claim digital_good, so it deepens evidence without changing
        # any claimed set (score-neutral) — and on ZERO of the api/retail/null fixtures.
        ("output-license", re.compile(
            r"\bcommercial licen[cs](?:e|es|ed|ing)\b"
            r"|\broyalty[- ]free\b"
            r"|\busage rights\b"
            r"|\byou own\s+(?:the\s+)?(?:output|render|renders|result|results|generation|generations|image|images|asset|assets)\b", _F)),
        # Output CONTENT-PROVENANCE — the "verify + trust the deliverable" leg of a
        # digital good. The existing digital_good signals say WHAT is produced
        # (`generation` / `generate-media`), WHERE it is delivered (`hosted-output`),
        # and whether the agent may USE it (`output-license`); NONE says whether the
        # agent can VERIFY the authenticity and origin of what it obtained. As synthetic
        # media proliferates, a generated deliverable that carries embedded provenance —
        # C2PA content credentials, a provenance manifest / metadata that records how it
        # was made — lets an autonomous agent confirm the asset is genuine and use it in
        # a provenance-aware pipeline (disclosure, attribution, downstream trust). A
        # render an agent cannot provenance-check has NOT completed the commercial job
        # in a world that requires content authenticity, so a storefront that embeds
        # content credentials / records provenance on its output is MORE agent-completable
        # at the digital-good layer. It is the trust/authenticity MIRROR of `output-license`
        # (which grants the RIGHT to use the deliverable — this grants the MEANS to trust
        # it). Vendor-neutral OPEN-STANDARD provenance vocabulary — C2PA (the Coalition for
        # Content Provenance and Authenticity standard), the CAI "Content Credentials" mark,
        # a media/output provenance manifest/metadata record — the same open-convention
        # category as REST/GraphQL/OpenAPI/x402 already in this bank, never a vendor.
        # PRECISION-CRITICAL: bare "provenance" is a false-positive minefield — art / wine /
        # supply-chain provenance, and — the trap this signal must dodge — "data provenance"
        # (a data_retrieval concern) and a MODEL FEATURE description on a metered_api
        # marketplace (api.replicate.com's hosted model "Embed invisible SynthID watermarking
        # for provenance on all generated ... images" describes what a HOSTED MODEL does, not a
        # deliverable the storefront itself vends — it must NOT conjure a digital_good claim on
        # a metered-API-only site). So NEVER match a bare "provenance"/"credentials": require
        # the C2PA standard name, the "content credentials" mark, a media/output noun
        # IMMEDIATELY qualifying "provenance" (content/media/image/output/asset/render
        # provenance), "provenance" naming a metadata/credential/record/manifest object, or a
        # "records provenance" grant. The art/wine/supply-chain/data senses and the
        # "watermarking for provenance" model-feature phrasing trip none of these. Fires
        # non-vacuously on BOTH canonical domains (drift-flight.org + driftflight.com — "embedded
        # C2PA content credentials", "C2PA credentials record provenance") — both ALREADY claim
        # digital_good, so it deepens evidence without adding or reordering any archetype
        # (score-neutral) — and on ZERO of the metered-api (api.replicate.com), retail
        # (books.toscrape.com), or null (example.com) fixtures, so it can never CONJURE a
        # digital_good claim on a site that does not already make one.
        ("content-provenance", re.compile(
            r"\bC2PA\b"
            r"|\bcontent credentials?\b"
            r"|\b(?:content|media|image|output|asset|render)\s+provenance\b"
            r"|\bprovenance\s+(?:metadata|credentials?|records?|manifest)\b"
            r"|\brecords?\s+provenance\b", _F)),
        # Output SPECIFICATION — the concrete dimensions of the generated
        # deliverable an agent must REQUEST and can RELY ON: the maximum output
        # RESOLUTION / pixel DIMENSIONS / ASPECT RATIO of the produced image /
        # video / render. This is the "understand + specify the offer" leg of a
        # digital good, and it is distinct from every existing digital_good signal:
        # `generation` / `generate-media` / `generations` / `render` say WHAT is
        # produced, `hosted-output` says WHERE it is delivered, `output-license`
        # whether the agent may USE it, `content-provenance` whether the agent can
        # TRUST it — NONE says the physical SHAPE of the deliverable the agent must
        # parameterize its request with. An autonomous agent that cannot read the
        # output-resolution contract either requests a size the API cannot produce
        # (a failed or clipped generation) or gets a deliverable at the wrong
        # resolution for its downstream use (a hero image delivered at thumbnail
        # size), so a generation storefront that documents its output resolutions /
        # dimensions is MORE agent-completable at the digital-good layer. Vendor-
        # neutral output-format vocabulary (a `maxResolution` field, an output /
        # render / print resolution in pixels, a WxH pixel dimension, an aspect
        # ratio) — the same open-convention category as the media nouns already in
        # this bank, never a vendor.
        # PRECISION-CRITICAL: bare "\bresolution\b" is a false-positive minefield —
        # "dispute resolution", a "New Year resolution", "DNS resolution", and — the
        # trap this signal must dodge on a metered-API marketplace — a hosted MODEL's
        # FEATURE description ("Super resolution", "Enhance image resolution" appear
        # verbatim in api.replicate.com's committed /openapi.json; those describe what
        # a hosted MODEL does, not a deliverable the storefront itself vends, and must
        # NOT conjure a digital_good claim on a metered_api-only site). A SCREEN /
        # MONITOR / DISPLAY resolution is the viewer's hardware, not the deliverable's
        # spec, and must not fire either. So NEVER match a bare "resolution": require
        # the `maxResolution` output-spec KEY, a `print` resolution, a resolution
        # expressed as an explicit PIXEL value (`resolution up to 4096px`) but NOT
        # when preceded by screen/monitor/display, an OUTPUT / RENDER / CANVAS /
        # GENERATION / TARGET resolution-or-dimensions phrase, a WxH pixel dimension
        # (`1024x1024 px`), or an `aspect ratio`. The dispute/New-Year/DNS senses, the
        # Super-/image-resolution model-feature phrasing, and the screen/monitor/
        # display hardware senses trip none of these. Fires non-vacuously on BOTH
        # canonical domains (the /docs models block's `"maxResolution":"1024px|2048px|
        # 4096px"` + the homepage "gallery for hero and print resolution") — both
        # ALREADY claim digital_good, so it deepens evidence without adding or
        # reordering any archetype (score-neutral) — and on ZERO of the metered-api
        # (api.replicate.com, whose "Super resolution" / "Enhance image resolution"
        # model features are correctly dodged), retail (books.toscrape.com), or null
        # (example.com) fixtures, so it can never CONJURE a digital_good claim on a
        # site that does not already make one. The classifier is off the scoring path.
        ("output-resolution", re.compile(
            r"\bmaxResolution\b"
            r"|\bprint\s+resolutions?\b"
            r"|(?<!screen\s)(?<!monitor\s)(?<!display\s)\bresolutions?\s*(?:up\s+to\s+|of\s+|:\s*|=\s*)?\d{2,5}\s?(?:px|pixels?)\b"
            r"|\b(?:output|render|canvas|generation|target)\s+(?:resolutions?|dimensions?)\b"
            r"|\b\d{3,5}\s?[x×]\s?\d{3,5}\s?(?:px|pixels?)\b"
            r"|\baspect[- ]ratios?\b", _F)),
        # Output DELIVERY-WINDOW / retention — how long the generated deliverable
        # PERSISTS at its hosted URL, and that the agent must RETRIEVE it (download
        # it into its OWN storage) before that window closes. This is the "complete
        # the job" LIFECYCLE leg of a digital good, and it is distinct from every
        # existing digital_good signal: `generation` / `generate-media` / `render` say
        # WHAT is produced, `hosted-output` WHERE it is delivered (a hosted URL exists),
        # `output-resolution` the SHAPE of it, `output-license` whether the agent may
        # USE it, `content-provenance` whether the agent can TRUST it — NONE says HOW
        # LONG the hosted deliverable lives or that the agent must copy it out before it
        # expires. An autonomous agent on a long-running or batched job that reads
        # "here is a hosted URL" but not "it is gone in 90 days — download it into your
        # own storage" silently LOSES its output when the link expires, so a generation
        # storefront that documents its output-retention window (and the download-to-
        # your-own-storage step) is MORE agent-completable at the digital-good layer. It
        # is the digital_good sibling of metered_api's `cancel-job` — both are
        # job-lifecycle CONTROL legs (there: STOP a runaway job; here: COLLECT a finished
        # job's deliverable in time). Vendor-neutral artifact-lifecycle vocabulary (a
        # hosted output/render/URL that remains available for / is stored / retained /
        # kept for N hours|days, download it into your own storage/bucket, an output
        # retention window/period/policy) — the same open-convention category as the
        # media nouns already in this bank, never a vendor.
        # PRECISION-CRITICAL: a bare time window ("available for 24 hours", "hosted for
        # 3 days") is a false-positive minefield — a support line ("agents remain
        # available for 24 hours"), an EVENT ("the conference is hosted for 3 days"), a
        # FREE TRIAL ("free for 30 days"), and — the trap this signal must dodge on a
        # metered-API marketplace — api.replicate.com's Files API file EXPIRY ("When the
        # file expires", "a Unix timestamp with expiration date of this download URL"),
        # which is a signed-URL expiry, NOT a hosted-deliverable retention window, and
        # must NOT conjure a digital_good claim on a metered_api-only site. So NEVER
        # match a bare window: require the retention window to attach to a DELIVERABLE
        # noun (output/render/image/video/audio/asset/file/generation/url/deliverable
        # within a short same-line span of `remain(s/ing) available` / `hosted` /
        # `stored` / `retained` / `kept` `for N hours|days|weeks|months`), the
        # unambiguous "download ... into your own storage/bucket" step, or an explicit
        # "<output/render/...> retention window/period/policy". The support-line,
        # event-hosting, free-trial, and api-key/file-expiry senses (no deliverable noun,
        # or no time window, or no "into your own storage") trip none of these. Fires
        # non-vacuously on BOTH canonical domains' captured /docs ("returned as hosted
        # URLs that remain available for 90 days; download them into your own storage") —
        # both ALREADY claim digital_good, so it deepens evidence without adding or
        # reordering any archetype (score-neutral, pinned by tests/test_offering_canonical.py)
        # — and on ZERO of the metered-api (api.replicate.com's file-expiry trap dodged),
        # retail (books.toscrape.com), or null (example.com) fixtures, so it can never
        # CONJURE a digital_good claim on a site that does not already make one. The
        # classifier is off the scoring path.
        ("output-retention", re.compile(
            r"\b(?:output|render|image|video|audio|asset|file|generation|url|deliverable)s?\b[^.\n]{0,40}?\b(?:remain(?:s|ing)?\s+available|hosted|stored|retained|kept)\s+for\s+\d+\s+(?:hours?|days?|weeks?|months?)\b"
            r"|\bdownload\s+(?:them|it|these|the\s+(?:images?|outputs?|renders?|results?|files?|assets?|generations?))\s+into\s+your\s+own\s+(?:storage|bucket|store)\b"
            r"|\b(?:output|render|image|video|asset|file|deliverable|generation)\s+retention\s+(?:window|period|policy)\b", _F)),
        # PROGRAMMATIC OUTPUT-VARIANT SELECTION — whether an autonomous agent can
        # DISCOVER and SELECT which VARIANT a generative digital-good service
        # produces: a named, listable style PRESET the agent passes on the request
        # so it obtains a FIT-FOR-PURPOSE, REPRODUCIBLE deliverable rather than a
        # nondeterministic one it cannot use downstream. This is the "complete the
        # job with a USABLE deliverable" leg of the digital_good archetype, and it
        # is currently UNCAPTURED. Every existing digital_good signal describes a
        # PROPERTY of the artifact the agent RECEIVES — that media is generated
        # (`generation`/`generate-media`/`generations`/`render`/`translation`), how
        # it is delivered (`hosted-output`), what rights attach (`output-license`),
        # whether it is authentic (`content-provenance`), how large it is
        # (`output-resolution`), how long it persists (`output-retention`); NONE
        # says whether the agent can CONTROL which variant gets produced. An agent
        # generating at scale (a catalog run where "the two-hundredth image has to
        # match the first") cannot use a service that returns a random style each
        # call — a selectable preset that "locks palette, lighting, and rendering
        # style" is exactly what makes the deliverable consistent and pipeline-safe,
        # so a generative offer that documents programmatic variant selection is
        # MORE agent-completable. Vendor-neutral variant-selection vocabulary (a
        # STYLE preset, a preset SLUG/STRING/PARAMETER/ID/NAME, pick/choose/select/
        # browse/pass/send a preset, a preset that locks/pins the style), never a
        # vendor.
        # PRECISION-CRITICAL: bare "model" and "tier" are false-positive minefields —
        # a language/business/role/3D "model" and a billing "tier" (which the
        # metered_api `tiered-volume` signal already owns) appear all over these
        # docs — so NEITHER is ever matched. "preset" is anchored to a STYLE preset,
        # a preset PARAMETER (slug/string/param/id/name), an explicit SELECT/BROWSE
        # verb naming a preset, or the determinism verb (a preset locks/pins the
        # style); the preset-VERB ("preset the oven to 200C"), factory/camera presets,
        # and "reset" trip none of these. Fires non-vacuously on BOTH canonical
        # domains' captured surfaces (homepage/docs "Pick a preset", "style presets",
        # "Browse presets", and the `preset` request-parameter "A style preset slug")
        # — BOTH ALREADY claim digital_good (both are image-generation storefronts, so
        # variant selection is a shared deliverable-control capability, NOT a
        # payment/rails gap), so it deepens evidence without adding or reordering any
        # archetype (score-neutral, pinned by tests/test_offering_canonical.py) — and
        # on ZERO of the metered-api (api.replicate.com), retail (books.toscrape.com),
        # or null (example.com) fixtures, so it can never CONJURE a digital_good claim
        # on a site that does not already make one. The classifier is off the scoring
        # path.
        ("variant-selection", re.compile(
            r"\bstyle\s+presets?\b"
            r"|\bpresets?\s+(?:slug|string|param(?:eter)?s?|id|name)\b"
            r"|\b(?:pick|choose|select|browse|specify|pass|send)\s+(?:a\s+|the\s+|your\s+|one\s+)?presets?\b"
            r"|\bpresets?\s+(?:lock|pin)s?\b", _F)),
    ],
    "physical_good": [
        # PRECISION-CRITICAL: bare "ship" is metaphorical on many agent-native
        # sites ("every image you ship"); require unambiguous fulfillment nouns.
        ("free-shipping", re.compile(r"\bfree shipping\b", _F)),
        ("shipping-noun", re.compile(r"\bshipping (address|cost|rates?|options?|method|fee|policy)\b", _F)),
        ("add-to-cart", re.compile(r"\badd to (cart|bag|basket)\b|\bshopping cart\b", _F)),
        ("stock", re.compile(r"\b(in|out of|back in) stock\b", _F)),
        # PRICED CATALOG LISTING — the "understand the offer" price leg for a
        # physical good. To DECIDE and FULFILL a physical purchase an agent must
        # read the CONCRETE price of a purchasable, in-stock catalog item; a
        # storefront that quotes a decimal amount directly beside the item's
        # availability / add-to-cart control ("£51.77 In stock", "$12.99 Add to
        # basket") makes that price machine-legible on the listing. Distinct from
        # the sibling physical_good legs: `add-to-cart` is the buy ACTION, `stock`
        # is WHETHER it is available, `sku-inventory` is inventory MANAGEMENT —
        # none of them guarantees a readable PRICE on the offer.
        # PRECISION-CRITICAL: a bare currency amount is a false-positive minefield —
        # a metered API quotes "$0.01 per API call" / "$29 / month" / "$5 per 1,000
        # requests" and a subscription quotes a per-period fee, NONE of which sits
        # adjacent to in-stock / add-to-cart availability language. So NEVER match a
        # bare price: require a decimal money amount IMMEDIATELY followed by
        # "in stock" or an "add to cart/basket/bag" control — the unambiguous
        # priced-catalog-listing shape. The canonical flight-API pair carries
        # 12–17 bare currency amounts (metered per-call pricing) yet ZERO priced
        # in-stock listings, so this leg can never CONJURE physical_good on an API
        # storefront that merely lists dollar amounts (physical_good stays NA there
        # — pinned by tests/test_offering_canonical.py). Currency symbol optional
        # (the amount, not the glyph, is the evidence; a mojibake "£" must not gate
        # recognition). Precision-first: recall loss on the reverse "in stock … price"
        # order (which can span two adjacent listings) is accepted — a real shop
        # trips add-to-cart / stock anyway. Fires non-vacuously on the real retail
        # fixture (books.toscrape.com, 60 priced listings) and on ZERO of the
        # metered-API (api.replicate.com), canonical (drift-flight.org /
        # driftflight.com), or null (example.com) fixtures.
        ("priced-listing", re.compile(
            r"\d+[.,]\d{2}\s+(?:in stock\b|add to (?:cart|basket|bag)\b)", _F)),
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
        # RECORD ENRICHMENT — an agent submits records and gets structured fields
        # back. PRECISION-CRITICAL: bare "\benrich\b" is a false-positive minefield —
        # marketing prose reads "an enriched user experience", "an enriching
        # partnership", "enrich your workflow", "enrichment of company culture" — none
        # of which is a data-retrieval OFFERING; each would falsely claim
        # data_retrieval and run an irrelevant lookup intent (the exact archetype
        # pollution this module removes, and doubly harmful on data_retrieval, one of
        # the two thinnest archetypes). So NEVER match a bare "enrich": require the
        # verb to name an unambiguous DATA object (records / data / a dataset /
        # contacts / leads / profiles / rows / fields) within a short same-clause
        # window (either order), or the fixed "data enrichment" phrase. The
        # experience/partnership/workflow/culture senses (no data noun) trip none of
        # these; the genuine "enrich a list of records" / "enriches company records"
        # data-service prose still fires (pinned by the genuine-offering tests).
        ("enrich", re.compile(
            r"\benrich\w*\b[^.\n]{0,40}?\b(?:records?|data|datasets?|contacts?|leads?|profiles?|rows?|fields?)\b"
            r"|\b(?:records?|data|contacts?|leads?|profiles?)\b[^.\n]{0,20}?\benrich\w*"
            r"|\bdata\s+enrichment\b", _F)),
        # QUERYABLE DATASET — a dataset the agent can RETRIEVE FROM (query / download /
        # access / subscribe to), or a dataset offered AS a product (a dataset API /
        # feed / subscription / marketplace). PRECISION-CRITICAL: bare "\bdataset\b" is
        # a false-positive minefield — it is the single most common TRAINING-PROVENANCE
        # word in generative/ML prose ("trained on a dataset of 100M images", "our
        # training dataset", "a diverse dataset of prompts"), which describes what a
        # MODEL learned from, NOT a data product the storefront vends. Left bare, an
        # image-generation API (metered_api + digital_good) whose marketing mentions
        # its training dataset would ALSO falsely claim data_retrieval and be probed
        # with a "query a dataset" intent it does not serve. So NEVER match a bare
        # "dataset": require a RETRIEVAL/ACCESS verb adjacent to it (query / search /
        # access / download / retrieve / fetch / pull / look up / subscribe to /
        # licence / browse / against a ... dataset) or the dataset named AS an offering
        # (dataset api / feed / subscription / catalog / marketplace / endpoint /
        # access / licence / download). The "trained on"/"training"/"dataset of ..."
        # provenance senses (no retrieval verb, no offering noun) trip none of these;
        # the genuine "query the dataset" / "enrich records against our datasets" prose
        # still fires (pinned by the genuine-offering tests). Off the scoring path;
        # data_retrieval stays NA on every committed fixture (none serves a dataset).
        ("dataset", re.compile(
            r"\bdatasets?\s+(?:api|feed|subscription|catalog(?:ue)?|marketplace|endpoint|access|licen[sc]e|download|lookup)\b"
            r"|\b(?:quer(?:y|ying|ies)|search|access|download|retriev\w+|fetch|pull|look\s?up|subscribe\s+to|licen[sc]e|browse|against)\s+(?:\w+\s+){0,3}datasets?\b", _F)),
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

    Drops script/style blocks then tags, DECODES HTML entities, collapses
    whitespace. A no-op on text that has no tags (llms.txt / plain manifests
    pass through unchanged).

    Entity decoding is what makes this the VISIBLE prose, not just the tag-free
    bytes. Real HTML routinely joins the exact two-word capability phrases a
    publisher does not want to line-wrap with a non-breaking space entity —
    ``Free&nbsp;shipping``, ``per&nbsp;month``, ``Add&nbsp;to&nbsp;cart`` — and
    escapes ampersands/quotes/dashes (``&amp;``, ``&#39;``, ``&mdash;``). Left
    literal, ``Free&nbsp;shipping`` is not the string ``free shipping``, so the
    many literal-single-space signals ("free shipping", "add to cart", "per
    month") silently miss and the storefront is under-classified purely on
    encoding — the sibling failure to the Cycle-178 line-wrap gap, from a space
    that was ENCODED rather than WRAPPED. Decoding runs AFTER tag removal (so a
    real ``<div>`` is stripped as markup) but BEFORE the whitespace collapse (so
    ``&nbsp;`` -> ``\\xa0`` folds into the single-space normalization with every
    other layout whitespace). Precision-safe: ``_html.unescape`` only rewrites
    ``&...;`` sequences, so it cannot conjure a capability phrase from prose that
    does not already contain one (an entity-shaped noise token like ``&amp;``
    decodes to ``&``, never to a signal word). Off the scoring path (discovery
    drives ``--battery auto`` task selection only); the canonical CLAIMED sets
    are invariant because their committed ``&nbsp;`` sits in a brand-logo marquee
    ("Arclight&nbsp;Goods"), which decodes to prose that fires no signal.
    """
    if not text or "<" not in text:
        return (text or "").strip()
    stripped = _SCRIPT_STYLE_RE.sub(" ", text)
    stripped = _TAG_RE.sub(" ", stripped)
    stripped = _html.unescape(stripped)
    return _WS_RE.sub(" ", stripped).strip()


def _is_html_document(text: str) -> bool:
    """True if ``text`` looks like a full HTML page (so it should be HTML-stripped).

    Keys on the leading bytes only — a ``<!doctype html>`` / ``<html`` prologue —
    so it fires on a rendered docs/API-reference page but NOT on a JSON surface
    (``{`` first) or a plain-text ``llms.txt`` (text first), both of which must
    pass through unstripped. This lets :func:`classify_offering` strip markup from
    an HTML doc-page surface (e.g. ``/docs``) exactly as it does the homepage,
    keeping ``<script>``/``<style>`` decoy words out of the scanned prose, without
    disturbing the non-HTML surfaces whose bytes carry the signal directly.
    """
    head = (text or "").lstrip()[:256].lower()
    return head.startswith("<!doctype html") or head.startswith("<html") or "<html" in head


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
        raw = text or ""
        # Strip markup to visible prose for the homepage AND any HTML-document
        # surface (a rendered /docs API-reference page); plain-text and JSON
        # surfaces (llms.txt, manifest.json, openapi.json, agent cards) carry the
        # signal directly and pass through unchanged.
        prose = strip_html(raw) if (surface == "homepage" or _is_html_document(raw)) else raw
        if not prose:
            continue
        # Whitespace-reflow invariance. A plain-text surface (llms.txt, a markdown
        # docs page) is routinely line-wrapped, so a two-word capability phrase can
        # straddle a newline ("free\nshipping", "per\nmonth"), and HTML-stripped
        # prose can carry runs of layout whitespace. Many signals separate their
        # tokens with a LITERAL single space ("free shipping", "add to cart",
        # "book a ..."), which a line-wrap or a double space silently defeats —
        # dropping the claim, and with it the site's whole task battery, purely on
        # typography. Collapse every whitespace run to a single space (the SAME
        # normalization already applied to evidence quotes via _WS_RE) so a signal
        # keys on the WORDS a surface declares, not the shape a crawl captured.
        # Precision-safe: a single space still separates tokens and \b boundaries
        # still hold, so collapsing runs cannot conjure a phrase that isn't there
        # (verified: paragraph-split "add\n\nto ... cart" stays unclaimed). Off the
        # scoring path (discovery drives --battery auto task selection only), so the
        # canonical scoring delta is untouched; the canonical CLAIMED sets are
        # invariant (tests/test_offering_canonical.py) because their evidence is not
        # reflowed.
        prose = _WS_RE.sub(" ", prose)
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
    (``.well-known/agent.json`` / ``.well-known/agent-card.json``), the machine
    API contract (``openapi.json`` / ``.well-known/openapi.json`` / ``swagger.json``),
    and the rendered API-docs page (``/docs`` / ``/api-docs`` / ``/reference`` — HTML,
    so it is HTML-stripped like the homepage before scanning)
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
