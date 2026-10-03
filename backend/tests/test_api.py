def test_health_and_asset_lifecycle(client):
    assert client.get("/api/health").json()["status"] == "ok"
    created = client.post("/api/assets", json={"hostname": "WEB01", "role": "Web Server"})
    assert created.status_code == 201
    assert created.json()["hostname"] == "WEB01"
    assert client.post("/api/assets", json={"hostname": "WEB01"}).status_code == 409
    assert len(client.get("/api/assets").json()) == 1


def test_vulnerability_verification(client):
    response = client.post("/api/vulnerabilities", json={
        "cve_id": "CVE-2026-10101",
        "affected_asset": "APP01",
        "severity": "high",
    })
    assert response.status_code == 201
    vulnerability_id = response.json()["id"]
    updated = client.patch(f"/api/vulnerabilities/{vulnerability_id}", json={"status": "verified", "verified_by": "Operator"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "verified"
    assert client.patch(f"/api/vulnerabilities/{vulnerability_id}", json={"unknown": "value"}).status_code == 422


def test_patch_create_and_ad_action_audit_log(client):
    patch = client.post("/api/patches", json={"title": "Security update", "asset_hostname": "APP01"})
    assert patch.status_code == 201
    assert patch.json()["installation_status"] == "needed"
    action = client.post("/api/ad/actions", json={
        "action_type": "Account unlock",
        "target": "j.smith",
        "actor": "Operator",
        "ticket_reference": "CHG-42",
    })
    assert action.status_code == 201
    assert action.json()["target"] == "j.smith"
    assert client.get("/api/ad/actions").json()[0]["ticket_reference"] == "CHG-42"
    invalid = client.post("/api/ad/actions", json={
        "action_type": "Unlock account",
        "target": "j.smith",
        "actor": "Operator",
        "ticket_reference": "CHG-43",
    })
    assert invalid.status_code == 422


def test_patch_lifecycle_requires_approval_and_records_installation(client):
    patch = client.post("/api/patches", json={"title": "Security update", "asset_hostname": "APP01"})
    patch_id = patch.json()["id"]
    assert client.patch(f"/api/patches/{patch_id}", json={"installation_status": "downloading"}).status_code == 409
    approved = client.patch(f"/api/patches/{patch_id}", json={"approval_status": "APPROVED"})
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "approved"
    installed = client.patch(f"/api/patches/{patch_id}", json={"installation_status": "installed"})
    assert installed.status_code == 200
    assert installed.json()["installation_status"] == "installed"
    assert client.patch(f"/api/patches/{patch_id}", json={"approval_status": "declined"}).status_code == 409
    assert client.patch("/api/patches/9999", json={"approval_status": "approved"}).status_code == 404
    assert client.patch(f"/api/patches/{patch_id}", json={"installation_status": "unknown"}).status_code == 422


def test_ad_hygiene_metrics_and_audit_export(client):
    from datetime import date, timedelta
    from app.models import ADIssue

    with client.app.state.testing_session() as db:
        db.add_all([
            ADIssue(issue_type="Disabled Account", username="former.user", account_enabled=False),
            ADIssue(
                issue_type="Password Expiry",
                username="svc_reports",
                is_service_account=True,
                password_age_days=120,
                password_expires_at=(date.today() + timedelta(days=5)).isoformat(),
            ),
        ])
        db.commit()
    health = client.get("/api/ad/health").json()
    assert health["disabled_accounts"] == 1
    assert health["passwords_expiring_within_7_days"] == 1
    assert health["service_accounts_over_password_age"] == 1

    report_response = client.get("/api/compliance/audit")
    assert report_response.status_code == 200
    assert "attachment; filename=" in report_response.headers["content-disposition"]
    report = report_response.json()
    assert report["report_type"] == "PatchGuard RecoveryHub compliance audit"
    assert "active_directory_findings" in report["evidence"]


def test_overview_captures_one_compliance_snapshot_per_day(client):
    from app.models import ComplianceSnapshot
    from sqlalchemy import select

    client.get("/api/compliance/overview")
    client.get("/api/compliance/overview")
    with client.app.state.testing_session() as db:
        snapshots = list(db.scalars(select(ComplianceSnapshot)))
    assert len(snapshots) == 1
    trend = client.get("/api/compliance/trend").json()
    assert len(trend) == 1


def test_csv_import_validates_and_persists_rows(client):
    response = client.post(
        "/api/imports?entity=assets",
        files={"file": ("assets.csv", "hostname,role,os_version\nSRV-01,Database,Windows Server 2022\n", "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["imported"] == 1
    assert client.get("/api/assets").json()[0]["hostname"] == "SRV-01"


def test_csv_import_persists_ad_hygiene_and_backup_policy_fields(client):
    ad_report = (
        "issue_type,username,account_enabled,is_service_account,password_last_set,"
        "password_expires_at,password_age_days\n"
        "Password Expiry,svc_api,true,true,2026-09-01,2026-10-05,34\n"
    )
    ad_response = client.post(
        "/api/imports?entity=ad_issues",
        files={"file": ("ad.csv", ad_report, "text/csv")},
    )
    assert ad_response.status_code == 200
    ad_row = client.get("/api/ad/issues").json()[0]
    assert ad_row["is_service_account"] is True
    assert ad_row["password_age_days"] == 34

    backup_report = (
        "protected_system,job_name,schedule_cadence,retention_days\n"
        "APP01,APP01-hourly,hourly,30\n"
    )
    backup_response = client.post(
        "/api/imports?entity=backups",
        files={"file": ("backup.csv", backup_report, "text/csv")},
    )
    assert backup_response.status_code == 200
    backup_row = client.get("/api/backups").json()[0]
    assert backup_row["schedule_cadence"] == "hourly"
    assert backup_row["retention_days"] == 30


def test_csv_import_rejects_unknown_entity_and_missing_required_field(client):
    files = {"file": ("items.csv", "not_a_field\nhello\n", "text/csv")}
    assert client.post("/api/imports?entity=unknown", files=files).status_code == 422
    invalid = {"file": ("assets.csv", "role\nDatabase\n", "text/csv")}
    assert client.post("/api/imports?entity=assets", files=invalid).status_code == 422


def test_csv_import_rejects_invalid_boolean_and_empty_records(client):
    invalid = {"file": ("vms.csv", "vm_name,ballooning\nAPP01,sometimes\n", "text/csv")}
    assert client.post("/api/imports?entity=vms", files=invalid).status_code == 422
    empty = {"file": ("assets.json", "[]", "application/json")}
    assert client.post("/api/imports?entity=assets", files=empty).status_code == 422


def test_vm_import_uses_defaults_for_blank_optional_numbers(client):
    report = "vm_name,vcpus,memory_active_gb,snapshot_size_gb\nVM-EMPTY,,,\n"
    response = client.post(
        "/api/imports?entity=vms",
        files={"file": ("vms.csv", report, "text/csv")},
    )
    assert response.status_code == 200
    vm = client.get("/api/vms").json()[0]
    assert vm["vcpus"] == 2
    assert vm["memory_active_gb"] == 0


def test_backup_readiness_scores_restore_test_recency(client):
    from datetime import UTC, date, datetime, timedelta

    with client.app.state.testing_session() as db:
        from app.models import Backup
        db.add_all([
            Backup(job_name="fresh", protected_system="A", status="success", last_successful_backup=datetime.now(UTC).isoformat(), restore_test_date=date.today().isoformat(), restore_test_result="passed"),
            Backup(job_name="failed", protected_system="B", status="failed"),
            Backup(job_name="stale-test", protected_system="C", status="success", last_successful_backup=datetime.now(UTC).isoformat(), restore_test_date=(date.today() - timedelta(days=120)).isoformat(), restore_test_result="passed"),
        ])
        db.commit()
    result = client.get("/api/backups/readiness").json()
    assert result["average_score"] == 53.3
    assert [row["score"] for row in result["systems"]] == [100, 0, 60]
