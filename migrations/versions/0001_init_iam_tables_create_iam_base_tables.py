"""create IAM base tables

Revision ID: 0001_init_iam_tables
Revises: 
Create Date: 2025-04-19 11:30:11.147279

"""
import pathlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_init_iam_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "init.sql"
    with sql_path.open("r") as f:
        sql = f.read()
    op.execute(sql)


def downgrade() -> None:
    pass
