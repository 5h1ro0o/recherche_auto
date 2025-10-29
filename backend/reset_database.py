#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour réinitialiser la base de données et les migrations Alembic"""

import sys
import psycopg2
from psycopg2 import sql

def get_connection():
    """Se connecter à PostgreSQL"""
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="recherche_auto",
        user="app",
        password="changeme"
    )

def list_tables(conn):
    """Lister toutes les tables"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        return [row[0] for row in cur.fetchall()]

def drop_all_tables(conn):
    """Supprimer toutes les tables"""
    with conn.cursor() as cur:
        # Supprimer les ENUMs d'abord (si ils existent)
        enums = ['userrole', 'requeststatus', 'proposalstatus']
        for enum_name in enums:
            try:
                cur.execute(sql.SQL("DROP TYPE IF EXISTS {} CASCADE").format(
                    sql.Identifier(enum_name)
                ))
                print(f"✓ ENUM '{enum_name}' supprimé")
            except Exception as e:
                print(f"⚠ Impossible de supprimer ENUM '{enum_name}': {e}")

        # Supprimer toutes les tables
        tables = list_tables(conn)
        if tables:
            print(f"\nSuppression de {len(tables)} tables...")
            for table in tables:
                try:
                    cur.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                        sql.Identifier(table)
                    ))
                    print(f"✓ Table '{table}' supprimée")
                except Exception as e:
                    print(f"✗ Erreur lors de la suppression de '{table}': {e}")
        else:
            print("Aucune table à supprimer")

        conn.commit()

def reset_alembic_version(conn):
    """Réinitialiser la table alembic_version"""
    with conn.cursor() as cur:
        try:
            cur.execute("DROP TABLE IF EXISTS alembic_version CASCADE")
            print("✓ Table 'alembic_version' supprimée")
            conn.commit()
        except Exception as e:
            print(f"⚠ Erreur: {e}")
            conn.rollback()

def main():
    print("=" * 70)
    print("RÉINITIALISATION DE LA BASE DE DONNÉES".center(70))
    print("=" * 70)
    print()
    print("⚠ ATTENTION : Cette opération va supprimer TOUTES les données !")
    print()

    # Confirmation
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non) : ").strip().lower()
    if response not in ['oui', 'yes', 'y', 'o']:
        print("Opération annulée.")
        sys.exit(0)

    print()
    print("Connexion à la base de données...")

    try:
        conn = get_connection()
        print("✓ Connexion réussie")
        print()

        # Lister les tables existantes
        tables = list_tables(conn)
        print(f"Tables existantes : {len(tables)}")
        for table in tables:
            print(f"  - {table}")
        print()

        # Supprimer toutes les tables
        drop_all_tables(conn)
        print()

        # Réinitialiser alembic_version
        reset_alembic_version(conn)
        print()

        print("=" * 70)
        print("✓ Base de données réinitialisée avec succès !".center(70))
        print("=" * 70)
        print()
        print("Prochaines étapes :")
        print("  1. Exécutez : alembic upgrade head")
        print("  2. Exécutez : python create_admin.py (optionnel)")
        print("  3. Démarrez le serveur : uvicorn app.main:app --reload")
        print()

        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Erreur PostgreSQL : {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
