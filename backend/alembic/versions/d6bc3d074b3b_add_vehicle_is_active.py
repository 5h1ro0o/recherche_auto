# backend/alembic/versions/add_vehicle_is_active.py
"""add vehicle is_active field

Revision ID: add_vehicle_is_active
Revises: add_messages
Create Date: 2025-01-26 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_vehicle_is_active'
down_revision = 'add_messages'

def upgrade():
    # Ajouter colonne is_active
    op.add_column('vehicles', 
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )
    
    # Créer index pour performance
    op.create_index('ix_vehicles_is_active', 'vehicles', ['is_active'])
    
    # Ajouter index sur professional_user_id + is_active
    op.create_index(
        'ix_vehicles_pro_active', 
        'vehicles', 
        ['professional_user_id', 'is_active']
    )

def downgrade():
    op.drop_index('ix_vehicles_pro_active', 'vehicles')
    op.drop_index('ix_vehicles_is_active', 'vehicles')
    op.drop_column('vehicles', 'is_active')