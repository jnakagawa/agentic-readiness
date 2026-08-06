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
# segment control:non-storefront) is scored in all three committed sweeps.
_NON_ANCHOR_WELDED = ("example.com",)
# Every population member welded across the offline-replay and live-sweep paths.
_WELDED_MEMBERS = _ANCHORS + _NON_ANCHOR_WELDED
_BASELINE_VERSION = "0.7"  # asserted == the replay baseline's version below (test 1)
_TOL = 0.05  # overalls are rounded to 0.1 on both paths; this catches any real move


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


def _member_row(sweep: dict, domain: str):
    """The sweep row for a welded member (anchor or non-anchor), matched by domain."""
    for row in sweep.get("rows", []):
        if row.get("domain") == domain:
            return row
    return None


def _divergences(sweeps, expected, baseline_version, tol=_TOL, members=_WELDED_MEMBERS):
    """Pure comparison shared by the real-evidence and synthetic legs.

    Returns (divergences, n_compared, n_unreachable, n_offversion). A divergence
    is a SCORED, same-version welded MEMBER whose overall differs from the
    fixture-replay baseline by more than `tol`. Not-scorable members (invariant #4)
    and off-version sweeps (invariant #2) are COUNTED, never compared. `members`
    defaults to every welded member (the two anchors + the non-anchor members); the
    teeth legs pass a narrower set."""
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
            exp = float(expected[domain]["overall"])
            got = float(row["overall"])
            n_compared += 1
            if abs(got - exp) > tol:
                divergences.append((label, domain, got, exp))
    return divergences, n_compared, n_unreachable, n_offversion


def _pillar_divergences(sweeps, expected, baseline_version, tol=_TOL, members=_WELDED_MEMBERS):
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
    diffed. Not-scorable members (invariant #4) are counted unreachable, skipped."""
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
            for pillar in sorted(set(exp_pillars) | set(got_pillars)):
                exp_v = exp_pillars.get(pillar)
                got_v = got_pillars.get(pillar)
                if exp_v is None or got_v is None:
                    n_null_skipped += 1
                    continue
                n_compared += 1
                if abs(float(got_v) - float(exp_v)) > tol:
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
    # fixture floor. Covers the two anchors AND every non-anchor welded member
    # (example.com), so n_compared today is 3 sweeps x 3 members = 9. n_compared>=2
    # keeps it non-vacuous.
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
    # The +39.4 regression delta, seen through the LIVE population path: for every
    # same-version sweep with BOTH anchors scored, com - org == EXPECTED_DELTA.
    sweeps = _committed_sweeps()
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
            abs(gap - replay.EXPECTED_DELTA) <= _TOL,
            f"{lbl}: live gap {gap} == EXPECTED_DELTA {replay.EXPECTED_DELTA}",
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
    # per-pillar scores equal the offline fixture floor. Covers the two anchors AND
    # example.com across every committed sweep, so n_compared today is 3 sweeps x 3
    # members x 4 non-null pillars = 36 (outcome is null in static mode → skipped).
    # n_compared>=8 keeps it non-vacuous even if a sweep drops a member.
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
        test_off_version_sweep_is_not_compared,
        test_live_sweep_pillars_agree_with_replay_baseline,
        test_pillar_canceling_drift_passes_overall_but_is_caught_by_pillar_weld,
        test_null_pillar_is_skipped_not_a_divergence,
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
