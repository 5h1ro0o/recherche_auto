# backend/app/routes/url_import.py
"""
Routes pour l'import d'annonces depuis une URL
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging

from app.services.url_import_service import url_import_service
from app.models import Vehicle
from app.db import SessionLocal
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["import"])


class URLImportRequest(BaseModel):
    """Request body pour importer une URL"""
    url: str
    save_to_favorites: bool = False


class URLImportResponse(BaseModel):
    """Response pour l'import d'URL"""
    success: bool
    message: str
    vehicle: Optional[dict] = None
    vehicle_id: Optional[str] = None


@router.post("/url", response_model=URLImportResponse)
async def import_from_url(
    request: URLImportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Importe une annonce depuis une URL spécifique

    Supports:
    - LeBonCoin
    - La Centrale
    - AutoScout24
    """
    try:
        logger.info(f"📥 Import URL demandé par user {current_user.get('id')}: {request.url}")

        # Extraire les données de l'URL
        vehicle_data = url_import_service.import_from_url(
            url=request.url,
            user_id=current_user.get('id')
        )

        if not vehicle_data:
            raise HTTPException(status_code=400, detail="Impossible d'extraire les données de l'URL")

        # Sauvegarder dans la base de données
        db = SessionLocal()
        try:
            # Vérifier si l'URL existe déjà
            existing = db.query(Vehicle).filter(
                Vehicle.source_ids['url'].astext == request.url
            ).first()

            if existing:
                logger.info(f"✅ Véhicule déjà existant: {existing.id}")
                return URLImportResponse(
                    success=True,
                    message="Ce véhicule existe déjà dans la base de données",
                    vehicle=None,
                    vehicle_id=existing.id
                )

            # Créer un nouveau véhicule
            vehicle = Vehicle(
                id=vehicle_data['id'],
                title=vehicle_data.get('title'),
                make=vehicle_data.get('make'),
                model=vehicle_data.get('model'),
                price=vehicle_data.get('price'),
                description=vehicle_data.get('description'),
                images=vehicle_data.get('images', []),
                location_city=vehicle_data.get('location_city'),
                source_ids=vehicle_data.get('source_ids', {})
            )

            db.add(vehicle)
            db.commit()
            db.refresh(vehicle)

            logger.info(f"✅ Véhicule importé avec succès: {vehicle.id}")

            # Optionnel : Ajouter aux favoris
            if request.save_to_favorites:
                from app.models import Favorite
                import uuid

                favorite = Favorite(
                    id=str(uuid.uuid4()),
                    user_id=current_user.get('id'),
                    vehicle_id=vehicle.id
                )
                db.add(favorite)
                db.commit()
                logger.info(f"⭐ Ajouté aux favoris")

            return URLImportResponse(
                success=True,
                message="Véhicule importé avec succès",
                vehicle={
                    'id': vehicle.id,
                    'title': vehicle.title,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'price': vehicle.price,
                    'images': vehicle.images
                },
                vehicle_id=vehicle.id
            )

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Erreur sauvegarde DB: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde: {str(e)}")
        finally:
            db.close()

    except ValueError as e:
        logger.error(f"❌ URL non valide: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"❌ Erreur import URL: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'import: {str(e)}")


@router.get("/supported-sites")
async def get_supported_sites():
    """Retourne la liste des sites supportés pour l'import"""
    return {
        "supported_sites": [
            {
                "name": "LeBonCoin",
                "domain": "leboncoin.fr",
                "example": "https://www.leboncoin.fr/voitures/123456.htm"
            },
            {
                "name": "La Centrale",
                "domain": "lacentrale.fr",
                "example": "https://www.lacentrale.fr/auto-occasion-annonce-123456.html"
            },
            {
                "name": "AutoScout24",
                "domain": "autoscout24.fr",
                "example": "https://www.autoscout24.fr/offres/123456"
            }
        ]
    }
