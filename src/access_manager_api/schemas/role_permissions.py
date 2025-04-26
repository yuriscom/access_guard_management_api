from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from access_manager_api.schemas.common import PolicyEffect
from access_manager_api.schemas.permission import IAMPermission
from access_manager_api.schemas.role import IAMRole


class IAMRolePermissionBase(BaseModel):
    role_id: str
    permission_id: str
    effect: PolicyEffect = Field(default=PolicyEffect.ALLOW)


class IAMRolePermissionCreate(IAMRolePermissionBase):
    pass


class IAMRolePermissionUpdate(BaseModel):
    effect: Optional[PolicyEffect] = None

    class Config:
        extra = "forbid"


class IAMRolePermission(IAMRolePermissionBase):
    id: str
    created_at: datetime
    role: Optional[IAMRole] = None
    permission: Optional[IAMPermission] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            role_id=str(obj.role_id),
            permission_id=str(obj.permission_id),
            effect=obj.effect,
            created_at=obj.created_at,
            role=IAMRole.from_orm(obj.role) if hasattr(obj, "role") and obj.role else None,
            permission=IAMPermission.from_orm(obj.permission) if hasattr(obj, "permission") and obj.permission else None
        )

    class Config:
        from_attributes = True