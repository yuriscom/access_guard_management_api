from access_manager_api.schemas import user_policy, role_policy, common, user_role, role, permission, resource
from access_manager_api.schemas.access import UserAccess, PermissionCheck, PermissionsList, Permission
from access_manager_api.schemas.permission import IAMPermission, IAMPermissionCreate, IAMPermissionBase
from access_manager_api.schemas.resource import IAMResource, IAMResourceCreate, IAMResourceBase
from access_manager_api.schemas.role import IAMRole, IAMRoleCreate, IAMRoleBase
from access_manager_api.schemas.role_policy import IAMRolePolicy, IAMRolePolicyCreate, IAMRolePolicyBase
from access_manager_api.schemas.user_policy import IAMUserPolicy, IAMUserPolicyCreate, IAMUserPolicyBase
from access_manager_api.schemas.user_role import UserRole, UserRoleBase, UserRoleCreate

__all__ = [
    'IAMResource', 'IAMResourceCreate', 'IAMResourceBase',
    'IAMRole', 'IAMRoleCreate', 'IAMRoleBase',
    'IAMPermission', 'IAMPermissionCreate', 'IAMPermissionBase',
    'IAMRolePolicy', 'IAMRolePolicyCreate', 'IAMRolePolicyBase',
    'IAMUserPolicy', 'IAMUserPolicyCreate', 'IAMUserPolicyBase',
    'UserRole', 'UserAccess', 'UserRoleCreate', 'UserRoleBase', 'PermissionCheck', 'PermissionsList', "Permission"
]
