from sqlalchemy.ext.declarative import declarative_base

from access_manager_api.models.app import App
from access_manager_api.models.enums import Scope
from access_manager_api.models.org import Org
from access_manager_api.models.org_apps import OrgApps
from access_manager_api.models.permission import IAMPermission
from access_manager_api.models.resource import IAMResource
from access_manager_api.models.role import IAMRole
from access_manager_api.models.role_policy import IAMRolePolicy
from access_manager_api.models.user import User
from access_manager_api.models.user_policy import IAMUserPolicy
from access_manager_api.models.user_role import UserRole

Base = declarative_base()
