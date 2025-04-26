"""rename tables

Revision ID: 0008_rename_role_permission_table
Revises: 0007_unique_constraints
Create Date: 2025-04-25 16:24:24.109919

"""
import pathlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0008_rename_tables'
down_revision: Union[str, None] = '0007_unique_constraints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0008_rename_role_permission_table.sql"
    with open(sql_path) as f:
        op.execute(f.read())


def downgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0008_rename_role_permission_table__down.sql"
    with open(sql_path) as f:
        op.execute(f.read())
