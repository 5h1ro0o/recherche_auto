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
        Scrape LeBonCoin avec la bibliothèque lbc - EXTRACTION COMPLÈTE

        search_params disponibles:
            RECHERCHE DE BASE:
            - query: str (ex: 'peugeot 208')
            - max_pages: int (défaut: 5)

            FILTRES DE PRIX:
            - min_price: int (prix minimum en €)
            - max_price: int (prix maximum en €)

            FILTRES VÉHICULE:
            - min_year: int (année minimale, ex: 2015)
            - max_year: int (année maximale, ex: 2023)
            - min_mileage: int (kilométrage min, ex: 0)
            - max_mileage: int (kilométrage max, ex: 100000)
            - fuel_types: list[str] (carburants: ['1'=essence, '2'=diesel, '3'=gpl, '4'=electrique, '5'=hybride])
            - transmissions: list[str] (boîtes: ['1'=manuelle, '2'=automatique])
            - doors: list[str] (nombre de portes: ['2', '3', '4', '5'])
            - seats: list[str] (nombre de places: ['2', '3', '4', '5', '6', '7'])

            FILTRES PUISSANCE/PERFORMANCES:
            - min_horsepower: int (puissance fiscale min)
            - max_horsepower: int (puissance fiscale max)
            - min_horse_power_din: int (puissance DIN min en ch)
            - max_horse_power_din: int (puissance DIN max en ch)

            FILTRES ÉQUIPEMENT/ÉTAT:
            - vehicle_types: list[str] (types de véhicule)
            - colors: list[str] (couleurs)
            - first_hand: bool (True = première main uniquement)
            - maintenance_booklet: bool (True = carnet d'entretien disponible)
            - vehicle_damage: list[str] (état du véhicule)

            FILTRES LOCALISATION:
            - locations: list[Region/Department/City] (filtrer par région/département/ville)

            FILTRES VENDEUR:
            - owner_type: str ('pro', 'private', 'all')
        """
        if not LBC_AVAILABLE:
            logger.error("❌ Bibliothèque lbc non disponible")
            return []

        query = search_params.get('query', 'voiture')
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

            # Construire les filtres (ranges et enums)
            filters = {}

            # FILTRES DE PRIX (range)
            min_price = search_params.get('min_price')
            max_price = search_params.get('max_price')
            if min_price is not None or max_price is not None:
                filters['price'] = (min_price or 0, max_price or 999999)

            # FILTRES ANNÉE (regdate range)
            min_year = search_params.get('min_year')
            max_year = search_params.get('max_year')
            if min_year is not None or max_year is not None:
                filters['regdate'] = (min_year or 1900, max_year or 2030)

            # FILTRES KILOMÉTRAGE (mileage range)
            min_mileage = search_params.get('min_mileage')
            max_mileage = search_params.get('max_mileage')
            if min_mileage is not None or max_mileage is not None:
                filters['mileage'] = (min_mileage or 0, max_mileage or 999999)

            # FILTRES PUISSANCE FISCALE (horsepower range)
            min_horsepower = search_params.get('min_horsepower')
            max_horsepower = search_params.get('max_horsepower')
            if min_horsepower is not None or max_horsepower is not None:
                filters['horsepower'] = (min_horsepower or 0, max_horsepower or 999)

            # FILTRES PUISSANCE DIN (horse_power_din range)
            min_horse_power_din = search_params.get('min_horse_power_din')
            max_horse_power_din = search_params.get('max_horse_power_din')
            if min_horse_power_din is not None or max_horse_power_din is not None:
                filters['horse_power_din'] = (min_horse_power_din or 0, max_horse_power_din or 999)

            # FILTRES CARBURANT (fuel enum)
            fuel_types = search_params.get('fuel_types')
            if fuel_types:
                filters['fuel'] = tuple(fuel_types) if isinstance(fuel_types, list) else (fuel_types,)

            # FILTRES TRANSMISSION (gearbox enum)
            transmissions = search_params.get('transmissions')
            if transmissions:
                filters['gearbox'] = tuple(transmissions) if isinstance(transmissions, list) else (transmissions,)

            # FILTRES PORTES (doors enum)
            doors = search_params.get('doors')
            if doors:
                filters['doors'] = tuple(doors) if isinstance(doors, list) else (doors,)

            # FILTRES PLACES (seats enum)
            seats = search_params.get('seats')
            if seats:
                filters['seats'] = tuple(seats) if isinstance(seats, list) else (seats,)

            # FILTRES TYPE DE VÉHICULE (vehicle_type enum)
            vehicle_types = search_params.get('vehicle_types')
            if vehicle_types:
                filters['vehicle_type'] = tuple(vehicle_types) if isinstance(vehicle_types, list) else (vehicle_types,)

            # FILTRES COULEUR (vehicule_color enum)
            colors = search_params.get('colors')
            if colors:
                filters['vehicule_color'] = tuple(colors) if isinstance(colors, list) else (colors,)

            # FILTRES ÉTAT DU VÉHICULE (vehicle_damage enum)
            vehicle_damage = search_params.get('vehicle_damage')
            if vehicle_damage:
                filters['vehicle_damage'] = tuple(vehicle_damage) if isinstance(vehicle_damage, list) else (vehicle_damage,)

            # FILTRES BOOLÉENS (convertis en enum)
            if search_params.get('first_hand') is True:
                filters['first_hand_vehicle'] = ('1',)  # '1' = oui

            if search_params.get('maintenance_booklet') is True:
                filters['maintenance_booklet_available'] = ('1',)  # '1' = oui

            # AUTRES PARAMÈTRES (owner_type, locations)
            owner_type_param = search_params.get('owner_type')
            locations_param = search_params.get('locations')

            if filters:
                logger.info(f"🔍 Filtres appliqués: {list(filters.keys())}")

            for page_num in range(1, max_pages + 1):
                try:
                    logger.info(f"📄 Page {page_num}/{max_pages}")

                    # Préparer les paramètres de recherche
                    search_kwargs = {
                        'text': query,
                        'category': Category.VEHICULES_VOITURES,
                        'sort': Sort.NEWEST,  # Trier par date (les plus récentes)
                        'page': page_num,
                        'limit': 35,  # Max par page
                    }

                    # Ajouter owner_type si spécifié
                    if owner_type_param:
                        from lbc import OwnerType
                        owner_type_map = {
                            'pro': OwnerType.PRO,
                            'private': OwnerType.PRIVATE,
                            'all': OwnerType.ALL
                        }
                        if owner_type_param.lower() in owner_type_map:
                            search_kwargs['owner_type'] = owner_type_map[owner_type_param.lower()]

                    # Ajouter locations si spécifié
                    if locations_param:
                        search_kwargs['locations'] = locations_param

                    # Ajouter tous les filtres
                    search_kwargs.update(filters)

                    # Effectuer la recherche
                    search_result = client.search(**search_kwargs)

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

                    # Si aucun résultat, arrêter
                    if page_results == 0:
                        logger.warning(f"⚠️ Aucun résultat sur page {page_num}, arrêt")
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
        Parser une annonce depuis l'objet Ad de la bibliothèque lbc - EXTRACTION COMPLÈTE

        Args:
            ad: Objet Ad de la bibliothèque lbc

        Returns:
            Dict avec TOUTES les données extraites ou None
        """
        try:
            # Extraire les données de base
            data = {
                # DONNÉES DE BASE
                'title': ad.subject if hasattr(ad, 'subject') else None,
                'description': ad.body if hasattr(ad, 'body') else None,
                'url': ad.url if hasattr(ad, 'url') else None,
                'price': None,
                'location': None,
                'image_url': None,  # Première image (compatibilité)
                'images': [],  # TOUTES les images

                # DATES
                'first_publication_date': ad.first_publication_date if hasattr(ad, 'first_publication_date') else None,
                'expiration_date': ad.expiration_date if hasattr(ad, 'expiration_date') else None,
                'index_date': ad.index_date if hasattr(ad, 'index_date') else None,
                'issuance_date': None,

                # INFORMATIONS VÉHICULE PRINCIPALES
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'transmission': None,

                # CARACTÉRISTIQUES VÉHICULE
                'brand': ad.brand if hasattr(ad, 'brand') else None,
                'doors': None,
                'seats': None,
                'finition': None,  # u_car_finition
                'version': None,   # u_car_version
                'vehicle_type': None,
                'color': None,  # vehicule_color

                # PUISSANCE
                'horsepower': None,  # Puissance fiscale (CV)
                'horse_power_din': None,  # Puissance DIN (ch)
                'critair': None,  # Vignette Crit'Air

                # ÉTAT ET ÉQUIPEMENTS
                'vehicle_damage': None,  # État du véhicule
                'first_hand_vehicle': None,  # Première main
                'maintenance_booklet_available': None,  # Carnet d'entretien
                'vehicle_specifications': None,  # Équipements extérieurs
                'vehicle_interior_specs': None,  # Équipements intérieurs
                'vehicle_upholstery': None,  # Sellerie

                # INFORMATIONS VENDEUR
                'store_name': None,  # Nom du magasin
                'custom_ref': None,  # Référence annonce
                'owner_type': None,  # Professionnel ou particulier

                # MÉTADONNÉES
                'category_id': ad.category_id if hasattr(ad, 'category_id') else None,
                'category_name': ad.category_name if hasattr(ad, 'category_name') else None,
                'ad_type': ad.ad_type if hasattr(ad, 'ad_type') else None,
                'has_phone': ad.has_phone if hasattr(ad, 'has_phone') else None,
            }

            # Prix
            if hasattr(ad, 'price') and ad.price is not None:
                try:
                    data['price'] = int(ad.price)
                except (ValueError, TypeError):
                    pass

            # Images - Extraire TOUTES les images disponibles
            # Note: ad.images est une List[str] d'URLs (ou None si pas d'images)
            try:
                if hasattr(ad, 'images'):
                    logger.debug(f"   🔍 ad.images type: {type(ad.images)}, value: {ad.images}")

                    if ad.images and isinstance(ad.images, list) and len(ad.images) > 0:
                        data['images'] = ad.images  # Toutes les images
                        data['image_url'] = ad.images[0]  # Première image (compatibilité)
                        logger.debug(f"   ✅ {len(ad.images)} images extraites")
                    else:
                        logger.debug(f"   ⚠️ ad.images vide ou None")
                        data['images'] = []
                        data['image_url'] = None
                else:
                    logger.debug(f"   ⚠️ ad n'a pas d'attribut 'images'")
                    data['images'] = []
                    data['image_url'] = None
            except (IndexError, AttributeError, TypeError) as e:
                logger.error(f"   ❌ Erreur extraction images: {e}")
                import traceback
                traceback.print_exc()
                data['images'] = []
                data['image_url'] = None

            # Localisation complète
            if hasattr(ad, 'location') and ad.location:
                try:
                    location_parts = []
                    if hasattr(ad.location, 'city') and ad.location.city:
                        location_parts.append(ad.location.city)
                    if hasattr(ad.location, 'zipcode') and ad.location.zipcode:
                        location_parts.append(ad.location.zipcode)
                    if hasattr(ad.location, 'department_name') and ad.location.department_name:
                        location_parts.append(ad.location.department_name)
                    data['location'] = ', '.join(location_parts) if location_parts else None

                    # Stocker aussi les coordonnées GPS
                    if hasattr(ad.location, 'lat') and hasattr(ad.location, 'lng'):
                        data['latitude'] = ad.location.lat
                        data['longitude'] = ad.location.lng
                except AttributeError:
                    pass

            # EXTRACTION COMPLÈTE DE TOUS LES ATTRIBUTS
            # Note: ad.attributes est une LISTE d'objets Attribute, pas un dict
            if hasattr(ad, 'attributes') and ad.attributes:
                # DEBUG: Log tous les attributs du premier véhicule pour voir les champs disponibles
                if not hasattr(self, '_logged_attributes'):
                    self._logged_attributes = True
                    logger.debug(f"📋 ATTRIBUTS DISPONIBLES pour l'annonce '{data.get('title', '')}' :")
                    for attr in ad.attributes:
                        if attr.key:
                            val_label = attr.value_label if hasattr(attr, 'value_label') else None
                            logger.debug(f"  - {attr.key} = {attr.value} (label: {val_label})")

                for attr in ad.attributes:
                    if not attr.key or not attr.value:
                        continue

                    # Utiliser les mappings pour convertir les valeurs
                    value = str(attr.value)
                    value_label = attr.value_label if hasattr(attr, 'value_label') and attr.value_label else None

                    # MARQUE (brand / make)
                    if attr.key in ('brand', 'make', 'car_brand', 'regmarque'):
                        data['brand'] = value_label or value
                        data['make'] = value_label or value  # Aussi copier dans make

                    # MODÈLE (model)
                    elif attr.key in ('model', 'car_model'):
                        data['model'] = value_label or value

                    # ANNÉE (regdate)
                    elif attr.key == 'regdate':
                        try:
                            data['year'] = int(value)
                        except (ValueError, TypeError):
                            pass

                    # KILOMÉTRAGE (mileage)
                    elif attr.key == 'mileage':
                        try:
                            data['mileage'] = int(value)
                        except (ValueError, TypeError):
                            pass

                    # CARBURANT (fuel)
                    elif attr.key == 'fuel':
                        fuel_mapping = {
                            '1': 'essence',
                            '2': 'diesel',
                            '3': 'gpl',
                            '4': 'electrique',
                            '5': 'hybride',
                        }
                        data['fuel_type'] = fuel_mapping.get(value, value_label or value).lower()

                    # TRANSMISSION (gearbox)
                    elif attr.key == 'gearbox':
                        gearbox_mapping = {
                            '1': 'manuelle',
                            '2': 'automatique',
                        }
                        data['transmission'] = gearbox_mapping.get(value, value_label or value).lower()

                    # PORTES (doors)
                    elif attr.key == 'doors':
                        data['doors'] = value_label or value

                    # PLACES (seats)
                    elif attr.key == 'seats':
                        data['seats'] = value_label or value

                    # FINITION (u_car_finition)
                    elif attr.key == 'u_car_finition':
                        data['finition'] = value_label or value

                    # VERSION (u_car_version)
                    elif attr.key == 'u_car_version':
                        data['version'] = value_label or value

                    # TYPE DE VÉHICULE (vehicle_type)
                    elif attr.key == 'vehicle_type':
                        data['vehicle_type'] = value_label or value

                    # COULEUR (vehicule_color)
                    elif attr.key == 'vehicule_color':
                        data['color'] = value_label or value

                    # PUISSANCE FISCALE (horsepower)
                    elif attr.key == 'horsepower':
                        try:
                            data['horsepower'] = int(value)
                        except (ValueError, TypeError):
                            data['horsepower'] = value_label or value

                    # PUISSANCE DIN (horse_power_din)
                    elif attr.key == 'horse_power_din':
                        try:
                            data['horse_power_din'] = int(value)
                        except (ValueError, TypeError):
                            data['horse_power_din'] = value_label or value

                    # CRIT'AIR (critair)
                    elif attr.key == 'critair':
                        data['critair'] = value_label or value

                    # DATE DE MISE EN CIRCULATION (issuance_date)
                    elif attr.key == 'issuance_date':
                        data['issuance_date'] = value

                    # ÉTAT DU VÉHICULE (vehicle_damage)
                    elif attr.key == 'vehicle_damage':
                        data['vehicle_damage'] = value_label or value

                    # PREMIÈRE MAIN (first_hand_vehicle)
                    elif attr.key == 'first_hand_vehicle':
                        data['first_hand_vehicle'] = value == '1' or value.lower() == 'oui'

                    # CARNET D'ENTRETIEN (maintenance_booklet_available)
                    elif attr.key == 'maintenance_booklet_available':
                        data['maintenance_booklet_available'] = value == '1' or value.lower() == 'oui'

                    # ÉQUIPEMENTS EXTÉRIEURS (vehicle_specifications)
                    elif attr.key == 'vehicle_specifications':
                        # C'est une liste d'équipements, on stocke les labels
                        if hasattr(attr, 'values_label') and attr.values_label:
                            data['vehicle_specifications'] = attr.values_label
                        else:
                            data['vehicle_specifications'] = value_label or value

                    # ÉQUIPEMENTS INTÉRIEURS (vehicle_interior_specs)
                    elif attr.key == 'vehicle_interior_specs':
                        if hasattr(attr, 'values_label') and attr.values_label:
                            data['vehicle_interior_specs'] = attr.values_label
                        else:
                            data['vehicle_interior_specs'] = value_label or value

                    # SELLERIE (vehicle_upholstery)
                    elif attr.key == 'vehicle_upholstery':
                        data['vehicle_upholstery'] = value_label or value

                    # NOM DU MAGASIN (store_name)
                    elif attr.key == 'store_name':
                        data['store_name'] = value

                    # RÉFÉRENCE (custom_ref)
                    elif attr.key == 'custom_ref':
                        data['custom_ref'] = value

            # Type de vendeur (owner_type depuis l'ad ou via attribut)
            if hasattr(ad, 'ad_type'):
                data['owner_type'] = ad.ad_type

            # Si pas d'attributs critiques extraits, essayer d'extraire depuis le titre/description
            if not data['year'] or not data['mileage']:
                self._enrich_with_nlp(data)

            # Validation minimale
            if not data['title']:
                return None

            # Mapper 'brand' vers 'make' pour compatibilité avec base_scraper
            if data.get('brand') and not data.get('make'):
                data['make'] = data['brand']

            # DEBUG: Log pour vérifier l'extraction des champs
            if data.get('make') or data.get('brand'):
                logger.debug(f"✓ Véhicule extrait: make={data.get('make')}, model={data.get('model')}, title={data.get('title', '')[:50]}")
            else:
                logger.warning(f"⚠️ Véhicule SANS marque: title={data.get('title', '')[:50]}")

            return data

        except Exception as e:
            logger.error(f"Erreur parsing ad: {e}")
            import traceback
            traceback.print_exc()
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



# ============================================================================
# SCRIPT DE TEST
# ============================================================================
if __name__ == '__main__':
    # Activer DEBUG pour voir tous les détails de l'extraction (images, etc.)
    logging.basicConfig(
        level=logging.DEBUG,  # DEBUG pour voir les détails de l'extraction d'images
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 70)
    print("🧪 TEST LEBONCOIN SCRAPER - EXTRACTION COMPLÈTE")
    print("=" * 70)
    print()

    # EXEMPLE 1: Recherche de base
    print("📋 EXEMPLE 1: Recherche de base")
    test_params_basic = {
        'query': 'peugeot 208',
        'max_price': 15000,
        'max_pages': 1
    }
    print(f"   Paramètres: {test_params_basic}")
    print()

    # EXEMPLE 2: Recherche avec TOUS les filtres disponibles
    print("📋 EXEMPLE 2: Recherche avancée avec TOUS les filtres")
    test_params_advanced = {
        # Recherche de base
        'query': 'peugeot 208',
        'max_pages': 2,

        # Filtres de prix
        'min_price': 8000,
        'max_price': 15000,

        # Filtres véhicule
        'min_year': 2018,      # Année minimale: 2018
        'max_year': 2023,      # Année maximale: 2023
        'min_mileage': 0,      # Kilométrage min
        'max_mileage': 80000,  # Kilométrage max: 80 000 km

        # Filtres carburant et transmission
        'fuel_types': ['1', '4'],  # '1'=essence, '4'=électrique
        'transmissions': ['2'],     # '2'=automatique

        # Filtres caractéristiques
        'doors': ['5'],        # 5 portes
        'seats': ['5'],        # 5 places

        # Filtres puissance
        'min_horsepower': 5,   # Puissance fiscale min: 5 CV
        'max_horsepower': 8,   # Puissance fiscale max: 8 CV

        # Filtres état/équipement
        'first_hand': True,    # Première main uniquement
        'maintenance_booklet': True,  # Carnet d'entretien disponible

        # Filtre vendeur
        'owner_type': 'private',  # Particuliers uniquement
    }
    print(f"   Paramètres: {test_params_advanced}")
    print()

    # Choisir quel test exécuter
    print("🚀 Lancement du test de base...")
    print()

    scraper = LeBonCoinScraper()
    results = scraper.scrape(test_params_basic)

    print()
    print("=" * 70)
    print(f"📊 RÉSULTATS: {len(results)} annonces")
    print("=" * 70)
    print()

    if results:
        # Afficher les 3 premières annonces avec TOUTES les informations
        for i, result in enumerate(results[:3], 1):
            print(f"\n{'='*70}")
            print(f"ANNONCE {i}: {result.get('title', 'N/A')}")
            print(f"{'='*70}")

            # Informations principales
            print(f"\n📌 INFORMATIONS PRINCIPALES:")
            print(f"   Prix: {result.get('price', 'N/A')}€")
            print(f"   Année: {result.get('year', 'N/A')}")
            print(f"   Kilométrage: {result.get('mileage', 'N/A')} km")
            print(f"   Carburant: {result.get('fuel_type', 'N/A')}")
            print(f"   Transmission: {result.get('transmission', 'N/A')}")

            # Caractéristiques
            print(f"\n🚗 CARACTÉRISTIQUES:")
            print(f"   Marque: {result.get('brand', 'N/A')}")
            print(f"   Finition: {result.get('finition', 'N/A')}")
            print(f"   Version: {result.get('version', 'N/A')}")
            print(f"   Portes: {result.get('doors', 'N/A')}")
            print(f"   Places: {result.get('seats', 'N/A')}")
            print(f"   Couleur: {result.get('color', 'N/A')}")
            print(f"   Type véhicule: {result.get('vehicle_type', 'N/A')}")

            # Puissance
            print(f"\n⚡ PUISSANCE:")
            print(f"   CV fiscaux: {result.get('horsepower', 'N/A')}")
            print(f"   Puissance DIN: {result.get('horse_power_din', 'N/A')} ch")
            print(f"   Crit'Air: {result.get('critair', 'N/A')}")

            # État et équipements
            print(f"\n🔧 ÉTAT ET ÉQUIPEMENTS:")
            print(f"   État: {result.get('vehicle_damage', 'N/A')}")
            print(f"   Première main: {result.get('first_hand_vehicle', 'N/A')}")
            print(f"   Carnet d'entretien: {result.get('maintenance_booklet_available', 'N/A')}")
            print(f"   Équipements ext.: {result.get('vehicle_specifications', 'N/A')}")
            print(f"   Équipements int.: {result.get('vehicle_interior_specs', 'N/A')}")
            print(f"   Sellerie: {result.get('vehicle_upholstery', 'N/A')}")

            # Localisation
            print(f"\n📍 LOCALISATION:")
            print(f"   Lieu: {result.get('location', 'N/A')}")
            if result.get('latitude') and result.get('longitude'):
                print(f"   Coordonnées: {result.get('latitude')}, {result.get('longitude')}")

            # Dates
            print(f"\n📅 DATES:")
            print(f"   Publication: {result.get('first_publication_date', 'N/A')}")
            print(f"   Mise en circulation: {result.get('issuance_date', 'N/A')}")

            # Vendeur
            print(f"\n👤 VENDEUR:")
            print(f"   Type: {result.get('owner_type', 'N/A')}")
            print(f"   Magasin: {result.get('store_name', 'N/A')}")
            print(f"   Référence: {result.get('custom_ref', 'N/A')}")
            print(f"   Téléphone: {'Oui' if result.get('has_phone') else 'Non'}")

            # Liens et Images
            print(f"\n🔗 LIENS:")
            print(f"   URL: {result.get('url', 'N/A')}")

            # Afficher TOUTES les images
            images = result.get('images', [])
            if images:
                print(f"\n📸 IMAGES ({len(images)} au total):")
                for idx, img_url in enumerate(images[:5], 1):  # Afficher les 5 premières
                    print(f"   {idx}. {img_url}")
                if len(images) > 5:
                    print(f"   ... et {len(images) - 5} autres images")
            else:
                print(f"\n📸 IMAGES: Aucune image disponible")

        if len(results) > 3:
            print(f"\n... et {len(results) - 3} autres annonces")
    else:
        print("❌ Aucun résultat")
        print()
        print("💡 L'IP peut être temporairement bloquée par DataDome.")
        print("   Attendez quelques heures ou utilisez un proxy.")
