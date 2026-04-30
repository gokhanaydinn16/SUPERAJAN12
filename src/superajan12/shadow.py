from __future__ import annotations

from superajan12.models import PaperPosition, ShadowOutcome


class ShadowEvaluator:
    """Evaluates paper positions against a latest observed price.

    This is not settlement accounting. It is mark-to-market shadow tracking for
    paper mode so the system can learn which decisions would have worked.
    """

    def evaluate_position(self, position: PaperPosition, latest_price: float | None) -> ShadowOutcome:
        if latest_price is None:
            return ShadowOutcome(
                market_id=position.market_id,
                reference_price=position.entry_price,
                latest_price=None,
                unrealized_pnl_usdc=None,
                status="unknown",
                reasons=["latest price missing"],
            )

        if latest_price < 0 or latest_price > 1:
            return ShadowOutcome(
                market_id=position.market_id,
                reference_price=position.entry_price,
                latest_price=latest_price,
                unrealized_pnl_usdc=None,
                status="invalid_price",
                reasons=["latest price outside prediction market range"],
            )

        if position.side.upper() == "YES":
            pnl = (latest_price - position.entry_price) * position.size_shares
        else:
            pnl = (position.entry_price - latest_price) * position.size_shares

        return ShadowOutcome(
            market_id=position.market_id,
            reference_price=position.entry_price,
            latest_price=latest_price,
            unrealized_pnl_usdc=pnl,
            status="marked",
            reasons=["mark-to-market calculated"],
        )
