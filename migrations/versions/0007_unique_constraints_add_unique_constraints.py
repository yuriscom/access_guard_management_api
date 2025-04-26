"""add unique constraints

Revision ID: 0007_unique_constraints
Revises: 0006_hooks_table
Create Date: 2025-04-24 15:01:41.707879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0007_unique_constraints'
down_revision: Union[str, None] = '0006_hooks_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
                   CREATE UNIQUE INDEX uix_user_permission_iam_user_policies
                   ON iam_user_policies (user_id, permission_id);
                   
                   CREATE UNIQUE INDEX uix_user_role_iam_user_roles
                   ON user_roles (user_id, role_id);
               """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS uix_user_permission_iam_user_policies;
        DROP INDEX IF EXISTS uix_user_role_iam_user_roles; 
    """)
