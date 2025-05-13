import logging

from access_guard.authz import get_permissions_enforcer
from access_guard.authz.loaders.policy_code_loader import PolicyCodeLoader
from access_guard.authz.loaders.policy_db_loader import PolicyDbLoader
from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams

from access_manager_api.infra.app_context import get_access_manager_app_id
from access_manager_api.infra.database import get_engine, get_db
from access_manager_api.models import Scope
from access_manager_api.providers.db_policies_provider import DBPoliciesProvider
from access_manager_api.providers.policy_query_provider import AccessManagementQueryProvider
from access_manager_api.providers.synthetic_policies_provider import load_synthetic_policies, SyntheticPoliciesProvider

logger = logging.getLogger(__name__)


def get_access_guard_enforcer():
    """
    Get Access Guard Enforcer instance.
    
    Args:
        
    Returns:
        PermissionAdapter: A permissions adapter instance
    """
    policy_loaders = [
        PolicyCodeLoader(SyntheticPoliciesProvider(next(get_db()))),
        PolicyCodeLoader(DBPoliciesProvider(next(get_db()))),
        PolicyDbLoader(AccessManagementQueryProvider(), get_engine()),
    ]

    params_dict = {
        "filter": {
            "policy_api_scope": Scope.SMC.name,
            "policy_api_appid": get_access_manager_app_id()
        }
    }
    params = PermissionsEnforcerParams(**params_dict)

    return get_permissions_enforcer(settings=params, policy_loaders=policy_loaders)
