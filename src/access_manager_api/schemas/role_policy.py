from datetime import datetime

from pydantic import BaseModel, Field

from access_manager_api.schemas.common import PolicyEffect


class IAMRolePolicyBase(BaseModel):
    role_id: int
    permission_id: int
    effect: PolicyEffect = Field(default=PolicyEffect.ALLOW)

class IAMRolePolicyCreate(IAMRolePolicyBase):
    pass

class IAMRolePolicy(IAMRolePolicyBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            role_id=str(obj.role_id),
            permission_id=str(obj.permission_id),
            effect=obj.effect,
            created_at=obj.created_at
        )

    class Config:
        from_attributes = True 