# backend/scrapers/leboncoin_scraper_simple.py
"""
Scraper simplifié pour LeBonCoin - Version robuste
Utilise des sélecteurs génériques et plusieurs fallbacks
"""
from typing import List, Dict, Any
import logging
import re
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LeBonCoinScraperSimple(BaseScraper):
    """Scraper simplifié et robuste pour LeBonCoin"""

    BASE_URL = "https://www.leboncoin.fr"

    def get_source_name(self) -> str:
        return "leboncoin"

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape LeBonCoin avec sélecteurs robustes"""
        query = search_params.get('query', 'voiture')
        max_pages = search_params.get('max_pages', 2)
        max_price = search_params.get('max_price')

        results = []

        try:
            self.init_browser(headless=True)
            logger.info(f"🔵 LeBonCoin Simple: Recherche '{query}' ({max_pages} pages max)")

            # Construire URL
            url = f"{self.BASE_URL}/recherche?category=2&text={query.replace(' ', '+')}"
            if max_price:
                url += f"&price_max={max_price}"

            logger.info(f"📍 URL: {url}")

            # Naviguer avec délai plus long (comportement humain)
            try:
                self.page.goto(url, wait_until='networkidle', timeout=30000)
                # Délai plus long pour imiter un humain
                self.random_delay(5, 8)

                # Simuler comportement humain
                self.simulate_human_behavior()
                self.random_delay(2, 4)

            except Exception as e:
                logger.error(f"❌ Impossible de charger LeBonCoin: {e}")
                return []

            # Essayer plusieurs sélecteurs pour trouver les annonces
            selectors_to_try = [
                '[data-qa-id="aditem_container"]',  # Ancien sélecteur
                'article[data-qa-id*="ad"]',
                'a[href*="/voitures/"]',
                'div[class*="styles_adCard"]',
                'div[class*="adCard"]',
                'li[data-qa-id*="list"]',
                'article',
                'div[data-testid*="ad"]'
            ]

            listings = []
            for selector in selectors_to_try:
                try:
                    found = self.page.query_selector_all(selector)
                    if found and len(found) > 0:
                        logger.info(f"✅ Trouvé {len(found)} éléments avec sélecteur: {selector}")
                        listings = found[:20]  # Limiter à 20 résultats
                        break
                except:
                    continue

            if not listings:
                logger.warning(f"⚠️ Aucune annonce trouvée avec les sélecteurs disponibles")
                # Sauvegarder la page HTML pour debug
                try:
                    html_content = self.page.content()
                    logger.debug(f"HTML de la page (premiers 500 caractères): {html_content[:500]}")
                except:
                    pass
                return []

            # Parser chaque annonce
            for idx, listing in enumerate(listings, 1):
                try:
                    parsed = self._parse_listing(listing)
                    if parsed:
                        results.append(parsed)
                        logger.debug(f"  ✓ Annonce {idx}: {parsed.get('title', 'N/A')[:40]}")
                except Exception as e:
                    logger.debug(f"  ✗ Erreur annonce {idx}: {e}")

            logger.info(f"🎉 LeBonCoin: {len(results)} annonces récupérées")

        except Exception as e:
            logger.exception(f"❌ Erreur LeBonCoin: {e}")
        finally:
            self.close_browser()

        return results

    def _parse_listing(self, element) -> Dict[str, Any]:
        """Parse une annonce avec sélecteurs génériques"""
        try:
            # Trouver le lien
            link = None
            link_selectors = ['a[href*="/voitures/"]', 'a[href*="/ad/"]', 'a[href]']
            for sel in link_selectors:
                link_elem = element.query_selector(sel)
                if link_elem:
                    link = link_elem.get_attribute('href')
                    if link and ('voitures' in link or 'ad' in link):
                        break

            if not link:
                return None

            # URL complète
            url = f"{self.BASE_URL}{link}" if not link.startswith('http') else link

            # ID
            source_id = url.split('/')[-1].replace('.htm', '').split('?')[0]

            # Titre - essayer plusieurs sélecteurs
            title = None
            title_selectors = [
                '[data-qa-id="aditem_title"]',
                'h2', 'h3',
                '[class*="title"]',
                'span[class*="title"]',
                'p[class*="title"]'
            ]
            for sel in title_selectors:
                title_elem = element.query_selector(sel)
                if title_elem:
                    title = title_elem.inner_text().strip()
                    if title and len(title) > 5:
                        break

            # Prix
            price = None
            price_text = None
            price_selectors = [
                '[data-qa-id="aditem_price"]',
                '[class*="price"]',
                'span[class*="amount"]',
                'div[class*="price"]'
            ]
            for sel in price_selectors:
                price_elem = element.query_selector(sel)
                if price_elem:
                    price_text = price_elem.inner_text().strip()
                    if price_text:
                        # Extraire le chiffre
                        price_match = re.search(r'(\d[\d\s]*)', price_text.replace('\xa0', ' '))
                        if price_match:
                            price = int(price_match.group(1).replace(' ', ''))
                            break

            # Image
            image_url = None
            img_selectors = ['img[src]', 'img[data-src]']
            for sel in img_selectors:
                img_elem = element.query_selector(sel)
                if img_elem:
                    image_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                    if image_url and image_url.startswith('http'):
                        break

            # Location
            location = None
            loc_selectors = [
                '[data-qa-id="aditem_location"]',
                '[class*="location"]',
                '[class*="city"]'
            ]
            for sel in loc_selectors:
                loc_elem = element.query_selector(sel)
                if loc_elem:
                    location = loc_elem.inner_text().strip()
                    if location:
                        break

            if not title:
                return None

            # Extraction marque/modèle depuis le titre
            make, model = self._extract_make_model(title)

            return {
                'id': source_id,
                'title': title,
                'make': make,
                'model': model,
                'price': price if price else 0,
                'url': url,
                'images': [image_url] if image_url else [],
                'location': location,
                'source': 'leboncoin'
            }

        except Exception as e:
            logger.debug(f"Erreur parsing: {e}")
            return None

    def _extract_make_model(self, title: str) -> tuple:
        """Extrait marque et modèle du titre"""
        brands = {
            'peugeot': 'Peugeot', 'renault': 'Renault', 'citroën': 'Citroën', 'citroen': 'Citroën',
            'volkswagen': 'Volkswagen', 'vw': 'Volkswagen', 'bmw': 'BMW', 'mercedes': 'Mercedes',
            'audi': 'Audi', 'ford': 'Ford', 'toyota': 'Toyota', 'nissan': 'Nissan',
            'opel': 'Opel', 'fiat': 'Fiat', 'seat': 'Seat'
        }

        title_lower = title.lower()
        make = None
        model = None

        for brand_key, brand_name in brands.items():
            if brand_key in title_lower:
                make = brand_name
                # Essayer d'extraire le modèle (mot après la marque)
                pattern = rf'{brand_key}\s+(\w+)'
                match = re.search(pattern, title_lower)
                if match:
                    model = match.group(1).capitalize()
                break

        return make, model
