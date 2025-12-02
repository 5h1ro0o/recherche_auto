"""Pydantic schemas pour l'encyclopédie automobile"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== MARQUES ====================

class CarBrandBase(BaseModel):
    name: str
    country: Optional[str] = None
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    reputation_score: Optional[int] = None
    reliability_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    innovation_rating: Optional[int] = None
    advantages: Optional[List[str]] = []
    disadvantages: Optional[List[str]] = []
    specialties: Optional[List[str]] = []
    popular_models: Optional[List[str]] = []
    price_range: Optional[str] = None
    market_segment: Optional[str] = None


class CarBrandCreate(CarBrandBase):
    pass


class CarBrandUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    reputation_score: Optional[int] = None
    reliability_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    innovation_rating: Optional[int] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    specialties: Optional[List[str]] = None
    popular_models: Optional[List[str]] = None
    price_range: Optional[str] = None
    market_segment: Optional[str] = None
    is_active: Optional[bool] = None


class CarBrandOut(CarBrandBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== MODÈLES ====================

class CarModelBase(BaseModel):
    brand_id: str
    name: str
    generation: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    is_current: bool = True
    body_type: Optional[str] = None
    segment: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = []
    length: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    wheelbase: Optional[int] = None
    trunk_capacity: Optional[int] = None
    weight: Optional[int] = None
    max_weight: Optional[int] = None
    seats: Optional[int] = None
    doors: Optional[int] = None
    price_new_min: Optional[int] = None
    price_new_max: Optional[int] = None
    price_used_avg: Optional[int] = None
    avg_consumption: Optional[str] = None
    co2_emissions: Optional[int] = None
    top_speed: Optional[int] = None
    acceleration_0_100: Optional[str] = None
    standard_equipment: Optional[List[str]] = []
    optional_equipment: Optional[List[str]] = []
    safety_features: Optional[List[str]] = []
    tech_features: Optional[List[str]] = []
    safety_rating: Optional[int] = None
    reliability_score: Optional[int] = None
    owner_satisfaction: Optional[int] = None
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    available_engines: Optional[List[str]] = []
    available_transmissions: Optional[List[str]] = []
    competitors: Optional[List[str]] = []
    ideal_for: Optional[str] = None


class CarModelCreate(CarModelBase):
    pass


class CarModelUpdate(BaseModel):
    brand_id: Optional[str] = None
    name: Optional[str] = None
    generation: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    is_current: Optional[bool] = None
    body_type: Optional[str] = None
    segment: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    length: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    wheelbase: Optional[int] = None
    trunk_capacity: Optional[int] = None
    weight: Optional[int] = None
    max_weight: Optional[int] = None
    seats: Optional[int] = None
    doors: Optional[int] = None
    price_new_min: Optional[int] = None
    price_new_max: Optional[int] = None
    price_used_avg: Optional[int] = None
    avg_consumption: Optional[str] = None
    co2_emissions: Optional[int] = None
    top_speed: Optional[int] = None
    acceleration_0_100: Optional[str] = None
    standard_equipment: Optional[List[str]] = None
    optional_equipment: Optional[List[str]] = None
    safety_features: Optional[List[str]] = None
    tech_features: Optional[List[str]] = None
    safety_rating: Optional[int] = None
    reliability_score: Optional[int] = None
    owner_satisfaction: Optional[int] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    available_engines: Optional[List[str]] = None
    available_transmissions: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    ideal_for: Optional[str] = None
    is_active: Optional[bool] = None


class CarModelOut(CarModelBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== MOTEURS ====================

class EngineBase(BaseModel):
    name: str
    code: Optional[str] = None
    fuel_type: str
    engine_type: Optional[str] = None
    aspiration: Optional[str] = None
    displacement: Optional[int] = None
    cylinders: Optional[int] = None
    configuration: Optional[str] = None
    valves: Optional[int] = None
    power_hp: Optional[int] = None
    power_kw: Optional[int] = None
    torque_nm: Optional[int] = None
    max_torque_rpm: Optional[str] = None
    top_speed: Optional[int] = None
    acceleration_0_100: Optional[str] = None
    consumption_urban: Optional[str] = None
    consumption_extra_urban: Optional[str] = None
    consumption_combined: Optional[str] = None
    co2_emissions: Optional[int] = None
    euro_norm: Optional[str] = None
    battery_capacity: Optional[str] = None
    electric_range: Optional[int] = None
    charging_time: Optional[str] = None
    technologies: Optional[List[str]] = []
    reliability_rating: Optional[int] = None
    maintenance_cost: Optional[str] = None
    known_issues: Optional[List[str]] = []
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    ideal_for: Optional[str] = None
    description: Optional[str] = None


class EngineCreate(EngineBase):
    pass


class EngineUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    fuel_type: Optional[str] = None
    engine_type: Optional[str] = None
    aspiration: Optional[str] = None
    displacement: Optional[int] = None
    cylinders: Optional[int] = None
    configuration: Optional[str] = None
    valves: Optional[int] = None
    power_hp: Optional[int] = None
    power_kw: Optional[int] = None
    torque_nm: Optional[int] = None
    max_torque_rpm: Optional[str] = None
    top_speed: Optional[int] = None
    acceleration_0_100: Optional[str] = None
    consumption_urban: Optional[str] = None
    consumption_extra_urban: Optional[str] = None
    consumption_combined: Optional[str] = None
    co2_emissions: Optional[int] = None
    euro_norm: Optional[str] = None
    battery_capacity: Optional[str] = None
    electric_range: Optional[int] = None
    charging_time: Optional[str] = None
    technologies: Optional[List[str]] = None
    reliability_rating: Optional[int] = None
    maintenance_cost: Optional[str] = None
    known_issues: Optional[List[str]] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    ideal_for: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EngineOut(EngineBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== TRANSMISSIONS ====================

class TransmissionBase(BaseModel):
    name: str
    type: str
    gears: Optional[int] = None
    technology: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    shift_speed: Optional[str] = None
    efficiency: Optional[str] = None
    reliability_rating: Optional[int] = None
    maintenance_cost: Optional[str] = None
    known_issues: Optional[List[str]] = []
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    ideal_for: Optional[str] = None
    typical_applications: Optional[List[str]] = []


class TransmissionCreate(TransmissionBase):
    pass


class TransmissionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    gears: Optional[int] = None
    technology: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    shift_speed: Optional[str] = None
    efficiency: Optional[str] = None
    reliability_rating: Optional[int] = None
    maintenance_cost: Optional[str] = None
    known_issues: Optional[List[str]] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    ideal_for: Optional[str] = None
    typical_applications: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TransmissionOut(TransmissionBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== AVIS ====================

class BrandReviewBase(BaseModel):
    brand_id: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    content: str
    overall_rating: Optional[int] = None
    reliability_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    value_rating: Optional[int] = None
    review_date: Optional[datetime] = None


class BrandReviewCreate(BrandReviewBase):
    pass


class BrandReviewOut(BrandReviewBase):
    id: str
    helpful_count: int
    verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModelReviewBase(BaseModel):
    model_id: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    content: str
    overall_rating: Optional[int] = None
    comfort_rating: Optional[int] = None
    performance_rating: Optional[int] = None
    fuel_economy_rating: Optional[int] = None
    reliability_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    value_rating: Optional[int] = None
    technology_rating: Optional[int] = None
    ownership_duration: Optional[str] = None
    mileage: Optional[int] = None
    usage_type: Optional[str] = None
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    review_date: Optional[datetime] = None


class ModelReviewCreate(ModelReviewBase):
    pass


class ModelReviewOut(ModelReviewBase):
    id: str
    helpful_count: int
    verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EngineReviewBase(BaseModel):
    engine_id: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    content: str
    overall_rating: Optional[int] = None
    performance_rating: Optional[int] = None
    fuel_economy_rating: Optional[int] = None
    reliability_rating: Optional[int] = None
    refinement_rating: Optional[int] = None
    mileage: Optional[int] = None
    ownership_duration: Optional[str] = None
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    review_date: Optional[datetime] = None


class EngineReviewCreate(EngineReviewBase):
    pass


class EngineReviewOut(EngineReviewBase):
    id: str
    helpful_count: int
    verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransmissionReviewBase(BaseModel):
    transmission_id: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    content: str
    overall_rating: Optional[int] = None
    smoothness_rating: Optional[int] = None
    reliability_rating: Optional[int] = None
    responsiveness_rating: Optional[int] = None
    mileage: Optional[int] = None
    ownership_duration: Optional[str] = None
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    review_date: Optional[datetime] = None


class TransmissionReviewCreate(TransmissionReviewBase):
    pass


class TransmissionReviewOut(TransmissionReviewBase):
    id: str
    helpful_count: int
    verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== SPÉCIFICATIONS TECHNIQUES ====================

class TechnicalSpecificationBase(BaseModel):
    model_id: str
    version_name: str
    trim_level: Optional[str] = None
    engine_id: Optional[str] = None
    transmission_id: Optional[str] = None
    power_hp: Optional[int] = None
    torque_nm: Optional[int] = None
    top_speed: Optional[int] = None
    acceleration_0_100: Optional[str] = None
    consumption_combined: Optional[str] = None
    co2_emissions: Optional[int] = None
    price_new: Optional[int] = None
    price_used_avg: Optional[int] = None
    standard_equipment: Optional[List[str]] = []
    optional_equipment: Optional[List[str]] = []
    year_start: Optional[int] = None
    year_end: Optional[int] = None


class TechnicalSpecificationCreate(TechnicalSpecificationBase):
    pass


class TechnicalSpecificationOut(TechnicalSpecificationBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== RÉPONSES COMBINÉES ====================

class CarBrandWithModels(CarBrandOut):
    """Marque avec ses modèles"""
    models: List[CarModelOut] = []


class CarModelWithDetails(CarModelOut):
    """Modèle avec marque, specs et avis"""
    brand: Optional[CarBrandOut] = None
    specifications: List[TechnicalSpecificationOut] = []
    reviews: List[ModelReviewOut] = []


class EngineWithReviews(EngineOut):
    """Moteur avec avis"""
    reviews: List[EngineReviewOut] = []


class TransmissionWithReviews(TransmissionOut):
    """Transmission avec avis"""
    reviews: List[TransmissionReviewOut] = []
