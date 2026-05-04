# Risk / Capital / Kill-Switch Hardening

This patch collects work from the expanded 200-agent execution board, focused on AG-051..AG-095.

## Scope

- hard market exposure caps
- total exposure caps
- daily loss guard
- stale-data lock
- disconnect lock
- safe-mode veto
- kill-switch veto
- pre-trade veto taxonomy
- scenario tests proving vetoes cannot be bypassed

## What this adds

- `RiskControlContext` for operator/runtime safety state.
- `PreTradeVetoCode` taxonomy for operator-readable rejection reasons.
- `PreTradeVeto` to carry structured veto sources.
- RiskEngine integration while keeping existing arguments backward-compatible.
- Tests for kill switch, safe mode, disconnect, stale data, daily loss, market cap, total exposure cap and extra veto injection.

## Safety boundary

This does not enable live order submission. It makes pre-trade gating stricter.

## Expected validation

```bash
pytest -q tests/test_risk_engine.py
```

## Next patches

1. Add a standalone kill-switch state machine with release protocol.
2. Add capital ladder by stage: paper -> shadow -> testnet -> canary -> scaled-live.
3. Wire risk-control context into execution guard and backend/API operator status.
4. Add incident/log events for each veto source.
