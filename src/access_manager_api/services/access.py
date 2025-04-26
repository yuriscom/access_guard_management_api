from typing import Optional, List, Dict
from typing import Set

from sqlalchemy.orm import Session

from access_manager_api.models import Scope
from access_manager_api.models import User
from access_manager_api.schemas import UserAccess, Permission
from access_manager_api.schemas.policies import PoliciesParams
from access_manager_api.services.policies import PoliciesService


def get_user_access(
        db: Session,
        user_id: str,
        scope: str,
        app_id: Optional[str] = None
) -> Optional[UserAccess]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    policies_service = PoliciesService(db)
    policies_params = PoliciesParams(scope=Scope.APP.name, app_id=app_id, user_id=user_id)
    policies_result = policies_service.get_policies(policies_params)

    resource_prefix = policies_result.get("resource_prefix", "")
    roles: List[str] = []
    user_roles: Set[str] = set()
    permissions: Dict[str, List[Permission]] = {}

    # Pass 1: g-policies (role assignment)
    for policy in policies_result["policies"]:
        if policy["ptype"] == "g":
            if policy["subject"] == user.email:
                role_path = policy["object"]
                role_name = extract_role_name(role_path, resource_prefix)
                roles.append(role_name)
                user_roles.add(role_path)

    # Pass 2: p-policies (permissions)
    for policy in policies_result["policies"]:
        if policy["ptype"] == "p":
            subject = policy["subject"]
            if subject == user.email or subject in user_roles:
                resource_path = policy["object"]
                action = policy.get("action", "*")
                effect = policy.get("effect", "allow")
                resource_name = extract_resource_name(resource_path, resource_prefix)

                if resource_name not in permissions:
                    permissions[resource_name] = []

                if not any(p.action == action for p in permissions[resource_name]):
                    permissions[resource_name].append(Permission(action=action, effect=effect))

    return UserAccess(
        user_id=user_id,
        user_email=user.email,
        scope=scope,
        roles=roles,
        permissions=permissions
    )


def extract_role_name(role_path: str, prefix: str) -> str:
    return role_path.removeprefix(prefix)


def extract_resource_name(resource_path: str, prefix: str) -> str:
    return resource_path.removeprefix(prefix)
