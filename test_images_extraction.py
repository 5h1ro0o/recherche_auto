#!/usr/bin/env python3
"""
Script de test pour vérifier l'extraction complète des images
"""

import logging
import sys
sys.path.insert(0, '/home/user/recherche_auto')

from backend.scrapers.leboncoin_scraper import LeBonCoinScraper

# Activer le logging DEBUG pour voir tous les détails
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("=" * 70)
print("🧪 TEST EXTRACTION DES IMAGES - LeBonCoin")
print("=" * 70)
print()

# Test avec seulement 1 page et 3 annonces max
test_params = {
    'query': 'voiture',
    'max_pages': 1,
    'max_price': 10000,
}

print(f"📋 Paramètres de test: {test_params}")
print()
print("🚀 Lancement du scraper...")
print()

scraper = LeBonCoinScraper()
results = scraper.scrape(test_params)

print()
print("=" * 70)
print(f"📊 RÉSULTATS: {len(results)} annonces récupérées")
print("=" * 70)
print()

if results:
    print("✅ Scraping réussi!")
    print()

    # Analyser les images
    total_annonces = len(results)
    annonces_avec_images = 0
    total_images = 0

    for result in results:
        images = result.get('images', [])
        if images:
            annonces_avec_images += 1
            total_images += len(images)

    print("📊 STATISTIQUES DES IMAGES:")
    print(f"   Total annonces: {total_annonces}")
    print(f"   Annonces avec images: {annonces_avec_images}")
    print(f"   Annonces sans images: {total_annonces - annonces_avec_images}")
    print(f"   Total images extraites: {total_images}")
    print(f"   Moyenne images/annonce: {total_images / total_annonces:.1f}")
    print()

    # Afficher détails des 3 premières annonces
    print("=" * 70)
    print("DÉTAILS DES ANNONCES:")
    print("=" * 70)

    for i, result in enumerate(results[:3], 1):
        print(f"\n📌 ANNONCE {i}: {result.get('title', 'N/A')[:60]}")
        print(f"   Prix: {result.get('price', 'N/A')}€")
        print(f"   URL: {result.get('url', 'N/A')}")

        images = result.get('images', [])
        if images:
            print(f"\n   📸 IMAGES ({len(images)} au total):")
            for idx, img_url in enumerate(images[:3], 1):
                print(f"      {idx}. {img_url}")
            if len(images) > 3:
                print(f"      ... et {len(images) - 3} autres images")
        else:
            print(f"\n   ⚠️ AUCUNE IMAGE pour cette annonce")
        print()

    if annonces_avec_images == 0:
        print("=" * 70)
        print("⚠️ AVERTISSEMENT: AUCUNE IMAGE N'A ÉTÉ EXTRAITE!")
        print("=" * 70)
        print()
        print("Causes possibles:")
        print("  1. Les annonces n'ont vraiment pas d'images")
        print("  2. La structure de l'objet Ad a changé")
        print("  3. Un problème dans le code d'extraction")
        print()
        print("Vérifiez les logs DEBUG ci-dessus pour plus de détails.")
    else:
        print("=" * 70)
        print(f"✅ SUCCÈS: {annonces_avec_images}/{total_annonces} annonces ont des images!")
        print("=" * 70)

else:
    print("❌ Aucune annonce récupérée")
    print()
    print("💡 Causes possibles:")
    print("   - L'IP est bloquée par DataDome (attendez quelques heures)")
    print("   - Problème de connexion réseau")
    print("   - Utilisez un proxy si le blocage persiste")
