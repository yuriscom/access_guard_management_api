"""org_admin built-in role

Revision ID: 0003_role_org_admin
Revises: 0002_built_in_roles
Create Date: 2025-04-19 15:23:51.315984

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003_role_org_admin'
down_revision: Union[str, None] = '0002_built_in_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roles = [
    ("OrgAdmin", "Full access to all Product operations across applications")
]


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM apps WHERE name = 'Access Manager'"))
    row = result.fetchone()
    if not row:
        raise RuntimeError("App 'Access Manager' not found in apps table.")

    conn.execute((sa.text("""
        ALTER TABLE org_apps ADD COLUMN is_owner BOOLEAN DEFAULT FALSE;
    """)))

    access_manager_id = str(row[0])
    now = datetime.utcnow()

    for role_name, description in roles:
        conn.execute(sa.text("""
            INSERT INTO iam_roles (scope, app_id, role_name, description, created_at, synthetic)
            VALUES (:scope, :app_id, :role_name, :desc, :created_at, true)
            ON CONFLICT DO NOTHING
        """), {
            "scope": "SMC",
            "app_id": access_manager_id,
            "role_name": role_name,
            "desc": description,
            "created_at": now,
        })


def downgrade() -> None:
    conn = op.get_bind()
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

    conn.execute((sa.text("""
            ALTER TABLE org_apps DROP COLUMN if exists is_owner;
        """)))
