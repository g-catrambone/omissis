"""Command line: `omissis run` for one text, `omissis batch` for a folder of texts.

Results go to standard output only. They include the restored reply, which holds
the original values, so never redirect them under `results/`.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from omissis.backends import CacheMissError
from omissis.config import ConfigError, load_config
from omissis.contracts import PipelineResult
from omissis.eval.datasets import DataError, load_text, load_texts
from omissis.pipeline import protect_send_restore

DEFAULT_TASK = "Scrivi una bozza di risposta a questa email."


def _read_input(path: Path) -> str:
    """The `text` of a JSON text file, or the whole content of any other file."""
    if path.suffix == ".json":
        return load_text(path).text
    return path.read_text(encoding="utf-8")


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="omissis", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in [("run", "protect one text"), ("batch", "protect a folder of texts")]:
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--config", required=True, type=Path, help="run configuration (YAML)")
        sub.add_argument("--task", default=DEFAULT_TASK, help="instruction sent before the text")
        sub.add_argument(
            "--backend", choices=["cloud", "replay"], help="override the config's backend"
        )
        if name == "run":
            sub.add_argument("--input", required=True, type=Path, help="a .json text or a file")
        else:
            sub.add_argument("--input-dir", required=True, type=Path, help="folder of .json texts")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        overrides = {"backend": args.backend} if args.backend else None
        config = load_config(args.config, overrides)
        if args.command == "run":
            _print_result(protect_send_restore(_read_input(args.input), args.task, config))
        else:
            for record in load_texts(args.input_dir):
                result = protect_send_restore(record.text, args.task, config)
                line = {"text_id": record.id, **_as_dict(result)}
                print(json.dumps(line, ensure_ascii=False))
    except (ConfigError, DataError, CacheMissError, OSError) as exc:
        print(f"omissis: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
