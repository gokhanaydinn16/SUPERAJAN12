"""Policy watcher that tracks venue capability snapshots and emits roll-out signals."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .venue_policy import VenuePolicy


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class PolicySnapshot:
    captured_at: datetime
    entries: Dict[str, Dict[str, object]] = field(default_factory=dict)

    def to_json(self) -> str:
        payload = {
            "captured_at": self.captured_at.isoformat(),
            "entries": self.entries,
        }
        return json.dumps(payload, indent=2)

    @staticmethod
    def from_dict(data: dict) -> "PolicySnapshot":
        captured_at = datetime.fromisoformat(data["captured_at"])
        return PolicySnapshot(captured_at=captured_at, entries=data["entries"])


class PolicyWatcher:
    """Tracks policy snapshots and surfaces freshness/requirement changes."""

    def __init__(self, snapshot_path: Path, stale_after: timedelta = timedelta(hours=2)) -> None:
        self.snapshot_path = snapshot_path
        self.stale_after = stale_after
        self._current: Optional[PolicySnapshot] = None
        self._previous: Optional[PolicySnapshot] = None

    def capture(self, policies: List[VenuePolicy]) -> PolicySnapshot:
        self._previous = self.load_previous()
        entries = {policy.name: asdict(policy) for policy in policies}
        snapshot = PolicySnapshot(captured_at=utcnow(), entries=entries)
        self._current = snapshot
        self._write(snapshot)
        return snapshot

    def _write(self, snapshot: PolicySnapshot) -> None:
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with self.snapshot_path.open("w", encoding="utf-8") as fh:
            fh.write(snapshot.to_json())

    def load_previous(self) -> Optional[PolicySnapshot]:
        if not self.snapshot_path.exists():
            return None
        with self.snapshot_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return PolicySnapshot.from_dict(data)

    def detect_changes(self, previous: Optional[PolicySnapshot]) -> bool:
        if previous is None or self._current is None:
            return False
        return previous.entries != self._current.entries

    def is_fresh(self, previous: Optional[PolicySnapshot]) -> bool:
        if previous is None:
            return True
        return utcnow() - previous.captured_at <= self.stale_after

    def rollout_signal(self) -> Dict[str, object]:
        previous = self._previous
        current = self._current or self.load_previous()
        if current is None:
            return {"policy_fresh": False, "changes_detected": False, "message": "no snapshot"}
        changes = self.detect_changes(previous)
        fresh = self.is_fresh(previous)
        signal = {
            "policy_fresh": fresh,
            "changes_detected": changes,
            "last_captured": current.captured_at.isoformat(),
        }
        if not fresh:
            signal["message"] = "policy snapshot is stale"
        elif changes:
            signal["message"] = "policy changes detected; flag rollout"
        else:
            signal["message"] = "policy steady"
        return signal
