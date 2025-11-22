# backend/scrapers/leboncoin_scraper.py - VERSION ROBUSTE ET SIMPLIFIÉE
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime, timedelta

try:
    from .base_scraper import BaseScraper
except ImportError:
    # Pour exécution directe du fichier de test
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LeBonCoinScraper(BaseScraper):
    """
    Scraper robuste pour LeBonCoin (leboncoin.fr)
    Utilise des sélecteurs multiples en fallback pour plus de fiabilité
    """

    BASE_URL = "https://www.leboncoin.fr"

    # Sélecteurs multiples (essayés dans l'ordre)
    SELECTORS = {
        'listing_container': [
            '[data-qa-id="aditem_container"]',
            'article[data-qa-id*="ad"]',
            'li[data-qa-id*="ad"]',
            'div[data-qa-id*="ad"]',
            'a[href*="/ad/"]',
            'a[href*="/voitures/"]',
            'div[class*="styles_adCard"]',
            'div[class*="AdCard"]',
            'article',
            'li.clearfix',
            'li',
            'div[itemtype*="Product"]',
            'div[data-test-id*="ad"]',
            'section article',
            'main article',
            'div[role="article"]'
        ],
        'title': [
            '[data-qa-id="aditem_title"]',
            'p[data-qa-id*="title"]',
            'div[data-qa-id*="title"]',
            'h2',
            'h3',
            '[itemprop="name"]',
            'p[class*="title"]',
            'div[class*="title"]'
        ],
        'price': [
            '[data-qa-id="aditem_price"]',
            'span[data-qa-id*="price"]',
            'p[data-qa-id*="price"]',
            'div[data-qa-id*="price"]',
            '[itemprop="price"]',
            'span[class*="price"]',
            'div[class*="price"]'
        ],
        'location': [
            '[data-qa-id="aditem_location"]',
            'p[data-qa-id*="location"]',
            '[itemprop="address"]',
            'span[class*="location"]'
        ],
        'image': [
            'img[alt]',
            'img[src*="thumbs"]',
            'img',
            '[data-qa-id*="image"] img'
        ],
        'link': [
            'a[href*="/ad/"]',
            'a[href*="/voitures/"]',
            'a[data-qa-id*="ad"]',
            'a[href*=".htm"]'
        ]
    }

    def get_source_name(self) -> str:
        return "leboncoin"

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LeBonCoin avec approche robuste

        search_params:
            - query: str (ex: 'peugeot 208')
            - max_price: int (optionnel)
            - min_year: int (optionnel)
            - max_mileage: int (optionnel)
            - fuel_type: str (optionnel)
            - transmission: str (optionnel)
            - max_pages: int (défaut: 20)
        """
        query = search_params.get('query', 'voiture')
        max_price = search_params.get('max_price')
        min_year = search_params.get('min_year')
        max_mileage = search_params.get('max_mileage')
        fuel_type = search_params.get('fuel_type')
        transmission = search_params.get('transmission')
        max_pages = search_params.get('max_pages', 20)

        results = []

        try:
            self.init_browser(headless=True)

            logger.info(f"🔵 LeBonCoin: Recherche '{query}' sur {max_pages} pages")

            for page_num in range(1, max_pages + 1):
                try:
                    logger.info(f"📄 Page {page_num}/{max_pages}")

                    # Construire URL
                    url = self._build_search_url(query, page_num, max_price)
                    logger.debug(f"URL: {url}")

                    # Navigation
                    self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

                    # Gérer les cookies GDPR si présents
                    try:
                        # Attendre 2 secondes pour la popup cookies
                        self.random_delay(1, 2)

                        # Essayer de cliquer sur accepter cookies
                        cookie_buttons = [
                            'button[id*="didomi-notice-agree"]',
                            'button[id*="accept"]',
                            'button:has-text("Accepter")',
                            'button:has-text("Tout accepter")',
                            '[data-testid="consent-accept-all"]'
                        ]
                        for btn_selector in cookie_buttons:
                            try:
                                btn = self.page.query_selector(btn_selector)
                                if btn:
                                    btn.click()
                                    logger.info(f"✅ Cookies acceptés via {btn_selector}")
                                    self.random_delay(1, 2)
                                    break
                            except:
                                pass
                    except:
                        pass

                    self.random_delay(2, 4)

                    # Attendre que le contenu charge (essayer plusieurs sélecteurs)
                    content_loaded = False
                    for selector in self.SELECTORS['listing_container']:
                        try:
                            self.page.wait_for_selector(selector, timeout=5000)
                            content_loaded = True
                            logger.info(f"✅ Sélecteur trouvé: {selector}")
                            break
                        except:
                            continue

                    if not content_loaded:
                        logger.warning(f"⚠️ Aucun sélecteur de listing trouvé, essai extraction brute...")

                        # MODE DEBUG: Sauvegarder HTML et screenshot
                        try:
                            import os
                            debug_dir = os.path.join(os.path.dirname(__file__), 'debug')
                            os.makedirs(debug_dir, exist_ok=True)

                            # Sauvegarder HTML complet
                            html_path = os.path.join(debug_dir, 'leboncoin_page.html')
                            with open(html_path, 'w', encoding='utf-8') as f:
                                f.write(self.page.content())
                            logger.warning(f"📄 HTML sauvegardé dans: {html_path}")

                            # Prendre screenshot
                            screenshot_path = os.path.join(debug_dir, 'leboncoin_page.png')
                            self.page.screenshot(path=screenshot_path, full_page=True)
                            logger.warning(f"📸 Screenshot sauvegardé dans: {screenshot_path}")

                            # Afficher snippet
                            html_snippet = self.page.content()[:2000]
                            logger.debug(f"HTML snippet:\n{html_snippet}")
                        except Exception as e:
                            logger.error(f"Erreur debug: {e}")

                    # Parser les listings avec TOUS les sélecteurs possibles
                    listings = []
                    best_selector = None
                    for selector in self.SELECTORS['listing_container']:
                        try:
                            found = self.page.query_selector_all(selector)
                            if found and len(found) > len(listings):
                                listings = found
                                best_selector = selector
                                logger.info(f"✅ {len(found)} éléments avec '{selector}'")
                        except Exception as e:
                            logger.debug(f"Erreur sélecteur '{selector}': {e}")
                            continue

                    if best_selector:
                        logger.info(f"🎯 Meilleur sélecteur: {best_selector} ({len(listings)} éléments)")

                    logger.info(f"✅ Trouvé {len(listings)} annonces potentielles")

                    if len(listings) == 0:
                        logger.warning(f"❌ Aucune annonce sur page {page_num}, arrêt")
                        break

                    # Parser chaque listing
                    page_results = 0
                    for idx, listing in enumerate(listings, 1):
                        try:
                            parsed = self._parse_listing_robust(listing)

                            if not parsed:
                                continue

                            # Appliquer les filtres
                            if not self._matches_filters(parsed, search_params):
                                logger.debug(f"  ✗ Annonce {idx}: Ne correspond pas aux filtres")
                                continue

                            # Normaliser
                            normalized = self.normalize_data(parsed)

                            # Enrichir avec NLP
                            self._enrich_with_nlp(normalized)

                            results.append(normalized)
                            page_results += 1

                            logger.debug(f"  ✓ Annonce {idx}: {normalized.get('title', 'N/A')[:60]}")

                        except Exception as e:
                            logger.debug(f"  ✗ Erreur annonce {idx}: {e}")

                    logger.info(f"📊 Page {page_num}: {page_results} annonces valides ajoutées")

                    # Si aucun résultat, arrêter
                    if page_results == 0:
                        logger.warning(f"⚠️ Aucun résultat valide sur page {page_num}, arrêt")
                        break

                    # Délai entre pages
                    if page_num < max_pages:
                        self.random_delay(2, 4)

                except Exception as e:
                    logger.error(f"❌ Erreur sur page {page_num}: {e}")
                    # Continuer quand même
                    continue

            logger.info(f"🎉 LeBonCoin terminé: {len(results)} annonces récupérées")

        except Exception as e:
            logger.exception(f"❌ Erreur critique LeBonCoin: {e}")
        finally:
            self.close_browser()

        return results

    def _build_search_url(self, query: str, page: int, max_price: Optional[int]) -> str:
        """Construit l'URL de recherche"""
        # Catégorie 2 = Voitures
        url = f"{self.BASE_URL}/recherche?category=2&text={query.replace(' ', '%20')}"

        if page > 1:
            url += f"&page={page}"

        if max_price:
            url += f"&price=0-{max_price}"

        return url

    def _parse_listing_robust(self, element) -> Optional[Dict[str, Any]]:
        """
        Parse un listing avec approche robuste (multiples sélecteurs)
        """
        try:
            # 1. Extraire le lien (ESSENTIEL)
            url = None

            # D'abord essayer si l'élément lui-même est un lien
            try:
                tag_name = element.evaluate('el => el.tagName.toLowerCase()')
                if tag_name == 'a':
                    url = element.get_attribute('href')
            except:
                pass

            # Sinon chercher un lien enfant
            if not url:
                for selector in self.SELECTORS['link']:
                    try:
                        link_elem = element.query_selector(selector)
                        if link_elem:
                            url = link_elem.get_attribute('href')
                            if url:
                                break
                    except:
                        continue

            if not url:
                logger.debug("Pas d'URL trouvée dans l'élément")
                return None

            # Construire URL complète
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"

            # Extraire ID depuis URL
            source_id = None
            patterns = [
                r'/(\d+)\.htm',
                r'/ad/(\d+)',
                r'id=(\d+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    source_id = match.group(1)
                    break

            if not source_id:
                # Utiliser hash de l'URL comme ID
                source_id = str(hash(url))[-10:]

            # 2. Extraire le titre
            title = None
            for selector in self.SELECTORS['title']:
                title = self.safe_get_text(element, selector)
                if title and len(title) > 3:
                    break

            if not title:
                title = "Sans titre"

            # 3. Extraire le prix
            price_text = None
            for selector in self.SELECTORS['price']:
                price_text = self.safe_get_text(element, selector)
                if price_text:
                    break

            # 4. Extraire la localisation
            location = None
            for selector in self.SELECTORS['location']:
                location = self.safe_get_text(element, selector)
                if location and len(location) > 2:
                    break

            # 5. Extraire l'image
            img_url = None
            for selector in self.SELECTORS['image']:
                try:
                    img_elem = element.query_selector(selector)
                    if img_elem:
                        # Essayer plusieurs attributs
                        for attr in ['src', 'data-src', 'data-lazy-src']:
                            img_url = img_elem.get_attribute(attr)
                            if img_url and img_url.startswith('http'):
                                break
                        if img_url and img_url.startswith('http'):
                            break
                except:
                    continue

            # Construire le résultat
            result = {
                'id': source_id,
                'title': title,
                'url': url,
            }

            if price_text:
                result['price'] = price_text

            if location:
                result['location'] = location

            if img_url:
                result['images'] = [img_url]

            return result

        except Exception as e:
            logger.debug(f"Erreur parse_listing_robust: {e}")
            return None

    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Vérifie si l'annonce correspond aux filtres"""
        try:
            # Filtre prix maximum
            max_price = filters.get('max_price')
            if max_price:
                price = data.get('price')
                if price:
                    # Extraire le nombre du prix
                    price_num = self._extract_number(price)
                    if price_num and price_num > max_price:
                        return False

            # Filtre année minimum
            min_year = filters.get('min_year')
            if min_year:
                year = data.get('year')
                if year and year < min_year:
                    return False

            # Filtre kilométrage maximum
            max_mileage = filters.get('max_mileage')
            if max_mileage:
                mileage = data.get('mileage')
                if mileage and mileage > max_mileage:
                    return False

            # Filtre carburant
            fuel_filter = filters.get('fuel_type')
            if fuel_filter:
                fuel = data.get('fuel_type', '').lower()
                if fuel and fuel_filter.lower() not in fuel:
                    return False

            # Filtre transmission
            trans_filter = filters.get('transmission')
            if trans_filter:
                trans = data.get('transmission', '').lower()
                if trans and trans_filter.lower() not in trans:
                    return False

            return True

        except Exception as e:
            logger.debug(f"Erreur filtre: {e}")
            return True

    def _enrich_with_nlp(self, data: Dict[str, Any]):
        """Enrichit les données avec extraction NLP depuis le titre"""
        title = data.get('title', '').lower()

        # Extraction année (4 chiffres entre 1990 et 2030)
        if not data.get('year'):
            years = re.findall(r'\b(19[9]\d|20[0-3]\d)\b', title)
            if years:
                data['year'] = int(years[0])

        # Extraction kilométrage
        if not data.get('mileage'):
            km_patterns = [
                r'(\d+)\s*000\s*km',
                r'(\d+)k\s*km',
                r'(\d{3,6})\s*km'
            ]
            for pattern in km_patterns:
                match = re.search(pattern, title)
                if match:
                    km_str = match.group(1).replace(' ', '')
                    try:
                        mileage = int(km_str)
                        # Si format "150 000 km" → 150
                        if '000 km' in title and mileage < 1000:
                            mileage *= 1000
                        data['mileage'] = mileage
                        break
                    except:
                        pass

        # Extraction marque/modèle
        if not data.get('make'):
            brands = {
                'peugeot': 'Peugeot', 'renault': 'Renault', 'citroën': 'Citroën', 'citroen': 'Citroën',
                'volkswagen': 'Volkswagen', 'vw': 'Volkswagen', 'bmw': 'BMW', 'mercedes': 'Mercedes-Benz',
                'audi': 'Audi', 'ford': 'Ford', 'toyota': 'Toyota', 'honda': 'Honda', 'nissan': 'Nissan',
                'opel': 'Opel', 'fiat': 'Fiat', 'seat': 'Seat', 'skoda': 'Skoda', 'hyundai': 'Hyundai',
                'kia': 'Kia', 'mazda': 'Mazda', 'volvo': 'Volvo', 'tesla': 'Tesla', 'dacia': 'Dacia',
                'mini': 'Mini', 'porsche': 'Porsche', 'jaguar': 'Jaguar', 'land rover': 'Land Rover'
            }

            for brand_key, brand_name in brands.items():
                if brand_key in title:
                    data['make'] = brand_name
                    # Essayer d'extraire le modèle
                    pattern = rf'\b{re.escape(brand_key)}\s+([a-z0-9\-]+)'
                    match = re.search(pattern, title)
                    if match:
                        model = match.group(1)
                        # Ignorer les mots communs
                        if model not in ['occasion', 'voiture', 'auto', 'diesel', 'essence']:
                            data['model'] = model.upper()
                    break

        # Extraction carburant
        if not data.get('fuel_type'):
            fuel_keywords = {
                'diesel': 'diesel',
                'essence': 'essence',
                'électrique': 'electrique',
                'electric': 'electrique',
                'hybride': 'hybride',
                'gpl': 'gpl',
                'ethanol': 'ethanol'
            }

            for keyword, fuel_type in fuel_keywords.items():
                if keyword in title:
                    data['fuel_type'] = fuel_type
                    break

        # Extraction transmission
        if not data.get('transmission'):
            if 'automatique' in title or 'auto' in title:
                data['transmission'] = 'automatique'
            elif 'manuelle' in title:
                data['transmission'] = 'manuelle'

    def _extract_number(self, text: str) -> Optional[int]:
        """Extrait un nombre d'un texte"""
        if not text:
            return None

        try:
            # Nettoyer et extraire le nombre
            cleaned = re.sub(r'[^\d]', '', text)
            if cleaned:
                return int(cleaned)
        except:
            pass

        return None


# ============ FONCTION DE TEST ============

def test_leboncoin_simple():
    """Test simple du scraper LeBonCoin"""
    import json

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("="*70)
    print("🧪 TEST LEBONCOIN SCRAPER")
    print("="*70)

    scraper = LeBonCoinScraper()

    search_params = {
        'query': 'peugeot 208',
        'max_price': 15000,
        'max_pages': 2
    }

    print(f"\n📋 Paramètres: {json.dumps(search_params, indent=2, ensure_ascii=False)}")
    print("\n🚀 Lancement...\n")

    results = scraper.scrape(search_params)

    print("\n" + "="*70)
    print(f"📊 RÉSULTATS: {len(results)} annonces")
    print("="*70)

    if results:
        print(f"\n✨ Première annonce:")
        print(json.dumps(results[0], indent=2, ensure_ascii=False))

        # Stats
        with_price = sum(1 for r in results if r.get('price'))
        with_year = sum(1 for r in results if r.get('year'))
        with_mileage = sum(1 for r in results if r.get('mileage'))
        with_images = sum(1 for r in results if r.get('images'))

        print(f"\n📈 STATS:")
        print(f"  - Avec prix: {with_price}/{len(results)}")
        print(f"  - Avec année: {with_year}/{len(results)}")
        print(f"  - Avec kilométrage: {with_mileage}/{len(results)}")
        print(f"  - Avec images: {with_images}/{len(results)}")
    else:
        print("\n❌ Aucun résultat")


if __name__ == "__main__":
    test_leboncoin_simple()
