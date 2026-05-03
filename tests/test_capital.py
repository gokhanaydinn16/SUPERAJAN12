from __future__ import annotations

import unittest

from src.agent_os.capital import CapitalController


class CapitalTests(unittest.TestCase):
    def setUp(self) -> None:
        allocations = {
            "micro": ("Binance USDT Futures", 100_000.0),
            "trend": ("Deribit", 50_000.0),
        }
        self.controller = CapitalController(allocations)

    def test_allocation_respects_max_at_risk(self) -> None:
        self.assertFalse(self.controller.allocate_for("micro", 10_000.0))

    def test_release_and_available(self) -> None:
        self.controller.adjust_max_at_risk(0.2)
        ok = self.controller.allocate_for("micro", 15_000.0)
        self.assertTrue(ok)
        self.controller.release_for("micro", 5_000.0)
        snapshot = self.controller.snapshot()
        self.assertAlmostEqual(snapshot["micro"], 100_000.0 - 10_000.0)

    def test_ladder_increase(self) -> None:
        ladder = self.controller.ladder()
        ladder.increase("canary_live")
        self.assertEqual(ladder.current_level, "canary_live")


if __name__ == "__main__":
    unittest.main()
