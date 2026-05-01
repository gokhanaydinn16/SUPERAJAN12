from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class SafetyState:
    safe_mode: bool
    kill_switch: bool
    reasons: tuple[str, ...]

    @property
    def can_open_new_positions(self) -> bool:
        return not self.safe_mode and not self.kill_switch


class SafetyController:
    """Central safe-mode / kill-switch controller.

    Phase 1 is in-memory and conservative. Later phases will persist incidents,
    connect alerts, and enforce this state inside live execution.
    """

    def __init__(self) -> None:
        self._safe_mode = False
        self._kill_switch = False
        self._safe_mode_reason: str | None = None
        self._kill_switch_reason: str | None = None

    def enable_safe_mode(self, reason: str) -> None:
        self._safe_mode = True
        self._safe_mode_reason = reason

    def enable_kill_switch(self, reason: str) -> None:
        self._kill_switch = True
        self._kill_switch_reason = reason
        if not self._safe_mode:
            self._safe_mode = True
            self._safe_mode_reason = "kill-switch enabled"

    def clear_safe_mode(self) -> None:
        self._safe_mode = False
        self._kill_switch = False
        self._safe_mode_reason = None
        self._kill_switch_reason = None

    def disable_kill_switch(self) -> None:
        self._kill_switch = False
        self._kill_switch_reason = None
        if self._safe_mode and self._safe_mode_reason == "kill-switch enabled":
            self._safe_mode = False
            self._safe_mode_reason = None

    def state(self) -> SafetyState:
        reasons = tuple(
            reason
            for reason in (self._safe_mode_reason, self._kill_switch_reason)
            if reason
        )
        return SafetyState(
            safe_mode=self._safe_mode,
            kill_switch=self._kill_switch,
            reasons=reasons,
        )


@lru_cache(maxsize=1)
def get_safety_controller() -> SafetyController:
    return SafetyController()
