from __future__ import annotations

import unittest

from src.agent_os.kill_switch import KillMode, KillSwitch, ReenableConditions


class KillSwitchTests(unittest.TestCase):
    def test_soft_halt_and_release(self) -> None:
        switch = KillSwitch()
        state = switch.soft_halt("stale data", "Binance USDT Futures")
        self.assertTrue(state.engaged)
        self.assertEqual(state.mode, KillMode.SOFT)
        released = switch.release(ReenableConditions())
        self.assertFalse(released.engaged)

    def test_release_requires_conditions(self) -> None:
        switch = KillSwitch()
        switch.hard_halt("risk breach")
        with self.assertRaises(RuntimeError):
            switch.release(ReenableConditions(policy_fresh=False))


if __name__ == "__main__":
    unittest.main()
