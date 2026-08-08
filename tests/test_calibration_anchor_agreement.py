"""TRUTH guard: the LIVE calibration-sweep anchors agree with the OFFLINE
fixture-replay baseline.

Runnable directly, no pytest required:

    python tests/test_calibration_anchor_agreement.py

The loop measures the two canonical anchors (drift-flight.org / driftflight.com)
along TWO independent paths that, until now, floated free of each other:

  1. the OFFLINE fixture replay — tests/test_canonical_replay.py replays the
     committed fixtures through the real scorer and pins 46.1 F / 85.5 B /
     +39.4 (rubric v0.7). This is the in-cloud regression floor.
  2. the LIVE population sweep — experiments/calibration_sweep.py re-scores the
     real domains over the network on a cadence and commits a dated
     runs/local/calibration_sweep_*.json; each carries the two anchors under the
     segments api-storefront:{rails,no-rails}-anchor.

Nothing asserted these two paths AGREE. They are measurements of the SAME
storefronts: if a live re-capture ever drifts from the committed fixture floor,
that is a real calibration signal — either the site changed (the fixtures are
stale and owe a [LOCAL] re-capture) or the live crawl is unstable. This guard
welds the paths together so a divergence in EITHER goes red, giving the
canonical-delta regression check a SECOND, independent witness on live data.

The weld extends PAST the two famous anchors: any population member that carries
BOTH a committed offline replay baseline (replay.EXPECTED) AND a scored presence
in the committed live sweeps is welded, so the cross-path agreement is witnessed
on a NON-anchor domain too (example.com, the zero-commerce baseline, scored in
every committed sweep). That widens the regression signal from the pair the whole
loop already watches to an independent third point on the capability spectrum — a
live crawl that drifted a non-anchor member from its fixture floor now goes red as
loudly as an anchor would, so calibration decay is caught wherever it appears.

Attribution honesty (invariant #4): a sweep anchor that is not-scorable
(unreachable that cadence) is SKIPPED, never counted as a divergence — a site is
never punished for what could not be observed. Versioned comparability
(invariant #2): only sweeps at the baseline's rubric version are compared; a
different-version sweep is never diffed against a v0.7 floor.

Documented live drift (experiments/documented_live_drift.json): the offline replay
fixture is DELIBERATELY frozen (invariant #2 — no re-capture on a live fluctuation),
so once a real site DURABLY regresses, an honest live sweep no longer equals the
frozen floor and would redden this weld for a real reason it never modelled. The
ledger records the DOCUMENTED live value (in capability terms, with committed
evidence) the weld may ACCEPT for a (rubric_version, domain), so a documented
regression reads as a documented drift, not a divergence. Teeth are preserved — the
frozen floor is ALWAYS accepted (a recovery is never masked) AND the documented
value is accepted EXACTLY (never an open-ended band): a live value matching NEITHER
(an undocumented regression, or drift PAST the documented one) still goes red. When
the site recovers, the entry is retired.

Pure guard: reads committed JSON + imports the replay baseline constants (ONE
source of truth — a legitimate version-bump re-capture that moves
test_canonical_replay.EXPECTED moves this guard's target in lockstep). No
network, no scoring-path import. Off the scoring path, score-neutral — this only
pins that the two committed measurement paths of the anchors agree.
"""
from __future__ import annotations

import glob
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "tests"))

import test_canonical_replay as replay  # noqa: E402  (ONE source of truth for the baseline)

