from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from superajan12.models import OrderBookLevel, OrderBookSnapshot


class VenueName(str, Enum):
    DERIBIT = "deribit"
    BINANCE = "binance"
    COINBASE = "coinbase"
    OKX = "okx"


class VenueCapability(str, Enum):
    PUBLIC_ORDERBOOK = "public_orderbook"
    PUBLIC_TRADES = "public_trades"
    PUBLIC_CANDLES = "public_candles"
    WEBSOCKET_ORDERBOOK = "websocket_orderbook"
    ORDER_PREVIEW = "order_preview"
    TESTNET = "testnet"
    ACCOUNT_REQUIRED = "account_required"
    POLICY_GATE_REQUIRED = "policy_gate_required"


@dataclass(frozen=True)
class VenueProfile:
    name: VenueName
    display_name: str
    capabilities: tuple[VenueCapability, ...]
    live_orders_enabled: bool = False
    default_testnet: bool = True
    notes: tuple[str, ...] = ()

    def supports(self, capability: VenueCapability) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class VenueOrderRequest:
    venue: VenueName
    symbol: str
    side: str
    price: float
    size: float
    client_order_id: str
    dry_run: bool = True


@dataclass(frozen=True)
class VenueOrderPreview:
    venue: VenueName
    accepted: bool
    dry_run: bool
    reasons: tuple[str, ...]
    normalized_symbol: str
    estimated_notional_usdc: float


@dataclass(frozen=True)
class VenueHealth:
    venue: VenueName
    ok: bool
    status: str
    reasons: tuple[str, ...] = ()


class VenueAdapter(Protocol):
    profile: VenueProfile

    def health(self) -> VenueHealth:
        ...

    def get_order_book(self, *, market_id: str, symbol: str, depth: int = 10) -> OrderBookSnapshot:
        ...

    def preview_order(self, request: VenueOrderRequest) -> VenueOrderPreview:
        ...


class DryRunVenueAdapter:
    """Deterministic adapter harness used for contracts and tests.

    This adapter never sends live orders. It gives the rest of the system a stable
    contract for venue capabilities, orderbook snapshots and preview-only orders
    before any real venue client is wired in.
    """

    def __init__(
        self,
        profile: VenueProfile,
        *,
        bid: float = 0.49,
        ask: float = 0.51,
        bid_size: float = 500.0,
        ask_size: float = 500.0,
        sequence: int = 1,
    ) -> None:
        self.profile = profile
        self.bid = bid
        self.ask = ask
        self.bid_size = bid_size
        self.ask_size = ask_size
        self.sequence = sequence

    def health(self) -> VenueHealth:
        reasons: list[str] = ["dry-run harness"]
        if not self.profile.live_orders_enabled:
            reasons.append("live orders disabled")
        return VenueHealth(
            venue=self.profile.name,
            ok=True,
            status="ready",
            reasons=tuple(reasons),
        )

    def get_order_book(self, *, market_id: str, symbol: str, depth: int = 10) -> OrderBookSnapshot:
        if depth <= 0:
            raise ValueError("depth must be positive")
        bid_levels = [
            OrderBookLevel(price=round(max(self.bid - i * 0.01, 0.01), 4), size=self.bid_size)
            for i in range(depth)
        ]
        ask_levels = [
            OrderBookLevel(price=round(min(self.ask + i * 0.01, 0.99), 4), size=self.ask_size)
            for i in range(depth)
        ]
        return OrderBookSnapshot(
            market_id=market_id,
            yes_bids=bid_levels,
            yes_asks=ask_levels,
            source="venue_harness",
            venue=self.profile.name.value,
            token_id=symbol,
            snapshot_kind="snapshot",
            snapshot_id=f"{self.profile.name.value}:{symbol}:{self.sequence}",
            sequence_start=self.sequence,
            sequence_end=self.sequence,
            checksum=f"dryrun-{self.profile.name.value}-{self.sequence}",
            checksum_valid=True,
            depth_levels=depth,
        )

    def preview_order(self, request: VenueOrderRequest) -> VenueOrderPreview:
        reasons: list[str] = []
        if request.venue != self.profile.name:
            reasons.append("request venue does not match adapter")
        if not request.dry_run:
            reasons.append("live order submission is disabled")
        if not self.profile.supports(VenueCapability.ORDER_PREVIEW):
            reasons.append("venue does not support local order preview")
        if request.price <= 0 or request.price >= 1:
            reasons.append("price must be inside prediction-market bounds")
        if request.size <= 0:
            reasons.append("size must be positive")
        if request.side.upper() not in {"YES", "NO", "BUY", "SELL"}:
            reasons.append("unsupported side")

        return VenueOrderPreview(
            venue=self.profile.name,
            accepted=not reasons,
            dry_run=True,
            reasons=tuple(reasons) if reasons else ("preview accepted",),
            normalized_symbol=request.symbol.upper(),
            estimated_notional_usdc=round(max(request.price, 0.0) * max(request.size, 0.0), 6),
        )


