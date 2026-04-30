from datetime import datetime, timezone

from superajan12.models import ShadowOutcome
from superajan12.storage import SQLiteStore
from superajan12.strategy import StrategyScorer


def test_storage_saves_strategy_score_and_lists_models(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "superajan12.sqlite3")
    score = StrategyScorer().score("baseline", [1.0, -0.5, 0.25])

    score_id = store.save_strategy_score(score)
    model_id = store.save_model_version("probability", "0.1.0", "candidate", "baseline")

    assert score_id == 1
    assert model_id == 1
    assert len(store.list_strategy_scores()) == 1
    assert len(store.list_model_versions()) == 1


def test_storage_shadow_summary(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "superajan12.sqlite3")
    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO scans (
                started_at, finished_at, requested_limit, approved_count,
                rejected_count, watch_count, idea_count, paper_position_count
            ) VALUES (?, ?, 1, 1, 0, 0, 1, 1)
            """,
            (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
        )
        conn.execute(
            """
            INSERT INTO paper_positions (
                scan_id, market_id, question, side, entry_price, size_shares,
                risk_usdc, opened_at, status
            ) VALUES (1, 'm1', 'Test?', 'YES', 0.4, 25, 10, ?, 'open')
            """,
            (datetime.now(timezone.utc).isoformat(),),
        )

    store.save_shadow_outcome(
        1,
        ShadowOutcome(
            market_id="m1",
            reference_price=0.4,
            latest_price=0.5,
            unrealized_pnl_usdc=2.5,
            status="marked",
            reasons=["test"],
        ),
    )

    summary = store.shadow_summary()

    assert summary["outcome_count"] == 1
    assert summary["total_unrealized_pnl_usdc"] == 2.5
    assert summary["win_rate"] == 1.0
