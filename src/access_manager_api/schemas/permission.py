from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from access_manager_api.schemas.resource import IAMResource


class IAMPermissionBase(BaseModel):
    resource_id: str
    action: str
    resource: Optional[IAMResource] = None  # <-- added field


class IAMPermissionCreate(IAMPermissionBase):
    pass


class IAMPermissionUpdate(BaseModel):
    action: Optional[str] = None

    class Config:
        extra = "forbid"


class IAMPermission(IAMPermissionBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            resource_id=str(obj.resource_id),
            action=obj.action,
            created_at=obj.created_at,
            resource=IAMResource.from_orm(obj.resource) if hasattr(obj, "resource") and obj.resource else None
        )

    class Config:
        from_attributes = True