from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class OKXPublicClient:
    """Read-only OKX public market data client."""

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def ticker(self, inst_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v5/market/ticker", params={"instId": inst_id})
            response.raise_for_status()
            payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        if isinstance(data, list) and data:
            return data[0]
        return {}

    async def reference_snapshot(self, inst_id: str) -> dict[str, Any]:
        ticker = await self.ticker(inst_id)
        return {
            "source": "okx",
            "symbol": inst_id,
            "last_price": _float_or_none(ticker.get("last")),
            "bid_price": _float_or_none(ticker.get("bidPx")),
            "ask_price": _float_or_none(ticker.get("askPx")),
            "volume_24h": _float_or_none(ticker.get("vol24h")),
            "timestamp": ticker.get("ts"),
        }


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
