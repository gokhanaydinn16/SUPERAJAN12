"""Venue capability and policy registry for the autonomous system."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VenuePolicy:
    name: str
    supports_testnet: bool
    supports_demo: bool
    order_preview: bool
    live_kyc_requirement: str
    websocket_style: str
    rate_limit_mode: str
    policy_sensitive: bool
    notes: str


REGISTRY: list[VenuePolicy] = [
    VenuePolicy(
        name="Binance USDT Futures",
        supports_testnet=True,
        supports_demo=False,
        order_preview=False,
        live_kyc_requirement="Live trading depends on account and regional eligibility requirements.",
        websocket_style="depth diff streams and trade streams",
        rate_limit_mode="request-weight and order-rate limits",
        policy_sensitive=False,
        notes="High-throughput venue; sequence-gap recovery and desync telemetry should be first-class.",
    ),
    VenuePolicy(
        name="Deribit",
        supports_testnet=True,
        supports_demo=False,
        order_preview=False,
        live_kyc_requirement="Separate testnet identity; production requirements differ from testnet.",
        websocket_style="JSON-RPC over WebSocket",
        rate_limit_mode="credit-based rate limiting",
        policy_sensitive=False,
        notes="Testnet is close to production semantics but can be taken down without notice and lacks production HFT access.",
    ),
    VenuePolicy(
        name="Coinbase Advanced Trade",
        supports_testnet=True,
        supports_demo=False,
        order_preview=True,
        live_kyc_requirement="Advanced Trade enabled account and valid API key permissions.",
        websocket_style="REST v3 brokerage plus WebSocket market data",
        rate_limit_mode="endpoint-specific permissions and limits",
        policy_sensitive=False,
        notes="Order preview is a strong fit for deterministic pre-trade validation.",
    ),
    VenuePolicy(
        name="OKX",
        supports_testnet=True,
        supports_demo=True,
        order_preview=False,
        live_kyc_requirement="KYC Level 2 for live trading, Level 1 for demo",
        websocket_style="channel subscriptions over WebSocket and REST",
        rate_limit_mode="endpoint and channel-specific limits",
        policy_sensitive=True,
        notes="Live API access is policy-sensitive; changelog and agreement monitoring should gate rollout.",
    ),
]


def find_policy(name: str) -> VenuePolicy | None:
    for policy in REGISTRY:
        if policy.name == name:
            return policy
    return None
