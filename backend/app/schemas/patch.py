from pydantic import BaseModel, ConfigDict


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
