# backend/app/services/ai_parser.py
import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY non définie - le parsing IA sera désactivé")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Prompt système pour structurer la requête
SYSTEM_PROMPT = """Tu es un assistant qui convertit des requêtes en langage naturel en filtres de recherche structurés pour des véhicules.

Réponds UNIQUEMENT avec un objet JSON valide contenant ces champs (tous optionnels) :
{
  "make": "marque du véhicule (ex: Peugeot, Volkswagen)",
  "model": "modèle (ex: 208, Golf)",
  "fuel_type": "essence | diesel | electrique | hybride",
  "transmission": "manuelle | automatique",
  "price_min": nombre,
  "price_max": nombre,
  "year_min": nombre,
  "year_max": nombre,
  "mileage_max": nombre en km,
  "category": "citadine | berline | suv | familiale | sportive | utilitaire"
}

Exemples :
- "Je cherche une citadine essence à moins de 50 000 km pour 8 000 euros"
  → {"category": "citadine", "fuel_type": "essence", "mileage_max": 50000, "price_max": 8000}

- "Golf diesel automatique récente"
  → {"model": "Golf", "fuel_type": "diesel", "transmission": "automatique", "year_min": 2020}

- "SUV familial 7 places budget 25000"
  → {"category": "suv", "price_max": 25000}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."""


def parse_natural_query(query: str) -> Dict[str, Any]:
    """
    Parse une requête en langage naturel et retourne des filtres structurés
    
    Args:
        query: Requête utilisateur (ex: "citadine essence moins de 8000 euros")
    
    Returns:
        Dict avec les filtres extraits
    """
    if not client:
        logger.warning("OpenAI client non configuré - retour filters vides")
        return {}
    
    if not query or len(query.strip()) < 3:
        return {}
    
    try:
        logger.info(f"Parsing requête IA: {query}")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Modèle économique et rapide
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            temperature=0.1,  # Très déterministe
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        logger.debug(f"Réponse OpenAI: {content}")
        
        # Parser le JSON
        filters = json.loads(content)
        
        # Validation basique
        if not isinstance(filters, dict):
            logger.error("Réponse OpenAI n'est pas un dictionnaire")
            return {}
        
        # Nettoyer les valeurs None
        filters = {k: v for k, v in filters.items() if v is not None}
        
        logger.info(f"Filtres extraits: {filters}")
        return filters
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur parsing JSON OpenAI: {e} - Content: {content}")
        return {}
    except Exception as e:
        logger.exception(f"Erreur parsing IA: {e}")
        return {}


def enhance_filters(base_filters: Dict[str, Any], natural_query: Optional[str] = None) -> Dict[str, Any]:
    """
    Enrichit des filtres existants avec du parsing IA
    
    Args:
        base_filters: Filtres de base (ex: depuis formulaire)
        natural_query: Requête optionnelle en langage naturel
    
    Returns:
        Filtres enrichis
    """
    enhanced = base_filters.copy()
    
    if natural_query and client:
        ai_filters = parse_natural_query(natural_query)
        
        # Merge : les filtres explicites (base) priment sur l'IA
        for key, value in ai_filters.items():
            if key not in enhanced:
                enhanced[key] = value
    
    return enhanced


# Fonction de test
def test_parser():
    """Test du parser avec des exemples"""
    test_queries = [
        "Je cherche une citadine essence à moins de 50 000 km pour 8 000 euros",
        "Golf diesel automatique récente",
        "SUV familial 7 places budget 25000",
        "Peugeot 208 manuelle 2020 max 15000 euros",
        "voiture électrique autonomie 400km"
    ]
    
    print("=== Test AI Parser ===\n")
    for query in test_queries:
        print(f"Query: {query}")
        filters = parse_natural_query(query)
        print(f"Filters: {json.dumps(filters, indent=2, ensure_ascii=False)}\n")


if __name__ == "__main__":
    test_parser()