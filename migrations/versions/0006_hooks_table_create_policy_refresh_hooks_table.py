"""create policy refresh hooks table

Revision ID: 0006_hooks_table
Revises: 0005_role_policies_unique
Create Date: 2025-04-23 16:14:50.499866

"""
import pathlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0006_hooks_table'
down_revision: Union[str, None] = '0005_role_policies_unique'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0006_create_policy_refresh_hooks.sql"
    with open(sql_path) as f:
        op.execute(f.read())


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_hooks_scope_app_id;")
    op.execute("DROP TABLE IF EXISTS policy_refresh_hooks;")
