"""Paper execution engine and cancel-on-disconnect behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from .domain import FillRecord, MarketSnapshot, OrderIntent, OrderRecord, OrderSide, OrderState


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class ExecutionEngine:
    venue: str
    connected: bool = True
    last_market: Optional[MarketSnapshot] = None
    open_orders: Dict[str, OrderRecord] = field(default_factory=dict)
    fills: List[FillRecord] = field(default_factory=list)

    def update_market(self, market: MarketSnapshot) -> None:
        self.last_market = market

    def submit(self, intent: OrderIntent) -> OrderRecord:
        if not self.connected:
            raise RuntimeError("venue disconnected")
        order = OrderRecord(
            order_id=f"{self.venue}-{uuid4().hex[:10]}",
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            venue=intent.venue,
            side=intent.side,
            quantity=intent.quantity,
            state=OrderState.OPEN,
            price=intent.price,
            reduce_only=intent.reduce_only,
        )
        self.open_orders[order.order_id] = order
        return order

    def try_fill(self, order_id: str) -> FillRecord | None:
        order = self.open_orders.get(order_id)
        if order is None or self.last_market is None:
            return None
        fill_price = self.last_market.best_ask if order.side is OrderSide.BUY else self.last_market.best_bid
        order.state = OrderState.FILLED
        order.filled_quantity = order.quantity
        order.updated_at = utcnow()
        fill = FillRecord(
            order_id=order.order_id,
            symbol=order.symbol,
            venue=order.venue,
            quantity=order.quantity,
            price=fill_price,
            reason="paper_best_level_fill",
        )
        self.fills.append(fill)
        return fill

    def cancel_on_disconnect(self) -> List[OrderRecord]:
        cancelled: List[OrderRecord] = []
        for order in self.open_orders.values():
            if order.state is OrderState.OPEN:
                order.state = OrderState.CANCELLED
                order.updated_at = utcnow()
                cancelled.append(order)
        return cancelled

    def disconnect(self) -> List[OrderRecord]:
        self.connected = False
        return self.cancel_on_disconnect()

    def reconnect(self) -> None:
        self.connected = True

    def open_order_view(self) -> List[Dict[str, object]]:
        return [order.to_dict() for order in self.open_orders.values() if order.state is OrderState.OPEN]
