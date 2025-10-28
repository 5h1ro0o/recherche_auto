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
    # Create RequestStatus enum type if it doesn't exist using raw SQL
    conn = op.get_bind()

    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'requeststatus');"
    ))
    if not result.scalar():
        conn.execute(sa.text(
            "CREATE TYPE requeststatus AS ENUM ('EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'ANNULEE')"
        ))
        conn.commit()

    # Create ProposalStatus enum type if it doesn't exist using raw SQL
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'proposalstatus');"
    ))
    if not result.scalar():
        conn.execute(sa.text(
            "CREATE TYPE proposalstatus AS ENUM ('PENDING', 'FAVORITE', 'REJECTED')"
        ))
        conn.commit()

    # Table assisted_requests - using raw SQL to avoid ENUM auto-creation
    op.execute("""
        CREATE TABLE assisted_requests (
            id VARCHAR NOT NULL,
            client_id VARCHAR NOT NULL,
            expert_id VARCHAR,
            status requeststatus NOT NULL DEFAULT 'EN_ATTENTE',
            description TEXT NOT NULL,
            budget_max INTEGER,
            preferred_fuel_type VARCHAR,
            preferred_transmission VARCHAR,
            max_mileage INTEGER,
            min_year INTEGER,
            ai_parsed_criteria JSON DEFAULT '{}',
            created_at TIMESTAMP DEFAULT now(),
            accepted_at TIMESTAMP,
            completed_at TIMESTAMP,
            PRIMARY KEY (id),
            FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (expert_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    op.create_index('ix_assisted_requests_client_id', 'assisted_requests', ['client_id'])
    op.create_index('ix_assisted_requests_expert_id', 'assisted_requests', ['expert_id'])
    op.create_index('ix_assisted_requests_status', 'assisted_requests', ['status'])
    op.create_index('ix_assisted_requests_created_at', 'assisted_requests', ['created_at'])

    # Table proposed_vehicles - using raw SQL to avoid ENUM auto-creation
    op.execute("""
        CREATE TABLE proposed_vehicles (
            id VARCHAR NOT NULL,
            request_id VARCHAR NOT NULL,
            vehicle_id VARCHAR NOT NULL,
            status proposalstatus NOT NULL DEFAULT 'PENDING',
            message TEXT,
            rejection_reason TEXT,
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY (request_id) REFERENCES assisted_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
        )
    """)
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
