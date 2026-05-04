# SuperAjan12 Secret Inventory

This document tracks secret classes, their intended scope, minimum permission boundary, storage expectations, and rotation owner. It never stores secret values.

## Rules

- No secret values belong in git, screenshots, issue comments, PR reviews, or audit payloads.
- Every secret must have a single named owner.
- Every secret must have the minimum permission scope needed for its runtime path.
- Live-capable secrets stay out of local `.env` files unless the operator intentionally accepts the local-risk tradeoff.
- Withdrawal, transfer, custody, or portfolio-wide write scopes are out of bounds for this project.

## Secret classes

| Secret | Purpose | Required for current paper/shadow mode | Future live relevance | Minimum scope | Storage expectation | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| `SUPERAJAN12_LIVE_API_KEY` | Exchange or venue API identity for future live-capable preview paths | No | Yes | Trade-preview or restricted execution only; never withdrawal | External secret manager preferred; environment injection allowed for isolated local testing | Operator |
| `SUPERAJAN12_LIVE_API_SECRET` | Paired signing/auth secret for future live-capable preview paths | No | Yes | Same scope as paired API key; never withdrawal | External secret manager preferred; environment injection allowed for isolated local testing | Operator |
| `DUNE_API_KEY` | Wallet and on-chain research provider access | No | Optional research only | Read-only analytics | Environment or external secret manager | Research owner |
| `NANSEN_API_KEY` | Wallet and smart-money research provider access | No | Optional research only | Read-only analytics | Environment or external secret manager | Research owner |
| `GLASSNODE_API_KEY` | On-chain metrics provider access | No | Optional research only | Read-only analytics | Environment or external secret manager | Research owner |
| `X_BEARER_TOKEN` | Social/news enrichment source | No | Optional research only | Read-only API access | Environment or external secret manager | Research owner |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | Reddit-based research ingestion | No | Optional research only | Read-only API access | Environment or external secret manager | Research owner |
| `COINGECKO_API_KEY` | CoinGecko premium/news endpoints if enabled | No | Optional reference/research only | Read-only market/news access | Environment or external secret manager | Research owner |

## Current enforcement boundary

Current paper/shadow operation does not require any live-trading secret. The backend already reports missing live execution secrets as a blocking readiness condition.

## Rotation metadata to track

Every secret should have these fields recorded outside git:

- secret name
- owner
- provider or venue
- scope granted
- creation time
- last rotated time
- next rotation due time
- last validation time
- emergency disable path

## Scope policy

Allowed future scope:

- read-only market-data access
- preview-only or tightly scoped trade access when live gates are explicitly unlocked later

Forbidden scope:

- withdrawals
- transfers
- account recovery actions
- sub-account creation
- wildcard organization-wide admin access

## Local development guidance

- Prefer `.env` only for public-data or read-only research credentials.
- Treat any live-capable credential as production-sensitive even during local testing.
- Remove local credentials immediately after troubleshooting.
- Re-run secret scanning before every push.

## Audit expectation

Any future live-capable secret onboarding should leave evidence in operator documentation:

- who created it
- what scope was granted
- where it is stored
- when it was last rotated
- which runbook was used

## Related docs

- `docs/SECRET_ROTATION_RUNBOOK.md`
- `docs/COMPLIANCE_BOUNDARY.md`
- `docs/PRODUCTION_CHECKLIST.md`
- `docs/RUNBOOK.md`
