"""The judge of the reply drafts and its validation (task 3.7; protocol, section 9).

The `judge` model sees the original email, the `REF-none` reply as reference and the
reply under evaluation after restoration, never the configuration. It gives three
scores from 1 to 5: correctness, completeness, Italian quality. A reply of the judge
that cannot be read scores 1 on each and is counted. The T1 score of a text is the
mean of the three, mapped to [0, 1] as (score - 1) / 4. `REF-none` is the reference:
its T1 is 1 by definition and it is not judged.

Validation. `sheets` writes one rating sheet per rater with the items in a shuffled
order and nothing that tells the configuration; the key that ties an item to its
text and configuration is a separate file, which the raters do not open. `accept`
compares the judge with the consensus of the raters and writes the outcome.

    python -m omissis.eval.judge sheets --split dev --raters GC --backend cloud
    python -m omissis.eval.judge accept --split dev

The R2 items come from a configuration that the runner never runs, so `sheets` makes
their replies: the first time it needs `--backend cloud` (one call to the `cloud` model
per text); without the option it replays and calls nothing.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

from omissis.backends import LLMRequest, complete
from omissis.config import RunConfig, load_eval_configs, run_id, with_overrides
from omissis.eval.datasets import TextRecord, load_texts
from omissis.eval.normalise import extract_json
from omissis.eval.utility import t1_reply

CRITERIA = ("correctness", "completeness", "italian")
MAX_TOKENS = 2048
KAPPA_MIN = 0.6
WITHIN_ONE_MIN = 0.85
EVAL_CONFIG = Path("configs/eval.yaml")
SHEET_COLUMNS = ("item", "email", "reference_reply", "reply", *CRITERIA)

SYSTEM = "Sei un revisore che valuta bozze di risposta a email. Rispondi solo con JSON valido."

PROMPT = """\
Valuta la RISPOSTA DA VALUTARE a questa email. La RISPOSTA DI RIFERIMENTO mostra che
cosa una buona risposta contiene: usala come termine di confronto, non come unica
risposta giusta.

EMAIL:
---
{email}
---

RISPOSTA DI RIFERIMENTO:
---
{reference}
---

RISPOSTA DA VALUTARE:
---
{reply}
---

Dai tre voti interi da 1 (pessimo) a 5 (ottimo):
- "correctness": risponde alla richiesta dell'email, senza fatti inventati, rivolta alla
  persona giusta, con importi e date giusti;
- "completeness": copre ciò che copre la risposta di riferimento;
- "italian": qualità dell'italiano: grammatica, accordo di genere, nessun segnaposto
  rimasto nel testo (come [PERSONA_1]) e nessuna parola spezzata.

Rispondi solo con questo JSON:
{{"correctness": voto, "completeness": voto, "italian": voto, "justification": "una frase"}}
"""


def parse_scores(reply: str) -> dict[str, int] | None:
    """The three scores of a judge reply, or None when one is missing or not in 1..5."""
    data = extract_json(reply)
    if data is None:
        return None
    scores = {c: data.get(c) for c in CRITERIA}
    if any(
        isinstance(s, bool) or not isinstance(s, int) or not 1 <= s <= 5 for s in scores.values()
    ):
        return None
    return scores


def t1_score(scores: dict[str, int]) -> float:
    """Mean of the three criteria, mapped to [0, 1] as (score - 1) / 4."""
    return sum((scores[c] - 1) / 4 for c in CRITERIA) / len(CRITERIA)


def judge_one(email: str, reference: str, reply: str, config: RunConfig) -> dict[str, Any]:
    """The judge's scores for one reply; 1 on each criterion when it cannot be read."""
    prompt = PROMPT.format(email=email, reference=reference, reply=reply)
    request = LLMRequest("judge", prompt, SYSTEM, {"max_tokens": MAX_TOKENS})
    scores = parse_scores(complete(request, config).text)
    parsed = scores is not None
    scores = scores or dict.fromkeys(CRITERIA, 1)
    return {"scores": scores, "judge_parsed": parsed, "t1": t1_score(scores)}


