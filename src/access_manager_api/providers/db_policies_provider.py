from typing import Dict, List, Any

from access_guard.authz.loaders.casbin_policy_provider import CasbinPolicyProvider
from access_guard.authz.models.casbin_policy import CasbinPolicy
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


class DBPoliciesProvider(CasbinPolicyProvider):
    def __init__(self, db: Session):
        self.db = db

    def get_policies(self, filter: Dict[str, Any]) -> List[CasbinPolicy]:
        scope = filter.get("policy_api_scope")
        app_id = filter.get("policy_api_appid")


        return [
            # CasbinPolicy(ptype="g", sub="Role1", obj="Resource1"),
            # CasbinPolicy(ptype="p", sub="a", obj="b", act="read", effect="allow"),
        ]

    def _get_role_permissions(self, scope: str, app_id: str) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT
                rp.role_id,
                r.role_name,
                r.scope AS role_scope,
                r.app_id AS role_app_id,
                res.resource_name,
                res.scope AS resource_scope,
                res.app_id AS resource_app_id,
                perm.action,
                COALESCE(rp.effect, 'allow') AS effect
            FROM iam_role_permissions rp
            JOIN iam_roles r ON rp.role_id = r.id
            JOIN iam_permissions perm ON rp.permission_id = perm.id
            JOIN iam_resources res ON perm.resource_id = res.id
            WHERE r.scope = :scope
              AND res.scope = :scope
              AND (:app_id IS NULL OR r.app_id = :app_id)
              AND (:app_id IS NULL OR res.app_id = :app_id)
              AND r.org_id IS NULL
              AND res.org_id IS NULL
              AND NOT COALESCE(r.synthetic, false)
              AND NOT COALESCE(res.synthetic, false)
        """)
        return [dict(row) for row in self.db.execute(sql, {"scope": scope, "app_id": app_id})]

    def _get_user_roles(self, scope: str, app_id: str) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT
                ur.user_id,
                u.email,
                ur.role_id,
                ur.scope,
                ur.app_id
            FROM iam_user_roles ur
            JOIN users u ON u.id = ur.user_id
            WHERE ur.scope = :scope
              AND (:app_id IS NULL OR ur.app_id = :app_id)
              AND ur.org_id IS NULL
        """)
        return [dict(row) for row in self.db.execute(sql, {"scope": scope, "app_id": app_id})]

    def _get_user_permissions(self, scope: str, app_id: str) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT
                up.user_id,
                u.email,
                res.resource_name,
                res.scope AS resource_scope,
                res.app_id AS resource_app_id,
                perm.action,
                COALESCE(up.effect, 'allow') AS effect
            FROM iam_user_permissions up
            JOIN users u ON u.id = up.user_id
            JOIN iam_permissions perm ON up.permission_id = perm.id
            JOIN iam_resources res ON perm.resource_id = res.id
            WHERE res.scope = :scope
              AND (:app_id IS NULL OR res.app_id = :app_id)
              AND up.org_id IS NULL
              AND res.org_id IS NULL
              AND NOT COALESCE(res.synthetic, false)
        """)
        return [dict(row) for row in self.db.execute(sql, {"scope": scope, "app_id": app_id})]