# The two canonical anchors, keyed as they appear both in replay.EXPECTED and in
# each sweep's `rows` (by `domain`). Their sweep `segment` ends with "-anchor".
# These stay the pair for the +39.4 gap/delta tests below.
_ANCHORS = ("drift-flight.org", "driftflight.com")
# NON-anchor population members welded across the two measurement paths: each must
# carry BOTH a committed offline replay baseline (replay.EXPECTED, same rubric
# version) AND a scored presence in the committed live sweeps, so the cross-path
# agreement is witnessed off the two famous anchors too. example.com (the
# zero-commerce baseline — guard 9 of test_canonical_replay pins its 22.5 floor;
# segment control:non-storefront) is scored in every committed sweep.
# books.toscrape.com (a real RETAIL catalog — the inverse storefront type from the
# API anchors, physical_good-claiming; test_canonical_replay pins its 29.5 floor) was
# added to the calibration POPULATION in the 20260807T045843Z sweep and is welded here
# as the SECOND non-anchor member. Its live↔frozen agreement was verified this fire
# (Local cycle 20260807T064228Z, static $0 re-score): live overall 29.5 == frozen 29.5
# and all four non-null pillars byte-identical, the cross-path evidence the cloud cannot
# produce (books.toscrape.com is NOT SCORABLE without outbound network).
# acuityscheduling.com (a real SERVICE-BOOKING appointment-scheduling SaaS — a THIRD
# structurally-distinct storefront type, neither an API storefront nor a retail catalog
# nor a zero-commerce page; test_canonical_replay pins its 54.0 floor, whose 25.0
# transactability is a genuine MIDDLE datapoint on the transactability scale) is welded
# here as the THIRD non-anchor member. It is scored 54.0 in THREE committed sweeps
# (20260805T014754Z, 20260806T044352Z, 20260807T045843Z, segment service-booking:saas).
# Its live↔frozen agreement was verified this fire (Local cycle 20260807T084355Z, static
# $0 re-score): live overall 54.0 == frozen 54.0 and all four non-null pillars
# byte-identical, the cross-path evidence the cloud cannot produce (acuityscheduling.com
# is NOT SCORABLE without outbound network).
# ipinfo.io (a real DATA-RETRIEVAL / IP-data enrichment API storefront — a FOURTH
# structurally-distinct storefront type, distinct from the two API storefront anchors, the
# retail catalog, the zero-commerce page, AND the service-booking SaaS; test_canonical_replay
# pins its 61.3 floor, whose 25.0 transactability + 72.73 legibility make it an UPPER-MIDDLE
# datapoint that densifies the overall scale) is welded here as the FOURTH non-anchor member.
# It is scored 61.3 in THREE committed sweeps (20260805T014754Z, 20260806T044352Z,
# 20260807T045843Z, segment data-retrieval:api). Its live↔frozen agreement was verified this
# fire (Local cycle 20260807T104102Z, static $0 re-score): live overall 61.3 == frozen 61.3
# and all four non-null pillars byte-identical, the cross-path evidence the cloud cannot
# produce (ipinfo.io is NOT SCORABLE without outbound network).
# api.replicate.com (a real PURE single-archetype metered_api compute / model-inference API
# storefront — a FIFTH structurally-distinct storefront TYPE, distinct from the two multi-archetype
# API storefront anchors, the retail catalog, the zero-commerce page, the service-booking SaaS,
# AND the data-retrieval API; test_canonical_replay pins its 29.5 floor, whose 18.18 legibility
# — the LOWEST of the non-anchor set — plus 0.0 transactability give 29.5 a pillar SHAPE distinct
# from books.toscrape.com's own 29.5 overall, so two same-overall members pin different pillar
# mixes) is welded here as the FIFTH non-anchor member. It is scored 29.5 in exactly ONE committed
# sweep (20260807T134527Z, segment metered-api:inference-platform — the cadence run that first
# added it to the POPULATION; absent from the four priors). Its live↔frozen agreement was verified
# this fire (Local cycle 20260807T144105Z, static $0 re-score): live overall 29.5 == frozen 29.5
# and all four non-null pillars byte-identical, the cross-path evidence the cloud cannot produce
# (api.replicate.com is NOT SCORABLE without outbound network). So the cross-path weld now spans
# FIVE structurally-distinct non-anchor witnesses: null-control (example.com) + retail-catalog
# (books.toscrape.com) + service-booking (acuityscheduling.com) + data-retrieval (ipinfo.io) +
# pure-inference-API (api.replicate.com).
# www.moleskine.com (a SECOND real RETAIL storefront — an established consumer-brand e-commerce
# shop; test_canonical_replay pins its 49.8 floor) is welded here as the SIXTH non-anchor member.
# It adds retail DEPTH rather than a new storefront TYPE: unlike books.toscrape.com's bare
# scraping-sandbox catalog (29.5; legibility 18.18 / transactability 0.0 / trust 33.33), a real
# brand earns higher legibility 40.91, PARTIAL transactability 18.75 (a real commerce surface but
# NO agent-native rail), and higher trust 73.33 — a DIFFERENT pillar mix at a DIFFERENT overall,
# so the two retail members pin a RANGE (29.5 -> 49.8), not a point, and 49.8 is a new distinct
# datapoint between example.com's 22.5 and acuityscheduling.com's 54.0. It EXERCISES the www/bare
# host-alias normalization (see _norm_domain): the replay baseline keys it 'www.moleskine.com'
# while all five committed sweeps row it 'moleskine.com' (segment retail:no-rails, scored 49.8 in
# every one) — the weld matches them as the same storefront, so this member is genuinely COMPARED
# (n_compared=5), not silently skipped. Its live<->frozen agreement was verified this fire (Local
# cycle 20260807T174235Z, static $0 re-score): live overall 49.8 == frozen 49.8 and all four
# non-null pillars byte-identical, the cross-path evidence the cloud cannot produce
# (www.moleskine.com is NOT SCORABLE without outbound network).
# exa.ai (a real AGENT-NATIVE web-search / content-retrieval API storefront — Exa; test_canonical_replay
# pins its 78.1 floor) is welded here as the SEVENTH non-anchor member, and the FIRST welded member
# with GENUINE partial agent-native commerce rails. Every non-anchor member above sits at the no-rails
# floor of the transactability axis (books/api.replicate 0.0, moleskine 18.75, acuity/ipinfo 25.0) — the
# only welded point with real programmatic-payment capability was the WITH-rails anchor driftflight.com.
# exa.ai's 50.0 transactability is honestly earned by documented x402 (its llms.txt cites an
# 'x402-agentkit-free-trial' surface) + an MCP surface + self-serve PAYG — a real MIDDLE strictly between
# the no-rails floor (0.0) and the anchor's full x402-LIVE handshake (87.5). At 78.1 (legibility 100.0,
# trust 83.33) it is the SECOND-HIGHEST baseline, filling the frozen guard's widest upper-middle gap
# (nothing sat between ipinfo's 61.3 and driftflight's 85.5), so the cross-path regression signal now
# reaches the upper / with-rails scale, not just the no-rails band. It is keyed 'exa.ai' identically on
# both paths (no www/bare alias needed, unlike moleskine) and scored 78.1 in ALL FIVE committed sweeps
# (segment api-service), so it is genuinely COMPARED (n_compared=5), not silently skipped. Its
# live<->frozen agreement was verified this fire (Local cycle 20260807T194459Z, static $0 re-score): live
# overall 78.1 == frozen 78.1 and all four non-null pillars byte-identical (access 100.0 / legibility
# 100.0 / transactability 50.0 / trust 83.33), the cross-path evidence the cloud cannot produce (exa.ai
# is NOT SCORABLE without outbound network). So the cross-path weld now spans SEVEN structurally-distinct
# non-anchor witnesses: null-control + 2 retail + service-booking + data-retrieval + pure-inference-API +
# agent-native-search-API (the first with partial agent-native rails).
# thebotwire.com (86.0) / api.x402oracle.com (64.4) / x402deploy.vercel.app (73.9) are welded here as the
# EIGHTH, NINTH, and TENTH non-anchor members, and — crucially — the FIRST welded members that carry a GENUINE
# LIVE x402 handshake (every prior welded witness carries NO live rail; exa.ai's rail is documented-not-probed).
# Each is a purpose-built agent-native x402 storefront the shipped scorer probes at x402_probe 8.0/8.0 x402-live,
# so their transactability sits at or near the ceiling (thebotwire 100.0 / oracle 87.5 / x402deploy 100.0) — the
# cross-path regression signal now reaches the LIVE upper / with-rails scale on non-anchor domains, not just the
# frozen 78.1 documented-rail point exa.ai contributes. They pin three distinct capability SHAPES: thebotwire.com
# (86.0, {metered_api, data_retrieval}, the HIGHEST baseline — a hair above the driftflight.com anchor's frozen
# 85.5) maxes transactability while carrying thin trust 43.33; api.x402oracle.com (64.4, PURE {metered_api}) is
# the controlled complement of the no-rails api.replicate.com — same single archetype, opposite rail, so its
# transactability 87.5 vs api.replicate's 0.0 isolates the rail's transactability contribution, AND its 87.5 is
# the IDENTICAL shape as the with-rails anchor; x402deploy.vercel.app (73.9, {metered_api, data_retrieval}) is a
# SECOND transactability-100 witness — with tx pinned at its ceiling on BOTH thebotwire (86.0) and x402deploy
# (73.9), the overall gap is forced onto legibility + trust, the "a live rail is NECESSARY but not SUFFICIENT"
# statement (non-trivial only with >=2 same-tx points at distinct overalls). Each is keyed identically on both
# paths (no www/bare alias needed) and scored at its floor in exactly ONE committed sweep so far
# (20260808T084504Z, segment x402-live:{news-data-wire,trust-oracle,web-data-tools} — the cadence run that first
# added all three to the POPULATION; absent from every prior sweep), so each is genuinely COMPARED (n_compared=1),
# not silently skipped. Because these rails are LIVE (volatile), each member's live/frozen agreement was
# independently re-confirmed by the authoring cycle (Local cycle 20260808T094101Z, static $0 re-score: live
# 86.0 / 64.4 / 73.9 == frozen 86.0 / 64.4 / 73.9, all four non-null pillars byte-identical, caps empty), the
# cross-path evidence the cloud cannot produce (none is SCORABLE without outbound network) — and MUST be
# re-confirmed at review time, since a divergence here would be REAL live-rail drift (re-capture that member, do
# not weld it). So the cross-path weld now spans TEN structurally-distinct non-anchor witnesses: null-control +
# 2 retail + service-booking + data-retrieval + pure-inference-API + agent-native-search-API + THREE live-x402
# storefronts (the first welded members with a genuine live payment handshake).
# checkout.coffeecircle.com (57.4) is welded here as the ELEVENTH non-anchor member, and — crucially — the
# FIRST welded member on a NEW agent-native rail TYPE: the UCP (Universal Commerce Protocol) commerce-protocol
# rail, structurally distinct from every x402 / no-rail witness above. It is a REAL coffee merchant's UCP
# checkout surface: GET /.well-known/ucp answers a $0 read with a valid `dev.ucp.*` capability manifest (version
# 2026-04-08), so the shipped scorer's `x402_probe` reads `commerce-protocol-live` PARTIAL 4.0/8.0 — the MIDDLE
# rung of the commerce-protocol ladder, strictly ABOVE a no-rail retail floor (books.toscrape.com x402_probe
# FAIL 0.0) and strictly BELOW a full live-x402 handshake (thebotwire.com x402_probe PASS 8.0) — earning
# transactability 50.0 (a genuine MIDDLE between the no-rails floor 0.0 and the anchor's full handshake 87.5).
# It claims exactly {metered_api, physical_good} (an honest coffee-merchant checkout API, NO topic-word
# over-claim), keyed identically on both paths (no www/bare alias needed), and scored at its 57.4 floor in
# exactly ONE committed sweep so far (20260808T114436Z, segment ucp-live:coffee-merchant — the cadence run that
# first added it to the POPULATION; absent from every prior sweep), so it is genuinely COMPARED (n_compared=1),
# not silently skipped. Because the UCP rail is LIVE (a served manifest, volatile), its live/frozen agreement was
# independently re-confirmed by the authoring cycle (Local cycle 20260808T124101Z, static $0 re-score: live 57.4
# == frozen 57.4, all four non-null pillars byte-identical, caps empty, x402_probe partial 4.0/8.0
# commerce-protocol-live), the cross-path evidence the cloud cannot produce (it is NOT SCORABLE without outbound
# network) — and MUST be re-confirmed at review time, since a divergence here would be REAL UCP-manifest drift
# (re-capture that member, do not weld it). So the cross-path weld now spans ELEVEN structurally-distinct
# non-anchor witnesses: null-control + 2 retail + service-booking + data-retrieval + pure-inference-API +
# agent-native-search-API + THREE live-x402 storefronts + ONE live-UCP commerce-protocol storefront (the first
# welded member on a rail TYPE other than x402).
_NON_ANCHOR_WELDED = (
    "example.com",
    "books.toscrape.com",
    "acuityscheduling.com",
    "ipinfo.io",
    "api.replicate.com",
    "www.moleskine.com",
    "exa.ai",
    "thebotwire.com",
    "api.x402oracle.com",
    "x402deploy.vercel.app",
    "checkout.coffeecircle.com",
)
# Every population member welded across the offline-replay and live-sweep paths.
_WELDED_MEMBERS = _ANCHORS + _NON_ANCHOR_WELDED
_BASELINE_VERSION = "0.7"  # asserted == the replay baseline's version below (test 1)
_TOL = 0.05  # overalls are rounded to 0.1 on both paths; this catches any real move
# The documented-live-drift ledger: curated, evidenced entries recording a PERSISTENT
# live-site regression the weld must tolerate without losing teeth (see docstring).
# Loaded once as the default the weld consults; every comparison helper still takes an
# explicit `ledger` so the teeth legs drive the acceptance logic with synthetic entries.
_LEDGER_PATH = os.path.join(_REPO, "experiments", "documented_live_drift.json")


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _committed_sweeps() -> list:
    """Every committed dated sweep, oldest first, as (basename, dict) pairs."""
    out = []
    pattern = os.path.join(_REPO, "runs", "local", "calibration_sweep_*.json")
    for p in sorted(glob.glob(pattern)):
        with open(p) as fh:
            out.append((os.path.basename(p), json.load(fh)))
    return out


def _norm_domain(domain):
    """Normalize a domain key for cross-path matching: strip a single leading 'www.'.

    The offline replay baseline and the live sweeps sometimes key the SAME storefront
    differently — the replay fixture was captured as 'www.moleskine.com' while every
    calibration sweep rows it 'moleskine.com'. A leading 'www.' host alias resolves to
    the same site, so the two paths are the same measurement and must weld; without this
    the welded member would silently never compare (n_compared=0, a vacuous weld). Only a
    LEADING 'www.' (dot-terminated) is stripped — an internal 'www' label or an unrelated
    domain is untouched, so two DISTINCT storefronts are never collapsed."""
    return domain[4:] if isinstance(domain, str) and domain.startswith("www.") else domain


def _member_row(sweep: dict, domain: str):
    """The sweep row for a welded member (anchor or non-anchor), matched by domain modulo a
    leading-'www.' host alias (see _norm_domain) so a member keyed 'www.moleskine.com' in the
    replay baseline matches its 'moleskine.com' sweep row (and vice versa)."""
    target = _norm_domain(domain)
    for row in sweep.get("rows", []):
        if _norm_domain(row.get("domain")) == target:
            return row
    return None


def _load_drift_ledger(path=_LEDGER_PATH) -> list:
    """The committed documented-live-drift entries (or [] if absent/unparseable)."""
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    entries = data.get("entries", []) if isinstance(data, dict) else []
    return [e for e in entries if isinstance(e, dict)]


# The real committed ledger — the default the weld consults. None of the pre-existing
# synthetic teeth legs use any ledgered value, so defaulting to the real ledger is
# score-neutral for them; the new teeth legs pass an explicit synthetic ledger.
_LEDGER = _load_drift_ledger()


