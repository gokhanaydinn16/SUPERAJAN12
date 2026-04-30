from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from superajan12.models import MarketScore, PaperTradeIdea, ScanResult


class SQLiteStore:
    """Small durable store for local paper/shadow mode.

    This is intentionally simple for phase 1. It gives us persistence and audit
    ability without introducing Postgres or a queue before the scanner is stable.
    """

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
                    idea_count INTEGER NOT NULL
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
                    orderbook_source TEXT,
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
                    created_at TEXT NOT NULL,
                    reasons_json TEXT NOT NULL
                );
                """
            )

    def save_scan(self, result: ScanResult) -> int:
        approved = sum(1 for item in result.scores if item.decision.value == "approve")
        rejected = sum(1 for item in result.scores if item.decision.value == "reject")
        watch = sum(1 for item in result.scores if item.decision.value == "watch")

        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO scans (
                    started_at, finished_at, requested_limit,
                    approved_count, rejected_count, watch_count, idea_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.started_at.isoformat(),
                    result.finished_at.isoformat(),
                    result.limit,
                    approved,
                    rejected,
                    watch,
                    len(result.ideas),
                ),
            )
            scan_id = int(cursor.lastrowid)
            self._insert_scores(conn, scan_id, result.scores)
            self._insert_ideas(conn, scan_id, result.ideas)
            return scan_id

    def _insert_scores(self, conn: sqlite3.Connection, scan_id: int, scores: Iterable[MarketScore]) -> None:
        conn.executemany(
            """
            INSERT INTO market_scores (
                scan_id, market_id, question, decision, score, volume_usdc,
                liquidity_usdc, spread_bps, best_bid, best_ask, orderbook_source,
                suggested_paper_risk_usdc, reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    score.orderbook_source,
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
                risk_usdc, created_at, reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    scan_id,
                    idea.market_id,
                    idea.question,
                    idea.side,
                    idea.reference_price,
                    idea.risk_usdc,
                    idea.created_at.isoformat(),
                    json.dumps(idea.reasons, ensure_ascii=False),
                )
                for idea in ideas
            ],
        )
