import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from access_manager_api.infra.error_handling import UnknownException
from access_manager_api.schemas import UserAccess
from access_manager_api.services import get_user_access
from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/iam/access", tags=["iam-access"])


@router.get("/user-access", response_model=UserAccess)
def get_user_access_info(
        user_id: str,
        scope: str,
        app_id: str = None,
        db: Session = Depends(get_db)
):
    try:
        return get_user_access(db, user_id, scope, app_id)
    except Exception as e:
        raise UnknownException(str(e))


@router.post("/refresh")
async def refresh_policies(
        access_guard_enforcer=Depends(get_access_guard_enforcer)
):
    """
    Refresh the in-memory policies from the database.
    Use this endpoint when policies have been updated and need to be reloaded.
    """
    access_guard_enforcer.refresh_policies()
    return {"message": "Policies refreshed successfully"}
