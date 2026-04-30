# Source Deep Dive: Polymarket

## Role in SuperAjan12

Polymarket is an event and prediction-market intelligence source. It should not be the first live execution venue. Its primary role is to expose event probabilities, market metadata, resolution rules, orderbook state and crowd pricing.

## Official surfaces

- Gamma API: market and event discovery.
- Data API: user activity, positions, trades, holders, open interest and analytics.
- CLOB API: orderbook, prices, midpoint, spread, price history and trading operations.

Docs:

- https://docs.polymarket.com/api-reference
- https://docs.polymarket.com/trading/orderbook
- https://docs.polymarket.com/developers/CLOB/websocket/market-channel
- https://docs.polymarket.com/api-reference/authentication

## MVP usage

Use only read/public data:

- markets
- events
- tags/categories
- orderbook snapshot
- midpoint
- spread
- price history
- volume/liquidity
- resolution metadata where available

## Not MVP

- live order submission
- deposits/withdrawals
- authenticated trading
- automated market making

## Reliability requirements

Polymarket data must be normalized into internal models with:

- source name
- endpoint name
- market id
- token id
- captured_at timestamp
- stale flag
- error state
- raw payload hash

## Known risks

- Resolution ambiguity.
- Event interpretation mistakes.
- Wide spreads and low liquidity.
- Token id mapping complexity.
- Possible rate limits and pagination constraints.
- Trading endpoints require authentication and signing.

## UI requirements

Polymarket panel must show:

- market question
- category/event
- YES/NO prices
- spread
- liquidity
- volume
- resolution confidence
- cross-market match status
- decision: research/watch/blocked/paper-ready

## Decision policy

Polymarket signal cannot directly create live action. It can create:

1. research task
2. event intelligence card
3. paper/shadow candidate
4. cross-market comparison input

Risk Engine must block if resolution is unclear, liquidity is weak or source health is stale.
