.PHONY: setup test fmt

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

test:
	@if [ -x $(BIN)/pytest ]; then \
		$(BIN)/pytest -q; \
	else \
		$(PYTHON) -m pytest -q; \
	fi

fmt:
	@echo "No formatter pinned yet."
