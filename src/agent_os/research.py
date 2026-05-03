"""Research layer that turns external context into structured suggestions."""

from __future__ import annotations

from statistics import mean
from typing import Iterable, List

from .domain import DecisionAction, DecisionSuggestion, MarketSnapshot, ResearchSignal


class ResearchAgent:
    """Advisory-only research agent.

    It never places orders directly. It only creates schema-valid suggestions that the
    deterministic risk and execution core can accept or reject.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.history: List[DecisionSuggestion] = []

    def build_suggestion(
        self,
        market: MarketSnapshot,
        signals: Iterable[ResearchSignal],
    ) -> DecisionSuggestion:
        signal_list = list(signals)
        if not signal_list:
            signal_list = default_signals()
        severity = mean(signal.severity for signal in signal_list)
        action = self._pick_action(severity)
        confidence = round(max(0.15, min(0.95, 1 - abs(0.5 - severity))), 2)
        target_size = round(0.15 + (confidence * 0.35), 4)
        rationale = (
            f"{self.name} saw average severity {severity:.2f} across "
            f"{len(signal_list)} advisory signals."
        )
        suggestion = DecisionSuggestion(
            symbol=market.symbol,
            venue=market.venue,
            action=action,
            confidence=confidence,
            rationale=rationale,
            target_size=target_size,
            reference_price=market.mid_price,
            signals=signal_list,
        )
        self.history.append(suggestion)
        return suggestion

    @staticmethod
    def _pick_action(severity: float) -> DecisionAction:
        if severity >= 0.78:
            return DecisionAction.HALT
        if severity >= 0.58:
            return DecisionAction.DECREASE
        if severity <= 0.32:
            return DecisionAction.INCREASE
        return DecisionAction.NEUTRAL


def default_signals() -> List[ResearchSignal]:
    return [
        ResearchSignal("news", "Macro headlines remain mixed.", 0.45),
        ResearchSignal("social", "Social chatter is elevated but not panicked.", 0.55),
        ResearchSignal("onchain", "Exchange inflows are slightly elevated.", 0.62),
        ResearchSignal("regime", "Volatility regime remains tradable.", 0.40),
    ]
