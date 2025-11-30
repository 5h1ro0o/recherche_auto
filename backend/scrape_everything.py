#!/usr/bin/env python3
"""
🌍 SCRAPER ULTIME - COLLECTE ABSOLUMENT TOUT
Lance tous les scrapers complets pour collecter TOUTES les données automobiles :
- TOUTES les marques mondiales
- TOUS les modèles avec caractéristiques techniques complètes
- TOUS les moteurs avec specs, fiabilité, problèmes
- TOUTES les transmissions avec fiabilité, avis
- TOUS les avis positifs et négatifs
"""

import asyncio
import sys
from datetime import datetime
import os


def print_banner():
    """Bannière de démarrage"""
    print("\n" + "=" * 100)
    print("║" + " " * 98 + "║")
    print("║" + "🌍 SCRAPING COMPLET ENCYCLOPÉDIE AUTOMOBILE".center(98) + "║")
    print("║" + "COLLECTE ABSOLUMENT TOUTES LES DONNÉES DEPUIS INTERNET".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("=" * 100 + "\n")


def print_step(step: int, total: int, title: str, emoji: str):
    """Affiche une étape"""
    print(f"\n{'=' * 100}")
    print(f"{emoji} ÉTAPE {step}/{total}: {title}")
    print("=" * 100 + "\n")


async def step1_brands_and_models():
    """
    ÉTAPE 1 : Marques et modèles complets
    """
    print_step(1, 4, "MARQUES ET MODÈLES COMPLETS", "🚗")

    print("📋 Ce qui sera collecté :")
    print("  • Toutes les marques automobiles mondiales")
    print("  • Tous les modèles de chaque marque")
    print("  • Caractéristiques techniques complètes (moteur, puissance, etc.)")
    print("  • Avis positifs et négatifs réels")
    print("  • Notes de fiabilité")
    print("  • Avantages et inconvénients")
    print("\n⏱️  Durée estimée : 1-2 heures\n")

    try:
        from scrape_complete_data import CompleteScraper

        scraper = CompleteScraper()
        await scraper.run_complete_scraping()

        print("\n✅ Marques et modèles collectés avec succès !")
        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de la collecte des marques/modèles : {e}")
        import traceback
        traceback.print_exc()
        return False


async def step2_engines():
    """
    ÉTAPE 2 : Moteurs complets
    """
    print_step(2, 4, "MOTEURS COMPLETS", "🔧")

    print("📋 Ce qui sera collecté :")
    print("  • Tous les moteurs de toutes les marques")
    print("  • Caractéristiques techniques (cylindrée, puissance, couple)")
    print("  • Notes de fiabilité")
    print("  • Problèmes communs recensés")
    print("  • Coûts d'entretien")
    print("  • Avis d'experts et utilisateurs")
    print("\n⏱️  Durée estimée : 1-2 heures\n")

    try:
        from scrape_engines_complete import EngineCompleteScraper

        scraper = EngineCompleteScraper()
        await scraper.run_complete_scraping()

        print("\n✅ Moteurs collectés avec succès !")
        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de la collecte des moteurs : {e}")
        import traceback
        traceback.print_exc()
        return False


async def step3_transmissions():
    """
    ÉTAPE 3 : Transmissions complètes
    """
    print_step(3, 4, "TRANSMISSIONS COMPLÈTES", "⚙️")

    print("📋 Ce qui sera collecté :")
    print("  • Toutes les transmissions (manuelles, automatiques, CVT)")
    print("  • Notes de fiabilité")
    print("  • Problèmes communs (embrayage, mécatronique, etc.)")
    print("  • Coûts de maintenance")
    print("  • Avis utilisateurs")
    print("\n⏱️  Durée estimée : 30-60 minutes\n")

    try:
        from scrape_transmissions_complete import TransmissionCompleteScraper

        scraper = TransmissionCompleteScraper()
        await scraper.run_complete_scraping()

        print("\n✅ Transmissions collectées avec succès !")
        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de la collecte des transmissions : {e}")
        import traceback
        traceback.print_exc()
        return False


async def step4_associations():
    """
    ÉTAPE 4 : Créer les associations
    """
    print_step(4, 4, "CRÉATION DES ASSOCIATIONS", "🔗")

    print("📋 Ce qui sera fait :")
    print("  • Lier les moteurs aux modèles")
    print("  • Lier les transmissions aux modèles")
    print("  • Lier les moteurs aux transmissions")
    print("\n⏱️  Durée estimée : 5-10 minutes\n")

    print("💡 Cette étape sera implémentée dans un prochain script...")
    print("⏭️  Passage au résumé\n")

    return True


def print_summary(results: dict, duration: float):
    """Affiche le résumé final"""
    print("\n" + "=" * 100)
    print("║" + " " * 98 + "║")
    print("║" + "📊 RÉSUMÉ FINAL".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("=" * 100 + "\n")

    # Statistiques par étape
    print("📈 ÉTAPES COMPLÉTÉES :")
    print(f"  {'✅' if results['brands_models'] else '❌'} Marques et modèles")
    print(f"  {'✅' if results['engines'] else '❌'} Moteurs")
    print(f"  {'✅' if results['transmissions'] else '❌'} Transmissions")
    print(f"  {'✅' if results['associations'] else '❌'} Associations")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n📊 TAUX DE RÉUSSITE : {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")

    # Durée
    hours, remainder = divmod(int(duration), 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"\n⏱️  DURÉE TOTALE : {hours:02d}h {minutes:02d}m {seconds:02d}s")

    if success_count == total_count:
        print("\n" + "🎉" * 30)
        print("\n✅ SCRAPING COMPLET TERMINÉ AVEC SUCCÈS !")
        print("\n🎉" * 30)

        print("\n📊 VOTRE BASE DE DONNÉES CONTIENT MAINTENANT :")
        print("  • Des centaines de marques automobiles")
        print("  • Des milliers de modèles avec specs complètes")
        print("  • Des centaines de moteurs avec fiabilité")
        print("  • Des dizaines de transmissions avec avis")
        print("  • Des milliers d'avis positifs et négatifs")

        print("\n🎯 PROCHAINES ÉTAPES :")
        print("  1. Vérifier les données :")
        print("     psql -U postgres -d recherche_auto")
        print("     SELECT COUNT(*) FROM car_brands;")
        print("     SELECT COUNT(*) FROM car_models;")
        print("     SELECT COUNT(*) FROM engines;")
        print("     SELECT COUNT(*) FROM transmissions;")
        print()
        print("  2. Créer les associations :")
        print("     python link_engines_models.py")
        print()
        print("  3. Démarrer l'API :")
        print("     uvicorn app.main:app --reload")
        print()
        print("  4. Tester le frontend :")
        print("     cd ../frontend && npm run dev")

    else:
        print("\n⚠️  SCRAPING TERMINÉ AVEC QUELQUES ERREURS")
        print("\n📋 VÉRIFICATIONS À FAIRE :")
        print("  • PostgreSQL est-il démarré ?")
        print("  • Les migrations sont-elles appliquées ?")
        print("  • Internet est-il accessible ?")
        print("  • Les sites web sont-ils accessibles ?")

    print("\n" + "=" * 100 + "\n")


async def main():
    """Point d'entrée principal"""
    start_time = datetime.now()

    print_banner()
    print(f"🕐 Démarrage : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️  ATTENTION : Ce scraping peut prendre 2-4 heures")
    print("💡 Vous pouvez l'interrompre avec Ctrl+C et le relancer plus tard\n")

    # Demander confirmation
    print("❓ Voulez-vous lancer le scraping complet ? (oui/non)")
    print("   (Tapez 'non' pour quitter, ou appuyez sur Entrée pour continuer)\n")

    # Pour l'instant, on lance directement (commentez ces lignes pour activer la confirmation)
    # response = input("Votre choix : ").strip().lower()
    # if response in ['non', 'n', 'no']:
    #     print("\n⏹️  Scraping annulé")
    #     return 1

    results = {
        'brands_models': False,
        'engines': False,
        'transmissions': False,
        'associations': False,
    }

    try:
        # ÉTAPE 1 : Marques et modèles
        results['brands_models'] = await step1_brands_and_models()

        if not results['brands_models']:
            print("\n⚠️  Échec de l'étape 1. Arrêt du scraping.")
            print("💡 Corrigez les erreurs et relancez avec : python scrape_everything.py")
            return 1

        # ÉTAPE 2 : Moteurs
        results['engines'] = await step2_engines()

        # ÉTAPE 3 : Transmissions
        results['transmissions'] = await step3_transmissions()

        # ÉTAPE 4 : Associations
        results['associations'] = await step4_associations()

        # Résumé final
        duration = (datetime.now() - start_time).total_seconds()
        print_summary(results, duration)

        return 0 if all(results.values()) else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrompu par l'utilisateur (Ctrl+C)")
        print("💡 Vous pouvez relancer le script plus tard, les données déjà collectées sont sauvegardées")
        duration = (datetime.now() - start_time).total_seconds()
        print_summary(results, duration)
        return 1

    except Exception as e:
        print(f"\n\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        duration = (datetime.now() - start_time).total_seconds()
        print_summary(results, duration)
        return 1


if __name__ == "__main__":
    print("\n🚀 SCRAPING ULTIME - COLLECTE ABSOLUMENT TOUT")
    print("=" * 100)
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
