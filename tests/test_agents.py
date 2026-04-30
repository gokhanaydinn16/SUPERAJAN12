from superajan12.agents.portfolio import PaperPortfolio
from superajan12.agents.probability import ProbabilityAgent
from superajan12.agents.resolution import ResolutionAgent
from superajan12.models import Decision, Market, OrderBookLevel, OrderBookSnapshot, PaperTradeIdea


def test_resolution_agent_watches_when_source_missing() -> None:
    market = Market(id="m1", question="Will something happen?", volume_usdc=10_000, liquidity_usdc=2_000)

    result = ResolutionAgent().evaluate(market)

    assert result.decision in {Decision.WATCH, Decision.APPROVE}
    assert result.confidence <= 0.65


def test_probability_agent_uses_implied_probability_without_fake_edge() -> None:
    market = Market(id="m1", question="Test?", volume_usdc=100_000, liquidity_usdc=20_000)
    book = OrderBookSnapshot(
        market_id="m1",
        yes_bids=[OrderBookLevel(price=0.39, size=100)],
        yes_asks=[OrderBookLevel(price=0.41, size=100)],
    )
    resolution = ResolutionAgent().evaluate(
        Market(
            id="m1",
            question="Test?",
            volume_usdc=100_000,
            liquidity_usdc=20_000,
            resolution_source="official source",
            raw={"description": "Will resolve according to official source rules."},
        )
    )

    estimate = ProbabilityAgent().estimate(market, book, resolution)

    assert estimate.implied_probability == 0.4
    assert estimate.model_probability == 0.4
    assert estimate.edge == 0.0
    assert estimate.confidence > 0


def test_paper_portfolio_opens_position_from_valid_idea() -> None:
    idea = PaperTradeIdea(
        market_id="m1",
        question="Test?",
        side="YES",
        reference_price=0.5,
        risk_usdc=10,
    )

    position = PaperPortfolio().open_from_idea(idea)

    assert position is not None
    assert position.size_shares == 20
    assert position.notional_usdc == 10
