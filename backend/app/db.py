# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importer la configuration centralisée qui charge le .env
from app.config import settings

# Force psycopg2 (synchronous) driver for FastAPI routes
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

# create engine with psycopg2 (synchronous driver)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True  # Vérifier la connexion avant utilisation
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Try to import Base from app.models to keep Alembic compatibility
try:
    from app.models import Base  # noqa: F401
except Exception:
    Base = None


# Dependency for FastAPI routes
def get_db():
    """
    Dependency function to get database session.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
