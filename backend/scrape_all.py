#!/usr/bin/env python3
"""
SCRIPT PRINCIPAL DE SCRAPING - VERSION SIMPLIFIÉE
Lance tous les scrapers dans le bon ordre pour peupler l'encyclopédie automobile
"""

import asyncio
import sys
from datetime import datetime


def print_banner():
    """Bannière de démarrage"""
    print("\n" + "=" * 80)
    print("🌍 SCRAPING ENCYCLOPÉDIE AUTOMOBILE COMPLÈTE".center(80))
    print("=" * 80 + "\n")


def print_section(title: str, emoji: str):
    """Affiche une section"""
    print(f"\n{'=' * 80}")
    print(f"{emoji} {title}")
    print("=" * 80 + "\n")


async def scrape_brands_and_models():
    """
    ÉTAPE 1 : Collecte des marques et modèles
    Utilise le scraper amélioré testé et fonctionnel
    """
    print_section("ÉTAPE 1/3 : MARQUES ET MODÈLES", "🚗")

    print("📌 Utilisation du scraper amélioré (scrape_encyclopedia_improved.py)")
    print("📊 Données : 57 marques + 155 modèles")
    print("⏱️  Durée estimée : 2-5 minutes\n")

    try:
        from scrape_encyclopedia_improved import ImprovedScraper

        scraper = ImprovedScraper()
        await scraper.run_complete_scraping()

        print("\n✅ Marques et modèles collectés avec succès !")
        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de la collecte des marques/modèles : {e}")
        import traceback
        traceback.print_exc()
        return False


async def scrape_engines():
    """
    ÉTAPE 2 : Collecte des moteurs (optionnel)
    """
    print_section("ÉTAPE 2/3 : MOTEURS (OPTIONNEL)", "🔧")

    print("⚠️  Cette étape est optionnelle et peut prendre du temps.")
    print("📊 Données : 100-200 moteurs avec specs et fiabilité")
    print("⏱️  Durée estimée : 30-60 minutes")

    # Pour l'instant, on skip cette étape car les autres scrapers
    # peuvent avoir des erreurs 403
    print("\n⏭️  Passage à l'étape suivante (à implémenter plus tard)")
    print("💡 Conseil : Utilisez scrape_engines_web.py séparément si besoin\n")
    return True


async def scrape_transmissions():
    """
    ÉTAPE 3 : Collecte des transmissions (optionnel)
    """
    print_section("ÉTAPE 3/3 : TRANSMISSIONS (OPTIONNEL)", "⚙️")

    print("⚠️  Cette étape est optionnelle et peut prendre du temps.")
    print("📊 Données : 30-50 transmissions avec fiabilité")
    print("⏱️  Durée estimée : 30-60 minutes")

    # Pour l'instant, on skip cette étape
    print("\n⏭️  Passage au résumé (à implémenter plus tard)")
    print("💡 Conseil : Utilisez scrape_transmissions_web.py séparément si besoin\n")
    return True


def print_summary(success: bool, duration: float):
    """Affiche le résumé final"""
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL".center(80))
    print("=" * 80 + "\n")

    if success:
        print("✅ Scraping terminé avec succès !")
        print("\n📈 Données collectées :")
        print("   • 57 marques automobiles")
        print("   • 155 modèles de voitures")
        print("   • Relations marque ↔ modèle créées")

        print(f"\n⏱️  Durée totale : {duration:.1f} secondes")

        print("\n🎯 PROCHAINES ÉTAPES :")
        print("   1. Vérifier les données : psql -U postgres -d recherche_auto")
        print("   2. Démarrer l'API : uvicorn app.main:app --reload")
        print("   3. Tester le frontend : cd ../frontend && npm run dev")

        print("\n💡 POUR ALLER PLUS LOIN :")
        print("   • Ajouter plus de modèles : python scrape_models_web.py")
        print("   • Ajouter des moteurs : python scrape_engines_web.py")
        print("   • Ajouter des transmissions : python scrape_transmissions_web.py")
    else:
        print("❌ Le scraping a rencontré des erreurs")
        print("\n📋 Vérifications à faire :")
        print("   • PostgreSQL est-il démarré ?")
        print("   • Les migrations sont-elles appliquées ? (alembic upgrade head)")
        print("   • Le fichier .env existe-t-il avec DATABASE_URL ?")

    print("\n" + "=" * 80 + "\n")


async def main():
    """Point d'entrée principal"""
    start_time = datetime.now()

    print_banner()
    print(f"🕐 Démarrage : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # ÉTAPE 1 : Marques et modèles (obligatoire)
        success = await scrape_brands_and_models()

        if not success:
            print("\n⚠️  Arrêt du scraping suite à une erreur critique")
            return 1

        # ÉTAPE 2 : Moteurs (optionnel)
        await scrape_engines()

        # ÉTAPE 3 : Transmissions (optionnel)
        await scrape_transmissions()

        # Résumé final
        duration = (datetime.now() - start_time).total_seconds()
        print_summary(True, duration)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrompu par l'utilisateur (Ctrl+C)")
        return 1

    except Exception as e:
        print(f"\n\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()

        duration = (datetime.now() - start_time).total_seconds()
        print_summary(False, duration)
        return 1


if __name__ == "__main__":
    print("\n" + "🚀 LANCEMENT DU SCRAPING AUTOMATIQUE".center(80))
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
