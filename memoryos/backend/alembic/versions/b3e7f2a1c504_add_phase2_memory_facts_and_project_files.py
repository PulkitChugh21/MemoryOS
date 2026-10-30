"""add_phase2_memory_facts_and_project_files

Revision ID: b3e7f2a1c504
Revises: 98704ae392fc
Create Date: 2026-09-23 14:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b3e7f2a1c504'
down_revision: Union[str, None] = '98704ae392fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- memory_facts table (Tier 3 structured memory) ---
    op.create_table(
        'memory_facts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('fact_type', sa.String(50), nullable=False),
        sa.Column('key', sa.String(500), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False, server_default='conversation'),
        sa.Column('source_episode_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('memory_episodes.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('confidence', sa.Float(), server_default='0.8'),
        sa.Column('is_stale', sa.Boolean(), server_default='false'),
        sa.Column('ttl_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # Indexes for memory_facts
    op.create_index('ix_facts_project_type', 'memory_facts', ['project_id', 'fact_type'])
    op.create_index('ix_facts_project_key', 'memory_facts', ['project_id', 'key'])
    op.create_index('ix_facts_project_stale', 'memory_facts', ['project_id', 'is_stale'])

    # --- project_files table (file versioning) ---
    op.create_table(
        'project_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('projects.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False, server_default='text/plain'),
        sa.Column('size_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_version_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('project_files.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('diff_summary', sa.Text(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # Indexes for project_files
    op.create_index('ix_files_project_filename', 'project_files',
                    ['project_id', 'filename', 'is_current'])
    op.create_index('ix_files_project_current', 'project_files',
                    ['project_id', 'is_current'])


def downgrade() -> None:
    op.drop_index('ix_files_project_current', table_name='project_files')
    op.drop_index('ix_files_project_filename', table_name='project_files')
    op.drop_table('project_files')

    op.drop_index('ix_facts_project_stale', table_name='memory_facts')
    op.drop_index('ix_facts_project_key', table_name='memory_facts')
    op.drop_index('ix_facts_project_type', table_name='memory_facts')
    op.drop_table('memory_facts')
