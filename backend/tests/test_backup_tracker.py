from datetime import UTC, datetime, timedelta

from app.backups.backup_tracker import backup_sla_state
from app.models import Backup


def test_backup_sla_state_accounts_for_tier_freshness():
    now = datetime(2026, 10, 2, 12, tzinfo=UTC)
    assert backup_sla_state(
        Backup(status="success", sla_domain="Gold", last_successful_backup=(now - timedelta(minutes=45)).isoformat()),
        now,
    ) == "on-track"
    assert backup_sla_state(
        Backup(status="success", sla_domain="Gold", last_successful_backup=(now - timedelta(minutes=100)).isoformat()),
        now,
    ) == "at-risk"
    assert backup_sla_state(
        Backup(status="success", sla_domain="Gold", last_successful_backup=(now - timedelta(hours=3)).isoformat()),
        now,
    ) == "breached"
    assert backup_sla_state(
        Backup(status="success", sla_domain="Silver", last_successful_backup="not-a-timestamp"),
        now,
    ) == "breached"
