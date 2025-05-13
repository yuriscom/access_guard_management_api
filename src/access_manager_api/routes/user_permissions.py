from collections import defaultdict
from typing import Dict, List

from access_guard.authz.exceptions import PermissionDeniedError
from access_guard.authz.models.entities import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from access_manager_api.infra.error_handling import UnauthorizedException, NotFoundException
from access_manager_api.models import IAMPermission, IAMUserPermission, User as UserModel
from access_manager_api.routes.dependencies import get_user
from access_manager_api.schemas.user_permissions import IAMUserPermission, IAMUserPermissionCreate
from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db
from access_manager_api.services.user_permissions import IAMUserPermissionsService
from access_manager_api.utils.utils import build_resource_path
from access_manager_api.utils.webhooks import send_policy_refresh_webhook

router = APIRouter(prefix="/iam/user-permissions", tags=["iam-user-permissions"])


@router.post("/", response_model=IAMUserPermission)
async def create_user_permission(
        payload: IAMUserPermissionCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db),
):
    # Step 1: Validate permission and its resource
    permission = (
        db.query(IAMPermission)
            .options(joinedload(IAMPermission.resource))
            .filter(IAMPermission.id == payload.permission_id)
            .first()
    )
    if not permission:
        raise NotFoundException(f"Permission {payload.permission_id} not found")
    if not permission.resource:
        raise NotFoundException("Associated resource not found")

    # Step 2: Check if user has access to app_id
    try:
        resource_path = build_resource_path("iam", permission.resource.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    service = IAMUserPermissionsService(db, policy_refresh_hook=send_policy_refresh_webhook)
    db_obj = await service.create_user_permission(payload)
    return IAMUserPermission.from_orm(db_obj)


@router.get("/{up_id}", response_model=IAMUserPermission)
def read_user_permission(
        up_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    service = IAMUserPermissionsService(db)
    db_obj = service.get_user_permission_by_id(up_id)
    if not db_obj:
        raise NotFoundException(f"IAM user permission with id {up_id} not found")

    try:
        app_id = db_obj.permission.resource.app_id
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return IAMUserPermission.from_orm(db_obj)


@router.get("/user/{user_id}", response_model=List[IAMUserPermission])
def read_user_permissions_by_user(
        user_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    service = IAMUserPermissionsService(db)
    user_permissions = service.get_user_permissions_by_user(user_id)

    grouped: Dict[str, List[IAMUserPermission]] = defaultdict(list)
    for up in user_permissions:
        if up.permission and up.permission.resource and up.permission.resource.app_id:
            app_id = str(up.permission.resource.app_id)
            grouped[app_id].append(up)

    result: List[IAMUserPermission] = []
    for app_id, policies in grouped.items():
        try:
            resource_path = build_resource_path("iam", app_id)
            access_guard_service.require_permission(User(id=user.email), resource_path, "read")
            result.extend(policies)
        except PermissionDeniedError:
            continue

    return [IAMUserPermission.from_orm(p) for p in result]


@router.delete("/{up_id}", status_code=204)
async def delete_user_permission(
        up_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    service = IAMUserPermissionsService(db, send_policy_refresh_webhook)
    db_obj = service.get_user_permission_by_id(up_id)
    if not db_obj:
        raise NotFoundException(f"IAM user permission with id {up_id} not found")

    try:
        app_id = db_obj.permission.resource.app_id
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    await service.delete_user_permission(db_obj)
