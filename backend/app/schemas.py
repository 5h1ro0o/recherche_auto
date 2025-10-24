from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from app.models import UserRole
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.PARTICULAR

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class VehicleBase(BaseModel):
    title: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    price: Optional[int] = None
    mileage: Optional[int] = None
    year: Optional[int] = None
    vin: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    professional_user_id: Optional[str] = None

class VehicleCreate(VehicleBase):
    id: Optional[str] = None

class VehicleUpdate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}