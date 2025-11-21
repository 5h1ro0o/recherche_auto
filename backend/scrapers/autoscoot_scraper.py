from typing import List, Dict, Any, Optional
import logging
import re
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class AutoScout24Scraper(BaseScraper):
    """Scraper pour AutoScout24 avec extraction complète des données"""

    BASE_URL = "https://www.autoscout24.fr"

    def get_source_name(self) -> str:
        return "autoscout24"

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape AutoScout24 avec support des filtres

        search_params:
            - max_pages: int (défaut: 3)
            - make: str (optionnel, ex: 'volkswagen')
            - model: str (optionnel, ex: 'golf')
            - min_year: int (optionnel)
            - max_year: int (optionnel)
            - max_price: int (optionnel)
            - fuel_type: str (optionnel: 'B' benzine, 'D' diesel, 'E' électrique)
        """
        max_pages = search_params.get('max_pages', 3)
        results = []

        try:
            self.init_browser(headless=True)
            logger.info(f"🔵 AutoScout24: Scraping {max_pages} pages")

            # Construire l'URL de recherche
            base_search_url = self._build_search_url(search_params)

            # Navigation initiale
            logger.info(f"🔗 URL: {base_search_url}")
            self.page.goto(base_search_url, wait_until='domcontentloaded', timeout=30000)
            self.random_delay(3, 5)

            # Gérer les cookies si présents
            self._handle_cookie_banner()

            for page_num in range(max_pages):
                logger.info(f"📄 Page {page_num + 1}/{max_pages}")

                if page_num > 0:
                    # Naviguer vers la page suivante
                    page_url = f"{base_search_url}&page={page_num + 1}"
                    self.page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
                    self.random_delay(2, 4)

                # Attendre les résultats
                page_results = self._scrape_page()

                if not page_results:
                    logger.warning(f"⚠️ Aucun résultat page {page_num + 1}, arrêt")
                    break

                results.extend(page_results)
                logger.info(f"✅ Page {page_num + 1}: {len(page_results)} annonces")

                # Délai entre pages
                self.random_delay(2, 4)

            logger.info(f"🎉 AutoScout24 terminé: {len(results)} annonces récupérées")

        except Exception as e:
            logger.exception(f"❌ Erreur AutoScout24: {e}")
        finally:
            self.close_browser()

        return results

    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """Construit l'URL de recherche avec filtres"""
        url_parts = [f"{self.BASE_URL}/lst"]
        query_params = []

        # Tri par défaut
        query_params.append("sort=standard")
        query_params.append("desc=0")

        # Type de véhicule (voiture)
        query_params.append("atype=C")

        # État (neuf et occasion)
        query_params.append("ustate=N,U")

        # Nombre de résultats par page
        query_params.append("size=20")

        # Marque
        if params.get('make'):
            make = params['make'].lower()
            query_params.append(f"mmvmk0={make}")

        # Modèle
        if params.get('model'):
            model = params['model'].lower()
            query_params.append(f"mmvmd0={model}")

        # Année
        if params.get('min_year'):
            query_params.append(f"fregfrom={params['min_year']}")
        if params.get('max_year'):
            query_params.append(f"fregto={params['max_year']}")

        # Prix
        if params.get('max_price'):
            query_params.append(f"priceto={params['max_price']}")

        # Carburant
        if params.get('fuel_type'):
            query_params.append(f"fuel={params['fuel_type']}")

        return f"{url_parts[0]}?{'&'.join(query_params)}"

    def _handle_cookie_banner(self):
        """Accepte les cookies si le banner est présent"""
        try:
            # Chercher le bouton d'acceptation des cookies
            accept_button = self.page.query_selector('button[data-testid="accept-all-button"]')
            if not accept_button:
                accept_button = self.page.query_selector('button:has-text("Accepter")')
            if not accept_button:
                accept_button = self.page.query_selector('button:has-text("Accept")')

            if accept_button:
                accept_button.click()
                self.random_delay(1, 2)
                logger.info("✅ Cookies acceptés")
        except Exception as e:
            logger.debug(f"Pas de banner cookies ou erreur: {e}")

    def _scrape_page(self) -> List[Dict[str, Any]]:
        """Scrape une page de résultats"""
        results = []

        try:
            # Attendre que les annonces se chargent
            # AutoScout24 utilise des articles avec classe ListItem_article
            selectors = [
                'article[data-testid="listing-item"]',
                'article.ListItem_article',
                'div[data-testid="search-listing"]',
                'a.ListItem_title'
            ]

            listings = []
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=15000)
                    listings = self.page.query_selector_all(selector)
                    if listings:
                        logger.info(f"✅ Trouvé {len(listings)} annonces avec sélecteur: {selector}")
                        break
                except:
                    continue

            if not listings:
                logger.warning("⚠️ Aucune annonce trouvée avec les sélecteurs")
                return results

            for idx, listing in enumerate(listings):
                try:
                    parsed = self.parse_listing(listing)
                    if parsed:
                        normalized = self.normalize_data(parsed)
                        results.append(normalized)
                except Exception as e:
                    logger.debug(f"Erreur parsing annonce {idx}: {e}")

        except Exception as e:
            logger.error(f"Erreur scraping page: {e}")

        return results

    def parse_listing(self, element) -> Optional[Dict[str, Any]]:
        """Parse une annonce AutoScout24"""
        try:
            # Trouver le lien principal
            link = element.query_selector('a') if element.tag_name != 'a' else element
            if not link:
                return None

            url = link.get_attribute('href')
            if not url:
                return None

            # Construire l'URL complète
            if url.startswith('/'):
                url = f"{self.BASE_URL}{url}"

            # Extraire l'ID depuis l'URL (format: /annonces/.../{id})
            source_id = None
            id_match = re.search(r'/([a-z0-9-]+)$', url)
            if id_match:
                source_id = id_match.group(1)

            # Titre (marque + modèle)
            title = None
            title_selectors = [
                'h2',
                '[data-testid="listing-title"]',
                '.ListItem_title',
                'span.ListItem_makeModelName'
            ]
            for selector in title_selectors:
                title_elem = element.query_selector(selector)
                if title_elem:
                    title = title_elem.inner_text().strip()
                    if title:
                        break

            # Prix
            price = None
            price_selectors = [
                '[data-testid="listing-price"]',
                '.Price_price',
                'span.PriceAndSeals_current-price'
            ]
            for selector in price_selectors:
                price_elem = element.query_selector(selector)
                if price_elem:
                    price_text = price_elem.inner_text().strip()
                    if price_text and price_text != '-':
                        price = price_text
                        break

            # Année
            year = None
            year_elem = element.query_selector('[data-testid="listing-year"]')
            if year_elem:
                year_text = year_elem.inner_text().strip()
                year_match = re.search(r'\d{4}', year_text)
                if year_match:
                    year = int(year_match.group())

            # Kilométrage
            mileage = None
            mileage_elem = element.query_selector('[data-testid="listing-mileage"]')
            if mileage_elem:
                mileage = mileage_elem.inner_text().strip()

            # Carburant
            fuel_type = None
            fuel_elem = element.query_selector('[data-testid="listing-fuel"]')
            if fuel_elem:
                fuel_type = fuel_elem.inner_text().strip()

            # Transmission
            transmission = None
            trans_elem = element.query_selector('[data-testid="listing-transmission"]')
            if trans_elem:
                transmission = trans_elem.inner_text().strip()

            # Localisation
            location = None
            location_elem = element.query_selector('[data-testid="listing-location"]')
            if location_elem:
                location = location_elem.inner_text().strip()

            # Image
            images = []
            img_elem = element.query_selector('img')
            if img_elem:
                img_src = img_elem.get_attribute('src')
                if img_src and not img_src.endswith('.svg'):
                    images.append(img_src)

            # Extraire marque et modèle du titre
            make = None
            model = None
            if title:
                parts = title.split()
                if len(parts) >= 2:
                    make = parts[0]
                    model = ' '.join(parts[1:])

            return {
                'id': source_id,
                'title': title or 'Sans titre',
                'make': make,
                'model': model,
                'price': price,
                'year': year,
                'mileage': mileage,
                'fuel_type': fuel_type,
                'transmission': transmission,
                'location': location,
                'url': url,
                'images': images
            }

        except Exception as e:
            logger.debug(f"Erreur parse listing: {e}")
            return None