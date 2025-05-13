import asyncio
import logging
from typing import List, Optional, Callable, Awaitable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMUserRole
from access_manager_api.schemas.user_roles import UserRoleCreate

logger = logging.getLogger(__name__)
PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]


class IAMUserRolesService:
    def __init__(self, db: Session,
                 policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    # alias to create_user_role
    async def assign_user_to_role(self, user_id: UUID, role_id: UUID, commit: bool = True):
        return await self.create_user_role(UserRoleCreate(user_id=user_id, role_id=role_id), commit=commit)

    async def create_user_role(self, payload: UserRoleCreate, commit: bool = True) -> IAMUserRole:
        db_obj = IAMUserRole(
            user_id=payload.user_id,
            role_id=payload.role_id
        )

        self.db.add(db_obj)
        if commit:
            try:
                self.db.commit()
                self.db.refresh(db_obj)
                if self.policy_refresh_hook:
                    asyncio.create_task(
                        self.policy_refresh_hook(db_obj.role.scope, db_obj.role.app_id, self.db)
                    )
            except IntegrityError:
                self.db.rollback()
                raise AlreadyExistsException("User already assigned to this role")
            except Exception as e:
                self.db.rollback()
                print(f"Unhandled error: {e}")
                raise UnknownException()
        else:
            self.db.flush()
        return db_obj

    def get_user_role_by_id(self, user_role_id: str) -> Optional[IAMUserRole]:
        return (
            self.db.query(IAMUserRole)
                .options(joinedload(IAMUserRole.role))
                .filter(IAMUserRole.id == user_role_id)
                .first()
        )

    def get_user_roles_by_user(self, user_id: str, app_id: Optional[str] = None) -> List[IAMUserRole]:
        query = (
            self.db.query(IAMUserRole)
                .options(joinedload(IAMUserRole.role))
                .filter(
                IAMUserRole.user_id == user_id,
                IAMUserRole.role.has(app_id=app_id) if app_id else True
            )
        )

        return query.all()

    async def delete_user_role(self, db_obj: IAMUserRole, commit: bool = True):
        if not db_obj:
            raise NotFoundException("Entry not found")

        # Eager load before delete
        role = db_obj.role

        self.db.delete(db_obj)
        if commit:
            try:
                self.db.commit()
                if self.policy_refresh_hook:
                    asyncio.create_task(
                        self.policy_refresh_hook(role.scope, role.app_id, self.db)
                    )
            except Exception as e:
                self.db.rollback()
                logger.warning(f"Failed to delete user role. System said: {e}")
                raise UnknownException()
        else:
            self.db.flush()
