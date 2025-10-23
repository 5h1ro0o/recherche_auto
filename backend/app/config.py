# backend/app/config.py
import os
from functools import lru_cache

class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:changeme@127.0.0.1:5432/vehicles"
    )
    
    # Elasticsearch
    ELASTIC_HOST: str = os.getenv("ELASTIC_HOST", "http://localhost:9200")
    ES_INDEX: str = os.getenv("ES_INDEX", "vehicles")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    
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