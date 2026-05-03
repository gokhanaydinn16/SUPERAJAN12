from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from superajan12.market_state import MarketStateValidation, MarketStateValidator
from superajan12.models import Market, OrderBookLevel, OrderBookSnapshot


class ReplayEventType(str, Enum):
    SNAPSHOT = "snapshot"
    DIFF = "diff"
    RESNAPSHOT = "resnapshot"


@dataclass(frozen=True)
class OrderBookDelta:
    side: str
    price: float
    size: float


@dataclass(frozen=True)
class ReplayEvent:
    event_type: ReplayEventType
    market_id: str
    venue: str
    symbol: str
    sequence_start: int
    sequence_end: int
    bids: tuple[OrderBookDelta, ...] = ()
    asks: tuple[OrderBookDelta, ...] = ()
    checksum: str | None = None
    checksum_valid: bool | None = True
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ReplayStep:
    event: ReplayEvent
    snapshot: OrderBookSnapshot | None
    validation: MarketStateValidation
    action: str


@dataclass(frozen=True)
class ReplayReport:
    market_id: str
    venue: str
    total_events: int
    accepted_events: int
    rejected_events: int
    resnapshot_events: int
    final_snapshot: OrderBookSnapshot | None
    steps: tuple[ReplayStep, ...]

    @property
    def ok(self) -> bool:
        return self.rejected_events == 0 and self.final_snapshot is not None


class DeterministicOrderBook:
    def __init__(self, *, market_id: str, venue: str, symbol: str) -> None:
        self.market_id = market_id
        self.venue = venue
        self.symbol = symbol
        self.bids: dict[float, float] = {}
        self.asks: dict[float, float] = {}
        self.sequence_end: int | None = None
        self.snapshot_id: str | None = None

    def apply(self, event: ReplayEvent) -> OrderBookSnapshot:
        if event.market_id != self.market_id:
            raise ValueError("event market id does not match book")
        if event.venue != self.venue:
            raise ValueError("event venue does not match book")
        if event.symbol != self.symbol:
            raise ValueError("event symbol does not match book")

        previous = self.sequence_end
        if event.event_type in {ReplayEventType.SNAPSHOT, ReplayEventType.RESNAPSHOT}:
            self.bids = self._levels_to_map(event.bids)
            self.asks = self._levels_to_map(event.asks)
        elif event.event_type == ReplayEventType.DIFF:
            self._apply_deltas(self.bids, event.bids)
            self._apply_deltas(self.asks, event.asks)
        else:
            raise ValueError(f"unsupported replay event type: {event.event_type}")

        self.sequence_end = event.sequence_end
        self.snapshot_id = f"{event.venue}:{event.symbol}:{event.sequence_end}"
        return self.to_snapshot(event=event, previous_sequence_end=previous)

    def to_snapshot(self, *, event: ReplayEvent, previous_sequence_end: int | None) -> OrderBookSnapshot:
        bids = [
            OrderBookLevel(price=price, size=size)
            for price, size in sorted(self.bids.items(), key=lambda item: item[0], reverse=True)
        ]
        asks = [
            OrderBookLevel(price=price, size=size)
            for price, size in sorted(self.asks.items(), key=lambda item: item[0])
        ]
        return OrderBookSnapshot(
            market_id=self.market_id,
            yes_bids=bids,
            yes_asks=asks,
            source="deterministic_replay",
            venue=self.venue,
            token_id=self.symbol,
            snapshot_kind=event.event_type.value,
            snapshot_id=self.snapshot_id,
            sequence_start=event.sequence_start,
            sequence_end=event.sequence_end,
            previous_sequence_end=previous_sequence_end,
            checksum=event.checksum,
            checksum_valid=event.checksum_valid,
            depth_levels=min(len(bids), len(asks)),
            captured_at=event.captured_at,
            received_at=event.received_at,
        )

    def _levels_to_map(self, deltas: tuple[OrderBookDelta, ...]) -> dict[float, float]:
        levels: dict[float, float] = {}
        for delta in deltas:
            if delta.size > 0:
                levels[round(delta.price, 8)] = delta.size
        return levels

    def _apply_deltas(self, levels: dict[float, float], deltas: tuple[OrderBookDelta, ...]) -> None:
        for delta in deltas:
            price = round(delta.price, 8)
            if delta.size <= 0:
                levels.pop(price, None)
            else:
                levels[price] = delta.size


