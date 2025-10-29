#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour créer un utilisateur administrateur"""

from app.db import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash
import uuid
import sys

def create_admin_user(email, password, full_name="Administrateur"):
    """Créer un utilisateur administrateur"""
    db = SessionLocal()

    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Erreur : Un utilisateur avec l'email '{email}' existe déjà.")
            print(f"   Rôle actuel : {existing_user.role.value}")
            return False

        # Créer l'utilisateur admin
        admin_user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"✓ Utilisateur administrateur créé avec succès !")
        print(f"  Email : {admin_user.email}")
        print(f"  Nom : {admin_user.full_name}")
        print(f"  Rôle : {admin_user.role.value}")
        print(f"  ID : {admin_user.id}")
        print()
        print("Vous pouvez maintenant vous connecter avec ces identifiants.")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur : {e}")
        db.rollback()
        return False

    finally:
        db.close()

def main():
    print("=" * 60)
    print("Création d'un utilisateur administrateur".center(60))
    print("=" * 60)
    print()

    # Mode interactif
    if len(sys.argv) > 1:
        email = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
        full_name = sys.argv[3] if len(sys.argv) > 3 else "Administrateur"
    else:
        email = input("Email de l'administrateur [admin@example.com] : ").strip() or "admin@example.com"
        password = input("Mot de passe [admin123] : ").strip() or "admin123"
        full_name = input("Nom complet [Administrateur] : ").strip() or "Administrateur"

    print()
    print(f"Création de l'utilisateur administrateur...")
    print(f"  Email : {email}")
    print(f"  Nom : {full_name}")
    print()

    success = create_admin_user(email, password, full_name)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
