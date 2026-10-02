from datetime import date, timedelta

from app.models import VM


def test_vm_alerts_report_resource_and_snapshot_risks(client):
    with client.app.state.testing_session() as db:
        db.add(VM(
            vm_name="RISKY-VM",
            datastore_free_percent=10,
            cpu_ready_percent=6,
            ballooning=True,
            tools_status="outdated",
            snapshot_created=(date.today() - timedelta(days=40)).isoformat(),
        ))
        db.commit()
    response = client.get("/api/vms/alerts")
    assert response.status_code == 200
    assert response.json()["alert_count"] == 5
    assert len(response.json()["vms"][0]["alerts"]) == 5
