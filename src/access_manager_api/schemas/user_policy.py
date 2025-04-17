from datetime import datetime

from pydantic import BaseModel, Field

from access_manager_api.schemas.common import PolicyEffect


class IAMUserPolicyBase(BaseModel):
    user_id: int
    permission_id: int
    effect: PolicyEffect = Field(default=PolicyEffect.ALLOW)


class IAMUserPolicyCreate(IAMUserPolicyBase):
    pass


class IAMUserPolicy(IAMUserPolicyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
