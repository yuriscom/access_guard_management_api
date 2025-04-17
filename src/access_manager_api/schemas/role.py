from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from access_manager_api.models.enums import Scope


class IAMRoleBase(BaseModel):
    scope: Scope
    app_id: Optional[int] = None
    role_name: str
    description: Optional[str] = None


class IAMRoleCreate(IAMRoleBase):
    pass


class IAMRole(IAMRoleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
