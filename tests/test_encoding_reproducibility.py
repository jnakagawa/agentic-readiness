"""Default-encoding reproducibility of the committed static evidence (METHOD track).

Runnable directly, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_encoding_reproducibility.py

Invariant #3 is "evidence or it didn't happen": every scored claim travels to
committed artifacts as the serialized ``Report.to_json``. For that committed
evidence to be REPRODUCIBLE — the same fixture re-scored on another machine
yielding the byte-identical report — the serialization must not depend on
anything the HOST ENVIRONMENT chooses. Cycle 267 closed the ``PYTHONHASHSEED``
axis; Cycle 271 closed the ``TZ`` axis; Cycle 274 broadened both to the whole
full-scorable population. This suite closes the THIRD host-environment axis of
that same family: the interpreter's DEFAULT TEXT ENCODING.

Every committed fixture in the reproducibility population carries non-ASCII
bytes (the canonical pair alone typesets the em-dash U+2014 and middot U+00B7;
the retail and booking fixtures carry dozens of lines). Python chooses the
default codec for an ``open(path)`` / ``Path.read_text()`` that omits an
explicit ``encoding=`` from the host locale — UTF-8 on a modern desktop, but
``ANSI_X3.4-1968`` (ASCII) under a bare ``LC_ALL=C`` C locale with UTF-8 mode
off. The scoring path reads its two files — the fixture (``fetch.from_fixture``)
and the rubric (``scoring.load_rubric``) — with EXPLICIT ``encoding="utf-8"``
today, and ``Report.to_json`` serializes with ``ensure_ascii`` so the emitted
bytes are pure ASCII regardless of host. So the SCORE and all scored evidence
are invariant to the machine's default encoding today — but that is an ASSUMED
property, never verified, exactly the situation the hash-seed and timezone
suites converted for their axes. The moment a future probe reads a surface or
fixture file with an IMPLICIT default encoding — a new ``open(path).read()``, a
bare ``Path(p).read_text()`` over an llms.txt / catalog / pricing capture — a
report scored under a UTF-8 host and one scored under a ``LC_ALL=C`` host would
DIVERGE (the C-locale run raising ``UnicodeDecodeError`` on the first non-ASCII
byte, or silently mis-decoding it), and this suite reddens even though the
canonical NUMBERS do not.

This suite re-scores the reproducibility population in SUBPROCESSES under two
maximally-divergent default-encoding environments — an explicit UTF-8 mode
(``PYTHONUTF8=1``, the modern-host reference) and a forced ASCII default
(``LC_ALL=C`` + ``PYTHONUTF8=0`` + ``PYTHONCOERCECLOCALE=0``, defeating both the
PEP 540 UTF-8 mode and the PEP 538 C-locale coercion) — and asserts the full
serialized report is byte-identical across both. Both environments are fully
host-independent, so the guard runs identically on any machine (unlike a
non-C system locale such as ``de_DE``/``tr_TR``, which must be installed to
activate — that axis stays a ``[LOCAL]`` item). The one intentionally varying
field, ``generated_at``, is pinned to a constant before hashing — so ONLY a
genuine default-encoding-dependent evidence projection can move the digest.

Off the scoring path, tests-only: rubric version, probes, and the canonical
delta are untouched. The detector's teeth are proven with a committed non-ASCII
fixture read the two ways — IMPLICIT (host-encoding-dependent: succeeds under
UTF-8, raises under ASCII) vs EXPLICIT ``encoding="utf-8"`` (byte-identical
across both) — so the invariance above cannot vacuously pass.
"""

from __future__ import annotations

import glob
import hashlib
import os
import subprocess
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FIXTURE_DIR = os.path.join(_REPO_ROOT, "fixtures", "canonical")

# The regression-signal pair. Two structurally different API storefronts (with
# vs without agent-native rails) exercise the richest probe set, so they are the
# surface most likely to grow an implicit-encoding surface read. Named by
# capability role, never special-cased.
_CANONICAL = ("driftflight.com", "drift-flight.org")

# The FULL reproducibility population: every committed fixture that covers the
# whole current probe set (0 replay-misses), so a full re-score is faithful —
# identical to the hash-seed/timezone population. The API pair alone is only two
# storefronts; the retail catalog (books.toscrape.com), the appointment-booking
# SaaS (acuityscheduling.com), the physical-goods retailer (www.moleskine.com)
# and the null storefront (example.com) each fire probe paths the API pair never
# exercises. An implicit-encoding read living on one of THOSE paths would slip
# past a pair-only guard; guard 1 below re-scores every one of them. Guard 5 pins
# this set to the LIVE-computed 0-miss set so a future [LOCAL] full-score
# re-capture that promotes a fixture forces its inclusion here.
_POPULATION = (
    "acuityscheduling.com",
    "books.toscrape.com",
    "drift-flight.org",
    "driftflight.com",
    "example.com",
    "www.moleskine.com",
)


