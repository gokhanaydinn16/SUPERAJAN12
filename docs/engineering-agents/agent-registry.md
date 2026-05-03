# 50 Engineering Agent Registry

This registry assigns the 50 development-support agents. These agents support engineering work only; they are not runtime trading agents.

## Venue adapter agents

### AG-01 Deribit REST Agent
- Scope: Deribit public/testnet REST contract research and adapter patch plan.
- Review: venue adapter code, endpoint docs, tests.
- Output: mapping table, fake response fixtures, adapter test checklist.

### AG-02 Deribit WebSocket Agent
- Scope: Deribit streaming orderbook/trade subscriptions.
- Review: reconnect, subscription, sequence behavior.
- Output: WS lifecycle plan and failure cases.

### AG-03 Binance Public REST Agent
- Scope: Binance spot/futures exchange info, ticker, orderbook, mark/funding endpoints.
- Output: normalized adapter mapping and rate-limit notes.

### AG-04 Binance Diff-Depth Agent
- Scope: snapshot + diff-depth merge logic.
- Output: gap recovery design and deterministic fixture cases.

### AG-05 Coinbase Preview Agent
- Scope: Coinbase Advanced Trade preview-only order path.
- Output: dry-run preview contract and response normalization.

### AG-06 Coinbase Product/Portfolio Agent
- Scope: product, account and portfolio boundary research.
- Output: account separation constraints and test fixtures.

### AG-07 OKX Policy Gate Agent
- Scope: OKX API agreement, KYC/account gate and policy readiness.
- Output: policy watcher input requirements.

### AG-08 OKX Market Data Agent
- Scope: ticker, book and candle mapping.
- Output: adapter contract and rate-limit notes.

### AG-09 Venue Capability Agent
- Scope: shared venue capability schema.
- Output: capability registry fields and readiness blockers.

### AG-10 Venue Harness Agent
- Scope: fake venue harness for all adapter tests.
- Output: reusable fixture protocol.

## Market data / orderbook / replay agents

### AG-11 Snapshot Agent
- Scope: canonical orderbook snapshot model.
- Output: required fields and validation rules.

### AG-12 Diff Merge Agent
- Scope: deterministic merge of book diffs into snapshots.
- Output: merge algorithm spec and tests.

### AG-13 Gap Recovery Agent
- Scope: sequence gap detection, quarantine, resnapshot.
- Output: recovery state machine.

### AG-14 Checksum Agent
- Scope: venue-aware checksum validation.
- Output: checksum policy by venue.

### AG-15 Replay Event Agent
- Scope: replay event schema.
- Output: event envelope and persistence requirements.

### AG-16 Replay Runner Agent
- Scope: deterministic replay runner CLI/API.
- Output: runner design and pass/fail criteria.

### AG-17 Fixture Agent
- Scope: reusable market data fixtures.
- Output: fixture inventory and naming convention.

### AG-18 Market-State QA Agent
- Scope: regression tests for stale, synthetic, gap and checksum cases.
- Output: expanded test matrix.

## Risk / capital / kill-switch agents

### AG-19 Position Cap Agent
- Scope: hard position cap and notional cap enforcement.
- Output: cap scenario table.

### AG-20 Daily Loss Agent
- Scope: daily loss buffer and shutdown behavior.
- Output: drawdown gate policy.

### AG-21 Stale Data Lock Agent
- Scope: stale market data vetoes.
- Output: stale lock rules and tests.

### AG-22 Disconnect Lock Agent
- Scope: disconnect/cancel behavior.
- Output: cancel-on-disconnect policy and tests.

### AG-23 Capital Ladder Agent
- Scope: capital budgets by paper/shadow/testnet/canary/scaled stage.
- Output: stage budget table.

### AG-24 Kill Switch Agent
- Scope: soft/hard kill switch state machine.
- Output: release protocol and audit requirements.

### AG-25 Pre-Trade Veto Agent
- Scope: normalized veto reasons.
- Output: veto taxonomy.

### AG-26 Risk QA Agent
- Scope: risk regression test suite.
- Output: must-pass scenarios.

## Alpha research / backtest agents

### AG-27 Feature Registry Agent
- Scope: candidate feature inventory and feature provenance.
- Output: feature registry draft.

### AG-28 Metrics Agent
- Scope: backtest metrics and calibration.
- Output: metrics contract.

### AG-29 Slippage Agent
- Scope: slippage/fill quality model.
- Output: paper-shadow-live gap model.

### AG-30 Walk-Forward Agent
- Scope: anti-overfit validation splits.
- Output: walk-forward policy.

### AG-31 Promotion Gate Agent
- Scope: model promotion policy.
- Output: promotion criteria and blockers.

### AG-32 Alpha Report Agent
- Scope: decision quality report.
- Output: report template.

## Observability / incident / chaos agents

### AG-33 Metrics Taxonomy Agent
- Scope: production metrics.
- Output: metric names, types, thresholds.

### AG-34 Trace Agent
- Scope: trace ids and event chain linking.
- Output: trace propagation plan.

### AG-35 Incident Agent
- Scope: open/ack/resolve/postmortem lifecycle.
- Output: incident model and tests.

### AG-36 Chaos Agent
- Scope: failure injection matrix.
- Output: chaos scenarios.

### AG-37 Alert Agent
- Scope: alert thresholds and operator escalation.
- Output: alert table.

## Dashboard / operator UX agents

### AG-38 Readiness UX Agent
- Scope: stage/readiness blocker screen.
- Output: operator UI spec.

### AG-39 Risk UX Agent
- Scope: caps, locks, vetoes view.
- Output: risk panel spec.

### AG-40 Venue UX Agent
- Scope: venue capability/health panel.
- Output: venue panel spec.

### AG-41 Replay UX Agent
- Scope: replay/backtest run screen.
- Output: replay UX flow.

### AG-42 Incident UX Agent
- Scope: incident/postmortem screen.
- Output: incident UX flow.

## Security / secrets / compliance agents

### AG-43 Secret Inventory Agent
- Scope: required env-only secret list.
- Output: secret inventory without values.

### AG-44 Secret Rotation Agent
- Scope: owner/provider/age checks.
- Output: rotation policy.

### AG-45 Compliance Boundary Agent
- Scope: live trading constraints and non-goals.
- Output: compliance guardrails.

### AG-46 Audit Policy Agent
- Scope: tamper-evident audit requirements.
- Output: audit retention and integrity plan.

## Packaging / release / CI agents

### AG-47 CI Agent
- Scope: unit/runtime/desktop/release lanes.
- Output: CI improvement backlog.

### AG-48 Release Artifact Agent
- Scope: wheel/web/desktop bundle policy.
- Output: artifact checklist.

### AG-49 Local Smoke Agent
- Scope: one-command local smoke test.
- Output: smoke script requirements.

### AG-50 Merge Manager Agent
- Scope: final review and merge gate.
- Output: PR checklist and rollback plan.
