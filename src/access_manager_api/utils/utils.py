from typing import Optional
from uuid import UUID

from access_manager_api.infra.app_context import get_access_manager_app_id
from access_manager_api.models.enums import Scope


def ensure_uuid(value):
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        return UUID(value)
    raise ValueError("Invalid UUID value")


def build_resource_path(resource_name: str, app_id: Optional[str], scope: Scope = Scope.SMC) -> str:
    """
    Builds resource path string from resource name and app_id.
    Default scope is SMC (platform-level), but can be overridden to APP.
    """
    if scope == Scope.APP:
        return f"{Scope.APP.name}/{app_id}/{resource_name}"
    return f"{Scope.SMC.name}/{get_access_manager_app_id()}/{Scope.APP.name}/{app_id}/{resource_name}"


def build_role_path(
    role_name: str,
    app_id: Optional[str] = None,
    org_id: Optional[str] = None,
    scope: Scope = Scope.SMC
) -> str:
    """
    Builds a standardized role path string based on scope.

    Examples:
    - SMC: SMC/{AM_ID}/APP/{app_id}/{role_name}
    - APP: APP/{app_id}/{role_name}
    - ORG: SMC/{AM_ID}/ORG/{org_id}/{role_name}
    """

    if scope == Scope.APP:
        return f"{Scope.APP.name}/{app_id}/{role_name}"

    if scope == Scope.ORG:
        return f"{Scope.SMC.name}/{get_access_manager_app_id()}/{Scope.ORG.name}/{org_id}/{role_name}"

    # Default: SMC-level
    return f"{Scope.SMC.name}/{get_access_manager_app_id()}/{Scope.APP.name}/{app_id}/{role_name}"

