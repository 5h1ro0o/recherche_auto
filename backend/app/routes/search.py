# backend/app/routes/search.py
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
from app.services.search import SearchService
from app.models import SearchHistory, User
from app.db import SessionLocal
from app.dependencies import get_current_user
import logging

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
    Accept generic JSON body. Expected shape:
    { "q": "...", "filters": {...}, "page": 1, "size": 20 }
    """
    try:
        q = payload.get("q")
        filters = payload.get("filters", {}) or {}
        page = int(payload.get("page", 1) or 1)
        size = int(payload.get("size", 20) or 20)
    except Exception as e:
        logger.exception("Malformed search payload")
        raise HTTPException(status_code=422, detail="Malformed search payload")

    try:
        res = SearchService.search(q=q, filters=filters, page=page, size=size)
        
        # Enregistrer dans l'historique si l'utilisateur est connecté
        if current_user:
            save_search_history(current_user.id, q, filters, res.get('total', 0), db)
        
        return res
    except Exception as e:
        logger.exception("SearchService error")
        raise HTTPException(status_code=500, detail="Search error")

@router.get("/search")
async def search_get(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: get_current_user if False else None)
):
    filters = {}
    if make:
        filters["make"] = make
    if model:
        filters["model"] = model
    if price_min is not None or price_max is not None:
        rng = {}
        if price_min is not None:
            rng["price_min"] = price_min
        if price_max is not None:
            rng["price_max"] = price_max
        filters.update(rng)
    
    try:
        res = SearchService.search(q=q, filters=filters, page=page, size=size)
        
        # Enregistrer dans l'historique si l'utilisateur est connecté
        if current_user:
            save_search_history(current_user.id, q, filters, res.get('total', 0), db)
        
        return res
    except Exception:
        logger.exception("SearchService error (GET)")
        raise HTTPException(status_code=500, detail="Search error")