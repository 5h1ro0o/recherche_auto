# backend/app/routes/pro.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

from app.db import SessionLocal
from app.models import User, Vehicle, UserRole, Message, Favorite
from app.schemas import VehicleCreate, VehicleOut, VehicleUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/pro", tags=["professional"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_pro_or_admin(current_user: User = Depends(get_current_user)):
    """Vérifier que l'utilisateur est PRO ou ADMIN"""
    if current_user.role not in [UserRole.PRO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte professionnel requis"
        )
    return current_user

# ============ GESTION STOCK ============

@router.get("/stock", response_model=List[VehicleOut])
async def get_my_stock(
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None
):
    """Récupérer mon stock de véhicules"""
    query = db.query(Vehicle).filter(
        Vehicle.professional_user_id == current_user.id
    )
    
    # Filtrer par statut
    if status_filter == "active":
        query = query.filter(Vehicle.is_active == True)
    elif status_filter == "inactive":
        query = query.filter(Vehicle.is_active == False)
    
    # Recherche
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vehicle.title.ilike(search_term)) |
            (Vehicle.make.ilike(search_term)) |
            (Vehicle.model.ilike(search_term))
        )
    
    # Pagination
    total = query.count()
    vehicles = query.order_by(
        Vehicle.created_at.desc()
    ).offset((page - 1) * size).limit(size).all()
    
    return vehicles

