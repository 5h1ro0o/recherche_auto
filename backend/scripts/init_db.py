#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Usage: python scripts/init_db.py
"""

import sys
import subprocess
from pathlib import Path

# Ajouter le dossier backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("Initialisation de la base de données PostgreSQL")
print("=" * 80)
print()

# Charger la configuration pour afficher la DATABASE_URL
try:
    from app.config import settings
    print(f"✓ Configuration chargée depuis .env")
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print()
except Exception as e:
    print(f"✗ Erreur lors du chargement de la configuration: {e}")
    print()
    sys.exit(1)

# Vérifier la connexion à la base de données
print("Étape 1: Vérification de la connexion à PostgreSQL...")
try:
    from app.db import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ Connexion réussie!")
        print(f"  PostgreSQL version: {version.split(',')[0]}")
        print()
except Exception as e:
    print(f"✗ Erreur de connexion à PostgreSQL:")
    print(f"  {e}")
    print()
    print("Vérifiez que:")
    print("  1. PostgreSQL est démarré")
    print("  2. La base de données existe (createdb vehicles)")
    print("  3. Les credentials dans .env sont corrects")
    print()
    sys.exit(1)

# Exécuter les migrations Alembic
print("Étape 2: Application des migrations Alembic...")
print()

try:
    # Vérifier l'état actuel des migrations
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True,
        cwd=backend_dir
    )

    print("État actuel des migrations:")
    if result.stdout.strip():
        print(f"  {result.stdout.strip()}")
    else:
        print("  Aucune migration appliquée")
    print()

    # Appliquer toutes les migrations
    print("Application de toutes les migrations (alembic upgrade head)...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        cwd=backend_dir
    )

    if result.returncode == 0:
        print("✓ Migrations appliquées avec succès!")
        print()
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        print()
    else:
        print("✗ Erreur lors de l'application des migrations:")
        print(result.stderr)
        sys.exit(1)

except FileNotFoundError:
    print("✗ Alembic n'est pas installé ou n'est pas dans le PATH")
    print("  Installez-le avec: pip install alembic")
    sys.exit(1)
except Exception as e:
    print(f"✗ Erreur inattendue: {e}")
    sys.exit(1)

# Vérifier que les tables ont été créées
print("Étape 3: Vérification des tables créées...")
try:
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if tables:
        print(f"✓ {len(tables)} tables créées:")
        for table in sorted(tables):
            print(f"  - {table}")
        print()
    else:
        print("✗ Aucune table créée")
        sys.exit(1)

except Exception as e:
    print(f"✗ Erreur lors de la vérification: {e}")
    sys.exit(1)

print("=" * 80)
print("✓ Initialisation terminée avec succès!")
print("=" * 80)
print()
print("Vous pouvez maintenant:")
print("  1. Démarrer le serveur: uvicorn app.main:app --reload")
print("  2. Créer votre premier compte utilisateur")
print()
