from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import VM

router = APIRouter(tags=["virtualization"])


@router.get("/vms")
def list_vms(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in VM.__table__.columns} for row in db.scalars(select(VM).order_by(VM.vm_name))]


@router.get("/vms/alerts")
def vm_alerts(db: Session = Depends(get_db)) -> dict:
    rows = list(db.scalars(select(VM)))
    alerts = []
    for vm in rows:
        reasons = []
        if vm.snapshot_created:
            try:
                age = (datetime.now(UTC).date() - datetime.fromisoformat(vm.snapshot_created.replace("Z", "+00:00")).date()).days
                if age > 30:
                    reasons.append("snapshot older than 30 days")
                elif age > 7:
                    reasons.append("snapshot older than 7 days")
            except ValueError:
                pass
        if vm.datastore_free_percent < 15:
            reasons.append("datastore below 15% free")
        if vm.tools_status.lower() not in {"current", "ok"}:
            reasons.append("VMware Tools outdated or missing")
        if vm.cpu_ready_percent > 5:
            reasons.append("high CPU ready time")
        if vm.ballooning:
            reasons.append("memory ballooning active")
        if reasons:
            alerts.append({"vm_name": vm.vm_name, "alerts": reasons})
    return {"alert_count": sum(len(row["alerts"]) for row in alerts), "vms": alerts}
