# backend/app/routes/similar.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Vehicle
from app.services.search import SearchService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vehicles", tags=["similar"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{vehicle_id}/similar")
async def get_similar_vehicles(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Trouve des véhicules similaires basés sur :
    - Même marque/modèle ou marque similaire
    - Fourchette de prix ±20%
    - Année ±2 ans
    - Type de carburant identique si possible
    """
    try:
        # Récupérer le véhicule de référence
        vehicle = db.get(Vehicle, vehicle_id)
        
        if not vehicle:
            raise HTTPException(status_code=404, detail="Véhicule non trouvé")
        
        # Construire les filtres
        filters = {}
        
        # Marque (même marque ou laisser ouvert si pas de marque)
        if vehicle.make:
            filters["make"] = vehicle.make
        
        # Prix ±20%
        if vehicle.price:
            price_margin = int(vehicle.price * 0.2)
            filters["price_min"] = max(0, vehicle.price - price_margin)
            filters["price_max"] = vehicle.price + price_margin
        
        # Année ±2 ans
        if vehicle.year:
            filters["year_min"] = vehicle.year - 2
            filters["year_max"] = vehicle.year + 2
        
        # Type de carburant (optionnel)
        if vehicle.fuel_type:
            filters["fuel_type"] = vehicle.fuel_type
        
        logger.info(f"Recherche similaire pour {vehicle_id}: {filters}")
        
        # Recherche Elasticsearch
        results = SearchService.search(
            q=vehicle.model if vehicle.model else None,  # Boost sur le modèle
            filters=filters,
            page=1,
            size=10
        )
        
        # Retirer le véhicule lui-même des résultats
        hits = [h for h in results.get('hits', []) if h['id'] != vehicle_id]
        
        return {
            "reference": {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "price": vehicle.price,
                "year": vehicle.year,
                "fuel_type": vehicle.fuel_type
            },
            "total": len(hits),
            "hits": hits[:8],  # Max 8 similaires
            "filters_used": filters
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erreur recherche similaire: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")