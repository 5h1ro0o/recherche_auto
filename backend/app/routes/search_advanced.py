# backend/app/routes/search_advanced.py
"""Route pour la recherche avancée multi-sources avec filtres stricts"""

import logging
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search-advanced", tags=["search-advanced"])


class AdvancedSearchRequest(BaseModel):
    """Requête de recherche avancée avec filtres stricts"""

    # Filtres obligatoires
    vehicle_type: str = Field("voiture", description="Type de véhicule")

    # Filtres principaux
    make: Optional[str] = Field(None, description="Marque (ex: volkswagen)")
    model: Optional[str] = Field(None, description="Modèle (ex: golf)")

    # Année
    year_min: Optional[int] = Field(None, ge=1950, le=2030, description="Année minimum")
    year_max: Optional[int] = Field(None, ge=1950, le=2030, description="Année maximum")

    # Prix
    price_min: Optional[int] = Field(None, ge=0, description="Prix minimum en €")
    price_max: Optional[int] = Field(None, ge=0, description="Prix maximum en €")

    # Kilométrage
    mileage_min: Optional[int] = Field(None, ge=0, description="Kilométrage minimum en km")
    mileage_max: Optional[int] = Field(None, ge=0, description="Kilométrage maximum en km")

    # Carburant
    fuel_type: Optional[str] = Field(None, description="Type de carburant: essence, diesel, electrique, hybride, gpl")

    # Transmission
    transmission: Optional[str] = Field(None, description="Type de transmission: manuelle, automatique")

    # Localisation
    location: Optional[str] = Field(None, description="Localisation (ville, département)")
    location_radius: Optional[int] = Field(None, ge=0, le=200, description="Rayon en km autour de la localisation")

    # Options supplémentaires
    seller_type: Optional[str] = Field(None, description="Type de vendeur: particulier, professionnel")
    first_registration: Optional[bool] = Field(None, description="Première main uniquement")
    nb_doors: Optional[int] = Field(None, ge=2, le=5, description="Nombre de portes")
    nb_seats: Optional[int] = Field(None, ge=2, le=9, description="Nombre de places")
    color: Optional[str] = Field(None, description="Couleur")

    # Contrôle pagination
    max_pages: int = Field(3, ge=1, le=10, description="Nombre de pages par source")

    # Sources à utiliser
    sources: List[str] = Field(["leboncoin", "autoscout24"], description="Sources à scraper")


class AdvancedSearchResponse(BaseModel):
    """Réponse de recherche avancée"""
    success: bool
    total_results: int
    results: List[Dict[str, Any]]
    sources_stats: Dict[str, Dict[str, Any]]
    filters_applied: Dict[str, Any]
    duration: float
    timestamp: str


