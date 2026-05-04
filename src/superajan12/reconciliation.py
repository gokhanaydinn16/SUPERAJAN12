from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationResult:
    ok: bool
    reasons: tuple[str, ...]


class ReconciliationAgent:
    """Compares local state with external state.

    Phase 1/2 only handles paper state. Live exchange reconciliation will be
    added only after execution is gated by secrets, approval and kill-switch.
    """

    def compare_counts(self, local_open_positions: int, external_open_positions: int) -> ReconciliationResult:
        if local_open_positions != external_open_positions:
            return ReconciliationResult(
                ok=False,
                reasons=(
                    f"position count mismatch: local={local_open_positions}, external={external_open_positions}",
                ),
            )
        return ReconciliationResult(ok=True, reasons=("position counts match",))

    def blocking_placeholder(self) -> ReconciliationResult:
        return ReconciliationResult(
            ok=False,
            reasons=(
                "live reconciliation is not wired to a real venue yet",
                "blocking live readiness until external positions and orders are checked",
            ),
        )
