from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from access_manager_api.schemas import IAMUserPolicy, IAMUserPolicyCreate
from access_manager_api.services import create_iam_user_policy, delete_iam_user_policy
from access_manager_api.services.db import get_db

router = APIRouter(prefix="/iam/user/policies", tags=["iam-policies"])


@router.post("/", response_model=IAMUserPolicy)
def create_policy(policy: IAMUserPolicyCreate, db: Session = Depends(get_db)):
    """Create a new IAM policy"""
    try:
        return create_iam_user_policy(db, policy)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{policy_id}")
def remove_policy(policy_id: int, db: Session = Depends(get_db)):
    """Delete an IAM policy"""
    try:
        delete_iam_user_policy(db, policy_id)
        return {"message": "Policy deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
