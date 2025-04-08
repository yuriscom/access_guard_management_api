from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.db import get_db
from ..schemas import IAMRolePolicy, IAMRolePolicyCreate
from ..services import create_iam_role_policy, delete_iam_role_policy

router = APIRouter(prefix="/iam/role/policies", tags=["iam-policies"])


@router.post("/", response_model=IAMRolePolicy)
def create_policy(policy: IAMRolePolicyCreate, db: Session = Depends(get_db)):
    """Create a new IAM policy"""
    try:
        return create_iam_role_policy(db, policy)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{policy_id}")
def remove_policy(policy_id: int, db: Session = Depends(get_db)):
    """Delete an IAM policy"""
    try:
        delete_iam_role_policy(db, policy_id)
        return {"message": "Policy deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
