from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class KalshiPublicClient:
    """Read-only Kalshi public market data client.

    This client does not authenticate and does not place orders. It is intended
    for cross-market event discovery and price sanity checks.
    """

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def list_markets(self, limit: int = 100, status: str = "open") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/markets",
                params={"limit": limit, "status": status},
            )
            response.raise_for_status()
            payload = response.json()
        markets = payload.get("markets") if isinstance(payload, dict) else None
        return markets if isinstance(markets, list) else []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def get_market(self, ticker: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/markets/{ticker}")
            response.raise_for_status()
            payload = response.json()
        market = payload.get("market") if isinstance(payload, dict) else None
        return market if isinstance(market, dict) else {}

    async def find_similar_markets(self, query: str, limit: int = 100) -> list[dict[str, Any]]:
        query_l = query.lower()
        markets = await self.list_markets(limit=limit)
        return [
            market
            for market in markets
            if query_l in str(market.get("title") or market.get("subtitle") or "").lower()
        ]
