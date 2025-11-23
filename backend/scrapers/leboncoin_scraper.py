# backend/scrapers/leboncoin_scraper.py - VERSION AVEC BIBLIOTHÈQUE LBC
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime

try:
    from .base_scraper import BaseScraper
except ImportError:
    # Pour exécution directe du fichier de test
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Importer la bibliothèque lbc
try:
    from lbc import Client, Category, Sort
    LBC_AVAILABLE = True
except ImportError:
    LBC_AVAILABLE = False
    logger.error("❌ Bibliothèque 'lbc' non disponible. Installez avec: pip install lbc")


class LeBonCoinScraper(BaseScraper):
    """
    Scraper pour LeBonCoin (leboncoin.fr) utilisant la bibliothèque lbc
    Contourne DataDome en utilisant curl-cffi au lieu de Playwright
    """

    BASE_URL = "https://www.leboncoin.fr"

    def get_source_name(self) -> str:
        return "leboncoin"

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LeBonCoin avec la bibliothèque lbc

        search_params:
            - query: str (ex: 'peugeot 208')
            - max_price: int (optionnel)
            - min_price: int (optionnel, défaut: 0)
            - min_year: int (optionnel)
            - max_mileage: int (optionnel)
            - fuel_type: str (optionnel)
            - transmission: str (optionnel)
            - max_pages: int (défaut: 5)
        """
        if not LBC_AVAILABLE:
            logger.error("❌ Bibliothèque lbc non disponible")
            return []

        query = search_params.get('query', 'voiture')
        max_price = search_params.get('max_price')
        min_price = search_params.get('min_price', 0)
        max_pages = search_params.get('max_pages', 5)

        results = []

        try:
            # Créer le client lbc avec impersonation aléatoire
            # Note: Vous pouvez passer un proxy si nécessaire:
            # from lbc import Proxy
            # proxy = Proxy(server="http://proxy-server:port", username="user", password="pass")
            # client = Client(proxy=proxy)
            client = Client()
            logger.info(f"🔵 LeBonCoin (API): Recherche '{query}' sur {max_pages} pages")
            logger.info(f"💡 Utilise curl-cffi pour contourner la détection de bot")

            # Construire les kwargs de filtres
            filters = {}
            if max_price:
                filters['price'] = (min_price, max_price)

            for page_num in range(1, max_pages + 1):
                try:
                    logger.info(f"📄 Page {page_num}/{max_pages}")

                    # Effectuer la recherche
                    search_result = client.search(
                        text=query,
                        category=Category.VEHICULES_VOITURES,
                        sort=Sort.NEWEST,  # Trier par date (les plus récentes)
                        page=page_num,
                        limit=35,  # Max par page
                        **filters
                    )

                    logger.info(f"✅ Trouvé {len(search_result.ads)} annonces sur page {page_num}")
                    logger.info(f"📊 Total disponible: {search_result.total} annonces")

                    if len(search_result.ads) == 0:
                        logger.warning(f"❌ Aucune annonce sur page {page_num}, arrêt")
                        break

                    # Parser chaque annonce
                    page_results = 0
                    for idx, ad in enumerate(search_result.ads, 1):
                        try:
                            parsed = self._parse_ad_from_lbc(ad)

                            if not parsed:
                                logger.debug(f"  ✗ Annonce {idx}: Parsing échoué (None)")
                                continue

                            # Appliquer les filtres personnalisés
                            if not self._matches_filters(parsed, search_params):
                                logger.debug(f"  ✗ Annonce {idx}: Ne correspond pas aux filtres - Prix: {parsed.get('price')}, Année: {parsed.get('year')}, Km: {parsed.get('mileage')}")
                                continue

                            # Normaliser
                            normalized = self.normalize_data(parsed)

                            results.append(normalized)
                            page_results += 1

                            logger.info(f"  ✓ Annonce {idx}: {normalized.get('title', 'N/A')[:60]} - {normalized.get('price')}€")

                        except Exception as e:
                            logger.error(f"  ✗ Erreur annonce {idx}: {e}")
                            import traceback
                            traceback.print_exc()

                    logger.info(f"📊 Page {page_num}: {page_results} annonces valides ajoutées")

                    # Si aucun résultat valide, arrêter
                    if page_results == 0:
                        logger.warning(f"⚠️ Aucun résultat valide sur page {page_num}, arrêt")
                        break

                    # Respecter un délai entre les pages
                    if page_num < max_pages:
                        self.random_delay(1, 3)

                except Exception as e:
                    error_msg = str(e)
                    if 'Datadome' in error_msg or 'datadome' in error_msg.lower():
                        logger.error(f"❌ Bloqué par DataDome sur page {page_num}")
                        logger.error(f"💡 Solutions:")
                        logger.error(f"   1. Attendre quelques heures (IP bloquée temporairement)")
                        logger.error(f"   2. Utiliser un proxy rotatif (voir doc lbc)")
                        logger.error(f"   3. Tester depuis une autre machine/réseau")
                        break  # Arrêter si bloqué par DataDome
                    else:
                        logger.error(f"❌ Erreur sur page {page_num}: {e}")
                        continue

            logger.info(f"🎉 LeBonCoin terminé: {len(results)} annonces récupérées")

        except Exception as e:
            logger.error(f"❌ Erreur critique LeBonCoin: {e}")
            import traceback
            traceback.print_exc()

        return results

    def _parse_ad_from_lbc(self, ad) -> Optional[Dict[str, Any]]:
        """
        Parser une annonce depuis l'objet Ad de la bibliothèque lbc

        Args:
            ad: Objet Ad de la bibliothèque lbc

        Returns:
            Dict avec les données extraites ou None
        """
        try:
            # Extraire les données de base
            data = {
                'title': ad.subject if hasattr(ad, 'subject') else None,
                'price': None,
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'transmission': None,
                'location': None,
                'url': ad.url if hasattr(ad, 'url') else None,
                'image_url': None,
                'description': ad.body if hasattr(ad, 'body') else None,
            }

            # Prix
            if hasattr(ad, 'price') and ad.price:
                try:
                    data['price'] = int(ad.price[0]) if isinstance(ad.price, list) else int(ad.price)
                except (ValueError, IndexError, TypeError):
                    pass

            # Image
            if hasattr(ad, 'images') and ad.images and hasattr(ad.images, 'urls'):
                try:
                    data['image_url'] = ad.images.urls[0] if ad.images.urls else None
                except (IndexError, AttributeError):
                    pass

            # Localisation
            if hasattr(ad, 'location') and ad.location:
                try:
                    location_parts = []
                    if hasattr(ad.location, 'city') and ad.location.city:
                        location_parts.append(ad.location.city)
                    if hasattr(ad.location, 'zipcode') and ad.location.zipcode:
                        location_parts.append(ad.location.zipcode)
                    data['location'] = ', '.join(location_parts) if location_parts else None
                except AttributeError:
                    pass

            # Attributs (année, kilométrage, carburant, transmission)
            # Note: ad.attributes est une LISTE d'objets Attribute, pas un dict
            if hasattr(ad, 'attributes') and ad.attributes:
                for attr in ad.attributes:
                    # Année (regdate)
                    if attr.key == 'regdate' and attr.value:
                        try:
                            data['year'] = int(attr.value)
                        except (ValueError, TypeError):
                            pass

                    # Kilométrage (mileage)
                    elif attr.key == 'mileage' and attr.value:
                        try:
                            data['mileage'] = int(attr.value)
                        except (ValueError, TypeError):
                            pass

                    # Carburant (fuel)
                    elif attr.key == 'fuel' and attr.value:
                        fuel_mapping = {
                            '1': 'essence',
                            '2': 'diesel',
                            '3': 'gpl',
                            '4': 'electrique',
                            '5': 'hybride',
                        }
                        data['fuel_type'] = fuel_mapping.get(str(attr.value), attr.value).lower()

                    # Boîte de vitesse (gearbox)
                    elif attr.key == 'gearbox' and attr.value:
                        gearbox_mapping = {
                            '1': 'manuelle',
                            '2': 'automatique',
                        }
                        data['transmission'] = gearbox_mapping.get(str(attr.value), attr.value).lower()

            # Si pas d'attributs extraits, essayer d'extraire depuis le titre/description
            if not data['year'] or not data['mileage']:
                self._enrich_with_nlp(data)

            # Validation minimale
            if not data['title']:
                return None

            return data

        except Exception as e:
            logger.debug(f"Erreur parsing ad: {e}")
            return None

    def _enrich_with_nlp(self, data: Dict[str, Any]):
        """
        Enrichir les données avec extraction NLP depuis titre/description

        Args:
            data: Dictionnaire à enrichir (modifié in-place)
        """
        text_sources = [
            data.get('title', ''),
            data.get('description', '')
        ]
        full_text = ' '.join([t for t in text_sources if t]).lower()

        # Année: 1990-2030
        if not data.get('year'):
            years = re.findall(r'\b(19[9]\d|20[0-3]\d)\b', full_text)
            if years:
                data['year'] = int(years[0])

        # Kilométrage
        if not data.get('mileage'):
            # Formats: "150 000 km", "150000km", "150k km"
            km_patterns = [
                r'(\d+)\s*000\s*km',  # 150 000 km
                r'(\d+)k\s*km',        # 150k km
                r'(\d{3,6})\s*km'      # 150000 km
            ]
            for pattern in km_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    try:
                        km = int(matches[0])
                        # Normaliser selon le format
                        if 'k km' in full_text or 'k km' in pattern:
                            km *= 1000
                        elif '000 km' in pattern and km < 1000:
                            km *= 1000
                        data['mileage'] = km
                        break
                    except ValueError:
                        continue

        # Carburant
        if not data.get('fuel_type'):
            fuel_keywords = {
                'essence': ['essence', 'sp95', 'sp98', 'e85'],
                'diesel': ['diesel', 'gazole', 'hdi', 'tdi', 'dci'],
                'electrique': ['électrique', 'electrique', '100% électrique', 'ev'],
                'hybride': ['hybride', 'hybrid', 'plug-in'],
                'gpl': ['gpl', 'lpg'],
            }
            for fuel_type, keywords in fuel_keywords.items():
                if any(kw in full_text for kw in keywords):
                    data['fuel_type'] = fuel_type
                    break

        # Transmission
        if not data.get('transmission'):
            if any(word in full_text for word in ['automatique', 'auto', 'bva', 'cvt', 'dsg']):
                data['transmission'] = 'automatique'
            elif any(word in full_text for word in ['manuelle', 'manuel', 'bvm']):
                data['transmission'] = 'manuelle'

    def _matches_filters(self, data: Dict[str, Any], search_params: Dict[str, Any]) -> bool:
        """
        Vérifie si une annonce correspond aux filtres de recherche

        Args:
            data: Données de l'annonce
            search_params: Paramètres de recherche avec filtres

        Returns:
            True si l'annonce correspond aux filtres
        """
        # Filtre prix max (déjà géré par l'API mais double vérification)
        max_price = search_params.get('max_price')
        if max_price and data.get('price'):
            if data['price'] > max_price:
                return False

        # Filtre année min
        min_year = search_params.get('min_year')
        if min_year and data.get('year'):
            if data['year'] < min_year:
                return False

        # Filtre kilométrage max
        max_mileage = search_params.get('max_mileage')
        if max_mileage and data.get('mileage'):
            if data['mileage'] > max_mileage:
                return False

        # Filtre carburant
        fuel_type = search_params.get('fuel_type')
        if fuel_type and data.get('fuel_type'):
            if fuel_type.lower() not in data['fuel_type'].lower():
                return False

        # Filtre transmission
        transmission = search_params.get('transmission')
        if transmission and data.get('transmission'):
            if transmission.lower() not in data['transmission'].lower():
                return False

        return True


# ============================================================================
# SCRIPT DE TEST
# ============================================================================
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,  # INFO for cleaner logs
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 70)
    print("🧪 TEST LEBONCOIN SCRAPER (avec bibliothèque lbc)")
    print("=" * 70)
    print()

    test_params = {
        'query': 'peugeot 208',
        'max_price': 15000,
        'max_pages': 2
    }

    print(f"📋 Paramètres: {test_params}")
    print()
    print("🚀 Lancement...")
    print()

    scraper = LeBonCoinScraper()
    results = scraper.scrape(test_params)

    print()
    print("=" * 70)
    print(f"📊 RÉSULTATS: {len(results)} annonces")
    print("=" * 70)
    print()

    if results:
        # Afficher les 5 premières annonces
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result.get('title', 'N/A')}")
            print(f"   Prix: {result.get('price', 'N/A')}€")
            print(f"   Année: {result.get('year', 'N/A')}")
            print(f"   Km: {result.get('mileage', 'N/A')}")
            print(f"   Carburant: {result.get('fuel_type', 'N/A')}")
            print(f"   Transmission: {result.get('transmission', 'N/A')}")
            print(f"   Lieu: {result.get('location', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")

        print(f"\n... et {len(results) - 5} autres annonces" if len(results) > 5 else "")
    else:
        print("❌ Aucun résultat")
