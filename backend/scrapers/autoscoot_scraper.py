from typing import List, Dict, Any
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class AutoScout24Scraper(BaseScraper):
    """Scraper pour AutoScout24"""
    
    BASE_URL = "https://www.autoscout24.fr"
    SEARCH_URL = f"{BASE_URL}/lst?sort=standard&desc=0&ustate=N%2CU&size=20&page={{page}}&atype=C&search_id={{search_id}}"
    
    def get_source_name(self) -> str:
        return "autoscout24"
    
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape AutoScout24
        """
        max_pages = search_params.get('max_pages', 3)
        results = []
        
        try:
            self.init_browser(headless=True)
            
            # Faire une recherche initiale pour obtenir search_id
            search_url = f"{self.BASE_URL}/lst?sort=standard&desc=0&ustate=N%2CU&size=20&page=0&atype=C"
            self.page.goto(search_url, wait_until='networkidle')
            self.random_delay(2, 4)
            
            current_url = self.page.url
            search_id = current_url.split('search_id=')[-1] if 'search_id=' in current_url else 'default'
            
            for page_num in range(0, max_pages):
                logger.info(f"Scraping AutoScout24 page {page_num}")
                
                url = self.SEARCH_URL.format(page=page_num, search_id=search_id)
                self.page.goto(url, wait_until='networkidle')
                self.random_delay(2, 4)
                
                try:
                    self.page.wait_for_selector('[data-item-name="detail-page-link"]', timeout=10000)
                except:
                    logger.warning(f"Pas d'annonces page {page_num}")
                    break
                
                listings = self.page.query_selector_all('[data-item-name="detail-page-link"]')
                
                for listing in listings:
                    try:
                        parsed = self.parse_listing(listing)
                        if parsed:
                            normalized = self.normalize_data(parsed)
                            results.append(normalized)
                    except Exception as e:
                        logger.error(f"Erreur parsing: {e}")
                
                self.random_delay(1, 2)
            
            logger.info(f"AutoScout24: {len(results)} annonces scrapées")
            
        except Exception as e:
            logger.exception(f"Erreur AutoScout24: {e}")
        finally:
            self.close_browser()
        
        return results
    
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse listing AutoScout24"""
        try:
            # Titre
            title_elem = element.query_selector('[data-item-name="make-model-title"]')
            title = title_elem.inner_text() if title_elem else ""
            
            # Prix
            price_elem = element.query_selector('[data-item-name="price"]')
            price = price_elem.inner_text() if price_elem else None
            
            # URL
            url = element.get_attribute('href')
            
            # ID depuis URL
            source_id = url.split('/')[-1] if url else None
            
            return {
                'id': source_id,
                'title': title,
                'make': None,
                'model': None,
                'price': price,
                'year': None,
                'mileage': None,
                'images': [],
                'url': f"{self.BASE_URL}{url}" if url and not url.startswith('http') else url,
                'fuel_type': None,
                'transmission': None,
                'location': None
            }
            
        except Exception as e:
            logger.error(f"Erreur parse AutoScout24: {e}")
            return None