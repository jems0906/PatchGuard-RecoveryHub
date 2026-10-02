from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backups.backup_tracker import backup_sla_state
from app.database import get_db
from app.models import Backup

router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("")
def list_backups(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in Backup.__table__.columns} for row in db.scalars(select(Backup).order_by(Backup.protected_system))]


@router.get("/sla")
def backup_sla(db: Session = Depends(get_db)) -> dict:
    rows = list(db.scalars(select(Backup).order_by(Backup.protected_system)))
    tiers = {}
    for tier in ("Gold", "Silver", "Bronze"):
        matches = [row for row in rows if row.sla_domain.lower().startswith(tier.lower())]
        tiers[tier] = {
            "total": len(matches),
            "on_track": sum(backup_sla_state(row) == "on-track" for row in matches),
            "compliance_percent": round(100 * sum(backup_sla_state(row) == "on-track" for row in matches) / len(matches), 1) if matches else 100.0,
            "at_risk": sum(backup_sla_state(row) == "at-risk" for row in matches),
            "breached": sum(backup_sla_state(row) == "breached" for row in matches),
        }
    return {
        "total_jobs": len(rows),
        "failed_jobs": sum(row.status.lower() in {"failed", "partial"} for row in rows),
        "restore_test_coverage_percent": round(100 * sum(bool(row.restore_test_date) for row in rows) / len(rows), 1) if rows else 100.0,
        "tiers": tiers,
        "backups": [{column.name: getattr(row, column.name) for column in Backup.__table__.columns} for row in rows],
    }


@router.get("/readiness")
def recovery_readiness(db: Session = Depends(get_db)) -> dict:
    rows = list(db.scalars(select(Backup).order_by(Backup.protected_system)))
    today = date.today()
    readiness = []
    for row in rows:
        sla_state = backup_sla_state(row)
        sla_score = {"on-track": 100, "at-risk": 50, "breached": 0}[sla_state]
        try:
            tested = datetime.fromisoformat(row.restore_test_date).date() if row.restore_test_date else None
        except ValueError:
            tested = None
        restore_score = 100 if tested and 0 <= (today - tested).days <= 90 and row.restore_test_result.lower() == "passed" else 0
        readiness.append({
            "protected_system": row.protected_system,
            "score": round(sla_score * 0.6 + restore_score * 0.4, 1),
            "sla_score": sla_score,
            "sla_state": sla_state,
            "restore_test_score": restore_score,
            "restore_test_date": row.restore_test_date,
        })
    average = round(sum(item["score"] for item in readiness) / len(readiness), 1) if readiness else 100.0
    return {"average_score": average, "systems": readiness}
