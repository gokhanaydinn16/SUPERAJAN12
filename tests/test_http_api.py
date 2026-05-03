from __future__ import annotations

import json
import threading
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from src.agent_os.app import AgentOS
from src.agent_os.http_api import ApiServices, start_api_server


class HttpApiTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        app = AgentOS.bootstrap()
        services = ApiServices(app, app, app, app, app, app, app, app, app, Path("web"))
        server = start_api_server("127.0.0.1", 18080, services)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.1)
        try:
            with urlopen("http://127.0.0.1:18080/api/health") as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertIn("system", payload)
            req = Request(
                "http://127.0.0.1:18080/api/seed-cycle",
                data=b"{}",
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urlopen(req) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertIn("status", payload)
            promote = Request(
                "http://127.0.0.1:18080/api/promote-stage",
                data=json.dumps({"target": "paper", "checks": {"risk_policy": True, "readiness": False}}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            try:
                urlopen(promote)
                self.fail("promotion with failed checks should not succeed")
            except Exception:
                pass
            select_venue = Request(
                "http://127.0.0.1:18080/api/select-venue",
                data=json.dumps({"venue": "Coinbase Advanced Trade"}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urlopen(select_venue) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(payload["selected_venue"], "Coinbase Advanced Trade")
            reconcile = Request(
                "http://127.0.0.1:18080/api/reconcile",
                data=b"{}",
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urlopen(reconcile) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertIn("reports", payload)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
