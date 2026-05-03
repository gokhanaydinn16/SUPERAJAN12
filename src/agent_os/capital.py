"""Capital budgeting helpers for the autonomous agent OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class CapitalBudget:
    strategy: str
    venue: str
    budget: float
    reserved: float = 0.0

    def allocate(self, amount: float) -> bool:
        if self.reserved + amount > self.budget:
            return False
        self.reserved += amount
        return True

    def release(self, amount: float) -> None:
        self.reserved = max(0.0, self.reserved - amount)

    @property
    def available(self) -> float:
        return self.budget - self.reserved


@dataclass(slots=True)
class CapitalLadder:
    levels: Dict[str, float] = field(default_factory=lambda: {
        "historical_replay": 0.0,
        "paper": 0.0,
        "testnet": 0.0,
        "canary_live": 0.01,
        "scaled_live": 0.05,
    })
    current_level: str = "historical_replay"

    def increase(self, target: str) -> None:
        if target not in self.levels:
            raise ValueError("Unknown ladder stage")
        self.current_level = target

    def current_ratio(self) -> float:
        return self.levels.get(self.current_level, 0.0)


class CapitalController:
    def __init__(self, allocations: Dict[str, float]):
        self._budgets = {
            key: CapitalBudget(key, venue, budget)
            for key, (venue, budget) in allocations.items()
        }
        self._ladder = CapitalLadder()
        self._max_at_risk = 0.05

    def allocate_for(self, strategy: str, amount: float) -> bool:
        budget = self._budgets.get(strategy)
        if budget is None:
            return False
        if amount > budget.budget * self._max_at_risk:
            return False
        return budget.allocate(amount)

    def release_for(self, strategy: str, amount: float) -> None:
        budget = self._budgets.get(strategy)
        if budget:
            budget.release(amount)

    def demand_ratio(self) -> float:
        total = sum(b.budget for b in self._budgets.values())
        at_risk = sum(b.reserved for b in self._budgets.values())
        return at_risk / total if total else 0.0

    def ladder(self) -> CapitalLadder:
        return self._ladder

    def adjust_max_at_risk(self, ratio: float) -> None:
        self._max_at_risk = max(0.0, min(1.0, ratio))

    def snapshot(self) -> Dict[str, float]:
        return {k: b.available for k, b in self._budgets.items()}
