from __future__ import annotations

from typing import Any

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from superajan12.agents.scanner import MarketScannerAgent
from superajan12.config import get_settings
from superajan12.endpoint_check import verify_polymarket_public_endpoints
from superajan12.reporting import Reporter
from superajan12.runtime import (
    build_polymarket_client,
    build_risk_engine,
    build_scan_response,
    ensure_runtime_paths,
    persist_scan_result,
)
from superajan12.storage import SQLiteStore

app = FastAPI(title="SuperAjan12", version="0.1.0")


INDEX_HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SuperAjan12</title>
  <style>
    :root {
      --bg: #090f1a;
      --panel: #111827;
      --panel2: #172033;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --green: #22c55e;
      --yellow: #f59e0b;
      --red: #ef4444;
      --blue: #38bdf8;
      --border: #263244;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #14213d 0, #090f1a 38%, #05070d 100%);
      color: var(--text);
    }
    header {
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--border);
      background: rgba(9,15,26,0.78);
      backdrop-filter: blur(14px);
      position: sticky;
      top: 0;
      z-index: 5;
    }
    h1 { margin: 0; font-size: 30px; letter-spacing: -0.04em; }
    .subtitle { margin-top: 8px; color: var(--muted); }
    main { padding: 24px 32px 48px; max-width: 1480px; margin: 0 auto; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
    .card {
      background: linear-gradient(180deg, rgba(17,24,39,0.94), rgba(10,16,28,0.94));
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 18px 45px rgba(0,0,0,0.24);
    }
    .label { color: var(--muted); font-size: 13px; }
    .value { margin-top: 8px; font-size: 28px; font-weight: 800; }
    .row { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
    button {
      border: 0;
      background: linear-gradient(135deg, #2563eb, #06b6d4);
      color: white;
      padding: 11px 15px;
      border-radius: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    button.secondary { background: #1f2937; border: 1px solid var(--border); }
    input {
      background: #0b1220;
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 12px;
      width: 90px;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 11px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
    td { font-size: 14px; }
    .section { margin-top: 18px; }
    .pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; }
    .approve { background: rgba(34,197,94,0.15); color: var(--green); }
    .watch { background: rgba(245,158,11,0.15); color: var(--yellow); }
    .reject { background: rgba(239,68,68,0.15); color: var(--red); }
    .muted { color: var(--muted); }
    .log {
      background: #050914;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      white-space: pre-wrap;
      overflow: auto;
      max-height: 280px;
      color: #cbd5e1;
    }
    @media (max-width: 1000px) { .grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 640px) { main, header { padding-left: 16px; padding-right: 16px; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>SuperAjan12</h1>
    <div class="subtitle">Paper/shadow prediction market ajan paneli · Canlı emir kapalı · Dry-run güvenli mod</div>
  </header>
  <main>
    <div class="grid">
      <div class="card"><div class="label">Scan Count</div><div class="value" id="scan_count">-</div></div>
      <div class="card"><div class="label">Approved</div><div class="value" id="approved_count">-</div></div>
      <div class="card"><div class="label">Watch</div><div class="value" id="watch_count">-</div></div>
      <div class="card"><div class="label">Paper Positions</div><div class="value" id="paper_position_count">-</div></div>
    </div>

    <div class="card section">
      <div class="row" style="justify-content: space-between;">
        <div>
          <h2 style="margin:0">Kontrol Merkezi</h2>
          <div class="muted">Market tara, endpoint kontrol et, raporu yenile. Gerçek emir gönderilmez.</div>
        </div>
        <div class="row">
          <label class="muted">Limit</label><input id="scan_limit" value="25" />
          <button onclick="runScan()">Scan Başlat</button>
          <button class="secondary" onclick="verifyEndpoints()">Endpoint Kontrol</button>
          <button class="secondary" onclick="loadDashboard()">Yenile</button>
        </div>
      </div>
    </div>

    <div class="card section">
      <h2>En Yüksek Skorlu Marketler</h2>
      <table>
        <thead><tr><th>Karar</th><th>Skor</th><th>Edge</th><th>Res. Güven</th><th>Spread</th><th>Soru</th></tr></thead>
        <tbody id="markets"><tr><td colspan="6" class="muted">Yükleniyor...</td></tr></tbody>
      </table>
    </div>

    <div class="grid section">
      <div class="card"><div class="label">Shadow Outcome</div><div class="value" id="outcome_count">-</div><div class="muted">işaretlenen pozisyon</div></div>
      <div class="card"><div class="label">Shadow PnL</div><div class="value" id="shadow_pnl">-</div><div class="muted">teorik toplam</div></div>
      <div class="card"><div class="label">Win Rate</div><div class="value" id="win_rate">-</div><div class="muted">shadow işaretlemeler</div></div>
      <div class="card"><div class="label">Live Durum</div><div class="value" style="color:var(--yellow)">Kapalı</div><div class="muted">dry-run dışında emir yok</div></div>
    </div>

    <div class="card section">
      <h2>Sistem Log</h2>
      <div class="log" id="log">Panel hazır.</div>
    </div>
  </main>
  <script>
    function fmt(x, digits=2) {
      if (x === null || x === undefined) return '-';
      if (typeof x === 'number') return x.toFixed(digits);
      return x;
    }
    function log(message) {
      const el = document.getElementById('log');
      el.textContent = `[${new Date().toLocaleTimeString()}] ${message}\n` + el.textContent;
    }
    function pill(decision) {
      const cls = decision === 'approve' ? 'approve' : decision === 'watch' ? 'watch' : 'reject';
      return `<span class="pill ${cls}">${decision || '-'}</span>`;
    }
    async function loadDashboard() {
      const res = await fetch('/api/dashboard');
      const data = await res.json();
      const a = data.aggregate || {};
      document.getElementById('scan_count').textContent = a.scan_count ?? 0;
      document.getElementById('approved_count').textContent = a.approved_count ?? 0;
      document.getElementById('watch_count').textContent = a.watch_count ?? 0;
      document.getElementById('paper_position_count').textContent = a.paper_position_count ?? 0;
      const s = data.shadow || {};
      document.getElementById('outcome_count').textContent = s.outcome_count ?? 0;
      document.getElementById('shadow_pnl').textContent = fmt(s.total_unrealized_pnl_usdc, 2);
      document.getElementById('win_rate').textContent = s.win_rate === null || s.win_rate === undefined ? '-' : `${(s.win_rate * 100).toFixed(1)}%`;
      const rows = (data.top_markets || []).map(m => `<tr>
        <td>${pill(m.decision)}</td><td>${fmt(m.score, 1)}</td><td>${fmt(m.edge, 4)}</td>
        <td>${fmt(m.resolution_confidence, 2)}</td><td>${fmt(m.spread_bps, 1)}</td><td>${m.question || '-'}</td>
      </tr>`).join('');
      document.getElementById('markets').innerHTML = rows || '<tr><td colspan="6" class="muted">Henüz kayıt yok. Scan başlat.</td></tr>';
    }
    async function runScan() {
      const limit = document.getElementById('scan_limit').value || 25;
      log(`Scan başlatıldı: limit=${limit}`);
      const res = await fetch(`/api/scan?limit=${encodeURIComponent(limit)}`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) { log(`Scan hata: ${JSON.stringify(data)}`); return; }
      log(`Scan tamamlandı. scan_id=${data.scan_id}, score=${data.score_count}, ideas=${data.idea_count}`);
      await loadDashboard();
    }
    async function verifyEndpoints() {
      log('Endpoint kontrol başlatıldı.');
      const res = await fetch('/api/verify-endpoints', { method: 'POST' });
      const data = await res.json();
      log(`Endpoint sonucu: ${JSON.stringify(data, null, 2)}`);
    }
    loadDashboard().catch(err => log(`Dashboard hata: ${err}`));
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.get("/api/dashboard")
def dashboard(top: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    settings = ensure_runtime_paths()
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


@app.post("/api/scan")
async def scan(limit: int = Query(default=25, ge=1, le=100)) -> dict[str, Any]:
    settings = ensure_runtime_paths()
    scanner = MarketScannerAgent(
        polymarket=build_polymarket_client(settings),
        risk_engine=build_risk_engine(settings),
    )
    result = await scanner.scan(limit=limit)
    scan_id = persist_scan_result(result, summary_event_type="web.scan.completed", settings=settings)
    return build_scan_response(result, scan_id)


@app.post("/api/verify-endpoints")
async def verify_endpoints() -> dict[str, Any]:
    result = await verify_polymarket_public_endpoints(build_polymarket_client())
    return {"ok": result.ok, "checks": [check.model_dump() for check in result.checks]}


def main() -> None:
    ensure_runtime_paths(get_settings())
    uvicorn.run("superajan12.web:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