def _ledger_entry(domain, baseline_version, ledger):
    """The same-version (invariant #2) documented-drift entry for `domain`, or None."""
    for e in ledger or ():
        if e.get("domain") == domain and str(e.get("rubric_version")) == str(baseline_version):
            return e
    return None


def _accepted_overalls(domain, expected, baseline_version, ledger):
    """The overall values the weld ACCEPTS for a welded member: the frozen replay floor
    ALWAYS, plus the documented live value if this member carries a same-version ledger
    entry. A live overall matching NONE of these is a divergence — teeth: an undocumented
    value or drift PAST the documented one still fires, and a RECOVERY to the frozen floor
    is always accepted so the ledger never masks a fix."""
    accepted = [float(expected[domain]["overall"])]
    e = _ledger_entry(domain, baseline_version, ledger)
    if e is not None and e.get("overall") is not None:
        accepted.append(float(e["overall"]))
    return accepted


def _accepted_pillars(domain, expected, baseline_version, ledger):
    """Per-pillar sibling of `_accepted_overalls`: pillar -> [accepted values] (the frozen
    floor pillar ALWAYS, plus the documented pillar if ledgered). Null pillars are omitted
    (the caller null-skips them)."""
    floor = expected[domain].get("pillars", {})
    out = {p: [float(v)] for p, v in floor.items() if v is not None}
    e = _ledger_entry(domain, baseline_version, ledger)
    if e is not None:
        for p, v in (e.get("pillars") or {}).items():
            if v is not None:
                out.setdefault(p, []).append(float(v))
    return out


def _divergences(sweeps, expected, baseline_version, tol=_TOL, members=_WELDED_MEMBERS, ledger=None):
    """Pure comparison shared by the real-evidence and synthetic legs.

    Returns (divergences, n_compared, n_unreachable, n_offversion). A divergence
    is a SCORED, same-version welded MEMBER whose overall matches NEITHER the
    fixture-replay baseline NOR any same-version documented-live-drift value in
    `ledger` (within `tol`) — an undocumented regression, or drift PAST the documented
    value. Not-scorable members (invariant #4) and off-version sweeps (invariant #2)
    are COUNTED, never compared. `members` defaults to every welded member (the two
    anchors + the non-anchor members); the teeth legs pass a narrower set. `ledger`
    defaults to the real committed ledger; the teeth legs pass a synthetic one. The
    recorded divergence tuple keeps the frozen floor as `exp` (its historical shape)."""
    led = _LEDGER if ledger is None else ledger
    divergences = []
    n_compared = n_unreachable = n_offversion = 0
    for label, sweep in sweeps:
        if str(sweep.get("rubric_version")) != baseline_version:
            n_offversion += 1
            continue
        for domain in members:
            row = _member_row(sweep, domain)
            if row is None:
                continue
            if not row.get("scored") or row.get("overall") is None:
                n_unreachable += 1
                continue
            accepted = _accepted_overalls(domain, expected, baseline_version, led)
            got = float(row["overall"])
            n_compared += 1
            if all(abs(got - a) > tol for a in accepted):
                divergences.append((label, domain, got, float(expected[domain]["overall"])))
    return divergences, n_compared, n_unreachable, n_offversion


def _pillar_divergences(sweeps, expected, baseline_version, tol=_TOL, members=_WELDED_MEMBERS, ledger=None):
    """The PILLAR-level weld — the per-pillar sibling of `_divergences`.

    `_divergences` welds only the single `overall` number. But `overall` is a
    WEIGHTED SUM of pillars, so a capability-profile drift that moves two pillars
    in opposite directions (e.g. more legible, less transactable) can leave the
    weighted overall exactly where it was — passing the overall weld while the
    site's real agent-facing profile has genuinely shifted. This function welds
    each welded member's per-PILLAR scores (access/legibility/transactability/
    trust) between the offline replay baseline and the live sweeps, so such a
    cancellation goes red where the overall weld is structurally blind.

    Returns (divergences, n_compared, n_unreachable, n_offversion, n_null_skipped).
    A divergence is a (label, domain, pillar, got, exp) tuple: a SCORED,
    same-version welded member whose sweep pillar differs from the fixture-replay
    baseline pillar by more than `tol`. Attribution honesty (invariant #4): a
    pillar that is null/absent on EITHER path (e.g. `outcome`, unmeasured in
    static-replay mode) is counted `n_null_skipped` and NEVER compared — a site
    is not punished, nor credited, for a pillar a path could not observe.
    Versioned comparability (invariant #2): off-version sweeps are counted, never
    diffed. Not-scorable members (invariant #4) are counted unreachable, skipped.
    Documented drift: a ledgered member's pillar accepts the frozen floor pillar OR
    the documented pillar value (same teeth as `_divergences`, per pillar)."""
    led = _LEDGER if ledger is None else ledger
    divergences = []
    n_compared = n_unreachable = n_offversion = n_null_skipped = 0
    for label, sweep in sweeps:
        if str(sweep.get("rubric_version")) != baseline_version:
            n_offversion += 1
            continue
        for domain in members:
            row = _member_row(sweep, domain)
            if row is None:
                continue
            if not row.get("scored") or row.get("overall") is None:
                n_unreachable += 1
                continue
            exp_pillars = expected[domain].get("pillars", {})
            got_pillars = row.get("pillars", {})
            accepted_by_pillar = _accepted_pillars(domain, expected, baseline_version, led)
            for pillar in sorted(set(exp_pillars) | set(got_pillars)):
                exp_v = exp_pillars.get(pillar)
                got_v = got_pillars.get(pillar)
                if exp_v is None or got_v is None:
                    n_null_skipped += 1
                    continue
                n_compared += 1
                accepted = accepted_by_pillar.get(pillar, [float(exp_v)])
                if all(abs(float(got_v) - a) > tol for a in accepted):
                    divergences.append((label, domain, pillar, float(got_v), float(exp_v)))
    return divergences, n_compared, n_unreachable, n_offversion, n_null_skipped


def _synthetic_sweep(version, org_overall, com_overall, *, com_scored=True, example_overall=None):
    """A minimal sweep dict carrying the two anchor rows (for the teeth legs), plus
    an optional example.com non-anchor row when `example_overall` is supplied."""
    rows = [
        {
            "domain": "drift-flight.org",
            "segment": "api-storefront:no-rails-anchor",
            "scored": org_overall is not None,
            "overall": org_overall,
        },
        {
            "domain": "driftflight.com",
            "segment": "api-storefront:rails-anchor",
            "scored": com_scored and com_overall is not None,
            "overall": com_overall,
        },
    ]
    if example_overall is not None:
        rows.append(
            {
                "domain": "example.com",
                "segment": "control:non-storefront",
                "scored": True,
                "overall": example_overall,
            }
        )
    return {"rubric_version": version, "rows": rows}


def test_baseline_version_and_gap_match_replay_guard() -> None:
    print("test_baseline_version_and_gap_match_replay_guard")
    # This file's constants are NOT a second source of truth — they must equal the
    # replay guard's. If a version bump re-captures the fixtures, EXPECTED moves and
    # these assertions drag this whole guard onto the new baseline.
    for domain in _ANCHORS:
        _check(
            replay.EXPECTED[domain]["rubric_version"] == _BASELINE_VERSION,
            f"{domain} replay baseline is rubric v{_BASELINE_VERSION}",
        )
    gap = round(
        float(replay.EXPECTED["driftflight.com"]["overall"])
        - float(replay.EXPECTED["drift-flight.org"]["overall"]),
        1,
    )
    _check(
        gap == replay.EXPECTED_DELTA,
        f"replay baseline gap {gap} == EXPECTED_DELTA {replay.EXPECTED_DELTA}",
    )


def test_committed_sweeps_carry_scored_anchors() -> None:
    print("test_committed_sweeps_carry_scored_anchors")
    # Non-vacuity: without this, a future sweep that silently dropped an anchor
    # would make the agreement test pass by comparing nothing.
    sweeps = _committed_sweeps()
    _check(len(sweeps) >= 1, f"at least one committed sweep exists (got {len(sweeps)})")
    v07 = [(lbl, s) for lbl, s in sweeps if str(s.get("rubric_version")) == _BASELINE_VERSION]
    _check(len(v07) >= 1, f"at least one committed v{_BASELINE_VERSION} sweep (got {len(v07)})")
    both_scored = 0
    for lbl, sweep in v07:
        for domain in _ANCHORS:
            _check(
                _member_row(sweep, domain) is not None,
                f"{lbl} carries anchor {domain}",
            )
        rows = [_member_row(sweep, d) for d in _ANCHORS]
        if all(r.get("scored") and r.get("overall") is not None for r in rows):
            both_scored += 1
    _check(
        both_scored >= 1,
        f"at least one v{_BASELINE_VERSION} sweep has BOTH anchors scored (got {both_scored})",
    )


def test_live_sweep_anchors_agree_with_replay_baseline() -> None:
    print("test_live_sweep_anchors_agree_with_replay_baseline")
    # THE weld: every scored, same-version live welded member equals the offline
    # fixture floor (or a documented-live-drift value — driftflight.com 76.2 while the
    # x402 endpoint is regressed). Covers the two anchors AND every non-anchor welded
    # member (example.com in every sweep; books.toscrape.com in the sweeps that scored
    # it — the 20260807T045843Z sweep onward). n_compared>=2 keeps it non-vacuous
    # regardless of how many sweeps carry each member.
    sweeps = _committed_sweeps()
    divergences, n_compared, n_unreachable, n_offversion = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(
        divergences == [],
        f"no live welded member diverges from the replay floor (got {divergences})",
    )
    _check(
        n_compared >= 2,
        f"the weld is non-vacuous: >=2 (sweep, member) pairs compared (got {n_compared})",
    )
    print(
        f"  .. {n_compared} compared, {n_unreachable} not-scorable (skipped), "
        f"{n_offversion} off-version (skipped)"
    )


