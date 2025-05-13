"""rename webhooks table

Revision ID: 0011_rename_tables
Revises: 0010_rename_tables
Create Date: 2025-05-01 13:57:48.311882

"""
import pathlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0011_rename_tables'
down_revision: Union[str, None] = '0010_rename_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0011_rename_webhooks_table.sql"
    with open(sql_path) as f:
        op.execute(f.read())


def downgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0011_rename_webhooks_table__down.sql"
    with open(sql_path) as f:
        op.execute(f.read())