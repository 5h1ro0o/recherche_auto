#!/usr/bin/env python3
"""
Script de web scraping pour collecter TOUTES les données de transmissions automobiles
Collecte automatique depuis :
- Sites techniques spécialisés boîtes de vitesses
- Forums d'expertise mécanique
- Retours de fiabilité (Caradisiac, L'Argus, forums)
- Bases de données constructeurs
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Transmission
import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

class TransmissionWebScraper:
    """Scraper automatique pour collecter toutes les données de transmissions"""

    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }

        # Sites sources pour données transmissions
        self.data_sources = {
            'technical': [
                'https://www.automobile-catalog.com/transmission/',
                'https://www.gearboxes-database.com/',
            ],
            'reliability': [
                'https://www.caradisiac.com/fiabilite/boites-vitesses/',
                'https://www.largus.fr/fiabilite/transmissions/',
                'https://www.forum-auto.caradisiac.com/automobile-pratique/',
            ],
        }

        # Transmissions courantes par constructeur
        self.common_transmissions = {
            'Renault': [
                {'name': 'JH3 5MT', 'type': 'Manuelle', 'gears': 5},
                {'name': 'PF6 6MT', 'type': 'Manuelle', 'gears': 6},
                {'name': 'EDC 6', 'type': 'Robotisée double embrayage', 'gears': 6},
                {'name': 'EDC 7', 'type': 'Robotisée double embrayage', 'gears': 7},
            ],
            'PSA': [
                {'name': 'BE4R 6MT', 'type': 'Manuelle', 'gears': 6},
                {'name': 'EAT6', 'type': 'Automatique', 'gears': 6},
                {'name': 'EAT8', 'type': 'Automatique', 'gears': 8},
            ],
            'Volkswagen': [
                {'name': 'MQ250 6MT', 'type': 'Manuelle', 'gears': 6},
                {'name': 'DSG 6 DQ250', 'type': 'Robotisée double embrayage', 'gears': 6},
                {'name': 'DSG 7 DQ200', 'type': 'Robotisée double embrayage', 'gears': 7},
                {'name': 'DSG 7 DQ381', 'type': 'Robotisée double embrayage', 'gears': 7},
            ],
            'BMW': [
                {'name': 'Getrag 6MT', 'type': 'Manuelle', 'gears': 6},
                {'name': 'ZF 8HP', 'type': 'Automatique', 'gears': 8},
            ],
            'Mercedes-Benz': [
                {'name': '9G-Tronic', 'type': 'Automatique', 'gears': 9},
                {'name': '7G-Tronic', 'type': 'Automatique', 'gears': 7},
            ],
            'Toyota': [
                {'name': 'E-CVT Hybrid', 'type': 'CVT électrique', 'gears': 0},
            ],
            'Ford': [
                {'name': 'Powershift 6DCT', 'type': 'Robotisée double embrayage', 'gears': 6},
                {'name': 'Getrag 6MT', 'type': 'Manuelle', 'gears': 6},
            ],
            'Aisin': [
                {'name': 'EAT8', 'type': 'Automatique', 'gears': 8},
            ],
            'ZF': [
                {'name': '8HP', 'type': 'Automatique', 'gears': 8},
            ],
        }

    async def init_session(self):
        """Initialise la session HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()

    async def fetch_url(self, url: str, retries: int = 3) -> Optional[str]:
        """Récupère le contenu d'une URL avec retry"""
        for attempt in range(retries):
            try:
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"⚠️  Status {response.status} pour {url}")
            except Exception as e:
                print(f"⚠️  Erreur {attempt + 1}/{retries}: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        return None

    async def scrape_transmission_specs(self, manufacturer: str, trans_name: str) -> Optional[Dict]:
        """Scrape les specs techniques d'une transmission"""
        print(f"\n🔍 Scraping specs transmission {manufacturer} {trans_name}...")

        trans_data = {
            'name': trans_name,
            'manufacturer': manufacturer,
        }

        try:
            # URL recherche transmission
            search_query = f"{manufacturer}+{trans_name}+specifications".replace(' ', '+')
            search_url = f"https://www.google.com/search?q={search_query}"

            html = await self.fetch_url(search_url)
            if not html:
                return trans_data

            soup = BeautifulSoup(html, 'html.parser')

            # Chercher dans les résultats
            # Note: Le scraping Google est limité, utiliser des sources spécialisées serait mieux

            # Données par défaut basées sur connaissances communes
            # (à enrichir avec du vrai scraping de sites spécialisés)

        except Exception as e:
            print(f"❌ Erreur scraping specs: {str(e)}")

        return trans_data

    async def scrape_caradisiac_transmission_reliability(self, manufacturer: str, trans_name: str) -> Dict:
        """Scrape la fiabilité d'une transmission depuis Caradisiac"""
        print(f"\n⚙️  Scraping fiabilité Caradisiac pour {manufacturer} {trans_name}...")

        reliability_data = {
            'reliability_rating': 0.0,
            'smoothness_rating': 0.0,
            'efficiency_rating': 0.0,
            'advantages': [],
            'disadvantages': [],
            'common_issues': "",
            'reviews': [],
            'maintenance_cost': "",
        }

        try:
            # Recherche sur Caradisiac
            search_query = f"{manufacturer}+{trans_name}+fiabilité+boîte".replace(' ', '+')
            search_url = f"https://www.caradisiac.com/recherche/?q={search_query}"

            html = await self.fetch_url(search_url)
            if not html:
                return reliability_data

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver l'article de fiabilité
            article_links = soup.find_all('a', href=re.compile(r'/(fiabilite|boite-vitesses)/'))

            if article_links:
                article_url = article_links[0].get('href')
                if not article_url.startswith('http'):
                    article_url = f"https://www.caradisiac.com{article_url}"

                article_html = await self.fetch_url(article_url)
                if article_html:
                    article_soup = BeautifulSoup(article_html, 'html.parser')

                    # Extraire note de fiabilité
                    rating_elem = article_soup.find('span', class_='reliability-score')
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        numbers = re.findall(r'\d+\.?\d*', rating_text)
                        if numbers:
                            reliability_data['reliability_rating'] = float(numbers[0])

                    # Extraire avantages
                    pros_section = article_soup.find('div', class_='transmission-pros')
                    if pros_section:
                        pros = pros_section.find_all('li')
                        reliability_data['advantages'] = [p.get_text(strip=True) for p in pros]

                    # Extraire inconvénients
                    cons_section = article_soup.find('div', class_='transmission-cons')
                    if cons_section:
                        cons = cons_section.find_all('li')
                        reliability_data['disadvantages'] = [c.get_text(strip=True) for c in cons]

                    # Extraire problèmes communs
                    issues_elem = article_soup.find('div', class_='common-problems')
                    if issues_elem:
                        reliability_data['common_issues'] = issues_elem.get_text(strip=True)

                    # Extraire avis utilisateurs
                    reviews_section = article_soup.find_all('div', class_='user-review')
                    for review in reviews_section[:5]:
                        review_text = review.get_text(strip=True)
                        if review_text:
                            reliability_data['reviews'].append(review_text[:200])

        except Exception as e:
            print(f"❌ Erreur scraping Caradisiac: {str(e)}")

        return reliability_data

    async def scrape_forum_transmission_feedback(self, manufacturer: str, trans_name: str) -> List[str]:
        """Scrape les retours des forums pour une transmission"""
        print(f"\n💬 Scraping forums pour {manufacturer} {trans_name}...")

        feedbacks = []

        try:
            # Recherche sur forum Caradisiac
            search_query = f"{manufacturer}+{trans_name}+boîte+problème".replace(' ', '+')
            forum_url = f"https://www.forum-auto.caradisiac.com/recherche.php?q={search_query}"

            html = await self.fetch_url(forum_url)
            if not html:
                return feedbacks

            soup = BeautifulSoup(html, 'html.parser')

            # Extraire les posts
            posts = soup.find_all('div', class_='post-content')

            for post in posts[:10]:
                text = post.get_text(strip=True)
                if len(text) > 50:
                    feedbacks.append(text[:250])

        except Exception as e:
            print(f"❌ Erreur scraping forums: {str(e)}")

        return feedbacks

    async def scrape_largus_transmission_data(self, manufacturer: str, trans_name: str) -> Dict:
        """Scrape données L'Argus pour une transmission"""
        print(f"\n📊 Scraping L'Argus pour {manufacturer} {trans_name}...")

        trans_data = {}

        try:
            search_query = f"{manufacturer}-{trans_name}-boite".lower().replace(' ', '-')
            search_url = f"https://www.largus.fr/transmissions/{search_query}"

            html = await self.fetch_url(search_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Extraire tableau specs
                specs_table = soup.find('table', class_='transmission-specs')
                if specs_table:
                    rows = specs_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True).lower()
                            value = cells[1].get_text(strip=True)

                            if 'rapports' in key or 'vitesses' in key:
                                trans_data['gears'] = self.parse_number(value)
                            elif 'couple' in key:
                                trans_data['max_torque_nm'] = self.parse_number(value)
                            elif 'poids' in key:
                                trans_data['weight_kg'] = self.parse_number(value)
                            elif 'applications' in key:
                                trans_data['applications'] = value

        except Exception as e:
            print(f"❌ Erreur scraping L'Argus: {str(e)}")

        return trans_data

    async def collect_all_transmissions_data(self) -> List[Dict]:
        """Collecte toutes les données de transmissions pour tous les constructeurs"""
        print(f"\n{'='*80}")
        print(f"⚙️  Collecte de TOUTES les transmissions depuis Internet")
        print(f"{'='*80}")

        all_transmissions = []

        for manufacturer, transmissions in self.common_transmissions.items():
            for trans_info in transmissions:
                trans_name = trans_info['name']

                print(f"\n{'='*60}")
                print(f"Collecte transmission: {manufacturer} {trans_name}")
                print(f"{'='*60}")

                # Données de base
                trans_data = {
                    'name': trans_name,
                    'manufacturer': manufacturer,
                    'type': trans_info['type'],
                    'gears': trans_info['gears'],
                }

                # 1. Specs techniques
                specs = await self.scrape_transmission_specs(manufacturer, trans_name)
                if specs:
                    trans_data.update(specs)

                # 2. Fiabilité Caradisiac
                reliability = await self.scrape_caradisiac_transmission_reliability(manufacturer, trans_name)
                trans_data.update(reliability)

                # 3. Données L'Argus
                largus_data = await self.scrape_largus_transmission_data(manufacturer, trans_name)
                trans_data.update(largus_data)

                # 4. Retours forums
                forum_feedback = await self.scrape_forum_transmission_feedback(manufacturer, trans_name)
                if forum_feedback:
                    if 'reviews' not in trans_data:
                        trans_data['reviews'] = []
                    trans_data['reviews'].extend(forum_feedback)

                all_transmissions.append(trans_data)

                await asyncio.sleep(3)  # Respecter les serveurs

        return all_transmissions

    async def save_transmissions_to_db(self, transmissions: List[Dict]):
        """Sauvegarde les transmissions dans la base de données"""
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                for idx, trans_data in enumerate(transmissions, 1):
                    # Nettoyer les données
                    cleaned_data = {k: v for k, v in trans_data.items() if v is not None and v != ''}

                    # Créer la transmission
                    transmission = Transmission(**cleaned_data)
                    session.add(transmission)

                    if idx % 10 == 0:
                        await session.commit()
                        print(f"✅ {idx}/{len(transmissions)} transmissions sauvegardées...")

                await session.commit()
                print(f"\n✅ Total: {len(transmissions)} transmissions sauvegardées dans la base de données")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur sauvegarde: {str(e)}")
                raise
            finally:
                await session.close()

    def parse_number(self, text: str) -> Optional[int]:
        """Parse un nombre depuis du texte"""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None


async def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("WEB SCRAPING AUTOMATIQUE - TRANSMISSIONS AUTOMOBILES")
    print("Collecte TOUTES les données depuis Internet")
    print("=" * 80)

    scraper = TransmissionWebScraper()
    await scraper.init_session()

    try:
        transmissions = await scraper.collect_all_transmissions_data()

        if transmissions:
            await scraper.save_transmissions_to_db(transmissions)
            print(f"\n🎉 TOTAL: {len(transmissions)} transmissions collectées et sauvegardées !")

    finally:
        await scraper.close_session()

    print("\n" + "=" * 80)
    print("Script terminé !")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
