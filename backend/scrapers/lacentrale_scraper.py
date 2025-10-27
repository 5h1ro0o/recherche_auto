# backend/scrapers/lacentrale_scraper.py - VERSION PRODUCTION
from typing import List, Dict, Any
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LaCentraleScraper(BaseScraper):
    """
    Scraper pour LaCentrale (lacentrale.fr)
    Format query: 'marque:modele' (ex: 'volkswagen:golf')
    """
    
    BASE_URL = "https://www.lacentrale.fr"
    SEARCH_URL = f"{BASE_URL}/listing?makesModelsCommercialNames={{query}}"
    
    def get_source_name(self) -> str:
        return "lacentrale"
    
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LaCentrale
        
        search_params:
            - query: str (ex: 'volkswagen:golf' ou 'mercedes')
            - max_price: int (optionnel)
            - max_pages: int (défaut: 3)
            - min_year: int (optionnel)
        """
        query = search_params.get('query', 'volkswagen:golf')
        max_price = search_params.get('max_price')
        max_pages = search_params.get('max_pages', 3)
        min_year = search_params.get('min_year')
        
        results = []
        
        try:
            self.init_browser(headless=True)
            
            logger.info(f"🟢 LaCentrale: Recherche '{query}' sur {max_pages} pages")
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"📄 Page {page_num}/{max_pages}")
                
                # Construire URL
                url = self.SEARCH_URL.format(query=query.replace(':', '%3A'))
                if page_num > 1:
                    url += f"&page={page_num}"
                if max_price:
                    url += f"&priceMax={max_price}"
                if min_year:
                    url += f"&yearMin={min_year}"
                
                # Navigation
                try:
                    self.page.goto(url, wait_until='networkidle', timeout=30000)
                    self.random_delay(3, 5)
                except Exception as e:
                    logger.error(f"❌ Erreur navigation page {page_num}: {e}")
                    continue
                
                # Attendre les résultats
                # LaCentrale utilise .searchCard pour les résultats
                try:
                    self.page.wait_for_selector('.searchCard', timeout=15000)
                except Exception as e:
                    logger.warning(f"⚠️ Timeout ou pas d'annonces page {page_num}: {e}")
                    break
                
                # Parser les listings
                try:
                    listings = self.page.query_selector_all('.searchCard')
                    logger.info(f"✅ Trouvé {len(listings)} annonces")
                    
                    if len(listings) == 0:
                        logger.warning("⚠️ Aucune annonce trouvée, arrêt")
                        break
                    
                    for idx, listing in enumerate(listings, 1):
                        try:
                            parsed = self.parse_listing(listing)
                            if parsed and parsed.get('id'):
                                normalized = self.normalize_data(parsed)
                                results.append(normalized)
                                logger.debug(f"  ✓ Annonce {idx}: {normalized.get('title', 'N/A')[:50]}")
                            else:
                                logger.debug(f"  ✗ Annonce {idx}: Données invalides")
                        except Exception as e:
                            logger.warning(f"  ✗ Erreur parsing annonce {idx}: {e}")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur parsing listings page {page_num}: {e}")
                    break
                
                # Délai entre pages
                if page_num < max_pages:
                    self.random_delay(2, 4)
            
            logger.info(f"🎉 LaCentrale terminé: {len(results)} annonces récupérées")
            
        except Exception as e:
            logger.exception(f"❌ Erreur critique LaCentrale: {e}")
        finally:
            self.close_browser()
        
        return results
    
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse un élément de listing LaCentrale"""
        try:
            # URL et ID
            link_elem = element.query_selector('a')
            url = link_elem.get_attribute('href') if link_elem else None
            
            if not url:
                return None
            
            # Extraire ID depuis URL (ex: /auto-occasion-annonce-123456.html)
            source_id = None
            if 'annonce-' in url:
                try:
                    source_id = url.split('annonce-')[1].split('.html')[0]
                except:
                    pass
            
            if not source_id:
                # Fallback: utiliser toute l'URL comme ID
                source_id = url.replace('/', '_').replace('.html', '')
            
            # Titre (marque + modèle + version)
            title = self.safe_get_text(element, '.searchCardTitle')
            
            # Prix
            price_text = self.safe_get_text(element, '.searchCardPrice')
            
            # Kilométrage
            mileage_text = self.safe_get_text(element, '.searchCardMileage')
            
            # Année
            year_text = self.safe_get_text(element, '.searchCardYear')
            
            # Carburant
            fuel_text = self.safe_get_text(element, '.searchCardFuel')
            
            # Localisation
            location = self.safe_get_text(element, '.searchCardLocation')
            
            # Image
            img_url = self.safe_get_attribute(element, 'img', 'src')
            
            # Extraction marque/modèle
            make, model = self.extract_make_model_from_title(title) if title else (None, None)
            
            # URL complète
            full_url = f"{self.BASE_URL}{url}" if url and not url.startswith('http') else url
            
            return {
                'id': source_id,
                'title': title,
                'make': make,
                'model': model,
                'price': price_text,
                'year': year_text,
                'mileage': mileage_text,
                'fuel_type': fuel_text if fuel_text else None,
                'location': location,
                'images': [img_url] if img_url and img_url.startswith('http') else [],
                'url': full_url,
                'transmission': None,  # Pas toujours affiché en liste
                'posted_date': None
            }
            
        except Exception as e:
            logger.debug(f"Erreur parse_listing: {e}")
            return None


# ============ FONCTION DE TEST STANDALONE ============

def test_lacentrale_scraper():
    """Test du scraper LaCentrale"""
    import json
    
    print("="*60)
    print("🧪 TEST LACENTRALE SCRAPER")
    print("="*60)
    
    scraper = LaCentraleScraper()
    
    search_params = {
        'query': 'volkswagen:golf',
        'max_price': 20000,
        'max_pages': 2,
        'min_year': 2018
    }

    results = scraper.scrape(search_params)
    print(f"Total annonces récupérées: {len(results)}")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    