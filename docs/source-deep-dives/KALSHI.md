# Source Deep Dive: Kalshi

## Role in SuperAjan12

Kalshi is a regulated event-market intelligence source and cross-market comparison venue. It should be used to compare event pricing, market wording and resolution structure against Polymarket and broader futures/spot market data.

## Official surfaces

Docs:

- https://docs.kalshi.com/welcome
- https://docs.kalshi.com/getting_started
- https://docs.kalshi.com/api-reference/market/get-markets
- https://docs.kalshi.com/websockets/websocket-connection

Kalshi exposes market data, event data, orderbooks, WebSocket streams and trading surfaces. Trading requires authentication and account eligibility.

## MVP usage

Read-only market intelligence:

- event discovery
- market title/subtitle/rules
- ticker
- status
- YES/NO bid/ask where public
- orderbook snapshots where available
- cross-market event comparison

## Not MVP

- live trading
- authenticated order placement
- account data

## Reliability requirements

Kalshi connector must store:

- source name
- endpoint
- ticker
- event ticker
- captured_at
- stale flag
- pagination cursor state
- raw payload hash

## Known risks

- API pagination and cursor handling.
- Difference between market title, subtitle and rules.
- Contract wording may not match Polymarket wording.
- Trading/account access and eligibility requirements.
- Event status transitions.

## UI requirements

Kalshi panel must show:

- event name
- market title
- ticker
- YES/NO prices where available
- status
- matched Polymarket market
- similarity score
- wording differences
- resolution differences

## Decision policy

Kalshi is used for research and cross-market verification. A Kalshi/Polymarket mismatch should not automatically create a trade. It should create a research card requiring source/wording review.
