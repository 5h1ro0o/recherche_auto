# backend/scrapers/base_scraper.py - VERSION PRODUCTION AMÉLIORÉE
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import random
import time
import logging
import os

logger = logging.getLogger(__name__)

# Gestion optionnelle de Playwright
try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ Playwright non disponible. Installez avec: pip install playwright && playwright install chromium")

# Gestion optionnelle de fake_useragent
try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False
    logger.warning("⚠️ fake_useragent non disponible. Installez avec: pip install fake-useragent")

class BaseScraper(ABC):
    """
    Classe abstraite pour tous les scrapers
    Gère Playwright, anti-détection, proxies, delays
    """
    
    def __init__(self, use_proxy: bool = False):
        self.use_proxy = use_proxy
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # User agents par défaut si fake_useragent indisponible
        self.fallback_ua = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        if FAKE_UA_AVAILABLE:
            try:
                self.ua = UserAgent()
            except Exception as e:
                logger.warning(f"Erreur init UserAgent: {e}, utilisation fallback")
                self.ua = None
        else:
            self.ua = None
    
    def get_random_user_agent(self) -> str:
        """User-Agent aléatoire"""
        if self.ua and FAKE_UA_AVAILABLE:
            try:
                return self.ua.random
            except:
                pass
        return random.choice(self.fallback_ua)
    
    def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Délai aléatoire entre requêtes"""
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"⏱️ Attente {delay:.2f}s")
        time.sleep(delay)
    
    def init_browser(self, headless: bool = True, proxy: Optional[str] = None):
        """Initialise Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("❌ Playwright n'est pas installé. Exécutez: pip install playwright && playwright install chromium")
        
        try:
            self.playwright = sync_playwright().start()
            
            launch_options = {
                'headless': headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                ]
            }
            
            if proxy and self.use_proxy:
                launch_options['proxy'] = {'server': proxy}
                logger.info(f"🌐 Utilisation proxy: {proxy}")
            
            self.browser = self.playwright.chromium.launch(**launch_options)
            
            context = self.browser.new_context(
                user_agent=self.get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080},
                locale='fr-FR',
                timezone_id='Europe/Paris',
                permissions=['geolocation'],
                geolocation={'latitude': 48.8566, 'longitude': 2.3522}  # Paris
            )
            
            # Scripts anti-détection avancés
            context.add_init_script("""
                // Supprimer webdriver flag
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Simuler plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Simuler languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['fr-FR', 'fr', 'en-US', 'en']
                });
                
                // Chrome présent
                window.chrome = { runtime: {} };
                
                // Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.page = context.new_page()
            
            # Bloquer ressources inutiles pour accélérer
            self.page.route("**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf,eot}", lambda route: route.abort())
            
            logger.info(f"✅ Browser initialisé pour {self.__class__.__name__}")
            
        except Exception as e:
            logger.error(f"❌ Erreur init browser: {e}")
            raise
    
    def close_browser(self):
        """Ferme le browser proprement"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("🔒 Browser fermé")
        except Exception as e:
            logger.warning(f"⚠️ Erreur fermeture browser: {e}")
    
    @abstractmethod
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Méthode principale de scraping (à implémenter)"""
        pass
    
    @abstractmethod
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse un élément de listing (à implémenter)"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Retourne le nom de la source"""
        pass
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise les données pour le format unifié
        Compatible avec le worker backend/app/worker.py
        """
        return {
            'source': self.get_source_name(),
            'source_id': raw_data.get('id') or raw_data.get('source_id'),
            'title': (raw_data.get('title') or '').strip(),
            'make': raw_data.get('make'),
            'model': raw_data.get('model'),
            'price': self._parse_price(raw_data.get('price')),
            'year': self._parse_year(raw_data.get('year')),
            'mileage': self._parse_mileage(raw_data.get('mileage')),
            'fuel_type': raw_data.get('fuel_type'),
            'transmission': raw_data.get('transmission'),
            'images': raw_data.get('images', []),
            'url': raw_data.get('url'),
            'location_city': raw_data.get('location'),
            'lat': raw_data.get('lat'),
            'lon': raw_data.get('lon'),
            'posted_date': raw_data.get('posted_date')
        }
    
    # ============ HELPERS DE PARSING ============
    
    def _parse_price(self, price_str: Optional[str]) -> Optional[int]:
        """Parse un prix (ex: "15 000 €" -> 15000)"""
        if not price_str:
            return None
        try:
            # Enlever tous les caractères non numériques
            clean = ''.join(filter(str.isdigit, str(price_str)))
            return int(clean) if clean else None
        except:
            return None
    
    def _parse_year(self, year_str: Optional[str]) -> Optional[int]:
        """Parse une année"""
        if not year_str:
            return None
        try:
            clean = ''.join(filter(str.isdigit, str(year_str)))
            year = int(clean) if clean else None
            # Validation (années réalistes)
            if year and 1980 <= year <= 2030:
                return year
            return None
        except:
            return None
    
    def _parse_mileage(self, mileage_str: Optional[str]) -> Optional[int]:
        """Parse un kilométrage"""
        if not mileage_str:
            return None
        try:
            clean = ''.join(filter(str.isdigit, str(mileage_str)))
            return int(clean) if clean else None
        except:
            return None
    
    def safe_get_text(self, element, selector: str, default: str = "") -> str:
        """Récupère texte d'un élément de façon safe"""
        try:
            el = element.query_selector(selector)
            return el.inner_text().strip() if el else default
        except:
            return default
    
    def safe_get_attribute(self, element, selector: str, attribute: str, default: str = "") -> str:
        """Récupère attribut d'un élément de façon safe"""
        try:
            el = element.query_selector(selector)
            return el.get_attribute(attribute) if el else default
        except:
            return default
    
    def extract_make_model_from_title(self, title: str) -> tuple:
        """
        Extrait marque/modèle du titre (logique basique)
        À améliorer avec ML/NLP pour meilleure précision
        """
        # Liste des marques courantes
        makes = [
            'Peugeot', 'Renault', 'Citroën', 'Volkswagen', 'BMW', 
            'Mercedes', 'Audi', 'Ford', 'Toyota', 'Honda', 'Nissan',
            'Opel', 'Fiat', 'Seat', 'Skoda', 'Hyundai', 'Kia',
            'Mazda', 'Volvo', 'Porsche', 'Tesla', 'Dacia'
        ]
        
        title_lower = title.lower()
        
        for make in makes:
            if make.lower() in title_lower:
                # Essayer d'extraire le modèle (mot après la marque)
                parts = title.split()
                try:
                    make_idx = [p.lower() for p in parts].index(make.lower())
                    if make_idx + 1 < len(parts):
                        model = parts[make_idx + 1]
                        # Nettoyer le modèle
                        model = model.strip('.,;:()[]{}')
                        return make, model
                except:
                    pass
                return make, None
        
        return None, None
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fermeture automatique du browser"""
        self.close_browser()