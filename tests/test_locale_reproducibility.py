"""System-locale reproducibility of the committed static evidence (METHOD track).

Runnable directly, no pytest required:

    ~/github/agentic-readiness/.venv/bin/python tests/test_locale_reproducibility.py

Invariant #3 is "evidence or it didn't happen": every scored claim travels to
committed artifacts as the serialized ``Report.to_json``. For that committed
evidence to be REPRODUCIBLE — the same fixture re-scored on another machine
yielding the byte-identical report — the serialization must not depend on
anything the HOST ENVIRONMENT chooses. Cycle 267 closed the ``PYTHONHASHSEED``
axis; Cycle 271 closed the ``TZ`` axis; Cycle 277 closed the DEFAULT-ENCODING
axis. Those three cover every host axis a MINIMAL container varies without
installing anything extra, so their environments are fully host-independent and
they run in the cloud. This suite closes the ONE remaining host-environment
reproducibility axis of that same family — a genuine non-C SYSTEM LOCALE — which
the cloud container CANNOT exercise (its ``locale -a`` is C / C.utf8 / POSIX
only; ``setlocale(LC_ALL, 'de_DE.UTF-8')`` raises there). That is why this axis
was spun out as a ``[LOCAL]`` item (Cycle 277): it needs the locales INSTALLED
to activate, so it is verified on the local runner (which has them) and skips
cleanly where they are absent.

The default-encoding suite (Cycle 277) forces the interpreter's default CODEC,
which catches an implicit ``open(path).read()`` mis-decoding a non-ASCII byte.
A system locale is a DIFFERENT hazard the ASCII-codec axis cannot reach: with
``LC_NUMERIC`` set to ``de_DE`` (and the locale ACTIVATED via
``setlocale(LC_ALL, "")``, the realistic worst case of a host or framework that
did so at startup) the C library's decimal point becomes ``,`` and the thousands
separator ``.`` — so a number formatted through ANY locale-aware path
(``"{:n}".format(n)``, ``locale.format_string(..., grouping=True)``,
``locale.atof``) serializes as ``1.234.567`` where a C-locale host emits
``1234567``. A report scored under a ``de_DE.UTF-8`` host and one scored under a
``C`` host would then DIVERGE even though the canonical NUMBERS are identical.
Turkish (``tr_TR``) adds the dotless-i axis on top of the comma-decimal one. The
scoring path today formats every number through locale-INDEPENDENT paths
(``json.dumps`` / ``repr(float)`` always emit ``.``; ``sorted()`` is codepoint
order, not ``locale.strcoll``), so the SCORE and all scored evidence are
invariant to the machine's system locale today — but that is an ASSUMED
property, never verified, exactly the situation the hash-seed / timezone /
encoding suites converted for their axes.

This suite re-scores the reproducibility population in SUBPROCESSES under three
system locales — ``C`` (the baseline), ``de_DE.UTF-8`` (comma-decimal,
dot-grouping) and ``tr_TR.UTF-8`` (dotless-i + comma-decimal) — each child
ACTIVATING the env-selected locale via ``setlocale(LC_ALL, "")`` so
``LC_NUMERIC`` genuinely bites, and asserts the full serialized report is
byte-identical across all three. The one intentionally varying field,
``generated_at``, is pinned to a constant before hashing — so ONLY a genuine
locale-dependent evidence projection can move the digest. The runner process
NEVER calls ``setlocale`` (it is process-global); every activation happens in a
spawned child, so the suite cannot corrupt the locale of any other test.

Off the scoring path, tests-only: rubric version, probes, and the canonical
delta are untouched. The detector's teeth are proven with a locale-sensitive
number format read the two ways under a child that activated the locale —
locale-AWARE (``"{:n}"``: ``1.234.567`` under ``de_DE`` vs ``1234567`` under
``C``) vs locale-INDEPENDENT (``str(n)``: byte-identical) — so the invariance
above cannot vacuously pass. Where the non-C locales are NOT installed (the
cloud container), the three locale-specific guards SKIP loudly and the two
host-independent guards (child-scores-the-real-pipeline, population-is-the-
replay-clean-set) still run, so this file exits 0 everywhere while doing its
real work only where the locales exist.
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
# surface most likely to grow a locale-aware number/collation projection. Named
# by capability role, never special-cased.
_CANONICAL = ("driftflight.com", "drift-flight.org")

# The FULL reproducibility population: every committed fixture that covers the
# whole current probe set (0 replay-misses), so a full re-score is faithful —
# identical to the hash-seed / timezone / encoding population. Guard 5 pins this
# set to the LIVE-computed 0-miss set so a future [LOCAL] full-score re-capture
# that promotes a fixture forces its inclusion here.
_POPULATION = (
    "acuityscheduling.com",
    "api.replicate.com",
    "api.x402oracle.com",
    "books.toscrape.com",
    "drift-flight.org",
    "driftflight.com",
    "exa.ai",
    "example.com",
    "ipinfo.io",
    "thebotwire.com",
    "www.moleskine.com",
)

# The three system-locale environments. ``C`` is always present; the two foreign
# locales must be INSTALLED on the host to activate (that is the [LOCAL] gate).
# Each child calls setlocale(LC_ALL, "") so LC_ALL from the env is what activates.
#   C   the locale-neutral baseline (decimal point '.', no grouping).
#   de  de_DE.UTF-8 — decimal point ',', thousands separator '.' (the comma-
#       decimal axis: "{:n}".format(1234567) -> "1.234.567").
#   tr  tr_TR.UTF-8 — comma-decimal AND the Turkish dotless-i case-fold axis.
_LOCALE_ENVS = {
    "C": "C",
    "de": "de_DE.UTF-8",
    "tr": "tr_TR.UTF-8",
}
_FOREIGN = ("de", "tr")  # the locales that must be installed to run guards 1-3


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
    NOT faithful. Same replay-miss signal test_canonical_replay uses to
    partition the population; computed here so guard 5 is self-verifying.
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


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


def _skip(msg: str) -> None:
    print(f"  SKIP: {msg}")


def _run(payload: str, loc: str, *, extra_env: dict | None = None,
         allow_fail: bool = False) -> tuple[int, str]:
    """Run ``payload`` in a fresh interpreter under the ``loc`` system locale.

    Returns ``(returncode, stdout.strip())``. ``LC_ALL`` from ``_LOCALE_ENVS`` is
    injected via ``env=`` and the payload activates it with
    ``setlocale(LC_ALL, "")``, so LC_NUMERIC genuinely bites. Unless
    ``allow_fail`` is set, a non-zero exit or empty stdout raises loudly so a
    crashing child can never masquerade as "invariant".
    """
    env = dict(os.environ)
    # Clear any inherited locale vars so the injected LC_ALL wins cleanly.
    for k in ("LC_ALL", "LANG", "LC_CTYPE", "LC_NUMERIC", "LC_COLLATE"):
        env.pop(k, None)
    env["LC_ALL"] = _LOCALE_ENVS[loc]
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "-c", payload],
        capture_output=True, text=True, env=env, cwd=_REPO_ROOT,
    )
    if not allow_fail:
        if proc.returncode != 0:
            raise AssertionError(
                f"locale subprocess (loc={loc}) failed rc={proc.returncode}: "
                f"{proc.stderr.strip()[-400:]}"
            )
        if not proc.stdout.strip():
            raise AssertionError(f"locale subprocess (loc={loc}) produced no output")
    return proc.returncode, proc.stdout.strip()


def _check_is_digest(s: str, label: str) -> None:
    if len(s) != 64 or any(c not in "0123456789abcdef" for c in s):
        raise AssertionError(f"{label}: expected a sha256 hex digest, got {s!r}")


# A child that just activates the env locale and reports its numeric conventions,
# used to (a) probe availability and (b) prove the foreign locale is genuinely
# active before trusting the teeth. Prints "<thousands_sep>|<decimal_point>".
_CONV_CHILD = r"""
import locale, sys
locale.setlocale(locale.LC_ALL, "")
c = locale.localeconv()
sys.stdout.write("%s|%s" % (c.get("thousands_sep"), c.get("decimal_point")))
"""


def _host_has_foreign_locales() -> bool:
    """True iff every foreign locale in _FOREIGN activates on this host.

    Probed in a child so the runner process's own locale is never touched. The
    cloud container (C / C.utf8 / POSIX only) returns False here → guards 1-3
    skip; the local runner (de_DE.UTF-8 + tr_TR.UTF-8 installed) returns True.
    """
    for loc in _FOREIGN:
        rc, _ = _run(_CONV_CHILD, loc, allow_fail=True)
        if rc != 0:
            return False
    return True


_HOST_HAS_FOREIGN = _host_has_foreign_locales()


# The child that re-scores one fixture and prints the sha256 of the full
# serialized report with the ONE non-reproducible field (the wall-clock
# timestamp) pinned, so only a genuine locale-dependent evidence projection can
# move the digest. It ACTIVATES the env-selected system locale first.
_SCORE_CHILD = r"""
import hashlib, locale, os, sys
locale.setlocale(locale.LC_ALL, "")          # activate the env system locale
sys.path.insert(0, os.environ["ASRS_LOC_ROOT"])
from asrs import scoring
from asrs.cli import _run_probes
from asrs.fetch import FetchContext
ctx = FetchContext.from_fixture(os.environ["ASRS_LOC_PATH"])
checks = _run_probes(ctx)
rep = scoring.score(checks, scoring.load_rubric(None), os.environ["ASRS_LOC_DOMAIN"])
rep.generated_at = "FIXED"                    # the only intentionally varying field
sys.stdout.write(hashlib.sha256(rep.to_json().encode("utf-8")).hexdigest())
"""


def _report_digest(domain: str, loc: str) -> str:
    path = os.path.join(_FIXTURE_DIR, f"{domain}.json")
    env = {"ASRS_LOC_ROOT": _REPO_ROOT, "ASRS_LOC_PATH": path, "ASRS_LOC_DOMAIN": domain}
    _, out = _run(_SCORE_CHILD, loc, extra_env=env)
    _check_is_digest(out, f"{domain}@{loc}")
    return out


# ---------------------------------------------------------------------------
# 1. The committed static report is byte-identical across system locales — the
#    host-environment sibling of the hash-seed / timezone / encoding guards.
#    Re-scoring ANY full-scorable committed fixture under C, de_DE.UTF-8 or
#    tr_TR.UTF-8 (locale activated) serializes the SAME report. Covers the whole
#    replay-clean population, so a locale-aware projection on a retail / booking
#    / null probe path is caught too. [LOCAL]: skips where the foreign locales
#    are not installed.
# ---------------------------------------------------------------------------
def test_committed_report_serialization_is_system_locale_invariant() -> None:
    print("test_committed_report_serialization_is_system_locale_invariant")
    if not _HOST_HAS_FOREIGN:
        _skip(
            f"foreign system locales {[_LOCALE_ENVS[k] for k in _FOREIGN]} not "
            "installed on this host ([LOCAL] axis) — invariance unverified here"
        )
        return
    for domain in _POPULATION:
        digests = {loc: _report_digest(domain, loc) for loc in _LOCALE_ENVS}
        distinct = set(digests.values())
        _check(
            len(distinct) == 1,
            f"{domain}: serialized report byte-identical across system locales "
            f"{[_LOCALE_ENVS[k] for k in _LOCALE_ENVS]} "
            f"(digests: { {loc: d[:12] + '…' for loc, d in digests.items()} })",
        )


# ---------------------------------------------------------------------------
# 2. The pair's reproducibility is JOINT — both regression-signal storefronts
#    reproduce, so a leak on EITHER side (with-rails or no-rails) is caught, not
#    only on whichever domain a spot check happened to pick. [LOCAL]: skips
#    without the foreign locales.
# ---------------------------------------------------------------------------
def test_both_regression_signal_sides_reproduce_under_locale() -> None:
    print("test_both_regression_signal_sides_reproduce_under_locale")
    if not _HOST_HAS_FOREIGN:
        _skip("foreign system locales not installed ([LOCAL] axis)")
        return
    per_domain = {}
    for domain in _CANONICAL:
        digs = [_report_digest(domain, loc) for loc in _LOCALE_ENVS]
        _check(
            len(set(digs)) == 1,
            f"{domain}: digest locale-stable across {list(_LOCALE_ENVS)} "
            f"({digs[0][:12]}…)",
        )
        per_domain[domain] = digs[0]
    _check(
        len(set(per_domain.values())) == len(_CANONICAL),
        f"the two sides serialize to DISTINCT reports (non-vacuous): "
        f"{ {d: h[:12] + '…' for d, h in per_domain.items()} }",
    )


# ---------------------------------------------------------------------------
# 3. TEETH — the subprocess mechanism actually distinguishes a locale-dependent
#    number projection, and locale-INDEPENDENT formatting is the fix. Had a
#    probe formatted a number through a locale-aware path (``"{:n}"`` /
#    ``locale.format_string(grouping=True)``), guard 1 would break under the
#    de_DE child; this proves it, without touching the real scorer. The leaky
#    payload formats 1234567 with ``"{:n}"`` after activating the locale; the
#    fixed payload uses ``str()``. Under de_DE the leaky read is ``1.234.567``,
#    under C it is ``1234567`` (locale-dependent → a leak the guard would
#    catch); the fixed read is ``1234567`` under both (the property the scorer
#    actually has). [LOCAL]: skips without the foreign locales.
# ---------------------------------------------------------------------------
_TEETH_CHILD = r"""
import locale, sys
locale.setlocale(locale.LC_ALL, "")
mode = sys.argv[1]
n = 1234567
if mode == "leaky":
    sys.stdout.write("{:n}".format(n))     # locale-AWARE grouping/decimal
