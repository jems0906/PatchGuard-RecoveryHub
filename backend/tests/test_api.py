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


def test_csv_import_validates_and_persists_rows(client):
    response = client.post(
        "/api/imports?entity=assets",
        files={"file": ("assets.csv", "hostname,role,os_version\nSRV-01,Database,Windows Server 2022\n", "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["imported"] == 1
    assert client.get("/api/assets").json()[0]["hostname"] == "SRV-01"


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
