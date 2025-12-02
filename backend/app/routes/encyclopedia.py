"""Routes API pour l'encyclopédie automobile"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.db import get_db
from app.models import (
    CarBrand, CarModel, Engine, Transmission,
    BrandReview, ModelReview, EngineReview, TransmissionReview,
    TechnicalSpecification
)
from app.schemas_encyclopedia import (
    CarBrandOut, CarBrandCreate, CarBrandUpdate, CarBrandWithModels,
    CarModelOut, CarModelCreate, CarModelUpdate, CarModelWithDetails,
    EngineOut, EngineCreate, EngineUpdate, EngineWithReviews,
    TransmissionOut, TransmissionCreate, TransmissionUpdate, TransmissionWithReviews,
    BrandReviewOut, BrandReviewCreate,
    ModelReviewOut, ModelReviewCreate,
    EngineReviewOut, EngineReviewCreate,
    TransmissionReviewOut, TransmissionReviewCreate,
    TechnicalSpecificationOut, TechnicalSpecificationCreate
)

router = APIRouter(prefix="/encyclopedia", tags=["encyclopedia"])


# ==================== MARQUES ====================

@router.get("/brands", response_model=List[CarBrandOut])
def get_brands(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    country: Optional[str] = None,
    market_segment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère toutes les marques avec filtres optionnels"""
    query = db.query(CarBrand).filter(CarBrand.is_active == True)

    if search:
        query = query.filter(CarBrand.name.ilike(f"%{search}%"))
    if country:
        query = query.filter(CarBrand.country == country)
    if market_segment:
        query = query.filter(CarBrand.market_segment == market_segment)

    query = query.order_by(CarBrand.name)
    return query.offset(skip).limit(limit).all()


@router.get("/brands/{brand_id}", response_model=CarBrandWithModels)
def get_brand(brand_id: str, db: Session = Depends(get_db)):
    """Récupère une marque avec ses modèles"""
    brand = db.query(CarBrand).options(
        joinedload(CarBrand.models)
    ).filter(CarBrand.id == brand_id).first()

    if not brand:
        raise HTTPException(status_code=404, detail="Marque non trouvée")

    return brand


