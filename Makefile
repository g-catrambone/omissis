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
	@echo "make demo is not built yet: task A8 (workstream A) builds it." >&2; exit 1

split:
	@echo "make split is not built yet: task C6 (workstream C) builds it. HUMANS ONLY." >&2; exit 1

eval-dev:
	@echo "make eval-dev is not built yet: task C10 (workstream C) builds it." >&2; exit 1

eval-test:
	@echo "make eval-test is not built yet: task C10 (workstream C) builds it. HUMANS ONLY." >&2; exit 1

reproduce:
	@echo "make reproduce is not built yet: task B9 (workstream B) builds it." >&2; exit 1
