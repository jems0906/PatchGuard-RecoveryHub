from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.reports.audit_report import build_audit_report
from app.reports.compliance_report import (
    build_compliance_overview,
    capture_daily_compliance_snapshot,
    compliance_trend,
)

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    result = build_compliance_overview(db)
    capture_daily_compliance_snapshot(db, result["overall_score"])
    return result


@router.get("/trend")
def trend(db: Session = Depends(get_db)) -> list[dict]:
    return compliance_trend(db)


@router.get("/audit")
def audit_report(db: Session = Depends(get_db)) -> JSONResponse:
    return JSONResponse(
        content=jsonable_encoder(build_audit_report(db)),
        headers={"Content-Disposition": 'attachment; filename="patchguard-compliance-audit.json"'},
    )
