"""Tests for the advisory ResearchAgent."""

from unittest import TestCase

from src.agent_os.domain import MarketSnapshot
from src.agent_os.research import ResearchAgent, default_signals


class ResearchAgentTests(TestCase):
    def setUp(self) -> None:
        self.agent = ResearchAgent("test-agent")
        self.market = MarketSnapshot(
            venue="binance-test",
            symbol="BTC-PERP",
            sequence=1,
            best_bid=30000.0,
            best_ask=30010.0,
            bid_size=1.0,
            ask_size=1.0,
        )

    def test_build_suggestion_from_default_signals(self) -> None:
        suggestion = self.agent.build_suggestion(self.market, default_signals())
        self.assertEqual(suggestion.symbol, "BTC-PERP")
        self.assertTrue(suggestion.signals)
        self.assertGreaterEqual(suggestion.confidence, 0.15)
        self.assertLessEqual(suggestion.confidence, 0.95)
