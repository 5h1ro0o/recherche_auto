#!/usr/bin/env python3
"""
Script de debug pour voir la DATABASE_URL et diagnostiquer le problème d'encodage
"""
import os
import sys
from urllib.parse import quote_plus, urlparse, parse_qs

print("=" * 80)
print("DEBUG DATABASE_URL")
print("=" * 80)
print()

# Essayer de lire la DATABASE_URL
db_url = os.getenv("DATABASE_URL", "NOT SET")

print(f"1. DATABASE_URL brute (type={type(db_url)}):")
print(f"   {repr(db_url)}")
print()

if db_url != "NOT SET":
    print("2. Analyse byte par byte:")
    if isinstance(db_url, str):
        for i, char in enumerate(db_url):
            print(f"   Position {i:3d}: '{char}' (ord={ord(char):3d}, hex=0x{ord(char):02x})")
            if ord(char) > 127:
                print(f"                ^^^ CARACTÈRE NON-ASCII DÉTECTÉ!")
    print()

    print("3. Tentative de parsing:")
    try:
        parsed = urlparse(db_url)
        print(f"   Schéma: {parsed.scheme}")
        print(f"   Utilisateur: {parsed.username}")
        print(f"   Mot de passe: {parsed.password}")
        print(f"   Hôte: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Database: {parsed.path}")
    except Exception as e:
        print(f"   ERREUR: {e}")
    print()

print("=" * 80)
print("SOLUTION")
print("=" * 80)
print()
print("Si des caractères non-ASCII ont été détectés, vous devez:")
print("1. Créer un fichier .env dans le dossier backend/ avec:")
print("   DATABASE_URL=postgresql+psycopg2://postgres:votremotdepasse@localhost:5432/vehicles")
print()
print("2. OU utiliser le script pour générer une URL encodée:")
print("   python scripts/generate_database_url.py")
print()
print("3. OU changer votre mot de passe PostgreSQL pour ne contenir que:")
print("   - Lettres non accentuées (a-z, A-Z)")
print("   - Chiffres (0-9)")
print("   - Caractères spéciaux simples (!, $, %, ^, &, *, -, _, +, =)")
print()
