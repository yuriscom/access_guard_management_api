import logging
from access_guard.authz import get_permissions_enforcer
from access_guard.authz.models.enums import PolicyLoaderType
from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams

from .db import get_engine
from ..config import settings
from ..models import Scope
from ..providers.policy_query_provider import AccessManagementQueryProvider

logger = logging.getLogger(__name__)


def get_access_guard_enforcer():
    """
    Get Access Guard Enforcer instance.
    
    Args:
        
    Returns:
        PermissionAdapter: A permissions adapter instance
    """
    params_dict = {
        **settings.model_dump(),  # static settings from config
        "policy_loader_type": PolicyLoaderType.DB,
        "filter": {
            "policy_api_scope": Scope.SMC.name,
            "policy_api_appid": None
        }
    }

    params = PermissionsEnforcerParams(**params_dict)

    return get_permissions_enforcer(params, get_engine(), query_provider=AccessManagementQueryProvider())