def scrape_source(source: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scrape une source avec les filtres donnés
    Cette fonction s'exécute dans un thread séparé
    """
    try:
        logger.info(f"🔍 Scraping {source} avec filtres: {filters}")

        if source == "leboncoin":
            from scrapers.leboncoin_scraper import LeBonCoinScraper
            scraper = LeBonCoinScraper()

            # Construire les paramètres pour LeBonCoin
            search_params = {
                'max_pages': filters.get('max_pages', 3),
                'deep_scrape': False
            }

            # LeBonCoin utilise une recherche textuelle, on construit la query
            query_parts = []
            if filters.get('make'):
                query_parts.append(filters['make'])
            if filters.get('model'):
                query_parts.append(filters['model'])

            search_params['query'] = ' '.join(query_parts) if query_parts else 'voiture'

            # Filtres additionnels
            if filters.get('price_max'):
                search_params['max_price'] = filters['price_max']
            if filters.get('location'):
                search_params['location'] = filters['location']

            results = scraper.scrape(search_params)

        elif source == "autoscout24":
            from scrapers.autoscoot_scraper import AutoScout24Scraper
            scraper = AutoScout24Scraper()

            # Construire les paramètres pour AutoScout24
            search_params = {
                'max_pages': filters.get('max_pages', 3),
                'make': filters.get('make'),
                'model': filters.get('model'),
                'min_year': filters.get('year_min'),
                'max_year': filters.get('year_max'),
                'max_price': filters.get('price_max'),
            }

            # Mapper le type de carburant pour AutoScout24
            fuel_mapping = {
                'essence': 'B',
                'diesel': 'D',
                'electrique': 'E',
                'hybride': 'H'
            }
            if filters.get('fuel_type'):
                search_params['fuel_type'] = fuel_mapping.get(filters['fuel_type'].lower())

            results = scraper.scrape(search_params)

        else:
            logger.warning(f"Source inconnue: {source}")
            return {'source': source, 'results': [], 'error': 'Source inconnue'}

        # Appliquer les filtres post-scraping
        filtered_results = apply_post_filters(results, filters)

        return {
            'source': source,
            'results': filtered_results,
            'count': len(filtered_results),
            'success': True
        }

    except Exception as e:
        logger.exception(f"❌ Erreur scraping {source}: {e}")
        return {
            'source': source,
            'results': [],
            'count': 0,
            'success': False,
            'error': str(e)
        }


def apply_post_filters(results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Applique des filtres supplémentaires sur les résultats
    (pour les filtres non supportés nativement par les scrapers)
    """
    filtered = results

    # Filtre sur le prix minimum
    if filters.get('price_min'):
        filtered = [r for r in filtered if r.get('price') and r['price'] >= filters['price_min']]

    # Filtre sur le kilométrage
    if filters.get('mileage_min'):
        filtered = [r for r in filtered if r.get('mileage') and r['mileage'] >= filters['mileage_min']]
    if filters.get('mileage_max'):
        filtered = [r for r in filtered if r.get('mileage') and r['mileage'] <= filters['mileage_max']]

    # Filtre sur le type de carburant
    if filters.get('fuel_type'):
        fuel_lower = filters['fuel_type'].lower()
        filtered = [r for r in filtered if r.get('fuel_type') and fuel_lower in r['fuel_type'].lower()]

    # Filtre sur la transmission
    if filters.get('transmission'):
        trans_lower = filters['transmission'].lower()
        filtered = [r for r in filtered if r.get('transmission') and trans_lower in r['transmission'].lower()]

    return filtered


@router.post("/search", response_model=AdvancedSearchResponse)
async def advanced_search(request: AdvancedSearchRequest):
    """
    Recherche avancée multi-sources avec filtres stricts

    Combine les résultats de plusieurs sources (LeBonCoin, AutoScout24)
    en appliquant des filtres stricts sur les critères de recherche.
    """
    start_time = datetime.utcnow()

    logger.info(f"🔍 Recherche avancée multi-sources: {request.sources}")
    logger.info(f"   Marque: {request.make}, Modèle: {request.model}")
    logger.info(f"   Prix: {request.price_min}-{request.price_max}€")
    logger.info(f"   Année: {request.year_min}-{request.year_max}")

    # Préparer les filtres
    filters = {
        'make': request.make,
        'model': request.model,
        'year_min': request.year_min,
        'year_max': request.year_max,
        'price_min': request.price_min,
        'price_max': request.price_max,
        'mileage_min': request.mileage_min,
        'mileage_max': request.mileage_max,
        'fuel_type': request.fuel_type,
        'transmission': request.transmission,
        'location': request.location,
        'max_pages': request.max_pages
    }

    # Scraper toutes les sources en parallèle
    all_results = []
    sources_stats = {}

    # Utiliser ThreadPoolExecutor pour paralléliser les scrapers
    with ThreadPoolExecutor(max_workers=len(request.sources)) as executor:
        futures = {
            executor.submit(scrape_source, source, filters): source
            for source in request.sources
        }

        for future in futures:
            source = futures[future]
            try:
                result = future.result(timeout=120)  # Timeout de 2 minutes par source

                sources_stats[source] = {
                    'count': result.get('count', 0),
                    'success': result.get('success', False),
                    'error': result.get('error')
                }

                if result.get('success'):
                    all_results.extend(result.get('results', []))
                    logger.info(f"✅ {source}: {result.get('count', 0)} résultats")
                else:
                    logger.warning(f"⚠️ {source}: {result.get('error', 'Erreur inconnue')}")

            except Exception as e:
                logger.exception(f"❌ Erreur future {source}: {e}")
                sources_stats[source] = {
                    'count': 0,
                    'success': False,
                    'error': str(e)
                }

    # Trier les résultats par prix (croissant)
    def get_sort_price(item):
        price = item.get('price')
        if price is None:
            return float('inf')
        if isinstance(price, str):
            # Enlever espaces et convertir
            try:
                return float(price.replace(' ', '').replace(',', ''))
            except (ValueError, AttributeError):
                return float('inf')
        try:
            return float(price)
        except (ValueError, TypeError):
            return float('inf')

    all_results.sort(key=get_sort_price)

    # Calculer la durée
    duration = (datetime.utcnow() - start_time).total_seconds()

    logger.info(f"🎉 Recherche terminée: {len(all_results)} résultats en {duration:.2f}s")

    return AdvancedSearchResponse(
        success=True,
        total_results=len(all_results),
        results=all_results,
        sources_stats=sources_stats,
        filters_applied=filters,
        duration=duration,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/filters/makes")
async def get_available_makes():
    """Liste des marques disponibles"""
    makes = [
        {"value": "volkswagen", "label": "Volkswagen"},
        {"value": "peugeot", "label": "Peugeot"},
        {"value": "renault", "label": "Renault"},
        {"value": "citroen", "label": "Citroën"},
        {"value": "bmw", "label": "BMW"},
        {"value": "mercedes", "label": "Mercedes-Benz"},
        {"value": "audi", "label": "Audi"},
        {"value": "ford", "label": "Ford"},
        {"value": "toyota", "label": "Toyota"},
        {"value": "honda", "label": "Honda"},
        {"value": "nissan", "label": "Nissan"},
        {"value": "opel", "label": "Opel"},
        {"value": "fiat", "label": "Fiat"},
        {"value": "seat", "label": "Seat"},
        {"value": "skoda", "label": "Skoda"},
        {"value": "hyundai", "label": "Hyundai"},
        {"value": "kia", "label": "Kia"},
        {"value": "mazda", "label": "Mazda"},
        {"value": "volvo", "label": "Volvo"},
        {"value": "mini", "label": "Mini"},
        {"value": "dacia", "label": "Dacia"},
        {"value": "tesla", "label": "Tesla"},
    ]
    return {"makes": makes}


@router.get("/filters/models/{make}")
async def get_models_by_make(make: str):
    """Liste des modèles par marque"""
    # Exemple de modèles (à compléter)
    models_by_make = {
        "volkswagen": ["Golf", "Polo", "Passat", "Tiguan", "T-Roc", "Arteon", "Touareg"],
        "peugeot": ["208", "308", "508", "2008", "3008", "5008"],
        "renault": ["Clio", "Megane", "Captur", "Kadjar", "Scenic", "Talisman"],
        "bmw": ["Série 1", "Série 2", "Série 3", "Série 4", "Série 5", "X1", "X3", "X5"],
        "audi": ["A1", "A3", "A4", "A5", "A6", "Q2", "Q3", "Q5", "Q7"],
        "mercedes": ["Classe A", "Classe B", "Classe C", "Classe E", "GLA", "GLC", "GLE"],
    }

    models = models_by_make.get(make.lower(), [])
    return {"make": make, "models": [{"value": m.lower(), "label": m} for m in models]}


@router.get("/filters/years")
async def get_available_years():
    """Liste des années disponibles"""
    current_year = datetime.now().year
    years = list(range(current_year, 1990, -1))
    return {"years": years}
