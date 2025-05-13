import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from access_manager_api.models.enums import Scope


class IAMResourceBase(BaseModel):
    scope: Scope
    app_id: Optional[uuid.UUID] = None
    resource_name: str
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_data: Optional[Dict[str, Any]] = None


class IAMResourceCreate(IAMResourceBase):
    actions: Optional[List[str]] = []
    pass


class IAMResourceUpdate(BaseModel):
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


class IAMResource(IAMResourceBase):
    id: uuid.UUID
    created_at: datetime
    actions: List[str] = []

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            app_id=str(obj.app_id) if obj.app_id else None,
            scope=obj.scope,
            resource_name=obj.resource_name,
            description=obj.description,
            created_at=obj.created_at,
            actions=[p.action for p in obj.permissions] if hasattr(obj, 'permissions') else []
        )

    class Config:
        from_attributes = True


class IAMResourceResponse(BaseModel):
    id: uuid.UUID
    resource_name: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            resource_name=obj.resource_name,
            created_at=obj.created_at,
            actions=[p.action for p in obj.permissions] if hasattr(obj, 'permissions') else []
        )

    class Config:
        from_attributes = True
