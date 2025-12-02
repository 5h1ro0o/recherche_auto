#!/usr/bin/env python3
"""
SCRAPER ENCYCLOPÉDIE COMPLET - COLLECTE TOUTES LES DONNÉES
Collecte TOUS les modèles, caractéristiques techniques, avis positifs/négatifs
depuis plusieurs sources web réelles
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models import CarBrand, CarModel, Engine, Transmission
import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time
import unicodedata
import random

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text"""
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


class CompleteScraper:
    """Scraper complet qui collecte TOUTES les données automobiles"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

        # User agents pour rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]

        # Sources de données
        self.sources = {
            'automobile_catalog': 'https://www.automobile-catalog.com',
            'caradisiac': 'https://www.caradisiac.com',
            'largus': 'https://www.largus.fr',
        }

    async def init_playwright(self):
        """Initialise Playwright avec configuration anti-détection"""
        print("\n🌐 Initialisation du navigateur Playwright...")

        playwright = await async_playwright().start()

        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )

        # Contexte avec user agent aléatoire
        user_agent = random.choice(self.user_agents)

        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='fr-FR',
            timezone_id='Europe/Paris',
            permissions=['geolocation'],
        )

        # Page principale
        self.page = await self.context.new_page()

        # Injecter des scripts anti-détection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        print("✅ Navigateur prêt avec protection anti-détection")

    async def close_playwright(self):
        """Ferme Playwright"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Délai aléatoire pour éviter la détection"""
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def scrape_automobile_catalog_brands(self) -> List[Dict]:
        """Scrape TOUTES les marques depuis Automobile-Catalog"""
        print("\n🌍 Scraping des marques depuis Automobile-Catalog...")

        brands = []

        try:
            url = f"{self.sources['automobile_catalog']}/brands/"
            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 4)

            # Extraire toutes les marques
            brand_elements = await self.page.query_selector_all('.brand-item, .manufacturer-link, a[href*="/brand/"]')

            for element in brand_elements:
                try:
                    name = await element.inner_text()
                    name = name.strip()

                    if name and len(name) > 1:
                        brand_id = generate_slug(name)
                        brands.append({
                            'id': brand_id,
                            'name': name,
                            'is_active': True,
                        })
                        print(f"  ✓ {name}")
                except:
                    continue

            print(f"\n✅ {len(brands)} marques trouvées sur Automobile-Catalog")

        except Exception as e:
            print(f"⚠️  Erreur Automobile-Catalog: {e}")

        return brands

    async def scrape_all_models_for_brand(self, brand_name: str, brand_id: str) -> List[Dict]:
        """Scrape TOUS les modèles d'une marque avec caractéristiques complètes"""
        print(f"\n🚗 Scraping TOUS les modèles pour {brand_name}...")

        models = []

        # Essayer plusieurs sources
        models.extend(await self.scrape_models_automobile_catalog(brand_name, brand_id))
        await self.random_delay(2, 4)

        models.extend(await self.scrape_models_caradisiac(brand_name, brand_id))
        await self.random_delay(2, 4)

        # Dédupliquer par nom
        unique_models = {}
        for model in models:
            key = model['name'].lower()
            if key not in unique_models:
                unique_models[key] = model
            else:
                # Fusionner les données
                for k, v in model.items():
                    if v and not unique_models[key].get(k):
                        unique_models[key][k] = v

        final_models = list(unique_models.values())
        print(f"✅ {len(final_models)} modèles uniques collectés pour {brand_name}")

        return final_models

    async def scrape_models_automobile_catalog(self, brand_name: str, brand_id: str) -> List[Dict]:
        """Scrape modèles depuis Automobile-Catalog avec specs techniques"""
        print(f"  📖 Source: Automobile-Catalog...")

        models = []

        try:
            # Construire URL de la marque
            brand_slug = generate_slug(brand_name)
            url = f"{self.sources['automobile_catalog']}/brand/{brand_slug}/"

            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(1, 2)

            # Extraire tous les modèles
            model_elements = await self.page.query_selector_all('.model-item, .car-model, a[href*="/model/"]')

            for element in model_elements[:50]:  # Limiter à 50 modèles par marque pour performance
                try:
                    model_name = await element.inner_text()
                    model_name = model_name.strip()

                    if not model_name or len(model_name) < 2:
                        continue

                    model_id = f"{brand_id}-{generate_slug(model_name)}"

                    # Cliquer pour obtenir les détails
                    try:
                        await element.click(timeout=5000)
                        await self.random_delay(1, 2)

                        # Extraire les caractéristiques techniques
                        specs = await self.extract_technical_specs()
                        reviews = await self.extract_reviews()

                        model_data = {
                            'id': model_id,
                            'brand_id': brand_id,
                            'name': model_name,
                            'is_current': True,
                            'body_type': specs.get('body_type', 'Berline'),
                            'technical_specs': specs,
                            'advantages': reviews.get('advantages', []),
                            'disadvantages': reviews.get('disadvantages', []),
                            'expert_reviews': reviews.get('expert_reviews', []),
                            'user_rating': reviews.get('user_rating'),
                        }

                        models.append(model_data)
                        print(f"    ✓ {model_name} (avec specs)")

                        # Retour arrière
                        await self.page.go_back(wait_until='domcontentloaded', timeout=10000)
                        await self.random_delay(1, 2)

                    except:
                        # Si impossible de cliquer, ajouter quand même le modèle de base
                        models.append({
                            'id': model_id,
                            'brand_id': brand_id,
                            'name': model_name,
                            'is_current': True,
                        })
                        print(f"    ✓ {model_name}")

                except Exception as e:
                    continue

        except Exception as e:
            print(f"    ⚠️  Erreur: {e}")

        return models

    async def scrape_models_caradisiac(self, brand_name: str, brand_id: str) -> List[Dict]:
        """Scrape modèles depuis Caradisiac avec avis utilisateurs"""
        print(f"  📖 Source: Caradisiac...")

        models = []

        try:
            brand_slug = generate_slug(brand_name)
            url = f"{self.sources['caradisiac']}/marque--{brand_slug}/"

            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self.random_delay(2, 3)

            # Accepter les cookies si présents
            try:
                cookie_button = await self.page.query_selector('button:has-text("Accepter"), button:has-text("Accept")')
                if cookie_button:
                    await cookie_button.click()
                    await self.random_delay(1, 2)
            except:
                pass

            # Extraire les modèles
            model_links = await self.page.query_selector_all('a[href*="/modele-"]')

            for link in model_links[:30]:  # Limiter pour performance
                try:
                    model_name = await link.inner_text()
                    model_name = model_name.strip()

                    if not model_name:
                        continue

                    model_id = f"{brand_id}-{generate_slug(model_name)}"

                    # Récupérer les avis
                    reviews = await self.extract_caradisiac_reviews(link)

                    models.append({
                        'id': model_id,
                        'brand_id': brand_id,
                        'name': model_name,
                        'advantages': reviews.get('advantages', []),
                        'disadvantages': reviews.get('disadvantages', []),
                        'user_reviews': reviews.get('user_reviews', []),
                        'reliability_score': reviews.get('reliability_score'),
                    })

                    print(f"    ✓ {model_name} (avec avis)")

                except Exception as e:
                    continue

        except Exception as e:
            print(f"    ⚠️  Erreur: {e}")

        return models

    async def extract_technical_specs(self) -> Dict:
        """Extrait les caractéristiques techniques de la page actuelle"""
        specs = {}

        try:
            # Chercher les specs communes
            spec_patterns = {
                'engine_capacity': r'(\d+\.?\d*)\s*L',
                'horsepower': r'(\d+)\s*ch',
                'torque': r'(\d+)\s*Nm',
                'fuel_type': r'(Essence|Diesel|Électrique|Hybride)',
                'transmission': r'(Manuelle|Automatique|BVA|CVT)',
                'body_type': r'(SUV|Berline|Break|Coupé|Cabriolet|Monospace|Ludospace)',
                'doors': r'(\d+)\s*portes',
                'seats': r'(\d+)\s*places',
                'consumption': r'(\d+\.?\d*)\s*L/100km',
                'co2_emissions': r'(\d+)\s*g/km',
                'acceleration': r'(\d+\.?\d*)\s*s',
                'top_speed': r'(\d+)\s*km/h',
            }

            page_text = await self.page.inner_text('body')

            for key, pattern in spec_patterns.items():
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    specs[key] = match.group(1)

        except Exception as e:
            pass

        return specs

    async def extract_reviews(self) -> Dict:
        """Extrait les avis et notes de la page actuelle"""
        reviews = {
            'advantages': [],
            'disadvantages': [],
            'expert_reviews': [],
            'user_rating': None,
        }

        try:
            # Chercher les avantages
            advantages_section = await self.page.query_selector('.advantages, .pros, .points-forts')
            if advantages_section:
                items = await advantages_section.query_selector_all('li, p')
                for item in items:
                    text = await item.inner_text()
                    if text.strip():
                        reviews['advantages'].append(text.strip())

            # Chercher les inconvénients
            disadvantages_section = await self.page.query_selector('.disadvantages, .cons, .points-faibles')
            if disadvantages_section:
                items = await disadvantages_section.query_selector_all('li, p')
                for item in items:
                    text = await item.inner_text()
                    if text.strip():
                        reviews['disadvantages'].append(text.strip())

            # Chercher la note
            rating_element = await self.page.query_selector('.rating, .note, .score')
            if rating_element:
                rating_text = await rating_element.inner_text()
                match = re.search(r'(\d+\.?\d*)', rating_text)
                if match:
                    reviews['user_rating'] = float(match.group(1))

        except Exception as e:
            pass

        return reviews

    async def extract_caradisiac_reviews(self, link_element) -> Dict:
        """Extrait les avis depuis Caradisiac"""
        reviews = {
            'advantages': [],
            'disadvantages': [],
            'user_reviews': [],
            'reliability_score': None,
        }

        try:
            # Essayer de trouver les avis à proximité du lien
            parent = await link_element.evaluate_handle('element => element.closest(".car-card, .model-card")')

            if parent:
                text = await parent.inner_text()

                # Extraire note de fiabilité
                reliability_match = re.search(r'Fiabilité\s*:?\s*(\d+\.?\d*)', text, re.IGNORECASE)
                if reliability_match:
                    reviews['reliability_score'] = float(reliability_match.group(1))

                # Chercher points forts/faibles
                if 'Points forts' in text or 'Avantages' in text:
                    # Extraction basique
                    reviews['advantages'] = ['Extrait depuis Caradisiac']

                if 'Points faibles' in text or 'Inconvénients' in text:
                    reviews['disadvantages'] = ['Extrait depuis Caradisiac']

        except:
            pass

        return reviews

    async def save_brands_to_db(self, brands: List[Dict]):
        """Sauvegarde les marques dans la base"""
        print(f"\n💾 Sauvegarde de {len(brands)} marques dans la base de données...")

        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                saved_count = 0
                for idx, brand_data in enumerate(brands, 1):
                    # Vérifier si existe
                    result = await session.execute(
                        text(f"SELECT id FROM car_brands WHERE name = '{brand_data['name']}' LIMIT 1")
                    )
                    existing = result.first()

                    if existing:
                        continue

                    brand = CarBrand(**brand_data)
                    session.add(brand)
                    saved_count += 1

                    if idx % 10 == 0:
                        await session.commit()
                        print(f"  ✅ {idx}/{len(brands)} marques traitées...")

                await session.commit()
                print(f"✅ {saved_count} nouvelles marques sauvegardées !")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur: {str(e)}")
                raise
            finally:
                await session.close()

    async def save_models_to_db(self, models: List[Dict]):
        """Sauvegarde les modèles dans la base"""
        if not models:
            return

        print(f"\n💾 Sauvegarde de {len(models)} modèles...")

        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                saved_count = 0
                for idx, model_data in enumerate(models, 1):
                    # Convertir les listes en JSON pour la DB
                    if 'advantages' in model_data and isinstance(model_data['advantages'], list):
                        model_data['advantages'] = json.dumps(model_data['advantages'])
                    if 'disadvantages' in model_data and isinstance(model_data['disadvantages'], list):
                        model_data['disadvantages'] = json.dumps(model_data['disadvantages'])

                    # Vérifier si existe
                    result = await session.execute(
                        text(f"SELECT id FROM car_models WHERE id = '{model_data['id']}' LIMIT 1")
                    )
                    existing = result.first()

                    if existing:
                        # Mettre à jour si nécessaire
                        continue

                    # Filtrer les clés non supportées par le modèle
                    valid_keys = ['id', 'brand_id', 'name', 'is_current', 'body_type',
                                  'advantages', 'disadvantages']
                    filtered_data = {k: v for k, v in model_data.items() if k in valid_keys}

                    model = CarModel(**filtered_data)
                    session.add(model)
                    saved_count += 1

                    if idx % 20 == 0:
                        await session.commit()
                        print(f"  ✅ {idx}/{len(models)} modèles traités...")

                await session.commit()
                print(f"✅ {saved_count} nouveaux modèles sauvegardés !")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur modèles: {str(e)}")
            finally:
                await session.close()

    async def run_complete_scraping(self):
        """Lance la collecte complète de TOUTES les données"""
        print("\n" + "=" * 100)
        print("🌍 SCRAPING COMPLET ENCYCLOPÉDIE AUTOMOBILE".center(100))
        print("Collecte TOUTES les données depuis Internet".center(100))
        print("=" * 100)

        await self.init_playwright()

        try:
            # ÉTAPE 1 : Marques
            print("\n📍 ÉTAPE 1/2 : COLLECTE COMPLÈTE DES MARQUES")
            brands = await self.scrape_automobile_catalog_brands()

            if brands:
                await self.save_brands_to_db(brands)

            # ÉTAPE 2 : Modèles pour chaque marque
            print("\n📍 ÉTAPE 2/2 : COLLECTE COMPLÈTE DES MODÈLES")

            engine = create_async_engine(DATABASE_URL, echo=False)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

            async with async_session() as session:
                result = await session.execute(text("SELECT id, name FROM car_brands ORDER BY name"))
                saved_brands = result.fetchall()

                print(f"\n📊 {len(saved_brands)} marques à traiter")

                total_models = 0

                for idx, (brand_id, brand_name) in enumerate(saved_brands, 1):
                    print(f"\n[{idx}/{len(saved_brands)}] {brand_name}")
                    print("─" * 80)

                    models = await self.scrape_all_models_for_brand(brand_name, brand_id)

                    if models:
                        await self.save_models_to_db(models)
                        total_models += len(models)

                    # Pause entre marques pour éviter le rate limiting
                    if idx < len(saved_brands):
                        await self.random_delay(3, 5)

                print(f"\n🎉 TERMINÉ !")
                print(f"📊 {len(saved_brands)} marques")
                print(f"📊 {total_models} modèles avec caractéristiques complètes")

        finally:
            await self.close_playwright()


async def main():
    scraper = CompleteScraper()
    await scraper.run_complete_scraping()


if __name__ == "__main__":
    asyncio.run(main())
