from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.agent_os.storage import Storage


class StorageTests(unittest.TestCase):
    def test_append_and_read_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "events.sqlite3")
            storage.append_event("test", "suite", {"ok": True})
            events = storage.recent_events()
            self.assertEqual(events[0]["event_type"], "test")


if __name__ == "__main__":
    unittest.main()