else:
    sys.stdout.write(str(n))               # locale-INDEPENDENT (the fix)
"""


def _teeth_run(kind: str, loc: str) -> str:
    payload = _TEETH_CHILD.replace("sys.argv[1]", repr(kind))
    _, out = _run(payload, loc)
    return out


def test_system_locale_guard_has_teeth() -> None:
    print("test_system_locale_guard_has_teeth")
    if not _HOST_HAS_FOREIGN:
        _skip("foreign system locales not installed ([LOCAL] axis)")
        return

    # Non-vacuity: prove the de_DE locale is GENUINELY active in the child (its
    # numeric conventions differ from C), else the teeth would be meaningless.
    _, conv_c = _run(_CONV_CHILD, "C")
    _, conv_de = _run(_CONV_CHILD, "de")
    _check(
        conv_de != conv_c,
        f"de_DE.UTF-8 is genuinely active in-child (thousands|decimal "
        f"{conv_de!r} != C {conv_c!r}) — teeth are non-vacuous",
    )

    # The locale-AWARE format is locale-DEPENDENT: it differs between de_DE and C.
    leaky_de = _teeth_run("leaky", "de")
    leaky_c = _teeth_run("leaky", "C")
    _check(
        leaky_de != leaky_c,
        f'"{{:n}}".format(1234567) is locale-dependent (de_DE {leaky_de!r} != '
        f"C {leaky_c!r}) — guard 1's mechanism has teeth",
    )

    # The locale-INDEPENDENT format — the fix the scorer uses — is byte-identical.
    fixed_de = _teeth_run("fixed", "de")
    fixed_c = _teeth_run("fixed", "C")
    _check(
        fixed_de == fixed_c,
        f"str(1234567) is locale-independent (de_DE {fixed_de!r} == C "
        f"{fixed_c!r}) — the fix the guard rewards",
    )


# ---------------------------------------------------------------------------
# 4. The child actually exercised the REAL scorer — a guard against the whole
#    suite silently passing because the subprocess no-op'd. Confirm the digest a
#    child computes (under the always-present C locale) matches an IN-PROCESS
#    serialization of the same report, so the children are scoring, not echoing.
#    Runs everywhere (C locale only), so it gives real coverage even in the
#    cloud where guards 1-3 skip.
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

    child = _report_digest(domain, "C")
    _check(
        in_proc == child,
        f"{domain}: in-process digest matches the C-locale child's "
        f"({in_proc[:12]}… == {child[:12]}…) — children score the real pipeline",
    )


# ---------------------------------------------------------------------------
# 5. The reproducibility population is EXACTLY the set of committed fixtures that
#    faithfully full-re-score (0 replay-misses), and it is strictly broader than
#    the regression pair — self-maintaining, identical to the hash-seed /
#    timezone / encoding guarantee: a NEW full-scorable fixture (or a [LOCAL]
#    re-capture that promotes a classification-only one) reddens until added
#    here; a classification-only fixture cannot sneak in (it misses under the
#    full scorer). Runs everywhere (no foreign locale needed).
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
        test_committed_report_serialization_is_system_locale_invariant,
        test_both_regression_signal_sides_reproduce_under_locale,
        test_system_locale_guard_has_teeth,
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
