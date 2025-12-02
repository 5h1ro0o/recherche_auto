#!/usr/bin/env python3
"""
Script principal pour lancer TOUS les scrapers de l'encyclopédie automobile
Collecte automatiquement TOUTES les données depuis Internet :
- Modèles de voitures (specs, avis, caractéristiques)
- Moteurs (specs techniques, fiabilité, problèmes communs)
- Transmissions (fiabilité, retours utilisateurs)
- Marques (historique, réputation)
"""

import asyncio
import sys
import os
from datetime import datetime

# Importer les scrapers
try:
    from scrape_models_web import AutoWebScraper
    from scrape_engines_web import EngineWebScraper
    from scrape_transmissions_web import TransmissionWebScraper
except ImportError as e:
    print(f"❌ Erreur import des scrapers: {e}")
    print("Assurez-vous que tous les scripts sont dans le même répertoire")
    sys.exit(1)


class MasterScraper:
    """Orchestrateur principal de tous les scrapers"""

    def __init__(self):
        self.start_time = None
        self.stats = {
            'models': 0,
            'engines': 0,
            'transmissions': 0,
            'errors': 0,
        }

    def print_banner(self):
        """Affiche la bannière de démarrage"""
        print("\n")
        print("=" * 100)
        print("║" + " " * 98 + "║")
        print("║" + "SCRAPING AUTOMATIQUE ENCYCLOPÉDIE AUTOMOBILE".center(98) + "║")
        print("║" + " " * 98 + "║")
        print("║" + "Collecte TOUTES les données depuis Internet".center(98) + "║")
        print("║" + " " * 98 + "║")
        print("=" * 100)
        print("\n")

    def print_section(self, title: str):
        """Affiche un titre de section"""
        print("\n")
        print("┌" + "─" * 98 + "┐")
        print("│" + title.center(98) + "│")
        print("└" + "─" * 98 + "┘")
        print("\n")

    async def scrape_all_models(self):
        """Lance le scraping de tous les modèles"""
        self.print_section("🚗 SCRAPING DES MODÈLES AUTOMOBILES")

        scraper = AutoWebScraper()
        await scraper.init_session()

        try:
            # Récupérer les marques depuis la DB
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from sqlalchemy.orm import sessionmaker
            from dotenv import load_dotenv

            load_dotenv()
            DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

            engine = create_async_engine(DATABASE_URL, echo=False)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

            async with async_session() as session:
                result = await session.execute("SELECT id, name FROM car_brands")
                brands = result.fetchall()

                print(f"📋 {len(brands)} marques trouvées")
                print("🌐 Sources : CarQuery API, Automobile-Catalog, Caradisiac, L'Argus")
                print("\n")

                total_models = []

                for brand_id, brand_name in brands:
                    print(f"\n{'─' * 80}")
                    print(f"Marque: {brand_name}")
                    print(f"{'─' * 80}")

                    models = await scraper.collect_all_models_for_brand(brand_name, brand_id)
                    total_models.extend(models)

                    print(f"✅ {brand_name}: {len(models)} modèles collectés")

                    # Sauvegarder par batch
                    if len(total_models) >= 50:
                        await scraper.save_models_to_db(total_models)
                        self.stats['models'] += len(total_models)
                        total_models = []

                # Sauvegarder le reste
                if total_models:
                    await scraper.save_models_to_db(total_models)
                    self.stats['models'] += len(total_models)

                print(f"\n✅ TOTAL MODÈLES: {self.stats['models']} collectés et sauvegardés")

        except Exception as e:
            print(f"❌ Erreur scraping modèles: {e}")
            self.stats['errors'] += 1
        finally:
            await scraper.close_session()

    async def scrape_all_engines(self):
        """Lance le scraping de tous les moteurs"""
        self.print_section("🔧 SCRAPING DES MOTEURS AUTOMOBILES")

        scraper = EngineWebScraper()
        await scraper.init_session()

        try:
            manufacturers = [
                'Renault', 'PSA', 'Volkswagen', 'BMW', 'Mercedes-Benz',
                'Audi', 'Toyota', 'Ford', 'Honda', 'Nissan', 'Hyundai', 'Kia'
            ]

            print(f"📋 {len(manufacturers)} constructeurs")
            print("🌐 Sources : Automobile-Catalog, Caradisiac, L'Argus, Forums")
            print("\n")

            engines = await scraper.collect_all_engines_data(manufacturers)

            if engines:
                await scraper.save_engines_to_db(engines)
                self.stats['engines'] = len(engines)
                print(f"\n✅ TOTAL MOTEURS: {self.stats['engines']} collectés et sauvegardés")

        except Exception as e:
            print(f"❌ Erreur scraping moteurs: {e}")
            self.stats['errors'] += 1
        finally:
            await scraper.close_session()

    async def scrape_all_transmissions(self):
        """Lance le scraping de toutes les transmissions"""
        self.print_section("⚙️  SCRAPING DES TRANSMISSIONS AUTOMOBILES")

        scraper = TransmissionWebScraper()
        await scraper.init_session()

        try:
            print("🌐 Sources : Caradisiac, L'Argus, Forums automobiles")
            print("\n")

            transmissions = await scraper.collect_all_transmissions_data()

            if transmissions:
                await scraper.save_transmissions_to_db(transmissions)
                self.stats['transmissions'] = len(transmissions)
                print(f"\n✅ TOTAL TRANSMISSIONS: {self.stats['transmissions']} collectées et sauvegardées")

        except Exception as e:
            print(f"❌ Erreur scraping transmissions: {e}")
            self.stats['errors'] += 1
        finally:
            await scraper.close_session()

    def print_final_stats(self):
        """Affiche les statistiques finales"""
        duration = datetime.now() - self.start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        print("\n")
        print("=" * 100)
        print("║" + " " * 98 + "║")
        print("║" + "STATISTIQUES FINALES".center(98) + "║")
        print("║" + " " * 98 + "║")
        print("=" * 100)
        print(f"\n📊 Modèles collectés      : {self.stats['models']:>6}")
        print(f"📊 Moteurs collectés      : {self.stats['engines']:>6}")
        print(f"📊 Transmissions collectées: {self.stats['transmissions']:>6}")
        print(f"{'─' * 50}")
        print(f"📊 TOTAL                  : {sum([self.stats['models'], self.stats['engines'], self.stats['transmissions']]):>6}")
        print(f"\n⚠️  Erreurs               : {self.stats['errors']:>6}")
        print(f"\n⏱️  Durée totale          : {hours:02d}h {minutes:02d}m {seconds:02d}s")
        print("\n" + "=" * 100)

        if self.stats['errors'] == 0:
            print("\n✅ Scraping terminé avec succès !")
        else:
            print(f"\n⚠️  Scraping terminé avec {self.stats['errors']} erreur(s)")

        print("\n")

    async def run(self):
        """Lance tous les scrapers séquentiellement"""
        self.start_time = datetime.now()
        self.print_banner()

        print(f"🕐 Démarrage: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. Scraper les modèles
        await self.scrape_all_models()

        # 2. Scraper les moteurs
        await self.scrape_all_engines()

        # 3. Scraper les transmissions
        await self.scrape_all_transmissions()

        # Afficher les stats finales
        self.print_final_stats()


async def main():
    """Point d'entrée principal"""
    master = MasterScraper()

    try:
        await master.run()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrompu par l'utilisateur")
        master.print_final_stats()
        return 1
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
