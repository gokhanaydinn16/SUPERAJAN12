from __future__ import annotations

from dataclasses import dataclass

from superajan12.execution_guard import ExecutionDecision


@dataclass(frozen=True)
class PreparedOrder:
    market_id: str
    side: str
    price: float
    size: float
    dry_run: bool


class LiveExecutionConnector:
    """Live connector scaffold.

    This class deliberately does not send orders. It only prepares an order shape
    after the execution guard has approved all gates. A real exchange adapter must
    be added later in a separate reviewed step.
    """

    def prepare_order(
        self,
        guard_decision: ExecutionDecision,
        market_id: str,
        side: str,
        price: float,
        size: float,
    ) -> PreparedOrder:
        if not guard_decision.allowed:
            raise RuntimeError("execution guard blocked order preparation")
        if price <= 0 or price >= 1:
            raise ValueError("prediction market price must be between 0 and 1")
        if size <= 0:
            raise ValueError("order size must be positive")
        return PreparedOrder(market_id=market_id, side=side, price=price, size=size, dry_run=True)
