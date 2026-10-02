import RecordsTable from "./RecordsTable.jsx";

export default function PatchComplianceDashboard({ overview, patches }) {
  const timeline = overview.patches.timeline || [];
  return (
    <div className="operations-page">
      <section className="panel patch-summary">
        <div className="panel-heading"><div><p className="eyebrow">WSUS DEPLOYMENT</p><h2>Patch compliance and wave schedule</h2></div><b className="patch-percent">{overview.patches.compliance_percent}% compliant</b></div>
        <div className="patch-metrics">
          <div><span>Critical/security needed</span><b>{overview.patches.critical_needed}</b></div>
          <div><span>Reboot required</span><b>{overview.patches.servers_needing_reboot}</b></div>
          <div><span>Failed installations</span><b>{overview.patches.failed_installations}</b></div>
        </div>
        <div className="timeline-list"><span className="timeline-title">Deployment timeline</span>{timeline.map((entry) => <div key={entry.deployment_date}><time>{entry.deployment_date}</time><span className="timeline-line" /><b>{entry.count} update{entry.count === 1 ? "" : "s"}</b></div>)}{!timeline.length && <p className="empty-note">No scheduled deployment dates.</p>}</div>
      </section>
      <section className="panel table-panel"><RecordsTable type="patches" rows={patches} /></section>
    </div>
  );
}
