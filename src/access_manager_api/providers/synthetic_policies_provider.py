from collections import defaultdict
from typing import Callable, Dict, List, Optional, Any
from uuid import UUID

from access_guard.authz.loaders.casbin_policy_provider import CasbinPolicyProvider
from access_guard.authz.models.casbin_policy import CasbinPolicy
from sqlalchemy import text
from sqlalchemy.orm import Session

from access_manager_api.infra.app_context import get_access_manager_app_id
from access_manager_api.infra.constants import (
    ROLE_AM_ADMIN,
    ROLE_IAM_MANAGER,
    ROLE_POLICY_READER,
    ROLE_SUPERADMIN, ROLE_PRODUCT_OWNER, ROLE_ORG_ADMIN, ROLE_IAM_VIEWER,
)
from access_manager_api.models import Scope
from access_manager_api.schemas.common import PolicyEffect
from access_manager_api.utils.utils import build_resource_path, build_role_path

# Role hierarchy
INHERITS: Dict[str, List[str]] = {
    ROLE_ORG_ADMIN: [
        ROLE_IAM_VIEWER
    ]
}
# Will be filled by create_role_inheritance_cache
INHERITED_ROLES_MAP: Dict[str, Dict[str, Any]] = None


class SyntheticPoliciesProvider(CasbinPolicyProvider):
    def __init__(self, db: Session):
        self.db = db

    def get_policies(self, filter: Dict[str, Any]) -> List[CasbinPolicy]:
        return load_synthetic_policies(self.db)


def load_synthetic_policies(db: Session) -> List[CasbinPolicy]:
    policies: List[CasbinPolicy] = []

    if not INHERITED_ROLES_MAP:
        create_role_inheritance_cache(db)

    load_am_synthetic_roles(db, policies)
    load_app_synthetic_roles(db, policies)
    load_org_admin_roles(db, policies)

    return policies


def create_role_inheritance_cache(db: Session):
    global INHERITED_ROLES_MAP

    roles_set = _get_unique_inherited_set()

    inheritance_sql = text("""
            SELECT role_name, synthetic_data
            FROM iam_roles
            WHERE synthetic = TRUE
              AND role_name = ANY(:role_names)
        """)
    inheritance_rows = db.execute(inheritance_sql, {"role_names": roles_set}).fetchall()
    INHERITED_ROLES_MAP = {
        row.role_name: row.synthetic_data or {} for row in inheritance_rows
    }


def load_app_synthetic_roles(db: Session, policies: List[CasbinPolicy]):
    APP_ROLE_HANDLERS: Dict[str, Callable] = {
        ROLE_IAM_MANAGER: handle_app_scoped_role,
        ROLE_POLICY_READER: handle_app_scoped_role,
        ROLE_PRODUCT_OWNER: handle_app_scoped_role,
    }

    sql = """
    SELECT r.id, r.app_id, r.role_name, r.synthetic_data, ur.user_id, u.email
    FROM iam_roles r
    JOIN iam_user_roles ur ON ur.role_id = r.id
    JOIN users u ON u.id = ur.user_id
    WHERE r.synthetic = TRUE
      AND r.scope = 'APP'
      AND r.role_name IN :role_names
    """
    rows = db.execute(text(sql), {"role_names": tuple(APP_ROLE_HANDLERS.keys())}).fetchall()

    grouped = defaultdict(list)
    for row in rows:
        role_name = row.role_name
        app_id = row.app_id
        synthetic_resource = row.synthetic_data.get("resource", None)
        synthetic_actions = tuple(row.synthetic_data.get("actions", []))
        user_email = row.email
        grouped_key = (role_name, app_id, synthetic_resource, synthetic_actions)
        grouped[grouped_key].append(user_email)

    for (role_name, app_id, synthetic_resource, synthetic_actions), user_ids in grouped.items():
        handler = APP_ROLE_HANDLERS.get(role_name)
        if handler:
            handler(
                policies,
                role_name,
                app_id,
                synthetic_resource,
                synthetic_actions,
                user_ids,
            )


def load_am_synthetic_roles(
        db: Session, policies: List[CasbinPolicy]
):
    AM_ROLE_HANDLERS: Dict[str, Callable] = {
        ROLE_AM_ADMIN: handle_am_admin_role,
        ROLE_SUPERADMIN: handle_superadmin_role,
    }

    sql = """
    SELECT r.id, r.app_id, r.role_name, r.synthetic_data, ur.user_id, u.email
    FROM iam_roles r
    JOIN iam_user_roles ur ON ur.role_id = r.id
    JOIN users u ON u.id = ur.user_id
    WHERE r.synthetic = TRUE
      AND r.scope = 'SMC'
      AND r.app_id = :access_manager_app_id
      AND r.role_name IN :role_names
    """
    rows = db.execute(
        text(sql),
        {
            "role_names": tuple(AM_ROLE_HANDLERS.keys()),
            "access_manager_app_id": get_access_manager_app_id(),
        },
    ).fetchall()

    grouped = defaultdict(list)
    for row in rows:
        role_name = row.role_name
        app_id = row.app_id
        synthetic_resource = row.synthetic_data.get("resource", None)
        synthetic_actions = tuple(row.synthetic_data.get("actions", []))
        user_email = row.email
        grouped_key = (role_name, app_id, synthetic_resource, synthetic_actions)
        grouped[grouped_key].append(user_email)

    for (role_name, app_id, synthetic_resource, synthetic_actions), user_ids in grouped.items():
        handler = AM_ROLE_HANDLERS.get(role_name)
        if handler:
            handler(
                policies,
                role_name,
                user_ids
            )


