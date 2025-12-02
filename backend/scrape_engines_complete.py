#!/usr/bin/env python3
"""
SCRAPER COMPLET DES MOTEURS
Collecte TOUS les moteurs avec caractéristiques techniques, fiabilité, problèmes communs, avis
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models import Engine
import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import random
import unicodedata

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text"""
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


class EngineCompleteScraper:
    """Scraper complet pour TOUS les moteurs automobiles"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

        # User agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        # Familles de moteurs connues par constructeur
        self.engine_families = {
            'Renault': ['TCe', 'dCi', 'Blue dCi', 'E-Tech'],
            'Peugeot': ['PureTech', 'BlueHDi'],
            'Citroën': ['PureTech', 'BlueHDi'],
            'Volkswagen': ['TSI', 'TDI', 'FSI'],
            'BMW': ['TwinPower Turbo', 'sDrive', 'xDrive'],
            'Mercedes-Benz': ['BlueTEC', 'CGI', 'CDI'],
            'Audi': ['TFSI', 'TDI', 'e-tron'],
            'Toyota': ['VVT-i', 'Hybrid', 'D-4D'],
            'Ford': ['EcoBoost', 'TDCi', 'Duratorq'],
            'Honda': ['i-VTEC', 'i-DTec'],
            'Nissan': ['DIG-T', 'dCi'],
            'Hyundai': ['T-GDi', 'CRDi'],
            'Kia': ['T-GDi', 'CRDi'],
        }

    async def init_playwright(self):
        """Initialise Playwright"""
        print("\n🌐 Initialisation du navigateur...")

        playwright = await async_playwright().start()

        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        self.context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            locale='fr-FR',
        )

        self.page = await self.context.new_page()
        print("✅ Navigateur prêt")

    async def close_playwright(self):
        """Ferme Playwright"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Délai aléatoire"""
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def scrape_engines_for_brand(self, brand_name: str, brand_id: str) -> List[Dict]:
        """Scrape TOUS les moteurs d'une marque"""
        print(f"\n🔧 Scraping moteurs pour {brand_name}...")

        engines = []

        # Méthode 1 : Utiliser les familles de moteurs connues
        if brand_name in self.engine_families:
            for family in self.engine_families[brand_name]:
                engine_data = await self.scrape_engine_family(brand_name, brand_id, family)
                engines.extend(engine_data)

        # Méthode 2 : Scraper depuis les sources web
        web_engines = await self.scrape_engines_web(brand_name, brand_id)
        engines.extend(web_engines)

        # Dédupliquer
        unique_engines = {}
        for engine in engines:
            key = f"{engine.get('code', '')}-{engine.get('displacement', '')}"
            if key not in unique_engines:
                unique_engines[key] = engine

        final_engines = list(unique_engines.values())
        print(f"✅ {len(final_engines)} moteurs collectés pour {brand_name}")

        return final_engines

    async def scrape_engine_family(self, brand_name: str, brand_id: str, family: str) -> List[Dict]:
        """Scrape une famille de moteurs spécifique"""
        print(f"  📖 Famille: {family}")

        engines = []

        # Configurations courantes par cylindrée
        displacements = ['1.0', '1.2', '1.4', '1.5', '1.6', '1.8', '2.0', '2.2', '2.5', '3.0']
        fuel_types = ['Essence', 'Diesel', 'Hybride']

        for displacement in displacements:
            for fuel_type in fuel_types:
                # Créer un moteur type
                code = f"{family} {displacement}"
                engine_id = generate_slug(f"{brand_name}-{code}")

                # Chercher les specs en ligne
                specs = await self.search_engine_specs(brand_name, code, fuel_type)

                if specs.get('found'):
                    engine_data = {
                        'id': engine_id,
                        'code': code,
                        'manufacturer': brand_name,
                        'fuel_type': fuel_type,
                        'displacement': float(displacement) if displacement else None,
                        'horsepower': specs.get('horsepower'),
                        'torque': specs.get('torque'),
                        'cylinders': specs.get('cylinders'),
                        'configuration': specs.get('configuration'),
                        'aspiration': specs.get('aspiration'),
                        'reliability_score': specs.get('reliability_score'),
                        'common_issues': specs.get('common_issues', []),
                        'maintenance_cost': specs.get('maintenance_cost'),
                        'advantages': specs.get('advantages', []),
                        'disadvantages': specs.get('disadvantages', []),
                    }

                    engines.append(engine_data)
                    print(f"    ✓ {code} {fuel_type} ({specs.get('horsepower', '?')} ch)")

        return engines

    async def search_engine_specs(self, brand: str, code: str, fuel_type: str) -> Dict:
        """Recherche les specs d'un moteur sur Internet"""
        specs = {'found': False}

        try:
            # Construire la requête de recherche
            query = f"{brand} {code} {fuel_type} moteur caractéristiques"
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            await self.page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
            await self.random_delay(1, 2)

            # Extraire des infos depuis les résultats
            page_text = await self.page.inner_text('body')

            # Chercher les specs
            hp_match = re.search(r'(\d+)\s*ch|(\d+)\s*CV', page_text, re.IGNORECASE)
            if hp_match:
                specs['horsepower'] = int(hp_match.group(1) or hp_match.group(2))
                specs['found'] = True

            torque_match = re.search(r'(\d+)\s*Nm', page_text, re.IGNORECASE)
            if torque_match:
                specs['torque'] = int(torque_match.group(1))

            # Configuration (4 cylindres, V6, etc.)
            config_match = re.search(r'(\d+)\s*cylindres|V(\d+)|L(\d+)', page_text, re.IGNORECASE)
            if config_match:
                specs['cylinders'] = int(config_match.group(1) or config_match.group(2) or config_match.group(3))

            # Aspiration
            if 'turbo' in page_text.lower():
                specs['aspiration'] = 'Turbo'
            elif 'compresseur' in page_text.lower():
                specs['aspiration'] = 'Compresseur'
            else:
                specs['aspiration'] = 'Atmosphérique'

            # Fiabilité (estimation basique)
            if 'fiable' in page_text.lower():
                specs['reliability_score'] = 4
            elif 'problème' in page_text.lower() or 'panne' in page_text.lower():
                specs['reliability_score'] = 2
            else:
                specs['reliability_score'] = 3

        except Exception as e:
            pass

        return specs

    async def scrape_engines_web(self, brand_name: str, brand_id: str) -> List[Dict]:
        """Scrape les moteurs depuis les sites spécialisés"""
        print(f"  📖 Source: Sites spécialisés...")

        engines = []

        try:
            # Caradisiac fiabilité
            url = f"https://www.caradisiac.com/fiabilite/{generate_slug(brand_name)}/"

            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 3)

            # Chercher les sections moteurs
            engine_sections = await self.page.query_selector_all('.engine-item, .moteur, [class*="engine"]')

            for section in engine_sections[:20]:
                try:
                    text = await section.inner_text()

                    # Extraire le code moteur
                    code_match = re.search(r'([A-Z0-9]+(?:\s+[A-Z0-9]+)*)', text)
                    if code_match:
                        code = code_match.group(1)
                        engine_id = generate_slug(f"{brand_name}-{code}")

                        # Extraire les specs
                        hp_match = re.search(r'(\d+)\s*ch', text)
                        displacement_match = re.search(r'(\d+\.?\d*)\s*L', text)

                        engines.append({
                            'id': engine_id,
                            'code': code,
                            'manufacturer': brand_name,
                            'horsepower': int(hp_match.group(1)) if hp_match else None,
                            'displacement': float(displacement_match.group(1)) if displacement_match else None,
                        })

                        print(f"    ✓ {code}")

                except:
                    continue

        except Exception as e:
            print(f"    ⚠️  Erreur web scraping: {e}")

        return engines

    async def save_engines_to_db(self, engines: List[Dict]):
        """Sauvegarde les moteurs dans la base"""
        if not engines:
            return

        print(f"\n💾 Sauvegarde de {len(engines)} moteurs...")

        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                saved_count = 0

                for idx, engine_data in enumerate(engines, 1):
                    # Convertir listes en JSON
                    if 'common_issues' in engine_data and isinstance(engine_data['common_issues'], list):
                        engine_data['common_issues'] = json.dumps(engine_data['common_issues'])
                    if 'advantages' in engine_data and isinstance(engine_data['advantages'], list):
                        engine_data['advantages'] = json.dumps(engine_data['advantages'])
                    if 'disadvantages' in engine_data and isinstance(engine_data['disadvantages'], list):
                        engine_data['disadvantages'] = json.dumps(engine_data['disadvantages'])

                    # Vérifier si existe
                    result = await session.execute(
                        text(f"SELECT id FROM engines WHERE id = '{engine_data['id']}' LIMIT 1")
                    )
                    existing = result.first()

                    if existing:
                        continue

                    # Filtrer les clés valides
                    valid_keys = ['id', 'code', 'manufacturer', 'fuel_type', 'displacement',
                                  'horsepower', 'torque', 'cylinders', 'configuration',
                                  'aspiration', 'reliability_score', 'common_issues',
                                  'maintenance_cost']
                    filtered_data = {k: v for k, v in engine_data.items() if k in valid_keys}

                    engine_obj = Engine(**filtered_data)
                    session.add(engine_obj)
                    saved_count += 1

                    if idx % 20 == 0:
                        await session.commit()
                        print(f"  ✅ {idx}/{len(engines)} moteurs traités...")

                await session.commit()
                print(f"✅ {saved_count} nouveaux moteurs sauvegardés !")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                await session.close()

    async def run_complete_scraping(self):
        """Lance la collecte complète de TOUS les moteurs"""
        print("\n" + "=" * 100)
        print("🔧 SCRAPING COMPLET DES MOTEURS".center(100))
        print("=" * 100)

        await self.init_playwright()

        try:
            # Récupérer toutes les marques
            engine = create_async_engine(DATABASE_URL, echo=False)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

            async with async_session() as session:
                result = await session.execute(text("SELECT id, name FROM car_brands ORDER BY name"))
                brands = result.fetchall()

                print(f"\n📊 {len(brands)} marques à traiter")

                total_engines = 0

                for idx, (brand_id, brand_name) in enumerate(brands, 1):
                    print(f"\n[{idx}/{len(brands)}] {brand_name}")
                    print("─" * 80)

                    engines = await self.scrape_engines_for_brand(brand_name, brand_id)

                    if engines:
                        await self.save_engines_to_db(engines)
                        total_engines += len(engines)

                    # Pause entre marques
                    if idx < len(brands):
                        await self.random_delay(2, 4)

                print(f"\n🎉 TERMINÉ !")
                print(f"📊 {total_engines} moteurs collectés")

        finally:
            await self.close_playwright()


async def main():
    scraper = EngineCompleteScraper()
    await scraper.run_complete_scraping()


if __name__ == "__main__":
    asyncio.run(main())
