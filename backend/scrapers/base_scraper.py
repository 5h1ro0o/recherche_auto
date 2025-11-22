# backend/scrapers/base_scraper.py - VERSION PRODUCTION ANTI-DÉTECTION AVANCÉE
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import random
import time
import logging
import os
import hashlib
import re

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
    Anti-détection avancé : proxies, fingerprinting, comportement humain
    """
    
    def __init__(self, use_proxy: bool = False, proxy_manager=None):
        self.use_proxy = use_proxy
        self.proxy_manager = proxy_manager
        self.current_proxy = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # User agents par défaut
        self.fallback_ua = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
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
        """Délai aléatoire entre requêtes avec variation"""
        delay = random.uniform(min_sec, max_sec)
        # Ajouter micro-variations pour plus de réalisme
        delay += random.uniform(-0.1, 0.1)
        logger.debug(f"⏱️ Attente {delay:.2f}s")
        time.sleep(max(0, delay))
    
    def human_like_delay(self):
        """Délai simulant comportement humain (lecture, réflexion)"""
        delay = random.choice([
            random.uniform(0.5, 1.5),   # Rapide
            random.uniform(2.0, 4.0),   # Normal
            random.uniform(5.0, 8.0),   # Lecture attentive
        ])
        self.random_delay(delay, delay + 0.5)
    
    def init_browser(self, headless: bool = True, proxy: Optional[str] = None, stealth_mode: bool = True):
        """Initialise Playwright browser avec anti-détection avancé"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("❌ Playwright n'est pas installé. Exécutez: pip install playwright && playwright install chromium")

        try:
            # Sélectionner proxy si manager disponible
            if self.use_proxy and self.proxy_manager:
                proxy = proxy or self.proxy_manager.get_proxy()
                self.current_proxy = proxy

            self.playwright = sync_playwright().start()

            # Arguments Chrome pour anti-détection max
            chrome_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--start-maximized',
                '--exclude-switches=enable-automation',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--safebrowsing-disable-auto-update',
                '--enable-automation=false',
                '--password-store=basic',
                '--use-mock-keychain',
                '--no-first-run',
                '--no-service-autorun',
                '--mute-audio',
            ]

            # Ajouter user-data-dir pour persistance (contourne certaines détections)
            if stealth_mode:
                import tempfile
                user_data_dir = tempfile.mkdtemp()
                chrome_args.append(f'--user-data-dir={user_data_dir}')

            launch_options = {
                'headless': headless,
                'args': chrome_args,
                'chromium_sandbox': False,
            }

            # Ajouter proxy si configuré
            if proxy:
                launch_options['proxy'] = {
                    'server': proxy
                }

            self.browser = self.playwright.chromium.launch(**launch_options)

            # Context avec anti-fingerprinting et headers réalistes
            context_options = {
                'user_agent': self.get_random_user_agent(),
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'fr-FR',
                'timezone_id': 'Europe/Paris',
                'permissions': ['geolocation'],
                'geolocation': {'latitude': 48.8566, 'longitude': 2.3522},  # Paris
                'extra_http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                }
            }

            context = self.browser.new_context(**context_options)

            # Injecter scripts anti-détection AVANCÉS
            context.add_init_script("""
                // Masquer webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Faux plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        }
                    ]
                });

                // Languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['fr-FR', 'fr', 'en-US', 'en']
                });

                // Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Chrome runtime
                window.chrome = {
                    runtime: {}
                };

                // Platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });

                // HardwareConcurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });

                // DeviceMemory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
            """)

            self.page = context.new_page()

            logger.info("✅ Browser Playwright initialisé avec succès")

        except Exception as e:
            logger.error(f"❌ Erreur init browser: {e}")
            self.close_browser()
            raise

    def close_browser(self):
        """Ferme proprement le browser"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("✅ Browser fermé")
        except Exception as e:
            logger.warning(f"⚠️ Erreur fermeture browser: {e}")

    @abstractmethod
    def get_source_name(self) -> str:
        """Retourne le nom de la source (ex: 'leboncoin', 'lacentrale')"""
        pass

    @abstractmethod
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Méthode principale de scraping
        Doit retourner une liste de dictionnaires normalisés
        """
        pass

    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise les données scrapées"""
        return {
            'source_ids': {self.get_source_name(): raw_data.get('id')},
            'title': raw_data.get('title', ''),
            'make': raw_data.get('make'),
            'model': raw_data.get('model'),
            'price': self._normalize_price(raw_data.get('price')),
            'year': self._normalize_year(raw_data.get('year')),
            'mileage': self._normalize_mileage(raw_data.get('mileage')),
            'fuel_type': raw_data.get('fuel_type'),
            'transmission': raw_data.get('transmission'),
            'location_city': raw_data.get('location'),
            'url': raw_data.get('url'),
            'images': raw_data.get('images', [])
        }

    def _normalize_price(self, price: Any) -> Optional[int]:
        """Normalise le prix en entier"""
        if price is None:
            return None
        try:
            price_str = str(price).replace(' ', '').replace('€', '').replace(',', '.')
            return int(float(re.sub(r'[^\d.]', '', price_str)))
        except:
            return None

    def _normalize_year(self, year: Any) -> Optional[int]:
        """Normalise l'année"""
        if year is None:
            return None
        try:
            return int(re.sub(r'[^\d]', '', str(year)))
        except:
            return None

    def _normalize_mileage(self, mileage: Any) -> Optional[int]:
        """Normalise le kilométrage"""
        if mileage is None:
            return None
        try:
            mileage_str = str(mileage).replace(' ', '').replace('km', '').replace(',', '')
            return int(re.sub(r'[^\d]', '', mileage_str))
        except:
            return None