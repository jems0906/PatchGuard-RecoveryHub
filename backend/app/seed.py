from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ADIssue, Asset, Backup, ComplianceSnapshot, Patch, VM, Vulnerability
from app.reports.compliance_report import build_compliance_overview


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Asset)):
        return
    assets = [
        Asset(hostname="DC01", os_version="Windows Server 2022", role="Domain Controller", ip_address="10.20.0.10", domain="corp.example", forest="corp.example", site="HQ", fsmo_roles="PDC Emulator; RID Master", last_boot="2026-09-28", asset_type="Domain Controller", backup_policy="Gold"),
        Asset(hostname="APP01", os_version="Windows Server 2022", role="Application Server", ip_address="10.20.1.20", domain="corp.example", last_boot="2026-09-17", asset_type="Application", app_name="Claims API", service_status="Running", backup_policy="Gold"),
        Asset(hostname="SQL01", os_version="Windows Server 2019", role="Database Server", ip_address="10.20.1.30", domain="corp.example", last_boot="2026-08-30", asset_type="Server", backup_policy="Silver"),
        Asset(hostname="FILE01", os_version="Windows Server 2022", role="File Server", ip_address="10.20.2.15", domain="corp.example", last_boot="2026-09-20", asset_type="Server", backup_policy="Silver"),
        Asset(hostname="WEB01", os_version="Windows Server 2022", role="Web Server", ip_address="10.20.1.40", domain="corp.example", last_boot="2026-09-05", asset_type="Server", backup_policy="Bronze"),
    ]
    db.add_all(assets)
    db.add_all([
        Patch(title="Windows Server Security Update", kb_number="KB5061234", classification="Security", approval_status="approved", target_group="Production Servers", asset_hostname="DC01", installation_status="installed", wave="Wave 1", deployment_date="2026-09-25"),
        Patch(title="Cumulative Update for Windows Server", kb_number="KB5061200", classification="Critical", approval_status="approved", target_group="Production Servers", asset_hostname="APP01", installation_status="reboot required", wave="Wave 1", deployment_date="2026-09-26"),
        Patch(title=".NET Framework Security Update", kb_number="KB5061010", classification="Security", approval_status="approved", target_group="Production Servers", asset_hostname="SQL01", installation_status="failed", wave="Wave 2", deployment_date="2026-09-27"),
        Patch(title="Windows Defender Definition Update", kb_number="KB2267602", classification="Update Rollup", approval_status="approved", target_group="All Servers", asset_hostname="FILE01", installation_status="installed", wave="Wave 1", deployment_date="2026-09-28"),
        Patch(title="Windows Server Security Update", kb_number="KB5061234", classification="Security", approval_status="approved", target_group="Production Servers", asset_hostname="WEB01", installation_status="needed", wave="Wave 2", deployment_date="2026-10-04"),
    ])
    db.add_all([
        Vulnerability(cve_id="CVE-2099-12345", severity="critical", affected_asset="APP01", description="Synthetic remote code execution finding for demonstration.", remediation="Install the lab security update and verify service health.", patch_available=True, kb_number="KB5061234", status="scheduled", deadline=(date.today() + timedelta(days=2)).isoformat()),
        Vulnerability(cve_id="CVE-2099-23456", severity="high", affected_asset="SQL01", description="Synthetic privilege escalation finding for demonstration.", remediation="Apply the lab security update during the next maintenance window.", patch_available=True, kb_number="KB5061010", status="open", deadline=(date.today() - timedelta(days=3)).isoformat()),
        Vulnerability(cve_id="CVE-2099-98765", severity="medium", affected_asset="WEB01", description="Synthetic configuration finding for demonstration.", remediation="Disable legacy protocol using the approved server baseline.", registry_change_needed=True, registry_key="HKLM\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders", registry_value="Enabled", status="in progress", deadline=(date.today() + timedelta(days=14)).isoformat()),
        Vulnerability(cve_id="CVE-2099-76543", severity="low", affected_asset="FILE01", description="Synthetic informational finding for demonstration.", remediation="Update package during routine maintenance.", status="verified", discovered_at=(date.today() - timedelta(days=9)).isoformat(), verified_by="Alex Morgan", verified_at=date.today().isoformat()),
    ])
    db.add_all([
        ADIssue(issue_type="Replication", domain_controller="DC01", dc_status="online", last_sync=(datetime.now(UTC) - timedelta(hours=5)).isoformat(timespec="minutes"), failed_partner="DC02", status="open", source="DC02", details="Last replication attempt returned a transient RPC error."),
        ADIssue(issue_type="Locked Account", username="j.smith", domain_controller="DC01", status="open", lockout_time=datetime.utcnow().isoformat(timespec="minutes"), source="APP01", details="Repeated failed sign-in attempts."),
        ADIssue(issue_type="Stale Computer", object_name="LAPTOP-OLD23", status="open", last_logon=(date.today() - timedelta(days=126)).isoformat(), details="No interactive logon in more than 90 days."),
        ADIssue(issue_type="Password Expiry", username="svc_reports", status="open", last_modified=(date.today() - timedelta(days=80)).isoformat(), is_service_account=True, password_last_set=(date.today() - timedelta(days=110)).isoformat(), password_age_days=110, password_expires_at=(date.today() + timedelta(days=5)).isoformat(), details="Service account password is nearing expiry and exceeds the configured age threshold."),
        ADIssue(issue_type="Disabled Account", username="former.user", status="open", account_enabled=False, details="Disabled account requires owner and retention review."),
    ])
    db.add_all([
        VM(vm_name="APP01", power_state="poweredOn", host_cluster="Prod-Cluster-A", datastore="DS-Prod-01", vcpus=4, cpu_ready_percent=2.1, memory_allocated_gb=16, memory_active_gb=11.2, ballooning=False, disk_provisioned_gb=180, disk_used_gb=122, datastore_free_percent=32, tools_status="current", snapshot_name="pre-sept-patch", snapshot_size_gb=18, snapshot_created=(date.today() - timedelta(days=11)).isoformat()),
        VM(vm_name="SQL01", power_state="poweredOn", host_cluster="Prod-Cluster-A", datastore="DS-Prod-02", vcpus=8, cpu_ready_percent=7.4, memory_allocated_gb=32, memory_active_gb=28, ballooning=True, disk_provisioned_gb=800, disk_used_gb=610, datastore_free_percent=12, tools_status="outdated", snapshot_name="sql-before-upgrade", snapshot_size_gb=94, snapshot_created=(date.today() - timedelta(days=38)).isoformat()),
        VM(vm_name="WEB01", power_state="poweredOn", host_cluster="Prod-Cluster-B", datastore="DS-Web-01", vcpus=2, cpu_ready_percent=1.2, memory_allocated_gb=8, memory_active_gb=4.7, disk_provisioned_gb=120, disk_used_gb=66, datastore_free_percent=48, tools_status="current"),
    ])
    db.add_all([
        Backup(job_name="APP01-Daily", protected_system="APP01", backup_type="incremental", sla_domain="Gold", last_successful_backup=datetime.now(UTC).isoformat(timespec="minutes"), status="success", next_scheduled_backup=(datetime.now(UTC) + timedelta(hours=1)).isoformat(timespec="minutes"), schedule_cadence="hourly", retention_days=30, restore_test_date=(date.today() - timedelta(days=18)).isoformat(), restore_test_result="passed", tested_by="Jordan Lee"),
        Backup(job_name="SQL01-Daily", protected_system="SQL01", backup_type="full", sla_domain="Gold", last_successful_backup=(datetime.now(UTC) - timedelta(days=2)).isoformat(timespec="minutes"), status="failed", next_scheduled_backup=(datetime.now(UTC) + timedelta(hours=1)).isoformat(timespec="minutes"), schedule_cadence="hourly", retention_days=30, restore_test_date=(date.today() - timedelta(days=45)).isoformat(), restore_test_result="passed", tested_by="Jordan Lee", error_details="Snapshot job exceeded the configured window."),
        Backup(job_name="FILE01-Daily", protected_system="FILE01", backup_type="incremental", sla_domain="Silver", last_successful_backup=datetime.now(UTC).isoformat(timespec="minutes"), status="success", next_scheduled_backup=(datetime.now(UTC) + timedelta(hours=6)).isoformat(timespec="minutes"), schedule_cadence="daily", retention_days=14),
        Backup(job_name="WEB01-Weekly", protected_system="WEB01", backup_type="full", sla_domain="Bronze", last_successful_backup=datetime.now(UTC).isoformat(timespec="minutes"), status="success", next_scheduled_backup=(datetime.now(UTC) + timedelta(days=6)).isoformat(timespec="minutes"), schedule_cadence="weekly", retention_days=7, restore_test_date=(date.today() - timedelta(days=25)).isoformat(), restore_test_result="passed", tested_by="Sam Patel"),
    ])
    db.flush()
    today = datetime.utcnow().date()
    current_score = build_compliance_overview(db)["overall_score"]
    db.add_all(ComplianceSnapshot(captured_at=datetime.combine(today - timedelta(days=offset), datetime.min.time()),
                                  score=round(max(0, current_score - offset * 0.4), 1)) for offset in range(29, -1, -1))
    db.commit()