def _committed_domains() -> list[str]:
    """Every committed canonical fixture, by bare domain, sorted."""
    return sorted(
        os.path.basename(p)[:-5]
        for p in glob.glob(os.path.join(_FIXTURE_DIR, "*.json"))
    )


def _replay_miss_count(domain: str) -> int:
    """In-process full re-score of a committed fixture; count replay-misses.

    A miss means a probe requested a URL the fixture never recorded — i.e. the
    fixture does not cover the full scoring surface, so a full re-score of it is
    NOT faithful. This is the same replay-miss signal test_canonical_replay uses
    to partition the population; computed here so guard 5 is self-verifying.
    """
    sys.path.insert(0, _REPO_ROOT)
    from asrs import scoring
    from asrs.cli import _run_probes
    from asrs.fetch import FetchContext

    ctx = FetchContext.from_fixture(os.path.join(_FIXTURE_DIR, f"{domain}.json"))
    checks = _run_probes(ctx)
    scoring.score(checks, scoring.load_rubric(None), domain)
    return sum(
        1 for res in ctx._cache.values()
        if res.error and "replay-miss" in res.error
    )


# The two default-encoding environments, each fully host-independent (they do
# not depend on the runner's own LANG). Keys are the labels used in messages.
#   utf8   PYTHONUTF8=1 forces UTF-8 mode ON (PEP 540) -> default codec utf-8,
#          the modern-host reference, regardless of the machine's locale.
#   ascii  LC_ALL=C selects the C locale; PYTHONUTF8=0 forces UTF-8 mode OFF and
#          PYTHONCOERCECLOCALE=0 defeats the PEP 538 C->C.UTF-8 coercion, so the
#          default codec is ANSI_X3.4-1968 (ASCII). This is the environment a
#          minimal container / cron shell with no locale configured presents.
_ENC_ENVS = {
    "utf8": {"PYTHONUTF8": "1"},
    "ascii": {"LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"},
}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _run(payload: str, enc: str, *, extra_env: dict | None = None,
         allow_fail: bool = False) -> tuple[int, str]:
    """Run ``payload`` in a fresh interpreter under the ``enc`` encoding env.

    Returns ``(returncode, stdout.strip())``. Unless ``allow_fail`` is set, a
    non-zero exit or empty stdout raises loudly so a crashing child can never
    masquerade as "invariant". Env vars in ``_ENC_ENVS[enc]`` are read by the
    interpreter at startup, so passing them via ``env=`` is what selects the
    default codec (verified: PYTHONUTF8=0+LC_ALL=C -> ANSI_X3.4-1968).
    """
    env = dict(os.environ)
    # Clear any inherited copies so the injected values win cleanly.
    for k in ("PYTHONUTF8", "PYTHONCOERCECLOCALE", "LC_ALL", "LANG", "LC_CTYPE"):
        env.pop(k, None)
    env.update(_ENC_ENVS[enc])
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "-c", payload],
        capture_output=True, text=True, env=env, cwd=_REPO_ROOT,
    )
    if not allow_fail:
        if proc.returncode != 0:
            raise AssertionError(
                f"encoded subprocess (enc={enc}) failed rc={proc.returncode}: "
                f"{proc.stderr.strip()[-400:]}"
            )
        if not proc.stdout.strip():
            raise AssertionError(f"encoded subprocess (enc={enc}) produced no output")
    return proc.returncode, proc.stdout.strip()


def _check_is_digest(s: str, label: str) -> None:
    if len(s) != 64 or any(c not in "0123456789abcdef" for c in s):
        raise AssertionError(f"{label}: expected a sha256 hex digest, got {s!r}")


# The child that re-scores one canonical fixture and prints the sha256 of the
# full serialized report with the ONE non-reproducible field (the wall-clock
# timestamp) pinned, so only a genuine default-encoding-dependent evidence
# projection can move the digest. The interpreter's default codec is already
# selected from the injected env at startup — no in-child setup needed.
_SCORE_CHILD = r"""
import hashlib, os, sys
sys.path.insert(0, os.environ["ASRS_ENC_ROOT"])
from asrs import scoring
from asrs.cli import _run_probes
from asrs.fetch import FetchContext
ctx = FetchContext.from_fixture(os.environ["ASRS_ENC_PATH"])
checks = _run_probes(ctx)
rep = scoring.score(checks, scoring.load_rubric(None), os.environ["ASRS_ENC_DOMAIN"])
rep.generated_at = "FIXED"          # the only intentionally varying field
sys.stdout.write(hashlib.sha256(rep.to_json().encode("utf-8")).hexdigest())
"""


