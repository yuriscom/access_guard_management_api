import asyncio
import logging
from typing import List, Optional, Callable, Awaitable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMUserPermission
from access_manager_api.schemas.user_permissions import IAMUserPermissionCreate

logger = logging.getLogger(__name__)
PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]


class IAMUserPermissionsService:
    def __init__(self, db: Session,
                 policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    async def create_user_permission(self, payload: IAMUserPermissionCreate) -> IAMUserPermission:
        db_obj = IAMUserPermission(
            user_id=payload.user_id,
            permission_id=payload.permission_id,
            effect=payload.effect.value
        )

        try:
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_obj.permission.resource.scope, db_obj.permission.resource.app_id, self.db)
                )
            return db_obj
        except IntegrityError:
            self.db.rollback()
            raise AlreadyExistsException("User already assigned to this permission")
        except Exception:
            self.db.rollback()
            raise UnknownException()

    def get_user_permission_by_id(self, up_id: str) -> Optional[IAMUserPermission]:
        return (
            self.db.query(IAMUserPermission)
                .options(joinedload(IAMUserPermission.permission))
                .filter(IAMUserPermission.id == up_id)
                .first()
        )

    def get_user_permissions_by_user(self, user_id: str) -> List[IAMUserPermission]:
        return (
            self.db.query(IAMUserPermission)
                .options(joinedload(IAMUserPermission.permission))
                .filter(IAMUserPermission.user_id == user_id)
                .all()
        )

    async def delete_user_permission(self, db_obj: IAMUserPermission):
        if not db_obj:
            raise NotFoundException("Entry not found")

        # Eager load before commit
        permission = db_obj.permission
        resource = permission.resource

        try:
            self.db.delete(db_obj)
            self.db.commit()
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(resource.scope, resource.app_id, self.db)
                )
        except Exception:
            self.db.rollback()
            logger.warning(f"Failed to delete user permission. System said: {e}")
            raise UnknownException()
