from __future__ import annotations

from superajan12.models import Decision, Market, SmartWalletSignal


class SmartWalletAgent:
    """Smart wallet signal placeholder.

    Real wallet intelligence requires Dune/Arkham/Nansen or an indexer. Until
    those sources are connected, this agent stays conservative and never creates
    positive edge by itself.
    """

    def evaluate(self, market: Market) -> SmartWalletSignal:
        text = f"{market.question} {market.category or ''}".lower()
        wallet_relevant_terms = ("token", "airdrop", "ethereum", "solana", "bitcoin", "btc", "eth", "sol")
        low_quality_terms = ("meme", "pump", "insider", "rumor")

        wallet_score = 0.0
        flow_score = 0.0
        confidence = 0.45
        reasons: list[str] = []

        if any(term in text for term in wallet_relevant_terms):
            confidence += 0.1
            reasons.append("on-chain/cuzdan verisi ileride faydali olabilir")

        if any(term in text for term in low_quality_terms):
            confidence -= 0.2
            reasons.append("dusuk kaliteli cuzdan/sosyal risk ifadesi bulundu")

        confidence = max(0.0, min(1.0, confidence))
        if confidence < 0.25:
            decision = Decision.REJECT
        elif confidence < 0.55:
            decision = Decision.WATCH
        else:
            decision = Decision.APPROVE

        return SmartWalletSignal(
            decision=decision,
            confidence=confidence,
            wallet_score=wallet_score,
            flow_score=flow_score,
            reasons=reasons or ["cuzdan verisi bagli degil; notr sinyal"],
        )
