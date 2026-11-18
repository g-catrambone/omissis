"""Rows, scorecard and chart from the per-text outcomes (task 3.10; protocol, 10 to 13).

Every estimate, interval and test is a function of the `per_text` lists and of the
seed stored in the metrics files. `rebuild(split)` recomputes the rows of every file
from them, then writes the scorecard and the chart: no model, no detector, no text.
It is the command `make reproduce` calls.

    python -m omissis.eval.report --split dev
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from omissis.eval import attacks, detection
from omissis.eval.stats import bootstrap_ci, holm, mcnemar_exact, mean, paired_bootstrap

RESULTS = Path("results")
OUTCOMES = ("restored", "restored_fuzzy", "dropped", "altered_unresolved", "hallucinated_token")
# The three primary contrasts of the protocol, section 5: (a, b, what is compared).
CONTRASTS = (
    ("D4+R1", "D1+R1", "linkage_top1_n25"),
    ("D4+R1", "REF-none", "utility"),
    ("D4+R2", "D4+R1", "full_restoration"),
)


def _configs(per_text: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(r["config"] for r in per_text))


def utility_rows(per_text: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """One row per configuration: T3, T1 and the utility score, each with its interval."""
    rows = []
    for name in _configs(per_text):
        group = [r for r in per_text if r["config"] == name]
        row: dict[str, Any] = {"config": name, "texts": len(group)}
        for metric in ("t3", "t1", "utility"):
            values = [r[metric] for r in group]
            if any(v is None for v in values):  # T1 without a judge: not reported
                row |= {metric: None, f"{metric}_ci_low": None, f"{metric}_ci_high": None}
                continue
            estimate, low, high = bootstrap_ci(values, seed)
            row |= {metric: estimate, f"{metric}_ci_low": low, f"{metric}_ci_high": high}
        row["t3_unparseable"] = sum(not r["t3_parsed"] for r in group)
        row["judge_unparseable"] = sum(not r["judge_parsed"] for r in group)
        rows.append(row)
    return rows


def restoration_rows(per_text: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """One row per configuration: full-restoration rate, outcome shares, restored fakes."""
    rows = []
    for name in _configs(per_text):
        group = [r for r in per_text if r["config"] == name]
        estimate, low, high = bootstrap_ci([float(r["fully_restored"]) for r in group], seed)
        events = {o: sum(r["outcomes"].get(o, 0) for r in group) for o in OUTCOMES}
        total = sum(events.values())
        rows.append(
            {
                "config": name,
                "texts": len(group),
                "full_restoration": estimate,
                "ci_low": low,
                "ci_high": high,
                "events": total,
                "outcome_shares": {o: (n / total if total else None) for o, n in events.items()},
                "restored_fakes_per_reply": mean([r["restored_fakes"] for r in group]),
            }
        )
    return rows


def _paired(per_text: list[dict[str, Any]], a: str, b: str, value) -> tuple[list, list] | None:
    """The values of two configurations on the texts both have, in the same order."""
    by = {(r["config"], r["text_id"]): value(r) for r in per_text if r["config"] in (a, b)}
    ids = sorted(t for c, t in by if c == a and (b, t) in by)
    if not ids or any(by[(c, t)] is None for c in (a, b) for t in ids):
        return None
    return [by[(a, t)] for t in ids], [by[(b, t)] for t in ids]


def contrast_rows(
    linkage: list[dict[str, Any]],
    utility: list[dict[str, Any]],
    restoration: list[dict[str, Any]],
    seed: int,
) -> list[dict[str, Any]]:
    """The primary contrasts whose two configurations were both run, Holm-adjusted."""
    top1 = [r for r in linkage if r["n"] == 25]
    sources = {
        "linkage_top1_n25": (top1, lambda r: r["top1"], True),
        # T3 alone and the mean of T3 and T1 are two scales: both sides need a T1.
        "utility": (utility, lambda r: None if r["t1"] is None else r["utility"], False),
        "full_restoration": (restoration, lambda r: r["fully_restored"], True),
    }
    rows = []
    for a, b, metric in CONTRASTS:
        per_text, value, binary = sources[metric]
        paired = _paired(per_text, a, b, value)
        if paired is None:
            continue
        xs, ys = paired
        row: dict[str, Any] = {"a": a, "b": b, "metric": metric, "texts": len(xs)}
        difference = paired_bootstrap([float(x) for x in xs], [float(y) for y in ys], seed)
        row |= {k: difference[k] for k in ("difference", "low", "high")}
        if binary:
            test = mcnemar_exact(xs, ys)
            row |= {
                "test": "mcnemar_exact",
                "p": test["p"],
                "a_only": test["a_only"],
                "b_only": test["b_only"],
            }
        else:
            row |= {"test": "paired_bootstrap", "p": difference["p"]}
        rows.append(row)
    for row, adjusted in zip(rows, holm([r["p"] for r in rows]), strict=True):
        row["p_holm"] = adjusted
        row["finding"] = adjusted < 0.05
    return rows


# --- files -------------------------------------------------------------------------


def read(folder: Path, name: str) -> dict[str, Any] | None:
    path = folder / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write(folder: Path, name: str, data: dict[str, Any]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _fmt(value: float | None, low: float | None = None, high: float | None = None) -> str:
    if value is None:
        return "—"
    if low is None or high is None:
        return f"{value:.2f}"
    if low == high:
        return f"{value:.2f} (no variation)"
    return f"{value:.2f} [{low:.2f}, {high:.2f}]"


def scorecard(split: str, metrics: dict[str, dict[str, Any] | None]) -> str:
    """The two tables of the protocol, section 13, as Markdown."""
    lines = [f"# Scorecard — {split}", ""]
    linkage, attributes = metrics["linkage"], metrics["attributes"]
    utility, restoration = metrics["utility"], metrics["restoration"]
    if linkage and attributes and utility and restoration:
        names = _configs(linkage["per_text"])
        texts = linkage["rows"][0]["texts"]
        lines += [
            f"{texts} texts. Estimates with 95% intervals (paired bootstrap over texts).",
            "Privacy score = 1 − linkage top-1 at N = 25.",
            "",
            "| Configuration | top-1 N=10 | top-3 N=10 | top-1 N=25 | top-3 N=25 | "
            + " | ".join(attacks.ATTRIBUTES)
            + " | T3 | T1 | utility | full restoration |",
            "|---|" + "---|" * (8 + len(attacks.ATTRIBUTES)),
        ]
        for name in names:
            link = {r["n"]: r for r in linkage["rows"] if r["config"] == name}
            attr = {r["attribute"]: r for r in attributes["rows"] if r["config"] == name}
            util = next(r for r in utility["rows"] if r["config"] == name)
            rest = next(r for r in restoration["rows"] if r["config"] == name)
            cells = [
                _fmt(link[10]["top1"]),
                _fmt(link[10]["top3"]),
                _fmt(link[25]["top1"], link[25]["top1_ci_low"], link[25]["top1_ci_high"]),
                _fmt(link[25]["top3"]),
                *(_fmt(attr[a]["accuracy"]) for a in attacks.ATTRIBUTES),
                _fmt(util["t3"]),
                _fmt(util["t1"]),
                _fmt(util["utility"], util["utility_ci_low"], util["utility_ci_high"]),
                _fmt(rest["full_restoration"], rest["ci_low"], rest["ci_high"]),
            ]
            lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
        lines += ["", "Chance: top-1 0.10 at N = 10 and 0.04 at N = 25; top-3 0.30 and 0.12.", ""]
    if metrics["detection"]:
        rows = metrics["detection"]["rows"]
        latency = {r["detector"]: r for r in (metrics["latency"] or {}).get("rows", [])}
        lines += [
            "## Detectors",
            "",
            "Recall under overlap matching. Leak rate: share of texts with a direct",
            "identifier not fully covered.",
            "",
            "| Detector | recall direct | recall quasi | recall special | precision | leak rate "
            "| latency p50 (s) | p95 (s) |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for detector in dict.fromkeys(r["detector"] for r in rows):
            mine = [r for r in rows if r["detector"] == detector]
            by_class = {
                r["name"]: r
                for r in mine
                if r.get("matching") == "overlap" and r["level"] == "class"
            }
            overall = next(
                r for r in mine if r.get("matching") == "overlap" and r["level"] == "all"
            )
            leak = next((r for r in mine if r["level"] == "leak_rate"), None)
            time = latency.get(detector)
            cells = [
                *(_fmt(by_class.get(c, {}).get("recall")) for c in ("direct", "quasi", "special")),
                _fmt(overall["precision"]),
                _fmt(leak["leak_rate"], leak["ci_low"], leak["ci_high"]) if leak else "n/a",
                _fmt(time["p50"]) if time else "—",
                _fmt(time["p95"]) if time else "—",
            ]
            lines.append(f"| {detector} | " + " | ".join(cells) + " |")
        lines.append("")
    if metrics["contrasts"] and metrics["contrasts"]["rows"]:
        lines += [
            "## Primary contrasts",
            "",
            "| Contrast | metric | difference | test | p | Holm p | finding |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in metrics["contrasts"]["rows"]:
            verdict = "yes" if r["finding"] else "not distinguishable with this sample"
            lines.append(
                f"| `{r['a']}` vs `{r['b']}` | {r['metric']} | "
                f"{_fmt(r['difference'], r['low'], r['high'])} | {r['test']} | {r['p']:.3f} | "
                f"{r['p_holm']:.3f} | {verdict} |"
            )
        lines.append("")
    return "\n".join(lines)


def chart_metric(rows: list[dict[str, Any]]) -> str:
    """What the chart plots: the utility score, or T3 when a configuration has no T1.

    Without a judge the configurations report T3 alone, and the chart uses T3 for every
    one of them (protocol, section 9): the reference would otherwise sit on another scale.
    """
    return "t3" if any(row["t1"] is None for row in rows) else "utility"


def chart(metrics: dict[str, dict[str, Any] | None], path: Path) -> bool:
    """Privacy against utility, one point per configuration. False without matplotlib."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    linkage, utility = metrics["linkage"], metrics["utility"]
    figure, axes = plt.subplots(figsize=(7, 5))
    metric = chart_metric(utility["rows"])
    for row in utility["rows"]:
        if row[metric] is None:
            continue
        link = next(r for r in linkage["rows"] if r["config"] == row["config"] and r["n"] == 25)
        x, y = 1 - link["top1"], row[metric]
        axes.errorbar(
            x,
            y,
            xerr=[[x - (1 - link["top1_ci_high"])], [(1 - link["top1_ci_low"]) - x]],
            yerr=[[y - row[f"{metric}_ci_low"]], [row[f"{metric}_ci_high"] - y]],
            fmt="o",
            capsize=3,
        )
        axes.annotate(row["config"], (x, y), textcoords="offset points", xytext=(6, 6))
    axes.axvline(1 - 1 / 25, linestyle="--", color="grey")
    axes.annotate("chance", (1 - 1 / 25, 0.02), rotation=90, color="grey", ha="right")
    axes.set_xlabel("Privacy score (1 − linkage top-1, N = 25)")
    axes.set_ylabel("Utility score" if metric == "utility" else "T3 score (judge rejected)")
    axes.set_xlim(-0.05, 1.05)
    axes.set_ylim(0, 1.05)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return True


