import { useMemo } from "react";
import ComplianceOverview from "./ComplianceOverview.jsx";
import ComplianceTrend from "./ComplianceTrend.jsx";

function Kpi({ label, value, detail, tone = "" }) {
  return <article className="kpi-card"><div className="kpi-top"><span>{label}</span><span className={`kpi-dot ${tone}`} /></div><strong>{value}</strong><p>{detail}</p></article>;
}

export default function Home({ overview, trend, vmAlerts }) {
  const latestTrend = useMemo(() => trend, [trend]);
  return (
    <div className="dashboard-grid">
      <section className="welcome">
        <div><p className="eyebrow">INFRASTRUCTURE POSTURE</p><h1>Operations overview</h1><p>Patch, risk, identity, virtualization, and recovery at a glance.</p></div>
        <div className={`score-ring ${overview.overall_score < 70 ? "score-warning" : ""}`}><strong>{overview.overall_score}%</strong><span>overall score</span></div>
      </section>
      <div className="kpi-grid">
        <Kpi label="Critical vulnerabilities" value={overview.open_critical_vulnerabilities} detail={`${overview.open_vulnerabilities} open · ${overview.average_remediation_cycle_days ?? "—"}d avg. cycle`} tone="red" />
        <Kpi label="Patch compliance" value={`${overview.patches.compliance_percent}%`} detail={`${overview.patches.critical_needed} critical/security updates needed`} tone="amber" />
        <Kpi label="Backup success" value={`${overview.backups.success_rate}%`} detail={`${overview.backups.failed_jobs} failed or partial jobs`} tone="green" />
        <Kpi label="Servers / virtual machines" value={`${overview.assets_total} / ${overview.vms_total}`} detail={`${overview.servers_needing_reboot} server(s) need reboot`} />
      </div>
      <div className="content-two-col">
        <ComplianceOverview overview={overview} />
        <section className="panel attention-panel">
          <div className="panel-heading"><div><p className="eyebrow">ACTION REQUIRED</p><h2>Attention queue</h2></div></div>
          <div className="attention-list">
            <div><span className="attention-icon red">!</span><span><b>{overview.open_critical_vulnerabilities} critical vulnerability findings</b><small>Prioritize remediation and verification</small></span></div>
            <div><span className="attention-icon amber">↻</span><span><b>{overview.patches.failed_installations} failed patch installations</b><small>{overview.servers_needing_reboot} system(s) awaiting restart</small></span></div>
            <div><span className="attention-icon blue">◈</span><span><b>{vmAlerts.alert_count} VM health alerts</b><small>Snapshot age, datastore, tools, and resource signals</small></span></div>
            <div><span className="attention-icon green">✓</span><span><b>{overview.backups.restore_test_coverage}% restore-test coverage</b><small>Keep recovery evidence current</small></span></div>
          </div>
        </section>
      </div>
      <div className="content-two-col bottom-grid">
        <ComplianceTrend data={latestTrend} />
        <section className="panel risk-panel">
          <div className="panel-heading"><div><p className="eyebrow">CONCENTRATED EXPOSURE</p><h2>High-risk systems</h2></div></div>
          {overview.high_risk_systems.length ? <div className="risk-list">{overview.high_risk_systems.map((item) => <div key={item.hostname}><span>{item.hostname}</span><b>{item.compliance_failures} failures</b></div>)}</div> : <p className="empty-note">No system currently meets the high-risk threshold.</p>}
          <div className="mini-stat"><span>Overdue remediations</span><b className={overview.overdue_remediations ? "text-red" : ""}>{overview.overdue_remediations}</b></div>
        </section>
      </div>
    </div>
  );
}
