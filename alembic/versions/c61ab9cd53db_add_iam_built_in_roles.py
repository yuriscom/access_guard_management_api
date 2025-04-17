"""add IAM built-in roles

Revision ID: c61ab9cd53db
Revises: 6ac078846683
Create Date: 2025-04-16 17:30:10.651482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = 'c61ab9cd53db'
down_revision: Union[str, None] = '6ac078846683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roles = [
    ("IAMManager", "Manage IAM resources for a specific product"),
    ("PolicyReader", "Read-only access to policies for system clients"),
    ("AMAdmin", "Full access to all Access Manager operations"),
    ("Superadmin", "Full access to all SMC operations across applications"),
]

def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM apps WHERE name = 'access_manager'"))
    row = result.fetchone()
    if not row:
        raise RuntimeError("App 'access_manager' not found in apps table.")

    access_manager_id = row[0]
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
    result = conn.execute(sa.text("SELECT id FROM apps WHERE name = 'access_manager'"))
    row = result.fetchone()
    if not row:
        return  # nothing to delete

    access_manager_id = row[0]

    for role_name, _ in roles:
        conn.execute(sa.text("""
                DELETE FROM iam_roles
                WHERE scope = 'SMC' AND app_id = :app_id AND role_name = :role_name
            """), {
            "app_id": access_manager_id,
            "role_name": role_name,
        })
