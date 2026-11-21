"""Command line: `omissis run` for one text, `omissis batch` for a folder of texts,
`omissis mask` to write the masked texts of the named configurations.

`run` and `batch` print to standard output only: the result includes the restored
reply, which holds the original values, so never redirect it under `results/`.
`mask` is for synthetic texts only (the evaluation texts and the fixtures).

Every error ends the command with one line on standard error and status 2: a wrong
configuration or input, a cache miss in replay, a provider that fails after its
retries, a broken cache line. The calls already answered stay in the cache.

`run` asks `feasibility.check_text` before it sends: a request for a calculation on
masked amounts, dates or ages is not sent, and ends the command in the same way.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from omissis.config import (
    GOLD_DETECTOR,
    ConfigError,
    RunConfig,
    load_config,
    load_eval_configs,
    run_id,
)
from omissis.contracts import PipelineResult, Span
from omissis.eval.datasets import TextRecord, load_text, load_texts
from omissis.feasibility import check_text
from omissis.pipeline import mask, protect_send_restore

DEFAULT_TASK = "Scrivi una bozza di risposta a questa email."


def _gold(record: TextRecord, config: RunConfig) -> tuple[Span, ...] | None:
    """The gold spans of `record` when the configuration masks the annotation."""
    return record.spans if config.detector == GOLD_DETECTOR else None


def _read_input(path: Path, config: RunConfig) -> tuple[str, tuple[Span, ...] | None]:
    """The text of a JSON text record (with its gold spans for GOLD), or of any other file."""
    if path.suffix == ".json":
        record = load_text(path)
        return record.text, _gold(record, config)
    if config.detector == GOLD_DETECTOR:
        raise ConfigError(f"detector GOLD needs a text record (.json) with spans, got {path}")
    if _is_committed(config.cache_dir):
        # A plain text is never an evaluation record: it may be a real letter, and the
        # cache keeps the prompt that is sent.
        raise ConfigError(
            f"{path} is not a text record and the cache {config.cache_dir} is committed: "
            "use a configuration whose cache_dir is under results/scratch/"
        )
    return path.read_text(encoding="utf-8"), None


def _is_committed(cache_dir: Path) -> bool:
    """True for a folder under `results/` that is not under the gitignored `results/scratch/`."""
    cache, results = Path(cache_dir).resolve(), Path("results").resolve()
    above = (cache, *cache.parents)
    return results in above and results / "scratch" not in above


def _records(folder: Path) -> list[TextRecord]:
    """The text records of `folder`; a folder that is missing or holds none is an error."""
    if not folder.is_dir():
        raise ConfigError(f"{folder} is not a folder")
    records = load_texts(folder)
    if not records:
        raise ConfigError(f"{folder} holds no text record (.json)")
    return records


def _as_dict(result: PipelineResult) -> dict:
    data = asdict(result)
    data["fully_restored"] = result.fully_restored
    return data


def _print_result(result: PipelineResult) -> None:
    print(f"run id: {result.run_id}")
    print("\n--- masked text (as sent) ---")
    print(result.masked_text)
    print("\n--- raw reply ---")
    print(result.raw_reply)
    print("\n--- restored reply ---")
    print(result.restored_reply)
    print("\n--- disclosure ---")
    for item in result.disclosure:
        reason = f" ({item.reason})" if item.reason else ""
        print(f"{item.surrogate}\t{item.cls.value}\t{item.type.value}\t{item.source}{reason}")
    print("\n--- restoration ---")
    for event in result.restore_events:
        found = f" found as {event.found_as!r}" if event.found_as else ""
        print(f"{event.surrogate}\t{event.outcome.value}{found}")
    print(f"\nfully restored: {result.fully_restored}")


def _mask_batch(args: argparse.Namespace, overrides: dict | None) -> None:
    configs = load_eval_configs(args.eval_config, overrides)
    names = args.names.split(",") if args.names else list(configs)
    unknown = [name for name in names if name not in configs]
    if unknown:
        raise ConfigError(f"{args.eval_config}: no configuration named {unknown}")
    write_masked(_records(args.input_dir), {name: configs[name] for name in names}, args.output)


def write_masked(records: list[TextRecord], configs: dict[str, RunConfig], output: Path) -> None:
    """Write `<output>/<config_name>/<text_id>.json` for every record and configuration."""
    for name, config in configs.items():
        folder = output / name
        folder.mkdir(parents=True, exist_ok=True)
        for record in records:
            result, _ = mask(record.text, config, _gold(record, config))  # a fresh vault
            data = {
                "text_id": record.id,
                "config_name": name,
                "run_id": run_id(config),
                "masked_text": result.masked_text,
                "disclosure": [
                    {
                        "surrogate": item.surrogate,
                        "type": item.type.value,
                        "class": item.cls.value,
                        "source": item.source,
                        "reason": item.reason,
                    }
                    for item in result.disclosure
                ],
            }
            path = folder / f"{record.id}.json"
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{name}: {len(records)} texts written to {folder}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="omissis", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in [("run", "protect one text"), ("batch", "protect a folder of texts")]:
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--config", required=True, type=Path, help="run configuration (YAML)")
        sub.add_argument("--task", default=DEFAULT_TASK, help="instruction sent before the text")
        if name == "run":
            sub.add_argument("--input", required=True, type=Path, help="a .json text or a file")
        else:
            sub.add_argument("--input-dir", required=True, type=Path, help="folder of .json texts")
    sub = commands.add_parser("mask", help="write the masked texts of the named configurations")
    sub.add_argument("--eval-config", required=True, type=Path, help="named configurations")
    sub.add_argument("--names", help="comma-separated configuration names (default: all)")
    sub.add_argument("--input-dir", required=True, type=Path, help="folder of .json texts")
    sub.add_argument("--output", required=True, type=Path, help="results/<split>/masked")
    for sub in commands.choices.values():
        sub.add_argument(
            "--backend", choices=["cloud", "replay"], help="override the config's backend"
        )
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        overrides = {"backend": args.backend} if args.backend else None
        if args.command == "mask":
            _mask_batch(args, overrides)
            return 0
        config = load_config(args.config, overrides)
        if args.command == "run":
            text, gold = _read_input(args.input, config)
            blocked = check_text(text, args.task, config, gold)
            if blocked:
                kinds = ", ".join(f"{kind.value}: {count}" for kind, count in blocked.items())
                raise RuntimeError(
                    "request not sent: it asks for a calculation on masked values "
                    f"({kinds}). The cloud model has no number behind a placeholder and "
                    "computes on the fake under R2: the result could not be restored"
                )
            _print_result(protect_send_restore(text, args.task, config, gold))
        else:
            for record in _records(args.input_dir):
                result = protect_send_restore(record.text, args.task, config, _gold(record, config))
                line = {"text_id": record.id, **_as_dict(result)}
                print(json.dumps(line, ensure_ascii=False))
    except (RuntimeError, ValueError, OSError) as exc:
        # ConfigError, DataError and a text that is not UTF-8 are ValueErrors; a cache
        # miss, a detector not built, a provider that fails and a request that the
        # feasibility check stops are RuntimeErrors.
        print(f"omissis: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
