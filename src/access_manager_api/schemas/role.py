from pydantic import BaseModel
from typing import Optional
from ..models.enums import Scope
from datetime import datetime

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