from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ADAction, ADIssue, Asset, Backup, ComplianceSnapshot, Patch, VM, Vulnerability
from app.reports.compliance_report import build_compliance_overview, compliance_trend


def _records(db: Session, model, order_by=None) -> list[dict]:
    statement = select(model)
    if order_by is not None:
        statement = statement.order_by(order_by)
    return [
        {column.name: getattr(row, column.name) for column in model.__table__.columns}
        for row in db.scalars(statement)
    ]


def build_audit_report(db: Session) -> dict:
    overview = build_compliance_overview(db)
    return {
        "report_type": "PatchGuard RecoveryHub compliance audit",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "trend_period_days": 30,
        "summary": overview,
        "compliance_trend": compliance_trend(db),
        "evidence": {
            "assets": _records(db, Asset),
            "patches": _records(db, Patch),
            "vulnerabilities": _records(db, Vulnerability),
            "active_directory_findings": _records(db, ADIssue),
            "active_directory_actions": _records(db, ADAction, ADAction.created_at.desc()),
            "virtual_machines": _records(db, VM),
            "backups": _records(db, Backup),
            "compliance_snapshots": _records(db, ComplianceSnapshot, ComplianceSnapshot.captured_at),
        },
    }
