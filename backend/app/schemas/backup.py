from pydantic import BaseModel, ConfigDict


class BackupCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_name: str
    protected_system: str
    backup_type: str = "incremental"
    sla_domain: str = "Silver"
    last_successful_backup: str = ""
    status: str = "success"
    next_scheduled_backup: str = ""
    restore_test_date: str = ""
    restore_test_result: str = ""
    tested_by: str = ""
    error_details: str = ""
