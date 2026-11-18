.PHONY: setup test lint format demo split eval-dev eval-test reproduce

setup:
	uv python install 3.11
	uv sync --locked

test:
	uv run --locked pytest

lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check .

format:
	uv run --locked ruff format .

demo:
	uv run --locked python -m omissis.app

split:
	uv run --locked python -m omissis.eval.split

eval-dev:
	uv run --locked --env-file .env python -m omissis.eval.run --split dev

eval-test:
	uv run --locked --env-file .env python -m omissis.eval.run --split test

reproduce:
	@echo "make reproduce is not built yet: see docs/TODO.md, step B1." >&2; exit 1
