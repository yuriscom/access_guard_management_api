from typing import Optional, Tuple
from uuid import UUID

from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from access_manager_api.infra.app_context import get_access_manager_app_id
from access_manager_api.models import User as UserModel, Scope
from access_manager_api.infra.database import get_db


def get_user(request: Request, db: Session = Depends(get_db)) -> UserModel:
    try:
        user_id = UUID(request.headers["user_id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid or missing user_id header")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


def get_request_headers(
        user_id: Optional[str] = Header(None, alias="user_id"),
        app_id: Optional[str] = Header(None, alias="app_id"),
        scope: Optional[str] = Header(None, alias="scope")
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract common request headers for IAM operations.
    """
    return user_id, app_id, scope
