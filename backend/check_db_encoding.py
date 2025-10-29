#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier l'encodage de la base de données PostgreSQL"""

import os
import sys
import locale

# IMPORTANT: Définir les variables d'environnement AVANT d'importer psycopg2
if sys.platform == 'win32':
    # Sur Windows, utiliser l'encodage Windows-1252 pour la connexion initiale
    # puis basculer vers UTF-8
    os.environ['PGCLIENTENCODING'] = 'WIN1252'

    # Forcer l'encodage UTF-8 pour Python
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    if sys.stderr.encoding != 'utf-8':
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

# Maintenant importer psycopg2
import psycopg2
import psycopg2.extensions

# Forcer psycopg2 à utiliser UTF-8 pour décoder les messages du serveur
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

try:
    # Connexion à la base de données
    # L'encodage est déjà défini via PGCLIENTENCODING avant l'import
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="vehicles",
        user="app",
        password="changeme"
    )

    # Basculer vers UTF-8 après la connexion
    conn.set_client_encoding('UTF8')
    cur = conn.cursor()

    # Vérifier l'encodage de la base de données
    cur.execute("SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database();")
    encoding = cur.fetchone()[0]
    print(f"Encodage de la base de données: {encoding}")

    # Vérifier le LC_COLLATE et LC_CTYPE depuis pg_database
    cur.execute("SELECT datcollate, datctype FROM pg_database WHERE datname = current_database();")
    collate, ctype = cur.fetchone()
    print(f"LC_COLLATE: {collate}")
    print(f"LC_CTYPE: {ctype}")

    # Vérifier l'encodage client
    cur.execute("SHOW client_encoding;")
    client_encoding = cur.fetchone()[0]
    print(f"Encodage client: {client_encoding}")

    # Vérifier quelques paramètres de configuration
    cur.execute("SHOW server_encoding;")
    server_encoding = cur.fetchone()[0]
    print(f"Encodage serveur: {server_encoding}")

    print("\n✓ Vérification terminée avec succès")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()
