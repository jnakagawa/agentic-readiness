"""ASRS command-line interface.

    python -m asrs score example.com [--behavioral ...]
    python -m asrs compare a.com b.com [--behavioral ...]

The CLI orchestrates the pipeline (fetch -> probes -> optional behavioral
panel -> scoring -> report) and prints a terminal report card. Probe and
behavioral modules are imported lazily and each guarded, so a crashed or
not-yet-written module degrades gracefully rather than aborting the run.
"""

from __future__ import annotations

import argparse
import sys


# Four static probe modules, in pillar order. Each exposes run(ctx) -> list.
_PROBE_MODULES = ("access", "legibility", "protocols", "trust_static")

# Excerpt size handed to the behavioral trust panel.
_EXCERPT_CHARS = 4000


def _normalize_domain(raw: str) -> str:
    """Strip scheme and trailing slash if the user passed a URL."""
    d = raw.strip()
    for scheme in ("https://", "http://"):
        if d.lower().startswith(scheme):
            d = d[len(scheme):]
            break
    d = d.rstrip("/")
    return d


def _parse_models(raw: str) -> list[str]:
    return [m.strip() for m in raw.split(",") if m.strip()]


def _run_probes(ctx) -> list:
    """Run the four static probe modules, each guarded independently."""
    import importlib

    checks: list = []
    for name in _PROBE_MODULES:
        try:
            mod = importlib.import_module(f"asrs.probes.{name}")
        except Exception as exc:  # module missing or import-time error
            print(
                f"[asrs] warning: probe module {name!r} unavailable "
                f"({type(exc).__name__}: {exc}) — skipped",
                file=sys.stderr,
            )
            continue
        try:
            results = mod.run(ctx)
            checks.extend(results or [])
        except Exception as exc:  # probe crashed at runtime
            print(
                f"[asrs] warning: probe {name!r} crashed "
                f"({type(exc).__name__}: {exc}) — its checks skipped",
                file=sys.stderr,
            )
    return checks


def _homepage_excerpt(ctx) -> str:
    """First ~4000 chars of homepage text, tags roughly stripped."""
    from . import report as report_mod

    try:
        res = ctx.homepage()
        text = getattr(res, "text", "") or ""
    except Exception as exc:
        print(
            f"[asrs] warning: could not fetch homepage for excerpt "
            f"({type(exc).__name__}: {exc})",
            file=sys.stderr,
        )
        return ""
    return report_mod.strip_tags(text)[:_EXCERPT_CHARS]


def _run_behavioral(domain, ctx, task, trials, models, battery=None):
    """Run the trust panel + shopper panel(s) + free-tier transaction probe.

    Returns ``(checks, verdicts, runs, battery_summary)``. Each panel/probe is
    guarded; a missing/crashing module contributes nothing.

    Without ``battery`` this runs the shopper panel ONCE on ``task`` and the
    fourth return value is None. With a :class:`asrs.battery.Battery`, the
    shopper panel runs ONCE PER battery task (each task's ``intent`` is the
    prompt); the FIRST task's runs become the primary scoring run (``runs`` and
    the ``bhv_*`` outcome checks come from it, exactly as a single-task run
    would), and every task's runs feed the additive ``battery_summary``. The
    trust panel and the free-tier transaction probe still run AT MOST ONCE for
    the whole battery — the free-tier probe consumes the target's allowance
    (invariant #1) and must never loop per task.
    """
    import importlib

    checks: list = []
    verdicts: list = []
    runs: list = []
    battery_summary = None

    excerpt = _homepage_excerpt(ctx)

    # -- trust panel (once; site-trust is task-independent) --
    try:
        tp = importlib.import_module("asrs.behavioral.trust_probe")
        verdicts, tp_checks = tp.run_panel(domain, excerpt, models=models)
        checks.extend(tp_checks or [])
    except Exception as exc:
        print(
            f"[asrs] warning: trust panel unavailable "
            f"({type(exc).__name__}: {exc}) — skipped",
            file=sys.stderr,
        )

    # -- shopper panel(s) --
    try:
        sh = importlib.import_module("asrs.behavioral.shopper")
        if battery is None:
            runs, sh_checks = sh.run_panel(
                domain, task, trials=trials, models=models, out_dir="runs"
            )
            checks.extend(sh_checks or [])
        else:
            # One panel per intent. The first task is the primary scoring run so
            # the score is computed from a single real task panel (unchanged
            # semantics); all tasks feed the battery summary.
            runs_by_task: dict = {}
            for i, bt in enumerate(battery.tasks):
                t_runs, t_checks = sh.run_panel(
                    domain, bt.intent, trials=trials, models=models, out_dir="runs"
                )
                runs_by_task[bt.id] = t_runs
                if i == 0:
                    runs = t_runs
                    checks.extend(t_checks or [])
            try:
                bt_mod = importlib.import_module("asrs.battery")
                battery_summary = bt_mod.aggregate_battery(battery, runs_by_task).to_dict()
            except Exception as exc:
                print(
                    f"[asrs] warning: battery aggregation failed "
                    f"({type(exc).__name__}: {exc}) — summary omitted",
                    file=sys.stderr,
                )
    except Exception as exc:
        print(
            f"[asrs] warning: shopper panel unavailable "
            f"({type(exc).__name__}: {exc}) — skipped",
            file=sys.stderr,
        )

    # -- free-tier transaction probe (rubric v0.4) --
    # Runs AFTER the shopper panel. At most ONE transaction attempt per scoring
    # run (it consumes the target's free allowance) — neither ``trials`` nor the
    # battery's per-task loop multiplies it. Guarded like the panels above.
    try:
        ft = importlib.import_module("asrs.behavioral.free_tier")
        ft_checks = ft.run_probe(ctx, out_dir="runs")
        checks.extend(ft_checks or [])
    except Exception as exc:
        print(
            f"[asrs] warning: free-tier probe unavailable "
            f"({type(exc).__name__}: {exc}) — skipped",
            file=sys.stderr,
        )

    return checks, verdicts, runs, battery_summary


