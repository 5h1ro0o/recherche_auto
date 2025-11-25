# backend/app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://app:changeme@127.0.0.1:5432/vehicles"
)

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
