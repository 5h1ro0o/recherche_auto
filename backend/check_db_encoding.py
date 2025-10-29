#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier l'encodage de la base de données PostgreSQL"""

import psycopg2
import psycopg2.extensions
import os
import sys
import locale

# Sur Windows, forcer l'encodage UTF-8 à tous les niveaux
if sys.platform == 'win32':
    # Forcer l'encodage UTF-8 pour Python
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

    # Variables d'environnement PostgreSQL
    os.environ['PGCLIENTENCODING'] = 'UTF8'

    # Définir la locale en UTF-8
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass  # Ignorer si ça ne fonctionne pas

# Forcer psycopg2 à utiliser UTF-8 pour décoder les messages du serveur
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

# Fonction pour tenter la connexion avec différents encodages
def connect_with_encoding_fallback():
    encodings = ['UTF8', 'LATIN1', 'WIN1252', 'ISO-8859-1']

    for encoding in encodings:
        try:
            if sys.platform == 'win32':
                os.environ['PGCLIENTENCODING'] = encoding

            conn = psycopg2.connect(
                host="127.0.0.1",
                port=5432,
                dbname="vehicles",
                user="app",
                password="changeme"
            )

            # Si la connexion réussit, forcer UTF-8 après connexion
            conn.set_client_encoding('UTF8')
            return conn

        except UnicodeDecodeError:
            if encoding == encodings[-1]:
                raise
            continue
        except Exception as e:
            # Si c'est une autre erreur que UnicodeDecodeError, la relancer
            raise

    return None

try:
    # Tenter la connexion avec gestion des encodages
    conn = connect_with_encoding_fallback()
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