def run(
    records: list[TextRecord], name: str, config: RunConfig, reference: RunConfig
) -> list[dict[str, Any]]:
    """One row per text with the judge's scores of the T1 reply of `config`.

    `reference` is the `REF-none` configuration. The replies come from the cache of
    the utility run. When `config` is the reference itself nothing is judged: T1 is 1.
    """
    rows = []
    for record in records:
        row: dict[str, Any] = {"text_id": record.id, "config": name}
        if config.detector == reference.detector:
            row |= {"scores": None, "judge_parsed": True, "t1": 1.0}
        else:
            row |= judge_one(
                record.text, t1_reply(record, reference), t1_reply(record, config), config
            )
        rows.append(row)
    return rows


# --- validation --------------------------------------------------------------------


def validation_configs(configs: dict[str, RunConfig]) -> dict[str, RunConfig]:
    """Gold-span masking with R1 and with R2: the two sources of the validation items."""
    oracle = configs["REF-oracle"]
    return {"R1": oracle, "R2": with_overrides(oracle, strategy="R2")}


def build_items(
    records: list[TextRecord], rated: dict[str, RunConfig], reference: RunConfig, seed: int
) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    """The items to rate, shuffled, and the key from item to text and configuration."""
    pairs = [(record, label) for record in records for label in rated]
    random.Random(f"{seed}|judge-sheet").shuffle(pairs)
    items, key = [], {}
    for number, (record, label) in enumerate(pairs, start=1):
        item = f"item-{number:03d}"
        key[item] = {"text_id": record.id, "config": label}
        items.append(
            {
                "item": item,
                "email": record.text,
                "reference_reply": t1_reply(record, reference),
                "reply": t1_reply(record, rated[label]),
            }
        )
    return items, key


def write_sheets(items: list[dict[str, str]], key: dict, folder: Path, raters: list[str]) -> None:
    """One empty sheet per rater, and the key in a file of its own."""
    folder.mkdir(parents=True, exist_ok=True)
    for rater in raters:
        with open(folder / f"sheet_{rater}.csv", "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=SHEET_COLUMNS)
            writer.writeheader()
            writer.writerows({**item, **dict.fromkeys(CRITERIA, "")} for item in items)
    (folder / "key.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")


def read_sheet(path: Path) -> dict[str, dict[str, int]]:
    """`item -> scores` of a filled sheet; an empty or invalid score is an error."""
    scores = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                values = {c: int(row[c]) for c in CRITERIA}
            except (KeyError, ValueError) as exc:
                raise ValueError(f"{path}, {row.get('item')}: every score must be filled") from exc
            if not all(1 <= v <= 5 for v in values.values()):
                raise ValueError(f"{path}, {row['item']}: scores go from 1 to 5")
            scores[row["item"]] = values
    return scores


def round_half_up(value: float) -> int:
    return math.floor(value + 0.5)


def quadratic_kappa(a: list[int], b: list[int], levels: int = 5) -> float:
    """Quadratic-weighted Cohen's kappa of two lists of scores in 1..levels."""
    if len(a) != len(b) or not a:
        raise ValueError("two lists of the same, non-zero length")
    n = len(a)
    observed = sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) / n
    expected = sum(
        (i - j) ** 2 * a.count(i) * b.count(j)
        for i in range(1, levels + 1)
        for j in range(1, levels + 1)
    ) / (n * n)
    if expected == 0:  # both lists hold one and the same score
        return 1.0
    return 1 - observed / expected


def agreement(judge: list[int], consensus: list[int]) -> dict[str, Any]:
    within = sum(abs(x - y) <= 1 for x, y in zip(judge, consensus, strict=True)) / len(judge)
    return {
        "n": len(judge),
        "kappa": quadratic_kappa(judge, consensus),
        "within_one": within,
        "judge_distribution": {str(s): judge.count(s) for s in range(1, 6)},
        "consensus_distribution": {str(s): consensus.count(s) for s in range(1, 6)},
    }


def acceptance(
    judge: dict[str, dict[str, int]], sheets: list[dict[str, dict[str, int]]]
) -> dict[str, Any]:
    """Judge against the rounded consensus of the raters, over all item-criterion scores.

    With one rater the consensus is that rater's scores.
    """
    if not sheets or any(set(sheet) != set(judge) for sheet in sheets):
        raise ValueError("one sheet or more, each rating exactly the items the judge scored")
    pairs = {
        criterion: [
            (
                judge[item][criterion],
                round_half_up(sum(sheet[item][criterion] for sheet in sheets) / len(sheets)),
            )
            for item in sorted(judge)
        ]
        for criterion in CRITERIA
    }
    everything = [pair for criterion in CRITERIA for pair in pairs[criterion]]
    result = agreement([j for j, _ in everything], [c for _, c in everything])
    result["per_criterion"] = {
        c: agreement([j for j, _ in pairs[c]], [h for _, h in pairs[c]]) for c in CRITERIA
    }
    result["accepted"] = result["kappa"] >= KAPPA_MIN or result["within_one"] >= WITHIN_ONE_MIN
    result["rule"] = f"kappa >= {KAPPA_MIN} or within one point >= {WITHIN_ONE_MIN}"
    return result


