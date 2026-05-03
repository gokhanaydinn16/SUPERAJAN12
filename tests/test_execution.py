"""Smoke tests for the paper execution engine."""

from unittest import TestCase

from src.agent_os.domain import MarketSnapshot, OrderIntent, OrderSide, OrderState, OrderType
from src.agent_os.execution import ExecutionEngine


class ExecutionEngineTests(TestCase):
    def setUp(self) -> None:
        self.engine = ExecutionEngine(venue="binance-test")
        snapshot = MarketSnapshot(
            venue="binance-test",
            symbol="BTC-PERP",
            sequence=1,
            best_bid=40000.0,
            best_ask=40010.0,
            bid_size=1.0,
            ask_size=1.0,
        )
        self.engine.update_market(snapshot)

    def _intent(self, order_id: str) -> OrderIntent:
        return OrderIntent(
            symbol="BTC-PERP",
            venue="binance-test",
            side=OrderSide.BUY,
            quantity=1.0,
            order_type=OrderType.LIMIT,
            price=40005.0,
            intent_id=order_id,
        )

    def test_submit_creates_order_and_fill(self) -> None:
        intent = self._intent("intent-1")
        order = self.engine.submit(intent)
        self.assertEqual(order.state, OrderState.OPEN)
        fill = self.engine.try_fill(order.order_id)
        self.assertIsNotNone(fill)
        self.assertEqual(order.state, OrderState.FILLED)

    def test_disconnect_cancels_open_orders(self) -> None:
        intent = self._intent("intent-2")
        order = self.engine.submit(intent)
        cancelled = self.engine.disconnect()
        self.assertIn(order, cancelled)
