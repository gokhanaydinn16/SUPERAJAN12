"""Venue-aware market validator with sequence, heartbeat, and stale-data checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from .domain import MarketSnapshot


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class PriceLevel:
    price: float
    size: float


@dataclass(slots=True)
class VenueState:
    venue: str
    symbol: str
    last_sequence: int = 0
    last_checksum: int | None = None
    last_update: datetime = field(default_factory=utcnow)
    gaps: List[Dict[str, int]] = field(default_factory=list)

    def age_seconds(self) -> float:
        return round((utcnow() - self.last_update).total_seconds(), 3)


@dataclass(slots=True)
class MarketDataValidator:
    venue: str
    symbol: str
    stale_after_seconds: int = 8
    state: VenueState = field(init=False)
    last_snapshot: MarketSnapshot | None = None

    def __post_init__(self) -> None:
        self.state = VenueState(venue=self.venue, symbol=self.symbol)

    def ingest(self, sequence: int, bids: List[PriceLevel], asks: List[PriceLevel]) -> MarketSnapshot:
        expected = self.state.last_sequence + 1
        if self.state.last_sequence and sequence != expected:
            self.state.gaps.append({"expected": expected, "received": sequence})
        checksum = self._checksum(bids, asks)
        self.state.last_sequence = sequence
        self.state.last_checksum = checksum
        self.state.last_update = utcnow()
        snapshot = MarketSnapshot(
            venue=self.venue,
            symbol=self.symbol,
            sequence=sequence,
            best_bid=bids[0].price,
            best_ask=asks[0].price,
            bid_size=bids[0].size,
            ask_size=asks[0].size,
            checksum=checksum,
            last_trade_price=(bids[0].price + asks[0].price) / 2.0,
            status=self.status(),
        )
        self.last_snapshot = snapshot
        return snapshot

    def status(self) -> str:
        if utcnow() - self.state.last_update > timedelta(seconds=self.stale_after_seconds):
            return "stale"
        if self.state.gaps:
            return "degraded"
        return "healthy"

    def heartbeat(self) -> Dict[str, object]:
        return {
            "venue": self.venue,
            "symbol": self.symbol,
            "status": self.status(),
            "age_seconds": self.state.age_seconds(),
            "last_sequence": self.state.last_sequence,
            "gap_count": len(self.state.gaps),
            "last_checksum": self.state.last_checksum,
        }

    @staticmethod
    def _checksum(bids: List[PriceLevel], asks: List[PriceLevel]) -> int:
        total = 0
        for level in bids[:3] + asks[:3]:
            total += int(level.price * 100) ^ int(level.size * 1000)
        return total & 0xFFFF
