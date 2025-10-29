# backend/debug_scrapers.py
"""
Script de débogage pour visualiser la structure HTML des sites
et trouver les bons sélecteurs CSS
"""
import logging
from scrapers.base_scraper import BaseScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebugScraper(BaseScraper):
    """Scraper de débogage pour inspecter la structure HTML"""

    def get_source_name(self):
        return "debug"

    def scrape(self, search_params):
        return []

    def inspect_page(self, url: str):
        """Inspecte une page et affiche sa structure"""
        try:
            self.init_browser(headless=False)  # Mode visible pour debug

            logger.info(f"📍 Chargement de: {url}")
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            self.random_delay(3, 5)

            # Afficher le HTML
            html = self.page.content()
            logger.info(f"📄 HTML de la page (premiers 2000 caractères):")
            print("="*80)
            print(html[:2000])
            print("="*80)

            # Essayer de trouver les éléments avec différents sélecteurs
            logger.info("\n🔍 Test des sélecteurs...")

            selectors_to_test = [
                'article',
                'div',
                'a[href*="voitures"]',
                'a[href*="auto"]',
                'a[href*="ad"]',
                '[data-qa-id]',
                '[class*="card"]',
                '[class*="item"]',
                '[class*="listing"]',
                '[class*="ad"]',
            ]

            for selector in selectors_to_test:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        print(f"✅ {selector}: {len(elements)} éléments trouvés")

                        # Afficher le HTML du premier élément
                        if elements:
                            first_elem_html = elements[0].inner_html()[:300]
                            print(f"   Premier élément: {first_elem_html}...")
                    else:
                        print(f"❌ {selector}: 0 éléments")
                except Exception as e:
                    print(f"⚠️ {selector}: Erreur - {e}")

            input("\n⏸️ Appuyez sur Entrée pour fermer le navigateur...")

        except Exception as e:
            logger.error(f"Erreur: {e}")
        finally:
            self.close_browser()

if __name__ == '__main__':
    print("🔧 Script de débogage des scrapers")
    print("="*80)

    debug = DebugScraper()

    # Tester LeBonCoin
    print("\n1️⃣ Test LeBonCoin")
    debug.inspect_page("https://www.leboncoin.fr/recherche?category=2&text=Peugeot")

    # Décommenter pour tester les autres sites :
    # print("\n2️⃣ Test La Centrale")
    # debug.inspect_page("https://www.lacentrale.fr/listing?makesModelsCommercialNames=Peugeot")

    # print("\n3️⃣ Test AutoScout24")
    # debug.inspect_page("https://www.autoscout24.fr/lst?sort=standard&desc=0&ustate=N%2CU&size=20&page=0&atype=C")
