"""HTTP layer for ASRS static probes.

A single ``FetchContext`` per domain: resolves the base URL by following
redirects on the first homepage fetch, maps a small set of agent identities to
their real published User-Agent strings, caches responses per (final url, ua)
in-memory, and — critically — never raises on a network error. A failed fetch
comes back as a ``FetchResult`` with ``error`` set and ``status`` None so probe
code can branch on it and emit CANT_TEST instead of crashing.

Stdlib + requests only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests

# Store at most ~500KB of body text per response; big enough for any HTML/JSON
# page we care about, small enough to keep a whole crawl in memory.
MAX_TEXT_BYTES = 500_000

# Real, published User-Agent strings. "browser" mimics current Chrome on macOS;
# the three agent identities are the exact strings the respective crawlers send
# (so a site's UA-based gating treats us exactly as it would the real agent).
USER_AGENTS: dict[str, str] = {
    "browser": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "claudebot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "ClaudeBot/1.0; +https://www.anthropic.com/claude-bot)"
    ),
    "gptbot": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
        "GPTBot/1.4; +https://openai.com/gptbot"
    ),
    "claude-user": (
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
        "Claude-User/1.0; +Claude-User@anthropic.com)"
    ),
}


@dataclass
class FetchResult:
    url: str  # what we asked for (resolved to absolute)
    final_url: str  # after redirects ("" when the request never completed)
    status: int | None  # HTTP status, or None on a transport-level error
    headers: dict  # response headers (case-insensitive lowercased keys)
    text: str  # body text, truncated to ~MAX_TEXT_BYTES
    error: str | None  # transport error message, or None on any HTTP response

    @property
    def ok(self) -> bool:
        """True when we got any HTTP response at all (even a 4xx/5xx)."""
        return self.error is None and self.status is not None

    @property
    def is_success(self) -> bool:
        """True for a 2xx or 3xx status (reachable + served content)."""
        return self.status is not None and 200 <= self.status < 400


class FetchContext:
    """Per-domain HTTP client with per-UA fetching and an in-memory cache."""

    def __init__(self, domain: str, timeout: float = 15.0) -> None:
        self.domain = _normalize_domain(domain)
        self.timeout = timeout
        # base_url is resolved lazily on the first homepage fetch (following
        # redirects, e.g. apex -> www, http -> https). Until then it's a best
        # guess from the domain so relative paths still resolve.
        self.base_url = f"https://{self.domain}"
        self._base_resolved = False
        self._cache: dict[tuple[str, str], FetchResult] = {}
        self._session = requests.Session()

    # -- public API ---------------------------------------------------------

    def get(self, path_or_url: str, ua: str = "browser") -> FetchResult:
        """Fetch a path (resolved against base_url) or an absolute URL.

        Caches per (final-requested-url, ua). Never raises: network problems
        return a FetchResult with error set and status None.
        """
        ua = ua if ua in USER_AGENTS else "browser"
        url = self._resolve(path_or_url)
        cache_key = (url, ua)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        result = self._fetch(url, ua)
        self._cache[cache_key] = result
        return result

    def homepage(self, ua: str = "browser") -> FetchResult:
        """Fetch the site root, resolving base_url from redirects on first call."""
        # Fetch the current best-guess root; _fetch updates base_url from the
        # final URL the first time so later relative paths resolve correctly.
        result = self.get(self.base_url, ua=ua)
        return result

    # -- internals ----------------------------------------------------------

    def _resolve(self, path_or_url: str) -> str:
        if _is_absolute_url(path_or_url):
            return path_or_url
        # urljoin needs a trailing slash context; base_url has no path so join
        # against base_url + "/" to make "docs" -> "<base>/docs".
        base = self.base_url
        if not base.endswith("/"):
            base = base + "/"
        return urljoin(base, path_or_url.lstrip("/"))

    def _fetch(self, url: str, ua: str) -> FetchResult:
        headers = {
            "User-Agent": USER_AGENTS[ua],
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            resp = self._session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
        except requests.exceptions.RequestException as exc:
            return FetchResult(
                url=url,
                final_url="",
                status=None,
                headers={},
                text="",
                error=f"{type(exc).__name__}: {exc}",
            )
        except Exception as exc:  # defensive: never let a fetch crash a probe
            return FetchResult(
                url=url,
                final_url="",
                status=None,
                headers={},
                text="",
                error=f"{type(exc).__name__}: {exc}",
            )

        text = _read_text(resp)
        # Lowercase header keys so probes can look up case-insensitively.
        resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        result = FetchResult(
            url=url,
            final_url=resp.url,
            status=resp.status_code,
            headers=resp_headers,
            text=text,
            error=None,
        )
        # Resolve base_url from the first successful root fetch's final URL.
        if not self._base_resolved and resp.url:
            parsed = urlparse(resp.url)
            if parsed.scheme and parsed.netloc:
                # Only adopt the origin (scheme + host), drop any path.
                self.base_url = f"{parsed.scheme}://{parsed.netloc}"
                self._base_resolved = True
        return result


# -- module helpers ---------------------------------------------------------


def _normalize_domain(domain: str) -> str:
    """Strip scheme/path/whitespace so 'https://x.com/y' -> 'x.com'."""
    d = domain.strip()
    if "://" in d:
        d = urlparse(d).netloc or urlparse(d).path
    # Drop any stray path/query and trailing slash.
    d = d.split("/")[0].strip()
    return d


def _is_absolute_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme in ("http", "https") and parsed.netloc)


def _read_text(resp: requests.Response) -> str:
    """Return the body decoded to str, truncated to ~MAX_TEXT_BYTES.

    Truncates on the raw byte content before decoding so we bound memory even
    for huge responses, then decodes with the response's apparent encoding.
    """
    raw = resp.content
    if len(raw) > MAX_TEXT_BYTES:
        raw = raw[:MAX_TEXT_BYTES]
    encoding = resp.encoding or resp.apparent_encoding or "utf-8"
    try:
        return raw.decode(encoding, errors="replace")
    except (LookupError, TypeError):
        return raw.decode("utf-8", errors="replace")
