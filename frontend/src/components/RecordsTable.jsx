const columnSets = {
  patches: [["title", "Update"], ["kb_number", "KB"], ["classification", "Class"], ["asset_hostname", "Server"], ["approval_status", "Approval"], ["installation_status", "Install status"], ["wave", "Wave"], ["deployment_date", "Deployment"]],
  vulnerabilities: [["cve_id", "CVE"], ["severity", "Severity"], ["affected_asset", "Asset"], ["description", "Finding"], ["remediation", "Remediation"], ["patch_available", "Patch available"], ["kb_number", "KB"], ["registry_change_needed", "Registry change"], ["registry_key", "Registry key"], ["registry_value", "Registry value"], ["status", "Status"], ["deadline", "Deadline"], ["verified_by", "Verified by"], ["verified_at", "Verified date"]],
  ad: [["issue_type", "Check"], ["username", "User"], ["account_enabled", "Enabled"], ["is_service_account", "Service account"], ["password_age_days", "Password age days"], ["password_expires_at", "Password expiry"], ["object_name", "Object"], ["domain_controller", "Domain controller"], ["dc_status", "DC status"], ["last_sync", "Last sync"], ["failed_partner", "Failed partner"], ["status", "Status"], ["last_logon", "Last logon"], ["lockout_time", "Lockout time"], ["source", "Source"], ["details", "Details"]],
  vms: [["vm_name", "VM"], ["power_state", "Power"], ["host_cluster", "Cluster"], ["datastore", "Datastore"], ["vcpus", "vCPU"], ["cpu_ready_percent", "CPU ready %"], ["memory_allocated_gb", "Memory alloc. GB"], ["memory_active_gb", "Memory active GB"], ["ballooning", "Ballooning"], ["disk_provisioned_gb", "Disk prov. GB"], ["disk_used_gb", "Disk used GB"], ["datastore_free_percent", "DS free %"], ["tools_status", "Tools"], ["snapshot_name", "Snapshot"], ["snapshot_size_gb", "Snapshot GB"], ["snapshot_created", "Snapshot date"], ["health_alerts", "Health alerts"]],
  backups: [["protected_system", "System"], ["job_name", "Job"], ["sla_domain", "SLA tier"], ["sla_state", "SLA state"], ["score", "Readiness"], ["backup_type", "Type"], ["schedule_cadence", "Cadence"], ["retention_days", "Retention days"], ["last_successful_backup", "Last success"], ["status", "Last job"], ["next_scheduled_backup", "Next scheduled"], ["restore_test_date", "Restore test"], ["restore_test_result", "Test result"], ["tested_by", "Tested by"], ["error_details", "Error details"]],
};

const titles = { patches: "WSUS patch deployment", vulnerabilities: "Vulnerability remediation", ad: "Active Directory health", vms: "VMware inventory", backups: "Backup validation" };

const patchStatuses = {
  approval_status: ["not approved", "approved", "declined"],
  installation_status: ["needed", "downloading", "installed", "failed", "reboot required"],
};

export default function RecordsTable({ type, rows, onVerify, onPatchUpdate }) {
  const columns = columnSets[type];
  return (
    <>
      <div className="toolbar"><div><p className="eyebrow">OPERATIONS</p><h2>{titles[type]} <span className="count-pill">{rows.length}</span></h2></div></div>
      <div className="table-scroll">
        <table>
          <thead><tr>{columns.map(([, label]) => <th key={label}>{label}</th>)}{type === "vulnerabilities" && <th>Action</th>}</tr></thead>
          <tbody>
            {rows.map((row) => <tr key={row.id}>
              {columns.map(([key]) => <td key={key} className={key === "severity" ? `severity-${String(row[key]).toLowerCase()}` : key === "status" || key === "installation_status" ? "status-cell" : ""}>
                {type === "patches" && patchStatuses[key] ? <select aria-label={`${key.replace("_", " ")} for ${row.title}`} value={String(row[key] ?? "").toLowerCase().replaceAll("_", " ")} onChange={(event) => onPatchUpdate(row.id, { [key]: event.target.value })}>{patchStatuses[key].map((status) => <option key={status} value={status}>{status}</option>)}</select> : key === "description" || key === "details" || key === "remediation" || key === "error_details" || key === "registry_key" || key === "registry_value" ? <span className="truncate" title={row[key]}>{row[key] || "—"}</span> : typeof row[key] === "boolean" ? (row[key] ? "Yes" : "No") : row[key] ?? "—"}
              </td>)}
              {type === "vulnerabilities" && <td>{!["verified", "remediated"].includes(row.status?.toLowerCase()) && <button className="button button-small" onClick={() => onVerify(row.id)}>Mark verified</button>}</td>}
            </tr>)}
            {!rows.length && <tr><td className="empty-cell" colSpan={columns.length + (type === "vulnerabilities" ? 1 : 0)}>No records available.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}
