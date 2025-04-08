from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import UserRole
from ..schemas import UserRoleCreate

class UserRoleService:
    def __init__(self, db: Session):
        self.db = db

    def create_user_role(self, user_role: UserRoleCreate) -> UserRole:
        db_user_role = UserRole(**user_role.model_dump())
        self.db.add(db_user_role)
        self.db.commit()
        self.db.refresh(db_user_role)
        return db_user_role

    def get_user_role(self, user_role_id: int) -> Optional[UserRole]:
        return self.db.query(UserRole).filter(UserRole.id == user_role_id).first()

    def get_user_roles(self, skip: int = 0, limit: int = 100) -> List[UserRole]:
        return self.db.query(UserRole).offset(skip).limit(limit).all()

    def get_user_roles_by_user(self, user_id: int) -> List[UserRole]:
        return self.db.query(UserRole).filter(UserRole.user_id == user_id).all()

    def get_user_roles_by_role(self, role_id: int) -> List[UserRole]:
        return self.db.query(UserRole).filter(UserRole.role_id == role_id).all()

    def update_user_role(self, user_role_id: int, user_role: UserRoleCreate) -> Optional[UserRole]:
        db_user_role = self.get_user_role(user_role_id)
        if db_user_role:
            for key, value in user_role.model_dump().items():
                setattr(db_user_role, key, value)
            self.db.commit()
            self.db.refresh(db_user_role)
        return db_user_role

    def delete_user_role(self, user_role_id: int) -> bool:
        db_user_role = self.get_user_role(user_role_id)
        if db_user_role:
            self.db.delete(db_user_role)
            self.db.commit()
            return True
        return False 