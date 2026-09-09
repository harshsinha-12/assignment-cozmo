.PHONY: setup test reproduce-synthetic fmt

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
REPRO_OUT ?= out/reproduction

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	$(BIN)/pip install --no-deps -e .

test:
	@if [ -x $(BIN)/pytest ]; then \
		PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(BIN)/pytest -q; \
	else \
		PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest -q; \
	fi

reproduce-synthetic:
	@if [ -x $(BIN)/python ]; then \
		$(BIN)/python -m cozmo_floorplan.reproduction.runner --repo . --out $(REPRO_OUT); \
	else \
		PYTHONPATH=src $(PYTHON) -m cozmo_floorplan.reproduction.runner --repo . --out $(REPRO_OUT); \
	fi

fmt:
	@echo "No formatter pinned yet."
