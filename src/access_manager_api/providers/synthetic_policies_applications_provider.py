import logging
from collections import defaultdict
from typing import List, Any, Dict
from uuid import UUID

from access_guard.authz.loaders.casbin_policy_provider import CasbinPolicyProvider
from access_guard.authz.models.casbin_policy import CasbinPolicy
from sqlalchemy import text
from sqlalchemy.orm import Session

from access_manager_api.infra.constants import ROLE_ORG_ADMIN
from access_manager_api.models import Scope
from access_manager_api.schemas.common import PolicyEffect
from access_manager_api.utils.utils import build_role_path, build_resource_path

logger = logging.getLogger(__name__)


class SyntheticAppPoliciesProvider(CasbinPolicyProvider):
    def __init__(self, db: Session):
        self.db = db

    def get_policies(self, filter: Dict[str, Any]) -> List[CasbinPolicy]:
        app_id = filter.get("policy_api_appid")
        if not app_id:
            logger.warning(f"app_id not found in filter")
            return list([])

        return load_synthetic_policies(self.db, app_id)


def load_synthetic_policies(db: Session, app_id: UUID) -> List[CasbinPolicy]:
    policies: List[CasbinPolicy] = []
    load_app_product_owner_roles(db, policies, app_id)
    return policies


def load_app_product_owner_roles(db: Session, policies: List[CasbinPolicy], app_id: UUID) -> List[CasbinPolicy]:
    sql = text("""
            SELECT r.role_name, ur.user_id, u.email, oa.app_id
            FROM iam_roles r
            JOIN iam_user_roles ur ON ur.role_id = r.id
            JOIN users u ON u.id = ur.user_id
            JOIN org_apps oa ON oa.org_id = u.org_id
            WHERE r.synthetic = TRUE
              AND r.scope = 'SMC'
              AND r.role_name = :role_name
              AND oa.app_id = :app_id
        """)
    rows = db.execute(sql, {
        "role_name": ROLE_ORG_ADMIN,
        "app_id": str(app_id)
    }).fetchall()

    grouped = defaultdict(list)
    for row in rows:
        grouped[(row.role_name, row.app_id)].append(row.email)

    for (role_name, app_id), user_ids in grouped.items():
        role_subject = build_role_path(role_name=role_name, app_id=app_id, scope=Scope.APP)
        resource = build_resource_path(resource_name="*", app_id=app_id, scope=Scope.APP)
        for action in ["*"]:
            cp = CasbinPolicy(ptype="p", sub=role_subject, obj=resource, act=action, effect=PolicyEffect.ALLOW.value)
            policies.append(cp)
        for user_id in user_ids:
            cp = CasbinPolicy(ptype="g", sub=user_id, obj=role_subject)
            policies.append(cp)

    return policies
