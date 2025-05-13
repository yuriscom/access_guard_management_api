from access_manager_api.infra.constants import (
    RESOURCE_ADMIN,
    RESOURCE_IAM,
    RESOURCE_POLICIES,
    ROLE_IAM_MANAGER,
    ROLE_ORG_ADMIN,
    ROLE_PRODUCT_OWNER,
    ROLE_POLICY_READER,
)
from access_manager_api.models import Scope

RESERVED_ROLES = {
    ROLE_PRODUCT_OWNER: {
        "scope": Scope.APP,
        "synthetic": True,
        "synthetic_data": {
            "resource": RESOURCE_ADMIN,
            "actions": ["*"]
        }
    },
    ROLE_ORG_ADMIN: {
        "scope": Scope.APP,
        "synthetic": True,
        "synthetic_data": {
            "resource": RESOURCE_ADMIN,
            "actions": ["*"]
        }
    },
    ROLE_IAM_MANAGER: {
        "scope": Scope.APP,
        "synthetic": True,
        "synthetic_data": {
            "resource": RESOURCE_IAM,
            "actions": ["*"]
        }
    },
    ROLE_POLICY_READER: {
        "scope": Scope.APP,
        "synthetic": True,
        "synthetic_data": {
            "resource": RESOURCE_POLICIES,
            "actions": ["read"]
        }
    }
}
