"""Script pour inspecter la structure de la table vehicles"""
import psycopg2
from app.db import engine
from sqlalchemy import inspect

# Méthode 1: Utiliser SQLAlchemy Inspector
print("=" * 60)
print("COLONNES DE LA TABLE 'vehicles' (via SQLAlchemy)")
print("=" * 60)

inspector = inspect(engine)
columns = inspector.get_columns('vehicles')

for col in columns:
    print(f"  {col['name']:30} {col['type']}")

print("\n" + "=" * 60)
print("TOTAL:", len(columns), "colonnes")
print("=" * 60)
