# backend/app/config.py
import os
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus, urlparse, urlunparse

# Charger le .env depuis backend/.env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.", file=sys.stderr)

def get_database_url() -> str:
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

class Settings:
    # Database - Utilise la fonction centralisée
    DATABASE_URL: str = get_database_url()

    # Elasticsearch
    ELASTIC_HOST: str = os.getenv("ELASTIC_HOST", "http://localhost:9200")
    ES_INDEX: str = os.getenv("ES_INDEX", "vehicles")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    REDIS_QUEUE_KEY: str = os.getenv("REDIS_QUEUE_KEY", "scraper_queue")

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Application
    APP_NAME: str = "Voiture Search"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()