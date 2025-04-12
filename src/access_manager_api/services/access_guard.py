import logging
from access_guard.authz import get_permissions_enforcer

from .db import get_engine
from ..config import settings

logger = logging.getLogger(__name__)


def get_access_guard_enforcer():
    """
    Get Access Guard Enforcer instance.
    
    Args:
        
    Returns:
        PermissionAdapter: A permissions adapter instance
    """
    return get_permissions_enforcer(settings.adapter, get_engine(), settings=settings)