def _load_battery_arg(args):
    """Load the ``--battery`` file into a Battery, or return None.

    Returns None when no battery was requested. In static mode a battery is a
    no-op — the static probes are task-independent — so we warn and proceed
    rather than fail. A structurally invalid battery file raises loud (the
    loader's ValueError) so a typo can't silently score fewer intents.
    """
    path = getattr(args, "battery", None)
    if not path:
        return None
    if not args.behavioral:
        print(
            "[asrs] warning: --battery has no effect without --behavioral "
            "(static probes are task-independent) — ignored",
            file=sys.stderr,
        )
        return None
    from .battery import load_battery

    return load_battery(path)


def _evaluate(domain, args, rubric):
    """Full pipeline for one domain -> Report."""
    from .fetch import FetchContext
    from . import scoring

    ctx = FetchContext(domain)
    checks = _run_probes(ctx)

    verdicts: list = []
    runs: list = []
    battery_summary = None
    battery = _load_battery_arg(args)  # None (+ warn) in static mode
    if args.behavioral:
        bhv_checks, verdicts, runs, battery_summary = _run_behavioral(
            domain, ctx, args.task, args.trials, _parse_models(args.models),
            battery=battery,
        )
        checks.extend(bhv_checks)

    report = scoring.score(
        checks, rubric, domain, trust_panel=verdicts, behavioral_runs=runs
    )

    # Attach the cross-intent battery summary additively (like panel_reliability
    # below): the score is already computed from the primary task; this only
    # annotates the report so JSON/HTML consumers see per-intent coverage and the
    # cross-task reliability spread. None on a single-task or static run.
    if battery_summary is not None:
        report.battery_summary = battery_summary

    # Attach within-panel reproducibility as an ADDITIVE diagnostic so JSON /
    # HTML consumers carry it, not just the terminal card. Computed from the same
    # runs by the same pure function the terminal uses, so the two never diverge.
    # Non-scoring: score() already ran; this only annotates the report. Left None
    # when no panel ran (static-only) — a static report has no reproducibility to
    # report, distinct from a panel that ran and produced no valid run.
    if runs:
        from .reliability import panel_reliability

        report.panel_reliability = panel_reliability(runs).to_dict()

    # Attach the quotability verdict as an ADDITIVE diagnostic (mirrors
    # panel_reliability above): the one-bit "is this number citable?" the terminal
    # card already computes, now travelling with the JSON/HTML so a leaderboard
    # consumer sees it next to the number, not only a human who ran the terminal.
    # Same pure function the terminal uses -> the two never diverge. Populated for
    # every mode (static -> static-deterministic; panel -> reproducible/provisional;
    # not-scorable -> not-scorable). Non-scoring: score() already ran; this only
    # annotates the report the same way as reliability/battery.
    from .reliability import quotability

    report.quotability = quotability(report).to_dict()

    return report


