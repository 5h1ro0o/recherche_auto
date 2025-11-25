# backend/app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

def get_database_url():
    """
    Récupère l'URL de la base de données en gérant les problèmes d'encodage
    """
    default_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicles"

    db_url = os.getenv("DATABASE_URL", default_url)

    # Sur Windows, s'assurer que l'URL est en UTF-8
    if isinstance(db_url, bytes):
        try:
            db_url = db_url.decode('utf-8')
        except UnicodeDecodeError:
            # Si l'encodage UTF-8 échoue, essayer Windows-1252
            db_url = db_url.decode('windows-1252')

    return db_url

DATABASE_URL = get_database_url()

# create engine with UTF-8 encoding
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "client_encoding": "utf8"
    },
    pool_pre_ping=True  # Vérifier la connexion avant utilisation
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Try to import Base from app.models to keep Alembic compatibility
try:
    from app.models import Base  # noqa: F401
except Exception:
    Base = None
