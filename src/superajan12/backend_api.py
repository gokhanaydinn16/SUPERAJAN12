from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query

from superajan12.agents.risk import RiskEngine
from superajan12.agents.scanner import MarketScannerAgent
from superajan12.audit import AuditLogger
from superajan12.config import get_settings
from superajan12.connectors.polymarket import PolymarketClient
from superajan12.endpoint_check import verify_polymarket_public_endpoints
from superajan12.health import build_default_health_registry
from superajan12.reporting import Reporter
from superajan12.storage import SQLiteStore


def create_backend_app() -> FastAPI:
    app = FastAPI(title="SuperAjan12 Backend", version="0.2.0")

    @app.get("/health")
    def health() -> dict[str, Any]:
        settings = get_settings()
        return {
            "ok": True,
            "mode": settings.mode,
            "live_trading": "disabled",
            "database": str(settings.sqlite_path),
        }

    @app.get("/sources")
    def sources() -> dict[str, Any]:
        registry = build_default_health_registry()
        return {"sources": registry.snapshot()}

    @app.get("/dashboard")
    def dashboard(top: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
        settings = get_settings()
        store = SQLiteStore(settings.sqlite_path)
        reporter = Reporter(settings.sqlite_path)
        return {
            "aggregate": reporter.aggregate_summary(),
            "latest": reporter.latest_summary(),
            "top_markets": reporter.top_scored_markets(limit=top),
            "shadow": store.shadow_summary(),
            "mode": settings.mode,
            "live_trading": "disabled",
        }

    @app.post("/scan")
    async def scan(limit: int = Query(default=25, ge=1, le=100)) -> dict[str, Any]:
        settings = get_settings()
        client = PolymarketClient(
            gamma_base_url=str(settings.polymarket_gamma_base_url),
            clob_base_url=str(settings.polymarket_clob_base_url),
        )
        risk_engine = RiskEngine(
            max_market_risk_usdc=settings.max_market_risk_usdc,
            max_daily_loss_usdc=settings.max_daily_loss_usdc,
            min_volume_usdc=settings.min_volume_usdc,
            max_spread_bps=settings.max_spread_bps,
            min_liquidity_usdc=settings.min_liquidity_usdc,
        )
        scanner = MarketScannerAgent(polymarket=client, risk_engine=risk_engine)
        result = await scanner.scan(limit=limit)
        scan_id = SQLiteStore(settings.sqlite_path).save_scan(result)
        AuditLogger(settings.audit_log_path).record(
            "backend.scan.completed",
            {"scan_id": scan_id, **result.model_dump(mode="json")},
        )
        return {
            "scan_id": scan_id,
            "score_count": len(result.scores),
            "idea_count": len(result.ideas),
            "paper_position_count": len(result.paper_positions),
        }

    @app.post("/verify-endpoints")
    async def verify_endpoints() -> dict[str, Any]:
        settings = get_settings()
        client = PolymarketClient(
            gamma_base_url=str(settings.polymarket_gamma_base_url),
            clob_base_url=str(settings.polymarket_clob_base_url),
        )
        result = await verify_polymarket_public_endpoints(client)
        return {"ok": result.ok, "checks": [check.model_dump() for check in result.checks]}

    return app


app = create_backend_app()