def _cmd_score(args) -> int:
    from . import scoring, report as report_mod

    domain = _normalize_domain(args.domain)
    rubric = scoring.load_rubric(args.rubric)

    report = _evaluate(domain, args, rubric)
    path = report_mod.save(report)

    if args.json_only:
        print(path)
    else:
        print(report_mod.render(report))
        print(f"(report saved: {path})")
    return 0


def _cmd_compare(args) -> int:
    from . import scoring, report as report_mod

    domain_a = _normalize_domain(args.domain_a)
    domain_b = _normalize_domain(args.domain_b)
    rubric = scoring.load_rubric(args.rubric)

    report_a = _evaluate(domain_a, args, rubric)
    report_b = _evaluate(domain_b, args, rubric)

    path_a = report_mod.save(report_a)
    path_b = report_mod.save(report_b)

    if args.json_only:
        print(path_a)
        print(path_b)
        return 0

    print(report_mod.render_compare(
        report_a, report_b, label_a=args.label_a, label_b=args.label_b
    ))
    print(report_mod.render(report_a))
    print(report_mod.render(report_b))
    print(f"(reports saved: {path_a}, {path_b})")
    return 0


def _cmd_scorecard(args) -> int:
    from . import scorecard

    labels = [l.strip() or None for l in args.labels.split(",")] if args.labels else None
    path = scorecard.build_scorecard(args.reports, labels=labels, out_path=args.out)
    print(path)
    return 0


def _add_common_options(p) -> None:
    p.add_argument(
        "--behavioral", action="store_true",
        help="run the live shopper + trust model panel (claude/codex CLIs)",
    )
    p.add_argument(
        "--task", default="purchase this site's primary product or service",
        help="shopper task prompt (behavioral mode)",
    )
    p.add_argument(
        "--trials", type=int, default=2,
        help="shopper trials per model (behavioral mode); default 2 so a quoted "
        "number is reproducibility-checked, not a single draw. The free-tier "
        "transaction probe still runs at most ONCE per scoring run regardless "
        "(invariant #1) — only the read-only shopper panel repeats.",
    )
    p.add_argument(
        "--models", default="claude,codex",
        help="comma-separated model panel (default: claude,codex)",
    )
    p.add_argument(
        "--battery", default=None,
        help="path to a task-battery YAML (behavioral mode): run the shopper "
        "panel once per intent and attach a cross-intent coverage/reliability "
        "summary. The score still comes from the first task; the free-tier "
        "transaction probe still fires at most once for the whole battery. "
        "No effect in static mode.",
    )
    p.add_argument(
        "--rubric", default=None,
        help="path to a rubric YAML (default: bundled rubric_v0.yaml)",
    )
    p.add_argument(
        "--json-only", action="store_true",
        help="print only the saved JSON path, no report card",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="asrs",
        description="Agentic Selling Readiness Score — probe a domain's "
        "readiness to sell to AI agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser(
        "score", help="score a single domain and print a report card"
    )
    p_score.add_argument("domain", help="domain to score (URL or bare host)")
    _add_common_options(p_score)
    p_score.set_defaults(func=_cmd_score)

    p_cmp = sub.add_parser(
        "compare",
        help="score two domains side-by-side (the with/without delta)",
    )
    p_cmp.add_argument("domain_a", help="first (baseline) domain")
    p_cmp.add_argument("domain_b", help="second (comparison) domain")
    p_cmp.add_argument(
        "--label-a", default="without", help="label for domain_a (default: without)"
    )
    p_cmp.add_argument(
        "--label-b", default="with", help="label for domain_b (default: with)"
    )
    _add_common_options(p_cmp)
    p_cmp.set_defaults(func=_cmd_compare)

    p_card = sub.add_parser(
        "scorecard",
        help="render saved report JSON(s) as an on-brand HTML scorecard",
    )
    p_card.add_argument(
        "reports", nargs="+",
        help="one report JSON (single card) or two (side-by-side delta card)",
    )
    p_card.add_argument(
        "--labels", default=None,
        help='comma-separated column labels, e.g. "Without ZeroClick,With ZeroClick"',
    )
    p_card.add_argument("--out", default=None, help="output HTML path")
    p_card.set_defaults(func=_cmd_scorecard)

    return parser


def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n[asrs] interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # operational failure -> nonzero
        print(f"[asrs] error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
