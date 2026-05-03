"""Environment stage model and rollout gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Stage(Enum):
    historical_replay = "historical_replay"
    paper = "paper"
    demo = "demo"
    testnet = "testnet"
    canary_live = "canary_live"
    scaled_live = "scaled_live"


@dataclass(slots=True)
class StageTransition:
    from_stage: Stage
    to_stage: Stage
    checks: Dict[str, bool]

    def healthy(self) -> bool:
        return all(self.checks.values())


@dataclass(slots=True)
class StageGate:
    stages: List[Stage] = field(default_factory=lambda: list(Stage))
    current_stage: Stage = Stage.historical_replay
    history: List[Stage] = field(default_factory=lambda: [Stage.historical_replay])

    def _stage_index(self, stage: Stage) -> int:
        return self.stages.index(stage)

    def can_transition(self, target: Stage) -> bool:
        return self._stage_index(target) == self._stage_index(self.current_stage) + 1

    def request_transition(self, transition: StageTransition) -> None:
        if transition.from_stage != self.current_stage:
            raise ValueError("transition must start from the current stage")
        if not self.can_transition(transition.to_stage):
            raise ValueError("only the next stage in the sequence can be requested")
        if not transition.healthy():
            raise RuntimeError("pre-flight checks failed; cannot progress")
        self.current_stage = transition.to_stage
        self.history.append(transition.to_stage)

    def rollback(self, target: Stage) -> None:
        if target not in self.history:
            raise ValueError("cannot roll back to a stage that was never reached")
        self.current_stage = target
        self.history.append(target)

    def snapshot(self) -> Dict[str, str]:
        return {
            "current_stage": self.current_stage.value,
            "history": ",".join(stage.value for stage in self.history),
        }
