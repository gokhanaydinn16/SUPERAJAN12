# Contributing

## Goal

Keep SuperAjan12 easy to run, easy to validate, and hard to accidentally weaken.

## Ground rules

- Default to paper and shadow workflows.
- Do not add live order submission by default.
- Do not commit secrets, runtime databases, or audit logs.
- Prefer focused pull requests with a clear validation path.
- Update docs when behavior, commands, or operational expectations change.

## Issue-driven workflow

- Start each meaningful change from an issue or an explicit sub-task linked to an issue.
- Keep every branch scoped to one issue or one clearly named wave of an issue.
- Close issues only when acceptance criteria are met, not when partial progress exists.
- Use issue bodies to capture `Problem`, `Scope`, `Acceptance Criteria`, `Out of Scope`, and `Risk`.

## Branch naming

Use these branch formats:

- `codex/<issue-no>-<short-kebab>` for normal engineering work
- `hotfix/<issue-no>-<short-kebab>` for urgent production-facing fixes

Examples:

- `codex/31-replay-market-state-gate`
- `codex/8-runtime-startup-lifecycle`
- `hotfix/54-release-icon-regression`

## Local setup

Recommended path:

```bash
make bootstrap
make check
make smoke
```

Fallback path for constrained environments:

```bash
make bootstrap-compat
bash scripts/check.sh compat
bash scripts/smoke.sh
```

## Validation lanes

Use these commands before opening or merging a PR:

```bash
make lint
make test
make test-compat
make smoke
pytest -q tests/test_orderbook_replay.py tests/test_market_state.py
```

Network-backed checks are intentionally separate:

```bash
make verify-endpoints
make reference-check
```

## Documentation touch points

When you change developer workflow, release flow, or operator expectations, review these files too:

- `README.md`
- `docs/DEVELOPMENT.md`
- `docs/STATUS.md`
- `docs/HANDOFF.md`
- `docs/RUNBOOK.md`
- `docs/RELEASE.md`
- `docs/ACTIVE_EXECUTION_QUEUE.md`
- `CHANGELOG.md`

## Pull request expectations

A good PR should state:

1. What changed.
2. Why it changed.
3. Safety boundary, especially if runtime or execution code is touched.
4. Validation commands used.
5. Rollback notes or follow-up work left visible.

## Preferred change shape

- Keep changes rollback-friendly.
- Reuse existing repo patterns before inventing new abstractions.
- Add tests when behavior changes.
- If full runtime dependencies are unavailable, keep the runtime-compat lane green.
- Prefer one behavior change per PR plus the matching test and doc updates.
- Keep merge-aftercare explicit: update `docs/ACTIVE_EXECUTION_QUEUE.md` when the current blocker or next technical move changes.