def _report_digest(domain: str, enc: str) -> str:
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    env = {"ASRS_ENC_ROOT": _REPO_ROOT, "ASRS_ENC_PATH": path, "ASRS_ENC_DOMAIN": domain}
    _, out = _run(_SCORE_CHILD, enc, extra_env=env)
    _check_is_digest(out, f"{domain}@{enc}")
    return out


# ---------------------------------------------------------------------------
# 1. The committed static report is byte-identical across default encodings —
#    the host-environment sibling of the hash-seed and timezone reproducibility
#    guards. Re-scoring ANY full-scorable committed fixture under UTF-8 mode or
#    a forced ASCII default serializes the SAME report. Covers the whole
#    replay-clean population, not just the API pair, so an implicit-encoding
#    read on a retail / booking / null probe path is caught too.
# ---------------------------------------------------------------------------
def test_committed_report_serialization_is_default_encoding_invariant() -> None:
    print("test_committed_report_serialization_is_default_encoding_invariant")
    for domain in _POPULATION:
        digests = {enc: _report_digest(domain, enc) for enc in _ENC_ENVS}
        distinct = set(digests.values())
        _check(
            len(distinct) == 1,
            f"{domain}: serialized report byte-identical across default "
            f"encodings {list(_ENC_ENVS)} "
            f"(digests: { {enc: d[:12] + '…' for enc, d in digests.items()} })",
        )


# ---------------------------------------------------------------------------
# 2. The pair's reproducibility is JOINT — both regression-signal storefronts
#    reproduce, so a leak on EITHER side (with-rails or no-rails) is caught, not
#    only on whichever domain a spot check happened to pick.
# ---------------------------------------------------------------------------
def test_both_regression_signal_sides_reproduce_under_encoding() -> None:
    print("test_both_regression_signal_sides_reproduce_under_encoding")
    per_domain = {}
    for domain in _CANONICAL:
        a, b = _report_digest(domain, "utf8"), _report_digest(domain, "ascii")
        _check(a == b, f"{domain}: digest encoding-stable ({a[:12]}… == {b[:12]}…)")
        per_domain[domain] = a
    _check(
        len(set(per_domain.values())) == len(_CANONICAL),
        f"the two sides serialize to DISTINCT reports (non-vacuous): "
        f"{ {d: h[:12] + '…' for d, h in per_domain.items()} }",
    )


# ---------------------------------------------------------------------------
# 3. TEETH — the subprocess mechanism actually distinguishes a default-encoding-
#    dependent file read, and reading with explicit ``encoding="utf-8"`` is the
#    fix. Had a probe read a non-ASCII surface with an IMPLICIT default codec,
#    guard 1 would break under the ASCII child; this proves it, without touching
#    the real scorer. The leaky payload reads a committed non-ASCII fixture with
#    NO encoding= (host default); the fixed payload reads the same file with
#    explicit UTF-8. Under UTF-8 mode both succeed; under the ASCII default the
#    leaky read RAISES UnicodeDecodeError (host-encoding-dependent) while the
#    explicit-UTF-8 read stays byte-identical (the fix the guard rewards).
# ---------------------------------------------------------------------------
_TEETH_CHILD = r"""
import hashlib, sys
mode, path = sys.argv[1], sys.argv[2]
if mode == "leaky":
    data = open(path).read()                       # host default codec
else:
    data = open(path, encoding="utf-8").read()     # explicit UTF-8 (the fix)
sys.stdout.write(hashlib.sha256(data.encode("utf-8")).hexdigest())
"""


def _teeth_run(kind: str, enc: str, path: str) -> tuple[int, str]:
    payload = _TEETH_CHILD.replace("sys.argv[1]", repr(kind)).replace(
        "sys.argv[2]", repr(path)
    )
    return _run(payload, enc, allow_fail=True)


