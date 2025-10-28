#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script pour verifier et afficher l'encodage de la base de donnees PostgreSQL"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

try:
    import psycopg2

    # Construire la DSN manuellement pour eviter les problemes d'encodage
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="recherche_auto",
        user="app",
        password="changeme",
        client_encoding='utf8'
    )

    cursor = conn.cursor()

    # Verifier l'encodage de la base
    cursor.execute("SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = 'recherche_auto';")
    db_encoding = cursor.fetchone()[0]
    print(f"Encodage de la base de donnees: {db_encoding}")

    # Verifier la locale
    cursor.execute("SHOW lc_collate;")
    lc_collate = cursor.fetchone()[0]
    print(f"LC_COLLATE: {lc_collate}")

    cursor.execute("SHOW lc_ctype;")
    lc_ctype = cursor.fetchone()[0]
    print(f"LC_CTYPE: {lc_ctype}")

    cursor.execute("SHOW server_encoding;")
    server_encoding = cursor.fetchone()[0]
    print(f"Server encoding: {server_encoding}")

    cursor.execute("SHOW client_encoding;")
    client_encoding = cursor.fetchone()[0]
    print(f"Client encoding: {client_encoding}")

    cursor.close()
    conn.close()

    print("\nSi l'encodage n'est pas UTF8, il faut recreer la base de donnees.")

except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)
