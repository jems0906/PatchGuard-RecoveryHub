from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hostname: str
    os_version: str = ""
    role: str = "Server"
    ip_address: str = ""
    domain: str = ""
    forest: str = ""
    site: str = ""
    fsmo_roles: str = ""
    last_boot: str = ""
    asset_type: str = "Server"
    app_name: str = ""
    service_status: str = ""
    backup_policy: str = ""
