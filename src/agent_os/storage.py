"""SQLite-backed audit log and dashboard query layer."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def append_event(self, event_type: str, source: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO events (event_type, source, payload, created_at) VALUES (?, ?, ?, ?)",
                (event_type, source, json.dumps(payload, default=str), utcnow().isoformat()),
            )
            self._conn.commit()

    def recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, event_type, source, payload, created_at FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "source": row["source"],
                "payload": json.loads(row["payload"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            count = self._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            latest = self._conn.execute(
                "SELECT created_at, event_type, source FROM events ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return {
            "event_count": count,
            "last_event_at": latest["created_at"] if latest else None,
            "last_event_type": latest["event_type"] if latest else None,
            "last_event_source": latest["source"] if latest else None,
        }
