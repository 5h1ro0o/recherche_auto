# backend/app/tasks.py - VERSION PRODUCTION AVEC MONITORING
import os
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.celery_app import app
from celery.utils.log import get_task_logger

# Import scrapers
from scrapers.leboncoin_scraper import LeBonCoinScraper
from scrapers.lacentrale_scraper import LaCentraleScraper
from scrapers.autoscoot_scraper import AutoScout24Scraper

# Import services
try:
    import redis
    from app.db import SessionLocal
    from app.models import Vehicle, SearchHistory, Alert
    from sqlalchemy import func
    REDIS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    REDIS_AVAILABLE = False

logger = get_task_logger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_AVAILABLE else None

# ============ MÉTRIQUES & MONITORING ============

def log_scraping_metrics(source: str, success: int, failed: int, duration: float):
    """Log des métriques de scraping dans Redis"""
    if not redis_client:
        return
    
    try:
        timestamp = datetime.utcnow().isoformat()
        metrics_key = f"metrics:scraping:{source}:{datetime.utcnow().strftime('%Y%m%d')}"
        
        redis_client.hincrby(metrics_key, 'success', success)
        redis_client.hincrby(metrics_key, 'failed', failed)
        redis_client.hincrbyfloat(metrics_key, 'duration', duration)
        redis_client.hincrby(metrics_key, 'runs', 1)
        redis_client.expire(metrics_key, 86400 * 30)  # Garder 30 jours
        
        # Dernière exécution
        redis_client.set(f"last_run:{source}", timestamp, ex=86400 * 7)
        
    except Exception as e:
        logger.warning(f"Erreur log metrics: {e}")


def check_scraper_health(source: str) -> Dict[str, Any]:
    """Vérifie la santé d'un scraper"""
    if not redis_client:
        return {'healthy': False, 'reason': 'Redis unavailable'}
    
    try:
        # Dernière exécution
        last_run = redis_client.get(f"last_run:{source}")
        
        if not last_run:
            return {'healthy': False, 'reason': 'Never run'}
        
        last_run_dt = datetime.fromisoformat(last_run)
        hours_since = (datetime.utcnow() - last_run_dt).total_seconds() / 3600
        
        # Alerte si pas exécuté depuis > 24h
        if hours_since > 24:
            return {
                'healthy': False,
                'reason': f'Not run for {hours_since:.1f}h',
                'last_run': last_run
            }
        
        # Vérifier taux d'échec
        today = datetime.utcnow().strftime('%Y%m%d')
        metrics_key = f"metrics:scraping:{source}:{today}"
        
        success = int(redis_client.hget(metrics_key, 'success') or 0)
        failed = int(redis_client.hget(metrics_key, 'failed') or 0)
        
        if success + failed > 0:
            failure_rate = failed / (success + failed)
            
            if failure_rate > 0.5:  # > 50% d'échec
                return {
                    'healthy': False,
                    'reason': f'High failure rate: {failure_rate:.1%}',
                    'success': success,
                    'failed': failed
                }
        
        return {
            'healthy': True,
            'last_run': last_run,
            'success': success,
            'failed': failed
        }
        
    except Exception as e:
        logger.error(f"Health check error for {source}: {e}")
        return {'healthy': False, 'reason': str(e)}


# ============ TÂCHES SCRAPING ============

