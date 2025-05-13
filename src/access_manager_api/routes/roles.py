from typing import List

from access_guard.authz.exceptions import PermissionDeniedError
from access_guard.authz.models.entities import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db
from access_manager_api.infra.error_handling import (
    NotFoundException,
    UnauthorizedException,
)
from access_manager_api.models import User as UserModel
from access_manager_api.routes.dependencies import get_request_headers, get_user
from access_manager_api.schemas import IAMRole, IAMRoleCreate
from access_manager_api.schemas.role import IAMRoleUpdate
from access_manager_api.services.role import IAMRoleService
from access_manager_api.utils.utils import build_resource_path
from access_manager_api.utils.webhooks import send_policy_refresh_webhook

router = APIRouter(prefix="/iam/roles", tags=["iam-roles"])


@router.post("/", response_model=IAMRole)
async def create_role(
    role: IAMRoleCreate,
    user: UserModel = Depends(get_user),
    access_guard_service=Depends(get_access_guard_enforcer),
    db: Session = Depends(get_db),
):
    try:
        resource_path = build_resource_path("iam", role.app_id)
        access_guard_service.require_permission(
            User(id=user.email), resource_path, "write"
        )
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    role_service = IAMRoleService(db, send_policy_refresh_webhook)
    if role.resources:
        db_role = await role_service.create_or_get_role_with_resources(role)
    else:
        db_role = await role_service.create_role(role)
    return IAMRole.from_orm(db_role)


@router.get("/{role_id}", response_model=IAMRole)
def read_role(
    role_id: str,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_user),
    access_guard_service=Depends(get_access_guard_enforcer),
):
    role_service = IAMRoleService(db)
    db_role = role_service.get_role_by_id(role_id)
    if not db_role:
        raise NotFoundException(f"IAM role with id {role_id} not found")

    try:
        resource_path = build_resource_path("iam", db_role.app_id)
        access_guard_service.require_permission(
            User(id=user.email), resource_path, "read"
        )
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return IAMRole.from_orm(db_role)


@router.get("/", response_model=List[IAMRole])
def read_roles_by_scope_app(
    headers=Depends(get_request_headers),
    user: UserModel = Depends(get_user),
    access_guard_service=Depends(get_access_guard_enforcer),
    db: Session = Depends(get_db),
):
    _, app_id, scope = headers
    role_service = IAMRoleService(db)

    try:
        resource_path = build_resource_path("iam", app_id)
        access_guard_service.require_permission(
            User(id=user.email), resource_path, "read"
        )
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return [
        IAMRole.from_orm(r) for r in role_service.get_roles_by_scope_app(scope, app_id)
    ]


@router.put("/{role_id}", response_model=IAMRole)
async def update_role(
    role_id: str,
    role_data: IAMRoleUpdate,
    user: UserModel = Depends(get_user),
    access_guard_service=Depends(get_access_guard_enforcer),
    db: Session = Depends(get_db),
):
    role_service = IAMRoleService(db, send_policy_refresh_webhook)
    db_role = role_service.get_role_by_id(role_id)
    if not db_role:
        raise NotFoundException(f"IAM role with id {role_id} not found")

    try:
        resource_path = build_resource_path("iam", db_role.app_id)
        access_guard_service.require_permission(
            User(id=user.email), resource_path, "write"
        )
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    return await role_service.update_role(db_role, role_data)


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: str,
    user: UserModel = Depends(get_user),
    access_guard_service=Depends(get_access_guard_enforcer),
    db: Session = Depends(get_db),
):
    role_service = IAMRoleService(db, send_policy_refresh_webhook)
    db_role = role_service.get_role_by_id(role_id)
    if not db_role:
        raise NotFoundException(f"IAM role with id {role_id} not found")

    try:
        resource_path = build_resource_path("iam", db_role.app_id)
        access_guard_service.require_permission(
            User(id=user.email), resource_path, "write"
        )
    except PermissionDeniedError as e:
        raise UnauthorizedException(str(e))

    await role_service.delete_role(db_role)
