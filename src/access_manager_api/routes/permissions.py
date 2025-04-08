from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.db import get_db
from ..schemas import IAMPermission, IAMPermissionCreate
from ..services import create_iam_permission

router = APIRouter(prefix="/iam/permissions", tags=["iam-permissions"])


@router.post("/", response_model=IAMPermission)
def create_permission(permission: IAMPermissionCreate, db: Session = Depends(get_db)):
    """Create a new IAM permission"""
    return create_iam_permission(db, permission)
