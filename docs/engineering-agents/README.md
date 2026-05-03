# 50 Engineering Agent Workflow

This folder defines the 50-agent development support system for SuperAjan12.

Important boundary: these agents are not runtime trading agents. They do not place orders, do not run inside `src/superajan12`, and do not change live execution behavior directly. They are engineering roles used to research, review, test, and prepare changes faster.

Target improvement: move the system from roughly 35/100 readiness toward 50/100 by focusing on the largest missing engineering areas.

## Operating rules

1. Every agent must produce evidence: research notes, patch plan, tests, or review findings.
2. No agent may enable live order submission.
3. No agent may add secrets or credentials to the repository.
4. Any code change must be covered by tests or a documented validation path.
5. Runtime trading code and engineering workflow documentation must stay separate.
6. Merge candidates must pass the merge rules in `merge-rules.md`.

## Agent groups

- Agents 01-10: real venue adapters
- Agents 11-18: market data, orderbook, replay
- Agents 19-26: risk, capital, kill switch
- Agents 27-32: alpha research and backtest
- Agents 33-37: observability, incident, chaos
- Agents 38-42: dashboard and operator UX
- Agents 43-46: security, secrets, compliance
- Agents 47-50: packaging, release, CI

## Deliverable format

Each agent should report with this shape:

```text
Agent: AG-XX Name
Scope:
Files reviewed:
Research sources:
Findings:
Patch proposal:
Tests required:
Risks:
Ready for implementation: yes/no
```

## Readiness goal

50/100 is not production-live. It means:

- testnet/paper/shadow paths are more realistic,
- adapter contracts are actionable,
- replay and backtest can evaluate decisions,
- safety gates are harder to bypass,
- operators can see system state and incidents,
- CI/release is stable enough for regular development.
