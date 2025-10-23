"""add users and roles tables

Revision ID: add_users_roles
Revises: d6bc3d074b3b
Create Date: 2025-01-20 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_users_roles'
down_revision: Union[str, Sequence[str], None] = 'd6bc3d074b3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False, server_default='PARTICULAR'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
    # Add professional_user_id to vehicles table for linking
    op.add_column('vehicles', sa.Column('professional_user_id', sa.String(), nullable=True))
    op.create_foreign_key('fk_vehicles_professional_user', 'vehicles', 'users', ['professional_user_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_vehicles_professional_user_id'), 'vehicles', ['professional_user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove vehicle foreign key and column
    op.drop_index(op.f('ix_vehicles_professional_user_id'), table_name='vehicles')
    op.drop_constraint('fk_vehicles_professional_user', 'vehicles', type_='foreignkey')
    op.drop_column('vehicles', 'professional_user_id')
    
    # Drop indexes
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop users table
    op.drop_table('users')