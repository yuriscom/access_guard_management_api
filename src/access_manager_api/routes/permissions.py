from typing import List

from access_guard.authz.exceptions import PermissionDeniedError
from access_guard.authz.models.entities import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import UnauthorizedException, NotFoundException
from access_manager_api.models import User as UserModel
from access_manager_api.routes.dependencies import get_user, build_resource_path
from access_manager_api.schemas.permission import IAMPermission, IAMPermissionCreate, IAMPermissionUpdate
from access_manager_api.services import IAMResourceService
from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db
from access_manager_api.services.permission import IAMPermissionService
from access_manager_api.utils.webhooks import send_policy_refresh_webhook

router = APIRouter(prefix="/iam/permissions", tags=["iam-permissions"])


@router.post("/", response_model=IAMPermission)
async def create_permission(
        permission: IAMPermissionCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db),
):
    from access_manager_api.services.resource import IAMResourceService

    # Step 1: Load the resource
    resource_service = IAMResourceService(db)
    resource = await resource_service.get_resource_by_id(permission.resource_id)
    if not resource:
        raise NotFoundException(f"IAM resource with id {permission.resource_id} not found")

    # Step 2: Check permission using the resource's app_id
    try:
        resource_path = build_resource_path("iam", resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    # Step 3: Create permission
    permission_service = IAMPermissionService(db, send_policy_refresh_webhook)
    db_permission = await permission_service.create_permission(permission)
    return IAMPermission.from_orm(db_permission)


@router.get("/{permission_id}", response_model=IAMPermission)
async def read_permission_by_id(
        permission_id: str,
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
):
    permission_service = IAMPermissionService(db)
    db_permission = permission_service.get_permission_by_id(permission_id)
    if not db_permission:
        raise NotFoundException(f"IAM permission with id {permission_id} not found")

    try:
        resource_path = build_resource_path("iam", db_permission.resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return IAMPermission.from_orm(db_permission)


@router.get("/resource/{resource_id}", response_model=List[IAMPermission])
async def read_permissions_by_resource(
        resource_id: str,
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
):
    resource_service = IAMResourceService(db)
    resource = await resource_service.get_resource_by_id(resource_id)
    if not resource:
        raise NotFoundException(f"Resource with id {resource_id} not found")

    try:
        resource_path = build_resource_path("iam", resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    permission_service = IAMPermissionService(db)
    return [IAMPermission.from_orm(p) for p in permission_service.get_permissions_by_resource(resource_id)]


@router.put("/{permission_id}", response_model=IAMPermission)
async def update_permission(
        permission_id: str,
        permission_data: IAMPermissionUpdate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db),
):
    permission_service = IAMPermissionService(db, send_policy_refresh_webhook)
    db_permission = permission_service.get_permission_by_id(permission_id)

    if not db_permission:
        raise NotFoundException(f"IAM permission with id {permission_id} not found")

    try:
        resource_path = build_resource_path("iam", db_permission.resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return await permission_service.update_permission(db_permission, permission_data)


@router.delete("/{permission_id}", status_code=204)
async def delete_permission(
        permission_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db),
):
    permission_service = IAMPermissionService(db, send_policy_refresh_webhook)
    db_permission = permission_service.get_permission_by_id(permission_id)
    if not db_permission:
        raise NotFoundException(f"IAM permission with id {permission_id} not found")

    try:
        resource_path = build_resource_path("iam", db_permission.resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    await permission_service.delete_permission(db_permission)
