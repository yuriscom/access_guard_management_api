from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.database import get_db
from access_manager_api.models import User as UserModel
from access_manager_api.routes.dependencies import get_user
from access_manager_api.schemas.product import ProductOnboard
from access_manager_api.services.product import onboard_product

router = APIRouter(prefix="/iam/products", tags=["iam-products"])


@router.post("/{app_id}/onboard", status_code=status.HTTP_201_CREATED)
async def onboard_product_route(
    app_id: UUID,
    request: ProductOnboard,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_user),
    access_guard_enforcer=Depends(get_access_guard_enforcer)
):
    """Onboard a new product into IAM (create built-in roles and assign users)"""
    await onboard_product(db, app_id, request, initiated_by=user)
    access_guard_enforcer.refresh_policies()

    return {"status": "success", "message": "Product onboarded successfully."}
