from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends
from ..services.db import get_db
from ..schemas.policies import PoliciesParams

class PoliciesService:
    def __init__(self, db: Session):
        self.db = db

    def get_policies(self, params: PoliciesParams):
        query = text("""
            WITH role_permissions AS (
            SELECT DISTINCT
                'p' AS ptype,
                r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS subject,
                res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
                perm.action AS action,
                COALESCE(rp.effect, 'allow') AS effect
            FROM iam_role_policies rp
            JOIN iam_roles r ON rp.role_id = r.id
            JOIN iam_permissions perm ON rp.permission_id = perm.id
            JOIN iam_resources res ON perm.resource_id = res.id
            WHERE r.scope = :scope AND (
                (:app_id IS NULL AND r.app_id IS NULL)
                OR (:app_id IS NOT NULL AND r.app_id = :app_id)
            )
            AND res.scope = :scope AND (
                (:app_id IS NULL AND res.app_id IS NULL)
                OR (:app_id IS NOT NULL AND res.app_id = :app_id)
            )
        ),
        user_permissions AS (
            SELECT DISTINCT
                'p' AS ptype,
                u.name AS subject,
                res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
                perm.action AS action,
                COALESCE(up.effect, 'allow') AS effect
            FROM iam_user_policies up
            JOIN users u ON up.user_id = u.id
            JOIN iam_permissions perm ON up.permission_id = perm.id
            JOIN iam_resources res ON perm.resource_id = res.id
            WHERE res.scope = :scope AND (
                (:app_id IS NULL AND res.app_id IS NULL)
                OR (:app_id IS NOT NULL AND res.app_id = :app_id)
            )
        ),
        user_roles AS (
            SELECT DISTINCT
                'g' AS ptype,
                u.name AS subject,
                r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS object,
                NULL AS action,
                NULL AS effect
            FROM user_roles ur
            JOIN users u ON ur.user_id = u.id
            JOIN iam_roles r ON ur.role_id = r.id
            WHERE r.scope = :scope AND (
                (:app_id IS NULL AND r.app_id IS NULL)
                OR (:app_id IS NOT NULL AND r.app_id = :app_id)
            )
        )
        SELECT ptype, subject, object, action, effect FROM role_permissions
        UNION ALL
        SELECT ptype, subject, object, action, effect FROM user_permissions
        UNION ALL
        SELECT ptype, subject, object, action, effect FROM user_roles
        """)

        result = self.db.execute(
            query, 
            {
                "scope": params.scope,
                "app_id": params.app_id,
                "user_id": params.user_id
            }
        )
        policies = result.fetchall()
        
        # Convert to list of dictionaries
        return [
            {
                "ptype": row.ptype,
                "subject": row.subject,
                "object": row.object,
                "action": row.action,
                "effect": row.effect
            }
            for row in policies
        ]

def get_policies_service(db: Session = Depends(get_db)):
    return PoliciesService(db) 