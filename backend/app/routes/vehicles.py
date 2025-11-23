# backend/app/routes/vehicles.py
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app import models  # expects app.models.Vehicle
from app.schemas import VehicleCreate, VehicleOut, VehicleUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[VehicleOut])
def list_vehicles(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    try:
        skip = (page - 1) * size
        q = db.query(models.Vehicle).order_by(models.Vehicle.created_at.desc()).offset(skip).limit(size).all()
        return q
    except Exception as e:
        logger.exception("Erreur list_vehicles")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la récupération des véhicules")

@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    try:
        # Check if this is a scraped vehicle ID (format: source_id)
        if '_' in vehicle_id and vehicle_id.split('_', 1)[0] in ['leboncoin', 'autoscout24']:
            source, external_id = vehicle_id.split('_', 1)

            # For scraped vehicles, we return mock data with the external URL
            # In a real implementation, you would fetch details from the scraper
            return {
                "id": vehicle_id,
                "source_ids": {source: external_id},
                "title": "Véhicule depuis " + source,
                "description": "Cliquez sur 'Voir l'annonce' pour voir les détails complets sur " + source,
                "price": None,
                "year": None,
                "mileage": None,
                "fuel_type": None,
                "transmission": None,
                "location_city": None,
                "url": f"https://www.{source}.fr/" if source == "leboncoin" else f"https://www.autoscout24.fr/",
                "images": []
            }

        # Normal DB vehicle lookup
        v = db.get(models.Vehicle, vehicle_id)
        if not v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        return v
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur get_vehicle %s", vehicle_id)
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la récupération du véhicule")

@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    try:
        # ensure id exists (generate if not provided)
        vid = payload.id or str(uuid.uuid4())
        # check existence
        exists = db.get(models.Vehicle, vid)
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle id already exists")
        data = payload.dict(exclude_unset=True)
        data["id"] = vid
        # create model instance - adapt depending on your model constructor
        obj = models.Vehicle(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur create_vehicle payload=%s", getattr(payload, "dict", lambda: {})())
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la création du véhicule")

@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: str, payload: VehicleUpdate, db: Session = Depends(get_db)):
    try:
        v = db.get(models.Vehicle, vehicle_id)
        if not v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        for k, val in payload.dict(exclude_unset=True).items():
            setattr(v, k, val)
        db.add(v)
        db.commit()
        db.refresh(v)
        return v
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur update_vehicle %s", vehicle_id)
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la mise à jour du véhicule")

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    try:
        v = db.get(models.Vehicle, vehicle_id)
        if not v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        db.delete(v)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur delete_vehicle %s", vehicle_id)
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la suppression du véhicule")
