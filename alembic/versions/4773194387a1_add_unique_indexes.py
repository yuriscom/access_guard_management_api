"""add unique indexes

Revision ID: 4773194387a1
Revises: 
Create Date: 2025-04-14 17:55:26.936353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4773194387a1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            CREATE UNIQUE INDEX uix_scope_app_resource
            ON iam_resources (scope, COALESCE(app_id, -1), resource_name)
        """)
    op.execute("""
            CREATE UNIQUE INDEX uix_scope_app_role
            ON iam_roles (scope, COALESCE(app_id, -1), role_name)
        """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uix_scope_app_resource")
    op.execute("DROP INDEX IF EXISTS uix_scope_app_role")
