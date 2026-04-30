from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyScore:
    strategy_name: str
    sample_count: int
    total_pnl_usdc: float
    win_rate: float | None
    avg_pnl_usdc: float | None
    score: float


class StrategyScorer:
    """Scores strategy quality from shadow/paper outcomes.

    This is intentionally simple. Later versions can account for drawdown,
    volatility, market category, time decay and resolution quality.
    """

    def score(self, strategy_name: str, pnl_values: list[float]) -> StrategyScore:
        sample_count = len(pnl_values)
        if sample_count == 0:
            return StrategyScore(
                strategy_name=strategy_name,
                sample_count=0,
                total_pnl_usdc=0.0,
                win_rate=None,
                avg_pnl_usdc=None,
                score=0.0,
            )

        total = sum(pnl_values)
        wins = sum(1 for value in pnl_values if value > 0)
        win_rate = wins / sample_count
        avg = total / sample_count
        # Conservative score: profit matters, but win-rate and sample size gate confidence.
        confidence = min(1.0, sample_count / 50)
        score = (avg * 0.7 + win_rate * 0.3) * confidence
        return StrategyScore(
            strategy_name=strategy_name,
            sample_count=sample_count,
            total_pnl_usdc=total,
            win_rate=win_rate,
            avg_pnl_usdc=avg,
            score=score,
        )
