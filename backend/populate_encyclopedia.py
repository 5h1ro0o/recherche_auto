"""Script pour peupler l'encyclopédie automobile avec des données complètes"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import (
    CarBrand, CarModel, Engine, Transmission,
    BrandReview, ModelReview, EngineReview, TransmissionReview
)
import uuid
from datetime import datetime

def populate_encyclopedia():
    """Peuple la base de données avec des données automobiles complètes"""
    db = SessionLocal()

    try:
        print("🚀 Démarrage du peuplement de l'encyclopédie automobile...")

        # ==================== MARQUES ====================
        print("\n📦 Ajout des marques...")

        brands_data = [
            {
                "name": "Renault",
                "country": "France",
                "founded_year": 1899,
                "description": "Constructeur automobile français fondé en 1899, spécialisé dans les véhicules compacts et électriques. Leader européen avec une forte présence internationale.",
                "reputation_score": 75,
                "reliability_rating": 3,
                "quality_rating": 3,
                "innovation_rating": 4,
                "advantages": ["Bon rapport qualité-prix", "Gamme électrique complète", "Réseau de distribution étendu", "Technologie innovante"],
                "disadvantages": ["Fiabilité moyenne", "Dépréciation rapide", "Électronique parfois capricieuse"],
                "specialties": ["Citadines", "Électrique", "Utilitaires"],
                "popular_models": ["Clio", "Megane", "Captur", "Zoe", "Arkana"],
                "price_range": "12000-45000",
                "market_segment": "Généraliste"
            },
            {
                "name": "Peugeot",
                "country": "France",
                "founded_year": 1810,
                "description": "Marque automobile française historique, reconnue pour son design moderne et son confort. Innovation constante avec les technologies i-Cockpit.",
                "reputation_score": 78,
                "reliability_rating": 4,
                "quality_rating": 4,
                "innovation_rating": 4,
                "advantages": ["Design attrayant", "Confort excellent", "i-Cockpit innovant", "Bon comportement routier"],
                "disadvantages": ["Prix parfois élevé", "Visibilité réduite (petit volant)", "Coût d'entretien"],
                "specialties": ["SUV", "Berlines", "Hybride"],
                "popular_models": ["208", "308", "3008", "5008", "2008"],
                "price_range": "15000-50000",
                "market_segment": "Généraliste Premium"
            },
            {
                "name": "Citroën",
                "country": "France",
                "founded_year": 1919,
                "description": "Constructeur français innovant, pionnier du confort avec la suspension hydraulique. Design audacieux et technologies avant-gardistes.",
                "reputation_score": 74,
                "reliability_rating": 3,
                "quality_rating": 3,
                "innovation_rating": 5,
                "advantages": ["Confort exceptionnel", "Design unique", "Technologies innovantes", "Prix attractifs"],
                "disadvantages": ["Fiabilité à surveiller", "Revente difficile", "Électronique complexe"],
                "specialties": ["Confort", "Design", "Familiales"],
                "popular_models": ["C3", "C4", "C5 Aircross", "Berlingo", "C3 Aircross"],
                "price_range": "14000-45000",
                "market_segment": "Généraliste"
            },
            {
                "name": "Volkswagen",
                "country": "Allemagne",
                "founded_year": 1937,
                "description": "Constructeur allemand leader mondial, synonyme de qualité et fiabilité. Gamme complète du petit citadin au SUV familial.",
                "reputation_score": 85,
                "reliability_rating": 4,
                "quality_rating": 5,
                "innovation_rating": 4,
                "advantages": ["Fiabilité reconnue", "Finitions premium", "Tenue de route", "Réseau mondial"],
                "disadvantages": ["Prix élevé", "Coût d'entretien", "Options onéreuses"],
                "specialties": ["Qualité", "Polyvalence", "Électrique"],
                "popular_models": ["Golf", "Polo", "Tiguan", "T-Roc", "ID.3", "ID.4"],
                "price_range": "18000-60000",
                "market_segment": "Premium"
            },
            {
                "name": "BMW",
                "country": "Allemagne",
                "founded_year": 1916,
                "description": "Marque allemande de prestige, spécialiste des berlines sportives. Plaisir de conduite et performances élevées.",
                "reputation_score": 88,
                "reliability_rating": 4,
                "quality_rating": 5,
                "innovation_rating": 5,
                "advantages": ["Plaisir de conduite", "Performances", "Prestige", "Technologies avancées"],
                "disadvantages": ["Prix très élevé", "Entretien coûteux", "Dépréciation importante"],
                "specialties": ["Sportives", "Premium", "Électrique"],
                "popular_models": ["Série 1", "Série 3", "X1", "X3", "iX3", "i4"],
                "price_range": "30000-120000",
                "market_segment": "Premium"
            },
            {
                "name": "Mercedes-Benz",
                "country": "Allemagne",
                "founded_year": 1926,
                "description": "Constructeur allemand premium, référence en matière de luxe et technologie. Excellence et innovation depuis près d'un siècle.",
                "reputation_score": 90,
                "reliability_rating": 4,
                "quality_rating": 5,
                "innovation_rating": 5,
                "advantages": ["Luxe absolu", "Technologies de pointe", "Confort premium", "Prestige"],
                "disadvantages": ["Prix très élevé", "Entretien onéreux", "Complexité technologique"],
                "specialties": ["Luxe", "Technologies", "SUV premium"],
                "popular_models": ["Classe A", "Classe C", "GLA", "GLC", "EQC"],
                "price_range": "35000-150000",
                "market_segment": "Luxe"
            },
            {
                "name": "Audi",
                "country": "Allemagne",
                "founded_year": 1909,
                "description": "Marque premium allemande, alliance de design sophistiqué et technologies avancées. Quattro et électrification.",
                "reputation_score": 87,
                "reliability_rating": 4,
                "quality_rating": 5,
                "innovation_rating": 5,
                "advantages": ["Design raffiné", "Quattro performant", "Technologies", "Qualité de construction"],
                "disadvantages": ["Prix élevé", "Entretien coûteux", "Options chères"],
                "specialties": ["Premium", "Quattro", "Électrique"],
                "popular_models": ["A3", "A4", "Q3", "Q5", "e-tron"],
                "price_range": "30000-120000",
                "market_segment": "Premium"
            },
            {
                "name": "Toyota",
                "country": "Japon",
                "founded_year": 1937,
                "description": "Constructeur japonais leader mondial, réputé pour sa fiabilité légendaire. Pionnier de l'hybride avec la Prius.",
                "reputation_score": 92,
                "reliability_rating": 5,
                "quality_rating": 4,
                "innovation_rating": 4,
                "advantages": ["Fiabilité exceptionnelle", "Hybride mature", "Réseau mondial", "Revente facile"],
                "disadvantages": ["Design conservateur", "Agrément de conduite moyen", "Prix parfois élevé"],
                "specialties": ["Fiabilité", "Hybride", "SUV"],
                "popular_models": ["Yaris", "Corolla", "RAV4", "C-HR", "Prius"],
                "price_range": "15000-60000",
                "market_segment": "Généraliste Premium"
            },
            {
                "name": "Tesla",
                "country": "États-Unis",
                "founded_year": 2003,
                "description": "Pionnier américain du véhicule électrique et de la conduite autonome. Innovation disruptive et performances électriques.",
                "reputation_score": 85,
                "reliability_rating": 3,
                "quality_rating": 3,
                "innovation_rating": 5,
                "advantages": ["Technologies avancées", "Performances électriques", "Autonomie élevée", "Réseau Supercharger"],
                "disadvantages": ["Qualité d'assemblage variable", "Service après-vente limité", "Prix élevé"],
                "specialties": ["Électrique pur", "Autopilot", "Performances"],
                "popular_models": ["Model 3", "Model Y", "Model S", "Model X"],
                "price_range": "40000-130000",
                "market_segment": "Premium Électrique"
            },
            {
                "name": "Dacia",
                "country": "Roumanie",
                "founded_year": 1966,
                "description": "Marque low-cost du groupe Renault, championne du rapport qualité-prix. Véhicules simples, robustes et abordables.",
                "reputation_score": 72,
                "reliability_rating": 4,
                "quality_rating": 3,
                "innovation_rating": 2,
                "advantages": ["Prix imbattables", "Robustesse", "Coûts d'entretien faibles", "Pratique"],
                "disadvantages": ["Équipements basiques", "Confort spartiate", "Insonorisation moyenne"],
                "specialties": ["Low-cost", "SUV abordables", "Familiales"],
                "popular_models": ["Sandero", "Duster", "Jogger", "Spring"],
                "price_range": "10000-25000",
                "market_segment": "Low-Cost"
            },
        ]

        brands = {}
        for brand_data in brands_data:
            brand = CarBrand(
                id=str(uuid.uuid4()),
                **brand_data
            )
            db.add(brand)
            brands[brand_data["name"]] = brand
            print(f"  ✓ {brand_data['name']}")

        db.commit()
        print(f"✅ {len(brands_data)} marques ajoutées")

        # ==================== MOTEURS ====================
        print("\n⚙️  Ajout des moteurs...")

        engines_data = [
            # Essence
            {
                "name": "1.0 TCe 90",
                "code": "H4B",
                "fuel_type": "Essence",
                "engine_type": "Thermique",
                "aspiration": "Turbo",
                "displacement": 999,
                "cylinders": 3,
                "configuration": "En ligne",
                "valves": 12,
                "power_hp": 90,
                "power_kw": 66,
                "torque_nm": 160,
                "max_torque_rpm": "2750",
                "consumption_combined": "5.2",
                "co2_emissions": 119,
                "euro_norm": "Euro 6d",
                "technologies": ["Turbo", "Injection directe", "Start-Stop"],
                "reliability_rating": 4,
                "maintenance_cost": "Faible",
                "pros": ["Économique", "Couple généreux", "Nerveux en ville"],
                "cons": ["Sonorité rauque", "Vibrations à froid"],
                "ideal_for": "Usage urbain et périurbain, petits trajets",
                "description": "Petit moteur essence 3 cylindres turbo, très économique et suffisant pour un usage quotidien."
            },
            {
                "name": "1.2 PureTech 130",
                "code": "EB2DTS",
                "fuel_type": "Essence",
                "engine_type": "Thermique",
                "aspiration": "Turbo",
                "displacement": 1199,
                "cylinders": 3,
                "configuration": "En ligne",
                "valves": 12,
                "power_hp": 130,
                "power_kw": 96,
                "torque_nm": 230,
                "max_torque_rpm": "1750",
                "consumption_combined": "5.6",
                "co2_emissions": 128,
                "euro_norm": "Euro 6d",
                "technologies": ["Turbo", "Injection directe", "Start-Stop", "Courroie de distribution"],
                "reliability_rating": 3,
                "maintenance_cost": "Moyen",
                "known_issues": ["Problèmes courroie distribution", "Consommation d'huile"],
                "pros": ["Performances correctes", "Souple", "Bon couple"],
                "cons": ["Fiabilité à surveiller", "Consommation d'huile parfois"],
                "ideal_for": "Usage mixte, trajets variés",
                "description": "Moteur 3 cylindres turbo polyvalent mais à la fiabilité discutée."
            },
            {
                "name": "1.5 TSI 150",
                "code": "EA211 evo",
                "fuel_type": "Essence",
                "engine_type": "Thermique",
                "aspiration": "Turbo",
                "displacement": 1498,
                "cylinders": 4,
                "configuration": "En ligne",
                "valves": 16,
                "power_hp": 150,
                "power_kw": 110,
                "torque_nm": 250,
                "max_torque_rpm": "1500-3500",
                "consumption_combined": "5.8",
                "co2_emissions": 132,
                "euro_norm": "Euro 6d",
                "technologies": ["Turbo", "Injection directe", "Start-Stop", "ACT (désactivation cylindres)"],
                "reliability_rating": 5,
                "maintenance_cost": "Moyen",
                "pros": ["Très fiable", "Performances excellentes", "Sobre", "Doux"],
                "cons": ["Prix options", "Nécessite carburant de qualité"],
                "ideal_for": "Tous usages, excellent polyvalent",
                "description": "Excellent moteur 4 cylindres turbo du groupe VAG, référence de fiabilité."
            },
            {
                "name": "2.0 TSI 245",
                "code": "EA888 Gen3B",
                "fuel_type": "Essence",
                "engine_type": "Thermique",
                "aspiration": "Turbo",
                "displacement": 1984,
                "cylinders": 4,
                "configuration": "En ligne",
                "valves": 16,
                "power_hp": 245,
                "power_kw": 180,
                "torque_nm": 370,
                "max_torque_rpm": "1600-4300",
                "top_speed": 250,
                "acceleration_0_100": "6.3",
                "consumption_combined": "7.4",
                "co2_emissions": 169,
                "euro_norm": "Euro 6d",
                "technologies": ["Turbo", "Injection directe", "Distribution variable", "Refroidissement sophistiqué"],
                "reliability_rating": 4,
                "maintenance_cost": "Élevé",
                "pros": ["Performances exceptionnelles", "Couple énorme", "Polyvalent"],
                "cons": ["Consommation élevée si sollicité", "Entretien coûteux"],
                "ideal_for": "Usage sportif, longs trajets autoroutiers",
                "description": "Moteur sportif très performant, idéal pour les grandes routières."
            },
            # Diesel
            {
                "name": "1.5 dCi 115",
                "code": "K9K",
                "fuel_type": "Diesel",
                "engine_type": "Thermique",
                "aspiration": "Turbo",
                "displacement": 1461,
                "cylinders": 4,
                "configuration": "En ligne",
                "valves": 16,
                "power_hp": 115,
                "power_kw": 85,
                "torque_nm": 260,
                "max_torque_rpm": "1750",
                "consumption_combined": "4.2",
                "co2_emissions": 110,
                "euro_norm": "Euro 6d-Temp",
                "technologies": ["Turbo", "Common Rail", "FAP", "EGR"],
                "reliability_rating": 5,
                "maintenance_cost": "Moyen",
                "pros": ["Très fiable", "Économique", "Couple généreux"],
                "cons": ["Bruit", "Vibrations", "DPF à surveiller"],
                "ideal_for": "Gros rouleurs, longs trajets",
                "description": "Diesel robuste et éprouvé, champion de l'économie sur longue distance."
            },
            {
                "name": "2.0 TDI 150",
                "code": "EA288 evo",
                "fuel_type": "Diesel",
                "engine_type": "Thermique",
                "aspiration": "Turbo",
                "displacement": 1968,
                "cylinders": 4,
                "configuration": "En ligne",
                "valves": 16,
                "power_hp": 150,
                "power_kw": 110,
                "torque_nm": 360,
                "max_torque_rpm": "1600-2750",
                "consumption_combined": "4.8",
                "co2_emissions": 126,
                "euro_norm": "Euro 6d",
                "technologies": ["Turbo", "Common Rail", "FAP", "SCR AdBlue", "Double injection"],
                "reliability_rating": 4,
                "maintenance_cost": "Élevé",
                "pros": ["Couple impressionnant", "Sobre", "Souple", "Doux"],
                "cons": ["Entretien coûteux", "AdBlue", "Complexe"],
                "ideal_for": "Gros rouleurs, autoroute, remorquage",
                "description": "Diesel moderne très performant, idéal pour les gros rouleurs."
            },
            # Hybride
            {
                "name": "1.8 HSD 122",
                "code": "2ZR-FXE",
                "fuel_type": "Hybride",
                "engine_type": "Hybride",
                "aspiration": "Atmosphérique",
                "displacement": 1798,
                "cylinders": 4,
                "configuration": "En ligne",
                "valves": 16,
                "power_hp": 122,
                "power_kw": 90,
                "torque_nm": 142,
                "consumption_combined": "4.3",
                "co2_emissions": 98,
                "euro_norm": "Euro 6d",
                "technologies": ["Hybride", "CVT", "Cycle Atkinson", "Régénération"],
                "reliability_rating": 5,
                "maintenance_cost": "Faible",
                "pros": ["Fiabilité Toyota", "Très économique", "Doux", "Silencieux"],
                "cons": ["CVT bruyante si sollicitée", "Performances moyennes"],
                "ideal_for": "Ville et trajets mixtes, économies maximales",
                "description": "Hybride Toyota éprouvée, championne de la fiabilité et de l'économie."
            },
            # Électrique
            {
                "name": "Moteur électrique 150 kW",
                "code": "R135",
                "fuel_type": "Électrique",
                "engine_type": "Électrique",
                "power_hp": 204,
                "power_kw": 150,
                "torque_nm": 300,
                "top_speed": 160,
                "acceleration_0_100": "7.9",
                "battery_capacity": "52 kWh",
                "electric_range": 385,
                "charging_time": "30 min (80% en charge rapide)",
                "euro_norm": "N/A",
                "technologies": ["Moteur synchrone", "Régénération", "Charge rapide"],
                "reliability_rating": 4,
                "maintenance_cost": "Très faible",
                "pros": ["Zéro émission", "Couple instantané", "Silence", "Entretien minimal"],
                "cons": ["Autonomie limitée l'hiver", "Charge longue à domicile"],
                "ideal_for": "Trajets quotidiens urbains et périurbains",
                "description": "Moteur électrique efficace pour usage quotidien."
            },
        ]

        engines = {}
        for engine_data in engines_data:
            engine = Engine(
                id=str(uuid.uuid4()),
                **engine_data
            )
            db.add(engine)
            engines[engine_data["name"]] = engine
            print(f"  ✓ {engine_data['name']}")

        db.commit()
        print(f"✅ {len(engines_data)} moteurs ajoutés")

        # ==================== TRANSMISSIONS ====================
        print("\n🔧 Ajout des transmissions...")

        transmissions_data = [
            {
                "name": "BVM5",
                "type": "Manuelle",
                "gears": 5,
                "technology": "Mécanique classique",
                "description": "Boîte manuelle 5 rapports simple et fiable",
                "reliability_rating": 5,
                "maintenance_cost": "Faible",
                "pros": ["Fiable", "Simple", "Peu coûteuse", "Agrément"],
                "cons": ["Étagement parfois court", "Pas de 6ème rapport"],
                "ideal_for": "Petites voitures, usage urbain",
            },
            {
                "name": "BVM6",
                "type": "Manuelle",
                "gears": 6,
                "technology": "Mécanique classique",
                "description": "Boîte manuelle 6 rapports polyvalente",
                "reliability_rating": 5,
                "maintenance_cost": "Faible",
                "pros": ["Fiable", "Étagement optimal", "Consommation réduite", "Agrément"],
                "cons": ["Précision variable selon modèles"],
                "ideal_for": "Tous usages, excellent compromis",
            },
            {
                "name": "EDC7",
                "type": "Robotisée",
                "gears": 7,
                "technology": "Double embrayage",
                "manufacturer": "Getrag",
                "description": "Boîte robotisée à double embrayage 7 rapports",
                "reliability_rating": 3,
                "maintenance_cost": "Élevé",
                "known_issues": ["Mécatronique fragile", "À-coups à basse vitesse"],
                "pros": ["Passages rapides", "Confortable", "Économique"],
                "cons": ["Fiabilité discutée", "Réparations coûteuses", "À-coups"],
                "ideal_for": "Usage souple, éviter embouteillages",
            },
            {
                "name": "DSG7",
                "type": "Robotisée",
                "gears": 7,
                "technology": "Double embrayage à sec",
                "manufacturer": "Volkswagen",
                "description": "Boîte DSG 7 rapports double embrayage à sec",
                "reliability_rating": 4,
                "maintenance_cost": "Élevé",
                "pros": ["Rapide", "Efficace", "Agréable"],
                "cons": ["Entretien coûteux", "Embrayages à surveiller"],
                "ideal_for": "Usage dynamique et mixte",
            },
            {
                "name": "BVA8",
                "type": "Automatique",
                "gears": 8,
                "technology": "Convertisseur de couple",
                "manufacturer": "ZF",
                "description": "Boîte automatique 8 rapports à convertisseur",
                "reliability_rating": 5,
                "maintenance_cost": "Moyen",
                "pros": ["Très fiable", "Douce", "Efficace", "Confort optimal"],
                "cons": ["Entretien spécialisé", "Poids"],
                "ideal_for": "Confort maximal, tous usages",
            },
            {
                "name": "CVT",
                "type": "CVT",
                "technology": "Variation continue",
                "description": "Transmission à variation continue",
                "reliability_rating": 4,
                "maintenance_cost": "Moyen",
                "pros": ["Douceur", "Économie", "Simplicité"],
                "cons": ["Bruit moteur élevé", "Sensation étrange"],
                "ideal_for": "Usage souple et économique",
            },
        ]

        transmissions = {}
        for trans_data in transmissions_data:
            trans = Transmission(
                id=str(uuid.uuid4()),
                **trans_data
            )
            db.add(trans)
            transmissions[trans_data["name"]] = trans
            print(f"  ✓ {trans_data['name']}")

        db.commit()
        print(f"✅ {len(transmissions_data)} transmissions ajoutées")

        # ==================== MODÈLES ====================
        print("\n🚗 Ajout des modèles de voitures...")

        # Exemple de modèles pour Renault
        renault_models = [
            {
                "brand_id": brands["Renault"].id,
                "name": "Clio V",
                "generation": "Phase 1",
                "year_start": 2019,
                "is_current": True,
                "body_type": "Berline 5 portes",
                "segment": "Segment B",
                "category": "Citadine polyvalente",
                "description": "Best-seller de Renault, la Clio V combine design moderne, technologies avancées et habitabilité. Idéale pour la ville comme pour les longs trajets.",
                "length": 4050,
                "width": 1798,
                "height": 1440,
                "wheelbase": 2583,
                "trunk_capacity": 391,
                "weight": 1130,
                "seats": 5,
                "doors": 5,
                "price_new_min": 18000,
                "price_new_max": 28000,
                "price_used_avg": 15000,
                "avg_consumption": "5.5",
                "co2_emissions": 125,
                "top_speed": 180,
                "acceleration_0_100": "9.8",
                "standard_equipment": ["Climatisation", "Régulateur de vitesse", "Écran tactile 7\"", "Aide parking"],
                "safety_features": ["6 airbags", "ABS", "ESP", "Freinage d'urgence"],
                "safety_rating": 5,
                "reliability_score": 80,
                "owner_satisfaction": 85,
                "pros": ["Habitabilité", "Équipements", "Agrément de conduite", "Design"],
                "cons": ["Finitions moyennes", "Motorisations limitées", "Options chères"],
                "ideal_for": "Premier véhicule, usage quotidien urbain et périurbain"
            },
            {
                "brand_id": brands["Renault"].id,
                "name": "Captur",
                "generation": "Génération 2",
                "year_start": 2020,
                "is_current": True,
                "body_type": "SUV compact",
                "segment": "Segment B",
                "category": "SUV urbain",
                "description": "SUV compact polyvalent, le Captur offre position de conduite surélevée et modularité. Version hybride disponible.",
                "length": 4227,
                "width": 1797,
                "height": 1576,
                "wheelbase": 2639,
                "trunk_capacity": 536,
                "weight": 1260,
                "seats": 5,
                "doors": 5,
                "price_new_min": 22000,
                "price_new_max": 35000,
                "price_used_avg": 18000,
                "safety_rating": 5,
                "reliability_score": 78,
                "owner_satisfaction": 82,
                "pros": ["Habitabilité", "Coffre modulable", "Confort", "Hybride E-Tech"],
                "cons": ["Prix élevé", "Insonorisation moyenne", "Plastiques durs"],
                "ideal_for": "Familles, trajets mixtes, recherche de polyvalence"
            },
        ]

        models = []
        for model_data in renault_models:
            model = CarModel(
                id=str(uuid.uuid4()),
                **model_data
            )
            db.add(model)
            models.append(model)
            print(f"  ✓ {model_data['name']}")

        db.commit()
        print(f"✅ {len(renault_models)} modèles Renault ajoutés")

        # ==================== AVIS ====================
        print("\n💬 Ajout des avis clients...")

        # Avis sur Renault
        brand_reviews = [
            {
                "brand_id": brands["Renault"].id,
                "source": "Forum Auto",
                "author": "Pierre M.",
                "title": "Bon rapport qualité-prix",
                "content": "J'ai toujours roulé en Renault et je ne suis jamais déçu. Le rapport qualité-prix est excellent, le réseau de distribution est partout en France. Les Clio et Mégane sont des valeurs sûres.",
                "overall_rating": 4,
                "reliability_rating": 3,
                "quality_rating": 4,
                "value_rating": 5,
                "review_date": datetime(2024, 3, 15),
                "helpful_count": 45
            },
            {
                "brand_id": brands["Toyota"].id,
                "source": "Caradisiac",
                "author": "Marie L.",
                "title": "Fiabilité exceptionnelle",
                "content": "350 000 km avec ma Corolla hybride, aucune panne majeure. L'hybride Toyota est au point, consommation ridicule en ville. Je recommande les yeux fermés pour ceux qui cherchent la tranquillité.",
                "overall_rating": 5,
                "reliability_rating": 5,
                "quality_rating": 4,
                "value_rating": 4,
                "review_date": datetime(2024, 5, 20),
                "helpful_count": 128
            },
        ]

        for review_data in brand_reviews:
            review = BrandReview(
                id=str(uuid.uuid4()),
                **review_data
            )
            db.add(review)
            print(f"  ✓ Avis de {review_data['author']} sur {brands[next(k for k, v in brands.items() if v.id == review_data['brand_id'])].name}")

        db.commit()
        print(f"✅ {len(brand_reviews)} avis ajoutés")

        print("\n🎉 Peuplement terminé avec succès!")
        print(f"   • {len(brands_data)} marques")
        print(f"   • {len(engines_data)} moteurs")
        print(f"   • {len(transmissions_data)} transmissions")
        print(f"   • {len(renault_models)} modèles")
        print(f"   • {len(brand_reviews)} avis")

    except Exception as e:
        print(f"\n❌ Erreur lors du peuplement: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_encyclopedia()
