from __future__ import annotations

from superajan12.models import Decision, Market, NewsReliability


class NewsReliabilityAgent:
    def evaluate(self, market: Market) -> NewsReliability:
        text_parts = [market.question]
        for key in ("description", "rules", "resolutionSource", "resolution_source"):
            value = market.raw.get(key)
            if isinstance(value, str):
                text_parts.append(value)
        text = " ".join(text_parts).lower()

        confidence = 0.5
        reasons: list[str] = []

        strong_terms = (
            "official",
            "according to",
            "government",
            "exchange",
            "court",
            "sec",
            "fed",
            "final result",
            "certified",
        )
        weak_terms = (
            "rumor",
            "unconfirmed",
            "leak",
            "anonymous",
            "may",
            "could",
            "speculation",
        )

        if any(term in text for term in strong_terms):
            confidence += 0.25
            reasons.append("guclu/resmi kaynak ifadesi bulundu")

        if any(term in text for term in weak_terms):
            confidence -= 0.25
            reasons.append("zayif veya belirsiz kaynak ifadesi bulundu")

        if market.resolution_source:
            confidence += 0.15
            reasons.append("resolution source var")

        confidence = max(0.0, min(1.0, confidence))
        if confidence < 0.35:
            decision = Decision.REJECT
        elif confidence < 0.6:
            decision = Decision.WATCH
        else:
            decision = Decision.APPROVE

        return NewsReliability(
            decision=decision,
            confidence=confidence,
            reasons=reasons or ["kaynak guveni baseline seviyede"],
        )
