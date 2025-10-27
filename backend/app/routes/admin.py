# backend/app/routes/admin.py
import logging
import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, Any

from app.db import SessionLocal
from app.models import User, Vehicle, UserRole
from app.dependencies import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

# Client Redis
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Erreur connexion Redis: {e}")
    redis_client = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Vérifier que l'utilisateur est ADMIN"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis"
        )
    return current_user

# ============ STATISTIQUES GÉNÉRALES ============

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Statistiques globales pour le dashboard admin"""
    
    # Total véhicules
    total_vehicles = db.query(Vehicle).count()
    
    # Par source
    sources_stats = {}
    for source in ['leboncoin', 'lacentrale', 'autoscout24']:
        count = db.query(Vehicle).filter(
            func.json_extract_path_text(Vehicle.source_ids, source).isnot(None)
        ).count()
        sources_stats[source] = count
    
    # Statistiques 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    new_vehicles_24h = db.query(Vehicle).filter(
        Vehicle.created_at >= yesterday
    ).count()
    
    updated_vehicles_24h = db.query(Vehicle).filter(
        Vehicle.updated_at >= yesterday,
        Vehicle.created_at < yesterday
    ).count()
    
    # Déduplication (simulé - à adapter selon votre logique)
    # Compter les véhicules avec même VIN ou similaires
    duplicates_count = db.query(Vehicle).filter(
        Vehicle.vin.isnot(None)
    ).group_by(Vehicle.vin).having(func.count(Vehicle.id) > 1).count()
    
    deduplication_rate = (duplicates_count / total_vehicles * 100) if total_vehicles > 0 else 0
    
    # Véhicules par jour (7 derniers jours)
    by_day = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=6-i)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        count = db.query(Vehicle).filter(
            Vehicle.created_at >= start_date,
            Vehicle.created_at < end_date
        ).count()
        
        by_day.append({
            "date": start_date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "total_vehicles": total_vehicles,
        "sources": sources_stats,
        "deduplication": {
            "total_processed": total_vehicles,
            "duplicates_found": duplicates_count,
            "rate": round(deduplication_rate, 1)
        },
        "last_24h": {
            "new_vehicles": new_vehicles_24h,
            "updated_vehicles": updated_vehicles_24h,
            "errors": 0  # À implémenter avec une table de logs
        },
        "by_day": by_day
    }

# ============ WORKER HEALTH ============

@router.get("/worker/health")
async def get_worker_health(
    current_user: User = Depends(require_admin)
):
    """État de santé du worker"""
    
    try:
        # Tester Redis
        redis_ok = redis_client.ping() if redis_client else False
        queue_size = redis_client.llen('scraper_queue') if redis_client else 0
    except Exception as e:
        logger.error(f"Erreur Redis: {e}")
        redis_ok = False
        queue_size = 0
    
    # Tester Elasticsearch
    try:
        from app.elasticsearch_client import es
        es_ok = es.ping()
    except Exception:
        es_ok = False
    
    # Tester PostgreSQL
    try:
        from app.db import engine
        conn = engine.connect()
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False
    
    # Statistiques worker (à récupérer depuis l'endpoint health du worker)
    # Pour l'instant, valeurs par défaut
    return {
        "status": "healthy" if (redis_ok and es_ok and db_ok) else "unhealthy",
        "uptime_seconds": 86400,  # À récupérer du worker
        "queue_size": queue_size,
        "stats": {
            "total_processed": 0,  # À récupérer du worker
            "total_errors": 0,
            "total_duplicates": 0
        },
        "connections": {
            "redis": redis_ok,
            "elasticsearch": es_ok,
            "database": db_ok
        }
    }

# ============ LOGS SCRAPERS ============

@router.get("/scrapers/logs")
async def get_scraper_logs(
    current_user: User = Depends(require_admin),
    limit: int = 20
):
    """Logs des dernières exécutions des scrapers"""
    
    # TODO: Implémenter une table ScraperLog pour stocker l'historique
    # Pour l'instant, retourner des données mockées
    
    mock_logs = [
        {
            "id": 1,
            "timestamp": datetime.utcnow() - timedelta(minutes=30),
            "source": "leboncoin",
            "status": "success",
            "message": "124 véhicules scrapés avec succès",
            "duration": "3.2s",
            "vehicles_found": 124,
            "vehicles_new": 15,
            "vehicles_updated": 109
        },
        {
            "id": 2,
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "source": "lacentrale",
            "status": "warning",
            "message": "Pagination limitée à 5 pages",
            "duration": "4.1s",
            "vehicles_found": 89,
            "vehicles_new": 8,
            "vehicles_updated": 81
        },
        {
            "id": 3,
            "timestamp": datetime.utcnow() - timedelta(hours=6),
            "source": "autoscout24",
            "status": "error",
            "message": "Timeout après 30s - connexion instable",
            "duration": "30.0s",
            "vehicles_found": 0,
            "vehicles_new": 0,
            "vehicles_updated": 0
        }
    ]
    
    return mock_logs[:limit]

# ============ ACTIONS SCRAPERS ============

@router.post("/scrapers/{source}/trigger")
async def trigger_scraper(
    source: str,
    current_user: User = Depends(require_admin)
):
    """Lancer manuellement un scraper"""
    
    valid_sources = ['leboncoin', 'lacentrale', 'autoscout24']
    if source not in valid_sources:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source invalide. Valeurs acceptées: {valid_sources}"
        )
    
    try:
        # Importer les tasks Celery
        if source == 'leboncoin':
            from app.tasks import scrape_leboncoin
            task = scrape_leboncoin.apply_async()
        elif source == 'lacentrale':
            from app.tasks import scrape_lacentrale
            task = scrape_lacentrale.apply_async()
        elif source == 'autoscout24':
            from app.tasks import scrape_autoscout
            task = scrape_autoscout.apply_async()
        
        logger.info(f"Scraper {source} lancé manuellement par {current_user.email}")
        
        return {
            "message": f"Scraper {source} lancé avec succès",
            "task_id": task.id,
            "source": source
        }
        
    except ImportError:
        # Si Celery n'est pas disponible
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Celery n'est pas disponible. Le scraping automatique est désactivé."
        )
    except Exception as e:
        logger.error(f"Erreur lancement scraper {source}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du lancement: {str(e)}"
        )

# ============ GESTION QUEUE REDIS ============

@router.post("/queue/clear")
async def clear_redis_queue(
    current_user: User = Depends(require_admin)
):
    """Vider la queue Redis"""
    
    if not redis_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis non disponible"
        )
    
    try:
        queue_size_before = redis_client.llen('scraper_queue')
        redis_client.delete('scraper_queue')
        
        logger.warning(f"Queue Redis vidée par {current_user.email} ({queue_size_before} éléments)")
        
        return {
            "message": "Queue vidée avec succès",
            "items_deleted": queue_size_before
        }
        
    except Exception as e:
        logger.error(f"Erreur vidage queue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.get("/queue/status")
async def get_queue_status(
    current_user: User = Depends(require_admin)
):
    """Status de la queue Redis"""
    
    if not redis_client:
        return {
            "available": False,
            "size": 0,
            "message": "Redis non disponible"
        }
    
    try:
        size = redis_client.llen('scraper_queue')
        
        # Peek les 5 premiers éléments sans les retirer
        sample = []
        for i in range(min(5, size)):
            item = redis_client.lindex('scraper_queue', i)
            if item:
                import json
                try:
                    sample.append(json.loads(item))
                except:
                    sample.append(item)
        
        return {
            "available": True,
            "size": size,
            "sample": sample,
            "message": f"{size} éléments en attente"
        }
        
    except Exception as e:
        logger.error(f"Erreur status queue: {e}")
        return {
            "available": False,
            "size": 0,
            "error": str(e)
        }

# ============ GESTION UTILISATEURS ============

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 50,
    role: str = None
):
    """Liste tous les utilisateurs (admin)"""
    
    query = db.query(User)
    
    if role:
        try:
            user_role = UserRole[role.upper()]
            query = query.filter(User.role == user_role)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rôle invalide: {role}"
            )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "users": users
    }

@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Changer le rôle d'un utilisateur"""
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    try:
        user_role = UserRole[new_role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rôle invalide: {new_role}"
        )
    
    old_role = user.role
    user.role = user_role
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Rôle de {user.email} changé de {old_role} à {user_role} par {current_user.email}")
    
    return {
        "message": "Rôle mis à jour",
        "user_id": user_id,
        "old_role": old_role.value,
        "new_role": user.role.value
    }

