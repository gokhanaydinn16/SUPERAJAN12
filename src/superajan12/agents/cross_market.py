from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from superajan12.models import CrossMarketMatch, Market


class CrossMarketAgent:
    def find_matches(
        self,
        polymarket_market: Market,
        external_markets: list[dict[str, Any]],
        source: str = "kalshi",
        min_similarity: float = 0.45,
        limit: int = 5,
    ) -> list[CrossMarketMatch]:
        base_text = self._normalize(polymarket_market.question)
        matches: list[CrossMarketMatch] = []

        for external in external_markets:
            title = str(external.get("title") or external.get("subtitle") or external.get("name") or "")
            if not title:
                continue
            similarity = SequenceMatcher(None, base_text, self._normalize(title)).ratio()
            if similarity < min_similarity:
                continue
            matches.append(
                CrossMarketMatch(
                    source=source,
                    external_id=str(external.get("ticker") or external.get("id") or title),
                    external_title=title,
                    similarity=similarity,
                    yes_price=_price_from_cents(external.get("yes_bid") or external.get("yes_ask")),
                    no_price=_price_from_cents(external.get("no_bid") or external.get("no_ask")),
                    reasons=[f"title similarity={similarity:.3f}"],
                )
            )

        return sorted(matches, key=lambda item: item.similarity, reverse=True)[:limit]

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9 ]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text


def _price_from_cents(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed > 1:
        return parsed / 100
    return parsed
