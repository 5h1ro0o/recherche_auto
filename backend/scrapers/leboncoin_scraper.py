from typing import List, Dict, Any
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LeBonCoinScraper(BaseScraper):
    """Scraper pour LeBonCoin"""
    
    BASE_URL = "https://www.leboncoin.fr"
    SEARCH_URL = f"{BASE_URL}/recherche?category=2&text={{query}}"
    
    def get_source_name(self) -> str:
        return "leboncoin"
    
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LeBonCoin
        search_params: {
            'query': 'golf volkswagen',
            'max_price': 15000,
            'max_pages': 3
        }
        """
        query = search_params.get('query', 'voiture')
        max_price = search_params.get('max_price')
        max_pages = search_params.get('max_pages', 3)
        
        results = []
        
        try:
            self.init_browser(headless=True)
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping LeBonCoin page {page_num}")
                
                # Construire URL avec pagination
                url = self.SEARCH_URL.format(query=query.replace(' ', '%20'))
                if page_num > 1:
                    url += f"&page={page_num}"
                if max_price:
                    url += f"&price=0-{max_price}"
                
                self.page.goto(url, wait_until='domcontentloaded')
                self.random_delay(2, 4)
                
                # Attendre que les annonces se chargent
                try:
                    self.page.wait_for_selector('[data-qa-id="aditem_container"]', timeout=10000)
                except:
                    logger.warning(f"Pas d'annonces trouvées page {page_num}")
                    break
                
                # Parser les listings
                listings = self.page.query_selector_all('[data-qa-id="aditem_container"]')
                
                for listing in listings:
                    try:
                        parsed = self.parse_listing(listing)
                        if parsed:
                            normalized = self.normalize_data(parsed)
                            results.append(normalized)
                    except Exception as e:
                        logger.error(f"Erreur parsing listing: {e}")
                
                self.random_delay(1, 2)
            
            logger.info(f"LeBonCoin: {len(results)} annonces scrapées")
            
        except Exception as e:
            logger.exception(f"Erreur scraping LeBonCoin: {e}")
        finally:
            self.close_browser()
        
        return results
    
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse un élément de listing LeBonCoin"""
        try:
            # ID
            link_elem = element.query_selector('a[href*="/voitures/"]')
            url = link_elem.get_attribute('href') if link_elem else None
            source_id = url.split('/')[-1].split('.htm')[0] if url else None
            
            # Titre
            title_elem = element.query_selector('[data-qa-id="aditem_title"]')
            title = title_elem.inner_text() if title_elem else ""
            
            # Prix
            price_elem = element.query_selector('[data-qa-id="aditem_price"]')
            price = price_elem.inner_text() if price_elem else None
            
            # Localisation
            location_elem = element.query_selector('[data-qa-id="aditem_location"]')
            location = location_elem.inner_text() if location_elem else None
            
            # Image
            img_elem = element.query_selector('img[alt]')
            img_url = img_elem.get_attribute('src') if img_elem else None
            
            # Extraction marque/modèle depuis titre (basique)
            make, model = self._extract_make_model(title)
            
            return {
                'id': source_id,
                'title': title,
                'make': make,
                'model': model,
                'price': price,
                'location': location,
                'images': [img_url] if img_url else [],
                'url': f"{self.BASE_URL}{url}" if url else None,
                'year': None,  # À extraire du titre si possible
                'mileage': None,
                'fuel_type': None,
                'transmission': None
            }
            
        except Exception as e:
            logger.error(f"Erreur parse_listing LeBonCoin: {e}")
            return None
    
    def _extract_make_model(self, title: str) -> tuple:
        """Extrait marque/modèle du titre (logique simple)"""
        # Liste des marques courantes
        makes = ['Peugeot', 'Renault', 'Citroën', 'Volkswagen', 'BMW', 
                 'Mercedes', 'Audi', 'Ford', 'Toyota', 'Honda']
        
        title_lower = title.lower()
        
        for make in makes:
            if make.lower() in title_lower:
                # Essayer d'extraire le modèle (mot après la marque)
                parts = title.split()
                try:
                    make_idx = [p.lower() for p in parts].index(make.lower())
                    model = parts[make_idx + 1] if make_idx + 1 < len(parts) else None
                    return make, model
                except:
                    return make, None
        
        return None, None