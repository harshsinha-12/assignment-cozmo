.PHONY: setup test fmt

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

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

fmt:
	@echo "No formatter pinned yet."
