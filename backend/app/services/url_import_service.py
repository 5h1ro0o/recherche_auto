# backend/app/services/url_import_service.py
"""
Service pour importer des annonces depuis une URL spécifique
Supporte: LeBonCoin, La Centrale, AutoScout24
"""
import logging
import re
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import optionnel de Playwright
try:
    from scrapers.base_scraper import BaseScraper
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ Scrapers non disponibles")


class URLImportService:
    """Service pour extraire les données d'une URL d'annonce spécifique"""

    @staticmethod
    def detect_source(url: str) -> Optional[str]:
        """Détecte la source depuis l'URL"""
        url_lower = url.lower()

        if 'leboncoin.fr' in url_lower:
            return 'leboncoin'
        elif 'lacentrale.fr' in url_lower:
            return 'lacentrale'
        elif 'autoscout24.fr' in url_lower:
            return 'autoscout24'
        else:
            return None

    @staticmethod
    def import_from_url(url: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Importe une annonce depuis une URL spécifique

        Args:
            url: URL de l'annonce
            user_id: ID de l'utilisateur qui importe (optionnel)

        Returns:
            Dictionnaire avec les données extraites
        """
        logger.info(f"📥 Import depuis URL: {url}")

        # Détecter la source
        source = URLImportService.detect_source(url)
        if not source:
            raise ValueError("URL non reconnue. Supports: LeBonCoin, La Centrale, AutoScout24")

        # Extraire les données selon la source
        if source == 'leboncoin':
            return URLImportService._extract_leboncoin(url)
        elif source == 'lacentrale':
            return URLImportService._extract_lacentrale(url)
        elif source == 'autoscout24':
            return URLImportService._extract_autoscout24(url)

    @staticmethod
    def _extract_leboncoin(url: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce LeBonCoin"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Scrapers non disponibles")

        from scrapers.base_scraper import BaseScraper

        class LeBonCoinExtractor(BaseScraper):
            def get_source_name(self):
                return "leboncoin"

            def scrape(self, params):
                return []

        extractor = LeBonCoinExtractor()

        try:
            extractor.init_browser(headless=True)
            logger.info(f"🔵 Extraction LeBonCoin: {url}")

            extractor.page.goto(url, wait_until='networkidle', timeout=30000)
            extractor.random_delay(3, 5)

            # Extraire le titre
            title = None
            title_selectors = ['h1', '[data-qa-id*="adview_title"]', 'h1[class*="title"]']
            for sel in title_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    title = elem.inner_text().strip()
                    if title:
                        break

            # Extraire le prix
            price = None
            price_selectors = ['[data-qa-id="adview_price"]', '[class*="price"]', 'span[class*="amount"]']
            for sel in price_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    price_text = elem.inner_text().strip()
                    match = re.search(r'(\d[\d\s]*)', price_text.replace('\xa0', ' '))
                    if match:
                        price = int(match.group(1).replace(' ', ''))
                        break

            # Extraire la description
            description = None
            desc_selectors = ['[data-qa-id="adview_description"]', '[class*="description"]', 'div[class*="text"]']
            for sel in desc_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    description = elem.inner_text().strip()
                    if description and len(description) > 20:
                        break

            # Extraire les images
            images = []
            img_elements = extractor.page.query_selector_all('img[src*="leboncoin"]')
            for img in img_elements[:5]:  # Max 5 images
                src = img.get_attribute('src')
                if src and src.startswith('http'):
                    images.append(src)

            # Extraire la localisation
            location = None
            loc_selectors = ['[data-qa-id="adview_location"]', '[class*="location"]']
            for sel in loc_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    location = elem.inner_text().strip()
                    if location:
                        break

            # Extraction marque/modèle depuis le titre
            make, model = URLImportService._extract_make_model(title or '')

            return {
                'id': str(uuid.uuid4()),
                'title': title,
                'make': make,
                'model': model,
                'price': price or 0,
                'description': description,
                'images': images,
                'location_city': location,
                'source_ids': {'source': 'leboncoin', 'url': url},
                'url': url,
                'source': 'leboncoin',
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erreur extraction LeBonCoin: {e}")
            raise
        finally:
            extractor.close_browser()

    @staticmethod
    def _extract_lacentrale(url: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce La Centrale"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Scrapers non disponibles")

        from scrapers.base_scraper import BaseScraper

        class LaCentraleExtractor(BaseScraper):
            def get_source_name(self):
                return "lacentrale"

            def scrape(self, params):
                return []

        extractor = LaCentraleExtractor()

        try:
            extractor.init_browser(headless=True)
            logger.info(f"🟢 Extraction La Centrale: {url}")

            extractor.page.goto(url, wait_until='networkidle', timeout=30000)
            extractor.random_delay(3, 5)

            # Extraction similaire à LeBonCoin mais avec sélecteurs La Centrale
            title = None
            title_selectors = ['h1', 'h1[class*="title"]', 'h1[class*="vehicleName"]']
            for sel in title_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    title = elem.inner_text().strip()
                    if title:
                        break

            price = None
            price_selectors = ['[class*="price"]', 'span[class*="Price"]', '[class*="amount"]']
            for sel in price_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    price_text = elem.inner_text().strip()
                    match = re.search(r'(\d[\d\s]*)', price_text.replace('\xa0', ' '))
                    if match:
                        price = int(match.group(1).replace(' ', ''))
                        break

            description = extractor.page.query_selector('div[class*="description"]')
            desc_text = description.inner_text().strip() if description else ''

            images = []
            img_elements = extractor.page.query_selector_all('img[src]')
            for img in img_elements[:5]:
                src = img.get_attribute('src')
                if src and src.startswith('http'):
                    images.append(src)

            make, model = URLImportService._extract_make_model(title or '')

            return {
                'id': str(uuid.uuid4()),
                'title': title,
                'make': make,
                'model': model,
                'price': price or 0,
                'description': desc_text,
                'images': images,
                'source_ids': {'source': 'lacentrale', 'url': url},
                'url': url,
                'source': 'lacentrale',
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erreur extraction La Centrale: {e}")
            raise
        finally:
            extractor.close_browser()

    @staticmethod
    def _extract_autoscout24(url: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce AutoScout24"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Scrapers non disponibles")

        from scrapers.base_scraper import BaseScraper

        class AutoScout24Extractor(BaseScraper):
            def get_source_name(self):
                return "autoscout24"

            def scrape(self, params):
                return []

        extractor = AutoScout24Extractor()

        try:
            extractor.init_browser(headless=True)
            logger.info(f"🟠 Extraction AutoScout24: {url}")

            extractor.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            extractor.random_delay(3, 5)

            # Extraction avec sélecteurs AutoScout24
            title = None
            title_selectors = ['h1', 'h1[class*="VehicleName"]', 'h2']
            for sel in title_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    title = elem.inner_text().strip()
                    if title:
                        break

            price = None
            price_selectors = ['[class*="Price"]', '[data-testid*="price"]']
            for sel in price_selectors:
                elem = extractor.page.query_selector(sel)
                if elem:
                    price_text = elem.inner_text().strip()
                    match = re.search(r'(\d[\d\s]*)', price_text.replace('\xa0', ' '))
                    if match:
                        price = int(match.group(1).replace(' ', ''))
                        break

            description_elem = extractor.page.query_selector('[class*="description"]')
            description = description_elem.inner_text().strip() if description_elem else ''

            images = []
            img_elements = extractor.page.query_selector_all('img[src]')
            for img in img_elements[:5]:
                src = img.get_attribute('src')
                if src and src.startswith('http'):
                    images.append(src)

            make, model = URLImportService._extract_make_model(title or '')

            return {
                'id': str(uuid.uuid4()),
                'title': title,
                'make': make,
                'model': model,
                'price': price or 0,
                'description': description,
                'images': images,
                'source_ids': {'source': 'autoscout24', 'url': url},
                'url': url,
                'source': 'autoscout24',
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erreur extraction AutoScout24: {e}")
            raise
        finally:
            extractor.close_browser()

    @staticmethod
    def _extract_make_model(title: str) -> tuple:
        """Extrait marque et modèle depuis le titre"""
        brands = {
            'peugeot': 'Peugeot', 'renault': 'Renault', 'citroën': 'Citroën', 'citroen': 'Citroën',
            'volkswagen': 'Volkswagen', 'vw': 'Volkswagen', 'bmw': 'BMW', 'mercedes': 'Mercedes',
            'audi': 'Audi', 'ford': 'Ford', 'toyota': 'Toyota', 'nissan': 'Nissan',
            'opel': 'Opel', 'fiat': 'Fiat', 'seat': 'Seat', 'hyundai': 'Hyundai', 'kia': 'Kia'
        }

        title_lower = title.lower()
        for brand_key, brand_name in brands.items():
            if brand_key in title_lower:
                match = re.search(rf'{brand_key}\s+(\w+)', title_lower)
                model = match.group(1).capitalize() if match else None
                return brand_name, model

        return None, None


# Instance globale
url_import_service = URLImportService()
