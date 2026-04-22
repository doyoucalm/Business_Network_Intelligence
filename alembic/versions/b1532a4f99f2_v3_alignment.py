"""v3_alignment

Revision ID: b1532a4f99f2
Revises: 21c227494aae
Create Date: 2026-04-22 08:00:09.406824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1532a4f99f2'
down_revision: Union[str, Sequence[str], None] = '21c227494aae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename columns in members (old -> new)
    op.alter_column('members', 'bni_classification', new_column_name='classification')
    op.alter_column('members', 'company_name', new_column_name='company')
    
    # 2. Add new columns to members
    op.add_column('members', sa.Column('is_gold_member', sa.Boolean(), server_default='false'))
    op.add_column('members', sa.Column('sponsored_by_member_id', sa.UUID(), sa.ForeignKey('members.id'), nullable=True))
    
    # 3. Update member_roles check constraint to include 'admin'
    # First drop it (we need the name from the failure detailed earlier)
    op.drop_constraint('member_roles_role_check', 'member_roles')
    op.create_check_constraint(
        'member_roles_role_check',
        'member_roles',
        "role::text = ANY (ARRAY['admin'::character varying, 'president'::character varying, 'vice_president'::character varying, 'secretary'::character varying, 'treasurer'::character varying, 'secretary_treasurer'::character varying, 'gdc'::character varying, 'ambassador'::character varying, 'visitor_host'::character varying, 'education_coordinator'::character varying, 'events_coordinator'::character varying, 'mc_coordinator'::character varying, 'mentor_coordinator'::character varying, 'growth_coordinator'::character varying, 'mc_qa'::character varying, 'mc_cb'::character varying, 'mc_me'::character varying, 'mc_mr'::character varying, 'social_media_coordinator'::character varying, 'connect_coordinator'::character varying, 'one_to_one_coordinator'::character varying, 'go_green_coordinator'::character varying, 'feature_presentation_coordinator'::character varying, 'member'::character varying]::text[])"
    )

    # 4. Data Migration: members.role -> member_roles table
    # Mapping 'admin' to 'admin' and everything else to its value or 'member' if unknown
    op.execute("""
        INSERT INTO member_roles (id, member_id, chapter_id, role, is_active, created_at)
        SELECT 
            uuid_generate_v4(), 
            id, 
            chapter_id, 
            CASE 
                WHEN role IN ('admin', 'president', 'vice_president', 'secretary', 'treasurer', 'secretary_treasurer', 'member') THEN role
                ELSE 'member'
            END,
            true, 
            now()
        FROM members
        WHERE role IS NOT NULL
    """)


def downgrade() -> None:
    # 1. Clean up member_roles
    op.execute("DELETE FROM member_roles")

    # 2. Restore check constraint
    op.drop_constraint('member_roles_role_check', 'member_roles')
    op.create_check_constraint(
        'member_roles_role_check',
        'member_roles',
        "role::text = ANY (ARRAY['president'::character varying, 'vice_president'::character varying, 'secretary'::character varying, 'treasurer'::character varying, 'secretary_treasurer'::character varying, 'gdc'::character varying, 'ambassador'::character varying, 'visitor_host'::character varying, 'education_coordinator'::character varying, 'events_coordinator'::character varying, 'mc_coordinator'::character varying, 'mentor_coordinator'::character varying, 'growth_coordinator'::character varying, 'mc_qa'::character varying, 'mc_cb'::character varying, 'mc_me'::character varying, 'mc_mr'::character varying, 'social_media_coordinator'::character varying, 'connect_coordinator'::character varying, 'one_to_one_coordinator'::character varying, 'go_green_coordinator'::character varying, 'feature_presentation_coordinator'::character varying, 'member'::character varying]::text[])"
    )

    # 3. Remove new columns from members
    op.drop_column('members', 'sponsored_by_member_id')
    op.drop_column('members', 'is_gold_member')
    
    # 4. Rename columns back (new -> old)
    op.alter_column('members', 'classification', new_column_name='bni_classification')
    op.alter_column('members', 'company', new_column_name='company_name')
