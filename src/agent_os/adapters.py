"""Venue adapter backbone with capability descriptions and mock responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict

from .domain import OrderIntent
from .venue_policy import REGISTRY, VenuePolicy, find_policy


@dataclass(slots=True)
class AdapterResponse:
    order_id: str
    venue: str
    status: str
    details: Dict[str, str]


class BaseAdapter:
    venue_name: str

    def preview_order(self, intent: OrderIntent) -> Dict[str, str]:
        raise NotImplementedError("Preview not supported for this venue")

    def submit_order(self, intent: OrderIntent) -> AdapterResponse:
        raise NotImplementedError

    def describe_capabilities(self) -> Dict[str, str]:
        return {
            "venue": self.venue_name,
            "preview_support": "false",
            "notes": "Default adapter",
        }

    def policy(self) -> VenuePolicy | None:
        return find_policy(self.venue_name)


class DeribitAdapter(BaseAdapter):
    venue_name = "Deribit"

    def submit_order(self, intent: OrderIntent) -> AdapterResponse:
        return AdapterResponse(
            order_id=f"deribit-{intent.intent_id}",
            venue=self.venue_name,
            status="queued",
            details={"type": intent.order_type.value, "tif": "good_til_cancel"},
        )


class BinanceFuturesAdapter(BaseAdapter):
    venue_name = "Binance USDT Futures"

    def submit_order(self, intent: OrderIntent) -> AdapterResponse:
        return AdapterResponse(
            order_id=f"binance-{intent.intent_id}",
            venue=self.venue_name,
            status="accepted",
            details={"sequence": "mocked", "use_checksum": "true"},
        )

    def describe_capabilities(self) -> Dict[str, str]:
        return {
            "venue": self.venue_name,
            "preview_support": "false",
            "notes": "Depth diff-compatible, rate-limiting strictness mocked.",
        }


class CoinbaseAdvancedTradeAdapter(BaseAdapter):
    venue_name = "Coinbase Advanced Trade"

    def preview_order(self, intent: OrderIntent) -> Dict[str, str]:
        return {
            "venue": self.venue_name,
            "estimated_price": f"{intent.price or 0:.2f}",
            "preview_status": "ready",
        }

    def submit_order(self, intent: OrderIntent) -> AdapterResponse:
        return AdapterResponse(
            order_id=f"coinbase-{intent.intent_id}",
            venue=self.venue_name,
            status="previewed_accepted",
            details={"preview_ok": "true", "risk_passed": "true"},
        )

    def describe_capabilities(self) -> Dict[str, str]:
        return {
            "venue": self.venue_name,
            "preview_support": "true",
            "notes": "Supports preview + order history via v3 brokerage.",
        }


class OKXAdapter(BaseAdapter):
    venue_name = "OKX"

    def submit_order(self, intent: OrderIntent) -> AdapterResponse:
        return AdapterResponse(
            order_id=f"okx-{intent.intent_id}",
            venue=self.venue_name,
            status="queued",
            details={"policy_sensitive": "true", "kyc_level": "2"},
        )

    def describe_capabilities(self) -> Dict[str, str]:
        return {
            "venue": self.venue_name,
            "preview_support": "false",
            "notes": "Policy-sensitive; should be gated by watcher before live use.",
        }


ADAPTERS: dict[str, type[BaseAdapter]] = {
    "Binance USDT Futures": BinanceFuturesAdapter,
    "Deribit": DeribitAdapter,
    "Coinbase Advanced Trade": CoinbaseAdvancedTradeAdapter,
    "OKX": OKXAdapter,
}


def get_adapter(venue_name: str) -> BaseAdapter:
    adapter_cls = ADAPTERS.get(venue_name)
    if adapter_cls is None:
        raise KeyError(f"unknown venue adapter: {venue_name}")
    return adapter_cls()


def list_adapter_capabilities() -> list[dict[str, object]]:
    capabilities = []
    for policy in REGISTRY:
        adapter = get_adapter(policy.name)
        capabilities.append(
            {
                "venue": policy.name,
                "policy": asdict(policy),
                "adapter_capabilities": adapter.describe_capabilities(),
            }
        )
    return capabilities
