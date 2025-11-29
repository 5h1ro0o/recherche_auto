# backend/app/routes/search_advanced.py
"""Route pour la recherche avancée multi-sources avec filtres stricts"""

import logging
import asyncio
import unicodedata
import os
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search-advanced", tags=["search-advanced"])

# Configuration pour l'API Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def normalize_text(text: str) -> str:
    """
    Normalise un texte en supprimant les accents et en le mettant en minuscules.

    Exemple: "Série 1" -> "serie 1"
    """
    if not text:
        return ""
    # Décomposer les caractères Unicode (sépare les lettres des accents)
    nfd = unicodedata.normalize('NFD', text)
    # Filtrer les marques diacritiques (accents)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    return without_accents.lower()


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

    # Carrosserie
    body_type: Optional[str] = Field(None, description="Type de carrosserie: berline, break, suv, coupe, cabriolet, monospace, utilitaire")

    # Puissance
    horsepower_min: Optional[int] = Field(None, ge=0, description="Puissance minimum en chevaux")
    horsepower_max: Optional[int] = Field(None, ge=0, description="Puissance maximum en chevaux")
    horsepower_fiscal_min: Optional[int] = Field(None, ge=0, description="Puissance fiscale minimum (CV)")
    horsepower_fiscal_max: Optional[int] = Field(None, ge=0, description="Puissance fiscale maximum (CV)")

    # Localisation
    location: Optional[str] = Field(None, description="Localisation (ville, département)")
    location_radius: Optional[int] = Field(None, ge=0, le=200, description="Rayon en km autour de la localisation")

    # Options vendeur
    seller_type: Optional[str] = Field(None, description="Type de vendeur: particulier, professionnel")
    first_registration: Optional[bool] = Field(None, description="Première main uniquement")

    # Caractéristiques du véhicule
    nb_doors: Optional[int] = Field(None, ge=2, le=5, description="Nombre de portes")
    nb_seats: Optional[int] = Field(None, ge=2, le=9, description="Nombre de places")
    color: Optional[str] = Field(None, description="Couleur extérieure")
    color_interior: Optional[str] = Field(None, description="Couleur intérieure")
    metallic_color: Optional[bool] = Field(None, description="Couleur métallisée")

    # Normes et contrôles
    emission_class: Optional[str] = Field(None, description="Classe d'émission (Euro 5, Euro 6, Euro 6d-TEMP)")
    critair: Optional[str] = Field(None, description="Crit'Air (0, 1, 2, 3, 4, 5)")
    co2_max: Optional[int] = Field(None, ge=0, description="Émissions CO2 maximum en g/km")
    technical_control_ok: Optional[bool] = Field(None, description="Contrôle technique OK")

    # Historique
    non_smoker: Optional[bool] = Field(None, description="Véhicule non fumeur")
    no_accident: Optional[bool] = Field(None, description="Jamais accidenté")
    service_history: Optional[bool] = Field(None, description="Carnet d'entretien")
    warranty: Optional[bool] = Field(None, description="Sous garantie")
    manufacturer_warranty: Optional[bool] = Field(None, description="Garantie constructeur")

    # Équipements confort
    climate_control: Optional[str] = Field(None, description="Climatisation: none, manual, automatic, bi_zone, tri_zone")
    leather_interior: Optional[bool] = Field(None, description="Intérieur cuir")
    sunroof: Optional[bool] = Field(None, description="Toit ouvrant")
    panoramic_roof: Optional[bool] = Field(None, description="Toit panoramique")
    heated_seats: Optional[bool] = Field(None, description="Sièges chauffants")
    electric_seats: Optional[bool] = Field(None, description="Sièges électriques")
    parking_sensors: Optional[bool] = Field(None, description="Capteurs de stationnement")
    parking_camera: Optional[bool] = Field(None, description="Caméra de recul")
    reversing_camera: Optional[bool] = Field(None, description="Caméra de recul")

    # Équipements technologie
    gps: Optional[bool] = Field(None, description="GPS / Navigation")
    bluetooth: Optional[bool] = Field(None, description="Bluetooth")
    apple_carplay: Optional[bool] = Field(None, description="Apple CarPlay")
    android_auto: Optional[bool] = Field(None, description="Android Auto")
    cruise_control: Optional[bool] = Field(None, description="Régulateur de vitesse")
    adaptive_cruise_control: Optional[bool] = Field(None, description="Régulateur adaptatif")
    keyless_entry: Optional[bool] = Field(None, description="Démarrage sans clé")
    head_up_display: Optional[bool] = Field(None, description="Affichage tête haute")

    # Équipements sécurité
    abs: Optional[bool] = Field(None, description="ABS")
    esp: Optional[bool] = Field(None, description="ESP")
    airbags: Optional[int] = Field(None, ge=0, description="Nombre d'airbags")
    lane_assist: Optional[bool] = Field(None, description="Aide au maintien de voie")
    blind_spot: Optional[bool] = Field(None, description="Détection angle mort")
    automatic_emergency_braking: Optional[bool] = Field(None, description="Freinage d'urgence automatique")

    # Autres équipements
    alloy_wheels: Optional[bool] = Field(None, description="Jantes alliage")
    led_headlights: Optional[bool] = Field(None, description="Phares LED")
    xenon_headlights: Optional[bool] = Field(None, description="Phares Xenon")
    tow_bar: Optional[bool] = Field(None, description="Attelage")
    ski_rack: Optional[bool] = Field(None, description="Porte-skis")
    roof_rack: Optional[bool] = Field(None, description="Barres de toit")

    # Motorisation
    cylinders: Optional[int] = Field(None, ge=1, le=16, description="Nombre de cylindres")
    engine_size: Optional[int] = Field(None, ge=0, description="Cylindrée en cm³")
    drive_type: Optional[str] = Field(None, description="Type de traction: front, rear, awd, 4wd")

    # Contrôle pagination (pas de limite max)
    max_pages: int = Field(20, ge=1, le=1000, description="Nombre de pages par source")

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


