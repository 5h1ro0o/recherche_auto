# backend/app/schemas.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class VehicleBase(BaseModel):
    title: Optional[str]
    make: Optional[str]
    model: Optional[str]
    price: Optional[int]
    mileage: Optional[int]
    year: Optional[int]
    vin: Optional[str]
    images: Optional[List[str]] = []
    source_ids: Optional[Dict[str, Any]] = {}

class VehicleCreate(VehicleBase):
    id: Optional[str] = None  # allow client-provided id (otherwise DB/worker generates)

class VehicleUpdate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# Search
class SearchRequest(BaseModel):
    q: Optional[str] = None
    filters: Optional[Dict[str, Any]] = {}
    page: int = 1
    size: int = 20

class SearchHit(BaseModel):
    id: str
    score: float
    source: Dict[str, Any]

class SearchResponse(BaseModel):
    total: int
    hits: List[SearchHit]
