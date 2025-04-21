from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from access_manager_api.models import IAMRole
from access_manager_api.schemas import IAMRoleCreate


class IAMRoleService:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role: IAMRoleCreate) -> IAMRole:
        db_role = IAMRole(id=str(uuid4()), **role.model_dump())
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def get_role(self, role_id: str) -> Optional[IAMRole]:
        return self.db.query(IAMRole).filter(IAMRole.id == role_id).first()

    def get_roles(self, skip: int = 0, limit: int = 100) -> List[IAMRole]:
        return self.db.query(IAMRole).offset(skip).limit(limit).all()

    def get_roles_by_app(self, app_id: str) -> List[IAMRole]:
        return self.db.query(IAMRole).filter(IAMRole.app_id == app_id).all()

    def update_role(self, role_id: str, role: IAMRoleCreate) -> Optional[IAMRole]:
        db_role = self.get_role(role_id)
        if db_role:
            for key, value in role.model_dump().items():
                setattr(db_role, key, value)
            self.db.commit()
            self.db.refresh(db_role)
        return db_role

    def delete_role(self, role_id: str) -> bool:
        db_role = self.get_role(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
            return True
        return False