@router.post("/stock", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def add_vehicle_to_stock(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Ajouter un véhicule à mon stock"""
    
    # Vérifier VIN unique si fourni
    if vehicle_data.vin:
        existing = db.query(Vehicle).filter(Vehicle.vin == vehicle_data.vin).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un véhicule avec ce VIN existe déjà"
            )
    
    vehicle = Vehicle(
        id=str(uuid.uuid4()),
        professional_user_id=current_user.id,
        is_active=True,
        **vehicle_data.dict(exclude_unset=True)
    )
    
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    # TODO: Indexer dans Elasticsearch
    
    return vehicle

@router.get("/stock/{vehicle_id}", response_model=VehicleOut)
async def get_my_vehicle(
    vehicle_id: str,
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Récupérer un véhicule de mon stock"""
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.professional_user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    return vehicle

@router.patch("/stock/{vehicle_id}", response_model=VehicleOut)
async def update_my_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Modifier un de mes véhicules"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.professional_user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    # Vérifier VIN unique si modifié
    if vehicle_update.vin and vehicle_update.vin != vehicle.vin:
        existing = db.query(Vehicle).filter(Vehicle.vin == vehicle_update.vin).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un véhicule avec ce VIN existe déjà"
            )
    
    # Mettre à jour
    for key, value in vehicle_update.dict(exclude_unset=True).items():
        setattr(vehicle, key, value)
    
    vehicle.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(vehicle)
    
    # TODO: Réindexer dans Elasticsearch
    
    return vehicle

@router.delete("/stock/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_vehicle(
    vehicle_id: str,
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Supprimer un de mes véhicules"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.professional_user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    db.delete(vehicle)
    db.commit()
    
    # TODO: Supprimer de Elasticsearch
    
    return None

@router.post("/stock/{vehicle_id}/toggle-visibility")
async def toggle_vehicle_visibility(
    vehicle_id: str,
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Activer/désactiver la visibilité d'un véhicule"""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.professional_user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    vehicle.is_active = not vehicle.is_active
    vehicle.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "vehicle_id": vehicle_id,
        "is_active": vehicle.is_active,
        "message": f"Véhicule {'activé' if vehicle.is_active else 'désactivé'}"
    }

# ============ STATISTIQUES ============

@router.get("/stats")
async def get_my_stats(
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Récupérer mes statistiques globales"""
    
    # Compteurs véhicules
    total_vehicles = db.query(Vehicle).filter(
        Vehicle.professional_user_id == current_user.id
    ).count()
    
    active_vehicles = db.query(Vehicle).filter(
        Vehicle.professional_user_id == current_user.id,
        Vehicle.is_active == True
    ).count()
    
    # Statistiques 30 derniers jours
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_additions = db.query(Vehicle).filter(
        Vehicle.professional_user_id == current_user.id,
        Vehicle.created_at >= thirty_days_ago
    ).count()
    
    # Favoris total sur mes véhicules
    total_favorites = db.query(Favorite).join(Vehicle).filter(
        Vehicle.professional_user_id == current_user.id
    ).count()
    
    # Messages reçus (approximation via conversations)
    messages_received = db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.created_at >= thirty_days_ago
    ).count()
    
    # Véhicule le plus populaire (le plus de favoris)
    most_popular = db.query(
        Vehicle.id,
        Vehicle.title,
        Vehicle.make,
        Vehicle.model,
        func.count(Favorite.id).label('favorites_count')
    ).outerjoin(Favorite).filter(
        Vehicle.professional_user_id == current_user.id
    ).group_by(Vehicle.id).order_by(
        func.count(Favorite.id).desc()
    ).first()
    
    return {
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "inactive_vehicles": total_vehicles - active_vehicles,
        "recent_additions": recent_additions,
        "total_favorites": total_favorites,
        "messages_received_30d": messages_received,
        "most_popular_vehicle": {
            "id": most_popular.id,
            "title": most_popular.title or f"{most_popular.make} {most_popular.model}",
            "favorites": most_popular.favorites_count
        } if most_popular and most_popular.favorites_count > 0 else None
    }

@router.get("/stats/vehicles-by-month")
async def get_vehicles_by_month(
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db),
    months: int = Query(6, ge=3, le=12)
):
    """Statistiques véhicules ajoutés par mois"""
    
    # Requête SQL avec GROUP BY mois
    results = db.query(
        extract('year', Vehicle.created_at).label('year'),
        extract('month', Vehicle.created_at).label('month'),
        func.count(Vehicle.id).label('count')
    ).filter(
        Vehicle.professional_user_id == current_user.id,
        Vehicle.created_at >= datetime.utcnow() - timedelta(days=months * 30)
    ).group_by(
        extract('year', Vehicle.created_at),
        extract('month', Vehicle.created_at)
    ).order_by(
        extract('year', Vehicle.created_at),
        extract('month', Vehicle.created_at)
    ).all()
    
    # Formater les données
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                   'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    labels = []
    data = []
    
    for result in results:
        month_name = month_names[int(result.month) - 1]
        labels.append(f"{month_name} {int(result.year)}")
        data.append(result.count)
    
    return {
        "labels": labels,
        "data": data
    }

@router.get("/stats/price-distribution")
async def get_price_distribution(
    current_user: User = Depends(require_pro_or_admin),
    db: Session = Depends(get_db)
):
    """Distribution des prix de mon stock"""
    
    vehicles = db.query(Vehicle.price).filter(
        Vehicle.professional_user_id == current_user.id,
        Vehicle.price.isnot(None)
    ).all()
    
    prices = [v.price for v in vehicles]
    
    if not prices:
        return {
            "ranges": [],
            "counts": []
        }
    
    # Créer des tranches de prix
    max_price = max(prices)
    ranges = [
        (0, 5000),
        (5000, 10000),
        (10000, 15000),
        (15000, 20000),
        (20000, 30000),
        (30000, max_price + 1)
    ]
    
    labels = []
    counts = []
    
    for min_p, max_p in ranges:
        count = sum(1 for p in prices if min_p <= p < max_p)
        if count > 0 or max_p <= 30000:  # Afficher jusqu'à 30k même si vide
            label = f"{min_p//1000}-{max_p//1000}k€" if max_p <= 30000 else f"+{min_p//1000}k€"
            labels.append(label)
            counts.append(count)
    
    return {
        "labels": labels,
        "data": counts
    }