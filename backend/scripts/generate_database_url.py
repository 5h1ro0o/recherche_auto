#!/usr/bin/env python3
"""
Script pour générer une DATABASE_URL correctement encodée
Usage: python scripts/generate_database_url.py
"""

from urllib.parse import quote_plus

def generate_database_url():
    print("=" * 60)
    print("Générateur de DATABASE_URL pour PostgreSQL")
    print("=" * 60)
    print()
    print("Ce script vous aide à créer une URL de connexion PostgreSQL")
    print("correctement encodée pour les caractères spéciaux.")
    print()

    # Collecter les informations
    user = input("Nom d'utilisateur PostgreSQL (défaut: postgres): ").strip() or "postgres"
    password = input("Mot de passe PostgreSQL: ").strip() or "postgres"
    host = input("Hôte (défaut: localhost): ").strip() or "localhost"
    port = input("Port (défaut: 5432): ").strip() or "5432"
    database = input("Nom de la base de données (défaut: vehicles): ").strip() or "vehicles"

    # Encoder les parties qui peuvent contenir des caractères spéciaux
    user_encoded = quote_plus(user)
    password_encoded = quote_plus(password)
    database_encoded = quote_plus(database)

    # Construire l'URL
    database_url = f"postgresql+psycopg2://{user_encoded}:{password_encoded}@{host}:{port}/{database_encoded}"

    print()
    print("=" * 60)
    print("URL générée:")
    print("=" * 60)
    print()
    print(database_url)
    print()
    print("Copiez cette ligne dans votre fichier backend/.env:")
    print()
    print(f"DATABASE_URL={database_url}")
    print()

    # Afficher les différences si des caractères ont été encodés
    if user != user_encoded or password != password_encoded or database != database_encoded:
        print("Caractères encodés:")
        if user != user_encoded:
            print(f"  - Utilisateur: {user} → {user_encoded}")
        if password != password_encoded:
            print(f"  - Mot de passe: {password} → {password_encoded}")
        if database != database_encoded:
            print(f"  - Base de données: {database} → {database_encoded}")
        print()

if __name__ == "__main__":
    generate_database_url()
