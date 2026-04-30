# SuperAjan12 Research Report

Status: Research Phase 1

## Purpose

This document is the research foundation for SuperAjan12. The goal is not to build a simple bot or a basic dashboard. The goal is to design a serious desktop command-center system that behaves like a live trading/research firm: research teams, market intelligence, wallet intelligence, strategy development, risk control, execution simulation, monitoring, and controlled progression from research to paper, shadow, micro-live, and only then live.

The system must use real data. It must not show fake data in production UI. If a data source is not connected or unavailable, the UI must display `no data`, `source offline`, or `not configured`.

## Non-negotiable principles

1. No fake production data.
2. No live order submission until research, paper, shadow, risk, approval, and reconciliation criteria are satisfied.
3. Risk Engine can block every strategy.
4. Execution Engine must not be able to bypass Risk Engine.
5. Social hype is not edge.
6. Smart-wallet data is research input until proven in paper/shadow.
7. Model-generated strategies must not promote themselves directly to live.
8. Every decision must be auditable.
9. Every connector must have timeout, retry, health state, stale-data detection, and circuit-breaker behavior.
10. Desktop app must remain responsive even when backend sources fail.

## A. How autonomous trading systems should be built

A serious autonomous trading system must be built as a multi-service operating system, not as a single script.

Required layers:

1. Data ingestion layer
2. Research layer
3. Signal layer
4. Strategy layer
5. Risk layer
6. Execution layer
7. Portfolio/reconciliation layer
8. Audit and observability layer
9. Desktop command-center UI

The correct decision flow is:

```text
raw data
-> normalized data
-> research findings
-> candidate signals
-> strategy validation
-> risk validation
-> paper/shadow action
-> performance measurement
-> model/strategy promotion decision
```

For future live mode:

```text
signal
-> strategy engine
-> risk engine
-> capital limit engine
-> execution guard
-> manual/micro-live policy
-> exchange adapter
-> reconciliation
-> audit log
```

## B. Prediction markets vs futures

Research conclusion: futures should be the main execution/market-data domain, while prediction markets should be an event intelligence and cross-market research domain.

Prediction markets are useful for:

- event probability discovery
- crowd pricing of political, sports, macro, crypto, and company events
- cross-checking sentiment and event expectations
- research-driven opportunities

Prediction market risks:

- resolution ambiguity
- low liquidity
- wide spreads
- event interpretation errors
- jurisdiction/platform restrictions

Futures are useful for:

- liquid execution
- high-frequency price discovery
- funding-rate analysis
- open-interest analysis
- volatility and orderbook signals

Futures risks:

- leverage
- liquidation
- funding flips
- cascading volatility
- exchange/API outages
- slippage under stress

Decision:

```text
Primary market intelligence and future execution domain: Binance Futures + OKX.
Reference/spot validation: Coinbase.
Event intelligence: Polymarket + Kalshi.
On-chain research: Nansen/Dune/Glassnode or equivalent.
```

## C. Venue and data-source research

### Polymarket

Polymarket provides separate APIs:

- Gamma API: markets, events, tags, series, profiles and discovery.
- Data API: user positions, trades, activity, holders, open interest and analytics.
- CLOB API: orderbook, prices, midpoints, spreads, price history and trading operations.

Public data is available for Gamma/Data and CLOB read endpoints. Trading endpoints require authentication and signatures.

Official docs:

- https://docs.polymarket.com/api-reference
- https://docs.polymarket.com/trading/orderbook
- https://docs.polymarket.com/api-reference/authentication

Use in SuperAjan12:

- MVP: market/event discovery, orderbook, spread, midpoint, price history.
- Later: WebSocket market channel for real-time orderbook/price/trade updates.
- Not in MVP: live trading.

### Kalshi

Kalshi provides API access for market data, order books, events, series, demo environment, WebSockets and trading.

Official docs:

- https://docs.kalshi.com/welcome
- https://help.kalshi.com/account-and-login/kalshi-api

Use in SuperAjan12:

- MVP: public market data and cross-market event comparison with Polymarket.
- Later: demo environment exploration.
- Not in MVP: live trading.

### Binance Futures

Binance USD-M Futures provides market data such as mark price, funding rate, open interest, orderbook depth and futures-specific metrics.

Use in SuperAjan12:

- MVP: mark price, index price, funding, open interest, orderbook, ticker, klines.
- Later: WebSocket streams for orderbook, trades, liquidation streams if available and allowed.
- Live execution only after production readiness.

### OKX

OKX provides REST and WebSocket market data. Public channels include tickers, order books, trades and candles. Some high-speed orderbook channels require login or VIP tiers.

Official docs:

- https://www.okx.com/docs-v5/en
- https://www.okx.com/docs-v5/trick_en

Use in SuperAjan12:

- MVP: public ticker, orderbook snapshots, funding/open-interest where available.
- Later: WebSocket orderbook streams.
- Must account for channel limitations and authentication/VIP requirements.

### Coinbase

Coinbase Advanced Trade WebSocket market data supports public channels such as ticker, ticker_batch, level2, candles, heartbeats, market_trades and status. User-specific channels require authentication.

Official docs:

- https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-overview
- https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-channels

Use in SuperAjan12:

- MVP: spot reference prices and orderbook reference for BTC/ETH/SOL.
- Not primary execution venue for futures MVP.

## D. Smart-wallet and on-chain tracking methods

Research options:

1. Nansen API
2. Dune API
3. Glassnode API
4. Arkham / other wallet intelligence providers
5. Custom indexer using chain RPC and event parsers

