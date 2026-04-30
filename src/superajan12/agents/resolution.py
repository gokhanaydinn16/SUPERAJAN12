from __future__ import annotations

from datetime import datetime, timezone

from superajan12.models import Decision, Market, ResolutionCheck


class ResolutionAgent:
    """First-pass resolution clarity checker.

    Prediction markets can be dangerous when the title looks simple but the
    resolution rule is ambiguous. This agent blocks or watches markets that lack
    enough settlement clarity.
    """

    def evaluate(self, market: Market) -> ResolutionCheck:
        reasons: list[str] = []
        confidence = 0.5

        text_parts = [market.question]
        for key in ("description", "rules", "resolutionSource", "resolution_source"):
            value = market.raw.get(key)
            if isinstance(value, str) and value.strip():
                text_parts.append(value)
        combined = " ".join(text_parts).lower()

        if market.resolution_source:
            confidence += 0.25
            reasons.append("resolution source bulundu")
        else:
            reasons.append("resolution source eksik")

        clear_terms = (
            "according to",
            "official",
            "will resolve",
            "source",
            "settlement",
            "rules",
            "criteria",
        )
        if any(term in combined for term in clear_terms):
            confidence += 0.15
            reasons.append("cozum kuralina benzeyen ifade bulundu")

        ambiguous_terms = (
            "unclear",
            "subject to",
            "may resolve",
            "disputed",
            "ambiguous",
            "opinion",
            "rumor",
        )
        if any(term in combined for term in ambiguous_terms):
            confidence -= 0.25
            reasons.append("belirsizlik/manipulasyon riski ifadesi bulundu")

        if market.end_date is not None and market.end_date < datetime.now(timezone.utc):
            confidence -= 0.4
            reasons.append("market bitis tarihi gecmis gorunuyor")

        confidence = max(0.0, min(1.0, confidence))
        if confidence < 0.45:
            decision = Decision.REJECT
        elif confidence < 0.65:
            decision = Decision.WATCH
        else:
            decision = Decision.APPROVE

        return ResolutionCheck(
            decision=decision,
            confidence=confidence,
            reasons=reasons,
            source=market.resolution_source,
        )
