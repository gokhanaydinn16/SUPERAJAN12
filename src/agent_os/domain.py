"""Canonical domain models for the autonomous crypto agent system."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DecisionAction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    NEUTRAL = "neutral"
    HALT = "halt"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderState(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(slots=True)
class Event:
    kind: str
    payload: Dict[str, Any]
    source: str
    event_id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "kind": self.kind,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "payload": _jsonify(self.payload),
        }


@dataclass(slots=True)
class MarketSnapshot:
    venue: str
    symbol: str
    sequence: int
    best_bid: float
    best_ask: float
    bid_size: float
    ask_size: float
    checksum: Optional[int] = None
    last_trade_price: Optional[float] = None
    status: str = "healthy"
    captured_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.best_bid < 0 or self.best_ask < 0:
            raise ValueError("top of book prices must be non-negative")
        if self.best_bid > self.best_ask:
            raise ValueError("best_bid cannot exceed best_ask")

    @property
    def mid_price(self) -> float:
        return round((self.best_bid + self.best_ask) / 2.0, 4)

    @property
    def spread(self) -> float:
        return round(self.best_ask - self.best_bid, 4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "venue": self.venue,
            "symbol": self.symbol,
            "sequence": self.sequence,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "checksum": self.checksum,
            "last_trade_price": self.last_trade_price,
            "status": self.status,
            "captured_at": self.captured_at.isoformat(),
            "mid_price": self.mid_price,
            "spread": self.spread,
        }


@dataclass(slots=True)
class ResearchSignal:
    source: str
    description: str
    severity: float
    captured_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be between 0 and 1")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "description": self.description,
            "severity": self.severity,
            "captured_at": self.captured_at.isoformat(),
        }


@dataclass(slots=True)
class DecisionSuggestion:
    symbol: str
    venue: str
    action: DecisionAction
    confidence: float
    rationale: str
    target_size: float
    reference_price: float
    signals: List[ResearchSignal]
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.target_size <= 0:
            raise ValueError("target_size must be positive")
        if self.reference_price <= 0:
            raise ValueError("reference_price must be positive")
        if not self.signals:
            raise ValueError("a suggestion must cite at least one signal")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "venue": self.venue,
            "action": self.action.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "target_size": self.target_size,
            "reference_price": self.reference_price,
            "signals": [signal.to_dict() for signal in self.signals],
            "created_at": self.created_at.isoformat(),
        }


@dataclass(slots=True)
class OrderIntent:
    symbol: str
    venue: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    intent_id: str = field(default_factory=lambda: uuid4().hex)
    price: Optional[float] = None
    reduce_only: bool = False
    leverage: float = 1.0
    source: str = "research"
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.order_type == OrderType.LIMIT and (self.price is None or self.price <= 0):
            raise ValueError("limit orders require a positive price")
        if self.leverage <= 0:
            raise ValueError("leverage must be positive")

    @property
    def notional(self) -> float:
        basis = self.price or 0.0
        return round(self.quantity * basis, 4)

    @property
    def signed_quantity(self) -> float:
        return self.quantity if self.side is OrderSide.BUY else -self.quantity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "side": self.side.value,
            "quantity": self.quantity,
            "order_type": self.order_type.value,
            "price": self.price,
            "reduce_only": self.reduce_only,
            "leverage": self.leverage,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(slots=True)
class OrderRecord:
    order_id: str
    intent_id: str
    symbol: str
    venue: str
    side: OrderSide
    quantity: float
    state: OrderState
    price: Optional[float] = None
    filled_quantity: float = 0.0
    reduce_only: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "intent_id": self.intent_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "side": self.side.value,
            "quantity": self.quantity,
            "state": self.state.value,
            "price": self.price,
            "filled_quantity": self.filled_quantity,
            "reduce_only": self.reduce_only,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(slots=True)
class FillRecord:
    order_id: str
    symbol: str
    venue: str
    quantity: float
    price: float
    reason: str
    captured_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "quantity": self.quantity,
            "price": self.price,
            "reason": self.reason,
            "captured_at": self.captured_at.isoformat(),
        }


@dataclass(slots=True)
class RiskDecision:
    allowed: bool
    reason: str
    projected_position: float
    observed_notional: float
    breaches: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "projected_position": self.projected_position,
            "observed_notional": self.observed_notional,
            "breaches": self.breaches,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(slots=True)
class RiskBreach:
    limit_name: str
    current_value: float
    threshold: float
    severity: Severity
    note: str
    captured_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "limit_name": self.limit_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "note": self.note,
            "captured_at": self.captured_at.isoformat(),
        }


@dataclass(slots=True)
class PositionSnapshot:
    symbol: str
    net_quantity: float = 0.0
    avg_entry_price: float = 0.0
    mark_price: float = 0.0
    updated_at: datetime = field(default_factory=utcnow)

    @property
    def unrealized_pnl(self) -> float:
        if not self.avg_entry_price or not self.net_quantity:
            return 0.0
        return round((self.mark_price - self.avg_entry_price) * self.net_quantity, 4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "net_quantity": self.net_quantity,
            "avg_entry_price": self.avg_entry_price,
            "mark_price": self.mark_price,
            "unrealized_pnl": self.unrealized_pnl,
            "updated_at": self.updated_at.isoformat(),
        }


def _jsonify(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, list):
        return [_jsonify(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonify(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonify(item) for key, item in asdict(value).items()}
    return value
