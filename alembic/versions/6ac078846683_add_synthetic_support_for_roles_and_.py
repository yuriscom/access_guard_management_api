"""add synthetic support for roles and resources

Revision ID: 6ac078846683
Revises: 4773194387a1
Create Date: 2025-04-16 16:10:20.793731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6ac078846683'
down_revision: Union[str, None] = '4773194387a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
                ALTER TABLE iam_resources ADD COLUMN synthetic boolean DEFAULT false;
                ALTER TABLE iam_resources ADD COLUMN synthetic_pattern varchar(255) NULL;
                
                ALTER TABLE iam_roles ADD COLUMN synthetic boolean DEFAULT false;
                ALTER TABLE iam_roles ADD COLUMN synthetic_pattern varchar(255) NULL;
            """)


def downgrade() -> None:
    op.execute("""
                    ALTER TABLE iam_resources DROP COLUMN if exists synthetic;
                    ALTER TABLE iam_resources DROP COLUMN if exists synthetic_pattern;

                    ALTER TABLE iam_roles DROP COLUMN if exists synthetic;
                    ALTER TABLE iam_roles DROP COLUMN if exists synthetic_pattern;
                """)