class NaturalSearchRequest(BaseModel):
    """Requête de recherche en langage naturel"""
    query: str = Field(..., description="Recherche en texte libre (ex: 'BMW Série 3 diesel de 2018 à moins de 20000€')")
    sources: List[str] = Field(["leboncoin", "autoscout24"], description="Sources à scraper")
    max_pages: int = Field(20, ge=1, le=1000, description="Nombre de pages par source")


class ParsedFiltersResponse(BaseModel):
    """Réponse contenant les filtres parsés"""
    success: bool
    filters: Dict[str, Any]
    explanation: str


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

    # Filtre sur la marque (STRICT)
    if filters.get('make'):
        make_lower = filters['make'].lower()
        before_count = len(filtered)

        # DEBUG: Log quelques exemples avant filtre
        if filtered[:3]:
            logger.debug(f"📋 Avant filtre make='{make_lower}', {before_count} résultats:")
            for r in filtered[:3]:
                logger.debug(f"  - make={r.get('make')}, model={r.get('model')}, title={r.get('title', '')[:40]}")

        filtered = [r for r in filtered if r.get('make') and make_lower in r['make'].lower()]

        logger.info(f"🔍 Filtre make='{make_lower}': {before_count} -> {len(filtered)} résultats")

    # Filtre sur le modèle (FLEXIBLE - cherche dans model ET title, insensible aux accents)
    if filters.get('model'):
        model_normalized = normalize_text(filters['model'])
        before_count = len(filtered)

        # DEBUG: Log quelques exemples avant filtre
        if filtered[:3]:
            logger.debug(f"📋 Avant filtre model='{filters['model']}' (normalisé: '{model_normalized}'), {before_count} résultats:")
            for r in filtered[:3]:
                logger.debug(f"  - make={r.get('make')}, model={r.get('model')}, title={r.get('title', '')[:60]}")

        # Chercher dans le champ model OU dans le titre (insensible aux accents)
        def matches_model(result):
            # Chercher dans le champ model
            if result.get('model'):
                if model_normalized in normalize_text(result['model']):
                    return True
            # Chercher dans le titre comme fallback
            if result.get('title'):
                if model_normalized in normalize_text(result['title']):
                    return True
            return False

        filtered = [r for r in filtered if matches_model(r)]

        logger.info(f"🔍 Filtre model='{filters['model']}': {before_count} -> {len(filtered)} résultats")

    # Filtre sur l'année
    if filters.get('year_min'):
        filtered = [r for r in filtered if r.get('year') and r['year'] >= filters['year_min']]
    if filters.get('year_max'):
        filtered = [r for r in filtered if r.get('year') and r['year'] <= filters['year_max']]

    # Filtre sur le prix
    if filters.get('price_min'):
        filtered = [r for r in filtered if r.get('price') and r['price'] >= filters['price_min']]
    if filters.get('price_max'):
        filtered = [r for r in filtered if r.get('price') and r['price'] <= filters['price_max']]

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

    # Filtre sur le type de carrosserie
    if filters.get('body_type'):
        body_normalized = normalize_text(filters['body_type'])
        filtered = [r for r in filtered if r.get('body_type') and body_normalized in normalize_text(r['body_type'])]

    # Filtre sur la puissance (chevaux)
    if filters.get('horsepower_min'):
        filtered = [r for r in filtered if r.get('horsepower') and r['horsepower'] >= filters['horsepower_min']]
    if filters.get('horsepower_max'):
        filtered = [r for r in filtered if r.get('horsepower') and r['horsepower'] <= filters['horsepower_max']]

    # Filtre sur la puissance fiscale (CV)
    if filters.get('horsepower_fiscal_min'):
        filtered = [r for r in filtered if r.get('horsepower_fiscal') and r['horsepower_fiscal'] >= filters['horsepower_fiscal_min']]
    if filters.get('horsepower_fiscal_max'):
        filtered = [r for r in filtered if r.get('horsepower_fiscal') and r['horsepower_fiscal'] <= filters['horsepower_fiscal_max']]

    # Filtre sur le type de vendeur
    if filters.get('seller_type'):
        seller_normalized = normalize_text(filters['seller_type'])
        filtered = [r for r in filtered if r.get('seller_type') and seller_normalized in normalize_text(r['seller_type'])]

    # Filtre première main
    if filters.get('first_registration') is True:
        filtered = [r for r in filtered if r.get('first_registration') is True or r.get('owners') == 1]

    # Filtre nombre de portes
    if filters.get('nb_doors'):
        filtered = [r for r in filtered if r.get('doors') == filters['nb_doors'] or r.get('nb_doors') == filters['nb_doors']]

    # Filtre nombre de places
    if filters.get('nb_seats'):
        filtered = [r for r in filtered if r.get('seats') == filters['nb_seats'] or r.get('nb_seats') == filters['nb_seats']]

    # Filtre couleur extérieure
    if filters.get('color'):
        color_normalized = normalize_text(filters['color'])
        filtered = [r for r in filtered if r.get('color') and color_normalized in normalize_text(r['color'])]

    # Filtre couleur intérieure
    if filters.get('color_interior'):
        color_int_normalized = normalize_text(filters['color_interior'])
        filtered = [r for r in filtered if r.get('color_interior') and color_int_normalized in normalize_text(r['color_interior'])]

    # Filtre couleur métallisée
    if filters.get('metallic_color') is True:
        filtered = [r for r in filtered if r.get('metallic_color') is True]

    # Filtre classe d'émission
    if filters.get('emission_class'):
        emission_normalized = normalize_text(filters['emission_class'])
        filtered = [r for r in filtered if r.get('emission_class') and emission_normalized in normalize_text(r['emission_class'])]

    # Filtre Crit'Air
    if filters.get('critair'):
        filtered = [r for r in filtered if r.get('critair') and str(r['critair']) == str(filters['critair'])]

    # Filtre CO2 maximum
    if filters.get('co2_max'):
        filtered = [r for r in filtered if r.get('co2') and r['co2'] <= filters['co2_max']]

    # Filtre contrôle technique OK
    if filters.get('technical_control_ok') is True:
        filtered = [r for r in filtered if r.get('technical_control_ok') is True]

    # Filtre non fumeur
    if filters.get('non_smoker') is True:
        filtered = [r for r in filtered if r.get('non_smoker') is True]

    # Filtre jamais accidenté
    if filters.get('no_accident') is True:
        filtered = [r for r in filtered if r.get('no_accident') is True or r.get('accident_free') is True]

    # Filtre carnet d'entretien
    if filters.get('service_history') is True:
        filtered = [r for r in filtered if r.get('service_history') is True or r.get('full_service_history') is True]

    # Filtre garantie
    if filters.get('warranty') is True:
        filtered = [r for r in filtered if r.get('warranty') is True]

    # Filtre garantie constructeur
    if filters.get('manufacturer_warranty') is True:
        filtered = [r for r in filtered if r.get('manufacturer_warranty') is True]

    # Filtres équipements (recherche dans features ou equipment lists)
    equipment_filters = {
        'climate_control': filters.get('climate_control'),
        'leather_interior': filters.get('leather_interior'),
        'sunroof': filters.get('sunroof'),
        'panoramic_roof': filters.get('panoramic_roof'),
        'heated_seats': filters.get('heated_seats'),
        'electric_seats': filters.get('electric_seats'),
        'parking_sensors': filters.get('parking_sensors'),
        'parking_camera': filters.get('parking_camera'),
        'reversing_camera': filters.get('reversing_camera'),
        'gps': filters.get('gps'),
        'bluetooth': filters.get('bluetooth'),
        'apple_carplay': filters.get('apple_carplay'),
        'android_auto': filters.get('android_auto'),
        'cruise_control': filters.get('cruise_control'),
        'adaptive_cruise_control': filters.get('adaptive_cruise_control'),
        'keyless_entry': filters.get('keyless_entry'),
        'head_up_display': filters.get('head_up_display'),
        'abs': filters.get('abs'),
        'esp': filters.get('esp'),
        'lane_assist': filters.get('lane_assist'),
        'blind_spot': filters.get('blind_spot'),
        'automatic_emergency_braking': filters.get('automatic_emergency_braking'),
        'alloy_wheels': filters.get('alloy_wheels'),
        'led_headlights': filters.get('led_headlights'),
        'xenon_headlights': filters.get('xenon_headlights'),
        'tow_bar': filters.get('tow_bar'),
        'ski_rack': filters.get('ski_rack'),
        'roof_rack': filters.get('roof_rack'),
    }

    for equipment_key, equipment_value in equipment_filters.items():
        if equipment_value is True:
            # Chercher dans les différents champs possibles
            filtered = [r for r in filtered if (
                r.get(equipment_key) is True or
                (r.get('equipment') and isinstance(r['equipment'], list) and equipment_key in [normalize_text(e) for e in r['equipment']]) or
                (r.get('features') and isinstance(r['features'], list) and any(normalize_text(equipment_key) in normalize_text(str(f)) for f in r['features']))
            )]

    # Filtre nombre d'airbags
    if filters.get('airbags'):
        filtered = [r for r in filtered if r.get('airbags') and r['airbags'] >= filters['airbags']]

    # Filtre nombre de cylindres
    if filters.get('cylinders'):
        filtered = [r for r in filtered if r.get('cylinders') == filters['cylinders']]

    # Filtre cylindrée
    if filters.get('engine_size'):
        # Tolérance de +/- 100 cm³ pour la cylindrée
        tolerance = 100
        filtered = [r for r in filtered if r.get('engine_size') and abs(r['engine_size'] - filters['engine_size']) <= tolerance]

    # Filtre type de traction
    if filters.get('drive_type'):
        drive_normalized = normalize_text(filters['drive_type'])
        filtered = [r for r in filtered if r.get('drive_type') and drive_normalized in normalize_text(r['drive_type'])]

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
                result = future.result(timeout=3600)  # Timeout de 1 heure par source

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


