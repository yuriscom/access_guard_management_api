import asyncio
import logging
from typing import List, Optional, Callable, Awaitable
from uuid import UUID

from access_manager_api.services import IAMPermissionService
from access_manager_api.utils import utils

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import AlreadyExistsException, UnknownException, NotFoundException
from access_manager_api.models import IAMResource, Scope
from access_manager_api.schemas import IAMResourceCreate, IAMPermissionCreate
from access_manager_api.schemas.resource import IAMResourceUpdate

PolicyRefreshHookType = Callable[[str, int, Session], Awaitable[None]]
logger = logging.getLogger(__name__)


class IAMResourceService:
    def __init__(self, db: Session
                 , policy_refresh_hook: Optional[PolicyRefreshHookType] = None):
        self.db = db
        self.policy_refresh_hook = policy_refresh_hook

    async def create_resource(self, resource: IAMResourceCreate, commit: bool = True) -> IAMResource:
        db_resource = IAMResource(
            scope=resource.scope,
            app_id=utils.ensure_uuid(resource.app_id) if resource.app_id else None,
            resource_name=resource.resource_name,
            description=resource.description,
            synthetic=resource.synthetic,
            synthetic_data=resource.synthetic_data
        )

        self.db.add(db_resource)

        if commit:
            try:
                self.db.commit()
                self.db.refresh(db_resource)
                if self.policy_refresh_hook:
                    asyncio.create_task(self.policy_refresh_hook(db_resource.scope, db_resource.app_id, self.db))
            except IntegrityError as e:
                self.db.rollback()
                raise AlreadyExistsException(f"IAM resource {resource.resource_name} already exists ")
            except Exception as e:
                self.db.rollback()
                print(f"Unhandled error: {e}")
                raise UnknownException()
        else:
            self.db.flush()
        return db_resource

    async def create_or_get_resource_with_actions(self, data: IAMResourceCreate) -> IAMResource:
        try:
            # Try to create resource (may raise if exists)
            resource = await self.create_resource(data, commit=False)
        except IntegrityError:
            self.db.rollback()
            resource = await self.get_resource_by_name(
                scope=data.scope,
                app_id=data.app_id,
                resource_name=data.resource_name
            )
        if not resource:
            raise NotFoundException(f"Failed to create or retrieve resource {data.resource_name}")

        # Handle actions
        if data.actions:
            permission_service = IAMPermissionService(self.db)
            for action in data.actions:
                try:
                    await permission_service.create_permission(
                        IAMPermissionCreate(resource_id=resource.id, action=action),
                        commit=False)
                except:
                    self.db.rollback()
                    logger.warning(
                        f"Could not assign action '{action}' to resource '{resource.resource_name}' "
                        f"(ID: {resource.id}) — likely already assigned."
                    )

        try:
            self.db.commit()
            self.db.refresh(resource)
            if self.policy_refresh_hook:
                asyncio.create_task(self.policy_refresh_hook(resource.scope, resource.app_id, self.db))
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unhandled error during commit: {e}")
            raise UnknownException()

        return resource

    async def get_resource_by_id(self, resource_id: int) -> Optional[IAMResource]:
        return self.db.query(IAMResource).filter(IAMResource.id == resource_id).first()

    async def get_resource_by_name(self, resource_name: str, scope: Scope, app_id: UUID = None) \
            -> Optional[IAMResource]:
        query = self.db.query(IAMResource).filter(
            IAMResource.resource_name == resource_name,
            IAMResource.scope == scope,
            IAMResource.app_id == app_id,
        )
        return query.first()

    async def get_resources_by_scope_app(self, scope: str, app_id: Optional[str]) -> List[IAMResource]:
        query = self.db.query(IAMResource).filter(IAMResource.scope == scope)

        if not app_id:
            query = query.filter(IAMResource.app_id.is_(None))
        else:
            query = query.filter(IAMResource.app_id == app_id)

        return query.all()

    async def get_resources(self, skip: int = 0, limit: int = 100) -> List[IAMResource]:
        return self.db.query(IAMResource).offset(skip).limit(limit).all()

    async def get_resources_by_app(self, app_id: int) -> List[IAMResource]:
        return self.db.query(IAMResource).filter(IAMResource.app_id == app_id).all()

    async def update_resource_by_id(self, resource_id: str, resource: IAMResourceUpdate) -> Optional[IAMResource]:
        db_resource = await self.get_resource_by_id(resource_id)
        return self.update_resource(db_resource, resource)

    async def update_resource(self, db_resource: IAMResource, resource: IAMResourceUpdate) -> Optional[IAMResource]:
        if not db_resource:
            raise NotFoundException("Resource not found")

        for key, value in resource.model_dump().items():
            setattr(db_resource, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_resource)
            if self.policy_refresh_hook:
                asyncio.create_task(
                    self.policy_refresh_hook(resource.scope, resource.app_id, self.db)
                )
        except Exception as e:
            self.db.rollback()
            logger.warning(f"Failed to update resource. System said: {e}")
            raise UnknownException()

        return db_resource

    async def delete_resource(self, resource: IAMResource) -> bool:
        if not resource:
            raise NotFoundException("Resource not found")

        try:
            self.db.delete(resource)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.warning(f"Failed to delete resource. System said: {e}")
            raise UnknownException()

        if self.policy_refresh_hook:
            asyncio.create_task(
                self.policy_refresh_hook(resource.scope, resource.app_id, self.db)
            )

        return True
