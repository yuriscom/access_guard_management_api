"""add synthetic pattern to specific roles

Revision ID: 0004_synthetic_roles_pattern
Revises: 0003_role_org_admin
Create Date: 2025-04-20 17:34:21.626102

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_synthetic_roles_pattern'
down_revision: Union[str, None] = '0003_role_org_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roles = [
    ("BillingViewer", "Access to view bills in SMC", "billing"),
    ("ReportingUser", "Access to user permissions for SMC reports", "reporting")
]

def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM apps WHERE name = 'Access Manager'"))
    row = result.fetchone()
    if not row:
        raise RuntimeError("App 'Access Manager' not found in apps table.")

    access_manager_id = str(row[0])
    now = datetime.utcnow()

    for role_name, description, pattern in roles:
        conn.execute(sa.text("""
                INSERT INTO iam_roles (scope, app_id, role_name, description, created_at, synthetic, synthetic_pattern)
                VALUES (:scope, :app_id, :role_name, :desc, :created_at, true, :pattern)
                ON CONFLICT DO NOTHING
            """), {
            "scope": "SMC",
            "app_id": access_manager_id,
            "role_name": role_name,
            "desc": description,
            "created_at": now,
            "pattern": pattern,
        })

    conn.execute((sa.text("""
            update iam_roles set synthetic_pattern = 'policies' where role_name = 'PolicyReader' and scope = 'SMC';
            update iam_roles set synthetic_pattern = 'iam' where role_name = 'IAMManager' and scope = 'SMC';
        """)))


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute((sa.text("""
                update iam_roles set synthetic_pattern = NULL;
            """)))

    result = conn.execute(sa.text("SELECT id FROM apps WHERE name = 'Access Manager'"))
    row = result.fetchone()
    if not row:
        return  # nothing to delete

    access_manager_id = str(row[0])

    for role_name, _ in roles:
        conn.execute(sa.text("""
                DELETE FROM iam_roles
                WHERE scope = 'SMC' AND app_id = :app_id AND role_name = :role_name
            """), {
            "app_id": access_manager_id,
            "role_name": role_name,
        })