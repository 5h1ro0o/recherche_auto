# backend/scrapers/base_scraper.py - VERSION PRODUCTION ANTI-DÉTECTION AVANCÉE
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import random
import time
import logging
import os
import hashlib

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

# Gestion optionnelle de playwright-stealth
try:
    from playwright_stealth import stealth_sync
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    logger.warning("⚠️ playwright-stealth non disponible. Installez avec: pip install playwright-stealth")

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
    
    def init_browser(self, headless: bool = True, proxy: Optional[str] = None):
        """Initialise Playwright browser avec anti-détection avancé"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("❌ Playwright n'est pas installé. Exécutez: pip install playwright && playwright install chromium")
        
        try:
            # Sélectionner proxy si manager disponible
            if self.use_proxy and self.proxy_manager:
                proxy = proxy or self.proxy_manager.get_proxy()
                self.current_proxy = proxy
            
            self.playwright = sync_playwright().start()
            
            launch_options = {
                'headless': headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-infobars',
                    '--window-size=1920,1080',
                    '--start-maximized',
                    # Anti-détection supplémentaire
                    '--disable-blink-features=AutomationControlled',
                    '--exclude-switches=enable-automation',
                    '--disable-extensions'
                ]
            }

            # Ajouter proxy si configuré
            if proxy:
                launch_options['proxy'] = {
                    'server': proxy
                }
                logger.info(f"🔒 Utilisation du proxy: {proxy}")

            # Lancer le navigateur
            self.browser = self.playwright.chromium.launch(**launch_options)

            # Créer un contexte avec user-agent personnalisé
            context_options = {
                'user_agent': self.get_random_user_agent(),
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'fr-FR',
                'timezone_id': 'Europe/Paris',
            }

            context = self.browser.new_context(**context_options)

            # Injection de scripts anti-détection
            context.add_init_script("""
                // Masquer webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Masquer plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Masquer languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['fr-FR', 'fr', 'en-US', 'en']
                });
            """)

            self.page = context.new_page()

            # Appliquer stealth mode si disponible
            if STEALTH_AVAILABLE:
                stealth_sync(self.page)
                logger.info("🛡️ Mode stealth activé")

            logger.info(f"✅ Browser initialisé (headless={headless})")

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
            logger.debug("🔒 Browser fermé")
        except Exception as e:
            logger.warning(f"⚠️ Erreur fermeture browser: {e}")

    def simulate_human_behavior(self):
        """Simule un comportement humain sur la page"""
        if not self.page:
            return

        try:
            # Scroll aléatoire
            scroll_amount = random.randint(100, 500)
            self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            self.random_delay(0.3, 0.8)

            # Mouvement de souris aléatoire
            self.page.mouse.move(
                random.randint(100, 800),
                random.randint(100, 600)
            )
            self.random_delay(0.2, 0.5)

        except Exception as e:
            logger.debug(f"⚠️ Erreur simulation comportement: {e}")

    @abstractmethod
    def scrape(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Méthode abstraite à implémenter par chaque scraper

        Args:
            params: Dictionnaire de paramètres de recherche

        Returns:
            Liste de dictionnaires contenant les données extraites
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Retourne le nom de la source (ex: 'leboncoin', 'lacentrale')"""
        pass