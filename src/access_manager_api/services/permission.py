from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from access_manager_api.models import IAMPermission
from access_manager_api.schemas import IAMPermissionCreate


class IAMPermissionService:
    def __init__(self, db: Session):
        self.db = db

    def create_permission(self, permission: IAMPermissionCreate) -> IAMPermission:
        db_permission = IAMPermission(id=str(uuid4()), **permission.model_dump())
        self.db.add(db_permission)
        self.db.commit()
        self.db.refresh(db_permission)
        return db_permission

    def get_permission(self, permission_id: str) -> Optional[IAMPermission]:
        return self.db.query(IAMPermission).filter(IAMPermission.id == permission_id).first()

    def get_permissions(self, skip: int = 0, limit: int = 100) -> List[IAMPermission]:
        return self.db.query(IAMPermission).offset(skip).limit(limit).all()

    def get_permissions_by_resource(self, resource_id: str) -> List[IAMPermission]:
        return self.db.query(IAMPermission).filter(IAMPermission.resource_id == resource_id).all()

    def update_permission(self, permission_id: str, permission: IAMPermissionCreate) -> Optional[IAMPermission]:
        db_permission = self.get_permission(permission_id)
        if db_permission:
            for key, value in permission.model_dump().items():
                setattr(db_permission, key, value)
            self.db.commit()
            self.db.refresh(db_permission)
        return db_permission

    def delete_permission(self, permission_id: str) -> bool:
        db_permission = self.get_permission(permission_id)
        if db_permission:
            self.db.delete(db_permission)
            self.db.commit()
            return True
        return False
