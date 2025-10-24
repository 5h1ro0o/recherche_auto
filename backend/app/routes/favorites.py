import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal
from app.models import Favorite, Vehicle, User
from app.dependencies import get_current_user
from app.schemas import VehicleOut

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=List[VehicleOut])
async def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer mes favoris"""
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()
    
    vehicle_ids = [f.vehicle_id for f in favorites]
    vehicles = db.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).all()
    
    return vehicles

@router.post("/{vehicle_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajouter un véhicule aux favoris"""
    # Vérifier que le véhicule existe
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    # Vérifier si déjà en favoris
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.vehicle_id == vehicle_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Déjà dans les favoris"
        )
    
    # Créer le favori
    favorite = Favorite(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        vehicle_id=vehicle_id
    )
    
    db.add(favorite)
    db.commit()
    
    return {"message": "Ajouté aux favoris", "vehicle_id": vehicle_id}

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retirer un véhicule des favoris"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.vehicle_id == vehicle_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favori non trouvé"
        )
    
    db.delete(favorite)
    db.commit()
    
    return None

@router.get("/check/{vehicle_id}")
async def check_favorite(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vérifier si un véhicule est en favoris"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.vehicle_id == vehicle_id
    ).first()
    
    return {"is_favorite": favorite is not None}