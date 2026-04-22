"""Add presenter fields to members and presentations

Revision ID: e9e20ec705ef
Revises: c41539ab16e8
Create Date: 2026-04-22 14:47:38.941039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e9e20ec705ef'
down_revision: Union[str, Sequence[str], None] = 'c41539ab16e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Members: photo + social
    op.add_column('members', sa.Column('photo_url', sa.String(500), nullable=True))
    op.add_column('members', sa.Column('instagram', sa.String(100), nullable=True))
    op.add_column('members', sa.Column('website', sa.String(200), nullable=True))
    
    # MemberPresentation: canvas support
    op.add_column('member_presentations', sa.Column('logo_url', sa.String(500), nullable=True))
    op.add_column('member_presentations', sa.Column('canvas_type', sa.String(30), server_default='4images'))
    op.add_column('member_presentations', sa.Column('canvas_content', postgresql.JSONB(astext_type=sa.Text()), server_default='{}'))
    op.add_column('member_presentations', sa.Column('contact_override', postgresql.JSONB(astext_type=sa.Text()), server_default='{}'))

def downgrade():
    op.drop_column('members', 'photo_url')
    op.drop_column('members', 'instagram')
    op.drop_column('members', 'website')
    op.drop_column('member_presentations', 'logo_url')
    op.drop_column('member_presentations', 'canvas_type')
    op.drop_column('member_presentations', 'canvas_content')
    op.drop_column('member_presentations', 'contact_override')
