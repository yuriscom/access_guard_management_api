import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..models import User as UserModel, IAMResource as IAMResourceModel
from ..schemas import UserAccess
from ..services import get_user_access
from ..services.db import get_db
from ..services.access_guard import get_access_guard_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/iam/access", tags=["iam-access"])

@router.get("/check-permission")
async def check_permission_get(
    user_id: int = Query(..., description="User ID"),
    resource_id: int = Query(..., description="Resource ID"),
    action: str = Query(..., description="Action to check"),
    db: Session = Depends(get_db),
    permissions = Depends(get_access_guard_service)
):
    """Check permission using database IDs"""
    # Get user and resource names
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    resource = db.query(IAMResourceModel).filter(IAMResourceModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource with id {resource_id} not found")

    logger.debug(f"Checking permission for user {user.name} on resource {resource.resource_name} with action {action}")

    allowed = permissions.enforce(user.name, resource.get_policy_object(), action)
    logger.debug(f"Permission check result: {allowed}")
    
    return {
        "allowed": allowed,
        "user_id": user_id,
        "user_name": user.name,
        "resource_id": resource_id,
        "resource_name": resource.resource_name,
        "action": action
    }

@router.get("/user-access", response_model=UserAccess)
def get_user_access_info(
    user_id: int,
    scope: str,
    app_id: int = None,
    db: Session = Depends(get_db)
):
    """Get user access information including roles and permissions."""
    try:
        return get_user_access(db, user_id, scope, app_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/refresh")
async def refresh_policies(
    permissions = Depends(get_access_guard_service)
):
    """
    Refresh the in-memory policies from the database.
    Use this endpoint when policies have been updated and need to be reloaded.
    """
    permissions.refresh_policies()
    return {"message": "Policies refreshed successfully"}