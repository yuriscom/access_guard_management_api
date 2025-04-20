from pydantic import BaseModel
from datetime import datetime

class IAMPermissionBase(BaseModel):
    resource_id: str
    action: str

class IAMPermissionCreate(IAMPermissionBase):
    pass

class IAMPermission(IAMPermissionBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            resource_id=str(obj.resource_id),
            action=obj.action,
            created_at=obj.created_at
        )

    class Config:
        from_attributes = True 