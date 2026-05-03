from __future__ import annotations

import unittest

from src.agent_os.reconciliation import DriftSeverity, ReconciliationWorker


class ReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.worker = ReconciliationWorker()

    def test_order_mismatch_detects_severity(self) -> None:
        local = [{"order_id": "1", "state": "open"}, {"order_id": "2", "state": "filled"}]
        venue = [{"order_id": "1", "state": "open"}, {"order_id": "3", "state": "open"}]
        report = self.worker.compare_orders(local, venue)
        self.assertEqual(report.severity, DriftSeverity.HIGH)
        self.assertTrue(report.details)

    def test_position_mismatch_critical(self) -> None:
        local_positions = {"BTC-PERP": 1.0}
        venue_positions = {"BTC-PERP": 0.0}
        report = self.worker.compare_positions(local_positions, venue_positions)
        self.assertEqual(report.severity, DriftSeverity.CRITICAL)

    def test_detect_drift_returns_two_reports(self) -> None:
        reports = self.worker.detect_drift(
            local_orders=[{"order_id": "1", "state": "open"}],
            venue_orders=[{"order_id": "1", "state": "open"}],
            local_positions={"BTC": 1.0},
            venue_positions={"BTC": 1.0},
        )
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].severity, DriftSeverity.LOW)
        self.assertEqual(reports[1].severity, DriftSeverity.LOW)


if __name__ == "__main__":
    unittest.main()
