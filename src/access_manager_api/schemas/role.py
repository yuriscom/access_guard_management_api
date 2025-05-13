from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, List, Any

from pydantic import BaseModel
from access_manager_api.models.enums import Scope
from access_manager_api.schemas.common import PolicyEffect


class IAMRoleBase(BaseModel):
    scope: Scope
    app_id: Optional[UUID] = None
    role_name: str
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_data: Optional[Dict[str, Any]] = None


class IAMRoleCreate(IAMRoleBase):
    resources: Optional[Dict[str, Dict[str, PolicyEffect]]] = None
    pass


class IAMRoleUpdate(BaseModel):
    description: Optional[str] = None
    synthetic: Optional[bool] = False
    synthetic_data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


class IAMRole(IAMRoleBase):
    id: UUID
    created_at: datetime
    resources: Dict[str, List[str]] = {}

    @classmethod
    def from_orm(cls, obj):

        resources_dict = {}

        if hasattr(obj, "role_permissions"):
            for rp in obj.role_permissions:
                if not rp.permission or not rp.permission.resource:
                    continue

                resource_name = rp.permission.resource.resource_name
                action = rp.permission.action

                if resource_name not in resources_dict:
                    resources_dict[resource_name] = []

                resources_dict[resource_name].append(action)

        return cls(
            id=str(obj.id),
            app_id=str(obj.app_id) if obj.app_id else None,
            scope=obj.scope,
            role_name=obj.role_name,
            description=obj.description,
            synthetic=obj.synthetic,
            synthetic_data=obj.synthetic_data,
            created_at=obj.created_at,
            resources=resources_dict
        )

    class Config:
        from_attributes = True
