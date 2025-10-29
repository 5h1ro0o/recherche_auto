# backend/add_test_vehicles.py
"""
Script pour ajouter des véhicules de test dans la base de données
"""

import uuid
from datetime import datetime
from app.db import SessionLocal
from app.models import Vehicle

def add_test_vehicles():
    """Ajoute des véhicules de test dans la base de données"""
    db = SessionLocal()

    test_vehicles = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Peugeot 308 1.6 HDi 92ch Active Business Pack 5p',
            'make': 'Peugeot',
            'model': '308',
            'price': 12500,
            'year': 2018,
            'mileage': 85000,
            'fuel_type': 'diesel',
            'transmission': 'manuelle',
            'description': 'Peugeot 308 en excellent état, entretien suivi, GPS, radar de recul, climatisation automatique.',
            'images': ['https://example.com/peugeot308.jpg'],
            'location_city': 'Paris'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Renault Clio V TCe 100 Zen',
            'make': 'Renault',
            'model': 'Clio',
            'price': 15800,
            'year': 2020,
            'mileage': 42000,
            'fuel_type': 'essence',
            'transmission': 'manuelle',
            'description': 'Renault Clio récente, première main, carnet d\'entretien à jour, écran tactile.',
            'images': ['https://example.com/clio.jpg'],
            'location_city': 'Lyon'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Volkswagen Golf VII 1.6 TDI 115 BlueMotion Technology FAP Confortline Business',
            'make': 'Volkswagen',
            'model': 'Golf',
            'price': 18900,
            'year': 2019,
            'mileage': 67000,
            'fuel_type': 'diesel',
            'transmission': 'manuelle',
            'description': 'Volkswagen Golf 7 très bien équipée, intérieur impeccable, GPS, caméra de recul.',
            'images': ['https://example.com/golf.jpg'],
            'location_city': 'Marseille'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Citroën C3 PureTech 82 Feel',
            'make': 'Citroën',
            'model': 'C3',
            'price': 11200,
            'year': 2017,
            'mileage': 92000,
            'fuel_type': 'essence',
            'transmission': 'manuelle',
            'description': 'Citroën C3 économique et fiable, parfait pour la ville, climatisation, Bluetooth.',
            'images': ['https://example.com/c3.jpg'],
            'location_city': 'Toulouse'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'BMW Série 3 320d 190ch M Sport',
            'make': 'BMW',
            'model': 'Série 3',
            'price': 28500,
            'year': 2019,
            'mileage': 55000,
            'fuel_type': 'diesel',
            'transmission': 'automatique',
            'description': 'BMW Série 3 M Sport, configuration haut de gamme, cuir, toit ouvrant, GPS.',
            'images': ['https://example.com/bmw3.jpg'],
            'location_city': 'Bordeaux'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Audi A4 2.0 TDI 150ch S line S tronic 7',
            'make': 'Audi',
            'model': 'A4',
            'price': 32000,
            'year': 2020,
            'mileage': 38000,
            'fuel_type': 'diesel',
            'transmission': 'automatique',
            'description': 'Audi A4 S line comme neuve, équipements premium, sièges chauffants, LED.',
            'images': ['https://example.com/audia4.jpg'],
            'location_city': 'Nantes'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Peugeot 208 1.2 PureTech 100ch S&S Allure Pack EAT8',
            'make': 'Peugeot',
            'model': '208',
            'price': 17500,
            'year': 2021,
            'mileage': 25000,
            'fuel_type': 'essence',
            'transmission': 'automatique',
            'description': 'Peugeot 208 récente, boîte automatique, GPS 3D, caméra de recul, garantie constructeur.',
            'images': ['https://example.com/208.jpg'],
            'location_city': 'Lille'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Mercedes Classe A 180d 116ch AMG Line 7G-DCT',
            'make': 'Mercedes',
            'model': 'Classe A',
            'price': 29800,
            'year': 2020,
            'mileage': 42000,
            'fuel_type': 'diesel',
            'transmission': 'automatique',
            'description': 'Mercedes Classe A AMG Line, pack Premium, écran MBUX, sièges sport.',
            'images': ['https://example.com/mercedes.jpg'],
            'location_city': 'Nice'
        },
    ]

    try:
        # Vérifier si des véhicules existent déjà
        count = db.query(Vehicle).count()
        if count > 0:
            print(f"⚠️ La base contient déjà {count} véhicules.")
            response = input("Voulez-vous ajouter quand même les véhicules de test ? (o/n): ")
            if response.lower() != 'o':
                print("❌ Opération annulée")
                return

        # Ajouter les véhicules
        added = 0
        for vehicle_data in test_vehicles:
            vehicle = Vehicle(**vehicle_data)
            db.add(vehicle)
            added += 1

        db.commit()
        print(f"✅ {added} véhicules de test ajoutés avec succès !")
        print(f"\n📊 Total de véhicules dans la base: {db.query(Vehicle).count()}")

        # Afficher quelques statistiques
        print("\n📈 Statistiques:")
        print(f"   - Peugeot: {db.query(Vehicle).filter(Vehicle.make == 'Peugeot').count()}")
        print(f"   - Renault: {db.query(Vehicle).filter(Vehicle.make == 'Renault').count()}")
        print(f"   - Volkswagen: {db.query(Vehicle).filter(Vehicle.make == 'Volkswagen').count()}")
        print(f"   - BMW: {db.query(Vehicle).filter(Vehicle.make == 'BMW').count()}")
        print(f"   - Audi: {db.query(Vehicle).filter(Vehicle.make == 'Audi').count()}")
        print(f"   - Mercedes: {db.query(Vehicle).filter(Vehicle.make == 'Mercedes').count()}")
        print(f"   - Citroën: {db.query(Vehicle).filter(Vehicle.make == 'Citroën').count()}")

    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des véhicules: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    print("🚗 Ajout de véhicules de test dans la base de données\n")
    add_test_vehicles()
