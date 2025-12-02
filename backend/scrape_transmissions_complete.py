#!/usr/bin/env python3
"""
SCRAPER COMPLET DES TRANSMISSIONS
Collecte TOUTES les transmissions avec fiabilité, problèmes communs, avis utilisateurs
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models import Transmission
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


class TransmissionCompleteScraper:
    """Scraper complet pour TOUTES les transmissions automobiles"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

        # User agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        # Transmissions connues par constructeur
        self.transmission_types = {
            'Renault': [
                {'type': 'Manuelle', 'gears': 5, 'code': 'JH3'},
                {'type': 'Manuelle', 'gears': 6, 'code': 'JR5'},
                {'type': 'Automatique', 'gears': 6, 'code': 'EDC'},
                {'type': 'Automatique', 'gears': 7, 'code': 'EDC'},
            ],
            'Peugeot': [
                {'type': 'Manuelle', 'gears': 5, 'code': 'MA5'},
                {'type': 'Manuelle', 'gears': 6, 'code': 'MA6'},
                {'type': 'Automatique', 'gears': 8, 'code': 'EAT8'},
            ],
            'Volkswagen': [
                {'type': 'Manuelle', 'gears': 5, 'code': 'MQ200'},
                {'type': 'Manuelle', 'gears': 6, 'code': 'MQ250'},
                {'type': 'Automatique', 'gears': 6, 'code': 'DSG'},
                {'type': 'Automatique', 'gears': 7, 'code': 'DSG'},
            ],
            'BMW': [
                {'type': 'Manuelle', 'gears': 6, 'code': 'Getrag'},
                {'type': 'Automatique', 'gears': 8, 'code': 'ZF 8HP'},
            ],
            'Mercedes-Benz': [
                {'type': 'Automatique', 'gears': 7, 'code': '7G-Tronic'},
                {'type': 'Automatique', 'gears': 9, 'code': '9G-Tronic'},
            ],
            'Audi': [
                {'type': 'Manuelle', 'gears': 6, 'code': 'MQ350'},
                {'type': 'Automatique', 'gears': 7, 'code': 'S tronic'},
            ],
            'Toyota': [
                {'type': 'Manuelle', 'gears': 6, 'code': 'iMT'},
                {'type': 'CVT', 'gears': None, 'code': 'Multidrive'},
                {'type': 'Automatique', 'gears': 8, 'code': 'Direct Shift'},
            ],
            'Ford': [
                {'type': 'Manuelle', 'gears': 5, 'code': 'MTX-75'},
                {'type': 'Manuelle', 'gears': 6, 'code': 'IB5'},
                {'type': 'Automatique', 'gears': 6, 'code': 'PowerShift'},
            ],
            'Honda': [
                {'type': 'Manuelle', 'gears': 6, 'code': 'K-Series'},
                {'type': 'CVT', 'gears': None, 'code': 'CVT'},
            ],
        }

        # Problèmes communs par type de transmission
        self.common_issues_by_type = {
            'DSG': [
                'Problèmes de mécatronique',
                'À-coups à basse vitesse',
                'Embrayages à remplacer vers 100-150k km',
            ],
            'EDC': [
                'Embrayage double fragile',
                'Problèmes électroniques',
                'Coût de réparation élevé',
            ],
            'PowerShift': [
                'Problèmes d\'embrayage fréquents',
                'Rappels constructeur',
                'Fiabilité moyenne',
            ],
            'CVT': [
                'Manque de sensations',
                'Fiabilité variable selon marque',
                'Entretien spécifique requis',
            ],
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

    async def scrape_transmissions_for_brand(self, brand_name: str) -> List[Dict]:
        """Scrape TOUTES les transmissions d'une marque"""
        print(f"\n⚙️  Scraping transmissions pour {brand_name}...")

        transmissions = []

        # Méthode 1 : Utiliser les transmissions connues
        if brand_name in self.transmission_types:
            for trans_info in self.transmission_types[brand_name]:
                trans_data = await self.create_transmission_data(brand_name, trans_info)
                transmissions.append(trans_data)

        # Méthode 2 : Scraper depuis le web
        web_transmissions = await self.scrape_transmissions_web(brand_name)
        transmissions.extend(web_transmissions)

        # Dédupliquer
        unique_transmissions = {}
        for trans in transmissions:
            key = f"{trans['type']}-{trans.get('gears', '')}-{trans.get('code', '')}"
            if key not in unique_transmissions:
                unique_transmissions[key] = trans

        final_transmissions = list(unique_transmissions.values())
        print(f"✅ {len(final_transmissions)} transmissions collectées pour {brand_name}")

        return final_transmissions

    async def create_transmission_data(self, brand_name: str, trans_info: Dict) -> Dict:
        """Crée les données complètes d'une transmission"""
        trans_type = trans_info['type']
        gears = trans_info.get('gears')
        code = trans_info.get('code', '')

        # Générer ID unique
        trans_id = generate_slug(f"{brand_name}-{code}-{trans_type}-{gears or 'cvt'}")

        # Chercher les infos détaillées
        details = await self.search_transmission_details(brand_name, code, trans_type)

        # Problèmes communs
        common_issues = []
        if code in self.common_issues_by_type:
            common_issues = self.common_issues_by_type[code]
        elif trans_type in self.common_issues_by_type:
            common_issues = self.common_issues_by_type[trans_type]

        # Score de fiabilité basé sur les retours
        reliability_score = details.get('reliability_score', 3)
        if code in ['DSG', 'PowerShift']:
            reliability_score = 2  # Connus pour problèmes
        elif code in ['ZF 8HP', 'Aisin']:
            reliability_score = 5  # Très fiables

        trans_data = {
            'id': trans_id,
            'type': trans_type,
            'gears': gears,
            'code': code,
            'manufacturer': details.get('manufacturer', 'Interne'),
            'reliability_score': reliability_score,
            'common_issues': common_issues,
            'maintenance_cost': details.get('maintenance_cost', 'Moyen'),
            'advantages': details.get('advantages', []),
            'disadvantages': details.get('disadvantages', []),
        }

        print(f"  ✓ {trans_type} {gears or 'CVT'} vitesses ({code})")

        return trans_data

    async def search_transmission_details(self, brand: str, code: str, trans_type: str) -> Dict:
        """Recherche les détails d'une transmission sur Internet"""
        details = {}

        try:
            # Construire la requête
            query = f"{brand} {code} transmission {trans_type} avis fiabilité"
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            await self.page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
            await self.random_delay(1, 2)

            page_text = await self.page.inner_text('body')

            # Chercher le fabricant
            if 'ZF' in page_text:
                details['manufacturer'] = 'ZF'
            elif 'Aisin' in page_text:
                details['manufacturer'] = 'Aisin'
            elif 'Getrag' in page_text:
                details['manufacturer'] = 'Getrag'

            # Chercher les avis
            if 'fiable' in page_text.lower() or 'robuste' in page_text.lower():
                details['reliability_score'] = 4
                details['advantages'] = ['Bonne fiabilité', 'Durabilité prouvée']
            elif 'problème' in page_text.lower() or 'défaut' in page_text.lower():
                details['reliability_score'] = 2
                details['disadvantages'] = ['Problèmes connus', 'Fiabilité moyenne']

            # Coût d'entretien
            if 'cher' in page_text.lower() or 'coûteux' in page_text.lower():
                details['maintenance_cost'] = 'Élevé'
            elif 'économique' in page_text.lower():
                details['maintenance_cost'] = 'Faible'

        except Exception as e:
            pass

        return details

    async def scrape_transmissions_web(self, brand_name: str) -> List[Dict]:
        """Scrape les transmissions depuis les sites spécialisés"""
        print(f"  📖 Source: Sites spécialisés...")

        transmissions = []

        try:
            # Caradisiac fiabilité
            url = f"https://www.caradisiac.com/fiabilite/{generate_slug(brand_name)}/"

            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 3)

            # Chercher les sections transmissions
            trans_sections = await self.page.query_selector_all('.transmission-item, .boite, [class*="transmission"]')

            for section in trans_sections[:10]:
                try:
                    text = await section.inner_text()

                    # Extraire le type
                    trans_type = 'Manuelle'
                    if 'automatique' in text.lower():
                        trans_type = 'Automatique'
                    elif 'cvt' in text.lower():
                        trans_type = 'CVT'

                    # Extraire nombre de vitesses
                    gears_match = re.search(r'(\d+)\s*(?:vitesses?|rapports?)', text, re.IGNORECASE)
                    gears = int(gears_match.group(1)) if gears_match else None

                    # Extraire code
                    code_match = re.search(r'([A-Z0-9-]+(?:\s+[A-Z0-9-]+)*)', text)
                    code = code_match.group(1) if code_match else ''

                    trans_id = generate_slug(f"{brand_name}-{code}-{trans_type}-{gears or 'cvt'}")

                    transmissions.append({
                        'id': trans_id,
                        'type': trans_type,
                        'gears': gears,
                        'code': code,
                    })

                    print(f"    ✓ {trans_type} {gears or 'CVT'} vitesses")

                except:
                    continue

        except Exception as e:
            print(f"    ⚠️  Erreur web scraping: {e}")

        return transmissions

    async def save_transmissions_to_db(self, transmissions: List[Dict]):
        """Sauvegarde les transmissions dans la base"""
        if not transmissions:
            return

        print(f"\n💾 Sauvegarde de {len(transmissions)} transmissions...")

        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                saved_count = 0

                for idx, trans_data in enumerate(transmissions, 1):
                    # Convertir listes en JSON
                    if 'common_issues' in trans_data and isinstance(trans_data['common_issues'], list):
                        trans_data['common_issues'] = json.dumps(trans_data['common_issues'])
                    if 'advantages' in trans_data and isinstance(trans_data['advantages'], list):
                        trans_data['advantages'] = json.dumps(trans_data['advantages'])
                    if 'disadvantages' in trans_data and isinstance(trans_data['disadvantages'], list):
                        trans_data['disadvantages'] = json.dumps(trans_data['disadvantages'])

                    # Vérifier si existe
                    result = await session.execute(
                        text(f"SELECT id FROM transmissions WHERE id = '{trans_data['id']}' LIMIT 1")
                    )
                    existing = result.first()

                    if existing:
                        continue

                    # Filtrer les clés valides
                    valid_keys = ['id', 'type', 'gears', 'code', 'manufacturer',
                                  'reliability_score', 'common_issues', 'maintenance_cost']
                    filtered_data = {k: v for k, v in trans_data.items() if k in valid_keys}

                    trans_obj = Transmission(**filtered_data)
                    session.add(trans_obj)
                    saved_count += 1

                    if idx % 20 == 0:
                        await session.commit()
                        print(f"  ✅ {idx}/{len(transmissions)} transmissions traitées...")

                await session.commit()
                print(f"✅ {saved_count} nouvelles transmissions sauvegardées !")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                await session.close()

    async def run_complete_scraping(self):
        """Lance la collecte complète de TOUTES les transmissions"""
        print("\n" + "=" * 100)
        print("⚙️  SCRAPING COMPLET DES TRANSMISSIONS".center(100))
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

                total_transmissions = 0

                for idx, (brand_id, brand_name) in enumerate(brands, 1):
                    print(f"\n[{idx}/{len(brands)}] {brand_name}")
                    print("─" * 80)

                    transmissions = await self.scrape_transmissions_for_brand(brand_name)

                    if transmissions:
                        await self.save_transmissions_to_db(transmissions)
                        total_transmissions += len(transmissions)

                    # Pause entre marques
                    if idx < len(brands):
                        await self.random_delay(2, 4)

                print(f"\n🎉 TERMINÉ !")
                print(f"📊 {total_transmissions} transmissions collectées")

        finally:
            await self.close_playwright()


async def main():
    scraper = TransmissionCompleteScraper()
    await scraper.run_complete_scraping()


if __name__ == "__main__":
    asyncio.run(main())
