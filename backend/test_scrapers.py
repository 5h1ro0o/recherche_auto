# backend/tests/test_scrapers.py
"""
Tests unitaires et d'intégration pour les scrapers
Utilise pytest pour les tests automatisés

Usage:
    pytest tests/test_scrapers.py -v
    pytest tests/test_scrapers.py::test_leboncoin_scrape -v
    pytest tests/test_scrapers.py -k "normalize" -v
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Ajouter backend au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.leboncoin_scraper import LeBonCoinScraper
from scrapers.lacentrale_scraper import LaCentraleScraper
from scrapers.autoscoot_scraper import AutoScout24Scraper
from scrapers.base_scraper import BaseScraper


# ============ FIXTURES ============

@pytest.fixture
def leboncoin_scraper():
    """Fixture pour scraper LeBonCoin"""
    return LeBonCoinScraper()


@pytest.fixture
def lacentrale_scraper():
    """Fixture pour scraper LaCentrale"""
    return LaCentraleScraper()


@pytest.fixture
def autoscout_scraper():
    """Fixture pour scraper AutoScout24"""
    return AutoScout24Scraper()


@pytest.fixture
def sample_raw_data():
    """Données brutes exemple pour tests"""
    return {
        'id': 'TEST123',
        'title': 'Peugeot 208 GTI 2019 essence',
        'price': '15 000 €',
        'year': '2019',
        'mileage': '45 000 km',
        'location': 'Paris 75001',
        'images': ['https://example.com/img1.jpg'],
        'url': 'https://example.com/annonce/TEST123',
        'description': 'Belle Peugeot 208 GTI essence, boîte manuelle, 45000km'
    }


# ============ TESTS LEBONCOIN ============

class TestLeBonCoinScraper:
    """Tests pour LeBonCoinScraper"""
    
    def test_source_name(self, leboncoin_scraper):
        """Test du nom de source"""
        assert leboncoin_scraper.get_source_name() == "leboncoin"
    
    def test_scrape_returns_list(self, leboncoin_scraper):
        """Test que scrape retourne une liste"""
        # Mock quick test avec 1 page
        results = leboncoin_scraper.scrape({
            'query': 'golf',
            'max_pages': 1,
            'deep_scrape': False
        })
        
        assert isinstance(results, list)
    
    @pytest.mark.slow
    def test_scrape_quality(self, leboncoin_scraper):
        """Test qualité des données scrapées"""
        results = leboncoin_scraper.scrape({
            'query': 'peugeot 208',
            'max_pages': 1,
            'deep_scrape': False
        })
        
        # Vérifier qu'on a des résultats
        assert len(results) > 0, "Aucune annonce récupérée"
        
        # Vérifier la première annonce
        first = results[0]
        
        assert first.get('source') == 'leboncoin'
        assert first.get('source_id') is not None
        assert first.get('title') is not None
        assert first.get('url') is not None
        
        # Au moins 70% des annonces doivent avoir un prix
        with_price = sum(1 for r in results if r.get('price'))
        assert with_price / len(results) >= 0.7
    
    def test_parse_price(self, leboncoin_scraper):
        """Test parsing des prix"""
        assert leboncoin_scraper._parse_price("15 000 €") == 15000
        assert leboncoin_scraper._parse_price("8500") == 8500
        assert leboncoin_scraper._parse_price("12,500 €") == 12500
        assert leboncoin_scraper._parse_price(None) is None
        assert leboncoin_scraper._parse_price("") is None
        assert leboncoin_scraper._parse_price("N/A") is None
    
    def test_parse_year(self, leboncoin_scraper):
        """Test parsing des années"""
        assert leboncoin_scraper._parse_year("2019") == 2019
        assert leboncoin_scraper._parse_year(2020) == 2020
        assert leboncoin_scraper._parse_year("1985") == 1985
        assert leboncoin_scraper._parse_year("1979") is None  # Trop vieux
        assert leboncoin_scraper._parse_year("2031") is None  # Futur
        assert leboncoin_scraper._parse_year(None) is None
    
    def test_parse_mileage(self, leboncoin_scraper):
        """Test parsing kilométrage"""
        assert leboncoin_scraper._parse_mileage("45 000 km") == 45000
        assert leboncoin_scraper._parse_mileage("120000") == 120000
        assert leboncoin_scraper._parse_mileage("12,500 km") == 12500
        assert leboncoin_scraper._parse_mileage(None) is None
    
    def test_extract_make_model_nlp(self, leboncoin_scraper):
        """Test extraction marque/modèle"""
        # Test avec titre complet
        make, model = leboncoin_scraper._extract_make_model_nlp(
            "Peugeot 208 GTI 2019"
        )
        assert make == "Peugeot"
        assert model == "208"
        
        # Test avec Volkswagen
        make, model = leboncoin_scraper._extract_make_model_nlp(
            "Volkswagen Golf 7 TDI"
        )
        assert make == "Volkswagen"
        assert model == "GOLF"
        
        # Test sans modèle clair
        make, model = leboncoin_scraper._extract_make_model_nlp(
            "Renault occasion"
        )
        assert make == "Renault"
    
    def test_extract_fuel_from_text(self, leboncoin_scraper):
        """Test extraction carburant"""
        assert leboncoin_scraper._extract_fuel_from_text("essence automatique") == "essence"
        assert leboncoin_scraper._extract_fuel_from_text("diesel manuelle") == "diesel"
        assert leboncoin_scraper._extract_fuel_from_text("voiture électrique") == "electrique"
        assert leboncoin_scraper._extract_fuel_from_text("hybride rechargeable") == "hybride"
        assert leboncoin_scraper._extract_fuel_from_text("gpl") == "gpl"
    
    def test_extract_transmission_from_text(self, leboncoin_scraper):
        """Test extraction transmission"""
        assert leboncoin_scraper._extract_transmission_from_text("boîte manuelle") == "manuelle"
        assert leboncoin_scraper._extract_transmission_from_text("automatique") == "automatique"
        assert leboncoin_scraper._extract_transmission_from_text("boite auto") == "automatique"
    
    def test_parse_relative_date(self, leboncoin_scraper):
        """Test parsing dates relatives"""
        now = datetime.utcnow()
        
        # Aujourd'hui
        result = leboncoin_scraper._parse_relative_date("Aujourd'hui")
        assert result is not None
        
        # Hier
        result = leboncoin_scraper._parse_relative_date("Hier")
        result_dt = datetime.fromisoformat(result)
        assert (now - result_dt).days == 1
        
        # Il y a X jours
        result = leboncoin_scraper._parse_relative_date("Il y a 3 jours")
        result_dt = datetime.fromisoformat(result)
        assert 2 <= (now - result_dt).days <= 4
    
    def test_normalize_and_enrich(self, leboncoin_scraper, sample_raw_data):
        """Test normalisation et enrichissement"""
        normalized = leboncoin_scraper.normalize_and_enrich(sample_raw_data)
        
        # Vérifier normalisation
        assert normalized['source'] == 'leboncoin'
        assert normalized['price'] == 15000
        assert normalized['year'] == 2019
        assert normalized['mileage'] == 45000
        
        # Vérifier enrichissement NLP
        assert normalized['make'] == 'Peugeot'
        assert normalized['model'] == '208'
        assert normalized['fuel_type'] == 'essence'
        assert normalized['transmission'] == 'manuelle'


# ============ TESTS LACENTRALE ============

class TestLaCentraleScraper:
    """Tests pour LaCentraleScraper"""
    
    def test_source_name(self, lacentrale_scraper):
        """Test du nom de source"""
        assert lacentrale_scraper.get_source_name() == "lacentrale"
    
    def test_scrape_returns_list(self, lacentrale_scraper):
        """Test que scrape retourne une liste"""
        results = lacentrale_scraper.scrape({
            'query': 'volkswagen:golf',
            'max_pages': 1
        })
        
        assert isinstance(results, list)
    
    @pytest.mark.slow
    def test_scrape_quality(self, lacentrale_scraper):
        """Test qualité des données"""
        results = lacentrale_scraper.scrape({
            'query': 'peugeot:208',
            'max_pages': 1
        })
        
        if len(results) > 0:
            first = results[0]
            assert first.get('source') == 'lacentrale'
            assert first.get('title') is not None


# ============ TESTS AUTOSCOUT ============

class TestAutoScout24Scraper:
    """Tests pour AutoScout24Scraper"""
    
    def test_source_name(self, autoscout_scraper):
        """Test du nom de source"""
        assert autoscout_scraper.get_source_name() == "autoscout24"
    
    def test_scrape_returns_list(self, autoscout_scraper):
        """Test que scrape retourne une liste"""
        results = autoscout_scraper.scrape({'max_pages': 1})
        assert isinstance(results, list)


# ============ TESTS BASE SCRAPER ============

class TestBaseScraper:
    """Tests pour la classe abstraite BaseScraper"""
    
    def test_parse_helpers(self):
        """Test des helpers de parsing"""
        # Créer un scraper concret pour tester
        scraper = LeBonCoinScraper()
        
        # Test _parse_price
        assert scraper._parse_price("15000") == 15000
        assert scraper._parse_price("15 000") == 15000
        assert scraper._parse_price("15,000") == 15000
        
        # Test _parse_year
        assert scraper._parse_year("2020") == 2020
        assert scraper._parse_year(2019) == 2019
        
        # Test _parse_mileage
        assert scraper._parse_mileage("50000") == 50000
        assert scraper._parse_mileage("50 000") == 50000
    
    def test_extract_make_model(self):
        """Test extraction marque/modèle générique"""
        scraper = LeBonCoinScraper()
        
        make, model = scraper.extract_make_model_from_title("BMW Serie 3")
        assert make == "BMW"
        
        make, model = scraper.extract_make_model_from_title("Audi A3 Sportback")
        assert make == "Audi"
        assert model == "A3"


# ============ TESTS ANTI-DÉTECTION ============

class TestAntiDetection:
    """Tests des fonctionnalités anti-détection"""
    
    @pytest.mark.slow
    def test_user_agent_randomization(self):
        """Test randomisation user-agent"""
        scraper = LeBonCoinScraper()
        
        ua1 = scraper.get_random_user_agent()
        ua2 = scraper.get_random_user_agent()
        
        assert ua1 is not None
        assert ua2 is not None
        assert len(ua1) > 50  # User-agent valide
    
    def test_random_delay(self):
        """Test délais aléatoires"""
        import time
        scraper = LeBonCoinScraper()
        
        start = time.time()
        scraper.random_delay(0.1, 0.2)
        duration = time.time() - start
        
        assert 0.09 <= duration <= 0.35  # Avec marge


# ============ TESTS NORMALISATION ============

class TestNormalization:
    """Tests de normalisation des données"""
    
    def test_normalize_data_complete(self, sample_raw_data):
        """Test normalisation complète"""
        scraper = LeBonCoinScraper()
        normalized = scraper.normalize_data(sample_raw_data)
        
        assert normalized['source'] == 'leboncoin'
        assert normalized['source_id'] == 'TEST123'
        assert normalized['title'] == 'Peugeot 208 GTI 2019 essence'
        assert normalized['url'] == 'https://example.com/annonce/TEST123'
    
    def test_normalize_data_missing_fields(self):
        """Test normalisation avec champs manquants"""
        scraper = LeBonCoinScraper()
        
        minimal_data = {
            'id': 'TEST456',
            'title': 'Voiture occasion'
        }
        
        normalized = scraper.normalize_data(minimal_data)
        
        assert normalized['source'] == 'leboncoin'
        assert normalized['source_id'] == 'TEST456'
        assert normalized['price'] is None
        assert normalized['year'] is None


# ============ MARKERS PYTEST ============

# Marquer les tests lents
pytestmark = pytest.mark.slow


# ============ CONFIGURATION PYTEST ============

def pytest_configure(config):
    """Configuration pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# ============ FIXTURES AVANCÉES ============

@pytest.fixture(scope="session")
def test_database():
    """Fixture pour base de données de test"""
    # TODO: Setup test DB
    yield
    # Teardown


@pytest.fixture
def mock_redis():
    """Mock Redis pour tests"""
    try:
        import fakeredis
        return fakeredis.FakeStrictRedis()
    except ImportError:
        pytest.skip("fakeredis not installed")


# ============ TESTS PERFORMANCE ============

@pytest.mark.benchmark
class TestPerformance:
    """Tests de performance"""
    
    def test_parsing_speed(self, benchmark):
        """Test vitesse de parsing"""
        scraper = LeBonCoinScraper()
        
        def parse_operation():
            return scraper._parse_price("15 000 €")
        
        result = benchmark(parse_operation)
        assert result == 15000


# ============ RAPPORT DE TESTS ============

def test_generate_report():
    """Génère un rapport de tests"""
    # Cette fonction est appelée après tous les tests
    pass


if __name__ == "__main__":
    # Lancer les tests
    pytest.main([__file__, "-v", "--tb=short"])