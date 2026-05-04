#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python interpreter not found: $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -e .[dev]

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
fi

"$VENV_DIR/bin/python" -m superajan12.cli init-db

echo "Bootstrap complete."
echo "Next steps:"
echo "  source $VENV_DIR/bin/activate"
echo "  make check"
echo "  make smoke"
