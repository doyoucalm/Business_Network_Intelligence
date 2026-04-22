"""meetings_add_state_columns

Revision ID: e30683d092b8
Revises: b1532a4f99f2
Create Date: 2026-04-22 09:15:09.630864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e30683d092b8'
down_revision: Union[str, Sequence[str], None] = 'b1532a4f99f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('meetings', sa.Column('current_slide_index', sa.Integer(), server_default='0'))
    op.add_column('meetings', sa.Column('status', sa.String(20), server_default='scheduled'))


def downgrade() -> None:
    op.drop_column('meetings', 'status')
    op.drop_column('meetings', 'current_slide_index')
