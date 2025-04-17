"""add resource_name for IAM built-in roles

Revision ID: 0e03e20ac3b5
Revises: c61ab9cd53db
Create Date: 2025-04-16 18:48:14.144619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e03e20ac3b5'
down_revision: Union[str, None] = 'c61ab9cd53db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
                UPDATE iam_roles
                SET synthetic_pattern = 'policies/APP/{app_id}'
                WHERE role_name = 'PolicyReader' AND scope = 'SMC';
                
                UPDATE iam_roles
                SET synthetic_pattern = 'iam/APP/{app_id}'
                WHERE role_name = 'IAMManager' AND scope = 'SMC';
            """)


def downgrade() -> None:
    op.execute("""
                    UPDATE iam_roles
                    SET synthetic_pattern = NULL
                    WHERE role_name = 'PolicyReader' AND scope = 'SMC';

                    UPDATE iam_roles
                    SET synthetic_pattern = NULL
                    WHERE role_name = 'IAMManager' AND scope = 'SMC';
                """)
