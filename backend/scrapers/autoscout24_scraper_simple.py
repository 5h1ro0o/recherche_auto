# backend/scrapers/autoscout24_scraper_simple.py
"""
Scraper simplifié pour AutoScout24 - Version robuste
"""
from typing import List, Dict, Any
import logging
import re
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class AutoScout24ScraperSimple(BaseScraper):
    """Scraper simplifié pour AutoScout24"""

    BASE_URL = "https://www.autoscout24.fr"

    def get_source_name(self) -> str:
        return "autoscout24"

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape AutoScout24"""
        query = search_params.get('query', 'voiture')
        max_price = search_params.get('max_price')

        results = []

        try:
            self.init_browser(headless=True)
            logger.info(f"🟠 AutoScout24 Simple: Recherche '{query}'")

            # Construire URL
            url = f"{self.BASE_URL}/lst?sort=standard&desc=0&ustate=N%2CU&size=20&page=0&atype=C"
            if max_price:
                url += f"&priceto={max_price}"

            # Ajouter la recherche si ce n'est pas juste "voiture"
            if query and query.lower() != 'voiture':
                url += f"&search_id={query.replace(' ', '+')}"

            logger.info(f"📍 URL: {url}")

            # Naviguer avec timeout plus long
            try:
                self.page.goto(url, wait_until='domcontentloaded', timeout=40000)
                self.random_delay(3, 5)
            except Exception as e:
                logger.error(f"❌ Timeout AutoScout24: {e}")
                return []

            # Essayer plusieurs sélecteurs
            selectors_to_try = [
                'article[data-item-name="listing-card"]',
                'article[class*="ListItem"]',
                'div[data-item-name*="listing"]',
                'a[href*="/offres/"]',
                'article',
                'div[class*="vehicle"]'
            ]

            listings = []
            for selector in selectors_to_try:
                try:
                    found = self.page.query_selector_all(selector)
                    if found and len(found) > 0:
                        logger.info(f"✅ Trouvé {len(found)} éléments avec: {selector}")
                        listings = found[:20]
                        break
                except:
                    continue

            if not listings:
                logger.warning(f"⚠️ Aucune annonce trouvée")
                return []

            # Parser
            for idx, listing in enumerate(listings, 1):
                try:
                    parsed = self._parse_listing(listing)
                    if parsed:
                        results.append(parsed)
                        logger.debug(f"  ✓ Annonce {idx}: {parsed.get('title', 'N/A')[:40]}")
                except Exception as e:
                    logger.debug(f"  ✗ Erreur annonce {idx}: {e}")

            logger.info(f"🎉 AutoScout24: {len(results)} annonces")

        except Exception as e:
            logger.exception(f"❌ Erreur AutoScout24: {e}")
        finally:
            self.close_browser()

        return results

    def _parse_listing(self, element) -> Dict[str, Any]:
        """Parse une annonce"""
        try:
            # Lien
            link = None
            link_selectors = ['a[href*="/offres/"]', 'a[href]']
            for sel in link_selectors:
                link_elem = element.query_selector(sel)
                if link_elem:
                    link = link_elem.get_attribute('href')
                    if link:
                        break

            if not link:
                return None

            url = f"{self.BASE_URL}{link}" if not link.startswith('http') else link
            source_id = url.split('/')[-1].split('?')[0]

            # Titre
            title = None
            title_selectors = ['h2', 'h3', '[class*="Title"]', 'span[class*="VehicleName"]']
            for sel in title_selectors:
                elem = element.query_selector(sel)
                if elem:
                    title = elem.inner_text().strip()
                    if title and len(title) > 5:
                        break

            # Prix
            price = None
            price_selectors = ['[class*="Price"]', '[data-testid*="price"]', 'span[class*="price"]']
            for sel in price_selectors:
                elem = element.query_selector(sel)
                if elem:
                    price_text = elem.inner_text().strip()
                    match = re.search(r'(\d[\d\s]*)', price_text.replace('\xa0', ' ').replace('€', ''))
                    if match:
                        price = int(match.group(1).replace(' ', ''))
                        break

            # Image
            image_url = None
            img_elem = element.query_selector('img')
            if img_elem:
                image_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')

            if not title:
                return None

            make, model = self._extract_make_model(title)

            return {
                'id': source_id,
                'title': title,
                'make': make,
                'model': model,
                'price': price if price else 0,
                'url': url,
                'images': [image_url] if image_url and image_url.startswith('http') else [],
                'source': 'autoscout24'
            }

        except Exception as e:
            logger.debug(f"Erreur parsing: {e}")
            return None

    def _extract_make_model(self, title: str) -> tuple:
        """Extrait marque et modèle"""
        brands = {
            'peugeot': 'Peugeot', 'renault': 'Renault', 'citroën': 'Citroën', 'citroen': 'Citroën',
            'volkswagen': 'Volkswagen', 'vw': 'Volkswagen', 'bmw': 'BMW', 'mercedes': 'Mercedes',
            'audi': 'Audi', 'ford': 'Ford', 'toyota': 'Toyota'
        }

        title_lower = title.lower()
        for brand_key, brand_name in brands.items():
            if brand_key in title_lower:
                match = re.search(rf'{brand_key}\s+(\w+)', title_lower)
                model = match.group(1).capitalize() if match else None
                return brand_name, model

        return None, None