@app.task(bind=True, name='app.tasks.scrape_leboncoin')
def scrape_leboncoin(self, query: str = 'voiture', max_pages: int = 5, 
                     deep_scrape: bool = False) -> Dict[str, Any]:
    """
    Tâche de scraping LeBonCoin avec retry et monitoring
    """
    start_time = datetime.utcnow()
    source = 'leboncoin'
    
    logger.info(f"🔵 Démarrage scraping {source}: query='{query}', pages={max_pages}, deep={deep_scrape}")
    
    try:
        scraper = LeBonCoinScraper()
        
        results = scraper.scrape({
            'query': query,
            'max_pages': max_pages,
            'deep_scrape': deep_scrape
        })
        
        success_count = 0
        failed_count = 0
        
        # Push vers Redis queue pour le worker
        for result in results:
            try:
                redis_client.lpush('scraper_queue', json.dumps(result))
                success_count += 1
            except Exception as e:
                logger.error(f"Erreur push Redis: {e}")
                failed_count += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Log metrics
        log_scraping_metrics(source, success_count, failed_count, duration)
        
        result_summary = {
            'source': source,
            'count': len(results),
            'success': success_count,
            'failed': failed_count,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ {source}: {success_count} annonces ajoutées en {duration:.1f}s")
        
        return result_summary
        
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_scraping_metrics(source, 0, 1, duration)
        
        logger.error(f"❌ Erreur scraping {source}: {e}")
        logger.error(traceback.format_exc())
        
        # Retry avec backoff exponentiel
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@app.task(bind=True, name='app.tasks.scrape_lacentrale')
def scrape_lacentrale(self, queries: List[str] = None, max_pages: int = 10) -> Dict[str, Any]:
    """Tâche de scraping LaCentrale"""
    start_time = datetime.utcnow()
    source = 'lacentrale'
    
    if queries is None:
        queries = ['volkswagen:golf']
    
    logger.info(f"🟢 Démarrage scraping {source}: queries={queries}, pages={max_pages}")
    
    try:
        scraper = LaCentraleScraper()
        
        all_results = []
        for query in queries:
            results = scraper.scrape({
                'query': query,
                'max_pages': max_pages
            })
            all_results.extend(results)
            logger.info(f"  Query '{query}': {len(results)} résultats")
        
        success_count = 0
        failed_count = 0
        
        for result in all_results:
            try:
                redis_client.lpush('scraper_queue', json.dumps(result))
                success_count += 1
            except Exception as e:
                logger.error(f"Erreur push Redis: {e}")
                failed_count += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_scraping_metrics(source, success_count, failed_count, duration)
        
        logger.info(f"✅ {source}: {success_count} annonces ajoutées en {duration:.1f}s")
        
        return {
            'source': source,
            'count': len(all_results),
            'success': success_count,
            'failed': failed_count,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_scraping_metrics(source, 0, 1, duration)
        
        logger.error(f"❌ Erreur scraping {source}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@app.task(bind=True, name='app.tasks.scrape_autoscout')
def scrape_autoscout(self, max_pages: int = 5) -> Dict[str, Any]:
    """Tâche de scraping AutoScout24"""
    start_time = datetime.utcnow()
    source = 'autoscout24'
    
    logger.info(f"🔴 Démarrage scraping {source}: pages={max_pages}")
    
    try:
        scraper = AutoScout24Scraper()
        
        results = scraper.scrape({
            'max_pages': max_pages
        })
        
        success_count = 0
        failed_count = 0
        
        for result in results:
            try:
                redis_client.lpush('scraper_queue', json.dumps(result))
                success_count += 1
            except Exception as e:
                logger.error(f"Erreur push Redis: {e}")
                failed_count += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_scraping_metrics(source, success_count, failed_count, duration)
        
        logger.info(f"✅ {source}: {success_count} annonces en {duration:.1f}s")
        
        return {
            'source': source,
            'count': len(results),
            'success': success_count,
            'failed': failed_count,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_scraping_metrics(source, 0, 1, duration)
        
        logger.error(f"❌ Erreur scraping {source}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


# ============ TÂCHES MAINTENANCE ============

@app.task(name='app.tasks.cleanup_old_listings')
def cleanup_old_listings(days: int = 90):
    """Supprime les annonces de plus de X jours"""
    logger.info(f"🗑️ Nettoyage des annonces > {days} jours")
    
    try:
        db = SessionLocal()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Compter avant
        old_count = db.query(Vehicle).filter(
            Vehicle.created_at < cutoff_date
        ).count()
        
        # Supprimer
        deleted = db.query(Vehicle).filter(
            Vehicle.created_at < cutoff_date
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"✅ Supprimé {deleted} annonces anciennes")
        
        return {'deleted': deleted, 'cutoff_date': cutoff_date.isoformat()}
        
    except Exception as e:
        logger.error(f"❌ Erreur cleanup: {e}")
        return {'error': str(e)}


@app.task(name='app.tasks.update_elasticsearch_index')
def update_elasticsearch_index():
    """Réindexe les véhicules récents dans Elasticsearch"""
    logger.info("🔍 Mise à jour index Elasticsearch")
    
    try:
        from app.elasticsearch_client import es
        from app.config import settings
        
        db = SessionLocal()
        
        # Réindexer les véhicules des dernières 24h
        since = datetime.utcnow() - timedelta(hours=24)
        
        vehicles = db.query(Vehicle).filter(
            Vehicle.updated_at >= since
        ).all()
        
        indexed = 0
        for vehicle in vehicles:
            try:
                es.index(
                    index=settings.ES_INDEX,
                    id=vehicle.id,
                    document={
                        'title': vehicle.title,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'price': vehicle.price,
                        'year': vehicle.year,
                        'mileage': vehicle.mileage,
                        'fuel_type': vehicle.fuel_type,
                        'transmission': vehicle.transmission,
                        'location_city': vehicle.location_city,
                    }
                )
                indexed += 1
            except Exception as e:
                logger.warning(f"Erreur indexation {vehicle.id}: {e}")
        
        db.close()
        
        logger.info(f"✅ Indexé {indexed} véhicules")
        
        return {'indexed': indexed}
        
    except Exception as e:
        logger.error(f"❌ Erreur indexation ES: {e}")
        return {'error': str(e)}


@app.task(name='app.tasks.send_alert_notifications')
def send_alert_notifications():
    """Envoie les notifications d'alertes aux utilisateurs"""
    logger.info("📧 Envoi notifications alertes")
    
    try:
        db = SessionLocal()
        
        # Récupérer alertes actives
        alerts = db.query(Alert).filter(
            Alert.is_active == True
        ).all()
        
        notifications_sent = 0
        
        for alert in alerts:
            # Vérifier fréquence
            if alert.last_sent_at:
                hours_since = (datetime.utcnow() - alert.last_sent_at).total_seconds() / 3600
                
                if alert.frequency == 'daily' and hours_since < 24:
                    continue
                elif alert.frequency == 'weekly' and hours_since < 168:
                    continue
            
            # Rechercher nouveaux véhicules correspondants
            # TODO: Implémenter logique de recherche selon criteria
            
            # Marquer comme envoyé
            alert.last_sent_at = datetime.utcnow()
            notifications_sent += 1
        
        db.commit()
        db.close()
        
        logger.info(f"✅ {notifications_sent} notifications envoyées")
        
        return {'sent': notifications_sent}
        
    except Exception as e:
        logger.error(f"❌ Erreur notifications: {e}")
        return {'error': str(e)}


@app.task(name='app.tasks.generate_stats_report')
def generate_stats_report():
    """Génère un rapport statistique quotidien"""
    logger.info("📊 Génération rapport statistiques")
    
    try:
        db = SessionLocal()
        
        # Stats véhicules
        total_vehicles = db.query(Vehicle).count()
        today_vehicles = db.query(Vehicle).filter(
            Vehicle.created_at >= datetime.utcnow().date()
        ).count()
        
        # Stats par source
        sources_stats = db.query(
            Vehicle.source_ids,
            func.count(Vehicle.id)
        ).group_by(Vehicle.source_ids).all()
        
        # Prix moyen
        avg_price = db.query(func.avg(Vehicle.price)).filter(
            Vehicle.price.isnot(None)
        ).scalar()
        
        db.close()
        
        report = {
            'date': datetime.utcnow().isoformat(),
            'total_vehicles': total_vehicles,
            'today_vehicles': today_vehicles,
            'avg_price': float(avg_price) if avg_price else 0,
            'sources': dict(sources_stats) if sources_stats else {}
        }
        
        # Sauvegarder dans Redis
        redis_client.set(
            f"stats:daily:{datetime.utcnow().strftime('%Y%m%d')}",
            json.dumps(report),
            ex=86400 * 90  # Garder 90 jours
        )
        
        logger.info(f"✅ Rapport généré: {total_vehicles} véhicules")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Erreur génération rapport: {e}")
        return {'error': str(e)}


@app.task(name='app.tasks.health_check_scrapers')
def health_check_scrapers():
    """Health check périodique des scrapers"""
    
    sources = ['leboncoin', 'lacentrale', 'autoscout24']
    
    health_report = {
        'timestamp': datetime.utcnow().isoformat(),
        'sources': {}
    }
    
    all_healthy = True
    
    for source in sources:
        health = check_scraper_health(source)
        health_report['sources'][source] = health
        
        if not health.get('healthy'):
            all_healthy = False
            logger.warning(f"⚠️ {source} unhealthy: {health.get('reason')}")
    
    health_report['overall_healthy'] = all_healthy
    
    # Sauvegarder dans Redis
    redis_client.set(
        'health:scrapers',
        json.dumps(health_report),
        ex=600  # 10 minutes
    )
    
    if all_healthy:
        logger.info("✅ Tous les scrapers sont opérationnels")
    else:
        logger.warning("⚠️ Certains scrapers ont des problèmes")
    
    return health_report


# ============ TÂCHES DE TEST ============

@app.task(name='app.tasks.test_task')
def test_task(message: str = "Hello from Celery!"):
    """Tâche de test simple"""
    logger.info(f"🧪 Test task: {message}")
    return {'message': message, 'timestamp': datetime.utcnow().isoformat()}