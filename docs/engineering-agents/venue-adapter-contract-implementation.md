# Venue Adapter Contract Implementation

This is the first implementation PR generated from the 50 engineering-agent workflow.

## Scope

Agents covered:

- AG-01 Deribit REST Agent
- AG-03 Binance Public REST Agent
- AG-05 Coinbase Preview Agent
- AG-07 OKX Policy Gate Agent
- AG-09 Venue Capability Agent
- AG-10 Venue Harness Agent

## What this adds

- A normalized venue profile model.
- Capability flags for orderbook, trades, candles, websocket, preview, testnet, account gates and policy gates.
- A dry-run venue adapter harness.
- Preview-only order validation that always keeps live submission disabled.
- A registry for venue readiness summaries.
- Tests proving the harness works with existing market-state validation.

## Safety boundary

This does not add account access, credentials, signing, or live order sending.

The dry-run harness exists so future real adapters can be added behind tests without polluting the execution core or enabling live trading prematurely.

## Next patches

1. Add a deterministic orderbook fixture library.
2. Add Binance snapshot + diff-depth merge fixtures.
3. Add Deribit testnet/public data mapping notes.
4. Add Coinbase preview response normalization fixtures.
5. Add OKX policy watcher integration notes.
