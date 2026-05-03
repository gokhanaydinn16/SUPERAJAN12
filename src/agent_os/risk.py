"""Deterministic risk engine and kill switch cage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from .config import RiskConfig
from .domain import OrderIntent, PositionSnapshot, RiskBreach, RiskDecision, Severity


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class RiskEngine:
    config: RiskConfig
    positions: Dict[str, PositionSnapshot] = field(default_factory=dict)
    recent_intents: Dict[str, datetime] = field(default_factory=dict)
    last_market_update: datetime | None = None
    kill_switch_engaged: bool = False

    def update_market_timestamp(self, timestamp: datetime) -> None:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        self.last_market_update = timestamp

    def toggle_kill_switch(self, engage: bool) -> Dict[str, object]:
        self.kill_switch_engaged = engage
        return {"kill_switch_engaged": self.kill_switch_engaged, "updated_at": utcnow().isoformat()}

    def market_is_stale(self) -> bool:
        if self.last_market_update is None:
            return True
        return utcnow() - self.last_market_update > timedelta(seconds=8)

    def evaluate(self, intent: OrderIntent) -> RiskDecision:
        breaches: List[str] = []
        if self.kill_switch_engaged:
            breaches.append("kill_switch")
        if self.market_is_stale():
            breaches.append("stale_market_data")
        duplicate_seen = self._register_duplicate(intent.intent_id)
        if duplicate_seen:
            breaches.append("duplicate_intent")

        position = self.positions.get(intent.symbol, PositionSnapshot(symbol=intent.symbol))
        projected = position.net_quantity + intent.signed_quantity
        if abs(projected) > self.config.max_position_size:
            breaches.append("max_position_size")
        if intent.notional > self.config.max_order_notional:
            breaches.append("max_order_notional")
        if intent.leverage > self.config.max_leverage:
            breaches.append("max_leverage")

        allowed = not breaches
        reason = "within envelope" if allowed else ", ".join(breaches)
        return RiskDecision(
            allowed=allowed,
            reason=reason,
            projected_position=round(projected, 6),
            observed_notional=round(intent.notional, 4),
            breaches=breaches,
        )

    def record_fill(self, intent: OrderIntent, fill_price: float) -> PositionSnapshot:
        position = self.positions.get(intent.symbol, PositionSnapshot(symbol=intent.symbol))
        new_qty = position.net_quantity + intent.signed_quantity
        if new_qty == 0:
            avg_entry = 0.0
        elif position.net_quantity == 0:
            avg_entry = fill_price
        else:
            gross = (position.avg_entry_price * abs(position.net_quantity)) + (fill_price * abs(intent.signed_quantity))
            avg_entry = gross / (abs(position.net_quantity) + abs(intent.signed_quantity))
        updated = PositionSnapshot(
            symbol=intent.symbol,
            net_quantity=round(new_qty, 6),
            avg_entry_price=round(avg_entry, 4),
            mark_price=fill_price,
            updated_at=utcnow(),
        )
        self.positions[intent.symbol] = updated
        return updated

    def position_view(self) -> List[Dict[str, object]]:
        return [position.to_dict() for position in self.positions.values()]

    def summarize(self) -> Dict[str, object]:
        return {
            "kill_switch_engaged": self.kill_switch_engaged,
            "market_is_stale": self.market_is_stale(),
            "positions": self.position_view(),
        }

    def make_breaches(self, decision: RiskDecision) -> List[RiskBreach]:
        mapping = {
            "kill_switch": ("kill_switch", 1.0, 0.0, Severity.CRITICAL, "Operator lock is engaged."),
            "stale_market_data": ("market_freshness", 1.0, 0.0, Severity.CRITICAL, "Market data is stale."),
            "duplicate_intent": ("duplicate_guard", 1.0, 0.0, Severity.WARNING, "Intent was repeated too quickly."),
            "max_position_size": ("max_position_size", abs(decision.projected_position), self.config.max_position_size, Severity.CRITICAL, "Projected position is too large."),
            "max_order_notional": ("max_order_notional", decision.observed_notional, self.config.max_order_notional, Severity.CRITICAL, "Order notional is too large."),
            "max_leverage": ("max_leverage", self.config.max_leverage + 1, self.config.max_leverage, Severity.CRITICAL, "Leverage exceeds policy."),
        }
        output: List[RiskBreach] = []
        for key in decision.breaches:
            limit_name, current_value, threshold, severity, note = mapping[key]
            output.append(RiskBreach(limit_name, current_value, threshold, severity, note))
        return output

    def _register_duplicate(self, intent_id: str) -> bool:
        now = utcnow()
        window = timedelta(seconds=self.config.duplicate_window_seconds)
        last_seen = self.recent_intents.get(intent_id)
        self.recent_intents = {
            key: seen_at for key, seen_at in self.recent_intents.items() if now - seen_at <= window
        }
        self.recent_intents[intent_id] = now
        return last_seen is not None and now - last_seen <= window
