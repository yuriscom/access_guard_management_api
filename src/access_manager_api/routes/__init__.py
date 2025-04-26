from fastapi import APIRouter

from access_manager_api.routes import (
    user_permissions,
    role_permissions,
    user_roles,
    permissions,
    roles,
    resources,
    access,
    policies
)

# router = APIRouter(prefix="/api/v1")
router = APIRouter(prefix="")

# Include all IAM routes
router.include_router(user_permissions.router)
router.include_router(role_permissions.router)
router.include_router(user_roles.router)
router.include_router(permissions.router)
router.include_router(roles.router)
router.include_router(resources.router)
router.include_router(access.router)
router.include_router(policies.router)
