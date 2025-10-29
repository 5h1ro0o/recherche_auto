# backend/app/services/search_with_scraping.py
"""
Service de recherche hybride : DB locale + Scraping en temps réel
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.unified_scraper import unified_scraper
from app.models import Vehicle
from app.db import SessionLocal

logger = logging.getLogger(__name__)


class HybridSearchService:
    """Service de recherche hybride combinant DB locale et scraping"""

    @staticmethod
    def search(
        q: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20,
        enable_scraping: bool = True,
        scraping_mode: str = 'auto'  # 'auto', 'always', 'never', 'db_first'
    ) -> Dict[str, Any]:
        """
        Recherche hybride : DB + Scraping

        Args:
            q: Terme de recherche
            filters: Filtres de recherche
            page: Numéro de page
            size: Taille de la page
            enable_scraping: Activer le scraping
            scraping_mode:
                - 'auto': Scraper uniquement si peu de résultats en DB
                - 'always': Toujours scraper
                - 'never': Jamais scraper (DB uniquement)
                - 'db_first': DB d'abord, puis scraping si nécessaire

        Returns:
            {
                'total': int,
                'results': List[Dict],
                'page': int,
                'size': int,
                'from_db': int,
                'from_scraping': int,
                'sources': Dict  # Si scraping activé
            }
        """

        logger.info(f"🔍 Recherche hybride: q='{q}', mode={scraping_mode}, page={page}")

        db_results = []
        scraping_results = []
        sources_info = {}

        # Recherche dans la DB locale
        if scraping_mode in ['auto', 'never', 'db_first']:
            db_results = HybridSearchService._search_in_database(q, filters, page, size)
            logger.info(f"📚 DB locale: {len(db_results)} résultats")

        # Déterminer si on doit scraper
        should_scrape = False

        if scraping_mode == 'always':
            should_scrape = True
        elif scraping_mode == 'never':
            should_scrape = False
        elif scraping_mode == 'auto':
            # Scraper si moins de 5 résultats en DB
            should_scrape = len(db_results) < 5
        elif scraping_mode == 'db_first':
            # Scraper uniquement si aucun résultat en DB
            should_scrape = len(db_results) == 0

        # Scraping si nécessaire
        if enable_scraping and should_scrape and q:
            logger.info(f"🕷️ Démarrage du scraping (mode: {scraping_mode})")

            scraping_response = unified_scraper.scrape_all_sources(
                query=q,
                filters=filters or {},
                max_pages=2,
                save_to_db=True,  # Sauvegarder pour futures recherches
                timeout=45
            )

            scraping_results = scraping_response.get('results', [])
            sources_info = scraping_response.get('sources', {})

            logger.info(f"🕷️ Scraping terminé: {len(scraping_results)} résultats")

        # Combiner et dédupliquer les résultats
        all_results = HybridSearchService._merge_results(db_results, scraping_results)

        # Pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_results = all_results[start_idx:end_idx]

        return {
            'total': len(all_results),
            'results': paginated_results,
            'page': page,
            'size': size,
            'from_db': len(db_results),
            'from_scraping': len(scraping_results),
            'scraping_enabled': enable_scraping and should_scrape,
            'sources': sources_info if sources_info else None
        }

    @staticmethod
    def _search_in_database(
        q: Optional[str],
        filters: Optional[Dict[str, Any]],
        page: int,
        size: int
    ) -> List[Dict[str, Any]]:
        """Recherche dans la base de données PostgreSQL"""
        db = SessionLocal()
        results = []

        try:
            query = db.query(Vehicle)

            # Filtrage par texte
            if q:
                search_term = f"%{q.lower()}%"
                query = query.filter(
                    (Vehicle.title.ilike(search_term)) |
                    (Vehicle.make.ilike(search_term)) |
                    (Vehicle.model.ilike(search_term)) |
                    (Vehicle.description.ilike(search_term))
                )

            # Filtres additionnels
            if filters:
                if 'price_min' in filters:
                    query = query.filter(Vehicle.price >= filters['price_min'])
                if 'price_max' in filters:
                    query = query.filter(Vehicle.price <= filters['price_max'])
                if 'year_min' in filters:
                    query = query.filter(Vehicle.year >= filters['year_min'])
                if 'year_max' in filters:
                    query = query.filter(Vehicle.year <= filters['year_max'])
                if 'make' in filters:
                    query = query.filter(Vehicle.make.ilike(f"%{filters['make']}%"))
                if 'model' in filters:
                    query = query.filter(Vehicle.model.ilike(f"%{filters['model']}%"))

            # Tri par date de création (plus récent en premier)
            query = query.order_by(Vehicle.created_at.desc())

            # Récupérer tous les résultats (on pagine après fusion)
            vehicles = query.limit(100).all()  # Limite raisonnable

            # Convertir en dictionnaires
            for vehicle in vehicles:
                results.append({
                    'id': vehicle.id,
                    'title': vehicle.title,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'price': vehicle.price,
                    'year': vehicle.year,
                    'mileage': vehicle.mileage,
                    'fuel_type': vehicle.fuel_type,
                    'transmission': vehicle.transmission,
                    'description': vehicle.description,
                    'images': vehicle.images or [],
                    'location_city': vehicle.location_city,
                    'vin': vehicle.vin,
                    'source': 'database',
                    'created_at': vehicle.created_at.isoformat() if vehicle.created_at else None
                })

        except Exception as e:
            logger.error(f"❌ Erreur recherche DB: {e}")

        finally:
            db.close()

        return results

    @staticmethod
    def _merge_results(db_results: List[Dict], scraping_results: List[Dict]) -> List[Dict]:
        """Fusionne et déduplique les résultats de la DB et du scraping"""

        # Commencer avec les résultats DB
        merged = list(db_results)
        seen_keys = set()

        # Créer des clés uniques pour les résultats DB
        for result in db_results:
            key = (
                result.get('title', '').lower().strip(),
                result.get('price', 0)
            )
            seen_keys.add(key)

        # Ajouter les résultats du scraping non dupliqués
        for result in scraping_results:
            key = (
                result.get('title', '').lower().strip(),
                result.get('price', 0)
            )

            if key not in seen_keys and key[0]:
                seen_keys.add(key)
                merged.append(result)

        logger.info(f"🔀 Fusion: {len(db_results)} DB + {len(scraping_results)} scraping = {len(merged)} uniques")

        return merged


# Instance globale
hybrid_search = HybridSearchService()
