import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client.js";
import AssetInventory from "./components/AssetInventory.jsx";
import ADActionLog from "./components/ADActionLog.jsx";
import DataImporter from "./components/DataImporter.jsx";
import Home from "./components/Home.jsx";
import PatchComplianceDashboard from "./components/PatchComplianceDashboard.jsx";
import RecordsTable from "./components/RecordsTable.jsx";
import VulnerabilityTracker from "./components/VulnerabilityTracker.jsx";

const navigation = [
  ["overview", "Overview", "⌂"],
  ["assets", "Asset inventory", "▦"],
  ["patches", "Patch management", "↻"],
  ["vulnerabilities", "Vulnerabilities", "◉"],
  ["ad", "Active Directory", "⌘"],
  ["vms", "Virtualization", "▧"],
  ["backups", "Backup validation", "◷"],
  ["imports", "Data imports", "⇧"],
];

const initialData = { overview: null, trend: [], assets: [], patches: [], vulnerabilities: [], ad: null, adActions: [], vms: [], vmAlerts: { alert_count: 0, vms: [] }, backups: [], recoveryReadiness: { average_score: 0, systems: [] } };

export default function App() {
  const [active, setActive] = useState("overview");
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [overview, trend, assets, patches, vulnerabilities, ad, adActions, vms, vmAlerts, backups, recoveryReadiness] = await Promise.all([
        api.overview(), api.trend(), api.assets(), api.patches(), api.vulnerabilities(), api.adHealth(), api.adActions(), api.vms(), api.vmAlerts(), api.backups(), api.recoveryReadiness(),
      ]);
      setData({ overview, trend, assets, patches, vulnerabilities, ad, adActions, vms, vmAlerts, backups, recoveryReadiness });
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load, refreshKey]);

  async function verifyVulnerability(id) {
    try {
      await api.verifyVulnerability(id);
      setRefreshKey((key) => key + 1);
    } catch (actionError) {
      setError(actionError.message);
    }
  }

  const title = navigation.find(([key]) => key === active)?.[1] || "Overview";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); setActive("overview"); }}>
          <span className="brand-mark">P</span><span><b>PatchGuard</b><small>RecoveryHub</small></span>
        </a>
        <div className="nav-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navigation.map(([key, label, icon]) => <button key={key} className={`nav-link ${active === key ? "active" : ""}`} onClick={() => setActive(key)}><span className="nav-icon">{icon}</span>{label}</button>)}
        </nav>
        <div className="sidebar-footer"><span className="environment-dot" /> Demo environment <small>Imported / sample data</small></div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>RecoveryHub</span><b>/</b><strong>{title}</strong></div>
          <div className="top-actions"><span className="system-status"><i /> {error ? "Connection issue" : data.overview ? "API connected" : "Connecting"}</span><button className="button button-quiet" onClick={() => setRefreshKey((key) => key + 1)}>↻ <span>Refresh</span></button><span className="avatar">OP</span></div>
        </header>
        <div className="page-content">
          {error && <div className="error-banner" role="alert"><b>Unable to load project data:</b> {error} <button onClick={() => setRefreshKey((key) => key + 1)}>Retry</button></div>}
          {loading && !data.overview ? <div className="loading-state"><span className="spinner" /> Loading compliance data…</div> : !data.overview ? <section className="panel setup-panel"><h1>RecoveryHub API unavailable</h1><p>Start the backend service, then retry. The API should be reachable at the frontend origin or through the Vite proxy.</p><button className="button button-primary" onClick={() => setRefreshKey((key) => key + 1)}>Try again</button></section> : <>
            {active === "overview" && <Home overview={data.overview} trend={data.trend} vmAlerts={data.vmAlerts} />}
            {active === "assets" && <section className="panel table-panel"><AssetInventory assets={data.assets} /></section>}
            {active === "patches" && <PatchComplianceDashboard overview={data.overview} patches={data.patches} />}
            {active === "vulnerabilities" && <VulnerabilityTracker overview={data.overview} vulnerabilities={data.vulnerabilities} onVerify={verifyVulnerability} />}
            {active === "ad" && <div className="ad-page"><section className="panel table-panel"><div className="ad-summary"><span className={`health-indicator ${data.ad.status === "healthy" ? "" : "needs-attention"}`} />{data.ad.open_issues} open health findings · {data.ad.replication_errors} replication errors · {data.ad.locked_accounts} locked accounts · {data.ad.stale_objects} stale objects</div><RecordsTable type="ad" rows={data.ad.issues} /></section><ADActionLog actions={data.adActions} onRecorded={load} /></div>}
            {active === "vms" && <section className="panel table-panel"><div className="ad-summary"><span className="health-indicator needs-attention" />{data.vmAlerts.alert_count} health alerts across {data.vmAlerts.vms.length} virtual machine(s)</div><RecordsTable type="vms" rows={data.vms.map((vm) => ({ ...vm, health_alerts: data.vmAlerts.vms.find((item) => item.vm_name === vm.vm_name)?.alerts.join(", ") || "None" }))} /></section>}
            {active === "backups" && <section className="panel table-panel"><div className="backup-summary">{["Gold", "Silver", "Bronze"].map((tier) => <div key={tier}><span>{tier} SLA</span><b>{data.overview.backups.sla_compliance[tier]}%</b><small>on-time status</small></div>)}<div><span>Recovery readiness</span><b>{data.recoveryReadiness.average_score}%</b><small>SLA + restore test recency</small></div></div><RecordsTable type="backups" rows={data.backups.map((backup) => ({ ...backup, ...data.recoveryReadiness.systems.find((item) => item.protected_system === backup.protected_system) }))} /></section>}
            {active === "imports" && <section className="panel import-panel"><div className="panel-heading"><div><p className="eyebrow">INGEST REPORTS</p><h2>Import infrastructure data</h2></div></div><p className="import-intro">Upload exports from WSUS, vulnerability scanners, Active Directory checks, vCenter, or backup reporting. Column names should match the API field names shown in the sample CSVs.</p><DataImporter onImported={() => { setRefreshKey((key) => key + 1); return Promise.resolve(); }} /><div className="import-note"><b>Data handling</b><p>Uploads are validated and committed as a single batch. Existing records are retained; imported rows are appended.</p></div></section>}
          </>}
          <footer className="page-footer"><span>PatchGuard RecoveryHub</span><span>Infrastructure compliance · Demo data</span></footer>
        </div>
      </main>
    </div>
  );
}
