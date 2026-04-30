from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class BinanceFuturesClient:
    """Read-only Binance USD-M futures public market data client."""

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def mark_price(self, symbol: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/fapi/v1/premiumIndex", params={"symbol": symbol})
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        return payload

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def open_interest(self, symbol: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/fapi/v1/openInterest", params={"symbol": symbol})
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def funding_rate(self, symbol: str, limit: int = 1) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": limit},
            )
            response.raise_for_status()
            payload = response.json()
        return payload if isinstance(payload, list) else []

    async def reference_snapshot(self, symbol: str) -> dict[str, Any]:
        mark = await self.mark_price(symbol)
        open_interest = await self.open_interest(symbol)
        funding = await self.funding_rate(symbol, limit=1)
        return {
            "source": "binance_usds_futures",
            "symbol": symbol,
            "mark_price": _float_or_none(mark.get("markPrice")),
            "index_price": _float_or_none(mark.get("indexPrice")),
            "last_funding_rate": _float_or_none(mark.get("lastFundingRate")),
            "next_funding_time": mark.get("nextFundingTime"),
            "open_interest": _float_or_none(open_interest.get("openInterest")),
            "funding_history": funding,
        }


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
