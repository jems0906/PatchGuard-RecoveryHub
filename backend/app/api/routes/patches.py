from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patch
from app.schemas.patch import PatchCreate, PatchUpdate

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


@router.patch("/{patch_id}")
def update_patch(patch_id: int, payload: PatchUpdate, db: Session = Depends(get_db)) -> dict:
    changes = payload.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Provide valid patch fields to update.")
    row = db.get(Patch, patch_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Patch not found.")
    resulting_approval = changes.get("approval_status", row.approval_status).lower()
    resulting_installation = changes.get("installation_status", row.installation_status).lower()
    if "installation_status" in changes and resulting_installation != "needed" and resulting_approval != "approved":
        raise HTTPException(status_code=409, detail="Approve the patch before changing its installation status.")
    if "approval_status" in changes and resulting_approval != "approved" and resulting_installation != "needed":
        raise HTTPException(status_code=409, detail="A patch with installation activity cannot be unapproved or declined.")
    for name, value in changes.items():
        setattr(row, name, value)
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
