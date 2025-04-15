from typing import List, Optional, Set

from access_guard.authz import get_permissions_enforcer
from sqlalchemy.orm import Session

from ..mappers.model_mappers import mapUserToAccessGuardUser
from ..models import IAMResource, IAMRole, IAMPermission, IAMRolePolicy, UserRole, IAMUserPolicy, Scope
from ..schemas import (
    IAMResourceCreate, IAMRoleCreate, IAMPermissionCreate, IAMUserPolicyCreate,
    IAMRolePolicyCreate, UserRoleCreate
)

def create_iam_resource(db: Session, resource: IAMResourceCreate) -> IAMResource:
    db_resource = IAMResource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

def get_iam_resource_by_id(db: Session, resource_id: int) -> IAMResource:
    return db.query(IAMResource).filter(IAMResource.id == resource_id).first()

def get_iam_resources_by_scope_app(db: Session, scope: str, app_id: Optional[int]) -> List[IAMResource]:
    query = db.query(IAMResource).filter(IAMResource.scope == scope)

    if not app_id:
        query = query.filter(IAMResource.app_id.is_(None))
    else:
        query = query.filter(IAMResource.app_id == app_id)

    return query.all()

def update_iam_resource(
        db: Session,
        existing: IAMResource,
        data: IAMResourceCreate
) -> IAMResource:
    existing.resource_name = data.resource_name
    existing.scope = data.scope
    existing.app_id = data.app_id
    existing.description = data.description
    db.commit()
    db.refresh(existing)
    return existing

def delete_iam_resource(
        db: Session,
        resource: IAMResource
) -> None:
    db.delete(resource)
    db.commit()

def create_iam_role(db: Session, role: IAMRoleCreate) -> IAMRole:
    db_role = IAMRole(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_iam_permission(db: Session, permission: IAMPermissionCreate) -> IAMPermission:
    db_permission = IAMPermission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def create_iam_role_policy(db: Session, policy: IAMRolePolicyCreate) -> IAMRolePolicy:
    db_policy = IAMRolePolicy(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

def create_iam_user_policy(db: Session, policy: IAMUserPolicyCreate) -> IAMUserPolicy:
    db_policy = IAMUserPolicy(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

def create_user_role(db: Session, user_role: UserRoleCreate) -> UserRole:
    db_user_role = UserRole(**user_role.model_dump())
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

def delete_iam_role_policy(db: Session, policy_id: int) -> bool:
    db_policy = db.query(IAMRolePolicy).filter(IAMRolePolicy.id == policy_id).first()
    if db_policy:
        db.delete(db_policy)
        db.commit()
        return True
    return False

def delete_iam_user_policy(db: Session, policy_id: int) -> bool:
    db_policy = db.query(IAMUserPolicy).filter(IAMUserPolicy.id == policy_id).first()
    if db_policy:
        db.delete(db_policy)
        db.commit()
        return True
    return False

def delete_user_role(db: Session, user_role_id: int) -> bool:
    db_user_role = db.query(UserRole).filter(UserRole.id == user_role_id).first()
    if db_user_role:
        db.delete(db_user_role)
        db.commit()
        return True
    return False

from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams
from access_guard.authz.models.enums import PolicyLoaderType
from access_guard.authz.models.load_policy_result import LoadPolicyResult
from access_manager_api.schemas import UserAccess, Permission
from access_manager_api.models import User
from access_manager_api.providers.policy_query_provider import AccessManagementQueryProvider

def get_user_access(
        db: Session,
        user_id: int,
        scope: str,
        app_id: Optional[int] = None
) -> Optional[UserAccess]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Step 1: Build params for Access Guard
    enforcer_params = PermissionsEnforcerParams(
        policy_loader_type=PolicyLoaderType.DB,
        filter={
            "policy_api_scope": Scope(scope.lower()).name,
            "policy_api_appid": str(app_id) if app_id is not None else None,
            "policy_api_userid": str(user_id)
        }
    )

    # Step 2: Create enforcer instance with filter
    enforcer = get_permissions_enforcer(
        settings=enforcer_params,
        engine=db.bind,
        query_provider=AccessManagementQueryProvider(),
        new_instance=True
    )

    # Step 3: Access policies (from filtered loader)
    entity = mapUserToAccessGuardUser(user)
    policies_result: LoadPolicyResult = enforcer._enforcer.adapter.load_policy(enforcer._model, entity=entity,
                                                                               filter=enforcer._params.filter)

    roles: List[str] = []
    user_roles: Set[str] = set()
    permissions: Dict[str, List[Permission]] = {}

    # Pass 1: Process g policies → collect roles
    for policy in policies_result.policies:
        ptype = policy[0]

        if ptype == "g":
            _, sub, role_path = policy
            if sub == str(user_id):
                role_name = extract_role_name(role_path)
                roles.append(role_name)
                user_roles.add(role_path)

    # Pass 2: Process p policies → handle direct + role-based permissions
    for policy in policies_result.policies:
        ptype = policy[0]

        if ptype == "p":
            _, sub, obj, act, *rest = policy
            if sub == str(user_id) or sub in user_roles:
                resource = extract_resource_name(obj)
                effect = rest[0] if rest else "allow"

                if resource not in permissions:
                    permissions[resource] = []

                if not any(p.action == act for p in permissions[resource]):
                    permissions[resource].append(Permission(action=act, effect=effect))

    return UserAccess(
        user_id=user.id,
        user_name=user.name,
        scope=scope,
        roles=roles,
        permissions=permissions
    )

def extract_resource_name(resource_path: str) -> str:
    """Returns the last part of a resource path (e.g., SMC/1/policies → policies)."""
    return resource_path.strip("/").split("/")[-1]

def extract_role_name(role_path: str) -> str:
    """
    Extracts role name from full role path.
    Example: APP/1/Viewer → Viewer
    """
    return role_path.strip("/").split("/")[-1]
