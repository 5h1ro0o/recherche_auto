# backend/app/routes/search_history.py
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import SessionLocal
from app.models import SearchHistory, User
from app.schemas import SearchHistoryOut
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search-history", tags=["search-history"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=List[SearchHistoryOut])
async def get_my_search_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer mon historique de recherche"""
    history = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.created_at.desc()).limit(limit).all()
    
    return history

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def clear_my_search_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Effacer tout mon historique de recherche"""
    db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).delete()
    
    db.commit()
    logger.info(f"Historique effacé pour user {current_user.email}")
    return None

@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_history_item(
    history_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un élément de l'historique"""
    item = db.query(SearchHistory).filter(
        SearchHistory.id == history_id,
        SearchHistory.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Élément non trouvé"
        )
    
    db.delete(item)
    db.commit()
    
    logger.info(f"Élément historique supprimé: {history_id}")
    return None