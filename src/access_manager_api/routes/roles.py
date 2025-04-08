from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.db import get_db
from ..schemas import IAMRole, IAMRoleCreate
from ..services import create_iam_role

router = APIRouter(prefix="/iam/roles", tags=["iam-roles"])


@router.post("/", response_model=IAMRole)
def create_role(role: IAMRoleCreate, db: Session = Depends(get_db)):
    """Create a new IAM role"""
    return create_iam_role(db, role)