def test_default_encoding_guard_has_teeth() -> None:
    print("test_default_encoding_guard_has_teeth")
    # A committed fixture that genuinely carries non-ASCII bytes, so the two read
    # strategies can actually diverge on it. Non-vacuity: assert the file really
    # is non-ASCII, else the teeth would be meaningless.
    path = os.path.join(_FIXTURE_DIR, f"{_CANONICAL[0]}.json")
    with open(path, "rb") as fh:
        raw = fh.read()
    _check(
        any(b > 0x7F for b in raw),
        f"{_CANONICAL[0]}.json carries non-ASCII bytes (teeth are non-vacuous)",
    )

    # The IMPLICIT read is host-encoding-dependent: it succeeds under UTF-8 mode
    # but RAISES under the forced ASCII default (a real UnicodeDecodeError).
    rc_utf8, out_utf8 = _teeth_run("leaky", "utf8", path)
    _check(rc_utf8 == 0, "implicit-encoding read SUCCEEDS under UTF-8 mode")
    _check_is_digest(out_utf8, "leaky@utf8")
    rc_ascii, _ = _teeth_run("leaky", "ascii", path)
    _check(
        rc_ascii != 0,
        "implicit-encoding read FAILS under the forced ASCII default "
        "(host-encoding-dependent) — guard 1's mechanism has teeth",
    )

    # The EXPLICIT-UTF-8 read — the fix — is byte-identical across both.
    _, fixed_utf8 = _teeth_run("fixed", "utf8", path)
    _, fixed_ascii = _teeth_run("fixed", "ascii", path)
    _check_is_digest(fixed_utf8, "fixed@utf8")
    _check_is_digest(fixed_ascii, "fixed@ascii")
    _check(
        fixed_utf8 == fixed_ascii,
        "explicit encoding=\"utf-8\" reads byte-identically across UTF-8 and "
        f"ASCII defaults ({fixed_utf8[:12]}… == {fixed_ascii[:12]}…) — the fix "
        "the guard rewards",
    )


# ---------------------------------------------------------------------------
# 4. The child actually exercised the REAL scorer — a guard against the whole
#    suite silently passing because the subprocess no-op'd. Confirm the digest
#    a child computes matches an IN-PROCESS serialization of the same report
#    (this runner's own encoding), so the children are scoring, not echoing.
# ---------------------------------------------------------------------------
def test_child_digest_matches_in_process_score() -> None:
    print("test_child_digest_matches_in_process_score")
    sys.path.insert(0, _REPO_ROOT)
    from asrs import scoring
    from asrs.cli import _run_probes
    from asrs.fetch import FetchContext

    domain = _CANONICAL[0]
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    ctx = FetchContext.from_fixture(path)
    checks = _run_probes(ctx)
    rep = scoring.score(checks, scoring.load_rubric(None), domain)
    rep.generated_at = "FIXED"
    in_proc = hashlib.sha256(rep.to_json().encode("utf-8")).hexdigest()

    child = _report_digest(domain, "utf8")
    _check(
        in_proc == child,
        f"{domain}: in-process digest matches the encoded child's "
        f"({in_proc[:12]}… == {child[:12]}…) — children score the real pipeline",
    )


# ---------------------------------------------------------------------------
# 5. The reproducibility population is EXACTLY the set of committed fixtures that
#    faithfully full-re-score (0 replay-misses), and it is strictly broader than
#    the regression pair — self-maintaining, identical to the hash-seed/timezone
#    guarantee: a NEW full-scorable fixture (or a [LOCAL] re-capture that
#    promotes a classification-only one) reddens until added here; a
#    classification-only fixture cannot sneak in (it misses under the full
#    scorer). Non-vacuity: _POPULATION strictly contains the canonical pair.
# ---------------------------------------------------------------------------
def test_reproducibility_population_is_the_replay_clean_set() -> None:
    print("test_reproducibility_population_is_the_replay_clean_set")
    committed = _committed_domains()
    live_clean = {d for d in committed if _replay_miss_count(d) == 0}
    _check(
        set(_POPULATION) == live_clean,
        f"_POPULATION is exactly the committed fixtures that full-re-score "
        f"with 0 replay-misses (pinned {sorted(_POPULATION)} vs live "
        f"{sorted(live_clean)}) — promote/re-capture forces inclusion",
    )
    _check(
        set(_CANONICAL).issubset(_POPULATION),
        f"the regression pair {sorted(_CANONICAL)} is inside the population",
    )
    _check(
        len(_POPULATION) > len(_CANONICAL),
        f"the population ({len(_POPULATION)}) is strictly broader than the pair "
        f"({len(_CANONICAL)}) — the extension is non-vacuous",
    )


def main() -> int:
    tests = [
        test_committed_report_serialization_is_default_encoding_invariant,
        test_both_regression_signal_sides_reproduce_under_encoding,
        test_default_encoding_guard_has_teeth,
        test_child_digest_matches_in_process_score,
        test_reproducibility_population_is_the_replay_clean_set,
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
