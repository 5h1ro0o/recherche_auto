# backend/app/schemas_auth.py
"""
Schemas for authentication
This file is kept for backward compatibility and imports from schemas.py
"""
from app.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserOut,
    Token,
    TokenData
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserOut",
    "Token",
    "TokenData"
]
