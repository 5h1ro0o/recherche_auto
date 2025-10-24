# backend/app/routes/alerts.py
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal
from app.models import Alert, User
from app.schemas import AlertCreate, AlertUpdate, AlertOut
from app.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["alerts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=List[AlertOut])
async def get_my_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer toutes mes alertes"""
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id
    ).order_by(Alert.created_at.desc()).all()
    
    return alerts

@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer une nouvelle alerte"""
    
    # Vérifier la fréquence
    valid_frequencies = ['daily', 'weekly', 'instant']
    if alert_data.frequency not in valid_frequencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fréquence invalide. Valeurs acceptées: {valid_frequencies}"
        )
    
    alert = Alert(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=alert_data.name,
        criteria=alert_data.criteria,
        frequency=alert_data.frequency,
        is_active=True
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alerte créée: {alert.name} pour user {current_user.email}")
    return alert

@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer une alerte spécifique"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    return alert

@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier une alerte"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    # Mettre à jour les champs
    update_data = alert_update.dict(exclude_unset=True)
    
    # Valider la fréquence si elle est modifiée
    if 'frequency' in update_data:
        valid_frequencies = ['daily', 'weekly', 'instant']
        if update_data['frequency'] not in valid_frequencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fréquence invalide. Valeurs acceptées: {valid_frequencies}"
            )
    
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alerte modifiée: {alert.id}")
    return alert

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer une alerte"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    db.delete(alert)
    db.commit()
    
    logger.info(f"Alerte supprimée: {alert_id}")
    return None

@router.post("/{alert_id}/toggle", response_model=AlertOut)
async def toggle_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activer/désactiver une alerte"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    alert.is_active = not alert.is_active
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alerte {'activée' if alert.is_active else 'désactivée'}: {alert_id}")
    return alert