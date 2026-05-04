from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PreTradeVetoCode(str, Enum):
    SAFE_MODE = "safe_mode"
    KILL_SWITCH = "kill_switch"
    DISCONNECTED = "disconnected"
    STALE_DATA = "stale_data"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    POSITION_CAP = "position_cap"
    EXPOSURE_CAP = "exposure_cap"
    MARKET_INACTIVE = "market_inactive"
    LOW_VOLUME = "low_volume"
    LOW_LIQUIDITY = "low_liquidity"
    ORDERBOOK_UNAVAILABLE = "orderbook_unavailable"
    ORDERBOOK_INCOMPLETE = "orderbook_incomplete"
    SPREAD_UNAVAILABLE = "spread_unavailable"
    SPREAD_TOO_WIDE = "spread_too_wide"
    REFERENCE_GATE = "reference_gate"


@dataclass(frozen=True)
class PreTradeVeto:
    code: PreTradeVetoCode
    reason: str


@dataclass(frozen=True)
class RiskControlContext:
    current_daily_pnl_usdc: float = 0.0
    safe_mode: bool = False
    kill_switch_active: bool = False
    connected: bool = True
    market_data_stale: bool = False
    current_market_exposure_usdc: float = 0.0
    current_total_exposure_usdc: float = 0.0
    requested_risk_usdc: float | None = None
    max_market_exposure_usdc: float | None = None
    max_total_exposure_usdc: float | None = None
    extra_vetoes: tuple[PreTradeVeto, ...] = field(default_factory=tuple)

    @property
    def requested_risk_or_zero(self) -> float:
        if self.requested_risk_usdc is None:
            return 0.0
        return max(self.requested_risk_usdc, 0.0)


def veto_reason(code: PreTradeVetoCode, detail: str) -> str:
    return f"{code.value}: {detail}"
