from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backups.backup_tracker import backup_sla_state
from app.models import ADIssue, Asset, Backup, ComplianceSnapshot, Patch, VM, Vulnerability


def _percent(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 1) if denominator else 100.0


def build_compliance_overview(db: Session) -> dict:
    patches = list(db.scalars(select(Patch)))
    vulnerabilities = list(db.scalars(select(Vulnerability)))
    backups = list(db.scalars(select(Backup)))
    ad_issues = list(db.scalars(select(ADIssue)))
    assets = list(db.scalars(select(Asset)))
    vms = list(db.scalars(select(VM)))

    critical_patches = [p for p in patches if p.classification.lower() in {"critical", "security"}]
    patch_rate = _percent(sum(p.installation_status.lower() == "installed" for p in critical_patches), len(critical_patches))
    open_vulnerabilities = [v for v in vulnerabilities if v.status.lower() not in {"verified", "remediated"}]
    vulnerability_rate = _percent(len(vulnerabilities) - len(open_vulnerabilities), len(vulnerabilities))
    backup_rate = _percent(sum(backup_sla_state(b) == "on-track" for b in backups), len(backups))
    active_ad_issues = [issue for issue in ad_issues if issue.status.lower() not in {"resolved", "healthy"}]
    ad_rate = max(0.0, 100.0 - 10.0 * len(active_ad_issues))
    score = round(patch_rate * 0.35 + vulnerability_rate * 0.30 + backup_rate * 0.25 + ad_rate * 0.10, 1)
    critical_open = sum(v.severity.lower() == "critical" for v in open_vulnerabilities)
    today = datetime.now(UTC).date()
    verified_cycles = []
    for vulnerability in vulnerabilities:
        if vulnerability.status.lower() == "verified" and vulnerability.discovered_at and vulnerability.verified_at:
            opened, closed = _date(vulnerability.discovered_at), _date(vulnerability.verified_at)
            if opened and closed and closed >= opened:
                verified_cycles.append((closed - opened).days)
    overdue = [
        v for v in open_vulnerabilities
        if v.deadline and _date(v.deadline) and _date(v.deadline) < today
    ]

    patch_status = {
        "compliance_percent": patch_rate,
        "critical_needed": sum(p.installation_status.lower() != "installed" for p in critical_patches),
        "servers_needing_reboot": len({p.asset_hostname for p in patches if p.installation_status.lower() == "reboot required"}),
        "failed_installations": sum(p.installation_status.lower() == "failed" for p in patches),
        "timeline": _group_by(patches, "deployment_date", "deployment_date"),
    }
    by_severity = {
        severity: sum(v.severity.lower() == severity and v in open_vulnerabilities for v in vulnerabilities)
        for severity in ("critical", "high", "medium", "low")
    }
    backup_summary = {
        "success_rate": backup_rate,
        "failed_jobs": sum(b.status.lower() in {"failed", "partial"} for b in backups),
        "without_recent_success": sum(backup_sla_state(b) != "on-track" for b in backups),
        "restore_test_coverage": _percent(sum(bool(b.restore_test_date) for b in backups), len(backups)),
        "sla_compliance": {
            tier: _percent(sum(backup_sla_state(b) == "on-track" for b in backups if b.sla_domain.lower().startswith(tier.lower())),
                           sum(b.sla_domain.lower().startswith(tier.lower()) for b in backups))
            for tier in ("Gold", "Silver", "Bronze")
        },
    }
    failures_by_asset: dict[str, int] = {}
    for vuln in open_vulnerabilities:
        failures_by_asset[vuln.affected_asset] = failures_by_asset.get(vuln.affected_asset, 0) + 1
    for patch in patches:
        if patch.installation_status.lower() in {"failed", "reboot required"} and patch.asset_hostname:
            failures_by_asset[patch.asset_hostname] = failures_by_asset.get(patch.asset_hostname, 0) + 1
    high_risk = sorted(({"hostname": name, "compliance_failures": count} for name, count in failures_by_asset.items() if count >= 2),
                       key=lambda item: item["compliance_failures"], reverse=True)

    return {
        "overall_score": score,
        "components": {
            "patching": {"score": patch_rate, "weight": 35},
            "vulnerabilities": {"score": vulnerability_rate, "weight": 30},
            "backups": {"score": backup_rate, "weight": 25},
            "active_directory": {"score": ad_rate, "weight": 10},
        },
        "assets_total": len(assets),
        "vms_total": len(vms),
        "open_critical_vulnerabilities": critical_open,
        "open_vulnerabilities": len(open_vulnerabilities),
        "overdue_remediations": len(overdue),
        "average_remediation_cycle_days": round(sum(verified_cycles) / len(verified_cycles), 1) if verified_cycles else None,
        "servers_needing_reboot": patch_status["servers_needing_reboot"],
        "patches": patch_status,
        "vulnerabilities_by_severity": by_severity,
        "backups": backup_summary,
        "active_directory": {"open_issues": len(active_ad_issues), "healthy_percent": ad_rate},
        "high_risk_systems": high_risk,
    }


def _date(value: str):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _group_by(rows: list, attribute: str, output_key: str) -> list[dict]:
    grouped: dict[str, int] = {}
    for row in rows:
        value = getattr(row, attribute, "") or "Unscheduled"
        grouped[value] = grouped.get(value, 0) + 1
    return [{output_key: key, "count": value} for key, value in sorted(grouped.items())]


def compliance_trend(db: Session) -> list[dict]:
    cutoff = datetime.utcnow() - timedelta(days=30)
    snapshots = db.scalars(
        select(ComplianceSnapshot).where(ComplianceSnapshot.captured_at >= cutoff).order_by(ComplianceSnapshot.captured_at)
    )
    return [{"date": row.captured_at.date().isoformat(), "score": row.score} for row in snapshots]
