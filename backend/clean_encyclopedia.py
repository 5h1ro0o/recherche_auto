"""
Script pour nettoyer toutes les données de l'encyclopédie
À utiliser avant de lancer populate_encyclopedia_massive.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import (
    CarBrand, CarModel, Engine, Transmission,
    BrandReview, ModelReview, EngineReview, TransmissionReview,
    TechnicalSpecification
)

def clean_encyclopedia():
    """Nettoie toutes les données de l'encyclopédie"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("🧹 NETTOYAGE DE L'ENCYCLOPÉDIE AUTOMOBILE")
        print("=" * 80)

        # Compter avant suppression
        brands_count = db.query(CarBrand).count()
        models_count = db.query(CarModel).count()
        engines_count = db.query(Engine).count()
        trans_count = db.query(Transmission).count()

        print(f"\n📊 Données actuelles :")
        print(f"   • {brands_count} marques")
        print(f"   • {models_count} modèles")
        print(f"   • {engines_count} moteurs")
        print(f"   • {trans_count} transmissions")

        if brands_count == 0 and models_count == 0 and engines_count == 0 and trans_count == 0:
            print("\n✅ La base est déjà vide !")
            return

        print("\n⚠️  Suppression en cours...")

        # Supprimer dans l'ordre (pour respecter les foreign keys)
        # Les avis en premier
        print("  • Suppression des avis...", end=" ")
        db.query(TransmissionReview).delete()
        db.query(EngineReview).delete()
        db.query(ModelReview).delete()
        db.query(BrandReview).delete()
        print("✓")

        # Les spécifications techniques
        print("  • Suppression des spécifications techniques...", end=" ")
        db.query(TechnicalSpecification).delete()
        print("✓")

        # Les transmissions et moteurs
        print("  • Suppression des transmissions...", end=" ")
        db.query(Transmission).delete()
        print("✓")

        print("  • Suppression des moteurs...", end=" ")
        db.query(Engine).delete()
        print("✓")

        # Les modèles
        print("  • Suppression des modèles...", end=" ")
        db.query(CarModel).delete()
        print("✓")

        # Les marques (en dernier)
        print("  • Suppression des marques...", end=" ")
        db.query(CarBrand).delete()
        print("✓")

        db.commit()

        print("\n" + "=" * 80)
        print("🎉 NETTOYAGE TERMINÉ !")
        print("=" * 80)
        print("\n✨ Votre base de données est maintenant vide.")
        print("   Vous pouvez lancer : python populate_encyclopedia_massive.py")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Demander confirmation
    print("\n⚠️  ATTENTION : Cette opération va SUPPRIMER TOUTES les données de l'encyclopédie !")
    print("   (marques, modèles, moteurs, transmissions, avis)")

    response = input("\nContinuer ? (oui/non) : ").strip().lower()

    if response in ['oui', 'o', 'yes', 'y']:
        clean_encyclopedia()
    else:
        print("\n❌ Opération annulée.")
