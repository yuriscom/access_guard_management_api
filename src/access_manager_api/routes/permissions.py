from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.schemas import IAMPermission, IAMPermissionCreate
from access_manager_api.services import create_iam_permission
from access_manager_api.services.db import get_db

router = APIRouter(prefix="/iam/permissions", tags=["iam-permissions"])


@router.post("/", response_model=IAMPermission)
def create_permission(permission: IAMPermissionCreate, db: Session = Depends(get_db)):
    """Create a new IAM permission"""
    return create_iam_permission(db, permission)
