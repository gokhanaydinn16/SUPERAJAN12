# 200 Engineering Agent Execution Board

This board expands the existing 50-agent workflow into 200 implementation tasks. These are engineering-support agents, not runtime trading bots. They do not run inside the trading system and they do not enable live orders.

## Operating boundary

- Engineering agents produce research, patch plans, tests and review evidence.
- Runtime code changes only happen through normal PRs.
- Live order submission remains disabled until production checklist and manual approval gates are complete.
- No secrets, credentials, account keys or local runtime databases may be committed.

## Wave 1: 35/100 -> 50/100

1. Venue adapter contracts and fake harness.
2. Market data / orderbook / deterministic replay.
3. Risk / capital / kill-switch hardening.
4. Operator readiness surface.
5. Local smoke and CI enforcement.

## Agent allocation

| Range | Area | Objective |
|---|---|---|
| AG-001..AG-025 | Venue adapters | Deribit, Binance, Coinbase, OKX contracts, fixtures, public/testnet boundaries |
| AG-026..AG-050 | Market data | Snapshot/diff/checksum/gap/replay fixture coverage |
| AG-051..AG-075 | Risk and capital | Hard caps, daily loss, exposure, stale data, veto taxonomy |
| AG-076..AG-095 | Kill switch and safety | Soft/hard kill, release gates, disconnect and safe-mode behavior |
| AG-096..AG-120 | Alpha/backtest | Feature registry, replay metrics, slippage, walk-forward validation |
| AG-121..AG-140 | Observability | Metrics, traces, incident lifecycle, alert taxonomy, chaos tests |
| AG-141..AG-160 | Operator UX | Readiness, risk, venue, replay, incident screens |
| AG-161..AG-175 | Security/secrets | Secret inventory, rotation, no-leak tests, audit retention |
| AG-176..AG-190 | Release/CI | Unit, runtime-compat, desktop, smoke, release artifact gates |
| AG-191..AG-200 | Merge and QA | Final review, rollback plans, documentation, readiness scoring |

## Current collected batch

This branch collects work from AG-051..AG-095 first:

- hard position/exposure caps
- daily loss guard
- stale-data lock
- disconnect lock
- kill-switch veto
- pre-trade veto reason taxonomy
- scenario tests for the risk engine

## Definition of done for this batch

- Existing risk behavior remains backward compatible.
- New scenario tests prove vetoes cannot be bypassed.
- Live order submission remains disabled.
- Risk decisions expose explicit, operator-readable reasons.
