import asyncio
import logging
from typing import List, Optional, Callable, Awaitable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMPermission
from access_manager_api.schemas.permission import IAMPermissionCreate, IAMPermissionUpdate

logger = logging.getLogger(__name__)
PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]


class IAMPermissionService:
    def __init__(self, db: Session,
                 policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    async def create_permission(self, permission: IAMPermissionCreate, commit: bool = True) -> IAMPermission:
        db_permission = IAMPermission(
            resource_id=permission.resource_id,
            action=permission.action
        )

        self.db.add(db_permission)

        if commit:
            try:
                self.db.commit()
                self.db.refresh(db_permission)
                if self.policy_refresh_hook:
                    asyncio.create_task(
                        self.policy_refresh_hook(db_permission.resource.scope, db_permission.resource.app_id, self.db)
                    )
            except IntegrityError:
                self.db.rollback()
                raise AlreadyExistsException(f"Permission already exists {permission.action}")
            except Exception as e:
                self.db.rollback()
                print(f"Unhandled error: {e}")
                raise UnknownException()
        else:
            self.db.flush()
        return db_permission

    def get_permission_by_id(self, permission_id: str) -> Optional[IAMPermission]:
        # return self.db.query(IAMPermission).filter(IAMPermission.id == permission_id).first()
        return self.db.query(IAMPermission) \
            .options(joinedload(IAMPermission.resource)) \
            .filter(IAMPermission.id == permission_id) \
            .first()

    def get_permissions_by_resource(self, resource_id: str) -> List[IAMPermission]:
        return self.db.query(IAMPermission).filter(IAMPermission.resource_id == resource_id).all()

    def get_permissions_by_resource_and_actions(self, resource_id: str, action_names: List[str]) -> List[IAMPermission]:
        return self.db.query(IAMPermission).filter(
                    IAMPermission.resource_id == resource_id,
                    IAMPermission.action.in_(action_names)
                ).all()

    def update_permission_by_id(self, permission_id: str, permission: IAMPermissionUpdate) -> Optional[IAMPermission]:
        db_permission = self.get_permission_by_id(permission_id)
        if db_permission:
            for key, value in permission.model_dump().items():
                setattr(db_permission, key, value)
            try:
                self.db.commit()
                self.db.refresh(db_permission)
            except Exception:
                self.db.rollback()
                raise UnknownException()
        return db_permission

    def update_permission(self, db_permission: IAMPermission, permission_data: IAMPermissionUpdate) \
            -> Optional[IAMPermission]:
        if not db_permission:
            raise NotFoundException("Entry not found")

        for key, value in permission_data.model_dump().items():
            setattr(db_permission, key, value)
        try:
            self.db.commit()
            self.db.refresh(db_permission)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_permission.resource.scope, db_permission.resource.app_id, self.db)
                )
        except Exception as e:
            self.db.rollback()
            logger.warning(f"Failed to update permission. System said: {e}")
            raise UnknownException()
        return db_permission

    async def delete_permission(self, db_permission: IAMPermission):
        if not db_permission:
            raise NotFoundException("Entry not found")

        resource = db_permission.resource
        try:
            self.db.delete(db_permission)
            self.db.commit()
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(resource.scope, resource.app_id, self.db)
                )
        except Exception as e:
            self.db.rollback()
            logger.warning(f"Failed to delete permission. System said: {e}")
            raise UnknownException()
