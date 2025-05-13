"""add org scope

Revision ID: 0012_org_scope
Revises: 0011_rename_tables
Create Date: 2025-05-02 15:53:19.218882

"""
import pathlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0012_org_scope'
down_revision: Union[str, None] = '0011_rename_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0012_org_scope.sql"
    with open(sql_path) as f:
        op.execute(f.read())


def downgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0012_org_scope__down.sql"
    with open(sql_path) as f:
        op.execute(f.read())
