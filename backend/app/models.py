# backend/app/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(String, primary_key=True)
    title = Column(String)
    make = Column(String)
    model = Column(String)
    price = Column(Integer)
    mileage = Column(Integer)
    year = Column(Integer)
    source_ids = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
