#!/usr/bin/env python3
"""
SCRAPER COMPLET ENCYCLOPÉDIE AUTOMOBILE
Collecte AUTOMATIQUEMENT depuis Internet :
1. TOUTES les marques automobiles mondiales
2. TOUS les modèles pour chaque marque
3. TOUTES les caractéristiques techniques
4. TOUS les retours positifs et négatifs (forums, avis clients)
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import CarBrand, CarModel
import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

class CompleteAutoEncyclopediaScraper:
    """Scraper ultra-complet qui collecte TOUT depuis Internet"""

    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        # Sources pour marques
        self.brands_sources = {
            'wikipedia': 'https://fr.wikipedia.org/wiki/Liste_de_constructeurs_automobiles',
            'automobile_catalog': 'https://www.automobile-catalog.com/make/make.html',
            'carlogos': 'https://www.carlogos.org/car-brands/',
        }

        # Sources pour modèles et specs
        self.models_sources = {
            'automobile_catalog': 'https://www.automobile-catalog.com',
            'cars_data': 'https://www.cars-data.com',
            'auto_evolution': 'https://www.autoevolution.com',
        }

        # Sources pour avis
        self.reviews_sources = {
            'caradisiac': 'https://www.caradisiac.com',
            'largus': 'https://www.largus.fr',
            'autoplus': 'https://www.autoplus.fr',
            'forum_caradisiac': 'https://www.forum-auto.caradisiac.com',
        }

    async def init_session(self):
        """Initialise la session HTTP"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=10)
            self.session = aiohttp.ClientSession(headers=self.headers, connector=connector)

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
                print(f"⚠️  Erreur tentative {attempt + 1}/{retries}: {str(e)[:100]}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        return None

    # ============================================================================
    # PARTIE 1 : COLLECTE DES MARQUES
    # ============================================================================

    async def scrape_brands_from_wikipedia(self) -> List[Dict]:
        """Scrape la liste complète des marques depuis Wikipedia"""
        print("\n🌍 Scraping Wikipedia pour TOUTES les marques automobiles...")

        brands = []

        try:
            html = await self.fetch_url(self.brands_sources['wikipedia'])
            if not html:
                return brands

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver toutes les tables de constructeurs
            tables = soup.find_all('table', class_='wikitable')

            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extraire nom et pays
                        name_cell = cells[0]
                        name_link = name_cell.find('a')

                        if name_link:
                            brand_name = name_link.get_text(strip=True)

                            # Extraire le pays
                            country = ""
                            if len(cells) >= 2:
                                country = cells[1].get_text(strip=True)

                            brands.append({
                                'name': brand_name,
                                'country': country,
                            })

            print(f"✅ Wikipedia: {len(brands)} marques trouvées")

        except Exception as e:
            print(f"❌ Erreur Wikipedia: {str(e)}")

        return brands

    async def scrape_brands_from_automobile_catalog(self) -> List[Dict]:
        """Scrape les marques depuis automobile-catalog.com"""
        print("\n🔍 Scraping Automobile-Catalog pour les marques...")

        brands = []

        try:
            html = await self.fetch_url(self.brands_sources['automobile_catalog'])
            if not html:
                return brands

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver tous les liens de marques
            brand_links = soup.find_all('a', class_='make-link')

            for link in brand_links:
                brand_name = link.get_text(strip=True)
                if brand_name:
                    brands.append({
                        'name': brand_name,
                        'url': link.get('href', '')
                    })

            print(f"✅ Automobile-Catalog: {len(brands)} marques trouvées")

        except Exception as e:
            print(f"❌ Erreur Automobile-Catalog: {str(e)}")

        return brands

    async def scrape_brands_from_carlogos(self) -> List[Dict]:
        """Scrape les marques depuis carlogos.org"""
        print("\n🚗 Scraping CarLogos.org pour les marques...")

        brands = []

        try:
            html = await self.fetch_url(self.brands_sources['carlogos'])
            if not html:
                return brands

            soup = BeautifulSoup(html, 'html.parser')

            # Trouver toutes les marques
            brand_items = soup.find_all('div', class_='brand-item')

            for item in brand_items:
                name_elem = item.find('h3') or item.find('h2')
                if name_elem:
                    brand_name = name_elem.get_text(strip=True)

                    # Extraire le pays si disponible
                    country_elem = item.find('span', class_='country')
                    country = country_elem.get_text(strip=True) if country_elem else ""

                    brands.append({
                        'name': brand_name,
                        'country': country,
                    })

            print(f"✅ CarLogos: {len(brands)} marques trouvées")

        except Exception as e:
            print(f"❌ Erreur CarLogos: {str(e)}")

        return brands

    async def get_brand_details_from_wikipedia(self, brand_name: str) -> Dict:
        """Récupère les détails d'une marque depuis Wikipedia"""
        print(f"\n📖 Détails Wikipedia pour {brand_name}...")

        details = {
            'description': '',
            'founded_year': None,
            'headquarters': '',
            'website': '',
        }

        try:
            # Recherche Wikipedia
            search_url = f"https://fr.wikipedia.org/wiki/{brand_name.replace(' ', '_')}"
            html = await self.fetch_url(search_url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Extraire infobox
                infobox = soup.find('table', class_='infobox')
                if infobox:
                    rows = infobox.find_all('tr')

                    for row in rows:
                        th = row.find('th')
                        td = row.find('td')

                        if th and td:
                            label = th.get_text(strip=True).lower()
                            value = td.get_text(strip=True)

                            if 'création' in label or 'fondation' in label:
                                years = re.findall(r'\d{4}', value)
                                if years:
                                    details['founded_year'] = int(years[0])

                            elif 'siège' in label or 'headquarters' in label:
                                details['headquarters'] = value

                            elif 'site web' in label or 'website' in label:
                                link = td.find('a')
                                if link:
                                    details['website'] = link.get('href', '')

                # Extraire description (premier paragraphe)
                first_para = soup.find('p', class_=lambda x: x != 'mw-empty-elt')
                if first_para:
                    details['description'] = first_para.get_text(strip=True)[:500]

        except Exception as e:
            print(f"⚠️  Erreur détails Wikipedia: {str(e)[:100]}")

        return details

    async def get_brand_reputation_from_caradisiac(self, brand_name: str) -> Dict:
        """Récupère la réputation d'une marque depuis Caradisiac"""
        print(f"\n⭐ Réputation Caradisiac pour {brand_name}...")

        reputation = {
            'reputation_score': 0.0,
            'reliability_rating': 0.0,
            'quality_rating': 0.0,
            'advantages': [],
            'disadvantages': [],
        }

        try:
            search_url = f"https://www.caradisiac.com/recherche/?q={brand_name}+fiabilité"
            html = await self.fetch_url(search_url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Chercher article de fiabilité
                articles = soup.find_all('article', class_='search-result')

                for article in articles[:3]:
                    link = article.find('a', href=re.compile(r'/fiabilite/'))
                    if link:
                        article_url = link.get('href')
                        if not article_url.startswith('http'):
                            article_url = f"https://www.caradisiac.com{article_url}"

                        # Récupérer l'article
                        article_html = await self.fetch_url(article_url)
                        if article_html:
                            article_soup = BeautifulSoup(article_html, 'html.parser')

                            # Extraire note
                            rating = article_soup.find('span', class_='rating-value')
                            if rating:
                                try:
                                    reputation['reliability_rating'] = float(rating.get_text(strip=True))
                                except:
                                    pass

                            # Extraire avantages
                            pros = article_soup.find('div', class_='pros')
                            if pros:
                                items = pros.find_all('li')
                                reputation['advantages'] = [item.get_text(strip=True) for item in items]

                            # Extraire inconvénients
                            cons = article_soup.find('div', class_='cons')
                            if cons:
                                items = cons.find_all('li')
                                reputation['disadvantages'] = [item.get_text(strip=True) for item in items]

                            break

        except Exception as e:
            print(f"⚠️  Erreur réputation Caradisiac: {str(e)[:100]}")

        return reputation

    async def collect_all_brands(self) -> List[Dict]:
        """Collecte TOUTES les marques depuis toutes les sources"""
        print("\n" + "=" * 100)
        print("🌍 COLLECTE DE TOUTES LES MARQUES AUTOMOBILES MONDIALES")
        print("=" * 100)

        all_brands = []
        brands_dict = {}

        # 1. Wikipedia
        wiki_brands = await self.scrape_brands_from_wikipedia()
        for brand in wiki_brands:
            if brand['name'] not in brands_dict:
                brands_dict[brand['name']] = brand

        # 2. Automobile Catalog
        catalog_brands = await self.scrape_brands_from_automobile_catalog()
        for brand in catalog_brands:
            if brand['name'] not in brands_dict:
                brands_dict[brand['name']] = brand
            else:
                brands_dict[brand['name']].update(brand)

        # 3. CarLogos
        carlogos_brands = await self.scrape_brands_from_carlogos()
        for brand in carlogos_brands:
            if brand['name'] not in brands_dict:
                brands_dict[brand['name']] = brand
            else:
                brands_dict[brand['name']].update(brand)

        print(f"\n✅ Total unique : {len(brands_dict)} marques uniques trouvées")

        # Enrichir chaque marque avec détails
        for idx, (brand_name, brand_data) in enumerate(list(brands_dict.items())[:100], 1):  # Limiter à 100 pour test
            print(f"\n[{idx}/100] Enrichissement {brand_name}...")

            # Détails Wikipedia
            details = await self.get_brand_details_from_wikipedia(brand_name)
            brand_data.update(details)

            # Réputation Caradisiac
            reputation = await self.get_brand_reputation_from_caradisiac(brand_name)
            brand_data.update(reputation)

            all_brands.append(brand_data)

            await asyncio.sleep(2)  # Respecter les serveurs

        return all_brands

    # ============================================================================
    # PARTIE 2 : COLLECTE DES MODÈLES ET CARACTÉRISTIQUES
    # ============================================================================

    async def scrape_all_models_for_brand(self, brand_name: str) -> List[Dict]:
        """Collecte TOUS les modèles pour une marque"""
        print(f"\n{'='*80}")
        print(f"🚗 Collecte de TOUS les modèles pour {brand_name}")
        print(f"{'='*80}")

        models = []

        # Source 1: Automobile Catalog
        catalog_models = await self.scrape_models_automobile_catalog(brand_name)
        models.extend(catalog_models)

        # Source 2: Auto-Evolution
        evolution_models = await self.scrape_models_auto_evolution(brand_name)
        models.extend(evolution_models)

        return models

    async def scrape_models_automobile_catalog(self, brand_name: str) -> List[Dict]:
        """Scrape les modèles depuis Automobile-Catalog"""
        print(f"\n🔍 Automobile-Catalog modèles pour {brand_name}...")

        models = []

        try:
            url = f"https://www.automobile-catalog.com/make/{brand_name.lower()}.html"
            html = await self.fetch_url(url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Trouver les modèles
                model_links = soup.find_all('a', href=re.compile(r'/car/\d+/'))

                for link in model_links[:50]:  # Max 50 modèles par marque
                    model_url = link.get('href')
                    if not model_url.startswith('http'):
                        model_url = f"https://www.automobile-catalog.com{model_url}"

                    # Récupérer specs du modèle
                    model_data = await self.scrape_model_full_specs(model_url)
                    if model_data:
                        models.append(model_data)

                    await asyncio.sleep(1)

            print(f"✅ Automobile-Catalog: {len(models)} modèles")

        except Exception as e:
            print(f"❌ Erreur: {str(e)[:100]}")

        return models

    async def scrape_models_auto_evolution(self, brand_name: str) -> List[Dict]:
        """Scrape les modèles depuis Auto-Evolution"""
        print(f"\n🔍 Auto-Evolution modèles pour {brand_name}...")

        models = []

        try:
            url = f"https://www.autoevolution.com/{brand_name.lower()}/"
            html = await self.fetch_url(url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Trouver les modèles
                model_divs = soup.find_all('div', class_='carmodel')

                for div in model_divs[:30]:
                    link = div.find('a')
                    if link:
                        model_url = link.get('href')
                        if not model_url.startswith('http'):
                            model_url = f"https://www.autoevolution.com{model_url}"

                        # Récupérer specs
                        model_data = await self.scrape_model_auto_evolution_specs(model_url)
                        if model_data:
                            models.append(model_data)

                        await asyncio.sleep(1)

            print(f"✅ Auto-Evolution: {len(models)} modèles")

        except Exception as e:
            print(f"❌ Erreur: {str(e)[:100]}")

        return models

    async def scrape_model_full_specs(self, url: str) -> Optional[Dict]:
        """Scrape TOUTES les caractéristiques d'un modèle"""
        try:
            html = await self.fetch_url(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            model_data = {
                'name': '',
                'year': None,
                'generation': '',
                'body_type': '',
                'segment': '',
                'doors': None,
                'seats': None,
                'length_mm': None,
                'width_mm': None,
                'height_mm': None,
                'wheelbase_mm': None,
                'trunk_capacity_liters': None,
                'weight_kg': None,
                'max_speed_kmh': None,
                'acceleration_0_100_sec': None,
                'fuel_consumption_city': None,
                'fuel_consumption_highway': None,
                'fuel_consumption_combined': None,
                'co2_emissions': None,
                'fuel_tank_capacity': None,
                'power_hp': None,
                'engine_displacement': None,
                'torque_nm': None,
                'drivetrain': '',
                'engine_type': '',
                'transmission_type': '',
                'fuel_type': '',
            }

            # Extraire nom
            title = soup.find('h1')
            if title:
                model_data['name'] = title.get_text(strip=True)

            # Extraire specs depuis tableau
            specs_table = soup.find('table', class_='specifications')
            if specs_table:
                rows = specs_table.find_all('tr')

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        # Mapper les valeurs
                        if 'longueur' in label or 'length' in label:
                            model_data['length_mm'] = self.extract_number(value)
                        elif 'largeur' in label or 'width' in label:
                            model_data['width_mm'] = self.extract_number(value)
                        elif 'hauteur' in label or 'height' in label:
                            model_data['height_mm'] = self.extract_number(value)
                        elif 'empattement' in label or 'wheelbase' in label:
                            model_data['wheelbase_mm'] = self.extract_number(value)
                        elif 'coffre' in label or 'trunk' in label:
                            model_data['trunk_capacity_liters'] = self.extract_number(value)
                        elif 'poids' in label or 'weight' in label:
                            model_data['weight_kg'] = self.extract_number(value)
                        elif 'vitesse max' in label or 'top speed' in label:
                            model_data['max_speed_kmh'] = self.extract_number(value)
                        elif '0-100' in label or '0 to 100' in label:
                            model_data['acceleration_0_100_sec'] = self.extract_float(value)
                        elif 'consommation' in label and 'ville' in label:
                            model_data['fuel_consumption_city'] = self.extract_float(value)
                        elif 'consommation' in label and 'route' in label:
                            model_data['fuel_consumption_highway'] = self.extract_float(value)
                        elif 'consommation' in label and 'mixte' in label:
                            model_data['fuel_consumption_combined'] = self.extract_float(value)
                        elif 'co2' in label:
                            model_data['co2_emissions'] = self.extract_number(value)
                        elif 'puissance' in label or 'power' in label:
                            model_data['power_hp'] = self.extract_number(value)
                        elif 'cylindrée' in label or 'displacement' in label:
                            model_data['engine_displacement'] = self.extract_number(value)
                        elif 'couple' in label or 'torque' in label:
                            model_data['torque_nm'] = self.extract_number(value)
                        elif 'portes' in label or 'doors' in label:
                            model_data['doors'] = self.extract_number(value)
                        elif 'places' in label or 'seats' in label:
                            model_data['seats'] = self.extract_number(value)

            return model_data

        except Exception as e:
            print(f"⚠️  Erreur specs: {str(e)[:100]}")
            return None

    async def scrape_model_auto_evolution_specs(self, url: str) -> Optional[Dict]:
        """Scrape specs depuis Auto-Evolution"""
        # Similaire à scrape_model_full_specs mais adapté pour Auto-Evolution
        return await self.scrape_model_full_specs(url)

    async def get_model_reviews_caradisiac(self, brand_name: str, model_name: str) -> Dict:
        """Récupère TOUS les avis (positifs/négatifs) depuis Caradisiac"""
        print(f"\n💬 Avis Caradisiac pour {brand_name} {model_name}...")

        reviews = {
            'advantages': [],
            'disadvantages': [],
            'reviews': [],
            'reliability_rating': 0.0,
            'comfort_rating': 0.0,
            'driving_rating': 0.0,
            'quality_rating': 0.0,
            'value_rating': 0.0,
        }

        try:
            search_url = f"https://www.caradisiac.com/recherche/?q={brand_name}+{model_name}"
            html = await self.fetch_url(search_url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Trouver l'article du modèle
                articles = soup.find_all('article', limit=5)

                for article in articles:
                    link = article.find('a')
                    if link:
                        article_url = link.get('href')
                        if not article_url.startswith('http'):
                            article_url = f"https://www.caradisiac.com{article_url}"

                        article_html = await self.fetch_url(article_url)
                        if article_html:
                            article_soup = BeautifulSoup(article_html, 'html.parser')

                            # Avantages
                            pros_section = article_soup.find('div', class_='pros')
                            if pros_section:
                                items = pros_section.find_all('li')
                                reviews['advantages'] = [item.get_text(strip=True) for item in items]

                            # Inconvénients
                            cons_section = article_soup.find('div', class_='cons')
                            if cons_section:
                                items = cons_section.find_all('li')
                                reviews['disadvantages'] = [item.get_text(strip=True) for item in items]

                            # Notes
                            ratings = article_soup.find_all('span', class_='rating')
                            for rating in ratings:
                                try:
                                    score = float(rating.get_text(strip=True))
                                    label = rating.find_previous('span', class_='label')
                                    if label:
                                        label_text = label.get_text(strip=True).lower()
                                        if 'fiabilité' in label_text:
                                            reviews['reliability_rating'] = score
                                        elif 'confort' in label_text:
                                            reviews['comfort_rating'] = score
                                        elif 'conduite' in label_text:
                                            reviews['driving_rating'] = score
                                        elif 'qualité' in label_text:
                                            reviews['quality_rating'] = score
                                        elif 'rapport' in label_text:
                                            reviews['value_rating'] = score
                                except:
                                    pass

                            break

        except Exception as e:
            print(f"⚠️  Erreur avis: {str(e)[:100]}")

        return reviews

    async def get_model_forum_reviews(self, brand_name: str, model_name: str) -> List[str]:
        """Récupère les avis depuis les forums Caradisiac"""
        print(f"\n💭 Forums pour {brand_name} {model_name}...")

        forum_reviews = []

        try:
            search_url = f"https://www.forum-auto.caradisiac.com/recherche.php?q={brand_name}+{model_name}+avis"
            html = await self.fetch_url(search_url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Extraire posts
                posts = soup.find_all('div', class_='post-content', limit=10)

                for post in posts:
                    text = post.get_text(strip=True)
                    if len(text) > 50:
                        forum_reviews.append(text[:300])

            print(f"✅ {len(forum_reviews)} avis forums trouvés")

        except Exception as e:
            print(f"⚠️  Erreur forums: {str(e)[:100]}")

        return forum_reviews

    # ============================================================================
    # SAUVEGARDE EN BASE DE DONNÉES
    # ============================================================================

    async def save_brands_to_db(self, brands: List[Dict]):
        """Sauvegarde les marques dans la base"""
        print(f"\n💾 Sauvegarde de {len(brands)} marques en base...")

        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                for idx, brand_data in enumerate(brands, 1):
                    # Nettoyer les données
                    cleaned = {k: v for k, v in brand_data.items() if v is not None and v != ''}

                    # Créer la marque
                    brand = CarBrand(**cleaned)
                    session.add(brand)

                    if idx % 20 == 0:
                        await session.commit()
                        print(f"✅ {idx}/{len(brands)} marques sauvegardées...")

                await session.commit()
                print(f"✅ {len(brands)} marques sauvegardées !")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur sauvegarde marques: {str(e)}")
                raise
            finally:
                await session.close()

    async def save_models_to_db(self, models: List[Dict], brand_id: str):
        """Sauvegarde les modèles dans la base"""
        print(f"\n💾 Sauvegarde de {len(models)} modèles en base...")

        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                for idx, model_data in enumerate(models, 1):
                    # Ajouter brand_id
                    model_data['brand_id'] = brand_id

                    # Nettoyer
                    cleaned = {k: v for k, v in model_data.items() if v is not None and v != ''}

                    # Créer le modèle
                    model = CarModel(**cleaned)
                    session.add(model)

                    if idx % 20 == 0:
                        await session.commit()
                        print(f"✅ {idx}/{len(models)} modèles sauvegardés...")

                await session.commit()
                print(f"✅ {len(models)} modèles sauvegardés !")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur sauvegarde modèles: {str(e)}")
            finally:
                await session.close()

    # ============================================================================
    # PROCESSUS COMPLET
    # ============================================================================

    async def run_complete_scraping(self):
        """Lance le scraping COMPLET de l'encyclopédie"""
        print("\n" + "=" * 100)
        print("🌍 SCRAPING COMPLET ENCYCLOPÉDIE AUTOMOBILE".center(100))
        print("Collecte AUTOMATIQUE de TOUTES les données depuis Internet".center(100))
        print("=" * 100)

        # ÉTAPE 1: Collecter toutes les marques
        print("\n\n📍 ÉTAPE 1/2 : COLLECTE DES MARQUES")
        brands = await self.collect_all_brands()

        if brands:
            await self.save_brands_to_db(brands)

        # ÉTAPE 2: Pour chaque marque, collecter tous les modèles
        print("\n\n📍 ÉTAPE 2/2 : COLLECTE DES MODÈLES")

        # Récupérer les marques sauvegardées
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            result = await session.execute("SELECT id, name FROM car_brands LIMIT 20")  # Limiter à 20 pour test
            saved_brands = result.fetchall()

            total_models = 0

            for brand_id, brand_name in saved_brands:
                print(f"\n{'='*100}")
                print(f"Marque: {brand_name}".center(100))
                print(f"{'='*100}")

                # Collecter tous les modèles
                models = await self.scrape_all_models_for_brand(brand_name)

                # Pour chaque modèle, enrichir avec avis
                for model in models:
                    # Avis Caradisiac
                    reviews = await self.get_model_reviews_caradisiac(brand_name, model.get('name', ''))
                    model.update(reviews)

                    # Avis forums
                    forum_reviews = await self.get_model_forum_reviews(brand_name, model.get('name', ''))
                    if forum_reviews:
                        model['reviews'] = forum_reviews

                    await asyncio.sleep(1)

                # Sauvegarder les modèles
                if models:
                    await self.save_models_to_db(models, brand_id)
                    total_models += len(models)

                print(f"\n✅ {brand_name}: {len(models)} modèles collectés")

            print(f"\n\n🎉 SCRAPING TERMINÉ !")
            print(f"📊 Total: {len(saved_brands)} marques, {total_models} modèles")

    # ============================================================================
    # UTILITAIRES
    # ============================================================================

    def extract_number(self, text: str) -> Optional[int]:
        """Extrait un nombre depuis du texte"""
        numbers = re.findall(r'\d+', text.replace(' ', ''))
        return int(numbers[0]) if numbers else None

    def extract_float(self, text: str) -> Optional[float]:
        """Extrait un float depuis du texte"""
        text = text.replace(',', '.')
        numbers = re.findall(r'\d+\.?\d*', text)
        return float(numbers[0]) if numbers else None


async def main():
    """Point d'entrée principal"""
    scraper = CompleteAutoEncyclopediaScraper()
    await scraper.init_session()

    try:
        await scraper.run_complete_scraping()
    finally:
        await scraper.close_session()


if __name__ == "__main__":
    asyncio.run(main())
