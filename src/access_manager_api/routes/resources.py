from typing import List, Tuple

from access_guard.authz.exceptions import PermissionDeniedError
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..services.access_guard import get_access_guard_enforcer
from ..services.db import get_db
from ..schemas import IAMResource, IAMResourceCreate
from ..services import create_iam_resource, operations
from ..models import User as UserModel
from ..routes.dependencies import get_user, build_resource_path, get_request_headers

router = APIRouter(prefix="/iam/resources", tags=["iam-resources"])


@router.post("/", response_model=IAMResource)
def create_resource(
        resource: IAMResourceCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):

    try:
        resource_path = build_resource_path(resource.scope.name, resource.app_id)
        access_guard_service.require_permission(user, f"SMC:{resource_path}:iam", "write")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    """Create a new IAM resource"""
    return create_iam_resource(db, resource)

@router.get("/{resource_id}", response_model=IAMResource)
def read_resource_by_id(
        resource_id: int,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):

    resource = operations.get_iam_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail=f"IAM resource with id {resource_id} not found")

    try:
        resource_path = build_resource_path(resource.scope.name, resource.app_id)
        access_guard_service.require_permission(user, f"SMC:{resource_path}:iam", "read")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return resource

@router.get("/", response_model=List[IAMResource])
def read_resources_by_scope_app(
        headers: Tuple[str, int, str] = Depends(get_request_headers),
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):
    user_id, app_id, scope = headers
    try:
        resource_path = build_resource_path(scope, app_id)
        access_guard_service.require_permission(user, f"SMC:{resource_path}:iam", "read")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return operations.get_iam_resources_by_scope_app(db, scope, app_id)

@router.put("/{resource_id}", response_model=IAMResource)
def update_resource(
        resource_id: int,
        resource_data: IAMResourceCreate,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):

    existing = operations.get_iam_resource_by_id(db, resource_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"IAM resource with id {resource_id} not found")

    try:
        resource_path = f"{existing.scope}:{existing.app_id}"
        access_guard_service.require_permission(user, f"SMC:{resource_path}:iam", "write")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return operations.update_iam_resource(db, existing, resource_data)


@router.delete("/{resource_id}", status_code=204)
def delete_resource(
        resource_id: int,
        user: UserModel = Depends(get_user),
        access_guard_service=Depends(get_access_guard_enforcer),
        db: Session = Depends(get_db)
):

    existing = operations.get_iam_resource_by_id(db, resource_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"IAM resource with id {resource_id} not found")

    try:
        resource_path = f"{existing.scope}:{existing.app_id}"
        access_guard_service.require_permission(user, f"SMC:{resource_path}:iam", "write")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    operations.delete_iam_resource(db, existing)
