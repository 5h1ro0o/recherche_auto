# backend/alembic/versions/xxx_add_scraper_logs.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
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