import json
from datetime import datetime, timezone

from superajan12.config import Settings
from superajan12.models import Decision, MarketScore, PaperPosition, PaperTradeIdea, ScanResult
from superajan12.runtime import build_scan_response, persist_scan_result


def test_persist_scan_result_records_summary_and_detail_audit_events(tmp_path) -> None:
    settings = Settings(
        sqlite_path=tmp_path / "superajan12.sqlite3",
        audit_log_path=tmp_path / "audit/events.jsonl",
    )
    result = ScanResult(
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        limit=1,
        scores=[
            MarketScore(
                market_id="m1",
                question="Test market?",
                decision=Decision.APPROVE,
                score=101.0,
                volume_usdc=5000,
                liquidity_usdc=1000,
                spread_bps=90,
                best_bid=0.49,
                best_ask=0.51,
                bid_depth_usdc=49,
                ask_depth_usdc=51,
                orderbook_source="book",
                implied_probability=0.5,
                model_probability=0.55,
                edge=0.05,
                resolution_confidence=0.8,
                suggested_paper_risk_usdc=10,
                reasons=["risk ok"],
            )
        ],
        ideas=[
            PaperTradeIdea(
                market_id="m1",
                question="Test market?",
                side="YES",
                reference_price=0.5,
                risk_usdc=10,
                model_probability=0.55,
                edge=0.05,
                reasons=["risk ok"],
            )
        ],
        paper_positions=[
            PaperPosition(
                market_id="m1",
                question="Test market?",
                side="YES",
                entry_price=0.5,
                size_shares=20,
                risk_usdc=10,
            )
        ],
    )

    scan_id = persist_scan_result(result, summary_event_type="test.scan.completed", settings=settings)
    response = build_scan_response(result, scan_id)

    assert response == {
        "scan_id": 1,
        "score_count": 1,
        "idea_count": 1,
        "paper_position_count": 1,
    }

    lines = settings.audit_log_path.read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in lines]

    assert [event["event_type"] for event in events] == [
        "test.scan.completed",
        "market.scored",
        "paper_trade.idea",
        "paper_position.opened",
    ]
    assert events[0]["payload"]["scan_id"] == 1
    assert events[1]["payload"]["market_id"] == "m1"
    assert events[2]["payload"]["question"] == "Test market?"
    assert events[3]["payload"]["side"] == "YES"
