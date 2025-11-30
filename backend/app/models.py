# backend/app/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP, Boolean, ForeignKey, Text, Enum as SQLEnum, Table
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


# ==================== ENCYCLOPÉDIE AUTOMOBILE ====================

class CarBrand(Base):
    """Marques automobiles avec toutes leurs informations"""
    __tablename__ = "car_brands"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    country = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    founded_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

    # Réputation et caractéristiques
    reputation_score = Column(Integer, nullable=True)  # Note sur 100
    reliability_rating = Column(Integer, nullable=True)  # Note sur 5
    quality_rating = Column(Integer, nullable=True)  # Note sur 5
    innovation_rating = Column(Integer, nullable=True)  # Note sur 5

    # Avantages et inconvénients
    advantages = Column(JSON, default=list)  # Liste de points forts
    disadvantages = Column(JSON, default=list)  # Liste de points faibles

    # Informations additionnelles
    specialties = Column(JSON, default=list)  # Ex: "SUV", "Électrique", "Luxe"
    popular_models = Column(JSON, default=list)  # Modèles les plus vendus
    price_range = Column(String, nullable=True)  # Ex: "15000-80000"
    market_segment = Column(String, nullable=True)  # Premium, Généraliste, Luxe, etc.

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    models = relationship("CarModel", back_populates="brand", cascade="all, delete-orphan")
    reviews = relationship("BrandReview", back_populates="brand", cascade="all, delete-orphan")


