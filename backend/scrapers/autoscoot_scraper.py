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
            # Attendre que les annonces se chargent avec plusieurs sélecteurs possibles
            selectors = [
                'article[data-testid="listing-item"]',  # Sélecteur spécifique
                'article.ListItem_article',  # Avec classe
                'article',  # Générique - tous les articles
                'div[data-testid="search-listing"]',  # Container de recherche
                'a[href*="/annonces/"]',  # Liens vers annonces
                'div[class*="ListItem"]'  # Contient ListItem dans la classe
            ]

            listings = []
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=10000)
                    elements = self.page.query_selector_all(selector)

                    # Filtrer pour ne garder que les éléments pertinents
                    if selector == 'article':
                        # Pour le sélecteur générique, vérifier qu'il y a un lien d'annonce
                        listings = [el for el in elements if el.query_selector('a[href*="/annonces/"]')]
                    else:
                        listings = elements

                    if listings and len(listings) > 0:
                        logger.info(f"✅ Trouvé {len(listings)} annonces avec sélecteur: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Sélecteur '{selector}' non trouvé: {e}")
                    continue

            if not listings or len(listings) == 0:
                logger.warning("⚠️ Aucune annonce trouvée avec tous les sélecteurs")
                return results

            for idx, listing in enumerate(listings):
                try:
                    parsed = self.parse_listing(listing)
                    if parsed:
                        normalized = self.normalize_data(parsed)
                        results.append(normalized)
                        logger.debug(f"✓ Annonce {idx+1}: {parsed.get('title', 'N/A')[:50]}")
                    else:
                        logger.debug(f"✗ Annonce {idx+1}: Parsing retourné None")
                except Exception as e:
                    logger.warning(f"✗ Annonce {idx+1}: {e}")

            logger.info(f"📊 Parsé {len(results)}/{len(listings)} annonces avec succès")

        except Exception as e:
            logger.error(f"Erreur scraping page: {e}")

        return results

    def parse_listing(self, element) -> Optional[Dict[str, Any]]:
        """Parse une annonce AutoScout24 avec extraction générique et robuste"""
        try:
            # Trouver le lien principal (plusieurs méthodes)
            link = None
            if element.tag_name == 'a':
                link = element
            else:
                # Chercher le premier lien dans l'élément
                link = element.query_selector('a[href*="/annonces/"]') or element.query_selector('a')

            if not link:
                return None

            url = link.get_attribute('href')
            if not url or '/annonces/' not in url:
                return None

            # Construire l'URL complète
            if url.startswith('/'):
                url = f"{self.BASE_URL}{url}"

            # Extraire l'ID depuis l'URL
            source_id = url.split('/')[-1] if '/' in url else 'unknown'

            # Extraction GÉNÉRIQUE du texte complet de l'élément
            full_text = element.inner_text() if element else ""

            # Titre - essayer plusieurs sélecteurs puis fallback sur premier h2/h3
            title = None
            title_selectors = ['h2', 'h3', '[data-testid*="title"]', '[class*="title"]', '[class*="Title"]', 'a']
            for selector in title_selectors:
                title_elem = element.query_selector(selector)
                if title_elem:
                    title = title_elem.inner_text().strip()
                    if title and len(title) > 3:  # Au moins 3 caractères
                        break

            # Si pas de titre, essayer d'extraire de l'attribut du lien
            if not title and link:
                title = link.get_attribute('title') or link.get_attribute('aria-label')

            # Prix - chercher pattern de prix dans le texte
            price = None
            price_patterns = [
                r'(\d{1,3}(?:\s?\d{3})*)\s*€',  # Ex: 15 000 €
                r'€\s*(\d{1,3}(?:\s?\d{3})*)',  # Ex: € 15000
            ]
            for pattern in price_patterns:
                match = re.search(pattern, full_text)
                if match:
                    price = match.group(1).replace(' ', '')
                    break

            # Année - chercher pattern 4 chiffres entre 1990 et 2030
            year = None
            year_match = re.search(r'\b(19\d{2}|20[0-3]\d)\b', full_text)
            if year_match:
                year = int(year_match.group(1))

            # Kilométrage - chercher pattern de km
            mileage = None
            km_patterns = [
                r'(\d{1,3}(?:\s?\d{3})*)\s*km',
                r'(\d{1,3}(?:\s?\d{3})*)\s*Kilomètres',
            ]
            for pattern in km_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    mileage = match.group(1).replace(' ', '')
                    break

            # Carburant - chercher mots-clés
            fuel_type = None
            fuel_keywords = ['Diesel', 'Essence', 'Électrique', 'Hybride', 'GPL']
            for keyword in fuel_keywords:
                if keyword.lower() in full_text.lower():
                    fuel_type = keyword
                    break

            # Transmission
            transmission = None
            if 'automatique' in full_text.lower():
                transmission = 'Automatique'
            elif 'manuelle' in full_text.lower():
                transmission = 'Manuelle'

            # Image
            images = []
            img_elem = element.query_selector('img')
            if img_elem:
                img_src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                if img_src and not img_src.endswith('.svg') and 'placeholder' not in img_src:
                    images.append(img_src)

            # Extraire marque et modèle du titre
            make = None
            model = None
            if title:
                parts = title.split()
                if len(parts) >= 1:
                    make = parts[0]
                if len(parts) >= 2:
                    model = ' '.join(parts[1:3])  # 2 premiers mots après la marque

            # Retourner au moins avec URL et titre
            if not title or len(title) < 3:
                return None  # Pas assez d'infos

            return {
                'id': source_id,
                'title': title,
                'make': make,
                'model': model,
                'price': price,
                'year': year,
                'mileage': mileage,
                'fuel_type': fuel_type,
                'transmission': transmission,
                'location': None,  # Pas extrait pour l'instant
                'url': url,
                'images': images
            }

        except Exception as e:
            logger.warning(f"Erreur parse listing: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None