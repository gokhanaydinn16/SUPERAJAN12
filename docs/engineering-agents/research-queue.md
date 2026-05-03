# Research Queue

This queue converts the 50 engineering agents into concrete research and implementation preparation work. Results should be added as notes or follow-up PRs; do not modify trading runtime behavior from this folder alone.

## Wave A - must unblock 50/100 readiness

1. Deribit public/testnet API contract: instruments, orderbook, trades, auth boundary, testnet caveats.
2. Binance spot and futures public book contract: snapshot endpoint, diff stream semantics, sequence gap handling.
3. Coinbase Advanced Trade preview contract: preview-only order path, product mapping, portfolio isolation.
4. OKX market data and policy gate: account/KYC constraints, market data endpoints, rate-limit implications.
5. Canonical orderbook event model: snapshot, diff, checksum, venue timestamp, local receipt timestamp.
6. Replay event format: source, sequence, decision context, risk gate result, paper fill, shadow mark.
7. Capital ladder: paper -> shadow -> testnet/demo -> canary -> scaled-live, with maximum risk per stage.
8. Kill-switch release conditions: who/what can release, cooldown, audit trail, postmortem requirement.
9. Backtest metrics: realized/unrealized PnL, max drawdown, hit rate, calibration, slippage impact.
10. Operator cockpit gaps: readiness blockers, venue health, risk locks, incident state.

## Wave B - implementation preparation

1. Build fake venue harness for deterministic adapter tests.
2. Build data fixtures for orderbook merge and replay.
3. Build smoke script for local API and dashboard checks.
4. Build incident lifecycle regression tests.
5. Build secret inventory checker that never prints secret values.
6. Build CI lane for unit + smoke + docs validation.

## Research note template

```text
Topic:
Agent:
Sources checked:
Current repo support:
Gap:
Recommended patch:
Tests required:
Safety concerns:
```

## Safety note

Research must not result in live order execution being enabled. Any live adapter work must stay behind explicit dry-run/testnet gates until production checklist requirements are met.
