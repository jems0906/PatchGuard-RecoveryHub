from typing import Literal

from pydantic import BaseModel, ConfigDict


class ADActionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action_type: Literal["Account unlock", "Password reset", "Group membership change", "Computer object cleanup"]
    target: str
    actor: str
    ticket_reference: str
    details: str = ""
