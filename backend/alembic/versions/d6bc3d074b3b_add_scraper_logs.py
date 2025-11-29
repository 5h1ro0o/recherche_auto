"""add scraper_logs table

Revision ID: add_scraper_logs
Revises: add_vehicle_is_active
Create Date: 2025-01-27 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_scraper_logs'
down_revision = 'add_vehicle_is_active'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'scraper_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('source', sa.String(), nullable=False, index=True),
        sa.Column('status', sa.String(), nullable=False),  # success, warning, error
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('vehicles_found', sa.Integer(), server_default='0'),
        sa.Column('vehicles_new', sa.Integer(), server_default='0'),
        sa.Column('vehicles_updated', sa.Integer(), server_default='0'),
        sa.Column('error_details', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_scraper_logs_created_at'), 'scraper_logs', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_scraper_logs_created_at'), table_name='scraper_logs')
    op.drop_table('scraper_logs')