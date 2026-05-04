#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if [ -x "$VENV_DIR/bin/python" ]; then
  RUNNER="$VENV_DIR/bin/python"
else
  RUNNER="$PYTHON_BIN"
fi

run_cli() {
  if [ "$RUNNER" = "$PYTHON_BIN" ]; then
    PYTHONPATH=src "$RUNNER" -m superajan12.cli "$@"
  else
    "$RUNNER" -m superajan12.cli "$@"
  fi
}

run_cli init-db
run_cli report --top 1
run_cli shadow-report
run_cli strategy-list --limit 1
run_cli model-list --limit 1
run_cli model-history --limit 1
run_cli model-policy --limit 1
run_cli operations-report

echo "Offline smoke checks completed."
echo "For network-backed checks, run: make verify-endpoints && make reference-check"
