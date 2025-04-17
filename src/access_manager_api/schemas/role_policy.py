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
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 