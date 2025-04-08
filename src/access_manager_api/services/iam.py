import logging
from access_guard import adapters

from .db import get_engine
from ..config import settings

logger = logging.getLogger(__name__)


def get_access_guard_service():
    """
    Get a permissions service instance.
    
    Args:
        
    Returns:
        PermissionAdapter: A permissions adapter instance
    """
    return adapters.factory.get_permission_adapter(settings.adapter, get_engine(), settings=settings)
