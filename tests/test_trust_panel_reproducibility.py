"""Trust-panel evidence must be reproducible under panel arrival-order permutation.

Companion to ``tests/test_attribution.py::test_reachability_evidence_is_order_
invariant`` (Cycle 253), which closed the shopper-side hole where an arrival-
order ``[:6]`` slice quoted different refusals for the same score. The trust
panel (``asrs.behavioral.trust_probe._build_check``) had the SAME latent hole in
a different shape:

    top = max(confident_refusal, key=lambda v: v.confidence)

``max`` returns the ARRIVAL-first element on a confidence TIE. So two panelists
refusing at equal confidence, fed in a different order, produced the SAME
points/status (order-invariant counts) but a DIFFERENT quoted refusal in the
remediation AND a differently-ordered ``refusing_models`` evidence list — an
order-dependent citable surface under "evidence or it didn't happen". The fix
orders confident refusals loudest-first with a deterministic model tie-break, so
the whole CheckResult is byte-identical under any panel permutation while still
surfacing the genuinely loudest refusal.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asrs.behavioral import trust_probe as T  # noqa: E402
from asrs.types import ModelTrustVerdict  # noqa: E402


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _refuse(model: str, confidence: float, concerns: list[str]) -> ModelTrustVerdict:
    return ModelTrustVerdict(
        model=model, willing=False, confidence=confidence,
        concerns=list(concerns), decision="refuse",
    )


# ---------------------------------------------------------------------------
# 1. Confidence TIE: the quoted refusal + refusing_models order must not depend
#    on which order the panelists happened to answer in. Metamorphic (forward vs
#    reversed panel => byte-identical CheckResult) plus teeth (the pre-fix
#    arrival-first max WOULD have picked different panelists for the two orders).
# ---------------------------------------------------------------------------
def test_loudest_refusal_is_order_invariant_on_confidence_ties() -> None:
    print("test_loudest_refusal_is_order_invariant_on_confidence_ties")
    # Two confident refusers TIED at 0.9 with DISTINCT models and DISTINCT
    # concerns, so any order leak is visible both in the quoted remediation and
    # in the refusing_models list.
    a = _refuse("claude", 0.9, ["claude-only-concern-x"])
    z = _refuse("zeta", 0.9, ["zeta-only-concern-y"])

    fwd = [a, z]
    rev = [z, a]
    models = ["claude", "zeta"]

    cr_fwd = T._build_check("x.example", models, fwd, codex_ok=True)
    cr_rev = T._build_check("x.example", models, rev, codex_ok=True)

    # THE INVARIANT: reversing panel arrival order changes NOTHING in the whole
    # CheckResult (status, points, finding, remediation, every evidence key —
    # including the ORDER of refusing_models).
    _check(cr_fwd == cr_rev,
           "trust-panel CheckResult is byte-identical under panel-order reversal")

    # THE PROPERTY: the deterministic pick on a tie is the model-ascending one
    # (claude < zeta), so its concern is what gets quoted regardless of order.
    _check("claude-only-concern-x" in cr_fwd.remediation,
           "the tie is broken deterministically on model (claude quoted)")
    _check("zeta-only-concern-y" not in cr_fwd.remediation,
           "the losing tied refuser is NOT quoted")
    _check([m["model"] for m in cr_fwd.evidence["refusing_models"]] == ["claude", "zeta"],
           "refusing_models is in the deterministic loudest-first order")

    # TEETH: the PRE-FIX selector (arrival-first max on confidence) DID depend on
    # order — it would have picked a different panelist for the two arrival
    # orders, so the invariant above is a real claim about the fixed code.
    old_fwd = max(fwd, key=lambda v: v.confidence)
    old_rev = max(rev, key=lambda v: v.confidence)
    _check(old_fwd.model != old_rev.model,
           "pre-fix arrival-first max was order-sensitive on the tie (guard has teeth)")


# ---------------------------------------------------------------------------
# 2. The tie-break must NOT override the primary "loudest" semantics: a strictly
#    higher-confidence refuser wins even when its model sorts LAST. Guards that
#    the fix's sort key puts confidence first, not model.
# ---------------------------------------------------------------------------
def test_loudest_refusal_prefers_highest_confidence_over_model() -> None:
    print("test_loudest_refusal_prefers_highest_confidence_over_model")
    # "zzz" sorts LAST by model but is the strictly loudest refuser.
    quiet = _refuse("aaa", 0.75, ["aaa-quieter-concern"])
    loud = _refuse("zzz", 0.95, ["zzz-loudest-concern"])
    models = ["aaa", "zzz"]

    cr = T._build_check("x.example", models, [quiet, loud], codex_ok=True)
    _check("zzz-loudest-concern" in cr.remediation,
           "the strictly loudest refuser is quoted even though its model sorts last")
    _check(cr.evidence["refusing_models"][0]["model"] == "zzz",
           "refusing_models lists the loudest refuser first (confidence dominates tie-break)")


def main() -> int:
    tests = [
        test_loudest_refusal_is_order_invariant_on_confidence_ties,
        test_loudest_refusal_prefers_highest_confidence_over_model,
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
    raise SystemExit(main())
