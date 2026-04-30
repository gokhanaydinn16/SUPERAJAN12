#!/usr/bin/env bash
set -e

python -m pip install --upgrade pip
pip install -e '.[dev]'

if [ ! -f .env ]; then
  cp .env.example .env
fi

superajan12 init-db
pytest -q
ruff check src tests

echo "Setup complete. Next run: superajan12 verify-endpoints"
