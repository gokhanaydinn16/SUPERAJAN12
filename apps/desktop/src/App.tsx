import { useEffect, useMemo, useState } from "react";
import { Activity, AlertTriangle, Brain, Database, Gauge, LineChart, Radar, Shield, WalletCards, Zap } from "lucide-react";
import { BackendEvent, DashboardPayload, SourceHealth, connectEventStream, getDashboard, getEvents, getSources, runScan, verifyEndpoints } from "./api";

type LogItem = { time: string; message: string };

const nav = [
  ["Command", Activity],
  ["Research", Brain],
  ["Markets", LineChart],
  ["Wallet", WalletCards],
  ["Strategy", Radar],
  ["Risk", Shield],
  ["Execution", Zap],
  ["Health", Gauge],
  ["Audit", Database],
] as const;

function fmt(value: unknown, digits = 2) {
  if (value === null || value === undefined) return "-";
  if (typeof value === "number") return Number.isFinite(value) ? value.toFixed(digits) : "-";
  return String(value);
}

function statusClass(status: string) {
  if (status === "live") return "good";
  if (status === "stale" || status === "loading") return "warn";
  if (status === "offline" || status === "error") return "bad";
  return "muted-pill";
}

function decisionClass(decision: unknown) {
  const value = String(decision || "watch");
  if (value === "approve") return "good";
  if (value === "reject") return "bad";
  return "warn";
}

function eventToLog(event: BackendEvent) {
  return `${event.type} ${JSON.stringify(event.payload)}`;
}

