#!/usr/bin/env python3
"""
Script pour créer un compte EXPERT via la console
Usage: python create_expert.py
"""
import sys
import uuid
from sqlalchemy.orm import Session

# Ajouter le dossier parent au path pour importer les modules
sys.path.insert(0, '/home/user/recherche_auto/backend')

from app.db import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

def create_expert(email: str, password: str, full_name: str = None, phone: str = None):
    """Créer un compte expert"""

    db: Session = SessionLocal()

    try:
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Erreur: Un compte avec l'email '{email}' existe déjà")
            return False

        # Créer l'expert
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(password)

        new_expert = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name or "Expert",
            phone=phone,
            role=UserRole.EXPERT,
            is_active=True,
            is_verified=True  # Auto-vérifié pour les experts créés manuellement
        )

        db.add(new_expert)
        db.commit()
        db.refresh(new_expert)

        print("✅ Compte expert créé avec succès !")
        print(f"   Email: {new_expert.email}")
        print(f"   Nom: {new_expert.full_name}")
        print(f"   Rôle: {new_expert.role.value}")
        print(f"   ID: {new_expert.id}")
        print(f"\n🔑 Vous pouvez maintenant vous connecter sur /login avec ces identifiants")

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la création: {e}")
        return False

    finally:
        db.close()


def main():
    print("=" * 60)
    print("🎯 Création d'un compte EXPERT")
    print("=" * 60)
    print()

    # Demander les informations
    email = input("Email de l'expert: ").strip()
    if not email:
        print("❌ Email requis")
        return

    password = input("Mot de passe (min 8 caractères): ").strip()
    if len(password) < 8:
        print("❌ Le mot de passe doit contenir au moins 8 caractères")
        return

    full_name = input("Nom complet (optionnel): ").strip() or None
    phone = input("Téléphone (optionnel): ").strip() or None

    print()
    print("📝 Récapitulatif:")
    print(f"   Email: {email}")
    print(f"   Nom: {full_name or '(non spécifié)'}")
    print(f"   Téléphone: {phone or '(non spécifié)'}")
    print(f"   Rôle: EXPERT")
    print()

    confirm = input("Confirmer la création ? (oui/non): ").strip().lower()
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Création annulée")
        return

    print()
    create_expert(email, password, full_name, phone)


if __name__ == "__main__":
    main()
