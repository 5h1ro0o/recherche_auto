#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Crée l'index Elasticsearch et ajoute des données de test
"""
import os
import sys
from elasticsearch import Elasticsearch
from datetime import datetime

# Configuration
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://127.0.0.1:9200")
ES_INDEX = os.getenv("ES_INDEX", "vehicles")

# Données de test
SAMPLE_VEHICLES = [
    {
        "title": "Peugeot 208 Active 1.2 PureTech",
        "make": "Peugeot",
        "model": "208",
        "year": 2020,
        "price": 14500,
        "mileage": 35000,
        "fuel_type": "Essence",
        "transmission": "Manuelle",
        "location": "Paris",
        "seller_type": "PRO",
        "description": "Magnifique Peugeot 208 en excellent état. Première main, entretien complet chez le concessionnaire.",
        "source": "test_data",
        "url": "http://example.com/vehicle/1",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Renault Clio V TCe 90",
        "make": "Renault",
        "model": "Clio",
        "year": 2021,
        "price": 16900,
        "mileage": 28000,
        "fuel_type": "Essence",
        "transmission": "Manuelle",
        "location": "Lyon",
        "seller_type": "PRO",
        "description": "Renault Clio récente, très bien entretenue. Garantie constructeur restante.",
        "source": "test_data",
        "url": "http://example.com/vehicle/2",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Volkswagen Golf 7 TDI 115",
        "make": "Volkswagen",
        "model": "Golf",
        "year": 2019,
        "price": 18500,
        "mileage": 62000,
        "fuel_type": "Diesel",
        "transmission": "Manuelle",
        "location": "Marseille",
        "seller_type": "PRO",
        "description": "Golf 7 diesel, idéale pour les gros rouleurs. GPS, climatisation automatique.",
        "source": "test_data",
        "url": "http://example.com/vehicle/3",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "BMW Série 3 320d 190ch",
        "make": "BMW",
        "model": "Série 3",
        "year": 2018,
        "price": 25900,
        "mileage": 78000,
        "fuel_type": "Diesel",
        "transmission": "Automatique",
        "location": "Bordeaux",
        "seller_type": "PRO",
        "description": "BMW Série 3 berline sport, boîte automatique, cuir, toit ouvrant.",
        "source": "test_data",
        "url": "http://example.com/vehicle/4",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Citroën C3 PureTech 82",
        "make": "Citroën",
        "model": "C3",
        "year": 2020,
        "price": 12900,
        "mileage": 41000,
        "fuel_type": "Essence",
        "transmission": "Manuelle",
        "location": "Toulouse",
        "seller_type": "PARTICULIER",
        "description": "Citroën C3 confortable, première main, carnet d'entretien à jour.",
        "source": "test_data",
        "url": "http://example.com/vehicle/5",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Audi A4 2.0 TDI 150",
        "make": "Audi",
        "model": "A4",
        "year": 2017,
        "price": 22500,
        "mileage": 95000,
        "fuel_type": "Diesel",
        "transmission": "Automatique",
        "location": "Nantes",
        "seller_type": "PRO",
        "description": "Audi A4 break, spacieuse et élégante. Intérieur cuir, pack LED.",
        "source": "test_data",
        "url": "http://example.com/vehicle/6",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Mercedes Classe A 180d AMG Line",
        "make": "Mercedes",
        "model": "Classe A",
        "year": 2019,
        "price": 27900,
        "mileage": 52000,
        "fuel_type": "Diesel",
        "transmission": "Automatique",
        "location": "Lille",
        "seller_type": "PRO",
        "description": "Mercedes Classe A finition AMG Line, écran MBUX, système audio premium.",
        "source": "test_data",
        "url": "http://example.com/vehicle/7",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Ford Fiesta 1.0 EcoBoost 100",
        "make": "Ford",
        "model": "Fiesta",
        "year": 2021,
        "price": 14900,
        "mileage": 22000,
        "fuel_type": "Essence",
        "transmission": "Manuelle",
        "location": "Strasbourg",
        "seller_type": "PARTICULIER",
        "description": "Ford Fiesta récente, moteur EcoBoost performant et économique.",
        "source": "test_data",
        "url": "http://example.com/vehicle/8",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Toyota Yaris Hybrid 116h",
        "make": "Toyota",
        "model": "Yaris",
        "year": 2020,
        "price": 17500,
        "mileage": 38000,
        "fuel_type": "Hybride",
        "transmission": "Automatique",
        "location": "Nice",
        "seller_type": "PRO",
        "description": "Toyota Yaris hybride, économique et fiable. Garantie constructeur restante.",
        "source": "test_data",
        "url": "http://example.com/vehicle/9",
        "created_at": datetime.now().isoformat(),
    },
    {
        "title": "Dacia Sandero TCe 90",
        "make": "Dacia",
        "model": "Sandero",
        "year": 2021,
        "price": 11900,
        "mileage": 18000,
        "fuel_type": "Essence",
        "transmission": "Manuelle",
        "location": "Rennes",
        "seller_type": "PARTICULIER",
        "description": "Dacia Sandero récente, excellent rapport qualité/prix. Idéale premier véhicule.",
        "source": "test_data",
        "url": "http://example.com/vehicle/10",
        "created_at": datetime.now().isoformat(),
    },
]

# Mapping pour l'index
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "french"},
            "make": {"type": "keyword"},
            "model": {"type": "keyword"},
            "year": {"type": "integer"},
            "price": {"type": "float"},
            "mileage": {"type": "integer"},
            "fuel_type": {"type": "keyword"},
            "transmission": {"type": "keyword"},
            "location": {"type": "text"},
            "seller_type": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "french"},
            "source": {"type": "keyword"},
            "url": {"type": "keyword"},
            "created_at": {"type": "date"},
        }
    }
}


def main():
    print("🚀 Initialisation de la base de données...")
    print(f"📡 Connexion à Elasticsearch: {ELASTIC_HOST}")

    # Connexion à Elasticsearch
    try:
        es = Elasticsearch(hosts=[ELASTIC_HOST])

        # Vérifier la connexion
        if not es.ping():
            print("❌ Impossible de se connecter à Elasticsearch")
            print("💡 Assurez-vous que Elasticsearch est démarré:")
            print("   cd infra && docker-compose up -d elasticsearch")
            sys.exit(1)

        print("✅ Connexion à Elasticsearch réussie")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        sys.exit(1)

    # Créer l'index s'il n'existe pas
    print(f"\n📊 Vérification de l'index '{ES_INDEX}'...")

    try:
        if es.indices.exists(index=ES_INDEX):
            print(f"⚠️  L'index '{ES_INDEX}' existe déjà")
            response = input("   Voulez-vous le recréer? (y/N): ")
            if response.lower() == 'y':
                es.indices.delete(index=ES_INDEX)
                print(f"🗑️  Index '{ES_INDEX}' supprimé")
            else:
                print("⏭️  Conservation de l'index existant")
                return

        # Créer l'index
        es.indices.create(index=ES_INDEX, body=INDEX_MAPPING)
        print(f"✅ Index '{ES_INDEX}' créé avec succès")

    except Exception as e:
        print(f"❌ Erreur lors de la création de l'index: {e}")
        sys.exit(1)

    # Indexer les données de test
    print(f"\n📝 Indexation de {len(SAMPLE_VEHICLES)} véhicules de test...")

    indexed_count = 0
    for i, vehicle in enumerate(SAMPLE_VEHICLES, 1):
        try:
            es.index(index=ES_INDEX, id=f"test_{i}", document=vehicle)
            indexed_count += 1
            print(f"   ✓ {vehicle['title']}")
        except Exception as e:
            print(f"   ✗ Erreur pour {vehicle['title']}: {e}")

    # Rafraîchir l'index
    es.indices.refresh(index=ES_INDEX)

    print(f"\n✅ {indexed_count}/{len(SAMPLE_VEHICLES)} véhicules indexés avec succès!")

    # Afficher les statistiques
    try:
        count = es.count(index=ES_INDEX)
        print(f"\n📊 Statistiques:")
        print(f"   • Total de véhicules dans l'index: {count['count']}")

        # Test de recherche
        result = es.search(
            index=ES_INDEX,
            body={"query": {"match_all": {}}, "size": 3}
        )
        print(f"\n🔍 Exemple de recherche (3 premiers résultats):")
        for hit in result['hits']['hits']:
            doc = hit['_source']
            print(f"   • {doc['title']} - {doc['price']}€ - {doc['location']}")

    except Exception as e:
        print(f"⚠️  Erreur lors de la récupération des stats: {e}")

    print("\n" + "="*60)
    print("✅ Initialisation terminée avec succès!")
    print("="*60)
    print("\n💡 Prochaines étapes:")
    print("   1. Démarrez le backend: uvicorn app.main:app --reload")
    print("   2. Démarrez le frontend: cd frontend && npm run dev")
    print("   3. Testez la recherche: http://localhost:5173")
    print("\n📚 Pour lancer les scrapers réels:")
    print("   python app/worker.py --run-worker")
    print()


if __name__ == "__main__":
    main()
