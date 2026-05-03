from __future__ import annotations

import unittest

from src.agent_os.readiness import ReadinessThresholds, ReadinessTracker


class ReadinessTests(unittest.TestCase):
    def test_tracking_rates_and_ready_flag(self) -> None:
        tracker = ReadinessTracker()
        thresholds = ReadinessThresholds(
            max_stale_rate=0.2,
            max_duplicate_rate=0.2,
            min_pnl_explained=0.5,
            min_fill_quality=0.5,
            min_incident_free_run=2,
        )
        tracker.record_cycle(stale=False, duplicate=False, pnl_explained=0.6, fill_quality=0.7, incident=False, preview_passed=True, policy_fresh=True)
        tracker.record_cycle(stale=False, duplicate=False, pnl_explained=0.7, fill_quality=0.8, incident=False, preview_passed=True, policy_fresh=True)
        ready, snapshot = tracker.is_ready(thresholds)
        self.assertTrue(ready)
        self.assertAlmostEqual(snapshot.stale_rate, 0.0)
        self.assertEqual(snapshot.incident_free_streak, 2)

    def test_incident_breaks_streak(self) -> None:
        tracker = ReadinessTracker()
        thresholds = ReadinessThresholds(min_incident_free_run=1)
        tracker.record_cycle(stale=False, duplicate=False, pnl_explained=0.9, fill_quality=0.9, incident=True, preview_passed=False, policy_fresh=True)
        ready, snapshot = tracker.is_ready(thresholds)
        self.assertFalse(ready)
        self.assertEqual(snapshot.incident_free_streak, 0)


if __name__ == "__main__":
    unittest.main()
