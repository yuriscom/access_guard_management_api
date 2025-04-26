"""add role policies unique index

Revision ID: 0005_role_policies_unique
Revises: 0004_synthetic_roles_pattern
Create Date: 2025-04-22 12:30:54.040810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0005_role_policies_unique'
down_revision: Union[str, None] = '0004_synthetic_roles_pattern'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
                CREATE UNIQUE INDEX uix_role_permission_effect_iam_role_policies
                ON iam_role_policies (role_id, permission_id, effect)
            """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uix_role_permission_effect_iam_role_policies")
