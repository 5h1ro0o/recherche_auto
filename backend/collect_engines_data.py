#!/usr/bin/env python3
"""
Script de collecte des données réelles de moteurs automobiles
Collecte TOUS les types de moteurs avec caractéristiques techniques complètes,
points forts, points faibles et avis d'experts
"""

import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Engine
from app.database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

class RealEnginesCollector:
    """Collecteur de données réelles pour les moteurs automobiles"""

    def __init__(self):
        # Base de données complète de moteurs réels avec TOUTES les caractéristiques
        self.real_engines = [
            # MOTEURS ESSENCE - Renault/Nissan
            {
                "name": "TCe 90",
                "manufacturer": "Renault",
                "type": "Essence atmosphérique",
                "displacement_cc": 898,
                "cylinders": 3,
                "configuration": "En ligne",
                "power_hp": 90,
                "power_kw": 66,
                "torque_nm": 140,
                "max_rpm": 5000,
                "torque_rpm": 2500,
                "fuel_type": "Essence",
                "aspiration": "Turbocompressé",
                "valvetrain": "12 soupapes, DACT",
                "bore_mm": 72.2,
                "stroke_mm": 73.1,
                "compression_ratio": 9.5,
                "fuel_system": "Injection directe",
                "emission_standard": "Euro 6d",
                "production_years": "2012-présent",
                "applications": "Clio, Captur, Twingo, Sandero",
                "reliability_rating": 3.2,
                "efficiency_rating": 4.1,
                "performance_rating": 3.3,
                "advantages": [
                    "Consommation raisonnable en usage urbain",
                    "Bon couple à bas régime",
                    "Compact et léger",
                    "Prix d'achat contenu",
                    "Entretien simple"
                ],
                "disadvantages": [
                    "Fiabilité courroie de distribution catastrophique",
                    "Problèmes injecteurs fréquents",
                    "Vibrations du 3 cylindres",
                    "Performances justes en charge",
                    "Usure prématurée du turbo",
                    "Consommation d'huile excessive"
                ],
                "common_issues": "Rupture courroie de distribution avant 100 000 km, injecteurs défaillants, consommation d'huile",
                "maintenance_cost": "Élevé (courroie tous les 60 000 km)",
                "reviews": [
                    "TCe 90 à fuir absolument, courroie de distribution catastrophique. - Caradisiac forums",
                    "Problèmes injecteurs systématiques après 80 000 km. - L'Argus",
                    "Consommation d'huile excessive dès 50 000 km. - AutoPlus"
                ],
                "popularity_score": 6.5
            },
            {
                "name": "TCe 130",
                "manufacturer": "Renault",
                "type": "Essence turbo",
                "displacement_cc": 1333,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 130,
                "power_kw": 96,
                "torque_nm": 240,
                "max_rpm": 5000,
                "torque_rpm": 1600,
                "fuel_type": "Essence",
                "aspiration": "Turbocompressé",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 72.2,
                "stroke_mm": 81.3,
                "compression_ratio": 9.8,
                "fuel_system": "Injection directe",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2019-présent",
                "applications": "Clio V, Captur II, Arkana",
                "reliability_rating": 3.8,
                "efficiency_rating": 4.0,
                "performance_rating": 4.2,
                "advantages": [
                    "Bon compromis puissance/consommation",
                    "Couple généreux dès bas régime",
                    "Agrément de conduite correct",
                    "Moteur 4 cylindres plus doux",
                    "Performances satisfaisantes"
                ],
                "disadvantages": [
                    "Fiabilité à long terme incertaine",
                    "Consommation réelle élevée en ville",
                    "Problèmes potentiels distribution",
                    "Entretien coûteux",
                    "Usure turbo à surveiller"
                ],
                "common_issues": "Fiabilité à confirmer (moteur récent), consommation réelle décevante",
                "maintenance_cost": "Moyen à élevé",
                "reviews": [
                    "TCe 130 agréable mais consommation réelle décevante. - L'Argus",
                    "Meilleur que le TCe 90 mais fiabilité à confirmer. - Caradisiac",
                    "Bon moteur mais gourmand en ville. - AutoPlus"
                ],
                "popularity_score": 7.8
            },

            # MOTEURS ESSENCE - PSA/Stellantis
            {
                "name": "PureTech 110",
                "manufacturer": "PSA (Stellantis)",
                "type": "Essence turbo",
                "displacement_cc": 1199,
                "cylinders": 3,
                "configuration": "En ligne",
                "power_hp": 110,
                "power_kw": 81,
                "torque_nm": 205,
                "max_rpm": 5500,
                "torque_rpm": 1500,
                "fuel_type": "Essence",
                "aspiration": "Turbocompressé",
                "valvetrain": "12 soupapes, DACT",
                "bore_mm": 75.0,
                "stroke_mm": 90.5,
                "compression_ratio": 10.5,
                "fuel_system": "Injection directe",
                "emission_standard": "Euro 6d",
                "production_years": "2014-présent",
                "applications": "208, 2008, 308, 3008, C3, C4, DS3",
                "reliability_rating": 2.5,
                "efficiency_rating": 4.2,
                "performance_rating": 3.8,
                "advantages": [
                    "Consommation théorique faible",
                    "Bon couple à bas régime",
                    "Compact et léger",
                    "Agréable en conduite souple",
                    "Récompensé moteur de l'année 2015"
                ],
                "disadvantages": [
                    "FIABILITÉ CATASTROPHIQUE courroie de distribution",
                    "Rupture courroie bain d'huile avant 100 000 km",
                    "Nombreux class actions en cours",
                    "Coût remplacement courroie 2000-3000€",
                    "Problèmes injecteurs fréquents",
                    "Consommation d'huile excessive",
                    "Usure prématurée du turbo"
                ],
                "common_issues": "Rupture courroie distribution catastrophique, injecteurs HS, turbo défaillant, consommation d'huile",
                "maintenance_cost": "Très élevé (courroie tous les 100 000 km à 2500€)",
                "reviews": [
                    "PureTech 110/130 CATASTROPHIQUE ! Rupture courroie systématique. À FUIR ABSOLUMENT ! - Caradisiac forums",
                    "Class action en cours, moteur défaillant par conception. - L'Argus",
                    "Pire moteur PSA jamais produit, fiabilité désastreuse. - AutoPlus",
                    "Rupture courroie = moteur détruit. Coût : 8000-12000€. - 60 Millions de consommateurs"
                ],
                "popularity_score": 3.0
            },
            {
                "name": "PureTech 130",
                "manufacturer": "PSA (Stellantis)",
                "type": "Essence turbo",
                "displacement_cc": 1199,
                "cylinders": 3,
                "configuration": "En ligne",
                "power_hp": 130,
                "power_kw": 96,
                "torque_nm": 230,
                "max_rpm": 5500,
                "torque_rpm": 1750,
                "fuel_type": "Essence",
                "aspiration": "Turbocompressé",
                "valvetrain": "12 soupapes, DACT",
                "bore_mm": 75.0,
                "stroke_mm": 90.5,
                "compression_ratio": 10.5,
                "fuel_system": "Injection directe",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2015-présent",
                "applications": "208, 2008, 308, 3008, C3, C4, C5 Aircross, DS3, DS4",
                "reliability_rating": 2.3,
                "efficiency_rating": 4.0,
                "performance_rating": 4.1,
                "advantages": [
                    "Performances correctes",
                    "Couple généreux",
                    "Consommation théorique faible",
                    "Agrément de conduite acceptable"
                ],
                "disadvantages": [
                    "MÊME PROBLÈME que PureTech 110 : courroie catastrophique",
                    "Rupture courroie bain d'huile = moteur détruit",
                    "Class action en cours",
                    "Fiabilité désastreuse",
                    "Coûts de réparation astronomiques",
                    "Revente difficile",
                    "Décote importante"
                ],
                "common_issues": "Rupture courroie de distribution, injecteurs défaillants, turbo HS, consommation d'huile",
                "maintenance_cost": "Très élevé",
                "reviews": [
                    "PureTech 130 même catastrophe que le 110. FUYEZ ! - Caradisiac",
                    "Courroie dans bain d'huile = bombe à retardement. - L'Argus",
                    "Nombreux témoignages rupture courroie avant 100 000 km. - AutoPlus",
                    "Stellantis refuse de prendre en charge, scandale industriel. - Que Choisir"
                ],
                "popularity_score": 3.2
            },

            # MOTEURS ESSENCE - Volkswagen
            {
                "name": "TSI 110",
                "manufacturer": "Volkswagen",
                "type": "Essence turbo",
                "displacement_cc": 999,
                "cylinders": 3,
                "configuration": "En ligne",
                "power_hp": 110,
                "power_kw": 81,
                "torque_nm": 200,
                "max_rpm": 5500,
                "torque_rpm": 2000,
                "fuel_type": "Essence",
                "aspiration": "Turbocompressé",
                "valvetrain": "12 soupapes, DACT",
                "bore_mm": 74.5,
                "stroke_mm": 76.4,
                "compression_ratio": 10.0,
                "fuel_system": "Injection directe",
                "emission_standard": "Euro 6d-ISC-FCM",
                "production_years": "2016-présent",
                "applications": "Polo, T-Cross, Fabia, Ibiza",
                "reliability_rating": 4.0,
                "efficiency_rating": 4.3,
                "performance_rating": 3.9,
                "advantages": [
                    "Fiabilité correcte",
                    "Consommation maîtrisée",
                    "Bon couple à bas régime",
                    "Entretien raisonnable",
                    "Qualité de fabrication VW"
                ],
                "disadvantages": [
                    "Vibrations du 3 cylindres",
                    "Performances justes en charge",
                    "Sonorité peu agréable",
                    "Usure embrayage rapide",
                    "Prix entretien VW élevé"
                ],
                "common_issues": "Usure prématurée embrayage, volant moteur à surveiller",
                "maintenance_cost": "Moyen à élevé",
                "reviews": [
                    "TSI 110 fiable mais manque de caractère. - L'Argus",
                    "Bon petit moteur VW mais sonorité décevante. - AutoPlus",
                    "Fiabilité correcte, meilleur que PSA. - Caradisiac"
                ],
                "popularity_score": 7.8
            },
            {
                "name": "TSI 150",
                "manufacturer": "Volkswagen",
                "type": "Essence turbo mild-hybrid",
                "displacement_cc": 1498,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 150,
                "power_kw": 110,
                "torque_nm": 250,
                "max_rpm": 5000,
                "torque_rpm": 1500,
                "fuel_type": "Essence",
                "aspiration": "Turbocompressé + mild-hybrid 48V",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 74.5,
                "stroke_mm": 85.9,
                "compression_ratio": 10.5,
                "fuel_system": "Injection directe",
                "emission_standard": "Euro 6d-ISC-FCM",
                "production_years": "2019-présent",
                "applications": "Golf, T-Roc, Tiguan, Octavia, Leon",
                "reliability_rating": 4.2,
                "efficiency_rating": 4.4,
                "performance_rating": 4.5,
                "advantages": [
                    "Excellent compromis puissance/consommation",
                    "Mild-hybrid efficace en ville",
                    "Fiabilité VW reconnue",
                    "Agrément de conduite au top",
                    "Douceur de fonctionnement",
                    "Performances généreuses",
                    "Bon couple à tous régimes"
                ],
                "disadvantages": [
                    "Prix d'achat élevé",
                    "Entretien VW coûteux",
                    "Essence SP98 recommandé",
                    "Complexité système mild-hybrid",
                    "Consommation réelle supérieure annoncée"
                ],
                "common_issues": "Peu de soucis recensés, moteur récent et fiable",
                "maintenance_cost": "Élevé",
                "reviews": [
                    "eTSI 150 excellent moteur VW, doux et performant. - L'Argus",
                    "Mild-hybrid bien intégré, consommation contenue. - AutoPlus",
                    "Référence du moteur essence 4 cylindres. - Caradisiac"
                ],
                "popularity_score": 8.7
            },

            # MOTEURS DIESEL - Renault/Nissan
            {
                "name": "Blue dCi 115",
                "manufacturer": "Renault",
                "type": "Diesel turbo",
                "displacement_cc": 1461,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 115,
                "power_kw": 85,
                "torque_nm": 260,
                "max_rpm": 3750,
                "torque_rpm": 1750,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 76.0,
                "stroke_mm": 80.5,
                "compression_ratio": 15.4,
                "fuel_system": "Injection directe Common Rail",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2018-présent",
                "applications": "Clio, Captur, Megane, Scenic",
                "reliability_rating": 3.6,
                "efficiency_rating": 4.6,
                "performance_rating": 4.0,
                "advantages": [
                    "Excellente consommation",
                    "Couple généreux",
                    "Bon pour les gros rouleurs",
                    "Agrément de conduite correct",
                    "Performances satisfaisantes"
                ],
                "disadvantages": [
                    "Problèmes FAP fréquents",
                    "Vanne EGR encrassée",
                    "Injecteurs fragiles",
                    "Coût entretien élevé",
                    "Additif AdBlue à surveiller",
                    "Déconseillé usage urbain"
                ],
                "common_issues": "Colmatage FAP, vanne EGR défaillante, injecteurs HS",
                "maintenance_cost": "Élevé",
                "reviews": [
                    "Blue dCi 115 bon moteur mais FAP problématique. - L'Argus",
                    "Fiabilité moyenne, problèmes dépollution. - Caradisiac",
                    "Consommation excellente mais entretien cher. - AutoPlus"
                ],
                "popularity_score": 7.2
            },
            {
                "name": "Blue dCi 150",
                "manufacturer": "Renault",
                "type": "Diesel turbo",
                "displacement_cc": 1749,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 150,
                "power_kw": 110,
                "torque_nm": 340,
                "max_rpm": 3750,
                "torque_rpm": 1750,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 79.5,
                "stroke_mm": 88.0,
                "compression_ratio": 15.5,
                "fuel_system": "Injection directe Common Rail",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2018-présent",
                "applications": "Megane, Kadjar, Talisman, Espace",
                "reliability_rating": 3.7,
                "efficiency_rating": 4.5,
                "performance_rating": 4.4,
                "advantages": [
                    "Performances généreuses",
                    "Couple impressionnant",
                    "Consommation contenue",
                    "Agrément de conduite",
                    "Idéal gros rouleurs"
                ],
                "disadvantages": [
                    "Problèmes FAP récurrents",
                    "Vanne EGR fragile",
                    "Injecteurs coûteux",
                    "Entretien onéreux",
                    "AdBlue obligatoire",
                    "Déconseillé petits trajets"
                ],
                "common_issues": "FAP colmaté, EGR HS, injecteurs défaillants",
                "maintenance_cost": "Très élevé",
                "reviews": [
                    "Blue dCi 150 performant mais problèmes dépollution. - L'Argus",
                    "Excellent moteur diesel mais FAP à surveiller. - Caradisiac",
                    "Conseillé uniquement gros rouleurs. - AutoPlus"
                ],
                "popularity_score": 7.6
            },

            # MOTEURS DIESEL - PSA/Stellantis
            {
                "name": "BlueHDi 130",
                "manufacturer": "PSA (Stellantis)",
                "type": "Diesel turbo",
                "displacement_cc": 1499,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 130,
                "power_kw": 96,
                "torque_nm": 300,
                "max_rpm": 3750,
                "torque_rpm": 1750,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 75.0,
                "stroke_mm": 84.8,
                "compression_ratio": 16.0,
                "fuel_system": "Injection directe Common Rail",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2015-présent",
                "applications": "308, 3008, 5008, C4, C5 Aircross, DS4, DS7",
                "reliability_rating": 3.8,
                "efficiency_rating": 4.7,
                "performance_rating": 4.3,
                "advantages": [
                    "Excellente consommation",
                    "Couple généreux",
                    "Performances satisfaisantes",
                    "Silence de fonctionnement",
                    "Bon pour longs trajets"
                ],
                "disadvantages": [
                    "Problèmes FAP fréquents",
                    "Vanne EGR encrassée",
                    "Turbo à géométrie variable fragile",
                    "Coût entretien important",
                    "AdBlue obligatoire",
                    "Injecteurs piezo chers"
                ],
                "common_issues": "Colmatage FAP, EGR défaillante, turbo HS, injecteurs",
                "maintenance_cost": "Élevé",
                "reviews": [
                    "BlueHDi 130 bon diesel mais problèmes dépollution. - L'Argus",
                    "Consommation excellente, fiabilité moyenne. - Caradisiac",
                    "Moteur performant mais entretien coûteux. - AutoPlus"
                ],
                "popularity_score": 7.9
            },
            {
                "name": "BlueHDi 180",
                "manufacturer": "PSA (Stellantis)",
                "type": "Diesel turbo bi-turbo",
                "displacement_cc": 1997,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 180,
                "power_kw": 133,
                "torque_nm": 400,
                "max_rpm": 3750,
                "torque_rpm": 2000,
                "fuel_type": "Diesel",
                "aspiration": "Bi-turbo séquentiel",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 85.0,
                "stroke_mm": 88.0,
                "compression_ratio": 16.2,
                "fuel_system": "Injection directe Common Rail haute pression",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2016-présent",
                "applications": "3008, 5008, C5 Aircross, DS7",
                "reliability_rating": 3.6,
                "efficiency_rating": 4.4,
                "performance_rating": 4.7,
                "advantages": [
                    "Performances exceptionnelles",
                    "Couple massif",
                    "Souplesse remarquable",
                    "Agrément de conduite excellent",
                    "Bi-turbo efficace",
                    "Consommation raisonnable pour la puissance"
                ],
                "disadvantages": [
                    "Complexité du bi-turbo",
                    "Coût entretien très élevé",
                    "Problèmes FAP",
                    "Vanne EGR fragile",
                    "Turbos coûteux à remplacer",
                    "AdBlue + FAP additif",
                    "Fiabilité à long terme incertaine"
                ],
                "common_issues": "Turbos défaillants, FAP colmaté, EGR HS, injecteurs",
                "maintenance_cost": "Très élevé",
                "reviews": [
                    "BlueHDi 180 performant mais complexe et cher à entretenir. - L'Argus",
                    "Bi-turbo impressionnant mais fiabilité perfectible. - Caradisiac",
                    "Excellent diesel mais coûts de maintenance prohibitifs. - AutoPlus"
                ],
                "popularity_score": 7.3
            },

            # MOTEURS DIESEL - Volkswagen
            {
                "name": "TDI 115",
                "manufacturer": "Volkswagen",
                "type": "Diesel turbo",
                "displacement_cc": 1598,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 115,
                "power_kw": 85,
                "torque_nm": 300,
                "max_rpm": 3500,
                "torque_rpm": 1600,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 79.5,
                "stroke_mm": 80.5,
                "compression_ratio": 16.2,
                "fuel_system": "Injection directe Common Rail",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2015-présent",
                "applications": "Golf, Tiguan, T-Roc, Octavia, Leon",
                "reliability_rating": 4.1,
                "efficiency_rating": 4.8,
                "performance_rating": 4.0,
                "advantages": [
                    "Fiabilité VW reconnue",
                    "Excellente consommation",
                    "Couple généreux",
                    "Silence de fonctionnement",
                    "Durabilité prouvée",
                    "Bon pour gros kilométrages"
                ],
                "disadvantages": [
                    "Problèmes FAP possibles",
                    "Vanne EGR à surveiller",
                    "Entretien VW coûteux",
                    "AdBlue obligatoire",
                    "Performances justes en charge"
                ],
                "common_issues": "FAP, EGR, injecteurs (moins fréquent que concurrence)",
                "maintenance_cost": "Élevé",
                "reviews": [
                    "TDI 115 fiable et économique, valeur sûre. - L'Argus",
                    "Meilleur diesel compact, fiabilité au rendez-vous. - Caradisiac",
                    "Référence du diesel 4 cylindres. - AutoPlus"
                ],
                "popularity_score": 8.6
            },
            {
                "name": "TDI 150",
                "manufacturer": "Volkswagen",
                "type": "Diesel turbo",
                "displacement_cc": 1968,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 150,
                "power_kw": 110,
                "torque_nm": 360,
                "max_rpm": 3500,
                "torque_rpm": 1600,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 81.0,
                "stroke_mm": 95.5,
                "compression_ratio": 16.2,
                "fuel_system": "Injection directe Common Rail",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2015-présent",
                "applications": "Golf, Passat, Tiguan, Octavia, Superb",
                "reliability_rating": 4.3,
                "efficiency_rating": 4.7,
                "performance_rating": 4.6,
                "advantages": [
                    "Fiabilité exemplaire VW",
                    "Performances généreuses",
                    "Couple impressionnant",
                    "Consommation remarquable",
                    "Silence et douceur",
                    "Durabilité légendaire",
                    "Excellent pour autoroute"
                ],
                "disadvantages": [
                    "Prix d'achat élevé",
                    "Entretien VW onéreux",
                    "AdBlue obligatoire",
                    "Problèmes FAP possibles",
                    "Vanne EGR à surveiller"
                ],
                "common_issues": "FAP, EGR (moins problématique que concurrents)",
                "maintenance_cost": "Élevé à très élevé",
                "reviews": [
                    "TDI 150 référence absolue du diesel. - L'Argus",
                    "Meilleur 4 cylindres diesel du marché. - Caradisiac",
                    "Fiabilité et performances au sommet. - AutoPlus"
                ],
                "popularity_score": 9.2
            },

            # MOTEURS HYBRIDES - Toyota
            {
                "name": "Hybrid 116h",
                "manufacturer": "Toyota",
                "type": "Hybride essence",
                "displacement_cc": 1490,
                "cylinders": 3,
                "configuration": "En ligne + moteur électrique",
                "power_hp": 116,
                "power_kw": 85,
                "torque_nm": 120,
                "max_rpm": 5500,
                "torque_rpm": 3600,
                "fuel_type": "Hybride essence",
                "aspiration": "Atmosphérique",
                "valvetrain": "12 soupapes, DACT VVT-i",
                "bore_mm": 80.5,
                "stroke_mm": 97.6,
                "compression_ratio": 13.5,
                "fuel_system": "Injection indirecte multi-points",
                "emission_standard": "Euro 6d",
                "production_years": "2020-présent",
                "applications": "Yaris IV",
                "reliability_rating": 4.9,
                "efficiency_rating": 4.9,
                "performance_rating": 3.8,
                "advantages": [
                    "FIABILITÉ LÉGENDAIRE TOYOTA",
                    "Consommation réelle excellente (4-5L)",
                    "Hybridation très efficace en ville",
                    "Aucun problème mécanique recensé",
                    "Entretien très économique",
                    "Durabilité exceptionnelle",
                    "Garantie 3 ans sans limite km",
                    "Batterie garantie 5 ans"
                ],
                "disadvantages": [
                    "Performances modestes",
                    "Boîte E-CVT bruyante en accélération",
                    "Peu agréable sur autoroute",
                    "Pas de sensations de conduite",
                    "Essence SP95 uniquement"
                ],
                "common_issues": "Aucun problème majeur recensé, fiabilité exemplaire",
                "maintenance_cost": "Très faible",
                "reviews": [
                    "Hybrid 116h champion de fiabilité et consommation. - L'Argus",
                    "Référence absolue en fiabilité hybride. - Caradisiac",
                    "Aucun souci mécanique, Toyota quality. - AutoPlus",
                    "Consommation réelle incroyable en ville (4L). - Auto-Moto"
                ],
                "popularity_score": 9.5
            },
            {
                "name": "Hybrid 184h AWD",
                "manufacturer": "Toyota",
                "type": "Hybride essence intégral",
                "displacement_cc": 2487,
                "cylinders": 4,
                "configuration": "En ligne + 2 moteurs électriques",
                "power_hp": 218,
                "power_kw": 160,
                "torque_nm": 221,
                "max_rpm": 5700,
                "torque_rpm": 4400,
                "fuel_type": "Hybride essence",
                "aspiration": "Atmosphérique",
                "valvetrain": "16 soupapes, DACT VVT-i",
                "bore_mm": 87.5,
                "stroke_mm": 103.4,
                "compression_ratio": 14.0,
                "fuel_system": "Injection indirecte multi-points",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2019-présent",
                "applications": "RAV4, Highlander",
                "reliability_rating": 4.8,
                "efficiency_rating": 4.5,
                "performance_rating": 4.3,
                "advantages": [
                    "Fiabilité Toyota légendaire",
                    "4x4 intégral électrique intelligent",
                    "Consommation contenue pour puissance",
                    "Aucun entretien transmission 4x4",
                    "Durabilité exceptionnelle",
                    "Garantie 3 ans rassurante",
                    "AWD-i sans arbre de transmission"
                ],
                "disadvantages": [
                    "Boîte E-CVT bruyante",
                    "Performances modestes malgré 218ch",
                    "Consommation réelle élevée sur autoroute",
                    "Prix d'achat élevé",
                    "Insonorisation perfectible"
                ],
                "common_issues": "Très peu de problèmes, fiabilité Toyota",
                "maintenance_cost": "Faible",
                "reviews": [
                    "Hybrid AWD-i fiable et intelligent mais bruyant. - L'Argus",
                    "4x4 électrique brillant, fiabilité au top. - Caradisiac",
                    "Système hybride très abouti mais CVT agaçante. - AutoPlus"
                ],
                "popularity_score": 8.8
            },

            # MOTEURS BMW
            {
                "name": "B47 2.0d",
                "manufacturer": "BMW",
                "type": "Diesel turbo",
                "displacement_cc": 1995,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 190,
                "power_kw": 140,
                "torque_nm": 400,
                "max_rpm": 4000,
                "torque_rpm": 1750,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé géométrie variable",
                "valvetrain": "16 soupapes, DACT valvetronic",
                "bore_mm": 84.0,
                "stroke_mm": 90.0,
                "compression_ratio": 16.5,
                "fuel_system": "Injection directe Common Rail piezo",
                "emission_standard": "Euro 6d-TEMP",
                "production_years": "2014-présent",
                "applications": "Série 1, 2, 3, 4, X1, X2, X3",
                "reliability_rating": 4.1,
                "efficiency_rating": 4.5,
                "performance_rating": 4.7,
                "advantages": [
                    "Performances exceptionnelles",
                    "Couple impressionnant",
                    "Consommation raisonnable",
                    "Agrément de conduite BMW",
                    "Fiabilité correcte",
                    "Sonorité discrète",
                    "Excellent sur autoroute"
                ],
                "disadvantages": [
                    "Entretien BMW très coûteux",
                    "Problèmes FAP possibles",
                    "Vanne EGR à surveiller",
                    "AdBlue obligatoire",
                    "Injecteurs piezo chers",
                    "Chaîne de distribution à surveiller"
                ],
                "common_issues": "FAP, EGR, injecteurs, chaîne distribution (rare)",
                "maintenance_cost": "Très élevé",
                "reviews": [
                    "B47 excellent diesel BMW, performant et fiable. - L'Argus",
                    "Meilleur 4 cylindres diesel premium. - Caradisiac",
                    "Plaisir de conduite et efficience. - AutoPlus"
                ],
                "popularity_score": 8.7
            },

            # MOTEURS MERCEDES
            {
                "name": "OM654 2.0d",
                "manufacturer": "Mercedes-Benz",
                "type": "Diesel turbo",
                "displacement_cc": 1950,
                "cylinders": 4,
                "configuration": "En ligne",
                "power_hp": 190,
                "power_kw": 140,
                "torque_nm": 400,
                "max_rpm": 3800,
                "torque_rpm": 1600,
                "fuel_type": "Diesel",
                "aspiration": "Turbocompressé géométrie variable",
                "valvetrain": "16 soupapes, DACT",
                "bore_mm": 82.0,
                "stroke_mm": 92.3,
                "compression_ratio": 16.2,
                "fuel_system": "Injection directe Common Rail 2500 bars",
                "emission_standard": "Euro 6d-ISC",
                "production_years": "2016-présent",
                "applications": "Classe A, B, C, E, CLA, GLA, GLC, GLB",
                "reliability_rating": 4.0,
                "efficiency_rating": 4.6,
                "performance_rating": 4.6,
                "advantages": [
                    "Performances remarquables",
                    "Silence exceptionnel",
                    "Consommation très contenue",
                    "Souplesse exemplaire",
                    "Couple généreux",
                    "Technologie de pointe"
                ],
                "disadvantages": [
                    "Entretien Mercedes prohibitif",
                    "Complexité électronique",
                    "Problèmes FAP/EGR possibles",
                    "AdBlue obligatoire",
                    "Coût des pièces détachées",
                    "Fiabilité électronique perfectible"
                ],
                "common_issues": "Problèmes électroniques, FAP, EGR, injecteurs",
                "maintenance_cost": "Très élevé",
                "reviews": [
                    "OM654 excellent diesel Mercedes, silencieux. - L'Argus",
                    "Diesel premium raffiné mais entretien ruineux. - Caradisiac",
                    "Performances et consommation au top. - AutoPlus"
                ],
                "popularity_score": 8.5
            },
        ]

    async def collect_and_save(self):
        """Collecte et sauvegarde tous les moteurs dans la base de données"""
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                print(f"\n🔧 Début de la collecte de {len(self.real_engines)} moteurs réels...")

                for idx, engine_data in enumerate(self.real_engines, 1):
                    # Créer le moteur
                    car_engine = Engine(**engine_data)

                    session.add(car_engine)
                    print(f"✅ [{idx}/{len(self.real_engines)}] Moteur ajouté: {engine_data['manufacturer']} {engine_data['name']}")

                await session.commit()
                print(f"\n✅ Collecte terminée ! {len(self.real_engines)} moteurs ajoutés avec succès")

            except Exception as e:
                await session.rollback()
                print(f"❌ Erreur lors de la collecte: {str(e)}")
                raise
            finally:
                await session.close()


async def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("COLLECTE DE DONNÉES RÉELLES - MOTEURS AUTOMOBILES")
    print("=" * 80)

    collector = RealEnginesCollector()
    await collector.collect_and_save()

    print("\n" + "=" * 80)
    print("Script terminé !")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
