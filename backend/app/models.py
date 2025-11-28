# backend/app/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    """Rôles utilisateurs"""
    ADMIN = "ADMIN"
    PRO = "PRO"
    PARTICULAR = "PARTICULAR"
    EXPERT = "EXPERT"

class User(Base):
    """Modèle utilisateur avec gestion des rôles"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.PARTICULAR, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    vehicles = relationship("Vehicle", back_populates="professional_user", foreign_keys="Vehicle.professional_user_id")
    favorites = relationship("Favorite", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

class Vehicle(Base):
    """Modèle véhicule - ALIGNÉ SUR LE SCHEMA DB RÉEL (selon migrations Alembic)

    Colonnes réelles en DB (depuis les migrations):
    - create_vehicles.py: id, title, make, model, price, mileage, year, source_ids, created_at
    - add_users_roles.py: professional_user_id
    - add_vehicle_is_active.py: is_active
    """
    __tablename__ = "vehicles"

    # ===== COLONNES QUI EXISTENT EN DB =====
    id = Column(String, primary_key=True)
    title = Column(String)
    make = Column(String, index=True)
    model = Column(String, index=True)
    price = Column(Integer, index=True)
    mileage = Column(Integer)
    year = Column(Integer)
    source_ids = Column(JSON, default=dict)  # Utiliser pour stocker: fuel_type, transmission, description, images, location, url, etc.
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    professional_user_id = Column(String, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # ===== COLONNES COMMENTÉES CAR N'EXISTENT PAS EN DB =====
    # Stocker ces données dans le JSON source_ids
    # vin = Column(String)
    # fuel_type = Column(String)
    # transmission = Column(String)
    # description = Column(Text)
    # images = Column(JSON)
    # location_lat = Column(String)
    # location_lon = Column(String)
    # location_city = Column(String)
    # updated_at = Column(TIMESTAMP)

    # Relations
    professional_user = relationship("User", back_populates="vehicles", foreign_keys=[professional_user_id])
    favorites = relationship("Favorite", back_populates="vehicle")

class Favorite(Base):
    """Favoris utilisateurs"""
    __tablename__ = "favorites"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    vehicle_id = Column(String, ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="favorites")
    vehicle = relationship("Vehicle", back_populates="favorites")

class Alert(Base):
    """Alertes de recherche"""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String, nullable=False)
    criteria = Column(JSON, nullable=False)  # Filtres de recherche sauvegardés
    frequency = Column(String, default='daily')  # daily, weekly, instant
    is_active = Column(Boolean, default=True)
    last_sent_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="alerts")

class SearchHistory(Base):
    """Historique des recherches"""
    __tablename__ = "search_history"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    query = Column(String, nullable=True)
    filters = Column(JSON, default=dict)
    results_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)


class RequestStatus(str, enum.Enum):
    """Statuts des demandes assistées"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ProposalStatus(str, enum.Enum):
    """Statuts des propositions de véhicules"""
    PENDING = "PENDING"
    LIKED = "LIKED"
    SUPER_LIKED = "SUPER_LIKED"  # Coup de foudre
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
    client_feedback = Column(Text, nullable=True)  # Feedback du client pour affiner la recherche

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