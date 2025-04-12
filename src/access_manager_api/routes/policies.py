import jwt
from access_guard.adapters import PermissionDeniedError
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..config import settings
from ..schemas.policies import PoliciesParams
from ..services.access_guard import get_access_guard_enforcer
from ..services.policies import get_policies_service
from ..services.db import get_db
from ..models import User as UserModel, IAMResource as IAMResourceModel

router = APIRouter(prefix="/iam")

async def validate_jwt(authorization: str = Header(...)) -> dict:
    try:
        token = authorization.replace("Bearer ", "")

        if settings.development_mode:
            # In development mode, just decode without validation
            decoded = jwt.decode(token, options={"verify_signature": False})
        else:
            # In production, validate the token
            decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])

        # Validate required claims
        required_claims = ["sub", "roles"]
        for claim in required_claims:
            if claim not in decoded:
                raise HTTPException(status_code=401, detail=f"Missing required claim: {claim}")

        return decoded
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/policies")
async def get_policies(
    # jwt_claims: dict = Depends(validate_jwt),
    app_id: str = Header(..., alias="app_id", description="Application ID"),
    user_id: str = Header(..., alias="user_id", description="Application Client ID"),
    scope: str = Header(..., alias="scope", description="Application Scope"),
    access_guard_service = Depends(get_access_guard_enforcer),
    policies_service = Depends(get_policies_service),
    db: Session = Depends(get_db)
):
    # Extract claims
    # user_id = jwt_claims["sub"]
    # app_id = jwt_claims.get("app_id")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    # Construct the resource string
    resource = f"SMC:{app_id}:policies"

    # Enforce access
    try:
        access_guard_service.require_permission(user.name, resource, "read")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Create policies params
    params = PoliciesParams(
        user_id=user_id,
        scope="APP" if app_id else "SMC",
        app_id=app_id
    )

    # If access granted, fetch policies
    policies = policies_service.get_policies(params)
    return policies 