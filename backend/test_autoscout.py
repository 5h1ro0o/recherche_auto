#!/usr/bin/env python3
"""Script de test pour le scraper AutoScout24"""

import sys
import logging
from scrapers.autoscoot_scraper import AutoScout24Scraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_autoscout24_basic():
    """Test basique du scraper AutoScout24"""
    logger.info("🧪 Test AutoScout24 - Recherche basique")

    scraper = AutoScout24Scraper()

    # Test avec recherche simple (1 page seulement)
    results = scraper.scrape({
        'max_pages': 1
    })

    logger.info(f"📊 Résultats: {len(results)} annonces")

    if results:
        logger.info("✅ Test réussi!")
        logger.info(f"Exemple d'annonce: {results[0]}")
        return True
    else:
        logger.error("❌ Test échoué: aucune annonce trouvée")
        return False

def test_autoscout24_with_filters():
    """Test avec filtres"""
    logger.info("🧪 Test AutoScout24 - Avec filtres")

    scraper = AutoScout24Scraper()

    # Test avec filtres
    results = scraper.scrape({
        'max_pages': 1,
        'make': 'volkswagen',
        'model': 'golf',
        'max_price': 25000
    })

    logger.info(f"📊 Résultats filtrés: {len(results)} annonces")

    if results:
        logger.info("✅ Test avec filtres réussi!")
        return True
    else:
        logger.warning("⚠️ Aucune annonce avec les filtres")
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("TEST AUTOSCOUT24 SCRAPER")
    logger.info("=" * 60)

    # Test 1: Recherche basique
    success1 = test_autoscout24_basic()

    print()
    logger.info("-" * 60)
    print()

    # Test 2: Avec filtres
    success2 = test_autoscout24_with_filters()

    print()
    logger.info("=" * 60)

    if success1:
        logger.info("✅ TOUS LES TESTS SONT PASSÉS")
        sys.exit(0)
    else:
        logger.error("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)
