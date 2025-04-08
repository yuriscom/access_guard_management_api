from pydantic import BaseModel
from datetime import datetime

class IAMPermissionBase(BaseModel):
    resource_id: int
    action: str

class IAMPermissionCreate(IAMPermissionBase):
    pass

class IAMPermission(IAMPermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 