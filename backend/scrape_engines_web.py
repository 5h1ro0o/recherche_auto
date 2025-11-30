#!/usr/bin/env python3
"""
Script de web scraping pour collecter TOUTES les données de moteurs automobiles
Collecte automatique depuis :
- Sites techniques spécialisés moteurs
- Forums d'experts mécaniques
- Bases de données constructeurs
- Avis de fiabilité (Caradisiac, L'Argus, forums)
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Engine
import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

class EngineWebScraper:
    """Scraper automatique pour collecter toutes les données de moteurs"""

    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }

        # Sites sources pour données moteurs
        self.data_sources = {
            'technical': [
                'https://www.automobile-catalog.com/engine/',
                'https://www.ultimatespecs.com/car-specs/engine/',
                'https://www.motortrend.com/cars/engine-specs/',
            ],
            'reliability': [
                'https://www.caradisiac.com/fiabilite/',
                'https://www.largus.fr/fiabilite/',
                'https://www.forum-auto.caradisiac.com/',
            ],
            'forums': [
                'https://www.forum-peugeot.com/',
                'https://www.forum-renault.com/',
                'https://www.vwforum.com/',
            ]
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

    async def scrape_engine_specs_catalog(self, manufacturer: str, engine_code: str) -> Optional[Dict]:
        """Scrape les specs techniques d'un moteur depuis automobile-catalog"""
        print(f"\n🔍 Scraping specs moteur {manufacturer} {engine_code}...")

        engine_data = {}

        try:
            # URL recherche moteur
            search_url = f"https://www.automobile-catalog.com/engine/{manufacturer.lower()}/{engine_code.lower()}.html"
            html = await self.fetch_url(search_url)

            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            # Extraire les données techniques
            engine_data = {
                'name': self.extract_text(soup, 'h1', 'engine-name'),
                'manufacturer': manufacturer,
                'type': self.extract_text(soup, 'span', 'engine-type'),
                'displacement_cc': self.extract_number(soup, 'span', 'displacement'),
                'cylinders': self.extract_number(soup, 'span', 'cylinders'),
                'configuration': self.extract_text(soup, 'span', 'configuration'),
                'power_hp': self.extract_number(soup, 'span', 'power-hp'),
                'power_kw': self.extract_number(soup, 'span', 'power-kw'),
                'torque_nm': self.extract_number(soup, 'span', 'torque'),
                'max_rpm': self.extract_number(soup, 'span', 'max-rpm'),
                'torque_rpm': self.extract_number(soup, 'span', 'torque-rpm'),
                'fuel_type': self.extract_text(soup, 'span', 'fuel-type'),
                'aspiration': self.extract_text(soup, 'span', 'aspiration'),
                'valvetrain': self.extract_text(soup, 'span', 'valvetrain'),
                'bore_mm': self.extract_float(soup, 'span', 'bore'),
                'stroke_mm': self.extract_float(soup, 'span', 'stroke'),
                'compression_ratio': self.extract_float(soup, 'span', 'compression'),
                'fuel_system': self.extract_text(soup, 'span', 'fuel-system'),
            }

        except Exception as e:
            print(f"❌ Erreur scraping specs: {str(e)}")

        return engine_data if engine_data.get('name') else None

    async def scrape_caradisiac_engine_reliability(self, manufacturer: str, engine_name: str) -> Dict:
        """Scrape la fiabilité d'un moteur depuis Caradisiac"""
        print(f"\n🔧 Scraping fiabilité Caradisiac pour {manufacturer} {engine_name}...")

        reliability_data = {
            'reliability_rating': 0.0,
            'advantages': [],
            'disadvantages': [],
            'common_issues': "",
            'reviews': [],
        }

        try:
            # Recherche sur Caradisiac
            search_query = f"{manufacturer}+{engine_name}+fiabilité".replace(' ', '+')
            search_url = f"https://www.caradisiac.com/recherche/?q={search_query}"

            html = await self.fetch_url(search_url)
            if not html:
                return reliability_data

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver l'article de fiabilité
            article_links = soup.find_all('a', href=re.compile(r'/fiabilite/'))

            if article_links:
                article_url = article_links[0].get('href')
                if not article_url.startswith('http'):
                    article_url = f"https://www.caradisiac.com{article_url}"

                article_html = await self.fetch_url(article_url)
                if article_html:
                    article_soup = BeautifulSoup(article_html, 'html.parser')

                    # Extraire note de fiabilité
                    rating_elem = article_soup.find('span', class_='reliability-rating')
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        numbers = re.findall(r'\d+\.?\d*', rating_text)
                        if numbers:
                            reliability_data['reliability_rating'] = float(numbers[0])

                    # Extraire avantages
                    pros_section = article_soup.find('div', class_='engine-pros')
                    if pros_section:
                        pros = pros_section.find_all('li')
                        reliability_data['advantages'] = [p.get_text(strip=True) for p in pros]

                    # Extraire inconvénients
                    cons_section = article_soup.find('div', class_='engine-cons')
                    if cons_section:
                        cons = cons_section.find_all('li')
                        reliability_data['disadvantages'] = [c.get_text(strip=True) for c in cons]

                    # Extraire problèmes communs
                    issues_section = article_soup.find('div', class_='common-issues')
                    if issues_section:
                        reliability_data['common_issues'] = issues_section.get_text(strip=True)

        except Exception as e:
            print(f"❌ Erreur scraping Caradisiac: {str(e)}")

        return reliability_data

    async def scrape_forum_engine_reviews(self, manufacturer: str, engine_name: str) -> List[str]:
        """Scrape les avis des forums pour un moteur"""
        print(f"\n💬 Scraping avis forums pour {manufacturer} {engine_name}...")

        reviews = []

        try:
            # Recherche sur forum Caradisiac
            search_query = f"{manufacturer}+{engine_name}+avis".replace(' ', '+')
            forum_url = f"https://www.forum-auto.caradisiac.com/recherche.php?q={search_query}"

            html = await self.fetch_url(forum_url)
            if not html:
                return reviews

            soup = BeautifulSoup(html, 'html.parser')

            # Extraire les posts de forum
            posts = soup.find_all('div', class_='forum-post')

            for post in posts[:10]:  # Top 10 posts
                post_text = post.get_text(strip=True)
                if len(post_text) > 50:  # Messages significatifs
                    reviews.append(post_text[:300])  # Limiter à 300 caractères

        except Exception as e:
            print(f"❌ Erreur scraping forums: {str(e)}")

        return reviews

    async def scrape_largus_engine_data(self, manufacturer: str, engine_name: str) -> Dict:
        """Scrape données L'Argus pour un moteur"""
        print(f"\n📊 Scraping L'Argus pour {manufacturer} {engine_name}...")

        engine_data = {}

        try:
            search_query = f"{manufacturer}-{engine_name}".lower().replace(' ', '-')
            search_url = f"https://www.largus.fr/moteurs/{search_query}"

            html = await self.fetch_url(search_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Extraire tableau specs
                specs_table = soup.find('table', class_='engine-specs')
                if specs_table:
                    rows = specs_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True).lower()
                            value = cells[1].get_text(strip=True)

                            # Mapper les clés
                            if 'cylindrée' in key:
                                engine_data['displacement_cc'] = self.parse_number(value)
                            elif 'puissance' in key:
                                engine_data['power_hp'] = self.parse_number(value)
                            elif 'couple' in key:
                                engine_data['torque_nm'] = self.parse_number(value)
                            elif 'application' in key:
                                engine_data['applications'] = value

        except Exception as e:
            print(f"❌ Erreur scraping L'Argus: {str(e)}")

        return engine_data

    async def collect_all_engines_data(self, manufacturers: List[str]) -> List[Dict]:
        """Collecte toutes les données de moteurs pour tous les constructeurs"""
        print(f"\n{'='*80}")
        print(f"🔧 Collecte de TOUS les moteurs pour {len(manufacturers)} constructeurs")
        print(f"{'='*80}")

        all_engines = []

        # Liste des codes moteurs courants par constructeur (à compléter)
        common_engines = {
            'Renault': ['TCe 90', 'TCe 130', 'Blue dCi 115', 'Blue dCi 150', 'dCi 130'],
            'PSA': ['PureTech 110', 'PureTech 130', 'BlueHDi 130', 'BlueHDi 180'],
            'Volkswagen': ['TSI 110', 'TSI 150', 'TDI 115', 'TDI 150', 'TDI 200'],
            'BMW': ['B47', 'B48', 'B58', 'N47', 'N57'],
            'Mercedes-Benz': ['OM654', 'OM656', 'M264', 'M256'],
            'Audi': ['TFSI', 'TDI', 'TFSI e'],
            'Toyota': ['Hybrid 116h', 'Hybrid 184h', 'Hybrid 218h'],
            'Ford': ['EcoBoost', 'EcoBlue', 'Duratorq'],
            'Honda': ['i-VTEC', 'i-MMD', 'e:HEV'],
        }

        for manufacturer in manufacturers:
            if manufacturer not in common_engines:
                continue

            for engine_code in common_engines[manufacturer]:
                print(f"\n{'='*60}")
                print(f"Collecte moteur: {manufacturer} {engine_code}")
                print(f"{'='*60}")

                # 1. Specs techniques
                specs = await self.scrape_engine_specs_catalog(manufacturer, engine_code)
                if not specs:
                    specs = {'name': engine_code, 'manufacturer': manufacturer}

                # 2. Fiabilité Caradisiac
                reliability = await self.scrape_caradisiac_engine_reliability(manufacturer, engine_code)
                specs.update(reliability)

                # 3. Données L'Argus
                largus_data = await self.scrape_largus_engine_data(manufacturer, engine_code)
                specs.update(largus_data)

                # 4. Avis forums
                forum_reviews = await self.scrape_forum_engine_reviews(manufacturer, engine_code)
                if forum_reviews:
                    specs['reviews'] = forum_reviews

                all_engines.append(specs)

                await asyncio.sleep(3)  # Respecter les serveurs

        return all_engines

    async def save_engines_to_db(self, engines: List[Dict]):
        """Sauvegarde les moteurs dans la base de données"""
        engine_db = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine_db, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                for idx, engine_data in enumerate(engines, 1):
                    # Nettoyer les données
                    cleaned_data = {k: v for k, v in engine_data.items() if v is not None}

                    # Créer le moteur
                    car_engine = Engine(**cleaned_data)
                    session.add(car_engine)

                    if idx % 10 == 0:
                        await session.commit()
                        print(f"✅ {idx}/{len(engines)} moteurs sauvegardés...")

                await session.commit()
                print(f"\n✅ Total: {len(engines)} moteurs sauvegardés dans la base de données")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur sauvegarde: {str(e)}")
                raise
            finally:
                await session.close()

    # Méthodes utilitaires
    def extract_text(self, soup, tag: str, class_name: str) -> str:
        elem = soup.find(tag, class_=class_name)
        return elem.get_text(strip=True) if elem else ""

    def extract_number(self, soup, tag: str, class_name: str) -> Optional[int]:
        elem = soup.find(tag, class_=class_name)
        if elem:
            text = elem.get_text(strip=True)
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else None
        return None

    def extract_float(self, soup, tag: str, class_name: str) -> Optional[float]:
        elem = soup.find(tag, class_=class_name)
        if elem:
            text = elem.get_text(strip=True).replace(',', '.')
            numbers = re.findall(r'\d+\.?\d*', text)
            return float(numbers[0]) if numbers else None
        return None

    def parse_number(self, text: str) -> Optional[int]:
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None


async def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("WEB SCRAPING AUTOMATIQUE - MOTEURS AUTOMOBILES")
    print("Collecte TOUTES les données depuis Internet")
    print("=" * 80)

    scraper = EngineWebScraper()
    await scraper.init_session()

    try:
        manufacturers = [
            'Renault', 'PSA', 'Volkswagen', 'BMW', 'Mercedes-Benz',
            'Audi', 'Toyota', 'Ford', 'Honda', 'Nissan'
        ]

        engines = await scraper.collect_all_engines_data(manufacturers)

        if engines:
            await scraper.save_engines_to_db(engines)
            print(f"\n🎉 TOTAL: {len(engines)} moteurs collectés et sauvegardés !")

    finally:
        await scraper.close_session()

    print("\n" + "=" * 80)
    print("Script terminé !")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
