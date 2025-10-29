#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier l'encodage de la base de données PostgreSQL"""

import subprocess
import sys
import os
import getpass
import re
from urllib.parse import urlparse

def parse_database_url(url):
    """Parse une DATABASE_URL PostgreSQL"""
    # Format: postgresql://user:password@host:port/dbname
    # ou postgresql+psycopg2://user:password@host:port/dbname
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "127.0.0.1",
        "port": str(parsed.port or 5432),
        "dbname": parsed.path.lstrip('/') if parsed.path else "recherche_auto",
        "user": parsed.username or "postgres",
        "password": parsed.password or ""
    }

def get_db_configs():
    """Récupère les configurations de base de données à essayer"""
    configs = []

    # 1. Essayer depuis DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        try:
            config = parse_database_url(database_url)
            configs.append(config)
            print(f"Configuration trouvée depuis DATABASE_URL")
        except:
            pass

    # 2. Configuration par défaut basée sur les fichiers du projet
    # La base de données est 'recherche_auto' avec l'utilisateur 'app'
    default_config = {
        "host": "127.0.0.1",
        "port": "5432",
        "dbname": "recherche_auto",
        "user": "app",
        "password": None  # Sera demandé si nécessaire
    }

    # 3. Essayer quelques mots de passe courants
    for password in ["password", "changeme", "postgres", "app"]:
        config = default_config.copy()
        config["password"] = password
        configs.append(config)

    return configs

# Forcer l'encodage UTF-8 pour la sortie Python sur Windows
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def run_psql_query(query, config):
    """Exécute une requête via psql et retourne le résultat"""
    env = os.environ.copy()
    env['PGPASSWORD'] = config['password']
    env['PGCLIENTENCODING'] = 'UTF8'

    cmd = [
        'psql',
        '-h', config['host'],
        '-p', config['port'],
        '-U', config['user'],
        '-d', config['dbname'],
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

def test_connection(config):
    """Teste si une configuration fonctionne"""
    result = run_psql_query("SELECT 1;", config)
    return result is not None

def main():
    try:
        print("Vérification de l'encodage de la base de données PostgreSQL...\n")

        # Obtenir les configurations à essayer
        configs = get_db_configs()

        # Trouver une configuration qui fonctionne
        working_config = None
        for i, config in enumerate(configs):
            print(f"Test de la configuration {i+1}: {config['user']}@{config['host']}:{config['port']}/{config['dbname']}")
            if test_connection(config):
                working_config = config
                print(f"✓ Connexion réussie avec cette configuration\n")
                break
            else:
                print(f"✗ Échec de connexion")

        # Si aucune configuration n'a fonctionné, demander le mot de passe
        if not working_config:
            print("\n⚠ Aucune configuration automatique n'a fonctionné.")
            print("Veuillez entrer les informations de connexion manuellement.\n")

            config = {
                "host": input("Hôte [127.0.0.1]: ").strip() or "127.0.0.1",
                "port": input("Port [5432]: ").strip() or "5432",
                "dbname": input("Base de données [recherche_auto]: ").strip() or "recherche_auto",
                "user": input("Utilisateur [app]: ").strip() or "app",
                "password": getpass.getpass("Mot de passe: ")
            }

            print(f"\nTest de la connexion avec {config['user']}@{config['host']}:{config['port']}/{config['dbname']}...")
            if test_connection(config):
                working_config = config
                print("✓ Connexion réussie!\n")
            else:
                print("✗ Échec de connexion")
                print("\nImpossible de se connecter à la base de données.")
                sys.exit(1)

        # Vérifier l'encodage de la base de données
        encoding = run_psql_query(
            "SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database();",
            working_config
        )
        if encoding:
            print(f"Encodage de la base de données: {encoding}")

        # Vérifier LC_COLLATE et LC_CTYPE
        collate_ctype = run_psql_query(
            "SELECT datcollate || '|' || datctype FROM pg_database WHERE datname = current_database();",
            working_config
        )
        if collate_ctype:
            parts = collate_ctype.split('|')
            if len(parts) == 2:
                print(f"LC_COLLATE: {parts[0]}")
                print(f"LC_CTYPE: {parts[1]}")

        # Vérifier l'encodage client
        client_encoding = run_psql_query("SHOW client_encoding;", working_config)
        if client_encoding:
            print(f"Encodage client: {client_encoding}")

        # Vérifier l'encodage serveur
        server_encoding = run_psql_query("SHOW server_encoding;", working_config)
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
