from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from superajan12.config import get_settings


@dataclass(frozen=True)
class SafetyState:
    safe_mode: bool
    kill_switch: bool
    stale_data_lock: bool
    disconnect_lock: bool
    reasons: tuple[str, ...]

    @property
    def can_open_new_positions(self) -> bool:
        return not (self.safe_mode or self.kill_switch or self.stale_data_lock or self.disconnect_lock)


class SafetyController:
    """Central safe-mode / kill-switch controller.

    The controller now persists state to a small runtime file so safety locks
    survive process restarts. Later phases can add richer release protocol and
    incident lifecycle behavior on top of this durable baseline.
    """

    def __init__(self, state_path: Path | None = None) -> None:
        self._state_path = state_path
        self._safe_mode = False
        self._kill_switch = False
        self._stale_data_lock = False
        self._disconnect_lock = False
        self._safe_mode_reason: str | None = None
        self._kill_switch_reason: str | None = None
        self._stale_data_reason: str | None = None
        self._disconnect_reason: str | None = None
        self._load_state()

    def enable_safe_mode(self, reason: str) -> None:
        self._safe_mode = True
        self._safe_mode_reason = reason
        self._persist_state()

    def enable_kill_switch(self, reason: str) -> None:
        self._kill_switch = True
        self._kill_switch_reason = reason
        if not self._safe_mode:
            self._safe_mode = True
            self._safe_mode_reason = "kill-switch enabled"
        self._persist_state()

    def enable_stale_data_lock(self, reason: str) -> None:
        self._stale_data_lock = True
        self._stale_data_reason = reason
        self._persist_state()

    def clear_stale_data_lock(self) -> None:
        self._stale_data_lock = False
        self._stale_data_reason = None
        self._persist_state()

    def enable_disconnect_lock(self, reason: str) -> None:
        self._disconnect_lock = True
        self._disconnect_reason = reason
        if not self._safe_mode:
            self._safe_mode = True
            self._safe_mode_reason = "disconnect lock enabled"
        self._persist_state()

    def clear_disconnect_lock(self) -> None:
        self._disconnect_lock = False
        self._disconnect_reason = None
        if self._safe_mode and self._safe_mode_reason == "disconnect lock enabled":
            self._safe_mode = False
            self._safe_mode_reason = None
        self._persist_state()

    def clear_safe_mode(self) -> None:
        self._safe_mode = False
        self._kill_switch = False
        self._stale_data_lock = False
        self._disconnect_lock = False
        self._safe_mode_reason = None
        self._kill_switch_reason = None
        self._stale_data_reason = None
        self._disconnect_reason = None
        self._persist_state()

    def disable_kill_switch(self) -> None:
        self._kill_switch = False
        self._kill_switch_reason = None
        if self._safe_mode and self._safe_mode_reason == "kill-switch enabled":
            self._safe_mode = False
            self._safe_mode_reason = None
        self._persist_state()

    def state(self) -> SafetyState:
        reasons = tuple(
            reason
            for reason in (
                self._safe_mode_reason,
                self._kill_switch_reason,
                self._stale_data_reason,
                self._disconnect_reason,
            )
            if reason
        )
        return SafetyState(
            safe_mode=self._safe_mode,
            kill_switch=self._kill_switch,
            stale_data_lock=self._stale_data_lock,
            disconnect_lock=self._disconnect_lock,
            reasons=reasons,
        )

    def _load_state(self) -> None:
        if self._state_path is None or not self._state_path.exists():
            return
        try:
            payload = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self._safe_mode = bool(payload.get("safe_mode", False))
        self._kill_switch = bool(payload.get("kill_switch", False))
        self._stale_data_lock = bool(payload.get("stale_data_lock", False))
        self._disconnect_lock = bool(payload.get("disconnect_lock", False))
        self._safe_mode_reason = _optional_text(payload.get("safe_mode_reason"))
        self._kill_switch_reason = _optional_text(payload.get("kill_switch_reason"))
        self._stale_data_reason = _optional_text(payload.get("stale_data_reason"))
        self._disconnect_reason = _optional_text(payload.get("disconnect_reason"))

    def _persist_state(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "safe_mode": self._safe_mode,
            "kill_switch": self._kill_switch,
            "stale_data_lock": self._stale_data_lock,
            "disconnect_lock": self._disconnect_lock,
            "safe_mode_reason": self._safe_mode_reason,
            "kill_switch_reason": self._kill_switch_reason,
            "stale_data_reason": self._stale_data_reason,
            "disconnect_reason": self._disconnect_reason,
        }
        self._state_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def get_safety_controller() -> SafetyController:
    state_path = get_settings().sqlite_path.with_name("safety_state.json")
    key = str(state_path.resolve())
    controller = _SAFETY_CONTROLLERS.get(key)
    if controller is None:
        controller = SafetyController(state_path)
        _SAFETY_CONTROLLERS[key] = controller
    return controller


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


_SAFETY_CONTROLLERS: dict[str, SafetyController] = {}
