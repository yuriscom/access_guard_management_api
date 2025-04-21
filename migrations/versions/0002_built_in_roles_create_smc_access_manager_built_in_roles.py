"""create SMC Access Manager built-in roles

Revision ID: 0002_built_in_roles
Revises: 0001_init_iam_tables
Create Date: 2025-04-19 11:37:12.407205

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_built_in_roles'
down_revision: Union[str, None] = '0001_init_iam_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


roles = [
    ("IAMManager", "Manage IAM resources for a specific product"),
    ("PolicyReader", "Read-only access to policies for system clients"),
    ("AMAdmin", "Full access to all Access Manager operations"),
    ("Superadmin", "Full access to all SMC operations across applications")
]

def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM apps WHERE name = 'Access Manager'"))
    row = result.fetchone()
    if not row:
        raise RuntimeError("App 'Access Manager' not found in apps table.")

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
