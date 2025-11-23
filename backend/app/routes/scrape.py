# backend/app/routes/scrape.py
"""Routes pour le scraping direct des différentes sources"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["scrape"])


class ScrapeRequest(BaseModel):
    """Requête de scraping"""
    source: str = Field(..., description="Source à scraper: leboncoin, lacentrale, autoscout24")
    max_pages: int = Field(default=3, ge=1, le=20, description="Nombre de pages à scraper")

    # Filtres optionnels
    query: Optional[str] = Field(None, description="Requête de recherche (pour leboncoin)")
    make: Optional[str] = Field(None, description="Marque du véhicule")
    model: Optional[str] = Field(None, description="Modèle du véhicule")
    min_year: Optional[int] = Field(None, ge=1950, le=2030)
    max_year: Optional[int] = Field(None, ge=1950, le=2030)
    max_price: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, description="Type de carburant")
    location: Optional[str] = Field(None, description="Localisation")
    deep_scrape: bool = Field(False, description="Scraping approfondi (leboncoin)")


class ScrapeResponse(BaseModel):
    """Réponse de scraping"""
    success: bool
    source: str
    count: int
    results: List[Dict[str, Any]]
    duration: float
    timestamp: str
    message: Optional[str] = None


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_vehicles(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    """
    Scrape direct d'une source de véhicules

    Sources disponibles:
    - leboncoin: Scraping LeBonCoin avec recherche par query
    - lacentrale: Scraping LaCentrale avec marque/modèle
    - autoscout24: Scraping AutoScout24 avec filtres avancés
    """

    start_time = datetime.utcnow()
    valid_sources = ['leboncoin', 'lacentrale', 'autoscout24']

    # Validation de la source
    if request.source not in valid_sources:
        raise HTTPException(
            status_code=400,
            detail=f"Source invalide. Sources disponibles: {', '.join(valid_sources)}"
        )

    logger.info(f"🔵 Scraping {request.source}: {request.max_pages} pages")

    results = []
    scraper = None

    try:
        # Importer le scraper approprié
        if request.source == 'leboncoin':
            from scrapers.leboncoin_scraper import LeBonCoinScraper
            scraper = LeBonCoinScraper()

            search_params = {
                'query': request.query or 'voiture',
                'max_pages': request.max_pages,
                'max_price': request.max_price,
                'location': request.location,
                'deep_scrape': request.deep_scrape
            }

        elif request.source == 'lacentrale':
            from scrapers.lacentrale_scraper import LaCentraleScraper
            scraper = LaCentraleScraper()

            # LaCentrale utilise le format 'marque:modèle'
            query = None
            if request.make:
                query = f"{request.make.lower()}"
                if request.model:
                    query += f":{request.model.lower()}"

            search_params = {
                'query': query or 'volkswagen:golf',
                'max_pages': request.max_pages
            }

        elif request.source == 'autoscout24':
            from scrapers.autoscoot_scraper import AutoScout24Scraper
            scraper = AutoScout24Scraper()

            search_params = {
                'max_pages': request.max_pages,
                'make': request.make,
                'model': request.model,
                'min_year': request.min_year,
                'max_year': request.max_year,
                'max_price': request.max_price,
                'fuel_type': request.fuel_type
            }

        # Exécuter le scraping
        logger.info(f"🚀 Lancement scraping {request.source} avec params: {search_params}")
        results = scraper.scrape(search_params)

        # Calculer la durée
        duration = (datetime.utcnow() - start_time).total_seconds()

        logger.info(f"✅ {request.source}: {len(results)} résultats en {duration:.2f}s")

        # Note: Le scraper gère déjà la fermeture du browser dans son finally block
        # Pas besoin d'appeler scraper.close() ici

        return ScrapeResponse(
            success=True,
            source=request.source,
            count=len(results),
            results=results,
            duration=duration,
            timestamp=datetime.utcnow().isoformat(),
            message=f"{len(results)} véhicules trouvés"
        )

    except ImportError as e:
        logger.error(f"❌ Erreur import scraper {request.source}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraper {request.source} non disponible: {str(e)}"
        )

    except Exception as e:
        logger.exception(f"❌ Erreur scraping {request.source}: {e}")

        duration = (datetime.utcnow() - start_time).total_seconds()

        # Retourner une réponse d'erreur au lieu de lever une exception
        return ScrapeResponse(
            success=False,
            source=request.source,
            count=0,
            results=[],
            duration=duration,
            timestamp=datetime.utcnow().isoformat(),
            message=f"Erreur: {str(e)}"
        )


@router.get("/scrape/sources")
async def get_available_sources():
    """Liste des sources de scraping disponibles"""

    sources = {
        "leboncoin": {
            "name": "LeBonCoin",
            "url": "https://www.leboncoin.fr",
            "available": True,
            "filters": ["query", "max_price", "location", "deep_scrape"]
        },
        "lacentrale": {
            "name": "La Centrale",
            "url": "https://www.lacentrale.fr",
            "available": True,
            "filters": ["make", "model", "max_pages"]
        },
        "autoscout24": {
            "name": "AutoScout24",
            "url": "https://www.autoscout24.fr",
            "available": True,
            "filters": ["make", "model", "min_year", "max_year", "max_price", "fuel_type"]
        }
    }

    return {
        "sources": sources,
        "total": len(sources)
    }


@router.get("/scrape/status")
async def get_scrape_status():
    """Status du système de scraping"""

    try:
        # Vérifier la disponibilité des scrapers
        scrapers_status = {}

        # LeBonCoin
        try:
            from scrapers.leboncoin_scraper import LeBonCoinScraper
            scrapers_status['leboncoin'] = {
                "available": True,
                "status": "ready"
            }
        except Exception as e:
            scrapers_status['leboncoin'] = {
                "available": False,
                "status": "error",
                "error": str(e)
            }

        # LaCentrale
        try:
            from scrapers.lacentrale_scraper import LaCentraleScraper
            scrapers_status['lacentrale'] = {
                "available": True,
                "status": "ready"
            }
        except Exception as e:
            scrapers_status['lacentrale'] = {
                "available": False,
                "status": "error",
                "error": str(e)
            }

        # AutoScout24
        try:
            from scrapers.autoscoot_scraper import AutoScout24Scraper
            scrapers_status['autoscout24'] = {
                "available": True,
                "status": "ready"
            }
        except Exception as e:
            scrapers_status['autoscout24'] = {
                "available": False,
                "status": "error",
                "error": str(e)
            }

        return {
            "status": "operational",
            "scrapers": scrapers_status,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Erreur status scraping: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}"
        )
