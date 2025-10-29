# backend/scrapers/__init__.py
"""
Package scrapers pour l'extraction de données multi-plateformes
Version simplifiée et robuste
"""

from .base_scraper import BaseScraper

# Utiliser les versions simplifiées (plus robustes)
try:
    from .leboncoin_scraper_simple import LeBonCoinScraperSimple as LeBonCoinScraper
    from .lacentrale_scraper_simple import LaCentraleScraperSimple as LaCentraleScraper
    from .autoscout24_scraper_simple import AutoScout24ScraperSimple as AutoScout24Scraper
    SIMPLE_SCRAPERS = True
except ImportError:
    # Fallback vers les anciens scrapers si les nouveaux ne sont pas disponibles
    from .leboncoin_scraper import LeBonCoinScraper
    from .lacentrale_scraper import LaCentraleScraper
    from .autoscoot_scraper import AutoScout24Scraper
    SIMPLE_SCRAPERS = False

__all__ = [
    'BaseScraper',
    'LeBonCoinScraper',
    'LaCentraleScraper',
    'AutoScout24Scraper',
]

__version__ = '2.0.0-simple' if SIMPLE_SCRAPERS else '1.0.0'