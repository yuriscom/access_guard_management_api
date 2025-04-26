from typing import List, Tuple

from access_guard.authz.exceptions import PermissionDeniedError
from access_guard.authz.models.entities import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import UnauthorizedException, NotFoundException
from access_manager_api.models import User as UserModel
from access_manager_api.routes.dependencies import get_user, build_resource_path, get_request_headers
from access_manager_api.schemas import IAMResource, IAMResourceCreate
from access_manager_api.schemas.resource import IAMResourceUpdate
from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db
from access_manager_api.services.resource import IAMResourceService
from access_manager_api.utils.webhooks import send_policy_refresh_webhook

router = APIRouter(prefix="/iam/resources", tags=["iam-resources"])


@router.post("/", response_model=IAMResource)
async def create_resource(
        resource: IAMResourceCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    try:
        resource_path = build_resource_path("iam", resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    resource_service = IAMResourceService(db, policy_refresh_hook=send_policy_refresh_webhook)
    db_resource = await resource_service.create_resource(resource)
    return IAMResource.from_orm(db_resource)


@router.get("/{resource_id}", response_model=IAMResource)
async def read_resource_by_id(
        resource_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    resource_service = IAMResourceService(db)
    resource = await resource_service.get_resource_by_id(resource_id)
    if not resource:
        raise NotFoundException(f"IAM resource with id {resource_id} not found")

    try:
        resource_path = build_resource_path("iam", resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return IAMResource.from_orm(resource)


@router.get("/", response_model=List[IAMResource])
async def read_resources_by_scope_app(
        headers: Tuple[str, int, str] = Depends(get_request_headers),
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    user_id, app_id, scope = headers
    try:
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    resource_service = IAMResourceService(db)
    resources = await resource_service.get_resources_by_scope_app(scope, app_id)
    return [IAMResource.from_orm(resource) for resource in resources]


@router.put("/{resource_id}", response_model=IAMResource)
async def update_resource(
        resource_id: str,
        resource_data: IAMResourceUpdate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    resource_service = IAMResourceService(db, policy_refresh_hook=send_policy_refresh_webhook)
    existing = await resource_service.get_resource_by_id(resource_id)
    if not existing:
        raise NotFoundException(f"IAM resource with id {resource_id} not found")

    try:
        # todo: check if SMC scope is needed, or it's ok to have APP here
        resource_path = build_resource_path("iam", {existing.app_id})
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return await resource_service.update_resource(existing, resource_data)


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
        resource_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    resource_service = IAMResourceService(db, policy_refresh_hook=send_policy_refresh_webhook)
    existing = await resource_service.get_resource_by_id(resource_id)
    if not existing:
        raise NotFoundException(f"IAM resource with id {resource_id} not found")

    try:
        resource_path = build_resource_path("iam", str(existing.app_id))
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    await resource_service.delete_resource(existing)
