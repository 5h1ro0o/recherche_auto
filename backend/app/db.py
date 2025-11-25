# backend/app/db.py
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus, urlparse, urlunparse

def get_database_url():
    """
    Récupère l'URL de la base de données en gérant les problèmes d'encodage Windows
    """
    default_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicles"

    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        return default_url

    # Sur Windows, s'assurer que l'URL est correctement encodée
    if isinstance(db_url, bytes):
        try:
            db_url = db_url.decode('utf-8')
        except UnicodeDecodeError:
            # Si l'encodage UTF-8 échoue, essayer Windows-1252
            db_url = db_url.decode('windows-1252')

    # Vérifier s'il y a des caractères non-ASCII qui poseraient problème à psycopg2
    try:
        # Essayer d'encoder en ASCII pour détecter les caractères problématiques
        db_url.encode('ascii')
    except UnicodeEncodeError:
        # Il y a des caractères non-ASCII, essayons de les encoder proprement
        print(f"WARNING: DATABASE_URL contains non-ASCII characters", file=sys.stderr)
        print(f"Attempting to URL-encode the connection string...", file=sys.stderr)

        try:
            # Parser l'URL et ré-encoder les parties problématiques
            parsed = urlparse(db_url)

            # Encoder le username et password si nécessaire
            username = quote_plus(parsed.username) if parsed.username else None
            password = quote_plus(parsed.password) if parsed.password else None

            # Reconstruire l'URL
            if username and password:
                netloc = f"{username}:{password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
            else:
                netloc = parsed.netloc

            db_url = urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            print(f"Successfully encoded DATABASE_URL", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Failed to encode DATABASE_URL: {e}", file=sys.stderr)
            print(f"Please use the script: python backend/scripts/generate_database_url.py", file=sys.stderr)
            return default_url

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
