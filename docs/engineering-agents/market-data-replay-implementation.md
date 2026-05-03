# Market Data / Orderbook / Replay Implementation

This patch strengthens the market data layer without enabling live trading.

## Scope

Agents covered:

- AG-11 Snapshot Agent
- AG-12 Diff Merge Agent
- AG-13 Gap Recovery Agent
- AG-14 Checksum Agent
- AG-15 Replay Event Agent
- AG-16 Replay Runner Agent
- AG-17 Fixture Agent
- AG-18 Market-State QA Agent

## What this adds

- Canonical replay event types: snapshot, diff and resnapshot.
- Deterministic orderbook merge logic for bid/ask level updates.
- Sequence gap rejection before bad diffs can mutate the local book.
- Resnapshot recovery after a rejected gap.
- Checksum validation integration through the existing `MarketStateValidator`.
- Reusable Binance-style replay fixtures.
- Regression tests for healthy replay, gap recovery, checksum mismatch, empty replay and custom validator thresholds.

## Safety boundary

This is market data and replay infrastructure only. It does not add API keys, account access, signing, live order submission or venue trading calls.

## Validation

Expected command:

```bash
pytest -q tests/test_orderbook_replay.py tests/test_market_state.py
```

## Next patches

1. Add a local smoke script that runs replay plus existing scanner tests.
2. Add replay report export to JSON for operator review.
3. Add venue-specific checksum implementations once each real venue adapter lands.
4. Add replay-driven risk/capital scenario tests.
