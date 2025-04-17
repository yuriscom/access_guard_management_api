from typing import Tuple

import jwt
from access_guard.authz.exceptions import PermissionDeniedError
from fastapi import APIRouter, Depends, HTTPException, Header

from access_manager_api.config import settings
from access_manager_api.models import User as UserModel
from access_manager_api.routes import dependencies
from access_manager_api.routes.dependencies import get_request_headers, get_user
from access_manager_api.schemas.policies import PoliciesParams
from access_manager_api.services.access_guard import get_access_guard_enforcer
from access_manager_api.services.policies import get_policies_service

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
        headers: Tuple[str, int, str] = Depends(get_request_headers),
        access_guard_service=Depends(get_access_guard_enforcer),
        policies_service=Depends(get_policies_service),
        user: UserModel = Depends(get_user)
):
    # Extract claims
    # user_id = jwt_claims["sub"]
    # app_id = jwt_claims.get("app_id")

    user_id, app_id, scope = headers

    # Construct the resource string
    resource_path = dependencies.build_resource_path("policies", app_id)

    # Enforce access
    try:
        access_guard_service.require_permission(user, resource_path, "read")
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
