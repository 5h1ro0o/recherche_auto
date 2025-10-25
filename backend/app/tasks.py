from app.celery_app import app
from scrapers.leboncoin_scraper import LeBonCoinScraper
from scrapers.lacentrale_scraper import LaCentraleScraper
from scrapers.autoscoot_scraper import AutoScout24Scraper
import os
import redis
import json
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@app.task
def scrape_leboncoin():
    """Tâche Celery pour LeBonCoin"""
    logger.info("🔵 Démarrage scraping LeBonCoin")
    
    scraper = LeBonCoinScraper()
    results = scraper.scrape({
        'query': 'voiture',
        'max_pages': 5
    })
    
    # Push vers Redis queue pour le worker
    for result in results:
        redis_client.lpush('scraper_queue', json.dumps(result))
    
    logger.info(f"✅ LeBonCoin: {len(results)} annonces ajoutées à la queue")
    return len(results)

@app.task
def scrape_lacentrale():
    """Tâche Celery pour LaCentrale"""
    logger.info("🟢 Démarrage scraping LaCentrale")
    
    scraper = LaCentraleScraper()
    results = scraper.scrape({
        'query': 'volkswagen:golf',
        'max_pages': 5
    })
    
    for result in results:
        redis_client.lpush('scraper_queue', json.dumps(result))
    
    logger.info(f"✅ LaCentrale: {len(results)} annonces")
    return len(results)

@app.task
def scrape_autoscout():
    """Tâche Celery pour AutoScout24"""
    logger.info("🔴 Démarrage scraping AutoScout24")
    
    scraper = AutoScout24Scraper()
    results = scraper.scrape({
        'max_pages': 3
    })
    
    for result in results:
        redis_client.lpush('scraper_queue', json.dumps(result))
    
    logger.info(f"✅ AutoScout24: {len(results)} annonces")
    return len(results)