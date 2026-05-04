SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: help bootstrap bootstrap-compat init-db lint test test-compat check smoke release-compliance verify-endpoints reference-check run-backend run-web

help:
	@printf '%s\n' \
	  'Available targets:' \
	  '  make bootstrap           Create .venv, install dev deps, copy .env.example when needed, init DB' \
	  '  make bootstrap-compat    Minimal local fallback bootstrap without package install' \
	  '  make init-db             Initialize or migrate the local SQLite schema' \
	  '  make lint                Run Ruff on src/ and tests/' \
	  '  make test                Run installed-dependency pytest lane' \
	  '  make test-compat         Run repository runtime-compat pytest lane' \
	  '  make check               Run lint + both pytest lanes' \
	  '  make smoke               Run offline CLI smoke checks' \
	  '  make release-compliance  Verify version parity and changelog release discipline' \
	  '  make verify-endpoints    Verify Polymarket public endpoints' \
	  '  make reference-check     Cross-check BTC/ETH/SOL reference prices' \
	  '  make run-backend         Start local backend API on 127.0.0.1:8000' \
	  '  make run-web             Start the web dashboard entrypoint'

bootstrap:
	bash scripts/bootstrap.sh

bootstrap-compat:
	@if [ ! -d "$(VENV_DIR)" ]; then $(PYTHON) -m venv "$(VENV_DIR)"; fi
	@if [ ! -f .env ] && [ -f .env.example ]; then cp .env.example .env; fi
	PYTHONPATH=src $(PYTHON) -m superajan12.cli init-db

init-db:
	$(VENV_PYTHON) -m superajan12.cli init-db

lint:
	$(VENV_PYTHON) -m ruff check src tests

test:
	$(VENV_PYTHON) -m pytest -q -o pythonpath=

test-compat:
	PYTHONPATH=src $(PYTHON) -m pytest -q

check:
	bash scripts/check.sh

smoke:
	bash scripts/smoke.sh

release-compliance:
	bash scripts/release-compliance.sh

verify-endpoints:
	$(VENV_PYTHON) -m superajan12.cli verify-endpoints

reference-check:
	$(VENV_PYTHON) -m superajan12.cli reference-check --symbols BTC,ETH,SOL

run-backend:
	PYTHONPATH=src $(PYTHON) -m superajan12.backend_server --host 127.0.0.1 --port 8000

run-web:
	$(VENV_PYTHON) -m superajan12.web
