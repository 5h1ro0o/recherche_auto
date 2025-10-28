"""add assisted_requests and proposed_vehicles tables

Revision ID: add_assisted_requests
Revises: add_messages
Create Date: 2025-01-26 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_assisted_requests'
down_revision = 'add_vehicle_is_active'

def upgrade():
    # Create RequestStatus enum type
    request_status_enum = postgresql.ENUM('EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'ANNULEE', name='requeststatus', create_type=True)
    request_status_enum.create(op.get_bind(), checkfirst=True)

    # Create ProposalStatus enum type
    proposal_status_enum = postgresql.ENUM('PENDING', 'FAVORITE', 'REJECTED', name='proposalstatus', create_type=True)
    proposal_status_enum.create(op.get_bind(), checkfirst=True)

    # Table assisted_requests
    op.create_table('assisted_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('expert_id', sa.String(), nullable=True),
        sa.Column('status', request_status_enum, nullable=False, server_default='EN_ATTENTE'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('budget_max', sa.Integer(), nullable=True),
        sa.Column('preferred_fuel_type', sa.String(), nullable=True),
        sa.Column('preferred_transmission', sa.String(), nullable=True),
        sa.Column('max_mileage', sa.Integer(), nullable=True),
        sa.Column('min_year', sa.Integer(), nullable=True),
        sa.Column('ai_parsed_criteria', sa.JSON(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('accepted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('ix_assisted_requests_client_id', 'assisted_requests', ['client_id'])
    op.create_index('ix_assisted_requests_expert_id', 'assisted_requests', ['expert_id'])
    op.create_index('ix_assisted_requests_status', 'assisted_requests', ['status'])
    op.create_index('ix_assisted_requests_created_at', 'assisted_requests', ['created_at'])

    # Table proposed_vehicles
    op.create_table('proposed_vehicles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('vehicle_id', sa.String(), nullable=False),
        sa.Column('status', proposal_status_enum, nullable=False, server_default='PENDING'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['assisted_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE')
    )
    op.create_index('ix_proposed_vehicles_request_id', 'proposed_vehicles', ['request_id'])
    op.create_index('ix_proposed_vehicles_vehicle_id', 'proposed_vehicles', ['vehicle_id'])
    op.create_index('ix_proposed_vehicles_status', 'proposed_vehicles', ['status'])

def downgrade():
    # Drop tables
    op.drop_index('ix_proposed_vehicles_status', 'proposed_vehicles')
    op.drop_index('ix_proposed_vehicles_vehicle_id', 'proposed_vehicles')
    op.drop_index('ix_proposed_vehicles_request_id', 'proposed_vehicles')
    op.drop_table('proposed_vehicles')

    op.drop_index('ix_assisted_requests_created_at', 'assisted_requests')
    op.drop_index('ix_assisted_requests_status', 'assisted_requests')
    op.drop_index('ix_assisted_requests_expert_id', 'assisted_requests')
    op.drop_index('ix_assisted_requests_client_id', 'assisted_requests')
    op.drop_table('assisted_requests')

    # Drop enum types
    proposal_status_enum = postgresql.ENUM('PENDING', 'FAVORITE', 'REJECTED', name='proposalstatus')
    proposal_status_enum.drop(op.get_bind(), checkfirst=True)

    request_status_enum = postgresql.ENUM('EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'ANNULEE', name='requeststatus')
    request_status_enum.drop(op.get_bind(), checkfirst=True)
