"""add_referral_breakdown_to_palms

Revision ID: c41539ab16e8
Revises: e54bea0867c7
Create Date: 2026-04-22 10:21:42.376141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c41539ab16e8'
down_revision: Union[str, Sequence[str], None] = 'e54bea0867c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('palms_snapshots', sa.Column('rgi', sa.Integer(), server_default='0'))
    op.add_column('palms_snapshots', sa.Column('rgo', sa.Integer(), server_default='0'))
    op.add_column('palms_snapshots', sa.Column('rri', sa.Integer(), server_default='0'))
    op.add_column('palms_snapshots', sa.Column('rro', sa.Integer(), server_default='0'))
    op.add_column('palms_snapshots', sa.Column('referrals_given_total', sa.Integer(), server_default='0'))
    op.add_column('palms_snapshots', sa.Column('referrals_received_total', sa.Integer(), server_default='0'))


def downgrade() -> None:
    op.drop_column('palms_snapshots', 'referrals_received_total')
    op.drop_column('palms_snapshots', 'referrals_given_total')
    op.drop_column('palms_snapshots', 'rro')
    op.drop_column('palms_snapshots', 'rri')
    op.drop_column('palms_snapshots', 'rgo')
    op.drop_column('palms_snapshots', 'rgi')
