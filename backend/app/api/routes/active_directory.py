from datetime import datetime, UTC

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ADAction, ADIssue
from app.reports.compliance_report import ad_hygiene_summary
from app.schemas.active_directory import ADActionCreate

router = APIRouter(prefix="/ad", tags=["active-directory"])


@router.get("/health")
def ad_health(db: Session = Depends(get_db)) -> dict:
    issues = list(db.scalars(select(ADIssue)))
    summary = ad_hygiene_summary(issues)
    return {
        "status": "healthy" if not summary["open_issues"] else "attention_required",
        "total_checks": len(issues),
        **summary,
        "issues": [{column.name: getattr(row, column.name) for column in ADIssue.__table__.columns} for row in issues],
    }


@router.get("/issues")
def list_ad_issues(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in ADIssue.__table__.columns} for row in db.scalars(select(ADIssue))]


@router.get("/actions")
def list_ad_actions(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in ADAction.__table__.columns}
            for row in db.scalars(select(ADAction).order_by(ADAction.created_at.desc()))]


@router.post("/actions", status_code=201)
def record_ad_action(payload: ADActionCreate, db: Session = Depends(get_db)) -> dict:
    row = ADAction(**payload.model_dump(), created_at=datetime.now(UTC).isoformat(timespec="seconds"))
    db.add(row)
    db.commit()
    db.refresh(row)
    return {column.name: getattr(row, column.name) for column in ADAction.__table__.columns}
