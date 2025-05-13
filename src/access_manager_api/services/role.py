import asyncio
import logging
from typing import List, Optional, Callable, Awaitable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMRole, Scope
from access_manager_api.schemas import IAMRoleCreate, IAMResourceCreate, IAMRolePermissionCreate
from access_manager_api.schemas.role import IAMRoleUpdate
from access_manager_api.services import IAMResourceService, IAMPermissionService
from access_manager_api.services.role_permissions import IAMRolePermissionsService

logger = logging.getLogger(__name__)
PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]


class IAMRoleService:
    def __init__(self, db: Session,
                 policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    async def create_role(self, role: IAMRoleCreate, commit: bool = True) -> IAMRole:
        from access_manager_api.infra.reserved_roles import RESERVED_ROLES
        reserved = RESERVED_ROLES.get(role.role_name)
        if reserved:
            role = role.copy(update=reserved)

        db_role = IAMRole(
            scope=role.scope,
            app_id=role.app_id,
            role_name=role.role_name,
            description=role.description,
            synthetic=role.synthetic,
            synthetic_data=role.synthetic_data
        )

        self.db.add(db_role)

        if commit:
            try:
                self.db.commit()
                self.db.refresh(db_role)
                if self.policy_refresh_hook:
                    asyncio.create_task(
                        self.policy_refresh_hook(db_role.scope, db_role.app_id, self.db)
                    )
            except IntegrityError:
                self.db.rollback()
                raise AlreadyExistsException(f"IAM role {role.role_name} already exists")
            except Exception as e:
                self.db.rollback()
                print(f"Unhandled error: {e}")
                raise UnknownException()
        else:
            self.db.flush()

        return db_role

    async def create_or_get_role_with_resources(self, data: IAMRoleCreate) -> IAMRole:
        try:
            db_role = await self.create_role(data, commit=True)
        except (IntegrityError, AlreadyExistsException):
            self.db.rollback()
            db_role = self.get_role_by_name(
                scope=data.scope,
                app_id=data.app_id,
                role_name=data.role_name
            )
        if not db_role:
            raise NotFoundException(f"Failed to create or retrieve role {data.role_name}")

        if data.resources:
            resource_service = IAMResourceService(self.db)
            role_permission_service = IAMRolePermissionsService(self.db)
            permission_service = IAMPermissionService(self.db)

            for resource_name, actions_dict in data.resources.items():
                action_names = list(actions_dict.keys())

                ## Idempontently create the resource with the provided actions
                resource_input = IAMResourceCreate(
                    scope=data.scope,
                    app_id=data.app_id,
                    resource_name=resource_name,
                    actions=action_names
                )

                try:
                    resource = await resource_service.create_or_get_resource_with_actions(resource_input)
                except Exception as e:
                    self.db.rollback()
                    logger.warning(f"Failed to create or get resource {resource_name}: {e}")
                    continue
                ## Resource is fetched

                # Build a dict: action -> permission
                permissions = permission_service.get_permissions_by_resource_and_actions(resource.id, action_names);
                perm_by_action = {p.action: p for p in permissions}

                for action, effect in actions_dict.items():
                    permission = perm_by_action.get(action)
                    if not permission:
                        logger.warning(f"Permission '{action}' not found for resource '{resource_name}'.")
                        continue

                    try:
                        role_permission_input = IAMRolePermissionCreate(
                            role_id=db_role.id,
                            permission_id=permission.id,
                            effect=effect
                        )
                        await role_permission_service.create_role_permission(role_permission_input)
                    except Exception as e:
                        self.db.rollback()
                        logger.warning(f"Could not assign permission '{action}' on '{resource_name}': {e}")

        return db_role

    def get_role_by_id(self, role_id: str) -> Optional[IAMRole]:
        return self.db.query(IAMRole).filter(IAMRole.id == role_id).first()

    def get_role_by_name(self, role_name: str, scope: Scope, app_id: UUID = None) -> Optional[IAMRole]:
        return self.db.query(IAMRole).filter(
            IAMRole.role_name == role_name,
            IAMRole.scope == scope,
            IAMRole.app_id == app_id
        ).first()

    def get_roles_by_scope_app(self, scope: str, app_id: Optional[str]) -> List[IAMRole]:
        query = self.db.query(IAMRole).filter(IAMRole.scope == scope)
        if app_id:
            query = query.filter(IAMRole.app_id == app_id)
        else:
            query = query.filter(IAMRole.app_id.is_(None))
        return query.all()

    async def update_role_by_id(self, role_id: str, role_data: IAMRoleUpdate, commit: bool = True) -> Optional[IAMRole]:
        db_role = self.get_role_by_id(role_id)
        return self.update_role(db_role, role_data, commit)

    async def update_role(self, db_role: IAMRole, role_data: IAMRoleUpdate, commit: bool = True) -> Optional[IAMRole]:
        if not db_role:
            raise NotFoundException("Entry not found")

        for key, value in role_data.model_dump().items():
            setattr(db_role, key, value)

        if commit:
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
        else:
            self.db.flush()
        return db_role

    async def delete_role(self, db_role: IAMRole, commit: bool = True):
        if not db_role:
            raise NotFoundException("Entry not found")

        self.db.delete(db_role)
        if commit:
            try:
                self.db.commit()
                if self.policy_refresh_hook:
                    asyncio.create_task(
                        self.policy_refresh_hook(db_role.scope, db_role.app_id, self.db)
                    )
            except Exception as e:
                self.db.rollback()
                logger.warning(f"Failed to delete role. System said: {e}")
                raise UnknownException()
        else:
            self.db.flush()
