from superajan12.market_state import MarketStateValidator
from superajan12.models import Market, OrderBookLevel, OrderBookSnapshot


def test_market_state_validator_accepts_healthy_snapshot() -> None:
    market = Market(id="m1", question="Healthy?", volume_usdc=5000, liquidity_usdc=1200)
    book = OrderBookSnapshot(
        market_id="m1",
        yes_bids=[OrderBookLevel(price=0.49, size=300)],
        yes_asks=[OrderBookLevel(price=0.51, size=300)],
    )

    result = MarketStateValidator().validate(market, book)

    assert result.ok is True
    assert result.status == "healthy"
    assert result.midpoint == 0.5


def test_market_state_validator_flags_crossed_book_as_invalid() -> None:
    market = Market(id="m1", question="Crossed?", volume_usdc=5000, liquidity_usdc=1200)
    book = OrderBookSnapshot(
        market_id="m1",
        yes_bids=[OrderBookLevel(price=0.55, size=300)],
        yes_asks=[OrderBookLevel(price=0.54, size=300)],
    )

    result = MarketStateValidator().validate(market, book)

    assert result.ok is False
    assert result.status == "invalid"
    assert any("crossed" in reason for reason in result.reasons)


def test_market_state_validator_marks_wide_spread_as_degraded() -> None:
    market = Market(id="m1", question="Wide spread?", volume_usdc=5000, liquidity_usdc=1200)
    book = OrderBookSnapshot(
        market_id="m1",
        yes_bids=[OrderBookLevel(price=0.30, size=400)],
        yes_asks=[OrderBookLevel(price=0.70, size=400)],
    )

    result = MarketStateValidator(max_spread_bps=500).validate(market, book)

    assert result.ok is True
    assert result.status == "degraded"
    assert any("spread" in reason for reason in result.reasons)
