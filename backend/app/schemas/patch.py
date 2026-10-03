from pydantic import BaseModel, ConfigDict, field_validator

APPROVAL_STATUSES = {"not approved", "approved", "declined"}
INSTALLATION_STATUSES = {"needed", "downloading", "installed", "failed", "reboot required"}
PATCH_CLASSIFICATIONS = {"critical", "security", "update rollup", "update"}


def _normalize_choice(value: str, allowed: set[str], field_name: str) -> str:
    normalized = value.strip().lower().replace("_", " ")
    if normalized not in allowed:
        raise ValueError(f"Unsupported {field_name}: {value}")
    return normalized


class PatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    kb_number: str = ""
    classification: str = "Security"
    approval_status: str = "not approved"
    target_group: str = ""
    asset_hostname: str = ""
    installation_status: str = "needed"
    wave: str = ""
    deployment_date: str = ""

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, value: str) -> str:
        return _normalize_choice(value, PATCH_CLASSIFICATIONS, "classification")

    @field_validator("approval_status")
    @classmethod
    def validate_approval_status(cls, value: str) -> str:
        return _normalize_choice(value, APPROVAL_STATUSES, "approval status")

    @field_validator("installation_status")
    @classmethod
    def validate_installation_status(cls, value: str) -> str:
        return _normalize_choice(value, INSTALLATION_STATUSES, "installation status")


class PatchUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = None
    kb_number: str | None = None
    classification: str | None = None
    approval_status: str | None = None
    target_group: str | None = None
    asset_hostname: str | None = None
    installation_status: str | None = None
    wave: str | None = None
    deployment_date: str | None = None

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, value: str | None) -> str | None:
        return _normalize_choice(value, PATCH_CLASSIFICATIONS, "classification") if value is not None else value

    @field_validator("approval_status")
    @classmethod
    def validate_approval_status(cls, value: str | None) -> str | None:
        return _normalize_choice(value, APPROVAL_STATUSES, "approval status") if value is not None else value

    @field_validator("installation_status")
    @classmethod
    def validate_installation_status(cls, value: str | None) -> str | None:
        return _normalize_choice(value, INSTALLATION_STATUSES, "installation status") if value is not None else value
