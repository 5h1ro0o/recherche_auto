# backend/scrapers/__init__.py
"""
Package scrapers pour l'extraction de données multi-plateformes
"""

from .base_scraper import BaseScraper
from .leboncoin_scraper import LeBonCoinScraper
from .lacentrale_scraper import LaCentraleScraper
from .autoscoot_scraper import AutoScout24Scraper

__all__ = [
    'BaseScraper',
    'LeBonCoinScraper',
    'LaCentraleScraper',
    'AutoScout24Scraper',
]

__version__ = '1.0.0'