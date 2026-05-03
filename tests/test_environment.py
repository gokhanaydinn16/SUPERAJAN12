from __future__ import annotations

import unittest

from src.agent_os.environment import Stage, StageGate, StageTransition


class EnvironmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = StageGate()

    def test_sequential_transition_accepts_checks(self) -> None:
        transition = StageTransition(
            from_stage=Stage.historical_replay,
            to_stage=Stage.paper,
            checks={"risk_policy": True, "policy_review": True},
        )
        self.gate.request_transition(transition)
        self.assertEqual(self.gate.current_stage, Stage.paper)

    def test_skip_stage_rejected(self) -> None:
        transition = StageTransition(
            from_stage=Stage.historical_replay,
            to_stage=Stage.testnet,
            checks={"risk_policy": True},
        )
        with self.assertRaises(ValueError):
            self.gate.request_transition(transition)

    def test_failed_checks_block_transition(self) -> None:
        transition = StageTransition(
            from_stage=Stage.historical_replay,
            to_stage=Stage.paper,
            checks={"risk_policy": False},
        )
        with self.assertRaises(RuntimeError):
            self.gate.request_transition(transition)

    def test_rollback_to_previous_stage(self) -> None:
        transition = StageTransition(
            from_stage=Stage.historical_replay,
            to_stage=Stage.paper,
            checks={"risk_policy": True},
        )
        self.gate.request_transition(transition)
        self.gate.rollback(Stage.historical_replay)
        self.assertEqual(self.gate.current_stage, Stage.historical_replay)
        snapshot = self.gate.snapshot()
        self.assertIn("historical_replay", snapshot["history"])


if __name__ == "__main__":
    unittest.main()
