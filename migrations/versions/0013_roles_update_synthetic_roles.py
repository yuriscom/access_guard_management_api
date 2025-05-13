"""update synthetic roles

Revision ID: 0013_roles
Revises: 0012_org_scope
Create Date: 2025-05-05 10:29:35.381146

"""
import pathlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0013_roles'
down_revision: Union[str, None] = '0012_org_scope'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0013_synthetic_roles.sql"
    with open(sql_path) as f:
        op.execute(f.read())


def downgrade() -> None:
    sql_path = pathlib.Path(__file__).parent.parent / "sql" / "0013_synthetic_roles__down.sql"
    with open(sql_path) as f:
        op.execute(f.read())