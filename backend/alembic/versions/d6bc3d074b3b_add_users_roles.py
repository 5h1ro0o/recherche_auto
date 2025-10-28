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
down_revision: Union[str, Sequence[str], None] = 'update_vehicles_complete'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create UserRole enum type if it doesn't exist using raw SQL
    conn = op.get_bind()

    # Check if the enum type already exists
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole');"
    ))
    enum_exists = result.scalar()

    if not enum_exists:
        # Create the enum type using raw SQL to avoid SQLAlchemy automatic creation
        conn.execute(sa.text(
            "CREATE TYPE userrole AS ENUM ('ADMIN', 'PRO', 'PARTICULAR', 'EXPERT')"
        ))
        conn.commit()

    # Create users table without using SQLAlchemy ENUM object
    # This prevents SQLAlchemy from trying to create the enum automatically
    op.execute("""
        CREATE TABLE users (
            id VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            full_name VARCHAR,
            phone VARCHAR,
            role userrole NOT NULL DEFAULT 'PARTICULAR',
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_verified BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now(),
            PRIMARY KEY (id),
            UNIQUE (email)
        )
    """)

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

    # Drop UserRole enum type
    user_role_enum = postgresql.ENUM('ADMIN', 'PRO', 'PARTICULAR', 'EXPERT', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)