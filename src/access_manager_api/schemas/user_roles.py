from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import uuid
from access_manager_api.schemas.role import IAMRole


class UserRoleBase(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    role_id: Optional[uuid.UUID] = None

    class Config:
        extra = "forbid"


class UserRole(UserRoleBase):
    id: uuid.UUID
    created_at: datetime
    role: Optional[IAMRole] = None  # Only return role object, not user

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            user_id=str(obj.user_id),
            role_id=str(obj.role_id),
            created_at=obj.created_at,
            role=IAMRole.from_orm(obj.role) if hasattr(obj, "role") and obj.role else None
        )

    class Config:
        from_attributes = True
