"""Review assignment, double annotation and agreement (task 3.5; protocol, section 3).

    python -m omissis.eval.review assign       write data/pool/REVIEWERS.md
    python -m omissis.eval.review export       write data/annotation/<text_id>.txt
    python -m omissis.eval.review agreement    write results/dev/metrics/agreement.json

`assign` deals the 66 planned texts to the three members, 22 each, by seed, and picks
the 13 texts of the double annotation among those that are not pilot texts, in
proportion to the two domains, each with a second annotator who is not its reviewer.

`export` writes those 13 as plain text, with no tag: the second annotator adds
`[[TYPE|text]]` tags and saves `data/annotation/<text_id>.<initials>.txt`.

`agreement` compares each annotated copy with the spans of the pool, before any
adjudication: span F1 under exact and overlap matching, and Cohen's kappa on the
class of the spans paired by character overlap whatever their class.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

from omissis.contracts import Span, SpanClass
from omissis.eval import profiles as planning
from omissis.eval.datasets import load_texts
from omissis.eval.detection import _overlap, match
from omissis.eval.textgen import parse_tagged

MEMBERS = ("Giuseppe", "Mattia", "Andrea")
DOUBLE = 13
POOL = Path("data/pool")
ANNOTATION = Path("data/annotation")
AGREEMENT = Path("results/dev/metrics/agreement.json")


def assign(plan: dict[str, dict[str, Any]], seed: int = planning.SEED) -> dict[str, dict[str, str]]:
    """`text_id -> {"reviewer": ..., "second": ...}`; `second` only for the 13 texts."""
    rng = random.Random(f"{seed}|review")
    ids = sorted(plan)
    rng.shuffle(ids)
    table = {text_id: {"reviewer": MEMBERS[i % len(MEMBERS)]} for i, text_id in enumerate(ids)}

    eligible = [t for t in sorted(plan) if not plan[t]["pilot"]]
    bank = [t for t in eligible if t.startswith("bank-")]
    hr = [t for t in eligible if t.startswith("hr-")]
    n_bank = round(DOUBLE * len(bank) / len(eligible))
    for text_id in rng.sample(bank, n_bank) + rng.sample(hr, DOUBLE - n_bank):
        others = [m for m in MEMBERS if m != table[text_id]["reviewer"]]
        table[text_id]["second"] = rng.choice(others)
    return dict(sorted(table.items()))


def reviewers_md(table: dict[str, dict[str, str]]) -> str:
    lines = [
        "# Reviewers",
        "",
        "Fixed by seed (`python -m omissis.eval.review assign`). Each member reviews 22",
        "texts as tagged text (`python -m omissis.eval.textgen export` and `import`) and",
        "writes their initials in `reviewed_by` by hand. The 13 texts with a second",
        "annotator are annotated a second time from plain text, before any review pull",
        "request is opened (`docs/evaluation_protocol.md`, section 3).",
        "",
        "| Text | Reviewer | Second annotator |",
        "|---|---|---|",
    ]
    lines += [f"| {t} | {row['reviewer']} | {row.get('second', '')} |" for t, row in table.items()]
    return "\n".join(lines) + "\n"


# --- agreement ---------------------------------------------------------------------


def pair_by_overlap(a: list[Span], b: list[Span]) -> list[tuple[Span, Span]]:
    """Spans of the two annotators paired one to one by longest overlap, whatever the class."""
    candidates = sorted(
        (-_overlap(x, y), i, j) for i, x in enumerate(a) for j, y in enumerate(b) if _overlap(x, y)
    )
    pairs, used_a, used_b = [], set(), set()
    for _, i, j in candidates:
        if i not in used_a and j not in used_b:
            pairs.append((a[i], b[j]))
            used_a.add(i)
            used_b.add(j)
    return pairs


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Cohen's kappa of two labellings of the same items; None with no item."""
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(x == y for x, y in pairs) / n
    labels = {label for pair in pairs for label in pair}
    expected = sum(
        sum(x == label for x, _ in pairs) * sum(y == label for _, y in pairs) for label in labels
    ) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def agreement(texts: dict[str, tuple[list[Span], list[Span]]]) -> dict[str, Any]:
    """Agreement of two annotators over `text_id -> (first spans, second spans)`."""
    totals = {m: {"matched": 0, "first": 0, "second": 0} for m in ("exact", "overlap")}
    classes: list[tuple[str, str]] = []
    per_text = []
    for text_id, (first, second) in texts.items():
        row: dict[str, Any] = {"text_id": text_id, "first": len(first), "second": len(second)}
        for matching, total in totals.items():
            matched = len(match(first, second, matching))
            row[f"matched_{matching}"] = matched
            total["matched"] += matched
            total["first"] += len(first)
            total["second"] += len(second)
        pairs = [(x.cls.value, y.cls.value) for x, y in pair_by_overlap(first, second)]
        row["class_pairs"] = pairs
        classes += pairs
        per_text.append(row)
    rows: list[dict[str, Any]] = []
    for matching, total in totals.items():
        spans = total["first"] + total["second"]
        rows.append(
            {"matching": matching, "f1": 2 * total["matched"] / spans if spans else None, **total}
        )
    rows.append({"metric": "kappa_class", "pairs": len(classes), "kappa": cohen_kappa(classes)})
    return {"rows": rows, "per_text": per_text, "classes": [c.value for c in SpanClass]}


def read_second(folder: Path) -> dict[str, tuple[str, list[Span]]]:
    """`text_id -> (text, spans)` of every annotated copy `<text_id>.<initials>.txt`."""
    found = {}
    for path in sorted(folder.glob("*.*.txt")):
        found[path.name.split(".")[0]] = parse_tagged(path.read_text(encoding="utf-8"))
    return found


# --- commands ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.review")
    parser.add_argument("command", choices=["assign", "export", "agreement"])
    args = parser.parse_args(argv)
    table = assign(planning.build()["plan.json"])
    if args.command == "assign":
        POOL.mkdir(parents=True, exist_ok=True)
        (POOL / "REVIEWERS.md").write_text(reviewers_md(table), encoding="utf-8")
        print(f"written {POOL / 'REVIEWERS.md'}")
        return 0
    records = {r.id: r for r in load_texts(POOL)}
    wanted = [t for t, row in table.items() if "second" in row]
    if args.command == "export":
        missing = [t for t in wanted if t not in records]
        if missing:
            print(f"not in the pool yet: {missing}", file=sys.stderr)
            return 2
        ANNOTATION.mkdir(parents=True, exist_ok=True)
        for text_id in wanted:
            (ANNOTATION / f"{text_id}.txt").write_text(records[text_id].text, encoding="utf-8")
        print(f"{len(wanted)} plain texts written to {ANNOTATION}")
        return 0
    second = read_second(ANNOTATION)
    missing = [t for t in wanted if t not in second]
    if missing:
        print(f"no annotated copy for: {missing}", file=sys.stderr)
        return 2
    texts = {}
    for text_id in wanted:
        text, spans = second[text_id]
        if text != records[text_id].text:
            print(f"{text_id}: the annotated copy changed the text itself", file=sys.stderr)
            return 2
        texts[text_id] = (list(records[text_id].spans), spans)
    result = {"split": "pool", "seed": planning.SEED, "generated_from": []} | agreement(texts)
    AGREEMENT.parent.mkdir(parents=True, exist_ok=True)
    AGREEMENT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written {AGREEMENT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
