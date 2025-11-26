"""create_assisted_requests_and_proposed_vehicles

Revision ID: 3b6e29d6f3ac
Revises: add_scraper_logs
Create Date: 2025-11-26 11:56:50.652271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3b6e29d6f3ac'
down_revision: Union[str, Sequence[str], None] = 'add_scraper_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Créer l'enum RequestStatus
    op.execute("""
        CREATE TYPE requeststatus AS ENUM ('EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'ANNULEE')
    """)

    # Créer l'enum ProposalStatus
    op.execute("""
        CREATE TYPE proposalstatus AS ENUM ('PENDING', 'FAVORITE', 'REJECTED')
    """)

    # Créer la table assisted_requests
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
        sa.Column('ai_parsed_criteria', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('accepted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='SET NULL')
    )

    # Créer les index
    op.create_index('ix_assisted_requests_client_id', 'assisted_requests', ['client_id'])
    op.create_index('ix_assisted_requests_expert_id', 'assisted_requests', ['expert_id'])
    op.create_index('ix_assisted_requests_status', 'assisted_requests', ['status'])
    op.create_index('ix_assisted_requests_created_at', 'assisted_requests', ['created_at'])

    # Créer la table proposed_vehicles
    op.create_table(
        'proposed_vehicles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('vehicle_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'FAVORITE', 'REJECTED', name='proposalstatus'), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['assisted_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE')
    )

    # Créer les index
    op.create_index('ix_proposed_vehicles_request_id', 'proposed_vehicles', ['request_id'])
    op.create_index('ix_proposed_vehicles_vehicle_id', 'proposed_vehicles', ['vehicle_id'])
    op.create_index('ix_proposed_vehicles_status', 'proposed_vehicles', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_proposed_vehicles_status', 'proposed_vehicles')
    op.drop_index('ix_proposed_vehicles_vehicle_id', 'proposed_vehicles')
    op.drop_index('ix_proposed_vehicles_request_id', 'proposed_vehicles')
    op.drop_table('proposed_vehicles')

    op.drop_index('ix_assisted_requests_created_at', 'assisted_requests')
    op.drop_index('ix_assisted_requests_status', 'assisted_requests')
    op.drop_index('ix_assisted_requests_expert_id', 'assisted_requests')
    op.drop_index('ix_assisted_requests_client_id', 'assisted_requests')
    op.drop_table('assisted_requests')

    op.execute('DROP TYPE proposalstatus')
    op.execute('DROP TYPE requeststatus')
