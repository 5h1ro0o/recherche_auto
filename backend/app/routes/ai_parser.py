# backend/app/routes/ai_parser.py
"""Module pour parser les requêtes en langage naturel avec IA"""

import logging
import os
import json
import anthropic
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configuration pour l'API Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


async def parse_natural_query_with_ai(query: str) -> Dict[str, Any]:
    """
    Parse une requête en langage naturel en utilisant Claude (Anthropic)
    pour extraire les filtres de recherche.

    Args:
        query: Texte libre de la recherche (ex: "BMW Série 3 diesel de 2018 à moins de 20000€")

    Returns:
        Dict contenant les filtres extraits et une explication
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY non définie, utilisation du parsing basique")
        return await parse_natural_query_basic(query)

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""Tu es un assistant qui extrait des filtres de recherche de véhicules à partir de texte libre.

Texte de recherche: "{query}"

Extrais TOUS les critères mentionnés et retourne un objet JSON avec les champs suivants (uniquement ceux qui sont mentionnés):
- make: marque (ex: bmw, volkswagen, renault) en minuscules
- model: modèle (ex: série 3, golf) en minuscules
- year_min: année minimum
- year_max: année maximum
- price_min: prix minimum en euros
- price_max: prix maximum en euros
- mileage_min: kilométrage minimum
- mileage_max: kilométrage maximum
- fuel_type: type de carburant (essence, diesel, electrique, hybride, gpl)
- transmission: transmission (manuelle, automatique)
- body_type: carrosserie (berline, break, suv, coupe, cabriolet, monospace, utilitaire)
- horsepower_min: puissance minimum en chevaux
- horsepower_max: puissance maximum en chevaux
- seller_type: type de vendeur (particulier, professionnel)
- first_registration: true si "première main" est mentionné
- no_accident: true si "jamais accidenté" est mentionné
- service_history: true si "carnet d'entretien" est mentionné
- warranty: true si "garantie" est mentionnée
- color: couleur
- leather_interior: true si "cuir" est mentionné
- sunroof: true si "toit ouvrant" est mentionné
- panoramic_roof: true si "toit panoramique" est mentionné
- gps: true si "gps" ou "navigation" est mentionné
- bluetooth: true si "bluetooth" est mentionné
- apple_carplay: true si "apple carplay" ou "carplay" est mentionné
- android_auto: true si "android auto" est mentionné
- heated_seats: true si "sièges chauffants" est mentionné
- parking_camera: true si "caméra de recul" ou "caméra" est mentionné
- alloy_wheels: true si "jantes alliage" est mentionné
- led_headlights: true si "phares led" est mentionné

Retourne UNIQUEMENT le JSON, sans texte avant ou après. Exemple:
{{"make": "bmw", "model": "série 3", "fuel_type": "diesel", "year_min": 2018, "price_max": 20000}}

Important:
- Normalise les accents (Série -> série)
- Convertis les montants en nombres (20000€ -> 20000)
- Pour les fourchettes, utilise min/max
- N'invente pas de valeurs, utilise seulement ce qui est explicitement mentionné
"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text.strip()

        # Parser le JSON
        try:
            # Enlever les éventuels ``` json et ```
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0]

            filters = json.loads(response_text)

            # Générer une explication lisible
            explanation = generate_explanation(filters, query)

            logger.info(f"✅ Filtres extraits par IA: {filters}")

            return {
                "success": True,
                "filters": filters,
                "explanation": explanation
            }

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON de Claude: {e}\nRéponse: {response_text}")
            # Fallback sur parsing basique
            return await parse_natural_query_basic(query)

    except Exception as e:
        logger.error(f"Erreur appel API Anthropic: {e}")
        # Fallback sur parsing basique
        return await parse_natural_query_basic(query)


async def parse_natural_query_basic(query: str) -> Dict[str, Any]:
    """
    Parsing basique sans IA (fallback)
    Utilise des règles simples pour extraire les filtres
    """
    filters = {}
    query_lower = query.lower()

    # Marques communes
    brands = {
        'bmw': 'bmw', 'mercedes': 'mercedes', 'audi': 'audi',
        'volkswagen': 'volkswagen', 'vw': 'volkswagen',
        'peugeot': 'peugeot', 'renault': 'renault', 'citroen': 'citroen',
        'toyota': 'toyota', 'honda': 'honda', 'ford': 'ford'
    }

    for brand_key, brand_value in brands.items():
        if brand_key in query_lower:
            filters['make'] = brand_value
            break

    # Type de carburant
    if 'diesel' in query_lower:
        filters['fuel_type'] = 'diesel'
    elif 'essence' in query_lower:
        filters['fuel_type'] = 'essence'
    elif 'electrique' in query_lower or 'électrique' in query_lower:
        filters['fuel_type'] = 'electrique'
    elif 'hybride' in query_lower:
        filters['fuel_type'] = 'hybride'

    # Transmission
    if 'automatique' in query_lower or 'auto' in query_lower:
        filters['transmission'] = 'automatique'
    elif 'manuelle' in query_lower:
        filters['transmission'] = 'manuelle'

    # Prix (chercher des patterns comme "moins de 20000", "maximum 15000", etc.)
    import re
    price_patterns = [
        r'moins\s+de\s+(\d+)',
        r'maximum\s+(\d+)',
        r'max\s+(\d+)',
        r'jusqu[\'']à\s+(\d+)',
        r'<\s*(\d+)',
    ]

    for pattern in price_patterns:
        match = re.search(pattern, query_lower)
        if match:
            filters['price_max'] = int(match.group(1))
            break

    # Année
    year_patterns = [
        r'de\s+(\d{4})',
        r'à\s+partir\s+de\s+(\d{4})',
        r'après\s+(\d{4})',
    ]

    for pattern in year_patterns:
        match = re.search(pattern, query_lower)
        if match:
            filters['year_min'] = int(match.group(1))
            break

    explanation = f"Recherche basique: {len(filters)} filtre(s) détecté(s)"

    return {
        "success": True,
        "filters": filters,
        "explanation": explanation
    }


def generate_explanation(filters: Dict[str, Any], original_query: str) -> str:
    """Génère une explication lisible des filtres extraits"""
    parts = []

    if filters.get('make'):
        parts.append(f"Marque: {filters['make']}")
    if filters.get('model'):
        parts.append(f"Modèle: {filters['model']}")
    if filters.get('year_min') or filters.get('year_max'):
        if filters.get('year_min') and filters.get('year_max'):
            parts.append(f"Année: {filters['year_min']}-{filters['year_max']}")
        elif filters.get('year_min'):
            parts.append(f"Année: à partir de {filters['year_min']}")
        else:
            parts.append(f"Année: jusqu'à {filters['year_max']}")

    if filters.get('price_min') or filters.get('price_max'):
        if filters.get('price_min') and filters.get('price_max'):
            parts.append(f"Prix: {filters['price_min']}-{filters['price_max']}€")
        elif filters.get('price_min'):
            parts.append(f"Prix: à partir de {filters['price_min']}€")
        else:
            parts.append(f"Prix: jusqu'à {filters['price_max']}€")

    if filters.get('fuel_type'):
        parts.append(f"Carburant: {filters['fuel_type']}")
    if filters.get('transmission'):
        parts.append(f"Transmission: {filters['transmission']}")
    if filters.get('body_type'):
        parts.append(f"Carrosserie: {filters['body_type']}")

    if not parts:
        return "Aucun filtre spécifique détecté"

    return " | ".join(parts)
