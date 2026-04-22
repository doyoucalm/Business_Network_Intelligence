"""migrate_member_role_to_member_roles

Revision ID: e54bea0867c7
Revises: e30683d092b8
Create Date: 2026-04-22 09:25:19.862452

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e54bea0867c7'
down_revision: Union[str, Sequence[str], None] = 'e30683d092b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('members', 'role')


def downgrade() -> None:
    op.add_column('members', sa.Column('role', sa.String(20), nullable=True))
    op.execute("""
        UPDATE members SET role = (
            SELECT role FROM member_roles
            WHERE member_id = members.id AND is_active = true
            LIMIT 1
        )
    """)
