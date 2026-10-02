from datetime import UTC, datetime

from app.models import ADIssue, Backup, Patch, VM, Vulnerability


def test_compliance_overview_weights_and_counts(client):
    client.post("/api/assets", json={"hostname": "SRV-A"})
    client.post("/api/assets", json={"hostname": "SRV-B"})
    with client.app.state.testing_session() as db:
        db.add_all([
            Patch(title="Critical A", classification="Critical", installation_status="installed", asset_hostname="SRV-A"),
            Patch(title="Security B", classification="Security", installation_status="failed", asset_hostname="SRV-B"),
            Vulnerability(cve_id="CVE-1", severity="critical", affected_asset="SRV-B", status="open"),
            Vulnerability(cve_id="CVE-2", severity="low", affected_asset="SRV-A", status="verified",
                          discovered_at="2026-09-25", verified_at="2026-10-02"),
            Backup(job_name="job-a", protected_system="SRV-A", status="success", sla_domain="Gold", last_successful_backup=datetime.now(UTC).isoformat()),
            Backup(job_name="job-b", protected_system="SRV-B", status="failed", sla_domain="Silver"),
            ADIssue(issue_type="Replication", status="open"),
            VM(vm_name="VM-A"),
        ])
        db.commit()
    response = client.get("/api/compliance/overview")
    assert response.status_code == 200
    overview = response.json()
    assert overview["patches"]["compliance_percent"] == 50
    assert overview["open_critical_vulnerabilities"] == 1
    assert overview["backups"]["success_rate"] == 50
    assert overview["active_directory"]["open_issues"] == 1
    assert overview["assets_total"] == 2
    assert overview["vms_total"] == 1
    assert overview["overall_score"] == 54
    assert overview["average_remediation_cycle_days"] == 7
