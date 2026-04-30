from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from superajan12.models import MarketScore, PaperPosition, PaperTradeIdea, ScanResult


class SQLiteStore:
    """Small durable store for local paper/shadow mode."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    requested_limit INTEGER NOT NULL,
                    approved_count INTEGER NOT NULL,
                    rejected_count INTEGER NOT NULL,
                    watch_count INTEGER NOT NULL,
                    idea_count INTEGER NOT NULL,
                    paper_position_count INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS market_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    market_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    score REAL NOT NULL,
                    volume_usdc REAL NOT NULL,
                    liquidity_usdc REAL NOT NULL,
                    spread_bps REAL,
                    best_bid REAL,
                    best_ask REAL,
                    bid_depth_usdc REAL NOT NULL DEFAULT 0,
                    ask_depth_usdc REAL NOT NULL DEFAULT 0,
                    orderbook_source TEXT,
                    implied_probability REAL,
                    model_probability REAL,
                    edge REAL,
                    resolution_confidence REAL,
                    liquidity_confidence REAL,
                    manipulation_risk_score REAL,
                    news_confidence REAL,
                    social_confidence REAL,
                    smart_wallet_confidence REAL,
                    reference_confidence REAL,
                    suggested_paper_risk_usdc REAL NOT NULL,
                    reasons_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS paper_trade_ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    market_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    side TEXT NOT NULL,
                    reference_price REAL,
                    risk_usdc REAL NOT NULL,
                    model_probability REAL,
                    edge REAL,
                    created_at TEXT NOT NULL,
                    reasons_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS paper_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    market_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    size_shares REAL NOT NULL,
                    risk_usdc REAL NOT NULL,
                    opened_at TEXT NOT NULL,
                    status TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS shadow_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER NOT NULL REFERENCES paper_positions(id) ON DELETE CASCADE,
                    market_id TEXT NOT NULL,
                    reference_price REAL,
                    latest_price REAL,
                    unrealized_pnl_usdc REAL,
                    status TEXT NOT NULL,
                    reasons_json TEXT NOT NULL,
                    checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            for table, column, ddl in (
                ("scans", "paper_position_count", "INTEGER NOT NULL DEFAULT 0"),
                ("market_scores", "bid_depth_usdc", "REAL NOT NULL DEFAULT 0"),
                ("market_scores", "ask_depth_usdc", "REAL NOT NULL DEFAULT 0"),
                ("market_scores", "implied_probability", "REAL"),
                ("market_scores", "model_probability", "REAL"),
                ("market_scores", "edge", "REAL"),
                ("market_scores", "resolution_confidence", "REAL"),
                ("market_scores", "liquidity_confidence", "REAL"),
                ("market_scores", "manipulation_risk_score", "REAL"),
                ("market_scores", "news_confidence", "REAL"),
                ("market_scores", "social_confidence", "REAL"),
                ("market_scores", "smart_wallet_confidence", "REAL"),
                ("market_scores", "reference_confidence", "REAL"),
                ("paper_trade_ideas", "model_probability", "REAL"),
                ("paper_trade_ideas", "edge", "REAL"),
            ):
                self._ensure_column(conn, table, column, ddl)

    def save_scan(self, result: ScanResult) -> int:
        approved = sum(1 for item in result.scores if item.decision.value == "approve")
        rejected = sum(1 for item in result.scores if item.decision.value == "reject")
        watch = sum(1 for item in result.scores if item.decision.value == "watch")

        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO scans (
                    started_at, finished_at, requested_limit,
                    approved_count, rejected_count, watch_count, idea_count, paper_position_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.started_at.isoformat(),
                    result.finished_at.isoformat(),
                    result.limit,
                    approved,
                    rejected,
                    watch,
                    len(result.ideas),
                    len(result.paper_positions),
                ),
            )
            scan_id = int(cursor.lastrowid)
            self._insert_scores(conn, scan_id, result.scores)
            self._insert_ideas(conn, scan_id, result.ideas)
            self._insert_positions(conn, scan_id, result.paper_positions)
            return scan_id

    def latest_scan_summary(self) -> dict[str, int | float | str] | None:
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT id, started_at, finished_at, requested_limit, approved_count,
                       rejected_count, watch_count, idea_count, paper_position_count
                FROM scans
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return None if row is None else dict(row)

    def _insert_scores(self, conn: sqlite3.Connection, scan_id: int, scores: Iterable[MarketScore]) -> None:
        conn.executemany(
            """
            INSERT INTO market_scores (
                scan_id, market_id, question, decision, score, volume_usdc,
                liquidity_usdc, spread_bps, best_bid, best_ask, bid_depth_usdc,
                ask_depth_usdc, orderbook_source, implied_probability, model_probability,
                edge, resolution_confidence, liquidity_confidence, manipulation_risk_score,
                news_confidence, social_confidence, smart_wallet_confidence, reference_confidence,
                suggested_paper_risk_usdc, reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    scan_id,
                    score.market_id,
                    score.question,
                    score.decision.value,
                    score.score,
                    score.volume_usdc,
                    score.liquidity_usdc,
                    score.spread_bps,
                    score.best_bid,
                    score.best_ask,
                    score.bid_depth_usdc,
                    score.ask_depth_usdc,
                    score.orderbook_source,
                    score.implied_probability,
                    score.model_probability,
                    score.edge,
                    score.resolution_confidence,
                    score.liquidity_confidence,
                    score.manipulation_risk_score,
                    score.news_confidence,
                    score.social_confidence,
                    score.smart_wallet_confidence,
                    score.reference_confidence,
                    score.suggested_paper_risk_usdc,
                    json.dumps(score.reasons, ensure_ascii=False),
                )
                for score in scores
            ],
        )

    def _insert_ideas(self, conn: sqlite3.Connection, scan_id: int, ideas: Iterable[PaperTradeIdea]) -> None:
        conn.executemany(
            """
            INSERT INTO paper_trade_ideas (
                scan_id, market_id, question, side, reference_price,
                risk_usdc, model_probability, edge, created_at, reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    scan_id,
                    idea.market_id,
                    idea.question,
                    idea.side,
                    idea.reference_price,
                    idea.risk_usdc,
                    idea.model_probability,
                    idea.edge,
                    idea.created_at.isoformat(),
                    json.dumps(idea.reasons, ensure_ascii=False),
                )
                for idea in ideas
            ],
        )

    def _insert_positions(self, conn: sqlite3.Connection, scan_id: int, positions: Iterable[PaperPosition]) -> None:
        conn.executemany(
            """
            INSERT INTO paper_positions (
                scan_id, market_id, question, side, entry_price,
                size_shares, risk_usdc, opened_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    scan_id,
                    position.market_id,
                    position.question,
                    position.side,
                    position.entry_price,
                    position.size_shares,
                    position.risk_usdc,
                    position.opened_at.isoformat(),
                    position.status,
                )
                for position in positions
            ],
        )

    def _ensure_column(self, conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        if column not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