class DeterministicReplayRunner:
    def __init__(self, *, validator: MarketStateValidator | None = None) -> None:
        self.validator = validator or MarketStateValidator()

    def run(self, *, market: Market, events: list[ReplayEvent]) -> ReplayReport:
        if not events:
            invalid = self.validator.validate(market, None)
            return ReplayReport(
                market_id=market.id,
                venue="unknown",
                total_events=0,
                accepted_events=0,
                rejected_events=1,
                resnapshot_events=0,
                final_snapshot=None,
                steps=(ReplayStep(event=self._empty_event(market.id), snapshot=None, validation=invalid, action="reject"),),
            )

        first = events[0]
        book = DeterministicOrderBook(market_id=first.market_id, venue=first.venue, symbol=first.symbol)
        steps: list[ReplayStep] = []
        accepted = 0
        rejected = 0
        resnapshots = 0
        final_snapshot: OrderBookSnapshot | None = None

        for event in events:
            if event.event_type == ReplayEventType.DIFF and book.sequence_end is not None:
                expected_next = book.sequence_end + 1
                if event.sequence_start > expected_next:
                    snapshot = book.to_snapshot(event=event, previous_sequence_end=book.sequence_end)
                    validation = self.validator.validate(market, snapshot)
                    steps.append(ReplayStep(event=event, snapshot=snapshot, validation=validation, action="reject_gap"))
                    rejected += 1
                    continue

            snapshot = book.apply(event)
            validation = self.validator.validate(market, snapshot)
            action = "accept" if validation.ok else "reject"
            if event.event_type == ReplayEventType.RESNAPSHOT:
                resnapshots += 1
                action = "resnapshot" if validation.ok else "reject_resnapshot"

            steps.append(ReplayStep(event=event, snapshot=snapshot, validation=validation, action=action))
            if validation.ok:
                accepted += 1
                final_snapshot = snapshot
            else:
                rejected += 1

        return ReplayReport(
            market_id=market.id,
            venue=first.venue,
            total_events=len(events),
            accepted_events=accepted,
            rejected_events=rejected,
            resnapshot_events=resnapshots,
            final_snapshot=final_snapshot,
            steps=tuple(steps),
        )

    def _empty_event(self, market_id: str) -> ReplayEvent:
        return ReplayEvent(
            event_type=ReplayEventType.SNAPSHOT,
            market_id=market_id,
            venue="unknown",
            symbol="unknown",
            sequence_start=0,
            sequence_end=0,
        )


def fixture_healthy_binance_replay(*, market_id: str = "m-binance", symbol: str = "BTCUSDT") -> list[ReplayEvent]:
    now = datetime.now(timezone.utc)
    return [
        ReplayEvent(
            event_type=ReplayEventType.SNAPSHOT,
            market_id=market_id,
            venue="binance",
            symbol=symbol,
            sequence_start=100,
            sequence_end=100,
            bids=(OrderBookDelta("bid", 0.49, 500), OrderBookDelta("bid", 0.48, 400)),
            asks=(OrderBookDelta("ask", 0.51, 500), OrderBookDelta("ask", 0.52, 400)),
            checksum="binance-100",
            checksum_valid=True,
            captured_at=now,
            received_at=now,
        ),
        ReplayEvent(
            event_type=ReplayEventType.DIFF,
            market_id=market_id,
            venue="binance",
            symbol=symbol,
            sequence_start=101,
            sequence_end=101,
            bids=(OrderBookDelta("bid", 0.50, 250),),
            asks=(OrderBookDelta("ask", 0.51, 0), OrderBookDelta("ask", 0.515, 300)),
            checksum="binance-101",
            checksum_valid=True,
            captured_at=now,
            received_at=now,
        ),
        ReplayEvent(
            event_type=ReplayEventType.DIFF,
            market_id=market_id,
            venue="binance",
            symbol=symbol,
            sequence_start=102,
            sequence_end=102,
            bids=(OrderBookDelta("bid", 0.475, 350),),
            asks=(OrderBookDelta("ask", 0.525, 350),),
            checksum="binance-102",
            checksum_valid=True,
            captured_at=now,
            received_at=now,
        ),
    ]


def fixture_gap_then_resnapshot(*, market_id: str = "m-gap", symbol: str = "BTCUSDT") -> list[ReplayEvent]:
    now = datetime.now(timezone.utc)
    return [
        ReplayEvent(
            event_type=ReplayEventType.SNAPSHOT,
            market_id=market_id,
            venue="binance",
            symbol=symbol,
            sequence_start=10,
            sequence_end=10,
            bids=(OrderBookDelta("bid", 0.49, 500),),
            asks=(OrderBookDelta("ask", 0.51, 500),),
            checksum="gap-10",
            checksum_valid=True,
            captured_at=now,
            received_at=now,
        ),
        ReplayEvent(
            event_type=ReplayEventType.DIFF,
            market_id=market_id,
            venue="binance",
            symbol=symbol,
            sequence_start=13,
            sequence_end=13,
            bids=(OrderBookDelta("bid", 0.50, 250),),
            asks=(OrderBookDelta("ask", 0.52, 250),),
            checksum="gap-13",
            checksum_valid=True,
            captured_at=now,
            received_at=now,
        ),
        ReplayEvent(
            event_type=ReplayEventType.RESNAPSHOT,
            market_id=market_id,
            venue="binance",
            symbol=symbol,
            sequence_start=14,
            sequence_end=14,
            bids=(OrderBookDelta("bid", 0.48, 600),),
            asks=(OrderBookDelta("ask", 0.52, 600),),
            checksum="gap-14",
            checksum_valid=True,
            captured_at=now,
            received_at=now,
        ),
    ]
