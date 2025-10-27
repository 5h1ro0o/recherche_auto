# backend/scrapers/leboncoin_scraper.py - VERSION PRODUCTION
from typing import List, Dict, Any
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LeBonCoinScraper(BaseScraper):
    """
    Scraper pour LeBonCoin (leboncoin.fr)
    Catégorie voitures: category=2
    """
    
    BASE_URL = "https://www.leboncoin.fr"
    SEARCH_URL = f"{BASE_URL}/recherche?category=2&text={{query}}"
    
    def get_source_name(self) -> str:
        return "leboncoin"
    
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape LeBonCoin
        
        search_params:
            - query: str (ex: 'volkswagen golf')
            - max_price: int (optionnel)
            - max_pages: int (défaut: 3)
            - location: str (optionnel, ex: 'paris')
        """
        query = search_params.get('query', 'voiture')
        max_price = search_params.get('max_price')
        max_pages = search_params.get('max_pages', 3)
        location = search_params.get('location')
        
        results = []
        
        try:
            self.init_browser(headless=True)
            
            logger.info(f"🔵 LeBonCoin: Recherche '{query}' sur {max_pages} pages")
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"📄 Page {page_num}/{max_pages}")
                
                # Construire URL
                url = self.SEARCH_URL.format(query=query.replace(' ', '%20'))
                if page_num > 1:
                    url += f"&page={page_num}"
                if max_price:
                    url += f"&price=0-{max_price}"
                if location:
                    url += f"&location={location}"
                
                # Navigation
                try:
                    self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    self.random_delay(2, 4)
                except Exception as e:
                    logger.error(f"❌ Erreur navigation page {page_num}: {e}")
                    continue
                
                # Attendre que les annonces se chargent
                try:
                    self.page.wait_for_selector('[data-qa-id="aditem_container"]', timeout=15000)
                except Exception as e:
                    logger.warning(f"⚠️ Timeout ou pas d'annonces page {page_num}: {e}")
                    break
                
                # Parser les listings
                try:
                    listings = self.page.query_selector_all('[data-qa-id="aditem_container"]')
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
            
            logger.info(f"🎉 LeBonCoin terminé: {len(results)} annonces récupérées")
            
        except Exception as e:
            logger.exception(f"❌ Erreur critique LeBonCoin: {e}")
        finally:
            self.close_browser()
        
        return results
    
    def parse_listing(self, element) -> Dict[str, Any]:
        """Parse un élément de listing LeBonCoin"""
        try:
            # ID et URL
            link_elem = element.query_selector('a[href*="/voitures/"]')
            url = link_elem.get_attribute('href') if link_elem else None
            
            if not url:
                return None
            
            # Extraire ID depuis URL (ex: /voitures/2517698412.htm)
            source_id = url.split('/')[-1].split('.htm')[0] if '/' in url else None
            
            if not source_id:
                return None
            
            # Titre
            title = self.safe_get_text(element, '[data-qa-id="aditem_title"]')
            
            # Prix
            price_text = self.safe_get_text(element, '[data-qa-id="aditem_price"]')
            
            # Localisation
            location = self.safe_get_text(element, '[data-qa-id="aditem_location"]')
            
            # Image
            img_elem = element.query_selector('img[alt]')
            img_url = img_elem.get_attribute('src') if img_elem else None
            
            # Date de publication (optionnelle)
            date_elem = element.query_selector('[data-qa-id="aditem_date"]')
            posted_date = date_elem.inner_text().strip() if date_elem else None
            
            # Extraction marque/modèle depuis titre
            make, model = self.extract_make_model_from_title(title) if title else (None, None)
            
            # URL complète
            full_url = f"{self.BASE_URL}{url}" if url and not url.startswith('http') else url
            
            return {
                'id': source_id,
                'title': title,
                'make': make,
                'model': model,
                'price': price_text,
                'location': location,
                'images': [img_url] if img_url and img_url.startswith('http') else [],
                'url': full_url,
                'posted_date': posted_date,
                'year': None,  # LBC ne l'affiche pas toujours en liste
                'mileage': None,
                'fuel_type': None,
                'transmission': None
            }
            
        except Exception as e:
            logger.debug(f"Erreur parse_listing: {e}")
            return None


# ============ FONCTION DE TEST STANDALONE ============

def test_leboncoin_scraper():
    """Test du scraper LeBonCoin"""
    import json
    
    print("="*60)
    print("🧪 TEST LEBONCOIN SCRAPER")
    print("="*60)
    
    scraper = LeBonCoinScraper()
    
    search_params = {
        'query': 'volkswagen golf',
        'max_price': 15000,
        'max_pages': 2,
        # 'location': 'paris'  # Optionnel
    }
    
    print(f"\n📋 Paramètres: {json.dumps(search_params, indent=2, ensure_ascii=False)}")
    print("\n🚀 Lancement du scraping...\n")
    
    results = scraper.scrape(search_params)
    
    print("\n" + "="*60)
    print(f"📊 RÉSULTATS: {len(results)} annonces")
    print("="*60)
    
    if results:
        print(f"\n✨ Exemple (première annonce):")
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
        
        print(f"\n💾 Sauvegarde dans leboncoin_results.json...")
        with open('leboncoin_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("✅ Sauvegardé!")
    else:
        print("\n⚠️ Aucun résultat trouvé")


if __name__ == "__main__":
    # Configuration logging pour le test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_leboncoin_scraper()