from superajan12.market_state import MarketStateValidator
from superajan12.models import Market
from superajan12.orderbook_replay import (
    DeterministicReplayRunner,
    ReplayEvent,
    ReplayEventType,
    fixture_gap_then_resnapshot,
    fixture_healthy_binance_replay,
)


def test_healthy_binance_replay_accepts_all_events() -> None:
    market = Market(id="m-binance", question="BTC above target?", volume_usdc=10_000, liquidity_usdc=5_000)
    runner = DeterministicReplayRunner()

    report = runner.run(market=market, events=fixture_healthy_binance_replay())

    assert report.ok is True
    assert report.total_events == 3
    assert report.accepted_events == 3
    assert report.rejected_events == 0
    assert report.final_snapshot is not None
    assert report.final_snapshot.best_bid == 0.5
    assert report.final_snapshot.best_ask == 0.515
    assert report.final_snapshot.sequence_end == 102


def test_replay_rejects_gap_and_recovers_on_resnapshot() -> None:
    market = Market(id="m-gap", question="Gap recovery?", volume_usdc=10_000, liquidity_usdc=5_000)
    runner = DeterministicReplayRunner()

    report = runner.run(market=market, events=fixture_gap_then_resnapshot())

    assert report.ok is False
    assert report.total_events == 3
    assert report.accepted_events == 2
    assert report.rejected_events == 1
    assert report.resnapshot_events == 1
    assert [step.action for step in report.steps] == ["accept", "reject_gap", "resnapshot"]
    assert report.final_snapshot is not None
    assert report.final_snapshot.sequence_end == 14
    assert report.final_snapshot.best_bid == 0.48


def test_replay_rejects_checksum_mismatch() -> None:
    market = Market(id="m-binance", question="Checksum?", volume_usdc=10_000, liquidity_usdc=5_000)
    events = fixture_healthy_binance_replay()
    bad_event = ReplayEvent(
        event_type=ReplayEventType.DIFF,
        market_id="m-binance",
        venue="binance",
        symbol="BTCUSDT",
        sequence_start=103,
        sequence_end=103,
        bids=(),
        asks=(),
        checksum="bad-103",
        checksum_valid=False,
    )
    runner = DeterministicReplayRunner()

    report = runner.run(market=market, events=[*events, bad_event])

    assert report.ok is False
    assert report.rejected_events == 1
    assert report.steps[-1].validation.checksum_status == "invalid"
    assert "order book checksum mismatch" in report.steps[-1].validation.reasons


def test_empty_replay_is_invalid() -> None:
    market = Market(id="empty", question="No events?")
    runner = DeterministicReplayRunner()

    report = runner.run(market=market, events=[])

    assert report.ok is False
    assert report.total_events == 0
    assert report.rejected_events == 1
    assert report.final_snapshot is None


def test_replay_uses_custom_validator_thresholds() -> None:
    market = Market(id="m-binance", question="Depth?", volume_usdc=10_000, liquidity_usdc=5_000)
    runner = DeterministicReplayRunner(validator=MarketStateValidator(min_depth_usdc=10_000))

    report = runner.run(market=market, events=fixture_healthy_binance_replay())

    assert report.ok is True
    assert all(step.validation.status == "degraded" for step in report.steps)
    assert any("depth" in reason for reason in report.steps[0].validation.reasons)
