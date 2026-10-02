const modules = [
  ["patching", "Patch compliance"],
  ["vulnerabilities", "Vulnerability remediation"],
  ["backups", "Backup success"],
  ["active_directory", "Active Directory hygiene"],
];

export default function ComplianceOverview({ overview }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">WEIGHTED CONTROLS</p>
          <h2>Compliance by area</h2>
        </div>
        <span className="muted">Scores reflect imported operational data</span>
      </div>
      <div className="control-list">
        {modules.map(([key, label]) => {
          const value = overview.components?.[key]?.score ?? 0;
          return (
            <div className="control-row" key={key}>
              <div className="control-meta"><span>{label}</span><b>{value}%</b></div>
              <div className="progress-track"><div className={`progress-fill ${value < 70 ? "warning" : ""}`} style={{ width: `${value}%` }} /></div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
