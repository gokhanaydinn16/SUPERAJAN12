from __future__ import annotations

from pydantic import BaseModel, Field

from superajan12.connectors.polymarket import PolymarketClient


class EndpointCheck(BaseModel):
    name: str
    ok: bool
    detail: str


class EndpointCheckResult(BaseModel):
    checks: list[EndpointCheck] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)


async def verify_polymarket_public_endpoints(client: PolymarketClient) -> EndpointCheckResult:
    """Run a minimal live compatibility check against public Polymarket endpoints.

    This does not trade and does not require secrets. It verifies that the fields
    needed by the scanner are available for at least one active market.
    """

    checks: list[EndpointCheck] = []

    try:
        markets = await client.list_markets(limit=5)
    except Exception as exc:  # noqa: BLE001
        return EndpointCheckResult(
            checks=[
                EndpointCheck(
                    name="gamma.markets",
                    ok=False,
                    detail=f"failed to fetch markets: {exc.__class__.__name__}",
                )
            ]
        )

    checks.append(
        EndpointCheck(
            name="gamma.markets",
            ok=bool(markets),
            detail=f"fetched {len(markets)} active markets",
        )
    )

    market_with_token = None
    token_id = None
    for market in markets:
        token_id = client.extract_yes_token_id(market)
        if token_id:
            market_with_token = market
            break

    checks.append(
        EndpointCheck(
            name="gamma.token_id",
            ok=bool(token_id),
            detail="found YES token id" if token_id else "no token id found in first markets",
        )
    )

    if not token_id or market_with_token is None:
        return EndpointCheckResult(checks=checks)

    try:
        book = await client.get_order_book(token_id=token_id, market_id=market_with_token.id)
        checks.append(
            EndpointCheck(
                name="clob.book",
                ok=book.best_bid is not None or book.best_ask is not None,
                detail=f"source={book.source}, best_bid={book.best_bid}, best_ask={book.best_ask}",
            )
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(
            EndpointCheck(
                name="clob.book",
                ok=False,
                detail=f"failed: {exc.__class__.__name__}",
            )
        )

    try:
        midpoint = await client.get_midpoint(token_id=token_id)
        checks.append(
            EndpointCheck(
                name="clob.midpoint",
                ok=midpoint is not None,
                detail=f"midpoint={midpoint}",
            )
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(
            EndpointCheck(
                name="clob.midpoint",
                ok=False,
                detail=f"failed: {exc.__class__.__name__}",
            )
        )

    try:
        spread = await client.get_spread(token_id=token_id)
        checks.append(
            EndpointCheck(
                name="clob.spread",
                ok=spread is not None,
                detail=f"spread={spread}",
            )
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(
            EndpointCheck(
                name="clob.spread",
                ok=False,
                detail=f"failed: {exc.__class__.__name__}",
            )
        )

    return EndpointCheckResult(checks=checks)