def load_org_admin_roles(db: Session, policies: List[CasbinPolicy]):
    sql = text("""
        SELECT r.role_name, r.app_id, r.scope, u.email, r.org_id, oa.app_id AS linked_app_id
        FROM iam_roles r
        JOIN iam_user_roles ur ON ur.role_id = r.id
        JOIN users u ON u.id = ur.user_id
        JOIN org_apps oa ON r.org_id = oa.org_id
        WHERE r.synthetic = TRUE
          AND r.scope = 'SMC'
          AND r.role_name = :role_name
    """)
    rows = db.execute(sql, {"role_name": ROLE_ORG_ADMIN}).fetchall()

    grouped = defaultdict(lambda: {"user_ids": set(), "app_ids": set()})
    for row in rows:
        key = (row.role_name, row.app_id, row.scope, row.org_id)
        grouped[key]["user_ids"].add(row.email)
        grouped[key]["app_ids"].add(row.linked_app_id)

    for (role_name, app_id, scope, org_id), data in grouped.items():
        handle_org_admin_role(
            policies=policies,
            role_name=role_name,
            app_id=app_id,
            scope=scope,
            org_id=org_id,
            user_ids=list(data["user_ids"]),
            linked_app_ids=list(data["app_ids"]),
        )

    return policies


# === Role Handlers ===

def handle_app_scoped_role(policies, role_name, app_id, synthetic_resource, synthetic_actions, user_ids):
    role_subject = build_role_path(role_name=role_name, app_id=app_id)
    resource = _resolve_resource_pattern(synthetic_resource, role_subject, app_id)
    actions = synthetic_actions or ["*"]
    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_am_admin_role(policies, role_name, user_ids):
    role_subject = f"{Scope.SMC.name}/{get_access_manager_app_id()}/{role_name}"
    resource = f"{Scope.SMC.name}/{get_access_manager_app_id()}/*"
    actions = ["*"]
    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_superadmin_role(policies, role_name, user_ids):
    role_subject = f"{Scope.SMC.name}/{role_name}"
    resource = f"{Scope.SMC.name}/*"
    actions = ["*"]
    _append_policies(policies, role_subject, resource, actions, user_ids)


def handle_org_admin_role(
        policies: List[CasbinPolicy],
        role_name: str,
        app_id: UUID,
        scope: str,
        org_id: UUID,
        user_ids: List[str],
        linked_app_ids: List[UUID]
):
    role_subject = build_role_path(role_name=role_name, org_id=org_id, app_id=app_id, scope=Scope.ORG)

    if inherited_role_names := INHERITS.get(role_name, []):
        _append_inherited_policies(policies, role_subject, inherited_role_names, linked_app_ids, INHERITED_ROLES_MAP)

    _append_policies(
        policies=policies,
        role_subject=role_subject,
        user_ids=user_ids
    )


# === Helpers ===
def _append_inherited_policies(
        policies: List[CasbinPolicy],
        role_subject: str,
        inherited_role_names: List[str],
        app_ids: List[UUID],
        inherited_role_map: Dict[str, Dict[str, Any]]
):
    for inherited_role_name in inherited_role_names:
        metadata = inherited_role_map.get(inherited_role_name, {})
        actions = metadata.get("actions", ["*"])
        resource_name = metadata.get("resource", "*")

        for aid in app_ids:
            inherited_role_subject = build_role_path(role_name=inherited_role_name, app_id=aid, scope=Scope.APP)
            resource = build_resource_path(resource_name=resource_name, app_id=aid, scope=Scope.APP)

            _append_policies(
                policies=policies,
                role_subject=inherited_role_subject,
                resource=resource,
                actions=actions,
                user_ids=[role_subject]  # just one subject in this case
            )


def _append_policies(
        policies: List[CasbinPolicy],
        role_subject: str,
        resource: str = "",
        actions: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None
):
    actions = actions or []
    user_ids = user_ids or []

    for action in actions:
        cp = CasbinPolicy(ptype="p", sub=role_subject, obj=resource, act=action, effect=PolicyEffect.ALLOW.value)
        policies.append(cp)
    for user_id in user_ids:
        cp = CasbinPolicy(ptype="g", sub=user_id, obj=role_subject)
        policies.append(cp)


def _resolve_resource_pattern(synthetic_resource: Optional[str], fallback_resource: str, app_id) -> str:
    if not synthetic_resource:
        return fallback_resource
    return build_resource_path(synthetic_resource, app_id)


def _get_unique_inherited_set():
    return list(set(item for sublist in INHERITS.values() for item in sublist))