@router.post("/brands", response_model=CarBrandOut)
def create_brand(brand: CarBrandCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle marque"""
    db_brand = CarBrand(
        id=str(uuid.uuid4()),
        **brand.model_dump()
    )
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


@router.put("/brands/{brand_id}", response_model=CarBrandOut)
def update_brand(brand_id: str, brand: CarBrandUpdate, db: Session = Depends(get_db)):
    """Met à jour une marque"""
    db_brand = db.query(CarBrand).filter(CarBrand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(status_code=404, detail="Marque non trouvée")

    for key, value in brand.model_dump(exclude_unset=True).items():
        setattr(db_brand, key, value)

    db.commit()
    db.refresh(db_brand)
    return db_brand


@router.delete("/brands/{brand_id}")
def delete_brand(brand_id: str, db: Session = Depends(get_db)):
    """Supprime une marque (soft delete)"""
    db_brand = db.query(CarBrand).filter(CarBrand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(status_code=404, detail="Marque non trouvée")

    db_brand.is_active = False
    db.commit()
    return {"message": "Marque supprimée"}


# ==================== MODÈLES ====================

@router.get("/models", response_model=List[CarModelOut])
def get_models(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    brand_id: Optional[str] = None,
    body_type: Optional[str] = None,
    category: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    is_current: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupère tous les modèles avec filtres optionnels"""
    query = db.query(CarModel).filter(CarModel.is_active == True)

    if search:
        query = query.filter(CarModel.name.ilike(f"%{search}%"))
    if brand_id:
        query = query.filter(CarModel.brand_id == brand_id)
    if body_type:
        query = query.filter(CarModel.body_type == body_type)
    if category:
        query = query.filter(CarModel.category == category)
    if year_min:
        query = query.filter(CarModel.year_start >= year_min)
    if year_max:
        query = query.filter(
            (CarModel.year_end <= year_max) | (CarModel.year_end == None)
        )
    if price_min:
        query = query.filter(CarModel.price_new_min >= price_min)
    if price_max:
        query = query.filter(CarModel.price_new_max <= price_max)
    if is_current is not None:
        query = query.filter(CarModel.is_current == is_current)

    query = query.order_by(CarModel.name)
    return query.offset(skip).limit(limit).all()


@router.get("/models/{model_id}", response_model=CarModelWithDetails)
def get_model(model_id: str, db: Session = Depends(get_db)):
    """Récupère un modèle avec tous ses détails"""
    model = db.query(CarModel).options(
        joinedload(CarModel.brand),
        joinedload(CarModel.specifications),
        joinedload(CarModel.reviews)
    ).filter(CarModel.id == model_id).first()

    if not model:
        raise HTTPException(status_code=404, detail="Modèle non trouvé")

    return model


@router.post("/models", response_model=CarModelOut)
def create_model(model: CarModelCreate, db: Session = Depends(get_db)):
    """Crée un nouveau modèle"""
    db_model = CarModel(
        id=str(uuid.uuid4()),
        **model.model_dump()
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put("/models/{model_id}", response_model=CarModelOut)
def update_model(model_id: str, model: CarModelUpdate, db: Session = Depends(get_db)):
    """Met à jour un modèle"""
    db_model = db.query(CarModel).filter(CarModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Modèle non trouvé")

    for key, value in model.model_dump(exclude_unset=True).items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/models/{model_id}")
def delete_model(model_id: str, db: Session = Depends(get_db)):
    """Supprime un modèle (soft delete)"""
    db_model = db.query(CarModel).filter(CarModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Modèle non trouvé")

    db_model.is_active = False
    db.commit()
    return {"message": "Modèle supprimé"}


# ==================== MOTEURS ====================

@router.get("/engines", response_model=List[EngineOut])
def get_engines(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    fuel_type: Optional[str] = None,
    power_min: Optional[int] = None,
    power_max: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Récupère tous les moteurs avec filtres optionnels"""
    query = db.query(Engine).filter(Engine.is_active == True)

    if search:
        query = query.filter(Engine.name.ilike(f"%{search}%"))
    if fuel_type:
        query = query.filter(Engine.fuel_type == fuel_type)
    if power_min:
        query = query.filter(Engine.power_hp >= power_min)
    if power_max:
        query = query.filter(Engine.power_hp <= power_max)

    query = query.order_by(Engine.name)
    return query.offset(skip).limit(limit).all()


@router.get("/engines/{engine_id}", response_model=EngineWithReviews)
def get_engine(engine_id: str, db: Session = Depends(get_db)):
    """Récupère un moteur avec ses avis"""
    engine = db.query(Engine).options(
        joinedload(Engine.reviews)
    ).filter(Engine.id == engine_id).first()

    if not engine:
        raise HTTPException(status_code=404, detail="Moteur non trouvé")

    return engine


@router.post("/engines", response_model=EngineOut)
def create_engine(engine: EngineCreate, db: Session = Depends(get_db)):
    """Crée un nouveau moteur"""
    db_engine = Engine(
        id=str(uuid.uuid4()),
        **engine.model_dump()
    )
    db.add(db_engine)
    db.commit()
    db.refresh(db_engine)
    return db_engine


@router.put("/engines/{engine_id}", response_model=EngineOut)
def update_engine(engine_id: str, engine: EngineUpdate, db: Session = Depends(get_db)):
    """Met à jour un moteur"""
    db_engine = db.query(Engine).filter(Engine.id == engine_id).first()
    if not db_engine:
        raise HTTPException(status_code=404, detail="Moteur non trouvé")

    for key, value in engine.model_dump(exclude_unset=True).items():
        setattr(db_engine, key, value)

    db.commit()
    db.refresh(db_engine)
    return db_engine


@router.delete("/engines/{engine_id}")
def delete_engine(engine_id: str, db: Session = Depends(get_db)):
    """Supprime un moteur (soft delete)"""
    db_engine = db.query(Engine).filter(Engine.id == engine_id).first()
    if not db_engine:
        raise HTTPException(status_code=404, detail="Moteur non trouvé")

    db_engine.is_active = False
    db.commit()
    return {"message": "Moteur supprimé"}


# ==================== TRANSMISSIONS ====================

@router.get("/transmissions", response_model=List[TransmissionOut])
def get_transmissions(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère toutes les transmissions avec filtres optionnels"""
    query = db.query(Transmission).filter(Transmission.is_active == True)

    if search:
        query = query.filter(Transmission.name.ilike(f"%{search}%"))
    if type:
        query = query.filter(Transmission.type == type)

    query = query.order_by(Transmission.name)
    return query.offset(skip).limit(limit).all()


@router.get("/transmissions/{transmission_id}", response_model=TransmissionWithReviews)
def get_transmission(transmission_id: str, db: Session = Depends(get_db)):
    """Récupère une transmission avec ses avis"""
    transmission = db.query(Transmission).options(
        joinedload(Transmission.reviews)
    ).filter(Transmission.id == transmission_id).first()

    if not transmission:
        raise HTTPException(status_code=404, detail="Transmission non trouvée")

    return transmission


@router.post("/transmissions", response_model=TransmissionOut)
def create_transmission(transmission: TransmissionCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle transmission"""
    db_transmission = Transmission(
        id=str(uuid.uuid4()),
        **transmission.model_dump()
    )
    db.add(db_transmission)
    db.commit()
    db.refresh(db_transmission)
    return db_transmission


@router.put("/transmissions/{transmission_id}", response_model=TransmissionOut)
def update_transmission(transmission_id: str, transmission: TransmissionUpdate, db: Session = Depends(get_db)):
    """Met à jour une transmission"""
    db_transmission = db.query(Transmission).filter(Transmission.id == transmission_id).first()
    if not db_transmission:
        raise HTTPException(status_code=404, detail="Transmission non trouvée")

    for key, value in transmission.model_dump(exclude_unset=True).items():
        setattr(db_transmission, key, value)

    db.commit()
    db.refresh(db_transmission)
    return db_transmission


@router.delete("/transmissions/{transmission_id}")
def delete_transmission(transmission_id: str, db: Session = Depends(get_db)):
    """Supprime une transmission (soft delete)"""
    db_transmission = db.query(Transmission).filter(Transmission.id == transmission_id).first()
    if not db_transmission:
        raise HTTPException(status_code=404, detail="Transmission non trouvée")

    db_transmission.is_active = False
    db.commit()
    return {"message": "Transmission supprimée"}


# ==================== AVIS ====================

@router.post("/brands/{brand_id}/reviews", response_model=BrandReviewOut)
def create_brand_review(brand_id: str, review: BrandReviewCreate, db: Session = Depends(get_db)):
    """Crée un avis sur une marque"""
    db_review = BrandReview(
        id=str(uuid.uuid4()),
        **review.model_dump()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/brands/{brand_id}/reviews", response_model=List[BrandReviewOut])
def get_brand_reviews(brand_id: str, db: Session = Depends(get_db)):
    """Récupère les avis d'une marque"""
    return db.query(BrandReview).filter(BrandReview.brand_id == brand_id).all()


@router.post("/models/{model_id}/reviews", response_model=ModelReviewOut)
def create_model_review(model_id: str, review: ModelReviewCreate, db: Session = Depends(get_db)):
    """Crée un avis sur un modèle"""
    db_review = ModelReview(
        id=str(uuid.uuid4()),
        **review.model_dump()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/models/{model_id}/reviews", response_model=List[ModelReviewOut])
def get_model_reviews(model_id: str, db: Session = Depends(get_db)):
    """Récupère les avis d'un modèle"""
    return db.query(ModelReview).filter(ModelReview.model_id == model_id).all()


@router.post("/engines/{engine_id}/reviews", response_model=EngineReviewOut)
def create_engine_review(engine_id: str, review: EngineReviewCreate, db: Session = Depends(get_db)):
    """Crée un avis sur un moteur"""
    db_review = EngineReview(
        id=str(uuid.uuid4()),
        **review.model_dump()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/engines/{engine_id}/reviews", response_model=List[EngineReviewOut])
def get_engine_reviews(engine_id: str, db: Session = Depends(get_db)):
    """Récupère les avis d'un moteur"""
    return db.query(EngineReview).filter(EngineReview.engine_id == engine_id).all()


@router.post("/transmissions/{transmission_id}/reviews", response_model=TransmissionReviewOut)
def create_transmission_review(transmission_id: str, review: TransmissionReviewCreate, db: Session = Depends(get_db)):
    """Crée un avis sur une transmission"""
    db_review = TransmissionReview(
        id=str(uuid.uuid4()),
        **review.model_dump()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/transmissions/{transmission_id}/reviews", response_model=List[TransmissionReviewOut])
def get_transmission_reviews(transmission_id: str, db: Session = Depends(get_db)):
    """Récupère les avis d'une transmission"""
    return db.query(TransmissionReview).filter(TransmissionReview.transmission_id == transmission_id).all()


# ==================== STATS ET FILTRES ====================

@router.get("/stats/fuel-types")
def get_fuel_types_stats(db: Session = Depends(get_db)):
    """Statistiques sur les types de carburant"""
    fuel_types = db.query(Engine.fuel_type).distinct().all()
    stats = []
    for (fuel_type,) in fuel_types:
        count = db.query(Engine).filter(
            Engine.fuel_type == fuel_type,
            Engine.is_active == True
        ).count()
        stats.append({"fuel_type": fuel_type, "count": count})
    return stats


@router.get("/stats/body-types")
def get_body_types_stats(db: Session = Depends(get_db)):
    """Statistiques sur les types de carrosserie"""
    body_types = db.query(CarModel.body_type).distinct().all()
    stats = []
    for (body_type,) in body_types:
        if body_type:
            count = db.query(CarModel).filter(
                CarModel.body_type == body_type,
                CarModel.is_active == True
            ).count()
            stats.append({"body_type": body_type, "count": count})
    return stats


@router.get("/stats/brands")
def get_brands_stats(db: Session = Depends(get_db)):
    """Statistiques sur les marques"""
    brands = db.query(CarBrand).filter(CarBrand.is_active == True).all()
    stats = []
    for brand in brands:
        model_count = db.query(CarModel).filter(
            CarModel.brand_id == brand.id,
            CarModel.is_active == True
        ).count()
        stats.append({
            "brand_id": brand.id,
            "brand_name": brand.name,
            "model_count": model_count,
            "country": brand.country,
            "market_segment": brand.market_segment
        })
    return stats
