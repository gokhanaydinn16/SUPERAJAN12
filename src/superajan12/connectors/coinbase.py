from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class CoinbasePublicClient:
    """Read-only Coinbase Advanced Trade public market data client."""

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def best_bid_ask(self, product_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/best_bid_ask",
                params={"product_ids": product_id},
            )
            response.raise_for_status()
            payload = response.json()
        books = payload.get("pricebooks") if isinstance(payload, dict) else None
        if isinstance(books, list) and books:
            return books[0]
        return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def product(self, product_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/products/{product_id}")
            response.raise_for_status()
            return response.json()

    async def reference_snapshot(self, product_id: str) -> dict[str, Any]:
        book = await self.best_bid_ask(product_id)
        product = await self.product(product_id)
        bids = book.get("bids") or []
        asks = book.get("asks") or []
        bid_price = _first_price(bids)
        ask_price = _first_price(asks)
        price = _float_or_none(product.get("price"))
        return {
            "source": "coinbase",
            "symbol": product_id,
            "last_price": price,
            "bid_price": bid_price,
            "ask_price": ask_price,
            "volume_24h": _float_or_none(product.get("volume_24h")),
        }


def _first_price(levels: Any) -> float | None:
    if isinstance(levels, list) and levels:
        first = levels[0]
        if isinstance(first, dict):
            return _float_or_none(first.get("price"))
    return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
