"""add scraper_logs table

Revision ID: add_scraper_logs
Revises: add_assisted_requests
Create Date: 2025-01-27 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_scraper_logs'
down_revision = 'add_assisted_requests'

def upgrade():
    # Check if scraper_logs table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'scraper_logs' not in inspector.get_table_names():
        op.create_table(
            'scraper_logs',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('source', sa.String(), nullable=False, index=True),
            sa.Column('status', sa.String(), nullable=False),  # success, warning, error
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('duration_seconds', sa.Float(), nullable=True),
            sa.Column('vehicles_found', sa.Integer(), default=0),
            sa.Column('vehicles_new', sa.Integer(), default=0),
            sa.Column('vehicles_updated', sa.Integer(), default=0),
            sa.Column('error_details', postgresql.JSON(), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(), default=sa.func.now(), index=True)
        )

def downgrade():
    op.drop_table('scraper_logs')