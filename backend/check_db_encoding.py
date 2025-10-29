#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier l'encodage de la base de données PostgreSQL"""

import psycopg2
import os
import sys

# Sur Windows, forcer l'encodage UTF-8 pour la communication avec PostgreSQL
if sys.platform == 'win32':
    os.environ['PGCLIENTENCODING'] = 'UTF8'

try:
    # Connexion à la base de données avec encodage UTF-8 explicite
    conn = psycopg2.connect(
        "host=127.0.0.1 port=5432 dbname=vehicles user=app password=changeme client_encoding=utf8"
    )
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
