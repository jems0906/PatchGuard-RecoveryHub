from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.reports.compliance_report import build_compliance_overview, compliance_trend

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    return build_compliance_overview(db)


@router.get("/trend")
def trend(db: Session = Depends(get_db)) -> list[dict]:
    return compliance_trend(db)
