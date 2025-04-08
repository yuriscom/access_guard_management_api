from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from ..models import IAMResource, IAMRole, IAMPermission, IAMRolePolicy, UserRole, User, IAMUserPolicy
from ..schemas import (
    IAMResourceCreate, IAMRoleCreate, IAMPermissionCreate, IAMUserPolicyCreate,
    IAMRolePolicyCreate, UserRoleCreate, UserAccess, Permission
)
from ..models.enums import Scope


def create_iam_resource(db: Session, resource: IAMResourceCreate) -> IAMResource:
    db_resource = IAMResource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

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

def get_user_access(
    db: Session,
    user_id: int,
    scope: str,
    app_id: Optional[int] = None
) -> Optional[UserAccess]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Get user's roles
    roles_query = db.query(IAMRole.role_name).join(UserRole).filter(
        UserRole.user_id == user.id,
        IAMRole.scope == scope
    )
    if app_id:
        roles_query = roles_query.filter(IAMRole.app_id == app_id)
    roles = roles_query.all()
    role_names = [role[0] for role in roles]

    # Get permissions for each role
    permissions: Dict[str, List[Permission]] = {}
    for role_name in role_names:
        role = db.query(IAMRole).filter(IAMRole.role_name == role_name).first()
        if role:
            role_permissions = (
                db.query(IAMPermission.action, IAMResource.resource_name, IAMRolePolicy.effect)
                .join(IAMRolePolicy, IAMRolePolicy.permission_id == IAMPermission.id)
                .join(IAMResource, IAMPermission.resource_id == IAMResource.id)
                .filter(IAMRolePolicy.role_id == role.id)
                .filter(IAMResource.scope == scope)
                .all()
            )
            
            for action, resource, effect in role_permissions:
                if resource not in permissions:
                    permissions[resource] = []
                # Check if this action already exists for this resource
                if not any(perm.action == action for perm in permissions[resource]):
                    permissions[resource].append(Permission(action=action, effect=effect))

    # Get direct user permissions
    user_permissions = (
        db.query(IAMPermission.action, IAMResource.resource_name, IAMUserPolicy.effect)
        .join(IAMUserPolicy, IAMUserPolicy.permission_id == IAMPermission.id)
        .join(IAMResource, IAMPermission.resource_id == IAMResource.id)
        .filter(IAMUserPolicy.user_id == user.id)
        .filter(IAMResource.scope == scope)
        .all()
    )

    # Merge user-specific permissions with role-based permissions
    for action, resource, effect in user_permissions:
        if resource not in permissions:
            permissions[resource] = []
        # Remove any existing permission for this action (from roles) and add the user-specific one
        permissions[resource] = [p for p in permissions[resource] if p.action != action]
        permissions[resource].append(Permission(action=action, effect=effect))

    return UserAccess(
        user_id=user.id,
        user_name=user.name,
        scope=scope,
        roles=role_names,
        permissions=permissions
    ) 