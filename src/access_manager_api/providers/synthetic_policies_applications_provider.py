from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from access_manager_api.infra import constants
from access_manager_api.infra.app_context import get_access_manager_app_id
from access_manager_api.models import Scope
from access_manager_api.models import User, Org, OrgApps, IAMUserRole, IAMRole


# === Public Facade ===
def load_synthetic_policies(db: Session, app_id: UUID) -> List[Tuple[str, ...]]:
    policies: List[Tuple[str, ...]] = []

    policies += synthetic_app_policies_for_org_admin(db, app_id)

    return policies


# === Synthetic Policy Hooks ===
def synthetic_app_policies_for_org_admin(db: Session, app_id: UUID) -> List[Tuple[str, ...]]:
    """
    For the given app_id, find users with OrgAdmin role from organizations that are linked
    to this app (via org_apps) with is_owner=False. These users can assign users to roles, etc.
    """
    access_manager_app_id = get_access_manager_app_id()

    query = db.query(User.email.label("user_id"))\
        .join(Org, Org.id == User.org_id)\
        .join(OrgApps, OrgApps.org_id == Org.id)\
        .join(IAMUserRole, IAMUserRole.user_id == User.id)\
        .join(IAMRole, IAMRole.id == IAMUserRole.role_id)\
        .filter(
        OrgApps.app_id == app_id,
        OrgApps.is_owner == True,
        User.role == constants.ROLE_USER_ADMIN,
        IAMRole.role_name == constants.ROLE_ORG_ADMIN,
        IAMRole.synthetic == True, # generic SMC-level OrgAdmin
        IAMRole.scope == Scope.SMC.name, # generic SMC-level OrgAdmin
        IAMRole.app_id == access_manager_app_id  # generic SMC-level OrgAdmin
        )

    rows = query.all()

    policies: List[Tuple[str, ...]] = []
    for row in rows:
        role_subject = f"{Scope.APP.name}/{app_id}/{constants.ROLE_ORG_ADMIN}"
        resource = f"{Scope.APP.name}/{app_id}/*"

        policies.append(("p", role_subject, resource, "*", "allow"))
        policies.append(("g", str(row.user_id), role_subject))

    return policies
