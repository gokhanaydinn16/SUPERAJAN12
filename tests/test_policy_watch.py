from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

from src.agent_os.policy_watch import PolicyWatcher
from src.agent_os.venue_policy import REGISTRY


class PolicyWatchTests(unittest.TestCase):
    def test_detects_changes_and_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policies.json"
            watcher = PolicyWatcher(snapshot_path=path, stale_after=timedelta(hours=1))
            watcher.capture(REGISTRY)
            signal = watcher.rollout_signal()
            self.assertTrue(signal["policy_fresh"])
            self.assertFalse(signal["changes_detected"])

            altered = list(REGISTRY)
            altered[0] = replace(altered[0], notes="changed")
            watcher.capture(altered)
            signal = watcher.rollout_signal()
            self.assertTrue(signal["policy_fresh"])
            self.assertTrue(signal["changes_detected"])

            previous = watcher._previous
            self.assertIsNotNone(previous)
            previous.captured_at = previous.captured_at - timedelta(hours=3)
            watcher._previous = previous
            signal = watcher.rollout_signal()
            self.assertFalse(signal["policy_fresh"])


if __name__ == "__main__":
    unittest.main()
