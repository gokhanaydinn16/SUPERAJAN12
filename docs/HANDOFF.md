# SuperAjan12 Handoff

## Project state

SuperAjan12 is ready for paper/shadow operation. It is not a live trading bot and does not submit real orders.

## Completed layers

1. Public market data connectors.
2. Polymarket scanner.
3. Risk engine.
4. Resolution agent.
5. Probability baseline.
6. Liquidity agent.
7. Manipulation risk agent.
8. News reliability agent.
9. Social signal agent.
10. Smart wallet placeholder.
11. Crypto reference checks.
12. Cross-market matching.
13. Paper positions.
14. Shadow mark-to-market.
15. Strategy scoring.
16. Model version registry.
17. SQLite persistence.
18. JSONL audit log.
19. Reconciliation scaffold.
20. Manual approval gate.
21. Secret manager scaffold.
22. Capital limit engine.
23. Execution guard.
24. Dry-run live connector.
25. CLI operations.
26. Tests and CI.
27. Runbook and production checklist.

## Main commands

```bash
superajan12 init-db
superajan12 verify-endpoints
superajan12 reference-check --symbols BTC,ETH,SOL
superajan12 scan --limit 25
superajan12 report
superajan12 shadow-report
superajan12 strategy-score --name baseline --pnl 1.2,-0.5,0.8 --save
superajan12 strategy-list --limit 10
superajan12 model-register --name probability --version 0.1.0 --status candidate --notes baseline
superajan12 model-list --limit 20
superajan12 reconcile --local 0 --external 0
superajan12 capital-check --requested-risk 5 --open-risk 10 --daily-pnl -1
superajan12 execution-check --mode paper
```

## Safety position

The project intentionally stops before real order submission. The dry-run live connector only prepares order-shaped data after an execution guard decision. It does not call a trading endpoint.

## Before any live work

Follow `docs/PRODUCTION_CHECKLIST.md` and `docs/RUNBOOK.md`.

Minimum required evidence before live adapter development:

- 500+ scanned markets.
- 100+ paper positions.
- Shadow outcome history.
- Positive strategy scores across multiple market periods.
- Approved model version.
- Stable endpoint verification.
- Stable reference price verification.
- Reconciliation design against the actual venue.
- Manual approval process.
- Secrets stored outside git.

## Next engineering tasks

1. Run the system locally and collect paper/shadow data.
2. Inspect real Polymarket token id behavior across many markets.
3. Add automated shadow marking from latest market price.
4. Add category-level performance reports.
5. Add model promotion policy enforcement in CLI.
6. Add real on-chain data connector only after source selection.
7. Add real social data connector only after rate limits and source quality are defined.
8. Keep live order sending disabled until production checklist is complete.

## Handoff conclusion

This phase is complete. The repository is ready for local paper/shadow operation and validation. It is safe to move to the next task while this system collects data in paper mode.
