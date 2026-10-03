"""Add structured AD hygiene and backup retention evidence."""

from alembic import op
import sqlalchemy as sa

revision = "0002_operational_evidence"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    additions = {
        "ad_issues": [
            sa.Column("account_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("is_service_account", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("password_last_set", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("password_expires_at", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("password_age_days", sa.Integer(), nullable=False, server_default="0"),
        ],
        "backups": [
            sa.Column("schedule_cadence", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("retention_days", sa.Integer(), nullable=False, server_default="0"),
        ],
    }
    inspector = sa.inspect(op.get_bind())
    for table, columns in additions.items():
        present = {column["name"] for column in inspector.get_columns(table)}
        for column in columns:
            if column.name not in present:
                op.add_column(table, column)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    for table, names in {
        "backups": ("retention_days", "schedule_cadence"),
        "ad_issues": ("password_age_days", "password_expires_at", "password_last_set", "is_service_account", "account_enabled"),
    }.items():
        present = {column["name"] for column in inspector.get_columns(table)}
        for name in names:
            if name in present:
                op.drop_column(table, name)
