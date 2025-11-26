"""add_tinder_features_to_proposals

Revision ID: ebb543dd0499
Revises: 3b6e29d6f3ac
Create Date: 2025-11-26 11:37:40.471444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebb543dd0499'
down_revision: Union[str, Sequence[str], None] = '3b6e29d6f3ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ajouter la colonne client_feedback
    op.add_column('proposed_vehicles', sa.Column('client_feedback', sa.Text(), nullable=True))

    # Modifier l'enum ProposalStatus pour ajouter LIKED et SUPER_LIKED
    # PostgreSQL nécessite d'utiliser ALTER TYPE ... ADD VALUE
    op.execute("ALTER TYPE proposalstatus ADD VALUE IF NOT EXISTS 'LIKED'")
    op.execute("ALTER TYPE proposalstatus ADD VALUE IF NOT EXISTS 'SUPER_LIKED'")

    # Migrer les anciennes valeurs FAVORITE vers LIKED (si elles existent)
    op.execute("""
        UPDATE proposed_vehicles
        SET status = 'LIKED'
        WHERE status = 'FAVORITE'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remettre LIKED vers FAVORITE
    op.execute("""
        UPDATE proposed_vehicles
        SET status = 'FAVORITE'
        WHERE status IN ('LIKED', 'SUPER_LIKED')
    """)

    # Supprimer la colonne client_feedback
    op.drop_column('proposed_vehicles', 'client_feedback')

    # Note: On ne peut pas supprimer les valeurs d'un enum en PostgreSQL facilement
    # donc on les laisse (LIKED et SUPER_LIKED resteront dans l'enum)