def validation_file(
    split: str,
    seed: int,
    run_ids: list[str],
    key: dict[str, dict[str, str]],
    judge: dict[str, dict[str, int]],
    sheets: list[dict[str, dict[str, int]]],
) -> dict[str, Any]:
    """`judge_validation.json` as a metrics file (docs/interfaces.md, section 5).

    One row for all the scores and one per criterion; `per_text` holds the scores of
    the judge and of every rater for each item, so the rows can be rebuilt from it.
    The outcome stays at the top, where the runner reads it.
    """
    result = acceptance(judge, sheets)
    per_criterion = result.pop("per_criterion")
    outcome = {name: result.pop(name) for name in ("accepted", "rule")}
    rows = [{"criterion": "all", **result}]
    rows += [{"criterion": criterion, **per_criterion[criterion]} for criterion in CRITERIA]
    per_text = [
        {
            "item": item,
            "text_id": key[item]["text_id"],
            "config": key[item]["config"],
            "judge": judge[item],
            "raters": [sheet[item] for sheet in sheets],
        }
        for item in sorted(judge)
    ]
    head = {"split": split, "seed": seed, "generated_from": run_ids}
    counts = {"raters": len(sheets), "items": len(judge)}
    return head | outcome | counts | {"rows": rows, "per_text": per_text}


# --- commands ----------------------------------------------------------------------


def _folder(split: str) -> Path:
    return Path("results") / split / "judge_validation"


def _sheets(args: argparse.Namespace) -> int:
    configs = load_eval_configs(EVAL_CONFIG, {"backend": args.backend or "replay"})
    rated = validation_configs(configs)
    records = load_texts(Path("data") / args.split)
    seed = configs["REF-none"].seed
    items, key = build_items(records, rated, configs["REF-none"], seed)
    write_sheets(items, key, _folder(args.split), args.raters)
    print(f"{len(items)} items written for {', '.join(args.raters)} in {_folder(args.split)}")
    return 0


def _accept(args: argparse.Namespace) -> int:
    folder = _folder(args.split)
    key = json.loads((folder / "key.json").read_text(encoding="utf-8"))
    sheets = [read_sheet(path) for path in sorted(folder.glob("sheet_*.csv"))]
    configs = load_eval_configs(EVAL_CONFIG, {"backend": args.backend} if args.backend else None)
    rated, reference = validation_configs(configs), configs["REF-none"]
    records = {r.id: r for r in load_texts(Path("data") / args.split)}
    judge = {}
    for item, where in key.items():
        record, config = records[where["text_id"]], rated[where["config"]]
        judged = judge_one(
            record.text, t1_reply(record, reference), t1_reply(record, config), config
        )
        judge[item] = judged["scores"]
    run_ids = [run_id(config) for config in (reference, *rated.values())]
    result = validation_file(args.split, reference.seed, run_ids, key, judge, sheets)
    out = Path("results") / args.split / "metrics" / "judge_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    overall = result["rows"][0]
    print(
        f"judge {'accepted' if result['accepted'] else 'rejected'}: kappa "
        f"{overall['kappa']:.2f}, within one point {overall['within_one']:.0%}; see {out}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.judge")
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("sheets", help="write the empty rating sheets")
    sub.add_argument("--split", required=True)
    sub.add_argument("--raters", nargs="+", required=True, help="initials of the raters")
    sub.add_argument("--backend", choices=["cloud", "replay"], help="replay when not given")
    sub.set_defaults(run=_sheets)
    sub = commands.add_parser("accept", help="compare the judge with the filled sheets")
    sub.add_argument("--split", required=True)
    sub.add_argument("--backend", choices=["cloud", "replay"])
    sub.set_defaults(run=_accept)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
