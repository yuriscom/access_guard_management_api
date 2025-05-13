from typing import List

from access_guard.authz.exceptions import PermissionDeniedError
from access_guard.authz.models.entities import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from access_manager_api.infra.error_handling import UnauthorizedException, NotFoundException, ValidationException
from access_manager_api.models import User as UserModel, IAMRole, IAMPermission
from access_manager_api.routes.dependencies import get_user
from access_manager_api.schemas.role_permissions import IAMRolePermission, IAMRolePermissionCreate
from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db
from access_manager_api.services.role_permissions import IAMRolePermissionsService
from access_manager_api.utils.utils import build_resource_path
from access_manager_api.utils.webhooks import send_policy_refresh_webhook

router = APIRouter(prefix="/iam/role-permissions", tags=["iam-role-permissions"])


@router.post("/", response_model=IAMRolePermission)
async def create_role_permission(
        payload: IAMRolePermissionCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db),
):
    # Step 1: Load role
    role = db.query(IAMRole).filter(IAMRole.id == payload.role_id).first()
    if not role:
        raise NotFoundException(f"Role with id {payload.role_id} not found")

    # Step 2: Load permission + resource
    permission = (
        db.query(IAMPermission)
            .options(joinedload(IAMPermission.resource))
            .filter(IAMPermission.id == payload.permission_id)
            .first()
    )
    if not permission:
        raise NotFoundException(f"Permission with id {payload.permission_id} not found")
    if not permission.resource:
        raise NotFoundException(f"Resource for permission {payload.permission_id} not found")

    # Step 3: Ensure app_id matches
    if role.app_id != permission.resource.app_id:
        raise ValidationException("Role and Permission belong to different apps")

    # Step 4: Enforce access
    try:
        resource_path = build_resource_path("iam", role.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    # Step 5: Proceed with creation
    service = IAMRolePermissionsService(db, policy_refresh_hook=send_policy_refresh_webhook)
    db_obj = await service.create_role_permission(payload)
    return IAMRolePermission.from_orm(db_obj)


@router.get("/{rp_id}", response_model=IAMRolePermission)
def read_role_permission(
        rp_id: str,
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
):
    service = IAMRolePermissionsService(db)
    db_obj = service.get_role_permission_by_id(rp_id)
    if not db_obj:
        raise NotFoundException(f"IAM role permission with id {rp_id} not found")

    app_id = db_obj.role.app_id if db_obj.role else (
        db_obj.permission.resource.app_id if db_obj.permission and db_obj.permission.resource else None
    )

    try:
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return IAMRolePermission.from_orm(db_obj)


@router.get("/role/{role_id}", response_model=List[IAMRolePermission])
def read_role_permissions_by_role(
        role_id: str,
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
):
    from access_manager_api.services.role import IAMRoleService
    role_service = IAMRoleService(db)
    db_role = role_service.get_role_by_id(role_id)
    if not db_role:
        raise NotFoundException(f"IAM role with id {role_id} not found")

    try:
        resource_path = build_resource_path("iam", db_role.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    service = IAMRolePermissionsService(db)
    return [IAMRolePermission.from_orm(rp) for rp in service.get_role_permissions_by_role_id(role_id)]


@router.delete("/{rp_id}", status_code=204)
async def delete_role_permission(
        rp_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db),
):
    service = IAMRolePermissionsService(db, policy_refresh_hook=send_policy_refresh_webhook)
    db_obj = service.get_role_permission_by_id(rp_id)
    if not db_obj:
        raise NotFoundException(f"IAM role permission with id {rp_id} not found")

    app_id = db_obj.role.app_id if db_obj.role else (
        db_obj.permission.resource.app_id if db_obj.permission and db_obj.permission.resource else None
    )

    try:
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    await service.delete_role_permission(db_obj)
