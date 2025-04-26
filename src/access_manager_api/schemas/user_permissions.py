from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from access_manager_api.schemas.common import PolicyEffect
from access_manager_api.schemas.permission import IAMPermission


class IAMUserPermissionBase(BaseModel):
    user_id: str
    permission_id: str
    effect: PolicyEffect = Field(default=PolicyEffect.ALLOW)


class IAMUserPermissionCreate(IAMUserPermissionBase):
    pass


class IAMUserPermissionUpdate(BaseModel):
    effect: Optional[str] = None

    class Config:
        extra = "forbid"


class IAMUserPermission(IAMUserPermissionBase):
    id: str
    created_at: datetime
    permission: Optional[IAMPermission] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            user_id=str(obj.user_id),
            permission_id=str(obj.permission_id),
            effect=obj.effect,
            created_at=obj.created_at,
            permission=IAMPermission.from_orm(obj.permission) if hasattr(obj,
                                                                         "permission") and obj.permission else None,
        )

    class Config:
        from_attributes = True
