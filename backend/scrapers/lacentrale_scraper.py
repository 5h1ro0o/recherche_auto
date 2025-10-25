from typing import List, Dict, Any
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LaCentraleScraper(BaseScraper):
    """Scraper pour LaCentrale"""
    
    BASE_URL = "https://www.lacentrale.fr"
    SEARCH_URL = f"{BASE_URL}/listing?makesModelsCommercialNames={{query}}"
    
    def get_source_name(self) -> str:
        return "lacentrale"
    
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LaCentrale
        """
        query = search_params.get('query', 'volkswagen%3Agolf')
        max_pages = search_params.get('max_pages', 3)
        
        results = []
        
        try:
            self.init_browser(headless=True)
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping LaCentrale page {page_num}")
                
                url = self.SEARCH_URL.format(query=query)
                if page_num > 1:
                    url += f"&page={page_num}"
                
                self.page.goto(url, wait_until='networkidle')
                self.random_delay(2, 4)
                
                # Sélecteurs LaCentrale (à adapter selon structure réelle)
                try:
                    self.page.wait_for_selector('.searchCard', timeout=10000)
                except:
                    logger.warning(f"Pas d'annonces page {page_num}")
                    break
                
                listings = self.page.query_selector_all('.searchCard')
                
                for listing in listings:
                    try:
                        parsed = self.parse_listing(listing)
                        if parsed:
                            normalized = self.normalize_data(parsed)
                            results.append(normalized)
                    except Exception as e:
                        logger.error(f"Erreur parsing: {e}")
                
                self.random_delay(1, 2)
            
            logger.info(f"LaCentrale: {len(results)} annonces scrapées")
            
        except Exception as e:
            logger.exception(f"Erreur LaCentrale: {e}")
        finally:
            self.close_browser()
        
        return results
    
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse listing LaCentrale"""
        try:
            # Titre
            title_elem = element.query_selector('.searchCardTitle')
            title = title_elem.inner_text() if title_elem else ""
            
            # Prix
            price_elem = element.query_selector('.searchCardPrice')
            price = price_elem.inner_text() if price_elem else None
            
            # Kilométrage
            km_elem = element.query_selector('.searchCardMileage')
            mileage = km_elem.inner_text() if km_elem else None
            
            # Année
            year_elem = element.query_selector('.searchCardYear')
            year = year_elem.inner_text() if year_elem else None
            
            # URL
            link_elem = element.query_selector('a')
            url = link_elem.get_attribute('href') if link_elem else None
            
            # Image
            img_elem = element.query_selector('img')
            img_url = img_elem.get_attribute('src') if img_elem else None
            
            return {
                'id': url.split('/')[-1].replace('.html', '') if url else None,
                'title': title,
                'make': None,  # À extraire du titre
                'model': None,
                'price': price,
                'year': year,
                'mileage': mileage,
                'images': [img_url] if img_url else [],
                'url': f"{self.BASE_URL}{url}" if url and not url.startswith('http') else url,
                'fuel_type': None,
                'transmission': None,
                'location': None
            }
            
        except Exception as e:
            logger.error(f"Erreur parse LaCentrale: {e}")
            return None