# Merge Rules for Engineering Agents

These rules keep the 50-agent workflow from polluting the trading runtime.

## Hard boundaries

1. Engineering-agent docs must stay under `docs/engineering-agents/`.
2. Engineering-agent orchestration must not be imported by `src/superajan12`.
3. No PR may enable live order sending.
4. No PR may commit API keys, secrets, tokens, `.env`, SQLite databases, JSONL audit logs, or local runtime data.
5. Any connector or adapter that can touch accounts must default to dry-run/testnet-disabled mode until production checklist requirements are met.

## Required evidence before merge

Every implementation PR created from the agent workflow must include:

- files changed
- risk impact
- test command and result
- rollback plan
- operator-visible change, if any
- statement confirming live trading remains disabled

## Test gates

Minimum expected validation by change class:

- Documentation only: markdown review and no runtime imports added.
- Adapter contract: unit tests with fake venue responses.
- Market data/orderbook: deterministic fixture tests for snapshot, diff, gap, and checksum behavior.
- Risk/capital: scenario tests proving vetoes cannot be bypassed.
- Replay/backtest: deterministic replay test with fixed input and expected output.
- Dashboard: endpoint smoke test and browser/static asset sanity check.
- Security/secrets: negative tests proving secret values are never logged.
- CI/release: workflow syntax review and dry-run notes.

## PR labels

Recommended labels:

- `area:venue`
- `area:market-data`
- `area:risk`
- `area:alpha`
- `area:observability`
- `area:ux`
- `area:security`
- `area:release`
- `safety:live-disabled`

## Merge manager checklist

AG-50 must confirm:

1. Scope matches one or more agent tasks.
2. Runtime impact is intentional and documented.
3. Live execution remains disabled unless a future production checklist explicitly authorizes otherwise.
4. Tests are appropriate for the touched area.
5. Docs and runbooks are updated when operator behavior changes.
6. The PR can be reverted cleanly.
