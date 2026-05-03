# 50 Engineering Agents Program

This directory defines a development-only agent workflow for SuperAjan12.

Important boundary:

- These agents are not runtime trading agents.
- They do not submit orders.
- They do not run inside the live/paper/shadow execution path.
- They exist to help plan, review, research, test, and safely accelerate engineering work.

Target outcome: move the system from roughly 35/100 maturity toward 50/100 without mixing agent orchestration into the trading runtime.

## Agent distribution

| Group | Count | Mission |
| --- | ---: | --- |
| Venue adapters | 10 | Harden real venue adapter contracts and testnet/live-readiness boundaries. |
| Market data / orderbook / replay | 8 | Make market state deterministic, replayable, and auditable. |
| Risk / capital / kill-switch | 8 | Enforce safety gates before any execution path. |
| Alpha research / backtest | 6 | Convert hypotheses into measurable backtests and promotion evidence. |
| Observability / incident / chaos | 5 | Make system behavior visible, alertable, and recoverable. |
| Dashboard / operator UX | 5 | Improve operator control without adding unsafe automation. |
| Security / secrets / compliance | 4 | Keep credentials, environments, and operational controls safe. |
| Packaging / release / CI | 4 | Keep builds, releases, and validation reproducible. |

## Operating rules

1. Agents produce research notes, implementation plans, test plans, or narrowly scoped patch proposals.
2. Any code change must pass existing tests and add focused regression coverage when behavior changes.
3. No agent may enable live order submission.
4. No agent may introduce fake progress counters into runtime code.
5. Any production/live-related change must be gated behind explicit configuration, dry-run defaults, and operator approval.
6. Work is merged only through normal review, CI, and release checklist rules.

## Files

- `agent-roster.md` lists all 50 agents and their responsibilities.
- `task-board.md` tracks the execution waves from 35/100 to 50/100.
- `merge-rules.md` defines what can and cannot be merged.
- `research-queue.md` lists research questions each agent group must answer before implementation.
