.PHONY: setup test reproduce-synthetic benchmark walkin fmt install-capture-app open-capture-app

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
REPRO_OUT ?= out/reproduction
BENCHMARK_ROOT ?= data/private
BENCHMARK_OUT ?= out/benchmark
BENCHMARK_AGENT_MODE ?= auto
WALKIN_ROOT ?= data/private/walkin
WALKIN_OUT ?= out/walkin
WALKIN_AGENT_MODE ?= auto

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

benchmark:
	@if [ -x $(BIN)/python ]; then \
		COZMO_AGENT_MODE=$(BENCHMARK_AGENT_MODE) $(BIN)/python -m cozmo_floorplan benchmark $(BENCHMARK_ROOT) --out $(BENCHMARK_OUT); \
	else \
		PYTHONPATH=src COZMO_AGENT_MODE=$(BENCHMARK_AGENT_MODE) $(PYTHON) -m cozmo_floorplan benchmark $(BENCHMARK_ROOT) --out $(BENCHMARK_OUT); \
	fi

walkin:
	@if [ -x $(BIN)/python ]; then \
		COZMO_AGENT_MODE=$(WALKIN_AGENT_MODE) $(BIN)/python -m cozmo_floorplan walkin $(WALKIN_ROOT) --out $(WALKIN_OUT); \
	else \
		PYTHONPATH=src COZMO_AGENT_MODE=$(WALKIN_AGENT_MODE) $(PYTHON) -m cozmo_floorplan walkin $(WALKIN_ROOT) --out $(WALKIN_OUT); \
	fi

fmt:
	@echo "No formatter pinned yet."

install-capture-app:
	./scripts/install-cozmo-capture.sh

open-capture-app:
	open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj
