"""add alerts and search_history tables

Revision ID: add_alerts_history
Revises: add_favorites
Create Date: 2025-01-22 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_alerts_history'
down_revision = 'add_favorites'

def upgrade():
    # Table alerts
    op.create_table('alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('criteria', sa.JSON(), nullable=False),
        sa.Column('frequency', sa.String(), server_default='daily'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_sent_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_alerts_user_id', 'alerts', ['user_id'])
    op.create_index('ix_alerts_is_active', 'alerts', ['is_active'])

    # Table search_history
    op.create_table('search_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('query', sa.String(), nullable=True),
        sa.Column('filters', sa.JSON(), server_default='{}'),
        sa.Column('results_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_search_history_user_id', 'search_history', ['user_id'])
    op.create_index('ix_search_history_created_at', 'search_history', ['created_at'])

def downgrade():
    op.drop_index('ix_search_history_created_at', 'search_history')
    op.drop_index('ix_search_history_user_id', 'search_history')
    op.drop_table('search_history')
    
    op.drop_index('ix_alerts_is_active', 'alerts')
    op.drop_index('ix_alerts_user_id', 'alerts')
    op.drop_table('alerts')