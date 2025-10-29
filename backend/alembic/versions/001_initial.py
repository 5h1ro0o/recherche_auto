"""Initial schema with all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-10-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'PRO', 'PARTICULAR', 'EXPERT', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # Create vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('make', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('vin', sa.String(), nullable=True),
        sa.Column('fuel_type', sa.String(), nullable=True),
        sa.Column('transmission', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('images', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('source_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('location_lat', sa.String(), nullable=True),
        sa.Column('location_lon', sa.String(), nullable=True),
        sa.Column('location_city', sa.String(), nullable=True),
        sa.Column('professional_user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['professional_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vehicles_make'), 'vehicles', ['make'], unique=False)
    op.create_index(op.f('ix_vehicles_model'), 'vehicles', ['model'], unique=False)
    op.create_index(op.f('ix_vehicles_price'), 'vehicles', ['price'], unique=False)
    op.create_index(op.f('ix_vehicles_vin'), 'vehicles', ['vin'], unique=True)
    op.create_index(op.f('ix_vehicles_created_at'), 'vehicles', ['created_at'], unique=False)
    op.create_index(op.f('ix_vehicles_professional_user_id'), 'vehicles', ['professional_user_id'], unique=False)

    # Create favorites table
    op.create_table(
        'favorites',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('vehicle_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_favorites_user_id'), 'favorites', ['user_id'], unique=False)
    op.create_index(op.f('ix_favorites_vehicle_id'), 'favorites', ['vehicle_id'], unique=False)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('criteria', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('frequency', sa.String(), nullable=True, server_default='daily'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_sent_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_user_id'), 'alerts', ['user_id'], unique=False)

    # Create search_history table
    op.create_table(
        'search_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('query', sa.String(), nullable=True),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('results_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_history_user_id'), 'search_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_search_history_created_at'), 'search_history', ['created_at'], unique=False)

    # Create assisted_requests table
    op.create_table(
        'assisted_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('expert_id', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'ANNULEE', name='requeststatus'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('budget_max', sa.Integer(), nullable=True),
        sa.Column('preferred_fuel_type', sa.String(), nullable=True),
        sa.Column('preferred_transmission', sa.String(), nullable=True),
        sa.Column('max_mileage', sa.Integer(), nullable=True),
        sa.Column('min_year', sa.Integer(), nullable=True),
        sa.Column('ai_parsed_criteria', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.Column('accepted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assisted_requests_client_id'), 'assisted_requests', ['client_id'], unique=False)
    op.create_index(op.f('ix_assisted_requests_expert_id'), 'assisted_requests', ['expert_id'], unique=False)
    op.create_index(op.f('ix_assisted_requests_status'), 'assisted_requests', ['status'], unique=False)
    op.create_index(op.f('ix_assisted_requests_created_at'), 'assisted_requests', ['created_at'], unique=False)

    # Create proposed_vehicles table
    op.create_table(
        'proposed_vehicles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('vehicle_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'FAVORITE', 'REJECTED', name='proposalstatus'), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['request_id'], ['assisted_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposed_vehicles_request_id'), 'proposed_vehicles', ['request_id'], unique=False)
    op.create_index(op.f('ix_proposed_vehicles_vehicle_id'), 'proposed_vehicles', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_proposed_vehicles_status'), 'proposed_vehicles', ['status'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('recipient_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('read_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_messages_recipient_id'), 'messages', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_messages_is_read'), 'messages', ['is_read'], unique=False)
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)


def downgrade():
    op.drop_table('messages')
    op.drop_table('proposed_vehicles')
    op.drop_table('assisted_requests')
    op.drop_table('search_history')
    op.drop_table('alerts')
    op.drop_table('favorites')
    op.drop_table('vehicles')
    op.drop_table('users')
