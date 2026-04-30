from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from superajan12.models import Market, OrderBookLevel, OrderBookSnapshot


class PolymarketClient:
    """Public-data Polymarket client.

    This client only reads market data. It does not sign orders and does not send
    live trades. That is intentional for the first implementation phase.
    """

    def __init__(self, gamma_base_url: str, clob_base_url: str, timeout: float = 15.0) -> None:
        self.gamma_base_url = gamma_base_url.rstrip("/")
        self.clob_base_url = clob_base_url.rstrip("/")
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def list_markets(self, limit: int = 50, offset: int = 0) -> list[Market]:
        params = {
            "limit": limit,
            "offset": offset,
            "active": "true",
            "closed": "false",
            "order": "volume",
            "ascending": "false",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.gamma_base_url}/markets", params=params)
            response.raise_for_status()
            payload = response.json()

        if isinstance(payload, dict):
            items = payload.get("markets") or payload.get("data") or []
        else:
            items = payload

        return [self._parse_market(item) for item in items if isinstance(item, dict)]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def get_order_book(self, token_id: str, market_id: str) -> OrderBookSnapshot:
        """Fetch an order book snapshot for a CLOB token id.

        Polymarket market ids and CLOB token ids are not the same thing. The
        scanner tries to extract token ids from market metadata before calling
        this method.
        """

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.clob_base_url}/book", params={"token_id": token_id})
            response.raise_for_status()
            payload = response.json()

        bids = self._parse_levels(payload.get("bids", []), reverse=True)
        asks = self._parse_levels(payload.get("asks", []), reverse=False)
        return OrderBookSnapshot(market_id=market_id, yes_bids=bids, yes_asks=asks)

    def extract_yes_token_id(self, market: Market) -> str | None:
        raw = market.raw
        candidates: list[Any] = []
        for key in ("clobTokenIds", "clobTokenIDs", "tokenIds", "outcomeTokenIds"):
            value = raw.get(key)
            if value:
                candidates.append(value)

        for value in candidates:
            if isinstance(value, str):
                stripped = value.strip().strip("[]")
                parts = [part.strip().strip('"') for part in stripped.split(",") if part.strip()]
                if parts:
                    return parts[0]
            if isinstance(value, list) and value:
                return str(value[0])
        return None

    def _parse_market(self, item: dict[str, Any]) -> Market:
        end_date = None
        raw_end_date = item.get("endDate") or item.get("end_date")
        if isinstance(raw_end_date, str):
            try:
                end_date = datetime.fromisoformat(raw_end_date.replace("Z", "+00:00"))
            except ValueError:
                end_date = None

        return Market(
            id=str(item.get("id") or item.get("conditionId") or item.get("slug") or "unknown"),
            question=str(item.get("question") or item.get("title") or "Untitled market"),
            slug=item.get("slug"),
            category=item.get("category"),
            active=bool(item.get("active", True)),
            closed=bool(item.get("closed", False)),
            volume_usdc=float(item.get("volume") or item.get("volumeNum") or 0.0),
            liquidity_usdc=float(item.get("liquidity") or item.get("liquidityNum") or 0.0),
            end_date=end_date,
            resolution_source=item.get("resolutionSource") or item.get("resolution_source"),
            raw=item,
        )

    def _parse_levels(self, levels: list[Any], reverse: bool) -> list[OrderBookLevel]:
        parsed: list[OrderBookLevel] = []
        for level in levels:
            if isinstance(level, dict):
                price = level.get("price")
                size = level.get("size")
            elif isinstance(level, list | tuple) and len(level) >= 2:
                price, size = level[0], level[1]
            else:
                continue
            try:
                parsed.append(OrderBookLevel(price=float(price), size=float(size)))
            except (TypeError, ValueError):
                continue
        return sorted(parsed, key=lambda row: row.price, reverse=reverse)
