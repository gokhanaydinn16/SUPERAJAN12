from superajan12.market_state import MarketStateValidator
from superajan12.models import Market
from superajan12.venue_adapters import (
    VenueCapability,
    VenueName,
    VenueOrderRequest,
    build_dry_run_venue_registry,
    default_venue_profiles,
)


def test_default_profiles_keep_live_orders_disabled() -> None:
    profiles = default_venue_profiles()

    assert {profile.name for profile in profiles} == {
        VenueName.DERIBIT,
        VenueName.BINANCE,
        VenueName.COINBASE,
        VenueName.OKX,
    }
    assert all(profile.live_orders_enabled is False for profile in profiles)


def test_dry_run_registry_exposes_capability_summary() -> None:
    registry = build_dry_run_venue_registry()

    summary = registry.readiness_summary()

    assert summary["deribit"]["ok"] is True
    assert summary["binance"]["status"] == "ready"
    assert "order_preview" in summary["coinbase"]["capabilities"]
    assert "policy_gate_required" in summary["okx"]["capabilities"]
    assert all(item["live_orders_enabled"] is False for item in summary.values())


def test_dry_run_orderbook_is_market_state_compatible() -> None:
    registry = build_dry_run_venue_registry()
    adapter = registry.get(VenueName.BINANCE)
    market = Market(id="btc-election", question="BTC above target?", volume_usdc=10_000, liquidity_usdc=5_000)

    snapshot = adapter.get_order_book(market_id=market.id, symbol="BTCUSDT", depth=5)
    result = MarketStateValidator().validate(market, snapshot)

    assert snapshot.venue == "binance"
    assert snapshot.depth_levels == 5
    assert result.ok is True
    assert result.status == "healthy"
    assert result.sequence_status == "validated"
    assert result.checksum_status == "validated"


def test_preview_order_accepts_only_dry_run_supported_preview() -> None:
    registry = build_dry_run_venue_registry()
    adapter = registry.get(VenueName.COINBASE)

    preview = adapter.preview_order(
        VenueOrderRequest(
            venue=VenueName.COINBASE,
            symbol="btc-usd",
            side="BUY",
            price=0.55,
            size=20,
            client_order_id="preview-1",
            dry_run=True,
        )
    )

    assert preview.accepted is True
    assert preview.dry_run is True
    assert preview.normalized_symbol == "BTC-USD"
    assert preview.estimated_notional_usdc == 11.0


def test_preview_order_rejects_live_or_unsupported_requests() -> None:
    registry = build_dry_run_venue_registry()
    binance = registry.get(VenueName.BINANCE)

    preview = binance.preview_order(
        VenueOrderRequest(
            venue=VenueName.BINANCE,
            symbol="BTCUSDT",
            side="BUY",
            price=0.5,
            size=10,
            client_order_id="live-1",
            dry_run=False,
        )
    )

    assert preview.accepted is False
    assert "live order submission is disabled" in preview.reasons
    assert "venue does not support local order preview" in preview.reasons


def test_profile_supports_capability_helper() -> None:
    coinbase = next(profile for profile in default_venue_profiles() if profile.name == VenueName.COINBASE)

    assert coinbase.supports(VenueCapability.ORDER_PREVIEW) is True
    assert coinbase.supports(VenueCapability.WEBSOCKET_ORDERBOOK) is False
