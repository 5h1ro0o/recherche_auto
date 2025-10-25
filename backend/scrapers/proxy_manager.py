# backend/scrapers/proxy_manager.py
"""
Gestionnaire de rotation de proxies pour éviter les blocages
"""
import random
import logging
from typing import List, Optional
import os

logger = logging.getLogger(__name__)

# Import avec gestion d'erreur
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    print("⚠️ httpx n'est pas installé. Installer avec: pip install httpx")
    HTTPX_AVAILABLE = False
    httpx = None

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    print("⚠️ beautifulsoup4 n'est pas installé. Installer avec: pip install beautifulsoup4")
    BS4_AVAILABLE = False
    BeautifulSoup = None


class ProxyManager:
    """
    Gère la rotation de proxies pour les scrapers
    
    Usage:
        pm = ProxyManager()
        proxy = pm.get_proxy()
        # Utiliser proxy dans votre scraper
        pm.mark_proxy_working(proxy)  # Ou mark_proxy_failed(proxy)
    """
    
    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialise le gestionnaire de proxies
        
        Args:
            proxy_list: Liste de proxies au format "http://ip:port"
                       Si None, charge depuis variable d'environnement ou liste vide
        """
        if proxy_list is None:
            # Charger depuis env ou utiliser liste vide
            proxy_string = os.getenv("PROXY_LIST", "")
            proxy_list = [p.strip() for p in proxy_string.split(',') if p.strip()]
        
        self.all_proxies = proxy_list
        self.working_proxies = proxy_list.copy()
        self.failed_proxies = []
        
        logger.info(f"✅ ProxyManager initialisé avec {len(self.all_proxies)} proxies")
    
    def get_proxy(self) -> Optional[str]:
        """
        Récupère un proxy aléatoire parmi les proxies fonctionnels
        
        Returns:
            Proxy au format "http://ip:port" ou None si aucun dispo
        """
        if not self.working_proxies:
            logger.warning("⚠️ Aucun proxy fonctionnel disponible")
            
            # Si tous ont échoué, réinitialiser (donner une 2ème chance)
            if self.failed_proxies:
                logger.info("🔄 Réinitialisation des proxies échoués")
                self.working_proxies = self.failed_proxies.copy()
                self.failed_proxies = []
            else:
                return None
        
        proxy = random.choice(self.working_proxies)
        logger.debug(f"🎯 Proxy sélectionné: {proxy}")
        return proxy
    
    def mark_proxy_working(self, proxy: str):
        """
        Marque un proxy comme fonctionnel
        
        Args:
            proxy: Le proxy qui a fonctionné
        """
        if proxy not in self.working_proxies:
            self.working_proxies.append(proxy)
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
        
        logger.debug(f"✅ Proxy {proxy} marqué comme fonctionnel")
    
    def mark_proxy_failed(self, proxy: str):
        """
        Marque un proxy comme défaillant
        
        Args:
            proxy: Le proxy qui a échoué
        """
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
        
        if proxy not in self.failed_proxies:
            self.failed_proxies.append(proxy)
        
        logger.warning(f"❌ Proxy {proxy} marqué comme défaillant")
    
    def get_stats(self) -> dict:
        """
        Statistiques sur l'état des proxies
        
        Returns:
            Dict avec compteurs de proxies
        """
        return {
            'total': len(self.all_proxies),
            'working': len(self.working_proxies),
            'failed': len(self.failed_proxies)
        }
    
    @staticmethod
    def test_proxy(proxy: str, test_url: str = "https://httpbin.org/ip", timeout: int = 10) -> bool:
        """
        Test si un proxy fonctionne
        
        Args:
            proxy: Proxy à tester
            test_url: URL de test
            timeout: Timeout en secondes
            
        Returns:
            True si le proxy fonctionne, False sinon
        """
        if not HTTPX_AVAILABLE:
            logger.error("❌ httpx non disponible pour tester les proxies")
            return False
        
        try:
            proxies = {"http://": proxy, "https://": proxy}
            with httpx.Client(proxies=proxies, timeout=timeout) as client:
                response = client.get(test_url)
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"❌ Proxy {proxy} échoué au test: {e}")
            return False


# Exemple de liste de proxies gratuits (pour tests uniquement)
# ⚠️ Pour production, utilisez des proxies payants (Bright Data, Oxylabs, etc.)
FREE_PROXY_LIST = [
    # Format : "http://ip:port"
    # Ces proxies gratuits sont souvent instables, utilisez avec précaution
]


def get_free_proxies() -> List[str]:
    """
    Récupère une liste de proxies gratuits depuis free-proxy-list.net
    
    ⚠️ Attention : Proxies gratuits = souvent lents et peu fiables
    Pour production, utilisez des services payants
    
    Returns:
        Liste de proxies au format "http://ip:port"
    """
    if not HTTPX_AVAILABLE or not BS4_AVAILABLE:
        logger.error("❌ httpx ou beautifulsoup4 non disponibles")
        return []
    
    proxies = []
    
    try:
        logger.info("🔍 Récupération de proxies gratuits...")
        response = httpx.get("https://free-proxy-list.net/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'class': 'table'})
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows[:20]:  # Prendre les 20 premiers
                cols = row.find_all('td')
                if len(cols) >= 7:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    https = cols[6].text.strip()
                    
                    protocol = 'https' if https == 'yes' else 'http'
                    proxy = f"{protocol}://{ip}:{port}"
                    proxies.append(proxy)
        
        logger.info(f"✅ Récupéré {len(proxies)} proxies gratuits")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des proxies gratuits: {e}")
    
    return proxies


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=== Test ProxyManager ===\n")
    
    # Test 1 : Avec liste manuelle
    print("📋 Test avec liste manuelle...")
    manual_proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
    ]
    
    pm = ProxyManager(manual_proxies)
    print(f"Stats initiales: {pm.get_stats()}")
    
    # Simuler utilisation
    proxy = pm.get_proxy()
    print(f"Proxy obtenu: {proxy}")
    
    # Marquer comme défaillant
    pm.mark_proxy_failed(proxy)
    print(f"Stats après échec: {pm.get_stats()}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2 : Avec proxies gratuits (optionnel)
    if HTTPX_AVAILABLE and BS4_AVAILABLE:
        print("🌐 Test avec proxies gratuits (peut prendre du temps)...")
        free_proxies = get_free_proxies()
        
        if free_proxies:
            pm2 = ProxyManager(free_proxies)
            print(f"Stats proxies gratuits: {pm2.get_stats()}")
            
            # Tester les 3 premiers
            print("\n🧪 Test des 3 premiers proxies...")
            for proxy in free_proxies[:3]:
                is_working = ProxyManager.test_proxy(proxy, timeout=5)
                status = "✅ fonctionne" if is_working else "❌ ne fonctionne pas"
                print(f"  {proxy}: {status}")
        else:
            print("❌ Aucun proxy gratuit récupéré")
    else:
        print("⚠️ httpx ou beautifulsoup4 manquant, skip test proxies gratuits")
    
    print("\n✅ Tests terminés")