@router.post("/parse-query", response_model=ParsedFiltersResponse)
async def parse_natural_query(request: Dict[str, str]):
    """
    Parse une requête en langage naturel pour extraire les filtres de recherche.

    Utilise l'IA (Claude) pour comprendre le texte et extraire les critères.

    Exemples:
    - "BMW Série 3 diesel de 2018 à moins de 20000€"
    - "Volkswagen Golf automatique avec GPS et toit ouvrant"
    - "SUV électrique récent première main avec caméra de recul"
    """
    from app.routes.ai_parser import parse_natural_query_with_ai

    query = request.get("query", "")

    if not query:
        raise HTTPException(status_code=400, detail="Query manquante")

    logger.info(f"🤖 Parsing requête naturelle: {query}")

    result = await parse_natural_query_with_ai(query)

    return ParsedFiltersResponse(
        success=result["success"],
        filters=result["filters"],
        explanation=result["explanation"]
    )


@router.post("/search-natural", response_model=AdvancedSearchResponse)
async def natural_search(request: NaturalSearchRequest):
    """
    Recherche en langage naturel.

    Combine le parsing IA du texte avec la recherche avancée multi-sources.

    Exemples:
    - "BMW Série 3 diesel de 2018 à moins de 20000€"
    - "Peugeot 308 essence automatique avec moins de 50000 km"
    - "Mercedes Classe A noire cuir GPS caméra de recul"
    """
    from app.routes.ai_parser import parse_natural_query_with_ai

    logger.info(f"🔍 Recherche naturelle: {request.query}")

    # 1. Parser la requête naturelle avec l'IA
    parse_result = await parse_natural_query_with_ai(request.query)
    filters_dict = parse_result["filters"]

    # 2. Ajouter les paramètres de la requête
    filters_dict['sources'] = request.sources
    filters_dict['max_pages'] = request.max_pages

    # 3. Créer une AdvancedSearchRequest à partir des filtres parsés
    search_request = AdvancedSearchRequest(**filters_dict)

    # 4. Exécuter la recherche avancée
    return await advanced_search(search_request)
