"""
Script pour tester la connexion a PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/recherche_auto")

print("Test de connexion a la base de donnees...")
# Masquer le mot de passe dans l'affichage
url_parts = DATABASE_URL.split('@')
if len(url_parts) == 2:
    masked_url = "postgresql+psycopg2://***:***@" + url_parts[1]
else:
    masked_url = DATABASE_URL
print(f"URL: {masked_url}")

try:
    # Creer un engine
    engine = create_engine(DATABASE_URL, echo=False)

    # Tester la connexion
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("Connexion reussie !")
        print(f"PostgreSQL version: {version}")

        # Verifier les tables existantes
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """))
        tables = [row[0] for row in result.fetchall()]

        if tables:
            print(f"\nTables existantes ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
        else:
            print("\nAucune table trouvee. Vous devez executer les migrations Alembic.")
            print("   Commande: alembic upgrade head")

        sys.exit(0)

except Exception as e:
    print("Erreur de connexion !")
    print(f"{type(e).__name__}: {e}")
    print("\nSolutions possibles:")
    print("  1. Verifier que PostgreSQL est installe et demarre")
    print("  2. Verifier les identifiants dans le fichier .env")
    print("  3. Creer la base de donnees 'recherche_auto' si elle n'existe pas")
    print("\nPour installer PostgreSQL sur Windows:")
    print("  - Telecharger: https://www.postgresql.org/download/windows/")
    print("  - Ou utiliser: winget install PostgreSQL.PostgreSQL")
    print("\nPour creer la base de donnees:")
    print("  psql -U postgres")
    print("  CREATE DATABASE recherche_auto;")
    sys.exit(1)
