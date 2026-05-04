#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"
PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
VENV_PYTHON="$VENV_DIR/bin/python"

run_full() {
  if [ ! -x "$VENV_PYTHON" ]; then
    echo "missing $VENV_PYTHON; run 'make bootstrap' first" >&2
    exit 1
  fi

  "$VENV_PYTHON" -m ruff check src tests
  "$VENV_PYTHON" -m pytest -q -o pythonpath=
}

run_compat() {
  PYTHONPATH=src "$PYTHON_BIN" -m pytest -q
}

case "$MODE" in
  full)
    run_full
    ;;
  compat)
    run_compat
    ;;
  all)
    run_full
    run_compat
    ;;
  *)
    echo "usage: bash scripts/check.sh [full|compat|all]" >&2
    exit 1
    ;;
esac

echo "Validation complete for mode=$MODE"
