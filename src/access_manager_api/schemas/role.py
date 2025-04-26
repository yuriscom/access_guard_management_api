from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from access_manager_api.models.enums import Scope


class IAMRoleBase(BaseModel):
    scope: Scope
    app_id: Optional[str] = None
    role_name: str
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_pattern: Optional[str] = None


class IAMRoleCreate(IAMRoleBase):
    pass


class IAMRoleUpdate(BaseModel):
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_pattern: Optional[str] = None

    class Config:
        extra = "forbid"


class IAMRole(IAMRoleBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            app_id=str(obj.app_id) if obj.app_id else None,
            scope=obj.scope,
            role_name=obj.role_name,
            description=obj.description,
            synthetic=obj.synthetic,
            synthetic_pattern=obj.synthetic_pattern,
            created_at=obj.created_at,
        )

    class Config:
        from_attributes = True
