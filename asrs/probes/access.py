"""Access pillar probes: can an agent get in at all?

Checks:
  - robots_ai_crawlers    — robots.txt policy for the major AI agent UAs
  - agent_ua_reachability — do agent User-Agents get blocked/challenged while a
                            browser UA passes (a bot wall aimed at agents)?

Both emit exactly one CheckResult with pillar="access" and the rubric's
max_points. Network failure or genuine ambiguity => Status.CANT_TEST; we never
punish the unknown and never raise.
"""

from __future__ import annotations

from asrs.fetch import FetchContext, FetchResult
from asrs.types import CheckResult, Status

# The AI agents whose robots.txt treatment we care about. These are the UA
# *tokens* a site would name in a robots.txt User-agent line.
AI_CRAWLERS = (
    "GPTBot",
    "ClaudeBot",
    "Claude-User",
    "OAI-SearchBot",
    "PerplexityBot",
    "Google-Extended",
)


def run(ctx: FetchContext) -> list[CheckResult]:
    return [
        _robots_ai_crawlers(ctx),
        _agent_ua_reachability(ctx),
    ]


# ---------------------------------------------------------------------------
# robots_ai_crawlers
# ---------------------------------------------------------------------------


def _robots_ai_crawlers(ctx: FetchContext) -> CheckResult:
    max_points = 10.0
    check_id = "robots_ai_crawlers"
    pillar = "access"

    # Ensure base_url is resolved so /robots.txt hits the right origin.
    ctx.homepage()
    res = ctx.get("/robots.txt", ua="browser")

    if res.error is not None:
        return CheckResult(
            check_id, pillar, Status.CANT_TEST, 0.0, max_points,
            finding="robots-fetch-failed",
            remediation="Ensure /robots.txt is reachable so crawlers can read your policy.",
            evidence={"url": res.url, "error": res.error},
        )

    # No robots.txt (or an error page) => default-allow for everyone.
    body = res.text or ""
    if res.status != 200 or not _looks_like_robots(body):
        return CheckResult(
            check_id, pillar, Status.PASS, max_points, max_points,
            finding="no-robots-txt-default-allow",
            remediation="",
            evidence={
                "url": res.url,
                "status": res.status,
                "note": "No robots.txt present; absence means crawlers are allowed by default.",
            },
        )

    groups = _parse_robots(body)
    blocked: list[str] = []
    for agent in AI_CRAWLERS:
        if not _agent_allowed(agent, groups):
            blocked.append(agent)

    allowed_n = len(AI_CRAWLERS) - len(blocked)
    fraction = allowed_n / len(AI_CRAWLERS)
    ev = {
        "url": res.url,
        "checked_agents": list(AI_CRAWLERS),
        "blocked_agents": blocked,
        "snippet": _snippet(body),
    }

    if not blocked:
        return CheckResult(
            check_id, pillar, Status.PASS, max_points, max_points,
            finding="robots-allows-ai-crawlers", remediation="", evidence=ev,
        )
    if len(blocked) == len(AI_CRAWLERS):
        return CheckResult(
            check_id, pillar, Status.FAIL, 0.0, max_points,
            finding="robots-blocks-all-ai-crawlers",
            remediation="Remove the Disallow: / rules for AI crawler user-agents "
            "in robots.txt so agents can read your catalog.",
            evidence=ev,
        )
    return CheckResult(
        check_id, pillar, Status.PARTIAL, round(max_points * fraction, 2), max_points,
        finding="robots-blocks-some-ai-crawlers",
        remediation=f"Allow the blocked AI crawlers in robots.txt: {', '.join(blocked)}.",
        evidence=ev,
    )


def _looks_like_robots(body: str) -> bool:
    """Heuristic: a real robots.txt has a User-agent or Disallow/Allow line."""
    low = body.lower()
    if "<html" in low or "<!doctype" in low:
        return False
    return "user-agent:" in low or "disallow:" in low or "allow:" in low or "sitemap:" in low


def _parse_robots(body: str) -> list[dict]:
    """Parse robots.txt into groups: [{'agents': [...], 'rules': [(kind, path)]}].

    kind is 'allow' or 'disallow'. Blank lines separate records; consecutive
    User-agent lines share the following rules (standard robots.txt semantics).
    """
    groups: list[dict] = []
    current: dict | None = None
    expecting_agents = False
    for raw in body.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            expecting_agents = False
            continue
        if ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()
        if field == "user-agent":
            if current is None or not expecting_agents:
                current = {"agents": [], "rules": []}
                groups.append(current)
                expecting_agents = True
            current["agents"].append(value.lower())
        elif field in ("disallow", "allow"):
            if current is None:
                # Rules before any User-agent line: treat as global (*) group.
                current = {"agents": ["*"], "rules": []}
                groups.append(current)
            current["rules"].append((field, value))
            expecting_agents = False
        else:
            # Sitemap:, Crawl-delay:, etc. don't end an agent block.
            pass
    return groups