def test_live_sweep_gap_matches_expected_delta() -> None:
    print("test_live_sweep_gap_matches_expected_delta")
    # The reference delta seen through the LIVE population path: for every same-version
    # sweep with BOTH anchors scored, com - org equals a DOCUMENTED gap — the frozen
    # +39.4 floor delta when both anchors are at their fixture baseline, OR a gap implied
    # by a same-version documented-live-drift entry (e.g. +30.1 while the with-rails x402
    # endpoint is regressed to 76.2). Teeth: a gap matching NEITHER still fails (an
    # undocumented anchor value is already a `_divergences` divergence — this is the
    # second, gap-level witness). The frozen +39.4 must always be one of the accepted gaps.
    sweeps = _committed_sweeps()
    com_ok = _accepted_overalls("driftflight.com", replay.EXPECTED, _BASELINE_VERSION, _LEDGER)
    org_ok = _accepted_overalls("drift-flight.org", replay.EXPECTED, _BASELINE_VERSION, _LEDGER)
    documented_gaps = sorted({round(c - o, 1) for c in com_ok for o in org_ok})
    _check(
        any(abs(replay.EXPECTED_DELTA - dg) <= _TOL for dg in documented_gaps),
        f"the frozen +{replay.EXPECTED_DELTA} floor delta is a documented gap (got {documented_gaps})",
    )
    checked = 0
    for lbl, sweep in sweeps:
        if str(sweep.get("rubric_version")) != _BASELINE_VERSION:
            continue
        org = _member_row(sweep, "drift-flight.org")
        com = _member_row(sweep, "driftflight.com")
        if not (org and com and org.get("scored") and com.get("scored")):
            continue
        gap = round(float(com["overall"]) - float(org["overall"]), 1)
        _check(
            any(abs(gap - dg) <= _TOL for dg in documented_gaps),
            f"{lbl}: live gap {gap} is a documented gap {documented_gaps}",
        )
        checked += 1
    _check(checked >= 1, f"at least one live sweep had both anchors scored (got {checked})")


def test_not_scorable_anchor_is_skipped_not_a_divergence() -> None:
    print("test_not_scorable_anchor_is_skipped_not_a_divergence")
    # Invariant #4 teeth: a not-scorable anchor is a REACHABILITY gap, never a
    # divergence. A naive impl treating overall=None as 0.0 would flag an 85.5
    # divergence here; the guard must skip it.
    synth = [("synthetic-unreachable", _synthetic_sweep("0.7", 46.1, None, com_scored=False))]
    divergences, n_compared, n_unreachable, n_offversion = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(divergences == [], f"not-scorable anchor is not a divergence (got {divergences})")
    _check(n_unreachable == 1, f"the not-scorable anchor was counted unreachable (got {n_unreachable})")
    _check(n_compared == 1, f"the reachable anchor (org) was still compared (got {n_compared})")


def test_drifted_live_anchor_is_caught() -> None:
    print("test_drifted_live_anchor_is_caught")
    # Teeth: a real live re-capture that drifted the rails anchor 85.5 -> 70.0 MUST
    # trip the weld. Without this, the agreement test could be silently toothless.
    synth = [("synthetic-drift", _synthetic_sweep("0.7", 46.1, 70.0))]
    divergences, n_compared, _, _ = _divergences(synth, replay.EXPECTED, _BASELINE_VERSION)
    _check(len(divergences) == 1, f"exactly one divergence caught (got {divergences})")
    label, domain, got, exp = divergences[0]
    _check(
        domain == "driftflight.com" and abs(got - 70.0) < 1e-9 and abs(exp - 85.5) < 1e-9,
        f"the drifted rails anchor is the caught divergence (got {divergences[0]})",
    )
    _check(n_compared == 2, f"both anchors were compared (got {n_compared})")


def test_non_anchor_member_is_welded() -> None:
    print("test_non_anchor_member_is_welded")
    # The weld extends PAST the two famous anchors: each non-anchor welded member
    # (example.com, the zero-commerce baseline) is measured along the SAME two
    # independent paths — the committed offline replay baseline (guard 9 of
    # test_canonical_replay pins 22.5) and the live population sweeps — and they
    # must agree, giving the cross-path weld an independent third witness that is
    # NOT one of the anchors the whole loop already watches. Restricting `members`
    # to _NON_ANCHOR_WELDED isolates this member from the anchor coverage above.
    sweeps = _committed_sweeps()
    divergences, n_compared, n_unreachable, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=_NON_ANCHOR_WELDED
    )
    _check(
        divergences == [],
        f"no non-anchor welded member diverges from its replay floor (got {divergences})",
    )
    _check(
        n_compared >= 2,
        f"the non-anchor weld is non-vacuous: >=2 (sweep, member) pairs compared "
        f"(got {n_compared})",
    )
    # Each non-anchor welded member must actually carry a committed, same-version
    # replay baseline (the ONE source of truth the weld reads) — a member added to
    # _NON_ANCHOR_WELDED without an EXPECTED entry would KeyError in _divergences;
    # assert the coupling explicitly so a future addition is caught cleanly here.
    for domain in _NON_ANCHOR_WELDED:
        _check(
            domain in replay.EXPECTED
            and str(replay.EXPECTED[domain]["rubric_version"]) == _BASELINE_VERSION,
            f"{domain} has a committed v{_BASELINE_VERSION} replay baseline",
        )
    print(
        f"  .. {n_compared} non-anchor pairs compared, "
        f"{n_unreachable} not-scorable (skipped)"
    )


def test_drifted_non_anchor_member_is_caught() -> None:
    print("test_drifted_non_anchor_member_is_caught")
    # Teeth for the non-anchor weld: a live re-capture that drifted example.com's
    # baseline (22.5 -> 30.0) MUST trip the weld, exactly as a drifted anchor does.
    # Without this, extending the weld to a non-anchor member could be silently
    # toothless. The anchor rows carry their correct values, so ONLY the drifted
    # non-anchor member is the caught divergence.
    synth = [
        ("synthetic-nonanchor-drift", _synthetic_sweep("0.7", 46.1, 85.5, example_overall=30.0))
    ]
    divergences, n_compared, _, _ = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, members=_NON_ANCHOR_WELDED
    )
    _check(len(divergences) == 1, f"exactly one non-anchor divergence caught (got {divergences})")
    label, domain, got, exp = divergences[0]
    _check(
        domain == "example.com" and abs(got - 30.0) < 1e-9 and abs(exp - 22.5) < 1e-9,
        f"the drifted non-anchor member is the caught divergence (got {divergences[0]})",
    )
    _check(n_compared == 1, f"the one non-anchor member was compared (got {n_compared})")


