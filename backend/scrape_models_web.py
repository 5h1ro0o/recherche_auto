#!/usr/bin/env python3
"""
Script de web scraping pour collecter TOUTES les données de modèles automobiles
Collecte automatique depuis :
- APIs automobiles (Auto-Data, CarQuery, VehicleDatabases)
- Sites de specs (automobile-catalog.com, cars-data.com)
- Forums et avis (Caradisiac, L'Argus, AutoPlus)
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import CarModel, CarBrand
import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

class AutoWebScraper:
    """Scraper automatique pour collecter toutes les données automobiles sur Internet"""

    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        # Sites sources pour les données
        self.data_sources = {
            'specs': [
                'https://www.automobile-catalog.com',
                'https://www.cars-data.com',
                'https://www.ultimatespecs.com',
            ],
            'reviews': [
                'https://www.caradisiac.com',
                'https://www.largus.fr',
                'https://www.autoplus.fr',
            ],
            'apis': {
                'carquery': 'https://www.carqueryapi.com/api/0.3/',
                'autodata': 'https://api.auto-data.net/v1/',
            }
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
                print(f"⚠️  Erreur tentative {attempt + 1}/{retries} pour {url}: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
        return None

    async def scrape_automobile_catalog(self, brand_name: str) -> List[Dict]:
        """Scrape automobile-catalog.com pour un constructeur"""
        models = []
        print(f"\n🔍 Scraping automobile-catalog.com pour {brand_name}...")

        try:
            # URL de recherche par marque
            search_url = f"https://www.automobile-catalog.com/make/{brand_name.lower()}.html"
            html = await self.fetch_url(search_url)

            if not html:
                return models

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver tous les liens de modèles
            model_links = soup.find_all('a', class_='model-link')

            for link in model_links[:50]:  # Limiter à 50 modèles par marque
                model_url = link.get('href')
                if model_url and not model_url.startswith('http'):
                    model_url = f"https://www.automobile-catalog.com{model_url}"

                # Récupérer les détails du modèle
                model_data = await self.scrape_model_details(model_url)
                if model_data:
                    models.append(model_data)

                await asyncio.sleep(1)  # Respecter le serveur

        except Exception as e:
            print(f"❌ Erreur scraping automobile-catalog pour {brand_name}: {str(e)}")

        return models

    async def scrape_model_details(self, url: str) -> Optional[Dict]:
        """Scrape les détails d'un modèle spécifique"""
        try:
            html = await self.fetch_url(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            # Extraire les données du modèle
            model_data = {
                'name': self.extract_text(soup, 'h1', 'model-name'),
                'year': self.extract_year(soup),
                'body_type': self.extract_text(soup, 'span', 'body-type'),
                'doors': self.extract_number(soup, 'span', 'doors'),
                'seats': self.extract_number(soup, 'span', 'seats'),
                'length_mm': self.extract_dimension(soup, 'length'),
                'width_mm': self.extract_dimension(soup, 'width'),
                'height_mm': self.extract_dimension(soup, 'height'),
                'wheelbase_mm': self.extract_dimension(soup, 'wheelbase'),
                'weight_kg': self.extract_number(soup, 'span', 'weight'),
                'trunk_capacity_liters': self.extract_number(soup, 'span', 'trunk'),
                'max_speed_kmh': self.extract_number(soup, 'span', 'max-speed'),
                'acceleration_0_100_sec': self.extract_float(soup, 'span', 'acceleration'),
                'fuel_consumption_combined': self.extract_float(soup, 'span', 'consumption'),
                'co2_emissions': self.extract_number(soup, 'span', 'co2'),
                'power_hp': self.extract_number(soup, 'span', 'power'),
                'engine_displacement': self.extract_number(soup, 'span', 'displacement'),
                'torque_nm': self.extract_number(soup, 'span', 'torque'),
            }

            return model_data

        except Exception as e:
            print(f"❌ Erreur extraction détails modèle: {str(e)}")
            return None

    async def scrape_caradisiac_reviews(self, brand: str, model: str) -> Dict:
        """Scrape les avis Caradisiac"""
        print(f"\n💬 Scraping avis Caradisiac pour {brand} {model}...")

        reviews_data = {
            'advantages': [],
            'disadvantages': [],
            'reviews': [],
            'reliability_rating': 0.0,
        }

        try:
            # URL de recherche Caradisiac
            search_query = f"{brand}+{model}".replace(' ', '+')
            search_url = f"https://www.caradisiac.com/recherche/?q={search_query}"

            html = await self.fetch_url(search_url)
            if not html:
                return reviews_data

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver le lien vers la fiche technique / avis
            article_links = soup.find_all('a', class_='article-link')

            if article_links:
                article_url = article_links[0].get('href')
                if article_url and not article_url.startswith('http'):
                    article_url = f"https://www.caradisiac.com{article_url}"

                # Récupérer les avis
                article_html = await self.fetch_url(article_url)
                if article_html:
                    article_soup = BeautifulSoup(article_html, 'html.parser')

                    # Extraire avantages
                    advantages_section = article_soup.find('div', class_='pros')
                    if advantages_section:
                        advantages = advantages_section.find_all('li')
                        reviews_data['advantages'] = [adv.get_text(strip=True) for adv in advantages]

                    # Extraire inconvénients
                    disadvantages_section = article_soup.find('div', class_='cons')
                    if disadvantages_section:
                        disadvantages = disadvantages_section.find_all('li')
                        reviews_data['disadvantages'] = [dis.get_text(strip=True) for dis in disadvantages]

                    # Extraire note de fiabilité
                    rating_elem = article_soup.find('span', class_='rating-value')
                    if rating_elem:
                        reviews_data['reliability_rating'] = float(rating_elem.get_text(strip=True))

        except Exception as e:
            print(f"❌ Erreur scraping Caradisiac: {str(e)}")

        return reviews_data

    async def fetch_carquery_api(self, brand: str) -> List[Dict]:
        """Utilise l'API CarQuery pour récupérer les modèles"""
        print(f"\n🌐 API CarQuery pour {brand}...")

        models = []

        try:
            # API CarQuery - liste des modèles
            api_url = f"{self.data_sources['apis']['carquery']}?cmd=getModels&make={brand}"

            async with self.session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()

                    if 'Models' in data:
                        for model in data['Models']:
                            model_data = {
                                'name': model.get('model_name'),
                                'year': model.get('model_year'),
                                'body_type': model.get('model_body'),
                                'doors': model.get('model_doors'),
                                'seats': model.get('model_seats'),
                                'engine_type': model.get('model_engine_type'),
                                'transmission_type': model.get('model_transmission_type'),
                                'drivetrain': model.get('model_drive'),
                                'power_hp': model.get('model_engine_power_hp'),
                                'engine_displacement': model.get('model_engine_cc'),
                                'fuel_type': model.get('model_engine_fuel'),
                            }
                            models.append(model_data)

        except Exception as e:
            print(f"❌ Erreur API CarQuery: {str(e)}")

        return models

    async def scrape_largus_specs(self, brand: str, model: str) -> Dict:
        """Scrape les specs depuis L'Argus"""
        print(f"\n📊 Scraping L'Argus pour {brand} {model}...")

        specs = {}

        try:
            # URL L'Argus
            search_query = f"{brand}-{model}".lower().replace(' ', '-')
            search_url = f"https://www.largus.fr/recherche/{search_query}"

            html = await self.fetch_url(search_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Extraire les specs techniques
                specs_table = soup.find('table', class_='specs-table')
                if specs_table:
                    rows = specs_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            specs[key] = value

        except Exception as e:
            print(f"❌ Erreur scraping L'Argus: {str(e)}")

        return specs

    # Méthodes utilitaires d'extraction
    def extract_text(self, soup, tag: str, class_name: str) -> str:
        """Extrait du texte depuis un élément"""
        elem = soup.find(tag, class_=class_name)
        return elem.get_text(strip=True) if elem else ""

    def extract_number(self, soup, tag: str, class_name: str) -> Optional[int]:
        """Extrait un nombre depuis un élément"""
        elem = soup.find(tag, class_=class_name)
        if elem:
            text = elem.get_text(strip=True)
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else None
        return None

    def extract_float(self, soup, tag: str, class_name: str) -> Optional[float]:
        """Extrait un float depuis un élément"""
        elem = soup.find(tag, class_=class_name)
        if elem:
            text = elem.get_text(strip=True).replace(',', '.')
            numbers = re.findall(r'\d+\.?\d*', text)
            return float(numbers[0]) if numbers else None
        return None

    def extract_dimension(self, soup, dimension_type: str) -> Optional[int]:
        """Extrait une dimension (longueur, largeur, hauteur)"""
        elem = soup.find('span', {'data-dimension': dimension_type})
        if elem:
            text = elem.get_text(strip=True)
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else None
        return None

    def extract_year(self, soup) -> Optional[int]:
        """Extrait l'année du modèle"""
        elem = soup.find('span', class_='year')
        if elem:
            text = elem.get_text(strip=True)
            numbers = re.findall(r'\d{4}', text)
            return int(numbers[0]) if numbers else None
        return None

    async def collect_all_models_for_brand(self, brand_name: str, brand_id: str) -> List[Dict]:
        """Collecte tous les modèles pour une marque depuis toutes les sources"""
        print(f"\n{'='*80}")
        print(f"🚗 Collecte de TOUS les modèles pour {brand_name}")
        print(f"{'='*80}")

        all_models = []

        # 1. API CarQuery
        api_models = await self.fetch_carquery_api(brand_name)
        print(f"✅ CarQuery API: {len(api_models)} modèles trouvés")

        # 2. Scraping automobile-catalog.com
        catalog_models = await self.scrape_automobile_catalog(brand_name)
        print(f"✅ Automobile Catalog: {len(catalog_models)} modèles trouvés")

        # Fusionner et enrichir les données
        for model in api_models + catalog_models:
            if model.get('name'):
                # Enrichir avec les avis Caradisiac
                reviews = await self.scrape_caradisiac_reviews(brand_name, model['name'])
                model.update(reviews)

                # Enrichir avec specs L'Argus
                specs = await self.scrape_largus_specs(brand_name, model['name'])
                model.update(specs)

                # Ajouter l'ID de la marque
                model['brand_id'] = brand_id

                all_models.append(model)

                await asyncio.sleep(2)  # Respecter les serveurs

        return all_models

    async def save_models_to_db(self, models: List[Dict]):
        """Sauvegarde les modèles dans la base de données"""
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                for idx, model_data in enumerate(models, 1):
                    # Créer le modèle
                    car_model = CarModel(**model_data)
                    session.add(car_model)

                    if idx % 10 == 0:
                        await session.commit()
                        print(f"✅ {idx}/{len(models)} modèles sauvegardés...")

                await session.commit()
                print(f"\n✅ Total: {len(models)} modèles sauvegardés dans la base de données")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur sauvegarde: {str(e)}")
                raise
            finally:
                await session.close()


async def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("WEB SCRAPING AUTOMATIQUE - MODÈLES AUTOMOBILES")
    print("Collecte TOUTES les données depuis Internet")
    print("=" * 80)

    scraper = AutoWebScraper()
    await scraper.init_session()

    try:
        # Récupérer toutes les marques depuis la DB
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            result = await session.execute("SELECT id, name FROM car_brands")
            brands = result.fetchall()

            print(f"\n📋 {len(brands)} marques trouvées dans la base de données")

            total_models = []

            for brand_id, brand_name in brands[:10]:  # Limiter à 10 marques pour test
                models = await scraper.collect_all_models_for_brand(brand_name, brand_id)
                total_models.extend(models)
                print(f"\n✅ {brand_name}: {len(models)} modèles collectés")

            # Sauvegarder tous les modèles
            if total_models:
                await scraper.save_models_to_db(total_models)
                print(f"\n🎉 TOTAL: {len(total_models)} modèles collectés et sauvegardés !")

    finally:
        await scraper.close_session()

    print("\n" + "=" * 80)
    print("Script terminé !")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
