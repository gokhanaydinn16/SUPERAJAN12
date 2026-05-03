"""Tests for the deterministic risk engine."""

from datetime import datetime, timezone
from unittest import TestCase

from src.agent_os.config import RiskConfig
from src.agent_os.domain import OrderIntent, OrderSide, OrderType
from src.agent_os.risk import RiskEngine


class RiskEngineTests(TestCase):
    def setUp(self) -> None:
        self.engine = RiskEngine(config=RiskConfig(max_position_size=2.0, duplicate_window_seconds=10))
        self.engine.update_market_timestamp(datetime.now(timezone.utc))

    def _intent(self, order_id: str) -> OrderIntent:
        return OrderIntent(
            symbol="BTC-PERP",
            venue="binance-test",
            side=OrderSide.BUY,
            quantity=0.5,
            order_type=OrderType.LIMIT,
            price=40000.0,
            intent_id=order_id,
        )

    def test_allows_when_within_limits(self) -> None:
        intent = self._intent("intent-1")
        decision = self.engine.evaluate(intent)
        self.assertTrue(decision.allowed)
        self.engine.record_fill(intent, fill_price=40000.0)

    def test_duplicate_guard_triggers(self) -> None:
        intent = self._intent("intent-dup")
        first = self.engine.evaluate(intent)
        second = self.engine.evaluate(intent)
        self.assertTrue(first.allowed)
        self.assertFalse(second.allowed)
        self.assertIn("duplicate_intent", second.breaches)

    def test_kill_switch_blocks_orders(self) -> None:
        self.engine.toggle_kill_switch(True)
        intent = self._intent("intent-kill")
        decision = self.engine.evaluate(intent)
        self.assertFalse(decision.allowed)
        self.assertIn("kill_switch", decision.breaches)
