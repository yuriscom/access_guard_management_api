from pydantic import BaseModel
from datetime import datetime

class UserRoleBase(BaseModel):
    user_id: int
    role_id: int

class UserRoleCreate(UserRoleBase):
    pass

class UserRole(UserRoleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 