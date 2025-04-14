from typing import Optional, Tuple
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from ..services.db import get_db
from ..models import User as UserModel


def build_resource_path(scope: str, app_id: Optional[int]) -> str:
    """
    Builds resource path string from scope and app_id.
    Example:
        build_resource_path("SMC", None) -> "SMC"
        build_resource_path("APP", 1) -> "APP:1"
    """
    return f"{scope}/" if app_id is None else f"{scope}/{app_id}"


def get_user(
    user_id: str = Header(..., alias="user_id"),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency to load user from user_id header.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


def get_request_headers(
    user_id: Optional[str] = Header(None, alias="user_id"),
    app_id: Optional[int] = Header(None, alias="app_id"),
    scope: Optional[str] = Header(None, alias="scope")
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    Extract common request headers for IAM operations.
    """
    return user_id, app_id, scope
