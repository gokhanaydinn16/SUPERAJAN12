from __future__ import annotations

import argparse
import asyncio

from rich.console import Console
from rich.table import Table

from superajan12.agents.risk import RiskEngine
from superajan12.agents.scanner import MarketScannerAgent
from superajan12.audit import AuditLogger
from superajan12.config import get_settings
from superajan12.connectors.polymarket import PolymarketClient
from superajan12.endpoint_check import verify_polymarket_public_endpoints
from superajan12.storage import SQLiteStore

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="superajan12")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan Polymarket markets and create paper ideas")
    scan.add_argument("--limit", type=int, default=25)
    scan.add_argument("--no-save", action="store_true", help="Do not write SQLite or audit log records")

    subparsers.add_parser("init-db", help="Create or migrate the local SQLite schema")
    subparsers.add_parser("verify-endpoints", help="Verify public Polymarket endpoints used by scanner")
    subparsers.add_parser("report", help="Show latest local scan summary")
    return parser


def build_polymarket_client() -> PolymarketClient:
    settings = get_settings()
    return PolymarketClient(
        gamma_base_url=str(settings.polymarket_gamma_base_url),
        clob_base_url=str(settings.polymarket_clob_base_url),
    )


async def run_scan(limit: int, save: bool = True) -> None:
    settings = get_settings()
    client = build_polymarket_client()
    risk_engine = RiskEngine(
        max_market_risk_usdc=settings.max_market_risk_usdc,
        max_daily_loss_usdc=settings.max_daily_loss_usdc,
        min_volume_usdc=settings.min_volume_usdc,
        max_spread_bps=settings.max_spread_bps,
        min_liquidity_usdc=settings.min_liquidity_usdc,
    )
    scanner = MarketScannerAgent(polymarket=client, risk_engine=risk_engine)
    result = await scanner.scan(limit=limit)

    scan_id: int | None = None
    if save:
        store = SQLiteStore(settings.sqlite_path)
        scan_id = store.save_scan(result)
        audit = AuditLogger(settings.audit_log_path)
        audit.record("scan.completed", {"scan_id": scan_id, **result.model_dump(mode="json")})
        for score in result.scores:
            audit.record("market.scored", {"scan_id": scan_id, **score.model_dump(mode="json")})
        for idea in result.ideas:
            audit.record("paper_trade.idea", {"scan_id": scan_id, **idea.model_dump(mode="json")})
        for position in result.paper_positions:
            audit.record("paper_position.opened", {"scan_id": scan_id, **position.model_dump(mode="json")})

    table = Table(title="SuperAjan12 Polymarket Scan")
    table.add_column("Decision")
    table.add_column("Score", justify="right")
    table.add_column("Edge", justify="right")
    table.add_column("ResConf", justify="right")
    table.add_column("Spread bps", justify="right")
    table.add_column("Source")
    table.add_column("Question")
    table.add_column("Reasons")

    for score in result.scores[:limit]:
        table.add_row(
            score.decision.value,
            f"{score.score:,.1f}",
            "-" if score.edge is None else f"{score.edge:.4f}",
            "-" if score.resolution_confidence is None else f"{score.resolution_confidence:.2f}",
            "-" if score.spread_bps is None else f"{score.spread_bps:,.1f}",
            score.orderbook_source or "-",
            score.question[:80],
            "; ".join(score.reasons[:3]),
        )

    console.print(table)

    if scan_id is not None:
        console.print(f"\n[green]Saved scan_id={scan_id}[/green]")
        console.print(f"SQLite: {settings.sqlite_path}")
        console.print(f"Audit log: {settings.audit_log_path}")

    if result.ideas:
        console.print("\n[bold green]Paper trade ideas[/bold green]")
        for idea in result.ideas:
            console.print(
                f"- {idea.side} | risk={idea.risk_usdc:.2f} USDC | "
                f"price={idea.reference_price} | edge={idea.edge} | {idea.question}"
            )
    else:
        console.print("\n[yellow]Risk motoru hicbir market icin paper trade izni vermedi.[/yellow]")

    if result.paper_positions:
        console.print("\n[bold cyan]Paper positions opened[/bold cyan]")
        for position in result.paper_positions:
            console.print(
                f"- {position.side} | entry={position.entry_price:.4f} | "
                f"shares={position.size_shares:.4f} | risk={position.risk_usdc:.2f} | {position.question}"
            )


async def run_verify_endpoints() -> None:
    result = await verify_polymarket_public_endpoints(build_polymarket_client())
    table = Table(title="SuperAjan12 Endpoint Verification")
    table.add_column("Endpoint")
    table.add_column("OK")
    table.add_column("Detail")

    for check in result.checks:
        table.add_row(check.name, "yes" if check.ok else "no", check.detail)

    console.print(table)
    if not result.ok:
        raise SystemExit(1)


def init_db() -> None:
    settings = get_settings()
    SQLiteStore(settings.sqlite_path)
    console.print(f"[green]SQLite schema ready:[/green] {settings.sqlite_path}")


def report() -> None:
    settings = get_settings()
    store = SQLiteStore(settings.sqlite_path)
    summary = store.latest_scan_summary()
    if summary is None:
        console.print("[yellow]Henuz kayitli scan yok.[/yellow]")
        return
    table = Table(title="Latest SuperAjan12 Scan")
    table.add_column("Field")
    table.add_column("Value")
    for key, value in summary.items():
        table.add_row(str(key), str(value))
    console.print(table)


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "scan":
        asyncio.run(run_scan(limit=args.limit, save=not args.no_save))
    elif args.command == "init-db":
        init_db()
    elif args.command == "verify-endpoints":
        asyncio.run(run_verify_endpoints())
    elif args.command == "report":
        report()


if __name__ == "__main__":
    main()
