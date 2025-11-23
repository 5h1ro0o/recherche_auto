#!/usr/bin/env python3
"""
Script de test pour l'API de scraping
Usage: python test_scrape_api.py
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def print_header(text: str):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_success(text: str):
    """Affiche un message de succès"""
    print(f"✅ {text}")


def print_error(text: str):
    """Affiche un message d'erreur"""
    print(f"❌ {text}")


def print_info(text: str):
    """Affiche une information"""
    print(f"ℹ️  {text}")


def test_server_running():
    """Teste si le serveur est accessible"""
    print_header("Test 1: Vérification du serveur")

    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"Serveur accessible: {response.json()}")
            return True
        else:
            print_error(f"Serveur répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Impossible de se connecter au serveur")
        print_info("Assurez-vous que le serveur est lancé avec: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_scrape_sources():
    """Teste l'endpoint /api/scrape/sources"""
    print_header("Test 2: Liste des sources disponibles")

    try:
        response = requests.get(f"{API_URL}/scrape/sources", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Sources disponibles: {data['total']}")

            for source_id, source_info in data['sources'].items():
                status = "✓" if source_info['available'] else "✗"
                print(f"  {status} {source_info['name']}: {source_info['url']}")
                print(f"     Filtres: {', '.join(source_info['filters'])}")

            return True
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_scrape_status():
    """Teste l'endpoint /api/scrape/status"""
    print_header("Test 3: Statut du système de scraping")

    try:
        response = requests.get(f"{API_URL}/scrape/status", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Système: {data['status']}")

            for scraper_id, scraper_info in data['scrapers'].items():
                status_icon = "✓" if scraper_info['available'] else "✗"
                status_text = scraper_info['status']
                print(f"  {status_icon} {scraper_id}: {status_text}")

                if 'error' in scraper_info:
                    print(f"     Erreur: {scraper_info['error']}")

            return True
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_scrape_autoscout24_basic():
    """Teste le scraping AutoScout24 basique (1 page)"""
    print_header("Test 4: Scraping AutoScout24 (basique)")

    payload = {
        "source": "autoscout24",
        "max_pages": 1
    }

    print_info(f"Requête: {json.dumps(payload, indent=2)}")
    print_info("⏳ Scraping en cours... (cela peut prendre 10-30 secondes)")

    try:
        response = requests.post(
            f"{API_URL}/scrape",
            json=payload,
            timeout=60  # Timeout plus long pour le scraping
        )

        if response.status_code == 200:
            data = response.json()

            if data['success']:
                print_success(f"Scraping réussi!")
                print_info(f"Source: {data['source']}")
                print_info(f"Véhicules trouvés: {data['count']}")
                print_info(f"Durée: {data['duration']:.2f}s")

                if data['count'] > 0:
                    print("\n📋 Exemple d'annonce:")
                    example = data['results'][0]
                    print(f"   Titre: {example.get('title', 'N/A')}")
                    print(f"   Prix: {example.get('price', 'N/A')}€")
                    print(f"   Année: {example.get('year', 'N/A')}")
                    print(f"   Kilométrage: {example.get('mileage', 'N/A')} km")
                    print(f"   URL: {example.get('url', 'N/A')}")

                return True
            else:
                print_error(f"Scraping échoué: {data.get('message', 'Erreur inconnue')}")
                return False

        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print_error("Timeout: le scraping a pris trop de temps")
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_scrape_autoscout24_with_filters():
    """Teste le scraping AutoScout24 avec filtres"""
    print_header("Test 5: Scraping AutoScout24 (avec filtres)")

    payload = {
        "source": "autoscout24",
        "max_pages": 1,
        "make": "volkswagen",
        "model": "golf",
        "max_price": 25000
    }

    print_info(f"Requête: {json.dumps(payload, indent=2)}")
    print_info("⏳ Scraping en cours...")

    try:
        response = requests.post(
            f"{API_URL}/scrape",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()

            if data['success']:
                print_success(f"Scraping réussi avec filtres!")
                print_info(f"Véhicules trouvés: {data['count']}")
                print_info(f"Durée: {data['duration']:.2f}s")
                return True
            else:
                print_error(f"Scraping échoué: {data.get('message')}")
                return False

        else:
            print_error(f"Erreur {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def main():
    """Fonction principale"""
    print("\n" + "🚗" * 35)
    print(" " * 20 + "TEST API SCRAPING")
    print("🚗" * 35)

    results = []

    # Test 1: Serveur accessible
    results.append(("Serveur accessible", test_server_running()))

    if not results[0][1]:
        print("\n❌ Le serveur n'est pas accessible. Tests arrêtés.")
        sys.exit(1)

    # Test 2: Liste des sources
    results.append(("Sources disponibles", test_scrape_sources()))

    # Test 3: Statut du système
    results.append(("Statut du système", test_scrape_status()))

    # Test 4: Scraping basique
    print_info("\n⚠️  Les tests suivants vont effectuer du scraping réel.")
    print_info("Ils peuvent prendre du temps et utiliser des ressources.")

    user_input = input("\nContinuer avec les tests de scraping? (o/N): ")

    if user_input.lower() in ['o', 'oui', 'y', 'yes']:
        results.append(("Scraping basique", test_scrape_autoscout24_basic()))
        results.append(("Scraping avec filtres", test_scrape_autoscout24_with_filters()))
    else:
        print_info("Tests de scraping ignorés")

    # Résumé
    print_header("RÉSUMÉ DES TESTS")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}")

    print("\n" + "-" * 70)
    print(f"Résultat: {passed}/{total} tests réussis")
    print("-" * 70)

    if passed == total:
        print_success("🎉 Tous les tests sont passés!")
        sys.exit(0)
    else:
        print_error("⚠️  Certains tests ont échoué")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
        sys.exit(1)
