from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalLimitDecision:
    allowed: bool
    reasons: tuple[str, ...]
    requested_risk_usdc: float
    max_allowed_risk_usdc: float


class CapitalLimitEngine:
    """Hard capital limits for controlled live testing.

    This layer is intentionally independent from strategy logic. Even if every
    strategy gate approves an idea, capital limits can still block it.
    """

    def __init__(
        self,
        max_single_trade_usdc: float,
        max_total_open_risk_usdc: float,
        max_daily_loss_usdc: float,
    ) -> None:
        self.max_single_trade_usdc = max_single_trade_usdc
        self.max_total_open_risk_usdc = max_total_open_risk_usdc
        self.max_daily_loss_usdc = max_daily_loss_usdc

    def check(
        self,
        requested_risk_usdc: float,
        current_open_risk_usdc: float,
        current_daily_pnl_usdc: float,
    ) -> CapitalLimitDecision:
        reasons: list[str] = []

        if requested_risk_usdc <= 0:
            reasons.append("requested risk must be positive")

        if requested_risk_usdc > self.max_single_trade_usdc:
            reasons.append("requested risk exceeds single-trade limit")

        if current_open_risk_usdc + requested_risk_usdc > self.max_total_open_risk_usdc:
            reasons.append("requested risk exceeds total open-risk limit")

        if current_daily_pnl_usdc <= -abs(self.max_daily_loss_usdc):
            reasons.append("daily loss limit reached")

        return CapitalLimitDecision(
            allowed=not reasons,
            reasons=tuple(reasons or ["capital limits passed"]),
            requested_risk_usdc=requested_risk_usdc,
            max_allowed_risk_usdc=min(
                self.max_single_trade_usdc,
                max(0.0, self.max_total_open_risk_usdc - current_open_risk_usdc),
            ),
        )
