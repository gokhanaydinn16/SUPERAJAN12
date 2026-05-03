"""ThreadingHTTPServer surface for the autonomous agent system."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_LOGGER = logging.getLogger("agent_os.http_api")


@dataclass
class ApiServices:
    """Minimal contract the HTTP layer expects from each subsystem."""

    health: Any  # Expected to expose `get_status() -> dict`
    dashboard: Any  # Expected to expose `snapshot() -> dict`
    events: Any  # Expected to expose `list_recent() -> list[dict]`
    kill_switch: Any  # Expected to expose `toggle(engage: bool) -> dict`
    seed_cycle: Any  # Expected to expose `advance_cycle() -> dict`
    stage_control: Any  # Expected to expose `promote_stage(target: str, checks: dict | None) -> dict`
    venue_control: Any  # Expected to expose `select_venue(venue_name: str) -> dict`
    reconciliation: Any  # Expected to expose `run_reconciliation() -> dict`
    release_control: Any  # Expected to expose `release_kill_switch() -> dict`
    static_dir: Path


class AgentHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "AgentOS/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        services = self.server.services
        if parsed.path == "/api/health":
            self._respond_json(services.health.get_status())
            return
        if parsed.path == "/api/dashboard":
            self._respond_json(services.dashboard.snapshot())
            return
        if parsed.path == "/api/events":
            self._respond_json(services.events.list_recent())
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        services = self.server.services
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length) if length else b""
        body = self._parse_json(payload)
        if parsed.path == "/api/kill-switch/toggle":
            engage = bool(body.get("engage", True))
            self._respond_json(services.kill_switch.toggle(engage))
            return
        if parsed.path == "/api/seed-cycle":
            self._respond_json(services.seed_cycle.advance_cycle())
            return
        if parsed.path == "/api/promote-stage":
            target = body.get("target")
            checks = body.get("checks")
            try:
                self._respond_json(services.stage_control.promote_stage(target, checks))
            except Exception as exc:
                self._respond_json({"error": str(exc)}, status=400)
            return
        if parsed.path == "/api/select-venue":
            venue_name = body.get("venue")
            try:
                self._respond_json(services.venue_control.select_venue(venue_name))
            except Exception as exc:
                self._respond_json({"error": str(exc)}, status=400)
            return
        if parsed.path == "/api/reconcile":
            self._respond_json(services.reconciliation.run_reconciliation())
            return
        if parsed.path == "/api/kill-switch/release":
            try:
                self._respond_json(services.release_control.release_kill_switch())
            except Exception as exc:
                self._respond_json({"error": str(exc)}, status=400)
            return
        self.send_error(404, "Unknown POST target")

    def _serve_static(self, path: str) -> None:
        services = self.server.services
        normalized = path.lstrip("/") or "index.html"
        safe_path = (services.static_dir / normalized).resolve()
        base = services.static_dir.resolve()
        if not safe_path.exists() or not safe_path.is_file() or base not in safe_path.parents and safe_path != base:
            self.send_error(404, "File not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", self._guess_content_type(safe_path.name))
        self.end_headers()
        with safe_path.open("rb") as fh:
            self.wfile.write(fh.read())

    def _respond_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _parse_json(self, payload: bytes) -> dict[str, Any]:
        if not payload:
            return {}
        try:
            return json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            _LOGGER.warning("Failed to decode JSON payload: %s", exc)
            return {}

    @staticmethod
    def _guess_content_type(name: str) -> str:
        if name.endswith(".html"):
            return "text/html; charset=utf-8"
        if name.endswith(".css"):
            return "text/css; charset=utf-8"
        if name.endswith(".js"):
            return "application/javascript"
        if name.endswith(".json"):
            return "application/json"
        return "application/octet-stream"

    def log_message(self, format: str, *args: object) -> None:
        _LOGGER.info("%s - %s", self.address_string(), format % args)


class AgentHTTPServer(ThreadingHTTPServer):
    def __init__(self, host: str, port: int, services: ApiServices) -> None:
        super().__init__((host, port), AgentHTTPRequestHandler)
        self.services = services


def start_api_server(host: str, port: int, services: ApiServices) -> AgentHTTPServer:
    """Create and return a running HTTP server; caller is responsible for `serve_forever()`."""
    server = AgentHTTPServer(host, port, services)
    _LOGGER.info("Starting HTTP API on %s:%d", host, port)
    return server


__all__ = ["ApiServices", "AgentHTTPServer", "start_api_server"]
