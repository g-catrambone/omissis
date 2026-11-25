"""Detection metrics and latency (protocol, sections 6 and 11).

`run(split, config)` runs every detector that can run on this machine over the texts
of a split, writes what each found to `results/<split>/detected/<detector>/`, then
computes the metrics from those files into `results/<split>/metrics/detection.json`.
The metrics are always computed from the files, so they can be recomputed without
running a detector, and the files of a detector that was not run here are kept and
counted.

Matching (protocol, section 6). Exact: same start, end and type. Overlap: at least one
shared character and the same class; each gold span matches at most one predicted
span and the other way round, the pairs with the longest overlap first. Under overlap
matching a gold span is counted under its own type (recall) and a predicted span
under its own (precision). Leak: a text where some gold direct identifier is not
fully covered by the predicted spans, whatever their type.

`time_detectors` is the timing pass: each detector once per text, on an empty cache
of its own under `results/scratch/`, after one call on an empty text that loads the
model. `make eval-dev` never calls it.

    python -m omissis.eval.detection run --split dev
    python -m omissis.eval.detection time --split dev
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from omissis import detect as detection
from omissis.config import RunConfig, load_eval_configs, run_id, with_overrides
from omissis.contracts import TYPE_CLASS, DetectorId, Span, SpanClass
from omissis.eval.datasets import TextRecord, load_texts
from omissis.eval.stats import bootstrap_ci

EVAL_CONFIG = Path("configs/eval.yaml")
RESULTS = Path("results")
HELD_OUT = "test"  # as in eval/run.py: evaluated once
MATCHINGS = ("exact", "overlap")
NO_LEAK_RATE = (DetectorId.D3.value,)  # D3 does not look for direct identifiers


# --- matching ----------------------------------------------------------------------


def _overlap(a: Span, b: Span) -> int:
    return max(0, min(a.end, b.end) - max(a.start, b.start))


def match(gold: list[Span], predicted: list[Span], matching: str) -> list[tuple[int, int]]:
    """Pairs (gold index, predicted index), one to one."""
    if matching == "exact":
        where = {(p.start, p.end, p.type): j for j, p in enumerate(predicted)}
        return [
            (i, where[(g.start, g.end, g.type)])
            for i, g in enumerate(gold)
            if (g.start, g.end, g.type) in where
        ]
    candidates = sorted(
        (
            (-_overlap(g, p), i, j)
            for i, g in enumerate(gold)
            for j, p in enumerate(predicted)
            if g.cls is p.cls and _overlap(g, p) > 0
        )
    )
    pairs, used_gold, used_predicted = [], set(), set()
    for _, i, j in candidates:  # the longest overlap first
        if i not in used_gold and j not in used_predicted:
            pairs.append((i, j))
            used_gold.add(i)
            used_predicted.add(j)
    return pairs


def leaks(gold: list[Span], predicted: list[Span]) -> bool:
    """True when a gold direct identifier is not fully covered by the predicted spans."""
    covered = set()
    for p in predicted:
        covered.update(range(p.start, p.end))
    return any(
        g.cls is SpanClass.DIRECT and not covered.issuperset(range(g.start, g.end)) for g in gold
    )


def text_counts(gold: list[Span], predicted: list[Span]) -> dict[str, Any]:
    """Matched, missed and spurious spans of one text, per type, under both matchings."""
    out: dict[str, Any] = {"leak": leaks(gold, predicted)}
    for matching in MATCHINGS:
        pairs = match(gold, predicted, matching)
        gold_hit, predicted_hit = {i for i, _ in pairs}, {j for _, j in pairs}
        counts: dict[str, dict[str, int]] = {}
        for i, g in enumerate(gold):
            cell = counts.setdefault(g.type.value, {"matched_gold": 0, "missed": 0})
            cell["matched_gold" if i in gold_hit else "missed"] += 1
        for j, p in enumerate(predicted):
            cell = counts.setdefault(p.type.value, {})
            key = "matched_predicted" if j in predicted_hit else "spurious"
            cell[key] = cell.get(key, 0) + 1
        out[matching] = counts
    return out


# --- metrics -----------------------------------------------------------------------


def _prf(matched_gold: int, missed: int, matched_predicted: int, spurious: int) -> dict[str, Any]:
    gold, predicted = matched_gold + missed, matched_predicted + spurious
    recall = matched_gold / gold if gold else None
    precision = matched_predicted / predicted if predicted else None
    f1 = None
    if recall is not None and precision is not None:
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "gold": gold,
        "predicted": predicted,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def rows(per_text: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """Micro-averaged precision, recall and F1 per detector, matching, class and type."""
    out = []
    for detector in dict.fromkeys(r["detector"] for r in per_text):
        group = [r for r in per_text if r["detector"] == detector]
        for matching in MATCHINGS:
            totals: dict[tuple[str, str], dict[str, int]] = {}
            for r in group:
                for type, cell in r[matching].items():
                    levels = (("type", type), ("class", TYPE_CLASS[type].value), ("all", "all"))
                    for level in levels:
                        total = totals.setdefault(level, {})
                        for key, value in cell.items():
                            total[key] = total.get(key, 0) + value
            for (level, name), total in sorted(totals.items()):
                out.append(
                    {"detector": detector, "matching": matching, "level": level, "name": name}
                    | _prf(
                        *(
                            total.get(k, 0)
                            for k in ("matched_gold", "missed", "matched_predicted", "spurious")
                        )
                    )
                )
        if detector not in NO_LEAK_RATE:
            estimate, low, high = bootstrap_ci([float(r["leak"]) for r in group], seed)
            out.append(
                {
                    "detector": detector,
                    "level": "leak_rate",
                    "texts": len(group),
                    "leak_rate": estimate,
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    return out


# --- files -------------------------------------------------------------------------


def _span_dict(span: Span) -> dict[str, Any]:
    return {
        "start": span.start,
        "end": span.end,
        "text": span.text,
        "type": span.type.value,
        "confidence": span.confidence,
        "source": span.source,
        "reason": span.reason,
    }


def write_detected(
    records: list[TextRecord], detectors: list[DetectorId], config: RunConfig, folder: Path
) -> None:
    """Run each detector on each text and write `<folder>/<detector>/<text_id>.json`."""
    for detector in detectors:
        out = folder / detector.value
        out.mkdir(parents=True, exist_ok=True)
        for record in records:
            started = time.perf_counter()
            spans = detection.detect(record.text, detector, config)
            seconds = time.perf_counter() - started
            data = {
                "text_id": record.id,
                "detector": detector.value,
                "spans": [_span_dict(s) for s in spans],
                "seconds": round(seconds, 4),
            }
            (out / f"{record.id}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )


def read_detected(folder: Path) -> dict[str, dict[str, list[Span]]]:
    """`detector -> text_id -> spans` of every detector folder under `folder`."""
    found: dict[str, dict[str, list[Span]]] = {}
    for path in sorted(folder.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        found.setdefault(data["detector"], {})[data["text_id"]] = [
            Span(**span) for span in data["spans"]
        ]
    return found


def per_text(records: list[TextRecord], folder: Path) -> list[dict[str, Any]]:
    """The counts of every text for every detector whose files hold all the texts."""
    out = []
    for detector, by_text in read_detected(folder).items():
        missing = [r.id for r in records if r.id not in by_text]
        if missing:
            raise FileNotFoundError(f"{folder / detector}: no file for {missing[:3]}")
        for record in records:
            # A file left from another version of the text would be scored in silence.
            if not all(span.matches(record.text) for span in by_text[record.id]):
                raise ValueError(
                    f"{folder / detector}: a span of {record.id} does not match the text; "
                    "run the detector again"
                )
            out.append(
                {"text_id": record.id, "detector": detector}
                | text_counts(list(record.spans), by_text[record.id])
            )
    return out


def run(split: str, config: RunConfig, results: Path = RESULTS, data: Path = Path("data")) -> Path:
    """Detect with every supported detector, then write the detection metrics."""
    records = load_texts(data / split)
    folder = results / split / "detected"
    write_detected(records, list(detection.supported_detectors()), config, folder)
    counts = per_text(records, folder)
    metrics = {
        "split": split,
        "seed": config.seed,
        "generated_from": [run_id(config)],
        "rows": rows(counts, config.seed),
        "per_text": counts,
    }
    path = results / split / "metrics" / "detection.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# --- latency -----------------------------------------------------------------------


def percentile(values: list[float], q: int) -> float:
    return (
        statistics.quantiles(values, n=100, method="inclusive")[q - 1]
        if len(values) > 1
        else values[0]
    )


def time_detectors(
    split: str, config: RunConfig, results: Path = RESULTS, data: Path = Path("data")
) -> Path:
    """Time each detector once per text on an empty cache; write `latency.json`."""
    records = load_texts(data / split)
    scratch = results / "scratch" / "timing" / uuid.uuid4().hex
    per, summary = [], []
    for detector in detection.supported_detectors():
        fresh = with_overrides(config, cache_dir=scratch / detector.value, backend="cloud")
        detection.detect("", detector, fresh)  # loads the model: not part of the timing
        seconds = []
        for record in records:
            started = time.perf_counter()
            detection.detect(record.text, detector, fresh)
            seconds.append(time.perf_counter() - started)
            per.append({"text_id": record.id, "detector": detector.value, "seconds": seconds[-1]})
        summary.append(
            {
                "detector": detector.value,
                "texts": len(seconds),
                "p50": percentile(seconds, 50),
                "p95": percentile(seconds, 95),
            }
        )
    metrics = {
        "split": split,
        "seed": config.seed,
        "generated_from": [run_id(config)],
        "machine": platform.node(),
        "rows": summary,
        "per_text": per,
    }
    path = results / split / "metrics" / "latency.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m omissis.eval.detection")
    parser.add_argument("command", choices=["run", "time"])
    parser.add_argument("--split", required=True)
    parser.add_argument("--backend", choices=["cloud", "replay"])
    args = parser.parse_args(argv)
    if args.split == HELD_OUT and (RESULTS / args.split / "metrics" / "contrasts.json").exists():
        print(f"{args.split} was already evaluated: a second run is refused.", file=sys.stderr)
        return 2
    overrides = {"backend": args.backend} if args.backend else None
    config = next(iter(load_eval_configs(EVAL_CONFIG, overrides).values()))
    path = (run if args.command == "run" else time_detectors)(args.split, config, results=RESULTS)
    print(f"written {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
