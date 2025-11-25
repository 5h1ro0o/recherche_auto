# backend/app/auth.py
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import base64
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Configuration du hashing de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash_password(password: str) -> str:
    """
    Pré-hashe le mot de passe avec SHA256 pour éviter la limitation de 72 bytes de bcrypt.
    Retourne une chaîne base64 du hash SHA256.
    """
    # Hasher avec SHA256
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256(password_bytes).digest()
    # Encoder en base64 pour avoir une chaîne ASCII valide
    return base64.b64encode(sha256_hash).decode('ascii')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    # Pré-hasher avant de vérifier
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash un mot de passe"""
    # Pré-hasher avec SHA256 pour gérer les mots de passe > 72 bytes
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token JWT d'accès"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Créer un token JWT de rafraîchissement"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """Décoder un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None