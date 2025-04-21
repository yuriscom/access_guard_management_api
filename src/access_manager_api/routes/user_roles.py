from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from access_manager_api.schemas import UserRole, UserRoleCreate
from access_manager_api.services import create_user_role, delete_user_role
from access_manager_api.services.db import get_db

router = APIRouter(prefix="/iam/user-roles", tags=["iam-user-roles"])


@router.post("/", response_model=UserRole)
def create_user_role_assignment(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """Assign a role to a user"""
    try:
        db_user_role = create_user_role(db, user_role)
        return UserRole.from_orm(db_user_role)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_role_id}")
def remove_user_role(user_role_id: int, db: Session = Depends(get_db)):
    """Remove a role from a user"""
    try:
        delete_user_role(db, user_role_id)
        return {"message": "User role deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