@dataclass
class VenueAdapterRegistry:
    adapters: dict[VenueName, VenueAdapter] = field(default_factory=dict)

    def register(self, adapter: VenueAdapter) -> None:
        self.adapters[adapter.profile.name] = adapter

    def get(self, venue: VenueName) -> VenueAdapter:
        if venue not in self.adapters:
            raise KeyError(f"venue adapter not registered: {venue.value}")
        return self.adapters[venue]

    def profiles(self) -> tuple[VenueProfile, ...]:
        return tuple(adapter.profile for adapter in self.adapters.values())

    def readiness_summary(self) -> dict[str, dict[str, object]]:
        summary: dict[str, dict[str, object]] = {}
        for venue, adapter in self.adapters.items():
            health = adapter.health()
            summary[venue.value] = {
                "display_name": adapter.profile.display_name,
                "ok": health.ok,
                "status": health.status,
                "capabilities": [capability.value for capability in adapter.profile.capabilities],
                "live_orders_enabled": adapter.profile.live_orders_enabled,
                "default_testnet": adapter.profile.default_testnet,
                "reasons": list(health.reasons),
            }
        return summary


def default_venue_profiles() -> tuple[VenueProfile, ...]:
    return (
        VenueProfile(
            name=VenueName.DERIBIT,
            display_name="Deribit",
            capabilities=(
                VenueCapability.PUBLIC_ORDERBOOK,
                VenueCapability.PUBLIC_TRADES,
                VenueCapability.PUBLIC_CANDLES,
                VenueCapability.WEBSOCKET_ORDERBOOK,
                VenueCapability.TESTNET,
            ),
            notes=("testnet can be unavailable during maintenance",),
        ),
        VenueProfile(
            name=VenueName.BINANCE,
            display_name="Binance",
            capabilities=(
                VenueCapability.PUBLIC_ORDERBOOK,
                VenueCapability.PUBLIC_TRADES,
                VenueCapability.PUBLIC_CANDLES,
                VenueCapability.WEBSOCKET_ORDERBOOK,
                VenueCapability.TESTNET,
            ),
            notes=("diff-depth requires sequence and resnapshot recovery",),
        ),
        VenueProfile(
            name=VenueName.COINBASE,
            display_name="Coinbase Advanced Trade",
            capabilities=(
                VenueCapability.PUBLIC_ORDERBOOK,
                VenueCapability.PUBLIC_TRADES,
                VenueCapability.PUBLIC_CANDLES,
                VenueCapability.ORDER_PREVIEW,
                VenueCapability.ACCOUNT_REQUIRED,
            ),
            notes=("preview-only order flow must remain dry-run until live checklist passes",),
        ),
        VenueProfile(
            name=VenueName.OKX,
            display_name="OKX",
            capabilities=(
                VenueCapability.PUBLIC_ORDERBOOK,
                VenueCapability.PUBLIC_TRADES,
                VenueCapability.PUBLIC_CANDLES,
                VenueCapability.WEBSOCKET_ORDERBOOK,
                VenueCapability.POLICY_GATE_REQUIRED,
                VenueCapability.ACCOUNT_REQUIRED,
            ),
            notes=("policy and account readiness gates must be checked before live work",),
        ),
    )


def build_dry_run_venue_registry() -> VenueAdapterRegistry:
    registry = VenueAdapterRegistry()
    for profile in default_venue_profiles():
        registry.register(DryRunVenueAdapter(profile))
    return registry
