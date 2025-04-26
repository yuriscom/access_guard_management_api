import asyncio
import logging
from typing import List, Optional, Callable, Awaitable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMRole
from access_manager_api.schemas import IAMRoleCreate
from access_manager_api.schemas.role import IAMRoleUpdate

logger = logging.getLogger(__name__)
PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]


class IAMRoleService:
    def __init__(self, db: Session,
                 policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    async def create_role(self, role: IAMRoleCreate) -> IAMRole:
        db_role = IAMRole(
            scope=role.scope,
            app_id=role.app_id,
            role_name=role.role_name,
            description=role.description,
            synthetic=role.synthetic,
            synthetic_pattern=role.synthetic_pattern
        )

        try:
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_role.scope, db_role.app_id, self.db)
                )
            return db_role
        except IntegrityError:
            self.db.rollback()
            raise AlreadyExistsException(f"IAM role {role.role_name} already exists")
        except Exception as e:
            self.db.rollback()
            print(f"Unhandled error: {e}")
            raise UnknownException()

    def get_role_by_id(self, role_id: str) -> Optional[IAMRole]:
        return self.db.query(IAMRole).filter(IAMRole.id == role_id).first()

    def get_roles_by_scope_app(self, scope: str, app_id: Optional[str]) -> List[IAMRole]:
        query = self.db.query(IAMRole).filter(IAMRole.scope == scope)
        if app_id:
            query = query.filter(IAMRole.app_id == app_id)
        else:
            query = query.filter(IAMRole.app_id.is_(None))
        return query.all()

    async def update_role_by_id(self, role_id: str, role_data: IAMRoleUpdate) -> Optional[IAMRole]:
        db_role = self.get_role_by_id(role_id)
        return self.update_role(db_role, role_data)

    async def update_role(self, db_role: IAMRole, role_data: IAMRoleUpdate) -> Optional[IAMRole]:
        if not db_role:
            raise NotFoundException("Entry not found")

        for key, value in role_data.model_dump().items():
            setattr(db_role, key, value)
        try:
            self.db.commit()
            self.db.refresh(db_role)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_role.scope, db_role.app_id, self.db)
                )
        except Exception:
            self.db.rollback()
            logger.warning(f"Failed to update role. System said: {e}")
            raise UnknownException()
        return db_role

    async def delete_role(self, db_role: IAMRole):
        if not db_role:
            raise NotFoundException("Entry not found")

        try:
            self.db.delete(db_role)
            self.db.commit()
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(db_role.scope, db_role.app_id, self.db)
                )
        except Exception:
            self.db.rollback()
            logger.warning(f"Failed to delete role. System said: {e}")
            raise UnknownException()
