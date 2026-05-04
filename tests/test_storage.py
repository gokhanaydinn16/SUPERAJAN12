from datetime import datetime, timezone

from superajan12.models import Decision, MarketScore, PaperPosition, PaperTradeIdea, ScanResult
from superajan12.storage import SQLiteStore


def test_sqlite_store_saves_scan(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "superajan12.sqlite3")
    result = ScanResult(
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        limit=1,
        scores=[
            MarketScore(
                market_id="m1",
                question="Test market?",
                category="crypto",
                decision=Decision.APPROVE,
                score=123.0,
                volume_usdc=5000,
                liquidity_usdc=1000,
                spread_bps=100,
                best_bid=0.49,
                best_ask=0.51,
                bid_depth_usdc=49,
                ask_depth_usdc=51,
                orderbook_source="book",
                implied_probability=0.5,
                model_probability=0.5,
                edge=0.0,
                resolution_confidence=0.8,
                liquidity_confidence=0.9,
                manipulation_risk_score=0.1,
                news_confidence=0.8,
                suggested_paper_risk_usdc=10,
                reasons=["risk kontrolleri gecti"],
            )
        ],
        ideas=[
            PaperTradeIdea(
                market_id="m1",
                question="Test market?",
                category="crypto",
                side="YES",
                reference_price=0.5,
                risk_usdc=10,
                model_probability=0.5,
                edge=0.0,
                reasons=["risk kontrolleri gecti"],
            )
        ],
        paper_positions=[
            PaperPosition(
                market_id="m1",
                question="Test market?",
                category="crypto",
                side="YES",
                entry_price=0.5,
                size_shares=20,
                risk_usdc=10,
            )
        ],
    )

    scan_id = store.save_scan(result)

    assert scan_id == 1
    with store.connect() as conn:
        scan_count = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        score_count = conn.execute("SELECT COUNT(*) FROM market_scores").fetchone()[0]
        idea_count = conn.execute("SELECT COUNT(*) FROM paper_trade_ideas").fetchone()[0]
        position_count = conn.execute("SELECT COUNT(*) FROM paper_positions").fetchone()[0]
        summary = conn.execute(
            "SELECT paper_position_count FROM scans WHERE id = ?", (scan_id,)
        ).fetchone()[0]
        quality = conn.execute(
            """
            SELECT category, liquidity_confidence, manipulation_risk_score, news_confidence
            FROM market_scores WHERE scan_id = ?
            """,
            (scan_id,),
        ).fetchone()

    assert scan_count == 1
    assert score_count == 1
    assert idea_count == 1
    assert position_count == 1
    assert summary == 1
    assert quality == ("crypto", 0.9, 0.1, 0.8)


def test_save_model_version_updates_existing_row_without_replacing_identity(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "superajan12.sqlite3")

    first_id = store.save_model_version("probability", "1.0.0", "candidate", notes="first")
    second_id = store.save_model_version("probability", "1.0.0", "approved", notes="updated")

    assert first_id == second_id
    rows = store.list_model_versions(limit=5)
    assert len(rows) == 1
    assert rows[0]["status"] == "approved"
    assert rows[0]["notes"] == "updated"


def test_auto_shadow_mark_uses_latest_market_scores(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "superajan12.sqlite3")
    result = ScanResult(
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        limit=1,
        scores=[
            MarketScore(
                market_id="m1",
                question="Test market?",
                category="crypto",
                decision=Decision.APPROVE,
                score=50.0,
                volume_usdc=5000,
                liquidity_usdc=1000,
                spread_bps=100,
                best_bid=0.59,
                best_ask=0.61,
                bid_depth_usdc=59,
                ask_depth_usdc=61,
                orderbook_source="book",
                suggested_paper_risk_usdc=10,
                reasons=["ok"],
            )
        ],
        ideas=[],
        paper_positions=[
            PaperPosition(
                market_id="m1",
                question="Test market?",
                category="crypto",
                side="YES",
                entry_price=0.5,
                size_shares=20,
                risk_usdc=10,
            )
        ],
    )
    store.save_scan(result)

    rows = store.auto_shadow_mark_from_latest_scores()

    assert len(rows) == 1
    assert rows[0]["status"] == "marked"
    assert rows[0]["latest_price"] == 0.6
    assert rows[0]["category"] == "crypto"


def test_execution_veto_persistence_round_trip(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "superajan12.sqlite3")

    veto_id = store.record_execution_veto(
        scope="reconciliation",
        vetoes=[
            "RECON_NOT_WIRED",
            "live reconciliation is not wired to a real venue yet",
        ],
    )

    veto = store.latest_execution_veto("reconciliation")

    assert veto_id == 1
    assert veto is not None
    assert veto["scope"] == "reconciliation"
    assert veto["vetoes"] == [
        "RECON_NOT_WIRED",
        "live reconciliation is not wired to a real venue yet",
    ]
    assert veto["created_at"]
