# backend/app/routes/assisted.py
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db import SessionLocal
from app.models import (
    User, AssistedRequest, ProposedVehicle, Vehicle,
    RequestStatus, ProposalStatus, UserRole
)
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Schemas inline pour l'instant
class AssistedRequestCreate(BaseModel):
    description: str
    budget_max: Optional[int] = None
    preferred_fuel_type: Optional[str] = None
    preferred_transmission: Optional[str] = None
    max_mileage: Optional[int] = None
    min_year: Optional[int] = None
    ai_parsed_criteria: Optional[Dict[str, Any]] = None

class AssistedRequestUpdate(BaseModel):
    description: Optional[str] = None
    budget_max: Optional[int] = None
    preferred_fuel_type: Optional[str] = None
    preferred_transmission: Optional[str] = None
    max_mileage: Optional[int] = None
    min_year: Optional[int] = None

class AssistedRequestOut(BaseModel):
    id: str
    client_id: str
    expert_id: Optional[str]
    status: str
    description: str
    budget_max: Optional[int]
    preferred_fuel_type: Optional[str]
    preferred_transmission: Optional[str]
    max_mileage: Optional[int]
    min_year: Optional[int]
    ai_parsed_criteria: Dict[str, Any]
    created_at: datetime
    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = {"from_attributes": True}

class ProposedVehicleCreate(BaseModel):
    vehicle_id: str
    message: Optional[str] = None

class ProposalUpdate(BaseModel):
    status: ProposalStatus
    rejection_reason: Optional[str] = None

class ProposedVehicleOut(BaseModel):
    id: str
    request_id: str
    vehicle_id: str
    status: str
    message: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
from app.dependencies import get_current_user, require_expert

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assisted", tags=["assisted"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ ROUTES CLIENT ============

@router.post("/requests", response_model=AssistedRequestOut, status_code=status.HTTP_201_CREATED)
async def create_assisted_request(
    request_data: AssistedRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer une demande d'assistance (client)"""
    
    request = AssistedRequest(
        id=str(uuid.uuid4()),
        client_id=current_user.id,
        status=RequestStatus.PENDING,
        description=request_data.description,
        budget_max=request_data.budget_max,
        preferred_fuel_type=request_data.preferred_fuel_type,
        preferred_transmission=request_data.preferred_transmission,
        max_mileage=request_data.max_mileage,
        min_year=request_data.min_year,
        ai_parsed_criteria=request_data.ai_parsed_criteria or {}
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    logger.info(f"Demande assistée créée: {request.id} par {current_user.email}")
    return request

@router.get("/requests/me", response_model=List[AssistedRequestOut])
async def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[RequestStatus] = None
):
    """Récupérer mes demandes (client)"""
    query = db.query(AssistedRequest).filter(
        AssistedRequest.client_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(AssistedRequest.status == status_filter)
    
    requests = query.order_by(AssistedRequest.created_at.desc()).all()
    return requests

@router.get("/requests/{request_id}", response_model=AssistedRequestOut)
async def get_request_detail(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Détail d'une demande (client)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.client_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée"
        )
    
    return request

@router.patch("/requests/{request_id}", response_model=AssistedRequestOut)
async def update_my_request(
    request_id: str,
    update_data: AssistedRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier ma demande (client, uniquement si EN_ATTENTE)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.client_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée"
        )
    
    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier une demande en cours ou terminée"
        )
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(request, key, value)
    
    db.commit()
    db.refresh(request)
    return request

@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Annuler ma demande (client)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.client_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée"
        )
    
    if request.status == RequestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'annuler une demande terminée"
        )
    
    request.status = RequestStatus.CANCELLED
    db.commit()
    
    logger.info(f"Demande annulée: {request_id}")
    return None

# ============ ROUTES PROPOSITIONS (CLIENT) ============

@router.get("/requests/{request_id}/proposals", response_model=List[ProposedVehicleOut])
async def get_my_proposals(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Voir les véhicules proposés par l'expert (client)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.client_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée"
        )
    
    proposals = db.query(ProposedVehicle).filter(
        ProposedVehicle.request_id == request_id
    ).order_by(ProposedVehicle.created_at.desc()).all()
    
    return proposals

