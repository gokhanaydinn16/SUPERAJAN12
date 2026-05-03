from __future__ import annotations

import unittest

from src.agent_os.domain import DecisionAction, DecisionSuggestion, MarketSnapshot, OrderIntent, OrderSide, OrderType, ResearchSignal


class DomainTests(unittest.TestCase):
    def test_market_snapshot_computes_mid(self) -> None:
        snapshot = MarketSnapshot("venue", "BTC-PERP", 1, 100.0, 101.0, 1.0, 1.0)
        self.assertEqual(snapshot.mid_price, 100.5)

    def test_suggestion_requires_signal(self) -> None:
        with self.assertRaises(ValueError):
            DecisionSuggestion("BTC-PERP", "venue", DecisionAction.INCREASE, 0.8, "x", 0.1, 100.0, [])

    def test_limit_intent_requires_price(self) -> None:
        with self.assertRaises(ValueError):
            OrderIntent("BTC-PERP", "venue", OrderSide.BUY, 1.0, OrderType.LIMIT)


if __name__ == "__main__":
    unittest.main()
