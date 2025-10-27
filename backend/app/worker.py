"""
Worker autonome pour PostgreSQL + Elasticsearch + Redis
-------------------------------------------------------

Ce worker :
- se connecte à ta base Postgres via DATABASE_URL (ex: postgresql+psycopg2://user:pass@localhost:5432/recherche_auto)
- consomme une file Redis ('scraper_queue')
- normalise, déduplique et indexe les annonces dans Elasticsearch

Usage :
    python app/worker.py --run-worker       # boucle continue sur Redis
    python app/worker.py --test-single      # test rapide local
    python app/worker.py --process-file fichier.json
"""

import os
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from math import radians, cos, sin, asin, sqrt

# === ENVIRONNEMENT ===
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/recherche_auto")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
ES_INDEX = os.getenv("ES_INDEX", "vehicles")
REDIS_QUEUE_KEY = os.getenv("REDIS_QUEUE_KEY", "scraper_queue")

# === LIBS ===
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from elasticsearch import Elasticsearch
import redis

# === INITIALISATION DES CLIENTS ===
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

es = Elasticsearch(hosts=[ELASTIC_HOST])
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# === IMPORT DU MODÈLE ===
try:
    from app.models import Vehicle
except Exception as e:
    print("⚠️ Impossible d'importer app.models.Vehicle :", e)
    Vehicle = None

# === FONCTIONS UTILES ===
def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))

def similar(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_int(v):
    try:
        return int(str(v).replace(" ", "").replace(",", "").replace(".", ""))
    except:
        return None

# === NORMALISATION ===
def normalize(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Nettoie et formate une annonce pour ingestion."""
    n = {}
    n["source"] = raw.get("source")
    n["source_id"] = raw.get("id") or raw.get("source_id")
    n["title"] = (raw.get("title") or "").strip()
    n["make"] = raw.get("make") or raw.get("brand")
    n["model"] = raw.get("model")
    n["price"] = parse_int(raw.get("price") or raw.get("prix"))
    n["year"] = parse_int(raw.get("year") or raw.get("annee"))
    n["mileage"] = parse_int(raw.get("mileage") or raw.get("km"))
    n["vin"] = raw.get("vin")
    n["lat"] = raw.get("lat")
    n["lon"] = raw.get("lon")
    n["images"] = raw.get("images") or []
    n["created_at"] = datetime.utcnow()
    n["id"] = f"{n['source']}::{n['source_id']}" if n["source"] and n["source_id"] else None
    return n

# === DEDUPLICATION SIMPLE ===
def find_duplicate(session, data: Dict[str, Any]) -> Optional[Any]:
    """Recherche simple d’un doublon basé sur vin ou (make, model, year, prix proche)."""
    vin = data.get("vin")
    if vin:
        existing = session.query(Vehicle).filter(Vehicle.vin == vin).first()
        if existing:
            return existing

    q = session.query(Vehicle).filter(
        Vehicle.make == data.get("make"),
        Vehicle.model == data.get("model"),
        Vehicle.year == data.get("year")
    ).all()

    for v in q:
        if abs((v.price or 0) - (data.get("price") or 0)) < 1000:
            return v
    return None

# === INGESTION ===
def process_listing(raw: Dict[str, Any]):
    session = SessionLocal()
    try:
        data = normalize(raw)
        existing = find_duplicate(session, data)

        if existing:
            for key, val in data.items():
                if val and getattr(existing, key, None) is None:
                    setattr(existing, key, val)
            session.add(existing)
            obj = existing
            print(f"🟡 Mise à jour : {obj.title}")
        else:
            obj = Vehicle(**data)
            session.add(obj)
            print(f"🟢 Nouveau véhicule ajouté : {obj.title}")

        session.commit()

        # Indexation ES
        if es.ping():
            es.index(index=ES_INDEX, id=obj.id, document={
                "title": obj.title,
                "make": obj.make,
                "model": obj.model,
                "price": obj.price,
                "year": obj.year,
                "mileage": obj.mileage,
                "vin": obj.vin,
                "images": obj.images,
            })
        else:
            print("⚠️ Elasticsearch non joignable")

    except SQLAlchemyError as e:
        session.rollback()
        print("Erreur SQL :", e)
    except Exception as e:
        print("Erreur générale :", e)
        traceback.print_exc()
    finally:
        session.close()

# === REDIS WORKER LOOP ===
def run_worker():
    print(f"🚀 Worker connecté à Redis: {REDIS_URL}")
    print(f"📦 Écoute la file : {REDIS_QUEUE_KEY}")
    while True:
        try:
            item = redis_client.brpop(REDIS_QUEUE_KEY, timeout=5)
            if not item:
                continue
            _, data = item
            try:
                raw = json.loads(data)
                process_listing(raw)
            except Exception:
                print("❌ Erreur JSON ou traitement :", data)
        except KeyboardInterrupt:
            print("🛑 Arrêt du worker.")
            break

# === MAIN ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-worker", action="store_true", help="Lancer le worker Redis")
    parser.add_argument("--process-file", type=str, help="Traiter un fichier JSON local")
    parser.add_argument("--test-single", action="store_true", help="Tester avec une annonce factice")
    args = parser.parse_args()

    if args.run_worker:
        run_worker()
    elif args.process_file:
        with open(args.process_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            process_listing(d)
    elif args.test_single:
        sample = {
            "source": "leboncoin",
            "id": "ABC123",
            "title": "Peugeot 208 2016 50 000 km 9000 €",
            "make": "Peugeot",
            "model": "208",
            "year": 2016,
            "mileage": 50000,
            "price": 9000,
            "vin": "VF3ABC123",
        }
        process_listing(sample)
    else:
        print("👉 Utilise --run-worker ou --process-file ou --test-single")


# === PROMETHEUS METRICS ===
try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    print("⚠️ prometheus_client non installé. Installer avec: pip install prometheus-client")
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = None