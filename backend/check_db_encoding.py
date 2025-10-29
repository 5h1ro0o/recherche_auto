#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier l'encodage de la base de données PostgreSQL"""

import subprocess
import sys
import os

# Configuration de la connexion
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "vehicles"
DB_USER = "app"
DB_PASSWORD = "changeme"

# Forcer l'encodage UTF-8 pour la sortie Python sur Windows
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def run_psql_query(query):
    """Exécute une requête via psql et retourne le résultat"""
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    env['PGCLIENTENCODING'] = 'UTF8'

    cmd = [
        'psql',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-t',  # Tuple only (pas de headers)
        '-A',  # Unaligned (pas de formatting)
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
        print(f"Erreur lors de l'exécution de la requête: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Erreur: psql n'est pas trouvé dans le PATH")
        print("Assurez-vous que PostgreSQL client est installé et dans le PATH")
        return None

def main():
    try:
        print("Vérification de l'encodage de la base de données PostgreSQL...\n")

        # Vérifier l'encodage de la base de données
        encoding = run_psql_query(
            "SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database();"
        )
        if encoding:
            print(f"Encodage de la base de données: {encoding}")

        # Vérifier LC_COLLATE et LC_CTYPE
        collate_ctype = run_psql_query(
            "SELECT datcollate || '|' || datctype FROM pg_database WHERE datname = current_database();"
        )
        if collate_ctype:
            parts = collate_ctype.split('|')
            if len(parts) == 2:
                print(f"LC_COLLATE: {parts[0]}")
                print(f"LC_CTYPE: {parts[1]}")

        # Vérifier l'encodage client
        client_encoding = run_psql_query("SHOW client_encoding;")
        if client_encoding:
            print(f"Encodage client: {client_encoding}")

        # Vérifier l'encodage serveur
        server_encoding = run_psql_query("SHOW server_encoding;")
        if server_encoding:
            print(f"Encodage serveur: {server_encoding}")

        print("\n✓ Vérification terminée avec succès")

    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