@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activer/désactiver un compte utilisateur"""
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver votre propre compte"
        )
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    action = "activé" if user.is_active else "désactivé"
    logger.info(f"Compte {user.email} {action} par {current_user.email}")
    
    return {
        "message": f"Compte {action}",
        "user_id": user_id,
        "is_active": user.is_active
    }

# ============ STATISTIQUES AVANCÉES ============

@router.get("/stats/sources-detail")
async def get_sources_detail(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Statistiques détaillées par source"""
    
    sources_detail = {}
    
    for source in ['leboncoin', 'lacentrale', 'autoscout24']:
        # Véhicules de cette source
        total = db.query(Vehicle).filter(
            func.json_extract_path_text(Vehicle.source_ids, source).isnot(None)
        ).count()
        
        # Ajoutés dans les 7 derniers jours
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent = db.query(Vehicle).filter(
            func.json_extract_path_text(Vehicle.source_ids, source).isnot(None),
            Vehicle.created_at >= week_ago
        ).count()
        
        # Prix moyen
        avg_price = db.query(func.avg(Vehicle.price)).filter(
            func.json_extract_path_text(Vehicle.source_ids, source).isnot(None),
            Vehicle.price.isnot(None)
        ).scalar()
        
        sources_detail[source] = {
            "total": total,
            "recent_7d": recent,
            "avg_price": round(avg_price, 2) if avg_price else None
        }
    
    return sources_detail