def rebuild(split: str, results: Path = RESULTS) -> dict[str, dict[str, Any] | None]:
    """Recompute the rows of every metrics file from `per_text`; write scorecard and chart."""
    folder = results / split / "metrics"
    builders = {
        "linkage": attacks.linkage_rows,
        "attributes": attacks.attribute_rows,
        "utility": utility_rows,
        "restoration": restoration_rows,
        "detection": detection.rows,
    }
    metrics: dict[str, dict[str, Any] | None] = {}
    for name, build in builders.items():
        data = read(folder, name)
        if data is not None:
            data["rows"] = build(data["per_text"], data["seed"])
            write(folder, name, data)
        metrics[name] = data
    contrasts = read(folder, "contrasts")
    if contrasts is not None and all(metrics[n] for n in ("linkage", "utility", "restoration")):
        contrasts["rows"] = contrast_rows(
            metrics["linkage"]["per_text"],
            metrics["utility"]["per_text"],
            metrics["restoration"]["per_text"],
            contrasts["seed"],
        )
        write(folder, "contrasts", contrasts)
    metrics["contrasts"] = contrasts
    metrics["latency"] = read(folder, "latency")
    (results / split / "scorecard.md").write_text(scorecard(split, metrics), encoding="utf-8")
    if metrics["linkage"] and metrics["utility"]:
        chart(metrics, results / split / "figures" / "privacy_utility.png")
    return metrics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.report")
    parser.add_argument("--split", required=True)
    args = parser.parse_args(argv)
    rebuild(args.split)
    print(f"written {RESULTS / args.split / 'scorecard.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
