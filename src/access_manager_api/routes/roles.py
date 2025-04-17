from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.schemas import IAMRole, IAMRoleCreate
from access_manager_api.services import create_iam_role
from access_manager_api.services.db import get_db

router = APIRouter(prefix="/iam/roles", tags=["iam-roles"])


@router.post("/", response_model=IAMRole)
def create_role(role: IAMRoleCreate, db: Session = Depends(get_db)):
    """Create a new IAM role"""
    return create_iam_role(db, role)
