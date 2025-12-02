"""add encyclopedia relations tables

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2025-01-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Créer la table de liaison Engine ↔ CarModel
    op.create_table(
        'engine_model_associations',
        sa.Column('engine_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engine_id'], ['engines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['car_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('engine_id', 'model_id')
    )

    # Index pour améliorer les performances
    op.create_index('idx_engine_model_engine', 'engine_model_associations', ['engine_id'])
    op.create_index('idx_engine_model_model', 'engine_model_associations', ['model_id'])

    # Créer la table de liaison Transmission ↔ CarModel
    op.create_table(
        'transmission_model_associations',
        sa.Column('transmission_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['transmission_id'], ['transmissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['car_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('transmission_id', 'model_id')
    )

    # Index
    op.create_index('idx_transmission_model_transmission', 'transmission_model_associations', ['transmission_id'])
    op.create_index('idx_transmission_model_model', 'transmission_model_associations', ['model_id'])

    # Créer la table de liaison Engine ↔ Transmission
    op.create_table(
        'engine_transmission_associations',
        sa.Column('engine_id', sa.String(), nullable=False),
        sa.Column('transmission_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engine_id'], ['engines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transmission_id'], ['transmissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('engine_id', 'transmission_id')
    )

    # Index
    op.create_index('idx_engine_transmission_engine', 'engine_transmission_associations', ['engine_id'])
    op.create_index('idx_engine_transmission_transmission', 'engine_transmission_associations', ['transmission_id'])


def downgrade() -> None:
    # Supprimer les tables de liaison dans l'ordre inverse
    op.drop_index('idx_engine_transmission_transmission', table_name='engine_transmission_associations')
    op.drop_index('idx_engine_transmission_engine', table_name='engine_transmission_associations')
    op.drop_table('engine_transmission_associations')

    op.drop_index('idx_transmission_model_model', table_name='transmission_model_associations')
    op.drop_index('idx_transmission_model_transmission', table_name='transmission_model_associations')
    op.drop_table('transmission_model_associations')

    op.drop_index('idx_engine_model_model', table_name='engine_model_associations')
    op.drop_index('idx_engine_model_engine', table_name='engine_model_associations')
    op.drop_table('engine_model_associations')
