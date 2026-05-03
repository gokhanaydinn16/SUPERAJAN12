"""Quantifiable readiness gates for production promotion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReadinessThresholds:
    max_stale_rate: float = 0.05
    max_duplicate_rate: float = 0.02
    min_pnl_explained: float = 0.8
    min_fill_quality: float = 0.95
    min_incident_free_run: int = 5
    min_preview_pass_ratio: float = 0.95
    require_policy_freshness: bool = True


@dataclass(slots=True)
class ReadinessSnapshot:
    stale_rate: float
    duplicate_rate: float
    pnl_explained: float
    fill_quality: float
    incident_free_streak: int
    preview_pass_ratio: float
    policy_fresh: bool

    def as_dict(self) -> dict[str, float | int | bool]:
        return {
            "stale_rate": self.stale_rate,
            "duplicate_rate": self.duplicate_rate,
            "pnl_explained": self.pnl_explained,
            "fill_quality": self.fill_quality,
            "incident_free_streak": self.incident_free_streak,
            "preview_pass_ratio": self.preview_pass_ratio,
            "policy_fresh": self.policy_fresh,
        }


class ReadinessTracker:
    def __init__(self) -> None:
        self._cycle_count = 0
        self._stale_events = 0
        self._duplicate_events = 0
        self._pnl_explained_total = 0.0
        self._fill_quality_total = 0.0
        self._incident_free_streak = 0
        self._preview_checks = 0
        self._preview_passes = 0
        self._policy_fresh = True

    def record_cycle(
        self,
        *,
        stale: bool,
        duplicate: bool,
        pnl_explained: float,
        fill_quality: float,
        incident: bool,
        preview_passed: bool = True,
        policy_fresh: bool = True,
    ) -> None:
        self._cycle_count += 1
        self._stale_events += 1 if stale else 0
        self._duplicate_events += 1 if duplicate else 0
        self._pnl_explained_total += pnl_explained
        self._fill_quality_total += fill_quality
        self._preview_checks += 1
        self._preview_passes += 1 if preview_passed else 0
        self._policy_fresh = self._policy_fresh and policy_fresh
        if incident:
            self._incident_free_streak = 0
        else:
            self._incident_free_streak += 1

    def snapshot(self) -> ReadinessSnapshot:
        if self._cycle_count == 0:
            return ReadinessSnapshot(0.0, 0.0, 0.0, 0.0, self._incident_free_streak, 0.0, self._policy_fresh)
        return ReadinessSnapshot(
            stale_rate=self._stale_events / self._cycle_count,
            duplicate_rate=self._duplicate_events / self._cycle_count,
            pnl_explained=self._pnl_explained_total / self._cycle_count,
            fill_quality=self._fill_quality_total / self._cycle_count,
            incident_free_streak=self._incident_free_streak,
            preview_pass_ratio=(self._preview_passes / self._preview_checks) if self._preview_checks else 0.0,
            policy_fresh=self._policy_fresh,
        )

    def is_ready(self, thresholds: ReadinessThresholds) -> tuple[bool, ReadinessSnapshot]:
        snapshot = self.snapshot()
        ready = (
            snapshot.stale_rate <= thresholds.max_stale_rate
            and snapshot.duplicate_rate <= thresholds.max_duplicate_rate
            and snapshot.pnl_explained >= thresholds.min_pnl_explained
            and snapshot.fill_quality >= thresholds.min_fill_quality
            and snapshot.incident_free_streak >= thresholds.min_incident_free_run
            and snapshot.preview_pass_ratio >= thresholds.min_preview_pass_ratio
            and (snapshot.policy_fresh if thresholds.require_policy_freshness else True)
        )
        return ready, snapshot
