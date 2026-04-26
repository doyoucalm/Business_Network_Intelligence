"""meeting_revisions

Adds:
- meetings.weekly_notes (TEXT) — per-meeting documentation field
- meetings.meeting_type CHECK constraint (regular | closed | launchpad)
- host_rotation_state table — drives Edu Moment + Core Value host auto-suggest

Revision ID: f5398a2b1eb5
Revises: e54bea0867c7
Create Date: 2026-04-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision: str = 'f5398a2b1eb5'
down_revision: Union[str, Sequence[str], None] = 'e9e20ec705ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('meetings', sa.Column('weekly_notes', sa.Text(), nullable=True))

    # Existing rows used 'weekly' as default; normalize to 'regular'.
    op.execute("UPDATE meetings SET meeting_type = 'regular' WHERE meeting_type NOT IN ('regular','closed','launchpad')")
    op.execute("ALTER TABLE meetings ALTER COLUMN meeting_type SET DEFAULT 'regular'")
    op.create_check_constraint(
        'ck_meetings_meeting_type',
        'meetings',
        "meeting_type IN ('regular','closed','launchpad')"
    )

    op.create_table(
        'host_rotation_state',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('chapter_id', UUID(as_uuid=True), sa.ForeignKey('chapters.id'), nullable=False),
        sa.Column('rotation_type', sa.String(30), nullable=False),  # core_value | education
        sa.Column('last_member_id', UUID(as_uuid=True), sa.ForeignKey('members.id'), nullable=True),
        sa.Column('last_index', sa.Integer(), server_default='0'),
        sa.Column('last_assigned_date', sa.Date(), nullable=True),
        sa.Column('history', JSONB(), server_default='[]'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('chapter_id', 'rotation_type', name='uq_host_rotation_chapter_type'),
    )


def downgrade() -> None:
    op.drop_table('host_rotation_state')
    op.drop_constraint('ck_meetings_meeting_type', 'meetings', type_='check')
    op.drop_column('meetings', 'weekly_notes')
