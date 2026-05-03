from __future__ import annotations

import unittest

from src.agent_os.market_data import MarketDataValidator, PriceLevel


class MarketDataTests(unittest.TestCase):
    def test_gap_is_recorded(self) -> None:
        validator = MarketDataValidator("venue", "BTC-PERP")
        validator.ingest(1, [PriceLevel(100, 1)], [PriceLevel(101, 1)])
        validator.ingest(3, [PriceLevel(100, 1)], [PriceLevel(101, 1)])
        self.assertEqual(validator.heartbeat()["gap_count"], 1)


if __name__ == "__main__":
    unittest.main()
