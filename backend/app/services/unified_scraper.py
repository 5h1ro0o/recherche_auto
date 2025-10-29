# backend/app/services/unified_scraper.py
"""
Service unifié de scraping pour tous les sites
Gère le scraping en parallèle et l'agrégation des résultats
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Import des scrapers
try:
    from scrapers import LeBonCoinScraper, LaCentraleScraper, AutoScout24Scraper
    SCRAPERS_AVAILABLE = True
except ImportError:
    SCRAPERS_AVAILABLE = False
    logging.warning("⚠️ Les modules de scraping ne sont pas disponibles")

from sqlalchemy.orm import Session
from app.models import Vehicle
from app.db import SessionLocal

logger = logging.getLogger(__name__)


class UnifiedScraperService:
    """Service unifié pour scraper tous les sites d'annonces"""

    def __init__(self):
        self.scrapers = []
        if SCRAPERS_AVAILABLE:
            self.scrapers = [
                ('leboncoin', LeBonCoinScraper),
                ('lacentrale', LaCentraleScraper),
                ('autoscout24', AutoScout24Scraper),
            ]

    def scrape_all_sources(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        max_pages: int = 2,
        save_to_db: bool = True,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Scrape tous les sites en parallèle

        Args:
            query: Terme de recherche (ex: "peugeot 308")
            filters: Filtres optionnels (prix, année, etc.)
            max_pages: Nombre maximum de pages à scraper par site
            save_to_db: Sauvegarder dans la base de données
            timeout: Timeout en secondes pour chaque scraper

        Returns:
            {
                'total': int,
                'results': List[Dict],
                'sources': {
                    'leboncoin': {'count': int, 'success': bool},
                    'lacentrale': {'count': int, 'success': bool},
                    'autoscout24': {'count': int, 'success': bool}
                }
            }
        """

        if not SCRAPERS_AVAILABLE:
            logger.error("❌ Les scrapers ne sont pas disponibles")
            return {
                'total': 0,
                'results': [],
                'sources': {},
                'error': 'Scrapers non disponibles. Installez playwright et les dépendances.'
            }

        logger.info(f"🔍 Démarrage du scraping unifié pour: '{query}'")

        all_results = []
        sources_info = {}

        # Préparer les paramètres de recherche
        search_params = {
            'query': query,
            'max_pages': max_pages,
            'deep_scrape': False,  # Pour la vitesse
        }

        # Ajouter les filtres
        if filters:
            if 'price_max' in filters:
                search_params['max_price'] = filters['price_max']
            if 'year_min' in filters:
                search_params['min_year'] = filters['year_min']

        # Scraper en parallèle avec ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {}

            for source_name, ScraperClass in self.scrapers:
                future = executor.submit(
                    self._scrape_source,
                    source_name,
                    ScraperClass,
                    search_params,
                    timeout
                )
                future_to_source[future] = source_name

            # Collecter les résultats
            for future in as_completed(future_to_source, timeout=timeout + 10):
                source_name = future_to_source[future]
                try:
                    source_results = future.result()

                    if source_results['success']:
                        all_results.extend(source_results['results'])
                        sources_info[source_name] = {
                            'count': len(source_results['results']),
                            'success': True
                        }
                        logger.info(f"✅ {source_name}: {len(source_results['results'])} résultats")
                    else:
                        sources_info[source_name] = {
                            'count': 0,
                            'success': False,
                            'error': source_results.get('error', 'Erreur inconnue')
                        }
                        logger.warning(f"⚠️ {source_name}: Échec - {source_results.get('error')}")

                except Exception as e:
                    logger.error(f"❌ Erreur lors du scraping de {source_name}: {e}")
                    sources_info[source_name] = {
                        'count': 0,
                        'success': False,
                        'error': str(e)
                    }

        # Dédupliquer les résultats basés sur le titre et le prix
        unique_results = self._deduplicate_results(all_results)

        logger.info(f"📊 Total: {len(unique_results)} résultats uniques (avant dédoublonnage: {len(all_results)})")

        # Sauvegarder dans la DB si demandé
        if save_to_db and unique_results:
            saved_count = self._save_to_database(unique_results)
            logger.info(f"💾 {saved_count} véhicules sauvegardés dans la base de données")

        return {
            'total': len(unique_results),
            'results': unique_results,
            'sources': sources_info,
            'query': query,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _scrape_source(
        self,
        source_name: str,
        ScraperClass,
        search_params: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Scrape un site spécifique"""
        try:
            logger.info(f"🚀 Début scraping {source_name}")

            scraper = ScraperClass(use_proxy=False)
            results = scraper.scrape(search_params)

            # Normaliser les résultats
            normalized = [self._normalize_result(r, source_name) for r in results]

            return {
                'success': True,
                'results': normalized,
                'source': source_name
            }

        except Exception as e:
            logger.error(f"❌ Erreur scraping {source_name}: {e}")
            return {
                'success': False,
                'results': [],
                'source': source_name,
                'error': str(e)
            }

    def _normalize_result(self, raw_result: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalise un résultat de scraping au format unifié"""
        return {
            'id': raw_result.get('id', str(uuid.uuid4())),
            'title': raw_result.get('title', ''),
            'make': raw_result.get('make', ''),
            'model': raw_result.get('model', ''),
            'price': raw_result.get('price', 0),
            'year': raw_result.get('year'),
            'mileage': raw_result.get('mileage'),
            'fuel_type': raw_result.get('fuel_type'),
            'transmission': raw_result.get('transmission'),
            'description': raw_result.get('description', ''),
            'images': raw_result.get('images', []),
            'location_city': raw_result.get('location'),
            'source': source,
            'source_url': raw_result.get('url', ''),
            'created_at': datetime.utcnow().isoformat()
        }

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Déduplique les résultats basés sur le titre et le prix"""
        seen = set()
        unique = []

        for result in results:
            # Créer une clé unique basée sur le titre et le prix
            key = (
                result.get('title', '').lower().strip(),
                result.get('price', 0)
            )

            if key not in seen and key[0]:  # Ignorer les titres vides
                seen.add(key)
                unique.append(result)

        return unique

    def _save_to_database(self, results: List[Dict[str, Any]]) -> int:
        """Sauvegarde les résultats dans la base de données"""
        db = SessionLocal()
        saved_count = 0

        try:
            for result in results:
                # Vérifier si le véhicule existe déjà (basé sur source_url)
                existing = db.query(Vehicle).filter(
                    Vehicle.source_ids.contains({'url': result.get('source_url')})
                ).first()

                if existing:
                    continue  # Skip si déjà en base

                # Créer un nouveau véhicule
                vehicle = Vehicle(
                    id=str(uuid.uuid4()),
                    title=result.get('title'),
                    make=result.get('make'),
                    model=result.get('model'),
                    price=result.get('price'),
                    year=result.get('year'),
                    mileage=result.get('mileage'),
                    fuel_type=result.get('fuel_type'),
                    transmission=result.get('transmission'),
                    description=result.get('description'),
                    images=result.get('images'),
                    location_city=result.get('location_city'),
                    source_ids={
                        'source': result.get('source'),
                        'url': result.get('source_url')
                    }
                )

                db.add(vehicle)
                saved_count += 1

            db.commit()
            logger.info(f"💾 {saved_count} nouveaux véhicules sauvegardés")

        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde en DB: {e}")
            db.rollback()

        finally:
            db.close()

        return saved_count


# Instance globale
unified_scraper = UnifiedScraperService()
