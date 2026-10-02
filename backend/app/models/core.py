from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(120), index=True)
    os_version: Mapped[str] = mapped_column(String(120), default="")
    role: Mapped[str] = mapped_column(String(80), default="Server")
    ip_address: Mapped[str] = mapped_column(String(64), default="")
    domain: Mapped[str] = mapped_column(String(120), default="")
    forest: Mapped[str] = mapped_column(String(120), default="")
    site: Mapped[str] = mapped_column(String(120), default="")
    fsmo_roles: Mapped[str] = mapped_column(String(240), default="")
    last_boot: Mapped[str] = mapped_column(String(40), default="")
    asset_type: Mapped[str] = mapped_column(String(40), default="Server")
    app_name: Mapped[str] = mapped_column(String(120), default="")
    service_status: Mapped[str] = mapped_column(String(40), default="")
    backup_policy: Mapped[str] = mapped_column(String(120), default="")


class Patch(Base):
    __tablename__ = "patches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(240))
    kb_number: Mapped[str] = mapped_column(String(40), default="")
    classification: Mapped[str] = mapped_column(String(40), default="Security")
    approval_status: Mapped[str] = mapped_column(String(40), default="not approved")
    target_group: Mapped[str] = mapped_column(String(120), default="")
    asset_hostname: Mapped[str] = mapped_column(String(120), default="", index=True)
    installation_status: Mapped[str] = mapped_column(String(40), default="needed")
    wave: Mapped[str] = mapped_column(String(80), default="")
    deployment_date: Mapped[str] = mapped_column(String(40), default="")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cve_id: Mapped[str] = mapped_column(String(40), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    affected_asset: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    remediation: Mapped[str] = mapped_column(Text, default="")
    patch_available: Mapped[bool] = mapped_column(Boolean, default=False)
    kb_number: Mapped[str] = mapped_column(String(40), default="")
    registry_change_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    registry_key: Mapped[str] = mapped_column(String(240), default="")
    registry_value: Mapped[str] = mapped_column(String(240), default="")
    status: Mapped[str] = mapped_column(String(40), default="open")
    deadline: Mapped[str] = mapped_column(String(40), default="")
    discovered_at: Mapped[str] = mapped_column(String(40), default="")
    verified_by: Mapped[str] = mapped_column(String(120), default="")
    verified_at: Mapped[str] = mapped_column(String(40), default="")


class ADIssue(Base):
    __tablename__ = "ad_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_type: Mapped[str] = mapped_column(String(80))
    username: Mapped[str] = mapped_column(String(120), default="")
    object_name: Mapped[str] = mapped_column(String(120), default="")
    domain_controller: Mapped[str] = mapped_column(String(120), default="")
    dc_status: Mapped[str] = mapped_column(String(40), default="")
    last_sync: Mapped[str] = mapped_column(String(40), default="")
    failed_partner: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(40), default="open")
    last_logon: Mapped[str] = mapped_column(String(40), default="")
    lockout_time: Mapped[str] = mapped_column(String(40), default="")
    last_modified: Mapped[str] = mapped_column(String(40), default="")
    source: Mapped[str] = mapped_column(String(120), default="")
    details: Mapped[str] = mapped_column(Text, default="")


class ADAction(Base):
    __tablename__ = "ad_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_type: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(120))
    actor: Mapped[str] = mapped_column(String(120))
    ticket_reference: Mapped[str] = mapped_column(String(120))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(40))


class VM(Base):
    __tablename__ = "vms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vm_name: Mapped[str] = mapped_column(String(120), index=True)
    power_state: Mapped[str] = mapped_column(String(40), default="poweredOn")
    host_cluster: Mapped[str] = mapped_column(String(120), default="")
    datastore: Mapped[str] = mapped_column(String(120), default="")
    vcpus: Mapped[int] = mapped_column(Integer, default=2)
    cpu_ready_percent: Mapped[float] = mapped_column(Float, default=0)
    memory_allocated_gb: Mapped[float] = mapped_column(Float, default=0)
    memory_active_gb: Mapped[float] = mapped_column(Float, default=0)
    ballooning: Mapped[bool] = mapped_column(Boolean, default=False)
    disk_provisioned_gb: Mapped[float] = mapped_column(Float, default=0)
    disk_used_gb: Mapped[float] = mapped_column(Float, default=0)
    datastore_free_percent: Mapped[float] = mapped_column(Float, default=100)
    tools_status: Mapped[str] = mapped_column(String(40), default="current")
    snapshot_name: Mapped[str] = mapped_column(String(120), default="")
    snapshot_size_gb: Mapped[float] = mapped_column(Float, default=0)
    snapshot_created: Mapped[str] = mapped_column(String(40), default="")


class Backup(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_name: Mapped[str] = mapped_column(String(120))
    protected_system: Mapped[str] = mapped_column(String(120), index=True)
    backup_type: Mapped[str] = mapped_column(String(40), default="incremental")
    sla_domain: Mapped[str] = mapped_column(String(80), default="Silver")
    last_successful_backup: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(40), default="success")
    next_scheduled_backup: Mapped[str] = mapped_column(String(40), default="")
    restore_test_date: Mapped[str] = mapped_column(String(40), default="")
    restore_test_result: Mapped[str] = mapped_column(String(40), default="")
    tested_by: Mapped[str] = mapped_column(String(120), default="")
    error_details: Mapped[str] = mapped_column(Text, default="")


class ComplianceSnapshot(Base):
    __tablename__ = "compliance_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    score: Mapped[float] = mapped_column(Float)