class CarModel(Base):
    """Modèles de voiture avec caractéristiques détaillées"""
    __tablename__ = "car_models"

    id = Column(String, primary_key=True)
    brand_id = Column(String, ForeignKey('car_brands.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    generation = Column(String, nullable=True)  # Ex: "Phase 2", "MK3"

    # Années de production
    year_start = Column(Integer, nullable=True, index=True)
    year_end = Column(Integer, nullable=True, index=True)  # NULL si toujours en production
    is_current = Column(Boolean, default=True)  # Toujours en vente neuf

    # Catégorie et type
    body_type = Column(String, nullable=True)  # Berline, SUV, Break, Coupé, etc.
    segment = Column(String, nullable=True)  # Segment A, B, C, D, etc.
    category = Column(String, nullable=True)  # Citadine, Compacte, Familiale, etc.

    # Informations générales
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    images = Column(JSON, default=list)  # Galerie d'images

    # Dimensions (en mm)
    length = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    wheelbase = Column(Integer, nullable=True)
    trunk_capacity = Column(Integer, nullable=True)  # En litres

    # Poids et capacités
    weight = Column(Integer, nullable=True)  # Poids à vide en kg
    max_weight = Column(Integer, nullable=True)  # PTAC en kg
    seats = Column(Integer, nullable=True)  # Nombre de places
    doors = Column(Integer, nullable=True)  # Nombre de portes

    # Prix (en euros)
    price_new_min = Column(Integer, nullable=True, index=True)
    price_new_max = Column(Integer, nullable=True)
    price_used_avg = Column(Integer, nullable=True)  # Prix moyen d'occasion

    # Consommation et performances moyennes
    avg_consumption = Column(String, nullable=True)  # L/100km ou kWh/100km
    co2_emissions = Column(Integer, nullable=True)  # g/km
    top_speed = Column(Integer, nullable=True)  # km/h
    acceleration_0_100 = Column(String, nullable=True)  # secondes

    # Équipements et technologies
    standard_equipment = Column(JSON, default=list)
    optional_equipment = Column(JSON, default=list)
    safety_features = Column(JSON, default=list)
    tech_features = Column(JSON, default=list)

    # Évaluations
    safety_rating = Column(Integer, nullable=True)  # Euro NCAP sur 5
    reliability_score = Column(Integer, nullable=True)  # Sur 100
    owner_satisfaction = Column(Integer, nullable=True)  # Sur 100

    # Avantages et inconvénients
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)

    # Motorisations disponibles (référence vers Engine)
    available_engines = Column(JSON, default=list)  # IDs des moteurs disponibles
    available_transmissions = Column(JSON, default=list)  # IDs des transmissions disponibles

    # Informations complémentaires
    competitors = Column(JSON, default=list)  # Modèles concurrents
    ideal_for = Column(Text, nullable=True)  # Pour quel type d'usage

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    brand = relationship("CarBrand", back_populates="models")
    specifications = relationship("TechnicalSpecification", back_populates="model", cascade="all, delete-orphan")
    reviews = relationship("ModelReview", back_populates="model", cascade="all, delete-orphan")
    # Relations many-to-many avec moteurs et transmissions
    engines = relationship("Engine", secondary="engine_model_associations", back_populates="models")
    transmissions = relationship("Transmission", secondary="transmission_model_associations", back_populates="models")


# Tables de liaison many-to-many

# Liaison Engine ↔ CarModel (un moteur peut équiper plusieurs modèles)
engine_model_association = Table(
    'engine_model_associations',
    Base.metadata,
    Column('engine_id', String, ForeignKey('engines.id', ondelete='CASCADE'), primary_key=True),
    Column('model_id', String, ForeignKey('car_models.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

# Liaison Transmission ↔ CarModel (une boîte peut équiper plusieurs modèles)
transmission_model_association = Table(
    'transmission_model_associations',
    Base.metadata,
    Column('transmission_id', String, ForeignKey('transmissions.id', ondelete='CASCADE'), primary_key=True),
    Column('model_id', String, ForeignKey('car_models.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

# Liaison Engine ↔ Transmission (associations moteur-boîte possibles)
engine_transmission_association = Table(
    'engine_transmission_associations',
    Base.metadata,
    Column('engine_id', String, ForeignKey('engines.id', ondelete='CASCADE'), primary_key=True),
    Column('transmission_id', String, ForeignKey('transmissions.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)


class Engine(Base):
    """Moteurs avec caractéristiques techniques détaillées"""
    __tablename__ = "engines"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)  # Ex: "1.5 dCi 110", "2.0 TSI 245"
    code = Column(String, nullable=True)  # Code constructeur

    # Type de moteur
    fuel_type = Column(String, nullable=False, index=True)  # Essence, Diesel, Hybride, Électrique, GPL, etc.
    engine_type = Column(String, nullable=True)  # Thermique, Électrique, Hybride
    aspiration = Column(String, nullable=True)  # Atmosphérique, Turbo, Compresseur

    # Caractéristiques techniques
    displacement = Column(Integer, nullable=True)  # Cylindrée en cm³
    cylinders = Column(Integer, nullable=True)  # Nombre de cylindres
    configuration = Column(String, nullable=True)  # En ligne, V, Boxer, etc.
    valves = Column(Integer, nullable=True)  # Nombre de soupapes

    # Puissance et couple
    power_hp = Column(Integer, nullable=True, index=True)  # Puissance en chevaux
    power_kw = Column(Integer, nullable=True)  # Puissance en kW
    torque_nm = Column(Integer, nullable=True)  # Couple en Nm
    max_torque_rpm = Column(String, nullable=True)  # Régime du couple max

    # Performances
    top_speed = Column(Integer, nullable=True)  # Vitesse max en km/h
    acceleration_0_100 = Column(String, nullable=True)  # 0-100 km/h en secondes

    # Consommation et émissions
    consumption_urban = Column(String, nullable=True)  # L/100km en ville
    consumption_extra_urban = Column(String, nullable=True)  # L/100km sur route
    consumption_combined = Column(String, nullable=True)  # L/100km mixte
    co2_emissions = Column(Integer, nullable=True)  # g/km
    euro_norm = Column(String, nullable=True)  # Euro 5, Euro 6d, etc.

    # Spécificités électrique/hybride
    battery_capacity = Column(String, nullable=True)  # kWh pour électrique
    electric_range = Column(Integer, nullable=True)  # Autonomie en km
    charging_time = Column(String, nullable=True)  # Temps de recharge

    # Technologies
    technologies = Column(JSON, default=list)  # Start-Stop, Injection directe, etc.

    # Fiabilité et entretien
    reliability_rating = Column(Integer, nullable=True)  # Sur 5
    maintenance_cost = Column(String, nullable=True)  # Faible, Moyen, Élevé
    known_issues = Column(JSON, default=list)  # Problèmes connus

    # Avantages et inconvénients
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)

    # Informations additionnelles
    ideal_for = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    reviews = relationship("EngineReview", back_populates="engine", cascade="all, delete-orphan")
    # Relation many-to-many avec les modèles
    models = relationship("CarModel", secondary=engine_model_association, back_populates="engines")
    # Relation many-to-many avec les transmissions
    transmissions = relationship("Transmission", secondary=engine_transmission_association, back_populates="engines")


class Transmission(Base):
    """Boîtes de vitesse avec caractéristiques"""
    __tablename__ = "transmissions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)  # Ex: "BVM6", "BVA8", "DSG7"
    type = Column(String, nullable=False, index=True)  # Manuelle, Automatique, Robotisée, CVT

    # Caractéristiques
    gears = Column(Integer, nullable=True)  # Nombre de rapports
    technology = Column(String, nullable=True)  # Double embrayage, Convertisseur, CVT, etc.
    manufacturer = Column(String, nullable=True)  # ZF, Aisin, Getrag, etc.

    # Description et caractéristiques
    description = Column(Text, nullable=True)

    # Performances
    shift_speed = Column(String, nullable=True)  # Rapidité de passage des rapports
    efficiency = Column(String, nullable=True)  # Rendement énergétique

    # Fiabilité
    reliability_rating = Column(Integer, nullable=True)  # Sur 5
    maintenance_cost = Column(String, nullable=True)  # Faible, Moyen, Élevé
    known_issues = Column(JSON, default=list)

    # Avantages et inconvénients
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)

    # Informations additionnelles
    ideal_for = Column(Text, nullable=True)
    typical_applications = Column(JSON, default=list)  # Types de véhicules utilisant cette boîte

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    reviews = relationship("TransmissionReview", back_populates="transmission", cascade="all, delete-orphan")
    # Relation many-to-many avec les modèles
    models = relationship("CarModel", secondary=transmission_model_association, back_populates="transmissions")
    # Relation many-to-many avec les moteurs
    engines = relationship("Engine", secondary=engine_transmission_association, back_populates="transmissions")


class TechnicalSpecification(Base):
    """Spécifications techniques détaillées par version de modèle"""
    __tablename__ = "technical_specifications"

    id = Column(String, primary_key=True)
    model_id = Column(String, ForeignKey('car_models.id', ondelete='CASCADE'), nullable=False, index=True)

    # Identification de la version
    version_name = Column(String, nullable=False)  # Ex: "1.5 dCi 110 Intens"
    trim_level = Column(String, nullable=True)  # Niveau de finition

    # Motorisation
    engine_id = Column(String, ForeignKey('engines.id', ondelete='SET NULL'), nullable=True)
    transmission_id = Column(String, ForeignKey('transmissions.id', ondelete='SET NULL'), nullable=True)

    # Données spécifiques à cette version
    power_hp = Column(Integer, nullable=True)
    torque_nm = Column(Integer, nullable=True)
    top_speed = Column(Integer, nullable=True)
    acceleration_0_100 = Column(String, nullable=True)
    consumption_combined = Column(String, nullable=True)
    co2_emissions = Column(Integer, nullable=True)

    # Prix
    price_new = Column(Integer, nullable=True)
    price_used_avg = Column(Integer, nullable=True)

    # Équipements spécifiques
    standard_equipment = Column(JSON, default=list)
    optional_equipment = Column(JSON, default=list)

    year_start = Column(Integer, nullable=True)
    year_end = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    model = relationship("CarModel", back_populates="specifications")
    engine = relationship("Engine")
    transmission = relationship("Transmission")


class BrandReview(Base):
    """Avis et retours clients sur les marques"""
    __tablename__ = "brand_reviews"

    id = Column(String, primary_key=True)
    brand_id = Column(String, ForeignKey('car_brands.id', ondelete='CASCADE'), nullable=False, index=True)

    # Source de l'avis
    source = Column(String, nullable=True)  # Forum, site, magazine, etc.
    source_url = Column(String, nullable=True)
    author = Column(String, nullable=True)

    # Contenu
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Évaluations
    overall_rating = Column(Integer, nullable=True)  # Sur 5
    reliability_rating = Column(Integer, nullable=True)
    quality_rating = Column(Integer, nullable=True)
    value_rating = Column(Integer, nullable=True)

    # Métadonnées
    helpful_count = Column(Integer, default=0)  # Nombre de "utile"
    review_date = Column(TIMESTAMP, nullable=True)
    verified = Column(Boolean, default=False)  # Avis vérifié

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    brand = relationship("CarBrand", back_populates="reviews")


class ModelReview(Base):
    """Avis et retours clients sur les modèles"""
    __tablename__ = "model_reviews"

    id = Column(String, primary_key=True)
    model_id = Column(String, ForeignKey('car_models.id', ondelete='CASCADE'), nullable=False, index=True)

    # Source de l'avis
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    author = Column(String, nullable=True)

    # Contenu
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Évaluations détaillées
    overall_rating = Column(Integer, nullable=True)  # Sur 5
    comfort_rating = Column(Integer, nullable=True)
    performance_rating = Column(Integer, nullable=True)
    fuel_economy_rating = Column(Integer, nullable=True)
    reliability_rating = Column(Integer, nullable=True)
    quality_rating = Column(Integer, nullable=True)
    value_rating = Column(Integer, nullable=True)
    technology_rating = Column(Integer, nullable=True)

    # Contexte d'utilisation
    ownership_duration = Column(String, nullable=True)  # Ex: "2 ans"
    mileage = Column(Integer, nullable=True)  # Kilométrage lors de l'avis
    usage_type = Column(String, nullable=True)  # Urbain, Mixte, Autoroute

    # Points positifs et négatifs
    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)

    # Métadonnées
    helpful_count = Column(Integer, default=0)
    review_date = Column(TIMESTAMP, nullable=True)
    verified = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    model = relationship("CarModel", back_populates="reviews")


class EngineReview(Base):
    """Avis et retours sur les moteurs"""
    __tablename__ = "engine_reviews"

    id = Column(String, primary_key=True)
    engine_id = Column(String, ForeignKey('engines.id', ondelete='CASCADE'), nullable=False, index=True)

    # Source
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    author = Column(String, nullable=True)

    # Contenu
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Évaluations
    overall_rating = Column(Integer, nullable=True)
    performance_rating = Column(Integer, nullable=True)
    fuel_economy_rating = Column(Integer, nullable=True)
    reliability_rating = Column(Integer, nullable=True)
    refinement_rating = Column(Integer, nullable=True)

    # Contexte
    mileage = Column(Integer, nullable=True)
    ownership_duration = Column(String, nullable=True)

    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)

    helpful_count = Column(Integer, default=0)
    review_date = Column(TIMESTAMP, nullable=True)
    verified = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    engine = relationship("Engine", back_populates="reviews")


class TransmissionReview(Base):
    """Avis sur les boîtes de vitesse"""
    __tablename__ = "transmission_reviews"

    id = Column(String, primary_key=True)
    transmission_id = Column(String, ForeignKey('transmissions.id', ondelete='CASCADE'), nullable=False, index=True)

    # Source
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    author = Column(String, nullable=True)

    # Contenu
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Évaluations
    overall_rating = Column(Integer, nullable=True)
    smoothness_rating = Column(Integer, nullable=True)
    reliability_rating = Column(Integer, nullable=True)
    responsiveness_rating = Column(Integer, nullable=True)

    # Contexte
    mileage = Column(Integer, nullable=True)
    ownership_duration = Column(String, nullable=True)

    pros = Column(JSON, default=list)
    cons = Column(JSON, default=list)

    helpful_count = Column(Integer, default=0)
    review_date = Column(TIMESTAMP, nullable=True)
    verified = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    transmission = relationship("Transmission", back_populates="reviews")