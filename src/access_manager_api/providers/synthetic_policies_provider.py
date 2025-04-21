from collections import defaultdict
from typing import List, Tuple, Optional, Dict
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from access_manager_api import constants
from access_manager_api.app_context import get_access_manager_app_id
from access_manager_api.models import Scope

# Which roles OrgAdmin inherits (resource mapping comes from DB)
ORG_ADMIN_INHERITS = [
    constants.ROLE_IAM_MANAGER,
    constants.ROLE_BILLING_VIEWER,
    constants.ROLE_REPORTING_USER,
]

# Will be filled by get_policies_from_synthetic_roles
_ROLE_RESOURCE_PATTERN_CACHE: Dict[str, str] = {}


def load_synthetic_policies(session: Session) -> List[Tuple[str, ...]]:
    return get_policies_from_synthetic_roles(session)


def get_policies_from_synthetic_roles(db: Session) -> List[Tuple[str, ...]]:
    global _ROLE_RESOURCE_PATTERN_CACHE
    access_manager_app_id = get_access_manager_app_id()

    # Cache: role_name -> synthetic_pattern
    _ROLE_RESOURCE_PATTERN_CACHE = {
        row.role_name: row.synthetic_pattern
        for row in db.execute(text("""
            SELECT role_name, synthetic_pattern
            FROM iam_roles
            WHERE app_id = :app_id AND synthetic = true
        """), {
            "app_id": access_manager_app_id
        }).fetchall()
    }

    sql = text("""
        SELECT 
            u.id AS user_id,
            a.id AS app_id,
            ir.role_name,
            ir.synthetic_pattern,
            oa.is_owner
        FROM users u
        JOIN orgs o ON o.id = u.org_id
        JOIN org_apps oa ON oa.org_id = o.id
        JOIN apps a ON a.id = oa.app_id
        JOIN user_roles ur ON ur.user_id = u.id
        JOIN iam_roles ir ON ir.id = ur.role_id
        WHERE 
            u.role = :admin_user_role
            AND ir.synthetic = true
            AND ir.scope = :scope
            AND ir.app_id = :app_id
    """)
    rows = db.execute(
        sql,
        {
            "scope": Scope.SMC.name,
            "app_id": access_manager_app_id,
            "admin_user_role": constants.ROLE_USER_ADMIN,
        },
    ).fetchall()

    grouped: defaultdict[Tuple[str, UUID, Optional[str], bool], List[UUID]] = defaultdict(list)
    for row in rows:
        if row.role_name in [constants.ROLE_SUPERADMIN, constants.ROLE_AM_ADMIN]:
            if str(row.app_id) != access_manager_app_id:
                continue
        key = (row.role_name, row.app_id, row.synthetic_pattern, row.is_owner)
        grouped[key].append(row.user_id)

    policies: List[Tuple[str, ...]] = []
    for (role_name, app_id, pattern, is_owner), user_ids in grouped.items():
        handler = ROLE_HANDLERS.get(role_name)
        if handler:
            handler(policies, role_name, app_id, pattern, user_ids, is_owner, access_manager_app_id)
    return policies


# === Role Handlers ===

def handle_iam_manager_role(policies, role_name, app_id, pattern, user_ids, is_owner, access_manager_app_id):
    role_subject = f"{Scope.SMC.name}/{access_manager_app_id}/{role_name}/{Scope.APP.name}/{app_id}"
    resource = _resolve_pattern(pattern, role_subject, access_manager_app_id, app_id)
    actions = ["read", "write"]

    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_policy_reader_role(policies, role_name, app_id, pattern, user_ids, is_owner, access_manager_app_id):
    role_subject = f"{Scope.SMC.name}/{access_manager_app_id}/{role_name}/{Scope.APP.name}/{app_id}"
    resource = _resolve_pattern(pattern, role_subject, access_manager_app_id, app_id)
    actions = ["read"]

    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_am_admin_role(policies, role_name, app_id, pattern, user_ids, is_owner, access_manager_app_id):
    role_subject = f"{Scope.SMC.name}/{access_manager_app_id}/{role_name}/{Scope.APP.name}/{app_id}"
    resource = f"{Scope.SMC.name}/{access_manager_app_id}/*"
    actions = ["*"]

    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_superadmin_role(policies, role_name, app_id, pattern, user_ids, is_owner, access_manager_app_id):
    role_subject = f"{Scope.SMC.name}/{access_manager_app_id}/{role_name}/{Scope.APP.name}/{app_id}"
    resource = f"{Scope.SMC.name}/*"
    actions = ["*"]

    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_org_admin_role(policies, role_name, app_id, pattern, user_ids, is_owner, access_manager_app_id):
    if not is_owner:
        return  # Skip if the org is not the product owner

    org_admin_subject = f"{Scope.SMC.name}/{access_manager_app_id}/{role_name}/{Scope.APP.name}/{app_id}"

    for inherited_role in ORG_ADMIN_INHERITS:
        # Load resource name for inherited role from DB pattern cache
        pattern_row = _ROLE_RESOURCE_PATTERN_CACHE.get(inherited_role)
        if not pattern_row:
            continue  # Could raise/log an error if missing pattern

        inherited_subject = f"{Scope.SMC.name}/{access_manager_app_id}/{inherited_role}/{Scope.APP.name}/{app_id}"
        resource = f"{Scope.SMC.name}/{access_manager_app_id}/{pattern_row}/{Scope.APP.name}/{app_id}"

        policies.append(("p", inherited_subject, resource, "*", "allow"))
        policies.append(("g", org_admin_subject, inherited_subject))

    for user_id in user_ids:
        policies.append(("g", str(user_id), org_admin_subject))


# === Role Handler Registry ===

ROLE_HANDLERS: Dict[str, callable] = {
    constants.ROLE_IAM_MANAGER: handle_iam_manager_role,
    constants.ROLE_POLICY_READER: handle_policy_reader_role,
    constants.ROLE_AM_ADMIN: handle_am_admin_role,
    constants.ROLE_SUPERADMIN: handle_superadmin_role,
    constants.ROLE_ORG_ADMIN: handle_org_admin_role,
}


# === Utility Helpers ===

def _append_policies(policies, role_subject, resource, actions, user_ids):
    for action in actions:
        policies.append(("p", role_subject, resource, action, "allow"))
    for user_id in user_ids:
        policies.append(("g", str(user_id), role_subject))


def _resolve_pattern(pattern: Optional[str], fallback_resource: str, access_manager_app_id: str, app_id: UUID) -> str:
    if not pattern:
        return fallback_resource
    return f"{Scope.SMC.name}/{access_manager_app_id}/{pattern}/{Scope.APP.name}/{str(app_id)}"