def test_books_toscrape_second_non_anchor_is_welded_nonvacuously() -> None:
    print("test_books_toscrape_second_non_anchor_is_welded_nonvacuously")
    # books.toscrape.com is the SECOND non-anchor welded member (a real retail catalog —
    # the inverse storefront type from the API anchors). Prove the weld is LOAD-BEARING
    # for it specifically, not silently skipped in every sweep: it carries a committed
    # v0.7 replay baseline, it is genuinely COMPARED in >=1 committed sweep (the
    # 20260807T045843Z cadence run scored it 29.5), and its live value agrees with the
    # frozen floor. Its live↔frozen agreement was independently re-scored this fire
    # (Local cycle 20260807T064228Z: live 29.5 == frozen 29.5, all pillars byte-identical).
    _check(
        "books.toscrape.com" in _NON_ANCHOR_WELDED,
        "books.toscrape.com is a welded non-anchor member",
    )
    _check(
        "books.toscrape.com" in replay.EXPECTED
        and str(replay.EXPECTED["books.toscrape.com"]["rubric_version"]) == _BASELINE_VERSION,
        "books.toscrape.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("books.toscrape.com",)
    )
    _check(
        divergences == [],
        f"books.toscrape.com's live sweeps agree with its 29.5 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"books.toscrape.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted books.toscrape.com 29.5 -> 40.0 MUST trip the
    # weld, exactly as a drifted anchor or example.com does — so welding this second
    # non-anchor member is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "books.toscrape.com",
                "segment": "retail-catalog:non-anchor",
                "scored": True,
                "overall": 40.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-books-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("books.toscrape.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "books.toscrape.com"
        and abs(dvg[0][2] - 40.0) < 1e-9
        and abs(dvg[0][3] - 29.5) < 1e-9,
        f"the drifted books.toscrape.com is caught vs its 29.5 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_acuity_third_non_anchor_is_welded_nonvacuously() -> None:
    print("test_acuity_third_non_anchor_is_welded_nonvacuously")
    # acuityscheduling.com is the THIRD non-anchor welded member (a real service-booking
    # appointment-scheduling SaaS — a structurally-distinct storefront TYPE from both the
    # API anchors AND the retail catalog). Prove the weld is LOAD-BEARING for it
    # specifically, not silently skipped in every sweep: it carries a committed v0.7 replay
    # baseline, it is genuinely COMPARED in >=1 committed sweep (three cadence runs scored
    # it 54.0), and its live value agrees with the frozen floor. Its live↔frozen agreement
    # was independently re-scored this fire (Local cycle 20260807T084355Z: live 54.0 ==
    # frozen 54.0, all four non-null pillars byte-identical).
    _check(
        "acuityscheduling.com" in _NON_ANCHOR_WELDED,
        "acuityscheduling.com is a welded non-anchor member",
    )
    _check(
        "acuityscheduling.com" in replay.EXPECTED
        and str(replay.EXPECTED["acuityscheduling.com"]["rubric_version"]) == _BASELINE_VERSION,
        "acuityscheduling.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("acuityscheduling.com",)
    )
    _check(
        divergences == [],
        f"acuityscheduling.com's live sweeps agree with its 54.0 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"acuityscheduling.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted acuityscheduling.com 54.0 -> 65.0 MUST trip the
    # weld, exactly as a drifted anchor, example.com, or books.toscrape.com does — so
    # welding this third non-anchor member is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "acuityscheduling.com",
                "segment": "service-booking:saas",
                "scored": True,
                "overall": 65.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-acuity-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("acuityscheduling.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "acuityscheduling.com"
        and abs(dvg[0][2] - 65.0) < 1e-9
        and abs(dvg[0][3] - 54.0) < 1e-9,
        f"the drifted acuityscheduling.com is caught vs its 54.0 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_ipinfo_fourth_non_anchor_is_welded_nonvacuously() -> None:
    print("test_ipinfo_fourth_non_anchor_is_welded_nonvacuously")
    # ipinfo.io is the FOURTH non-anchor welded member (a real data-retrieval / IP-data
    # enrichment API storefront — a structurally-distinct storefront TYPE from the two API
    # anchors, the retail catalog, the zero-commerce control, AND the service-booking SaaS).
    # Prove the weld is LOAD-BEARING for it specifically, not silently skipped in every
    # sweep: it carries a committed v0.7 replay baseline, it is genuinely COMPARED in >=1
    # committed sweep (three cadence runs scored it 61.3), and its live value agrees with
    # the frozen floor. Its live↔frozen agreement was independently re-scored this fire
    # (Local cycle 20260807T104102Z: live 61.3 == frozen 61.3, all four non-null pillars
    # byte-identical).
    _check(
        "ipinfo.io" in _NON_ANCHOR_WELDED,
        "ipinfo.io is a welded non-anchor member",
    )
    _check(
        "ipinfo.io" in replay.EXPECTED
        and str(replay.EXPECTED["ipinfo.io"]["rubric_version"]) == _BASELINE_VERSION,
        "ipinfo.io carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("ipinfo.io",)
    )
    _check(
        divergences == [],
        f"ipinfo.io's live sweeps agree with its 61.3 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"ipinfo.io is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted ipinfo.io 61.3 -> 72.0 MUST trip the weld,
    # exactly as a drifted anchor, example.com, books.toscrape.com, or acuityscheduling.com
    # does — so welding this fourth non-anchor member is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "ipinfo.io",
                "segment": "data-retrieval:api",
                "scored": True,
                "overall": 72.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-ipinfo-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("ipinfo.io",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "ipinfo.io"
        and abs(dvg[0][2] - 72.0) < 1e-9
        and abs(dvg[0][3] - 61.3) < 1e-9,
        f"the drifted ipinfo.io is caught vs its 61.3 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_api_replicate_fifth_non_anchor_is_welded_nonvacuously() -> None:
    print("test_api_replicate_fifth_non_anchor_is_welded_nonvacuously")
    # api.replicate.com is the FIFTH non-anchor welded member (a real PURE single-archetype
    # metered_api compute / model-inference API storefront — a structurally-distinct storefront
    # TYPE from the two multi-archetype API anchors, the retail catalog, the zero-commerce
    # control, the service-booking SaaS, AND the data-retrieval API). Prove the weld is
    # LOAD-BEARING for it specifically, not silently skipped in every sweep: it carries a
    # committed v0.7 replay baseline, it is genuinely COMPARED in >=1 committed sweep (the
    # 20260807T134527Z cadence run — the first to add it to the POPULATION — scored it 29.5),
    # and its live value agrees with the frozen floor. Its live↔frozen agreement was
    # independently re-scored this fire (Local cycle 20260807T144105Z: live 29.5 == frozen 29.5,
    # all four non-null pillars byte-identical).
    _check(
        "api.replicate.com" in _NON_ANCHOR_WELDED,
        "api.replicate.com is a welded non-anchor member",
    )
    _check(
        "api.replicate.com" in replay.EXPECTED
        and str(replay.EXPECTED["api.replicate.com"]["rubric_version"]) == _BASELINE_VERSION,
        "api.replicate.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("api.replicate.com",)
    )
    _check(
        divergences == [],
        f"api.replicate.com's live sweeps agree with its 29.5 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"api.replicate.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted api.replicate.com 29.5 -> 40.0 MUST trip the weld,
    # exactly as a drifted anchor, example.com, books.toscrape.com, acuityscheduling.com, or
    # ipinfo.io does — so welding this fifth non-anchor member is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "api.replicate.com",
                "segment": "metered-api:inference-platform",
                "scored": True,
                "overall": 40.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-api-replicate-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("api.replicate.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "api.replicate.com"
        and abs(dvg[0][2] - 40.0) < 1e-9
        and abs(dvg[0][3] - 29.5) < 1e-9,
        f"the drifted api.replicate.com is caught vs its 29.5 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_moleskine_sixth_non_anchor_is_welded_nonvacuously() -> None:
    print("test_moleskine_sixth_non_anchor_is_welded_nonvacuously")
    # www.moleskine.com is the SIXTH non-anchor welded member (a SECOND real RETAIL
    # storefront — an established consumer-brand e-commerce shop). It adds retail DEPTH,
    # not a new storefront TYPE: it earns real legibility 40.91 + PARTIAL transactability
    # 18.75 (a real commerce surface, no agent-native rail) + high trust 73.33, a DIFFERENT
    # pillar mix at a DIFFERENT overall than books.toscrape.com's 29.5, so the two retail
    # members pin a RANGE 29.5 -> 49.8, not a point; 49.8 is a new distinct datapoint between
    # example.com's 22.5 and acuityscheduling.com's 54.0.
    #
    # This member exercises the www/bare host-alias normalization (see _norm_domain): the
    # offline replay baseline keys it 'www.moleskine.com' while every live sweep rows it
    # 'moleskine.com'. Both are the same storefront; the weld matches them modulo the leading
    # 'www.', so this member is genuinely COMPARED rather than silently skipped. Prove the
    # weld is LOAD-BEARING for it specifically: it carries a committed v0.7 replay baseline,
    # it is genuinely COMPARED in >=1 committed sweep (all five cadence runs scored
    # moleskine.com 49.8, segment retail:no-rails), and its live value agrees with the frozen
    # floor. Its live<->frozen agreement was independently re-scored this fire (Local cycle
    # 20260807T174235Z: live overall 49.8 == frozen 49.8, all four non-null pillars
    # byte-identical), the cross-path evidence the cloud cannot produce (www.moleskine.com is
    # NOT SCORABLE without outbound network).
    _check(
        "www.moleskine.com" in _NON_ANCHOR_WELDED,
        "www.moleskine.com is a welded non-anchor member",
    )
    _check(
        "www.moleskine.com" in replay.EXPECTED
        and str(replay.EXPECTED["www.moleskine.com"]["rubric_version"]) == _BASELINE_VERSION,
        "www.moleskine.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    # The www/bare normalization is what makes this member non-vacuous: the sweeps key it
    # 'moleskine.com', so without _norm_domain the member 'www.moleskine.com' would match no
    # row. Assert the alias actually resolves to a bare-keyed sweep row.
    sweeps = _committed_sweeps()
    resolved = [
        _member_row(s, "www.moleskine.com") for _, s in sweeps
        if _member_row(s, "www.moleskine.com") is not None
    ]
    _check(
        len(resolved) >= 1 and all(r.get("domain") == "moleskine.com" for r in resolved),
        f"the 'www.moleskine.com' member resolves to bare-'moleskine.com' sweep rows via "
        f"_norm_domain (got {len(resolved)} resolved)",
    )
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("www.moleskine.com",)
    )
    _check(
        divergences == [],
        f"www.moleskine.com's live sweeps agree with its 49.8 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"www.moleskine.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted moleskine 49.8 -> 60.0 MUST trip the weld,
    # exactly as a drifted anchor or any prior non-anchor member does — welding this sixth
    # member is not toothless. The drift row is keyed 'moleskine.com' (as the real sweeps
    # are), so this also proves the teeth fire THROUGH the www/bare normalization.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "moleskine.com",
                "segment": "retail:no-rails",
                "scored": True,
                "overall": 60.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-moleskine-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("www.moleskine.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "www.moleskine.com"
        and abs(dvg[0][2] - 60.0) < 1e-9
        and abs(dvg[0][3] - 49.8) < 1e-9,
        f"the drifted moleskine is caught vs its 49.8 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_exa_ai_seventh_non_anchor_is_welded_nonvacuously() -> None:
    print("test_exa_ai_seventh_non_anchor_is_welded_nonvacuously")
    # exa.ai is the SEVENTH non-anchor welded member (a real AGENT-NATIVE web-search /
    # content-retrieval API — Exa), and the FIRST welded member with GENUINE partial
    # agent-native commerce rails: documented x402 (llms.txt 'x402-agentkit-free-trial')
    # + an MCP surface + self-serve PAYG earn transactability 50.0 — a real MIDDLE strictly
    # between the no-rails floor (0.0) and the anchor's full x402-LIVE handshake (87.5).
    # At 78.1 it is the second-highest baseline, so the cross-path regression signal now
    # reaches the upper / with-rails scale, not just the no-rails band every prior non-anchor
    # member sat in. Prove the weld is LOAD-BEARING for it specifically, not silently skipped
    # in every sweep: it carries a committed v0.7 replay baseline, it is genuinely COMPARED in
    # >=1 committed sweep (all five cadence runs scored it 78.1, segment api-service, keyed
    # 'exa.ai' identically on both paths — no www/bare alias needed), and its live value agrees
    # with the frozen floor. Its live↔frozen agreement was independently re-scored this fire
    # (Local cycle 20260807T194459Z, static $0: live 78.1 == frozen 78.1, all four non-null
    # pillars byte-identical), the cross-path evidence the cloud cannot produce (exa.ai is NOT
    # SCORABLE without outbound network).
    _check(
        "exa.ai" in _NON_ANCHOR_WELDED,
        "exa.ai is a welded non-anchor member",
    )
    _check(
        "exa.ai" in replay.EXPECTED
        and str(replay.EXPECTED["exa.ai"]["rubric_version"]) == _BASELINE_VERSION,
        "exa.ai carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("exa.ai",)
    )
    _check(
        divergences == [],
        f"exa.ai's live sweeps agree with its 78.1 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"exa.ai is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted exa.ai 78.1 -> 90.0 MUST trip the weld, exactly as
    # a drifted anchor or any prior non-anchor member does — so welding this seventh member (the
    # first on the upper / with-rails scale) is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "exa.ai",
                "segment": "api-service",
                "scored": True,
                "overall": 90.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-exa-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("exa.ai",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "exa.ai"
        and abs(dvg[0][2] - 90.0) < 1e-9
        and abs(dvg[0][3] - 78.1) < 1e-9,
        f"the drifted exa.ai is caught vs its 78.1 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_thebotwire_eighth_non_anchor_is_welded_nonvacuously() -> None:
    print("test_thebotwire_eighth_non_anchor_is_welded_nonvacuously")
    # thebotwire.com is the EIGHTH non-anchor welded member (a purpose-built agent-native
    # x402 news/data storefront — {metered_api, data_retrieval}), and the FIRST welded member
    # with a GENUINE LIVE x402 handshake: the shipped scorer probes it at x402_probe 8.0/8.0
    # x402-live, so its transactability sits at the 100.0 ceiling and its 86.0 is the HIGHEST
    # baseline (a hair above the driftflight.com anchor's frozen 85.5). Every prior welded
    # witness sits below on the transactability axis (exa.ai's rail is documented-not-probed,
    # 50.0; all others no-rails), so this member pushes the cross-path regression signal onto
    # the LIVE upper / with-rails scale for the first time on a non-anchor domain. Prove the
    # weld is LOAD-BEARING for it specifically, not silently skipped in every sweep: it carries
    # a committed v0.7 replay baseline, it is genuinely COMPARED in >=1 committed sweep (the
    # 20260808T084504Z cadence run — the first to add it to the POPULATION — scored it 86.0,
    # segment x402-live:news-data-wire), and its live value agrees with the frozen floor. Because
    # its rail is LIVE (volatile), its live<->frozen agreement was independently re-confirmed by
    # the authoring cycle (Local cycle 20260808T094101Z, static $0: live 86.0 == frozen 86.0, all
    # four non-null pillars byte-identical, caps empty) — a divergence here at review time would be
    # REAL live-rail drift, not a code regression.
    _check(
        "thebotwire.com" in _NON_ANCHOR_WELDED,
        "thebotwire.com is a welded non-anchor member",
    )
    _check(
        "thebotwire.com" in replay.EXPECTED
        and str(replay.EXPECTED["thebotwire.com"]["rubric_version"]) == _BASELINE_VERSION,
        "thebotwire.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("thebotwire.com",)
    )
    _check(
        divergences == [],
        f"thebotwire.com's live sweeps agree with its 86.0 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"thebotwire.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted thebotwire.com 86.0 -> 95.0 MUST trip the weld,
    # exactly as a drifted anchor or any prior non-anchor member does — so welding this eighth
    # member (the first on the LIVE with-rails scale) is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "thebotwire.com",
                "segment": "x402-live:news-data-wire",
                "scored": True,
                "overall": 95.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-thebotwire-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("thebotwire.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "thebotwire.com"
        and abs(dvg[0][2] - 95.0) < 1e-9
        and abs(dvg[0][3] - 86.0) < 1e-9,
        f"the drifted thebotwire.com is caught vs its 86.0 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_x402oracle_ninth_non_anchor_is_welded_nonvacuously() -> None:
    print("test_x402oracle_ninth_non_anchor_is_welded_nonvacuously")
    # api.x402oracle.com is the NINTH non-anchor welded member (a PURE single-archetype
    # {metered_api} x402 "trust oracle" gateway) and the SECOND welded member with a GENUINE
    # LIVE x402 handshake (x402_probe 8.0/8.0 x402-live). Its calibration value is a controlled
    # complement: it shares the pure-{metered_api} archetype with the no-rails api.replicate.com
    # (the FIFTH welded member) but carries the OPPOSITE rail, so its transactability 87.5 vs
    # api.replicate's 0.0 isolates the rail's transactability contribution against a fixed archetype
    # — AND its 87.5 is the IDENTICAL transactability shape as the with-rails anchor driftflight.com.
    # Prove the weld is LOAD-BEARING for it specifically, not silently skipped in every sweep: it
    # carries a committed v0.7 replay baseline, it is genuinely COMPARED in >=1 committed sweep (the
    # 20260808T084504Z cadence run scored it 64.4, segment x402-live:trust-oracle), and its live
    # value agrees with the frozen floor. Because its rail is LIVE (volatile), its live<->frozen
    # agreement was independently re-confirmed by the authoring cycle (Local cycle 20260808T094101Z,
    # static $0: live 64.4 == frozen 64.4, all four non-null pillars byte-identical, caps empty) — a
    # divergence here at review time would be REAL live-rail drift, not a code regression.
    _check(
        "api.x402oracle.com" in _NON_ANCHOR_WELDED,
        "api.x402oracle.com is a welded non-anchor member",
    )
    _check(
        "api.x402oracle.com" in replay.EXPECTED
        and str(replay.EXPECTED["api.x402oracle.com"]["rubric_version"]) == _BASELINE_VERSION,
        "api.x402oracle.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("api.x402oracle.com",)
    )
    _check(
        divergences == [],
        f"api.x402oracle.com's live sweeps agree with its 64.4 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"api.x402oracle.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted api.x402oracle.com 64.4 -> 75.0 MUST trip the weld,
    # exactly as a drifted anchor or any prior non-anchor member does — so welding this ninth
    # member is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "api.x402oracle.com",
                "segment": "x402-live:trust-oracle",
                "scored": True,
                "overall": 75.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-x402oracle-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("api.x402oracle.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "api.x402oracle.com"
        and abs(dvg[0][2] - 75.0) < 1e-9
        and abs(dvg[0][3] - 64.4) < 1e-9,
        f"the drifted api.x402oracle.com is caught vs its 64.4 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_x402deploy_tenth_non_anchor_is_welded_nonvacuously() -> None:
    print("test_x402deploy_tenth_non_anchor_is_welded_nonvacuously")
    # x402deploy.vercel.app is the TENTH non-anchor welded member (a purpose-built agent-native
    # x402 "Web & Data Tools" gateway — {metered_api, data_retrieval}) and the THIRD welded member
    # with a GENUINE LIVE x402 handshake (x402_probe 8.0/8.0 x402-live). Its calibration value is a
    # SECOND transactability-100 witness: with transactability pinned at its 100.0 ceiling on BOTH
    # thebotwire.com (86.0) and x402deploy.vercel.app (73.9), the overall gap between them is forced
    # entirely onto legibility (45.45 vs 86.36) + trust (33.33 vs 43.33) — the "a live rail is
    # NECESSARY but not SUFFICIENT" statement, which is non-trivial only with >=2 same-tx points at
    # distinct overalls. Prove the weld is LOAD-BEARING for it specifically, not silently skipped in
    # every sweep: it carries a committed v0.7 replay baseline, it is genuinely COMPARED in >=1
    # committed sweep (the 20260808T084504Z cadence run scored it 73.9, segment
    # x402-live:web-data-tools), and its live value agrees with the frozen floor. Because its rail is
    # LIVE (volatile), its live<->frozen agreement was independently re-confirmed by the authoring
    # cycle (Local cycle 20260808T094101Z, static $0: live 73.9 == frozen 73.9, all four non-null
    # pillars byte-identical, caps empty) — a divergence here at review time would be REAL live-rail
    # drift, not a code regression.
    _check(
        "x402deploy.vercel.app" in _NON_ANCHOR_WELDED,
        "x402deploy.vercel.app is a welded non-anchor member",
    )
    _check(
        "x402deploy.vercel.app" in replay.EXPECTED
        and str(replay.EXPECTED["x402deploy.vercel.app"]["rubric_version"]) == _BASELINE_VERSION,
        "x402deploy.vercel.app carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("x402deploy.vercel.app",)
    )
    _check(
        divergences == [],
        f"x402deploy.vercel.app's live sweeps agree with its 73.9 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"x402deploy.vercel.app is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted x402deploy.vercel.app 73.9 -> 85.0 MUST trip the weld,
    # exactly as a drifted anchor or any prior non-anchor member does — so welding this tenth member
    # is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "x402deploy.vercel.app",
                "segment": "x402-live:web-data-tools",
                "scored": True,
                "overall": 85.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-x402deploy-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("x402deploy.vercel.app",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "x402deploy.vercel.app"
        and abs(dvg[0][2] - 85.0) < 1e-9
        and abs(dvg[0][3] - 73.9) < 1e-9,
        f"the drifted x402deploy.vercel.app is caught vs its 73.9 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_coffeecircle_eleventh_non_anchor_is_welded_nonvacuously() -> None:
    print("test_coffeecircle_eleventh_non_anchor_is_welded_nonvacuously")
    # checkout.coffeecircle.com is the ELEVENTH non-anchor welded member (a REAL coffee merchant's
    # UCP checkout surface — {metered_api, physical_good}) and the FIRST welded member on a NEW
    # agent-native rail TYPE: the UCP (Universal Commerce Protocol) commerce-protocol rail, distinct
    # from every x402 / no-rail witness. GET /.well-known/ucp answers a $0 read with a valid dev.ucp.*
    # manifest, so the shipped scorer's x402_probe reads `commerce-protocol-live` PARTIAL 4.0/8.0 — the
    # MIDDLE rung of the commerce-protocol ladder, earning transactability 50.0, strictly above the
    # no-rail retail floor (books.toscrape.com x402_probe 0.0) and strictly below a full live-x402
    # handshake (thebotwire.com x402_probe 8.0). Prove the weld is LOAD-BEARING for it specifically, not
    # silently skipped in every sweep: it carries a committed v0.7 replay baseline, it is genuinely
    # COMPARED in >=1 committed sweep (the 20260808T114436Z cadence run scored it 57.4, segment
    # ucp-live:coffee-merchant), and its live value agrees with the frozen floor. Because its rail is
    # LIVE (volatile), its live<->frozen agreement was independently re-confirmed by the authoring cycle
    # (Local cycle 20260808T124101Z, static $0: live 57.4 == frozen 57.4, all four non-null pillars
    # byte-identical, caps empty, x402_probe partial 4.0/8.0 commerce-protocol-live) — a divergence here
    # at review time would be REAL UCP-manifest drift, not a code regression.
    _check(
        "checkout.coffeecircle.com" in _NON_ANCHOR_WELDED,
        "checkout.coffeecircle.com is a welded non-anchor member",
    )
    _check(
        "checkout.coffeecircle.com" in replay.EXPECTED
        and str(replay.EXPECTED["checkout.coffeecircle.com"]["rubric_version"]) == _BASELINE_VERSION,
        "checkout.coffeecircle.com carries a committed v0.7 replay baseline (the weld's source of truth)",
    )
    sweeps = _committed_sweeps()
    divergences, n_compared, _, _ = _divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION, members=("checkout.coffeecircle.com",)
    )
    _check(
        divergences == [],
        f"checkout.coffeecircle.com's live sweeps agree with its 57.4 replay floor (got {divergences})",
    )
    _check(
        n_compared >= 1,
        f"checkout.coffeecircle.com is genuinely compared, not silently skipped (got {n_compared})",
    )
    # Teeth: a live re-capture that drifted checkout.coffeecircle.com 57.4 -> 68.0 (e.g. the UCP manifest
    # upgrading commerce-protocol-live PARTIAL -> a full handshake) MUST trip the weld, exactly as a
    # drifted anchor or any prior non-anchor member does — so welding this eleventh member is not toothless.
    drifted = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "checkout.coffeecircle.com",
                "segment": "ucp-live:coffee-merchant",
                "scored": True,
                "overall": 68.0,
            }
        ],
    }
    dvg, n_cmp, _, _ = _divergences(
        [("synthetic-coffeecircle-drift", drifted)], replay.EXPECTED, _BASELINE_VERSION,
        members=("checkout.coffeecircle.com",),
    )
    _check(len(dvg) == 1, f"exactly one divergence caught (got {dvg})")
    _check(
        dvg[0][1] == "checkout.coffeecircle.com"
        and abs(dvg[0][2] - 68.0) < 1e-9
        and abs(dvg[0][3] - 57.4) < 1e-9,
        f"the drifted checkout.coffeecircle.com is caught vs its 57.4 floor (got {dvg[0]})",
    )
    _check(n_cmp == 1, f"the one member was compared (got {n_cmp})")


def test_www_bare_domain_key_is_normalized() -> None:
    print("test_www_bare_domain_key_is_normalized")
    # _member_row matches a welded member to its sweep row modulo a single leading 'www.'
    # host alias, so the offline replay baseline (keyed 'www.moleskine.com') and the live
    # sweeps (keyed 'moleskine.com') weld as the same storefront. Prove the normalization is
    # correct in BOTH directions and does NOT over-normalize — a different domain, or an
    # internal 'www' label, is never collapsed (attribution honesty: two DISTINCT storefronts
    # must never weld as one).
    sweep = {
        "rubric_version": "0.7",
        "rows": [
            {"domain": "moleskine.com", "segment": "retail:no-rails", "scored": True, "overall": 49.8},
            {"domain": "example.com", "segment": "control:non-storefront", "scored": True, "overall": 22.5},
        ],
    }
    # A 'www.'-prefixed member key finds the bare sweep row ...
    r = _member_row(sweep, "www.moleskine.com")
    _check(
        r is not None and r["domain"] == "moleskine.com",
        "a 'www.'-prefixed member key matches its bare sweep row",
    )
    # ... and a bare member key finds a 'www.'-prefixed sweep row (the mirror direction).
    www_sweep = {
        "rubric_version": "0.7",
        "rows": [
            {"domain": "www.moleskine.com", "segment": "retail:no-rails", "scored": True, "overall": 49.8}
        ],
    }
    r2 = _member_row(www_sweep, "moleskine.com")
    _check(
        r2 is not None and r2["domain"] == "www.moleskine.com",
        "a bare member key matches a 'www.'-prefixed sweep row",
    )
    # No over-normalization: an unrelated domain never matches ...
    _check(
        _member_row(sweep, "www.example.org") is None,
        "an unrelated 'www.'-prefixed member matches nothing (no false collapse)",
    )
    # ... and only a LEADING, dot-terminated 'www.' is stripped.
    _check(
        _norm_domain("wwwx.moleskine.com") == "wwwx.moleskine.com",
        "only a leading 'www.' (dot-terminated) is stripped, not a 'wwwx' prefix",
    )
    _check(
        _norm_domain("api.www.example.com") == "api.www.example.com",
        "an internal 'www' label is never stripped",
    )
    _check(
        _norm_domain("moleskine.com") == "moleskine.com" and _norm_domain("ipinfo.io") == "ipinfo.io",
        "a bare domain is unchanged (identity)",
    )


def test_off_version_sweep_is_not_compared() -> None:
    print("test_off_version_sweep_is_not_compared")
    # Invariant #2 teeth: a different-rubric sweep is never diffed against the v0.7
    # floor, even with a wildly wrong anchor overall. Scores compare within a
    # version only.
    synth = [("synthetic-v0.8", _synthetic_sweep("0.8", 999.0, 999.0))]
    divergences, n_compared, n_unreachable, n_offversion = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(divergences == [], f"off-version sweep yields no divergence (got {divergences})")
    _check(n_compared == 0, f"off-version anchors were not compared (got {n_compared})")
    _check(n_offversion == 1, f"the off-version sweep was counted, not diffed (got {n_offversion})")


def test_live_sweep_pillars_agree_with_replay_baseline() -> None:
    print("test_live_sweep_pillars_agree_with_replay_baseline")
    # THE pillar weld on real evidence: every scored, same-version welded member's
    # per-pillar scores equal the offline fixture floor (or a documented pillar value).
    # Covers the two anchors AND the non-anchor members (example.com in every sweep,
    # books.toscrape.com in the sweeps that scored it) across 4 non-null pillars per
    # member (outcome is null in static mode → skipped). n_compared>=8 keeps it
    # non-vacuous even if a sweep drops a member.
    sweeps = _committed_sweeps()
    divergences, n_compared, n_unreachable, n_offversion, n_null = _pillar_divergences(
        sweeps, replay.EXPECTED, _BASELINE_VERSION
    )
    _check(
        divergences == [],
        f"no live welded member's pillar diverges from the replay floor (got {divergences})",
    )
    _check(
        n_compared >= 8,
        f"the pillar weld is non-vacuous: >=8 pillar comparisons (got {n_compared})",
    )
    print(
        f"  .. {n_compared} pillar comparisons, {n_unreachable} not-scorable (skipped), "
        f"{n_null} null-pillar (skipped), {n_offversion} off-version (skipped)"
    )


def test_pillar_canceling_drift_passes_overall_but_is_caught_by_pillar_weld() -> None:
    print("test_pillar_canceling_drift_passes_overall_but_is_caught_by_pillar_weld")
    # THE reason the pillar weld exists. `overall` is a weighted sum of pillars, so
    # a capability-profile drift that moves two pillars in opposite directions can
    # leave the weighted overall exactly on its floor. Take drift-flight.org and
    # shift legibility +6.0 and transactability -4.0. With the outcome-null
    # renormalized weights (rubric v0.7: access .15 legibility .20 transactability
    # .30 trust .15, outcome .20 dropped → /.80), the weighted overall change is
    #   (.20*(+6.0) + .30*(-4.0)) / .80 = (1.2 - 1.2) / .80 = 0.0
    # → the overall stays on the 46.1 floor while the site got genuinely MORE
    # legible and LESS transactable. The overall weld is blind to this; the pillar
    # weld must catch exactly those two pillars.
    base = replay.EXPECTED["drift-flight.org"]["pillars"]
    drifted = dict(base)
    drifted["legibility"] = base["legibility"] + 6.0
    drifted["transactability"] = base["transactability"] - 4.0

    # Prove the synthetic is PHYSICALLY realizable, not a hand-set number: recompute
    # the weighted overall from the drifted pillars with the same outcome-dropped
    # renormalized weights (no scoring-path import — the guard stays pure). It must
    # still round to the 46.1 floor, so a REAL sweep could land exactly here while
    # two pillars genuinely moved.
    weights = {"access": 0.15, "legibility": 0.20, "transactability": 0.30, "trust": 0.15}
    wsum = sum(weights.values())
    recomputed = round(sum(weights[k] * drifted[k] for k in weights) / wsum, 1)
    _check(
        recomputed == 46.1,
        f"the drifted pillars still weight to the 46.1 overall floor (got {recomputed})",
    )

    sweep = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "drift-flight.org",
                "segment": "api-storefront:no-rails-anchor",
                "scored": True,
                "overall": 46.1,  # genuinely on-floor, per the recompute above
                "pillars": drifted,
            }
        ],
    }
    synth = [("synthetic-pillar-cancel", sweep)]

    # The OVERALL weld is structurally blind — overall is byte-equal to the floor.
    odiv, _, _, _ = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, members=("drift-flight.org",)
    )
    _check(
        odiv == [],
        f"the overall weld does NOT catch a pillar-canceling drift (got {odiv})",
    )
    # The PILLAR weld catches exactly the two drifted pillars.
    pdiv, n_cmp, _, _, _ = _pillar_divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, members=("drift-flight.org",)
    )
    caught = sorted(d[2] for d in pdiv)
    _check(
        caught == ["legibility", "transactability"],
        f"the pillar weld catches exactly the two drifted pillars (got {caught})",
    )
    _check(n_cmp == 4, f"the 4 non-null org pillars were compared (got {n_cmp})")


def test_null_pillar_is_skipped_not_a_divergence() -> None:
    print("test_null_pillar_is_skipped_not_a_divergence")
    # Invariant #4 teeth for the pillar weld: the `outcome` pillar is null in
    # static-replay mode on the baseline path. A live behavioral sweep that DID
    # measure outcome must not be diffed against a floor that never observed it —
    # a naive impl coercing None→0.0 would flag a huge divergence. The guard skips
    # it (counts it null-skipped), comparing only the pillars observed on BOTH
    # paths.
    base = replay.EXPECTED["drift-flight.org"]["pillars"]
    _check(base.get("outcome") is None, "precondition: the org baseline outcome pillar is null")
    measured = dict(base)
    measured["outcome"] = 88.0  # a value where the baseline has none
    sweep = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "drift-flight.org",
                "segment": "api-storefront:no-rails-anchor",
                "scored": True,
                "overall": 46.1,
                "pillars": measured,
            }
        ],
    }
    synth = [("synthetic-null-pillar", sweep)]
    pdiv, n_cmp, _, _, n_null = _pillar_divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, members=("drift-flight.org",)
    )
    _check(
        pdiv == [],
        f"a pillar null on the baseline path is skipped, not a divergence (got {pdiv})",
    )
    _check(n_null >= 1, f"the null baseline pillar was counted null-skipped (got {n_null})")
    _check(n_cmp == 4, f"the 4 shared non-null pillars were still compared (got {n_cmp})")


# A synthetic ledger for the teeth legs below — isolates the acceptance LOGIC from the
# committed ledger's exact contents. Mirrors the real driftflight.com x402-regression
# entry (overall 76.2, transactability 62.5, other pillars = frozen floor).
_SYNTH_LEDGER = [
    {
        "domain": "driftflight.com",
        "rubric_version": "0.7",
        "overall": 76.2,
        "pillars": {
            "access": 100.0,
            "legibility": 90.9090909090909,
            "transactability": 62.5,
            "trust": 60.0,
            "outcome": None,
        },
    }
]


def test_documented_drift_is_accepted_not_a_divergence() -> None:
    print("test_documented_drift_is_accepted_not_a_divergence")
    # A live sweep at the DOCUMENTED value (driftflight.com 76.2, per a same-version
    # ledger entry) is NOT a divergence — the weld tolerates a documented, evidenced live
    # regression while the frozen fixture stays 85.5 (invariant #2). The ledger is
    # LOAD-BEARING: with an EMPTY ledger the SAME sweep goes red, so a documented drift is
    # never a silent free pass.
    synth = [("synthetic-documented", _synthetic_sweep("0.7", 46.1, 76.2))]
    div_led, n_cmp, _, _ = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, ledger=_SYNTH_LEDGER
    )
    _check(div_led == [], f"the documented 76.2 drift is accepted, not a divergence (got {div_led})")
    _check(n_cmp == 2, f"both anchors were compared (got {n_cmp})")
    div_none, _, _, _ = _divergences(synth, replay.EXPECTED, _BASELINE_VERSION, ledger=[])
    _check(
        len(div_none) == 1 and div_none[0][1] == "driftflight.com",
        f"with NO ledger the same 76.2 sweep IS a divergence — the ledger is load-bearing (got {div_none})",
    )


def test_drift_past_documented_value_is_caught() -> None:
    print("test_drift_past_documented_value_is_caught")
    # Teeth: a live value that is NEITHER the frozen floor (85.5) NOR the documented drift
    # (76.2) — here 60.0, a FURTHER regression past the documented one — still goes red even
    # with the ledger active. The ledger accepts EXACTLY the documented value, never a band.
    synth = [("synthetic-further-drift", _synthetic_sweep("0.7", 46.1, 60.0))]
    div, n_cmp, _, _ = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, ledger=_SYNTH_LEDGER
    )
    _check(len(div) == 1, f"exactly one divergence caught (got {div})")
    _check(
        div[0][1] == "driftflight.com" and abs(div[0][2] - 60.0) < 1e-9,
        f"the further-drifted anchor is the caught divergence (got {div[0]})",
    )
    _check(n_cmp == 2, f"both anchors compared (got {n_cmp})")


def test_recovery_to_floor_is_accepted_even_with_ledger() -> None:
    print("test_recovery_to_floor_is_accepted_even_with_ledger")
    # A RECOVERY — driftflight.com back at its frozen 85.5 floor — is accepted even while
    # the ledger still documents the 76.2 drift, so the ledger can never mask a site healing
    # back to its fixture baseline (the frozen floor is ALWAYS accepted).
    synth = [("synthetic-recovered", _synthetic_sweep("0.7", 46.1, 85.5))]
    div, n_cmp, _, _ = _divergences(
        synth, replay.EXPECTED, _BASELINE_VERSION, ledger=_SYNTH_LEDGER
    )
    _check(div == [], f"a recovery to the frozen floor is accepted (got {div})")
    _check(n_cmp == 2, f"both anchors compared (got {n_cmp})")


def test_documented_pillar_drift_accepted_further_pillar_drift_caught() -> None:
    print("test_documented_pillar_drift_accepted_further_pillar_drift_caught")
    # The PILLAR weld consults the ledger too: driftflight.com's DOCUMENTED transactability
    # 62.5 (the x402 regression's per-pillar effect) is accepted, while every other pillar
    # still welds to the frozen floor. Teeth: a FURTHER transactability drop (50.0, past the
    # documented 62.5) still goes red — and ONLY that pillar.
    floor = replay.EXPECTED["driftflight.com"]["pillars"]
    documented = dict(floor)
    documented["transactability"] = 62.5
    ok_sweep = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "driftflight.com",
                "segment": "api-storefront:rails-anchor",
                "scored": True,
                "overall": 76.2,
                "pillars": documented,
            }
        ],
    }
    pdiv, n_cmp, _, _, _ = _pillar_divergences(
        [("synthetic-doc-pillar", ok_sweep)], replay.EXPECTED, _BASELINE_VERSION,
        members=("driftflight.com",), ledger=_SYNTH_LEDGER,
    )
    _check(pdiv == [], f"the documented transactability 62.5 is accepted (got {pdiv})")
    _check(n_cmp == 4, f"the 4 non-null pillars were compared (got {n_cmp})")

    further = dict(floor)
    further["transactability"] = 50.0
    bad_sweep = {
        "rubric_version": "0.7",
        "rows": [
            {
                "domain": "driftflight.com",
                "segment": "api-storefront:rails-anchor",
                "scored": True,
                "overall": 70.0,
                "pillars": further,
            }
        ],
    }
    pdiv2, _, _, _, _ = _pillar_divergences(
        [("synthetic-further-pillar", bad_sweep)], replay.EXPECTED, _BASELINE_VERSION,
        members=("driftflight.com",), ledger=_SYNTH_LEDGER,
    )
    caught = sorted(d[2] for d in pdiv2)
    _check(
        caught == ["transactability"],
        f"a further transactability drop past the documented value is caught, alone (got {caught})",
    )


