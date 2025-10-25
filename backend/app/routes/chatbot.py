# backend/app/routes/chatbot.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.ai_parser import parse_natural_query
from app.services.search import SearchService
from app.db import SessionLocal
from app.models import User, SearchHistory
from app.dependencies import get_current_user
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    interpretation: str
    filters_used: Dict[str, Any]
    total: int
    hits: list
    suggestions: Optional[list] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/search", response_model=ChatResponse)
async def chat_search(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: None)  # Optionnel
):
    """
    Recherche conversationnelle : parse la requête naturelle et retourne résultats
    """
    try:
        message = request.message.strip()
        
        if not message:
            raise HTTPException(status_code=400, detail="Message vide")
        
        logger.info(f"Chat search: '{message}'")
        
        # 1. Parser avec l'IA
        filters = parse_natural_query(message)
        
        # 2. Générer l'interprétation
        interpretation = generate_interpretation(message, filters)
        
        # 3. Recherche Elasticsearch
        search_results = SearchService.search(
            q=None,  # Pas de query texte, on utilise les filtres
            filters=filters,
            page=1,
            size=10
        )
        
        # 4. Enregistrer dans l'historique si connecté
        if current_user:
            try:
                history = SearchHistory(
                    id=str(uuid.uuid4()),
                    user_id=current_user.id,
                    query=message,
                    filters=filters,
                    results_count=search_results.get('total', 0)
                )
                db.add(history)
                db.commit()
            except Exception as e:
                logger.error(f"Erreur historique: {e}")
                db.rollback()
        
        # 5. Suggestions si peu de résultats
        suggestions = None
        if search_results.get('total', 0) < 3:
            suggestions = generate_suggestions(filters)
        
        return ChatResponse(
            interpretation=interpretation,
            filters_used=filters,
            total=search_results.get('total', 0),
            hits=search_results.get('hits', []),
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.exception(f"Erreur chat_search: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")


def generate_interpretation(message: str, filters: Dict[str, Any]) -> str:
    """Génère un message d'interprétation lisible"""
    
    if not filters:
        return f"Je recherche : '{message}'"
    
    parts = []
    
    if "make" in filters:
        parts.append(f"marque {filters['make']}")
    
    if "model" in filters:
        parts.append(f"modèle {filters['model']}")
    
    if "category" in filters:
        parts.append(f"type {filters['category']}")
    
    if "fuel_type" in filters:
        fuel_fr = {
            "essence": "essence",
            "diesel": "diesel", 
            "electrique": "électrique",
            "hybride": "hybride"
        }
        parts.append(fuel_fr.get(filters["fuel_type"], filters["fuel_type"]))
    
    if "transmission" in filters:
        trans_fr = {
            "manuelle": "boîte manuelle",
            "automatique": "boîte automatique"
        }
        parts.append(trans_fr.get(filters["transmission"], filters["transmission"]))
    
    price_parts = []
    if "price_max" in filters:
        price_parts.append(f"max {filters['price_max']}€")
    if "price_min" in filters:
        price_parts.append(f"min {filters['price_min']}€")
    if price_parts:
        parts.append("prix " + " ".join(price_parts))
    
    if "year_min" in filters:
        parts.append(f"à partir de {filters['year_min']}")
    
    if "mileage_max" in filters:
        parts.append(f"max {filters['mileage_max']} km")
    
    if parts:
        return "Je recherche : " + ", ".join(parts)
    else:
        return f"Je recherche : '{message}'"


def generate_suggestions(filters: Dict[str, Any]) -> list:
    """Génère des suggestions pour élargir la recherche"""
    suggestions = []
    
    if "price_max" in filters:
        new_price = int(filters["price_max"] * 1.2)
        suggestions.append(f"Augmenter le budget à {new_price}€")
    
    if "mileage_max" in filters:
        new_km = int(filters["mileage_max"] * 1.3)
        suggestions.append(f"Accepter jusqu'à {new_km} km")
    
    if "year_min" in filters:
        new_year = filters["year_min"] - 2
        suggestions.append(f"Inclure les modèles depuis {new_year}")
    
    if "make" in filters or "model" in filters:
        suggestions.append("Essayer avec d'autres marques similaires")
    
    if not suggestions:
        suggestions.append("Élargir les critères de recherche")
    
    return suggestions[:3]  # Max 3 suggestions


@router.post("/parse")
async def chat_parse(request: ChatRequest):
    """
    Parse uniquement la requête sans faire de recherche
    Utile pour preview des filtres
    """
    try:
        message = request.message.strip()
        
        if not message:
            raise HTTPException(status_code=400, detail="Message vide")
        
        filters = parse_natural_query(message)
        interpretation = generate_interpretation(message, filters)
        
        return {
            "interpretation": interpretation,
            "filters": filters
        }
        
    except Exception as e:
        logger.exception(f"Erreur chat_parse: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du parsing")