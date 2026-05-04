from superajan12.agents.risk import RiskEngine
from superajan12.models import Decision, Market, OrderBookLevel, OrderBookSnapshot
from superajan12.risk_controls import PreTradeVeto, PreTradeVetoCode, RiskControlContext


def make_engine() -> RiskEngine:
    return RiskEngine(
        max_market_risk_usdc=10,
        max_daily_loss_usdc=25,
        min_volume_usdc=1000,
        max_spread_bps=1200,
        min_liquidity_usdc=250,
    )


def make_market() -> Market:
    return Market(id="1", question="Test?", volume_usdc=5000, liquidity_usdc=1000)


def make_book() -> OrderBookSnapshot:
    return OrderBookSnapshot(
        market_id="1",
        yes_bids=[OrderBookLevel(price=0.49, size=100)],
        yes_asks=[OrderBookLevel(price=0.51, size=100)],
    )


def test_risk_engine_rejects_low_volume_market() -> None:
    market = Market(id="1", question="Test?", volume_usdc=10, liquidity_usdc=500)
    decision = make_engine().evaluate_market(market, make_book())

    assert decision.decision == Decision.REJECT
    assert any("low_volume" in reason and "hacim dusuk" in reason for reason in decision.reasons)


def test_risk_engine_approves_clean_market() -> None:
    decision = make_engine().evaluate_market(make_market(), make_book())

    assert decision.decision == Decision.APPROVE
    assert decision.max_risk_usdc == 10


def test_risk_engine_rejects_kill_switch_safe_mode_and_disconnect() -> None:
    context = RiskControlContext(
        safe_mode=True,
        kill_switch_active=True,
        connected=False,
    )

    decision = make_engine().evaluate_market(make_market(), make_book(), control_context=context)

    assert decision.decision == Decision.REJECT
    assert any("safe_mode" in reason for reason in decision.reasons)
    assert any("kill_switch" in reason for reason in decision.reasons)
    assert any("disconnected" in reason for reason in decision.reasons)


def test_risk_engine_rejects_stale_data() -> None:
    context = RiskControlContext(market_data_stale=True)

    decision = make_engine().evaluate_market(make_market(), make_book(), control_context=context)

    assert decision.decision == Decision.REJECT
    assert any("stale_data" in reason for reason in decision.reasons)


def test_risk_engine_rejects_daily_loss_limit_from_context() -> None:
    context = RiskControlContext(current_daily_pnl_usdc=-25)

    decision = make_engine().evaluate_market(make_market(), make_book(), control_context=context)

    assert decision.decision == Decision.REJECT
    assert any("daily_loss_limit" in reason for reason in decision.reasons)


def test_risk_engine_rejects_market_position_cap() -> None:
    context = RiskControlContext(
        current_market_exposure_usdc=95,
        requested_risk_usdc=10,
        max_market_exposure_usdc=100,
    )

    decision = make_engine().evaluate_market(make_market(), make_book(), control_context=context)

    assert decision.decision == Decision.REJECT
    assert any("position_cap" in reason for reason in decision.reasons)


def test_risk_engine_rejects_total_exposure_cap() -> None:
    context = RiskControlContext(
        current_total_exposure_usdc=995,
        requested_risk_usdc=10,
        max_total_exposure_usdc=1000,
    )

    decision = make_engine().evaluate_market(make_market(), make_book(), control_context=context)

    assert decision.decision == Decision.REJECT
    assert any("exposure_cap" in reason for reason in decision.reasons)


def test_risk_engine_rejects_extra_vetoes() -> None:
    context = RiskControlContext(
        extra_vetoes=(PreTradeVeto(PreTradeVetoCode.KILL_SWITCH, "operator forced halt"),)
    )

    decision = make_engine().evaluate_market(make_market(), make_book(), control_context=context)

    assert decision.decision == Decision.REJECT
    assert any("operator forced halt" in reason for reason in decision.reasons)


def test_risk_engine_keeps_backward_compatible_safe_mode_argument() -> None:
    decision = make_engine().evaluate_market(make_market(), make_book(), safe_mode=True)

    assert decision.decision == Decision.REJECT
    assert any("safe_mode" in reason for reason in decision.reasons)
