import asyncio
import logging
from typing import List, Optional, Callable, Awaitable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMRolePermission
from access_manager_api.schemas.role_permissions import IAMRolePermissionCreate, IAMRolePermissionUpdate

logger = logging.getLogger(__name__)
PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]


class IAMRolePermissionsService:
    def __init__(self, db: Session,
                 policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    async def create_role_permission(self, role_permission: IAMRolePermissionCreate) -> IAMRolePermission:
        db_obj = IAMRolePermission(
            role_id=role_permission.role_id,
            permission_id=role_permission.permission_id,
            effect=role_permission.effect.value
        )
        try:
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_obj.role.scope, db_obj.role.app_id, self.db)
                )
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            raise AlreadyExistsException("Role permission already exists")
        except Exception as e:
            self.db.rollback()
            print(f"Unhandled error: {e}")
            raise UnknownException()

    def get_role_permission_by_id(self, rp_id: str) -> Optional[IAMRolePermission]:
        return (
            self.db.query(IAMRolePermission)
                .options(joinedload(IAMRolePermission.role), joinedload(IAMRolePermission.permission))
                .filter(IAMRolePermission.id == rp_id)
                .first()
        )

    def get_role_permissions_by_role_id(self, role_id: str) -> List[IAMRolePermission]:
        return (
            self.db.query(IAMRolePermission)
                .options(joinedload(IAMRolePermission.role), joinedload(IAMRolePermission.permission))
                .filter(IAMRolePermission.role_id == role_id)
                .all()
        )

    async def update_role_permission_by_id(self, permission_id: str, data: IAMRolePermissionUpdate) \
            -> Optional[IAMRolePermission]:
        db_obj = self.get_role_permission_by_id(permission_id)
        return self.update_role_permission(db_obj, data)

    async def update_role_permission(self, db_obj: IAMRolePermission, data: IAMRolePermissionUpdate) \
            -> Optional[IAMRolePermission]:
        if not db_obj:
            raise NotFoundException("Entry not found")

        for key, value in data.model_dump().items():
            setattr(db_obj, key, value)
        try:
            self.db.commit()
            self.db.refresh(db_obj)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_obj.role.scope, db_obj.role.app_id, self.db)
                )
        except Exception:
            self.db.rollback()
            logger.warning(f"Failed to update role permission. System said: {e}")
            raise UnknownException()
        return db_obj

    async def delete_role_permission(self, db_obj: IAMRolePermission):
        if not db_obj:
            raise NotFoundException("Entry not found")
        role = db_obj.role
        try:
            self.db.delete(db_obj)
            self.db.commit()
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(role.scope, role.app_id, self.db)
                )
        except Exception:
            self.db.rollback()
            raise UnknownException()
