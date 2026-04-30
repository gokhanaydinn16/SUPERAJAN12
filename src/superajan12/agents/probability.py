from __future__ import annotations

from superajan12.models import Market, OrderBookSnapshot, ProbabilityEstimate, ResolutionCheck


class ProbabilityAgent:
    """Conservative baseline probability estimator.

    This is not yet a predictive AI model. It creates a transparent baseline so
    the system can reason about implied probability, confidence and edge before
    we plug in news/social/on-chain models.
    """

    def estimate(
        self,
        market: Market,
        order_book: OrderBookSnapshot | None,
        resolution: ResolutionCheck,
    ) -> ProbabilityEstimate:
        implied = order_book.mid if order_book else None
        reasons: list[str] = []

        if implied is None:
            return ProbabilityEstimate(
                market_id=market.id,
                implied_probability=None,
                model_probability=None,
                edge=None,
                confidence=0.0,
                reasons=["implied probability hesaplanamadi"],
            )

        # Baseline: start at market implied probability, then make tiny
        # conservative adjustments based on market quality. This prevents fake
        # overconfidence while still giving the Strategy/Risk layers a full data
        # shape to work with.
        model_probability = implied
        confidence = min(0.85, max(0.1, resolution.confidence))

        if market.volume_usdc >= 100_000:
            confidence += 0.05
            reasons.append("hacim yuksek, fiyat kesfi daha guvenilir")
        elif market.volume_usdc < 5_000:
            confidence -= 0.1
            reasons.append("hacim dusuk, model guveni azaltildi")

        if market.liquidity_usdc >= 10_000:
            confidence += 0.05
            reasons.append("likidite iyi")
        elif market.liquidity_usdc < 1_000:
            confidence -= 0.1
            reasons.append("likidite dusuk")

        # Resolution uncertainty should not create a trade edge. It reduces trust.
        if resolution.confidence < 0.65:
            confidence -= 0.2
            reasons.append("resolution guveni dusuk, edge baskilandi")

        confidence = max(0.0, min(1.0, confidence))
        edge = model_probability - implied

        return ProbabilityEstimate(
            market_id=market.id,
            implied_probability=implied,
            model_probability=model_probability,
            edge=edge,
            confidence=confidence,
            reasons=reasons or ["baseline model: piyasa olasiligi referans alindi"],
        )
