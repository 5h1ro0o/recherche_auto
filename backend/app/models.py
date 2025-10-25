# backend/app/models.py - AJOUTER ces modèles (garder les existants)

from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# ============ GARDER LES MODELES EXISTANTS ============
# Base, UserRole, User, Vehicle, Favorite, Alert, SearchHistory

# ============ NOUVEAUX MODELES POUR MODE ASSISTE ============

class RequestStatus(str, enum.Enum):
    """Statuts des demandes assistées"""
    PENDING = "EN_ATTENTE"
    IN_PROGRESS = "EN_COURS"
    COMPLETED = "TERMINEE"
    CANCELLED = "ANNULEE"

class ProposalStatus(str, enum.Enum):
    """Statuts des propositions de véhicules"""
    PENDING = "PENDING"
    FAVORITE = "FAVORITE"
    REJECTED = "REJECTED"

class AssistedRequest(Base):
    """Demandes d'assistance client → expert"""
    __tablename__ = "assisted_requests"
    
    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    expert_id = Column(String, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    status = Column(SQLEnum(RequestStatus), nullable=False, default=RequestStatus.PENDING, index=True)
    description = Column(Text, nullable=False)
    
    # Critères de recherche
    budget_max = Column(Integer, nullable=True)
    preferred_fuel_type = Column(String, nullable=True)
    preferred_transmission = Column(String, nullable=True)
    max_mileage = Column(Integer, nullable=True)
    min_year = Column(Integer, nullable=True)
    ai_parsed_criteria = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    accepted_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    
    # Relations
    client = relationship("User", foreign_keys=[client_id], backref="client_requests")
    expert = relationship("User", foreign_keys=[expert_id], backref="expert_requests")
    proposals = relationship("ProposedVehicle", back_populates="request", cascade="all, delete-orphan")

class ProposedVehicle(Base):
    """Véhicules proposés par l'expert au client"""
    __tablename__ = "proposed_vehicles"
    
    id = Column(String, primary_key=True)
    request_id = Column(String, ForeignKey('assisted_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    vehicle_id = Column(String, ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False, index=True)
    
    status = Column(SQLEnum(ProposalStatus), nullable=False, default=ProposalStatus.PENDING, index=True)
    message = Column(Text, nullable=True)  # Message de l'expert
    rejection_reason = Column(Text, nullable=True)  # Raison du refus par le client
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    request = relationship("AssistedRequest", back_populates="proposals")
    vehicle = relationship("Vehicle")

class Message(Base):
    """Messages entre utilisateurs (pour la messagerie interne)"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, nullable=False, index=True)
    sender_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    attachments = Column(JSON, default=list)  # URLs de fichiers joints
    
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    
    # Relations
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")