### Nansen

Nansen Smart Money endpoints include netflows, holdings, historical holdings, DEX trades, perpetual trades and other smart-money datasets. This is relevant for wallet intelligence but likely requires API key and credits.

Docs:

- https://docs.nansen.ai/api/smart-money
- https://docs.nansen.ai/api/overview

### Dune

Dune API can run saved queries, track execution status and fetch results. This is useful for custom wallet dashboards and curated on-chain queries.

Docs:

- https://docs.dune.com/api-reference/executions/execution-object

### Glassnode

Glassnode offers live and historical on-chain/market data through REST API but API access is tied to paid plans/add-ons.

Docs:

- https://docs.glassnode.com/basic-api/api

Decision:

```text
Wallet intelligence is research input first.
Do not connect wallet signal directly to live execution until proven in paper/shadow.
MVP should support provider adapters but show no data if API keys are absent.
```

## E. Social-media signal reliability

Social-media signal is dangerous as a standalone trading source.

Risks:

- bots
- coordinated pump campaigns
- fake screenshots
- recycled news
- influencer manipulation
- delayed trend detection
- survivorship bias

Correct use:

- trend discovery
- early event detection
- source clustering
- bot/spam scoring
- cross-source verification
- research task creation

Decision:

```text
Social media = research queue input.
Social media != direct trade signal.
```

MVP must not require social media API on day one. It should have a Research Center interface and adapter slots. Real integrations come after source/API selection and rate-limit research.

## F. News and data-source verification

News must be handled by a verification chain.

Verification questions:

1. Is the source official?
2. Are there multiple independent sources?
3. Is the timestamp reliable?
4. Has price already reacted?
5. Is the event resolution rule clear?
6. Is the data source manipulable?
7. Does the signal conflict with market/futures/on-chain data?

Required components:

- Source registry
- Source credibility scoring
- Timestamp normalization
- Deduplication
- Cross-source verification
- Event-to-market mapping
- Resolution-rule checker

Decision:

```text
News Reliability Engine and Resolution Engine are mandatory.
No verified source -> no action beyond research/watch.
```

## G. Architecture for a non-freezing, non-crashing system

The requirement is not literally "never fail"; the practical requirement is graceful degradation, recovery, monitoring and isolation.

Architecture requirements:

1. Desktop UI must not block on external APIs.
2. Backend workers must be isolated from UI.
3. Connectors must have timeouts and retries.
4. Failed source must degrade to `offline/stale`, not freeze the app.
5. Data bus or internal event stream must decouple ingestion from processing.
6. Market snapshots must be cached.
7. Audit log must be append-only.
8. Health checks must exist for every source and engine.
9. Circuit breakers must protect the system from repeated source failures.
10. Execution must run in a separate guarded path.

Recommended architecture:

```text
Tauri Desktop App
-> Python sidecar backend
-> FastAPI local API + WebSocket stream
-> worker processes for connectors/research/strategy/risk
-> SQLite for MVP
-> optional Postgres/TimescaleDB for scaled history
-> optional Redpanda/Kafka-compatible event bus for high-throughput streams
-> optional Temporal for durable long-running workflows
```

Supporting references:

- Tauri sidecars can package external binaries such as Python CLI/API servers: https://v2.tauri.app/fr/develop/sidecar/
- Temporal provides durable execution with retries and state recovery: https://temporal.io/
- Redpanda is Kafka-compatible and designed for streaming workloads: https://docs.redpanda.com/current/home/

## H. Risk and capital protection architecture

Risk is the core product. Strategy is secondary.

Risk controls:

- max single-trade risk
- max total open risk
- max daily loss
- max leverage
- liquidation distance
- funding-rate risk
- spread/slippage risk
- stale data detection
- connector health gating
- correlation exposure
- asset concentration
- safe mode
- kill switch
- reconciliation mismatch block
- model version approval block

Rule:

```text
Strategy can request action.
Risk decides if action is allowed.
Execution cannot bypass risk.
```

## I. Research -> Paper -> Shadow -> Micro-live transition plan

Progression:

1. Research mode: collect and explain; no positions.
2. Paper mode: simulated positions from real data.
3. Shadow mode: decision as-if live, no real orders.
4. Micro-live: tiny size, manual approval, strict limits.
5. Controlled live: limited autonomous scope.
6. Autonomous live: only after extensive evidence.

Gate criteria before micro-live:

- 500+ scanned markets.
- 100+ paper positions.
- meaningful shadow outcomes.
- positive strategy score across multiple periods.
- stable endpoints.
- stable audit logs.
- approved model version.
- tested kill switch.
- tested reconciliation.
- legal/platform eligibility verified.

## J. Minimum viable desktop system

MVP must be a desktop command center, not a web page.

Required MVP screens:

1. Command Center
2. Research Center
3. Market Intelligence
4. Wallet / On-chain Intelligence
5. Strategy Lab
6. Risk Center
7. Paper / Shadow Positions
8. Audit Log
9. System Health

Required MVP behavior:

- Uses real data from configured sources.
- Shows `not configured` if source/API key is missing.
- Shows `offline` or `stale` if source fails.
- No fake production rows.
- No live order submission.
- Every action is logged.
- UI feels alive through real refresh, live feeds, health states and event logs.

## Current conclusion

The previous web panel is only a prototype and should not be treated as final. The next correct build target is:

```text
SuperAjan12 Desktop Command Center
Tauri UI + Python sidecar backend + real data connectors + paper/shadow engine + research/risk/strategy operating system
```

