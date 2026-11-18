"""The evaluation runner (task 3.10): every configuration of `configs/eval.yaml` on a split.

    uv run --env-file .env python -m omissis.eval.run --split dev      (make eval-dev)

For each named configuration it writes the masked texts, runs the two attacks and the
two utility tasks, has the reply drafts judged, and writes the metrics files with
their per-text outcomes; it runs the detection evaluation for every detector that can
run here; then the report module writes scorecard and chart. Adding a configuration
to the file needs no change here.

Before any call it prints how many it will make and waits for a confirmation. It
stops with a clear message, instead of scoring a text as if nothing had been found,
when a configuration needs a detector that cannot run on this machine, and on a
`CacheMissError` or a `ConfigError`.

The held-out split is evaluated once: a launch on it is logged, and it is refused
once `contrasts.json`, the last file, exists. A launch that stopped earlier resumes
from the cache. When the judge was rejected at its validation, T1 is not scored by
the judge: on the held-out split the runner writes rating sheets for `D4+R1`, stops
before `contrasts.json`, and completes the same run when the sheets are filled.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from omissis import detect as detectors
from omissis.backends import CacheMissError
from omissis.cli import write_masked
from omissis.config import ConfigError, RunConfig, load_eval_configs, run_id
from omissis.contracts import DetectorId
from omissis.eval import attacks, detection, judge, report, review, utility
from omissis.eval import profiles as planning
from omissis.eval.datasets import DataError, TextRecord, load_texts

EVAL_CONFIG = Path("configs/eval.yaml")
RESULTS = Path("results")
DATA = Path("data")
REFERENCE = "REF-none"
HELD_OUT = "test"
FALLBACK_CONFIG = "D4+R1"
TOKENS = {"utility": 1500, "judge": 2500, **attacks.TOKENS}


def count_calls(texts: int, configs: dict[str, RunConfig]) -> dict[str, int]:
    """Calls per role and rough tokens of a whole run (protocol, section 14)."""
    n = len(configs)
    judged = sum(name != REFERENCE for name in configs)
    calls = {"cloud": texts * n * 2, "judge": texts * judged, "attacker": texts * n * 3}
    tokens = (
        calls["cloud"] * TOKENS["utility"]
        + calls["judge"] * TOKENS["judge"]
        + texts * n * (TOKENS["linkage_10"] + TOKENS["linkage_25"] + TOKENS["attributes"])
    )
    return calls | {"total": sum(calls.values()), "tokens": tokens}


def unsupported(configs: dict[str, RunConfig]) -> list[str]:
    """The configurations whose detector cannot run on this machine."""
    here = set(detectors.supported_detectors())
    return [
        name
        for name, config in configs.items()
        if isinstance(config.detector, DetectorId) and config.detector not in here
    ]


def judge_accepted(results: Path) -> bool:
    """The outcome of the judge validation; true until the validation has been done."""
    outcome = report.read(results / "dev" / "metrics", "judge_validation")
    return outcome is None or bool(outcome["accepted"])


def fallback_scores(
    records: list[TextRecord], configs: dict[str, RunConfig], folder: Path
) -> dict[str, float] | None:
    """Human T1 of `D4+R1` from filled sheets; None after writing empty ones."""
    rated = {FALLBACK_CONFIG: configs[FALLBACK_CONFIG]}
    seed = configs[REFERENCE].seed
    if not (folder / "key.json").exists():
        items, key = judge.build_items(records, rated, configs[REFERENCE], seed)
        judge.write_sheets(items, key, folder, list(review.MEMBERS))
        return None
    key = json.loads((folder / "key.json").read_text(encoding="utf-8"))
    try:
        sheets = [judge.read_sheet(path) for path in sorted(folder.glob("sheet_*.csv"))]
    except ValueError:
        return None  # not filled yet
    scores = {}
    for item, where in key.items():
        consensus = {
            c: judge.round_half_up(sum(s[item][c] for s in sheets) / len(sheets))
            for c in judge.CRITERIA
        }
        scores[where["text_id"]] = judge.t1_score(consensus)
    return scores


def evaluate(
    split: str,
    eval_config: Path = EVAL_CONFIG,
    results: Path = RESULTS,
    data: Path = DATA,
    backend: str | None = None,
    confirm: bool = True,
) -> int:
    """Run the whole evaluation of `split`. Returns the exit status of the command."""
    out = results / split
    metrics = out / "metrics"
    if split == HELD_OUT:
        with open(data / f"{split}_access.log", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now(UTC).isoformat(timespec='seconds')} launch\n")
        if (metrics / "contrasts.json").exists():
            print(f"{split} was already evaluated: a second run is refused.", file=sys.stderr)
            return 2

    configs = load_eval_configs(eval_config, {"backend": backend} if backend else None)
    missing = unsupported(configs)
    if missing:
        print(
            f"these configurations need a detector that cannot run on this machine: {missing} "
            "(run `uv sync --locked --group detect`, pin the models, download the weights)",
            file=sys.stderr,
        )
        return 2
    records = load_texts(data / split)
    files = planning.build(data / "profiles")
    plan, pools = files["plan.json"], planning.load_pools(data / "profiles")
    profiles = {p["id"]: p for p in files["profiles.json"]}
    by_id = {r.id: r for r in records}
    reference = configs[REFERENCE]
    accepted = judge_accepted(results)

    count = count_calls(len(records), configs)
    print(
        f"{len(records)} texts x {len(configs)} configurations: {count['total']} calls "
        f"(cloud {count['cloud']}, judge {count['judge']}, attacker {count['attacker']}), "
        f"about {count['tokens']:,} tokens. Calls already in the cache are not made again."
    )
    if confirm and input("Proceed? [y/N] ").strip().lower() != "y":
        return 1

    write_masked(records, configs, out / "masked")
    detection.run(split, reference, results, data)
    linkage, attribute, useful, restored = [], [], [], []
    # The reference first: its replies are what the judge compares the others with.
    for name in [REFERENCE, *(n for n in configs if n != REFERENCE)]:
        config = configs[name]
        masked = attacks.load_masked(out / "masked" / name)
        for size in planning.LIST_SIZES:
            candidates = files[f"candidates_N{size}.json"]
            linkage += attacks.linkage(masked, name, size, plan, profiles, candidates, config)
        attribute += attacks.attributes(masked, name, by_id, profiles, pools, config)
        rows = utility.run(records, name, config)
        if accepted or name == REFERENCE:
            judged = judge.run(records, name, config, reference)
        else:
            judged = [{"scores": None, "judge_parsed": True, "t1": None} for _ in records]
        for row, verdict in zip(rows, judged, strict=True):
            t1 = verdict["t1"]
            useful.append(
                {
                    "text_id": row["text_id"],
                    "config": name,
                    "t3": row["t3"],
                    "t3_parsed": row["t3_parsed"],
                    "t3_fields": row["t3_fields"],
                    "t1": t1,
                    "scores": verdict["scores"],
                    "judge_parsed": verdict["judge_parsed"],
                    "utility": row["t3"] if t1 is None else (row["t3"] + t1) / 2,
                }
            )
            restored.append(
                {
                    k: row[k]
                    for k in ("text_id", "config", "fully_restored", "outcomes", "restored_fakes")
                }
            )
        print(f"{name}: done")

    seed = reference.seed
    head = {"split": split, "seed": seed, "generated_from": [run_id(c) for c in configs.values()]}
    report.write(metrics, "linkage", head | {"rows": [], "per_text": linkage})
    report.write(metrics, "attributes", head | {"rows": [], "per_text": attribute})
    report.write(metrics, "restoration", head | {"rows": [], "per_text": restored})
    cost = [
        {
            "config": name,
            "cloud": len(records) * 2,
            "attacker": len(records) * 3,
            "judge": len(records) * (name != REFERENCE and accepted),
        }
        for name in configs
    ]
    report.write(metrics, "cost", head | {"rows": cost, "per_text": [], "estimate": count})

    if not accepted and split == HELD_OUT and FALLBACK_CONFIG in configs:
        human = fallback_scores(records, configs, out / "judge_fallback")
        if human is None:
            report.write(metrics, "utility", head | {"rows": [], "per_text": useful})
            report.rebuild(split, results)
            print(
                f"The judge was rejected: fill the sheets in {out / 'judge_fallback'} and "
                "launch the command again. This run is not complete yet."
            )
            return 0
        for row in useful:
            if row["config"] == FALLBACK_CONFIG:
                row["t1"] = human[row["text_id"]]
                row["utility"] = (row["t3"] + row["t1"]) / 2

    report.write(metrics, "utility", head | {"rows": [], "per_text": useful})
    report.write(metrics, "contrasts", head | {"rows": [], "per_text": []})  # the last file
    report.rebuild(split, results)
    print(f"written {out / 'scorecard.md'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.run")
    parser.add_argument("--split", required=True)
    parser.add_argument("--backend", choices=["cloud", "replay"])
    parser.add_argument("--yes", action="store_true", help="do not ask before calling the models")
    args = parser.parse_args(argv)
    try:
        return evaluate(args.split, backend=args.backend, confirm=not args.yes)
    except (CacheMissError, ConfigError, DataError, NotImplementedError, RuntimeError) as exc:
        # RuntimeError: a provider that fails after its retries, a reply cut at the token
        # limit. Nothing of that reply is cached, so the next launch asks again.
        print(f"evaluation stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
