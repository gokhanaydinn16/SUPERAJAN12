"""Drift detection between local state and venue-reported state."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List


class DriftSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriftReport:
    severity: DriftSeverity
    mismatches: int
    details: List[str]
    mitigation: str


class ReconciliationWorker:
    """Compares local and venue states to surface dangerous drifts."""

    def compare_orders(self, local: Iterable[Dict[str, object]], venue: Iterable[Dict[str, object]]) -> DriftReport:
        local_set = {(order["order_id"], order.get("state")) for order in local}
        venue_set = {(order["order_id"], order.get("state")) for order in venue}
        mismatches = local_set.symmetric_difference(venue_set)
        mismatch_count = len(mismatches)
        severity = self._classify_order_mismatch(mismatch_count, len(local_set) or 1)
        details = [f"Order mismatch: {entry}" for entry in mismatches]
        mitigation = "Run order reconciliation, cancel unexpected orders, refresh local book."
        return DriftReport(severity, mismatch_count, details, mitigation)

    def compare_positions(self, local: Dict[str, float], venue: Dict[str, float]) -> DriftReport:
        mismatches = []
        mismatch_count = 0
        for symbol, local_qty in local.items():
            venue_qty = venue.get(symbol, 0.0)
            if abs(local_qty - venue_qty) > max(abs(local_qty), abs(venue_qty), 1e-6) * 0.05:
                mismatch_count += 1
                mismatches.append(f"{symbol}: local {local_qty} vs venue {venue_qty}")
        severity = self._classify_position_mismatch(mismatch_count, len(local) or 1)
        mitigation = "Trigger position reconciliation, freeze execution if severity high."
        return DriftReport(severity, mismatch_count, mismatches, mitigation)

    def detect_drift(
        self,
        local_orders: Iterable[Dict[str, object]],
        venue_orders: Iterable[Dict[str, object]],
        local_positions: Dict[str, float],
        venue_positions: Dict[str, float],
    ) -> List[DriftReport]:
        order_report = self.compare_orders(local_orders, venue_orders)
        position_report = self.compare_positions(local_positions, venue_positions)
        return [order_report, position_report]

    def _classify_order_mismatch(self, count: int, base: int) -> DriftSeverity:
        ratio = count / base
        if ratio == 0:
            return DriftSeverity.LOW
        if ratio < 0.2:
            return DriftSeverity.MEDIUM
        if ratio <= 1.0:
            return DriftSeverity.HIGH
        return DriftSeverity.CRITICAL

    def _classify_position_mismatch(self, count: int, base: int) -> DriftSeverity:
        if count == 0:
            return DriftSeverity.LOW
        ratio = count / base
        if ratio >= 1.0:
            return DriftSeverity.CRITICAL
        return self._classify_order_mismatch(count, base)
