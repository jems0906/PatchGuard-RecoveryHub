from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Vulnerability
from app.schemas.vulnerability import VulnerabilityCreate, VulnerabilityUpdate

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("")
def list_vulnerabilities(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in Vulnerability.__table__.columns} for row in db.scalars(select(Vulnerability).order_by(Vulnerability.severity, Vulnerability.deadline))]


@router.post("", status_code=201)
def create_vulnerability(payload: VulnerabilityCreate, db: Session = Depends(get_db)) -> dict:
    row = Vulnerability(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {column.name: getattr(row, column.name) for column in Vulnerability.__table__.columns}


@router.patch("/{vulnerability_id}")
def update_vulnerability(vulnerability_id: int, payload: VulnerabilityUpdate, db: Session = Depends(get_db)) -> dict:
    changes = payload.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Provide valid vulnerability fields to update.")
    row = db.get(Vulnerability, vulnerability_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Vulnerability not found.")
    for name, value in changes.items():
        setattr(row, name, value)
    db.commit()
    db.refresh(row)
    return {column.name: getattr(row, column.name) for column in Vulnerability.__table__.columns}
