# backend/app/routes/auth.py
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db import SessionLocal
from app import models, schemas, auth
from app.dependencies import get_db, get_current_user, get_current_active_user
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur
    """
    # Vérifier si l'email existe déjà
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    user_id = str(uuid.uuid4())
    hashed_password = auth.get_password_hash(user_data.password)
    
    new_user = models.User(
        id=user_id,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=True,
        is_verified=False  # Nécessite vérification email (à implémenter plus tard)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Nouvel utilisateur créé: {new_user.email} (role: {new_user.role})")
    return new_user

@router.post("/login", response_model=schemas.Token)
async def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Connexion et génération de tokens JWT
    """
    # Récupérer l'utilisateur
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier le mot de passe
    if not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Créer les tokens
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role.value, "user_id": user.id}
    )
    refresh_token = auth.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    logger.info(f"Connexion réussie: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Rafraîchir l'access token avec un refresh token
    """
    payload = auth.decode_token(refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide"
        )
    
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur invalide"
        )
    
    # Générer de nouveaux tokens
    new_access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role.value, "user_id": user.id}
    )
    new_refresh_token = auth.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=schemas.UserOut)
async def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """
    Récupérer les informations de l'utilisateur connecté
    """
    return current_user

@router.patch("/me", response_model=schemas.UserOut)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour les informations de l'utilisateur connecté
    """
    # Vérifier si l'email est déjà utilisé par un autre compte
    if user_update.email and user_update.email != current_user.email:
        existing = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
    
    # Mettre à jour les champs
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Profil mis à jour: {current_user.email}")
    return current_user

@router.post("/logout")
async def logout(current_user: models.User = Depends(get_current_user)):
    """
    Déconnexion (côté client, supprimer le token)
    Note: Avec JWT, la déconnexion est principalement côté client
    Pour une vraie révocation, il faudrait une blacklist Redis
    """
    logger.info(f"Déconnexion: {current_user.email}")
    return {"message": "Déconnexion réussie"}