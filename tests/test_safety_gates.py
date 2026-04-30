from superajan12.approval import ManualApprovalGate
from superajan12.execution_guard import ExecutionGuard
from superajan12.model_registry import ModelRegistry, ModelVersion
from superajan12.reconciliation import ReconciliationAgent
from superajan12.safety import SafetyController
from superajan12.strategy import StrategyScorer


def test_strategy_scorer_scores_positive_samples() -> None:
    score = StrategyScorer().score("baseline", [1.0, -0.5, 2.0])

    assert score.sample_count == 3
    assert score.total_pnl_usdc == 2.5
    assert score.win_rate == 2 / 3
    assert score.score > 0


def test_model_registry_only_approved_can_trade_live() -> None:
    registry = ModelRegistry()
    candidate = ModelVersion(name="probability", version="0.1.0", status="candidate")
    approved = ModelVersion(name="probability", version="0.1.1", status="approved")

    registry.validate(candidate)
    registry.validate(approved)

    assert registry.can_trade_live(candidate) is False
    assert registry.can_trade_live(approved) is True


def test_reconciliation_detects_position_mismatch() -> None:
    result = ReconciliationAgent().compare_counts(local_open_positions=2, external_open_positions=1)

    assert result.ok is False
    assert "mismatch" in result.reasons[0]


def test_manual_approval_gate_requires_approval() -> None:
    gate = ManualApprovalGate()
    ticket = gate.request("live_execution", "small capital test")

    assert gate.can_execute(ticket) is False
    approved = gate.approve(ticket, approved_by="operator")
    assert gate.can_execute(approved) is True


def test_execution_guard_blocks_without_live_mode() -> None:
    safety = SafetyController().state()
    decision = ExecutionGuard().can_execute(mode="paper", safety_state=safety)

    assert decision.allowed is False


def test_execution_guard_allows_only_when_all_gates_pass() -> None:
    gate = ManualApprovalGate()
    ticket = gate.approve(gate.request("live_execution", "controlled test"), approved_by="operator")
    safety = SafetyController().state()

    decision = ExecutionGuard(gate).can_execute(
        mode="live",
        safety_state=safety,
        approval_ticket=ticket,
        secrets_ready=True,
    )

    assert decision.allowed is True
