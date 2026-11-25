.PHONY: setup test lint format demo split eval-dev eval-test reproduce

# Every target but setup runs uv offline: `uv run --locked` alone wants the network
# to check the lock (the direct-URL source it-core-news-lg). The environment is
# synced again, with the network, only when .venv is missing or uv.lock or
# pyproject.toml is newer than the last `make setup`.
RUN = uv run --locked --offline
SYNCED = .venv/.synced

setup:
	uv python install 3.11
	uv sync --locked
	touch $(SYNCED)

$(SYNCED): uv.lock pyproject.toml
	$(MAKE) setup

test: $(SYNCED)
	$(RUN) pytest

lint: $(SYNCED)
	$(RUN) ruff check .
	$(RUN) ruff format --check .

format: $(SYNCED)
	$(RUN) ruff format .

demo: $(SYNCED)
	$(RUN) python -m omissis.app

split: $(SYNCED)
	$(RUN) python -m omissis.eval.split

eval-dev: $(SYNCED)
	$(RUN) --env-file .env python -m omissis.eval.run --split dev

eval-test: $(SYNCED)
	$(RUN) --env-file .env python -m omissis.eval.run --split test

reproduce: $(SYNCED)
	@for split in pilot dev test; do \
		if [ -d results/$$split/metrics ]; then \
			$(RUN) python -m omissis.eval.report --split $$split || exit 1; \
		else \
			echo "skipped $$split: no results/$$split/metrics/"; \
		fi; \
	done
