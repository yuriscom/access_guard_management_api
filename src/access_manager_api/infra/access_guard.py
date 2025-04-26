import logging

from access_guard.authz import get_permissions_enforcer
from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams

from access_manager_api.infra.app_context import get_access_manager_app_id
from access_manager_api.infra.config import settings
from access_manager_api.models import Scope
from access_manager_api.providers.policy_query_provider import AccessManagementQueryProvider
from access_manager_api.providers.synthetic_policies_provider import load_synthetic_policies
from access_manager_api.infra.database import get_engine, get_db

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
        "policy_loader_type": settings.AccessManager.policy_loader_type,
        "filter": {
            "policy_api_scope": Scope.SMC.name,
            "policy_api_appid": get_access_manager_app_id()
        }
    }

    params = PermissionsEnforcerParams(**params_dict)

    # Lazy policy provider to inject current db session
    def synthetic_policy_provider():
        db_session = next(get_db())
        try:
            return load_synthetic_policies(db_session)
        finally:
            db_session.close()

    return get_permissions_enforcer(params, get_engine(), query_provider=AccessManagementQueryProvider()
                                    , synthetic_policy_provider=synthetic_policy_provider)
