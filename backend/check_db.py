#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier la base de données et les tables"""

import subprocess
import sys
import os

# Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "5432",
    "dbname": "recherche_auto",
    "user": "app",
    "password": "changeme"
}

def run_psql_query(query):
    """Exécute une requête via psql"""
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_CONFIG['password']
    env['PGCLIENTENCODING'] = 'UTF8'

    cmd = [
        'psql',
        '-h', DB_CONFIG['host'],
        '-p', DB_CONFIG['port'],
        '-U', DB_CONFIG['user'],
        '-d', DB_CONFIG['dbname'],
        '-t',  # Tuple only
        '-A',  # Unaligned
        '-c', query
    ]

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erreur: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Erreur: psql non trouvé dans le PATH")
        return None

def main():
    print("=" * 70)
    print("Vérification de la Base de Données PostgreSQL".center(70))
    print("=" * 70)
    print()

    # Lister les tables
    print("📋 Tables dans le schéma public:")
    tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
    """
    tables_result = run_psql_query(tables_query)

    if tables_result:
        tables = [t for t in tables_result.split('\n') if t.strip()]
        if tables:
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
            print(f"\n✓ Total: {len(tables)} tables")
        else:
            print("  ⚠ Aucune table trouvée")
            print("\n  Avez-vous exécuté les migrations ?")
            print("  Commande: alembic upgrade head")
    else:
        print("  ✗ Impossible de récupérer les tables")
        return

    print()

    # Vérifier alembic_version
    print("🔄 Version de migration Alembic:")
    version_query = "SELECT version_num FROM alembic_version;"
    version_result = run_psql_query(version_query)

    if version_result:
        print(f"  Version: {version_result}")
    else:
        print("  ⚠ Table alembic_version non trouvée ou vide")

    print()

    # Compter les enregistrements dans chaque table
    print("📊 Nombre d'enregistrements par table:")
    if tables_result:
        tables = [t for t in tables_result.split('\n') if t.strip() and t != 'alembic_version']
        for table in tables:
            count_query = f"SELECT COUNT(*) FROM {table};"
            count_result = run_psql_query(count_query)
            if count_result:
                print(f"  {table:.<30} {count_result:>5} enregistrements")

    print()
    print("=" * 70)
    print("✓ Vérification terminée".center(70))
    print("=" * 70)

if __name__ == "__main__":
    main()
