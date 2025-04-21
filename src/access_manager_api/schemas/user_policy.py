from datetime import datetime

from pydantic import BaseModel, Field

from access_manager_api.schemas.common import PolicyEffect


class IAMUserPolicyBase(BaseModel):
    user_id: str
    permission_id: str
    effect: PolicyEffect = Field(default=PolicyEffect.ALLOW)


class IAMUserPolicyCreate(IAMUserPolicyBase):
    pass


class IAMUserPolicy(IAMUserPolicyBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            user_id=str(obj.user_id),
            permission_id=str(obj.permission_id),
            effect=obj.effect,
            created_at=obj.created_at
        )

    class Config:
        from_attributes = True
