"""add favorites table

Revision ID: add_favorites
Revises: add_users_roles
Create Date: 2025-01-21 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_favorites'
down_revision = 'add_users_roles'

def upgrade():
    op.create_table('favorites',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('vehicle_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'vehicle_id', name='unique_user_vehicle_favorite')
    )
    op.create_index('ix_favorites_user_id', 'favorites', ['user_id'])
    op.create_index('ix_favorites_vehicle_id', 'favorites', ['vehicle_id'])

def downgrade():
    op.drop_index('ix_favorites_vehicle_id', 'favorites')
    op.drop_index('ix_favorites_user_id', 'favorites')
    op.drop_table('favorites')