"""Hard/soft kill switch state machine with venue/global scopes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional


class KillMode(str, Enum):
    SOFT = "soft"
    HARD = "hard"
    VENUE = "venue"
    GLOBAL = "global"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class KillSwitchState:
    engaged: bool = False
    mode: Optional[KillMode] = None
    since: Optional[datetime] = None
    details: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ReenableConditions:
    risk_fresh: bool = True
    policy_fresh: bool = True
    data_health: bool = True
    incidents_resolved: bool = True


class KillSwitch:
    def __init__(self) -> None:
        self.state = KillSwitchState()

    def engage(self, mode: KillMode, reason: str, context: Dict[str, str] | None = None) -> KillSwitchState:
        self.state.engaged = True
        self.state.mode = mode
        self.state.since = utcnow()
        self.state.details = {"reason": reason, **(context or {})}
        return self.state

    def soft_halt(self, reason: str, venue: str) -> KillSwitchState:
        return self.engage(KillMode.SOFT, reason, {"venue": venue})

    def hard_halt(self, reason: str) -> KillSwitchState:
        return self.engage(KillMode.HARD, reason)

    def venue_halt(self, reason: str, venue: str) -> KillSwitchState:
        return self.engage(KillMode.VENUE, reason, {"venue": venue})

    def global_halt(self, reason: str) -> KillSwitchState:
        return self.engage(KillMode.GLOBAL, reason)

    def release(self, conditions: ReenableConditions) -> KillSwitchState:
        if not self.can_reenable(conditions):
            raise RuntimeError("reenable conditions not met")
        self.state.engaged = False
        self.state.mode = None
        self.state.details = {"reenabled_at": utcnow().isoformat()}
        self.state.since = None
        return self.state

    def can_reenable(self, conditions: ReenableConditions) -> bool:
        return all(
            [conditions.risk_fresh, conditions.policy_fresh, conditions.data_health, conditions.incidents_resolved]
        )

    def snapshot(self) -> dict[str, str | bool]:
        return {
            "engaged": self.state.engaged,
            "mode": self.state.mode.value if self.state.mode else "none",
            "since": self.state.since.isoformat() if self.state.since else None,
            "details": self.state.details,
        }
