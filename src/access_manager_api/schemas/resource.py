from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from access_manager_api.models.enums import Scope


class IAMResourceBase(BaseModel):
    scope: Scope
    app_id: Optional[str] = None
    resource_name: str
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_pattern: Optional[str] = None


class IAMResourceCreate(IAMResourceBase):
    pass


class IAMResourceUpdate(BaseModel):
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_pattern: Optional[str] = None

    class Config:
        extra = "forbid"


class IAMResource(IAMResourceBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            app_id=str(obj.app_id) if obj.app_id else None,
            scope=obj.scope,
            resource_name=obj.resource_name,
            description=obj.description,
            created_at=obj.created_at
        )

    class Config:
        from_attributes = True


class IAMResourceResponse(BaseModel):
    id: str
    resource_name: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            resource_name=obj.resource_name,
            created_at=obj.created_at
        )

    class Config:
        from_attributes = True