@router.patch("/proposals/{proposal_id}", response_model=ProposedVehicleOut)
async def update_proposal_status(
    proposal_id: str,
    update_data: ProposalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marquer un véhicule proposé (client : coup de cœur ou refusé)"""
    proposal = db.query(ProposedVehicle).join(AssistedRequest).filter(
        ProposedVehicle.id == proposal_id,
        AssistedRequest.client_id == current_user.id
    ).first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposition non trouvée"
        )
    
    proposal.status = update_data.status
    proposal.rejection_reason = update_data.rejection_reason
    proposal.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(proposal)
    
    logger.info(f"Proposition {proposal_id} mise à jour: {update_data.status}")
    return proposal

# ============ ROUTES EXPERT ============

@router.get("/requests", response_model=List[AssistedRequestOut])
async def get_available_requests(
    current_user: User = Depends(require_expert),
    db: Session = Depends(get_db),
    status_filter: Optional[RequestStatus] = Query(RequestStatus.PENDING)
):
    """Liste des demandes disponibles (expert)"""
    query = db.query(AssistedRequest)
    
    if status_filter == RequestStatus.PENDING:
        # Demandes en attente (non assignées)
        query = query.filter(
            AssistedRequest.status == RequestStatus.PENDING,
            AssistedRequest.expert_id.is_(None)
        )
    elif status_filter == RequestStatus.IN_PROGRESS:
        # Mes demandes en cours
        query = query.filter(
            AssistedRequest.status == RequestStatus.IN_PROGRESS,
            AssistedRequest.expert_id == current_user.id
        )
    else:
        # Toutes mes demandes (en cours + terminées)
        query = query.filter(AssistedRequest.expert_id == current_user.id)
    
    requests = query.order_by(AssistedRequest.created_at.desc()).all()
    return requests

@router.post("/requests/{request_id}/accept", response_model=AssistedRequestOut)
async def accept_request(
    request_id: str,
    current_user: User = Depends(require_expert),
    db: Session = Depends(get_db)
):
    """Accepter une demande (expert)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.status == RequestStatus.PENDING,
        AssistedRequest.expert_id.is_(None)
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée ou déjà prise en charge"
        )
    
    request.expert_id = current_user.id
    request.status = RequestStatus.IN_PROGRESS
    request.accepted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(request)
    
    logger.info(f"Demande {request_id} acceptée par expert {current_user.email}")
    return request

@router.post("/requests/{request_id}/propose", response_model=ProposedVehicleOut)
async def propose_vehicle(
    request_id: str,
    proposal_data: ProposedVehicleCreate,
    current_user: User = Depends(require_expert),
    db: Session = Depends(get_db)
):
    """Proposer un véhicule à un client (expert)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.expert_id == current_user.id,
        AssistedRequest.status == RequestStatus.IN_PROGRESS
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée ou vous n'êtes pas assigné"
        )
    
    # Vérifier que le véhicule existe
    vehicle = db.query(Vehicle).filter(Vehicle.id == proposal_data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    # Vérifier si déjà proposé
    existing = db.query(ProposedVehicle).filter(
        ProposedVehicle.request_id == request_id,
        ProposedVehicle.vehicle_id == proposal_data.vehicle_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Véhicule déjà proposé pour cette demande"
        )
    
    proposal = ProposedVehicle(
        id=str(uuid.uuid4()),
        request_id=request_id,
        vehicle_id=proposal_data.vehicle_id,
        status=ProposalStatus.PENDING,
        message=proposal_data.message
    )
    
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    
    logger.info(f"Véhicule {proposal_data.vehicle_id} proposé pour demande {request_id}")
    return proposal

@router.post("/requests/{request_id}/complete", response_model=AssistedRequestOut)
async def complete_request(
    request_id: str,
    current_user: User = Depends(require_expert),
    db: Session = Depends(get_db)
):
    """Marquer une demande comme terminée (expert)"""
    request = db.query(AssistedRequest).filter(
        AssistedRequest.id == request_id,
        AssistedRequest.expert_id == current_user.id,
        AssistedRequest.status == RequestStatus.IN_PROGRESS
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande non trouvée"
        )
    
    request.status = RequestStatus.COMPLETED
    request.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(request)
    
    logger.info(f"Demande {request_id} terminée")
    return request

# ============ STATISTIQUES EXPERT ============

@router.get("/expert/stats")
async def get_expert_stats(
    current_user: User = Depends(require_expert),
    db: Session = Depends(get_db)
):
    """Statistiques de l'expert"""
    
    # Compteurs
    total_requests = db.query(AssistedRequest).filter(
        AssistedRequest.expert_id == current_user.id
    ).count()
    
    pending_requests = db.query(AssistedRequest).filter(
        AssistedRequest.expert_id == current_user.id,
        AssistedRequest.status == RequestStatus.IN_PROGRESS
    ).count()
    
    completed_requests = db.query(AssistedRequest).filter(
        AssistedRequest.expert_id == current_user.id,
        AssistedRequest.status == RequestStatus.COMPLETED
    ).count()
    
    # Propositions
    total_proposals = db.query(ProposedVehicle).join(AssistedRequest).filter(
        AssistedRequest.expert_id == current_user.id
    ).count()
    
    accepted_proposals = db.query(ProposedVehicle).join(AssistedRequest).filter(
        AssistedRequest.expert_id == current_user.id,
        ProposedVehicle.status == ProposalStatus.FAVORITE
    ).count()
    
    # Taux d'acceptation
    acceptance_rate = (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "completed_requests": completed_requests,
        "total_proposals": total_proposals,
        "accepted_proposals": accepted_proposals,
        "acceptance_rate": round(acceptance_rate, 1)
    }