# SuperAjan12 Desktop Architecture

Status: Architecture v1

## Goal

SuperAjan12 must become a standalone desktop command-center application, not a browser-only dashboard. The app should feel like a live research/trading operations room while using real data and explicit no-data/offline states.

## Architecture decision

```text
Tauri Desktop App
  -> Local UI shell
  -> Python backend sidecar
      -> FastAPI local API
      -> local WebSocket/event stream
      -> connector workers
      -> research/market/wallet/strategy/risk services
      -> SQLite for MVP
      -> append-only audit log
```

## Why this direction

- Desktop app opens as one application.
- Python backend already contains useful trading/research logic.
- Tauri can package sidecar binaries.
- UI remains local and responsive.
- Backend services can fail/degrade without freezing the desktop shell.
- No production fake data is required.

## App modules

### 1. Command Center

Purpose: global system overview.

Shows:

- system mode: research, paper, shadow, micro-live-prep
- live orders disabled state
- source health summary
- active research tasks
- open opportunities
- risk blocks
- paper positions
- shadow PnL
- system health

### 2. Research Center

Purpose: research workflow and intelligence collection.

Shows:

- configured sources
- research tasks
- event findings
- source credibility
- timestamp and freshness
- verification state
- notes and audit trail

No fake rows. If no sources are configured, show `not configured`.

### 3. Market Intelligence

Purpose: live market data and cross-market comparison.

Shows:

- Polymarket markets
- Kalshi events
- Binance futures
- OKX market data
- Coinbase reference prices
- spread, volume, funding, open interest, volatility
- source freshness
- opportunity map

### 4. Wallet Intelligence

Purpose: on-chain and smart-wallet research.

Shows:

- provider status: Dune/Nansen/Glassnode/custom
- whale/smart-money feed
- token flow summaries
- exchange inflow/outflow
- confidence and source labels

If provider is absent, show `not configured`.

### 5. Strategy Lab

Purpose: strategy creation, paper/shadow scoring and model promotion.

Shows:

- strategy candidates
- paper/shadow results
- win rate
- average PnL
- drawdown
- model versions
- promotion status

### 6. Risk Center

Purpose: capital protection and hard gating.

Shows:

- max daily loss
- max single-trade risk
- total open risk
- leverage cap
- liquidation distance
- funding risk
- source-health gating
- safe mode
- kill switch
- why blocked

### 7. Execution Center

Purpose: pipeline visibility without live order sending in MVP.

Shows:

```text
research -> signal -> strategy -> risk -> approval -> paper/shadow execution
```

No live order submission in MVP.

### 8. Paper / Shadow Positions

Purpose: simulated and shadow performance tracking.

Shows:

- position id
- market/symbol
- side
- entry
- latest
- unrealized PnL
- risk
- rationale
- source freshness

### 9. Audit Log

Purpose: append-only explanation and forensic review.

Shows:

- decision events
- source failures
- risk blocks
- paper/shadow actions
- model registration
- strategy scoring
- manual approval actions

### 10. System Health

Purpose: operational reliability.

Shows:

- source health
- latency
- stale data
- worker status
- backend uptime
- database status
- audit log status
- circuit breaker states

## Backend services

Recommended packages/modules:

```text
superajan12/backend/api.py
superajan12/backend/events.py
superajan12/backend/health.py
superajan12/connectors/*
superajan12/research/*
superajan12/market/*
superajan12/wallet/*
superajan12/strategy/*
superajan12/risk/*
superajan12/execution/*
superajan12/storage/*
```

## Local API contract v1

REST endpoints:

```text
GET  /health
GET  /sources
GET  /dashboard
POST /scan
GET  /research/tasks
GET  /markets
GET  /wallet/events
GET  /strategy/scores
GET  /risk/status
GET  /positions
GET  /audit/events
```

WebSocket/event stream:

```text
/source.health
/research.event
/market.snapshot
/wallet.event
/strategy.event
/risk.block
/position.update
/audit.event
```

## No-fake-data policy

Desktop UI must never show fake production values.

Allowed UI states:

- not configured
- offline
- stale
- loading
- no data
- live
- error

Demo/mock data is allowed only in tests or explicitly labeled design demo mode.

## Failure behavior

If a connector fails:

1. mark source offline or stale
2. write audit event
3. keep UI responsive
4. do not create new action from stale data
5. risk system blocks affected actions

## MVP implementation order

1. Create `apps/desktop/` Tauri shell.
2. Keep Python backend as sidecar target.
3. Expose stable local API endpoints.
4. Implement source health model.
5. Build Command Center screen.
6. Build Market Intelligence screen using real current backend data.
7. Build Research Center with not-configured states.
8. Build Risk Center and Paper/Shadow screens.
9. Add local event stream.
10. Retire simple web dashboard or keep it as developer-only.
