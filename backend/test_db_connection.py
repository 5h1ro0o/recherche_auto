"""
Script pour tester la connexion à PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/recherche_auto")

print(f"🔍 Test de connexion à la base de données...")
print(f"📍 URL: {DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('//')[1], '***:***')}")

try:
    # Créer un engine
    engine = create_engine(DATABASE_URL, echo=False)

    # Tester la connexion
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connexion réussie !")
        print(f"📊 PostgreSQL version: {version}")

        # Vérifier les tables existantes
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """))
        tables = [row[0] for row in result.fetchall()]

        if tables:
            print(f"\n📋 Tables existantes ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
        else:
            print(f"\n⚠️  Aucune table trouvée. Vous devez exécuter les migrations Alembic.")
            print(f"   Commande: alembic upgrade head")

        sys.exit(0)

except Exception as e:
    print(f"❌ Erreur de connexion !")
    print(f"💥 {type(e).__name__}: {e}")
    print(f"\n📝 Solutions possibles:")
    print(f"  1. Vérifier que PostgreSQL est installé et démarré")
    print(f"  2. Vérifier les identifiants dans le fichier .env")
    print(f"  3. Créer la base de données 'recherche_auto' si elle n'existe pas")
    print(f"\n🔧 Pour installer PostgreSQL sur Windows:")
    print(f"  - Télécharger: https://www.postgresql.org/download/windows/")
    print(f"  - Ou utiliser: winget install PostgreSQL.PostgreSQL")
    print(f"\n🔧 Pour créer la base de données:")
    print(f"  psql -U postgres")
    print(f"  CREATE DATABASE recherche_auto;")
    sys.exit(1)
