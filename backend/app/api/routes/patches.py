from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patch
from app.schemas.patch import PatchCreate

router = APIRouter(prefix="/patches", tags=["patches"])


@router.get("")
def list_patches(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in Patch.__table__.columns} for row in db.scalars(select(Patch).order_by(Patch.deployment_date.desc()))]


@router.post("", status_code=201)
def create_patch(payload: PatchCreate, db: Session = Depends(get_db)) -> dict:
    row = Patch(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {column.name: getattr(row, column.name) for column in Patch.__table__.columns}


@router.get("/compliance")
def patch_compliance(db: Session = Depends(get_db)) -> dict:
    rows = list(db.scalars(select(Patch)))
    critical = [row for row in rows if row.classification.lower() in {"critical", "security"}]
    installed = sum(row.installation_status.lower() == "installed" for row in critical)
    return {
        "compliance_percent": round(installed * 100 / len(critical), 1) if critical else 100.0,
        "critical_needed": sum(row.installation_status.lower() != "installed" for row in critical),
        "failed_installations": sum(row.installation_status.lower() == "failed" for row in rows),
        "servers_needing_reboot": len({row.asset_hostname for row in rows if row.installation_status.lower() == "reboot required"}),
        "patches": [{column.name: getattr(row, column.name) for column in Patch.__table__.columns} for row in rows],
    }
