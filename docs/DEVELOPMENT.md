# SuperAjan12 Development Guide

## Purpose

This guide makes the repository easier to re-enter, validate, and extend without re-discovering the local workflow each time.

## Recommended local workflow

```bash
make bootstrap
make check
make smoke
```

What this gives you:

- a local virtual environment in `.venv`
- dev dependencies installed
- `.env` created from `.env.example` when available
- local SQLite schema initialized
- lint, test, and offline smoke commands ready to run

## Constrained environment workflow

If package installation or registry access is blocked, use the repository fallback path:

```bash
make bootstrap-compat
bash scripts/check.sh compat
bash scripts/smoke.sh
```

This path keeps the Python source tree and local compatibility modules usable even when full dependency setup is unavailable.

## Command map

### Core validation

```bash
make lint
make test
make test-compat
make check
make smoke
```

### Network-backed validation

```bash
make verify-endpoints
make reference-check
```

### Runtime entrypoints

```bash
make run-backend
make run-web
```

## Local security gate

Install pre-commit once if you want the same secret leak check before commit that CI now runs:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

This uses `.pre-commit-config.yaml` and `.gitleaks.toml` to scan for accidental secret commits before code leaves your machine.

## Dependency audit lane

CI now runs a separate dependency vulnerability lane for both Python and desktop web dependencies.

A close local equivalent is:

```bash
pip install pip-audit
pip-audit
cd apps/desktop && npm install && npm audit --audit-level=high
```

Use this before opening a PR when dependency versions or lockfile behavior change.

## When to use each lane

- `make test`: use when the package is installed into `.venv` and you want the real dependency lane.
- `make test-compat`: use when you need to prove the repository's fallback runtime still works.
- `make check`: use before PRs or when touching shared code paths.
- `make smoke`: use for quick confidence that the local CLI/reporting surfaces still start and query storage.

## Working agreements for future changes

- Prefer adding one stable entrypoint over many ad hoc shell snippets.
- Keep offline checks available whenever possible.
- Keep network-dependent checks explicit so failures are easier to diagnose.
- Document new commands in the Makefile and README at the same time.
- If an implementation changes operator expectations, update `docs/RUNBOOK.md` and `docs/PRODUCTION_CHECKLIST.md` too.

## Suggested first commands after pulling new changes

```bash
make bootstrap
make smoke
make check
```
