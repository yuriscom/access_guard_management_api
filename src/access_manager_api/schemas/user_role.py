from pydantic import BaseModel
from datetime import datetime

class UserRoleBase(BaseModel):
    user_id: str
    role_id: str

class UserRoleCreate(UserRoleBase):
    pass

class UserRole(UserRoleBase):
    id: str
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            user_id=str(obj.user_id),
            role_id=str(obj.role_id),
            created_at=obj.created_at
        )

    class Config:
        from_attributes = True 