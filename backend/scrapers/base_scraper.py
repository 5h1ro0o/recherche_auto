from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page
from fake_useragent import UserAgent
import random
import time
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Classe abstraite pour tous les scrapers"""
    
    def __init__(self, use_proxy: bool = False):
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def get_random_user_agent(self) -> str:
        """User-Agent aléatoire"""
        return self.ua.random
    
    def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Délai aléatoire entre requêtes"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def init_browser(self, headless: bool = True, proxy: Optional[str] = None):
        """Initialise Playwright browser"""
        playwright = sync_playwright().start()
        
        launch_options = {
            'headless': headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        }
        
        if proxy and self.use_proxy:
            launch_options['proxy'] = {
                'server': proxy
            }
        
        self.browser = playwright.chromium.launch(**launch_options)
        
        context = self.browser.new_context(
            user_agent=self.get_random_user_agent(),
            viewport={'width': 1920, 'height': 1080},
            locale='fr-FR',
            timezone_id='Europe/Paris'
        )
        
        # Anti-détection scripts
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = context.new_page()
        logger.info(f"Browser initialized for {self.__class__.__name__}")
    
    def close_browser(self):
        """Ferme le browser"""
        if self.browser:
            self.browser.close()
            logger.info("Browser closed")
    
    @abstractmethod
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Méthode principale de scraping (à implémenter)"""
        pass
    
    @abstractmethod
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse un élément de listing (à implémenter)"""
        pass
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise les données pour le format unifié"""
        return {
            'source': self.get_source_name(),
            'source_id': raw_data.get('id'),
            'title': raw_data.get('title', '').strip(),
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
            'posted_date': raw_data.get('posted_date')
        }
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Retourne le nom de la source"""
        pass
    
    # Helpers de parsing
    def _parse_price(self, price_str: Optional[str]) -> Optional[int]:
        """Parse un prix (ex: "15 000 €" -> 15000)"""
        if not price_str:
            return None
        try:
            return int(''.join(filter(str.isdigit, str(price_str))))
        except:
            return None
    
    def _parse_year(self, year_str: Optional[str]) -> Optional[int]:
        """Parse une année"""
        if not year_str:
            return None
        try:
            return int(''.join(filter(str.isdigit, str(year_str))))
        except:
            return None
    
    def _parse_mileage(self, mileage_str: Optional[str]) -> Optional[int]:
        """Parse un kilométrage"""
        if not mileage_str:
            return None
        try:
            return int(''.join(filter(str.isdigit, str(mileage_str))))
        except:
            return None