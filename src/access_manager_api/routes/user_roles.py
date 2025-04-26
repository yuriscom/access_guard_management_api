from collections import defaultdict
from typing import List, Dict

from access_guard.authz.exceptions import PermissionDeniedError
from access_guard.authz.models.entities import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import UnauthorizedException, NotFoundException
from access_manager_api.models import User as UserModel
from access_manager_api.routes.dependencies import get_db, get_user, build_resource_path
from access_manager_api.schemas.user_roles import UserRole, UserRoleCreate
from access_manager_api.services import IAMRoleService
from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.services.user_roles import IAMUserRolesService
from access_manager_api.utils.webhooks import send_policy_refresh_webhook

router = APIRouter(prefix="/iam/user-roles", tags=["iam-user-roles"])


@router.post("/", response_model=UserRole)
async def assign_user_role(
        payload: UserRoleCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    role_service = IAMRoleService(db)
    user_role_service = IAMUserRolesService(db, send_policy_refresh_webhook)

    # Step 1: Check if the role exists
    role = role_service.get_role_by_id(payload.role_id)
    if not role:
        raise NotFoundException(f"Role with id {payload.role_id} not found")

    # Step 2: Check access to the app associated with the role
    try:
        resource_path = build_resource_path("iam", role.app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    # Step 3: Assign the role
    db_obj = await user_role_service.create_user_role(payload)
    return UserRole.from_orm(db_obj)


@router.get("/{user_role_id}", response_model=UserRole)
def read_user_role_by_id(
        user_role_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    user_role_service = IAMUserRolesService(db)
    db_user_role = user_role_service.get_user_role_by_id(user_role_id)
    if not db_user_role:
        raise NotFoundException(f"IAM user role with id {user_role_id} not found")

    try:
        app_id = db_user_role.role.app_id
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "read")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return UserRole.from_orm(db_user_role)


@router.get("/user/{user_id}", response_model=List[UserRole])
def read_user_roles_by_user_id(
        user_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    user_role_service = IAMUserRolesService(db)
    user_roles = user_role_service.get_user_roles_by_user(user_id)

    # Group roles by app_id
    roles_by_app: Dict[str, List[UserRole]] = defaultdict(list)
    for ur in user_roles:
        if ur.role and ur.role.app_id:
            roles_by_app[str(ur.role.app_id)].append(ur)

    # Filter by access
    result: List[UserRole] = []
    for app_id, roles in roles_by_app.items():
        try:
            resource_path = build_resource_path("iam", app_id)
            access_guard_service.require_permission(User(id=user.email), resource_path, "read")
            result.extend(roles)
        except PermissionDeniedError:
            continue  # skip roles for app_id user doesn't have access to

    return [UserRole.from_orm(ur) for ur in result]


@router.delete("/{user_role_id}", status_code=204)
async def delete_user_role(
        user_role_id: str,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    user_role_service = IAMUserRolesService(db, send_policy_refresh_webhook)
    db_user_role = user_role_service.get_user_role_by_id(user_role_id)
    if not db_user_role:
        raise NotFoundException(f"IAM user role with id {user_role_id} not found")

    try:
        app_id = db_user_role.role.app_id
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(User(id=user.email), resource_path, "write")
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    await user_role_service.delete_user_role(db_user_role)