def _agent_allowed(agent: str, groups: list[dict]) -> bool:
    """Effective allow/deny for one agent token. A specific UA group overrides *.

    Rule: if the agent is named in any group, only those groups apply (the *
    group is ignored). Blocked = a Disallow rule matches "/" (root) and no
    more-specific Allow overrides it for the root path.
    """
    agent_l = agent.lower()
    specific = [g for g in groups if agent_l in g["agents"]]
    applicable = specific if specific else [g for g in groups if "*" in g["agents"]]
    if not applicable:
        return True  # unspecified => allowed
    # Determine access to the site root "/". Longest-match wins between
    # Allow and Disallow (RFC 9309); a bare "Disallow:" (empty) allows all.
    best_kind: str | None = None
    best_len = -1
    for g in applicable:
        for kind, path in g["rules"]:
            if path == "":
                # Empty Disallow = allow all; empty Allow = no-op. Treat both as
                # zero-length matches that don't block root.
                if kind == "disallow" and best_len < 0:
                    best_kind, best_len = "allow", 0
                continue
            if _path_matches_root(path):
                plen = len(path)
                if plen > best_len or (plen == best_len and kind == "allow"):
                    best_kind, best_len = kind, plen
    if best_kind is None:
        return True
    return best_kind == "allow"


def _path_matches_root(pattern: str) -> bool:
    """Does a robots Disallow/Allow pattern cover the site root '/'?"""
    if pattern == "/" or pattern == "/*":
        return True
    # A pattern like "/private" does not block root; only root-covering
    # patterns matter for "can the agent fetch the homepage/catalog".
    return False


# ---------------------------------------------------------------------------
# agent_ua_reachability
# ---------------------------------------------------------------------------

_CHALLENGE_MARKERS = (
    "just a moment",
    "cf-chl",
    "challenge-platform",
    "cf_chl_opt",
    "_cf_chl",
    "attention required",
    "checking your browser",
)


def _agent_ua_reachability(ctx: FetchContext) -> CheckResult:
    max_points = 10.0
    check_id = "agent_ua_reachability"
    pillar = "access"

    browser = ctx.homepage(ua="browser")
    if not _reachable(browser):
        return CheckResult(
            check_id, pillar, Status.CANT_TEST, 0.0, max_points,
            finding="site-unreachable",
            remediation="Site did not return a usable response even to a browser "
            "User-Agent; confirm the domain is live before assessing agent access.",
            evidence={"url": browser.url, "status": browser.status, "error": browser.error},
        )

    claude = ctx.homepage(ua="claudebot")
    gpt = ctx.homepage(ua="gptbot")

    claude_blocked = _is_agent_blocked(claude)
    gpt_blocked = _is_agent_blocked(gpt)
    blocked = [
        name for name, flag in (("ClaudeBot", claude_blocked), ("GPTBot", gpt_blocked)) if flag
    ]

    ev = {
        "browser": _ua_evidence(browser),
        "claudebot": _ua_evidence(claude),
        "gptbot": _ua_evidence(gpt),
        "blocked_agents": blocked,
    }

    if not blocked:
        return CheckResult(
            check_id, pillar, Status.PASS, max_points, max_points,
            finding="agent-ua-allowed", remediation="", evidence=ev,
        )
    if len(blocked) == 2:
        # Browsers pass, both agents blocked => a bot wall aimed at agents.
        # This finding slug triggers the agent-ua-hard-blocked grade cap.
        return CheckResult(
            check_id, pillar, Status.FAIL, 0.0, max_points,
            finding="agent-ua-hard-blocked",
            remediation="Allowlist AI agent User-Agents (ClaudeBot, GPTBot, etc.) "
            "in your WAF/CDN bot rules so agents aren't served a 403/challenge.",
            evidence=ev,
        )
    return CheckResult(
        check_id, pillar, Status.PARTIAL, 5.0, max_points,
        finding="agent-ua-partially-blocked",
        remediation=f"One agent User-Agent is blocked ({', '.join(blocked)}); "
        "review WAF/bot rules to allow all major AI agents consistently.",
        evidence=ev,
    )


def _reachable(res: FetchResult) -> bool:
    """A browser-UA fetch counts as reachable on a 2xx/3xx that isn't a challenge."""
    if res.error is not None or res.status is None:
        return False
    if not (200 <= res.status < 400):
        return False
    return not _looks_like_challenge(res)


def _is_agent_blocked(res: FetchResult) -> bool:
    """True when an agent UA is met with a block or challenge."""
    if res.error is not None or res.status is None:
        # Transport error only for the agent UA (browser reached the site) is
        # itself a signal the agent can't get through.
        return True
    if res.status in (401, 403, 429, 503):
        return True
    if _looks_like_challenge(res):
        return True
    # A tiny body with a 4xx is a bare block page.
    if res.status >= 400 and len(res.text.strip()) < 100:
        return True
    return False


def _looks_like_challenge(res: FetchResult) -> bool:
    if res.headers.get("cf-mitigated"):
        return True
    low = (res.text or "").lower()
    return any(marker in low for marker in _CHALLENGE_MARKERS)


def _ua_evidence(res: FetchResult) -> dict:
    return {
        "url": res.url,
        "status": res.status,
        "error": res.error,
        "cf_mitigated": res.headers.get("cf-mitigated"),
        "server": res.headers.get("server"),
        "body_len": len(res.text or ""),
    }


# ---------------------------------------------------------------------------
# shared
# ---------------------------------------------------------------------------


def _snippet(text: str, limit: int = 300) -> str:
    t = (text or "").strip()
    return t[:limit]
