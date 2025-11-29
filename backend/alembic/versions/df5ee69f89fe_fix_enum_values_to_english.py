"""fix_enum_values_to_english

Revision ID: df5ee69f89fe
Revises: ebb543dd0499
Create Date: 2025-11-26 12:10:46.762838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df5ee69f89fe'
down_revision: Union[str, Sequence[str], None] = 'ebb543dd0499'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Convert ENUM values from French to English."""

    # PostgreSQL ne permet pas de modifier directement les valeurs d'un ENUM
    # On doit créer un nouveau type, migrer les données, puis remplacer l'ancien

    # 1. Créer un nouveau type ENUM avec les valeurs anglaises
    op.execute("""
        CREATE TYPE requeststatus_new AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
    """)

    # 2. Convertir la colonne pour utiliser le nouveau type
    #    On doit d'abord convertir en text, puis vers le nouveau type
    op.execute("""
        ALTER TABLE assisted_requests
        ALTER COLUMN status TYPE text
    """)

    # 3. Mapper les anciennes valeurs françaises vers les nouvelles valeurs anglaises
    op.execute("""
        UPDATE assisted_requests SET status =
            CASE status
                WHEN 'EN_ATTENTE' THEN 'PENDING'
                WHEN 'EN_COURS' THEN 'IN_PROGRESS'
                WHEN 'TERMINEE' THEN 'COMPLETED'
                WHEN 'ANNULEE' THEN 'CANCELLED'
                ELSE status
            END
    """)

    # 4. Convertir la colonne vers le nouveau type ENUM
    op.execute("""
        ALTER TABLE assisted_requests
        ALTER COLUMN status TYPE requeststatus_new
        USING status::requeststatus_new
    """)

    # 5. Supprimer l'ancien type
    op.execute("DROP TYPE requeststatus")

    # 6. Renommer le nouveau type
    op.execute("ALTER TYPE requeststatus_new RENAME TO requeststatus")


def downgrade() -> None:
    """Downgrade schema - Convert ENUM values from English back to French."""

    # Créer un nouveau type ENUM avec les valeurs françaises
    op.execute("""
        CREATE TYPE requeststatus_new AS ENUM ('EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'ANNULEE')
    """)

    # Convertir la colonne en text
    op.execute("""
        ALTER TABLE assisted_requests
        ALTER COLUMN status TYPE text
    """)

    # Mapper les valeurs anglaises vers françaises
    op.execute("""
        UPDATE assisted_requests SET status =
            CASE status
                WHEN 'PENDING' THEN 'EN_ATTENTE'
                WHEN 'IN_PROGRESS' THEN 'EN_COURS'
                WHEN 'COMPLETED' THEN 'TERMINEE'
                WHEN 'CANCELLED' THEN 'ANNULEE'
                ELSE status
            END
    """)

    # Convertir vers le nouveau type
    op.execute("""
        ALTER TABLE assisted_requests
        ALTER COLUMN status TYPE requeststatus_new
        USING status::requeststatus_new
    """)

    # Supprimer l'ancien et renommer
    op.execute("DROP TYPE requeststatus")
    op.execute("ALTER TYPE requeststatus_new RENAME TO requeststatus")