export default function App() {
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [sources, setSources] = useState<SourceHealth[]>([]);
  const [limit, setLimit] = useState(25);
  const [busy, setBusy] = useState(false);
  const [eventState, setEventState] = useState("connecting");
  const [logs, setLogs] = useState<LogItem[]>([{ time: new Date().toLocaleTimeString(), message: "Desktop Command Center ready" }]);

  const addLog = (message: string) => setLogs((items) => [{ time: new Date().toLocaleTimeString(), message }, ...items].slice(0, 120));

  async function refresh() {
    try {
      const [dash, sourcePayload, events] = await Promise.all([getDashboard(), getSources(), getEvents(20)]);
      setDashboard(dash);
      setSources(sourcePayload.sources);
      if (events.events.length > 0) {
        setLogs((items) => [
          ...events.events.slice(-8).reverse().map((event) => ({ time: new Date(event.created_at).toLocaleTimeString(), message: eventToLog(event) })),
          ...items,
        ].slice(0, 120));
      }
    } catch (error) {
      addLog(`Backend unavailable: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async function startScan() {
    setBusy(true);
    addLog(`Scan started limit=${limit}`);
    try {
      const result = await runScan(limit);
      addLog(`Scan completed ${JSON.stringify(result)}`);
      await refresh();
    } catch (error) {
      addLog(`Scan failed: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setBusy(false);
    }
  }

  async function checkEndpoints() {
    setBusy(true);
    addLog("Endpoint verification started");
    try {
      const result = await verifyEndpoints();
      addLog(`Endpoint verification ${JSON.stringify(result)}`);
      await refresh();
    } catch (error) {
      addLog(`Endpoint verification failed: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    refresh();
    const socket = connectEventStream(
      (event) => {
        setEventState("live");
        addLog(eventToLog(event));
      },
      (message) => {
        setEventState("offline");
        addLog(message);
      },
    );
    const id = window.setInterval(refresh, 15000);
    return () => {
      socket.close();
      window.clearInterval(id);
    };
  }, []);

  const aggregate = dashboard?.aggregate || {};
  const shadow = dashboard?.shadow || {};
  const topMarkets = dashboard?.top_markets || [];
  const onlineSources = useMemo(() => sources.filter((source) => source.status === "live").length, [sources]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">SA</div>
          <div>
            <div className="brand-title">SuperAjan12</div>
            <div className="brand-subtitle">Desktop Command Center</div>
          </div>
        </div>
        <nav>
          {nav.map(([label, Icon], index) => (
            <button key={label} className={index === 0 ? "nav-item active" : "nav-item"}>
              <Icon size={17} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>Autonomous Research + Paper/Shadow Operations</h1>
            <p>Gerçek kaynak bağlıysa canlı veri; kaynak yoksa açıkça not configured/offline. Canlı emir kapalı.</p>
          </div>
          <div className="top-actions">
            <span className="pill warn">Live Orders Disabled</span>
            <span className="pill good">Mode {dashboard?.mode || "paper"}</span>
            <span className="pill muted-pill">Sources {onlineSources}/{sources.length || 9}</span>
            <span className={`pill ${eventState === "live" ? "good" : eventState === "connecting" ? "warn" : "bad"}`}>Events {eventState}</span>
          </div>
        </header>

        <section className="kpi-grid">
          <Kpi title="Scan Count" value={fmt(aggregate.scan_count, 0)} tone="blue" />
          <Kpi title="Approved" value={fmt(aggregate.approved_count, 0)} tone="green" />
          <Kpi title="Risk Blocks" value={fmt(aggregate.rejected_count, 0)} tone="red" />
          <Kpi title="Paper Positions" value={fmt(aggregate.paper_position_count, 0)} tone="yellow" />
          <Kpi title="Shadow PnL" value={fmt(shadow.total_unrealized_pnl_usdc, 2)} tone="green" />
          <Kpi title="Win Rate" value={shadow.win_rate === null || shadow.win_rate === undefined ? "-" : `${(Number(shadow.win_rate) * 100).toFixed(1)}%`} tone="blue" />
        </section>

        <section className="control-card">
          <div>
            <h2>Operations Control</h2>
            <p>Scan, endpoint check ve source health desktop sidecar backend üzerinden çalışır.</p>
          </div>
          <div className="controls">
            <label>Limit</label>
            <input value={limit} onChange={(event) => setLimit(Number(event.target.value || 25))} />
            <button disabled={busy} onClick={startScan}>Scan Başlat</button>
            <button disabled={busy} className="secondary" onClick={checkEndpoints}>Endpoint Kontrol</button>
            <button disabled={busy} className="secondary" onClick={refresh}>Yenile</button>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel large">
            <div className="panel-head">
              <h2>Market Intelligence</h2>
              <span className="pill muted-pill">real backend data</span>
            </div>
            <table>
              <thead><tr><th>Decision</th><th>Score</th><th>Edge</th><th>Resolution</th><th>Spread</th><th>Question</th></tr></thead>
              <tbody>
                {topMarkets.length === 0 ? <tr><td colSpan={6} className="empty">No market data yet. Run a scan.</td></tr> : topMarkets.map((market, index) => (
                  <tr key={`${market.market_id}-${index}`}>
                    <td><span className={`pill ${decisionClass(market.decision)}`}>{fmt(market.decision, 0)}</span></td>
                    <td>{fmt(market.score, 1)}</td>
                    <td>{fmt(market.edge, 4)}</td>
                    <td>{fmt(market.resolution_confidence, 2)}</td>
                    <td>{fmt(market.spread_bps, 1)}</td>
                    <td>{fmt(market.question, 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="panel">
            <div className="panel-head"><h2>Source Health</h2><AlertTriangle size={18} /></div>
            <div className="source-list">
              {sources.map((source) => (
                <div className="source-row" key={source.name}>
                  <span>{source.name}</span>
                  <span className={`pill ${statusClass(source.status)}`}>{source.status}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="content-grid bottom">
          <div className="panel">
            <div className="panel-head"><h2>Research Center</h2><span className="pill muted-pill">no fake data</span></div>
            <div className="empty-box">Research sources are shown as not configured until real providers are connected. No demo headlines are displayed.</div>
          </div>
          <div className="panel">
            <div className="panel-head"><h2>Wallet Intelligence</h2><span className="pill muted-pill">provider gated</span></div>
            <div className="empty-box">Dune / Nansen / Glassnode adapters require real API access. Wallet feed remains empty until configured.</div>
          </div>
          <div className="panel large">
            <div className="panel-head"><h2>Audit / Agent Activity</h2><span className="pill good">live event stream</span></div>
            <div className="log-feed">
              {logs.map((log, index) => <div key={`${log.time}-${index}`}><b>{log.time}</b> {log.message}</div>)}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function Kpi({ title, value, tone }: { title: string; value: string; tone: string }) {
  return <div className={`kpi ${tone}`}><span>{title}</span><strong>{value}</strong></div>;
}