def main() -> int:
    tests = [
        test_baseline_version_and_gap_match_replay_guard,
        test_committed_sweeps_carry_scored_anchors,
        test_live_sweep_anchors_agree_with_replay_baseline,
        test_live_sweep_gap_matches_expected_delta,
        test_not_scorable_anchor_is_skipped_not_a_divergence,
        test_drifted_live_anchor_is_caught,
        test_non_anchor_member_is_welded,
        test_drifted_non_anchor_member_is_caught,
        test_books_toscrape_second_non_anchor_is_welded_nonvacuously,
        test_acuity_third_non_anchor_is_welded_nonvacuously,
        test_ipinfo_fourth_non_anchor_is_welded_nonvacuously,
        test_api_replicate_fifth_non_anchor_is_welded_nonvacuously,
        test_moleskine_sixth_non_anchor_is_welded_nonvacuously,
        test_exa_ai_seventh_non_anchor_is_welded_nonvacuously,
        test_thebotwire_eighth_non_anchor_is_welded_nonvacuously,
        test_x402oracle_ninth_non_anchor_is_welded_nonvacuously,
        test_x402deploy_tenth_non_anchor_is_welded_nonvacuously,
        test_coffeecircle_eleventh_non_anchor_is_welded_nonvacuously,
        test_www_bare_domain_key_is_normalized,
        test_off_version_sweep_is_not_compared,
        test_live_sweep_pillars_agree_with_replay_baseline,
        test_pillar_canceling_drift_passes_overall_but_is_caught_by_pillar_weld,
        test_null_pillar_is_skipped_not_a_divergence,
        test_documented_drift_is_accepted_not_a_divergence,
        test_drift_past_documented_value_is_caught,
        test_recovery_to_floor_is_accepted_even_with_ledger,
        test_documented_pillar_drift_accepted_further_pillar_drift_caught,
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
