# Source Deep Dive: On-chain and Smart Wallet Intelligence

## Role in SuperAjan12

On-chain and smart-wallet intelligence is a research and confirmation layer. It should not directly trigger live execution. It helps identify abnormal flows, whale activity, smart-money behavior, exchange inflows/outflows, token accumulation and distribution patterns.

## Candidate providers

### Nansen

Potential use:

- smart-money wallet labels
- netflows
- holdings
- historical holdings
- DEX trades
- perpetual trades
- entity/wallet intelligence

Docs:

- https://docs.nansen.ai/api/overview
- https://docs.nansen.ai/api/smart-money

### Dune

Potential use:

- custom SQL-based blockchain analysis
- saved query execution
- query result retrieval
- project-specific wallet dashboards
- curated strategy research datasets

Docs:

- https://docs.dune.com/api-reference/overview/introduction
- https://docs.dune.com/api-reference/executions/execution-object

### Glassnode

Potential use:

- historical and live on-chain metrics
- exchange flows
- supply metrics
- market indicators
- macro crypto network intelligence

Docs:

- https://docs.glassnode.com/basic-api/api

### Arkham / alternatives

Potential use:

- entity intelligence
- wallet labels
- visual wallet graph exploration
- alerting

Provider terms, API availability and cost must be verified before implementation.

## MVP policy

MVP should include provider adapter interfaces and UI states, but not fake wallet data.

UI states:

- not configured
- source offline
- stale
- live
- no matching flows

## Data model

A wallet intelligence event should include:

- source
- chain
- wallet_address or entity id
- entity_label if available
- asset
- flow direction
- amount
- value_usd if available
- transaction hash if available
- event timestamp
- captured_at
- confidence
- raw payload hash

## Signal policy

Wallet intelligence can create:

1. research note
2. whale alert
3. market watch signal
4. risk warning
5. paper/shadow feature

Wallet intelligence cannot directly create:

- live order
- leverage increase
- model promotion

## Risks

- provider cost
- API limits
- label inaccuracies
- chain reorgs or delayed indexing
- false positives
- wallet spoofing
- exchange wallet misclassification
- hindsight bias

## UI requirements

Wallet Intelligence screen must show:

- provider configuration status
- chain coverage
- whale/smart-money feed
- token flow summaries
- exchange inflow/outflow cards
- confidence and source labels
- last update time
- no-data state when unavailable

## Recommendation

Start with Dune for custom queries and optional Nansen/Glassnode only after API access and cost are confirmed. Keep all wallet signals as research-only until paper/shadow evidence proves predictive value.
