from __future__ import annotations

from superajan12.models import Decision, LiquidityCheck, Market, OrderBookSnapshot


class LiquidityAgent:
    def __init__(self, min_depth_usdc: float = 100.0, max_spread_bps: float = 1200.0) -> None:
        self.min_depth_usdc = min_depth_usdc
        self.max_spread_bps = max_spread_bps

    def evaluate(self, market: Market, order_book: OrderBookSnapshot | None) -> LiquidityCheck:
        if order_book is None:
            return LiquidityCheck(
                decision=Decision.REJECT,
                confidence=0.0,
                spread_bps=None,
                bid_depth_usdc=0.0,
                ask_depth_usdc=0.0,
                reasons=["orderbook yok; likidite olculemedi"],
            )

        reasons: list[str] = []
        spread_bps = order_book.spread_bps
        bid_depth = order_book.bid_depth_usdc
        ask_depth = order_book.ask_depth_usdc
        confidence = 0.5

        if spread_bps is None:
            confidence -= 0.3
            reasons.append("spread hesaplanamadi")
        elif spread_bps > self.max_spread_bps:
            confidence -= 0.35
            reasons.append(f"spread genis: {spread_bps:.1f} bps")
        else:
            confidence += 0.2
            reasons.append("spread kabul edilebilir")

        if market.liquidity_usdc >= self.min_depth_usdc:
            confidence += 0.15
            reasons.append("market likiditesi yeterli")
        else:
            confidence -= 0.25
            reasons.append("market likiditesi dusuk")

        if bid_depth == 0.0 and ask_depth == 0.0 and order_book.source != "midpoint_spread_fallback":
            confidence -= 0.25
            reasons.append("orderbook derinligi sifir")
        elif order_book.source == "midpoint_spread_fallback":
            confidence -= 0.15
            reasons.append("fallback kullanildi; derinlik guveni dusuk")
        else:
            confidence += 0.1
            reasons.append("orderbook derinligi var")

        confidence = max(0.0, min(1.0, confidence))
        if confidence < 0.35:
            decision = Decision.REJECT
        elif confidence < 0.6:
            decision = Decision.WATCH
        else:
            decision = Decision.APPROVE

        return LiquidityCheck(
            decision=decision,
            confidence=confidence,
            spread_bps=spread_bps,
            bid_depth_usdc=bid_depth,
            ask_depth_usdc=ask_depth,
            reasons=reasons,
        )
