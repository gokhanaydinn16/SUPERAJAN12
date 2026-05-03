"""Application orchestration for the autonomous crypto agent OS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .adapters import BaseAdapter, get_adapter, list_adapter_capabilities
from .capital import CapitalController
from .config import AppConfig, load_config
from .domain import DecisionAction, Event, OrderIntent, OrderSide, OrderType, ResearchSignal
from .environment import Stage, StageGate, StageTransition
from .execution import ExecutionEngine
from .kill_switch import KillMode, KillSwitch, ReenableConditions
from .market_data import MarketDataValidator, PriceLevel
from .policy_watch import PolicyWatcher
from .readiness import ReadinessThresholds, ReadinessTracker
from .reconciliation import DriftSeverity, ReconciliationWorker
from .research import ResearchAgent
from .risk import RiskEngine
from .storage import Storage
from .venue_policy import REGISTRY


@dataclass(slots=True)
class AgentOS:
    config: AppConfig
    market: MarketDataValidator
    research: ResearchAgent
    risk: RiskEngine
    execution: ExecutionEngine
    storage: Storage
    stage_gate: StageGate
    readiness: ReadinessTracker
    adapter: BaseAdapter
    policy_watcher: PolicyWatcher
    capital: CapitalController
    kill_switch: KillSwitch
    reconciliation: ReconciliationWorker

    @classmethod
    def bootstrap(cls) -> "AgentOS":
        config = load_config()
        primary_venue = config.venues[0]
        market = MarketDataValidator(primary_venue.alias, config.symbol, primary_venue.stale_after_seconds)
        research = ResearchAgent("advisory-research")
        risk = RiskEngine(config.risk)
        execution = ExecutionEngine(primary_venue.alias)
        storage = Storage(config.storage.path)
        stage_gate = StageGate()
        readiness = ReadinessTracker()
        adapter = get_adapter(config.preferred_venue)
        policy_watcher = PolicyWatcher(Path(config.storage.path).with_name("venue_policies.json"))
        policy_watcher.capture(REGISTRY)
        capital = CapitalController({"core_strategy": (adapter.venue_name, 100_000.0)})
        kill_switch = KillSwitch()
        reconciliation = ReconciliationWorker()
        return cls(
            config,
            market,
            research,
            risk,
            execution,
            storage,
            stage_gate,
            readiness,
            adapter,
            policy_watcher,
            capital,
            kill_switch,
            reconciliation,
        )

    def advance_cycle(self) -> Dict[str, Any]:
        next_sequence = self.market.state.last_sequence + 1 or 1
        bid = 102_450.0 + (next_sequence % 7) * 12
        ask = bid + 14.0
        market_snapshot = self.market.ingest(
            next_sequence,
            [PriceLevel(bid, 1.35)],
            [PriceLevel(ask, 1.10)],
        )
        self.execution.update_market(market_snapshot)
        self.risk.update_market_timestamp(market_snapshot.captured_at)
        self.storage.append_event("market_snapshot", "market", market_snapshot.to_dict())

        if next_sequence % 2:
            signals = [
                ResearchSignal("news", "Risk appetite is firm.", 0.18),
                ResearchSignal("social", "Momentum chatter is constructive.", 0.22),
                ResearchSignal("onchain", "Exchange flows remain calm.", 0.24),
                ResearchSignal("regime", f"Sequence {next_sequence} remains stable.", 0.28),
            ]
        else:
            signals = [
                ResearchSignal("news", "Leverage chatter is heating up.", 0.68),
                ResearchSignal("social", "Volatility discussion is rising.", 0.72),
                ResearchSignal("onchain", "Exchange inflows are elevated.", 0.70),
                ResearchSignal("regime", f"Sequence {next_sequence} is defensive.", 0.66),
            ]
        suggestion = self.research.build_suggestion(market_snapshot, signals)
        self.storage.append_event("decision_suggestion", "research", suggestion.to_dict())

        if suggestion.action is DecisionAction.HALT:
            toggled = self.risk.toggle_kill_switch(True)
            self.storage.append_event("kill_switch", "risk", toggled)
            self.kill_switch.engage(KillMode.HARD, "research requested halt")
            return {"status": "halted", "reason": "research requested halt", "suggestion": suggestion.to_dict()}

        if suggestion.action is DecisionAction.NEUTRAL:
            return {"status": "idle", "reason": "neutral suggestion", "suggestion": suggestion.to_dict()}

        side = OrderSide.BUY if suggestion.action is DecisionAction.INCREASE else OrderSide.SELL
        intent = OrderIntent(
            symbol=suggestion.symbol,
            venue=self.adapter.venue_name,
            side=side,
            quantity=suggestion.target_size,
            order_type=OrderType.LIMIT,
            price=suggestion.reference_price,
            leverage=2.0,
        )
        self.storage.append_event("order_intent", "orchestrator", intent.to_dict())

        policy_signal = self.policy_watcher.rollout_signal()
        self.storage.append_event("policy_signal", "policy", policy_signal)
        if not policy_signal.get("policy_fresh", False):
            self.kill_switch.global_halt("policy stale")
            self.risk.toggle_kill_switch(True)
            self.storage.append_event("kill_switch", "policy", self.kill_switch.snapshot())
            return {"status": "halted", "reason": "policy stale", "policy_signal": policy_signal}

        preview_passed = True
        if self.adapter.describe_capabilities().get("preview_support") == "true":
            preview = self.adapter.preview_order(intent)
            preview_passed = preview.get("preview_status") == "ready"
            self.storage.append_event("order_preview", "adapter", preview)

        current_stage = self.stage_gate.current_stage.value
        self.capital.ladder().increase(current_stage if current_stage in self.capital.ladder().levels else "historical_replay")
        required_capital = (intent.notional or (intent.quantity * suggestion.reference_price)) * self.capital.ladder().current_ratio()
        if not self.capital.allocate_for("core_strategy", required_capital):
            self.kill_switch.soft_halt("capital budget exceeded", self.adapter.venue_name)
            self.storage.append_event("kill_switch", "capital", self.kill_switch.snapshot())
            return {"status": "halted", "reason": "capital budget exceeded"}

        decision = self.risk.evaluate(intent)
        self.storage.append_event("risk_decision", "risk", decision.to_dict())
        if not decision.allowed:
            for breach in self.risk.make_breaches(decision):
                self.storage.append_event("risk_breach", "risk", breach.to_dict())
            self.readiness.record_cycle(
                stale="stale_market_data" in decision.breaches,
                duplicate="duplicate_intent" in decision.breaches,
                pnl_explained=0.0,
                fill_quality=0.0,
                incident=True,
                preview_passed=preview_passed,
                policy_fresh=bool(policy_signal.get("policy_fresh", False)),
            )
            self.capital.release_for("core_strategy", required_capital)
            return {"status": "rejected", "decision": decision.to_dict()}

        adapter_response = self.adapter.submit_order(intent)
        self.storage.append_event(
            "adapter_submit",
            "adapter",
            {
                "order_id": adapter_response.order_id,
                "venue": adapter_response.venue,
                "status": adapter_response.status,
                "details": adapter_response.details,
            },
        )
        order = self.execution.submit(intent)
        self.storage.append_event("order_opened", "execution", order.to_dict())
        fill = self.execution.try_fill(order.order_id)
        if fill is not None:
            self.storage.append_event("order_fill", "execution", fill.to_dict())
            position = self.risk.record_fill(intent, fill.price)
            self.storage.append_event("position_update", "risk", position.to_dict())
            fill_quality = 1.0 - min(abs(fill.price - suggestion.reference_price) / suggestion.reference_price, 1.0)
            self.readiness.record_cycle(
                stale=False,
                duplicate=False,
                pnl_explained=0.9,
                fill_quality=fill_quality,
                incident=False,
                preview_passed=preview_passed,
                policy_fresh=bool(policy_signal.get("policy_fresh", False)),
            )
        self.capital.release_for("core_strategy", required_capital)
        return {"status": "executed", "order": order.to_dict(), "fill": fill.to_dict() if fill else None}

    def get_status(self) -> Dict[str, Any]:
        ready, readiness_snapshot = self.readiness.is_ready(ReadinessThresholds())
        return {
            "system": self.config.system_name,
            "symbol": self.config.symbol,
            "market": self.market.heartbeat(),
            "risk": self.risk.summarize(),
            "storage": self.storage.summary(),
            "stage": self.stage_gate.snapshot(),
            "venues": [asdict(policy) for policy in REGISTRY],
            "adapter_capabilities": list_adapter_capabilities(),
            "policy_signal": self.policy_watcher.rollout_signal(),
            "capital": {"snapshot": self.capital.snapshot(), "demand_ratio": self.capital.demand_ratio()},
            "kill_switch_state": self.kill_switch.snapshot(),
            "readiness": {"ready_for_promotion": ready, **readiness_snapshot.as_dict()},
        }

    def snapshot(self) -> Dict[str, Any]:
        recent_events = self.storage.recent_events(30)
        fills = [event for event in recent_events if event["event_type"] == "order_fill"]
        orders = [event for event in recent_events if event["event_type"] == "order_opened"]
        suggestions = [event for event in recent_events if event["event_type"] == "decision_suggestion"]
        previews = [event for event in recent_events if event["event_type"] == "order_preview"]
        return {
            "health": self.get_status(),
            "positions": self.risk.position_view(),
            "open_orders": self.execution.open_order_view(),
            "recent_orders": orders,
            "recent_fills": fills,
            "recent_suggestions": suggestions,
            "recent_previews": previews,
            "timeline": recent_events,
        }

    def list_recent(self) -> List[Dict[str, Any]]:
        return self.storage.recent_events()

    def toggle(self, engage: bool) -> Dict[str, Any]:
        payload = self.risk.toggle_kill_switch(engage)
        self.storage.append_event("kill_switch", "operator", payload)
        return payload

    def run_reconciliation(self) -> Dict[str, object]:
        local_orders = self.execution.open_order_view()
        venue_orders = local_orders
        local_positions = {position["symbol"]: position["net_quantity"] for position in self.risk.position_view()}
        venue_positions = dict(local_positions)
        reports = self.reconciliation.detect_drift(local_orders, venue_orders, local_positions, venue_positions)
        payload = {
            "reports": [
                {
                    "severity": report.severity.value,
                    "mismatches": report.mismatches,
                    "details": report.details,
                    "mitigation": report.mitigation,
                }
                for report in reports
            ]
        }
        self.storage.append_event("reconciliation", "ops", payload)
        if any(report.severity in (DriftSeverity.HIGH, DriftSeverity.CRITICAL) for report in reports):
            self.kill_switch.hard_halt("reconciliation drift")
            self.storage.append_event("kill_switch", "ops", self.kill_switch.snapshot())
        return payload

    def select_venue(self, venue_name: str) -> Dict[str, Any]:
        self.adapter = get_adapter(venue_name)
        payload = {"selected_venue": self.adapter.venue_name}
        self.storage.append_event("venue_selected", "operator", payload)
        return payload

    def release_kill_switch(self) -> Dict[str, object]:
        state = self.kill_switch.release(ReenableConditions(policy_fresh=bool(self.policy_watcher.rollout_signal().get("policy_fresh", False))))
        self.risk.toggle_kill_switch(False)
        payload = self.kill_switch.snapshot()
        self.storage.append_event("kill_switch_release", "operator", payload)
        return payload

    def promote_stage(self, target: str, checks: Dict[str, bool] | None = None) -> Dict[str, Any]:
        target_stage = Stage(target)
        policy_signal = self.policy_watcher.rollout_signal()
        default_checks = {
            "risk_policy": True,
            "readiness": self.readiness.is_ready(ReadinessThresholds())[0],
            "policy_freshness": bool(policy_signal.get("policy_fresh", False)),
        }
        transition = StageTransition(
            from_stage=self.stage_gate.current_stage,
            to_stage=target_stage,
            checks=checks or default_checks,
        )
        self.stage_gate.request_transition(transition)
        payload = self.stage_gate.snapshot()
        self.storage.append_event("stage_promotion", "operator", payload)
        return payload


def event_from(obj: Any, kind: str, source: str) -> Event:
    payload = obj.to_dict() if hasattr(obj, "to_dict") else dict(obj)
    return Event(kind=kind, payload=payload, source=source)
