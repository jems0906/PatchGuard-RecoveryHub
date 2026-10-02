from datetime import UTC, datetime, timedelta

from app.models import Backup

SLA_WINDOWS = {
    "gold": timedelta(hours=2),
    "silver": timedelta(hours=26),
    "bronze": timedelta(days=8),
}


def backup_sla_state(backup: Backup, now: datetime | None = None) -> str:
    if backup.status.lower() in {"failed", "partial"} or not backup.last_successful_backup:
        return "breached"
    try:
        last_success = datetime.fromisoformat(backup.last_successful_backup.replace("Z", "+00:00"))
    except ValueError:
        return "breached"
    if last_success.tzinfo is None:
        last_success = last_success.replace(tzinfo=UTC)
    current_time = now or datetime.now(UTC)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=UTC)
    tier = next((key for key in SLA_WINDOWS if backup.sla_domain.lower().startswith(key)), None)
    window = SLA_WINDOWS[tier] if tier else timedelta(days=1)
    age = current_time - last_success
    if age > window:
        return "breached"
    if age > window * 0.75:
        return "at-risk"
    return "on-track"
