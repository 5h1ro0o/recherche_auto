# backend/scrapers/leboncoin_scraper.py - VERSION PRODUCTION AVANCÉE
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LeBonCoinScraper(BaseScraper):
    """
    Scraper avancé pour LeBonCoin (leboncoin.fr)
    Extraction complète : photos, description, contact, GPS, etc.
    """
    
    BASE_URL = "https://www.leboncoin.fr"
    SEARCH_URL = f"{BASE_URL}/recherche?category=2&text={{query}}"
    
    # Mapping des marques courantes pour extraction NLP
    BRAND_MAPPING = {
        'peugeot': 'Peugeot', 'renault': 'Renault', 'citroën': 'Citroën', 'citroen': 'Citroën',
        'volkswagen': 'Volkswagen', 'vw': 'Volkswagen', 'bmw': 'BMW', 'mercedes': 'Mercedes-Benz',
        'audi': 'Audi', 'ford': 'Ford', 'toyota': 'Toyota', 'honda': 'Honda', 'nissan': 'Nissan',
        'opel': 'Opel', 'fiat': 'Fiat', 'seat': 'Seat', 'skoda': 'Skoda', 'hyundai': 'Hyundai',
        'kia': 'Kia', 'mazda': 'Mazda', 'volvo': 'Volvo', 'porsche': 'Porsche', 'tesla': 'Tesla',
        'dacia': 'Dacia', 'mini': 'Mini', 'alfa romeo': 'Alfa Romeo', 'jeep': 'Jeep',
        'land rover': 'Land Rover', 'jaguar': 'Jaguar', 'lexus': 'Lexus', 'infiniti': 'Infiniti'
    }
    
    # Patterns pour extraction carburant
    FUEL_PATTERNS = {
        r'\bess(?:ence)?\b': 'essence',
        r'\bdiesel\b': 'diesel',
        r'\bélectrique\b': 'electrique',
        r'\belectric\b': 'electrique',
        r'\bhybride\b': 'hybride',
        r'\bgpl\b': 'gpl',
        r'\bethanol\b': 'ethanol'
    }
    
    # Patterns pour transmission
    TRANSMISSION_PATTERNS = {
        r'\bmanuelle\b': 'manuelle',
        r'\bmanual\b': 'manuelle',
        r'\bauto(?:matique)?\b': 'automatique',
        r'\bséquentielle\b': 'sequentielle'
    }
    
    def get_source_name(self) -> str:
        return "leboncoin"
    
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LeBonCoin avec extraction complète
        
        search_params:
            - query: str (ex: 'volkswagen golf')
            - max_price: int (optionnel)
            - max_pages: int (défaut: 5)
            - location: str (optionnel)
            - deep_scrape: bool (défaut: True) - Extraire détails complets
        """
        query = search_params.get('query', 'voiture')
        max_price = search_params.get('max_price')
        max_pages = search_params.get('max_pages', 5)
        location = search_params.get('location')
        deep_scrape = search_params.get('deep_scrape', True)
        
        results = []
        retry_count = 0
        max_retries = 3
        
        try:
            self.init_browser(headless=True)
            
            logger.info(f"🔵 LeBonCoin: Recherche '{query}' sur {max_pages} pages (deep={deep_scrape})")
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"📄 Page {page_num}/{max_pages}")
                
                # Construire URL
                url = self._build_search_url(query, page_num, max_price, location)
                
                # Navigation avec retry
                page_loaded = False
                for attempt in range(max_retries):
                    try:
                        self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        self.random_delay(2, 4)
                        
                        # Détecter captcha
                        if self._detect_captcha():
                            logger.warning("🤖 Captcha détecté! Pause de 60s...")
                            self.random_delay(60, 90)
                            continue
                        
                        page_loaded = True
                        break
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée: {e}")
                        self.random_delay(5, 10)
                
                if not page_loaded:
                    logger.error(f"❌ Impossible de charger page {page_num}, skip")
                    continue
                
                # Attendre que la page charge complètement (LeBonCoin est lent)
                self.random_delay(3, 5)

                # Attendre les annonces avec plusieurs sélecteurs possibles
                listings = []
                selectors = [
                    '[data-qa-id="aditem_container"]',  # Ancien sélecteur
                    'article[data-qa-id]',  # Article avec data-qa-id
                    'div[data-qa-id*="ad"]',  # Div avec data-qa-id contenant "ad"
                    'a[href*="/ad/"]',  # Liens vers annonces
                    'a[href*="voitures"]',  # Liens vers voitures
                    'article',  # Tous les articles (générique)
                    'li[data-qa-id]',  # Liste d'éléments avec data-qa-id
                ]

                for selector in selectors:
                    try:
                        self.page.wait_for_selector(selector, timeout=8000)
                        elements = self.page.query_selector_all(selector)

                        # Filtrer pour ne garder que les liens d'annonces
                        if selector in ['article', 'li[data-qa-id]', 'div[data-qa-id*="ad"]']:
                            # Vérifier que l'élément contient un lien vers une annonce
                            listings = [el for el in elements if el.query_selector('a[href*="/ad/"]') or el.query_selector('a[href*="voitures"]')]
                        elif selector == 'a[href*="/ad/"]' or selector == 'a[href*="voitures"]':
                            # Ne garder que les liens qui semblent être des annonces (pas footer, header, etc.)
                            listings = [el for el in elements if 'footer' not in (el.get_attribute('class') or '').lower()]
                        else:
                            listings = elements

                        if listings and len(listings) > 5:  # Au moins 5 éléments pour être sûr
                            logger.info(f"✅ Trouvé {len(listings)} annonces avec sélecteur: {selector}")
                            break
                        elif listings:
                            logger.debug(f"Sélecteur '{selector}': {len(listings)} éléments (trop peu)")
                    except Exception as e:
                        logger.debug(f"Sélecteur '{selector}' non trouvé: {e}")
                        continue

                if not listings or len(listings) == 0:
                    logger.warning(f"⚠️ Aucune annonce trouvée page {page_num} avec tous les sélecteurs")
                    # Sauvegarder la page HTML pour debug
                    try:
                        html_content = self.page.content()
                        with open(f'leboncoin_page{page_num}_debug.html', 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        logger.info(f"💾 Page HTML sauvegardée: leboncoin_page{page_num}_debug.html")
                    except:
                        pass
                    break

                logger.info(f"📊 Traitement de {len(listings)} éléments...")

                for idx, listing in enumerate(listings, 1):
                    try:
                        # Extraction basique (liste)
                        parsed = self.parse_listing(listing)
                        
                        if not parsed or not parsed.get('id'):
                            logger.debug(f"  ✗ Annonce {idx}: Données invalides")
                            continue
                        
                        # Extraction détaillée (page annonce)
                        if deep_scrape and parsed.get('url'):
                            detailed = self._scrape_detail_page(parsed['url'])
                            if detailed:
                                parsed.update(detailed)
                        
                        # Normalisation + enrichissement
                        normalized = self.normalize_and_enrich(parsed)
                        results.append(normalized)
                        
                        logger.debug(f"  ✓ Annonce {idx}: {normalized.get('title', 'N/A')[:50]}")
                        
                    except Exception as e:
                        logger.warning(f"  ✗ Erreur annonce {idx}: {e}")
                
                # Délai entre pages
                if page_num < max_pages:
                    self.random_delay(3, 6)
            
            logger.info(f"🎉 LeBonCoin terminé: {len(results)} annonces récupérées")
            
        except Exception as e:
            logger.exception(f"❌ Erreur critique LeBonCoin: {e}")
        finally:
            self.close_browser()
        
        return results
    
    def _build_search_url(self, query: str, page: int, max_price: Optional[int], location: Optional[str]) -> str:
        """Construit l'URL de recherche"""
        url = self.SEARCH_URL.format(query=query.replace(' ', '%20'))
        
        if page > 1:
            url += f"&page={page}"
        if max_price:
            url += f"&price=0-{max_price}"
        if location:
            url += f"&location={location}"
        
        return url
    
    def _detect_captcha(self) -> bool:
        """Détecte la présence d'un captcha"""
        try:
            # LeBonCoin utilise souvent reCAPTCHA
            captcha_selectors = [
                '.g-recaptcha',
                '#recaptcha',
                'iframe[src*="recaptcha"]',
                '[data-sitekey]'
            ]
            
            for selector in captcha_selectors:
                if self.page.query_selector(selector):
                    return True
            
            # Détecter dans le titre
            title = self.page.title().lower()
            if 'captcha' in title or 'robot' in title:
                return True
                
        except:
            pass
        
        return False
    
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse un élément de listing (vue liste)"""
        try:
            # ID et URL
            link_elem = element.query_selector('a[href*="/voitures/"]')
            url = link_elem.get_attribute('href') if link_elem else None
            
            if not url:
                return None
            
            # Extraire ID
            source_id = url.split('/')[-1].split('.htm')[0] if '/' in url else None
            if not source_id:
                return None
            
            # Titre
            title = self.safe_get_text(element, '[data-qa-id="aditem_title"]')
            
            # Prix
            price_text = self.safe_get_text(element, '[data-qa-id="aditem_price"]')
            
            # Localisation
            location = self.safe_get_text(element, '[data-qa-id="aditem_location"]')
            
            # Image principale
            img_elem = element.query_selector('img[alt]')
            img_url = img_elem.get_attribute('src') if img_elem else None
            
            # Date
            date_text = self.safe_get_text(element, '[data-qa-id="aditem_date"]')
            posted_date = self._parse_relative_date(date_text)
            
            # URL complète
            full_url = f"{self.BASE_URL}{url}" if url and not url.startswith('http') else url
            
            return {
                'id': source_id,
                'title': title,
                'price': price_text,
                'location': location,
                'images': [img_url] if img_url and img_url.startswith('http') else [],
                'url': full_url,
                'posted_date': posted_date,
            }
            
        except Exception as e:
            logger.debug(f"Erreur parse_listing: {e}")
            return None
    
    def _scrape_detail_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape la page détail d'une annonce
        Extrait : description, toutes les photos, téléphone, specs, GPS
        """
        try:
            logger.debug(f"  🔍 Scraping détails: {url}")
            
            # Navigation
            self.page.goto(url, wait_until='domcontentloaded', timeout=20000)
            self.random_delay(1, 2)
            
            # Captcha check
            if self._detect_captcha():
                logger.warning("  🤖 Captcha sur page détail, skip")
                return None
            
            details = {}
            
            # Description complète
            description = self.safe_get_text(self.page, '[data-qa-id="adview_description_container"]')
            if description:
                details['description'] = description
            
            # Toutes les photos
            images = []
            img_elements = self.page.query_selector_all('[data-qa-id="slideshow_container"] img')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and src.startswith('http') and 'placeholder' not in src:
                    images.append(src)
            
            if images:
                details['images'] = images
            
            # Specs techniques (dans les propriétés)
            specs = self._extract_specs()
            if specs:
                details.update(specs)
            
            # Localisation GPS
            gps = self._extract_gps()
            if gps:
                details.update(gps)
            
            # Téléphone (si visible)
            phone = self._extract_phone()
            if phone:
                details['phone'] = phone
            
            # Type vendeur
            seller_type = self._extract_seller_type()
            if seller_type:
                details['seller_type'] = seller_type
            
            return details
            
        except Exception as e:
            logger.debug(f"  ✗ Erreur scraping détail: {e}")
            return None
    
    def _extract_specs(self) -> Dict[str, Any]:
        """Extrait les specs techniques depuis la page détail"""
        specs = {}
        
        try:
            # LeBonCoin affiche les specs dans une liste
            prop_elements = self.page.query_selector_all('[data-qa-id="criteria_item"]')
            
            for prop in prop_elements:
                label = self.safe_get_text(prop, '[data-qa-id="criteria_item_key"]').lower()
                value = self.safe_get_text(prop, '[data-qa-id="criteria_item_value"]')
                
                # Mapping des propriétés
                if 'année' in label or 'modèle' in label:
                    year = self._parse_year(value)
                    if year:
                        specs['year'] = year
                
                elif 'kilométrage' in label or 'km' in label:
                    mileage = self._parse_mileage(value)
                    if mileage:
                        specs['mileage'] = mileage
                
                elif 'carburant' in label:
                    specs['fuel_type'] = self._normalize_fuel(value)
                
                elif 'boîte' in label or 'transmission' in label:
                    specs['transmission'] = self._normalize_transmission(value)
                
                elif 'puissance' in label:
                    specs['horsepower'] = value
                
                elif 'portes' in label:
                    specs['doors'] = value
        
        except Exception as e:
            logger.debug(f"Erreur extraction specs: {e}")
        
        return specs
    
    def _extract_gps(self) -> Optional[Dict[str, float]]:
        """Extrait coordonnées GPS si disponibles"""
        try:
            # LeBonCoin peut afficher une carte
            map_elem = self.page.query_selector('[data-qa-id="adview_location_map"]')
            
            if map_elem:
                # Chercher dans les attributs data-
                lat = map_elem.get_attribute('data-lat')
                lon = map_elem.get_attribute('data-lon')
                
                if lat and lon:
                    return {
                        'lat': float(lat),
                        'lon': float(lon)
                    }
        
        except Exception as e:
            logger.debug(f"Erreur extraction GPS: {e}")
        
        return None
    
    def _extract_phone(self) -> Optional[str]:
        """Tente d'extraire le numéro de téléphone"""
        try:
            # Cliquer sur "Voir le numéro" si présent
            phone_btn = self.page.query_selector('[data-qa-id="adview_phone_container"] button')
            
            if phone_btn:
                phone_btn.click()
                self.random_delay(1, 2)
                
                # Récupérer le numéro affiché
                phone_text = self.safe_get_text(self.page, '[data-qa-id="adview_phone_number"]')
                
                if phone_text:
                    # Nettoyer le numéro
                    phone = re.sub(r'[^\d+]', '', phone_text)
                    return phone if len(phone) >= 10 else None
        
        except Exception as e:
            logger.debug(f"Erreur extraction téléphone: {e}")
        
        return None
    
    def _extract_seller_type(self) -> Optional[str]:
        """Détermine si vendeur Pro ou Particulier"""
        try:
            seller_text = self.safe_get_text(self.page, '[data-qa-id="adview_profile_container"]').lower()
            
            if 'professionnel' in seller_text or 'pro' in seller_text:
                return 'professional'
            elif 'particulier' in seller_text:
                return 'particular'
        
        except:
            pass
        
        return None
    
    def normalize_and_enrich(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise et enrichit les données avec NLP
        """
        # Normalisation de base
        normalized = self.normalize_data(raw_data)
        
        # Enrichissement NLP
        title = normalized.get('title', '')
        description = raw_data.get('description', '')
        full_text = f"{title} {description}".lower()
        
        # Extraction marque/modèle si manquants
        if not normalized.get('make'):
            make, model = self._extract_make_model_nlp(title)
            if make:
                normalized['make'] = make
            if model:
                normalized['model'] = model
        
        # Extraction carburant si manquant
        if not normalized.get('fuel_type'):
            fuel = self._extract_fuel_from_text(full_text)
            if fuel:
                normalized['fuel_type'] = fuel
        
        # Extraction transmission si manquante
        if not normalized.get('transmission'):
            transmission = self._extract_transmission_from_text(full_text)
            if transmission:
                normalized['transmission'] = transmission
        
        # Extraction année si manquante
        if not normalized.get('year'):
            year = self._extract_year_from_text(full_text)
            if year:
                normalized['year'] = year
        
        return normalized
    
    def _extract_make_model_nlp(self, title: str) -> tuple:
        """Extraction marque/modèle via NLP basique"""
        title_lower = title.lower()
        
        # Chercher la marque
        for brand_key, brand_name in self.BRAND_MAPPING.items():
            if brand_key in title_lower:
                # Extraire le modèle (mot suivant la marque)
                pattern = rf'\b{re.escape(brand_key)}\s+([A-Za-z0-9\-]+)'
                match = re.search(pattern, title_lower)
                
                if match:
                    model = match.group(1).upper()
                    return brand_name, model
                
                return brand_name, None
        
        return None, None
    
    def _extract_fuel_from_text(self, text: str) -> Optional[str]:
        """Extrait le type de carburant du texte"""
        for pattern, fuel_type in self.FUEL_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return fuel_type
        return None
    
    def _extract_transmission_from_text(self, text: str) -> Optional[str]:
        """Extrait la transmission du texte"""
        for pattern, trans_type in self.TRANSMISSION_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return trans_type
        return None
    
    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extrait l'année du texte"""
        # Chercher un pattern d'année (4 chiffres entre 1980 et 2030)
        years = re.findall(r'\b(19[89]\d|20[0-3]\d)\b', text)
        
        if years:
            # Prendre la première année trouvée
            return int(years[0])
        
        return None
    
    def _parse_relative_date(self, date_text: str) -> Optional[str]:
        """Parse les dates relatives (ex: 'Il y a 2 jours')"""
        if not date_text:
            return None
        
        try:
            date_text = date_text.lower()
            now = datetime.utcnow()
            
            if 'aujourd' in date_text or 'instant' in date_text:
                return now.isoformat()
            
            elif 'hier' in date_text:
                return (now - timedelta(days=1)).isoformat()
            
            elif 'jour' in date_text:
                match = re.search(r'(\d+)\s*jour', date_text)
                if match:
                    days = int(match.group(1))
                    return (now - timedelta(days=days)).isoformat()
            
            elif 'heure' in date_text:
                match = re.search(r'(\d+)\s*heure', date_text)
                if match:
                    hours = int(match.group(1))
                    return (now - timedelta(hours=hours)).isoformat()
            
            elif 'semaine' in date_text:
                match = re.search(r'(\d+)\s*semaine', date_text)
                if match:
                    weeks = int(match.group(1))
                    return (now - timedelta(weeks=weeks)).isoformat()
        
        except Exception as e:
            logger.debug(f"Erreur parse date: {e}")
        
        return None
    
    def _normalize_fuel(self, fuel_text: str) -> str:
        """Normalise le type de carburant"""
        fuel_lower = fuel_text.lower()
        
        for pattern, fuel_type in self.FUEL_PATTERNS.items():
            if re.search(pattern, fuel_lower):
                return fuel_type
        
        return fuel_text
    
    def _normalize_transmission(self, trans_text: str) -> str:
        """Normalise la transmission"""
        trans_lower = trans_text.lower()
        
        for pattern, trans_type in self.TRANSMISSION_PATTERNS.items():
            if re.search(pattern, trans_lower):
                return trans_type
        
        return trans_text


# ============ FONCTION DE TEST ============

def test_leboncoin_advanced():
    """Test du scraper LeBonCoin avancé"""
    import json
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("🧪 TEST LEBONCOIN SCRAPER AVANCÉ")
    print("="*70)
    
    scraper = LeBonCoinScraper()
    
    search_params = {
        'query': 'peugeot 208',
        'max_price': 15000,
        'max_pages': 2,
        'deep_scrape': True  # Extraction complète
    }
    
    print(f"\n📋 Paramètres: {json.dumps(search_params, indent=2, ensure_ascii=False)}")
    print("\n🚀 Lancement du scraping avancé...\n")
    
    results = scraper.scrape(search_params)
    
    print("\n" + "="*70)
    print(f"📊 RÉSULTATS: {len(results)} annonces")
    print("="*70)
    
    if results:
        print(f"\n✨ Exemple détaillé (première annonce):")
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
        
        # Statistiques
        with_description = sum(1 for r in results if r.get('description'))
        with_multiple_images = sum(1 for r in results if len(r.get('images', [])) > 1)
        with_gps = sum(1 for r in results if r.get('lat') and r.get('lon'))
        with_phone = sum(1 for r in results if r.get('phone'))
        
        print(f"\n📈 STATISTIQUES:")
        print(f"  - Avec description: {with_description}/{len(results)}")
        print(f"  - Avec plusieurs photos: {with_multiple_images}/{len(results)}")
        print(f"  - Avec GPS: {with_gps}/{len(results)}")
        print(f"  - Avec téléphone: {with_phone}/{len(results)}")


if __name__ == "__main__":
    test_leboncoin_advanced()