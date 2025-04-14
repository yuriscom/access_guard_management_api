import logging
from access_guard.authz import get_permissions_enforcer
from access_guard.authz.models.enums import PolicyLoaderType
from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams

from .db import get_engine, get_db
from ..config import settings
from ..models import Scope
from ..providers.policy_query_provider import AccessManagementQueryProvider
from ..providers.synthetic_policies_provider import load_smc_superadmin_policies

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

    # Lazy policy provider to inject current db session
    def synthetic_policy_provider():
        db_session = next(get_db())
        try:
            return load_smc_superadmin_policies(db_session)
        finally:
            db_session.close()


    return get_permissions_enforcer(params, get_engine(), query_provider=AccessManagementQueryProvider()
                                    , synthetic_policy_provider=synthetic_policy_provider)
