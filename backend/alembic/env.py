import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# --- charger .env (optionnel mais pratique sous Windows) ---
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
# ---------------------------------------------------------

# Si ton projet a la structure backend/app, ajoute le dossier backend au path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

# --------------------------------------------------------------------
# IMPORTANT: importe ici ton Base (déclarative_base) pour fournir target_metadata
# --------------------------------------------------------------------
# Exemple : si tu as backend/app/models.py avec `Base = declarative_base()`
try:
    from app.models import Base  # adapte le module si nécessaire
    target_metadata = Base.metadata
except Exception as e:
    # affiche l'erreur explicite pour debug
    raise RuntimeError("Impossible d'importer app.models.Base — vérifie le chemin/module. Erreur: %s" % e)

# Récupère l'URL depuis la variable d'environnement (ou alembic.ini)
# Utilise la configuration centralisée qui charge le .env et gère l'encodage
try:
    from app.config import settings
    DATABASE_URL = settings.DATABASE_URL
except Exception as e:
    print(f"Warning: Could not load settings from app.config: {e}", file=sys.stderr)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # fallback to value in alembic.ini if present
        DATABASE_URL = config.get_main_option("sqlalchemy.url")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL non défini — vérifie backend/.env ou la variable d'environnement")

# Ne pas utiliser set_main_option car ConfigParser ne supporte pas les % dans les valeurs
# (les % sont interprétés comme syntaxe d'interpolation)
# On va plutôt passer l'URL directement à engine_from_config

# --------------------------------------------------------------------
# Fonctions alembic (générées)
# --------------------------------------------------------------------
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    # Utiliser DATABASE_URL directement au lieu de config.get_main_option
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Créer l'engine directement avec DATABASE_URL pour éviter les problèmes d'interpolation ConfigParser
    from sqlalchemy import create_engine
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,         # utile pour detecter changements de type de colonne
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
