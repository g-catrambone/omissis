"""The pilot (protocol, section 2): both attacks on the 10 pilot texts.

    uv run --env-file .env python -m omissis.eval.pilot

It masks the pilot texts of `data/pool/` under the three references, prints the number
of calls and waits for a confirmation, runs linkage (N = 10 and 25) and attribute
inference, and writes `results/pilot/masked/`, `results/pilot/metrics/linkage.json`
and `attributes.json`, and the one-page note `results/pilot/pilot.md`.

The go or no-go is the team's: the note states the rule and the numbers, not a
decision.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from omissis.cli import write_masked
from omissis.config import load_eval_configs, run_id
from omissis.eval import attacks
from omissis.eval import profiles as planning
from omissis.eval.datasets import load_texts

POOL = Path("data/pool")
OUT = Path("results/pilot")
EVAL_CONFIG = Path("configs/eval.yaml")
REFERENCES = ("REF-none", "REF-oracle-direct", "REF-oracle")
RULE_MIN_DIRECT = 6  # authors identified under REF-oracle-direct, of 10
RULE_MIN_DROP = 3  # fewer under REF-oracle


def write_metrics(path: Path, seed: int, run_ids: list[str], rows: list, per_text: list) -> None:
    data = {
        "split": "pilot",
        "seed": seed,
        "generated_from": run_ids,
        "rows": rows,
        "per_text": per_text,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def note(
    linkage_rows: list[dict[str, Any]], attribute_rows: list[dict[str, Any]], texts: int
) -> str:
    """The one-page note: the numbers of the pilot and the rule they are read with."""
    top1 = {(r["config"], r["n"]): round(r["top1"] * r["texts"]) for r in linkage_rows}
    direct, oracle = top1[("REF-oracle-direct", 10)], top1[("REF-oracle", 10)]
    lines = [
        "# Pilot",
        "",
        f"Both attacks on the {texts} pilot texts under the three references. Written by",
        "`python -m omissis.eval.pilot`; the numbers are in `results/pilot/metrics/`.",
        "",
        "## Linkage: authors identified (top-1), of " + str(texts),
        "",
        "| Configuration | N = 10 | N = 25 | top-3, N = 10 | unparseable |",
        "|---|---|---|---|---|",
    ]
    for name in REFERENCES:
        by_n = {r["n"]: r for r in linkage_rows if r["config"] == name}
        lines.append(
            f"| `{name}` | {top1[(name, 10)]} | {top1[(name, 25)]} | "
            f"{round(by_n[10]['top3'] * texts)} | "
            f"{by_n[10]['unparseable'] + by_n[25]['unparseable']} |"
        )
    lines += [
        "",
        "Chance: 1 of 10 at N = 10, 0.4 of 10 at N = 25.",
        "",
        "## Pilot rule (protocol, section 2)",
        "",
        f"Go when the attacker identifies at least {RULE_MIN_DIRECT} authors under "
        f"`REF-oracle-direct` at N = 10",
        f"and at least {RULE_MIN_DROP} fewer under `REF-oracle`. `REF-none` is reported only.",
        "",
        f"- `REF-oracle-direct`: {direct} of {texts} "
        f"(needs {RULE_MIN_DIRECT}: {'met' if direct >= RULE_MIN_DIRECT else 'not met'})",
        f"- `REF-oracle`: {oracle} of {texts}, {direct - oracle} fewer "
        f"(needs {RULE_MIN_DROP}: {'met' if direct - oracle >= RULE_MIN_DROP else 'not met'})",
        "",
        "The decision is the team's and goes in `docs/decisions.md` with these numbers.",
        "",
        "## Attribute inference: accuracy",
        "",
        "| Attribute | " + " | ".join(f"`{n}`" for n in REFERENCES) + " | majority | invalid |",
        "|---|" + "---|" * (len(REFERENCES) + 2),
    ]
    for attribute in attacks.ATTRIBUTES:
        cells = {r["config"]: r for r in attribute_rows if r["attribute"] == attribute}
        accuracy = " | ".join(f"{cells[n]['accuracy']:.2f}" for n in REFERENCES)
        invalid = sum(cells[n]["invalid"] for n in REFERENCES)
        baseline = cells[REFERENCES[0]]["majority_baseline"]
        lines.append(f"| {attribute} | {accuracy} | {baseline:.2f} | {invalid} |")
    lines += [
        "",
        "Ten texts: every number here is a count to read, not an estimate to report.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.pilot")
    parser.add_argument("--yes", action="store_true", help="do not ask before calling the model")
    parser.add_argument("--backend", choices=["cloud", "replay"])
    args = parser.parse_args(argv)

    files = planning.build()
    plan, pools = files["plan.json"], planning.load_pools()
    profiles = {p["id"]: p for p in files["profiles.json"]}
    records = {r.id: r for r in load_texts(POOL) if plan[r.id]["pilot"]}
    missing = sorted(t for t, e in plan.items() if e["pilot"] and t not in records)
    if missing:
        print(f"pilot texts missing from {POOL}: {missing}", file=sys.stderr)
        return 2
    overrides = {"backend": args.backend} if args.backend else None
    configs = load_eval_configs(EVAL_CONFIG, overrides)
    configs = {name: configs[name] for name in REFERENCES}

    count = attacks.count_calls(len(records), len(configs))
    print(
        f"{len(records)} texts x {len(configs)} configurations: {count['calls']} calls to the "
        f"attacker, about {count['tokens']:,} tokens (free tier: no charge; cached calls "
        "are not made again)."
    )
    if not args.yes and input("Proceed? [y/N] ").strip().lower() != "y":
        return 1

    write_masked(list(records.values()), configs, OUT / "masked")
    linkage, attribute = [], []
    for name, config in configs.items():
        masked = attacks.load_masked(OUT / "masked" / name)
        for size in planning.LIST_SIZES:
            candidates = files[f"candidates_N{size}.json"]
            linkage += attacks.linkage(masked, name, size, plan, profiles, candidates, config)
            print(f"{name}: linkage N={size} done")
        attribute += attacks.attributes(masked, name, records, profiles, pools, config)
        print(f"{name}: attributes done")

    seed = next(iter(configs.values())).seed
    run_ids = [run_id(c) for c in configs.values()]
    linkage_rows = attacks.linkage_rows(linkage, seed)
    attribute_rows = attacks.attribute_rows(attribute, seed)
    write_metrics(OUT / "metrics" / "linkage.json", seed, run_ids, linkage_rows, linkage)
    write_metrics(OUT / "metrics" / "attributes.json", seed, run_ids, attribute_rows, attribute)
    (OUT / "pilot.md").write_text(
        note(linkage_rows, attribute_rows, len(records)), encoding="utf-8"
    )
    print(f"written {OUT / 'pilot.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