@router.get("/stats/users")
async def get_users_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Statistiques utilisateurs"""
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Par rôle
    by_role = {}
    for role in UserRole:
        count = db.query(User).filter(User.role == role).count()
        by_role[role.value] = count
    
    # Nouveaux utilisateurs (7 derniers jours)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_7d = db.query(User).filter(User.created_at >= week_ago).count()
    
    return {
        "total": total_users,
        "active": active_users,
        "inactive": total_users - active_users,
        "by_role": by_role,
        "new_7d": new_users_7d
    }

# ============ MAINTENANCE ============

@router.post("/maintenance/reindex-elasticsearch")
async def reindex_elasticsearch(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Réindexer tous les véhicules dans Elasticsearch"""
    
    try:
        from app.elasticsearch_client import es
        from app.config import settings
        
        # Compter les véhicules
        total_vehicles = db.query(Vehicle).count()
        
        # TODO: Implémenter la logique de réindexation en batch
        # Pour éviter de surcharger, traiter par lots de 100
        
        logger.info(f"Réindexation ES lancée par {current_user.email} ({total_vehicles} véhicules)")
        
        return {
            "message": "Réindexation lancée",
            "total_vehicles": total_vehicles,
            "status": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Erreur réindexation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.post("/maintenance/cleanup-old-vehicles")
async def cleanup_old_vehicles(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    days: int = 90
):
    """Supprimer les véhicules de plus de X jours"""
    
    if days < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum 30 jours requis pour la sécurité"
        )
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Compter d'abord
    count = db.query(Vehicle).filter(Vehicle.created_at < cutoff_date).count()
    
    if not confirm:
        return {
            "message": f"{count} véhicules seraient supprimés",
            "cutoff_date": cutoff_date.isoformat(),
            "status": "preview"
        }
    
    # Supprimer
    deleted = db.query(Vehicle).filter(Vehicle.created_at < cutoff_date).delete()
    db.commit()
    
    logger.warning(f"{deleted} véhicules supprimés par {current_user.email} (> {days} jours)")
    
    return {
        "message": f"{deleted} véhicules supprimés",
        "cutoff_date": cutoff_date.isoformat(),
        "status": "completed"
    }