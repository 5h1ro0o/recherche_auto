"""add missing fields to vehicles table

Revision ID: update_vehicles_complete
Revises: d6bc3d074b3b
Create Date: 2025-01-20 09:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'update_vehicles_complete'
down_revision = 'd6bc3d074b3b'

def upgrade():
    # Add missing columns to vehicles table
    op.add_column('vehicles', sa.Column('vin', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('fuel_type', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('transmission', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('vehicles', sa.Column('images', sa.JSON(), server_default='[]', nullable=True))
    op.add_column('vehicles', sa.Column('location_lat', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('location_lon', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('location_city', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True))

    # Create indexes
    op.create_index('ix_vehicles_make', 'vehicles', ['make'])
    op.create_index('ix_vehicles_model', 'vehicles', ['model'])
    op.create_index('ix_vehicles_price', 'vehicles', ['price'])
    op.create_index('ix_vehicles_vin', 'vehicles', ['vin'], unique=True)
    op.create_index('ix_vehicles_created_at', 'vehicles', ['created_at'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_vehicles_created_at', 'vehicles')
    op.drop_index('ix_vehicles_vin', 'vehicles')
    op.drop_index('ix_vehicles_price', 'vehicles')
    op.drop_index('ix_vehicles_model', 'vehicles')
    op.drop_index('ix_vehicles_make', 'vehicles')

    # Drop columns
    op.drop_column('vehicles', 'updated_at')
    op.drop_column('vehicles', 'location_city')
    op.drop_column('vehicles', 'location_lon')
    op.drop_column('vehicles', 'location_lat')
    op.drop_column('vehicles', 'images')
    op.drop_column('vehicles', 'description')
    op.drop_column('vehicles', 'transmission')
    op.drop_column('vehicles', 'fuel_type')
    op.drop_column('vehicles', 'vin')
