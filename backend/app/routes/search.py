# backend/app/routes/search.py
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import logging

# Utiliser le nouveau service de recherche hybride
from app.services.search_with_scraping import hybrid_search
from app.models import SearchHistory, User
from app.db import SessionLocal
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_search_history(user_id: str, query: Optional[str], filters: Dict, results_count: int, db: Session):
    """Enregistrer une recherche dans l'historique"""
    try:
        history = SearchHistory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            query=query,
            filters=filters,
            results_count=results_count
        )
        db.add(history)
        db.commit()
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'historique: {e}")
        db.rollback()

@router.post("/search")
async def search_post(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: get_current_user if False else None)
):
    """
    Recherche hybride avec scraping en temps réel

    Body JSON:
    {
        "q": "peugeot 308",
        "filters": {
            "price_min": 5000,
            "price_max": 15000,
            "year_min": 2015
        },
        "page": 1,
        "size": 20,
        "enable_scraping": true,  // Activer le scraping (défaut: true)
        "scraping_mode": "auto"   // 'auto', 'always', 'never', 'db_first'
    }
    """
    try:
        q = payload.get("q")
        filters = payload.get("filters", {}) or {}
        page = int(payload.get("page", 1) or 1)
        size = int(payload.get("size", 20) or 20)
        enable_scraping = payload.get("enable_scraping", True)
        scraping_mode = payload.get("scraping_mode", "auto")

    except Exception as e:
        logger.exception("Malformed search payload")
        raise HTTPException(status_code=422, detail="Malformed search payload")

    try:
        # Utiliser le service de recherche hybride
        res = hybrid_search.search(
            q=q,
            filters=filters,
            page=page,
            size=size,
            enable_scraping=enable_scraping,
            scraping_mode=scraping_mode
        )

        # Enregistrer dans l'historique si l'utilisateur est connecté
        if current_user:
            save_search_history(current_user.id, q, filters, res.get('total', 0), db)

        return res

    except Exception as e:
        logger.exception("Hybrid search error")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/search")
async def search_get(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
    enable_scraping: bool = Query(True, description="Activer le scraping en temps réel"),
    scraping_mode: str = Query("auto", description="Mode de scraping: auto, always, never, db_first"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: get_current_user if False else None)
):
    """
    Recherche GET avec scraping en temps réel

    Paramètres:
    - q: Terme de recherche
    - page: Numéro de page (défaut: 1)
    - size: Taille de la page (défaut: 20, max: 200)
    - make: Marque du véhicule
    - model: Modèle du véhicule
    - price_min: Prix minimum
    - price_max: Prix maximum
    - enable_scraping: Activer le scraping (défaut: true)
    - scraping_mode: Mode de scraping (défaut: auto)
        - 'auto': Scraper si moins de 5 résultats en DB
        - 'always': Toujours scraper
        - 'never': Jamais scraper (DB uniquement)
        - 'db_first': Scraper uniquement si aucun résultat en DB
    """
    filters = {}
    if make:
        filters["make"] = make
    if model:
        filters["model"] = model
    if price_min is not None:
        filters["price_min"] = price_min
    if price_max is not None:
        filters["price_max"] = price_max

    try:
        # Utiliser le service de recherche hybride
        res = hybrid_search.search(
            q=q,
            filters=filters,
            page=page,
            size=size,
            enable_scraping=enable_scraping,
            scraping_mode=scraping_mode
        )

        # Enregistrer dans l'historique si l'utilisateur est connecté
        if current_user:
            save_search_history(current_user.id, q, filters, res.get('total', 0), db)

        return res

    except Exception:
        logger.exception("Hybrid search error (GET)")
        raise HTTPException(status_code=500, detail="Search error")
